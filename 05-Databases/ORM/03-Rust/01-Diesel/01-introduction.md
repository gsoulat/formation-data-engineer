# Diesel — Introduction et setup

## Initialiser un projet Diesel

```bash
# Créer le projet Rust
cargo new diesel-demo
cd diesel-demo

# Configurer la connexion
echo DATABASE_URL=postgres://formation:formation@localhost/orm_db > .env

# Initialiser Diesel (crée migrations/ et diesel.toml)
diesel setup

# Vérifier la connexion
diesel database reset  # Supprime et recrée la BDD
```

## Cargo.toml

```toml
[package]
name = "diesel-demo"
version = "0.1.0"
edition = "2021"

[dependencies]
diesel = { version = "2.1", features = ["postgres", "chrono", "r2d2"] }
dotenvy = "0.15"
chrono = { version = "0.4", features = ["serde"] }
serde = { version = "1", features = ["derive"] }
```

## Créer une migration

```bash
# Créer la migration
diesel migration generate create_produits

# Cela crée deux fichiers :
# migrations/2024-01-15-120000_create_produits/up.sql
# migrations/2024-01-15-120000_create_produits/down.sql
```

```sql
-- migrations/2024-01-15-120000_create_produits/up.sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE produits (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    prix NUMERIC(10, 2) NOT NULL CHECK (prix > 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    categorie_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_produits_actif ON produits(actif);
CREATE INDEX idx_produits_categorie ON produits(categorie_id);
```

```sql
-- migrations/2024-01-15-120000_create_produits/down.sql
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS categories;
```

```bash
# Appliquer la migration
diesel migration run

# Cette commande crée aussi src/schema.rs automatiquement !
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `diesel migration run` et montrer le fichier `src/schema.rs` généré
> **Expliquer :** Montrer le fichier `schema.rs` auto-généré par Diesel. Expliquer que ce fichier représente le schéma de la BDD en types Rust. Insister : ce fichier ne se modifie PAS manuellement — il est regénéré à chaque migration. Montrer aussi le contenu de la table `__diesel_schema_migrations` dans DBeaver.

---

## src/schema.rs (généré automatiquement)

```rust
// src/schema.rs — GÉNÉRÉ par diesel migration run — NE PAS MODIFIER
// @generated automatically by Diesel CLI.

diesel::table! {
    categories (id) {
        id -> Int4,
        nom -> Varchar,
        description -> Nullable<Text>,
        active -> Bool,
        created_at -> Timestamp,
    }
}

diesel::table! {
    produits (id) {
        id -> Int4,
        nom -> Varchar,
        description -> Nullable<Text>,
        prix -> Numeric,
        stock -> Int4,
        actif -> Bool,
        categorie_id -> Nullable<Int4>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::joinable!(produits -> categories (categorie_id));

diesel::allow_tables_to_appear_in_same_query!(
    categories,
    produits,
);
```

## Définir les modèles Rust

```rust
// src/models.rs
use diesel::prelude::*;
use chrono::NaiveDateTime;
use serde::{Deserialize, Serialize};
use crate::schema::{produits, categories};

// Modèle de lecture (SELECT)
#[derive(Debug, Serialize, Queryable, Selectable, Identifiable)]
#[diesel(table_name = produits)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Produit {
    pub id: i32,
    pub nom: String,
    pub description: Option<String>,
    pub prix: bigdecimal::BigDecimal,
    pub stock: i32,
    pub actif: bool,
    pub categorie_id: Option<i32>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}

// Modèle d'insertion (INSERT)
#[derive(Debug, Deserialize, Insertable)]
#[diesel(table_name = produits)]
pub struct NouveauProduit {
    pub nom: String,
    pub description: Option<String>,
    pub prix: bigdecimal::BigDecimal,
    pub stock: i32,
    pub categorie_id: Option<i32>,
}

// Modèle de mise à jour (UPDATE)
#[derive(Debug, Deserialize, AsChangeset)]
#[diesel(table_name = produits)]
pub struct ProduitMaj {
    pub nom: Option<String>,
    pub description: Option<Option<String>>,  // Option<Option<T>> pour allow NULL
    pub prix: Option<bigdecimal::BigDecimal>,
    pub stock: Option<i32>,
    pub actif: Option<bool>,
}

// Modèle Categorie
#[derive(Debug, Serialize, Queryable, Selectable, Identifiable)]
#[diesel(table_name = categories)]
pub struct Categorie {
    pub id: i32,
    pub nom: String,
    pub description: Option<String>,
    pub active: bool,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = categories)]
pub struct NouvelleCategorie<'a> {
    pub nom: &'a str,
    pub description: Option<&'a str>,
}
```

## Connexion à PostgreSQL

```rust
// src/db.rs
use diesel::pg::PgConnection;
use diesel::r2d2::{self, ConnectionManager};
use std::env;

pub type Pool = r2d2::Pool<ConnectionManager<PgConnection>>;
pub type DbConnection = r2d2::PooledConnection<ConnectionManager<PgConnection>>;

pub fn create_pool() -> Pool {
    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL doit être définie dans .env");

    let manager = ConnectionManager::<PgConnection>::new(database_url);

    r2d2::Pool::builder()
        .max_size(10)
        .min_idle(Some(2))
        .build(manager)
        .expect("Impossible de créer le pool de connexions")
}

// Connexion simple (sans pool)
pub fn establish_connection() -> PgConnection {
    dotenvy::dotenv().ok();
    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL doit être définie");
    PgConnection::establish(&database_url)
        .unwrap_or_else(|_| panic!("Erreur de connexion à {}", database_url))
}
```

## main.rs — point d'entrée

```rust
// src/main.rs
mod db;
mod models;
mod schema;

use diesel::prelude::*;
use dotenvy::dotenv;

fn main() {
    dotenv().ok();

    let mut conn = db::establish_connection();
    println!("Connexion établie !");

    // Démonstration CRUD
    demo_crud(&mut conn);
}

fn demo_crud(conn: &mut PgConnection) {
    use schema::produits::dsl::*;
    use models::{Produit, NouveauProduit};

    // INSERT
    let nouveau = NouveauProduit {
        nom: String::from("Clavier mécanique"),
        description: Some(String::from("Clavier Cherry MX Blue")),
        prix: bigdecimal::BigDecimal::from(8999u32) / bigdecimal::BigDecimal::from(100u32),
        stock: 15,
        categorie_id: None,
    };

    let produit_cree: Produit = diesel::insert_into(produits)
        .values(&nouveau)
        .get_result(conn)
        .expect("Erreur lors de l'insertion");

    println!("Créé: {:?}", produit_cree);

    // SELECT
    let tous_produits: Vec<Produit> = produits
        .filter(actif.eq(true))
        .order(nom.asc())
        .load(conn)
        .expect("Erreur lors de la sélection");

    println!("Produits actifs: {}", tous_produits.len());

    // UPDATE
    let produit_maj = diesel::update(produits.find(produit_cree.id))
        .set(stock.eq(20))
        .get_result::<Produit>(conn)
        .expect("Erreur lors de la mise à jour");

    println!("Stock mis à jour: {}", produit_maj.stock);

    // DELETE
    let nb_suppr = diesel::delete(produits.find(produit_cree.id))
        .execute(conn)
        .expect("Erreur lors de la suppression");

    println!("Supprimés: {}", nb_suppr);
}
```
