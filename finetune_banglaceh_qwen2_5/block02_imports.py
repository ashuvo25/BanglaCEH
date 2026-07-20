# ══════════════════════════════════════════════════════════════
# BLOCK 2 — Imports
# ══════════════════════════════════════════════════════════════
import json, os, re, gc, random
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import torch
from torch.utils.data import Dataset as TorchDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig,
    TrainingArguments, Trainer, EarlyStoppingCallback,
)
from peft import (
    LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType,
)

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
print(f"imports ok | GPU: {torch.cuda.get_device_name(0)}")
