# Exercice 02 — Pipeline ML avec MLflow

## Objectif

Construire un pipeline de Machine Learning orchestré avec Airflow qui :
1. **Prépare** les données (feature engineering)
2. **Entraîne** un modèle scikit-learn
3. **Évalue** ses performances sur un jeu de test
4. **Enregistre** le modèle et les métriques dans MLflow
5. **Décide** de promouvoir ou non le modèle selon ses performances

Durée estimée : **2h à 2h30**

---

## Contexte métier

Vous travaillez pour une plateforme e-commerce. Votre équipe ML entraîne chaque semaine un modèle de prédiction du risque de churn client. Votre mission est d'automatiser ce pipeline hebdomadaire avec Airflow et de tracer tous les runs dans MLflow.

---

## Architecture du pipeline

```
PostgreSQL                    MLflow
(données clients)             (tracking)
    │                             │
    ▼                             │
[Extraction features]             │
    │                             │
    ▼                             │
[Feature engineering]             │
    │                             │
    ▼                             │
[Split train/test]                │
    │                             │
    ├──────────────────────────────
    ▼                             │
[Entraînement modèle]  ──► [Log params + métriques]
    │                             │
    ▼                             │
[Évaluation]  ──────────► [Log métriques test]
    │                             │
    ▼                        ┌────▼──────────┐
[Décision promotion]  ──────►│  Model Registry│
  (branchement)               │  (si OK)      │
    │                         └───────────────┘
    ├──► [Promouvoir]
    └──► [Alerter équipe]
```

---

## Mise en place

### Docker Compose avec MLflow

```yaml
# docker-compose.yml

version: '3'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.9.0
  environment:
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__CORE__FERNET_KEY: 'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
    MLFLOW_TRACKING_URI: http://mlflow:5000
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./data:/opt/airflow/data
  depends_on:
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_ml_db.sql:/docker-entrypoint-initdb.d/init_ml_db.sql
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    ports:
      - "5000:5000"
    command: >
      mlflow server
        --host 0.0.0.0
        --port 5000
        --backend-store-uri postgresql+psycopg2://airflow:airflow@postgres/airflow
        --default-artifact-root /mlartifacts
    volumes:
      - mlflow_artifacts:/mlartifacts
    depends_on:
      postgres:
        condition: service_healthy

  airflow-init:
    <<: *airflow-common
    command: >
      bash -c "
        airflow db init &&
        airflow users create --username admin --password admin
          --firstname Admin --lastname User --role Admin --email admin@example.com &&
        pip install scikit-learn pandas mlflow pyarrow
      "

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"

volumes:
  postgres_data:
  mlflow_artifacts:
```

### Données de simulation

```sql
-- init_ml_db.sql

CREATE SCHEMA IF NOT EXISTS churn;

-- Table clients avec features
CREATE TABLE IF NOT EXISTS churn.features_clients (
    client_id           INTEGER PRIMARY KEY,
    anciennete_jours    INTEGER,
    nb_achats_30j       INTEGER,
    nb_achats_90j       INTEGER,
    montant_total_30j   NUMERIC(10,2),
    montant_total_90j   NUMERIC(10,2),
    nb_visites_30j      INTEGER,
    taux_retour         NUMERIC(5,4),
    nb_tickets_support  INTEGER,
    score_satisfaction  NUMERIC(3,1),
    segment             VARCHAR(20),
    has_churned         BOOLEAN,     -- Cible : a-t-il churné ?
    date_maj            DATE DEFAULT CURRENT_DATE
);

-- Générer des données simulées (1000 clients)
INSERT INTO churn.features_clients
SELECT
    gs.id,
    (RANDOM() * 1825 + 30)::INTEGER,              -- anciennete 30-1855 jours
    (RANDOM() * 15)::INTEGER,                      -- achats 30j
    (RANDOM() * 45)::INTEGER,                      -- achats 90j
    (RANDOM() * 500)::NUMERIC(10,2),               -- montant 30j
    (RANDOM() * 1500)::NUMERIC(10,2),              -- montant 90j
    (RANDOM() * 30)::INTEGER,                      -- visites
    (RANDOM() * 0.3)::NUMERIC(5,4),               -- taux retour
    (RANDOM() * 5)::INTEGER,                       -- tickets support
    (RANDOM() * 4 + 1)::NUMERIC(3,1),             -- satisfaction 1-5
    (ARRAY['bronze', 'silver', 'gold', 'platinum'])[FLOOR(RANDOM()*4+1)::INTEGER],
    (RANDOM() < 0.2)                               -- ~20% ont churné
FROM generate_series(1, 1000) gs(id)
ON CONFLICT (client_id) DO NOTHING;
```

---

## Étapes de l'exercice

### Étape 1 : Extraction et préparation des features

```python
@task
def extraire_features(**context) -> str:
    """
    Extrait les features clients depuis PostgreSQL.
    Retourne le chemin du fichier parquet sauvegardé.
    """
    import pandas as pd
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    hook = PostgresHook('postgres_default')
    semaine = context['ds']

    df = hook.get_pandas_df("""
        SELECT
            client_id,
            anciennete_jours,
            nb_achats_30j,
            nb_achats_90j,
            montant_total_30j,
            montant_total_90j,
            nb_visites_30j,
            taux_retour,
            nb_tickets_support,
            score_satisfaction,
            segment,
            has_churned::INTEGER AS has_churned
        FROM churn.features_clients
        WHERE date_maj <= %(semaine)s
    """, parameters={'semaine': semaine})

    chemin = f'/opt/airflow/data/features_{context["ds_nodash"]}.parquet'
    df.to_parquet(chemin, index=False)

    print(f"Features extraites : {len(df)} clients, {len(df.columns)} features")
    print(f"Taux de churn : {df['has_churned'].mean():.1%}")
    return chemin
```

### Étape 2 : Feature engineering

```python
@task
def feature_engineering(chemin_features: str, **context) -> dict:
    """
    Crée des features dérivées et encode les variables catégorielles.
    Retourne les chemins des jeux train et test.
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder

    df = pd.read_parquet(chemin_features)

    # TODO :
    # 1. Créer des ratios features :
    #    - ratio_achats = nb_achats_30j / (nb_achats_90j + 1)
    #    - ratio_montant = montant_total_30j / (montant_total_90j + 1)
    #    - achats_par_visite = nb_achats_30j / (nb_visites_30j + 1)
    # 2. Encoder 'segment' avec LabelEncoder
    # 3. Remplir les valeurs manquantes avec la médiane
    # 4. Séparer X (features) et y (cible has_churned)
    # 5. Faire un train_test_split(test_size=0.2, random_state=42, stratify=y)
    # 6. Sauvegarder X_train, X_test, y_train, y_test en parquet
    # 7. Retourner un dict avec les chemins et les métriques du split
    pass
```

### Étape 3 : Entraînement avec MLflow

```python
@task
def entrainer_modele(split: dict, **context) -> dict:
    """
    Entraîne un Random Forest, log les params et métriques dans MLflow.
    """
    import pandas as pd
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score, roc_auc_score,
        classification_report, confusion_matrix
    )

    # Charger les données
    X_train = pd.read_parquet(split['X_train_path'])
    y_train = pd.read_parquet(split['y_train_path'])['has_churned']
    X_test = pd.read_parquet(split['X_test_path'])
    y_test = pd.read_parquet(split['y_test_path'])['has_churned']

    # Paramètres du modèle
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'random_state': 42,
        'class_weight': 'balanced',
    }

    # TODO :
    # 1. Configurer mlflow.set_tracking_uri depuis la variable d'env MLFLOW_TRACKING_URI
    # 2. mlflow.set_experiment("churn_prediction")
    # 3. with mlflow.start_run(run_name=f"rf_weekly_{context['ds']}") as run:
    #    a. mlflow.log_params(params)
    #    b. mlflow.log_param("n_train", len(X_train))
    #    c. mlflow.log_param("n_test", len(X_test))
    #    d. Entraîner RandomForestClassifier(**params)
    #    e. Prédire sur X_test
    #    f. Calculer et logger : accuracy, roc_auc, precision, recall
    #    g. mlflow.sklearn.log_model(model, "model")
    #    h. Retourner {'run_id': run.info.run_id, 'accuracy': ..., 'roc_auc': ...}
    pass
```

### Étape 4 : Décision de promotion

```python
@task.branch
def decider_promotion(metriques: dict) -> str:
    """
    Promeut le modèle si :
    - ROC-AUC >= 0.75
    - Accuracy >= 0.70
    Sinon, alerte l'équipe.
    """
    roc_auc = metriques.get('roc_auc', 0)
    accuracy = metriques.get('accuracy', 0)

    print(f"Métriques du modèle :")
    print(f"  ROC-AUC : {roc_auc:.4f} (seuil : 0.75)")
    print(f"  Accuracy : {accuracy:.4f} (seuil : 0.70)")

    if roc_auc >= 0.75 and accuracy >= 0.70:
        print("Décision : PROMOTION du modèle")
        return 'promouvoir_modele'
    else:
        print("Décision : modèle insuffisant — alerte équipe")
        return 'alerter_equipe'
```

### Étape 5 : Promotion dans le Model Registry

```python
@task
def promouvoir_modele(metriques: dict) -> str:
    """
    Enregistre le modèle dans le MLflow Model Registry
    et le passe en stage 'Staging'.
    """
    import mlflow
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    run_id = metriques['run_id']

    # TODO :
    # 1. Enregistrer le modèle :
    #    mlflow.register_model(f"runs:/{run_id}/model", "churn_prediction")
    # 2. Récupérer la dernière version
    # 3. Passer en stage 'Staging' :
    #    client.transition_model_version_stage(name, version, stage="Staging")
    # 4. Logger des tags et une description
    # 5. Retourner le nom du modèle et la version
    pass


@task
def alerter_equipe(metriques: dict) -> None:
    """
    Envoie une alerte quand le modèle ne passe pas les seuils.
    """
    print(f"""
ALERTE — Modèle churn insuffisant !

Run MLflow : {metriques.get('run_id')}
ROC-AUC    : {metriques.get('roc_auc', 'N/A'):.4f} (seuil requis : 0.75)
Accuracy   : {metriques.get('accuracy', 'N/A'):.4f} (seuil requis : 0.70)

Action requise : Revoir la préparation des features ou les hyperparamètres.
    """)
    # En production : envoyer un email ou Slack
```

---

## Solution complète

```python
# dags/pipeline_ml_churn_solution.py

import os
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.utils.trigger_rule import TriggerRule

SEUIL_ROC_AUC = 0.75
SEUIL_ACCURACY = 0.70
MLFLOW_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://mlflow:5000')

@dag(
    dag_id='pipeline_ml_churn_solution',
    start_date=datetime(2024, 1, 1),
    schedule='@weekly',
    catchup=False,
    default_args={'owner': 'ml-team', 'retries': 1, 'retry_delay': timedelta(minutes=10)},
    tags=['ml', 'churn', 'mlflow', 'solution'],
)
def pipeline_ml_churn_solution():

    @task
    def extraire_features(**context) -> str:
        import pandas as pd
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook('postgres_default')
        df = hook.get_pandas_df("""
            SELECT client_id, anciennete_jours, nb_achats_30j, nb_achats_90j,
                   montant_total_30j, montant_total_90j, nb_visites_30j,
                   taux_retour, nb_tickets_support, score_satisfaction,
                   segment, has_churned::INTEGER AS has_churned
            FROM churn.features_clients
        """)

        chemin = f'/opt/airflow/data/features_{context["ds_nodash"]}.parquet'
        os.makedirs('/opt/airflow/data', exist_ok=True)
        df.to_parquet(chemin, index=False)
        print(f"Extrait : {len(df)} clients | Taux churn : {df['has_churned'].mean():.1%}")
        return chemin

    @task
    def feature_engineering(chemin: str, **context) -> dict:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder

        df = pd.read_parquet(chemin)
        date = context['ds_nodash']

        # Features dérivées
        df['ratio_achats'] = df['nb_achats_30j'] / (df['nb_achats_90j'] + 1)
        df['ratio_montant'] = df['montant_total_30j'] / (df['montant_total_90j'] + 1)
        df['achats_par_visite'] = df['nb_achats_30j'] / (df['nb_visites_30j'] + 1)

        # Encodage
        le = LabelEncoder()
        df['segment_encoded'] = le.fit_transform(df['segment'].fillna('unknown'))

        # Features numériques
        features_cols = [
            'anciennete_jours', 'nb_achats_30j', 'nb_achats_90j',
            'montant_total_30j', 'montant_total_90j', 'nb_visites_30j',
            'taux_retour', 'nb_tickets_support', 'score_satisfaction',
            'segment_encoded', 'ratio_achats', 'ratio_montant', 'achats_par_visite',
        ]
        X = df[features_cols].fillna(df[features_cols].median())
        y = df[['has_churned']]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        chemins = {
            'X_train_path': f'/opt/airflow/data/X_train_{date}.parquet',
            'X_test_path':  f'/opt/airflow/data/X_test_{date}.parquet',
            'y_train_path': f'/opt/airflow/data/y_train_{date}.parquet',
            'y_test_path':  f'/opt/airflow/data/y_test_{date}.parquet',
            'features_cols': features_cols,
            'n_train': len(X_train),
            'n_test': len(X_test),
        }

        X_train.to_parquet(chemins['X_train_path'], index=False)
        X_test.to_parquet(chemins['X_test_path'], index=False)
        y_train.to_parquet(chemins['y_train_path'], index=False)
        y_test.to_parquet(chemins['y_test_path'], index=False)

        print(f"Split: {len(X_train)} train / {len(X_test)} test")
        return chemins

    @task
    def entrainer_modele(split: dict, **context) -> dict:
        import pandas as pd
        import mlflow, mlflow.sklearn
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment("churn_prediction")

        X_train = pd.read_parquet(split['X_train_path'])
        y_train = pd.read_parquet(split['y_train_path'])['has_churned']
        X_test  = pd.read_parquet(split['X_test_path'])
        y_test  = pd.read_parquet(split['y_test_path'])['has_churned']

        params = {
            'n_estimators': 100, 'max_depth': 10,
            'min_samples_split': 5, 'random_state': 42, 'class_weight': 'balanced',
        }

        with mlflow.start_run(run_name=f"rf_weekly_{context['ds']}") as run:
            mlflow.log_params(params)
            mlflow.log_param("n_train", split['n_train'])
            mlflow.log_param("n_test", split['n_test'])
            mlflow.log_param("n_features", len(split['features_cols']))

            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            accuracy = accuracy_score(y_test, y_pred)
            roc_auc  = roc_auc_score(y_test, y_proba)

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("roc_auc", roc_auc)
            mlflow.sklearn.log_model(model, "model")

            # Feature importances
            import pandas as pd as pd2
            fi = pd2.Series(model.feature_importances_, index=split['features_cols'])
            print(f"\nTop 5 features :\n{fi.nlargest(5)}")

            print(f"\n{classification_report(y_test, y_pred, target_names=['Actif', 'Churné'])}")
            print(f"ROC-AUC: {roc_auc:.4f} | Accuracy: {accuracy:.4f}")

        return {
            'run_id': run.info.run_id,
            'accuracy': accuracy,
            'roc_auc': roc_auc,
        }

    @task.branch
    def decider_promotion(metriques: dict) -> str:
        roc_auc  = metriques.get('roc_auc', 0)
        accuracy = metriques.get('accuracy', 0)
        print(f"ROC-AUC={roc_auc:.4f} (seuil {SEUIL_ROC_AUC}) | Accuracy={accuracy:.4f} (seuil {SEUIL_ACCURACY})")
        if roc_auc >= SEUIL_ROC_AUC and accuracy >= SEUIL_ACCURACY:
            return 'promouvoir_modele'
        return 'alerter_equipe'

    @task
    def promouvoir_modele(metriques: dict) -> dict:
        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(MLFLOW_URI)
        client = MlflowClient()

        model_uri = f"runs:/{metriques['run_id']}/model"
        model_version = mlflow.register_model(model_uri, "churn_prediction")

        client.transition_model_version_stage(
            name="churn_prediction",
            version=model_version.version,
            stage="Staging",
        )
        client.update_model_version(
            name="churn_prediction",
            version=model_version.version,
            description=f"Modèle hebdomadaire — ROC-AUC={metriques['roc_auc']:.4f}",
        )

        print(f"Modèle promu : churn_prediction v{model_version.version} → Staging")
        return {'model_name': 'churn_prediction', 'version': model_version.version, 'stage': 'Staging'}

    @task
    def alerter_equipe(metriques: dict) -> None:
        print(f"""
ALERTE — Modèle churn insuffisant !
ROC-AUC  : {metriques.get('roc_auc', 'N/A'):.4f} (requis >= {SEUIL_ROC_AUC})
Accuracy : {metriques.get('accuracy', 'N/A'):.4f} (requis >= {SEUIL_ACCURACY})
Run MLflow : {metriques.get('run_id')}
Action : Revoir features et hyperparamètres.
        """)

    @task(trigger_rule='none_failed_min_one_success')
    def rapport_ml(metriques: dict) -> None:
        print(f"""
╔══════════════════════════════════════╗
║     RAPPORT PIPELINE ML CHURN       ║
╠══════════════════════════════════════╣
║ Run MLflow : {metriques.get('run_id', 'N/A')[:20]}      ║
║ ROC-AUC    : {metriques.get('roc_auc', 0):.4f}               ║
║ Accuracy   : {metriques.get('accuracy', 0):.4f}               ║
╚══════════════════════════════════════╝
        """)

    # Orchestration
    chemin = extraire_features()
    split = feature_engineering(chemin)
    metriques = entrainer_modele(split)
    decision = decider_promotion(metriques)

    promotion = promouvoir_modele(metriques)
    alerte = alerter_equipe(metriques)

    decision >> [promotion, alerte]
    [promotion, alerte] >> rapport_ml(metriques)

dag = pipeline_ml_churn_solution()
```

---

## Questions de validation

1. **MLflow** : Où dans l'interface MLflow peut-on comparer deux runs côte à côte ? Comment interpréter la courbe ROC ?
2. **Branchement** : Que se passe-t-il si le modèle dépasse le seuil ROC-AUC mais pas le seuil Accuracy ? Comment gérer ce cas ?
3. **Idempotence** : La tâche `entrainer_modele` est-elle idempotente ? Que se passe-t-il si elle est rejouée ?
4. **Amélioration** : Comment implémenter un test A/B pour comparer le nouveau modèle avec le modèle en production ?
5. **Tests** : Écrire un test pytest pour la fonction `decider_promotion` avec des métriques mockées qui passent et échouent les seuils.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface MLflow (http://localhost:5000) — vue "Experiments" montrant plusieurs runs avec leurs métriques (ROC-AUC, Accuracy) triés par performance
> **Expliquer :** Naviguer dans MLflow pour : (1) voir la liste des runs, (2) comparer deux runs en cochant leurs cases et cliquant "Compare", (3) afficher la courbe ROC dans les artifacts, (4) naviguer vers le Model Registry pour voir le modèle promu en "Staging". Expliquer le concept de Model Registry et les stages (None → Staging → Production → Archived).

---

## Pour aller plus loin

- Ajouter un test de **data drift** : comparer la distribution des features entre la semaine courante et la semaine précédente
- Implémenter une **validation croisée** au lieu d'un simple split train/test
- Ajouter un **hyperparameter tuning** avec Optuna ou GridSearchCV
- Connecter le pipeline à un **Feature Store** (Feast) pour centraliser les features
- Ajouter une tâche de **monitoring du modèle en production** (prédictions sur des données récentes)
