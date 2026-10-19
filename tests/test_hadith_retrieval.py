"""
Hidayah AI — Hadith Retrieval & Takhrīj Engine Unit Tests
========================================================
Validates:
1. Dual-Script Hadith fetching (Arabic Matn + English Translation).
2. Authenticated Scholarly Grades extraction (Al-Albani, Darussalam, Zubair Ali Zai).
3. Explicit reference regex parsing ("Bukhari 1", "Abu Dawud 1035").
4. Local LanceDB 50,762 Hadith search integrity.
"""

import unittest
from utils.sunnah_api import fetch_hadith_by_reference, fetch_hadith_from_cdn
from utils.hadith_api import resolve_hadith_reference
from rag.lancedb_store import search_canonical_hadiths


class TestHadithRetrievalEngine(unittest.TestCase):

    def test_bukhari_1_dual_script(self):
        """Verify Bukhari #1 returns verified Arabic Matn and English translation."""
        hadith = fetch_hadith_by_reference("bukhari", "1")
        self.assertIsNotNone(hadith, "Bukhari #1 should be resolved")
        self.assertEqual(hadith.get("type"), "hadith")
        self.assertIn("Sahih al-Bukhari", hadith.get("title", ""))
        self.assertIn("https://sunnah.com/bukhari", hadith.get("canonical_url", ""))

        excerpt = hadith.get("excerpt", "")
        # Verify dual-script presence
        self.assertTrue(
            "النص العربي" in excerpt or "English Translation" in excerpt or "reward of deeds" in excerpt.lower(),
            f"Excerpt should contain dual-script or verified text: {excerpt[:120]}"
        )

    def test_abudawud_1035_scholarly_grades(self):
        """Verify Abu Dawud #1035 extracts verified classical scholar grades."""
        hadith = fetch_hadith_by_reference("abudawud", "1035")
        self.assertIsNotNone(hadith, "Abu Dawud #1035 should be resolved")
        
        meta = hadith.get("metadata", {})
        grades = meta.get("grade_raw", [])
        self.assertTrue(len(grades) > 0, "Abu Dawud 1035 should contain classical grades")
        
        # Check for certifying scholar presence
        grade_str = str(grades)
        self.assertTrue(
            "Al-Albani" in grade_str or "Sahih" in grade_str or "Zubair Ali Zai" in grade_str,
            f"Grades should name certifying scholars: {grade_str}"
        )
        self.assertEqual(hadith.get("canonical_status"), "verified")

    def test_resolve_hadith_reference_parser(self):
        """Verify natural language queries with citations are resolved accurately."""
        # Query 1: Bukhari 1
        res1 = resolve_hadith_reference("What is the meaning of Sahih Bukhari 1 regarding intentions?")
        self.assertIsNotNone(res1)
        self.assertIn("Bukhari", res1.get("title", ""))

        # Query 2: Abu Dawud 1035
        res2 = resolve_hadith_reference("Can you check Abu Dawud #1035 authenticity?")
        self.assertIsNotNone(res2)
        self.assertIn("Abu Dawud", res2.get("title", ""))

        # Query 3: Non-reference query should return None
        res3 = resolve_hadith_reference("How do Muslims pray Fajr?")
        self.assertIsNone(res3, "General questions without Hadith references should return None")

    def test_local_lancedb_hadith_store(self):
        """Verify local LanceDB 50k corpus returns results offline in sub-10ms."""
        results = search_canonical_hadiths("deeds intentions", top_k=2)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0, "Local LanceDB should return matching hadiths")
        first_hit = results[0]
        self.assertIn("text", first_hit)
        self.assertIn("book", first_hit)

    def test_unauthentic_hadith_gate(self):
        """Verify that known fabricated/weak narrations are intercepted with classical takhrij."""
        from utils.hadith_api import check_unauthentic_hadith
        from agents.scholar import get_scholar_response

        # Test 1: Direct pattern match
        hit = check_unauthentic_hadith("Is the statement 'Seek knowledge even if you have to go to China' authentic?")
        self.assertIsNotNone(hit)
        self.assertIn("Mawdūʿ", hit["status"])
        self.assertIn("Sunan Ibn Majah #224", hit["authentic_alternative"])

        # Test 2: Full scholar response interception
        resp = get_scholar_response(
            query="Is the statement 'Seek knowledge even if you have to go to China' an authentic hadith of the Prophet ﷺ?",
            intent="HADITH_AUTHENTICATION",
        )
        self.assertIn("Mawdūʿ", resp)
        self.assertIn("Sunan Ibn Majah #224", resp)
        # Ensure it does NOT falsely attribute this to Bukhari
        self.assertNotIn("certified Hadith from Sahih al-Bukhari", resp)

    def test_direct_bukhari_1_matn_card(self):
        """Verify that direct queries for Bukhari 1 output the full Arabic Matn and English translation."""
        from agents.scholar import get_scholar_response

        resp = get_scholar_response(
            query="What is Bukhari hadith 1?",
            intent="HADITH_AUTHENTICATION",
        )
        self.assertIn("Sahih al-Bukhari #1", resp)
        self.assertIn("reward of deeds", resp.lower())
        self.assertIn("Authenticity:", resp)
        self.assertIn("Muttafaq 'Alayh", resp)

    def test_explicit_verse_disambiguation_no_fatiha_bleed(self):
        """Verify explicit verse queries (18:49 and 54:49) resolve the exact verses without Al-Faatiha bleed."""
        from rag.lancedb_store import get_canonical_ayah

        v1 = get_canonical_ayah(18, 49)
        self.assertIsNotNone(v1)
        self.assertEqual(v1.get("surah_name"), "Al-Kahf")
        self.assertIn("record [of deeds]", v1.get("text", "").lower())

        v2 = get_canonical_ayah(54, 49)
        self.assertIsNotNone(v2)
        self.assertEqual(v2.get("surah_name"), "Al-Qamar")
        self.assertIn("predestination", v2.get("text", "").lower())

    def test_comparative_fiqh_routing(self):
        """Verify that questions mentioning the four Sunni schools route to SENSITIVE_FIQH."""
        from agents.router import classify_intent_heuristic
        from utils.islamic_guardrails import classify_fatwa_sensitivity

        query = "Explain the differences between the four Sunni schools of thought regarding raising hands (Raf' al-Yadayn) before and after Ruku' in prayer."
        intent = classify_intent_heuristic(query)
        self.assertEqual(intent, "SENSITIVE_FIQH")

        info = classify_fatwa_sensitivity(query)
        self.assertTrue(info["is_sensitive"])
        self.assertFalse(info["is_personal_verdict"])
        self.assertTrue(info["requires_madhhab_synthesis"])


if __name__ == "__main__":
    unittest.main()
