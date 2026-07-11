# Exercice Rust 2 — API REST avec Axum : Gestionnaire de Tâches

## Objectif

Construire une API REST complète de gestion de tâches avec Axum, Serde et un état partagé en mémoire. Vous partirez d'un squelette de projet et implémenterez progressivement chaque fonctionnalité.

## Durée estimée : 3 à 4 heures

---

## Mise en place du projet

```bash
cargo new todo-api
cd todo-api
```

### Cargo.toml

```toml
[package]
name = "todo-api"
version = "0.1.0"
edition = "2021"

[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
uuid = { version = "1", features = ["v4"] }
chrono = { version = "0.4", features = ["serde"] }
```

---

## Partie 1 — Modèles de données (30 min)

### 1.1 Définir les types

Créez un fichier `src/models.rs` avec les structures suivantes :

```rust
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

// Statut d'une tâche
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum StatutTache {
    EnAttente,
    EnCours,
    Terminee,
    Annulee,
}

// Priorité d'une tâche
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, PartialOrd)]
#[serde(rename_all = "UPPERCASE")]
pub enum Priorite {
    Basse,
    Normale,
    Haute,
    Critique,
}

// Tâche principale (dans la DB/état)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Tache {
    pub id: Uuid,
    pub titre: String,
    pub description: Option<String>,
    pub statut: StatutTache,
    pub priorite: Priorite,
    pub tags: Vec<String>,
    pub cree_le: DateTime<Utc>,
    pub modifie_le: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub termine_le: Option<DateTime<Utc>>,
}

// Corps de requête pour créer une tâche
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreerTacheRequest {
    pub titre: String,
    pub description: Option<String>,
    #[serde(default = "priorite_defaut")]
    pub priorite: Priorite,
    #[serde(default)]
    pub tags: Vec<String>,
}

fn priorite_defaut() -> Priorite { Priorite::Normale }

// Corps de requête pour mettre à jour le statut
#[derive(Debug, Deserialize)]
pub struct MajStatutRequest {
    pub statut: StatutTache,
}

// Corps de requête pour modifier une tâche
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModifierTacheRequest {
    pub titre: Option<String>,
    pub description: Option<String>,
    pub priorite: Option<Priorite>,
    pub tags: Option<Vec<String>>,
}

// Réponse pour la liste (pagination)
#[derive(Debug, Serialize)]
pub struct PageTaches {
    pub taches: Vec<Tache>,
    pub total: usize,
    pub page: usize,
    pub par_page: usize,
}

// Paramètres de filtrage/pagination
#[derive(Debug, Deserialize)]
pub struct FiltresTaches {
    pub statut: Option<StatutTache>,
    pub priorite: Option<Priorite>,
    pub tag: Option<String>,
    pub page: Option<usize>,
    pub par_page: Option<usize>,
}
```

**Question** : Pourquoi `StatutTache` et `Priorite` dérivent-ils `PartialEq` mais pas `Eq` pour `Priorite` ? Quel trait supplémentaire serait nécessaire pour trier par priorité ?

---

## Partie 2 — État de l'application (20 min)

### 2.1 Store en mémoire

Créez `src/store.rs` :

```rust
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use uuid::Uuid;
use crate::models::Tache;

// Type alias pour simplifier
pub type Store = Arc<RwLock<HashMap<Uuid, Tache>>>;

pub fn new_store() -> Store {
    Arc::new(RwLock::new(HashMap::new()))
}
```

### 2.2 État global de l'application

Créez `src/state.rs` :

```rust
use crate::store::Store;

#[derive(Clone)]
pub struct AppState {
    pub taches: Store,
}

impl AppState {
    pub fn new() -> Self {
        AppState {
            taches: crate::store::new_store(),
        }
    }
}
```

**Question** : Pourquoi utilise-t-on `RwLock` plutôt que `Mutex` ici ? Dans quel cas `Mutex` serait-il préférable ?

---

## Partie 3 — Gestion des erreurs (30 min)

### 3.1 Type d'erreur API

Créez `src/errors.rs` :

```rust
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

#[derive(Debug)]
pub enum ApiError {
    TacheIntrouvable(uuid::Uuid),
    TransitionInvalide { de: String, vers: String },
    TitreVide,
    LimitePagination,
    ErreurInterne(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, code, message) = match &self {
            ApiError::TacheIntrouvable(id) => (
                StatusCode::NOT_FOUND,
                "TACHE_INTROUVABLE",
                format!("Tâche {} introuvable", id),
            ),
            ApiError::TransitionInvalide { de, vers } => (
                StatusCode::UNPROCESSABLE_ENTITY,
                "TRANSITION_INVALIDE",
                format!("Transition {} → {} non autorisée", de, vers),
            ),
            ApiError::TitreVide => (
                StatusCode::BAD_REQUEST,
                "TITRE_VIDE",
                "Le titre ne peut pas être vide".to_string(),
            ),
            ApiError::LimitePagination => (
                StatusCode::BAD_REQUEST,
                "LIMITE_PAGINATION",
                "La limite de pagination doit être entre 1 et 100".to_string(),
            ),
            ApiError::ErreurInterne(msg) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "ERREUR_INTERNE",
                msg.clone(),
            ),
        };

        let body = json!({
            "erreur": {
                "code": code,
                "message": message,
            }
        });

        (status, Json(body)).into_response()
    }
}

// Conversion depuis les erreurs de lock poisonné
impl<T> From<std::sync::PoisonError<T>> for ApiError {
    fn from(err: std::sync::PoisonError<T>) -> Self {
        ApiError::ErreurInterne(format!("Erreur de verrou: {}", err))
    }
}

// Type Result pratique
pub type ApiResult<T> = Result<T, ApiError>;
```

---

## Partie 4 — Handlers (60 min)

### 4.1 Squelette du module handlers

Créez `src/handlers.rs` :

```rust
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use chrono::Utc;
use uuid::Uuid;

use crate::{
    errors::{ApiError, ApiResult},
    models::*,
    state::AppState,
};

// ─── Créer une tâche ─────────────────────────────────────────────────────────

pub async fn creer_tache(
    State(state): State<AppState>,
    Json(req): Json<CreerTacheRequest>,
) -> ApiResult<(StatusCode, Json<Tache>)> {
    // TODO: Implémenter la création d'une tâche
    // 1. Valider que le titre n'est pas vide (trim)
    // 2. Créer une Tache avec un Uuid::new_v4(), statut EnAttente, timestamps Utc::now()
    // 3. Insérer dans state.taches
    // 4. Retourner (StatusCode::CREATED, Json(tache))
    todo!()
}

// ─── Lister les tâches avec filtres et pagination ────────────────────────────

pub async fn lister_taches(
    State(state): State<AppState>,
    Query(filtres): Query<FiltresTaches>,
) -> ApiResult<Json<PageTaches>> {
    // TODO: Implémenter la liste avec filtres
    // 1. Lire toutes les tâches (read lock)
    // 2. Filtrer par statut si fourni
    // 3. Filtrer par priorité si fournie
    // 4. Filtrer par tag si fourni (tache.tags.contains(&tag))
    // 5. Appliquer la pagination (page par défaut = 1, par_page par défaut = 20, max = 100)
    // 6. Retourner PageTaches avec total avant pagination
    todo!()
}

// ─── Obtenir une tâche par ID ─────────────────────────────────────────────────

pub async fn obtenir_tache(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> ApiResult<Json<Tache>> {
    // TODO: Obtenir une tâche par son ID
    // Retourner ApiError::TacheIntrouvable(id) si absente
    todo!()
}

// ─── Modifier une tâche (PATCH partiel) ──────────────────────────────────────

pub async fn modifier_tache(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
    Json(req): Json<ModifierTacheRequest>,
) -> ApiResult<Json<Tache>> {
    // TODO: Modifier partiellement une tâche
    // 1. Récupérer la tâche existante (erreur si absente)
    // 2. Appliquer seulement les champs Some(...)
    // 3. Mettre à jour modifie_le
    // 4. Valider le titre s'il est modifié (non vide)
    todo!()
}

// ─── Changer le statut ────────────────────────────────────────────────────────

pub async fn changer_statut(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
    Json(req): Json<MajStatutRequest>,
) -> ApiResult<Json<Tache>> {
    // TODO: Changer le statut avec validation des transitions
    // Transitions autorisées :
    //   EnAttente  → EnCours, Annulee
    //   EnCours    → Terminee, Annulee, EnAttente
    //   Terminee   → (aucune, état final)
    //   Annulee    → EnAttente (réouverture)
    //
    // Si la transition est Terminee : mettre termine_le = Some(Utc::now())
    // Si la transition depuis Terminee : remettre termine_le = None
    todo!()
}

// ─── Supprimer une tâche ──────────────────────────────────────────────────────

pub async fn supprimer_tache(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> ApiResult<StatusCode> {
    // TODO: Supprimer une tâche par ID
    // Retourner StatusCode::NO_CONTENT si supprimée
    // Retourner ApiError::TacheIntrouvable si absente
    todo!()
}

// ─── Statistiques ─────────────────────────────────────────────────────────────

pub async fn statistiques(
    State(state): State<AppState>,
) -> ApiResult<Json<serde_json::Value>> {
    // TODO: Calculer et retourner des statistiques
    // {
    //   "total": N,
    //   "par_statut": { "EN_ATTENTE": N, "EN_COURS": N, "TERMINEE": N, "ANNULEE": N },
    //   "par_priorite": { "BASSE": N, "NORMALE": N, "HAUTE": N, "CRITIQUE": N },
    //   "taux_completion": 0.75  // terminées / (total - annulées)
    // }
    todo!()
}
```

---

## Partie 5 — Router et main (20 min)

### 5.1 Fichier main.rs

```rust
mod errors;
mod handlers;
mod models;
mod state;
mod store;

use axum::{
    routing::{delete, get, patch, post},
    Router,
};
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use state::AppState;

#[tokio::main]
async fn main() {
    // Initialiser le logging
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "todo_api=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let state = AppState::new();

    let app = Router::new()
        // Routes tâches
        .route("/taches",     get(handlers::lister_taches).post(handlers::creer_tache))
        .route("/taches/:id", get(handlers::obtenir_tache)
                                  .patch(handlers::modifier_tache)
                                  .delete(handlers::supprimer_tache))
        .route("/taches/:id/statut", patch(handlers::changer_statut))
        // Statistiques
        .route("/stats", get(handlers::statistiques))
        // Santé
        .route("/health", get(|| async { "OK" }))
        // Middlewares
        .layer(TraceLayer::new_for_http())
        .layer(
            CorsLayer::new()
                .allow_origin(tower_http::cors::Any)
                .allow_methods(tower_http::cors::Any)
                .allow_headers(tower_http::cors::Any),
        )
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    tracing::info!("Serveur démarré sur http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

---

## Partie 6 — Tests avec curl (30 min)

Une fois votre API démarrée (`cargo run`), testez chaque endpoint :

### Créer des tâches

```bash
# Tâche simple
curl -X POST http://localhost:3000/taches \
  -H "Content-Type: application/json" \
  -d '{"titre": "Apprendre Rust", "priorite": "HAUTE", "tags": ["formation", "rust"]}'

# Tâche critique
curl -X POST http://localhost:3000/taches \
  -H "Content-Type: application/json" \
  -d '{"titre": "Fix production bug", "description": "Crash en production", "priorite": "CRITIQUE"}'

# Tâche avec priorité par défaut
curl -X POST http://localhost:3000/taches \
  -H "Content-Type: application/json" \
  -d '{"titre": "Mettre à jour la doc"}'

# Titre vide → doit retourner 400
curl -X POST http://localhost:3000/taches \
  -H "Content-Type: application/json" \
  -d '{"titre": "   "}'
```

### Lister et filtrer

```bash
# Toutes les tâches
curl http://localhost:3000/taches | jq

# Filtrer par statut
curl "http://localhost:3000/taches?statut=EN_ATTENTE" | jq

# Filtrer par priorité
curl "http://localhost:3000/taches?priorite=CRITIQUE" | jq

# Filtrer par tag
curl "http://localhost:3000/taches?tag=rust" | jq

# Pagination
curl "http://localhost:3000/taches?page=1&par_page=2" | jq
```

### Obtenir, modifier, changer statut

```bash
# Remplacer <ID> par un UUID retourné lors de la création
export ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Obtenir une tâche
curl http://localhost:3000/taches/$ID | jq

# Tâche inexistante → 404
curl http://localhost:3000/taches/00000000-0000-0000-0000-000000000000 | jq

# Modifier le titre et la priorité
curl -X PATCH http://localhost:3000/taches/$ID \
  -H "Content-Type: application/json" \
  -d '{"titre": "Maîtriser Rust", "priorite": "CRITIQUE"}' | jq

# Démarrer la tâche
curl -X PATCH http://localhost:3000/taches/$ID/statut \
  -H "Content-Type: application/json" \
  -d '{"statut": "EN_COURS"}' | jq

# Terminer la tâche
curl -X PATCH http://localhost:3000/taches/$ID/statut \
  -H "Content-Type: application/json" \
  -d '{"statut": "TERMINEE"}' | jq

# Transition invalide depuis TERMINEE → EN_COURS
curl -X PATCH http://localhost:3000/taches/$ID/statut \
  -H "Content-Type: application/json" \
  -d '{"statut": "EN_COURS"}' | jq
```

### Statistiques et suppression

```bash
# Statistiques
curl http://localhost:3000/stats | jq

# Supprimer
curl -X DELETE http://localhost:3000/taches/$ID
# → 204 No Content

# Supprimer à nouveau → 404
curl -X DELETE http://localhost:3000/taches/$ID | jq
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `cargo run` et montrer la sortie du compilateur quand `todo!()` est laissé dans le code. Montrer que le projet compile malgré les `todo!()` mais panique à l'exécution quand un endpoint est appelé. Montrer le message `not yet implemented` dans les logs.
> **Expliquer :** Expliquer que `todo!()` est une macro de développement qui compile mais panique. Contraster avec les erreurs de compilation : `todo!()` permet de construire le squelette du projet et de s'assurer que les types sont corrects avant d'implémenter le comportement.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer la séquence de tests curl en terminal côte à côte avec les logs Axum affichant les requêtes (TraceLayer). Montrer spécifiquement : 201 Created, 404 Not Found avec le JSON d'erreur structuré, 422 pour une transition invalide.
> **Expliquer :** Expliquer le format d'erreur standardisé (`{ "erreur": { "code": "...", "message": "..." } }`). Montrer comment `IntoResponse` pour `ApiError` centralise la gestion des erreurs : chaque handler retourne `ApiResult<T>` et le mapping HTTP est défini une seule fois.

---

## Partie 7 — Solutions commentées

### Handler creer_tache

```rust
pub async fn creer_tache(
    State(state): State<AppState>,
    Json(req): Json<CreerTacheRequest>,
) -> ApiResult<(StatusCode, Json<Tache>)> {
    let titre = req.titre.trim().to_string();
    if titre.is_empty() {
        return Err(ApiError::TitreVide);
    }

    let maintenant = Utc::now();
    let tache = Tache {
        id: Uuid::new_v4(),
        titre,
        description: req.description,
        statut: StatutTache::EnAttente,
        priorite: req.priorite,
        tags: req.tags,
        cree_le: maintenant,
        modifie_le: maintenant,
        termine_le: None,
    };

    let mut store = state.taches.write()?;
    store.insert(tache.id, tache.clone());

    Ok((StatusCode::CREATED, Json(tache)))
}
```

### Handler lister_taches

```rust
pub async fn lister_taches(
    State(state): State<AppState>,
    Query(filtres): Query<FiltresTaches>,
) -> ApiResult<Json<PageTaches>> {
    let par_page = filtres.par_page.unwrap_or(20);
    if par_page == 0 || par_page > 100 {
        return Err(ApiError::LimitePagination);
    }
    let page = filtres.page.unwrap_or(1).max(1);

    let store = state.taches.read()?;
    let mut taches: Vec<Tache> = store.values()
        .filter(|t| {
            filtres.statut.as_ref().map_or(true, |s| &t.statut == s)
        })
        .filter(|t| {
            filtres.priorite.as_ref().map_or(true, |p| &t.priorite == p)
        })
        .filter(|t| {
            filtres.tag.as_ref().map_or(true, |tag| t.tags.contains(tag))
        })
        .cloned()
        .collect();

    // Trier par date de création (plus récent en premier)
    taches.sort_by(|a, b| b.cree_le.cmp(&a.cree_le));

    let total = taches.len();
    let debut = (page - 1) * par_page;
    let taches_page: Vec<Tache> = taches.into_iter().skip(debut).take(par_page).collect();

    Ok(Json(PageTaches {
        taches: taches_page,
        total,
        page,
        par_page,
    }))
}
```

### Handler changer_statut

```rust
pub async fn changer_statut(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
    Json(req): Json<MajStatutRequest>,
) -> ApiResult<Json<Tache>> {
    let mut store = state.taches.write()?;
    let tache = store.get_mut(&id).ok_or(ApiError::TacheIntrouvable(id))?;

    // Valider la transition
    let transition_valide = match (&tache.statut, &req.statut) {
        (StatutTache::EnAttente, StatutTache::EnCours)   => true,
        (StatutTache::EnAttente, StatutTache::Annulee)   => true,
        (StatutTache::EnCours,   StatutTache::Terminee)  => true,
        (StatutTache::EnCours,   StatutTache::Annulee)   => true,
        (StatutTache::EnCours,   StatutTache::EnAttente) => true,
        (StatutTache::Annulee,   StatutTache::EnAttente) => true,
        (de, vers) if de == vers                         => true,  // pas de changement
        _                                                => false,
    };

    if !transition_valide {
        return Err(ApiError::TransitionInvalide {
            de: format!("{:?}", tache.statut),
            vers: format!("{:?}", req.statut),
        });
    }

    // Mise à jour timestamps spéciaux
    if req.statut == StatutTache::Terminee {
        tache.termine_le = Some(Utc::now());
    } else if tache.statut == StatutTache::Terminee {
        tache.termine_le = None;
    }

    tache.statut = req.statut;
    tache.modifie_le = Utc::now();

    Ok(Json(tache.clone()))
}
```

### Handler statistiques

```rust
pub async fn statistiques(
    State(state): State<AppState>,
) -> ApiResult<Json<serde_json::Value>> {
    use serde_json::json;
    use std::collections::HashMap;

    let store = state.taches.read()?;
    let taches: Vec<&Tache> = store.values().collect();
    let total = taches.len();

    let mut par_statut: HashMap<String, usize> = HashMap::new();
    let mut par_priorite: HashMap<String, usize> = HashMap::new();

    for tache in &taches {
        let statut_str = serde_json::to_value(&tache.statut)
            .unwrap()
            .as_str()
            .unwrap_or("INCONNU")
            .to_string();
        *par_statut.entry(statut_str).or_insert(0) += 1;

        let priorite_str = serde_json::to_value(&tache.priorite)
            .unwrap()
            .as_str()
            .unwrap_or("INCONNU")
            .to_string();
        *par_priorite.entry(priorite_str).or_insert(0) += 1;
    }

    let terminee = *par_statut.get("TERMINEE").unwrap_or(&0);
    let annulee  = *par_statut.get("ANNULEE").unwrap_or(&0);
    let taux_completion = if total > annulee {
        terminee as f64 / (total - annulee) as f64
    } else {
        0.0
    };

    Ok(Json(json!({
        "total": total,
        "par_statut": par_statut,
        "par_priorite": par_priorite,
        "taux_completion": (taux_completion * 100.0).round() / 100.0
    })))
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer le pattern `match (&tache.statut, &req.statut)` dans le handler `changer_statut`. Montrer que le compilateur exige un bras `_` ou que tous les cas soient couverts. Supprimer le bras `_` et montrer l'erreur du compilateur listant les cas manquants.
> **Expliquer :** Expliquer l'exhaustivité du pattern matching sur les tuples. C'est une des forces de Rust : si on ajoute un variant à `StatutTache`, le compilateur signale toutes les fonctions `match` à mettre à jour. Comparer avec un switch Java où un cas oublié est silencieux.

---

## Partie 8 — Challenge bonus (facultatif)

### 8.1 Ajouter des sous-tâches

Étendez le modèle `Tache` pour supporter des sous-tâches :

```rust
// Dans models.rs
pub struct Tache {
    // ... champs existants ...
    pub sous_taches: Vec<SousTache>,
}

pub struct SousTache {
    pub id: Uuid,
    pub titre: String,
    pub completee: bool,
}
```

Ajoutez les endpoints :
- `POST /taches/:id/sous-taches` — ajouter une sous-tâche
- `PATCH /taches/:id/sous-taches/:sous_id` — cocher/décocher
- `DELETE /taches/:id/sous-taches/:sous_id` — supprimer

**Contrainte** : Une tâche ne peut pas passer en `Terminee` si elle a des sous-tâches non complétées.

### 8.2 Middleware de logging personnalisé

Ajoutez un middleware qui log chaque requête avec le temps d'exécution :

```rust
async fn logging_middleware<B>(
    req: axum::http::Request<B>,
    next: axum::middleware::Next<B>,
) -> impl IntoResponse {
    let methode = req.method().clone();
    let uri = req.uri().clone();
    let debut = std::time::Instant::now();

    let response = next.run(req).await;

    let duree = debut.elapsed();
    tracing::info!(
        "{} {} → {} ({:?})",
        methode,
        uri,
        response.status(),
        duree
    );

    response
}
```

### 8.3 Tests d'intégration

Créez `src/tests.rs` :

```rust
#[cfg(test)]
mod tests {
    use axum::http::StatusCode;
    use axum_test::TestServer;  // axum-test = "0.15"
    use serde_json::json;

    use crate::{state::AppState, /* router */};

    fn app() -> axum::Router {
        // Créer l'application de test avec un état frais
        todo!()
    }

    #[tokio::test]
    async fn test_creer_tache() {
        let server = TestServer::new(app()).unwrap();

        let resp = server.post("/taches")
            .json(&json!({"titre": "Test"}))
            .await;

        assert_eq!(resp.status_code(), StatusCode::CREATED);
        let body: serde_json::Value = resp.json();
        assert_eq!(body["titre"], "Test");
        assert_eq!(body["statut"], "EN_ATTENTE");
    }

    #[tokio::test]
    async fn test_titre_vide_retourne_400() {
        let server = TestServer::new(app()).unwrap();

        let resp = server.post("/taches")
            .json(&json!({"titre": "  "}))
            .await;

        assert_eq!(resp.status_code(), StatusCode::BAD_REQUEST);
    }

    #[tokio::test]
    async fn test_transition_invalide() {
        // TODO: Créer une tâche, la terminer, tenter de la passer EN_COURS
        // Vérifier StatusCode::UNPROCESSABLE_ENTITY
        todo!()
    }
}
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| Tous les handlers compilent sans `todo!()` | 4 |
| Validation du titre (trim + vide) | 1 |
| Filtres (statut, priorité, tag) fonctionnels | 2 |
| Pagination correcte (page, par_page, total) | 2 |
| Transitions de statut validées | 3 |
| Format d'erreur JSON standardisé | 2 |
| Tests curl passent tous | 4 |
| Bonus : sous-tâches | +3 |
| Bonus : tests d'intégration | +3 |

**Total : 18 points (+ 6 bonus)**

---

## Points clés à retenir

1. `Arc<RwLock<HashMap>>` est le pattern standard pour l'état partagé en lecture-écriture dans Axum — `RwLock` permet plusieurs lecteurs simultanés contrairement à `Mutex`.

2. Le type `ApiResult<T> = Result<T, ApiError>` avec `impl IntoResponse for ApiError` centralise la gestion des erreurs HTTP : les handlers retournent `Err(ApiError::...)` et Axum appelle automatiquement `into_response()`.

3. `#[serde(rename_all = "camelCase")]` sur les structs et `#[serde(rename_all = "SCREAMING_SNAKE_CASE")]` sur les enums sont les conventions habituelles pour les APIs REST en Rust.

4. Le pattern `match (&statut_actuel, &nouveau_statut)` pour les machines d'état est idiomatique en Rust et le compilateur garantit l'exhaustivité.
