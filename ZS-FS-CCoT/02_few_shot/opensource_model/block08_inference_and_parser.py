# ══════════════════════════════════════════════════════════════
# BLOCK 8 — Inference + Parser
# ══════════════════════════════════════════════════════════════
import re
import torch

def run_inference(prompt, max_new_tokens=80):
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

    # Decode only NEW tokens (not the prompt)
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    response   = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return response


def parse_response(response):
    pred_1, pred_2 = "Unknown", "Unknown"

    for line in response.strip().split("\n"):
        # Capture multi-word labels e.g. "Emotional State", "Collective State"
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*([A-Za-z ]+)", line, re.IGNORECASE)
        if m1:
            pred_1 = m1.group(1).strip().title()
        if m2:
            pred_2 = m2.group(1).strip().title()

    # Normalize — reject anything outside valid labels
    pred_1 = pred_1 if pred_1 in VALID_LABELS else "Unknown"
    pred_2 = pred_2 if pred_2 in VALID_LABELS else "Unknown"
    return pred_1, pred_2


# ── Quick test ────────────────────────────────────────────
test_responses = [
    "Occurrence 1: Name\nOccurrence 2: Emotional State",
    "Occurrence 1: Collective State\nOccurrence 2: Concept",
    "Occurrence 1: Name\nOccurrence 2: Spiritual",
    "Occurrence 1: blabla\nOccurrence 2: xyz",       # should give Unknown
]

print("── Parser Test ─────────────────────────────")
for t in test_responses:
    p1, p2 = parse_response(t)
    print(f"  Input : {t.strip()}")
    print(f"  Output: {p1} | {p2}")
    print()

print("Block 8 ready")
