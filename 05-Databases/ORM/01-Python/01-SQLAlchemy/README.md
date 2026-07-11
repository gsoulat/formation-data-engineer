# SQLAlchemy — L'ORM Python de référence

SQLAlchemy est l'ORM le plus utilisé en Python. Il existe depuis 2006 et est considéré comme le standard de l'industrie pour la persistance de données en Python.

## Pourquoi SQLAlchemy ?

- **Mature et stable** : 15+ ans de développement, utilisé par des milliers de projets en production
- **Deux niveaux d'abstraction** : Core (SQL expressif) et ORM (objets Python)
- **Très flexible** : supporte tous les patterns, toutes les bases de données
- **Version 2.0** (2023) : nouvelle API plus claire avec `Mapped` et type hints

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Architecture, installation, première connexion |
| [02-modeles.md](./02-modeles.md) | Définir des modèles avec `DeclarativeBase` et `Mapped` |
| [03-requetes.md](./03-requetes.md) | CRUD, filtres, tri, pagination, SQL brut |
| [04-relations.md](./04-relations.md) | OneToMany, ManyToMany, OneToOne, lazy/eager loading |

## Installation rapide

```bash
pip install sqlalchemy psycopg2-binary  # PostgreSQL
# ou
pip install sqlalchemy aiosqlite         # SQLite async
```

## Exemple minimal

```python
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

engine = create_engine("postgresql://formation:formation@localhost/orm_db")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
    print(f"Utilisateur créé : {user.id}")
```
