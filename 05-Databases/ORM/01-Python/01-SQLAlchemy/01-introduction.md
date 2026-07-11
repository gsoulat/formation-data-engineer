# SQLAlchemy — Introduction et architecture

## Qu'est-ce que SQLAlchemy ?

SQLAlchemy est une bibliothèque Python en deux parties :

1. **SQLAlchemy Core** : une couche d'abstraction SQL qui génère du SQL de manière programmatique (sans ORM). Vous écrivez des requêtes en Python mais restez proche du SQL.
2. **SQLAlchemy ORM** : la couche ORM complète au-dessus de Core, qui mappe des classes Python vers des tables SQL.

```
Votre code Python
      ↓
 SQLAlchemy ORM  (modèles, sessions, relations)
      ↓
 SQLAlchemy Core (expressions SQL, connexions)
      ↓
    DBAPI  (psycopg2, pymysql, sqlite3…)
      ↓
  Base de données (PostgreSQL, MySQL, SQLite…)
```

## Version 1.x vs 2.x

La version 2.0 (sortie en 2023) apporte une API modernisée :

| Aspect | Version 1.x (ancienne) | Version 2.0 (actuelle) |
|--------|------------------------|------------------------|
| Déclaration modèle | `Column(Integer)` | `Mapped[int] = mapped_column()` |
| Requête | `session.query(User)` | `session.execute(select(User))` |
| Type hints | Non | Oui, intégrés |
| Async | Extension externe | `AsyncSession` natif |

> Ce cours utilise **SQLAlchemy 2.0** exclusivement.

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer SQLAlchemy + driver PostgreSQL
pip install sqlalchemy psycopg2-binary

# Pour le mode async (PostgreSQL)
pip install sqlalchemy asyncpg

# Pour SQLite (inclus dans Python, pas de driver externe)
pip install sqlalchemy
```

Vérifier l'installation :
```bash
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
# 2.0.x
```

## Créer un engine (connexion à la BDD)

L'`engine` est le point d'entrée vers la base de données. Il gère le pool de connexions.

```python
from sqlalchemy import create_engine

# PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://user:password@localhost:5432/dbname",
    echo=True,          # Affiche toutes les requêtes SQL générées (debug)
    pool_size=5,        # Nombre de connexions dans le pool
    max_overflow=10,    # Connexions supplémentaires si le pool est plein
)

# MySQL
engine = create_engine("mysql+pymysql://user:password@localhost/dbname")

# SQLite (fichier local)
engine = create_engine("sqlite:///./ma_base.db")

# SQLite en mémoire (tests)
engine = create_engine("sqlite:///:memory:")
```

La chaîne de connexion suit le format :
```
dialect+driver://user:password@host:port/dbname
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — lancer Python, créer un engine avec `echo=True`, exécuter `engine.connect()` et montrer la sortie
> **Expliquer :** Montrer les logs de connexion qui apparaissent, expliquer le pool de connexions, montrer que `echo=True` affiche chaque requête SQL générée par SQLAlchemy. Lancer Docker PostgreSQL avant.

---

## Base déclarative

Tous vos modèles doivent hériter d'une classe `Base` qui enregistre les métadonnées.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Cette `Base` contient `Base.metadata` — un registre de toutes les tables définies dans votre application.

## Premier modèle complet

```python
# models.py
from sqlalchemy import create_engine, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

engine = create_engine("postgresql+psycopg2://formation:formation@localhost/orm_db", echo=True)

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"

    # Colonnes
    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    contenu: Mapped[str] = mapped_column(Text)
    publie: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Représentation lisible
    def __repr__(self) -> str:
        return f"<Article id={self.id} titre={self.titre!r}>"

# Créer les tables dans la BDD (si elles n'existent pas)
Base.metadata.create_all(engine)
```

## Créer et inspecter les tables

```python
# Voir le SQL généré par SQLAlchemy (sans l'exécuter)
from sqlalchemy.schema import CreateTable
print(CreateTable(Article.__table__).compile(engine))

# Créer toutes les tables
Base.metadata.create_all(engine)

# Supprimer toutes les tables (attention !)
Base.metadata.drop_all(engine)

# Créer uniquement si la table n'existe pas
Base.metadata.create_all(engine, checkfirst=True)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `Base.metadata.create_all(engine)` avec `echo=True` activé, puis ouvrir DBeaver/pgAdmin et montrer la table créée avec ses colonnes
> **Expliquer :** Montrer le SQL `CREATE TABLE` affiché dans le terminal, puis dans DBeaver faire un clic droit → "View DDL" pour comparer le SQL généré par SQLAlchemy avec ce qu'a vraiment créé PostgreSQL. Insister sur la correspondance exacte.

---

## Session — le cœur du pattern Data Mapper

La `Session` est le lien entre vos objets Python et la base de données. Elle :
- maintient un registre des objets chargés (identity map)
- accumule les changements (unit of work)
- exécute les requêtes au moment du `commit()`

```python
from sqlalchemy.orm import Session

# Pattern context manager (recommandé)
with Session(engine) as session:
    # Toutes les opérations ici
    article = Article(titre="Mon premier article", contenu="Contenu...")
    session.add(article)
    session.commit()
    # Session fermée automatiquement en fin de bloc

# Avec begin() pour gérer la transaction explicitement
with Session(engine) as session:
    with session.begin():
        article = Article(titre="Test", contenu="...")
        session.add(article)
    # commit() appelé automatiquement en fin de with session.begin()
```

## États d'un objet SQLAlchemy

Un objet peut être dans 4 états :

```python
from sqlalchemy import inspect

article = Article(titre="Test")

# 1. transient — pas encore associé à une session
print(inspect(article).transient)   # True

session.add(article)

# 2. pending — dans la session, pas encore en BDD
print(inspect(article).pending)     # True

session.commit()

# 3. persistent — en BDD et dans la session
print(inspect(article).persistent)  # True

session.close()

# 4. detached — en BDD mais plus dans une session active
print(inspect(article).detached)    # True
```

## Résumé

```
engine        → connexion à la BDD (pool de connexions)
Base          → registre des modèles/tables
session       → unité de travail (accumule, persiste, charge)
model class   → représentation Python d'une table
instance      → représentation Python d'une ligne
```

La prochaine étape est de définir des modèles plus riches avec toutes les options de colonnes disponibles.
