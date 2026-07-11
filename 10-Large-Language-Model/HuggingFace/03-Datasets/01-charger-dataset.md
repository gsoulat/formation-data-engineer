# Charger un dataset — `load_dataset`, DatasetDict et features

## Pourquoi la bibliothèque `datasets` ?

La bibliothèque `datasets` de Hugging Face résout plusieurs problèmes :

1. **Taille** : les datasets ML sont souvent plusieurs GB. `datasets` utilise le format Apache Arrow (memory-mapped) pour manipuler des données plus grandes que la RAM.
2. **Reproductibilité** : version contrôlée des datasets via le Hub.
3. **Efficacité** : transformations vectorisées avec plusieurs cœurs CPU.
4. **Interopérabilité** : conversion facile vers Pandas, PyTorch, NumPy.

```bash
pip install datasets
```

---

## `load_dataset` — Chargement depuis le Hub

```python
from datasets import load_dataset

# Format général
dataset = load_dataset(
    path="<nom-du-dataset>",           # Identifiant sur le Hub
    name="<configuration>",            # Sous-configuration optionnelle
    split="train",                     # Split spécifique
    # data_files="./data.csv",         # Chargement local
    # streaming=True,                  # Mode streaming (pas de download)
)
```

### Exemples concrets

```python
from datasets import load_dataset

# Dataset populaire : IMDB (critique de films, anglais)
imdb = load_dataset("stanfordnlp/imdb")
print(imdb)

# Dataset français : Allocine (critiques de films français)
allocine = load_dataset("allocine")
print(allocine)

# SQuAD (Question Answering)
squad = load_dataset("rajpurkar/squad")
print(squad)

# MNLI (Natural Language Inference)
mnli = load_dataset("nyu-mll/multi_nli")
print(mnli)

# Dataset multilingue avec configuration
xnli = load_dataset("xnli", "fr")  # Sous-config "fr" pour le français
print(xnli)
```

Sortie de `print(imdb)` :
```
DatasetDict({
    train: Dataset({
        features: ['text', 'label'],
        num_rows: 25000
    })
    test: Dataset({
        features: ['text', 'label'],
        num_rows: 25000
    })
    unsupervised: Dataset({
        features: ['text', 'label'],
        num_rows: 50000
    })
})
```

---

## `DatasetDict` — Structure générale

```python
from datasets import load_dataset

dataset = load_dataset("stanfordnlp/imdb")

# DatasetDict est un dictionnaire de Dataset
print(type(dataset))          # datasets.DatasetDict
print(dataset.keys())         # dict_keys(['train', 'test', 'unsupervised'])

# Accéder à un split
train = dataset["train"]
print(type(train))             # datasets.Dataset

# Informations sur un split
print(f"Nombre d'exemples : {len(train)}")     # 25000
print(f"Colonnes         : {train.column_names}")  # ['text', 'label']
print(f"Features         : {train.features}")
print(f"Shape            : {train.shape}")     # (25000, 2)
```

---

## Features — Schéma du dataset

```python
from datasets import load_dataset

dataset = load_dataset("stanfordnlp/imdb")
print(dataset["train"].features)
```

Sortie :
```
{'text': Value(dtype='string', id=None),
 'label': ClassLabel(names=['neg', 'pos'], id=None)}
```

### Types de features disponibles

```python
from datasets import Value, ClassLabel, Sequence, Array2D, Image, Audio

# Exemples de features
features_exemple = {
    "texte"   : Value("string"),
    "entier"  : Value("int32"),
    "flottant": Value("float32"),
    "label"   : ClassLabel(names=["négatif", "neutre", "positif"]),
    "tags"    : Sequence(Value("string")),
    "embedding": Sequence(Value("float32"), length=768),
    "image"   : Image(),
    "audio"   : Audio(sampling_rate=16000),
}
```

---

## Accéder aux données

```python
from datasets import load_dataset

dataset = load_dataset("stanfordnlp/imdb")
train = dataset["train"]

# Accéder par index
exemple_0 = train[0]
print(f"Texte  : {exemple_0['text'][:100]}...")
print(f"Label  : {exemple_0['label']}")  # 0 ou 1

# Accéder à une slice
batch = train[10:15]  # dict de listes
print(f"Labels batch : {batch['label']}")

# Accéder à une colonne entière
all_labels = train["label"]  # liste Python de 25000 éléments

# Itérer
for i, exemple in enumerate(train):
    if i >= 3:
        break
    print(f"[{i}] Label={exemple['label']} | {exemple['text'][:50]}...")
```

---

## Splits disponibles et chargement sélectif

```python
from datasets import load_dataset, get_dataset_split_names, get_dataset_config_names

# Voir les configurations disponibles
configs = get_dataset_config_names("wikipedia")
print(f"Configs Wikipedia : {configs[:5]}")
# ['20220301.aa', '20220301.ab', '20220301.ace', ...]

# Voir les splits disponibles pour une config
splits = get_dataset_split_names("wikipedia", "20220301.fr")
print(f"Splits : {splits}")

# Charger un seul split
train_only = load_dataset("stanfordnlp/imdb", split="train")
print(type(train_only))  # datasets.Dataset (pas DatasetDict)

# Charger avec des proportions
small_train = load_dataset("stanfordnlp/imdb", split="train[:10%]")
print(f"10% du train : {len(small_train)} exemples")

# Combiner des splits
combined = load_dataset("stanfordnlp/imdb", split="train+test")
print(f"Train + Test : {len(combined)} exemples")

# Mélanger et sous-échantillonner
shuffled = load_dataset("stanfordnlp/imdb", split="train[:5000]")
print(f"5000 premiers : {len(shuffled)}")
```

---

## Charger des données locales

```python
from datasets import load_dataset, Dataset
import pandas as pd

# ─── Depuis un CSV ───
dataset_csv = load_dataset(
    "csv",
    data_files={
        "train": "./data/train.csv",
        "test" : "./data/test.csv",
    },
    delimiter=",",
)

# ─── Depuis un JSON (une entrée par ligne = JSONL) ───
dataset_json = load_dataset(
    "json",
    data_files="./data/data.jsonl",
)

# ─── Depuis des fichiers texte ───
dataset_txt = load_dataset(
    "text",
    data_files=["./data/corpus1.txt", "./data/corpus2.txt"],
)

# ─── Depuis un DataFrame Pandas ───
df = pd.read_csv("./data/reviews.csv")
dataset_from_df = Dataset.from_pandas(df)
print(dataset_from_df)

# ─── Depuis un dictionnaire Python ───
data_dict = {
    "texte": ["J'adore ce produit", "Déçu par la qualité", "Correct"],
    "label": [1, 0, 2],
}
dataset_from_dict = Dataset.from_dict(data_dict)
print(dataset_from_dict)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `load_dataset("allocine")` dans un notebook avec la barre de progression du téléchargement visible, puis `print(dataset)` montrant la structure DatasetDict, et enfin `dataset["train"][0]` montrant un exemple réel de critique de film français avec son label
> **Expliquer :** Où sont stockés les fichiers téléchargés (cache Arrow), pourquoi le deuxième chargement est instantané (mémoire mappée), et comment le format Arrow permet de manipuler des datasets plus grands que la RAM

---

## Mode streaming — Grands datasets

Pour les très grands datasets (Wikipedia, Common Crawl, The Pile...) qu'on ne peut pas télécharger entièrement :

```python
from datasets import load_dataset

# streaming=True : les données sont lues à la volée (pas de téléchargement complet)
wiki_stream = load_dataset(
    "wikipedia",
    "20220301.fr",
    split="train",
    streaming=True,   # ← Dataset itérable, pas de download
    trust_remote_code=True,
)

print(type(wiki_stream))  # datasets.IterableDataset

# Itérer sur les premiers exemples
for i, exemple in enumerate(wiki_stream):
    if i >= 3:
        break
    print(f"Titre : {exemple['title']}")
    print(f"Texte : {exemple['text'][:100]}...\n")

# take() : équivalent à head() pour les IterableDataset
premiers_100 = wiki_stream.take(100)
for exemple in premiers_100:
    pass  # Traiter sans tout télécharger

# shuffle() sur IterableDataset (buffer_size contrôle le mélange)
wiki_shuffled = wiki_stream.shuffle(seed=42, buffer_size=1000)
```

---

## Explorer et visualiser un dataset

```python
from datasets import load_dataset
import pandas as pd
import matplotlib.pyplot as plt

dataset = load_dataset("allocine")
train = dataset["train"]

# Convertir en DataFrame pour l'exploration
df = train.to_pandas()
print(df.head())
print(df.info())
print(df["label"].value_counts())

# Distribution des longueurs de texte
df["longueur"] = df["review"].str.len()
print(df["longueur"].describe())

# Visualisation
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribution des labels
df["label"].map({0: "Négatif", 1: "Positif"}).value_counts().plot(
    kind="bar", ax=axes[0], color=["#e74c3c", "#2ecc71"]
)
axes[0].set_title("Distribution des labels")
axes[0].set_xlabel("Sentiment")
axes[0].set_ylabel("Nombre d'exemples")

# Distribution des longueurs
df["longueur"].hist(bins=50, ax=axes[1], color="#3498db", alpha=0.7)
axes[1].set_title("Distribution des longueurs")
axes[1].set_xlabel("Caractères")
axes[1].set_ylabel("Fréquence")

plt.tight_layout()
plt.savefig("dataset_distribution.png", dpi=150)
plt.show()

# Statistiques par label
print(df.groupby("label")["longueur"].describe())
```

---

## Créer un split train/validation/test

```python
from datasets import load_dataset

# Beaucoup de datasets n'ont pas de split validation
dataset = load_dataset("stanfordnlp/imdb")
train = dataset["train"]

print(f"Train original : {len(train)}")

# Créer un split validation à partir du train (90/10)
train_val = train.train_test_split(
    test_size=0.1,
    seed=42,
    stratify_by_column="label"  # Split stratifié pour garder la proportion
)

print(f"Nouveau train : {len(train_val['train'])}")
print(f"Validation    : {len(train_val['test'])}")

# Recombiner avec le test original
from datasets import DatasetDict

final_dataset = DatasetDict({
    "train"     : train_val["train"],
    "validation": train_val["test"],
    "test"      : dataset["test"],
})

print(final_dataset)
```

---

## Sauvegarder et partager un dataset

```python
from datasets import load_dataset, Dataset
import pandas as pd

# Créer un dataset custom
data = {
    "review": [
        "Excellent service, livraison rapide et produit conforme.",
        "Produit de mauvaise qualité, je suis très déçu.",
        "Correct mais rien d'exceptionnel.",
    ],
    "label": [1, 0, 2],
    "source": ["amazon", "amazon", "fnac"],
}

dataset = Dataset.from_dict(data)

# Sauvegarder localement (format Arrow)
dataset.save_to_disk("./data/mon-dataset/")

# Recharger
from datasets import load_from_disk
dataset_loaded = load_from_disk("./data/mon-dataset/")

# Sauvegarder en CSV/JSON pour partage
dataset.to_csv("./data/mon-dataset.csv")
dataset.to_json("./data/mon-dataset.jsonl")  # JSONL (une ligne par exemple)

# Pousser sur le Hub
dataset.push_to_hub("mon-username/mon-dataset-sentiment-fr")
```

---

## Informations utiles sur les datasets populaires

```python
from datasets import load_dataset

datasets_populaires = [
    ("stanfordnlp/imdb",   None,        "Sentiment anglais (films)"),
    ("allocine",            None,        "Sentiment français (films)"),
    ("rajpurkar/squad",    None,        "QA anglais extractif"),
    ("glue",               "sst2",      "Sentiment anglais (GLUE)"),
    ("glue",               "mnli",      "NLI anglais (GLUE)"),
    ("conll2003",          None,        "NER anglais"),
    ("wmt14",              "fr-en",     "Traduction FR-EN"),
    ("Helsinki-NLP/tatoeba_mt", "fra-eng", "Traduction FR-EN (Tatoeba)"),
]

print(f"{'Dataset':<35} {'Train':>10} {'Test':>10} {'Colonnes'}")
print("-" * 75)

for dataset_id, config, description in datasets_populaires:
    try:
        ds = load_dataset(dataset_id, config, split="train[:1]")  # 1 exemple pour la vitesse
        # Récupérer les infos sans tout télécharger
        from datasets import load_dataset_builder
        builder = load_dataset_builder(dataset_id, config)
        info = builder.info
        print(f"{dataset_id + (f'/{config}' if config else ''):<35} {description}")
    except Exception as e:
        print(f"{dataset_id:<35} Erreur: {str(e)[:40]}")
```

---

## Suite du cours

Le prochain module ([02-preparer-dataset.md](./02-preparer-dataset.md)) montre comment transformer un dataset brut en dataset tokenisé et prêt pour le fine-tuning : `map()`, `filter()`, `DataCollator` et gestion des batches.
