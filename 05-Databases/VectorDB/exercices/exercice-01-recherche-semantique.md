# Exercice 01 — Moteur de recherche sémantique

## Objectif

Construire de A à Z un **moteur de recherche sémantique** sur un corpus de documents texte. L'utilisateur tape une requête en langage naturel et le système retourne les documents les plus pertinents, même si les mots exacts ne correspondent pas.

**Durée estimée** : 2h à 3h

---

## Contexte

Vous travaillez pour une entreprise qui possède une base de connaissance interne : des fiches techniques, des guides utilisateur et des articles de blog. Les employés passent trop de temps à trouver l'information pertinente avec la recherche par mots-clés classique.

Votre mission : construire un moteur de recherche sémantique qui comprend l'intention des requêtes.

---

## Prérequis

```bash
pip install chromadb sentence-transformers rich
```

---

## Partie 1 : Préparer les données (20 min)

### Étape 1.1 — Créer le corpus

Créez un fichier `corpus.py` avec les documents suivants :

```python
# corpus.py

DOCUMENTS = [
    {
        "id": "doc_001",
        "title": "Guide d'installation Python",
        "content": "Pour installer Python sur Ubuntu, ouvrez un terminal et tapez : sudo apt-get update && sudo apt-get install python3 python3-pip. Vérifiez l'installation avec python3 --version.",
        "categorie": "python",
        "niveau": "debutant",
        "auteur": "Équipe Tech"
    },
    {
        "id": "doc_002",
        "title": "Comprendre les environnements virtuels",
        "content": "Un environnement virtuel Python isole les dépendances d'un projet. Créez-en un avec python -m venv mon_env, activez-le avec source mon_env/bin/activate (Linux/Mac) ou mon_env\\Scripts\\activate (Windows).",
        "categorie": "python",
        "niveau": "debutant",
        "auteur": "Équipe Tech"
    },
    {
        "id": "doc_003",
        "title": "Introduction aux décorateurs Python",
        "content": "Les décorateurs modifient le comportement d'une fonction sans modifier son code. Un décorateur est une fonction qui prend une fonction en paramètre et retourne une nouvelle fonction enrichie.",
        "categorie": "python",
        "niveau": "intermediaire",
        "auteur": "Alice Martin"
    },
    {
        "id": "doc_004",
        "title": "FastAPI — Créer votre première API",
        "content": "FastAPI est un framework web moderne pour Python. Installez-le avec pip install fastapi uvicorn. Créez une route avec @app.get('/hello') def hello(): return {'message': 'Bonjour'}. Lancez avec uvicorn main:app --reload.",
        "categorie": "web",
        "niveau": "debutant",
        "auteur": "Bob Dupont"
    },
    {
        "id": "doc_005",
        "title": "Validation des données avec Pydantic",
        "content": "Pydantic permet de valider automatiquement les données en Python grâce aux type hints. Définissez un modèle en héritant de BaseModel et FastAPI utilisera automatiquement ce modèle pour valider les requêtes entrantes.",
        "categorie": "web",
        "niveau": "intermediaire",
        "auteur": "Bob Dupont"
    },
    {
        "id": "doc_006",
        "title": "Introduction à Docker",
        "content": "Docker permet de containeriser vos applications. Un conteneur est une unité logicielle légère qui contient le code et toutes ses dépendances. Créez un Dockerfile, construisez avec docker build -t mon-app . et lancez avec docker run -p 8080:8080 mon-app.",
        "categorie": "devops",
        "niveau": "debutant",
        "auteur": "Carol Smith"
    },
    {
        "id": "doc_007",
        "title": "Docker Compose pour les applications multi-services",
        "content": "Docker Compose orchestre plusieurs conteneurs Docker. Définissez vos services dans docker-compose.yml et lancez tout avec docker-compose up. Pratique pour démarrer une app web avec sa base de données en une seule commande.",
        "categorie": "devops",
        "niveau": "intermediaire",
        "auteur": "Carol Smith"
    },
    {
        "id": "doc_008",
        "title": "PostgreSQL — Requêtes avancées",
        "content": "PostgreSQL supporte les CTEs (Common Table Expressions) avec la syntaxe WITH. Les window functions permettent des calculs sur des ensembles de lignes liées. INDEX CONCURRENT crée un index sans bloquer les opérations en lecture.",
        "categorie": "database",
        "niveau": "avance",
        "auteur": "David Lee"
    },
    {
        "id": "doc_009",
        "title": "Introduction à Redis",
        "content": "Redis est une base de données en mémoire utilisée comme cache, broker de messages et store de sessions. Stockez des données avec SET key value et récupérez-les avec GET key. Redis supporte les structures de données avancées : listes, ensembles, hashes.",
        "categorie": "database",
        "niveau": "debutant",
        "auteur": "Emma Wilson"
    },
    {
        "id": "doc_010",
        "title": "Git — Gestion des branches",
        "content": "Créez une branche avec git checkout -b ma-feature. Fusionnez-la avec git merge ma-feature depuis la branche principale. Préférez git rebase pour un historique linéaire. Supprimez une branche fusionnée avec git branch -d ma-feature.",
        "categorie": "git",
        "niveau": "debutant",
        "auteur": "Frank Brown"
    },
    {
        "id": "doc_011",
        "title": "CI/CD avec GitHub Actions",
        "content": "GitHub Actions automatise votre pipeline CI/CD. Créez un fichier .github/workflows/main.yml. Déclenchez des jobs sur push ou pull_request. Chaque job tourne dans un conteneur Ubuntu, macOS ou Windows. Utilisez des actions prédéfinies de la marketplace.",
        "categorie": "devops",
        "niveau": "intermediaire",
        "auteur": "Grace Kim"
    },
    {
        "id": "doc_012",
        "title": "Pandas — Manipulation de DataFrames",
        "content": "Pandas est la bibliothèque de référence pour la manipulation de données tabulaires en Python. Chargez des CSV avec pd.read_csv(), filtrez avec df[df['colonne'] > 10], groupez avec df.groupby('categorie').mean(). Les DataFrames sont l'équivalent des tables SQL en Python.",
        "categorie": "data",
        "niveau": "debutant",
        "auteur": "Henry Zhang"
    },
    {
        "id": "doc_013",
        "title": "Introduction au Machine Learning avec scikit-learn",
        "content": "Scikit-learn fournit des algorithmes de machine learning prêts à l'emploi. Entraînez un modèle avec model.fit(X_train, y_train) et prédisez avec model.predict(X_test). Évaluez avec accuracy_score, precision_score, recall_score.",
        "categorie": "ml",
        "niveau": "intermediaire",
        "auteur": "Iris Johnson"
    },
    {
        "id": "doc_014",
        "title": "Sécurité des API REST",
        "content": "Sécurisez vos API avec JWT (JSON Web Tokens) pour l'authentification. Utilisez HTTPS en production. Implémentez le rate limiting pour éviter les abus. Validez toujours les données entrantes. Utilisez les en-têtes CORS pour contrôler les origines autorisées.",
        "categorie": "securite",
        "niveau": "intermediaire",
        "auteur": "Jack Davis"
    },
    {
        "id": "doc_015",
        "title": "Monitoring avec Prometheus et Grafana",
        "content": "Prometheus collecte des métriques depuis vos applications via des endpoints /metrics. Grafana visualise ces métriques dans des tableaux de bord personnalisables. Configurez des alertes quand une métrique dépasse un seuil critique.",
        "categorie": "devops",
        "niveau": "avance",
        "auteur": "Kate Miller"
    },
]
```

### Étape 1.2 — Vérifier la structure

```python
# test_corpus.py
from corpus import DOCUMENTS

print(f"Nombre de documents : {len(DOCUMENTS)}")
print(f"Catégories : {set(d['categorie'] for d in DOCUMENTS)}")
print(f"Niveaux : {set(d['niveau'] for d in DOCUMENTS)}")
print(f"\nPremier document :")
print(DOCUMENTS[0])
```

**Résultat attendu :**
```
Nombre de documents : 15
Catégories : {'python', 'web', 'devops', 'database', 'git', 'data', 'ml', 'securite'}
Niveaux : {'debutant', 'intermediaire', 'avance'}
```

---

## Partie 2 : Indexation dans Chroma (40 min)

### Étape 2.1 — Créer le script d'indexation

Créez `indexer.py` :

```python
# indexer.py
import chromadb
from sentence_transformers import SentenceTransformer
from corpus import DOCUMENTS

# ─────────────────────────────────────────────────────────────
# TODO 1 : Initialiser le client Chroma persistant
# Stocker les données dans le dossier "./search_engine_db"
# ─────────────────────────────────────────────────────────────
client = ???

# ─────────────────────────────────────────────────────────────
# TODO 2 : Supprimer et recréer la collection "knowledge_base"
# Utiliser la métrique cosinus
# ─────────────────────────────────────────────────────────────
try:
    client.delete_collection("knowledge_base")
    print("Collection existante supprimée.")
except:
    pass

collection = ???

# ─────────────────────────────────────────────────────────────
# TODO 3 : Charger le modèle d'embedding multilingue
# Utiliser "paraphrase-multilingual-mpnet-base-v2"
# ─────────────────────────────────────────────────────────────
print("Chargement du modèle d'embedding...")
model = ???
print("Modèle chargé.")

# ─────────────────────────────────────────────────────────────
# TODO 4 : Préparer les listes pour l'insertion
# - ids : liste des IDs de documents
# - documents : liste des textes à indexer (concaténer title + content)
# - metadatas : liste des dictionnaires de métadonnées
#              (exclure 'id' et 'content' des métadonnées)
# ─────────────────────────────────────────────────────────────
ids = ???
documents = ???
metadatas = ???

print(f"\nExemple de texte indexé :")
print(f"  {documents[0][:100]}...")

# ─────────────────────────────────────────────────────────────
# TODO 5 : Générer les embeddings
# Utiliser model.encode() avec normalize_embeddings=True
# ─────────────────────────────────────────────────────────────
print("\nGénération des embeddings...")
embeddings = ???
print(f"Shape des embeddings : {embeddings.shape}")

# ─────────────────────────────────────────────────────────────
# TODO 6 : Insérer dans Chroma avec les embeddings précalculés
# ─────────────────────────────────────────────────────────────
collection.add(
    ???
)

print(f"\n✅ Indexation terminée : {collection.count()} documents stockés.")
```

**Lancez le script :**
```bash
python indexer.py
```

**Résultat attendu :**
```
Collection existante supprimée.
Chargement du modèle d'embedding...
Modèle chargé.

Exemple de texte indexé :
  Guide d'installation Python Pour installer Python sur Ubuntu...
Génération des embeddings...
Shape des embeddings : (15, 768)

✅ Indexation terminée : 15 documents stockés.
```

---

## Partie 3 : Moteur de recherche (50 min)

### Étape 3.1 — Créer le moteur de recherche

Créez `search_engine.py` :

```python
# search_engine.py
import chromadb
from sentence_transformers import SentenceTransformer

class SemanticSearchEngine:
    def __init__(self, db_path: str = "./search_engine_db", collection_name: str = "knowledge_base"):
        """Initialise le moteur de recherche."""

        # ─────────────────────────────────────────────────────
        # TODO 1 : Charger le client Chroma et la collection
        # ─────────────────────────────────────────────────────
        self.client = ???
        self.collection = ???

        # ─────────────────────────────────────────────────────
        # TODO 2 : Charger le même modèle d'embedding que lors de l'indexation
        # ─────────────────────────────────────────────────────
        print("Chargement du moteur de recherche...")
        self.model = ???
        print(f"Prêt. {self.collection.count()} documents indexés.")

    def search(self, query: str, n_results: int = 5, filters: dict = None) -> list[dict]:
        """
        Recherche sémantique.

        Args:
            query: La requête en langage naturel
            n_results: Nombre de résultats à retourner
            filters: Dictionnaire de filtres sur les métadonnées (optionnel)

        Returns:
            Liste de dictionnaires avec les résultats triés par pertinence
        """

        # ─────────────────────────────────────────────────────
        # TODO 3 : Encoder la requête avec le modèle
        # ─────────────────────────────────────────────────────
        query_embedding = ???

        # ─────────────────────────────────────────────────────
        # TODO 4 : Lancer la recherche dans Chroma
        # Inclure les documents, métadonnées et distances dans les résultats
        # Appliquer le filtre si fourni (paramètre "where")
        # ─────────────────────────────────────────────────────
        results = self.collection.query(
            ???
        )

        # ─────────────────────────────────────────────────────
        # TODO 5 : Formater les résultats
        # Retourner une liste de dicts avec :
        #   - rank : position (1, 2, 3...)
        #   - score : 1 - distance (similarité entre 0 et 1)
        #   - id, title, content, categorie, niveau, auteur
        # ─────────────────────────────────────────────────────
        formatted = []
        for i in range(len(results['documents'][0])):
            result = {
                "rank": i + 1,
                "score": ???,
                "id": ???,
                "title": ???,
                "content": ???,
                "categorie": ???,
                "niveau": ???,
                "auteur": ???,
            }
            formatted.append(result)

        return formatted

    def search_by_category(self, query: str, categorie: str, n_results: int = 5) -> list[dict]:
        """Recherche limitée à une catégorie."""
        # ─────────────────────────────────────────────────────
        # TODO 6 : Appeler self.search() avec un filtre sur la catégorie
        # ─────────────────────────────────────────────────────
        return ???
```

### Étape 3.2 — Créer l'interface CLI

Créez `main.py` :

```python
# main.py
from search_engine import SemanticSearchEngine

def display_results(results: list[dict], query: str):
    """Affiche les résultats de recherche de façon lisible."""
    print(f"\n{'='*70}")
    print(f"Résultats pour : \"{query}\"")
    print(f"{'='*70}")

    if not results:
        print("Aucun résultat trouvé.")
        return

    for r in results:
        score_bar = "█" * int(r['score'] * 20) + "░" * (20 - int(r['score'] * 20))
        print(f"\n[{r['rank']}] Score : {r['score']:.3f} |{score_bar}|")
        print(f"    Titre     : {r['title']}")
        print(f"    Catégorie : {r['categorie']} | Niveau : {r['niveau']}")
        print(f"    Auteur    : {r['auteur']}")
        print(f"    Contenu   : {r['content'][:120]}...")

    print()

def main():
    engine = SemanticSearchEngine()

    # ─────────────────────────────────────────────────────────────
    # TEST 1 : Requêtes sémantiques (mots-clés différents des documents)
    # ─────────────────────────────────────────────────────────────
    test_queries = [
        "Comment mettre en place un conteneur pour mon application ?",   # → Docker
        "Isoler les packages de mon projet Python",                      # → virtualenv
        "Faire des calculs agrégés sur des données tabulaires",          # → Pandas
        "Protéger mon API contre les attaques",                          # → Sécurité
        "Automatiser les tests à chaque push de code",                   # → CI/CD
    ]

    for query in test_queries:
        results = engine.search(query, n_results=3)
        display_results(results, query)

    # ─────────────────────────────────────────────────────────────
    # TEST 2 : Recherche avec filtre de catégorie
    # ─────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("TEST 2 : Recherche dans la catégorie 'devops' uniquement")
    print("="*70)
    results = engine.search_by_category("gestion des services", "devops", n_results=3)
    display_results(results, "gestion des services [devops only]")

    # ─────────────────────────────────────────────────────────────
    # TEST 3 : Mode interactif
    # ─────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("MODE INTERACTIF — tapez 'quit' pour quitter")
    print("Commandes : 'cat:<catégorie> <requête>' pour filtrer par catégorie")
    print("="*70 + "\n")

    while True:
        query = input("Recherche > ").strip()
        if query.lower() in ['quit', 'exit', 'q', '']:
            break

        if query.startswith("cat:"):
            parts = query[4:].split(" ", 1)
            if len(parts) == 2:
                cat, q = parts
                results = engine.search_by_category(q, cat, n_results=5)
                display_results(results, f"{q} [catégorie: {cat}]")
            else:
                print("Format : cat:<catégorie> <requête>")
        else:
            results = engine.search(query, n_results=5)
            display_results(results, query)

if __name__ == "__main__":
    main()
```

---

## Partie 4 : Analyse des résultats (30 min)

### Étape 4.1 — Évaluation manuelle

Répondez aux questions suivantes en observant les résultats de vos tests :

1. Pour la requête "Comment mettre en place un conteneur pour mon application ?", quel document est en première position ? Le score est-il cohérent ?

2. Pour la requête "Isoler les packages de mon projet Python", le moteur trouve-t-il le document sur les environnements virtuels même sans les mots "environnement" ou "venv" ?

3. Testez la requête "erreur dans mon code Python". Quels documents remontent ? Est-ce pertinent ?

4. Testez la requête "base de données rapide pour le cache". Quel document devrait remonter en premier ? Redis ? Pourquoi ?

### Étape 4.2 — Calcul de métriques simples

```python
# evaluation.py
from search_engine import SemanticSearchEngine

engine = SemanticSearchEngine()

# Paires requête → document attendu en top-3
evaluation_set = [
    ("comment containeriser une application", "doc_006"),
    ("créer des routes dans une API web", "doc_004"),
    ("base de données en mémoire vive", "doc_009"),
    ("fusionner des branches dans un projet", "doc_010"),
    ("protéger les endpoints de l'API", "doc_014"),
    ("automatisation du déploiement continu", "doc_011"),
    ("analyse de données avec Python", "doc_012"),
]

hits_at_1 = 0
hits_at_3 = 0

for query, expected_id in evaluation_set:
    results = engine.search(query, n_results=3)
    ids_returned = [r['id'] for r in results]

    if ids_returned[0] == expected_id:
        hits_at_1 += 1
    if expected_id in ids_returned:
        hits_at_3 += 1

    status = "✅" if ids_returned[0] == expected_id else ("⚠️" if expected_id in ids_returned else "❌")
    print(f"{status} \"{query[:40]}\" → attendu: {expected_id}, obtenu: {ids_returned[0]}")

n = len(evaluation_set)
print(f"\nPrécision@1 : {hits_at_1}/{n} = {hits_at_1/n:.1%}")
print(f"Rappel@3    : {hits_at_3}/{n} = {hits_at_3/n:.1%}")
```

---

## Partie 5 : Bonus — Interface web avec Streamlit (optionnel)

```python
# app_streamlit.py
# pip install streamlit

import streamlit as st
from search_engine import SemanticSearchEngine

@st.cache_resource
def load_engine():
    return SemanticSearchEngine()

st.title("🔍 Moteur de recherche sémantique")
st.markdown("Recherchez dans la base de connaissance par intention, pas par mots-clés.")

engine = load_engine()

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    query = st.text_input("Votre question :", placeholder="ex: comment déployer mon application en production ?")
with col2:
    n_results = st.selectbox("Résultats :", [3, 5, 10], index=1)
with col3:
    categorie = st.selectbox("Catégorie :", ["Toutes", "python", "web", "devops", "database", "git", "data", "ml", "securite"])

if query:
    if categorie == "Toutes":
        results = engine.search(query, n_results=n_results)
    else:
        results = engine.search_by_category(query, categorie, n_results=n_results)

    if results:
        for r in results:
            with st.expander(f"[{r['rank']}] {r['title']} — Score : {r['score']:.3f}"):
                st.progress(r['score'])
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Catégorie", r['categorie'])
                col_b.metric("Niveau", r['niveau'])
                col_c.metric("Auteur", r['auteur'])
                st.markdown(r['content'])
    else:
        st.warning("Aucun résultat trouvé.")
```

```bash
streamlit run app_streamlit.py
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Script `indexer.py` fonctionnel, 15 documents indexés | 3 pts |
| Classe `SemanticSearchEngine` correctement implémentée | 4 pts |
| Recherche sémantique fonctionnelle (mots ≠ documents) | 4 pts |
| Filtrage par catégorie fonctionnel | 2 pts |
| Précision@1 ≥ 70% sur le jeu d'évaluation | 4 pts |
| Mode interactif CLI | 2 pts |
| Bonus : interface Streamlit | +3 pts |

**Total : 19 pts (+ 3 bonus)**

---

## Solution partielle — indexer.py

<details>
<summary>Cliquez pour voir la solution (essayez d'abord !)</summary>

```python
# Réponses aux TODOs

# TODO 1
client = chromadb.PersistentClient(path="./search_engine_db")

# TODO 2
collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

# TODO 3
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# TODO 4
ids = [doc["id"] for doc in DOCUMENTS]
documents = [f"{doc['title']} {doc['content']}" for doc in DOCUMENTS]
metadatas = [
    {k: v for k, v in doc.items() if k not in ('id', 'content')}
    for doc in DOCUMENTS
]

# TODO 5
embeddings = model.encode(documents, normalize_embeddings=True)

# TODO 6
collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)
```
</details>
