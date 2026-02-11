# Module 08 - Anti-patterns et Data Swamp

## Du Data Lake au Data Swamp

Un **Data Swamp** (marecage de donnees) est un Data Lake qui a echoue : les donnees sont inaccessibles, incomprehensibles et inutilisables.

```
Data Lake sain                       Data Swamp
+------------------------------+    +------------------------------+
| Donnees organisees           |    | Fichiers en vrac             |
| Schema documente             |    | "c'est quoi ce fichier ?"    |
| Qualite mesuree              |    | Donnees corrompues/doublons  |
| Acces controle               |    | Tout le monde ecrit partout  |
| Retention definie            |    | Rien n'est supprime          |
| Pipeline fiable              |    | Jobs qui plantent en silence |
| Donnees a jour               |    | Donnees de 2019 obsoletes    |
+------------------------------+    +------------------------------+
       VALEUR                              COUT
```

### Les signaux d'alerte

| Signal | Symptome |
|--------|----------|
| Personne ne sait ce qui existe | "On a un dossier `data_old_v2_final` ?!" |
| Pas de documentation | Aucun schema, aucun README, aucun catalogue |
| Donnees dupliquees partout | La meme table dans 5 dossiers differents |
| Pipelines casses non detectes | Un job a echoue il y a 3 mois, personne n'a vu |
| Couts qui explosent | Stockage qui double chaque trimestre sans valeur ajoutee |
| Personne ne fait confiance aux donnees | "Les chiffres de ce rapport sont faux..." |

## Les 10 anti-patterns du Data Lake

### 1. Le "dump and pray" (deposer et prier)

**Probleme :** Ingerer toutes les donnees sans plan, en esperant qu'elles serviront un jour.

```
ANTI-PATTERN :
Source A  --dump-->  /raw/dump_2024_01_15.csv
Source B  --dump-->  /raw/export_B.json
Source C  --dump-->  /raw/data.parquet
Source D  --dump-->  /raw/truc_machin.csv.gz

Resultat : 500 fichiers, personne ne sait a quoi ils servent
```

**Solution :**
- Definir un **cas d'usage** avant chaque ingestion
- Utiliser une **convention de nommage stricte**
- Documenter chaque source dans le **Data Catalog**

```
BONNE PRATIQUE :
Source A  -->  /raw/ecommerce/orders/date=2024-01-15/orders.parquet
Source B  -->  /raw/crm/contacts/date=2024-01-15/contacts.parquet
+ documentation dans le Data Catalog
+ proprietaire identifie
```

### 2. L'absence de zones (pas de Raw/Curated/Consumption)

**Probleme :** Tout est melange dans un seul dossier, pas de distinction entre donnees brutes et traitees.

```
ANTI-PATTERN :
/data/
+-- orders.csv              <-- brut ou nettoye ?
+-- orders_clean.csv        <-- c'est la derniere version ?
+-- orders_v2.parquet       <-- v2 de quoi ?
+-- orders_final.parquet    <-- "final" comme dans "final_final" ?
+-- orders_FINAL_v3.parquet <-- ...
```

**Solution :**
- Architecture **3 zones** (Raw / Curated / Consumption)
- **Immutabilite** de la zone Raw
- **Pipeline defini** entre chaque zone

### 3. Le probleme des "small files"

**Probleme :** Des milliers de petits fichiers (< 1 Mo) qui degradent les performances.

```
ANTI-PATTERN :
/curated/orders/date=2024-01-15/
+-- part-00001.parquet  (50 Ko)
+-- part-00002.parquet  (50 Ko)
+-- ... (2000 fichiers)
+-- part-02000.parquet  (50 Ko)

Total : 100 Mo en 2000 fichiers
Temps de lecture : 45 secondes (overhead par fichier)

BONNE PRATIQUE :
/curated/orders/date=2024-01-15/
+-- part-00001.parquet  (50 Mo)
+-- part-00002.parquet  (50 Mo)

Total : 100 Mo en 2 fichiers
Temps de lecture : 2 secondes
```

**Solution :**
- **Compaction** reguliere (Delta OPTIMIZE, Iceberg rewrite)
- **Repartition** avant ecriture (`df.repartition(n)`)
- **Buffer** en streaming (flush quand > 128 Mo)

### 4. Le sur-partitionnement

**Probleme :** Partitionner sur une colonne a haute cardinalite cree des millions de dossiers vides ou avec 1 fichier.

```
ANTI-PATTERN :
/curated/orders/
+-- customer_id=C-00001/     (1 fichier, 2 Ko)
+-- customer_id=C-00002/     (1 fichier, 1 Ko)
+-- ... (500 000 dossiers)
+-- customer_id=C-500000/    (1 fichier, 3 Ko)

BONNE PRATIQUE :
/curated/orders/
+-- year=2024/month=01/      (10 fichiers, 500 Mo chacun)
+-- year=2024/month=02/      (10 fichiers, 480 Mo chacun)
```

**Regle :** Partitionner sur des colonnes avec une cardinalite de **100 a 10 000** maximum.

### 5. L'absence de gestion du schema

**Probleme :** Les schemas changent sans avertissement et cassent les pipelines en aval.

```
ANTI-PATTERN :
Jour 1 : {"user_id": 123, "name": "Alice", "email": "a@b.com"}
Jour 2 : {"userId": 123, "name": "Alice", "mail": "a@b.com"}
                ^                                  ^
         Renommage silencieux           Renommage silencieux

--> Pipeline en aval : "Colonne 'user_id' not found" (crash a 3h du matin)
```

**Solution :**
- **Schema enforcement** (Delta Lake, Iceberg)
- **Schema registry** (pour le streaming Kafka)
- **Contrat de donnees** entre producteurs et consommateurs
- **Tests de schema** automatises (dbt tests, Great Expectations)

### 6. L'absence de retention

**Probleme :** Les donnees s'accumulent indefiniment, les couts explosent.

```
ANTI-PATTERN :
/raw/logs/
+-- date=2019-01-01/    (jamais accede depuis 4 ans)
+-- date=2019-01-02/    (jamais accede depuis 4 ans)
+-- ...
+-- date=2024-01-15/    (accede quotidiennement)

Cout : 80% du stockage pour des donnees jamais utilisees
```

**Solution :**
- Definir une **politique de retention** par zone et par source
- Utiliser les **lifecycle policies** du cloud (S3, ADLS, GCS)
- **Archiver** les donnees anciennes (Glacier, Archive tier)
- **Supprimer** les donnees non necessaires (avec validation)

```
Politique de retention exemple :
Zone Raw     : 90 jours en Standard, puis Archive 2 ans, puis suppression
Zone Curated : 1 an en Standard, puis Archive
Zone Consumption : 30 jours (regenerable depuis Curated)
```

### 7. Les pipelines sans monitoring ni alerting

**Probleme :** Un pipeline echoue et personne ne le sait pendant des jours/semaines.

```
ANTI-PATTERN :
Lundi    : Pipeline OK     --> donnees a jour
Mardi    : Pipeline ECHEC  --> ... silence ...
Mercredi : Pipeline ECHEC  --> ... silence ...
Jeudi    : Pipeline ECHEC  --> ... silence ...
Vendredi : "Pourquoi les chiffres n'ont pas bouge depuis lundi ?!"
```

**Solution :**
- **Alertes** sur chaque etape du pipeline (Slack, email, PagerDuty)
- **Monitoring** des metriques : duree, volume, taux d'erreur
- **Quality gates** : si la qualite est insuffisante, le pipeline s'arrete
- **Dashboard operationnel** : vue d'ensemble de tous les pipelines

### 8. Le manque de controle d'acces

**Probleme :** Tout le monde a acces a tout, y compris les donnees sensibles.

```
ANTI-PATTERN :
Stagiaire --> Acces complet a /raw/ (donnees PII non masquees)
Data Scientist --> Peut ecrire dans /consumption/ (ecrase les donnees BI)
Externe --> Acces au bucket S3 entier via cle partagee
```

**Solution :**
- **RBAC** : roles avec permissions minimales
- **Zone-based access** : Raw (data engineers), Curated (analysts), etc.
- **Column-level security** : masquer les colonnes PII
- **Audit des acces** : qui accede a quoi, quand

### 9. Ignorer les formats columnar

**Probleme :** Stocker les donnees en CSV ou JSON dans les zones Curated/Consumption.

```
ANTI-PATTERN :
/curated/orders/orders_clean.csv  (1 Go, pas de types, lent a requeter)

BONNE PRATIQUE :
/curated/orders/year=2024/month=01/part-00000.parquet  (200 Mo, types forts, rapide)

Performance : Parquet est 5-100x plus rapide que CSV pour les requetes analytiques
Cout       : Parquet est 4-7x moins cher a stocker (compression)
```

**Solution :**
- **CSV/JSON** : zone Raw uniquement
- **Parquet** : zone Curated et Consumption
- **Delta/Iceberg** : quand ACID est necessaire

### 10. Le "schema-on-read" pousse a l'extreme

**Probleme :** Utiliser schema-on-read comme excuse pour ne jamais valider les donnees.

```
ANTI-PATTERN :
"On verra le schema plus tard"   --> Plus tard n'arrive jamais
"Pas besoin de valider"          --> Donnees corrompues decouvertes 6 mois apres
"Schema-on-read = pas de schema" --> Mauvaise interpretation du concept
```

**Solution :**
- Schema-on-read pour la **zone Raw** (accepter tout)
- Schema enforcement pour les **zones Curated et Consumption**
- **Contrats de donnees** entre producteurs et consommateurs

## Checklist : Data Lake sain

```
ORGANISATION
[_] Convention de nommage definie et documentee
[_] Architecture 3 zones (Raw/Curated/Consumption)
[_] Zone Raw immutable
[_] Partitionnement adapte (cardinalite moderee)
[_] Fichiers de taille optimale (128 Mo - 1 Go)

GOUVERNANCE
[_] Data Catalog en place et a jour
[_] Proprietaire identifie pour chaque dataset
[_] Politique de retention definie
[_] Lineage trace automatiquement

QUALITE
[_] Tests de qualite automatises (quality gates)
[_] Schema enforcement sur Curated/Consumption
[_] Monitoring et alerting sur les pipelines
[_] Metriques de qualite mesurees et suivies

SECURITE
[_] RBAC avec permissions minimales
[_] Donnees PII identifiees et protegees
[_] Chiffrement au repos et en transit
[_] Audit des acces en place

PERFORMANCE
[_] Format Parquet/Delta/Iceberg pour Curated/Consumption
[_] Compaction reguliere (pas de small files)
[_] Statistiques a jour dans le Data Catalog
[_] Lifecycle policies configurees (archivage auto)
```

## Points cles a retenir

- Un Data Lake devient un **Data Swamp** par manque de discipline, pas par defaut technique
- Les **3 erreurs les plus courantes** : pas de zones, pas de catalogue, pas de qualite
- La **convention de nommage** et les **quality gates** sont les premieres lignes de defense
- Les **formats columnar** (Parquet) et la **compaction** sont indispensables des la zone Curated
- Le **monitoring des pipelines** evite les surprises (donnees manquantes non detectees)
- La gouvernance n'est **pas un luxe** : c'est ce qui rend un Data Lake exploitable

---

[Retour au sommaire](./README.md)
