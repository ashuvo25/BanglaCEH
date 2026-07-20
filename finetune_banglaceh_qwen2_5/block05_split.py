# ══════════════════════════════════════════════════════════════
# BLOCK 5 — Split  78% train / 10% val / 12% test
# ══════════════════════════════════════════════════════════════
import json
from sklearn.model_selection import train_test_split

OUTPUT_DIR = "xxxxxxxxxx"

train_val, test_set = train_test_split(processed, test_size=0.12, random_state=SEED)
val_ratio = 0.10 / 0.88
train_set, val_set = train_test_split(train_val, test_size=val_ratio, random_state=SEED)

print(f"Train: {len(train_set)} ({len(train_set)/len(processed)*100:.1f}%)")
print(f"Val  : {len(val_set)} ({len(val_set)/len(processed)*100:.1f}%)")
print(f"Test : {len(test_set)} ({len(test_set)/len(processed)*100:.1f}%)")

for nm, sp in [("train", train_set), ("val", val_set), ("test", test_set)]:
    json.dump(sp, open(f"{OUTPUT_DIR}/ceh_{nm}.json", "w"),
              ensure_ascii=False, indent=2)
print("splits saved")
