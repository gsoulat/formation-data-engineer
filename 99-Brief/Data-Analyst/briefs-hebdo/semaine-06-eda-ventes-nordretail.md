# Brief S06 — Auditer et explorer les ventes de NordRetail avec pandas (EDA)

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S06 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant → intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, matplotlib, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Extraction SQL](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/) · [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) · [Module EDA](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, mais son équipe data est naissante — vous en faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion.

### Le problème

La direction commerciale veut se doter d'un **tableau de bord de pilotage** pour suivre l'activité des points de vente. Mais avant de calculer le moindre indicateur, un doute plane : **les données d'export sont-elles fiables ?** Lors d'une réunion, la contrôleuse de gestion a repéré des montants qui « ne tombaient pas juste », et le responsable BI soupçonne des lignes en double après une migration d'outil de caisse.

Construire un dashboard sur des données non auditées, c'est prendre le risque de piloter l'enseigne sur des chiffres faux. Votre mission de la semaine intervient donc **en amont** du projet de tableau de bord : établir un **diagnostic de confiance** sur les données de ventes et en tirer les premiers enseignements métier.

### La question centrale

Toute la semaine, chaque analyse que vous produisez doit contribuer à répondre à la question que la direction vous a posée :

> **« Peut-on faire confiance aux données de ventes de NordRetail — et que racontent-elles déjà sur l'activité de l'enseigne ? »**

### Les données

Un seul fichier d'export cette semaine, mais bien réel et pas parfait :

- [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) — **12 000 lignes** de ventes détaillées. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

Le fichier couvre plusieurs mois d'activité. Comme tout export de production, il peut contenir des trous, des doublons ou des valeurs incohérentes : c'est précisément ce que vous devez détecter.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Auditer la qualité d'un jeu de données réel** : mesurer la complétude (valeurs manquantes), les doublons et la cohérence métier (montants négatifs, quantités nulles, remises hors bornes).
- **Produire et interpréter des statistiques descriptives** : tendance centrale (moyenne, médiane), dispersion (écart-type, quartiles) et savoir choisir l'indicateur qui décrit le mieux une réalité métier.
- **Agréger des données selon des dimensions métier** avec `groupby` (par ville, catégorie, canal de vente) et hiérarchiser les résultats.
- **Construire des visualisations exploratoires lisibles** : histogramme, diagramme en barres, chacun titré et interprétable sans explication orale.
- **Synthétiser des constats analytiques** dans un rapport destiné à un lecteur métier non technique.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_magasins.csv`](../data/ventes_magasins.csv). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur ce fichier ; vos éventuelles corrections restent dans le notebook (on ne modifie jamais la source).

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook et son propre rapport. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et prise en main, SANS analyse chiffrée (J1)

Avant de coder, appropriez-vous le sujet. Ouvrez le fichier dans un tableur pour un premier regard : que représente une ligne ? une vente unitaire, un panier, une ligne de ticket ? Rédigez en quelques phrases ce que vous attendez de « données saines » pour chaque colonne — par exemple, un `montant` peut-il légitimement être négatif (un retour ?), une `remise` supérieure à 1 a-t-elle un sens ? Ces hypothèses guideront votre audit. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Audit de qualité des données (J1-J2)

Chargez le fichier avec pandas en typant correctement la date (`parse_dates`). Établissez le **profil de qualité** : volume (`shape`), types (`dtypes`), période couverte (`date.min()` / `max()`), valeurs manquantes par colonne, doublons de lignes. Confrontez ensuite les données à vos hypothèses de la Phase 1 : cherchez les `montant`, `quantite` ou `prix_unitaire` négatifs ou nuls, les remises aberrantes. Chaque anomalie détectée doit être **documentée** (combien de lignes ? quelle proportion ? hypothèse sur la cause : erreur de saisie, retour client, bug d'export ?). Comment décideriez-vous, à ce stade, s'il faut écarter ou conserver ces lignes ?

### Phase 3 — Statistiques descriptives et profil de l'activité (J2-J3)

Décrivez la distribution des ventes. Pour `montant` et `quantite` : moyenne, médiane, écart-type, quartiles. La moyenne et la médiane du `montant` sont-elles proches ? Si elles s'écartent nettement, qu'est-ce que cela révèle sur la forme de la distribution, et quel indicateur recommanderiez-vous à la direction pour parler du « panier typique » ? Repérez les valeurs extrêmes et interrogez-les : promotion exceptionnelle, achat professionnel, ou erreur ?

### Phase 4 — Agrégations métier et visualisations (J3-J4)

Faites parler les dimensions. Calculez le chiffre d'affaires (`montant`) agrégé par **ville**, par **catégorie** et par **canal** (Magasin vs E-commerce), triés du plus fort au plus faible. Produisez au moins **trois visualisations** claires et titrées : un histogramme de `montant`, un diagramme en barres du CA par ville, un du CA par catégorie. Quelle ville porte l'activité ? Quelle catégorie ? Le e-commerce pèse-t-il autant que les magasins ? Chaque graphique doit pouvoir être lu seul, sans commentaire oral.

### Phase 5 — Synthèse, rapport et mise en ligne (J5)

Rédigez un **rapport de synthèse** (8 à 15 lignes) qui répond frontalement à la question centrale : peut-on faire confiance à ces données (et sous quelles réserves), et quels sont les 3 à 5 premiers enseignements métier ? Ce rapport s'adresse à la direction : pas de jargon Python, des phrases actionnables. Nettoyez votre notebook (il doit s'exécuter de haut en bas sans erreur), soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : audit qualité documenté, statistiques descriptives interprétées, 3 agrégations, 3 graphiques titrés, rapport de synthèse, dépôt public à jour.

### Pour aller plus loin (bonus)

- Analysez la **saisonnalité** : le CA par mois révèle-t-il des pics (soldes, fêtes) ?
- Croisez deux dimensions (`groupby(["ville", "categorie"])`) pour trouver le couple ville × catégorie le plus rentable.
- Comparez `ventes_magasins.csv` à `ventes_corrompu.csv` (présent dans `data/`) : quelles dégradations supplémentaires votre audit détecte-t-il ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `eda_ventes.ipynb` — notebook exécuté de bout en bout (code + graphiques + cellules d'analyse) ;
  - un **rapport de synthèse** (`SYNTHESE.md` ou PDF) rédigé pour un lecteur métier ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Une **fiche de qualité des données** (tableau récapitulatif des anomalies : type, volume, décision proposée) — dans le notebook ou le rapport.

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook et rapport (60 %)** : rigueur de l'audit, justesse des statistiques et des interprétations, lisibilité des visualisations, qualité du rapport de synthèse.
- **Restitution orale (40 %)** : 10 minutes de présentation des constats à un « comité de direction » (le formateur et un autre binôme) + 5 minutes de questions.

**Validation partielle** : un binôme dont le notebook n'est pas complètement finalisé mais dont l'audit et le raisonnement statistique sont structurés et documentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Auditer la qualité des données**
- Le fichier est chargé avec les bons types (`date` en datetime, numériques cohérents).
- Valeurs manquantes, doublons et incohérences métier sont mesurés ET commentés (volume + hypothèse de cause).
- Une décision argumentée est proposée pour les lignes problématiques (garder / écarter / corriger).

**Produire des statistiques descriptives**
- Moyenne, médiane, écart-type et quartiles de `montant` sont calculés.
- L'écart moyenne/médiane est interprété et un indicateur est recommandé avec justification.
- Les valeurs extrêmes sont identifiées et questionnées.

**Agréger et visualiser**
- Au moins 3 agrégations `groupby` pertinentes (ville, catégorie, canal) sont produites et triées.
- Au moins 3 graphiques titrés, lisibles de façon autonome, sont générés.
- Les visualisations sont correctement rattachées à une question métier.

**Restituer**
- Le rapport de synthèse répond explicitement à la question centrale.
- Il est rédigé sans jargon technique, avec des constats actionnables.
- Le dépôt GitHub public est complet (notebook exécutable + README).

## Ressources

- Module de cours — [Analyse exploratoire (EDA)](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/)
- Rappels — [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/)
- Documentation pandas : https://pandas.pydata.org/docs/
- Documentation matplotlib : https://matplotlib.org/stable/
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
