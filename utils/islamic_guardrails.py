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
    {
        "topic": "Comparative Jurisprudence & Madhhab Ikhtilaf (Fiqh al-Muqaran)",
        "patterns": [
            r"\b(four (?:sunni )?(?:madhhabs?|madhabs?|schools? of thought|schools? of jurisprudence)|4 (?:sunni )?(?:madhhabs?|schools?))\b",
            r"\b(ikhtilaf|madhhab differences?|raf'? al-?yadayn|raising hands (?:in|during) prayer|qunoot (?:in|during) fajr|tashahhud (?:finger|pointing) differences?)\b",
            r"\b(hanafi.*(shafi|maliki|hanbali)|shafi.*(hanafi|maliki|hanbali)|maliki.*(hanafi|shafi|hanbali)|hanbali.*(hanafi|maliki|shafi))\b",
            r"(مذاهب أربعة|اختلاف الفقهاء|رفع اليدين|قنوت الفجر|فقه مقارن)",
        ],
    },
    {
        "topic": "Financial Transactions, Usury & Commercial Contracts (Riba / Loans / Banking)",
        "patterns": [
            r"\b(riba|usury|interest loan|car loan|vehicle loan|bank loan|mortgage|interest-bearing|is interest permissible|can i take an? interest|buy a (?:car|vehicle|house) on interest)\b",
            r"(ربا|فائدة بنكية|قرض ربوي|قرض سيارة|رهن عقاري|هل يجوز أخذ قرض)",
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
    r"\b(is it permissible for me|can i (?:take|borrow|buy)|take an? (?:interest|car|bank|vehicle|mortgage) loan|buy a (?:car|vehicle|house) on interest)\b",
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

CANONICAL_114_SURAHS = {
    1: "Al-Fatihah", 2: "Al-Baqarah", 3: "Ali 'Imran", 4: "An-Nisa", 5: "Al-Ma'idah",
    6: "Al-An'am", 7: "Al-A'raf", 8: "Al-Anfal", 9: "At-Tawbah", 10: "Yunus",
    11: "Hud", 12: "Yusuf", 13: "Ar-Ra'd", 14: "Ibrahim", 15: "Al-Hijr",
    16: "An-Nahl", 17: "Al-Isra", 18: "Al-Kahf", 19: "Maryam", 20: "Ta-Ha",
    21: "Al-Anbiya", 22: "Al-Hajj", 23: "Al-Mu'minun", 24: "An-Nur", 25: "Al-Furqan",
    26: "Ash-Shu'ara", 27: "An-Naml", 28: "Al-Qasas", 29: "Al-'Ankabut", 30: "Ar-Rum",
    31: "Luqman", 32: "As-Sajdah", 33: "Al-Ahzab", 34: "Saba", 35: "Fatir",
    36: "Ya-Sin", 37: "As-Saffat", 38: "Sad", 39: "Az-Zumar", 40: "Ghafir",
    41: "Fussilat", 42: "Ash-Shura", 43: "Az-Zukhruf", 44: "Ad-Dukhan", 45: "Al-Jathiyah",
    46: "Al-Ahqaf", 47: "Muhammad", 48: "Al-Fath", 49: "Al-Hujurat", 50: "Qaf",
    51: "Adh-Dhariyat", 52: "At-Tur", 53: "An-Najm", 54: "Al-Qamar", 55: "Ar-Rahman",
    56: "Al-Waqi'ah", 57: "Al-Hadid", 58: "Al-Mujadila", 59: "Al-Hashr", 60: "Al-Mumtahanah",
    61: "As-Saff", 62: "Al-Jumu'ah", 63: "Al-Munafiqun", 64: "At-Taghabun", 65: "At-Talaq",
    66: "At-Tahrim", 67: "Al-Mulk", 68: "Al-Qalam", 69: "Al-Haqqah", 70: "Al-Ma'arij",
    71: "Nuh", 72: "Al-Jinn", 73: "Al-Muzzammil", 74: "Al-Muddaththir", 75: "Al-Qiyamah",
    76: "Al-Insan", 77: "Al-Mursalat", 78: "An-Naba", 79: "An-Nazi'at", 80: "'Abasa",
    81: "At-Takwir", 82: "Al-Infitar", 83: "Al-Mutaffifin", 84: "Al-Inshiqaq", 85: "Al-Buruj",
    86: "At-Tariq", 87: "Al-A'la", 88: "Al-Ghashiyah", 89: "Al-Fajr", 90: "Al-Balad",
    91: "Ash-Shams", 92: "Al-Layl", 93: "Ad-Duha", 94: "Ash-Sharh", 95: "At-Tin",
    96: "Al-'Alaq", 97: "Al-Qadr", 98: "Al-Bayyinah", 99: "Az-Zalzalah", 100: "Al-'Adiyat",
    101: "Al-Qari'ah", 102: "At-Takathur", 103: "Al-'Asr", 104: "Al-Humazah", 105: "Al-Fil",
    106: "Quraysh", 107: "Al-Ma'un", 108: "Al-Kawthar", 109: "Al-Kafirun", 110: "An-Nasr",
    111: "Al-Masad", 112: "Al-Ikhlas", 113: "Al-Falaq", 114: "An-Nas"
}

def normalize_surah_name(name: str) -> str:
    """Normalize a surah name by stripping prefix 'al-', 'at-', apostrophes, hyphens, and whitespace."""
    s = name.lower().strip()
    s = re.sub(r"^(?:al|at|an|ar|as|ash|az|ad|adh)[\s'-]+", "", s)
    s = re.sub(r"[\s'-]+", "", s)
    return s

CANONICAL_SURAH_NAME_SET = {
    normalize_surah_name(name) for name in CANONICAL_114_SURAHS.values()
}
CANONICAL_SURAH_NAME_SET.update({
    "fatiha", "fateha", "baqara", "baqarah", "imran", "aleimran", "aliimran",
    "isra", "israa", "kahf", "qamar", "qiamah", "qiyamah", "takwir", "inshiqaq"
})

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

    # Step 1: Detect matching sensitive domains (supporting compound/multi-topic inquiries)
    matched_topics = []
    for domain in SENSITIVE_FATWA_DOMAINS:
        for pattern in domain["patterns"]:
            if re.search(pattern, query_lower, re.IGNORECASE):
                if domain["topic"] not in matched_topics:
                    matched_topics.append(domain["topic"])
                break

    if not matched_topics:
        return default_res

    matched_topic = matched_topics[0]

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
        notices = [FATWA_GUARD_TEMPLATE.format(topic=t) for t in matched_topics]
        advisory_notice = "\n\n---\n\n".join(notices)
        return {
            "is_sensitive": True,
            "is_personal_verdict": True,
            "topic": " & ".join(matched_topics),
            "topics": matched_topics,
            "advisory_notice": advisory_notice,
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

    # Pre-Sanitization 1: Cross-Wired Tag Stripper (e.g. [H#] tagged to a Surah/Ayah)
    llm_response = re.sub(r"(?m)^\s*\[H\d+\]\s*(?:Surah|Ayah|Verse)[^\r\n]*\r?\n?", "", llm_response)

    # Pre-Sanitization 2: Canonical 114 Surah Whitelist Audit (rejection of fabricated names like 'Surah Al-Qiyaq')
    surah_mentions = list(re.finditer(r"\bSurah\s+([A-Za-z'-]+)", llm_response, re.IGNORECASE))
    for sm in surah_mentions:
        raw_name = sm.group(1).strip()
        norm_name = normalize_surah_name(raw_name)
        if norm_name not in CANONICAL_SURAH_NAME_SET and len(norm_name) >= 3:
            log.warning(f"Sanitizing non-canonical Surah name: '{raw_name}'")
            pattern = rf"(?:\[[A-Za-z0-9]+\]\s*)?Surah\s+{re.escape(raw_name)}[^\n\.]*[\n\.]?"
            llm_response = re.sub(pattern, "", llm_response)

    audit_notes = []

    # 1. Check bracket markers ([Q#], [H#], [T#], [W#], [C#], [Page #])
    if context_text:
        markers = set(re.findall(r"\[(Q\d+|H\d+|T\d+|W\d+|C\d+|Page\s*\d+|Excerpt\s*\d+)\]", llm_response, re.IGNORECASE))
        missing_markers = []
        for marker in markers:
            pattern = re.escape(marker)
            if not re.search(r"\[" + pattern + r"\]", context_text, re.IGNORECASE):
                missing_markers.append(f"[{marker}]")

        if missing_markers:
            log.warning(f"Detected ungrounded citation markers in response: {missing_markers}")
            audit_notes.append(
                f"The citation markers **{', '.join(missing_markers)}** were not in the primary retrieved context. "
                "Please cross-verify with primary classical sources."
            )

    # 2. Check Quranic Surah:Ayah numerical validity and canonical text alignment
    verse_refs = re.findall(r"(?:(?:Surah|Quran)\s*)?\[?(\b\d{1,3}):(\d{1,3})\b\]?", llm_response)
    invalid_refs = []
    
    # Try importing LanceDB canonical ayah fetcher
    try:
        from rag.lancedb_store import get_canonical_ayah
    except Exception:
        get_canonical_ayah = None

    for surah_str, ayah_str in verse_refs:
        surah_num = int(surah_str)
        ayah_num = int(ayah_str)
        if 1 <= surah_num <= 114:
            max_ayahs = QURAN_SURAH_MAX_AYAHS.get(surah_num, 0)
            if ayah_num < 1 or ayah_num > max_ayahs:
                invalid_refs.append(f"{surah_num}:{ayah_num} (Surah {surah_num} has max {max_ayahs} ayahs)")
            elif get_canonical_ayah:
                # Deterministic check for famous parametric cross-wiring (e.g. 18:49 vs 54:49)
                try:
                    if surah_num == 18 and ayah_num == 49:
                        lower_resp = llm_response.lower()
                        # Only flag if 18:49 is falsely attributed to Qadar WITHOUT 54:49 being present in the response
                        has_54_49 = "54:49" in llm_response or "al-qamar" in lower_resp
                        if not has_54_49 and any(kw in lower_resp for kw in ["decree", "predestination", "qadar", "created all things"]):
                            note = (
                                "The quote regarding divine decree (*Qadar*) is authentically from **Surah Al-Qamar (54:49)** (*'Indeed, all things We created with predestination'*). "
                                "Surah Al-Kahf (18:49) specifically addresses the Book of Deeds on Judgment Day."
                            )
                            if note not in audit_notes:
                                audit_notes.append(note)
                except Exception as audit_err:
                    log.warning(f"Ayah text verification notice: {audit_err}")
        elif surah_num > 114:
            invalid_refs.append(f"{surah_num}:{ayah_num} (Quran has 114 Surahs)")

    if invalid_refs:
        log.warning(f"Detected invalid Quranic verse citations: {invalid_refs}")
        inv_note = (
            f"Detected uncanonical Quranic verse reference: **{', '.join(invalid_refs)}**. "
            "Please cross-verify with the canonical Uthmani Mushaf."
        )
        if inv_note not in audit_notes:
            audit_notes.append(inv_note)

    # 3. Detect and sanitize ungrounded verse citations (citations introduced by LLM not in retrieved context)
    if context_text and verse_refs:
        ungrounded = []
        for surah_str, ayah_str in verse_refs:
            ref_str = f"{surah_str}:{ayah_str}"
            if ref_str not in context_text and int(surah_str) <= 114:
                ungrounded.append(ref_str)
        if ungrounded:
            log.warning(f"Detected ungrounded verse citations not present in context: {ungrounded}")
            # Sanitize hallucinated parentheticals (e.g. '(Surah Al-Baqara 2:35)') from output
            for u_ref in ungrounded:
                u_s, u_a = u_ref.split(":")
                llm_response = re.sub(rf"\s*\([A-Za-z\s'-]*{u_s}:{u_a}\)", "", llm_response)
            clean_ungrounded = [u for u in ungrounded if u in llm_response]
            if clean_ungrounded:
                audit_notes.append(
                    f"Verses ({', '.join(clean_ungrounded)}) were cited without primary retrieved context. "
                    "Cross-verification with classical sources is recommended."
                )



    if audit_notes:
        unique_notes = list(dict.fromkeys(audit_notes))
        note_str = "\n\n> 🔍 **Scholarly Citation & Verification Note (Citation Audit Note):** " + " ".join(unique_notes)
        return llm_response + note_str

    return llm_response
