"""
Tests for Scripture Disambiguation and Offline Canonical Exegesis Store
Ensures 100% grounded exegesis for comparative Quranic inquiries,
verifying that 18:49 (Book of Deeds) and 54:49 (Divine Decree/Qadar)
are retrieved with zero grouped-ayah bleed, zero network latency,
and zero fabricated citations.
"""

import pytest
from utils.tafsir_store import has_canonical_tafsir, get_canonical_tafsir_for_ayah
from agents.scholar import prepare_scholar_context
from utils.islamic_guardrails import verify_grounded_citations


def test_canonical_tafsir_store_retrieval():
    """Verify 18:49 and 54:49 exist in the offline store with pristine isolated text."""
    assert has_canonical_tafsir(18, 49, "en") is True
    assert has_canonical_tafsir(54, 49, "en") is True

    tafsir_18 = get_canonical_tafsir_for_ayah(18, 49, "en")
    assert len(tafsir_18) >= 1
    t18_text = " ".join([t["excerpt"] for t in tafsir_18]).lower()
    # 18:49 MUST be about the Book of Deeds
    assert "book of deeds" in t18_text or "kitab" in t18_text
    # 18:49 MUST NOT contain the grouped 18:47 mountain bleed
    assert "mountains to pass away" not in t18_text

    tafsir_54 = get_canonical_tafsir_for_ayah(54, 49, "en")
    assert len(tafsir_54) >= 1
    t54_text = " ".join([t["excerpt"] for t in tafsir_54]).lower()
    # 54:49 MUST be about Qadar / predestination
    assert "qadar" in t54_text or "predestination" in t54_text or "decree" in t54_text
    # 54:49 MUST NOT contain the grouped 54:47-48 criminal dragging bleed
    assert "dragged into the fire on their faces" not in t54_text


def test_prepare_scholar_context_comparative_disambiguation():
    """Verify context assembly correctly provisions isolated Tafsir and suppresses spurious Hadith."""
    query = "What is the difference between Surah al-Kahf 18:49 and Surah al-Qamar 54:49?"
    bundle = prepare_scholar_context(
        query=query,
        intent="SCHOLARLY_RESEARCH",
        use_local_llm=True,
    )

    prompt = bundle.full_prompt
    context = bundle.context_str

    # Both explicit coordinates must be isolated in context
    assert "18:49" in context
    assert "54:49" in context

    # Exegesis must be anchored
    assert "Classical Tafseer Exegesis" in context
    assert "Book of Deeds" in context
    assert "Qadar" in context or "predestination" in context.lower()

    # Spurious Hadith tags must be suppressed for pure exegesis inquiries
    assert not any("[H" in s for s in bundle.grounded_sources)

    # Prompt length must be tightly bounded for CPU TTFT < 20s
    assert len(prompt) <= 5200


def test_guardrail_sanitizes_hallucinated_citations():
    """Verify that ungrounded verse parentheticals not in context are sanitized."""
    context_text = "Explicitly Cited Verses: [Q-18:49] and [Q-54:49]. Tafsir explains deeds vs decree."
    
    # Simulate a response where LLM mistakenly references Surah Al-Baqara 2:35
    hallucinated_resp = (
        "Surah Al-Kahf 18:49 discusses the Book of Deeds. "
        "Surah Al-Qamar 54:49 discusses divine decree (Surah Al-Baqara 2:35). "
        "And Allah knows best."
    )

    verified = verify_grounded_citations(hallucinated_resp, context_text)

    # The ungrounded reference (Surah Al-Baqara 2:35) should be sanitized from the primary text
    assert "(Surah Al-Baqara 2:35)" not in verified
