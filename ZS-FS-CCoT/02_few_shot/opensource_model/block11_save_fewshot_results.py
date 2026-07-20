# ══════════════════════════════════════════════════════════════
# BLOCK 11 — Save Few-Shot Results
# ══════════════════════════════════════════════════════════════
import json
import pandas as pd

OUTPUT_DIR = "xxxxxxxxxx"

summary = {
    "Model"            : MODEL_PATH,
    "Test Entries"     : len(results_fewshot),
    "Exact Match %"    : round(exact_match,  2),
    "Partial Match %"  : round(partial_match, 2),
    "Total Wrong %"    : round(total_wrong,   2),
    "Avg Score %"      : round(avg_score,     2),
    "Macro-F1"         : round(macro_f1,      3),
    "Micro-F1"         : round(micro_f1,      3),
    "chrF"             : round(chrf_score,    2),
    "BERTScore-F1"     : round(F1_bs.mean().item(), 3),
    "Hallucination %"  : round(hall_rate,     2),
    "Dominant-Bias %"  : round(bias_rate,     2),
}

# Save CSV
df_few = pd.DataFrame(results_fewshot)
df_few["score"] = [score_entry(r) for r in results_fewshot]
df_few.to_csv(f"{OUTPUT_DIR}/ceh_fewshot_results.csv",
              index=False, encoding="utf-8-sig")

# Save JSON
with open(f"{OUTPUT_DIR}/ceh_fewshot_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("Saved:")
print(f"   {OUTPUT_DIR}/ceh_fewshot_results.csv")
print(f"   {OUTPUT_DIR}/ceh_fewshot_summary.json")

print("\n══════════════════════════════════════════")
print("  FINAL SUMMARY — 3-Shot Results")
print("══════════════════════════════════════════")
for k, v in summary.items():
    print(f"  {k:<22} {v}")
print("══════════════════════════════════════════")
