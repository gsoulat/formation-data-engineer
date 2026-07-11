# Ormar — Mini ORM async SQLAlchemy + Pydantic

Ormar est un ORM Python async qui combine **SQLAlchemy Core** (pour les requêtes SQL), **databases** (pour les connexions async) et **Pydantic** (pour la validation).

## Caractéristiques

- **Un seul modèle** : joue le rôle d'ORM ET de schéma Pydantic simultanément
- **Async natif** : basé sur la bibliothèque `databases`
- **FastAPI natif** : intégration très naturelle
- **Léger** : moins de concepts que SQLAlchemy complet

## Relation avec SQLModel

Ormar et SQLModel adressent le même besoin (unifier ORM + Pydantic) mais avec des approches différentes :

| Aspect | Ormar | SQLModel |
|--------|-------|----------|
| Base ORM | SQLAlchemy Core | SQLAlchemy ORM |
| Async | Natif | Via AsyncSession |
| Auteur | Komunauté | Sebastián Ramírez (FastAPI) |
| Statut | Moins actif | Activement maintenu |

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Installation, modèles, CRUD async, FastAPI |

## Installation

```bash
pip install ormar databases asyncpg  # PostgreSQL
# ou
pip install ormar databases aiosqlite # SQLite
```
