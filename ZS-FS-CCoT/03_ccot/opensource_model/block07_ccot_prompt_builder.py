# ══════════════════════════════════════════════════════════════
# BLOCK 7 — Contrastive Chain-of-Thought (C-CoT) Prompt Builder
# ══════════════════════════════════════════════════════════════
# KEY IDEA: force the model to argue BOTH readings (Name vs concept)
# for each occurrence BEFORE committing — directly attacks the
# dominant-meaning bias where models suppress the Name reading.
VALID_LABELS = {
    "Name",
    "Emotion",
    "Concept",
    "Spiritual",
    "Emotional State",
    "Collective State",
}

def build_ccot_prompt(entry):
    word  = entry["word_bangla"]
    roman = entry["word_roman"]
    narr  = entry["narrative_bangla"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in Bangla cultural linguistics and semantics. "
                "Some Bangla words are simultaneously a person's NAME and a "
                "culturally meaningful concept, emotion, or spiritual state. "
                "You reason about BOTH possible readings before deciding."
            ),
        },
        {
            "role": "user",
            "content": (
                f"The Bangla word '{word}' ({roman}) appears TWICE in this sentence "
                f"with two different meanings.\n\n"
                f"Sentence: {narr}\n\n"
                f"Reason contrastively for EACH occurrence:\n\n"
                f"For Occurrence 1:\n"
                f"- Argument A: why it could be a Name.\n"
                f"- Argument B: why it could be an Emotion / Concept / Spiritual / State.\n"
                f"- Decision: which reading the context supports.\n\n"
                f"For Occurrence 2:\n"
                f"- Argument A: why it could be a Name.\n"
                f"- Argument B: why it could be an Emotion / Concept / Spiritual / State.\n"
                f"- Decision: which reading the context supports.\n\n"
                f"After reasoning, end your reply with EXACTLY this block and nothing after:\n"
                f"FINAL:\n"
                f"Occurrence 1: <label>\n"
                f"Occurrence 2: <label>\n\n"
                f"Valid labels only: Name, Emotion, Concept, Spiritual, Emotional State, Collective State"
            ),
        },
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    return prompt

print(build_ccot_prompt(test_set[0]))
