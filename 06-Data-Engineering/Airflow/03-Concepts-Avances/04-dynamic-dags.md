# 04 — DAGs et Tâches Dynamiques

## Pourquoi le dynamisme ?

Les pipelines statiques (une tâche par action codée en dur) ne passent pas à l'échelle quand le nombre de sources ou d'entités varie. Le dynamisme permet de :

- **Créer des tâches automatiquement** en fonction d'une liste (tables, fichiers, pays...)
- **Générer plusieurs DAGs** à partir d'un template commun
- **Adapter le pipeline** à une configuration externe

---

## Dynamic Task Mapping — @task.expand (Airflow 2.3+)

La fonctionnalité la plus moderne pour les tâches dynamiques : `@task.expand()` crée automatiquement N instances d'une tâche à partir d'une liste.

### Exemple simple

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@daily', catchup=False)
def dynamic_mapping_simple():

    @task
    def traiter_table(nom_table: str) -> dict:
        print(f"Traitement de la table : {nom_table}")
        # Simulation d'une extraction SQL
        import random
        nb_lignes = random.randint(100, 10000)
        return {'table': nom_table, 'lignes': nb_lignes}

    @task
    def consolider(resultats: list) -> int:
        total = sum(r['lignes'] for r in resultats)
        print(f"Total traité : {total} lignes sur {len(resultats)} tables")
        return total

    tables = ['commandes', 'clients', 'produits', 'categories', 'fournisseurs']

    # expand() crée une instance de tâche par élément de la liste
    resultats = traiter_table.expand(nom_table=tables)

    # consolidation des résultats (liste des retours de chaque instance)
    consolider(resultats)

dag = dynamic_mapping_simple()
```

Dans l'interface Airflow, vous verrez :
```
traiter_table [commandes]    ✓
traiter_table [clients]      ✓
traiter_table [produits]     ✓
traiter_table [categories]   ✓
traiter_table [fournisseurs] ✓
consolider                   ✓
```

---

## Dynamic Task Mapping avec liste dynamique

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@daily', catchup=False)
def dynamic_mapping_liste_dynamique():

    @task
    def obtenir_liste_tables() -> list[str]:
        """
        La liste est calculée au runtime — non connue à la définition du DAG.
        Peut venir d'une DB, d'une API, d'une Variable Airflow...
        """
        from airflow.models import Variable

        # Option 1 : depuis une Variable Airflow
        # tables = Variable.get("tables_a_traiter", deserialize_json=True)

        # Option 2 : depuis une requête SQL
        # from airflow.providers.postgres.hooks.postgres import PostgresHook
        # hook = PostgresHook('postgres_prod')
        # tables = [row[0] for row in hook.get_records(
        #     "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        # )]

        # Option 3 : liste simulée
        return ['ventes_fr', 'ventes_de', 'ventes_es', 'ventes_it', 'ventes_uk']

    @task
    def extraire_par_pays(pays_table: str) -> dict:
        pays = pays_table.replace('ventes_', '').upper()
        print(f"Extraction des ventes pour {pays}")
        import random
        return {'pays': pays, 'nb': random.randint(500, 5000)}

    @task
    def transformer(extraction: dict) -> dict:
        # Transformation par pays
        montant_moyen = extraction['nb'] * 42.5  # Simulation
        return {**extraction, 'montant_total': montant_moyen}

    @task
    def charger_tout(transformations: list) -> dict:
        total_lignes = sum(t['nb'] for t in transformations)
        total_montant = sum(t['montant_total'] for t in transformations)
        print(f"Chargement global : {total_lignes} lignes, {total_montant:.2f} €")
        return {'total_lignes': total_lignes, 'total_montant': total_montant}

    # Chaîne dynamique
    tables = obtenir_liste_tables()
    extractions = extraire_par_pays.expand(pays_table=tables)
    transformations = transformer.expand(extraction=extractions)
    charger_tout(transformations)

dag = dynamic_mapping_liste_dynamique()
```

---

## expand_kwargs — plusieurs paramètres dynamiques

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@daily', catchup=False)
def dynamic_mapping_multi_params():

    @task
    def obtenir_configurations() -> list[dict]:
        """Retourne une liste de configurations."""
        return [
            {'source': 'postgresql', 'table': 'commandes', 'batch_size': 10000},
            {'source': 'mysql',      'table': 'factures',  'batch_size': 5000},
            {'source': 'sqlite',     'table': 'archives',  'batch_size': 1000},
        ]

    @task
    def migrer_table(source: str, table: str, batch_size: int) -> dict:
        print(f"Migration {source}.{table} par batches de {batch_size}")
        return {'source': source, 'table': table, 'lignes': batch_size * 3}

    @task
    def rapport_migration(resultats: list) -> None:
        for r in resultats:
            print(f"  {r['source']}.{r['table']}: {r['lignes']} lignes")

    configs = obtenir_configurations()

    # expand_kwargs() passe chaque dict comme kwargs à la fonction
    migrations = migrer_table.expand_kwargs(configs)
    rapport_migration(migrations)

dag = dynamic_mapping_multi_params()
```

---

## expand avec constantes — partial()

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@daily', catchup=False)
def dynamic_mapping_avec_constante():

    @task
    def traiter(table: str, schema: str, mode: str) -> dict:
        print(f"Traitement : {schema}.{table} en mode {mode}")
        return {'table': table, 'schema': schema}

    tables = ['commandes', 'clients', 'produits']

    # partial() fixe les arguments constants, expand() fixe les arguments dynamiques
    resultats = traiter.partial(
        schema='public',  # ← constant pour toutes les instances
        mode='incremental',  # ← constant pour toutes les instances
    ).expand(
        table=tables  # ← varie pour chaque instance
    )

dag = dynamic_mapping_avec_constante()
```

---

## Génération de DAGs dynamiques (pattern factory)

Une autre approche : générer plusieurs DAGs à partir d'un template Python.

### Pattern 1 : boucle simple

```python
# dags/dags_dynamiques.py

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuration des pipelines à générer
CONFIGURATIONS_PIPELINES = [
    {
        'dag_id': 'etl_france',
        'pays': 'FR',
        'source_conn': 'postgres_france',
        'schedule': '0 6 * * *',
        'tags': ['etl', 'france'],
    },
    {
        'dag_id': 'etl_allemagne',
        'pays': 'DE',
        'source_conn': 'postgres_allemagne',
        'schedule': '0 7 * * *',
        'tags': ['etl', 'allemagne'],
    },
    {
        'dag_id': 'etl_espagne',
        'pays': 'ES',
        'source_conn': 'postgres_espagne',
        'schedule': '0 8 * * *',
        'tags': ['etl', 'espagne'],
    },
]


def creer_dag(config: dict) -> DAG:
    """Factory function qui crée un DAG à partir d'une configuration."""

    def extraire(pays, conn, **context):
        print(f"Extraction pour {pays} depuis {conn}")
        print(f"Date : {context['ds']}")

    def transformer(pays, **context):
        print(f"Transformation des données {pays}")

    def charger(pays, **context):
        print(f"Chargement des données {pays} dans le DWH")

    with DAG(
        dag_id=config['dag_id'],
        start_date=datetime(2024, 1, 1),
        schedule=config['schedule'],
        catchup=False,
        tags=config['tags'],
        doc_md=f"Pipeline ETL pour le pays : **{config['pays']}**",
    ) as dag:

        t_extraire = PythonOperator(
            task_id='extraire',
            python_callable=extraire,
            op_kwargs={'pays': config['pays'], 'conn': config['source_conn']},
        )

        t_transformer = PythonOperator(
            task_id='transformer',
            python_callable=transformer,
            op_kwargs={'pays': config['pays']},
        )

        t_charger = PythonOperator(
            task_id='charger',
            python_callable=charger,
            op_kwargs={'pays': config['pays']},
        )

        t_extraire >> t_transformer >> t_charger

    return dag


# Créer les DAGs et les injecter dans le namespace global
# (Airflow détecte les objets DAG dans le namespace global du module)
for config_pipeline in CONFIGURATIONS_PIPELINES:
    globals()[config_pipeline['dag_id']] = creer_dag(config_pipeline)
```

### Pattern 2 : configuration depuis un fichier YAML

```yaml
# dags/config/pipelines.yaml
pipelines:
  - dag_id: etl_api_meteo
    description: "Extraction données météo"
    schedule: "0 6 * * *"
    source_type: http
    source_conn: api_meteo
    destination: postgres_dwh
    tags: [etl, meteo]

  - dag_id: etl_api_finance
    description: "Extraction données financières"
    schedule: "0 7 * * 1-5"
    source_type: http
    source_conn: api_finance
    destination: postgres_dwh
    tags: [etl, finance]

  - dag_id: etl_api_crm
    description: "Extraction données CRM"
    schedule: "30 7 * * *"
    source_type: http
    source_conn: api_crm
    destination: postgres_dwh
    tags: [etl, crm]
```

```python
# dags/factory_depuis_yaml.py

import yaml
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# Charger le fichier YAML
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config/pipelines.yaml')

def charger_config(fichier: str) -> list:
    with open(fichier) as f:
        return yaml.safe_load(f)['pipelines']

def creer_dag_depuis_config(config: dict) -> DAG:
    def extraire(**context):
        print(f"Extraction depuis {config['source_conn']} (type: {config['source_type']})")
        return f"données extraites pour {config['dag_id']}"

    def charger(**context):
        ti = context['task_instance']
        donnees = ti.xcom_pull(task_ids='extraire')
        print(f"Chargement vers {config['destination']}: {donnees}")

    with DAG(
        dag_id=config['dag_id'],
        description=config.get('description', ''),
        start_date=datetime(2024, 1, 1),
        schedule=config['schedule'],
        catchup=False,
        tags=config.get('tags', []),
    ) as dag:

        t_extraire = PythonOperator(task_id='extraire', python_callable=extraire)
        t_charger = PythonOperator(task_id='charger', python_callable=charger)
        t_extraire >> t_charger

    return dag

# Générer et enregistrer les DAGs
for config in charger_config(CONFIG_FILE):
    globals()[config['dag_id']] = creer_dag_depuis_config(config)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow — liste des DAGs filtrée par tag "etl" montrant plusieurs DAGs générés dynamiquement (etl_france, etl_allemagne, etl_espagne)
> **Expliquer :** Montrer comment un seul fichier Python génère plusieurs DAGs. Filtrer par tag dans l'UI pour grouper les DAGs liés. Ouvrir l'un d'eux pour montrer que tous ont la même structure de tâches. Expliquer le risque : si la configuration change (ajout d'un pays), les DAGs précédents restent en DB avec leur historique.

---

## Bonnes pratiques pour les DAGs dynamiques

### expand() vs factory

| Critère | `expand()` | Factory de DAGs |
|---|---|---|
| Usage | Même pipeline, N instances d'une tâche | N pipelines distincts |
| Visibilité | Une seule entrée dans la liste des DAGs | Un DAG par entrée (lisible mais encombre l'UI) |
| Contrôle indépendant | Difficile | Facile (chaque DAG a son schedule, ses alertes) |
| Logging | Groupé sous le même DAG Run | Séparé par DAG |
| Performance | Meilleure (moins d'overhead) | Plus d'overhead (N DAGs scannés) |

### Limites de expand()

```python
# ✓ expand() supporte jusqu'à plusieurs milliers d'instances
# (limité par max_map_length dans airflow.cfg, défaut = 1024)

# ❌ expand() ne supporte pas les opérateurs classiques directement
# Uniquement @task et les TaskFlow operators

# ❌ Chaîne d'expand() complexe peut être difficile à déboguer
```

### Limites des factories de DAGs

```python
# ❌ Ne jamais faire d'I/O lourds au top-level (connexion DB, appel API)
# pour générer la liste des configs — le Scheduler parse les DAGs fréquemment

# ✓ Utiliser un fichier YAML local ou une Variable Airflow statique
# pour la configuration des factories

# ✓ Limiter le nombre de DAGs générés (< 200 recommandé)
# Au-delà, utiliser expand() ou des DAGs avec paramètres
```

---

## DAGs avec params — alternative aux factories

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='pipeline_avec_params',
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Déclenché manuellement avec des params
    catchup=False,
    params={
        'pays': 'FR',
        'date_debut': '2024-01-01',
        'date_fin': '2024-01-31',
        'batch_size': 1000,
    },
)
def pipeline_avec_params():

    @task
    def extraire(**context) -> dict:
        params = context['params']
        pays = params['pays']
        date_debut = params['date_debut']
        date_fin = params['date_fin']

        print(f"Extraction pour {pays} : {date_debut} → {date_fin}")
        return {'pays': pays, 'lignes': 5000}

    @task
    def charger(extraction: dict, **context) -> int:
        batch_size = context['params']['batch_size']
        print(f"Chargement {extraction['pays']} par batches de {batch_size}")
        return extraction['lignes']

    extraction = extraire()
    charger(extraction)

dag = pipeline_avec_params()
```

Déclencher avec des params personnalisés :

```bash
# Via CLI
airflow dags trigger pipeline_avec_params \
    --conf '{"pays": "DE", "date_debut": "2024-02-01", "date_fin": "2024-02-29"}'
```

Ou via l'interface : bouton "Trigger DAG w/ config" → formulaire JSON.

---

## Points clés à retenir

1. `@task.expand()` : crée N instances d'une tâche depuis une liste — style moderne, recommandé
2. `@task.partial().expand()` : fixe des arguments constants + arguments dynamiques
3. Les factories de DAGs (boucle `for` + `globals()`) génèrent plusieurs DAGs depuis un template
4. Préférer `expand()` pour les traitements en batch, les factories pour des pipelines vraiment distincts
5. Ne jamais faire d'appels réseau/DB au top-level d'un fichier DAG factory
6. Les **params** permettent un DAG unique déclenché manuellement avec des arguments variables
