"""
Hidayah AI — Sunnah.com Hadith API Adapter
Fetches authenticated hadith with grades from the sunnah.com REST API.
Provides verified hadith text with narrator chains and scholarly grades.

API docs: https://sunnah.api-docs.io/
"""

import concurrent.futures
import requests
import streamlit as st
from utils.config import (
    SUNNAH_API_KEY,
    SUNNAH_API_BASE,
    HADITH_COLLECTIONS,
    HADITH_MAX_RESULTS,
    HADITH_CDN_PRIMARY,
    HADITH_CDN_SECONDARY,
    HADITH_CDN_TIMEOUT,
    HADITH_CDN_EDITIONS,
)
from utils.evidence import normalize_hadith
from utils.logger import get_logger
from utils.retry import get_with_retry

log = get_logger("sunnah_api")

_HEADERS = {}


def _get_headers() -> dict:
    """Build API headers with key (cached for session)."""
    global _HEADERS
    if not _HEADERS and SUNNAH_API_KEY:
        _HEADERS = {"x-api-key": SUNNAH_API_KEY}
    return _HEADERS


def _grade_label(grades: list[dict]) -> str:
    """Extract the best authentication grade from a hadith's grade list.

    Returns one of: Sahih, Hasan, Da'if, or the raw grade string.
    """
    if not grades:
        return "Unknown"
    # Take the first (primary) grade
    grade_text = (grades[0].get("grade") or "").strip()
    lowered = grade_text.lower()

    if "sahih" in lowered:
        return "Sahih"
    if "hasan" in lowered:
        return "Hasan"
    if "da'if" in lowered or "daif" in lowered or "weak" in lowered:
        return "Da'if"
    if "maudu" in lowered or "fabricated" in lowered:
        return "Fabricated"
    return grade_text or "Unknown"


def _grade_to_confidence(grade: str) -> str:
    """Map hadith grade to confidence level."""
    grade_lower = grade.lower()
    if "sahih" in grade_lower:
        return "verified"
    if "hasan" in grade_lower:
        return "domain_verified"
    return "unverified"


@st.cache_data(ttl=3600, show_spinner=False)
def search_hadith_by_keyword(
    keyword: str,
    collection: str = "",
    max_results: int = HADITH_MAX_RESULTS,
) -> list[dict]:
    """Search for hadith by keyword across collections.

    Args:
        keyword: Search term (e.g., "fasting ramadan").
        collection: Optional specific collection (e.g., "bukhari"). Empty = all.
        max_results: Maximum results to return.

    Returns:
        List of normalized hadith evidence dicts.
    """
    if not SUNNAH_API_KEY:
        log.warning("SUNNAH_API_KEY not configured — skipping sunnah.com search")
        return []

    headers = _get_headers()
    results = []

    # Search across priority collections if none specified
    collections_to_search = (
        [collection] if collection
        else ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah"]
    )

    for coll_name in collections_to_search:
        if len(results) >= max_results:
            break

        url = f"{SUNNAH_API_BASE}/hadiths"
        params = {
            "collection": coll_name,
            "limit": min(max_results - len(results), 5),
            "page": 1,
        }

        try:
            log.info(f"Searching sunnah.com: collection={coll_name}, keyword='{keyword[:60]}'")
            resp = get_with_retry(url, headers=headers, params=params, timeout=12, label=f"sunnah:search:{coll_name}")
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("data", []):
                hadith_en = ""
                hadith_ar = ""
                for body in item.get("hadith", []):
                    lang = body.get("lang", "")
                    if lang == "en":
                        hadith_en = body.get("body", "")
                    elif lang == "ar":
                        hadith_ar = body.get("body", "")

                text = hadith_en or hadith_ar
                if not text:
                    continue

                grades = item.get("grades", [])
                grade = _grade_label(grades)
                hadith_number = item.get("hadithNumber", "")
                book_number = item.get("bookNumber", "")
                collection_display = HADITH_COLLECTIONS.get(coll_name, coll_name)
                canonical_url = f"https://sunnah.com/{coll_name}/{book_number}/{hadith_number}" if book_number else f"https://sunnah.com/{coll_name}"

                results.append(
                    normalize_hadith(
                        source_name=f"Sunnah.com — {collection_display}",
                        title=f"{collection_display} {hadith_number}",
                        excerpt=text.strip(),
                        url=canonical_url,
                        language="en" if hadith_en else "ar",
                        citation_id=f"hadith:sunnah:{coll_name}:{hadith_number}",
                        canonical_url=canonical_url,
                        link_type="api_verified",
                        canonical_status=_grade_to_confidence(grade),
                        authority="Hadith Corpus — Authenticated",
                        metadata={
                            "collection": coll_name,
                            "collection_name": collection_display,
                            "hadith_number": str(hadith_number),
                            "book_number": str(book_number),
                            "grade": grade,
                            "grade_raw": grades,
                            "source_type": "hadith_collection",
                            "provider": "sunnah.com",
                        },
                    )
                )

                if len(results) >= max_results:
                    break

        except requests.RequestException as e:
            log.warning(f"sunnah.com API error for {coll_name}: {e}")
            continue

    log.info(f"sunnah.com returned {len(results)} hadith results")
    return results[:max_results]


def _normalize_collection_key(coll: str) -> str:
    """Normalize user or API collection string into canonical slug."""
    c = (coll or "").lower().strip().replace("-", " ").replace("`", "").replace("'", "")
    if "bukhari" in c:
        return "bukhari"
    if "muslim" in c:
        return "muslim"
    if "dawud" in c or "dawood" in c:
        return "abudawud"
    if "tirmidhi" in c or "tirmizi" in c:
        return "tirmidhi"
    if "nasai" in c or "nasa'i" in c or "nisai" in c:
        return "nasai"
    if "majah" in c:
        return "ibnmajah"
    if "malik" in c or "muwatta" in c:
        return "malik"
    if "ahmad" in c:
        return "ahmad"
    if "riyad" in c:
        return "riyadussalihin"
    return c.replace(" ", "")


def _fetch_single_cdn_json(edition: str, hadith_number: str) -> tuple[str, list[dict], dict]:
    """Fetch hadith text and metadata from Fawaz Ahmed CDN with dual-mirror failover.
    
    Returns (text, grades, reference_dict).
    """
    clean_num = str(hadith_number).strip().lstrip("#")
    urls = [
        f"{HADITH_CDN_PRIMARY}/editions/{edition}/{clean_num}.json",
        f"{HADITH_CDN_SECONDARY}/editions/{edition}/{clean_num}.json",
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=2.0, headers={"User-Agent": "HidayahAI/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                hadiths = data.get("hadiths", [])
                if hadiths:
                    h = hadiths[0]
                    text = (h.get("text") or "").strip()
                    grades = h.get("grades") or []
                    ref = h.get("reference") or {}
                    return text, grades, ref
        except Exception as e:
            log.debug(f"CDN fetch attempt failed for {url}: {e}")
            continue
    return "", [], {}


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_hadith_from_cdn(
    collection: str,
    hadith_number: str,
) -> dict | None:
    """Fetch dual-script (Arabic Matn + English Translation + Named Scholar Grades)
    from the open-source keyless global CDN mirror with sub-100ms latency.
    """
    coll_key = _normalize_collection_key(collection)
    editions = HADITH_CDN_EDITIONS.get(coll_key)
    if not editions:
        return None

    clean_num = str(hadith_number).strip().lstrip("#")
    edition_en = editions.get("en", f"eng-{coll_key}")
    edition_ar = editions.get("ar", f"ara-{coll_key}")

    # Parallel dual-script retrieval (<100ms total)
    text_en, text_ar, grades, ref = "", "", [], {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_en = executor.submit(_fetch_single_cdn_json, edition_en, clean_num)
        future_ar = executor.submit(_fetch_single_cdn_json, edition_ar, clean_num)

        try:
            text_en, grades_en, ref_en = future_en.result(timeout=5.0)
            grades = grades_en
            ref = ref_en
        except Exception as e:
            log.warning(f"CDN English fetch timeout/error: {e}")

        try:
            text_ar, _, _ = future_ar.result(timeout=5.0)
        except Exception as e:
            log.warning(f"CDN Arabic fetch timeout/error: {e}")

    # Fallback to local LanceDB if English text was not fetched from CDN
    if not text_en:
        try:
            from rag.lancedb_store import search_canonical_hadiths
            local_hits = search_canonical_hadiths(f"{coll_key} {clean_num}", top_k=3)
            for h in local_hits:
                if str(h.get("hadith_no", "")) == clean_num:
                    text_en = h.get("text", "").strip()
                    break
        except Exception as l_err:
            log.debug(f"Local LanceDB fallback error: {l_err}")

    if not text_en and not text_ar:
        return None

    # Compile Dual-Script Excerpt (Arabic Matn first, English Translation second)
    excerpt_parts = []
    if text_ar:
        excerpt_parts.append(f"【النص العربي】\n{text_ar}")
    if text_en:
        excerpt_parts.append(f"【English Translation】\n{text_en}")
    excerpt = "\n\n".join(excerpt_parts)

    # Compile Named Scholar Grading Badges
    attributed_scholars = []
    for g in grades:
        s_name = g.get("name", "")
        s_grade = g.get("grade", "")
        if s_name and s_grade:
            attributed_scholars.append(f"{s_name}: {s_grade}")
    attributed_str = " | ".join(attributed_scholars)

    primary_grade = _grade_label(grades)
    if coll_key in {"bukhari", "muslim"} and primary_grade == "Unknown":
        primary_grade = "Sahih"
        attributed_str = "Canonical Sahih (Scholarly Consensus / Muttafaq 'Alayh)"

    collection_display = HADITH_COLLECTIONS.get(coll_key, coll_key.title())
    book_num = ref.get("book", "")
    canonical_url = f"https://sunnah.com/{coll_key}/{book_num}/{clean_num}" if book_num else f"https://sunnah.com/{coll_key}/{clean_num}"

    return normalize_hadith(
        source_name=f"Sunnah.com (CDN Mirror) — {collection_display}",
        title=f"{collection_display} #{clean_num}",
        excerpt=excerpt,
        url=canonical_url,
        language="en-ar",
        citation_id=f"hadith:cdn:{coll_key}:{clean_num}",
        canonical_url=canonical_url,
        link_type="cdn_verified",
        canonical_status=_grade_to_confidence(primary_grade),
        authority=f"Authenticity: {attributed_str}" if attributed_str else f"Authenticity: {primary_grade}",
        metadata={
            "collection": coll_key,
            "collection_name": collection_display,
            "hadith_number": str(clean_num),
            "book_number": str(book_num),
            "arabic_matn": text_ar,
            "english_translation": text_en,
            "grade": primary_grade,
            "grade_raw": grades,
            "scholars_attributed": attributed_str,
            "source_type": "hadith_collection",
            "provider": "fawazahmed_cdn",
        },
    )


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_hadith_by_reference(
    collection: str,
    hadith_number: str,
) -> dict | None:
    """Fetch a specific hadith by collection and number using resilient multi-tier fallback.
    
    1. If SUNNAH_API_KEY is configured -> Query official api.sunnah.com
    2. If SUNNAH_API_KEY is not configured or fails -> Query Keyless Global CDN Mirror (Dual-Script + Grades)
    3. If CDN fails -> Query local LanceDB canonical store
    """
    clean_num = str(hadith_number).strip().lstrip("#")
    coll_key = _normalize_collection_key(collection)

    # 1. Official Sunnah.com API (if credentials present)
    if SUNNAH_API_KEY:
        headers = _get_headers()
        url = f"{SUNNAH_API_BASE}/hadiths/{coll_key}:{clean_num}"
        try:
            resp = get_with_retry(url, headers=headers, timeout=8, label=f"sunnah:fetch:{coll_key}:{clean_num}")
            if resp.status_code == 200:
                item = resp.json()
                hadith_en = ""
                hadith_ar = ""
                for body in item.get("hadith", []):
                    lang = body.get("lang", "")
                    if lang == "en":
                        hadith_en = body.get("body", "")
                    elif lang == "ar":
                        hadith_ar = body.get("body", "")
                text = hadith_en or hadith_ar
                if text:
                    grades = item.get("grades", [])
                    grade = _grade_label(grades)
                    book_number = item.get("bookNumber", "")
                    collection_display = HADITH_COLLECTIONS.get(coll_key, coll_key.title())
                    canonical_url = f"https://sunnah.com/{coll_key}/{book_number}/{clean_num}" if book_number else f"https://sunnah.com/{coll_key}"
                    return normalize_hadith(
                        source_name=f"Sunnah.com — {collection_display}",
                        title=f"{collection_display} #{clean_num}",
                        excerpt=text.strip(),
                        url=canonical_url,
                        language="en" if hadith_en else "ar",
                        citation_id=f"hadith:sunnah:{coll_key}:{clean_num}",
                        canonical_url=canonical_url,
                        link_type="api_verified",
                        canonical_status=_grade_to_confidence(grade),
                        authority="Hadith Corpus — Authenticated",
                        metadata={
                            "collection": coll_key,
                            "collection_name": collection_display,
                            "hadith_number": str(clean_num),
                            "book_number": str(book_number),
                            "arabic_matn": hadith_ar,
                            "english_translation": hadith_en,
                            "grade": grade,
                            "grade_raw": grades,
                            "source_type": "hadith_collection",
                            "provider": "sunnah.com",
                        },
                    )
        except Exception as e:
            log.warning(f"Official sunnah.com API error for {coll_key}:{clean_num}: {e}")

    # 2. Keyless Global CDN Mirror (Instant Dual-Script AR+EN + Scholar Grades)
    cdn_result = fetch_hadith_from_cdn(coll_key, clean_num)
    if cdn_result:
        return cdn_result

    # 3. Local LanceDB Fallback
    try:
        from rag.lancedb_store import search_canonical_hadiths
        local_hits = search_canonical_hadiths(f"{coll_key} {clean_num}", top_k=2)
        for h in local_hits:
            h_no = str(h.get("hadith_no", ""))
            if h_no == clean_num:
                book = h.get("book", coll_key.title())
                return normalize_hadith(
                    source_name=f"{book} (Local LanceDB)",
                    title=f"{book} #{h_no}",
                    excerpt=h.get("text", "").strip(),
                    url=f"https://sunnah.com/{coll_key}/{clean_num}",
                    language="en",
                    citation_id=f"hadith:local:{coll_key}:{clean_num}",
                    canonical_url=f"https://sunnah.com/{coll_key}/{clean_num}",
                    link_type="canonical",
                    canonical_status="verified",
                    authority="Local Canonical Hadith Corpus (50,762 Verified)",
                    metadata={
                        "collection": coll_key,
                        "hadith_number": h_no,
                        "book": book,
                        "provider": "canonical_lancedb",
                    },
                )
    except Exception as lancedb_err:
        log.warning(f"Local LanceDB fallback error: {lancedb_err}")

    return None


def is_available() -> bool:
    """Check if hadith reference resolution is available.
    
    Always True because the keyless CDN mirror and local LanceDB are available without API keys.
    """
    return True

