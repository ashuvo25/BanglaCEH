# ══════════════════════════════════════════════════════════════
# BLOCK C — Few-Shot (3-shot) Inference with GPT-4o-mini
# ══════════════════════════════════════════════════════════════
import time, re
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

FEW_SHOT_EXAMPLES = [
    {
        "word"     : "মায়া (Maya)",
        "narrative": "মায়া নামের মেয়েটিকে একাকী বসে কাঁদতে দেখে উপস্থিত সবার মনেই এক গভীর মায়া জেগে উঠল।",
        "label_1"  : "Name",
        "label_2"  : "Emotion",
    },
    {
        "word"     : "বিপ্লব (Biplab)",
        "narrative": "বিপ্লব যখন রাজপথে নামল, তখন সারা দেশে এক নতুন বিপ্লব শুরু হলো।",
        "label_1"  : "Name",
        "label_2"  : "Concept",
    },
    {
        "word"     : "শান্তি (Shanti)",
        "narrative": "শান্তি মন্দিরে প্রবেশ করতেই তার ভেতরে এক অপার শান্তি নেমে এলো।",
        "label_1"  : "Name",
        "label_2"  : "Spiritual",
    },
]


def build_fewshot_messages(entry):
    word  = entry["word_bangla"]
    roman = entry["word_roman"]
    narr  = entry["narrative_bangla"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in Bangla linguistics and cultural semantics. "
                "Some Bangla words are simultaneously a person's name AND a "
                "culturally meaningful concept, emotion, or spiritual state. "
                "Identify what each occurrence of the given word represents. "
                "Choose ONLY from: Name, Emotion, Concept, Spiritual, "
                "Emotional State, Collective State"
            ),
        },
    ]

    # Add 3-shot examples as user/assistant turns
    for ex in FEW_SHOT_EXAMPLES:
        messages.append({
            "role": "user",
            "content": (
                f"The Bangla word '{ex['word']}' appears TWICE in this sentence "
                f"with two different meanings.\n\n"
                f"Sentence: {ex['narrative']}\n\n"
                f"What does each occurrence represent?\n"
                f"Reply in EXACTLY this format:\n"
                f"Occurrence 1: <label>\n"
                f"Occurrence 2: <label>"
            ),
        })
        messages.append({
            "role": "assistant",
            "content": (
                f"Occurrence 1: {ex['label_1']}\n"
                f"Occurrence 2: {ex['label_2']}"
            ),
        })

    # Actual test question
    messages.append({
        "role": "user",
        "content": (
            f"The Bangla word '{word}' ({roman}) appears TWICE in this sentence "
            f"with two different meanings.\n\n"
            f"Sentence: {narr}\n\n"
            f"What does each occurrence represent?\n"
            f"Reply in EXACTLY this format:\n"
            f"Occurrence 1: <label>\n"
            f"Occurrence 2: <label>"
        ),
    })

    return messages


def run_gpt_fewshot_inference(entry, max_retries=3):
    messages = build_fewshot_messages(entry)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,
                max_tokens=60,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  Retry {attempt+1}/{max_retries} — {e}")
            time.sleep(2)

    return ""


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
results_fewshot = []

for entry in tqdm(test_set, desc="GPT-4o-mini 3-Shot"):
    response       = run_gpt_fewshot_inference(entry)
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

    time.sleep(0.5)

print(f"GPT-4o-mini 3-shot done: {len(results_fewshot)} entries")
