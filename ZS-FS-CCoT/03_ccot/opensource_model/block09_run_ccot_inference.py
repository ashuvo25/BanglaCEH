# ══════════════════════════════════════════════════════════════
# BLOCK 9 — Run C-CoT Inference on TEST set
# ══════════════════════════════════════════════════════════════
from tqdm import tqdm

results = []
for entry in tqdm(test_set, desc="C-CoT"):
    prompt         = build_ccot_prompt(entry)
    response       = run_inference(prompt)
    pred_1, pred_2 = parse_ccot_response(response)
    results.append({
        "id"              : entry["id"],
        "word_bangla"     : entry["word_bangla"],
        "category"        : entry["category"],
        "narrative"       : entry["narrative_bangla"],
        "gold_label_1"    : entry["gold_label_1"],
        "gold_label_2"    : entry["gold_label_2"],
        "pred_label_1"    : pred_1,
        "pred_label_2"    : pred_2,
        "raw_response"    : response,
        "gold_explanation": entry["gold_explanation"],
    })

print(f"C-CoT inference done on {len(results)} entries")
r = results[0]
print(f"\nWord : {r['word_bangla']}")
print(f"Gold : {r['gold_label_1']} | {r['gold_label_2']}")
print(f"Pred : {r['pred_label_1']} | {r['pred_label_2']}")
print(f"Response (truncated):\n{r['raw_response'][:400]}...")
