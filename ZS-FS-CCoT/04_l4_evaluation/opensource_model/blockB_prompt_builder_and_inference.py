# ══════════════════════════════════════════════════════════════
# BLOCK B — L4 Prompt Builder + Inference + Generate Output
# ══════════════════════════════════════════════════════════════
import json
import torch
from tqdm import tqdm

# Load target_output lookup
target_output_by_id = {e["id"]: e["target_output"] for e in raw_data}

def build_l4_prompt(entry):
    word    = entry["word_bangla"]
    roman   = entry["word_roman"]
    narr    = entry["narrative_bangla"]
    label_1 = entry["gold_label_1"]
    label_2 = entry["gold_label_2"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert in Bangla linguistics and cultural semantics. "
                "You understand that some Bangla words are simultaneously a person's "
                "name AND a culturally meaningful concept, emotion, or spiritual state."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Sentence: {narr}\n\n"
                f"In this sentence, the word '{word}' ({roman}) appears TWICE:\n"
                f"- Occurrence 1 = {label_1}\n"
                f"- Occurrence 2 = {label_2}\n\n"
                f"Explain WHY occurrence 1 means '{label_1}', "
                f"WHY occurrence 2 means '{label_2}', "
                f"and WHY these two meanings are culturally connected "
                f"in Bangla naming tradition.\n\n"
                f"Write your explanation in English, 3-5 sentences."
            ),
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    return prompt


def run_l4_inference(prompt, max_new_tokens=250):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    response   = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return response


# ── Run on test set ──────────────────────────────────────────
l4_results = []
total = len(test_set)

for i, entry in enumerate(tqdm(test_set, desc=f"L4 ({MODEL_PATH})")):
    prompt        = build_l4_prompt(entry)
    response      = run_l4_inference(prompt)
    target_output = target_output_by_id[entry["id"]]

    l4_results.append({
        "id"                           : entry["id"],
        "word_bangla"                  : entry["word_bangla"],
        "word_roman"                   : entry["word_roman"],
        "category"                     : entry["category"],
        "narrative"                    : entry["narrative_bangla"],
        "gold_label_1"                 : entry["gold_label_1"],
        "gold_label_2"                 : entry["gold_label_2"],
        "model_response"               : response,
        "gold_why_first_bangla"        : target_output["why_first_is_label1_bangla"],
        "gold_why_second_bangla"       : target_output["why_second_is_label2_bangla"],
        "gold_why_first_english"       : target_output["why_first_is_label1_english"],
        "gold_why_second_english"      : target_output["why_second_is_label2_english"],
        "gold_cultural_entanglement_bn": target_output["cultural_entanglement_bangla"],
        "gold_cultural_entanglement_en": target_output["cultural_entanglement_english"],
        "gold_explanation"             : target_output["full_explanation_english"],
    })

    if (i + 1) % 10 == 0 or (i + 1) == total:
        print(f"  {i+1}/{total} | {entry['word_bangla']} -> {response[:60]}...")

print(f"\nL4 output done: {len(l4_results)} entries")
r = l4_results[0]
print(f"\nWord     : {r['word_bangla']}")
print(f"Labels   : {r['gold_label_1']} | {r['gold_label_2']}")
print(f"Response : {r['model_response'][:200]}...")
