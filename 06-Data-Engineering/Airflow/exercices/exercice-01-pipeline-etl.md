# Exercice 01 — Pipeline ETL Complet

## Objectif

Construire un pipeline ETL complet qui :
1. **Extrait** des données depuis une API REST publique
2. **Transforme** les données avec pandas (nettoyage, enrichissement)
3. **Charge** les données dans PostgreSQL
4. **Valide** la qualité des données après chargement

Durée estimée : **1h30 à 2h**

---

## Contexte métier

Vous êtes Data Engineer dans une agence météorologique. Votre mission est de construire un pipeline quotidien qui :
- Récupère les données météo de 5 villes françaises depuis l'API Open-Meteo (gratuite, sans clé)
- Calcule des métriques agrégées par ville (moyenne, min, max des températures)
- Stocke les résultats dans une base PostgreSQL pour le dashboard BI
- Génère une alerte si une ville a des données manquantes

---

## Architecture cible

```
API Open-Meteo          PostgreSQL
(5 villes)               (DWH)
    │                       │
    ▼                       │
[Extraction]               │
    │                       │
    ▼                       │
[Validation]               │
    │                       │
    ▼                       │
[Transformation pandas]    │
    │                       │
    ▼                       │
[Chargement] ──────────────►
    │
    ▼
[Vérification qualité]
    │
    ▼
[Notification]
```

---

## Mise en place

### Docker Compose pour l'exercice

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
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
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
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql

  airflow-init:
    <<: *airflow-common
    command: >
      bash -c "
        airflow db init &&
        airflow users create
          --username admin --password admin
          --firstname Admin --lastname User
          --role Admin --email admin@example.com &&
        pip install requests pandas
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
```

### Script d'initialisation de la DB

```sql
-- init_db.sql

-- Schéma météo
CREATE SCHEMA IF NOT EXISTS meteo;

-- Table principale
CREATE TABLE IF NOT EXISTS meteo.mesures_journalieres (
    id              SERIAL PRIMARY KEY,
    date_mesure     DATE NOT NULL,
    ville           VARCHAR(100) NOT NULL,
    latitude        NUMERIC(8, 4) NOT NULL,
    longitude       NUMERIC(8, 4) NOT NULL,
    temp_max        NUMERIC(5, 2),
    temp_min        NUMERIC(5, 2),
    temp_moyenne    NUMERIC(5, 2),
    precipitation   NUMERIC(6, 2),
    code_meteo      INTEGER,
    qualite         VARCHAR(20) DEFAULT 'ok',
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (date_mesure, ville)
);

-- Table de métriques agrégées
CREATE TABLE IF NOT EXISTS meteo.agregats_hebdomadaires (
    id              SERIAL PRIMARY KEY,
    semaine_debut   DATE NOT NULL,
    ville           VARCHAR(100) NOT NULL,
    temp_moy_7j     NUMERIC(5, 2),
    temp_min_7j     NUMERIC(5, 2),
    temp_max_7j     NUMERIC(5, 2),
    precip_total_7j NUMERIC(7, 2),
    nb_jours_pluie  INTEGER,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE (semaine_debut, ville)
);

-- Vue pour le dashboard BI
CREATE OR REPLACE VIEW meteo.dashboard_villes AS
SELECT
    date_mesure,
    ville,
    temp_max,
    temp_min,
    temp_moyenne,
    precipitation,
    CASE
        WHEN precipitation > 10 THEN 'Pluie forte'
        WHEN precipitation > 1  THEN 'Pluie faible'
        ELSE 'Sec'
    END AS condition_pluie
FROM meteo.mesures_journalieres
ORDER BY date_mesure DESC, ville;
```

---

## Étapes de l'exercice

### Étape 1 : Créer le squelette du DAG

Créer le fichier `dags/pipeline_meteo_etl.py` avec cette structure :

```python
# dags/pipeline_meteo_etl.py

from datetime import datetime, timedelta
from airflow.decorators import dag, task

# Configuration des villes
VILLES = [
    {'nom': 'Paris',     'lat': 48.8566, 'lon': 2.3522},
    {'nom': 'Lyon',      'lat': 45.7640, 'lon': 4.8357},
    {'nom': 'Marseille', 'lat': 43.2965, 'lon': 5.3698},
    {'nom': 'Toulouse',  'lat': 43.6047, 'lon': 1.4442},
    {'nom': 'Bordeaux',  'lat': 44.8378, 'lon': -0.5792},
]

@dag(
    dag_id='pipeline_meteo_etl',
    description='Pipeline ETL météo quotidien — 5 villes françaises',
    start_date=datetime(2024, 1, 1),
    schedule='0 7 * * *',
    catchup=False,
    default_args={
        'owner': 'data-team',
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    tags=['etl', 'météo', 'exercice'],
)
def pipeline_meteo_etl():
    # TODO : implémenter les tâches
    pass

dag = pipeline_meteo_etl()
```

### Étape 2 : Implémenter la tâche d'extraction

```python
@task
def extraire_meteo(villes: list, **context) -> list[dict]:
    """
    Extrait les données météo pour chaque ville depuis l'API Open-Meteo.

    API : https://api.open-meteo.com/v1/forecast
    Paramètres utiles :
        - latitude, longitude
        - daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode
        - start_date, end_date (format YYYY-MM-DD)
        - timezone=auto
    """
    import requests

    date = context['ds']
    resultats = []

    for ville in villes:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': ville['lat'],
            'longitude': ville['lon'],
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
            'start_date': date,
            'end_date': date,
            'timezone': 'Europe/Paris',
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get('daily', {})
            if daily.get('time'):
                resultats.append({
                    'ville': ville['nom'],
                    'lat': ville['lat'],
                    'lon': ville['lon'],
                    'date': daily['time'][0],
                    'temp_max': daily.get('temperature_2m_max', [None])[0],
                    'temp_min': daily.get('temperature_2m_min', [None])[0],
                    'precipitation': daily.get('precipitation_sum', [None])[0],
                    'code_meteo': daily.get('weathercode', [None])[0],
                    'statut': 'ok',
                })
                print(f"  {ville['nom']} : OK")
            else:
                resultats.append({'ville': ville['nom'], 'statut': 'pas_de_donnees'})
                print(f"  {ville['nom']} : AUCUNE DONNÉE")

        except Exception as e:
            resultats.append({'ville': ville['nom'], 'statut': 'erreur', 'erreur': str(e)})
            print(f"  {ville['nom']} : ERREUR — {e}")

    print(f"\nExtraction terminée : {sum(1 for r in resultats if r['statut'] == 'ok')}/{len(villes)} villes OK")
    return resultats
```

### Étape 3 : Implémenter la validation

```python
@task
def valider_extraction(extraction: list[dict]) -> dict:
    """
    Vérifie que l'extraction a réussi pour au moins 80% des villes.
    Retourne un rapport de validation.
    """
    # TODO :
    # 1. Compter le nombre de villes avec statut='ok'
    # 2. Calculer le taux de succès
    # 3. Lever une ValueError si taux < 0.8 (80%)
    # 4. Retourner un dict avec le rapport de validation
    pass
```

### Étape 4 : Implémenter la transformation

```python
@task
def transformer_donnees(extraction: list[dict]) -> list[dict]:
    """
    Transforme les données brutes :
    - Calcule la température moyenne
    - Convertit le code météo en label lisible
    - Classifie la qualité de la donnée
    - Supprime les villes sans données
    """
    import pandas as pd

    # Mapping des codes météo WMO
    CODES_METEO = {
        0: 'Ciel dégagé',
        1: 'Principalement dégagé',
        2: 'Partiellement nuageux',
        3: 'Couvert',
        45: 'Brouillard',
        48: 'Brouillard givrant',
        51: 'Bruine légère',
        61: 'Pluie légère',
        63: 'Pluie modérée',
        65: 'Pluie forte',
        71: 'Neige légère',
        80: 'Averses légères',
        95: 'Orage',
        99: 'Orage violent',
    }

    # TODO :
    # 1. Filtrer uniquement les enregistrements avec statut='ok'
    # 2. Créer un DataFrame pandas
    # 3. Calculer temp_moyenne = (temp_max + temp_min) / 2
    # 4. Ajouter une colonne 'label_meteo' depuis CODES_METEO
    # 5. Ajouter une colonne 'qualite' :
    #    - 'ok' si temp_max et temp_min non nulls
    #    - 'incomplet' sinon
    # 6. Retourner la liste de dicts
    pass
```

### Étape 5 : Implémenter le chargement

```python
@task
def charger_en_postgresql(donnees: list[dict], **context) -> int:
    """
    Charge les données dans la table meteo.mesures_journalieres.
    Utilise un UPSERT (INSERT ON CONFLICT DO UPDATE) pour l'idempotence.
    """
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    # TODO :
    # 1. Créer un PostgresHook avec conn_id='postgres_default'
    # 2. Pour chaque enregistrement, exécuter un UPSERT :
    #    INSERT INTO meteo.mesures_journalieres (...) VALUES (...)
    #    ON CONFLICT (date_mesure, ville) DO UPDATE SET ...
    # 3. Retourner le nombre de lignes chargées
    pass
```

### Étape 6 : Vérification qualité post-chargement

```python
@task
def verifier_chargement(**context) -> dict:
    """
    Vérifie que les données ont bien été chargées en PostgreSQL.
    Utilise le PostgresHook pour requêter directement.
    """
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    hook = PostgresHook('postgres_default')
    date = context['ds']

    # TODO :
    # 1. Requêter le nombre de lignes pour la date du jour
    # 2. Vérifier que toutes les 5 villes sont présentes
    # 3. Requêter les statistiques (temp min/max globale)
    # 4. Retourner un dict de métriques
    pass
```

---

## Solution complète

```python
# dags/pipeline_meteo_etl_solution.py

from datetime import datetime, timedelta
from airflow.decorators import dag, task

VILLES = [
    {'nom': 'Paris',     'lat': 48.8566, 'lon': 2.3522},
    {'nom': 'Lyon',      'lat': 45.7640, 'lon': 4.8357},
    {'nom': 'Marseille', 'lat': 43.2965, 'lon': 5.3698},
    {'nom': 'Toulouse',  'lat': 43.6047, 'lon': 1.4442},
    {'nom': 'Bordeaux',  'lat': 44.8378, 'lon': -0.5792},
]

CODES_METEO = {
    0: 'Ciel dégagé', 1: 'Principalement dégagé', 2: 'Partiellement nuageux',
    3: 'Couvert', 45: 'Brouillard', 61: 'Pluie légère', 63: 'Pluie modérée',
    65: 'Pluie forte', 80: 'Averses', 95: 'Orage',
}

@dag(
    dag_id='pipeline_meteo_etl_solution',
    start_date=datetime(2024, 1, 1),
    schedule='0 7 * * *',
    catchup=False,
    default_args={'owner': 'formation', 'retries': 2, 'retry_delay': timedelta(minutes=5)},
    tags=['etl', 'météo', 'solution'],
)
def pipeline_meteo_etl_solution():

    @task
    def extraire_meteo(**context) -> list:
        import requests
        date = context['ds']
        resultats = []
        print(f"Extraction météo pour le {date}")

        for ville in VILLES:
            try:
                r = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        'latitude': ville['lat'], 'longitude': ville['lon'],
                        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
                        'start_date': date, 'end_date': date, 'timezone': 'Europe/Paris',
                    },
                    timeout=10,
                )
                r.raise_for_status()
                d = r.json().get('daily', {})
                if d.get('time'):
                    resultats.append({
                        'ville': ville['nom'], 'lat': ville['lat'], 'lon': ville['lon'],
                        'date': d['time'][0],
                        'temp_max': d.get('temperature_2m_max', [None])[0],
                        'temp_min': d.get('temperature_2m_min', [None])[0],
                        'precipitation': d.get('precipitation_sum', [None])[0],
                        'code_meteo': d.get('weathercode', [None])[0],
                        'statut': 'ok',
                    })
            except Exception as e:
                resultats.append({'ville': ville['nom'], 'statut': 'erreur', 'erreur': str(e)})

        ok = sum(1 for r in resultats if r['statut'] == 'ok')
        print(f"Extraction : {ok}/{len(VILLES)} villes OK")
        return resultats

    @task
    def valider_extraction(extraction: list) -> dict:
        ok = [r for r in extraction if r['statut'] == 'ok']
        taux = len(ok) / len(VILLES)
        print(f"Taux de succès : {taux:.0%} ({len(ok)}/{len(VILLES)})")

        if taux < 0.8:
            raise ValueError(f"Taux de succès insuffisant : {taux:.0%} < 80%")

        return {'nb_ok': len(ok), 'nb_total': len(VILLES), 'taux': taux}

    @task
    def transformer_donnees(extraction: list) -> list:
        import pandas as pd

        records = [r for r in extraction if r.get('statut') == 'ok']
        df = pd.DataFrame(records)

        df['temp_moyenne'] = (df['temp_max'] + df['temp_min']) / 2
        df['label_meteo'] = df['code_meteo'].map(CODES_METEO).fillna('Inconnu')
        df['qualite'] = df.apply(
            lambda r: 'ok' if pd.notna(r.get('temp_max')) and pd.notna(r.get('temp_min')) else 'incomplet',
            axis=1,
        )

        print(f"Transformation terminée :\n{df[['ville', 'temp_max', 'temp_min', 'temp_moyenne', 'label_meteo']].to_string(index=False)}")
        return df.to_dict('records')

    @task
    def charger_en_postgresql(donnees: list, **context) -> int:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook('postgres_default')
        nb = 0

        for d in donnees:
            hook.run("""
                INSERT INTO meteo.mesures_journalieres
                    (date_mesure, ville, latitude, longitude, temp_max, temp_min, temp_moyenne,
                     precipitation, code_meteo, qualite)
                VALUES (%(date)s, %(ville)s, %(lat)s, %(lon)s, %(temp_max)s, %(temp_min)s,
                        %(temp_moy)s, %(precip)s, %(code)s, %(qualite)s)
                ON CONFLICT (date_mesure, ville) DO UPDATE SET
                    temp_max = EXCLUDED.temp_max,
                    temp_min = EXCLUDED.temp_min,
                    temp_moyenne = EXCLUDED.temp_moyenne,
                    precipitation = EXCLUDED.precipitation,
                    qualite = EXCLUDED.qualite,
                    updated_at = NOW()
            """, parameters={
                'date': d['date'], 'ville': d['ville'],
                'lat': d['lat'], 'lon': d['lon'],
                'temp_max': d.get('temp_max'), 'temp_min': d.get('temp_min'),
                'temp_moy': d.get('temp_moyenne'), 'precip': d.get('precipitation'),
                'code': d.get('code_meteo'), 'qualite': d.get('qualite', 'ok'),
            })
            nb += 1

        print(f"{nb} lignes chargées dans meteo.mesures_journalieres")
        return nb

    @task
    def verifier_chargement(**context) -> dict:
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        hook = PostgresHook('postgres_default')
        date = context['ds']

        count = hook.get_records(
            "SELECT COUNT(*), MIN(temp_min), MAX(temp_max) FROM meteo.mesures_journalieres WHERE date_mesure = %(d)s",
            parameters={'d': date},
        )
        nb, temp_min_global, temp_max_global = count[0]

        print(f"Vérification pour le {date}:")
        print(f"  Lignes en DB : {nb}")
        print(f"  Température min globale : {temp_min_global}°C")
        print(f"  Température max globale : {temp_max_global}°C")

        assert nb == len(VILLES), f"Attendu {len(VILLES)} villes, trouvé {nb}"
        return {'nb_lignes': nb, 'temp_min': temp_min_global, 'temp_max': temp_max_global}

    @task(trigger_rule='none_failed_min_one_success')
    def rapport_final(validation: dict, nb_charges: int, verification: dict):
        print(f"""
╔══════════════════════════════════╗
║   RAPPORT PIPELINE MÉTÉO ETL    ║
╠══════════════════════════════════╣
║ Villes extraites : {validation['nb_ok']}/{validation['nb_total']}           ║
║ Lignes chargées  : {nb_charges}                   ║
║ Temp min globale : {verification.get('temp_min', 'N/A')}°C            ║
║ Temp max globale : {verification.get('temp_max', 'N/A')}°C            ║
╚══════════════════════════════════╝
        """)

    # Orchestration
    extraction = extraire_meteo()
    validation = valider_extraction(extraction)
    donnees_propres = transformer_donnees(extraction)
    nb = charger_en_postgresql(donnees_propres)
    verif = verifier_chargement()
    rapport_final(validation, nb, verif)

dag = pipeline_meteo_etl_solution()
```

---

## Questions de validation

1. Pourquoi utilise-t-on `ON CONFLICT DO UPDATE` plutôt qu'un simple `INSERT` ?
2. Que se passe-t-il si l'API retourne une erreur 503 pour 2 villes sur 5 ?
3. Comment modifier le DAG pour qu'il traite les 5 villes en parallèle avec `expand()` ?
4. Comment ajouter une alerte Slack si le taux de succès de l'extraction est inférieur à 80% ?
5. Comment tester la fonction `valider_extraction` avec pytest ?

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface Airflow montrant le DAG `pipeline_meteo_etl_solution` après une exécution réussie — vue Graph avec toutes les tâches en vert, et les logs de `charger_en_postgresql` montrant les 5 UPSERT
> **Expliquer :** Montrer comment déclencher manuellement le DAG via le bouton "Trigger DAG". Naviguer dans les logs de chaque tâche. Ouvrir `verifier_chargement` pour voir les métriques calculées. Montrer comment re-déclencher le même DAG Run plusieurs fois pour prouver l'idempotence (toujours 5 lignes en DB, pas de doublons).
