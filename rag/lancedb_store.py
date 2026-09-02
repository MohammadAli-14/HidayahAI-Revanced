"""
Hidayah AI — LanceDB Vector Store & Hybrid Search Engine
Provides persistent embedded vector storage with Tantivy BM25 Full-Text Search (FTS).
"""

import time
from pathlib import Path
import numpy as np
from utils.config import LANCEDB_DIR
from utils.logger import get_logger

log = get_logger("lancedb_store")


class IslamicLanceStore:
    """
    Persistent embedded LanceDB database manager for Islamic research documents.
    Combines dense semantic vector search with Tantivy BM25 Full-Text Search.
    """

    def __init__(self, table_name: str = "scholarly_documents"):
        self.table_name = table_name
        self.db_path = str(LANCEDB_DIR)
        self._db = None
        self._table = None
        self._init_db()

    def _init_db(self):
        """Initialize connection to local embedded LanceDB."""
        try:
            import lancedb

            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            self._db = lancedb.connect(self.db_path)
            log.info(f"Connected to LanceDB at: {self.db_path}")
        except ImportError:
            log.warning("LanceDB not installed. Run: pip install lancedb tantivy")
            self._db = None
        except Exception as e:
            log.error(f"LanceDB connection error: {e}")
            self._db = None

    def is_available(self) -> bool:
        """Check if LanceDB is initialized and available."""
        return self._db is not None

    def index_chunks(
        self,
        chunks: list[dict],
        embeddings: np.ndarray | list,
        replace_existing_file: bool = True,
    ) -> bool:
        """
        Store document chunks and vector embeddings in LanceDB,
        and build a Tantivy Full-Text Search (FTS) index.

        Args:
            chunks: List of chunk dicts from smart_loader
            embeddings: Numpy array or list of vectors (same length as chunks)
            replace_existing_file: If True, replaces existing chunks with same filename

        Returns:
            True on success, False otherwise
        """
        if not self.is_available() or not chunks or embeddings is None:
            log.error("Cannot index chunks: LanceDB not available or empty data")
            return False

        try:
            records = []
            now_ts = time.time()

            for i, chunk in enumerate(chunks):
                vector = embeddings[i]
                if isinstance(vector, np.ndarray):
                    vector = vector.tolist()

                records.append({
                    "id": str(chunk.get("id", f"chunk_{i}")),
                    "text": str(chunk.get("text", "")),
                    "clean_text": str(chunk.get("clean_text", chunk.get("text", ""))),
                    "vector": vector,
                    "page": int(chunk.get("page", 1)),
                    "filename": str(chunk.get("filename", "document.pdf")),
                    "chunk_index": int(chunk.get("chunk_index", i)),
                    "word_count": int(chunk.get("word_count", 0)),
                    "created_at": float(now_ts),
                })

            table_names = self._db.table_names()
            filename = chunks[0].get("filename", "")

            if self.table_name not in table_names:
                # Create table
                self._table = self._db.create_table(self.table_name, data=records, mode="create")
                log.info(f"Created table '{self.table_name}' with {len(records)} records")
            else:
                self._table = self._db.open_table(self.table_name)
                if replace_existing_file and filename:
                    try:
                        # Delete existing chunks for this filename
                        self._table.delete(f'filename = "{filename}"')
                        log.info(f"Deleted previous records for '{filename}'")
                    except Exception as del_err:
                        log.warning(f"Could not delete previous records: {del_err}")

                # Append new records
                self._table.add(records)
                log.info(f"Added {len(records)} records to '{self.table_name}'")

            # Create / Refresh Tantivy Full-Text Search (FTS) index on text column
            try:
                self._table.create_fts_index("text", replace=True)
                log.info("Built Tantivy FTS index on 'text' column")
            except Exception as fts_err:
                log.warning(f"FTS index creation note (vector search remains active): {fts_err}")

            return True

        except Exception as e:
            log.error(f"Error indexing chunks in LanceDB: {e}")
            return False

    def hybrid_search(
        self,
        query_text: str,
        query_vector: list[float] | np.ndarray | None = None,
        filename_filter: str | None = None,
        top_k: int = 15,
    ) -> list[dict]:
        """
        Execute Hybrid Search (BM25 keyword search + Dense Vector search)
        with Reciprocal Rank Fusion (RRF).

        Args:
            query_text: Natural language or keyword query
            query_vector: Dense embedding vector for semantic search
            filename_filter: Optional filter to search within a specific document
            top_k: Number of candidates to retrieve

        Returns:
            List of matching chunk dicts sorted by relevance
        """
        if not self.is_available():
            return []

        try:
            if self.table_name not in self._db.table_names():
                log.warning(f"Table '{self.table_name}' does not exist in LanceDB")
                return []

            table = self._db.open_table(self.table_name)
            if len(table) == 0:
                return []

            if isinstance(query_vector, np.ndarray):
                query_vector = query_vector.tolist()

            # Attempt native Hybrid Search (BM25 + Vector)
            if query_vector is not None and query_text:
                try:
                    from lancedb.rerankers import RRFReranker

                    search_builder = (
                        table.search(query_type="hybrid")
                        .vector(query_vector)
                        .text(query_text)
                        .rerank(reranker=RRFReranker())
                    )
                    if filename_filter:
                        search_builder = search_builder.where(f'filename = "{filename_filter}"')

                    df_results = search_builder.limit(top_k).to_pandas()
                    records = df_results.to_dict(orient="records")
                    log.info(f"Hybrid search returned {len(records)} results for: '{query_text[:50]}'")
                    return records
                except Exception as hybrid_err:
                    log.warning(f"Hybrid search fallback to vector search: {hybrid_err}")

            # Fallback 1: Vector Search only
            if query_vector is not None:
                try:
                    search_builder = table.search(query_vector).metric("cosine")
                    if filename_filter:
                        search_builder = search_builder.where(f'filename = "{filename_filter}"')
                    df_results = search_builder.limit(top_k).to_pandas()
                    return df_results.to_dict(orient="records")
                except Exception as vec_err:
                    log.warning(f"Vector search error: {vec_err}")

            # Fallback 2: Full-Text Search only
            if query_text:
                try:
                    search_builder = table.search(query_text, query_type="fts")
                    if filename_filter:
                        search_builder = search_builder.where(f'filename = "{filename_filter}"')
                    df_results = search_builder.limit(top_k).to_pandas()
                    return df_results.to_dict(orient="records")
                except Exception as fts_err:
                    log.warning(f"FTS search error: {fts_err}")

            return []

        except Exception as e:
            log.error(f"LanceDB search error: {e}")
            return []

    def list_indexed_documents(self) -> list[dict]:
        """
        Return a list of indexed documents with page counts and chunk counts.
        """
        if not self.is_available():
            return []

        try:
            if self.table_name not in self._db.table_names():
                return []

            table = self._db.open_table(self.table_name)
            if len(table) == 0:
                return []

            df = table.to_pandas()
            if df.empty or "filename" not in df.columns:
                return []

            docs_summary = []
            for filename, group in df.groupby("filename"):
                docs_summary.append({
                    "filename": str(filename),
                    "chunk_count": len(group),
                    "page_count": int(group["page"].max()) if "page" in group.columns else 1,
                    "created_at": float(group["created_at"].max()) if "created_at" in group.columns else 0.0,
                })

            return docs_summary
        except Exception as e:
            log.error(f"Error listing indexed documents: {e}")
            return []

    def delete_document(self, filename: str) -> bool:
        """Delete all chunks for a specific document."""
        if not self.is_available():
            return False

        try:
            if self.table_name not in self._db.table_names():
                return False

            table = self._db.open_table(self.table_name)
            table.delete(f'filename = "{filename}"')
            log.info(f"Successfully deleted document '{filename}' from LanceDB")
            return True
        except Exception as e:
            log.error(f"Error deleting document '{filename}': {e}")
            return False

    def clear_all(self) -> bool:
        """Drop the entire table and clear data."""
        if not self.is_available():
            return False

        try:
            if self.table_name in self._db.table_names():
                self._db.drop_table(self.table_name)
                log.info(f"Dropped table '{self.table_name}'")
            return True
        except Exception as e:
            log.error(f"Error dropping table '{self.table_name}': {e}")
            return False
