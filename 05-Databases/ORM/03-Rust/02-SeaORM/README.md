# SeaORM — ORM async pour Rust

SeaORM est l'alternative async-first à Diesel. Il est construit au-dessus de SQLx et supporte nativement `tokio` et `async-std`.

## SeaORM vs Diesel

| Critère | SeaORM | Diesel |
|---------|--------|--------|
| Async | Oui (natif) | Non (sync) |
| Type-safety compile-time | Partiel | Complet |
| Génération de code | Oui (sea-orm-cli) | Oui (diesel-cli) |
| API | Active Record like | Data Mapper |
| Maturité | Récent (2021+) | Mature (2015+) |
| Intégration Axum/Actix | Très bonne | Possible avec spawn_blocking |

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Setup, entités, CRUD async |
| [02-entites-migrations.md](./02-entites-migrations.md) | Entités dérivées, migrations SeaORM |

## Installation

```toml
[dependencies]
sea-orm = { version = "0.12", features = ["sqlx-postgres", "runtime-tokio-rustls", "macros", "with-chrono"] }
tokio = { version = "1", features = ["full"] }
```
