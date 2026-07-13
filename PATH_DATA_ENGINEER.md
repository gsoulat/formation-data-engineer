# 🔵 Parcours : Data Engineer Junior

[🏠 Retour à l'accueil](README.md)

Ce parcours est conçu pour vous emmener de la maîtrise du terminal à la mise en production de pipelines de données complexes.

## 📅 Timeline de Formation (6 mois)

> **Rythme** : chaque module s'accompagne d'un **brief à réaliser** (livrable évalué).
> Les briefs sont dans [`99-Brief/`](99-Brief/) : le tronc commun dans
> [`99-Brief/00-Tronc-Commun/`](99-Brief/00-Tronc-Commun/) et les briefs métier dans
> [`99-Brief/Data-Engineer/`](99-Brief/Data-Engineer/). Là où un module n'a pas encore de
> brief, la case est marquée `[brief à créer]`.

### 🟢 Phase 1 : La Forge (Mois 1)
*Objectif : Ne plus avoir peur du terminal et poser les bases du code propre.*
- [ ] [Bash & Zsh](01-Fondamentaux/Bash-Zsh/) : Automatisation CLI.
- [ ] [Git & GitHub](01-Fondamentaux/Git/) : Versionnage et collaboration.
- [ ] [Bonnes Pratiques](01-Fondamentaux/Bonne%20pratique/) : Clean Code et architecture.

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Bash & Zsh** | [Automatisation CLI en Bash/Zsh](99-Brief/00-Tronc-Commun/brief-bash-zsh.md) |
| **Git** | [Versionnage avec Git](99-Brief/00-Tronc-Commun/brief-git.md) |
| **GitHub** | [Collaboration sur GitHub](99-Brief/00-Tronc-Commun/brief-github.md) |
| **Bonnes Pratiques** | `[brief à créer]` |

### 🟡 Phase 2 : L'Artisanat (Mois 2-3)
*Objectif : Manipuler la donnée de manière robuste et isolée.*
- [ ] [Python Avancé](01-Fondamentaux/Python/) : POO et scripts complexes.
- [ ] [SQL Pro](01-Fondamentaux/SQL/) : Requêtes analytiques et optimisation.
- [ ] [Docker](02-Containerisation/Docker/) : Conteneurisation des environnements.

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Python Avancé** | `[brief à créer]` |
| **SQL Pro / Administration BDD** | [Administration PostgreSQL pour une plateforme logistique](99-Brief/Data-Engineer/PostgreSQL-Logistique/README.md) |
| **Python & Collecte (API + Scraping)** | [Veille concurrentielle : pipeline batch API + scraping vers PostgreSQL](99-Brief/Data-Engineer/API-Scraping/BRIEF_API_SCRAPING.md) |
| **Docker** | [Conteneuriser un environnement de données](99-Brief/00-Tronc-Commun/brief-docker.md) |

### 🔴 Phase 3 : L'Architecture (Mois 4-5)
*Objectif : Penser "Pipeline", "Scale" et "Cloud".*
- [ ] [Data Warehouse](05-Databases/DataWarehouse/) : Modélisation (Star Schema).
- [ ] [Data Lake](05-Databases/DataLake/) : Architecture multi-zones, formats (Parquet, Delta), gouvernance.
- [ ] [Spark](06-Data-Engineering/Spark/) : Traitement distribué.
- [ ] [Cloud Platforms (Azure/GCP)](04-Cloud-Platforms/) : Stockage et calcul managé.

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Data Lake** | [Data Lake avec MinIO, Spark et Delta Lake](99-Brief/Data-Engineer/DataLake/BRIEF_DATALAKE.md) |
| **Data Warehouse (Cloud)** | [Pipeline Data Warehouse E-commerce sur BigQuery (Medallion)](99-Brief/Data-Engineer/BigQuery-Medallion/BRIEF_BIGQUERY_MEDALLION.md) |
| **DWH & dbt (Snowflake)** | [Pipeline NYC Taxi avec Snowflake + dbt](99-Brief/Data-Engineer/Snowflake+Dbt/nyc_taxi_dbt_pipeline.md) |
| **Cloud & Lakehouse (Fabric)** | [Pipeline éolien sur Microsoft Fabric](99-Brief/Data-Engineer/Eolienne/Brief_Principal_Introduction.md) |
| **Spark & Analyse énergétique** | [Analyse de la production énergétique française (eCO2mix RTE)](99-Brief/Data-Engineer/ECO2-RTE/BRIEF_ECO2MIX_RTE.md) |

### 🚀 Phase 4 : Mise en Production (Mois 6)
- [ ] [Terraform](03-Infrastructure-as-Code/Terraform/) : Infrastructure as Code.
- [ ] [dbt](06-Data-Engineering/Dbt/) : Transformation SQL, Jinja et macros.
- [ ] [CI/CD](07-DevOps/01-CI-CD/) : Automatisation des tests et déploiements.
- [ ] **Projet Final End-to-End** (Voir ci-dessous).

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Maintenance & exploitation DWH** | [Maintenir et faire évoluer l'entrepôt (SCD, supervision PostgreSQL)](99-Brief/Data-Engineer/Maintenance-Data-Warehouse/BRIEF_MAINTENANCE_DWH.md) |
| **Gouvernance & catalogue** | [Cataloguer et gouverner les données avec OpenMetadata](99-Brief/Data-Engineer/Gouvernance-Donnees/BRIEF_GOUVERNANCE.md) |
| **Streaming temps réel** | [Pipeline de streaming Kafka (ventes flash)](99-Brief/Data-Engineer/Kafka-Streaming/BRIEF_KAFKA_STREAMING.md) |
| **Pipeline Cloud (Azure)** | [Pipeline Azure : qualité de l'eau en France](99-Brief/Data-Engineer/BRIEF_QUALITE_EAU_FRANCE.md) |
| **Pipeline complet (end-to-end)** | [Pipeline Data Engineering NYC Taxi](99-Brief/Data-Engineer/brief-pipeline-data-engineering.md) |
| **Terraform / CI-CD** | `[brief à créer]` |

---

## 🎯 Passeport de Compétences

| Module | Compétence Clé | Livrable attendu |
| :--- | :--- | :--- |
| **Fondamentaux** | Maîtriser l'automatisation CLI | Scripts Bash de nettoyage |
| **Python Data** | Manipuler des volumes via Pandas/Spark | Notebook d'analyse exploratoire |
| **Storage** | Modéliser un entrepôt (Snowflake/BigQuery) | Schéma SQL normalisé |
| **Data Lake** | Construire un Data Lake multi-zones avec Delta Lake | Pipeline Data Lake complet (Brief) |
| **Cloud & IaC** | Déployer une infra reproductible | Code Terraform (Provider Azure/GCP) |

---

## 🎓 Évaluation : Le Projet Final
Pour valider ce parcours, vous devez réaliser le projet suivant :
👉 **[Brief : Pipeline ETL E-Commerce](99-Brief/FINAL_PROJECT_TEMPLATES/DATA_ENGINEER_ETL.md)**

---
[🏠 Retour à l'accueil](README.md)
