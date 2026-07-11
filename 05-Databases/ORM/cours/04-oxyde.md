# Module 04 - Oxyde

## Objectifs du module

- Comprendre le positionnement d'Oxyde dans l'ecosysteme ORM Python
- Decouvrir son approche inspiree de Rust et des ORM modernes
- Definir des modeles et effectuer des operations CRUD
- Comparer Oxyde avec SQLAlchemy et SQLModel

## Qu'est-ce qu'Oxyde ?

**Oxyde** est un ORM Python moderne qui se distingue par une approche inspiree des ecosystemes Rust et TypeScript. Il vise a offrir :

- Une **API declarative** claire et concise
- Un **typage fort** de bout en bout
- Des **performances** optimisees
- Une experience developpeur moderne

```
Ecosysteme ORM Python - Evolution

2006              2021              2024+
SQLAlchemy  ───>  SQLModel   ───>  Oxyde
                                   (+ autres)
Complet,          SQLAlchemy       Approche
flexible,         + Pydantic       nouvelle
verbeux           + FastAPI        generation
```

### Philosophie

| Principe | Description |
|----------|-------------|
| **Type-safety** | Le typage guide le developpeur et previent les erreurs |
| **Zero magic** | Comportement explicite, pas de surprises |
| **Performance** | Requetes optimisees, lazy loading intelligent |
| **Developer Experience** | API intuitive, messages d'erreur clairs |

## Installation

```bash
pip install oxyde
```

## Definir des modeles

### Configuration de la connexion

```python
from oxyde import Database, Model, Field

# Configurer la base de donnees
db = Database("sqlite:///app.db")
# ou
db = Database("postgresql://user:pass@localhost/mydb")
```

### Modele de base

```python
from oxyde import Model, Field
from datetime import datetime

class User(Model):
    __tablename__ = "users"

    id: int = Field(primary_key=True, auto_increment=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True)
    age: int | None = Field(default=None)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Types et contraintes

```python
class Product(Model):
    __tablename__ = "products"

    id: int = Field(primary_key=True, auto_increment=True)
    name: str = Field(max_length=200, index=True)
    price: float = Field(ge=0)                        # >= 0
    stock: int = Field(default=0, ge=0)
    category: str = Field(max_length=50, index=True)
    description: str | None = Field(default=None)
    sku: str = Field(max_length=20, unique=True)       # Stock Keeping Unit
```

## Operations CRUD

### Create

```python
async def create_user():
    user = User(name="Alice", email="alice@example.com", age=30)
    await db.save(user)
    print(user.id)  # ID genere automatiquement
```

### Read

```python
async def read_users():
    # Par ID
    user = await db.get(User, id=1)

    # Avec filtre
    users = await db.find(User, where=User.active == True)

    # Requete complexe
    users = await db.find(
        User,
        where=(User.age >= 18) & (User.active == True),
        order_by=User.name,
        limit=10,
        offset=0,
    )

    # Premier resultat
    user = await db.find_one(User, where=User.email == "alice@example.com")
```

### Update

```python
async def update_user():
    user = await db.get(User, id=1)
    user.name = "Alice Updated"
    await db.save(user)

    # Update en masse
    await db.update(
        User,
        where=User.active == False,
        values={"active": True},
    )
```

### Delete

```python
async def delete_user():
    user = await db.get(User, id=1)
    await db.delete(user)

    # Delete en masse
    await db.delete_many(User, where=User.active == False)
```

## Relations

### One-to-Many

```python
class Author(Model):
    __tablename__ = "authors"

    id: int = Field(primary_key=True, auto_increment=True)
    name: str = Field(max_length=100)

    books: list["Book"] = Relation(back_populates="author")


class Book(Model):
    __tablename__ = "books"

    id: int = Field(primary_key=True, auto_increment=True)
    title: str = Field(max_length=200)
    author_id: int = Field(foreign_key="authors.id")

    author: "Author" = Relation(back_populates="books")
```

```python
async def create_with_relation():
    author = Author(name="Victor Hugo")
    book = Book(title="Les Miserables", author=author)

    await db.save(author)
    await db.save(book)

    # Charger les relations
    author = await db.get(Author, id=1, include=["books"])
    print(author.books)  # [Book(title='Les Miserables')]
```

### Many-to-Many

```python
class StudentCourse(Model):
    __tablename__ = "student_courses"

    student_id: int = Field(foreign_key="students.id", primary_key=True)
    course_id: int = Field(foreign_key="courses.id", primary_key=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)


class Student(Model):
    __tablename__ = "students"

    id: int = Field(primary_key=True, auto_increment=True)
    name: str = Field(max_length=100)

    courses: list["Course"] = Relation(
        through=StudentCourse, back_populates="students"
    )


class Course(Model):
    __tablename__ = "courses"

    id: int = Field(primary_key=True, auto_increment=True)
    title: str = Field(max_length=200)

    students: list["Student"] = Relation(
        through=StudentCourse, back_populates="courses"
    )
```

## Async natif

Un des avantages majeurs d'Oxyde : le support **async natif**, ideal pour les applications web modernes :

```python
import asyncio
from oxyde import Database, Model, Field

db = Database("sqlite+aiosqlite:///app.db")

async def main():
    await db.create_tables()

    # Toutes les operations sont async
    user = User(name="Alice", email="alice@example.com")
    await db.save(user)

    users = await db.find(User, where=User.active == True)
    for user in users:
        print(user.name)

asyncio.run(main())
```

### Avec FastAPI

```python
from fastapi import FastAPI
from oxyde import Database

db = Database("postgresql+asyncpg://user:pass@localhost/mydb")
app = FastAPI()

@app.on_event("startup")
async def startup():
    await db.create_tables()

@app.post("/users/")
async def create_user(name: str, email: str):
    user = User(name=name, email=email)
    await db.save(user)
    return user

@app.get("/users/")
async def list_users():
    return await db.find(User, order_by=User.name)
```

## Comparaison avec SQLAlchemy et SQLModel

### Meme operation, trois styles

**Creer un utilisateur et ses posts :**

```python
# --- SQLAlchemy ---
with Session(engine) as session:
    user = UserSA(name="Alice", email="alice@ex.com")
    post = PostSA(title="Hello", content="World", author=user)
    session.add(user)
    session.commit()

# --- SQLModel ---
with Session(engine) as session:
    user = UserSM(name="Alice", email="alice@ex.com")
    post = PostSM(title="Hello", content="World", author=user)
    session.add(user)
    session.commit()
    session.refresh(user)

# --- Oxyde ---
user = UserOx(name="Alice", email="alice@ex.com")
post = PostOx(title="Hello", content="World", author=user)
await db.save(user)
await db.save(post)
```

### Tableau comparatif

| Critere | SQLAlchemy | SQLModel | Oxyde |
|---------|-----------|---------|-------|
| **Async natif** | Via extension | Non | Oui |
| **Typage** | Bon (2.0) | Excellent | Excellent |
| **API** | Verbeuse mais complete | Concise | Concise |
| **Validation** | Non | Oui (Pydantic) | Oui (integree) |
| **Maturite** | 18+ ans | 4+ ans | Recente |
| **Communaute** | Tres large | Large | En croissance |
| **Documentation** | Tres complete | Bonne | En croissance |
| **FastAPI** | Manuel | Natif | Bon |
| **Migrations** | Alembic | Alembic | Integrees |

## Quand choisir Oxyde ?

### Bon choix

- Nouveau projet sans contrainte de compatibilite
- Application async (FastAPI, Starlette)
- Equipe qui valorise le typage fort et l'API moderne
- Projet de taille moyenne

### Moins adapte

- Projet existant avec SQLAlchemy (migration couteuse)
- Besoin de fonctionnalites ORM avancees (heritage de tables, polymorphisme)
- Besoin d'une communaute large et de ressources abondantes
- Projet critique en production (maturite moindre)

## Exercices

### Exercice 1 : CRUD basique

Creer une application de gestion de livres avec Oxyde :
- `Book` (id, title, author, isbn, published_year, available)
- Implementer toutes les operations CRUD
- Ajouter des filtres (par auteur, par annee, par disponibilite)

### Exercice 2 : Relations

Etendre l'application avec :
- `Library` (id, name, city)
- `BookCopy` (id, book_id, library_id, condition)
- Un livre peut avoir plusieurs copies dans plusieurs bibliotheques

### Exercice 3 : API async

Creer une API FastAPI avec Oxyde pour gerer un systeme de reservations :
- `User`, `Book`, `Reservation`
- Routes async pour toutes les operations
- Gestion des conflits (livre deja reserve)

---

> **A retenir** : Oxyde represente une nouvelle generation d'ORM Python avec un focus sur l'async, le typage et l'experience developpeur. C'est un choix pertinent pour les nouveaux projets, mais SQLAlchemy reste la reference pour les cas complexes et les projets existants.
