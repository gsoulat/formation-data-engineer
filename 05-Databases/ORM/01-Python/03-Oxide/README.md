# Oxide — ORM Python async moderne et léger

Oxide est un ORM Python orienté async, conçu pour être simple d'utilisation tout en restant performant. Il adopte une approche minimaliste comparé à SQLAlchemy.

> **Note importante** : Oxide est un ORM Python (pas Rust). Ne pas confondre avec le projet "Oxide Computer" ou les crates Rust.

## Caractéristiques

- Async natif (compatible `asyncio`, FastAPI, Starlette)
- Syntaxe simple et expressive
- Moins de boilerplate que SQLAlchemy
- Idéal pour les projets de taille petite à moyenne
- Supporte PostgreSQL, MySQL, SQLite

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Installation, modèles, CRUD async |

## Installation

```bash
pip install oxide-orm
# ou selon le packaging disponible
pip install oxide
```
