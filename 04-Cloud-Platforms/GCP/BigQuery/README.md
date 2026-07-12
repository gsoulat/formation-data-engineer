# Formation Google BigQuery - Data Warehouse Cloud

## Objectifs pédagogiques

A l'issue de cette formation, vous serez capable de :

- **Configurer** un projet GCP et créer des datasets BigQuery
- **Charger** des données depuis Cloud Storage et d'autres sources
- **Implémenter** l'architecture Medallion (Bronze/Silver/Gold) dans BigQuery
- **Automatiser** les transformations avec Stored Procedures et Scheduled Queries
- **Orchestrer** un pipeline complet avec Dataform
- **Optimiser** les coûts et performances de vos requêtes

## Prérequis

- Compte Google Cloud Platform (Free Tier disponible)
- Connaissances SQL de base
- Notions de Data Warehouse (voir [cours générique](../../../05-Databases/DataWarehouse/cours/))

## Free Tier GCP

BigQuery offre un niveau gratuit généreux :

| Ressource | Quota gratuit |
|-----------|---------------|
| Requêtes | 1 TB / mois |
| Stockage | 10 GB / mois |
| Chargement | Gratuit |
| Export | Gratuit |

## Structure du cours

| Module | Titre | Durée |
|--------|-------|-------|
| 01 | [Introduction à BigQuery](./01-introduction.md) | 45min |
| 02 | [Création de projet et datasets](./02-setup.md) | 30min |
| 03 | [Chargement des données](./03-ingestion.md) | 45min |
| 04 | [Architecture Medallion dans BigQuery](./04-medallion.md) | 1h30 |
| 05 | [Automatisation avec Procedures et Schedules](./05-automatisation.md) | 1h |
| 06 | [Orchestration avec Dataform](./06-dataform.md) | 1h |
| 07 | [Optimisation et bonnes pratiques](./07-optimisation.md) | 45min |

**Durée totale :** ~6 heures

## Brief pratique

Après ce cours, mettez en pratique vos connaissances avec le brief :
- [Brief BigQuery Medallion - Pipeline E-commerce](../../../99-Brief/Data-Engineer/BigQuery-Medallion/)

## Architecture cible

```
┌─────────────────────────────────────────────────────────┐
│                    GCP PROJECT                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐                                     │
│  │ Cloud Storage  │─── fichiers CSV/JSON ──┐            │
│  │   (bucket)     │                        │            │
│  └────────────────┘                        ▼            │
│                                    ┌───────────────┐    │
│                                    │   BIGQUERY    │    │
│                                    ├───────────────┤    │
│                                    │               │    │
│                                    │  ┌─────────┐  │    │
│                                    │  │ BRONZE  │  │    │
│                                    │  │ dataset │  │    │
│                                    │  └────┬────┘  │    │
│                                    │       │       │    │
│  ┌────────────────┐                │  ┌────▼────┐  │    │
│  │   Scheduled    │◄──────────────►│  │ SILVER  │  │    │
│  │   Queries      │                │  │ dataset │  │    │
│  └────────────────┘                │  └────┬────┘  │    │
│                                    │       │       │    │
│  ┌────────────────┐                │  ┌────▼────┐  │    │
│  │   Dataform     │◄──────────────►│  │  GOLD   │  │    │
│  │   (optional)   │                │  │ dataset │  │    │
│  └────────────────┘                │  └─────────┘  │    │
│                                    │               │    │
│                                    └───────┬───────┘    │
│                                            │            │
│  ┌────────────────┐                        │            │
│  │  Looker Studio │◄───────────────────────┘            │
│  │  / Data Studio │                                     │
│  └────────────────┘                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Ressources

- [Documentation officielle BigQuery](https://cloud.google.com/bigquery/docs)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [Dataform Documentation](https://cloud.google.com/dataform/docs)
