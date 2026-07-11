# Qdrant — Installation et démarrage

## Présentation

[Qdrant](https://qdrant.tech/) est une base de données vectorielle **haute performance** écrite en Rust, conçue pour les déploiements en production. Elle offre des fonctionnalités avancées comme le filtrage de précision, la gestion de payloads complexes, le sharding, la réplication et une interface web intégrée.

**Pourquoi choisir Qdrant :**
- Performance exceptionnelle grâce à Rust (vitesse + faible consommation mémoire)
- Interface web intégrée pour explorer les collections visuellement
- Filtrage puissant sur les payloads (JSON arbitraire attaché à chaque vecteur)
- Support des vecteurs nommés et des vecteurs sparse (hybrid search)
- Déploiement flexible : local, Docker, cloud managé (Qdrant Cloud)
- API REST + gRPC + clients Python, Go, TypeScript, Rust, Java

---

## 1. Architecture de Qdrant

### Concepts clés

```
Qdrant
├── Collections (équivalent de "tables")
│   ├── Points (équivalent de "lignes")
│   │   ├── ID (uuid ou integer)
│   │   ├── Vector (float32[])
│   │   └── Payload (JSON arbitraire = métadonnées)
│   └── Segments (partitions physiques internes)
├── Index HNSW (un par collection)
└── Payload Index (optionnel, pour accélérer les filtres)
```

### Comparaison vocabulaire Chroma vs Qdrant

| Concept | Chroma | Qdrant |
|---------|--------|--------|
| Groupe de vecteurs | Collection | Collection |
| Un vecteur | Document | Point |
| Métadonnées | Metadata | Payload |
| Texte brut | Document | Payload (champ libre) |
| Score de similarité | Distance | Score |

---

## 2. Installation et démarrage

### 2.1 Via Docker (recommandé)

```bash
# Démarrer Qdrant avec persistance des données
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# 6333 : API REST + interface web
# 6334 : gRPC (plus rapide pour les grandes opérations)
```

```bash
# Vérifier que Qdrant tourne
curl http://localhost:6333/health
# → {"title":"qdrant - vector search engine","version":"1.x.x"}

# Interface web
open http://localhost:6333/dashboard
```

### 2.2 Via Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### 2.3 Client Python

```bash
pip install qdrant-client sentence-transformers
```

```python
from qdrant_client import QdrantClient

# Connexion au serveur local
client = QdrantClient(host="localhost", port=6333)

# Vérification
info = client.get_collections()
print(f"Collections existantes : {[c.name for c in info.collections]}")
```

### 2.4 Mode in-memory (sans Docker, pour les tests)

```python
from qdrant_client import QdrantClient

# Client in-memory — aucun serveur requis
client = QdrantClient(":memory:")

# Ou mode fichier local (persistance sans Docker)
client = QdrantClient(path="./qdrant_local_db")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `docker run` pour Qdrant dans le terminal, attendre que le conteneur démarre, puis ouvrir le navigateur sur `http://localhost:6333/dashboard`. Naviguer dans l'interface web (onglet Collections, puis créer une collection depuis l'UI).
> **Expliquer :** "Qdrant vient avec une interface web intégrée, le 'dashboard'. On peut y créer des collections, visualiser les points, lancer des requêtes de recherche et monitorer les performances. En production, c'est très utile pour déboguer et superviser."

---

## 3. Créer une collection

### 3.1 Collection basique

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)

# Créer une collection
client.create_collection(
    collection_name="tech_articles",
    vectors_config=VectorParams(
        size=768,              # Dimension des vecteurs (doit correspondre au modèle d'embedding)
        distance=Distance.COSINE  # COSINE, EUCLID, ou DOT
    )
)

# Vérifier
collection_info = client.get_collection("tech_articles")
print(f"Status : {collection_info.status}")
print(f"Vecteurs indexés : {collection_info.vectors_count}")
print(f"Points total : {collection_info.points_count}")
```

### 3.2 Obtenir ou créer (idempotent)

```python
from qdrant_client.models import Distance, VectorParams

def get_or_create_collection(client, collection_name: str, vector_size: int):
    """Crée la collection si elle n'existe pas, la récupère sinon."""
    existing = [c.name for c in client.get_collections().collections]

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"Collection '{collection_name}' créée.")
    else:
        print(f"Collection '{collection_name}' existante.")

    return client.get_collection(collection_name)
```

### 3.3 Configuration avancée de l'index HNSW

```python
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff, OptimizersConfigDiff

client.create_collection(
    collection_name="high_perf_collection",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
        # Configuration HNSW pour améliorer recall vs vitesse
        hnsw_config=HnswConfigDiff(
            m=16,              # Nombre de connexions par nœud (défaut: 16) — plus élevé = meilleur recall, plus de RAM
            ef_construct=100,  # Fenêtre de construction (défaut: 100) — plus élevé = meilleur recall, plus lent à construire
        )
    ),
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=20000  # Indexer après 20000 points (économise du temps en dev)
    )
)
```

---

## 4. Qdrant Cloud (mode SaaS)

```python
from qdrant_client import QdrantClient

# Connexion à Qdrant Cloud (gratuit jusqu'à 1GB)
client = QdrantClient(
    url="https://xyz-example.eu-central.aws.cloud.qdrant.io",
    api_key="votre_api_key_ici"  # Obtenu sur cloud.qdrant.io
)
```

La migration de local vers cloud ne nécessite que de changer la configuration du client. Tout le reste du code reste identique.
