# Brief : Construction d'un Data Lake E-commerce avec MinIO, Spark et Delta Lake

## Informations

| Critere | Valeur |
|---------|--------|
| **Duree** | 3 jours (21 heures) |
| **Niveau** | Intermediaire |
| **Modalite** | Individuel |
| **Technologies** | Docker, MinIO (S3), PySpark, Delta Lake, Great Expectations, Python |
| **Prerequis** | [Cours Data Lake](../../../05-Databases/DataLake/cours/) + [Cours Spark](../../../06-Data-Engineering/Spark/) + Notions Docker |

## Contexte

Vous etes Data Engineer chez **StreamCart**, une marketplace en ligne qui vend des produits electroniques, des vetements et des articles de maison. L'entreprise genere chaque jour des donnees provenant de **4 systemes differents** :

- **ERP interne** : commandes, produits, stocks (CSV exports quotidiens)
- **CRM Salesforce** : clients, interactions, segments (JSON API dumps)
- **Application web** : clickstream / evenements de navigation (JSON logs)
- **Service livraison** : suivi des expeditions (CSV partenaire externe)

Aujourd'hui, chaque equipe travaille avec ses propres fichiers sur un disque partage. Les analystes passent **2 jours par semaine** a chercher, nettoyer et croiser les donnees manuellement. Le CTO veut un **Data Lake centralise** pour :

1. Centraliser toutes les sources dans un point unique
2. Garantir la qualite et la tracabilite des donnees
3. Permettre aux analystes de requeter les donnees propres en self-service
4. Preparer le terrain pour un futur projet de recommandation produit (ML)

## Objectifs pedagogiques

A l'issue de ce brief, vous serez capable de :

- Deployer un Data Lake local avec **MinIO** (compatible S3) via Docker
- Implementer l'architecture **3 zones** (Raw / Curated / Consumption)
- Ingerer des donnees multi-format (CSV, JSON) dans la zone Raw
- Transformer les donnees avec **PySpark** (nettoyage, deduplication, typage)
- Utiliser **Delta Lake** pour ajouter ACID, time travel et schema enforcement
- Mettre en place des **controles de qualite** automatises
- Construire un **Data Catalog** simple (metadonnees, documentation)
- Respecter les **bonnes pratiques** : partitionnement, nommage, compression

## Architecture cible

```
+-------+  +-------+  +-------+  +---------+
|  ERP  |  |  CRM  |  |  Web  |  |Livraison|
| (CSV) |  |(JSON) |  |(JSON) |  |  (CSV)  |
+---+---+  +---+---+  +---+---+  +----+----+
    |          |          |            |
    +-----+----+-----+----+-----+-----+
          |          |          |
    +-----v----------v----------v------+
    |        SCRIPTS D'INGESTION       |
    |          (Python)                |
    +-----+----------+----------+------+
          |          |          |
+---------v----------v----------v---------+
|              MinIO (S3)                 |
|                                         |
|  +-----------------------------------+  |
|  |         ZONE RAW (Bronze)         |  |
|  |  Donnees brutes, immutables       |  |
|  |  Format: CSV / JSON d'origine     |  |
|  +----------------+------------------+  |
|                   |                     |
|         [PySpark + Delta Lake]          |
|         Nettoyage, validation           |
|                   |                     |
|  +----------------v------------------+  |
|  |       ZONE CURATED (Silver)       |  |
|  |  Donnees nettoyees, typees        |  |
|  |  Format: Delta Lake (Parquet)     |  |
|  +----------------+------------------+  |
|                   |                     |
|         [PySpark + Delta Lake]          |
|         Agregation, jointures           |
|                   |                     |
|  +----------------v------------------+  |
|  |     ZONE CONSUMPTION (Gold)       |  |
|  |  Data Marts, KPIs pre-calcules    |  |
|  |  Format: Delta Lake (Parquet)     |  |
|  +-----------------------------------+  |
+-----------------------------------------+
```

## Donnees fournies

Les donnees sont fournies dans le dossier `data/` de ce brief.

### 1. ERP - Commandes : `erp_orders.csv`

```csv
order_id,order_date,customer_id,product_id,quantity,unit_price,discount_pct,status,payment_method
ORD-0001,2024-01-15 10:23:45,CUST-042,PROD-101,2,49.99,0,completed,credit_card
ORD-0002,2024-01-15 11:05:12,CUST-017,PROD-203,1,129.00,10,completed,paypal
```

~5000 lignes, couvre Janvier a Juin 2024.

### 2. ERP - Produits : `erp_products.csv`

```csv
product_id,name,category,sub_category,brand,cost_price,selling_price,weight_kg
PROD-101,Casque Bluetooth,Electronics,Audio,SoundMax,22.50,49.99,0.35
```

~200 produits.

### 3. CRM - Clients : `crm_customers.json`

```json
[
  {
    "customer_id": "CUST-042",
    "email": "Alice.Dupont@Gmail.com",
    "first_name": "Alice",
    "last_name": "Dupont",
    "phone": "+33 6 12 34 56 78",
    "city": "Paris",
    "country": "FR",
    "registration_date": "2023-06-15",
    "segment": "Premium",
    "gdpr_consent": true
  }
]
```

~1500 clients. Contient des **donnees personnelles (PII)**.

### 4. Web - Clickstream : `web_events.json`

```json
{"event_id": "EVT-00001", "timestamp": "2024-01-15T10:20:30Z", "user_id": "CUST-042", "event_type": "page_view", "page": "/products/PROD-101", "device": "mobile", "browser": "Chrome", "session_id": "SESS-abc123"}
{"event_id": "EVT-00002", "timestamp": "2024-01-15T10:20:45Z", "user_id": "CUST-042", "event_type": "add_to_cart", "page": "/products/PROD-101", "device": "mobile", "browser": "Chrome", "session_id": "SESS-abc123"}
```

~50 000 evenements (JSON Lines / NDJSON).

### 5. Livraison - Expeditions : `delivery_shipments.csv`

```csv
shipment_id,order_id,carrier,tracking_number,shipped_date,delivered_date,status
SHP-0001,ORD-0001,Colissimo,COL123456789,2024-01-16,2024-01-18,delivered
SHP-0002,ORD-0002,Chronopost,CHR987654321,2024-01-16,,in_transit
```

~4500 expeditions.

### Problemes de qualite volontaires dans les donnees

Les donnees contiennent intentionnellement des problemes que vous devrez gerer :

| Probleme | Fichier | Detail |
|----------|---------|--------|
| Doublons | `erp_orders.csv` | ~50 commandes en double |
| Valeurs nulles | `crm_customers.json` | emails et telephones manquants |
| Formats de dates inconsistants | `delivery_shipments.csv` | Mix `YYYY-MM-DD` et `DD/MM/YYYY` |
| Montants negatifs | `erp_orders.csv` | ~10 commandes avec prix negatifs |
| Emails invalides | `crm_customers.json` | Emails mal formates |
| Doublons d'evenements | `web_events.json` | ~500 evenements en double (retry) |
| Statuts inconsistants | `erp_orders.csv` | Mix majuscules/minuscules |
| Caracteres speciaux | `erp_products.csv` | Noms de produits avec accents et caracteres speciaux |

---

## JOUR 1 : Infrastructure et Zone Raw (7h)

### Partie 1 : Setup de l'infrastructure (2h)

#### Tache 1.1 : Docker Compose

Creer un fichier `docker-compose.yml` qui lance :

- **MinIO** : stockage S3-compatible (port 9000 pour l'API, 9001 pour la console)
- **Spark** : un master + un worker (ou utiliser PySpark local)

```yaml
# Structure attendue
services:
  minio:
    image: minio/minio
    # ... configuration
  spark-master:
    image: bitnami/spark
    # ... configuration (optionnel, PySpark local accepte)
```

- [ ] Creer le `docker-compose.yml`
- [ ] Demarrer les services : `docker compose up -d`
- [ ] Verifier l'acces a la console MinIO : `http://localhost:9001`

#### Tache 1.2 : Creer les buckets (zones)

Via la console MinIO ou le CLI `mc` :

- [ ] Creer le bucket `streamcart-raw`
- [ ] Creer le bucket `streamcart-curated`
- [ ] Creer le bucket `streamcart-consumption`

#### Tache 1.3 : Configurer l'acces S3

Creer un script `config/s3_config.py` qui configure la connexion MinIO compatible S3 :

```python
# Configuration MinIO pour PySpark
S3_ENDPOINT = "http://localhost:9000"
S3_ACCESS_KEY = "minioadmin"
S3_SECRET_KEY = "minioadmin"

BUCKETS = {
    "raw": "s3a://streamcart-raw",
    "curated": "s3a://streamcart-curated",
    "consumption": "s3a://streamcart-consumption",
}
```

- [ ] Creer le fichier de configuration
- [ ] Tester la connexion depuis PySpark

**Livrable :** `docker-compose.yml` fonctionnel + screenshot de la console MinIO montrant les 3 buckets.

---

### Partie 2 : Ingestion dans la Zone Raw (2h30)

#### Tache 2.1 : Script d'ingestion generique

Creer `scripts/ingest_to_raw.py` : un script Python qui :

1. Prend en parametre : chemin du fichier source, nom de la source, nom de l'entite
2. Upload le fichier dans MinIO avec la convention de nommage :
   ```
   s3a://streamcart-raw/{source}/{entite}/ingestion_date={YYYY-MM-DD}/{fichier}
   ```
3. Ajoute un fichier de metadonnees `_metadata.json` contenant :
   - `source_file` : nom du fichier original
   - `ingestion_timestamp` : horodatage UTC
   - `file_size_bytes` : taille du fichier
   - `row_count` : nombre de lignes (pour CSV) ou d'objets (pour JSON)
   - `file_format` : csv / json
   - `md5_checksum` : hash du fichier

- [ ] Creer le script d'ingestion
- [ ] Le script doit etre **idempotent** (re-executable sans duplication)

#### Tache 2.2 : Ingerer toutes les sources

Executer le script pour chaque source :

- [ ] `erp/orders/` : ingerer `erp_orders.csv`
- [ ] `erp/products/` : ingerer `erp_products.csv`
- [ ] `crm/customers/` : ingerer `crm_customers.json`
- [ ] `web/events/` : ingerer `web_events.json`
- [ ] `delivery/shipments/` : ingerer `delivery_shipments.csv`

#### Tache 2.3 : Verifier la zone Raw

- [ ] Lister les fichiers dans MinIO et verifier l'arborescence
- [ ] Verifier que chaque dossier contient un `_metadata.json`
- [ ] Verifier que les fichiers sont identiques aux originaux (checksum)

**Livrable :** Script `ingest_to_raw.py` + screenshot de l'arborescence dans MinIO.

---

### Partie 3 : Spark et lecture de la Zone Raw (2h30)

#### Tache 3.1 : Configurer PySpark avec MinIO

Creer `scripts/spark_session.py` :

```python
from pyspark.sql import SparkSession

def get_spark_session(app_name="StreamCart-DataLake"):
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages",
                "io.delta:delta-spark_2.12:3.1.0,"
                "org.apache.hadoop:hadoop-aws:3.3.4") \
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()
    return spark
```

- [ ] Configurer la session Spark avec Delta Lake + S3 (MinIO)
- [ ] Verifier la lecture d'un fichier CSV depuis la zone Raw

#### Tache 3.2 : Explorer les donnees brutes

Creer un notebook `notebooks/01_exploration_raw.ipynb` qui :

- [ ] Lit chaque source depuis la zone Raw
- [ ] Affiche le schema infere (`printSchema()`)
- [ ] Affiche les premieres lignes (`show()`)
- [ ] Compte les lignes et identifie les problemes de qualite
- [ ] Documente les anomalies trouvees dans une cellule Markdown

**Livrable :** Notebook d'exploration avec les anomalies documentees.

---

## JOUR 2 : Zones Curated et Consumption (7h)

### Partie 4 : Zone Curated - Transformations (4h)

#### Tache 4.1 : Transformer les commandes (orders)

Creer `scripts/transform_orders.py` qui lit depuis Raw et ecrit dans Curated :

| Transformation | Detail |
|---------------|--------|
| Deduplication | Supprimer les doublons sur `order_id` (garder le plus recent) |
| Typage | `order_date` en TIMESTAMP, `quantity` en INT, `unit_price` en DECIMAL |
| Nettoyage | Statuts en majuscules, suppression des prix negatifs |
| Calcul | `line_total = quantity * unit_price * (1 - discount_pct/100)` |
| Metadata | Ajouter `_processed_at`, `_source_file` |

- [ ] Ecrire en **Delta Lake** dans `s3a://streamcart-curated/erp/orders/`
- [ ] Partitionner par `year` et `month` (extraits de `order_date`)
- [ ] Verifier : `spark.read.format("delta").load(path).count()`

#### Tache 4.2 : Transformer les clients (customers)

Creer `scripts/transform_customers.py` :

| Transformation | Detail |
|---------------|--------|
| Email | Lowercase, suppression des espaces, validation regex basique |
| Telephone | Format standardise ou NULL si invalide |
| PII | Creer une version `_hashed` de l'email (SHA-256) pour la zone Consumption |
| Deduplication | Sur `customer_id` |
| RGPD | Exclure les clients avec `gdpr_consent = false` de la zone Consumption |

- [ ] Ecrire en Delta Lake dans `s3a://streamcart-curated/crm/customers/`

#### Tache 4.3 : Transformer les evenements web (events)

Creer `scripts/transform_events.py` :

| Transformation | Detail |
|---------------|--------|
| Deduplication | Sur `event_id` (retirer les doublons de retry) |
| Typage | `timestamp` en TIMESTAMP |
| Extraction | Extraire `product_id` depuis le champ `page` (regex) |
| Session | Garder les sessions valides (au moins 1 evenement) |

- [ ] Ecrire en Delta Lake dans `s3a://streamcart-curated/web/events/`
- [ ] Partitionner par `year`, `month`, `day`

#### Tache 4.4 : Transformer les expeditions (shipments)

Creer `scripts/transform_shipments.py` :

| Transformation | Detail |
|---------------|--------|
| Dates | Parser les deux formats (`YYYY-MM-DD` et `DD/MM/YYYY`) |
| Calcul | `delivery_days = delivered_date - shipped_date` |
| Statut | Normaliser en majuscules |

- [ ] Ecrire en Delta Lake dans `s3a://streamcart-curated/delivery/shipments/`

#### Tache 4.5 : Transformer les produits (products)

Creer `scripts/transform_products.py` :

| Transformation | Detail |
|---------------|--------|
| Nettoyage | Trim, suppression caracteres speciaux dans les noms |
| Calcul | `margin = selling_price - cost_price`, `margin_pct = margin / selling_price * 100` |

- [ ] Ecrire en Delta Lake dans `s3a://streamcart-curated/erp/products/`

**Livrable :** 5 scripts de transformation + verification des tables Delta Lake dans MinIO.

---

### Partie 5 : Zone Consumption - Data Marts (3h)

#### Tache 5.1 : Fact Table - fact_sales

Creer `scripts/build_fact_sales.py` :

Joindre orders + customers + products + shipments pour creer une table de fait complete :

```
fact_sales :
  - order_id, order_date, year, month
  - customer_id, customer_segment, customer_country
  - product_id, product_name, category, brand
  - quantity, unit_price, discount_pct, line_total
  - cost_price, margin
  - shipment_status, delivery_days
  - payment_method
```

- [ ] Ecrire en Delta Lake dans `s3a://streamcart-consumption/marts/fact_sales/`
- [ ] Partitionner par `year`, `month`
- [ ] Utiliser Z-ORDER sur `category` (Delta Lake OPTIMIZE)

#### Tache 5.2 : Data Mart - Ventes quotidiennes

Creer `scripts/build_agg_daily_sales.py` :

| Metrique | Calcul |
|----------|--------|
| `nb_orders` | COUNT(DISTINCT order_id) |
| `nb_items` | SUM(quantity) |
| `total_revenue` | SUM(line_total) |
| `total_cost` | SUM(quantity * cost_price) |
| `total_margin` | SUM(margin) |
| `avg_order_value` | AVG(line_total) par commande |
| `avg_delivery_days` | AVG(delivery_days) |

- [ ] Ecrire dans `s3a://streamcart-consumption/marts/agg_daily_sales/`

#### Tache 5.3 : Data Mart - Customer 360

Creer `scripts/build_customer_360.py` :

| Metrique | Calcul |
|----------|--------|
| `first_order_date` | MIN(order_date) |
| `last_order_date` | MAX(order_date) |
| `total_orders` | COUNT(DISTINCT order_id) |
| `lifetime_value` | SUM(line_total) |
| `avg_basket` | AVG(line_total) par commande |
| `favorite_category` | Categorie la plus achetee (MODE) |
| `total_page_views` | COUNT evenements `page_view` |
| `total_add_to_cart` | COUNT evenements `add_to_cart` |
| `conversion_rate` | orders / sessions |
| `customer_status` | Active (<30j) / At Risk (30-90j) / Churned (>90j) |

- [ ] Ecrire dans `s3a://streamcart-consumption/marts/customer_360/`
- [ ] **RGPD** : exclure les clients `gdpr_consent = false`, hasher les emails

#### Tache 5.4 : Data Mart - Performance produits

Creer `scripts/build_product_performance.py` :

| Metrique | Calcul |
|----------|--------|
| `total_sold` | SUM(quantity) |
| `total_revenue` | SUM(line_total) |
| `total_margin` | SUM(margin) |
| `avg_discount` | AVG(discount_pct) |
| `unique_buyers` | COUNT(DISTINCT customer_id) |
| `avg_delivery_days` | AVG(delivery_days) |
| `return_to_product_view_ratio` | orders / page_views sur ce produit |

- [ ] Ecrire dans `s3a://streamcart-consumption/marts/product_performance/`

**Livrable :** 4 scripts de construction des marts + verification des donnees.

---

## JOUR 3 : Qualite, Catalogue et Pipeline (7h)

### Partie 6 : Controles de qualite (2h30)

#### Tache 6.1 : Quality Gates entre zones

Creer `scripts/quality_checks.py` avec des fonctions de verification :

**Gate 1 : Raw -> Curated**

```python
def check_raw_quality(source, entity):
    """Verifie la zone Raw avant transformation"""
    # - Fichier present et non vide
    # - Nombre de lignes > 0
    # - Metadata JSON valide
    # Retourne True/False + rapport
```

**Gate 2 : Curated -> Consumption**

```python
def check_curated_quality(entity):
    """Verifie la zone Curated avant agregation"""
    # - Pas de doublons sur la cle primaire
    # - Colonnes obligatoires non-null > 95%
    # - Valeurs dans les plages attendues
    # - Schema Delta Lake valide
    # Retourne True/False + rapport
```

- [ ] Implementer les quality gates
- [ ] Les gates doivent **bloquer** le pipeline si un seuil n'est pas atteint
- [ ] Generer un rapport de qualite JSON pour chaque execution

#### Tache 6.2 : Rapport de qualite

Creer `scripts/generate_quality_report.py` qui genere un rapport global :

```
=== RAPPORT QUALITE DATA LAKE ===
Date : 2024-01-15 08:30:00

ZONE RAW :
  erp/orders     : 5000 lignes  | OK
  erp/products   : 200 lignes   | OK
  crm/customers  : 1500 lignes  | OK
  web/events     : 50000 lignes | OK
  delivery/ship. : 4500 lignes  | OK

ZONE CURATED :
  orders     : 4950 lignes (-50 doublons) | Completude: 99.2% | OK
  customers  : 1485 lignes (-15 sans RGPD) | Completude: 97.8% | OK
  events     : 49500 lignes (-500 doublons) | Completude: 100% | OK
  shipments  : 4500 lignes | Completude: 95.1% | WARNING (delivered_date null)
  products   : 200 lignes | Completude: 100% | OK

ZONE CONSUMPTION :
  fact_sales          : 4800 lignes | OK
  agg_daily_sales     : 182 jours   | OK
  customer_360        : 1200 lignes | OK
  product_performance : 200 lignes  | OK

QUALITE GLOBALE : 98.4% -- PASS
```

- [ ] Creer le script de rapport
- [ ] Sauvegarder le rapport dans `s3a://streamcart-consumption/quality/`

**Livrable :** Scripts de qualite + exemple de rapport genere.

---

### Partie 7 : Data Catalog simple (1h30)

#### Tache 7.1 : Creer le catalogue

Creer `catalog/data_catalog.json` qui documente chaque table :

```json
{
  "tables": [
    {
      "name": "orders",
      "zone": "curated",
      "path": "s3a://streamcart-curated/erp/orders/",
      "format": "delta",
      "description": "Commandes nettoyees et deduplicees",
      "owner": "equipe-data",
      "pii": false,
      "partitions": ["year", "month"],
      "primary_key": "order_id",
      "row_count": 4950,
      "size_mb": 12.3,
      "freshness_sla": "daily",
      "last_updated": "2024-01-15T08:30:00Z",
      "schema": [
        {"name": "order_id", "type": "STRING", "nullable": false, "description": "Identifiant unique"},
        {"name": "order_date", "type": "TIMESTAMP", "nullable": false, "description": "Date de commande"},
        {"name": "customer_id", "type": "STRING", "nullable": false, "description": "Reference client"},
        {"name": "line_total", "type": "DECIMAL", "nullable": false, "description": "Montant total ligne"}
      ],
      "upstream": ["raw/erp/orders"],
      "downstream": ["consumption/marts/fact_sales"]
    }
  ]
}
```

- [ ] Documenter les **5 tables Curated** et les **4 tables Consumption**
- [ ] Inclure le lineage (`upstream` / `downstream`)
- [ ] Marquer les tables contenant des PII

#### Tache 7.2 : Script de mise a jour du catalogue

Creer `scripts/update_catalog.py` qui met a jour automatiquement :
- Le `row_count` depuis Delta Lake
- Le `size_mb` depuis MinIO
- Le `last_updated` depuis les metadonnees Delta

- [ ] Le script lit les tables Delta et met a jour le catalogue

**Livrable :** `data_catalog.json` complet + script de mise a jour.

---

### Partie 8 : Pipeline complet et documentation (3h)

#### Tache 8.1 : Orchestrer le pipeline

Creer `scripts/run_pipeline.py` : un script principal qui orchestre toutes les etapes dans l'ordre :

```
1. Ingestion       : Raw (tous les fichiers)
2. Quality Gate 1  : Verification Raw
3. Transformation  : Raw -> Curated (5 tables)
4. Quality Gate 2  : Verification Curated
5. Aggregation     : Curated -> Consumption (4 marts)
6. Quality Report  : Generer le rapport global
7. Catalog Update  : Mettre a jour le catalogue
```

- [ ] Chaque etape log son debut, sa fin et son statut
- [ ] Si une quality gate echoue, le pipeline s'arrete avec un message clair
- [ ] Le pipeline est **idempotent** (re-executable)

#### Tache 8.2 : Makefile

Creer un `Makefile` pour simplifier les operations :

```makefile
setup:          ## Demarrer l'infrastructure (Docker)
ingest:         ## Ingerer les donnees dans Raw
transform:      ## Transformer Raw -> Curated
build-marts:    ## Construire les Data Marts (Consumption)
quality:        ## Executer les controles de qualite
pipeline:       ## Executer le pipeline complet
catalog:        ## Mettre a jour le Data Catalog
clean:          ## Arreter l'infrastructure et nettoyer
time-travel:    ## Demonstrer le time travel Delta Lake
```

- [ ] Creer le Makefile avec toutes les cibles

#### Tache 8.3 : Demonstrer le Time Travel

Creer `scripts/demo_time_travel.py` qui :

1. Lit la version actuelle d'une table Delta
2. Modifie des donnees (UPDATE/DELETE)
3. Lit la version precedente (time travel)
4. Affiche la difference entre les deux versions
5. Restaure la version precedente (RESTORE)

- [ ] Executer et capturer la sortie

#### Tache 8.4 : Documentation README

Creer un `README.md` du projet contenant :

- [ ] Schema d'architecture (reproduire le schema ASCII de ce brief)
- [ ] Instructions d'installation (`docker compose up`, pip install)
- [ ] Description de chaque zone et table
- [ ] Comment executer le pipeline (`make pipeline`)
- [ ] Rapport de qualite exemple
- [ ] Decisions techniques prises et justifications

**Livrable :** `run_pipeline.py`, `Makefile`, `demo_time_travel.py`, `README.md`

---

## Criteres de validation

### Infrastructure et Ingestion (20%)

| Critere | Points |
|---------|--------|
| Docker Compose fonctionnel (MinIO) | 5 |
| 3 buckets crees avec bonne nomenclature | 5 |
| Script d'ingestion generique avec metadonnees | 5 |
| Arborescence Raw conforme (source/entite/date) | 5 |

### Transformations Curated (25%)

| Critere | Points |
|---------|--------|
| 5 tables en Delta Lake dans la zone Curated | 10 |
| Deduplication effective | 5 |
| Typage correct et nettoyage des anomalies | 5 |
| Partitionnement adapte | 5 |

### Data Marts Consumption (20%)

| Critere | Points |
|---------|--------|
| fact_sales : jointure complete et correcte | 8 |
| agg_daily_sales : metriques correctes | 4 |
| customer_360 : metriques et statut client | 4 |
| product_performance : metriques et ratio | 4 |

### Qualite et Gouvernance (20%)

| Critere | Points |
|---------|--------|
| Quality gates fonctionnels (bloquants) | 8 |
| Rapport de qualite genere automatiquement | 4 |
| Data Catalog complet (9 tables documentees) | 4 |
| Gestion RGPD (consent, hashing PII) | 4 |

### Pipeline et Documentation (15%)

| Critere | Points |
|---------|--------|
| Pipeline orchestre et idempotent | 5 |
| Makefile complet | 3 |
| Demo Time Travel fonctionnelle | 3 |
| README complet et clair | 4 |

**Total : 100 points**

---

## Bonus (optionnel)

- [ ] **Schema enforcement** : configurer Delta Lake pour rejeter les ecritures avec un schema invalide (+5 points)
- [ ] **OPTIMIZE + ZORDER** : compacter les tables Delta et ordonner par colonne de filtre (+5 points)
- [ ] **Notebook d'analyse** : creer un notebook Jupyter qui repond aux questions business ci-dessous (+10 points)
- [ ] **Tests unitaires** : ecrire des tests pytest pour les fonctions de transformation (+5 points)
- [ ] **Airflow DAG** : remplacer `run_pipeline.py` par un DAG Airflow (+10 points)

---

## Questions business a repondre

Avec vos Data Marts, ecrivez les requetes PySpark ou SQL qui repondent a :

1. Quel est le chiffre d'affaires par mois et quelle est la tendance ?
2. Quels sont les 10 produits les plus vendus par categorie ?
3. Quel est le taux de conversion moyen (page_view -> achat) par device ?
4. Quels sont les 5 clients avec le plus haut lifetime value ?
5. Quel est le delai de livraison moyen par transporteur ?
6. Quelle est la marge totale par categorie de produit ?

---

## Structure attendue du projet

```
streamcart-datalake/
+-- docker-compose.yml
+-- Makefile
+-- README.md
+-- requirements.txt
+-- config/
|   +-- s3_config.py
+-- data/                          # Donnees source fournies
|   +-- erp_orders.csv
|   +-- erp_products.csv
|   +-- crm_customers.json
|   +-- web_events.json
|   +-- delivery_shipments.csv
+-- scripts/
|   +-- spark_session.py
|   +-- ingest_to_raw.py
|   +-- transform_orders.py
|   +-- transform_customers.py
|   +-- transform_events.py
|   +-- transform_shipments.py
|   +-- transform_products.py
|   +-- build_fact_sales.py
|   +-- build_agg_daily_sales.py
|   +-- build_customer_360.py
|   +-- build_product_performance.py
|   +-- quality_checks.py
|   +-- generate_quality_report.py
|   +-- update_catalog.py
|   +-- run_pipeline.py
|   +-- demo_time_travel.py
+-- notebooks/
|   +-- 01_exploration_raw.ipynb
+-- catalog/
|   +-- data_catalog.json
+-- quality_reports/
    +-- report_2024-01-15.json
```

---

## Ressources

- [Cours Data Lake](../../../05-Databases/DataLake/cours/)
- [Cours Spark](../../../06-Data-Engineering/Spark/)
- [Cours Data Warehouse](../../../05-Databases/DataWarehouse/cours/)
- [Documentation Delta Lake](https://docs.delta.io/)
- [Documentation MinIO](https://min.io/docs/minio/container/index.html)
- [Documentation PySpark](https://spark.apache.org/docs/latest/api/python/)
