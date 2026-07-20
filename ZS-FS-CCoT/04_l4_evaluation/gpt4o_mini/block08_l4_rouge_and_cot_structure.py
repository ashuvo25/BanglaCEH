# ══════════════════════════════════════════════════════════════
# Extra L4 metrics — ROUGE-L + CoT structural features
# ══════════════════════════════════════════════════════════════
from rouge_score import rouge_scorer
import re

# Initialize ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)

# ── Programmatic CoT Metrics ──────────────────────────────────
def compute_cot_structure(hyp):
    # Count sequential steps based on line breaks, numbers, or bullet points
    steps = [line for line in hyp.split('\n') if line.strip()]

    # Also look for explicit reasoning markers
    markers = len(re.findall(r'\b(therefore|thus|hence|because|step|implies|consequently)\b', hyp.lower()))

    return len(steps), markers

# ── Inside your loop ──────────────────────────────────────────
for i, r in enumerate(l4_results):
    hyp = hyps[i]
    ref = refs[i]

    # Existing metrics
    r["chrF"] = round(chrf_metric.sentence_score(hyp, [ref]).score, 2)
    r["bertscore_f1"] = round(F1_bs[i].item(), 3)
    r["wer"] = round(safe_wer(hyp, ref), 3)
    r["label_mention_score"] = label_mention_score(r["model_response"], r["gold_label_1"], r["gold_label_2"])

    # ROUGE-L Recall/Precision/F1
    rouge_scores = scorer.score(ref, hyp)
    r["rougeL_f1"] = round(rouge_scores['rougeL'].fmeasure, 3)

    # CoT Structural features
    step_count, marker_count = compute_cot_structure(hyp)
    r["cot_step_count"] = step_count
    r["cot_marker_count"] = marker_count

# Summary averages
rougeL_avg = sum(r["rougeL_f1"] for r in l4_results) / len(l4_results)
avg_steps = sum(r["cot_step_count"] for r in l4_results) / len(l4_results)

print("rougeL_avg :", rougeL_avg)
print("avg_steps  :", avg_steps)
