# Tortoise-ORM — ORM async inspiré de Django

Tortoise-ORM est un ORM Python **async natif** qui s'inspire fortement de l'API de Django ORM. Si vous connaissez Django, vous vous sentirez immédiatement à l'aise.

## Caractéristiques

- **Async natif** : conçu pour `asyncio` dès le départ
- **API Django-like** : `Model.filter()`, `Model.create()`, `Model.get()`
- **Pydantic optionnel** : intégration via `tortoise-contrib[pydantic]`
- **Migrations** : via Aerich (outil dédié)
- **BDD supportées** : PostgreSQL, MySQL, SQLite

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Installation, modèles, CRUD, relations, FastAPI |

## Installation

```bash
pip install tortoise-orm
pip install tortoise-orm[asyncpg]    # PostgreSQL
pip install tortoise-orm[aiomysql]   # MySQL
pip install aerich                    # Pour les migrations
```

## Positionnement dans l'écosystème

Tortoise-ORM est plus mûr qu'Oxide et plus populaire dans la communauté async Python. Il est souvent choisi pour des projets qui veulent l'ergonomie de Django ORM sans le framework Django entier.
