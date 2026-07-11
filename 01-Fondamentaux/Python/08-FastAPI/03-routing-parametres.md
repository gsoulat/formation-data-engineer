# Module 03 — Routing et paramètres

## Sommaire
1. [Les paramètres de chemin (path parameters)](#1-les-paramètres-de-chemin-path-parameters)
2. [Les paramètres de requête (query parameters)](#2-les-paramètres-de-requête-query-parameters)
3. [Le corps de la requête (request body)](#3-le-corps-de-la-requête-request-body)
4. [Les méthodes HTTP](#4-les-méthodes-http)
5. [Modèles de réponse (response_model)](#5-modèles-de-réponse-response_model)
6. [Paramètres mixtes](#6-paramètres-mixtes)
7. [APIRouter — organiser les routes](#7-apirouter--organiser-les-routes)
8. [Gestion des erreurs](#8-gestion-des-erreurs)

---

## 1. Les paramètres de chemin (path parameters)

Les paramètres de chemin sont des parties dynamiques de l'URL, déclarés entre accolades `{}`.

### Déclaration de base

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# Appel : GET /users/42
# Réponse : {"user_id": 42}

# Appel : GET /users/abc
# Réponse : 422 Unprocessable Entity (abc n'est pas un int)
```

### Types supportés

FastAPI valide et convertit automatiquement les types :

```python
from fastapi import FastAPI
from uuid import UUID
from datetime import date

app = FastAPI()

# Entier
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

# Float
@app.get("/prices/{price}")
def get_price(price: float):
    return {"price": price}

# UUID (format standard pour les IDs)
@app.get("/orders/{order_id}")
def get_order(order_id: UUID):
    return {"order_id": str(order_id)}

# Date (format YYYY-MM-DD)
@app.get("/events/{event_date}")
def get_events(event_date: date):
    return {"date": event_date.isoformat()}

# String (par défaut, accepte tout)
@app.get("/files/{filename}")
def get_file(filename: str):
    return {"filename": filename}
```

### Chemin avec sous-chemins (Path avec `...`)

Pour capturer un chemin complet (avec des `/` à l'intérieur) :

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    # file_path peut contenir des /
    return {"file_path": file_path}

# Appel : GET /files/documents/2024/rapport.pdf
# Réponse : {"file_path": "documents/2024/rapport.pdf"}
```

### Paramètres de chemin prédéfinis avec Enum

Les Enum permettent de restreindre les valeurs acceptées :

```python
from fastapi import FastAPI
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        description = "AlexNet : pionnier des CNN profonds"
    elif model_name == ModelName.resnet:
        description = "ResNet : réseau résiduel"
    else:
        description = "LeNet : l'un des premiers CNN"

    return {
        "model_name": model_name.value,
        "description": description
    }

# Appel : GET /models/resnet → OK
# Appel : GET /models/vgg → 422 (valeur non autorisée)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La Swagger UI avec le dropdown de sélection généré pour un paramètre Enum
> **Expliquer :** Montrer que Swagger UI génère automatiquement un menu déroulant pour les Enum. Tester avec une valeur valide et une invalide. Montrer le message d'erreur 422 généré automatiquement par FastAPI quand la valeur n'est pas dans l'Enum.

---

### Ordre des routes

L'ordre de déclaration des routes est important. Les routes statiques doivent être déclarées **avant** les routes dynamiques.

```python
from fastapi import FastAPI

app = FastAPI()

# ✓ CORRECT : route statique AVANT route dynamique
@app.get("/users/me")        # Route statique en premier
def get_current_user():
    return {"user": "utilisateur courant"}

@app.get("/users/{user_id}") # Route dynamique après
def get_user(user_id: str):
    return {"user_id": user_id}


# ✗ INCORRECT : la route dynamique capturera "me" avant la route statique
@app.get("/categories/{cat_id}")  # Capturera aussi /categories/featured !
def get_category(cat_id: str):
    return {"cat_id": cat_id}

@app.get("/categories/featured")  # JAMAIS atteinte !
def featured_categories():
    return {"categories": ["top", "new"]}
```

---

## 2. Les paramètres de requête (query parameters)

Les paramètres de requête sont ajoutés après `?` dans l'URL : `/items?skip=0&limit=10`

### Paramètres optionnels et obligatoires

```python
from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/items/")
def list_items(
    skip: int = 0,          # Optionnel, défaut 0
    limit: int = 10,        # Optionnel, défaut 10
    search: str | None = None,  # Optionnel, peut être None
):
    """
    Lister les items avec pagination et recherche.

    - skip : nombre d'items à sauter
    - limit : nombre max d'items retournés
    - search : terme de recherche (optionnel)
    """
    fake_items = [
        {"id": i, "name": f"Item {i}"} for i in range(1, 101)
    ]

    if search:
        fake_items = [item for item in fake_items if search.lower() in item["name"].lower()]

    return fake_items[skip : skip + limit]

# Appels valides :
# GET /items/
# GET /items/?skip=20&limit=5
# GET /items/?search=item 5
# GET /items/?skip=10&limit=20&search=test
```

### Paramètre obligatoire (sans valeur par défaut)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
def get_items(
    category: str,       # Obligatoire (pas de valeur par défaut)
    active: bool = True, # Optionnel
):
    return {"category": category, "active": active}

# GET /items/?category=electronics        → OK
# GET /items/                              → 422 (category manquante)
# GET /items/?category=electronics&active=false → OK
```

### Conversion de types booléens

FastAPI accepte plusieurs formes pour les booléens :

```python
# Valeurs acceptées comme True :  1, true, on, yes
# Valeurs acceptées comme False : 0, false, off, no

# GET /items/?active=true  → active = True
# GET /items/?active=1     → active = True
# GET /items/?active=yes   → active = True
# GET /items/?active=false → active = False
# GET /items/?active=0     → active = False
```

### Query avec `Query()` pour la validation

```python
from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()

@app.get("/items/")
def list_items(
    q: Annotated[str | None, Query(
        title="Terme de recherche",
        description="Recherche dans le nom et la description des items",
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9 ]+$",  # Regex : lettres, chiffres, espaces
    )] = None,

    limit: Annotated[int, Query(
        ge=1,    # Greater or equal : >= 1
        le=100,  # Less or equal : <= 100
    )] = 10,
):
    return {"q": q, "limit": limit}

# GET /items/?q=ab     → 422 (min_length=3 non respecté)
# GET /items/?q=hello  → OK
# GET /items/?limit=0  → 422 (ge=1 non respecté)
# GET /items/?limit=50 → OK
```

### Paramètres de requête multiples (liste)

```python
from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()

@app.get("/items/")
def get_items_by_ids(
    ids: Annotated[list[int], Query()] = [],
):
    return {"ids": ids}

# GET /items/?ids=1&ids=2&ids=3
# Réponse : {"ids": [1, 2, 3]}
```

---

## 3. Le corps de la requête (request body)

Pour envoyer des données au serveur (POST, PUT, PATCH), on utilise le corps de la requête.

### Corps de base avec Pydantic

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
def create_item(item: Item):
    """
    Créer un item.

    Le corps de la requête doit être un JSON avec :
    - name (string, requis)
    - description (string, optionnel)
    - price (float, requis)
    - tax (float, optionnel)
    """
    item_dict = item.model_dump()

    # Calculer le prix avec taxe si applicable
    if item.tax:
        item_dict["price_with_tax"] = item.price + item.tax

    return item_dict
```

Exemple de corps JSON à envoyer :

```json
{
  "name": "Marteau",
  "description": "Un excellent marteau de charpentier",
  "price": 29.99,
  "tax": 3.0
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La Swagger UI pour le POST /items/ — montrer le formulaire de corps JSON
> **Expliquer :** Ouvrir la route POST dans Swagger, cliquer "Try it out". Montrer le JSON exemple pré-rempli. Modifier les valeurs, cliquer Execute. Montrer la réponse avec `price_with_tax`. Ensuite, tester avec des données invalides (price en string) pour montrer l'erreur 422.

---

### Corps avec `Body()` pour validation avancée

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    item: Item,
    importance: Annotated[int, Body(ge=1, le=5)] = 1,
    # importance est un champ du body mais pas dans le modèle Pydantic
):
    return {
        "item_id": item_id,
        "item": item,
        "importance": importance
    }
```

Corps JSON attendu :
```json
{
  "item": {"name": "Tournevis", "price": 15.0},
  "importance": 3
}
```

### Plusieurs corps dans une requête

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str
    email: str

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, user: User):
    return {
        "item_id": item_id,
        "item": item,
        "user": user
    }
```

Corps JSON attendu :
```json
{
  "item": {
    "name": "Tournevis",
    "price": 15.0
  },
  "user": {
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

### Formulaires HTML

```python
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login/")
def login(
    username: str = Form(...),  # ... signifie obligatoire
    password: str = Form(...),
):
    return {"username": username}
```

> Requiert `pip install python-multipart`

### Upload de fichiers

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content),
    }

@app.post("/upload-multiple/")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(content),
        })
    return results
```

---

## 4. Les méthodes HTTP

FastAPI supporte toutes les méthodes HTTP standard. La convention REST à suivre :

| Méthode | Utilisation | Idempotent | Exemple |
|---|---|---|---|
| GET | Lire une ressource | Oui | `GET /users/1` |
| POST | Créer une ressource | Non | `POST /users/` |
| PUT | Remplacer une ressource | Oui | `PUT /users/1` |
| PATCH | Modifier partiellement | Non | `PATCH /users/1` |
| DELETE | Supprimer une ressource | Oui | `DELETE /users/1` |

### CRUD complet — exemple

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Schéma de données
class Product(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0

class ProductUpdate(BaseModel):
    """Pour PATCH : tous les champs sont optionnels"""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None

# "Base de données" en mémoire
products_db: dict[int, dict] = {
    1: {"id": 1, "name": "Pomme", "price": 0.5, "stock": 100},
    2: {"id": 2, "name": "Banane", "price": 0.3, "stock": 50},
}
next_id = 3


# GET /products/ — lister tous les produits
@app.get("/products/", tags=["products"])
def list_products():
    return list(products_db.values())


# GET /products/{id} — récupérer un produit
@app.get("/products/{product_id}", tags=["products"])
def get_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return products_db[product_id]


# POST /products/ — créer un produit
@app.post("/products/", status_code=status.HTTP_201_CREATED, tags=["products"])
def create_product(product: Product):
    global next_id
    new_product = {"id": next_id, **product.model_dump()}
    products_db[next_id] = new_product
    next_id += 1
    return new_product


# PUT /products/{id} — remplacer un produit
@app.put("/products/{product_id}", tags=["products"])
def replace_product(product_id: int, product: Product):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    updated = {"id": product_id, **product.model_dump()}
    products_db[product_id] = updated
    return updated


# PATCH /products/{id} — mise à jour partielle
@app.patch("/products/{product_id}", tags=["products"])
def update_product(product_id: int, product: ProductUpdate):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    stored = products_db[product_id]
    # Appliquer seulement les champs fournis (exclude_unset=True)
    update_data = product.model_dump(exclude_unset=True)
    stored.update(update_data)
    return stored


# DELETE /products/{id} — supprimer un produit
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["products"])
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    del products_db[product_id]
    # Retourner None avec 204 No Content
```

---

## 5. Modèles de réponse (response_model)

Le `response_model` permet de définir et valider la structure de la réponse.

### Filtrer les données sensibles

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    """Données reçues lors de la création"""
    username: str
    email: str
    password: str          # Champ sensible !
    full_name: str | None = None

class UserOut(BaseModel):
    """Données renvoyées — sans le mot de passe"""
    username: str
    email: str
    full_name: str | None = None

@app.post(
    "/users/",
    response_model=UserOut,      # Le mot de passe sera filtré
    status_code=201
)
def create_user(user: UserIn):
    # Même si on retourne l'objet complet (avec password),
    # FastAPI ne renverra que les champs de UserOut
    return user  # password sera automatiquement exclu de la réponse
```

### response_model_exclude_unset

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []

@app.get(
    "/items/{item_id}",
    response_model=Item,
    response_model_exclude_unset=True,  # N'inclure que les champs définis
)
def get_item(item_id: int):
    items = {
        1: {"name": "Pomme"},           # Seulement name
        2: {"name": "Banane", "price": 0.3},  # name + price
    }
    return items.get(item_id, {})

# GET /items/1 → {"name": "Pomme"}
# GET /items/2 → {"name": "Banane", "price": 0.3}
# (pas de description, tax, tags dans la réponse)
```

### Réponse avec liste

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str

@app.get("/items/", response_model=list[Item])
def list_items():
    return [
        {"id": 1, "name": "Pomme", "extra": "ce champ sera filtré"},
        {"id": 2, "name": "Banane"},
    ]
```

### Unions de types de réponse

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union

app = FastAPI()

class Cat(BaseModel):
    pet_type: str = "cat"
    name: str

class Dog(BaseModel):
    pet_type: str = "dog"
    name: str
    breed: str

@app.get("/pets/{pet_id}", response_model=Union[Cat, Dog])
def get_pet(pet_id: int):
    if pet_id == 1:
        return Cat(name="Whiskers")
    return Dog(name="Rex", breed="Labrador")
```

---

## 6. Paramètres mixtes

Dans la vraie vie, on combine souvent path, query et body.

```python
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

class ItemUpdate(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.patch("/shops/{shop_id}/items/{item_id}")
def update_shop_item(
    # Path parameters avec validation
    shop_id: Annotated[int, Path(title="ID de la boutique", ge=1)],
    item_id: Annotated[int, Path(title="ID de l'item", ge=1)],

    # Query parameters
    notify_owner: bool = False,
    reason: Annotated[str | None, Query(max_length=200)] = None,

    # Request body
    item: ItemUpdate,
):
    return {
        "shop_id": shop_id,
        "item_id": item_id,
        "item": item,
        "notify_owner": notify_owner,
        "reason": reason,
    }
```

**Règle pour distinguer path / query / body :**
- Si c'est dans `{}` dans l'URL → path parameter
- Si c'est un type simple (int, str, bool...) sans `{}` dans l'URL → query parameter
- Si c'est un modèle Pydantic → request body

---

## 7. APIRouter — organiser les routes

Quand l'application grandit, on utilise `APIRouter` pour séparer les routes dans des fichiers.

### Structure de fichiers

```
app/
├── main.py
└── routers/
    ├── __init__.py
    ├── products.py
    └── users.py
```

```python
# app/routers/products.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/products",     # Préfixe ajouté à toutes les routes
    tags=["Products"],      # Tag Swagger pour toutes les routes
    responses={
        404: {"description": "Produit introuvable"},
        500: {"description": "Erreur serveur"},
    }
)

class Product(BaseModel):
    name: str
    price: float

fake_products = {1: {"id": 1, "name": "Test", "price": 9.99}}

@router.get("/")
def list_products():
    return list(fake_products.values())

@router.get("/{product_id}")
def get_product(product_id: int):
    if product_id not in fake_products:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return fake_products[product_id]

@router.post("/", status_code=201)
def create_product(product: Product):
    new_id = max(fake_products.keys()) + 1
    fake_products[new_id] = {"id": new_id, **product.model_dump()}
    return fake_products[new_id]
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import products, users

app = FastAPI(title="Mon API")

app.include_router(products.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "API opérationnelle"}

# Résultat :
# GET /         → root()
# GET /products/ → list_products() dans products.py
# GET /users/    → list_users() dans users.py
```

---

## 8. Gestion des erreurs

### Gestionnaire d'exceptions global

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Handler pour les erreurs de validation Pydantic (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Erreur de validation sur {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Données invalides",
            "errors": exc.errors(),
            "body": exc.body,
        }
    )

# Handler pour les HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
        }
    )

# Handler global pour toutes les erreurs non gérées
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erreur non gérée sur {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"},
    )
```

### Exceptions personnalisées

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Définir une exception personnalisée
class InsufficientStockException(Exception):
    def __init__(self, product_id: int, requested: int, available: int):
        self.product_id = product_id
        self.requested = requested
        self.available = available

# Enregistrer un handler
@app.exception_handler(InsufficientStockException)
async def stock_exception_handler(request: Request, exc: InsufficientStockException):
    return JSONResponse(
        status_code=409,  # Conflict
        content={
            "detail": "Stock insuffisant",
            "product_id": exc.product_id,
            "requested": exc.requested,
            "available": exc.available,
        }
    )

@app.post("/orders/")
def create_order(product_id: int, quantity: int):
    stock = {1: 5, 2: 0}  # Simulation

    available = stock.get(product_id, 0)
    if quantity > available:
        raise InsufficientStockException(
            product_id=product_id,
            requested=quantity,
            available=available,
        )

    return {"order": "créée", "product_id": product_id, "quantity": quantity}
```

---

## Récapitulatif

| Concept | Syntaxe | Exemple |
|---|---|---|
| Path parameter | `{name}` dans l'URL + arg typé | `GET /items/{item_id}` |
| Query parameter | Arg simple avec défaut | `skip: int = 0` |
| Request body | Arg de type BaseModel | `item: Item` |
| Query validé | `Query(min_length=3)` | `q: Annotated[str, Query(min_length=3)]` |
| Path validé | `Path(ge=1)` | `id: Annotated[int, Path(ge=1)]` |
| Response model | `response_model=Model` | `@app.get(..., response_model=ItemOut)` |
| APIRouter | Séparer les routes | `router = APIRouter(prefix="/items")` |

---

**Précédent** : [Module 02 — Premiers pas](./02-premiers-pas.md)
**Suite** : [Module 04 — Pydantic et validation](./04-pydantic-validation.md)
