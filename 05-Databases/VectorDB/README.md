# Bases de Données Vectorielles (Vector Databases)

## Vue d'ensemble

Ce module introduit les bases de données vectorielles, une technologie fondamentale dans l'écosystème de l'intelligence artificielle moderne. Avec l'essor des modèles de langage (LLM) et des systèmes RAG (Retrieval-Augmented Generation), les vector databases sont devenues un composant incontournable pour tout data engineer ou ML engineer.

Une base de données vectorielle stocke des **embeddings** — des représentations numériques de données (texte, images, audio) sous forme de vecteurs haute dimension — et permet des **recherches par similarité sémantique** plutôt que par correspondance exacte.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer une démo live : taper une requête dans une interface de recherche sémantique et montrer des résultats pertinents qui ne contiennent pas les mots exacts de la requête.
> **Expliquer :** "Voyez ici — j'ai cherché 'voiture rapide' et le système a trouvé un document qui parle de 'automobile sportive de haute performance'. C'est la magie des vector databases : elles comprennent le sens, pas juste les mots."

---

## Objectifs pédagogiques

À l'issue de ce module, vous serez capable de :

- Expliquer ce qu'est un embedding vectoriel et pourquoi les vector databases existent
- Comprendre les métriques de distance (cosinus, euclidienne, produit scalaire)
- Générer des embeddings avec OpenAI ou sentence-transformers
- Utiliser **Chroma DB** en mode local et persistant
- Déployer et utiliser **Qdrant** via Docker
- Utiliser **FAISS** pour la recherche vectorielle locale haute performance
- Implémenter un pipeline RAG complet (Retrieval-Augmented Generation)
- Choisir la bonne vector database selon le contexte (local, cloud, scalabilité)

## Prérequis

- Python 3.10+ installé
- Notions de bases en Python (listes, dictionnaires, fonctions)
- Compréhension basique des API REST
- Docker installé (pour Qdrant)
- Clé API OpenAI (optionnel — des alternatives locales sont disponibles)

### Installation rapide des dépendances

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dépendances principales
pip install chromadb qdrant-client faiss-cpu sentence-transformers langchain openai python-dotenv
```

## Structure du module

```
VectorDB/
├── README.md                          ← Ce fichier
├── CHEATSHEET-vectordb.md             ← Référence rapide
├── Concepts/
│   ├── 01-introduction.md             ← Concepts fondamentaux des vector databases
│   ├── 02-embeddings.md               ← Génération d'embeddings (OpenAI, sentence-transformers, chunking)
│   └── 03-comparatif.md               ← Comparatif Chroma / Qdrant / FAISS / Pinecone / Weaviate / pgvector
├── Chroma/
│   ├── README.md
│   ├── 01-installation.md             ← Installation, modes de fonctionnement, collections
│   ├── 02-operations.md               ← CRUD, recherche, filtrage par métadonnées
│   └── 03-integration-langchain.md    ← Intégration LangChain, ingestion PDF, chaîne RAG
├── Qdrant/
│   ├── README.md
│   ├── 01-installation.md             ← Architecture, Docker, client Python, collections
│   ├── 02-operations.md               ← Upsert, recherche, scroll, pipeline complet
│   └── 03-filtres-avances.md          ← Filtres AND/OR/NOT, index payload, optimisation mémoire
├── FAISS/
│   ├── README.md
│   └── 01-utilisation.md              ← Types d'index, recherche, métadonnées, intégration LangChain
├── Integration-RAG/
│   ├── README.md
│   └── 01-pipeline-rag.md             ← Pipeline RAG complet, stratégies de retrieval, évaluation RAGAS
└── exercices/
    ├── exercice-01-recherche-semantique.md
    └── exercice-02-rag-local.md
```

## Parcours recommandé

### Débutant (première approche)
1. `Concepts/01-introduction.md` — Comprendre le problème et les concepts clés
2. `Concepts/02-embeddings.md` — Générer ses premiers embeddings
3. `Chroma/01-installation.md` + `Chroma/02-operations.md` — Pratiquer avec Chroma
4. `exercices/exercice-01-recherche-semantique.md`

### Intermédiaire (pour aller en production)
1. `Qdrant/01-installation.md` + `Qdrant/02-operations.md` — Maîtriser Qdrant
2. `Qdrant/03-filtres-avances.md` — Filtres complexes et optimisation
3. `Integration-RAG/01-pipeline-rag.md` — Construire un pipeline RAG complet
4. `exercices/exercice-02-rag-local.md`

### Avancé (comparatif et choix technologique)
1. `Concepts/03-comparatif.md` — Choisir la bonne solution
2. `FAISS/01-utilisation.md` — FAISS pour les très grands corpus
3. `Chroma/03-integration-langchain.md` — Intégrations avancées

## Ressources complémentaires

- [Documentation officielle Chroma](https://docs.trychroma.com/)
- [Documentation officielle Qdrant](https://qdrant.tech/documentation/)
- [Documentation FAISS](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Vector Stores](https://python.langchain.com/docs/integrations/vectorstores/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

## Durée estimée

| Section | Durée |
|---------|-------|
| Concepts (introduction + embeddings) | 2h30 |
| Chroma | 2h |
| Qdrant | 2h |
| FAISS | 1h |
| Comparatif | 45min |
| RAG Pipeline | 2h |
| Exercices | 3h |
| **Total** | **~13h15** |
