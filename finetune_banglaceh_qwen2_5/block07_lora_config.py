# ══════════════════════════════════════════════════════════════
# BLOCK 7 — LoRA config (reduced capacity to curb overfitting)
# ══════════════════════════════════════════════════════════════
from peft import LoraConfig, get_peft_model, TaskType

lora = LoraConfig(
    r=16,                 # less capacity to memorise
    lora_alpha=32,        # keep alpha = 2×r ratio
    lora_dropout=0.1,     # stronger regularisation
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, lora)
model.print_trainable_parameters()
print("LoRA attached (r=16, alpha=32, dropout=0.1)")
