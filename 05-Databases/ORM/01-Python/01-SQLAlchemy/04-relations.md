# SQLAlchemy — Relations entre modèles

## One-to-Many (1 → N)

La relation la plus courante : un utilisateur a plusieurs commandes, une catégorie a plusieurs produits.

```python
from sqlalchemy import create_engine, String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, Session
)
from typing import List, Optional
from decimal import Decimal

engine = create_engine("postgresql+psycopg2://formation:formation@localhost/orm_db", echo=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)

    # Côté "un" : liste de commandes
    # List[Commande] → 1 user a N commandes
    commandes: Mapped[List["Commande"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"  # Si on supprime le user, ses commandes sont supprimées
    )

    def __repr__(self) -> str:
        return f"<User {self.name!r}>"

class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    statut: Mapped[str] = mapped_column(String(50), default="en_attente")

    # Côté "N" : clé étrangère
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relation inverse : commande → user
    user: Mapped["User"] = relationship(back_populates="commandes")

    def __repr__(self) -> str:
        return f"<Commande id={self.id} total={self.total}>"

Base.metadata.create_all(engine)
```

### Utiliser la relation

```python
with Session(engine) as session:
    # Créer un user avec des commandes
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.flush()  # Pour avoir l'id du user

    commande1 = Commande(total=Decimal("89.99"), user_id=user.id)
    commande2 = Commande(total=Decimal("149.00"), user_id=user.id)
    session.add_all([commande1, commande2])
    session.commit()

    # Accéder aux commandes d'un user (lazy loading par défaut)
    user = session.get(User, user.id)
    print(f"Commandes de {user.name}: {user.commandes}")

    # Accéder au user d'une commande
    commande = session.get(Commande, commande1.id)
    print(f"Commande passée par: {commande.user.name}")

    # Ajouter une commande via la relation
    user.commandes.append(Commande(total=Decimal("55.00")))
    session.commit()
```

## Many-to-Many (N → N)

Un produit peut appartenir à plusieurs catégories, une catégorie peut contenir plusieurs produits.

```python
from sqlalchemy import Table, Column

# Table d'association (pivot) — pas de classe Python, juste une Table
produit_categorie = Table(
    "produit_categorie",  # Nom de la table pivot
    Base.metadata,
    Column("produit_id", ForeignKey("produits.id"), primary_key=True),
    Column("categorie_id", ForeignKey("categories.id"), primary_key=True),
)

class Categorie(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True)

    produits: Mapped[List["Produit"]] = relationship(
        secondary=produit_categorie,
        back_populates="categories"
    )

class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    categories: Mapped[List["Categorie"]] = relationship(
        secondary=produit_categorie,
        back_populates="produits"
    )

Base.metadata.create_all(engine)
```

### Utiliser la relation N-to-N

```python
with Session(engine) as session:
    cat_info = Categorie(nom="Informatique")
    cat_bureau = Categorie(nom="Bureau")
    session.add_all([cat_info, cat_bureau])

    produit = Produit(nom="Clavier mécanique", prix=Decimal("89.99"))
    produit.categories = [cat_info, cat_bureau]  # Appartient aux deux catégories
    session.add(produit)
    session.commit()

    # Lire les catégories d'un produit
    p = session.get(Produit, produit.id)
    print(f"{p.nom} appartient à: {[c.nom for c in p.categories]}")

    # Lire les produits d'une catégorie
    cat = session.get(Categorie, cat_info.id)
    print(f"Produits dans {cat.nom}: {[p.nom for p in cat.produits]}")
```

## Many-to-Many avec données sur la table pivot

Quand la table pivot contient des données (ex: quantité dans une ligne de commande).

```python
class LigneCommande(Base):
    """Table d'association enrichie avec des données."""
    __tablename__ = "lignes_commande"

    commande_id: Mapped[int] = mapped_column(ForeignKey("commandes.id"), primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"), primary_key=True)
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    prix_unitaire: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # Prix au moment de l'achat

    # Relations vers les deux côtés
    commande: Mapped["Commande"] = relationship(back_populates="lignes")
    produit: Mapped["Produit"] = relationship(back_populates="lignes_commande")

# Mise à jour des classes
class Commande(Base):
    __tablename__ = "commandes"
    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="commandes")
    lignes: Mapped[List["LigneCommande"]] = relationship(back_populates="commande")

class Produit(Base):
    __tablename__ = "produits"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    lignes_commande: Mapped[List["LigneCommande"]] = relationship(back_populates="produit")
```

## One-to-One (1 → 1)

Un user a exactement un profil.

```python
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str | None] = mapped_column(String(500))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    # ForeignKey avec unique=True → One-to-One
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    # Relation vers User
    user: Mapped["User"] = relationship(back_populates="profile")

# Mettre à jour User
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)

    # Optional car le profil peut ne pas exister
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        uselist=False,   # uselist=False → One-to-One (pas une liste)
        cascade="all, delete-orphan"
    )
    commandes: Mapped[List["Commande"]] = relationship(back_populates="user")
```

## Lazy Loading vs Eager Loading

### Lazy Loading (par défaut) — le problème N+1

```python
with Session(engine) as session:
    users = session.scalars(select(User)).all()

    # PROBLÈME N+1 : pour chaque user, une requête SQL supplémentaire pour charger ses commandes
    for user in users:
        print(f"{user.name}: {len(user.commandes)} commandes")
        # → 1 requête pour les users + N requêtes pour les commandes (une par user)
```

### Eager Loading — solution au N+1

```python
from sqlalchemy.orm import selectinload, joinedload

with Session(engine) as session:
    # selectinload — charge les relations avec une 2ème requête SQL (IN clause)
    # Recommandé pour les collections (1→N, N→N)
    stmt = select(User).options(selectinload(User.commandes))
    users = session.scalars(stmt).all()
    # → 2 requêtes seulement : SELECT users, puis SELECT commandes WHERE user_id IN (1,2,3...)

    for user in users:
        print(f"{user.name}: {len(user.commandes)} commandes")  # Pas de requête supplémentaire

    # joinedload — charge avec un JOIN SQL
    # Recommandé pour les relations *→1 (commande → user)
    stmt = select(Commande).options(joinedload(Commande.user))
    commandes = session.scalars(stmt).all()
    # → 1 seule requête avec JOIN

    for c in commandes:
        print(f"Commande {c.id} de {c.user.name}")

    # Charger plusieurs niveaux de relations
    stmt = (
        select(User)
        .options(
            selectinload(User.commandes).selectinload(Commande.lignes)
        )
    )
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — montrer le problème N+1 avec `echo=True` (compter les requêtes) puis la solution avec `selectinload` (2 requêtes)
> **Expliquer :** Mettre `echo=True` sur l'engine, insérer 5 users avec 3 commandes chacun, puis exécuter la boucle sans et avec `selectinload`. Compter les requêtes dans le terminal. C'est la démonstration la plus concrète du problème N+1. Insister : en production avec 1000 users, cela génère 1001 requêtes.

---

## Requêtes avec JOIN explicite

```python
from sqlalchemy import select, join

with Session(engine) as session:
    # JOIN implicite via la relation
    stmt = (
        select(Commande)
        .join(Commande.user)
        .where(User.email.like("%@example.com"))
    )
    commandes = session.scalars(stmt).all()

    # JOIN explicite avec colonnes des deux tables
    stmt = (
        select(
            User.name,
            User.email,
            func.count(Commande.id).label("nb_commandes"),
            func.sum(Commande.total).label("total_achats")
        )
        .join(Commande, Commande.user_id == User.id)
        .group_by(User.id, User.name, User.email)
        .order_by(func.sum(Commande.total).desc())
    )
    for row in session.execute(stmt):
        print(f"{row.name} ({row.email}): {row.nb_commandes} commandes, {row.total_achats}€")

    # LEFT JOIN (inclut les users sans commandes)
    from sqlalchemy import outerjoin
    stmt = (
        select(User.name, func.count(Commande.id).label("nb"))
        .outerjoin(Commande, Commande.user_id == User.id)
        .group_by(User.id)
    )
```

## Cascade et suppression

```python
with Session(engine) as session:
    # Avec cascade="all, delete-orphan" sur User.commandes :
    # Supprimer un user supprime automatiquement ses commandes
    user = session.get(User, 1)
    session.delete(user)
    session.commit()
    # → DELETE FROM commandes WHERE user_id = 1
    # → DELETE FROM users WHERE id = 1

    # Retirer un élément d'une relation (avec delete-orphan)
    user = session.get(User, 2)
    commande_a_retirer = user.commandes[0]
    user.commandes.remove(commande_a_retirer)
    session.commit()
    # → DELETE FROM commandes WHERE id = ?  (car delete-orphan)
```
