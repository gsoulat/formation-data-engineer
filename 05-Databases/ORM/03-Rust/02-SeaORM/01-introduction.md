# SeaORM — Introduction et CRUD async

## Installation et configuration

```toml
# Cargo.toml
[dependencies]
sea-orm = { version = "0.12", features = [
    "sqlx-postgres",        # Driver PostgreSQL
    "runtime-tokio-rustls", # Async runtime
    "macros",               # Macros de dérivation
    "with-chrono",          # Support des types DateTime
    "with-bigdecimal",      # Support BigDecimal
] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
dotenvy = "0.15"
```

```bash
# Installer la CLI SeaORM
cargo install sea-orm-cli
```

## Connexion à la base de données

```rust
// src/db.rs
use sea_orm::{Database, DatabaseConnection, DbErr};

pub async fn connect() -> Result<DatabaseConnection, DbErr> {
    dotenvy::dotenv().ok();
    let database_url = std::env::var("DATABASE_URL")
        .expect("DATABASE_URL doit être définie");

    Database::connect(&database_url).await
}
```

## Définir les entités SeaORM

SeaORM utilise des entités avec des modules dédiés. Chaque entité est un module Rust.

```rust
// src/entities/categorie.rs
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "categories")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    #[sea_orm(unique)]
    pub nom: String,
    pub description: Option<String>,
    pub active: bool,
    pub created_at: ChronoDateTimeUtc,
}

// Définir les relations
#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::produit::Entity")]
    Produit,
}

impl Related<super::produit::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Produit.def()
    }
}

// Comportement actif (pour les insertions/mises à jour)
impl ActiveModelBehavior for ActiveModel {}
```

```rust
// src/entities/produit.rs
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Serialize, Deserialize)]
#[sea_orm(table_name = "produits")]
pub struct Model {
    #[sea_orm(primary_key)]
    pub id: i32,
    pub nom: String,
    pub description: Option<String>,
    #[sea_orm(column_type = "Decimal(Some((10, 2)))")]
    pub prix: Decimal,
    pub stock: i32,
    pub actif: bool,
    pub categorie_id: Option<i32>,
    pub created_at: ChronoDateTimeUtc,
    pub updated_at: ChronoDateTimeUtc,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::categorie::Entity",
        from = "Column::CategorieId",
        to = "super::categorie::Column::Id"
    )]
    Categorie,
}

impl Related<super::categorie::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::Categorie.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
```

## CRUD async complet

### CREATE

```rust
use sea_orm::{Set, ActiveModelTrait, EntityTrait};
use entities::produit;

async fn creer_produit(db: &DatabaseConnection) -> Result<produit::Model, DbErr> {
    // ActiveModel — modèle mutable pour INSERT/UPDATE
    let nouveau_produit = produit::ActiveModel {
        nom: Set("Clavier mécanique".to_owned()),
        description: Set(Some("Cherry MX Blue".to_owned())),
        prix: Set(Decimal::new(8999, 2)),  // 89.99
        stock: Set(15),
        actif: Set(true),
        categorie_id: Set(Some(1)),
        ..Default::default()  // id, created_at, updated_at auto
    };

    let produit_cree = nouveau_produit.insert(db).await?;
    println!("Créé: id={} nom={}", produit_cree.id, produit_cree.nom);
    Ok(produit_cree)
}
```

### READ

```rust
use sea_orm::{EntityTrait, QueryFilter, ColumnTrait, QueryOrder, QuerySelect};
use entities::produit::{self, Entity as Produit};

async fn exemples_select(db: &DatabaseConnection) -> Result<(), DbErr> {
    // Tous les enregistrements
    let tous: Vec<produit::Model> = Produit::find().all(db).await?;
    println!("Total: {}", tous.len());

    // Par ID
    let un: Option<produit::Model> = Produit::find_by_id(1).one(db).await?;
    if let Some(p) = un {
        println!("Trouvé: {}", p.nom);
    }

    // Avec filtre
    let actifs = Produit::find()
        .filter(produit::Column::Actif.eq(true))
        .order_by_asc(produit::Column::Prix)
        .all(db)
        .await?;

    // Filtres combinés
    use sea_orm::Condition;
    let selection = Produit::find()
        .filter(
            Condition::all()
                .add(produit::Column::Actif.eq(true))
                .add(produit::Column::Prix.lte(Decimal::new(10000, 2)))
        )
        .order_by_desc(produit::Column::Prix)
        .limit(10)
        .offset(0)
        .all(db)
        .await?;

    // LIKE
    let recherche = Produit::find()
        .filter(produit::Column::Nom.contains("clavier"))
        .all(db)
        .await?;

    // Compter
    let nb = Produit::find()
        .filter(produit::Column::Actif.eq(true))
        .count(db)
        .await?;
    println!("Produits actifs: {}", nb);

    Ok(())
}
```

### UPDATE

```rust
use sea_orm::{IntoActiveModel, Set, ActiveModelTrait};

async fn exemples_update(db: &DatabaseConnection) -> Result<(), DbErr> {
    // Méthode 1 : charger puis modifier
    let produit: produit::Model = Produit::find_by_id(1)
        .one(db)
        .await?
        .expect("Produit non trouvé");

    let mut produit_actif: produit::ActiveModel = produit.into_active_model();
    produit_actif.stock = Set(20);
    produit_actif.actif = Set(true);

    let produit_maj = produit_actif.update(db).await?;
    println!("Stock mis à jour: {}", produit_maj.stock);

    // Méthode 2 : update en masse (sans charger)
    use sea_orm::QueryFilter;

    let resultat = produit::Entity::update_many()
        .col_expr(produit::Column::Actif, Expr::value(false))
        .filter(produit::Column::Stock.eq(0))
        .exec(db)
        .await?;
    println!("{} produits désactivés", resultat.rows_affected);

    Ok(())
}
```

### DELETE

```rust
async fn exemples_delete(db: &DatabaseConnection) -> Result<(), DbErr> {
    // Supprimer par ID
    let resultat = Produit::delete_by_id(1).exec(db).await?;
    println!("{} supprimé(s)", resultat.rows_affected);

    // Supprimer avec filtre
    let resultat = produit::Entity::delete_many()
        .filter(produit::Column::Actif.eq(false))
        .filter(produit::Column::Stock.eq(0))
        .exec(db)
        .await?;
    println!("{} supprimés", resultat.rows_affected);

    Ok(())
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — `cargo run` avec le CRUD complet, montrer les logs SQL de SeaORM et les résultats
> **Expliquer :** Activer les logs SeaORM (`RUST_LOG=sea_orm=debug`) pour voir les requêtes SQL générées. Comparer avec Diesel : SeaORM est async (tout est `.await`), Diesel est sync. Montrer que SeaORM est mieux adapté à Axum/Actix web async. Discuter le trade-off : SeaORM = async + ergonomique vs Diesel = type-safety maximale à la compilation.

---

## Relations avec SeaORM

```rust
use sea_orm::{EntityTrait, QuerySelect, RelationTrait, JoinType};

async fn avec_relations(db: &DatabaseConnection) -> Result<(), DbErr> {
    // Charger un produit avec sa catégorie
    let produit_avec_cat = Produit::find_by_id(1)
        .find_also_related(categorie::Entity)
        .one(db)
        .await?;

    if let Some((produit, Some(cat))) = produit_avec_cat {
        println!("{} appartient à {}", produit.nom, cat.nom);
    }

    // Charger tous les produits avec leurs catégories
    let produits_cats: Vec<(produit::Model, Option<categorie::Model>)> = Produit::find()
        .find_also_related(categorie::Entity)
        .filter(produit::Column::Actif.eq(true))
        .all(db)
        .await?;

    for (p, cat_opt) in produits_cats {
        let cat_nom = cat_opt.map(|c| c.nom).unwrap_or("Sans catégorie".to_string());
        println!("{} — {} ({}€)", p.nom, cat_nom, p.prix);
    }

    // Charger les produits d'une catégorie
    use sea_orm::ModelTrait;
    let cat = categorie::Entity::find_by_id(1).one(db).await?.unwrap();
    let produits_de_cat = cat.find_related(Produit)
        .filter(produit::Column::Actif.eq(true))
        .all(db)
        .await?;

    println!("Produits dans '{}': {}", cat.nom, produits_de_cat.len());

    Ok(())
}
```

## Transactions SeaORM

```rust
use sea_orm::TransactionTrait;

async fn avec_transaction(db: &DatabaseConnection) -> Result<(), DbErr> {
    db.transaction::<_, (), DbErr>(|txn| {
        Box::pin(async move {
            // Toutes ces opérations sont dans la même transaction
            let p = produit::ActiveModel {
                nom: Set("Nouveau produit".to_owned()),
                prix: Set(Decimal::new(999, 2)),
                stock: Set(5),
                actif: Set(true),
                ..Default::default()
            }.insert(txn).await?;

            // Si cette opération échoue, tout est rollbacké
            produit::Entity::update_many()
                .col_expr(produit::Column::Stock, Expr::col(produit::Column::Stock).sub(1))
                .filter(produit::Column::Id.eq(2))
                .exec(txn)
                .await?;

            Ok(())
        })
    })
    .await?;

    Ok(())
}
```

## main.rs avec tokio

```rust
// src/main.rs
mod db;
mod entities;

use sea_orm::EntityTrait;

#[tokio::main]
async fn main() -> Result<(), sea_orm::DbErr> {
    dotenvy::dotenv().ok();

    // Activer les logs SQL
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();

    let db = db::connect().await?;
    println!("Connexion établie");

    // CRUD
    let tous = entities::produit::Entity::find().all(&db).await?;
    println!("Produits: {}", tous.len());

    Ok(())
}
```
