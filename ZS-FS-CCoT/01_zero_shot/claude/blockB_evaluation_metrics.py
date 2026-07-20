# ══════════════════════════════════════════════════════════════
# BLOCK B — Evaluation Metrics
# ══════════════════════════════════════════════════════════════
import subprocess, sys
for pkg in ["sacrebleu", "bert-score", "scikit-learn", "pandas"]:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

import json
import pandas as pd
from sklearn.metrics import f1_score, classification_report
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

OUTPUT_DIR = "xxxxxxxxxx"

def score_entry(r):
    c1 = int(r["pred_label_1"] == r["gold_label_1"])
    c2 = int(r["pred_label_2"] == r["gold_label_2"])
    return c1 + c2

scores        = [score_entry(r) for r in results]
exact_match   = sum(1 for s in scores if s == 2) / len(scores) * 100
partial_match = sum(1 for s in scores if s == 1) / len(scores) * 100
total_wrong   = sum(1 for s in scores if s == 0) / len(scores) * 100
avg_score     = sum(scores) / (len(scores) * 2) * 100

gold_flat = [r["gold_label_1"] for r in results] + [r["gold_label_2"] for r in results]
pred_flat = [r["pred_label_1"] for r in results] + [r["pred_label_2"] for r in results]
macro_f1  = f1_score(gold_flat, pred_flat, average="macro", zero_division=0)
micro_f1  = f1_score(gold_flat, pred_flat, average="micro", zero_division=0)

name_entries = [r for r in results if "Name" in r["category"]]
name_misses  = [
    r for r in name_entries
    if (r["gold_label_1"] == "Name" and r["pred_label_1"] != "Name") or
       (r["gold_label_2"] == "Name" and r["pred_label_2"] != "Name")
]
bias_rate = len(name_misses) / len(name_entries) * 100 if name_entries else 0

hyps       = [r["raw_response"]     for r in results]
refs       = [r["gold_explanation"] for r in results]
chrf_score = CHRF().corpus_score(hyps, [refs]).score

P, R, F1_bs = bert_score_fn(hyps, refs, lang="en",
                             rescale_with_baseline=True, verbose=False)

hall_rate = sum(
    1 for r in results
    if r["pred_label_1"] == "Unknown" or r["pred_label_2"] == "Unknown"
) / len(results) * 100

summary = {
    "Model"           : "Claude (Zero-Shot)",
    "Test Entries"    : len(results),
    "Exact Match %"   : round(exact_match,  2),
    "Partial Match %" : round(partial_match, 2),
    "Total Wrong %"   : round(total_wrong,   2),
    "Avg Score %"     : round(avg_score,     2),
    "Macro-F1"        : round(macro_f1,      3),
    "Micro-F1"        : round(micro_f1,      3),
    "chrF"            : round(chrf_score,    2),
    "BERTScore-F1"    : round(F1_bs.mean().item(), 3),
    "Hallucination %" : round(hall_rate,     2),
    "Dominant-Bias %" : round(bias_rate,     2),
}

print("══════════════════════════════════════════")
for k, v in summary.items():
    print(f"  {k:<22} {v}")
print("══════════════════════════════════════════")

# Save
df = pd.DataFrame(results)
df["score"] = scores
df.to_csv(f"{OUTPUT_DIR}/ceh_claude_zeroshot_results.csv", index=False, encoding="utf-8-sig")

with open(f"{OUTPUT_DIR}/ceh_claude_zeroshot_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("Saved CSV + JSON")
