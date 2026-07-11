# Formation Rust — De l'Ownership à l'Axum Web Framework

## Objectifs pédagogiques

Ce module couvre Rust de manière progressive, depuis les fondamentaux jusqu'au développement d'APIs web avec Axum. À l'issue de cette formation, l'apprenant sera capable de :

- Comprendre et maîtriser l'ownership et le borrowing
- Écrire du code Rust idiomatique sans erreurs de compilation
- Utiliser les structs, enums, traits et génériques
- Gérer les erreurs avec Result et Option
- Développer une API REST avec Axum
- Sérialiser/désérialiser des données avec Serde

## Pourquoi Rust ?

Rust est un langage système qui offre :
- **Sécurité mémoire** sans garbage collector
- **Performance** comparable au C/C++
- **Concurrence sans data races** (garantie à la compilation)
- Utilisé par : Linux, Android, Firefox, Dropbox, Discord, Cloudflare, Microsoft Azure

## Installation

```bash
# Installer rustup (gestionnaire de toolchain)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Recharger le PATH
source ~/.cargo/env

# Vérifier
rustc --version   # compilateur
cargo --version   # gestionnaire de projet/dépendances

# Mettre à jour
rustup update

# IDE recommandé : VS Code + extension "rust-analyzer"
# Ou : IntelliJ IDEA + plugin Rust (CLion)
```

## Plan du cours

| Module | Contenu | Durée estimée |
|--------|---------|---------------|
| **Fondamentaux** | Cargo, variables, ownership, borrowing, types | 8h |
| **Système** | Traits, erreurs, closures, itérateurs | 6h |
| **Avancé** | Smart pointers, async/await | 4h |
| **Écosystème** | Axum, Serde | 6h |
| **Exercices** | Ownership challenges, API Axum | 4h |

**Durée totale estimée : ~28 heures**

## Structure des fichiers

```
Rust/
├── README.md
├── Fondamentaux/
│   ├── 01-introduction.md       ← Why Rust, cargo, variables, types
│   ├── 02-ownership.md          ← Ownership, move semantics, Copy trait
│   ├── 03-borrowing.md          ← References, borrow rules, lifetimes
│   └── 04-types-controle.md     ← structs, enums, match, if let
├── Systeme/
│   ├── 01-traits.md             ← trait, impl, generics, common traits
│   ├── 02-gestion-erreurs.md    ← Result, Option, ?, custom errors
│   └── 03-closures-iterateurs.md ← Closures, Iterator, map/filter/collect
├── Avance/
│   ├── 01-smart-pointers.md     ← Box, Rc, RefCell, Arc, Mutex
│   └── 02-async-await.md        ← async/await, tokio, futures
├── Ecosystem/
│   ├── 01-axum.md               ← Axum web framework
│   └── 02-serde.md              ← Serde, JSON, TOML
├── exercices/
│   ├── exercice-01-ownership.md
│   └── exercice-02-api-axum.md
└── CHEATSHEET-rust.md
```

## Ressources

- [The Rust Book (officiel)](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Rustlings (exercices)](https://github.com/rust-lang/rustlings)
- [docs.rs](https://docs.rs/) — documentation des crates
- [crates.io](https://crates.io/) — registre des packages
