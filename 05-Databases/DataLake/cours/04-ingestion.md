# Module 04 - Ingestion de donnees

## Les modes d'ingestion

L'ingestion est le processus d'acheminement des donnees depuis les sources vers le Data Lake. Il existe trois modes principaux :

```
                     Latence          Volume        Complexite
+-----------+       +-----------+    +-----------+  +-----------+
|   Batch   |       | Minutes   |    |  Tres     |  |  Faible   |
|           |       | a heures  |    |  eleve    |  |           |
+-----------+       +-----------+    +-----------+  +-----------+

+-----------+       +-----------+    +-----------+  +-----------+
|  Micro-   |       | Secondes  |    |  Eleve    |  |  Moyenne  |
|  Batch    |       | a minutes |    |           |  |           |
+-----------+       +-----------+    +-----------+  +-----------+

+-----------+       +-----------+    +-----------+  +-----------+
| Streaming |       | Milli-    |    |  Variable |  |  Elevee   |
|           |       | secondes  |    |           |  |           |
+-----------+       +-----------+    +-----------+  +-----------+
```

## Ingestion Batch

### Principe

Les donnees sont collectees et chargees **a intervalles reguliers** (toutes les heures, tous les jours, toutes les semaines).

```
Sources                    Orchestrateur             Data Lake
+-----------+             +-------------+           +----------+
| BDD       |--dump SQL-->|             |           |          |
+-----------+             |  Airflow /  |--ecrire-->| /raw/    |
+-----------+             |  Glue /     |           |          |
| Fichiers  |--upload---->|  ADF        |           |          |
+-----------+             |             |           |          |
+-----------+             |  Planifie:  |           |          |
| APIs      |--pull------>|  Cron/DAG   |           |          |
+-----------+             +-------------+           +----------+
```

### Strategies de chargement batch

#### Full Load (chargement complet)

On extrait **toutes les donnees** de la source a chaque execution.

```
Execution 1 (Lundi)     Execution 2 (Mardi)
+--------+              +--------+
| 100    |              | 105    |
| lignes |              | lignes |
+--------+              +--------+
   |                       |
   v                       v
/raw/orders/             /raw/orders/
  date=2024-01-15/         date=2024-01-16/
  orders_full.parquet      orders_full.parquet
  (100 lignes)             (105 lignes)
```

| Avantage | Inconvenient |
|----------|-------------|
| Simple a implementer | Couteux en donnees et temps |
| Pas de logique incrementale | Redondance des donnees |
| Toujours coherent | Ne scale pas avec le volume |

**Quand l'utiliser :** Petites tables de reference (<100K lignes), tables sans colonne de modification

#### Incremental Load (chargement incremental)

On extrait **uniquement les nouvelles donnees ou modifications** depuis la derniere execution.

```
Execution 1 (Lundi)     Execution 2 (Mardi)
+--------+              +--------+
| 100    |              | 5 new  |
| lignes |              | lignes |
+--------+              +--------+
   |                       |
   v                       v
/raw/orders/             /raw/orders/
  date=2024-01-15/         date=2024-01-16/
  orders_full.parquet      orders_incr.parquet
  (100 lignes)             (5 lignes seulement)
```

**Techniques d'incremental :**

| Technique | Comment | Prerequis |
|-----------|---------|-----------|
| Timestamp-based | `WHERE updated_at > last_run` | Colonne `updated_at` fiable |
| ID-based | `WHERE id > last_max_id` | ID auto-increment |
| CDC (Change Data Capture) | Lecture du binlog/WAL | Acces aux logs de la BDD |
| Watermark | Marqueur dans la source | Source qui supporte les watermarks |

#### Change Data Capture (CDC)

Le CDC capture les **changements au niveau de la base source** (INSERT, UPDATE, DELETE) en temps reel ou quasi-reel.

```
BDD Source                  CDC                    Data Lake
+----------+          +------------+          +-----------+
| Table    |          |            |          | /raw/cdc/ |
| orders   |--binlog->| Debezium / |--event-->| orders/   |
|          |  /WAL    | DMS / Airbyte|        |           |
+----------+          +------------+          +-----------+

Evenement CDC :
{
  "op": "u",           // u=update, c=create, d=delete
  "before": {"id": 1, "amount": 100.00},
  "after":  {"id": 1, "amount": 150.00},
  "ts_ms": 1705312800000,
  "source": {"table": "orders", "db": "ecommerce"}
}
```

**Outils CDC populaires :**

| Outil | Type | Cloud |
|-------|------|-------|
| **Debezium** | Open source | Multi-cloud |
| **AWS DMS** | Manage | AWS |
| **Azure Data Factory** | Manage | Azure |
| **Airbyte** | Open source / SaaS | Multi-cloud |
| **Fivetran** | SaaS | Multi-cloud |

### Outils d'orchestration batch

| Outil | Type | Forces |
|-------|------|--------|
| **Apache Airflow** | Open source | Standard, flexible, Python DAGs |
| **AWS Glue** | Manage (AWS) | Serverless, integration S3/Catalog |
| **Azure Data Factory** | Manage (Azure) | UI drag-and-drop, integration Azure |
| **Prefect** | Open source / SaaS | Moderne, Python-native |
| **Dagster** | Open source | Software-defined assets, testing |

### Exemple d'un DAG Airflow d'ingestion

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG(
    'ingest_orders_to_datalake',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

def extract_from_source(**context):
    """Extraire les donnees de la source"""
    execution_date = context['ds']
    # SELECT * FROM orders WHERE date = execution_date
    pass

def load_to_raw(**context):
    """Deposer dans la zone Raw du Data Lake"""
    execution_date = context['ds']
    # Ecrire dans s3://datalake/raw/orders/date={execution_date}/
    pass

def validate_ingestion(**context):
    """Valider que l'ingestion s'est bien passee"""
    # Verifier le nombre de lignes, la taille du fichier
    pass

extract = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_from_source,
    dag=dag
)

load = PythonOperator(
    task_id='load_to_raw',
    python_callable=load_to_raw,
    dag=dag
)

validate = PythonOperator(
    task_id='validate',
    python_callable=validate_ingestion,
    dag=dag
)

extract >> load >> validate
```

## Ingestion Streaming

### Principe

Les donnees sont traitees **en continu**, evenement par evenement ou par micro-lots.

```
Sources temps reel         Message Broker           Consumers
+-----------+             +-------------+          +-----------+
| Capteurs  |--event----->|             |          |           |
+-----------+             |   Kafka /   |--read--->| Spark     |
+-----------+             |   Kinesis / |          | Streaming |
| Clics web |--event----->|   Pub/Sub   |--read--->| Flink     |
+-----------+             |             |          |           |
+-----------+             |   Topics /  |--read--->| Data Lake |
| Logs      |--event----->|   Streams   |          | (direct)  |
+-----------+             +-------------+          +-----------+
```

### Apache Kafka : le standard du streaming

```
Producteur          Kafka Cluster                Consommateur
+---------+      +---------------------------+    +---------+
| App     |----->| Topic: orders             |    | Spark   |
+---------+      |  Partition 0: [e1][e2][e3]|--->| Stream  |
                 |  Partition 1: [e4][e5]    |    +---------+
+---------+      |  Partition 2: [e6][e7][e8]|    +---------+
| IoT     |----->|                           |--->| Flink   |
+---------+      +---------------------------+    +---------+
```

**Concepts cles Kafka :**

| Concept | Description |
|---------|-------------|
| **Topic** | Canal de donnees (equivalent d'une table) |
| **Partition** | Subdivision d'un topic pour le parallelisme |
| **Producer** | Application qui envoie des messages |
| **Consumer** | Application qui lit des messages |
| **Consumer Group** | Groupe de consumers qui se partagent la charge |
| **Offset** | Position d'un message dans une partition |

### Patterns d'ecriture dans le Data Lake depuis le streaming

#### 1. Micro-batch (Spark Structured Streaming)

```python
# Lire depuis Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "orders") \
    .load()

# Ecrire dans le Data Lake toutes les 5 minutes
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/orders") \
    .trigger(processingTime="5 minutes") \
    .start("/curated/orders/")
```

#### 2. Direct sink (Kafka Connect)

```
Kafka --> Kafka Connect S3 Sink --> s3://datalake/raw/orders/
```

Configuration typique :
```json
{
  "connector.class": "io.confluent.connect.s3.S3SinkConnector",
  "topics": "orders",
  "s3.bucket.name": "my-datalake",
  "s3.region": "eu-west-1",
  "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
  "flush.size": 10000,
  "rotate.interval.ms": 300000,
  "partition.duration.ms": 3600000
}
```

## ETL vs ELT

### ETL (Extract - Transform - Load)

```
Source --> [Extract] --> [Transform] --> [Load] --> Data Warehouse
                              |
                     Transformation AVANT
                     le chargement
                     (sur un serveur ETL)
```

**Caracteristiques :**
- Transformation en dehors de la destination
- Historiquement utilise pour les DW
- Outils : Talend, Informatica, SSIS

### ELT (Extract - Load - Transform)

```
Source --> [Extract] --> [Load] --> Data Lake --> [Transform] --> Curated
                                                      |
                                              Transformation APRES
                                              le chargement
                                              (dans le Data Lake)
```

**Caracteristiques :**
- Chargement brut d'abord, transformation ensuite
- Pattern standard des Data Lakes modernes
- Outils : dbt, Spark, Dataflow

### Comparaison ETL vs ELT

| Critere | ETL | ELT |
|---------|-----|-----|
| Ordre | Transform puis Load | Load puis Transform |
| Ou transformer | Serveur ETL dedie | Dans le Data Lake/DW |
| Donnees brutes conservees | Non | Oui (zone Raw) |
| Flexibilite | Faible (schema avant) | Haute (schema apres) |
| Cout compute | Serveur ETL | Puissance du Data Lake |
| Latence | Plus elevee | Plus faible |
| Usage moderne | Legacy | Standard Data Lake |

## Gestion des fichiers : le probleme des small files

### Le probleme

```
Mauvais : 10 000 fichiers de 1 Mo = 10 Go
  --> Overhead metadata : 10 000 x ouverture de fichier
  --> Spark : 10 000 taches paralleles inutiles
  --> Cout API S3 : 10 000 x $0.0004 = $4.00

Bon : 10 fichiers de 1 Go = 10 Go
  --> Overhead metadata : 10 x ouverture de fichier
  --> Spark : 10 taches paralleles efficaces
  --> Cout API S3 : 10 x $0.0004 = $0.004
```

### Solutions

| Solution | Comment | Quand |
|----------|---------|-------|
| **Compaction** | Fusionner les petits fichiers en gros fichiers | Post-ingestion (batch job) |
| **Buffer + flush** | Accumuler en memoire, ecrire quand > 128 Mo | Ingestion streaming |
| **Repartition Spark** | `df.repartition(10)` avant ecriture | Transformation Spark |
| **Delta OPTIMIZE** | `OPTIMIZE table` (compaction native Delta) | Tables Delta Lake |
| **Iceberg rewrite** | Rewrite data files | Tables Iceberg |

```python
# Compaction avec Spark
df = spark.read.parquet("/raw/orders/date=2024-01-15/")
df.repartition(4).write.mode("overwrite").parquet("/raw/orders/date=2024-01-15/")

# Compaction avec Delta Lake
spark.sql("OPTIMIZE orders")
spark.sql("OPTIMIZE orders ZORDER BY (customer_id)")
```

## Patterns d'ingestion par source

| Source | Mode | Format | Outil recommande |
|--------|------|--------|-----------------|
| Base relationnelle (petit volume) | Batch full | CSV/Parquet | Airbyte, Glue, ADF |
| Base relationnelle (gros volume) | Batch incremental | Parquet | Spark, Glue |
| Base relationnelle (temps reel) | CDC | Avro/JSON | Debezium, DMS |
| API REST | Batch | JSON | Airflow + Python, dlt |
| Fichiers (SFTP/FTP) | Batch | Tel quel | Airflow, ADF |
| Kafka / Event Hub | Streaming | Avro/JSON | Kafka Connect, Spark Streaming |
| Capteurs IoT | Streaming | JSON/Avro | IoT Hub/Core + Streaming |
| Logs applicatifs | Streaming | JSON | Fluentd, Logstash |

## Points cles a retenir

- **Batch** pour les gros volumes a latence toleree, **streaming** pour le temps reel
- Le **CDC** (Change Data Capture) est la methode la plus fiable pour capter les changements
- **ELT** est le pattern standard des Data Lakes : charger brut, transformer ensuite
- Le **probleme des small files** est un piege classique : viser **128 Mo - 1 Go** par fichier
- L'**orchestration** (Airflow, ADF) est indispensable pour fiabiliser les pipelines batch
- Le choix du mode d'ingestion depend de la **latence requise** et du **volume**

---

**Prochain module :** [05 - Gouvernance et qualite des donnees](./05-gouvernance-qualite.md)

[Retour au sommaire](./README.md)
