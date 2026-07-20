# ══════════════════════════════════════════════════════════════
# BLOCK 3 — Load Dataset
# ══════════════════════════════════════════════════════════════
import json

DATASET_PATH = "xxxxxxxxxx"

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} entries")
