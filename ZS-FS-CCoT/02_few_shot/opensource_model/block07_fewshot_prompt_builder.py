# ══════════════════════════════════════════════════════════════
# BLOCK 7 — Few-Shot Prompt Builder (3-shot)
# ══════════════════════════════════════════════════════════════
VALID_LABELS = {
    "Name",
    "Emotion",
    "Concept",
    "Spiritual",
    "Emotional State",
    "Collective State",
}

# 3 fixed examples — one from each major category
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


def build_fewshot_prompt(entry):
    word  = entry["word_bangla"]
    roman = entry["word_roman"]
    narr  = entry["narrative_bangla"]

    # Build few-shot examples as part of conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in Bangla linguistics and cultural semantics. "
                "Some Bangla words are simultaneously a person's name AND a "
                "culturally meaningful concept, emotion, or spiritual state. "
                "Identify what each occurrence of the given word represents. "
                "Choose ONLY from: Name, Emotion, Concept, Spiritual, State"
            ),
        },
    ]

    # Add few-shot examples as user/assistant turns
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

    # Now add the actual test question
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

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    return prompt

print("Few-shot prompt builder ready")

# Sanity check — print one prompt
print("\n── Sample Prompt ───────────────────────────")
print(build_fewshot_prompt(test_set[0]))
