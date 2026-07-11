# Exercice 01 — API Produits avec PostgreSQL

## Contexte

Vous êtes développeur dans une startup qui vend des produits en ligne. Le CTO vous demande de créer une API REST pour gérer le catalogue de produits. Cette API sera consommée par le frontend de la boutique et par l'application mobile.

**Durée estimée** : 2h30 à 3h

---

## Objectifs

À la fin de cet exercice, vous aurez créé une API FastAPI complète avec :
- Un CRUD complet sur les produits
- Une gestion des catégories
- Une connexion PostgreSQL avec SQLAlchemy
- Les migrations Alembic
- La validation Pydantic
- La gestion des erreurs
- Des tests automatisés

---

## Spécifications fonctionnelles

### Modèle Produit

Un produit possède les propriétés suivantes :

| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | int | Auto, PK | Identifiant unique |
| `name` | string | Requis, 2-100 chars | Nom du produit |
| `description` | string | Optionnel | Description détaillée |
| `sku` | string | Unique, format AAA-0000 | Code article |
| `price` | float | > 0 | Prix HT en euros |
| `tax_rate` | float | 0-100, défaut 20.0 | Taux de TVA % |
| `stock` | int | >= 0, défaut 0 | Quantité en stock |
| `category_id` | int | FK vers categories | Catégorie |
| `is_active` | bool | défaut True | Produit visible |
| `created_at` | datetime | Auto | Date de création |
| `updated_at` | datetime | Auto | Dernière modification |

### Modèle Catégorie

| Champ | Type | Contraintes |
|---|---|---|
| `id` | int | Auto, PK |
| `name` | string | Requis, unique |
| `slug` | string | Auto-généré depuis name |
| `description` | string | Optionnel |

### Endpoints à implémenter

#### Produits
```
GET    /api/v1/products/                  → Lister (filtres + pagination)
GET    /api/v1/products/{id}              → Récupérer un produit
POST   /api/v1/products/                  → Créer un produit
PUT    /api/v1/products/{id}              → Remplacer un produit
PATCH  /api/v1/products/{id}              → Mise à jour partielle
DELETE /api/v1/products/{id}              → Supprimer (soft delete)
GET    /api/v1/products/{id}/price-ttc    → Calculer le prix TTC
```

#### Catégories
```
GET    /api/v1/categories/                → Lister toutes les catégories
GET    /api/v1/categories/{id}            → Récupérer une catégorie
GET    /api/v1/categories/{id}/products   → Produits d'une catégorie
POST   /api/v1/categories/                → Créer une catégorie
DELETE /api/v1/categories/{id}            → Supprimer une catégorie
```

---

## Instructions

### Étape 1 — Mise en place du projet (15 min)

Créez la structure de projet suivante :

```
api-produits/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── category.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── category.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── products.py
│   │   └── categories.py
│   └── crud/
│       ├── __init__.py
│       ├── product.py
│       └── category.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_products.py
│   └── test_categories.py
├── alembic/
├── alembic.ini
├── requirements.txt
├── .env
└── docker-compose.yml
```

```bash
# Créer le projet
mkdir api-produits && cd api-produits
python -m venv venv && source venv/bin/activate
pip install "fastapi[standard]" sqlalchemy psycopg2-binary alembic pydantic-settings python-dotenv pytest httpx
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La création de la structure du projet et l'installation des dépendances dans le terminal
> **Expliquer :** Montrer la commande `mkdir` et la structure de fichiers créée. Expliquer chaque dossier : `models/` pour SQLAlchemy, `schemas/` pour Pydantic, `routers/` pour les routes FastAPI, `crud/` pour la logique de base de données. Insister sur la séparation des responsabilités.

---

### Étape 2 — Configuration (10 min)

Créez le fichier `.env` :

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/products_db
SECRET_KEY=dev-secret-key
DEBUG=true
```

Créez `app/config.py` avec Pydantic Settings pour charger la configuration.

**Indice :**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    # ...
```

### Étape 3 — Modèles SQLAlchemy (20 min)

Créez les modèles SQLAlchemy dans `app/models/`.

**Points importants :**
- Utilisez `relationship()` pour la relation Product ↔ Category
- Ajoutez `cascade="save-update, merge"` sur la relation
- Pensez aux index sur `sku`, `name`, `category_id`, `is_active`
- Générez le `slug` automatiquement dans un `@staticmethod`

**Indice pour le slug :**
```python
import re

@staticmethod
def generate_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r'[àáâãäå]', 'a', slug)
    slug = re.sub(r'[éèêë]', 'e', slug)
    slug = re.sub(r'[îï]', 'i', slug)
    slug = re.sub(r'[ôö]', 'o', slug)
    slug = re.sub(r'[ùûü]', 'u', slug)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug
```

### Étape 4 — Schémas Pydantic (25 min)

Créez les schémas dans `app/schemas/`.

Pour les produits, créez :
- `ProductBase` : champs communs
- `ProductCreate` : données de création (avec validation du SKU via regex)
- `ProductUpdate` : tous les champs optionnels (pour PATCH)
- `ProductReplace` : tous les champs requis (pour PUT)
- `ProductPublic` : réponse API (avec `price_ttc` calculé, sans champs internes)
- `ProductWithCategory` : produit avec ses infos de catégorie imbriquées

**Validation du SKU à implémenter :**
```python
# Format attendu : 3 lettres majuscules, tiret, 4 chiffres
# Exemple : ABC-1234, ELC-9999
sku: str | None = Field(default=None, pattern=r"^[A-Z]{3}-\d{4}$")
```

**Prix TTC calculé :**
```python
@computed_field  # Pydantic v2
@property
def price_ttc(self) -> float:
    return round(self.price * (1 + self.tax_rate / 100), 2)
```

### Étape 5 — Couche CRUD (30 min)

Implémentez les fonctions CRUD dans `app/crud/`.

**Fonctions à implémenter pour les produits :**

```python
def get_product(db: Session, product_id: int) -> Product | None: ...
def get_product_by_sku(db: Session, sku: str) -> Product | None: ...
def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    active_only: bool = True,
) -> list[Product]: ...
def create_product(db: Session, product: ProductCreate) -> Product: ...
def update_product(db: Session, product: Product, data: ProductUpdate) -> Product: ...
def deactivate_product(db: Session, product: Product) -> Product: ...  # Soft delete
def count_products(db: Session, active_only: bool = True) -> int: ...
```

### Étape 6 — Routes FastAPI (40 min)

Implémentez les routes dans `app/routers/`.

**Route de listing avec filtres multiples :**
```python
@router.get("/", response_model=list[ProductPublic])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=2),
    category_id: int | None = None,
    min_price: float | None = Query(default=None, gt=0),
    max_price: float | None = Query(default=None, gt=0),
    in_stock: bool | None = None,
    db: Session = Depends(get_db),
):
    ...
```

**Route pour le prix TTC :**
```python
@router.get("/{product_id}/price-ttc")
def get_price_ttc(product_id: int, db: Session = Depends(get_db)):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    ttc = round(product.price * (1 + product.tax_rate / 100), 2)
    return {
        "product_id": product_id,
        "price_ht": product.price,
        "tax_rate": product.tax_rate,
        "price_ttc": ttc,
    }
```

### Étape 7 — Migrations Alembic (15 min)

```bash
# Initialiser Alembic
alembic init alembic

# Configurer env.py pour pointer vers vos modèles
# (voir module 05 pour les détails)

# Générer la première migration
alembic revision --autogenerate -m "create products and categories tables"

# Vérifier le fichier généré
cat alembic/versions/xxxx_create_products_and_categories_tables.py

# Appliquer
alembic upgrade head
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant la génération et l'application de la migration Alembic
> **Expliquer :** Montrer le fichier de migration généré — expliquer la fonction `upgrade()` (crée les tables) et `downgrade()` (supprime les tables). Puis montrer `alembic upgrade head` avec les messages de succès. Enfin, se connecter à PostgreSQL avec `psql` ou PgAdmin pour montrer que les tables `products` et `categories` ont bien été créées avec toutes leurs colonnes.

---

### Étape 8 — Tests (30 min)

Écrivez des tests pour au moins les scénarios suivants :

**Tests des produits :**
- `test_create_product_success` : créer avec des données valides
- `test_create_product_invalid_sku` : SKU ne correspondant pas au format
- `test_create_product_invalid_price` : price négatif → 422
- `test_get_product_not_found` : ID inexistant → 404
- `test_list_products_with_filters` : filtres par catégorie, prix min/max
- `test_soft_delete` : vérifier que le produit n'apparaît plus dans la liste
- `test_get_price_ttc` : vérifier le calcul du prix TTC

**Tests des catégories :**
- `test_create_category_generates_slug` : vérifier la génération du slug
- `test_get_category_products` : vérifier la relation

---

## Critères d'évaluation

| Critère | Points |
|---|---|
| Structure du projet propre et organisée | 10 |
| Modèles SQLAlchemy corrects (types, contraintes, relations) | 15 |
| Schémas Pydantic avec validation (SKU, prix, etc.) | 15 |
| CRUD complet et fonctionnel | 20 |
| Routes FastAPI avec gestion d'erreurs | 20 |
| Migration Alembic qui fonctionne | 10 |
| Tests automatisés (min. 10 tests) | 10 |
| **Total** | **100** |

### Bonus

- Implémenter la pagination avec les métadonnées (`total`, `page`, `pages`)
- Ajouter un endpoint de recherche plein texte
- Implémenter un soft delete avec champ `deleted_at`
- Ajouter des index de performance sur les requêtes fréquentes

---

## Solution de référence (structure)

```python
# app/schemas/product.py — Solution complète

from pydantic import BaseModel, Field, field_validator, computed_field
from pydantic.config import ConfigDict
from datetime import datetime
import re

class CategoryNested(BaseModel):
    """Catégorie imbriquée dans la réponse produit."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str

class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    sku: str | None = Field(default=None, pattern=r"^[A-Z]{3}-\d{4}$")
    price: float = Field(gt=0)
    tax_rate: float = Field(default=20.0, ge=0, le=100)
    stock: int = Field(default=0, ge=0)
    category_id: int | None = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    """Tous les champs optionnels pour PATCH."""
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    sku: str | None = Field(default=None, pattern=r"^[A-Z]{3}-\d{4}$")
    price: float | None = Field(default=None, gt=0)
    tax_rate: float | None = Field(default=None, ge=0, le=100)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    is_active: bool | None = None

class ProductPublic(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryNested | None = None

    @computed_field
    @property
    def price_ttc(self) -> float:
        return round(self.price * (1 + self.tax_rate / 100), 2)
```

---

## Ressources

- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html)
- [Pydantic computed_field](https://docs.pydantic.dev/latest/concepts/fields/#computed-fields)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
