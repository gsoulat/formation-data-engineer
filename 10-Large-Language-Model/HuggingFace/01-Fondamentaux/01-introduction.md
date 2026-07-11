# Introduction à l'écosystème Hugging Face

## Qu'est-ce que Hugging Face ?

Hugging Face est une entreprise et une plateforme open-source devenue le **centre névralgique du machine learning moderne**. Fondée en 2016, elle héberge aujourd'hui :

- Plus de **500 000 modèles** pré-entraînés
- Plus de **100 000 datasets**
- Des bibliothèques Python utilisées par des millions de développeurs
- Une communauté active de chercheurs et praticiens

L'idée centrale : **ne pas réinventer la roue**. Plutôt que d'entraîner un modèle de zéro (ce qui coûte des milliers d'euros en GPU), on part d'un modèle déjà entraîné et on l'adapte à son problème spécifique.

---

## Les bibliothèques de l'écosystème

### `transformers` — La bibliothèque principale

C'est le cœur de l'écosystème. Elle donne accès à des centaines d'architectures (BERT, GPT-2, T5, LLaMA, Mistral, Falcon...) via une API unifiée.

```python
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
```

**Ce qu'elle fait :**
- Charge des modèles pré-entraînés depuis le Hub ou en local
- Fournit des classes de haut niveau (`pipeline`) et bas niveau (`AutoModel`)
- Gère l'inférence et le fine-tuning
- Compatible PyTorch, TensorFlow et JAX

### `datasets` — Gestion des données

```python
from datasets import load_dataset, DatasetDict, Dataset
```

**Ce qu'elle fait :**
- Charge des datasets depuis le Hub (IMDB, SQuAD, COCO, etc.)
- Gère efficacement de très grands datasets (Arrow format, memory-mapped)
- Fournit des transformations vectorisées (`map`, `filter`, `sort`)

### `evaluate` — Métriques standardisées

```python
import evaluate
accuracy = evaluate.load("accuracy")
bleu = evaluate.load("bleu")
```

**Ce qu'elle fait :**
- Implémente des métriques standards (accuracy, F1, BLEU, ROUGE, etc.)
- Garantit la reproductibilité des évaluations
- Compatible avec le `Trainer`

### `accelerate` — Entraînement distribué simplifié

```python
from accelerate import Accelerator
accelerator = Accelerator()
```

**Ce qu'elle fait :**
- Abstrait les différences CPU/GPU/TPU/multi-GPU
- Permet de lancer le même code sur n'importe quelle infrastructure
- Utilisé en interne par le `Trainer`

### `peft` — Parameter-Efficient Fine-Tuning

```python
from peft import get_peft_model, LoraConfig
```

**Ce qu'elle fait :**
- Implémente LoRA, QLoRA, Prefix Tuning, Prompt Tuning
- Permet de fine-tuner des LLMs avec très peu de GPU
- Réduit la mémoire nécessaire de 90%+

### `huggingface_hub` — Interaction avec le Hub

```python
from huggingface_hub import HfApi, snapshot_download
```

**Ce qu'elle fait :**
- Upload/download de modèles et datasets
- Gestion des repositories
- CLI `huggingface-cli`

---

## Le Hugging Face Hub

Le Hub est une **plateforme collaborative** (similaire à GitHub mais pour les modèles ML) accessible à [huggingface.co](https://huggingface.co).

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page d'accueil du Hub (huggingface.co/models) avec les filtres sur la gauche (task, library, language) et quelques modèles populaires visibles
> **Expliquer :** La navigation par tâche (NLP, Vision, Audio), les filtres de langue, les badges "Trending", comment lire les stats d'un modèle (downloads/mois, likes), et la différence entre modèles de la communauté et modèles officiels (Meta, Google, Mistral AI, etc.)

---

### Anatomie d'une page modèle sur le Hub

Chaque modèle sur le Hub dispose d'une **Model Card** qui documente :

- **Intended uses** : cas d'usage prévus
- **Training data** : données d'entraînement
- **Evaluation results** : performances sur benchmarks
- **Limitations** : biais connus, cas limites
- **Carbon footprint** : empreinte carbone de l'entraînement

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page du modèle `bert-base-uncased` sur le Hub (huggingface.co/bert-base-uncased) en montrant : l'onglet Model Card, le bouton "Use this model", le widget d'inference en ligne, et l'onglet Files
> **Expliquer :** Comment lire une model card professionnelle, comment tester un modèle directement dans le navigateur sans écrire de code, et la structure des fichiers (config.json, tokenizer.json, pytorch_model.bin)

---

### Catégories de tâches sur le Hub

| Domaine | Tâches disponibles |
|---------|-------------------|
| NLP | Classification, NER, QA, Résumé, Traduction, Génération |
| Vision | Classification d'images, Détection d'objets, Segmentation |
| Audio | ASR (speech-to-text), Classification audio, Text-to-Speech |
| Multimodal | Image captioning, Visual QA, Document AI |

---

## Installation complète

### Installation minimale (CPU)

```bash
pip install transformers torch datasets evaluate
```

### Installation complète (développement)

```bash
# Environnement virtuel recommandé
python -m venv hf-env
source hf-env/bin/activate

# Bibliothèques core
pip install transformers[torch]   # Transformers + PyTorch
pip install datasets              # Gestion des données
pip install evaluate              # Métriques
pip install accelerate            # Entraînement optimisé
pip install peft                  # Fine-tuning efficace
pip install bitsandbytes          # Quantization (Linux/GPU only)
pip install sentence-transformers # Embeddings
pip install huggingface_hub       # CLI Hub

# Outils de développement
pip install jupyter ipywidgets    # Notebooks
pip install tqdm                  # Barres de progression
```

### Connexion au Hub

```bash
# Via CLI (recommandé)
huggingface-cli login
# Entrer votre token depuis huggingface.co/settings/tokens

# Ou via Python
from huggingface_hub import login
login(token="hf_votre_token_ici")  # Ne jamais commiter ce token !
```

### Vérification de l'installation

```python
# verification.py
import transformers
import torch
import datasets
import evaluate

print(f"transformers : {transformers.__version__}")
print(f"torch        : {torch.__version__}")
print(f"CUDA dispo   : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU          : {torch.cuda.get_device_name(0)}")
    print(f"VRAM         : {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
print(f"datasets     : {datasets.__version__}")
print(f"evaluate     : {evaluate.__version__}")
```

Sortie attendue (exemple sur une machine avec GPU) :
```
transformers : 4.41.0
torch        : 2.3.0
CUDA dispo   : True
GPU          : NVIDIA GeForce RTX 3090
VRAM         : 24.0 GB
datasets     : 2.19.0
evaluate     : 0.4.1
```

---

## Gestion du cache

Hugging Face télécharge et met en cache les modèles localement. Par défaut :

- **Linux/macOS** : `~/.cache/huggingface/hub/`
- **Windows** : `C:\Users\<user>\.cache\huggingface\hub\`

```python
import os

# Changer le dossier de cache
os.environ["HF_HOME"] = "/data/hf-cache"          # Cache global
os.environ["TRANSFORMERS_CACHE"] = "/data/models"  # Modèles uniquement
os.environ["HF_DATASETS_CACHE"] = "/data/datasets" # Datasets uniquement

# Toujours définir AVANT les imports huggingface
import transformers
```

```bash
# Voir la taille du cache
du -sh ~/.cache/huggingface/

# Lister les modèles en cache
huggingface-cli scan-cache

# Supprimer des révisions spécifiques du cache
huggingface-cli delete-cache
```

---

## Premier exemple complet

Voici un exemple minimal qui valide que tout fonctionne :

```python
# premier_exemple.py
from transformers import pipeline

# Chargement d'un pipeline de classification de sentiment
# Le modèle sera téléchargé automatiquement (~250MB la première fois)
classifier = pipeline(
    task="text-classification",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device=0  # GPU si disponible, sinon mettre -1 pour CPU
)

textes = [
    "I love this product, it's absolutely amazing!",
    "This is the worst experience I've ever had.",
    "The weather today is okay, nothing special.",
]

resultats = classifier(textes)

for texte, resultat in zip(textes, resultats):
    label = resultat["label"]
    score = resultat["score"]
    print(f"[{label:8s} {score:.2%}] {texte}")
```

Sortie attendue :
```
[POSITIVE 99.97%] I love this product, it's absolutely amazing!
[NEGATIVE 99.98%] This is the worst experience I've ever had.
[POSITIVE 56.43%] The weather today is okay, nothing special.
```

---

## Architecture Transformer — Rappel conceptuel

Les modèles Transformers reposent sur le mécanisme d'**attention** introduit dans "Attention Is All You Need" (Vaswani et al., 2017).

### Les trois grandes familles

| Architecture | Exemples | Usage principal |
|-------------|----------|----------------|
| **Encoder-only** | BERT, RoBERTa, CamemBERT | Classification, NER, QA extractif |
| **Decoder-only** | GPT-2, LLaMA, Mistral | Génération de texte, complétion |
| **Encoder-Decoder** | T5, BART, mBART | Traduction, résumé, QA génératif |

### Flux de traitement

```
Texte brut
    ↓
Tokenisation (mots → IDs numériques)
    ↓
Embedding (IDs → vecteurs denses)
    ↓
Couches d'attention (contextualisation)
    ↓
Tête de tâche (classification / génération / ...)
    ↓
Prédiction finale
```

---

## Points clés à retenir

1. **Ne pas entraîner de zéro** : toujours partir d'un modèle pré-entraîné du Hub
2. **Choisir la bonne architecture** : encoder pour comprendre, decoder pour générer
3. **Gérer le cache** : les modèles sont volumineux (100MB à plusieurs GB)
4. **Token HuggingFace** : nécessaire pour les modèles "gated" (LLaMA, Gemma...)
5. **GPU recommandé** : l'inférence CPU fonctionne mais est 10-100x plus lente

---

## Suite du cours

Le prochain module ([02-pipeline.md](./02-pipeline.md)) explore en détail la fonction `pipeline()` qui est le moyen le plus rapide d'utiliser un modèle Transformer pour une tâche donnée.
