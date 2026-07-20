# ══════════════════════════════════════════════════════════════
# BLOCK 4 — Preprocess (labels from token_labels, reasoning from english)
# ══════════════════════════════════════════════════════════════
from collections import Counter

VALID_LABELS = {"Name", "Emotion", "Concept",
                "Spiritual", "Emotional State", "Collective State"}

def clean_reasoning(txt):
    # remove the stray " can " corruption seen in some entries
    txt = txt.replace("\n\n can ", "\n\n").replace(" can দ্বিতীয়", "দ্বিতীয়")
    return txt.strip()

def preprocess(e):
    tl = e["token_labels"]
    return {
        "id": e["id"],
        "word_bangla": e["word_bangla"],
        "word_roman": e["word_roman"],
        "category": e["category"],
        "narrative_bangla": e["input"]["narrative_bangla"],
        "gold_label_1": tl["token_1"].strip(),      # clean, direct — no parsing
        "gold_label_2": tl["token_2"].strip(),
        # gold reasoning the model learns to generate:
        "kd_target": clean_reasoning(e["target_output"]["full_explanation_english"]),
    }

processed = [preprocess(e) for e in raw_data]

# ── sanity: verify labels are all valid ──
bad = [p for p in processed if p["gold_label_1"] not in VALID_LABELS
       or p["gold_label_2"] not in VALID_LABELS]
print(f"entries with unexpected labels: {len(bad)}")
if bad:
    print("   examples:", [(b["gold_label_1"], b["gold_label_2"]) for b in bad[:5]])

c = Counter([p["gold_label_1"] for p in processed] + [p["gold_label_2"] for p in processed])
print("label distribution:", dict(c))

p = processed[0]
print("\nWord   :", p["word_bangla"], "| Labels:", p["gold_label_1"], "|", p["gold_label_2"])
print("KD head:", p["kd_target"][:150], "...")
print(f"preprocessed {len(processed)}")
