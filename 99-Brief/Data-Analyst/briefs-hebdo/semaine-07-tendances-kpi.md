# Brief S07 — Lire les tendances des ventes NordRetail et définir les premiers KPI

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S07 — Phase 1 : Ajuster & analyser un tableau de bord métier |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant → intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | Python 3, pandas, matplotlib, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [EDA des ventes NordRetail (S06)](semaine-06-eda-ventes-nordretail.md) · [Tendances & séries temporelles](../../../15-Business-Intelligence/05-Tendances-Series-Temporelles/) · [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. L'entreprise pèse plusieurs dizaines de millions d'euros de chiffre d'affaires annuel, et son équipe data — dont vous faites partie, aux côtés d'un responsable BI et d'une contrôleuse de gestion — est en train de construire, semaine après semaine, le tableau de bord de pilotage réclamé par la direction commerciale.

### Le problème

La semaine dernière, vous avez établi un **diagnostic de confiance** sur les données de ventes et sorti les premiers constats sur l'activité globale. Vous savez désormais que les données sont exploitables (sous réserve des anomalies documentées). Mais un chiffre d'affaires global ne suffit pas à piloter une enseigne de distribution.

Le retail des Hauts-de-France vit au rythme des saisons : les soldes d'hiver, le pic de Noël, le creux de la rentrée. Lors du dernier comité, la direction a posé deux questions très concrètes. D'abord : **quand** l'activité monte-t-elle et retombe-t-elle au fil de l'année, et cette respiration saisonnière est-elle la même pour tous les rayons et tous les canaux ? Ensuite : sur quels **indicateurs** l'équipe va-t-elle s'accorder pour suivre l'activité mois après mois, sans réinventer le calcul à chaque réunion ?

Votre mission de la semaine transforme donc l'exploration de la semaine 6 en **lecture temporelle** de l'activité, puis en **une poignée d'indicateurs stables et documentés**, prêts à être affichés sur le futur tableau de bord.

### La question centrale

Toute la semaine, chaque analyse que vous produisez doit contribuer à répondre à la question que la direction vous a posée :

> **« À quel rythme les ventes de NordRetail respirent-elles au fil de l'année, et sur quels indicateurs fiables l'équipe peut-elle piloter l'enseigne mois après mois ? »**

### Les données

Vous repartez du même export réel que la semaine dernière, désormais familier :

- [`../data/ventes_magasins.csv`](../data/ventes_magasins.csv) — **12 000 lignes** de ventes détaillées. Colonnes : `date`, `ville`, `type` (Magasin / E-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.

Le fichier couvre plusieurs mois d'activité : c'est cette profondeur temporelle que vous allez exploiter cette semaine pour faire apparaître les tendances.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Construire une série temporelle** à partir de données transactionnelles : agréger les ventes par mois et représenter leur évolution dans le temps.
- **Repérer et chiffrer une saisonnalité** : identifier les pics (Noël, soldes) et les creux, et mesurer leur ampleur relative par rapport au reste de l'année.
- **Comparer des tendances par segment** (catégorie, canal de vente) pour voir si toutes les activités suivent le même rythme.
- **Distinguer corrélation et causalité** : formuler des interprétations prudentes qui séparent ce que l'on observe de ce que l'on suppose.
- **Définir des indicateurs de pilotage documentés et vérifiables** (méthode SMART), avec formule exacte, granularité, cible chiffrée et source, prêts à alimenter un tableau de bord.

## Données fournies

Le jeu de données est déjà présent dans le dépôt : [`99-Brief/Data-Analyst/data/ventes_magasins.csv`](../data/ventes_magasins.csv). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur ce fichier ; comme la semaine dernière, on ne modifie jamais la source.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit son propre notebook et son propre dictionnaire d'indicateurs. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage temporel et choix des indicateurs, SANS analyse chiffrée (J1)

Avant de coder, posez le cadre. Reprenez les constats de la semaine 6 : que savez-vous déjà de la période couverte par le fichier ? Combien de mois complets pouvez-vous espérer analyser, et cela suffit-il pour parler de « saisonnalité » ? Listez, en vous appuyant sur votre connaissance du retail, les moments de l'année où vous vous attendez à un pic ou à un creux, et notez ces hypothèses : elles vous serviront de repères à confronter aux chiffres. Réfléchissez ensuite à ce que la direction voudra suivre en permanence : de quels indicateurs a besoin un responsable de magasin pour savoir, chaque mois, si « ça va bien » ? Écrivez une première liste brute (sans formule encore), que vous affinerez en Phase 4. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Agrégation mensuelle et courbe d'évolution (J1-J2)

Chargez le fichier avec pandas en typant correctement la date (`parse_dates`). Créez une colonne `mois` (par exemple `df["date"].dt.to_period("M")`) et calculez le chiffre d'affaires mensuel (`df.groupby("mois")["montant"].sum()`). Tracez ensuite la **courbe d'évolution** du CA mensuel : un axe temporel lisible, un titre explicite, des mois identifiables. Que raconte cette courbe ? Où sont les points hauts et les points bas ? Annotez visuellement ou par écrit les pics et les creux que vous repérez. Attention aux mois partiels en début ou fin de période : un mois incomplet peut créer un faux creux — comment le signalez-vous pour ne pas induire la direction en erreur ?

### Phase 3 — Effet soldes, effet Noël et tendances segmentées (J2-J3)

Quantifiez ce que la courbe suggère. Comparez les mois de soldes (janvier, juillet) et le mois de décembre au reste de l'année : le CA y est-il réellement plus élevé, et de combien en pourcentage par rapport à la moyenne mensuelle ? Un pic « à l'œil » n'est un enseignement que s'il est chiffré. Produisez ensuite au moins **une tendance segmentée** : le CA mensuel par `categorie` **ou** par `type` (Magasin vs E-commerce). Toutes les activités respirent-elles au même rythme ? Le e-commerce suit-il la même saisonnalité que les magasins ? Une catégorie tire-t-elle son épingle du jeu au moment des fêtes ? Pour chaque constat, restez prudents : distinguez clairement ce que vous **observez** (deux courbes montent en même temps) de ce que vous **supposez** (l'une cause l'autre). Pas de raccourci corrélation → causalité.

### Phase 4 — Définition des indicateurs de pilotage (J4)

Passez de l'analyse à l'outillage. En repartant de votre liste brute de la Phase 1, choisissez **4 à 5 indicateurs** que l'équipe affichera sur le tableau de bord (par exemple : CA total, panier moyen, marge totale, nombre de commandes, taux de remise moyen). Pour chacun, remplissez un tableau avec : **nom · formule exacte (colonnes du fichier) · granularité (mois, ville, catégorie…) · cible chiffrée · source**. Puis passez chaque indicateur au filtre **SMART** : est-il Spécifique (sait-on exactement ce qu'il mesure ?), Mesurable (la formule est-elle sans ambiguïté ?), Atteignable et Réaliste (la cible tient-elle debout au vu des chiffres observés cette semaine ?), Temporel (à quelle fréquence le lit-on ?). Un indicateur dont la cible sort de nulle part n'est pas pilotable : justifiez vos cibles à partir de ce que les données vous ont montré.

### Phase 5 — Synthèse, restitution et mise en ligne (J5)

Rédigez une **note de synthèse** (8 à 15 lignes) qui répond frontalement à la question centrale : à quel rythme les ventes respirent-elles, et quels indicateurs recommandez-vous pour le pilotage ? Cette note s'adresse à la direction : pas de jargon Python, des constats actionnables et des réserves honnêtes (mois partiels, prudence sur les causes). Nettoyez votre notebook (il doit s'exécuter de haut en bas sans erreur), finalisez le dictionnaire des indicateurs, soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : CA mensuel calculé et tracé, saisonnalité chiffrée (% vs moyenne), au moins une tendance segmentée, interprétations qui ne confondent pas corrélation et causalité, 4 à 5 indicateurs SMART documentés, note de synthèse, dépôt public à jour.

### Pour aller plus loin (bonus)

- Comparez la saisonnalité entre **deux villes** (Dunkerque vs Roubaix, par exemple) : le calendrier commercial est-il identique partout ?
- Lissez la série avec une **moyenne mobile** (3 mois) pour distinguer la tendance de fond du bruit mensuel.
- Confrontez vos indicateurs aux objectifs déjà fixés par le contrôle de gestion dans [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) : vos cibles SMART sont-elles cohérentes avec ces objectifs ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - `tendances.ipynb` — notebook exécuté de bout en bout (courbe du CA mensuel + tendance segmentée + interprétations écrites) ;
  - un **dictionnaire des indicateurs** (`dictionnaire_kpi.md`) : tableau des 4-5 indicateurs (nom, formule, granularité, cible, source) avec la justification SMART de chacun ;
  - une **note de synthèse** destinée à la direction (dans le notebook, le README ou un fichier dédié) ;
  - un **`README.md`** : description du projet, technologies, instructions de lancement, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Notebook et dictionnaire d'indicateurs (60 %)** : justesse de l'agrégation mensuelle, lisibilité de la courbe, saisonnalité effectivement chiffrée, pertinence de la tendance segmentée, prudence des interprétations, et solidité des indicateurs (formule exacte, cible justifiée, contrôle SMART).
- **Restitution orale (40 %)** : 10 minutes de présentation des tendances et des indicateurs proposés à un « comité de direction » (le formateur et un autre binôme) + 5 minutes de questions.

**Validation partielle** : un binôme dont le notebook n'est pas complètement finalisé mais dont l'analyse de saisonnalité et la démarche de définition des indicateurs sont structurées et documentées peut valider partiellement les compétences travaillées.

## Critères de performance

**Analyser les tendances temporelles**
- Le CA mensuel est calculé (agrégation par mois) et visualisé sous forme de courbe titrée et lisible.
- La saisonnalité (Noël, soldes) est repérée ET chiffrée (% par rapport à la moyenne mensuelle).
- Au moins une tendance segmentée (catégorie ou canal) est produite et comparée.
- Les mois partiels ou atypiques sont signalés pour éviter les fausses conclusions.
- Les interprétations distinguent explicitement corrélation et causalité.

**Définir des indicateurs de pilotage**
- 4 à 5 indicateurs sont définis avec nom, formule exacte, granularité, cible chiffrée et source (colonne).
- Chaque cible est justifiée à partir des données observées, pas fixée arbitrairement.
- Chaque indicateur est passé au filtre SMART et le contrôle est explicité.

**Restituer**
- La note de synthèse répond explicitement à la question centrale (rythme des ventes + indicateurs recommandés).
- Elle est rédigée sans jargon technique, avec des constats actionnables et des réserves honnêtes.
- Le dépôt GitHub public est complet (notebook exécutable + dictionnaire d'indicateurs + README).

## Ressources

- Module de cours — [Tendances & séries temporelles](../../../15-Business-Intelligence/05-Tendances-Series-Temporelles/)
- Module de cours — [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/)
- Brief précédent du parcours — [S06 : Audit & EDA des ventes NordRetail](semaine-06-eda-ventes-nordretail.md)
- Documentation pandas — séries temporelles : https://pandas.pydata.org/docs/user_guide/timeseries.html
- Documentation matplotlib : https://matplotlib.org/stable/
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
