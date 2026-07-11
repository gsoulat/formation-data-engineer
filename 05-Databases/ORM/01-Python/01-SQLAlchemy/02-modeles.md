# SQLAlchemy — Définir des modèles

## Types de colonnes disponibles

SQLAlchemy propose des types génériques (portables entre SGBD) et des types spécifiques à PostgreSQL.

### Types génériques

```python
from sqlalchemy import (
    Integer, BigInteger, SmallInteger,
    Float, Numeric, Boolean,
    String, Text, Unicode, UnicodeText,
    Date, Time, DateTime, Interval,
    LargeBinary, Enum, JSON, UUID
)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from datetime import date, time, datetime
import uuid

class ExempleTypes(Base):
    __tablename__ = "exemple_types"

    # Entiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    age: Mapped[int] = mapped_column(SmallInteger)         # -32768 à 32767
    population: Mapped[int] = mapped_column(BigInteger)

    # Décimaux
    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # 10 chiffres, 2 décimales
    score: Mapped[float] = mapped_column(Float)

    # Texte
    nom: Mapped[str] = mapped_column(String(100))          # VARCHAR(100)
    description: Mapped[str] = mapped_column(Text)          # TEXT (illimité)

    # Booléen
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    # Dates et heures
    naissance: Mapped[date] = mapped_column(Date)
    heure_ouverture: Mapped[time] = mapped_column(Time)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # UUID
    ref: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)

    # JSON (supporte dict et list)
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=True)
```

### Types PostgreSQL spécifiques

```python
from sqlalchemy.dialects.postgresql import (
    ARRAY, JSONB, INET, CIDR, UUID as PG_UUID,
    TSVECTOR, BYTEA, HSTORE
)

class ArticlePostgres(Base):
    __tablename__ = "articles_pg"

    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[list] = mapped_column(ARRAY(String))      # Array de strings
    meta: Mapped[dict] = mapped_column(JSONB)              # JSONB (indexable)
    ip_client: Mapped[str] = mapped_column(INET)           # Adresse IP
    search_vector: Mapped[str] = mapped_column(TSVECTOR)   # Full-text search
```

## Options de colonnes

```python
from sqlalchemy import String, Index, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)

    # nullable=False → NOT NULL (par défaut Mapped[str] est NOT NULL)
    nom: Mapped[str] = mapped_column(String(100))

    # Valeur optionnelle → Mapped[str | None] ou Mapped[Optional[str]]
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Valeur par défaut Python (évaluée côté Python)
    actif: Mapped[bool] = mapped_column(default=True)

    # Valeur par défaut serveur (évaluée côté SQL)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Unique
    sku: Mapped[str] = mapped_column(String(50), unique=True)

    # Index simple
    categorie: Mapped[str] = mapped_column(String(50), index=True)

    # Nom de colonne différent du nom d'attribut
    prix_ht: Mapped[Decimal] = mapped_column("price_excl_tax", Numeric(10, 2))

    # Contraintes au niveau de la table (dans __table_args__)
    __table_args__ = (
        # Index composite
        Index("idx_produit_cat_actif", "categorie", "actif"),
        # Contrainte unique composite
        UniqueConstraint("nom", "categorie", name="uq_produit_nom_cat"),
        # Contrainte CHECK
        CheckConstraint("prix_ht >= 0", name="ck_prix_positif"),
    )
```

## Clés primaires

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, UUID, func
import uuid

class AvecAutoIncrement(Base):
    __tablename__ = "auto_increment"
    # Entier auto-incrémenté (SERIAL en PostgreSQL)
    id: Mapped[int] = mapped_column(primary_key=True)

class AvecUUID(Base):
    __tablename__ = "avec_uuid"
    # UUID généré côté Python
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

class AvecUUIDServeur(Base):
    __tablename__ = "avec_uuid_serveur"
    # UUID généré côté PostgreSQL
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

class ClePrimaireComposite(Base):
    __tablename__ = "cle_composite"
    # Clé primaire sur plusieurs colonnes
    commande_id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(primary_key=True)
    quantite: Mapped[int] = mapped_column(default=1)
```

## Héritage et classe de base commune

En production, on crée souvent une classe de base qui ajoute automatiquement `id`, `created_at`, `updated_at` à tous les modèles.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import DateTime, func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """Mixin qui ajoute created_at et updated_at à tous les modèles."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class IDMixin:
    """Mixin qui ajoute un id entier auto-incrémenté."""
    id: Mapped[int] = mapped_column(primary_key=True)

class ModelBase(IDMixin, TimestampMixin, Base):
    """Base commune à tous les modèles métier."""
    __abstract__ = True  # Ne crée pas de table

# Utilisation
class User(ModelBase):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    # hérite de id, created_at, updated_at automatiquement

class Commande(ModelBase):
    __tablename__ = "commandes"
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    # hérite de id, created_at, updated_at automatiquement
```

## Exemple complet — modèle e-commerce

```python
# models_ecommerce.py
from sqlalchemy import (
    create_engine, String, Text, Numeric,
    Boolean, DateTime, Integer, func, CheckConstraint, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from decimal import Decimal
import uuid

engine = create_engine("postgresql+psycopg2://formation:formation@localhost/orm_db", echo=False)

class Base(DeclarativeBase):
    pass

class Categorie(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Categorie {self.nom!r}>"

class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    prix_ht: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    tva: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.20"))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @property
    def prix_ttc(self) -> Decimal:
        return self.prix_ht * (1 + self.tva)

    def __repr__(self) -> str:
        return f"<Produit {self.reference!r} — {self.prix_ht}€ HT>"

    __table_args__ = (
        CheckConstraint("prix_ht >= 0", name="ck_prix_positif"),
        CheckConstraint("stock >= 0", name="ck_stock_positif"),
        Index("idx_produit_actif", "actif"),
    )

Base.metadata.create_all(engine)
print("Tables créées avec succès")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal + DBeaver en parallèle — exécuter le script de création des tables, puis dans DBeaver inspecter les tables `categories` et `produits`
> **Expliquer :** Montrer dans DBeaver les colonnes créées (types, nullable, default), les contraintes (CHECK, UNIQUE), les index. Faire un clic droit → "View DDL" et comparer avec le code Python. Montrer que `Mapped[str | None]` génère bien `nullable = true` dans le DDL.

---

## Introspection — inspecter un modèle

```python
from sqlalchemy import inspect

# Inspecter les colonnes d'une table
insp = inspect(Produit)
for col in insp.columns:
    print(f"{col.name}: {col.type} | nullable={col.nullable} | pk={col.primary_key}")

# Voir les contraintes
for constraint in Produit.__table__.constraints:
    print(f"Contrainte: {constraint}")

# Voir les index
for index in Produit.__table__.indexes:
    print(f"Index: {index.name} sur {[c.name for c in index.columns]}")
```
