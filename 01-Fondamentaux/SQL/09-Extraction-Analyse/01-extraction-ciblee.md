# 01 - Extraction ciblée pour l'analyse

[🏠 Accueil](../README.md) | [📂 Module 09](README.md) | [02 - SQL avancé pour l'analyse →](02-sql-avance-analyse.md)

---

| | |
|---|---|
| **Durée indicative** | ~25 heures (pratique incluse) |
| **Objectif** | Requêter une base de données relationnelle pour extraire les données nécessaires à une analyse |
| **Prérequis** | [Module 01 (SELECT, WHERE)](../01-Introduction-Select/README.md), [Module 02 (Agrégations)](../02-Agregations-Groupby/README.md), [Module 03 (Jointures)](../03-Jointures/README.md) |
| **Outils** | DB Browser for SQLite (ou PostgreSQL/DuckDB) + le jeu de données « Ventes Retail Nord » |

---

## 1. Objectifs

À la fin de ce chapitre, tu seras capable de :

- Expliquer ce qu'est une **base de données relationnelle** (tables, colonnes, lignes, clés primaires et étrangères).
- Traduire une **demande métier** en requête SQL : filtres (`WHERE`), tri (`ORDER BY`), Top N (`LIMIT`), dédoublonnage (`DISTINCT`).
- Produire des **indicateurs** avec les agrégations (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`), `GROUP BY` et `HAVING`.
- **Croiser plusieurs tables** avec `INNER JOIN` et `LEFT JOIN` pour répondre à une question d'analyse.
- Utiliser des **alias** pour rendre tes requêtes lisibles.

> Ces gestes correspondent à ce qu'on attend d'un data analyst débutant : **aller chercher la bonne donnée, au bon endroit, et la mettre en forme pour l'analyse.**

> 📖 **La syntaxe détaillée de chaque clause est couverte dans les modules précédents** ([SELECT/WHERE](../01-Introduction-Select/README.md), [Agrégations](../02-Agregations-Groupby/README.md), [Jointures](../03-Jointures/README.md)). Ici, on se concentre sur **l'angle analyse** : les demandes métier, les résultats attendus et les pièges qui faussent une analyse.

---

## 2. Pourquoi le SQL est LA compétence n°1 du data analyst

Si tu ne devais apprendre **qu'une seule** compétence technique pour devenir data analyst, ce serait le SQL. Voici pourquoi.

- **~95 % des offres d'emploi data analyst exigent SQL.** Avant Python, avant Power BI, avant Excel avancé : SQL est dans presque toutes les fiches de poste. C'est le dénominateur commun du métier.
- **Les données vivent dans des bases de données.** Dans une entreprise, les ventes, les clients, les stocks, les commandes ne sont pas dans un fichier Excel : ils sont stockés dans une base de données relationnelle (PostgreSQL, MySQL, SQL Server, BigQuery, Snowflake…). Pour les analyser, il faut savoir **les en extraire**, et la langue de l'extraction, c'est SQL.
- **C'est la première étape de TOUTE analyse.** Avant de faire un graphique, un tableau de bord ou un modèle, tu dois d'abord récupérer les bonnes données. Un dashboard Power BI ou Tableau s'alimente très souvent par une requête SQL.
- **SQL est stable et universel.** Le langage existe depuis les années 1970 et n'a presque pas changé. Ce que tu apprends aujourd'hui te servira toute ta carrière, quel que soit l'outil ou l'éditeur de base de données.
- **C'est lisible, presque de l'anglais.** `SELECT nom FROM clients WHERE ville = 'Lille'` se lit « sélectionne le nom depuis les clients où la ville est Lille ». La barrière d'entrée est faible.

> **En résumé :** maîtriser SQL, c'est devenir **autonome sur la donnée**. Tu n'attends plus que quelqu'un t'envoie un export : tu vas chercher toi-même exactement ce dont tu as besoin.

---

## 3. Le schéma de données : « Ventes Retail Nord »

Tout au long du chapitre, on travaille sur une chaîne fictive de magasins de la région **Hauts-de-France** (Lille, Roubaix, Dunkerque, Valenciennes…). Quatre tables :

### Table `clients`
| Colonne | Type | Description |
|---|---|---|
| `client_id` 🔑 | INTEGER | Identifiant unique du client (clé primaire) |
| `nom` | TEXT | Nom de famille |
| `prenom` | TEXT | Prénom |
| `ville` | TEXT | Ville de résidence |
| `code_postal` | TEXT | Code postal |
| `date_inscription` | DATE | Date de création du compte fidélité |

### Table `produits`
| Colonne | Type | Description |
|---|---|---|
| `produit_id` 🔑 | INTEGER | Identifiant unique du produit |
| `nom_produit` | TEXT | Libellé du produit |
| `categorie` | TEXT | Catégorie (Épicerie, Boisson, Hygiène…) |
| `prix_unitaire` | REAL | Prix de vente unitaire en € |

### Table `magasins`
| Colonne | Type | Description |
|---|---|---|
| `magasin_id` 🔑 | INTEGER | Identifiant unique du magasin |
| `nom_magasin` | TEXT | Nom du magasin |
| `ville` | TEXT | Ville du magasin |

### Table `commandes`
| Colonne | Type | Description |
|---|---|---|
| `commande_id` 🔑 | INTEGER | Identifiant unique de la commande |
| `client_id` 🔗 | INTEGER | Clé étrangère → `clients.client_id` |
| `produit_id` 🔗 | INTEGER | Clé étrangère → `produits.produit_id` |
| `magasin_id` 🔗 | INTEGER | Clé étrangère → `magasins.magasin_id` |
| `quantite` | INTEGER | Nombre d'unités achetées |
| `date_commande` | DATE | Date de la commande |

**Comment lire ce schéma :** la table `commandes` est la table centrale. Chaque commande pointe vers **un** client, **un** produit et **un** magasin via les colonnes `client_id`, `produit_id`, `magasin_id`. Ce sont les **clés étrangères** (🔗) : elles font le lien entre les tables. C'est ça, le côté « relationnel » d'une base de données relationnelle.

Pourquoi séparer en plusieurs tables au lieu d'un seul grand tableau ? Pour **éviter de répéter l'information**. On écrit l'adresse d'un client **une seule fois** dans `clients`, et toutes ses commandes y font référence par son `client_id`. C'est plus propre, plus léger, et ça évite les incohérences.

> 💡 **Image mentale :** une base relationnelle, c'est un classeur Excel **bien rangé**, où chaque onglet a un rôle précis et où les onglets sont reliés par des numéros d'identification.

---

## 4. De la demande métier à la requête

Chaque section reprend une notion sous l'angle « analyse » : la demande métier type, une requête modèle avec son résultat, et les pièges qui faussent les chiffres.

### 4.1 Lire et filtrer — `SELECT`, `FROM`, `WHERE`

> 📖 Syntaxe complète : [SELECT](../01-Introduction-Select/01-introduction-select.md) et [WHERE](../01-Introduction-Select/02-filtrage-where.md).

> **Demande métier :** « Donne-moi tous les clients du littoral (Dunkerque, Calais, Boulogne) inscrits cette année. »

```sql
SELECT prenom, nom, ville, date_inscription
FROM clients
WHERE ville IN ('Dunkerque', 'Calais', 'Boulogne')
  AND date_inscription >= '2026-01-01';
```

Autre classique, la recherche de motif :

```sql
-- Clients dont le nom commence par 'Le'
SELECT nom, prenom
FROM clients
WHERE nom LIKE 'Le%';
```

**Résultat attendu :**

| nom | prenom |
|---|---|
| Lefebvre | Sophie |
| Leroy | Antoine |

> ⚠️ **Erreurs courantes qui faussent une extraction**
> - **Les guillemets** : les chaînes de texte s'entourent de **guillemets simples** : `'Lille'`, pas `"Lille"` ni `Lille`.
> - **`=` vs `==`** : en SQL, l'égalité s'écrit avec **un seul** `=`.
> - **`BETWEEN` inclut les bornes** : `BETWEEN 1 AND 3` garde aussi 1 et 3 — important quand on découpe des périodes.
> - **`AND` est prioritaire sur `OR`.** En cas de doute, mets des **parenthèses** : `WHERE (ville = 'Lille' OR ville = 'Roubaix') AND prix_unitaire > 5`. Sans elles, ton périmètre d'analyse n'est pas celui que tu crois.
> - **`SELECT *` partout** : pratique pour explorer, mais pour alimenter un dashboard on précise les colonnes utiles (plus rapide, plus clair).

### 4.2 Classer et dédoublonner — `ORDER BY`, `LIMIT`, `DISTINCT`

> 📖 Syntaxe complète : [Tri et Limitation](../01-Introduction-Select/03-tri-limites.md).

> **Demande métier :** « Quels sont nos 3 produits les plus chers ? » — la base de tout classement (« Top N ») dans un tableau de bord.

```sql
SELECT nom_produit, prix_unitaire
FROM produits
ORDER BY prix_unitaire DESC
LIMIT 3;
```

**Résultat attendu :**

| nom_produit | prix_unitaire |
|---|---|
| Café en grains 1kg | 12.50 |
| Lessive 3L | 9.90 |
| Huile d'olive 1L | 8.40 |

`DISTINCT` supprime les doublons — utile pour lister les valeurs possibles d'une dimension :

```sql
-- La liste des villes distinctes où l'on a des clients
SELECT DISTINCT ville
FROM clients;
```

**Résultat attendu :**

| ville |
|---|
| Lille |
| Roubaix |
| Dunkerque |
| Valenciennes |

> ⚠️ **Erreurs courantes**
> - **L'ordre des clauses est imposé :** `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`. Mettre `ORDER BY` avant `WHERE` = erreur.
> - **`DISTINCT` porte sur TOUTES les colonnes du SELECT.** `SELECT DISTINCT ville, nom` dédoublonne sur le couple (ville, nom), pas seulement sur la ville.

### 4.3 Produire des indicateurs — agrégations, `GROUP BY`, `HAVING`

> 📖 Syntaxe complète : [Fonctions d'agrégation](../02-Agregations-Groupby/01-fonctions-agregation.md), [GROUP BY](../02-Agregations-Groupby/02-group-by.md), [HAVING](../02-Agregations-Groupby/03-having.md).

> **Demande métier :** « Quel est le panier moyen ? Combien de commandes ce mois-ci ? Le CA par magasin ? » — `COUNT`, `SUM`, `AVG` sont tes outils du quotidien pour les KPI d'un dashboard, et `GROUP BY` sert tous les classiques du reporting (CA par magasin, commandes par mois, panier moyen par catégorie).

```sql
-- Prix moyen par catégorie de produit, du plus cher au moins cher
SELECT categorie, AVG(prix_unitaire) AS prix_moyen
FROM produits
GROUP BY categorie
ORDER BY prix_moyen DESC;
```

**Résultat attendu :**

| categorie | prix_moyen |
|---|---|
| Hygiène | 6.80 |
| Épicerie | 4.10 |
| Boisson | 1.95 |

> **Demande métier :** « Quels magasins ont fait plus de 100 commandes ce mois-ci ? » → `GROUP BY magasin` puis `HAVING COUNT(*) > 100`.

```sql
-- Villes qui comptent plus de 9 clients
SELECT ville, COUNT(*) AS nombre_clients
FROM clients
GROUP BY ville
HAVING COUNT(*) > 9;
```

**Résultat attendu :**

| ville | nombre_clients |
|---|---|
| Lille | 15 |
| Roubaix | 10 |

On peut combiner `WHERE` (avant regroupement) et `HAVING` (après agrégation) dans une même requête :

```sql
-- Parmi les produits coûtant plus de 1 €, les catégories
-- dont le prix moyen dépasse 4 €
SELECT categorie, AVG(prix_unitaire) AS prix_moyen
FROM produits
WHERE prix_unitaire > 1          -- filtre les lignes AVANT
GROUP BY categorie
HAVING AVG(prix_unitaire) > 4;   -- filtre les groupes APRÈS
```

> **La règle d'or :** toute colonne du `SELECT` qui n'est **pas** dans une fonction d'agrégation **doit** apparaître dans le `GROUP BY`.

> ⚠️ **Erreurs courantes qui faussent les KPI**
> - **`COUNT(*)` vs `COUNT(colonne)`** : `COUNT(*)` compte toutes les lignes ; `COUNT(ville)` ne compte que les lignes où `ville` n'est **pas NULL**. Sur une colonne à trous, tes deux comptages divergent.
> - **Utiliser `WHERE` à la place de `HAVING`** pour filtrer un `COUNT`/`SUM` → erreur de syntaxe (`WHERE COUNT(*) > 5` est interdit).
> - **Inverser la logique :** filtrer une simple colonne (ex. `ville = 'Lille'`) doit se faire dans `WHERE`, pas `HAVING`, pour de meilleures performances.
> - **Croire que `GROUP BY` trie.** Il regroupe, mais ne garantit pas l'ordre. Pour trier, ajoute `ORDER BY`.

### 4.4 Croiser les tables — `INNER JOIN` et `LEFT JOIN`

> 📖 Syntaxe complète et autres types de jointures : [Module 03 - Jointures](../03-Jointures/README.md).

Le choix du type de jointure est une **décision d'analyse**, pas un détail technique :

- `INNER JOIN` → « je ne veux que les lignes qui matchent des deux côtés » (ex. les commandes **avec** leur client).
- `LEFT JOIN` → « je veux **tout** de la table principale, même sans correspondance » (ex. **tous** les clients, y compris ceux sans commande).

```sql
-- TOUS les clients, avec leurs commandes s'ils en ont
SELECT
    clients.nom,
    clients.prenom,
    commandes.commande_id
FROM clients
LEFT JOIN commandes ON clients.client_id = commandes.client_id;
```

**Résultat attendu :**

| nom | prenom | commande_id |
|---|---|---|
| Dubois | Camille | 1 |
| Bernard | Mehdi | 2 |
| Petit | Julie | *NULL* |

Ici, **Julie Petit n'a jamais commandé** : avec un `INNER JOIN` elle disparaîtrait du résultat ; avec un `LEFT JOIN` elle apparaît, avec `NULL` en face. C'est précieux pour repérer les clients inactifs.

> **Demande métier :** « Liste des clients qui n'ont jamais commandé » → un `LEFT JOIN` de `clients` vers `commandes` puis `WHERE commandes.commande_id IS NULL`. Parfait pour une campagne de réactivation.

> ⚠️ **Erreurs courantes**
> - **Oublier la condition `ON`** → produit cartésien (chaque ligne croisée avec chaque ligne, des milliers de résultats inutiles).
> - **Se tromper de colonnes dans le `ON`** (relier `client_id` à `produit_id`) → résultats incohérents.
> - **Croire que `LEFT JOIN` = `INNER JOIN`** : la différence n'apparaît que quand il existe des lignes sans correspondance — c'est-à-dire exactement les cas intéressants pour l'analyse (clients inactifs, produits jamais vendus…).

### 4.5 Les alias (`AS`) — rendre les requêtes lisibles

Un **alias** donne un nom plus court ou plus parlant à une table ou à une colonne. C'est confortable, surtout avec les jointures — et indispensable pour que les en-têtes de ton export soient compréhensibles par le métier.

```sql
SELECT
    c.nom        AS nom_client,
    cmd.quantite AS qte
FROM clients AS c
INNER JOIN commandes AS cmd ON c.client_id = cmd.client_id;
```

- **Alias de colonne** : `COUNT(*) AS nombre_clients` → l'en-tête du résultat s'appelle `nombre_clients`.
- **Alias de table** : `clients AS c` → on écrit ensuite `c.nom` au lieu de `clients.nom`.

> Le mot-clé `AS` est **optionnel** : `FROM clients c` fonctionne aussi. Mais l'écrire rend le code plus clair pour un débutant.

> ⚠️ **Erreur courante** : l'alias remplace le nom complet. Si tu écris `FROM clients AS c`, tu ne peux plus écrire `clients.nom`, il faut `c.nom`.

---

## 5. Travaux pratiques

Travaille sur le jeu de données **« Ventes Retail Nord »**. Écris chaque requête, exécute-la, **vérifie le résultat**, puis compare avec le corrigé.

### TP 1 — Premiers SELECT (échauffement)
Affiche le **nom du produit** et son **prix unitaire** pour tous les produits, triés du **moins cher au plus cher**.

<details><summary>✅ Corrigé</summary>

```sql
SELECT nom_produit, prix_unitaire
FROM produits
ORDER BY prix_unitaire ASC;
```
</details>

### TP 2 — Filtrer avec WHERE
Affiche les clients (`prenom`, `nom`, `ville`) qui habitent à **Lille ou Roubaix**. Utilise `IN`.

<details><summary>✅ Corrigé</summary>

```sql
SELECT prenom, nom, ville
FROM clients
WHERE ville IN ('Lille', 'Roubaix');
```
*Variante acceptée :* `WHERE ville = 'Lille' OR ville = 'Roubaix'`.
</details>

### TP 3 — LIKE et BETWEEN
Affiche les produits de la catégorie **Épicerie** dont le prix est **entre 2 € et 6 €**, et dont le nom **contient le mot « bio »**.

<details><summary>✅ Corrigé</summary>

```sql
SELECT nom_produit, categorie, prix_unitaire
FROM produits
WHERE categorie = 'Épicerie'
  AND prix_unitaire BETWEEN 2 AND 6
  AND nom_produit LIKE '%bio%';
```
*Astuce : `%bio%` trouve « bio » n'importe où dans le libellé.*
</details>

### TP 4 — Agrégation + GROUP BY
Calcule le **nombre de produits** et le **prix moyen** **par catégorie**. Trie par prix moyen décroissant.

<details><summary>✅ Corrigé</summary>

```sql
SELECT
    categorie,
    COUNT(*)            AS nombre_produits,
    AVG(prix_unitaire)  AS prix_moyen
FROM produits
GROUP BY categorie
ORDER BY prix_moyen DESC;
```
</details>

### TP 5 — GROUP BY + HAVING
Affiche les **villes ayant strictement plus de 8 clients**, avec leur nombre de clients, triées du plus grand au plus petit.

<details><summary>✅ Corrigé</summary>

```sql
SELECT ville, COUNT(*) AS nombre_clients
FROM clients
GROUP BY ville
HAVING COUNT(*) > 8
ORDER BY nombre_clients DESC;
```
*Rappel : le filtre sur `COUNT(*)` se fait avec `HAVING`, pas `WHERE`.*
</details>

### TP 6 — Jointures (le grand final)
Pour chaque commande, affiche le **nom du client**, le **nom du produit**, le **nom du magasin** et la **quantité**. Garde uniquement les commandes effectuées dans le magasin de **Lille**, triées par quantité décroissante.

<details><summary>✅ Corrigé</summary>

```sql
SELECT
    c.nom          AS client,
    p.nom_produit  AS produit,
    m.nom_magasin  AS magasin,
    cmd.quantite   AS qte
FROM commandes AS cmd
INNER JOIN clients  AS c ON cmd.client_id  = c.client_id
INNER JOIN produits AS p ON cmd.produit_id = p.produit_id
INNER JOIN magasins AS m ON cmd.magasin_id = m.magasin_id
WHERE m.ville = 'Lille'
ORDER BY cmd.quantite DESC;
```
</details>

### TP 7 (bonus) — LEFT JOIN : les clients inactifs
Trouve **tous les clients qui n'ont jamais passé de commande** (nom, prénom).

<details><summary>✅ Corrigé</summary>

```sql
SELECT c.nom, c.prenom
FROM clients AS c
LEFT JOIN commandes AS cmd ON c.client_id = cmd.client_id
WHERE cmd.commande_id IS NULL;
```
*Logique : on garde tous les clients (`LEFT JOIN`) puis on ne conserve que ceux qui n'ont AUCUNE commande en face (`IS NULL`).*
</details>

---

## 6. Vidéos d'auto-formation

> Quand l'URL exacte d'une vidéo n'est pas certaine, le lien pointe vers une **recherche YouTube** : choisis la vidéo la plus vue et récente.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| MySQL Tutorial for Beginners [Full Course] | Programming with Mosh | EN (sous-titres FR auto) | ~3h | [youtu.be/7S_tz1z_5bA](https://www.youtube.com/watch?v=7S_tz1z_5bA) | Cours complet : SELECT, WHERE, ORDER BY, agrégations, GROUP BY, jointures. La référence pour débuter. |
| Complete SQL Mastery (playlist) | Programming with Mosh | EN | série | [Playlist YouTube](https://www.youtube.com/playlist?list=PLOghUv2IDLKHKlkQNuzN8SPLYuVhhLlpa) | Découpage par notion : pratique pour réviser un point précis (jointures, GROUP BY…). |
| Apprendre SQL — les bases (recherche) | Cookie connecté | FR | variable | [Recherche YouTube](https://www.youtube.com/results?search_query=cookie+connect%C3%A9+SQL+base+de+donn%C3%A9es) | Vulgarisation claire : à quoi sert une base relationnelle, concepts clés en français. |
| Cours SQL débutant complet (recherche) | Graven - Développement | FR | variable | [Recherche YouTube](https://www.youtube.com/results?search_query=graven+SQL+tutoriel+d%C3%A9butant) | Tutoriel francophone pas à pas, du SELECT aux jointures, avec démonstrations. |
| SQL Joins Tutorial — Inner, Left, Right, Full | (recherche) | EN | ~1h | [Recherche YouTube](https://www.youtube.com/results?search_query=sql+joins+tutorial+inner+left+right+full+beginners) | Focalisé sur les jointures, avec schémas visuels (diagrammes de Venn) très parlants. |

---

## 7. Quiz — 5 QCM

**Q1.** Quelle clause sert à **filtrer des lignes avant tout regroupement** ?
- a) `HAVING`
- b) `WHERE`
- c) `GROUP BY`
- d) `ORDER BY`

**Q2.** Que renvoie `SELECT COUNT(*) FROM clients WHERE ville = 'Lille';` ?
- a) La liste des clients de Lille
- b) Le nombre de clients de Lille
- c) Toutes les villes
- d) Une erreur

**Q3.** Tu veux **tous les clients, même ceux sans commande**. Quelle jointure ?
- a) `INNER JOIN`
- b) `LEFT JOIN` (clients à gauche)
- c) `WHERE`
- d) `GROUP BY`

**Q4.** Quelle requête est **correcte** pour « les catégories ayant plus de 3 produits » ?
- a) `SELECT categorie FROM produits WHERE COUNT(*) > 3 GROUP BY categorie;`
- b) `SELECT categorie, COUNT(*) FROM produits GROUP BY categorie HAVING COUNT(*) > 3;`
- c) `SELECT categorie FROM produits HAVING COUNT(*) > 3;`
- d) `SELECT categorie, COUNT(*) FROM produits ORDER BY COUNT(*) > 3;`

**Q5.** Que fait `WHERE nom LIKE 'Du%'` ?
- a) Les noms qui finissent par « Du »
- b) Les noms qui contiennent « Du »
- c) Les noms qui commencent par « Du »
- d) Les noms exactement égaux à « Du »

<details><summary>✅ Réponses</summary>

1. **b)** `WHERE` filtre les lignes avant le `GROUP BY`. (`HAVING` filtre les groupes après.)
2. **b)** `COUNT(*)` compte les lignes correspondant au filtre → le nombre de clients de Lille.
3. **b)** `LEFT JOIN` conserve toutes les lignes de la table de gauche (`clients`), même sans correspondance.
4. **b)** Filtrer un `COUNT` se fait avec `HAVING`, après le `GROUP BY`.
5. **c)** `'Du%'` = commence par « Du » (le `%` représente la suite). Pour « finit par », ce serait `'%Du'` ; pour « contient », `'%Du%'`.
</details>

---

## 8. À retenir — mémo de syntaxe

**L'ordre des clauses (à respecter impérativement) :**

```sql
SELECT   colonnes / agrégations
FROM     table
JOIN     autre_table ON condition
WHERE    condition sur les lignes
GROUP BY colonnes de regroupement
HAVING   condition sur les groupes
ORDER BY colonnes de tri [ASC|DESC]
LIMIT    nombre;
```

**Aide-mémoire express :**

| Je veux… | J'utilise… |
|---|---|
| Choisir des colonnes | `SELECT col1, col2` |
| Lire une table | `FROM table` |
| Filtrer des lignes | `WHERE condition` |
| Plusieurs conditions | `AND`, `OR`, `IN (...)`, `BETWEEN x AND y`, `LIKE '%motif%'` |
| Trier | `ORDER BY col DESC` |
| Limiter le nombre de lignes | `LIMIT 10` |
| Supprimer les doublons | `SELECT DISTINCT col` |
| Compter / additionner / moyenne | `COUNT(*)`, `SUM(col)`, `AVG(col)`, `MIN`, `MAX` |
| Agréger par catégorie | `GROUP BY col` |
| Filtrer sur une agrégation | `HAVING COUNT(*) > 5` |
| Croiser des tables (correspondances) | `INNER JOIN t ON a = b` |
| Croiser en gardant tout à gauche | `LEFT JOIN t ON a = b` |
| Renommer | `AS nouveau_nom` |

> 🎯 **La phrase à graver :** *« WHERE filtre les lignes, HAVING filtre les groupes. INNER JOIN garde les correspondances, LEFT JOIN garde tout à gauche. »*

---

[🏠 Accueil](../README.md) | [📂 Module 09](README.md) | [02 - SQL avancé pour l'analyse →](02-sql-avance-analyse.md)
