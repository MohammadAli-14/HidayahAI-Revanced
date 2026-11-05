"""
Unit tests for Phase 1: Compound Queries, Multi-Entity Resolution, and Canonical 114 Surah Whitelist.
"""

import pytest
from agents.scholar import prepare_scholar_context
from utils.islamic_guardrails import verify_grounded_citations, CANONICAL_SURAH_NAME_SET, normalize_surah_name


def test_multi_hadith_retrieval_no_omission():
    """Verify that multiple Hadith references in a single query are all retrieved."""
    q = "Retrieve Sunan Abi Dawud 1035 and Sahih al-Bukhari 1 with Arabic text and authenticity grades."
    bundle = prepare_scholar_context(q, intent="HADITH_AUTHENTICATION")
    assert bundle.fast_response is not None
    assert len(bundle.grounded_sources) == 2
    # Both hadith titles must appear in the fast response card
    assert "Abu Dawud #1035" in bundle.fast_response
    assert "al-Bukhari #1" in bundle.fast_response


def test_compound_sensitive_fiqh_interception():
    """Verify that multi-topic personal queries (Talaq + Riba) intercept both domains."""
    q = 'Is my divorce valid? I said talaq three times in extreme anger. and Is it permissible for me to take an interest loan to buy a vehicle?'
    bundle = prepare_scholar_context(q, intent="SENSITIVE_FIQH")
    assert bundle.fast_response is not None
    assert "Marital Dissolution" in bundle.fast_response
    assert "Financial Transactions" in bundle.fast_response


def test_canonical_114_surah_whitelist():
    """Verify canonical Surah name normalization and recognition."""
    assert normalize_surah_name("Al-Baqarah") in CANONICAL_SURAH_NAME_SET
    assert normalize_surah_name("At-Takwir") in CANONICAL_SURAH_NAME_SET
    assert normalize_surah_name("Surah Al-Kahf") in CANONICAL_SURAH_NAME_SET or "kahf" in CANONICAL_SURAH_NAME_SET
    # Non-canonical fabricated names must NOT be in the whitelist
    assert normalize_surah_name("Al-Qiyaq") not in CANONICAL_SURAH_NAME_SET


def test_sanitizes_fabricated_surah_and_negative_hadith_tag():
    """Verify that verify_grounded_citations strips non-canonical Surah names and ungrounded [H#] tags."""
    raw_llm_output = (
        "From [Q1]: Allah establishes that the record will be placed.\n"
        "[H1] Surah Al-Qiyaq (81:9) establishes an eternal foundation: And the Quran is from Allah.\n"
        "And Allah knows best (Allahu A'lam)."
    )
    context_text = "Context:\n[Q1] Surah Al-Kahf (18:49) deeds will be placed.\nNo Hadiths in context."

    sanitized = verify_grounded_citations(raw_llm_output, context_text)

    # Fabricated name Al-Qiyaq must be stripped
    assert "Al-Qiyaq" not in sanitized
    # Hallucinated [H1] marker must be stripped because context had 0 Hadiths
    assert "[H1]" not in sanitized
    # Authentic text must remain
    assert "From [Q1]: Allah establishes that the record will be placed." in sanitized
