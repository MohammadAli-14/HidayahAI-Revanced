"""
Hidayah AI — Intent Router Agent
Uses Gemini 2.5 Flash-Lite for fast intent classification of user queries.
Categories: VERSE_LOOKUP, SCHOLARLY_RESEARCH, SENSITIVE_FIQH, HADITH_AUTHENTICATION, PDF_ANALYSIS
"""

from google import genai
import re
from utils.config import MODEL_ROUTER, GEMINI_API_KEY, USE_LOCAL_LLM, get_gemini_client
from utils.logger import get_logger

log = get_logger("router")

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for an Islamic Quranic research application called Hidayah AI.

Classify the user's query into EXACTLY ONE of these categories. Return ONLY the category name, nothing else.

Categories:
- VERSE_LOOKUP: The user wants to look up, read, or hear a specific verse, surah, or juz. Examples: "Show me verse 255 of Al-Baqarah", "Read Surah Al-Fatiha", "What does ayah 183 say?"
- SENSITIVE_FIQH: The user asks about sensitive jurisprudence, personal status, family law, divorce (talaq), inheritance (mirath), legal penalties (hudud), or controversial fiqh matters. Examples: "What are the inheritance rules in Surah An-Nisa?", "Explain Talaq al-Sunnah vs Talaq al-Bid'ah", "What do the 4 Madhhabs say about Khula?"
- HADITH_AUTHENTICATION: The user wants to check the authenticity, grade (Sahih, Hasan, Da'if), narrator chain (Isnad), or specific reference of a Hadith. Examples: "Is the hadith about intentions authentic?", "Where is the narration about fasting in Sahih Muslim?", "What is the grade of this hadith?"
- SCHOLARLY_RESEARCH: The user wants general tafsir, historical context, virtues, spirituality, ethics, or general Islamic knowledge. Examples: "Explain the purpose of fasting", "What was the context of Battle of Badr?", "What are the virtues of Laylatul Qadr?"
- PDF_ANALYSIS: The user wants to analyze, search, or ask questions about an uploaded PDF document. If a PDF is present, assume general questions should be answered using the PDF. Examples: "What does the PDF say about...", "Summarize the document", "Find references in the uploaded paper".

If unsure, default to SCHOLARLY_RESEARCH."""


def classify_intent_heuristic(query: str, active_pdf_name: str | None = None) -> str:
    """
    High-precision offline rule-based heuristic classifier (0ms, 0 tokens, no 429 quota calls).
    Returns one of: PDF_ANALYSIS, SENSITIVE_FIQH, HADITH_AUTHENTICATION, VERSE_LOOKUP, SCHOLARLY_RESEARCH.
    """
    q = query.lower().strip()

    # 1. PDF Analysis check
    if active_pdf_name:
        pdf_indicators = [
            "pdf", "document", "uploaded", "paper", "booklet", "file",
            "author", "summary", "summarize", "in this text", "this article",
            "table of contents", "chapter in document"
        ]
        if any(ind in q for ind in pdf_indicators):
            return "PDF_ANALYSIS"
        # If short question and PDF is active
        if len(q.split()) <= 6 and not any(k in q for k in ["ayah", "verse", "surah", "hadith", "talaq"]):
            return "PDF_ANALYSIS"

    # 2. Sensitive Fiqh & Personal Status / Marital / Inheritance
    fiqh_patterns = [
        r"\b(?:divorce|talaq|talaaq|khula|khul'|separation|nikah|marriage contract|iddah|idda)\b",
        r"\b(?:inheritance|mirath|wiratha|estate division|heir|shares of inheritance|wasiyyah|bequest)\b",
        r"\b(?:hudud|qisas|stoning|amputation|corporal punishment|apostasy|blasphemy)\b",
        r"\b(?:is my (?:divorce|marriage|prayer|fast|wudu) valid|is it valid|is this valid)\b",
        r"\b(?:fatwa|legal ruling|is it permissible|is it forbidden|is it haram|is it halal)\b",
        r"\b(?:four (?:sunni )?(?:schools?(?: of thought)?|madhhabs?|madhabs?)|4 (?:sunni )?(?:schools?|madhhabs?)|hanafi|shafi|shafii|maliki|hanbali|ikhtilaf|raf'? al-?yadayn|raising hands in prayer|qunoot|tashahhud differences|fiqh al-muqaran|comparative (?:fiqh|jurisprudence))\b",
        r"\b(?:custody of children|mahr|dowry|alimony|nafaqah)\b",
    ]
    for pattern in fiqh_patterns:
        if re.search(pattern, q):
            return "SENSITIVE_FIQH"

    # 3. Hadith Authentication & Sanad / Takhrij
    hadith_auth_patterns = [
        r"\b(?:is the hadith|is this hadith|authenticity of hadith|authenticity of the narration|authentic hadith|is the statement|is this narration|is it authentic|is this authentic)\b",
        r"\b(?:sahih|hasan|da'if|daif|weak hadith|fabricated hadith|mawdu|maudu|fabrication)\b",
        r"\b(?:isnad|sanad|chain of narrators?|takhrij|narrator chain|who narrated)\b",
        r"\b(?:grade of (?:this |the )?hadith|hadith grade|hadith authentication)\b",
        r"\b(?:bukhari|muslim|tirmidhi|abu dawud|ibn majah|nasai|musnad ahmad|muwatta)\s*(?:#|\d+|hadith|narration)\b",
        r"\b(?:seek knowledge even (?:if |unto )?(?:in |to )?china|even unto china|china)\b",
    ]
    for pattern in hadith_auth_patterns:
        if re.search(pattern, q):
            return "HADITH_AUTHENTICATION"

    # 4. Verse Lookup
    # If the inquiry asks for thematic, explanatory, or historical analysis, prioritize SCHOLARLY_RESEARCH
    research_indicators = [
        "theme", "spiritual", "meaning of", "explain", "explanation", "tafsir", "tafseer",
        "context of revelation", "asbab al-nuzul", "lessons from", "story of", "why was",
        "historical", "summary of surah", "purpose of", "virtues of", "compare", "comparison",
        "contrast", "difference between", "relation between"
    ]
    has_research_indicator = any(ind in q for ind in research_indicators)

    verse_patterns = [
        r"\b\d{1,3}:\d{1,3}\b",
        r"\b(?:ayah|verse|ayat)\s+\d+\b",
        r"\b(?:show|read|display|recite|listen to|play|recitation of)\s+(?:me\s+)?(?:the\s+)?(?:surah|verse|ayah|chapter)\b",
        r"\b(?:ayatul kursi|surah fatiha|surah al-fatiha|surah yasin|surah al-mulk)\b",
    ]
    if not has_research_indicator:
        for pattern in verse_patterns:
            if re.search(pattern, q):
                return "VERSE_LOOKUP"

    # 5. Default: Scholarly Research
    return "SCHOLARLY_RESEARCH"


def classify_intent(query: str, active_pdf_name: str | None = None) -> str:
    """
    Classify user intent into one of:
    VERSE_LOOKUP, SCHOLARLY_RESEARCH, SENSITIVE_FIQH, HADITH_AUTHENTICATION, PDF_ANALYSIS.

    - When USE_LOCAL_LLM is enabled, runs the offline heuristic classifier instantly (0ms, 0 tokens, no 429 quota exhaustion).
    - When Gemini is active, attempts cloud classification with automatic fallback to heuristic on error/rate limit.
    """
    # 1. Local LLM / Offline Mode: Instant heuristic routing
    if USE_LOCAL_LLM:
        intent = classify_intent_heuristic(query, active_pdf_name)
        log.info(f"[OFFLINE ROUTER] Classified intent as: {intent}")
        return intent

    # 2. Cloud Mode with Gemini
    client = get_gemini_client()
    if not client:
        return classify_intent_heuristic(query, active_pdf_name)

    try:
        system_prompt = ROUTER_SYSTEM_PROMPT
        if active_pdf_name:
            system_prompt += f"\n\nCRITICAL CONTEXT: A PDF named '{active_pdf_name}' is currently uploaded. If the user asks a general question, they PROBABLY want to know the PDF's answer. Strongly bias towards PDF_ANALYSIS unless they explicitly ask for a verse, hadith takhrij, or a wide-ranging web search. If the question is covered by the concept of the document, choose PDF_ANALYSIS."

        response = client.models.generate_content(
            model=MODEL_ROUTER,
            contents=query,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                max_output_tokens=50,
            ),
        )

        if not response.text:
            log.warning("Empty response from model. Falling back to heuristic classifier.")
            return classify_intent_heuristic(query, active_pdf_name)

        result = response.text.strip().upper()

        # Validate the response is one of the expected categories
        valid_categories = {
            "VERSE_LOOKUP",
            "SCHOLARLY_RESEARCH",
            "SENSITIVE_FIQH",
            "HADITH_AUTHENTICATION",
            "PDF_ANALYSIS",
        }
        if result in valid_categories:
            log.info(f"Classified intent as: {result}")
            return result

        # Fuzzy match
        for cat in valid_categories:
            if cat in result or (len(result) >= 3 and result in cat):
                log.info(f"Fuzzy matched intent as: {cat} (from: {result})")
                return cat

        return classify_intent_heuristic(query, active_pdf_name)

    except Exception as e:
        log.warning(f"Gemini router notice ({e}). Falling back to offline heuristic router.")
        return classify_intent_heuristic(query, active_pdf_name)


