# Exemple 02 — Architecture Plateforme Data en C4

## Présentation du système

**Système :** Plateforme data **DataLake360** — une plateforme moderne d'ingestion, de transformation et de visualisation des données d'entreprise.

Ce système illustre une architecture **Lambda** (traitement batch + temps réel) avec une couche de gouvernance des données.

---

## Niveau 1 — Diagramme de Contexte

```plantuml
@startuml DataLake360-Contexte

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title Diagramme de Contexte — Plateforme DataLake360

LAYOUT_WITH_LEGEND()

Person(dataEngineer, "Data Engineer", "Développe et maintient\nles pipelines de données.")

Person(dataAnalyst, "Data Analyst", "Analyse les données,\ncréé des rapports et dashboards.")

Person(dataScientist, "Data Scientist", "Développe des modèles ML\nen accédant aux données brutes et transformées.")

Person(businessUser, "Utilisateur Métier", "Consulte les tableaux de bord\net les rapports opérationnels.")

System(datalake360, "DataLake360", "Plateforme d'ingestion, stockage,\ntransformation et visualisation des données d'entreprise.")

System_Ext(crmSalesforce, "Salesforce CRM", "Données clients, opportunités, contrats.")
System_Ext(erpSAP, "SAP ERP", "Commandes, factures, stocks, comptabilité.")
System_Ext(ecommerceShopify, "Shopify", "Données e-commerce : commandes, produits, clients.")
System_Ext(iotSensors, "Capteurs IoT", "Données industrielles en temps réel\n(température, pression, débit).")
System_Ext(openData, "Open Data (data.gouv.fr)", "Données météo, géographiques,\nstatistiques publiques.")
System_Ext(slackNotif, "Slack", "Alertes et notifications\npour les équipes data.")

Rel(dataEngineer, datalake360, "Développe les pipelines", "HTTPS / SSH")
Rel(dataAnalyst, datalake360, "Analyse et crée des rapports", "HTTPS")
Rel(dataScientist, datalake360, "Accède aux données brutes", "HTTPS / JupyterHub")
Rel(businessUser, datalake360, "Consulte les dashboards", "HTTPS")

Rel(datalake360, crmSalesforce, "Ingère les données CRM", "API REST")
Rel(datalake360, erpSAP, "Ingère les données ERP", "JDBC / API")
Rel(datalake360, ecommerceShopify, "Ingère les ventes e-commerce", "API REST + Webhooks")
Rel(datalake360, iotSensors, "Collecte les mesures IoT", "MQTT / Kafka")
Rel(datalake360, openData, "Importe les données publiques", "HTTP / SFTP")
Rel(datalake360, slackNotif, "Envoie les alertes pipeline", "Webhook HTTPS")

@enduml
```

---

## Niveau 2 — Diagramme de Conteneurs

```plantuml
@startuml DataLake360-Conteneurs

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Diagramme de Conteneurs — DataLake360

LAYOUT_LEFT_RIGHT()
LAYOUT_WITH_LEGEND()

Person(dataEngineer, "Data Engineer", "")
Person(dataAnalyst, "Data Analyst", "")
Person(dataScientist, "Data Scientist", "")
Person(businessUser, "Utilisateur Métier", "")

System_Ext(salesforce, "Salesforce", "CRM")
System_Ext(sap, "SAP ERP", "ERP")
System_Ext(shopify, "Shopify", "E-commerce")
System_Ext(iot, "Capteurs IoT", "IoT")
System_Ext(slack, "Slack", "Notifications")

System_Boundary(dl360, "DataLake360") {

    ' ── Couche Ingestion ─────────────────────────────────

    Container(airflow, "Apache Airflow", "Python, Airflow 2.8", "Orchestration des pipelines\nbatch (CRM, ERP, fichiers).")

    ContainerQueue(kafka, "Apache Kafka", "Kafka 3.6, Kraft Mode", "Ingestion des événements\ntemps réel (IoT, webhooks Shopify).")

    Container(kafkaConnect, "Kafka Connect", "Java, Kafka Connect", "Connecteurs sources/sinks :\nJDBC, S3, Elasticsearch.")

    Container(ingestApi, "Ingestion API", "Python, FastAPI", "API de déclenchement\nmanuel des ingestions.")

    ' ── Couche Stockage ──────────────────────────────────

    ContainerDb(bronze, "Bronze Layer", "MinIO (S3)", "Données brutes sans transformation.\nFormat Parquet ou JSON horodaté.")

    ContainerDb(silver, "Silver Layer", "Delta Lake sur MinIO", "Données nettoyées, déduplicées,\nvalidées. Format Delta.")

    ContainerDb(gold, "Gold Layer", "PostgreSQL DWH", "Tables agrégées, métriques calculées,\nstars schema pour l'analytique.")

    ContainerDb(metastore, "Hive Metastore", "Apache Hive Metastore", "Catalogue des schémas et partitions\nde Bronze et Silver.")

    ' ── Couche Transformation ─────────────────────────────

    Container(dbt, "dbt", "Python, dbt Core 1.7", "Transformations SQL Silver → Gold.\nTests de qualité, documentation.")

    Container(sparkJobs, "Apache Spark", "PySpark 3.5", "Transformations large volume.\nTraitement batch et streaming.")

    ' ── Couche Gouvernance ────────────────────────────────

    Container(dataCatalog, "Data Catalog", "Apache Atlas", "Catalogue des assets data,\nlineage, classification, glossaire.")

    Container(dataQuality, "Data Quality", "Great Expectations", "Tests de qualité des données.\nAlertes sur les anomalies.")

    ' ── Couche Accès ──────────────────────────────────────

    Container(queryEngine, "Query Engine", "Trino (ex-Presto)", "Requêtes SQL fédérées sur\nBronze, Silver, Gold, Kafka.")

    Container(jupyterHub, "JupyterHub", "Python, JupyterHub", "Environnement notebooks\npour les Data Scientists.")

    Container(metabase, "Metabase", "JavaScript", "Dashboards et rapports\npour les utilisateurs métier.")

    Container(dataPortal, "Data Portal", "React, TypeScript", "Interface self-service pour\nexplorer le catalogue et les données.")
}

' Ingestion batch
Rel(airflow, salesforce, "Extrait", "API REST")
Rel(airflow, sap, "Extrait", "JDBC")
Rel(airflow, bronze, "Stocke les données brutes", "S3 API")
Rel(airflow, dbt, "Déclenche les transformations", "CLI")
Rel(airflow, sparkJobs, "Soumet les jobs", "Spark Submit / REST")
Rel(airflow, slack, "Alertes de pipeline", "Webhook")
Rel(airflow, dataQuality, "Lance les checks", "API")

' Ingestion temps réel
Rel(iot, kafka, "Publie les mesures", "MQTT → Kafka")
Rel(shopify, kafka, "Publie les événements", "Webhook → Kafka")
Rel(kafkaConnect, salesforce, "CDC Salesforce", "API")
Rel(kafkaConnect, bronze, "Écrit en Bronze", "S3 Sink Connector")

' Transformations
Rel(sparkJobs, bronze, "Lit les données brutes", "S3 API")
Rel(sparkJobs, silver, "Écrit les données nettoyées", "Delta API")
Rel(dbt, silver, "Lit Silver", "SQL via Trino")
Rel(dbt, gold, "Écrit Gold", "SQL")
Rel(sparkJobs, metastore, "Enregistre les schémas", "Thrift API")

' Gouvernance
Rel(dataCatalog, bronze, "Indexe les métadonnées", "S3 API")
Rel(dataCatalog, silver, "Indexe les métadonnées", "Delta API")
Rel(dataCatalog, gold, "Indexe les métadonnées", "JDBC")
Rel(dataQuality, silver, "Valide les données", "SQL / Delta")

' Accès aux données
Rel(dataEngineer, airflow, "Développe et monitore", "HTTPS")
Rel(dataEngineer, ingestApi, "Déclenche les ingestions", "HTTPS")
Rel(dataScientist, jupyterHub, "Notebooks d'analyse", "HTTPS")
Rel(jupyterHub, queryEngine, "Requêtes SQL", "JDBC")
Rel(queryEngine, bronze, "Requête", "S3 API")
Rel(queryEngine, silver, "Requête", "Delta API")
Rel(queryEngine, gold, "Requête", "JDBC")
Rel(dataAnalyst, metabase, "Dashboards", "HTTPS")
Rel(metabase, gold, "SQL", "JDBC")
Rel(businessUser, metabase, "Consulte", "HTTPS")
Rel(businessUser, dataPortal, "Explore le catalogue", "HTTPS")
Rel(dataPortal, dataCatalog, "Recherche les assets", "API REST")

@enduml
```

---

## Niveau 2 — Vue du flux de données (Dynamic Diagram)

```plantuml
@startuml DataLake360-FluxDonnees

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Dynamic.puml

title Flux de données — Ingestion CRM vers Dashboard

LAYOUT_WITH_LEGEND()

Container(airflow, "Apache Airflow", "Python", "")
System_Ext(salesforce, "Salesforce CRM", "")
ContainerDb(bronze, "Bronze Layer", "S3/Parquet", "")
Container(sparkJobs, "Apache Spark", "PySpark", "")
ContainerDb(silver, "Silver Layer", "Delta Lake", "")
Container(dbt, "dbt", "SQL", "")
ContainerDb(gold, "PostgreSQL DWH", "Gold Layer", "")
Container(dataQuality, "Great Expectations", "", "")
ContainerDb(metabase, "Metabase", "Dashboard", "")
Person(businessUser, "Utilisateur Métier", "")

RelIndex(1, airflow, salesforce, "Extrait les opportunités (API REST)")
RelIndex(2, airflow, bronze, "Stocke en JSON horodaté (S3)")
RelIndex(3, airflow, sparkJobs, "Déclenche le job de nettoyage")
RelIndex(4, sparkJobs, bronze, "Lit les données brutes")
RelIndex(5, sparkJobs, silver, "Écrit les données nettoyées (Delta)")
RelIndex(6, airflow, dataQuality, "Vérifie la qualité des données Silver")
RelIndex(7, airflow, dbt, "Déclenche les modèles Gold")
RelIndex(8, dbt, silver, "Lit les données Silver")
RelIndex(9, dbt, gold, "Écrit les agrégats (PostgreSQL)")
RelIndex(10, businessUser, metabase, "Consulte le dashboard ventes")
RelIndex(11, metabase, gold, "Requête SQL sur le DWH")

@enduml
```

---

## Architecture Medallion expliquée

L'architecture de stockage utilise le **pattern Medallion** (Bronze → Silver → Gold), popularisé par Databricks.

| Couche | Contenu | Transformations | Format |
|--------|---------|----------------|--------|
| **Bronze** | Données brutes, telles que reçues | Aucune — copie exacte de la source | Parquet / JSON horodaté |
| **Silver** | Données nettoyées et validées | Déduplication, normalisation, validation de types | Delta Lake |
| **Gold** | Données agrégées prêtes à l'analyse | Calculs métier, joins, agrégations | PostgreSQL / Delta |

**Avantages :**
- Idempotence : on peut rejouer depuis Bronze sans re-extraire les sources
- Traçabilité : chaque transformation est documentée entre les couches
- Séparation des préoccupations : Ingestion / Qualité / Modélisation sont indépendantes

---

## Observations architecturales

**Pourquoi Kafka + Airflow ?**
Kafka gère le temps réel (IoT, webhooks), Airflow gère le batch (CRM, ERP, fichiers). Les deux sont complémentaires — Kafka Streams ou Spark Structured Streaming traite les événements Kafka en continu pendant qu'Airflow orchestre les jobs planifiés.

**Pourquoi Trino comme Query Engine ?**
Trino permet des requêtes SQL fédérées sur plusieurs sources (S3 Bronze, Delta Silver, PostgreSQL Gold) sans déplacer les données. Un data scientist peut joindre des tables Bronze et Gold dans une seule requête SQL.

**Pourquoi Great Expectations ?**
La qualité des données est un problème critique. Great Expectations permet de définir des contrats de données (expectations) et de les valider automatiquement dans le pipeline Airflow. Si les données Silver ne respectent pas les attentes, le pipeline s'arrête et envoie une alerte Slack.
