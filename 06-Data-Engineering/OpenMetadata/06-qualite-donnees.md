# Chapitre 6 : Qualité des Données

## Table des matières

1. [Introduction à la data quality](#introduction-à-la-data-quality)
2. [Profiling des données](#profiling-des-données)
3. [Tests de qualité natifs](#tests-de-qualité-natifs)
4. [Tests personnalisés (SQL)](#tests-personnalisés-sql)
5. [Tableaux de bord de qualité](#tableaux-de-bord-de-qualité)
6. [Alertes sur les anomalies](#alertes-sur-les-anomalies)
7. [Intégration avec Great Expectations](#intégration-avec-great-expectations)

---

## Introduction à la data quality

### Pourquoi la qualité des données ?

> *"Garbage in, garbage out"* — Si les données sont mauvaises, les décisions basées sur elles le seront aussi.

### Les dimensions de la qualité

| Dimension | Question | Exemple de test |
|-----------|----------|-----------------|
| **Complétude** | Y a-t-il des valeurs manquantes ? | % de NULL dans une colonne |
| **Unicité** | Y a-t-il des doublons ? | Nombre de valeurs distinctes |
| **Validité** | Les valeurs respectent-elles les contraintes ? | Email contient '@' |
| **Cohérence** | Les données sont-elles cohérentes entre elles ? | total = quantité × prix |
| **Fraîcheur** | Les données sont-elles à jour ? | Dernière mise à jour < 24h |
| **Précision** | Les données reflètent-elles la réalité ? | Coordonnées GPS valides |

### OpenMetadata vs outils dédiés

| Fonctionnalité | OpenMetadata | Great Expectations | dbt tests |
|---------------|-------------|-------------------|-----------|
| Profiling automatique | ✅ | ✅ | ❌ |
| Tests natifs | ✅ (40+) | ✅ (300+) | ✅ (4 + packages) |
| Tests SQL custom | ✅ | ✅ | ✅ |
| Dashboard intégré | ✅ | ❌ (Data Docs) | ❌ |
| Alertes | ✅ | Via pipeline | Via pipeline |
| Intégré au catalog | ✅ | ❌ | ❌ |

**Avantage d'OpenMetadata** : qualité + catalog + lineage dans un seul outil.

---

## Profiling des données

### Qu'est-ce que le profiling ?

Le profiling calcule des **statistiques automatiques** sur vos données :

| Statistique | Niveau | Description |
|------------|--------|-------------|
| Row count | Table | Nombre total de lignes |
| Column count | Table | Nombre de colonnes |
| Null count | Colonne | Nombre de valeurs NULL |
| Null % | Colonne | Pourcentage de NULL |
| Distinct count | Colonne | Nombre de valeurs uniques |
| Min / Max | Colonne | Valeurs min et max |
| Mean / Median | Colonne | Moyenne et médiane (numériques) |
| Std Dev | Colonne | Écart-type (numériques) |
| Histogram | Colonne | Distribution des valeurs |

### Activer le profiling

1. Aller dans **Settings** → **Services** → **[Service]**
2. **Add Ingestion** → **Profiler Ingestion**
3. Configurer :

| Option | Description | Recommandation |
|--------|-------------|----------------|
| **Profile Sample** | % de données à profiler | 10-30% pour les grosses tables |
| **Thread Count** | Parallélisme | 2-4 |
| **Timeout** | Timeout par requête | 300s |
| **Ingest Sample Data** | Stocker un échantillon | Oui (utile pour preview) |

4. **Schedule** : Hebdomadaire (le profiling peut être coûteux en requêtes)
5. **Deploy**

### Profiling sélectif

Pour éviter de profiler les très grosses tables :

```yaml
# Filtrer par pattern de table
sourceConfig:
  config:
    type: Profiler
    tableFilterPattern:
      includes:
        - "dim_.*"
        - "fact_.*"
      excludes:
        - ".*_staging"
        - ".*_tmp"
    profileSample: 10  # Profiler seulement 10% des données
```

### Résultat du profiling

Après exécution, chaque table affiche dans l'onglet **Profiler** :

```
Table : dim_customers (15 432 lignes)
┌────────────────┬─────────┬────────┬──────────┬─────────┬───────────┐
│ Colonne        │ Type    │ Null % │ Distinct │ Min     │ Max       │
├────────────────┼─────────┼────────┼──────────┼─────────┼───────────┤
│ customer_id    │ INTEGER │ 0%     │ 15 432   │ 1       │ 15 432    │
│ first_name     │ VARCHAR │ 0%     │ 3 201    │ -       │ -         │
│ last_name      │ VARCHAR │ 0%     │ 8 912    │ -       │ -         │
│ email          │ VARCHAR │ 0%     │ 15 432   │ -       │ -         │
│ phone          │ VARCHAR │ 12.3%  │ 13 523   │ -       │ -         │
│ lifetime_value │ DECIMAL │ 0.5%   │ 11 203   │ 0.00    │ 45 231.99 │
│ created_at     │ TIMESTAMP│ 0%    │ 14 998   │ 2020-01 │ 2024-12   │
└────────────────┴─────────┴────────┴──────────┴─────────┴───────────┘
```

---

## Tests de qualité natifs

### Catégories de tests

OpenMetadata propose des tests pré-configurés organisés par catégorie :

### Tests au niveau table

| Test | Description | Paramètres |
|------|-------------|------------|
| `tableRowCountToEqual` | Le nombre de lignes doit être égal à N | `value: 1000` |
| `tableRowCountToBeBetween` | Le nombre de lignes doit être entre min et max | `min: 100, max: 10000` |
| `tableColumnCountToEqual` | Le nombre de colonnes doit être N | `value: 12` |
| `tableCustomSQLQuery` | Test SQL personnalisé | `sqlExpression: "..."` |

### Tests au niveau colonne

| Test | Description | Paramètres |
|------|-------------|------------|
| `columnValuesToBeNotNull` | Aucune valeur NULL | - |
| `columnValuesToBeUnique` | Toutes les valeurs uniques | - |
| `columnValuesToBeBetween` | Valeurs entre min et max | `min: 0, max: 100` |
| `columnValueLengthsToBeBetween` | Longueur entre min et max | `min: 5, max: 50` |
| `columnValuesToMatchRegex` | Valeurs matchant une regex | `regex: "^[A-Z].*"` |
| `columnValuesToBeInSet` | Valeurs dans un ensemble | `allowedValues: [...]` |
| `columnValuesMissingCount` | Nombre de NULL ≤ seuil | `missingCount: 10` |
| `columnValuesMissingPercentage` | % de NULL ≤ seuil | `missingPercentage: 5` |
| `columnValuesToNotMatchRegex` | Valeurs ne matchant PAS une regex | `forbiddenRegex: "..."` |
| `columnMean` | Moyenne dans un intervalle | `min: 10, max: 50` |
| `columnMedian` | Médiane dans un intervalle | `min: 10, max: 50` |
| `columnStdDev` | Écart-type dans un intervalle | `min: 0, max: 10` |

### Créer un test via l'UI

1. Ouvrir une table → Onglet **Data Quality**
2. Cliquer **Add Test**
3. Sélectionner le type de test
4. Configurer les paramètres
5. **Run** (exécution immédiate) ou **Schedule** (planifier)

### Exemple : tester la table `raw.customers`

Tests recommandés :

```
Table: raw.customers
├── Test 1: tableRowCountToBeBetween (min: 1, max: 1000000)
│   → S'assurer que la table n'est pas vide ni anormalement grosse
│
├── Column: customer_id
│   ├── Test 2: columnValuesToBeNotNull
│   └── Test 3: columnValuesToBeUnique
│
├── Column: email
│   ├── Test 4: columnValuesToBeNotNull
│   ├── Test 5: columnValuesToBeUnique
│   └── Test 6: columnValuesToMatchRegex (regex: "^.+@.+\\..+$")
│
├── Column: status
│   └── Test 7: columnValuesToBeInSet (["active", "inactive", "churned"])
│
└── Column: created_at
    └── Test 8: columnValuesToBeNotNull
```

---

## Tests personnalisés (SQL)

### Quand utiliser des tests SQL ?

Les tests natifs ne couvrent pas tous les cas. Les tests SQL permettent de vérifier des **règles métier complexes**.

### Syntaxe

Un test SQL custom doit retourner un **nombre**. Le test passe si le résultat respecte la condition.

### Exemples de tests SQL

#### 1. Intégrité référentielle

```sql
-- Nombre de commandes avec un customer_id qui n'existe pas
-- Attendu : 0
SELECT COUNT(*)
FROM raw.orders o
LEFT JOIN raw.customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
```

#### 2. Cohérence des montants

```sql
-- Nombre de commandes où le total ne correspond pas aux items
-- Attendu : 0
SELECT COUNT(*)
FROM raw.orders o
JOIN (
    SELECT order_id, SUM(quantity * unit_price) AS calculated_total
    FROM raw.order_items
    GROUP BY order_id
) oi ON o.order_id = oi.order_id
WHERE ABS(o.total_amount - oi.calculated_total) > 0.01
```

#### 3. Fraîcheur des données

```sql
-- Nombre d'heures depuis la dernière mise à jour
-- Attendu : < 24
SELECT EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(updated_at))) / 3600
FROM raw.customers
```

#### 4. Distribution anormale

```sql
-- Ratio de commandes "pending" (ne devrait pas dépasser 20%)
-- Attendu : < 20
SELECT
    (COUNT(*) FILTER (WHERE status = 'pending')::FLOAT / COUNT(*)) * 100
FROM raw.orders
WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
```

### Créer un test SQL via l'API

```python
test_case = {
    "name": "check_referential_integrity_orders",
    "entityLink": "<#E::table::demo-postgres.ecommerce.raw.orders>",
    "testDefinition": "tableCustomSQLQuery",
    "testSuite": "demo-postgres.ecommerce.raw.orders.testSuite",
    "parameterValues": [
        {
            "name": "sqlExpression",
            "value": "SELECT COUNT(*) FROM raw.orders o LEFT JOIN raw.customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL"
        },
        {
            "name": "strategy",
            "value": "COUNT"
        },
        {
            "name": "threshold",
            "value": "0"
        }
    ]
}

response = requests.post(
    f"{API_URL}/dataQuality/testCases",
    headers=headers,
    json=test_case
)
```

---

## Tableaux de bord de qualité

### Vue globale

La page **Quality** affiche un tableau de bord synthétique :

```
┌────────────────────────────────────────────────────────┐
│                Data Quality Overview                    │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Tests Total: 156    ✅ Pass: 142   ❌ Fail: 14         │
│                                                         │
│  ┌─────────────────────────────────────┐               │
│  │  Success Rate: 91%  ████████████░░  │               │
│  └─────────────────────────────────────┘               │
│                                                         │
│  Tables avec échecs :                                   │
│  ├── raw.orders       → 3 tests en échec              │
│  ├── raw.customers    → 2 tests en échec              │
│  └── analytics.daily  → 1 test en échec               │
│                                                         │
│  Tendance (30 jours) :                                  │
│  ████████████████████████████████                       │
│  Jan 1                        Jan 30                    │
└────────────────────────────────────────────────────────┘
```

### Vue par table

Chaque table a son propre tableau de bord qualité :

| Information | Détail |
|-------------|--------|
| Score global | % de tests passés |
| Historique | Évolution sur 7/30/90 jours |
| Tests en échec | Liste avec détails et dernière exécution |
| Profiling | Métriques et tendances des colonnes |

### Métriques de suivi

| Métrique | Description | Cible |
|----------|-------------|-------|
| **Test coverage** | % de tables avec des tests | > 80% |
| **Success rate** | % de tests qui passent | > 95% |
| **Mean time to fix** | Temps moyen pour corriger un échec | < 24h |
| **Freshness** | Âge des données par rapport au SLA | Selon le Tier |

---

## Alertes sur les anomalies

### Configuration des alertes

1. **Settings** → **Notifications** → **Add Alert**
2. Configurer :

| Paramètre | Options |
|-----------|---------|
| **Trigger** | Test failure, Status change, Anomaly detected |
| **Filter** | Par service, table, owner, tier |
| **Destination** | Slack, Teams, Email, Webhook |
| **Fréquence** | Immédiate, Résumé quotidien |

### Exemple d'alerte Slack

```json
{
    "name": "DQ Alert - Tier 1 Tables",
    "trigger": {
        "type": "testCaseFailure"
    },
    "filteringRules": {
        "resources": ["table"],
        "condition": "matchAnyTag",
        "tags": ["Tier.Tier1"]
    },
    "destinations": [{
        "type": "slack",
        "config": {
            "webhookUrl": "https://hooks.slack.com/services/xxx/yyy/zzz"
        }
    }]
}
```

### Message d'alerte type

```
🔴 Data Quality Alert
━━━━━━━━━━━━━━━━━━━━
Table: demo-postgres.ecommerce.raw.orders
Test: columnValuesToBeNotNull (column: customer_id)
Status: FAILED
Details: 15 NULL values found (expected: 0)
Time: 2024-01-16 02:15:00 UTC
Owner: data-engineering

🔗 View in OpenMetadata
```

---

## Intégration avec Great Expectations

### Pourquoi intégrer Great Expectations ?

Great Expectations offre **300+ tests** pré-configurés vs ~40 dans OpenMetadata. L'intégration permet d'utiliser les tests GE tout en visualisant les résultats dans OpenMetadata.

### Architecture d'intégration

```
Great Expectations          OpenMetadata
┌───────────────────┐      ┌───────────────────┐
│ Expectations      │      │ Data Quality      │
│ (300+ tests)      │      │ Dashboard         │
│                   │─────▶│                   │
│ Validation        │      │ Résultats         │
│ Results           │      │ centralisés       │
└───────────────────┘      └───────────────────┘
```

### Configuration

```python
# Pipeline Great Expectations → OpenMetadata
from metadata.ingestion.api.workflow import Workflow

config = {
    "source": {
        "type": "great-expectations",
        "serviceName": "ge-ecommerce",
        "sourceConfig": {
            "config": {
                "type": "TestSuite",
                "entityFullyQualifiedName": "demo-postgres.ecommerce.raw.customers"
            }
        }
    },
    "processor": {
        "type": "orm-test-runner",
        "config": {
            "testCases": [
                {
                    "name": "ge_customers_email_valid",
                    "testDefinitionName": "columnValuesToMatchRegex",
                    "columnName": "email",
                    "parameterValues": [
                        {"name": "regex", "value": "^.+@.+\\..+$"}
                    ]
                }
            ]
        }
    },
    "sink": {"type": "metadata-rest", "config": {}}
}
```

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| Profiling | Statistiques automatiques (null%, min/max, distribution) |
| Tests natifs | 40+ tests pré-configurés (table et colonne) |
| Tests SQL | Tests personnalisés pour les règles métier |
| Dashboard | Vue globale et par table de la qualité |
| Alertes | Notifications sur Slack/Teams/Email |
| Great Expectations | Intégration pour tests avancés (300+) |

---

> **Prochain chapitre** : [Glossaire Métier et Classification](07-glossaire-classification.md) - Formaliser le vocabulaire et protéger les données sensibles
