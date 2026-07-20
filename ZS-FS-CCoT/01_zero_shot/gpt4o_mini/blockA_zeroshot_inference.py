# ══════════════════════════════════════════════════════════════
# BLOCK A — Zero-Shot Inference with GPT-4o-mini
# ══════════════════════════════════════════════════════════════
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "openai"])

import json, re, time
from openai import OpenAI
from tqdm import tqdm

# ── Set your API key here ───────────────────────────────────
OPENAI_API_KEY = "xxxxxxxxxx"
client = OpenAI(api_key=OPENAI_API_KEY)
# ─────────────────────────────────────────────────────────────

VALID_LABELS = {
    "Name", "Emotion", "Concept", "Spiritual",
    "Emotional State", "Collective State",
}

def build_prompt_messages(entry):
    word  = entry["word_bangla"]
    roman = entry["word_roman"]
    narr  = entry["narrative_bangla"]

    return [
        {
            "role": "system",
            "content": (
                "You are an expert in Bangla linguistics and cultural semantics. "
                "Some Bangla words are simultaneously a person's name AND a "
                "culturally meaningful concept, emotion, or spiritual state. "
                "Identify what each occurrence of the given word represents."
            ),
        },
        {
            "role": "user",
            "content": (
                f"The Bangla word '{word}' ({roman}) appears TWICE in this sentence "
                f"with two different meanings.\n\n"
                f"Sentence: {narr}\n\n"
                f"What does each occurrence of '{word}' represent?\n"
                f"Choose ONLY from: Name, Emotion, Concept, Spiritual, "
                f"Emotional State, Collective State\n\n"
                f"Reply in EXACTLY this format, nothing else:\n"
                f"Occurrence 1: <label>\n"
                f"Occurrence 2: <label>"
            ),
        },
    ]


def run_gpt_inference(entry, max_retries=3):
    messages = build_prompt_messages(entry)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,        # greedy / deterministic
                max_tokens=60,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  Retry {attempt+1}/{max_retries} — {e}")
            time.sleep(2)

    return ""   # fallback on repeated failure


def parse_response(response):
    pred_1, pred_2 = "Unknown", "Unknown"

    for line in response.strip().split("\n"):
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        if m1:
            pred_1 = m1.group(1).strip().title()
        if m2:
            pred_2 = m2.group(1).strip().title()

    pred_1 = pred_1 if pred_1 in VALID_LABELS else "Unknown"
    pred_2 = pred_2 if pred_2 in VALID_LABELS else "Unknown"
    return pred_1, pred_2


# ── Run on Test Set ──────────────────────────────────────────
results = []

for entry in tqdm(test_set, desc="GPT-4o-mini Zero-Shot"):
    response       = run_gpt_inference(entry)
    pred_1, pred_2 = parse_response(response)

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

    time.sleep(0.5)   # rate-limit friendly

print(f"GPT-4o-mini zero-shot done: {len(results)} entries")
