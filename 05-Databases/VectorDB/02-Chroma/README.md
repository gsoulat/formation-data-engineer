# Chroma DB

[Chroma](https://www.trychroma.com/) est une base de données vectorielle **open source** conçue pour être simple à utiliser et parfaite pour le développement local et les prototypes.

## Contenu de ce dossier

| Fichier | Description |
|---------|-------------|
| `01-installation.md` | Installation, modes de fonctionnement (in-memory, persistant, serveur), gestion des collections |
| `02-operations.md` | CRUD complet : ajout, recherche, filtrage par métadonnées, mise à jour, suppression |
| `03-integration-langchain.md` | Intégration avec LangChain, ingestion de PDFs, chaîne RAG |

## Installation rapide

```bash
pip install chromadb
pip install langchain langchain-chroma sentence-transformers  # pour l'intégration LangChain
```

## Quand utiliser Chroma ?

- Développement local et prototypage rapide
- Intégration LangChain/LlamaIndex en priorité
- Volume < 1 million de vecteurs
- Équipe Python, besoin de simplicité maximale

## Ressources

- [Documentation officielle Chroma](https://docs.trychroma.com/)
- [LangChain + Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
