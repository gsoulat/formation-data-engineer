# Diesel Migrations — Migrations pour Rust/Diesel

Diesel intègre son propre système de migrations, basé sur des fichiers SQL `.sql` versionnés.

## Caractéristiques

- **SQL pur** : les migrations sont des fichiers `up.sql` et `down.sql`
- **Intégré** : fait partie de l'écosystème Diesel (pas d'outil séparé)
- **CLI** : géré via `diesel_cli`
- **Embedding** : les migrations peuvent être embarquées dans le binaire Rust

## Différence avec Alembic

| Aspect | Alembic | Diesel Migrations |
|--------|---------|-------------------|
| Langage migrations | Python ou SQL | SQL pur |
| Autogenerate | Oui | Non (SQL manuel) |
| Intégration | Séparé de SQLAlchemy | Intégré à Diesel |
| Embeddable | Non | Oui (dans le binaire) |
| Table tracking | `alembic_version` | `__diesel_schema_migrations` |

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | CLI Diesel, workflow migrations, embedding |

## Installation

```bash
# Installer la CLI Diesel
cargo install diesel_cli --no-default-features --features postgres

# Ajouter diesel_migrations au projet
# Cargo.toml:
# [dependencies]
# diesel_migrations = "2.1"
```
