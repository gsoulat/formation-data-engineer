# Chapitre 1 : Introduction à OpenMetadata

## Table des matières

1. [Qu'est-ce qu'un Data Catalog ?](#quest-ce-quun-data-catalog)
2. [Le problème de la gouvernance des données](#le-problème-de-la-gouvernance-des-données)
3. [OpenMetadata : vue d'ensemble](#openmetadata--vue-densemble)
4. [Architecture](#architecture)
5. [Concepts fondamentaux](#concepts-fondamentaux)
6. [Comparaison avec les alternatives](#comparaison-avec-les-alternatives)
7. [Cas d'usage](#cas-dusage)

---

## Qu'est-ce qu'un Data Catalog ?

Un **data catalog** est un inventaire centralisé de tous les assets de données d'une organisation. Il répond aux questions fondamentales :

- **Où sont mes données ?** → Découverte
- **Que contiennent-elles ?** → Documentation
- **D'où viennent-elles ?** → Lineage
- **Sont-elles fiables ?** → Qualité
- **Qui en est responsable ?** → Ownership
- **Qui peut y accéder ?** → Gouvernance

### Analogie

Pensez à un data catalog comme à la **bibliothèque** de votre organisation :
- Les **livres** sont vos tables, dashboards, pipelines
- Le **catalogue** permet de chercher et trouver ce dont vous avez besoin
- Le **bibliothécaire** (data steward) maintient l'ordre et la qualité
- Les **fiches** décrivent le contenu de chaque livre (métadonnées)

### Pourquoi c'est essentiel ?

Sans data catalog, les organisations font face à :

| Problème | Impact |
|----------|--------|
| Données en silo | Duplication, incohérences |
| Manque de documentation | Temps perdu à chercher/comprendre |
| Pas de lineage | Impossible de mesurer l'impact d'un changement |
| Pas de qualité | Décisions basées sur des données erronées |
| Pas de gouvernance | Risques RGPD, fuite de données sensibles |

---

## Le problème de la gouvernance des données

### Le data swamp

Sans gouvernance, un data lake devient un **data swamp** :

```
Data Lake bien gouverné          Data Swamp
┌──────────────────────┐    ┌──────────────────────┐
│ ✅ Données documentées│    │ ❌ Personne ne sait   │
│ ✅ Lineage tracé      │    │    ce que contient    │
│ ✅ Qualité mesurée    │    │    chaque table       │
│ ✅ Accès contrôlé     │    │ ❌ Données dupliquées │
│ ✅ Ownership clair    │    │ ❌ Qualité inconnue   │
└──────────────────────┘    └──────────────────────┘
```

### Les piliers de la gouvernance

1. **Découvrabilité** : trouver facilement les données pertinentes
2. **Compréhension** : savoir ce que chaque donnée représente
3. **Confiance** : s'assurer de la qualité et de la fraîcheur
4. **Sécurité** : contrôler qui accède à quoi
5. **Conformité** : respecter les réglementations (RGPD, etc.)

---

## OpenMetadata : vue d'ensemble

### Qu'est-ce qu'OpenMetadata ?

**OpenMetadata** est une plateforme open-source (licence Apache 2.0) qui centralise la découverte, la gouvernance et la qualité des métadonnées.

Créée par l'équipe fondatrice d'**Uber's Data Platform** (anciennement Databook), elle a été open-sourcée en 2021.

### Fonctionnalités principales

| Fonctionnalité | Description |
|---------------|-------------|
| **Data Discovery** | Recherche full-text sur tous les assets |
| **Data Lineage** | Traçabilité de bout en bout automatique |
| **Data Quality** | Profiling et tests de qualité natifs |
| **Data Glossary** | Glossaire métier avec termes et relations |
| **Collaboration** | Conversations, tâches, notifications |
| **Data Profiler** | Statistiques automatiques sur les colonnes |
| **Alertes** | Notifications sur changements et anomalies |
| **API-first** | API REST complète + SDK Python |
| **Connecteurs** | 60+ connecteurs natifs |

### Pourquoi OpenMetadata ?

- **Open-source** : pas de vendor lock-in, communauté active
- **API-first** : tout est accessible via API REST
- **Schema-first** : schéma JSON standardisé pour toutes les entités
- **Connecteurs riches** : bases, warehouses, dashboards, pipelines, ML
- **UI moderne** : interface React intuitive et réactive
- **Extensible** : créez vos propres connecteurs et tests

---

## Architecture

### Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────┐
│                    OpenMetadata Platform                       │
│                                                                │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  UI       │  │  API Server  │  │  Ingestion Framework    │ │
│  │  (React)  │──│  (Java/      │──│  (Python)               │ │
│  │           │  │   Dropwizard)│  │                         │ │
│  └──────────┘  └──────┬───────┘  └─────────────────────────┘ │
│                        │                                       │
│                ┌───────┴────────┐                              │
│                │                │                              │
│         ┌──────┴─────┐  ┌──────┴──────┐                      │
│         │  MySQL /    │  │ Elasticsearch│                      │
│         │  PostgreSQL │  │ / OpenSearch │                      │
│         │  (Store)    │  │ (Search)     │                      │
│         └────────────┘  └─────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

### Composants

| Composant | Rôle | Technologie |
|-----------|------|-------------|
| **UI** | Interface utilisateur | React, TypeScript |
| **API Server** | Backend REST | Java, Dropwizard |
| **Ingestion Framework** | Collecte de métadonnées | Python |
| **Store** | Stockage des métadonnées | MySQL ou PostgreSQL |
| **Search** | Moteur de recherche | Elasticsearch / OpenSearch |

### Flux de données

```
1. Les connecteurs Python collectent les métadonnées des sources
2. Les métadonnées sont envoyées à l'API Server
3. L'API Server les stocke dans MySQL/PostgreSQL
4. L'index de recherche est mis à jour dans Elasticsearch
5. L'UI interroge l'API pour afficher les résultats
```

---

## Concepts fondamentaux

### Entités (Entities)

OpenMetadata modélise tout comme des **entités** avec un schéma JSON standardisé :

| Entité | Description | Exemples |
|--------|-------------|----------|
| **Database Service** | Connexion à une source | PostgreSQL, BigQuery |
| **Database** | Base de données | `production_db` |
| **Schema** | Schéma dans une base | `public`, `analytics` |
| **Table** | Table ou vue | `dim_customers` |
| **Column** | Colonne d'une table | `customer_id`, `email` |
| **Dashboard** | Tableau de bord | Dashboard Superset |
| **Pipeline** | Pipeline de données | DAG Airflow |
| **Topic** | Flux de messages | Topic Kafka |
| **ML Model** | Modèle de ML | Modèle MLflow |

### Métadonnées

Chaque entité possède des métadonnées :

```json
{
  "id": "uuid",
  "name": "dim_customers",
  "fullyQualifiedName": "prod.analytics.public.dim_customers",
  "description": "Table dimensionnelle des clients",
  "owner": { "name": "data-team" },
  "tags": ["PII", "Tier1"],
  "columns": [...],
  "lineage": [...],
  "dataQuality": [...]
}
```

### Fully Qualified Name (FQN)

Chaque entité est identifiée de manière unique par son **FQN** :

```
service.database.schema.table.column

Exemple : bigquery_prod.analytics.public.dim_customers.email
```

### Services

Un **service** représente une connexion à un système externe :

```
Services
├── Database Services    → PostgreSQL, MySQL, BigQuery, Snowflake
├── Dashboard Services   → Superset, Metabase, Looker, Power BI
├── Messaging Services   → Kafka, Redpanda, Kinesis
├── Pipeline Services    → Airflow, dbt, Dagster, Prefect
├── ML Model Services    → MLflow, SageMaker
└── Storage Services     → S3, GCS, ADLS
```

---

## Comparaison avec les alternatives

| Critère | OpenMetadata | DataHub (LinkedIn) | Amundsen (Lyft) | Atlan |
|---------|-------------|-------------------|-----------------|-------|
| **Licence** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Propriétaire |
| **Data Quality** | Natif | Via intégration | Non | Natif |
| **Lineage** | Automatique | Automatique | Limité | Automatique |
| **Glossaire** | Oui | Oui | Non | Oui |
| **Collaboration** | Conversations, tâches | Limité | Non | Avancé |
| **API** | REST complète | GraphQL | REST | REST |
| **Connecteurs** | 60+ | 50+ | 20+ | 30+ |
| **UI** | Moderne, intuitive | Fonctionnelle | Basique | Premium |
| **Communauté** | Active, croissante | Très active | En déclin | N/A |
| **Installation** | Simple (Docker) | Complexe | Moyenne | SaaS |

### Quand choisir OpenMetadata ?

- Vous voulez une solution **open-source complète** (catalog + quality + lineage)
- Vous avez besoin d'une **API REST first**
- Vous cherchez une **UI moderne** et intuitive
- Vous voulez du **data quality natif** sans outil supplémentaire
- Vous utilisez un écosystème **diversifié** (multi-cloud, multi-outils)

---

## Cas d'usage

### 1. Découverte de données

> *"En tant que data analyst, je cherche les données de vente par région"*

OpenMetadata permet de rechercher par mots-clés, tags, owners, et de trouver immédiatement les tables, colonnes et dashboards pertinents.

### 2. Analyse d'impact

> *"On veut modifier la colonne `customer_id` dans la table source. Quel est l'impact ?"*

Le lineage montre tous les pipelines, tables dérivées et dashboards impactés.

### 3. Conformité RGPD

> *"Quelles tables contiennent des données personnelles ?"*

Les classifications (PII, PHI) et le glossaire permettent d'identifier et tracer toutes les données sensibles.

### 4. Onboarding

> *"Je suis nouveau dans l'équipe, où sont les données importantes ?"*

Le glossaire métier, la documentation et les tiers permettent de comprendre rapidement le paysage data.

### 5. Data Quality

> *"Comment s'assurer que les données du dashboard financier sont fiables ?"*

Les tests de qualité et le profiling automatique détectent les anomalies avant qu'elles n'impactent les décisions.

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| Data Catalog | Inventaire centralisé de tous vos assets data |
| OpenMetadata | Plateforme open-source, API-first, schema-first |
| Architecture | UI React + API Java + Ingestion Python + MySQL + Elasticsearch |
| Entités | Tables, dashboards, pipelines, topics, ML models |
| FQN | Identifiant unique : `service.database.schema.table` |
| Gouvernance | Découverte + Compréhension + Confiance + Sécurité + Conformité |

---

> **Prochain chapitre** : [Installation et Configuration](02-installation.md) - Mise en place d'OpenMetadata avec Docker Compose
