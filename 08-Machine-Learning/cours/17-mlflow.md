# Chapitre 17 : MLflow — Tracker, Reproduire et Déployer vos Modèles

> **Scénario métier :** Votre équipe Data a testé 47 combinaisons de modèles en 2 semaines. Le manager demande : *"Quel modèle a les meilleurs résultats ? Avec quels paramètres ? On peut le remettre en production ?"*. Personne ne sait. MLflow empêche ce cauchemar.

---

## Objectifs

- Comprendre **pourquoi** le tracking d'expériences est indispensable en ML
- Installer et configurer **MLflow** (local et distant)
- Maîtriser le **Tracking** : paramètres, métriques, artefacts, tags
- Utiliser l'**autolog** pour tracker automatiquement vos expériences
- Comparer des expériences via l'**interface web MLflow UI**
- Gérer le cycle de vie d'un modèle avec le **Model Registry**
- Servir un modèle en production via **MLflow Models**
- Intégrer MLflow dans un **projet d'équipe** avec un serveur distant

> **Phase 6 - Semaine 17** | Durée estimée : 4h | Niveau : Avancé

---

## 1. Le problème : la jungle des expériences

### 1.1 Sans tracking, c'est le chaos

Tout le monde a vécu ça :

```
Mon bureau de Data Scientist (sans MLflow) :

notebook_v1.ipynb
notebook_v2.ipynb
notebook_v2_final.ipynb
notebook_v2_final_VRAIEMENT_final.ipynb
notebook_v3_adam_lr001.ipynb
notebook_v3_adam_lr001_dropout05.ipynb
notebook_BEST_MODEL_NE_PAS_TOUCHER.ipynb

→ 47 fichiers. Lequel est le bon ?
→ Quels paramètres pour chaque expérience ?
→ Quelles métriques exactement ?
→ Quel preprocessing a été appliqué ?
→ Impossible de reproduire le modèle de la semaine dernière.
```

### 1.2 Ce que MLflow résout

```
┌────────────────────────────────────────────────────────────────┐
│                    MLflow — Vue d'ensemble                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   TRACKING    │  │   MODELS     │  │   MODEL REGISTRY     │  │
│  │              │  │              │  │                      │  │
│  │  Paramètres  │  │  Packaging   │  │  Versioning          │  │
│  │  Métriques   │  │  Flavors     │  │  Staging → Prod      │  │
│  │  Artefacts   │  │  Serving     │  │  Approbation         │  │
│  │  Code source │  │  Signatures  │  │  Rollback            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐                                                │
│  │   PROJECTS    │  → Reproductibilité du code                   │
│  │  MLproject    │  → Packaging des expériences                  │
│  │  conda.yaml   │  → Exécution reproductible                    │
│  └──────────────┘                                                │
└────────────────────────────────────────────────────────────────┘
```

Les **4 composants** de MLflow :

| Composant | Rôle | Analogie |
|-----------|------|----------|
| **Tracking** | Enregistrer chaque expérience (params, métriques, artefacts) | Le cahier de labo du chercheur |
| **Models** | Packager un modèle dans un format standard | La boîte normalisée pour expédier |
| **Model Registry** | Gérer les versions et le cycle de vie | Le catalogue de la bibliothèque |
| **Projects** | Rendre le code reproductible | La recette de cuisine complète |

---

## 2. Installation et configuration

### 2.1 Installation

```bash
# Installation de base
pip install mlflow

# Avec les extras pour le serving
pip install mlflow[extras]

# Vérifier l'installation
mlflow --version
```

### 2.2 Les modes de stockage

MLflow peut stocker les données de tracking de 3 façons :

```
Mode 1 : LOCAL (développement solo)
┌─────────────────────────┐
│  Votre machine           │
│  ┌───────────────────┐  │
│  │  ./mlruns/         │  │  ← Dossier local créé automatiquement
│  │  ├── experiment_0/ │  │
│  │  │   ├── run_abc/  │  │
│  │  │   └── run_def/  │  │
│  │  └── experiment_1/ │  │
│  └───────────────────┘  │
└─────────────────────────┘

Mode 2 : SQLite (développement solo, plus robuste)
┌─────────────────────────┐
│  Votre machine           │
│  ┌───────────────────┐  │
│  │  mlflow.db (SQLite)│  │  ← Base de données locale
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │  ./mlartifacts/    │  │  ← Artefacts sur disque
│  └───────────────────┘  │
└─────────────────────────┘

Mode 3 : SERVEUR DISTANT (équipe)
┌──────────────┐     ┌────────────────────────┐
│  Dev 1       │────▶│  Serveur MLflow         │
│  Dev 2       │────▶│  ┌──────────────────┐  │
│  Dev 3       │────▶│  │  PostgreSQL       │  │  ← Métriques/params
│              │     │  └──────────────────┘  │
│              │     │  ┌──────────────────┐  │
│              │     │  │  S3 / MinIO       │  │  ← Artefacts/modèles
│              │     │  └──────────────────┘  │
└──────────────┘     └────────────────────────┘
```

### 2.3 Configuration initiale

```python
import mlflow

# --- Mode 1 : Local (par défaut, rien à configurer) ---
# Les données sont dans ./mlruns/

# --- Mode 2 : SQLite (recommandé pour commencer) ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# --- Mode 3 : Serveur distant ---
mlflow.set_tracking_uri("http://mlflow-server:5000")
```

> 💡 **Conseil** : Commencez avec le mode SQLite. C'est un bon compromis entre simplicité et robustesse. Le mode fichier local peut poser des problèmes si vous avez beaucoup d'expériences.

---

## 3. Tracking — Le coeur de MLflow

### 3.1 Concepts fondamentaux

```
Experiment (= un projet / un objectif)
  │
  ├── Run 1 (= une tentative)
  │   ├── Parameters : {"n_estimators": 100, "max_depth": 5}
  │   ├── Metrics    : {"f1": 0.87, "accuracy": 0.91}
  │   ├── Artifacts  : model.pkl, confusion_matrix.png
  │   └── Tags       : {"developer": "Alice", "version": "v1"}
  │
  ├── Run 2
  │   ├── Parameters : {"n_estimators": 200, "max_depth": 10}
  │   ├── Metrics    : {"f1": 0.92, "accuracy": 0.94}
  │   ├── Artifacts  : model.pkl, confusion_matrix.png
  │   └── Tags       : {"developer": "Alice", "version": "v2"}
  │
  └── Run 3
      └── ...
```

| Concept | Description | Exemple |
|---------|-------------|---------|
| **Experiment** | Regroupe les runs d'un même objectif | "churn-prediction", "recommendation-engine" |
| **Run** | Une exécution unique d'entraînement | Un essai avec des hyperparamètres précis |
| **Parameter** | Valeur d'entrée (hyperparamètre, choix) | `n_estimators=100`, `model_type="xgboost"` |
| **Metric** | Valeur de sortie mesurée | `f1_score=0.92`, `training_time=45.2` |
| **Artifact** | Fichier produit par le run | Modèle sérialisé, graphique, dataset |
| **Tag** | Métadonnée libre (texte) | `developer=Alice`, `dataset_version=v3` |

### 3.2 Premier tracking manuel

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.datasets import load_breast_cancer
import numpy as np

# --- Configuration ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("breast-cancer-classification")

# --- Données ---
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# --- Run MLflow ---
with mlflow.start_run(run_name="random_forest_baseline"):

    # 1. Définir et logger les paramètres
    params = {
        "model_type": "RandomForest",
        "n_estimators": 100,
        "max_depth": 5,
        "random_state": 42,
        "test_size": 0.2,
    }
    mlflow.log_params(params)

    # 2. Entraîner le modèle
    model = RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        random_state=params["random_state"],
    )
    model.fit(X_train, y_train)

    # 3. Prédire et calculer les métriques
    y_pred = model.predict(X_test)

    metrics = {
        "f1_score": f1_score(y_test, y_pred),
        "accuracy": accuracy_score(y_test, y_pred),
    }
    mlflow.log_metrics(metrics)

    # 4. Logger le modèle comme artefact
    mlflow.sklearn.log_model(model, "model")

    # 5. Ajouter des tags
    mlflow.set_tag("developer", "Guillaume")
    mlflow.set_tag("stage", "experimentation")

    print(f"Run terminé — F1: {metrics['f1_score']:.4f}")
```

### 3.3 Logger des artefacts personnalisés

```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import json

with mlflow.start_run(run_name="rf_with_artifacts"):

    # ... (entraînement du modèle) ...

    # --- Artefact 1 : Matrice de confusion ---
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues")
    plt.title("Matrice de confusion — Random Forest")
    plt.savefig("confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()

    mlflow.log_artifact("confusion_matrix.png")

    # --- Artefact 2 : Rapport de classification ---
    report = classification_report(y_test, y_pred, output_dict=True)
    with open("classification_report.json", "w") as f:
        json.dump(report, f, indent=2)

    mlflow.log_artifact("classification_report.json")

    # --- Artefact 3 : Feature importances ---
    importances = dict(zip(data.feature_names, model.feature_importances_))
    importances_sorted = dict(
        sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    with open("feature_importances.json", "w") as f:
        json.dump(importances_sorted, f, indent=2)

    mlflow.log_artifact("feature_importances.json")
```

### 3.4 Logger des métriques au fil du temps (courbes)

MLflow permet de logger une métrique à **plusieurs étapes** (steps), ce qui crée une courbe dans l'UI :

```python
# Exemple : logger la loss à chaque epoch
for epoch in range(1, 51):
    train_loss = 1.0 / (epoch * 0.1 + 1)  # Simulation
    val_loss = 1.0 / (epoch * 0.08 + 1)

    mlflow.log_metric("train_loss", train_loss, step=epoch)
    mlflow.log_metric("val_loss", val_loss, step=epoch)
```

<!-- 🔴 SCREENSHOT : Courbe de loss dans MLflow UI montrant train_loss et val_loss qui décroissent au fil des epochs -->

---

## 4. Autolog — Le tracking sans effort

### 4.1 Le principe

Au lieu de logger manuellement chaque paramètre et métrique, **autolog** instrumente automatiquement les librairies ML populaires :

```python
import mlflow

# UNE SEULE LIGNE pour tout tracker automatiquement
mlflow.autolog()
```

### 4.2 Librairies supportées

| Librairie | Ce qui est loggé automatiquement |
|-----------|----------------------------------|
| **scikit-learn** | Paramètres du modèle, métriques (accuracy, F1...), modèle sérialisé |
| **XGBoost** | Paramètres, métriques à chaque itération, feature importance |
| **LightGBM** | Paramètres, métriques, feature importance, modèle |
| **PyTorch** | Paramètres, loss par epoch, gradients, modèle |
| **TensorFlow/Keras** | Paramètres, métriques par epoch, modèle sauvegardé |
| **Transformers (HuggingFace)** | Paramètres d'entraînement, métriques, checkpoints |

### 4.3 Exemple complet avec autolog

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer

# --- Activer l'autolog ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("breast-cancer-autolog")

mlflow.autolog()

# --- Données ---
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# --- Entraîner (tout est loggé automatiquement !) ---
model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
)

with mlflow.start_run(run_name="autolog_gradient_boosting"):
    model.fit(X_train, y_train)

    # Autolog a DÉJÀ loggé :
    # ✅ Tous les paramètres (n_estimators, max_depth, learning_rate...)
    # ✅ Les métriques (accuracy, F1, precision, recall)
    # ✅ Le modèle sérialisé
    # ✅ La signature du modèle (types d'entrée/sortie)

    # Vous pouvez ajouter des métriques supplémentaires
    mlflow.set_tag("use_case", "churn_prediction")
```

<!-- 🔴 SCREENSHOT : Vue MLflow UI d'un run autolog montrant les paramètres, métriques et artefacts automatiquement enregistrés -->

### 4.4 Autolog par librairie (plus fin)

```python
# Si vous voulez activer l'autolog uniquement pour certaines librairies :
mlflow.sklearn.autolog()          # Seulement scikit-learn
mlflow.xgboost.autolog()          # Seulement XGBoost
mlflow.tensorflow.autolog()       # Seulement TensorFlow

# Désactiver l'autolog
mlflow.autolog(disable=True)

# Autolog sans logger le modèle (plus rapide pour des tests rapides)
mlflow.autolog(log_models=False)
```

---

## 5. L'interface web MLflow UI

### 5.1 Lancer l'UI

```bash
# Lancer l'interface web (mode SQLite)
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# Ouvrir dans le navigateur : http://localhost:5000
```

<!-- 🔴 SCREENSHOT : Page d'accueil MLflow UI avec la liste des expériences dans le panneau gauche -->

### 5.2 Explorer les expériences

L'interface MLflow UI permet de :

```
┌──────────────────────────────────────────────────────────────────┐
│  MLflow UI — http://localhost:5000                                │
│                                                                    │
│  ┌────────────┐  ┌──────────────────────────────────────────┐    │
│  │ Experiments │  │  breast-cancer-classification             │    │
│  │             │  │                                          │    │
│  │ ▸ breast-  │  │  ┌──────┬──────┬──────┬────────┬──────┐ │    │
│  │   cancer   │  │  │ Run  │ F1   │ Acc  │ Params │ Date │ │    │
│  │ ▸ churn-   │  │  ├──────┼──────┼──────┼────────┼──────┤ │    │
│  │   predict  │  │  │ RF   │ 0.96 │ 0.95 │ n=100  │ 10/02│ │    │
│  │             │  │  │ GB   │ 0.97 │ 0.96 │ n=200  │ 10/02│ │    │
│  │             │  │  │ XGB  │ 0.98 │ 0.97 │ n=300  │ 11/02│ │    │
│  │             │  │  └──────┴──────┴──────┴────────┴──────┘ │    │
│  │             │  │                                          │    │
│  │             │  │  [Compare] [Delete] [Download CSV]       │    │
│  └────────────┘  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

<!-- 🔴 SCREENSHOT : Liste des runs dans une expérience, avec colonnes de métriques et paramètres -->

### 5.3 Comparer des runs

La fonctionnalité **Compare** est l'une des plus puissantes de MLflow :

1. Sélectionner 2+ runs dans la liste
2. Cliquer sur **Compare**
3. Voir côte à côte : paramètres, métriques, courbes

<!-- 🔴 SCREENSHOT : Vue de comparaison de 3 runs avec graphiques de métriques côte à côte (parallel coordinates ou bar chart) -->

### 5.4 Visualiser un run en détail

En cliquant sur un run, vous accédez à :

- **Parameters** : tous les hyperparamètres utilisés
- **Metrics** : toutes les métriques enregistrées (avec courbes si steps)
- **Artifacts** : fichiers générés (modèle, graphiques, rapports)
- **Tags** : métadonnées

<!-- 🔴 SCREENSHOT : Page de détail d'un run avec les onglets Parameters, Metrics, Artifacts, Tags -->

<!-- 🔴 SCREENSHOT : Vue Artifacts d'un run montrant le modèle sauvegardé, la matrice de confusion et le rapport -->

---

## 6. Comparaison systématique de modèles

### 6.1 Script de benchmark

Voici un pattern courant : tester plusieurs modèles et hyperparamètres de façon systématique.

```python
import mlflow
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# --- Configuration ---
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("benchmark-classifiers")

# --- Données ---
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# --- Modèles à tester ---
models = {
    "LogisticRegression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, random_state=42)),
    ]),
    "RandomForest_100": RandomForestClassifier(
        n_estimators=100, max_depth=5, random_state=42
    ),
    "RandomForest_200": RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=42
    ),
    "GradientBoosting": GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42
    ),
    "AdaBoost": AdaBoostClassifier(
        n_estimators=100, learning_rate=0.5, random_state=42
    ),
    "SVM_RBF": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC(kernel="rbf", probability=True, random_state=42)),
    ]),
}

# --- Benchmark ---
for name, model in models.items():
    with mlflow.start_run(run_name=name):

        # Logger le nom du modèle
        mlflow.set_tag("model_name", name)

        # Entraîner
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Métriques
        metrics = {
            "f1_score": f1_score(y_test, y_pred),
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
        }
        mlflow.log_metrics(metrics)

        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1")
        mlflow.log_metric("cv_f1_mean", cv_scores.mean())
        mlflow.log_metric("cv_f1_std", cv_scores.std())

        # Logger le modèle
        mlflow.sklearn.log_model(model, "model")

        print(f"{name:25s} — F1: {metrics['f1_score']:.4f}  "
              f"CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
```

### 6.2 Rechercher le meilleur run programmatiquement

```python
import mlflow

# --- Trouver le meilleur run ---
experiment = mlflow.get_experiment_by_name("benchmark-classifiers")

best_run = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.f1_score DESC"],
    max_results=1,
).iloc[0]

print(f"Meilleur modèle : {best_run['tags.model_name']}")
print(f"  F1 Score : {best_run['metrics.f1_score']:.4f}")
print(f"  Accuracy : {best_run['metrics.accuracy']:.4f}")
print(f"  Run ID   : {best_run['run_id']}")
```

### 6.3 Filtrer les runs avec des requêtes

```python
# Syntaxe de filtre MLflow (SQL-like)
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="metrics.f1_score > 0.95 AND metrics.cv_f1_std < 0.03",
    order_by=["metrics.f1_score DESC"],
)

print(f"{len(runs)} runs avec F1 > 0.95 et CV stable :")
for _, run in runs.iterrows():
    print(f"  {run['tags.model_name']:25s} F1={run['metrics.f1_score']:.4f}")
```

<!-- 🔴 SCREENSHOT : MLflow UI avec un filtre appliqué montrant seulement les runs avec F1 > 0.95 -->

---

## 7. Model Registry — Gérer le cycle de vie

### 7.1 Le problème

```
SANS Model Registry :                 AVEC Model Registry :

"Le modèle en prod,                   ┌──────────────────────┐
 c'est lequel ?"                      │  churn-model          │
                                      │                      │
"Le fichier model_v3_final            │  Version 1 → Archived│
 sur le serveur de Bob."              │  Version 2 → Staging │
                                      │  Version 3 → Production
"Et si on veut revenir               │                      │
 à la version d'avant ?"              │  → Rollback en 1 clic│
                                      └──────────────────────┘
"Euh..."
```

### 7.2 Enregistrer un modèle dans le Registry

```python
import mlflow
from mlflow import MlflowClient

# --- Méthode 1 : Enregistrer directement pendant un run ---
with mlflow.start_run(run_name="model_pour_registry"):
    # ... entraînement ...
    model.fit(X_train, y_train)

    # Enregistrer ET ajouter au Registry en une ligne
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="breast-cancer-classifier",
    )


# --- Méthode 2 : Enregistrer un run existant ---
best_run_id = best_run["run_id"]
model_uri = f"runs:/{best_run_id}/model"

mlflow.register_model(model_uri, "breast-cancer-classifier")
```

<!-- 🔴 SCREENSHOT : Page Model Registry dans MLflow UI montrant un modèle avec ses versions -->

### 7.3 Gérer les stages (cycle de vie)

MLflow utilise des **aliases** (anciennement "stages") pour marquer les versions :

```python
client = MlflowClient()

# --- Voir les versions du modèle ---
model_name = "breast-cancer-classifier"

for mv in client.search_model_versions(f"name='{model_name}'"):
    print(f"Version {mv.version} — Run: {mv.run_id} — Aliases: {mv.aliases}")


# --- Assigner des aliases ---
# Marquer la version 2 comme "champion" (production)
client.set_registered_model_alias(model_name, "champion", version=2)

# Marquer la version 3 comme "challenger" (staging/test)
client.set_registered_model_alias(model_name, "challenger", version=3)
```

```
Cycle de vie d'un modèle :

    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │          │      │          │      │          │
    │  Nouveau │─────▶│Challenger│─────▶│ Champion │
    │          │      │(staging) │      │  (prod)  │
    │          │      │          │      │          │
    └──────────┘      └────┬─────┘      └────┬─────┘
                           │                 │
                           │    Rollback     │
                           │◀────────────────│
                           │                 │
                      ┌────▼─────┐           │
                      │ Archived │◀──────────┘
                      │          │   Remplacé par
                      └──────────┘   nouvelle version
```

### 7.4 Charger un modèle depuis le Registry

```python
import mlflow

# --- Charger par alias (recommandé) ---
model_prod = mlflow.sklearn.load_model(f"models:/{model_name}@champion")

# --- Charger par version ---
model_v2 = mlflow.sklearn.load_model(f"models:/{model_name}/2")

# --- Prédire ---
predictions = model_prod.predict(X_test)
print(f"Prédictions du modèle champion : {predictions[:5]}")
```

### 7.5 Ajouter une description

```python
# Description du modèle
client.update_registered_model(
    name=model_name,
    description="Classificateur de cancer du sein. Utilisé en production "
    "par l'équipe diagnostic. Seuil de décision : 0.5.",
)

# Description d'une version
client.update_model_version(
    name=model_name,
    version=2,
    description="GradientBoosting, n_estimators=200, F1=0.97. "
    "Entraîné sur le dataset v3 (10 000 samples).",
)
```

<!-- 🔴 SCREENSHOT : Détail d'une version de modèle dans le Registry avec description, alias et métadonnées -->

---

## 8. MLflow Models — Servir un modèle

### 8.1 Les "flavors" (formats)

MLflow sauvegarde les modèles dans un format standardisé qui supporte plusieurs "flavors" :

```
Modèle MLflow sauvegardé :

model/
├── MLmodel              ← Métadonnées (flavors disponibles)
├── model.pkl            ← Le modèle sérialisé
├── conda.yaml           ← Dépendances Conda
├── python_env.yaml      ← Dépendances Python
├── requirements.txt     ← Dépendances pip
└── input_example.json   ← Exemple d'entrée (optionnel)
```

| Flavor | Librairie | Format |
|--------|-----------|--------|
| `mlflow.sklearn` | scikit-learn | pickle / joblib |
| `mlflow.xgboost` | XGBoost | JSON / pickle |
| `mlflow.pytorch` | PyTorch | state_dict |
| `mlflow.tensorflow` | TensorFlow | SavedModel |
| `mlflow.transformers` | HuggingFace | pipeline |
| `mlflow.pyfunc` | Universel | Wrapper Python personnalisé |

### 8.2 Signatures de modèle

La **signature** décrit les types d'entrée et de sortie du modèle :

```python
from mlflow.models import infer_signature

with mlflow.start_run(run_name="model_with_signature"):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Inférer la signature automatiquement
    signature = infer_signature(X_test, y_pred)

    # Logger avec la signature
    mlflow.sklearn.log_model(
        model,
        "model",
        signature=signature,
        input_example=X_test[:3],  # Exemple d'entrée
    )
```

<!-- 🔴 SCREENSHOT : Onglet Artifacts d'un run montrant le fichier MLmodel avec la signature (input/output schema) -->

### 8.3 Servir un modèle comme API REST

```bash
# Servir le modèle champion directement
mlflow models serve \
  --model-uri "models:/breast-cancer-classifier@champion" \
  --port 5001 \
  --no-conda

# Tester l'API
curl -X POST http://localhost:5001/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [[17.99, 10.38, 122.8, 1001.0, 0.1184, 0.2776, 0.3001,
                 0.1471, 0.2419, 0.07871, 1.095, 0.9053, 8.589, 153.4,
                 0.006399, 0.04904, 0.05373, 0.01587, 0.03003, 0.006193,
                 25.38, 17.33, 184.6, 2019.0, 0.1622, 0.6656, 0.7119,
                 0.2654, 0.4601, 0.1189]]
  }'
```

<!-- 🔴 SCREENSHOT : Terminal montrant le lancement du serving MLflow et la réponse de l'API curl -->

### 8.4 Créer un modèle personnalisé (pyfunc)

Pour des cas plus complexes (preprocessing + modèle + postprocessing) :

```python
import mlflow.pyfunc
import pandas as pd
import numpy as np


class ChurnModel(mlflow.pyfunc.PythonModel):
    """Modèle personnalisé avec preprocessing intégré."""

    def load_context(self, context):
        """Chargé une seule fois au démarrage."""
        import joblib
        self.model = joblib.load(context.artifacts["model_path"])
        self.scaler = joblib.load(context.artifacts["scaler_path"])
        self.threshold = 0.5

    def predict(self, context, model_input: pd.DataFrame) -> np.ndarray:
        """Preprocessing + prédiction + seuil personnalisé."""
        # Preprocessing
        X_scaled = self.scaler.transform(model_input)

        # Prédiction avec probabilité
        probas = self.model.predict_proba(X_scaled)[:, 1]

        # Appliquer le seuil
        predictions = (probas >= self.threshold).astype(int)
        return predictions


# --- Enregistrer le modèle personnalisé ---
with mlflow.start_run(run_name="custom_pyfunc_model"):
    artifacts = {
        "model_path": "artefacts/model.joblib",
        "scaler_path": "artefacts/scaler.joblib",
    }

    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=ChurnModel(),
        artifacts=artifacts,
        registered_model_name="churn-model-custom",
    )
```

---

## 9. MLflow en équipe — Serveur distant

### 9.1 Architecture recommandée

```
┌──────────────┐        ┌────────────────────────────────┐
│              │        │     Serveur MLflow              │
│  Dev 1       │──┐     │                                │
│  (notebook)  │  │     │  ┌────────────────────┐        │
│              │  │     │  │  MLflow Server      │        │
├──────────────┤  ├────▶│  │  (port 5000)        │        │
│              │  │     │  └────────┬───────────┘        │
│  Dev 2       │──┤     │           │                    │
│  (VS Code)   │  │     │  ┌────────▼───────────┐        │
│              │  │     │  │  PostgreSQL         │        │
├──────────────┤  │     │  │  (métriques/params) │        │
│              │  │     │  └────────────────────┘        │
│  Dev 3       │──┘     │                                │
│  (script)    │        │  ┌────────────────────┐        │
│              │        │  │  MinIO / S3         │        │
└──────────────┘        │  │  (artefacts/modèles)│        │
                        │  └────────────────────┘        │
                        └────────────────────────────────┘
```

### 9.2 Lancer un serveur MLflow avec Docker Compose

```yaml
# docker-compose-mlflow.yml

services:
  # --- Base de données PostgreSQL ---
  postgres:
    image: postgres:15
    container_name: mlflow-postgres
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow_password
      POSTGRES_DB: mlflow_db
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # --- Stockage d'artefacts MinIO (S3 compatible) ---
  minio:
    image: minio/minio:latest
    container_name: mlflow-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"   # API S3
      - "9001:9001"   # Console web

  # --- Créer le bucket MLflow au démarrage ---
  minio-setup:
    image: minio/mc:latest
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      sleep 5;
      mc alias set myminio http://minio:9000 minioadmin minioadmin123;
      mc mb --ignore-existing myminio/mlflow-artifacts;
      exit 0;
      "

  # --- Serveur MLflow ---
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: mlflow-server
    depends_on:
      - postgres
      - minio
    environment:
      MLFLOW_BACKEND_STORE_URI: postgresql://mlflow:mlflow_password@postgres:5432/mlflow_db
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin123
    command: >
      mlflow server
        --backend-store-uri postgresql://mlflow:mlflow_password@postgres:5432/mlflow_db
        --artifacts-destination s3://mlflow-artifacts
        --host 0.0.0.0
        --port 5000
    ports:
      - "5000:5000"

volumes:
  postgres-data:
  minio-data:
```

```bash
# Lancer la stack
docker compose -f docker-compose-mlflow.yml up -d

# Vérifier
docker compose -f docker-compose-mlflow.yml ps

# Accéder aux services :
# MLflow UI   : http://localhost:5000
# MinIO Console : http://localhost:9001 (minioadmin / minioadmin123)
```

<!-- 🔴 SCREENSHOT : MLflow UI accessible via le serveur distant avec plusieurs expériences de différents développeurs -->

### 9.3 Se connecter au serveur depuis son code

```python
import os
import mlflow

# Configuration pour se connecter au serveur distant
mlflow.set_tracking_uri("http://mlflow-server:5000")

# Si MinIO / S3 est utilisé pour les artefacts
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin123"

# Maintenant, tout fonctionne comme en local
mlflow.set_experiment("mon-experiment")

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
```

---

## 10. Bonnes pratiques

### 10.1 Conventions de nommage

| Élément | Convention | Exemple |
|---------|-----------|---------|
| **Experiment** | kebab-case, descriptif | `churn-prediction-v2` |
| **Run name** | modèle + contexte | `xgb_lr01_depth5` |
| **Tags** | clé-valeur normalisées | `developer=alice`, `dataset=v3` |
| **Model Registry** | kebab-case, nom métier | `churn-classifier`, `fraud-detector` |

### 10.2 Structure de projet recommandée

```
mon-projet-ml/
├── src/
│   ├── train.py              ← Script d'entraînement avec MLflow
│   ├── evaluate.py           ← Évaluation + logging des métriques
│   ├── preprocessing.py      ← Feature engineering
│   └── config.py             ← Hyperparamètres centralisés
├── notebooks/
│   └── exploration.ipynb     ← EDA (pas de tracking ici)
├── docker-compose-mlflow.yml ← Stack MLflow pour l'équipe
├── MLproject                 ← (optionnel) Reproductibilité
├── conda.yaml                ← Environnement
└── pyproject.toml
```

### 10.3 Les erreurs courantes

| Erreur | Pourquoi c'est un problème | Solution |
|--------|---------------------------|----------|
| Ne pas logger le **preprocessing** | Impossible de reproduire les résultats | Logger le pipeline complet ou les transformations |
| Logger depuis un **notebook** seulement | Difficile à reproduire, pas versionnable | Extraire le code dans des scripts Python |
| **Trop de runs** sans organisation | Impossible de s'y retrouver | Utiliser des tags, des noms de run explicites |
| **Pas de signature** sur le modèle | Erreurs silencieuses en production | Toujours `infer_signature()` |
| Logger des **artefacts trop lourds** | Stockage saturé, lenteur | Logger uniquement ce qui est nécessaire |
| **Pas de seed** (random_state) | Résultats non reproductibles | Toujours fixer le seed et le logger |

### 10.4 Checklist avant de mettre un modèle en production

```
□ Le modèle est enregistré dans le Model Registry
□ La signature du modèle est définie (input/output)
□ Les métriques sont satisfaisantes sur le jeu de test
□ La cross-validation confirme la stabilité (faible écart-type)
□ Le preprocessing est inclus dans le pipeline (pas de fuite)
□ Les dépendances sont figées (requirements.txt ou conda.yaml)
□ Un input_example est fourni
□ La description du modèle est renseignée dans le Registry
□ L'alias "champion" est assigné à la bonne version
□ L'ancienne version est archivée (pas supprimée)
```

---

## 11. Exercice pratique guidé

### 11.1 Contexte

Vous travaillez sur un projet de prédiction de churn (désabonnement client). Vous devez comparer 3 modèles et mettre le meilleur en production via le Model Registry.

### 11.2 Étapes

**Étape 1 : Setup**
```bash
pip install mlflow scikit-learn xgboost pandas matplotlib
```

**Étape 2 : Créer le script de benchmark**

Créez un fichier `mlflow_exercice.py` qui :

1. Configure MLflow avec SQLite
2. Crée une expérience "churn-benchmark"
3. Entraîne et logge 3 modèles :
   - `RandomForestClassifier(n_estimators=200, max_depth=10)`
   - `GradientBoostingClassifier(n_estimators=200, learning_rate=0.1)`
   - `XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=5)`
4. Logge pour chaque modèle : paramètres, F1, accuracy, precision, recall, CV F1
5. Logge un artefact (matrice de confusion en PNG)

**Étape 3 : Explorer dans l'UI**
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

<!-- 🔴 SCREENSHOT : Résultat attendu dans MLflow UI avec les 3 runs du benchmark comparés -->

**Étape 4 : Enregistrer le meilleur modèle**

```python
# Trouver le meilleur run et l'enregistrer dans le Model Registry
best_run = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["metrics.f1_score DESC"],
    max_results=1,
).iloc[0]

mlflow.register_model(
    f"runs:/{best_run['run_id']}/model",
    "churn-classifier",
)

# Assigner l'alias "champion"
client = MlflowClient()
client.set_registered_model_alias("churn-classifier", "champion", version=1)
```

**Étape 5 : Charger et utiliser le modèle champion**

```python
model = mlflow.sklearn.load_model("models:/churn-classifier@champion")
predictions = model.predict(X_test)
```

---

## Points clés à retenir

1. **MLflow Tracking** enregistre chaque expérience : paramètres, métriques, artefacts — fini les notebooks perdus
2. **`mlflow.autolog()`** permet de tracker automatiquement la plupart des librairies ML en une ligne
3. L'**UI MLflow** (`mlflow ui`) permet de comparer visuellement les expériences et de trouver le meilleur modèle
4. Le **Model Registry** gère le cycle de vie : Nouveau → Challenger → Champion → Archived
5. Les **aliases** (`@champion`, `@challenger`) remplacent les anciens stages et permettent un rollback instantané
6. **MLflow Models** standardise le format de sauvegarde avec des signatures et des flavors
7. En équipe, un **serveur MLflow distant** (PostgreSQL + S3/MinIO) centralise toutes les expériences
8. Toujours logger la **signature** et un **input_example** pour les modèles en production
9. Utiliser des **tags** et des **noms de run explicites** pour garder les expériences organisées
10. Le **serving MLflow** (`mlflow models serve`) permet de déployer un modèle en API REST en une commande

---

## Checklist de validation

- [ ] Je sais installer et configurer MLflow (local et SQLite)
- [ ] Je sais créer une expérience et logger manuellement params, métriques et artefacts
- [ ] Je sais utiliser `mlflow.autolog()` pour tracker automatiquement
- [ ] Je sais lancer et naviguer dans l'UI MLflow
- [ ] Je sais comparer des runs et trouver le meilleur modèle
- [ ] Je sais utiliser `mlflow.search_runs()` pour chercher programmatiquement
- [ ] Je sais enregistrer un modèle dans le Model Registry
- [ ] Je comprends le cycle de vie : alias champion / challenger / archived
- [ ] Je sais charger un modèle depuis le Registry (`models:/name@alias`)
- [ ] Je comprends la notion de signature et de flavor
- [ ] Je sais servir un modèle en API REST avec `mlflow models serve`
- [ ] Je sais déployer un serveur MLflow distant avec Docker Compose

---

**Précédent** : [Chapitre 16 : Docker, Monitoring et MLOps](16-docker-monitoring.md)

**Suivant** : Projet final de la formation
