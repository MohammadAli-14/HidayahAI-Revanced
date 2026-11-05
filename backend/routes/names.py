"""
Hidayah AI — Asma-ul-Husna (99 Names of Allah) API Routes
Provides endpoints for retrieving canonical names, categories, search, and scripture cross-references.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import logging

log = logging.getLogger("hidayah.names_api")

router = APIRouter(prefix="/names-of-allah", tags=["Names of Allah"])

_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "names_of_allah.json"
_NAMES_CACHE: List[Dict[str, Any]] = []


def _load_names() -> List[Dict[str, Any]]:
    global _NAMES_CACHE
    if _NAMES_CACHE:
        return _NAMES_CACHE
    if not _DATA_PATH.exists():
        log.error(f"Names dataset not found at {_DATA_PATH}")
        return []
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            _NAMES_CACHE = json.load(f)
            return _NAMES_CACHE
    except Exception as e:
        log.error(f"Failed to read names dataset: {e}")
        return []


@router.get("")
async def get_all_names(
    category: Optional[str] = Query(None, description="Filter by theological category"),
    search: Optional[str] = Query(None, description="Search term in Arabic, transliteration, English, or Urdu")
):
    """
    Fetch all 99 Names of Allah with optional category and search filtering.
    """
    names = _load_names()
    if not names:
        raise HTTPException(status_code=500, detail="Names of Allah dataset is not available.")

    results = names

    if category and category.lower() != "all":
        cat_lower = category.lower().strip()
        results = [
            n for n in results
            if n.get("category", "").lower() == cat_lower
            or n.get("category_ur", "").lower() == cat_lower
        ]

    if search:
        s = search.lower().strip()
        results = [
            n for n in results
            if s in n.get("name_ar", "").lower()
            or s in n.get("transliteration", "").lower()
            or s in n.get("meaning_en", "").lower()
            or s in n.get("meaning_ur", "").lower()
            or s in n.get("root_ar", "").lower()
            or s in str(n.get("number", ""))
        ]

    return {
        "total": len(results),
        "names": results
    }


@router.get("/categories")
async def get_categories():
    """
    Return available theological categories with counts.
    """
    names = _load_names()
    cats: Dict[str, Dict[str, Any]] = {}

    for n in names:
        c_en = n.get("category", "General")
        c_ur = n.get("category_ur", "")
        if c_en not in cats:
            cats[c_en] = {"category_en": c_en, "category_ur": c_ur, "count": 0}
        cats[c_en]["count"] += 1

    return {
        "categories": list(cats.values())
    }


@router.get("/{name_id}")
async def get_name_by_id(name_id: int):
    """
    Get a single Divine Name by ID (1-99).
    """
    if name_id < 1 or name_id > 99:
        raise HTTPException(status_code=400, detail="Name ID must be between 1 and 99.")

    names = _load_names()
    match = next((n for n in names if n.get("id") == name_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Name with ID {name_id} not found.")

    # Find adjacent names for prev/next navigation
    prev_id = 99 if name_id == 1 else name_id - 1
    next_id = 1 if name_id == 99 else name_id + 1

    return {
        "name": match,
        "navigation": {
            "prev_id": prev_id,
            "next_id": next_id
        }
    }


@router.get("/{name_id}/scripture")
async def get_name_scripture(name_id: int):
    """
    Retrieve contextual scripture (Quranic verses and Hadith citations)
    grounding this specific Divine Name.
    """
    if name_id < 1 or name_id > 99:
        raise HTTPException(status_code=400, detail="Name ID must be between 1 and 99.")

    names = _load_names()
    match = next((n for n in names if n.get("id") == name_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Name not found.")

    qrefs = match.get("quran_references", [])
    
    # Contextual canonical Hadith records
    hadiths = [
        {
            "collection": "Sahih al-Bukhari",
            "hadith_number": 2736,
            "narrator": "Abu Hurairah (may Allah be pleased with him)",
            "arabic": "إِنَّ لِلَّهِ تِسْعَةً وَتِسْعِينَ اسْمًا مِائَةً إِلَّا وَاحِدًا مَنْ أَحْصَاهَا دَخَلَ الْجَنَّةَ",
            "english": "Allah has ninety-nine names, one hundred less one; and he who memorizes them all by heart and acts upon them will enter Paradise.",
            "urdu": "اللہ تعالیٰ کے ننانوے نام ہیں، یعنی ایک کم سو، جس نے ان کو محفوظ کیا اور ان کا حق ادا کیا وہ جنت میں داخل ہو گا۔",
            "canonical_url": "https://sunnah.com/bukhari:2736"
        },
        {
            "collection": "Sahih Muslim",
            "hadith_number": 2677,
            "narrator": "Abu Hurairah (may Allah be pleased with him)",
            "arabic": "لِلَّهِ تِسْعَةٌ وَتِسْعُونَ اسْمًا مَنْ حَفِظَهَا دَخَلَ الْجَنَّةَ وَإِنَّ اللَّهَ وِتْرٌ يُحِبُّ الْوِتْرَ",
            "english": "To Allah belong ninety-nine names. He who memorizes them enters Paradise. And Allah is an odd number (One) and loves odd numbers.",
            "urdu": "اللہ کے ننانوے نام ہیں۔ جو انہیں یاد رکھے گا وہ جنت میں جائے گا، اور اللہ طاق ہے اور طاق کو پسند فرماتا ہے۔",
            "canonical_url": "https://sunnah.com/muslim:2677"
        }
    ]

    return {
        "name_id": name_id,
        "name_ar": match.get("name_ar"),
        "transliteration": match.get("transliteration"),
        "quran_verses": qrefs,
        "hadith_citations": hadiths
    }
