# Brief : Pipeline Data Warehouse E-commerce sur BigQuery

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 2 jours (14 heures) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | GCP, BigQuery, Cloud Storage, SQL |
| **Prérequis** | [Cours Data Warehouse](../../../05-Databases/DataWarehouse/cours/) + [Cours BigQuery](../../../04-Cloud-Platforms/GCP/BigQuery/) |

## Contexte

Vous êtes Data Engineer chez **ShopFlow**, une entreprise e-commerce en pleine croissance. L'équipe data actuelle utilise des fichiers CSV exportés manuellement pour l'analyse. Votre mission est de construire un **Data Warehouse moderne** sur BigQuery en implémentant l'**architecture Medallion** (Bronze/Silver/Gold).

Le CEO veut pouvoir répondre rapidement à ces questions :
- Quel est le chiffre d'affaires par jour/mois/région ?
- Quels sont les clients les plus rentables ?
- Quels produits se vendent le mieux ?
- Comment évolue le panier moyen ?

## Objectifs pédagogiques

A l'issue de ce brief, vous serez capable de :

- Configurer un environnement BigQuery avec datasets Bronze/Silver/Gold
- Ingérer des données depuis Cloud Storage vers BigQuery
- Implémenter des transformations Bronze → Silver → Gold
- Automatiser le pipeline avec des Stored Procedures
- Planifier des rafraîchissements avec Scheduled Queries
- Optimiser les coûts et performances (partitionnement, clustering)

## Données fournies

Trois fichiers CSV simulant les exports du système e-commerce :

### 1. orders.csv (Commandes)

```csv
order_id,order_date,customer_id,shipping_country,payment_method,status
```

### 2. order_items.csv (Lignes de commande)

```csv
order_item_id,order_id,product_id,quantity,unit_price,discount_pct
```

### 3. customers.csv (Clients)

```csv
customer_id,email,first_name,last_name,country,registration_date,segment
```

### 4. products.csv (Produits)

```csv
product_id,product_name,category,brand,cost_price,selling_price
```

Les fichiers sont disponibles dans le dossier `data/` de ce brief.

---

## JOUR 1 : Setup et couche Bronze/Silver (7h)

### Partie 1 : Configuration de l'environnement (1h30)

#### Tâche 1.1 : Créer le projet GCP

- [ ] Créer un nouveau projet GCP : `shopflow-dwh-[votre-nom]`
- [ ] Activer l'API BigQuery
- [ ] Vérifier les quotas Free Tier

#### Tâche 1.2 : Créer les datasets Medallion

- [ ] Créer le dataset `bronze` (région EU)
- [ ] Créer le dataset `silver` (région EU)
- [ ] Créer le dataset `gold` (région EU)
- [ ] Ajouter des labels : `layer=bronze/silver/gold`, `project=shopflow`

#### Tâche 1.3 : Créer le bucket Cloud Storage

- [ ] Créer un bucket : `shopflow-data-[votre-nom]`
- [ ] Créer les dossiers : `landing/`, `archive/`, `rejected/`
- [ ] Uploader les fichiers CSV dans `landing/`

**Livrable :** Screenshot montrant les 3 datasets et le bucket avec les fichiers.

---

### Partie 2 : Couche Bronze - Ingestion (2h)

#### Tâche 2.1 : Créer les tables Bronze

Créer les tables Bronze avec :
- Tous les champs en STRING (données brutes)
- Colonnes de métadonnées : `_ingested_at`, `_source_file`
- Partitionnement par `_ingested_at`

```sql
-- Exemple de structure attendue pour bronze.raw_orders
CREATE TABLE bronze.raw_orders (
    _ingested_at TIMESTAMP,
    _source_file STRING,
    order_id STRING,
    order_date STRING,
    customer_id STRING,
    shipping_country STRING,
    payment_method STRING,
    status STRING
)
PARTITION BY DATE(_ingested_at);
```

- [ ] Créer `bronze.raw_orders`
- [ ] Créer `bronze.raw_order_items`
- [ ] Créer `bronze.raw_customers`
- [ ] Créer `bronze.raw_products`

#### Tâche 2.2 : Charger les données

- [ ] Charger les CSV depuis Cloud Storage vers les tables Bronze
- [ ] Utiliser LOAD DATA ou bq CLI
- [ ] Vérifier le nombre de lignes chargées

**Livrable :** Requêtes SQL de création des tables + résultat du chargement (row count).

---

### Partie 3 : Couche Silver - Transformation (3h30)

#### Tâche 3.1 : Transformer les commandes

Créer `silver.clean_orders` avec :
- Types corrects (DATE, INT64, etc.)
- Dédoublonnage sur `order_id`
- Normalisation des pays (`FR`, `DE`, `UK`, etc.)
- Filtrage des commandes invalides

Transformations attendues :

| Champ source | Transformation | Champ cible |
|--------------|----------------|-------------|
| order_id | Cast STRING | order_id STRING |
| order_date | PARSE_DATE | order_date DATE |
| customer_id | UPPER, TRIM | customer_id STRING |
| shipping_country | UPPER | country_code STRING |
| payment_method | UPPER | payment_method STRING |
| status | UPPER | status STRING |

- [ ] Créer la table `silver.clean_orders` partitionnée par `order_date`

#### Tâche 3.2 : Transformer les lignes de commande

Créer `silver.clean_order_items` avec :
- Montant total calculé : `quantity * unit_price * (1 - discount_pct/100)`
- Types numériques corrects

- [ ] Créer la table avec le calcul du montant

#### Tâche 3.3 : Transformer les clients

Créer `silver.clean_customers` avec :
- Email normalisé (lowercase)
- Domaine email extrait
- Date d'inscription parsée

- [ ] Créer la table avec les transformations

#### Tâche 3.4 : Transformer les produits

Créer `silver.clean_products` avec :
- Marge calculée : `selling_price - cost_price`
- Catégorie normalisée

- [ ] Créer la table avec le calcul de marge

#### Tâche 3.5 : Créer une vue de qualité

- [ ] Créer `silver.vw_quality_report` affichant pour chaque table :
  - Nombre total de lignes
  - Nombre de valeurs NULL par colonne clé
  - Min/Max dates

**Livrable :** Scripts SQL complets de transformation Bronze → Silver.

---

## JOUR 2 : Couche Gold et Automatisation (7h)

### Partie 4 : Couche Gold - Agrégations (3h)

#### Tâche 4.1 : Fact Table - Ventes

Créer `gold.fact_sales` en joignant orders, order_items, customers, products :

```sql
-- Structure attendue
fact_sales (
    sale_id,           -- order_item_id
    order_id,
    order_date,
    customer_id,
    customer_email,
    customer_segment,
    product_id,
    product_name,
    category,
    brand,
    country_code,
    quantity,
    unit_price,
    discount_pct,
    line_total,
    cost_price,
    margin
)
```

- [ ] Créer `gold.fact_sales` partitionnée par `order_date`, clusterisée par `category`

#### Tâche 4.2 : Agrégation quotidienne

Créer `gold.agg_sales_daily` :

| Métrique | Calcul |
|----------|--------|
| order_count | COUNT(DISTINCT order_id) |
| item_count | COUNT(*) |
| total_revenue | SUM(line_total) |
| total_cost | SUM(quantity * cost_price) |
| total_margin | SUM(margin) |
| avg_order_value | AVG sur les commandes |
| unique_customers | COUNT(DISTINCT customer_id) |

- [ ] Créer la table avec toutes les métriques

#### Tâche 4.3 : Vue Customer 360

Créer `gold.dm_customer_360` :

| Métrique | Description |
|----------|-------------|
| first_order_date | Première commande |
| last_order_date | Dernière commande |
| total_orders | Nombre de commandes |
| total_items | Nombre d'articles |
| lifetime_value | Somme des achats |
| avg_order_value | Panier moyen |
| favorite_category | Catégorie la plus achetée |
| days_since_last_order | Récence |
| customer_status | Active/At Risk/Churned |

- [ ] Créer la table avec le calcul de la catégorie favorite (MODE)

#### Tâche 4.4 : Tendances mensuelles

Créer `gold.agg_monthly_trends` avec :
- Revenue par mois
- Croissance vs mois précédent (%)
- Nombre de nouveaux clients

- [ ] Créer la table avec les calculs de croissance (LAG)

**Livrable :** Scripts SQL complets de création des tables Gold.

---

### Partie 5 : Automatisation (2h30)

#### Tâche 5.1 : Créer les Stored Procedures

- [ ] `silver.sp_refresh_orders()` - Bronze → Silver pour orders
- [ ] `silver.sp_refresh_all()` - Appelle toutes les transformations Silver
- [ ] `gold.sp_refresh_all()` - Crée toutes les tables Gold
- [ ] `pipeline.sp_run_full_etl()` - Orchestre tout le pipeline

Chaque procédure doit :
- Logger le début et la fin dans une table `pipeline.logs`
- Compter les lignes traitées
- Gérer les erreurs avec EXCEPTION

#### Tâche 5.2 : Créer la table de logs

```sql
-- Structure attendue
pipeline.logs (
    log_id STRING,
    procedure_name STRING,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    rows_processed INT64,
    status STRING,  -- SUCCESS, ERROR
    error_message STRING
)
```

- [ ] Créer la table de logs
- [ ] Intégrer le logging dans les procédures

#### Tâche 5.3 : Planifier l'exécution

- [ ] Créer une Scheduled Query qui appelle `CALL pipeline.sp_run_full_etl()`
- [ ] Configurer pour exécution quotidienne à 6h00 UTC
- [ ] Tester manuellement

**Livrable :** Scripts des procédures stockées + screenshot de la Scheduled Query.

---

### Partie 6 : Optimisation et documentation (1h30)

#### Tâche 6.1 : Optimiser les tables

- [ ] Vérifier que les tables Gold sont partitionnées et clusterisées
- [ ] Exécuter ANALYZE TABLE sur les tables Gold
- [ ] Documenter les choix de partitionnement/clustering

#### Tâche 6.2 : Créer un dashboard de monitoring

Créer une vue `pipeline.vw_monitoring` affichant :
- Dernière exécution de chaque procédure
- Statut (SUCCESS/ERROR)
- Temps d'exécution
- Lignes traitées

- [ ] Créer la vue de monitoring

#### Tâche 6.3 : Documentation

Créer un fichier `README.md` documentant :
- Architecture du pipeline (schéma)
- Description de chaque table
- Procédure de refresh manuel
- Contacts et escalade

- [ ] Créer la documentation

**Livrable :** README.md + vue de monitoring fonctionnelle.

---

## Critères de validation

### Fonctionnel (60%)

| Critère | Points |
|---------|--------|
| Bronze : 4 tables avec métadonnées d'ingestion | 10 |
| Silver : 4 tables avec transformations correctes | 15 |
| Gold : Fact table + 3 agrégations | 15 |
| Procédures stockées fonctionnelles | 10 |
| Pipeline automatisé (Scheduled Query) | 10 |

### Qualité (25%)

| Critère | Points |
|---------|--------|
| Partitionnement et clustering appropriés | 10 |
| Gestion des erreurs dans les procédures | 5 |
| Logging et monitoring | 5 |
| Code SQL propre et commenté | 5 |

### Documentation (15%)

| Critère | Points |
|---------|--------|
| README complet | 10 |
| Schéma d'architecture | 5 |

**Total : 100 points**

---

## Bonus (optionnel)

- [ ] Implémenter avec Dataform au lieu des Scheduled Queries (+10 points)
- [ ] Créer un dashboard Looker Studio connecté aux tables Gold (+10 points)
- [ ] Ajouter des assertions de qualité (tests de non-nullité, etc.) (+5 points)
- [ ] Implémenter un traitement incrémental pour Silver (+10 points)

---

## Ressources

- [Cours Data Warehouse](../../../05-Databases/DataWarehouse/cours/)
- [Cours BigQuery](../../../04-Cloud-Platforms/GCP/BigQuery/)
- [Documentation BigQuery](https://cloud.google.com/bigquery/docs)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)

---

## Livrables attendus

A la fin des 2 jours, vous devez rendre :

1. **Scripts SQL** : Tous les scripts de création de tables et procédures
2. **Screenshots** : Console BigQuery montrant les datasets et tables
3. **README.md** : Documentation du pipeline
4. **Réponses aux questions** : Document répondant aux questions business du CEO

### Questions business à répondre

Avec vos tables Gold, répondez à ces questions (requêtes SQL + résultats) :

1. Quel est le chiffre d'affaires total par mois en 2024 ?
2. Quels sont les 10 clients avec le plus haut lifetime value ?
3. Quelles sont les 5 catégories de produits les plus rentables (marge) ?
4. Quel est le panier moyen par pays ?
5. Combien de clients sont "At Risk" (pas d'achat depuis 30-90 jours) ?
