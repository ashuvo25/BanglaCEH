# ══════════════════════════════════════════════════════════════
# BLOCK 8 — Inference + Label Parser
# ══════════════════════════════════════════════════════════════
import re
import torch

def run_inference(prompt, max_new_tokens=80):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,       # greedy — deterministic
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only NEW tokens (not the prompt)
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    response   = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return response


def parse_response(response):
    pred_1, pred_2 = "Unknown", "Unknown"

    for line in response.strip().split("\n"):
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*(\w+)", line, re.IGNORECASE)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*(\w+)", line, re.IGNORECASE)
        if m1:
            pred_1 = m1.group(1).strip().capitalize()
        if m2:
            pred_2 = m2.group(1).strip().capitalize()

    # Reject anything outside valid labels
    pred_1 = pred_1 if pred_1 in VALID_LABELS else "Unknown"
    pred_2 = pred_2 if pred_2 in VALID_LABELS else "Unknown"
    return pred_1, pred_2

print("Ready")
