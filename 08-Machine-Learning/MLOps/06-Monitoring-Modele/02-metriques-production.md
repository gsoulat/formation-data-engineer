# Métriques de production — Prometheus et Grafana

## Monitoring ML vs Monitoring DevOps classique

En DevOps classique, on monitore : uptime, latence, taux d'erreur, utilisation CPU/RAM.

En ML, on monitore en plus :
- **Distribution des inputs** : les features reçues correspondent-elles à ce qu'on attendait ?
- **Distribution des prédictions** : le modèle prédit-il dans les plages habituelles ?
- **Performance réelle** : quand les labels ground truth sont disponibles, l'accuracy a-t-elle changé ?
- **Data quality** : valeurs manquantes, outliers, types incorrects en production

```
Monitoring ML en production
────────────────────────────
Infrastructure  : CPU, RAM, latence API, taux d'erreur HTTP
Données         : distribution features, valeurs manquantes, outliers
Prédictions     : distribution des outputs, confiance, dérive
Performance     : RMSE, MAE, R² (si labels disponibles)
Dérive          : PSI, KS test (voir 01-drift-detection.md)
```

---

## Architecture Prometheus + Grafana pour ML

```
API ML (FastAPI)
     │
     │  GET /metrics (format Prometheus)
     ▼
Prometheus
     │  stockage time-series
     ▼
Grafana ──▶ Dashboards ML
```

---

## Exposer des métriques ML avec prometheus-client

```python
# api/metrics.py
from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    REGISTRY, generate_latest, CONTENT_TYPE_LATEST
)
import time

# ── Compteurs ─────────────────────────────────────────────────────
PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total",
    "Nombre total de prédictions effectuées",
    ["status", "model_version"]  # labels
)

PREDICTION_ERRORS = Counter(
    "ml_prediction_errors_total",
    "Nombre d'erreurs lors des prédictions",
    ["error_type"]
)

# ── Histogrammes ──────────────────────────────────────────────────
PREDICTION_LATENCY = Histogram(
    "ml_prediction_latency_seconds",
    "Temps de traitement d'une prédiction",
    ["model_version"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

PREDICTION_VALUE = Histogram(
    "ml_prediction_value",
    "Distribution des valeurs prédites",
    buckets=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0]
)

# ── Gauges (valeurs instantanées) ─────────────────────────────────
MODEL_VERSION = Gauge(
    "ml_model_version_info",
    "Informations sur le modèle en service",
    ["model_name", "version", "stage"]
)

INPUT_FEATURE_MEAN = Gauge(
    "ml_input_feature_mean",
    "Moyenne des features d'entrée (fenêtre glissante)",
    ["feature_name"]
)

PREDICTION_ROLLING_MEAN = Gauge(
    "ml_prediction_rolling_mean",
    "Moyenne glissante des prédictions (1000 dernières)"
)

DATA_QUALITY_SCORE = Gauge(
    "ml_data_quality_score",
    "Score de qualité des données entrantes (0-1)"
)

# ── Summary ───────────────────────────────────────────────────────
BATCH_SIZE = Summary(
    "ml_batch_size",
    "Taille des batches de prédiction"
)
```

---

## Intégration dans FastAPI

```python
# api/main.py (version complète avec métriques)
import time
import logging
import numpy as np
from collections import deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .schemas import HouseFeatures, PredictionResponse
from .model import load_model, predict, get_model_version
from .metrics import (
    PREDICTIONS_TOTAL, PREDICTION_ERRORS, PREDICTION_LATENCY,
    PREDICTION_VALUE, MODEL_VERSION, INPUT_FEATURE_MEAN,
    PREDICTION_ROLLING_MEAN, DATA_QUALITY_SCORE
)

logger = logging.getLogger(__name__)

# Buffer pour calculs de statistiques glissantes
_recent_predictions = deque(maxlen=1000)
_recent_inputs = {}  # feature_name → deque

FEATURE_NAMES = [
    "MedInc", "HouseAge", "AveRooms", "AveBedrms",
    "Population", "AveOccup", "Latitude", "Longitude"
]
for feat in FEATURE_NAMES:
    _recent_inputs[feat] = deque(maxlen=1000)

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    version = get_model_version()
    MODEL_VERSION.labels(
        model_name="prix-immobilier-rf",
        version=str(version),
        stage="Production"
    ).set(1)
    logger.info(f"Modèle v{version} chargé")
    yield

app = FastAPI(title="Prix Immobilier API", lifespan=lifespan)

@app.get("/metrics")
def metrics():
    """Endpoint Prometheus — scraped toutes les 15 secondes."""
    # Mettre à jour les gauges glissantes
    if _recent_predictions:
        PREDICTION_ROLLING_MEAN.set(np.mean(list(_recent_predictions)))

    for feat in FEATURE_NAMES:
        if _recent_inputs[feat]:
            INPUT_FEATURE_MEAN.labels(feature_name=feat).set(
                np.mean(list(_recent_inputs[feat]))
            )

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=PredictionResponse)
def predict_price(features: HouseFeatures):
    start = time.time()
    model_version = str(get_model_version())

    # Validation rapide des données
    quality_score = _compute_quality_score(features)
    DATA_QUALITY_SCORE.set(quality_score)

    if quality_score < 0.5:
        logger.warning(f"Qualité des données faible : {quality_score:.2f}")

    try:
        prix = predict(features.model_dump())
        latency = time.time() - start

        # Métriques
        PREDICTIONS_TOTAL.labels(status="success", model_version=model_version).inc()
        PREDICTION_LATENCY.labels(model_version=model_version).observe(latency)
        PREDICTION_VALUE.observe(prix)

        # Mettre à jour les buffers glissants
        _recent_predictions.append(prix)
        for feat in FEATURE_NAMES:
            _recent_inputs[feat].append(getattr(features, feat))

        return PredictionResponse(prix_predit=prix, model_version=model_version)

    except Exception as e:
        PREDICTIONS_TOTAL.labels(status="error", model_version=model_version).inc()
        PREDICTION_ERRORS.labels(error_type=type(e).__name__).inc()
        raise HTTPException(status_code=500, detail=str(e))

def _compute_quality_score(features: HouseFeatures) -> float:
    """Score de qualité simple : 1.0 si tout est dans les plages attendues."""
    score = 1.0
    checks = [
        0 < features.MedInc < 20,
        0 < features.HouseAge < 100,
        0 < features.AveRooms < 50,
        0 < features.AveBedrms < 50,
        0 < features.Population < 100_000,
        0 < features.AveOccup < 20,
        32 < features.Latitude < 42,      # Californie
        -125 < features.Longitude < -114,  # Californie
    ]
    return sum(checks) / len(checks)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Prometheus (`http://localhost:9090`) avec une requête PromQL sur `ml_predictions_total` et le graphique correspondant. Montrer ensuite l'onglet "Targets" pour voir que l'API ML est bien scrapée.
> **Expliquer :** "Prometheus scrape le endpoint `/metrics` de notre API toutes les 15 secondes. Chaque prédiction incrémente un compteur. On peut voir en temps réel le taux de prédictions par seconde, la latence p99, la distribution des valeurs prédites."

---

## Requêtes PromQL utiles

```promql
# ── Taux de prédictions par seconde ───────────────────────────
rate(ml_predictions_total[5m])

# ── Taux d'erreur ──────────────────────────────────────────────
rate(ml_predictions_total{status="error"}[5m])
  /
rate(ml_predictions_total[5m])

# ── Latence P50, P95, P99 ──────────────────────────────────────
histogram_quantile(0.50, rate(ml_prediction_latency_seconds_bucket[5m]))
histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m]))
histogram_quantile(0.99, rate(ml_prediction_latency_seconds_bucket[5m]))

# ── Moyenne glissante des prédictions ─────────────────────────
ml_prediction_rolling_mean

# ── Score de qualité des données ──────────────────────────────
ml_data_quality_score

# ── Évolution de la moyenne d'une feature ─────────────────────
ml_input_feature_mean{feature_name="MedInc"}

# ── Nombre de prédictions par version de modèle ───────────────
sum(ml_predictions_total) by (model_version)
```

---

## Configuration Grafana — Dashboard ML

```json
// monitoring/grafana/dashboards/ml-dashboard.json
{
  "title": "ML Model Monitoring — Prix Immobilier",
  "uid": "ml-monitoring",
  "panels": [
    {
      "title": "Taux de prédictions/s",
      "type": "stat",
      "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
      "targets": [{
        "expr": "sum(rate(ml_predictions_total[5m]))",
        "legendFormat": "pred/s"
      }]
    },
    {
      "title": "Latence P95",
      "type": "stat",
      "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m]))",
        "legendFormat": "P95 latency"
      }],
      "options": {
        "unit": "s",
        "thresholds": {
          "steps": [
            {"color": "green", "value": 0},
            {"color": "yellow", "value": 0.1},
            {"color": "red", "value": 0.5}
          ]
        }
      }
    },
    {
      "title": "Taux d'erreur",
      "type": "stat",
      "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
      "targets": [{
        "expr": "rate(ml_predictions_total{status='error'}[5m]) / rate(ml_predictions_total[5m])",
        "legendFormat": "error rate"
      }],
      "options": {
        "unit": "percentunit",
        "thresholds": {
          "steps": [
            {"color": "green", "value": 0},
            {"color": "red", "value": 0.01}
          ]
        }
      }
    },
    {
      "title": "Distribution des prédictions",
      "type": "histogram",
      "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
      "targets": [{
        "expr": "rate(ml_prediction_value_bucket[5m])",
        "legendFormat": "{{le}}"
      }]
    },
    {
      "title": "Moyenne glissante des prédictions",
      "type": "graph",
      "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
      "targets": [{
        "expr": "ml_prediction_rolling_mean",
        "legendFormat": "Prix prédit moyen"
      }]
    },
    {
      "title": "Qualité des données entrantes",
      "type": "graph",
      "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8},
      "targets": [{
        "expr": "ml_data_quality_score",
        "legendFormat": "Score qualité"
      }],
      "options": {
        "alert": {
          "conditions": [{
            "query": {"params": ["A", "5m", "now"]},
            "reducer": "last",
            "evaluator": {"type": "lt", "params": [0.8]}
          }],
          "name": "Qualité données faible"
        }
      }
    },
    {
      "title": "Moyenne des features d'entrée",
      "type": "graph",
      "gridPos": {"x": 12, "y": 12, "w": 12, "h": 8},
      "targets": [
        {"expr": "ml_input_feature_mean{feature_name='MedInc'}", "legendFormat": "MedInc"},
        {"expr": "ml_input_feature_mean{feature_name='HouseAge'}", "legendFormat": "HouseAge"},
        {"expr": "ml_input_feature_mean{feature_name='AveRooms'}", "legendFormat": "AveRooms"}
      ]
    }
  ]
}
```

---

## Provisionner Grafana automatiquement

```yaml
# monitoring/grafana/provisioning/datasources/prometheus.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

```yaml
# monitoring/grafana/provisioning/dashboards/dashboard.yaml
apiVersion: 1
providers:
  - name: MLOps Dashboards
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le dashboard Grafana avec les panneaux : taux de prédictions (stat en vert), latence P95 (stat en jaune/vert), taux d'erreur (stat), graphique de la moyenne glissante des prédictions montrant une variation, graphique de la qualité des données. Simuler un pic de trafic et montrer la mise à jour en temps réel.
> **Expliquer :** "Ce dashboard se rafraîchit toutes les 10 secondes. Regardez comment la moyenne des prédictions évolue dans le temps — c'est un indicateur précoce de dérive. Si la valeur prédite moyenne baisse de 15% en une semaine, c'est un signal que quelque chose a changé dans les données d'entrée."

---

## Alertes Grafana

```yaml
# Alerte Grafana (format Grafana 9+)
# Configurable dans l'UI : Alerting → Alert rules

# Règle 1 : Taux d'erreur élevé
name: "Taux erreur ML élevé"
condition: rate(ml_predictions_total{status="error"}[5m]) / rate(ml_predictions_total[5m]) > 0.05
for: 2m  # Doit durer 2 minutes avant l'alerte
labels:
  severity: critical
  team: data-science
annotations:
  summary: "Taux d'erreur de l'API ML dépasse 5%"
  runbook: "https://wiki/ml-api-runbook"

# Règle 2 : Latence élevée
name: "Latence ML élevée"
condition: histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m])) > 0.5
for: 5m
labels:
  severity: warning

# Règle 3 : Qualité données faible
name: "Qualité données dégradée"
condition: ml_data_quality_score < 0.7
for: 10m
labels:
  severity: warning

# Règle 4 : Drift de prédiction
name: "Dérive prédictions détectée"
condition: abs(ml_prediction_rolling_mean - 4.5) / 4.5 > 0.2
for: 30m
labels:
  severity: warning
```

---

## Script de simulation de trafic pour tester le monitoring

```python
# scripts/simulate_traffic.py
"""Simule du trafic vers l'API ML pour tester le monitoring."""
import requests
import random
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://localhost:8000"

def generate_house(drift_factor: float = 1.0):
    """Générer des features aléatoires, avec dérive optionnelle."""
    return {
        "MedInc": random.gauss(4.5, 1.2) * drift_factor,
        "HouseAge": random.gauss(28, 12),
        "AveRooms": random.gauss(5.4, 1.5),
        "AveBedrms": random.gauss(1.1, 0.2),
        "Population": random.gauss(1500, 800),
        "AveOccup": random.gauss(2.8, 0.8),
        "Latitude": random.uniform(32.5, 41.5),
        "Longitude": random.uniform(-124.5, -114.5)
    }

def make_prediction(features):
    """Envoyer une requête de prédiction."""
    try:
        r = requests.post(f"{API_URL}/predict", json=features, timeout=5)
        return r.status_code, r.json().get("prix_predit") if r.status_code == 200 else None
    except Exception as e:
        return None, None

def simulate_normal_traffic(n_requests: int = 100, rps: float = 10):
    """Trafic normal."""
    print(f"Simulation trafic normal : {n_requests} requêtes à {rps} req/s")
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(n_requests):
            executor.submit(make_prediction, generate_house())
            time.sleep(1 / rps)
    print("Trafic normal terminé")

def simulate_drift(n_requests: int = 200, drift_factor: float = 0.7):
    """Trafic avec dérive (revenus plus faibles)."""
    print(f"Simulation dérive : factor={drift_factor}")
    for i in range(n_requests):
        status, pred = make_prediction(generate_house(drift_factor))
        if i % 50 == 0:
            print(f"  {i}/{n_requests} - pred: {pred}")
        time.sleep(0.1)
    print("Simulation dérive terminée")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["normal", "drift", "both"], default="normal")
    args = parser.parse_args()

    if args.mode in ["normal", "both"]:
        simulate_normal_traffic(200, rps=5)

    if args.mode in ["drift", "both"]:
        print("\nDémarre simulation de dérive dans 30 secondes...")
        time.sleep(30)
        simulate_drift(500, drift_factor=0.65)
```

---

## Récapitulatif : les métriques ML à monitorer

| Catégorie | Métrique | Outil | Alerte si... |
|---|---|---|---|
| **Infrastructure** | Latence P95 | Prometheus/Grafana | > 500ms |
| **Infrastructure** | Taux erreur HTTP | Prometheus/Grafana | > 1% |
| **Prédictions** | Distribution outputs | Prometheus | Changement > 20% |
| **Prédictions** | Valeurs aberrantes | Prometheus | > seuil business |
| **Données** | Qualité input | Prometheus | Score < 0.8 |
| **Données** | Feature drift (PSI) | Evidently | PSI > 0.2 |
| **Performance** | RMSE (si labels dispo) | MLflow/Custom | Régression > 5% |
