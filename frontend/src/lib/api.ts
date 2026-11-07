/**
 * Hidayah AI — Frontend API Client
 * Connects to the local FastAPI Theological Gateway (Port 8001).
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001/api";
export const DIRECT_BACKEND_URL = "http://127.0.0.1:8001/api";

/**
 * Checks if the FastAPI Theological Gateway is healthy and reachable.
 */
export async function checkGatewayHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === "online";
  } catch {
    return false;
  }
}

export interface Ayah {
  number: number;
  number_in_surah: number;
  surah_number: number;
  surah_name: string;
  surah_english_name: string;
  surah_arabic_name?: string;
  arabic: string;
  english: string;
  urdu: string;
  audio_url: string;
  audio_en?: string;
  audio_ur?: string;
  page?: number;
  juz?: number;
}

export interface JuzMeta {
  id: number;
  name: string;
  arabic: string;
  english: string;
  surahs: string;
}

export interface SurahMeta {
  number: number;
  name: string;
  englishName: string;
  englishNameTranslation: string;
  numberOfAyahs: number;
}

export interface TafsirSource {
  source_id: string;
  source_name: string;
  surah_number: number;
  ayah_number: number;
  text: string;
  language: string;
  canonical_url?: string;
}

export interface AsbabData {
  has_specific_sabab: boolean;
  category: string;
  surah_number: number;
  ayah_number: number;
  title: string;
  period: string;
  authority: string;
  narrator?: string;
  arabic_summary?: string;
  circumstance: string;
  significance: string;
  reference: string;
}

export interface FiqhSchool {
  ruling: string;
  proofs: string;
  classical_references: string;
}

export interface FiqhMatrix {
  title: string;
  classical_consensus: string;
  schools: Record<string, FiqhSchool>;
  adab_note?: string;
}

export interface HadithGradingBadge {
  tier: "sahih" | "hasan" | "daif" | "mawdu" | "canonical";
  label: string;
  color: string;
}

export interface RelatedHadith {
  id?: string;
  source?: string;
  title?: string;
  source_name?: string;
  book?: string;
  hadith_no?: string;
  chapter?: string;
  grade?: string;
  grading_badge?: HadithGradingBadge;
  narrator?: string;
  text_arabic?: string;
  text_english?: string;
  text?: string;
  excerpt?: string;
  url?: string;
  canonical_url?: string;
}

export interface ScholarSource {
  type: string;
  source: string;
  label: string;
  canonical: string;
  url?: string;
}

export interface ScholarResponse {
  intent: string;
  answer: string;
  sources: ScholarSource[];
  fiqh_matrix?: FiqhMatrix | null;
  raw_response: string;
}

// Canonical Fallback 30 Juzs (Ensures zero-blank screen UI resilience)
export const DEFAULT_JUZ_LIST: JuzMeta[] = [
  { id: 1, name: "Alif Lam Mim", arabic: "الم", english: "Alif Lam Mim", surahs: "Al-Fatiha 1 – Al-Baqarah 141" },
  { id: 2, name: "Sayaqulu", arabic: "سيقول", english: "They will say", surahs: "Al-Baqarah 142 – Al-Baqarah 252" },
  { id: 3, name: "Tilka ar-Rusul", arabic: "تلك الرسل", english: "Those Messengers", surahs: "Al-Baqarah 253 – Al-Imran 92" },
  { id: 4, name: "Lan Tanalu", arabic: "لن تنالوا", english: "Never will you attain", surahs: "Al-Imran 93 – An-Nisa 23" },
  { id: 5, name: "Wal-Muhsanat", arabic: "والمحصنات", english: "And forbidden to you are", surahs: "An-Nisa 24 – An-Nisa 147" },
  { id: 6, name: "La Yuhibbu-llah", arabic: "لا يحب الله", english: "Allah does not like", surahs: "An-Nisa 148 – Al-Ma'idah 81" },
  { id: 7, name: "Wa Idha Sami'u", arabic: "وإذا سمعوا", english: "And when they hear", surahs: "Al-Ma'idah 82 – Al-An'am 110" },
  { id: 8, name: "Wa Lau Annana", arabic: "ولو أننا", english: "And even if We had", surahs: "Al-An'am 111 – Al-A'raf 87" },
  { id: 9, name: "Qal al-Mala'", arabic: "قال الملأ", english: "Said the eminent ones", surahs: "Al-A'raf 88 – Al-Anfal 40" },
  { id: 10, name: "Wa A'lamu", arabic: "واعلموا", english: "And know that", surahs: "Al-Anfal 41 – At-Tawbah 92" },
  { id: 11, name: "Ya'tadhiruna", arabic: "يعتذرون", english: "They will make excuses", surahs: "At-Tawbah 93 – Hud 5" },
  { id: 12, name: "Wa Ma Min Dabbah", arabic: "وما من دابة", english: "And there is no creature", surahs: "Hud 6 – Yusuf 52" },
  { id: 13, name: "Wa Ma Ubarri'u", arabic: "وما أبرئ", english: "And I do not acquit", surahs: "Yusuf 53 – Ibrahim 52" },
  { id: 14, name: "Rubama", arabic: "ربما", english: "Perhaps", surahs: "Al-Hijr 1 – An-Nahl 128" },
  { id: 15, name: "Subhan-alladhi", arabic: "سبحان الذي", english: "Exalted is He who", surahs: "Al-Isra 1 – Al-Kahf 74" },
  { id: 16, name: "Qal Alam", arabic: "قال ألم", english: "Said: Did I not", surahs: "Al-Kahf 75 – Ta-Ha 135" },
  { id: 17, name: "Iqtaraba", arabic: "اقترب", english: "Has drawn near", surahs: "Al-Anbiya 1 – Al-Hajj 78" },
  { id: 18, name: "Qad Aflaha", arabic: "قد أفلح", english: "Certainly have succeeded", surahs: "Al-Mu'minun 1 – Al-Furqan 20" },
  { id: 19, name: "Wa Qal-alladhina", arabic: "وقال الذين", english: "And said those who", surahs: "Al-Furqan 21 – An-Naml 55" },
  { id: 20, name: "A'man Khalaqa", arabic: "أمن خلق", english: "Or, who created", surahs: "An-Naml 56 – Al-Ankabut 45" },
  { id: 21, name: "Utlu Ma Uhiya", arabic: "اتل ما أوحي", english: "Recite what has been", surahs: "Al-Ankabut 46 – Al-Ahzab 30" },
  { id: 22, name: "Wa Man Yaqnut", arabic: "ومن يقنت", english: "And whoever is obedient", surahs: "Al-Ahzab 31 – Ya-Sin 27" },
  { id: 23, name: "Wa Mali", arabic: "ومالي", english: "And what is it for me", surahs: "Ya-Sin 28 – Az-Zumar 31" },
  { id: 24, name: "Fa Man Azlamu", arabic: "فمن أظلم", english: "So who is more unjust", surahs: "Az-Zumar 32 – Fussilat 46" },
  { id: 25, name: "Ilayhi Yuraddu", arabic: "إليه يرد", english: "To Him is referred", surahs: "Fussilat 47 – Al-Jathiyah 37" },
  { id: 26, name: "Ha Mim", arabic: "حم", english: "Ha Mim", surahs: "Al-Ahqaf 1 – Adh-Dhariyat 30" },
  { id: 27, name: "Qala Fa-ma Khatbukum", arabic: "قال فما خطبكم", english: "Said: Then what is your", surahs: "Adh-Dhariyat 31 – Al-Hadid 29" },
  { id: 28, name: "Qad Sami Allahu", arabic: "قد سمع الله", english: "Certainly has Allah heard", surahs: "Al-Mujadila 1 – At-Tahrim 12" },
  { id: 29, name: "Tabaraka-lladhi", arabic: "تبارك الذي", english: "Blessed is He who", surahs: "Al-Mulk 1 – Al-Mursalat 50" },
  { id: 30, name: "Amma Yatasa'alun", arabic: "عم يتساءلون", english: "About what are they asking", surahs: "An-Naba 1 – An-Nas 6" },
];

// Canonical 114 Surah to Starting Juz Mapping
export const SURAH_STARTING_JUZ: Record<number, number> = {
  1: 1, 2: 1, 3: 3, 4: 4, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11,
  11: 11, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 16, 20: 16,
  21: 17, 22: 17, 23: 18, 24: 18, 25: 18, 26: 19, 27: 19, 28: 20, 29: 20, 30: 21,
  31: 21, 32: 21, 33: 21, 34: 22, 35: 22, 36: 22, 37: 23, 38: 23, 39: 23, 40: 24,
  41: 24, 42: 25, 43: 25, 44: 25, 45: 25, 46: 26, 47: 26, 48: 26, 49: 26, 50: 26,
  51: 26, 52: 27, 53: 27, 54: 27, 55: 27, 56: 27, 57: 27, 58: 28, 59: 28, 60: 28,
  61: 28, 62: 28, 63: 28, 64: 28, 65: 28, 66: 28, 67: 29, 68: 29, 69: 29, 70: 29,
  71: 29, 72: 29, 73: 29, 74: 29, 75: 29, 76: 29, 77: 29, 78: 30, 79: 30, 80: 30,
  81: 30, 82: 30, 83: 30, 84: 30, 85: 30, 86: 30, 87: 30, 88: 30, 89: 30, 90: 30,
  91: 30, 92: 30, 93: 30, 94: 30, 95: 30, 96: 30, 97: 30, 98: 30, 99: 30, 100: 30,
  101: 30, 102: 30, 103: 30, 104: 30, 105: 30, 106: 30, 107: 30, 108: 30, 109: 30, 110: 30,
  111: 30, 112: 30, 113: 30, 114: 30,
};

// Resilient HTTP fetcher with single micro-retry to absorb cold-start gateway initialization
async function fetchWithRetry(url: string, options?: RequestInit, retries = 1, delayMs = 350): Promise<Response> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, options);
      if (res.ok) return res;
      // If gateway returned 502/503/504 or temporary connection error, retry once
      if (attempt < retries && (res.status >= 500 || res.status === 404)) {
        await new Promise((r) => setTimeout(r, delayMs));
        continue;
      }
      return res;
    } catch (err) {
      lastError = err;
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, delayMs));
      }
    }
  }
  throw lastError || new Error(`Network request failed for ${url}`);
}

export async function fetchJuzList(): Promise<JuzMeta[]> {
  try {
    const res = await fetchWithRetry(`${API_BASE}/quran/juz-list`);
    if (!res.ok) throw new Error("Failed to fetch Juz list from gateway");
    const data = await res.json();
    return (data.juzs && data.juzs.length > 0) ? data.juzs : DEFAULT_JUZ_LIST;
  } catch (err) {
    console.warn("fetchJuzList fallback active:", err);
    return DEFAULT_JUZ_LIST;
  }
}

// In-memory Client Cache for instant (0ms) Juz transitions
const CLIENT_JUZ_CACHE = new Map<number, { ayahs: Ayah[]; name: string; arabic: string }>();

export async function fetchJuzAyahs(juzId: number): Promise<{ ayahs: Ayah[]; name: string; arabic: string }> {
  if (CLIENT_JUZ_CACHE.has(juzId)) {
    return CLIENT_JUZ_CACHE.get(juzId)!;
  }

  try {
    const res = await fetchWithRetry(`${API_BASE}/quran/juz/${juzId}`);
    if (!res.ok) throw new Error(`Failed to fetch Juz ${juzId}`);
    const data = await res.json();
    const result = {
      ayahs: data.ayahs || [],
      name: data.name || `Juz ${juzId}`,
      arabic: data.arabic || "",
    };

    if (result.ayahs.length > 0) {
      CLIENT_JUZ_CACHE.set(juzId, result);
    }
    return result;
  } catch (err) {
    console.warn(`fetchJuzAyahs(${juzId}) fallback:`, err);
    const fallbackMeta = DEFAULT_JUZ_LIST[juzId - 1] || { name: `Juz ${juzId}`, arabic: "" };
    return { ayahs: [], name: fallbackMeta.name, arabic: fallbackMeta.arabic };
  }
}

export async function fetchSurahs(): Promise<SurahMeta[]> {
  try {
    const res = await fetchWithRetry(`${API_BASE}/quran/surahs`);
    if (!res.ok) throw new Error("Failed to fetch surahs");
    const data = await res.json();
    return data.surahs || [];
  } catch (err) {
    console.warn("fetchSurahs warning:", err);
    return [];
  }
}

export async function fetchTafsir(surahNum: number, ayahNum: number, lang: string = "en"): Promise<TafsirSource[]> {
  try {
    const res = await fetch(`${API_BASE}/tafsir/${surahNum}/${ayahNum}?lang=${lang}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.sources || [];
  } catch (err) {
    console.warn("fetchTafsir warning:", err);
    return [];
  }
}

export async function fetchRelatedHadith(surahName: string, ayahNum: number, text: string = ""): Promise<RelatedHadith[]> {
  try {
    const params = new URLSearchParams({
      surah_name: surahName,
      ayah_number: ayahNum.toString(),
      ayah_text: text.slice(0, 100),
    });
    const res = await fetch(`${API_BASE}/hadith/related?${params.toString()}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || [];
  } catch (err) {
    console.warn("fetchRelatedHadith warning:", err);
    return [];
  }
}

export async function fetchAsbabAlNuzul(surahNum: number, ayahNum: number): Promise<AsbabData | null> {
  try {
    const res = await fetch(`${API_BASE}/tafsir/asbab/${surahNum}/${ayahNum}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn("fetchAsbabAlNuzul error:", err);
    return null;
  }
}

export async function fetchFiqhMatrix(query: string): Promise<FiqhMatrix | null> {
  try {
    const res = await fetch(`${API_BASE}/scholar/fiqh-matrix?query=${encodeURIComponent(query)}`);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.matched) {
      return {
        title: data.title,
        classical_consensus: data.classical_consensus,
        schools: data.schools,
        adab_note: data.adab_note,
      };
    }
    return null;
  } catch (err) {
    console.warn("fetchFiqhMatrix error:", err);
    return null;
  }
}

export async function askScholarApi(query: string, activePdfName?: string): Promise<ScholarResponse> {
  const res = await fetch(`${API_BASE}/scholar/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, active_pdf_name: activePdfName }),
  });
  if (!res.ok) throw new Error("Scholar API request failed");
  return res.json();
}

// ── Names of Allah & Reciters ──

export interface QuranReference {
  surah: number;
  ayah: number;
  text: string;
  translation: string;
}

export interface NameOfAllah {
  id: number;
  number: number;
  name_ar: string;
  transliteration: string;
  meaning_en: string;
  meaning_ur: string;
  root_ar: string;
  category: string;
  category_ur: string;
  explanation_en: string;
  explanation_ur: string;
  quran_references: QuranReference[];
  audio_url: string;
  audio_fallback_url?: string;
  canonical_hadith_ref?: string;
}

export interface NameCategory {
  category_en: string;
  category_ur: string;
  count: number;
}

export interface ReciterInfo {
  id: string;
  name: string;
  name_ar: string;
  style: string;
  description: string;
  bitrate: string;
  audio_base: string;
}

export async function fetchNamesOfAllah(category?: string, search?: string): Promise<NameOfAllah[]> {
  try {
    const params = new URLSearchParams();
    if (category && category !== "All") params.set("category", category);
    if (search) params.set("search", search);
    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${API_BASE}/names-of-allah${qs}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.names || [];
  } catch (err) {
    console.warn("fetchNamesOfAllah error:", err);
    return [];
  }
}

export async function fetchNameCategories(): Promise<NameCategory[]> {
  try {
    const res = await fetch(`${API_BASE}/names-of-allah/categories`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.categories || [];
  } catch (err) {
    console.warn("fetchNameCategories error:", err);
    return [];
  }
}

export async function fetchNameById(nameId: number): Promise<{ name: NameOfAllah; navigation: { prev_id: number; next_id: number } } | null> {
  try {
    const res = await fetch(`${API_BASE}/names-of-allah/${nameId}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn(`fetchNameById(${nameId}) error:`, err);
    return null;
  }
}

export async function fetchNameScripture(nameId: number): Promise<{ name_id: number; name_ar: string; transliteration: string; quran_verses: QuranReference[]; hadith_citations: any[] } | null> {
  try {
    const res = await fetch(`${API_BASE}/names-of-allah/${nameId}/scripture`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn(`fetchNameScripture(${nameId}) error:`, err);
    return null;
  }
}

export async function fetchReciters(): Promise<ReciterInfo[]> {
  try {
    const res = await fetch(`${API_BASE}/quran/reciters`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.reciters || [];
  } catch (err) {
    console.warn("fetchReciters error:", err);
    return [];
  }
}

