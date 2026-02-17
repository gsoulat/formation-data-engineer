# Chapitre 4 : Découverte et Documentation

## Table des matières

1. [Recherche et exploration](#recherche-et-exploration)
2. [Documentation des assets](#documentation-des-assets)
3. [Tags et labels](#tags-et-labels)
4. [Ownership et responsabilité](#ownership-et-responsabilité)
5. [Tiers et importance](#tiers-et-importance)
6. [Bonnes pratiques de documentation](#bonnes-pratiques-de-documentation)

---

## Recherche et exploration

### Recherche globale

La barre de recherche d'OpenMetadata utilise **Elasticsearch** pour une recherche full-text sur :

- Noms de tables, colonnes, dashboards, pipelines
- Descriptions et documentation
- Tags et classifications
- Owners et équipes

### Syntaxe de recherche

| Syntaxe | Exemple | Résultat |
|---------|---------|----------|
| Mot-clé simple | `customers` | Tous les assets contenant "customers" |
| Phrase exacte | `"daily sales"` | Assets contenant la phrase exacte |
| Champ spécifique | `owner:data-team` | Assets appartenant à data-team |
| Tag | `tags:PII` | Assets tagués PII |
| Type | `table:dim_customers` | Rechercher uniquement dans les tables |

### Filtres dans Explore

La page **Explore** propose des filtres avancés :

```
Explore
├── Filtres par type
│   ├── Tables (156)
│   ├── Topics (12)
│   ├── Dashboards (34)
│   ├── Pipelines (8)
│   └── ML Models (3)
│
├── Filtres par service
│   ├── demo-postgres (45)
│   ├── bigquery-prod (89)
│   └── snowflake-analytics (22)
│
├── Filtres par tag
│   ├── PII (12)
│   ├── Tier1 (34)
│   └── Finance (18)
│
└── Filtres par owner
    ├── data-engineering (67)
    ├── data-analytics (52)
    └── data-science (37)
```

### Page détaillée d'une table

Quand vous ouvrez une table, vous accédez à :

| Onglet | Contenu |
|--------|---------|
| **Schema** | Colonnes, types, descriptions, tags |
| **Activity Feed** | Historique des modifications et conversations |
| **Sample Data** | Aperçu des données (premières lignes) |
| **Queries** | Requêtes fréquentes sur cette table |
| **Profiler** | Statistiques sur les colonnes |
| **Data Quality** | Tests et résultats |
| **Lineage** | Graphe de dépendances |
| **Custom Properties** | Propriétés personnalisées |

---

## Documentation des assets

### Documenter une table

La documentation se fait en **Markdown** directement dans l'interface :

1. Ouvrir la table dans Explore
2. Cliquer sur l'icône d'édition à côté de la description
3. Rédiger la documentation en Markdown

**Exemple de bonne documentation pour une table** :

```markdown
## Table `raw.customers`

Table principale des clients de la plateforme e-commerce.

### Source
- Alimentée par le système CRM (Salesforce) via un pipeline Airflow quotidien
- Refresh : chaque jour à 02h00 UTC

### Règles métier
- Un client est identifié de manière unique par son `email`
- Le champ `status` peut être : 'active', 'inactive', 'churned'
- Les clients `churned` sont ceux sans commande depuis 12 mois

### Contacts
- **Owner** : Data Engineering Team
- **SME** : Marie Dupont (équipe CRM)
```

### Documenter les colonnes

Chaque colonne peut avoir sa propre description :

| Colonne | Type | Description |
|---------|------|-------------|
| `customer_id` | INTEGER | Identifiant unique auto-incrémenté |
| `email` | VARCHAR | Email du client, utilisé comme identifiant métier. **PII** |
| `status` | VARCHAR | Statut du client : 'active', 'inactive', 'churned' |
| `lifetime_value` | DECIMAL | Valeur totale des commandes du client (calculée) |

### Documentation via l'API

```python
import requests

API_URL = "http://localhost:8585/api/v1"
TOKEN = "votre-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Mettre à jour la description d'une table
table_fqn = "demo-postgres.ecommerce.raw.customers"

response = requests.patch(
    f"{API_URL}/tables/name/{table_fqn}",
    headers={**headers, "Content-Type": "application/json-patch+json"},
    json=[{
        "op": "add",
        "path": "/description",
        "value": "Table principale des clients e-commerce. Alimentée quotidiennement depuis le CRM."
    }]
)
```

---

## Tags et labels

### Système de tags

OpenMetadata propose deux types de catégorisation :

| Type | Usage | Exemple |
|------|-------|---------|
| **Tags** | Classification technique libre | `PII`, `Deprecated`, `Tier1` |
| **Glossary Terms** | Termes métier formalisés | `Revenue`, `Client Actif`, `Churn Rate` |

### Tags par défaut

OpenMetadata fournit des catégories de tags pré-configurées :

```
Tags
├── PersonalData (PII)
│   ├── Personal
│   ├── Sensitive
│   └── SpecialCategory
│
├── Tier
│   ├── Tier1 (Mission Critical)
│   ├── Tier2 (Important)
│   ├── Tier3 (Standard)
│   ├── Tier4 (Nice to Have)
│   └── Tier5 (Deprecated)
│
└── Classification personnalisée
    ├── Finance
    ├── Marketing
    └── Operations
```

### Créer une catégorie de tags

1. **Settings** → **Tags** → **Add Tag**
2. Définir le nom, la description et les tags enfants
3. Appliquer les tags aux tables et colonnes

### Appliquer des tags

**Via l'UI** :
- Ouvrir une table → Schema → Cliquer sur "+" à côté de la colonne → Sélectionner le tag

**Via l'API** :

```python
# Ajouter un tag PII à une colonne
response = requests.patch(
    f"{API_URL}/tables/name/{table_fqn}",
    headers={**headers, "Content-Type": "application/json-patch+json"},
    json=[{
        "op": "add",
        "path": "/columns/3/tags/0",  # Index de la colonne
        "value": {
            "tagFQN": "PersonalData.Personal",
            "labelType": "Manual",
            "state": "Confirmed",
            "source": "Classification"
        }
    }]
)
```

---

## Ownership et responsabilité

### Pourquoi l'ownership est important ?

L'ownership répond à la question : **"Qui contacter quand il y a un problème avec cette donnée ?"**

### Types d'owners

| Type | Description | Exemple |
|------|-------------|---------|
| **User** | Personne individuelle | `alice.martin` |
| **Team** | Équipe | `data-engineering` |

### Assigner un owner

**Via l'UI** :
1. Ouvrir l'asset → Cliquer sur "No Owner" ou l'owner actuel
2. Rechercher et sélectionner l'utilisateur ou l'équipe

**Bonne pratique** : Assigner une **équipe** plutôt qu'un individu pour éviter les problèmes de turnover.

### Structure des équipes

```
Organisation
├── Data Platform
│   ├── Data Engineering (pipelines, infra)
│   └── Data Ops (monitoring, qualité)
│
├── Analytics
│   ├── Data Analytics (dashboards, rapports)
│   └── Business Intelligence
│
└── Data Science
    ├── ML Engineering
    └── Research
```

---

## Tiers et importance

### Système de Tiers

Les **Tiers** classent les assets par niveau d'importance :

| Tier | Nom | Description | SLA typique |
|------|-----|-------------|-------------|
| **Tier 1** | Mission Critical | Données essentielles au business | 99.9% uptime |
| **Tier 2** | Important | Données utilisées régulièrement | 99% uptime |
| **Tier 3** | Standard | Données d'usage courant | Best effort |
| **Tier 4** | Nice to Have | Données complémentaires | Pas de SLA |
| **Tier 5** | Deprecated | Données en cours de décommission | Migration planifiée |

### Exemples de classification

| Asset | Tier | Justification |
|-------|------|---------------|
| `fact_orders` | Tier 1 | Source de vérité pour le chiffre d'affaires |
| `dim_customers` | Tier 1 | Table dimensionnelle critique |
| `stg_web_events` | Tier 3 | Données de staging intermédiaires |
| `tmp_analysis_q4` | Tier 4 | Analyse ponctuelle |
| `old_customers_v1` | Tier 5 | Ancienne version, à supprimer |

---

## Bonnes pratiques de documentation

### Checklist de documentation

Pour chaque table importante (Tier 1-2) :

- [ ] Description claire de la table (quoi, pourquoi, source)
- [ ] Documentation de chaque colonne
- [ ] Tags de classification (PII, Finance, etc.)
- [ ] Owner assigné (équipe)
- [ ] Tier défini
- [ ] Lineage vérifié
- [ ] Tests de qualité configurés

### Convention de nommage recommandée

```
Préfixes de tables :
├── raw_    → Données brutes (sources)
├── stg_    → Staging (nettoyage léger)
├── int_    → Intermediate (transformations)
├── dim_    → Dimensions (tables de référence)
├── fact_   → Facts (tables de faits)
├── agg_    → Aggregations (pré-calculées)
└── rpt_    → Reports (vues pour reporting)
```

### Template de description

```markdown
## [Nom de la table]

**Objectif** : [Description en une phrase]

**Source** : [D'où viennent les données]
**Fréquence de mise à jour** : [Quotidienne, temps réel, etc.]
**Volumétrie** : [Nombre de lignes approximatif]

### Règles métier
- [Règle 1]
- [Règle 2]

### Points d'attention
- [Limitation ou piège à éviter]
```

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| Recherche | Full-text via Elasticsearch, filtres avancés |
| Documentation | Markdown, au niveau table et colonne |
| Tags | Classification technique (PII, Finance, etc.) |
| Ownership | Toujours assigner une équipe responsable |
| Tiers | Classifier par importance (Tier 1 à 5) |

---

> **Prochain chapitre** : [Lineage](05-lineage.md) - Tracer l'origine et l'impact de vos données
