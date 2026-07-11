# Module 05 — Bases de données avec SQLAlchemy

## Sommaire
1. [Introduction : SQLAlchemy et FastAPI](#1-introduction--sqlalchemy-et-fastapi)
2. [Configuration de la connexion](#2-configuration-de-la-connexion)
3. [Définir les modèles SQLAlchemy](#3-définir-les-modèles-sqlalchemy)
4. [Injection de dépendances pour la DB](#4-injection-de-dépendances-pour-la-db)
5. [CRUD complet avec SQLAlchemy](#5-crud-complet-avec-sqlalchemy)
6. [Migrations avec Alembic](#6-migrations-avec-alembic)
7. [SQLAlchemy async (asyncpg)](#7-sqlalchemy-async-asyncpg)
8. [Relations entre tables](#8-relations-entre-tables)
9. [Bonnes pratiques](#9-bonnes-pratiques)

---

## 1. Introduction : SQLAlchemy et FastAPI

### Pourquoi SQLAlchemy ?

SQLAlchemy est l'ORM (Object-Relational Mapper) le plus populaire en Python. Il permet de :
- Définir les tables comme des classes Python
- Écrire des requêtes SQL en Python (sans écrire du SQL brut)
- Gérer les connexions et les transactions
- Supporter PostgreSQL, MySQL, SQLite, Oracle...

### Installation

```bash
# SQLAlchemy + driver PostgreSQL async
pip install sqlalchemy asyncpg

# SQLAlchemy + driver PostgreSQL sync (plus simple pour débuter)
pip install sqlalchemy psycopg2-binary

# Pour les migrations
pip install alembic

# Tout d'un coup
pip install sqlalchemy asyncpg psycopg2-binary alembic
```

### Architecture dans FastAPI

```
FastAPI Route
    ↓ (appelle)
Fonction handler
    ↓ (utilise via injection)
Session SQLAlchemy
    ↓ (communique avec)
Base de données PostgreSQL
```

---

## 2. Configuration de la connexion

### Variables d'environnement

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Ou pour le mode async
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb

# Pour les tests (SQLite en mémoire)
TEST_DATABASE_URL=sqlite:///./test.db
```

### Fichier `app/database.py`

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de connexion
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/mydb")

# Créer le moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Nombre de connexions dans le pool
    max_overflow=20,       # Connexions supplémentaires si pool plein
    pool_pre_ping=True,    # Tester les connexions avant utilisation
    echo=False,            # True pour afficher le SQL généré (debug)
)

# Factory de sessions
SessionLocal = sessionmaker(
    autocommit=False,   # Pas de commit automatique
    autoflush=False,    # Pas de flush automatique
    bind=engine,
)

# Classe de base pour les modèles
Base = declarative_base()
```

### Configuration avec Pydantic Settings (recommandé)

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Base de données
    database_url: str = "postgresql://postgres:password@localhost/mydb"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False  # True en dev pour voir le SQL

    # Application
    app_name: str = "Mon API FastAPI"
    debug: bool = False
    secret_key: str = "changeme-in-production"

# Singleton (instancié une seule fois)
settings = Settings()
```

```python
# app/database.py (version avec Settings)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    echo=settings.db_echo,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal montrant le démarrage de PostgreSQL avec Docker et la connexion réussie
> **Expliquer :** Lancer `docker run -e POSTGRES_PASSWORD=password -p 5432:5432 postgres`. Montrer que le conteneur démarre. Puis lancer l'application FastAPI et montrer dans les logs qu'elle se connecte à PostgreSQL. Si `db_echo=True`, montrer les requêtes SQL générées dans le terminal.

---

## 3. Définir les modèles SQLAlchemy

### Modèle de base

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"  # Nom de la table SQL

    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)

    # Champs texte
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(50), unique=True, nullable=True)

    # Champs numériques
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)

    # Booléen
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps automatiques
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r}>"
```

### Modèle utilisateur

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation vers les commandes (définie plus bas)
    orders = relationship("Order", back_populates="user")
```

### Initialiser les tables

```python
# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
import app.models.product  # Importer pour que SQLAlchemy connaisse le modèle
import app.models.user

app = FastAPI()

# Créer toutes les tables au démarrage
# (En production, utiliser Alembic à la place)
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
```

---

## 4. Injection de dépendances pour la DB

L'injection de dépendances de FastAPI permet de gérer proprement le cycle de vie de la session base de données.

### La dépendance `get_db`

```python
# app/database.py (ajout de la dépendance)
from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI qui fournit une session SQLAlchemy.

    - Ouvre une session au début de la requête
    - La ferme automatiquement à la fin (même en cas d'erreur)
    """
    db = SessionLocal()
    try:
        yield db       # La session est disponible dans le handler
    finally:
        db.close()     # Toujours fermer, même si une exception a été levée
```

### Utilisation dans les routes

```python
# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.product import Product as ProductModel
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

# Type alias pour simplifier les signatures
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[ProductPublic])
def list_products(
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
):
    query = db.query(ProductModel)
    if active_only:
        query = query.filter(ProductModel.is_active == True)
    return query.offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, db: DBSession):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product


@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: DBSession):
    # Vérifier si le SKU existe déjà
    if product_data.sku:
        existing = db.query(ProductModel).filter(
            ProductModel.sku == product_data.sku
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un produit avec le SKU '{product_data.sku}' existe déjà"
            )

    # Créer l'objet SQLAlchemy
    db_product = ProductModel(**product_data.model_dump())

    # Ajouter à la session et sauvegarder
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Recharger depuis la DB pour avoir l'ID et les defaults

    return db_product


@router.put("/{product_id}", response_model=ProductPublic)
def update_product(product_id: int, product_data: ProductCreate, db: DBSession):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    for field, value in product_data.model_dump().items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductPublic)
def partial_update_product(product_id: int, product_data: ProductUpdate, db: DBSession):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    # N'appliquer que les champs fournis
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DBSession):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    db.delete(product)
    db.commit()
```

---

## 5. CRUD complet avec SQLAlchemy

### Couche CRUD (Repository Pattern)

Pour séparer la logique DB du routeur, on peut créer une couche CRUD :

```python
# app/crud/product.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(Product.sku == sku).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    active_only: bool = True,
) -> list[Product]:
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == True)

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        )

    return query.order_by(Product.name).offset(skip).limit(limit).all()


def count_products(db: Session, active_only: bool = True) -> int:
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.count()


def create_product(db: Session, product_data: ProductCreate) -> Product:
    db_product = Product(**product_data.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product: Product, update_data: ProductUpdate) -> Product:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def deactivate_product(db: Session, product: Product) -> Product:
    """Soft delete : désactiver plutôt que supprimer."""
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product
```

```python
# app/routers/products.py — version simplifiée avec la couche CRUD
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.crud import product as crud_product
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[ProductPublic])
def list_products(
    db: DBSession,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    active_only: bool = True,
):
    products = crud_product.get_products(db, skip, limit, search, active_only)
    return products


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, db: DBSession):
    product = crud_product.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product


@router.post("/", response_model=ProductPublic, status_code=201)
def create_product(product_data: ProductCreate, db: DBSession):
    if product_data.sku:
        if crud_product.get_product_by_sku(db, product_data.sku):
            raise HTTPException(status_code=409, detail="SKU déjà utilisé")
    return crud_product.create_product(db, product_data)
```

---

## 6. Migrations avec Alembic

Alembic est le standard pour gérer les migrations de schéma de base de données avec SQLAlchemy.

### Initialiser Alembic

```bash
# Initialiser Alembic dans le projet
alembic init alembic

# Structure créée :
# alembic/
# ├── env.py          ← Configuration de l'environnement
# ├── script.py.mako  ← Template des fichiers de migration
# └── versions/       ← Fichiers de migration générés
# alembic.ini         ← Configuration principale
```

### Configurer `alembic/env.py`

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Importer tous les modèles pour qu'Alembic les connaisse
from app.database import Base
from app.config import settings
import app.models.product  # Noqa: F401
import app.models.user     # Noqa: F401

config = context.config

# Lire la configuration du logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées de nos modèles
target_metadata = Base.metadata

# URL de la base de données depuis nos settings
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Créer et appliquer des migrations

```bash
# Générer une migration automatique (compare modèles vs DB)
alembic revision --autogenerate -m "create products and users tables"

# Vérifier la migration générée avant de l'appliquer
cat alembic/versions/xxxx_create_products_and_users_tables.py

# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer une migration spécifique
alembic upgrade +1   # Une migration de plus

# Revenir en arrière
alembic downgrade -1    # Une migration en arrière
alembic downgrade base  # Revenir à l'état initial

# Voir l'état actuel
alembic current

# Voir l'historique
alembic history --verbose
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant la création et l'application d'une migration Alembic
> **Expliquer :** Montrer `alembic revision --autogenerate -m "create tables"`. Ouvrir le fichier de migration généré dans `alembic/versions/` et expliquer ce qu'il contient (`upgrade()` et `downgrade()`). Ensuite, lancer `alembic upgrade head` et montrer le message de succès. Enfin, se connecter à psql pour montrer que la table a bien été créée.

---

## 7. SQLAlchemy async (asyncpg)

Pour les applications haute performance, on peut utiliser SQLAlchemy en mode async.

### Configuration async

```python
# app/database_async.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# URL doit commencer par postgresql+asyncpg://
ASYNC_DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Moteur async
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

# Session async
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass


async def get_async_db():
    """Dépendance FastAPI pour session async."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Routes async

```python
# app/routers/products_async.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.database_async import get_async_db
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])
AsyncDB = Annotated[AsyncSession, Depends(get_async_db)]


@router.get("/")
async def list_products(db: AsyncDB, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncDB):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product


@router.post("/", status_code=201)
async def create_product(product_data: dict, db: AsyncDB):
    db_product = Product(**product_data)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product
```

---

## 8. Relations entre tables

### One-to-Many (un à plusieurs)

```python
# app/models/order.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relations
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
```

### Many-to-Many (plusieurs à plusieurs)

```python
# app/models/associations.py
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# Table d'association (sans classe dédiée si elle n'a pas de colonnes supplémentaires)
product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


# Ajouter la relation dans Product
class Product(Base):
    # ... autres colonnes ...
    categories = relationship("Category", secondary=product_category, back_populates="products")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    products = relationship("Product", secondary=product_category, back_populates="categories")
```

### Requêtes avec jointures

```python
from sqlalchemy.orm import joinedload, selectinload, Session

def get_orders_with_items(db: Session, user_id: int):
    """Récupérer les commandes d'un utilisateur avec leurs items (eager loading)."""
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product)
        )
        .order_by(Order.created_at.desc())
        .all()
    )
```

---

## 9. Bonnes pratiques

### Transactions et rollback

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException

def transfer_stock(db: Session, from_product_id: int, to_product_id: int, quantity: int):
    """Transférer du stock d'un produit à un autre (opération atomique)."""
    try:
        # Tout ou rien : si une opération échoue, tout est annulé
        from_product = db.query(Product).filter(Product.id == from_product_id).with_for_update().first()
        to_product = db.query(Product).filter(Product.id == to_product_id).with_for_update().first()

        if not from_product or not to_product:
            raise HTTPException(status_code=404, detail="Produit introuvable")

        if from_product.stock < quantity:
            raise HTTPException(status_code=409, detail="Stock insuffisant")

        from_product.stock -= quantity
        to_product.stock += quantity

        db.commit()
        return {"transferred": quantity}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Index pour les performances

```python
from sqlalchemy import Column, Integer, String, Index
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True)
    category = Column(String(50))

    # Index composite pour les recherches fréquentes
    __table_args__ = (
        Index("idx_product_category_active", "category", "is_active"),
        Index("idx_product_name_search", "name"),  # Pour les LIKE
    )
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `Base = DeclarativeBase()` | Classe de base pour les modèles SQLAlchemy |
| `Column(Type, ...)` | Définir une colonne |
| `ForeignKey("table.col")` | Clé étrangère |
| `relationship(...)` | Relation entre modèles |
| `get_db()` | Dépendance FastAPI pour la session |
| `db.add()` + `db.commit()` | Insérer |
| `db.query(Model).filter(...)` | Requêter |
| `db.commit()` + `db.refresh()` | Sauvegarder et recharger |
| `alembic revision --autogenerate` | Créer une migration |
| `alembic upgrade head` | Appliquer les migrations |

---

**Précédent** : [Module 04 — Pydantic et validation](./04-pydantic-validation.md)
**Suite** : [Module 06 — Authentification](./06-authentification.md)
