# ══════════════════════════════════════════════════════════════
# BLOCK 3 — Load dataset (auto-repair version)
# ══════════════════════════════════════════════════════════════
import json, re

DATASET_PATH = "xxxxxxxxxx"

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    text = f.read()
try:
    raw_data = json.loads(text)
except json.JSONDecodeError:
    text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)   # fix bad escapes
    raw_data = json.loads(text)
print(f"loaded {len(raw_data)} entries")
print("keys:", list(raw_data[0].keys()))
