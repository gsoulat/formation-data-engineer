# Chapitre 5 : Lineage

## Table des matières

1. [Qu'est-ce que le data lineage ?](#quest-ce-que-le-data-lineage)
2. [Types de lineage dans OpenMetadata](#types-de-lineage-dans-openmetadata)
3. [Lineage automatique](#lineage-automatique)
4. [Lineage SQL parsing](#lineage-sql-parsing)
5. [Lineage dbt](#lineage-dbt)
6. [Lineage manuel](#lineage-manuel)
7. [Analyse d'impact](#analyse-dimpact)
8. [Column-level lineage](#column-level-lineage)

---

## Qu'est-ce que le data lineage ?

Le **data lineage** (lignée des données) trace le parcours complet des données depuis leur source jusqu'à leur consommation.

### Les 3 dimensions du lineage

| Dimension | Question | Exemple |
|-----------|----------|---------|
| **Upstream** (amont) | D'où viennent mes données ? | CRM → raw.customers → dim_customers |
| **Downstream** (aval) | Qui utilise mes données ? | dim_customers → dashboard "Clients" |
| **Column-level** | Quelle colonne alimente quelle colonne ? | raw.customers.email → dim_customers.email |

### Pourquoi le lineage est essentiel ?

```
Sans lineage                        Avec lineage
┌─────────────────────┐            ┌─────────────────────┐
│ "On a modifié la    │            │ "La colonne email    │
│  table customers,   │            │  alimente 3 tables,  │
│  j'espère que rien  │            │  2 dashboards et     │
│  n'est cassé..."    │            │  1 modèle ML.        │
│                     │            │  Impact : mesuré."   │
└─────────────────────┘            └─────────────────────┘
```

### Cas d'usage concrets

1. **Analyse d'impact** : "Si je modifie cette colonne, qu'est-ce qui casse ?"
2. **Root cause analysis** : "Ce dashboard affiche des données fausses, d'où vient le problème ?"
3. **Conformité RGPD** : "Par où transitent les données personnelles ?"
4. **Documentation** : "Comment ce KPI est-il calculé ?"

---

## Types de lineage dans OpenMetadata

### Sources de lineage

| Source | Méthode | Fiabilité |
|--------|---------|-----------|
| **SQL Queries** | Parsing des requêtes exécutées | Haute |
| **dbt** | Fichier manifest.json | Très haute |
| **Airflow** | Opérateurs SQL dans les DAGs | Moyenne |
| **Spark** | OpenLineage events | Haute |
| **Views** | Définition SQL de la vue | Très haute |
| **Manuel** | Ajouté par l'utilisateur | Variable |

### Niveaux de granularité

```
Table-level lineage           Column-level lineage
┌──────┐    ┌──────┐         ┌──────────┐    ┌──────────┐
│ raw. │───▶│ dim. │         │ raw.     │    │ dim.     │
│ cust.│    │ cust.│         │ .email   │───▶│ .email   │
└──────┘    └──────┘         │ .name    │───▶│ .full_nm │
                              │ .phone   │    │          │
                              └──────────┘    └──────────┘
```

---

## Lineage automatique

### Via les connecteurs de bases de données

Quand vous activez l'ingestion **Usage & Lineage**, OpenMetadata :

1. Collecte les requêtes exécutées (query log)
2. Parse le SQL pour extraire les relations
3. Construit le graphe de lineage

### Activer l'ingestion de lineage

1. Aller dans **Settings** → **Services** → **[Votre service]**
2. **Add Ingestion** → **Lineage Ingestion**
3. Configurer :
   - **Query Log Duration** : nombre de jours d'historique (7 par défaut)
   - **Result Limit** : nombre maximum de requêtes à analyser
4. **Deploy**

### Exemple avec PostgreSQL

OpenMetadata analyse les requêtes comme :

```sql
-- Cette requête crée un lineage automatique
INSERT INTO analytics.daily_sales
SELECT
    DATE(o.order_date) AS sale_date,
    COUNT(*) AS total_orders,
    SUM(o.total_amount) AS revenue
FROM raw.orders o
JOIN raw.order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_date);
```

**Lineage détecté** :
```
raw.orders ─────────┐
                     ├───▶ analytics.daily_sales
raw.order_items ────┘
```

---

## Lineage SQL parsing

### Comment ça fonctionne ?

OpenMetadata utilise un **SQL parser** pour analyser les requêtes et en extraire le lineage :

```
Requête SQL
    │
    ▼
┌───────────┐
│ SQL Parser│ → Identifie les tables source (FROM, JOIN)
│ (sqlfluff │ → Identifie les tables cible (INSERT INTO, CREATE TABLE AS)
│  / custom)│ → Mappe les colonnes (SELECT ... AS ...)
└───────────┘
    │
    ▼
Lineage Graph
```

### Types de requêtes supportées

| Pattern SQL | Lineage détecté |
|-------------|-----------------|
| `INSERT INTO ... SELECT FROM` | source → cible |
| `CREATE TABLE ... AS SELECT` | source → cible |
| `CREATE VIEW ... AS SELECT` | source → vue |
| `MERGE INTO ... USING` | source → cible |
| `SELECT ... JOIN ...` | tables jointes identifiées |
| Sous-requêtes | Relations imbriquées |
| CTEs (`WITH ... AS`) | Relations temporaires |

### Exemple complexe

```sql
WITH monthly_metrics AS (
    SELECT
        c.customer_id,
        c.segment,
        DATE_TRUNC('month', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM raw.customers c
    JOIN raw.orders o ON c.customer_id = o.customer_id
    JOIN raw.order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.segment, DATE_TRUNC('month', o.order_date)
)
INSERT INTO analytics.customer_monthly_revenue
SELECT * FROM monthly_metrics;
```

**Lineage détecté** :
```
raw.customers ──────┐
                     │
raw.orders ─────────┼───▶ analytics.customer_monthly_revenue
                     │
raw.order_items ────┘

Column-level :
- customers.customer_id  → customer_monthly_revenue.customer_id
- customers.segment      → customer_monthly_revenue.segment
- orders.order_date      → customer_monthly_revenue.month
- order_items.quantity    ┐
- order_items.unit_price ┘→ customer_monthly_revenue.revenue
```

---

## Lineage dbt

### Le lineage le plus riche

dbt produit le lineage le plus complet grâce au fichier `manifest.json` qui contient :
- Les relations entre **sources**, **models**, **seeds**, **snapshots**
- Le lineage au niveau **colonne**
- Les **tests** associés
- Les **exposures** (dashboards, applications)

### Exemple de projet dbt

```
dbt Project
├── models/
│   ├── staging/
│   │   ├── stg_customers.sql    ← SELECT FROM {{ source('raw', 'customers') }}
│   │   └── stg_orders.sql       ← SELECT FROM {{ source('raw', 'orders') }}
│   ├── intermediate/
│   │   └── int_orders_enriched.sql ← JOIN stg_customers + stg_orders
│   └── marts/
│       └── fct_revenue.sql      ← SELECT FROM int_orders_enriched
└── exposures/
    └── dashboards.yml           ← Dashboard "Revenue" depends on fct_revenue
```

### Lineage résultant dans OpenMetadata

```
raw.customers ──▶ stg_customers ──┐
                                   ├──▶ int_orders_enriched ──▶ fct_revenue ──▶ Dashboard "Revenue"
raw.orders ─────▶ stg_orders ─────┘
```

### Configuration de l'ingestion dbt

```yaml
# Dans OpenMetadata, l'ingestion dbt récupère :
source:
  type: dbt
  config:
    # Les fichiers dbt contiennent tout le lineage
    dbtManifestFilePath: target/manifest.json
    dbtCatalogFilePath: target/catalog.json

    # Le lineage est automatiquement associé au service de base
    dbtServiceName: demo-postgres
```

---

## Lineage manuel

### Quand ajouter du lineage manuellement ?

- Pipelines non supportés (scripts Python custom, ETL legacy)
- Relations entre systèmes non connectés
- Enrichissement du lineage automatique

### Via l'UI

1. Ouvrir une table → Onglet **Lineage**
2. Cliquer **Edit Lineage** (icône crayon)
3. Glisser-déposer pour créer des connexions entre les nœuds
4. Ajouter des nœuds avec le bouton **+**
5. Sauvegarder

### Via l'API

```python
import requests

API_URL = "http://localhost:8585/api/v1"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Ajouter un lineage entre deux tables
lineage_data = {
    "edge": {
        "fromEntity": {
            "id": "uuid-table-source",
            "type": "table"
        },
        "toEntity": {
            "id": "uuid-table-cible",
            "type": "table"
        },
        "lineageDetails": {
            "sqlQuery": "INSERT INTO cible SELECT * FROM source",
            "columnsLineage": [
                {
                    "fromColumns": ["source.customer_id"],
                    "toColumn": "cible.customer_id"
                },
                {
                    "fromColumns": ["source.first_name", "source.last_name"],
                    "toColumn": "cible.full_name"
                }
            ]
        }
    }
}

response = requests.put(
    f"{API_URL}/lineage",
    headers=headers,
    json=lineage_data
)
```

---

## Analyse d'impact

### Upstream analysis (analyse amont)

> "D'où viennent les données de mon dashboard ?"

```
Dashboard "Revenue mensuelle"
    ↑
fct_monthly_revenue (table)
    ↑
int_orders_enriched (table intermédiaire)
    ↑
stg_customers + stg_orders (staging)
    ↑
raw.customers + raw.orders (sources brutes)
    ↑
CRM Salesforce + Système de commandes (systèmes source)
```

### Downstream analysis (analyse aval)

> "Si je modifie la colonne `email` dans `raw.customers`, qu'est-ce qui est impacté ?"

```
raw.customers.email
    ↓
stg_customers.email
    ↓
├── dim_customers.email
│   ├── Dashboard "Profil Client" ⚠️
│   └── ML Model "Churn Prediction" ⚠️
│
├── int_notifications.recipient_email
│   └── Pipeline "Email Marketing" ⚠️
│
└── rpt_gdpr_audit.personal_email
    └── Dashboard "RGPD Compliance" ⚠️
```

### Utiliser l'analyse d'impact dans l'UI

1. Ouvrir la table ou la colonne
2. Aller dans l'onglet **Lineage**
3. Le graphe interactif montre :
   - **Nœuds verts** : tables en amont (sources)
   - **Nœuds bleus** : la table sélectionnée
   - **Nœuds orange** : tables en aval (impactées)
4. Cliquer sur un nœud pour voir ses détails
5. Naviguer dans le graphe pour explorer les dépendances

---

## Column-level lineage

### Le plus fin niveau de traçabilité

Le lineage au niveau colonne montre exactement quelle colonne source alimente quelle colonne cible, incluant les transformations.

### Exemple visuel

```
┌─ raw.customers ──────┐     ┌─ dim_customers ────────┐
│                       │     │                         │
│ customer_id ──────────┼────▶│ customer_id             │
│ first_name ───────┐   │     │                         │
│ last_name ────────┼───┼────▶│ full_name (CONCAT)      │
│ email ────────────┼───┼────▶│ email                   │
│ created_at ───────┼───┼────▶│ registration_date       │
│ phone ────────────┼───┼────▶│ phone_number            │
│                   │   │     │                         │
└───────────────────┘   │     │ total_orders ◀──────────┼─── raw.orders (COUNT)
                        │     │ lifetime_value ◀────────┼─── raw.order_items (SUM)
                        │     │                         │
                        │     └─────────────────────────┘
```

### Activer le column-level lineage

Le column-level lineage est automatiquement extrait :
- Par le **SQL parser** lors de l'ingestion Usage/Lineage
- Par **dbt** via le manifest.json
- Manuellement via l'UI ou l'API

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| Lineage | Traçabilité complète des données source → consommation |
| Automatique | Extrait des query logs et des connecteurs |
| SQL parsing | Analyse les requêtes pour détecter les relations |
| dbt | Source de lineage la plus riche (manifest.json) |
| Manuel | Complément pour les pipelines non supportés |
| Impact analysis | Upstream (d'où ?) et Downstream (vers où ?) |
| Column-level | Traçabilité au niveau le plus fin (colonne) |

---

> **Prochain chapitre** : [Qualité des Données](06-qualite-donnees.md) - Profiling et tests de qualité natifs
