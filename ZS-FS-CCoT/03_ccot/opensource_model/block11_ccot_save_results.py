# ══════════════════════════════════════════════════════════════
# BLOCK 11 — Save Results
# ══════════════════════════════════════════════════════════════
import json
import pandas as pd

OUTPUT_DIR = "xxxxxxxxxx"

model_tag = MODEL_PATH.split("/")[-1].replace(".", "-")

df = pd.DataFrame(results)
df["score"] = scores
df.to_csv(f"{OUTPUT_DIR}/ceh_ccot_{model_tag}.csv",
          index=False, encoding="utf-8-sig")

summary = {
    "Model"           : MODEL_PATH,
    "Method"          : "C-CoT",
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
with open(f"{OUTPUT_DIR}/ceh_ccot_summary_{model_tag}.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("Saved:")
print(f"   {OUTPUT_DIR}/ceh_ccot_{model_tag}.csv")
print(f"   {OUTPUT_DIR}/ceh_ccot_summary_{model_tag}.json")
