# ══════════════════════════════════════════════════════════════
# BLOCK 1 — Install Libraries
# ══════════════════════════════════════════════════════════════
import subprocess, sys

pkgs = [
    "transformers>=4.43.0",
    "torch",
    "sacrebleu",
    "bert-score",
    "scikit-learn",
    "pandas",
    "tqdm",
    "accelerate",
    "bitsandbytes",
]

for pkg in pkgs:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

print("Done")
