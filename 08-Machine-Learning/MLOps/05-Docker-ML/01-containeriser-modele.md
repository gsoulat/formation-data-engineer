# Docker — Conteneuriser un modèle ML

## Pourquoi Docker pour le ML ?

Sans Docker, le problème classique est : "Ça marche sur mon ordi". En ML, cette phrase prend une dimension supplémentaire : les versions de bibliothèques ML (scikit-learn, numpy, pandas) ont des impacts majeurs sur les résultats des prédictions.

```
Développeur                    Serveur de production
numpy 1.24                     numpy 1.26
scikit-learn 1.3               scikit-learn 1.5
pandas 1.5                     pandas 2.2
model.pkl ──── envoi ────▶  ImportError / résultats différents
```

Avec Docker :
```
Développeur                    Serveur de production
                ┌─────────────────────────┐
model.pkl ──▶  │  python:3.11             │  ──▶  Identique
requirements   │  numpy==1.26.0           │       dans tous
code           │  scikit-learn==1.5.0     │       les environnements
               │  pandas==2.2.0           │
               │  fastapi + uvicorn       │
               └─────────────────────────┘
                        Image Docker
```

---

## Projet fil rouge : API de prédiction immobilière

Structure du projet :

```
prix-immobilier-api/
├── api/
│   ├── __init__.py
│   ├── main.py           ← API FastAPI
│   ├── model.py          ← Chargement et prédiction
│   └── schemas.py        ← Modèles Pydantic
├── models/
│   └── model.pkl         ← Modèle entraîné
├── scripts/
│   └── train.py          ← Script d'entraînement
├── tests/
│   └── test_api.py       ← Tests de l'API
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

---

## L'application FastAPI

```python
# api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class HouseFeatures(BaseModel):
    MedInc: float = Field(..., ge=0, description="Revenu médian")
    HouseAge: float = Field(..., ge=0, description="Âge de la maison")
    AveRooms: float = Field(..., ge=0, description="Nb moyen de pièces")
    AveBedrms: float = Field(..., ge=0, description="Nb moyen de chambres")
    Population: float = Field(..., ge=0, description="Population quartier")
    AveOccup: float = Field(..., ge=0, description="Nb moyen d'occupants")
    Latitude: float = Field(..., ge=-90, le=90)
    Longitude: float = Field(..., ge=-180, le=180)

    model_config = {
        "json_schema_extra": {
            "example": {
                "MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984,
                "AveBedrms": 1.024, "Population": 322.0, "AveOccup": 2.556,
                "Latitude": 37.88, "Longitude": -122.23
            }
        }
    }

class PredictionResponse(BaseModel):
    prix_predit: float
    unite: str = "centaines_de_milliers_USD"
    model_version: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
```

```python
# api/model.py
import pickle
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/model.pkl")
_model = None

def load_model():
    """Charge le modèle depuis le disque."""
    global _model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)
    logger.info(f"Modèle chargé depuis {MODEL_PATH}")
    return _model

def get_model():
    """Retourne le modèle (le charge si nécessaire)."""
    global _model
    if _model is None:
        load_model()
    return _model

def predict(features: dict) -> float:
    """Effectue une prédiction."""
    model = get_model()
    df = pd.DataFrame([features])
    prediction = model.predict(df)
    return float(prediction[0])
```

```python
# api/main.py
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .schemas import HouseFeatures, PredictionResponse, HealthResponse
from .model import load_model, predict

# ── Configuration du logging ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ── Métriques Prometheus ──────────────────────────────────────────
PREDICTION_COUNTER = Counter(
    "predictions_total",
    "Nombre total de prédictions",
    ["status"]
)
PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Latence des prédictions",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# ── Lifecycle de l'application ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Chargement au démarrage, nettoyage à l'arrêt."""
    logger.info("Démarrage de l'API — chargement du modèle...")
    try:
        load_model()
        logger.info("Modèle chargé avec succès")
    except Exception as e:
        logger.error(f"Erreur de chargement du modèle : {e}")
        raise
    yield
    logger.info("Arrêt de l'API")

app = FastAPI(
    title="Prix Immobilier API",
    description="Prédiction du prix de l'immobilier californien",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Endpoints ──────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health():
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        version="1.0.0"
    )

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Endpoint Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
def predict_price(features: HouseFeatures):
    """Prédit le prix d'un bien immobilier."""
    start = time.time()

    try:
        prix = predict(features.model_dump())
        PREDICTION_COUNTER.labels(status="success").inc()
        PREDICTION_LATENCY.observe(time.time() - start)

        logger.info(f"Prédiction : {prix:.3f}")
        return PredictionResponse(prix_predit=prix)

    except Exception as e:
        PREDICTION_COUNTER.labels(status="error").inc()
        logger.error(f"Erreur de prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Le Dockerfile

```dockerfile
# Dockerfile
# ── Stage 1 : Entraînement du modèle ─────────────────────────────
FROM python:3.11-slim AS trainer

WORKDIR /train

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/train.py .
# Entraîner le modèle et sauvegarder
RUN python train.py

# ── Stage 2 : Application de production ───────────────────────────
FROM python:3.11-slim AS production

# Métadonnées OCI
LABEL org.opencontainers.image.title="Prix Immobilier API"
LABEL org.opencontainers.image.description="API ML de prédiction immobilière"
LABEL org.opencontainers.image.authors="formation@datascience.com"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/model.pkl \
    PORT=8000

WORKDIR /app

# Installer uniquement les dépendances runtime (pas les outils ML de dev)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copier l'application
COPY api/ ./api/

# Copier le modèle entraîné depuis le stage trainer
COPY --from=trainer /train/models/model.pkl ./models/model.pkl

# Créer un utilisateur non-root
RUN useradd --uid 1000 --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "
import urllib.request, sys
try:
    urllib.request.urlopen('http://localhost:8000/health', timeout=5)
    sys.exit(0)
except:
    sys.exit(1)
"

CMD ["python", "-m", "uvicorn", "api.main:app",
     "--host", "0.0.0.0",
     "--port", "8000",
     "--workers", "2"]
```

---

## Le fichier .dockerignore

```
# .dockerignore
# Git
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
*.egg-info/
dist/
build/
.venv/
venv/
env/

# DVC
.dvc/cache/

# IDE
.vscode/
.idea/

# Données lourdes (non nécessaires dans l'image)
data/raw/
data/processed/

# Notebooks
*.ipynb
notebooks/

# Documentation
*.md
docs/

# Secrets
.env
.env.*
secrets/
```

---

## Construire et tester l'image

```bash
# ── Build ──────────────────────────────────────────────────────
docker build -t prix-immobilier-api:latest .

# Build avec args
docker build \
  --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  -t prix-immobilier-api:$(git rev-parse --short HEAD) \
  -t prix-immobilier-api:latest \
  .

# Vérifier la taille
docker images prix-immobilier-api
# REPOSITORY              TAG    IMAGE ID  CREATED        SIZE
# prix-immobilier-api    latest  abc123    2 minutes ago  512MB

# ── Lancer le conteneur ────────────────────────────────────────
docker run -d \
  --name prix-api \
  -p 8000:8000 \
  -e MODEL_PATH=/app/models/model.pkl \
  prix-immobilier-api:latest

# Voir les logs
docker logs -f prix-api

# ── Tester l'API ──────────────────────────────────────────────
# Health check
curl http://localhost:8000/health

# Prédiction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.984127,
    "AveBedrms": 1.023810,
    "Population": 322.0,
    "AveOccup": 2.555556,
    "Latitude": 37.88,
    "Longitude": -122.23
  }'
# {"prix_predit": 4.526, "unite": "centaines_de_milliers_USD"}

# ── Arrêter et nettoyer ────────────────────────────────────────
docker stop prix-api && docker rm prix-api
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le `docker build` en cours (montrant les layers qui se créent), puis le `docker run` suivi d'un `curl` vers l'endpoint `/predict` avec la réponse JSON visible.
> **Expliquer :** "Regardez les layers Docker : chaque ligne du Dockerfile est une couche. Si on relance le build sans modifier les dépendances, Docker réutilise le cache pour les premières étapes. Seules les couches qui ont changé sont reconstruites — gain de temps considérable en CI."

---

## Tests de l'API Docker

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestAPI:

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True

    def test_predict_valid(self):
        response = client.post("/predict", json={
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        })
        assert response.status_code == 200
        data = response.json()
        assert "prix_predit" in data
        assert data["prix_predit"] > 0
        assert data["prix_predit"] < 20  # plage réaliste

    def test_predict_invalid_negative_income(self):
        response = client.post("/predict", json={
            "MedInc": -1.0,  # invalide
            "HouseAge": 41.0,
            "AveRooms": 6.984,
            "AveBedrms": 1.024,
            "Population": 322.0,
            "AveOccup": 2.556,
            "Latitude": 37.88,
            "Longitude": -122.23
        })
        assert response.status_code == 422  # Validation error

    def test_predict_missing_field(self):
        response = client.post("/predict", json={
            "MedInc": 8.3252
            # champs manquants
        })
        assert response.status_code == 422
```

```bash
# Lancer les tests
pytest tests/test_api.py -v

# Tests avec coverage
pytest tests/ --cov=api --cov-report=html
```

---

## Optimiser la taille de l'image

```dockerfile
# Comparaison des tailles d'images de base
# python:3.11            → ~1.0 Go
# python:3.11-slim       → ~150 Mo
# python:3.11-alpine     → ~50 Mo  (mais incompatibilités possibles avec scipy/numpy)

# Stratégies pour réduire la taille :

# 1. Combiner les RUN en une seule couche
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 2. Utiliser le multi-stage build (séparation train/serve)

# 3. Exclure les outils de développement
# requirements-dev.txt : pytest, black, mypy, jupyter
# requirements.txt : fastapi, uvicorn, scikit-learn, pandas, numpy

# 4. Ne copier que le strict nécessaire
COPY api/ ./api/           # ← Seulement le code de l'API
COPY models/ ./models/     # ← Seulement le modèle
# PAS les notebooks, tests, scripts d'entraînement
```

---

## Variables d'environnement et configuration

```python
# api/config.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_path: str = "/app/models/model.pkl"
    mlflow_tracking_uri: str = "http://mlflow:5000"
    model_name: str = "prix-immobilier-rf"
    model_stage: str = "Production"
    log_level: str = "INFO"
    workers: int = 2
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

```bash
# Lancer avec des variables d'environnement
docker run -d \
  -p 8000:8000 \
  -e MODEL_PATH=/app/models/custom_model.pkl \
  -e LOG_LEVEL=DEBUG \
  -e WORKERS=4 \
  -v /host/models:/app/models \  # Monter le dossier models
  prix-immobilier-api:latest
```

---

## Résumé : Dockerfile ML checklist

```
Dockerfile ML — Bonnes pratiques :
────────────────────────────────────
✓ python:3.11-slim (pas python:3.11)
✓ Multi-stage build si entraînement inclus
✓ .dockerignore complet
✓ Utilisateur non-root (sécurité)
✓ HEALTHCHECK configuré
✓ Variables d'environnement pour la configuration
✓ PYTHONDONTWRITEBYTECODE=1 et PYTHONUNBUFFERED=1
✓ pip cache purge après installation
✓ Séparer requirements dev et prod
```
