# Exercice 01 — Fine-tuner un classifieur de sentiment

## Objectif

Fine-tuner **CamemBERT** sur le dataset **Allocine** pour la classification de sentiment (positif / négatif sur des critiques de films français).

À la fin de cet exercice, vous aurez :
- Préparé un dataset pour le fine-tuning
- Fine-tuné un modèle BERT français
- Évalué les performances avec accuracy et F1
- Exporté le modèle pour la production
- (Bonus) Publié le modèle sur le Hub

---

## Durée estimée

2h30 (dont 1h d'entraînement GPU)

---

## Prérequis

```bash
pip install transformers datasets evaluate torch accelerate
```

---

## Contexte

Vous travaillez pour une startup de recommandation de films. Votre mission est de créer un analyseur de sentiment pour les critiques françaises.

**Dataset** : [Allocine](https://huggingface.co/datasets/allocine) — 160 000 critiques de films en français avec labels positif/négatif

**Modèle de base** : [CamemBERT-base](https://huggingface.co/camembert-base) — BERT pré-entraîné sur du français (OSCAR corpus)

**Objectif de performance** : F1 > 0.93 sur le set de test

---

## Partie 1 — Exploration des données (30 min)

### 1.1 Charger et explorer le dataset

```python
# TODO : Compléter ce code
from datasets import load_dataset

# Charger le dataset Allocine
dataset = load_dataset("allocine")

# EXERCICE : Afficher les informations suivantes :
# 1. La structure du DatasetDict (splits disponibles)
# 2. Le nombre d'exemples par split
# 3. Les noms des colonnes
# 4. Un exemple du split train (index 0)
# 5. La distribution des labels (nombre de positifs et négatifs dans le train)

# Votre code ici :
print(dataset)
# ...
```

**Questions de réflexion** :
- Combien d'exemples y a-t-il dans chaque split ?
- Le dataset est-il équilibré (même nombre de positifs et négatifs) ?
- Quelle est la longueur moyenne des critiques ?

### 1.2 Analyser les longueurs de texte

```python
import pandas as pd
import matplotlib.pyplot as plt

# Convertir le split train en DataFrame
df = dataset["train"].to_pandas()

# EXERCICE : Calculer et afficher :
# 1. Les statistiques descriptives de la longueur des critiques (en caractères)
# 2. Le pourcentage de critiques qui dépassent 512 tokens (hint : tokeniser d'abord)
# 3. Un histogramme de la distribution des longueurs

# Votre code ici :
```

**Question** : Quelle `max_length` choisiriez-vous pour la tokenisation ? Justifiez.

---

## Partie 2 — Préparation des données (30 min)

### 2.1 Tokenisation

```python
from transformers import AutoTokenizer

MODEL_CHECKPOINT = "camembert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)

# EXERCICE : Compléter la fonction de tokenisation
def tokenize_function(batch):
    """
    Tokenise un batch de critiques.

    Args:
        batch: dict avec clé "review" (liste de textes)

    Returns:
        dict avec input_ids, attention_mask
    """
    # TODO : Compléter
    # Hint : utiliser tokenizer() avec truncation=True et max_length appropriée
    # Ne pas faire de padding ici (le DataCollator s'en charge)
    return tokenizer(
        # ...
    )

# Appliquer la tokenisation à tous les splits
# TODO : Utiliser dataset.map() avec batched=True
tokenized_dataset = # ...

# Renommer la colonne "label" en "labels" (convention Trainer)
tokenized_dataset = # ...

print(tokenized_dataset)
print(f"\nExemple tokenisé : {tokenized_dataset['train'][0]}")
```

### 2.2 Vérification

```python
from transformers import DataCollatorWithPadding
from torch.utils.data import DataLoader

data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

# EXERCICE : Créer un DataLoader pour le split train (batch_size=4)
# et afficher le shape de chaque tensor du premier batch

# Votre code ici :
```

---

## Partie 3 — Fine-tuning (45 min d'entraînement)

### 3.1 Définir les métriques

```python
import evaluate
import numpy as np

# EXERCICE : Compléter la fonction compute_metrics
# Elle doit calculer accuracy ET f1 (binary)

def compute_metrics(eval_pred):
    """
    Calcule accuracy et F1 à partir des logits.

    Args:
        eval_pred: EvalPrediction(predictions=logits, label_ids=labels)

    Returns:
        dict avec "accuracy" et "f1"
    """
    logits, labels = eval_pred

    # TODO : 1. Convertir logits en prédictions (argmax)
    predictions = # ...

    # TODO : 2. Calculer accuracy
    # TODO : 3. Calculer f1 (average="binary")
    # TODO : 4. Retourner un dict combinant les deux résultats

    # Votre code ici :
    return # ...
```

### 3.2 Configurer l'entraînement

```python
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

# EXERCICE : Charger le modèle CamemBERT pour la classification binaire
# Configurer : num_labels, id2label, label2id
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_CHECKPOINT,
    # TODO : compléter
)

# EXERCICE : Configurer les TrainingArguments
# Objectifs :
# - 3 epochs
# - batch_size 32 pour l'entraînement, 64 pour l'évaluation
# - learning_rate 2e-5
# - évaluation et sauvegarde à chaque epoch
# - charger le meilleur modèle à la fin (selon le F1)
# - mixed precision FP16 si GPU disponible
# - logs toutes les 200 steps

training_args = TrainingArguments(
    output_dir="./results/camembert-allocine",
    # TODO : compléter
)

# EXERCICE : Créer le Trainer et lancer l'entraînement
trainer = Trainer(
    model=model,
    args=training_args,
    # TODO : compléter
)

# Lancer l'entraînement
trainer.train()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Les logs d'entraînement epoch par epoch : la perte d'entraînement qui descend, et les métriques d'évaluation (accuracy + F1) qui montent. Idéalement sur 3 epochs pour montrer la convergence.
> **Expliquer :** Comment interpréter les courbes (train_loss et eval_loss doivent converger, si eval_loss remonte = overfitting), pourquoi l'accuracy seule est insuffisante (importance du F1 sur les datasets déséquilibrés), et ce que signifie "load_best_model_at_end=True" dans la pratique

---

## Partie 4 — Évaluation (20 min)

### 4.1 Évaluer sur le set de test

```python
# EXERCICE : Évaluer le modèle sur le set de test
# et afficher les résultats

eval_results = # ...
print("Résultats sur le set de test :")
print(eval_results)

# EXERCICE : Calculer et afficher la matrice de confusion
# Utiliser sklearn.metrics.confusion_matrix et classification_report

predictions = trainer.predict(tokenized_dataset["test"])
predicted_labels = # ...
true_labels = # ...

from sklearn.metrics import classification_report, confusion_matrix
print("\nRapport de classification :")
print(classification_report(
    true_labels,
    predicted_labels,
    target_names=["NÉGATIF", "POSITIF"]
))
```

### 4.2 Analyser les erreurs

```python
# EXERCICE : Identifier les 10 exemples les plus mal classés
# (plus forte confiance du modèle mais prédiction incorrecte)

import torch
import numpy as np

# Utiliser predictions.predictions (logits) et predictions.label_ids

# Votre code ici :
# Pour chaque faux positif/négatif très confiant, afficher :
# - Le texte de la critique
# - Le label réel
# - La prédiction du modèle
# - Le score de confiance
```

**Questions de réflexion** :
- Y a-t-il des patterns dans les erreurs ? (ironie, phrases complexes ?)
- Quelle stratégie proposeriez-vous pour réduire ces erreurs ?

---

## Partie 5 — Inférence et export (15 min)

### 5.1 Sauvegarder le modèle

```python
# EXERCICE : Sauvegarder le modèle et le tokenizer
# dans le dossier "./models/camembert-sentiment-fr/"

# Votre code ici :
```

### 5.2 Tester l'inférence

```python
from transformers import pipeline

# EXERCICE : Créer un pipeline de classification
# avec le modèle sauvegardé localement

classifier = # ...

# Tester sur ces critiques
critiques_test = [
    "Un chef-d'œuvre absolu ! La mise en scène est époustouflante et le jeu des acteurs est d'une justesse remarquable.",
    "Décevant au possible. L'histoire n'a ni queue ni tête, les personnages sont creux et la fin est bâclée.",
    "Pas mal sans être exceptionnel. Quelques bonnes scènes mais l'ensemble manque de rythme.",
    "Je suis sorti de la salle avec un sentiment mitigé. Belles images mais scénario prévisible.",
    "Un film à voir absolument ! Émouvant, drôle et intelligent à la fois.",
]

for critique in critiques_test:
    result = classifier(critique)[0]
    print(f"[{result['label']:8s} {result['score']:.1%}] {critique[:60]}...")
```

---

## Partie 6 — Bonus : LoRA (si temps restant)

```python
# BONUS : Refaire l'exercice en utilisant LoRA
# Comparer les résultats (performance, temps d'entraînement, taille du modèle)

from peft import get_peft_model, LoraConfig, TaskType

# EXERCICE : Configurer et appliquer LoRA à CamemBERT
# Objectif : obtenir des résultats comparables au fine-tuning complet
# mais avec moins de 2% des paramètres entraînables

lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,
    lora_alpha=16,
    # TODO : choisir les bons target_modules pour CamemBERT
    target_modules=# ...
    modules_to_save=["classifier"],
)

# EXERCICE : Appliquer LoRA, entraîner et comparer avec le modèle complet
```

---

## Barème et critères de réussite

| Critère | Points | Requis pour valider |
|---------|--------|---------------------|
| Exploration du dataset | 10 | Distribution affichée + graphique longueurs |
| Tokenisation correcte | 20 | Shape correct, attention_mask présent |
| compute_metrics fonctionnel | 15 | Accuracy + F1 calculés correctement |
| Entraînement complet | 25 | 3 epochs sans erreur |
| F1 > 0.90 sur test | 15 | Performances acceptables |
| Analyse des erreurs | 10 | 5+ exemples mal classés identifiés |
| Export + pipeline | 5 | Inférence fonctionnelle |
| **Bonus LoRA** | **+10** | F1 > 0.88 avec < 2% paramètres |

**Total : 100 points + 10 bonus**

---

## Solution commentée

> **Note pour le formateur** : La solution complète est disponible dans `exercice-01-solution.py` (non inclus dans ce repo — à fournir séparément après l'exercice).

### Indices si blocage

**Partie 2** :
- `max_length=256` est un bon compromis (couvre 95%+ des critiques sans trop de troncature)
- N'oubliez pas `remove_columns=["review"]` dans `map()`

**Partie 3** :
- `id2label={0: "NÉGATIF", 1: "POSITIF"}`, `label2id={"NÉGATIF": 0, "POSITIF": 1}`
- `metric_for_best_model="f1"` avec `greater_is_better=True`
- Pour LoRA : `target_modules=["query", "value"]` pour CamemBERT

**Performance attendue** :
- Accuracy : ~93-95%
- F1 : ~93-95%
- Temps d'entraînement : ~20-30 min sur GPU T4 (Colab)

---

## Exercice suivant

Passer à [exercice-02-rag-hf.md](./exercice-02-rag-hf.md) pour construire un système RAG (Retrieval-Augmented Generation) en utilisant les embeddings HuggingFace et un modèle local.
