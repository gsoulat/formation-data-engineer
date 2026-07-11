# MLflow — Serving de modèles

## Qu'est-ce que le MLflow Serving ?

Une fois un modèle enregistré dans le registry, MLflow permet de le **servir comme une API REST** en une seule commande, sans écrire de code serveur. C'est le pont entre le modèle entraîné et les applications qui consomment les prédictions.

```
Model Registry
      │
      ▼
mlflow models serve  ──────▶  REST API  ──────▶  Client (app, script, test)
                              POST /invocations
                              GET /health
                              GET /version
```

---

## Serving via CLI — Le plus simple

```bash
# Servir la version Production d'un modèle enregistré
mlflow models serve \
  --model-uri "models:/prix-immobilier-rf/Production" \
  --host 0.0.0.0 \
  --port 8080 \
  --env-manager conda  # ou 'virtualenv' ou 'local'

# Servir une version spécifique
mlflow models serve \
  --model-uri "models:/prix-immobilier-rf/3" \
  --port 8080

# Servir depuis un run (sans registry)
mlflow models serve \
  --model-uri "runs:/abc123def456/model" \
  --port 8080

# Sans gestion d'environnement (plus rapide, si dépendances déjà installées)
mlflow models serve \
  --model-uri "models:/prix-immobilier-rf/Production" \
  --port 8080 \
  --env-manager local \
  --no-conda
```

---

## Tester l'API MLflow Serve

L'API MLflow attend les données dans un format JSON spécifique :

```bash
# Format 1 : dataframe_split (le plus courant)
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_split": {
      "columns": ["MedInc", "HouseAge", "AveRooms", "AveBedrms", "Population", "AveOccup", "Latitude", "Longitude"],
      "data": [[8.3252, 41.0, 6.984127, 1.023810, 322.0, 2.555556, 37.88, -122.23]]
    }
  }'
# Réponse : {"predictions": [4.526]}

# Format 2 : dataframe_records
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_records": [
      {"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984, "AveBedrms": 1.02,
       "Population": 322.0, "AveOccup": 2.56, "Latitude": 37.88, "Longitude": -122.23}
    ]
  }'

# Vérifier la santé du serveur
curl http://localhost:8080/health
# Réponse : OK

# Obtenir la version
curl http://localhost:8080/version
```

```python
# Appel depuis Python
import requests

url = "http://localhost:8080/invocations"

payload = {
    "dataframe_split": {
        "columns": ["MedInc", "HouseAge", "AveRooms", "AveBedrms",
                    "Population", "AveOccup", "Latitude", "Longitude"],
        "data": [
            [8.3252, 41.0, 6.984127, 1.023810, 322.0, 2.555556, 37.88, -122.23],
            [4.1521, 22.0, 5.963273, 1.040283, 2401.0, 2.109843, 37.86, -122.22]
        ]
    }
}

response = requests.post(url, json=payload)
predictions = response.json()
print(f"Prédictions : {predictions['predictions']}")
# Prédictions : [4.526, 2.374]
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans deux terminaux côte à côte : à gauche le serveur MLflow en cours d'exécution avec ses logs, à droite les commandes curl et leurs réponses JSON.
> **Expliquer :** "Remarquez qu'on n'a écrit aucun code serveur. MLflow a tout géré : chargement du modèle, sérialisation, API REST. C'est suffisant pour des prototypes ou des intégrations internes rapides."

---

## Construire une image Docker avec MLflow

MLflow peut construire une image Docker complète avec le modèle inclus :

```bash
# Construire l'image Docker
mlflow models build-docker \
  --model-uri "models:/prix-immobilier-rf/Production" \
  --name "prix-immobilier-api" \
  --env-manager local

# L'image est maintenant disponible localement
docker images | grep prix-immobilier

# Lancer le conteneur
docker run -p 8080:8080 prix-immobilier-api

# Avec des variables d'environnement
docker run -p 8080:8080 \
  -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
  prix-immobilier-api

# Pousser sur un registry Docker
docker tag prix-immobilier-api:latest registry.example.com/ml/prix-immobilier-api:v3
docker push registry.example.com/ml/prix-immobilier-api:v3
```

---

## API FastAPI personnalisée avec MLflow

Pour plus de contrôle, on construit sa propre API en utilisant MLflow pour charger le modèle :

```python
# api/main.py
import os
import time
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "prix-immobilier-rf")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")

# ── Initialisation de l'app ──────────────────────────────────────
app = FastAPI(
    title="Prix Immobilier API",
    description="API de prédiction du prix immobilier basée sur Random Forest",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Chargement du modèle au démarrage ────────────────────────────
@app.on_event("startup")
async def load_model():
    global MODEL, MODEL_VERSION, LOADED_AT

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
    logger.info(f"Chargement du modèle : {model_uri}")

    try:
        MODEL = mlflow.sklearn.load_model(model_uri)

        # Récupérer les métadonnées
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])
        if versions:
            MODEL_VERSION = versions[0].version
        else:
            MODEL_VERSION = "unknown"

        LOADED_AT = time.time()
        logger.info(f"Modèle v{MODEL_VERSION} chargé avec succès")

    except Exception as e:
        logger.error(f"Erreur lors du chargement : {e}")
        raise

# ── Schémas Pydantic ─────────────────────────────────────────────
class HouseFeatures(BaseModel):
    MedInc: float = Field(..., description="Revenu médian du quartier (en 10k$)", ge=0)
    HouseAge: float = Field(..., description="Âge médian des maisons", ge=0)
    AveRooms: float = Field(..., description="Nombre moyen de pièces", ge=0)
    AveBedrms: float = Field(..., description="Nombre moyen de chambres", ge=0)
    Population: float = Field(..., description="Population du quartier", ge=0)
    AveOccup: float = Field(..., description="Nombre moyen d'occupants", ge=0)
    Latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    Longitude: float = Field(..., description="Longitude", ge=-180, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.984127,
                "AveBedrms": 1.023810,
                "Population": 322.0,
                "AveOccup": 2.555556,
                "Latitude": 37.88,
                "Longitude": -122.23
            }
        }

class BatchRequest(BaseModel):
    houses: List[HouseFeatures]

class PredictionResponse(BaseModel):
    prix_predit: float
    model_version: str
    latency_ms: float

class BatchPredictionResponse(BaseModel):
    predictions: List[float]
    count: int
    model_version: str
    latency_ms: float

# ── Endpoints ────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "stage": MODEL_STAGE,
        "version": MODEL_VERSION,
        "uptime_seconds": int(time.time() - LOADED_AT)
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_single(features: HouseFeatures):
    start = time.time()

    try:
        data = pd.DataFrame([features.dict()])
        prediction = MODEL.predict(data)
        prix = float(prediction[0])

        latency = (time.time() - start) * 1000
        logger.info(f"Prédiction : {prix:.3f} (latence : {latency:.1f}ms)")

        return PredictionResponse(
            prix_predit=prix,
            model_version=str(MODEL_VERSION),
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        logger.error(f"Erreur de prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchRequest):
    start = time.time()

    try:
        data = pd.DataFrame([h.dict() for h in request.houses])
        predictions = MODEL.predict(data)

        latency = (time.time() - start) * 1000
        return BatchPredictionResponse(
            predictions=[float(p) for p in predictions],
            count=len(predictions),
            model_version=str(MODEL_VERSION),
            latency_ms=round(latency, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
def model_info():
    """Informations sur le modèle actuellement chargé."""
    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])

    if not versions:
        raise HTTPException(status_code=404, detail="Aucune version trouvée")

    v = versions[0]
    run = client.get_run(v.run_id)

    return {
        "model_name": MODEL_NAME,
        "version": v.version,
        "stage": v.current_stage,
        "run_id": v.run_id,
        "description": v.description,
        "creation_timestamp": v.creation_timestamp,
        "params": run.data.params,
        "metrics": run.data.metrics,
        "tags": run.data.tags
    }
```

```bash
# Lancer l'API FastAPI
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Documentation Swagger auto-générée
open http://localhost:8000/docs
```

---

## Dockerfile pour l'API FastAPI + MLflow

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY api/ ./api/

# Variables d'environnement par défaut
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV MODEL_NAME=prix-immobilier-rf
ENV MODEL_STAGE=Production
ENV PORT=8000

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```text
# requirements.txt
fastapi==0.111.0
uvicorn==0.30.0
mlflow==2.14.0
scikit-learn==1.5.0
pandas==2.2.0
numpy==1.26.0
pydantic==2.7.0
```

```bash
# Construire et lancer
docker build -t prix-immobilier-api:latest .

docker run -p 8000:8000 \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 \
  prix-immobilier-api:latest
```

---

## Exporter un modèle MLflow sans dépendance au tracking server

Parfois, on veut un modèle autonome qui n'a pas besoin de se connecter à un serveur MLflow :

```python
import mlflow

# Télécharger les artefacts du modèle localement
local_path = mlflow.artifacts.download_artifacts(
    "models:/prix-immobilier-rf/Production"
)
print(f"Modèle téléchargé dans : {local_path}")
# /tmp/mlflow-abc123/model

# Charger depuis le chemin local (sans connexion MLflow)
model = mlflow.sklearn.load_model(local_path)

# Sauvegarder le modèle en format MLflow local
mlflow.sklearn.save_model(
    sk_model=model,
    path="./model_export"
)

# L'image Docker peut maintenant inclure ce répertoire directement
```

Structure du répertoire exporté :
```
model_export/
├── MLmodel          ← Métadonnées du modèle (signature, loader)
├── model.pkl        ← Le modèle sérialisé
├── conda.yaml       ← Environnement conda
├── python_env.yaml  ← Environnement Python
└── requirements.txt ← Dépendances Python
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page Swagger de l'API FastAPI (`http://localhost:8000/docs`) avec le schéma du body de `/predict` visible, et ensuite le résultat d'un appel depuis l'interface Swagger UI.
> **Expliquer :** "Voici l'API auto-documentée. Chaque data scientist peut tester son modèle sans écrire de code client. En production, cette documentation est également consommée par les équipes applicatives pour intégrer les prédictions."

---

## Stratégies de déploiement avancées

### Blue-Green Deployment

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
           ┌─────────────────┴──────────────────┐
           │                                    │
    ┌──────▼──────┐                    ┌────────▼──────┐
    │  BLUE (v2)  │                    │  GREEN (v3)   │
    │   100%      │   ────switch────▶  │    100%       │
    │  trafic     │                    │   trafic      │
    └─────────────┘                    └───────────────┘
     (ancienne prod)                    (nouvelle prod)
```

### Canary Release

```python
# Envoi progressif du trafic vers la nouvelle version
import random

def route_prediction(features, canary_percentage=10):
    """
    Envoie `canary_percentage`% du trafic vers la nouvelle version.
    """
    if random.randint(1, 100) <= canary_percentage:
        # Canary : nouvelle version
        pred = model_v3.predict(features)
        version_used = "v3-canary"
    else:
        # Production stable : ancienne version
        pred = model_v2.predict(features)
        version_used = "v2-stable"

    # Logger pour analyser l'impact
    logger.info(f"version={version_used}, prediction={pred}")
    return pred, version_used
```

---

## Résumé des options de serving

| Option | Avantages | Inconvénients | Usage |
|---|---|---|---|
| `mlflow models serve` | Zero code | Peu de contrôle | Prototypes |
| FastAPI + MLflow | Contrôle total | Plus de code | Production |
| Docker MLflow | Portable | Build long | CI/CD |
| BentoML | Fonctionnalités avancées | Dépendance supplémentaire | Production avancée |
| Seldon Core | Kubernetes natif | Complexité K8s | Scale enterprise |
