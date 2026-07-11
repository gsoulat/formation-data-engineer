# SQLAlchemy — Requêtes et opérations CRUD

## Setup de base

```python
from sqlalchemy import create_engine, select, update, delete, func, and_, or_, not_
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime
from decimal import Decimal
from datetime import datetime

engine = create_engine("postgresql+psycopg2://formation:formation@localhost/orm_db", echo=True)

class Base(DeclarativeBase):
    pass

class Produit(Base):
    __tablename__ = "produits"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    categorie: Mapped[str] = mapped_column(String(50))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

Base.metadata.create_all(engine)
```

## CREATE — Insérer des données

### Insérer un objet

```python
with Session(engine) as session:
    produit = Produit(nom="Clavier mécanique", prix=Decimal("89.99"), categorie="informatique", stock=15)
    session.add(produit)
    session.commit()

    # Après commit, l'id est disponible
    print(f"Produit créé avec id={produit.id}")
```

### Insérer plusieurs objets

```python
with Session(engine) as session:
    produits = [
        Produit(nom="Souris sans fil", prix=Decimal("29.99"), categorie="informatique", stock=50),
        Produit(nom="Écran 27 pouces", prix=Decimal("349.00"), categorie="informatique", stock=8),
        Produit(nom="Webcam HD", prix=Decimal("79.99"), categorie="informatique", stock=25),
        Produit(nom="Casque audio", prix=Decimal("149.00"), categorie="audio", stock=12),
        Produit(nom="Enceinte Bluetooth", prix=Decimal("99.00"), categorie="audio", stock=30),
    ]
    session.add_all(produits)
    session.commit()
    print(f"{len(produits)} produits insérés")
```

### Insertion bulk performante (SQLAlchemy Core)

Pour de gros volumes, utiliser `insert()` est beaucoup plus rapide que `add_all()`.

```python
from sqlalchemy import insert

with Session(engine) as session:
    # Insert bulk — une seule requête SQL
    session.execute(
        insert(Produit),
        [
            {"nom": f"Produit {i}", "prix": Decimal("9.99"), "categorie": "test", "stock": i}
            for i in range(1000)
        ]
    )
    session.commit()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter les insertions avec `echo=True`, montrer le SQL `INSERT INTO` généré
> **Expliquer :** Comparer le SQL généré pour `add_all()` (plusieurs INSERT séparés) vs `insert()` bulk (un seul INSERT). Montrer dans DBeaver le résultat dans la table. Insister sur la différence de performance pour les gros volumes.

---

## READ — Lire des données

### Sélectionner tous les enregistrements

```python
with Session(engine) as session:
    # Méthode recommandée SQLAlchemy 2.0
    stmt = select(Produit)
    produits = session.scalars(stmt).all()

    for p in produits:
        print(f"{p.nom} — {p.prix}€ (stock: {p.stock})")
```

### Sélectionner par clé primaire

```python
with Session(engine) as session:
    # Méthode rapide par primary key (utilise l'identity map)
    produit = session.get(Produit, 1)
    if produit:
        print(produit.nom)
    else:
        print("Produit non trouvé")
```

### Filtrer avec WHERE

```python
with Session(engine) as session:
    # Filtre simple
    stmt = select(Produit).where(Produit.categorie == "informatique")
    produits = session.scalars(stmt).all()

    # Filtre avec opérateurs de comparaison
    stmt = select(Produit).where(Produit.prix > 100)
    stmt = select(Produit).where(Produit.prix.between(50, 200))
    stmt = select(Produit).where(Produit.nom.like("%clavier%"))
    stmt = select(Produit).where(Produit.nom.ilike("%clavier%"))  # case-insensitive
    stmt = select(Produit).where(Produit.categorie.in_(["informatique", "audio"]))
    stmt = select(Produit).where(Produit.categorie.not_in(["test"]))
    stmt = select(Produit).where(Produit.description.is_(None))  # IS NULL
    stmt = select(Produit).where(Produit.description.is_not(None))  # IS NOT NULL

    # Filtre combiné avec AND (par défaut)
    stmt = select(Produit).where(
        Produit.categorie == "informatique",
        Produit.prix < 100,
        Produit.actif == True
    )

    # Filtre avec and_(), or_(), not_()
    stmt = select(Produit).where(
        and_(
            Produit.actif == True,
            or_(
                Produit.categorie == "informatique",
                Produit.prix < 50
            )
        )
    )

    produits = session.scalars(stmt).all()
```

### Tri et pagination

```python
with Session(engine) as session:
    # Tri ascendant (par défaut)
    stmt = select(Produit).order_by(Produit.prix)

    # Tri descendant
    stmt = select(Produit).order_by(Produit.prix.desc())

    # Tri multiple
    stmt = select(Produit).order_by(Produit.categorie.asc(), Produit.prix.desc())

    # Pagination
    page = 2
    taille_page = 10
    stmt = (
        select(Produit)
        .order_by(Produit.id)
        .offset((page - 1) * taille_page)
        .limit(taille_page)
    )

    produits = session.scalars(stmt).all()
    print(f"Page {page} : {len(produits)} produits")
```

### Sélectionner des colonnes spécifiques

```python
with Session(engine) as session:
    # Sélectionner des colonnes individuelles (retourne des tuples)
    stmt = select(Produit.nom, Produit.prix).where(Produit.actif == True)
    rows = session.execute(stmt).all()
    for nom, prix in rows:
        print(f"{nom}: {prix}€")

    # Sélectionner avec un alias
    from sqlalchemy import label
    stmt = select(
        Produit.nom,
        Produit.prix.label("tarif"),
        (Produit.prix * Produit.stock).label("valeur_stock")
    )
    rows = session.execute(stmt).all()
    for row in rows:
        print(f"{row.nom}: {row.tarif}€ — valeur stock: {row.valeur_stock}€")
```

### Agrégations

```python
with Session(engine) as session:
    from sqlalchemy import func

    # Compter
    count = session.scalar(select(func.count()).select_from(Produit))
    print(f"Nombre total de produits: {count}")

    # Compter avec filtre
    count_actifs = session.scalar(
        select(func.count(Produit.id)).where(Produit.actif == True)
    )

    # Min, max, avg, sum
    stmt = select(
        func.min(Produit.prix).label("prix_min"),
        func.max(Produit.prix).label("prix_max"),
        func.avg(Produit.prix).label("prix_moyen"),
        func.sum(Produit.stock).label("stock_total")
    )
    result = session.execute(stmt).one()
    print(f"Prix: min={result.prix_min} max={result.prix_max} moy={result.prix_moyen:.2f}")

    # GROUP BY
    stmt = (
        select(
            Produit.categorie,
            func.count(Produit.id).label("nb_produits"),
            func.avg(Produit.prix).label("prix_moyen")
        )
        .group_by(Produit.categorie)
        .order_by(func.count(Produit.id).desc())
    )
    for row in session.execute(stmt):
        print(f"{row.categorie}: {row.nb_produits} produits à {row.prix_moyen:.2f}€ en moyenne")

    # HAVING
    stmt = (
        select(Produit.categorie, func.count(Produit.id).label("nb"))
        .group_by(Produit.categorie)
        .having(func.count(Produit.id) > 2)
    )
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter les requêtes avec agrégations, montrer le SQL généré et les résultats
> **Expliquer :** Montrer le SQL GROUP BY généré, puis exécuter la même requête directement dans DBeaver/psql pour montrer que le résultat est identique. Comparer la lisibilité Python vs SQL brut.

---

## UPDATE — Modifier des données

### Modifier un objet chargé

```python
with Session(engine) as session:
    produit = session.get(Produit, 1)
    if produit:
        produit.prix = Decimal("79.99")
        produit.stock = 20
        session.commit()
        print(f"Produit mis à jour: {produit}")
```

### Update en masse (sans charger les objets)

```python
with Session(engine) as session:
    # Mise à jour directe — performant pour les gros volumes
    stmt = (
        update(Produit)
        .where(Produit.categorie == "test")
        .values(actif=False, stock=0)
    )
    result = session.execute(stmt)
    session.commit()
    print(f"{result.rowcount} produits mis à jour")
```

## DELETE — Supprimer des données

### Supprimer un objet chargé

```python
with Session(engine) as session:
    produit = session.get(Produit, 1)
    if produit:
        session.delete(produit)
        session.commit()
        print("Produit supprimé")
```

### Suppression en masse

```python
with Session(engine) as session:
    stmt = delete(Produit).where(Produit.actif == False)
    result = session.execute(stmt)
    session.commit()
    print(f"{result.rowcount} produits supprimés")
```

## SQL brut avec `text()`

Pour des requêtes trop complexes pour l'ORM :

```python
from sqlalchemy import text

with Session(engine) as session:
    # Requête SQL brute avec paramètres liés (toujours utiliser :param pour éviter les injections)
    stmt = text("""
        SELECT
            categorie,
            COUNT(*) as nb,
            AVG(prix)::numeric(10,2) as prix_moyen,
            SUM(prix * stock)::numeric(10,2) as valeur_totale
        FROM produits
        WHERE actif = :actif
        GROUP BY categorie
        ORDER BY valeur_totale DESC
    """)
    rows = session.execute(stmt, {"actif": True}).all()
    for row in rows:
        print(f"{row.categorie}: {row.nb} produits, {row.prix_moyen}€ moy, {row.valeur_totale}€ total")
```

## Gestion des transactions

```python
with Session(engine) as session:
    try:
        # Toutes ces opérations sont dans la même transaction
        p1 = Produit(nom="Produit A", prix=Decimal("10.00"), categorie="test", stock=5)
        p2 = Produit(nom="Produit B", prix=Decimal("20.00"), categorie="test", stock=3)
        session.add_all([p1, p2])

        # flush() envoie les changements en BDD sans committer
        # (utile pour récupérer les IDs générés)
        session.flush()
        print(f"IDs générés: {p1.id}, {p2.id}")

        # Simuler une erreur
        if p1.id > 0:
            raise ValueError("Erreur simulée")

        session.commit()
    except Exception as e:
        session.rollback()  # Annule tous les changements
        print(f"Rollback effectué: {e}")
```

## Upsert (INSERT ou UPDATE)

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert

with Session(engine) as session:
    stmt = pg_insert(Produit).values(
        nom="Clavier mécanique",
        prix=Decimal("89.99"),
        categorie="informatique",
        stock=15
    )
    # Si conflit sur 'nom', mettre à jour le prix et le stock
    stmt = stmt.on_conflict_do_update(
        index_elements=["nom"],
        set_={"prix": stmt.excluded.prix, "stock": stmt.excluded.stock}
    )
    session.execute(stmt)
    session.commit()
```
