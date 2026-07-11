# Exercice 2 — Monitoring d'un modèle en production

## Objectif

Ajouter un système de monitoring complet à un modèle en production : détection de dérive des données avec Evidently, métriques Prometheus, dashboard Grafana, et alertes automatiques.

**Durée estimée :** 2h

**Niveau :** Intermédiaire / Avancé

**Prérequis :** Exercice 1 terminé (ou modèle de classification e-commerce disponible)

---

## Contexte

Le modèle de prédiction de conversion e-commerce est en production depuis 3 mois. L'équipe marketing se plaint que les recommandations semblent moins pertinentes. Vous devez :

1. Mettre en place un monitoring de dérive des données
2. Exposer des métriques métier via Prometheus
3. Créer un dashboard Grafana dédié ML
4. Configurer des alertes pour détecter les anomalies automatiquement

---

## Architecture de la solution

```
Données production (simulées)
          │
          ▼
┌──────────────────────────────────────────────────────┐
│              Stack Monitoring                         │
│                                                      │
│  API ML (FastAPI)                                    │
│     │── /predict  ──▶ prédictions + métriques        │
│     └── /metrics  ──▶ Prometheus scrape              │
│                                                      │
│  Drift Checker (job quotidien)                       │
│     ├── Charger données prod vs référence            │
│     ├── Calcul PSI / KS test                        │
│     ├── Rapport Evidently HTML                       │
│     └── Alerte si drift > seuil                     │
│                                                      │
│  Prometheus ──▶ Grafana ──▶ Alertes Slack/Email     │
└──────────────────────────────────────────────────────┘
```

---

## Partie 1 — Enrichir l'API avec des métriques ML (30 min)

### Étape 1.1 : Métriques métier spécifiques

```python
# api/ml_metrics.py
"""Métriques Prometheus spécifiques au modèle e-commerce."""
from prometheus_client import Counter, Histogram, Gauge, Summary
import numpy as np
from collections import deque

# ── Métriques de prédiction ────────────────────────────────────
PREDICTIONS_TOTAL = Counter(
    "ecom_predictions_total",
    "Total des prédictions",
    ["predicted_class", "confidence_level"]
)

PREDICTION_LATENCY = Histogram(
    "ecom_prediction_latency_seconds",
    "Latence de prédiction",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

CONVERSION_PROBABILITY = Histogram(
    "ecom_conversion_probability",
    "Distribution des probabilités de conversion prédites",
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# ── Métriques de drift des features ───────────────────────────
FEATURE_MEAN = Gauge(
    "ecom_feature_mean",
    "Moyenne glissante d'une feature",
    ["feature_name"]
)

FEATURE_STD = Gauge(
    "ecom_feature_std",
    "Écart-type glissant d'une feature",
    ["feature_name"]
)

# ── Métriques business ─────────────────────────────────────────
PREDICTED_CONVERSION_RATE = Gauge(
    "ecom_predicted_conversion_rate",
    "Taux de conversion prédit (fenêtre glissante 1000)"
)

HIGH_VALUE_VISITORS = Counter(
    "ecom_high_value_visitors_total",
    "Visiteurs à haute probabilité de conversion (>0.7)"
)

# ── Buffers pour statistiques glissantes ─────────────────────
WINDOW = 1000
_predictions_buffer = deque(maxlen=WINDOW)
_feature_buffers = {}

FEATURE_NAMES = [
    "administrative", "administrative_duration", "informational",
    "informational_duration", "product_related", "product_related_duration",
    "bounce_rates", "exit_rates", "page_values", "special_day",
    "month", "visitor_type", "weekend"
]

for feat in FEATURE_NAMES:
    _feature_buffers[feat] = deque(maxlen=WINDOW)

def record_prediction(features: dict, probability: float, predicted_class: int):
    """Enregistre une prédiction et met à jour les métriques."""
    confidence = "high" if probability > 0.7 or probability < 0.3 else "medium"

    PREDICTIONS_TOTAL.labels(
        predicted_class=str(predicted_class),
        confidence_level=confidence
    ).inc()

    CONVERSION_PROBABILITY.observe(probability)

    if probability > 0.7:
        HIGH_VALUE_VISITORS.inc()

    # Mettre à jour les buffers
    _predictions_buffer.append(predicted_class)
    for feat, val in features.items():
        if feat in _feature_buffers:
            _feature_buffers[feat].append(float(val))

def update_sliding_metrics():
    """Mettre à jour les gauges glissantes (appelé par /metrics)."""
    if _predictions_buffer:
        PREDICTED_CONVERSION_RATE.set(
            sum(_predictions_buffer) / len(_predictions_buffer)
        )

    for feat, buf in _feature_buffers.items():
        if buf:
            vals = list(buf)
            FEATURE_MEAN.labels(feature_name=feat).set(np.mean(vals))
            FEATURE_STD.labels(feature_name=feat).set(np.std(vals))
```

### Étape 1.2 : Intégrer dans l'API

```python
# api/main.py — version avec monitoring complet
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import pickle, os, time, logging
import pandas as pd

from .ml_metrics import (
    record_prediction, update_sliding_metrics, PREDICTION_LATENCY
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-commerce Conversion API with Monitoring")

MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
with open(MODEL_PATH, "rb") as f:
    MODEL = pickle.load(f)

class VisitorFeatures(BaseModel):
    administrative: float = Field(ge=0, default=0)
    administrative_duration: float = Field(ge=0, default=0)
    informational: float = Field(ge=0, default=0)
    informational_duration: float = Field(ge=0, default=0)
    product_related: float = Field(ge=0, default=0)
    product_related_duration: float = Field(ge=0, default=0)
    bounce_rates: float = Field(ge=0, le=1, default=0.05)
    exit_rates: float = Field(ge=0, le=1, default=0.05)
    page_values: float = Field(ge=0, default=0)
    special_day: float = Field(ge=0, le=1, default=0)
    month: int = Field(ge=1, le=12, default=6)
    visitor_type: int = Field(ge=0, le=2, default=1)
    weekend: int = Field(ge=0, le=1, default=0)

@app.get("/health")
def health():
    return {"status": "healthy", "model": "ecommerce-conversion-v1"}

@app.get("/metrics")
def metrics():
    update_sliding_metrics()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
def predict(features: VisitorFeatures):
    start = time.time()

    try:
        feat_dict = features.model_dump()
        df = pd.DataFrame([feat_dict])
        proba = MODEL.predict_proba(df)[0][1]
        pred = int(proba >= 0.5)

        PREDICTION_LATENCY.observe(time.time() - start)
        record_prediction(feat_dict, float(proba), pred)

        return {
            "will_purchase": bool(pred),
            "probability": round(float(proba), 4),
            "confidence": "high" if proba > 0.7 or proba < 0.3 else "medium"
        }
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Étape 1.3 : Tester les métriques

```bash
# Lancer l'API
uvicorn api.main:app --port 8000

# Dans un autre terminal : simuler du trafic
python -c "
import requests, random, time

for i in range(50):
    payload = {
        'administrative': random.randint(0, 10),
        'administrative_duration': random.uniform(0, 300),
        'informational': random.randint(0, 5),
        'informational_duration': random.uniform(0, 150),
        'product_related': random.randint(5, 50),
        'product_related_duration': random.uniform(100, 5000),
        'bounce_rates': random.uniform(0, 0.2),
        'exit_rates': random.uniform(0, 0.3),
        'page_values': random.uniform(0, 100),
        'special_day': random.choice([0, 0, 0, 0.4, 0.8]),
        'month': random.randint(1, 12),
        'visitor_type': random.choice([0, 1, 2]),
        'weekend': random.choice([0, 1])
    }
    r = requests.post('http://localhost:8000/predict', json=payload)
    print(f'{i}: {r.json().get(\"probability\", \"err\"):.2f}')
    time.sleep(0.1)
"

# Vérifier les métriques Prometheus
curl http://localhost:8000/metrics | grep ecom_
```

---

## Partie 2 — Détection de dérive avec Evidently (40 min)

### Étape 2.1 : Script de génération de données de production simulées

```python
# scripts/simulate_production_data.py
"""
Simule 3 mois de données de production avec une dérive progressive.
Les données de novembre ont une dérive significative.
"""
import pandas as pd
import numpy as np
import os

np.random.seed(123)
os.makedirs("data/production", exist_ok=True)

def generate_month_data(month: int, n: int = 500, drift_factor: float = 1.0) -> pd.DataFrame:
    """Génère des données pour un mois donné avec dérive optionnelle."""
    df = pd.DataFrame({
        "administrative": np.random.poisson(2 * drift_factor, n),
        "administrative_duration": np.random.exponential(50, n),
        "informational": np.random.poisson(1, n),
        "informational_duration": np.random.exponential(30, n),
        # Les pages produit diminuent (les gens lisent moins avant d'acheter)
        "product_related": np.random.poisson(20 / drift_factor, n),
        "product_related_duration": np.random.exponential(1000 / drift_factor, n),
        "bounce_rates": np.random.beta(2 * drift_factor, 8, n),  # Plus de rebonds
        "exit_rates": np.random.beta(3 * drift_factor, 7, n),
        "page_values": np.random.exponential(20 / drift_factor, n),  # Valeur page diminue
        "special_day": np.random.choice([0, 0, 0, 0.2, 0.4, 0.6, 0.8, 1.0], n),
        "month": month,
        "visitor_type": np.random.choice([0, 1, 2], n, p=[0.15, 0.75, 0.10]),
        "weekend": np.random.choice([0, 1], n, p=[0.7, 0.3]),
    })
    df["production_date"] = pd.Timestamp(f"2024-{month:02d}-01")
    return df

# Septembre 2024 : pas de dérive
sept = generate_month_data(9, drift_factor=1.0)
sept.to_csv("data/production/sept_2024.csv", index=False)

# Octobre 2024 : dérive légère
oct_data = generate_month_data(10, drift_factor=1.3)
oct_data.to_csv("data/production/oct_2024.csv", index=False)

# Novembre 2024 : dérive forte (Black Friday changed behavior)
nov_data = generate_month_data(11, drift_factor=1.8)
nov_data.to_csv("data/production/nov_2024.csv", index=False)

print("Données de production simulées :")
print(f"  Septembre : {len(sept)} visites")
print(f"  Octobre   : {len(oct_data)} visites")
print(f"  Novembre  : {len(nov_data)} visites")
print(f"\nMoyenne page_values (référence) : {pd.read_csv('data/processed/train.csv')['page_values'].mean():.2f}")
print(f"Moyenne page_values (novembre)  : {nov_data['page_values'].mean():.2f}")
```

### Étape 2.2 : Script de monitoring drift complet

```python
# monitoring/run_drift_check.py
"""
Script de monitoring de dérive à exécuter quotidiennement.
Compare les données de production récentes avec les données de référence.
"""
import pandas as pd
import numpy as np
import json
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    DatasetDriftMetric,
    ColumnDriftMetric
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
FEATURE_COLS = [
    "administrative", "administrative_duration", "informational",
    "informational_duration", "product_related", "product_related_duration",
    "bounce_rates", "exit_rates", "page_values", "special_day",
    "month", "visitor_type", "weekend"
]

DRIFT_THRESHOLDS = {
    "dataset_drift_share": 0.3,   # 30% de features driftées = alerte
    "critical_features": {        # Seuils PSI par feature critique
        "page_values": 0.2,
        "bounce_rates": 0.2,
        "product_related": 0.25
    }
}

def load_reference() -> pd.DataFrame:
    return pd.read_csv("data/processed/train.csv")[FEATURE_COLS]

def load_production(period: str) -> pd.DataFrame:
    """
    Charger les données de production pour une période.
    period: 'sept_2024', 'oct_2024', 'nov_2024'
    """
    path = f"data/production/{period}.csv"
    df = pd.read_csv(path)
    return df[FEATURE_COLS]

def run_drift_analysis(reference: pd.DataFrame, current: pd.DataFrame, period: str) -> dict:
    """Exécuter l'analyse de drift et générer le rapport."""
    logger.info(f"Analyse de drift pour la période : {period}")
    logger.info(f"  Référence : {len(reference)} lignes")
    logger.info(f"  Courant   : {len(current)} lignes")

    # ── Rapport Evidently complet ──────────────────────────────
    report = Report(metrics=[
        DatasetDriftMetric(
            stattest="psi",
            stattest_threshold=0.2
        ),
        DataDriftPreset(
            stattest="psi",
            stattest_threshold=0.2
        ),
        DataQualityPreset(),
    ])

    report.run(reference_data=reference, current_data=current)

    # Sauvegarder HTML
    out_dir = Path("reports/drift")
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / f"drift_{period}.html"
    report.save_html(str(html_path))
    logger.info(f"Rapport HTML sauvegardé : {html_path}")

    # Extraire les résultats JSON
    result = report.as_dict()
    summary = {"period": period, "timestamp": datetime.now().isoformat()}

    for metric in result["metrics"]:
        res = metric.get("result", {})
        if "dataset_drift" in res:
            summary["dataset_drift"] = res["dataset_drift"]
            summary["drifted_features_count"] = res.get("number_of_drifted_columns", 0)
            summary["total_features"] = res.get("number_of_columns", 0)
            summary["drift_share"] = res.get("share_of_drifted_columns", 0)

    # Analyse par feature critique
    summary["feature_drift"] = {}
    for metric in result["metrics"]:
        res = metric.get("result", {})
        col = res.get("column_name")
        if col and col in DRIFT_THRESHOLDS["critical_features"]:
            summary["feature_drift"][col] = {
                "drift_detected": res.get("drift_detected", False),
                "drift_score": round(res.get("drift_score", 0), 4),
                "threshold": DRIFT_THRESHOLDS["critical_features"][col]
            }

    # Évaluer les alertes
    alerts = []
    if summary.get("drift_share", 0) > DRIFT_THRESHOLDS["dataset_drift_share"]:
        alerts.append({
            "level": "critical",
            "message": f"Dérive détectée sur {summary['drifted_features_count']}"
                       f"/{summary['total_features']} features"
                       f" ({summary['drift_share']:.0%})"
        })

    for feat, info in summary.get("feature_drift", {}).items():
        if info["drift_detected"] and info["drift_score"] > info["threshold"]:
            alerts.append({
                "level": "warning",
                "feature": feat,
                "message": f"Feature '{feat}': PSI={info['drift_score']:.3f}"
                           f" > seuil {info['threshold']}"
            })

    summary["alerts"] = alerts
    summary["alert_triggered"] = len(alerts) > 0

    # Sauvegarder JSON
    json_path = out_dir / f"drift_{period}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary

def print_summary(summary: dict):
    """Afficher un résumé lisible."""
    print(f"\n{'='*60}")
    print(f"RAPPORT DE DRIFT — {summary['period']}")
    print(f"{'='*60}")
    print(f"Features driftées : {summary.get('drifted_features_count', '?')}"
          f" / {summary.get('total_features', '?')}"
          f" ({summary.get('drift_share', 0):.0%})")
    print(f"Drift détecté     : {'OUI' if summary.get('dataset_drift') else 'NON'}")

    if summary.get("feature_drift"):
        print("\nFeatures critiques :")
        for feat, info in summary["feature_drift"].items():
            status = "DRIFT" if info["drift_detected"] else "OK"
            print(f"  {feat:30} PSI={info['drift_score']:.3f}  [{status}]")

    if summary.get("alerts"):
        print(f"\n{'!'*40}")
        print("ALERTES :")
        for alert in summary["alerts"]:
            print(f"  [{alert['level'].upper()}] {alert['message']}")
        print(f"{'!'*40}")
    else:
        print("\nAucune alerte — modèle stable")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="nov_2024",
                        choices=["sept_2024", "oct_2024", "nov_2024"])
    args = parser.parse_args()

    reference = load_reference()
    current = load_production(args.period)

    summary = run_drift_analysis(reference, current, args.period)
    print_summary(summary)
```

### Étape 2.3 : Exécuter et analyser

```bash
# Générer les données de production simulées
python scripts/simulate_production_data.py

# Analyser chaque période
python monitoring/run_drift_check.py --period sept_2024
# → Drift faible attendu

python monitoring/run_drift_check.py --period oct_2024
# → Drift modéré

python monitoring/run_drift_check.py --period nov_2024
# → Drift élevé → ALERTE attendue

# Ouvrir les rapports HTML
open reports/drift/drift_nov_2024.html
```

**Questions à analyser :**
- Quelles features sont les plus driftées en novembre ?
- Le PSI de `page_values` dépasse-t-il le seuil critique ?
- Quelle serait votre recommandation : réentraîner ou non ?

---

## Partie 3 — Stack Docker Compose avec Monitoring (20 min)

### Étape 3.1 : docker-compose.yml minimal pour l'exercice

```yaml
# docker-compose.yml
version: '3.9'

services:
  ml-api:
    build: .
    ports: ["8000:8000"]
    environment:
      MODEL_PATH: /app/models/model.pkl
    volumes:
      - ./models:/app/models:ro
    networks: [mlops]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:v2.52.0
    ports: ["9090:9090"]
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks: [mlops]

  grafana:
    image: grafana/grafana:10.4.0
    ports: ["3000:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    networks: [mlops]
    depends_on: [prometheus]

networks:
  mlops:
    driver: bridge
```

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 10s

scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
    metrics_path: '/metrics'
```

### Étape 3.2 : Démarrer et tester

```bash
docker compose up -d

# Simuler du trafic pendant 2 minutes
python scripts/simulate_traffic.py --mode normal

# Accéder aux interfaces
# Prometheus : http://localhost:9090
# Grafana    : http://localhost:3000 (admin/admin123)

# Vérifier dans Prometheus :
# Requête : ecom_predictions_total
# Requête : ecom_predicted_conversion_rate
# Requête : ecom_feature_mean{feature_name="page_values"}
```

---

## Partie 4 — Créer le Dashboard Grafana (30 min)

### Étape 4.1 : Créer manuellement dans l'UI

Dans Grafana (`http://localhost:3000`) :

1. **Connexion** : admin / admin123
2. **Datasource** : Connections → Data Sources → Add → Prometheus → URL : `http://prometheus:9090`
3. **Dashboard** : Dashboards → New → New Dashboard → Add visualization

**Panneaux à créer :**

**Panneau 1 : Taux de conversion prédit (Stat)**
```
Requête : ecom_predicted_conversion_rate * 100
Titre   : Taux de conversion prédit (%)
Unité   : Percent (0-100)
Thresholds : 0=green, 5=yellow, 15=red
```

**Panneau 2 : Prédictions par seconde (Graph)**
```
Requête : sum(rate(ecom_predictions_total[1m]))
Titre   : Prédictions / seconde
```

**Panneau 3 : Distribution des probabilités (Bar chart)**
```
Requête : rate(ecom_conversion_probability_bucket[5m])
Titre   : Distribution des probabilités de conversion
```

**Panneau 4 : Moyenne de page_values (Graph)**
```
Requête : ecom_feature_mean{feature_name="page_values"}
Titre   : Valeur page moyenne (détecteur de dérive)
Alerte  : Si valeur < 15 pendant 5 min → warning
```

**Panneau 5 : Latence P99 (Stat)**
```
Requête : histogram_quantile(0.99, rate(ecom_prediction_latency_seconds_bucket[5m]))
Titre   : Latence P99
Unité   : seconds
Thresholds: 0=green, 0.1=yellow, 0.5=red
```

### Étape 4.2 : Simuler une dérive et observer

```bash
# Simuler une dérive progressive (page_values divisé par 2)
python -c "
import requests, random, time, numpy as np

print('Phase 1 : Trafic normal (1 min)')
for i in range(60):
    payload = {
        'page_values': random.uniform(15, 45),
        'product_related': random.randint(15, 40),
        'bounce_rates': random.uniform(0.01, 0.08),
        # autres features...
        'administrative': random.randint(0, 5),
        'administrative_duration': random.uniform(0, 200),
        'informational': random.randint(0, 3),
        'informational_duration': random.uniform(0, 100),
        'product_related_duration': random.uniform(500, 3000),
        'exit_rates': random.uniform(0.02, 0.12),
        'special_day': 0.0,
        'month': 11, 'visitor_type': 1, 'weekend': 0
    }
    requests.post('http://localhost:8000/predict', json=payload)
    time.sleep(1)

print('Phase 2 : Dérive (page_values réduit)')
for i in range(60):
    payload['page_values'] = random.uniform(2, 8)  # Dérive !
    requests.post('http://localhost:8000/predict', json=payload)
    time.sleep(1)
print('Done')
"
```

**Observez dans Grafana :** le graphique de `ecom_feature_mean{feature_name="page_values"}` doit montrer une chute nette à partir de la phase 2.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans Grafana, le dashboard ML complet avec tous les panneaux remplis. Montrer l'effet de la simulation de dérive : la métrique `page_values mean` qui chute, le taux de conversion prédit qui baisse. Mettre en évidence l'alerte Grafana qui se déclenche.
> **Expliquer :** "Regardez ce qui se passe au bout de 60 secondes : la valeur moyenne de `page_values` chute de 30 à 5. C'est exactement le genre de signal précoce qu'on cherche. Avant même de calculer un PSI complet, Grafana nous indique que quelque chose a changé dans les données d'entrée."

---

## Questions finales

1. Quelle est la différence entre le PSI et le test KS pour détecter une dérive ?
2. Quand une dérive des données ne se traduit-elle PAS forcément par une dégradation des performances ?
3. Comment le dashboard Grafana vous aide-t-il à distinguer une dérive réelle d'un pic de trafic ponctuel ?
4. Dans quel cas devez-vous réentraîner le modèle plutôt que simplement l'ajuster ?
5. Quel est le risque de configurer des alertes de dérive avec un seuil trop bas ?

---

## Résumé de ce qu'on a construit

```
✅ API FastAPI exposant /metrics (Prometheus format)
✅ Métriques ML : conversion rate, distribution probabilités, feature means
✅ Script Evidently : détection drift PSI sur 3 périodes
✅ Rapports HTML Evidently avec graphiques de distribution
✅ Stack Docker Compose : API + Prometheus + Grafana
✅ Dashboard Grafana avec 5 panneaux ML
✅ Simulation de dérive et observation en temps réel
```

---

## Aller plus loin

- Ajouter un **webhook d'alerte** Grafana vers Slack : Settings → Notification channels → Slack
- Créer un **job Airflow** qui exécute `run_drift_check.py` tous les jours à 8h
- Implémenter le **calcul du RMSE en production** (quand les labels sont disponibles avec délai)
- Ajouter **Evidently Cloud** pour un monitoring managé avec historique
