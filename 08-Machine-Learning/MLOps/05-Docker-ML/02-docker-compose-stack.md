# Docker Compose — Stack MLOps complète

## Architecture de la stack

Une stack MLOps complète réunit plusieurs services qui collaborent :

```
┌──────────────────────────────────────────────────────────────────┐
│                     STACK MLOPS DOCKER COMPOSE                   │
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐  │
│  │  API ML     │    │   MLflow     │    │    PostgreSQL        │  │
│  │  (FastAPI)  │    │   Tracking   │    │  (backend MLflow)   │  │
│  │  :8000      │    │  Server :5000│    │  :5432              │  │
│  └──────┬──────┘    └──────┬───────┘    └──────────┬──────────┘  │
│         │                 │                        │             │
│         └────────────────▶│◀───────────────────────┘             │
│                           │                                      │
│  ┌─────────────┐    ┌──────┴───────┐    ┌─────────────────────┐  │
│  │  Prometheus │    │   MinIO      │    │      Grafana         │  │
│  │  Métriques  │    │  (S3 local)  │    │   Dashboards        │  │
│  │  :9090      │    │  :9000/:9001 │    │  :3000              │  │
│  └─────────────┘    └──────────────┘    └─────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## docker-compose.yml — Stack complète

```yaml
# docker-compose.yml
version: '3.9'

# ── Réseaux ────────────────────────────────────────────────────────
networks:
  mlops-network:
    driver: bridge

# ── Volumes persistants ────────────────────────────────────────────
volumes:
  postgres_data:
  mlflow_artifacts:
  minio_data:
  prometheus_data:
  grafana_data:

services:

  # ────────────────────────────────────────────────────────────────
  # Base de données PostgreSQL (backend MLflow)
  # ────────────────────────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: mlops-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow_secret
      POSTGRES_DB: mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - mlops-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mlflow"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ────────────────────────────────────────────────────────────────
  # MinIO — Stockage S3-compatible pour les artefacts MLflow
  # ────────────────────────────────────────────────────────────────
  minio:
    image: minio/minio:latest
    container_name: mlops-minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"   # API S3
      - "9001:9001"   # Console web
    networks:
      - mlops-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # ────────────────────────────────────────────────────────────────
  # Init MinIO — Créer le bucket mlflow-artifacts
  # ────────────────────────────────────────────────────────────────
  minio-init:
    image: minio/mc:latest
    container_name: mlops-minio-init
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set myminio http://minio:9000 minioadmin minioadmin123;
      mc mb --ignore-existing myminio/mlflow-artifacts;
      mc mb --ignore-existing myminio/dvc-store;
      echo 'Buckets créés';
      "
    networks:
      - mlops-network

  # ────────────────────────────────────────────────────────────────
  # MLflow Tracking Server
  # ────────────────────────────────────────────────────────────────
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.14.0
    container_name: mlops-mlflow
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      minio-init:
        condition: service_completed_successfully
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin123
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow_secret@postgres:5432/mlflow
      --default-artifact-root s3://mlflow-artifacts/
      --host 0.0.0.0
      --port 5000
    ports:
      - "5000:5000"
    networks:
      - mlops-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # ────────────────────────────────────────────────────────────────
  # API ML — Modèle de prédiction
  # ────────────────────────────────────────────────────────────────
  ml-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mlops-api
    restart: unless-stopped
    depends_on:
      mlflow:
        condition: service_healthy
    environment:
      MLFLOW_TRACKING_URI: http://mlflow:5000
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin123
      MODEL_NAME: prix-immobilier-rf
      MODEL_STAGE: Production
      PORT: 8000
    ports:
      - "8000:8000"
    networks:
      - mlops-network
    volumes:
      - ./models:/app/models:ro  # Lecture seule
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # ────────────────────────────────────────────────────────────────
  # Prometheus — Collecte de métriques
  # ────────────────────────────────────────────────────────────────
  prometheus:
    image: prom/prometheus:v2.52.0
    container_name: mlops-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=15d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - mlops-network

  # ────────────────────────────────────────────────────────────────
  # Grafana — Tableaux de bord
  # ────────────────────────────────────────────────────────────────
  grafana:
    image: grafana/grafana:10.4.0
    container_name: mlops-grafana
    restart: unless-stopped
    depends_on:
      - prometheus
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
    ports:
      - "3000:3000"
    networks:
      - mlops-network
```

---

## Configuration Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Scraper Prometheus lui-même
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Scraper l'API ML
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Scraper MLflow (si exposition de métriques activée)
  - job_name: 'mlflow'
    static_configs:
      - targets: ['mlflow:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Scraper les conteneurs Docker (avec cAdvisor)
  - job_name: 'docker'
    static_configs:
      - targets: ['cadvisor:8080']
```

---

## Démarrer et gérer la stack

```bash
# ── Démarrer toute la stack ────────────────────────────────────
docker compose up -d

# Suivre les logs au démarrage
docker compose logs -f

# ── Voir l'état des services ───────────────────────────────────
docker compose ps
# NAME               IMAGE                    STATUS    PORTS
# mlops-api          prix-immobilier-api      healthy   0.0.0.0:8000
# mlops-grafana      grafana/grafana          running   0.0.0.0:3000
# mlops-minio        minio/minio              healthy   0.0.0.0:9000
# mlops-mlflow       mlflow/mlflow            healthy   0.0.0.0:5000
# mlops-postgres     postgres:16-alpine       healthy   0.0.0.0:5432
# mlops-prometheus   prom/prometheus          running   0.0.0.0:9090

# ── Accéder aux interfaces ─────────────────────────────────────
# MLflow UI       : http://localhost:5000
# API prédictions : http://localhost:8000/docs
# MinIO Console  : http://localhost:9001  (minioadmin/minioadmin123)
# Prometheus     : http://localhost:9090
# Grafana        : http://localhost:3000  (admin/admin123)

# ── Redémarrer un service ──────────────────────────────────────
docker compose restart ml-api

# ── Reconstruire une image et redémarrer ──────────────────────
docker compose up -d --build ml-api

# ── Arrêter et supprimer (garder les volumes) ──────────────────
docker compose down

# Supprimer aussi les volumes (perte de données !)
docker compose down -v
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal avec `docker compose ps` montrant tous les services en état "healthy" avec leurs ports, puis ouvrir successivement dans le navigateur : MLflow UI, API Swagger, MinIO Console, Grafana — montrer la connexion entre les services.
> **Expliquer :** "Toute cette infrastructure complexe se lance en une seule commande : `docker compose up -d`. C'est reproductible sur n'importe quelle machine. Un nouveau développeur peut avoir l'environnement complet en 5 minutes au lieu de 2 jours."

---

## Entraîner un modèle depuis la stack

```python
# scripts/train_with_stack.py
"""
Script d'entraînement qui utilise la stack Docker Compose complète.
À lancer depuis l'hôte (pas depuis un conteneur).
"""
import os
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from mlflow.models.signature import infer_signature

# Pointer vers le serveur MLflow de la stack
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin123"

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("prix-immobilier-stack")

# Données
housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = pd.Series(housing.target)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

with mlflow.start_run(run_name="rf_via_stack"):
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    mlflow.log_params({"n_estimators": 100, "max_depth": 10})
    mlflow.log_metric("rmse", rmse)

    signature = infer_signature(X_train, model.predict(X_train))
    mlflow.sklearn.log_model(
        model, "model",
        signature=signature,
        registered_model_name="prix-immobilier-rf"
    )

    print(f"RMSE: {rmse:.4f}")
    print(f"Artefacts stockés dans MinIO : s3://mlflow-artifacts/")
    print(f"Voir le run : http://localhost:5000")
```

---

## Profil Docker Compose (stack partielle)

```yaml
# docker-compose.yml — avec profils
services:
  postgres:
    profiles: ["core", "full"]
    # ...

  mlflow:
    profiles: ["core", "full"]
    # ...

  ml-api:
    profiles: ["core", "full"]
    # ...

  prometheus:
    profiles: ["monitoring", "full"]
    # ...

  grafana:
    profiles: ["monitoring", "full"]
    # ...
```

```bash
# Stack minimale (MLflow + DB + API)
docker compose --profile core up -d

# Stack monitoring seule
docker compose --profile monitoring up -d

# Stack complète
docker compose --profile full up -d
```

---

## docker-compose.override.yml pour le développement

```yaml
# docker-compose.override.yml (non commité dans Git)
# Fichier chargé automatiquement par Docker Compose en dev

services:
  ml-api:
    build:
      target: production
    volumes:
      # Hot-reload du code en développement
      - ./api:/app/api
      - ./models:/app/models
    environment:
      LOG_LEVEL: DEBUG
    command: >
      python -m uvicorn api.main:app
      --host 0.0.0.0
      --port 8000
      --reload  # ← Hot-reload activé

  mlflow:
    # Moins de ressources en dev
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## Vérifier la connectivité entre services

```bash
# Entrer dans le conteneur de l'API
docker compose exec ml-api bash

# Tester la connexion à MLflow
curl http://mlflow:5000/health

# Tester la connexion à MinIO
curl http://minio:9000/minio/health/live

# Vérifier les variables d'environnement
env | grep MLFLOW

# Quitter
exit
```

```python
# health_check_stack.py — vérifier que tous les services répondent
import requests
import sys

services = {
    "ML API": "http://localhost:8000/health",
    "MLflow": "http://localhost:5000/health",
    "Prometheus": "http://localhost:9090/-/healthy",
    "Grafana": "http://localhost:3000/api/health",
    "MinIO": "http://localhost:9000/minio/health/live",
}

all_ok = True
for name, url in services.items():
    try:
        r = requests.get(url, timeout=5)
        status = "OK" if r.status_code in (200, 204) else f"FAIL ({r.status_code})"
    except Exception as e:
        status = f"ERREUR ({e})"
        all_ok = False
    print(f"{name:20} : {status}")

sys.exit(0 if all_ok else 1)
```

---

## Résumé des services

| Service | URL | Rôle | Identifiants |
|---|---|---|---|
| ML API | http://localhost:8000/docs | Prédictions | - |
| MLflow | http://localhost:5000 | Tracking | - |
| MinIO | http://localhost:9001 | Stockage S3 | minioadmin/minioadmin123 |
| Prometheus | http://localhost:9090 | Métriques | - |
| Grafana | http://localhost:3000 | Dashboards | admin/admin123 |
| PostgreSQL | localhost:5432 | BDD MLflow | mlflow/mlflow_secret |
