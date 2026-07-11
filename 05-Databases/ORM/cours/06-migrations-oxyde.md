# Module 06 - Migrations avec Oxyde

## Objectifs du module

- Comprendre l'approche d'Oxyde pour les migrations
- Creer et appliquer des migrations avec Oxyde
- Comparer avec Alembic
- Connaitre les avantages et limites

## L'approche Oxyde

Contrairement a Alembic qui est un outil **separe** de SQLAlchemy, Oxyde integre les migrations **directement** dans l'ORM. Pas d'outil CLI externe, pas de configuration supplementaire.

```
Alembic (approche separee)           Oxyde (approche integree)
┌──────────┐  ┌──────────┐          ┌──────────────────────┐
│SQLAlchemy│  │ Alembic  │          │       Oxyde          │
│ (modeles)│  │(migrations│          │                      │
│          │  │  CLI)     │          │ Modeles + Migrations │
│          │  │          │          │ dans le meme outil   │
└──────────┘  └──────────┘          └──────────────────────┘
  2 outils     Config separee         1 seul outil
  alembic.ini  env.py                 Config integree
```

### Philosophie

| Principe | Description |
|----------|-------------|
| **Zero config** | Pas de fichier de configuration supplementaire |
| **Integre** | Les migrations font partie de l'ORM |
| **Auto-detection** | Detection automatique des changements |
| **Type-safe** | Les migrations sont du code Python type |

## Configuration

### Activer les migrations

```python
from oxyde import Database, Model, Field

# Activer le support des migrations
db = Database(
    "postgresql://user:pass@localhost/mydb",
    migrations=True,           # Active les migrations
    migrations_dir="migrations" # Dossier de stockage (defaut: migrations/)
)
```

Structure creee automatiquement :

```
mon-projet/
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_add_role_to_users.py
│   └── ...
├── models.py
└── main.py
```

## Creer des migrations

### Generation automatique

```python
# Apres avoir modifie vos modeles, dans un script ou le CLI :
await db.make_migrations(message="ajout colonne role a users")
```

Ou via la ligne de commande :

```bash
oxyde makemigrations -m "ajout colonne role a users"
```

### Fichier de migration genere

```python
# migrations/0002_ajout_colonne_role_a_users.py
"""
Migration: ajout colonne role a users
Created: 2025-01-15 10:30:00
"""

from oxyde.migrations import Migration, op
import oxyde.types as t


class Migration_0002(Migration):
    depends_on = ["0001_initial"]

    async def upgrade(self):
        await op.add_column(
            "users",
            op.Column("role", t.String(50), default="viewer"),
        )

    async def downgrade(self):
        await op.drop_column("users", "role")
```

### Migration manuelle

```python
# migrations/0003_donnees_initiales.py
from oxyde.migrations import Migration, op


class Migration_0003(Migration):
    depends_on = ["0002_ajout_colonne_role_a_users"]

    async def upgrade(self):
        await op.execute("""
            INSERT INTO roles (name, description) VALUES
            ('admin', 'Administrateur'),
            ('editor', 'Editeur'),
            ('viewer', 'Lecteur')
        """)

    async def downgrade(self):
        await op.execute(
            "DELETE FROM roles WHERE name IN ('admin', 'editor', 'viewer')"
        )
```

## Appliquer les migrations

### Commandes

```bash
# Appliquer toutes les migrations en attente
oxyde migrate

# Appliquer jusqu'a une migration specifique
oxyde migrate 0002

# Annuler la derniere migration
oxyde rollback

# Annuler jusqu'a une migration specifique
oxyde rollback 0001

# Voir le statut
oxyde migrate --status

# Voir l'historique
oxyde migrate --history
```

### Programmatiquement

```python
# Dans votre code Python
async def setup():
    db = Database("postgresql://...", migrations=True)

    # Appliquer les migrations au demarrage
    await db.migrate()

    # Ou verifier s'il y a des migrations en attente
    pending = await db.pending_migrations()
    if pending:
        print(f"{len(pending)} migrations en attente")
        await db.migrate()
```

### Integration au demarrage FastAPI

```python
from fastapi import FastAPI
from oxyde import Database

db = Database("postgresql://...", migrations=True)
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Appliquer automatiquement les migrations
    await db.migrate()
    print("Migrations appliquees")
```

## Operations courantes

### Ajouter une colonne

```python
async def upgrade(self):
    await op.add_column(
        "users",
        op.Column("phone", t.String(20), nullable=True),
    )

async def downgrade(self):
    await op.drop_column("users", "phone")
```

### Creer une table

```python
async def upgrade(self):
    await op.create_table(
        "categories",
        op.Column("id", t.Integer, primary_key=True, auto_increment=True),
        op.Column("name", t.String(100), nullable=False, unique=True),
        op.Column("description", t.Text, nullable=True),
    )

async def downgrade(self):
    await op.drop_table("categories")
```

### Creer un index

```python
async def upgrade(self):
    await op.create_index("ix_users_email", "users", ["email"], unique=True)

async def downgrade(self):
    await op.drop_index("ix_users_email", "users")
```

### Ajouter une foreign key

```python
async def upgrade(self):
    await op.add_column(
        "posts",
        op.Column("category_id", t.Integer, nullable=True),
    )
    await op.create_foreign_key(
        "fk_posts_category",
        "posts", "categories",
        ["category_id"], ["id"],
    )

async def downgrade(self):
    await op.drop_foreign_key("fk_posts_category", "posts")
    await op.drop_column("posts", "category_id")
```

## Comparaison Alembic vs Oxyde Migrations

### Configuration

```
Alembic                              Oxyde
──────                               ─────
alembic init alembic                 db = Database(..., migrations=True)
Modifier alembic.ini                 # C'est tout
Modifier env.py
Importer les modeles
```

### Commandes

| Action | Alembic | Oxyde |
|--------|---------|-------|
| Initialiser | `alembic init` | Automatique |
| Creer migration | `alembic revision --autogenerate -m "..."` | `oxyde makemigrations -m "..."` |
| Appliquer | `alembic upgrade head` | `oxyde migrate` |
| Annuler | `alembic downgrade -1` | `oxyde rollback` |
| Statut | `alembic current` | `oxyde migrate --status` |
| Historique | `alembic history` | `oxyde migrate --history` |
| Verifier | `alembic check` | Integre |

### Style des migrations

```python
# --- Alembic (synchrone, fonctions) ---
def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(50)))

def downgrade() -> None:
    op.drop_column('users', 'role')


# --- Oxyde (async, classes) ---
class Migration_0002(Migration):
    async def upgrade(self):
        await op.add_column("users", op.Column("role", t.String(50)))

    async def downgrade(self):
        await op.drop_column("users", "role")
```

### Tableau comparatif complet

| Critere | Alembic | Oxyde Migrations |
|---------|---------|-----------------|
| **Configuration** | Manuelle (3+ fichiers) | Automatique |
| **Autogeneration** | Oui (tres bonne) | Oui |
| **Async** | Non natif | Natif |
| **Branches** | Oui (merge de branches) | Lineaire |
| **Integration CI** | `alembic check` | Integre |
| **Maturite** | 12+ ans | Recente |
| **Documentation** | Tres complete | En croissance |
| **Complexite** | Peut gerer tout | Cas courants |
| **Ecosysteme** | Large | Limite a Oxyde |

### Quand choisir quoi ?

| Situation | Choix |
|-----------|-------|
| Projet SQLAlchemy / SQLModel | **Alembic** (seul choix) |
| Projet Oxyde | **Oxyde Migrations** |
| Besoin de branches de migration | **Alembic** |
| Migration de donnees complexe | **Alembic** (plus mature) |
| Simplicite maximale | **Oxyde Migrations** |
| Nouveau projet sans contrainte | Les deux conviennent |

## Bonnes pratiques (valables pour les deux)

### 1. Nommer clairement ses migrations

```bash
# ❌
oxyde makemigrations -m "update"

# ✅
oxyde makemigrations -m "ajout colonne role a users default viewer"
```

### 2. Tester le rollback

```bash
# Toujours verifier
oxyde migrate
oxyde rollback
oxyde migrate
```

### 3. Ne pas modifier une migration deployee

Si une migration est deja en production, creer une **nouvelle** migration corrective.

### 4. Commiter les migrations avec le code

```bash
git add migrations/ models.py
git commit -m "feat: ajout role utilisateur avec migration"
```

### 5. Appliquer les migrations au deploiement

```python
# Au demarrage de l'application
await db.migrate()
```

## Exercices

### Exercice 1 : Workflow complet avec Oxyde

1. Creer un projet avec Oxyde et les migrations activees
2. Definir un modele `Article` (id, title, content, published)
3. Generer et appliquer la migration initiale
4. Ajouter une colonne `author` a `Article`
5. Generer, appliquer, puis rollback la migration

### Exercice 2 : Migration de donnees

1. Avoir une table `users` avec `name` (prenom + nom)
2. Creer une migration qui :
   - Ajoute `first_name` et `last_name`
   - Migre les donnees
   - Supprime `name`
3. Tester le rollback

### Exercice 3 : Comparaison pratique

Sur le meme schema (User, Post, Comment) :
1. Implementer les migrations avec Alembic (sur un projet SQLAlchemy)
2. Implementer les migrations avec Oxyde
3. Comparer : lignes de code, facilite, temps de setup

---

> **A retenir** : Les migrations Oxyde offrent une experience simplifiee et integree, ideale pour les projets Oxyde. Alembic reste la reference pour les projets SQLAlchemy/SQLModel et les scenarios complexes. Dans tous les cas, **versionner son schema est indispensable** des qu'on travaille en equipe ou qu'on deploie en production.
