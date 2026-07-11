# Module 04 — Pydantic et validation des données

## Sommaire
1. [Introduction à Pydantic v2](#1-introduction-à-pydantic-v2)
2. [Les modèles de base](#2-les-modèles-de-base)
3. [Types de champs et contraintes](#3-types-de-champs-et-contraintes)
4. [Modèles imbriqués](#4-modèles-imbriqués)
5. [Validateurs personnalisés](#5-validateurs-personnalisés)
6. [Configuration des modèles](#6-configuration-des-modèles)
7. [Sérialisation et désérialisation](#7-sérialisation-et-désérialisation)
8. [Modèles pour la base de données (patterns)](#8-modèles-pour-la-base-de-données-patterns)
9. [Gestion des erreurs Pydantic](#9-gestion-des-erreurs-pydantic)

---

## 1. Introduction à Pydantic v2

Pydantic est la bibliothèque de validation de données utilisée par FastAPI. La version 2 (sortie en 2023) est écrite en Rust et est **5 à 50 fois plus rapide** que la v1.

### Rôle de Pydantic

1. **Validation** : vérifier que les données respectent le schéma
2. **Conversion** : convertir les types (ex: `"42"` → `42`)
3. **Sérialisation** : convertir les modèles en dict/JSON
4. **Documentation** : générer le schéma JSON Schema (utilisé par FastAPI pour Swagger)

### Pourquoi Pydantic avec FastAPI ?

Sans Pydantic, vous devriez écrire manuellement :
```python
# Sans Pydantic — ce que vous devriez faire
def create_user(data: dict):
    if "name" not in data:
        raise ValueError("name est requis")
    if not isinstance(data["name"], str):
        raise ValueError("name doit être une string")
    if len(data["name"]) < 2:
        raise ValueError("name doit avoir au moins 2 caractères")
    if "email" not in data:
        raise ValueError("email est requis")
    # ... 50 lignes de validation de plus...
```

Avec Pydantic :
```python
# Avec Pydantic — tout est automatique
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
```

---

## 2. Les modèles de base

### Déclaration d'un modèle

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    id: int
    name: str
    description: str | None = None   # Optionnel, défaut None
    price: float
    tax: float = 0.0                  # Optionnel, défaut 0.0
    is_available: bool = True
    created_at: datetime = None       # Peut être None
    tags: list[str] = []              # Liste vide par défaut
```

### Instanciation et validation

```python
# Créer depuis un dict (typique dans une API)
data = {
    "id": 1,
    "name": "Marteau",
    "price": "29.99",    # String → sera converti en float automatiquement
    "tags": ["outil", "bricolage"]
}
product = Product(**data)

print(product.id)          # 1 (int)
print(product.price)       # 29.99 (float, pas "29.99")
print(product.description) # None
print(product.is_available) # True (valeur par défaut)

# Accès comme un objet Python normal
print(product.name.upper())  # MARTEAU

# Convertir en dict
product_dict = product.model_dump()
# {'id': 1, 'name': 'Marteau', 'description': None, 'price': 29.99, ...}

# Convertir en JSON
product_json = product.model_dump_json()
# '{"id":1,"name":"Marteau","description":null,"price":29.99,...}'
```

### Erreurs de validation

```python
from pydantic import BaseModel, ValidationError

class Product(BaseModel):
    name: str
    price: float

# Données invalides
try:
    product = Product(name="Test", price="pas_un_nombre")
except ValidationError as e:
    print(e.json())
    # [{"type": "float_parsing", "loc": ["price"], "msg": "Input should be a valid number..."}]
    print(e.error_count())  # 1 erreur
    print(e.errors())       # Liste des erreurs détaillées
```

---

## 3. Types de champs et contraintes

### `Field()` pour les contraintes

```python
from pydantic import BaseModel, Field
from datetime import datetime

class Product(BaseModel):
    # Contraintes sur les strings
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Nom du produit",
        examples=["Marteau", "Tournevis"],
    )

    # Contraintes sur les nombres
    price: float = Field(
        gt=0,          # greater than : > 0
        le=10000,      # less or equal : <= 10000
        description="Prix en euros (HT)",
    )

    stock: int = Field(
        ge=0,          # greater or equal : >= 0
        default=0,
    )

    # Contrainte regex sur string
    sku: str = Field(
        pattern=r"^[A-Z]{3}-\d{4}$",  # Ex: ABC-1234
        description="Code article (format: ABC-1234)",
    )

    # Valeur par défaut via factory (pour les types mutables)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
```

### Types spéciaux Pydantic

```python
from pydantic import BaseModel, EmailStr, HttpUrl, AnyUrl, IPvAnyAddress
from pydantic import constr, confloat, conint
from uuid import UUID

class UserProfile(BaseModel):
    # Email validé
    email: EmailStr

    # URL validée
    website: HttpUrl | None = None

    # UUID
    user_id: UUID

    # Adresse IP (v4 ou v6)
    last_ip: IPvAnyAddress | None = None

class ItemStrict(BaseModel):
    # Équivalents de Field() avec types contraints
    name: constr(min_length=2, max_length=50)   # str contraint
    price: confloat(gt=0, le=10000)             # float contraint
    stock: conint(ge=0)                          # int contraint
```

### Types Python courants

```python
from pydantic import BaseModel
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID
from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

class ComplexModel(BaseModel):
    # Dates et heures
    birth_date: date
    created_at: datetime
    opening_time: time
    duration: timedelta

    # Précision financière
    price: Decimal

    # Chemin fichier
    config_file: Path | None = None

    # Identifiant unique
    uuid: UUID

    # Enum
    status: StatusEnum = StatusEnum.active

    # Dict
    metadata: dict[str, str] = {}

    # Tuple
    coordinates: tuple[float, float] | None = None

    # Ensemble
    permissions: set[str] = set()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal Python interactif montrant la validation Pydantic
> **Expliquer :** Ouvrir un REPL Python. Importer BaseModel et Field. Créer un modèle simple avec des contraintes. Montrer la création d'une instance valide. Puis montrer une instance invalide et le message d'erreur détaillé retourné. Insister sur le fait que FastAPI utilise exactement ces erreurs pour générer les 422.

---

## 4. Modèles imbriqués

### Imbrication simple

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    postal_code: str
    country: str = "France"

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: Address         # Modèle imbriqué
    created_at: datetime = None

# Création avec dict imbriqué
user_data = {
    "id": 1,
    "name": "Alice Dupont",
    "email": "alice@example.com",
    "address": {
        "street": "12 rue des Lilas",
        "city": "Paris",
        "postal_code": "75011",
    }
}

user = User(**user_data)
print(user.address.city)  # "Paris"
print(user.address.country)  # "France" (défaut)
```

### Listes de modèles imbriqués

```python
from pydantic import BaseModel

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

class Order(BaseModel):
    id: int
    customer_name: str
    items: list[OrderItem]
    shipping_address: str

    @property
    def total_amount(self) -> float:
        return sum(item.total for item in self.items)

# Utilisation
order_data = {
    "id": 100,
    "customer_name": "Bob Martin",
    "items": [
        {"product_id": 1, "quantity": 2, "unit_price": 9.99},
        {"product_id": 3, "quantity": 1, "unit_price": 24.99},
    ],
    "shipping_address": "5 rue de la Paix, Lyon"
}

order = Order(**order_data)
print(order.total_amount)  # 44.97
print(order.items[0].total)  # 19.98
```

### Modèles auto-référencés (récursifs)

```python
from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    id: int
    name: str
    parent: Optional["Category"] = None   # Référence circulaire
    children: list["Category"] = []

# Résoudre les références forward
Category.model_rebuild()

# Exemple d'utilisation
electronics = Category(
    id=1,
    name="Électronique",
    children=[
        Category(id=2, name="Smartphones"),
        Category(id=3, name="Ordinateurs"),
    ]
)
```

---

## 5. Validateurs personnalisés

### `@field_validator` — validation d'un champ

```python
from pydantic import BaseModel, field_validator, ValidationInfo
import re

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    age: int

    @field_validator("username")
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", v):
            raise ValueError(
                "Le nom d'utilisateur doit contenir 3-20 caractères "
                "alphanumériques ou underscores"
            )
        return v.lower()  # On peut aussi transformer la valeur

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Le mot de passe doit avoir au moins 8 caractères")
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v: int) -> int:
        if v < 18:
            raise ValueError("Vous devez avoir au moins 18 ans")
        if v > 120:
            raise ValueError("Âge invalide")
        return v
```

### `@model_validator` — validation inter-champs

```python
from pydantic import BaseModel, model_validator
from datetime import date

class Event(BaseModel):
    title: str
    start_date: date
    end_date: date
    max_participants: int
    min_participants: int = 1

    @model_validator(mode="after")
    def validate_dates_and_participants(self) -> "Event":
        # Valider que la date de fin est après la date de début
        if self.end_date < self.start_date:
            raise ValueError(
                f"La date de fin ({self.end_date}) doit être "
                f"après la date de début ({self.start_date})"
            )

        # Valider que min <= max
        if self.min_participants > self.max_participants:
            raise ValueError(
                "Le nombre minimum de participants ne peut pas "
                "dépasser le maximum"
            )

        return self

class PasswordConfirmation(BaseModel):
    password: str
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordConfirmation":
        if self.password != self.password_confirm:
            raise ValueError("Les mots de passe ne correspondent pas")
        return self
```

### Validators `mode="before"` — avant la conversion de type

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float
    tags: list[str] = []

    @field_validator("name", mode="before")
    @classmethod
    def strip_and_capitalize(cls, v):
        """Nettoyer le nom avant la validation de type."""
        if isinstance(v, str):
            return v.strip().title()
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        """Accepter une string CSV en plus d'une liste."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v

# Utilisation
p = Product(name="  marteau  ", price=9.99, tags="outil, bricolage, manuel")
print(p.name)   # "Marteau" (stripped + title case)
print(p.tags)   # ["outil", "bricolage", "manuel"]
```

---

## 6. Configuration des modèles

### `model_config` — configurer le comportement

```python
from pydantic import BaseModel
from pydantic.config import ConfigDict

class StrictProduct(BaseModel):
    model_config = ConfigDict(
        # Ne pas accepter les champs inconnus (défaut: ignorer)
        extra="forbid",

        # Mode strict : ne pas convertir les types (str "42" → int interdit)
        strict=False,

        # Valider les valeurs par défaut
        validate_default=True,

        # Valider lors de l'assignation
        validate_assignment=True,

        # Alias snake_case ↔ camelCase (pour les APIs)
        populate_by_name=True,
    )

    name: str
    price: float

# extra="forbid" : champs supplémentaires refusés
try:
    p = StrictProduct(name="Test", price=9.99, unknown_field="oops")
except Exception as e:
    print(e)  # Extra inputs are not permitted
```

### Alias et camelCase

Les APIs JSON utilisent souvent camelCase, mais Python utilise snake_case.

```python
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

class ProductAPI(BaseModel):
    """Modèle avec support camelCase pour les APIs frontend."""
    model_config = ConfigDict(populate_by_name=True)

    product_id: int = Field(alias="productId")
    product_name: str = Field(alias="productName")
    unit_price: float = Field(alias="unitPrice")
    is_in_stock: bool = Field(alias="isInStock", default=True)

# Instanciation depuis JSON camelCase
data = {
    "productId": 1,
    "productName": "Marteau",
    "unitPrice": 29.99,
}
product = ProductAPI(**data)
print(product.product_id)    # 1
print(product.product_name)  # "Marteau"

# Sérialiser avec alias (pour envoyer au frontend)
print(product.model_dump(by_alias=True))
# {'productId': 1, 'productName': 'Marteau', 'unitPrice': 29.99, 'isInStock': True}
```

### Génération automatique d'alias camelCase

```python
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.alias_generators import to_camel

class OrderItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    product_id: int
    quantity: int
    unit_price: float
    discount_percent: float = 0.0

# Les champs snake_case deviennent automatiquement camelCase
item = OrderItem(productId=1, quantity=2, unitPrice=9.99)
print(item.model_dump(by_alias=True))
# {'productId': 1, 'quantity': 2, 'unitPrice': 9.99, 'discountPercent': 0.0}
```

---

## 7. Sérialisation et désérialisation

### `model_dump()` — convertir en dict

```python
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    created_at: datetime = None

user = User(id=1, name="Alice", email="alice@test.com", password="secret")

# Tout inclure
user.model_dump()
# {'id': 1, 'name': 'Alice', 'email': 'alice@test.com', 'password': 'secret', ...}

# Exclure des champs sensibles
user.model_dump(exclude={"password"})
# {'id': 1, 'name': 'Alice', 'email': 'alice@test.com', ...}

# Inclure seulement certains champs
user.model_dump(include={"id", "name"})
# {'id': 1, 'name': 'Alice'}

# Exclure les valeurs None
user.model_dump(exclude_none=True)

# Exclure les valeurs par défaut non modifiées
user.model_dump(exclude_unset=True)

# Mode round-trip : pour JSON (sérialise datetime en string)
user.model_dump(mode="json")
```

### `model_validate()` — créer depuis des données externes

```python
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

# Depuis un dict
product = Product.model_validate({"id": 1, "name": "Test", "price": 9.99})

# Depuis du JSON
product = Product.model_validate_json('{"id": 1, "name": "Test", "price": 9.99}')

# Depuis un objet SQLAlchemy (avec from_attributes=True dans la config)
```

### `model_copy()` — copier avec modifications

```python
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int = 0

product = Product(id=1, name="Marteau", price=29.99, stock=10)

# Copier avec mise à jour
updated = product.model_copy(update={"price": 24.99, "stock": 8})
print(updated.price)   # 24.99
print(product.price)   # 29.99 (inchangé, les modèles sont immutables par défaut)
```

---

## 8. Modèles pour la base de données (patterns)

Dans une vraie application FastAPI, on utilise en général 3-4 schémas Pydantic par entité.

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# --- SCHÉMAS POUR LES UTILISATEURS ---

class UserBase(BaseModel):
    """Champs communs à tous les schémas utilisateur."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    """Données pour créer un utilisateur (reçues par l'API)."""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """Données pour mettre à jour (tous les champs optionnels)."""
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None

class UserInDB(UserBase):
    """Représentation en base de données (avec hashed_password)."""
    id: int
    hashed_password: str
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}  # Pour SQLAlchemy

class UserPublic(UserBase):
    """Données renvoyées par l'API (sans mot de passe)."""
    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- UTILISATION DANS LES ROUTES ---

from fastapi import FastAPI

app = FastAPI()

@app.post("/users/", response_model=UserPublic, status_code=201)
def create_user(user_data: UserCreate):
    # 1. Recevoir UserCreate (avec password)
    # 2. Hasher le mot de passe
    # 3. Créer UserInDB en base
    # 4. Retourner UserPublic (sans password)
    pass

@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    pass

@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_data: UserUpdate):
    pass
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La Swagger UI montrant les différents schémas (UserCreate, UserPublic) dans la section "Schemas"
> **Expliquer :** Faire défiler jusqu'en bas de la page Swagger, section "Schemas". Montrer que FastAPI génère automatiquement la documentation de chaque modèle Pydantic utilisé. Montrer que UserCreate inclut le champ password alors que UserPublic ne l'a pas. Expliquer que c'est ça le principe du response_model : filtrer les données sensibles automatiquement.

---

## 9. Gestion des erreurs Pydantic

### Format des erreurs de validation

Quand la validation échoue, FastAPI retourne automatiquement un 422 avec ce format :

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab",
      "ctx": {"min_length": 3}
    },
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "pas-un-email",
      "ctx": {"reason": "An email address must have an @-sign."}
    }
  ]
}
```

### Personnaliser les messages d'erreur

```python
from pydantic import BaseModel, Field, field_validator

class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        json_schema_extra={"example": "Marteau de charpentier"},
    )
    price: float = Field(gt=0, description="Prix en euros HT")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Le nom ne peut pas être vide ou composé d'espaces")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_reasonable(cls, v: float) -> float:
        if v > 1_000_000:
            raise ValueError(
                "Prix trop élevé. Contactez un administrateur pour les articles > 1 000 000 €"
            )
        return round(v, 2)  # Arrondir à 2 décimales
```

### Capturer les erreurs de validation dans les tests

```python
from pydantic import ValidationError
import pytest

def test_product_validation():
    from myapp.schemas import ProductCreate

    # Données invalides
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(name="X", price=-5.0)

    errors = exc_info.value.errors()
    error_types = [e["type"] for e in errors]

    assert "string_too_short" in error_types  # name trop court
    assert "greater_than" in error_types       # price négatif
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `BaseModel` | Classe de base pour tous les schémas |
| `Field()` | Contraintes et métadonnées sur les champs |
| `@field_validator` | Validation personnalisée d'un champ |
| `@model_validator` | Validation inter-champs |
| `model_dump()` | Convertir en dict |
| `model_validate()` | Créer depuis un dict/JSON |
| `from_attributes=True` | Pour créer depuis des objets SQLAlchemy |
| Pattern CRUD | Base, Create, Update, InDB, Public |

---

**Précédent** : [Module 03 — Routing et paramètres](./03-routing-parametres.md)
**Suite** : [Module 05 — Bases de données](./05-bases-de-donnees.md)
