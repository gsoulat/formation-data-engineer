# Diesel — ORM type-safe pour Rust

Diesel est l'ORM le plus utilisé en Rust. Sa caractéristique principale : les **erreurs SQL sont détectées à la compilation**, pas à l'exécution.

## Pourquoi Diesel ?

```rust
// Diesel refuse de compiler ce code si "colonne_inexistante" n'existe pas
// → Erreur à la compilation, jamais en production
let results = products
    .filter(colonne_inexistante.eq("test"))  // ERREUR de compilation
    .load::<Product>(&mut conn);
```

- **Type-safe** : le schéma de la BDD est représenté en types Rust
- **Performant** : pas d'overhead runtime, requêtes proches du SQL brut
- **Mature** : projet bien maintenu, utilisé en production
- **Limitation** : synchrone uniquement (pas d'async natif)

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Setup, CLI, schéma, modèles |
| [02-requetes.md](./02-requetes.md) | CRUD, filtres, relations |

## Installation

```toml
# Cargo.toml
[dependencies]
diesel = { version = "2.1", features = ["postgres", "chrono", "uuid"] }
dotenvy = "0.15"

[dev-dependencies]
diesel_migrations = "2.1"
```

```bash
# Installer la CLI Diesel
cargo install diesel_cli --no-default-features --features postgres
```
