# Formation OpenMetadata – Data Catalog & Gouvernance

Ce cours vous guidera à travers l'utilisation d'**OpenMetadata**, la plateforme open-source de découverte, gouvernance et qualité des données. Vous apprendrez à centraliser les métadonnées de votre écosystème data, tracer le lineage, mettre en place des tests de qualité et collaborer autour de vos assets de données.

## 🎯 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :
- Comprendre le rôle d'un data catalog dans un écosystème data moderne
- Installer et configurer OpenMetadata (Docker / Kubernetes)
- Connecter vos sources de données (bases, warehouses, pipelines)
- Explorer et documenter vos tables, dashboards et pipelines
- Tracer le lineage de bout en bout
- Mettre en place des tests de qualité des données
- Créer un glossaire métier et classifier vos données
- Collaborer via les conversations, tâches et alertes
- Interagir avec l'API REST et le SDK Python

## 📚 Contenu du cours

### [Chapitre 1 : Introduction à OpenMetadata](01-introduction.md)
- Qu'est-ce qu'un data catalog ?
- Positionnement d'OpenMetadata dans l'écosystème
- Architecture et concepts fondamentaux
- Comparaison avec les alternatives (DataHub, Amundsen, Atlan)

### [Chapitre 2 : Installation et Configuration](02-installation.md)
- Prérequis
- Installation via Docker Compose
- Déploiement Kubernetes (Helm)
- Configuration de l'authentification (SSO, OIDC)
- Premier tour de l'interface

### [Chapitre 3 : Connecteurs et Ingestion](03-connecteurs-ingestion.md)
- Concept d'ingestion de métadonnées
- Connecteurs bases de données (PostgreSQL, MySQL, BigQuery, Snowflake)
- Connecteurs dashboards (Superset, Metabase, Looker, Power BI)
- Connecteurs pipelines (Airflow, dbt, Spark)
- Connecteurs stockage (S3, GCS, ADLS)
- Planification et monitoring des ingestions

### [Chapitre 4 : Découverte et Documentation](04-decouverte-documentation.md)
- Recherche et exploration des assets
- Documentation des tables, colonnes et schémas
- Tags et labels personnalisés
- Ownership et responsabilité des données
- Tiers (importance des assets)

### [Chapitre 5 : Lineage](05-lineage.md)
- Qu'est-ce que le data lineage ?
- Lineage automatique via les connecteurs
- Lineage SQL parsing
- Lineage dbt (models, sources, exposures)
- Lineage manuel et enrichissement
- Analyse d'impact et traçabilité

### [Chapitre 6 : Qualité des Données](06-qualite-donnees.md)
- Profiling des données
- Tests de qualité natifs
- Tests personnalisés (SQL)
- Tableaux de bord de qualité
- Alertes sur les anomalies
- Intégration avec Great Expectations

### [Chapitre 7 : Glossaire Métier et Classification](07-glossaire-classification.md)
- Création d'un glossaire métier
- Termes, synonymes et relations
- Classification et données sensibles (PII, PHI)
- Politiques de gouvernance
- Conformité RGPD et data privacy

### [Chapitre 8 : Collaboration et Alertes](08-collaboration-alertes.md)
- Conversations sur les assets
- Système de tâches et assignation
- Notifications et alertes
- Intégrations (Slack, Teams, email)
- Activity feeds et audit

### [Chapitre 9 : API REST et SDK Python](09-api-sdk.md)
- Architecture de l'API REST
- Authentification et tokens
- CRUD sur les entités (tables, pipelines, dashboards)
- SDK Python `openmetadata-ingestion`
- Automatisation et scripts
- Exemples pratiques

### [Chapitre 10 : Exercices Pratiques](10-exercices.md)
- Exercice 1 : Mise en place d'un data catalog
- Exercice 2 : Ingestion multi-sources
- Exercice 3 : Qualité et lineage
- Exercice 4 : Gouvernance et glossaire
- Exercice 5 : Automatisation via l'API

## 🚀 Prérequis

- Docker et Docker Compose installés
- Connaissances de base en SQL
- Familiarité avec les concepts de data engineering (ETL, data warehouse)
- Python 3.9+ (pour le SDK et les exercices)
- Optionnel : connaissance de dbt, Airflow

## 🛠️ Architecture du cours

```
Sources de données          OpenMetadata              Consommateurs
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│ PostgreSQL       │    │  📖 Data Catalog     │    │ Data Engineers    │
│ BigQuery         │───▶│  🔗 Lineage          │◀──▶│ Data Analysts    │
│ Airflow          │    │  ✅ Data Quality      │    │ Data Scientists  │
│ dbt              │    │  📚 Glossaire         │    │ Data Stewards    │
│ Superset         │    │  🔔 Alertes           │    │ Product Owners   │
└─────────────────┘    └──────────────────────┘    └──────────────────┘
```

## 📁 Ressources

- [Documentation officielle OpenMetadata](https://docs.open-metadata.org/)
- [GitHub OpenMetadata](https://github.com/open-metadata/OpenMetadata)
- [OpenMetadata Slack](https://slack.open-metadata.org/)

---
