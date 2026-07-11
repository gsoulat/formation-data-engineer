# ORM — Object-Relational Mapping : Vue d'ensemble

Un ORM (Object-Relational Mapping) est une couche d'abstraction qui permet de manipuler une base de données relationnelle via des objets dans votre langage de programmation, sans écrire de SQL brut.

## Qu'est-ce que l'impedance mismatch ?

Les bases de données relationnelles stockent des données sous forme de **tables, lignes et colonnes**. Les langages orientés objet les représentent sous forme d'**objets, instances et attributs**. Cette différence de paradigme s'appelle l'impedance mismatch — un ORM la résout en faisant la traduction automatiquement.

```
[Objet Python/Java/Rust]  ←→  [ORM]  ←→  [Table SQL]
     user.name                             users.name
     user.posts (liste)                    SELECT * FROM posts WHERE user_id = ?
```

## Les deux grands patterns d'ORM

### Active Record
Le modèle **est** la table. L'objet connait comment se sauvegarder lui-même.
```python
# L'objet User sait interagir directement avec la BDD
user = User(name="Alice")
user.save()          # INSERT INTO users ...
user.delete()        # DELETE FROM users ...
User.find(id=1)      # SELECT * FROM users WHERE id = 1
```
Exemples : Django ORM, Rails ActiveRecord, Tortoise-ORM (mode simplifié)

### Data Mapper
Le modèle est **séparé** de la logique de persistance. Une couche Session/Repository fait la traduction.
```python
# L'objet User ne sait pas qu'il est en BDD
user = User(name="Alice")
session.add(user)    # enregistrement délégué à la session
session.commit()     # INSERT INTO users ...
```
Exemples : SQLAlchemy, Hibernate/JPA, Diesel

---

## Tableau comparatif des ORMs

| ORM | Langage | Async | Pattern | DB supportées | Points forts | Points faibles |
|-----|---------|-------|---------|---------------|--------------|----------------|
| **SQLAlchemy** | Python | Partiel (2.0+) | Data Mapper | PostgreSQL, MySQL, SQLite, Oracle, MSSQL | Complet, mature, flexible | Verbeux, courbe d'apprentissage |
| **SQLModel** | Python | Partiel | Data Mapper | Idem SQLAlchemy | SQLAlchemy + Pydantic unifié | Moins mature, sous-ensemble SQLAlchemy |
| **Oxide** | Python | Natif | Active Record | PostgreSQL, MySQL, SQLite | Simple, moderne, async natif | Moins de fonctionnalités avancées |
| **Tortoise-ORM** | Python | Natif | Active Record | PostgreSQL, MySQL, SQLite | Django-like, async complet | Moins mature que SQLAlchemy |
| **Ormar** | Python | Natif | Data Mapper | PostgreSQL, MySQL, SQLite | SQLAlchemy + Pydantic + async | Projet moins actif |
| **Hibernate/JPA** | Java | Non (JPA std) | Data Mapper | Tous (JDBC) | Standard Java EE, très complet | Configuration XML/annotation lourde |
| **Spring Data JPA** | Java | Via Reactor | Repository | Idem Hibernate | Repositories auto-générés, Spring Boot | Couplé à Spring |
| **Diesel** | Rust | Non (sync) | Data Mapper | PostgreSQL, MySQL, SQLite | Type-safe, compile-time checks | Pas d'async natif |
| **SeaORM** | Rust | Natif | Active Record | PostgreSQL, MySQL, SQLite | Async, ergonomique | Moins mature que Diesel |

---

## Quand utiliser un ORM vs SQL brut ?

### Utiliser un ORM quand...
- Vous faites du CRUD classique (insert, select, update, delete simples)
- Vous voulez la portabilité entre plusieurs SGBD
- Votre équipe est plus à l'aise avec le code qu'avec SQL
- Vous voulez les migrations automatisées
- Vous construisez une API REST ou une application web

### Utiliser du SQL brut quand...
- Vos requêtes sont très complexes (analytics, agrégations, window functions)
- Les performances sont critiques et vous avez besoin du contrôle total
- Vous faites du reporting ou du Data Warehousing
- Vous utilisez des fonctionnalités spécifiques à un SGBD (JSONB, arrays, etc.)
- Vous avez déjà une équipe SQL forte

### Approche hybride (recommandée en production)
```python
# CRUD simple → ORM
users = session.exec(select(User).where(User.active == True)).all()

# Requête complexe → SQL brut via l'ORM
result = session.exec(text("""
    SELECT u.name, COUNT(o.id) as order_count, SUM(o.total) as revenue
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
    HAVING COUNT(o.id) > 5
    ORDER BY revenue DESC
""")).all()
```

---

## Structure de ce cours

### Python
| Section | Description |
|---------|-------------|
| [SQLAlchemy](./Python/SQLAlchemy/) | L'ORM Python de référence, pattern Data Mapper |
| [SQLModel](./Python/SQLModel/) | SQLAlchemy + Pydantic, idéal pour FastAPI |
| [Oxide](./Python/Oxide/) | ORM async moderne et léger |
| [Tortoise-ORM](./Python/Tortoise-ORM/) | ORM async inspiré de Django |
| [Ormar](./Python/Ormar/) | Mini ORM async SQLAlchemy + Pydantic |

### Java
| Section | Description |
|---------|-------------|
| [JPA / Hibernate](./Java/JPA-Hibernate/) | Standard Java EE, ORM le plus utilisé en entreprise |
| [Spring Data JPA](./Java/Spring-Data-JPA/) | Couche Repository au-dessus de JPA, Spring Boot |

### Rust
| Section | Description |
|---------|-------------|
| [Diesel](./Rust/Diesel/) | ORM type-safe compilé, sync |
| [SeaORM](./Rust/SeaORM/) | ORM async pour Rust, moderne |

### Migrations
| Section | Description |
|---------|-------------|
| [Alembic](./Migrations/Alembic/) | Gestion de migrations pour SQLAlchemy/Python |
| [Diesel Migrations](./Migrations/Diesel-Migrations/) | Migrations intégrées pour Diesel/Rust |

---

## Prérequis généraux

- **SQL** : bases solides (SELECT, INSERT, UPDATE, DELETE, JOIN, CREATE TABLE)
- **POO** : classes, héritage, instances
- **Git** : pour versionner les migrations
- **Docker** : recommandé pour lancer PostgreSQL localement

## Lancer une base de données PostgreSQL pour les exercices

```bash
docker run --name orm-postgres \
  -e POSTGRES_USER=formation \
  -e POSTGRES_PASSWORD=formation \
  -e POSTGRES_DB=orm_db \
  -p 5432:5432 \
  -d postgres:15
```

```bash
# Vérifier que PostgreSQL tourne
docker ps | grep orm-postgres

# Se connecter avec psql
docker exec -it orm-postgres psql -U formation -d orm_db
```

---

> **Conseil pédagogique** : commencez par SQLAlchemy (Python) pour maîtriser les concepts fondamentaux, puis explorez les autres ORMs en comparant avec ce que vous avez appris. Les patterns se retrouvent dans tous les langages.
