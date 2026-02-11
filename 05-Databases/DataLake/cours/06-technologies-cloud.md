# Module 06 - Technologies et plateformes Cloud

## Le Data Lake dans le Cloud

Aujourd'hui, la quasi-totalite des Data Lakes sont deployes dans le Cloud. Le stockage objet (S3, ADLS, GCS) est devenu le standard grace a son cout faible, sa scalabilite infinie et son ecosysteme riche.

```
On-Premise (ancien)                    Cloud (moderne)
+---------------------------+         +---------------------------+
| HDFS (Hadoop)             |         | S3 / ADLS / GCS           |
| Serveurs physiques        |         | Stockage objet manage     |
| Administration manuelle   |         | Pas d'infrastructure      |
| Scalabilite limitee       |         | Scalabilite infinie       |
| Cout eleve (materiel)     |         | Pay-as-you-go             |
+---------------------------+         +---------------------------+
```

## AWS : Amazon S3 + Ecosysteme

### Amazon S3 (Simple Storage Service)

S3 est le **stockage objet le plus utilise** pour les Data Lakes dans le monde.

```
Architecture Data Lake AWS
+---------------------------------------------------------------+
|                        AWS Account                            |
|                                                               |
|  +------------------+    +------------------+                 |
|  | S3 Bucket        |    | AWS Glue         |                 |
|  | s3://my-lake/    |    | - Crawlers       |                 |
|  | +-- raw/         |    | - Data Catalog   |                 |
|  | +-- curated/     |    | - ETL Jobs       |                 |
|  | +-- consumption/ |    +--------+---------+                 |
|  +--------+---------+             |                           |
|           |                       |                           |
|  +--------v---------+    +--------v---------+                 |
|  | Amazon Athena    |    | AWS Glue Jobs    |                 |
|  | (SQL serverless) |    | (Spark manage)   |                 |
|  +------------------+    +------------------+                 |
|                                                               |
|  +------------------+    +------------------+                 |
|  | Amazon Redshift  |    | Amazon EMR       |                 |
|  | Spectrum         |    | (Spark/Hive)     |                 |
|  | (DW + Lake)      |    |                  |                 |
|  +------------------+    +------------------+                 |
+---------------------------------------------------------------+
```

### Classes de stockage S3

| Classe | Usage | Cout stockage | Cout acces |
|--------|-------|---------------|------------|
| **S3 Standard** | Donnees actives, acces frequent | $0.023/Go | Faible |
| **S3 Infrequent Access** | Zone Raw ancienne | $0.0125/Go | Moyen |
| **S3 Glacier Instant** | Archives, acces occasionnel | $0.004/Go | Eleve |
| **S3 Glacier Deep Archive** | Archives long terme | $0.00099/Go | Tres eleve |

**Lifecycle policies :** Automatiser le deplacement entre classes

```
Jour 0-30  : S3 Standard         (acces frequent)
Jour 30-90 : S3 Infrequent Access (acces rare)
Jour 90+   : S3 Glacier          (archivage)
Jour 365+  : S3 Glacier Deep     (conformite)
```

### Services cles de l'ecosysteme AWS

| Service | Role | Equivalent |
|---------|------|-----------|
| **Amazon S3** | Stockage objet | ADLS, GCS |
| **AWS Glue** | ETL serverless + Data Catalog | ADF, Dataflow |
| **Amazon Athena** | SQL serverless sur S3 | Synapse Serverless, BigQuery |
| **Amazon EMR** | Cluster Spark/Hadoop manage | HDInsight, Dataproc |
| **AWS Lake Formation** | Gouvernance et securite | Purview, Dataplex |
| **Amazon Kinesis** | Streaming | Event Hubs, Pub/Sub |
| **Amazon Redshift Spectrum** | DW + query S3 | Synapse, BigQuery |

## Azure : ADLS Gen2 + Ecosysteme

### Azure Data Lake Storage Gen2

ADLS Gen2 combine les capacites de **Blob Storage** et d'un **systeme de fichiers hierarchique** (HNS - Hierarchical Namespace).

```
Architecture Data Lake Azure
+---------------------------------------------------------------+
|                     Azure Subscription                        |
|                                                               |
|  +------------------+    +------------------+                 |
|  | ADLS Gen2        |    | Azure Purview    |                 |
|  | Storage Account  |    | - Data Catalog   |                 |
|  | +-- raw/         |    | - Lineage        |                 |
|  | +-- curated/     |    | - Classification |                 |
|  | +-- consumption/ |    +--------+---------+                 |
|  +--------+---------+             |                           |
|           |                       |                           |
|  +--------v---------+    +--------v---------+                 |
|  | Azure Synapse    |    | Azure Data       |                 |
|  | Analytics        |    | Factory (ADF)    |                 |
|  | - SQL Serverless |    | - Orchestration  |                 |
|  | - Spark Pools    |    | - Pipelines      |                 |
|  | - Dedicated SQL  |    | - Dataflows      |                 |
|  +------------------+    +------------------+                 |
|                                                               |
|  +------------------+    +------------------+                 |
|  | Azure Databricks |    | Microsoft Fabric |                 |
|  | (Spark + Delta)  |    | (Lakehouse)      |                 |
|  +------------------+    +------------------+                 |
+---------------------------------------------------------------+
```

### Particularites ADLS Gen2

| Feature | Description |
|---------|-------------|
| **Hierarchical Namespace** | Vrai systeme de fichiers (rename atomique, permissions par dossier) |
| **Integration AAD** | Securite via Azure Active Directory (RBAC natif) |
| **ACL POSIX** | Permissions fines par fichier/dossier (Unix-like) |
| **Tiers de stockage** | Hot, Cool, Cold, Archive |
| **Integration Synapse** | Requetes SQL directes sur le lake |

### Services cles de l'ecosysteme Azure

| Service | Role | Equivalent |
|---------|------|-----------|
| **ADLS Gen2** | Stockage objet + fichiers | S3, GCS |
| **Azure Data Factory** | Orchestration ETL | Glue, Cloud Composer |
| **Azure Synapse Analytics** | Plateforme analytique unifiee | Redshift+Athena+EMR |
| **Azure Databricks** | Spark + Delta Lake | EMR+Databricks, Dataproc |
| **Azure Purview** | Gouvernance, catalogue, lineage | Lake Formation, Dataplex |
| **Azure Event Hubs** | Streaming | Kinesis, Pub/Sub |
| **Microsoft Fabric** | Lakehouse tout-en-un | Pas d'equivalent direct |

## GCP : Google Cloud Storage + Ecosysteme

### Google Cloud Storage (GCS)

```
Architecture Data Lake GCP
+---------------------------------------------------------------+
|                     GCP Project                               |
|                                                               |
|  +------------------+    +------------------+                 |
|  | GCS Buckets      |    | Dataplex         |                 |
|  | gs://my-lake/    |    | - Data Catalog   |                 |
|  | +-- raw/         |    | - Data Quality   |                 |
|  | +-- curated/     |    | - Gouvernance    |                 |
|  | +-- consumption/ |    +--------+---------+                 |
|  +--------+---------+             |                           |
|           |                       |                           |
|  +--------v---------+    +--------v---------+                 |
|  | BigQuery         |    | Cloud Composer   |                 |
|  | - External tables|    | (Airflow manage) |                 |
|  | - BigLake        |    |                  |                 |
|  | - SQL natif      |    |                  |                 |
|  +------------------+    +------------------+                 |
|                                                               |
|  +------------------+    +------------------+                 |
|  | Dataproc         |    | Dataflow         |                 |
|  | (Spark manage)   |    | (Apache Beam)    |                 |
|  +------------------+    +------------------+                 |
+---------------------------------------------------------------+
```

### Particularites GCP

| Feature | Description |
|---------|-------------|
| **BigQuery External Tables** | Requeter GCS directement depuis BigQuery |
| **BigLake** | Tables unifiees sur GCS avec gouvernance |
| **Dataplex** | Gouvernance, qualite, decouverte automatique |
| **Separation compute/storage** | Facturation independante |

### Services cles de l'ecosysteme GCP

| Service | Role | Equivalent |
|---------|------|-----------|
| **Google Cloud Storage** | Stockage objet | S3, ADLS |
| **BigQuery** | DW + SQL sur lake | Redshift+Athena, Synapse |
| **Dataproc** | Cluster Spark manage | EMR, HDInsight |
| **Dataflow** | ETL streaming (Apache Beam) | Kinesis Analytics, Stream Analytics |
| **Cloud Composer** | Orchestration (Airflow) | MWAA, ADF |
| **Dataplex** | Gouvernance Data Lake | Lake Formation, Purview |
| **Pub/Sub** | Messaging streaming | Kinesis, Event Hubs |

## Comparaison des 3 clouds

### Stockage

| Critere | AWS S3 | Azure ADLS Gen2 | GCP GCS |
|---------|--------|-----------------|---------|
| Cout (Standard/Go/mois) | $0.023 | $0.020 | $0.020 |
| Systeme de fichiers | Non (objet plat) | Oui (HNS) | Non (objet plat) |
| Versioning | Oui | Oui (Blob) | Oui |
| Lifecycle policies | Oui | Oui | Oui |
| Encryption | SSE-S3, SSE-KMS | Microsoft-managed, CMK | Google-managed, CMEK |
| Maturite | +++ (leader) | ++ | ++ |

### SQL sur le Data Lake (serverless)

| Critere | Athena | Synapse Serverless | BigQuery External |
|---------|--------|-------------------|-------------------|
| Moteur | Trino (Presto) | SQL Server | BigQuery |
| Format natif | Parquet, ORC, JSON, CSV | Parquet, Delta, CSV | Parquet, ORC, Avro, JSON |
| Table Format | Iceberg, Hudi, Delta | Delta Lake | Iceberg, BigLake |
| Cout | $5/To scanne | $5/To traite | $6.25/To traite |
| Performance | Bonne | Bonne | Excellente |

### Gouvernance

| Critere | Lake Formation | Purview | Dataplex |
|---------|---------------|---------|----------|
| Catalogue | Glue Catalog | Purview Catalog | Data Catalog |
| Lineage | Basique | Avance | Avance |
| Classification auto | Oui | Oui (AI) | Oui |
| Row/Column security | Oui | Via Synapse | Via BigQuery |

## Databricks : la plateforme unifiee

Databricks fonctionne sur **les 3 clouds** et propose une experience unifiee avec **Delta Lake** comme format de table.

```
+-----------------------------------------------------------+
|                    Databricks Lakehouse                    |
|                                                           |
|  +------------------+  +------------------+               |
|  | Unity Catalog    |  | Delta Lake       |               |
|  | - Gouvernance    |  | - ACID           |               |
|  | - Lineage        |  | - Time Travel    |               |
|  | - Acces fin      |  | - Schema Evol.   |               |
|  +------------------+  +------------------+               |
|                                                           |
|  +------------------+  +------------------+               |
|  | SQL Warehouses   |  | Notebooks        |               |
|  | (SQL analytics)  |  | (Python/Scala/R) |               |
|  +------------------+  +------------------+               |
|                                                           |
|  +------------------+  +------------------+               |
|  | MLflow           |  | Workflows        |               |
|  | (ML lifecycle)   |  | (Orchestration)  |               |
|  +------------------+  +------------------+               |
|                                                           |
|  Deploye sur : AWS (S3) | Azure (ADLS) | GCP (GCS)       |
+-----------------------------------------------------------+
```

## Guide de choix de la plateforme

```
Quel cloud pour votre Data Lake ?

Deja sur un cloud ?
+-- AWS          --> S3 + Glue + Athena (ou Databricks)
+-- Azure        --> ADLS + Synapse (ou Fabric, ou Databricks)
+-- GCP          --> GCS + BigQuery (ou Databricks)
+-- Multi-cloud  --> Databricks (fonctionne partout)

Equipe existante ?
+-- Competences Microsoft / SQL Server --> Azure
+-- Competences open source / Hadoop   --> AWS
+-- Competences BigQuery / Analytics   --> GCP

Budget serre ?
+-- Serverless pur --> Athena / BigQuery / Synapse Serverless
+-- Volumes eleves --> Negocier reserved capacity
```

## Points cles a retenir

- Les 3 clouds (AWS, Azure, GCP) offrent des stacks Data Lake completes et matures
- **S3** est le leader historique, **ADLS Gen2** se distingue par le HNS, **GCS** par l'integration BigQuery
- Le **SQL serverless** (Athena, Synapse, BigQuery) permet de requeter le lake sans infrastructure
- **Databricks** offre une experience unifiee multi-cloud avec Delta Lake
- **Microsoft Fabric** est l'offre integree la plus recente (Lakehouse tout-en-un)
- Le choix depend souvent de l'**ecosysteme existant** et des **competences de l'equipe**

---

**Prochain module :** [07 - Data Lake vs Data Warehouse vs Lakehouse](./07-comparaison-architectures.md)

[Retour au sommaire](./README.md)
