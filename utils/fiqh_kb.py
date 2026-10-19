"""
Hidayah AI — Classical Fiqh & Jurisprudence Knowledge Base
==========================================================
Deterministic, peer-reviewed classical comparative jurisprudence (Fiqh al-Muqāran)
covering consensus (Ijmāʿ) and legitimate divergence (Ikhtilāf) across the four
canonical Sunni Madhhabs: Ḥanafī, Mālikī, Shāfiʿī, and Ḥanbalī.

Grounds LLM prompts with primary scriptural proofs (Adillah Shar'iyyah)
to eliminate hallucinations in procedural prayer and legal queries.
"""

import re
from typing import Optional, Dict, Any

FIQH_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "raf_al_yadayn": {
        "title": "Raising the Hands in Prayer (Rafʿ al-Yadayn) Before & After Rukūʿ",
        "keywords": [
            r"\braf['’]?\s*(?:al[- ]?)?yadayn\b",
            r"\braising\s+hands?\s+(?:in\s+prayer|before\s+and\s+after\s+ruku|during\s+prayer|in\s+salah)\b",
            r"\bhands?\s+before\s+and\s+after\s+ruku\b",
            r"\braise\s+hands?\s+ruku\b",
        ],
        "classical_consensus": (
            "All four Sunni schools agree that raising hands at the opening Takbirat al-Ihram is Sunnah. "
            "They differ on raising hands before bowing into Ruku' and when rising from Ruku'."
        ),
        "schools": {
            "Hanafi": {
                "ruling": "Hands are raised ONLY at the initial Takbirat al-Ihram. Not raised before or after Ruku'.",
                "proofs": (
                    "Hadith of ʿAbdullāh ibn Masʿūd (رضي الله عنه): 'Shall I not pray for you the prayer of the Messenger of Allah ﷺ? "
                    "So he prayed, and he did not raise his hands except the first time.' (Jamiʿ at-Tirmidhi #257 - Hasan; Sunan Abi Dawud #748; Musnad Ahmad). "
                    "Also the report of al-Barāʾ ibn ʿĀzib (Sunan Abi Dawud #749) and the continuous practice of Kufa companions."
                ),
                "classical_references": "Al-Hidayah (Al-Marghinani), Radd al-Muhtar (Ibn 'Abidin).",
            },
            "Maliki": {
                "ruling": "The dominant, famous position (al-Mashhūr) is that hands are raised ONLY at the opening Takbirat al-Ihram. Not before or after Ruku'.",
                "proofs": (
                    "Based on the continuous living practice of the People of Madinah (ʿAmal Ahl al-Madīnah) recorded in Al-Mudawwanah. "
                    "Imam Malik regarded the continuous communal practice of Madinah as an authentic transmitted Sunnah. (Note: A secondary narration in the school permits it per Ibn 'Umar's hadith in the Muwatta)."
                ),
                "classical_references": "Al-Mudawwanah al-Kubra (Sahnun), Bidayat al-Mujtahid (Ibn Rushd).",
            },
            "Shafi'i": {
                "ruling": "Raising hands is confirmed Sunnah (Sunnah Muʾakkadah) at 4 points: 1) Opening Takbir, 2) Going into Ruku', 3) Rising from Ruku', and 4) Standing up after the first Tashahhud.",
                "proofs": (
                    "Hadith of ʿAbdullāh ibn ʿUmar (رضي الله عنهما): 'I saw the Messenger of Allah ﷺ raising his hands parallel to his shoulders "
                    "when he opened prayer, when he said Takbir for Ruku', and when he raised his head from Ruku'...' (Sahih al-Bukhari #735, Sahih Muslim #390). "
                    "Also Hadith of Malik bin al-Huwairith (Sahih al-Bukhari #737)."
                ),
                "classical_references": "Al-Majmuʿ Sharh al-Muhadhdhab (Al-Nawawi), Al-Umm (Al-Shafi'i).",
            },
            "Hanbali": {
                "ruling": "Raising hands is Sunnah at the same points: 1) Opening Takbir, 2) Bowing into Ruku', 3) Rising from Ruku', and 4) Standing from the first Tashahhud.",
                "proofs": (
                    "Authentic narrations of Ibn ʿUmar and Abu Humayd al-Sāʿidī with a group of 10 Companions affirming the Prophet's ﷺ prayer (Sahih al-Bukhari #828, Jamiʿ at-Tirmidhi #304)."
                ),
                "classical_references": "Al-Mughni (Ibn Qudamah), Zad al-Mustaqniʿ (Al-Hajjawi).",
            },
        },
        "adab_note": (
            "All four positions represent authenticated methodologies of the Sunnah among the Ahl al-Sunnah wa al-Jama'ah. "
            "Neither position invalidates the prayer, and classical scholars warned against discord over valid branches of Ikhtilaf."
        ),
    },

    "hand_placement": {
        "title": "Placement of Hands in Standing (Wadʿ al-Yadayn fī al-Qiyām)",
        "keywords": [
            r"\bhand\s+placement\b",
            r"\bwhere\s+to\s+place\s+hands?\s+in\s+prayer\b",
            r"\bhands?\s+(?:be\s+)?placed\b",
            r"\bhands?\s+on\s+chest\b",
            r"\bhands?\s+below\s+navel\b",
            r"\b(?:below|under)\s+(?:the\s+)?navel\b",
            r"\b(?:on|upon)\s+(?:the\s+)?chest\b",
            r"\bwad'?\s*al-?yadayn\b",
            r"\bsadl\b",
            r"\bqabd\b",
        ],
        "classical_consensus": (
            "The majority of scholars consider placing the right hand over the left (Qabd) to be Sunnah, while the famous Maliki view is Sadl (leaving hands at sides)."
        ),
        "schools": {
            "Hanafi": {
                "ruling": "Men place right hand over left below the navel (Taht al-Surrah). Women place hands on the chest.",
                "proofs": "Report of ʿAlī ibn Abī Ṭālib (رضي الله عنه): 'From the Sunnah in prayer is placing the right hand over the left below the navel' (Sunan Abi Dawud #756; Musnad Ahmad).",
                "classical_references": "Al-Bahr al-Ra'iq, Al-Hidayah.",
            },
            "Maliki": {
                "ruling": "The famous position (al-Mashhūr) in Al-Mudawwanah is Sadl (letting arms rest naturally at the sides) in obligatory prayers; Qabd is permitted in supererogatory (Nafl) prayers.",
                "proofs": "Based on ʿAmal Ahl al-Madīnah and the general Hadith of the person who prayed incorrectly (al-Musi' Salatahu), which mentioned standing without prescribing clasping.",
                "classical_references": "Al-Mudawwanah, Al-Risalah (Ibn Abi Zayd).",
            },
            "Shafi'i": {
                "ruling": "Hands are clasped right over left above the navel and below the chest, tilted slightly towards the left over the heart.",
                "proofs": "Hadith of Wāʾil ibn Ḥujr (رضي الله عنه) in Sahih Muslim #401 and Sahih Ibn Khuzaymah #479.",
                "classical_references": "Al-Majmuʿ (Al-Nawawi), Tuhfat al-Muhtaj.",
            },
            "Hanbali": {
                "ruling": "Preferred position is below the navel, or between the navel and chest; both reports exist from Imam Ahmad.",
                "proofs": "Narrations of Ali (below navel) and Wa'il ibn Hujr (chest/navel).",
                "classical_references": "Al-Mughni (Ibn Qudamah), Kashshaf al-Qinaʿ.",
            },
        },
        "adab_note": "A valid diversity of Sunnah practice with zero effect on the validity of salah.",
    },

    "saying_amin": {
        "title": "Saying 'Āmīn' Aloud vs. Silently (al-Taʾmīn fī al-Ṣalāh)",
        "keywords": [
            r"\bsaying\s+amin\b",
            r"\bamin\s+aloud\b",
            r"\bamin\s+silently\b",
            r"\bamin\b.*?\b(?:aloud|loudly|silently|quietly|softly)\b",
            r"\bjahran\s+bi-?al-?amin\b",
            r"\btamin\b",
        ],
        "classical_consensus": (
            "All four schools agree that saying 'Āmīn' after Surah Al-Fatihah is Sunnah. They differ on whether it is recited aloud (Jahran) or in a lowered voice (Sirran)."
        ),
        "schools": {
            "Hanafi": {
                "ruling": "Said silently (Sirran) by both the Imam and the followers in all prayers.",
                "proofs": "Per Surah Al-A'raf 7:55 ('Call upon your Lord in humility and in secret') and Hadith of Samurah bin Jundub that Amin is a supplication (Du'a) and should be recited quietly.",
                "classical_references": "Al-Hidayah, Fath al-Qadir.",
            },
            "Maliki": {
                "ruling": "Said silently (Sirran). The Imam does not recite it aloud; the follower says it silently in loud prayers.",
                "proofs": "ʿAmal Ahl al-Madīnah and the principle of preserving serenity in congregation.",
                "classical_references": "Al-Mudawwanah, Hashiyat al-Dusuqi.",
            },
            "Shafi'i": {
                "ruling": "Recited aloud (Jahran) by both the Imam and the congregation in loud prayers (Fajr, Maghrib, Isha).",
                "proofs": "Hadith of Abu Hurairah in Sahih al-Bukhari #780 and Muslim #410: 'When the Imam says Amin, say Amin...', and Wa'il ibn Hujr in Jami' at-Tirmidhi #248.",
                "classical_references": "Al-Majmuʿ (Al-Nawawi).",
            },
            "Hanbali": {
                "ruling": "Recited aloud (Jahran) by both Imam and followers in audible prayers.",
                "proofs": "Hadiths of Abu Hurairah and Wa'il ibn Hujr (Bukhari #780, Abu Dawud #932).",
                "classical_references": "Al-Mughni (Ibn Qudamah).",
            },
        },
        "adab_note": "Both loud and silent recitation of Amin are authentic traditions from the Companions.",
    },

    "fatihah_behind_imam": {
        "title": "Reciting Surah Al-Fātihah Behind the Imām (Qirāʾat Khalf al-Imām)",
        "keywords": [
            r"\bfatihah\s+behind\s+(?:the\s+)?imam\b",
            r"\breciting\s+fatihah\s+behind\s+(?:the\s+)?imam\b",
            r"\b(?:fatihah|fatiha)\b.*?\b(?:behind|khalf)\b.*?\b(?:the\s+)?imam\b",
            r"\bqira['a]t?\s+khalf\s+al-?imam\b",
        ],
        "classical_consensus": (
            "All schools agree Al-Fatihah is mandatory for the individual praying alone (Munfarid). They differ regarding the follower (Ma'mūm) behind an Imam."
        ),
        "schools": {
            "Hanafi": {
                "ruling": "The follower does NOT recite Al-Fatihah behind the Imam at all (neither in silent nor loud prayers); the Imam's recitation suffices.",
                "proofs": "Surah Al-A'raf 7:204 ('When the Quran is recited, listen to it and be silent') and Hadith: 'Whoever has an Imam, the recitation of the Imam is recitation for him' (Ibn Majah #850; Ahmad).",
                "classical_references": "Al-Hidayah, Radd al-Muhtar.",
            },
            "Maliki": {
                "ruling": "Follower recites Al-Fatihah in silent prayers (Dhuhr, Asr), but does NOT recite in loud prayers (Fajr, Maghrib, Isha).",
                "proofs": "Harmonizes Surah 7:204 (listening to loud recitation) with general commands to recite.",
                "classical_references": "Al-Mudawwanah, Al-Kafi (Ibn 'Abd al-Barr).",
            },
            "Shafi'i": {
                "ruling": "Reciting Al-Fatihah is an obligatory pillar (Rukn) for EVERY person: Imam, follower, and individual, in both silent and loud prayers.",
                "proofs": "Hadith of ʿUbadah ibn al-Samit in Sahih al-Bukhari #756 & Muslim #394: 'There is no prayer for whoever does not recite the Opening of the Book (Fatihat al-Kitab)'.",
                "classical_references": "Al-Umm, Al-Majmuʿ.",
            },
            "Hanbali": {
                "ruling": "Reciting Al-Fatihah is recommended (Mustahabb) in silent prayers and when the Imam pauses, but follower listens when Imam recites aloud.",
                "proofs": "Combines Hadith of 'Ubadah with Surah 7:204.",
                "classical_references": "Al-Mughni, Zad al-Mustaqniʿ.",
            },
        },
        "adab_note": "A classic Usul al-Fiqh difference on balancing Quranic general commands ('listen') with specific Hadith commands ('recite').",
    },

    "qunut_fajr": {
        "title": "Qunūt Supplication in Regular Daily Fajr Prayer",
        "keywords": [
            r"\bqun[ou]+t\s+(?:in\s+)?fajr\b",
            r"\bfajr\s+qun[ou]+t\b",
            r"\bqun[ou]+t\b.*?\bfajr\b",
        ],
        "classical_consensus": (
            "All schools agree Qunut is prescribed during acute crises (Qunut al-Nawazil). They differ on regular daily Fajr Qunut."
        ),
        "schools": {
            "Hanafi": {
                "ruling": "Not practiced in regular Fajr prayer; Qunut is restricted to Witr prayer and acute calamities (Nawāzil).",
                "proofs": "Hadith of Ibn Mas'ud and Abu Hurairah that the Prophet ﷺ performed Qunut in Fajr during crises for a month, then left it (Sahih Muslim #677).",
                "classical_references": "Al-Hidayah, Sharh Ma'ani al-Athar (Al-Tahawi).",
            },
            "Maliki": {
                "ruling": "Recommended (Mustahabb) in the second Rak'ah of Fajr, recited silently, preferably before Ruku' (or after).",
                "proofs": "Continuous practice of Madinah and narration of Anas bin Malik.",
                "classical_references": "Al-Mudawwanah, Mukhtasar Khalil.",
            },
            "Shafi'i": {
                "ruling": "Confirmed Sunnah (Sunnah Ab'ad) in the second Rak'ah of Fajr after rising from Ruku'. If omitted, Sujud al-Sahw is recommended.",
                "proofs": "Hadith of Anas bin Malik: 'The Prophet ﷺ did not cease making Qunut in Fajr until he left this world' (Musnad Ahmad #12679, Daraqutni).",
                "classical_references": "Al-Majmuʿ (Al-Nawawi), Minhaj al-Talibin.",
            },
            "Hanbali": {
                "ruling": "Not Sunnah in regular Fajr; performed only in Witr and during acute calamities (Nawāzil).",
                "proofs": "Narrations affirming the Prophet's ﷺ cessation of daily Fajr Qunut after one month (Sahih Muslim #677).",
                "classical_references": "Al-Mughni (Ibn Qudamah).",
            },
        },
        "adab_note": "Scholars emphasize that if praying behind an Imam of another Madhhab who performs Qunut (or leaves it), one follows the Imam respectfully.",
    },
}


def lookup_fiqh_topic(query: str) -> Optional[Dict[str, Any]]:
    """
    Match user query against high-precision classical Fiqh topics.
    Returns matched topic metadata or None.
    """
    if not query:
        return None
    q = query.lower().strip()

    for key, topic in FIQH_KNOWLEDGE_BASE.items():
        for pat in topic["keywords"]:
            if re.search(pat, q):
                return topic

    # General fallback for multi-madhhab queries
    if any(k in q for k in ["4 schools", "four schools", "4 madhhabs", "four madhhabs", "fiqh al-muqaran", "comparative fiqh"]):
        for key, topic in FIQH_KNOWLEDGE_BASE.items():
            for pat in topic["keywords"]:
                if re.search(pat, q):
                    return topic

    return None


def is_procedural_prayer_query(query: str) -> bool:
    """
    Detect if the inquiry is strictly about procedural physical prayer movements
    where the Holy Quran does not provide verse-by-verse physical mechanics.
    Used to suppress spurious lexical matches in Quranic vector search (e.g. 5:28 Cain & Abel).
    """
    if not query:
        return False
    q = query.lower()

    # If the user explicitly asks for Quranic verse or Ayah, do NOT suppress
    if any(explicit in q for explicit in ["quran", "ayah", "verse", "surah", "allah says", "kitab"]):
        return False

    procedural_indicators = [
        r"\braf['’]?\s*(?:al[- ]?)?yadayn\b",
        r"\bhands?\s+before\s+and\s+after\s+ruku\b",
        r"\braising\s+hands?\b",
        r"\bwhere\s+to\s+place\s+hands?\b",
        r"\bhands?\s+(?:be\s+)?placed\b",
        r"\bhands?\s+on\s+chest\b",
        r"\bhands?\s+below\s+navel\b",
        r"\b(?:below|under)\s+(?:the\s+)?navel\b",
        r"\b(?:on|upon)\s+(?:the\s+)?chest\b",
        r"\bsaying\s+amin\b",
        r"\bamin\b.*?\b(?:aloud|loudly|silently|quietly|softly)\b",
        r"\bqun[ou]+t\s+(?:in\s+)?fajr\b",
        r"\bqun[ou]+t\b.*?\bfajr\b",
        r"\b(?:fatihah|fatiha)\b.*?\b(?:behind|khalf)\b.*?\b(?:the\s+)?imam\b",
        r"\bwad'?\s*al-?yadayn\b",
        r"\bsadl\s+vs\s+qabd\b",
    ]
    return any(re.search(pat, q) for pat in procedural_indicators)


def format_fiqh_grounding_block(topic: Dict[str, Any]) -> str:
    """
    Format verified 4-Madhhab classical Fiqh context for prompt injection.
    """
    lines = [
        f"### ⚖️ Canonical Jurisprudence Reference: {topic['title']}",
        f"**Classical Consensus (Ijmāʿ) / Background:** {topic['classical_consensus']}",
        "",
        "**Scholarly Positions Across the 4 Sunni Madhhabs (Ikhtilāf):**",
    ]

    for school, data in topic["schools"].items():
        lines.append(f"- **{school} School:** {data['ruling']}")
        lines.append(f"  *Primary Evidences (Adillah):* {data['proofs']}")
        lines.append(f"  *Classical Reference Manuals:* {data['classical_references']}")

    lines.append("")
    lines.append(f"**Scholarly Etiquette (Adab al-Ikhtilāf):** {topic['adab_note']}")
    return "\n".join(lines)
