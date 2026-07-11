# Ormar — Introduction et CRUD async

## Architecture d'Ormar

Ormar utilise trois bibliothèques en combinaison :

```
Votre code Python
      ↓
   Ormar (modèles + requêtes)
      ↓
   SQLAlchemy Core  (génération SQL)  +  Pydantic (validation)
      ↓
   databases  (connexion async)
      ↓
   asyncpg / aiosqlite (drivers async)
      ↓
   PostgreSQL / SQLite
```

## Installation

```bash
pip install ormar databases[asyncpg] asyncpg
```

## Configuration de base

```python
# database.py
import databases
import sqlalchemy
from ormar import OrmarConfig

DATABASE_URL = "postgresql+asyncpg://formation:formation@localhost:5432/orm_db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Configuration de base partagée par tous les modèles
base_ormar_config = OrmarConfig(
    metadata=metadata,
    database=database
)
```

## Définir des modèles

```python
# models.py
import ormar
from ormar import OrmarConfig
from typing import Optional, List
from datetime import datetime
from database import base_ormar_config

class Categorie(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="categories")

    id: int = ormar.Integer(primary_key=True)
    nom: str = ormar.String(max_length=100, unique=True)
    description: Optional[str] = ormar.Text(nullable=True)
    active: bool = ormar.Boolean(default=True)

class Produit(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="produits")

    id: int = ormar.Integer(primary_key=True)
    nom: str = ormar.String(max_length=200)
    description: Optional[str] = ormar.Text(nullable=True)
    prix: float = ormar.Float()
    stock: int = ormar.Integer(default=0)
    actif: bool = ormar.Boolean(default=True)
    created_at: datetime = ormar.DateTime(default=datetime.utcnow)

    # Relation ForeignKey
    categorie: Optional[Categorie] = ormar.ForeignKey(
        Categorie,
        nullable=True,
        ondelete="SET NULL"
    )
```

## Créer les tables

```python
import asyncio
import sqlalchemy
from database import DATABASE_URL, metadata

async def create_tables():
    engine = sqlalchemy.create_engine(DATABASE_URL.replace("+asyncpg", ""))
    metadata.create_all(engine)
    engine.dispose()
    print("Tables créées")

asyncio.run(create_tables())
```

## CRUD avec Ormar

### CREATE

```python
import asyncio
from database import database

async def exemples_create():
    async with database:
        # Créer une catégorie
        cat = await Categorie.objects.create(
            nom="Informatique",
            description="Matériel informatique"
        )
        print(f"Catégorie: id={cat.id} nom={cat.nom}")

        # Créer un produit avec relation
        produit = await Produit.objects.create(
            nom="Clavier mécanique",
            prix=89.99,
            stock=15,
            categorie=cat
        )
        print(f"Produit: id={produit.id}")

asyncio.run(exemples_create())
```

### READ

```python
async def exemples_read():
    async with database:
        # Tous les enregistrements
        produits = await Produit.objects.all()

        # Filtres
        actifs = await Produit.objects.filter(actif=True).all()
        chers = await Produit.objects.filter(prix__gte=100).all()
        recherche = await Produit.objects.filter(nom__icontains="clavier").all()

        # Tri et pagination
        page_1 = await Produit.objects.order_by("prix").limit(10).all()
        page_2 = await Produit.objects.order_by("prix").offset(10).limit(10).all()

        # Obtenir un seul
        produit = await Produit.objects.get(id=1)   # Exception si non trouvé
        produit = await Produit.objects.get_or_none(id=99)  # None si non trouvé

        # Compter
        total = await Produit.objects.count()

        # Charger les relations (select_related = JOIN)
        produits_avec_cat = await Produit.objects.select_related("categorie").all()
        for p in produits_avec_cat:
            cat_nom = p.categorie.nom if p.categorie else "Sans catégorie"
            print(f"{p.nom} — {cat_nom}")
```

### UPDATE

```python
async def exemples_update():
    async with database:
        # Modifier un objet
        produit = await Produit.objects.get(id=1)
        await produit.update(prix=79.99, stock=20)

        # Update en masse
        nb = await Produit.objects.filter(categorie=None).update(actif=False)
        print(f"{nb} produits désactivés")
```

### DELETE

```python
async def exemples_delete():
    async with database:
        produit = await Produit.objects.get(id=1)
        await produit.delete()

        # Suppression en masse
        await Produit.objects.filter(actif=False).delete()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter le CRUD complet avec Ormar, montrer les résultats
> **Expliquer :** Comparer la syntaxe Ormar (`.objects.create()`, `.objects.filter()`) avec Tortoise-ORM (`.create()`, `.filter()`) et SQLAlchemy (`session.add()`, `select(...).where()`). Montrer que les trois font la même chose avec des styles différents. Insister sur le choix selon le contexte du projet.

---

## Intégration FastAPI

```python
# main.py
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from database import database
import sqlalchemy

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connexion à la BDD au démarrage
    await database.connect()
    yield
    # Déconnexion à l'arrêt
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# Schéma de création (Pydantic)
class ProduitCreate(BaseModel):
    nom: str
    prix: float
    stock: int = 0
    categorie_id: Optional[int] = None

@app.post("/produits/", status_code=201)
async def create_produit(data: ProduitCreate):
    cat = None
    if data.categorie_id:
        cat = await Categorie.objects.get_or_none(id=data.categorie_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")

    produit = await Produit.objects.create(
        nom=data.nom,
        prix=data.prix,
        stock=data.stock,
        categorie=cat
    )
    return produit

@app.get("/produits/")
async def list_produits(actif: Optional[bool] = None):
    query = Produit.objects.select_related("categorie")
    if actif is not None:
        query = query.filter(actif=actif)
    return await query.all()

@app.get("/produits/{produit_id}")
async def get_produit(produit_id: int):
    produit = await Produit.objects.select_related("categorie").get_or_none(id=produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit

@app.delete("/produits/{produit_id}", status_code=204)
async def delete_produit(produit_id: int):
    produit = await Produit.objects.get_or_none(id=produit_id)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    await produit.delete()
```

## Avantages et limites d'Ormar

### Avantages
- Un modèle = ORM + validation Pydantic + schéma API
- Async natif, très bien adapté à FastAPI
- Syntaxe claire et concise

### Limites
- Projet moins actif depuis 2023
- Moins de fonctionnalités avancées que SQLAlchemy
- La génération automatique des tables est moins robuste
- Peu de documentation pour les cas complexes

**Recommandation** : Pour les nouveaux projets FastAPI avec besoin d'async, préférez SQLModel (plus actif, meilleur support Pydantic v2) ou Tortoise-ORM (plus mature en async). Ormar reste intéressant pour comprendre les patterns mais n'est pas le meilleur choix en 2024.
