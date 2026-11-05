"""
Hidayah AI — Quran Cache Pre-warmer
Pre-fetches and persists all 30 Juzs (Arabic, English, Urdu text and audio)
into data/quran_cache/juz_{1..30}.json for instantaneous (0ms) offline loading.
"""

import sys
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.quran_api import fetch_juz_combined, _DISK_CACHE_DIR

def prewarm_all_juzs(start: int = 1, end: int = 30):
    print(f"=== Hidayah AI Quran Cache Pre-warmer ===")
    print(f"Target Directory: {_DISK_CACHE_DIR}")
    print(f"Processing Juz {start} through {end}...\n")

    cached_count = 0
    fetched_count = 0
    failed_count = 0
    start_time = time.time()

    for juz_no in range(start, end + 1):
        cache_file = _DISK_CACHE_DIR / f"juz_{juz_no}.json"
        if cache_file.exists() and cache_file.stat().st_size > 1000:
            print(f"[CACHED] Juz {juz_no:2d} already present on disk ({cache_file.stat().st_size / 1024:.1f} KB).")
            cached_count += 1
            continue

        print(f"[FETCHING] Juz {juz_no:2d} from AlQuran.cloud (parallel multi-edition)...", end=" ", flush=True)
        t0 = time.time()
        try:
            ayahs = fetch_juz_combined(juz_no)
            dur = time.time() - t0
            if ayahs and len(ayahs) > 0:
                print(f"DONE in {dur:.2f}s ({len(ayahs)} ayahs saved).")
                fetched_count += 1
            else:
                print(f"WARNING: Empty result for Juz {juz_no}.")
                failed_count += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed_count += 1

        # Small pause to be polite to the AlQuran.cloud API
        time.sleep(0.2)

    total_time = time.time() - start_time
    print(f"\n=== Pre-warming Complete in {total_time:.1f}s ===")
    print(f"Already Cached: {cached_count} | Newly Fetched: {fetched_count} | Failed: {failed_count}")
    print(f"Total Cached Files in {_DISK_CACHE_DIR}: {len(list(_DISK_CACHE_DIR.glob('juz_*.json')))} / 30")

if __name__ == "__main__":
    prewarm_all_juzs()
