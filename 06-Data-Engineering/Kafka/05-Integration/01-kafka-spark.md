# Kafka + Apache Spark Structured Streaming

## Pourquoi intégrer Kafka et Spark ?

Kafka est une plateforme de **streaming et de stockage d'événements**. Spark est un moteur de **traitement distribué** optimisé pour les grandes volumétries. Ensemble, ils forment un pipeline puissant :

```
[Sources]         [Ingestion]    [Traitement]        [Destinations]
Capteurs IoT  ──→               Filtrage
API externes  ──→ [Kafka]   ──→ Agrégation      ──→  Data Warehouse
Logs          ──→               Jointure         ──→  Elasticsearch
Transactions  ──→               ML Scoring       ──→  Dashboard
```

### Kafka vs Spark Streaming : rôles complémentaires

| Rôle                    | Kafka                        | Spark Structured Streaming     |
|-------------------------|------------------------------|-------------------------------|
| Stockage des events     | Oui (durée configurable)     | Non                           |
| Ingestion multi-sources | Oui (Kafka Connect)          | Via connecteurs Spark          |
| Traitement             | Simple (Faust pour Python)   | Complexe (SQL, ML, graphes)    |
| Scalabilité             | Horizontale native           | Horizontale via cluster        |
| Latence                 | < 10ms                       | 100ms - quelques secondes      |
| Cas d'usage typique     | Pipeline temps réel          | Analytique streaming           |

---

## Spark Structured Streaming : rappel

Spark Structured Streaming traite un flux comme une **table qui grossit infiniment** :

```
Kafka Topic "orders.created" :
┌────┬──────────┬────────┬──────────┐
│ t  │ order_id │ amount │ customer │  ← nouveaux messages arrivant
├────┼──────────┼────────┼──────────┤
│ t1 │ ORD-001  │ 149.99 │ cust-42  │
│ t2 │ ORD-002  │  89.50 │ cust-13  │
│ t3 │ ORD-003  │ 299.00 │ cust-42  │
│ t4 │ ORD-004  │  45.00 │ cust-07  │  ← continuellement appendé
└────┴──────────┴────────┴──────────┘
         ↓
   Requête SQL qui tourne en continu :
   SELECT customer, SUM(amount) FROM stream GROUP BY customer
         ↓
   Résultat mis à jour à chaque micro-batch
```

---

## Configuration de l'environnement

### Dépendances

```bash
pip install pyspark==3.5.0

# Ou dans requirements.txt
pyspark==3.5.0
```

### Packages Maven nécessaires

Spark a besoin du connecteur Kafka. On le passe via `--packages` ou dans la configuration :

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    ) \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
```

---

## Lire depuis Kafka

### Lecture en streaming

```python
# spark_kafka_reader.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, cast
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    IntegerType, ArrayType, LongType
)

spark = SparkSession.builder \
    .appName("KafkaOrderReader") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    ) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ─────────────────────────────────────────────
# 1. Lire le flux Kafka brut
# ─────────────────────────────────────────────
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders.created") \
    .option("startingOffsets", "earliest") \
    .option("maxOffsetsPerTrigger", 1000) \
    .load()

# Le DataFrame Kafka a ces colonnes :
# key (binary), value (binary), topic, partition, offset, timestamp, timestampType
print("Colonnes Kafka brutes :")
raw_stream.printSchema()
# root
#  |-- key: binary (nullable = true)
#  |-- value: binary (nullable = true)
#  |-- topic: string (nullable = true)
#  |-- partition: integer (nullable = true)
#  |-- offset: long (nullable = true)
#  |-- timestamp: timestamp (nullable = true)
#  |-- timestampType: integer (nullable = true)

# ─────────────────────────────────────────────
# 2. Définir le schéma des messages JSON
# ─────────────────────────────────────────────
order_schema = StructType([
    StructField("order_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("status", StringType()),
    StructField("created_at", StringType()),
    StructField("items", ArrayType(StructType([
        StructField("product_id", StringType()),
        StructField("quantity", IntegerType()),
        StructField("unit_price", DoubleType()),
    ]))),
])

# ─────────────────────────────────────────────
# 3. Parser le JSON depuis la colonne "value"
# ─────────────────────────────────────────────
orders_stream = raw_stream \
    .select(
        col("key").cast(StringType()).alias("partition_key"),
        col("timestamp").alias("kafka_timestamp"),
        col("partition"),
        col("offset"),
        from_json(col("value").cast(StringType()), order_schema).alias("data")
    ) \
    .select(
        col("partition_key"),
        col("kafka_timestamp"),
        col("partition"),
        col("offset"),
        col("data.*")  # Décompacter toutes les colonnes du JSON
    )

orders_stream.printSchema()

# ─────────────────────────────────────────────
# 4. Écrire dans la console (pour déboguer)
# ─────────────────────────────────────────────
query = orders_stream.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("append") \
    .trigger(processingTime="5 seconds") \
    .start()

query.awaitTermination()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer le script Spark et montrer la sortie console avec les micro-batches. Dans un autre terminal, produire des messages Kafka et montrer qu'ils apparaissent dans la sortie Spark après le délai du trigger (5 secondes).
> **Expliquer :** Expliquer la différence entre streaming continu et micro-batch : Spark regroupe les événements par petits lots (ici toutes les 5 secondes). C'est différent de Faust qui traite événement par événement. Montrer le schéma Spark après parsing JSON.

---

## Agrégations en streaming

```python
# spark_aggregations.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, cast, sum as spark_sum, count, avg,
    window, to_timestamp, current_timestamp
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

spark = SparkSession.builder \
    .appName("KafkaAggregations") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    ) \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

order_schema = StructType([
    StructField("order_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("status", StringType()),
    StructField("created_at", StringType()),
])

# Lire depuis Kafka
stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders.created") \
    .option("startingOffsets", "latest") \
    .load() \
    .select(from_json(col("value").cast(StringType()), order_schema).alias("d")) \
    .select("d.*") \
    .withColumn("event_time", to_timestamp(col("created_at")))


# ─────────────────────────────────────────────
# Agrégation 1 : CA et nb commandes par fenêtre de 1 minute
# ─────────────────────────────────────────────
revenue_per_minute = stream \
    .withWatermark("event_time", "2 minutes") \
    .groupBy(window(col("event_time"), "1 minute")) \
    .agg(
        spark_sum("amount").alias("total_revenue"),
        count("order_id").alias("order_count"),
        avg("amount").alias("avg_order_value"),
    ) \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("total_revenue"),
        col("order_count"),
        col("avg_order_value"),
    )

query1 = revenue_per_minute.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("update") \
    .trigger(processingTime="30 seconds") \
    .start()


# ─────────────────────────────────────────────
# Agrégation 2 : Top clients par CA (fenêtre glissante 5 min)
# ─────────────────────────────────────────────
top_customers = stream \
    .withWatermark("event_time", "5 minutes") \
    .groupBy(
        window(col("event_time"), "5 minutes", "1 minute"),  # slide de 1 min
        col("customer_id")
    ) \
    .agg(
        spark_sum("amount").alias("customer_revenue"),
        count("order_id").alias("order_count"),
    ) \
    .filter(col("customer_revenue") > 100)  # Seulement les clients > 100€

query2 = top_customers.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("update") \
    .trigger(processingTime="60 seconds") \
    .start()

spark.streams.awaitAnyTermination()
```

---

## Écrire dans Kafka depuis Spark

```python
# spark_to_kafka.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, to_json, struct, lit,
    cast, expr, when
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("KafkaTransform") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    ) \
    .getOrCreate()

order_schema = StructType([
    StructField("order_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("status", StringType()),
])

# Lire depuis Kafka
stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders.created") \
    .option("startingOffsets", "latest") \
    .load() \
    .select(from_json(col("value").cast(StringType()), order_schema).alias("d")) \
    .select("d.*")

# Transformation : enrichir la commande
enriched = stream \
    .withColumn("tax", col("amount") * 0.20) \
    .withColumn("total_with_tax", col("amount") * 1.20) \
    .withColumn(
        "tier",
        when(col("amount") >= 500, "vip")
        .when(col("amount") >= 100, "premium")
        .otherwise("standard")
    )

# Préparer la sortie Kafka :
# - key : customer_id (pour partitionner par client)
# - value : JSON sérialisé
output = enriched \
    .select(
        col("customer_id").alias("key"),
        to_json(struct(
            col("order_id"),
            col("customer_id"),
            col("amount"),
            col("tax"),
            col("total_with_tax"),
            col("tier"),
        )).alias("value")
    )

# Écrire dans le topic Kafka de sortie
query = output.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "orders.enriched.spark") \
    .option("checkpointLocation", "/tmp/spark-checkpoint/orders-enriched") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
```

---

## Jointure stream-stream

```python
# stream_join.py
"""
Jointure entre deux flux Kafka :
- orders.created
- payments.processed

Enrichir les commandes avec les informations de paiement.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("StreamJoin") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    ) \
    .getOrCreate()

order_schema = StructType([
    StructField("order_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("created_at", StringType()),
])

payment_schema = StructType([
    StructField("order_id", StringType()),
    StructField("transaction_id", StringType()),
    StructField("method", StringType()),
    StructField("paid_at", StringType()),
])


def read_topic(topic: str, schema: StructType):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load() \
        .select(from_json(col("value").cast(StringType()), schema).alias("d")) \
        .select("d.*")


orders = read_topic("orders.created", order_schema)
payments = read_topic("payments.processed", payment_schema)

# Watermark obligatoire pour les jointures stream-stream
orders_w = orders.withWatermark("created_at", "10 minutes")
payments_w = payments.withWatermark("paid_at", "10 minutes")

# Jointure : commande + paiement dans une fenêtre de 10 minutes
joined = orders_w.join(
    payments_w,
    expr("""
        orders_w.order_id = payments_w.order_id
        AND orders_w.created_at >= payments_w.paid_at - INTERVAL 10 MINUTES
        AND orders_w.created_at <= payments_w.paid_at + INTERVAL 10 MINUTES
    """),
    how="inner"
)

result = joined.select(
    col("orders_w.order_id"),
    col("orders_w.customer_id"),
    col("orders_w.amount"),
    col("payments_w.transaction_id"),
    col("payments_w.method").alias("payment_method"),
    col("payments_w.paid_at"),
)

query = result.writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("append") \
    .start()

query.awaitTermination()
```

---

## Écrire vers d'autres destinations

### Écriture en Parquet (Data Lake)

```python
# spark_to_parquet.py
query = enriched.writeStream \
    .format("parquet") \
    .option("path", "s3a://mon-bucket/orders/") \
    .option("checkpointLocation", "/tmp/spark-checkpoint/parquet") \
    .partitionBy("status") \
    .outputMode("append") \
    .trigger(processingTime="5 minutes") \
    .start()
```

### Écriture en base PostgreSQL

```python
# spark_to_postgres.py
def write_batch_to_postgres(batch_df, batch_id):
    """
    Appelé pour chaque micro-batch par foreachBatch.
    Permet d'utiliser n'importe quel sink batch dans un contexte streaming.
    """
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/analytics") \
        .option("dbtable", "orders_aggregated") \
        .option("user", "postgres") \
        .option("password", "postgres") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    print(f"Batch {batch_id} : {batch_df.count()} lignes écrites en PostgreSQL")

query = revenue_per_minute.writeStream \
    .foreachBatch(write_batch_to_postgres) \
    .option("checkpointLocation", "/tmp/spark-checkpoint/postgres") \
    .outputMode("update") \
    .trigger(processingTime="1 minute") \
    .start()
```

---

## Monitoring et checkpoints

```python
# monitoring.py
"""
Surveiller l'état d'une query Spark Streaming.
"""

def monitor_query(query):
    """Affiche les métriques de la query en cours."""
    status = query.status
    progress = query.lastProgress

    print(f"Query : {query.name}")
    print(f"Active : {query.isActive}")
    print(f"Status : {status['message']}")

    if progress:
        print(f"Trigger : {progress['trigger']}")
        print(f"Input rows/s : {progress.get('inputRowsPerSecond', 0):.1f}")
        print(f"Processed rows/s : {progress.get('processedRowsPerSecond', 0):.1f}")
        print(f"Batch duration : {progress.get('batchDuration', 0)}ms")

# Appeler périodiquement
import time
while query.isActive:
    monitor_query(query)
    time.sleep(30)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer le pipeline Spark complet (lecture Kafka → transformation → écriture Kafka), puis dans Kafka UI montrer les messages dans `orders.enriched.spark`. Comparer un message d'entrée (`orders.created`) et le message de sortie enrichi (`orders.enriched.spark`).
> **Expliquer :** Pointer les différences clés entre Spark et Faust : Spark est orienté micro-batch (adapté aux analyses complexes), Faust est orienté événement par événement (adapté aux réactions temps réel). Expliquer le checkpoint : Spark sauvegarde sa position dans Kafka dans un répertoire local/S3 — si le job redémarre, il reprend exactement où il s'était arrêté.

---

## Architecture Lambda vs Kappa

### Architecture Lambda

```
[Kafka]
   │
   ├── Speed Layer (Spark Streaming) ──→ Vue temps réel (approximative)
   │                                        ↓
   └── Batch Layer (Spark Batch)    ──→ Vue exacte (toutes les heures)
              ↑
              ↓
         [Data Lake (Parquet)]
```

### Architecture Kappa

```
[Kafka] (conservation longue durée des events)
   │
   └── Streaming Layer (Spark/Faust)
          │
          ├── Vue temps réel (résultats courants)
          └── Rejeu depuis Kafka pour corriger les bugs
```

La **Kappa Architecture** (recommandée aujourd'hui) simplifie l'Architecture Lambda en n'ayant qu'un seul layer de traitement, rendu possible par la capacité de Kafka à rejouer les événements.

---

## Résumé

| Concept                    | Description                                              |
|----------------------------|----------------------------------------------------------|
| `readStream.format("kafka")`| Lire un flux Kafka dans Spark                            |
| `from_json()`              | Parser la valeur binaire Kafka en struct typé            |
| `withWatermark()`          | Définir le délai max pour les données tardives           |
| `window()`                 | Agréger sur une fenêtre temporelle                       |
| `writeStream.format("kafka")`| Écrire le résultat dans un topic Kafka                 |
| `foreachBatch()`           | Traiter chaque batch avec du code batch arbitraire       |
| Checkpoint                 | Sauvegarde de la position pour reprendre après un crash  |
| Trigger                    | Fréquence de traitement des micro-batches                |
