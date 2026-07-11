# Exercice 1 — Pipeline MLOps End-to-End

## Objectif

Construire un pipeline MLOps complet autour d'un modèle de classification : de l'entraînement jusqu'au déploiement automatisé via GitHub Actions.

**Durée estimée :** 2h30

**Niveau :** Intermédiaire

---

## Contexte

Vous êtes data scientist dans une entreprise de e-commerce. L'équipe marketing veut un modèle qui prédit si un client va **faire un achat** lors de sa prochaine visite sur le site (classification binaire).

Vous devez construire **toute la chaîne MLOps** :
1. Versionner les données avec DVC
2. Entraîner et tracker avec MLflow
3. Conteneuriser l'API avec Docker
4. Automatiser avec GitHub Actions

---

## Données

Nous utilisons le dataset **UCI Online Shoppers Intention** (simplifié) :

```python
# scripts/generate_data.py
"""Génère un dataset synthétique pour l'exercice."""
import pandas as pd
import numpy as np

np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "administrative": np.random.poisson(2, n),
    "administrative_duration": np.random.exponential(50, n),
    "informational": np.random.poisson(1, n),
    "informational_duration": np.random.exponential(30, n),
    "product_related": np.random.poisson(20, n),
    "product_related_duration": np.random.exponential(1000, n),
    "bounce_rates": np.random.beta(2, 8, n),
    "exit_rates": np.random.beta(3, 7, n),
    "page_values": np.random.exponential(20, n),
    "special_day": np.random.choice([0, 0, 0, 0.2, 0.4, 0.6, 0.8, 1.0], n),
    "month": np.random.choice(range(1, 13), n),
    "visitor_type": np.random.choice(["New_Visitor", "Returning_Visitor", "Other"], n),
    "weekend": np.random.choice([0, 1], n, p=[0.7, 0.3]),
})

# Variable cible : achat (15% de taux de conversion)
prob = 0.1 + 0.3 * (df["page_values"] > 10).astype(float) + \
             0.1 * (df["product_related"] > 30).astype(float)
df["revenue"] = (np.random.random(n) < prob.clip(0, 0.85)).astype(int)

df.to_csv("data/raw/shoppers.csv", index=False)
print(f"Dataset généré : {len(df)} lignes, {df['revenue'].mean():.1%} de conversions")
```

---

## Partie 1 — Mise en place DVC (20 min)

### Étape 1.1 : Initialiser le projet

```bash
# Créer le projet
mkdir ecommerce-mlops && cd ecommerce-mlops
git init
git commit --allow-empty -m "init: projet vide"

# Initialiser DVC
dvc init
git add .dvc/
git commit -m "feat: initialiser DVC"

# Créer la structure
mkdir -p data/raw data/processed models reports scripts tests .github/workflows
```

### Étape 1.2 : Générer et versionner les données

```bash
# Générer les données
python scripts/generate_data.py

# Versionner avec DVC
dvc add data/raw/shoppers.csv
git add data/raw/.gitignore data/raw/shoppers.csv.dvc
git commit -m "data: ajouter dataset shoppers v1"
```

### Étape 1.3 : Configurer le remote DVC

```bash
# Remote local (pour l'exercice)
mkdir -p /tmp/dvc-ecommerce
dvc remote add -d local /tmp/dvc-ecommerce
dvc push

git add .dvc/config
git commit -m "config: DVC remote local"
```

**Vérification :** `dvc status` doit afficher "Data and pipelines are up to date."

---

## Partie 2 — Pipeline DVC + MLflow (40 min)

### Étape 2.1 : Script de préparation des données

```python
# scripts/prepare.py
"""Prépare les données : encode les catégories, split train/test."""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import yaml, json, os

with open("params.yaml") as f:
    p = yaml.safe_load(f)["prepare"]

df = pd.read_csv("data/raw/shoppers.csv")

# Encoder les variables catégorielles
le = LabelEncoder()
df["visitor_type"] = le.fit_transform(df["visitor_type"])
# visitor_type est maintenant 0, 1, 2

X = df.drop(columns=["revenue"])
y = df["revenue"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=p["test_size"], random_state=p["random_state"], stratify=y
)

os.makedirs("data/processed", exist_ok=True)
train = X_train.copy()
train["revenue"] = y_train.values
test = X_test.copy()
test["revenue"] = y_test.values

train.to_csv("data/processed/train.csv", index=False)
test.to_csv("data/processed/test.csv", index=False)
print(f"Train: {len(train)}, Test: {len(test)}")
print(f"Taux de conversion train: {y_train.mean():.2%}")
```

### Étape 2.2 : Script d'entraînement

```python
# scripts/train.py
"""Entraîne le modèle de classification et logge dans MLflow."""
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import pickle, yaml, json, os
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    precision_score, recall_score, average_precision_score
)
from mlflow.models.signature import infer_signature

with open("params.yaml") as f:
    params = yaml.safe_load(f)

train_params = params["train"]

df_train = pd.read_csv("data/processed/train.csv")
X_train = df_train.drop(columns=["revenue"])
y_train = df_train["revenue"]

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("ecommerce-conversion")

with mlflow.start_run(run_name=f"{train_params['model_type']}_run"):
    mlflow.log_params(train_params)
    mlflow.set_tag("git_commit", os.getenv("GIT_COMMIT", "local"))

    if train_params["model_type"] == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=train_params["n_estimators"],
            max_depth=train_params["max_depth"],
            learning_rate=train_params["learning_rate"],
            random_state=42
        )
    else:
        model = RandomForestClassifier(
            n_estimators=train_params["n_estimators"],
            max_depth=train_params["max_depth"],
            random_state=42, n_jobs=-1
        )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_train)
    y_proba = model.predict_proba(X_train)[:, 1]

    metrics = {
        "train_accuracy": accuracy_score(y_train, y_pred),
        "train_f1": f1_score(y_train, y_pred),
        "train_roc_auc": roc_auc_score(y_train, y_proba),
        "train_precision": precision_score(y_train, y_pred),
        "train_recall": recall_score(y_train, y_pred),
    }
    mlflow.log_metrics(metrics)

    os.makedirs("models", exist_ok=True)
    with open("models/model.pkl", "wb") as f:
        pickle.dump(model, f)

    signature = infer_signature(X_train, y_proba)
    mlflow.sklearn.log_model(
        model, "model",
        signature=signature,
        registered_model_name="ecommerce-conversion-model"
    )

    os.makedirs("reports", exist_ok=True)
    with open("reports/train_metrics.json", "w") as f:
        json.dump({k: round(v, 4) for k, v in metrics.items()}, f, indent=2)

    print(f"F1: {metrics['train_f1']:.4f}, AUC: {metrics['train_roc_auc']:.4f}")
```

### Étape 2.3 : Script d'évaluation

```python
# scripts/evaluate.py
"""Évalue le modèle sur le jeu de test."""
import pandas as pd
import numpy as np
import pickle, json, os
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix
)

with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)

df_test = pd.read_csv("data/processed/test.csv")
X_test = df_test.drop(columns=["revenue"])
y_test = df_test["revenue"]

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

metrics = {
    "test_accuracy": round(accuracy_score(y_test, y_pred), 4),
    "test_f1": round(f1_score(y_test, y_pred), 4),
    "test_roc_auc": round(roc_auc_score(y_test, y_proba), 4),
    "test_precision": round(float(np.mean(y_pred[y_pred == 1] == y_test[y_pred == 1])), 4) if y_pred.sum() > 0 else 0,
    "test_recall": round(float(y_pred[y_test == 1].sum() / y_test.sum()), 4),
}

print("Métriques test :")
for k, v in metrics.items():
    print(f"  {k}: {v}")

print("\nClassification Report :")
print(classification_report(y_test, y_pred, target_names=["No purchase", "Purchase"]))

os.makedirs("reports", exist_ok=True)
with open("reports/eval_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

# Matrice de confusion pour DVC plots
cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(cm, columns=["pred_0", "pred_1"], index=["actual_0", "actual_1"])
cm_df.reset_index(inplace=True)
cm_df.rename(columns={"index": "actual"}, inplace=True)
cm_df.to_csv("reports/confusion_matrix.csv", index=False)
```

### Étape 2.4 : Configurer dvc.yaml et params.yaml

```yaml
# params.yaml
prepare:
  test_size: 0.2
  random_state: 42

train:
  model_type: gradient_boosting
  n_estimators: 100
  max_depth: 5
  learning_rate: 0.1
  random_state: 42

evaluate:
  threshold: 0.5
  min_f1: 0.60
  min_roc_auc: 0.75
```

```yaml
# dvc.yaml
stages:
  prepare:
    cmd: python scripts/prepare.py
    deps: [scripts/prepare.py, data/raw/shoppers.csv]
    params: [prepare]
    outs: [data/processed/train.csv, data/processed/test.csv]

  train:
    cmd: python scripts/train.py
    deps: [scripts/train.py, data/processed/train.csv]
    params: [train]
    outs: [models/model.pkl]
    metrics:
      - reports/train_metrics.json:
          cache: false

  evaluate:
    cmd: python scripts/evaluate.py
    deps: [scripts/evaluate.py, models/model.pkl, data/processed/test.csv]
    metrics:
      - reports/eval_metrics.json:
          cache: false
    plots:
      - reports/confusion_matrix.csv:
          cache: false
```

### Étape 2.5 : Exécuter le pipeline

```bash
dvc repro
dvc metrics show
# reports/eval_metrics.json:
#   test_f1: 0.7234
#   test_roc_auc: 0.8156

git add dvc.lock dvc.yaml params.yaml reports/
git commit -m "feat: pipeline DVC + MLflow opérationnel"
```

---

## Partie 3 — API FastAPI + Docker (30 min)

### Étape 3.1 : Créer l'API

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle, os
import pandas as pd
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

app = FastAPI(title="E-commerce Conversion Predictor")

# Charger le modèle
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
with open(MODEL_PATH, "rb") as f:
    MODEL = pickle.load(f)

PREDICTIONS = Counter("predictions_total", "Prédictions", ["outcome"])
LATENCY = Histogram("prediction_latency_seconds", "Latence")

class VisitorFeatures(BaseModel):
    administrative: float = Field(ge=0)
    administrative_duration: float = Field(ge=0)
    informational: float = Field(ge=0)
    informational_duration: float = Field(ge=0)
    product_related: float = Field(ge=0)
    product_related_duration: float = Field(ge=0)
    bounce_rates: float = Field(ge=0, le=1)
    exit_rates: float = Field(ge=0, le=1)
    page_values: float = Field(ge=0)
    special_day: float = Field(ge=0, le=1)
    month: int = Field(ge=1, le=12)
    visitor_type: int = Field(ge=0, le=2)
    weekend: int = Field(ge=0, le=1)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
def predict(features: VisitorFeatures):
    start = time.time()
    df = pd.DataFrame([features.model_dump()])
    proba = MODEL.predict_proba(df)[0][1]
    pred = int(proba >= 0.5)
    PREDICTIONS.labels(outcome="purchase" if pred else "no_purchase").inc()
    LATENCY.observe(time.time() - start)
    return {
        "will_purchase": bool(pred),
        "probability": round(float(proba), 4),
        "confidence": "high" if proba > 0.7 or proba < 0.3 else "medium"
    }
```

### Étape 3.2 : Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/
COPY models/ ./models/
ENV MODEL_PATH=/app/models/model.pkl
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Étape 3.3 : Tester l'image

```bash
docker build -t ecommerce-api:latest .

docker run -d --name ecom-test -p 8000:8000 ecommerce-api:latest

curl http://localhost:8000/health

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "administrative": 3, "administrative_duration": 120,
    "informational": 1, "informational_duration": 30,
    "product_related": 25, "product_related_duration": 1500,
    "bounce_rates": 0.05, "exit_rates": 0.08,
    "page_values": 35.0, "special_day": 0.0,
    "month": 11, "visitor_type": 1, "weekend": 0
  }'
# Résultat attendu : {"will_purchase": true, "probability": 0.73, "confidence": "high"}

docker stop ecom-test && docker rm ecom-test
```

---

## Partie 4 — GitHub Actions CI (20 min)

### Étape 4.1 : Workflow CI

```yaml
# .github/workflows/train-ci.yml
name: ML Training CI

on:
  push:
    branches: [main]
    paths: ['scripts/**', 'params.yaml', 'dvc.yaml']
  pull_request:
    branches: [main]

jobs:
  train-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate data (or pull from DVC)
        run: python scripts/generate_data.py

      - name: Run pipeline
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI || 'file:///tmp/mlruns' }}
        run: dvc repro --force

      - name: Validate metrics
        run: |
          python -c "
          import json, sys
          with open('reports/eval_metrics.json') as f:
              m = json.load(f)
          print(f'F1: {m[\"test_f1\"]}, AUC: {m[\"test_roc_auc\"]}')
          if m['test_f1'] < 0.55:
              print('ERREUR: F1 trop faible'); sys.exit(1)
          if m['test_roc_auc'] < 0.70:
              print('ERREUR: AUC trop faible'); sys.exit(1)
          print('Métriques OK')
          "

      - name: Build Docker image
        run: docker build -t ecommerce-api:ci-${{ github.sha }} .

      - name: Test Docker image
        run: |
          docker run -d --name ci-test -p 8000:8000 ecommerce-api:ci-${{ github.sha }}
          sleep 10
          curl -f http://localhost:8000/health
          docker stop ci-test && docker rm ci-test

      - name: Upload model artifact
        uses: actions/upload-artifact@v4
        with:
          name: model-${{ github.sha }}
          path: models/model.pkl
          retention-days: 14
```

---

## Questions de vérification

Après avoir terminé l'exercice, vérifiez que vous pouvez répondre à ces questions :

1. Quelle commande permet de retrouver exactement les données utilisées pour un entraînement donné ?
2. Comment MLflow identifie-t-il deux runs utilisant les mêmes paramètres ?
3. Quelle étape du pipeline DVC est sautée si les données n'ont pas changé ?
4. Comment tester qu'une image Docker fonctionne correctement avant de la pousser ?
5. Que se passe-t-il dans le workflow GitHub Actions si le F1-score est inférieur à 0.55 ?

---

## Aller plus loin (optionnel)

- Ajouter un test de non-régression : comparer le F1 du nouveau modèle avec le modèle en production dans MLflow
- Configurer un vrai remote DVC sur S3 ou GCS
- Ajouter une étape d'hyperparameter tuning avec `dvc exp run --set-param train.n_estimators=50,100,200`
- Créer un workflow de déploiement qui pousse l'image sur GitHub Container Registry

---

## Solution de référence

La solution complète est disponible dans le répertoire `solutions/exercice-01/`. Les points clés à vérifier :

```bash
# Vérifier que le pipeline est reproductible
dvc repro --force
dvc metrics show

# Vérifier le versioning des données
git log --oneline data/raw/shoppers.csv.dvc

# Vérifier que l'image Docker répond correctement
docker run --rm -p 8000:8000 ecommerce-api:latest &
curl -s http://localhost:8000/health | python -m json.tool
```
