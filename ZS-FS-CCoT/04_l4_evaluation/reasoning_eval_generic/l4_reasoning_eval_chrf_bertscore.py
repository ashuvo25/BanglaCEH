# ══════════════════════════════════════════════════════════════
# L4 — Reasoning Eval (chrF + BERTScore + Label Mention Rate)
# ══════════════════════════════════════════════════════════════
import subprocess, sys
for pkg in ["sacrebleu", "bert-score", "pandas", "tqdm"]:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

import json, time, re
import pandas as pd
from tqdm import tqdm
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn

# ── STEP 1 — Load main dataset ──────────────────────────────
MAIN_DATASET_PATH = "xxxxxxxxxx"
with open(MAIN_DATASET_PATH, "r", encoding="utf-8") as f:
    main_data = json.load(f)

main_by_id = {d["id"]: d for d in main_data}

# ── STEP 2 — Load your zero/few-shot results CSV ────────────
RESULTS_CSV_PATH = "xxxxxxxxxx"   # ← change per model/setting
csv_df = pd.read_csv(RESULTS_CSV_PATH)

# ── STEP 3 — L4 Prompt Builder ──────────────────────────────
def build_l4_prompt(entry, gold_label_1, gold_label_2):
    word  = entry["word_bangla"]
    roman = entry["word_roman"]
    narr  = entry["input"]["narrative_bangla"]

    return (
        "You are an expert in Bangla linguistics and cultural semantics.\n\n"
        f"Sentence: {narr}\n\n"
        f"In this sentence, the word '{word}' ({roman}) appears TWICE:\n"
        f"- Occurrence 1 = {gold_label_1}\n"
        f"- Occurrence 2 = {gold_label_2}\n\n"
        f"Explain WHY occurrence 1 means '{gold_label_1}', WHY occurrence 2 means "
        f"'{gold_label_2}', and WHY these two meanings are culturally connected "
        f"in Bangla naming tradition.\n\n"
        f"Write your explanation in English, 3-5 sentences."
    )

# ── STEP 4 — Inference (PLUG IN YOUR MODEL CALL HERE) ───────
def run_inference(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            response = MY_MODEL_CALL(prompt)   # ← e.g. client.chat.completions.create(...)
            return response.strip()
        except Exception as e:
            print(f"  Retry {attempt+1} — {e}")
            time.sleep(3)
    return ""

# ── STEP 5 — Run, matched by ID ──────────────────────────────
results = []

for _, row in tqdm(csv_df.iterrows(), total=len(csv_df), desc="L4 Reasoning"):
    entry_id = int(row["id"])
    entry    = main_by_id.get(entry_id)

    if entry is None:
        print(f"  ID {entry_id} not found in main dataset, skipping")
        continue

    gold_label_1 = row["gold_label_1"]
    gold_label_2 = row["gold_label_2"]

    prompt   = build_l4_prompt(entry, gold_label_1, gold_label_2)
    response = run_inference(prompt)

    gold_explanation = entry["target_output"]["full_explanation_english"]

    results.append({
        "id"               : entry_id,
        "word_bangla"      : entry["word_bangla"],
        "category"         : entry["category"],
        "narrative"        : entry["input"]["narrative_bangla"],
        "gold_label_1"     : gold_label_1,
        "gold_label_2"     : gold_label_2,
        "gold_explanation" : gold_explanation,
        "model_response"   : response,
    })

    time.sleep(1)

print(f"L4 inference done: {len(results)} entries")

# ── STEP 6 — Evaluate chrF + BERTScore + Label Mention Rate ──
hyps = [r["model_response"]    for r in results]
refs = [r["gold_explanation"]  for r in results]

chrf_corpus = CHRF().corpus_score(hyps, [refs]).score
P, R, F1    = bert_score_fn(hyps, refs, lang="en", rescale_with_baseline=True, verbose=False)

def label_mention_score(response, label_1, label_2):
    resp_lower = response.lower()
    m1 = label_1.lower() in resp_lower
    m2 = label_2.lower() in resp_lower
    return int(m1) + int(m2)

for i, r in enumerate(results):
    r["chrF"]               = round(CHRF().sentence_score(hyps[i], [refs[i]]).score, 2)
    r["bertscore_f1"]       = round(F1[i].item(), 3)
    r["label_mention_score"] = label_mention_score(r["model_response"], r["gold_label_1"], r["gold_label_2"])

label_mention_avg = sum(r["label_mention_score"] for r in results) / (len(results) * 2) * 100

# ── STEP 7 — Save CSV ─────────────────────────────────────────
df_out = pd.DataFrame(results)
df_out.to_csv("ceh_l4_results.csv", index=False, encoding="utf-8-sig")

print("\n══════════════════════════════════════════")
print(f"  L4 Reasoning — Summary")
print("══════════════════════════════════════════")
print(f"  Entries              : {len(results)}")
print(f"  chrF (corpus)        : {chrf_corpus:.2f}")
print(f"  BERTScore-F1         : {F1.mean().item():.3f}")
print(f"  Label Mention Rate % : {label_mention_avg:.1f}")
print("\nSaved: ceh_l4_results.csv")
