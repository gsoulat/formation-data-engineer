# Introduction au Fine-Tuning — Stratégies et concepts

## Qu'est-ce que le fine-tuning ?

Les modèles pré-entraînés (BERT, GPT, LLaMA...) ont appris des **représentations génériques** de la langue sur d'immenses corpus. Ils sont excellents pour comprendre la langue mais ne connaissent pas votre domaine spécifique ni votre tâche précise.

Le **fine-tuning** consiste à continuer l'entraînement d'un modèle pré-entraîné sur vos propres données, pour l'adapter à votre cas d'usage.

```
Modèle pré-entraîné (général)
        ↓ fine-tuning (vos données)
Modèle spécialisé (votre domaine/tâche)
```

---

## Quand fine-tuner ?

| Situation | Approche recommandée |
|-----------|---------------------|
| Tâche standard (sentiment, NER, QA) | Fine-tuning d'un modèle existant |
| Domaine très spécialisé (médical, juridique) | Fine-tuning avec données domaine |
| Peu de données labellisées (<100) | Zero-shot ou few-shot avec LLM |
| Beaucoup de données (>10K) | Fine-tuning complet |
| Ressources limitées (GPU < 16GB) | PEFT (LoRA, QLoRA) |
| Prototype rapide | Pipeline HF sans fine-tuning |
| Instruction following personnalisé | Fine-tuning instructif (SFT) |

**Règle d'or** : avant de fine-tuner, **tester un modèle existant** sur votre tâche. Si les performances sont suffisantes, inutile de fine-tuner.

---

## Le transfer learning en pratique

```
Corpus Wikipedia + Books (pré-entraînement)
        ↓ 100 milliards de tokens, des semaines de calcul
Modèle BERT (12 couches, 110M paramètres)
        ↓ Vos 10 000 critiques produits, quelques minutes
Classifieur de sentiment pour votre e-commerce
```

**Ce qui change lors du fine-tuning :**
- Les poids des couches d'encodage sont légèrement ajustés
- Une nouvelle "tête" de classification est entraînée depuis zéro
- Le modèle apprend le vocabulaire et les patterns de votre domaine

---

## Fine-tuning complet vs PEFT

### Fine-tuning complet (Full Fine-Tuning)

```
Tous les paramètres sont mis à jour
→ Meilleure performance potentielle
→ Coût : GPU puissant, risque d'oubli catastrophique
```

```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# TOUS les paramètres sont entraînables par défaut
n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Paramètres entraînables : {n_trainable:,}")  # 109,483,778 (BERT)
```

### PEFT — Parameter-Efficient Fine-Tuning

```
Seule une petite fraction des paramètres est mise à jour
→ Performance quasi-équivalente au fine-tuning complet
→ Coût : beaucoup moins de VRAM, plus rapide
```

```python
from peft import get_peft_model, LoraConfig

config = LoraConfig(r=16, lora_alpha=32, target_modules=["query", "value"])
peft_model = get_peft_model(model, config)

n_trainable = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
n_total = sum(p.numel() for p in peft_model.parameters())
print(f"Paramètres entraînables : {n_trainable:,} ({n_trainable/n_total:.1%})")
# Paramètres entraînables : 884,736 (0.81%)  ← 100x moins !
```

---

## Choisir le bon modèle de base

### Pour les tâches de compréhension (classification, NER, QA extractif)

| Modèle | Langue | Paramètres | Notes |
|--------|--------|-----------|-------|
| `bert-base-uncased` | EN | 110M | Référence absolue |
| `bert-large-uncased` | EN | 340M | Plus puissant, plus lent |
| `distilbert-base-uncased` | EN | 66M | 40% plus léger que BERT |
| `roberta-base` | EN | 125M | Meilleur que BERT |
| `camembert-base` | FR | 110M | Référence pour le français |
| `camembert-large` | FR | 340M | Plus puissant |
| `xlm-roberta-base` | 100 langues | 270M | Multilingue |
| `flaubert/flaubert_base_cased` | FR | 137M | Alternative CamemBERT |

### Pour les tâches de génération (chat, résumé, traduction)

| Modèle | Langue | Paramètres | Notes |
|--------|--------|-----------|-------|
| `gpt2` | EN | 117M | Petit, pour apprendre |
| `facebook/bart-large` | EN | 400M | Résumé, traduction |
| `t5-base` | EN | 250M | Polyvalent (seq2seq) |
| `mistralai/Mistral-7B-v0.1` | EN | 7B | SOTA open source |
| `meta-llama/Meta-Llama-3-8B` | EN | 8B | Très bon modèle |
| `bofenghuang/vigogne-2-7b-instruct` | FR | 7B | LLaMA2 en français |

---

## L'oubli catastrophique

Problème majeur du fine-tuning complet : en apprenant une nouvelle tâche, le modèle peut **oublier** ce qu'il savait avant.

```python
# Visualiser l'oubli catastrophique
import torch
from transformers import AutoModelForSequenceClassification

# Charger le modèle
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# Sauvegarder les poids AVANT fine-tuning
weights_before = {
    name: param.data.clone()
    for name, param in model.named_parameters()
}

# ... fine-tuning ...

# Comparer les poids APRÈS fine-tuning
weights_after = {
    name: param.data
    for name, param in model.named_parameters()
}

print("Variation des poids par couche :")
for name in list(weights_before.keys())[:5]:
    delta = (weights_after[name] - weights_before[name]).abs().mean().item()
    print(f"  {name:50s} : Δ = {delta:.6f}")
```

**Solutions :**
1. **Taux d'apprentissage très petit** (1e-5 à 5e-5 pour BERT)
2. **Learning rate scheduler** (warmup + decay)
3. **PEFT/LoRA** : les poids originaux restent gelés
4. **Early stopping** : arrêter dès que la validation ne s'améliore plus

---

## Stratégies de taux d'apprentissage

```python
from transformers import AutoModelForSequenceClassification, AdamW
from transformers import get_linear_schedule_with_warmup
import torch

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

# ─── Learning Rate Différencié par Couche ───
# Les couches du bas (tokens, premières couches) changent moins
# Les couches du haut et la tête de classification changent plus

optimizer_grouped_parameters = [
    # Embeddings : taux très bas (informations génériques précieuses)
    {
        "params": model.bert.embeddings.parameters(),
        "lr": 1e-5,
    },
    # Couches intermédiaires : taux bas
    {
        "params": model.bert.encoder.parameters(),
        "lr": 2e-5,
    },
    # Pooler + Classifier : taux normal (à entraîner depuis zéro)
    {
        "params": list(model.bert.pooler.parameters()) + list(model.classifier.parameters()),
        "lr": 5e-5,
    },
]

optimizer = AdamW(optimizer_grouped_parameters, weight_decay=0.01)

# ─── Scheduler avec Warmup ───
num_epochs = 3
num_training_steps = 1000 * num_epochs
num_warmup_steps = num_training_steps // 10  # 10% des steps

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=num_warmup_steps,
    num_training_steps=num_training_steps,
)
```

---

## Gel partiel des couches

Pour les petits datasets, on peut **geler** les premières couches et n'entraîner que les dernières.

```python
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

# Geler toutes les couches sauf les 2 dernières et la tête
def freeze_bottom_layers(model, n_layers_to_freeze=10):
    """Gèle les N premières couches du transformer"""

    # Geler les embeddings
    for param in model.bert.embeddings.parameters():
        param.requires_grad = False

    # Geler les N premières couches
    for i in range(n_layers_to_freeze):
        for param in model.bert.encoder.layer[i].parameters():
            param.requires_grad = False

    # Vérifier
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Entraînables : {trainable:,} / {total:,} ({trainable/total:.1%})")

freeze_bottom_layers(model, n_layers_to_freeze=10)  # Geler 10/12 couches
# Entraînables : ~2M / 110M (1.8%)
```

---

## Comparaison des stratégies

```python
# Résumé des approches disponibles

approches = {
    "Zero-shot (pipeline)": {
        "GPU": "Aucun (CPU ok)",
        "Données": "0",
        "Temps": "Instantané",
        "Performance": "Bonne sur tâches standards",
        "Cas d'usage": "Prototype, tâches génériques",
    },
    "Few-shot (prompting)": {
        "GPU": "Aucun si API",
        "Données": "5-20 exemples",
        "Temps": "Quelques minutes",
        "Performance": "Bonne sur LLMs",
        "Cas d'usage": "Adaptation sans GPU",
    },
    "Gel partiel": {
        "GPU": "GPU 8GB",
        "Données": "1K-10K",
        "Temps": "30-60 min",
        "Performance": "Bonne",
        "Cas d'usage": "Petit dataset, ressources limitées",
    },
    "Fine-tuning complet": {
        "GPU": "GPU 16GB+ (BERT) / 80GB+ (LLM)",
        "Données": "10K+",
        "Temps": "1-8h",
        "Performance": "Très bonne",
        "Cas d'usage": "Dataset large, meilleure performance",
    },
    "LoRA / PEFT": {
        "GPU": "GPU 8-16GB",
        "Données": "1K-10K",
        "Temps": "30 min - 2h",
        "Performance": "Quasi-équivalent au complet",
        "Cas d'usage": "LLMs avec ressources limitées",
    },
    "QLoRA": {
        "GPU": "GPU 8GB",
        "Données": "1K-10K",
        "Temps": "1-4h",
        "Performance": "Bonne (légère perte vs LoRA)",
        "Cas d'usage": "LLMs 7B+ sur GPU domestique",
    },
}

for approche, details in approches.items():
    print(f"\n{'='*50}")
    print(f"  {approche}")
    print(f"{'='*50}")
    for k, v in details.items():
        print(f"  {k:15s} : {v}")
```

---

## Les métriques d'évaluation

Choisir la bonne métrique est crucial pour évaluer correctement son modèle.

```python
import evaluate
import numpy as np

# ─── Classification binaire ───
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

predictions = [0, 1, 1, 0, 1, 1, 0, 1]
references  = [0, 1, 0, 0, 1, 0, 0, 1]

print(accuracy.compute(predictions=predictions, references=references))
# {'accuracy': 0.75}

print(f1.compute(predictions=predictions, references=references, average="binary"))
# {'f1': 0.75}

# ─── Classification multiclasse ───
print(f1.compute(predictions=[0,1,2,0,1], references=[0,2,1,0,1], average="macro"))
# Macro : moyenne non pondérée par classe
print(f1.compute(predictions=[0,1,2,0,1], references=[0,2,1,0,1], average="weighted"))
# Weighted : pondéré par le support de chaque classe

# ─── NER ───
seqeval = evaluate.load("seqeval")
predictions_ner = [["O", "B-PER", "I-PER", "O", "B-LOC"]]
references_ner  = [["O", "B-PER", "I-PER", "O", "B-LOC"]]
print(seqeval.compute(predictions=predictions_ner, references=references_ner))
# {'precision': 1.0, 'recall': 1.0, 'f1': 1.0, 'accuracy': 1.0}

# ─── Génération de texte ───
rouge = evaluate.load("rouge")
bleu = evaluate.load("bleu")

predictions_gen = ["The cat is on the mat.", "The dog is in the yard."]
references_gen  = [["The cat sat on the mat."], ["A dog is playing in the yard."]]

print(rouge.compute(predictions=predictions_gen, references=references_gen))
print(bleu.compute(predictions=predictions_gen, references=references_gen))
```

---

## Points clés à retenir

1. **Commencer simple** : tester le zero-shot avant de fine-tuner
2. **Learning rate** : valeurs typiques 1e-5 à 5e-5 pour les encodeurs, 1e-4 à 3e-4 pour LoRA
3. **Epochs** : généralement 2-5 epochs (risque d'overfitting avec plus)
4. **Taille du batch** : batch_size × gradient_accumulation_steps = batch effectif
5. **Évaluer fréquemment** : eval_steps petit pour détecter le surapprentissage
6. **Checkpointing** : sauvegarder le meilleur modèle selon la validation

---

## Suite du cours

Le prochain module ([02-trainer.md](./02-trainer.md)) présente l'API `Trainer` de Hugging Face qui automatise la boucle d'entraînement complète (forward pass, backward pass, gradient descent, évaluation, sauvegarde des checkpoints).
