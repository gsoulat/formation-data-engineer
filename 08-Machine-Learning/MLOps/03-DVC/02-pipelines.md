# DVC — Pipelines reproductibles

## Pourquoi des pipelines ?

Un pipeline DVC transforme une série de scripts en un **graphe de dépendances** (DAG) où :
- Chaque étape déclare ses inputs et outputs
- DVC sait quelles étapes rejouer quand quelque chose change
- Le pipeline entier est reproductible avec `dvc repro`

```
Sans pipeline :         Avec pipeline DVC :
────────────────         ─────────────────────
python prepare.py        dvc repro
python train.py    →     (rejoue uniquement les étapes
python evaluate.py        dont les inputs ont changé)
```

---

## Structure d'un pipeline DVC

Un pipeline DVC est défini dans le fichier `dvc.yaml` :

```yaml
# dvc.yaml
stages:
  prepare:           # Nom de l'étape
    cmd: python scripts/prepare.py  # Commande à exécuter
    deps:                            # Fichiers dont dépend cette étape
      - scripts/prepare.py
      - data/raw/housing.csv
    params:                          # Paramètres depuis params.yaml
      - prepare.test_size
      - prepare.random_state
    outs:                            # Fichiers produits
      - data/processed/train.csv
      - data/processed/test.csv

  train:
    cmd: python scripts/train.py
    deps:
      - scripts/train.py
      - data/processed/train.csv
    params:
      - train.n_estimators
      - train.max_depth
      - train.learning_rate
    outs:
      - models/model.pkl
    metrics:                         # Métriques à tracker
      - reports/metrics.json:
          cache: false               # Ne pas cacher (petit fichier)

  evaluate:
    cmd: python scripts/evaluate.py
    deps:
      - scripts/evaluate.py
      - models/model.pkl
      - data/processed/test.csv
    metrics:
      - reports/evaluation.json:
          cache: false
    plots:                           # Graphiques à générer
      - reports/confusion_matrix.csv:
          cache: false
```

---

## Le fichier params.yaml

```yaml
# params.yaml
prepare:
  test_size: 0.2
  random_state: 42
  target_column: target

train:
  n_estimators: 100
  max_depth: 10
  min_samples_split: 5
  random_state: 42
  model_type: random_forest  # ou 'gradient_boosting'

evaluate:
  threshold: 0.5
  metrics:
    - rmse
    - mae
    - r2
```

---

## Scripts du pipeline

### scripts/prepare.py

```python
"""Préparation des données."""
import sys
import yaml
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json
import os

# Charger les paramètres
with open("params.yaml") as f:
    params = yaml.safe_load(f)["prepare"]

test_size = params["test_size"]
random_state = params["random_state"]
target_column = params["target_column"]

print(f"Paramètres : test_size={test_size}, random_state={random_state}")

# Charger les données brutes
# (dans un vrai projet, lire depuis data/raw/housing.csv)
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df[target_column] = housing.target

print(f"Dataset chargé : {len(df)} lignes, {len(df.columns)} colonnes")

# Vérifications qualité
assert df.isnull().sum().sum() == 0, "Des valeurs manquantes trouvées !"
print(f"Qualité OK : aucune valeur manquante")

# Split
X = df.drop(columns=[target_column])
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=random_state
)

# Assembler les DataFrames train/test
train_df = X_train.copy()
train_df[target_column] = y_train.values

test_df = X_test.copy()
test_df[target_column] = y_test.values

# Sauvegarder
os.makedirs("data/processed", exist_ok=True)
train_df.to_csv("data/processed/train.csv", index=False)
test_df.to_csv("data/processed/test.csv", index=False)

print(f"Train : {len(train_df)} lignes → data/processed/train.csv")
print(f"Test  : {len(test_df)} lignes → data/processed/test.csv")

# Rapport
os.makedirs("reports", exist_ok=True)
report = {
    "total_samples": len(df),
    "train_samples": len(train_df),
    "test_samples": len(test_df),
    "features": list(X.columns),
    "target_stats": {
        "mean": float(y.mean()),
        "std": float(y.std()),
        "min": float(y.min()),
        "max": float(y.max())
    }
}
with open("reports/prepare_report.json", "w") as f:
    json.dump(report, f, indent=2)
print("Rapport de préparation sauvegardé.")
```

### scripts/train.py

```python
"""Entraînement du modèle."""
import yaml
import json
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import mlflow.sklearn

# Charger les paramètres
with open("params.yaml") as f:
    params = yaml.safe_load(f)["train"]

print(f"Paramètres d'entraînement : {params}")

# Charger les données
train_df = pd.read_csv("data/processed/train.csv")
target_col = "target"

X_train = train_df.drop(columns=[target_col])
y_train = train_df[target_col]

print(f"Données d'entraînement : {X_train.shape}")

# Configurer MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("prix-immobilier-dvc")

# Choisir le modèle selon le paramètre
model_type = params.get("model_type", "random_forest")

with mlflow.start_run():
    # Logger tous les params DVC
    mlflow.log_params(params)
    mlflow.set_tag("pipeline", "dvc")

    if model_type == "random_forest":
        model = RandomForestRegressor(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            min_samples_split=params["min_samples_split"],
            random_state=params["random_state"],
            n_jobs=-1
        )
    elif model_type == "gradient_boosting":
        model = GradientBoostingRegressor(
            n_estimators=params["n_estimators"],
            max_depth=params.get("max_depth", 5),
            random_state=params["random_state"]
        )
    else:
        raise ValueError(f"model_type inconnu : {model_type}")

    print(f"Entraînement {model_type}...")
    model.fit(X_train, y_train)

    # Métriques sur train
    y_pred_train = model.predict(X_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_r2 = r2_score(y_train, y_pred_train)

    mlflow.log_metric("train_rmse", train_rmse)
    mlflow.log_metric("train_r2", train_r2)

    print(f"Train RMSE: {train_rmse:.4f}, R²: {train_r2:.4f}")

    # Sauvegarder le modèle
    os.makedirs("models", exist_ok=True)
    with open("models/model.pkl", "wb") as f:
        pickle.dump(model, f)

    # Logger aussi dans MLflow
    mlflow.sklearn.log_model(model, "model")

    run_id = mlflow.active_run().info.run_id

# Sauvegarder les métriques de train pour DVC
os.makedirs("reports", exist_ok=True)
metrics = {
    "train_rmse": round(train_rmse, 4),
    "train_r2": round(train_r2, 4),
    "mlflow_run_id": run_id
}
with open("reports/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print(f"Modèle sauvegardé. Run MLflow : {run_id}")
```

### scripts/evaluate.py

```python
"""Évaluation finale sur le jeu de test."""
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os

# Charger le modèle
with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)

# Charger les données de test
test_df = pd.read_csv("data/processed/test.csv")
target_col = "target"
X_test = test_df.drop(columns=[target_col])
y_test = test_df[target_col]

print(f"Données de test : {X_test.shape}")

# Prédire
y_pred = model.predict(X_test)

# Calculer les métriques
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Test RMSE : {rmse:.4f}")
print(f"Test MAE  : {mae:.4f}")
print(f"Test R²   : {r2:.4f}")

# Sauvegarder les métriques d'évaluation
metrics = {
    "test_rmse": round(rmse, 4),
    "test_mae": round(mae, 4),
    "test_r2": round(r2, 4)
}

os.makedirs("reports", exist_ok=True)
with open("reports/evaluation.json", "w") as f:
    json.dump(metrics, f, indent=2)

# Sauvegarder les prédictions pour le plot DVC
predictions_df = pd.DataFrame({
    "actual": y_test.values,
    "predicted": y_pred,
    "residual": y_test.values - y_pred
})
predictions_df.to_csv("reports/predictions.csv", index=False)

print(f"Évaluation terminée → reports/evaluation.json")
```

---

## Exécuter et reproduire le pipeline

```bash
# ── Première exécution ──────────────────────────────────────────
dvc repro
# Running stage 'prepare':   > python scripts/prepare.py
# Running stage 'train':     > python scripts/train.py
# Running stage 'evaluate':  > python scripts/evaluate.py

# ── Voir l'état du pipeline ─────────────────────────────────────
dvc status
# Pipeline is up to date

# ── Modifier un paramètre et rejouer ────────────────────────────
# Éditer params.yaml : n_estimators: 100 → 200
dvc repro
# Stage 'prepare' didn't change, skipping
# Running stage 'train':     > python scripts/train.py
# Running stage 'evaluate':  > python scripts/evaluate.py
# (seules les étapes affectées sont rejouées !)

# ── Forcer la réexécution complète ──────────────────────────────
dvc repro --force

# ── Committer le lock file ──────────────────────────────────────
git add dvc.lock dvc.yaml params.yaml reports/
git commit -m "exp: n_estimators=200, RMSE amélioré"
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Afficher le DAG du pipeline avec `dvc dag`, puis montrer `dvc repro` en action : d'abord toutes les étapes s'exécutent, puis après une seconde exécution sans changement, toutes les étapes sont skippées, puis après modification d'un paramètre, seulement les étapes impactées se rejouent.
> **Expliquer :** "C'est le principe du cache intelligent de DVC. Si vous entraînez 50 modèles et que vous changez uniquement l'hyperparamètre n_estimators, DVC ne retraite pas les données. Ça économise énormément de temps et de compute."

---

## Visualiser le DAG

```bash
# Afficher le graphe dans le terminal
dvc dag

# ┌───────────────────────────────────┐
# │ data/raw/housing.csv.dvc          │
# └──────────────────┬────────────────┘
#                    │
#             ┌──────▼──────┐
#             │   prepare   │
#             └──────┬──────┘
#                    │
#             ┌──────▼──────┐
#             │    train    │
#             └──────┬──────┘
#                    │
#             ┌──────▼──────┐
#             │  evaluate   │
#             └─────────────┘

# Exporter en DOT (Graphviz)
dvc dag --dot > pipeline.dot
dot -Tpng pipeline.dot -o pipeline.png
```

---

## Comparer des expériences avec DVC

```bash
# Voir les métriques actuelles
dvc metrics show
# reports/evaluation.json:
#   test_rmse: 38.7420
#   test_mae: 26.3310
#   test_r2: 0.8801

# Comparer avec un commit précédent
dvc metrics diff HEAD~1
# Path                    Metric     Old      New     Change
# reports/evaluation.json  test_rmse  40.123   38.742  -1.381 (-3.44%)
# reports/evaluation.json  test_r2    0.865    0.880   +0.015 (+1.73%)

# Comparer plusieurs branches/experiments
dvc metrics diff main experiment/boosting
```

---

## DVC Experiments — Gérer les expériences

DVC Experiments permettent de lancer et comparer des runs sans créer de commits Git :

```bash
# Lancer une expérience avec un paramètre modifié
dvc exp run --set-param train.n_estimators=200

# Modifier plusieurs paramètres
dvc exp run \
  --set-param train.n_estimators=300 \
  --set-param train.max_depth=15 \
  --name "exp_rf_large"

# Voir toutes les expériences
dvc exp show
# ┌──────────────────┬──────────────┬──────────┬───────┬────────────┐
# │ Experiment       │ Created      │ test_rmse│ test_r2│n_estimators│
# ├──────────────────┼──────────────┼──────────┼───────┼────────────┤
# │ workspace        │ Jan 20, 12:00│ 38.74    │ 0.880 │ 100        │
# │ exp_rf_large     │ Jan 20, 12:10│ 36.21    │ 0.893 │ 300        │
# └──────────────────┴──────────────┴──────────┴───────┴────────────┘

# Promouvoir la meilleure expérience en commit Git
dvc exp apply exp_rf_large

# Lancer plusieurs expériences en parallèle (grid search)
dvc exp run \
  --set-param train.n_estimators=50,100,200,300 \
  --set-param train.max_depth=5,10,15 \
  --jobs 4  # 4 expériences en parallèle
```

---

## Intégration DVC + Git + MLflow

```
Workflow complet :
──────────────────
1. Modifier params.yaml (ex: n_estimators: 200)
2. dvc repro  →  train.py logge dans MLflow
3. dvc metrics show  →  voir les résultats
4. Si bon résultat :
   git add dvc.lock params.yaml reports/
   git commit -m "exp: rf n_estimators=200, RMSE -3%"
   dvc push  →  sauvegarder les artefacts
```

```python
# scripts/train.py — intégration DVC + MLflow
import yaml
import mlflow
import os

# Récupérer le hash Git pour traçabilité
import subprocess
try:
    git_hash = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"]
    ).decode().strip()
except:
    git_hash = "unknown"

with mlflow.start_run():
    # Lier MLflow run au commit Git
    mlflow.set_tag("git_commit", git_hash)
    mlflow.set_tag("dvc_pipeline", "true")

    # Logger les paramètres DVC
    with open("params.yaml") as f:
        all_params = yaml.safe_load(f)
    mlflow.log_params(all_params.get("train", {}))

    # ... entraînement ...
```

---

## Pipeline avancé avec plusieurs branches

```yaml
# dvc.yaml — pipeline avec feature engineering optionnel
stages:
  download:
    cmd: python scripts/download.py
    deps:
      - scripts/download.py
    outs:
      - data/raw/housing.csv

  prepare:
    cmd: python scripts/prepare.py
    deps:
      - scripts/prepare.py
      - data/raw/housing.csv
    params:
      - prepare
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  feature_engineering:
    cmd: python scripts/features.py
    deps:
      - scripts/features.py
      - data/processed/train.csv
      - data/processed/test.csv
    params:
      - features
    outs:
      - data/features/train_features.csv
      - data/features/test_features.csv

  train_rf:
    cmd: python scripts/train.py --model random_forest
    deps:
      - scripts/train.py
      - data/features/train_features.csv
    params:
      - train.random_forest
    outs:
      - models/rf_model.pkl
    metrics:
      - reports/rf_metrics.json:
          cache: false

  train_gb:
    cmd: python scripts/train.py --model gradient_boosting
    deps:
      - scripts/train.py
      - data/features/train_features.csv
    params:
      - train.gradient_boosting
    outs:
      - models/gb_model.pkl
    metrics:
      - reports/gb_metrics.json:
          cache: false

  select_best:
    cmd: python scripts/select_best.py
    deps:
      - scripts/select_best.py
      - models/rf_model.pkl
      - models/gb_model.pkl
      - reports/rf_metrics.json
      - reports/gb_metrics.json
    outs:
      - models/best_model.pkl
    metrics:
      - reports/final_metrics.json:
          cache: false
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer `dvc exp show` dans le terminal et montrer le tableau comparatif de plusieurs expériences avec leurs métriques et paramètres.
> **Expliquer :** "DVC Experiments nous donne une vue similaire à MLflow mais directement dans le terminal, avec la correspondance Git. La colonne 'test_rmse' nous permet de choisir la meilleure expérience à promouvoir en commit définitif."

---

## Résumé : DVC Pipelines

| Commande | Action |
|---|---|
| `dvc repro` | Rejouer le pipeline (smart cache) |
| `dvc repro --force` | Forcer la réexécution complète |
| `dvc status` | Voir ce qui a changé |
| `dvc dag` | Visualiser le graphe |
| `dvc metrics show` | Afficher les métriques |
| `dvc metrics diff` | Comparer les métriques |
| `dvc params diff` | Comparer les paramètres |
| `dvc exp run` | Lancer une expérience |
| `dvc exp show` | Voir le tableau des expériences |
| `dvc exp apply NAME` | Appliquer une expérience |
