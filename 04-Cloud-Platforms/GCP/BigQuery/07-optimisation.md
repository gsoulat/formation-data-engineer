# Module 07 - Optimisation et bonnes pratiques

## Optimisation des coûts

### Comprendre la facturation

```
┌─────────────────────────────────────────────────────────┐
│                 FACTURATION BIGQUERY                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ANALYSE (On-demand)                                    │
│  ├── $5 par TB de données scannées                      │
│  ├── Minimum : 10 MB par requête                        │
│  └── Cache : requêtes identiques gratuites (24h)        │
│                                                          │
│  STOCKAGE                                               │
│  ├── Active : $0.02 / GB / mois                         │
│  └── Long-term (>90j) : $0.01 / GB / mois               │
│                                                          │
│  GRATUIT                                                │
│  ├── 1 TB de requêtes / mois                            │
│  ├── 10 GB de stockage / mois                           │
│  └── Chargement et export                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Vérifier le coût avant exécution

```sql
-- Dans la console : voir "This query will process X GB"
-- Ou utiliser le dry-run

-- Via bq CLI
bq query --dry_run --use_legacy_sql=false '
SELECT * FROM projet.dataset.grande_table
'
-- Retourne : Query successfully validated. Estimated cost: X GB
```

### Réduire les données scannées

#### 1. SELECT explicite (pas de SELECT *)

```sql
-- MAUVAIS : scanne toutes les colonnes
SELECT * FROM projet.dataset.events;

-- BON : scanne seulement les colonnes nécessaires
SELECT event_id, event_type, timestamp
FROM projet.dataset.events;
```

#### 2. Partitionnement

```sql
-- Table partitionnée par date
CREATE TABLE projet.dataset.events (
    event_id STRING,
    event_date DATE,
    event_type STRING
)
PARTITION BY event_date;

-- Requête optimisée (scanne 1 partition)
SELECT *
FROM projet.dataset.events
WHERE event_date = '2024-01-15';  -- Filtre sur partition
```

#### 3. Clustering

```sql
-- Table clusterisée
CREATE TABLE projet.dataset.events (
    event_id STRING,
    event_date DATE,
    event_type STRING,
    user_id STRING
)
PARTITION BY event_date
CLUSTER BY event_type, user_id;  -- Clustering

-- Requête optimisée (données pré-triées)
SELECT *
FROM projet.dataset.events
WHERE event_date = '2024-01-15'
  AND event_type = 'purchase';  -- Bénéficie du clustering
```

### Limiter les coûts

```sql
-- Limite de bytes au niveau projet
-- Console → BigQuery → Project Settings → Maximum bytes billed

-- Limite par requête
SELECT *
FROM projet.dataset.grande_table
OPTIONS(maximum_bytes_billed=1000000000);  -- 1 GB max
```

## Optimisation des performances

### Partitionnement efficace

| Type | Description | Usage |
|------|-------------|-------|
| **Par date** | DATE, TIMESTAMP, DATETIME | Données temporelles |
| **Par ingestion** | `_PARTITIONTIME` | Données streaming |
| **Par plage d'entiers** | Integer range | ID séquentiels |

```sql
-- Partition par date
PARTITION BY order_date

-- Partition par mois (moins de partitions)
PARTITION BY DATE_TRUNC(order_date, MONTH)

-- Partition par ingestion
PARTITION BY DATE(_PARTITIONTIME)

-- Partition par plage d'entiers
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 1000000, 10000))
```

### Clustering optimal

```sql
-- Jusqu'à 4 colonnes de clustering
CLUSTER BY col1, col2, col3, col4

-- Ordre important : du plus filtré au moins filtré
CLUSTER BY event_type, country, user_id

-- Requêtes bénéficiant du clustering
SELECT ... WHERE event_type = 'click' AND country = 'FR';
```

### Vues matérialisées

```sql
-- Créer une vue matérialisée
CREATE MATERIALIZED VIEW gold.mv_daily_sales
PARTITION BY order_date
CLUSTER BY product_id
AS
SELECT
    order_date,
    product_id,
    COUNT(*) as order_count,
    SUM(amount) as total_revenue
FROM silver.clean_orders
GROUP BY order_date, product_id;

-- BigQuery utilise automatiquement la MV si applicable
-- Les agrégations sont pré-calculées
```

### BI Engine (cache en mémoire)

```sql
-- Réserver de la capacité BI Engine
-- Console → BigQuery → BI Engine → Create Reservation

-- Tables avec BI Engine activé sont en cache mémoire
-- Latence sub-seconde pour les dashboards
```

## Bonnes pratiques SQL

### Éviter les anti-patterns

```sql
-- MAUVAIS : Sous-requête corrélée
SELECT *
FROM orders o
WHERE total_amount > (
    SELECT AVG(total_amount)
    FROM orders
    WHERE customer_id = o.customer_id  -- Exécuté pour chaque ligne
);

-- BON : Window function
SELECT *
FROM (
    SELECT *,
        AVG(total_amount) OVER (PARTITION BY customer_id) as avg_amount
    FROM orders
)
WHERE total_amount > avg_amount;
```

### Utiliser APPROX_COUNT_DISTINCT

```sql
-- PRÉCIS mais lent sur gros volumes
SELECT COUNT(DISTINCT user_id) FROM events;  -- Exact

-- APPROXIMATIF mais rapide (erreur < 1%)
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;  -- ~100x plus rapide
```

### Filtrer tôt

```sql
-- MAUVAIS : filtre après jointure
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date = '2024-01-15';

-- BON : filtre avant jointure
SELECT *
FROM (SELECT * FROM orders WHERE order_date = '2024-01-15') o
JOIN customers c ON o.customer_id = c.id;
```

### Éviter les fonctions sur colonnes de filtre

```sql
-- MAUVAIS : fonction sur la colonne (pas d'utilisation d'index)
SELECT * FROM events
WHERE EXTRACT(YEAR FROM event_date) = 2024;

-- BON : comparaison directe
SELECT * FROM events
WHERE event_date >= '2024-01-01' AND event_date < '2025-01-01';
```

## Monitoring et debugging

### Information Schema

```sql
-- Taille des tables
SELECT
    table_name,
    ROUND(size_bytes / 1e9, 2) as size_gb,
    row_count
FROM `projet.dataset.INFORMATION_SCHEMA.TABLE_STORAGE`
ORDER BY size_bytes DESC;

-- Historique des jobs
SELECT
    creation_time,
    job_id,
    user_email,
    total_bytes_processed,
    total_slot_ms
FROM `region-eu.INFORMATION_SCHEMA.JOBS`
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
ORDER BY total_bytes_processed DESC
LIMIT 20;
```

### Analyser le plan d'exécution

```sql
-- Dans la console : onglet "Execution details" après une requête
-- Montre :
--   - Étapes d'exécution
--   - Données lues/écrites par étape
--   - Slot time utilisé
--   - Shuffle (données déplacées entre workers)
```

### Colonnes de métadonnées

```sql
-- Métadonnées automatiques pour tables partitionnées
SELECT
    _PARTITIONTIME,  -- Timestamp de la partition
    _PARTITIONDATE,  -- Date de la partition
    *
FROM projet.dataset.events;

-- Pour tables streaming
SELECT
    _PARTITIONTIME,
    *
FROM projet.dataset.streaming_events;
```

## Sécurité et gouvernance

### Row-Level Security

```sql
-- Créer une politique de sécurité
CREATE ROW ACCESS POLICY region_filter
ON projet.dataset.sales
GRANT TO ("user:analyst@company.com")
FILTER USING (region = 'EU');

-- L'utilisateur ne voit que les lignes region = 'EU'
```

### Column-Level Security

```sql
-- Utiliser les policy tags (Data Catalog)
-- 1. Créer un taxonomy dans Data Catalog
-- 2. Créer des policy tags (ex: "PII", "Confidentiel")
-- 3. Appliquer aux colonnes sensibles
-- 4. Configurer les permissions IAM

-- Les colonnes taguées sont masquées pour les utilisateurs non autorisés
```

### Audit des accès

```sql
-- Logs d'audit dans Cloud Logging
-- Filtrer : resource.type="bigquery_resource"

-- Ou via INFORMATION_SCHEMA
SELECT
    creation_time,
    user_email,
    query
FROM `region-eu.INFORMATION_SCHEMA.JOBS`
WHERE user_email NOT LIKE '%gserviceaccount.com'
ORDER BY creation_time DESC;
```

## Checklist d'optimisation

### Avant la mise en production

- [ ] Tables partitionnées par date
- [ ] Clustering sur colonnes fréquemment filtrées
- [ ] Pas de SELECT *
- [ ] Requêtes testées avec dry-run
- [ ] Limite de bytes configurée
- [ ] Documentation des modèles

### Monitoring régulier

- [ ] Coûts par dataset/table
- [ ] Requêtes les plus coûteuses
- [ ] Taille des tables
- [ ] Fraîcheur des données
- [ ] Erreurs dans les pipelines

## Points clés à retenir

- **Partitionnement** = réduction des données scannées
- **Clustering** = données pré-triées pour filtres rapides
- **SELECT explicite** = ne pas utiliser SELECT *
- **Vues matérialisées** = pré-agrégations automatiques
- **Dry-run** = estimer le coût avant exécution
- **INFORMATION_SCHEMA** = monitoring et debugging
- **Sécurité** = Row/Column level security

---

[Module précédent](./06-dataform.md) | [Retour au sommaire](./README.md)

## Pour aller plus loin

- [Brief pratique : BigQuery Medallion](../../../99-Brief/Data-Engineer/BigQuery-Medallion/)
- [Documentation officielle BigQuery](https://cloud.google.com/bigquery/docs)
- [Bonnes pratiques BigQuery](https://cloud.google.com/bigquery/docs/best-practices-performance)
