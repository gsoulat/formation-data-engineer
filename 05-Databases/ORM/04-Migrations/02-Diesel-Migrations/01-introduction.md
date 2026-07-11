# Diesel Migrations — Introduction et workflow

## Setup initial

```bash
# Prérequis : PostgreSQL en cours d'exécution
# Créer le fichier .env
echo DATABASE_URL=postgres://formation:formation@localhost/orm_db > .env

# Initialiser Diesel (crée migrations/ et diesel.toml)
diesel setup

# Structure créée :
# .env
# diesel.toml                    ← configuration Diesel
# migrations/                    ← dossier des migrations
#   .gitkeep                     ← pour Git

# La BDD est maintenant créée avec la table de tracking
# (__diesel_schema_migrations)
```

## Créer une migration

```bash
# Créer une nouvelle migration (crée un dossier avec up.sql et down.sql)
diesel migration generate create_initial_tables

# Structure créée :
# migrations/
#   2024-01-15-120000_create_initial_tables/
#     up.sql     ← applique le changement
#     down.sql   ← annule le changement
```

## Écrire les fichiers SQL

```sql
-- migrations/2024-01-15-120000_create_initial_tables/up.sql

-- Table categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table produits
CREATE TABLE produits (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    prix NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    categorie_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_produit_prix_positif CHECK (prix > 0),
    CONSTRAINT ck_produit_stock_positif CHECK (stock >= 0)
);

-- Index
CREATE INDEX idx_produits_actif ON produits(actif);
CREATE INDEX idx_produits_categorie ON produits(categorie_id);
CREATE INDEX idx_produits_prix ON produits(prix);
```

```sql
-- migrations/2024-01-15-120000_create_initial_tables/down.sql
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS categories;
```

## Commandes Diesel CLI

```bash
# Appliquer toutes les migrations en attente
diesel migration run

# Voir le statut des migrations
diesel migration list

# Annuler la dernière migration
diesel migration revert

# Annuler ET réappliquer (dev)
diesel migration redo

# Tester le redo (annule puis réapplique sans garder les changements)
diesel migration redo --all

# Générer/régénérer src/schema.rs
diesel print-schema
diesel print-schema > src/schema.rs
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `diesel migration run`, montrer la sortie et le fichier `schema.rs` généré, puis vérifier dans DBeaver
> **Expliquer :** Montrer les étapes : 1) `diesel migration run` applique le SQL, 2) `diesel print-schema` génère `schema.rs`. Montrer la table `__diesel_schema_migrations` dans DBeaver avec les migrations listées. Comparer avec la table `alembic_version` vue dans Alembic. Exécuter `diesel migration revert` puis `diesel migration run` pour montrer la réversibilité.

---

## Deuxième migration — ajouter une colonne

```bash
diesel migration generate add_tags_to_produits
```

```sql
-- up.sql
ALTER TABLE produits ADD COLUMN tags TEXT[] DEFAULT '{}';
CREATE INDEX idx_produits_tags ON produits USING GIN(tags);
```

```sql
-- down.sql
DROP INDEX IF EXISTS idx_produits_tags;
ALTER TABLE produits DROP COLUMN IF EXISTS tags;
```

```bash
diesel migration run
# → src/schema.rs est automatiquement mis à jour !
```

## Exemple de migration complexe

```bash
diesel migration generate normalize_categories
```

```sql
-- up.sql — Normaliser la colonne categorie_texte vers une FK
BEGIN;

-- 1. Créer la table categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Peupler avec les catégories existantes
INSERT INTO categories (nom)
SELECT DISTINCT LOWER(TRIM(categorie_texte))
FROM produits
WHERE categorie_texte IS NOT NULL
  AND categorie_texte != '';

-- 3. Ajouter la colonne FK
ALTER TABLE produits ADD COLUMN categorie_id INTEGER;

-- 4. Remplir la FK
UPDATE produits p
SET categorie_id = c.id
FROM categories c
WHERE LOWER(TRIM(p.categorie_texte)) = c.nom;

-- 5. Ajouter la contrainte FK
ALTER TABLE produits
ADD CONSTRAINT fk_produit_categorie
FOREIGN KEY (categorie_id) REFERENCES categories(id) ON DELETE SET NULL;

COMMIT;
```

```sql
-- down.sql
BEGIN;
ALTER TABLE produits DROP CONSTRAINT IF EXISTS fk_produit_categorie;
ALTER TABLE produits DROP COLUMN IF EXISTS categorie_id;
DROP TABLE IF EXISTS categories;
COMMIT;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal + DBeaver — exécuter la migration de normalisation, montrer les données avant et après dans DBeaver
> **Expliquer :** Avant la migration, insérer quelques produits avec `categorie_texte = 'informatique'`. Exécuter la migration et montrer dans DBeaver : 1) la table `categories` créée et peuplée, 2) la colonne `categorie_id` avec les FK correctement remplies, 3) la contrainte FK dans la structure de la table. C'est un exemple de data migration réelle.

---

## Embarquer les migrations dans le binaire Rust

Une fonctionnalité unique de Diesel : les migrations peuvent être compilées dans le binaire. Cela permet de déployer un seul binaire qui s'auto-migrate.

```toml
# Cargo.toml
[dependencies]
diesel = { version = "2.1", features = ["postgres"] }
diesel_migrations = "2.1"
```

```rust
// src/main.rs
use diesel::pg::PgConnection;
use diesel::Connection;
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};

// Embarquer toutes les migrations dans le binaire à la compilation
pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("migrations");

fn main() {
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL doit être définie");

    let mut conn = PgConnection::establish(&database_url)
        .expect("Impossible de se connecter à la BDD");

    // Appliquer les migrations au démarrage
    println!("Application des migrations...");
    conn.run_pending_migrations(MIGRATIONS)
        .expect("Erreur lors des migrations");
    println!("Migrations appliquées avec succès");

    // Votre application continue ici...
}
```

```bash
# La compilation embarque les fichiers SQL dans le binaire
cargo build --release

# Le binaire contient maintenant les migrations
# Pas besoin de diesel_cli en production !
./target/release/mon-app
# → "Application des migrations..."
# → "Migrations appliquées avec succès"
# → Application démarre
```

## Comparaison détaillée Alembic vs Diesel Migrations

| Critère | Alembic | Diesel Migrations |
|---------|---------|-------------------|
| Langage de migration | Python ou SQL | SQL pur |
| Autogenerate | Oui (depuis modèles) | Non |
| Schema.rs | N/A | Regénéré automatiquement |
| Embeddable | Non | Oui |
| Rollback granulaire | Oui | Un seul niveau |
| Branches/Merges | Oui | Non |
| CI/CD | Script Python | Binaire auto-migrate |
| Complexité des scripts | Haute (Python) | Faible (SQL) |
| Portabilité SGBD | Haute (abstraction) | Faible (SQL spécifique) |

**Quand utiliser Diesel Migrations** :
- Projet Rust avec Diesel
- Vous préférez écrire du SQL pur
- Vous voulez embarquer les migrations dans le binaire
- Déploiement simple (un seul binaire)

**Quand utiliser Alembic** :
- Projet Python avec SQLAlchemy/SQLModel
- Vous voulez l'autogenerate
- Vous avez des équipes avec des migrations parallèles
- Vous avez besoin de migrations de données complexes en Python
