# Diesel — Requêtes et opérations avancées

## Import des DSL

```rust
// Importer les symboles nécessaires
use diesel::prelude::*;
use schema::produits::dsl::*;
// Cela importe : produits (table), id, nom, prix, stock, actif, etc.
// Chaque colonne devient une variable Rust typée
```

## SELECT — lire des données

```rust
use diesel::prelude::*;
use schema::produits::dsl::*;
use models::Produit;

fn exemples_select(conn: &mut PgConnection) {
    // Tous les enregistrements
    let tous: Vec<Produit> = produits
        .load(conn)
        .expect("Erreur de chargement");

    // Avec filtre simple
    let actifs: Vec<Produit> = produits
        .filter(actif.eq(true))
        .load(conn)
        .expect("Erreur");

    // Filtres combinés
    let selection: Vec<Produit> = produits
        .filter(actif.eq(true))
        .filter(prix.le(bigdecimal::BigDecimal::from(100u32)))
        .order(prix.asc())
        .load(conn)
        .expect("Erreur");

    // Opérateurs disponibles
    // .eq(val)     →  =
    // .ne(val)     →  !=
    // .gt(val)     →  >
    // .ge(val)     →  >=
    // .lt(val)     →  <
    // .le(val)     →  <=
    // .like(pat)   →  LIKE
    // .ilike(pat)  →  ILIKE (PostgreSQL case-insensitive)
    // .is_null()   →  IS NULL
    // .is_not_null() → IS NOT NULL
    // .eq_any(vec) →  IN (...)

    // LIKE
    let recherche: Vec<Produit> = produits
        .filter(nom.ilike("%clavier%"))
        .load(conn)
        .expect("Erreur");

    // IN
    let par_ids: Vec<Produit> = produits
        .filter(id.eq_any(vec![1, 2, 3]))
        .load(conn)
        .expect("Erreur");

    // IS NULL
    let sans_categorie: Vec<Produit> = produits
        .filter(categorie_id.is_null())
        .load(conn)
        .expect("Erreur");

    // Pagination
    let page_2: Vec<Produit> = produits
        .order(id.asc())
        .offset(10)
        .limit(10)
        .load(conn)
        .expect("Erreur");

    // Un seul enregistrement
    let un_produit: Option<Produit> = produits
        .find(1)  // WHERE id = 1
        .first(conn)
        .optional()
        .expect("Erreur");

    // Avec select — colonnes spécifiques
    let noms_prix: Vec<(String, bigdecimal::BigDecimal)> = produits
        .select((nom, prix))
        .filter(actif.eq(true))
        .load(conn)
        .expect("Erreur");
}
```

## Agrégations

```rust
use diesel::dsl::{count, sum, avg, min, max};

fn exemples_agregations(conn: &mut PgConnection) {
    use schema::produits::dsl::*;

    // COUNT
    let total: i64 = produits
        .count()
        .get_result(conn)
        .expect("Erreur");
    println!("Total produits: {}", total);

    // COUNT avec filtre
    let nb_actifs: i64 = produits
        .filter(actif.eq(true))
        .count()
        .get_result(conn)
        .expect("Erreur");

    // SUM
    let stock_total: Option<i64> = produits
        .select(sum(stock))
        .first(conn)
        .expect("Erreur");

    // MAX, MIN
    let prix_max: Option<bigdecimal::BigDecimal> = produits
        .select(max(prix))
        .first(conn)
        .expect("Erreur");

    println!("Stock total: {:?}, Prix max: {:?}", stock_total, prix_max);
}
```

## INSERT

```rust
use models::NouveauProduit;

fn exemples_insert(conn: &mut PgConnection) {
    use schema::produits::dsl::*;

    // Insertion simple avec retour de l'enregistrement créé
    let nouveau = NouveauProduit {
        nom: String::from("Souris sans fil"),
        description: Some(String::from("Logitech MX Master 3")),
        prix: bigdecimal::BigDecimal::from(2999u32) / bigdecimal::BigDecimal::from(100u32),
        stock: 50,
        categorie_id: Some(1),
    };

    let cree: models::Produit = diesel::insert_into(produits)
        .values(&nouveau)
        .get_result(conn)
        .expect("Erreur d'insertion");
    println!("Créé: id={}, nom={}", cree.id, cree.nom);

    // Insertion multiple
    let nouveaux = vec![
        NouveauProduit {
            nom: String::from("Webcam HD"),
            description: None,
            prix: bigdecimal::BigDecimal::from(7999u32) / bigdecimal::BigDecimal::from(100u32),
            stock: 25,
            categorie_id: Some(1),
        },
        NouveauProduit {
            nom: String::from("Casque audio"),
            description: Some(String::from("Sony WH-1000XM5")),
            prix: bigdecimal::BigDecimal::from(14900u32) / bigdecimal::BigDecimal::from(100u32),
            stock: 12,
            categorie_id: Some(2),
        },
    ];

    let nb_inseres = diesel::insert_into(produits)
        .values(&nouveaux)
        .execute(conn)
        .expect("Erreur d'insertion bulk");
    println!("{} produits insérés", nb_inseres);

    // Upsert — INSERT ... ON CONFLICT DO UPDATE
    use diesel::pg::upsert::excluded;

    diesel::insert_into(produits)
        .values(&nouveau)
        .on_conflict(nom)
        .do_update()
        .set((
            stock.eq(excluded(stock)),
            actif.eq(true),
        ))
        .execute(conn)
        .expect("Erreur upsert");
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal — `cargo run` avec les insertions et sélections, montrer les résultats dans le terminal et les données dans DBeaver
> **Expliquer :** Montrer que le compilateur Rust détecte les erreurs de type avant l'exécution. Introduire volontairement une erreur (ex: passer un `String` là où un `i32` est attendu) et montrer l'erreur de compilation. Insister : avec Diesel, si ça compile, les types SQL correspondent aux types Rust.

---

## UPDATE

```rust
use models::ProduitMaj;

fn exemples_update(conn: &mut PgConnection) {
    use schema::produits::dsl::*;

    // Mise à jour d'un champ
    let nb_modifies = diesel::update(produits.find(1))
        .set(stock.eq(20))
        .execute(conn)
        .expect("Erreur de mise à jour");
    println!("{} produit(s) mis à jour", nb_modifies);

    // Mise à jour de plusieurs champs avec AsChangeset
    let maj = ProduitMaj {
        nom: None,
        description: None,
        prix: Some(bigdecimal::BigDecimal::from(7999u32) / bigdecimal::BigDecimal::from(100u32)),
        stock: Some(15),
        actif: None,
    };

    let produit_maj: models::Produit = diesel::update(produits.find(1))
        .set(&maj)
        .get_result(conn)
        .expect("Erreur");
    println!("Mis à jour: {:?}", produit_maj);

    // Mise à jour en masse
    let nb = diesel::update(produits.filter(stock.eq(0)))
        .set(actif.eq(false))
        .execute(conn)
        .expect("Erreur");
    println!("{} produits sans stock désactivés", nb);

    // Incrémenter une valeur
    diesel::update(produits.find(1))
        .set(stock.eq(stock + 1))
        .execute(conn)
        .expect("Erreur");
}
```

## DELETE

```rust
fn exemples_delete(conn: &mut PgConnection) {
    use schema::produits::dsl::*;

    // Supprimer par ID
    let nb = diesel::delete(produits.find(1))
        .execute(conn)
        .expect("Erreur de suppression");
    println!("{} supprimé(s)", nb);

    // Suppression en masse avec condition
    let nb = diesel::delete(
        produits.filter(actif.eq(false)).filter(stock.eq(0))
    )
    .execute(conn)
    .expect("Erreur");
    println!("{} produits supprimés", nb);
}
```

## JOIN entre tables

```rust
use schema::{produits, categories};

fn exemples_join(conn: &mut PgConnection) {
    // Inner join produits → categories
    let resultats: Vec<(models::Produit, models::Categorie)> = produits::table
        .inner_join(categories::table)
        .filter(produits::actif.eq(true))
        .order(produits::prix.asc())
        .load(conn)
        .expect("Erreur");

    for (produit, categorie) in resultats {
        println!("{} — {} ({}€)", produit.nom, categorie.nom, produit.prix);
    }

    // Left join (inclut les produits sans catégorie)
    let resultats_left: Vec<(models::Produit, Option<models::Categorie>)> = produits::table
        .left_join(categories::table)
        .filter(produits::actif.eq(true))
        .load(conn)
        .expect("Erreur");

    for (produit, categorie_opt) in resultats_left {
        let cat_nom = categorie_opt
            .map(|c| c.nom)
            .unwrap_or_else(|| String::from("Sans catégorie"));
        println!("{} — {}", produit.nom, cat_nom);
    }
}
```

## SQL brut avec Diesel

```rust
use diesel::sql_query;
use diesel::sql_types::{Text, Integer};

fn requete_sql_brute(conn: &mut PgConnection) {
    #[derive(QueryableByName, Debug)]
    struct StatCategorie {
        #[diesel(sql_type = Text)]
        categorie_nom: String,
        #[diesel(sql_type = Integer)]
        nb_produits: i32,
    }

    let stats: Vec<StatCategorie> = sql_query(
        "SELECT c.nom AS categorie_nom, COUNT(p.id)::int AS nb_produits
         FROM categories c
         LEFT JOIN produits p ON p.categorie_id = c.id AND p.actif = TRUE
         GROUP BY c.id, c.nom
         ORDER BY nb_produits DESC"
    )
    .load(conn)
    .expect("Erreur");

    for s in stats {
        println!("{}: {} produits", s.categorie_nom, s.nb_produits);
    }
}
```

## Transactions

```rust
use diesel::Connection;

fn avec_transaction(conn: &mut PgConnection) {
    conn.transaction::<_, diesel::result::Error, _>(|conn| {
        use schema::produits::dsl::*;

        // Toutes ces opérations sont dans la même transaction
        let p1 = diesel::insert_into(produits)
            .values(&NouveauProduit { /* ... */ })
            .get_result::<models::Produit>(conn)?;

        diesel::update(produits.find(2))
            .set(stock.eq(stock - 1))
            .execute(conn)?;

        // Si on retourne Err, la transaction est rollbackée automatiquement
        if p1.stock < 0 {
            return Err(diesel::result::Error::RollbackTransaction);
        }

        Ok(())
    })
    .expect("Transaction échouée");
}
```
