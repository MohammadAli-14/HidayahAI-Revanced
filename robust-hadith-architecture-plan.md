# 🕌 Master Architecture & Implementation Plan: Theological-Grade Hadith Takhrīj & Retrieval Engine

> **Document Version:** 2.0 (Post-Deep-Think & Theological Integrity Audit)  
> **Target System:** Hidayah AI (Local & Edge Production Workstation)  
> **Status:** Final Implementation Plan  
> **Core Objective:** Establish a fault-tolerant, religiously authenticated Hadith retrieval and verification system that guarantees zero dependence on stalled external API queues while enforcing strict classical Takhrīj standards (Arabic Matn, Isnad, and Named Scholar Gradings).

---

## 1. Theological & Epistemic Foundations

In classical Islamic jurisprudence (*Usul al-Fiqh*) and Hadith criticism (*Mustalah al-Hadith*), deploying automated generative AI to religious scripture imposes four inviolable constraints:

1. **Textual Primacy (*Asl al-Matn*):**  
   English translations are human interpretive approximations (*Tarjamah Ma'nawiyyah*). The sacred evidence (*Hujjah*) resides strictly in the original vocalized Arabic text (*Matn*). A scholarly application must never deliver an English excerpt without verifiable binding to its canonical Arabic source.
2. **Attributed Authenticity (*Ijtihad fi al-Tashih*):**  
   Hadith grading is an interpretive scholarly evaluation (*Ijtihad*), not an objective mathematical constant. Presenting a blanket "Sahih" or "Da'if" without naming the evaluating authority (*e.g., Al-Albani, Darussalam, or Allama Zubair Ali Zai*) misrepresents Islamic scholarly consensus.
3. **Decoupled Discovery from Citation:**  
   Conceptual thematic research requires high-recall semantic vector and BM25 lexical search (handled offline by local LanceDB across 50,762 narrations). Specific coordinate verification (*Takhrīj*, e.g., "Sahih al-Bukhari #1") requires exact $O(1)$ deterministic index matching.
4. **Offline Sovereignty & Data Immortality:**  
   A religious tool cannot fail or change its verdict because an external web service is rate-limited, down, or blocked by a 2,975-ticket approval queue. Any retrieved external text must be cached and validated against local canonical indices.

---

## 2. Strategic Decision Matrix: Options & Recommendations

### 📌 Decision 1: Textual Integrity & Linguistic Representation
* **(Recommended) Option 1: Dual-Script Canonical Representation (Arabic Matn + English Translation + Isnad Chain)**
  * *Rationale:* Parallel asynchronous retrieval (`ara-{book}` + `eng-{book}`) injects both the authentic vocalized Arabic text and the reliable translation into the context stream. The model can cross-examine Arabic theological roots (*e.g., Niyyah, Ighlaq, Riba*) rather than guessing from an English translation.
  * *Performance Impact:* ~40–80 ms concurrent network latency (completely masked by Streamlit background worker).
* **Option 2: English-Only with External Web Anchor**
  * *Rationale:* Fetches only the English translation and attaches a link to Sunnah.com.
  * *Why Not Recommended:* Compromises theological rigor; researchers cannot verify Arabic diacritics or subtle word variations without leaving the app.

---

### 📌 Decision 2: Authenticity & Takhrīj Attribution
* **(Recommended) Option 1: Named Scholarly Attribution Badges**
  * *Rationale:* The CDN `/info.json` and edition records supply structured grading objects. Hidayah AI will render:  
    `Grade: Sahih (Authentic) — Verified by Sheikh Nasiruddin al-Albani & Darussalam Research Division`.
  * *Why Recommended:* Prevents sectarian dispute and adheres to classical academic etiquette (*Adab al-Ikhtilaf*).
* **Option 2: Flattened Binary Label ("Authentic" vs "Unverified")**
  * *Rationale:* Simpler UI layout.
  * *Why Not Recommended:* Violates scholarly transparency; obscures which classical methodology (*Mutaqaddimun* vs. *Muta'akhkhirun*) was applied.

---

### 📌 Decision 3: Storage & Offline Sovereignty
* **(Recommended) Option 1: Self-Enriching Hybrid Persistence (RAM TTL Cache + LanceDB Storage)**
  * *Rationale:* When a verified narration with detailed multi-scholar grades is fetched via CDN, it is cached in RAM for instant 0ms retrieval AND asynchronously indexed into the local `canonical_hadiths.lance` store. The local offline corpus grows smarter and richer with every query.
* **Option 2: Ephemeral RAM Cache Only (`@st.cache_data`)**
  * *Rationale:* Zero disk write overhead.
  * *Why Not Recommended:* Re-fetches identical data on app restarts; does not improve offline capabilities.

---

## 3. End-to-End Architectural Pipeline

```
                                [User Inquiry]
                                       │
                                       ▼
                     [agents/router.py: Intent Classifier]
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │                                                     │
   [Topical / Thematic Search]                          [Specific Coordinate Query]
   e.g. "hadith about patience in trials"               e.g. "Abu Dawud 1035" or "Bukhari 1"
            │                                                     │
            ▼                                                     ▼
┌──────────────────────────────────────┐            ┌──────────────────────────────────────┐
│  Tier 1: Local Canonical LanceDB     │            │  Tier 2: Keyless Edge CDN Bridge     │
│  * 50,762 Narrations                 │            │  * fawazahmed0/hadith-api via jsDelivr│
│  * Tantivy BM25 + Vector Hybrid Search│            │  * Concurrent Dual-Script (AR + EN)  │
│  * Sub-5ms search, 100% Offline      │            │  * Structured Scholarly Grades       │
└──────────────────┬───────────────────┘            │  * Fallback: raw.githubusercontent   │
                   │                                └──────────────────┬───────────────────┘
                   │ (If local hadith lacks grades)                    │ (If CDN unreachable)
                   └───────────────────┬───────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Verification & Evidence Normalizer (utils/evidence.py)                                  │
│  * Validates Arabic vocalization and English translation                                 │
│  * Attaches Named Authenticity Badges (Sahih / Hasan / Da'if)                            │
│  * Generates Canonical URL: https://sunnah.com/{collection}/{hadith_number}              │
│  * Persists rich metadata to Local LanceDB Table                                         │
└──────────────────────────────────────┬───────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Tier 3: Supplementary Web Commentary (agents/web_search.py via Tavily)                 │
│  * Triggered ONLY for complex jurisprudence questions                                    │
│  * Domain allowlist: islamqa.info, seekersguidance.org, yaqeeninstitute.org              │
│  * Hard-budgeted to <= 350 characters                                                    │
└──────────────────────────────────────┬───────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  Inference Tier: HidayahLM-3B (Ollama Q4_K_M on CPU)                                     │
│  * Grounded exclusively in verified excerpts [H1], [H2], [Q1]                            │
│  * Mandatory closing disclaimer: "And Allah knows best (Allahu A'lam)"                   │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Step-by-Step Implementation Action Plan

### Step 1: Configuration & Collection Manifest
* **Target File:** `utils/config.py`
* **Changes:**
  - Define `HADITH_CDN_MIRRORS`:
    - Primary: `https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1`
    - Secondary: `https://raw.githubusercontent.com/fawazahmed0/hadith-api/1`
  - Define `HADITH_COLLECTION_REGISTRY`: Mapping standard user terms (`bukhari`, `sahih bukhari`, `muslim`, `abu dawud`, `tirmidhi`, `nasai`, `ibn majah`, `muwatta malik`, `ahmad`) to:
    - English edition: `eng-bukhari`, `eng-abudawud`, etc.
    - Arabic edition: `ara-bukhari`, `ara-abudawud`, etc.
    - Urdu edition: `urd-bukhari`, `urd-abudawud`, etc.
  - Set `HADITH_NET_TIMEOUT = 3.5` seconds.

### Step 2: High-Performance Keyless Takhrīj Adapter
* **Target File:** `utils/sunnah_api.py`
* **Changes:**
  - Implement `fetch_dual_script_hadith(collection, hadith_number, lang="en")`:
    - Uses Python `concurrent.futures.ThreadPoolExecutor(max_workers=2)` to fetch both English translation and Arabic vocalized text in parallel.
    - Extracts structured scholarly grading array: `[{"scholar": g["name"], "grade": g["grade"]}]`.
    - Handles failover transparently between jsDelivr and GitHub Raw.
  - Upgrade `fetch_hadith_by_reference()`:
    1. If `SUNNAH_API_KEY` exists in `.env` $\to$ query `api.sunnah.com`.
    2. If `SUNNAH_API_KEY` missing $\to$ query `fetch_dual_script_hadith()`.
    3. If network fails $\to$ query local `search_canonical_hadiths()`.
  - Attach `@st.cache_data(ttl=86400)` with memory guard.

### Step 3: Cascade Logic & Reference Router Integration
* **Target File:** `utils/hadith_api.py`
* **Changes:**
  - Add regular expression detector for hadith citations:
    `HADITH_REF_PATTERN = r"\b(bukhari|muslim|tirmidhi|abu\s*dawud|dawud|nasai|ibn\s*majah|malik|ahmad)\s*(?:hadith|no|number|#)?\s*(\d+)\b"`
  - When pattern matches $\to$ route directly to Tier 2 (Exact Takhrīj) to get instant verbatim Arabic + English + Grades.
  - When pattern does not match $\to$ route to Tier 1 (LanceDB Tantivy BM25 + Vector Search over 50,762 records).

### Step 4: Theological Evidence Formatting & Source Cards
* **Target File:** `utils/evidence.py`
* **Changes:**
  - Enhance `normalize_hadith()` to store:
    - `arabic_text`: Full vocalized Arabic Matn.
    - `english_text`: Cleaned English translation.
    - `scholars_grades`: List of certifying scholars.
    - `canonical_url`: Direct clickable link to `https://sunnah.com/{collection}/{hadith_number}`.

### Step 5: Test Suite & Verification Checklist
* **Target File:** `tests/test_hadith_retrieval.py`
* **Test Cases:**
  1. `test_bukhari_1_dual_script`: Verifies exact wording of Bukhari #1 in both Arabic and English.
  2. `test_abudawud_1035_grades`: Verifies extraction of Al-Albani and Darussalam Sahih grades.
  3. `test_offline_fallback`: Verifies that cutting network access falls back smoothly to local LanceDB without raising exceptions.
  4. `test_theological_compliance_suite`: Execute `python -m unittest discover -s tests`.
  5. `test_system_checklist`: Run `python .agent/scripts/checklist.py .` (ensuring 6/6 audits green).
