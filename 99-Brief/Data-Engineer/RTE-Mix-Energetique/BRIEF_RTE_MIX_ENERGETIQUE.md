# Brief Projet Senior — Mix Électrique Français : Séries Temporelles, Empreinte Carbone et Optimisation de Coût

## Domaine : Énergie / Données publiques RTE · Stack : Snowflake + dbt Core + Dagster + Elementary + GitHub Actions

---

## Question centrale

> Comment évolue le mix électrique français — part des renouvelables, empreinte carbone au kWh, saisonnalité — et peut-on modéliser un historique long de séries temporelles de façon fiable, incrémentale et optimisée en coût ?

Cette question drive toutes les décisions d'architecture du projet : choix des matérialisations, granularité du partitionnement, stratégie de backfill, réglage du `TARGET_LAG`, et emplacement des data contracts.

---

## Contexte métier

RTE (Réseau de Transport d'Électricité) publie en open data, via le dispositif éCO2mix, les données de production et consommation électrique de la France à une granularité de 15 minutes. Ces données couvrent l'ensemble des filières de production (nucléaire, hydraulique, éolien terrestre, éolien offshore, solaire, gaz, fioul, charbon, bioénergies), les échanges transfrontaliers et le taux d'émission de CO2 marginal du réseau.

L'enjeu de ce projet n'est pas d'ingérer quelques jours de données en temps réel — c'est de construire une plateforme analytique capable de :

- traiter plusieurs **années d'historique** (backfill) en mode batch quotidien idempotent,
- maintenir des **séries temporelles longues** sans trou ni doublon,
- exposer des **marts analytiques fiables** sur la saisonnalité, les tendances EnR, l'intensité carbone et la corrélation consommation/température,
- offrir une observabilité fine du pipeline et un **SLA de fraîcheur explicite**,
- maîtriser le coût Snowflake sur un historique qui peut dépasser 5 millions de lignes à granularité 15 min.

---

## Sources de données (APIs live)

### ODRÉ — Open Data Réseaux Énergies (éCO2mix)

URL portail : https://odre.opendatasoft.com/

L'API utilisée est l'**Opendatasoft Explore API v2**. Trois jeux de données sont pertinents :

| Jeu de données | Identifiant ODS | Usage |
|---|---|---|
| éCO2mix national temps réel | `eco2mix-national-tr` | Données J du jour (non consolidées) |
| éCO2mix national consolidé | `eco2mix-national-cons-def` | Données définitives (J-2 à J-365) — **source principale historique** |
| éCO2mix régional temps réel | `eco2mix-regional-tr` | Décomposition par région administrative |

Endpoint Explore v2 (exemple national consolidé) :

```
GET https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/records
    ?select=date_heure,consommation,nucleaire,eolien,solaire,hydraulique,bioenergies,
            gaz,fioul,charbon,pompage,ech_physiques,taux_co2
    &where=date_heure >= "2024-01-01T00:00:00+01:00"
    &order_by=date_heure ASC
    &limit=100
    &offset=0
```

L'API est publique, sans authentification, mais paginée. La volumétrie est d'environ 35 000 enregistrements par an (96 mesures × 365 jours) pour le jeu national consolidé.

> Questions guidantes : Quelle stratégie de pagination allez-vous adopter ? Comment gérez-vous le fuseau horaire (Europe/Paris, heure d'été/hiver) lors de l'ingestion pour éviter les doublons sur les changements d'heure ? Comment détectez-vous une réponse partielle (timeout réseau) pour déclencher une reprise ?

### Portail RTE Data (APIs OAuth2)

URL portail : https://data.rte-france.com/

Les APIs RTE nécessitent une authentification OAuth2 (client credentials). Deux endpoints complémentaires aux données ODRÉ :

| API RTE | Endpoint | Données |
|---|---|---|
| Actual Generation | `/open_api/actual_generation/v1/actual_generations_per_production_type` | Production par filière, par pas de 30 min |
| Consumption | `/open_api/consumption/v1/short_term` | Consommation réalisée et prévisions |

L'API RTE offre un niveau de détail supplémentaire (sous-filières hydrauliques, TAC) utile pour enrichir les marts Gold. L'authentification OAuth2 impose de gérer le cycle de vie du token (expiration 3600 s) dans votre script d'ingestion.

> Questions guidantes : Comment stockez-vous le `client_secret` RTE de façon sécurisée dans vos assets Dagster (ne jamais en clair dans le code) ? Comment gérez-vous la rotation du token sans bloquer le pipeline ?

### Météo — Open-Meteo (corrélation consommation/température)

URL : https://open-meteo.com/

API gratuite, sans clé, archive historique disponible :

```
GET https://archive-api.open-meteo.com/v1/archive
    ?latitude=48.85&longitude=2.35
    &start_date=2020-01-01&end_date=2024-12-31
    &daily=temperature_2m_mean,temperature_2m_min,temperature_2m_max
    &timezone=Europe/Paris
```

La corrélation température/consommation est un enrichissement Gold (ASOF JOIN Snowflake). Pour un pipeline senior, on récupère cette donnée une fois par jour en complément des données RTE.

---

## Architecture cible

### Vue d'ensemble — Médaillon sur Snowflake

```
┌──────────────────────────────────────────────────────────────────┐
│  SOURCES EXTERNES                                                │
│  ODRÉ Explore API v2  ·  RTE APIs OAuth2  ·  Open-Meteo         │
└───────────────────────────┬──────────────────────────────────────┘
                            │ Python ingestion scripts
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  BRONZE  (schema: RTE_BRONZE)                                    │
│  Tables brutes partitionnées par date · idempotentes             │
│  Assets Dagster partitionnés (DailyPartitionsDefinition)         │
│  Backfill d'historique via UI Dagster ou CLI                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │ dbt staging + incremental
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  SILVER  (schema: RTE_SILVER)                                    │
│  Modèles incrémentaux dbt · dim_temps · dim_filiere              │
│  dbt snapshots (SCD2) · data contracts enforced                  │
│  Tests de fraîcheur · bornes physiques par filière               │
└───────────────────────────┬──────────────────────────────────────┘
                            │ dbt marts
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  GOLD  (schema: RTE_GOLD)                                        │
│  mart_mix_quotidien · mart_enr_share · mart_co2_intensite        │
│  mart_saisonnalite · mart_meteo_conso (ASOF JOIN)                │
│  Dynamic tables (agrégations incrémentales, TARGET_LAG réglé)   │
│  Prévision consommation (Snowflake Cortex ML / SQL windowed)     │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION  Dagster (software-defined assets)                │
│  Asset graph · partitions temporelles · asset checks             │
│  Schedules quotidiens · backfill UI natif · lineage complet      │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│  OBSERVABILITÉ  Elementary · Dagster asset checks                │
│  GitHub Actions CI/CD (lint, dbt build slim, docs)               │
│  RUNBOOK.md · SLA de fraîcheur · alerting Slack                  │
└──────────────────────────────────────────────────────────────────┘
```

### Nommage des objets Snowflake

Adoptez une convention explicite dès le départ ; elle sera auditée en revue de code :

```
DATABASE : RTE_MIX_PROD
  SCHEMA  : RTE_BRONZE   → tables brutes + stages
  SCHEMA  : RTE_SILVER   → modèles dbt incrémentaux, dimensions, snapshots
  SCHEMA  : RTE_GOLD     → marts + dynamic tables
  SCHEMA  : RTE_METRICS  → résultats Elementary + audit logs
```

---

## Phase 1 — Cadrage, sources & contrats (J1-J2)

**Aucun pipeline ne s'écrit en Phase 1.** L'objectif est de produire les documents qui guident toute l'implémentation.

### Exploration des sources

Avant d'écrire une ligne de code, explorez manuellement les APIs :

- Interrogez `eco2mix-national-cons-def` pour une semaine complète. Comptez les enregistrements : obtenez-vous bien 96 × 7 = 672 lignes ? Y a-t-il des créneaux manquants ?
- Identifiez les colonnes nulles systématiques (certaines sous-filières hydrauliques ne sont pas toujours renseignées) et documentez-les dans le data contract.
- Testez le comportement de l'API sur un changement d'heure (dernier dimanche d'octobre 2023 : le créneau 2h00–3h00 est dupliqué en UTC±1 → UTC+1). Comment l'API renvoie-t-elle ces créneaux ? Comment votre pipeline les déduplique-t-il ?
- Vérifiez les plages physiques des colonnes : la colonne `taux_co2` est-elle toujours entre 20 et 500 g/kWh ? La production `nucleaire` est-elle toujours positive ? Y a-t-il des valeurs négatives pour `pompage` (normale) ou `solaire` (aberrante) ?

### Schéma d'architecture

Produisez un diagramme (draw.io, Mermaid ou équivalent) couvrant : les sources, les trois couches médaillon, les assets Dagster principaux, les jobs et schedules, les flux de données CI/CD.

### Dimension temps

La dimension temps est la colonne vertébrale de toute série temporelle. Définissez-la dès la Phase 1 :

```sql
-- Pattern de la dimension temps (à implémenter en dbt seed ou dbt model)
-- Couvre la granularité 15 min ET le grain quotidien
-- Colonnes attendues (non exhaustif) :
--   time_id TIMESTAMP_TZ   -- clé primaire, UTC
--   date_local DATE         -- date en Europe/Paris
--   hour_local INTEGER
--   quarter_hour INTEGER    -- 0, 15, 30, 45
--   day_of_week INTEGER
--   week_number INTEGER
--   month INTEGER
--   year INTEGER
--   is_weekend BOOLEAN
--   is_bank_holiday BOOLEAN -- jours fériés France
--   season VARCHAR          -- 'hiver','printemps','été','automne'
```

> Question guidante : Pourquoi est-il préférable de matérialiser `dim_temps` comme un modèle dbt `table` et non `view` ? Quelle est la borne temporelle de cette dimension ? Comment la prolongez-vous sans rebuild complet ?

### Kanban initial

Traduisez les livrables par phase en tickets Kanban (GitHub Projects ou équivalent) avec des critères d'acceptation mesurables. Chaque ticket de pipeline doit mentionner : la source concernée, le schéma Snowflake cible, la partition concernée, et la condition d'idempotence.

---

## Phase 2 — Ingestion batch + backfill Bronze (J3-J5)

### Assets Dagster partitionnés

Dagster est choisi ici pour sa capacité native à modéliser un historique long comme un ensemble de **partitions matérialisables individuellement**. Chaque jour d'historique est une partition ; le backfill consiste à matérialiser les partitions manquantes, avec reprise possible en cas d'échec partiel.

Structure d'asset recommandée (pattern, pas solution complète) :

```python
from dagster import asset, DailyPartitionsDefinition, AssetExecutionContext

# Définition des partitions journalières depuis le début de l'historique
daily_partitions = DailyPartitionsDefinition(start_date="2018-01-01")

@asset(
    partitions_def=daily_partitions,
    group_name="bronze",
    # metadata déclarative : source, SLA, owner
)
def bronze_eco2mix_national(context: AssetExecutionContext):
    partition_date = context.partition_key  # "2024-03-15"
    # Votre logique d'ingestion ici
    # 1. Construire l'URL API avec le filtre date_heure pour cette partition
    # 2. Paginer la réponse jusqu'à épuisement (limit/offset)
    # 3. Écrire en Snowflake (MERGE ou INSERT OVERWRITE sur la partition)
    # 4. Logger le nombre de lignes ingérées dans context.add_output_metadata
    ...
```

> Questions guidantes : Comment rendez-vous cet asset **idempotent** — c'est-à-dire, comment garantissez-vous qu'exécuter deux fois le même asset pour la même partition produit exactement le même résultat en base ? Utilisez-vous un `DELETE WHERE date = partition_date` avant l'INSERT, ou un MERGE, ou une autre approche ? Quels sont les trade-offs de chaque option sur Snowflake (coût des micro-partitions, Time Travel) ?

### Ingestion Python — structure recommandée

```
ingestion/
├── connectors/
│   ├── odre_client.py       # Client ODRÉ (Explore API v2, pagination)
│   ├── rte_client.py        # Client RTE (OAuth2, gestion token)
│   └── meteo_client.py      # Client Open-Meteo (archive)
├── loaders/
│   └── snowflake_loader.py  # Chargement Snowflake via connecteur Python
├── assets/
│   ├── bronze_eco2mix.py    # Assets Dagster Bronze national
│   ├── bronze_eco2mix_regional.py
│   └── bronze_meteo.py
└── resources/
    └── snowflake_resource.py  # SnowflakeResource Dagster
```

### Gestion de l'authentification RTE

Le token OAuth2 RTE expire toutes les 3600 secondes. Dans un contexte Dagster, gérez cette dépendance via une **Dagster Resource** (`IOManager` ou ressource custom), pas via une variable globale. La ressource encapsule la logique de refresh automatique du token.

```python
# Pattern de resource Dagster pour OAuth2 (à compléter)
from dagster import ConfigurableResource
import requests

class RTEApiResource(ConfigurableResource):
    client_id: str
    client_secret: str
    _token: str = None
    _token_expiry: float = 0

    def get_token(self) -> str:
        # Vérifier si le token est encore valide
        # Sinon, appel POST /token avec client_credentials
        # Stocker et retourner le token
        ...
```

> Question guidante : Dagster permet de passer des secrets via `EnvVar("RTE_CLIENT_SECRET")` dans la configuration de la resource. Comment configurez-vous cela pour que le secret ne soit jamais loggé dans les métadonnées d'asset ni dans les runs logs ?

### Idempotence et reprise

Le backfill d'un historique de 5 ans (~1 825 partitions) ne se fait pas en une seule passe. Des échecs de réseau, des rate limits API ou des timeouts Snowflake peuvent interrompre le processus. Votre pipeline doit être conçu pour :

- Détecter les partitions manquantes en Bronze (gap detection via `dim_temps`)
- Permettre un backfill ciblé sur les partitions KO sans retoucher les partitions OK
- Loguer le nombre de lignes ingérées par partition pour la réconciliation

---

## Phase 3 — Silver : séries temporelles & data contracts (J6-J8)

### Modèles dbt incrémentaux

La table Silver centrale est une série temporelle à granularité 15 min sur plusieurs années. Un `dbt run` full-refresh sur 5 ans de données est coûteux. Utilisez la matérialisation incrémentale :

```sql
-- models/silver/stg_eco2mix_national.sql
-- Pattern de modèle incrémental (à compléter)

{{
  config(
    materialized='incremental',
    unique_key='time_id',
    incremental_strategy='merge',
    cluster_by=['date_local'],
    contract={"enforced": true}
  )
}}

with source as (
  select * from {{ source('bronze', 'eco2mix_national_raw') }}
  {% if is_incremental() %}
    -- Ne traiter que les nouvelles partitions
    where ingestion_date >= (select max(ingestion_date) from {{ this }})
  {% endif %}
),

-- Unification du timestamp (gestion UTC / Europe/Paris)
typed as (
  select
    convert_timezone('UTC', 'Europe/Paris', date_heure_raw::timestamp_ntz) as time_id,
    -- caster tous les champs numériques avec gestion des nulls
    ...
)

select * from typed
```

> Questions guidantes : Pourquoi `unique_key='time_id'` avec `incremental_strategy='merge'` est-il préférable à `delete+insert` pour une série temporelle ? Dans quels cas inverseriez-vous ce choix ? Comment le `cluster_by=['date_local']` réduit-il le coût des requêtes window sur Snowflake ?

### Unification des timestamps

Le point le plus délicat de Silver. Les APIs ODRÉ renvoient des timestamps avec offset `+01:00` ou `+02:00` selon la saison. Snowflake stocke ces valeurs en `TIMESTAMP_TZ` (avec offset conservé) ou en `TIMESTAMP_NTZ` (sans timezone). Définissez une convention claire dès le data contract :

- `time_id` : `TIMESTAMP_TZ` en UTC (normalisé) — clé primaire de la série
- `time_local` : `TIMESTAMP_NTZ` en Europe/Paris — pour l'affichage et les agrégations saisonnières

> Question guidante : Lors du passage à l'heure d'hiver (répétition du créneau 2h–3h), comment votre pipeline détecte-t-il et déduplique-t-il les deux enregistrements qui auront le même `time_local` mais des offsets différents ?

### Dimensions

#### `dim_temps`

Décrite en Phase 1. Matérialisée en `table`, régénérée mensuellement via job Dagster distinct.

#### `dim_filiere`

Référentiel des filières de production :

```yaml
# Exemple de contenu attendu (à implémenter en dbt seed)
filiere_id, filiere_label,       categorie,       est_renouvelable, facteur_co2_gkwh_min, facteur_co2_gkwh_max
NUC,        Nucléaire,           Low-carbon,      false,            4,                   12
EOL,        Éolien (total),      Renouvelable,    true,             7,                   15
SOL,        Solaire,             Renouvelable,    true,             20,                  50
HYD,        Hydraulique (total), Renouvelable,    true,             4,                   30
BIO,        Bioénergies,         Renouvelable,    true,             230,                 300
GAZ,        Gaz naturel,         Fossile,         false,            410,                 490
CHAR,       Charbon,             Fossile,         false,            820,                 1000
FIOUL,      Fioul,               Fossile,         false,            650,                 750
```

#### Snapshots SCD2 — évolution du référentiel

Le référentiel des filières évolue (nouvelles sous-filières, changements de classification). Un dbt snapshot capture ces évolutions avec les colonnes `dbt_valid_from` / `dbt_valid_to` :

```sql
-- snapshots/snap_dim_filiere.sql
{% snapshot snap_dim_filiere %}
{{
  config(
    target_schema='rte_silver',
    unique_key='filiere_id',
    strategy='check',
    check_cols=['categorie', 'est_renouvelable', 'facteur_co2_gkwh_min']
  )
}}
select * from {{ ref('dim_filiere') }}
{% endsnapshot %}
```

> Question guidante : Quand auriez-vous besoin de joindre un mart Gold au snapshot plutôt qu'à la dimension courante ? Décrivez un scénario concret lié aux données RTE.

### Data contracts (socle senior 1)

Un data contract est un accord formel entre producteur et consommateur d'une couche de données. Dans ce projet, il couvre la frontière Bronze → Silver.

Structure du contrat Bronze → Silver (fichier `data_contracts/eco2mix_national_contract.yml`) :

```yaml
contract_version: "1.2"
owner: "data-engineering-team"
sla_freshness_hours: 25       # données J-1 disponibles avant 9h00
effective_date: "2024-01-01"
source_dataset: "eco2mix-national-cons-def"

schema:
  - name: time_id
    data_type: TIMESTAMP_TZ
    nullable: false
    description: "Timestamp UTC du créneau 15 min"
  - name: consommation_mw
    data_type: NUMBER(8,0)
    nullable: true
    constraints:
      min: 15000        # Consommation nationale plancher physique
      max: 105000       # Consommation nationale plafond physique
  - name: nucleaire_mw
    data_type: NUMBER(8,0)
    nullable: true
    constraints:
      min: 0
      max: 64000        # Capacité installée nucléaire France ~63 GW
  - name: taux_co2
    data_type: NUMBER(5,1)
    nullable: true
    constraints:
      min: 20
      max: 500          # g CO2/kWh — hors anomalie

evolution_policy:
  add_column: "backward_compatible — aucun impact consommateurs"
  rename_column: "breaking_change — version bump obligatoire"
  change_type: "breaking_change — version bump + migration guide"
  remove_column: "breaking_change — deprecation 30 jours"
```

L'enforcement dans dbt se fait via le bloc `contract` du modèle :

```yaml
# models/silver/schema.yml (extrait)
models:
  - name: stg_eco2mix_national
    config:
      contract:
        enforced: true
    columns:
      - name: consommation_mw
        data_type: number
        constraints:
          - type: not_null
```

> Questions guidantes : Que se passe-t-il si RTE ajoute une colonne `eolien_offshore_mw` dans le jeu de données ODRÉ ? Votre contract bloque-t-il ce changement en Silver, ou le laisse-t-il passer ? Comment versionner le contrat sans casser les marts Gold existants ?

### Tests de fraîcheur dbt

```yaml
# models/silver/sources.yml
sources:
  - name: bronze
    schema: rte_bronze
    freshness:
      warn_after: {count: 25, period: hour}
      error_after: {count: 48, period: hour}
    loaded_at_field: ingestion_timestamp
    tables:
      - name: eco2mix_national_raw
```

---

## Phase 4 — Gold : marts énergie, saisonnalité & prévision (J9-J11)

### `mart_mix_quotidien`

Agrégation journalière de la série 15 min. Ce mart est la base de la plupart des visualisations :

```sql
-- Pattern du mart quotidien (à compléter)
-- grain : 1 ligne par jour (date_local)
select
    dt.date_local,
    dt.year,
    dt.month,
    dt.season,
    -- Énergie produite par filière (MWh = somme des MW × 0.25h)
    sum(f.nucleaire_mw)    * 0.25 as nucleaire_mwh,
    sum(f.eolien_mw)       * 0.25 as eolien_mwh,
    sum(f.solaire_mw)      * 0.25 as solaire_mwh,
    sum(f.hydraulique_mw)  * 0.25 as hydraulique_mwh,
    -- Part des renouvelables (%)
    (sum(f.eolien_mw + f.solaire_mw + f.hydraulique_mw + f.bioenergies_mw))
        / nullif(sum(f.production_totale_mw), 0) * 100 as part_enr_pct,
    -- Intensité carbone moyenne pondérée
    avg(f.taux_co2) as co2_intensite_gkwh,
    -- Consommation
    sum(f.consommation_mw) * 0.25 as consommation_mwh
from {{ ref('stg_eco2mix_national') }} f
join {{ ref('dim_temps') }} dt on f.time_id = dt.time_id
group by 1, 2, 3, 4
```

> Question guidante : Ce mart est matérialisé en `table`. Dans quel cas vous tourneriez-vous vers une **dynamic table** Snowflake à la place ? Quels sont les critères de décision (fréquence de mise à jour, coût compute, latence acceptable) ?

### `mart_saisonnalite` — Window functions

La saisonnalité est le cœur analytique du projet. Calculez des profils moyens par saison, jour de la semaine et heure :

```sql
-- Pattern window functions sur séries temporelles
select
    dt.hour_local,
    dt.day_of_week,
    dt.season,
    avg(f.consommation_mw)                                         as conso_moy_mw,
    avg(f.part_enr_pct)                                            as enr_moy_pct,
    -- Comparaison avec la moyenne annuelle (window)
    avg(f.consommation_mw) over (partition by dt.year)             as conso_moy_annuelle,
    avg(f.consommation_mw)
        - avg(f.consommation_mw) over (partition by dt.year)       as ecart_moyenne_annuelle
from {{ ref('stg_eco2mix_national') }} f
join {{ ref('dim_temps') }} dt on f.time_id = dt.time_id
group by 1, 2, 3, dt.year
```

### `mart_meteo_conso` — ASOF JOIN Snowflake

La corrélation consommation/température nécessite un alignement temporel des deux séries. Snowflake propose l'**ASOF JOIN** qui joint chaque enregistrement de gauche au dernier enregistrement de droite antérieur ou égal dans le temps :

```sql
-- Pattern ASOF JOIN pour aligner météo journalière et consommation 15 min
select
    f.time_id,
    f.consommation_mw,
    m.temperature_2m_mean,
    -- Modèle linéaire simplifié (DJU - Degrés-Jours Unifiés)
    case
        when m.temperature_2m_mean < 17
        then (17 - m.temperature_2m_mean) * f.consommation_mw / 1000
        else 0
    end as dju_contrib
from {{ ref('stg_eco2mix_national') }} f
asof join {{ ref('stg_meteo_france') }} m
    match_condition (f.time_id >= m.date_local::timestamp_tz)
    on f.region = m.region
```

> Question guidante : L'ASOF JOIN Snowflake est une fonctionnalité relativement récente. Quelle alternative SQL standard utiliseriez-vous si vous deviez supporter un moteur sans ASOF JOIN ? Quels en sont les coûts de performance comparés ?

### Prévision de consommation

Deux approches, à évaluer dans un ADR :

**Option A — SQL windowed (simple, zéro infrastructure) :**

```sql
-- Prévision naïve : moyenne mobile pondérée + saisonnalité
-- Utile pour baseline et validation du mart saisonnalité
select
    next_day,
    avg(consommation_mwh) over (
        partition by day_of_week, season
        order by date_local
        rows between 28 preceding and 1 preceding
    ) as forecast_mwh
from {{ ref('mart_mix_quotidien') }}
```

**Option B — Snowflake Cortex ML Forecast :**

```sql
-- Snowflake Cortex Forecast (à partir de Snowflake 2024)
-- Nécessite un warehouse avec accès Cortex activé
CREATE OR REPLACE SNOWFLAKE.ML.FORECAST rte_conso_forecast (
    INPUT_DATA => SYSTEM$REFERENCE('VIEW', 'RTE_GOLD.v_conso_for_forecast'),
    SERIES_COLNAME => 'region',
    TIMESTAMP_COLNAME => 'date_local',
    TARGET_COLNAME => 'consommation_mwh',
    CONFIG_OBJECT => { 'ON_ERROR': 'SKIP' }
);
```

> Questions guidantes : Quels sont les critères qui vous feraient choisir Cortex ML plutôt que l'option SQL ? Comment évaluez-vous la qualité d'une prévision de consommation sur ce domaine (MAPE, RMSE) ? Quelle est la saisonnalité dominante à capturer (hebdomadaire ? annuelle ?) ?

---

## Phase 5 — Observabilité, CI/CD, coût & SLA (J12-J14)

### Observabilité des données — Elementary (socle senior 2)

Elementary est un package dbt qui étend les tests natifs et publie un rapport d'observabilité. Installation :

```yaml
# packages.yml
packages:
  - package: elementary-data/elementary
    version: "0.14.x"
```

```yaml
# profiles.yml (section elementary)
elementary:
  target: prod
  outputs:
    prod:
      type: snowflake
      ...
      schema: rte_metrics   # schéma dédié aux résultats Elementary
```

Configurez Elementary pour surveiller :

- **Fraîcheur** : alerte si `eco2mix_national_raw` n'a pas été actualisé depuis > 25 heures
- **Volume** : anomalie si le nombre de lignes ingérées pour une partition J est < 85 % de la médiane des 30 derniers jours (détection d'un jour tronqué ou d'une rupture API)
- **Changement de schéma** : notification si une colonne disparaît de la source ODRÉ
- **Anomalie métier** : test sur `nucleaire_mw >= 0` ET sur `solaire_mw >= 0` (valeur négative = aberration physique)

```yaml
# models/silver/schema.yml — tests Elementary
models:
  - name: stg_eco2mix_national
    tests:
      - elementary.volume_anomalies:
          timestamp_column: date_local
          where: "date_local > dateadd(day, -60, current_date)"
      - elementary.freshness_anomalies:
          timestamp_column: ingestion_timestamp
    columns:
      - name: nucleaire_mw
        tests:
          - elementary.column_anomalies:
              column_anomalies:
                - zero_count
                - min
```

> Question guidante : Comment Elementary détecte-t-il une anomalie de volume vs un simple trou de données (jour férié vs panne API) ? Comment distinguez-vous les deux dans votre runbook ?

### Asset checks Dagster

En complément d'Elementary, les **asset checks Dagster** permettent de valider la qualité à l'asset level, au moment de la matérialisation, avec un résultat visible dans le graphe d'assets :

```python
from dagster import asset_check, AssetCheckResult, AssetCheckSeverity

@asset_check(asset=bronze_eco2mix_national)
def check_bronze_row_count(context, bronze_eco2mix_national):
    # Requêter Snowflake pour vérifier le nombre de lignes
    # de la partition qui vient d'être matérialisée
    row_count = ...
    expected_min = 85   # 85% de 96 créneaux = 81 lignes minimum
    return AssetCheckResult(
        passed=row_count >= expected_min,
        severity=AssetCheckSeverity.ERROR,
        metadata={"row_count": row_count, "expected_min": expected_min}
    )
```

### CI/CD de la donnée — GitHub Actions (socle senior 3)

```yaml
# .github/workflows/ci.yml — structure (à compléter)
name: dbt CI Pipeline

on:
  pull_request:
    branches: [main]
    paths: ['models/**', 'tests/**', 'macros/**', 'snapshots/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SQLFluff lint
        run: |
          pip install sqlfluff sqlfluff-templater-dbt
          sqlfluff lint models/ --dialect snowflake --templater dbt

  dbt-slim-ci:
    needs: lint
    runs-on: ubuntu-latest
    env:
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
    steps:
      - uses: actions/checkout@v4
      - name: dbt build (Slim CI — state:modified+)
        run: |
          # Télécharger le manifest.json de prod depuis S3/GCS/artifact
          dbt build \
            --select "state:modified+" \
            --state ./prod-manifest/ \
            --target ci \
            --vars '{"target_schema": "ci_${{ github.event.number }}"}'
      - name: dbt docs generate
        run: dbt docs generate
      - name: Validate Dagster definitions
        run: |
          dagster definitions validate -f dagster_definitions.py
```

Points critiques de la CI :

- Le **Slim CI** (`state:modified+`) évite de rebuilder tout le projet sur chaque PR ; il ne construit que les modèles modifiés et leurs descendants. Cela nécessite de stocker et télécharger le `manifest.json` de production.
- Le schéma CI est éphémère (`ci_<PR_NUMBER>`) et doit être nettoyé après le merge.
- Les secrets Snowflake et RTE ne sont jamais écrits dans le code ou les logs ; ils transitent exclusivement par GitHub Secrets.

> Questions guidantes : Comment implémentez-vous la suppression automatique du schéma CI éphémère après le merge de la PR ? Comment évitez-vous les conflits si deux PRs tournent en parallèle sur le même environnement CI ?

### Optimisation coût & performance Snowflake (socle senior 4)

#### Sizing des warehouses

Créez des warehouses distincts par usage, avec des politiques d'auto-suspend différenciées :

| Warehouse | Taille | Auto-suspend | Usage |
|---|---|---|---|
| `RTE_INGEST_WH` | X-SMALL | 60 s | Ingestion Python (faible parallélisme) |
| `RTE_TRANSFORM_WH` | SMALL | 120 s | dbt runs quotidiens |
| `RTE_ANALYTICS_WH` | SMALL | 60 s | Requêtes analytiques / marts Gold |
| `RTE_CI_WH` | X-SMALL | 30 s | GitHub Actions CI (facturable, à réduire) |

> Question guidante : Comment justifiez-vous le choix d'un SMALL plutôt qu'un MEDIUM pour `RTE_TRANSFORM_WH` ? Quel est l'impact du multi-cluster sur le coût si plusieurs dbt threads tournent en parallèle ?

#### Clustering de la fact table Silver

La table Silver à granularité 15 min sur 5 ans contient ~1,75 million de lignes. Sans clustering, une requête filtrée sur `date_local` scannera toutes les micro-partitions.

```sql
-- Après création initiale, ajouter un clustering key
ALTER TABLE RTE_SILVER.stg_eco2mix_national
CLUSTER BY (date_local);
```

> Question guidante : Comment mesurez-vous l'efficacité du clustering avec `SYSTEM$CLUSTERING_INFORMATION` ? À partir de quelle taille de table le clustering devient-il bénéfique sur Snowflake (coût de maintenance vs économies de scan) ?

#### Dynamic tables vs modèles incrémentaux dbt

Ce choix est matérialisé en ADR (cf. ADR-02 ci-dessous). Pour les agrégations Gold :

```sql
-- Pattern de dynamic table pour une agrégation Gold
-- TARGET_LAG contrôle la fraîcheur (et donc le coût de maintenance)
CREATE OR REPLACE DYNAMIC TABLE RTE_GOLD.dyn_mix_quotidien
    TARGET_LAG = '1 day'
    WAREHOUSE = RTE_TRANSFORM_WH
AS
select
    date_local,
    sum(nucleaire_mw) * 0.25     as nucleaire_mwh,
    sum(eolien_mw)   * 0.25     as eolien_mwh,
    -- ...
from RTE_SILVER.stg_eco2mix_national
group by date_local;
```

Un `TARGET_LAG = '1 day'` signifie que Snowflake peut attendre jusqu'à 24 heures avant de recalculer la table. Pour un mart de SLA J+1, c'est acceptable. Pour un mart de saisonnalité consulté hebdomadairement, vous pourriez monter à `'7 days'`.

#### Resource monitor

```sql
-- Protéger le budget mensuel
CREATE OR REPLACE RESOURCE MONITOR rte_monthly_budget
    WITH CREDIT_QUOTA = 50
    TRIGGERS
        ON 75 PERCENT DO NOTIFY
        ON 90 PERCENT DO NOTIFY
        ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE RTE_TRANSFORM_WH SET RESOURCE_MONITOR = rte_monthly_budget;
```

> Question guidante : Un resource monitor `SUSPEND` au seuil de 100 % peut interrompre un pipeline en cours d'exécution. Comment conçoit-on l'alerte pour intervenir avant le suspend ? Quel est l'impact d'un suspend sur les transactions Snowflake en cours ?

#### Query Profile — analyse d'une requête coûteuse

Dans la revue de code, vous devrez présenter l'analyse d'**au moins une requête via le Query Profile Snowflake** (onglet Query History → Explain Plan). Choisissez une requête Gold complexe (avec window function ou ASOF JOIN) et montrez :

- La proportion de temps passée en `TableScan` vs `Aggregate` vs `Join`
- L'efficacité du clustering (partition pruning visible dans les statistiques)
- La présence éventuelle d'un `Remote Disk Spill` (signe de manque de mémoire → warehouse trop petit)

### SLA, monitoring & runbook (socle senior 5)

#### SLA de fraîcheur

| Flux | SLA de fraîcheur | Mesure |
|---|---|---|
| Bronze eco2mix national | J-1 disponible avant 9h00 | `max(ingestion_timestamp)` par date dans Bronze |
| Silver stg_eco2mix_national | J-1 transformé avant 10h00 | `max(dbt_updated_at)` en Silver |
| Gold mart_mix_quotidien | J-1 disponible avant 10h30 | `max(date_local)` en Gold |

Le job Dagster quotidien est schedulé à 6h00 UTC (données J-2 consolidées disponibles). Un asset check sur le mart Gold vérifie que `max(date_local) >= current_date - 1` avant 10h30.

#### Alerting

Configurez deux canaux d'alerte :

1. **Dagster → Slack** : échec d'un asset ou d'un asset check → webhook Slack `#data-alerts`
2. **Elementary → Slack** : test échoué ou anomalie de volume → webhook Slack `#data-quality`

#### RUNBOOK.md — incidents types

Le runbook doit couvrir **au minimum deux incidents types** avec les sections : Symptômes / Détection / Diagnostic / Remédiation / Prévention.

**Incident 1 — Jour d'historique manquant (trou de série)**

- Symptômes : asset check `check_bronze_row_count` échoué sur une partition J. Elementary détecte une anomalie de volume.
- Détection : alerte Dagster → Slack + rapport Elementary du matin.
- Diagnostic : vérifier si le trou est en Bronze (panne API lors de l'ingestion) ou en Silver (échec de la transformation). Requête de vérification des gaps :
```sql
-- Détecter les créneaux manquants sur une plage
select t.time_id
from {{ ref('dim_temps') }} t
left join {{ ref('stg_eco2mix_national') }} f on t.time_id = f.time_id
where t.date_local = '2024-07-14'
  and f.time_id is null
order by t.time_id;
```
- Remédiation : déclencher un backfill ciblé sur la partition KO via `dagster asset materialize --select bronze_eco2mix_national --partition 2024-07-14`.
- Prévention : asset check sur le nombre de créneaux attendus par partition.

**Incident 2 — Valeurs de production aberrantes**

- Symptômes : test dbt `nucleaire_mw >= 0` échoué. Alerte Elementary `column_anomalies` sur `nucleaire_mw`.
- Détection : rapport Elementary + log dbt run.
- Diagnostic : isoler les lignes aberrantes en Bronze ; vérifier si l'anomalie provient de l'API (erreur source) ou d'une transformation incorrecte. Requête d'isolation :
```sql
select time_id, nucleaire_mw, ingestion_timestamp
from rte_bronze.eco2mix_national_raw
where date_local = '<date_suspecte>'
  and nucleaire_mw < 0
order by time_id;
```
- Remédiation : si l'anomalie est source, ouvrir un signalement ODRÉ et exclure les lignes via un filtre Silver. Si transformation, corriger le modèle et forcer un `dbt run --full-refresh --select stg_eco2mix_national`.
- Prévention : contrôle de borne dans le data contract + test dbt `accepted_range`.

---

## Décisions d'architecture (ADR) — socle senior 6

Les ADR suivent le format MADR (Markdown Any Decision Record) : Contexte → Décision → Alternatives → Conséquences.

### ADR-01 — Dagster (assets) vs Airflow (tâches)

**Contexte** : Le projet traite un historique de 5 ans en batch quotidien. Le backfill doit être simple, ciblé et reproductible. La qualité des données doit être visible au niveau de chaque unité logique (asset).

**Décision** : Dagster avec software-defined assets et partitions temporelles.

**Alternatives écartées** :
- *Apache Airflow* : centré tâche (DAG/Operator), le lineage est opaque (on voit les tâches, pas les datasets produits). Le backfill d'historique s'implémente via `catchup=True` mais sans visibilité fine sur les partitions en échec. L'interface ne permet pas de re-matérialiser un asset ciblé sans modifier le DAG.
- *Prefect* : bonne gestion du backfill mais écosystème moins mature sur le concept d'asset-level lineage.

**Conséquences** :
- Les modèles dbt sont exposés comme assets Dagster via `dagster-dbt` (chaque modèle dbt = un asset dans le graphe).
- Le graphe de lineage Dagster couvre l'ensemble de la chaîne source → Bronze → Silver → Gold.
- La courbe d'apprentissage Dagster est supérieure à Airflow pour une équipe habituée aux DAGs.

**Point de vigilance** : L'intégration `dagster-dbt` impose une version compatible entre dagster, dagster-dbt et dbt-core. Vérifiez la matrice de compatibilité avant de figer les versions.

> Question guidante : En quoi le concept de "software-defined asset" diffère-t-il fondamentalement d'un "operateur" Airflow ? Quelle implication cela a-t-il sur la façon dont vous raisonnez votre pipeline ?

### ADR-02 — Dynamic tables Snowflake vs modèles incrémentaux dbt

**Contexte** : Les marts Gold sont des agrégations recalculées quotidiennement. Deux options nationales sur Snowflake : les dynamic tables (Snowflake gère le refresh automatiquement) et les modèles dbt incrémentaux (Dagster/dbt gèrent l'orchestration).

**Décision** : Modèles dbt incrémentaux pour les marts Gold principaux ; dynamic tables pour les agrégations secondaires à forte fréquence de consultation (saisonnalité horaire).

| Critère | Dynamic tables | dbt incrémental |
|---|---|---|
| Orchestration | Snowflake-native (TARGET_LAG) | Dagster → dbt run |
| Lineage Dagster | Hors graphe (opaque) | Dans le graphe (visible) |
| Tests dbt | Non applicables directement | Natifs |
| Coût refresh | Continu (selon TARGET_LAG) | Ponctuel (schedule) |
| Backfill historique | Non supporté nativement | Natif (partitions Dagster) |

**Conséquences** : Les dynamic tables ne participent pas au lineage Dagster. Elles doivent être monitorées séparément (Snowflake Activity → Dynamic Tables). L'usage des dynamic tables est limité aux agrégations statiques ne nécessitant pas de backfill.

### ADR-03 — Approche de prévision de consommation

**Contexte** : Le projet demande une prévision simple de la consommation quotidienne. Trois options ont été évaluées.

**Décision** : Baseline SQL windowed (option A) pour la livraison initiale, avec migration vers Cortex ML Forecast en extension senior.

**Alternatives** :
- *SQL windowed* : implémentation nulle infrastructure, testable dans dbt, lisible pour l'équipe data. Précision limitée (pas de features météo dans le modèle).
- *Snowflake Cortex ML Forecast* : précision supérieure, sans code ML externe, mais nécessite un warehouse avec Cortex activé et génère des coûts de compute supplémentaires. La reproductibilité du modèle est moindre (boîte noire relative).
- *Prophet externe* : précision élevée, explicabilité totale, mais nécessite une infrastructure Python (Dagster ops), gestion de dépendances, stockage des artefacts de modèle.

**Conséquences** : La prévision SQL est une approximation naive (MAPE attendu ~5-8 % sur consommation journalière). Elle sert de baseline pour valider la plausibilité des données, pas d'outil décisionnel.

---

## Évaluation par blocs de compétence

### Bloc 1 — Ingestion & backfill partitionné

| Critère | Attendu |
|---|---|
| Assets Dagster partitionnés avec `DailyPartitionsDefinition` configurée depuis 2018 | OUI/NON |
| Idempotence démontrée : relancer 2 fois la même partition produit le même résultat en base | OUI/NON |
| Backfill de 12 mois d'historique exécuté et visible dans l'UI Dagster | OUI/NON |
| Gestion du token OAuth2 RTE via Dagster Resource (secret non loggé) | OUI/NON |

### Bloc 2 — Modélisation séries temporelles & SCD

| Critère | Attendu |
|---|---|
| Modèle Silver incrémental avec `unique_key`, `cluster_by`, `is_incremental()` correctement implémentés | OUI/NON |
| Timestamps unifiés en UTC (TIMESTAMP_TZ) sans doublons sur changement d'heure | OUI/NON |
| `dim_temps` complète (colonnes grain 15 min + quotidien, is_weekend, is_bank_holiday) | OUI/NON |
| Snapshot SCD2 sur `dim_filiere` avec au moins une evolution simulée | OUI/NON |

### Bloc 3 — Data contracts & qualité

| Critère | Attendu |
|---|---|
| Fichier `data_contracts/eco2mix_national_contract.yml` avec bornes physiques documentées | OUI/NON |
| `contract: enforced: true` actif sur le modèle Silver principal | OUI/NON |
| Tests dbt couvrant : bornes MW, taux_co2, fraîcheur de source | OUI/NON |
| Stratégie d'évolution de schéma documentée (breaking vs non-breaking) | OUI/NON |

### Bloc 4 — Observabilité & CI/CD

| Critère | Attendu |
|---|---|
| Elementary configuré avec au moins 3 types de tests (volume, freshness, column anomalies) | OUI/NON |
| Rapport Elementary généré et consultable (HTML ou lien) | OUI/NON |
| `.github/workflows/ci.yml` avec Slim CI (`state:modified+`) fonctionnel sur une PR de démonstration | OUI/NON |
| Asset checks Dagster sur Bronze (row count) et Gold (max date) | OUI/NON |

### Bloc 5 — Coût, performance & exploitation

| Critère | Attendu |
|---|---|
| Au moins une dynamic table Gold avec `TARGET_LAG` justifié dans l'ADR-02 | OUI/NON |
| Clustering key sur Silver fact table + analyse `SYSTEM$CLUSTERING_INFORMATION` documentée | OUI/NON |
| Resource monitor Snowflake configuré avec notification avant suspend | OUI/NON |
| `RUNBOOK.md` couvrant 2 incidents types avec commandes de remédiation | OUI/NON |

**Clause de validation partielle** : un candidat dont le pipeline n'est pas parfaitement fonctionnel en démonstration finale, mais dont l'architecture (ADR), les data contracts, le runbook et la CI/CD sont solides et argumentés, peut valider les blocs 3, 4 et 5 indépendamment des blocs 1 et 2. La démonstration technique (blocs 1 et 2) représente 60 % de la note finale ; la revue d'architecture et de documentation représente 40 %.

---

## Livrables

### Repo GitHub public

```
rte-mix-energetique/
├── ingestion/
│   ├── connectors/
│   │   ├── odre_client.py
│   │   ├── rte_client.py
│   │   └── meteo_client.py
│   ├── assets/
│   │   ├── bronze_eco2mix_national.py
│   │   ├── bronze_eco2mix_regional.py
│   │   └── bronze_meteo.py
│   └── resources/
│       ├── snowflake_resource.py
│       └── rte_api_resource.py
├── dagster_definitions.py
├── dbt/
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml          # (sans secrets, valeurs via env vars)
│   ├── models/
│   │   ├── bronze/           # sources déclaratives uniquement
│   │   ├── silver/
│   │   │   ├── stg_eco2mix_national.sql
│   │   │   ├── stg_eco2mix_regional.sql
│   │   │   ├── stg_meteo.sql
│   │   │   ├── dim_temps.sql
│   │   │   └── schema.yml    # contracts + tests + freshness
│   │   └── gold/
│   │       ├── mart_mix_quotidien.sql
│   │       ├── mart_saisonnalite.sql
│   │       ├── mart_co2_intensite.sql
│   │       └── mart_meteo_conso.sql
│   ├── snapshots/
│   │   └── snap_dim_filiere.sql
│   ├── seeds/
│   │   └── dim_filiere.csv
│   └── tests/
│       └── generic/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── docs/
│   └── adr/
│       ├── ADR-01-dagster-vs-airflow.md
│       ├── ADR-02-dynamic-tables-vs-incremental.md
│       └── ADR-03-forecast-approach.md
├── data_contracts/
│   ├── eco2mix_national_contract.yml
│   └── eco2mix_regional_contract.yml
├── RUNBOOK.md
└── README.md
```

### Livrables non-code

- Schéma d'architecture complet (draw.io / PNG exporté, dans `docs/architecture.png`)
- Tableau Kanban (GitHub Projects) avec historique des tickets fermés par phase
- Rapport Elementary (capture ou lien HTML hébergé)
- Dashboard de suivi des crédits Snowflake (export Resource Monitor ou capture Snowsight)
- Capture du graphe de lineage Dagster (Asset Lineage view couvrant Bronze → Gold)

---

## Ressources techniques

**Snowflake**

- Dynamic tables : https://docs.snowflake.com/en/user-guide/dynamic-tables-intro
- TARGET_LAG : https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table
- ASOF JOIN : https://docs.snowflake.com/en/sql-reference/constructs/asof-join
- Cortex ML Forecast : https://docs.snowflake.com/en/user-guide/ml-functions/forecasting
- Resource monitors : https://docs.snowflake.com/en/user-guide/resource-monitors
- SYSTEM$CLUSTERING_INFORMATION : https://docs.snowflake.com/en/sql-reference/functions/system_clustering_information

**dbt**

- Modèles incrémentaux : https://docs.getdbt.com/docs/build/incremental-models
- Sources freshness : https://docs.getdbt.com/docs/build/sources#source-freshness
- Snapshots : https://docs.getdbt.com/docs/build/snapshots
- Model contracts : https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- Slim CI : https://docs.getdbt.com/docs/deploy/slim-ci-cd

**Dagster**

- Software-defined assets : https://docs.dagster.io/concepts/assets/software-defined-assets
- Partitions & backfill : https://docs.dagster.io/concepts/partitions-schedules-sensors/partitions
- Asset checks : https://docs.dagster.io/concepts/assets/asset-checks
- dagster-dbt integration : https://docs.dagster.io/integrations/dbt

**Elementary**

- Documentation : https://docs.elementary-data.com/
- Volume anomalies : https://docs.elementary-data.com/data-tests/anomaly-detection-tests/volume-anomalies

**Sources de données**

- ODRÉ Explore API v2 : https://help.opendatasoft.com/apis/ods-explore-v2/
- Jeu national consolidé : https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/
- Portail RTE data : https://data.rte-france.com/
- Open-Meteo archive : https://open-meteo.com/en/docs/historical-weather-api

**Outillage**

- SQLFluff (lint SQL) : https://docs.sqlfluff.com/
- MADR (format ADR) : https://adr.github.io/madr/

---

## Pour aller plus loin (niveau senior confirmé)

- **Prévision avancée avec Prophet** : intégrer un Dagster op Python qui entraîne un modèle Prophet sur `mart_mix_quotidien`, stocke les prédictions en Gold et loggue les métriques (MAPE, RMSE) dans les métadonnées d'asset Dagster.
- **OpenLineage / Marquez** : brancher Dagster sur un backend OpenLineage pour exporter le lineage dans un format standard inter-outils ; visualiser dans Marquez le lineage inter-assets jusqu'aux marts.
- **Comparaison inter-régions** : exploiter `eco2mix-regional-tr` pour comparer les mix régionaux (île-de-France vs Occitanie) et modéliser les échanges inter-régions ; ajoute une dimension régionale à `dim_filiere` et nécessite une partition composite (date × région) dans Dagster.
- **Alerting coût automatisé** : créer un Dagster sensor sur le Resource Monitor Snowflake ; si le ratio crédits consommés / crédits budgétés dépasse 80 %, le sensor déclenche une alerte Slack et suspend les warehouses non critiques.
- **Data mesh** : si le projet s'inscrit dans une organisation multi-équipes, modéliser la couche Gold comme un data product autonome (owner, SLA, contrat d'interface publié) consommable par d'autres domaines sans accès direct à Silver.
