# Oxide — ORM Python async, introduction

## Positionnement

Oxide se positionne comme un ORM Python **async-first**, plus simple que SQLAlchemy mais plus complet que de simples query builders. Il est inspiré de frameworks comme Prisma (JavaScript/TypeScript) dans son approche déclarative et ergonomique.

> **Note pédagogique** : Oxide est moins répandu que SQLAlchemy ou Tortoise-ORM. Si vous l'étudiez dans le cadre d'une formation, l'objectif est de comprendre comment différents ORMs Python résolvent les mêmes problèmes avec des approches différentes. Les concepts appris ici se transfèrent directement à d'autres ORMs.

## Principe async-first

Oxide a été conçu dès le départ pour fonctionner avec `asyncio`. Toutes ses opérations sont des coroutines (`async def`).

```python
import asyncio
from oxide import Database, Model, Field

# Connexion à la base de données
db = Database("postgresql://formation:formation@localhost/orm_db")

class Produit(Model):
    class Meta:
        table = "produits"
        database = db

    id = Field(int, primary_key=True, auto_increment=True)
    nom = Field(str, max_length=200)
    prix = Field(float)
    stock = Field(int, default=0)
    actif = Field(bool, default=True)

async def main():
    # Connexion
    await db.connect()

    # Créer les tables
    await db.create_tables([Produit])

    # INSERT
    produit = await Produit.create(nom="Clavier", prix=89.99, stock=15)
    print(f"Créé: {produit.id} — {produit.nom}")

    # SELECT
    produits = await Produit.all()
    for p in produits:
        print(f"{p.nom}: {p.prix}€")

    # SELECT avec filtre
    chers = await Produit.filter(prix__gte=50).all()

    # UPDATE
    await produit.update(prix=79.99)

    # DELETE
    await produit.delete()

    await db.disconnect()

asyncio.run(main())
```

## Connexion et configuration

```python
from oxide import Database

# PostgreSQL
db = Database("postgresql://user:password@host:5432/dbname")

# MySQL
db = Database("mysql://user:password@host:3306/dbname")

# SQLite
db = Database("sqlite:///./ma_base.db")

# Configuration avancée
db = Database(
    "postgresql://formation:formation@localhost/orm_db",
    min_size=2,      # Pool minimum
    max_size=10,     # Pool maximum
    timeout=30,      # Timeout en secondes
)
```

## Définir des modèles

```python
from oxide import Database, Model, Field
from datetime import datetime

db = Database("postgresql://formation:formation@localhost/orm_db")

class Categorie(Model):
    class Meta:
        table = "categories"
        database = db

    id = Field(int, primary_key=True, auto_increment=True)
    nom = Field(str, max_length=100, unique=True)
    description = Field(str, nullable=True)
    active = Field(bool, default=True)

class Article(Model):
    class Meta:
        table = "articles"
        database = db

    id = Field(int, primary_key=True, auto_increment=True)
    titre = Field(str, max_length=200, nullable=False)
    contenu = Field(str)
    publie = Field(bool, default=False)
    vues = Field(int, default=0)
    created_at = Field(datetime, auto_now_add=True)
    updated_at = Field(datetime, auto_now=True)
    categorie_id = Field(int, foreign_key="categories.id", nullable=True)
```

## CRUD complet

### CREATE

```python
async def exemples_create():
    await db.connect()
    await db.create_tables([Categorie, Article])

    # Créer un enregistrement
    cat = await Categorie.create(nom="Technologie", description="Articles tech")
    print(f"Catégorie créée: id={cat.id}")

    # Créer plusieurs enregistrements
    articles = await Article.bulk_create([
        {"titre": "Python en 2024", "contenu": "...", "categorie_id": cat.id},
        {"titre": "Async Python", "contenu": "...", "categorie_id": cat.id},
        {"titre": "ORM comparatifs", "contenu": "...", "categorie_id": cat.id},
    ])
    print(f"{len(articles)} articles créés")
```

### READ

```python
async def exemples_read():
    # Tous les enregistrements
    articles = await Article.all()

    # Filtres
    # Opérateurs : __eq, __ne, __lt, __lte, __gt, __gte, __in, __contains, __startswith
    publies = await Article.filter(publie=True).all()
    populaires = await Article.filter(vues__gte=100).all()
    recents = await Article.filter(titre__contains="Python").all()

    # Chaîner les filtres (équivalent à AND)
    resultats = await Article.filter(
        publie=True,
        categorie_id=1
    ).order_by("-created_at").limit(10).all()

    # Obtenir un seul enregistrement
    article = await Article.get(id=1)          # Lève une exception si non trouvé
    article = await Article.get_or_none(id=99) # Retourne None si non trouvé

    # Premier résultat
    premier = await Article.filter(publie=True).first()

    # Compter
    total = await Article.count()
    nb_publies = await Article.filter(publie=True).count()

    # Vérifier l'existence
    existe = await Article.filter(titre="Test").exists()
```

### UPDATE

```python
async def exemples_update():
    # Modifier un objet récupéré
    article = await Article.get(id=1)
    await article.update(publie=True, vues=article.vues + 1)

    # Modifier en masse sans charger les objets
    nb_modifies = await Article.filter(publie=False).update(publie=True)
    print(f"{nb_modifies} articles publiés")
```

### DELETE

```python
async def exemples_delete():
    # Supprimer un objet
    article = await Article.get(id=1)
    await article.delete()

    # Supprimer en masse
    nb_supprimes = await Article.filter(vues=0, publie=False).delete()
    print(f"{nb_supprimes} articles supprimés")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter un script async complet (create → read → update → delete) et montrer les outputs
> **Expliquer :** Montrer la différence avec SQLAlchemy : pas de `Session`, pas de `commit()` explicite — Oxide gère la transaction automatiquement. Expliquer pourquoi `asyncio.run()` est nécessaire en dehors de FastAPI. Comparer la verbosité avec SQLAlchemy pour le même CRUD.

---

## Intégration FastAPI

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await db.create_tables([Article, Categorie])
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

class ArticleCreate(BaseModel):
    titre: str
    contenu: str
    categorie_id: Optional[int] = None

@app.post("/articles/")
async def create_article(data: ArticleCreate):
    article = await Article.create(**data.model_dump())
    return article

@app.get("/articles/")
async def list_articles(publie: Optional[bool] = None, limit: int = 20):
    query = Article.all() if publie is None else Article.filter(publie=publie)
    return await query.order_by("-created_at").limit(limit).all()

@app.get("/articles/{article_id}")
async def get_article(article_id: int):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article
```

## Comparaison avec SQLAlchemy

| Critère | Oxide | SQLAlchemy |
|---------|-------|-----------|
| Async natif | Oui | Partiel (AsyncSession) |
| Verbosité | Faible | Élevée |
| Flexibilité | Moyenne | Très élevée |
| Requêtes complexes | Limitée | Complète |
| Maturité | Récent | Très mature |
| Communauté | Petite | Grande |
| Migrations | Basiques | Alembic (complet) |

**Recommandation** : Utilisez Oxide pour des projets simples à moyens nécessitant de l'async sans la complexité de SQLAlchemy. Pour des projets complexes en production, SQLAlchemy reste la référence.
