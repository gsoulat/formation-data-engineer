# 02 - SQL avancé pour l'analyse

[← 01 - Extraction ciblée](01-extraction-ciblee.md) | [🏠 Accueil](../README.md) | [📂 Module 09](README.md) | [03 - Extraction multi-sources →](03-extraction-multi-sources.md)

---

| | |
|---|---|
| **Durée indicative** | ~14 heures (pratique incluse) |
| **Objectif** | Requêter une base de données et extraire des données de sources variées |
| **Prérequis** | [01 - Extraction ciblée](01-extraction-ciblee.md), [Module 05 (CTE, Window Functions)](../05-Fonctions-Avancees/README.md) |
| **Outils** | SQLite (DB Browser for SQLite ou la librairie `sqlite3` de Python) + une base de ventes retail |

---

## 1. Objectifs

À la fin de ce chapitre, tu seras capable d'écrire des requêtes **SQL avancées** orientées analyse :

- **Sous-requêtes** : comparer chaque ligne à une valeur calculée globalement.
- **CTE (`WITH`)** : organiser une requête complexe en étapes nommées et lisibles.
- **Fonctions de fenêtrage** : classer (`ROW_NUMBER`, `RANK`, `DENSE_RANK`) et comparer aux lignes voisines (`LAG`, `LEAD`).
- **Agrégations conditionnelles** (`CASE WHEN`) : produire des tableaux croisés directement en SQL.
- **Combinaisons de résultats** (`UNION`, `UNION ALL`) : reconstituer un historique à partir de plusieurs tables.

> 📖 **La syntaxe de base des CTE et des window functions est introduite dans le [Module 05 - Fonctions Avancées](../05-Fonctions-Avancees/README.md)** ([CTE](../05-Fonctions-Avancees/01-ctes-with.md), [Window Functions](../05-Fonctions-Avancees/02-window-functions.md)). Ici, on les met au service de **questions d'analyse réelles** : top N par groupe, évolution mois/mois, tableau croisé, historique multi-années.

---

## 2. Pourquoi le SQL « simple » ne suffit plus

Avec `SELECT`, `WHERE`, `GROUP BY` et les jointures (chapitre [01](01-extraction-ciblee.md)), tu sais répondre à « quel est le CA par magasin ? ». Mais les demandes métier qui arrivent réellement sur ton bureau ressemblent plutôt à :

- « Donne-moi le **top 3 des vendeurs de chaque magasin**. » → impossible avec un simple `GROUP BY` : il faut classer **à l'intérieur** de chaque groupe.
- « Quelle est l'**évolution du CA par rapport au mois précédent** ? » → il faut comparer chaque ligne à la ligne d'avant.
- « Fais-moi un **tableau avec une colonne par catégorie**. » → il faut agréger conditionnellement.
- « Reconstitue l'**historique 2023 + 2024** alors que chaque année est dans une table séparée. » → il faut empiler des résultats.

Ce sont exactement les outils de ce chapitre. C'est ce qui distingue un analyst qui « connaît le SQL » d'un analyst **opérationnel en entreprise**.

---

## 3. La table de travail : `ventes`

On travaille sur une base de ventes retail (chaîne de magasins du Nord). Table principale :

```sql
-- Table ventes (un enregistrement = une ligne de ticket)
-- colonnes : vente_id, date_vente, magasin, vendeur, categorie, produit, quantite, montant
SELECT * FROM ventes LIMIT 3;
```

| vente_id | date_vente | magasin | vendeur | categorie | produit | quantite | montant |
|---|---|---|---|---|---|---|---|
| 1 | 2024-01-03 | Lille | Amel | Textile | Pull | 2 | 59.80 |
| 2 | 2024-01-03 | Roubaix | Karim | Maison | Lampe | 1 | 24.90 |
| 3 | 2024-01-04 | Lille | Amel | Textile | Jean | 1 | 49.90 |

---

## 4. Les outils du SQL analytique

### 4.1 Les sous-requêtes

Une **sous-requête** est une requête imbriquée dans une autre. Utile pour comparer chaque ligne à une valeur calculée globalement.

> **Demande métier :** « Quels magasins font un CA supérieur à la moyenne des magasins ? »

```sql
-- Magasins dont le CA total dépasse la moyenne des CA par magasin
SELECT magasin, SUM(montant) AS ca_magasin
FROM ventes
GROUP BY magasin
HAVING SUM(montant) > (
    SELECT AVG(ca) FROM (
        SELECT SUM(montant) AS ca
        FROM ventes
        GROUP BY magasin
    ) AS ca_par_magasin
);
```

**Résultat attendu :**

| magasin | ca_magasin |
|---|---|
| Lille | 184250.40 |
| Villeneuve-d'Ascq | 142890.10 |

> La sous-requête interne calcule le CA de chaque magasin, l'intermédiaire en fait la moyenne, et la requête externe ne garde que ceux au-dessus.

### 4.2 Les CTE (`WITH`)

> 📖 Syntaxe de base : [Module 05 - Les CTE](../05-Fonctions-Avancees/01-ctes-with.md).

Une **CTE** (Common Table Expression) est une sous-requête **nommée**, déclarée avant le `SELECT` principal. Même résultat que les sous-requêtes imbriquées, mais **bien plus lisible** — et réutilisable plusieurs fois dans la même requête.

```sql
-- La même logique que ci-dessus, en version lisible
WITH ca_par_magasin AS (
    SELECT magasin, SUM(montant) AS ca
    FROM ventes
    GROUP BY magasin
)
SELECT magasin, ca
FROM ca_par_magasin
WHERE ca > (SELECT AVG(ca) FROM ca_par_magasin)
ORDER BY ca DESC;
```

**Résultat attendu :**

| magasin | ca |
|---|---|
| Lille | 184250.40 |
| Villeneuve-d'Ascq | 142890.10 |

> On peut chaîner plusieurs CTE séparées par des virgules. C'est la **bonne pratique** professionnelle : on lit la requête de haut en bas comme une suite d'étapes.

### 4.3 Les fonctions de fenêtrage (window functions)

> 📖 Syntaxe de base : [Module 05 - Window Functions](../05-Fonctions-Avancees/02-window-functions.md).

Une **fonction de fenêtrage** effectue un calcul sur un **groupe de lignes lié à la ligne courante**, **sans** réduire le nombre de lignes (contrairement à `GROUP BY`). C'est la grande différence : on garde le détail **et** on ajoute une colonne calculée.

La syntaxe centrale est la clause `OVER (PARTITION BY ... ORDER BY ...)` :
- `PARTITION BY` : découpe en groupes (comme un GROUP BY, mais sans fusionner les lignes).
- `ORDER BY` : ordonne à l'intérieur de chaque groupe.

**ROW_NUMBER, RANK, DENSE_RANK — classer les lignes :**

> **Demande métier :** « Classe les produits par CA à l'intérieur de chaque catégorie. »

```sql
SELECT
    categorie,
    produit,
    SUM(montant) AS ca,
    ROW_NUMBER() OVER (PARTITION BY categorie ORDER BY SUM(montant) DESC) AS num_ligne,
    RANK()       OVER (PARTITION BY categorie ORDER BY SUM(montant) DESC) AS rang
FROM ventes
GROUP BY categorie, produit;
```

**Résultat attendu :**

| categorie | produit | ca | num_ligne | rang |
|---|---|---|---|---|
| Textile | Jean | 12450.00 | 1 | 1 |
| Textile | Pull | 9870.30 | 2 | 2 |
| Textile | Tee-shirt | 9870.30 | 3 | 2 |
| Maison | Lampe | 5400.00 | 1 | 1 |

> Différence clé : sur l'ex-aequo à 9870.30, **ROW_NUMBER** met 2 puis 3 (jamais d'égalité), **RANK** met 2 et 2 puis sauterait à 4. `DENSE_RANK` ferait 2 et 2 puis 3 (sans saut).

**LAG et LEAD — comparer à la ligne précédente / suivante :**

> **Demande métier :** « Quelle est l'évolution du CA mensuel par rapport au mois précédent ? »

```sql
WITH ca_mensuel AS (
    SELECT
        strftime('%Y-%m', date_vente) AS mois,
        SUM(montant) AS ca
    FROM ventes
    GROUP BY mois
)
SELECT
    mois,
    ca,
    LAG(ca) OVER (ORDER BY mois) AS ca_mois_precedent,
    ca - LAG(ca) OVER (ORDER BY mois) AS evolution
FROM ca_mensuel
ORDER BY mois;
```

**Résultat attendu :**

| mois | ca | ca_mois_precedent | evolution |
|---|---|---|---|
| 2024-01 | 42000.00 | NULL | NULL |
| 2024-02 | 38500.00 | 42000.00 | -3500.00 |
| 2024-03 | 51200.00 | 38500.00 | 12700.00 |

> `LAG` regarde **en arrière** (mois précédent), `LEAD` regarde **en avant**. La première ligne n'a pas de précédent → `NULL`. C'est le calcul d'évolution mois/mois, archi-classique en analyse retail.

> ⚠️ **Piège — `strftime()` exige des dates au format ISO**
> En SQLite, `strftime('%Y-%m', date_vente)` ne fonctionne **que** si `date_vente` est stockée au format ISO `YYYY-MM-DD` (ex. `2024-01-15`). Si la colonne contient un autre format (ex. `15/01/2024` en `JJ/MM/AAAA`), SQLite ne lève **aucune erreur** : `strftime` renvoie `NULL` **silencieusement**.
> C'est sournois, car le cœur de ce module est justement la **validation de l'exactitude des données** : un GROUP BY sur un `mois` à `NULL` regroupe alors **toutes** les ventes dans une seule ligne fantôme, et personne ne voit le problème tant qu'on ne regarde pas les résultats de près.
>
> **Comment le détecter** : si la colonne `mois` (ou un `WHERE strftime(...) IS NULL`) renvoie des `NULL` inattendus, le format des dates est en cause.
> ```sql
> -- Diagnostic : combien de dates SQLite n'arrive pas à parser ?
> SELECT COUNT(*) FROM ventes WHERE strftime('%Y-%m', date_vente) IS NULL;
> -- > 0  =>  dates dans un format non-ISO
> ```
> **Comment l'éviter** : normaliser les dates en ISO `YYYY-MM-DD` **avant** de charger les données (étape de nettoyage), ou reconstruire la date à la volée depuis un format `JJ/MM/AAAA` :
> ```sql
> -- Recoller JJ/MM/AAAA -> AAAA-MM-JJ avant strftime
> strftime('%Y-%m',
>   substr(date_vente, 7, 4) || '-' || substr(date_vente, 4, 2) || '-' || substr(date_vente, 1, 2)
> ) AS mois
> ```
> En pratique : on stocke **toujours** les dates en ISO dès l'ingestion, et `strftime`/`date()` redeviennent fiables.

### 4.4 Agrégations conditionnelles avec `CASE WHEN`

`CASE WHEN` permet de **catégoriser** une valeur ou de faire un **comptage conditionnel** (l'équivalent SQL d'un tableau croisé).

> **Demande métier :** « Répartis le CA par tranche de panier, avec la part du Textile, magasin par magasin. »

```sql
SELECT
    magasin,
    SUM(CASE WHEN montant < 30 THEN montant ELSE 0 END)        AS ca_petit_panier,
    SUM(CASE WHEN montant >= 30 THEN montant ELSE 0 END)       AS ca_gros_panier,
    SUM(CASE WHEN categorie = 'Textile' THEN montant ELSE 0 END) AS ca_textile,
    COUNT(CASE WHEN montant >= 30 THEN 1 END)                  AS nb_gros_paniers
FROM ventes
GROUP BY magasin;
```

**Résultat attendu :**

| magasin | ca_petit_panier | ca_gros_panier | ca_textile | nb_gros_paniers |
|---|---|---|---|---|
| Lille | 31200.00 | 153050.40 | 98400.00 | 1842 |
| Roubaix | 18900.00 | 64100.10 | 41200.00 | 980 |

> 💡 **Astuce :** dans `COUNT(CASE WHEN ... THEN 1 END)`, le `ELSE` est omis → les lignes non concernées valent `NULL` et ne sont pas comptées.

### 4.5 `UNION` — empiler des résultats

`UNION` colle deux résultats l'un sous l'autre (les colonnes doivent correspondre). `UNION` supprime les doublons, `UNION ALL` les garde (et est plus rapide).

> **Demande métier :** « Reconstitue l'historique complet des ventes, alors que 2023 est dans une table archivée et 2024 dans la table courante. »

```sql
-- Combiner les ventes 2023 (table archivée) et 2024 (table courante)
SELECT date_vente, magasin, montant FROM ventes_2023
UNION ALL
SELECT date_vente, magasin, montant FROM ventes;
```

> Cas typique : une table d'archive par année à reconstituer en historique complet.

> ⚠️ **Erreur courante — UNION vs UNION ALL.** Si tu utilises `UNION` (sans `ALL`) pour empiler deux années, et qu'une vente identique existe dans les deux tables (même date, même magasin, même montant), elle sera **supprimée** silencieusement. Pour empiler de l'historique, utilise quasi toujours `UNION ALL`.

---

## 5. Travaux pratiques

> Utilise **SQLite** (via DB Browser for SQLite ou la librairie `sqlite3` de Python) avec une base de ventes retail. Écris chaque requête, exécute-la, **vérifie le résultat**, puis compare avec le corrigé.

### TP 1 — Classement avec ROW_NUMBER

Écris une requête qui, pour **chaque magasin**, donne le **top 3 des vendeurs** par CA généré.

<details><summary>✅ Corrigé</summary>

```sql
WITH ca_vendeur AS (
    SELECT magasin, vendeur, SUM(montant) AS ca
    FROM ventes
    GROUP BY magasin, vendeur
),
classement AS (
    SELECT
        magasin, vendeur, ca,
        ROW_NUMBER() OVER (PARTITION BY magasin ORDER BY ca DESC) AS rang
    FROM ca_vendeur
)
SELECT magasin, vendeur, ca
FROM classement
WHERE rang <= 3
ORDER BY magasin, rang;
```

*On classe à l'intérieur de chaque magasin (`PARTITION BY magasin`), puis on filtre `rang <= 3`. **Impossible** de filtrer directement sur `ROW_NUMBER()` dans un `WHERE` simple : il faut passer par une CTE (ou sous-requête) car la fonction de fenêtrage est calculée après le `WHERE`.*
</details>

### TP 2 — Évolution mensuelle avec LAG

Calcule, par magasin, le CA de chaque mois **et** le pourcentage d'évolution par rapport au mois précédent.

<details><summary>✅ Corrigé</summary>

```sql
WITH ca_mensuel AS (
    SELECT
        magasin,
        strftime('%Y-%m', date_vente) AS mois,
        SUM(montant) AS ca
    FROM ventes
    GROUP BY magasin, mois
)
SELECT
    magasin,
    mois,
    ca,
    LAG(ca) OVER (PARTITION BY magasin ORDER BY mois) AS ca_precedent,
    ROUND(
        (ca - LAG(ca) OVER (PARTITION BY magasin ORDER BY mois))
        * 100.0 / LAG(ca) OVER (PARTITION BY magasin ORDER BY mois),
        1
    ) AS evolution_pct
FROM ca_mensuel
ORDER BY magasin, mois;
```

*Le `PARTITION BY magasin` est essentiel : sans lui, le LAG comparerait le janvier de Roubaix au décembre de Lille. Penser à `* 100.0` (et pas `* 100`) pour éviter la division entière.*
</details>

### TP 3 — Tableau croisé avec CASE WHEN

Produis un tableau avec une ligne par magasin et une colonne par catégorie (Textile, Maison, Autre) contenant le CA de chaque catégorie.

<details><summary>✅ Corrigé</summary>

```sql
SELECT
    magasin,
    SUM(CASE WHEN categorie = 'Textile' THEN montant ELSE 0 END) AS ca_textile,
    SUM(CASE WHEN categorie = 'Maison'  THEN montant ELSE 0 END) AS ca_maison,
    SUM(CASE WHEN categorie NOT IN ('Textile', 'Maison') THEN montant ELSE 0 END) AS ca_autre,
    SUM(montant) AS ca_total
FROM ventes
GROUP BY magasin
ORDER BY ca_total DESC;
```

*C'est le **pivot** en SQL : une colonne par valeur, agrégée conditionnellement. Vérification : `ca_textile + ca_maison + ca_autre` doit égaler `ca_total`.*
</details>

---

## 6. Vidéos d'auto-formation

> Les liens sont vérifiés au moment de la rédaction. Si une vidéo a disparu, cherche un équivalent avec les mots-clés du titre.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Sous-requêtes SQL & CTE (WITH) : écrire des requêtes propres | Tutoriel SQL FR | FR | ~25 min | [YouTube](https://www.youtube.com/watch?v=EQadZsOUSbk) | Quand utiliser une sous-requête vs une CTE, écrire du SQL lisible et professionnel |
| Maîtriser les CTE SQL : Expressions de Table Communes | Tutoriel SQL FR | FR | ~15 min | [YouTube](https://www.youtube.com/watch?v=KSVeW55vuec) | Syntaxe `WITH`, CTE chaînées, cas d'usage en analyse de données |
| SQL Window Functions \| ROW_NUMBER, SUM, RANK | SQL Beginner Tutorial | EN | ~20 min | [YouTube](https://www.youtube.com/watch?v=rj6d4C1PQNc) | Les fonctions de fenêtrage de base avec exemples simples |
| SQL Ranking Window Functions \| ROW_NUMBER, RANK, DENSE_RANK, NTILE | (cours SQL) | EN | ~12 min | [YouTube](https://www.youtube.com/watch?v=cXhv4kmIzFw) | Différences entre les fonctions de classement, expliquées visuellement |

---

## 7. Quiz — 5 QCM

**Q1.** Quelle est la principale différence entre une fonction de fenêtrage (`OVER`) et un `GROUP BY` ?
- a) La fonction de fenêtrage est plus rapide
- b) `GROUP BY` garde toutes les lignes, la fonction de fenêtrage les fusionne
- c) La fonction de fenêtrage garde toutes les lignes en ajoutant une colonne calculée, `GROUP BY` réduit le nombre de lignes
- d) Il n'y a aucune différence

**Q2.** Avec un ex-aequo, que fait `ROW_NUMBER()` comparé à `RANK()` ?
- a) Les deux donnent le même résultat
- b) `ROW_NUMBER` ne donne jamais d'égalité (1,2,3...), `RANK` donne la même valeur aux ex-aequo puis saute
- c) `RANK` ne donne jamais d'égalité, `ROW_NUMBER` saute
- d) Aucun des deux ne gère les ex-aequo

**Q3.** Pourquoi préférer `UNION ALL` à `UNION` pour empiler deux années de ventes ?
- a) `UNION ALL` trie automatiquement
- b) `UNION ALL` garde tous les enregistrements (ne supprime pas les doublons légitimes) et est plus rapide
- c) `UNION` ne fonctionne pas sur plus de 1000 lignes
- d) Il n'y a pas de différence

**Q4.** Que compte `COUNT(CASE WHEN montant >= 30 THEN 1 END)` ?
- a) Toutes les lignes de la table
- b) Uniquement les lignes dont `montant >= 30` (les autres valent `NULL` et ne sont pas comptées)
- c) La somme des montants supérieurs à 30
- d) Rien : c'est une erreur de syntaxe car le `ELSE` est obligatoire

**Q5.** En SQLite, `strftime('%Y-%m', date_vente)` renvoie `NULL` pour certaines lignes. Cause la plus probable ?
- a) La table est trop grande
- b) Il manque un `GROUP BY`
- c) Les dates concernées ne sont pas stockées au format ISO `YYYY-MM-DD`
- d) `strftime` ne fonctionne pas dans une CTE

<details><summary>✅ Réponses</summary>

1. **c)** C'est la distinction fondamentale : la fonction de fenêtrage conserve le détail ligne à ligne.
2. **b)** `ROW_NUMBER` = numérotation unique sans égalité ; `RANK` = même rang aux ex-aequo puis saut.
3. **b)** `UNION` supprimerait silencieusement des ventes réellement identiques ; `UNION ALL` préserve tout.
4. **b)** Sans `ELSE`, les lignes non concernées valent `NULL` et `COUNT` ignore les `NULL` : on obtient un comptage conditionnel.
5. **c)** `strftime` échoue **silencieusement** (renvoie `NULL`) sur les dates non-ISO — un piège classique à détecter avec `WHERE strftime(...) IS NULL`.
</details>

---

## 8. À retenir

- **CTE (`WITH`)** : la façon lisible et professionnelle d'organiser des requêtes complexes en étapes nommées. À privilégier sur les sous-requêtes imbriquées.
- **Fonctions de fenêtrage** : `ROW_NUMBER`/`RANK` pour classer, `LAG`/`LEAD` pour comparer aux lignes voisines (évolutions). Elles **gardent le détail**, contrairement à `GROUP BY`.
- **`CASE WHEN`** dans une agrégation = tableau croisé / comptage conditionnel en SQL.
- **`UNION ALL`** pour empiler de l'historique (`UNION` seul supprime les doublons, silencieusement).
- **Les dates se stockent en ISO** (`YYYY-MM-DD`) dès l'ingestion, sinon `strftime` renvoie `NULL` sans prévenir.

**Aide-mémoire express :**

| Je veux… | J'utilise… |
|---|---|
| Comparer chaque groupe à une valeur globale | sous-requête ou CTE |
| Organiser une requête complexe en étapes | `WITH etape1 AS (...), etape2 AS (...)` |
| Top N **par groupe** | `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` + filtre dans une CTE |
| Évolution vs mois précédent | `LAG(ca) OVER (ORDER BY mois)` |
| Tableau croisé (une colonne par valeur) | `SUM(CASE WHEN ... THEN ... ELSE 0 END)` |
| Comptage conditionnel | `COUNT(CASE WHEN ... THEN 1 END)` |
| Empiler des historiques | `UNION ALL` |

> 🎯 **La phrase à graver :** *« GROUP BY résume, la window function annote. LAG regarde derrière, LEAD regarde devant. UNION ALL empile sans rien perdre. »*

---

[← 01 - Extraction ciblée](01-extraction-ciblee.md) | [🏠 Accueil](../README.md) | [📂 Module 09](README.md) | [03 - Extraction multi-sources →](03-extraction-multi-sources.md)
