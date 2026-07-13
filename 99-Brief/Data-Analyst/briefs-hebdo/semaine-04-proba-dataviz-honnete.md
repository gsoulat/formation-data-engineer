# Brief S04 — Dataviz honnête et probabilités appliquées aux ventes de NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S04 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant → intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, matplotlib, scipy.stats, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) · [Probabilités](../../../01-Fondamentaux/Mathematiques/04-Probabilites/) · [Maths pour la dataviz](../../../01-Fondamentaux/Mathematiques/06-Mathematiques-Dataviz/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, mais son équipe data est naissante — vous en faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion. Le tableau de bord de pilotage se construit semaine après semaine ; cette fois, on s'intéresse à la manière dont les chiffres seront **montrés** à la direction, et à ce que la statistique permet d'en **anticiper**.

### Le problème

Le directeur marketing prépare le prochain comité et réclame « un graphe qui montre que nos ventes explosent ». Le responsable BI, lui, s'inquiète : un même jeu de données peut produire un graphique parfaitement honnête ou un graphique délibérément flatteur, et personne dans l'équipe ne sait encore expliquer clairement la différence. Le risque est double : diffuser en interne des visualisations trompeuses qui fausseront les décisions, et se laisser abuser par les graphiques orientés des fournisseurs.

En parallèle, la contrôleuse de gestion voudrait pouvoir répondre à des questions de type « à quelle fréquence une journée dépasse-t-elle tel niveau de recettes ? » — non pas en comptant a posteriori, mais en **modélisant** la variabilité des ventes. Votre mission de la semaine consiste donc à outiller l'équipe sur deux fronts : produire des visualisations **honnêtes** (et savoir démasquer celles qui ne le sont pas), et poser les premières **estimations probabilistes** sur l'activité.

### La question centrale

Toute la semaine, chaque graphique et chaque calcul que vous produisez doit contribuer à répondre à la question que la direction vous a posée :

> **« Comment montrer et estimer honnêtement l'activité de NordRetail, sans tromper le lecteur ni se laisser tromper ? »**

### Les données

Un seul fichier d'export cette semaine, le même que celui déjà connu de l'équipe :

- [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) — **12 000 lignes** de ventes détaillées. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

Le fichier couvre plusieurs mois d'activité. Il vous servira à la fois de matière pour vos visualisations (une série agrégée par période ou par magasin) et de base pour vos calculs de probabilité (moyenne et écart-type du montant journalier).

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Construire une visualisation honnête** : axe des ordonnées partant de zéro, échelle régulière, titre neutre et factuel, graphique lisible sans commentaire oral.
- **Identifier et reproduire les pièges d'une visualisation trompeuse** : axe tronqué, échelle déformée, titre orienté, sélection partielle de la période, ordre des barres manipulé — et expliquer comment un lecteur les repère.
- **Appliquer une loi normale** à une question métier : calculer, à partir de la moyenne et de l'écart-type observés, la probabilité qu'une journée de ventes dépasse un seuil donné avec `scipy.stats.norm`.
- **Questionner une hypothèse statistique** : confronter la forme réelle de la distribution des ventes à l'hypothèse de normalité, et en énoncer les limites.
- **Restituer une position argumentée** sur les bonnes pratiques de visualisation, destinée à un lecteur métier non technique.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_magasins.csv`](../data/ventes_magasins.csv). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur ce fichier ; vos agrégations et transformations restent dans le notebook (on ne modifie jamais la source).

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook et sa propre synthèse. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et prise en main, SANS analyse chiffrée (J1)

Avant de coder, appropriez-vous le sujet. Ouvrez le fichier dans un tableur pour un premier regard et posez-vous la question de la maille : à partir de ce détail de lignes, quelle **série** allez-vous construire pour comparer une évolution — un chiffre d'affaires par mois, par ville, par jour ? Réfléchissez ensuite à ce qui rend un graphique loyal : pourquoi un axe des ventes qui ne part pas de zéro peut-il faire « exploser » visuellement une croissance modeste ? Un titre comme « Des ventes qui explosent ! » relève-t-il du constat ou de l'interprétation ? Listez, en quelques phrases, les pièges que vous connaissez déjà et l'effet que chacun produit sur l'œil du lecteur. Ces hypothèses guideront votre travail de la semaine. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Préparer la série et bâtir la visualisation honnête (J1-J2)

Chargez le fichier avec pandas en typant correctement la date (`parse_dates`). Agrégez les ventes pour obtenir une **série comparable** : par exemple le `montant` total par mois, ou le CA par ville — l'important est d'obtenir un support de comparaison propre. Produisez ensuite une **première visualisation honnête** : barres ou courbe, **axe des ordonnées partant de zéro**, échelle régulière, titre neutre et factuel qui décrit ce que montre le graphique sans le commenter. Vérifiez qu'un lecteur découvrant ce graphique isolé comprendrait l'évolution réelle sans être orienté.

### Phase 3 — Construire la visualisation trompeuse et la décrypter (J2-J3)

À partir des **mêmes données exactement**, produisez une seconde version délibérément trompeuse cumulant **au moins deux pièges** parmi : axe des ordonnées tronqué (ne partant pas de zéro), échelle déformée ou non linéaire, titre orienté, sélection partielle de la période pour ne garder que la partie flatteuse, ordre des barres manipulé. Sous chaque graphique, rédigez 3 à 4 lignes de décryptage : quel piège est employé, quel effet il produit, et surtout **comment un lecteur attentif peut le repérer** (par exemple : vérifier l'origine de l'axe, comparer l'écart réel des valeurs, se méfier d'un titre qui conclut à la place du lecteur). L'enjeu n'est pas de « bien mentir » mais de rendre le mensonge visible et démontable.

### Phase 4 — Probabilités appliquées : loi normale sur les ventes (J3-J4)

Passez de la description à l'estimation. Calculez la **moyenne** et l'**écart-type** du montant des ventes journalières (agrégez le `montant` par jour, puis décrivez cette série). En supposant les ventes journalières approximativement normales, répondez avec `scipy.stats.norm` à une question du type : *« quelle est la probabilité qu'une journée dépasse X € de recettes ? »* — choisissez un seuil X pertinent au regard de la distribution observée et justifiez-le. Interprétez le résultat en langage métier. Puis prenez du recul : tracez la distribution réelle des ventes journalières (histogramme) et confrontez-la à la courbe normale théorique. L'hypothèse de normalité tient-elle ? Où et pourquoi s'écarte-t-elle de la réalité (asymétrie, valeurs extrêmes, effet des soldes) ? Énoncez clairement cette limite.

### Phase 5 — Synthèse, note de bonnes pratiques et mise en ligne (J5)

Rédigez une **note de synthèse** (8 à 15 lignes) qui répond frontalement à la question centrale et propose à l'équipe une courte charte : *« comment garder nos visualisations honnêtes chez NordRetail »* (règles concrètes : axe à zéro par défaut, titre factuel, période complète, échelle régulière, mention des hypothèses derrière une estimation probabiliste). Cette note s'adresse à la direction : pas de jargon Python, des recommandations actionnables. Nettoyez votre notebook (il doit s'exécuter de haut en bas sans erreur), soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : série agrégée propre, une visualisation honnête et une visualisation trompeuse sur les **mêmes données**, décryptage des pièges avec méthode de repérage, calcul de probabilité par la loi normale commenté et limité, note de bonnes pratiques, dépôt public à jour.

### Pour aller plus loin (bonus)

- Produisez un **troisième graphique** volontairement piégé sur une autre dimension (CA par ville avec ordre des barres manipulé) et faites deviner le piège à l'autre binôme.
- Comparez la probabilité obtenue sous hypothèse normale à un **comptage empirique direct** (proportion réelle de journées au-dessus du seuil) : l'écart confirme-t-il votre critique de l'hypothèse de normalité ?
- Refaites l'exercice honnête/trompeur sur [`../data/ventes_consolidees.csv`](../data/ventes_consolidees.csv) et vérifiez que vos règles de repérage tiennent sur un autre export.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `dataviz_honnete.ipynb` — notebook exécuté de bout en bout (code + les deux graphiques + décryptages + calcul probabiliste + cellules d'analyse) ;
  - une **note de synthèse** (`SYNTHESE.md` ou PDF) rédigée pour un lecteur métier, incluant la mini-charte de bonnes pratiques ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Les **deux visualisations comparées** (honnête vs trompeuse) présentées côte à côte ou successivement, chacune avec son décryptage.

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook et note de synthèse (60 %)** : rigueur de la comparaison honnête/trompeuse, pertinence des pièges et de leur méthode de repérage, justesse du calcul probabiliste et de sa critique, qualité de la note de bonnes pratiques.
- **Restitution orale (40 %)** : 10 minutes de présentation à un « comité de direction » (le formateur et un autre binôme) — vous projetez les deux graphiques et démontez le trompeur en direct — + 5 minutes de questions.

**Validation partielle** : un binôme dont le notebook n'est pas complètement finalisé mais dont la comparaison honnête/trompeuse et le raisonnement probabiliste sont structurés et documentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Construire des visualisations pertinentes et honnêtes**
- Les deux graphiques utilisent exactement les **mêmes données**.
- La version honnête a un axe des ordonnées partant de zéro, une échelle régulière et un titre neutre.
- Chaque graphique est titré et lisible de façon autonome, sans commentaire oral.

**Démasquer une visualisation trompeuse**
- La version trompeuse contient **au moins deux pièges** clairement identifiés (dont l'axe tronqué).
- Chaque piège est expliqué ET la méthode pour le repérer côté lecteur est donnée.

**Appliquer une loi de probabilité**
- La moyenne et l'écart-type des ventes journalières sont calculés.
- La probabilité de dépassement d'un seuil est calculée avec `scipy.stats.norm`, avec un seuil justifié.
- L'hypothèse de normalité est confrontée à la distribution réelle et sa limite est énoncée.

**Restituer**
- La note de synthèse répond explicitement à la question centrale et propose une charte de bonnes pratiques.
- Elle est rédigée sans jargon technique, avec des recommandations actionnables.
- Le dépôt GitHub public est complet (notebook exécutable + README).

## Ressources

- Module de cours — [Maths pour la dataviz](../../../01-Fondamentaux/Mathematiques/06-Mathematiques-Dataviz/)
- Rappels — [Probabilités](../../../01-Fondamentaux/Mathematiques/04-Probabilites/) · [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/)
- Documentation `scipy.stats.norm` : https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
- Documentation matplotlib : https://matplotlib.org/stable/
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
