# Préparer un dataset — `map()`, `filter()` et DataCollator

## Vue d'ensemble

La préparation d'un dataset pour le fine-tuning suit toujours la même pipeline :

```
Dataset brut (texte + labels)
    ↓ filter()            — Supprimer les exemples non valides
    ↓ map(tokenize)       — Tokeniser les textes
    ↓ remove_columns()    — Supprimer les colonnes inutiles
    ↓ set_format("torch") — Convertir en tenseurs PyTorch
    ↓ DataCollator        — Créer des batches homogènes
    ↓ DataLoader          — Itérer pendant l'entraînement
```

---

## `map()` — Transformation vectorisée

`map()` applique une fonction à chaque exemple (ou batch d'exemples) du dataset. C'est l'opération de transformation principale.

### Utilisation basique

```python
from datasets import load_dataset

dataset = load_dataset("stanfordnlp/imdb", split="train[:1000]")

# Fonction appliquée à chaque exemple (dict → dict)
def add_text_length(example):
    example["length"] = len(example["text"])
    return example

# Appliquer la transformation
dataset_with_length = dataset.map(add_text_length)

print(dataset_with_length.column_names)
# ['text', 'label', 'length']

print(dataset_with_length[0]["length"])
print(dataset_with_length.features)
```

### Mode batched (beaucoup plus rapide)

```python
# batched=True : la fonction reçoit un dict de LISTES plutôt qu'un dict de valeurs
def add_text_length_batched(batch):
    batch["length"] = [len(text) for text in batch["text"]]
    return batch

dataset_fast = dataset.map(
    add_text_length_batched,
    batched=True,
    batch_size=256,   # Taille des batches (défaut : 1000)
    num_proc=4,       # Paralléliser sur 4 cœurs CPU
)
```

---

## Tokenisation avec `map()`

C'est l'usage le plus courant de `map()` : tokeniser tous les textes.

```python
from datasets import load_dataset
from transformers import AutoTokenizer

# Charger le dataset et le tokenizer
dataset = load_dataset("stanfordnlp/imdb")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Fonction de tokenisation
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding=False,       # Pas de padding ici (le DataCollator s'en charge)
        truncation=True,
        max_length=512,
    )

# Appliquer à tous les splits en une fois
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    batch_size=256,
    num_proc=4,
    remove_columns=["text"],  # Supprimer la colonne texte brut (inutile après tokenisation)
    desc="Tokenisation",      # Description de la barre de progression
)

print(tokenized_dataset)
print(tokenized_dataset["train"].features)
# {
#   'label': ClassLabel(names=['neg', 'pos']),
#   'input_ids': Sequence(Value('int32')),
#   'attention_mask': Sequence(Value('int8'))
# }
```

---

## `filter()` — Supprimer des exemples

```python
from datasets import load_dataset

dataset = load_dataset("stanfordnlp/imdb", split="train")

print(f"Avant : {len(dataset)} exemples")

# Supprimer les textes trop courts (bruit)
dataset_filtered = dataset.filter(
    lambda example: len(example["text"]) >= 50
)
print(f"Après (texte >= 50 chars) : {len(dataset_filtered)} exemples")

# Mode batched pour la performance
def filter_by_length(batch):
    return [len(text) >= 50 and len(text) <= 5000 for text in batch["text"]]

dataset_clean = dataset.filter(
    filter_by_length,
    batched=True,
    batch_size=512,
    num_proc=4,
)
print(f"Après (50 <= len <= 5000) : {len(dataset_clean)} exemples")
```

---

## Transformation de labels

```python
from datasets import load_dataset, ClassLabel

dataset = load_dataset("allocine")

# Renommer les labels pour plus de clarté
label_map = {0: "NÉGATIF", 1: "POSITIF"}

def rename_labels(example):
    example["label_str"] = label_map[example["label"]]
    return example

dataset = dataset.map(rename_labels)

# Ou redéfinir le type de feature
new_features = dataset["train"].features.copy()
new_features["label"] = ClassLabel(names=["NÉGATIF", "POSITIF"])
dataset = dataset.cast(new_features)  # Recast sans modifier les valeurs

# Vérification
print(dataset["train"].features["label"].int2str(0))  # "NÉGATIF"
print(dataset["train"].features["label"].int2str(1))  # "POSITIF"
```

---

## Préparer un dataset pour la classification

Pipeline complet de classification de sentiment :

```python
from datasets import load_dataset, DatasetDict
from transformers import AutoTokenizer

# ─── 1. Charger et diviser ───
raw_dataset = load_dataset("allocine")

# Créer un split validation
train_val = raw_dataset["train"].train_test_split(test_size=0.1, seed=42)
dataset = DatasetDict({
    "train"     : train_val["train"],
    "validation": train_val["test"],
    "test"      : raw_dataset["test"],
})

print(f"Train      : {len(dataset['train'])} exemples")
print(f"Validation : {len(dataset['validation'])} exemples")
print(f"Test       : {len(dataset['test'])} exemples")

# ─── 2. Initialiser le tokenizer ───
MODEL_CHECKPOINT = "camembert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)

# ─── 3. Tokeniser ───
def tokenize(batch):
    return tokenizer(
        batch["review"],   # Colonne texte dans Allocine
        truncation=True,
        max_length=256,    # Réduire pour accélérer l'entraînement
        padding=False,     # DataCollator s'en charge
    )

tokenized = dataset.map(
    tokenize,
    batched=True,
    batch_size=256,
    num_proc=4,
    remove_columns=["review"],  # Supprimer le texte brut
    desc="Tokenisation",
)

# ─── 4. Renommer la colonne label (convention Trainer) ───
# Le Trainer attend une colonne "labels" (pas "label")
tokenized = tokenized.rename_column("label", "labels")

# ─── 5. Convertir au format PyTorch ───
tokenized.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "labels"]
)

print(tokenized)
print(f"\nExemple tokenisé : {tokenized['train'][0]}")
```

---

## DataCollator — Créer des batches homogènes

Le `DataCollator` assemble les exemples individuels en batches en gérant le padding dynamique.

### `DataCollatorWithPadding` — Pour la classification

```python
from transformers import AutoTokenizer, DataCollatorWithPadding
from torch.utils.data import DataLoader

tokenizer = AutoTokenizer.from_pretrained("camembert-base")

# DataCollator qui pad dynamiquement à la longueur max du batch
data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    padding=True,         # "longest" : pad à la longueur max du batch
    pad_to_multiple_of=8, # Pour les GPU Tensor Core (A100, V100...) : multiple de 8
    return_tensors="pt",  # PyTorch tensors
)

# Utilisation avec DataLoader
train_dataloader = DataLoader(
    tokenized["train"],
    batch_size=32,
    shuffle=True,
    collate_fn=data_collator,
)

# Vérifier un batch
batch = next(iter(train_dataloader))
print(f"input_ids shape    : {batch['input_ids'].shape}")     # [32, max_len_in_batch]
print(f"attention_mask shape: {batch['attention_mask'].shape}")
print(f"labels shape       : {batch['labels'].shape}")         # [32]

# Avantage du padding dynamique :
# - Pas de padding inutile si les séquences sont courtes
# - Chaque batch a sa propre longueur max → moins de calcul
```

### `DataCollatorForSeq2Seq` — Pour la traduction/résumé

```python
from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-fr-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,                      # Pour préparer decoder_input_ids
    padding=True,
    label_pad_token_id=-100,          # -100 = ignoré dans le calcul de la loss
    return_tensors="pt",
)
```

### `DataCollatorForLanguageModeling` — Pour le fine-tuning de LLM

```python
from transformers import AutoTokenizer, DataCollatorForLanguageModeling

tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # GPT-2 n'a pas de pad token

# Pour le Causal LM (GPT-style) : mlm=False
data_collator_clm = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # Causal LM : les labels sont les input_ids décalés d'un token
)

# Pour le Masked LM (BERT-style) : mlm=True
data_collator_mlm = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15,  # 15% des tokens seront masqués (comme BERT)
)
```

---

## Pipeline complet avec `DataCollatorForSeq2Seq`

```python
from datasets import load_dataset
from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM
from torch.utils.data import DataLoader

# Traduction EN → FR avec Helsinki NLP
MODEL = "Helsinki-NLP/opus-mt-en-fr"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)

# Charger un petit dataset de traduction
raw = load_dataset("Helsinki-NLP/tatoeba_mt", "eng-fra", split="test[:500]")
print(raw.column_names)  # ['id', 'sourceString', 'targetString', ...]

def preprocess_translation(batch):
    # Tokeniser les sources (anglais)
    model_inputs = tokenizer(
        batch["sourceString"],
        max_length=128,
        truncation=True,
        padding=False,
    )
    # Tokeniser les cibles (français) → deviennent les labels
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            batch["targetString"],
            max_length=128,
            truncation=True,
            padding=False,
        )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_pairs = raw.map(
    preprocess_translation,
    batched=True,
    remove_columns=raw.column_names,
)

data_collator = DataCollatorForSeq2Seq(
    tokenizer, model=model, padding=True, return_tensors="pt"
)

dataloader = DataLoader(tokenized_pairs, batch_size=8, collate_fn=data_collator)
batch = next(iter(dataloader))

print(f"input_ids  : {batch['input_ids'].shape}")
print(f"labels     : {batch['labels'].shape}")
# -100 dans labels = tokens de padding ignorés dans le calcul de la loss
print(f"Labels[0]  : {batch['labels'][0][:10]}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un notebook montrant un batch avant et après passage dans le DataCollatorWithPadding : d'abord des séquences de longueurs différentes (ex: [15, 42, 8, 73]), puis le batch final où toutes ont la même longueur (73) avec les 0 de padding visibles dans `attention_mask`
> **Expliquer :** Pourquoi on préfère le padding dynamique (plus efficace que le padding à 512 pour tous), le rôle crucial du `attention_mask` (dire au modèle d'ignorer les tokens de padding), et comment `-100` dans les labels dit à la loss de ne pas pénaliser les prédictions sur les tokens paddés

---

## Mise en cache des transformations

`map()` met automatiquement en cache les résultats. Si on relance le script sans modifier la fonction, les résultats sont chargés depuis le cache.

```python
import os
from datasets import load_dataset
from transformers import AutoTokenizer

# Le cache est dans ~/.cache/huggingface/datasets/
dataset = load_dataset("stanfordnlp/imdb", split="train")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, max_length=512)

# Premier appel : exécute la tokenisation et sauvegarde en cache
tokenized = dataset.map(tokenize, batched=True)

# Deuxième appel : charge depuis le cache (instantané !)
tokenized_again = dataset.map(tokenize, batched=True)

# Désactiver le cache si on développe et modifie souvent la fonction
tokenized_no_cache = dataset.map(tokenize, batched=True, load_from_cache_file=False)
```

---

## Gestion des datasets déséquilibrés

```python
from datasets import load_dataset
import numpy as np

dataset = load_dataset("stanfordnlp/imdb", split="train")
labels = dataset["label"]

# Analyser le déséquilibre
from collections import Counter
counts = Counter(labels)
total = len(labels)
for label, count in sorted(counts.items()):
    print(f"Label {label}: {count} exemples ({count/total:.1%})")

# Stratégie 1 : Sous-échantillonnage (undersampling)
# Garder seulement N exemples par classe
N = 5000
indices_0 = [i for i, l in enumerate(labels) if l == 0][:N]
indices_1 = [i for i, l in enumerate(labels) if l == 1][:N]
balanced_dataset = dataset.select(indices_0 + indices_1).shuffle(seed=42)

# Stratégie 2 : Pondération des classes dans la loss
import torch
label_counts = torch.tensor([counts[0], counts[1]], dtype=torch.float)
class_weights = 1.0 / label_counts
class_weights = class_weights / class_weights.sum()
print(f"Poids de classes : {class_weights}")
# À passer à la loss : CrossEntropyLoss(weight=class_weights)
```

---

## Vérifications finales avant entraînement

```python
from transformers import AutoTokenizer, DataCollatorWithPadding
from torch.utils.data import DataLoader
import torch

def validate_dataset(tokenized_dataset, tokenizer, batch_size=4):
    """Vérifie qu'un dataset est correctement préparé pour l'entraînement"""

    collator = DataCollatorWithPadding(tokenizer, return_tensors="pt")
    loader = DataLoader(tokenized_dataset, batch_size=batch_size, collate_fn=collator)
    batch = next(iter(loader))

    print("=== Validation du dataset ===")
    for key, value in batch.items():
        print(f"  {key:20s} : shape={value.shape}, dtype={value.dtype}, min={value.min()}, max={value.max()}")

    # Vérifications critiques
    assert "input_ids" in batch, "input_ids manquant !"
    assert "attention_mask" in batch, "attention_mask manquant !"
    assert batch["input_ids"].dtype in (torch.long, torch.int32, torch.int64), "input_ids doit être de type entier"
    assert batch["attention_mask"].max() == 1 and batch["attention_mask"].min() == 0, "attention_mask doit être 0/1"

    if "labels" in batch:
        print(f"  Labels uniques : {batch['labels'].unique().tolist()}")

    print("\n✓ Dataset prêt pour l'entraînement")
    return batch

# Utilisation
batch = validate_dataset(tokenized["train"], tokenizer)
```

---

## Résumé de la pipeline de préparation

```python
# Template complet réutilisable
from datasets import load_dataset, DatasetDict
from transformers import AutoTokenizer, DataCollatorWithPadding
from torch.utils.data import DataLoader

def prepare_classification_dataset(
    dataset_name: str,
    model_checkpoint: str,
    text_column: str,
    label_column: str,
    max_length: int = 256,
    test_size: float = 0.1,
    batch_size: int = 32,
    seed: int = 42,
):
    # 1. Charger
    raw = load_dataset(dataset_name)
    train_val = raw["train"].train_test_split(test_size=test_size, seed=seed)
    dataset = DatasetDict({
        "train"     : train_val["train"],
        "validation": train_val["test"],
        "test"      : raw["test"],
    })

    # 2. Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

    # 3. Tokeniser
    def tokenize(batch):
        return tokenizer(batch[text_column], truncation=True, max_length=max_length)

    tokenized = dataset.map(tokenize, batched=True, remove_columns=[text_column])

    # 4. Renommer labels
    if label_column != "labels":
        tokenized = tokenized.rename_column(label_column, "labels")

    # 5. Format PyTorch
    tokenized.set_format("torch")

    # 6. DataCollator
    collator = DataCollatorWithPadding(tokenizer, return_tensors="pt")

    # 7. DataLoaders
    loaders = {
        split: DataLoader(
            tokenized[split],
            batch_size=batch_size,
            shuffle=(split == "train"),
            collate_fn=collator,
        )
        for split in tokenized.keys()
    }

    return tokenized, loaders, tokenizer

# Utilisation
tokenized, loaders, tokenizer = prepare_classification_dataset(
    dataset_name="allocine",
    model_checkpoint="camembert-base",
    text_column="review",
    label_column="label",
    max_length=256,
    batch_size=32,
)

print(f"Train batches : {len(loaders['train'])}")
print(f"Val batches   : {len(loaders['validation'])}")
```

---

## Suite du cours

Le module suivant ([../Fine-Tuning/01-introduction.md](../Fine-Tuning/01-introduction.md)) présente les stratégies de fine-tuning : quand fine-tuner, la différence entre fine-tuning complet et PEFT, et les critères pour choisir le bon modèle de base.
