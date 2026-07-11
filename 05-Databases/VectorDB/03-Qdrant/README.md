# Qdrant

[Qdrant](https://qdrant.tech/) est une base de données vectorielle **haute performance** écrite en Rust, conçue pour les déploiements en production.

## Contenu de ce dossier

| Fichier | Description |
|---------|-------------|
| `01-installation.md` | Architecture, installation Docker, client Python, création de collections |
| `02-operations.md` | Indexation (upsert), recherche par similarité, scroll, suppression, pipeline complet |
| `03-filtres-avances.md` | Filtres AND/OR/NOT sur les payloads, index payload, optimisation mémoire |

## Démarrage rapide

```bash
# Lancer Qdrant avec Docker
docker run -d --name qdrant -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Installer le client Python
pip install qdrant-client sentence-transformers
```

## Interface web

Après démarrage : [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

## Quand utiliser Qdrant ?

- Production avec des exigences de performance
- Filtres complexes sur des payloads riches
- Volume de quelques milliers à plusieurs dizaines de millions de vecteurs
- Self-hosted sur vos propres serveurs

## Ressources

- [Documentation officielle Qdrant](https://qdrant.tech/documentation/)
- [LangChain + Qdrant](https://python.langchain.com/docs/integrations/vectorstores/qdrant/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
