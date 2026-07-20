# ══════════════════════════════════════════════════════════════
# BLOCK 10 — Evaluation Metrics
# ══════════════════════════════════════════════════════════════
import pandas as pd
from sklearn.metrics import f1_score, classification_report
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

# ── Exact / Partial Match ─────────────────────────────
def score_entry(r):
    c1 = int(r["pred_label_1"] == r["gold_label_1"])
    c2 = int(r["pred_label_2"] == r["gold_label_2"])
    return c1 + c2

scores        = [score_entry(r) for r in results]
exact_match   = sum(1 for s in scores if s == 2) / len(scores) * 100
partial_match = sum(1 for s in scores if s == 1) / len(scores) * 100
total_wrong   = sum(1 for s in scores if s == 0) / len(scores) * 100
avg_score     = sum(scores) / (len(scores) * 2) * 100

# ── Label F1 ──────────────────────────────────────────
gold_flat = [r["gold_label_1"] for r in results] + [r["gold_label_2"] for r in results]
pred_flat = [r["pred_label_1"] for r in results] + [r["pred_label_2"] for r in results]
macro_f1  = f1_score(gold_flat, pred_flat, average="macro", zero_division=0)
micro_f1  = f1_score(gold_flat, pred_flat, average="micro", zero_division=0)

# ── Dominant-Meaning Bias ─────────────────────────────
name_entries = [r for r in results if "Name" in r["category"]]
name_misses  = [
    r for r in name_entries
    if (r["gold_label_1"] == "Name" and r["pred_label_1"] != "Name") or
       (r["gold_label_2"] == "Name" and r["pred_label_2"] != "Name")
]
bias_rate = len(name_misses) / len(name_entries) * 100 if name_entries else 0

# ── chrF ──────────────────────────────────────────────
chrf       = CHRF()
hyps       = [r["raw_response"]     for r in results]
refs       = [r["gold_explanation"] for r in results]
chrf_score = chrf.corpus_score(hyps, [refs]).score

# ── BERTScore ─────────────────────────────────────────
P, R, F1_bs = bert_score_fn(hyps, refs, lang="en",
                             rescale_with_baseline=True, verbose=False)

# ── Hallucination Rate ────────────────────────────────
hallucinated = [r for r in results
                if r["pred_label_1"] == "Unknown" or r["pred_label_2"] == "Unknown"]
hall_rate = len(hallucinated) / len(results) * 100

# ── Per-Category Accuracy ─────────────────────────────
cat_df = pd.DataFrame(results)
cat_df["score"] = scores
cat_summary = (cat_df.groupby("category")["score"]
               .agg(["mean","count"]))
cat_summary["mean"] = (cat_summary["mean"] / 2 * 100).round(1)
cat_summary.columns = ["Avg Score %", "Count"]

# ── Print All ─────────────────────────────────────────
print("══════════════════════════════════════════════")
print(f"  RESULTS — {MODEL_PATH}   Zero-Shot")
print("══════════════════════════════════════════════")
print(f"  Exact Match        : {exact_match:.1f}%")
print(f"  Partial Match      : {partial_match:.1f}%")
print(f"  Total Wrong        : {total_wrong:.1f}%")
print(f"  Avg Score          : {avg_score:.1f}%")
print(f"  Macro-F1           : {macro_f1:.3f}")
print(f"  Micro-F1           : {micro_f1:.3f}")
print(f"  chrF               : {chrf_score:.2f}")
print(f"  BERTScore-F1       : {F1_bs.mean().item():.3f}")
print(f"  Hallucination %    : {hall_rate:.1f}%")
print(f"  Dominant-Bias %    : {bias_rate:.1f}%")
print(f"\n── Per-Category ───────────────────────────────")
print(cat_summary.to_string())
print(f"\n── Label Classification Report ────────────────")
print(classification_report(gold_flat, pred_flat, zero_division=0))
