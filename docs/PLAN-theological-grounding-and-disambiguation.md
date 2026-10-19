# Master Implementation Plan: Theological Grounding, Verse Disambiguation & Hadith Anti-Hallucination

## Objective
Remediate the theological hallucinations, context-bleed errors, and Hadith Matn omissions discovered during live testing of Hidayah AI, elevating the system to absolute scholarly compliance (*Mustalah al-Hadith*, *Usul al-Fiqh*, *Fiqh al-Muqaran*).

---

## 1. Root Cause Summary & Defect Log

| # | Discovered Defect | Root Cause | Remediation Target |
|---|---|---|---|
| 1 | **Hadith Matn Omission (Bukhari 1, Abu Dawud 1035)** | CDN fetched Matn & grades into metadata, but small 3B model summarized it away into an evasive 1-liner. | Directly format and inject the Canonical Hadith Card (Arabic Harakat + English + Scholar Grades) into the response. |
| 2 | **Context-Bleed (Kahf 18:49 & Qamar 54:49 answered with Al-Faatiha)** | `VERSE_LOOKUP` intent in `agents/scholar.py` blindly injected `window[:10]` (the background reader screen's Juz 1 Al-Faatiha ayahs and 10 tafsirs). | Parse explicit `Surah:Ayah` numerical patterns in query; suppress background screen window and retrieve *only* the cited verses and their exegeses. |
| 3 | **Fabricated Hadith Attributed to Bukhari ("Seek knowledge in China")** | Vector search matched keyword "knowledge" to Bukhari #114. Small 3B model assumed the user's quote was part of Bukhari #114 due to "Answer based strictly on context" prompt. | Implement Curated Classical Authenticity Guardrail for famous unauthentic/fabricated narrations + strict negative attribution instructions in prompt. |
| 4 | **Comparative Fiqh (Raf' al-Yadayn) Retrieval Miss** | Phrase "four Sunni schools of thought" missed keyword trigger in `router.py`, routed to generic `SCHOLARLY_RESEARCH`, retrieving unrelated verses. | Expand `fiqh_patterns` to catch four schools / madhhabs / ikhtilaf / prayer variations and mandate 4-madhhab synthesis directive. |

---

## 2. Technical Implementation Architecture

### Pillar 1: Deterministic Canonical Hadith Card (`agents/scholar.py` & `utils/hadith_api.py`)
- Detect specific Hadith references (`Bukhari 1`, `Abu Dawud 1035`, etc.) via `resolve_hadith_reference()`.
- Return a dedicated, verified markdown/HTML card containing:
  - Header with Collection name and Hadith number
  - Authentication badge with named scholar grades (*Al-Albani*, *Zubair Ali Zai*, etc.)
  - Complete Arabic text with Harakat in RTL styling
  - Verified English translation
  - Direct canonical link to Sunnah.com
- If the query is an inquiry about the Hadith's text or meaning, include both the canonical card and scholarly exegesis.

### Pillar 2: Surah/Ayah Numerical Disambiguation (`agents/scholar.py`)
- Extract all `(\d{1,3}):(\d{1,3})` pairs from the query string.
- When explicit verses are mentioned:
  - Suppress `ayah_window` from the current browser session.
  - Fetch exact verses from LanceDB `canonical_quran` via `get_canonical_ayah()`.
  - Fetch authentic Tafsir (Ibn Kathir / Jalalayn) specifically for the matched verses.
  - Present side-by-side comparison with precise theological boundaries.

### Pillar 3: Classical Authenticity Guardrail (`utils/hadith_api.py`)
- Curate classical verification database for known unauthentic/weak narrations:
  - "Seek knowledge even unto China" -> *Mawdu'* / *Da'if Jiddan* (Ibn al-Jawzi, Al-Albani). Alternative: Sunan Ibn Majah #224 (*Sahih*).
  - "Differences of opinion among my Ummah is a mercy" -> *La Asla Lahu* (Al-Subki, Al-Albani).
  - "Cleanliness is from faith" -> *Da'if*. Alternative: Sahih Muslim #223 (*Sahih*).
  - "Love of one's country is from faith" -> *Mawdu'*.
- Add negative constraint to scholar prompts: Never claim a quoted statement belongs to a canonical source unless the exact text is present in the source excerpt.

### Pillar 4: Comparative Fiqh Expansion (`agents/router.py` & `utils/islamic_guardrails.py`)
- Expand regex in `router.py` and `islamic_guardrails.py` to recognize:
  `r"\b(four (?:sunni )?(?:schools?(?: of thought)?|madhhabs?)|raf'? al-?yadayn|raising hands|qunoot|tashahhud differences|ikhtilaf)\b"`
- Set `requires_madhhab_synthesis = True`.
- Ensure multi-school balanced presentation across Hanafi, Maliki, Shafi'i, and Hanbali traditions.

---

## 3. Verification & Testing Strategy
1. **Unit Tests:** Add test cases in `tests/test_islamic_compliance.py` and `tests/test_hadith_retrieval.py`.
2. **Regression Check:** Run `python -m unittest discover -s tests`.
3. **Master Audit:** Run `python .agent/scripts/checklist.py .`.
