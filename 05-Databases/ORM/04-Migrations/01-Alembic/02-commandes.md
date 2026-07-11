# Alembic — Opérations avancées et CI/CD

## Opérations disponibles dans une migration

### Colonnes

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Ajouter une colonne
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

    # Ajouter avec valeur par défaut (pour NOT NULL sur table existante)
    op.add_column('produits',
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='FALSE')
    )

    # Modifier le type d'une colonne
    op.alter_column('produits', 'prix',
        existing_type=sa.Numeric(10, 2),
        type_=sa.Numeric(12, 2),    # Agrandir la précision
        existing_nullable=False
    )

    # Rendre une colonne NOT NULL (après avoir backfillé les données)
    op.execute("UPDATE users SET phone = '' WHERE phone IS NULL")
    op.alter_column('users', 'phone', nullable=False)

    # Renommer une colonne
    op.alter_column('users', 'phone', new_column_name='phone_number')

    # Supprimer une colonne
    op.drop_column('users', 'old_field')

def downgrade() -> None:
    op.drop_column('users', 'phone')
    op.drop_column('produits', 'archived')
```

### Index et contraintes

```python
def upgrade() -> None:
    # Créer un index simple
    op.create_index('idx_users_email', 'users', ['email'])

    # Index unique
    op.create_index('uq_users_email', 'users', ['email'], unique=True)

    # Index composite
    op.create_index('idx_produits_cat_actif', 'produits', ['categorie_id', 'actif'])

    # Index CONCURRENT (sans bloquer les lectures/écritures)
    # IMPORTANT : ne pas inclure dans une transaction (execute_args)
    op.execute(
        'CREATE INDEX CONCURRENTLY idx_produits_prix ON produits(prix)'
    )

    # Contrainte UNIQUE
    op.create_unique_constraint('uq_produit_sku', 'produits', ['sku'])

    # Contrainte CHECK
    op.create_check_constraint('ck_produit_prix_positif', 'produits', 'prix > 0')

    # Foreign Key
    op.create_foreign_key(
        'fk_produit_categorie',
        'produits', 'categories',
        ['categorie_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade() -> None:
    op.drop_constraint('fk_produit_categorie', 'produits', type_='foreignkey')
    op.drop_constraint('ck_produit_prix_positif', 'produits', type_='check')
    op.drop_constraint('uq_produit_sku', 'produits', type_='unique')
    op.drop_index('idx_produits_cat_actif', table_name='produits')
    op.drop_index('idx_users_email', table_name='users')
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal + DBeaver — exécuter une migration qui ajoute une colonne, puis montrer la colonne dans DBeaver
> **Expliquer :** Créer une migration qui ajoute `phone VARCHAR(20)` à la table `users`. Exécuter `alembic upgrade head`. Dans DBeaver, faire F5 (refresh) et montrer la nouvelle colonne. Puis `alembic downgrade -1` et montrer que la colonne disparaît. C'est la démonstration de la réversibilité des migrations.

---

### Tables

```python
def upgrade() -> None:
    # Créer une table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('lue', sa.Boolean(), nullable=False, server_default='FALSE'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifs_user', 'notifications', ['user_id'])

def downgrade() -> None:
    op.drop_index('idx_notifs_user', table_name='notifications')
    op.drop_table('notifications')
```

## Migration de données (data migration)

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Étape 1 : Créer la table de normalisation
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nom')
    )

    # Étape 2 : Ajouter la FK sur produits
    op.add_column('produits',
        sa.Column('categorie_id', sa.Integer(), nullable=True)
    )

    # Étape 3 : Migration de données (insérer les catégories uniques)
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO categories (nom)
        SELECT DISTINCT LOWER(TRIM(categorie_texte))
        FROM produits
        WHERE categorie_texte IS NOT NULL
        ORDER BY 1
    """))

    # Étape 4 : Remplir la FK
    conn.execute(sa.text("""
        UPDATE produits p
        SET categorie_id = c.id
        FROM categories c
        WHERE LOWER(TRIM(p.categorie_texte)) = c.nom
    """))

    # Étape 5 : Ajouter la contrainte FK
    op.create_foreign_key(
        'fk_produit_categorie',
        'produits', 'categories',
        ['categorie_id'], ['id']
    )

    # Optionnel : Supprimer l'ancienne colonne textuelle
    # (faire dans une migration séparée après avoir validé)
    # op.drop_column('produits', 'categorie_texte')

def downgrade() -> None:
    op.drop_constraint('fk_produit_categorie', 'produits', type_='foreignkey')
    op.drop_column('produits', 'categorie_id')
    op.drop_table('categories')
```

## Transactions dans les migrations

```python
def upgrade() -> None:
    # Par défaut, les migrations Alembic sont dans une transaction
    # Si une opération échoue → rollback automatique

    # Pour des opérations qui ne peuvent pas être dans une transaction
    # (comme CREATE INDEX CONCURRENTLY en PostgreSQL)
    op.execute(sa.text('COMMIT'))  # Valider ce qui est avant
    op.execute(sa.text('CREATE INDEX CONCURRENTLY idx_gros_index ON grande_table(colonne)'))
```

## Branches et merges (équipes)

Quand plusieurs développeurs travaillent en parallèle :

```bash
# Développeur A crée sa migration
alembic revision -m "add_user_avatar"
# → revision: abc123, down_revision: xyz789

# Développeur B crée la sienne en même temps
alembic revision -m "add_product_weight"
# → revision: def456, down_revision: xyz789

# Les deux ont le même down_revision → branches divergentes
alembic history
#  abc123 -> (head)  add_user_avatar
#  def456 -> (head)  add_product_weight
#  xyz789 -> (branchpoint)

# Merger les branches
alembic merge -m "merge_user_and_product_changes" abc123 def456
# Crée une migration de merge : révision qui a deux down_revision

alembic history
#  ghi789 -> (head)  merge_user_and_product_changes
#  abc123 -> ghi789
#  def456 -> ghi789
#  xyz789 -> abc123, def456
```

## Intégration CI/CD

### Script de migration en production

```python
# scripts/migrate.py
import subprocess
import sys
from sqlalchemy import create_engine, text
import os

def run_migrations():
    """Exécute les migrations Alembic et vérifie le résultat."""
    database_url = os.environ["DATABASE_URL"]

    # Vérifier la connexion BDD avant de migrer
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connexion BDD OK")
    except Exception as e:
        print(f"Impossible de se connecter à la BDD: {e}")
        sys.exit(1)

    # Exécuter alembic upgrade head
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"ERREUR de migration:\n{result.stderr}")
        sys.exit(1)

    print(f"Migrations appliquées avec succès:\n{result.stdout}")

if __name__ == "__main__":
    run_migrations()
```

### Makefile

```makefile
# Makefile
.PHONY: migrate migrate-check migrate-rollback

migrate:
	alembic upgrade head

migrate-check:
	alembic check  # Vérifie si des migrations sont en attente

migrate-rollback:
	alembic downgrade -1

migrate-history:
	alembic history --verbose

migrate-current:
	alembic current
```

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  migrate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: alembic upgrade head

      - name: Deploy application
        run: ./deploy.sh
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — simuler un pipeline CI/CD complet : écrire un modèle, générer la migration, l'appliquer, vérifier dans DBeaver
> **Expliquer :** Faire le workflow complet en direct : 1) Ajouter une colonne `tags` à un modèle SQLAlchemy, 2) `alembic revision --autogenerate -m "add_tags"`, 3) vérifier le fichier généré, 4) `alembic upgrade head`, 5) DBeaver montre la colonne. Puis faire le rollback. Insister : ce workflow est identique en dev, staging et prod.

---

## Checklist avant de déployer une migration en prod

```
□ La migration a été testée en dev
□ La migration a été testée avec les données de prod (snapshot)
□ Le downgrade a été testé et fonctionne
□ La migration est dans Git (avec le code applicatif)
□ Un backup de la BDD de prod a été créé
□ La migration est dans une transaction (atomic)
□ Les opérations dangereuses sont coordonnées avec le déploiement du code
□ L'équipe est informée (pas de migration à l'improviste)
□ Un plan de rollback est prêt
```
