# Chapitre 3 : Connecteurs et Ingestion

## Table des matières

1. [Concept d'ingestion de métadonnées](#concept-dingestion-de-métadonnées)
2. [Types de connecteurs](#types-de-connecteurs)
3. [Connecter une base PostgreSQL](#connecter-une-base-postgresql)
4. [Connecter BigQuery](#connecter-bigquery)
5. [Connecter Airflow](#connecter-airflow)
6. [Connecter dbt](#connecter-dbt)
7. [Connecter un outil de dashboard](#connecter-un-outil-de-dashboard)
8. [Planification et monitoring](#planification-et-monitoring)

---

## Concept d'ingestion de métadonnées

### Qu'est-ce que l'ingestion ?

L'ingestion est le processus de **collecte automatique des métadonnées** depuis vos sources vers OpenMetadata.

```
Source (PostgreSQL)                OpenMetadata
┌───────────────────┐            ┌───────────────────┐
│ Tables             │            │ Entités Table      │
│ Colonnes           │──Ingestion│ Colonnes + types   │
│ Contraintes        │──────────▶│ Relations          │
│ Stats d'usage      │            │ Profiling          │
│ Requêtes           │            │ Lineage            │
└───────────────────┘            └───────────────────┘
```

### Types d'ingestion

| Type | Ce qu'il collecte | Fréquence recommandée |
|------|-------------------|----------------------|
| **Metadata** | Schémas, tables, colonnes, types | Quotidienne |
| **Usage** | Requêtes exécutées, popularité | Quotidienne |
| **Lineage** | Relations entre tables/colonnes | Quotidienne |
| **Profiler** | Stats sur les données (min, max, null%, etc.) | Hebdomadaire |
| **Data Quality** | Résultats des tests de qualité | Selon les tests |

### Pipeline d'ingestion

Chaque ingestion est un **pipeline** orchestré par le framework d'ingestion Python :

```
1. Source      → Se connecte à la source et extrait les métadonnées
2. Processor   → Transforme et enrichit les métadonnées
3. Stage       → Met en file d'attente
4. Sink        → Envoie les métadonnées à l'API OpenMetadata
```

---

## Types de connecteurs

### Connecteurs bases de données

| Connecteur | Metadata | Usage | Lineage | Profiler |
|-----------|----------|-------|---------|----------|
| PostgreSQL | ✅ | ✅ | ✅ | ✅ |
| MySQL | ✅ | ✅ | ✅ | ✅ |
| BigQuery | ✅ | ✅ | ✅ | ✅ |
| Snowflake | ✅ | ✅ | ✅ | ✅ |
| Redshift | ✅ | ✅ | ✅ | ✅ |
| Databricks | ✅ | ✅ | ✅ | ✅ |
| SQL Server | ✅ | ✅ | ✅ | ✅ |
| Oracle | ✅ | ❌ | ✅ | ✅ |

### Connecteurs dashboards

| Connecteur | Metadata | Lineage | Datamodels |
|-----------|----------|---------|------------|
| Superset | ✅ | ✅ | ✅ |
| Metabase | ✅ | ✅ | ✅ |
| Looker | ✅ | ✅ | ✅ |
| Power BI | ✅ | ✅ | ✅ |
| Tableau | ✅ | ✅ | ✅ |
| Grafana | ✅ | ❌ | ❌ |

### Connecteurs pipelines

| Connecteur | Metadata | Lineage | Status |
|-----------|----------|---------|--------|
| Airflow | ✅ | ✅ | ✅ |
| dbt | ✅ | ✅ | ✅ |
| Dagster | ✅ | ✅ | ✅ |
| Prefect | ✅ | ❌ | ✅ |
| Spark | ✅ | ✅ | ✅ |

### Connecteurs messaging et stockage

| Connecteur | Type |
|-----------|------|
| Kafka | Messaging |
| Redpanda | Messaging |
| Amazon S3 | Storage |
| Google Cloud Storage | Storage |
| Azure Data Lake Storage | Storage |

---

## Connecter une base PostgreSQL

### Étape 1 : Préparer la base PostgreSQL

Pour ce cours, ajoutons un PostgreSQL au `docker-compose.yml` :

```yaml
# Ajouter ce service dans docker-compose.yml
services:
  demo-postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo123
      POSTGRES_DB: ecommerce
    ports:
      - "5433:5432"
    volumes:
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
```

Script d'initialisation `init-db.sql` :

```sql
-- Schéma source
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Tables sources
CREATE TABLE raw.customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES raw.customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12, 2),
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE raw.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES raw.orders(order_id),
    product_id INTEGER REFERENCES raw.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Vue analytique
CREATE VIEW analytics.daily_sales AS
SELECT
    DATE(o.order_date) AS sale_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    SUM(o.total_amount) AS revenue
FROM raw.orders o
WHERE o.status = 'completed'
GROUP BY DATE(o.order_date);

-- Données d'exemple
INSERT INTO raw.customers (first_name, last_name, email, phone)
VALUES
    ('Alice', 'Martin', 'alice@example.com', '+33601020304'),
    ('Bob', 'Dupont', 'bob@example.com', '+33605060708'),
    ('Claire', 'Bernard', 'claire@example.com', '+33609101112');

INSERT INTO raw.products (name, category, price, stock_quantity)
VALUES
    ('Laptop Pro 15', 'Electronics', 1299.99, 50),
    ('Wireless Mouse', 'Electronics', 29.99, 200),
    ('Standing Desk', 'Furniture', 499.99, 30);

INSERT INTO raw.orders (customer_id, order_date, total_amount, status)
VALUES
    (1, '2024-01-15', 1329.98, 'completed'),
    (2, '2024-01-16', 499.99, 'completed'),
    (3, '2024-01-16', 59.98, 'pending');

INSERT INTO raw.order_items (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 1, 29.99),
    (2, 3, 1, 499.99),
    (3, 2, 2, 29.99);
```

### Étape 2 : Ajouter le service dans OpenMetadata

**Via l'interface UI** :

1. Aller dans **Settings** → **Services** → **Databases**
2. Cliquer **Add New Service**
3. Sélectionner **PostgreSQL**
4. Remplir la configuration :

| Champ | Valeur |
|-------|--------|
| Name | `demo-postgres` |
| Host | `demo-postgres` (nom Docker) |
| Port | `5432` |
| Username | `demo` |
| Password | `demo123` |
| Database | `ecommerce` |

5. Cliquer **Test Connection** → Vérifier que tous les tests passent
6. Cliquer **Save**

### Étape 3 : Lancer l'ingestion

1. Après la création du service, cliquer **Add Ingestion**
2. Sélectionner **Metadata Ingestion**
3. Configuration :
   - **Filter Pattern** : laisser vide pour tout ingérer (ou filtrer par schéma)
   - **Include views** : ✅ Oui
   - **Include tags** : ✅ Oui
4. **Schedule** : Choisir la fréquence (quotidienne recommandée)
5. Cliquer **Deploy**

### Étape 4 : Vérifier les résultats

Après l'ingestion, naviguer vers **Explore** → **Tables** :

```
demo-postgres
├── ecommerce
│   ├── raw
│   │   ├── customers (4 colonnes)
│   │   ├── products (6 colonnes)
│   │   ├── orders (5 colonnes)
│   │   └── order_items (5 colonnes)
│   └── analytics
│       └── daily_sales (vue - 4 colonnes)
```

### Via le SDK Python (alternative)

```python
from metadata.ingestion.api.workflow import Workflow

config = {
    "source": {
        "type": "postgres",
        "serviceName": "demo-postgres",
        "serviceConnection": {
            "config": {
                "type": "Postgres",
                "hostPort": "localhost:5433",
                "username": "demo",
                "password": "demo123",
                "database": "ecommerce"
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DatabaseMetadata",
                "includeViews": True,
                "schemaFilterPattern": {
                    "includes": ["raw", "analytics"]
                }
            }
        }
    },
    "sink": {
        "type": "metadata-rest",
        "config": {}
    },
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://localhost:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {
                "jwtToken": "votre-jwt-token"
            }
        }
    }
}

workflow = Workflow.create(config)
workflow.execute()
workflow.print_status()
```

---

## Connecter BigQuery

### Configuration du service

| Champ | Valeur |
|-------|--------|
| Name | `bigquery-prod` |
| Type | `BigQuery` |
| GCS Credentials | Fichier JSON du service account |
| Project ID | `votre-projet-gcp` |

### Service Account requis

Le service account GCP nécessite les rôles :
- `roles/bigquery.dataViewer` (lecture des schémas et données)
- `roles/bigquery.jobUser` (exécution de requêtes pour le profiling)
- `roles/bigquery.readSessionUser` (optionnel, pour le profiling)

### Ingestion des métadonnées

```python
config = {
    "source": {
        "type": "bigquery",
        "serviceName": "bigquery-prod",
        "serviceConnection": {
            "config": {
                "type": "BigQuery",
                "credentials": {
                    "gcpConfig": {
                        "type": "service_account",
                        "projectId": "votre-projet",
                        "privateKeyId": "...",
                        "privateKey": "...",
                        "clientEmail": "om@votre-projet.iam.gserviceaccount.com",
                        "clientId": "..."
                    }
                }
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DatabaseMetadata",
                "schemaFilterPattern": {
                    "includes": ["analytics_.*", "staging_.*"]
                }
            }
        }
    },
    "sink": {"type": "metadata-rest", "config": {}}
}
```

---

## Connecter Airflow

### Configuration via l'UI

1. **Settings** → **Services** → **Pipelines** → **Add New Service**
2. Sélectionner **Airflow**
3. Configuration :

| Champ | Valeur |
|-------|--------|
| Name | `airflow-prod` |
| Host | `http://airflow-webserver:8080` |
| Connection | `backend_db` (connexion à la base Airflow) |

### Ce que l'ingestion collecte

- Liste des DAGs et leur description
- Tasks et dépendances
- Historique des exécutions (status, durée)
- Lineage entre les tasks et les tables

### Lineage automatique

Si vos DAGs Airflow utilisent des opérateurs SQL, OpenMetadata peut extraire le lineage automatiquement :

```python
# Airflow DAG avec lineage traçable
extract_task = PostgresOperator(
    task_id='extract_customers',
    sql="INSERT INTO staging.customers SELECT * FROM raw.customers",
    postgres_conn_id='warehouse'
)
```

OpenMetadata détecte : `raw.customers` → `staging.customers`

---

## Connecter dbt

### Pourquoi connecter dbt ?

dbt est une source riche de métadonnées :
- **Descriptions** des modèles et colonnes
- **Lineage** entre les modèles
- **Tests** et leur résultats
- **Tags** et meta

### Configuration

dbt se connecte comme un **pipeline service** et nécessite les fichiers générés par dbt :

| Fichier dbt | Contenu | Chemin par défaut |
|-------------|---------|-------------------|
| `manifest.json` | Modèles, sources, tests, lineage | `target/manifest.json` |
| `catalog.json` | Statistiques sur les colonnes | `target/catalog.json` |
| `run_results.json` | Résultats des tests | `target/run_results.json` |

### Ingestion via l'UI

1. **Settings** → **Services** → **Pipelines** → **Add New Service**
2. Sélectionner **dbt**
3. Fournir les fichiers `manifest.json` et `catalog.json`
4. Associer au **Database Service** correspondant (ex: `demo-postgres`)

### Ingestion via le SDK

```python
config = {
    "source": {
        "type": "dbt",
        "serviceName": "dbt-ecommerce",
        "serviceConnection": {
            "config": {
                "type": "DBT",
                "dbtConfigSource": {
                    "dbtConfigType": "local",
                    "dbtManifestFilePath": "/path/to/target/manifest.json",
                    "dbtCatalogFilePath": "/path/to/target/catalog.json",
                    "dbtRunResultsFilePath": "/path/to/target/run_results.json"
                }
            }
        },
        "sourceConfig": {
            "config": {
                "type": "DBTSource",
                "dbtServiceName": "demo-postgres"
            }
        }
    },
    "sink": {"type": "metadata-rest", "config": {}}
}
```

### Résultat de l'intégration dbt

Après ingestion, les tables affichent :
- Les descriptions dbt dans la documentation
- Le lineage dbt (sources → staging → marts)
- Les tests dbt et leurs résultats
- Les tags dbt comme tags OpenMetadata

---

## Connecter un outil de dashboard

### Exemple avec Superset

1. **Settings** → **Services** → **Dashboards** → **Add New Service**
2. Sélectionner **Superset**
3. Configuration :

| Champ | Valeur |
|-------|--------|
| Name | `superset-prod` |
| Host | `http://superset:8088` |
| Username | `admin` |
| Password | `admin` |
| Provider | `db` (ou `ldap`) |

### Métadonnées collectées

```
superset-prod
├── Dashboard : "Sales Overview"
│   ├── Chart : "Revenue par mois"
│   │   └── Lineage → analytics.monthly_revenue
│   ├── Chart : "Top clients"
│   │   └── Lineage → analytics.top_customers
│   └── Chart : "Tendance commandes"
│       └── Lineage → analytics.daily_sales
```

---

## Planification et monitoring

### Planification des ingestions

Chaque ingestion peut être planifiée :

| Fréquence | Cron | Usage |
|-----------|------|-------|
| Toutes les heures | `0 * * * *` | Sources très actives |
| Quotidienne | `0 2 * * *` | Recommandé par défaut |
| Hebdomadaire | `0 2 * * 0` | Profiler (coûteux) |

### Monitoring des ingestions

**Via l'UI** : Settings → Services → [Service] → Ingestion → Voir les logs

**Via l'API** :

```bash
# Lister les pipelines d'ingestion
curl -X GET "http://localhost:8585/api/v1/services/ingestionPipelines" \
  -H "Authorization: Bearer $TOKEN"

# Voir le statut d'un pipeline
curl -X GET "http://localhost:8585/api/v1/services/ingestionPipelines/{id}/status" \
  -H "Authorization: Bearer $TOKEN"
```

### Gestion des erreurs courantes

| Erreur | Cause probable | Solution |
|--------|---------------|----------|
| Connection refused | Service inaccessible | Vérifier le réseau Docker |
| Authentication failed | Credentials incorrects | Vérifier user/password |
| Permission denied | Droits insuffisants | Accorder les rôles nécessaires |
| Timeout | Source trop lente | Augmenter le timeout |
| Filter mismatch | Pattern de filtre incorrect | Vérifier les regex |

---

## Résumé

| Action | Comment |
|--------|---------|
| Ajouter un service | Settings → Services → Add New Service |
| Lancer une ingestion | Service → Add Ingestion → Deploy |
| Planifier | Configurer le cron dans l'ingestion |
| Monitorer | Service → Ingestion → Logs |
| Filtrer | Schema/Table Filter Pattern (regex) |

---

> **Prochain chapitre** : [Découverte et Documentation](04-decouverte-documentation.md) - Explorer et documenter vos assets
