# GitHub Actions — Workflow d'entraînement ML

## Pourquoi CI pour le Machine Learning ?

En développement logiciel classique, le CI vérifie que le code compile et que les tests passent. En ML, le CI doit en plus :

- Vérifier la qualité des données
- Entraîner le modèle de façon reproductible
- Évaluer les performances et les comparer au modèle actuel
- Empêcher le déploiement si les métriques régressent
- Tracer chaque entraînement (MLflow)

```
Push vers main/PR
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                   CI Pipeline ML                         │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────┐│
│  │  Lint &  │──▶│Validation│──▶│    Entraînement      ││
│  │  Tests   │   │ données  │   │    + MLflow          ││
│  └──────────┘   └──────────┘   └──────────┬───────────┘│
│                                            │            │
│  ┌─────────────────────────────────────────▼───────────┐│
│  │         Évaluation & Comparaison                    ││
│  │   Nouveau RMSE < RMSE actuel ?                      ││
│  │   OUI → Upload artifact + rapport                  ││
│  │   NON → Fail le job + notification                 ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## Structure du projet pour CI

```
ml-project/
├── .github/
│   └── workflows/
│       ├── train.yml          ← Workflow d'entraînement
│       └── deploy.yml         ← Workflow de déploiement
├── scripts/
│   ├── prepare.py
│   ├── train.py
│   └── evaluate.py
├── tests/
│   ├── test_data.py           ← Tests de qualité données
│   └── test_model.py          ← Tests du modèle
├── data/
│   └── *.dvc
├── params.yaml
├── dvc.yaml
└── requirements.txt
```

---

## Workflow d'entraînement : version simple

```yaml
# .github/workflows/train.yml
name: ML Training Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'scripts/**'
      - 'params.yaml'
      - 'dvc.yaml'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Déclenchement manuel depuis l'UI GitHub

env:
  MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
  PYTHON_VERSION: '3.11'

jobs:
  train:
    name: Train and Evaluate Model
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      # ── 1. Checkout du code ────────────────────────────────────
      - name: Checkout repository
        uses: actions/checkout@v4

      # ── 2. Configurer Python ───────────────────────────────────
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      # ── 3. Installer les dépendances ───────────────────────────
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      # ── 4. Configurer DVC avec les credentials AWS ─────────────
      - name: Configure DVC remote
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          dvc remote modify myremote access_key_id $AWS_ACCESS_KEY_ID
          dvc remote modify myremote secret_access_key $AWS_SECRET_ACCESS_KEY

      # ── 5. Récupérer les données depuis DVC ────────────────────
      - name: Pull data with DVC
        run: dvc pull

      # ── 6. Tests qualité des données ───────────────────────────
      - name: Validate data quality
        run: pytest tests/test_data.py -v

      # ── 7. Entraîner le modèle ─────────────────────────────────
      - name: Train model
        run: dvc repro train

      # ── 8. Évaluer le modèle ───────────────────────────────────
      - name: Evaluate model
        run: dvc repro evaluate

      # ── 9. Vérifier que les métriques sont acceptables ─────────
      - name: Check metrics threshold
        run: |
          python -c "
          import json, sys
          with open('reports/evaluation.json') as f:
              metrics = json.load(f)
          rmse = metrics['test_rmse']
          threshold = 45.0
          print(f'RMSE: {rmse} (seuil: {threshold})')
          if rmse > threshold:
              print(f'ERREUR: RMSE {rmse} dépasse le seuil {threshold}')
              sys.exit(1)
          print('Métriques OK')
          "

      # ── 10. Uploader les artefacts ─────────────────────────────
      - name: Upload model artifact
        uses: actions/upload-artifact@v4
        with:
          name: trained-model-${{ github.sha }}
          path: |
            models/model.pkl
            reports/
          retention-days: 30

      # ── 11. Commenter la PR avec les métriques ─────────────────
      - name: Comment PR with metrics
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const metrics = JSON.parse(fs.readFileSync('reports/evaluation.json'));
            const body = `## Résultats d'entraînement ML

            | Métrique | Valeur |
            |---|---|
            | RMSE (test) | ${metrics.test_rmse} |
            | MAE (test) | ${metrics.test_mae} |
            | R² (test) | ${metrics.test_r2} |

            Commit: \`${context.sha.substring(0, 8)}\``;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans GitHub, onglet Actions, montrer un workflow en cours d'exécution avec les étapes visibles (cercles verts/en cours), puis le détail d'une étape (logs d'entraînement) et enfin les artifacts uploadés.
> **Expliquer :** "Regardez comment chaque push déclenche automatiquement l'entraînement. Les logs sont visibles en temps réel. Si le RMSE dépasse le seuil, le job fail et le développeur reçoit une notification. Plus personne ne peut merger un modèle dégradé sans que l'équipe le sache."

---

## Workflow complet avec comparaison modèle précédent

```yaml
# .github/workflows/train-full.yml
name: ML Training Pipeline (Full)

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint and Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install linting tools
        run: pip install flake8 mypy black isort
      - name: Run Black (formatting check)
        run: black --check scripts/ tests/
      - name: Run Flake8 (linting)
        run: flake8 scripts/ tests/ --max-line-length=100
      - name: Run isort (import ordering)
        run: isort --check-only scripts/ tests/

  test-data:
    name: Data Quality Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Configure DVC
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          dvc remote modify myremote access_key_id $AWS_ACCESS_KEY_ID
          dvc remote modify myremote secret_access_key $AWS_SECRET_ACCESS_KEY
      - name: Pull data
        run: dvc pull
      - name: Run data tests
        run: pytest tests/test_data.py -v --junit-xml=reports/data-tests.xml
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: data-test-results
          path: reports/data-tests.xml

  train-and-evaluate:
    name: Train and Evaluate
    runs-on: ubuntu-latest
    needs: test-data
    outputs:
      model_rmse: ${{ steps.metrics.outputs.rmse }}
      model_r2: ${{ steps.metrics.outputs.r2 }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Configure DVC and MLflow
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          dvc remote modify myremote access_key_id $AWS_ACCESS_KEY_ID
          dvc remote modify myremote secret_access_key $AWS_SECRET_ACCESS_KEY

      - name: Pull data
        run: dvc pull

      - name: Run full pipeline
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          GIT_COMMIT: ${{ github.sha }}
          BRANCH_NAME: ${{ github.ref_name }}
        run: dvc repro --force

      - name: Push DVC outputs
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: dvc push

      - name: Extract metrics
        id: metrics
        run: |
          RMSE=$(python -c "import json; print(json.load(open('reports/evaluation.json'))['test_rmse'])")
          R2=$(python -c "import json; print(json.load(open('reports/evaluation.json'))['test_r2'])")
          echo "rmse=$RMSE" >> $GITHUB_OUTPUT
          echo "r2=$R2" >> $GITHUB_OUTPUT
          echo "RMSE: $RMSE, R²: $R2"

      - name: Compare with production model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python scripts/compare_with_production.py \
            --new-rmse ${{ steps.metrics.outputs.rmse }} \
            --fail-on-regression

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: model-${{ github.sha }}
          path: |
            models/
            reports/
            dvc.lock
          retention-days: 90

      - name: Run model tests
        run: pytest tests/test_model.py -v

  report:
    name: Generate Report
    runs-on: ubuntu-latest
    needs: train-and-evaluate
    if: always()
    steps:
      - uses: actions/checkout@v4
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: model-${{ github.sha }}

      - name: Generate HTML report
        run: |
          python scripts/generate_report.py

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: training-report-${{ github.sha }}
          path: reports/report.html
```

---

## Tests de données et de modèle

```python
# tests/test_data.py
import pytest
import pandas as pd
import numpy as np
import os

@pytest.fixture
def train_data():
    """Charger les données d'entraînement."""
    return pd.read_csv("data/processed/train.csv")

@pytest.fixture
def test_data():
    """Charger les données de test."""
    return pd.read_csv("data/processed/test.csv")

class TestDataQuality:
    """Tests de qualité des données."""

    def test_no_missing_values(self, train_data):
        """Aucune valeur manquante."""
        missing = train_data.isnull().sum()
        assert missing.sum() == 0, f"Valeurs manquantes trouvées:\n{missing[missing > 0]}"

    def test_expected_columns(self, train_data):
        """Les colonnes attendues sont présentes."""
        expected_cols = [
            "MedInc", "HouseAge", "AveRooms", "AveBedrms",
            "Population", "AveOccup", "Latitude", "Longitude", "target"
        ]
        for col in expected_cols:
            assert col in train_data.columns, f"Colonne manquante: {col}"

    def test_target_range(self, train_data):
        """La cible est dans une plage réaliste."""
        assert train_data["target"].min() > 0, "Prix négatif détecté"
        assert train_data["target"].max() < 20, "Prix anormalement élevé"

    def test_no_duplicates(self, train_data):
        """Aucune ligne dupliquée."""
        dupes = train_data.duplicated().sum()
        assert dupes == 0, f"{dupes} doublons trouvés"

    def test_train_test_no_overlap(self, train_data, test_data):
        """Pas de fuite entre train et test."""
        train_hashes = set(pd.util.hash_pandas_object(train_data).values)
        test_hashes = set(pd.util.hash_pandas_object(test_data).values)
        overlap = train_hashes.intersection(test_hashes)
        assert len(overlap) == 0, f"{len(overlap)} lignes en commun entre train et test"

    def test_minimum_samples(self, train_data, test_data):
        """Assez de données pour un entraînement fiable."""
        assert len(train_data) >= 1000, f"Trop peu d'exemples train: {len(train_data)}"
        assert len(test_data) >= 200, f"Trop peu d'exemples test: {len(test_data)}"
```

```python
# tests/test_model.py
import pytest
import pickle
import pandas as pd
import numpy as np
import os
import time

@pytest.fixture
def model():
    """Charger le modèle entraîné."""
    with open("models/model.pkl", "rb") as f:
        return pickle.load(f)

@pytest.fixture
def sample_data():
    """Données de sample pour les tests."""
    return pd.DataFrame({
        "MedInc": [8.3252, 4.1521],
        "HouseAge": [41.0, 22.0],
        "AveRooms": [6.984, 5.963],
        "AveBedrms": [1.024, 1.040],
        "Population": [322.0, 2401.0],
        "AveOccup": [2.556, 2.110],
        "Latitude": [37.88, 37.86],
        "Longitude": [-122.23, -122.22]
    })

class TestModel:
    """Tests du modèle entraîné."""

    def test_model_exists(self):
        """Le modèle existe."""
        assert os.path.exists("models/model.pkl")

    def test_prediction_shape(self, model, sample_data):
        """Les prédictions ont la bonne forme."""
        preds = model.predict(sample_data)
        assert preds.shape == (2,)

    def test_prediction_range(self, model, sample_data):
        """Les prédictions sont dans une plage réaliste."""
        preds = model.predict(sample_data)
        assert all(preds > 0), "Prédictions négatives"
        assert all(preds < 20), "Prédictions anormalement élevées"

    def test_prediction_latency(self, model, sample_data):
        """Latence de prédiction acceptable (< 100ms pour 1 prédiction)."""
        single_row = sample_data.iloc[:1]
        start = time.time()
        for _ in range(100):
            model.predict(single_row)
        avg_ms = (time.time() - start) / 100 * 1000
        assert avg_ms < 100, f"Latence trop élevée: {avg_ms:.1f}ms"

    def test_metrics_threshold(self):
        """Les métriques dépassent le seuil minimum."""
        import json
        with open("reports/evaluation.json") as f:
            metrics = json.load(f)

        assert metrics["test_rmse"] < 45.0, f"RMSE trop élevé: {metrics['test_rmse']}"
        assert metrics["test_r2"] > 0.80, f"R² trop faible: {metrics['test_r2']}"
```

---

## Comparer avec le modèle en production

```python
# scripts/compare_with_production.py
"""Compare le nouveau modèle avec celui en production."""
import argparse
import sys
import mlflow
import os

def compare_with_production(new_rmse: float, fail_on_regression: bool = True):
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    client = mlflow.tracking.MlflowClient()

    # Récupérer le modèle en production
    try:
        prod_versions = client.get_latest_versions(
            "prix-immobilier-rf", stages=["Production"]
        )

        if not prod_versions:
            print("Aucun modèle en production. Le nouveau modèle peut être déployé.")
            return True

        prod_run = client.get_run(prod_versions[0].run_id)
        prod_rmse = prod_run.data.metrics.get("rmse", float("inf"))

        improvement = (prod_rmse - new_rmse) / prod_rmse * 100

        print(f"RMSE Production : {prod_rmse:.4f}")
        print(f"RMSE Nouveau    : {new_rmse:.4f}")
        print(f"Amélioration    : {improvement:+.2f}%")

        if new_rmse > prod_rmse:
            msg = f"RÉGRESSION : nouveau RMSE ({new_rmse:.4f}) > prod RMSE ({prod_rmse:.4f})"
            print(f"ERREUR : {msg}")
            if fail_on_regression:
                sys.exit(1)
            return False

        print(f"OK : amélioration de {improvement:.2f}%")
        return True

    except Exception as e:
        print(f"Impossible de comparer avec la production : {e}")
        return True  # En cas d'erreur, ne pas bloquer le pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-rmse", type=float, required=True)
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()

    compare_with_production(args.new_rmse, args.fail_on_regression)
```

---

## Configurer les secrets GitHub

```bash
# Secrets à ajouter dans GitHub → Settings → Secrets → Actions
MLFLOW_TRACKING_URI          # ex: http://mlflow.mon-domaine.com:5000
AWS_ACCESS_KEY_ID            # Credentials AWS pour DVC
AWS_SECRET_ACCESS_KEY        # Credentials AWS pour DVC
DOCKER_REGISTRY_URL          # ex: ghcr.io ou registry.hub.docker.com
DOCKER_REGISTRY_USERNAME     # Identifiant registry Docker
DOCKER_REGISTRY_PASSWORD     # Mot de passe / token
```

```yaml
# Utilisation dans le workflow
env:
  MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}

steps:
  - name: Configure AWS
    uses: aws-actions/configure-aws-credentials@v4
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: eu-west-1
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page des secrets GitHub (Settings → Secrets → Actions) montrant les secrets configurés (sans leurs valeurs), puis la page d'un workflow qui utilise ces secrets avec le résultat des étapes.
> **Expliquer :** "Les secrets sont chiffrés par GitHub et ne sont jamais visibles dans les logs. Remarquez qu'on ne voit que les noms, jamais les valeurs. C'est la bonne façon de gérer les credentials dans le CI — jamais de clés en dur dans le code."

---

## Déclencher le workflow manuellement avec des paramètres

```yaml
on:
  workflow_dispatch:
    inputs:
      n_estimators:
        description: 'Nombre d'estimateurs (Random Forest)'
        required: false
        default: '100'
        type: string
      model_type:
        description: 'Type de modèle'
        required: false
        default: 'random_forest'
        type: choice
        options:
          - random_forest
          - gradient_boosting
      deploy_to_production:
        description: 'Déployer en production si meilleur ?'
        required: false
        default: false
        type: boolean

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Override params
        run: |
          # Modifier params.yaml avec les inputs du workflow
          python -c "
          import yaml
          with open('params.yaml') as f:
              params = yaml.safe_load(f)
          params['train']['n_estimators'] = int('${{ inputs.n_estimators }}')
          params['train']['model_type'] = '${{ inputs.model_type }}'
          with open('params.yaml', 'w') as f:
              yaml.dump(params, f)
          "
      - name: Train with custom params
        run: dvc repro --force
```
