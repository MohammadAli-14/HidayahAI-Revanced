"""
Hidayah AI — Vector Store & Embedding Engine
Provides dense vector embeddings (Gemini embedding-001 or local fallback)
and integrates with LanceDB persistent storage.
"""

import time
import numpy as np
from google import genai
from utils.config import MODEL_EMBEDDING, GEMINI_API_KEY, get_gemini_client
from utils.logger import get_logger

log = get_logger("vector_store")


def embed_texts(texts: list[str], task_type: str = "retrieval_document") -> np.ndarray | None:
    """
    Embed a list of text chunks using Gemini embedding-001 with retry & backoff.

    Args:
        texts: List of text strings to embed
        task_type: "retrieval_document" for indexing, "retrieval_query" for searching

    Returns:
        numpy array of shape (n, dim) or None on failure
    """
    client = get_gemini_client()
    if not client or not texts:
        return None

    try:
        embeddings = []
        batch_size = 20  # Reduced batch size for rate-limit protection

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                if not text.strip():
                    continue

                # Retry with backoff for 429
                retries = 3
                while retries > 0:
                    try:
                        result = client.models.embed_content(
                            model=MODEL_EMBEDDING,
                            contents=text,
                        )
                        if result.embeddings:
                            embeddings.append(result.embeddings[0].values)
                        break
                    except genai.errors.APIError as e:
                        if e.code == 429:
                            retries -= 1
                            if retries == 0:
                                log.warning("Hit 429 rate limit on embedding.")
                                return "⚠️ 429"
                            time.sleep(1.5)
                        else:
                            raise e

        if not embeddings:
            return None

        return np.array(embeddings, dtype=np.float32)

    except Exception as e:
        log.error(f"Embedding error: {e}")
        return None


def embed_single_query(query: str) -> list[float] | None:
    """Embed a single query string into a vector."""
    res = embed_texts([query], task_type="retrieval_query")
    if isinstance(res, str) and "⚠️ 429" in res:
        return "⚠️ 429"
    if res is not None and len(res) > 0:
        return res[0].tolist()
    return None


def build_index(chunks: list[dict] | list[str], filename: str = "document.pdf"):
    """
    Build and store embeddings into both LanceDB (persistent) and FAISS (in-memory).

    Args:
        chunks: List of chunk dicts from smart_loader or list of string chunks
        filename: Document filename

    Returns:
        Tuple of (store_status, embeddings)
    """
    if not chunks:
        return None, None

    # Handle string chunks vs dict chunks
    if isinstance(chunks[0], dict):
        text_list = [c.get("clean_text") or c.get("text", "") for c in chunks]
        structured_chunks = chunks
    else:
        text_list = chunks
        structured_chunks = [
            {"id": f"{filename}_c{i}", "text": t, "page": 1, "filename": filename, "chunk_index": i}
            for i, t in enumerate(chunks)
        ]

    embeddings = embed_texts(text_list, task_type="retrieval_document")
    if isinstance(embeddings, str) and "⚠️ 429" in embeddings:
        return "⚠️ 429", None
    if embeddings is None:
        return None, None

    # 1. Index into LanceDB (Persistent + FTS)
    try:
        from rag.lancedb_store import IslamicLanceStore

        lance_store = IslamicLanceStore()
        if lance_store.is_available():
            lance_store.index_chunks(structured_chunks, embeddings, replace_existing_file=True)
            log.info(f"Indexed {len(structured_chunks)} chunks in LanceDB for '{filename}'")
    except Exception as lance_err:
        log.warning(f"LanceDB indexing notice: {lance_err}")

    # 2. Build in-memory FAISS index as fallback
    try:
        import faiss

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = embeddings / norms

        dimension = normalized.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(normalized)

        return index, embeddings
    except Exception as faiss_err:
        log.warning(f"FAISS index notice: {faiss_err}")
        return "LANCEDB_READY", embeddings


def search_index(
    query: str,
    index,
    chunks: list[dict] | list[str],
    top_k: int = 5,
    filename_filter: str | None = None,
) -> list[dict] | list[str]:
    """
    Search for relevant chunks using LanceDB Hybrid Search (with RRF)
    or FAISS vector search fallback.
    """
    if not chunks or not query:
        return []

    # 1. Try LanceDB Hybrid Search (BM25 + Vector)
    try:
        from rag.lancedb_store import IslamicLanceStore
        from rag.reranker import rerank_passages

        lance_store = IslamicLanceStore()
        if lance_store.is_available():
            query_vector = embed_single_query(query)
            if isinstance(query_vector, str) and "⚠️ 429" in query_vector:
                return "⚠️ 429"

            lance_results = lance_store.hybrid_search(
                query_text=query,
                query_vector=query_vector if isinstance(query_vector, list) else None,
                filename_filter=filename_filter,
                top_k=top_k * 3,  # Retrieve more for cross-encoder reranking
            )
            if lance_results:
                reranked = rerank_passages(query, lance_results, top_k=top_k)
                return reranked
    except Exception as lance_search_err:
        log.warning(f"LanceDB search fallback: {lance_search_err}")

    # 2. Fallback to FAISS
    if index is not None and index != "LANCEDB_READY":
        try:
            import faiss

            query_embedding = embed_texts([query], task_type="retrieval_query")
            if isinstance(query_embedding, str) and "⚠️ 429" in query_embedding:
                return "⚠️ 429"
            if query_embedding is not None:
                norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
                if norm[0][0] != 0:
                    query_normalized = query_embedding / norm
                    scores, indices = index.search(query_normalized, min(top_k, len(chunks)))
                    results = []
                    for idx in indices[0]:
                        if 0 <= idx < len(chunks):
                            results.append(chunks[idx])
                    return results
        except Exception as faiss_err:
            log.error(f"FAISS search fallback error: {faiss_err}")

    return []
