# Module 07 - Data Lake vs Data Warehouse vs Lakehouse

## Les trois architectures de donnees

```
             Data Warehouse          Data Lake              Lakehouse
             (annees 1990+)          (annees 2010+)         (annees 2020+)
             +--------------+        +--------------+       +--------------+
 Donnees     | Structurees  |        | Toutes       |       | Toutes       |
             | uniquement   |        | (brut)       |       | (gouvernees) |
             +--------------+        +--------------+       +--------------+
 Schema      | On-write     |        | On-read      |       | On-write +   |
             | (avant)      |        | (apres)      |       | enforcement  |
             +--------------+        +--------------+       +--------------+
 Stockage    | Proprietaire |        | Ouvert       |       | Ouvert       |
             | (format DW)  |        | (Parquet/ORC)|       | (Delta/Ice.) |
             +--------------+        +--------------+       +--------------+
 ACID        | Oui          |        | Non (natif)  |       | Oui          |
             +--------------+        +--------------+       +--------------+
 Cout        | Eleve        |        | Faible       |       | Moyen        |
             +--------------+        +--------------+       +--------------+
 Performance | Excellente   |        | Variable     |       | Tres bonne   |
             +--------------+        +--------------+       +--------------+
```

## Data Warehouse : forces et limites

### Forces

| Force | Detail |
|-------|--------|
| **Performance SQL** | Optimise pour les requetes analytiques, index, materialized views |
| **Qualite garantie** | Schema-on-write impose la coherence |
| **ACID natif** | Transactions fiables, pas de donnees corrompues |
| **Maturite** | 30+ ans d'experience, patterns etablis |
| **Gouvernance integree** | Securite, audit, lineage natifs |

### Limites

| Limite | Impact |
|--------|--------|
| **Cout de stockage** | $20-40/To/mois vs $2-5/To pour le stockage objet |
| **Donnees structurees uniquement** | Pas de support natif pour JSON imbrique, images, logs |
| **Rigidite** | Chaque changement de schema necessite une migration |
| **Scalabilite limitee** | Cout prohibitif au-dela de quelques To |
| **Vendor lock-in** | Format proprietaire (Snowflake, Redshift, BigQuery) |

### Cas d'usage ideaux

- Reporting et tableaux de bord (BI)
- KPIs et metriques metier
- Requetes SQL ad-hoc par des analystes
- Donnees structurees et curatees

## Data Lake : forces et limites

### Forces

| Force | Detail |
|-------|--------|
| **Cout tres faible** | Stockage objet : $2-5/To/mois |
| **Tous types de donnees** | Structurees, semi-structurees, non-structurees |
| **Flexibilite** | Schema-on-read, pas de contrainte a l'ingestion |
| **Scalabilite infinie** | Petaoctets sans probleme |
| **Formats ouverts** | Parquet, Avro, ORC : pas de vendor lock-in |
| **ML-friendly** | Acces direct aux donnees brutes pour le ML |

### Limites

| Limite | Impact |
|--------|--------|
| **Pas de transactions ACID** | Ecritures concurrentes = corruption possible |
| **Performance variable** | Sans optimisation, les requetes sont lentes |
| **Risque de Data Swamp** | Sans gouvernance, les donnees deviennent introuvables |
| **Pas de schema enforcement** | Donnees de mauvaise qualite acceptees sans controle |
| **Complexite operationnelle** | Plus d'outils a gerer (Spark, Hive, Presto...) |

### Cas d'usage ideaux

- Stockage brut de toutes les sources (archive)
- Data Science et Machine Learning
- Traitement de donnees non-structurees
- Ingestion massive a faible cout

## Lakehouse : le meilleur des deux mondes

### Qu'est-ce qu'un Lakehouse ?

Le Lakehouse est une architecture qui ajoute les fonctionnalites d'un Data Warehouse **directement sur le Data Lake** grace aux formats de table ouverts (Delta Lake, Iceberg, Hudi).

```
Architecture Lakehouse :

+-------------------------------------------------------------------+
|                    Applications                                   |
|              BI        ML         SQL        APIs                 |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|                   Moteur de requete                               |
|          (Spark SQL, Trino, Athena, Synapse)                     |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|              Table Format (couche transactionnelle)               |
|                  Delta Lake / Iceberg / Hudi                      |
|                                                                   |
|     ACID  |  Time Travel  |  Schema Enforcement  |  Indexing     |
+-------------------------------------------------------------------+
                              |
+-------------------------------------------------------------------+
|                   Stockage objet (Data Lake)                     |
|                    S3 / ADLS Gen2 / GCS                          |
|                      (Fichiers Parquet)                           |
+-------------------------------------------------------------------+
```

### Forces

| Force | Detail |
|-------|--------|
| **ACID sur stockage ouvert** | Transactions fiables sur S3/ADLS/GCS |
| **Cout du Data Lake** | Stockage objet bon marche |
| **Performance du DW** | Indexing, caching, predicate pushdown |
| **Tous types de donnees** | Structurees et non-structurees |
| **Time Travel** | Acces aux versions anterieures des donnees |
| **Schema enforcement** | Qualite garantie comme un DW |
| **Formats ouverts** | Delta/Iceberg : pas de lock-in |
| **BI + ML unifies** | Memes donnees pour les analystes et les data scientists |

### Limites

| Limite | Detail |
|--------|--------|
| **Maturite** | Architecture recente, patterns encore en evolution |
| **Complexite** | Necessite de maitriser Spark, Delta/Iceberg, etc. |
| **Performance vs DW dedie** | Un Snowflake/BigQuery reste plus rapide en pur SQL |
| **Compaction necessaire** | Maintenance des fichiers (OPTIMIZE, VACUUM) |

## Tableau comparatif detaille

| Critere | Data Warehouse | Data Lake | Lakehouse |
|---------|---------------|-----------|-----------|
| **Types de donnees** | Structurees | Toutes | Toutes |
| **Schema** | On-write | On-read | Enforcement + evolution |
| **ACID** | Oui | Non | Oui |
| **Cout stockage** | $$$ | $ | $ |
| **Performance SQL** | Excellente | Variable | Tres bonne |
| **ML/Data Science** | Limite | Excellent | Excellent |
| **Gouvernance** | Native | A construire | Integree (Unity, Purview) |
| **Format** | Proprietaire | Ouvert (Parquet) | Ouvert (Delta/Iceberg) |
| **Time Travel** | Limite | Non | Oui |
| **Scalabilite** | Verticale ($$$) | Horizontale ($) | Horizontale ($) |
| **Utilisateurs cibles** | Analystes BI | Data Engineers/Scientists | Tous |
| **Exemples** | Snowflake, BigQuery, Redshift | S3+Athena, ADLS+Spark | Databricks, Fabric |

## Architectures hybrides courantes

### Pattern 1 : Data Lake + Data Warehouse (classique)

```
Sources --> Data Lake (stockage brut) --> ETL --> Data Warehouse (BI)
                  |
                  +--> ML / Data Science (directement sur le lake)

Exemple :
  S3 (Raw) --> Spark (transform) --> Snowflake (BI)
                     |
                     +--> SageMaker (ML)
```

**Quand :** Organisation avec une equipe BI forte + une equipe Data Science

### Pattern 2 : Lakehouse (unifie)

```
Sources --> Lakehouse (Delta Lake / Iceberg)
                  |
                  +--> SQL (BI, reporting)
                  +--> ML (Data Science)
                  +--> Streaming (temps reel)

Exemple :
  Sources --> Databricks Lakehouse (Delta Lake sur S3/ADLS)
                  |
                  +--> SQL Warehouse (BI)
                  +--> MLflow (ML)
```

**Quand :** Nouvelle architecture, equipe technique, budget maitrise

### Pattern 3 : Data Mesh (decentralise)

```
Domaine A                    Domaine B                    Domaine C
+------------------+        +------------------+        +------------------+
| Data Lake local  |        | Data Lake local  |        | Data Lake local  |
| (equipe Ventes)  |        | (equipe Produit) |        | (equipe Finance) |
+--------+---------+        +--------+---------+        +--------+---------+
         |                           |                           |
         +-----------+---------------+-----------+---------------+
                     |                           |
              +------v------+            +-------v------+
              | Data Products|            | Gouvernance  |
              | (APIs/SQL)  |            | Federee      |
              +-------------+            +--------------+
```

**Quand :** Grande organisation, domaines metier autonomes

## Arbre de decision

```
Quel architecture choisir ?

Quel type de donnees ?
+-- Structurees uniquement
|   +-- Volume < 10 To    --> Data Warehouse
|   +-- Volume > 10 To    --> Lakehouse
|
+-- Structurees + Semi-structurees
|   +-- BI uniquement     --> DW + Data Lake hybride
|   +-- BI + ML           --> Lakehouse
|
+-- Toutes (y compris non-structurees)
    +-- ML/DS primaire    --> Data Lake
    +-- BI + ML           --> Lakehouse

Budget ?
+-- Stockage important, budget serre  --> Data Lake / Lakehouse
+-- Performance critique, budget OK   --> Data Warehouse

Equipe ?
+-- Analystes SQL                     --> Data Warehouse
+-- Data Engineers + Scientists       --> Data Lake / Lakehouse
+-- Mixte                             --> Lakehouse
```

## L'evolution du marche

```
Tendance 2024+ :

Data Warehouse     -->  Ajoute du support Data Lake
(Snowflake)             (Iceberg Tables, External Tables)

Data Lake          -->  Ajoute des fonctionnalites DW
(S3 + Spark)            (Delta Lake, Iceberg, ACID)

                        CONVERGENCE
                            |
                            v
                       Lakehouse
                   (best of both worlds)
```

Les frontieres entre DW et Data Lake s'estompent :
- **Snowflake** supporte Iceberg Tables (format ouvert)
- **BigQuery** supporte BigLake (tables externes gouvernees)
- **Databricks** pousse le Lakehouse avec Delta Lake + SQL Warehouses
- **Microsoft Fabric** unifie DW + Lake dans une seule plateforme

## Points cles a retenir

- Le **Data Warehouse** excelle en BI/SQL mais coute cher et ne supporte que le structure
- Le **Data Lake** stocke tout a faible cout mais manque de gouvernance native
- Le **Lakehouse** combine les forces des deux : ACID + formats ouverts + cout faible
- La **tendance** est a la convergence : tous les acteurs evoluent vers le modele Lakehouse
- Le choix depend du **type de donnees**, du **budget**, de l'**equipe** et des **cas d'usage**
- Les architectures **hybrides** (Lake + DW) restent courantes et valides

---

**Prochain module :** [08 - Anti-patterns et Data Swamp](./08-anti-patterns.md)

[Retour au sommaire](./README.md)
