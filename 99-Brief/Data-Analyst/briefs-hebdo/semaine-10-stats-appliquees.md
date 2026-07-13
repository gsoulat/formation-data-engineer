# Brief S10 — Faire parler les données clients de NordRetail : corrélations & segmentation

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S10 — Phase 2 : Analyse avancée pour piloter la relation client |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, matplotlib, seaborn, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Audit & EDA des ventes (S06)](semaine-06-eda-ventes-nordretail.md) · [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) · [Module EDA](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Depuis quelques semaines, son équipe data — dont vous faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion — a assaini les exports de ventes et posé les premières briques du tableau de bord de pilotage. Les données sont désormais fiables et organisées en un modèle en étoile prêt à l'emploi.

### Le problème

La direction marketing veut lancer une **campagne de fidélisation**, mais elle avance à l'aveugle : jusqu'ici, personne n'a fait parler les ventes autrement qu'en additionnant le chiffre d'affaires. Or additionner un CA ne dit rien de *qui* achète, ni *comment*. Deux magasins peuvent réaliser le même CA avec des clientèles radicalement différentes — l'un porté par quelques gros comptes professionnels, l'autre par une foule de petits paniers particuliers. Piloter une campagne sur le seul CA total, c'est arroser au hasard.

Votre mission de la semaine prolonge donc le travail d'exploration : passer des **totaux** aux **relations** et aux **profils**. Vous allez mesurer comment les grandeurs de vente se répondent (les remises rognent-elles vraiment la marge ? la quantité tire-t-elle le montant ?), puis segmenter la clientèle pour distinguer les clients à choyer de ceux qu'on est en train de perdre.

### La question centrale

Toute la semaine, chaque analyse que vous produisez doit contribuer à répondre à la question que la direction marketing vous a posée :

> **« Qui sont les meilleurs clients de NordRetail, lesquels risque-t-on de perdre, et quels leviers (remise, canal, ville) agissent réellement sur la valeur d'une vente ? »**

### Les données

Cette semaine, vous ne travaillez plus sur un export brut mais sur le **modèle en étoile** consolidé de l'enseigne — une table de faits reliée à ses dimensions :

- [`../data/Faits_Ventes.csv`](../data/Faits_Ventes.csv) — **12 000 lignes** de ventes. Colonnes : `vente_id`, `date_id`, `magasin_id`, `produit_id`, `client_id`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`.
- [`../data/Dim_Client.csv`](../data/Dim_Client.csv) — **600 clients**. Colonnes : `client_id`, `prenom`, `nom`, `ville`, `segment` (Particulier / Pro), `date_inscription`, `email`.
- [`../data/Dim_Produit.csv`](../data/Dim_Produit.csv) — catalogue produits (`produit_id`, `produit`, `categorie`, `prix_unitaire`, `cout_unitaire`).
- [`../data/Dim_Date.csv`](../data/Dim_Date.csv) — calendrier (`date_id`, `date`, `annee`, `trimestre`, `mois`, `nom_mois`, `jour_semaine`, `est_weekend`).

Le `date_id` de la table de faits se relie à `Dim_Date` pour retrouver la vraie date d'une vente ; le `client_id` se relie à `Dim_Client`. C'est cette capacité à **joindre** qui va vous permettre de croiser une vente avec un profil client.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Décrire finement la distribution de variables métier** : tendance centrale, dispersion, asymétrie et valeurs extrêmes, en choisissant la représentation (boxplot, histogramme) qui révèle le mieux la forme des données.
- **Mesurer et interpréter des corrélations** entre grandeurs de vente : construire une matrice de corrélation, la visualiser (heatmap), et distinguer rigoureusement **corrélation** et **causalité**.
- **Segmenter une population** par une méthode reproductible (analyse RFM — Récence, Fréquence, Montant) et transformer des scores en **segments nommés et actionnables**.
- **Croiser une segmentation avec des dimensions métier** (type de client, ville) pour faire émerger des constats non triviaux.
- **Restituer des recommandations chiffrées** à un décideur marketing non technique.

## Données fournies

Les quatre fichiers sont déjà présents dans le dépôt (dossier [`99-Brief/Data-Analyst/data/`](../data/)). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule : les jointures, agrégations et scores se construisent dans le notebook, jamais dans les fichiers sources.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook et sa propre synthèse. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage de l'analyse, SANS calcul (J1)

Avant de coder, appropriez-vous la question marketing. Ouvrez les fichiers dans un tableur : que représente une ligne de `Faits_Ventes` ? Combien de clients pour combien de ventes — un client achète-t-il en moyenne une fois, ou plusieurs ? Réfléchissez à ce que serait un « bon client » pour NordRetail : celui qui dépense le plus ? le plus souvent ? le plus récemment ? Notez, avant tout chiffre, quelles corrélations vous *anticipez* — pensez-vous qu'une remise élevée fasse mécaniquement grimper la quantité vendue ? qu'elle protège ou grignote la marge ? Ces hypothèses serviront de fil rouge : une analyse qui confirme une intuition et une analyse qui la contredit ont toutes deux de la valeur. Initialisez votre dépôt GitHub dès aujourd'hui et écrivez-y ces hypothèses.

### Phase 2 — Distributions et statistiques descriptives (J1-J2)

Chargez les fichiers avec pandas. Reliez `Faits_Ventes` à `Dim_Date` (via `date_id`) pour disposer de la vraie date de chaque vente, et à `Dim_Client` (via `client_id`) pour connaître le type et la ville de l'acheteur. Pour `montant`, `marge`, `quantite` et `remise`, produisez le profil statistique complet : moyenne, médiane, écart-type, quartiles. Chaque variable est-elle symétrique ou asymétrique ? Appuyez-vous sur au moins un **boxplot** et un **histogramme** pour trancher, et interrogez les valeurs extrêmes : une marge très basse est-elle une erreur, une promotion agressive, ou un achat professionnel négocié ? Pour une variable nettement asymétrique, quel indicateur recommanderiez-vous à la direction pour parler d'une « vente typique » ?

### Phase 3 — Corrélations : ce qui bouge ensemble (J2-J3)

Construisez la **matrice de corrélation** entre les variables numériques de vente (`quantite`, `prix_unitaire`, `remise`, `montant`, `marge`) et visualisez-la en **heatmap** lisible. Commentez les couples qui vous intéressent métier : `quantite` vs `montant`, `remise` vs `marge`, `remise` vs `montant`. Quels liens sont forts, faibles, positifs, négatifs ? Surtout : une corrélation forte entre remise et marge prouve-t-elle que la remise *cause* la baisse de marge, ou d'autres facteurs entrent-ils en jeu ? Formulez explicitement, pour au moins un couple, pourquoi corrélation ne vaut pas causalité — et ce qu'il faudrait pour l'établir.

### Phase 4 — Segmentation RFM des clients (J3-J4)

Passez de la vente au client. Par `client_id`, calculez les trois axes RFM :
- **Récence** — nombre de jours depuis le dernier achat (date de référence = date maximale du jeu de données) ;
- **Fréquence** — nombre de ventes du client ;
- **Montant** — somme des `montant` du client.

Attribuez à chaque axe un **score de 1 à 5** par quintiles (pensez à `qcut`), en justifiant votre logique (un client très récent doit-il avoir le score de Récence le plus haut ou le plus bas ?). Combinez ensuite les scores pour définir **3 à 5 segments nommés et lisibles** — par exemple « Champions », « Fidèles », « À risque », « Endormis » — chacun décrit en une phrase métier (qui sont-ils, que faut-il en faire ?).

### Phase 5 — Croisements métier, synthèse et mise en ligne (J5)

Reliez vos segments aux dimensions client : les « Champions » sont-ils plutôt des professionnels ou des particuliers ? Une ville concentre-t-elle les clients « À risque » ? Un tableau croisé (segment × `segment` Particulier/Pro, segment × `ville`) suffit à révéler l'essentiel. Rédigez enfin une **synthèse de 5 à 8 enseignements chiffrés et orientés action** à destination de la direction marketing : pas de jargon Python, des recommandations concrètes (« cibler tel segment par tel canal parce que… »). Nettoyez le notebook (il doit s'exécuter de haut en bas sans erreur), exportez-le en PDF ou HTML, soignez le README et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : profil statistique des quatre variables interprété, matrice de corrélation commentée sans confondre corrélation et causalité, scores RFM calculés et justifiés, 3 à 5 segments nommés, au moins un croisement métier, synthèse actionnable, dépôt public à jour.

### Pour aller plus loin (bonus)

- Comparez la valeur moyenne d'une vente entre **deux groupes** (Magasin vs E-commerce, ou Particulier vs Pro) : l'écart observé est-il net, ou pourrait-il tenir au hasard de l'échantillon ? Amorcez ce raisonnement à l'aide des [rappels de statistique inférentielle](../../../01-Fondamentaux/Mathematiques/05-Statistique-Inferentielle/).
- Ajoutez une **cinquième dimension** au RFM (ex. marge moyenne du client) et discutez de son apport.
- Reliez `Dim_Produit` pour repérer si certains segments sont associés à des **catégories** de produits particulières.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `stats_clients.ipynb` — notebook exécuté de bout en bout (code + graphiques + cellules d'analyse), plus son export **PDF ou HTML** ;
  - une **synthèse** (`SYNTHESE.md` ou PDF) d'une demi-page rédigée pour la direction marketing ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).
- Un **tableau des segments** (nom, effectif, profil RFM moyen, action recommandée) — dans le notebook ou la synthèse.

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook et synthèse (60 %)** : justesse des statistiques et de l'interprétation des distributions, lecture correcte de la matrice de corrélation (sans glissement vers la causalité), rigueur et reproductibilité du calcul RFM, pertinence des segments et de leur croisement métier, qualité de la synthèse.
- **Restitution orale (40 %)** : 10 minutes de présentation des segments et des recommandations à un « comité marketing » (le formateur et un autre binôme) + 5 minutes de questions.

**Validation partielle** : un binôme dont le notebook n'est pas complètement finalisé mais dont le raisonnement statistique (distributions, corrélations, logique de segmentation) est structuré et documenté peut valider partiellement les compétences travaillées.

## Critères de performance

**Décrire les distributions**
- Les jointures `Faits_Ventes` × `Dim_Date` × `Dim_Client` sont réalisées correctement.
- Moyenne, médiane, écart-type et quartiles de `montant`, `marge`, `quantite`, `remise` sont calculés.
- Asymétrie et valeurs extrêmes sont identifiées à l'appui d'au moins un boxplot ET un histogramme, et interprétées.

**Mesurer les corrélations**
- Une matrice de corrélation est produite et visualisée en heatmap lisible.
- Au moins deux couples de variables sont commentés (force, signe, sens métier).
- La distinction corrélation / causalité est formulée explicitement pour au moins un couple.

**Segmenter les clients (RFM)**
- Récence, Fréquence et Montant sont calculés par `client_id` avec une méthode justifiée (date de référence explicite, scoring par quintiles).
- 3 à 5 segments nommés et décrits en termes métier sont obtenus.
- Au moins un croisement segment × dimension métier (type de client ou ville) est produit et commenté.

**Restituer**
- La synthèse propose 5 à 8 enseignements chiffrés et des actions concrètes.
- Elle est rédigée sans jargon technique, orientée décision marketing.
- Le dépôt GitHub public est complet (notebook exécutable + export + README).

## Ressources

- Module de cours — [Analyse exploratoire (EDA)](../../../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/)
- Rappels — [Statistiques descriptives](../../../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/)
- Pour le bonus — [Statistique inférentielle](../../../01-Fondamentaux/Mathematiques/05-Statistique-Inferentielle/)
- Étape précédente du parcours — [Audit & EDA des ventes (S06)](semaine-06-eda-ventes-nordretail.md)
- Documentation pandas (`describe`, `corr`, `qcut`) : https://pandas.pydata.org/docs/
- Documentation seaborn (heatmap, boxplot) : https://seaborn.pydata.org/
