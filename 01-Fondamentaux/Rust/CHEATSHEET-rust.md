# Rust — Cheatsheet de référence rapide

## Variables et types

```rust
// Déclaration
let x = 5;              // immuable, inférence de type
let mut y = 10;         // mutable
const MAX: u32 = 100;   // constante (type obligatoire)
let z = x;              // shadowing possible avec let z = ...;

// Types scalaires
let i: i32  = -42;      // entier signé 8/16/32/64/128/isize
let u: u64  = 42;       // entier non signé 8/16/32/64/128/usize
let f: f64  = 3.14;     // flottant 32/64
let b: bool = true;
let c: char = 'é';      // Unicode (4 octets)

// Types composés
let t: (i32, &str, bool) = (1, "ok", true);
let (a, b, _) = t;      // destructuration
let first = t.0;

let arr: [i32; 5] = [1, 2, 3, 4, 5];
let zeros = [0; 10];    // [0, 0, 0, ..., 0]
let slice: &[i32] = &arr[1..3];  // [2, 3]

// String vs &str
let s: String = String::from("hello");
let s2: String = "hello".to_string();
let sr: &str = "bonjour";       // string literal (statique)
let sr2: &str = &s[0..3];       // slice d'une String
```

## Ownership et Borrowing

```rust
// Move : l'ownership est transféré
let s1 = String::from("hello");
let s2 = s1;            // s1 n'est plus valide

// Clone : copie profonde
let s3 = s2.clone();    // s2 et s3 valides

// Copy : types primitifs copiés automatiquement
let x = 5;
let y = x;              // x toujours valide (i32 est Copy)

// Borrowing immuable
fn lire(s: &String) { println!("{}", s); }
lire(&s2);              // s2 toujours valide après

// Borrowing mutable (exclusif)
fn ajouter(s: &mut String) { s.push_str("!"); }
let mut msg = String::from("hello");
ajouter(&mut msg);

// Règles borrow checker
// 1 seul &mut  OU  N &  — jamais les deux simultanément

// Lifetimes explicites
fn plus_long<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() >= y.len() { x } else { y }
}

// Struct avec référence
struct Extrait<'a> { texte: &'a str }
```

## Structs et Enums

```rust
// Struct classique
struct Point { x: f64, y: f64 }

impl Point {
    fn new(x: f64, y: f64) -> Self { Point { x, y } }  // constructeur
    fn distance(&self, autre: &Point) -> f64 {           // méthode
        ((self.x - autre.x).powi(2) + (self.y - autre.y).powi(2)).sqrt()
    }
    fn deplacer(&mut self, dx: f64, dy: f64) {           // méthode mutable
        self.x += dx; self.y += dy;
    }
}

// Syntaxe mise à jour
let p1 = Point { x: 1.0, y: 2.0 };
let p2 = Point { x: 5.0, ..p1 };   // y copié depuis p1

// Enum avec données
#[derive(Debug)]
enum Message {
    Quitter,
    Deplacer { x: i32, y: i32 },
    Texte(String),
    Couleur(u8, u8, u8),
}

// Option<T>
let some: Option<i32> = Some(42);
let none: Option<i32> = None;
let val = some.unwrap_or(0);         // 42
let val = some.map(|x| x * 2);      // Some(84)
let val = some.unwrap_or_default();  // 42
```

## Pattern Matching

```rust
// match exhaustif
match msg {
    Message::Quitter                => println!("Quitter"),
    Message::Deplacer { x, y }     => println!("→ ({},{})", x, y),
    Message::Texte(ref s)           => println!("{}", s),
    Message::Couleur(r, g, b)      => println!("#{:02X}{:02X}{:02X}", r, g, b),
}

// Guards et binding
match x {
    n if n < 0 => println!("négatif"),
    0           => println!("zéro"),
    n @ 1..=9   => println!("chiffre: {}", n),
    _           => println!("grand"),
}

// if let (un seul pattern)
if let Some(val) = option { println!("{}", val); }

// while let
while let Some(top) = pile.pop() { println!("{}", top); }

// let-else (Rust 1.65+)
let Some(val) = option else { return; };
```

## Traits

```rust
// Définition
trait Affichable {
    fn afficher(&self);
    fn description(&self) -> String {  // méthode par défaut
        format!("Un objet Affichable")
    }
}

// Implémentation
impl Affichable for Point {
    fn afficher(&self) { println!("({}, {})", self.x, self.y); }
}

// Trait bound
fn imprimer<T: Affichable + std::fmt::Debug>(val: &T) { val.afficher(); }

// where clause
fn traiter<T, U>(t: T, u: U)
where
    T: Affichable + Clone,
    U: std::fmt::Debug,
{ /* ... */ }

// Trait object
let objets: Vec<Box<dyn Affichable>> = vec![Box::new(p1)];

// Traits courants à dériver
#[derive(Debug, Clone, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
struct MaStruct { /* ... */ }

// impl Display
use std::fmt;
impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// From/Into
impl From<(f64, f64)> for Point {
    fn from((x, y): (f64, f64)) -> Self { Point { x, y } }
}
let p: Point = (1.0, 2.0).into();
```

## Gestion des erreurs

```rust
// Result<T, E>
fn lire_fichier(path: &str) -> Result<String, std::io::Error> {
    std::fs::read_to_string(path)
}

// Opérateur ? (propagation)
fn traiter(path: &str) -> Result<usize, std::io::Error> {
    let contenu = lire_fichier(path)?;  // retourne Err si échec
    Ok(contenu.len())
}

// Méthodes sur Result
let val = result.unwrap();                    // panic si Err
let val = result.expect("message");           // panic avec message
let val = result.unwrap_or(0);                // valeur par défaut
let val = result.unwrap_or_else(|e| 0);       // closure
let new = result.map(|v| v * 2);              // transformer Ok
let new = result.map_err(|e| format!("{}", e)); // transformer Err
let new = result.and_then(|v| autre(v));       // chaîner Results

// Erreur personnalisée avec thiserror
use thiserror::Error;

#[derive(Debug, Error)]
enum MonErreur {
    #[error("fichier introuvable: {0}")]
    Fichier(#[from] std::io::Error),
    #[error("valeur invalide: {val}")]
    Valeur { val: String },
}

// anyhow pour les applications
use anyhow::{Context, Result, bail, ensure};
fn main() -> Result<()> {
    let contenu = std::fs::read_to_string("f.txt")
        .context("impossible de lire f.txt")?;
    ensure!(!contenu.is_empty(), "fichier vide");
    bail!("erreur fatale");
}
```

## Closures et Itérateurs

```rust
// Closures
let doubler = |x: i32| x * 2;
let ajouter = |x| x + 10;       // type inféré
let multi = |x, y| x * y;
let complex = |x| {
    let y = x + 1;
    y * 2
};

// Capture par move
let offset = 5;
let ajouter_offset = move |x| x + offset;  // offset copié dans la closure

// Fn / FnMut / FnOnce
fn appliquer<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 { f(x) }
fn appliquer_mut<F: FnMut() -> i32>(mut f: F) -> i32 { f() }

// Itérateurs — lazy, aucun calcul jusqu'à collect/next
let v = vec![1, 2, 3, 4, 5];

let res: Vec<i32> = v.iter()
    .filter(|&&x| x % 2 == 0)    // [2, 4]
    .map(|&x| x * 10)             // [20, 40]
    .collect();

// Méthodes terminales
let somme: i32  = v.iter().sum();
let produit: i32 = v.iter().product();
let count       = v.iter().filter(|&&x| x > 2).count();
let trouve      = v.iter().find(|&&x| x > 3);     // Option<&i32>
let position    = v.iter().position(|&x| x == 3); // Option<usize>
let tous        = v.iter().all(|&x| x > 0);
let un          = v.iter().any(|&x| x > 4);
let max         = v.iter().max();
let min         = v.iter().min();
let fold        = v.iter().fold(0, |acc, &x| acc + x);

// Enumérer et zipper
for (i, val) in v.iter().enumerate() { println!("{}: {}", i, val); }
let paires: Vec<_> = v.iter().zip(v.iter().skip(1)).collect();

// flat_map / flatten
let nested = vec![vec![1, 2], vec![3, 4]];
let plat: Vec<i32> = nested.into_iter().flatten().collect();

// Chaînes de chars
let mots: Vec<&str> = "bonjour le monde".split_whitespace().collect();
let majuscules: String = "bonjour".chars().map(|c| c.to_uppercase().next().unwrap()).collect();
```

## Smart Pointers

```rust
use std::rc::Rc;
use std::cell::RefCell;
use std::sync::{Arc, Mutex, RwLock};

// Box<T> : allocation heap, types récursifs
let b: Box<i32> = Box::new(5);
let trait_obj: Box<dyn std::fmt::Display> = Box::new(42);

// Rc<T> : plusieurs propriétaires, thread unique
let a = Rc::new(vec![1, 2, 3]);
let b = Rc::clone(&a);           // léger, incrémente compteur
println!("{}", Rc::strong_count(&a));  // 2

// Rc<RefCell<T>> : partage mutable, thread unique
let partagé = Rc::new(RefCell::new(vec![1, 2, 3]));
partagé.borrow_mut().push(4);    // mutation via RefCell

// Arc<T> : plusieurs propriétaires, multi-threads
let données = Arc::new(vec![1, 2, 3]);
let clone = Arc::clone(&données);
std::thread::spawn(move || println!("{:?}", clone));

// Arc<Mutex<T>> : état mutable partagé entre threads
let compteur = Arc::new(Mutex::new(0));
let c = Arc::clone(&compteur);
std::thread::spawn(move || { *c.lock().unwrap() += 1; });

// Arc<RwLock<T>> : nombreux lecteurs, peu d'écritures
let cache = Arc::new(RwLock::new(std::collections::HashMap::<String, i32>::new()));
cache.write().unwrap().insert("clé".into(), 42);
let val = cache.read().unwrap().get("clé").copied();  // lecture simultanée OK
```

## Async/Await (Tokio)

```rust
use tokio::time::{sleep, Duration};

// Fonction async
async fn chercher(id: u32) -> String {
    sleep(Duration::from_millis(100)).await;
    format!("résultat {}", id)
}

// Concurrent avec join!
let (r1, r2) = tokio::join!(chercher(1), chercher(2));  // ~100ms

// Tâche indépendante
let handle = tokio::spawn(async move { chercher(3).await });
let r3 = handle.await.unwrap();

// Timeout
use tokio::time::timeout;
match timeout(Duration::from_millis(50), chercher(1)).await {
    Ok(val)  => println!("{}", val),
    Err(_)   => println!("Timeout !"),
}

// Channels
use tokio::sync::mpsc;
let (tx, mut rx) = mpsc::channel::<String>(32);
tokio::spawn(async move { tx.send("msg".into()).await.unwrap(); });
while let Some(msg) = rx.recv().await { println!("{}", msg); }

// HTTP avec reqwest
use reqwest::Client;
let client = Client::new();
let json: serde_json::Value = client
    .get("https://api.example.com/data")
    .send().await?
    .json().await?;

// Point d'entrée
#[tokio::main]
async fn main() { /* ... */ }
```

## Axum

```rust
use axum::{
    Router,
    routing::{get, post, put, delete, patch},
    extract::{Path, Query, State, Json},
    http::StatusCode,
    response::IntoResponse,
};

// Handler minimal
async fn sante() -> &'static str { "OK" }

// Avec paramètre de chemin
async fn get_item(Path(id): Path<u64>) -> String {
    format!("Item {}", id)
}

// Avec query params
#[derive(serde::Deserialize)]
struct Filtres { page: Option<usize>, limite: Option<usize> }
async fn liste(Query(f): Query<Filtres>) -> impl IntoResponse { /* ... */ }

// Avec JSON body
async fn creer(Json(data): Json<serde::de::DeserializeOwned>) -> impl IntoResponse { /* ... */ }

// Avec état partagé
#[derive(Clone)]
struct AppState { db: std::sync::Arc<std::sync::Mutex<Vec<String>>> }

async fn handler(State(state): State<AppState>) -> impl IntoResponse { /* ... */ }

// Réponse avec status code
async fn creer_item() -> (StatusCode, Json<serde_json::Value>) {
    (StatusCode::CREATED, Json(serde_json::json!({"id": 1})))
}

// Router complet
let app = Router::new()
    .route("/items",     get(liste).post(creer))
    .route("/items/:id", get(get_item).put(/* maj */).delete(/* del */))
    .with_state(AppState { /* ... */ });

// Démarrage
let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
axum::serve(listener, app).await.unwrap();
```

## Serde

```rust
use serde::{Serialize, Deserialize};

// Dérivation de base
#[derive(Debug, Serialize, Deserialize, Clone)]
struct Utilisateur {
    id: u64,
    nom: String,
    email: Option<String>,
}

// Annotations courantes
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]          // snake_case → camelCase
struct MonStruct {
    #[serde(rename = "userId")]              // renommage individuel
    id: u64,
    #[serde(skip_serializing_if = "Option::is_none")]  // omettre si None
    champ_optionnel: Option<String>,
    #[serde(default)]                        // valeur par défaut si absent
    actif: bool,
    #[serde(skip)]                           // ignorer complètement
    cache: String,
    #[serde(alias = "username", alias = "user")]  // accepter plusieurs noms
    nom: String,
    #[serde(flatten)]                        // aplatir un sous-struct
    extras: std::collections::HashMap<String, serde_json::Value>,
}

// Enum stratégies
#[derive(Serialize, Deserialize)]
#[serde(tag = "type")]       // {"type": "Texte", "contenu": "..."}
enum Message {
    Texte { contenu: String },
    Image { url: String },
}

#[derive(Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
enum Statut { EnAttente, EnCours, Termine }

// JSON ↔ String
let json_str = serde_json::to_string(&user)?;
let json_pretty = serde_json::to_string_pretty(&user)?;
let user: Utilisateur = serde_json::from_str(&json_str)?;

// JSON dynamique
use serde_json::{json, Value};
let val = json!({ "clé": "valeur", "nombre": 42 });
let texte = val["clé"].as_str().unwrap_or("");

// Fichiers
let contenu = std::fs::read_to_string("config.json")?;
let config: MonStruct = serde_json::from_str(&contenu)?;
std::fs::write("out.json", serde_json::to_string_pretty(&config)?)?;
```

## Collections

```rust
use std::collections::{HashMap, HashSet, BTreeMap, VecDeque};

// Vec
let mut v: Vec<i32> = Vec::new();
let mut v = vec![1, 2, 3];
v.push(4);
v.pop();                          // Option<i32>
v.insert(0, 0);
v.remove(0);
v.len(); v.is_empty();
v.contains(&3);
v.iter(); v.iter_mut(); v.into_iter();
v.sort(); v.sort_by(|a, b| b.cmp(a));
v.dedup();                        // supprimer doublons consécutifs
v.retain(|&x| x > 0);            // filtrer en place

// HashMap
let mut map: HashMap<String, i32> = HashMap::new();
map.insert("clé".into(), 42);
map.get("clé");                   // Option<&i32>
map.contains_key("clé");
map.remove("clé");                // Option<i32>
map.entry("clé".into()).or_insert(0);          // insérer si absent
*map.entry("clé".into()).or_insert(0) += 1;    // incrémenter
map.iter();                       // (&K, &V)
let keys: Vec<&String> = map.keys().collect();

// HashSet
let mut set: HashSet<i32> = HashSet::new();
set.insert(1); set.remove(&1);
set.contains(&1);
let union: HashSet<_> = set1.union(&set2).collect();
let inter: HashSet<_> = set1.intersection(&set2).collect();
```

## Cargo et outils

```bash
# Créer et gérer
cargo new mon_projet       # binaire
cargo new --lib ma_lib     # bibliothèque
cargo build                # compilation debug
cargo build --release      # optimisé
cargo run                  # compile + exécute
cargo run -- arg1 arg2     # avec arguments
cargo check                # vérification rapide (sans compilation)
cargo test                 # tests
cargo test nom_test        # un test spécifique
cargo test -- --nocapture  # voir les println! dans les tests
cargo fmt                  # formater le code
cargo clippy               # linter
cargo doc --open           # générer et ouvrir la doc
cargo add tokio --features full  # ajouter une dépendance
cargo add serde -F derive        # avec feature
cargo update               # mettre à jour les dépendances
cargo tree                 # arbre des dépendances

# Variables d'environnement utiles
RUST_LOG=debug cargo run   # niveau de log
RUST_BACKTRACE=1 cargo run # backtrace sur panic
```

## Cargo.toml

```toml
[package]
name = "mon_projet"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
axum = "0.7"
thiserror = "1"
anyhow = "1"
uuid = { version = "1", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }
reqwest = { version = "0.11", features = ["json"] }

[dev-dependencies]
tokio-test = "0.4"

[profile.release]
opt-level = 3
```

## Tests

```rust
// Tests unitaires dans le même fichier
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_addition() {
        assert_eq!(2 + 2, 4);
    }

    #[test]
    fn test_avec_erreur() {
        assert!(2 > 1);
        assert_ne!(1, 2);
    }

    #[test]
    #[should_panic(expected = "division par zéro")]
    fn test_panic() {
        let _ = 1 / 0;
    }

    #[tokio::test]  // test async
    async fn test_async() {
        let result = ma_fonction_async().await;
        assert_eq!(result, "attendu");
    }
}

// Tests d'intégration dans tests/
// tests/integration_test.rs
use mon_projet::ma_fonction_publique;

#[test]
fn test_integration() {
    assert_eq!(ma_fonction_publique(), 42);
}
```

## Patterns idiomatiques

```rust
// Builder pattern
struct RequeteBuilder {
    url: String,
    timeout: Option<Duration>,
    headers: Vec<(String, String)>,
}

impl RequeteBuilder {
    fn new(url: impl Into<String>) -> Self {
        RequeteBuilder { url: url.into(), timeout: None, headers: vec![] }
    }
    fn timeout(mut self, d: Duration) -> Self { self.timeout = Some(d); self }
    fn header(mut self, k: impl Into<String>, v: impl Into<String>) -> Self {
        self.headers.push((k.into(), v.into())); self
    }
    fn build(self) -> Requete { /* ... */ }
}

let req = RequeteBuilder::new("https://api.example.com")
    .timeout(Duration::from_secs(30))
    .header("Authorization", "Bearer token")
    .build();

// Newtype pattern
struct Email(String);
impl Email {
    fn new(s: &str) -> Result<Self, String> {
        if s.contains('@') { Ok(Email(s.into())) }
        else { Err(format!("email invalide: {}", s)) }
    }
}

// Type state pattern (compilation garantit l'ordre)
struct Brouillon;
struct Publie;
struct Article<Etat> { contenu: String, _etat: std::marker::PhantomData<Etat> }

impl Article<Brouillon> {
    fn new(contenu: String) -> Self {
        Article { contenu, _etat: std::marker::PhantomData }
    }
    fn publier(self) -> Article<Publie> {
        Article { contenu: self.contenu, _etat: std::marker::PhantomData }
    }
}
impl Article<Publie> {
    fn lire(&self) -> &str { &self.contenu }
}
// Article<Brouillon> ne peut pas appeler lire() — erreur de compilation !

// Extension trait
trait VecExt<T> {
    fn deuxieme(&self) -> Option<&T>;
}
impl<T> VecExt<T> for Vec<T> {
    fn deuxieme(&self) -> Option<&T> { self.get(1) }
}
```

## Pièges courants

```rust
// ❌ Itérer et modifier
for val in &v { v.push(*val); }  // erreur borrow checker → utiliser index ou collect

// ✓ Bon
let nouveaux: Vec<i32> = v.iter().map(|&x| x * 2).collect();
v.extend(nouveaux);

// ❌ Capturer par référence dans spawn
let data = vec![1, 2, 3];
tokio::spawn(async { println!("{:?}", data); });  // data ne vit pas assez longtemps

// ✓ Bon — move la capture dans la closure
tokio::spawn(async move { println!("{:?}", data); });

// ❌ Deadlock — acquérir le même Mutex deux fois dans le même thread
let lock = mutex.lock().unwrap();
let lock2 = mutex.lock().unwrap();  // deadlock !

// ✓ Bon — libérer avant de réacquérir
drop(lock);
let lock2 = mutex.lock().unwrap();

// ❌ unwrap() en production
let val = option.unwrap();          // panic si None

// ✓ Bon — gérer l'erreur
let val = option.unwrap_or_default();
let val = option.ok_or(MonErreur::ManquantValeur)?;

// ❌ Cloner inutilement
fn traiter(v: Vec<String>) { /* prend ownership */ }
traiter(ma_vec.clone());  // clone entier

// ✓ Bon — emprunter
fn traiter(v: &[String]) { /* emprunt */ }
traiter(&ma_vec);
```
