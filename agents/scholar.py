"""
Hidayah AI — Scholar Agent
Uses Gemini 2.5 Flash for grounded scholarly responses with strict citation rules,
Islamic theological guardrails, and citation verification.
"""

from google import genai
import requests
import json
import time
import re
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
from rag.lancedb_store import (
    search_canonical_quran,
    search_canonical_hadiths,
    get_canonical_ayah,
)
from rag.surah_themes import detect_surah_in_query, get_surah_thematic_summary
from utils.hadith_api import (
    resolve_hadith_reference,
    check_unauthentic_hadith,
    format_hadith_card,
)
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
        log.info(f"[LOCAL LLM] Dispatching prompt to {LOCAL_LLM_MODEL} via Ollama ({LOCAL_LLM_URL})...")
        t0 = time.time()

        # hidayah-lm:3b has its comprehensive Islamic scholar system prompt compiled inside its Modelfile.
        payload = {
            "model": LOCAL_LLM_MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 768,
        }
        res = requests.post(f"{LOCAL_LLM_URL}/chat/completions", json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            elapsed = time.time() - t0
            log.info(f"[LOCAL LLM] {LOCAL_LLM_MODEL} generated response in {elapsed:.1f}s!")
            return content
        else:
            log.warning(f"[LOCAL LLM] Ollama returned HTTP {res.status_code}: {res.text}")
    except Exception as e:
        log.warning(f"Local LLM generation failed in scholar agent: {e}")
    return None


def stream_scholar_local(prompt: str):
    """
    Yield real-time streaming token chunks from local Ollama/vLLM instance.
    Enables Streamlit UI to begin rendering text within 2-3 seconds.
    """
    try:
        log.info(f"[LOCAL LLM STREAM] Initiating streaming prompt to {LOCAL_LLM_MODEL}...")

        payload = {
            "model": LOCAL_LLM_MODEL,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 768,
            "stream": True,
        }
        with requests.post(f"{LOCAL_LLM_URL}/chat/completions", json=payload, stream=True, timeout=120) as res:
            if res.status_code == 200:
                for line in res.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: ") and line_str.strip() != "data: [DONE]":
                            try:
                                chunk_json = json.loads(line_str[6:])
                                delta = chunk_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                pass
            else:
                log.warning(f"[LOCAL LLM STREAM] Ollama returned HTTP {res.status_code}: {res.text}")
    except Exception as e:
        log.warning(f"Local LLM streaming error: {e}")


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

    # 1b. Unauthentic & Fabricated Hadith Gate (Mustalah al-Hadith)
    unauth_hit = check_unauthentic_hadith(query)
    if unauth_hit:
        log.info(f"Unauthentic narration detected: {unauth_hit.get('status', 'Unauthentic')}")
        resp_lines = [
            "### ⚠️ Authentication Notice (*Takhrij & Naqd al-Hadith*)",
            f"**Narration Inquired:** {unauth_hit['statement']}",
            f"**Scholarly Classification:** `{unauth_hit['status']}`",
            "",
            "**Scholarly Evaluation:**",
            f"{unauth_hit['theological_verdict']}",
            "",
            f"**Graded by Classical Hadith Masters:** {unauth_hit['scholars']}.",
            "",
            "**Verified Scriptural Alternative:**",
            f"> {unauth_hit['authentic_alternative']}",
            "",
            "And Allah knows best (*Allahu A'lam*). Always verify religious sayings with classical scholarly collections.",
            "",
            "Sources:",
            f"- [H1] {unauth_hit['canonical_ref']} | Authenticity: Sahih / Verified Canonical Alternative | canonical:verified",
        ]
        return "\n\n".join(resp_lines)

    # 1c. Deterministic Canonical Hadith Reference Resolver
    hadith_ref = resolve_hadith_reference(query)
    is_direct_lookup = False
    if hadith_ref:
        q_clean = query.lower()
        is_direct_lookup = any(
            phrase in q_clean for phrase in [
                "what is", "show", "read", "text", "grading", "grade", "arabic and english",
                "in arabic", "in english", "bukhari 1", "abu dawud 1035", "hadith 1"
            ]
        ) and not any(kw in q_clean for kw in ["derive", "fiqh ruling", "explain the legal ruling", "philosophical"])

        if is_direct_lookup:
            log.info(f"Direct hadith lookup query matched: {hadith_ref.get('title')}")
            hadith_card = format_hadith_card(hadith_ref)
            final_resp = f"{hadith_card}\n\nAnd Allah knows best (*Allahu A'lam*)."
            final_resp += f"\n\nSources:\n- [H1] {hadith_ref.get('title')} | {hadith_ref.get('authority')} | canonical:{hadith_ref.get('canonical_status', 'verified')} — {hadith_ref.get('canonical_url', '')}"
            return final_resp

    client = get_gemini_client()
    if not client and not USE_LOCAL_LLM:
        return "⚠️ **Gemini API key not configured.** Please add `GEMINI_API_KEY` to your settings (Secrets on Streamlit Cloud or .env locally)."

    try:
        log.info(f"Assembling context. Intent: {intent}")
        context_parts = []
        grounded_sources = []

        # Check for explicit Surah:Ayah numerical references in the query (e.g. 18:49 and 54:49)
        explicit_verses = re.findall(r"\b(\d{1,3}):(\d{1,3})\b", query)
        exact_verses_loaded = False
        if explicit_verses:
            log.info(f"Explicit Quran verse references detected: {explicit_verses}")
            exact_quran_lines = []
            explicit_window = []
            for s_str, a_str in explicit_verses:
                s_num, a_num = int(s_str), int(a_str)
                if 1 <= s_num <= 114:
                    v_data = get_canonical_ayah(s_num, a_num)
                    if v_data:
                        v_text = v_data.get('text', '')
                        exact_quran_lines.append(f"[Q-{s_num}:{a_num}]\n{v_text}")
                        grounded_sources.append(
                            f"[Q{len(grounded_sources)+1}] Surah {v_data.get('surah_name', '')} ({s_num}:{a_num}) | Juz {v_data.get('juz', '')} | canonical:verified"
                        )
                        explicit_window.append({
                            "surah_number": s_num,
                            "number_in_surah": a_num,
                            "surah_name": v_data.get("surah_name", f"Surah {s_num}"),
                            "english": v_text,
                        })
            if exact_quran_lines:
                context_parts.append("Explicitly Cited Quranic Verses:\n" + "\n\n".join(exact_quran_lines))
                exact_verses_loaded = True

            # Retrieve grounded Tafseer specifically for the explicitly cited verses
            if explicit_window:
                try:
                    bundle = get_context_bundle_for_window(explicit_window, tafseer_language=tafseer_language)
                    tafsir_by_ayah = bundle.get("tafsir_by_ayah", {})
                    tafsir_counter = 1
                    tafsir_lines = []
                    for ayah_ref, tafsir_items in tafsir_by_ayah.items():
                        for item in tafsir_items[:1]:
                            snippet = item.get("excerpt", "").strip()[:400]
                            tafsir_lines.append(f"[T{tafsir_counter}] Tafseer for {ayah_ref} ({item['source_name']}):\n{snippet}")
                            grounded_sources.append(f"[T{tafsir_counter}] {item['source_name']} | {ayah_ref} | canonical:verified")
                            tafsir_counter += 1
                    if tafsir_lines:
                        context_parts.append("Classical Tafseer Exegesis for Cited Verses:\n" + "\n\n".join(tafsir_lines))
                except Exception as t_err:
                    log.warning(f"Error fetching tafseer for explicit verses: {t_err}")

        # 2. Canonical LanceDB Retrieval for Scholarly / Fiqh / Hadith Inquiries
        if intent in {"SCHOLARLY_RESEARCH", "SENSITIVE_FIQH", "HADITH_AUTHENTICATION"}:
            # A0. Retrieve Classical Surah Thematic Structure (if a specific Surah is queried and no explicit verses)
            if not exact_verses_loaded:
                try:
                    detected_surah = detect_surah_in_query(query)
                    if detected_surah:
                        surah_theme_text = get_surah_thematic_summary(detected_surah)
                        if surah_theme_text:
                            context_parts.append(f"Classical Surah Thematic Structure:\n{surah_theme_text}")
                            grounded_sources.append(f"[T1] Classical Surah Exegesis (Chapter {detected_surah}) | canonical:verified")
                except Exception as th_err:
                    log.warning(f"Surah thematic context notice: {th_err}")

            # A. Retrieve Authentic Canonical Quran Verses (only if no explicit verses and not an explicit hadith ref)
            if not exact_verses_loaded and not hadith_ref:
                try:
                    verse_k = 2 if USE_LOCAL_LLM else 3
                    canonical_verses = search_canonical_quran(query, top_k=verse_k)
                    if canonical_verses:
                        quran_context_lines = []
                        for idx, v in enumerate(canonical_verses, start=1):
                            v_text = v.get("text", "").strip()
                            if USE_LOCAL_LLM and len(v_text) > 250:
                                v_text = v_text[:250] + "..."
                            if v_text:
                                quran_context_lines.append(f"[Q{idx}]\n{v_text}")
                                surah_info = f"Surah {v.get('surah_name', '')} ({v.get('surah_number', '')}:{v.get('ayah_number', '')})"
                                grounded_sources.append(f"[Q{idx}] {surah_info} | Juz {v.get('juz', '')} | canonical:verified")
                        if quran_context_lines:
                            context_parts.append("Canonical Quran Verses:\n" + "\n\n".join(quran_context_lines))
                except Exception as q_err:
                    log.warning(f"Canonical Quran retrieval notice: {q_err}")

            # B. Retrieve Authentic Canonical Hadiths (50,762 corpus)
            if hadith_ref:
                h_text = hadith_ref.get("excerpt", "")
                h_title = hadith_ref.get("title", "Hadith Reference")
                h_auth = hadith_ref.get("authority", "Authentic Hadith")
                context_parts.append(f"Canonical Hadith Citation ({h_title}):\n{h_text}")
                grounded_sources.append(f"[H1] {h_title} | {h_auth} | canonical:{hadith_ref.get('canonical_status', 'verified')} — {hadith_ref.get('canonical_url', '')}")
            else:
                try:
                    hadith_k = 2 if USE_LOCAL_LLM else 3
                    canonical_hadiths = search_canonical_hadiths(query, top_k=hadith_k)
                    if canonical_hadiths:
                        hadith_context_lines = []
                        for idx, h in enumerate(canonical_hadiths, start=1):
                            h_book = h.get("book", "Hadith Collection")
                            h_no = h.get("hadith_no", "")
                            h_chapter = h.get("chapter", "")
                            h_text = h.get("text", "").strip()
                            if USE_LOCAL_LLM and len(h_text) > 250:
                                h_text = h_text[:250] + "..."
                            hadith_context_lines.append(
                                f"[H{idx}] {h_book} #{h_no} (Chapter: {h_chapter})\n{h_text}"
                            )
                            grounded_sources.append(f"[H{idx}] {h_book} #{h_no} | Chapter: {h_chapter} | canonical:verified")
                        if hadith_context_lines:
                            context_parts.append("Canonical Hadiths (50,762 Collection):\n" + "\n\n".join(hadith_context_lines))
                except Exception as h_err:
                    log.warning(f"Canonical Hadith retrieval notice: {h_err}")

            # C. Supplementary Compact Web Search (Domain-Verified Only)
            try:
                web_results = search_web(f"Islamic scholarly {query}")
                trusted_results = []
                for r in (web_results or []):
                    url = r.get("url", "")
                    if not url or is_trusted_scholarly(url):
                        trusted_results.append(r)
                if trusted_results:
                    best_r = trusted_results[0]
                    if best_r.get("url") and best_r.get("title") != "Search Error":
                        snippet = best_r.get("content", "").strip()[:350]
                        if snippet:
                            context_parts.append(f"Domain-Verified Scholarly Commentary [W1]:\nSource: {best_r.get('title', 'Reference')}\n{snippet}...")
                            grounded_sources.append(f"[W1] {best_r.get('title', 'Web Reference')} | {best_r.get('url', '')} | domain_verified")
            except Exception as w_err:
                log.warning(f"Web search notice: {w_err}")

            # D. Sensitive Fiqh Multi-Madhhab Guidance Instruction
            if sensitivity_info["requires_madhhab_synthesis"]:
                context_parts.append(
                    "CRITICAL SENSITIVE JURISPRUDENCE DIRECTIVE:\n"
                    f"The question involves '{sensitivity_info['topic']}'.\n"
                    "1. Present the scriptural proofs from Quran and authentic Hadiths.\n"
                    "2. Detail the consensus (Ijma') and divergence (Ikhtilaf) across the 4 Sunni schools (Hanafi, Maliki, Shafi'i, Hanbali) neutrally.\n"
                    "3. Do not issue a personal ruling; remind the user that personal cases require human jurist adjudication."
                )

            # E. Strict Anti-Hallucination Scripture Directive
            context_parts.append(
                "STRICT SCRIPTURAL CITATION RULES:\n"
                "1. When citing specific chapter:verse numbers (e.g. [18:49]), you MUST ONLY cite verses explicitly provided in the Context above.\n"
                "2. If discussing stories or spiritual themes not explicitly quoted in the [Q#] excerpts, describe them conceptually by narrative name (e.g. 'In the story of the Companions of the Cave...'); DO NOT invent or misattribute chapter and verse numbers.\n"
                "3. Conclude with: And Allah knows best (Allahu A'lam)."
            )

        elif intent == "VERSE_LOOKUP" and not exact_verses_loaded and (ayah_window or ayahs_context):
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

        # Assemble the full prompt (ensuring User Question is never truncated)
        context_str = ""
        if context_parts:
            context_str = "\n\n---\n\n".join(context_parts)
            if USE_LOCAL_LLM and len(context_str) > 3500:
                context_str = context_str[:3500] + "\n\n[Context streamlined for local inference]"

        system_rules = [
            "CRITICAL SCHOLARLY INSTRUCTIONS:",
            "1. CITE SCRIPTURE ACCURATELY: When quoting verses or Hadiths, cite them using the exact tags provided in context ([Q1], [H1], etc.).",
            "2. ATTRIBUTION INTEGRITY: Never claim a specific quote or saying belongs to Sahih al-Bukhari, Sahih Muslim, or any collection unless that EXACT text appears inside the context excerpts above. If a user asks about a saying not in the context, clarify that it is unverified or not present.",
            "3. RESPECT IKHTILAF: In matters of jurisprudence (Fiqh) where scholars differ across the 4 Sunni schools (Hanafi, Maliki, Shafi'i, Hanbali), explain each view respectfully without sectarian bias.",
            "4. HUMILITY: Conclude your answer with traditional adab: And Allah knows best (Allahu A'lam).",
        ]
        system_rules_str = "\n".join(system_rules)
        full_prompt = f"Context:\n{context_str}\n\n---\n\n{system_rules_str}\n\nQuestion: {query}\n\nScholarly Response:"

        # 3. Generation (Local LLM or Gemini)
        answer = None
        if USE_LOCAL_LLM:
            answer = _generate_scholar_local(full_prompt)

        # Only use cloud Gemini if local LLM is disabled or returned None with client available
        if not answer and client and not USE_LOCAL_LLM:
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
            if USE_LOCAL_LLM:
                return "⚠️ **Local HidayahLM Notice:** Local inference did not produce a response within the timeout. Please check that Ollama is running (`ollama list`) and try again."
            return "⚠️ **Scholar Agent error:** The model returned an empty response. Please try again."

        log.info("Response generated successfully.")

        # 4. Post-generation Citation & Quran Reference Verification
        if context_str:
            answer = verify_grounded_citations(answer, context_str)

        # 5. Prepend Academic Advisory Header for Sensitive Inquiries
        if sensitivity_info["is_sensitive"] and sensitivity_info.get("advisory_notice"):
            answer = sensitivity_info["advisory_notice"] + "\n\n" + answer

        if hadith_ref and not is_direct_lookup:
            hadith_card = format_hadith_card(hadith_ref)
            answer = f"{hadith_card}\n\n### 📖 Scholarly Analysis\n{answer}"

        if grounded_sources:
            answer += "\n\nSources:\n" + "\n".join(f"- {src}" for src in grounded_sources)
        return answer

    except genai.errors.APIError as e:
        if e.code == 429:
            log.warning("[FAILOVER] Gemini 429 Rate Limit hit. Attempting automatic failover to local HidayahLM model...")
            fallback_answer = _generate_scholar_local(full_prompt)
            if fallback_answer:
                if context_str:
                    fallback_answer = verify_grounded_citations(fallback_answer, context_str)
                if sensitivity_info["is_sensitive"] and sensitivity_info.get("advisory_notice"):
                    fallback_answer = sensitivity_info["advisory_notice"] + "\n\n" + fallback_answer
                if hadith_ref and not is_direct_lookup:
                    hadith_card = format_hadith_card(hadith_ref)
                    fallback_answer = f"{hadith_card}\n\n### 📖 Scholarly Analysis\n{fallback_answer}"
                if grounded_sources:
                    fallback_answer += "\n\nSources:\n" + "\n".join(f"- {src}" for src in grounded_sources)
                return fallback_answer
            return "⚠️ **Gemini Free-Tier Rate Limit Reached.** Switched to local HidayahLM. Please ensure Ollama is running (`ollama run hidayah-lm:3b`)."
        return f"⚠️ **API Error:** {str(e.message) if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        log.error(f"Scholar Agent error: {e}")
        return f"⚠️ **Scholar Agent error:** An unexpected error occurred. Please try again."
