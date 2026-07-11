# Sentence Transformers — Embeddings et recherche sémantique

## Qu'est-ce qu'un embedding de phrase ?

Les modèles BERT et ses variantes produisent des représentations vectorielles **dépendantes du contexte** pour chaque token. Mais pour comparer des phrases entières (similarité, recherche), on a besoin d'un **vecteur unique par phrase**.

`sentence-transformers` est une bibliothèque spécialisée qui entraîne des modèles à produire des vecteurs denses de haute qualité pour des phrases complètes.

```
"Le chat dort sur le canapé" → [0.23, -0.41, 0.87, ..., 0.12]  (384 ou 768 dimensions)
"Le félin repose sur le sofa" → [0.25, -0.39, 0.84, ..., 0.11]  (similaire !)
"La météo sera pluvieuse"     → [-0.12, 0.73, -0.23, ..., 0.67] (différent)
```

---

## Installation

```bash
pip install sentence-transformers
```

---

## Premier exemple

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Charger un modèle pré-entraîné
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Léger (22M params), rapide, très bon en anglais

# Encoder des phrases
phrases = [
    "Machine learning is transforming every industry.",
    "Artificial intelligence is revolutionizing businesses.",
    "I enjoy going for walks in the park.",
    "The weather today is cloudy with a chance of rain.",
    "Deep learning models require large amounts of data.",
]

# Obtenir les embeddings (shape : [n_phrases, 384])
embeddings = model.encode(phrases)
print(f"Shape : {embeddings.shape}")  # (5, 384)
print(f"Type  : {type(embeddings)}")  # numpy.ndarray

# Pour avoir des tenseurs PyTorch
embeddings_torch = model.encode(phrases, convert_to_tensor=True)
print(f"Type  : {type(embeddings_torch)}")  # torch.Tensor
```

---

## Modèles disponibles

```python
# Modèles populaires sur le Hub

modeles = {
    # ─── Anglais ───
    "all-MiniLM-L6-v2": {
        "dim": 384, "params": "22M",
        "note": "Très rapide, bon équilibre taille/qualité"
    },
    "all-mpnet-base-v2": {
        "dim": 768, "params": "110M",
        "note": "Meilleure qualité que MiniLM, plus lent"
    },
    "all-MiniLM-L12-v2": {
        "dim": 384, "params": "33M",
        "note": "Légèrement mieux que L6, légèrement plus lent"
    },
    # ─── Multilingue ───
    "paraphrase-multilingual-MiniLM-L12-v2": {
        "dim": 384, "params": "118M",
        "note": "50+ langues, dont le français"
    },
    "paraphrase-multilingual-mpnet-base-v2": {
        "dim": 768, "params": "278M",
        "note": "50+ langues, très haute qualité"
    },
    # ─── Français ───
    "dangvantuan/vietnamese-embedding": {
        "dim": 768, "params": "110M",
        "note": "Spécialisé, exemple de modèle custom"
    },
    # ─── Très grands modèles ───
    "BAAI/bge-large-en-v1.5": {
        "dim": 1024, "params": "335M",
        "note": "État de l'art en anglais (2024)"
    },
    "intfloat/multilingual-e5-large": {
        "dim": 1024, "params": "560M",
        "note": "État de l'art multilingue"
    },
}

# Charger le modèle multilingue pour les exemples français
model_fr = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
```

---

## Similarité cosinus

La **similarité cosinus** est la métrique standard pour comparer des embeddings. Elle mesure l'angle entre deux vecteurs (1 = identiques, 0 = orthogonaux, -1 = opposés).

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import torch

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Paires de phrases
paires = [
    ("Le chat dort sur le canapé.",          "Le félin repose sur le sofa."),
    ("J'adore la pizza italienne.",           "La pizza est mon plat préféré."),
    ("J'adore la pizza italienne.",           "Il fait beau aujourd'hui."),
    ("La réunion est annulée.",               "Le meeting est supprimé."),
    ("Python est un langage de programmation.", "Le serpent python vit en Asie."),
]

print(f"{'Phrase 1':35s}  {'Phrase 2':35s}  Similarité")
print("-" * 85)

for phrase1, phrase2 in paires:
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    sim = cos_sim(emb1, emb2).item()
    print(f"{phrase1[:33]:35s}  {phrase2[:33]:35s}  {sim:.4f}")
```

Sortie attendue :
```
Le chat dort sur le canapé.         Le félin repose sur le sofa.         0.8934
J'adore la pizza italienne.         La pizza est mon plat préféré.        0.8721
J'adore la pizza italienne.         Il fait beau aujourd'hui.             0.1247
La réunion est annulée.             Le meeting est supprimé.              0.9102
Python est un langage de progr...   Le serpent python vit en Asie.        0.4823
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une heatmap de matrice de similarité cosinus pour 8-10 phrases couvrant 3 thèmes différents (technologie, cuisine, sport) — les blocs diagonaux thématiques doivent apparaître clairement en rouge/chaud
> **Expliquer :** Ce que la matrice révèle (les phrases du même thème ont une forte similarité), le concept d'espace sémantique (les vecteurs similaires sont proches), et pourquoi la similarité cosinus est meilleure que la distance euclidienne pour comparer des embeddings (invariante à la norme)

---

## Recherche sémantique — Cas d'usage fondamental

```python
from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# ─── Base de connaissance (corpus) ───
corpus = [
    "Python est un langage de programmation interprété créé par Guido van Rossum.",
    "Le machine learning est un sous-domaine de l'intelligence artificielle.",
    "PyTorch est une bibliothèque de deep learning développée par Facebook.",
    "Les réseaux de neurones sont inspirés du cerveau humain.",
    "Le fine-tuning consiste à adapter un modèle pré-entraîné à une tâche spécifique.",
    "BERT est un modèle de type encodeur entraîné sur du texte masqué.",
    "La tokenisation découpe le texte en sous-mots appelés tokens.",
    "Les transformers utilisent le mécanisme d'attention pour contextualiser les tokens.",
    "Le gradient descent est l'algorithme d'optimisation de base du deep learning.",
    "L'overfitting survient quand un modèle mémorise les données d'entraînement.",
]

# ─── Encoder le corpus (une seule fois, à mettre en cache) ───
corpus_embeddings = model.encode(corpus, convert_to_tensor=True, show_progress_bar=True)
print(f"Corpus encodé : {corpus_embeddings.shape}")  # [10, 384]

# ─── Requêtes ───
requetes = [
    "Comment fonctionne l'attention dans les transformers ?",
    "Qu'est-ce que le surentraînement ?",
    "Comment adapter un LLM à mon domaine ?",
    "Quel framework utiliser pour entraîner des réseaux de neurones ?",
]

print("\n" + "="*70)
for requete in requetes:
    # Encoder la requête
    query_embedding = model.encode(requete, convert_to_tensor=True)

    # Calculer les similarités avec tout le corpus
    similarities = util.cos_sim(query_embedding, corpus_embeddings)[0]

    # Top-3 résultats
    top_k = torch.topk(similarities, k=3)
    print(f"\nRequête : {requete}")
    for score, idx in zip(top_k.values, top_k.indices):
        print(f"  [{score:.3f}] {corpus[idx]}")
```

---

## Recherche sémantique à grande échelle avec FAISS

Pour des corpus de millions de documents, la recherche par similarité cosinus exhaustive devient trop lente. **FAISS** (Facebook AI Similarity Search) permet une recherche approximative en temps sous-linéaire.

```bash
pip install faiss-cpu  # CPU
# pip install faiss-gpu  # GPU (plus rapide)
```

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# ─── Construire l'index FAISS ───
def build_faiss_index(documents: list[str]):
    """Construit un index FAISS pour la recherche sémantique"""
    # Encoder tous les documents
    embeddings = model.encode(documents, show_progress_bar=True, batch_size=256)
    embeddings = embeddings.astype(np.float32)

    # Normaliser les vecteurs (pour similarité cosinus = produit scalaire)
    faiss.normalize_L2(embeddings)

    # Créer l'index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product = cosinus sur vecteurs normalisés

    # Pour grands corpus : IndexIVFFlat (quantization + clustering)
    # nlist = 100  # Nombre de clusters
    # quantizer = faiss.IndexFlatIP(dimension)
    # index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
    # index.train(embeddings)  # Nécessaire pour IVF

    index.add(embeddings)
    print(f"Index créé : {index.ntotal} vecteurs de dimension {dimension}")
    return index

# ─── Rechercher ───
def semantic_search_faiss(query: str, index, documents: list[str], top_k: int = 5):
    """Recherche sémantique avec FAISS"""
    query_embedding = model.encode([query], normalize_embeddings=True).astype(np.float32)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:  # FAISS retourne -1 si résultat non trouvé
            results.append({
                "score"   : float(score),
                "index"   : int(idx),
                "document": documents[idx],
            })
    return results

# Exemple avec un corpus fictif
documents = [
    "Guide d'installation de Python sur Ubuntu",
    "Introduction au machine learning avec scikit-learn",
    "Deep learning avec PyTorch : premier réseau de neurones",
    "Comment optimiser les hyperparamètres avec Optuna",
    "Déploiement d'un modèle ML avec FastAPI et Docker",
    "Transfer learning avec BERT pour la classification",
    "Traitement du langage naturel : tokenisation et embeddings",
    "Réseaux convolutifs pour la classification d'images",
    "Reinforcement learning : introduction à Q-Learning",
    "Séries temporelles avec LSTM et Prophet",
] * 1000  # Simuler un grand corpus (10 000 documents)

index = build_faiss_index(documents)

results = semantic_search_faiss(
    "Comment faire de la classification de texte ?",
    index, documents
)
for r in results:
    print(f"[{r['score']:.3f}] {r['document']}")
```

---

## Bi-Encodeur vs Cross-Encodeur

```python
# ─── Bi-Encodeur (Sentence Transformers) ───
# Encode query et document INDÉPENDAMMENT → rapide mais moins précis
# Utilisé pour le premier filtrage (retrieval)

from sentence_transformers import SentenceTransformer
bi_encoder = SentenceTransformer("all-MiniLM-L6-v2")

query_emb = bi_encoder.encode("Quelle est la capitale de la France ?")
doc_emb = bi_encoder.encode("Paris est la capitale de la France.")
score_bi = float(util.cos_sim(query_emb, doc_emb))

# ─── Cross-Encodeur ───
# Encode query ET document ENSEMBLE → plus précis mais plus lent
# Utilisé pour le re-ranking (après le bi-encodeur)

from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

score_cross = cross_encoder.predict([("Quelle est la capitale de la France ?",
                                      "Paris est la capitale de la France.")])

print(f"Bi-Encoder score  : {score_bi:.4f}")
print(f"Cross-Encoder score: {score_cross[0]:.4f}")

# ─── Pipeline hybride (recommandé pour la production) ───
def two_stage_search(query, documents, top_k_retrieval=50, top_k_final=5):
    """
    Etape 1 : Bi-encodeur pour filtrer rapidement
    Etape 2 : Cross-encodeur pour re-ranker les meilleurs résultats
    """
    # Etape 1 : Retrieval rapide
    query_emb = bi_encoder.encode(query, convert_to_tensor=True)
    doc_embs = bi_encoder.encode(documents, convert_to_tensor=True)
    scores_1 = util.cos_sim(query_emb, doc_embs)[0]
    top_indices = torch.topk(scores_1, k=min(top_k_retrieval, len(documents))).indices

    # Etape 2 : Re-ranking précis
    candidate_docs = [documents[i] for i in top_indices]
    pairs = [(query, doc) for doc in candidate_docs]
    scores_2 = cross_encoder.predict(pairs)

    # Trier par score cross-encoder
    ranked = sorted(zip(scores_2, candidate_docs), reverse=True)
    return ranked[:top_k_final]
```

---

## Clustering sémantique

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

textes = [
    # Technologie
    "Python est utilisé pour le machine learning.",
    "Les GPU accélèrent l'entraînement des réseaux de neurones.",
    "PyTorch facilite la construction de modèles de deep learning.",
    "Le cloud computing permet de scaler les applications.",
    # Cuisine
    "La blanquette de veau est un classique de la cuisine française.",
    "Faire du pain au levain demande du temps mais c'est délicieux.",
    "Le wok permet de cuisiner rapidement à haute température.",
    "Les épices indiennes donnent du caractère aux plats.",
    # Sport
    "Le Tour de France est la course cycliste la plus prestigieuse.",
    "La préparation physique est essentielle pour les sportifs.",
    "La natation est un sport complet qui travaille tout le corps.",
    "L'entraînement fractionné améliore les performances cardio.",
]

embeddings = model.encode(textes)

# Clustering K-Means (3 catégories)
n_clusters = 3
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
labels = kmeans.fit_predict(embeddings)

# Afficher les clusters
print("Résultats du clustering :")
for cluster_id in range(n_clusters):
    print(f"\nCluster {cluster_id} :")
    for texte, label in zip(textes, labels):
        if label == cluster_id:
            print(f"  - {texte}")

# Visualisation 2D avec PCA
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

plt.figure(figsize=(12, 8))
colors = ["#e74c3c", "#2ecc71", "#3498db"]
for i, (x, y) in enumerate(embeddings_2d):
    cluster = labels[i]
    plt.scatter(x, y, color=colors[cluster], s=100, alpha=0.8)
    plt.annotate(textes[i][:30] + "...", (x, y), textcoords="offset points",
                 xytext=(5, 5), fontsize=8)

plt.title("Clustering sémantique (PCA 2D)")
plt.xlabel("Composante 1")
plt.ylabel("Composante 2")
plt.savefig("clustering_semantique.png", dpi=150, bbox_inches="tight")
plt.show()
```

---

## Fine-tuner un modèle Sentence Transformers

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Charger le modèle de base
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# ─── Données d'entraînement ───
# Paires (phrase1, phrase2, score de similarité 0-1)
train_examples = [
    InputExample(texts=["Le chat mange.", "Le félin s'alimente."], label=0.9),
    InputExample(texts=["Il pleut.", "Il fait beau."], label=0.1),
    InputExample(texts=["J'aime Python.", "Python est mon langage favori."], label=0.85),
    InputExample(texts=["La voiture roule.", "Le train siffle."], label=0.2),
    InputExample(texts=["Le machine learning est complexe.", "L'IA est difficile à maîtriser."], label=0.8),
]

# ─── DataLoader ───
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# ─── Loss function ───
# CosineSimilarityLoss : minimise la différence entre cos_sim prédit et label
train_loss = losses.CosineSimilarityLoss(model)

# Pour les paires positives/négatives (pas de score continu) :
# train_loss = losses.ContrastiveLoss(model)
# Pour triplets (anchor, positive, negative) :
# train_loss = losses.TripletLoss(model)

# ─── Entraîner ───
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=100,
    output_path="./models/sentence-transformer-fr-custom/",
    show_progress_bar=True,
)

print("Modèle fine-tuné sauvegardé !")
```

---

## Application complète — FAQ sémantique

```python
from sentence_transformers import SentenceTransformer, util
import torch

class FAQSemanticSearch:
    """Moteur de recherche sémantique pour une FAQ"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.questions = []
        self.answers = []
        self.question_embeddings = None

    def add_faq(self, faq: list[dict]):
        """Ajoute des entrées FAQ sous forme [{'question': ..., 'answer': ...}]"""
        self.questions = [item["question"] for item in faq]
        self.answers = [item["answer"] for item in faq]
        self.question_embeddings = self.model.encode(
            self.questions, convert_to_tensor=True
        )
        print(f"FAQ indexée : {len(self.questions)} entrées")

    def search(self, user_query: str, top_k: int = 3, threshold: float = 0.5) -> list[dict]:
        """Recherche les réponses les plus pertinentes"""
        query_emb = self.model.encode(user_query, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, self.question_embeddings)[0]

        top = torch.topk(scores, k=min(top_k, len(self.questions)))

        results = []
        for score, idx in zip(top.values, top.indices):
            score_val = score.item()
            if score_val >= threshold:
                results.append({
                    "score"   : score_val,
                    "question": self.questions[idx],
                    "answer"  : self.answers[idx],
                })

        return results


# Test
faq_data = [
    {"question": "Comment réinitialiser mon mot de passe ?",
     "answer": "Cliquez sur 'Mot de passe oublié' sur la page de connexion."},
    {"question": "Quels sont les délais de livraison ?",
     "answer": "La livraison standard prend 3-5 jours ouvrés."},
    {"question": "Puis-je retourner un article ?",
     "answer": "Oui, vous avez 30 jours pour retourner tout article non utilisé."},
    {"question": "Comment contacter le service client ?",
     "answer": "Par email à support@exemple.fr ou par téléphone au 01 23 45 67 89."},
    {"question": "Comment suivre ma commande ?",
     "answer": "Un lien de suivi est envoyé par email dès l'expédition."},
]

faq = FAQSemanticSearch()
faq.add_faq(faq_data)

test_queries = [
    "J'ai oublié mon identifiant",
    "Quand vais-je recevoir ma commande ?",
    "Je veux annuler ma commande",  # Pas dans la FAQ → faible score
    "Besoin d'aide pour me connecter",
]

for query in test_queries:
    print(f"\nQ: {query}")
    results = faq.search(query, top_k=2, threshold=0.4)
    if results:
        for r in results:
            print(f"  [{r['score']:.3f}] {r['question']}")
            print(f"           → {r['answer']}")
    else:
        print("  Aucune réponse pertinente trouvée (score trop faible)")
```

---

## Suite du cours

Les exercices pratiques se trouvent dans le dossier [../exercices/](../exercices/). Commencer par [exercice-01-classification.md](../exercices/exercice-01-classification.md) pour pratiquer le fine-tuning complet d'un classifieur de sentiment.
