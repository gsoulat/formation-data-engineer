# Chroma — Opérations CRUD et recherche

## 1. Ajouter des documents

### 1.1 Sans embeddings personnalisés (Chroma génère automatiquement)

Par défaut, Chroma utilise le modèle `all-MiniLM-L6-v2` de Sentence-Transformers si vous ne fournissez pas d'embeddings.

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("articles_tech")

# Ajouter des documents — Chroma génère les embeddings automatiquement
collection.add(
    documents=[
        "Python est un langage de programmation interprété, orienté objet.",
        "Le machine learning est une sous-catégorie de l'intelligence artificielle.",
        "Docker est un outil de containerisation qui facilite le déploiement.",
        "Kubernetes orchestre les conteneurs Docker à grande échelle.",
        "FastAPI est un framework web Python moderne et très rapide.",
    ],
    metadatas=[
        {"source": "wikipedia", "categorie": "langages", "annee": 2024},
        {"source": "wikipedia", "categorie": "ia", "annee": 2024},
        {"source": "docs.docker.com", "categorie": "devops", "annee": 2024},
        {"source": "kubernetes.io", "categorie": "devops", "annee": 2024},
        {"source": "fastapi.tiangolo.com", "categorie": "frameworks", "annee": 2024},
    ],
    ids=["doc_001", "doc_002", "doc_003", "doc_004", "doc_005"]
    # Les IDs doivent être uniques dans la collection
)

print(f"Nombre de documents : {collection.count()}")  # 5
```

### 1.2 Avec embeddings personnalisés

```python
from sentence_transformers import SentenceTransformer
import chromadb

# Préparer les données
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

documents = [
    "Python est un langage polyvalent.",
    "Le deep learning utilise des réseaux de neurones profonds.",
    "Git est un système de contrôle de version distribué.",
]

ids = [f"doc_{i:03d}" for i in range(len(documents))]
metadatas = [{"langue": "fr", "index": i} for i in range(len(documents))]

# Générer les embeddings
embeddings = model.encode(documents).tolist()

# Insérer avec embeddings personnalisés
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="documents_fr",
    metadata={"hnsw:space": "cosine"}
)

collection.add(
    documents=documents,
    embeddings=embeddings,   # Vecteurs précalculés
    metadatas=metadatas,
    ids=ids
)

print(f"Insérés : {collection.count()} documents")
```

### 1.3 Ingestion par batch (grands volumes)

```python
def add_documents_by_batch(
    collection,
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    model,
    batch_size: int = 100
):
    """Insère des documents par lots pour éviter les problèmes mémoire."""
    total = len(documents)

    for i in range(0, total, batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        # Générer les embeddings pour ce batch
        batch_embeddings = model.encode(batch_docs, show_progress_bar=False).tolist()

        collection.add(
            documents=batch_docs,
            embeddings=batch_embeddings,
            metadatas=batch_meta,
            ids=batch_ids
        )

        print(f"Batch {i//batch_size + 1} : {min(i+batch_size, total)}/{total} documents insérés")

    print(f"Total final : {collection.count()} documents")
```

---

## 2. Recherche (Query)

### 2.1 Recherche sémantique basique

```python
# Requête par texte — Chroma génère automatiquement l'embedding de la requête
results = collection.query(
    query_texts=["Comment fonctionne l'apprentissage automatique ?"],
    n_results=3  # Retourner les 3 documents les plus proches
)

print("=== Résultats ===")
for i in range(len(results['documents'][0])):
    doc = results['documents'][0][i]
    dist = results['distances'][0][i]
    meta = results['metadatas'][0][i]
    print(f"\n[{i+1}] Score distance : {dist:.4f}")
    print(f"     Document : {doc[:100]}")
    print(f"     Métadonnées : {meta}")
```

**Note** : avec la métrique `cosine`, Chroma retourne des **distances** (0 = identique, 2 = opposé). Pour obtenir la similarité, utilisez `1 - distance`.

### 2.2 Recherche avec embeddings personnalisés

```python
# Si vous utilisez votre propre modèle d'embedding
query = "Quel langage pour faire du web ?"
query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],  # Toujours une liste de vecteurs
    n_results=3
)
```

### 2.3 Recherche multi-requêtes

```python
# Plusieurs requêtes en une seule fois
results = collection.query(
    query_texts=[
        "apprentissage automatique",
        "déploiement d'applications",
        "frameworks web Python"
    ],
    n_results=2
)

# results['documents'] est une liste de listes
for query_idx, query_docs in enumerate(results['documents']):
    print(f"\nRequête {query_idx + 1} :")
    for doc in query_docs:
        print(f"  → {doc[:80]}")
```

### 2.4 Inclure les embeddings dans les résultats

```python
results = collection.query(
    query_texts=["machine learning"],
    n_results=2,
    include=["documents", "metadatas", "distances", "embeddings"]
    # Par défaut : ["documents", "metadatas", "distances"]
)

print(f"Dimension du vecteur retourné : {len(results['embeddings'][0][0])}")
```

---

## 3. Filtrage par métadonnées

Le filtrage par métadonnées permet de restreindre la recherche à un sous-ensemble de documents.

### 3.1 Filtres simples

```python
# Filtrer par catégorie exacte
results = collection.query(
    query_texts=["déploiement infrastructure"],
    n_results=3,
    where={"categorie": "devops"}  # WHERE categorie = 'devops'
)

# Filtrer par valeur numérique
results = collection.query(
    query_texts=["nouvelles technologies"],
    n_results=5,
    where={"annee": {"$gte": 2023}}  # WHERE annee >= 2023
)
```

### 3.2 Opérateurs de filtrage disponibles

```python
# Opérateurs de comparaison
{"annee": {"$eq": 2024}}    # Égal
{"annee": {"$ne": 2023}}    # Différent
{"annee": {"$gt": 2022}}    # Supérieur strict
{"annee": {"$gte": 2022}}   # Supérieur ou égal
{"annee": {"$lt": 2025}}    # Inférieur strict
{"annee": {"$lte": 2024}}   # Inférieur ou égal

# Opérateurs de liste
{"categorie": {"$in": ["devops", "ia"]}}     # IN
{"categorie": {"$nin": ["langages"]}}        # NOT IN

# Opérateurs logiques
{
    "$and": [
        {"categorie": "devops"},
        {"annee": {"$gte": 2023}}
    ]
}

{
    "$or": [
        {"categorie": "ia"},
        {"categorie": "langages"}
    ]
}
```

### 3.3 Filtrage sur le contenu des documents

```python
# where_document filtre sur le texte brut du document (contains/not_contains)
results = collection.query(
    query_texts=["containerisation"],
    n_results=3,
    where_document={"$contains": "Docker"}  # Le texte du doc doit contenir "Docker"
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démontrer en live une recherche sémantique dans Chroma : créer une collection avec 10 documents variés, lancer une requête qui ne contient aucun mot des documents les plus pertinents, et montrer que les bons documents remontent quand même.
> **Expliquer :** "J'ai cherché 'comment faire tourner mon app en prod' et Chroma a trouvé les documents sur Docker et Kubernetes. Aucun de ces documents ne contient les mots 'faire tourner' ou 'en prod', mais leurs embeddings sont proches sémantiquement. C'est ça la vraie valeur des vector databases."

---

## 4. Mise à jour et suppression

### 4.1 Mettre à jour des documents

```python
# Mettre à jour le texte, les métadonnées ou les embeddings d'un document existant
collection.update(
    ids=["doc_001"],
    documents=["Python est un langage de programmation populaire et polyvalent."],
    metadatas=[{"source": "wikipedia", "categorie": "langages", "annee": 2025, "updated": True}]
)

# update() ne fait rien si l'ID n'existe pas
# upsert() = update() + insert si inexistant
collection.upsert(
    ids=["doc_999"],
    documents=["Nouveau document ajouté par upsert."],
    metadatas=[{"source": "manuel", "categorie": "divers"}]
)
```

### 4.2 Supprimer des documents

```python
# Suppression par IDs
collection.delete(ids=["doc_001", "doc_002"])

# Suppression par filtre (ATTENTION : supprime tous les documents correspondants)
collection.delete(where={"categorie": "obsolete"})

# Vérifier
print(f"Documents restants : {collection.count()}")
```

### 4.3 Récupérer des documents par ID

```python
# Récupérer des documents spécifiques
result = collection.get(
    ids=["doc_003", "doc_004"],
    include=["documents", "metadatas"]
)

print(result['documents'])
print(result['metadatas'])

# Récupérer avec filtre de métadonnées
result = collection.get(
    where={"categorie": "devops"},
    include=["documents", "metadatas", "embeddings"]
)
```

---

## 5. Bonnes pratiques

### Nommer les IDs de façon significative

```python
import hashlib

def generate_stable_id(text: str, source: str) -> str:
    """
    Génère un ID stable basé sur le contenu.
    Le même texte donnera toujours le même ID → permet l'upsert idempotent.
    """
    content = f"{source}::{text}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]
```

### Inspecter une collection

```python
def inspect_collection(collection):
    """Affiche un résumé d'une collection Chroma."""
    count = collection.count()
    print(f"Nom : {collection.name}")
    print(f"Nombre de documents : {count}")
    print(f"Métadonnées de la collection : {collection.metadata}")

    if count > 0:
        # Récupérer les 5 premiers documents
        sample = collection.get(limit=5, include=["documents", "metadatas"])
        print(f"\nÉchantillon ({min(5, count)} documents) :")
        for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas'])):
            print(f"  [{i}] {doc[:60]}... | {meta}")
```
