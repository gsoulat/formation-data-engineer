# Module 02 - SQLAlchemy

## Objectifs du module

- Comprendre l'architecture de SQLAlchemy (Core vs ORM)
- Definir des modeles avec le style declaratif (2.0)
- Maitriser les operations CRUD avec les sessions
- Gerer les relations entre tables
- Ecrire des requetes avancees

## Architecture de SQLAlchemy

SQLAlchemy est compose de deux couches distinctes :

```
┌─────────────────────────────────────────┐
│              Votre Code                  │
├─────────────────────────────────────────┤
│           SQLAlchemy ORM                 │  ← Objets Python, relations, sessions
│  (Session, Query, Mapped Classes)        │
├─────────────────────────────────────────┤
│           SQLAlchemy Core                │  ← Construction de requetes SQL
│  (Engine, Connection, Table, Select)     │
├─────────────────────────────────────────┤
│              DBAPI                        │  ← Driver Python (psycopg2, sqlite3)
├─────────────────────────────────────────┤
│          Base de donnees                  │  ← PostgreSQL, MySQL, SQLite...
└─────────────────────────────────────────┘
```

### Core vs ORM

| Couche | Role | Quand l'utiliser |
|--------|------|-----------------|
| **Core** | Construction de SQL en Python | Requetes complexes, bulk operations |
| **ORM** | Mapping objets ↔ tables | CRUD, relations, logique metier |

> On utilise generalement l'ORM pour 90% des cas, et on descend au Core pour les requetes complexes.

## Installation

```bash
pip install sqlalchemy

# Avec PostgreSQL
pip install sqlalchemy psycopg2-binary

# Avec MySQL
pip install sqlalchemy pymysql
```

## Connexion a la base

### Creer un Engine

```python
from sqlalchemy import create_engine

# SQLite (fichier local)
engine = create_engine("sqlite:///ma_base.db", echo=True)

# PostgreSQL
engine = create_engine("postgresql://user:password@localhost:5432/ma_base")

# MySQL
engine = create_engine("mysql+pymysql://user:password@localhost:3306/ma_base")

# Options utiles
engine = create_engine(
    "postgresql://user:password@localhost:5432/ma_base",
    echo=True,           # Affiche le SQL genere (debug)
    pool_size=5,         # Taille du pool de connexions
    max_overflow=10,     # Connexions supplementaires autorisees
    pool_recycle=3600,   # Recycler les connexions apres 1h
)
```

### Format de l'URL

```
dialect+driver://username:password@host:port/database

Exemples :
sqlite:///relative/path/to/file.db
sqlite:////absolute/path/to/file.db
postgresql://scott:tiger@localhost/mydatabase
mysql+pymysql://scott:tiger@localhost/mydatabase
```

## Definir des modeles (Style 2.0)

### Base declarative

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from datetime import datetime

# Base pour tous les modeles
class Base(DeclarativeBase):
    pass
```

### Modele simple

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int | None] = mapped_column(default=None)  # Nullable
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"
```

### Types de colonnes

| Python Type | SQL Type | Notes |
|------------|----------|-------|
| `Mapped[int]` | `INTEGER` | NOT NULL par defaut |
| `Mapped[str]` | `VARCHAR` | Utiliser `String(n)` pour la longueur |
| `Mapped[float]` | `FLOAT` | |
| `Mapped[bool]` | `BOOLEAN` | |
| `Mapped[datetime]` | `DATETIME` | |
| `Mapped[int \| None]` | `INTEGER` | NULL autorise |
| `Mapped[str \| None]` | `VARCHAR` | NULL autorise |

### Creer les tables

```python
# Creer toutes les tables definies
Base.metadata.create_all(engine)

# Supprimer toutes les tables (attention !)
Base.metadata.drop_all(engine)
```

## Sessions et operations CRUD

### La Session

La session est le **centre de controle** de l'ORM. Elle gere :
- Le suivi des objets modifies (Unit of Work)
- Les transactions
- Le cache d'identite (un objet = une seule instance)

```python
from sqlalchemy.orm import Session, sessionmaker

# Methode 1 : Session directe
with Session(engine) as session:
    # operations...
    session.commit()

# Methode 2 : Factory (recommande pour les applications)
SessionLocal = sessionmaker(bind=engine)

with SessionLocal() as session:
    # operations...
    session.commit()
```

### Create (Creer)

```python
with Session(engine) as session:
    # Un seul objet
    user = User(name="Alice", email="alice@example.com", age=30)
    session.add(user)
    session.commit()

    print(user.id)  # L'ID est rempli apres le commit

    # Plusieurs objets
    users = [
        User(name="Bob", email="bob@example.com"),
        User(name="Charlie", email="charlie@example.com"),
    ]
    session.add_all(users)
    session.commit()
```

### Read (Lire)

```python
from sqlalchemy import select

with Session(engine) as session:
    # Par ID (cle primaire)
    user = session.get(User, 1)

    # Un seul resultat
    stmt = select(User).where(User.email == "alice@example.com")
    user = session.execute(stmt).scalar_one_or_none()

    # Plusieurs resultats
    stmt = select(User).where(User.active == True).order_by(User.name)
    users = session.execute(stmt).scalars().all()

    # Avec filtre complexe
    from sqlalchemy import and_, or_

    stmt = select(User).where(
        and_(
            User.age >= 18,
            or_(
                User.name.like("A%"),
                User.name.like("B%"),
            )
        )
    )
    users = session.execute(stmt).scalars().all()
```

### Update (Modifier)

```python
with Session(engine) as session:
    # Modifier un objet
    user = session.get(User, 1)
    user.name = "Alice Updated"
    session.commit()  # SQLAlchemy detecte le changement automatiquement

    # Mise a jour en masse (sans charger les objets)
    from sqlalchemy import update

    stmt = update(User).where(User.active == False).values(active=True)
    session.execute(stmt)
    session.commit()
```

### Delete (Supprimer)

```python
with Session(engine) as session:
    # Supprimer un objet
    user = session.get(User, 1)
    session.delete(user)
    session.commit()

    # Suppression en masse
    from sqlalchemy import delete

    stmt = delete(User).where(User.active == False)
    session.execute(stmt)
    session.commit()
```

## Relations

### One-to-Many (1 → N)

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # Relation : un user a plusieurs posts
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relation inverse
    author: Mapped["User"] = relationship(back_populates="posts")
```

```python
# Utilisation
with Session(engine) as session:
    user = User(name="Alice")
    post = Post(title="Mon premier post", content="Hello !", author=user)

    session.add(user)
    session.commit()

    # Navigation
    print(user.posts)       # [Post(id=1, title='Mon premier post')]
    print(post.author.name) # "Alice"
```

### Many-to-Many (N → N)

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

# Table d'association
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags, back_populates="tags"
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags, back_populates="posts"
    )
```

```python
# Utilisation
with Session(engine) as session:
    tag_python = Tag(name="python")
    tag_sql = Tag(name="sql")

    post = Post(title="ORM en Python", tags=[tag_python, tag_sql])
    session.add(post)
    session.commit()

    # Navigation bidirectionnelle
    print(post.tags)           # [Tag(python), Tag(sql)]
    print(tag_python.posts)    # [Post(ORM en Python)]
```

### One-to-One (1 → 1)

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship(back_populates="profile")
```

## Requetes avancees

### Agregation

```python
from sqlalchemy import func

# Compter
stmt = select(func.count(User.id))
count = session.execute(stmt).scalar()

# Group by
stmt = (
    select(User.active, func.count(User.id).label("total"))
    .group_by(User.active)
)
results = session.execute(stmt).all()
# [(True, 42), (False, 5)]
```

### Jointures explicites

```python
# INNER JOIN
stmt = (
    select(User.name, Post.title)
    .join(Post, User.id == Post.user_id)
)

# LEFT JOIN
stmt = (
    select(User.name, func.count(Post.id))
    .join(Post, User.id == Post.user_id, isouter=True)
    .group_by(User.name)
)
```

### Eager Loading (eviter N+1)

```python
from sqlalchemy.orm import joinedload, selectinload

# joinedload : un seul SELECT avec JOIN
stmt = select(User).options(joinedload(User.posts))
users = session.execute(stmt).unique().scalars().all()

# selectinload : deux SELECT (un pour users, un pour posts)
stmt = select(User).options(selectinload(User.posts))
users = session.execute(stmt).scalars().all()
```

| Strategie | SQL genere | Quand l'utiliser |
|-----------|-----------|-----------------|
| **joinedload** | 1 SELECT + JOIN | Relations 1→1, petites collections |
| **selectinload** | 2 SELECT (IN clause) | Collections larges, N→N |
| **subqueryload** | 2 SELECT (subquery) | Comme selectinload, cas specifiques |
| **lazyload** | N SELECT (a la demande) | Par defaut, OK si peu d'acces |

### SQL brut

```python
from sqlalchemy import text

# Requete brute avec parametres
stmt = text("SELECT * FROM users WHERE age > :min_age")
result = session.execute(stmt, {"min_age": 25}).all()
```

## Bonnes pratiques

### 1. Toujours utiliser des context managers

```python
# ✅ Bon
with Session(engine) as session:
    # La session est fermee automatiquement
    session.commit()

# ❌ Mauvais (fuite de connexion possible)
session = Session(engine)
session.commit()
# Oubli de session.close()
```

### 2. Gerer les erreurs

```python
with Session(engine) as session:
    try:
        user = User(name="Alice", email="alice@example.com")
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Email deja utilise !")
```

### 3. Ne pas melanger session et logique metier

```python
# ❌ Mauvais : la logique metier depend de la session
class UserService:
    def create_user(self, name, email):
        session = Session(engine)
        user = User(name=name, email=email)
        session.add(user)
        session.commit()

# ✅ Bon : injection de la session
class UserService:
    def create_user(self, session: Session, name: str, email: str) -> User:
        user = User(name=name, email=email)
        session.add(user)
        return user
```

## Exercices

### Exercice 1 : Blog

Creer un modele de blog avec :
- `User` (id, name, email)
- `Post` (id, title, content, created_at, user_id)
- `Comment` (id, content, created_at, post_id, user_id)

Relations : Un user a plusieurs posts, un post a plusieurs comments, un user a plusieurs comments.

### Exercice 2 : CRUD complet

Sur le modele du blog :
1. Creer 3 users, 5 posts et 10 comments
2. Lister tous les posts d'un user
3. Compter le nombre de comments par post
4. Trouver le user avec le plus de posts
5. Supprimer un post et verifier que ses comments sont supprimees (cascade)

### Exercice 3 : Optimisation

Identifier et corriger le probleme N+1 dans ce code :

```python
users = session.execute(select(User)).scalars().all()
for user in users:
    print(f"{user.name}: {len(user.posts)} posts")
    for post in user.posts:
        print(f"  - {post.title}: {len(post.comments)} comments")
```

---

> **A retenir** : SQLAlchemy est l'ORM le plus complet de l'ecosysteme Python. Sa force reside dans sa flexibilite : on peut rester au niveau ORM pour le CRUD simple, et descendre au Core pour les requetes complexes. Le style 2.0 avec les `Mapped` types rend le code plus lisible et type-safe.
