"""
Hidayah AI — Configuration & Constants
Loads environment variables, defines model names, color palette, and Juz metadata.
"""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load Environment
load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    """Resolve secret from environment or Streamlit secrets."""
    # 1. Try OS Environment (Local .env)
    val = os.getenv(key)
    if val:
        return val

    # 2. Try Streamlit Secrets (Production)
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return default


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

# Configure Gemini client globally
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Model Tier Strategy
MODEL_ROUTER = "gemini-2.5-flash"             # Intent classification (fastest)
MODEL_SCHOLAR = "gemini-2.5-flash"            # Scholarly chat & RAG answers (generous free tier)
MODEL_EMBEDDING = "gemini-embedding-001"      # Vector embeddings for RAG

# LanceDB & Reranking Strategy
_APP_DIR = Path(__file__).resolve().parent.parent
LANCEDB_DIR = _APP_DIR / "data" / "lancedb"
LANCEDB_DIR.mkdir(parents=True, exist_ok=True)
RERANKER_MODEL = "ms-marco-MiniLM-L-12-v2"    # Ultra-fast CPU cross-encoder reranker
USE_HYBRID_SEARCH = True                      # Combine Tantivy BM25 FTS + Vector embeddings

# Optional Local / Open-Source LLM (Ollama / vLLM fallback)
USE_LOCAL_LLM = get_secret("USE_LOCAL_LLM", "true").lower() in {"true", "1", "yes"}
LOCAL_LLM_URL = get_secret("LOCAL_LLM_URL", "http://localhost:11434/v1")
LOCAL_LLM_MODEL = get_secret("LOCAL_LLM_MODEL", "hidayah-lm:3b")

# Design Tokens (from design.instructions.md)
MIDNIGHT_BLUE = "#1a2a40"
BG_DARK = "#0F172A"
GOLD = "#D4AF37"
EMERALD_DEEP = "#064E3B"
EMERALD_LIGHT = "#10B981"
BG_LIGHT = "#F8FAFC"

# ── Logo Configuration ──
# Elite vector emblem synced to BG_DARK (#0F172A), GOLD (#D4AF37), and BG_LIGHT (#F8FAFC)
_DEFAULT_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="hidayahGold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F3DF99" />
      <stop offset="35%" stop-color="#D4AF37" />
      <stop offset="70%" stop-color="#AA8220" />
      <stop offset="100%" stop-color="#E6C665" />
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="96" fill="#0F172A" />
  <g transform="translate(256, 256) scale(1.15)" fill="none" stroke-miterlimit="10">
    <polygon points="0,-172 50.4,-121.6 121.6,-121.6 121.6,-50.4 172,0 121.6,50.4 121.6,121.6 50.4,121.6 0,172 -50.4,121.6 -121.6,121.6 -121.6,50.4 -172,0 -121.6,-50.4 -121.6,-121.6 -50.4,-121.6" stroke="url(#hidayahGold)" stroke-width="12" />
    <polyline points="-98,42 -140,0 -98,-42 -98,-98 -42,-98 0,-140 42,-98 98,-98 98,-42 140,0 98,42" stroke="#F8FAFC" stroke-width="10" stroke-linecap="square" />
    <polyline points="-82,36 0,88 82,36" stroke="#F8FAFC" stroke-width="10" stroke-linecap="square" />
    <polyline points="-98,58 0,118 98,58" stroke="url(#hidayahGold)" stroke-width="11" stroke-linecap="square" />
    <polyline points="-98,78 -98,98 -42,98 0,142 42,98 98,98 98,78" stroke="url(#hidayahGold)" stroke-width="10" stroke-linecap="square" />
    <line x1="-44" y1="-64" x2="-44" y2="30" stroke="url(#hidayahGold)" stroke-width="12" stroke-linecap="square" />
    <line x1="44" y1="8" x2="44" y2="30" stroke="url(#hidayahGold)" stroke-width="12" stroke-linecap="square" />
    <line x1="22" y1="8" x2="22" y2="38" stroke="url(#hidayahGold)" stroke-width="10" stroke-linecap="square" />
    <line x1="-22" y1="6" x2="-22" y2="38" stroke="url(#hidayahGold)" stroke-width="10" stroke-linecap="square" />
    <path d="M -22,-34 Q -12,-66 0,-80 Q 22,-54 22,-16 C 22,8 -18,12 -18,-14 C -18,-34 6,-34 6,-16 C 6,0 -26,8 -44,24" stroke="url(#hidayahGold)" stroke-width="12" stroke-linejoin="round" />
    <path d="M -14,-6 C 8,12 44,4 44,-24 L 44,-64" stroke="url(#hidayahGold)" stroke-width="12" stroke-linecap="square" />
  </g>
</svg>"""


def _resolve_logo_path() -> Path:
    """Resolve the active logo file in project root, auto-creating hidayah_logo.svg if missing."""
    candidates = [
        _APP_DIR / "hidayah_logo.svg",
        _APP_DIR / "hidayah_logo.png",
        _APP_DIR / "hidayah_logo.jpg",
        _APP_DIR / "Hidayah AI.png",
        _APP_DIR / "Hidayah AI.jpg",
        _APP_DIR / "Hadayah AI.jpg",
    ]
    for path in candidates:
        if path.exists():
            return path

    # Auto-create the crisp vector SVG in root if no logo file exists yet
    default_svg_path = _APP_DIR / "hidayah_logo.svg"
    try:
        default_svg_path.write_text(_DEFAULT_LOGO_SVG, encoding="utf-8")
    except Exception:
        pass
    return default_svg_path


LOGO_PATH = _resolve_logo_path()


def get_logo_base64() -> str:
    """Return the logo as a properly typed base64-encoded data URI for embedding in HTML."""
    path = _resolve_logo_path()
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = path.suffix.lower()
        if ext == ".svg":
            mime = "image/svg+xml"
        elif ext in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif ext == ".webp":
            mime = "image/webp"
        else:
            mime = "image/png"
        return f"data:{mime};base64,{data}"
    except FileNotFoundError:
        # Fallback to in-memory SVG if disk is read-only
        data = base64.b64encode(_DEFAULT_LOGO_SVG.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{data}"


# AlQuran.cloud API
QURAN_API_BASE = "https://api.alquran.cloud/v1"
ARABIC_EDITION = "ar.alafasy"       # Mishary Rashid Alafasy (with audio)
ENGLISH_EDITION = "en.asad"         # Muhammad Asad English translation
URDU_EDITION = "ur.jalandhry"       # Maulana Fateh Muhammad Jalandhry
ENGLISH_AUDIO_EDITION = "en.walk"   # Ibrahim Walk
URDU_AUDIO_EDITION = "ur.khan"      # Shamshad Ali Khan

# Tafseer & Hadith Sources
TAFSEER_EDITIONS = {
    "ar.muyassar": "Tafsir Al-Muyassar",
    "ar.jalalayn": "Tafsir Al-Jalalayn",
    "ar.qurtubi": "Tafsir Al-Qurtubi",
}
DEFAULT_TAFSEER_EDITION = "ar.muyassar"
TAFSEER_LANGUAGE_LABELS = {
    "ar": "Arabic",
    "en": "English",
    "ur": "Urdu",
}
TAFSEER_SOURCE_TARGET_COUNT = 3

# Tafseer provider strategy (phase-1 keeps current provider default for safety)
TAFSEER_PROVIDER_PRIMARY = "alquran_cloud"
TAFSEER_PROVIDER_PRIORITY = ["alquran_cloud", "quran_com", "spa5k"]
TAFSEER_ALLOW_TRANSLATION_AS_EXPLANATORY = True

# Preferred tafseer edition IDs (best-effort). Actual availability is resolved dynamically
# from AlQuran.cloud and these act as ranking hints only.
TAFSEER_PREFERRED_BY_LANGUAGE = {
    "ar": [
        "ar.muyassar",
        "ar.jalalayn",
        "ar.qurtubi",
        "ar.waseet",
        "ar.baghawi",
        "ar.miqbas",
    ],
    "en": [
        "en.jalalayn",
        "en.maududi",
        "en.ahmedali",
    ],
    "ur": [
        "ur.jalandhry",
        "ur.junagarhi",
        "ur.maududi",
    ],
}

# Hadith Source Strategy
# Primary: sunnah.com API (verified hadith with grades).
# Fallback: Tavily web search filtered to trusted domains (commentary only).
SUNNAH_API_KEY = get_secret("SUNNAH_API_KEY")
SUNNAH_API_BASE = "https://api.sunnah.com/v1"
HADITH_PROVIDER_PRIMARY = get_secret("HADITH_PROVIDER_PRIMARY", "canonical_lancedb")      # "canonical_lancedb" | "sunnah_api" | "web_search"
HADITH_TRUSTED_DOMAINS = [
    "sunnah.com",
    "islamqa.info",
]
HADITH_MAX_RESULTS = 4
CANONICAL_LINK_FALLBACK = "api_fallback"
HADITH_CANONICAL_STATUS_DEFAULT = "unverified"

# Hadith collections available via sunnah.com API (name → display label)
HADITH_COLLECTIONS = {
    "bukhari": "Sahih al-Bukhari",
    "muslim": "Sahih Muslim",
    "abudawud": "Sunan Abu Dawud",
    "tirmidhi": "Jami` at-Tirmidhi",
    "nasai": "Sunan an-Nasa'i",
    "ibnmajah": "Sunan Ibn Majah",
    "malik": "Muwatta Malik",
    "riyadussalihin": "Riyad as-Salihin",
}

# ── Keyless Edge CDN Mirrors (fawazahmed0/hadith-api) ──
HADITH_CDN_PRIMARY = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"
HADITH_CDN_SECONDARY = "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1"
HADITH_CDN_TIMEOUT = 3.5  # Max seconds before fallback to local LanceDB

# Collection slug mappings for keyless CDN editions (English, Arabic, Urdu)
HADITH_CDN_EDITIONS = {
    "bukhari": {"en": "eng-bukhari", "ar": "ara-bukhari", "ur": "urd-bukhari"},
    "muslim": {"en": "eng-muslim", "ar": "ara-muslim", "ur": "urd-muslim"},
    "abudawud": {"en": "eng-abudawud", "ar": "ara-abudawud", "ur": "urd-abudawud"},
    "tirmidhi": {"en": "eng-tirmidhi", "ar": "ara-tirmidhi", "ur": "urd-tirmidhi"},
    "nasai": {"en": "eng-nasai", "ar": "ara-nasai", "ur": "urd-nasai"},
    "ibnmajah": {"en": "eng-ibnmajah", "ar": "ara-ibnmajah", "ur": "urd-ibnmajah"},
    "malik": {"en": "eng-malik", "ar": "ara-malik", "ur": "urd-malik"},
    "ahmad": {"en": "eng-ahmad", "ar": "ara-ahmad", "ur": "urd-ahmad"},
}

# Quran.com v4 API ─
QURANCOM_API_BASE = "https://api.quran.com/api/v4"
# Quran.com tafsir resource IDs — real English/Urdu tafseer (not just translations)
QURANCOM_TAFSIRS = {
    "en": [
        {"id": 169, "name": "Tafsir Ibn Kathir", "language": "en"},
        {"id": 171, "name": "Maariful Quran", "language": "en"},
        {"id": 168, "name": "Tafsir al-Jalalayn", "language": "en"},
    ],
    "ur": [
        {"id": 159, "name": "Tafsir Ibn Kathir (Urdu)", "language": "ur"},
        {"id": 819, "name": "Maariful Quran (Urdu)", "language": "ur"},
    ],
    "ar": [
        {"id": 93, "name": "Tafsir al-Tabari", "language": "ar"},
        {"id": 90, "name": "Tafsir al-Baghawi", "language": "ar"},
    ],
}

# UI visibility controls for source transparency details.
# Keep False for production-facing UX; enable for internal QA/debugging.
SHOW_TECHNICAL_SOURCE_DETAILS = False

# Audio Modes ─
AUDIO_MODES = [
    "Arabic (Mishary Rashid)",
    "Arabic + Urdu Translation",
    "Arabic + English Translation",
    "Urdu Translation Only",
    "English Translation Only",
]

# 30 Juz Metadata
JUZ_DATA = {
    1:  {"name": "Alif Lam Mim", "arabic": "الم", "english": "Alif Lam Mim", "surahs": "Al-Fatiha 1 – Al-Baqarah 141"},
    2:  {"name": "Sayaqulu", "arabic": "سيقول", "english": "They will say", "surahs": "Al-Baqarah 142 – Al-Baqarah 252"},
    3:  {"name": "Tilka ar-Rusul", "arabic": "تلك الرسل", "english": "Those Messengers", "surahs": "Al-Baqarah 253 – Al-Imran 92"},
    4:  {"name": "Lan Tanalu", "arabic": "لن تنالوا", "english": "Never will you attain", "surahs": "Al-Imran 93 – An-Nisa 23"},
    5:  {"name": "Wal-Muhsanat", "arabic": "والمحصنات", "english": "And forbidden to you are", "surahs": "An-Nisa 24 – An-Nisa 147"},
    6:  {"name": "La Yuhibbu-llah", "arabic": "لا يحب الله", "english": "Allah does not like", "surahs": "An-Nisa 148 – Al-Ma'idah 81"},
    7:  {"name": "Wa Idha Sami'u", "arabic": "وإذا سمعوا", "english": "And when they hear", "surahs": "Al-Ma'idah 82 – Al-An'am 110"},
    8:  {"name": "Wa Lau Annana", "arabic": "ولو أننا", "english": "And even if We had", "surahs": "Al-An'am 111 – Al-A'raf 87"},
    9:  {"name": "Qal al-Mala'", "arabic": "قال الملأ", "english": "Said the eminent ones", "surahs": "Al-A'raf 88 – Al-Anfal 40"},
    10: {"name": "Wa A'lamu", "arabic": "واعلموا", "english": "And know that", "surahs": "Al-Anfal 41 – At-Tawbah 92"},
    11: {"name": "Ya'tadhiruna", "arabic": "يعتذرون", "english": "They will make excuses", "surahs": "At-Tawbah 93 – Hud 5"},
    12: {"name": "Wa Ma Min Dabbah", "arabic": "وما من دابة", "english": "And there is no creature", "surahs": "Hud 6 – Yusuf 52"},
    13: {"name": "Wa Ma Ubarri'u", "arabic": "وما أبرئ", "english": "And I do not acquit", "surahs": "Yusuf 53 – Ibrahim 52"},
    14: {"name": "Rubama", "arabic": "ربما", "english": "Perhaps", "surahs": "Al-Hijr 1 – An-Nahl 128"},
    15: {"name": "Subhan-alladhi", "arabic": "سبحان الذي", "english": "Exalted is He who", "surahs": "Al-Isra 1 – Al-Kahf 74"},
    16: {"name": "Qal Alam", "arabic": "قال ألم", "english": "Said: Did I not", "surahs": "Al-Kahf 75 – Ta-Ha 135"},
    17: {"name": "Iqtaraba", "arabic": "اقترب", "english": "Has drawn near", "surahs": "Al-Anbiya 1 – Al-Hajj 78"},
    18: {"name": "Qad Aflaha", "arabic": "قد أفلح", "english": "Certainly have succeeded", "surahs": "Al-Mu'minun 1 – Al-Furqan 20"},
    19: {"name": "Wa Qal-alladhina", "arabic": "وقال الذين", "english": "And said those who", "surahs": "Al-Furqan 21 – An-Naml 55"},
    20: {"name": "A'man Khalaqa", "arabic": "أمن خلق", "english": "Or, who created", "surahs": "An-Naml 56 – Al-Ankabut 45"},
    21: {"name": "Utlu Ma Uhiya", "arabic": "اتل ما أوحي", "english": "Recite what has been", "surahs": "Al-Ankabut 46 – Al-Ahzab 30"},
    22: {"name": "Wa Man Yaqnut", "arabic": "ومن يقنت", "english": "And whoever is obedient", "surahs": "Al-Ahzab 31 – Ya-Sin 27"},
    23: {"name": "Wa Mali", "arabic": "ومالي", "english": "And what is it for me", "surahs": "Ya-Sin 28 – Az-Zumar 31"},
    24: {"name": "Fa Man Azlamu", "arabic": "فمن أظلم", "english": "So who is more unjust", "surahs": "Az-Zumar 32 – Fussilat 46"},
    25: {"name": "Ilayhi Yuraddu", "arabic": "إليه يرد", "english": "To Him is referred", "surahs": "Fussilat 47 – Al-Jathiyah 37"},
    26: {"name": "Ha Mim", "arabic": "حم", "english": "Ha Mim", "surahs": "Al-Ahqaf 1 – Adh-Dhariyat 30"},
    27: {"name": "Qala Fa-ma Khatbukum", "arabic": "قال فما خطبكم", "english": "Said: Then what is your", "surahs": "Adh-Dhariyat 31 – Al-Hadid 29"},
    28: {"name": "Qad Sami Allahu", "arabic": "قد سمع الله", "english": "Certainly has Allah heard", "surahs": "Al-Mujadila 1 – At-Tahrim 12"},
    29: {"name": "Tabaraka-lladhi", "arabic": "تبارك الذي", "english": "Blessed is He who", "surahs": "Al-Mulk 1 – Al-Mursalat 50"},
    30: {"name": "Amma Yatasa'alun", "arabic": "عم يتساءلون", "english": "About what are they asking", "surahs": "An-Naba 1 – An-Nas 6"},
}


def get_gemini_client() -> genai.Client | None:
    """Return the global Gemini client instance."""
    return client


def get_juz_display_name(juz_num: int) -> str:
    """Return a formatted display string for a Juz number."""
    data = JUZ_DATA.get(juz_num, {})
    return data.get("name", f"Juz {juz_num}")