# MLflow — Tracking d'expériences

## Pourquoi tracker ses expériences ?

Imaginez que vous entraînez 50 modèles différents sur deux semaines : différents algorithmes, différents hyperparamètres, différents ensembles de features. Sans système de tracking, vous vous retrouvez avec :

```
results_final.csv
results_final_v2.csv
results_VRAIMENT_final.csv
results_pour_de_bon.csv
best_model_jan_28.pkl
best_model_feb_3_GOOD.pkl
```

MLflow résout ce problème en centralisant **toutes les informations** de chaque entraînement dans une interface structurée et consultable.

---

## Architecture MLflow

MLflow est composé de **4 composants** principaux :

```
┌─────────────────────────────────────────────────────────────┐
│                        MLFLOW                               │
├──────────────┬──────────────┬───────────────┬───────────────┤
│   Tracking   │   Projects   │    Models     │    Registry   │
│              │              │               │               │
│ Logs params  │ Reproductibil│ Format        │ Cycle de vie  │
│ métriques    │ ité projets  │ universel     │ des modèles   │
│ artefacts    │ ML           │ déploiement   │               │
└──────────────┴──────────────┴───────────────┴───────────────┘
```

Dans ce cours, nous nous concentrons sur **Tracking** (ce fichier), **Models** et **Registry** (fichiers suivants).

---

## Installation et démarrage

```bash
pip install mlflow scikit-learn pandas numpy matplotlib

# Démarrer le serveur MLflow localement
mlflow ui

# Ou avec un port et host spécifiques
mlflow ui --host 0.0.0.0 --port 5000

# Avec un backend de stockage PostgreSQL (production)
mlflow server \
  --backend-store-uri postgresql://user:password@localhost/mlflow \
  --default-artifact-root s3://mon-bucket/mlflow-artifacts \
  --host 0.0.0.0 \
  --port 5000
```

Ouvrir `http://localhost:5000` dans le navigateur.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface MLflow vide au démarrage (`http://localhost:5000`), puis après avoir lancé quelques runs, l'affichage de la liste d'expériences avec les colonnes de métriques.
> **Expliquer :** "C'est l'interface centrale de MLflow. Chaque ligne représente un entraînement. On peut comparer, filtrer, trier. C'est notre 'journal de bord' automatique de toutes nos expériences."

---

## Concepts clés

### Experiment (Expérience)
Un groupe logique de runs liés au même projet ou problème.

```python
import mlflow

# Créer ou récupérer une expérience
mlflow.set_experiment("prediction-prix-immobilier")

# L'expérience est identifiée par un nom unique
# MLflow crée automatiquement une expérience "Default" si aucune n'est définie
```

### Run (Exécution)
Une instance unique d'entraînement dans une expérience.

```python
with mlflow.start_run(run_name="random_forest_v1"):
    # Tout ce qui est logué ici est associé à ce run
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("rmse", 45.3)
```

### Params, Metrics, Artifacts

| Type | Description | Exemple |
|---|---|---|
| **Params** | Hyperparamètres fixes | `n_estimators=100` |
| **Metrics** | Valeurs numériques (peuvent évoluer) | `rmse=45.3` |
| **Artifacts** | Fichiers binaires | modèle, graphiques, données |
| **Tags** | Métadonnées libres | `author`, `dataset_version` |

---

## Premier exemple complet

```python
# train.py
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.datasets import fetch_california_housing
import matplotlib.pyplot as plt

# ── 1. Charger les données ──────────────────────────────────────
housing = fetch_california_housing()
X = pd.DataFrame(housing.data, columns=housing.feature_names)
y = pd.Series(housing.target, name="price")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── 2. Configurer MLflow ────────────────────────────────────────
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("prediction-prix-immobilier")

# ── 3. Entraîner et logger ──────────────────────────────────────
with mlflow.start_run(run_name="random_forest_baseline"):

    # Hyperparamètres
    n_estimators = 100
    max_depth = 10
    min_samples_split = 5

    # Logger les paramètres AVANT l'entraînement
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    mlflow.log_param("min_samples_split", min_samples_split)
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("random_state", 42)

    # Entraîner le modèle
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Prédictions et métriques
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Logger les métriques
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("r2", r2)

    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R²:   {r2:.4f}")

    # ── 4. Sauvegarder des artefacts ────────────────────────────
    # Graphique importance des features
    fig, ax = plt.subplots(figsize=(10, 6))
    importances = pd.Series(
        model.feature_importances_,
        index=housing.feature_names
    ).sort_values(ascending=True)
    importances.plot(kind="barh", ax=ax)
    ax.set_title("Importance des features")
    plt.tight_layout()
    plt.savefig("feature_importance.png", dpi=100)
    mlflow.log_artifact("feature_importance.png")
    plt.close()

    # Graphique prédictions vs réalité
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(y_test, y_pred, alpha=0.3)
    ax.plot([y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()], 'r--')
    ax.set_xlabel("Valeur réelle")
    ax.set_ylabel("Valeur prédite")
    ax.set_title("Prédictions vs Réalité")
    plt.tight_layout()
    plt.savefig("predictions_vs_reality.png", dpi=100)
    mlflow.log_artifact("predictions_vs_reality.png")
    plt.close()

    # ── 5. Logger le modèle ─────────────────────────────────────
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="prix-immobilier-rf"  # Enregistre dans le registry
    )

    # Ajouter des tags
    mlflow.set_tag("author", "data_scientist_1")
    mlflow.set_tag("dataset", "california_housing")
    mlflow.set_tag("framework", "scikit-learn")

    print(f"\nRun ID: {mlflow.active_run().info.run_id}")
```

---

## Logger des métriques évolutives

Les métriques peuvent être loggées à chaque étape (epoch) pour suivre la progression :

```python
import mlflow
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

with mlflow.start_run(run_name="gradient_boosting_progressive"):

    mlflow.log_param("n_estimators", 200)
    mlflow.log_param("learning_rate", 0.05)

    # Simuler l'évolution des métriques par étape
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        warm_start=True  # Permet d'ajouter des arbres progressivement
    )

    for n in range(10, 210, 10):  # 10, 20, 30... 200 estimateurs
        model.n_estimators = n
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        # Step = numéro de l'itération
        mlflow.log_metric("rmse", rmse, step=n)

    # Métrique finale
    y_pred_final = model.predict(X_test)
    mlflow.log_metric("final_rmse", np.sqrt(mean_squared_error(y_test, y_pred_final)))
    mlflow.sklearn.log_model(model, "model")
```

---

## Logger des paramètres en masse

```python
# Au lieu de logger param par param, utiliser log_params
hyperparams = {
    "n_estimators": 150,
    "max_depth": 8,
    "min_samples_split": 4,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "bootstrap": True
}

with mlflow.start_run():
    # Logger tous les params d'un coup
    mlflow.log_params(hyperparams)

    # Logger plusieurs métriques d'un coup
    metrics = {
        "train_rmse": 32.1,
        "test_rmse": 38.7,
        "train_r2": 0.92,
        "test_r2": 0.88
    }
    mlflow.log_metrics(metrics)
```

---

## Logger des artefacts avancés

```python
import os
import json
import pickle

with mlflow.start_run():

    # ── Logger un fichier JSON (configuration) ──────────────────
    config = {
        "preprocessing": {
            "scaler": "StandardScaler",
            "features_selected": ["MedInc", "HouseAge", "AveRooms"]
        },
        "model": {
            "type": "RandomForest",
            "params": {"n_estimators": 100}
        }
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    mlflow.log_artifact("config.json")

    # ── Logger un répertoire entier ─────────────────────────────
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/train_report.txt", "w") as f:
        f.write("Train RMSE: 32.1\nTrain R2: 0.92\n")
    with open("outputs/test_report.txt", "w") as f:
        f.write("Test RMSE: 38.7\nTest R2: 0.88\n")

    # Enregistre tout le répertoire comme artefact
    mlflow.log_artifacts("outputs", artifact_path="reports")

    # ── Logger un fichier texte directement ────────────────────
    mlflow.log_text(
        "Feature engineering: StandardScaler on numerical features",
        "notes.txt"
    )

    # ── Logger un dictionnaire comme JSON ──────────────────────
    mlflow.log_dict(
        {"accuracy": 0.88, "threshold_used": 0.5},
        "evaluation_config.json"
    )

    # ── Logger une image matplotlib ─────────────────────────────
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    mlflow.log_figure(fig, "courbe_apprentissage.png")
    plt.close()
```

---

## Auto-logging

MLflow peut logger automatiquement tous les paramètres et métriques d'un framework :

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Activer l'auto-logging scikit-learn
mlflow.sklearn.autolog()

# À partir de là, TOUT est loggé automatiquement
with mlflow.start_run():
    model = RandomForestRegressor(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)
    # MLflow a automatiquement loggé :
    # - Tous les hyperparamètres
    # - Les métriques de validation
    # - Le modèle lui-même
    # - La signature du modèle
```

**Auto-logging disponible pour :**
- `mlflow.sklearn.autolog()`
- `mlflow.xgboost.autolog()`
- `mlflow.lightgbm.autolog()`
- `mlflow.tensorflow.autolog()`
- `mlflow.pytorch.autolog()`
- `mlflow.keras.autolog()`

---

## Comparer des runs programmatiquement

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Récupérer une expérience par son nom
experiment = client.get_experiment_by_name("prediction-prix-immobilier")
experiment_id = experiment.experiment_id

# Lister tous les runs d'une expérience
runs = client.search_runs(
    experiment_ids=[experiment_id],
    filter_string="metrics.rmse < 40",  # Filtrer par métrique
    order_by=["metrics.rmse ASC"],       # Trier par RMSE
    max_results=10
)

print("Top 10 runs :")
for run in runs:
    print(f"  Run {run.info.run_id[:8]}... | "
          f"RMSE={run.data.metrics.get('rmse', 'N/A'):.3f} | "
          f"R2={run.data.metrics.get('r2', 'N/A'):.3f} | "
          f"n_estimators={run.data.params.get('n_estimators', 'N/A')}")

# Récupérer le meilleur run
best_run = runs[0]
print(f"\nMeilleur run : {best_run.info.run_id}")
print(f"RMSE : {best_run.data.metrics['rmse']:.4f}")
print(f"Params : {best_run.data.params}")
```

---

## Récupérer un modèle loggé

```python
import mlflow.sklearn

# Par run_id et chemin de l'artefact
run_id = "abc123def456"
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# Par URI de modèle enregistré (voir fichier model-registry.md)
model = mlflow.sklearn.load_model("models:/prix-immobilier-rf/Production")

# Utiliser le modèle
predictions = model.predict(X_test)
```

---

## Organiser ses expériences : bonnes pratiques

```python
# ── Structure recommandée ───────────────────────────────────────

# 1. Une expérience = un problème ML
mlflow.set_experiment("prediction-prix-immobilier")

# 2. Nommer les runs de façon descriptive
with mlflow.start_run(run_name="rf_100est_depth10_v2"):
    ...

# 3. Utiliser les tags pour les métadonnées importantes
mlflow.set_tags({
    "author": "guillaume",
    "dataset_version": "2024-01-15",
    "git_commit": "abc123",
    "feature_set": "v2_with_location",
    "env": "development"
})

# 4. Grouper avec des runs parents/enfants (nested runs)
with mlflow.start_run(run_name="grid_search_parent") as parent_run:
    for n_est in [50, 100, 200]:
        with mlflow.start_run(run_name=f"child_n_est_{n_est}", nested=True):
            mlflow.log_param("n_estimators", n_est)
            model = RandomForestRegressor(n_estimators=n_est)
            model.fit(X_train, y_train)
            rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
            mlflow.log_metric("rmse", rmse)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans l'UI MLflow, afficher la vue de comparaison de plusieurs runs côte à côte (bouton "Compare" après sélection de plusieurs runs), avec le graphique de comparaison des métriques et le tableau de paramètres.
> **Expliquer :** "Cette vue de comparaison est l'une des fonctionnalités les plus puissantes. En un coup d'oeil, on voit quel modèle performe mieux et pourquoi. Les graphiques de métriques en parallèle sont particulièrement utiles pour le tuning d'hyperparamètres."

---

## Signature de modèle et Input Example

La signature décrit les types d'entrée et de sortie du modèle — essentielle pour le déploiement :

```python
from mlflow.models.signature import infer_signature

with mlflow.start_run():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # Inférer automatiquement la signature depuis les données
    signature = infer_signature(X_train, predictions)

    # Fournir un exemple d'input (5 premières lignes)
    input_example = X_train.iloc[:5]

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        signature=signature,       # Schéma d'entrée/sortie
        input_example=input_example  # Exemple pour la documentation
    )
```

La signature générée ressemble à :
```
inputs:
  ['MedInc': double, 'HouseAge': double, 'AveRooms': double, ...]
outputs:
  [double]
```

---

## Résumé des méthodes de tracking

```python
# Params (string, pas de step)
mlflow.log_param("key", "value")
mlflow.log_params({"key1": "v1", "key2": "v2"})

# Metrics (numériques, avec step optionnel)
mlflow.log_metric("rmse", 45.3)
mlflow.log_metric("loss", 0.23, step=10)
mlflow.log_metrics({"rmse": 45.3, "mae": 31.2})

# Artefacts (fichiers)
mlflow.log_artifact("fichier.png")
mlflow.log_artifacts("dossier/")
mlflow.log_text("contenu texte", "fichier.txt")
mlflow.log_dict({"key": "val"}, "fichier.json")
mlflow.log_figure(fig, "graphique.png")

# Tags (métadonnées libres)
mlflow.set_tag("author", "alice")
mlflow.set_tags({"version": "2", "team": "data"})

# Modèles
mlflow.sklearn.log_model(model, "model")
mlflow.xgboost.log_model(model, "model")
mlflow.pytorch.log_model(model, "model")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La page de détail d'un run dans MLflow, montrant les onglets "Params", "Metrics", "Artifacts" et les graphiques de métriques temporelles.
> **Expliquer :** "Voici la fiche complète d'un entraînement. Tout est archivé : les paramètres utilisés, les métriques obtenues, les fichiers produits. Si quelqu'un me demande 'quel modèle était en production le 15 janvier ?', je peux retrouver la réponse exacte en quelques secondes."
