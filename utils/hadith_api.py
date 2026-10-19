"""
Hidayah AI — Hadith Retrieval Adapter
Primary: sunnah.com API (verified hadith with authentication grades).
Fallback: Tavily web search filtered to trusted domains (commentary only).
"""

import re
import streamlit as st
from utils.config import (
    HADITH_TRUSTED_DOMAINS,
    HADITH_MAX_RESULTS,
    HADITH_PROVIDER_PRIMARY,
)
from utils.evidence import normalize_hadith
from utils.trust import trusted_host, COMMENTARY_DOMAINS
from utils.logger import get_logger

log = get_logger("hadith_api")

HADITH_REF_REGEX = re.compile(
    r"\b(bukhari|muslim|tirmidhi|tirmizi|abu\s*dawud|dawud|nasai|ibn\s*majah|majah|malik|muwatta|ahmad)\s*(?:hadith|no|number|#)?\s*(\d+)\b",
    re.IGNORECASE,
)


def resolve_hadith_reference(query_text: str) -> dict | None:
    """Inspect a query string for specific Hadith citations (e.g. 'Bukhari 1', 'Abu Dawud 1035').
    Resolves directly via the Keyless CDN Takhrīj adapter or official Sunnah.com API.
    """
    if not query_text:
        return None
    match = HADITH_REF_REGEX.search(query_text)
    if not match:
        return None

    collection_raw = match.group(1).strip()
    hadith_num = match.group(2).strip()

    try:
        from utils.sunnah_api import fetch_hadith_by_reference
        return fetch_hadith_by_reference(collection=collection_raw, hadith_number=hadith_num)
    except Exception as e:
        log.warning(f"Error resolving hadith reference: {e}")
        return None


# -----------------------------------------------------------------------------
# Curated Classical Authentication Database for Renowned Unauthentic Sayings
# (Mustalah al-Hadith & Kutub al-Mawdu'at)
# -----------------------------------------------------------------------------
KNOWN_UNAUTHENTIC_HADITHS = [
    {
        "patterns": [
            r"\b(seek knowledge.*china|even (?:unto|to) china)\b",
            r"(اطلبوا العلم ولو بالصين|طلب العلم ولو بالصين)",
        ],
        "statement": "«اطْلُبُوا الْعِلْمَ وَلَوْ بِالصِّينِ» (\"Seek knowledge even if you have to go to China\")",
        "status": "Mawdūʿ (Fabricated) / Daʿīf Jiddan (Extremely Weak)",
        "scholars": "Ibn al-Jawzi (Al-Mawdūʿāt 1/215), Ibn Hibban (Al-Majrūḥīn), Al-ʿUqayli, and Shaykh al-Albani (Silsilah al-Aḥādīth al-Ḍaʿīfah #416)",
        "theological_verdict": (
            "Classical Hadith masters have established that this phrase cannot be authentically attributed "
            "to the Messenger of Allah ﷺ. While Islam places paramount emphasis on seeking knowledge, the specific addition "
            "mentioning 'China' has chains that are severely defective (narrated through Abu 'Atikah Tarif bin Salman, who is Matruk/abandoned by Hadith critics)."
        ),
        "authentic_alternative": (
            "Sunan Ibn Majah #224 (Graded Sahih by Al-Albani):\n"
            "«طَلَبُ الْعِلْمِ فَرِيضَةٌ عَلَى كُلِّ مُسْلِمٍ»\n"
            "(\"Seeking sacred knowledge is an obligation upon every Muslim.\")"
        ),
        "canonical_ref": "Sunan Ibn Majah #224",
    },
    {
        "patterns": [
            r"\b(difference(?:s)? of opinion (?:in|among) my ummah is a mercy|ikhtilaf ummati rahmah)\b",
            r"(اختلاف أمتي رحمة|اختلاف أصحابي رحمة)",
        ],
        "statement": "«اخْتِلافُ أُمَّتِي رَحْمَةٌ» (\"Differences of opinion among my Ummah is a mercy\")",
        "status": "Lā Aṣla Lahu (No Authentic Chain / Unfounded Narration)",
        "scholars": "Imam al-Subki, Ibn Hazm (Al-Ihkam 5/64), and Shaykh al-Albani (Silsilah al-Aḥādīth al-Ḍaʿīfah #59)",
        "theological_verdict": (
            "Muhaddithin have noted that this phrase has no authentic Isnad from the Prophet ﷺ. "
            "While gentle scholarly disagreement in secondary jurisprudential matters (Furu') is accommodated through valid ijtihad, "
            "attributing this statement as a prophetic hadith is unverified."
        ),
        "authentic_alternative": (
            "Sahih al-Bukhari #7352 & Sahih Muslim #1716:\n"
            "«إِذَا حَكَمَ الْحَاكِمُ فَاجْتَهَدَ ثُمَّ أَصَابَ فَلَهُ أَجْرَانِ، وَإِذَا حَكَمَ فَاجْتَهَدَ ثُمَّ أَخْطَأَ فَلَهُ أَجْرٌ»\n"
            "(\"When a judge exerts his utmost effort (ijtihad) and is correct, he receives two rewards; if he errs, he receives one reward.\")"
        ),
        "canonical_ref": "Sahih al-Bukhari #7352",
    },
    {
        "patterns": [
            r"\b(love of (?:one's )?(?:homeland|country|nation) is (?:part of|from) faith|hubb al-?watan)\b",
            r"(حب الوطن من الإيمان)",
        ],
        "statement": "«حُبُّ الْوَطَنِ مِنَ الإِيمَانِ» (\"Love of one's homeland is part of faith\")",
        "status": "Mawdūʿ (Fabricated as a Prophetic Hadith)",
        "scholars": "Al-Saghani (Al-Mawdu'at p. 7), Al-Qari (Al-Asrar al-Marfu'ah #164), and Al-Albani (Al-Da'ifah #36)",
        "theological_verdict": (
            "Loving one's birthplace or homeland is a noble, natural human instinct, but formulating it as a certified "
            "Hadith of the Prophet ﷺ is fabricated. It cannot be cited as canonical Sunnah."
        ),
        "authentic_alternative": (
            "Jami` at-Tirmidhi #3926 (Sahih):\n"
            "The Prophet's ﷺ heartfelt address to Makkah: «مَا أَطْيَبَكِ مِنْ بَلَدٍ وَأَحَبَّكِ إِلَيَّ...»\n"
            "(\"How sweet of a land you are and how beloved you are to me! Had my people not driven me out, I would not have dwelt anywhere else.\")"
        ),
        "canonical_ref": "Jami` at-Tirmidhi #3926",
    },
    {
        "patterns": [
            r"\b(cleanliness is (?:half of|part of|from) faith|an-?nazhafatu minal iman)\b",
            r"(النظافة من الإيمان)",
        ],
        "statement": "«النَّظَافَةُ مِنَ الإِيمَانِ» (\"Cleanliness is from faith\")",
        "status": "Ḍaʿīf (Weak in this specific phrasing)",
        "scholars": "Al-Tabarani, Ibn Hibban, and Al-Albani (Da'if al-Jami' #6129)",
        "theological_verdict": (
            "While bodily cleanliness is deeply virtuous in Islam, this specific phrasing is not an authentic hadith."
        ),
        "authentic_alternative": (
            "Sahih Muslim #223 (Canonical Sahih):\n"
            "«الطُّهُورُ شَطْرُ الإِيمَانِ»\n"
            "(\"Ritual and physical purity (Al-Tuhūr) is half of faith.\")"
        ),
        "canonical_ref": "Sahih Muslim #223",
    },
]


def check_unauthentic_hadith(query_text: str) -> dict | None:
    """Check if query is asking about a known unauthentic/fabricated narration."""
    if not query_text:
        return None
    q_lower = query_text.lower()
    for item in KNOWN_UNAUTHENTIC_HADITHS:
        for pat in item["patterns"]:
            if re.search(pat, q_lower, re.IGNORECASE):
                return item
    return None


def format_hadith_card(hadith: dict) -> str:
    """Format a verified canonical Hadith into a rich dual-script presentation card."""
    title = hadith.get("title", "Hadith Reference")
    url = hadith.get("canonical_url", hadith.get("url", "https://sunnah.com"))
    authority = hadith.get("authority", "Canonical Sunnah")
    meta = hadith.get("metadata", {})
    arabic_matn = meta.get("arabic_matn", "")
    english_trans = meta.get("english_translation", "")

    # If excerpt contains both, unpack if needed
    if not arabic_matn and not english_trans:
        excerpt = hadith.get("excerpt", "")
        if "Arabic Matn:" in excerpt and "English Translation:" in excerpt:
            parts = excerpt.split("English Translation:")
            arabic_matn = parts[0].replace("Arabic Matn:", "").strip()
            english_trans = parts[1].strip() if len(parts) > 1 else ""
        else:
            english_trans = excerpt

    card = [
        f"### 📜 [{title}]({url})",
        f"> **{authority}**",
        "",
    ]
    if arabic_matn:
        card.extend([
            f"<div dir='rtl' style='font-family: Scheherazade New, Amiri, serif; font-size: 1.25rem; line-height: 2.2; color: #f1f5f9; background: rgba(15, 23, 42, 0.45); padding: 1.1rem; border-radius: 8px; border-right: 4px solid #d4af37; margin: 0.8rem 0;'>",
            arabic_matn,
            "</div>",
            "",
        ])
    if english_trans:
        card.extend([
            "**English Translation:**",
            f"> {english_trans}",
            "",
        ])
    card.append(f"*Verified canonical record via [{title} on Sunnah.com]({url})*")
    return "\n".join(card)


#  Primary: Canonical LanceDB 50,762 Hadiths ─

def _fetch_from_canonical_lancedb(
    ayah_text_english: str,
    surah_name: str,
    ayah_number: int,
    max_results: int = HADITH_MAX_RESULTS,
) -> list[dict]:
    """Fetch matching hadiths from pre-indexed local LanceDB (50,762 canonical hadith corpus)."""
    try:
        from rag.lancedb_store import search_canonical_hadiths

        # Build focused search keywords
        query_parts = []
        if surah_name:
            query_parts.append(surah_name)
        if ayah_text_english:
            query_parts.append(ayah_text_english[:120])
        keyword = " ".join(query_parts).strip()
        if not keyword:
            keyword = f"{surah_name} {ayah_number}".strip()

        results = search_canonical_hadiths(query_text=keyword, top_k=max_results)
        if not results and surah_name:
            results = search_canonical_hadiths(query_text=surah_name, top_k=max_results)

        if not results:
            return []

        normalized = []
        for h in results:
            book = h.get("book", "Hadith Collection")
            h_no = str(h.get("hadith_no", ""))
            chapter = h.get("chapter", "")
            text = h.get("text", "").strip()

            normalized.append(
                normalize_hadith(
                    source_name=f"{book} (Canonical)",
                    title=f"{book} #{h_no} - {chapter}" if chapter else f"{book} #{h_no}",
                    excerpt=text,
                    url="https://sunnah.com",
                    language="en",
                    citation_id=f"hadith:{book.lower().replace(' ', '_')}:{h_no}",
                    canonical_url="https://sunnah.com",
                    link_type="canonical",
                    canonical_status="verified",
                    source_rank=1,
                    authority="Canonical Hadith Corpus (50,762 Verified)",
                    metadata={
                        "book": book,
                        "hadith_no": h_no,
                        "chapter": chapter,
                        "surah_name": surah_name,
                        "ayah_number": ayah_number,
                        "provider": "canonical_lancedb",
                    },
                )
            )

        log.info(f"LanceDB canonical hadiths returned {len(normalized)} narrations for {surah_name}:{ayah_number}")
        return normalized[:max_results]
    except Exception as e:
        log.warning(f"LanceDB canonical hadith search notice: {e}")
        return []


#  Secondary: sunnah.com API ─

def _fetch_from_sunnah_api(
    ayah_text_english: str,
    surah_name: str,
    ayah_number: int,
    max_results: int,
) -> list[dict]:
    """Fetch hadith from sunnah.com API using keyword search."""
    try:
        from utils.sunnah_api import search_hadith_by_keyword, is_available

        if not is_available():
            log.info("sunnah.com API not configured, skipping to fallback")
            return []

        # Build a focused search keyword from the ayah context
        keyword_parts = []
        if surah_name:
            keyword_parts.append(surah_name)
        if ayah_text_english:
            keyword_parts.append(ayah_text_english[:120])

        keyword = " ".join(keyword_parts).strip()
        if not keyword:
            keyword = f"Quran {surah_name} verse {ayah_number}"

        results = search_hadith_by_keyword(
            keyword=keyword,
            max_results=max_results,
        )
        log.info(f"sunnah.com returned {len(results)} results for {surah_name}:{ayah_number}")
        return results

    except Exception as e:
        log.error(f"sunnah.com adapter error: {e}")
        return []


#  Fallback: Tavily Web Search (commentary only) ─

def _fetch_web_commentary_fallback(
    ayah_text_english: str,
    surah_name: str,
    ayah_number: int,
    max_results: int,
) -> list[dict]:
    """Fetch scholarly commentary via Tavily web search (NOT hadith corpus)."""
    try:
        from agents.web_search import search_web
    except ImportError:
        log.error("web_search module not available")
        return []

    query = f"{surah_name} {ayah_number} related hadith explanation"
    if ayah_text_english:
        query = f"{query} {ayah_text_english[:140]}"

    domain_filter = " OR ".join(f"site:{d}" for d in HADITH_TRUSTED_DOMAINS)
    full_query = f"{query} {domain_filter}"

    results = search_web(full_query, max_results=max_results)
    normalized = []

    for item in results:
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "")

        if not url:
            continue

        trusted = trusted_host(url, HADITH_TRUSTED_DOMAINS)
        if not trusted:
            continue

        is_commentary = trusted_host(url, COMMENTARY_DOMAINS)
        if trusted == "sunnah.com":
            source_name = "Sunnah.com (Web)"
            source_type = "hadith_collection"
            authority = "Hadith Reference (Web-sourced)"
            canonical_status = "domain_verified"
        elif is_commentary:
            source_name = "IslamQA Commentary"
            source_type = "scholarly_commentary"
            authority = "Scholarly Commentary"
            canonical_status = "unverified"
        else:
            source_name = f"{trusted} Reference"
            source_type = "web_reference"
            authority = "Web Reference"
            canonical_status = "unverified"

        normalized.append(
            normalize_hadith(
                source_name=source_name,
                title=title or f"Related Reference — {surah_name} {ayah_number}",
                excerpt=content,
                url=url,
                language="en",
                citation_id=f"hadith:{source_name.lower().replace(' ', '_')}:{url}",
                canonical_url=url,
                link_type="search_fallback",
                canonical_status=canonical_status,
                authority=authority,
                metadata={
                    "surah_name": surah_name,
                    "ayah_number": ayah_number,
                    "trusted_domain": trusted,
                    "source_type": source_type,
                    "provider": "tavily_web",
                },
            )
        )

    return normalized[:max_results]


#  Public Interface 

@st.cache_data(ttl=900, show_spinner=False)
def fetch_related_hadith(
    ayah_text_english: str,
    surah_name: str,
    ayah_number: int,
    max_results: int = HADITH_MAX_RESULTS,
) -> list[dict]:
    """Fetch related Hadith references using the configured provider strategy.

    1. Explicit reference resolution (e.g. 'Bukhari 1' or 'Abu Dawud 1035') via CDN/Sunnah.
    2. Primary: Local LanceDB canonical hadiths (50,762 authentic narrations).
    3. Secondary: sunnah.com / CDN search.
    4. Fallback: Tavily web search (domain-verified commentary).
    """
    # 0. Check if the query itself or context mentions an explicit Hadith citation
    for candidate in [ayah_text_english, f"{surah_name} {ayah_number}"]:
        if candidate:
            ref_hit = resolve_hadith_reference(candidate)
            if ref_hit:
                log.info(f"Directly resolved explicit hadith citation: {ref_hit.get('title')}")
                return [ref_hit]

    results = []

    # 1. Primary: Local LanceDB (50,762 authentic Hadiths)
    if HADITH_PROVIDER_PRIMARY in {"canonical_lancedb", "lancedb", "local"}:
        results = _fetch_from_canonical_lancedb(
            ayah_text_english=ayah_text_english,
            surah_name=surah_name,
            ayah_number=ayah_number,
            max_results=max_results,
        )

    # 2. Secondary: sunnah.com / CDN API
    if not results and HADITH_PROVIDER_PRIMARY in {"sunnah_api", "canonical_lancedb"}:
        results = _fetch_from_sunnah_api(
            ayah_text_english=ayah_text_english,
            surah_name=surah_name,
            ayah_number=ayah_number,
            max_results=max_results,
        )

    # 3. Tertiary: Web Search Fallback
    if not results:
        log.info("Primary & secondary hadith sources returned 0 results, falling back to web search")
        results = _fetch_web_commentary_fallback(
            ayah_text_english=ayah_text_english,
            surah_name=surah_name,
            ayah_number=ayah_number,
            max_results=max_results,
        )

    return results[:max_results]
