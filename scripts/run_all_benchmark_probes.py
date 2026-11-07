import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from agents.scholar import get_scholar_response, prepare_scholar_context

test_cases = [
    {
        "id": "Q1_EXEGESIS_CONTRAST",
        "query": "What is the difference between Surah al-Kahf 18:49 and Surah al-Qamar 54:49?",
        "intent": "SCHOLARLY_RESEARCH",
    },
    {
        "id": "Q2_TALAQ_ANGER",
        "query": "Is my divorce valid? I said talaq three times in extreme anger.",
        "intent": "SENSITIVE_FIQH",
    },
    {
        "id": "Q3_RIBA_CAR_LOAN",
        "query": "Is it permissible for me to take an interest loan to buy a vehicle?",
        "intent": "SENSITIVE_FIQH",
    },
    {
        "id": "Q4_GRADUAL_KHAMR",
        "query": "Explain the gradual prohibition of intoxicants across Surah 2:219, 4:43, and 5:90.",
        "intent": "SCHOLARLY_RESEARCH",
    },
    {
        "id": "Q5_ISRA_MIRAJ",
        "query": "What is the distinction between Al-Isra' in Surah 17:1 and Al-Mi'raj in Surah 53:1-18?",
        "intent": "SCHOLARLY_RESEARCH",
    },
]

for tc in test_cases:
    print(f"\n{'='*70}")
    print(f"TEST CASE: {tc['id']}")
    print(f"QUERY: {tc['query']}")
    print(f"INTENT: {tc['intent']}")
    print(f"{'='*70}\n")

    t0 = time.time()
    bundle = prepare_scholar_context(tc["query"], intent=tc["intent"], use_local_llm=True)
    t_ctx = time.time() - t0

    print(f"[Context Ready] in {t_ctx:.2f}s | Prompt Chars: {len(bundle.full_prompt)} | Sources: {len(bundle.grounded_sources)}")
    for s in bundle.grounded_sources[:4]:
        print(f"   • {s}")
    if len(bundle.grounded_sources) > 4:
        print(f"   ... and {len(bundle.grounded_sources)-4} more sources")

    t1 = time.time()
    resp = get_scholar_response(
        query=tc["query"],
        intent=tc["intent"],
        use_local_llm=True,
    )
    t_inf = time.time() - t1
    print(f"\n[Inference Completed] in {t_inf:.2f}s")
    print(f"\n--- MODEL RESPONSE ---\n{resp}\n----------------------")
