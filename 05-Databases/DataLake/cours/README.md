# Formation Data Lake

## Objectifs pedagogiques

A l'issue de cette formation, vous serez capable de :

- **Comprendre** les concepts fondamentaux du Data Lake et son positionnement dans l'ecosysteme data
- **Concevoir** une architecture Data Lake en couches (Raw, Curated, Consumption)
- **Choisir** les formats de stockage adaptes (Parquet, Avro, ORC, Delta) selon le cas d'usage
- **Maitriser** les strategies d'ingestion de donnees (batch, micro-batch, streaming)
- **Implementer** une gouvernance des donnees (catalogage, lineage, qualite, securite)
- **Comparer** les plateformes cloud (S3, ADLS, GCS) et leurs ecosystemes
- **Distinguer** Data Lake, Data Warehouse et Lakehouse pour choisir l'architecture adaptee
- **Identifier** les anti-patterns (Data Swamp) et appliquer les bonnes pratiques

## Prerequis

- Connaissances SQL de base (SELECT, JOIN, GROUP BY)
- Notions de Data Warehouse (recommande : cours 05-Databases/DataWarehouse)
- Comprehension basique du Cloud (S3/Blob Storage)

## Structure du cours

| Module | Titre | Duree |
|--------|-------|-------|
| 01 | [Introduction au Data Lake](./01-introduction.md) | 1h |
| 02 | [Architecture d'un Data Lake](./02-architecture.md) | 1h30 |
| 03 | [Formats de stockage](./03-formats-stockage.md) | 1h |
| 04 | [Ingestion de donnees](./04-ingestion.md) | 1h30 |
| 05 | [Gouvernance et qualite des donnees](./05-gouvernance-qualite.md) | 1h30 |
| 06 | [Technologies et plateformes Cloud](./06-technologies-cloud.md) | 1h |
| 07 | [Data Lake vs Data Warehouse vs Lakehouse](./07-comparaison-architectures.md) | 1h |
| 08 | [Anti-patterns et Data Swamp](./08-anti-patterns.md) | 45min |

**Duree totale cours :** ~9h15

## Planning suggere (semaine type)

```
Jour 1 : Fondamentaux et Architecture (~6h30)
+-- Module 01 - Introduction au Data Lake (1h)
+-- Module 02 - Architecture d'un Data Lake (1h30)
+-- Module 03 - Formats de stockage (1h)
+-- Module 04 - Ingestion de donnees (1h30)
+-- Exercices pratiques formats & ingestion (1h30)

Jour 2 : Gouvernance, Technologies et Comparaison (~6h15)
+-- Module 05 - Gouvernance et qualite (1h30)
+-- Module 06 - Technologies et plateformes Cloud (1h)
+-- Module 07 - Data Lake vs Data Warehouse vs Lakehouse (1h)
+-- Module 08 - Anti-patterns et Data Swamp (45min)
+-- Exercices pratiques architecture Data Lake (2h)
```

## Parcours recommande

```
 CONCEPTS                ARCHITECTURE             STOCKAGE
+-----------+  +-----------+  +---------------+  +---------------+
| Module 01 |->| Module 02 |->|  Module 03    |->|  Module 04    |
|   Intro   |  |   Archi   |  |   Formats     |  |  Ingestion    |
+-----------+  +-----------+  +-------+-------+  +-------+-------+
                                      |                   |
                                      v                   v
                                +-----------+       +-----------+
                                |  TP 1     |       | Module 05 |
                                |  Formats  |       |Gouvernance|
                                +-----+-----+       +-----+-----+
                                      |                   |
                                      +-------+-----------+
                                              v
 TECHNOLOGIES            COMPARAISON            BONNES PRATIQUES
+-----------+  +-----------+  +-----------+  +---------------+
| Module 06 |->| Module 07 |->| Module 08 |  |     Brief     |
| Cloud     |  |Comparaison|  |Anti-pattern|  |   Data Lake   |
+-----------+  +-----------+  +-----------+  +---------------+
```

## Ressources complementaires

- [Cours Data Warehouse](../../DataWarehouse/cours/)
- [Cours Spark](../../../06-Data-Engineering/Spark/)
- [Cours Microsoft Fabric - Lakehouse](../../../06-Data-Engineering/Fabric/02-Lakehouse/)
- [Cours Dbt](../../../06-Data-Engineering/Dbt/)
