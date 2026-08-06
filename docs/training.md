# AutoScientist Training Guide

## Overview

The **AutoScientist** model is a scientific reasoning language model fine-tuned on the Dataset Genome benchmark using **LoRA** (Low-Rank Adaptation) via the HuggingFace **PEFT** library.

The training pipeline takes the generated benchmark dataset and produces a model capable of:
- Formulating scientific hypotheses from observations
- Designing experimental validation procedures
- Identifying research gaps in existing literature
- Predicting experimental outcomes and failure modes

---

## Training Pipeline

```
Generated Dataset (JSONL)
         │
         ▼
┌──────────────────────────┐
│  Adaption Adaptive Data  │  ← Dataset preprocessing
│  Processing              │     Formatting to instruction-tuning format
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  LoRA Configuration      │  ← Parameter-Efficient Fine-Tuning (PEFT)
│  (PEFT Library)          │     Rank: r=8 or r=16
│                          │     Alpha: lora_alpha=32
│                          │     Dropout: 0.05
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  GPT-class Base Model    │  ← Pre-trained base
│  (Instruction-tuned)     │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  AutoScientist Model     │  ← Fine-tuned adapter weights
│  (LoRA Adapter)          │     Stored as .safetensors
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  HuggingFace Model Hub   │  ← Published
│                          │
└──────────────────────────┘
```

---

## Adaptive Data Processing

Before training, the dataset goes through the **Adaption Adaptive Data** pipeline:

1. **Format conversion** — Records are converted from the benchmark schema to instruction-tuning format:
   ```
   ### Instruction:
   {prompt}

   ### Context:
   {context}

   ### Response:
   Primary Hypothesis: {primary_hypothesis}
   Experiment Design: {experiment_design}
   Expected Result: {expected_result}
   Scientific Conclusion: {scientific_conclusion}
   ```

2. **Quality filtering** — Only records with adaptive score above threshold are included

3. **Deduplication** — Near-identical samples removed before training

4. **Split preparation** — Training set prepared (no test split in v1.0 release)

---

## PEFT / LoRA Configuration

Dataset Genome uses **PEFT** (Parameter-Efficient Fine-Tuning) with **LoRA** (Low-Rank Adaptation) for efficient fine-tuning.

### Why LoRA?

| Advantage | Description |
|-----------|-------------|
| **Parameter efficiency** | Fine-tunes <1% of model parameters |
| **Memory efficiency** | Trainable on consumer-grade GPUs |
| **No catastrophic forgetting** | Base model weights unchanged |
| **Modular** | Adapter can be merged or swapped |

### LoRA Parameters

```python
from peft import LoraConfig, TaskType

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,                         # Rank of update matrices
    lora_alpha=32,               # Scaling factor
    lora_dropout=0.05,           # Dropout for LoRA layers
    target_modules=["q_proj", "v_proj"],  # Attention modules to adapt
    bias="none",
)
```

### Training Configuration

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./autoscientist-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,                   # Mixed precision for efficiency
)
```

---

## Dataset Used for Training

| Property | Value |
|----------|-------|
| **HF Release Dataset** | 20 records (Agriculture, v1.0) |
| **Full Benchmark** | 200 records (10 domains) |
| **Format** | JSONL (instruction-tuning) |
| **Task** | Causal Language Modeling |

The HuggingFace v1.0 release uses the **Agriculture** domain subset. The full 10-domain benchmark (`export_benchmark/benchmark_v1.0.jsonl`) is available for broader training.

---

## Model Evaluation

The AutoScientist model is evaluated on:

| Metric | Description |
|--------|-------------|
| **Reasoning Quality** | Coherence and logical validity of hypothesis chains |
| **Hypothesis Accuracy** | Alignment with ground-truth primary hypothesis |
| **Model Confidence** | Calibration of prediction certainty |

Evaluation results from the publication pipeline:

| Metric | Score |
|--------|-------|
| Reasoning Quality | 88.5 / 100 |
| Hypothesis Accuracy | 84.0% |
| Model Confidence | 89.0% |

---

## Published Model

The trained AutoScientist model adapter weights are published to HuggingFace:

```bash
# Load from HuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("YOUR-BASE-MODEL")
model = PeftModel.from_pretrained(base_model, "YOUR-HF-USERNAME/autoscientist-reasoning-model")
tokenizer = AutoTokenizer.from_pretrained("YOUR-HF-USERNAME/autoscientist-reasoning-model")
```

---

## Reproducing Training

```bash
# 1. Setup environment
cp .env.example .env
pip install -r requirements.txt

# 2. Generate the dataset
python demo.py

# 3. The training dataset is available at:
#    export_benchmark/benchmark_v1.0.jsonl   (full 200 samples)
#    publication/huggingface/train.jsonl     (20 Agriculture samples)
```

---

*See [`dataset.md`](dataset.md) for the training data schema and [`benchmark.md`](benchmark.md) for quality metrics.*
