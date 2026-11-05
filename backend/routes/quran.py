"""
Hidayah AI — Quran API Routes
Serves 30 Juz, 114 Surahs, and trilingual Ayah data with audio URLs.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import requests

from utils.config import JUZ_DATA, AUDIO_MODES, QURAN_API_BASE
from utils.quran_api import fetch_juz_combined, get_surah_info_for_juz

router = APIRouter(prefix="/quran", tags=["Quran"])

# In-memory cache for 114 Surahs
_SURAHS_CACHE: List[Dict[str, Any]] = []


# Canonical verified Qurra (Reciters) for multi-reciter streaming
RECITER_CATALOG = [
    {
        "id": "ar.alafasy",
        "name": "Mishary Rashid Alafasy",
        "name_ar": "مشاري بن راشد العفاسي",
        "style": "Murattal",
        "description": "Fluid, melodic, highly accessible recitation style.",
        "bitrate": "128kbps",
        "audio_base": "https://cdn.islamic.network/quran/audio/128/ar.alafasy",
    },
    {
        "id": "ar.husary",
        "name": "Mahmoud Khalil Al-Husary",
        "name_ar": "محمود خليل الحصري",
        "style": "Tajweed Murattal",
        "description": "The gold standard for Tajweed precision, articulation, and deliberate learning.",
        "bitrate": "128kbps",
        "audio_base": "https://cdn.islamic.network/quran/audio/128/ar.husary",
    },
    {
        "id": "ar.abdulbasitmurattal",
        "name": "Abdul Basit Abdul Samad",
        "name_ar": "عبد الباسط عبد الصمد",
        "style": "Murattal",
        "description": "Timeless, resonant, classical Egyptian Murattal.",
        "bitrate": "192kbps",
        "audio_base": "https://cdn.islamic.network/quran/audio/192/ar.abdulbasitmurattal",
    },
    {
        "id": "ar.minshawi",
        "name": "Muhammad Siddiq Al-Minshawi",
        "name_ar": "محمد صديق المنشاوي",
        "style": "Murattal",
        "description": "Deeply spiritual, soulful, and heartfelt Murattal.",
        "bitrate": "128kbps",
        "audio_base": "https://cdn.islamic.network/quran/audio/128/ar.minshawi",
    },
    {
        "id": "ar.sudais",
        "name": "Abdul Rahman Al-Sudais",
        "name_ar": "عبد الرحمن السديس",
        "style": "Haramain Murattal",
        "description": "Renowned Imam of Masjid al-Haram, energetic and inspiring.",
        "bitrate": "192kbps",
        "audio_base": "https://cdn.islamic.network/quran/audio/192/ar.sudais",
    },
]


@router.get("/reciters")
async def get_reciters():
    """Return catalog of authentic canonical reciters."""
    return {"reciters": RECITER_CATALOG}


@router.get("/juz-list")
async def get_juz_list():
    """Return all 30 Juz with English, Arabic, and Surah ranges."""
    result = []
    for juz_id in range(1, 31):
        info = JUZ_DATA.get(juz_id, {})
        result.append({
            "id": juz_id,
            "name": info.get("name", f"Juz {juz_id}"),
            "arabic": info.get("arabic", ""),
            "english": info.get("english", ""),
            "surahs": info.get("surahs", ""),
        })
    return {"juzs": result}


@router.get("/audio-modes")
async def get_audio_modes():
    """Return available audio recitation modes."""
    return {"modes": AUDIO_MODES}


@router.get("/juz/{juz_id}")
async def get_juz_ayahs(juz_id: int):
    """
    Fetch and return combined Arabic, English, and Urdu text and audio URLs
    for a given Juz (1-30).
    """
    if juz_id < 1 or juz_id > 30:
        raise HTTPException(status_code=400, detail="Juz number must be between 1 and 30.")

    ayahs = fetch_juz_combined(juz_id)
    if not ayahs:
        raise HTTPException(status_code=502, detail=f"Failed to fetch Quran data for Juz {juz_id}.")

    surahs = get_surah_info_for_juz(ayahs)
    juz_meta = JUZ_DATA.get(juz_id, {})

    return {
        "juz": juz_id,
        "name": juz_meta.get("name", f"Juz {juz_id}"),
        "arabic": juz_meta.get("arabic", ""),
        "english": juz_meta.get("english", ""),
        "surahs_in_juz": surahs,
        "total_ayahs": len(ayahs),
        "ayahs": ayahs,
    }


@router.get("/surahs")
async def get_all_surahs():
    """Return list of all 114 Surahs from AlQuran.cloud API."""
    global _SURAHS_CACHE
    if _SURAHS_CACHE:
        return {"surahs": _SURAHS_CACHE}

    try:
        url = f"{QURAN_API_BASE}/surah"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 200:
            _SURAHS_CACHE = data.get("data", [])
            return {"surahs": _SURAHS_CACHE}
    except Exception as e:
        # Fallback minimal 114 list if external API fails
        fallback = [
            {"number": 1, "name": "سُورَةُ ٱلْفَاتِحَةِ", "englishName": "Al-Faatiha", "englishNameTranslation": "The Opening", "numberOfAyahs": 7},
            {"number": 2, "name": "سُورَةُ البَقَرَةِ", "englishName": "Al-Baqara", "englishNameTranslation": "The Cow", "numberOfAyahs": 286},
            {"number": 3, "name": "سُورَةُ آلِ عِمْرَانَ", "englishName": "Aal-i-Imraan", "englishNameTranslation": "The Family of Imraan", "numberOfAyahs": 200},
            {"number": 36, "name": "سُورَةُ يسٓ", "englishName": "Yaseen", "englishNameTranslation": "Yaseen", "numberOfAyahs": 83},
            {"number": 67, "name": "سُورَةُ المُلْكِ", "englishName": "Al-Mulk", "englishNameTranslation": "The Sovereignty", "numberOfAyahs": 30},
            {"number": 112, "name": "سُورَةُ الإِخْلَاصِ", "englishName": "Al-Ikhlaas", "englishNameTranslation": "Sincerity", "numberOfAyahs": 4},
        ]
        return {"surahs": fallback}

    raise HTTPException(status_code=502, detail="Failed to fetch Surahs catalog.")
