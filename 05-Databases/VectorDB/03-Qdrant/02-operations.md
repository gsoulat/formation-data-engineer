# Qdrant — Opérations : indexation et recherche

## 1. Indexer des points (upsert)

### 1.1 Upsert simple

```python
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# Préparer les données
documents = [
    {
        "text": "Python est un langage de programmation interprété et orienté objet.",
        "source": "wikipedia",
        "categorie": "langages",
        "annee": 2024,
        "popularite": 9.5
    },
    {
        "text": "Docker est un outil de containerisation d'applications.",
        "source": "docs.docker.com",
        "categorie": "devops",
        "annee": 2024,
        "popularite": 8.8
    },
    {
        "text": "FastAPI est un framework web Python basé sur les type hints.",
        "source": "fastapi.tiangolo.com",
        "categorie": "frameworks",
        "annee": 2024,
        "popularite": 8.2
    },
    {
        "text": "PostgreSQL est une base de données relationnelle open source.",
        "source": "postgresql.org",
        "categorie": "databases",
        "annee": 2024,
        "popularite": 9.0
    },
    {
        "text": "Kubernetes orchestre les conteneurs à grande échelle en production.",
        "source": "kubernetes.io",
        "categorie": "devops",
        "annee": 2024,
        "popularite": 9.2
    },
]

# Générer les embeddings
texts = [doc["text"] for doc in documents]
embeddings = model.encode(texts, normalize_embeddings=True)

# Construire les PointStruct
points = []
for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
    point = PointStruct(
        id=i + 1,           # ID entier (ou UUID)
        vector=embedding.tolist(),
        payload={           # Payload = toutes vos métadonnées (JSON arbitraire)
            "text": doc["text"],
            "source": doc["source"],
            "categorie": doc["categorie"],
            "annee": doc["annee"],
            "popularite": doc["popularite"]
        }
    )
    points.append(point)

# Insérer dans Qdrant
operation_info = client.upsert(
    collection_name="tech_articles",
    points=points,
    wait=True  # Attendre la confirmation d'indexation
)

print(f"Opération : {operation_info.status}")
print(f"Points total : {client.get_collection('tech_articles').points_count}")
```

### 1.2 Upsert avec UUID

```python
import uuid
from qdrant_client.models import PointStruct

# Les IDs peuvent être des entiers ou des UUIDs
point = PointStruct(
    id=str(uuid.uuid4()),    # UUID string : "550e8400-e29b-41d4-a716-446655440000"
    vector=[0.1, 0.2, ...],
    payload={"text": "Mon document", "source": "test"}
)
```

### 1.3 Upsert par batch (gros volumes)

```python
def upsert_batch(client, collection_name: str, documents: list[dict], model, batch_size: int = 100):
    """Insère des documents par lots avec barre de progression."""
    from tqdm import tqdm

    total = len(documents)
    texts = [doc["text"] for doc in documents]

    print(f"Génération des embeddings pour {total} documents...")
    all_embeddings = model.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=True)

    print(f"Insertion dans Qdrant par batches de {batch_size}...")
    for i in tqdm(range(0, total, batch_size)):
        batch_docs = documents[i:i+batch_size]
        batch_emb = all_embeddings[i:i+batch_size]

        points = [
            PointStruct(
                id=i + j + 1,
                vector=emb.tolist(),
                payload={k: v for k, v in doc.items()}
            )
            for j, (doc, emb) in enumerate(zip(batch_docs, batch_emb))
        ]

        client.upsert(collection_name=collection_name, points=points, wait=True)

    print(f"Total : {client.get_collection(collection_name).points_count} points")
```

---

## 2. Recherche par similarité

### 2.1 Recherche basique

```python
# Encoder la requête
query = "Comment déployer une application en production ?"
query_vector = model.encode(query, normalize_embeddings=True).tolist()

# Recherche
results = client.search(
    collection_name="tech_articles",
    query_vector=query_vector,
    limit=3,         # Nombre de résultats
    with_payload=True,  # Inclure les payloads dans les résultats
    with_vectors=False  # Ne pas retourner les vecteurs (économise la bande passante)
)

print("=== Résultats de recherche ===\n")
for result in results:
    print(f"Score : {result.score:.4f}")
    print(f"ID    : {result.id}")
    print(f"Texte : {result.payload.get('text', '')[:80]}")
    print(f"Source: {result.payload.get('source', '')}")
    print(f"Catégorie : {result.payload.get('categorie', '')}")
    print()
```

### 2.2 Recherche avec filtre sur le payload

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Filtrer par catégorie exacte
results = client.search(
    collection_name="tech_articles",
    query_vector=query_vector,
    query_filter=Filter(
        must=[  # Toutes les conditions doivent être vraies (AND)
            FieldCondition(
                key="categorie",
                match=MatchValue(value="devops")
            )
        ]
    ),
    limit=5
)
```

---

## 3. Recherche par ID et scroll

### 3.1 Récupérer des points par ID

```python
# Récupérer des points spécifiques par leurs IDs
points = client.retrieve(
    collection_name="tech_articles",
    ids=[1, 2, 3],
    with_payload=True,
    with_vectors=True
)

for point in points:
    print(f"ID: {point.id} | Score: N/A | Texte: {point.payload['text'][:50]}")
```

### 3.2 Scroll (parcourir tous les points)

```python
# Parcourir tous les points de la collection (pagination)
offset = None
all_points = []

while True:
    result, next_offset = client.scroll(
        collection_name="tech_articles",
        scroll_filter=None,   # Optionnel : filtre
        limit=100,
        offset=offset,
        with_payload=True,
        with_vectors=False
    )

    all_points.extend(result)

    if next_offset is None:
        break
    offset = next_offset

print(f"Total de points récupérés : {len(all_points)}")
```

---

## 4. Supprimer des points et des collections

```python
# Supprimer par IDs
client.delete(
    collection_name="tech_articles",
    points_selector=[1, 2]  # Liste d'IDs
)

# Supprimer par filtre
from qdrant_client.models import FilterSelector

client.delete(
    collection_name="tech_articles",
    points_selector=FilterSelector(
        filter=Filter(
            must=[FieldCondition(key="categorie", match=MatchValue(value="obsolete"))]
        )
    )
)

# Supprimer toute la collection
client.delete_collection("tech_articles")
```

---

## 5. Pipeline complet : exemple réel

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import uuid

# --- Configuration ---
COLLECTION_NAME = "knowledge_base"
VECTOR_SIZE = 768  # paraphrase-multilingual-mpnet-base-v2

# --- Initialisation ---
qdrant = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# --- Création de la collection ---
if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"Collection '{COLLECTION_NAME}' créée.")

# --- Données à indexer ---
knowledge_base = [
    {"id": 1, "text": "Pour installer Python sur Ubuntu : sudo apt-get install python3", "domaine": "python", "niveau": "debutant"},
    {"id": 2, "text": "Les list comprehensions Python : [x*2 for x in range(10)]", "domaine": "python", "niveau": "intermediaire"},
    {"id": 3, "text": "FastAPI : créer une route GET avec @app.get('/items/{item_id}')", "domaine": "fastapi", "niveau": "debutant"},
    {"id": 4, "text": "FastAPI supporte les types Pydantic pour la validation automatique des données", "domaine": "fastapi", "niveau": "intermediaire"},
    {"id": 5, "text": "Docker build -t mon-image . construit une image à partir du Dockerfile", "domaine": "docker", "niveau": "debutant"},
    {"id": 6, "text": "Docker-compose permet d'orchestrer plusieurs conteneurs avec un seul fichier YAML", "domaine": "docker", "niveau": "intermediaire"},
]

# --- Indexation ---
texts = [item["text"] for item in knowledge_base]
embeddings = model.encode(texts, normalize_embeddings=True)

points = [
    PointStruct(
        id=item["id"],
        vector=emb.tolist(),
        payload={"text": item["text"], "domaine": item["domaine"], "niveau": item["niveau"]}
    )
    for item, emb in zip(knowledge_base, embeddings)
]

qdrant.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
print(f"Indexés : {qdrant.get_collection(COLLECTION_NAME).points_count} points")

# --- Fonction de recherche ---
def search(query: str, domaine: str = None, niveau: str = None, top_k: int = 3):
    """Recherche sémantique avec filtres optionnels."""
    query_vec = model.encode(query, normalize_embeddings=True).tolist()

    # Construire le filtre dynamiquement
    conditions = []
    if domaine:
        conditions.append(FieldCondition(key="domaine", match=MatchValue(value=domaine)))
    if niveau:
        conditions.append(FieldCondition(key="niveau", match=MatchValue(value=niveau)))

    query_filter = Filter(must=conditions) if conditions else None

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True
    )

    return results

# --- Tests ---
print("\n=== Recherche : 'comment créer une route API' ===")
for r in search("comment créer une route API"):
    print(f"  [{r.score:.3f}] {r.payload['text'][:70]}")

print("\n=== Recherche limitée au domaine 'docker' ===")
for r in search("gestion de plusieurs services", domaine="docker"):
    print(f"  [{r.score:.3f}] {r.payload['text'][:70]}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer le pipeline complet ci-dessus dans un terminal, montrer les logs d'indexation, puis lancer plusieurs requêtes de recherche avec et sans filtres. Afficher les scores de similarité pour chaque résultat.
> **Expliquer :** "Remarquez les scores : plus le score est proche de 1.0, plus le document est similaire sémantiquement à la requête. Avec le filtre domaine='docker', on restreint la recherche à seulement 2 points au lieu de 6, mais Qdrant utilise quand même l'index vectoriel pour trouver le plus pertinent parmi eux."
