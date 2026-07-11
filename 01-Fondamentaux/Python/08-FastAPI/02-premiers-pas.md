# Module 02 — Premiers pas avec FastAPI

## Sommaire
1. [Votre première application FastAPI](#1-votre-première-application-fastapi)
2. [Lancer le serveur avec uvicorn](#2-lancer-le-serveur-avec-uvicorn)
3. [Rechargement automatique](#3-rechargement-automatique)
4. [Structure d'un projet FastAPI](#4-structure-dun-projet-fastapi)
5. [L'objet FastAPI et ses options](#5-lobjet-fastapi-et-ses-options)
6. [Les réponses automatiques](#6-les-réponses-automatiques)
7. [Codes de statut HTTP](#7-codes-de-statut-http)
8. [Middleware et configuration de base](#8-middleware-et-configuration-de-base)

---

## 1. Votre première application FastAPI

Créons le fichier le plus simple possible pour démarrer avec FastAPI.

### Le fichier `main.py`

```python
# main.py
from fastapi import FastAPI

# Créer l'instance de l'application
app = FastAPI()


# Définir une route GET sur "/"
@app.get("/")
def read_root():
    """Route d'accueil de l'API."""
    return {"message": "Bonjour depuis FastAPI !"}


# Une deuxième route avec un paramètre
@app.get("/items/{item_id}")
def read_item(item_id: int):
    """Récupérer un item par son ID."""
    return {"item_id": item_id, "name": f"Item numéro {item_id}"}
```

### Qu'est-ce qui se passe ici ?

1. `from fastapi import FastAPI` — on importe la classe principale
2. `app = FastAPI()` — on crée une instance de l'application
3. `@app.get("/")` — décorateur qui déclare une route GET sur le chemin `/`
4. `def read_root()` — la fonction qui sera appelée quand la route est sollicitée
5. `return {"message": "..."}` — FastAPI sérialise automatiquement le dict en JSON

### Points importants

- Le nom de la fonction (`read_root`) n'a pas d'importance pour le routage, mais il est utilisé dans la documentation Swagger
- Le docstring de la fonction devient la description dans la documentation
- FastAPI accepte `def` (synchrone) et `async def` (asynchrone)

---

## 2. Lancer le serveur avec uvicorn

### Commande de base

```bash
# Syntaxe : uvicorn <fichier>:<variable_app>
uvicorn main:app

# Résultat dans le terminal :
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal au moment du lancement de `uvicorn main:app` puis l'ouverture du navigateur sur `http://localhost:8000`
> **Expliquer :** Montrer le message de démarrage dans le terminal. Ouvrir le navigateur, aller sur `http://localhost:8000` et montrer la réponse JSON. Ensuite aller sur `http://localhost:8000/items/42` pour montrer le paramètre. Enfin, aller sur `http://localhost:8000/docs` pour révéler la Swagger UI générée automatiquement.

---

### Options importantes de uvicorn

```bash
# Spécifier le host et le port
uvicorn main:app --host 0.0.0.0 --port 8080

# Mode rechargement automatique (développement)
uvicorn main:app --reload

# Nombre de workers (production)
uvicorn main:app --workers 4

# Niveau de log
uvicorn main:app --log-level debug

# Combinaison typique pour le développement
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Combinaison typique pour la production
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Lancer depuis le code Python

On peut aussi lancer uvicorn directement depuis un fichier Python, ce qui est pratique dans certains contextes :

```python
# main.py
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello"}

# Ce bloc ne s'exécute que si on lance le fichier directement
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

```bash
# On peut alors lancer simplement
python main.py
```

---

## 3. Rechargement automatique

Le flag `--reload` est essentiel pendant le développement. Il surveille les modifications des fichiers et redémarre automatiquement le serveur.

```bash
uvicorn main:app --reload
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal en mode `--reload` pendant une modification de code
> **Expliquer :** Montrer le serveur lancé avec `--reload`. Modifier le message retourné dans `read_root()` (ex: "Bonjour" → "Hello world"). Sauvegarder le fichier. Montrer dans le terminal le message "WatchFiles detected changes in 'main.py', reloading...". Rafraîchir le navigateur pour voir le changement. Insister sur le fait que c'est un outil de développement uniquement, pas à utiliser en production.

---

### Ce que surveille `--reload`

Par défaut, `--reload` surveille :
- Les fichiers `.py` dans le répertoire courant
- Les fichiers `.py` dans les sous-répertoires

```bash
# Surveiller des répertoires supplémentaires
uvicorn main:app --reload --reload-dir src/ --reload-dir config/

# Surveiller des extensions supplémentaires
uvicorn main:app --reload --reload-include "*.html" --reload-include "*.yaml"
```

---

## 4. Structure d'un projet FastAPI

Pour un projet réel, un seul fichier `main.py` devient rapidement ingérable. Voici la structure recommandée.

### Projet minimal (petite API)

```
mon-projet/
├── main.py              # Point d'entrée
├── requirements.txt     # Dépendances
└── .env                 # Variables d'environnement (ne pas committer)
```

### Projet intermédiaire

```
mon-projet/
├── app/
│   ├── __init__.py
│   ├── main.py          # Création de l'app FastAPI
│   ├── config.py        # Configuration (settings)
│   ├── database.py      # Connexion à la base de données
│   │
│   ├── models/          # Modèles SQLAlchemy (tables DB)
│   │   ├── __init__.py
│   │   └── item.py
│   │
│   ├── schemas/         # Schémas Pydantic (validation)
│   │   ├── __init__.py
│   │   └── item.py
│   │
│   └── routers/         # Routes FastAPI (endpoints)
│       ├── __init__.py
│       └── items.py
│
├── tests/
│   ├── __init__.py
│   └── test_items.py
│
├── alembic/             # Migrations de base de données
├── alembic.ini
├── requirements.txt
├── .env
└── Dockerfile
```

### Projet avancé (microservices ou grande API)

```
mon-projet/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/                   # Versioning de l'API
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # Agrège toutes les routes v1
│   │   │   └── endpoints/
│   │   │       ├── items.py
│   │   │       ├── users.py
│   │   │       └── auth.py
│   │   └── deps.py               # Dépendances partagées
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, hachage
│   │   └── config.py             # Settings Pydantic
│   │
│   ├── models/                   # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── item.py
│   │   └── user.py
│   │
│   └── schemas/                  # Schémas Pydantic
│       ├── __init__.py
│       ├── item.py
│       └── user.py
│
├── tests/
├── alembic/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env
└── pyproject.toml
```

### Exemple de projet avec plusieurs fichiers

Voici comment structurer une petite API en plusieurs fichiers :

```python
# app/main.py
from fastapi import FastAPI
from app.routers import items, users

app = FastAPI(
    title="Mon API",
    description="Une API de démonstration FastAPI",
    version="1.0.0",
)

# Inclure les routers
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API"}
```

```python
# app/routers/items.py
from fastapi import APIRouter

router = APIRouter()

# Liste simulée d'items
fake_items_db = [
    {"item_id": 1, "name": "Pomme", "price": 0.5},
    {"item_id": 2, "name": "Banane", "price": 0.3},
    {"item_id": 3, "name": "Cerise", "price": 2.0},
]

@router.get("/")
def list_items():
    return fake_items_db

@router.get("/{item_id}")
def get_item(item_id: int):
    item = next((i for i in fake_items_db if i["item_id"] == item_id), None)
    if item is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Item non trouvé")
    return item
```

```python
# app/routers/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users():
    return [{"id": 1, "username": "alice"}, {"id": 2, "username": "bob"}]
```

```bash
# Lancer l'application (depuis la racine du projet)
uvicorn app.main:app --reload
```

---

## 5. L'objet FastAPI et ses options

L'instance `FastAPI()` accepte de nombreux paramètres pour configurer l'application.

```python
from fastapi import FastAPI

app = FastAPI(
    # Informations de base (visibles dans la doc Swagger)
    title="Mon Super API",
    description="""
    ## Description

    Cette API permet de gérer un catalogue de produits.

    ## Fonctionnalités

    * Créer des produits
    * Lister et filtrer les produits
    * Mettre à jour et supprimer
    """,
    version="2.1.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Support API",
        "url": "https://example.com/contact",
        "email": "api@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },

    # URLs des docs (on peut les changer ou les désactiver)
    docs_url="/docs",          # Swagger UI (défaut: /docs)
    redoc_url="/redoc",        # ReDoc (défaut: /redoc)
    openapi_url="/openapi.json",  # Schéma JSON (défaut: /openapi.json)

    # Désactiver les docs en production (optionnel)
    # docs_url=None,
    # redoc_url=None,
)
```

### Tags pour organiser la documentation

Les tags permettent de regrouper les endpoints dans Swagger UI.

```python
from fastapi import FastAPI

# Définir les métadonnées des tags
tags_metadata = [
    {
        "name": "items",
        "description": "Opérations sur les items. L'item peut être un produit, article, etc.",
    },
    {
        "name": "users",
        "description": "Gestion des utilisateurs et de l'authentification.",
    },
    {
        "name": "health",
        "description": "Health checks et métriques de l'API.",
    },
]

app = FastAPI(
    title="Mon API",
    openapi_tags=tags_metadata,
)

@app.get("/items/", tags=["items"])
def list_items():
    return []

@app.get("/users/", tags=["users"])
def list_users():
    return []

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
```

---

## 6. Les réponses automatiques

FastAPI convertit automatiquement les valeurs de retour en JSON.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    created_at: datetime

# Retourner un dictionnaire → JSON
@app.get("/dict")
def return_dict():
    return {"key": "value", "number": 42}

# Retourner une liste → JSON array
@app.get("/list")
def return_list():
    return [1, 2, 3, 4, 5]

# Retourner un modèle Pydantic → JSON
@app.get("/item")
def return_item():
    return Item(id=1, name="Test", created_at=datetime.now())
    # datetime est automatiquement sérialisée en ISO 8601

# Retourner None → corps vide avec 200
@app.get("/nothing")
def return_nothing():
    return None
```

### La classe Response

Pour un contrôle plus fin de la réponse :

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, RedirectResponse

app = FastAPI()

@app.get("/json")
def custom_json():
    return JSONResponse(
        content={"message": "ok"},
        status_code=200,
        headers={"X-Custom-Header": "my-value"}
    )

@app.get("/text")
def plain_text():
    return PlainTextResponse("Hello world !")

@app.get("/html")
def html_response():
    return HTMLResponse("<h1>Hello <b>world</b> !</h1>")

@app.get("/redirect")
def redirect():
    return RedirectResponse(url="https://fastapi.tiangolo.com")
```

---

## 7. Codes de statut HTTP

FastAPI utilise les codes HTTP standard. Voici les plus importants.

### Référence rapide

| Code | Nom | Signification |
|---|---|---|
| 200 | OK | Succès (GET, PUT, PATCH) |
| 201 | Created | Ressource créée (POST) |
| 204 | No Content | Succès sans corps (DELETE) |
| 400 | Bad Request | Requête malformée |
| 401 | Unauthorized | Non authentifié |
| 403 | Forbidden | Non autorisé (authentifié mais sans permission) |
| 404 | Not Found | Ressource introuvable |
| 409 | Conflict | Conflit (ex: email déjà utilisé) |
| 422 | Unprocessable Entity | Erreur de validation (Pydantic) |
| 500 | Internal Server Error | Erreur serveur |

### Utilisation dans FastAPI

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.post("/items/", status_code=status.HTTP_201_CREATED)
def create_item(name: str):
    # status.HTTP_201_CREATED vaut 201
    return {"name": name, "id": 1}

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    # Retourner None avec 204 = pas de corps
    return None

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        # Lever une HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} introuvable"
        )
    return {"item_id": item_id}
```

### HTTPException

`HTTPException` est le moyen standard de retourner des erreurs HTTP dans FastAPI.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

fake_db = {1: "Alice", 2: "Bob"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Utilisateur introuvable",
                "user_id": user_id,
                "suggestion": "Vérifiez l'ID utilisateur"
            }
        )
    return {"id": user_id, "name": fake_db[user_id]}
```

Réponse JSON générée par FastAPI :
```json
{
  "detail": {
    "message": "Utilisateur introuvable",
    "user_id": 99,
    "suggestion": "Vérifiez l'ID utilisateur"
  }
}
```

---

## 8. Middleware et configuration de base

### CORS (Cross-Origin Resource Sharing)

Le CORS est essentiel quand votre frontend (Vue.js, React...) est sur un domaine différent de votre API.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend Vue/React en dev
        "https://mon-site.com",     # Frontend en production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "CORS configuré !"}
```

> **Attention** : Ne jamais utiliser `allow_origins=["*"]` en production si votre API est authentifiée.

### Middleware de logging

```python
import time
import logging
from fastapi import FastAPI, Request

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware qui log toutes les requêtes."""
    start_time = time.time()

    # Appeler le prochain handler
    response = await call_next(request)

    # Calculer la durée
    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} "
        f"({duration:.3f}s)"
    )

    # Ajouter un header custom avec la durée
    response.headers["X-Process-Time"] = str(duration)

    return response
```

### Événements de démarrage et arrêt

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Méthode moderne (FastAPI 0.95+) : lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au démarrage
    print("Démarrage de l'application...")
    print("Connexion à la base de données...")
    # await database.connect()

    yield  # L'application tourne ici

    # Code exécuté à l'arrêt
    print("Arrêt de l'application...")
    # await database.disconnect()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "running"}
```

---

## Exercice pratique

Créez un fichier `main.py` avec les éléments suivants :

1. Une application FastAPI avec un titre et une description
2. Une route `GET /` qui retourne un message de bienvenue et la date/heure actuelle
3. Une route `GET /about` qui retourne des informations sur l'API (version, auteur)
4. Une route `GET /items/{item_id}` qui :
   - Accepte un `item_id` entier
   - Retourne un 404 si `item_id` est négatif
   - Retourne des informations fictives sur l'item sinon
5. Configurez le CORS pour autoriser `http://localhost:3000`

```python
# Solution proposée
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Mon API de formation",
    description="API créée pendant la formation FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API !",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/about")
def about():
    return {
        "api": "Formation FastAPI",
        "version": "1.0.0",
        "auteur": "Formation Data Engineer",
        "framework": "FastAPI",
    }

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=404,
            detail=f"ID invalide : {item_id}. L'ID doit être positif."
        )
    return {
        "item_id": item_id,
        "name": f"Produit #{item_id}",
        "price": item_id * 9.99,
        "available": True,
    }
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `FastAPI()` | Crée l'instance de l'application |
| `@app.get()` | Décorateur pour une route GET |
| `uvicorn main:app` | Lance le serveur |
| `--reload` | Rechargement automatique (dev only) |
| `HTTPException` | Pour retourner des erreurs HTTP |
| `status.HTTP_*` | Constantes pour les codes HTTP |
| `CORSMiddleware` | Pour autoriser les requêtes cross-origin |
| `lifespan` | Pour le code de démarrage/arrêt |

---

**Précédent** : [Module 01 — Introduction](./01-introduction.md)
**Suite** : [Module 03 — Routing et paramètres](./03-routing-parametres.md)
