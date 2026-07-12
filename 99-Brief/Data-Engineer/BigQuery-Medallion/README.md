# Brief BigQuery Medallion - Pipeline E-commerce

## Description

Ce brief pratique de 2 jours vous permet de construire un Data Warehouse complet sur Google BigQuery en utilisant l'architecture Medallion (Bronze/Silver/Gold).

## Fichiers

```
BigQuery-Medallion/
├── BRIEF_BIGQUERY_MEDALLION.md    # Instructions complètes du brief
├── README.md                       # Ce fichier
└── data/                          # Données sources
    ├── orders.csv                 # 35 commandes
    ├── order_items.csv            # 45 lignes de commande
    ├── customers.csv              # 20 clients
    └── products.csv               # 19 produits
```

## Prérequis

Avant de commencer ce brief, assurez-vous d'avoir :

1. **Suivi les cours préalables :**
   - [Cours Data Warehouse](../../../05-Databases/DataWarehouse/cours/)
   - [Cours GCP BigQuery](../../../04-Cloud-Platforms/GCP/BigQuery/)

2. **Un compte Google Cloud Platform** avec Free Tier

3. **Connaissances requises :**
   - SQL intermédiaire
   - Concepts Data Warehouse (OLAP, dimensions, faits)
   - Architecture Medallion (Bronze/Silver/Gold)

## Durée

- **Jour 1 :** Setup + Bronze + Silver (7h)
- **Jour 2 :** Gold + Automatisation + Documentation (7h)

## Objectifs

A la fin de ce brief, vous aurez :
- Un projet GCP avec 3 datasets (bronze, silver, gold)
- Un pipeline complet Bronze → Silver → Gold
- Des procédures stockées automatisant les transformations
- Un scheduling quotidien du pipeline
- Une documentation complète

## Pour commencer

1. Lisez le fichier [BRIEF_BIGQUERY_MEDALLION.md](./BRIEF_BIGQUERY_MEDALLION.md)
2. Créez votre projet GCP
3. Uploadez les fichiers `data/` vers Cloud Storage
4. Suivez les tâches dans l'ordre

Bon courage !
