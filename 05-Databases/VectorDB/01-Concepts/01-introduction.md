# 01 — Introduction aux Bases de Données Vectorielles

## Pourquoi ce module existe

Depuis 2022-2023, les Large Language Models (LLM) ont transformé l'industrie du logiciel. Avec eux, une nouvelle famille d'outils est devenue indispensable : les **bases de données vectorielles**. Elles sont le moteur silencieux derrière ChatGPT with browsing, les assistants documentaires, les moteurs de recommandation intelligents, et les systèmes de recherche sémantique.

Ce chapitre pose les bases conceptuelles. Avant d'écrire une ligne de code, il est essentiel de comprendre **pourquoi** ces outils existent et **quel problème** ils résolvent.

---

## 1. Le problème des bases de données classiques

Une base de données relationnelle (PostgreSQL, MySQL) fonctionne sur un principe de correspondance exacte :

```sql
SELECT * FROM articles WHERE title LIKE '%intelligence artificielle%';
```

Ce type de requête ne trouvera jamais un article dont le titre est "machine learning et deep learning" même si le contenu est parfaitement pertinent. Les bases documentaires (MongoDB, Elasticsearch) améliorent légèrement les choses avec la recherche full-text, mais restent fondamentalement basées sur des mots-clés.

**Le problème fondamental** : les données non structurées (textes, images, sons) ont un *sens* que les bases de données classiques ne peuvent pas capturer. Elles stockent des chaînes de caractères, pas de la sémantique.

### Comparaison illustrée

| Requête | Résultat BDD classique | Résultat Vector DB |
|---------|----------------------|-------------------|
| "voiture rapide" | Trouve "voiture rapide" uniquement | Trouve aussi "automobile sportive", "véhicule haute performance", "supercar" |
| "problème de connexion" | Trouve "problème de connexion" | Trouve aussi "erreur réseau", "impossible de se connecter", "timeout" |
| "repas sain" | Trouve "repas sain" | Trouve aussi "alimentation équilibrée", "diète méditerranéenne", "nutrition" |

---

## 2. Qu'est-ce qu'un embedding vectoriel ?

Un **embedding** est une représentation numérique d'une donnée (texte, image, son) sous forme d'un vecteur de nombres réels en haute dimension. C'est un modèle de machine learning qui effectue cette transformation.

### Intuition géométrique

Imaginez que chaque phrase ou document est un **point dans un espace à N dimensions**. Les modèles d'embedding sont entraînés de telle sorte que :

- Deux textes avec un **sens similaire** → points **proches** dans l'espace
- Deux textes avec un **sens différent** → points **éloignés** dans l'espace

```
Espace 2D simplifié (en réalité 384 à 3072 dimensions) :

"chien"     ●                    ● "voiture"
"chat"    ●                   ●  "moto"
"animal" ●                  ●   "véhicule"

      Cluster "animaux"       Cluster "transport"
```

### Exemple concret

Le texte "Le chat dort sur le canapé" est transformé en un vecteur comme :

```python
[0.023, -0.145, 0.891, 0.002, -0.334, 0.712, ..., 0.089]
# 384 ou 1536 ou 3072 dimensions selon le modèle
```

Ce vecteur encode le *sens* de la phrase. Un modèle bien entraîné placera "Le félin sommeille sur le sofa" très proche de ce vecteur.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le site [projector.tensorflow.org](https://projector.tensorflow.org/) et naviguer dans la visualisation 3D des embeddings de mots.
> **Expliquer :** "Regardez comment les mots similaires se regroupent naturellement dans l'espace vectoriel. Les pays sont proches les uns des autres, les verbes d'action ensemble, etc. Les embeddings de texte modernes font exactement ça, mais en 384 ou 1536 dimensions."

---

## 3. Architecture d'une Vector Database

Une vector database n'est pas simplement un tableau de vecteurs. Elle est conçue pour répondre efficacement à la question :

> "Parmi des millions de vecteurs, quels sont les K plus proches de ce vecteur requête ?"

C'est le problème du **k-Nearest Neighbor** (kNN).

### Le défi de l'échelle

Avec 1 million de vecteurs de 1536 dimensions, une recherche exhaustive signifie **1.5 milliard de multiplications** pour chaque requête. C'est trop lent.

### La solution : Approximate Nearest Neighbor (ANN)

Les vector databases utilisent des **index spécialisés** qui permettent de trouver les voisins *approximativement* proches en un temps bien inférieur, avec un excellent rappel (recall) :

| Algorithme | Description | Utilisé par |
|-----------|-------------|-------------|
| **HNSW** | Hierarchical Navigable Small World — graphe multi-couches | Qdrant, Chroma, Weaviate |
| **IVF** | Inverted File Index — clustering + recherche locale | FAISS |
| **LSH** | Locality Sensitive Hashing — hachage probabiliste | Anciennes solutions |
| **ScaNN** | Scalable Approximate Nearest Neighbor (Google) | Solutions Google |

**HNSW** est aujourd'hui le standard de facto pour sa combinaison vitesse/précision.

```
HNSW — structure simplifiée :

Couche 2 (peu de nœuds) :  A --------- B
                                \      /
Couche 1 :                  C -- D -- E -- F
                           / \  / \  / \  / \
Couche 0 (tous les vecteurs): G H I J K L M N O P ...

Recherche : partir d'un point en haut, descendre couche par couche vers le plus proche
```

---

## 4. Les métriques de distance

Pour calculer la "proximité" entre deux vecteurs, plusieurs métriques existent. Le choix dépend du cas d'usage et du modèle d'embedding utilisé.

### 4.1 Similarité cosinus (Cosine Similarity)

Mesure l'**angle** entre deux vecteurs, ignorant leur magnitude (longueur).

```
cos(θ) = (A · B) / (||A|| × ||B||)

Résultat : entre -1 et 1
  1   = même direction (très similaires)
  0   = perpendiculaires (non liés)
 -1   = directions opposées (sens opposé)
```

```python
import numpy as np

def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

# Exemple
v1 = np.array([1.0, 0.5, 0.3])
v2 = np.array([0.9, 0.6, 0.2])
v3 = np.array([-1.0, -0.5, -0.3])  # opposé de v1

print(cosine_similarity(v1, v2))  # 0.997 — très similaires
print(cosine_similarity(v1, v3))  # -1.0  — opposés
```

**Quand l'utiliser** : texte (la direction compte, pas la magnitude). C'est la métrique par défaut de la plupart des modèles NLP.

### 4.2 Distance euclidienne (L2)

Mesure la **distance géométrique** réelle entre deux points dans l'espace.

```
d(A, B) = √(Σ(Aᵢ - Bᵢ)²)

Résultat : entre 0 et +∞
  0   = points identiques
  +∞  = très éloignés
```

```python
def euclidean_distance(v1, v2):
    return np.linalg.norm(np.array(v1) - np.array(v2))

# Ou avec scipy
from scipy.spatial.distance import euclidean
d = euclidean(v1, v2)
```

**Quand l'utiliser** : images, données continues où la magnitude a de l'importance, clustering K-means.

### 4.3 Produit scalaire (Dot Product / Inner Product)

```
A · B = Σ(Aᵢ × Bᵢ)

Résultat : peut être négatif
```

```python
def dot_product(v1, v2):
    return np.dot(np.array(v1), np.array(v2))
```

**Quand l'utiliser** : quand les embeddings sont normalisés (longueur = 1). Dans ce cas, le dot product est équivalent à la similarité cosinus mais plus rapide. Recommandé par OpenAI pour leurs embeddings.

### 4.4 Tableau récapitulatif

| Métrique | Plage | Meilleur score | Cas d'usage typique |
|---------|-------|---------------|-------------------|
| Cosinus | [-1, 1] | 1 | Texte, documents |
| Euclidienne | [0, +∞] | 0 | Images, données géospatiales |
| Dot Product | (-∞, +∞) | +∞ | Embeddings normalisés, recommandation |

---

## 5. Cas d'usage principaux

### 5.1 Recherche sémantique (Semantic Search)

Au lieu de chercher des mots-clés exacts, on cherche des documents **sémantiquement proches** d'une requête.

```
Application : moteur de recherche d'une base de connaissance interne
Requête utilisateur → embedding → recherche vectorielle → top-K documents pertinents
```

Exemples réels :
- Notion AI : retrouver des notes similaires
- GitHub Copilot : retrouver du code similaire dans le repository
- Recherche interne d'entreprise sur des milliers de documents

### 5.2 RAG — Retrieval-Augmented Generation

Le pattern le plus important avec les LLM aujourd'hui :

```
1. Ingestion : Documents → Embeddings → Vector DB
2. Requête :
   Question utilisateur
       ↓ embedding
   Vector DB (recherche top-K documents pertinents)
       ↓
   Contexte pertinent + Question → LLM → Réponse fondée sur les documents
```

Pourquoi RAG plutôt que fine-tuning ?
- Moins cher (pas de réentraînement)
- Données mises à jour en temps réel
- Sources citables (grounding)
- Réduit les hallucinations

### 5.3 Recommandations

```
Netflix/Spotify-like :
1. Chaque film/musique → embedding de ses caractéristiques
2. Chaque utilisateur → embedding de son historique
3. Recommander les items les plus proches de l'embedding utilisateur
```

### 5.4 Détection de doublons / déduplication

```python
# Identifier des documents quasi-identiques dans une large base
# embedding(doc1) cosine_similarity embedding(doc2) > 0.95 → probablement doublon
```

### 5.5 Classification zero-shot

```python
# Classer un document sans exemples d'entraînement
# embedding(document) → chercher la classe la plus proche parmi les classes candidates
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démontrer un cas RAG simple en live : poser une question sur un document que le LLM ne connaît pas (ex : un document interne inventé), montrer que sans RAG la réponse est fausse/inventée, puis avec RAG elle est correcte et sourcée.
> **Expliquer :** "Sans RAG, le LLM 'hallucine' car il ne connaît pas ce document. Avec RAG, on lui injecte le contexte pertinent. La vector database est ce qui nous permet de retrouver ce contexte rapidement parmi des milliers de documents."

---

## 6. Le flux complet d'une vector database

```
PHASE D'INGESTION (une fois) :
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Documents  │ →  │  Modèle Embedding │ →  │   Vector DB      │
│  (textes,   │    │  (transforme en   │    │  (stocke vecteurs│
│  PDFs, etc) │    │   vecteur float)  │    │   + métadonnées) │
└─────────────┘    └──────────────────┘    └──────────────────┘

PHASE DE REQUÊTE (à chaque question) :
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────┐
│  Requête    │ →  │  Même modèle     │ →  │  Recherche ANN   │ →  │ Top-K   │
│  utilisateur│    │  d'embedding     │    │  (index HNSW)    │    │ résultats│
└─────────────┘    └──────────────────┘    └──────────────────┘    └─────────┘
```

Points clés :
- **Le même modèle d'embedding** doit être utilisé pour l'ingestion ET la requête
- L'index ANN (HNSW, IVF...) est construit pendant l'ingestion
- La recherche retourne les K documents avec les **scores de similarité**

---

## 7. Vocabulaire essentiel

| Terme | Définition |
|-------|-----------|
| **Embedding** | Représentation vectorielle d'une donnée |
| **Dimension** | Nombre de valeurs dans un vecteur (ex: 1536) |
| **Collection** | Ensemble de vecteurs d'une même "table" |
| **kNN** | k-Nearest Neighbors : trouver les K plus proches voisins |
| **ANN** | Approximate Nearest Neighbor : version rapide de kNN |
| **HNSW** | Algorithme d'indexation standard pour les vector DBs |
| **Payload / Metadata** | Données structurées attachées à un vecteur (titre, date, source...) |
| **Score** | Valeur de similarité entre le vecteur requête et un résultat |
| **Chunking** | Découpage de documents longs en morceaux avant embedding |
| **RAG** | Retrieval-Augmented Generation |

---

## 8. Premiers pas : visualiser des embeddings

Avant de plonger dans les outils, voici un exercice mental. Installez et lancez ce script pour voir des embeddings en action :

```python
# pip install sentence-transformers matplotlib scikit-learn
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

# Modèle léger, 100% local
model = SentenceTransformer('all-MiniLM-L6-v2')

# Phrases à comparer
phrases = [
    "Le chat dort sur le canapé",
    "Le félin sommeille sur le sofa",
    "La voiture roule vite",
    "L'automobile accélère rapidement",
    "Il pleut des cordes ce soir",
    "Le temps est très pluvieux aujourd'hui",
]

# Générer les embeddings (vecteurs de 384 dimensions)
embeddings = model.encode(phrases)
print(f"Shape des embeddings : {embeddings.shape}")
# → (6, 384)

# Réduire à 2 dimensions pour visualisation
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

# Visualiser
plt.figure(figsize=(10, 7))
colors = ['blue', 'blue', 'red', 'red', 'green', 'green']
for i, (phrase, color) in enumerate(zip(phrases, colors)):
    x, y = embeddings_2d[i]
    plt.scatter(x, y, c=color, s=100)
    plt.annotate(phrase[:30], (x, y), textcoords="offset points",
                xytext=(0, 10), fontsize=8)

plt.title("Visualisation 2D des embeddings (PCA)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("embeddings_visualization.png")
plt.show()

# Calculer les similarités
from sklearn.metrics.pairwise import cosine_similarity
sim_matrix = cosine_similarity(embeddings)

print("\nMatrice de similarité :")
for i, phrase in enumerate(phrases):
    for j, phrase2 in enumerate(phrases):
        if i < j:
            print(f"{phrase[:25]:<25} ↔ {phrase2[:25]:<25} : {sim_matrix[i][j]:.3f}")
```

Vous devriez observer :
- Les paires de phrases similaires ont une similarité proche de **0.8 à 0.95**
- Les phrases non liées ont une similarité proche de **0.1 à 0.3**
- Sur le graphe PCA, les phrases similaires sont **proches physiquement**

---

## Résumé

- Les bases de données classiques ne comprennent pas le **sens** des données
- Les embeddings transforment du texte (ou des images) en **vecteurs numériques** qui capturent la sémantique
- Une vector database stocke ces vecteurs et permet des **recherches par similarité** efficaces grâce aux index ANN (HNSW)
- Les trois métriques principales : **cosinus** (texte), **euclidienne** (images), **dot product** (embeddings normalisés)
- Les cas d'usage clés : RAG, recherche sémantique, recommandations, déduplication

**Prochain chapitre** : comment générer des embeddings de qualité avec OpenAI et sentence-transformers.
