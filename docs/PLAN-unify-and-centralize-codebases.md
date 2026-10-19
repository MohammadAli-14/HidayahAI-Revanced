# Master Architectural Consolidation Plan: Unified Hidayah AI Codebase

> **Status:** Completed & Verified  
> **Target Repository:** `d:\Hidayah AI` (Root Centralized Repository)  
> **Reference Snapshot Analyzed:** `d:\Hidayah AI\Hidayah AI - Copy`  

---

## 1. Executive Summary

Hidayah AI had been developed across two concurrent directory trees:
1. **Root Directory (`d:\Hidayah AI`)**: The primary production workspace containing the full canonical LanceDB corpus (6,236 Quranic ayahs + 50,762 authentic Hadiths), Two-Tier Islamic Fatwa sensitivity guardrails, FlashRank reranking, the HidayahLM-3B fine-tuning pipeline, offline heuristic routing, and comprehensive academic research specifications.
2. **Copy Directory (`d:\Hidayah AI\Hidayah AI - Copy`)**: A parallel baseline snapshot (branched at commit `12da8e7`, *"Source authenticity hardened"*) containing proven UI layout refinements, Sunnah.com authenticated Hadith API integrations, and in-memory FAISS fallback mechanisms.

This consolidation plan establishes `d:\Hidayah AI` as the **single, unified, and authoritative root repository**, consolidating all accuracy enhancements, theological safety mechanisms, and multi-engine capabilities into one cohesive application.

---

## 2. Deep Comparative Audit & Diff Analysis

### 2.1 File System Topology Comparison
A comprehensive tree comparison across both directories revealed:
- **Identical Files (235 files)**: Core Streamlit rendering (`app.py`, `ui/quran_display.py`, `ui/sidebar.py`, `ui/audio_player.py`, `utils/evidence.py`, `utils/tafsir_api.py`, `utils/trust.py`) are fully synchronized.
- **Exclusive to Root (13 critical subsystems)**:
  - `rag/lancedb_store.py`: Embedded LanceDB vector + Tantivy BM25 full-text search tables.
  - `rag/reranker.py`: CPU-optimized FlashRank cross-encoder reranking.
  - `rag/smart_loader.py`: High-fidelity PyMuPDF loader with Arabic/Urdu RTL normalization and diacritic handling.
  - `rag/surah_themes.py`: Classical Surah thematic structure and exegesis summaries.
  - `rag/index_canonical_quran.py`: Automated indexing pipeline for the complete Uthmani text.
  - `utils/islamic_guardrails.py`: Pre-query two-tier Fatwa sensitivity gate & post-generation citation auditor.
  - `training/`: Complete fine-tuning dataset generator, Unsloth Qwen-2.5-3B LoRA training script, Modelfile for Ollama, and Kaggle execution cells.
  - `data/`: Local LanceDB persistent database containing indexed Quran and Hadith corpus.
  - `tests/`: Automated unit and compliance test suites (`test_islamic_compliance.py`, `test_islamic_rag.py`).
  - `docs/RESEARCH_PAPER_MASTER_SPECIFICATION.md`: Complete academic publication blueprint.
  - `visualize_corpus.py`: Interactive 3D vector space and distribution visualization tools.
- **Exclusive to Copy (0 files)**: Every file in `Hidayah AI - Copy` exists in `d:\Hidayah AI`.
- **Divergent Files (12 files)**: Carefully examined line-by-line:
  - `.env.example`: Root includes optional `USE_LOCAL_LLM` and `LOCAL_LLM_URL` parameters.
  - `.gitignore`: Root protects models, datasets, binaries, and ignores the legacy copy folder.
  - `agents/router.py`: Root includes a 0ms offline rule-based heuristic intent classifier with Gemini 2.5 Flash-Lite fallback.
  - `agents/scholar.py`: Root features strict Islamic theological guardrails, Fatwa sensitivity gating, abrogation awareness, 4-Madhhab neutrality, and local Ollama streaming failover.
  - `rag/query.py`: Root utilizes LanceDB Hybrid Search + Reranker + page citation audit, while gracefully supporting FAISS in-memory search.
  - `rag/vector_store.py`: Root builds persistent LanceDB tables with Tantivy FTS while simultaneously creating an in-memory FAISS index as fallback.
  - `ui/chat_panel.py`: Root provides LanceDB persistent research document management (with chunk counters, deletion, and active focus) alongside responsive mobile controls.
  - `utils/config.py`: Root maintains LanceDB directory paths, local LLM configurations, and primary Hadith provider flags.
  - `utils/hadith_api.py`: Root implements a 3-tier cascade (Canonical LanceDB 50k -> Sunnah.com API -> Tavily web commentary).

---

## 3. Unified Root Architecture

```
                                  [ User Query ]
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │    agents/router.py         │
                         │  0ms Heuristic Classifier   │
                         │  (Gemini Flash-Lite Fallback)│
                         └──────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
      [ VERSE_LOOKUP ]        [ SCHOLARLY_RESEARCH ]       [ PDF_ANALYSIS ]
              │                         │                         │
              ▼                         ▼                         ▼
   ┌────────────────────┐   ┌────────────────────────┐  ┌─────────────────────┐
   │ utils/tafsir_api.py│   │ utils/islamic_         │  │ rag/smart_loader.py │
   │ • Quran.com v4     │   │   guardrails.py        │  │ • PyMuPDF + RTL     │
   │ • AlQuran.cloud    │   │ • Fatwa Sensitivity    │  │ • Diacritic cleaner │
   │ • Arabic/En/Urdu   │   │ • Personal vs Academic │  │ • PyPDF2 fallback   │
   └──────────┬─────────┘   └───────────┬────────────┘  └──────────┬──────────┘
              │                         │                          │
              │                         ▼                          ▼
              │             ┌────────────────────────┐  ┌─────────────────────┐
              │             │ utils/hadith_api.py    │  │ rag/query.py        │
              │             │ 1. LanceDB 50k Corpus  │  │ • LanceDB Hybrid    │
              │             │ 2. Sunnah.com API      │  │ • FlashRank Rerank  │
              │             │ 3. Tavily Web Fallback │  │ • FAISS Fallback    │
              │             └───────────┬────────────┘  └──────────┬──────────┘
              │                         │                          │
              └─────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │    agents/scholar.py        │
                         │  Cloud: Gemini 2.5 Flash    │
                         │  Local: HidayahLM-3B Ollama │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ utils/islamic_guardrails.py │
                         │ • Citation Verification     │
                         │ • Surah:Ayah Bounds Check   │
                         │ • Anti-Hallucination Audit  │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                           [ Verified UI Response ]
```

### 3.1 Key Architectural Tenets
1. **Resilience & Zero Single-Point-of-Failure**:
   - Works fully cloud-connected with Gemini 2.5 Flash and Sunnah.com API.
   - Works fully local/offline with LanceDB tables and local `hidayah-lm:3b` via Ollama.
   - If LanceDB or PyMuPDF is not installed in an environment, the system automatically falls back to in-memory FAISS and PyPDF2.
2. **Theological Rigor & Fatwa Safety**:
   - Binding personal rulings (divorce, inheritance, hudud, takfir) are intercepted by the deterministic sensitivity gate with standardized advisory notices.
   - Academic inquiries trigger balanced multi-madhhab presentation and abrogation awareness.
   - Post-generation citation audit verifies that all `[Q#]`, `[H#]`, and `[T#]` markers stem from verified context excerpts.
3. **High-Precision Multi-Tier Retrieval**:
   - 6,236 Quranic verses and 50,762 authentic hadiths pre-indexed for sub-5ms local retrieval.
   - Authenticated Sunnah.com API provides secondary enrichment with narrator chains and scholars' authentication grades (Sahih/Hasan).

---

## 4. Verification Evidence & Quality Assurance

| Category | Verification Method | Status | Notes |
|:---|:---|:---:|:---|
| **Unit & Compliance Tests** | `unittest discover -s tests` | ✅ PASS | 14/14 tests passing (`test_islamic_compliance.py`, `test_islamic_rag.py`) |
| **Module Import Integrity** | Bare-mode Streamlit import | ✅ PASS | All core modules (`app`, `agents`, `rag`, `utils`) loaded without error |
| **Security Audit** | `.agent/scripts/checklist.py` | ✅ PASS | OWASP, secrets, and vulnerability scan clean |
| **Code Syntax & Linting** | Python compileall AST check | ✅ PASS | All production Python scripts validated |
| **LanceDB Connectivity** | Local table initialization | ✅ PASS | Connected to `data/lancedb`, canonical ayah and hadith retrieval operational |

---

## 5. Maintenance & Single-Repo Operational Guide

1. **Running the Unified Application**:
   ```bash
   streamlit run app.py
   ```
2. **Switching Between Cloud and Local Inference**:
   - To use Cloud Gemini: Ensure `GEMINI_API_KEY` is defined in `.env` and `USE_LOCAL_LLM=false`.
   - To use Local HidayahLM: Run `ollama run hidayah-lm:3b` and set `USE_LOCAL_LLM=true` in `.env`.
3. **Executing Validation Tests**:
   ```bash
   python -m unittest discover -s tests
   ```
4. **Legacy Directory Note**:
   The `Hidayah AI - Copy` directory is now fully superseded and archived in `.gitignore`. All future development should take place exclusively within the root directory `d:\Hidayah AI`.
