# ══════════════════════════════════════════════════════════════
# BLOCK 6 — L4 Reasoning Inference (GPT-4o-mini)
# ══════════════════════════════════════════════════════════════
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openai", "jiwer"])

import time
from openai import OpenAI
from tqdm import tqdm

# ── Set your API key here ───────────────────────────────────
OPENAI_API_KEY = "xxxxxxxxxx"
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = "gpt-4o-mini"
# ─────────────────────────────────────────────────────────────

# Build id -> full target_output lookup from raw_data (has all CoT fields)
target_output_by_id = {e["id"]: e["target_output"] for e in raw_data}


def build_l4_prompt(entry):
    word    = entry["word_bangla"]
    roman   = entry["word_roman"]
    narr    = entry["narrative_bangla"]
    label_1 = entry["gold_label_1"]
    label_2 = entry["gold_label_2"]

    return (
        "You are an expert in Bangla linguistics and cultural semantics.\n\n"
        f"Sentence: {narr}\n\n"
        f"In this sentence, the word '{word}' ({roman}) appears TWICE:\n"
        f"- Occurrence 1 = {label_1}\n"
        f"- Occurrence 2 = {label_2}\n\n"
        f"Explain WHY occurrence 1 means '{label_1}', WHY occurrence 2 means "
        f"'{label_2}', and WHY these two meanings are culturally connected "
        f"in Bangla naming tradition.\n\n"
        f"Write your explanation in English, 3-5 sentences."
    )


def run_l4_inference(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            r = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=250,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            print(f"  Retry {attempt+1}/{max_retries} — {e}")
            time.sleep(3)
    return ""


# ── Run L4 on test set ───────────────────────────────────────
l4_results = []

for entry in tqdm(test_set, desc="L4 Reasoning (GPT-4o-mini)"):
    prompt   = build_l4_prompt(entry)
    response = run_l4_inference(prompt)

    target_output = target_output_by_id[entry["id"]]

    l4_results.append({
        "id"            : entry["id"],
        "word_bangla"   : entry["word_bangla"],
        "word_roman"    : entry["word_roman"],
        "category"      : entry["category"],
        "narrative"     : entry["narrative_bangla"],
        "gold_label_1"  : entry["gold_label_1"],
        "gold_label_2"  : entry["gold_label_2"],
        "model_response": response,

        # Full ground-truth CoT fields (for reference / future use)
        "gold_why_first_bangla"        : target_output["why_first_is_label1_bangla"],
        "gold_why_second_bangla"       : target_output["why_second_is_label2_bangla"],
        "gold_why_first_english"       : target_output["why_first_is_label1_english"],
        "gold_why_second_english"      : target_output["why_second_is_label2_english"],
        "gold_cultural_entanglement_bn": target_output["cultural_entanglement_bangla"],
        "gold_cultural_entanglement_en": target_output["cultural_entanglement_english"],
        "gold_explanation"             : target_output["full_explanation_english"],
    })

    time.sleep(0.5)

print(f"L4 inference done: {len(l4_results)} entries")
