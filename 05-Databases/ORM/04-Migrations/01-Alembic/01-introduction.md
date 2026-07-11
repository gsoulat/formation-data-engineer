# Alembic — Introduction et configuration

## Initialiser Alembic

```bash
# Dans votre projet Python
pip install alembic sqlalchemy psycopg2-binary

# Initialiser Alembic (crée le dossier alembic/ et alembic.ini)
alembic init alembic

# Structure créée :
# alembic.ini              ← configuration principale
# alembic/
#   env.py                 ← configuration Python (connexion, modèles)
#   script.py.mako         ← template pour les nouvelles migrations
#   versions/              ← dossier contenant les fichiers de migration
```

## Configuration alembic.ini

```ini
# alembic.ini
[alembic]
# Chemin vers le dossier de migrations
script_location = alembic

# Format du nom de fichier de migration
# %(rev)s = hash de révision, %(slug)s = nom donné
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# URL de connexion (peut être surchargée dans env.py)
# Mieux : utiliser une variable d'environnement
sqlalchemy.url = postgresql+psycopg2://formation:formation@localhost/orm_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

## Configuration env.py — la clé d'Alembic

C'est ici qu'on connecte Alembic à vos modèles SQLAlchemy pour l'autogenerate.

```python
# alembic/env.py
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# IMPORTANT : importer votre Base et tous vos modèles
# pour que Alembic puisse les comparer avec la BDD
from myapp.models import Base
import myapp.models  # Importer pour enregistrer tous les modèles dans Base.metadata

# Configuration Alembic
config = context.config

# Surcharger l'URL depuis la variable d'environnement
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Configurer les logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Connecter les métadonnées SQLAlchemy à Alembic (pour l'autogenerate)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Mode offline : génère du SQL sans connexion BDD."""
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
    """Mode online : applique les migrations directement."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Activer la détection des changements de type de colonnes
            compare_type=True,
            # Activer la détection des valeurs par défaut serveur
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Modèles SQLAlchemy (myapp/models.py)

```python
# myapp/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, func
from decimal import Decimal
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Categorie(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column()

class Produit(Base):
    __tablename__ = "produits"
    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200))
    prix: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

## Créer la première migration

```bash
# Générer une migration vide
alembic revision -m "create_initial_tables"

# OU générer automatiquement en comparant les modèles avec la BDD
alembic revision --autogenerate -m "create_initial_tables"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `alembic revision --autogenerate -m "create_initial_tables"` et montrer le fichier généré
> **Expliquer :** Montrer le fichier de migration auto-généré dans `alembic/versions/`. Expliquer les fonctions `upgrade()` et `downgrade()`. Montrer que l'autogenerate a correctement détecté toutes les tables, colonnes et contraintes. Insister : il faut **toujours** vérifier le fichier généré avant de l'appliquer — l'autogenerate peut rater certains changements.

---

## Fichier de migration auto-généré

```python
# alembic/versions/20240115_1200_create_initial_tables.py
"""create_initial_tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2024-01-15 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Identifiant unique de cette révision
revision: str = 'a1b2c3d4e5f6'
# Révision précédente (None = première migration)
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Applique les changements."""
    # Créer la table categories
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nom')
    )

    # Créer la table produits
    op.create_table(
        'produits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('prix', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('actif', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Annule les changements."""
    op.drop_table('produits')
    op.drop_table('categories')
```

## Appliquer les migrations

```bash
# Voir le statut actuel
alembic current

# Voir l'historique
alembic history
alembic history --verbose

# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer jusqu'à une révision spécifique
alembic upgrade a1b2c3d4e5f6

# Appliquer les N prochaines migrations
alembic upgrade +1
alembic upgrade +2
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `alembic upgrade head` et montrer la sortie, puis vérifier dans DBeaver
> **Expliquer :** Montrer la sortie d'Alembic qui liste les migrations appliquées. Aller dans DBeaver et montrer : 1) les tables créées, 2) la table `alembic_version` avec le hash de la dernière migration appliquée. Exécuter `alembic current` pour confirmer. Puis exécuter `alembic downgrade base` pour tout annuler et montrer que les tables disparaissent.

---

## Revenir en arrière (rollback)

```bash
# Annuler la dernière migration
alembic downgrade -1

# Revenir à une révision spécifique
alembic downgrade a1b2c3d4e5f6

# Annuler TOUTES les migrations (base = état initial)
alembic downgrade base
```
