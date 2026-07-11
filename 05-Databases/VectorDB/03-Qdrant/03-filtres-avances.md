# Qdrant — Filtres avancés et gestion des payloads

## 1. Filtres avancés sur les payloads

### 1.1 Filtres combinés (AND, OR, NOT)

```python
from qdrant_client.models import (
    Filter, FieldCondition, MatchValue, MatchAny, Range,
    IsNullCondition, IsEmptyCondition
)

# Filtre complexe : (categorie = "devops" OR categorie = "databases") AND popularite >= 8.5
results = client.search(
    collection_name="tech_articles",
    query_vector=query_vector,
    query_filter=Filter(
        must=[
            # Condition "popularite >= 8.5"
            FieldCondition(
                key="popularite",
                range=Range(gte=8.5)
            )
        ],
        should=[  # Au moins une doit être vraie (OR)
            FieldCondition(key="categorie", match=MatchValue(value="devops")),
            FieldCondition(key="categorie", match=MatchValue(value="databases"))
        ],
        must_not=[  # Aucune ne doit être vraie (NOT)
            FieldCondition(key="source", match=MatchValue(value="deprecated.com"))
        ]
    ),
    limit=5,
    with_payload=True
)
```

### 1.2 Filtre par liste de valeurs

```python
# Filtre par liste de valeurs
results = client.search(
    collection_name="tech_articles",
    query_vector=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="categorie",
                match=MatchAny(any=["devops", "databases", "frameworks"])
            )
        ]
    ),
    limit=5
)
```

### 1.3 Filtre par plage de valeurs numériques

```python
# Filtre par plage de valeurs numériques
results = client.search(
    collection_name="tech_articles",
    query_vector=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="annee",
                range=Range(gte=2023, lte=2025)
            ),
            FieldCondition(
                key="popularite",
                range=Range(gt=8.0)  # Strictement supérieur à 8.0
            )
        ]
    ),
    limit=5
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le dashboard Qdrant dans le navigateur (`http://localhost:6333/dashboard`), naviguer dans la collection créée, afficher la liste des points avec leurs payloads, puis utiliser l'onglet "Search" du dashboard pour lancer une requête vectorielle visuellement.
> **Expliquer :** "Le dashboard Qdrant permet de naviguer dans vos données visuellement sans écrire de code. Vous pouvez voir chaque point, son payload complet, et même lancer des recherches interactives. C'est indispensable pour déboguer en développement."

---

## 2. Gestion des payloads et indexation

### 2.1 Ajouter un index sur un champ payload

Sans index payload, les filtres fonctionnent mais sont lents car Qdrant doit scanner tous les points. Avec un index, les filtres sont quasi-instantanés.

```python
from qdrant_client.models import PayloadSchemaType

# Créer un index sur le champ "categorie" (pour accélérer les filtres)
client.create_payload_index(
    collection_name="tech_articles",
    field_name="categorie",
    field_schema=PayloadSchemaType.KEYWORD  # Pour les chaînes exactes
)

# Index pour les valeurs numériques
client.create_payload_index(
    collection_name="tech_articles",
    field_name="popularite",
    field_schema=PayloadSchemaType.FLOAT
)

# Index pour le texte full-text (recherche par mots-clés dans le payload)
from qdrant_client.models import TextIndexParams, TokenizerType

client.create_payload_index(
    collection_name="tech_articles",
    field_name="text",
    field_schema=TextIndexParams(
        type="text",
        tokenizer=TokenizerType.WORD,
        lowercase=True,
        min_token_len=2,
    )
)
```

### 2.2 Types d'index disponibles

| Type | Cas d'usage | Exemple |
|------|-------------|---------|
| `KEYWORD` | Correspondance exacte sur strings | categorie, status, type |
| `INTEGER` | Plages de valeurs entières | annee, version |
| `FLOAT` | Plages de valeurs décimales | score, prix, popularite |
| `BOOL` | Valeurs booléennes | is_active, is_published |
| `GEO` | Coordonnées GPS (lat/lon) | localisation |
| `TEXT` | Full-text search | contenu, description |
| `DATETIME` | Dates et timestamps | created_at, updated_at |

### 2.3 Mettre à jour des payloads

```python
# Mettre à jour un champ spécifique d'un point
client.set_payload(
    collection_name="tech_articles",
    payload={"popularite": 9.8, "updated_at": "2024-12-01"},
    points=[1]  # IDs des points à mettre à jour
)

# Supprimer des champs du payload
client.delete_payload(
    collection_name="tech_articles",
    keys=["deprecated_field"],
    points=[1, 2, 3]
)

# Mettre à jour des payloads avec un filtre
client.set_payload(
    collection_name="tech_articles",
    payload={"reviewed": True},
    points=Filter(
        must=[FieldCondition(key="categorie", match=MatchValue(value="devops"))]
    )
)
```

---

## 3. Optimisation mémoire

### 3.1 Quantification des vecteurs

```python
from qdrant_client.models import ScalarQuantizationConfig, ScalarType

client.update_collection(
    collection_name="ma_collection",
    quantization_config=ScalarQuantizationConfig(
        type=ScalarType.INT8,       # float32 (4 bytes) → int8 (1 byte) = 4x moins de RAM
        quantile=0.99,              # Percentile pour la plage de quantification
        always_ram=True             # Garder les vecteurs quantifiés en RAM
    )
)
```

### 3.2 Estimation de la consommation mémoire

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
- Avec l'index HNSW, multiplier par ~1.5 à 2

---

## Résumé

Qdrant excelle quand vous avez besoin de :
- **Filtres complexes** sur des payloads riches
- **Performance en production** avec des millions de vecteurs
- **Interface web** pour superviser et déboguer
- **Déploiement flexible** (local, Docker, cloud)
- **Scalabilité** (sharding, réplication)
