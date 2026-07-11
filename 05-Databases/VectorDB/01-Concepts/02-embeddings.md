# 02 — Les Embeddings : Transformer du texte en vecteurs

## Introduction

Un embedding est le point d'entrée de tout système vectoriel. Avant de stocker quoi que ce soit dans une vector database, il faut transformer vos données brutes (texte, images, audio) en vecteurs numériques. La qualité de vos embeddings détermine directement la qualité de vos recherches.

Ce chapitre couvre les deux approches principales :
1. **OpenAI API** — qualité maximale, payant, nécessite une connexion internet
2. **Sentence-Transformers** — gratuit, local, excellente qualité

---

## 1. Comment un modèle transforme du texte en vecteur

### 1.1 Le pipeline de transformation

```
"Le chat dort sur le canapé"
           ↓
    Tokenisation
["Le", "chat", "dort", "sur", "le", "canapé"]
           ↓
  Token IDs (vocabulaire)
    [1234, 5678, 910, ...]
           ↓
  Couches Transformer (attention, feed-forward)
           ↓
  Pooling (moyenne ou [CLS] token)
           ↓
  Vecteur de sortie
[0.023, -0.145, 0.891, ..., 0.089]  ← 384, 768, ou 1536 dimensions
```

### 1.2 L'attention — pourquoi le contexte compte

Un modèle de type Transformer (BERT, GPT) comprend que le mot "banque" a un sens différent dans :
- "Je vais à la **banque** retirer de l'argent" (institution financière)
- "Je m'assieds sur la **banque** du jardin" (siège)

Le mécanisme d'attention permet au modèle de regarder tous les autres mots de la phrase pour comprendre le sens d'un mot en contexte. L'embedding final intègre ce contexte.

### 1.3 Pooling

Les Transformers produisent un vecteur par token. Pour obtenir un seul vecteur représentant toute la phrase, on applique un **pooling** :

- **Mean Pooling** : moyenne de tous les vecteurs de tokens (le plus courant pour les embeddings de phrases)
- **[CLS] Token** : utiliser uniquement le premier token spécial [CLS] (méthode BERT originale)
- **Max Pooling** : prendre le maximum sur chaque dimension

---

## 2. OpenAI Embeddings

### 2.1 Les modèles disponibles

| Modèle | Dimensions | Prix (1M tokens) | Usage recommandé |
|--------|-----------|-----------------|-----------------|
| `text-embedding-3-small` | 1536 | $0.02 | Cas d'usage général, bon rapport qualité/prix |
| `text-embedding-3-large` | 3072 | $0.13 | Qualité maximale, use cases critiques |
| `text-embedding-ada-002` | 1536 | $0.10 | Modèle legacy, `3-small` le surpasse |

**Recommandation** : utiliser `text-embedding-3-small` dans 90% des cas.

### 2.2 Installation et configuration

```bash
pip install openai python-dotenv
```

```python
# .env
OPENAI_API_KEY=sk-...
```

```python
# embed_openai.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Générer un embedding pour un texte."""
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

# Test
embedding = embed_text("Bonjour, comment puis-je vous aider ?")
print(f"Dimensions : {len(embedding)}")          # 1536
print(f"Premiers éléments : {embedding[:5]}")   # [0.023, -0.145, ...]
```

### 2.3 Embeddings en batch (efficace)

```python
def embed_batch(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """
    Générer des embeddings pour une liste de textes en un seul appel API.
    Beaucoup plus efficace que d'appeler l'API une fois par texte.
    """
    # L'API OpenAI accepte jusqu'à 2048 inputs par requête
    # et jusqu'à 8191 tokens par input
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    # Trier par index pour garantir l'ordre
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

# Exemple
documents = [
    "Python est un langage de programmation populaire.",
    "Les bases de données vectorielles stockent des embeddings.",
    "Le machine learning transforme l'industrie technologique.",
    "Chroma est une vector database open source.",
]

embeddings = embed_batch(documents)
print(f"Nombre d'embeddings : {len(embeddings)}")      # 4
print(f"Dimensions : {len(embeddings[0])}")            # 1536
```

### 2.4 Réduire les dimensions (Matryoshka)

Les modèles `text-embedding-3-*` supportent la réduction de dimensions sans réentraînement (technique Matryoshka Representation Learning) :

```python
# Embeddings réduits à 256 dimensions (moins précis mais plus rapide et moins cher à stocker)
response = client.embeddings.create(
    input="Mon texte à encoder",
    model="text-embedding-3-small",
    dimensions=256   # Peut aller jusqu'à 1536 pour small, 3072 pour large
)

embedding_256 = response.data[0].embedding
print(len(embedding_256))  # 256
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir un terminal, lancer le script Python d'embedding OpenAI en live, afficher un embedding brut (les 1536 valeurs), puis calculer la similarité cosinus entre deux phrases : "Il fait beau aujourd'hui" et "Le soleil brille ce matin". Montrer le score élevé (~0.9).
> **Expliquer :** "Ces 1536 nombres, c'est tout ce qu'il faut pour représenter sémantiquement cette phrase. Regardez le score de similarité entre ces deux phrases : 0.89. Pour un humain c'est évident qu'elles sont similaires. Pour un programme naïf qui compare des chaînes de caractères, elles n'ont rien en commun."

---

## 3. Sentence-Transformers (local, gratuit)

### 3.1 Présentation

[Sentence-Transformers](https://www.sbert.net/) est une bibliothèque Python open source basée sur HuggingFace Transformers. Elle propose des modèles pré-entraînés spécifiquement pour les embeddings de phrases.

**Avantages** :
- 100% local — aucune donnée ne sort de votre machine
- Gratuit — aucun coût d'API
- Nombreux modèles multilingues disponibles
- Qualité comparable à OpenAI pour beaucoup de tâches

**Inconvénients** :
- Première utilisation : téléchargement du modèle (~100MB à 500MB)
- Légèrement moins performant qu'`ada-002`/`3-small` sur les benchmarks anglais
- Nécessite du CPU/GPU local

### 3.2 Installation

```bash
pip install sentence-transformers
```

### 3.3 Les modèles recommandés

| Modèle | Dimensions | Langue | Taille | Qualité |
|--------|-----------|--------|--------|---------|
| `all-MiniLM-L6-v2` | 384 | EN | ~80MB | Bon, très rapide |
| `all-mpnet-base-v2` | 768 | EN | ~420MB | Excellent |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 50+ langues | ~120MB | Bon, multilingue |
| `paraphrase-multilingual-mpnet-base-v2` | 768 | 50+ langues | ~420MB | Excellent, multilingue |
| `intfloat/multilingual-e5-large` | 1024 | 100+ langues | ~570MB | Très bon, multilingue |

**Pour du français** : `paraphrase-multilingual-mpnet-base-v2` ou `intfloat/multilingual-e5-large`

### 3.4 Utilisation basique

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Chargement du modèle (téléchargé automatiquement la 1ère fois)
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# Encoder une phrase
embedding = model.encode("Bonjour le monde !")
print(f"Type : {type(embedding)}")     # numpy.ndarray
print(f"Shape : {embedding.shape}")    # (768,)

# Encoder plusieurs phrases (batch)
phrases = [
    "Le chat dort sur le canapé.",
    "Le félin sommeille sur le sofa.",
    "La voiture roule très vite.",
    "L'automobile accélère brusquement.",
]

embeddings = model.encode(phrases)
print(f"Shape batch : {embeddings.shape}")  # (4, 768)
```

### 3.5 Calcul de similarité

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

phrases = [
    "Le chat dort sur le canapé.",
    "Le félin sommeille sur le sofa.",
    "La voiture roule très vite.",
    "L'automobile accélère brusquement.",
]

# Encoder
embeddings = model.encode(phrases, convert_to_tensor=True)

# Matrice de similarité cosinus complète
cos_sim = util.cos_sim(embeddings, embeddings)

print("Matrice de similarité cosinus :")
for i in range(len(phrases)):
    for j in range(i+1, len(phrases)):
        score = cos_sim[i][j].item()
        print(f"  [{i}] vs [{j}] : {score:.4f} | {phrases[i][:30]} ↔ {phrases[j][:30]}")
```

Résultat attendu :
```
[0] vs [1] : 0.8934 | Le chat dort sur le canapé.  ↔ Le félin sommeille sur le sofa.
[0] vs [2] : 0.1823 | Le chat dort sur le canapé.  ↔ La voiture roule très vite.
[2] vs [3] : 0.8741 | La voiture roule très vite.   ↔ L'automobile accélère brusquement.
```

### 3.6 Utiliser GPU si disponible

```python
import torch
from sentence_transformers import SentenceTransformer

device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Utilisation de : {device}")

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', device=device)

# L'encoding sur GPU est 10-50x plus rapide que sur CPU
embeddings = model.encode(my_large_list_of_texts, batch_size=64, show_progress_bar=True)
```

---

## 4. Stratégies de chunking

Le **chunking** est l'étape de découpage des documents longs en morceaux avant l'embedding. C'est une étape critique qui impacte directement la qualité de la recherche.

### 4.1 Pourquoi chunker ?

Les modèles d'embedding ont une **fenêtre de contexte maximale** :
- `text-embedding-3-small` : 8191 tokens (~6000 mots)
- `all-MiniLM-L6-v2` : 256 tokens (~190 mots) ← très limité !
- `paraphrase-multilingual-mpnet-base-v2` : 514 tokens (~380 mots)

Mais surtout : un embedding sur 5000 mots capture **trop d'informations** et devient moins précis pour la recherche. Un chunk ciblé donne de meilleurs résultats.

### 4.2 Chunking par taille fixe (Fixed-size)

```python
def chunk_by_size(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Découpe un texte en chunks de taille fixe avec chevauchement.

    chunk_size : nombre de caractères par chunk
    overlap    : nombre de caractères partagés entre chunks consécutifs
                 (évite de couper une idée en deux)
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

# Exemple
long_text = """
Les bases de données vectorielles sont des systèmes de stockage spécialisés...
[texte très long...]
"""

chunks = chunk_by_size(long_text, chunk_size=500, overlap=50)
print(f"Nombre de chunks : {len(chunks)}")
for i, chunk in enumerate(chunks[:3]):
    print(f"\nChunk {i} ({len(chunk)} chars) :")
    print(chunk[:100] + "...")
```

**Avantages** : simple, prévisible
**Inconvénients** : peut couper au milieu d'une phrase ou d'un paragraphe

### 4.3 Chunking par phrase (Sentence-based)

```python
import nltk
nltk.download('punkt')

def chunk_by_sentences(text: str, sentences_per_chunk: int = 5, overlap: int = 1) -> list[str]:
    """
    Découpe un texte en groupes de phrases.
    Préserve la cohérence grammaticale.
    """
    from nltk.tokenize import sent_tokenize

    sentences = sent_tokenize(text, language='french')
    chunks = []

    for i in range(0, len(sentences), sentences_per_chunk - overlap):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk = " ".join(chunk_sentences)
        if chunk:
            chunks.append(chunk)

    return chunks
```

### 4.4 Chunking récursif (LangChain RecursiveCharacterTextSplitter)

C'est la méthode **recommandée par LangChain** et la plus utilisée en pratique :

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # taille cible en caractères
    chunk_overlap=200,      # chevauchement pour la continuité du contexte
    length_function=len,
    # Séparateurs essayés dans cet ordre :
    separators=["\n\n", "\n", ". ", " ", ""]
    # 1. Essaie de couper sur double saut de ligne (paragraphes)
    # 2. Puis simple saut de ligne
    # 3. Puis point-espace (fin de phrase)
    # 4. Puis espace (fin de mot)
    # 5. Dernier recours : couper brutalement
)

# Avec un document texte
with open("document.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = splitter.split_text(text)
print(f"Nombre de chunks : {len(chunks)}")
print(f"Taille moyenne : {sum(len(c) for c in chunks) / len(chunks):.0f} chars")

# Avec des documents LangChain (contient aussi les métadonnées source)
from langchain.schema import Document

doc = Document(
    page_content=text,
    metadata={"source": "document.txt", "auteur": "John Doe"}
)

split_docs = splitter.split_documents([doc])
# Chaque chunk hérite des métadonnées du document parent
print(split_docs[0].metadata)  # {'source': 'document.txt', 'auteur': 'John Doe'}
```

### 4.5 Chunking sémantique (avancé)

Découpe en respectant les frontières sémantiques détectées automatiquement :

```python
# pip install semantic-chunkers

from semantic_chunkers import StatisticalChunker
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(name="paraphrase-multilingual-mpnet-base-v2")
chunker = StatisticalChunker(encoder=encoder)

chunks = chunker(docs=[text])
print(f"Nombre de chunks sémantiques : {len(chunks[0])}")
```

### 4.6 Tableau de comparaison des stratégies

| Stratégie | Complexité | Qualité | Quand l'utiliser |
|-----------|-----------|---------|-----------------|
| Taille fixe | Simple | Correcte | POC, données peu structurées |
| Par phrase | Moyenne | Bonne | Textes narratifs, articles |
| Récursive (LangChain) | Facile à utiliser | Très bonne | **Recommandé en général** |
| Sémantique | Complexe | Excellente | Production, haute précision |

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer en live l'impact du chunking sur la recherche. Prendre un PDF de 10 pages, chunker de deux façons (chunk_size=2000 vs chunk_size=300), faire la même requête, et montrer que les chunks petits donnent des résultats plus précis.
> **Expliquer :** "Avec des chunks de 2000 caractères, l'embedding représente trop d'idées à la fois. Avec des chunks de 300 caractères, chaque vecteur représente une idée précise. La recherche retourne exactement le paragraphe pertinent, pas tout une page."

---

## 5. Enrichissement des chunks (métadonnées)

Ne stockez jamais un vecteur seul. Ajoutez toujours des métadonnées pour filtrer et tracer les résultats.

```python
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from datetime import datetime

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

def process_document(filepath: str, source_name: str, category: str) -> list[dict]:
    """
    Pipeline complet : lecture → chunking → embedding → préparation pour insertion.
    Retourne une liste de dictionnaires prêts à être insérés dans une vector DB.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = splitter.split_text(text)
    embeddings = model.encode(chunks, show_progress_bar=True)

    records = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        records.append({
            "id": f"{source_name}_chunk_{i}",
            "embedding": embedding.tolist(),
            "text": chunk,
            "metadata": {
                "source": source_name,
                "filepath": filepath,
                "category": category,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "ingested_at": datetime.now().isoformat(),
                "char_count": len(chunk),
            }
        })

    return records

# Utilisation
records = process_document(
    filepath="rapport_annuel_2024.txt",
    source_name="rapport_annuel_2024",
    category="finance"
)

print(f"Documents générés : {len(records)}")
print(f"Premier document :")
print(f"  ID : {records[0]['id']}")
print(f"  Texte (début) : {records[0]['text'][:80]}...")
print(f"  Métadonnées : {records[0]['metadata']}")
```

---

## 6. Comparer OpenAI vs Sentence-Transformers

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Test avec les deux approches
test_pairs = [
    ("Python est un langage de programmation.", "Python est utilisé pour le développement logiciel."),
    ("Le ciel est bleu.", "La mer est vaste."),
    ("Intelligence artificielle et machine learning.", "Deep learning et réseaux de neurones."),
]

# Sentence-Transformers
from sentence_transformers import SentenceTransformer
st_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

print("=== Comparaison des similarités ===\n")
print(f"{'Paire':<50} | {'ST':<6} | {'OpenAI':<6}")
print("-" * 70)

for text1, text2 in test_pairs:
    # Sentence-Transformers
    emb1_st = st_model.encode(text1)
    emb2_st = st_model.encode(text2)
    sim_st = cosine_similarity([emb1_st], [emb2_st])[0][0]

    # OpenAI (nécessite une clé API)
    # emb1_oai = embed_text(text1)
    # emb2_oai = embed_text(text2)
    # sim_oai = cosine_similarity([emb1_oai], [emb2_oai])[0][0]

    label = f"{text1[:25]} ↔ {text2[:20]}"
    print(f"{label:<50} | {sim_st:.4f} | (nécessite API)")
```

---

## 7. Bonnes pratiques

### Normaliser les embeddings

```python
import numpy as np

def normalize(vector: np.ndarray) -> np.ndarray:
    """Normalise un vecteur à longueur 1 (norme L2)."""
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

# Ou en batch
embeddings = model.encode(texts, normalize_embeddings=True)
# → Le paramètre normalize_embeddings=True dans SentenceTransformer fait exactement ça
```

Quand les embeddings sont normalisés, le dot product est équivalent à la similarité cosinus et est plus rapide à calculer.

### Mettre en cache les embeddings

```python
import json
import hashlib

def embed_with_cache(text: str, cache_file: str = "embeddings_cache.json") -> list[float]:
    """Cache les embeddings pour éviter de recalculer / dépenser des appels API."""

    # Charger le cache
    try:
        with open(cache_file) as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

    # Clé de cache = hash du texte
    key = hashlib.md5(text.encode()).hexdigest()

    if key not in cache:
        # Calculer et mettre en cache
        cache[key] = embed_text(text)  # Votre fonction d'embedding
        with open(cache_file, "w") as f:
            json.dump(cache, f)

    return cache[key]
```

### Gérer les textes trop longs

```python
def embed_long_text(text: str, max_tokens: int = 500) -> list[float]:
    """
    Pour les textes longs : chunker, embedder chaque chunk,
    puis moyenner les embeddings (stratégie 'moyenne des chunks').
    """
    chunks = chunk_by_size(text, chunk_size=max_tokens * 4)  # ~4 chars/token

    if len(chunks) == 1:
        return embed_text(chunks[0])

    embeddings = [embed_text(chunk) for chunk in chunks]

    # Moyenne des embeddings
    mean_embedding = np.mean(embeddings, axis=0).tolist()
    return mean_embedding
```

---

## Résumé

| | OpenAI `text-embedding-3-small` | Sentence-Transformers |
|--|---|---|
| **Prix** | $0.02 / 1M tokens | Gratuit |
| **Confidentialité** | Données envoyées sur les serveurs OpenAI | 100% local |
| **Dimensions** | 1536 (réductible) | 384-768-1024 |
| **Qualité** | Très haute | Haute (légèrement inférieure) |
| **Setup** | Clé API uniquement | Téléchargement modèle (~100-500MB) |
| **Latence** | ~100-300ms (réseau) | ~5-50ms (local, CPU) |
| **Recommandé pour** | Production critique, projets commerciaux | Dev local, données sensibles, budget limité |

**Prochain chapitre** : stocker et interroger ces embeddings avec Chroma DB.
