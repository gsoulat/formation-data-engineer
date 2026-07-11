# 02 — Opérateurs SQL

## Vue d'ensemble des opérateurs SQL

Airflow propose plusieurs opérateurs pour interagir avec des bases de données relationnelles. Ils nécessitent le package `apache-airflow-providers-common-sql` ainsi que le provider spécifique à chaque base.

```bash
# Installation des providers
pip install apache-airflow-providers-common-sql
pip install apache-airflow-providers-postgres
pip install apache-airflow-providers-mysql
pip install apache-airflow-providers-microsoft-mssql
pip install apache-airflow-providers-snowflake
```

---

## Configurer une connexion PostgreSQL dans Airflow

Avant d'utiliser les opérateurs SQL, il faut configurer une **Connection** dans Airflow.

### Via l'interface web

Aller dans **Admin → Connections → + Add a new record**

| Champ | Valeur exemple |
|---|---|
| Connection Id | `postgres_production` |
| Connection Type | `Postgres` |
| Host | `localhost` ou nom du service Docker |
| Schema | `ma_base` |
| Login | `airflow` |
| Password | `motdepasse` |
| Port | `5432` |

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow — Admin → Connections → formulaire de création d'une connexion PostgreSQL rempli
> **Expliquer :** Montrer chaque champ. Expliquer que le Connection Id est la clé qui sera utilisée dans les opérateurs (`conn_id='postgres_production'`). Montrer le bouton "Test" qui permet de vérifier que la connexion fonctionne avant de sauvegarder.

---

### Via CLI

```bash
# Créer une connexion PostgreSQL
airflow connections add 'postgres_production' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-login 'airflow' \
    --conn-password 'motdepasse' \
    --conn-port '5432' \
    --conn-schema 'ma_base'

# Vérifier la connexion
airflow connections get 'postgres_production'
```

### Via variable d'environnement (Docker)

```yaml
# docker-compose.yaml
environment:
  AIRFLOW_CONN_POSTGRES_PRODUCTION: >-
    postgresql://airflow:motdepasse@postgres:5432/ma_base
```

---

## PostgresOperator

Exécute du SQL sur une base PostgreSQL.

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Requête simple
creer_table = PostgresOperator(
    task_id='creer_table',
    postgres_conn_id='postgres_production',
    sql="""
        CREATE TABLE IF NOT EXISTS ventes (
            id          SERIAL PRIMARY KEY,
            date_vente  DATE NOT NULL,
            produit_id  INTEGER NOT NULL,
            quantite    INTEGER NOT NULL,
            montant     NUMERIC(10, 2) NOT NULL,
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """,
)

# Insertion avec template Jinja
inserer_donnees = PostgresOperator(
    task_id='inserer_donnees',
    postgres_conn_id='postgres_production',
    sql="""
        INSERT INTO ventes (date_vente, produit_id, quantite, montant)
        SELECT
            '{{ ds }}'::DATE,
            produit_id,
            SUM(quantite),
            SUM(montant)
        FROM ventes_staging
        WHERE date_vente = '{{ ds }}'::DATE
        GROUP BY produit_id
        ON CONFLICT (date_vente, produit_id)
        DO UPDATE SET
            quantite = EXCLUDED.quantite,
            montant  = EXCLUDED.montant;
    """,
)

# Requête depuis un fichier .sql
executer_fichier = PostgresOperator(
    task_id='executer_transformation',
    postgres_conn_id='postgres_production',
    sql='sql/transformer_ventes.sql',  # Chemin relatif au dossier dags/
)
```

### Fichier SQL externe

```sql
-- dags/sql/transformer_ventes.sql
-- Variables Jinja disponibles dans les fichiers .sql aussi

INSERT INTO ventes_agregees (
    semaine,
    produit_id,
    total_quantite,
    total_montant,
    ticket_moyen
)
SELECT
    DATE_TRUNC('week', date_vente) AS semaine,
    produit_id,
    SUM(quantite)                  AS total_quantite,
    SUM(montant)                   AS total_montant,
    AVG(montant)                   AS ticket_moyen
FROM ventes
WHERE date_vente >= '{{ data_interval_start }}'::DATE
  AND date_vente <  '{{ data_interval_end }}'::DATE
GROUP BY 1, 2
ON CONFLICT (semaine, produit_id)
DO UPDATE SET
    total_quantite = EXCLUDED.total_quantite,
    total_montant  = EXCLUDED.total_montant,
    ticket_moyen   = EXCLUDED.ticket_moyen;
```

### Exécuter plusieurs requêtes

```python
# Passer une liste de requêtes SQL
pipeline_sql = PostgresOperator(
    task_id='pipeline_sql',
    postgres_conn_id='postgres_production',
    sql=[
        "TRUNCATE TABLE staging.ventes_temp;",
        "INSERT INTO staging.ventes_temp SELECT * FROM source.ventes WHERE date = '{{ ds }}';",
        "UPDATE staging.ventes_temp SET statut = 'traite' WHERE statut IS NULL;",
    ],
)

# Ou passer une liste de fichiers
pipeline_sql_fichiers = PostgresOperator(
    task_id='pipeline_sql_fichiers',
    postgres_conn_id='postgres_production',
    sql=[
        'sql/01_truncate_staging.sql',
        'sql/02_insert_staging.sql',
        'sql/03_transform.sql',
    ],
)
```

---

## SQLExecuteQueryOperator — opérateur universel

Depuis Airflow 2.4, `SQLExecuteQueryOperator` remplace les opérateurs SQL spécifiques en utilisant le provider détecté automatiquement depuis la connexion.

```python
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Fonctionne avec PostgreSQL, MySQL, SQLite, Snowflake, BigQuery...
# Le type de DB est détecté depuis la connexion conn_id

tache_sql = SQLExecuteQueryOperator(
    task_id='executer_requete',
    conn_id='postgres_production',  # ou 'mysql_prod', 'snowflake_prod'...
    sql="""
        SELECT COUNT(*) as nb_lignes
        FROM ventes
        WHERE date_vente = '{{ ds }}';
    """,
    # Retourner les résultats dans les logs et XCom
    do_xcom_push=True,
)
```

---

## SQLCheckOperator — vérification de la qualité des données

```python
from airflow.providers.common.sql.operators.sql import SQLCheckOperator

# Vérifie que la requête retourne une seule ligne avec une valeur "truthy"
# (valeurs non nulles, non zéro)
verifier_donnees = SQLCheckOperator(
    task_id='verifier_donnees_du_jour',
    conn_id='postgres_production',
    sql="""
        SELECT COUNT(*) > 0
        FROM ventes
        WHERE date_vente = '{{ ds }}'
    """,
    # Si COUNT(*) = 0, retourne False → la tâche ÉCHOUE
)
```

---

## SQLValueCheckOperator — vérifier une valeur précise

```python
from airflow.providers.common.sql.operators.sql import SQLValueCheckOperator

# Vérifie que la requête retourne exactement la valeur attendue
verifier_total = SQLValueCheckOperator(
    task_id='verifier_total_journalier',
    conn_id='postgres_production',
    sql="""
        SELECT COUNT(DISTINCT client_id)
        FROM commandes
        WHERE date_commande = '{{ ds }}'
    """,
    pass_value=100,        # Valeur exacte attendue
    tolerance=0.05,        # Tolérance : ± 5% (optionnel)
    # → Accepte entre 95 et 105 commandes
)
```

---

## SQLIntervalCheckOperator — comparer avec le passé

```python
from airflow.providers.common.sql.operators.sql import SQLIntervalCheckOperator

# Compare les métriques actuelles avec celles d'il y a N jours
verifier_variation = SQLIntervalCheckOperator(
    task_id='verifier_variation_vs_hier',
    conn_id='postgres_production',
    table='ventes',
    metrics_thresholds={
        'COUNT(*)': 1.5,        # Ne pas dépasser 150% ou descendre sous 66% vs hier
        'SUM(montant)': 2.0,    # Variation max de 200%
    },
    date_filter_column='date_vente',
    days_back=-1,               # Comparer avec J-1
)
```

---

## Un DAG complet avec pipeline SQL

```python
# dags/pipeline_datawarehouse.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.common.sql.operators.sql import SQLCheckOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='pipeline_datawarehouse',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='0 2 * * *',   # Tous les jours à 2h du matin
    catchup=False,
    tags=['dwh', 'sql', 'etl'],
) as dag:

    # ---- 1. Créer les tables si elles n'existent pas ----
    creer_tables = PostgresOperator(
        task_id='creer_tables',
        postgres_conn_id='postgres_production',
        sql="""
            CREATE TABLE IF NOT EXISTS staging.commandes_raw (
                id              BIGINT,
                client_id       INTEGER,
                produit_id      INTEGER,
                date_commande   DATE,
                montant         NUMERIC(10,2),
                statut          VARCHAR(50),
                loaded_at       TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS dwh.fait_commandes (
                date_commande   DATE,
                client_id       INTEGER,
                produit_id      INTEGER,
                nb_commandes    INTEGER,
                total_montant   NUMERIC(12,2),
                PRIMARY KEY (date_commande, client_id, produit_id)
            );
        """,
    )

    # ---- 2. Charger dans le staging ----
    charger_staging = PostgresOperator(
        task_id='charger_staging',
        postgres_conn_id='postgres_production',
        sql="""
            -- Supprimer les données du jour pour idempotence
            DELETE FROM staging.commandes_raw
            WHERE date_commande = '{{ ds }}'::DATE;

            -- Insérer depuis la source
            INSERT INTO staging.commandes_raw
                (id, client_id, produit_id, date_commande, montant, statut)
            SELECT
                id, client_id, produit_id, date_commande, montant, statut
            FROM source.commandes
            WHERE date_commande = '{{ ds }}'::DATE;
        """,
    )

    # ---- 3. Vérification qualité staging ----
    verifier_staging = SQLCheckOperator(
        task_id='verifier_staging_non_vide',
        conn_id='postgres_production',
        sql="""
            SELECT COUNT(*) > 0
            FROM staging.commandes_raw
            WHERE date_commande = '{{ ds }}'::DATE
        """,
    )

    verifier_pas_doublons = SQLCheckOperator(
        task_id='verifier_pas_doublons',
        conn_id='postgres_production',
        sql="""
            SELECT COUNT(*) = COUNT(DISTINCT id)
            FROM staging.commandes_raw
            WHERE date_commande = '{{ ds }}'::DATE
        """,
    )

    # ---- 4. Transformation vers le DWH ----
    transformer_dwh = PostgresOperator(
        task_id='transformer_vers_dwh',
        postgres_conn_id='postgres_production',
        sql="""
            INSERT INTO dwh.fait_commandes
                (date_commande, client_id, produit_id, nb_commandes, total_montant)
            SELECT
                date_commande,
                client_id,
                produit_id,
                COUNT(*)            AS nb_commandes,
                SUM(montant)        AS total_montant
            FROM staging.commandes_raw
            WHERE date_commande = '{{ ds }}'::DATE
              AND statut = 'validee'
            GROUP BY date_commande, client_id, produit_id
            ON CONFLICT (date_commande, client_id, produit_id)
            DO UPDATE SET
                nb_commandes  = EXCLUDED.nb_commandes,
                total_montant = EXCLUDED.total_montant;
        """,
    )

    # ---- 5. Vérification post-chargement ----
    verifier_dwh = SQLCheckOperator(
        task_id='verifier_chargement_dwh',
        conn_id='postgres_production',
        sql="""
            SELECT
                (SELECT COUNT(*) FROM dwh.fait_commandes WHERE date_commande = '{{ ds }}'::DATE) > 0
        """,
    )

    # ---- 6. Log des métriques ----
    def logger_metriques(**context):
        print(f"Pipeline DWH terminé pour le {context['ds']}")
        print("Toutes les vérifications de qualité ont passé.")

    log_metriques = PythonOperator(
        task_id='log_metriques',
        python_callable=logger_metriques,
    )

    # ---- Dépendances ----
    creer_tables >> charger_staging >> [verifier_staging, verifier_pas_doublons]
    [verifier_staging, verifier_pas_doublons] >> transformer_dwh
    transformer_dwh >> verifier_dwh >> log_metriques
```

---

## Récupérer des résultats SQL dans Python

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator

def recuperer_et_traiter(**context):
    """
    Utiliser un Hook pour exécuter du SQL et récupérer les résultats
    dans une fonction Python.
    """
    # Le Hook est la couche basse — l'opérateur l'utilise en interne
    hook = PostgresHook(postgres_conn_id='postgres_production')

    # Méthode 1 : get_records — retourne une liste de tuples
    records = hook.get_records(
        sql="""
            SELECT client_id, SUM(montant) as total
            FROM ventes
            WHERE date_vente = %(date)s
            GROUP BY client_id
            ORDER BY total DESC
            LIMIT 10
        """,
        parameters={'date': context['ds']},
    )

    print(f"Top 10 clients du {context['ds']}:")
    for client_id, total in records:
        print(f"  Client {client_id}: {total:.2f} €")

    # Méthode 2 : get_pandas_df — retourne un DataFrame
    df = hook.get_pandas_df(
        sql="SELECT * FROM ventes WHERE date_vente = %(date)s",
        parameters={'date': context['ds']},
    )
    print(f"\nDataFrame shape: {df.shape}")
    print(df.head())

    # Méthode 3 : run — exécuter sans récupérer de résultats
    hook.run(
        sql="UPDATE ventes SET traite = TRUE WHERE date_vente = %(date)s",
        parameters={'date': context['ds']},
    )

    return len(records)  # Valeur retournée dans XCom

tache_sql_python = PythonOperator(
    task_id='recuperer_et_traiter',
    python_callable=recuperer_et_traiter,
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow montrant les logs d'une tâche `SQLCheckOperator` qui a échoué (requête retournant 0 ou False)
> **Expliquer :** Lire l'erreur dans les logs — montrer que l'opérateur lève une `AirflowException` avec le message "Test failed" quand la condition est False. Expliquer comment déboguer : aller dans Admin → Connections pour tester la connexion, puis vérifier la requête SQL directement dans psql.

---

## Points clés à retenir

1. **Toujours configurer une Connection** avant d'utiliser un opérateur SQL
2. `PostgresOperator` pour PostgreSQL, `SQLExecuteQueryOperator` pour un opérateur universel
3. Les templates Jinja `{{ ds }}` sont disponibles dans les chaînes SQL et les fichiers `.sql`
4. `SQLCheckOperator` et `SQLValueCheckOperator` pour les contrôles de qualité des données
5. Pour récupérer des résultats SQL dans Python, utiliser le **Hook** directement (`PostgresHook`)
6. L'idempotence SQL s'obtient avec `DELETE WHERE date = ...` puis `INSERT` ou `INSERT ... ON CONFLICT DO UPDATE`
