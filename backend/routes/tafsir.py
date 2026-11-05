"""
Hidayah AI — Tafseer API Routes
Fetches classical & authentic multi-source Tafseer (Ibn Kathir, Jalalayn, Maariful Quran).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from utils.tafsir_api import fetch_multisource_tafseer_for_ayah
from utils.asbab_api import get_asbab_al_nuzul

router = APIRouter(prefix="/tafsir", tags=["Tafseer"])


@router.get("/asbab/{surah_number}/{ayah_number}")
async def get_ayah_asbab(surah_number: int, ayah_number: int):
    """
    Fetch authentic Occasions of Revelation (Asbab al-Nuzul) for a specific Ayah,
    grounded in the classical works of Imam al-Wahidi and Imam al-Suyuti.
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Invalid Surah number (1-114).")
    if ayah_number < 1:
        raise HTTPException(status_code=400, detail="Ayah number must be >= 1.")

    try:
        asbab = get_asbab_al_nuzul(surah_number, ayah_number)
        return asbab
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Asbab al-Nuzul: {str(e)}")



@router.get("/{surah_number}/{ayah_number}")
async def get_ayah_tafsir(
    surah_number: int,
    ayah_number: int,
    lang: str = Query("en", description="Language: en, ur, or ar"),
    max_sources: int = Query(3, description="Maximum number of Tafseer sources to return"),
):
    """
    Fetch multi-source Tafseer for a specific Ayah.
    Supports English, Urdu, and Arabic commentary.
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Invalid Surah number (1-114).")
    if ayah_number < 1:
        raise HTTPException(status_code=400, detail="Ayah number must be >= 1.")

    try:
        tafsir_items = fetch_multisource_tafseer_for_ayah(
            surah_number=surah_number,
            ayah_number=ayah_number,
            language=lang,
            max_sources=max_sources,
        )

        formatted_sources = []
        for src in tafsir_items or []:
            item = dict(src)
            text_val = item.get("text") or item.get("excerpt") or ""
            item["text"] = text_val
            item["excerpt"] = text_val
            formatted_sources.append(item)

        return {
            "surah_number": surah_number,
            "ayah_number": ayah_number,
            "language": lang,
            "sources": formatted_sources,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Tafseer: {str(e)}")
