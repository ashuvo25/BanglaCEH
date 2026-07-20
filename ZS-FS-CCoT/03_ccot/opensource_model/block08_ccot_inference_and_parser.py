# ══════════════════════════════════════════════════════════════
# BLOCK 8 — Inference + C-CoT Label Parser
# ══════════════════════════════════════════════════════════════
import re
import torch

def run_inference(prompt, max_new_tokens=512):
    # C-CoT needs more tokens than zero-shot because it reasons first
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
            do_sample=False,        # greedy — deterministic
            temperature=1.0,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    response   = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return response

def parse_ccot_response(response):
    # Prefer parsing the FINAL block (after reasoning). Fall back to
    # scanning the whole text if the model forgot the FINAL header.
    pred_1, pred_2 = "Unknown", "Unknown"

    # Isolate text after the last "FINAL" marker if present
    search_zone = response
    idx = response.upper().rfind("FINAL")
    if idx != -1:
        search_zone = response[idx:]

    two_word_labels = ["Emotional State", "Collective State"]

    for line in search_zone.split("\n"):
        # two-word labels first (avoid capturing only "Emotional")
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*(.+)", line, re.IGNORECASE)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*(.+)", line, re.IGNORECASE)
        if m1:
            cand = m1.group(1).strip()
            pred_1 = _normalise_label(cand, two_word_labels)
        if m2:
            cand = m2.group(1).strip()
            pred_2 = _normalise_label(cand, two_word_labels)

    pred_1 = pred_1 if pred_1 in VALID_LABELS else "Unknown"
    pred_2 = pred_2 if pred_2 in VALID_LABELS else "Unknown"
    return pred_1, pred_2

def _normalise_label(cand, two_word_labels):
    cand_clean = cand.strip().strip(".").strip()
    # check two-word labels
    for lbl in two_word_labels:
        if lbl.lower() in cand_clean.lower():
            return lbl
    # else take first word, capitalize
    first = cand_clean.split()[0] if cand_clean.split() else "Unknown"
    return first.capitalize()

print("Inference + C-CoT parser ready")
