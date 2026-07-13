# Brief S03 — Poser les fondations statistiques des ventes de NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S03 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, matplotlib/seaborn, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) · [Extraction SQL](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/) · [Module EDA](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, mais son équipe data est naissante — vous venez d'y être intégrés, aux côtés d'un responsable BI et d'une contrôleuse de gestion.

### Le problème

La direction ambitionne à moyen terme un **tableau de bord de pilotage** pour suivre l'activité des points de vente. C'est un chantier de plusieurs semaines, et il ne peut pas démarrer sur du sable : avant de brancher le moindre indicateur, l'équipe doit savoir **parler chiffres** de manière rigoureuse. Or, la première question posée par le contrôleur de gestion sur le tchat de l'équipe est déjà piégeuse : *« On vend combien en moyenne par jour, et pourquoi certaines journées semblent complètement à côté de la plaque ? »*

Répondre « en moyenne » sans réfléchir, c'est risquer de tromper la direction : une poignée de journées exceptionnelles (soldes, gros achat professionnel) peut gonfler la moyenne et donner une image fausse du quotidien. Votre mission de la semaine intervient donc **tout en amont** du projet de tableau de bord : établir un **socle statistique fiable** sur les ventes, en distinguant clairement ce qui est « typique » de ce qui est « exceptionnel ».

### La question centrale

Toute la semaine, chaque calcul que vous produisez doit contribuer à répondre à la question que le contrôleur de gestion vous a posée :

> **« À combien s'élève une journée de ventes "normale" chez NordRetail — et que faut-il faire des journées qui sortent du lot ? »**

### Les données

Un seul fichier d'export cette semaine, volontairement **propre** : le nettoyage viendra dans les semaines suivantes, ici on se concentre sur la statistique.

- [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) — **12 000 lignes** de ventes détaillées. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

Le fichier couvre plusieurs mois d'activité. Vous n'aurez pas de gros nettoyage à faire, mais des valeurs extrêmes bien réelles s'y cachent : c'est justement leur interprétation qui fait tout l'intérêt de la semaine.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Explorer un jeu de données** pour en dresser un premier profil : volume, colonnes, types, aperçu des valeurs (`info()`, `describe()`, `head()`).
- **Calculer et distinguer les indicateurs de tendance centrale** — moyenne, médiane, mode — et savoir lequel décrit le mieux une réalité métier.
- **Mesurer la dispersion d'une distribution** : étendue, variance, écart-type, quartiles (Q1, Q3) et écart interquartile (IQR).
- **Visualiser une distribution** avec un histogramme et une boîte à moustaches, chacun titré et interprétable sans explication orale.
- **Détecter les valeurs aberrantes par une méthode reproductible** (règle de l'IQR) plutôt qu'« à l'œil », et décider de leur sort de façon argumentée.
- **Traduire des résultats statistiques en langage métier** dans une note destinée à un lecteur non technique.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_magasins.csv`](../data/ventes_magasins.csv). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur ce fichier : on ne modifie jamais la source, tous vos calculs restent dans le notebook.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook et sa propre note métier. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et prise en main, SANS calcul chiffré (J1)

Avant de coder, appropriez-vous la question. Que représente une ligne du fichier — une vente unitaire, une ligne de ticket, un panier ? Le contrôleur parle de « journée de ventes » : pour raisonner à sa maille, faudra-t-il regarder chaque ligne, ou plutôt agréger le `montant` par jour (et par magasin) ? Écrivez en quelques phrases votre définition d'une « journée normale » : est-ce la moyenne, la médiane, autre chose ? Anticipez enfin ce qui pourrait rendre une journée « à côté de la plaque » : une opération commerciale, un gros client professionnel, une saisie erronée ? Ces hypothèses guideront votre lecture des résultats. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Prise en main du fichier et tendance centrale (J1-J2)

Chargez le fichier avec pandas en typant correctement la date (`parse_dates`). Dressez un premier profil : volume (`shape`), types (`dtypes`), aperçu (`head()`), et un `describe()` global. Calculez ensuite la **moyenne, la médiane et le mode** du `montant`. Comparez moyenne et médiane : sont-elles proches ? Si elles s'écartent nettement, dans quel sens penche l'écart, et qu'est-ce que cela suggère sur la forme de la distribution (symétrique, ou tirée par le haut) ? Formulez déjà une première réponse provisoire au contrôleur.

### Phase 3 — Dispersion et distribution (J2-J3)

Une moyenne seule ne dit rien de la régularité de l'activité. Mesurez la **dispersion** du `montant` : étendue (min/max), variance, écart-type, puis les **quartiles Q1 et Q3** et l'**écart interquartile (IQR)**. Que raconte un écart-type élevé pour le contrôleur — des ventes régulières ou très variables d'un jour à l'autre ? Tracez ensuite un **histogramme** et une **boîte à moustaches (boxplot)** du `montant`, tous deux titrés et lisibles seuls. La forme visuelle confirme-t-elle l'écart moyenne/médiane observé en Phase 2 ?

### Phase 4 — Détection des valeurs aberrantes (J3-J4)

Passez au repérage des journées « à côté de la plaque ». Appliquez la **règle de l'IQR** : toute valeur hors de l'intervalle `[Q1 − 1,5 × IQR ; Q3 + 1,5 × IQR]` est considérée comme aberrante. Comptez combien de valeurs sortent de ces bornes, et quelle proportion du total cela représente. Listez les plus marquantes et interrogez-les au cas par cas : promotion exceptionnelle, achat professionnel, ou erreur de saisie ? Comment décideriez-vous, pour chacune, s'il faut la conserver ou l'écarter — et cette décision est-elle la même selon qu'on veut mesurer le « quotidien » ou le « chiffre d'affaires total » ?

### Phase 5 — Note métier, recommandation et mise en ligne (J5)

Rédigez une **note de synthèse** (5 à 8 lignes) qui répond frontalement à la question centrale : combien vaut une journée « normale » de NordRetail, et que faire des journées hors norme ? Tranchez explicitement : recommandez-vous la **moyenne ou la médiane** pour le reporting de la direction, et pourquoi ? Cette note s'adresse au contrôleur de gestion : pas de jargon Python, des phrases actionnables. Nettoyez votre notebook (il doit s'exécuter de haut en bas sans erreur), soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : profil du fichier, tendance centrale (moyenne / médiane / mode) commentée, dispersion complète (écart-type, variance, IQR), histogramme + boxplot titrés, outliers détectés par la règle de l'IQR et comptés, note métier tranchée, dépôt public à jour.

### Pour aller plus loin (bonus)

- Agrégez le `montant` **par jour et par magasin** et refaites l'analyse à cette maille : la définition d'une « journée normale » change-t-elle par rapport à la maille « ligne » ?
- Comparez la distribution du `montant` entre le canal **Magasin** et **E-commerce** (deux boxplots côte à côte) : l'un est-il plus dispersé que l'autre ?
- Confrontez vos indicateurs aux [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) : une journée « normale » atteint-elle l'objectif fixé à l'enseigne ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `mini_analyse_ventes.ipynb` — notebook exécuté de bout en bout (code commenté + graphiques + cellules d'analyse) ;
  - une **note de synthèse** (`SYNTHESE.md` ou PDF) rédigée pour le contrôleur de gestion ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Un **tableau récapitulatif des indicateurs** (moyenne, médiane, mode, écart-type, quartiles, nombre d'outliers) — dans le notebook ou la note.

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook et note métier (60 %)** : justesse des indicateurs statistiques, pertinence des interprétations, lisibilité des graphiques, rigueur de la détection d'outliers, clarté de la note de synthèse.
- **Restitution orale (40 %)** : 10 minutes pour présenter au contrôleur de gestion (le formateur et un autre binôme) votre réponse à la question centrale + 5 minutes de questions.

**Validation partielle** : un binôme dont le notebook n'est pas complètement finalisé mais dont le raisonnement statistique (choix moyenne/médiane, méthode IQR, interprétation) est structuré et documenté peut valider partiellement les compétences travaillées.

## Critères de performance

**Explorer et décrire la tendance centrale**
- Le fichier est chargé avec les bons types (`date` en datetime) et un premier profil est dressé (`shape`, `dtypes`, `describe`).
- Moyenne, médiane ET mode du `montant` sont calculés.
- L'écart moyenne/médiane est interprété (symétrie / distribution tirée par les extrêmes).

**Mesurer la dispersion et visualiser**
- Écart-type, variance et quartiles (Q1, Q3, IQR) du `montant` sont présents.
- Un histogramme ET une boîte à moustaches sont tracés, titrés et lisibles de façon autonome.
- La forme des graphiques est rattachée à l'analyse chiffrée (elle confirme ou nuance l'écart moyenne/médiane).

**Détecter et décider sur les valeurs aberrantes**
- Les outliers sont détectés par la **règle de l'IQR** (pas « à l'œil ») et comptés (volume + proportion).
- Les valeurs extrêmes sont questionnées (cause probable : promo, achat pro, erreur).
- Une décision argumentée est proposée (garder / écarter), cohérente avec l'usage visé.

**Restituer**
- La note de synthèse répond explicitement à la question centrale et tranche entre moyenne et médiane, justification à l'appui.
- Elle est rédigée sans jargon technique, avec des constats actionnables.
- Le dépôt GitHub public est complet (notebook exécutable + README).

## Ressources

- Rappels — [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) (tendance centrale, dispersion, IQR)
- Module de cours — [Analyse exploratoire (EDA)](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/)
- Documentation pandas — [`describe()`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html) · https://pandas.pydata.org/docs/
- Documentation seaborn — [`boxplot`](https://seaborn.pydata.org/generated/seaborn.boxplot.html) & [`histplot`](https://seaborn.pydata.org/generated/seaborn.histplot.html)
- Documentation matplotlib : https://matplotlib.org/stable/
- Étape suivante du parcours — l'audit qualité des mêmes données : [Brief S06 — EDA des ventes NordRetail](semaine-06-eda-ventes-nordretail.md)
