# Module 03 - Formats de stockage

## Pourquoi le format de stockage est-il si important ?

Dans un Data Lake, le choix du format de fichier impacte directement :
- La **performance** des requetes (x10 a x100 de difference)
- Le **cout** de stockage et de traitement
- La **compatibilite** avec les outils de l'ecosysteme
- L'**evolutivite** du schema

```
Meme donnees, formats differents :

CSV    : 1.0 Go  | Lecture complete obligatoire | Pas de types
JSON   : 1.3 Go  | Lecture complete obligatoire | Schema flexible
Parquet: 0.2 Go  | Lecture colonne par colonne  | Types forts
ORC    : 0.18 Go | Lecture colonne par colonne  | Types forts + index
```

## Formats orientees ligne vs colonne

### Formats orientees ligne (Row-based)

Les donnees sont stockees **ligne par ligne**. Ideal pour les ecritures et lectures de lignes completes.

```
Stockage ligne par ligne :
+-----------+---------+--------+
| Alice     | Paris   | 150.00 |  --> Ligne 1
| Bob       | Lyon    | 89.99  |  --> Ligne 2
| Charlie   | Paris   | 210.00 |  --> Ligne 3
+-----------+---------+--------+

Sur disque : [Alice|Paris|150.00][Bob|Lyon|89.99][Charlie|Paris|210.00]
```

**Avantages :** Ecriture rapide, lecture de lignes completes efficace
**Inconvenients :** Lecture d'une seule colonne = lire toutes les lignes

### Formats orientees colonne (Columnar)

Les donnees sont stockees **colonne par colonne**. Ideal pour l'analytique.

```
Stockage colonne par colonne :
+-----------+---------+--------+
| Alice     | Paris   | 150.00 |
| Bob       | Lyon    | 89.99  |
| Charlie   | Paris   | 210.00 |
+-----------+---------+--------+

Sur disque : [Alice|Bob|Charlie][Paris|Lyon|Paris][150.00|89.99|210.00]
                  Col 1              Col 2              Col 3
```

**Avantages :** Ne lit que les colonnes necessaires, meilleure compression
**Inconvenients :** Ecriture plus lente, lecture de lignes completes moins efficace

### Comparaison pour une requete typique

```sql
SELECT AVG(amount) FROM orders WHERE city = 'Paris';
```

```
Format LIGNE (CSV) :                    Format COLONNE (Parquet) :
Doit lire TOUTES les colonnes           Ne lit que 'city' et 'amount'

[Alice|Paris|150.00]  <-- lu            [Paris|Lyon|Paris]  <-- lu (city)
[Bob|Lyon|89.99]      <-- lu            [150.00|89.99|210.00] <-- lu (amount)
[Charlie|Paris|210.00]<-- lu            [Alice|Bob|Charlie] <-- PAS lu (name)

Donnees lues : 100%                     Donnees lues : ~66%
(avec 50 colonnes : toujours 100%)      (avec 50 colonnes : ~4%)
```

## Les formats en detail

### CSV (Comma-Separated Values)

```
name,city,amount,order_date
Alice,Paris,150.00,2024-01-15
Bob,Lyon,89.99,2024-01-16
```

| Critere | Valeur |
|---------|--------|
| Type | Ligne |
| Compression | Faible (texte brut) |
| Schema | Aucun (tout est string) |
| Lisibilite humaine | Excellente |
| Ecosysteme | Universel |
| Usage Data Lake | Zone Raw uniquement |

**Quand l'utiliser :** Import/export, zone Raw, donnees legacy

### JSON / JSON Lines (NDJSON)

```json
{"name": "Alice", "city": "Paris", "amount": 150.00, "tags": ["vip", "paris"]}
{"name": "Bob", "city": "Lyon", "amount": 89.99, "tags": ["standard"]}
```

| Critere | Valeur |
|---------|--------|
| Type | Ligne |
| Compression | Moyenne (cles repetees) |
| Schema | Semi-structure, flexible |
| Lisibilite humaine | Bonne |
| Structures imbriquees | Oui (arrays, nested objects) |
| Usage Data Lake | Zone Raw (APIs, logs, IoT) |

**Quand l'utiliser :** Donnees d'APIs, logs applicatifs, donnees semi-structurees

### Apache Avro

Format **binaire, oriente ligne** avec le schema embarque.

```
+------------------+--------------------+
|  Schema (JSON)   |   Donnees (binaire)|
+------------------+--------------------+
```

| Critere | Valeur |
|---------|--------|
| Type | Ligne (binaire) |
| Compression | Bonne |
| Schema | Embarque dans le fichier |
| Evolution du schema | Excellente (backward/forward compatible) |
| Serialisation | Tres rapide |
| Usage Data Lake | Streaming, schemas evolutifs |

**Quand l'utiliser :** Kafka (messages), ingestion streaming, schemas qui evoluent souvent

### Apache Parquet

Format **binaire, oriente colonne**. C'est le **standard de facto** des Data Lakes modernes.

```
Fichier Parquet :
+-----------------------------------+
| Header                            |
+-----------------------------------+
| Row Group 1                       |
|   +-- Column Chunk: name          |
|   |   +-- Page 1 (compressed)     |
|   +-- Column Chunk: city          |
|   |   +-- Page 1 (compressed)     |
|   +-- Column Chunk: amount        |
|       +-- Page 1 (compressed)     |
+-----------------------------------+
| Row Group 2                       |
|   +-- Column Chunk: name          |
|   +-- Column Chunk: city          |
|   +-- Column Chunk: amount        |
+-----------------------------------+
| Footer (schema + statistiques)    |
|   - min/max par colonne           |
|   - nombre de lignes              |
|   - encodage utilise              |
+-----------------------------------+
```

| Critere | Valeur |
|---------|--------|
| Type | Colonne (binaire) |
| Compression | Excellente (Snappy, Zstd, Gzip) |
| Schema | Embarque dans le footer |
| Predicate pushdown | Oui (grace aux stats min/max) |
| Structures imbriquees | Oui (Dremel encoding) |
| Usage Data Lake | Standard pour zones Curated et Consumption |

**Quand l'utiliser :** Zone Curated, zone Consumption, analytique, tout usage principal

### Apache ORC (Optimized Row Columnar)

Format **binaire, oriente colonne**, optimise pour l'ecosysteme Hive/Hadoop.

| Critere | Valeur |
|---------|--------|
| Type | Colonne (binaire) |
| Compression | Excellente (Zlib, Snappy, LZO) |
| Index integre | Oui (Bloom filters, statistiques avancees) |
| Predicate pushdown | Oui (plus avance que Parquet) |
| ACID natif | Oui (avec Hive ACID) |
| Usage Data Lake | Ecosysteme Hive/Hadoop |

**Quand l'utiliser :** Ecosysteme Hadoop/Hive, besoin d'index integres

## Tableau comparatif complet

```
              CSV      JSON     Avro     Parquet   ORC
              -------  -------  -------  --------  --------
Orientation   Ligne    Ligne    Ligne    Colonne   Colonne
Compression   Faible   Faible   Bonne    Excell.   Excell.
Schema        Non      Semi     Oui      Oui       Oui
Lisibilite    +++      ++       -        -         -
Ecriture      +++      ++       +++      ++        ++
Lecture ana.  -        -        +        +++       +++
Imbrication   Non      Oui      Oui      Oui       Oui
Ecosysteme    Univ.    Univ.    Kafka    Spark/DL  Hive
Taille (ref)  1x       1.3x     0.3x     0.2x      0.18x
```

## Compression

### Algorithmes de compression

| Algorithme | Ratio | Vitesse | Usage |
|------------|-------|---------|-------|
| **Snappy** | Moyen | Tres rapide | Default Parquet/Spark, bon compromis |
| **Zstd** | Bon | Rapide | Recommande pour le stockage long terme |
| **Gzip** | Bon | Lent | Compatible partout, archivage |
| **LZ4** | Moyen | Tres rapide | Temps reel, faible latence |
| **Brotli** | Excellent | Lent | Archivage, compression maximale |

### Impact concret de la compression

```
Donnees brutes (CSV) :     1.0 Go

Avec Snappy (Parquet) :    0.22 Go  (compression 4.5x)
Avec Zstd (Parquet) :      0.15 Go  (compression 6.7x)
Avec Gzip (Parquet) :      0.14 Go  (compression 7.1x)

Cout S3 mensuel (1 To de CSV) :
  CSV non compresse :   $23.00 / mois
  Parquet + Snappy :     $5.11 / mois   (-78%)
  Parquet + Zstd :       $3.43 / mois   (-85%)
```

## Formats de table ouverts (Table Formats)

Les formats de table ouverts ajoutent une **couche de gestion** au-dessus des fichiers Parquet/ORC, apportant des fonctionnalites de type base de donnees.

### Delta Lake

```
Structure Delta Lake :
/delta_table/
+-- _delta_log/                   <-- Transaction log (JSON)
|   +-- 00000000000000000000.json
|   +-- 00000000000000000001.json
|   +-- 00000000000000000002.json
+-- part-00000-xxx.parquet        <-- Fichiers de donnees
+-- part-00001-xxx.parquet
+-- part-00002-xxx.parquet
```

**Fonctionnalites :**
- Transactions ACID
- Time Travel (requetes sur des versions anterieures)
- Schema enforcement et evolution
- MERGE / UPSERT / DELETE
- Audit history

```sql
-- Time Travel : lire les donnees d'il y a 3 versions
SELECT * FROM my_table VERSION AS OF 3;

-- Time Travel : lire les donnees a un timestamp
SELECT * FROM my_table TIMESTAMP AS OF '2024-01-15 10:00:00';
```

### Apache Iceberg

```
Structure Iceberg :
/iceberg_table/
+-- metadata/
|   +-- v1.metadata.json          <-- Metadata (schema, partitions)
|   +-- snap-xxx-1.avro           <-- Snapshot (liste de manifests)
|   +-- manifest-xxx.avro         <-- Manifest (liste de fichiers)
+-- data/
    +-- partition=A/
    |   +-- file1.parquet
    +-- partition=B/
        +-- file2.parquet
```

**Fonctionnalites :**
- Transactions ACID
- Hidden partitioning (partition transparente)
- Schema evolution (ajout, renommage, suppression de colonnes)
- Partition evolution (changer le partitionnement sans reecrire)
- Time Travel

### Apache Hudi

**Fonctionnalites :**
- Upserts efficaces (Copy-on-Write et Merge-on-Read)
- Incremental queries (ne lire que les nouveaux changements)
- Compaction automatique
- Rollback

### Comparaison des Table Formats

| Fonctionnalite | Delta Lake | Iceberg | Hudi |
|----------------|-----------|---------|------|
| ACID | Oui | Oui | Oui |
| Time Travel | Oui | Oui | Oui |
| Schema Evolution | Oui | Excellente | Oui |
| Partition Evolution | Non | Oui | Non |
| Hidden Partitioning | Non | Oui | Non |
| Upserts | Oui | Oui | Excellent |
| Incremental Read | Oui | Oui | Excellent |
| Ecosysteme | Databricks | Multi-cloud | AWS (EMR) |
| Adoption | Tres large | En forte croissance | Moderee |

## Guide de choix du format

```
Quel format choisir ?

Donnees en entree (Raw) ?
+-- Depuis une API/logs  --> JSON / Avro
+-- Depuis un SGBD       --> CSV / Parquet
+-- Streaming (Kafka)    --> Avro
+-- Fichiers legacy      --> CSV (tel quel)

Zone Curated / Consumption ?
+-- Standard             --> Parquet
+-- Besoin ACID          --> Delta Lake / Iceberg
+-- Ecosysteme Hive      --> ORC
+-- Schema qui evolue    --> Iceberg
+-- Upserts frequents    --> Hudi / Delta Lake
```

## Points cles a retenir

- Les formats **colonne** (Parquet, ORC) sont le standard pour l'analytique : x5-10 plus rapides
- **Parquet** est le format de facto des Data Lakes modernes
- La **compression** (Snappy, Zstd) reduit les couts de 78-85%
- Les **Table Formats** (Delta, Iceberg, Hudi) ajoutent ACID et Time Travel sur le Data Lake
- **Iceberg** se distingue par la partition evolution et le hidden partitioning
- Le choix du format depend de la **zone** (Raw vs Curated) et du **cas d'usage**

---

**Prochain module :** [04 - Ingestion de donnees](./04-ingestion.md)

[Retour au sommaire](./README.md)
