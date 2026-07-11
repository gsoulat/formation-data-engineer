# MLflow — Model Registry

## Qu'est-ce que le Model Registry ?

Le **Model Registry** est le composant de MLflow qui gère le **cycle de vie des modèles** en production. C'est un catalogue centralisé qui permet de :

- Versionner les modèles automatiquement (v1, v2, v3...)
- Associer un statut à chaque version (Staging, Production, Archived)
- Tracer qui a promu quel modèle et quand
- Annoter les modèles avec des descriptions et des tags
- Faciliter les transitions entre environnements

```
Entraînement (MLflow Run)
        │
        ▼
  Model Registry
        │
   ┌────┴────┐
   │ Version │
   │    1    │──── Archived (remplacé)
   └─────────┘
   ┌─────────┐
   │ Version │──── Staging (en test)
   │    2    │
   └─────────┘
   ┌─────────┐
   │ Version │──── Production (en ligne)
   │    3    │
   └─────────┘
```

---

## Enregistrer un modèle dans le registry

### Méthode 1 : Lors du log du modèle

```python
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("prediction-prix-immobilier")

with mlflow.start_run():
    model.fit(X_train, y_train)

    # Le paramètre registered_model_name crée automatiquement
    # une entrée dans le Model Registry
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="prix-immobilier-rf"
    )
```

### Méthode 2 : Enregistrer un run existant

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# À partir d'un run_id existant
run_id = "abc123def456"
model_uri = f"runs:/{run_id}/model"

# Enregistrer dans le registry
model_version = mlflow.register_model(
    model_uri=model_uri,
    name="prix-immobilier-rf"
)

print(f"Version créée : {model_version.version}")
print(f"Statut : {model_version.current_stage}")
```

---

## Gérer les stages du cycle de vie

Les stages disponibles sont :
- **None** : version fraîchement enregistrée (pas encore testée)
- **Staging** : en cours de validation / test
- **Production** : déployée et active
- **Archived** : obsolète, remplacée

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
model_name = "prix-immobilier-rf"

# ── Promouvoir une version en Staging ──────────────────────────
client.transition_model_version_stage(
    name=model_name,
    version=2,
    stage="Staging",
    archive_existing_versions=False  # Ne pas archiver les autres versions Staging
)

# ── Promouvoir en Production ────────────────────────────────────
client.transition_model_version_stage(
    name=model_name,
    version=2,
    stage="Production",
    archive_existing_versions=True  # Archiver l'ancienne version Production
)

# ── Archiver une version ────────────────────────────────────────
client.transition_model_version_stage(
    name=model_name,
    version=1,
    stage="Archived"
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface MLflow → onglet "Models", montrant la liste des modèles enregistrés, puis le détail d'un modèle avec ses différentes versions et leurs stages respectifs.
> **Expliquer :** "Regardez comment chaque version a un stage différent. La version 1 est archivée (elle était en prod avant), la version 2 est en staging (on la teste), la version 3 est en production. C'est notre source de vérité pour savoir ce qui tourne réellement."

---

## Ajouter des descriptions et des tags

```python
client = MlflowClient()

# ── Description du modèle (niveau global) ──────────────────────
client.update_registered_model(
    name="prix-immobilier-rf",
    description="""
    Modèle de prédiction du prix immobilier (Californie).
    Basé sur Random Forest. Entraîné sur California Housing Dataset.
    Features : revenus médians, âge maison, nb chambres, population, localisation.
    Métrique principale : RMSE en milliers de dollars.
    """
)

# ── Description d'une version spécifique ───────────────────────
client.update_model_version(
    name="prix-immobilier-rf",
    version=3,
    description="""
    Version 3 — Améliorations :
    - Ajout feature localisation (lat/lon clustering)
    - n_estimators augmenté à 200
    - RMSE amélioré de 5% vs v2 (38.7 → 36.8)
    - Validé sur données Jan 2024
    """
)

# ── Tags sur le modèle global ───────────────────────────────────
client.set_registered_model_tag(
    name="prix-immobilier-rf",
    key="team",
    value="data-science"
)

# ── Tags sur une version ────────────────────────────────────────
client.set_model_version_tag(
    name="prix-immobilier-rf",
    version=3,
    key="validated_by",
    value="alice"
)
client.set_model_version_tag(
    name="prix-immobilier-rf",
    version=3,
    key="validation_date",
    value="2024-01-20"
)
```

---

## Workflow de validation automatisé

Un pattern courant : valider automatiquement un modèle avant de le promouvoir.

```python
import mlflow
import numpy as np
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_squared_error

def validate_and_promote_model(
    model_name: str,
    candidate_version: int,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    rmse_threshold: float = 40.0
):
    """
    Valide un modèle en Staging et le promeut en Production
    s'il passe le seuil de performance.
    """
    client = MlflowClient()

    # ── 1. Charger le modèle candidat ──────────────────────────
    model_uri = f"models:/{model_name}/{candidate_version}"
    model = mlflow.sklearn.load_model(model_uri)

    # ── 2. Évaluer sur le jeu de validation ────────────────────
    y_pred = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))

    print(f"Modèle {model_name} v{candidate_version} — RMSE: {rmse:.3f}")

    # ── 3. Décision de promotion ────────────────────────────────
    if rmse <= rmse_threshold:
        print(f"RMSE ({rmse:.3f}) <= seuil ({rmse_threshold}) → Promotion en Production")

        # Promouvoir en production (archive l'ancienne version)
        client.transition_model_version_stage(
            name=model_name,
            version=candidate_version,
            stage="Production",
            archive_existing_versions=True
        )

        client.set_model_version_tag(
            name=model_name,
            version=candidate_version,
            key="validation_rmse",
            value=str(round(rmse, 4))
        )

        return True, rmse
    else:
        print(f"RMSE ({rmse:.3f}) > seuil ({rmse_threshold}) → Rejet, reste en Staging")

        client.set_model_version_tag(
            name=model_name,
            version=candidate_version,
            key="rejection_reason",
            value=f"RMSE {rmse:.3f} dépasse seuil {rmse_threshold}"
        )

        return False, rmse


# Utilisation
promoted, rmse = validate_and_promote_model(
    model_name="prix-immobilier-rf",
    candidate_version=3,
    X_val=X_test,
    y_val=y_test,
    rmse_threshold=40.0
)
```

---

## Comparer deux versions de modèle

```python
from mlflow.tracking import MlflowClient
import mlflow

client = MlflowClient()
model_name = "prix-immobilier-rf"

def compare_model_versions(model_name: str, version_a: int, version_b: int,
                            X_test, y_test):
    """Compare deux versions d'un modèle sur le même jeu de test."""
    results = {}

    for version in [version_a, version_b]:
        model = mlflow.sklearn.load_model(f"models:/{model_name}/{version}")
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Récupérer les infos du run associé
        model_version_info = client.get_model_version(model_name, str(version))
        run_id = model_version_info.run_id
        run = client.get_run(run_id)

        results[f"v{version}"] = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "stage": model_version_info.current_stage,
            "params": run.data.params,
            "run_id": run_id
        }

    # Afficher la comparaison
    print(f"\n{'='*60}")
    print(f"Comparaison {model_name} : v{version_a} vs v{version_b}")
    print(f"{'='*60}")
    for ver, info in results.items():
        print(f"\n{ver} (Stage: {info['stage']})")
        print(f"  RMSE  : {info['rmse']:.4f}")
        print(f"  MAE   : {info['mae']:.4f}")
        print(f"  R²    : {info['r2']:.4f}")
        print(f"  Params: {info['params']}")

    return results

compare_model_versions("prix-immobilier-rf", 2, 3, X_test, y_test)
```

---

## Charger un modèle depuis le registry en production

```python
import mlflow.sklearn

# ── Charger la version Production ──────────────────────────────
model_prod = mlflow.sklearn.load_model("models:/prix-immobilier-rf/Production")

# ── Charger une version spécifique ─────────────────────────────
model_v2 = mlflow.sklearn.load_model("models:/prix-immobilier-rf/2")

# ── Charger la version Staging ─────────────────────────────────
model_staging = mlflow.sklearn.load_model("models:/prix-immobilier-rf/Staging")

# ── Utiliser dans une API FastAPI ───────────────────────────────
from fastapi import FastAPI
from pydantic import BaseModel
import mlflow

app = FastAPI()

# Charger le modèle une seule fois au démarrage
MODEL = mlflow.sklearn.load_model("models:/prix-immobilier-rf/Production")

class HouseFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.post("/predict")
def predict(features: HouseFeatures):
    data = pd.DataFrame([features.dict()])
    prediction = MODEL.predict(data)
    return {"prix_predit": float(prediction[0])}
```

---

## Gérer les alias (MLflow 2.9+)

Les alias permettent de nommer une version de façon sémantique, indépendamment du stage :

```python
client = MlflowClient()

# Associer un alias à une version
client.set_registered_model_alias(
    name="prix-immobilier-rf",
    alias="champion",
    version=3
)

client.set_registered_model_alias(
    name="prix-immobilier-rf",
    alias="challenger",
    version=4
)

# Charger via l'alias
champion = mlflow.sklearn.load_model("models:/prix-immobilier-rf@champion")
challenger = mlflow.sklearn.load_model("models:/prix-immobilier-rf@challenger")

# A/B testing entre champion et challenger
def predict_with_ab_test(features, ratio_challenger=0.1):
    """Envoie 10% du trafic vers le challenger."""
    import random
    if random.random() < ratio_challenger:
        pred = challenger.predict(features)
        model_used = "challenger"
    else:
        pred = champion.predict(features)
        model_used = "champion"
    return pred, model_used
```

---

## Script complet : pipeline register → staging → production

```python
"""
pipeline_registry.py
Pipeline complet : entraîner → enregistrer → valider → déployer
"""
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature

# Configuration
TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME = "prediction-prix-immobilier"
MODEL_NAME = "prix-immobilier-rf"
RMSE_THRESHOLD = 40.0

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
client = MlflowClient()

# 1. Préparer les données
housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = pd.Series(housing.target)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Entraîner et enregistrer
print("Entraînement du modèle...")
with mlflow.start_run(run_name="rf_production_candidate") as run:
    params = {"n_estimators": 200, "max_depth": 12, "random_state": 42}
    mlflow.log_params(params)

    model = RandomForestRegressor(**params, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mlflow.log_metric("rmse", rmse)

    signature = infer_signature(X_train, model.predict(X_train))
    mlflow.sklearn.log_model(
        model, "model",
        signature=signature,
        registered_model_name=MODEL_NAME
    )

    run_id = run.info.run_id
    print(f"Run ID: {run_id}, RMSE: {rmse:.4f}")

# 3. Récupérer la version qui vient d'être créée
versions = client.search_model_versions(f"name='{MODEL_NAME}'")
latest_version = max(versions, key=lambda v: int(v.version))
version_num = latest_version.version
print(f"Version créée : {version_num}")

# 4. Mettre en Staging
client.transition_model_version_stage(MODEL_NAME, version_num, "Staging")
print(f"Version {version_num} → Staging")

# 5. Valider
model_staging = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/Staging")
y_pred_val = model_staging.predict(X_test)
rmse_val = np.sqrt(mean_squared_error(y_test, y_pred_val))
print(f"Validation RMSE : {rmse_val:.4f} (seuil : {RMSE_THRESHOLD})")

# 6. Promouvoir ou rejeter
if rmse_val <= RMSE_THRESHOLD:
    client.transition_model_version_stage(
        MODEL_NAME, version_num, "Production",
        archive_existing_versions=True
    )
    print(f"✓ Version {version_num} → Production")
else:
    print(f"✗ Version {version_num} rejetée (RMSE trop élevé)")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter le script ci-dessus et montrer dans l'UI MLflow le modèle passer de "None" → "Staging" → "Production", avec l'ancienne version archivée automatiquement.
> **Expliquer :** "Regardez comment la promotion est traçable : qui a fait la transition, quand, depuis quel run. Si on a un incident en production, on peut immédiatement identifier quelle version est déployée et revenir à la précédente."

---

## Résumé des opérations registry

```python
# Lister tous les modèles enregistrés
for rm in client.search_registered_models():
    print(rm.name)

# Lister les versions d'un modèle
for v in client.search_model_versions(f"name='prix-immobilier-rf'"):
    print(f"v{v.version} - {v.current_stage} - {v.run_id[:8]}")

# Récupérer la version en Production
prod_versions = client.get_latest_versions(
    "prix-immobilier-rf",
    stages=["Production"]
)

# Supprimer une version
client.delete_model_version("prix-immobilier-rf", "1")

# Supprimer un modèle entier (toutes versions)
client.delete_registered_model("prix-immobilier-rf")
```
