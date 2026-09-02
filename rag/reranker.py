"""
Hidayah AI — Cross-Encoder Reranker
Uses FlashRank for ultra-fast, CPU-efficient reranking of retrieved passages.
"""

from utils.config import RERANKER_MODEL
from utils.logger import get_logger

log = get_logger("reranker")

_ranker_instance = None


def _get_ranker():
    """Lazy initialize the FlashRank ranker."""
    global _ranker_instance
    if _ranker_instance is not None:
        return _ranker_instance

    try:
        from flashrank import Ranker

        _ranker_instance = Ranker(model_name=RERANKER_MODEL, cache_dir="./data/models")
        log.info(f"Initialized FlashRank reranker with model: {RERANKER_MODEL}")
        return _ranker_instance
    except ImportError:
        log.warning("FlashRank not installed. Falling back to rank-preserving pass-through.")
        return None
    except Exception as e:
        log.warning(f"Could not load FlashRank ({e}). Falling back to pass-through.")
        return None


def rerank_passages(
    query: str,
    passages: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Rerank retrieved passages against the query using a cross-encoder.

    Args:
        query: User search query
        passages: List of candidate chunk dicts (each containing 'text' or 'clean_text')
        top_k: Number of top-scoring passages to return

    Returns:
        List of reranked passage dicts with 'relevance_score' attached
    """
    if not passages or not query:
        return []

    ranker = _get_ranker()
    if ranker is None or len(passages) <= 1:
        # Return initial ranking if reranker unavailable
        return passages[:top_k]

    try:
        from flashrank import RerankRequest

        # Format passages for FlashRank
        flashrank_passages = []
        for idx, p in enumerate(passages):
            text_content = p.get("text") or p.get("clean_text") or ""
            flashrank_passages.append({
                "id": p.get("id", f"p_{idx}"),
                "text": text_content,
                "meta": p,
            })

        rerank_request = RerankRequest(query=query, passages=flashrank_passages)
        results = ranker.rerank(rerank_request)

        reranked_output = []
        for item in results[:top_k]:
            original_meta = item.get("meta", {})
            original_meta["relevance_score"] = round(float(item.get("score", 0.0)), 4)
            reranked_output.append(original_meta)

        log.info(f"Reranked {len(passages)} passages down to {len(reranked_output)} for query: '{query[:40]}'")
        return reranked_output

    except Exception as e:
        log.warning(f"Reranking error ({e}). Returning original order.")
        return passages[:top_k]
