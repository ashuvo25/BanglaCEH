# ══════════════════════════════════════════════════════════════
# BLOCK C — L4 Evaluation + Save
# ══════════════════════════════════════════════════════════════
import subprocess, sys
for pkg in ["rouge-score", "jiwer"]:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

import json
import pandas as pd
from tqdm import tqdm
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn
from rouge_score import rouge_scorer as rouge_scorer_lib
import jiwer

OUTPUT_DIR = "xxxxxxxxxx"

rouge_scorer_obj = rouge_scorer_lib.RougeScorer(["rougeL"], use_stemmer=True)
chrf_metric      = CHRF()

hyps = [r["model_response"]   for r in l4_results]
refs = [r["gold_explanation"] for r in l4_results]

# ── chrF ─────────────────────────────────────────────────────
chrf_corpus = chrf_metric.corpus_score(hyps, [refs]).score

# ── BERTScore ─────────────────────────────────────────────────
print("Computing BERTScore ...")
P, R, F1_bs = bert_score_fn(hyps, refs, lang="en",
                             rescale_with_baseline=True, verbose=False)

# ── WER ──────────────────────────────────────────────────────
def safe_wer(hyp, ref):
    if not hyp.strip() or not ref.strip():
        return 1.0
    try:
        return jiwer.wer(ref, hyp)
    except Exception:
        return 1.0

# ── Rouge-L ───────────────────────────────────────────────────
def get_rougeL(hyp, ref):
    if not hyp.strip() or not ref.strip():
        return 0.0
    return rouge_scorer_obj.score(ref, hyp)["rougeL"].fmeasure

# ── Label Mention Rate ────────────────────────────────────────
def label_mention_score(response, label_1, label_2):
    resp_lower = response.lower()
    return int(label_1.lower() in resp_lower) + int(label_2.lower() in resp_lower)

print("Computing per-entry metrics ...")
for i, r in enumerate(tqdm(l4_results, desc="Evaluating")):
    r["chrF"]                = round(chrf_metric.sentence_score(hyps[i], [refs[i]]).score, 2)
    r["bertscore_f1"]        = round(F1_bs[i].item(), 3)
    r["wer"]                 = round(safe_wer(hyps[i], refs[i]), 3)
    r["rouge_l"]             = round(get_rougeL(hyps[i], refs[i]), 3)
    r["label_mention_score"] = label_mention_score(
        r["model_response"], r["gold_label_1"], r["gold_label_2"]
    )

label_mention_avg = sum(r["label_mention_score"] for r in l4_results) / (len(l4_results) * 2) * 100
wer_avg           = sum(r["wer"]     for r in l4_results) / len(l4_results)
rougeL_avg        = sum(r["rouge_l"] for r in l4_results) / len(l4_results)

model_tag = MODEL_PATH.replace("/", "_")

# ── FILE 1: Raw model outputs JSON (for future LLM-as-Judge) ─
raw_outputs = [
    {
        "id"              : r["id"],
        "word_bangla"     : r["word_bangla"],
        "category"        : r["category"],
        "gold_label_1"    : r["gold_label_1"],
        "gold_label_2"    : r["gold_label_2"],
        "model_response"  : r["model_response"],
        "gold_explanation": r["gold_explanation"],
    }
    for r in l4_results
]

with open(f"{OUTPUT_DIR}/ceh_l4_{model_tag}_raw_outputs.json", "w", encoding="utf-8") as f:
    json.dump(raw_outputs, f, ensure_ascii=False, indent=2)

# ── FILE 2: Final results summary JSON ───────────────────────
summary_l4 = {
    "Model"                : MODEL_PATH,
    "Test Entries"         : len(l4_results),
    "chrF"                 : round(chrf_corpus,         2),
    "BERTScore-F1"         : round(F1_bs.mean().item(), 3),
    "WER"                  : round(wer_avg,             3),
    "Rouge-L"              : round(rougeL_avg,          3),
    "Label Mention Rate %" : round(label_mention_avg,   1),
}

with open(f"{OUTPUT_DIR}/ceh_l4_{model_tag}_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary_l4, f, ensure_ascii=False, indent=2)

# ── Print ─────────────────────────────────────────────────────
print("\n══════════════════════════════════════════════")
print(f"  L4 RESULTS — {MODEL_PATH}")
print("══════════════════════════════════════════════")
for k, v in summary_l4.items():
    print(f"  {k:<24} {v}")
print(f"\nSaved:")
print(f"   ceh_l4_{model_tag}_raw_outputs.json  <- model responses for LLM-as-Judge later")
print(f"   ceh_l4_{model_tag}_summary.json      <- final evaluation metrics")
