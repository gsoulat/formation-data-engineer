# 03 — Comparatif : Choisir sa Vector Database

## Introduction

Le marché des vector databases a explosé entre 2022 et 2024. Il existe aujourd'hui des dizaines de solutions, chacune avec ses forces et ses faiblesses. Ce chapitre vous donne les outils pour prendre une décision éclairée selon votre contexte.

---

## 1. Les principales solutions

### 1.1 Chroma

**Type** : Open source, Python-first
**Site** : [trychroma.com](https://www.trychroma.com/)
**Langage backend** : Python + Rust (DuckDB sous le capot)

```
POUR VOUS SI :
✅ Développement local et prototypage rapide
✅ Intégration LangChain/LlamaIndex en priorité
✅ Équipe Python, besoin de simplicité maximale
✅ Volume < 1 million de vecteurs
✅ Pas de besoin d'interface web intégrée

ÉVITER SI :
❌ Production à grande échelle
❌ Besoin de filtres très complexes et performants
❌ Équipe multi-langages (Go, Rust, Java...)
❌ Besoin de réplication ou sharding
```

### 1.2 Qdrant

**Type** : Open source + cloud managé
**Site** : [qdrant.tech](https://qdrant.tech/)
**Langage backend** : Rust

```
POUR VOUS SI :
✅ Production avec des exigences de performance
✅ Filtres complexes sur des payloads riches
✅ Équipe multi-langages (Python, Go, TypeScript, Java, Rust)
✅ Besoin d'une interface web intégrée
✅ Volume de quelques milliers à plusieurs dizaines de millions de vecteurs
✅ Self-hosted sur vos propres serveurs

ÉVITER SI :
❌ Prototype ultra-rapide où la simplicité prime
❌ Besoin d'un service entièrement managé sans maintenance
```

### 1.3 FAISS (Facebook AI Similarity Search)

**Type** : Bibliothèque Python/C++ (pas une base de données à part entière)
**Site** : [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)
**Langage** : C++ avec binding Python

```
POUR VOUS SI :
✅ Performance maximale en mémoire vive
✅ Recherche offline sur de très grands corpus (centaines de millions de vecteurs)
✅ Équipe ML/recherche qui contrôle finement l'index
✅ Pas besoin de persistance ou d'API REST
✅ Budget zéro (100% open source, pas de serveur)

ÉVITER SI :
❌ Besoin de métadonnées/filtres (FAISS ne gère pas les payloads nativement)
❌ Mises à jour dynamiques fréquentes (FAISS est optimisé pour les index statiques)
❌ Besoin d'une API réseau ou d'un multi-utilisateurs
❌ Équipe sans expertise ML
```

```python
# Exemple FAISS basique
import faiss
import numpy as np

# Créer un index L2 de 768 dimensions
dimension = 768
index = faiss.IndexFlatL2(dimension)

# Ajouter des vecteurs (numpy float32)
vectors = np.random.rand(1000, dimension).astype('float32')
index.add(vectors)

# Rechercher les 5 plus proches voisins
query = np.random.rand(1, dimension).astype('float32')
distances, indices = index.search(query, k=5)

print(f"Indices trouvés : {indices[0]}")
print(f"Distances L2 : {distances[0]}")

# Sauvegarder/charger l'index
faiss.write_index(index, "my_index.faiss")
index = faiss.read_index("my_index.faiss")
```

### 1.4 Pinecone

**Type** : Cloud-only SaaS (aucun self-hosting)
**Site** : [pinecone.io](https://www.pinecone.io/)

```
POUR VOUS SI :
✅ Vous ne voulez pas gérer d'infrastructure du tout
✅ Startup qui veut démarrer vite et scale automatiquement
✅ Budget disponible pour un service managé
✅ Besoin de SLAs garantis et support
✅ Volume variable (scale automatique)

ÉVITER SI :
❌ Contraintes de souveraineté des données (vos données sont chez Pinecone/AWS)
❌ Budget serré (peut devenir très cher à grande échelle)
❌ Besoin de déploiement on-premise
```

```python
# Exemple Pinecone
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="votre_cle_api")

# Créer un index serverless
pc.create_index(
    name="mon-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

index = pc.Index("mon-index")

# Upsert des vecteurs
vectors = [
    ("id1", [0.1, 0.2, ...], {"texte": "document 1", "source": "wiki"}),
    ("id2", [0.3, 0.4, ...], {"texte": "document 2", "source": "docs"}),
]

index.upsert(vectors=[(id, vec, meta) for id, vec, meta in vectors])

# Recherche
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=3,
    include_metadata=True,
    filter={"source": {"$eq": "wiki"}}
)
```

### 1.5 Weaviate

**Type** : Open source + cloud managé
**Site** : [weaviate.io](https://weaviate.io/)
**Langage backend** : Go

```
POUR VOUS SI :
✅ Besoin de hybrid search (vectoriel + BM25 keyword) natif
✅ Schéma orienté knowledge graph (relations entre objets)
✅ Besoin de modules intégrés (text2vec-openai, generative-openai...)
✅ GraphQL comme interface de requête

ÉVITER SI :
❌ Courbe d'apprentissage jugée trop importante
❌ Pas besoin des fonctionnalités avancées de schéma
❌ Équipe peu familière avec Go/GraphQL
```

### 1.6 pgvector (PostgreSQL extension)

**Type** : Extension open source pour PostgreSQL
**Site** : [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)

```
POUR VOUS SI :
✅ Vous avez déjà PostgreSQL en production
✅ Volume modéré (< 1-5M vecteurs selon le matériel)
✅ Besoin de joindre vos vecteurs avec des données relationnelles
✅ Équipe SQL familière, pas envie d'apprendre un nouvel outil
✅ Recherche vectorielle + requêtes SQL dans une seule requête

ÉVITER SI :
❌ Volume très grand (pgvector est moins optimisé que les solutions dédiées)
❌ Besoin de performance de type HNSW à très grande échelle
```

```sql
-- pgvector : recherche vectorielle en SQL pur
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    source TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Créer un index HNSW
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);

-- Recherche des 5 plus proches voisins
SELECT id, content, source,
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- Recherche avec filtre SQL classique
SELECT id, content
FROM documents
WHERE source = 'wikipedia' AND created_at > '2024-01-01'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

---

## 2. Tableau comparatif global

| Critère | Chroma | Qdrant | FAISS | Pinecone | Weaviate | pgvector |
|---------|--------|--------|-------|----------|----------|----------|
| **Facilité d'installation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Scalabilité** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Filtrage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Interface web** | ❌ | ✅ intégrée | ❌ | ✅ cloud | ✅ cloud | via pgAdmin |
| **Self-hosted** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Gratuit** | ✅ | ✅ free tier | ✅ | Tier gratuit limité | ✅ / payant | ✅ |
| **API REST** | ✅ (mode serveur) | ✅ | ❌ | ✅ | ✅ | Via PostgREST |
| **Multi-langages** | Python | Py/Go/TS/Java/Rust | Python/C++ | Py/TS/Go/Java | Py/TS/Go/Java | Tout |
| **LangChain support** | ✅ natif | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 3. Arbre de décision

```
Vous avez besoin d'une vector database...

Étape 1 : C'est pour quoi ?
├── Prototype / cours / POC rapide → Chroma
└── Application réelle → Étape 2

Étape 2 : Où tourne votre app ?
├── Cloud uniquement, pas de maintenance infra → Pinecone
└── Self-hosted ou on-premise → Étape 3

Étape 3 : Vous avez déjà PostgreSQL ?
├── Oui, et volume < 2M vecteurs → pgvector (restez dans votre stack)
└── Non → Étape 4

Étape 4 : Quel volume de vecteurs ?
├── < 1 million → Chroma (si vous n'avez pas commencé) ou Qdrant
├── 1M à 100M → Qdrant
└── > 100M → Qdrant (cluster) ou FAISS

Étape 5 : Besoin de hybrid search (vectoriel + keyword) ?
├── Oui → Weaviate ou Qdrant (avec sparse vectors)
└── Non → Qdrant ou Chroma

Décision finale pour 90% des cas :
  - DEV/POC → Chroma
  - PROD → Qdrant
  - Déjà sur PostgreSQL et volume modéré → pgvector
  - SaaS sans infra → Pinecone
```

---

## 4. Considérations sur la scalabilité

### Volume de vecteurs vs performance

```
Vecteurs    | Dimension | RAM nécessaire (approx)
------------|-----------|------------------------
100,000     | 768       | ~300 MB
1,000,000   | 768       | ~3 GB
10,000,000  | 768       | ~30 GB
100,000,000 | 768       | ~300 GB (cluster nécessaire)
1,000,000   | 1536      | ~6 GB (double dimension = double RAM)
```

**Formule approximative** : `N vecteurs × D dimensions × 4 bytes (float32) / 1024³ = GB`
- 1M vecteurs × 768 dim × 4 = 3 GB (juste pour les vecteurs, sans index)
- Avec l'index HNSW, multiplier par ~1.5 à 2

### Stratégies pour réduire la consommation mémoire

```python
# 1. Réduire les dimensions (Matryoshka Embeddings)
# OpenAI text-embedding-3-small : 1536 → 256 dimensions
# Perte de qualité légère mais acceptable pour beaucoup de cas

# 2. Quantification (approximation)
# Stocker les vecteurs en int8 ou binary au lieu de float32
# Qdrant supporte la quantisation :

from qdrant_client.models import ScalarQuantizationConfig, ScalarType

client.update_collection(
    collection_name="ma_collection",
    quantization_config=ScalarQuantizationConfig(
        type=ScalarType.INT8,       # float32 (4 bytes) → int8 (1 byte) = 4x moins de RAM
        quantile=0.99,              # Percentile pour la plage de quantification
        always_ram=True             # Garder les vecteurs quantifiés en RAM
    )
)

# 3. Réduction de dimension (PCA)
from sklearn.decomposition import PCA
import numpy as np

# Entraîner PCA sur un échantillon représentatif
pca = PCA(n_components=256)
pca.fit(sample_embeddings)  # Votre échantillon

# Réduire toutes les embeddings
reduced_embeddings = pca.transform(all_embeddings)
print(f"Variance expliquée : {pca.explained_variance_ratio_.sum():.1%}")
```

---

## 5. Local vs Cloud : analyse des coûts

### Option 1 : Self-hosted Qdrant (VPS ou VM)

```
Infrastructure : VPS 16GB RAM, 4 vCPU, 100GB SSD
Coût mensuel : ~40-80€/mois (Hetzner, OVH, etc.)
Capacity : ~2-5M vecteurs de 768 dimensions

Avantages :
- Contrôle total des données
- Coût fixe prévisible
- Pas de limite de requêtes

Inconvénients :
- Maintenance (mises à jour, backups, monitoring)
- Vous gérez les incidents
```

### Option 2 : Qdrant Cloud (managé)

```
Free tier : 1 cluster gratuit, 1GB stockage
Starter  : ~25$/mois pour 4GB, 1 nœud
Growth   : ~95$/mois pour 16GB, 1 nœud
Custom   : sur devis (multi-nœuds, SLA)
```

### Option 3 : Pinecone

```
Free tier : 1 index, ~100K vecteurs de 1536 dim
Starter   : ~70$/mois pour 5M vecteurs
Standard  : à partir de ~0.096$ par heure
Enterprise: sur devis
```

### Option 4 : pgvector (si déjà PostgreSQL)

```
Si vous payez déjà pour PostgreSQL → coût additionnel = ~0
Extension gratuite, fonctionne sur votre instance existante
```

---

## 6. Benchmark de performance

*Résultats indicatifs — varient selon le matériel et la configuration*

```
Index : HNSW, 1M vecteurs de 768 dimensions
Matériel : 8 vCPU, 32GB RAM

Solution      | Latence P50 | Latence P99 | Recall@10 | QPS max
--------------|-------------|-------------|-----------|--------
Qdrant        | 2ms         | 8ms         | 0.98      | 2000
FAISS (IVF)   | 1ms         | 4ms         | 0.95      | 5000
Weaviate      | 3ms         | 12ms        | 0.97      | 1500
Chroma        | 5ms         | 25ms        | 0.96      | 500
pgvector      | 8ms         | 40ms        | 0.97      | 300

QPS = Queries Per Second
Recall@10 = fraction des 10 vrais plus proches voisins retrouvés
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer le site cloud.qdrant.io et pinecone.io, naviguer dans les dashboards cloud, comparer les plans tarifaires et montrer comment créer un cluster cloud en quelques clics.
> **Expliquer :** "La différence entre self-hosted et cloud managé, c'est la responsabilité opérationnelle. En cloud, vous payez pour ne pas gérer l'infrastructure. En self-hosted, vous payez moins mais vous êtes responsables des backups, des mises à jour et des incidents à 3h du matin."

---

## 7. Matrice de décision par profil

### Profil Data Engineer / ML Engineer débutant

```
Recommandation : Chroma + sentence-transformers
Raison : Installation pip install chromadb, API intuitive, intégration LangChain native
Quand migrer : quand vous dépassez ~1M vecteurs ou avez besoin de filtres avancés
```

### Profil Startup / Petit projet commercial

```
Recommandation : Qdrant self-hosted sur VPS (ou Qdrant Cloud free tier pour démarrer)
Raison : Meilleur rapport fonctionnalités/coût, performance production-ready
```

### Profil Grande entreprise, données sensibles

```
Recommandation : Qdrant self-hosted ou pgvector selon la stack existante
Raison : Contrôle total des données, conformité RGPD, déploiement on-premise possible
```

### Profil Chercheur / Data Scientist

```
Recommandation : FAISS pour les expériences large scale, Chroma pour les prototypes
Raison : FAISS offre le contrôle maximal sur les algorithmes d'indexation
```

### Profil Startup bien financée, go-to-market rapide

```
Recommandation : Pinecone
Raison : Zéro infrastructure à gérer, scale automatique, intégrations ready-to-use
```

---

## 8. Migration entre vector databases

Un avantage des vector databases est que vous pouvez migrer relativement facilement car LangChain abstrait la plupart des différences :

```python
# Migration Chroma → Qdrant via LangChain

# Étape 1 : Exporter depuis Chroma
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
chroma_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Récupérer tous les documents
all_docs = chroma_store.get()  # ou scroll si trop grand

# Étape 2 : Réinsérer dans Qdrant
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

qdrant_client = QdrantClient(host="localhost", port=6333)
qdrant_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="migrated_collection",
    embedding=embeddings
)

# Insérer les documents migrés
from langchain.schema import Document
docs_to_migrate = [
    Document(page_content=text, metadata=meta)
    for text, meta in zip(all_docs['documents'], all_docs['metadatas'])
]
qdrant_store.add_documents(docs_to_migrate)
print(f"Migration terminée : {len(docs_to_migrate)} documents transférés")
```

---

## Résumé

| Situation | Solution recommandée |
|-----------|---------------------|
| Prototype / cours | **Chroma** |
| Production Python, self-hosted | **Qdrant** |
| Déjà sur PostgreSQL | **pgvector** |
| No-ops, SaaS | **Pinecone** |
| Recherche ML, volume énorme | **FAISS** |
| Hybrid search avancé | **Weaviate** |

Le message clé : **commencez simple** (Chroma), et **migrez quand vous en avez besoin** (Qdrant, pgvector). Le sur-engineering prématuré est l'ennemi.
