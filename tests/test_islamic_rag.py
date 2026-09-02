"""
Unit and Integration Tests for Hidayah AI Islamic RAG & LanceDB Pipeline
"""

import sys
import unittest
from rag.smart_loader import normalize_arabic, chunk_pages
from utils.islamic_guardrails import check_fatwa_sensitivity, verify_grounded_citations


class TestIslamicRAG(unittest.TestCase):

    def test_arabic_normalization(self):
        sample = "إِنَّا أَنزَلْنَاهُ فِي لَيْلَةِ الْقَدْرِ"
        normalized_with_tashkeel = normalize_arabic(sample, strip_tashkeel=False)
        self.assertIn("انزلناه", normalize_arabic(sample, strip_tashkeel=True))
        self.assertTrue(len(normalized_with_tashkeel) > 0)

    def test_chunk_pages(self):
        pages = [
            {"page": 1, "filename": "sample.pdf", "text": "This is paragraph one.\n\nThis is paragraph two about fasting in Ramadan."}
        ]
        chunks = chunk_pages(pages, chunk_size=10, overlap=2)
        self.assertTrue(len(chunks) > 0)
        self.assertEqual(chunks[0]["page"], 1)
        self.assertEqual(chunks[0]["filename"], "sample.pdf")

    def test_fatwa_guardrail_sensitive(self):
        divorce_query = "What is the ruling on three talaqs in one sitting for my wife?"
        guard = check_fatwa_sensitivity(divorce_query)
        self.assertIsNotNone(guard)
        self.assertIn("Marital Dissolution", guard)

        inheritance_query = "How to divide the inheritance and mirath for two sons and one daughter?"
        guard2 = check_fatwa_sensitivity(inheritance_query)
        self.assertIsNotNone(guard2)
        self.assertIn("Inheritance", guard2)

    def test_fatwa_guardrail_safe(self):
        safe_query = "What does Surah Al-Baqarah verse 183 say about the purpose of fasting?"
        guard = check_fatwa_sensitivity(safe_query)
        self.assertIsNone(guard)

    def test_citation_verification(self):
        context = "Tafsir Ibn Kathir explains [T1] regarding the virtue of charity."
        grounded_answer = "Charity brings blessings as explained in [T1]."
        verified = verify_grounded_citations(grounded_answer, context)
        self.assertNotIn("Citation Audit Note", verified)

        hallucinated_answer = "This hadith [H5] states something not in context."
        verified_hallucinated = verify_grounded_citations(hallucinated_answer, context)
        self.assertIn("Citation Audit Note", verified_hallucinated)
        self.assertIn("[H5]", verified_hallucinated)


if __name__ == "__main__":
    unittest.main()
