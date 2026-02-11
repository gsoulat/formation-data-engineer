# Module 02 - Architecture d'un Data Lake

## Architecture en couches (Zones)

L'architecture d'un Data Lake repose sur un systeme de **zones** qui organise les donnees selon leur niveau de maturite. C'est le pattern le plus repandu, souvent appele **architecture multi-zones** ou **architecture en couches**.

```
+-------------------------------------------------------------------+
|                    COUCHE DE CONSOMMATION                          |
|          (BI, ML, APIs, Reporting, Self-service)                  |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|                    ZONE CONSUMPTION / GOLD                        |
|         Donnees agregees, metriques, vues metier                  |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|                    ZONE CURATED / SILVER                          |
|         Donnees nettoyees, conformes, validees                    |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|                    ZONE RAW / BRONZE                              |
|         Donnees brutes, copie exacte des sources                  |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|              SOURCES DE DONNEES                                   |
|    (ERP, CRM, APIs, IoT, Fichiers, Streaming)                    |
+-------------------------------------------------------------------+
```

## Zone Raw (Bronze)

### Principe

La zone Raw est la **copie fidele des sources**. Aucune transformation n'est appliquee. C'est la "source de verite" du Data Lake.

### Regles

- **Aucune modification** des donnees sources
- Conservation du **format d'origine** (ou conversion minimale)
- **Horodatage** de l'ingestion
- **Partitionnement** par date d'ingestion
- **Retention longue duree** (archivage)

### Organisation typique

```
/raw/
+-- erp/
|   +-- orders/
|   |   +-- ingestion_date=2024-01-15/
|   |   |   +-- orders_full_20240115_083000.csv
|   |   +-- ingestion_date=2024-01-16/
|   |       +-- orders_full_20240116_083000.csv
|   +-- products/
|       +-- ingestion_date=2024-01-15/
|           +-- products_20240115.json
+-- crm/
|   +-- contacts/
|       +-- ingestion_date=2024-01-15/
|           +-- contacts_export.csv
+-- web_analytics/
|   +-- clickstream/
|       +-- year=2024/month=01/day=15/
|           +-- events_00.json.gz
|           +-- events_01.json.gz
+-- iot/
    +-- sensors/
        +-- year=2024/month=01/day=15/hour=08/
            +-- sensor_data.parquet
```

### Bonnes pratiques Zone Raw

| Pratique | Explication |
|----------|-------------|
| Fichiers immutables | Ne jamais modifier un fichier une fois depose |
| Nommage explicite | Inclure source, date, timestamp dans le nom |
| Compression | Gzip, Snappy, Zstd pour reduire les couts |
| Partitionnement temporel | Par date d'ingestion minimum |
| Metadata | Stocker les metadonnees d'ingestion (source, timestamp, job_id) |

## Zone Curated (Silver)

### Principe

La zone Curated contient les donnees **nettoyees, validees et conformes**. C'est ici qu'on applique les regles de qualite et les transformations metier.

### Transformations typiques

1. **Nettoyage** : suppression des doublons, correction des types
2. **Validation** : regles de qualite (NOT NULL, plages de valeurs)
3. **Standardisation** : formats de dates, codes pays, devises
4. **Deduplication** : identification et elimination des doublons
5. **Conformite** : application des regles RGPD (anonymisation, pseudonymisation)

### Organisation typique

```
/curated/
+-- erp/
|   +-- orders/
|   |   +-- year=2024/month=01/
|   |       +-- part-00000.parquet
|   |       +-- part-00001.parquet
|   +-- products/
|       +-- year=2024/month=01/
|           +-- part-00000.parquet
+-- crm/
|   +-- contacts/
|       +-- year=2024/month=01/
|           +-- part-00000.parquet
+-- unified/
    +-- customers/          <-- Vue unifiee client (ERP + CRM)
        +-- year=2024/month=01/
            +-- part-00000.parquet
```

### Exemple de transformation Raw -> Curated

```
Raw (CSV brut)                          Curated (Parquet nettoye)
+----------+--------+----------+       +----------+--------+----------+---------+
| order_id | amount | date     |       | order_id | amount | date     | is_valid|
+----------+--------+----------+       +----------+--------+----------+---------+
| 1001     | 150.0  | 15/01/24 |  -->  | 1001     | 150.00 | 2024-01  | true    |
| 1002     | -10    | 16-01-24 |       | 1003     |  89.99 | 2024-01  | true    |
| 1001     | 150.0  | 15/01/24 |       +----------+--------+----------+---------+
| 1003     | 89.99  | 2024-1-17|       Doublon supprime, montant negatif exclu,
+----------+--------+----------+       dates standardisees, format Parquet
```

## Zone Consumption (Gold)

### Principe

La zone Consumption contient les donnees **pretes a l'emploi** pour les consommateurs finaux : BI, reporting, ML, APIs.

### Types de donnees

- **Agregats** : metriques pre-calculees (CA mensuel, nombre de commandes)
- **Data Marts** : sous-ensembles orientes metier (Finance, Marketing, RH)
- **Feature Stores** : features pre-calculees pour le ML
- **Vues materialisees** : jointures complexes pre-calculees

### Organisation typique

```
/consumption/
+-- data_marts/
|   +-- finance/
|   |   +-- monthly_revenue/
|   |   |   +-- year=2024/month=01/
|   |   |       +-- part-00000.parquet
|   |   +-- daily_costs/
|   |       +-- year=2024/month=01/day=15/
|   |           +-- part-00000.parquet
|   +-- marketing/
|       +-- customer_segments/
|       |   +-- part-00000.parquet
|       +-- campaign_performance/
|           +-- year=2024/month=01/
|               +-- part-00000.parquet
+-- ml/
|   +-- feature_store/
|   |   +-- customer_features/
|   |       +-- part-00000.parquet
|   +-- training_datasets/
|       +-- churn_model_v2/
|           +-- train.parquet
|           +-- test.parquet
+-- reporting/
    +-- executive_dashboard/
        +-- kpi_daily.parquet
```

## Architecture de reference complete

```
+----------+  +----------+  +----------+  +----------+
|   ERP    |  |   CRM    |  |   APIs   |  |   IoT    |
+----+-----+  +----+-----+  +----+-----+  +----+-----+
     |             |             |             |
     +------+------+------+------+------+------+
            |                    |
     +------v------+      +-----v------+
     |   Batch     |      |  Streaming |
     |  Ingestion  |      |  Ingestion |
     | (Airflow,   |      | (Kafka,    |
     |  Glue, ADF) |      |  Kinesis)  |
     +------+------+      +-----+------+
            |                    |
+-----------v--------------------v--------------+
|                ZONE RAW (Bronze)              |
|  Donnees brutes, immutables, partitionnees    |
|  Format: JSON, CSV, Avro, Parquet             |
+----------------------+------------------------+
                       |
              [Nettoyage, Validation, Deduplication]
              [Spark, dbt, Dataflow]
                       |
+----------------------v------------------------+
|             ZONE CURATED (Silver)             |
|  Donnees nettoyees, conformes, validees       |
|  Format: Parquet / Delta / Iceberg            |
+----------------------+------------------------+
                       |
              [Agregation, Jointures, Metriques]
              [Spark, dbt, SQL]
                       |
+----------------------v------------------------+
|           ZONE CONSUMPTION (Gold)             |
|  Data Marts, Agregats, Feature Store          |
|  Format: Parquet / Delta / Iceberg            |
+---------+----------+-----------+--------------+
          |          |           |
     +----v---+ +---v----+ +---v--------+
     |  BI    | |  ML    | |  APIs /    |
     | (Power | |(MLflow,| |  Apps      |
     |  BI,   | | Sage-  | | (REST,     |
     | Looker)| | maker) | |  GraphQL)  |
     +--------+ +--------+ +------------+
```

## Patterns d'organisation des fichiers

### Partitionnement

Le partitionnement est critique pour la performance des requetes sur un Data Lake.

#### Partitionnement Hive-style

```
/curated/orders/
+-- year=2024/
|   +-- month=01/
|   |   +-- day=15/
|   |   |   +-- part-00000.parquet
|   |   |   +-- part-00001.parquet
|   |   +-- day=16/
|   |       +-- part-00000.parquet
|   +-- month=02/
|       +-- day=01/
|           +-- part-00000.parquet
+-- year=2023/
    +-- month=12/
        +-- ...
```

**Avantage :** Les moteurs de requete (Spark, Athena, Trino) effectuent du **partition pruning** — ils ne lisent que les partitions necessaires.

```sql
-- Cette requete ne lira que le dossier year=2024/month=01/
SELECT * FROM orders
WHERE year = 2024 AND month = 1;
```

#### Regles de partitionnement

| Regle | Explication |
|-------|-------------|
| Cardinalite moderee | 100-10000 partitions max, eviter le sur-partitionnement |
| Colonnes de filtre frequentes | Partitionner sur les colonnes les plus filtrees |
| Taille de fichier optimale | 128 Mo - 1 Go par fichier |
| Eviter les small files | Trop de petits fichiers degradent les performances |

### Convention de nommage

```
/{zone}/{source}/{entite}/{partition}/

Exemples :
/raw/erp/orders/ingestion_date=2024-01-15/orders_20240115.csv
/curated/erp/orders/year=2024/month=01/part-00000.parquet
/consumption/finance/monthly_revenue/year=2024/month=01/revenue.parquet
```

## Metadata Layer (Couche de metadonnees)

Un Data Lake sans metadonnees est inutilisable. La couche de metadonnees permet de **decouvrir**, **comprendre** et **gouverner** les donnees.

### Composants

```
+-------------------------------------------+
|          Data Catalog                      |
|  (AWS Glue Catalog, Hive Metastore,       |
|   Unity Catalog, Azure Purview)            |
+-------------------------------------------+
|  - Schema des tables                      |
|  - Localisation des fichiers              |
|  - Statistiques (nombre de lignes, taille)|
|  - Lineage (d'ou viennent les donnees)    |
|  - Tags et classification                 |
|  - Droits d'acces                         |
+-------------------------------------------+
```

### Metadonnees techniques vs metier

| Type | Exemples | Outil |
|------|----------|-------|
| **Techniques** | Schema, format, taille, partitions, localisation | Glue Catalog, Hive Metastore |
| **Metier** | Description, proprietaire, domaine, SLA, PII | Data Catalog (Purview, DataHub) |
| **Operationnelles** | Date d'ingestion, job_id, duree, statut | Airflow, metadata tables |
| **Qualite** | Taux de completude, doublons, anomalies | Great Expectations, dbt tests |

## Points cles a retenir

- L'architecture en 3 zones (**Raw / Curated / Consumption**) est le standard
- La zone Raw est **immutable** : on ne modifie jamais les donnees brutes
- Le **partitionnement** est critique pour la performance des requetes
- Les fichiers doivent avoir une taille optimale (**128 Mo - 1 Go**)
- La **couche de metadonnees** (Data Catalog) rend le Data Lake exploitable
- Sans organisation rigoureuse, le Data Lake devient un **Data Swamp**

---

**Prochain module :** [03 - Formats de stockage](./03-formats-stockage.md)

[Retour au sommaire](./README.md)
