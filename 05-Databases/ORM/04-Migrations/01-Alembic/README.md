# Alembic — Migrations pour SQLAlchemy/Python

Alembic est l'outil de migrations de référence pour SQLAlchemy. Il permet de versionner le schéma de votre base de données de manière fiable.

## Caractéristiques

- **Autogenerate** : détecte automatiquement les différences entre vos modèles SQLAlchemy et le schéma BDD
- **Branches** : supporte les migrations parallèles (pour les équipes)
- **Online et Offline mode** : génère du SQL pur ou l'applique directement
- **Compatible** : SQLAlchemy, SQLModel, tout projet Python utilisant SQLAlchemy

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Installation, configuration, premières migrations |
| [02-commandes.md](./02-commandes.md) | Commandes avancées, opérations complexes, CI/CD |

## Installation

```bash
pip install alembic sqlalchemy psycopg2-binary
```
