# Charger un modèle — AutoModel et AutoTokenizer

## Du pipeline au modèle brut

Le `pipeline()` est pratique mais opaque. Pour comprendre et contrôler ce qui se passe, ou pour faire du fine-tuning, on doit travailler directement avec les classes `AutoModel` et `AutoTokenizer`.

```
pipeline("text-classification", model="bert")
    = AutoTokenizer.from_pretrained("bert")
    + AutoModelForSequenceClassification.from_pretrained("bert")
    + logique de pré/post-traitement
```

---

## La famille `Auto*`

Hugging Face fournit des classes `Auto*` qui **détectent automatiquement** l'architecture correcte en lisant le fichier `config.json` du modèle.

```python
from transformers import (
    AutoTokenizer,
    AutoModel,                          # Modèle de base (sorties brutes)
    AutoModelForSequenceClassification, # + tête de classification
    AutoModelForTokenClassification,    # + tête NER
    AutoModelForQuestionAnswering,      # + tête QA
    AutoModelForCausalLM,               # + tête génération (GPT-style)
    AutoModelForSeq2SeqLM,              # + tête encoder-decoder (T5-style)
    AutoModelForMaskedLM,               # + tête fill-mask (BERT-style)
)
```

---

## Charger un modèle pas-à-pas

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

# 1. Charger le tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# 2. Charger le modèle
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# 3. Inspecter le modèle
print(f"Architecture : {type(model).__name__}")
print(f"Config       : {model.config.model_type}")
print(f"Nombre labels: {model.config.num_labels}")
print(f"Labels       : {model.config.id2label}")

# 4. Compter les paramètres
n_params = sum(p.numel() for p in model.parameters())
n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Paramètres   : {n_params:,} total, {n_trainable:,} entraînables")
# Paramètres   : 66,955,010 total, 66,955,010 entraînables
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La sortie de `print(model)` dans un terminal/notebook, montrant l'arborescence complète du modèle DistilBERT (DistilBertModel → Embeddings → Transformer → layers → attention → etc.)
> **Expliquer :** Comment lire l'architecture d'un modèle PyTorch, la signification de chaque sous-module (Embeddings, TransformerBlock, MultiHeadSelfAttention, FFN), et que la "tête" de classification est la dernière couche linéaire

---

## Naviguer sur le Hub pour choisir un modèle

```python
from huggingface_hub import HfApi, list_models

api = HfApi()

# Chercher des modèles pour une tâche spécifique
models = list(list_models(
    task="text-classification",
    language="fr",                  # Modèles français
    sort="downloads",               # Trier par popularité
    limit=10,
))

for m in models:
    print(f"{m.downloads:>10,} downloads | {m.id}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page de recherche du Hub (huggingface.co/models) filtrée sur "text-classification" + "French" avec les modèles triés par téléchargements, montrant CamemBERT, RoBERTa-FR, etc.
> **Expliquer :** Comment filtrer par tâche, langue et librairie sur le Hub, comment lire la Model Card pour évaluer si un modèle convient (données d'entraînement, métriques), et comment utiliser le widget d'inférence en ligne pour tester sans coder

---

## `from_pretrained` — Options avancées

```python
from transformers import AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",

    # Précision numérique (économise la VRAM)
    torch_dtype=torch.float16,       # FP16 : divise la VRAM par 2
    # torch_dtype=torch.bfloat16,    # BF16 : plus stable numériquement

    # Distribution multi-GPU
    device_map="auto",               # Répartit automatiquement sur les GPU disponibles
    # device_map={"": "cuda:0"},     # Forcer un GPU spécifique

    # Ignorer les poids manquants/inattendus (pour le fine-tuning)
    ignore_mismatched_sizes=True,    # Utile si on change le nombre de labels

    # Charger en mémoire basse (gradient checkpointing)
    # low_cpu_mem_usage=True,        # Réduit la RAM CPU pendant le chargement

    # Cache
    cache_dir="/data/hf-cache",      # Dossier de cache personnalisé
    force_download=False,            # Ne pas retélécharger si en cache
    local_files_only=False,          # Forcer l'utilisation locale (mode offline)
)
```

### Mode offline

```python
import os

# Désactiver complètement les connexions réseau HF
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

# Le modèle DOIT être en cache local
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
```

---

## Charger depuis un dossier local

```python
# Sauvegarder modèle + tokenizer
model.save_pretrained("./mon-modele/")
tokenizer.save_pretrained("./mon-modele/")

# Structure créée :
# ./mon-modele/
# ├── config.json
# ├── tokenizer_config.json
# ├── tokenizer.json
# ├── vocab.txt
# ├── special_tokens_map.json
# └── model.safetensors  (ou pytorch_model.bin pour les anciens)

# Recharger depuis local
model = AutoModelForSequenceClassification.from_pretrained("./mon-modele/")
tokenizer = AutoTokenizer.from_pretrained("./mon-modele/")
```

### Format SafeTensors vs PyTorch Bin

```python
# SafeTensors (format recommandé depuis 2023)
# - Plus rapide à charger
# - Plus sécurisé (pas d'exécution de code arbitraire)
# - Extension .safetensors

# PyTorch Bin (format historique)
# - Basé sur pickle (risque de sécurité)
# - Extension .bin

# Sauvegarder en SafeTensors (défaut dans les nouvelles versions)
model.save_pretrained("./mon-modele/", safe_serialization=True)

# Forcer le format PyTorch Bin (compatibilité)
model.save_pretrained("./mon-modele/", safe_serialization=False)
```

---

## Inspecter la configuration d'un modèle

```python
from transformers import AutoConfig

# Charger uniquement la config (sans les poids = instantané)
config = AutoConfig.from_pretrained("bert-base-uncased")

print(f"Architecture : {config.model_type}")
print(f"Couches      : {config.num_hidden_layers}")
print(f"Attention    : {config.num_attention_heads} têtes")
print(f"Taille hidden: {config.hidden_size}")
print(f"Vocab size   : {config.vocab_size}")
print(f"Max position : {config.max_position_embeddings}")
```

Sortie :
```
Architecture : bert
Couches      : 12
Attention    : 12 têtes
Taille hidden: 768
Vocab size   : 30522
Max position : 512
```

### Comparer les tailles de modèles populaires

```python
from transformers import AutoConfig

modeles = {
    "DistilBERT-base"     : "distilbert-base-uncased",
    "BERT-base"           : "bert-base-uncased",
    "BERT-large"          : "bert-large-uncased",
    "RoBERTa-base"        : "roberta-base",
    "GPT-2 small"         : "gpt2",
    "GPT-2 medium"        : "gpt2-medium",
    "T5-small"            : "t5-small",
    "T5-base"             : "t5-base",
}

print(f"{'Modèle':<22} {'Couches':>8} {'Hidden':>8} {'Têtes':>8} {'Vocab':>8}")
print("-" * 58)
for nom, model_id in modeles.items():
    try:
        cfg = AutoConfig.from_pretrained(model_id)
        layers = getattr(cfg, "num_hidden_layers", getattr(cfg, "num_layers", "?"))
        hidden = getattr(cfg, "hidden_size", getattr(cfg, "d_model", "?"))
        heads  = getattr(cfg, "num_attention_heads", "?")
        vocab  = getattr(cfg, "vocab_size", "?")
        print(f"{nom:<22} {layers:>8} {hidden:>8} {heads:>8} {vocab:>8}")
    except Exception as e:
        print(f"{nom:<22} Erreur: {e}")
```

---

## Charger un modèle pour une tâche différente de celle d'origine

Cas fréquent : prendre BERT (entraîné sur fill-mask) et l'adapter à la classification.

```python
from transformers import AutoModelForSequenceClassification
import torch

# BERT-base n'a pas de tête de classification → HF en crée une aléatoire
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=3,  # Votre nombre de classes
    # id2label={0: "NÉGATIF", 1: "NEUTRE", 2: "POSITIF"},
    # label2id={"NÉGATIF": 0, "NEUTRE": 1, "POSITIF": 2},
)

# Warning attendu :
# "Some weights of BertForSequenceClassification were not initialized
#  from the model checkpoint: ['classifier.bias', 'classifier.weight']
#  You should probably TRAIN this model on a down-stream task..."
# → C'est NORMAL : la tête de classification est nouvelle

print(f"Labels : {model.config.id2label}")
```

---

## Pousser un modèle sur le Hub

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from huggingface_hub import login

# Se connecter
login()  # Entrer le token HF

# Charger/fine-tuner votre modèle
model = AutoModelForSequenceClassification.from_pretrained("./mon-modele-fine-tune/")
tokenizer = AutoTokenizer.from_pretrained("./mon-modele-fine-tune/")

# Pousser sur le Hub
model.push_to_hub("mon-username/mon-modele-sentiment-fr")
tokenizer.push_to_hub("mon-username/mon-modele-sentiment-fr")

# Le modèle est maintenant accessible publiquement !
# huggingface.co/mon-username/mon-modele-sentiment-fr
```

---

## Modèles à accès restreint (Gated Models)

Certains modèles (LLaMA, Gemma, Mistral Instruct) requièrent d'**accepter les conditions d'utilisation** sur le Hub avant de pouvoir être téléchargés.

```python
# 1. Aller sur la page du modèle (ex: meta-llama/Meta-Llama-3-8B)
# 2. Cliquer "Agree and access repository"
# 3. Se connecter avec son token HF

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Nécessite d'être connecté ET d'avoir accepté les CGU du modèle
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    token="hf_votre_token"  # ou variable d'env HF_TOKEN
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    token="hf_votre_token"
)
```

---

## Points clés à retenir

| Classe | Usage |
|--------|-------|
| `AutoTokenizer` | Toujours l'utiliser pour charger le tokenizer |
| `AutoModel` | Sorties brutes (hidden states) sans tête de tâche |
| `AutoModelForSequenceClassification` | Classification de texte |
| `AutoModelForTokenClassification` | NER, POS tagging |
| `AutoModelForQuestionAnswering` | QA extractif |
| `AutoModelForCausalLM` | Génération de texte (GPT-style) |
| `AutoModelForSeq2SeqLM` | Traduction, résumé (T5-style) |

---

## Suite du cours

Le prochain module ([02-inference.md](./02-inference.md)) explique comment effectuer une inférence manuelle (forward pass) avec les modèles chargés, interpréter les logits, utiliser l'attention, et générer du texte avec les stratégies d'échantillonnage avancées.
