# Architecture Plan: Strict Scripture Grounding & Robust Dual-Retrieval Pipeline

> **Document:** `docs/PLAN-strict-scripture-grounding.md`  
> **Status:** APPROVED & READY FOR IMPLEMENTATION  
> **Target:** Hidayah AI (`hidayah-lm:3b` on CPU + LanceDB + Tavily Dual RAG)

---

## 1. Deep Root Cause Analysis: What Went Wrong?

### What is "Parametric Cross-Wiring"?
In Large Language Models, knowledge exists in two places:
1. **Parametric Memory:** The weights formed during pretraining across billions of tokens.
2. **Contextual Memory (RAG):** The explicit text injected into the prompt via the context window.

When a model is relatively small (3 billion parameters like `Qwen2.5-3B`) and quantized to 4-bit (`Q4_K_M`), its attention heads have limited capacity. When the contextual memory provided is sparse or mismatched with the question, the model falls back to its parametric memory.

### The Exact Failure Mode in Query 1:
1. **Thematic Question:** The user asked *"What are the core spiritual themes of Surah Al-Kahf?"*.
2. **Thematic vs. Verse RAG Mismatch:**
   - Raw vector search on 6,236 individual verses returned only 2 isolated verses:
     - `18:3` (*"wherein they will abide forever"*)
     - `18:85` (*"so he followed a way [Dhul-Qarnayn]"*)
   - Neither of these two verses explains the overarching 4 trials of Surah Al-Kahf (Trial of Faith, Trial of Wealth, Trial of Knowledge, Trial of Power).
3. **Web Search Was Completely Blocked:**
   - Because `has_local_scriptures` was `True` (since 2 verses were returned), the previous code suppressed web search to save tokens.
   - Consequently, the model had **zero** thematic summaries or Tafseer excerpts in its context!
4. **Parametric Cross-Wiring Occurred:**
   - The model attempted to recall Islamic themes from its internal weights.
   - It recalled the spiritual theme of *Qadar* (Divine Decree).
   - The authentic verse on divine decree is **Surah Al-Qamar 54:49** (*"Inna kulla shay'in khalaqnahu bi-qadar"*).
   - But because the conversation and prompt were heavily conditioned on the number **18 (Al-Kahf)**, its attention mechanism cross-wired the numbers: it combined Surah index **18** with Ayah **49**, producing:
     `[Quran 18:49] "Indeed, We have created all things in accordance with a decree."`
   - In reality, Surah Al-Kahf 18:49 describes the Book of Deeds on the Day of Judgment (*"Wa wudi'a al-kitabu fa-tara al-mujrimeen..."*).

---

## 2. The 4-Pillar Architectural Solution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       USER QUERY (Thematic or Specific)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
     Local LanceDB (50,762 Hadiths               Compact Web Thematic Search
        + 6,236 Quran Verses)                   (Domain-Verified: IslamQA/Yaqeen)
  • Top 2 Verses (clean snippets)              • 1-2 curated excerpts (max 300 chars)
  • Top 2 Hadiths (clean snippets)             • Token budget capped at ~100 tokens!
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                     Context Streamliner & Strict Prompt
             • Context strictly capped at <1,800 characters (~400 tokens)
             • Strict Directive: "Do NOT invent verse numbers. If describing
               stories or themes not in context, refer to them conceptually."
                                       │
                                       ▼
                           HidayahLM 3B (Local CPU)
                           Real-Time Token Streaming
                                       │
                                       ▼
                   Post-Generation Canonical Verification
       • Validate [Q#] and [H#] markers against retrieved context.
       • Check cited [Surah:Ayah] against local LanceDB 6,236 verses.
       • Auto-append corrective scholarly footnote if cross-wiring detected!
                                       │
                                       ▼
                       Streamlit UI (Instant Streaming)
```

### Pillar 1: Smart Dual Retrieval (Local LanceDB + Compact Thematic Web)
- For thematic questions (e.g., *"themes of Surah Al-Kahf"*, *"lessons of battle of Badr"*), we query **both**:
  1. Local LanceDB for authentic primary scriptural anchors (verses & hadiths).
  2. Domain-verified Web Search (Tavily restricted to `islamqa.info`, `sunnah.com`, `quran.com`) for thematic synthesis, but **hard-capped to 350 characters**.
  - Total context stays under **500 tokens**, completely avoiding CPU timeouts while feeding the model the exact thematic knowledge (the 4 trials).

### Pillar 2: Strict Negative Constraints in Generation Prompt
- In `agents/scholar.py`:
  - *"CRITICAL ACCURACY DIRECTIVE: You must NEVER invent or misattribute verse numbers. If a verse number (e.g. [18:49]) is not explicitly provided in the Context, DO NOT assign an arbitrary chapter and verse number. Instead, cite the story or concept by name (e.g. 'In the story of the People of the Cave...')."*

### Pillar 3: Canonical LanceDB Post-Audit Verifier
- In `utils/islamic_guardrails.py` (`verify_grounded_citations`):
  - Add `[Q\d+]` to the citation marker audit regex.
  - For any cited verse like `18:49`, query local LanceDB `canonical_quran` table in 0.5ms:
    - Compare the English text in the model's response with the true canonical text in LanceDB.
    - If a mismatch is detected (e.g. text of 54:49 cited as 18:49), the verifier automatically appends a helpful academic footnote:
      `> 🔍 Scholarly Note: The quoted text on divine decree is from Surah Al-Qamar (54:49). Surah Al-Kahf (18:49) pertains to the Book of Deeds.`

### Pillar 4: Real-Time Token Streaming in UI (`st.write_stream`)
- In `agents/scholar.py` and `ui/chat_panel.py`:
  - Support Python generator streaming (`requests.post(..., stream=True)` with SSE decoding).
  - Use `st.write_stream` in Streamlit so words begin rendering on screen within **2 to 3 seconds** of submitting the prompt, providing a 10x more responsive user experience.

---

## 3. Implementation Task Breakdown

| Step | File | Description | Complexity |
|---|---|---|---|
| **Step 1** | `agents/scholar.py` | Add compact dual retrieval (LanceDB scriptures + 1 compact web thematic snippet) and strict negative citation constraints. | Medium |
| **Step 2** | `utils/islamic_guardrails.py` | Upgrade `verify_grounded_citations` to audit `[Q#]` markers and perform LanceDB canonical verse text cross-checking. | Medium |
| **Step 3** | `agents/scholar.py` & `ui/chat_panel.py` | Implement Ollama token streaming (`stream_scholar_response`) and render via `st.write_stream`. | Medium |
| **Step 4** | `scratch/test_enhanced_grounding.py` | End-to-end verification of dual retrieval, streaming, and Surah Al-Kahf thematic query. | Low |

---

## 4. Verification Criteria
1. Asking *"What are the core spiritual themes of Surah Al-Kahf?"* produces:
   - Coverage of the 4 trials of Al-Kahf (Faith, Wealth, Knowledge, Power).
   - Zero misattributed verse numbers (no 18:49 with 54:49 text).
   - Prompt context remains strictly under 1,800 characters (<450 tokens).
2. CPU generation begins displaying tokens within 3–4 seconds via streaming.
3. Total CPU completion remains <60 seconds.
4. No external API quota or rate limits hit.
