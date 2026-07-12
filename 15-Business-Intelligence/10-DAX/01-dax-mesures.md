# 01 — DAX & mesures avancées (Power BI)

| | |
|---|---|
| **Titre** | DAX & mesures avancées (Power BI) |
| **Phase** | Phase 2 — BI avancée |
| **Durée** | ~35 h |
| **Compétence visée** | **C18** — Concevoir des indicateurs et mesures de performance à l'aide d'un langage d'expression analytique (DAX) afin de répondre à un besoin métier |
| **Pré-requis** | Module 2.2 — Modélisation BI (modèle en étoile, relations, table de dates / table de faits / tables de dimensions) |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

- Expliquer **ce qu'est le DAX** et à quoi il sert dans Power BI.
- Distinguer **une mesure** d'**une colonne calculée** et savoir laquelle utiliser.
- Comprendre la différence entre **contexte de filtre** et **contexte de ligne** (LE concept clé).
- Utiliser les **fonctions d'agrégation** : `SUM`, `AVERAGE`, `COUNTROWS`, `DISTINCTCOUNT`.
- Maîtriser **`CALCULATE`** (la fonction reine) et **`FILTER`**.
- Construire des **calculs temporels** (YoY, MoM) avec `TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`.
- Écrire du DAX lisible grâce aux **variables** (`VAR` / `RETURN`).
- Produire les **mesures retail usuelles** : chiffre d'affaires, marge %, panier moyen, évolution N-1.

---

## Pourquoi le DAX fait la différence

Tu sais déjà construire un modèle propre (module 2.2). Mais un modèle ne « calcule » rien tout seul. Glisser un champ `Montant` dans un visuel te donne une somme brute, point. Dès que ton commanditaire demande :

> *« Quel est le CA de cette année comparé à l'an dernier, **uniquement** pour le magasin de Lille, **hors** retours, et en pourcentage d'évolution ? »*

… tu te retrouves coincé. Aucun glisser-déposer ne répond à ça. C'est **exactement** le territoire du DAX.

Le DAX, c'est ce qui sépare un tableau de bord « joli » d'un tableau de bord qui **répond à une vraie question métier**. Concrètement, le DAX te permet de :

- créer des indicateurs qui **réagissent aux filtres** que l'utilisateur clique (région, mois, catégorie) ;
- comparer des périodes (cette année vs N-1, ce mois vs le mois dernier) **sans dupliquer tes données** ;
- calculer des ratios métier (marge %, panier moyen, taux de conversion) qui se recalculent dynamiquement.

Une mesure DAX bien écrite est réutilisable dans **tous** tes visuels et **toujours** correcte, quel que soit le découpage. C'est l'investissement qui rapporte le plus dans Power BI.

> **Analogie** — Le modèle (module 2.2) est le moteur de ta voiture. Le DAX, c'est l'accélérateur, le compteur et le GPS : ce avec quoi tu produis réellement de l'information.

---

## Contenu

### Qu'est-ce que le DAX ?

**DAX** = *Data Analysis Expressions*. C'est le langage de formules de Power BI (aussi présent dans Power Pivot et Analysis Services). Il ressemble visuellement aux formules Excel… mais raisonne **par tables et par colonnes**, jamais par cellule.

Différence mentale fondamentale :

- En **Excel**, tu écris `=A2*B2` : tu raisonnes **cellule par cellule**.
- En **DAX**, tu écris une formule qui s'applique à **toute une colonne / toute une table**, et qui se recalcule selon le **contexte** (les filtres actifs).

Une formule DAX produit soit une **colonne calculée**, soit une **mesure** (voir 3.2).

---

### Mesures vs colonnes calculées (différence cruciale)

C'est LA première erreur des débutants. Les deux s'écrivent en DAX, mais ne fonctionnent **pas du tout** pareil.

| | **Colonne calculée** | **Mesure** |
|---|---|---|
| **Quand est-ce calculé ?** | À l'actualisation des données (une fois) | À la volée, à chaque interaction / visuel |
| **Où c'est stocké ?** | Dans la table (occupe de la mémoire, ligne par ligne) | Rien n'est stocké (juste la formule) |
| **Contexte** | Contexte de **ligne** (voit la ligne courante) | Contexte de **filtre** (voit les filtres du visuel) |
| **Usage typique** | Catégoriser, créer une clé, un drapeau (`"Cher"/"Pas cher"`) | Agréger : CA, marge, moyenne, comptage |
| **Réagit aux filtres du visuel ?** | Non (figée) | Oui (dynamique) |

**Règle d'or** : *si le résultat doit s'agréger ou réagir aux filtres → mesure. Si tu as besoin d'une nouvelle valeur ligne par ligne (étiquette, segment) → colonne calculée.*

Exemple de **colonne calculée** (étiqueter chaque vente) :

```DAX
Segment Prix =
IF ( Ventes[Montant] >= 100, "Gros panier", "Petit panier" )
```

> Résultat attendu : une nouvelle colonne dans la table `Ventes`, avec `"Gros panier"` ou `"Petit panier"` sur **chaque ligne**.

Exemple de **mesure** (le CA total, dynamique) :

```DAX
CA Total = SUM ( Ventes[Montant] )
```

> Résultat attendu : une valeur unique qui change selon ce qui est filtré dans le visuel (1 250 000 € sur tout le jeu, 180 000 € si on filtre Lille, etc.).

> #### Encadré — Erreur courante n°1 : « j'ai fait une colonne au lieu d'une mesure »
> Symptôme classique : tu crées une « colonne CA » avec `SUM(Ventes[Montant])`. Résultat : **toutes les lignes affichent le même nombre géant** (le total global), et ça ne réagit à aucun filtre.
> Cause : `SUM` dans une colonne calculée n'a **pas** de contexte de ligne utile, il somme tout.
> Fix : un total agrégé est **toujours** une mesure, jamais une colonne.

---

### Où créer une mesure dans Power BI ?

Plusieurs chemins équivalents dans **Power BI Desktop** :

1. Dans le volet **Données** (à droite), **clic droit** sur la table qui doit porter la mesure (souvent ta table de faits `Ventes`) → **Nouvelle mesure**.
2. Ou ruban **Accueil** / **Modélisation** → bouton **Nouvelle mesure**.
3. Tu écris ta formule dans la **barre de formule** en haut (`Nom = formule`).
4. Valide avec **Entrée**. La mesure apparaît avec une icône **calculatrice** (∑/calculatrice) dans le volet Données.

Pour une **colonne calculée** : même volet, **Nouvelle colonne** (et tu dois être sur la bonne table).

> **Astuce pro** : regroupe toutes tes mesures dans une **table dédiée vide** (« Mesures ») pour t'y retrouver. Crée une table sans données via *Entrer des données*, puis déplaces-y tes mesures.

---

### Contexte de filtre vs contexte de ligne (notion clé)

Si tu ne devais retenir qu'une chose de ce module, c'est **ça**. 90 % des bugs DAX viennent d'une mauvaise compréhension du contexte.

**Le contexte de ligne** = « DAX sait sur quelle ligne il est ». Il existe naturellement dans une **colonne calculée** (chaque ligne est évaluée tour à tour) et dans les fonctions itératives (`SUMX`, `FILTER`…).

```DAX
-- Colonne calculée : contexte de ligne automatique
Total Ligne = Ventes[Quantite] * Ventes[Prix Unitaire]
```
> DAX lit `Quantite` et `Prix Unitaire` **de la ligne courante**. Logique.

**Le contexte de filtre** = « l'ensemble des filtres actifs au moment du calcul ». Il vient de :
- ce que l'utilisateur clique (segments, filtres),
- les axes du visuel (lignes/colonnes d'un tableau),
- les filtres écrits en DAX (via `CALCULATE`).

```DAX
CA Total = SUM ( Ventes[Montant] )
```
> Dans une carte simple → CA global. Dans un tableau par `Ville` → DAX recalcule le CA **pour chaque ville**, car chaque ligne du tableau crée un **contexte de filtre** « Ville = X ».

**Image mentale** : le contexte de filtre est une **paire de lunettes**. La mesure regarde toujours toutes les données, mais à travers les lunettes posées par le visuel : « ne montre que Lille », « ne montre que 2025 ». La mesure ne change pas, c'est la vue qui change.

> #### Encadré — Erreur courante n°2 : « pourquoi ma mesure affiche toujours le total ? »
> Tu mets `CA Total` dans une carte → 1,2 M€. Tu t'attendais au CA d'une ville mais la carte n'a **aucun** axe ni filtre : le contexte de filtre est « tout ». Pour voir le détail par ville, il faut un visuel qui **découpe** (tableau, graphe à barres avec `Ville` en axe) ou un segment cliqué.
> Le contexte ne se devine pas : il vient **toujours** d'un visuel ou d'un `CALCULATE`.

---

### Fonctions d'agrégation

Les briques de base. Toutes s'utilisent dans une **mesure**.

```DAX
CA Total          = SUM ( Ventes[Montant] )
Panier Moyen Brut = AVERAGE ( Ventes[Montant] )
Nb Lignes Vente   = COUNTROWS ( Ventes )
Nb Clients        = DISTINCTCOUNT ( Ventes[Client_ID] )
```

| Fonction | Ce qu'elle fait | Exemple retail |
|---|---|---|
| `SUM` | Somme d'une colonne numérique | CA total |
| `AVERAGE` | Moyenne d'une colonne numérique | Montant moyen d'une ligne de ticket |
| `COUNTROWS` | Compte les **lignes** d'une table | Nombre de transactions |
| `DISTINCTCOUNT` | Compte les **valeurs uniques** | Nombre de clients distincts |

> Résultat attendu (sur le jeu retail Nord, sans filtre) :
> `CA Total` = 1 250 000 € · `Nb Lignes Vente` = 48 300 · `Nb Clients` = 6 740.

> **Piège** : `COUNT` compte les valeurs **non vides** d'une colonne, `COUNTROWS` compte les **lignes** d'une table. Pour « combien de ventes ? », préfère `COUNTROWS(Ventes)`, plus clair et plus rapide.

---

### `CALCULATE` — la fonction reine

`CALCULATE` est **la seule** fonction qui peut **modifier le contexte de filtre**. C'est le couteau suisse du DAX, tu l'utiliseras partout.

Syntaxe :

```DAX
CALCULATE ( <expression> , <filtre1> , <filtre2> , ... )
```

> Elle calcule `<expression>` **après avoir appliqué** les filtres indiqués (qui s'ajoutent ou remplacent le contexte courant).

Exemple retail — CA du seul magasin de Lille :

```DAX
CA Lille =
CALCULATE (
    SUM ( Ventes[Montant] ),
    Magasins[Ville] = "Lille"
)
```
> Résultat attendu : même dans une carte sans filtre, affiche **180 000 €** (le CA de Lille uniquement), car `CALCULATE` a forcé le filtre `Ville = "Lille"`.

Exemple — CA hors retours :

```DAX
CA Net =
CALCULATE (
    SUM ( Ventes[Montant] ),
    Ventes[Type] <> "Retour"
)
```

Exemple — **retirer** un filtre avec `ALL` (très utile pour les % du total) :

```DAX
% du CA Total =
DIVIDE (
    SUM ( Ventes[Montant] ),
    CALCULATE ( SUM ( Ventes[Montant] ), ALL ( Magasins ) )
)
```
> `ALL(Magasins)` ignore le filtre sur les magasins → le dénominateur reste le CA **global**, même quand chaque ligne du tableau est filtrée sur une ville. Résultat : la part de chaque ville dans le CA total.

> #### Encadré — `DIVIDE` plutôt que `/`
> Utilise toujours `DIVIDE(a, b)` au lieu de `a / b`. `DIVIDE` gère la division par zéro (retourne vide au lieu d'une erreur). Indispensable pour les marges et évolutions.

---

### `FILTER`

`FILTER` renvoie une **table** réduite aux lignes qui respectent une condition. On l'emploie surtout **dans** `CALCULATE` quand la condition est complexe (comparaison à une mesure, plusieurs colonnes).

```DAX
CA Grosses Ventes =
CALCULATE (
    SUM ( Ventes[Montant] ),
    FILTER ( Ventes, Ventes[Montant] > 100 )
)
```
> Résultat attendu : CA réalisé uniquement sur les lignes de plus de 100 €.

Quand un simple `Ventes[Montant] > 100` suffit-il dans `CALCULATE` sans `FILTER` ? Pour une condition sur **une seule colonne** comparée à une **valeur fixe**, `CALCULATE(..., Ventes[Montant] > 100)` marche (c'est un raccourci que DAX transforme en `FILTER` en interne). `FILTER` explicite devient nécessaire dès que tu compares à **une mesure** ou que la logique porte sur **plusieurs colonnes**.

> #### Encadré — Erreur courante n°3 : `FILTER` sur une table trop grosse
> `FILTER(Ventes, ...)` parcourt **toute** la table ligne à ligne → lent sur de gros volumes. Si tu peux exprimer le filtre comme une simple condition de colonne, fais-le directement dans `CALCULATE` (plus rapide). Réserve `FILTER` aux cas qui l'exigent.

---

### Time intelligence — calculs YoY / MoM

Ces fonctions exigent une **vraie table de dates** continue, marquée comme **« Table de dates »** dans le modèle (vu en 2.2), reliée à ta table de faits.

**Cumul depuis le 1er janvier (Year-To-Date)** :

```DAX
CA YTD =
TOTALYTD (
    SUM ( Ventes[Montant] ),
    Calendrier[Date]
)
```
> Résultat attendu : au 31 mars, affiche le CA cumulé du 1er janvier au 31 mars.

**Même période l'an dernier (pour le comparatif N-1)** :

```DAX
CA N-1 =
CALCULATE (
    SUM ( Ventes[Montant] ),
    SAMEPERIODLASTYEAR ( Calendrier[Date] )
)
```
> Résultat attendu : si le contexte est « mars 2025 », renvoie le CA de **mars 2024**.

**Évolution N-1 en %** (le YoY que tout commanditaire réclame) :

```DAX
Évolution N-1 % =
VAR CaActuel = SUM ( Ventes[Montant] )
VAR CaN1 = CALCULATE ( SUM ( Ventes[Montant] ), SAMEPERIODLASTYEAR ( Calendrier[Date] ) )
RETURN
    DIVIDE ( CaActuel - CaN1, CaN1 )
```
> Résultat attendu : `+0,12` (→ format pourcentage = **+12 %**) si le CA a progressé de 12 % vs l'an dernier.

**Mois précédent (pour le MoM)** avec `DATEADD` :

```DAX
CA Mois Précédent =
CALCULATE (
    SUM ( Ventes[Montant] ),
    DATEADD ( Calendrier[Date], -1, MONTH )
)
```
> `DATEADD(..., -1, MONTH)` décale le contexte d'un mois en arrière. Mets `-1, YEAR` pour un décalage d'un an, `-7, DAY` pour une semaine, etc. Très souple.

> #### Encadré — Erreur courante n°4 : la time intelligence « ne marche pas »
> Causes les plus fréquentes :
> 1. Pas de **table de dates dédiée** (tu utilises la date de la table de faits directement) → crée une table `Calendrier` continue.
> 2. La table n'est **pas marquée** comme table de dates (clic droit sur la table → *Marquer comme table de dates*).
> 3. Des **trous** dans les dates (jours manquants) faussent les cumuls : la table de dates doit être **continue**, sans manque.

---

### Variables DAX (`VAR` / `RETURN`)

Les variables rendent le DAX **lisible**, **plus rapide** (un calcul fait une fois est réutilisé) et plus facile à déboguer.

Syntaxe :

```DAX
Ma Mesure =
VAR Truc = <calcul>
VAR Machin = <autre calcul>
RETURN
    <expression utilisant Truc et Machin>
```

Exemple — marge en % avec variables (lisible) :

```DAX
Marge % =
VAR CA = SUM ( Ventes[Montant] )
VAR Cout = SUM ( Ventes[Cout_Achat] )
RETURN
    DIVIDE ( CA - Cout, CA )
```
> Résultat attendu : `0,34` → format % = **34 %** de marge.

> **Avantages des `VAR`** : (1) tu lis la formule comme une recette ; (2) `CaActuel` calculé une fois est réutilisé deux fois sans recalcul ; (3) pour déboguer, tu mets temporairement `RETURN CaActuel` pour vérifier une étape.
>
> **Piège** : une `VAR` est figée **au moment où elle est définie**. Elle ne « voit » pas un `CALCULATE` qui viendrait après. Si tu veux un montant N-1, calcule-le **dans** une `VAR` avec son propre `CALCULATE` (comme ci-dessus), n'essaie pas de modifier le contexte d'une variable déjà fixée.

---

### Les mesures retail usuelles (à connaître par cœur)

Le kit de survie du Data Analyst retail. Mets-les dans ta table `Mesures`.

```DAX
CA Total = SUM ( Ventes[Montant] )

Coût Total = SUM ( Ventes[Cout_Achat] )

Marge = [CA Total] - [Coût Total]

Marge % = DIVIDE ( [Marge], [CA Total] )

Nb Transactions = DISTINCTCOUNT ( Ventes[Ticket_ID] )

Panier Moyen = DIVIDE ( [CA Total], [Nb Transactions] )

CA N-1 =
CALCULATE ( [CA Total], SAMEPERIODLASTYEAR ( Calendrier[Date] ) )

Évolution N-1 % =
DIVIDE ( [CA Total] - [CA N-1], [CA N-1] )
```

> Note : on **réutilise** les mesures entre elles (`[Marge]` appelle `[CA Total]`). C'est la bonne pratique : tu corriges `[CA Total]` une fois, tout suit.
>
> `Panier Moyen` = CA / **nombre de tickets** (transactions distinctes), pas la moyenne ligne à ligne. Un ticket contient souvent plusieurs lignes → ne confonds pas `AVERAGE(Ventes[Montant])` (moyenne par ligne) et le vrai panier moyen (par ticket).

---

## Travaux pratiques

> Contexte commun : jeu de données **retail Nord** avec une table de faits `Ventes` (`Ticket_ID`, `Client_ID`, `Montant`, `Cout_Achat`, `Quantite`, `Type`, `Date`, `Magasin_ID`), une dimension `Magasins` (`Magasin_ID`, `Ville`), une dimension `Produits`, et une table `Calendrier` marquée comme table de dates. Crée toutes les mesures dans une table `Mesures`.

### TP1 — Les agrégations de base
Crée 4 mesures : `CA Total`, `Nb Transactions` (tickets distincts), `Nb Clients` (clients distincts), `Panier Moyen`.

<details><summary>Corrigé</summary>

```DAX
CA Total = SUM ( Ventes[Montant] )

Nb Transactions = DISTINCTCOUNT ( Ventes[Ticket_ID] )

Nb Clients = DISTINCTCOUNT ( Ventes[Client_ID] )

Panier Moyen = DIVIDE ( [CA Total], [Nb Transactions] )
```
Le panier moyen se calcule **par ticket** (transaction), pas par ligne. On réutilise `[CA Total]` et `[Nb Transactions]`.
</details>

### TP2 — Marge et marge %
Crée `Coût Total`, `Marge` (€) et `Marge %`. Affiche `Marge %` au format pourcentage.

<details><summary>Corrigé</summary>

```DAX
Coût Total = SUM ( Ventes[Cout_Achat] )

Marge = [CA Total] - [Coût Total]

Marge % = DIVIDE ( [Marge], [CA Total] )
```
Format : sélectionne `Marge %` → onglet *Outils de mesure* → format **Pourcentage**. On utilise `DIVIDE` (jamais `/`) pour éviter l'erreur si `[CA Total]` vaut 0.
</details>

### TP3 — `CALCULATE` : CA d'une ville et CA hors retours
1. Crée `CA Lille` (CA du seul magasin de Lille).
2. Crée `CA Net` (CA en excluant les lignes `Type = "Retour"`).

<details><summary>Corrigé</summary>

```DAX
CA Lille =
CALCULATE ( [CA Total], Magasins[Ville] = "Lille" )

CA Net =
CALCULATE ( [CA Total], Ventes[Type] <> "Retour" )
```
`CALCULATE` modifie le contexte de filtre. `CA Lille` reste figé sur Lille même sans segment ; `CA Net` retire les retours partout.
</details>

### TP4 — Part de chaque ville dans le CA (avec `ALL`)
Crée `% CA Ville` : la part du CA d'une ville rapportée au CA total, même quand un tableau découpe par ville.

<details><summary>Corrigé</summary>

```DAX
% CA Ville =
DIVIDE (
    [CA Total],
    CALCULATE ( [CA Total], ALL ( Magasins ) )
)
```
`ALL(Magasins)` retire le filtre sur les magasins → le dénominateur reste le CA **global**. Dans un tableau par `Ville`, le numérateur est filtré ville par ville, le dénominateur non → on obtient bien un pourcentage qui somme à 100 %.
</details>

### TP5 — Comparatif N-1 et évolution YoY
1. Crée `CA N-1` (même période l'an dernier).
2. Crée `Évolution N-1 %` avec des variables `VAR`.

<details><summary>Corrigé</summary>

```DAX
CA N-1 =
CALCULATE ( [CA Total], SAMEPERIODLASTYEAR ( Calendrier[Date] ) )

Évolution N-1 % =
VAR CaActuel = [CA Total]
VAR CaPrec   = [CA N-1]
RETURN
    DIVIDE ( CaActuel - CaPrec, CaPrec )
```
Exige une table `Calendrier` continue et marquée comme table de dates. `SAMEPERIODLASTYEAR` décale le contexte d'un an. `DIVIDE` protège le cas où `[CA N-1]` est vide (premier exercice de l'historique).
</details>

### TP6 — Cumul YTD et CA des grosses ventes (`FILTER`)
1. Crée `CA YTD` (cumul depuis le 1er janvier).
2. Crée `CA Grosses Ventes` : CA des lignes de plus de 100 €, via `FILTER`.

<details><summary>Corrigé</summary>

```DAX
CA YTD =
TOTALYTD ( [CA Total], Calendrier[Date] )

CA Grosses Ventes =
CALCULATE (
    [CA Total],
    FILTER ( Ventes, Ventes[Montant] > 100 )
)
```
`TOTALYTD` cumule sur l'année courante du contexte. Pour `CA Grosses Ventes`, la condition porte sur une colonne comparée à une valeur fixe : ici `FILTER` est pédagogique, mais `CALCULATE([CA Total], Ventes[Montant] > 100)` ferait aussi l'affaire et serait plus rapide.
</details>

---

## Vidéos d'auto-formation

> Les liens YouTube ci-dessous ont été vérifiés. Si une vidéo a été retirée, utilise le lien de recherche fourni.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Power BI - Les 5 mesures DAX à connaître | Mandarine Academy | FR | ~10 min | https://www.youtube.com/watch?v=i6PcaXqal9k | Tour des mesures DAX incontournables (SUM, CALCULATE, etc.) pour démarrer vite |
| DAX pour débutants (recherche) | — | FR | varié | https://www.youtube.com/results?search_query=DAX+power+bi+d%C3%A9butant+CALCULATE+fran%C3%A7ais | Bases du DAX, mesures, CALCULATE expliqués en français |
| DAX - Basics Of Filter Context and Calculate | (chaîne PBI) | EN | ~15 min | https://www.youtube.com/watch?v=pUCpxJdlvQ0 | Le contexte de filtre et comment CALCULATE le modifie (concept clé) |
| Power BI DAX for Beginners #9: Time Intelligence (SAMEPERIODLASTYEAR, DATEADD, TOTALYTD) | (série Beginners) | EN | ~20 min | https://www.youtube.com/watch?v=1UdswHPRE2c | Calculs temporels YoY/YTD pas à pas |
| Time Intelligence in DAX - TOTALYTD, TOTALQTD, TOTALMTD | (PBI Tutorial) | EN | ~15 min | https://www.youtube.com/watch?v=Oea2HV5cOcs | Les fonctions de cumul (YTD/QTD/MTD) en détail |

> Ressources écrites de référence (à garder en favoris) : [SQLBI — Introducing CALCULATE](https://www.sqlbi.com/articles/introducing-calculate-in-dax/), [SQLBI — Filter context expliqué visuellement](https://www.sqlbi.com/articles/filter-context-in-dax-explained-visually/), [dax.guide](https://dax.guide/), [Microsoft Learn — Principes fondamentaux DAX](https://learn.microsoft.com/fr-fr/power-bi/transform-model/desktop-quickstart-learn-dax-basics).

---

## Quiz (5 QCM)

**Q1.** Quelle est la bonne approche pour calculer le chiffre d'affaires total qui réagit aux filtres ?
- A. Une colonne calculée avec `SUM`
- B. Une mesure avec `SUM`
- C. Une colonne calculée avec `IF`
- D. Un champ tiré directement dans le visuel

**Q2.** Quelle est la **seule** fonction DAX capable de modifier le contexte de filtre ?
- A. `FILTER`
- B. `SUM`
- C. `CALCULATE`
- D. `ALL`

**Q3.** Tu veux le CA de la même période l'an dernier. Quelle fonction ?
- A. `DATEADD(..., -1, DAY)`
- B. `TOTALYTD`
- C. `SAMEPERIODLASTYEAR`
- D. `COUNTROWS`

**Q4.** Pourquoi privilégier `DIVIDE(a, b)` plutôt que `a / b` ?
- A. C'est plus rapide à écrire
- B. `DIVIDE` gère la division par zéro sans erreur
- C. `a / b` est interdit en DAX
- D. `DIVIDE` arrondit automatiquement

**Q5.** Une colonne calculée `CA = SUM(Ventes[Montant])` affiche le même grand nombre sur toutes les lignes. Pourquoi ?
- A. `SUM` est buggé
- B. Il manque un `CALCULATE`
- C. Dans une colonne calculée, `SUM` somme toute la table, sans contexte de filtre utile : c'était à faire en mesure
- D. La table n'a pas de relation

<details><summary>Réponses</summary>

**Q1 → B.** Un total qui réagit aux filtres est **toujours** une mesure.
**Q2 → C.** `CALCULATE` (et `CALCULATETABLE`) est la seule à modifier le contexte de filtre ; `FILTER`/`ALL` n'agissent qu'**à l'intérieur** d'un `CALCULATE`.
**Q3 → C.** `SAMEPERIODLASTYEAR` renvoie la même période l'année précédente.
**Q4 → B.** `DIVIDE` retourne vide (pas une erreur) si le dénominateur est 0.
**Q5 → C.** C'est l'erreur mesure vs colonne : un agrégat se fait en mesure, pas en colonne.
</details>

---

## À retenir (mémo fonctions)

| Besoin | Fonction(s) | Exemple court |
|---|---|---|
| Somme | `SUM` | `SUM(Ventes[Montant])` |
| Moyenne | `AVERAGE` | `AVERAGE(Ventes[Montant])` |
| Compter des lignes | `COUNTROWS` | `COUNTROWS(Ventes)` |
| Compter des valeurs uniques | `DISTINCTCOUNT` | `DISTINCTCOUNT(Ventes[Client_ID])` |
| Diviser sans erreur | `DIVIDE` | `DIVIDE([Marge],[CA Total])` |
| Modifier le contexte de filtre | `CALCULATE` | `CALCULATE([CA Total], Magasins[Ville]="Lille")` |
| Ignorer un filtre | `ALL` | `CALCULATE([CA Total], ALL(Magasins))` |
| Filtrer une table | `FILTER` | `FILTER(Ventes, Ventes[Montant]>100)` |
| Cumul année en cours | `TOTALYTD` | `TOTALYTD([CA Total], Calendrier[Date])` |
| Même période N-1 | `SAMEPERIODLASTYEAR` | `CALCULATE([CA Total], SAMEPERIODLASTYEAR(Calendrier[Date]))` |
| Décaler une période | `DATEADD` | `DATEADD(Calendrier[Date], -1, MONTH)` |
| Variables lisibles | `VAR` / `RETURN` | `VAR x = ... RETURN ...` |

**Les 3 réflexes à graver :**
1. **Agrégat ou réaction aux filtres → mesure.** Étiquette ligne à ligne → colonne calculée.
2. **Le contexte de filtre vient du visuel** (ou de `CALCULATE`). Rien ne se calcule « tout seul ».
3. **Time intelligence → table de dates** continue, dédiée et marquée comme telle. Sinon ça casse.
