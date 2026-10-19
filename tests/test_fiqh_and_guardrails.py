"""
Hidayah AI — Unit Tests for Fiqh Knowledge Base & Guardrail Deduplication
========================================================================
Validates:
1. Classical 4-Madhhab Fiqh topic detection & grounding.
2. Procedural prayer query detection for Quranic noise suppression.
3. Verification that all 4 Sunni Madhhabs are represented with primary proofs.
4. Islamic guardrail citation audit deduplication.
"""

import unittest
from utils.fiqh_kb import (
    lookup_fiqh_topic,
    is_procedural_prayer_query,
    format_fiqh_grounding_block,
    FIQH_KNOWLEDGE_BASE,
)
from utils.islamic_guardrails import verify_grounded_citations


class TestFiqhAndGuardrails(unittest.TestCase):

    def test_raf_al_yadayn_detection(self):
        query = "Explain the differences between the four Sunni schools of thought regarding raising hands (Raf' al-Yadayn) before and after Ruku' in prayer."
        topic = lookup_fiqh_topic(query)
        self.assertIsNotNone(topic, "Should detect Raf al-Yadayn topic")
        self.assertIn("Rafʿ al-Yadayn", topic["title"])

        # Check all 4 schools are present
        schools = topic["schools"]
        self.assertIn("Hanafi", schools)
        self.assertIn("Maliki", schools)
        self.assertIn("Shafi'i", schools)
        self.assertIn("Hanbali", schools)

        # Check primary proofs
        self.assertIn("Ibn Mas", schools["Hanafi"]["proofs"])
        self.assertIn("Ibn ʿUmar", schools["Shafi'i"]["proofs"])
        self.assertIn("Amal Ahl al-Mad", schools["Maliki"]["proofs"])

    def test_procedural_suppression(self):
        # Pure procedural question -> True
        self.assertTrue(is_procedural_prayer_query("Raf al yadayn before and after ruku"))
        self.assertTrue(is_procedural_prayer_query("Where to place hands in prayer"))
        self.assertTrue(is_procedural_prayer_query("Saying amin aloud vs silently"))

        # Explicit Quran inquiry -> False (do not suppress)
        self.assertFalse(is_procedural_prayer_query("What does the Quran say about raising hands?"))
        self.assertFalse(is_procedural_prayer_query("Show me the verse about salah in Surah Al-Baqarah"))

    def test_other_fiqh_topics(self):
        self.assertIsNotNone(lookup_fiqh_topic("Where should hands be placed below navel or on chest?"))
        self.assertIsNotNone(lookup_fiqh_topic("Is saying amin aloud permissible behind the imam?"))
        self.assertIsNotNone(lookup_fiqh_topic("Can a person recite Surah Fatihah behind the imam?"))
        self.assertIsNotNone(lookup_fiqh_topic("Is Qunut in Fajr prayer Sunnah according to Imam Shafi'i?"))

    def test_guardrail_deduplication_on_comparison(self):
        # A response comparing 18:49 and 54:49 legitimately discussing Qadar and deeds
        sample_response = (
            "Comparing Surah Al-Kahf [18:49] and Surah Al-Qamar [54:49]. "
            "In 18:49, the Book of Deeds records all human actions. "
            "In 54:49, Allah created all things with predestination (Qadar). "
            "Both 18:49 and 54:49 harmonize divine decree with human accountability."
        )
        context = "[Q1] Surah Al-Kahf 18:49\n[Q2] Surah Al-Qamar 54:49"
        audited = verify_grounded_citations(sample_response, context)

        # Ensure no duplicate note repetition
        note_count = audited.count("The quote regarding divine decree (*Qadar*) is authentically from")
        self.assertEqual(note_count, 0, "Legitimate comparison of 18:49 and 54:49 should not trigger a false-alarm note")


if __name__ == "__main__":
    unittest.main()
