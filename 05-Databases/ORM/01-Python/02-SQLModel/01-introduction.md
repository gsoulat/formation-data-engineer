# SQLModel — Introduction et concepts de base

## Qu'est-ce que SQLModel ?

SQLModel est une couche fine au-dessus de SQLAlchemy et Pydantic. Un même modèle peut jouer le rôle de :
- **Modèle ORM** : mappé vers une table SQL
- **Schéma Pydantic** : validation des données d'entrée/sortie d'une API

```python
# Avec SQLModel : un seul modèle
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True)
    hashed_password: str
```

`table=True` indique que ce modèle doit être mappé vers une table SQL.

## Installation

```bash
pip install sqlmodel psycopg2-binary
# ou pour async
pip install sqlmodel asyncpg
```

## Modèle de base

```python
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime

# Modèle de table (ORM)
class Produit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=200, description="Nom du produit")
    description: Optional[str] = Field(default=None)
    prix: float = Field(gt=0, description="Prix en euros, doit être positif")
    stock: int = Field(default=0, ge=0)
    actif: bool = Field(default=True)

engine = create_engine("postgresql+psycopg2://formation:formation@localhost/orm_db", echo=True)

# Créer les tables
SQLModel.metadata.create_all(engine)
```

## Le pattern de modèles séparés

En pratique, on utilise plusieurs classes pour séparer les usages. C'est le pattern recommandé par SQLModel.

```python
from sqlmodel import SQLModel, Field
from typing import Optional

# 1. Classe de base — champs communs (pas de table)
class ProduitBase(SQLModel):
    nom: str = Field(max_length=200)
    description: Optional[str] = None
    prix: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    actif: bool = True

# 2. Modèle de table (BDD) — hérite de Base, ajoute id et champs BDD
class Produit(ProduitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    categorie_id: Optional[int] = Field(default=None, foreign_key="categories.id")

# 3. Schéma de création — ce que l'API reçoit (pas d'id)
class ProduitCreate(ProduitBase):
    categorie_id: Optional[int] = None

# 4. Schéma de mise à jour — tous les champs optionnels
class ProduitUpdate(SQLModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    actif: Optional[bool] = None

# 5. Schéma de réponse — ce que l'API retourne (avec id)
class ProduitPublic(ProduitBase):
    id: int
```

## CRUD avec Session

```python
from sqlmodel import Session, select

# CREATE
with Session(engine) as session:
    produit = Produit(nom="Clavier", prix=89.99, stock=15)
    session.add(produit)
    session.commit()
    session.refresh(produit)  # Recharge depuis la BDD (pour avoir l'id)
    print(f"Produit créé: id={produit.id}")

# READ — tous
with Session(engine) as session:
    stmt = select(Produit)
    produits = session.exec(stmt).all()
    for p in produits:
        print(f"{p.nom}: {p.prix}€")

# READ — avec filtre
with Session(engine) as session:
    stmt = select(Produit).where(Produit.actif == True).order_by(Produit.prix)
    produits = session.exec(stmt).all()

# READ — par id
with Session(engine) as session:
    produit = session.get(Produit, 1)
    if produit:
        print(produit.model_dump())  # Pydantic : convertit en dict

# UPDATE
with Session(engine) as session:
    produit = session.get(Produit, 1)
    if produit:
        update_data = ProduitUpdate(prix=79.99, stock=20)
        # Appliquer les champs non-None seulement
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(produit, field, value)
        session.add(produit)
        session.commit()
        session.refresh(produit)

# DELETE
with Session(engine) as session:
    produit = session.get(Produit, 1)
    if produit:
        session.delete(produit)
        session.commit()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter le CRUD complet, montrer les requêtes SQL générées et les résultats
> **Expliquer :** Montrer comment `session.refresh()` est nécessaire après `commit()` pour que SQLModel recharge les valeurs générées par la BDD (id auto-incrémenté, valeurs default serveur). Sans `refresh`, accéder à `produit.id` après commit peut nécessiter une nouvelle requête.

---

## Validation Pydantic intégrée

L'un des avantages majeurs de SQLModel : la validation se fait automatiquement.

```python
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, validator

class UserCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr  # Validation format email automatique
    age: int = Field(ge=0, le=150)
    password: str = Field(min_length=8)

    @validator("password")
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        return v

# Test
try:
    user = UserCreate(name="Al", email="pas-un-email", age=-5, password="weak")
except Exception as e:
    print(e)
    # Affiche toutes les erreurs de validation en une fois

user = UserCreate(name="Alice", email="alice@example.com", age=30, password="SecurePass1")
print(user.model_dump())
```

## Relations SQLModel

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Categorie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=100, unique=True)

    produits: List["Produit"] = Relationship(back_populates="categorie")

class Produit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(max_length=200)
    prix: float
    categorie_id: Optional[int] = Field(default=None, foreign_key="categorie.id")

    categorie: Optional[Categorie] = Relationship(back_populates="produits")

# Utilisation
with Session(engine) as session:
    cat = Categorie(nom="Informatique")
    session.add(cat)
    session.commit()
    session.refresh(cat)

    produit = Produit(nom="Clavier", prix=89.99, categorie_id=cat.id)
    session.add(produit)
    session.commit()
    session.refresh(produit)

    # Accéder à la catégorie
    p = session.get(Produit, produit.id)
    print(f"{p.nom} appartient à: {p.categorie.nom}")
```

## Différences clés SQLModel vs SQLAlchemy

| Aspect | SQLAlchemy | SQLModel |
|--------|-----------|----------|
| Déclaration modèle | `Mapped[str] = mapped_column()` | `str = Field()` |
| Validation | Aucune (juste types) | Pydantic intégré |
| Sérialisation JSON | Manuelle | `.model_dump()`, `.model_dump_json()` |
| Requête | `session.scalars(select(...))` | `session.exec(select(...))` |
| Refresh après commit | Automatique parfois | `session.refresh()` recommandé |
| FastAPI integration | Possible | Natif |
