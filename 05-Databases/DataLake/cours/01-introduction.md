# Module 01 - Introduction au Data Lake

## Qu'est-ce qu'un Data Lake ?

Un **Data Lake** (lac de donnees) est un systeme de stockage centralise qui permet de stocker des donnees **brutes** a grande echelle, dans leur format natif, sans transformation prealable.

### Definition

> "Un Data Lake est un depot de stockage qui conserve une vaste quantite de donnees brutes dans leur format natif jusqu'a ce qu'elles soient necessaires pour l'analyse."
> -- James Dixon, CTO de Pentaho (2010)

### Les caracteristiques fondamentales

| Caracteristique | Description | Exemple |
|-----------------|-------------|---------|
| **Stockage brut** | Donnees conservees dans leur format d'origine | JSON, CSV, Parquet, images, videos |
| **Schema-on-read** | Le schema est applique a la lecture, pas a l'ecriture | Structure definie au moment de l'analyse |
| **Scalable** | Capacite de stockage quasi illimitee | Petaoctets de donnees a faible cout |
| **Multi-format** | Supporte tous les types de donnees | Structure, semi-structure, non-structure |
| **Centralise** | Point unique de stockage | Toutes les sources reunies |

## Historique et contexte

### L'evolution du stockage analytique

```
Annees 1990          Annees 2000          Annees 2010          Annees 2020+
+-----------+       +-----------+       +-----------+       +-----------+
|   Data    |       |   Data    |       |   Data    |       | Lakehouse |
| Warehouse |  -->  | Warehouse |  -->  |   Lake    |  -->  |  (DW+DL)  |
|  (Inmon)  |       |  + ETL    |       | + Big Data|       | + Delta   |
+-----------+       +-----------+       +-----------+       +-----------+
 Donnees             Volumes             Hadoop/S3           Best of
 structurees         croissants          Tout type           both worlds
```

### Pourquoi le Data Lake est-il apparu ?

**Limites du Data Warehouse traditionnel :**

1. **Cout de stockage eleve** : stocker des To de donnees en DW coute cher
2. **Schema rigide** : obligation de definir le schema avant l'ingestion (schema-on-write)
3. **Donnees structurees uniquement** : pas de support natif pour images, logs, JSON imbrique
4. **Temps d'integration long** : chaque nouvelle source necessite un processus ETL complet
5. **Explosion des volumes** : Big Data (logs, IoT, reseaux sociaux) depasse les capacites des DW

**La reponse du Data Lake :**

| Limite du DW | Solution Data Lake |
|--------------|-------------------|
| Cout eleve | Stockage objet bon marche (S3 : ~0.023$/Go/mois) |
| Schema rigide | Schema-on-read : stocker d'abord, structurer ensuite |
| Structure uniquement | Tous formats : CSV, JSON, Parquet, images, videos |
| Integration lente | Ingestion rapide : deposer les fichiers tels quels |
| Volumes limites | Scalabilite horizontale quasi infinie |

## Les types de donnees dans un Data Lake

### Donnees structurees

Donnees avec un schema fixe et predefini :
- Tables relationnelles (exports SQL)
- Fichiers CSV avec colonnes definies
- Donnees ERP/CRM

```
+----------+-----------+--------+------------+
| order_id | client_id | amount | order_date |
+----------+-----------+--------+------------+
| 1001     | C-42      | 150.00 | 2024-01-15 |
| 1002     | C-17      | 89.99  | 2024-01-16 |
+----------+-----------+--------+------------+
```

### Donnees semi-structurees

Donnees avec une structure flexible, auto-descriptive :
- JSON, XML
- Logs applicatifs
- Donnees IoT

```json
{
  "event": "page_view",
  "user": {
    "id": "U-12345",
    "segment": "premium"
  },
  "page": "/products/shoes",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "device": "mobile",
    "browser": "Chrome",
    "custom_tags": ["promo", "winter-sale"]
  }
}
```

### Donnees non-structurees

Donnees sans schema predefini :
- Images et videos
- Documents PDF, Word
- Fichiers audio
- Emails

```
Data Lake
+-- images/
|   +-- product_001.jpg    (2.3 Mo)
|   +-- product_002.png    (1.8 Mo)
+-- documents/
|   +-- contrat_2024.pdf   (450 Ko)
+-- audio/
    +-- call_recording.mp3 (15 Mo)
```

## Cas d'usage du Data Lake

### 1. Centralisation des donnees

Agreger toutes les sources de l'entreprise en un seul endroit :

```
Sources                          Data Lake
+-----------+                   +---------------------------+
| ERP       |----+              | /raw/erp/                 |
+-----------+    |              | /raw/crm/                 |
+-----------+    +----------->  | /raw/web_analytics/       |
| CRM       |----+              | /raw/iot_sensors/         |
+-----------+    |              | /raw/social_media/        |
+-----------+    |              | /raw/documents/           |
| Web logs  |----+              +---------------------------+
+-----------+    |
+-----------+    |
| IoT       |----+
+-----------+
```

### 2. Data Science et Machine Learning

- Acces aux donnees brutes pour le feature engineering
- Entrainement de modeles sur des datasets volumineux
- Experimentation sans impacter les systemes de production

### 3. Archivage et conformite

- Conservation longue duree a faible cout
- Conformite reglementaire (RGPD, SOX) : conserver les donnees brutes
- Audit trail complet

### 4. Analytics avancee

- Analyse exploratoire sur des donnees variees
- Croisement de sources heterogenes
- Analyse de sentiments sur les reseaux sociaux

### 5. Ingestion IoT / Streaming

- Collecte de millions d'evenements par seconde
- Stockage de series temporelles a grande echelle
- Analyse en temps reel et batch sur les memes donnees

## Schema-on-read vs Schema-on-write

C'est la difference fondamentale entre Data Lake et Data Warehouse :

### Schema-on-write (Data Warehouse)

```
Donnees brutes --> [Definir le schema] --> [Transformer] --> [Charger] --> Requeter
                          |
                   On DOIT connaitre
                   la structure AVANT
                   de stocker
```

**Avantages :** Donnees propres, requetes rapides, coherence garantie
**Inconvenients :** Lent a mettre en place, rigide, perte de donnees potentielle

### Schema-on-read (Data Lake)

```
Donnees brutes --> [Stocker tel quel] --> ... --> [Definir le schema] --> Requeter
                          |                              |
                   On stocke TOUT                  On definit la
                   immediatement                   structure au moment
                                                   de l'ANALYSE
```

**Avantages :** Ingestion rapide, flexibilite maximale, pas de perte de donnees
**Inconvenients :** Qualite variable, requetes potentiellement lentes, risque de "Data Swamp"

### Comparaison directe

```
                   Schema-on-Write          Schema-on-Read
                   +-----------------+      +-----------------+
 Ingestion         | Lente (ETL)     |      | Rapide (ELT)    |
 Flexibilite       | Faible          |      | Haute            |
 Qualite donnees   | Haute           |      | Variable         |
 Performance query | Rapide          |      | Depend du format |
 Cout initial      | Eleve           |      | Faible           |
 Risque            | Rigidite        |      | Data Swamp       |
                   +-----------------+      +-----------------+
```

## Data Lake : les acteurs cles

### Stockage objet Cloud

| Fournisseur | Service | Particularite |
|-------------|---------|---------------|
| **AWS** | Amazon S3 | Leader du marche, ecosysteme le plus riche |
| **Azure** | Azure Data Lake Storage Gen2 (ADLS) | Integration Microsoft, hierarchie de fichiers |
| **GCP** | Google Cloud Storage (GCS) | Integration BigQuery native |

### Frameworks de traitement

| Technologie | Role | Quand l'utiliser |
|-------------|------|------------------|
| **Apache Spark** | Traitement distribue batch/streaming | Gros volumes, transformations complexes |
| **Apache Hive** | SQL sur Data Lake (via Hadoop) | Requetes SQL sur fichiers HDFS/S3 |
| **Presto / Trino** | Moteur SQL federe | Requetes interactives multi-sources |
| **Apache Flink** | Traitement streaming | Temps reel, faible latence |
| **dbt** | Transformation SQL | Modelisation, tests, documentation |

### Formats de table ouverts (Table Formats)

| Technologie | Createur | Apport |
|-------------|----------|--------|
| **Delta Lake** | Databricks | ACID sur Data Lake, time travel |
| **Apache Iceberg** | Netflix/Apple | Schema evolution, partition evolution |
| **Apache Hudi** | Uber | Upserts efficaces, incremental processing |

## Points cles a retenir

- Un Data Lake stocke les donnees **brutes** dans leur **format natif** a **faible cout**
- Il applique le principe de **Schema-on-read** : stocker d'abord, structurer ensuite
- Il supporte **tous les types de donnees** : structurees, semi-structurees, non-structurees
- Il est ne des **limites du Data Warehouse** face au Big Data
- Les **formats de table ouverts** (Delta, Iceberg, Hudi) ajoutent ACID et gouvernance
- Sans gouvernance, un Data Lake devient un **Data Swamp** (marecage de donnees)

---

**Prochain module :** [02 - Architecture d'un Data Lake](./02-architecture.md)

[Retour au sommaire](./README.md)
