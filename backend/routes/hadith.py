"""
Hidayah AI — Hadith API Routes
Supports Takhrīj reference lookups, authentic chain analysis, and related hadiths.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import re
import urllib.parse

from utils.hadith_api import (
    resolve_hadith_reference,
    check_unauthentic_hadith,
    fetch_related_hadith,
    format_hadith_card,
)

router = APIRouter(prefix="/hadith", tags=["Hadith"])


def build_sunnah_url(book: str, hadith_no: str, chapter: str, arabic_text: str, english_text: str) -> str:
    """
    Build a direct, deep link to the exact Hadith on Sunnah.com
    instead of dropping the user on the generic homepage.
    """
    b_lower = (book or "").lower()
    slug = None
    if "bukhari" in b_lower: slug = "bukhari"
    elif "muslim" in b_lower: slug = "muslim"
    elif "dawud" in b_lower or "dawood" in b_lower: slug = "abudawud"
    elif "tirmidhi" in b_lower or "tirmizi" in b_lower: slug = "tirmidhi"
    elif "nasai" in b_lower or "nasa'i" in b_lower or "nisai" in b_lower: slug = "nasai"
    elif "majah" in b_lower: slug = "ibnmajah"
    elif "malik" in b_lower or "muwatta" in b_lower: slug = "malik"
    elif "ahmad" in b_lower: slug = "ahmad"
    elif "riyad" in b_lower: slug = "riyadussalihin"
    elif "mishkat" in b_lower: slug = "mishkat"
    elif "adab" in b_lower: slug = "adab"
    elif "bulugh" in b_lower: slug = "bulugh"
    elif "nawawi" in b_lower: slug = "nawawi40"
    elif "qudsi" in b_lower: slug = "qudsi40"

    clean_no = str(hadith_no).strip().lstrip("#")
    try:
        no_val = int(clean_no)
        max_bounds = {
            "bukhari": 7563, "muslim": 7500, "abudawud": 5274,
            "tirmidhi": 3956, "nasai": 5758, "ibnmajah": 4341,
            "malik": 1900, "ahmad": 28000, "riyadussalihin": 1900,
            "mishkat": 6300, "adab": 1329, "bulugh": 1600,
            "nawawi40": 42, "qudsi40": 40
        }
        if slug and 0 < no_val <= max_bounds.get(slug, 5000):
            return f"https://sunnah.com/{slug}:{no_val}"
    except (ValueError, TypeError):
        pass

    # Build targeted search query on Sunnah.com using distinctive Arabic or English terms
    if arabic_text:
        clean_ar = re.sub(r'[\u064B-\u065F\u0670]', '', arabic_text)
        words = [
            w for w in clean_ar.split()
            if len(w) > 2 and w not in {'وعن', 'قال', 'أنه', 'رسول', 'الله', 'صلى', 'عليه', 'وسلم', 'رضي', 'عنه', 'حدثنا', 'أخبرنا'}
        ]
        distinctive_ar = " ".join(words[:6])
        if len(distinctive_ar) > 5:
            q = f"{book} {distinctive_ar}".strip() if book else distinctive_ar
            return f"https://sunnah.com/search?q={urllib.parse.quote(q)}"

    if english_text:
        words_en = [
            w for w in english_text.split()
            if len(w) > 3 and w.lower() not in {'that', 'with', 'from', 'this', 'have', 'said', 'when', 'they', 'will', 'been'}
        ]
        distinctive_en = " ".join(words_en[:6])
        if len(distinctive_en) > 5:
            q = f"{book} {distinctive_en}".strip() if book else distinctive_en
            return f"https://sunnah.com/search?q={urllib.parse.quote(q)}"

    if slug:
        if chapter:
            return f"https://sunnah.com/search?q={urllib.parse.quote(slug + ' ' + chapter)}"
        return f"https://sunnah.com/{slug}"

    return "https://sunnah.com"


def get_theological_grade_badge(book: str, raw_grade: str, text: str) -> Dict[str, str]:
    """
    Categorize Hadith grading into standardized theological classifications:
    - Sahih (Authentic / Muttafaq 'Alayh) -> Gold/Emerald
    - Hasan (Sound / Good Chain) -> Cyan
    - Da'if (Weak) -> Amber
    - Mawdu' (Fabricated Warning) -> Rose
    """
    b_lower = (book or "").lower()
    g_lower = (raw_grade or "").lower()

    if "bukhari" in b_lower or "muslim" in b_lower:
        return {
            "tier": "sahih",
            "label": "Sahih (Canonical Consensus)",
            "color": "emerald",
        }
    
    if "mawdu" in g_lower or "fabricated" in g_lower or "mawdoo" in g_lower:
        return {
            "tier": "mawdu",
            "label": "Mawdu' (Fabricated Warning)",
            "color": "rose",
        }
    
    if "da'if" in g_lower or "daeef" in g_lower or "weak" in g_lower or "da'eef" in g_lower:
        return {
            "tier": "daif",
            "label": "Da'if (Weak Chain)",
            "color": "amber",
        }

    if "hasan" in g_lower:
        return {
            "tier": "hasan",
            "label": "Hasan (Sound Chain)",
            "color": "cyan",
        }

    if "sahih" in g_lower:
        return {
            "tier": "sahih",
            "label": "Sahih (Authentic)",
            "color": "emerald",
        }

    if any(k in b_lower for k in ["malik", "muwatta", "nawawi", "riyad"]):
        return {
            "tier": "sahih",
            "label": "Sahih (Authentic Canonical)",
            "color": "emerald",
        }

    if any(k in b_lower for k in ["dawud", "tirmidhi", "nasai", "majah", "mishkat", "adab"]):
        return {
            "tier": "hasan",
            "label": "Hasan / Sahih (Canonical Sunan)",
            "color": "cyan",
        }

    return {
        "tier": "canonical",
        "label": raw_grade if raw_grade and raw_grade != "sunnah.com" else "Canonical Record",
        "color": "emerald",
    }


def _normalize_related_hadith(item: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure consistent schema for Related Hadith cards in the Next.js drawer."""
    h = dict(item)
    meta = h.get("metadata") or {}
    excerpt = h.get("excerpt") or h.get("text") or ""

    arabic = h.get("text_arabic") or ""
    english = h.get("text_english") or ""
    narrator = h.get("narrator") or ""

    # Extract Arabic and English sections from LanceDB excerpt string
    if not arabic and not english and excerpt:
        if "Arabic:" in excerpt and "English:" in excerpt:
            parts_ar = excerpt.split("Arabic:", 1)
            if len(parts_ar) > 1:
                rest = parts_ar[1]
                parts_en = rest.split("English:", 1)
                arabic = parts_en[0].strip()
                english = parts_en[1].strip() if len(parts_en) > 1 else ""
        elif "English:" in excerpt:
            parts_en = excerpt.split("English:", 1)
            english = parts_en[1].strip()
        else:
            english = excerpt.strip()

    # Extract narrator line if present
    if not narrator and "Narrator:" in excerpt:
        try:
            n_part = excerpt.split("Narrator:", 1)[1]
            first_line = n_part.split("\n", 1)[0].strip()
            if first_line and not first_line.startswith("Arabic:"):
                narrator = first_line
        except Exception:
            pass

    book = meta.get("book") or h.get("book") or "Canonical Hadith"
    hadith_no = meta.get("hadith_no") or h.get("hadith_no") or ""
    chapter = meta.get("chapter") or h.get("chapter") or ""

    source_title = h.get("title") or (f"{book} #{hadith_no}" if hadith_no else book)
    if chapter and chapter not in source_title:
        source_title = f"{source_title} — {chapter}"

    grade = (
        h.get("grade")
        or meta.get("grade")
        or meta.get("hadith_grade")
        or "sunnah.com"
    )

    # Deep URL on Sunnah.com
    sunnah_deep_url = build_sunnah_url(book, hadith_no, chapter, arabic, english)

    h["source"] = source_title
    h["source_name"] = h.get("source_name") or book
    h["book"] = book
    h["hadith_no"] = hadith_no
    h["chapter"] = chapter
    h["grade"] = grade
    h["narrator"] = narrator
    h["text_arabic"] = arabic
    h["text_english"] = english
    h["text"] = english or excerpt
    h["url"] = sunnah_deep_url
    h["canonical_url"] = sunnah_deep_url
    h["grading_badge"] = get_theological_grade_badge(book, str(grade), english or excerpt)
    return h


@router.get("/takhrij")
async def lookup_hadith(q: str = Query(..., description="Query e.g. 'Bukhari 1' or 'Abu Dawud 1035'")):
    """
    Look up a specific Hadith reference by collection and number (Takhrīj).
    Returns Arabic Matn, English translation, and named scholar grading badges.
    """
    # 1. Check if it's a known fabricated / unauthentic narration
    unauth = check_unauthentic_hadith(q)
    if unauth:
        return {
            "type": "unauthentic_warning",
            "statement": unauth["statement"],
            "status": unauth["status"],
            "scholars": unauth["scholars"],
            "verdict": unauth["theological_verdict"],
            "authentic_alternative": unauth.get("authentic_alternative", ""),
            "canonical_ref": unauth.get("canonical_ref", ""),
        }

    # 2. Resolve coordinate reference
    hadith = resolve_hadith_reference(q)
    if not hadith:
        return {
            "type": "not_found",
            "message": f"Could not find exact canonical hadith reference matching '{q}'. Please try e.g. 'Bukhari 1' or 'Muslim 24'.",
        }

    # Ensure grade is exposed at top-level
    hadith_data = dict(hadith)
    meta = hadith_data.get("metadata") or {}
    grade_val = hadith_data.get("grade") or meta.get("hadith_grade") or hadith_data.get("authority") or "sunnah.com"
    hadith_data["grade"] = grade_val

    return {
        "type": "canonical_hadith",
        "data": hadith_data,
        "formatted_card": format_hadith_card(hadith),
    }


@router.get("/related")
async def get_related_hadith(
    surah_name: str = Query(..., description="Name of the Surah"),
    ayah_number: int = Query(..., description="Number of the Ayah"),
    ayah_text: str = Query("", description="English translation or topic text"),
    max_results: int = Query(3, description="Maximum number of narrations to return"),
):
    """
    Fetch related Hadiths for a given Ayah from local LanceDB canonical store or Sunnah.com.
    """
    try:
        raw_results = fetch_related_hadith(
            ayah_text_english=ayah_text,
            surah_name=surah_name,
            ayah_number=ayah_number,
            max_results=max_results,
        )
        normalized_results = [_normalize_related_hadith(r) for r in (raw_results or [])]
        return {
            "surah_name": surah_name,
            "ayah_number": ayah_number,
            "results": normalized_results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch related hadiths: {str(e)}")
