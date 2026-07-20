# ══════════════════════════════════════════════════════════════
# BLOCK 6 — Load Model (HuggingFace)
# ══════════════════════════════════════════════════════════════
import torch
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

HF_TOKEN = "xxxxxxxxxx"
login(token=HF_TOKEN)

# unsloth/Qwen2.5-1.5B-Instruct
# unsloth/Llama-3.2-3B-Instruct
# unsloth/DeepSeek-R1-Distill-Qwen-1.5B
# openbmb/MiniCPM5-1B
# google/gemma-3-1b-it
# hishab/titulm-llama-3.2-1b-v1.1
# mistralai/Ministral-3-3B-Instruct-2512

MODEL_PATH = "hishab/titulm-llama-3.2-1b-v1.1"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)
model.eval()
print(f"{MODEL_PATH}  loaded (4-bit on T4)")
