# Module 03 - SQLModel

## Objectifs du module

- Comprendre le positionnement de SQLModel (SQLAlchemy + Pydantic)
- Definir des modeles qui servent a la fois d'ORM et de schemas API
- Integrer SQLModel avec FastAPI
- Connaitre les patterns recommandes

## Qu'est-ce que SQLModel ?

**SQLModel** est une bibliotheque creee par **Sebastian Ramirez** (le createur de FastAPI) qui combine :

```
┌─────────────┐     ┌─────────────┐
│  SQLAlchemy  │     │  Pydantic   │
│  (ORM)       │     │ (Validation)│
│              │     │              │
│ Persistence  │  +  │ Serialisation│
│ en base      │     │ Validation   │
│ Relations    │     │ JSON schema  │
└──────┬───────┘     └──────┬──────┘
       │                     │
       └─────────┬───────────┘
                 │
         ┌───────▼───────┐
         │   SQLModel     │
         │                │
         │ Un seul modele │
         │ pour tout      │
         └────────────────┘
```

### Le probleme que SQLModel resout

Sans SQLModel, dans une application FastAPI, vous devez definir **3 classes** pour une seule entite :

```python
# ❌ Sans SQLModel : 3 classes pour "User"

# 1. Modele SQLAlchemy (base de donnees)
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))

# 2. Schema Pydantic pour la creation (API input)
class UserCreate(BaseModel):
    name: str
    email: str

# 3. Schema Pydantic pour la reponse (API output)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True
```

Avec SQLModel :

```python
# ✅ Avec SQLModel : tout en un

class UserBase(SQLModel):
    name: str
    email: str

class User(UserBase, table=True):  # Modele de base de donnees
    id: int | None = Field(default=None, primary_key=True)

class UserCreate(UserBase):         # Schema de creation (API)
    pass

class UserPublic(UserBase):         # Schema de reponse (API)
    id: int
```

## Installation

```bash
pip install sqlmodel

# SQLModel inclut SQLAlchemy et Pydantic
# Pas besoin de les installer separement
```

## Definir des modeles

### Modele de base

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):  # table=True → cree une table en base
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True)
    age: int | None = Field(default=None, ge=0, le=150)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Options de Field

```python
Field(
    default=None,          # Valeur par defaut
    default_factory=...,   # Fonction pour la valeur par defaut
    primary_key=True,      # Cle primaire
    unique=True,           # Contrainte unique
    index=True,            # Index pour les recherches
    nullable=True,         # Autorise NULL
    max_length=255,        # Longueur max (String)
    ge=0,                  # Greater or equal (validation Pydantic)
    le=100,                # Less or equal (validation Pydantic)
    regex="^[a-z]+$",     # Regex (validation Pydantic)
    foreign_key="users.id" # Cle etrangere
)
```

### Pattern recommande : modeles separes

```python
# --- Modele de base (champs partages) ---
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

# --- Modele de table (base de donnees) ---
class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")

# --- Schema de creation (input API) ---
class HeroCreate(HeroBase):
    pass

# --- Schema de mise a jour (input API, tous optionnels) ---
class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None

# --- Schema de reponse (output API) ---
class HeroPublic(HeroBase):
    id: int
```

> Ce pattern evite d'exposer des champs sensibles (comme `secret_name` ou `hashed_password`) dans les reponses API, tout en gardant un seul modele de base.

## Connexion et Session

```python
from sqlmodel import SQLModel, Session, create_engine

# Creer l'engine
engine = create_engine("sqlite:///database.db", echo=True)

# Creer les tables
SQLModel.metadata.create_all(engine)

# Utiliser une session
with Session(engine) as session:
    hero = Hero(name="Spider-Man", secret_name="Peter Parker")
    session.add(hero)
    session.commit()
    session.refresh(hero)  # Recharger pour avoir l'ID
    print(hero.id)
```

## Operations CRUD

### Create

```python
with Session(engine) as session:
    hero = Hero(name="Batman", secret_name="Bruce Wayne", age=35)
    session.add(hero)
    session.commit()
    session.refresh(hero)
```

### Read

```python
from sqlmodel import select

with Session(engine) as session:
    # Par ID
    hero = session.get(Hero, 1)

    # Avec filtre
    statement = select(Hero).where(Hero.age >= 18)
    heroes = session.exec(statement).all()

    # Premier resultat
    statement = select(Hero).where(Hero.name == "Batman")
    hero = session.exec(statement).first()

    # Avec LIKE
    statement = select(Hero).where(Hero.name.contains("man"))
    heroes = session.exec(statement).all()

    # Avec ORDER BY et LIMIT
    statement = select(Hero).order_by(Hero.name).limit(10).offset(0)
    heroes = session.exec(statement).all()
```

### Update

```python
with Session(engine) as session:
    hero = session.get(Hero, 1)
    if hero:
        hero.age = 36
        session.add(hero)
        session.commit()
        session.refresh(hero)

    # Update partiel (depuis un schema Pydantic)
    hero_update = HeroUpdate(age=37)
    hero_data = hero_update.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(hero, key, value)
    session.add(hero)
    session.commit()
```

### Delete

```python
with Session(engine) as session:
    hero = session.get(Hero, 1)
    if hero:
        session.delete(hero)
        session.commit()
```

## Relations

### One-to-Many

```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None)

    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")
```

```python
with Session(engine) as session:
    team = Team(name="Avengers", headquarters="New York")
    hero = Hero(name="Iron Man", secret_name="Tony Stark", team=team)

    session.add(hero)
    session.commit()

    # Navigation
    session.refresh(team)
    print(team.heroes)  # [Hero(name='Iron Man')]
```

### Many-to-Many

```python
class HeroTeamLink(SQLModel, table=True):
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    team_id: int | None = Field(
        default=None, foreign_key="team.id", primary_key=True
    )


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    heroes: list["Hero"] = Relationship(
        back_populates="teams", link_model=HeroTeamLink
    )


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    teams: list["Team"] = Relationship(
        back_populates="heroes", link_model=HeroTeamLink
    )
```

## Integration FastAPI

### Application complete

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, create_engine, select

# --- Database ---
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- App ---
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Routes ---
@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session),
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

### Ce qui se passe automatiquement

```
POST /heroes/ avec {"name": "Spider-Man", "secret_name": "Peter Parker"}
       │
       ▼
┌─────────────────┐
│ Pydantic valide │  ← HeroCreate valide le JSON
│ l'input         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SQLModel cree   │  ← Hero(table=True) est un objet ORM
│ l'objet ORM     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SQLAlchemy      │  ← INSERT INTO hero ...
│ persiste en DB  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pydantic        │  ← HeroPublic serialise la reponse
│ serialise       │     (sans secret_name !)
└─────────────────┘
```

## SQLModel vs SQLAlchemy : quand choisir quoi ?

| Critere | SQLModel | SQLAlchemy |
|---------|---------|------------|
| **Avec FastAPI** | Ideal | Fonctionne mais plus verbeux |
| **Validation input** | Integree (Pydantic) | A gerer separement |
| **Relations complexes** | Supporte les bases | Plus flexible |
| **Heritage de tables** | Limite | Complet |
| **Requetes complexes** | Via SQLAlchemy Core | Natif |
| **Maturite** | Recente | 18+ ans |
| **Ecosysteme** | Croissant | Enorme |

### Regle simple

- **Nouveau projet FastAPI** → SQLModel
- **Projet complexe / existant** → SQLAlchemy
- **Besoin de Pydantic + ORM** → SQLModel
- **Besoin de controle total** → SQLAlchemy

## Exercices

### Exercice 1 : API CRUD

Creer une API FastAPI complete pour gerer une liste de taches (todo list) :
- `Task` (id, title, description, completed, created_at)
- Routes : POST, GET (liste + detail), PATCH, DELETE
- Validation : title obligatoire, max 200 caracteres

### Exercice 2 : Relations

Ajouter des categories aux taches :
- `Category` (id, name, color)
- Une tache appartient a une categorie
- Lister les taches par categorie

### Exercice 3 : Pagination et filtres

Implementer :
- Pagination (offset + limit)
- Filtre par statut (completed/pending)
- Recherche par titre (LIKE)
- Tri (par date, par titre)

---

> **A retenir** : SQLModel brille quand vous utilisez FastAPI. Il elimine la duplication entre modeles ORM et schemas Pydantic. Pour les cas simples a intermediaires, c'est le choix ideal. Pour les cas complexes, vous pouvez toujours "descendre" vers SQLAlchemy directement, car SQLModel en est une surcouche.
