# Rust — Axum : Web Framework, Router, Handlers, State, Extractors

## 1. Introduction à Axum

Axum est un framework web Rust construit sur **Tokio** et **Hyper**. Il est développé par l'équipe Tokio et est l'un des frameworks Rust les plus utilisés.

Caractéristiques :
- Basé sur `tower` : middleware composable
- Type-safe : les extracteurs sont validés à la compilation
- Zéro `macro` obligatoires : tout est du Rust standard
- Haute performance : comparable à Go et bien supérieur à Node.js

## 2. Setup

```toml
# Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace"] }
tracing = "0.1"
tracing-subscriber = "0.3"
```

## 3. Application minimaliste

```rust
use axum::{
    routing::{get, post, put, delete},
    Router,
    response::Json,
    extract::Path,
};
use serde_json::{json, Value};

// Handler = fonction async qui retourne une réponse
async fn racine() -> &'static str {
    "Bonjour depuis Axum !"
}

async fn sante() -> Json<Value> {
    Json(json!({ "status": "ok", "version": "1.0" }))
}

#[tokio::main]
async fn main() {
    // Router : associer des routes à des handlers
    let app = Router::new()
        .route("/", get(racine))
        .route("/health", get(sante));

    // Lier à une adresse et démarrer
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Serveur démarré sur http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `cargo run` et montrer le serveur démarré. Puis dans un autre terminal, utiliser `curl http://localhost:3000/health` pour obtenir le JSON. Montrer aussi l'ouverture dans un navigateur.
> **Expliquer :** Expliquer la vitesse de démarrage (< 100ms), la légèreté mémoire (quelques MB), et les performances. Comparer le débit potentiel avec Spring Boot Java (quelques secondes au démarrage, plus de mémoire).
---

## 4. Extracteurs — Récupérer des données depuis la requête

```rust
use axum::{
    extract::{Path, Query, State, Json as ExtractJson},
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize, Clone)]
struct Produit {
    id: u64,
    nom: String,
    prix: f64,
    stock: u32,
}

#[derive(Debug, Deserialize)]
struct FiltresProduits {
    nom: Option<String>,
    prix_max: Option<f64>,
    page: Option<usize>,
    limite: Option<usize>,
}

#[derive(Debug, Deserialize)]
struct NouveauProduit {
    nom: String,
    prix: f64,
    stock: u32,
}

// --- Path : variable dans l'URL ---
// GET /produits/:id
async fn get_produit(Path(id): Path<u64>) -> Json<Produit> {
    Json(Produit {
        id,
        nom: format!("Produit {}", id),
        prix: 9.99,
        stock: 10,
    })
}

// Plusieurs variables de chemin
// GET /categories/:cat_id/produits/:prod_id
async fn get_produit_dans_categorie(
    Path((cat_id, prod_id)): Path<(u64, u64)>
) -> String {
    format!("Produit {} dans catégorie {}", prod_id, cat_id)
}

// --- Query : paramètres de requête (?nom=x&prix_max=100) ---
async fn lister_produits(Query(filtres): Query<FiltresProduits>) -> Json<Vec<Produit>> {
    println!("Filtres: {:?}", filtres);
    // ... filtrage réel depuis la DB
    Json(vec![
        Produit { id: 1, nom: "Clavier".into(), prix: 79.99, stock: 10 },
        Produit { id: 2, nom: "Souris".into(), prix: 29.99, stock: 20 },
    ])
}

// --- Json : corps de la requête ---
async fn creer_produit(
    ExtractJson(nouveau): ExtractJson<NouveauProduit>
) -> Json<Produit> {
    println!("Nouveau produit: {:?}", nouveau);
    Json(Produit {
        id: 42,  // généré
        nom: nouveau.nom,
        prix: nouveau.prix,
        stock: nouveau.stock,
    })
}

// --- Headers ---
use axum::http::HeaderMap;
async fn avec_headers(headers: HeaderMap) -> String {
    let auth = headers.get("Authorization")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("non fourni");
    format!("Authorization: {}", auth)
}
```

## 5. State partagé

```rust
use axum::{
    extract::State,
    routing::{get, post, delete},
    Router, Json,
    http::StatusCode,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

// État partagé de l'application
#[derive(Clone)]
struct AppState {
    produits: Arc<Mutex<HashMap<u64, Produit>>>,
    prochain_id: Arc<Mutex<u64>>,
}

impl AppState {
    fn new() -> Self {
        let mut produits = HashMap::new();
        produits.insert(1, Produit { id: 1, nom: "Clavier".into(), prix: 79.99, stock: 10 });
        produits.insert(2, Produit { id: 2, nom: "Souris".into(), prix: 29.99, stock: 20 });

        AppState {
            produits: Arc::new(Mutex::new(produits)),
            prochain_id: Arc::new(Mutex::new(3)),
        }
    }
}

// Handlers avec State
async fn lister_tous(State(state): State<AppState>) -> Json<Vec<Produit>> {
    let produits = state.produits.lock().unwrap();
    let liste: Vec<Produit> = produits.values().cloned().collect();
    Json(liste)
}

async fn get_par_id(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> impl IntoResponse {
    let produits = state.produits.lock().unwrap();
    match produits.get(&id) {
        Some(p) => (StatusCode::OK, Json(p.clone())).into_response(),
        None    => (StatusCode::NOT_FOUND,
                    Json(serde_json::json!({"erreur": "Produit introuvable"}))).into_response(),
    }
}

async fn creer(
    State(state): State<AppState>,
    Json(nouveau): Json<NouveauProduit>,
) -> impl IntoResponse {
    let mut id_lock = state.prochain_id.lock().unwrap();
    let id = *id_lock;
    *id_lock += 1;
    drop(id_lock);  // libérer avant d'acquérir l'autre lock

    let produit = Produit { id, nom: nouveau.nom, prix: nouveau.prix, stock: nouveau.stock };
    state.produits.lock().unwrap().insert(id, produit.clone());

    (StatusCode::CREATED, Json(produit))
}

async fn supprimer(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> StatusCode {
    match state.produits.lock().unwrap().remove(&id) {
        Some(_) => StatusCode::NO_CONTENT,
        None    => StatusCode::NOT_FOUND,
    }
}

#[tokio::main]
async fn main() {
    let state = AppState::new();

    let app = Router::new()
        .route("/produits",     get(lister_tous).post(creer))
        .route("/produits/:id", get(get_par_id).delete(supprimer))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("API démarrée sur http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Utiliser curl pour tester l'API complète :
> ```bash
> curl http://localhost:3000/produits
> curl -X POST http://localhost:3000/produits -H "Content-Type: application/json" -d '{"nom":"Écran","prix":299.99,"stock":5}'
> curl http://localhost:3000/produits/3
> curl -X DELETE http://localhost:3000/produits/1
> ```
> Montrer chaque réponse dans le terminal, les codes HTTP et les JSON retournés.
> **Expliquer :** Expliquer que l'État partagé avec `Arc<Mutex<HashMap>>` est la solution temporaire pour les démos. En production, on utiliserait une vraie base de données via `sqlx` ou `diesel`. Montrer que sans `Arc`, Axum refuse de compiler car l'état doit être `Send + Sync`.
---

## 6. Réponses personnalisées

```rust
use axum::{
    response::{IntoResponse, Response},
    http::{StatusCode, HeaderMap, HeaderValue, header},
    body::Body,
};
use serde_json::json;

// Réponse JSON personnalisée
async fn reponse_complexe() -> impl IntoResponse {
    let mut headers = HeaderMap::new();
    headers.insert(header::CONTENT_TYPE, HeaderValue::from_static("application/json"));
    headers.insert("X-Request-Id", HeaderValue::from_static("abc123"));

    let body = json!({
        "status": "success",
        "data": { "message": "Bonjour" }
    });

    (StatusCode::OK, headers, Json(body))
}

// Type de réponse personnalisé
struct HtmlResponse(String);

impl IntoResponse for HtmlResponse {
    fn into_response(self) -> Response {
        Response::builder()
            .status(200)
            .header("Content-Type", "text/html; charset=utf-8")
            .body(Body::from(self.0))
            .unwrap()
    }
}

async fn page_html() -> HtmlResponse {
    HtmlResponse("<html><body><h1>Hello from Axum!</h1></body></html>".into())
}

// Enum de réponse (pattern courant pour les erreurs)
enum ApiError {
    NotFound(String),
    BadRequest(String),
    Internal(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            ApiError::NotFound(m)   => (StatusCode::NOT_FOUND, m),
            ApiError::BadRequest(m) => (StatusCode::BAD_REQUEST, m),
            ApiError::Internal(m)  => (StatusCode::INTERNAL_SERVER_ERROR, m),
        };
        let body = json!({ "erreur": message });
        (status, Json(body)).into_response()
    }
}

async fn trouver_utilisateur(Path(id): Path<u64>) -> Result<Json<Value>, ApiError> {
    if id == 0 {
        return Err(ApiError::BadRequest("L'id ne peut pas être 0".into()));
    }
    if id > 100 {
        return Err(ApiError::NotFound(format!("Utilisateur {} introuvable", id)));
    }
    Ok(Json(json!({ "id": id, "nom": "Alice" })))
}
```

## 7. Middleware

```rust
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use axum::middleware::{self, Next};
use axum::http::Request;

// Middleware d'authentification basique
async fn auth_middleware<B>(
    req: Request<B>,
    next: Next<B>,
) -> impl IntoResponse {
    let token = req.headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|s| s.strip_prefix("Bearer "));

    match token {
        Some("mon-token-secret") => next.run(req).await.into_response(),
        _ => (
            StatusCode::UNAUTHORIZED,
            Json(json!({"erreur": "Token manquant ou invalide"}))
        ).into_response(),
    }
}

#[tokio::main]
async fn main() {
    // Initialiser le logging
    tracing_subscriber::init();

    // Routes publiques
    let publiques = Router::new()
        .route("/health", get(|| async { "OK" }))
        .route("/produits", get(lister_tous));

    // Routes protégées
    let protegees = Router::new()
        .route("/admin/produits", post(creer))
        .layer(middleware::from_fn(auth_middleware));

    let app = Router::new()
        .merge(publiques)
        .merge(protegees)
        // Logging automatique des requêtes
        .layer(TraceLayer::new_for_http())
        // CORS
        .layer(
            CorsLayer::new()
                .allow_origin(tower_http::cors::Any)
                .allow_methods(tower_http::cors::Any)
                .allow_headers(tower_http::cors::Any)
        );

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

## Récapitulatif

| Concept | Syntaxe | Description |
|---------|---------|-------------|
| Route | `.route("/path", get(handler))` | Associer URL + méthode HTTP |
| Handler | `async fn h() -> impl IntoResponse` | Fonction de traitement |
| Path param | `Path(id): Path<u64>` | `/produits/:id` |
| Query param | `Query(p): Query<Params>` | `?page=1&limite=10` |
| JSON body | `Json(data): Json<T>` | Corps de requête |
| State | `State(s): State<S>` | État partagé |
| Headers | `headers: HeaderMap` | En-têtes HTTP |
| Réponse | `(StatusCode, Json(body))` | Code + corps |
| Middleware | `.layer(...)` | Traitement transversal |
| Logging | `TraceLayer::new_for_http()` | Logs automatiques |
| CORS | `CorsLayer::new()` | Headers CORS |
