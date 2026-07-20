# ══════════════════════════════════════════════════════════════
# BLOCK 8 — Build generative KD target + prompt masking
# ══════════════════════════════════════════════════════════════
import numpy as np
import torch
from torch.utils.data import Dataset as TorchDataset

def build_prompt(e):
    msgs = [
        {"role": "system", "content": (
            "You are an expert in Bangla cultural linguistics. Some Bangla words "
            "are simultaneously a person's NAME and a culturally meaningful concept, "
            "emotion, or spiritual state. Explain WHY each occurrence carries its "
            "meaning, then give the final labels."
        )},
        {"role": "user", "content": (
            f"The Bangla word '{e['word_bangla']}' ({e['word_roman']}) appears TWICE "
            f"in this sentence with two different meanings.\n\n"
            f"Sentence: {e['narrative_bangla']}\n\n"
            f"Explain the cultural reasoning for each occurrence, then end with:\n"
            f"FINAL:\nOccurrence 1: <label>\nOccurrence 2: <label>\n\n"
            f"Valid labels: Name, Emotion, Concept, Spiritual, Emotional State, Collective State"
        )},
    ]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

def build_target(e):
    reasoning = e["kd_target"].strip()
    final = (f"\n\nFINAL:\nOccurrence 1: {e['gold_label_1']}\n"
             f"Occurrence 2: {e['gold_label_2']}")
    return reasoning + final + tokenizer.eos_token

# length audit → set MAX_LEN to p95
_lens = [len(tokenizer(build_prompt(e) + build_target(e))["input_ids"]) for e in train_set]
MAX_LEN = int(np.percentile(_lens, 95)) + 8
print(f"token lengths → mean {np.mean(_lens):.0f} | p95 {np.percentile(_lens,95):.0f} "
      f"| max {max(_lens)} → MAX_LEN={MAX_LEN}")

class KDDataset(TorchDataset):
    def __init__(self, entries):
        self.ex = []; skip = 0
        for e in entries:
            pid = tokenizer(build_prompt(e), add_special_tokens=False)["input_ids"]
            tid = tokenizer(build_target(e), add_special_tokens=False)["input_ids"]
            ids = pid + tid
            if len(ids) > MAX_LEN:
                skip += 1
                continue
            labels = [-100] * len(pid) + tid[:]        # supervise only reasoning+label
            self.ex.append({"input_ids": ids, "labels": labels})
        if skip:
            print(f"  skipped {skip} over MAX_LEN")

    def __len__(self):
        return len(self.ex)

    def __getitem__(self, i):
        return self.ex[i]

def collate(batch):
    m = max(len(b["input_ids"]) for b in batch); pad = tokenizer.pad_token_id
    ii, ll, am = [], [], []
    for b in batch:
        n = m - len(b["input_ids"])
        ii.append(b["input_ids"] + [pad] * n)
        ll.append(b["labels"] + [-100] * n)
        am.append([1] * len(b["input_ids"]) + [0] * n)
    return {"input_ids": torch.tensor(ii), "labels": torch.tensor(ll),
            "attention_mask": torch.tensor(am)}

train_ds, val_ds = KDDataset(train_set), KDDataset(val_set)
s = train_ds[0]
print(f"Train {len(train_ds)} | Val {len(val_ds)} | "
      f"supervised tokens ex0: {sum(1 for x in s['labels'] if x!=-100)}")
