# SQLModel — Intégration avec FastAPI

## Architecture d'une application FastAPI + SQLModel

```
app/
├── main.py           ← Application FastAPI, routes
├── database.py       ← Engine, session, lifespan
├── models.py         ← Modèles SQLModel (table=True)
└── schemas.py        ← Schémas Pydantic (validation API)
```

## database.py — Configuration de la base de données

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

DATABASE_URL = "postgresql+psycopg2://formation:formation@localhost/orm_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Vérifie les connexions avant utilisation
)

def create_db_and_tables():
    """Crée toutes les tables si elles n'existent pas."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency FastAPI : fournit une session par requête HTTP."""
    with Session(engine) as session:
        yield session
```

## models.py — Modèles de table

```python
# models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Categorie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=100, unique=True)
    description: Optional[str] = None

    produits: List["Produit"] = Relationship(back_populates="categorie")

class Produit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=200)
    description: Optional[str] = None
    prix: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    actif: bool = Field(default=True)
    categorie_id: Optional[int] = Field(default=None, foreign_key="categorie.id")

    categorie: Optional["Categorie"] = Relationship(back_populates="produits")
```

## schemas.py — Schémas de validation API

```python
# schemas.py
from sqlmodel import SQLModel, Field
from typing import Optional

# --- Produit ---
class ProduitBase(SQLModel):
    nom: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    prix: float = Field(gt=0, description="Prix HT en euros")
    stock: int = Field(default=0, ge=0)
    actif: bool = Field(default=True)
    categorie_id: Optional[int] = None

class ProduitCreate(ProduitBase):
    pass  # Identique à Base pour la création

class ProduitUpdate(SQLModel):
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    prix: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    actif: Optional[bool] = None
    categorie_id: Optional[int] = None

class ProduitPublic(ProduitBase):
    id: int

class ProduitAvecCategorie(ProduitPublic):
    categorie: Optional["CategoriePublic"] = None

# --- Categorie ---
class CategorieBase(SQLModel):
    nom: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None

class CategorieCreate(CategorieBase):
    pass

class CategoriePublic(CategorieBase):
    id: int

class CategorieAvecProduits(CategoriePublic):
    produits: List["ProduitPublic"] = []

# Résoudre les références circulaires
ProduitAvecCategorie.model_rebuild()
CategorieAvecProduits.model_rebuild()
```

## main.py — Application FastAPI complète

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from typing import List, Optional

from database import create_db_and_tables, get_session
from models import Produit, Categorie
from schemas import (
    ProduitCreate, ProduitUpdate, ProduitPublic, ProduitAvecCategorie,
    CategorieCreate, CategoriePublic, CategorieAvecProduits
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crée les tables au démarrage."""
    create_db_and_tables()
    yield

app = FastAPI(
    title="API Produits",
    description="CRUD de produits avec SQLModel + FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================
# CATEGORIES
# ============================================================

@app.post("/categories/", response_model=CategoriePublic, status_code=201)
def create_categorie(
    categorie: CategorieCreate,
    session: Session = Depends(get_session)
):
    db_cat = Categorie.model_validate(categorie)
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat

@app.get("/categories/", response_model=List[CategoriePublic])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Categorie)).all()

@app.get("/categories/{categorie_id}", response_model=CategorieAvecProduits)
def get_categorie(categorie_id: int, session: Session = Depends(get_session)):
    cat = session.get(Categorie, categorie_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return cat

# ============================================================
# PRODUITS
# ============================================================

@app.post("/produits/", response_model=ProduitPublic, status_code=201)
def create_produit(
    produit: ProduitCreate,
    session: Session = Depends(get_session)
):
    # Vérifier que la catégorie existe si fournie
    if produit.categorie_id:
        cat = session.get(Categorie, produit.categorie_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")

    db_produit = Produit.model_validate(produit)
    session.add(db_produit)
    session.commit()
    session.refresh(db_produit)
    return db_produit

@app.get("/produits/", response_model=List[ProduitPublic])
def list_produits(
    actif: Optional[bool] = Query(default=None, description="Filtrer par statut actif"),
    categorie_id: Optional[int] = Query(default=None),
    min_prix: Optional[float] = Query(default=None, gt=0),
    max_prix: Optional[float] = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    stmt = select(Produit)
    if actif is not None:
        stmt = stmt.where(Produit.actif == actif)
    if categorie_id:
        stmt = stmt.where(Produit.categorie_id == categorie_id)
    if min_prix:
        stmt = stmt.where(Produit.prix >= min_prix)
    if max_prix:
        stmt = stmt.where(Produit.prix <= max_prix)
    stmt = stmt.offset(offset).limit(limit)
    return session.exec(stmt).all()

@app.get("/produits/{produit_id}", response_model=ProduitAvecCategorie)
def get_produit(produit_id: int, session: Session = Depends(get_session)):
    produit = session.get(Produit, produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

@app.patch("/produits/{produit_id}", response_model=ProduitPublic)
def update_produit(
    produit_id: int,
    produit_update: ProduitUpdate,
    session: Session = Depends(get_session)
):
    produit = session.get(Produit, produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # exclude_unset=True → ne modifier que les champs envoyés
    update_data = produit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(produit, field, value)

    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit

@app.delete("/produits/{produit_id}", status_code=204)
def delete_produit(produit_id: int, session: Session = Depends(get_session)):
    produit = session.get(Produit, produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    session.delete(produit)
    session.commit()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur — ouvrir `http://localhost:8000/docs` et montrer la documentation Swagger auto-générée
> **Expliquer :** Montrer que FastAPI génère automatiquement la doc Swagger depuis les schémas SQLModel. Cliquer sur chaque endpoint, montrer les schémas de requête/réponse. Tester `POST /produits/` directement depuis Swagger, montrer la validation automatique (tenter d'envoyer un prix négatif). Montrer comment `response_model` filtre les champs dans la réponse.

---

## Lancer l'application

```bash
pip install fastapi uvicorn sqlmodel psycopg2-binary

# Lancer le serveur
uvicorn main:app --reload --port 8000

# Tester avec curl
curl -X POST "http://localhost:8000/categories/" \
  -H "Content-Type: application/json" \
  -d '{"nom": "Informatique", "description": "Matériel informatique"}'

curl -X POST "http://localhost:8000/produits/" \
  -H "Content-Type: application/json" \
  -d '{"nom": "Clavier mécanique", "prix": 89.99, "stock": 15, "categorie_id": 1}'

curl "http://localhost:8000/produits/?min_prix=50&actif=true"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal + Swagger — exécuter les requêtes curl, montrer les réponses JSON, puis aller dans DBeaver et montrer les données insérées en BDD
> **Expliquer :** Montrer la correspondance entre la requête HTTP, le schéma Pydantic qui valide, le modèle SQLModel qui persiste, et la réponse filtrée par `response_model`. Insister sur le fait qu'un seul modèle fait tout.

---

## Session asynchrone (FastAPI async)

```python
# Pour les applications haute performance
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    "postgresql+asyncpg://formation:formation@localhost/orm_db"
)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/produits/async/", response_model=List[ProduitPublic])
async def list_produits_async(session: AsyncSession = Depends(get_async_session)):
    result = await session.exec(select(Produit))
    return result.all()
```
