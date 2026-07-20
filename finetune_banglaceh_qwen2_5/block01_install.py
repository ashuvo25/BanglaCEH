# ══════════════════════════════════════════════════════════════
# BLOCK 1 — Install
# ══════════════════════════════════════════════════════════════
import subprocess, sys
pkgs = [
    "transformers>=4.43.0", "torch", "peft>=0.11.0", "trl>=0.9.0",
    "datasets", "sacrebleu", "bert-score", "scikit-learn",
    "pandas", "matplotlib", "tqdm", "accelerate", "bitsandbytes",
]
for p in pkgs:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", p])
print("installed")
