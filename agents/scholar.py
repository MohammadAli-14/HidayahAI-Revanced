"""
Hidayah AI — Scholar Agent
Uses Gemini 2.5 Flash for grounded scholarly responses with strict citation rules,
Islamic theological guardrails, and citation verification.
"""

from google import genai
import requests
from utils.config import (
    MODEL_SCHOLAR,
    GEMINI_API_KEY,
    get_gemini_client,
    USE_LOCAL_LLM,
    LOCAL_LLM_URL,
    LOCAL_LLM_MODEL,
)
from agents.web_search import search_web
from agents.context_retriever import get_context_bundle_for_window
from utils.trust import is_trusted_scholarly
from utils.islamic_guardrails import (
    check_fatwa_sensitivity,
    classify_fatwa_sensitivity,
    verify_grounded_citations,
)
from rag.lancedb_store import search_canonical_quran, search_canonical_hadiths
from utils.logger import get_logger

log = get_logger("scholar")

SCHOLAR_SYSTEM_PROMPT = """You are Hidayah AI, an elite Islamic scholarly research assistant grounded in traditional Islamic Sciences (Usul al-Fiqh, Takhreej al-Hadith, Tafseer, and Classical Arabic).

THEOLOGICAL & ACADEMIC DIRECTIVES (CRITICAL — strict compliance required):

1. STRICT SOURCE GROUNDING & ANTI-HALLUCINATION:
- ONLY cite Quranic verses, Tafseer passages, and Hadiths that are explicitly provided in the Context below.
- NEVER fabricate, guess, or invent Hadith text, chain of narrators (Isnad), or specific scholarly rulings.
- NEVER synthesize or generate your own classical Arabic religious text from scratch; only reproduce the exact Arabic text provided in the verified context excerpts.
- If the context does not contain verified sources for a specific detail, state with humility: "I do not have authenticated primary sources in my immediate corpus for this specific inquiry. Please consult a qualified Islamic scholar."

2. HADITH AUTHENTICATION & TAKHREEJ:
- When referencing a Hadith, ALWAYS state its primary book collection, Hadith reference number, and authentication grade (e.g., Sahih, Hasan, Da'if) as indicated in the context.
- Distinguish clearly between sound (Sahih/Hasan) narrations and weak (Da'if) narrations. Never present weak narrations as binding theological or legal proofs.

3. ABROGATION (NASIKH & MANSUKH) AWARENESS:
- When discussing verses with historical revelation stages (e.g., gradual prohibition of alcohol from 2:219 to 4:43 to 5:90, or the change of Qibla), ALWAYS clarify the chronological progression and final established ruling (al-Hukm al-Istiqrari) according to classical consensus (Ijma').

4. MADHHAB BALANCE & NEUTRALITY (IKHTILAF):
- In practical Fiqh matters where valid scholarly differences exist across the 4 Sunni Madhhabs (Hanafi, Maliki, Shafi'i, Hanbali) or Ja'fari jurisprudence, present each scholarly position neutrally with attribution. NEVER assert one localized opinion as universal dogma.

5. SENSITIVE FIQH & PERSONAL STATUS MATTERS:
- In inheritance (*Mirath*), outline the statutory priorities: 1) Funeral expenses, 2) Debt settlements, 3) Bequests (*Wasiyyah*, max 1/3), 4) Scriptural division under Surah An-Nisa 4:11-12.
- In marital dissolution (*Talaq* / *Khula*), explain the legal distinctions between Talaq al-Sunnah and Talaq al-Bid'ah, the necessity of examining intent (*Niyyah*) and mental state (*Ighlaq*), and emphasize that personal legal validity can only be evaluated by human jurists.

6. FATWA BOUNDARY & SCHOLARLY ETIQUETTE (ADAB):
- You are an educational and academic research assistant, NOT a Mufti or Qadi. NEVER issue personal binding verdicts ("I declare that...", "You must divorce...").
- Begin responses with a respectful greeting when appropriate.
- Cite sources clearly using [Q#] for Quran, [H#] for Hadith, [T#] for Tafseer, and [Page #] for documents.
- Conclude responses with traditional scholarly humility: "And Allah knows best (Allahu A'lam). Please consult qualified scholars for personal binding rulings."
- Support English, Arabic, and Urdu based on the user's inquiry language."""



def _generate_scholar_local(prompt: str) -> str | None:
    """Generate scholarly response using local Ollama/vLLM instance."""
    try:
        payload = {
            "model": LOCAL_LLM_MODEL,
            "messages": [
                {"role": "system", "content": SCHOLAR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        }
        res = requests.post(f"{LOCAL_LLM_URL}/chat/completions", json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        log.warning(f"Local LLM fallback failed in scholar agent: {e}")
    return None


def get_scholar_response(
    query: str,
    intent: str,
    ayahs_context: list[dict] | None = None,
    ayah_window: list[dict] | None = None,
    tafseer_language: str = "en",
    pdf_context: str | None = None,
) -> str:
    """
    Generate a scholarly response using Gemini 2.5 (or local LLM) with strict Islamic guardrails,
    fusing canonical LanceDB Quran & Hadiths with trusted scholarly sources.

    Args:
        query: User's question
        intent: Classified intent (VERSE_LOOKUP, SCHOLARLY_RESEARCH, SENSITIVE_FIQH, HADITH_AUTHENTICATION, PDF_ANALYSIS)
        ayahs_context: Current ayahs being viewed (for verse context)
        pdf_context: Retrieved PDF chunks (for RAG answers)

    Returns:
        Formatted response string with verified citations and sources
    """
    # 1. Pre-query Two-Tier Sensitivity Gate
    sensitivity_info = classify_fatwa_sensitivity(query)
    if sensitivity_info["is_personal_verdict"]:
        log.info(f"Personal verdict request intercepted: {sensitivity_info['topic']}")
        return sensitivity_info["advisory_notice"]

    client = get_gemini_client()
    if not client and not USE_LOCAL_LLM:
        return "⚠️ **Gemini API key not configured.** Please add `GEMINI_API_KEY` to your settings (Secrets on Streamlit Cloud or .env locally)."

    try:
        log.info(f"Assembling context. Intent: {intent}")
        context_parts = []
        grounded_sources = []

        # 2. Canonical LanceDB Retrieval for Scholarly / Fiqh / Hadith Inquiries
        if intent in {"SCHOLARLY_RESEARCH", "SENSITIVE_FIQH", "HADITH_AUTHENTICATION"}:
            # A. Retrieve Authentic Canonical Quran Verses
            try:
                canonical_verses = search_canonical_quran(query, top_k=3)
                if canonical_verses:
                    quran_context_lines = []
                    for idx, v in enumerate(canonical_verses, start=1):
                        v_text = v.get("text", "").strip()
                        if v_text:
                            quran_context_lines.append(f"[Q{idx}]\n{v_text}")
                            surah_info = f"Surah {v.get('surah_name', '')} ({v.get('surah_number', '')}:{v.get('ayah_number', '')})"
                            grounded_sources.append(f"[Q{idx}] {surah_info} | Juz {v.get('juz', '')} | canonical:verified")
                    if quran_context_lines:
                        context_parts.append("Canonical Quran Verses:\n" + "\n\n".join(quran_context_lines))
            except Exception as q_err:
                log.warning(f"Canonical Quran retrieval notice: {q_err}")

            # B. Retrieve Authentic Canonical Hadiths (50,762 corpus)
            try:
                canonical_hadiths = search_canonical_hadiths(query, top_k=3)
                if canonical_hadiths:
                    hadith_context_lines = []
                    for idx, h in enumerate(canonical_hadiths, start=1):
                        h_book = h.get("book", "Hadith Collection")
                        h_no = h.get("hadith_no", "")
                        h_chapter = h.get("chapter", "")
                        h_text = h.get("text", "").strip()
                        hadith_context_lines.append(
                            f"[H{idx}] {h_book} #{h_no} (Chapter: {h_chapter})\n{h_text}"
                        )
                        grounded_sources.append(f"[H{idx}] {h_book} #{h_no} | Chapter: {h_chapter} | canonical:verified")
                    if hadith_context_lines:
                        context_parts.append("Canonical Hadiths (50,762 Collection):\n" + "\n\n".join(hadith_context_lines))
            except Exception as h_err:
                log.warning(f"Canonical Hadith retrieval notice: {h_err}")

            # C. Supplementary Web Search (Domain-Verified Only)
            web_results = search_web(f"Islamic scholarly {query}")
            trusted_results = []
            for r in (web_results or []):
                url = r.get("url", "")
                if not url or is_trusted_scholarly(url):
                    trusted_results.append(r)
            if trusted_results:
                web_text = "\n\n".join(
                    f"Source: {r['title']}\nURL: {r['url']}\n{r['content']}"
                    for r in trusted_results[:2]
                )
                context_parts.append(f"Scholarly web references (domain-verified sources):\n{web_text}")

            # D. Sensitive Fiqh Multi-Madhhab Guidance Instruction
            if sensitivity_info["requires_madhhab_synthesis"]:
                context_parts.append(
                    "CRITICAL SENSITIVE JURISPRUDENCE DIRECTIVE:\n"
                    f"The question involves '{sensitivity_info['topic']}'.\n"
                    "1. Present the scriptural proofs from Quran and authentic Hadiths.\n"
                    "2. Detail the consensus (Ijma') and divergence (Ikhtilaf) across the 4 Sunni schools (Hanafi, Maliki, Shafi'i, Hanbali) neutrally.\n"
                    "3. Do not issue a personal ruling; remind the user that personal cases require human jurist adjudication."
                )

        elif intent == "VERSE_LOOKUP" and (ayah_window or ayahs_context):
            window = ayah_window or ayahs_context or []

            # Provide current verse context
            verses_text = "\n".join(
                f"[{a.get('surah_name', '')} {a.get('number_in_surah', '')}] Arabic: {a.get('arabic', '')}\n"
                f"English: {a.get('english', '')}\nUrdu: {a.get('urdu', '')}"
                for a in window[:10]
            )
            context_parts.append(f"Currently viewing these Quranic verses:\n{verses_text}")

            # Also check if query mentions a specific verse not in current window
            try:
                canonical_verses = search_canonical_quran(query, top_k=2)
                if canonical_verses:
                    extra_verses = []
                    for idx, v in enumerate(canonical_verses, start=1):
                        extra_verses.append(f"[Q-Ref{idx}] " + v.get("text", ""))
                    context_parts.append("Matched Quranic Canonical Verses:\n" + "\n\n".join(extra_verses))
            except Exception as q_err:
                log.warning(f"Verse lookup extra search notice: {q_err}")

            # Retrieve grounded Tafseer + Hadith across visible ayah window
            bundle = get_context_bundle_for_window(
                ayah_window=window[:10],
                tafseer_language=tafseer_language,
            )

            tafsir_context_lines = []
            hadith_context_lines = []
            tafsir_counter = 1
            hadith_counter = 1

            if bundle:
                tafsir_by_ayah = bundle.get("tafsir_by_ayah", {})
                hadith_by_ayah = bundle.get("hadith_by_ayah", {})
                citations = bundle.get("citations", [])

                for ayah_ref, tafsir_items in tafsir_by_ayah.items():
                    for item in tafsir_items[:2]:
                        tafsir_context_lines.append(
                            f"[T{tafsir_counter}] {item['source_name']} ({ayah_ref}, {item.get('language', '').upper()})\n"
                            f"{item['excerpt']}"
                        )
                        tafsir_source = (
                            f"[T{tafsir_counter}] {item['source_name']} | {ayah_ref} | "
                            f"lang:{item.get('language', '').upper()} | canonical:{item.get('canonical_status', 'unverified')}"
                        )
                        if item.get("canonical_url"):
                            tafsir_source += f" — {item['canonical_url']}"
                        grounded_sources.append(tafsir_source)
                        tafsir_counter += 1

                for ayah_ref, hadith_items in hadith_by_ayah.items():
                    for item in hadith_items[:1]:
                        hadith_context_lines.append(
                            f"[H{hadith_counter}] {item['source_name']} ({ayah_ref})\n{item['excerpt']}"
                        )
                        hadith_counter += 1

                for idx, citation in enumerate(citations, start=1):
                    citation_type = citation.get("type", "source")
                    source_name = citation.get("source_name", "Unknown Source")
                    reference = citation.get("reference", "")
                    language = (citation.get("language", "") or "").upper() or "N/A"
                    canonical_status = citation.get("canonical_status", "unverified")
                    canonical_url = citation.get("canonical_url", "")
                    ayah_ref = citation.get("metadata", {}).get("ayah_ref", "")
                    source_rank = citation.get("source_rank", 0)

                    line = (
                        f"type:{citation_type} | id:C{idx} | source:{source_name} | ref:{reference} | "
                        f"ayah:{ayah_ref} | lang:{language} | rank:{source_rank} | canonical:{canonical_status}"
                    )
                    if canonical_url:
                        line += f" | url:{canonical_url}"
                    grounded_sources.append(line)

            if tafsir_context_lines:
                context_parts.append("Authenticated Tafseer Context:\n" + "\n\n".join(tafsir_context_lines[:8]))
            if hadith_context_lines:
                context_parts.append("Related Hadith references:\n" + "\n\n".join(hadith_context_lines[:5]))

        elif intent == "PDF_ANALYSIS" and pdf_context:
            context_parts.append(f"Relevant excerpts from the uploaded document:\n{pdf_context}")

        # Assemble the full prompt
        full_prompt = query
        context_str = ""
        if context_parts:
            context_str = "\n\n---\n\n".join(context_parts)
            full_prompt = f"Context:\n{context_str}\n\n---\n\nUser Question: {query}"

        # 3. Generation (Local LLM or Gemini)
        answer = None
        if USE_LOCAL_LLM:
            answer = _generate_scholar_local(full_prompt)

        if not answer and client:
            log.info(f"Sending final prompt to {MODEL_SCHOLAR} (Context parts: {len(context_parts)})")
            response = client.models.generate_content(
                model=MODEL_SCHOLAR,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SCHOLAR_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )
            answer = response.text

        if not answer:
            return "⚠️ **Scholar Agent error:** The model returned an empty response. Please try again."

        log.info("Response generated successfully.")

        # 4. Post-generation Citation & Quran Reference Verification
        if context_str:
            answer = verify_grounded_citations(answer, context_str)

        # 5. Prepend Academic Advisory Header for Sensitive Inquiries
        if sensitivity_info["is_sensitive"] and sensitivity_info.get("advisory_notice"):
            answer = sensitivity_info["advisory_notice"] + "\n\n" + answer

        if grounded_sources:
            answer += "\n\nSources:\n" + "\n".join(f"- {src}" for src in grounded_sources)
        return answer

    except genai.errors.APIError as e:
        if e.code == 429:
            return "⚠️ **Scholar Agent is currently resting.** Hidayah AI is receiving a high volume of requests. Please wait a moment and try again."
        return f"⚠️ **API Error:** {str(e.message) if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        log.error(f"Scholar Agent error: {e}")
        return f"⚠️ **Scholar Agent error:** An unexpected error occurred. Please try again."
