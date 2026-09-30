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

    def _get_table_names(self) -> list[str]:
        """Safely fetch table names avoiding LanceDB deprecation warnings."""
        if not self._db:
            return []
        try:
            res = self._db.list_tables()
            if hasattr(res, "tables"):
                return list(res.tables)
            if isinstance(res, (list, tuple, set)):
                return list(res)
            return list(self._db.table_names())
        except Exception:
            try:
                return list(self._db.table_names())
            except Exception:
                return []

    def index_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]] | np.ndarray,
        replace_existing_file: bool = True,
    ) -> bool:
        """
        Index text chunks with vector embeddings and metadata into LanceDB.

        Args:
            chunks: List of chunk dicts from smart_loader (must have 'text', 'page', 'filename')
            embeddings: 2D array/list of vector embeddings corresponding to chunks
            replace_existing_file: If True, replaces existing chunks for this filename

        Returns:
            True if successfully indexed, False otherwise
        """
        if not self.is_available() or not chunks or len(chunks) == 0:
            log.error("Cannot index chunks: LanceDB not available or empty data")
            return False

        try:
            now_ts = time.time()
            records = []
            for i, chunk in enumerate(chunks):
                vector = embeddings[i]
                if isinstance(vector, np.ndarray):
                    vector = vector.tolist()

                records.append({
                    "id": str(uuid.uuid4()),
                    "text": str(chunk.get("text", "")),
                    "clean_text": str(chunk.get("clean_text", chunk.get("text", ""))),
                    "vector": vector,
                    "page": int(chunk.get("page", 1)),
                    "filename": str(chunk.get("filename", "document.pdf")),
                    "chunk_index": int(chunk.get("chunk_index", i)),
                    "word_count": int(chunk.get("word_count", 0)),
                    "created_at": float(now_ts),
                })

            table_names = self._get_table_names()
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
            if self.table_name not in self._get_table_names():
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
            if self.table_name not in self._get_table_names():
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
            if self.table_name not in self._get_table_names():
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
            if self.table_name in self._get_table_names():
                self._db.drop_table(self.table_name)
                log.info(f"Dropped table '{self.table_name}'")
            return True
        except Exception as e:
            log.error(f"Error dropping table '{self.table_name}': {e}")
            return False


def search_canonical_hadiths(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Search the pre-indexed 50,762 authentic Hadith corpus using LanceDB Tantivy FTS.
    
    Args:
        query_text: Keyword or topic to search (e.g. 'prayer', 'fasting', 'abu bakr')
        top_k: Number of matching Hadiths to retrieve
        
    Returns:
        List of matching Hadith dictionaries with Arabic & English text and Isnad
    """
    store = IslamicLanceStore(table_name="canonical_hadiths")
    if not store.is_available():
        return []
    return store.hybrid_search(query_text=query_text, top_k=top_k)


SURAH_NAME_MAP = {
    'al faatiha': 1, 'fatiha': 1, 'al baqara': 2, 'baqarah': 2, 'baqara': 2,
    'aal i imraan': 3, 'imran': 3, 'ali imran': 3, 'an nisaa': 4, 'nisa': 4, 'an nisa': 4, 'an nisaa': 4,
    'al maaida': 5, 'maidah': 5, 'al anaam': 6, 'anam': 6, 'al araaf': 7, 'araf': 7,
    'al anfaal': 8, 'anfal': 8, 'at tawba': 9, 'tawbah': 9, 'yunus': 10, 'hud': 11,
    'yusuf': 12, 'ar rad': 13, 'rad': 13, 'ibrahim': 14, 'al hijr': 15, 'an nahl': 16,
    'nahl': 16, 'al israa': 17, 'isra': 17, 'al kahf': 18, 'kahf': 18, 'maryam': 19,
    'taa haa': 20, 'taha': 20, 'al anbiyaa': 21, 'anbiya': 21, 'al hajj': 22, 'hajj': 22,
    'al muminoon': 23, 'muminun': 23, 'an noor': 24, 'nur': 24, 'al furqaan': 25, 'furqan': 25,
    'ash shuaraa': 26, 'shuara': 26, 'an naml': 27, 'naml': 27, 'al qasas': 28, 'qasas': 28,
    'al ankaboot': 29, 'ankabut': 29, 'ar room': 30, 'rum': 30, 'luqman': 31, 'as sajda': 32,
    'sajdah': 32, 'al ahzaab': 33, 'ahzab': 33, 'saba': 34, 'faatir': 35, 'fatir': 35,
    'yaseen': 36, 'yasin': 36, 'as saaffaat': 37, 'saffat': 37, 'saad': 38, 'sad': 38,
    'az zumar': 39, 'zumar': 39, 'ghafir': 40, 'fussilat': 41, 'ash shura': 42, 'shura': 42,
    'az zukhruf': 43, 'zukhruf': 43, 'ad dukhaan': 44, 'dukhan': 44, 'al jaathiya': 45,
    'al ahqaf': 46, 'ahqaf': 46, 'muhammad': 47, 'al fath': 48, 'fath': 48, 'al hujuraat': 49,
    'hujurat': 49, 'qaaf': 50, 'qaf': 50, 'adh dhaariyat': 51, 'dhariyat': 51, 'at tur': 52,
    'tur': 52, 'an najm': 53, 'najm': 53, 'al qamar': 54, 'qamar': 54, 'ar rahmaan': 55,
    'rahman': 55, 'al waaqia': 56, 'waqiah': 56, 'al hadid': 57, 'hadid': 57, 'al mujaadila': 58,
    'al hashr': 59, 'hashr': 59, 'al mumtahana': 60, 'as saff': 61, 'al jumua': 62,
    'jumuah': 62, 'al munaafiqoon': 63, 'munafiqun': 63, 'at taghaabun': 64, 'at talaaq': 65,
    'talaq': 65, 'at tahrim': 66, 'tahrim': 66, 'al mulk': 67, 'mulk': 67, 'al qalam': 68,
    'qalam': 68, 'al haaqqa': 69, 'al maaarij': 70, 'nooh': 71, 'nuh': 71, 'al jinn': 72,
    'jinn': 72, 'al muzzammil': 73, 'muzzammil': 73, 'al muddaththir': 74, 'muddathir': 74,
    'al qiyaama': 75, 'qiyamah': 75, 'al insaan': 76, 'insan': 76, 'al mursalaat': 77,
    'an naba': 78, 'naba': 78, 'an naaziaat': 79, 'naziat': 79, 'abasa': 80, 'at takwir': 81,
    'al infitaar': 82, 'al mutaffifin': 83, 'al inshiqaaq': 84, 'al burooj': 85, 'buruj': 85,
    'at taariq': 86, 'tariq': 86, 'al alaa': 87, 'ala': 87, 'al ghaashiya': 88, 'al fajr': 89,
    'fajr': 89, 'al balad': 90, 'balad': 90, 'ash shams': 91, 'shams': 91, 'al lail': 92,
    'layl': 92, 'ad dhuhaa': 93, 'duha': 93, 'ash sharh': 94, 'sharh': 94, 'inshirah': 94,
    'at tin': 95, 'tin': 95, 'al alaq': 96, 'alaq': 96, 'al qadr': 97, 'qadr': 97,
    'al bayyina': 98, 'bayyinah': 98, 'az zalzala': 99, 'zalzalah': 99, 'al aadiyaat': 100,
    'al qaaria': 101, 'qariah': 101, 'at takaathur': 102, 'al asr': 103, 'asr': 103,
    'al humaza': 104, 'humazah': 104, 'al fil': 105, 'fil': 105, 'quraish': 106, 'quraysh': 106,
    'al maaun': 107, 'maun': 107, 'al kawthar': 108, 'kawthar': 108, 'al kaafiroon': 109,
    'kafirun': 109, 'an nasr': 110, 'nasr': 110, 'al masad': 111, 'masad': 111, 'lahab': 111,
    'al ikhlaas': 112, 'ikhlas': 112, 'al falaq': 113, 'falaq': 113, 'an naas': 114, 'nas': 114
}


def search_canonical_quran(query_text: str, top_k: int = 5) -> list[dict]:
    """
    Search the pre-indexed 6,236 Quranic verses using LanceDB Tantivy FTS & vector search.
    Features smart exact reference resolution for queries citing specific Surahs and Ayahs.
    
    Args:
        query_text: Topic, keyword, or meaning (e.g. 'healing', 'parents', 'sabr', 'charity')
        top_k: Number of matching Ayahs to retrieve
        
    Returns:
        List of matching Quran Ayah dictionaries with Arabic, English, Urdu, Surah, and Juz
    """
    store = IslamicLanceStore(table_name="canonical_quran")
    if not store.is_available():
        return []

    exact_results = []
    try:
        # Check for numerical reference (e.g. 4:11, 2:255)
        import re
        q_clean = query_text.lower().replace("-", " ").replace("'", "")
        
        surah_num = None
        ayah_num = None

        m_num = re.search(r"(\b\d{1,3}):(\d{1,3})\b", query_text)
        if m_num:
            surah_num = int(m_num.group(1))
            ayah_num = int(m_num.group(2))
        else:
            # Check for name + verse pattern (e.g. "surah an nisa verse 11")
            for s_name, s_id in SURAH_NAME_MAP.items():
                if s_name in q_clean:
                    m_ayah = re.search(r"(?:verse|ayah|number)\s*(\d{1,3})", q_clean)
                    if m_ayah:
                        surah_num = s_id
                        ayah_num = int(m_ayah.group(1))
                        break

        if surah_num and ayah_num and 1 <= surah_num <= 114:
            table = store._db.open_table(store.table_name)
            df_exact = table.search().where(f"surah_number = {surah_num} AND ayah_number = {ayah_num}").to_pandas()
            if not df_exact.empty:
                exact_results = df_exact.to_dict(orient="records")
                log.info(f"Directly resolved exact Quran verse: Surah {surah_num}, Ayah {ayah_num}")
    except Exception as e:
        log.warning(f"Exact verse parser notice: {e}")

    # If exact verse found, prioritize it at the top
    if exact_results:
        hybrid_res = store.hybrid_search(query_text=query_text, top_k=max(1, top_k - 1))
        # Deduplicate
        seen_ids = {exact_results[0].get("id")}
        combined = list(exact_results)
        for r in hybrid_res:
            if r.get("id") not in seen_ids and len(combined) < top_k:
                seen_ids.add(r.get("id"))
                combined.append(r)
        return combined

    return store.hybrid_search(query_text=query_text, top_k=top_k)


