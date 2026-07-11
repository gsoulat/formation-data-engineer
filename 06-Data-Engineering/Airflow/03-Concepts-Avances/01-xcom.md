# 01 — XCom : Passage de données entre tâches

## Qu'est-ce qu'un XCom ?

**XCom** (Cross-Communication) est le mécanisme d'Airflow permettant à des tâches de **partager de petites quantités de données** entre elles.

Les XComs sont stockés dans la **metadata database** d'Airflow. Ils sont associés à :
- Un `dag_id`
- Un `task_id`
- Un `run_id` (DAG Run)
- Une `key` (par défaut : `"return_value"`)

> **Attention** : XCom est conçu pour de **petites valeurs** (quelques Ko maximum).
> Ne jamais stocker des DataFrames complets, des modèles ML, ou des fichiers volumineux.
> Pour de gros volumes : utiliser le chemin du fichier comme XCom.

---

## XCom push — pousser une valeur

### Méthode 1 : via la valeur de retour (automatique)

```python
from airflow.operators.python import PythonOperator

def extraire() -> dict:
    """
    La valeur de retour est automatiquement pushée en XCom
    sous la clé 'return_value'.
    """
    nb_enregistrements = 1234
    source = "api_ventes"
    return {"count": nb_enregistrements, "source": source}

tache_extraire = PythonOperator(
    task_id='extraire',
    python_callable=extraire,
    # do_xcom_push=True  ← True par défaut
)
# → Pousse {"count": 1234, "source": "api_ventes"} sous la clé 'return_value'
```

### Méthode 2 : push explicite via task_instance

```python
def ma_tache(**context):
    ti = context['task_instance']

    # Push avec clé personnalisée
    ti.xcom_push(key='nb_lignes', value=5678)
    ti.xcom_push(key='fichier_output', value='/tmp/output_2024-01-15.parquet')
    ti.xcom_push(key='metriques', value={
        'accuracy': 0.94,
        'precision': 0.91,
        'recall': 0.97,
    })

    # On peut aussi pousser la valeur de retour ET des XComs custom
    return "status_ok"  # → clé 'return_value'

tache = PythonOperator(
    task_id='ma_tache',
    python_callable=ma_tache,
)
```

---

## XCom pull — récupérer une valeur

```python
def tache_suivante(**context):
    ti = context['task_instance']

    # Récupérer la valeur de retour d'une autre tâche
    resultat_extraction = ti.xcom_pull(task_ids='extraire')
    # → {"count": 1234, "source": "api_ventes"}

    # Récupérer avec une clé spécifique
    nb_lignes = ti.xcom_pull(task_ids='ma_tache', key='nb_lignes')
    # → 5678

    fichier = ti.xcom_pull(task_ids='ma_tache', key='fichier_output')
    # → '/tmp/output_2024-01-15.parquet'

    # Récupérer depuis plusieurs tâches en même temps
    resultats = ti.xcom_pull(task_ids=['tache_a', 'tache_b', 'tache_c'])
    # → [valeur_a, valeur_b, valeur_c]

    print(f"Extraction : {resultat_extraction}")
    print(f"Nb lignes : {nb_lignes}")
    print(f"Fichier : {fichier}")

tache_2 = PythonOperator(
    task_id='tache_suivante',
    python_callable=tache_suivante,
)
```

---

## XCom avec la TaskFlow API — passage implicite

Avec `@task`, les XComs sont gérés **automatiquement**. Pas besoin de `xcom_push` / `xcom_pull` :

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@daily', catchup=False)
def pipeline_avec_xcoms():

    @task
    def extraire() -> dict:
        return {"donnees": [1, 2, 3, 4, 5], "source": "api"}

    @task
    def transformer(extraction: dict) -> list:
        # 'extraction' contient automatiquement le retour de 'extraire'
        donnees = extraction['donnees']
        return [x * 2 for x in donnees]

    @task
    def charger(donnees: list) -> int:
        print(f"Chargement de {len(donnees)} éléments : {donnees}")
        return len(donnees)

    @task
    def notifier(nb_charges: int, source: dict):
        # On peut même récupérer des valeurs de PLUSIEURS tâches précédentes
        print(f"Pipeline terminé : {nb_charges} éléments depuis {source['source']}")

    # Le passage de données se fait par les appels de fonctions
    data = extraire()
    transformed = transformer(data)
    nb = charger(transformed)
    notifier(nb, data)   # data est partagé entre transformer ET notifier

dag = pipeline_avec_xcoms()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow → Admin → XComs — montrer la liste des XComs stockés pour un DAG Run avec leurs clés et valeurs
> **Expliquer :** Naviguer vers Admin → XComs dans le menu. Filtrer par DAG. Montrer que chaque XCom a un dag_id, task_id, run_id, key, et value. Ouvrir un XCom pour montrer la valeur sérialisée. Expliquer que c'est un tableau en base de données — donc limité en taille.

---

## Exemple complet : pipeline de traitement avec XComs

```python
# dags/pipeline_xcom.py

from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(
    dag_id='pipeline_xcom_demonstration',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['xcom', 'formation'],
)
def pipeline_xcom_demonstration():
    """
    Démonstration du passage de données via XCom et TaskFlow API.
    """

    @task
    def lire_configuration() -> dict:
        """Retourne la configuration du pipeline pour ce run."""
        return {
            'limite': 1000,
            'format': 'parquet',
            'destination': 's3://mon-bucket/processed/',
        }

    @task
    def extraire_donnees(config: dict) -> dict:
        """Simule une extraction de données depuis une API."""
        import random

        nb = random.randint(500, config['limite'])
        donnees = [{'id': i, 'valeur': random.uniform(0, 100)} for i in range(nb)]

        # Sauvegarder localement
        import json
        chemin = '/tmp/donnees_brutes.json'
        with open(chemin, 'w') as f:
            json.dump(donnees, f)

        return {
            'chemin': chemin,
            'nb_lignes': nb,
            'statut': 'succes',
        }

    @task
    def valider_donnees(extraction: dict) -> bool:
        """Valide que l'extraction a fonctionné correctement."""
        nb = extraction['nb_lignes']
        statut = extraction['statut']

        if statut != 'succes':
            raise ValueError(f"Extraction en échec : statut={statut}")

        if nb < 100:
            raise ValueError(f"Trop peu de données : {nb} < 100 attendus")

        print(f"Validation OK : {nb} lignes, statut={statut}")
        return True

    @task
    def transformer_donnees(extraction: dict, validation: bool) -> dict:
        """Transforme les données brutes."""
        import json, statistics

        chemin = extraction['chemin']
        with open(chemin) as f:
            donnees = json.load(f)

        # Calculs
        valeurs = [d['valeur'] for d in donnees]
        stats = {
            'min': min(valeurs),
            'max': max(valeurs),
            'moyenne': statistics.mean(valeurs),
            'ecart_type': statistics.stdev(valeurs),
        }

        print(f"Statistiques calculées sur {len(donnees)} lignes:")
        for k, v in stats.items():
            print(f"  {k}: {v:.4f}")

        return {
            'chemin': chemin,
            'nb_lignes': len(donnees),
            'statistiques': stats,
        }

    @task
    def generer_rapport(transformation: dict, config: dict) -> str:
        """Génère un rapport des métriques."""
        stats = transformation['statistiques']
        rapport = f"""
=== RAPPORT PIPELINE ===
Date : 2024-01-15
Destination : {config['destination']}
Lignes traitées : {transformation['nb_lignes']}
Format : {config['format']}

Statistiques des valeurs :
  Min    : {stats['min']:.2f}
  Max    : {stats['max']:.2f}
  Moyenne: {stats['moyenne']:.2f}
  Écart-type: {stats['ecart_type']:.2f}
========================
        """.strip()

        print(rapport)

        chemin_rapport = '/tmp/rapport_pipeline.txt'
        with open(chemin_rapport, 'w') as f:
            f.write(rapport)

        return chemin_rapport

    # Orchestration
    config = lire_configuration()
    extraction = extraire_donnees(config)
    validation = valider_donnees(extraction)
    transformation = transformer_donnees(extraction, validation)
    rapport = generer_rapport(transformation, config)

dag = pipeline_xcom_demonstration()
```

---

## XComs avancés : utilisation avec PythonOperator classique

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    dag_id='xcom_avance',
    start_date=datetime(2024, 1, 1),
    schedule='@once',
    catchup=False,
) as dag:

    def tache_a(**context):
        ti = context['task_instance']

        # Push multiple valeurs avec des clés différentes
        ti.xcom_push(key='config_etl', value={
            'source': 'postgresql',
            'destination': 'bigquery',
            'batch_size': 10000,
        })

        ti.xcom_push(key='liste_tables', value=[
            'commandes', 'clients', 'produits', 'categories'
        ])

        ti.xcom_push(key='timestamp_debut', value=datetime.now().isoformat())

        return 'tache_a_terminee'  # clé 'return_value'

    def tache_b(**context):
        ti = context['task_instance']

        # Récupérer différentes valeurs
        statut_a = ti.xcom_pull(task_ids='tache_a')                          # return_value
        config = ti.xcom_pull(task_ids='tache_a', key='config_etl')          # dict
        tables = ti.xcom_pull(task_ids='tache_a', key='liste_tables')        # list
        ts = ti.xcom_pull(task_ids='tache_a', key='timestamp_debut')         # str

        print(f"Statut A : {statut_a}")
        print(f"Config ETL : {config}")
        print(f"Tables : {tables}")
        print(f"Timestamp début : {ts}")

        # Traiter chaque table
        resultats = {}
        for table in tables:
            # Simulation
            resultats[table] = {'lignes': 1000, 'statut': 'ok'}

        ti.xcom_push(key='resultats_tables', value=resultats)
        return len(tables)

    def tache_finale(**context):
        ti = context['task_instance']

        # Récupérer depuis les deux tâches précédentes
        nb_tables = ti.xcom_pull(task_ids='tache_b')
        resultats = ti.xcom_pull(task_ids='tache_b', key='resultats_tables')
        ts_debut = ti.xcom_pull(task_ids='tache_a', key='timestamp_debut')

        print(f"Pipeline terminé : {nb_tables} tables traitées")
        print(f"Résultats : {resultats}")
        print(f"Durée : depuis {ts_debut}")

    op_a = PythonOperator(task_id='tache_a', python_callable=tache_a)
    op_b = PythonOperator(task_id='tache_b', python_callable=tache_b)
    op_finale = PythonOperator(task_id='tache_finale', python_callable=tache_finale)

    op_a >> op_b >> op_finale
```

---

## Limites et bonnes pratiques XCom

### Ce qu'il ne faut PAS faire

```python
# ❌ INTERDIT : retourner un DataFrame en XCom
@task
def extraire() -> pd.DataFrame:
    df = pd.read_csv('/data/gros_fichier_1go.csv')
    return df  # → Va saturer la metadata DB !

# ❌ INTERDIT : retourner un modèle ML
@task
def entrainer():
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X, y)
    return model  # → Non sérialisable, trop volumineux

# ❌ DÉCONSEILLÉ : retourner une liste de milliers d'éléments
@task
def extraire() -> list:
    return [{"id": i, "data": "..."} for i in range(100000)]  # → Trop gros
```

### Ce qu'il FAUT faire

```python
# ✓ Retourner un chemin de fichier
@task
def extraire() -> str:
    df = pd.read_csv('/data/gros_fichier.csv')
    chemin = '/tmp/extrait.parquet'
    df.to_parquet(chemin)
    return chemin  # ← Petit, sérialisable

# ✓ Retourner un chemin S3
@task
def extraire() -> str:
    # ... traitement ...
    return 's3://mon-bucket/data/extrait.parquet'

# ✓ Retourner des métriques (petites)
@task
def transformer(chemin: str) -> dict:
    df = pd.read_parquet(chemin)
    # ... transformation ...
    return {
        'nb_lignes': len(df),
        'nb_colonnes': len(df.columns),
        'taille_mb': os.path.getsize(chemin) / 1024 / 1024,
    }
```

### Configurer les backends XCom personnalisés

Pour de gros volumes de données, il est possible de configurer un **backend XCom custom** (stockage dans S3, GCS, etc.) :

```python
# airflow.cfg
[core]
xcom_backend = airflow.providers.amazon.aws.xcom_backends.S3XComBackend

# Variables d'environnement
AIRFLOW__CORE__XCOM_BACKEND=airflow.providers.amazon.aws.xcom_backends.S3XComBackend
AIRFLOW__AWS__XCOM_S3_BUCKET=mon-bucket-xcoms
```

---

## Voir les XComs dans l'interface

1. Aller dans **Admin → XComs**
2. Filtrer par DAG ou task
3. Chaque ligne = un XCom avec dag_id, task_id, run_id, key, value, timestamp

Ou depuis la vue d'une Task Instance :
1. Cliquer sur la tâche dans Graph View
2. Cliquer sur "XCom"

---

## Points clés à retenir

1. Les XComs permettent le passage de **petites valeurs** entre tâches (quelques Ko max)
2. La **TaskFlow API** gère les XComs automatiquement via les valeurs de retour
3. Avec `PythonOperator`, utiliser `ti.xcom_push()` et `ti.xcom_pull()`
4. **Ne jamais stocker** des DataFrames, modèles ML, ou gros fichiers en XCom
5. Stocker des **chemins de fichiers** (local ou S3) à la place
6. Les XComs sont consultables dans **Admin → XComs** dans l'interface web
