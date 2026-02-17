# Chapitre 16 : Docker, Monitoring et la Vie en Production

## 🎯 Objectifs

- Comprendre pourquoi **Docker** est indispensable pour le ML en production
- Savoir écrire un **Dockerfile optimisé** pour une API ML
- Maîtriser **Docker Compose** pour orchestrer API + monitoring
- Comprendre les **3 niveaux de monitoring** (technique, données, métier)
- Détecter le **data drift** et savoir quand retrainer un modèle
- Découvrir **MLflow** pour le tracking d'expériences
- Mettre en place une **CI/CD** basique pour le ML

> **Phase 6 - Semaine 16**

---

## 1. 🐳 Pourquoi Docker pour le ML

### 1.1 Le problème classique

```
Développeur : "Ça marche sur ma machine !"
Ops         : "Pas chez nous."
Développeur : "T'as bien Python 3.11 ? Avec numpy 1.24.3 ? Et scikit-learn 1.3.0 ?"
Ops         : "On a Python 3.9 et numpy 1.21..."
Développeur : "..."
```

Docker résout ce problème en empaquetant **tout** dans un conteneur : le code, les dépendances, le système d'exploitation.

### 1.2 Les avantages pour le ML

| Avantage | Description |
|----------|-------------|
| **Reproductibilité** | Même environnement partout (dev, staging, prod) |
| **Isolation** | Pas de conflits entre dépendances de projets différents |
| **Déploiement** | Un seul `docker run` pour lancer l'API |
| **Scaling** | Facile de lancer plusieurs instances |
| **Rollback** | Revenir à une version précédente en changeant le tag |

```
SANS Docker :                        AVEC Docker :
┌─────────────┐                     ┌─────────────────────┐
│  Ma machine │                     │  Conteneur Docker   │
│             │                     │ ┌─────────────────┐ │
│  Python 3.11│                     │ │ Python 3.11     │ │
│  numpy 1.24 │  ≠  Serveur prod   │ │ numpy 1.24      │ │
│  sklearn 1.3│     Python 3.9     │ │ sklearn 1.3     │ │
│             │     numpy 1.21     │ │ Mon code + modèle│ │
└─────────────┘                     │ └─────────────────┘ │
                                    └─────────────────────┘
                                     = IDENTIQUE partout
```

---

## 2. 📄 Dockerfile optimisé pour ML

### 2.1 Dockerfile complet

```dockerfile
# Dockerfile

# --- Étape 1 : Image de base ---
FROM python:3.11-slim AS base

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Créer un utilisateur non-root (sécurité)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# --- Étape 2 : Installer les dépendances ---
WORKDIR /app

COPY pyproject.toml ./
# Ou si vous utilisez requirements.txt :
# COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -e ".[prod]"
# Ou : pip install -r requirements.txt

# --- Étape 3 : Copier le code ---
COPY src/ ./src/
COPY models/ ./models/

# Changer le propriétaire
RUN chown -R appuser:appuser /app

# Basculer vers l'utilisateur non-root
USER appuser

# --- Étape 4 : Exposer et lancer ---
EXPOSE 8000

# Health check intégré
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Lancer l'API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Multi-stage build (image plus légère)

```dockerfile
# Dockerfile.multistage

# --- Stage 1 : Build ---
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# --- Stage 2 : Production ---
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1

# Copier seulement les packages installés
COPY --from=builder /install /usr/local

WORKDIR /app

COPY src/ ./src/
COPY models/ ./models/

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.3 .dockerignore

```
# .dockerignore

__pycache__/
*.pyc
*.pyo
.git/
.gitignore
.env
*.egg-info/
dist/
build/
notebooks/
data/raw/
*.ipynb
.vscode/
.idea/
*.md
tests/
```

### 2.4 Construire et lancer

```bash
# Construire l'image
docker build -t ml-churn-api:v1.0.0 .

# Vérifier la taille
docker images ml-churn-api

# Lancer le conteneur
docker run -d \
  --name churn-api \
  -p 8000:8000 \
  ml-churn-api:v1.0.0

# Tester
curl http://localhost:8000/health

# Voir les logs
docker logs -f churn-api

# Arrêter
docker stop churn-api && docker rm churn-api
```

> 💡 **Conseil** : "Utilisez `python:3.11-slim` et non `python:3.11` comme image de base. La version slim est 5x plus petite (~150 Mo vs ~900 Mo). Évitez `python:3.11-alpine` pour le ML car numpy/scipy sont difficiles à compiler dessus."

---

## 3. 🐙 Docker Compose

### 3.1 API + Monitoring

Docker Compose permet d'orchestrer **plusieurs conteneurs** en une seule commande.

```yaml
# docker-compose.yml

version: '3.8'

services:
  # --- API de prédiction ---
  api:
    build: .
    container_name: churn-api
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models:ro    # Modèles en lecture seule
      - ./logs:/app/logs           # Logs persistants
    environment:
      - MODEL_PATH=/app/models/model_v1.0.0.joblib
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  # --- Prometheus (collecte de métriques) ---
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    depends_on:
      - api
    restart: unless-stopped

  # --- Grafana (visualisation) ---
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  grafana-data:
```

### 3.2 Configuration Prometheus

```yaml
# monitoring/prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'churn-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

### 3.3 Lancer la stack complète

```bash
# Démarrer tout
docker compose up -d

# Vérifier que tout tourne
docker compose ps

# Accéder aux services
# API :        http://localhost:8000/docs
# Prometheus : http://localhost:9090
# Grafana :    http://localhost:3000 (admin/admin)

# Voir les logs de l'API
docker compose logs -f api

# Tout arrêter
docker compose down
```

---

## 4. 📊 Monitoring — Les 3 niveaux

### 4.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────┐
│              MONITORING ML EN PRODUCTION         │
├─────────────────┬──────────────┬────────────────┤
│  TECHNIQUE      │  DONNÉES     │  MÉTIER        │
│                 │              │                │
│  Latence        │  Data drift  │  Accuracy      │
│  Erreurs        │  Distribution│  F1-Score      │
│  CPU/RAM        │  PSI         │  Impact métier │
│  Throughput     │  KS test     │  A/B testing   │
│                 │              │                │
│  "L'API marche?"│  "Les données│  "Le modèle    │
│                 │   changent?" │   est bon ?"   │
└─────────────────┴──────────────┴────────────────┘
```

### 4.2 Niveau 1 : Monitoring technique

#### Logging structuré

```python
# src/logging_config.py

import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formatte les logs en JSON pour faciliter le parsing."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logger(name: str, log_file: str = "logs/api.log") -> logging.Logger:
    """Configure un logger avec sortie JSON."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger
```

#### Ajout du logging à l'API

```python
# Ajouter dans src/api.py

import time
from src.logging_config import setup_logger

logger = setup_logger("churn-api")

@app.middleware("http")
async def log_requests(request, call_next):
    """Log chaque requête avec sa durée."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s"
    )
    return response
```

#### Health check enrichi

```python
@app.get("/health")
def health_check():
    """Health check détaillé."""
    import psutil

    return {
        "status": "healthy",
        "model_version": artefact.get('version', 'unknown'),
        "model_date": artefact.get('date', 'unknown'),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
        }
    }
```

### 4.3 Niveau 2 : Monitoring des données (Data Drift)

#### Qu'est-ce que le drift ?

Le **data drift** se produit quand la distribution des données en production **diffère** de celle des données d'entraînement.

```
Pendant l'entraînement :           En production (6 mois plus tard) :

  Revenu moyen                     Revenu moyen
  │                                │
  │    ╱╲                          │         ╱╲
  │   ╱  ╲                        │        ╱  ╲
  │  ╱    ╲                       │       ╱    ╲
  │ ╱      ╲                      │      ╱      ╲
  │╱        ╲                     │     ╱        ╲
  └──────────── Revenu            └──────────────── Revenu
    30k  45k  60k                   40k  55k  70k

  → La distribution a GLISSÉ vers la droite !
  → Le modèle entraîné sur l'ancienne distribution sera moins performant.
```

#### PSI (Population Stability Index)

```python
import numpy as np


def calculer_psi(reference: np.ndarray, production: np.ndarray, n_bins: int = 10) -> float:
    """
    Calcule le PSI entre une distribution de référence et une distribution
    de production.

    PSI < 0.1  → Pas de changement significatif
    PSI 0.1-0.2 → Changement modéré, surveiller
    PSI > 0.2  → Changement important, investiguer / retrainer
    """
    # Discrétiser en bins
    breakpoints = np.percentile(reference, np.linspace(0, 100, n_bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    # Compter les proportions dans chaque bin
    ref_counts = np.histogram(reference, bins=breakpoints)[0]
    prod_counts = np.histogram(production, bins=breakpoints)[0]

    # Éviter les zéros
    ref_proportions = (ref_counts + 1) / (ref_counts.sum() + n_bins)
    prod_proportions = (prod_counts + 1) / (prod_counts.sum() + n_bins)

    # PSI
    psi = np.sum(
        (prod_proportions - ref_proportions) *
        np.log(prod_proportions / ref_proportions)
    )
    return psi


# --- Exemple ---
np.random.seed(42)

# Données d'entraînement
revenus_train = np.random.normal(45000, 15000, 5000)

# Production sans drift
revenus_prod_ok = np.random.normal(45000, 15000, 1000)

# Production avec drift
revenus_prod_drift = np.random.normal(55000, 18000, 1000)

print(f"PSI sans drift  : {calculer_psi(revenus_train, revenus_prod_ok):.4f}")
print(f"PSI avec drift  : {calculer_psi(revenus_train, revenus_prod_drift):.4f}")
```

#### Test de Kolmogorov-Smirnov

```python
from scipy import stats

# --- Test KS ---
stat_ok, p_value_ok = stats.ks_2samp(revenus_train, revenus_prod_ok)
stat_drift, p_value_drift = stats.ks_2samp(revenus_train, revenus_prod_drift)

print(f"Sans drift  : KS={stat_ok:.4f}, p-value={p_value_ok:.4f}")
print(f"Avec drift  : KS={stat_drift:.4f}, p-value={p_value_drift:.4f}")

# Si p-value < 0.05 → les distributions sont significativement différentes
if p_value_drift < 0.05:
    print("ALERTE : Data drift détecté !")
```

| Métrique | Seuil d'alerte | Interprétation |
|----------|---------------|----------------|
| **PSI** | > 0.2 | Changement important de distribution |
| **KS test** | p-value < 0.05 | Distributions significativement différentes |

### 4.4 Niveau 3 : Monitoring métier

```python
# Enregistrer les prédictions pour le monitoring

import json
from datetime import datetime

def logger_prediction(client_data, prediction, proba):
    """Enregistre chaque prédiction pour le monitoring."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": client_data,
        "prediction": int(prediction),
        "probabilite": float(proba),
    }
    with open("logs/predictions.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## 5. 🔄 Détection de drift et retraining

### 5.1 Pourquoi un modèle "meurt" avec le temps

```
Performance
  │
  │ ──────╲
  │        ╲
  │         ╲──────╲
  │                 ╲
  │                  ╲───── Seuil d'alerte
  │                        ╲
  └──────────────────────────── Temps
  Déploiement    3 mois    6 mois    1 an

  Causes :
  - Les clients changent (comportement, démographie)
  - Le marché évolue (concurrence, réglementation)
  - Les produits changent (nouvelles offres)
  - Le monde change (COVID, crise économique)
```

### 5.2 Quand retrainer

| Signal | Action |
|--------|--------|
| PSI > 0.2 sur une feature importante | Investiguer + planifier retraining |
| Performance métier en baisse (feedback loop) | Retrainer immédiatement |
| Retraining programmé (ex: tous les mois) | Retrainer + comparer avec le modèle actuel |
| Nouveau dataset disponible | Évaluer si retraining apporte un gain |

### 5.3 Introduction à EvidentlyAI

EvidentlyAI est une librairie open-source pour le monitoring de modèles ML en production.

```python
# Installation
# pip install evidently

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
import pandas as pd
import numpy as np

# --- Données de référence (entraînement) ---
np.random.seed(42)
reference_data = pd.DataFrame({
    'anciennete_mois': np.random.exponential(24, 1000).clip(1, 120),
    'montant_mensuel': np.random.normal(60, 25, 1000).clip(10, 200),
    'nb_reclamations': np.random.poisson(2, 1000),
    'satisfaction': np.random.uniform(1, 5, 1000),
    'prediction': np.random.choice([0, 1], 1000, p=[0.7, 0.3]),
})

# --- Données de production (avec drift) ---
production_data = pd.DataFrame({
    'anciennete_mois': np.random.exponential(18, 500).clip(1, 120),  # Drift !
    'montant_mensuel': np.random.normal(70, 30, 500).clip(10, 200),  # Drift !
    'nb_reclamations': np.random.poisson(3, 500),                     # Drift !
    'satisfaction': np.random.uniform(1, 5, 500),
    'prediction': np.random.choice([0, 1], 500, p=[0.5, 0.5]),
})

# --- Rapport de drift ---
report = Report(metrics=[
    DataDriftPreset(),
])

report.run(
    reference_data=reference_data,
    current_data=production_data
)

# Sauvegarder le rapport HTML
report.save_html("monitoring/drift_report.html")
print("Rapport de drift sauvegardé dans monitoring/drift_report.html")

# Accéder aux résultats programmatiquement
result = report.as_dict()
drift_detected = result['metrics'][0]['result']['dataset_drift']
print(f"Drift détecté : {drift_detected}")
```

---

## 6. 📈 Introduction à MLflow

### 6.1 Pourquoi MLflow

MLflow résout 3 problèmes :

```
SANS MLflow :                       AVEC MLflow :
"C'était quels paramètres          Tracking automatique de
 pour le modèle de mardi ?"         CHAQUE expérience :
                                     - Paramètres
"J'ai 47 notebooks avec             - Métriques
 des résultats partout..."           - Artefacts (modèles)
                                     - Code source
"Quel modèle est en prod ?"         - Model Registry
```

### 6.2 Tracking des expériences

```python
# Installation
# pip install mlflow

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.datasets import load_breast_cancer
import numpy as np

# --- Configuration ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")  # Stockage local
mlflow.set_experiment("churn-prediction")

# --- Données ---
cancer = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    cancer.data, cancer.target, test_size=0.2, random_state=42
)

# --- Expérience 1 : Random Forest ---
with mlflow.start_run(run_name="random_forest_v1"):
    # Paramètres
    n_estimators = 100
    max_depth = 5

    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)

    # Entraîner
    rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    # Métriques
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)

    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("accuracy", acc)

    # Cross-validation
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='f1')
    mlflow.log_metric("cv_f1_mean", cv_scores.mean())
    mlflow.log_metric("cv_f1_std", cv_scores.std())

    # Sauvegarder le modèle
    mlflow.sklearn.log_model(rf, "model")

    print(f"Random Forest - F1: {f1:.4f}, Accuracy: {acc:.4f}")


# --- Expérience 2 : Gradient Boosting ---
with mlflow.start_run(run_name="gradient_boosting_v1"):
    n_estimators = 200
    max_depth = 3
    learning_rate = 0.1

    mlflow.log_param("model_type", "GradientBoosting")
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("learning_rate", learning_rate)

    gb = GradientBoostingClassifier(
        n_estimators=n_estimators, max_depth=max_depth,
        learning_rate=learning_rate, random_state=42
    )
    gb.fit(X_train, y_train)
    y_pred = gb.predict(X_test)

    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)

    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("accuracy", acc)

    mlflow.sklearn.log_model(gb, "model")

    print(f"Gradient Boosting - F1: {f1:.4f}, Accuracy: {acc:.4f}")
```

### 6.3 Interface web MLflow

```bash
# Lancer l'interface web
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# Ouvrir http://localhost:5000
```

```
┌─────────────────────────────────────────────────────┐
│  MLflow - Experiment: churn-prediction              │
├──────────────────┬──────────┬──────────┬────────────┤
│  Run             │ F1 Score │ Accuracy │ Model Type │
├──────────────────┼──────────┼──────────┼────────────┤
│  gradient_boost  │  0.9650  │  0.9561  │ GB         │
│  random_forest   │  0.9580  │  0.9474  │ RF         │
└──────────────────┴──────────┴──────────┴────────────┘
```

### 6.4 Model Registry

```python
# Enregistrer le meilleur modèle dans le Registry
import mlflow

# Après avoir identifié le meilleur run
best_run_id = "abc123..."  # ID du meilleur run

# Enregistrer dans le Registry
model_uri = f"runs:/{best_run_id}/model"
mlflow.register_model(model_uri, "churn-model")

# Passer le modèle en production
from mlflow.tracking import MlflowClient

client = MlflowClient()
client.transition_model_version_stage(
    name="churn-model",
    version=1,
    stage="Production"
)

# Charger le modèle de production
model_prod = mlflow.sklearn.load_model("models:/churn-model/Production")
```

> 💡 **Conseil** : "MLflow est gratuit et open-source. Utilisez-le dès que vous avez plus de 3 expériences à comparer. Cela vous évitera de perdre des heures à retrouver les paramètres d'un bon modèle."

---

## 7. 🔄 CI/CD pour le ML (aperçu)

### 7.1 GitHub Actions pour tests + build Docker

```yaml
# .github/workflows/ml-pipeline.yml

name: ML Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ -v --tb=short

      - name: Run linting
        run: |
          ruff check src/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t ml-churn-api:${{ github.sha }} .

      - name: Test Docker image
        run: |
          docker run -d --name test-api -p 8000:8000 ml-churn-api:${{ github.sha }}
          sleep 5
          curl -f http://localhost:8000/health || exit 1
          docker stop test-api
```

### 7.2 Automatiser le retraining

```yaml
# .github/workflows/retrain.yml

name: Retraining Scheduled

on:
  schedule:
    - cron: '0 2 1 * *'  # Le 1er de chaque mois à 2h du matin
  workflow_dispatch:       # Déclenchement manuel possible

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Retrain model
        run: python scripts/train.py

      - name: Evaluate new model
        run: python scripts/evaluate.py

      - name: Compare with current model
        run: python scripts/compare_models.py
```

```
Pipeline CI/CD pour le ML :

┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│ Push │ →  │ Test │ →  │Build │ →  │Deploy│ →  │Monitor│
│      │    │pytest│    │Docker│    │ API  │    │ Drift │
└──────┘    └──────┘    └──────┘    └──────┘    └──┬───┘
                                                   │
                                         ┌─────────▼──────────┐
                                         │ Drift détecté ?    │
                                         │ OUI → Retrain      │
                                         │ NON → Continue      │
                                         └────────────────────┘
```

---

## 8. 🏆 Livrable final : API Dockerisée + Monitoring basique

### 8.1 Résumé du livrable

Votre livrable final combine tout ce que vous avez appris :

```
projet-ml-churn/
├── .github/
│   └── workflows/
│       └── ml-pipeline.yml        # CI/CD
├── data/
│   └── raw/
├── monitoring/
│   ├── prometheus.yml             # Config Prometheus
│   └── drift_check.py            # Script de détection de drift
├── notebooks/
│   └── exploration.ipynb
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── model.py
│   ├── predict.py
│   ├── api.py
│   └── logging_config.py
├── scripts/
│   └── train.py
├── tests/
│   ├── test_preprocessing.py
│   ├── test_model.py
│   └── test_api.py
├── models/
│   └── model_v1.0.0.joblib
├── logs/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .dockerignore
└── README.md
```

### 8.2 Commandes pour tout lancer

```bash
# 1. Entraîner le modèle
python scripts/train.py

# 2. Exécuter les tests
pytest tests/ -v

# 3. Construire l'image Docker
docker build -t ml-churn-api:v1.0.0 .

# 4. Lancer la stack complète
docker compose up -d

# 5. Vérifier
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"anciennete_mois": 6, "montant_mensuel": 89.99, "nb_reclamations": 5, "nb_produits": 1, "satisfaction": 1.5}'

# 6. Accéder au monitoring
# Grafana : http://localhost:3000
# Prometheus : http://localhost:9090
```

---

## 🎯 Points clés à retenir

1. **Docker** garantit la reproductibilité : "ça marche partout, pas seulement sur ma machine"
2. Utilisez `python:3.11-slim` comme image de base (pas `alpine` pour le ML)
3. Le **multi-stage build** réduit la taille de l'image de production
4. **Docker Compose** orchestre l'API + le monitoring en une commande
5. Le monitoring a **3 niveaux** : technique (latence), données (drift), métier (performance)
6. Le **data drift** est la cause principale de dégradation des modèles en production
7. Le **PSI > 0.2** est un signal d'alerte pour investiguer un potentiel drift
8. **MLflow** permet de tracker toutes les expériences et de gérer les versions de modèles
9. La **CI/CD** automatise les tests, le build Docker et le retraining
10. Un modèle en production doit être **monitoré en continu** et retrainé régulièrement

---

## ✅ Checklist de validation

- [ ] Je sais écrire un Dockerfile optimisé pour une API ML
- [ ] Je comprends le multi-stage build et son intérêt
- [ ] Je sais écrire un docker-compose.yml pour API + monitoring
- [ ] Je sais construire, lancer et tester un conteneur Docker
- [ ] Je comprends les 3 niveaux de monitoring (technique, données, métier)
- [ ] Je sais implémenter du logging structuré dans une API
- [ ] Je comprends le data drift et sais calculer le PSI
- [ ] Je sais utiliser le test de Kolmogorov-Smirnov pour détecter un drift
- [ ] Je connais EvidentlyAI pour le monitoring de drift
- [ ] Je sais utiliser MLflow pour tracker mes expériences
- [ ] Je comprends le principe de CI/CD appliqué au ML
- [ ] J'ai réalisé le livrable final : API Dockerisée + monitoring basique

---

**Précédent** : [Chapitre 15 : Du Notebook à l'API — Mettre en Production](15-notebook-api.md)

**Suivant** : [Chapitre 17 : MLflow — Tracker, Reproduire et Déployer](17-mlflow.md)
