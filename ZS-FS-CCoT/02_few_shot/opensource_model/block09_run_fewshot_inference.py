# ══════════════════════════════════════════════════════════════
# BLOCK 9 — Run Few-Shot Inference
# ══════════════════════════════════════════════════════════════
from tqdm import tqdm

results_fewshot = []

for entry in tqdm(test_set, desc="Few-Shot (3-shot)"):
    prompt         = build_fewshot_prompt(entry)   # ← only change from zero-shot
    response       = run_inference(prompt)
    pred_1, pred_2 = parse_response(response)

    results_fewshot.append({
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

print(f"Few-shot inference done on {len(results_fewshot)} entries")

# Quick peek
r = results_fewshot[0]
print(f"\nWord  : {r['word_bangla']}")
print(f"Gold  : {r['gold_label_1']} | {r['gold_label_2']}")
print(f"Pred  : {r['pred_label_1']} | {r['pred_label_2']}")
print(f"Output: {r['raw_response']}")
