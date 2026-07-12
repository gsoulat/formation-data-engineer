# Formation Data Warehouse

![Synthèse Data Warehouse](../synthese.png)

## Objectifs pédagogiques

A l'issue de cette formation, vous serez capable de :

- **Comprendre** les concepts fondamentaux du Data Warehouse
- **Distinguer** les systèmes OLTP des systèmes OLAP
- **Modéliser** des données selon l'approche dimensionnelle (Star Schema, Snowflake, SCD, Factless Facts)
- **Concevoir** une architecture de données décisionnelle (Kimball vs Inmon, Data Vault, Data Mesh)
- **Maîtriser** les opérations OLAP (slice, dice, roll-up, drill-down, pivot)
- **Écrire** des requêtes SQL OLAP avancées (ROLLUP, CUBE, window functions)
- **Comparer** les approches ROLAP, MOLAP et HOLAP
- **Choisir** la technologie adaptée à votre contexte (PostgreSQL, Snowflake, BigQuery)
- **Implémenter** l'architecture Medallion (Bronze/Silver/Gold) avec Data Quality et gouvernance

## Prérequis

- Connaissances SQL de base (SELECT, JOIN, GROUP BY)
- Notions de modélisation de données
- Compréhension basique du Cloud

## Structure du cours

| Module | Titre | Durée |
|--------|-------|-------|
| 01 | [Introduction au Data Warehouse](./01-introduction.md) | 1h |
| 02 | [OLTP vs OLAP](./02-oltp-vs-olap.md) | 45min |
| 03a | [Modélisation dimensionnelle : fondamentaux](./03a-modelisation-fondamentaux.md) | 1h |
| 03b | [Modélisation avancée : SCD, Factless Facts, Data Vault](./03b-modelisation-avancee.md) | 45min |
| 04 | [Architectures et Patterns](./04-architectures.md) | 1h30 |
| 05 | [Opérations OLAP & ROLAP/MOLAP/HOLAP](./05-operations-olap.md) | 1h30 |
| 06 | [Technologies Cloud](./06-technologies-cloud.md) | 1h |
| 07 | [PostgreSQL vs BigQuery](./07-postgresql-vs-bigquery.md) | 45min |
| 08 | [Architecture Medallion](./08-medallion.md) | 1h |

**Durée totale cours :** ~9 heures

> **Note :** L'ancien module 03 unique a été scindé en 03a (fondamentaux) et 03b (avancé) pour faciliter l'apprentissage progressif. L'ancien fichier [03-modelisation.md](./03-modelisation.md) reste disponible comme référence complète.

## Notebook interactif

Pour pratiquer les opérations OLAP sans installer PostgreSQL :

| Ressource | Description |
|-----------|-------------|
| [Notebook OLAP interactif](./notebook-olap-interactif.ipynb) | Pratiquez ROLLUP, CUBE, GROUPING SETS et Window Functions directement dans Jupyter avec DuckDB |

Le notebook fonctionne avec DuckDB (installé automatiquement), aucune configuration serveur nécessaire.

## Exercices pratiques

| Exercice | Titre | Durée | Prérequis |
|----------|-------|-------|-----------|
| TD | [Conception conceptuelle d'un DW](../exercices/TD-conception-conceptuelle.md) | 2h30 | Modules 01, 03a |
| TP 1 | [Conception logique ROLAP](../exercices/TP-conception-logique-rolap.md) | 2h | TD + Module 05 |
| TP 2 | [SQL OLAP PostgreSQL](../exercices/TP-sql-olap-postgresql.md) | 3h | TP 1 + Module 05 |
| TP 3 | [PostgreSQL vers BigQuery](../exercices/TP-postgresql-vers-bigquery.md) | 1h | Module 07 |

**Durée totale exercices :** ~8h30

## Planning suggéré (semaine type)

```
Jour 1 : Fondamentaux et Modélisation (~6h)
├── Module 01 - Introduction au Data Warehouse (1h)
├── Module 02 - OLTP vs OLAP (45min)
├── Module 03a - Modélisation : fondamentaux (1h)
├── Module 03b - Modélisation : avancée (45min)
└── TD : Conception conceptuelle d'un DW (2h30)

Jour 2 : Architectures et Pratique OLAP (~7h)
├── Module 04 - Architectures et Patterns (1h30)
├── Module 05 - Opérations OLAP & ROLAP/MOLAP/HOLAP (1h30)
├── 📓 Notebook OLAP interactif (30min, optionnel)
├── TP 1 : Conception logique ROLAP (2h)
└── TP 2 : SQL OLAP PostgreSQL (début - 2h)

Jour 3 : SQL OLAP et Technologies (~7h)
├── TP 2 : SQL OLAP PostgreSQL (fin - 1h)
├── Module 06 - Technologies Cloud (1h)
├── Module 07 - PostgreSQL vs BigQuery (45min)
├── TP 3 : PostgreSQL vers BigQuery (1h)
├── Module 08 - Architecture Medallion (1h)
└── Démarrer le Brief BigQuery Medallion (2h15)

Jours 4-5 : Brief pratique
└── Brief BigQuery Medallion (suite et fin)
```

## Parcours recommandé

```
 CONCEPTS                MODÉLISATION             ARCHITECTURES
┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐
│Module 01 │─►│Module 02 │─►│ Module 03a   │─►│  Module 04   │
│  Intro   │  │OLTP/OLAP │  │Star/Snowflake│  │Inmon/Kimball │
└──────────┘  └──────────┘  └──────┬───────┘  └──────┬───────┘
                                   │                  │
                                   ▼                  │
                             ┌──────────────┐         │
                             │ Module 03b   │         │
                             │SCD/DataVault │         │
                             └──────┬───────┘         │
                                    │                 │
                                    ▼                 ▼
                             ┌──────────┐       ┌──────────┐
                             │    TD    │       │Module 05 │
                             │Conception│       │Opér. OLAP│
                             └────┬─────┘       └────┬─────┘
                                  │    📓 Notebook    │
                                  │    OLAP (opt.)    │
                                  └──────┬────────────┘
                                         ▼
                                  ┌──────────┐  ┌──────────┐
                                  │   TP 1   │─►│   TP 2   │
                                  │  ROLAP   │  │ SQL OLAP │
                                  └──────────┘  └──────────┘

 TECHNOLOGIES            PRATIQUE                 MODERNE
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│Module 06 │─►│Module 07 │─►│   TP 3   │  │  Module 08   │
│Cloud DW  │  │PG vs BQ  │  │Migration │  │  Medallion   │
└──────────┘  └──────────┘  └──────────┘  └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │    Brief     │
                                           │BigQuery Medal│
                                           └──────────────┘
```

## Ressources complémentaires

- [Brief pratique BigQuery Medallion](../../../99-Brief/Data-Engineer/BigQuery-Medallion/)
- [Cours BigQuery](../../../04-Cloud-Platforms/GCP/BigQuery/cours/)
- [Cours Snowflake](../../../04-Cloud-Platforms/snowflake/)
- [Cours Microsoft Fabric](../../../06-Data-Engineering/Fabric/)
