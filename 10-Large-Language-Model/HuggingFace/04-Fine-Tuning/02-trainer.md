# Trainer API — Fine-tuning avec Hugging Face

## Qu'est-ce que le `Trainer` ?

Le `Trainer` est la classe principale de Hugging Face pour l'entraînement. Il automatise :

- La boucle d'entraînement (forward pass, loss, backward, optimizer step)
- L'évaluation sur le set de validation
- La sauvegarde des checkpoints
- Le logging (TensorBoard, WandB, etc.)
- La gestion du multi-GPU via `accelerate`
- Le gradient accumulation et mixed precision (FP16/BF16)

**Principe** : configurer via `TrainingArguments`, puis appeler `trainer.train()`.

---

## Pipeline complet — Classification de sentiment

```python
# fine_tune_classification.py
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
import evaluate
import numpy as np

# ─── 1. Données ───
dataset = load_dataset("allocine")
tokenizer = AutoTokenizer.from_pretrained("camembert-base")

def tokenize(batch):
    return tokenizer(batch["review"], truncation=True, max_length=256)

tokenized = dataset.map(tokenize, batched=True, remove_columns=["review"])
tokenized = tokenized.rename_column("label", "labels")

# ─── 2. Modèle ───
model = AutoModelForSequenceClassification.from_pretrained(
    "camembert-base",
    num_labels=2,
    id2label={0: "NÉGATIF", 1: "POSITIF"},
    label2id={"NÉGATIF": 0, "POSITIF": 1},
)

# ─── 3. Métriques ───
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=predictions, references=labels)
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="binary")
    return {**acc, **f1}

# ─── 4. TrainingArguments ───
training_args = TrainingArguments(
    output_dir="./results/sentiment-camembert",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",       # Évaluer à chaque epoch
    save_strategy="epoch",       # Sauvegarder à chaque epoch
    load_best_model_at_end=True, # Charger le meilleur checkpoint à la fin
    metric_for_best_model="f1",  # Critère de sélection du meilleur modèle
    fp16=True,                   # Mixed precision FP16 (GPU CUDA seulement)
    # bf16=True,                 # Ou BF16 pour les GPU récents (A100, etc.)
    logging_steps=100,
    report_to="none",            # Désactiver W&B/TensorBoard pour l'exemple
)

# ─── 5. Trainer ───
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

# ─── 6. Entraînement ───
trainer.train()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La sortie du terminal pendant l'entraînement montrant la progression : barre de progression tqdm, les logs par step (`{'loss': 0.42, 'learning_rate': 1.8e-05, 'epoch': 0.5}`), et le tableau d'évaluation à chaque epoch (`{'eval_loss': 0.18, 'eval_accuracy': 0.93, 'eval_f1': 0.93, 'epoch': 1.0}`)
> **Expliquer :** Comment lire les métriques en temps réel, ce que signifie la `eval_loss` qui diminue (le modèle généralise), et comment détecter le surapprentissage (eval_loss remonte tandis que train_loss continue de baisser)

---

## `TrainingArguments` — Référence complète

```python
from transformers import TrainingArguments

args = TrainingArguments(
    # ─── Chemins ───
    output_dir="./results",          # Dossier de sortie (checkpoints + logs)

    # ─── Epochs et batch size ───
    num_train_epochs=3,
    per_device_train_batch_size=16,  # Batch par GPU pour l'entraînement
    per_device_eval_batch_size=32,   # Batch par GPU pour l'évaluation
    gradient_accumulation_steps=2,  # Simule un batch de 16*2=32 sans VRAM

    # ─── Optimizer ───
    learning_rate=2e-5,
    weight_decay=0.01,               # Régularisation L2
    adam_epsilon=1e-8,
    adam_beta1=0.9,
    adam_beta2=0.999,
    max_grad_norm=1.0,               # Gradient clipping

    # ─── Scheduler ───
    lr_scheduler_type="linear",      # "linear", "cosine", "constant"
    warmup_ratio=0.1,                # 10% des steps = warmup
    # warmup_steps=100,              # Ou nombre fixe de steps

    # ─── Évaluation et sauvegarde ───
    eval_strategy="steps",           # "no" / "epoch" / "steps"
    eval_steps=500,                  # Si eval_strategy="steps"
    save_strategy="steps",           # "no" / "epoch" / "steps"
    save_steps=500,
    save_total_limit=3,              # Garder seulement les 3 derniers checkpoints
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,          # F1 : plus grand = meilleur

    # ─── Précision ───
    fp16=True,                       # FP16 (GPU CUDA)
    # bf16=True,                     # BF16 (Ampere+)
    # tf32=True,                     # TF32 (Ampere+, calculs internes)

    # ─── Logging ───
    logging_dir="./logs",
    logging_steps=50,
    report_to="tensorboard",         # "none" / "tensorboard" / "wandb"

    # ─── Optimisation mémoire ───
    dataloader_num_workers=4,
    group_by_length=True,            # Regroupe par longueur → moins de padding
    # gradient_checkpointing=True,   # Échange VRAM contre calcul

    # ─── Reproductibilité ───
    seed=42,
    data_seed=42,

    # ─── Hub ───
    push_to_hub=False,               # Pousser sur HF Hub après entraînement
    # hub_model_id="username/model", # ID du repo Hub
    # hub_token="hf_...",            # Token d'accès
)
```

---

## Évaluation et prédiction

```python
# Après l'entraînement

# Évaluer sur le set de test
eval_results = trainer.evaluate(eval_dataset=tokenized["test"])
print(eval_results)
# {'eval_loss': 0.1823, 'eval_accuracy': 0.9421, 'eval_f1': 0.9418, 'epoch': 3.0}

# Faire des prédictions (logits + labels)
predictions = trainer.predict(tokenized["test"])
print(f"Logits shape    : {predictions.predictions.shape}")  # [n_test, 2]
print(f"Labels shape    : {predictions.label_ids.shape}")    # [n_test]
print(f"Métriques       : {predictions.metrics}")

# Extraire les classes prédites
import numpy as np
predicted_classes = np.argmax(predictions.predictions, axis=-1)

# Matrice de confusion
from sklearn.metrics import classification_report, confusion_matrix
print(classification_report(
    predictions.label_ids,
    predicted_classes,
    target_names=["NÉGATIF", "POSITIF"]
))
```

---

## Sauvegarder et charger le meilleur modèle

```python
# Le Trainer sauvegarde automatiquement si load_best_model_at_end=True
# Mais on peut aussi sauvegarder manuellement

# Sauvegarder le modèle actuel
trainer.save_model("./best_model/")

# Le tokenizer aussi (important !)
tokenizer.save_pretrained("./best_model/")

# ─── Recharger pour l'inférence ───
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("./best_model/")
tokenizer = AutoTokenizer.from_pretrained("./best_model/")

# Pipeline de production
classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
)

textes = [
    "Ce film est absolument magnifique, je le recommande à tout le monde !",
    "Franchement décevant, je m'attendais à beaucoup mieux.",
    "Correct, sans plus. Quelques bonnes scènes mais trop de longueurs.",
]

for texte in textes:
    result = classifier(texte)[0]
    label = result["label"]
    score = result["score"]
    print(f"[{label:8s} {score:.1%}] {texte}")
```

---

## Pousser le modèle sur le Hub

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Méthode 1 : Pendant l'entraînement
training_args = TrainingArguments(
    output_dir="./results",
    push_to_hub=True,
    hub_model_id="mon-username/camembert-sentiment-allocine",
    hub_strategy="every_save",   # Pousser à chaque sauvegarde
    # hub_strategy="end",        # Ou seulement à la fin
)

# Méthode 2 : Après l'entraînement
trainer.push_to_hub(
    commit_message="Fine-tuned CamemBERT on Allocine sentiment",
    tags=["text-classification", "french", "sentiment-analysis"],
)

# Méthode 3 : Manuellement
model.push_to_hub("mon-username/camembert-sentiment-allocine")
tokenizer.push_to_hub("mon-username/camembert-sentiment-allocine")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page du modèle fine-tuné sur le Hub après `push_to_hub`, montrant : la model card auto-générée avec les hyperparamètres d'entraînement et les métriques d'évaluation, le widget d'inférence en ligne opérationnel, et le graphique de training loss dans l'onglet "Training metrics"
> **Expliquer :** Comment le Trainer génère automatiquement une model card avec toutes les informations d'entraînement, comment le widget d'inférence fonctionne (Inference API de HF), et pourquoi c'est important de documenter ses expériences (reproductibilité, partage avec l'équipe)

---

## Callbacks — Personnaliser le comportement

Les callbacks permettent d'intervenir à chaque étape de l'entraînement.

```python
from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
import torch

class CustomLogCallback(TrainerCallback):
    """Callback personnalisé pour logger des informations supplémentaires"""

    def on_train_begin(self, args, state, control, **kwargs):
        print(f"Début de l'entraînement : {state.max_steps} steps total")

    def on_epoch_begin(self, args, state, control, **kwargs):
        print(f"\n=== Epoch {state.epoch:.0f} / {args.num_train_epochs} ===")

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            lr = logs.get("learning_rate", 0)
            loss = logs["loss"]
            step = state.global_step
            print(f"Step {step:5d} | Loss: {loss:.4f} | LR: {lr:.2e}")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics:
            print(f"\nÉvaluation :")
            for key, value in metrics.items():
                print(f"  {key:30s} : {value:.4f}")

    def on_save(self, args, state, control, **kwargs):
        print(f"Checkpoint sauvegardé : step {state.global_step}")

    def on_train_end(self, args, state, control, **kwargs):
        print(f"\nEntraînement terminé ! Meilleur score : {state.best_metric:.4f}")


# Callback d'early stopping intégré
from transformers import EarlyStoppingCallback

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    compute_metrics=compute_metrics,
    callbacks=[
        CustomLogCallback(),
        EarlyStoppingCallback(
            early_stopping_patience=2,      # Arrêter si pas d'amélioration après 2 évals
            early_stopping_threshold=0.001, # Seuil minimum d'amélioration
        ),
    ],
)
```

---

## Entraînement multi-GPU avec `accelerate`

```bash
# Configurer accelerate (une seule fois)
accelerate config

# Lancer l'entraînement sur 2 GPU
accelerate launch --num_processes=2 train_script.py
```

```python
# train_script.py — compatible single GPU et multi-GPU
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,  # Par GPU : 16 × 2 GPU = 32 effectif
    gradient_accumulation_steps=1,
    fp16=True,
    # Le Trainer utilise automatiquement accelerate en multi-GPU
)
```

---

## Logging avec TensorBoard et WandB

```python
# ─── TensorBoard ───
training_args = TrainingArguments(
    output_dir="./results",
    report_to="tensorboard",
    logging_dir="./logs",
    logging_steps=50,
)

# Lancer TensorBoard
# tensorboard --logdir ./logs --port 6006

# ─── Weights & Biases ───
# pip install wandb && wandb login

training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",
    run_name="camembert-sentiment-allocine-v1",
)

import wandb
wandb.init(
    project="nlp-training",
    name="camembert-sentiment",
    config={
        "model": "camembert-base",
        "dataset": "allocine",
        "learning_rate": 2e-5,
        "epochs": 3,
    }
)
```

---

## Gradient Accumulation — Simuler de grands batches

```python
# Problème : batch_size=64 dépasse la VRAM disponible
# Solution : gradient_accumulation_steps=4 avec batch_size=16

# Batch effectif = per_device_train_batch_size × gradient_accumulation_steps × n_gpus
# = 16 × 4 × 1 = 64 (sur 1 GPU)

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,
    gradient_accumulation_steps=4,    # ← Accumule sur 4 mini-batches
    # Equivalent à batch_size=64 mais avec 4x moins de VRAM
)
```

---

## Récapitulatif de la pipeline complète

```python
# Template complet et réutilisable

def fine_tune_classifier(
    model_checkpoint: str,
    dataset_name: str,
    text_col: str,
    label_col: str,
    output_dir: str,
    num_labels: int,
    id2label: dict,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 2e-5,
):
    from datasets import load_dataset
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, DataCollatorWithPadding
    )
    import evaluate, numpy as np

    # Données
    raw = load_dataset(dataset_name)
    tok = AutoTokenizer.from_pretrained(model_checkpoint)

    tokenized = raw.map(
        lambda b: tok(b[text_col], truncation=True, max_length=256),
        batched=True, remove_columns=[text_col]
    ).rename_column(label_col, "labels")

    # Modèle
    model = AutoModelForSequenceClassification.from_pretrained(
        model_checkpoint, num_labels=num_labels, id2label=id2label,
        label2id={v: k for k, v in id2label.items()}
    )

    # Métriques
    acc = evaluate.load("accuracy")
    f1 = evaluate.load("f1")
    def metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {**acc.compute(predictions=preds, references=labels),
                **f1.compute(predictions=preds, references=labels, average="macro")}

    # Trainer
    args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=lr, eval_strategy="epoch",
        save_strategy="epoch", load_best_model_at_end=True,
        metric_for_best_model="f1", fp16=True,
    )
    trainer = Trainer(
        model=model, args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized.get("validation", tokenized.get("test")),
        tokenizer=tok,
        data_collator=DataCollatorWithPadding(tok),
        compute_metrics=metrics,
    )

    trainer.train()
    return trainer

# Utilisation
trainer = fine_tune_classifier(
    model_checkpoint="camembert-base",
    dataset_name="allocine",
    text_col="review",
    label_col="label",
    output_dir="./results/allocine-sentiment",
    num_labels=2,
    id2label={0: "NÉGATIF", 1: "POSITIF"},
)
```

---

## Suite du cours

Le module suivant ([03-peft-lora.md](./03-peft-lora.md)) présente les techniques de fine-tuning efficace (LoRA et QLoRA) qui permettent d'entraîner des LLMs de 7B+ paramètres sur un GPU de 8-16GB.
