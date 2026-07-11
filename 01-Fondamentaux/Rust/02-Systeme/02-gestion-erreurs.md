# Rust — Gestion des erreurs : Result<T,E>, Option<T>, ?, Custom Errors, thiserror

## 1. La philosophie Rust des erreurs

Rust n'a pas d'exceptions. Les erreurs sont des **valeurs** retournées par les fonctions :

```
Option<T>  : valeur qui peut être absente  → Some(T) | None
Result<T,E>: opération qui peut échouer   → Ok(T) | Err(E)
panic!()   : erreur irrécupérable (bug)   → arrête le programme
```

```rust
// En Java :
// String lireFichier(String path) throws IOException { ... }

// En Rust :
// fn lire_fichier(path: &str) -> Result<String, io::Error> { ... }
// L'erreur fait PARTIE du type → le compilateur force sa gestion
```

## 2. Result<T, E>

```rust
use std::fs;
use std::io;

// Lire un fichier retourne Result<String, io::Error>
fn lire_nom_utilisateur(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)  // retourne Result<String, io::Error>
}

fn main() {
    // --- Gérer avec match ---
    match lire_nom_utilisateur("utilisateur.txt") {
        Ok(nom) => println!("Utilisateur : {}", nom),
        Err(e)  => println!("Erreur de lecture : {}", e),
    }

    // --- Méthodes de Result ---
    let resultat: Result<i32, String> = Ok(42);
    let erreur:   Result<i32, String> = Err(String::from("quelque chose a raté"));

    // unwrap : Ok → valeur, Err → panic
    println!("{}", resultat.unwrap());         // 42
    // erreur.unwrap();                         // PANIC !

    // expect : unwrap avec message personnalisé
    // erreur.expect("Échec lors du calcul");  // PANIC avec message

    // unwrap_or : valeur par défaut
    println!("{}", erreur.unwrap_or(0));       // 0
    println!("{}", erreur.unwrap_or_else(|e| { println!("Erreur: {}", e); -1 }));

    // is_ok / is_err
    println!("{}", resultat.is_ok());  // true
    println!("{}", erreur.is_err());   // true

    // map : transformer Ok
    let double = resultat.map(|n| n * 2);  // Ok(84)
    let texte  = resultat.map(|n| n.to_string());  // Ok("42")

    // map_err : transformer Err
    let converti = erreur.map_err(|e| format!("Erreur formatée: {}", e));

    // and_then : chaîner des opérations (flat_map)
    let chaine = resultat
        .and_then(|n| if n > 0 { Ok(n * 2) } else { Err(String::from("négatif")) });
    println!("{:?}", chaine);  // Ok(84)

    // ok() : Result → Option (perd l'info d'erreur)
    let option: Option<i32> = resultat.ok();  // Some(42)

    // or / or_else : fallback sur erreur
    let _ = erreur.or(Ok::<i32, String>(99));  // Ok(99)
}
```

## 3. L'opérateur ? — Propagation d'erreur

```rust
use std::fs;
use std::io;
use std::num::ParseIntError;

// Sans ? : verbeux
fn lire_nombre_v1(path: &str) -> Result<i32, String> {
    let contenu = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => return Err(format!("Lecture impossible: {}", e)),
    };
    let nombre = match contenu.trim().parse::<i32>() {
        Ok(n) => n,
        Err(e) => return Err(format!("Parsing impossible: {}", e)),
    };
    Ok(nombre)
}

// Avec ? : concis
fn lire_nombre_v2(path: &str) -> Result<i32, Box<dyn std::error::Error>> {
    let contenu = fs::read_to_string(path)?;   // ? = return Err(e) si Err
    let nombre = contenu.trim().parse::<i32>()?;  // ? = return Err(e) si Err
    Ok(nombre)
}

// Encore plus concis
fn lire_et_doubler(path: &str) -> Result<i32, Box<dyn std::error::Error>> {
    Ok(fs::read_to_string(path)?.trim().parse::<i32>()? * 2)
}

// ? dans main (pour les programmes simples)
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let contenu = fs::read_to_string("mon_fichier.txt")?;
    println!("{}", contenu);
    Ok(())
}
```

## 4. Erreurs personnalisées

```rust
use std::fmt;
use std::num::ParseIntError;

// --- Approche manuelle ---
#[derive(Debug)]
enum AppError {
    IoError(std::io::Error),
    ParseError(ParseIntError),
    ValidationError(String),
    NotFound(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::IoError(e)          => write!(f, "Erreur I/O : {}", e),
            AppError::ParseError(e)       => write!(f, "Erreur de parsing : {}", e),
            AppError::ValidationError(msg) => write!(f, "Validation : {}", msg),
            AppError::NotFound(res)       => write!(f, "Introuvable : {}", res),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::IoError(e)    => Some(e),
            AppError::ParseError(e) => Some(e),
            _ => None,
        }
    }
}

// From permet la conversion automatique avec ?
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self {
        AppError::IoError(e)
    }
}

impl From<ParseIntError> for AppError {
    fn from(e: ParseIntError) -> Self {
        AppError::ParseError(e)
    }
}

// Maintenant ? convertit automatiquement
fn traiter_fichier(path: &str) -> Result<i32, AppError> {
    let contenu = std::fs::read_to_string(path)?;   // io::Error → AppError via From
    let nombre = contenu.trim().parse::<i32>()?;     // ParseIntError → AppError via From

    if nombre < 0 {
        return Err(AppError::ValidationError("Le nombre doit être positif".into()));
    }

    Ok(nombre * 2)
}
```

## 5. thiserror — Erreurs personnalisées simplifiées

```toml
# Cargo.toml
[dependencies]
thiserror = "1.0"
```

```rust
use thiserror::Error;

// thiserror génère automatiquement Display et Error
#[derive(Debug, Error)]
pub enum ServiceError {
    #[error("Erreur I/O : {0}")]
    Io(#[from] std::io::Error),          // #[from] génère From<io::Error>

    #[error("Erreur de parsing : {0}")]
    Parse(#[from] std::num::ParseIntError),

    #[error("Produit introuvable : id={id}")]
    ProduitInconnu { id: u64 },

    #[error("Stock insuffisant : demande={demande}, disponible={disponible}")]
    StockInsuffisant { demande: u32, disponible: u32 },

    #[error("Validation échouée pour '{champ}' : {message}")]
    Validation { champ: String, message: String },

    #[error("Erreur de base de données : {0}")]
    Database(String),
}

// Utilisation
fn verifier_stock(id: u64, quantite: u32) -> Result<(), ServiceError> {
    let stock_disponible = 5u32;  // simulé

    if id == 999 {
        return Err(ServiceError::ProduitInconnu { id });
    }

    if quantite > stock_disponible {
        return Err(ServiceError::StockInsuffisant {
            demande: quantite,
            disponible: stock_disponible,
        });
    }

    Ok(())
}

fn valider_prix(prix: f64) -> Result<f64, ServiceError> {
    if prix <= 0.0 {
        return Err(ServiceError::Validation {
            champ: "prix".into(),
            message: "doit être positif".into(),
        });
    }
    Ok(prix)
}

fn creer_commande(produit_id: u64, quantite: u32, prix: f64)
    -> Result<String, ServiceError> {
    verifier_stock(produit_id, quantite)?;
    let prix_valide = valider_prix(prix)?;
    Ok(format!("Commande: produit={}, qté={}, prix={:.2}", produit_id, quantite, prix_valide))
}

fn main() {
    // Test des différents cas d'erreur
    let cas = vec![
        (1u64, 3u32, 9.99_f64),     // OK
        (999,  1,    9.99),          // ProduitInconnu
        (1,    10,   9.99),          // StockInsuffisant
        (1,    1,    -5.0),          // Validation
    ];

    for (id, qte, prix) in cas {
        match creer_commande(id, qte, prix) {
            Ok(cmd)  => println!("✓ {}", cmd),
            Err(e)   => println!("✗ {}", e),
        }
    }
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer dans VS Code rust-analyzer qui force la gestion d'un `Result` : écrire `fs::read_to_string("fichier.txt")` sans gérer le résultat. rust-analyzer affiche un warning "this `Result` may be an `Err` variant, which should be handled". Montrer les quick-fixes proposés.
> **Expliquer :** Insister sur le fait que contrairement à Java, un `Result` non géré est un warning (voire une erreur selon la config). On ne peut pas "oublier" de gérer une erreur en Rust sans que le compilateur le signale. Montrer la différence avec les checked exceptions Java (obligatoires mais contournables avec `catch (Exception e) {}`).
---

## 6. anyhow — Pour les applications (pas les bibliothèques)

```toml
[dependencies]
anyhow = "1.0"
```

```rust
use anyhow::{Result, Context, bail, ensure, anyhow};

// anyhow::Result = Result<T, anyhow::Error>
// anyhow::Error peut contenir n'importe quelle erreur

fn lire_config(path: &str) -> Result<String> {
    let contenu = std::fs::read_to_string(path)
        .context("Impossible de lire le fichier de config")?;  // Context ajoute du contexte
    Ok(contenu)
}

fn parser_port(s: &str) -> Result<u16> {
    let port: u16 = s.parse()
        .context(format!("'{}' n'est pas un port valide", s))?;

    ensure!(port >= 1024, "Le port {} est réservé (< 1024)", port);

    Ok(port)
}

fn connecter(host: &str, port_str: &str) -> Result<()> {
    if host.is_empty() {
        bail!("L'hôte ne peut pas être vide");  // return Err(...)
    }

    let port = parser_port(port_str)?;
    println!("Connexion à {}:{}", host, port);
    Ok(())
}

fn main() -> Result<()> {
    // anyhow est parfait pour le main
    connecter("localhost", "8080")?;

    // Créer une erreur manuellement
    let err = anyhow!("Quelque chose a raté: {}", 42);
    println!("{}", err);

    // Chaîne de contexte
    let resultat = lire_config("inexistant.toml");
    if let Err(e) = &resultat {
        println!("{:#}", e);  // affiche la chaîne de contexte complète
    }

    Ok(())
}
```

## 7. Quand utiliser quoi

```rust
// panic! : pour les bugs de programmation (jamais en prod)
fn get_premier(v: &[i32]) -> i32 {
    v[0]  // panic si vide
    // ou
    *v.first().expect("Le vecteur ne devrait jamais être vide ici")
}

// Option : valeur qui peut légitimement être absente
fn trouver_utilisateur(id: u32, db: &[Utilisateur]) -> Option<&Utilisateur> {
    db.iter().find(|u| u.id == id)
}

// Result : opération qui peut échouer pour des raisons extérieures
fn envoyer_email(dest: &str, msg: &str) -> Result<(), EmailError> { /* ... */ Ok(()) }

// thiserror : pour les bibliothèques (erreurs typées, exhaustives)
// anyhow : pour les applications (simple, contexte riche)

fn main() {
    // Convertir Option en Result
    let opt: Option<i32> = Some(42);
    let res: Result<i32, &str> = opt.ok_or("Valeur absente");

    // Convertir Result en Option
    let res2: Result<i32, String> = Ok(42);
    let opt2: Option<i32> = res2.ok();  // perd l'info d'erreur

    // Collecter des Results
    let strs = vec!["1", "2", "3", "abc", "5"];
    let nombres: Result<Vec<i32>, _> = strs.iter()
        .map(|s| s.parse::<i32>())
        .collect();
    println!("{:?}", nombres);  // Err(ParseIntError) à cause de "abc"

    // Ignorer les erreurs (filtrer les Ok)
    let valides: Vec<i32> = strs.iter()
        .filter_map(|s| s.parse::<i32>().ok())
        .collect();
    println!("{:?}", valides);  // [1, 2, 3, 5]
}
```

## Récapitulatif

| Outil | Cas d'usage | Exemple |
|-------|-------------|---------|
| `Option<T>` | Valeur optionnelle | `find()`, index de HashMap |
| `Result<T,E>` | Opération faillible | I/O, réseau, parsing |
| `?` | Propagation concise | Dans toute fn → Result/Option |
| `unwrap()` | Tests/prototypes | Éviter en production |
| `expect("msg")` | Bugs impossibles | Avec message clair |
| `thiserror` | Erreurs de bibliothèque | Enum d'erreurs typé |
| `anyhow` | Erreurs d'application | main, scripts, CLIs |
| `panic!` | Bugs de programmation | État incohérent irréparable |
