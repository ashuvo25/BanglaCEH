# ══════════════════════════════════════════════════════════════
# Zero-Shot Inference with Claude
# ══════════════════════════════════════════════════════════════
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "anthropic"])

import json, re, time
import anthropic
from tqdm import tqdm

ANTHROPIC_API_KEY = "xxxxxxxxxx"
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL_NAME = "claude-haiku-4-5-20251001"

VALID_LABELS = {
    "Name", "Emotion", "Concept", "Spiritual",
    "Emotional State", "Collective State",
}

def build_prompt(entry):
    word, roman, narr = entry["word_bangla"], entry["word_roman"], entry["narrative_bangla"]
    return (
        "You are an expert in Bangla linguistics and cultural semantics. "
        "Some Bangla words are simultaneously a person's name AND a "
        "culturally meaningful concept, emotion, or spiritual state.\n\n"
        f"The Bangla word '{word}' ({roman}) appears TWICE in this sentence "
        f"with two different meanings.\n\nSentence: {narr}\n\n"
        f"What does each occurrence of '{word}' represent?\n"
        f"Choose ONLY from: Name, Emotion, Concept, Spiritual, Emotional State, Collective State\n\n"
        f"Reply in EXACTLY this format:\nOccurrence 1: <label>\nOccurrence 2: <label>"
    )

def run_inference(prompt, max_retries=4):
    for attempt in range(max_retries):
        try:
            msg = client.messages.create(
                model=MODEL_NAME,
                max_tokens=60,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"  Retry {attempt+1} — {e}")
            time.sleep(3)
    return ""

def parse_response(response):
    pred_1, pred_2 = "Unknown", "Unknown"
    for line in response.strip().split("\n"):
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        if m1: pred_1 = m1.group(1).strip().title()
        if m2: pred_2 = m2.group(1).strip().title()
    pred_1 = pred_1 if pred_1 in VALID_LABELS else "Unknown"
    pred_2 = pred_2 if pred_2 in VALID_LABELS else "Unknown"
    return pred_1, pred_2

results = []
for entry in tqdm(test_set, desc="Claude Zero-Shot"):
    response = run_inference(build_prompt(entry))
    pred_1, pred_2 = parse_response(response)
    results.append({
        "id": entry["id"], "word_bangla": entry["word_bangla"],
        "category": entry["category"], "narrative": entry["narrative_bangla"],
        "gold_label_1": entry["gold_label_1"], "gold_label_2": entry["gold_label_2"],
        "pred_label_1": pred_1, "pred_label_2": pred_2,
        "raw_response": response, "gold_explanation": entry["gold_explanation"],
    })
    time.sleep(1)

print(f"Done: {len(results)} entries")
