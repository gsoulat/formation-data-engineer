# PEFT, LoRA et QLoRA — Fine-tuning efficace des LLMs

## Le problème du fine-tuning des LLMs

Un modèle comme LLaMA 3 8B possède **8 milliards de paramètres**. En FP32, stocker ces paramètres + gradients + états de l'optimizer (Adam) nécessite :

```
Paramètres (FP32)    : 8B × 4 bytes = 32 GB
Gradients (FP32)     : 8B × 4 bytes = 32 GB
Adam states (FP32)   : 8B × 8 bytes = 64 GB  (m + v pour chaque paramètre)
                                       ───────
Total                                = 128 GB  ← Hors de portée d'un GPU grand public
```

**LoRA réduit cela à ~16 GB** en ne mettant à jour qu'une infime fraction des paramètres.

---

## LoRA — Low-Rank Adaptation

### Principe mathématique

Au lieu de mettre à jour directement la matrice de poids W (n×m), LoRA injecte deux **matrices de petite dimension** A et B :

```
Mise à jour complète : W' = W + ΔW
LoRA               : W' = W + B × A

Où :
- W  est figé (frozen)
- A  : matrice (r × m), r << n  ← petite !
- B  : matrice (n × r), r << n  ← petite !
- ΔW = B × A est de rang r (faible rang)
```

**Exemple concret** :
- Matrice originale W : 4096 × 4096 = 16 777 216 paramètres
- LoRA avec r=16 : A (16×4096) + B (4096×16) = 131 072 paramètres
- **Réduction : 128x moins de paramètres à entraîner !**

```python
import torch
import torch.nn as nn

# Illustration du principe LoRA
class LoRALinear(nn.Module):
    def __init__(self, in_features, out_features, rank=16, alpha=32):
        super().__init__()
        self.original_weight = nn.Parameter(
            torch.randn(out_features, in_features),
            requires_grad=False  # FIGÉ
        )
        self.lora_A = nn.Parameter(torch.randn(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        self.scaling = alpha / rank  # Facteur de mise à l'échelle

        # Initialisation : B=0 donc ΔW=0 au départ (modèle intact)
        nn.init.kaiming_uniform_(self.lora_A)
        nn.init.zeros_(self.lora_B)

    def forward(self, x):
        # Calcul original + adaptation LoRA
        original = x @ self.original_weight.T
        lora_update = (x @ self.lora_A.T) @ self.lora_B.T
        return original + self.scaling * lora_update
```

---

## Installation PEFT

```bash
pip install peft
pip install bitsandbytes  # Pour QLoRA (quantization 4-bit)
pip install accelerate    # Pour l'entraînement optimisé
```

---

## LoRA avec la bibliothèque PEFT

### Fine-tuning d'un classifieur avec LoRA

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import get_peft_model, LoraConfig, TaskType
import torch

MODEL = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2)

# Vérifier les modules disponibles pour LoRA
# (il faut cibler les couches d'attention)
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        print(name)
# bert.encoder.layer.0.attention.self.query
# bert.encoder.layer.0.attention.self.key
# bert.encoder.layer.0.attention.self.value
# bert.encoder.layer.0.attention.output.dense
# ...

# Configuration LoRA
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,           # Tâche : classification de séquence
    r=16,                                  # Rang des matrices A et B
    lora_alpha=32,                         # Facteur d'échelle = alpha/r = 2
    target_modules=["query", "value"],     # Modules à adapter
    lora_dropout=0.1,                      # Dropout pour régularisation
    bias="none",                           # "none" / "all" / "lora_only"
    modules_to_save=["classifier"],        # Entraîner aussi la tête de classification
)

# Appliquer LoRA au modèle
peft_model = get_peft_model(model, lora_config)

# Comparer les paramètres
peft_model.print_trainable_parameters()
# trainable params: 887,042 || all params: 110,370,050 || trainable%: 0.8036
```

---

## QLoRA — Quantization + LoRA

QLoRA combine la quantization 4-bit (NF4) avec LoRA pour permettre le fine-tuning de modèles 7B+ sur un GPU de 8-16GB.

```
Modèle 7B en FP16     = 14 GB VRAM
Modèle 7B en NF4      = ~4 GB VRAM
+ adaptateurs LoRA    = ~1 GB VRAM
─────────────────────────────────
Total QLoRA (7B)      = ~5 GB VRAM  ← Fonctionne sur RTX 3080/4080 !
```

---

## Pipeline QLoRA complet pour instruction following

```python
# qlora_fine_tuning.py
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer  # pip install trl

# ─── 1. Configuration de la quantization ───
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# ─── 2. Charger le modèle en 4-bit ───
MODEL_ID = "mistralai/Mistral-7B-v0.1"  # Nécessite un token HF + accès

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"  # Important pour Causal LM

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

# ─── 3. Préparer le modèle pour le fine-tuning k-bit ───
model = prepare_model_for_kbit_training(model)
# Active le gradient checkpointing, désactive les caches

# ─── 4. Configuration LoRA ───
lora_config = LoraConfig(
    r=64,                           # Rang élevé pour plus d'expressivité
    lora_alpha=16,
    target_modules=[                # Modules Mistral à adapter
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

peft_model = get_peft_model(model, lora_config)
peft_model.print_trainable_parameters()
# trainable params: 41,943,040 || all params: 3,794,358,272 || trainable%: 1.11

# ─── 5. Dataset d'instruction following ───
# Format Alpaca : {"instruction": "...", "input": "...", "output": "..."}
dataset = load_dataset("tatsu-lab/alpaca", split="train[:5000]")

def format_alpaca(example):
    """Convertir en format prompt-completion"""
    if example["input"]:
        prompt = f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n"
    else:
        prompt = f"### Instruction:\n{example['instruction']}\n\n### Response:\n"
    return {"text": prompt + example["output"] + tokenizer.eos_token}

dataset = dataset.map(format_alpaca, remove_columns=dataset.column_names)

# ─── 6. TrainingArguments ───
training_args = TrainingArguments(
    output_dir="./results/mistral-qlora",
    num_train_epochs=1,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,   # Batch effectif = 4×4 = 16
    learning_rate=2e-4,
    optim="paged_adamw_32bit",       # Optimiseur adapté à bitsandbytes
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    save_strategy="epoch",
    logging_steps=25,
    bf16=True,                        # BF16 pour les calculs LoRA
    fp16=False,
    group_by_length=True,
    max_grad_norm=0.3,
    report_to="none",
)

# ─── 7. SFTTrainer ───
trainer = SFTTrainer(
    model=peft_model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    packing=False,
)

trainer.train()
```

---

## Modules cibles selon l'architecture

```python
# Chaque architecture a des noms de modules différents
# Voici les plus courants :

cibles_par_modele = {
    "bert/camembert": ["query", "value"],
    "roberta": ["query", "value"],
    "gpt2": ["c_attn"],  # Conv1D fusionnée Q+K+V
    "llama/mistral": ["q_proj", "v_proj"],  # ou aussi "k_proj", "o_proj"
    "llama (complet)": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "falcon": ["query_key_value"],
    "t5": ["q", "v"],
    "bloom": ["query_key_value"],
}

# Pour trouver les noms des modules d'un modèle :
def find_linear_module_names(model):
    """Retourne tous les noms de couches linéaires"""
    import re
    linear_modules = set()
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            # Extraire le nom du module (sans le préfixe du path complet)
            module_name = name.split(".")[-1]
            linear_modules.add(module_name)
    return list(linear_modules)

# Utilisation
module_names = find_linear_module_names(model)
print(f"Modules linéaires disponibles : {sorted(module_names)}")
```

---

## Sauvegarder et fusionner les adaptateurs LoRA

```python
from peft import PeftModel
import torch

# ─── Sauvegarder les adaptateurs LoRA (très léger !) ───
peft_model.save_pretrained("./lora-adapters/")
# Crée seulement 2 fichiers :
# - adapter_config.json   (~1 KB)
# - adapter_model.safetensors  (~quelques MB selon r)

# ─── Recharger le modèle de base + adaptateurs LoRA ───
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

model_with_lora = PeftModel.from_pretrained(
    base_model,
    "./lora-adapters/",
    is_trainable=False,  # Mode inférence
)

# ─── Fusionner les poids LoRA dans le modèle de base ───
# Utile pour l'inférence : un seul modèle, sans overhead PEFT
merged_model = model_with_lora.merge_and_unload()

# Sauvegarder le modèle fusionné
merged_model.save_pretrained("./merged-model/")
tokenizer.save_pretrained("./merged-model/")

print("Modèle fusionné prêt pour l'inférence !")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La comparaison dans `nvidia-smi` : fine-tuning complet d'un modèle 7B (VRAM insuffisante, erreur OOM) vs QLoRA du même modèle (VRAM < 10GB, entraînement en cours), illustrant l'apport concret de QLoRA
> **Expliquer :** Le principe de décomposition de rang faible (approximation de ΔW par BA), pourquoi initialiser B=0 (le modèle commence identique à la base), le choix du rang r (r=8 léger mais expressif, r=64 pour les tâches complexes), et l'importance de `prepare_model_for_kbit_training` (désactive les couches non-compatibles avec la propagation du gradient sur INT4)

---

## Hyperparamètres LoRA — Guide pratique

```python
# Guide pour choisir les hyperparamètres LoRA

"""
r (rang) :
  - r=4  : très léger, pour des ajustements mineurs de style
  - r=8  : bon équilibre pour la plupart des tâches
  - r=16 : standard, recommandé pour les tâches complexes
  - r=64 : pour les tâches très complexes ou les datasets larges

lora_alpha :
  - alpha/r = facteur d'échelle effectif
  - alpha=r*2 (ex: r=16, alpha=32) : facteur 2, souvent un bon départ
  - alpha=r   (ex: r=16, alpha=16) : facteur 1, plus conservateur

target_modules :
  - Commencer par ["q_proj", "v_proj"] (attention : Q et V)
  - Ajouter "k_proj", "o_proj" si performances insuffisantes
  - Ajouter les couches FFN pour plus d'expressivité

lora_dropout :
  - 0.0  : pas de dropout (datasets larges)
  - 0.05 : légère régularisation (défaut recommandé)
  - 0.1  : plus de régularisation (petits datasets)

learning_rate :
  - 1e-4 à 3e-4 pour LoRA (plus élevé que le fine-tuning complet)
  - Les adaptateurs LoRA partent de zéro → besoin d'un LR plus élevé
"""

# Configuration recommandée pour le fine-tuning instruction :
lora_config_instruction = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

# Configuration pour petits modèles de classification :
lora_config_classification = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["query", "value"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS,
    modules_to_save=["classifier"],
)
```

---

## Autres techniques PEFT

### Prefix Tuning

```python
from peft import PrefixTuningConfig, TaskType

config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,   # Nombre de tokens "virtuels" préfixant chaque couche
    encoder_hidden_size=512,
)
# Entraîne seulement les représentations des tokens préfixes
```

### Prompt Tuning

```python
from peft import PromptTuningConfig, PromptTuningInit

config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    prompt_tuning_init=PromptTuningInit.TEXT,
    num_virtual_tokens=8,
    prompt_tuning_init_text="Classify the sentiment of the following text:",
    tokenizer_name_or_path="gpt2",
)
# Entraîne seulement des tokens "soft" en entrée
```

### IA3

```python
from peft import IA3Config, TaskType

config = IA3Config(
    task_type=TaskType.CAUSAL_LM,
    target_modules=["k_proj", "v_proj", "down_proj"],
    feedforward_modules=["down_proj"],
)
# Encore plus léger que LoRA : seulement des vecteurs de pondération
```

---

## Comparaison des techniques PEFT

```python
# Résumé comparatif

techniques_peft = {
    "Full Fine-tuning": {
        "Paramètres entraînés": "100%",
        "VRAM 7B": "~128 GB (FP32) / ~60 GB (FP16)",
        "Performance": "Maximale",
        "Vitesse": "Lente",
    },
    "LoRA (r=16)": {
        "Paramètres entraînés": "~1%",
        "VRAM 7B": "~14 GB (FP16)",
        "Performance": "Quasi-maximale",
        "Vitesse": "Rapide",
    },
    "QLoRA (r=16, 4-bit)": {
        "Paramètres entraînés": "~1%",
        "VRAM 7B": "~5-8 GB",
        "Performance": "Très bonne",
        "Vitesse": "Modérée (quantization overhead)",
    },
    "Prefix Tuning": {
        "Paramètres entraînés": "~0.1%",
        "VRAM 7B": "~14 GB",
        "Performance": "Bonne",
        "Vitesse": "Très rapide",
    },
    "IA3": {
        "Paramètres entraînés": "~0.01%",
        "VRAM 7B": "~14 GB",
        "Performance": "Correcte",
        "Vitesse": "Très rapide",
    },
}

print(f"{'Technique':<20} {'Params':>10} {'VRAM 7B':>25} {'Perf':>20} {'Vitesse':>15}")
print("-" * 95)
for technique, details in techniques_peft.items():
    print(f"{technique:<20} {details['Paramètres entraînés']:>10} {details['VRAM 7B']:>25} {details['Performance']:>20} {details['Vitesse']:>15}")
```

---

## Exemple final — CamemBERT + LoRA pour la classification

```python
# Exemple complet et autonome (fonctionne avec un GPU 8GB)
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding
)
from peft import get_peft_model, LoraConfig, TaskType
import evaluate, numpy as np

# Config
MODEL = "camembert-base"
DATASET = "allocine"
OUTPUT_DIR = "./results/camembert-lora-allocine"

# Données
ds = load_dataset(DATASET)
tokenizer = AutoTokenizer.from_pretrained(MODEL)
tok = lambda b: tokenizer(b["review"], truncation=True, max_length=256)
tokenized = ds.map(tok, batched=True, remove_columns=["review"]).rename_column("label", "labels")

# Modèle + LoRA
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2)
lora_cfg = LoraConfig(
    task_type=TaskType.SEQ_CLS, r=8, lora_alpha=16,
    target_modules=["query", "value"], lora_dropout=0.1,
    modules_to_save=["classifier"],
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()

# Métriques
acc = evaluate.load("accuracy")
f1 = evaluate.load("f1")
def metrics(ep):
    preds = np.argmax(ep.predictions, axis=-1)
    return {**acc.compute(predictions=preds, references=ep.label_ids),
            **f1.compute(predictions=preds, references=ep.label_ids, average="binary")}

# Entraîner
args = TrainingArguments(
    output_dir=OUTPUT_DIR, num_train_epochs=3,
    per_device_train_batch_size=64, learning_rate=3e-4,
    eval_strategy="epoch", save_strategy="epoch",
    load_best_model_at_end=True, metric_for_best_model="f1",
    fp16=torch.cuda.is_available(), report_to="none",
)
Trainer(
    model=model, args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=metrics,
).train()

# Sauvegarder les adaptateurs LoRA
model.save_pretrained(f"{OUTPUT_DIR}/lora-adapters/")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/lora-adapters/")
print("Adaptateurs LoRA sauvegardés !")
```

---

## Suite du cours

Le module suivant ([../Embeddings/01-sentence-transformers.md](../Embeddings/01-sentence-transformers.md)) présente la bibliothèque `sentence-transformers` pour calculer des embeddings de phrases et effectuer de la recherche sémantique.
