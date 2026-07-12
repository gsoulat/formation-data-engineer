# 01 — Du fichier plat au modèle en étoile

| | |
|---|---|
| **Durée du module** | ~30 h |
| **Compétences RNCP visées** | **C18** — Modéliser des données structurées (modèle dimensionnel, schéma en étoile) pour alimenter un outil de BI (bloc **BC06** — Analyser des données et concevoir des tableaux de bord) |
| **Prérequis** | Manipulation de tables (Power Query / nettoyage), notions de SQL (jointures, clés) — voir [01-Fondamentaux/SQL](../../01-Fondamentaux/SQL/) —, bases de Power BI (importer des données, vue Rapport) |

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

- Expliquer **pourquoi** on passe d'un fichier plat à un modèle de données structuré.
- Distinguer une **table de faits** d'une **table de dimension**.
- Définir et choisir la **granularité** d'une table de faits.
- Concevoir un **schéma en étoile** (et reconnaître un schéma en flocon).
- Comprendre les **clés primaires / étrangères** et les **relations 1-à-plusieurs**.
- Créer et configurer des **relations dans Power BI** (vue Modèle, cardinalité, sens du filtre).
- Construire une **table de dates** (dimension temps) et l'utiliser comme dimension.
- Appliquer les **bonnes pratiques** de modélisation recommandées pour Power BI.

> 📌 **Pour approfondir la modélisation dimensionnelle côté Data Engineering** (Kimball, SCD, entrepôts de données), voir le module [05-Databases/DataWarehouse](../../05-Databases/DataWarehouse/).

---

## Pourquoi c'est utile au Data Analyst (cœur du BC06)

Quand on débute, on charge souvent **un seul gros fichier Excel/CSV** dans Power BI et on fonce sur les graphiques. Ça marche… jusqu'au jour où :

- le rapport devient **lent** (chaque visuel rescanne des centaines de milliers de lignes redondantes) ;
- les **totaux sont faux** (un même client compté plusieurs fois) ;
- on ne peut pas **filtrer proprement** par mois, par région, par catégorie ;
- ajouter une nouvelle source (objectifs, stocks) **casse tout**.

Le **BC06** demande au Data Analyst de produire des **tableaux de bord fiables et performants**. Or un bon dashboard repose à 80 % sur un **bon modèle de données** en amont. La modélisation, c'est la **fondation invisible** : un visuel mal fichu se corrige en 2 minutes, un modèle mal fichu se traîne sur tout le projet.

Concrètement, maîtriser la modélisation te permet de :

- écrire des **mesures DAX** simples et justes (le DAX adore le schéma en étoile) ;
- garantir que les **filtres se propagent** correctement (sélectionner « Lille » filtre bien les ventes de Lille) ;
- **réutiliser** les mêmes dimensions sur plusieurs tables de faits (ventes ET objectifs partagent la dimension Date) ;
- présenter un livrable **professionnel** et maintenable, attendu par un commanditaire.

> En entretien comme en mission, « Sais-tu construire un schéma en étoile dans Power BI ? » est une question quasi systématique pour un Data Analyst BI.

---

## Du fichier plat au modèle : le problème de départ

Imaginons un export de ventes retail (enseigne du Nord, magasins de Lille, Roubaix, Douai). Une seule table, **une ligne = un article vendu** :

```
Ventes_plat.csv
+------------+------------+----------+-----------+-------------+----------+--------+------+----------+
| Date       | Magasin    | Ville    | Produit   | Catégorie   | Client   | Ville_C| Qté  | Montant  |
+------------+------------+----------+-----------+-------------+----------+--------+------+----------+
| 2025-03-01 | Lille C.   | Lille    | Café 1kg  | Épicerie    | Dupont   | Lille  | 2    | 13.80    |
| 2025-03-01 | Lille C.   | Lille    | Thé vert  | Épicerie    | Martin   | Roubaix| 1    | 4.50     |
| 2025-03-02 | Roubaix    | Roubaix  | Café 1kg  | Épicerie    | Dupont   | Lille  | 1    | 6.90     |
| ...        | ...        | ...      | ...       | ...         | ...      | ...    | ...  | ...      |
+------------+------------+----------+-----------+-------------+----------+--------+------+----------+
```

Problèmes de ce fichier plat :

- **Redondance** : « Lille C. / Lille » et « Café 1kg / Épicerie » sont répétés des milliers de fois → fichier lourd, lent.
- **Risque d'incohérence** : « Lille C. », « Lille Centre », « lille c. » = 3 orthographes pour 1 magasin.
- **Difficile à enrichir** : pour ajouter la surface du magasin ou la catégorie parente, il faut tout réécrire.
- **Mélange des sujets** : qui (client), quoi (produit), où (magasin), quand (date) et combien (qté/montant) sont entassés ensemble.

La solution : **séparer ce qui se mesure** (les faits : quantité, montant) **de ce qui décrit** (les dimensions : produit, magasin, client, date).

---

## Le modèle en étoile (star schema)

Le modèle en étoile organise les données autour d'**une table de faits centrale** reliée à plusieurs **tables de dimensions** par des relations. Vu de haut, ça ressemble à une étoile :

```
                +------------------+
                |   Dim_Produit    |
                | ProduitID (PK)   |
                | Nom, Catégorie   |
                +--------+---------+
                         |
                         | 1
                         | *
+----------------+   +---v------------------+   +----------------+
|   Dim_Date     |   |     Faits_Ventes     |   |  Dim_Magasin   |
| DateID (PK)    |1 *|  DateID     (FK)     |* 1| MagasinID (PK) |
| Jour, Mois,    +---+  ProduitID  (FK)     +---+ Nom, Ville,    |
| Trimestre, An  |   |  MagasinID  (FK)     |   | Surface        |
+----------------+   |  ClientID   (FK)     |   +----------------+
                     |  Quantité            |
                     |  Montant             |
                     +----------^-----------+
                                | *
                                | 1
                        +-------+--------+
                        |   Dim_Client   |
                        | ClientID (PK)  |
                        | Nom, VilleClt  |
                        +----------------+
```

- **Centre = table de faits** (`Faits_Ventes`) : les chiffres qu'on additionne (quantité, montant), plus les **clés étrangères** vers chaque dimension.
- **Branches = dimensions** : le contexte d'analyse (par quel produit ? quel magasin ? quand ? quel client ?).
- Chaque relation est **1-à-plusieurs** : *une* date concerne *plusieurs* lignes de ventes, *un* produit apparaît dans *plusieurs* ventes, etc.

C'est **le modèle recommandé pour Power BI** (cf. la documentation Microsoft).

---

## Table de faits vs tables de dimensions

| | **Table de faits** | **Table de dimension** |
|---|---|---|
| Contient | Des **mesures** numériques additionnables (qté, montant, marge) | Des **attributs** descriptifs (nom, catégorie, ville) |
| Nombre de lignes | **Beaucoup** (transactions) | **Peu** (référentiel) |
| Croît | Vite (chaque vente) | Lentement (nouveau produit/client) |
| Clés | Des **clés étrangères** (FK) + les mesures | Une **clé primaire** (PK) unique |
| Sert à | **Sommer / agréger** | **Filtrer / grouper / étiqueter** |
| Exemple retail | `Faits_Ventes` | `Dim_Produit`, `Dim_Magasin`, `Dim_Date`, `Dim_Client` |

**Astuce mémo** : si la colonne se retrouve sur un **axe de graphique ou dans un slicer** → c'est une **dimension**. Si elle se retrouve dans la **valeur agrégée (Σ)** → c'est un **fait**.

---

## Pour aller plus loin

- Suite du module : [02 — Granularité, clés et flocon](02-granularite-cles-flocon.md)
