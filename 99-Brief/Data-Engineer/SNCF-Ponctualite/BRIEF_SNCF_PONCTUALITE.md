# Brief Projet Senior — Ponctualité et Perturbations du Réseau Ferroviaire SNCF en Temps Réel

> **Question centrale** : Le réseau ferroviaire tient-il ses promesses de ponctualité — quelles lignes, à quelles heures, pour quelles causes de retard — et peut-on le savoir de façon **fiable**, **fraîche** et **à moindre coût** ?

---

## Contexte métier

La SNCF transporte chaque année plus d'un milliard de voyageurs sur un réseau mêlant TGV, TER, Intercités et Transilien. La ponctualité est l'engagement contractuel le plus visible de l'opérateur : un retard supérieur à cinq minutes déclenche des droits à compensation, une dégradation mesurable de la satisfaction voyageur, et une pression régulatrice de l'ARAFER.

Pourtant, la production de la donnée de ponctualité demeure fragmentée : les horaires théoriques vivent dans des fichiers GTFS statiques publiés mensuellement, le temps réel arrive en flux GTFS-RT toutes les 30 secondes, et les causes de perturbations sont qualifiées dans l'API disruptions de Navitia avec une latence variable. Recroiser ces trois sources, les historiser fidèlement, et en extraire des indicateurs fiables à l'échelle nationale relève d'un vrai défi d'ingénierie de la donnée.

**Votre mission** : concevoir et opérer une plateforme de données de niveau production qui ingère ces flux en continu, les transforme en un entrepôt Snowflake bien modélisé, et fournit des marts analytiques permettant à n'importe quelle équipe produit ou exploitante de répondre à la question centrale — en moins d'une heure de fraîcheur, 24 h/24, 365 j/an.

---

## Sources de données réelles

### API SNCF / Navitia — flux temps réel

L'ensemble des APIs temps réel de la SNCF est exposé via le portail **Navitia** (https://doc.navitia.io/) et le portail numérique SNCF (https://numerique.sncf.com/startup/api/). L'authentification se fait par clé API en header `Authorization`.

| Endpoint | Contenu | Fréquence |
|---|---|---|
| `GET /v1/coverage/{region}/vehicle_journeys` | Positions et états des trains en circulation | ~30 s |
| `GET /v1/coverage/{region}/disruptions` | Perturbations actives : cause, lignes impactées, severity | Événementiel |
| `GET /v1/coverage/{region}/departures?from_datetime=…` | Départs temps réel par gare | À la demande |
| `GET /v1/coverage/{region}/arrivals` | Arrivées temps réel par gare | À la demande |

Le paramètre `coverage` peut prendre les valeurs `fr-idf` (Île-de-France), `fr-se` (Sud-Est), `fr-no` (Nord-Ouest), etc. La granularité géographique est au niveau ligne (`line`) et point d'arrêt (`stop_point`).

**GTFS-RT** : format binaire Protocol Buffers standardisé par Google Transit. Trois flux sont disponibles : `TripUpdates` (retards par arrêt), `VehiclePositions` (position GPS), `ServiceAlerts` (alertes). La spec complète est à https://gtfs.org/realtime/reference/.

Questions à poser dès la Phase 1 : Quelle couverture géographique en termes de régions Navitia allez-vous cibler ? Tous les types de trains (TGV, TER, Transilien) ou un sous-ensemble ? Quelles sont les contraintes de volumétrie de votre quota API ?

### GTFS statique SNCF — horaires théoriques

Disponible sur **SNCF Open Data** (https://ressources.data.sncf.com/) sous la recherche "GTFS". Le zip contient les fichiers standards : `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`, `calendar_dates.txt`. Ce référentiel est mis à jour plusieurs fois par mois lors des changements de service.

C'est la source de vérité pour le **temps théorique** : la comparaison GTFS statique vs GTFS-RT constitue le cœur du calcul de ponctualité (`délai_réel = heure_réelle_départ - heure_théorique_départ`).

### Régularité mensuelle historique (backfill)

Le jeu de données `regularite-mensuelle-tgv-aqst` (https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/) fournit les taux de régularité officiels SNCF par axe TGV, mois par mois depuis 2015. Il permet de valider les calculs temps réel agrégés contre les chiffres publiés, et de constituer un backfill historique pour les analyses de tendance.

Un jeu équivalent existe pour les TER : `regularite-mensuelle-ter`.

### Référentiel gares voyageurs

Disponible à https://ressources.data.sncf.com/explore/dataset/referentiel-gares-voyageurs/. Contient l'UIC de chaque gare, le nom commercial, la région administrative, les coordonnées GPS, la classification voyageurs (A+, A, B, C). Ce référentiel est la `dim_gare` de votre entrepôt.

---

## Architecture cible

### Vue d'ensemble

```
Sources externes
        │
        ├── GTFS-RT (TripUpdates / Alerts)  ──► Python ingestor (micro-batch 5 min)
        │                                              │
        ├── API Navitia disruptions          ──►       │
        │                                              ▼
        └── GTFS statique + référentiel  ──► Snowflake INTERNAL STAGE
                                                       │
                                               Snowpipe / Streams+Tasks
                                                       │
                                                       ▼
                                         ┌─────────────────────────┐
                                         │   BRONZE (VARIANT JSON) │
                                         │   ingestion_metadata    │
                                         └─────────────┬───────────┘
                                                       │ dbt staging
                                                       ▼
                                         ┌─────────────────────────┐
                                         │   SILVER (typé, SCD2)   │
                                         │   contrats enforced      │
                                         └─────────────┬───────────┘
                                                       │ dbt marts
                                                       ▼
                                         ┌─────────────────────────┐
                                         │   GOLD (marts métier)   │
                                         │   fact_retards, dims    │
                                         └─────────────────────────┘
                                                       │
                                               BI / Alerting

        Orchestration : Apache Airflow (micro-batch DAG toutes les 5-15 min)
        Observabilité : Elementary (dbt package)
        CI/CD         : GitHub Actions (Slim CI + dbt docs)
```

### Couche Bronze — ingestion brute idempotente

La couche Bronze stocke les données **telles que reçues**, sans transformation métier. La colonne centrale est de type `VARIANT` (JSON natif Snowflake), accompagnée de métadonnées d'ingestion immuables.

Schéma type de la table `bronze.gtfsrt_trip_updates` :

```sql
CREATE TABLE bronze.gtfsrt_trip_updates (
    _ingestion_id       VARCHAR        NOT NULL,  -- UUID généré à l'ingestion
    _ingested_at        TIMESTAMP_NTZ  NOT NULL DEFAULT SYSDATE(),
    _source             VARCHAR        NOT NULL,  -- 'navitia_fr-idf' | 'navitia_fr-se' | ...
    _batch_id           VARCHAR        NOT NULL,  -- identifiant du micro-batch Airflow
    _file_name          VARCHAR,                  -- nom du fichier dans le stage
    payload             VARIANT        NOT NULL   -- contenu brut GTFS-RT décodé en JSON
);
```

La table `bronze.disruptions` suit le même patron. La table `bronze.gtfs_static_stops` ingère les CSV GTFS ligne par ligne dans un VARIANT simplifié.

**Idempotence** : L'ingestion est idempotente sur `(_source, _batch_id)`. Un script Python qui tourne deux fois sur le même batch doit produire exactement le même état en Bronze — ni doublon, ni perte. Comment garantir cela avec un MERGE sur ces deux colonnes ?

**Snowpipe vs Streams+Tasks — arbitrage** : voir ADR-002 ci-dessous.

### Couche Silver — typage, contrats, SCD2

La couche Silver est entièrement pilotée par dbt. Chaque modèle de staging `stg_*` parse le VARIANT Bronze et applique les types stricts.

Patron de parsing VARIANT en dbt :

```sql
-- models/staging/stg_trip_updates.sql
with source as (
    select * from {{ source('bronze', 'gtfsrt_trip_updates') }}
),
parsed as (
    select
        _ingestion_id,
        _ingested_at,
        _source,
        payload:header:timestamp::timestamp_ntz         as feed_timestamp,
        entity.value:id::varchar                        as entity_id,
        entity.value:trip_update:trip:trip_id::varchar  as trip_id,
        entity.value:trip_update:trip:route_id::varchar as route_id,
        stop_seq.value:stop_id::varchar                 as stop_id,
        stop_seq.value:arrival:delay::integer           as arrival_delay_s,
        stop_seq.value:departure:delay::integer         as departure_delay_s,
        stop_seq.value:stop_sequence::integer           as stop_sequence
    from source,
         lateral flatten(input => payload:entity)          as entity,
         lateral flatten(input => entity.value:trip_update:stop_time_update) as stop_seq
)
select * from parsed
```

Quelles validations devez-vous appliquer immédiatement après le parsing ? Pensez aux nulls sur `trip_id` et `stop_id`, aux délais aberrants (> 7 200 secondes ?), aux `feed_timestamp` hors fenêtre attendue.

**Snapshots SCD Type 2 sur le référentiel gares** :

Le référentiel gares évolue : une gare change de région administrative, une ligne est renommée. Ces évolutions doivent être historisées sans écraser le passé, pour que les faits historiques conservent la bonne version de la dimension.

```yaml
# snapshots/snap_dim_gare.yml
snapshots:
  - name: snap_dim_gare
    config:
      strategy: check
      unique_key: uic_code
      check_cols:
        - nom_commercial
        - region_administrative
        - classification_voyageurs
      updated_at: _ingested_at
      invalidate_hard_deletes: true
```

Quelle est la différence entre `strategy: timestamp` et `strategy: check` ici ? Pourquoi `invalidate_hard_deletes: true` est-il important pour un référentiel de gares ?

### Couche Gold — marts analytiques

Les marts Gold sont des vues matérialisées ou des tables incrémentales dbt répondant directement aux questions métier.

**`fact_passages`** — grain : un arrêt réel d'un train dans une gare.

| Colonne | Type | Description |
|---|---|---|
| `passage_sk` | VARCHAR | Clé de substitution (hash de `trip_id + stop_id + feed_date`) |
| `trip_id` | VARCHAR | FK vers `dim_voyage` |
| `stop_id` | VARCHAR | FK vers `dim_gare` (version SCD2 active) |
| `date_sk` | DATE | FK vers `dim_temps` |
| `heure_depart_theorique` | TIME | Depuis GTFS statique |
| `heure_depart_reel` | TIME | Depuis GTFS-RT |
| `retard_depart_s` | INTEGER | Différence en secondes |
| `retard_depart_min` | NUMERIC(5,1) | Dérivé, en minutes |
| `est_en_retard` | BOOLEAN | Seuil > 5 min (TGV) ou > 3 min (RER) |
| `cause_perturbation_sk` | VARCHAR | FK vers `dim_cause` (nullable) |

**`mart_ponctualite_ligne_heure`** — grain : ligne × tranche horaire × jour.

```sql
-- Patron d'agrégation (à compléter)
select
    d.nom_ligne,
    d.type_train,
    date_trunc('hour', f.heure_depart_theorique)    as tranche_horaire,
    f.date_sk,
    count(*)                                         as nb_passages,
    count_if(f.est_en_retard)                        as nb_retards,
    avg(f.retard_depart_s) / 60.0                    as retard_moyen_min,
    percentile_cont(0.95) within group
        (order by f.retard_depart_s)                 as p95_retard_s,
    -- Taux de ponctualité : comment le calculer en tenant compte
    -- des suppressions totales de trains ?
    ...
from {{ ref('fact_passages') }} f
join {{ ref('dim_voyage') }} d using (trip_id)
group by 1, 2, 3, 4
```

**`mart_causes_perturbations`** : agrégation des `disruptions` par cause (`effect`, `severity`), ligne, période. Ce mart permet de répondre à « quelles sont les cinq causes les plus fréquentes de retard sur le TGV Paris-Lyon un vendredi soir ? ».

**`mart_comparaison_theorique_reel`** : jointure entre `fact_passages` (temps réel) et le jeu de données `regularite-mensuelle-tgv-aqst` (officiel SNCF). Quels écarts observez-vous entre votre calcul bottom-up et le chiffre publié ? Ces écarts sont-ils de l'ordre du bruit ou révèlent-ils une limite méthodologique ?

---

## Orchestration Apache Airflow

### Pourquoi Airflow plutôt qu'un scheduler simple ?

Le régime micro-batch impose des contraintes que les schedulers natifs cloud (Snowflake Tasks seules, par exemple) gèrent mal de façon intégrée :

- **Dépendances inter-tâches conditionnelles** : le `dbt run` Gold ne peut partir que si le Silver est frais ET si le volume Bronze du dernier batch dépasse un seuil minimum (sinon le feed est probablement dégradé).
- **SLA callbacks** : Airflow permet d'envoyer une alerte Slack si un DAG n'a pas terminé dans un délai configuré — indispensable pour un SLA de fraîcheur < 60 min.
- **Backfill natif** : le backfill des horaires GTFS statiques historiques (plusieurs années) et de la régularité mensuelle se lance avec `airflow dags backfill` sans modifier le code du DAG.
- **Retries exponentiels avec backoff** : si l'API Navitia est temporairement indisponible (429 / 503), Airflow retentera automatiquement avec un délai croissant.
- **Sensors** : un `S3KeySensor` ou un `SnowflakeSensor` peut faire attendre le dbt staging que le Snowpipe ait terminé d'ingérer le dernier fichier.

### DAG principal — micro-batch ingestion + transform

```python
# dags/sncf_microbatch_dag.py — structure (non exhaustif)

with DAG(
    dag_id="sncf_ponctualite_microbatch",
    schedule_interval="*/10 * * * *",   # toutes les 10 minutes
    max_active_runs=1,                   # évite les exécutions concurrentes
    sla_miss_callback=notify_slack_sla,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
    },
) as dag:

    ingest_gtfsrt = PythonOperator(
        task_id="ingest_gtfsrt_to_stage",
        python_callable=fetch_and_stage_gtfsrt,
        # Quelle information de contexte Airflow passez-vous
        # pour garantir l'idempotence du batch ?
    )

    freshness_gate = SnowflakeOperator(
        task_id="check_bronze_freshness",
        sql="""
            select iff(
                max(_ingested_at) >= dateadd('minute', -15, current_timestamp()),
                'OK', 'STALE'
            ) as status
            from bronze.gtfsrt_trip_updates
        """,
        # Comment transformez-vous ce résultat en condition bloquante ?
    )

    dbt_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command="dbt run --select staging --target prod",
    )

    dbt_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command="dbt run --select marts --target prod",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="dbt test --select marts --target prod",
    )

    ingest_gtfsrt >> freshness_gate >> dbt_silver >> dbt_gold >> dbt_test
```

### DAG backfill — GTFS statique et régularité historique

Un DAG séparé, déclenché manuellement ou une fois par mois, ingère les fichiers GTFS statiques (horaires théoriques) et les CSV de régularité historique. Son schedule est `None` (triggered uniquement). Il doit être idempotent : relancer le backfill sur une période déjà ingérée ne doit pas créer de doublons en Bronze.

Comment organisez-vous le `catchup=False` vs `catchup=True` selon le DAG ? Quels paramètres `start_date` choisissez-vous pour le DAG micro-batch vs le DAG backfill ?

### DAG disruptions — collecte événementielle

L'API `disruptions` de Navitia ne suit pas un calendrier régulier : une perturbation peut s'ouvrir et se fermer à n'importe quel moment. Un DAG cadencé à 5 min interroge l'endpoint en filtrant sur `since=<dernière_collecte>`. La logique de déduplication doit se trouver en Bronze (MERGE sur `id` de disruption) et non dans le DAG.

---

## Socle senior — six exigences de niveau production

### 1. Data contracts et évolution de schéma

Un data contract est un accord explicite entre le producteur (ingestion Python / API SNCF) et le consommateur (dbt Silver) sur la forme et la qualité de la donnée. Il est versionné en YAML au même titre que le code.

```yaml
# data_contracts/gtfsrt_trip_updates_v1.yml
contract:
  name: gtfsrt_trip_updates
  version: "1.0.0"
  owner: "equipe-data-engineering"
  sla:
    freshness_max_minutes: 15
    availability_target_pct: 99.5
  schema:
    - name: trip_id
      data_type: varchar
      nullable: false
      tests:
        - not_null
        - relationships:
            to: ref('stg_gtfs_trips')
            field: trip_id
    - name: stop_id
      data_type: varchar
      nullable: false
      tests:
        - not_null
    - name: arrival_delay_s
      data_type: integer
      nullable: true
      tests:
        - accepted_range:
            min_value: -3600
            max_value: 86400
    - name: feed_timestamp
      data_type: timestamp_ntz
      nullable: false
      tests:
        - not_null
        - dbt_utils.recency:
            datepart: minute
            interval: 30
```

Ce contrat est enforced dans dbt via `contract: enforced: true` dans le `.yml` du modèle Silver :

```yaml
models:
  - name: stg_trip_updates
    config:
      contract:
        enforced: true
    columns:
      - name: trip_id
        data_type: varchar
        constraints:
          - type: not_null
```

**Stratégie d'évolution de schéma** : L'API SNCF/Navitia fait évoluer ses réponses JSON — un nouveau champ `vehicle_descriptor.occupancy_status` apparaît dans GTFS-RT 2.0. Comment gérez-vous cela sans casser les modèles Silver existants ?

Trois scénarios à documenter dans votre ADR-003 :
- **Ajout d'un champ optionnel** : le VARIANT Bronze l'absorbe silencieusement ; le modèle Silver peut l'exposer progressivement.
- **Changement de type d'un champ existant** (`delay` passe de `integer` à `float`) : que se passe-t-il avec `contract: enforced: true` ? Comment versionnez-vous le modèle ?
- **Suppression d'un champ** : comment détectez-vous qu'un champ disparaît du flux avant que le downstream ne plante ?

### 2. Observabilité données avec Elementary

Elementary (https://docs.elementary-data.com/) s'installe comme package dbt et expose des tests d'anomalie sur volume, fraîcheur et schéma. Il génère un rapport HTML et peut pousser des alertes vers Slack.

Configuration dans `packages.yml` :

```yaml
packages:
  - package: elementary-data/elementary
    version: [">=0.14.0", "<0.15.0"]
```

Dans `dbt_project.yml`, activer le schema de résultats :

```yaml
models:
  elementary:
    +schema: elementary
```

Tests Elementary à appliquer sur les modèles Silver et Gold :

```yaml
models:
  - name: stg_trip_updates
    tests:
      - elementary.volume_anomalies:
          timestamp_column: _ingested_at
          # Une chute de volume > 50 % par rapport à la moyenne glissante
          # signale très probablement un feed GTFS-RT dégradé.
          # Comment calibrez-vous le seuil ? Quels jours/heures excluez-vous
          # (nuit, dimanche) pour éviter les faux positifs ?
      - elementary.freshness_anomalies:
          timestamp_column: feed_timestamp
      - elementary.schema_changes
  - name: fact_passages
    tests:
      - elementary.dimension_anomalies:
          dimensions:
            - type_train
          # Une disparition soudaine d'un type_train dans la fact
          # peut indiquer un problème d'ingestion partielle.
```

Le rapport Elementary doit être **publié automatiquement** à chaque run CI/CD (artifact GitHub Actions ou hébergement S3/GCS). Comment organisez-vous la rotation des rapports (rétention 30 jours) sans exploser les coûts de stockage ?

La détection d'anomalie sur une métrique métier est le test le plus puissant : si le taux moyen de retard sur la ligne Paris-Lyon dépasse 3 sigma par rapport à la distribution historique sur les 30 derniers jours, une alerte doit être déclenchée. Ce n'est pas une panne technique, c'est un signal opérationnel. Comment distinquez-vous les deux dans votre chaîne d'alerting ?

### 3. CI/CD de la donnée avec GitHub Actions

Chaque Pull Request déclenche un workflow de validation :

```yaml
# .github/workflows/ci.yml
name: dbt CI
on:
  pull_request:
    paths:
      - "dbt/**"
      - "data_contracts/**"
      - ".github/workflows/ci.yml"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SQLFluff lint
        run: sqlfluff lint dbt/models --dialect snowflake --rules L001,L010,L019,L031

  dbt-ci:
    runs-on: ubuntu-latest
    needs: lint
    env:
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
      # Jamais de secrets en clair dans le code ni dans les logs
    steps:
      - uses: actions/checkout@v4
      - name: Install dbt
        run: pip install dbt-snowflake

      - name: dbt deps
        working-directory: dbt
        run: dbt deps

      - name: Slim CI — build only modified models
        working-directory: dbt
        run: |
          dbt build \
            --select state:modified+ \
            --defer \
            --state ./prod-artifacts \
            --target ci \
            --profiles-dir .
          # Le schéma CI est isolé : DATABASE.CI_PR_${PR_NUMBER}
          # Comment nettoyez-vous ce schéma éphémère après la PR ?

      - name: Generate docs
        working-directory: dbt
        run: dbt docs generate --target ci

      - name: Upload Elementary report
        run: edr send-report --slack-token ${{ secrets.SLACK_TOKEN }}
```

**Slim CI** est le pattern le plus important pour la vélocité en équipe : `state:modified+` construit uniquement les modèles modifiés et leurs descendants, en s'appuyant sur le manifest de production (`prod-artifacts/manifest.json`). Comment maintenez-vous ce manifest à jour dans le repo sans commiter un fichier binaire de plusieurs mégaoctets à chaque run prod ?

Le déploiement en production se fait au merge sur `main` via un job séparé qui exécute `dbt build --target prod` sans le flag `--defer`.

### 4. Optimisation coût et performance Snowflake

#### Sizing et séparation des warehouses

Un entrepôt unique est un antipattern pour ce projet : les charges sont hétérogènes.

| Warehouse | Taille | Auto-suspend | Usage |
|---|---|---|---|
| `SNCF_INGEST_WH` | X-SMALL | 60 s | Snowpipe / chargement Bronze continu |
| `SNCF_TRANSFORM_WH` | SMALL | 120 s | dbt run Silver + Gold |
| `SNCF_BI_WH` | X-SMALL | 30 s | Requêtes analytiques / dashboard |

Justifiez ce choix dans votre ADR. Un X-SMALL à 1 crédit/heure coûte ~2,5x moins qu'un SMALL. Pour les dbt runs nocturnes de backfill, un MEDIUM avec auto-suspend agressif peut être plus rapide ET moins cher qu'un SMALL qui tourne longtemps — pourquoi ?

#### Clustering key sur `fact_passages`

La table `fact_passages` aura, après six mois d'ingestion, plusieurs centaines de millions de lignes. Sans clustering, une requête filtrée sur `date_sk` scannera l'intégralité de la table.

```sql
ALTER TABLE gold.fact_passages
    CLUSTER BY (date_sk, type_train);
```

Pourquoi `date_sk` en premier ? Quand le clustering automatique de Snowflake est-il préférable à un CLUSTER BY manuel ? Utilisez le **Query Profile** (onglet dans Snowflake UI) pour vérifier qu'une requête sur les 7 derniers jours effectue du partition pruning après clustering.

#### MERGE vs INSERT pour le streaming

En ingestion micro-batch, chaque run peut recevoir une mise à jour du retard d'un train déjà ingéré (le retard s'aggrave en cours de trajet). Le choix INSERT (append-only) vs MERGE (upsert) a des implications majeures :

```sql
-- Pattern MERGE pour les mises à jour de retard en Silver
MERGE INTO silver.stg_trip_updates AS target
USING (
    select
        trip_id, stop_id, feed_timestamp,
        arrival_delay_s, departure_delay_s
    from bronze.gtfsrt_trip_updates
    where _batch_id = :batch_id
) AS source
ON target.trip_id = source.trip_id
   AND target.stop_id = source.stop_id
ON MATCHED AND source.feed_timestamp > target.feed_timestamp
    THEN UPDATE SET
        arrival_delay_s   = source.arrival_delay_s,
        departure_delay_s = source.departure_delay_s,
        feed_timestamp    = source.feed_timestamp,
        _updated_at       = current_timestamp()
WHEN NOT MATCHED THEN INSERT (...) VALUES (...)
```

Un MERGE fréquent sur une grande table peut devenir coûteux. Quelle alternative dbt propose-t-elle pour les modèles incrémentaux sur Snowflake (`unique_key` + `incremental_strategy = 'merge'`) ? Quand préférer `delete+insert` ?

#### Resource monitor

```sql
CREATE RESOURCE MONITOR sncf_budget
    WITH CREDIT_QUOTA = 500  -- crédits mensuels maximum
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 90 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE SNCF_TRANSFORM_WH SET RESOURCE_MONITOR = sncf_budget;
```

Comment calibrez-vous le quota initial ? Quelles métriques Snowflake (QUERY_HISTORY, WAREHOUSE_METERING_HISTORY) utilisez-vous pour estimer la consommation hebdomadaire avant de fixer le plafond mensuel ?

### 5. SLA, monitoring et runbook

#### SLA de fraîcheur

| Couche | SLA fraîcheur | Mesure |
|---|---|---|
| Bronze (GTFS-RT) | ≤ 15 min depuis l'émission du feed | `max(feed_timestamp) >= now() - 15min` |
| Silver (passages typés) | ≤ 30 min depuis l'émission | Contrôlé par `dbt source freshness` |
| Gold (marts ponctualité) | ≤ 60 min depuis l'émission | Alerting Elementary |

Le SLA de 60 minutes en Gold impose une chaîne de bout en bout : ingestion (5 min) + Snowpipe latence (1-3 min) + dbt Silver (5-10 min) + dbt Gold (5-10 min) + tests (5 min) = marge de ~25 minutes. Cette marge est votre budget de tolérance aux incidents.

#### Alerting Airflow

```python
def notify_slack_sla(context):
    """Callback déclenché si le DAG dépasse son SLA."""
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    # Construire le payload Slack Blocks et appeler le webhook
    # Comment incluez-vous le lien vers le log Airflow dans l'alerte ?
```

#### RUNBOOK.md — Incidents types

Votre `RUNBOOK.md` doit être consultable par une personne d'astreinte sans accès au code. Il documente au minimum :

**Incident 1 — Feed GTFS-RT manquant ou en retard**

- **Détection** : alerte Elementary `freshness_anomalies` ou callback SLA Airflow. Le dashboard Slack indique "Bronze stale depuis N minutes".
- **Diagnostic** :
  1. Vérifier le statut de l'API Navitia : https://status.navitia.io/
  2. Inspecter les logs du DAG Airflow : tâche `ingest_gtfsrt_to_stage` en erreur ?
  3. Contrôler le quota API (header `X-RateLimit-Remaining` dans les logs Python).
  4. Requête Snowflake : `SELECT max(_ingested_at), count(*) FROM bronze.gtfsrt_trip_updates WHERE _ingested_at > dateadd('hour', -2, current_timestamp())`.
- **Remédiation** :
  - Si erreur 429 (rate limit) : réduire la fréquence du DAG de 10 min à 15 min via variable Airflow.
  - Si erreur 5xx Navitia : attendre la récupération, le DAG retentera automatiquement (3 retries exp.). Vérifier que `max_active_runs=1` évite l'accumulation.
  - Si quota épuisé : contacter l'équipe pour demander une augmentation ou basculer sur un endpoint secondaire.
- **Impact SLA** : un feed manquant de < 30 min ne dégrade pas les marts (données en cache). Au-delà, les marts sont marqués "stale" dans Elementary.

**Incident 2 — Explosion anormale du taux de retard**

- **Détection** : test Elementary `volume_anomalies` sur `fact_passages.est_en_retard` dépasse 3 sigma. Alerte Slack "Anomalie taux retard détectée".
- **Diagnostic** :
  1. L'anomalie est-elle réelle ou liée à un artefact de données ? Vérifier `mart_comparaison_theorique_reel` : l'écart avec les données officielles SNCF est-il cohérent ?
  2. Contrôler la fraîcheur du GTFS statique : une mise à jour de grille horaire non encore ingérée crée une désynchronisation théorique/réel.
  3. Vérifier l'absence de doublon en Bronze sur le dernier batch (`_batch_id`).
  4. Croiser avec les disruptions actives : une grève ou un incident infrastructure justifie-t-il le pic ?
- **Remédiation** :
  - Si artefact (doublon) : supprimer les doublons Bronze et relancer dbt avec `--full-refresh` sur les modèles Silver concernés.
  - Si GTFS statique désynchronisé : déclencher manuellement le DAG de backfill GTFS.
  - Si événement réel (grève) : annoter le rapport Elementary avec une note contextuelle et ne pas désactiver l'alerte.

### 6. Décisions d'architecture (ADR)

Les ADR (Architecture Decision Records) formalisent les choix techniques importants au format MADR léger. Ils vivent dans `docs/adr/`.

#### ADR-001 — Streaming continu vs micro-batch

```markdown
# ADR-001 : Micro-batch toutes les 10 minutes vs streaming continu

## Contexte
Le flux GTFS-RT est émis toutes les 30 secondes. Les marts analytiques
alimentent des dashboards rafraîchis à la minute. Le budget crédits
Snowflake est contraint. L'équipe maîtrise Python et Airflow ; Kafka
n'est pas encore dans le stack.

## Décision
Micro-batch toutes les 10 minutes via Airflow + Snowpipe.

## Alternatives considérées
- **Streaming continu Kafka→Snowflake (Kafka Connector)** : latence < 30 s,
  mais complexité opérationnelle élevée, coût Snowpipe streaming > classique.
- **Streaming natif Snowflake (Snowpipe Streaming API)** : latence < 1 min,
  SDK Python disponible. Retenu comme évolution future (voir "Pour aller plus loin").
- **Polling pur sans Snowpipe (INSERT direct chaque 30 s)** : charge trop
  élevée sur les micro-transactions Snowflake.

## Conséquences
- SLA fraîcheur Gold ≤ 60 min : tenable.
- Simplification opérationnelle : un seul outil d'orchestration (Airflow).
- Limitation : un incident de 15 min de l'API n'est pas détecté en temps réel,
  mais rattrapé au batch suivant.
```

#### ADR-002 — Snowpipe vs Streams+Tasks pour l'auto-ingest

```markdown
# ADR-002 : Snowpipe auto-ingest vs Streams+Tasks

## Contexte
Les fichiers JSON produits par le script Python sont déposés dans un
stage Snowflake interne. L'ingestion en table Bronze doit être déclenchée
automatiquement à l'arrivée du fichier.

## Décision
Snowpipe avec notification event (ou polling) pour l'ingestion Bronze.
Streams+Tasks pour la propagation Silver (consommation du stream Bronze).

## Justification
Snowpipe est conçu pour l'ingest de fichiers en quasi-temps réel avec
une latence de quelques secondes à quelques minutes. Il est managé,
sans infra à opérer. Streams+Tasks est plus approprié pour les
transformations continues sur des tables déjà ingérées.

## Alternatives
- **COPY INTO schedulé** : simple, mais latence = fréquence du schedule.
- **Snowpipe Streaming (SDK)** : pas de passage par fichier, idéal pour
  le streaming pur — évolution cible.

## Conséquences
Deux mécanismes à monitorer : Snowpipe (via SYSTEM$PIPE_STATUS) et
les Tasks (via TASK_HISTORY). La complexité opérationnelle est faible
mais la surface de surveillance est doublée.
```

#### ADR-003 — Enforcement des data contracts

```markdown
# ADR-003 : Contrats bloquants vs avertissements non-bloquants

## Contexte
Les tests dbt sur les données SNCF échouent parfois sur des anomalies
transitoires (train annulé sans disruption correspondante, `stop_id`
temporairement absent du référentiel). Un mode tout-bloquant arrêterait
le pipeline plusieurs fois par jour.

## Décision
Deux niveaux d'enforcement :
- **Bloquant (severity: error)** : nulls sur `trip_id`, `stop_id`,
  `feed_timestamp` ; doublons sur la clé naturelle ; timestamps futurs.
- **Avertissement (severity: warn)** : retards > 2 heures, `stop_id`
  absent du référentiel (couverture incomplète possible), volume < 80 %
  de la moyenne.

## Conséquences
Le pipeline ne s'arrête pas sur un arrêt annulé sans référence.
Les anomalies warn remontent dans Elementary sans bloquer les marts.
La revue hebdomadaire des warns permet d'ajuster les seuils.
```

---

## Phases du projet

### Phase 1 — Cadrage, sources et contrats (J1-J2)

Cette phase ne contient pas une ligne de code de pipeline. Elle conditionne la qualité de tout ce qui suit.

**J1 — Exploration et documentation des sources**

Créez un compte sur le portail Navitia (https://doc.navitia.io/#getting-started), obtenez une clé API, et interrogez manuellement les endpoints suivants avec `curl` ou Postman :
- `GET /v1/coverage/` — lister les régions disponibles
- `GET /v1/coverage/fr-idf/disruptions?since=<iso8601>&count=10` — observer la structure d'une disruption
- `GET /v1/coverage/fr-idf/vehicle_journeys?since=<iso8601>` — observer un TripUpdate

Documentez dans un fichier `docs/sources.md` : format de réponse, volumétrie estimée (nb d'entités par appel, nb d'appels par heure dans les limites du quota), champs disponibles vs champs utiles, limites connues (coverage géographique, latence de publication, champs nullable).

Téléchargez le GTFS statique SNCF et analysez les fichiers CSV : combien de `trips` ? Combien de `stop_times` ? Quelle est la fréquence de mise à jour du zip (date dans le nom de fichier) ?

**J2 — Contrats, architecture et Kanban**

Rédigez les data contracts YAML pour les trois sources principales (GTFS-RT trip_updates, disruptions, GTFS statique stops). Posez l'ADR-001 (streaming vs micro-batch). Construisez le schéma d'architecture (draw.io ou Excalidraw, exporté en PNG dans `docs/architecture.png`). Initialisez le Kanban (GitHub Projects ou Notion) avec les user stories par phase.

Livrable de validation : le schéma d'architecture relu et validé par le formateur avant de passer à la Phase 2.

### Phase 2 — Ingestion temps réel Bronze (J3-J5)

**J3 — Script d'ingestion Python**

Implémentez `ingestion/fetch_gtfsrt.py` : appel à l'API Navitia, parsing du binaire GTFS-RT (librairie `google.transit.gtfs_realtime_pb2`), sérialisation en JSON, écriture dans le stage Snowflake interne via le connecteur Python Snowflake. Gérez l'authentification par variable d'environnement (jamais de clé en dur). Implémentez les retries avec `tenacity`.

Questions à résoudre : comment nommez-vous les fichiers dans le stage pour garantir l'idempotence ? (`{source}_{batch_id}_{timestamp}.json` ?) Comment gérez-vous le cas où l'API renvoie un flux vide (pas de trains en circulation la nuit) ?

**J4 — Snowpipe et table Bronze**

Créez le stage interne, la table Bronze avec le schéma VARIANT défini plus haut, le pipe Snowpipe. Vérifiez le fonctionnement avec `SYSTEM$PIPE_STATUS` et `COPY_HISTORY`. Testez l'idempotence : re-déposez le même fichier, vérifiez qu'il n'y a pas de doublon (le pipe ignore les fichiers déjà traités).

**J5 — DAG Airflow micro-batch**

Implémentez le DAG `sncf_ponctualite_microbatch` avec les quatre tâches de la structure décrite plus haut. Testez le `freshness_gate` : forcez un état stale en arrêtant l'ingestion 20 minutes, vérifiez que le DAG ne fait pas partir `dbt_silver`.

### Phase 3 — Silver, contrats et SCD2 (J6-J8)

**J6 — Modèles dbt staging**

Créez `models/staging/stg_trip_updates.sql` avec le parsing VARIANT complet. Ajoutez les tests dbt standard (not_null, unique sur la clé naturelle, relationships vers stg_gtfs_stops). Activez `contract: enforced: true`. Configurez `dbt source freshness` avec `warn_after: {count: 20, period: minute}` et `error_after: {count: 30, period: minute}`.

**J7 — Snapshots SCD2**

Implémentez `snapshots/snap_dim_gare.sql`. Testez l'évolution : modifiez manuellement une ligne dans la table source du référentiel gares, relancez `dbt snapshot`, vérifiez que l'ancienne version est conservée avec `dbt_valid_to` non null et la nouvelle version insérée avec `dbt_valid_to` null.

**J8 — Gestion de l'évolution de schéma**

Simulez les trois scénarios de l'ADR-003 : ajout de champ, changement de type, suppression. Documentez les résultats observés et les actions correctives. Ajoutez un test Elementary `schema_changes` sur les modèles Silver.

### Phase 4 — Gold : marts ponctualité (J9-J10)

**J9 — Modèles incrémentaux fact et dims**

Implémentez `fact_passages` en modèle dbt incrémental (`materialized: incremental`, `unique_key: passage_sk`, `incremental_strategy: merge`). Assurez-vous que le calcul `retard_depart_s = heure_depart_reel - heure_depart_theorique` est correct même quand les deux timestamps ne sont pas dans le même fuseau horaire (GTFS-RT est en UTC ; les horaires GTFS statiques sont en heure locale — attention au DST).

**J10 — Marts analytiques**

Implémentez `mart_ponctualite_ligne_heure`, `mart_causes_perturbations`, `mart_comparaison_theorique_reel`. Pour ce dernier, croisez vos données avec le CSV de régularité mensuelle SNCF. Les écarts sont-ils < 1 point de pourcentage ? Sinon, quelle méthodologie différente applique la SNCF dans son calcul officiel ?

### Phase 5 — Observabilité, CI/CD, coût et SLA (J11-J13)

**J11 — Elementary et alerting**

Installez le package Elementary, configurez les tests d'anomalie sur les modèles clés, publiez le premier rapport. Configurez les webhooks Slack pour les alertes d'anomalie. Vérifiez que le rapport est généré et accessible après chaque `dbt run` en CI.

**J12 — GitHub Actions Slim CI**

Implémentez `.github/workflows/ci.yml` complet avec lint, dbt build Slim CI sur schéma éphémère, publication du rapport Elementary. Testez en ouvrant une PR factice. Vérifiez que `state:modified+` ne rebuilde que les modèles touchés.

**J13 — Cost-opt, clustering, RUNBOOK et SLA**

Configurez les resource monitors, ajoutez le clustering key sur `fact_passages`, analysez une requête lente avec Query Profile. Rédigez `RUNBOOK.md` avec les deux incidents types documentés. Préparez la démonstration : pipeline qui tourne en live, fresshness dashboard Elementary, marts interrogeables.

---

## Modalités d'évaluation

### Démonstration technique — 60 %

Le pipeline doit être en fonctionnement au moment de la démo. L'évaluateur pose trois questions en live :

1. "Montrez-moi le taux de ponctualité sur la ligne Paris-Lyon pour les 7 derniers jours, réparti par tranche horaire."
2. "Déclenchez une alerte de fraîcheur : arrêtez l'ingestion, attendez 20 minutes, montrez l'alerte dans Slack."
3. "Combien de crédits Snowflake votre pipeline a-t-il consommé cette semaine ? Décomposez par warehouse."

### Revue d'architecture et de code — 40 %

#### Bloc 1 — Ingestion temps réel et Bronze

| Critère | Validation |
|---|---|
| Script Python idempotent sur re-run même batch | OUI / NON |
| Snowpipe fonctionnel, latence < 5 min mesurée | OUI / NON |
| Métadonnées d'ingestion présentes et correctes (`_batch_id`, `_ingested_at`) | OUI / NON |
| DAG Airflow avec freshness gate opérationnel | OUI / NON |

#### Bloc 2 — Modélisation et SCD2

| Critère | Validation |
|---|---|
| Parsing VARIANT Silver correct (au moins 3 champs typés vérifiés en live) | OUI / NON |
| Snapshot SCD2 gares : historique préservé après modification d'une ligne | OUI / NON |
| `fact_passages` : grain correct, clé naturelle sans doublon | OUI / NON |
| Mart ponctualité : résultats cohérents avec régularité officielle SNCF (± 2 pp) | OUI / NON |

#### Bloc 3 — Data contracts et qualité

| Critère | Validation |
|---|---|
| Contrats YAML versionnés, au moins 2 sources documentées | OUI / NON |
| `contract: enforced: true` sur au moins un modèle Silver, test bloquant démontré | OUI / NON |
| `dbt source freshness` configuré et reporté | OUI / NON |
| Stratégie d'évolution de schéma documentée (ADR-003) | OUI / NON |

#### Bloc 4 — Observabilité et CI/CD

| Critère | Validation |
|---|---|
| Rapport Elementary publié, tests volume/freshness/schema présents | OUI / NON |
| Alerte Slack déclenchée sur anomalie fraîcheur (démo live) | OUI / NON |
| GitHub Actions CI vert sur une PR de démonstration | OUI / NON |
| Slim CI (`state:modified+`) documenté et opérationnel | OUI / NON |

#### Bloc 5 — Coût et exploitation

| Critère | Validation |
|---|---|
| 3 warehouses distincts avec auto-suspend configuré | OUI / NON |
| Resource monitor actif, budget crédits défini | OUI / NON |
| Clustering key sur `fact_passages`, Query Profile analysé | OUI / NON |
| `RUNBOOK.md` avec 2 incidents documentés, consultable sans accès au code | OUI / NON |

**Clause de validation partielle** : un pipeline non parfaitement fonctionnel en démo ne disqualifie pas automatiquement. Si les blocs 2, 3 et 5 (architecture, contrats, runbook) sont solides et documentés, la validation partielle est accordée sur les blocs non démontrés, sous réserve que le code existe et que les choix d'architecture soient défendus à l'oral.

---

## Livrables

### Repo GitHub public

```
sncf-ponctualite-data-platform/
├── README.md                        # Description, stack, install, archi, auteur
├── RUNBOOK.md                       # Runbook opérationnel
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml                 # dbt-utils, elementary, dbt_expectations
│   ├── profiles.yml.example         # Sans secrets
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_trip_updates.sql
│   │   │   ├── stg_disruptions.sql
│   │   │   ├── stg_gtfs_stops.sql
│   │   │   └── stg_gtfs_trips.sql
│   │   ├── intermediate/
│   │   │   └── int_passages_enrichis.sql
│   │   └── marts/
│   │       ├── fact_passages.sql
│   │       ├── dim_gare.sql
│   │       ├── dim_voyage.sql
│   │       ├── dim_cause_perturbation.sql
│   │       ├── mart_ponctualite_ligne_heure.sql
│   │       ├── mart_causes_perturbations.sql
│   │       └── mart_comparaison_theorique_reel.sql
│   ├── snapshots/
│   │   └── snap_dim_gare.sql
│   └── tests/
│       └── generic/
├── airflow/
│   └── dags/
│       ├── sncf_microbatch_dag.py
│       ├── sncf_backfill_gtfs_dag.py
│       └── sncf_disruptions_dag.py
├── ingestion/
│   ├── fetch_gtfsrt.py
│   ├── fetch_disruptions.py
│   ├── load_gtfs_static.py
│   └── requirements.txt
├── data_contracts/
│   ├── gtfsrt_trip_updates_v1.yml
│   ├── disruptions_v1.yml
│   └── gtfs_static_v1.yml
├── docs/
│   ├── adr/
│   │   ├── ADR-001-streaming-vs-microbatch.md
│   │   ├── ADR-002-snowpipe-vs-streams-tasks.md
│   │   └── ADR-003-contract-enforcement.md
│   ├── sources.md
│   └── architecture.png
└── .github/
    └── workflows/
        ├── ci.yml
        └── deploy.yml
```

### Non-code

- Schéma d'architecture exporté en PNG (draw.io / Excalidraw)
- Tableau Kanban avec user stories par phase (GitHub Projects ou Notion, lien dans le README)
- Rapport Elementary HTML (lien public S3 ou GitHub Pages)
- Dashboard Snowflake : capture d'écran du Credit Usage par warehouse sur la durée du projet

---

## Ressources

### APIs et données

- Portail API SNCF : https://numerique.sncf.com/startup/api/
- Documentation Navitia : https://doc.navitia.io/
- Spécification GTFS-RT : https://gtfs.org/realtime/reference/
- SNCF Open Data — GTFS statique : https://ressources.data.sncf.com/explore/dataset/sncf-transilien-gtfs-rt/
- Régularité mensuelle TGV : https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/
- Régularité mensuelle TER : https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-ter/
- Référentiel gares voyageurs : https://ressources.data.sncf.com/explore/dataset/referentiel-gares-voyageurs/

### Snowflake

- Snowpipe : https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto
- Snowpipe Streaming (SDK) : https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-overview
- Streams & Tasks : https://docs.snowflake.com/en/user-guide/streams-intro
- Dynamic Tables : https://docs.snowflake.com/en/user-guide/dynamic-tables-intro
- Resource Monitors : https://docs.snowflake.com/en/user-guide/resource-monitors
- Query Profile : https://docs.snowflake.com/en/user-guide/ui-query-profile
- Clustering : https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions

### dbt

- Source freshness : https://docs.getdbt.com/docs/build/sources#snapshotting-source-data-freshness
- Snapshots (SCD2) : https://docs.getdbt.com/docs/build/snapshots
- Model contracts : https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- Incremental models : https://docs.getdbt.com/docs/build/incremental-models

### Elementary

- Documentation : https://docs.elementary-data.com/
- Anomaly detection tests : https://docs.elementary-data.com/data-tests/anomaly-detection
- Slack alerts : https://docs.elementary-data.com/oss/deployment-and-configuration/slack

### Airflow

- Documentation : https://airflow.apache.org/docs/
- SLA callbacks : https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html#sla-misses
- Sensors : https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html

### GitHub Actions

- Actions marketplace : https://github.com/marketplace/actions
- SQLFluff : https://docs.sqlfluff.com/en/stable/

---

## Pour aller plus loin (senior)

Ces pistes ne sont pas dans le scope du brief mais constituent la feuille de route naturelle pour une plateforme de niveau entreprise :

**Kafka vers Snowflake** : remplacer le micro-batch Airflow par un producteur Kafka (ou Confluent Cloud) qui publie les messages GTFS-RT au fil de l'eau, et le Kafka Connect Snowflake Sink qui les consomme en continu via Snowpipe Streaming. La latence Bronze passe de ~10 min à ~30 secondes.

**dbt Exposures et lineage** : déclarez dans `exposures.yml` les dashboards BI et les APIs qui consomment vos marts Gold. dbt docs génère alors un graphe de lineage bout en bout (source API → Gold → dashboard) qui facilite l'impact analysis lors des évolutions de schéma.

**Détection d'anomalie ML sur les retards** : entraîner un modèle de séries temporelles (Prophet, SARIMA ou Isolation Forest) sur l'historique des taux de retard par ligne/heure pour distinguer les anomalies structurelles (dégradation chronique d'une ligne) des pics conjoncturels (incident ponctuel, grève). Ce modèle peut être invoké directement depuis Snowpark (Python in Snowflake).

**Blue/green des modèles dbt** : pour les marts à forte audience, éviter le downtime lors des `dbt run --full-refresh` en appliquant le pattern blue/green : construire la nouvelle version du modèle dans un schéma `_next`, permuter l'alias à la fin, supprimer l'ancien. Snowflake's `SWAP WITH` rend cette opération atomique.

**Data mesh et ownership distribué** : si le projet s'étend à d'autres domaines (infrastructure, matériel roulant, commercial), structurer le repo dbt en domaines avec des owners distincts, et exposer les marts via dbt Semantic Layer pour une consommation self-service sans dépendance à l'équipe Data Engineering.
