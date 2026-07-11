# Tortoise-ORM — Introduction

## Pourquoi Tortoise-ORM ?

Tortoise-ORM comble un vide : l'ORM de Django est excellent mais synchrone et couplé au framework Django. Tortoise-ORM apporte la même ergonomie en async, utilisable avec n'importe quel framework (FastAPI, Starlette, etc.).

```
Django ORM          →  Synchrone, couplé à Django
SQLAlchemy AsyncIO  →  Async, mais API complexe
Tortoise-ORM        →  Async natif, API Django-like, standalone
```

## Installation

```bash
pip install tortoise-orm[asyncpg]  # PostgreSQL avec asyncpg
pip install aerich                  # Outil de migrations (comme Alembic pour Tortoise)
```

## Configuration

Tortoise-ORM utilise une configuration centralisée qui déclare la connexion et les modules contenant les modèles.

```python
# config.py
TORTOISE_ORM = {
    "connections": {
        "default": "postgres://formation:formation@localhost:5432/orm_db"
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],  # modules Python contenant les modèles
            "default_connection": "default",
        }
    }
}
```

## Définir des modèles

```python
# models.py
from tortoise import fields
from tortoise.models import Model
from datetime import datetime

class Categorie(Model):
    id = fields.IntField(pk=True)
    nom = fields.CharField(max_length=100, unique=True)
    description = fields.TextField(null=True)
    active = fields.BooleanField(default=True)

    # Relation inverse (définie automatiquement par la FK sur Produit)
    # produits → RelatedManager

    class Meta:
        table = "categories"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

class Produit(Model):
    id = fields.IntField(pk=True)
    nom = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    prix = fields.DecimalField(max_digits=10, decimal_places=2)
    stock = fields.IntField(default=0)
    actif = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Foreign Key — relation ManyToOne
    categorie = fields.ForeignKeyField(
        "models.Categorie",
        related_name="produits",  # Nom de l'accès inverse : categorie.produits
        null=True,
        on_delete=fields.SET_NULL
    )

    class Meta:
        table = "produits"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} ({self.prix}€)"

class Tag(Model):
    id = fields.IntField(pk=True)
    nom = fields.CharField(max_length=50, unique=True)

    # Relation ManyToMany
    produits: fields.ManyToManyRelation["Produit"]

    class Meta:
        table = "tags"

# Ajouter la relation M2M côté Produit (ou Tag — peu importe)
Produit.tags = fields.ManyToManyField(
    "models.Tag",
    related_name="produits",
    through="produit_tag"  # Nom de la table pivot
)
```

## Initialiser Tortoise-ORM

### Mode script (asyncio direct)

```python
import asyncio
from tortoise import Tortoise

async def init():
    await Tortoise.init(
        db_url="postgres://formation:formation@localhost:5432/orm_db",
        modules={"models": ["models"]}
    )
    # Générer les schémas (CREATE TABLE IF NOT EXISTS)
    await Tortoise.generate_schemas()

async def main():
    await init()

    # ... votre code ici ...

    await Tortoise.close_connections()

asyncio.run(main())
```

### Mode FastAPI avec tortoise.contrib.fastapi

```python
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()

register_tortoise(
    app,
    db_url="postgres://formation:formation@localhost:5432/orm_db",
    modules={"models": ["app.models"]},
    generate_schemas=True,   # Crée les tables au démarrage (dev seulement)
    add_exception_handlers=True,
)
```

## CRUD complet

### CREATE

```python
async def exemples_create():
    # Méthode 1 : create() — crée et sauvegarde en une ligne
    cat = await Categorie.create(nom="Informatique", description="Matériel IT")
    print(f"Créé: {cat.id} — {cat.nom}")

    # Méthode 2 : instancier puis save()
    produit = Produit(nom="Clavier mécanique", prix=89.99, stock=15, categorie=cat)
    await produit.save()
    print(f"Produit créé: {produit.id}")

    # Bulk create
    await Produit.bulk_create([
        Produit(nom="Souris", prix=29.99, stock=50),
        Produit(nom="Écran", prix=349.00, stock=8),
        Produit(nom="Webcam", prix=79.99, stock=25),
    ])
```

### READ

```python
async def exemples_read():
    # Tous
    produits = await Produit.all()

    # Filtre simple
    actifs = await Produit.filter(actif=True).all()

    # Opérateurs de filtre (syntaxe Django __field__lookup)
    chers = await Produit.filter(prix__gte=100).all()
    pas_chers = await Produit.filter(prix__lt=50).all()
    par_nom = await Produit.filter(nom__icontains="clavier").all()
    dans_cats = await Produit.filter(categorie_id__in=[1, 2, 3]).all()

    # Chaîner les filtres (AND implicite)
    resultats = await Produit.filter(
        actif=True,
        prix__gte=20,
        prix__lte=200
    ).order_by("prix").limit(10).all()

    # Obtenir un seul
    produit = await Produit.get(id=1)        # Exception si non trouvé
    produit = await Produit.get_or_none(id=99)  # None si non trouvé

    # Compter
    total = await Produit.all().count()
    nb_actifs = await Produit.filter(actif=True).count()

    # Exclure
    sans_stock = await Produit.exclude(stock__gt=0).all()

    # Premier/Dernier
    premier = await Produit.all().first()
    dernier = await Produit.all().order_by("-created_at").first()
```

### Charger les relations (prefetch)

```python
async def exemples_relations():
    # Sans prefetch → lazy loading (N+1 possible)
    produits = await Produit.all()
    for p in produits:
        cat = await p.categorie  # Requête SQL à chaque itération !

    # Avec prefetch_related → résout le N+1
    produits = await Produit.all().prefetch_related("categorie")
    for p in produits:
        print(f"{p.nom} — catégorie: {p.categorie.nom}")  # Pas de requête supp.

    # select_related — JOIN SQL (pour relations *→1)
    produits = await Produit.all().select_related("categorie")

    # Accéder à la relation inverse (1→N)
    cat = await Categorie.get(id=1)
    produits_cat = await cat.produits.all()
    print(f"Produits dans {cat.nom}: {len(produits_cat)}")

    # Prefetch sur les relations M2M
    produits = await Produit.all().prefetch_related("tags")
    for p in produits:
        tags = [t.nom for t in p.tags]
        print(f"{p.nom}: tags={tags}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — montrer le problème N+1 sans `prefetch_related`, puis la solution avec, en activant les logs SQL de Tortoise
> **Expliquer :** Activer `logging` pour tortoise (niveau DEBUG) afin de voir toutes les requêtes. Exécuter le même code avec et sans `prefetch_related` et compter les requêtes SQL générées. C'est la même démonstration que SQLAlchemy mais avec la syntaxe Tortoise.

---

### UPDATE

```python
async def exemples_update():
    produit = await Produit.get(id=1)
    produit.prix = 79.99
    produit.stock = 20
    await produit.save()

    # Update en masse
    nb = await Produit.filter(categorie_id=None).update(actif=False)
    print(f"{nb} produits désactivés")

    # update_or_create (cherche ou crée)
    cat, created = await Categorie.update_or_create(
        {"description": "Articles tech mis à jour"},
        nom="Technologie"
    )
    print(f"{'Créé' if created else 'Mis à jour'}: {cat.nom}")
```

### DELETE

```python
async def exemples_delete():
    produit = await Produit.get(id=1)
    await produit.delete()

    # Suppression en masse
    nb = await Produit.filter(actif=False, stock=0).delete()
    print(f"{nb} produits supprimés")
```

## Agrégations

```python
from tortoise.functions import Count, Sum, Avg, Min, Max
from tortoise.expressions import Q

async def exemples_agregations():
    # Compter par catégorie
    from tortoise import connections

    # Requête avec annotate (GROUP BY implicite)
    categories = await Categorie.annotate(
        nb_produits=Count("produits"),
        prix_moyen=Avg("produits__prix")
    ).filter(nb_produits__gt=0).all()

    for cat in categories:
        print(f"{cat.nom}: {cat.nb_produits} produits à {cat.prix_moyen:.2f}€ en moy.")

    # Requête Q — OR logique
    resultats = await Produit.filter(
        Q(prix__lt=30) | Q(prix__gt=300)
    ).all()
    print(f"Produits < 30€ ou > 300€: {len(resultats)}")
```

## Pydantic avec Tortoise

```python
from tortoise.contrib.pydantic import pydantic_model_creator

# Générer automatiquement un schéma Pydantic depuis un modèle Tortoise
ProduitSchema = pydantic_model_creator(Produit, name="ProduitSchema")
ProduitCreateSchema = pydantic_model_creator(
    Produit,
    name="ProduitCreate",
    exclude=("id", "created_at", "updated_at")
)

# Utilisation dans FastAPI
from fastapi import FastAPI

@app.get("/produits/{id}")
async def get_produit(id: int):
    produit = await Produit.get(id=id)
    return await ProduitSchema.from_tortoise_orm(produit)

@app.get("/produits/")
async def list_produits():
    return await ProduitSchema.from_queryset(Produit.all())
```

## Résumé — Tortoise-ORM vs Django ORM

| Fonctionnalité | Tortoise-ORM | Django ORM |
|----------------|--------------|------------|
| Async | Natif | Non (depuis Django 4.1 partiel) |
| Dépendance framework | Aucune | Django complet |
| Syntaxe | Identique | Référence |
| Migrations | Aerich | Django migrations |
| Admin UI | Non | Oui (Django Admin) |
| Communauté | Moyenne | Très grande |
