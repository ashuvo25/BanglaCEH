# ══════════════════════════════════════════════════════════════
# BLOCK 5 — Split Dataset
# ══════════════════════════════════════════════════════════════
import json, random
from sklearn.model_selection import train_test_split

OUTPUT_DIR = "xxxxxxxxxx"

random.seed(42)

# 10% test
train_val, test_set = train_test_split(
    processed, test_size=0.15, random_state=42
)

# 15% val from remaining
val_ratio = 0.10 / 0.90
train_set, val_set = train_test_split(
    train_val, test_size=val_ratio, random_state=42
)

print(f"Train : {len(train_set)}  ({len(train_set)/len(processed)*100:.1f}%)")
print(f"Val   : {len(val_set)}   ({len(val_set)/len(processed)*100:.1f}%)")
print(f"Test  : {len(test_set)}  ({len(test_set)/len(processed)*100:.1f}%)")

# Save splits
for name, split in [("train", train_set), ("val", val_set), ("test", test_set)]:
    with open(f"{OUTPUT_DIR}/ceh_{name}.json", "w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)

print("Splits saved")
