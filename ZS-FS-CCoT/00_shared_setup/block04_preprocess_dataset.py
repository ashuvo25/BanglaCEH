# ══════════════════════════════════════════════════════════════
# BLOCK 4 — Preprocess Dataset
# ══════════════════════════════════════════════════════════════

def preprocess(entry):
    return {
        "id"               : entry["id"],
        "word_bangla"      : entry["word_bangla"],
        "word_roman"       : entry["word_roman"],
        "category"         : entry["category"],
        "narrative_bangla" : entry["input"]["narrative_bangla"],
        "gold_label_1"     : entry["token_labels"]["token_1"],
        "gold_label_2"     : entry["token_labels"]["token_2"],
        "gold_explanation" : entry["target_output"]["full_explanation_english"],
    }

processed = [preprocess(e) for e in raw_data]

# Sanity check
p = processed[0]
print(f"Word     : {p['word_bangla']} ({p['word_roman']})")
print(f"Category : {p['category']}")
print(f"Narrative: {p['narrative_bangla']}")
print(f"Labels   : {p['gold_label_1']} | {p['gold_label_2']}")
print(f"Preprocessed {len(processed)} entries")
