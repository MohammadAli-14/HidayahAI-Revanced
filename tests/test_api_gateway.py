"""
Hidayah AI — Complete API Gateway Verification Suite
Tests all endpoints: Health, Quran, Tafseer, Hadith Takhrīj, Scholar Agent, and RAG.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify system health and status check."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"
    assert "timestamp" in data


def test_juz_list_endpoint():
    """Verify the 30 Juz index is complete and properly formatted."""
    resp = client.get("/api/quran/juz-list")
    assert resp.status_code == 200
    data = resp.json()
    assert "juzs" in data
    assert len(data["juzs"]) == 30

    # Validate Juz 1 structure
    juz1 = data["juzs"][0]
    assert juz1["id"] == 1
    assert "name" in juz1
    assert "arabic" in juz1
    assert "surahs" in juz1


def test_audio_modes_endpoint():
    """Verify audio recitation modes."""
    resp = client.get("/api/quran/audio-modes")
    assert resp.status_code == 200
    data = resp.json()
    assert "modes" in data
    assert len(data["modes"]) >= 3
    assert "Arabic (Mishary Rashid)" in data["modes"]


def test_surahs_endpoint():
    """Verify Surahs catalog."""
    resp = client.get("/api/quran/surahs")
    assert resp.status_code == 200
    data = resp.json()
    assert "surahs" in data
    assert len(data["surahs"]) > 0
    surah1 = data["surahs"][0]
    assert surah1["number"] == 1
    assert "Al-Faa" in surah1["englishName"] or "Al-Fatihah" in surah1["englishName"]


def test_juz_ayahs_fetch():
    """Verify fetching ayahs with trilingual text and audio links for Juz 1."""
    resp = client.get("/api/quran/juz/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["juz"] == 1
    assert data["total_ayahs"] > 0
    assert len(data["ayahs"]) == data["total_ayahs"]

    # Check Ayah 1 attributes
    first_ayah = data["ayahs"][0]
    assert "arabic" in first_ayah and len(first_ayah["arabic"]) > 0
    assert "english" in first_ayah
    assert "urdu" in first_ayah
    assert "audio_url" in first_ayah
    assert first_ayah["number_in_surah"] == 1


def test_juz_boundary_validation():
    """Verify boundary validation for invalid Juz numbers."""
    resp_low = client.get("/api/quran/juz/0")
    assert resp_low.status_code == 400

    resp_high = client.get("/api/quran/juz/31")
    assert resp_high.status_code == 400


def test_tafsir_multisource():
    """Verify multi-source Tafseer endpoint returns authentic classical commentaries."""
    resp = client.get("/api/tafsir/1/1?lang=en")
    assert resp.status_code == 200
    data = resp.json()
    assert data["surah_number"] == 1
    assert data["ayah_number"] == 1
    assert "sources" in data
    assert len(data["sources"]) > 0

    first_source = data["sources"][0]
    assert "source_name" in first_source
    assert "text" in first_source
    assert len(first_source["text"]) > 0


def test_hadith_takhrij_canonical():
    """Verify deterministic coordinate lookup for Sahih al-Bukhari #1."""
    resp = client.get("/api/hadith/takhrij?q=Bukhari+1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "canonical_hadith"
    assert "data" in data
    assert "formatted_card" in data

    hadith = data["data"]
    assert "Sahih al-Bukhari" in hadith.get("title", "")
    assert "Sahih" in hadith.get("grade", "") or "Authentic" in hadith.get("grade", "")


def test_hadith_unauthentic_interception():
    """Verify that fabricated / unauthentic sayings are intercepted with classical Naqd warnings."""
    resp = client.get("/api/hadith/takhrij?q=Seek+knowledge+even+unto+China")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "unauthentic_warning"
    assert "Mawdūʿ" in data["status"] or "Daʿīf" in data["status"]
    assert "scholars" in data
    assert "verdict" in data
    assert "authentic_alternative" in data


def test_hadith_related():
    """Verify related Hadith endpoint."""
    resp = client.get("/api/hadith/related?surah_name=Al-Baqarah&ayah_number=183&max_results=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["surah_name"] == "Al-Baqarah"
    assert data["ayah_number"] == 183
    assert "results" in data


def test_scholar_empty_query_rejected():
    """Verify that empty queries return HTTP 400."""
    resp = client.post("/api/scholar/ask", json={"query": "   "})
    assert resp.status_code == 400


def test_scholar_sensitive_fiqh_advisory():
    """Verify that sensitive marital/divorce/inheritance queries trigger Islamic guardrail advisory notices."""
    resp = client.post("/api/scholar/ask", json={"query": "What are the rules of Talaq al-Sunnah vs Bid'ah?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "SENSITIVE_FIQH"
    assert "answer" in data
    # Must include classical scholarly etiquette or advisory notice
    assert "jurisprudence" in data["answer"].lower() or "scholars" in data["answer"].lower() or "fiqh" in data["answer"].lower()


def test_rag_documents_list():
    """Verify RAG knowledge base document listing endpoint."""
    resp = client.get("/api/rag/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total_chunks" in data
    assert isinstance(data["documents"], list)


def test_rag_upload_non_pdf_rejected():
    """Verify non-PDF uploads are rejected with HTTP 400."""
    files = {"file": ("test.txt", b"Non-pdf content", "text/plain")}
    resp = client.post("/api/rag/upload", files=files)
    assert resp.status_code == 400
