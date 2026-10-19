# Project Plan: Robust Local Pipeline & Self-Contained Islamic RAG

## 1. Context & Architectural Diagnosis (Phase -1)

### Shortcoming A: Hadith Retrieval Bypasses Local Database
- **Observation in logs**: `[hidayah.hadith_api] WARNING — sunnah.com API not configured, skipping` -> `Primary hadith source returned 0 results, falling back to web search`.
- **Root Cause**: `utils/hadith_api.py` was hardcoded to look for a remote `api.sunnah.com` key (which is not configured) and then fell back to Tavily web search across the internet, completely ignoring the **50,762 authentic canonical Hadiths** already embedded in our local LanceDB database (`canonical_hadiths`).
- **Impact**: Slows down every verse lookup by 5–10 seconds, consumes internet bandwidth, and returns web commentary instead of authentic Hadith text.

### Shortcoming B: Intent Router Crashes on Gemini Quota
- **Observation in logs**: `[hidayah.router] ERROR — Classification error: 429 RESOURCE_EXHAUSTED`.
- **Root Cause**: `agents/router.py` always calls Gemini API for basic intent classification. When Google's free tier (20 requests/day) is exhausted, the router crashes and defaults blindly.
- **Impact**: Makes the application dependent on cloud quotas even when the user wants to run locally.

### Shortcoming C: Context Bloat Causes CPU Timeout (>120s)
- **Observation in logs**: `[LOCAL LLM] Dispatching prompt to hidayah-lm:3b` -> `WARNING — Local LLM fallback failed in scholar agent: Read timed out. (read timeout=120)`.
- **Root Cause**: In `agents/scholar.py`, the prompt assembled 3 Quran verses + 3 Hadiths + 6 full web articles + system prompt (~3,700 tokens). On consumer CPU without a dedicated CUDA GPU, processing 3,700 tokens (prefill) plus generating 500 tokens takes ~140 seconds. Because `timeout=120`, the connection aborted right before completion.
- **Impact**: Local inference failed, causing an unwanted failover to Gemini, which was already rate-limited (429), resulting in `"API Error: This model is currently experiencing high demand"`.

---

## 2. Targeted Action Plan (Phase 1)

### Step 1: Wire Local LanceDB as the Primary Hadith Engine
- **File**: `utils/hadith_api.py`
- **Action**:
  1. Import `search_canonical_hadiths` from `rag.lancedb_store`.
  2. In `fetch_related_hadith()`, search local LanceDB FIRST.
  3. Format the top matching authentic Hadiths (Bukhari, Muslim, Abu Dawud, Tirmidhi, etc.) with book title, hadith number, chapter, and text.
  4. Only fall back to web search if local LanceDB yields zero results.
- **Outcome**: Hadith retrieval becomes **instant (<10ms)**, 100% offline, authentic, and removes the "Primary hadith source returned 0 results" warning.

### Step 2: Implement Zero-Cloud Local Heuristic Intent Router
- **File**: `agents/router.py`
- **Action**:
  1. Add a high-precision, instant rule-based classifier:
     - Regex / keywords for Quran verses (e.g., `verse 255`, `surah 18`, `ayah 1`) -> `VERSE_LOOKUP`.
     - Sensitive personal fiqh terms (e.g., `talaq`, `divorce`, `inheritance`, `mirath`, `khula`) -> `SENSITIVE_FIQH`.
     - Hadith terminology (e.g., `hadith`, `isnad`, `authentic`, `bukhari`, `sahih`) -> `HADITH_AUTHENTICATION`.
     - PDF references -> `PDF_ANALYSIS`.
     - General topics -> `SCHOLARLY_RESEARCH`.
  2. When `USE_LOCAL_LLM=True` or when Gemini returns 429, use the local heuristic router immediately.
- **Outcome**: Intent routing runs in **0.001 seconds**, uses 0 API tokens, and never throws 429 errors.

### Step 3: Streamline Context for Fast CPU Inference (<30s)
- **File**: `agents/scholar.py`
- **Action**:
  1. When `USE_LOCAL_LLM=True`:
     - If local canonical Quran and Hadiths are found in LanceDB, **skip the slow web search**. Scriptural authority is superior to general web blogs.
     - Keep the context lean: Top 2 Ayahs + Top 2 Hadiths (~600 tokens).
     - Set `max_tokens` to `400` (~250 words, ideal for concise scholarly synthesis).
     - Set HTTP client timeout to `180` seconds to give CPU ample headroom.
- **Outcome**: Reduces CPU prefill latency from 140s down to **18–25 seconds**, completely eliminating timeouts.

### Step 4: True Self-Contained Local Mode (No Gemini Fallback Loop)
- **File**: `agents/scholar.py`
- **Action**:
  1. When running in local mode, if the Gemini API key is rate-limited (429), prevent the code from attempting an invalid Gemini fallback.
  2. If local LLM needs a retry, retry locally with an ultra-compact prompt instead of failing to an exhausted cloud API.
- **Outcome**: The app becomes a truly standalone, resilient local Islamic research workstation.

---

## 3. Verification & Acceptance Criteria (Phase 4)

1. **Hadith Test**: Query an Ayah; verify terminal logs show `LanceDB returned X canonical hadiths` instead of `sunnah.com skipping / falling back to web search`.
2. **Router Test**: Verify intent routing completes in 0ms without any `429 RESOURCE_EXHAUSTED` logs.
3. **Speed Test**: Ask `"What are the central spiritual themes of Surah Al-Ikhlas?"`; verify that `hidayah-lm:3b` completes in under **30 seconds** on CPU.
4. **Resilience Test**: Disconnect internet or use an exhausted Gemini key; verify the entire app continues to answer questions using local LanceDB + local `hidayah-lm:3b`.
