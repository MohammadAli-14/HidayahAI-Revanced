"""
Hidayah AI — Surah Thematic Knowledge Base & Classical Exegesis Index
Provides curated, authenticated thematic overviews, revelation backgrounds,
and core narrative divisions for Quranic Surahs to prevent LLM parametric cross-wiring.
"""

from typing import Optional

# Curated thematic overviews of major researched Surahs
SURAH_THEMES: dict[int, dict] = {
    1: {
        "name": "Al-Fatiha",
        "transliteration": "The Opening",
        "type": "Makki",
        "verses_count": 7,
        "central_theme": "Praise of Allah, acknowledgment of His exclusive Sovereignty and Mercy, and the ultimate supplication for the Straight Path (Sirat al-Mustaqim). It serves as Umm al-Kitab (Mother of the Book).",
        "core_divisions": [
            "Verses 1-4: Affirmation of Tawhid, Divine Names (Ar-Rahman, Ar-Rahim), and Master of the Day of Judgment.",
            "Verse 5: Covenant of exclusive worship and reliance ('Iyyaka na'budu wa iyyaka nasta'in').",
            "Verses 6-7: Dua for guidance to the path of the favored, avoiding those who earned wrath or went astray."
        ]
    },
    2: {
        "name": "Al-Baqarah",
        "transliteration": "The Cow",
        "type": "Madani",
        "verses_count": 286,
        "central_theme": "Comprehensive blueprint for the Muslim Ummah: foundational theology, law (shari'ah), covenants of previous nations (Bani Isra'il), social justice, and financial ethics.",
        "core_divisions": [
            "Verses 1-20: Categories of mankind (Believers, Disbelievers, Hypocrites).",
            "Verses 30-39: Creation of Adam (AS) and human stewardship (Khilafah) on earth.",
            "Verses 40-141: Critique of Bani Isra'il and the covenant of Ibrahim (AS).",
            "Verses 142-253: Ordinances of worship (Qiblah, Fasting, Hajj, Jihad) and family law.",
            "Verse 255: Ayat al-Kursi (The Throne Verse) — the greatest verse affirming absolute divine transcendence.",
            "Verses 275-281: Strict prohibition of Riba (usury/interest) and contract ethics.",
            "Verses 285-286: Concluding affirmation of faith and the prayer of believers."
        ]
    },
    3: {
        "name": "Aal-i-Imran",
        "transliteration": "The Family of Imran",
        "type": "Madani",
        "verses_count": 200,
        "central_theme": "Doctrinal steadfastness against theological distortion (dialogue with Christians of Najran regarding Isa AS) and perseverance through military and moral trials (Battle of Uhud).",
        "core_divisions": [
            "Verses 1-32: The decisive (Muhkam) and allegorical (Mutashabih) verses, and pure monotheism.",
            "Verses 33-64: The family of Imran, miraculous birth of Maryam and Isa (AS) as a human prophet.",
            "Verses 121-180: Detailed analysis of the Battle of Uhud: causes of setback, repentance, and courage.",
            "Verses 190-200: Reflection upon the cosmos for people of intellect ('Ulul Albab')."
        ]
    },
    4: {
        "name": "An-Nisa",
        "transliteration": "The Women",
        "type": "Madani",
        "verses_count": 176,
        "central_theme": "Social justice, protection of vulnerable societal segments (orphans, women, minorities), inheritance distribution (Mirath), family contracts, and institutional governance.",
        "core_divisions": [
            "Verses 1-10: Rights of orphans, marriage ethics, and protection of wealth.",
            "Verses 11-14: Statutory inheritance shares (Mirath) established by divine decree.",
            "Verses 19-35: Marital reconciliation, arbiters (Hakam), and mutual rights.",
            "Verse 59: Obedience to Allah, the Messenger, and legitimate authority (Uli al-Amr).",
            "Verse 135: Standing firmly for justice as witnesses for Allah, even against self or parents."
        ]
    },
    18: {
        "name": "Al-Kahf",
        "transliteration": "The Cave",
        "type": "Makki",
        "verses_count": 110,
        "central_theme": "Spiritual shield against trials (Fitnah) and the deceptive material illusions of worldly life (Dunya). It anchors believers against the 4 major existential tests before the end of time.",
        "core_divisions": [
            "1. Trial of Faith (Fitnat al-Deen) — Verses 9-26: The Companions of the Cave (Ashab al-Kahf) who fled tyranny to protect their pure monotheism.",
            "2. Trial of Wealth (Fitnat al-Mal) — Verses 32-44: The parable of the Owner of the Two Gardens (pride, materialism, and ultimate loss vs. true gratitude).",
            "3. Trial of Knowledge (Fitnat al-'Ilm) — Verses 60-82: The journey of Prophet Musa and Al-Khidr, revealing that divine wisdom often transcends limited human perception.",
            "4. Trial of Power & Authority (Fitnat al-Sultan) — Verses 83-98: The just ruler Dhul-Qarnayn who utilized supreme technological and military power strictly for justice and righteousness."
        ]
    },
    19: {
        "name": "Maryam",
        "transliteration": "Mary",
        "type": "Makki",
        "verses_count": 98,
        "central_theme": "Divine mercy, miraculous lineage of Prophets, vindication of Maryam (AS) from slander, and the reality of resurrection.",
        "core_divisions": [
            "Verses 1-15: The prayer of Zakariya (AS) and the miraculous birth of Yahya (AS).",
            "Verses 16-40: The conception and miraculous birth of Isa (AS) without a father, speaking from the cradle.",
            "Verses 41-50: The gentle debate between Ibrahim (AS) and his idolatrous father.",
            "Verses 66-98: Refutation of claims that Allah has taken an offspring; affirmation of the Day of Judgment."
        ]
    },
    36: {
        "name": "Ya-Sin",
        "transliteration": "Ya-Sin",
        "type": "Makki",
        "verses_count": 83,
        "central_theme": "The Heart of the Quran (Qalb al-Quran): affirming divine revelation, the truth of the Prophethood of Muhammad (peace be upon him), and undeniable signs of resurrection in nature.",
        "core_divisions": [
            "Verses 1-12: The certainty of revelation and the spiritual blindness of hardened deniers.",
            "Verses 13-32: The story of the Town (Ashab al-Qaryah) and the believer who gave his life for truth.",
            "Verses 33-44: Cosmic signs: reviving dead earth, the solar and lunar orbits, and ships sailing the seas.",
            "Verses 77-83: Philosophical refutation of resurrection skeptics: 'Kun fa-yakun' (He says to it 'Be', and it is)."
        ]
    },
    67: {
        "name": "Al-Mulk",
        "transliteration": "The Sovereignty",
        "type": "Makki",
        "verses_count": 30,
        "central_theme": "Protection from the punishment of the grave: awakening human consciousness to the perfection of Allah's creation, the purpose of life and death as a moral test, and accountability.",
        "core_divisions": [
            "Verses 1-5: The purpose of creation: testing who is best in deed (ahsan 'amala) and the flawless cosmos.",
            "Verses 6-12: The plight of the deniers in Hell and the great reward for those who fear their Lord unseen.",
            "Verses 13-24: Divine omniscience, the sustenance of birds in flight, and warnings of cosmic instability.",
            "Verses 28-30: Reflection upon water: if your water sank into the earth, who could bring you flowing spring water?"
        ]
    }
}

SURAH_NAME_TO_NUMBER: dict[str, int] = {
    "fatiha": 1, "al-fatiha": 1, "al fatiha": 1, "the opening": 1,
    "baqarah": 2, "al-baqarah": 2, "al baqarah": 2, "the cow": 2,
    "imran": 3, "aal-e-imran": 3, "aal i imran": 3, "ali imran": 3,
    "nisa": 4, "an-nisa": 4, "an-nisaa": 4, "an nisa": 4, "the women": 4,
    "maidah": 5, "al-maidah": 5, "al maaida": 5,
    "anam": 6, "al-anam": 6,
    "araf": 7, "al-araf": 7,
    "anfal": 8, "al-anfal": 8,
    "tawbah": 9, "at-tawbah": 9,
    "yunus": 10, "hud": 11, "yusuf": 12, "rad": 13, "ibrahim": 14, "hijr": 15, "nahl": 16, "isra": 17,
    "kahf": 18, "al-kahf": 18, "al kahf": 18, "the cave": 18,
    "maryam": 19, "taha": 20, "anbiya": 21, "hajj": 22, "muminun": 23, "nur": 24, "an-nur": 24,
    "furqan": 25, "shuara": 26, "naml": 27, "qasas": 28, "ankabut": 29, "rum": 30, "luqman": 31,
    "sajdah": 32, "ahzab": 33, "saba": 34, "fatir": 35,
    "yasin": 36, "ya-sin": 36, "ya sin": 36, "yaseen": 36,
    "mulk": 67, "al-mulk": 67, "al mulk": 67, "the sovereignty": 67,
    "qalam": 68, "haqqah": 69, "jinn": 72, "muzzammil": 73, "muddathir": 74, "qiyamah": 75,
    "insan": 76, "naba": 78, "fajr": 89, "duha": 93, "inshirah": 94, "tin": 95, "alaq": 96,
    "qadr": 97, "zalzalah": 99, "asr": 103, "fil": 105, "quraysh": 106, "kawthar": 108,
    "kafirun": 109, "nasr": 110, "ikhlas": 112, "falaq": 113, "nas": 114
}


def detect_surah_in_query(query: str) -> Optional[int]:
    """Detect if the user query references a specific Surah by name or number."""
    import re
    q_clean = query.lower().replace("-", " ").replace("'", "")
    
    # Check numerical: "surah 18", "chapter 18"
    m_num = re.search(r"(?:surah|chapter|sura)\s+(\d{1,3})\b", q_clean)
    if m_num:
        surah_id = int(m_num.group(1))
        if 1 <= surah_id <= 114:
            return surah_id
            
    # Check name map
    for name, s_id in SURAH_NAME_TO_NUMBER.items():
        # Match as whole word
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, q_clean):
            return s_id
            
    return None


def get_surah_thematic_summary(surah_number: int) -> Optional[str]:
    """
    Retrieve concise thematic exegesis of a Surah (under 150 words)
    to provide the LLM with grounded structural awareness.
    """
    theme_info = SURAH_THEMES.get(surah_number)
    if not theme_info:
        return None
        
    divisions_str = "\n".join(f"- {d}" for d in theme_info["core_divisions"])
    summary = (
        f"Surah {theme_info['name']} ({theme_info['transliteration']} — Chapter {surah_number}, {theme_info['type']}, {theme_info['verses_count']} verses):\n"
        f"Central Theme: {theme_info['central_theme']}\n"
        f"Structural Narratives:\n{divisions_str}"
    )
    return summary
