"""
Hidayah AI — Comprehensive Islamic Theological Guardrails & Citation Verification
Implements multi-layer semantic, conceptual, and linguistic protection to prevent
theological hallucinations, guard against unauthorized Fatwas, and audit citations.
"""

import re
from utils.logger import get_logger

log = get_logger("guardrails")

# -----------------------------------------------------------------------------
# Comprehensive Domain Ontologies & Conceptual Regex Patterns
# Covers English, Arabic, and Urdu phrasing (both explicit terms and implicit idioms)
# -----------------------------------------------------------------------------
SENSITIVE_FATWA_DOMAINS = [
    {
        "topic": "Marital Dissolution & Family Law (Talaq / Khula / Separation)",
        "patterns": [
            # Explicit terms
            r"\b(talaq|divorce|khula|khul'|iddah|three talaqs|talaq-e-bain|talaq-e-mughallaza|halala|mut'ah|nikah cancellation)\b",
            r"(طلاق|خلع|عدة|فسخ النكاح|ظهار|لعان|ايلاء|طلاق بائن|طلاق مغلظ)",
            # Implicit / Kinetic expressions (Kinayat al-Talaq)
            r"\b(we are done|no longer (my|his|her) wife|leave (my|her) husband|separated for \d+|kicked me out|cut ties with (husband|wife))\b",
            r"\b(told me (it'?s over|we are finished|get out|you are free))\b",
            r"\b(status of (my|our) marriage|are we (still|considered) married|did (my|our) marriage end|is (my|our) (divorce|separation) valid)\b",
            r"\b(said (three|3) times|texted (three|3) times|via text message .* divorce)\b",
            r"\b(release (you|her|him) from .* marriage contract)\b",
        ],
    },
    {
        "topic": "Estate & Inheritance Distribution (Mirath / Wasiyyah)",
        "patterns": [
            # Explicit terms
            r"\b(inheritance|mirath|estate distribution|wasiyyah|shares of inheritance|estate division|heirs|succession)\b",
            r"(ورثة|ميراث|فرائض|وصية|تركة|قسمة التركة|أنصبة الورثة)",
            # Implicit / Deceased asset questions
            r"\b((father|mother|parent|husband|wife|sibling|grandfather|relative|someone|a person|a man|a woman) (passed away|died|leaves? (behind|estate|money|property|wealth)))\b",
            r"\b(when (someone|a person|a man|a woman|a parent|father|mother|husband) dies)\b",
            r"\b(split|divid(e|ed|ing)|distribut(e|ed|ing)|shares?) (the|his|her|their)?\s*(money|property|estate|house|wealth|assets)?\s*between\b",
            r"\b(how (much|many shares) (does|do) (the|my|each)?\s*(son|daughter|brother|sister|wife|mother|husband|heir) get)\b",
            r"\b(who inherits (from|when)|legal islamic share for (his|her|my))\b",
        ],
    },
    {
        "topic": "Takfir, Creed & Excommunication Verdicts",
        "patterns": [
            # Explicit terms
            r"\b(takfir|declare .* (kafir|apostate|non-believer)|murtad|riddah|excommunicate|apostasy ruling)\b",
            r"(تكفير|مرتد|ردة|خروج عن الملة|هل فلان كافر)",
            # Implicit questions on Muslim status
            r"\b(is (he|she|someone|my neighbor|my friend|a person who .*) (still|considered) a muslim)\b",
            r"\b(outside the fold of islam|out of islam|does .* make (one|someone|him|her) a kafir|nullifies (one's|his|her) islam)\b",
            r"\b(are\s+.*(ahmadis?|qadianis?|shias?|sunnis?|ibadis?|bahais?|alawis?)\s+.*(muslims?|non-?believers?|kafirs?|disbelievers?|out of islam))\b",
            r"\b(is (a|an)?\s*(ahmadi|qadiani|shia|sunni|ibadi|bahai)\s*(a\s*)?(muslim|kafir|non-?believer))\b",
        ],
    },
    {
        "topic": "Criminal Jurisprudence, Penalties & Retribution (Hudud / Qisas)",
        "patterns": [
            # Explicit terms
            r"\b(hudud|qisas|blood money|diyah|stoning penalty|amputation penalty|capital punishment in islam|execution penalty)\b",
            r"(حدود|قصاص|دية|رجم|قطع يد|حد الردة|حد الزنا|حد السرقة)",
            r"\b(what is the (punishment|penalty) for (adultery|zina|blasphemy|apostasy|theft) in (my|this) case)\b",
        ],
    },
]

FATWA_GUARD_TEMPLATE = """⚠️ **Scholarly Guidance Notice on {topic}:**

This inquiry touches upon a sensitive domain of personal Islamic jurisprudence (*Fiqh* / *Personal Status*). 

**Theological Principles:**
1. **No Automated Fatwas:** Automated AI assistants cannot evaluate personal intent, verify judicial conditions, or issue legally binding rulings (*Fatwas*).
2. **Contextual Evaluation Required:** In Islamic jurisprudence (*Usul al-Fiqh*), personal status rulings require formal verification of testimonies, contracts, and state of mind by an accredited human jurist (*Mufti* / *Qadi*).

👉 **Recommendation:** Please consult a recognized scholar, your local Islamic Judicial Council, or an accredited Dar al-Ifta (such as *Al-Azhar*, *Dar al-Ifta al-Misriyyah*, or *AMJA*) for a formal, legally grounded evaluation.
"""

ACADEMIC_FIQH_HEADER = """⚖️ **Scholarly Jurisprudence Overview ({topic}):**
*The following is an academic summary of classical Quranic principles, authentic Hadiths, and scholarly consensus/differences (Ikhtilaf) across the recognized Sunni Madhhabs. AI assistants cannot issue legally binding personal rulings (Fatwas). For specific personal legal application, consult a qualified Mufti or accredited judicial council.*
"""

# Indicators that query is a personal, case-specific dispute/ruling rather than theoretical study
PERSONAL_CASE_PATTERNS = [
    # First-person relationships and situational indicators
    r"\b(my|our|we|me|i am|i have|my wife|my husband|my father|my mother|my spouse|my son|my daughter|my sister|my brother|my neighbor|my friend|said to me|told me|texted me|kicked me out|cut ties with)\b",
    # Direct personal outcome queries
    r"\b(are we (still|considered) married|did (my|our) marriage end|is (my|our) (divorce|marriage|separation) valid|am i divorced|can i marry|calculate (my|our) share|how much do (i|we|my) get|in (my|this) case)\b",
    # Specific amounts and asset allocations
    r"\b(\$\s*\d+|\d+\s*dollars?|\d+\s*usd|\d+\s*rupees?|\d+\s*pkr|\d+\s*pounds?|\d+\s*eur|leaving \d+|left behind \d+)\b",
    # Specific individuals/family splitting
    r"\b(divided between (their|our|the)?\s*(mother|wife|son|daughter|brother|sister))\b",
    r"\b(divid(e|ing)|split|distribut(e|ing)) (the )?(inheritance|mirath|estate|money|property|wealth|shares?)\b",
    r"\b(for|between|among) \d+\s*(sons?|daughters?|wives|wife|brothers?|sisters?|heirs?)\b",
    r"\b(three talaqs in one sitting)\b",
    r"\b(release (you|her|him) from (our|the) marriage contract)\b",
    # Implicit kinetic divorce expressions
    r"\b(we are done|no longer (my|his|her) wife|leave (my|her) husband|separated for \d+)\b",
    r"\b(status of (my|our) marriage)\b",
]

# Canonical 114 Surahs max Ayah counts for scripture hallucination audit
QURAN_SURAH_MAX_AYAHS = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6,
}


def classify_fatwa_sensitivity(query: str, in_pdf_context: bool = False) -> dict:
    """
    Two-Tier Sensitivity Classifier:
    Differentiates between personal binding legal requests (Istifta)
    and academic/theological inquiries (Ta'leem / Fiqh al-Muqaran).

    Returns:
        dict: {
            "is_sensitive": bool,
            "is_personal_verdict": bool,
            "topic": str | None,
            "advisory_notice": str | None,
            "requires_madhhab_synthesis": bool,
        }
    """
    default_res = {
        "is_sensitive": False,
        "is_personal_verdict": False,
        "topic": None,
        "advisory_notice": None,
        "requires_madhhab_synthesis": False,
    }
    if not query:
        return default_res

    query_lower = query.strip().lower()

    # Step 1: Detect matching sensitive domain
    matched_topic = None
    for domain in SENSITIVE_FATWA_DOMAINS:
        for pattern in domain["patterns"]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                matched_topic = domain["topic"]
                break
        if matched_topic:
            break

    if not matched_topic:
        return default_res

    # Step 2: In PDF Analysis context, questions querying the document are academic
    if in_pdf_context and any(kw in query_lower for kw in ["pdf", "document", "author", "paper", "book", "chapter"]):
        return {
            "is_sensitive": True,
            "is_personal_verdict": False,
            "topic": matched_topic,
            "advisory_notice": ACADEMIC_FIQH_HEADER.format(topic=matched_topic),
            "requires_madhhab_synthesis": True,
        }

    # Step 3: Takfir & Excommunication is strictly intercepted per Amman Message consensus
    if "Takfir" in matched_topic:
        return {
            "is_sensitive": True,
            "is_personal_verdict": True,
            "topic": matched_topic,
            "advisory_notice": FATWA_GUARD_TEMPLATE.format(topic=matched_topic),
            "requires_madhhab_synthesis": False,
        }

    # Step 4: Check personal case indicators
    is_personal = False
    for pat in PERSONAL_CASE_PATTERNS:
        if re.search(pat, query_lower, re.IGNORECASE):
            is_personal = True
            break

    # If asking case-specific division or divorce status without academic markers
    if is_personal:
        return {
            "is_sensitive": True,
            "is_personal_verdict": True,
            "topic": matched_topic,
            "advisory_notice": FATWA_GUARD_TEMPLATE.format(topic=matched_topic),
            "requires_madhhab_synthesis": False,
        }

    # Step 5: Academic & Scriptural Jurisprudence Inquiry (Ta'leem)
    return {
        "is_sensitive": True,
        "is_personal_verdict": False,
        "topic": matched_topic,
        "advisory_notice": ACADEMIC_FIQH_HEADER.format(topic=matched_topic),
        "requires_madhhab_synthesis": True,
    }


def check_fatwa_sensitivity(query: str) -> str | None:
    """
    Evaluate user query for sensitive Islamic legal topics.
    Returns FATWA_GUARD_TEMPLATE if a personal ruling / binding verdict is sought.
    Maintains full backward compatibility for compliance test suites.
    """
    if not query:
        return None

    info = classify_fatwa_sensitivity(query)
    if info["is_personal_verdict"]:
        log.info(f"Triggered Personal Fatwa Guardrail for: {info['topic']}")
        return info["advisory_notice"]

    return None


def verify_grounded_citations(llm_response: str, context_text: str) -> str:
    """
    Post-generation audit:
    1. Verifies that citation markers ([H#], [T#], [Page #], [Excerpt #])
       actually exist in the retrieved context.
    2. Validates Quranic verse references against canonical boundaries (Surah 1-114 and Ayah counts).

    Appends an audit note if unverified citations or invalid verse numbers are detected.
    """
    if not llm_response:
        return llm_response

    audit_notes = []

    # 1. Check bracket markers
    if context_text:
        markers = set(re.findall(r"\[(H\d+|T\d+|C\d+|Page\s*\d+|Excerpt\s*\d+)\]", llm_response, re.IGNORECASE))
        missing_markers = []
        for marker in markers:
            pattern = re.escape(marker)
            if not re.search(r"\[" + pattern + r"\]", context_text, re.IGNORECASE):
                missing_markers.append(f"[{marker}]")

        if missing_markers:
            log.warning(f"Detected ungrounded citation markers in response: {missing_markers}")
            audit_notes.append(
                f"The citation markers **{', '.join(missing_markers)}** could not be directly "
                "cross-referenced with the retrieved source excerpts. Please verify against primary classical sources."
            )

    # 2. Check Quranic Surah:Ayah numerical validity
    # Matches patterns like 2:255, 4:11, [2:183], Surah 2:255
    verse_refs = re.findall(r"(?:Surah\s*)?\[?(\b\d{1,3}):(\d{1,3})\b\]?", llm_response)
    invalid_refs = []
    for surah_str, ayah_str in verse_refs:
        surah_num = int(surah_str)
        ayah_num = int(ayah_str)
        if 1 <= surah_num <= 114:
            max_ayahs = QURAN_SURAH_MAX_AYAHS.get(surah_num, 0)
            if ayah_num < 1 or ayah_num > max_ayahs:
                invalid_refs.append(f"{surah_num}:{ayah_num} (Surah {surah_num} has max {max_ayahs} ayahs)")
        elif surah_num > 114:
            invalid_refs.append(f"{surah_num}:{ayah_num} (Quran has 114 Surahs)")

    if invalid_refs:
        log.warning(f"Detected invalid Quranic verse citations: {invalid_refs}")
        audit_notes.append(
            f"Detected uncanonical Quranic verse reference: **{', '.join(invalid_refs)}**. "
            "Please cross-verify with the canonical Uthmani Mushaf."
        )

    if audit_notes:
        note_str = "\n\n> 🔍 **Citation Audit Note:** " + " ".join(audit_notes)
        return llm_response + note_str

    return llm_response
