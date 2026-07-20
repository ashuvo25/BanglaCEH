# ══════════════════════════════════════════════════════════════
# BLOCK 9 — Training args (lower LR, more weight decay, early stop)
# ══════════════════════════════════════════════════════════════
from transformers import TrainingArguments, Trainer, EarlyStoppingCallback

model.is_parallelizable = False
model.model_parallel    = False

args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=5,                 # cap; early stop will end sooner
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,      # eff. batch 16
    gradient_checkpointing=True,
    learning_rate=1e-4,                 # smoother, later overfit
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,                   # gentler start
    weight_decay=0.05,                  # more regularisation
    max_grad_norm=0.3,
    fp16=True,
    optim="paged_adamw_8bit",
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=True,        # keep best (lowest val) checkpoint
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none",
    seed=SEED,
    dataloader_pin_memory=False,
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=val_ds,
    data_collator=collate,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
)
print("trainer ready (lr=1e-4, wd=0.05, r=16, dropout=0.1)")
