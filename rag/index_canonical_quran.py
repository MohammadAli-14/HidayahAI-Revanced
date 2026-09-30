"""
Hidayah AI — Quran Canonical Indexer
Fetches all 6,236 verses of the Holy Quran (Arabic Uthmani text, English Sahih International,
Urdu Jalandhry, Surah metadata, and Juz indices), generates embeddings, and indexes them
into LanceDB as 'canonical_quran' with a Tantivy BM25 Full-Text Search (FTS) index.
"""

import os
import sys
import time
from pathlib import Path
import requests
import numpy as np
import lancedb

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
DB_DIR = BASE_DIR / "data" / "lancedb"
DB_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("[+] HIDAYAH AI — QURAN CANONICAL VECTOR INDEXER")
print("=" * 70)

# 1. Fetch Complete Quran from Canonical API
print("\n[1/4] Fetching all 6,236 Quranic verses (Arabic, English, Urdu)...")

try:
    # Arabic Uthmani
    print("  -> Fetching Arabic Uthmani text...")
    r_ar = requests.get("https://api.alquran.cloud/v1/quran/quran-uthmani", timeout=30)
    r_ar.raise_for_status()
    ar_data = r_ar.json()["data"]["surahs"]

    # English (Sahih International)
    print("  -> Fetching English translation (Sahih International)...")
    r_en = requests.get("https://api.alquran.cloud/v1/quran/en.sahih", timeout=30)
    r_en.raise_for_status()
    en_data = r_en.json()["data"]["surahs"]

    # Urdu (Fateh Muhammad Jalandhry)
    print("  -> Fetching Urdu translation (Jalandhry)...")
    r_ur = requests.get("https://api.alquran.cloud/v1/quran/ur.jalandhry", timeout=30)
    r_ur.raise_for_status()
    ur_data = r_ur.json()["data"]["surahs"]

    print("  [+] Successfully fetched all Quranic editions from AlQuran.cloud API!")
except Exception as e:
    print(f"❌ Error fetching Quranic text: {e}")
    sys.exit(1)

# 2. Structure the 6,236 Ayahs into unified records
print("\n[2/4] Structuring 6,236 Quran Ayah records with metadata...")
records = []
total_ayah_count = 0

for s_idx in range(len(ar_data)):
    surah_ar = ar_data[s_idx]
    surah_en = en_data[s_idx]
    surah_ur = ur_data[s_idx]

    surah_num = surah_ar["number"]
    surah_name_en = surah_en["englishName"]
    surah_name_trans = surah_en["englishNameTranslation"]
    surah_name_ar = surah_ar["name"]
    revelation_type = surah_en.get("revelationType", "Meccan")

    for a_idx in range(len(surah_ar["ayahs"])):
        ayah_ar = surah_ar["ayahs"][a_idx]
        ayah_en = surah_en["ayahs"][a_idx]
        ayah_ur = surah_ur["ayahs"][a_idx]

        ayah_num_in_surah = ayah_ar["numberInSurah"]
        global_ayah_num = ayah_ar["number"]
        juz_num = ayah_ar.get("juz", 1)
        page_num = ayah_ar.get("page", 1)

        text_ar = ayah_ar["text"].strip()
        text_en = ayah_en["text"].strip()
        text_ur = ayah_ur["text"].strip()

        # Rich scholarly citation format
        full_text = (
            f"[Surah {surah_name_en} ({surah_num}:{ayah_num_in_surah}) — {surah_name_ar}]\n"
            f"Surah Meaning: {surah_name_trans} ({revelation_type})\n"
            f"Juz: {juz_num} | Page: {page_num}\n"
            f"Arabic: {text_ar}\n"
            f"English: {text_en}\n"
            f"Urdu: {text_ur}"
        )

        records.append({
            "id": f"ayah_{surah_num}_{ayah_num_in_surah}",
            "text": full_text.strip(),
            "surah_number": int(surah_num),
            "surah_name": str(surah_name_en),
            "surah_arabic_name": str(surah_name_ar),
            "ayah_number": int(ayah_num_in_surah),
            "global_ayah_number": int(global_ayah_num),
            "juz": int(juz_num),
            "page": int(page_num),
            "revelation_type": str(revelation_type),
        })
        total_ayah_count += 1

print(f"  [+] Prepared {len(records):,} Ayah records (Total: 6,236).")
print("\n--- SAMPLE AYAH 1 (Al-Fatihah 1:1) ---")
print(records[0]["text"])

# 3. Compute Embeddings
print(f"\n[3/4] Computing embeddings for {len(records)} verses...")
try:
    # Try local SentenceTransformer (BGE-M3 or MiniLM) or Gemini
    from sentence_transformers import SentenceTransformer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  -> Using SentenceTransformer on {device.upper()} (all-MiniLM-L6-v2 / BGE-M3)...")
    
    # Use fast high-precision multilingual embedder
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"  -> Loading {model_name}...")
    embedder = SentenceTransformer(model_name, device=device)
    
    texts = [r["text"] for r in records]
    batch_size = 32
    embeddings = []
    
    print("  -> Encoding 6,236 Ayahs...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeds = embedder.encode(batch, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
        embeddings.append(batch_embeds)
        if (i // batch_size) % 30 == 0:
            print(f"     Processed {min(i + batch_size, len(texts))}/{len(texts)} ayahs...")
            
    all_embeddings = np.vstack(embeddings)
    print(f"  [+] Embedding matrix shape: {all_embeddings.shape}")

except Exception as embed_err:
    print(f"  ⚠️ SentenceTransformer note: {embed_err}. Falling back to Gemini Embedding API...")
    from rag.vector_store import embed_texts
    texts = [r["text"] for r in records]
    all_embeddings = embed_texts(texts, task_type="retrieval_document")

# 4. Save to LanceDB table 'canonical_quran'
print("\n[4/4] Writing to LanceDB table 'canonical_quran'...")
db = lancedb.connect(str(DB_DIR))

lancedb_rows = []
for i, rec in enumerate(records):
    rec_copy = rec.copy()
    rec_copy["vector"] = all_embeddings[i].tolist() if isinstance(all_embeddings[i], np.ndarray) else all_embeddings[i]
    lancedb_rows.append(rec_copy)

table = db.create_table("canonical_quran", data=lancedb_rows, mode="overwrite")
print("  [+] Created table 'canonical_quran' with 6,236 records.")

print("  -> Building Tantivy BM25 Full-Text Search (FTS) index on 'text' column...")
table.create_fts_index("text", replace=True)
print("  [+] Tantivy BM25 index active!")

print("\n" + "=" * 70)
print("🎉 QURAN CANONICAL VECTOR INDEX COMPLETE! (6,236 AYAHS READY)")
print("=" * 70)
