# ══════════════════════════════════════════════════════════════
# BLOCK 14 — Paper figures (300 dpi, publication-ready)
# ══════════════════════════════════════════════════════════════
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

FIGURES_OUTPUT_DIR = "xxxxxxxxxx"

plt.rcParams.update({"figure.dpi": 300, "font.size": 11, "font.family": "DejaVu Sans"})

# Fig 1 — training / validation loss curve
fig, ax = plt.subplots(figsize=(6, 4))
tr = hist[hist["loss"].notna()]
ev = hist[hist["eval_loss"].notna()]
ax.plot(tr["epoch"], tr["loss"], label="Train loss", lw=1.5)
ax.plot(ev["epoch"], ev["eval_loss"], label="Val loss", marker="o", lw=1.5)
best = ev.loc[ev["eval_loss"].idxmin()]
ax.axvline(best["epoch"], ls="--", c="gray", alpha=.6)
ax.scatter([best["epoch"]], [best["eval_loss"]], c="red", zorder=5,
           label=f"Best (ep {best['epoch']:.0f})")
ax.set_xlabel("Epoch"); ax.set_ylabel("Loss")
ax.set_title(f"QLoRA-KD Training — {MODEL_TAG}")
ax.legend(); ax.grid(alpha=.3); fig.tight_layout()
fig.savefig(f"{FIGURES_OUTPUT_DIR}/fig1_loss_curve.png", bbox_inches="tight")

# Fig 2 — method progression (fill your other numbers)
fig, ax = plt.subplots(figsize=(7, 4))
methods = ["Zero-shot", "Few-shot", "C-CoT", "QLoRA-KD"]
em = [0.65, 8.39, 30.97, exact]           # exact-match across methods
db = [63.46, 23.08, 2.88, bias]           # dominant-bias across methods
x = np.arange(len(methods)); w = .38
ax.bar(x - w / 2, em, w, label="Exact Match %", color="#2a78d6")
ax.bar(x + w / 2, db, w, label="Dominant-Bias %", color="#e34948")
ax.set_xticks(x); ax.set_xticklabels(methods)
ax.set_ylabel("%"); ax.set_title(f"Method Progression — {MODEL_TAG}")
ax.legend(); ax.grid(axis="y", alpha=.3); fig.tight_layout()
fig.savefig(f"{FIGURES_OUTPUT_DIR}/fig2_method_progression.png", bbox_inches="tight")

# Fig 3 — per-category exact accuracy
cat_df = pd.DataFrame(results); cat_df["score"] = scores
cs = (cat_df.groupby("category")["score"].mean() / 2 * 100).sort_values()
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(range(len(cs)), cs.values, color="#1baf7a")
ax.set_yticks(range(len(cs))); ax.set_yticklabels(cs.index, fontsize=8)
ax.set_xlabel("Avg Score %"); ax.set_title(f"Per-Category Accuracy — {MODEL_TAG}")
ax.grid(axis="x", alpha=.3); fig.tight_layout()
fig.savefig(f"{FIGURES_OUTPUT_DIR}/fig3_per_category.png", bbox_inches="tight")

# Fig 4 — confusion of labels
labs = sorted(VALID_LABELS)
cm = confusion_matrix(gold, pred, labels=labs)
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs, fontsize=8)
for i in range(len(labs)):
    for j in range(len(labs)):
        ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8,
                 color="white" if cm[i, j] > cm.max() / 2 else "black")
ax.set_xlabel("Predicted"); ax.set_ylabel("Gold")
ax.set_title(f"Label Confusion — {MODEL_TAG}")
fig.colorbar(im, fraction=.046); fig.tight_layout()
fig.savefig(f"{FIGURES_OUTPUT_DIR}/fig4_confusion.png", bbox_inches="tight")

print("figures saved: fig1_loss_curve, fig2_method_progression, fig3_per_category, fig4_confusion")
