# Module 01 - Introduction aux ORM

## Objectifs du module

- Comprendre ce qu'est un ORM et pourquoi en utiliser un
- Connaitre les patterns fondamentaux (Active Record, Data Mapper)
- Identifier les avantages et inconvenients des ORM
- Decouvrir l'ecosysteme Python des ORM

## Qu'est-ce qu'un ORM ?

Un **ORM** (Object-Relational Mapping) est une technique qui permet de manipuler une base de donnees relationnelle en utilisant des **objets** dans un langage de programmation, au lieu d'ecrire du SQL brut.

```
Sans ORM                              Avec ORM
──────────────────                    ──────────────────
cursor.execute("""                    user = User(
    INSERT INTO users                     name="Alice",
    (name, email, age)                    email="alice@ex.com",
    VALUES (%s, %s, %s)                   age=30
""", ("Alice",                        )
     "alice@ex.com",                  session.add(user)
     30))                             session.commit()
conn.commit()
```

### Le probleme que l'ORM resout

```
┌──────────────┐                    ┌──────────────┐
│   Monde      │                    │   Monde      │
│   Objet      │   "Impedance      │ Relationnel  │
│              │    Mismatch"       │              │
│ - Classes    │ ◄──────────────►   │ - Tables     │
│ - Heritage   │   Incompatibilite │ - Lignes     │
│ - Methodes   │   fondamentale    │ - Colonnes   │
│ - References │                    │ - FK / Joins │
└──────────────┘                    └──────────────┘

         L'ORM fait le pont entre ces deux mondes
```

**L'impedance mismatch** : les objets en Python (classes, heritage, polymorphisme) ne correspondent pas directement aux structures relationnelles (tables, lignes, foreign keys). L'ORM traduit l'un vers l'autre.

## Les patterns fondamentaux

### Active Record

Chaque objet sait comment se sauvegarder, se charger et se supprimer lui-meme :

```python
# Pattern Active Record (style Django ORM)
user = User(name="Alice", email="alice@ex.com")
user.save()           # L'objet se sauvegarde lui-meme

user.name = "Bob"
user.save()           # L'objet se met a jour lui-meme

user.delete()         # L'objet se supprime lui-meme

# Recherche via la classe
users = User.objects.filter(age__gt=25)
```

**Avantages** : Simple, intuitif, peu de code
**Inconvenients** : L'objet melange logique metier et persistance

### Data Mapper

La persistance est geree par un composant separe (le "mapper" ou "session") :

```python
# Pattern Data Mapper (style SQLAlchemy)
user = User(name="Alice", email="alice@ex.com")

session.add(user)     # La session gere la persistance
session.commit()      # La session ecrit en base

user.name = "Bob"
session.commit()      # La session detecte le changement

session.delete(user)
session.commit()
```

**Avantages** : Separation des responsabilites, testable, flexible
**Inconvenients** : Plus verbeux, necessite de gerer la session

### Comparaison

| Critere | Active Record | Data Mapper |
|---------|--------------|-------------|
| **Simplicite** | Tres simple | Plus complexe |
| **Separation** | Faible (objet = persistence) | Forte (objet ≠ persistence) |
| **Testabilite** | Moyenne | Excellente |
| **Flexibilite** | Moyenne | Excellente |
| **ORM Python** | Django ORM | SQLAlchemy |
| **Cas d'usage** | CRUD simple, prototypage | Applications complexes, DDD |

## Avantages et inconvenients des ORM

### Avantages

| Avantage | Explication |
|----------|-------------|
| **Productivite** | Moins de code a ecrire, moins de SQL repetitif |
| **Portabilite** | Changer de SGBD sans reecrire les requetes |
| **Securite** | Protection native contre les injections SQL |
| **Maintenabilite** | Le schema est defini dans le code (single source of truth) |
| **Migrations** | Versioning du schema de base de donnees |
| **Relations** | Navigation intuitive entre objets lies |

### Inconvenients

| Inconvenient | Explication |
|-------------|-------------|
| **Performance** | Les requetes generees ne sont pas toujours optimales |
| **Abstraction fuyante** | On finit quand meme par devoir comprendre le SQL |
| **N+1 queries** | Piege classique : une requete par objet lie |
| **Complexite** | Courbe d'apprentissage pour les cas avances |
| **Magie noire** | Comportements implicites difficiles a debugger |

### Le probleme N+1

```python
# ❌ N+1 queries (1 requete + N requetes supplementaires)
users = session.query(User).all()  # 1 requete : SELECT * FROM users
for user in users:
    print(user.posts)               # N requetes : SELECT * FROM posts WHERE user_id = ?

# ✅ Eager loading (1 seule requete avec JOIN)
users = session.query(User).options(joinedload(User.posts)).all()
# 1 requete : SELECT * FROM users JOIN posts ON ...
```

## L'ecosysteme Python

### Les ORM majeurs

```
┌─────────────────────────────────────────────────────────┐
│                    Ecosysteme Python                     │
├──────────────┬──────────────┬──────────────┬────────────┤
│  SQLAlchemy  │   SQLModel   │    Django    │   Oxyde    │
│              │              │     ORM      │            │
│  Le standard │  SQLAlchemy  │  Integre a   │  Approche  │
│  industrie   │  + Pydantic  │  Django      │  moderne   │
│              │  + FastAPI   │              │  Rust-like │
│  Data Mapper │  Data Mapper │ Active Record│            │
│  2006+       │  2021+       │  2005+       │  Recent    │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### Lequel choisir ?

| Situation | Choix recommande | Pourquoi |
|-----------|-----------------|----------|
| Application FastAPI | **SQLModel** | Integration native Pydantic + FastAPI |
| Application complexe | **SQLAlchemy** | Flexibilite maximale, controle total |
| Application Django | **Django ORM** | Integre, pas le choix |
| Projet qui valorise la performance | **Oxyde** | Approche moderne et performante |
| Prototypage rapide | **SQLModel** | Minimal, peu de code |
| Legacy / migration | **SQLAlchemy** | Standard, communaute, documentation |

### Ce que nous allons couvrir

Dans ce cours, nous nous concentrons sur trois ORM :

1. **SQLAlchemy** (module 02) : le standard Python, fondation des autres
2. **SQLModel** (module 03) : la surcouche moderne pour FastAPI
3. **Oxyde** (module 04) : l'approche nouvelle generation

Puis nous aborderons le **versioning de base de donnees** :

4. **Alembic** (module 05) : migrations pour SQLAlchemy
5. **Oxyde Migrations** (module 06) : migrations avec Oxyde

## SQL vs ORM : quand utiliser quoi ?

### Utiliser du SQL brut quand...

- Requetes analytiques complexes (fenetres, CTE recursives)
- Optimisation fine des performances
- Requetes specifiques a un SGBD (extensions PostgreSQL)
- Migrations de donnees en masse

### Utiliser un ORM quand...

- CRUD standard (Create, Read, Update, Delete)
- Relations entre entites
- Logique metier liee aux donnees
- Portabilite entre SGBD
- Equipe avec des niveaux SQL varies

### L'approche hybride (recommandee)

```python
# ORM pour le CRUD standard
user = session.get(User, user_id)
user.name = "Nouveau nom"
session.commit()

# SQL brut pour les requetes complexes
result = session.execute(text("""
    WITH monthly_stats AS (
        SELECT user_id,
               DATE_TRUNC('month', created_at) as month,
               COUNT(*) as post_count
        FROM posts
        GROUP BY user_id, month
    )
    SELECT u.name, ms.month, ms.post_count
    FROM users u
    JOIN monthly_stats ms ON u.id = ms.user_id
    WHERE ms.post_count > 10
"""))
```

## Exercices

### Exercice 1 : Reflexion

Pour un projet de gestion de bibliotheque (livres, auteurs, emprunts) :
1. Lister les entites et leurs relations
2. Ecrire les requetes SQL pour les operations CRUD de base
3. Imaginer comment ce meme code serait ecrit avec un ORM

### Exercice 2 : Comparaison

Comparer ces deux approches et identifier les avantages de chacune :

```python
# Approche SQL
cursor.execute("""
    SELECT u.name, COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    WHERE u.active = true
    GROUP BY u.name
    HAVING COUNT(p.id) > 5
    ORDER BY post_count DESC
""")

# Approche ORM
users = (
    session.query(User.name, func.count(Post.id).label("post_count"))
    .join(Post, isouter=True)
    .filter(User.active == True)
    .group_by(User.name)
    .having(func.count(Post.id) > 5)
    .order_by(desc("post_count"))
    .all()
)
```

---

> **A retenir** : Un ORM n'est pas un remplacement du SQL, c'est un **complement**. Le bon developpeur sait utiliser les deux et choisit le bon outil selon le contexte. Maitriser SQL reste indispensable, meme avec un ORM.
