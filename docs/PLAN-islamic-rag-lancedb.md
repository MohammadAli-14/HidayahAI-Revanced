# PLAN: Advanced Islamic RAG Pipeline & LanceDB Integration

**Overview:** Transform Hidayah AI's PDF RAG system from ephemeral FAISS into an academically sound, persistent, hybrid-search Islamic research engine with LanceDB, PyMuPDF, BGE-M3, and Islamic guardrails.

## Tasks Breakdown

### Phase 1: Foundation & Dependencies
- [x] Task 1.1: Update `requirements.txt` with `lancedb`, `tantivy`, `pymupdf`, `sentence-transformers`, `flashrank`.
- [x] Task 1.2: Update `utils/config.py` with LanceDB paths, model definitions, and local LLM options.

### Phase 2: Ingestion & Smart Parsing
- [x] Task 2.1: Implement `rag/smart_loader.py` with PyMuPDF and Arabic/Urdu RTL text normalizers.
- [x] Task 2.2: Implement metadata-preserving Islamic document chunker.

### Phase 3: LanceDB Storage & Hybrid Search
- [x] Task 3.1: Implement `rag/lancedb_store.py` with embedded LanceDB tables, vector index, and Tantivy FTS index.
- [x] Task 3.2: Implement `rag/reranker.py` with CPU-optimized FlashRank / Cross-Encoder.
- [x] Task 3.3: Refactor `rag/query.py` to use LanceDB hybrid search and pass rich citation context to LLM.

### Phase 4: Islamic Guardrails & Safety
- [x] Task 4.1: Implement `utils/islamic_guardrails.py` (Pre-generation Fatwa Gate & Post-generation Citation Verifier).
- [x] Task 4.2: Integrate guardrails into `agents/scholar.py`.

### Phase 5: UI & Experience Polish
- [x] Task 5.1: Update `ui/chat_panel.py` to show document index manager, progress bars, and citation sources.
- [x] Task 5.2: Verify end-to-end flow with Arabic/English/Urdu queries.
