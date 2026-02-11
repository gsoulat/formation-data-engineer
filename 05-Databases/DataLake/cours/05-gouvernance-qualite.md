# Module 05 - Gouvernance et qualite des donnees

## Pourquoi la gouvernance est-elle critique ?

Un Data Lake sans gouvernance devient rapidement un **Data Swamp** (marecage de donnees) : personne ne sait quelles donnees existent, ou elles sont, si elles sont fiables, et qui a le droit de les utiliser.

```
Data Lake bien gouverne              Data Swamp
+---------------------------+       +---------------------------+
| Donnees cataloguees       |       | "C'est quoi ce fichier ?" |
| Qualite mesuree           |       | "Ca date de quand ?"      |
| Acces controle            |       | "C'est fiable ?"          |
| Lineage trace             |       | "Qui a le droit ?"        |
| Proprietaires identifies  |       | "Ca sert a quoi ?"        |
+---------------------------+       +---------------------------+
      Exploitable                        Inutilisable
```

## Les 4 piliers de la gouvernance Data Lake

```
+-------------------------------------------------------------------+
|                     GOUVERNANCE DATA LAKE                         |
+-------------------------------------------------------------------+
|                                                                   |
|  1. CATALOGAGE        2. QUALITE        3. SECURITE  4. LINEAGE  |
|  Decouvrir les        Mesurer et        Controler    Tracer       |
|  donnees              garantir la       les acces    l'origine    |
|                       fiabilite                                   |
+-------------------------------------------------------------------+
```

## 1. Data Catalog (Catalogage)

### Qu'est-ce qu'un Data Catalog ?

Un Data Catalog est un **inventaire centralise** de toutes les donnees disponibles dans le Data Lake, avec leurs metadonnees.

```
Data Catalog
+---------------------------------------------------+
| Table: orders                                      |
| +-----------------------------------------------+ |
| | Localisation : s3://lake/curated/orders/       | |
| | Format       : Delta Lake (Parquet)            | |
| | Partitions   : year, month                     | |
| | Lignes       : 12,450,000                      | |
| | Taille       : 2.3 Go                          | |
| | Schema :                                       | |
| |   - order_id    : BIGINT (PK)                  | |
| |   - customer_id : STRING                       | |
| |   - amount      : DECIMAL(10,2)                | |
| |   - order_date  : DATE                         | |
| |   - status      : STRING                       | |
| | Proprietaire : equipe-ecommerce                | |
| | Classification : Confidentiel                  | |
| | Tags : #ecommerce #transactionnel #pii        | |
| | MAJ : 2024-01-15 08:30:00                      | |
| +-----------------------------------------------+ |
+---------------------------------------------------+
```

### Outils de Data Catalog

| Outil | Type | Ecosysteme | Forces |
|-------|------|-----------|--------|
| **AWS Glue Data Catalog** | Manage | AWS | Integre Athena/Redshift, crawlers auto |
| **Azure Purview** | Manage | Azure | Scan multi-sources, classification auto |
| **Databricks Unity Catalog** | Manage | Databricks | Gouvernance unifiee Delta Lake |
| **Apache Atlas** | Open source | Hadoop | Lineage, classification |
| **DataHub** | Open source | Multi | LinkedIn, API-first, moderne |
| **OpenMetadata** | Open source | Multi | Standard ouvert, UI moderne |

### Metadonnees essentielles

| Categorie | Metadonnees | Exemple |
|-----------|-------------|---------|
| **Techniques** | Schema, format, taille, partitions | `orders : 12M lignes, Parquet, 2.3 Go` |
| **Metier** | Description, domaine, glossaire | `Table des commandes e-commerce B2C` |
| **Operationnelles** | Frequence MAJ, derniere ingestion, job | `Daily, 2024-01-15 08:30, dag_orders` |
| **Qualite** | Completude, fraicheur, unicite | `99.2% complet, <2h de retard` |
| **Securite** | Classification, PII, proprietaire | `Confidentiel, contient email/telephone` |

## 2. Qualite des donnees (Data Quality)

### Les dimensions de la qualite

| Dimension | Definition | Mesure | Seuil typique |
|-----------|-----------|--------|---------------|
| **Completude** | Pas de valeurs manquantes | % de champs non-null | > 95% |
| **Unicite** | Pas de doublons | % de lignes uniques | > 99.9% |
| **Validite** | Valeurs dans les plages attendues | % de valeurs valides | > 99% |
| **Coherence** | Donnees coherentes entre sources | % de correspondances | > 98% |
| **Fraicheur** | Donnees a jour | Age des donnees | < SLA defini |
| **Exactitude** | Donnees refletent la realite | Validation manuelle | Echantillonnage |

### Ou appliquer les controles de qualite ?

```
Zone Raw (Bronze)         Zone Curated (Silver)       Zone Consumption (Gold)
+-------------------+    +-------------------+       +-------------------+
| Controles legers  |    | Controles stricts |       | Controles metier  |
| - Fichier recu ?  |    | - Schema valide ? |       | - KPIs coherents? |
| - Taille > 0 ?    |    | - Pas de doublons?|       | - Totaux corrects?|
| - Format correct? |    | - Valeurs valides?|       | - SLA respecte ?  |
| - Lignes > 0 ?    |    | - Completude OK ? |       | - Reconciliation? |
+-------------------+    +-------------------+       +-------------------+
      GATE 1                   GATE 2                      GATE 3
```

### Outils de Data Quality

| Outil | Type | Approche |
|-------|------|----------|
| **Great Expectations** | Open source | Tests en Python, documentation auto |
| **dbt tests** | Open source | Tests SQL integres a dbt |
| **Soda** | Open source / SaaS | YAML declaratif, multi-sources |
| **AWS Deequ** | Open source (AWS) | Scala/Spark, Amazon |
| **Monte Carlo** | SaaS | Observabilite, detection d'anomalies |

### Exemple : tests de qualite avec dbt

```yaml
# schema.yml
models:
  - name: orders_curated
    description: "Commandes nettoyees et validees"
    columns:
      - name: order_id
        description: "Identifiant unique de la commande"
        tests:
          - unique
          - not_null

      - name: amount
        description: "Montant de la commande en euros"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100000

      - name: status
        description: "Statut de la commande"
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']

      - name: customer_id
        description: "Reference client"
        tests:
          - not_null
          - relationships:
              to: ref('customers_curated')
              field: customer_id
```

### Exemple : tests avec Great Expectations

```python
import great_expectations as gx

context = gx.get_context()

# Creer une suite de tests
suite = context.add_expectation_suite("orders_quality")

# Definir les attentes
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="orders_quality"
)

# Tests de completude
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_not_be_null("amount")

# Tests de validite
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=100000)
validator.expect_column_values_to_be_in_set(
    "status",
    ["pending", "confirmed", "shipped", "delivered", "cancelled"]
)

# Tests d'unicite
validator.expect_column_values_to_be_unique("order_id")

# Tests de fraicheur
validator.expect_column_max_to_be_between(
    "order_date",
    min_value="2024-01-14",
    max_value="2024-01-16"
)

# Executer et generer le rapport
results = validator.validate()
```

## 3. Securite et controle d'acces

### Modeles de securite

#### RBAC (Role-Based Access Control)

```
Roles                    Permissions                 Zones
+--------------+        +--------------------+      +-------------+
| data_engineer| -----> | read/write Raw     | ---> | /raw/       |
|              |        | read/write Curated |      | /curated/   |
+--------------+        +--------------------+      +-------------+

+--------------+        +--------------------+      +-------------+
| data_analyst | -----> | read Curated       | ---> | /curated/   |
|              |        | read Consumption   |      | /consumption|
+--------------+        +--------------------+      +-------------+

+--------------+        +--------------------+      +-------------+
| data_scientist| ----> | read Curated       | ---> | /curated/   |
|              |        | read/write ML zone |      | /ml/        |
+--------------+        +--------------------+      +-------------+

+--------------+        +--------------------+      +-------------+
| bi_user      | -----> | read Consumption   | ---> | /consumption|
+--------------+        +--------------------+      +-------------+
```

#### Securite au niveau des donnees

| Niveau | Description | Exemple |
|--------|-------------|---------|
| **Table-level** | Acces a une table entiere | L'equipe finance accede a `revenue` |
| **Column-level** | Acces a certaines colonnes | Masquer la colonne `salary` |
| **Row-level** | Acces a certaines lignes | Chaque region voit ses propres donnees |
| **Cell-level** | Masquage de valeurs specifiques | `email` affiche comme `a***@mail.com` |

### Conformite RGPD / donnees personnelles

```
Donnees personnelles dans le Data Lake :

Identification          Pseudonymisation        Anonymisation
+----------------+     +----------------+     +----------------+
| Jean Dupont    |     | USR-a7b3c      |     | [supprime]     |
| jean@mail.com  | --> | hash(email)    | --> | [supprime]     |
| 06 12 34 56 78 |     | ***-**-56-78   |     | [supprime]     |
| Paris          |     | Paris          |     | Ile-de-France  |
+----------------+     +----------------+     +----------------+
   Zone Raw               Zone Curated          Zone Consumption
   (acces restreint)      (acces controle)      (acces large)
```

**Actions RGPD sur le Data Lake :**

| Droit RGPD | Implementation Data Lake |
|------------|-------------------------|
| Droit d'acces | Cataloguer les PII, requete de recherche |
| Droit a l'oubli | Suppression dans toutes les zones (problematique avec l'immutabilite !) |
| Droit de rectification | Mise a jour dans les zones Curated/Consumption |
| Minimisation | Ne collecter que le necessaire |
| Limitation du traitement | Controle d'acces fin (RBAC) |

### Chiffrement

```
Chiffrement au repos (at rest)          Chiffrement en transit
+----------------------------+         +----------------------------+
| S3 : SSE-S3, SSE-KMS      |         | HTTPS / TLS               |
| ADLS : Microsoft-managed   |         | VPN / Private Link        |
| GCS : Google-managed       |         | VPC Endpoints             |
+----------------------------+         +----------------------------+
```

## 4. Data Lineage (Tracabilite)

### Qu'est-ce que le Data Lineage ?

Le Data Lineage trace le **parcours complet des donnees** depuis leur source jusqu'a leur consommation.

```
Lineage de la table "monthly_revenue" :

Source              Raw                Curated            Consumption
+--------+    +----------+     +-----------+     +----------------+
| ERP    |--->| raw/     |-+-->| curated/  |-+-->| consumption/   |
| orders |    | orders/  | |   | orders/   | |   | monthly_revenue|
+--------+    +----------+ |   +-----------+ |   +----------------+
                           |                 |
+--------+    +----------+ |   +-----------+ |
| CRM    |--->| raw/     |-+-->| curated/  |-+
| clients|    | clients/ |     | customers/|
+--------+    +----------+     +-----------+

Transformations appliquees :
1. Raw -> Curated : nettoyage, deduplication, jointure ERP+CRM
2. Curated -> Consumption : agregation mensuelle, calcul du CA
```

### Pourquoi le lineage est-il important ?

| Besoin | Utilite du lineage |
|--------|-------------------|
| **Impact analysis** | Si la source change, quels rapports sont impactes ? |
| **Root cause analysis** | Un KPI est faux : d'ou vient l'erreur ? |
| **Conformite** | Prouver la provenance des donnees (audit) |
| **Documentation** | Comprendre comment une metrique est calculee |
| **Migration** | Identifier toutes les dependances avant de migrer |

### Outils de lineage

| Outil | Integration | Particularite |
|-------|-------------|---------------|
| **dbt** | SQL models | Lineage automatique via `ref()` |
| **Apache Atlas** | Hadoop | Standard Hadoop |
| **Azure Purview** | Azure | Scan automatique, classification |
| **DataHub** | Multi | API-first, open source |
| **OpenLineage** | Multi | Standard ouvert, OpenTelemetry-like |

## Framework de gouvernance : implementation pratique

### Etape 1 : Definir les roles et responsabilites

| Role | Responsabilite |
|------|---------------|
| **Data Owner** | Proprietaire metier des donnees, definit les regles |
| **Data Steward** | Gardien de la qualite, maintient le catalogue |
| **Data Engineer** | Implemente les pipelines et controles |
| **Data Platform** | Infrastructure, securite, performance |

### Etape 2 : Convention de nommage

```
/{zone}/{domaine}/{entite}/{partitions}/

Zones       : raw, curated, consumption
Domaines    : finance, marketing, operations, hr
Entites     : orders, customers, products
Partitions  : year=YYYY/month=MM/day=DD

Exemples :
/raw/ecommerce/orders/ingestion_date=2024-01-15/
/curated/ecommerce/orders/year=2024/month=01/
/consumption/finance/monthly_revenue/year=2024/month=01/
```

### Etape 3 : Mettre en place les quality gates

```
Source --> [Ingest] --> Gate 1 --> [Clean] --> Gate 2 --> [Aggregate] --> Gate 3
                         |                     |                          |
                    Fichier OK?           Schema OK?               KPIs OK?
                    Taille > 0?           Doublons < 0.1%?         Totaux corrects?
                    Format valide?        Null < 5%?               SLA respecte?
                         |                     |                          |
                    Si KO: alerte         Si KO: quarantaine       Si KO: rollback
```

## Points cles a retenir

- La **gouvernance** est ce qui distingue un Data Lake d'un Data Swamp
- Les **4 piliers** : Catalogage, Qualite, Securite, Lineage
- Le **Data Catalog** est le point d'entree pour decouvrir les donnees
- Les **tests de qualite** doivent etre automatises et integres aux pipelines (quality gates)
- La **securite** s'applique a tous les niveaux : zone, table, colonne, ligne
- Le **lineage** est essentiel pour l'audit, le debug et la conformite RGPD
- Definir des **roles clairs** (Data Owner, Steward, Engineer) des le depart

---

**Prochain module :** [06 - Technologies et plateformes Cloud](./06-technologies-cloud.md)

[Retour au sommaire](./README.md)
