# ══════════════════════════════════════════════════════════════
# BLOCK 2 — Import Libraries
# ══════════════════════════════════════════════════════════════
import json, random, re, os
import pandas as pd
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from sacrebleu.metrics import CHRF
from bert_score import score as bert_score_fn
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

print("Done")
