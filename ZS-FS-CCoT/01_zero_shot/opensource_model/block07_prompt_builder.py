# ══════════════════════════════════════════════════════════════
# BLOCK 7 — Prompt Builder (Zero-Shot, no examples)
# ══════════════════════════════════════════════════════════════
VALID_LABELS = {
    "Name",
    "Emotion",
    "Concept",
    "Spiritual",
    "Emotional State",
    "Collective State",
}

def build_prompt(entry):
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
                f"Choose ONLY from: Name, Emotion, Concept, Spiritual, State\n\n"
                f"Reply in EXACTLY this format, nothing else:\n"
                f"Occurrence 1: <label>\n"
                f"Occurrence 2: <label>"
            ),
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    return prompt

# Test prompt
print(build_prompt(test_set[0]))
