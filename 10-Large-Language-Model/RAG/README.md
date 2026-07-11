# Formation RAG — Retrieval-Augmented Generation

## Vue d'ensemble

Le RAG (Retrieval-Augmented Generation) est l'architecture dominante pour construire des applications LLM capables de répondre à des questions sur des données privées ou récentes. Au lieu de ré-entraîner un modèle, on lui fournit dynamiquement le contexte pertinent au moment de la requête.

Ce module couvre l'ensemble du pipeline RAG, des concepts fondamentaux jusqu'aux patterns avancés, avec des exercices pratiques utilisant LangChain, Chroma et OpenAI (ou des alternatives 100% locales).

---

## Objectifs pédagogiques

À l'issue de ce module, vous serez capable de :

- Expliquer l'architecture RAG et ses avantages face au fine-tuning
- Implémenter un pipeline RAG complet avec LangChain LCEL
- Choisir et appliquer la bonne stratégie de chunking selon le type de document
- Mettre en place une recherche hybride avec reranking
- Évaluer la qualité d'un système RAG avec RAGAS
- Construire un RAG conversationnel multi-tours
- Déployer un RAG 100% local sans clé API

---

## Prérequis

### Connaissances requises

- Python intermédiaire
- Bases de LangChain (module LangChain de cette formation)
- Notions sur les LLM et les embeddings
- Git et environnements virtuels Python

### Outils à installer

```bash
# Environnement de base
pip install langchain langchain-openai langchain-community langchain-chroma
pip install python-dotenv pypdf tiktoken

# Pour l'évaluation
pip install ragas datasets

# Pour le RAG local
pip install langchain-ollama sentence-transformers chromadb
```

### Comptes et clés API

| Service | Utilisation | Obligatoire |
|---------|-------------|-------------|
| OpenAI | Embeddings + génération | Recommandé |
| Ollama | Modèles 100% locaux | Optionnel (exercice 2) |
| LangSmith | Tracing du pipeline | Recommandé (tier gratuit) |

---

## Table des matières

### Concepts

| Fichier | Titre | Durée estimée |
|---------|-------|---------------|
| [Concepts/01-introduction-rag.md](./Concepts/01-introduction-rag.md) | Qu'est-ce que le RAG, pourquoi, architecture | 45 min |
| [Concepts/02-chunking-strategies.md](./Concepts/02-chunking-strategies.md) | Stratégies de découpage de documents | 45 min |

### Pipeline

| Fichier | Titre | Durée estimée |
|---------|-------|---------------|
| [Pipeline/01-ingestion.md](./Pipeline/01-ingestion.md) | Chargement, découpage, embedding, stockage | 60 min |
| [Pipeline/02-retrieval.md](./Pipeline/02-retrieval.md) | Recherche vectorielle, hybride, reranking | 60 min |
| [Pipeline/03-generation.md](./Pipeline/03-generation.md) | Construction du prompt, synthèse, citations | 45 min |

### Évaluation

| Fichier | Titre | Durée estimée |
|---------|-------|---------------|
| [Evaluation/01-metriques.md](./Evaluation/01-metriques.md) | Métriques : fidélité, pertinence, qualité | 30 min |
| [Evaluation/02-ragas.md](./Evaluation/02-ragas.md) | Framework RAGAS pour l'évaluation automatisée | 45 min |

### Patterns avancés

| Fichier | Titre | Durée estimée |
|---------|-------|---------------|
| [Avance/01-rag-conversationnel.md](./Avance/01-rag-conversationnel.md) | RAG multi-tours avec historique | 45 min |
| [Avance/02-self-rag.md](./Avance/02-self-rag.md) | Self-RAG et Corrective-RAG | 60 min |

### Exercices pratiques

| Fichier | Description | Niveau |
|---------|-------------|--------|
| [exercices/exercice-01-rag-documents.md](./exercices/exercice-01-rag-documents.md) | RAG sur collection de PDFs (LangChain + Chroma + OpenAI) | Intermédiaire |
| [exercices/exercice-02-rag-local.md](./exercices/exercice-02-rag-local.md) | RAG 100% local (Ollama + Chroma + sentence-transformers) | Intermédiaire |

### Référence rapide

| Fichier | Description |
|---------|-------------|
| [CHEATSHEET-rag.md](./CHEATSHEET-rag.md) | Aide-mémoire complet RAG |

---

## Structure du module

```
RAG/
├── README.md
├── CHEATSHEET-rag.md
├── Concepts/
│   ├── 01-introduction-rag.md
│   └── 02-chunking-strategies.md
├── Pipeline/
│   ├── 01-ingestion.md
│   ├── 02-retrieval.md
│   └── 03-generation.md
├── Evaluation/
│   ├── 01-metriques.md
│   └── 02-ragas.md
├── Avance/
│   ├── 01-rag-conversationnel.md
│   └── 02-self-rag.md
└── exercices/
    ├── exercice-01-rag-documents.md
    └── exercice-02-rag-local.md
```

---

## Progression recommandée

```
Débutant / Découverte
   └── Concepts/01-introduction-rag.md
       └── Pipeline/01-ingestion.md
           └── exercice-01-rag-documents.md (parties 1-3)

Intermédiaire
   └── Concepts/02-chunking-strategies.md
       └── Pipeline/02-retrieval.md
           └── Pipeline/03-generation.md
               └── exercice-01-rag-documents.md (complet)

Avancé / Production
   └── Evaluation/01-metriques.md
       └── Evaluation/02-ragas.md
           └── Avance/01-rag-conversationnel.md
               └── Avance/02-self-rag.md
                   └── exercice-02-rag-local.md
```

---

## Architecture RAG — vue d'ensemble

```
                    ┌─────────────────────────────────┐
                    │         PHASE OFFLINE             │
                    │  (indexation, faite une fois)     │
                    │                                   │
  Documents ───────►│  Loader → Splitter → Embeddings  │
  (PDF, HTML, TXT)  │             │                     │
                    │             ▼                     │
                    │      Vector Store (Chroma)        │
                    └─────────────────────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │         PHASE ONLINE              │
                    │    (à chaque requête utilisateur) │
                    │                                   │
  Question ────────►│  Embed question → Similarity     │
                    │  Search → Top-k chunks            │
                    │         │                         │
                    │         ▼                         │
                    │  Prompt = question + chunks       │
                    │         │                         │
                    │         ▼                         │
                    │       LLM → Réponse               │
                    └─────────────────────────────────┘
```

---

## Environnement de travail

```bash
# Naviguer vers le répertoire
cd formation-data-engineer/10-Large-Language-Model/RAG/

# Fichier .env type
OPENAI_API_KEY=sk-proj-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=formation-rag
```

---

## Ressources complémentaires

- [Documentation LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [RAGAS documentation](https://docs.ragas.io/)
- [Chroma documentation](https://docs.trychroma.com/)
- [Ollama — modèles locaux](https://ollama.ai/)
- [Article original RAG (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
