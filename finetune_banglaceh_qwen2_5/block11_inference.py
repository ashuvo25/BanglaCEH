# ══════════════════════════════════════════════════════════════
# BLOCK 11 — Inference on TEST (generate reasoning + FINAL block)
# ══════════════════════════════════════════════════════════════
import re
import torch
from tqdm import tqdm

model.eval(); model.config.use_cache = True; tokenizer.padding_side = "left"

def generate(e, max_new=400):
    prompt = build_prompt(e)
    inp = tokenizer(prompt, return_tensors="pt", truncation=True,
                     max_length=MAX_LEN).to(model.device)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=max_new, do_sample=False,
                              pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(out[0][inp["input_ids"].shape[1]:],
                             skip_special_tokens=True).strip()

def parse_labels(resp):
    p1, p2 = "Unknown", "Unknown"
    zone = resp
    idx = resp.upper().rfind("FINAL")
    if idx != -1:
        zone = resp[idx:]

    def norm(c):
        c = c.strip().strip(".").strip()
        for lbl in ["Emotional State", "Collective State"]:
            if lbl.lower() in c.lower():
                return lbl
        w = c.split()
        return w[0].capitalize() if w else "Unknown"

    for line in zone.split("\n"):
        m1 = re.search(r"Occurrence\s*1\s*[:：]\s*(.+)", line, re.I)
        m2 = re.search(r"Occurrence\s*2\s*[:：]\s*(.+)", line, re.I)
        if m1:
            p1 = norm(m1.group(1))
        if m2:
            p2 = norm(m2.group(1))
    p1 = p1 if p1 in VALID_LABELS else "Unknown"
    p2 = p2 if p2 in VALID_LABELS else "Unknown"
    # reasoning = everything BEFORE final block
    reasoning = resp[:idx].strip() if idx != -1 else resp
    return p1, p2, reasoning

results = []
for e in tqdm(test_set, desc="Test inference"):
    resp = generate(e)
    p1, p2, reason = parse_labels(resp)
    results.append({**e, "pred_label_1": p1, "pred_label_2": p2,
                     "gen_reasoning": reason, "raw": resp})
r = results[0]
print("\nGold  :", r["gold_label_1"], "|", r["gold_label_2"])
print("Pred  :", r["pred_label_1"], "|", r["pred_label_2"])
print("Reason:", r["gen_reasoning"][:200], "...")
print(f"inference on {len(results)}")
