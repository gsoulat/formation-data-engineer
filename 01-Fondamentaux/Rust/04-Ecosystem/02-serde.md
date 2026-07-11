# Rust — Serde : Serialize/Deserialize, JSON, TOML

## 1. Introduction à Serde

Serde est **le** framework de sérialisation Rust. Il permet de convertir des structures Rust vers/depuis JSON, TOML, YAML, CSV, etc. via des macros de dérivation.

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"       # JSON
toml = "0.8"           # TOML
serde_yaml = "0.9"     # YAML (optionnel)
```

## 2. Dérivation de base

```rust
use serde::{Deserialize, Serialize};
use serde_json;

// #[derive(Serialize, Deserialize)] génère le code de sérialisation
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
struct Utilisateur {
    id: u64,
    nom: String,
    email: String,
    actif: bool,
    age: Option<u32>,
}

fn main() -> Result<(), serde_json::Error> {
    let user = Utilisateur {
        id: 1,
        nom: "Alice".into(),
        email: "alice@example.com".into(),
        actif: true,
        age: Some(30),
    };

    // Rust → JSON String
    let json_str = serde_json::to_string(&user)?;
    println!("{}", json_str);
    // {"id":1,"nom":"Alice","email":"alice@example.com","actif":true,"age":30}

    // Rust → JSON String (pretty)
    let json_pretty = serde_json::to_string_pretty(&user)?;
    println!("{}", json_pretty);

    // JSON String → Rust
    let json = r#"{"id":2,"nom":"Bob","email":"bob@example.com","actif":false,"age":null}"#;
    let user2: Utilisateur = serde_json::from_str(json)?;
    println!("{:?}", user2);

    // Vec → JSON Array
    let users = vec![user, user2];
    let array_json = serde_json::to_string(&users)?;
    println!("{}", array_json);

    // JSON Array → Vec
    let back: Vec<Utilisateur> = serde_json::from_str(&array_json)?;
    println!("{} utilisateurs", back.len());

    Ok(())
}
```

## 3. Annotations Serde

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Produit {
    // Renommer un champ dans le JSON
    #[serde(rename = "productId")]
    id: u64,

    // Valeur par défaut si le champ est absent du JSON
    #[serde(default)]
    stock: u32,

    #[serde(default = "prix_defaut")]
    prix: f64,

    // Ignorer si None dans la sérialisation (ne pas écrire "age": null)
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,

    // Ignorer complètement ce champ (ni lu ni écrit)
    #[serde(skip)]
    cache_interne: String,

    // Alias pour la désérialisation (accepte plusieurs noms)
    #[serde(alias = "categoryName", alias = "cat")]
    categorie: String,
}

fn prix_defaut() -> f64 { 0.0 }

// Renommer tous les champs en camelCase
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct CommandeAPI {
    commande_id: u64,
    date_creation: String,
    montant_total: f64,
    statut_livraison: String,
    // → {"commandeId": ..., "dateCreation": ..., "montantTotal": ..., "statutLivraison": ...}
}

// snake_case → SCREAMING_SNAKE_CASE
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
enum Statut {
    EnAttente,
    EnCours,
    Termine,
    // → "EN_ATTENTE", "EN_COURS", "TERMINE"
}

// Enum avec données : plusieurs stratégies
#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type")]  // tag interne : {"type": "Texte", "contenu": "..."}
enum Message {
    Texte { contenu: String },
    Image { url: String, largeur: u32, hauteur: u32 },
    Audio { url: String, duree_secondes: u32 },
}

// tag externe (défaut) : {"Texte": {"contenu": "..."}}
#[derive(Debug, Serialize, Deserialize)]
enum MessageExterne {
    Texte(String),
    Nombre(i64),
}

fn main() -> Result<(), serde_json::Error> {
    // Test skip_serializing_if
    let produit = Produit {
        id: 1,
        stock: 5,
        prix: 9.99,
        description: None,        // ne sera pas sérialisé
        cache_interne: "...".into(), // ne sera pas sérialisé
        categorie: "Électronique".into(),
    };

    let json = serde_json::to_string_pretty(&produit)?;
    println!("{}", json);
    // Pas de "description" ni "cache_interne" dans le JSON !

    // Test camelCase
    let commande = CommandeAPI {
        commande_id: 42,
        date_creation: "2024-01-15".into(),
        montant_total: 149.99,
        statut_livraison: "Expédié".into(),
    };
    println!("{}", serde_json::to_string_pretty(&commande)?);

    // Test enum avec tag
    let msgs = vec![
        Message::Texte { contenu: "Hello !".into() },
        Message::Image { url: "img.jpg".into(), largeur: 800, hauteur: 600 },
    ];
    println!("{}", serde_json::to_string_pretty(&msgs)?);

    Ok(())
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer la macro `#[derive(Serialize, Deserialize)]` dans VS Code. Montrer comment rust-analyzer peut afficher le code généré par la macro (via "Expand macro"). Montrer le JSON produit avec et sans `skip_serializing_if` pour voir la différence.
> **Expliquer :** Expliquer que `Serialize` et `Deserialize` sont des macros procédurales qui génèrent du code Rust à la compilation. Il n'y a pas de réflexion (reflection) à l'exécution comme en Java. C'est pour ça que Serde est extrêmement rapide.
---

## 4. Désérialisation robuste

```rust
use serde::{Deserialize, Deserializer};
use serde_json::Value;

// Désérialiseur personnalisé
fn deserialiser_prix<'de, D: Deserializer<'de>>(d: D) -> Result<f64, D::Error> {
    let val = Value::deserialize(d)?;
    match val {
        Value::Number(n) => n.as_f64().ok_or_else(|| serde::de::Error::custom("nombre invalide")),
        Value::String(s) => s.parse::<f64>().map_err(serde::de::Error::custom),
        _ => Err(serde::de::Error::custom("type invalide pour le prix")),
    }
}

#[derive(Debug, Deserialize)]
struct Prix {
    #[serde(deserialize_with = "deserialiser_prix")]
    montant: f64,
    devise: String,
}

// Gestion des JSONs dynamiques avec Value
fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Accepte "9.99" (string) ET 9.99 (number)
    let p1: Prix = serde_json::from_str(r#"{"montant": 9.99, "devise": "EUR"}"#)?;
    let p2: Prix = serde_json::from_str(r#"{"montant": "15.50", "devise": "USD"}"#)?;
    println!("{:?} {:?}", p1, p2);

    // --- serde_json::Value : JSON dynamique ---
    let json = r#"{"nom": "Alice", "scores": [95, 87, 92], "actif": true}"#;
    let val: Value = serde_json::from_str(json)?;

    println!("{}", val["nom"]);              // "Alice"
    println!("{}", val["scores"][0]);        // 95
    println!("{}", val["actif"]);            // true
    println!("{}", val["inexistant"]);       // null

    // Navigation avec as_*
    if let Some(nom) = val["nom"].as_str() {
        println!("Nom: {}", nom);
    }
    if let Some(scores) = val["scores"].as_array() {
        let total: i64 = scores.iter()
            .filter_map(|v| v.as_i64())
            .sum();
        println!("Total scores: {}", total);
    }

    // Construire un JSON dynamique
    let json_value = serde_json::json!({
        "id": 42,
        "utilisateur": {
            "nom": "Alice",
            "roles": ["admin", "user"]
        },
        "timestamp": chrono::Utc::now().timestamp()  // si chrono est inclus
    });
    println!("{}", json_value);

    // Désérialisation partielle tolérante
    #[derive(Debug, Deserialize)]
    struct Flexible {
        nom: String,
        #[serde(default)]  // absent = valeur par défaut
        age: u32,
        #[serde(flatten)]  // aplatir les champs supplémentaires
        extras: std::collections::HashMap<String, Value>,
    }

    let json = r#"{"nom": "Bob", "email": "bob@ex.com", "prefs": true}"#;
    let f: Flexible = serde_json::from_str(json)?;
    println!("{:?}", f);

    Ok(())
}
```

## 5. Serde avec des fichiers

```rust
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
struct Config {
    hote: String,
    port: u16,
    base_de_donnees: DBConfig,
    fonctionnalites: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct DBConfig {
    url: String,
    pool_max: u32,
    timeout_secondes: u32,
}

fn lire_config(path: &Path) -> Result<Config, Box<dyn std::error::Error>> {
    // JSON
    if path.extension() == Some(std::ffi::OsStr::new("json")) {
        let contenu = fs::read_to_string(path)?;
        return Ok(serde_json::from_str(&contenu)?);
    }
    // TOML
    if path.extension() == Some(std::ffi::OsStr::new("toml")) {
        let contenu = fs::read_to_string(path)?;
        return Ok(toml::from_str(&contenu)?);
    }
    Err("Format non supporté".into())
}

fn sauvegarder_config(config: &Config, path: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let contenu = match path.extension().and_then(|e| e.to_str()) {
        Some("json") => serde_json::to_string_pretty(config)?,
        Some("toml") => toml::to_string(config)?,
        _ => return Err("Format non supporté".into()),
    };
    fs::write(path, contenu)?;
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config {
        hote: "localhost".into(),
        port: 8080,
        base_de_donnees: DBConfig {
            url: "postgres://localhost/app".into(),
            pool_max: 10,
            timeout_secondes: 30,
        },
        fonctionnalites: vec!["auth".into(), "cache".into()],
    };

    // Sauvegarder en JSON
    sauvegarder_config(&config, Path::new("config.json"))?;

    // Sauvegarder en TOML
    sauvegarder_config(&config, Path::new("config.toml"))?;

    // Lire
    let config_relue: Config = serde_json::from_str(
        &fs::read_to_string("config.json")?
    )?;
    println!("{:?}", config_relue);

    // Nettoyage
    let _ = fs::remove_file("config.json");
    let _ = fs::remove_file("config.toml");

    Ok(())
}
```

## 6. Serde dans le contexte Axum

```rust
use axum::{Router, routing::{get, post}, Json, extract::{Path, State}};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Tache {
    pub id: u64,
    pub titre: String,
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub date_echeance: Option<String>,
    pub completee: bool,
    pub priorite: Priorite,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "UPPERCASE")]
pub enum Priorite { Basse, Normale, Haute, Critique }

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreerTacheRequest {
    pub titre: String,
    pub description: Option<String>,
    pub date_echeance: Option<String>,
    #[serde(default = "priorite_defaut")]
    pub priorite: Priorite,
}

fn priorite_defaut() -> Priorite { Priorite::Normale }

type Store = Arc<RwLock<HashMap<u64, Tache>>>;

async fn creer_tache(
    State(store): State<Store>,
    Json(req): Json<CreerTacheRequest>,
) -> Json<Tache> {
    let mut map = store.write().unwrap();
    let id = map.len() as u64 + 1;
    let tache = Tache {
        id,
        titre: req.titre,
        description: req.description,
        date_echeance: req.date_echeance,
        completee: false,
        priorite: req.priorite,
    };
    map.insert(id, tache.clone());
    Json(tache)
}

async fn lister_taches(State(store): State<Store>) -> Json<Vec<Tache>> {
    let map = store.read().unwrap();
    Json(map.values().cloned().collect())
}

#[tokio::main]
async fn main() {
    let store: Store = Arc::new(RwLock::new(HashMap::new()));

    let app = Router::new()
        .route("/taches", get(lister_taches).post(creer_tache))
        .with_state(store);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Serveur: http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

## Récapitulatif

| Annotation | Description | Exemple |
|------------|-------------|---------|
| `#[derive(Serialize)]` | Active la sérialisation | → JSON, TOML... |
| `#[derive(Deserialize)]` | Active la désérialisation | JSON → struct |
| `#[serde(rename = "x")]` | Renommer un champ | `id` → `productId` |
| `#[serde(rename_all = "camelCase")]` | Renommer tous les champs | Style API REST |
| `#[serde(skip_serializing_if = "Option::is_none")]` | Omettre si None | Pas de `"field": null` |
| `#[serde(default)]` | Valeur par défaut | Champ absent → défaut |
| `#[serde(skip)]` | Ignorer complètement | Champs internes |
| `#[serde(alias = "x")]` | Accepter plusieurs noms | Rétrocompatibilité |
| `#[serde(tag = "type")]` | Enum tagged | `{"type": "Texte", ...}` |
| `#[serde(flatten)]` | Aplatir un sous-struct | Champs extras |
