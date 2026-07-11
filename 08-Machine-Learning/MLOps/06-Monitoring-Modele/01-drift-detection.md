# Détection de dérive — Data Drift et Concept Drift

## Pourquoi un modèle se dégrade-t-il en production ?

Un modèle entraîné en janvier peut être excellent. En juillet, sans avoir changé une ligne de code, ses prédictions peuvent devenir mauvaises. Pourquoi ?

```
Janvier 2024                          Juillet 2024
────────────────                      ────────────────
Entraînement :                        Production :
- données immobilières 2020-2023      - demandes immobilières 2024
- marché pré-taux-montants           - marché post-hausse des taux
- revenu médian : 4.5k€              - revenu médian : 3.8k€ (récession)
- prix moyen : 350k€                 - prix moyen : 280k€

Résultat : le modèle surestime systématiquement les prix de 20-25%
```

Ce phénomène s'appelle la **dérive** (drift).

---

## Les types de dérive

### Data Drift (dérive des données)

La distribution des **features d'entrée** change, mais la relation features → target reste la même.

```
Distribution de MedInc (revenu médian) :
──────────────────────────────────────────
Entraînement : μ=4.5, σ=1.2  |  Production : μ=3.8, σ=0.9
                              │
        ██                    │         ███
       ████                   │        █████
      ██████                  │       ███████
     █████████                │      ██████████
────────────────              │  ────────────────────
    0    5    10              │       0    5    10
```

### Concept Drift (dérive du concept)

La **relation** entre features et target change.

```
Avant : prix = f(revenu, localisation, surface) → R² = 0.88
Après : la localisation est devenue bien plus importante
        (télétravail → exode urbain)
        Le même modèle donne maintenant R² = 0.62
```

### Label Drift

La **distribution de la variable cible** change.

```
Entraînement : 30% ventes > 500k€
Production   : 15% ventes > 500k€ (retournement de marché)
```

### Prediction Drift

La **distribution des prédictions** change (souvent un symptôme des dérives ci-dessus).

---

## Evidently AI — Librairie de détection de dérive

Evidently est la bibliothèque open-source de référence pour la détection de dérive en ML.

```bash
pip install evidently
```

---

## Rapport de drift en HTML

```python
# monitoring/drift_report.py
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import (
    DatasetDriftMetric,
    DataDriftTable,
    ColumnDriftMetric,
    ColumnSummaryMetric
)

# ── 1. Charger les données ─────────────────────────────────────
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['target'] = housing.target

# Simuler des données de référence (entraînement) et de production
reference_data, current_data = train_test_split(df, test_size=0.3, random_state=42)

# Simuler une dérive artificielle sur les données courantes
# (dans la réalité, current_data = données collectées en production)
current_data = current_data.copy()
current_data["MedInc"] = current_data["MedInc"] * 0.8      # Revenus en baisse
current_data["Population"] = current_data["Population"] * 1.2  # Densification

print(f"Référence : {len(reference_data)} lignes")
print(f"Courant   : {len(current_data)} lignes")

# ── 2. Créer le rapport de drift ───────────────────────────────
report = Report(metrics=[
    DataDriftPreset(),           # Détection de drift sur toutes les features
    DataQualityPreset(),         # Qualité des données
])

report.run(
    reference_data=reference_data.drop(columns=['target']),
    current_data=current_data.drop(columns=['target'])
)

# ── 3. Exporter en HTML ────────────────────────────────────────
report.save_html("reports/drift_report.html")
print("Rapport généré : reports/drift_report.html")

# ── 4. Obtenir les résultats en JSON ───────────────────────────
result = report.as_dict()
print("\nRésumé du drift :")
for metric_result in result["metrics"]:
    metric_id = metric_result["metric"]
    result_data = metric_result.get("result", {})
    if "dataset_drift" in result_data:
        print(f"  Drift détecté : {result_data['dataset_drift']}")
        print(f"  Features avec drift : {result_data.get('number_of_drifted_columns', 0)}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le fichier `reports/drift_report.html` dans le navigateur et montrer : (1) le tableau de synthèse avec les colonnes en rouge/vert selon le drift détecté, (2) les graphiques de distribution superposés pour une feature driftée (ex: MedInc), (3) le score statistique de drift.
> **Expliquer :** "Ce rapport est généré automatiquement en quelques lignes de code. En production, on le génère chaque jour avec les nouvelles données et on envoie une alerte si le score de drift dépasse un seuil. Les graphiques de distribution permettent de comprendre visuellement ce qui a changé."

---

## Tests statistiques de drift

Evidently utilise différents tests statistiques selon le type de données :

```python
from evidently.metrics import ColumnDriftMetric
from evidently.report import Report

# Tests disponibles :
# - "ks" : Kolmogorov-Smirnov (données continues)
# - "psi" : Population Stability Index (données continues)
# - "wasserstein" : Distance de Wasserstein (données continues)
# - "chisquare" : Chi-2 (données catégorielles)
# - "jensenshannon" : Jensen-Shannon (données catégorielles et continues)
# - "z" : Z-test (proportions)

report = Report(metrics=[
    ColumnDriftMetric(
        column_name="MedInc",
        stattest="ks",          # Test KS pour les données continues
        stattest_threshold=0.05  # p-value threshold
    ),
    ColumnDriftMetric(
        column_name="HouseAge",
        stattest="psi",
        stattest_threshold=0.2  # PSI : > 0.2 = dérive significative
    ),
])

report.run(reference_data=reference_data, current_data=current_data)
result = report.as_dict()

for metric in result["metrics"]:
    res = metric.get("result", {})
    if "drift_detected" in res:
        col = res.get("column_name")
        drift = res.get("drift_detected")
        score = res.get("drift_score")
        print(f"  {col}: drift={drift}, score={score:.4f}")
```

---

## Monitoring continu avec Evidently

```python
# monitoring/continuous_drift_monitor.py
"""
Moniteur de drift à exécuter périodiquement (ex: via cron ou Airflow).
"""
import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import DatasetDriftMetric

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DRIFT_THRESHOLD = 0.3        # Proportion de features driftées déclenchant l'alerte
PSI_THRESHOLD = 0.2           # Seuil PSI pour dérive significative
REPORTS_DIR = Path("reports/drift")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_reference_data() -> pd.DataFrame:
    """Charger les données de référence (données d'entraînement)."""
    return pd.read_csv("data/processed/train.csv")

def load_production_data(days_back: int = 7) -> pd.DataFrame:
    """
    Charger les données de production récentes.
    Dans la réalité : requête base de données, API, etc.
    """
    # Simuler des données de production avec dérive légère
    ref = load_reference_data()
    np.random.seed(int(datetime.now().timestamp()) % 1000)

    prod = ref.sample(n=500, replace=True).copy()
    # Simulation de dérive progressive
    prod["MedInc"] *= np.random.uniform(0.85, 0.95)
    prod["AveOccup"] *= np.random.uniform(1.1, 1.3)

    return prod

def run_drift_check(date: str = None) -> dict:
    """Exécuter un check de drift et retourner les résultats."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Drift check pour {date}")

    # Charger les données
    reference = load_reference_data().drop(columns=["target"], errors="ignore")
    production = load_production_data()

    feature_cols = [c for c in reference.columns if c != "target"]
    reference = reference[feature_cols]
    production = production[feature_cols]

    # Rapport Evidently
    report = Report(metrics=[
        DatasetDriftMetric(),
        DataDriftPreset(),
    ])
    report.run(reference_data=reference, current_data=production)

    # Extraire les résultats
    result = report.as_dict()
    drift_metrics = {}

    for metric in result["metrics"]:
        res = metric.get("result", {})
        if "dataset_drift" in res:
            drift_metrics["dataset_drift"] = res["dataset_drift"]
            drift_metrics["drifted_columns"] = res.get("number_of_drifted_columns", 0)
            drift_metrics["total_columns"] = res.get("number_of_columns", 0)
            drift_metrics["drift_share"] = res.get("share_of_drifted_columns", 0)

    # Sauvegarder le rapport HTML
    report_path = REPORTS_DIR / f"drift_{date}.html"
    report.save_html(str(report_path))

    # Sauvegarder les métriques JSON
    metrics_path = REPORTS_DIR / f"drift_{date}.json"
    metrics_data = {
        "date": date,
        "metrics": drift_metrics,
        "alert": drift_metrics.get("drift_share", 0) > DRIFT_THRESHOLD
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics_data, f, indent=2)

    logger.info(f"Résultats : {drift_metrics}")
    return metrics_data

def send_alert(metrics: dict):
    """Envoyer une alerte si dérive détectée."""
    if not metrics.get("alert"):
        return

    message = (
        f"ALERTE DRIFT DÉTECTÉ — {metrics['date']}\n"
        f"Features driftées : {metrics['metrics'].get('drifted_columns')}"
        f" / {metrics['metrics'].get('total_columns')}\n"
        f"Score de drift : {metrics['metrics'].get('drift_share', 0):.1%}"
    )

    logger.warning(message)

    # Envoyer vers Slack (si webhook configuré)
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if webhook_url:
        import requests
        requests.post(webhook_url, json={"text": message})

if __name__ == "__main__":
    results = run_drift_check()
    send_alert(results)
    print(json.dumps(results, indent=2))
```

---

## Tableau de bord de drift avec Streamlit

```python
# monitoring/drift_dashboard.py
"""
Dashboard interactif de monitoring drift.
streamlit run monitoring/drift_dashboard.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

st.set_page_config(
    page_title="ML Model Drift Monitor",
    page_icon="📊",
    layout="wide"
)

st.title("Monitoring de dérive — Modèle Prix Immobilier")

# ── Sidebar ────────────────────────────────────────────────────
st.sidebar.header("Configuration")
days_back = st.sidebar.slider("Fenêtre d'analyse (jours)", 7, 90, 30)
drift_threshold = st.sidebar.slider("Seuil d'alerte drift", 0.1, 0.5, 0.3)

# ── Charger les données ────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache 5 minutes
def load_data():
    from sklearn.datasets import fetch_california_housing
    housing = fetch_california_housing()
    df = pd.DataFrame(housing.data, columns=housing.feature_names)
    return df

df = load_data()
n_ref = int(len(df) * 0.7)
reference = df.iloc[:n_ref]

# Simuler données de production avec dérive
np.random.seed(42)
current = df.iloc[n_ref:].copy()
current["MedInc"] *= 0.85
current["AveOccup"] *= 1.2

# ── Métriques principales ──────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Lignes référence", f"{len(reference):,}")
with col2:
    st.metric("Lignes production", f"{len(current):,}")
with col3:
    drift_score = abs(current["MedInc"].mean() - reference["MedInc"].mean())
    st.metric("Score drift MedInc", f"{drift_score:.3f}",
              delta=f"{drift_score:.3f}", delta_color="inverse")
with col4:
    alerted = drift_score > drift_threshold
    st.metric("Alerte", "OUI" if alerted else "NON",
              delta="Dérive détectée" if alerted else "Normal",
              delta_color="inverse" if alerted else "off")

# ── Comparaison des distributions ─────────────────────────────
st.subheader("Distribution des features")
feature_to_compare = st.selectbox("Choisir une feature", df.columns.tolist())

fig = go.Figure()
fig.add_trace(go.Histogram(
    x=reference[feature_to_compare],
    name="Référence (train)",
    opacity=0.7,
    nbinsx=50
))
fig.add_trace(go.Histogram(
    x=current[feature_to_compare],
    name="Production",
    opacity=0.7,
    nbinsx=50
))
fig.update_layout(
    barmode="overlay",
    title=f"Distribution de {feature_to_compare}",
    xaxis_title=feature_to_compare,
    yaxis_title="Fréquence"
)
st.plotly_chart(fig, use_container_width=True)

# ── Tableau de drift par feature ───────────────────────────────
st.subheader("Score de drift par feature")
drift_data = []
for col in df.columns:
    ref_mean = reference[col].mean()
    cur_mean = current[col].mean()
    drift = abs(cur_mean - ref_mean) / (ref_mean + 1e-8)
    drift_data.append({
        "Feature": col,
        "Moy. Référence": round(ref_mean, 3),
        "Moy. Production": round(cur_mean, 3),
        "Drift (%)": round(drift * 100, 1)
    })

drift_df = pd.DataFrame(drift_data).sort_values("Drift (%)", ascending=False)
st.dataframe(
    drift_df.style.background_gradient(subset=["Drift (%)"], cmap="RdYlGn_r"),
    use_container_width=True
)
```

---

## Intégration avec MLflow : logger les résultats de drift

```python
# monitoring/log_drift_to_mlflow.py
"""Logge les métriques de drift dans MLflow pour le suivi historique."""
import mlflow
import json
from datetime import datetime

def log_drift_to_mlflow(drift_results: dict, experiment_name: str = "drift-monitoring"):
    """Logge un rapport de drift comme un run MLflow."""
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"drift-check-{drift_results['date']}"):
        # Métriques
        metrics = drift_results.get("metrics", {})
        mlflow.log_metric("drift_share", metrics.get("drift_share", 0))
        mlflow.log_metric("drifted_columns", metrics.get("drifted_columns", 0))
        mlflow.log_metric("dataset_drift", int(metrics.get("dataset_drift", False)))

        # Tags
        mlflow.set_tag("check_date", drift_results["date"])
        mlflow.set_tag("alert_triggered", str(drift_results.get("alert", False)))
        mlflow.set_tag("check_type", "drift_monitoring")

        # Rapport HTML comme artefact
        report_path = f"reports/drift/drift_{drift_results['date']}.html"
        mlflow.log_artifact(report_path, "drift_reports")

        print(f"Drift loggé dans MLflow - Run: {mlflow.active_run().info.run_id}")
```

---

## Seuils PSI de référence

| Valeur PSI | Interprétation | Action |
|---|---|---|
| PSI < 0.1 | Changement insignifiant | Aucune action |
| 0.1 ≤ PSI < 0.2 | Changement modéré | Surveiller |
| PSI ≥ 0.2 | Changement significatif | Réentraîner le modèle |
| PSI ≥ 0.3 | Dérive sévère | Réentraîner en urgence |

---

## Résumé

```
Workflow de monitoring drift (à exécuter quotidiennement) :
────────────────────────────────────────────────────────────
1. Collecter les données de production (dernières 24h / 7j)
2. Comparer avec les données de référence (train)
3. Calculer les métriques de drift (PSI, KS, etc.)
4. Générer le rapport Evidently HTML
5. Logger les métriques dans MLflow
6. Si drift > seuil → alerter l'équipe + déclencher réentraînement
```
