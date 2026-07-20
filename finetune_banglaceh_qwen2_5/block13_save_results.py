# ══════════════════════════════════════════════════════════════
# BLOCK 13 — Save results
# ══════════════════════════════════════════════════════════════
import json
import pandas as pd

RESULTS_OUTPUT_DIR = "xxxxxxxxxx"

pd.DataFrame(results).to_csv(f"{RESULTS_OUTPUT_DIR}/ceh_qlora_{MODEL_TAG}.csv",
    index=False, encoding="utf-8-sig")
json.dump(summary, open(f"{RESULTS_OUTPUT_DIR}/ceh_qlora_summary_{MODEL_TAG}.json", "w"),
    ensure_ascii=False, indent=2)
print("saved csv + summary + adapter")
