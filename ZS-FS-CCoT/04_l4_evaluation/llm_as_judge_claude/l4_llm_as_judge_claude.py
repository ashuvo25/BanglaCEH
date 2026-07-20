# ══════════════════════════════════════════════════════════════
# L4 LLM-as-Judge (Claude) — matches JSON + CSV by ID
# ══════════════════════════════════════════════════════════════
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "anthropic"])

import json, time, re
import pandas as pd
import anthropic
from tqdm import tqdm

ANTHROPIC_API_KEY = "xxxxxxxxxx"
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
JUDGE_MODEL = "claude-haiku-4-5-20251001"

# ── PATH 1 — Main dataset JSON ───────────────────────────────
JSON_PATH = "xxxxxxxxxx"
with open(JSON_PATH, "r", encoding="utf-8") as f:
    main_data = json.load(f)
main_by_id = {d["id"]: d for d in main_data}

# ── PATH 2 — Zero/Few-shot results CSV ──────────────────────
CSV_PATH = "xxxxxxxxxx"   # ← change per model/setting
csv_df = pd.read_csv(CSV_PATH)

# ── Build judge prompt ───────────────────────────────────────
def build_judge_prompt(model_response, gold_explanation):
    return (
        "You are an expert evaluator of cultural linguistic reasoning about Bangla.\n\n"
        f"REFERENCE (expert explanation):\n{gold_explanation}\n\n"
        f"MODEL RESPONSE (to evaluate):\n{model_response}\n\n"
        "Rate the MODEL RESPONSE on a scale of 1-10 for how well it captures:\n"
        "1. Correct identification of why each occurrence has its meaning\n"
        "2. The cultural entanglement reasoning (WHY name and meaning are linked)\n\n"
        "Reply with ONLY a single integer from 1 to 10, nothing else."
    )

def run_judge(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            msg = client.messages.create(
                model=JUDGE_MODEL,
                max_tokens=10,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"  Retry {attempt+1} — {e}")
            time.sleep(3)
    return ""

def parse_score(response):
    m = re.search(r"\b([1-9]|10)\b", response)
    return int(m.group(1)) if m else None

# ── Match by ID, judge each entry ────────────────────────────
judge_results = []

for _, row in tqdm(csv_df.iterrows(), total=len(csv_df), desc="Claude Judge"):
    entry_id = int(row["id"])
    entry    = main_by_id.get(entry_id)

    if entry is None:
        print(f"  ID {entry_id} not found in JSON, skipping")
        continue

    gold_explanation = entry["target_output"]["full_explanation_english"]
    model_response   = row.get("model_response", row.get("raw_response", ""))

    prompt = build_judge_prompt(model_response, gold_explanation)
    response = run_judge(prompt)
    score = parse_score(response)

    judge_results.append({
        "id"               : entry_id,
        "word_bangla"      : entry["word_bangla"],
        "category"         : entry["category"],
        "gold_explanation" : gold_explanation,
        "model_response"   : model_response,
        "llm_judge_score"  : score,
    })

    time.sleep(1)

# ── Summary ───────────────────────────────────────────────────
valid_scores = [r["llm_judge_score"] for r in judge_results if r["llm_judge_score"] is not None]
avg_score    = sum(valid_scores) / len(valid_scores) if valid_scores else 0
failed       = sum(1 for r in judge_results if r["llm_judge_score"] is None)

output = {
    "model"            : "Llama-3.2-3B (Zero-Shot)",   # ← change per run
    "entries_scored"   : len(valid_scores),
    "total_entries"    : len(judge_results),
    "failed_parses"    : failed,
    "avg_judge_score"  : round(avg_score, 2),
    "results"          : judge_results,
}

with open("ceh_l4_judge_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n══════════════════════════════════════════")
print(f"  LLM-as-Judge (Claude) — Summary")
print("══════════════════════════════════════════")
print(f"  Entries scored      : {len(valid_scores)}/{len(judge_results)}")
print(f"  Avg Judge Score /10 : {avg_score:.2f}")
print(f"  Failed parses       : {failed}")
print("\nSaved: ceh_l4_judge_results.json")
