# ══════════════════════════════════════════════════════════════
# BLOCK 12 — Full metric suite (reasoning scored vs full_explanation_english)
# ══════════════════════════════════════════════════════════════
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

def sc(r):
    return int(r["pred_label_1"] == r["gold_label_1"]) + int(r["pred_label_2"] == r["gold_label_2"])

scores = [sc(r) for r in results]; n = len(scores)
exact = sum(s == 2 for s in scores) / n * 100
partial = sum(s == 1 for s in scores) / n * 100
wrong = sum(s == 0 for s in scores) / n * 100
avg = sum(scores) / (n * 2) * 100

gold = [r["gold_label_1"] for r in results] + [r["gold_label_2"] for r in results]
pred = [r["pred_label_1"] for r in results] + [r["pred_label_2"] for r in results]
macro = f1_score(gold, pred, average="macro", zero_division=0)
micro = f1_score(gold, pred, average="micro", zero_division=0)

# Dominant-Bias: Name-gold entries where model missed the Name label
name_e = [r for r in results if r["gold_label_1"] == "Name" or r["gold_label_2"] == "Name"]
name_miss = [r for r in name_e if (r["gold_label_1"] == "Name" and r["pred_label_1"] != "Name")
             or (r["gold_label_2"] == "Name" and r["pred_label_2"] != "Name")]
bias = len(name_miss) / len(name_e) * 100 if name_e else 0

# chrF + BERTScore: GENERATED reasoning vs GOLD english explanation
hyps = [r["gen_reasoning"] for r in results]
refs = [r["kd_target"] for r in results]
chrf = CHRF().corpus_score(hyps, [refs]).score
_, _, F1bs = bert_score_fn(hyps, refs, lang="en", rescale_with_baseline=True, verbose=False)
bert = F1bs.mean().item()

hall = len([r for r in results if r["pred_label_1"] == "Unknown" or r["pred_label_2"] == "Unknown"]) / n * 100

assert abs(exact + partial + wrong - 100) < 0.5
assert abs((exact * 2 + partial) / 2 - avg) < 0.5

summary = {"Model": MODEL_TAG, "Method": "QLoRA-KD",
 "Exact Match %": round(exact, 2), "Partial Match %": round(partial, 2),
 "Total Wrong %": round(wrong, 2), "Avg Score %": round(avg, 2),
 "Macro-F1": round(macro, 3), "Micro-F1": round(micro, 3),
 "chrF": round(chrf, 2), "BERTScore-F1": round(bert, 3),
 "Hallucination %": round(hall, 2), "Dominant-Bias %": round(bias, 2)}
print("=" * 50)
for k, v in summary.items():
    print(f"  {k:<18}: {v}")
print("=" * 50, "\nconsistency passed")
print(classification_report(gold, pred, zero_division=0))
