# FAISS — Recherche vectorielle locale haute performance

## Présentation

[FAISS](https://github.com/facebookresearch/faiss) (Facebook AI Similarity Search) est une **bibliothèque** Python/C++ développée par Meta pour la recherche efficace de voisins proches dans de grands ensembles de vecteurs. Contrairement à Chroma ou Qdrant, FAISS n'est pas une base de données à part entière : c'est une bibliothèque d'indexation vectorielle.

**Caractéristiques principales :**
- Performance maximale en mémoire vive
- Conçu pour des corpus de centaines de millions de vecteurs
- 100% local, zéro infrastructure
- C++ sous le capot avec binding Python
- Plusieurs algorithmes d'index disponibles (IVF, HNSW, PQ...)

**Limites :**
- Ne gère pas les métadonnées/filtres nativement (à gérer manuellement)
- Optimisé pour les index statiques (mises à jour dynamiques coûteuses)
- Pas d'API réseau ni d'interface web
- Nécessite une expertise ML pour exploiter les configurations avancées

---

## 1. Installation

```bash
# Version CPU (recommandée pour commencer)
pip install faiss-cpu

# Version GPU (si vous avez CUDA disponible)
pip install faiss-gpu
```

```python
import faiss
print(faiss.__version__)  # ex: 1.7.x
```

---

## 2. Index de base : IndexFlatL2

L'index le plus simple : recherche exhaustive exacte (pas d'approximation).

```python
import faiss
import numpy as np

# Dimensions des vecteurs
d = 768  # Doit correspondre à votre modèle d'embedding

# Créer un index L2 (distance euclidienne)
index = faiss.IndexFlatL2(d)

print(f"Index vide ? {index.is_trained}")  # True (IndexFlat n'a pas besoin d'entraînement)
print(f"Nombre de vecteurs : {index.ntotal}")  # 0
```

---

## 3. Ajouter des vecteurs

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
d = 768

# Données
documents = [
    "Python est un langage de programmation populaire.",
    "Le machine learning transforme l'industrie technologique.",
    "Docker est un outil de containerisation.",
    "Kubernetes orchestre les conteneurs en production.",
    "FastAPI permet de créer des APIs REST rapidement.",
    "PostgreSQL est une base de données relationnelle.",
    "Redis est une base de données clé-valeur en mémoire.",
    "Elasticsearch permet la recherche full-text à grande échelle.",
]

# Générer les embeddings (FAISS attend du float32)
embeddings = model.encode(documents, normalize_embeddings=True).astype('float32')
print(f"Shape : {embeddings.shape}")  # (8, 768)

# Créer et remplir l'index
index = faiss.IndexFlatIP(d)  # IP = Inner Product (équivalent cosinus si vecteurs normalisés)
index.add(embeddings)
print(f"Vecteurs indexés : {index.ntotal}")  # 8
```

**Note** : `IndexFlatIP` (Inner Product) est équivalent à la similarité cosinus lorsque les vecteurs sont normalisés. Pour des vecteurs non normalisés, utilisez `IndexFlatL2`.

---

## 4. Recherche des K plus proches voisins

```python
# Requête
query = "Comment déployer des applications en production ?"
query_vec = model.encode([query], normalize_embeddings=True).astype('float32')

# Rechercher les 3 plus proches voisins
k = 3
scores, indices = index.search(query_vec, k)

print("=== Résultats ===")
for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
    print(f"[{i+1}] Score : {score:.4f} | Document : {documents[idx]}")
```

Résultat attendu :
```
[1] Score : 0.8912 | Kubernetes orchestre les conteneurs en production.
[2] Score : 0.8234 | Docker est un outil de containerisation.
[3] Score : 0.7891 | FastAPI permet de créer des APIs REST rapidement.
```

---

## 5. Gérer les métadonnées manuellement

FAISS ne stocke que des vecteurs avec des indices entiers. Pour associer des métadonnées, il faut les gérer séparément.

```python
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
d = 768

# Données avec métadonnées
data = [
    {"text": "Python est populaire pour le data science.", "source": "wiki", "categorie": "langages"},
    {"text": "Docker containerise les applications.", "source": "docs", "categorie": "devops"},
    {"text": "FastAPI crée des APIs REST modernes.", "source": "docs", "categorie": "frameworks"},
    {"text": "PostgreSQL est une BDD relationnelle.", "source": "docs", "categorie": "databases"},
]

# Séparer les textes et les métadonnées
texts = [d["text"] for d in data]
metadata_store = {i: item for i, item in enumerate(data)}  # index → métadonnées

# Indexer
embeddings = model.encode(texts, normalize_embeddings=True).astype('float32')
index = faiss.IndexFlatIP(d)
index.add(embeddings)

# Recherche avec récupération des métadonnées
def search_with_metadata(query: str, k: int = 3):
    query_vec = model.encode([query], normalize_embeddings=True).astype('float32')
    scores, indices = index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:  # -1 = résultat invalide (peut arriver si k > ntotal)
            results.append({
                "score": float(score),
                "metadata": metadata_store[idx]
            })
    return results

# Test
results = search_with_metadata("déploiement d'applications")
for r in results:
    print(f"Score : {r['score']:.4f} | {r['metadata']['text']}")
```

---

## 6. Index IVF : plus rapide pour les grands corpus

`IndexFlatL2/IP` effectue une recherche exhaustive (O(n)). Pour de très grands corpus, l'index IVF (Inverted File) divise l'espace en clusters et n'explore que les plus proches.

```python
import faiss
import numpy as np

d = 768           # Dimension des vecteurs
n_vectors = 100000  # Nombre de vecteurs

# Générer des données de test
np.random.seed(42)
vectors = np.random.rand(n_vectors, d).astype('float32')

# Index IVF avec quantification
nlist = 100   # Nombre de clusters (règle empirique : sqrt(n_vectors))
quantizer = faiss.IndexFlatL2(d)  # Index pour trouver les clusters les plus proches
index_ivf = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

# L'IVF doit être entraîné avant ajout de vecteurs
print("Entraînement de l'index IVF...")
index_ivf.train(vectors)  # Apprend les centroïdes des clusters

# Ajouter les vecteurs
index_ivf.add(vectors)
print(f"Vecteurs indexés : {index_ivf.ntotal}")

# Paramètre nprobe : combien de clusters explorer lors de la recherche
# Plus élevé = meilleur recall mais plus lent
index_ivf.nprobe = 10  # Explorer 10 clusters (sur nlist=100)

# Recherche
query = np.random.rand(1, d).astype('float32')
distances, indices = index_ivf.search(query, k=5)
print(f"Indices trouvés : {indices[0]}")
```

---

## 7. Sauvegarder et charger un index

```python
# Sauvegarder l'index
faiss.write_index(index, "mon_index.faiss")
print("Index sauvegardé.")

# Charger l'index
index_loaded = faiss.read_index("mon_index.faiss")
print(f"Index chargé : {index_loaded.ntotal} vecteurs")

# Les métadonnées doivent être sauvegardées séparément
import json
with open("metadata.json", "w") as f:
    json.dump(metadata_store, f, ensure_ascii=False)

# Chargement des métadonnées
with open("metadata.json") as f:
    metadata_store_loaded = {int(k): v for k, v in json.load(f).items()}
```

---

## 8. Intégration avec LangChain

LangChain propose une intégration FAISS qui gère automatiquement les métadonnées.

```python
# pip install langchain-community faiss-cpu
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")

# Créer depuis des documents
documents = [
    Document(page_content="Python est populaire.", metadata={"source": "wiki", "cat": "langages"}),
    Document(page_content="Docker containerise.", metadata={"source": "docs", "cat": "devops"}),
    Document(page_content="Kubernetes orchestre.", metadata={"source": "docs", "cat": "devops"}),
]

vectorstore = FAISS.from_documents(documents, embeddings)

# Recherche
docs = vectorstore.similarity_search("déploiement conteneurs", k=2)
for doc in docs:
    print(f"{doc.page_content} | {doc.metadata}")

# Sauvegarder / charger (LangChain gère aussi les métadonnées)
vectorstore.save_local("./faiss_index")
vectorstore_loaded = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
```

---

## 9. Tableau comparatif des types d'index FAISS

| Index | Recherche | Entraînement | Mémoire | Quand l'utiliser |
|-------|-----------|--------------|---------|-----------------|
| `IndexFlatL2` | Exacte (L2) | Non | Haute | < 100K vecteurs, précision maximale |
| `IndexFlatIP` | Exacte (dot product) | Non | Haute | < 100K vecteurs, vecteurs normalisés |
| `IndexIVFFlat` | Approx (IVF) | Oui | Haute | 100K–10M vecteurs, bon recall |
| `IndexIVFPQ` | Approx (IVF+PQ) | Oui | Très basse | > 10M vecteurs, mémoire limitée |
| `IndexHNSWFlat` | Approx (HNSW) | Non | Haute | Bonne alternative à IVF |

---

## Résumé

FAISS est recommandé pour :
- Recherche offline sur de très grands corpus (centaines de millions de vecteurs)
- Performance maximale en mémoire vive
- Équipe ML/recherche qui contrôle finement l'indexation
- Budget zéro, pas de serveur, 100% open source

Pour la plupart des projets avec besoin de métadonnées, filtres et API, Chroma ou Qdrant sont plus adaptés.
