# Module 01 — Introduction à FastAPI

## Sommaire
1. [Qu'est-ce que FastAPI ?](#quest-ce-que-fastapi)
2. [Pourquoi choisir FastAPI ?](#pourquoi-choisir-fastapi)
3. [Comparaison avec Flask et Django](#comparaison-avec-flask-et-django)
4. [ASGI vs WSGI](#asgi-vs-wsgi)
5. [Installation](#installation)
6. [L'écosystème FastAPI](#lécosystème-fastapi)

---

## 1. Qu'est-ce que FastAPI ?

**FastAPI** est un framework web Python moderne, créé par **Sebastián Ramírez** (tiangolo) et publié en 2018. Il est conçu spécifiquement pour la création d'**APIs REST** (et GraphQL) avec Python 3.7+.

### Les caractéristiques fondamentales

FastAPI repose sur trois piliers techniques :

1. **Starlette** : un framework ASGI léger et performant pour la partie réseau
2. **Pydantic** : une bibliothèque de validation de données basée sur les type hints Python
3. **Python type hints** : les annotations de type de Python 3.5+ (PEP 484)

La combinaison de ces trois éléments permet à FastAPI d'être à la fois :
- **Rapide à l'exécution** (performances comparables à Node.js et Go)
- **Rapide à développer** (réduction du code boilerplate de 40-60% selon les benchmarks)
- **Fiable** (validation automatique des données, typage fort)
- **Auto-documenté** (Swagger UI et ReDoc générés automatiquement)

### Qui utilise FastAPI ?

FastAPI est utilisé en production par des entreprises comme :
- **Microsoft** (pour certains de leurs services internes)
- **Uber** (pour leurs services de machine learning)
- **Netflix** (pour des pipelines de données)
- **Explosion AI** (les créateurs de spaCy)
- De nombreuses startups et scale-ups

---

## 2. Pourquoi choisir FastAPI ?

### Performance

FastAPI est l'un des frameworks Python les plus rapides disponibles. Selon les benchmarks indépendants (TechEmpower), il se positionne parmi les plus performants, dépassant largement Flask et Django.

```
Performances relatives (requêtes/seconde, ordre de grandeur) :
┌─────────────┬────────────────────┬────────────────┐
│ Framework   │ Req/sec (sync)     │ Req/sec (async)│
├─────────────┼────────────────────┼────────────────┤
│ FastAPI     │ ~10 000            │ ~30 000+       │
│ Flask       │ ~5 000             │ ~8 000         │
│ Django      │ ~3 000             │ ~5 000         │
│ Django REST │ ~2 000             │ ~4 000         │
└─────────────┴────────────────────┴────────────────┘
Note : ces chiffres varient selon le matériel et la charge
```

### Documentation automatique

C'est l'une des fonctionnalités les plus appréciées de FastAPI. En écrivant votre code normalement, vous obtenez **gratuitement** :

- **Swagger UI** : accessible à `/docs` — interface interactive pour tester vos routes
- **ReDoc** : accessible à `/redoc` — documentation plus lisible
- **OpenAPI JSON** : accessible à `/openapi.json` — schéma machine-lisible

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le navigateur sur `http://localhost:8000/docs` d'une application FastAPI simple
> **Expliquer :** Montrer comment la Swagger UI est générée automatiquement. Faire une démonstration en cliquant sur une route GET, puis sur "Try it out", puis "Execute". Montrer la réponse JSON et le code de statut. Insister sur le fait que cette doc est générée sans aucun effort supplémentaire.

---

### Validation des données

Avec Pydantic, FastAPI valide automatiquement :
- Les types des paramètres
- Les contraintes (min/max, longueur, regex...)
- La présence des champs obligatoires

En cas d'erreur, FastAPI renvoie automatiquement une réponse 422 avec le détail de l'erreur, sans que vous ayez à écrire de code de validation.

### Typage fort

FastAPI exploite pleinement les type hints Python. Cela signifie :
- L'autocomplétion fonctionne dans votre IDE
- Les erreurs sont détectées à l'écriture, pas à l'exécution
- Le code est auto-documenté

### Support async natif

FastAPI supporte nativement `async/await`. Vous pouvez écrire des handlers asynchrones sans configuration supplémentaire, ce qui est essentiel pour les opérations I/O (base de données, appels externes, etc.).

---

## 3. Comparaison avec Flask et Django

### Flask

Flask est un **micro-framework** minimaliste. Il est excellent pour les petits projets et les prototypes, mais manque de structure pour les grands projets.

| Critère | Flask | FastAPI |
|---|---|---|
| Type | Micro-framework WSGI | Framework ASGI |
| Validation | Manuelle (Marshmallow, WTForms) | Automatique (Pydantic) |
| Documentation | Manuelle (flask-swagger) | Automatique |
| Async | Via gevent/eventlet (hackish) | Natif |
| Courbe d'apprentissage | Faible | Faible à moyenne |
| Performances | Moyennes | Excellentes |
| Adapté pour | Petits projets, prototypes | APIs modernes, microservices |

**Exemple Flask vs FastAPI :**

```python
# Flask — endpoint basique
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    # Pas de validation automatique du type
    # Pas de documentation automatique
    return jsonify({"item_id": item_id})


# FastAPI — même endpoint
from fastapi import FastAPI

app = FastAPI()

@app.get('/items/{item_id}')
def get_item(item_id: int):
    # item_id est automatiquement validé comme entier
    # route documentée dans Swagger
    return {"item_id": item_id}
```

### Django REST Framework (DRF)

Django est un framework **batteries included** : il vient avec un ORM, un système d'administration, l'authentification, etc. Django REST Framework est une extension pour créer des APIs.

| Critère | Django REST | FastAPI |
|---|---|---|
| Type | Framework complet WSGI | Framework ASGI |
| ORM | Django ORM (intégré) | SQLAlchemy (à installer) |
| Admin | Interface admin intégrée | À faire manuellement |
| Validation | Serializers (verbeux) | Pydantic (concis) |
| Documentation | drf-yasg (config manuelle) | Automatique |
| Async | Partiel (Django 3.1+) | Natif |
| Courbe d'apprentissage | Élevée | Faible à moyenne |
| Adapté pour | Applications web complètes | APIs pures, microservices |

**Exemple DRF vs FastAPI :**

```python
# Django REST Framework — vue basique
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

class ItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    price = serializers.FloatField()

@api_view(['POST'])
def create_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data, status=201)
    return Response(serializer.errors, status=400)


# FastAPI — même fonctionnalité
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    item_id: int
    name: str
    price: float

@app.post('/items/', status_code=201)
def create_item(item: Item):
    return item
```

### Quand choisir quoi ?

```
Nouveau projet d'API ?
├── Besoin d'un admin Django, d'un ORM complet, d'une app web ?
│   └── → Django + DRF
│
├── Petit projet, prototype rapide, peu de validation ?
│   └── → Flask
│
└── API moderne, microservice, ML serving, haute performance ?
    └── → FastAPI ✓
```

---

## 4. ASGI vs WSGI

### WSGI — Web Server Gateway Interface

WSGI est le standard Python traditionnel pour les serveurs web (PEP 3333). Il est **synchrone** par nature : le serveur traite une requête à la fois par thread.

```
Client → Serveur WSGI → Application Flask/Django → Réponse
         (synchrone, bloque pendant le traitement)
```

Avec WSGI, si votre application fait une requête à une base de données (100ms), le thread est bloqué pendant ces 100ms et ne peut pas traiter d'autres requêtes.

**Serveurs WSGI courants** :
- Gunicorn
- uWSGI
- Waitress

### ASGI — Asynchronous Server Gateway Interface

ASGI est le successeur de WSGI, conçu pour gérer la concurrence et les WebSockets. Il supporte nativement `async/await`.

```
Client → Serveur ASGI → Application FastAPI → Réponse
         (asynchrone, peut traiter d'autres requêtes pendant l'attente)
```

Avec ASGI, si votre application fait une requête à une base de données (100ms), le serveur peut traiter d'autres requêtes pendant ce temps.

**Serveurs ASGI courants** :
- **uvicorn** (recommandé, le plus performant)
- Hypercorn
- Daphne

### Impact pratique

```python
# Handler WSGI (Flask) — synchrone
@app.route('/data')
def get_data():
    result = db.query(...)  # Bloque le thread pendant la requête SQL
    return jsonify(result)


# Handler ASGI (FastAPI) — asynchrone
@app.get('/data')
async def get_data():
    result = await db.execute(...)  # Libère le thread pendant la requête SQL
    return result
```

> **Remarque importante** : Vous pouvez aussi écrire des fonctions synchrones (`def` sans `async`) dans FastAPI. Dans ce cas, FastAPI les exécute dans un thread pool pour ne pas bloquer l'event loop. C'est utile si vous utilisez des bibliothèques qui ne supportent pas async.

---

## 5. Installation

### Installation minimale

```bash
# Installer FastAPI avec toutes les dépendances standard
pip install "fastapi[standard]"

# Cela installe :
# - fastapi
# - uvicorn[standard] (serveur ASGI)
# - pydantic (validation)
# - email-validator (pour les emails dans Pydantic)
# - python-multipart (pour les formulaires)
# - httpx (pour les tests)
```

### Installation avec uv (recommandé)

`uv` est un gestionnaire de paquets Python ultra-rapide écrit en Rust, développé par Astral (les créateurs de ruff).

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Créer un nouveau projet
uv init mon-api
cd mon-api

# Ajouter FastAPI
uv add "fastapi[standard]"

# Lancer un script
uv run uvicorn main:app --reload
```

### Vérification de l'installation

```bash
# Vérifier les versions installées
python -c "import fastapi; print(fastapi.__version__)"
python -c "import pydantic; print(pydantic.__version__)"
python -c "import uvicorn; print(uvicorn.__version__)"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant l'installation de FastAPI avec `pip install "fastapi[standard]"`
> **Expliquer :** Montrer la liste des packages installés. Pointer uvicorn, pydantic, starlette. Expliquer que "fastapi[standard]" est un raccourci qui installe toutes les dépendances utiles pour démarrer.

---

### Dépendances courantes selon le projet

```bash
# Pour une API avec base de données PostgreSQL
pip install "fastapi[standard]" sqlalchemy asyncpg alembic psycopg2-binary

# Pour l'authentification JWT
pip install python-jose[cryptography] passlib[bcrypt]

# Pour les tests
pip install pytest pytest-asyncio httpx

# Pour la configuration
pip install pydantic-settings python-dotenv
```

---

## 6. L'écosystème FastAPI

### Les bibliothèques complémentaires essentielles

| Bibliothèque | Rôle | Installation |
|---|---|---|
| **uvicorn** | Serveur ASGI | `pip install uvicorn[standard]` |
| **sqlalchemy** | ORM (base de données) | `pip install sqlalchemy` |
| **alembic** | Migrations de base de données | `pip install alembic` |
| **asyncpg** | Driver PostgreSQL async | `pip install asyncpg` |
| **python-jose** | Tokens JWT | `pip install python-jose[cryptography]` |
| **passlib** | Hachage de mots de passe | `pip install passlib[bcrypt]` |
| **pydantic-settings** | Configuration depuis env vars | `pip install pydantic-settings` |
| **python-dotenv** | Chargement des fichiers .env | `pip install python-dotenv` |
| **httpx** | Client HTTP (pour les tests) | `pip install httpx` |
| **pytest-asyncio** | Tests async avec pytest | `pip install pytest-asyncio` |

### L'écosystème OpenAPI

FastAPI génère automatiquement un schéma **OpenAPI 3.0**. Ce schéma est utilisable pour :

- Générer des clients dans d'autres langages (TypeScript, Java, Go...)
- Valider les requêtes/réponses dans un reverse proxy
- Générer de la documentation
- Faire du contract testing

```bash
# Récupérer le schéma OpenAPI de votre API
curl http://localhost:8000/openapi.json

# Utiliser openapi-generator pour créer un client TypeScript
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o ./frontend/src/api
```

---

## Récapitulatif

| Point clé | À retenir |
|---|---|
| FastAPI | Framework Python ASGI pour APIs REST modernes |
| Starlette | Base réseau de FastAPI |
| Pydantic | Validation des données via les type hints |
| ASGI | Standard asynchrone, successeur de WSGI |
| uvicorn | Serveur ASGI recommandé pour FastAPI |
| Swagger UI | Documentation interactive générée automatiquement à `/docs` |
| OpenAPI | Standard de description d'APIs, généré automatiquement |

---

**Suite** : [Module 02 — Premiers pas avec FastAPI](./02-premiers-pas.md)
