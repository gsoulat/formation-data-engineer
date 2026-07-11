# SeaORM — Entités dérivées et migrations

## Générer les entités depuis une BDD existante

SeaORM peut générer automatiquement les entités à partir du schéma d'une base de données existante.

```bash
# Installer la CLI
cargo install sea-orm-cli

# Générer les entités depuis la BDD
sea-orm-cli generate entity \
  --database-url "postgres://formation:formation@localhost/orm_db" \
  --output-dir src/entities \
  --with-serde both \   # Génère les derives Serialize et Deserialize
  --date-time-crate chrono

# Résultat : src/entities/
# ├── mod.rs
# ├── prelude.rs
# ├── produit.rs
# ├── categorie.rs
# └── ...
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `sea-orm-cli generate entity` et montrer les fichiers générés
> **Expliquer :** Comparer l'approche SeaORM (génération à partir de la BDD) avec Diesel (génération du `schema.rs` + modèles manuels). Montrer le contenu d'une entité générée et expliquer chaque partie : `Model`, `ActiveModel`, `Column`, `Relation`. Insister sur le fait que les deux approches (code first vs database first) sont valides selon le contexte.

---

## Structure d'une entité générée

```rust
// src/entities/produit.rs (généré par sea-orm-cli)
use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

// Model — représentation lecture (SELECT)
#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq, Serialize, Deserialize)]
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
    pub created_at: DateTimeWithTimeZone,
    pub updated_at: DateTimeWithTimeZone,
}

// Entity — le type qui identifie la table
pub struct Entity;
impl EntityName for Entity {
    fn table_name(&self) -> &str { "produits" }
}

// Columns — enum de toutes les colonnes (type-safe)
#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum Column {
    Id, Nom, Description, Prix, Stock, Actif, CategorieId, CreatedAt, UpdatedAt,
}

// PrimaryKey
#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKey { Id }

// Relation — déclare les FK
#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::categorie::Entity",
        from = "Column::CategorieId",
        to = "super::categorie::Column::Id",
        on_update = "NoAction",
        on_delete = "SetNull"
    )]
    Categorie,
}

impl Related<super::categorie::Entity> for Entity {
    fn to() -> RelationDef { Relation::Categorie.def() }
}

// ActiveModel — représentation mutable (INSERT/UPDATE)
// Généré automatiquement depuis Model
impl ActiveModelBehavior for ActiveModel {
    // On peut surcharger before_save et after_save
    fn before_save<C>(self, db: &C, insert: bool) -> Pin<Box<dyn Future<Output = Result<Self, DbErr>> + Send + '_>>
    where C: ConnectionTrait
    {
        Box::pin(async move {
            let mut this = self;
            if !insert {
                // Mettre à jour updated_at avant chaque save
                this.updated_at = Set(chrono::Utc::now().into());
            }
            Ok(this)
        })
    }
}
```

## Migrations avec SeaORM

SeaORM a son propre système de migrations basé sur du code Rust (pas du SQL pur).

```bash
# Créer une migration
sea-orm-cli migrate generate create_produits

# Cela crée : migration/src/m20240115_120000_create_produits.rs
```

```rust
// migration/src/m20240115_120000_create_produits.rs
use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Créer la table categories
        manager.create_table(
            Table::create()
                .table(Categories::Table)
                .if_not_exists()
                .col(
                    ColumnDef::new(Categories::Id)
                        .integer()
                        .not_null()
                        .auto_increment()
                        .primary_key()
                )
                .col(
                    ColumnDef::new(Categories::Nom)
                        .string_len(100)
                        .not_null()
                        .unique_key()
                )
                .col(ColumnDef::new(Categories::Description).text())
                .col(
                    ColumnDef::new(Categories::Active)
                        .boolean()
                        .not_null()
                        .default(true)
                )
                .col(
                    ColumnDef::new(Categories::CreatedAt)
                        .timestamp_with_time_zone()
                        .not_null()
                        .default(Expr::current_timestamp())
                )
                .to_owned()
        ).await?;

        // Créer la table produits
        manager.create_table(
            Table::create()
                .table(Produits::Table)
                .if_not_exists()
                .col(
                    ColumnDef::new(Produits::Id)
                        .integer()
                        .not_null()
                        .auto_increment()
                        .primary_key()
                )
                .col(
                    ColumnDef::new(Produits::Nom)
                        .string_len(200)
                        .not_null()
                )
                .col(ColumnDef::new(Produits::Description).text())
                .col(
                    ColumnDef::new(Produits::Prix)
                        .decimal_len(10, 2)
                        .not_null()
                )
                .col(
                    ColumnDef::new(Produits::Stock)
                        .integer()
                        .not_null()
                        .default(0)
                )
                .col(
                    ColumnDef::new(Produits::Actif)
                        .boolean()
                        .not_null()
                        .default(true)
                )
                .col(ColumnDef::new(Produits::CategorieId).integer())
                .col(
                    ColumnDef::new(Produits::CreatedAt)
                        .timestamp_with_time_zone()
                        .not_null()
                        .default(Expr::current_timestamp())
                )
                .col(
                    ColumnDef::new(Produits::UpdatedAt)
                        .timestamp_with_time_zone()
                        .not_null()
                        .default(Expr::current_timestamp())
                )
                // Foreign Key
                .foreign_key(
                    ForeignKey::create()
                        .name("fk_produit_categorie")
                        .from(Produits::Table, Produits::CategorieId)
                        .to(Categories::Table, Categories::Id)
                        .on_delete(ForeignKeyAction::SetNull)
                )
                .to_owned()
        ).await?;

        // Créer les index
        manager.create_index(
            Index::create()
                .name("idx_produits_actif")
                .table(Produits::Table)
                .col(Produits::Actif)
                .to_owned()
        ).await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager.drop_table(Table::drop().table(Produits::Table).to_owned()).await?;
        manager.drop_table(Table::drop().table(Categories::Table).to_owned()).await?;
        Ok(())
    }
}

// Identifiants des tables et colonnes
#[derive(Iden)]
enum Categories {
    Table, Id, Nom, Description, Active, CreatedAt,
}

#[derive(Iden)]
enum Produits {
    Table, Id, Nom, Description, Prix, Stock, Actif, CategorieId, CreatedAt, UpdatedAt,
}
```

## Enregistrer et exécuter les migrations

```rust
// migration/src/lib.rs
pub use sea_orm_migration::prelude::*;

mod m20240115_120000_create_produits;
mod m20240116_093000_add_index_prix;  // Exemple d'une deuxième migration

pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20240115_120000_create_produits::Migration),
            Box::new(m20240116_093000_add_index_prix::Migration),
        ]
    }
}
```

```bash
# Appliquer toutes les migrations en attente
sea-orm-cli migrate up

# Annuler la dernière migration
sea-orm-cli migrate down

# Statut des migrations
sea-orm-cli migrate status

# Annuler toutes les migrations
sea-orm-cli migrate reset

# Annuler et réappliquer (dev)
sea-orm-cli migrate fresh
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — exécuter `sea-orm-cli migrate up` puis `migrate status`, montrer la table `seaql_migrations` dans DBeaver
> **Expliquer :** Montrer la table de tracking des migrations (`seaql_migrations` pour SeaORM vs `__diesel_schema_migrations` pour Diesel vs `alembic_version` pour Python/Alembic). Insister sur le concept commun : tous les ORMs gardent un historique des migrations appliquées. Exécuter `migrate down` puis `migrate up` pour montrer la réversibilité.

---

## Comparaison SeaORM vs Diesel

```
DIESEL
  Avantages :
  + Type-safety maximale à la compilation
  + Pas de runtime overhead
  + Très mature et stable
  + Excellent pour les applications sync

  Inconvénients :
  - Pas d'async natif
  - Verbeux (schema.rs + modèles séparés)
  - Courbe d'apprentissage plus élevée

SEAORM
  Avantages :
  + Async natif (excellent avec Axum/Actix)
  + API plus ergonomique
  + Génération d'entités depuis la BDD
  + Migrations en Rust (pas de SQL pur)

  Inconvénients :
  - Moins de garanties compile-time que Diesel
  - Plus récent, moins de recul en production
  - Dépend de SQLx (couche supplémentaire)
```

**Recommandation** :
- Application web async (Axum, Actix-web) → **SeaORM**
- Application CLI/batch/sync → **Diesel**
- Performances maximales et type-safety → **Diesel**
- Nouveau projet avec besoin d'async → **SeaORM**
