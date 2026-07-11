# Module 05 - Migrations avec Alembic

## Objectifs du module

- Comprendre pourquoi versionner le schema de base de donnees
- Installer et configurer Alembic avec SQLAlchemy
- Creer, appliquer et annuler des migrations
- Maitriser l'autogeneration et les migrations manuelles
- Integrer Alembic dans un workflow d'equipe et CI/CD

## Pourquoi versionner son schema ?

### Le probleme

```
Developpeur A                     Developpeur B
"J'ai ajoute une colonne          "J'ai ajoute une colonne
 'role' a la table users"          'phone' a la table users"
         │                                  │
         ▼                                  ▼
   ALTER TABLE users               ALTER TABLE users
   ADD COLUMN role VARCHAR;        ADD COLUMN phone VARCHAR;
         │                                  │
         └──────────┬───────────────────────┘
                    │
                    ▼
          En production, qui fait quoi ?
          Dans quel ordre ?
          Et si ca echoue a mi-chemin ?
```

### La solution : les migrations

```
Code source (Git)                    Base de donnees
┌─────────────────┐                 ┌─────────────────┐
│ migration_001   │ ──── apply ───> │ version: 001    │
│ + colonne role  │                 │ + colonne role  │
├─────────────────┤                 ├─────────────────┤
│ migration_002   │ ──── apply ───> │ version: 002    │
│ + colonne phone │                 │ + colonne phone │
├─────────────────┤                 ├─────────────────┤
│ migration_003   │ ──── apply ───> │ version: 003    │
│ + index email   │                 │ + index email   │
└─────────────────┘                 └─────────────────┘

    Versionne dans Git                Etat tracable
    Executable par tous               Reproductible
    Reversible (downgrade)            Auditable
```

### Principes fondamentaux

| Principe | Description |
|----------|-------------|
| **Versionne** | Chaque changement de schema a un identifiant unique |
| **Ordonne** | Les migrations s'appliquent dans un ordre precis |
| **Reversible** | Chaque migration a un `upgrade` et un `downgrade` |
| **Idempotent** | Appliquer deux fois la meme migration ne casse rien |
| **Incremental** | Petits changements frequents > gros changements rares |

## Qu'est-ce qu'Alembic ?

**Alembic** est l'outil de migration officiel de SQLAlchemy, cree par le meme auteur (Mike Bayer).

```
┌─────────────────┐
│   SQLAlchemy     │  ← Definit les modeles (etat desire)
│   Models         │
└────────┬────────┘
         │
         ▼ compare
┌─────────────────┐
│    Alembic       │  ← Genere les migrations (differences)
│                  │
│ upgrade()        │  → ALTER TABLE, CREATE TABLE, ...
│ downgrade()      │  → DROP TABLE, ALTER TABLE, ...
└────────┬────────┘
         │
         ▼ execute
┌─────────────────┐
│  Base de donnees │  ← Applique les changements
│  (+ table        │
│   alembic_version│  ← Stocke la version courante
│  )               │
└─────────────────┘
```

## Installation et initialisation

### Installation

```bash
pip install alembic
```

### Initialisation

```bash
# Dans le repertoire du projet
alembic init alembic
```

Structure creee :

```
mon-projet/
├── alembic/
│   ├── versions/          # Les fichiers de migration
│   ├── env.py             # Configuration Alembic
│   ├── README
│   └── script.py.mako     # Template des migrations
├── alembic.ini            # Configuration principale
└── models.py              # Vos modeles SQLAlchemy
```

### Configuration

**`alembic.ini`** : URL de la base de donnees

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/mydb
```

> **Bonne pratique** : ne pas mettre le mot de passe en dur. Utiliser une variable d'environnement.

**`alembic/env.py`** : importer vos modeles

```python
# alembic/env.py
from models import Base  # Importer votre Base declarative

# Trouver cette ligne et la modifier :
target_metadata = Base.metadata
```

### Configuration avec variable d'environnement

```python
# alembic/env.py
import os
from models import Base

def run_migrations_online():
    url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
        )
        with context.begin_transaction():
            context.run_migrations()
```

## Creer des migrations

### Autogeneration (recommandee)

Alembic compare vos modeles Python avec l'etat actuel de la base et genere automatiquement la migration :

```bash
# Creer une migration automatique
alembic revision --autogenerate -m "ajout table users"
```

Fichier genere (`alembic/versions/xxxx_ajout_table_users.py`) :

```python
"""ajout table users

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2025-01-15 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

# Identifiants de revision
revision = 'a1b2c3d4e5f6'
down_revision = None  # Premiere migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_name'), 'users', ['name'])


def downgrade() -> None:
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
```

### Migration manuelle

Pour les cas que l'autogeneration ne detecte pas :

```bash
# Creer une migration vide
alembic revision -m "ajout donnees initiales"
```

```python
def upgrade() -> None:
    # Insertion de donnees
    op.execute("""
        INSERT INTO roles (name) VALUES
        ('admin'), ('editor'), ('viewer')
    """)

    # Renommage de colonne (non detecte par autogenerate)
    op.alter_column('users', 'name', new_column_name='full_name')


def downgrade() -> None:
    op.alter_column('users', 'full_name', new_column_name='name')
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'editor', 'viewer')")
```

### Ce que l'autogeneration detecte (et ne detecte pas)

| Detecte automatiquement | Non detecte |
|------------------------|-------------|
| Creation/suppression de table | Renommage de table |
| Ajout/suppression de colonne | Renommage de colonne |
| Changement de type | Migration de donnees |
| Ajout/suppression d'index | Changement de nom de contrainte |
| Ajout/suppression de FK | Triggers, fonctions SQL |
| Changement de nullable | Vues, procedures stockees |

## Appliquer et gerer les migrations

### Commandes essentielles

```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer une seule migration
alembic upgrade +1

# Appliquer jusqu'a une revision specifique
alembic upgrade a1b2c3d4e5f6

# Annuler la derniere migration
alembic downgrade -1

# Revenir a zero (tout supprimer)
alembic downgrade base

# Voir l'etat actuel
alembic current

# Voir l'historique
alembic history

# Voir l'historique detaille
alembic history --verbose

# Voir les migrations en attente
alembic heads
```

### Workflow quotidien

```bash
# 1. Modifier vos modeles Python
#    (ajouter une colonne, une table, etc.)

# 2. Generer la migration
alembic revision --autogenerate -m "description claire"

# 3. Relire et ajuster la migration generee
#    (verifier le upgrade ET le downgrade)

# 4. Appliquer la migration
alembic upgrade head

# 5. Tester le downgrade
alembic downgrade -1
alembic upgrade head

# 6. Commiter le fichier de migration avec le code
git add alembic/versions/xxxx_description.py
git commit -m "feat: ajout colonne role a users"
```

## Operations courantes

### Ajouter une colonne

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(50), server_default='viewer'))

def downgrade() -> None:
    op.drop_column('users', 'role')
```

### Creer un index

```python
def upgrade() -> None:
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
```

### Modifier un type de colonne

```python
def upgrade() -> None:
    op.alter_column(
        'products',
        'price',
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 2),
    )

def downgrade() -> None:
    op.alter_column(
        'products',
        'price',
        existing_type=sa.Numeric(10, 2),
        type_=sa.Integer(),
    )
```

### Migration de donnees

```python
from sqlalchemy import table, column, String

def upgrade() -> None:
    # Ajouter la colonne
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # Migrer les donnees
    users = table('users',
        column('first_name', String),
        column('last_name', String),
        column('full_name', String),
    )
    op.execute(
        users.update().values(
            full_name=users.c.first_name + ' ' + users.c.last_name
        )
    )

    # Supprimer les anciennes colonnes
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade() -> None:
    op.add_column('users', sa.Column('first_name', sa.String(100)))
    op.add_column('users', sa.Column('last_name', sa.String(100)))

    users = table('users',
        column('full_name', String),
        column('first_name', String),
        column('last_name', String),
    )
    # Attention : la migration inverse perd potentiellement des donnees
    op.execute(
        users.update().values(
            first_name=sa.func.split_part(users.c.full_name, ' ', 1),
            last_name=sa.func.split_part(users.c.full_name, ' ', 2),
        )
    )

    op.drop_column('users', 'full_name')
```

## Integration CI/CD

### Verifier qu'il n'y a pas de migration manquante

```bash
# Dans le pipeline CI, verifier que les modeles sont en sync
alembic check
# Retourne un code d'erreur si une migration est necessaire
```

### Appliquer les migrations au deploiement

```yaml
# docker-compose.yml
services:
  app:
    build: .
    command: >
      sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0"
    depends_on:
      - db
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0"]
```

### GitHub Actions

```yaml
# .github/workflows/migrations.yml
name: Check Migrations

on: [pull_request]

jobs:
  check-migrations:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - run: pip install -r requirements.txt

      - name: Apply migrations
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/postgres
        run: alembic upgrade head

      - name: Check no pending migrations
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/postgres
        run: alembic check
```

## Bonnes pratiques

### 1. Toujours relire les migrations generees

L'autogeneration n'est pas parfaite. Verifiez toujours :
- Le `upgrade()` fait ce que vous attendez
- Le `downgrade()` est l'inverse exact
- Pas d'operation destructive involontaire

### 2. Messages descriptifs

```bash
# ❌ Mauvais
alembic revision --autogenerate -m "update"

# ✅ Bon
alembic revision --autogenerate -m "ajout colonne role a users avec default viewer"
```

### 3. Tester les downgrades

```bash
# Toujours verifier que le downgrade fonctionne
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### 4. Une migration = un changement logique

```bash
# ❌ Mauvais : une mega-migration
alembic revision --autogenerate -m "ajout users, posts, comments, tags, categories"

# ✅ Bon : une migration par changement
alembic revision --autogenerate -m "ajout table users"
alembic revision --autogenerate -m "ajout table posts avec FK vers users"
alembic revision --autogenerate -m "ajout table comments"
```

### 5. Ne jamais modifier une migration deja appliquee en production

```
Migration deja en prod ?
├── Oui → Creer une NOUVELLE migration corrective
└── Non → Vous pouvez la modifier
```

## Exercices

### Exercice 1 : Setup complet

1. Creer un projet avec SQLAlchemy + Alembic
2. Definir les modeles `User`, `Post`, `Tag`
3. Generer et appliquer la migration initiale
4. Verifier les tables creees

### Exercice 2 : Evolution du schema

En partant de l'exercice 1 :
1. Ajouter une colonne `bio` a `User`
2. Creer une table `Comment` avec FK vers `Post` et `User`
3. Ajouter un index sur `Post.title`
4. Pour chaque changement : generer, relire, appliquer, tester le downgrade

### Exercice 3 : Migration de donnees

1. Vous avez une colonne `User.name` (ex: "Alice Dupont")
2. Creer une migration qui :
   - Ajoute `first_name` et `last_name`
   - Migre les donnees depuis `name`
   - Supprime `name`
3. Ecrire le downgrade correspondant

---

> **A retenir** : Alembic est a la base de donnees ce que Git est au code source. Chaque changement de schema est tracable, reversible et reproductible. C'est un outil indispensable des qu'on travaille en equipe ou qu'on deploie en production.
