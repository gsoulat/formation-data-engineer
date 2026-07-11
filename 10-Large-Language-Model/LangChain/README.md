# Formation LangChain — Framework pour Applications LLM

## Vue d'ensemble

LangChain est un framework open-source conçu pour simplifier la création d'applications basées sur les grands modèles de langage (LLM). Il fournit une abstraction cohérente pour travailler avec différents fournisseurs de modèles, gérer la mémoire conversationnelle, orchestrer des chaînes de traitement, et construire des agents capables d'utiliser des outils.

Ce module de formation couvre les concepts fondamentaux et les patterns avancés de LangChain, avec une approche pratique orientée vers des cas d'usage réels en data engineering et en développement d'applications IA.

---

## Objectifs pédagogiques

À l'issue de ce module, vous serez capable de :

- Comprendre l'architecture de LangChain et son rôle dans l'écosystème LLM
- Construire des chaînes de traitement avec LCEL (LangChain Expression Language)
- Gérer la mémoire conversationnelle dans vos applications
- Switcher entre plusieurs fournisseurs LLM (OpenAI, Ollama, Anthropic) sans changer votre code
- Créer des agents capables d'utiliser des outils personnalisés
- Déboguer et tracer vos applications avec LangSmith
- Mettre en place des patterns de production robustes

---

## Prérequis

### Connaissances requises

- Python intermédiaire (classes, décorateurs, gestion des exceptions)
- Notions de base sur les LLM et les API REST
- Compréhension des variables d'environnement et fichiers `.env`
- Git et environnements virtuels Python

### Outils à installer

```bash
# Python 3.10+ requis
python --version

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Installation de base
pip install langchain langchain-openai langchain-community python-dotenv
```

### Comptes et clés API recommandés

| Service | Utilisation | Obligatoire |
|---------|-------------|-------------|
| OpenAI | Modèles GPT-4o, GPT-3.5 | Recommandé |
| Anthropic | Claude 3 Haiku/Sonnet | Optionnel |
| Ollama | Modèles locaux (Llama, Mistral) | Recommandé (gratuit) |
| LangSmith | Tracing et debugging | Recommandé (tier gratuit) |

---

## Table des matières

### Cours principaux

| Fichier | Titre | Durée estimée |
|---------|-------|---------------|
| [01-introduction.md](./01-introduction.md) | Introduction à LangChain | 45 min |
| [02-lcel-chains.md](./02-lcel-chains.md) | LCEL et composition de chaînes | 60 min |
| [03-memoire-conversation.md](./03-memoire-conversation.md) | Mémoire et contexte conversationnel | 45 min |
| [04-multi-providers.md](./04-multi-providers.md) | Multi-fournisseurs LLM | 30 min |
| [05-agents-tools.md](./05-agents-tools.md) | Agents et outils | 60 min |

### Exercices pratiques

| Fichier | Description | Niveau |
|---------|-------------|--------|
| [exercices/exercice-01-chatbot-simple.md](./exercices/exercice-01-chatbot-simple.md) | Chatbot avec historique | Débutant |
| [exercices/exercice-02-chain-documents.md](./exercices/exercice-02-chain-documents.md) | Analyse de documents | Intermédiaire |

### Référence rapide

| Fichier | Description |
|---------|-------------|
| [CHEATSHEET-langchain.md](./CHEATSHEET-langchain.md) | Aide-mémoire complet |

---

## Structure du module

```
LangChain/
├── README.md                          # Ce fichier
├── 01-introduction.md                 # Introduction et écosystème
├── 02-lcel-chains.md                  # LCEL et chaînes
├── 03-memoire-conversation.md         # Mémoire conversationnelle
├── 04-multi-providers.md              # Multi-fournisseurs
├── 05-agents-tools.md                 # Agents et outils
├── CHEATSHEET-langchain.md            # Référence rapide
└── exercices/
    ├── exercice-01-chatbot-simple.md  # Exercice 1
    └── exercice-02-chain-documents.md # Exercice 2
```

---

## Progression recommandée

```
Débutant
   └── 01-introduction.md
       └── 02-lcel-chains.md (parties 1-3)
           └── exercice-01-chatbot-simple.md

Intermédiaire
   └── 02-lcel-chains.md (parties 4-6)
       └── 03-memoire-conversation.md
           └── 04-multi-providers.md
               └── exercice-02-chain-documents.md

Avancé
   └── 05-agents-tools.md
       └── Projets personnels
```

---

## Environnement de travail recommandé

```bash
# Cloner ou naviguer vers le répertoire du cours
cd formation-data-engineer/10-Large-Language-Model/LangChain/

# Fichier .env type (à créer à la racine de votre projet)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=formation-langchain
```

---

## Ressources complémentaires

- [Documentation officielle LangChain](https://python.langchain.com/docs/)
- [LangSmith](https://smith.langchain.com/) — plateforme de tracing
- [LangChain Hub](https://smith.langchain.com/hub) — bibliothèque de prompts
- [GitHub LangChain](https://github.com/langchain-ai/langchain)
- [Ollama](https://ollama.ai/) — modèles locaux gratuits
