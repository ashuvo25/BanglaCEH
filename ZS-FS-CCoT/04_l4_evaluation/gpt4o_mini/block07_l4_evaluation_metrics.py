# ══════════════════════════════════════════════════════════════
# BLOCK 7 — L4 Evaluation Metrics
# ══════════════════════════════════════════════════════════════
import json
import jiwer
import pandas as pd
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

OUTPUT_DIR = "xxxxxxxxxx"

hyps = [r["model_response"]    for r in l4_results]
refs = [r["gold_explanation"]  for r in l4_results]

# ── chrF ────────────────────────────────────────────────────
chrf_metric = CHRF()
chrf_corpus = chrf_metric.corpus_score(hyps, [refs]).score

# ── BERTScore ───────────────────────────────────────────────
P, R, F1_bs = bert_score_fn(hyps, refs, lang="en",
                             rescale_with_baseline=True, verbose=False)

# ── WER (Word Error Rate) ──────────────────────────────────
def safe_wer(hyp, ref):
    if not hyp.strip() or not ref.strip():
        return 1.0
    try:
        return jiwer.wer(ref, hyp)
    except Exception:
        return 1.0

# ── Label Mention Rate ──────────────────────────────────────
def label_mention_score(response, label_1, label_2):
    resp_lower = response.lower()
    m1 = label_1.lower() in resp_lower
    m2 = label_2.lower() in resp_lower
    return int(m1) + int(m2)

for i, r in enumerate(l4_results):
    r["chrF"]               = round(chrf_metric.sentence_score(hyps[i], [refs[i]]).score, 2)
    r["bertscore_f1"]        = round(F1_bs[i].item(), 3)
    r["wer"]                 = round(safe_wer(hyps[i], refs[i]), 3)
    r["label_mention_score"] = label_mention_score(r["model_response"], r["gold_label_1"], r["gold_label_2"])

label_mention_avg = sum(r["label_mention_score"] for r in l4_results) / (len(l4_results) * 2) * 100
wer_avg            = sum(r["wer"] for r in l4_results) / len(l4_results)

# ── Save ──────────────────────────────────────────────────────
df_l4 = pd.DataFrame(l4_results)
df_l4.to_csv(f"{OUTPUT_DIR}/ceh_l4_gpt4omini_results.csv", index=False, encoding="utf-8-sig")

summary_l4 = {
    "Model"              : "GPT-4o-mini (L4 Zero-Shot)",
    "Test Entries"       : len(l4_results),
    "chrF"               : round(chrf_corpus, 2),
    "BERTScore-F1"       : round(F1_bs.mean().item(), 3),
    "WER"                : round(wer_avg, 3),
    "Label Mention Rate %": round(label_mention_avg, 1),
}

with open(f"{OUTPUT_DIR}/ceh_l4_gpt4omini_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary_l4, f, ensure_ascii=False, indent=2)

print("══════════════════════════════════════════")
print("  L4 Reasoning — GPT-4o-mini Summary")
print("══════════════════════════════════════════")
for k, v in summary_l4.items():
    print(f"  {k:<22} {v}")
print("\nSaved:")
print(f"   {OUTPUT_DIR}/ceh_l4_gpt4omini_results.csv")
print(f"   {OUTPUT_DIR}/ceh_l4_gpt4omini_summary.json")
