# ══════════════════════════════════════════════════════════════
# BLOCK 10 — TRAIN
# ══════════════════════════════════════════════════════════════
import gc
import torch
import pandas as pd

torch.cuda.empty_cache(); gc.collect()
trainer.train()

BEST_DIR = f"{OUT_DIR}/best_adapter"
trainer.model.save_pretrained(BEST_DIR); tokenizer.save_pretrained(BEST_DIR)
hist = pd.DataFrame(trainer.state.log_history)
hist.to_csv(f"{OUT_DIR}/train_log.csv", index=False)
print(f"done | best eval_loss {trainer.state.best_metric:.4f}")
print(hist[hist['eval_loss'].notna()][['epoch', 'eval_loss']].to_string(index=False))
