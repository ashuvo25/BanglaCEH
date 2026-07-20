# ══════════════════════════════════════════════════════════════
# BLOCK 0 — GPU setup
# ══════════════════════════════════════════════════════════════
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch
print(torch.cuda.device_count())
