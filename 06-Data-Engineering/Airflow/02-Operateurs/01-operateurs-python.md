# 01 — Opérateurs Python et TaskFlow API

## PythonOperator — rappel et approfondissement

Le `PythonOperator` est l'opérateur le plus utilisé. Il exécute n'importe quelle fonction Python callable.

### Signature complète

```python
from airflow.operators.python import PythonOperator

PythonOperator(
    task_id: str,
    python_callable: Callable,
    op_args: list = None,         # Arguments positionnels
    op_kwargs: dict = None,       # Arguments nommés
    templates_dict: dict = None,  # Dict avec templates Jinja
    templates_exts: list = None,
    show_return_value_in_logs: bool = True,  # Afficher la valeur de retour dans les logs
    # + tous les paramètres BaseOperator (retries, timeout, etc.)
)
```

### Passage d'arguments

```python
from airflow.operators.python import PythonOperator

# --- Avec op_kwargs ---
def traiter_fichier(chemin: str, encodage: str = 'utf-8', limite: int = None):
    print(f"Traitement de {chemin} (encodage: {encodage}, limite: {limite})")
    # ... logique

tache = PythonOperator(
    task_id='traiter_fichier',
    python_callable=traiter_fichier,
    op_kwargs={
        'chemin': '/data/fichier.csv',
        'encodage': 'latin-1',
        'limite': 10000,
    },
)

# --- Avec op_args ---
def additionner(a, b, c):
    return a + b + c

tache2 = PythonOperator(
    task_id='additionner',
    python_callable=additionner,
    op_args=[1, 2, 3],
)

# --- Avec templates_dict (Jinja dans les arguments) ---
def traiter_par_date(date_traitement: str):
    print(f"Traitement pour la date : {date_traitement}")

tache3 = PythonOperator(
    task_id='traiter_par_date',
    python_callable=traiter_par_date,
    op_kwargs={'date_traitement': '{{ ds }}'},  # Jinja dans les kwargs
)
```

---

## Le contexte Airflow dans les fonctions Python

### Via **kwargs

```python
def ma_tache_avec_contexte(**context):
    """
    Le contexte fournit toutes les métadonnées Airflow pour ce run.
    """
    # Objets courants dans le contexte
    dag = context['dag']                      # Objet DAG
    task = context['task']                    # Objet Task (BaseOperator)
    task_instance = context['task_instance']  # Objet TaskInstance (TI)
    dag_run = context['dag_run']              # Objet DagRun

    # Dates
    logical_date = context['logical_date']    # datetime — date logique
    ds = context['ds']                        # str "YYYY-MM-DD"
    ts = context['ts']                        # str ISO 8601
    data_interval_start = context['data_interval_start']
    data_interval_end = context['data_interval_end']

    # Identifiants
    run_id = context['run_id']                # str — ID du DAG Run
    dag_id = dag.dag_id
    task_id = task.task_id

    print(f"Exécution de {dag_id}.{task_id}")
    print(f"Date logique : {ds}")
    print(f"Intervalle : {data_interval_start} → {data_interval_end}")

    # Accès aux paramètres du DAG Run (si DAG déclenché avec params)
    params = context.get('params', {})
    env = params.get('environment', 'dev')
    print(f"Environnement : {env}")

tache = PythonOperator(
    task_id='ma_tache_contexte',
    python_callable=ma_tache_avec_contexte,
)
```

### Via provide_context (ancienne syntaxe — Airflow < 2.0)

```python
# ❌ Ancienne syntaxe Airflow 1.x — NE PLUS UTILISER
tache = PythonOperator(
    task_id='ancienne_syntaxe',
    python_callable=ma_fonction,
    provide_context=True,   # Déprécié depuis Airflow 2.0
)

# ✓ Depuis Airflow 2.0, le contexte est fourni automatiquement
# si la fonction accepte **kwargs ou des paramètres nommés du contexte
```

---

## La TaskFlow API — @task decorator

Introduite dans Airflow 2.0, la **TaskFlow API** permet d'écrire des DAGs de façon plus pythonique, sans instancier explicitement des opérateurs.

### Comparaison : PythonOperator vs @task

```python
# ---- Ancienne façon (PythonOperator) ----
def extraire():
    return {"donnees": [1, 2, 3]}

def transformer(donnees):
    return [x * 2 for x in donnees]

tache_extraire = PythonOperator(
    task_id='extraire',
    python_callable=extraire,
)
tache_transformer = PythonOperator(
    task_id='transformer',
    python_callable=transformer,
    op_kwargs={'donnees': ???}  # Comment passer la valeur de retour d'extraire ?
    # → Il faut utiliser XCom manuellement !
)

# ---- Nouvelle façon (TaskFlow API) ----
from airflow.decorators import dag, task

@dag(
    dag_id='pipeline_taskflow',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
)
def pipeline_taskflow():

    @task
    def extraire():
        return {"donnees": [1, 2, 3]}

    @task
    def transformer(donnees: dict):
        return [x * 2 for x in donnees['donnees']]

    @task
    def charger(resultats: list):
        print(f"Chargement de {len(resultats)} éléments")
        for item in resultats:
            print(f"  → {item}")

    # Passage de données : syntaxe naturelle Python
    donnees_brutes = extraire()
    donnees_transformees = transformer(donnees_brutes)
    charger(donnees_transformees)

# Instanciation du DAG
dag = pipeline_taskflow()
```

---

## TaskFlow API — syntaxe complète

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

@dag(
    dag_id='etl_taskflow_complet',
    description='ETL avec TaskFlow API',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    default_args={
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    tags=['etl', 'taskflow'],
)
def etl_taskflow_complet():
    """
    Pipeline ETL utilisant la TaskFlow API.
    La docstring du DAG apparaît dans l'interface Airflow.
    """

    # Paramètre de configuration du DAG
    @task(task_id='configurer')  # task_id optionnel — par défaut = nom de la fonction
    def configurer():
        return {
            'source_url': 'https://api.example.com/data',
            'table_cible': 'public.donnees',
        }

    @task(
        retries=3,                           # Override les default_args
        retry_delay=timedelta(seconds=10),
        execution_timeout=timedelta(minutes=5),
    )
    def extraire(config: dict) -> dict:
        """Extraction des données depuis l'API."""
        import requests

        response = requests.get(config['source_url'], timeout=30)
        response.raise_for_status()
        data = response.json()

        print(f"Extrait {len(data)} enregistrements")
        return {'records': data, 'count': len(data)}

    @task
    def valider(extraction: dict) -> dict:
        """Validation du schéma des données."""
        records = extraction['records']

        champs_requis = ['id', 'nom', 'valeur']
        erreurs = []

        for i, record in enumerate(records):
            for champ in champs_requis:
                if champ not in record:
                    erreurs.append(f"Ligne {i}: champ '{champ}' manquant")

        if erreurs:
            raise ValueError(f"Validation échouée : {len(erreurs)} erreurs\n" + "\n".join(erreurs[:5]))

        print(f"Validation OK : {len(records)} enregistrements valides")
        return extraction  # Pass-through

    @task
    def transformer(extraction: dict) -> list:
        """Transformation et nettoyage des données."""
        records = extraction['records']

        transformes = []
        for record in records:
            transformes.append({
                'id': record['id'],
                'nom': record['nom'].strip().title(),
                'valeur': float(record['valeur']),
                'source': 'api_externe',
            })

        return transformes

    @task
    def charger(records: list, config: dict) -> int:
        """Chargement dans la base de données (simulé)."""
        table = config['table_cible']

        print(f"Chargement de {len(records)} lignes dans {table}")
        for record in records[:3]:  # Afficher les 3 premiers
            print(f"  → INSERT INTO {table} VALUES {tuple(record.values())}")

        if len(records) > 3:
            print(f"  ... et {len(records) - 3} autres")

        return len(records)

    @task
    def notifier(nb_lignes: int):
        """Envoi d'une notification de fin de pipeline."""
        print(f"Pipeline ETL terminé avec succès !")
        print(f"Total : {nb_lignes} lignes chargées")
        # Ici : appel Slack, email, etc.

    # ---- Orchestration ----
    config = configurer()
    donnees_brutes = extraire(config)
    donnees_validees = valider(donnees_brutes)
    donnees_transformees = transformer(donnees_validees)
    nb = charger(donnees_transformees, config)
    notifier(nb)

# Instanciation
dag = etl_taskflow_complet()
```

---

## Mélanger @task et opérateurs classiques

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models.baseoperator import chain

@dag(
    dag_id='mix_taskflow_operateurs',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
)
def mix_taskflow_operateurs():

    # Opérateur classique
    preparer_env = BashOperator(
        task_id='preparer_env',
        bash_command='mkdir -p /tmp/pipeline && echo "Environnement prêt"',
    )

    # Tâche TaskFlow
    @task
    def extraire():
        return [1, 2, 3, 4, 5]

    @task
    def transformer(data: list):
        return [x ** 2 for x in data]

    # Opérateur classique
    nettoyer = BashOperator(
        task_id='nettoyer',
        bash_command='rm -rf /tmp/pipeline',
    )

    # Orchestration — mélange les deux styles
    donnees = extraire()
    resultats = transformer(donnees)

    # Dépendance manuelle entre opérateur classique et tâche TaskFlow
    preparer_env >> donnees    # Syntaxe >> fonctionne avec les tâches TaskFlow
    resultats >> nettoyer

dag = mix_taskflow_operateurs()
```

---

## ShortCircuitOperator — court-circuiter le pipeline

```python
from airflow.operators.python import ShortCircuitOperator

def verifier_condition(**context) -> bool:
    """
    Si retourne False, toutes les tâches en aval sont skippées.
    Si retourne True, l'exécution continue normalement.
    """
    import datetime
    # Ne traiter que les lundis
    jour = context['logical_date'].weekday()  # 0=lundi, 6=dimanche
    est_lundi = (jour == 0)

    if not est_lundi:
        print(f"Aujourd'hui n'est pas lundi (jour={jour}) — skip du pipeline")
    return est_lundi

with DAG('pipeline_conditionnel', start_date=datetime(2024,1,1),
         schedule='@daily', catchup=False) as dag:

    verifier = ShortCircuitOperator(
        task_id='verifier_si_lundi',
        python_callable=verifier_condition,
    )

    traiter = BashOperator(
        task_id='traiter_donnees_hebdo',
        bash_command='echo "Traitement hebdomadaire du lundi"',
    )

    notifier = BashOperator(
        task_id='notifier',
        bash_command='echo "Notification envoyée"',
    )

    verifier >> traiter >> notifier
    # Si verifier retourne False : traiter et notifier sont en état "skipped"
```

---

## @task.short_circuit — TaskFlow version

```python
from airflow.decorators import dag, task

@dag(start_date=datetime(2024,1,1), schedule='@daily', catchup=False)
def pipeline_conditionnel_taskflow():

    @task.short_circuit
    def verifier_disponibilite_donnees() -> bool:
        """Vérifie que les données sources sont disponibles."""
        import os
        fichier = '/data/source/fichier_du_jour.csv'
        disponible = os.path.exists(fichier)
        print(f"Fichier {fichier} : {'disponible' if disponible else 'absent'}")
        return disponible

    @task
    def traiter():
        print("Traitement des données...")

    @task
    def publier():
        print("Publication des résultats...")

    disponible = verifier_disponibilite_donnees()
    donnees = traiter()
    disponible >> donnees >> publier()

dag = pipeline_conditionnel_taskflow()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La vue Graph d'un DAG TaskFlow dans l'interface Airflow, avec certaines tâches en état "skipped" (couleur rose/grise) après un ShortCircuit
> **Expliquer :** Montrer que les tâches skippées ne sont pas considérées comme des échecs — le DAG Run global est quand même "success". Expliquer la différence entre "skipped", "failed" et "upstream_failed".

---

## PythonVirtualenvOperator — isolation des dépendances

```python
from airflow.operators.python import PythonVirtualenvOperator

def analyser_avec_sklearn(data_path: str):
    """
    Cette fonction tourne dans un virtualenv isolé.
    Les imports sont faits à l'intérieur.
    """
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(data_path)
    # ... analyse ML
    print("Analyse terminée")

tache_sklearn = PythonVirtualenvOperator(
    task_id='analyser_sklearn',
    python_callable=analyser_avec_sklearn,
    requirements=[
        'scikit-learn==1.3.2',
        'pandas==2.1.4',
    ],
    system_site_packages=False,  # Isoler du système
    op_kwargs={'data_path': '/data/dataset.csv'},
)
```

---

## @task.virtualenv — TaskFlow version

```python
from airflow.decorators import dag, task

@dag(start_date=datetime(2024,1,1), schedule='@weekly', catchup=False)
def pipeline_ml_isole():

    @task.virtualenv(
        requirements=['scikit-learn==1.3.2', 'pandas==2.1.4'],
        system_site_packages=False,
    )
    def entrainer_modele(dataset_path: str) -> dict:
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score

        df = pd.read_csv(dataset_path)
        X = df.drop('target', axis=1)
        y = df['target']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)

        accuracy = accuracy_score(y_test, model.predict(X_test))
        print(f"Accuracy: {accuracy:.4f}")

        return {'accuracy': accuracy, 'n_features': X.shape[1]}

    @task
    def enregistrer_metriques(metriques: dict):
        print(f"Enregistrement des métriques : {metriques}")

    resultats = entrainer_modele('/data/dataset.csv')
    enregistrer_metriques(resultats)

dag = pipeline_ml_isole()
```

---

## Bonnes pratiques TaskFlow API

```python
# ✓ Utiliser des type hints — améliore la lisibilité et la sérialisation XCom
@task
def extraire() -> list[dict]:
    return [{"id": 1, "val": 42}]

# ✓ Nommer les tâches explicitement si le nom de fonction est trop générique
@task(task_id='extraire_depuis_api_meteo')
def extraire():
    pass

# ✓ Documenter les tâches — la docstring apparaît dans l'UI
@task
def transformer(data: list) -> list:
    """
    Nettoie et normalise les données brutes.
    - Supprime les doublons
    - Normalise les chaînes de caractères
    - Convertit les types
    """
    pass

# ❌ Ne pas retourner de gros objets (DataFrames, modèles ML)
# Les retours de @task sont sérialisés en XCom (stockés en DB)
@task
def mauvais():
    import pandas as pd
    df = pd.read_csv('/data/fichier_10go.csv')
    return df  # ← DANGER : va saturer la DB !

# ✓ Retourner un chemin de fichier à la place
@task
def bon():
    import pandas as pd
    df = pd.read_csv('/data/fichier_10go.csv')
    output_path = '/tmp/output.parquet'
    df.to_parquet(output_path)
    return output_path  # ← OK : seulement le chemin est stocké en XCom
```

---

## Points clés à retenir

1. `PythonOperator` : opérateur classique, flexible, explicite
2. `@task` : syntaxe moderne, passage de données automatique via XCom
3. Le contexte Airflow (`**context`) donne accès à `ds`, `logical_date`, `dag`, `task_instance`, etc.
4. `ShortCircuitOperator` / `@task.short_circuit` : sauter des tâches conditionnellement
5. `PythonVirtualenvOperator` : isolation des dépendances par tâche
6. Ne jamais retourner de gros objets depuis `@task` — utiliser des chemins de fichiers
