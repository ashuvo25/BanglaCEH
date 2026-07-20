# ══════════════════════════════════════════════════════════════
# BLOCK D — Evaluation (Few-Shot)
# ══════════════════════════════════════════════════════════════
import json
import pandas as pd
from sklearn.metrics import f1_score
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

OUTPUT_DIR = "xxxxxxxxxx"

scores        = [score_entry(r) for r in results_fewshot]
exact_match   = sum(1 for s in scores if s == 2) / len(scores) * 100
partial_match = sum(1 for s in scores if s == 1) / len(scores) * 100
total_wrong   = sum(1 for s in scores if s == 0) / len(scores) * 100
avg_score     = sum(scores) / (len(scores) * 2) * 100

gold_flat = [r["gold_label_1"] for r in results_fewshot] + [r["gold_label_2"] for r in results_fewshot]
pred_flat = [r["pred_label_1"] for r in results_fewshot] + [r["pred_label_2"] for r in results_fewshot]
macro_f1  = f1_score(gold_flat, pred_flat, average="macro", zero_division=0)
micro_f1  = f1_score(gold_flat, pred_flat, average="micro", zero_division=0)

name_entries = [r for r in results_fewshot if "Name" in r["category"]]
name_misses  = [
    r for r in name_entries
    if (r["gold_label_1"] == "Name" and r["pred_label_1"] != "Name") or
       (r["gold_label_2"] == "Name" and r["pred_label_2"] != "Name")
]
bias_rate = len(name_misses) / len(name_entries) * 100 if name_entries else 0

hyps       = [r["raw_response"]     for r in results_fewshot]
refs       = [r["gold_explanation"] for r in results_fewshot]
chrf_score = CHRF().corpus_score(hyps, [refs]).score

P, R, F1_bs = bert_score_fn(hyps, refs, lang="en",
                             rescale_with_baseline=True, verbose=False)

hall_rate = sum(
    1 for r in results_fewshot
    if r["pred_label_1"] == "Unknown" or r["pred_label_2"] == "Unknown"
) / len(results_fewshot) * 100

summary_fewshot = {
    "Model"           : "GPT-4o-mini (3-Shot)",
    "Test Entries"    : len(results_fewshot),
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
for k, v in summary_fewshot.items():
    print(f"  {k:<22} {v}")
print("══════════════════════════════════════════")

# Save
df = pd.DataFrame(results_fewshot)
df["score"] = scores
df.to_csv(f"{OUTPUT_DIR}/ceh_gpt4omini_fewshot_results.csv", index=False, encoding="utf-8-sig")

with open(f"{OUTPUT_DIR}/ceh_gpt4omini_fewshot_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary_fewshot, f, ensure_ascii=False, indent=2)

print("Saved CSV + JSON")
