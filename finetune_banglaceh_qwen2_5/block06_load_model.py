# ══════════════════════════════════════════════════════════════
# BLOCK 6 — Load base model in 4-bit
# ══════════════════════════════════════════════════════════════
import torch
from huggingface_hub import login
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
)
from peft import prepare_model_for_kbit_training

HF_TOKEN = "xxxxxxxxxx"
login(token=HF_TOKEN)

MODEL_PATH = "xxxxxxxxxx"
MODEL_TAG  = "xxxxxxxxxx"
OUT_DIR    = "xxxxxxxxxx"

bnb = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16,
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb,
    device_map={"": 0},          # everything on GPU 0 — no sharding, no DataParallel
    torch_dtype=torch.float16,
)
model.config.use_cache = False
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

# ── HARD GUARD: refuse to continue if 2 GPUs are visible ──
n_gpu = torch.cuda.device_count()
print(f"Visible GPUs: {n_gpu}")
assert n_gpu == 1, (
    "More than 1 GPU visible — GPU setup did not take effect. "
    "Factory-reset the kernel and run the GPU setup block as the FIRST cell before any import."
)
print(f"{MODEL_PATH} loaded 4-bit on {next(model.parameters()).device}")
