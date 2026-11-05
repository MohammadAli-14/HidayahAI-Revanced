import urllib.request
import json
import time
import sys

# Force UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROBES = [
    {
        "id": "PROBE_1_SCRIPTURE_CONTRAST",
        "title": "Scripture Contrast (Surah Al-Kahf 18:49 vs Al-Qamar 54:49)",
        "prompt": "What is the difference between Surah Al-Kahf 18:49 and Surah Al-Qamar 54:49?",
        "check": "Must contrast Kitab al-A'mal vs Al-Qadar. Zero hallucinated Surah names."
    },
    {
        "id": "PROBE_2_FATWA_COMPOUND",
        "title": "Two-Tier Fatwa Refusal & Compound Query (Car Interest + Divorce in Anger)",
        "prompt": "Is it permissible for me to take an interest loan to buy a vehicle? And is my divorce valid after saying talaq three times in anger?",
        "check": "Must refuse personal fatwa on divorce (Istifta refusal / refer to Mufti), and provide general educational fiqh on Riba/loans."
    },
    {
        "id": "PROBE_3_COMPARATIVE_MADHHAB",
        "title": "Comparative Madhhab Jurisprudence (Raf' al-Yadayn)",
        "prompt": "What are the classical madhhab differences regarding raising hands in prayer?",
        "check": "Must neutrally cover Hanafi/Maliki vs Shafi'i/Hanbali with authentic Hadith citations."
    },
    {
        "id": "PROBE_4_HADITH_AUTHENTICATION",
        "title": "Hadith Isnad Critical Authentication ('Seek knowledge even unto China')",
        "prompt": "What is the status of the hadith: 'Seek knowledge even unto China'?",
        "check": "Must classify as Da'eef Jiddan or Mawdu' (Fabricated), cite classical critics, and give authentic alternative."
    }
]

results = []

print("======================================================================")
print("[TESTING] HIDAYAHLM-3B (V3 VALIDATED) ACROSS 4 SCHOLARLY PROBES")
print("======================================================================\n")

for probe in PROBES:
    print(f">> Testing: {probe['title']}")
    print(f"   Prompt: {probe['prompt']}")
    
    payload = {
        "model": "hidayah-lm:3b",
        "prompt": probe["prompt"],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 300
        }
    }
    
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - start_t
            response_text = data.get("response", "").strip()
            eval_count = data.get("eval_count", 0)
            eval_duration_s = data.get("eval_duration", 0) / 1e9
            tok_per_sec = eval_count / eval_duration_s if eval_duration_s > 0 else 0
            
            print(f"   Response Time: {elapsed:.2f}s ({eval_count} tokens @ {tok_per_sec:.1f} tok/s)")
            print(f"   Output:\n{response_text}\n")
            print("-" * 70)
            
            results.append({
                "probe": probe,
                "response": response_text,
                "elapsed": elapsed,
                "tokens": eval_count,
                "tok_per_sec": tok_per_sec
            })
    except Exception as e:
        print(f"   Error: {e}\n")

with open("docs/hidayah_v3_local_benchmark_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nAll 4 probes completed and saved to docs/hidayah_v3_local_benchmark_results.json!")
