"""
Hidayah AI — Islamic Theological Guardrails & Citation Verification
Ensures grounding, prevents theological hallucinations, and enforces the "AI is not a Mufti" boundary.
"""

import re
from utils.logger import get_logger

log = get_logger("guardrails")

# Sensitive Islamic Jurisprudence (Fiqh) Topics requiring qualified human scholars (Dar al-Ifta)
SENSITIVE_FATWA_PATTERNS = [
    # Marital disputes & dissolution
    (
        r"\b(talaq|divorce|khula|khul'|iddah|three talaqs|talaq-e-bain|talaq-e-mugallaza|طلاق|خلع|عدة)\b",
        "Marital Dissolution & Family Law (Talaq/Khula)",
    ),
    # Inheritance & Estate
    (
        r"\b(inheritance|mirath|estate distribution|wasiyyah|shares of inheritance|ورثة|ميراث|فرائض)\b",
        "Estate & Inheritance Distribution (Mirath)",
    ),
    # Excommunication & Creed Disputes
    (
        r"\b(takfir|is .* a kafir|declare .* apostate|murtad|riddah|تكفير|مرتد|ردة)\b",
        "Takfir & Apostasy Verdicts",
    ),
    # Capital / Criminal Rulings
    (
        r"\b(hudud|qisas|blood money|diyah|stoning penalty|حدود|قصاص|دية)\b",
        "Criminal Jurisprudence & Penalties (Hudud/Qisas)",
    ),
]

FATWA_GUARD_TEMPLATE = """⚠️ **Scholarly Guidance Notice on {topic}:**

This question touches upon a sensitive area of personal Islamic jurisprudence (*Fiqh* / *Personal Status*). 

**Important Principles:**
1. Automated AI tools cannot assess individual life circumstances, verify contractual conditions, or issue legally binding religious rulings (*Fatwas*).
2. Rulings on matters such as divorce, inheritance, and personal legal disputes require direct consultation with a qualified jurist who can review all testimonies and documentation.

👉 **Recommendation:** Please consult a recognized Islamic scholar, your local Islamic Council, or an accredited Dar al-Ifta (such as *Al-Azhar*, *Dar al-Ifta al-Misriyyah*, or *AMJA*) for guidance on this matter.
"""


def check_fatwa_sensitivity(query: str) -> str | None:
    """
    Check if user query asks for a personal binding fatwa in high-risk areas.
    
    Returns:
        Formatted disclaimer string if matched, or None if query is safe for research.
    """
    if not query:
        return None

    query_lower = query.lower()
    for pattern, topic_name in SENSITIVE_FATWA_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            log.info(f"Triggered Fatwa Guardrail for topic: {topic_name}")
            return FATWA_GUARD_TEMPLATE.format(topic=topic_name)

    return None


def verify_grounded_citations(llm_response: str, context_text: str) -> str:
    """
    Post-generation audit: Verifies that citation markers ([H#], [T#], [Chunk #])
    present in the LLM response actually exist in the retrieved context.

    Appends an audit note if unverified citations are detected.
    """
    if not llm_response or not context_text:
        return llm_response

    # Extract all citation markers like [H1], [T2], [Chunk 3]
    markers = set(re.findall(r"\[(H\d+|T\d+|C\d+|Chunk\s*\d+)\]", llm_response, re.IGNORECASE))
    if not markers:
        return llm_response

    missing_markers = []
    for marker in markers:
        # Check if the marker appeared in the context provided to the LLM
        pattern = re.escape(marker)
        if not re.search(r"\[" + pattern + r"\]", context_text, re.IGNORECASE):
            missing_markers.append(f"[{marker}]")

    if missing_markers:
        log.warning(f"Detected ungrounded citation markers in response: {missing_markers}")
        audit_note = (
            f"\n\n> 🔍 **Citation Audit Note:** The citation markers **{', '.join(missing_markers)}** "
            "could not be directly cross-referenced with the retrieved source snippets. "
            "Please verify this information against primary classical sources."
        )
        return llm_response + audit_note

    return llm_response
