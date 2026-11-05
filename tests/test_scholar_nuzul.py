"""
Unit tests for Scripture Coordinate Extraction and Asbab al-Nuzul Resolution.
"""

from agents.scholar import extract_scripture_coordinates


def test_extract_scripture_coordinates_colon_format():
    assert extract_scripture_coordinates("What is the tafseer of 2:183?") == [(2, 183)]
    assert extract_scripture_coordinates("Compare 18:49 and 54:49") == [(18, 49), (54, 49)]


def test_extract_scripture_coordinates_natural_language():
    # User's exact query
    coords = extract_scripture_coordinates("Explain Asbab al-Nuzul of Surah Al-Baqarah 183")
    assert (2, 183) in coords

    # Common speech variants
    assert (2, 183) in extract_scripture_coordinates("Surah Baqarah verse 183")
    assert (2, 183) in extract_scripture_coordinates("Al-Baqarah ayah 183")
    assert (18, 10) in extract_scripture_coordinates("Surah Al-Kahf verse 10")
    assert (1, 1) in extract_scripture_coordinates("Surah Al-Fatiha 1")


def test_extract_scripture_coordinates_no_ayah_returns_empty():
    # When user only mentions the Surah without an ayah number
    assert extract_scripture_coordinates("What are the themes of Surah Al-Baqarah?") == []
    assert extract_scripture_coordinates("Tell me about Surah 2") == []
