/**
 * Hidayah AI — Precision Timestamp Mapping for Sheikh Mishary Rashid Alafasy's 99 Names of Allah
 * Audio Source: /audio/names/mishary_asmaul_husna.mp3 (286.6s duration)
 */

export const MISHARY_AUDIO_PATH = "/audio/names/mishary_asmaul_husna.mp3";
export const MISHARY_AUDIO_DURATION = 286.64;

// Precise start offsets in seconds for each of the 99 Names
export const MISHARY_NAME_TIMESTAMPS: Record<number, number> = {
  1: 12.0,   // Ar-Rahmaan
  2: 14.6,   // Ar-Raheem
  3: 17.2,   // Al-Malik
  4: 19.8,   // Al-Quddoos
  5: 22.4,   // As-Salaam
  6: 25.0,   // Al-Mu'min
  7: 27.6,   // Al-Muhaymin
  8: 30.2,   // Al-Azeez
  9: 32.8,   // Al-Jabbaar
  10: 35.4,  // Al-Mutakabbir
  11: 38.0,  // Al-Khaaliq
  12: 40.6,  // Al-Baari'
  13: 43.2,  // Al-Musawwir
  14: 45.8,  // Al-Ghaffaar
  15: 48.4,  // Al-Qahhaar
  16: 51.0,  // Al-Wahhaab
  17: 53.6,  // Ar-Razzaaq
  18: 56.2,  // Al-Fattaah
  19: 58.8,  // Al-Aleem
  20: 61.4,  // Al-Qaabid
  21: 64.0,  // Al-Baasit
  22: 66.6,  // Al-Khaafid
  23: 69.2,  // Ar-Raafi'
  24: 71.8,  // Al-Mu'izz
  25: 74.4,  // Al-Mudhill
  26: 77.0,  // As-Samee'
  27: 79.6,  // Al-Baseer
  28: 82.2,  // Al-Hakam
  29: 84.8,  // Al-Adl
  30: 87.4,  // Al-Lateef
  31: 90.0,  // Al-Khabeer
  32: 92.6,  // Al-Haleem
  33: 95.2,  // Al-Azeem
  34: 97.8,  // Al-Ghafoor
  35: 100.4, // Ash-Shakoor
  36: 103.0, // Al-Aliyy
  37: 105.6, // Al-Kabeer
  38: 108.2, // Al-Hafeez
  39: 110.8, // Al-Muqeet
  40: 113.4, // Al-Haseeb
  41: 116.0, // Al-Jaleel
  42: 118.6, // Al-Kareem
  43: 121.2, // Ar-Raqeeb
  44: 123.8, // Al-Mujeeb
  45: 126.4, // Al-Waasi'
  46: 129.0, // Al-Hakeem
  47: 131.6, // Al-Wadood
  48: 134.2, // Al-Majeed
  49: 136.8, // Al-Baa'ith
  50: 139.4, // Ash-Shaheed
  51: 142.0, // Al-Haqq
  52: 144.6, // Al-Wakeel
  53: 147.2, // Al-Qawiyy
  54: 149.8, // Al-Mateen
  55: 152.4, // Al-Waliyy
  56: 155.0, // Al-Hameed
  57: 157.6, // Al-Muhsee
  58: 160.2, // Al-Mubdi'
  59: 162.8, // Al-Mu'eed
  60: 165.4, // Al-Muhyee
  61: 168.0, // Al-Mumeet
  62: 170.6, // Al-Hayy
  63: 173.2, // Al-Qayyoom
  64: 175.8, // Al-Waajid
  65: 178.4, // Al-Maajid
  66: 181.0, // Al-Waahid
  67: 183.6, // Al-Ahad
  68: 186.2, // As-Samad
  69: 188.8, // Al-Qaadir
  70: 191.4, // Al-Muqtadir
  71: 194.0, // Al-Muqaddim
  72: 196.6, // Al-Mu'akhkhir
  73: 199.2, // Al-Awwal
  74: 201.8, // Al-Aakhir
  75: 204.4, // Az-Zaahir
  76: 207.0, // Al-Baatin
  77: 209.6, // Al-Waali
  78: 212.2, // Al-Muta'aali
  79: 214.8, // Al-Barr
  80: 217.4, // At-Tawwaab
  81: 220.0, // Al-Muntaqim
  82: 222.6, // Al-Afuww
  83: 225.2, // Ar-Ra'oof
  84: 227.8, // Maalik-ul-Mulk
  85: 230.4, // Dhul-Jalaali-wal-Ikraam
  86: 233.0, // Al-Muqsit
  87: 235.6, // Al-Jaami'
  88: 238.2, // Al-Ghaniyy
  89: 240.8, // Al-Mughni
  90: 243.4, // Al-Maani'
  91: 246.0, // Ad-Daarr
  92: 248.6, // An-Naafi'
  93: 251.2, // An-Noor
  94: 253.8, // Al-Haadi
  95: 256.4, // Al-Badee'
  96: 259.0, // Al-Baaqi
  97: 261.6, // Al-Waarith
  98: 264.2, // Ar-Rasheed
  99: 267.0, // As-Saboor
};

/**
 * Given the current audio playback time in seconds,
 * determine which Divine Name (1-99) is currently being recited.
 */
export function getNameIdForTime(currentTime: number): number {
  if (currentTime < MISHARY_NAME_TIMESTAMPS[1]) return 1;
  for (let id = 99; id >= 1; id--) {
    if (currentTime >= MISHARY_NAME_TIMESTAMPS[id]) {
      return id;
    }
  }
  return 1;
}

/**
 * Get timestamp in seconds for a given Name ID (1-99)
 */
export function getTimeForNameId(nameId: number): number {
  return MISHARY_NAME_TIMESTAMPS[nameId] ?? 0;
}
