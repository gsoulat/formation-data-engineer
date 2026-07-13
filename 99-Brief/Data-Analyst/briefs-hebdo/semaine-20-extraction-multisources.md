# Brief S20 — Confronter les ventes aux objectifs : extraction multi-sources chez NordRetail

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S20 — Phase 3 : Alimenter le tableau de bord depuis plusieurs sources |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Technologies** | SQL (SQLite ou PostgreSQL), Python 3, pandas, requests, Jupyter Notebook, Git/GitHub |
| **Prérequis** | [Jointures SQL](../../../01-Fondamentaux/SQL/03-Jointures/) · [Fonctions avancées SQL](../../../01-Fondamentaux/SQL/05-Fonctions-Avancees/) · [Extraction & analyse](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/) · [Collecte de données](../../../15-Business-Intelligence/14-Collecte-Donnees/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes, Amiens) doublé d'un canal e-commerce. Depuis plusieurs semaines, votre équipe data — un responsable BI, une contrôleuse de gestion et vous — construit pas à pas le **tableau de bord de pilotage** de la direction commerciale. Les données de ventes ont été auditées, nettoyées, et les premiers indicateurs sont posés. Il manque encore une brique décisive : le **point de comparaison**.

### Le problème

Un chiffre d'affaires seul ne dit pas si un magasin va bien. « 130 000 € en mars, est-ce beaucoup ? » La seule réponse honnête est : *par rapport à quoi ?* La direction a fixé en début d'année des **objectifs de CA mensuels, magasin par magasin** — mais ce classeur d'objectifs vit à part, hors de la base de ventes. Tant que les deux mondes ne se rencontrent pas, impossible de dire qui atteint sa cible et qui décroche.

Deux difficultés se cumulent. D'abord, le CA réel dort dans la **base transactionnelle** : il faut aller le chercher magasin par magasin, mois par mois, à coup de requêtes qui joignent commandes, produits et magasins — et savoir classer les magasins entre eux. Ensuite, les objectifs arrivent dans un **format séparé** (un fichier tableur), avec sa propre structure. Votre mission de la semaine : faire **converger ces sources** pour que le tableau de bord affiche enfin un **taux d'atteinte des objectifs** fiable.

### La question centrale

Toute la semaine, chaque requête et chaque croisement que vous produisez doit contribuer à répondre à la question que la direction vous a posée :

> **« Quels magasins de NordRetail atteignent leurs objectifs de chiffre d'affaires en 2024, et lesquels décrochent ? »**

### Les données

Deux sources de nature différente, qu'il faudra réconcilier :

- [`../data/setup.sql`](../data/setup.sql) — le **dump de la base transactionnelle** NordRetail (tables `magasins`, `produits`, `clients`, `commandes`). La table `commandes` porte le détail des ventes (`date`, `magasin_id`, `produit_id`, `quantite`, `prix_unitaire`, `remise`, `montant`) ; `magasins` porte la ville et le type de point de vente ; `produits` porte la catégorie.
- [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) — les **objectifs de CA fixés par la direction**, structurés **par magasin** : colonnes `magasin_id`, `annee`, `mois`, `objectif_ca`. Une version tableur équivalente, [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx), existe pour ceux qui veulent s'exercer à un second format.

Les deux sources partagent la même clé métier : l'identifiant de magasin et le mois. C'est le pivot de tout votre travail.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Écrire des requêtes SQL avancées** pour extraire une donnée agrégée : expressions de table communes (CTE, `WITH …`) pour structurer un calcul en étapes, et fonctions de fenêtrage (`RANK()`, `ROW_NUMBER()`, `SUM() OVER …`) pour classer et cumuler sans perdre le détail.
- **Charger une source de fichier dans pandas** et en comprendre la structure (`read_csv`, typage des colonnes de clé).
- **Croiser deux sources hétérogènes** (résultat SQL × fichier) par une jointure sur une clé composite (magasin + mois), en anticipant les pièges de correspondance (types, valeurs manquantes, lignes orphelines).
- **Construire un indicateur de pilotage** — le taux d'atteinte des objectifs — et l'interpréter magasin par magasin.
- **Restituer une lecture métier** claire à partir d'un croisement de données, à destination d'un lecteur non technique.

## Données fournies

Tout est déjà présent dans le dépôt, dans [`99-Brief/Data-Analyst/data/`](../data/). Rien à télécharger. Vous montez la base localement à partir de `setup.sql` (SQLite suffit, PostgreSQL possible) et travaillez en lecture seule sur les fichiers d'objectifs : vos résultats sont exportés à part, on ne modifie jamais les sources.

## Travail demandé

Travail en **binôme sur 5 jours**. L'entraide entre binômes est encouragée, mais chaque binôme produit ses propres requêtes, son propre notebook et sa propre analyse. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et exploration des sources, SANS écrire de requête (J1)

Avant d'attaquer le SQL, cartographiez le terrain. Ouvrez `setup.sql` et repérez le **schéma** : quelles tables, quelles colonnes, quelles clés relient `commandes` à `magasins` et à `produits` ? Dessinez ce petit modèle relationnel sur papier — de quelles tables avez-vous besoin pour reconstituer un CA par magasin et par mois ? Ouvrez ensuite `objectifs_2024.csv` dans un tableur : à quelle **granularité** est-il ? (une ligne = un magasin × un mois ?). Interrogez la clé de jonction : le `magasin_id` du fichier d'objectifs correspond-il bien à celui de la base ? Le « mois » est-il stocké de la même façon des deux côtés (un numéro, une date) ? Notez les écarts que vous anticipez — ce sont eux qui feront rater ou réussir votre croisement. Initialisez votre dépôt GitHub dès aujourd'hui.

### Phase 2 — Extraction SQL avancée : CA réel par magasin (J1-J2)

Montez la base à partir de `setup.sql`, puis écrivez vos requêtes. Le socle attendu :

- une **CTE** (`WITH …`) qui calcule le **CA mensuel par magasin** en joignant `commandes` × `magasins` (et `produits` si vous voulez ventiler par catégorie). Structurer le calcul en étapes nommées rend la requête lisible et rejouable ;
- au moins une **fonction de fenêtrage** appliquée à ce CA : un **classement** des magasins par CA à l'intérieur de chaque mois (`RANK()` ou `ROW_NUMBER() OVER (PARTITION BY mois ORDER BY ca DESC)`), et/ou un **cumul glissant** du CA sur l'année (`SUM(ca) OVER (PARTITION BY magasin_id ORDER BY mois)`).

Vérifiez vos résultats : le total de CA recalculé colle-t-il à ce que vous saviez de l'activité ? Un magasin ressort-il systématiquement en tête du classement ? Le fenêtrage vous permet-il de voir *qui monte* au fil des mois sans écraser le détail mensuel ?

### Phase 3 — Deuxième source et croisement (J2-J3)

Chargez `objectifs_2024.csv` dans pandas (`read_csv`) et récupérez le résultat de votre requête SQL dans un DataFrame. Vous avez maintenant deux tables : le **CA réel** (issu de la base) et l'**objectif** (issu du fichier), toutes deux à la maille magasin × mois. Croisez-les avec un `merge` sur la **clé composite** `magasin_id` + `mois`. Soyez méthodique sur les pièges repérés en Phase 1 : les types des clés sont-ils identiques des deux côtés ? Combien de lignes après jonction, et est-ce le compte attendu ? Y a-t-il des magasins ou des mois **sans correspondance** (objectif sans vente, ou l'inverse) — et qu'est-ce que cela signifie ? Un `merge` qui « perd » des lignes en silence est le bug classique de l'extraction multi-sources : traquez-le.

### Phase 4 — Taux d'atteinte et lecture métier (J3-J4)

Calculez le **taux d'atteinte** = `CA réel / objectif_ca`, magasin par magasin et mois par mois. Ce ratio est l'indicateur que la direction attend : au-dessus de 1, le magasin dépasse sa cible ; en dessous, il décroche. Produisez une table de synthèse lisible (par magasin : CA cumulé, objectif cumulé, taux moyen). Faites parler les données : **quels magasins sur-performent, lesquels sous-performent** par rapport à leur objectif ? Le classement par CA brut (Phase 2) et le classement par taux d'atteinte racontent-ils la même histoire — un « gros » magasin peut-il rater sa cible pendant qu'un « petit » la dépasse ? À l'aide de votre cumul glissant, **quel magasin progresse le plus** sur l'année ? Exportez votre table finale en CSV.

### Phase 5 — Synthèse, rapport et mise en ligne (J5)

Rédigez une **note de synthèse** (8 à 15 lignes) qui répond frontalement à la question centrale : quels magasins atteignent leurs objectifs, lesquels décrochent, et quelle tendance se dessine sur l'année ? Cette note s'adresse à la direction : pas de jargon SQL ni Python, des constats actionnables (« le magasin X est à 78 % de sa cible depuis trois mois, à surveiller »). Vérifiez que votre chaîne est **rejouable** de bout en bout (la requête tourne, le notebook s'exécute de haut en bas sans erreur), soignez le README, et poussez le tout sur GitHub.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : schéma des sources compris, requête SQL avec CTE **et** fonction de fenêtrage, chargement du fichier d'objectifs, croisement sans perte de ligne sur la clé composite, taux d'atteinte calculé, table finale exportée en CSV, note de synthèse, dépôt public à jour.

### Pour aller plus loin (bonus)

- **Une source externe via API.** Appelez l'API gratuite et sans clé **Open-Meteo** (endpoint *archive*) pour récupérer la température journalière 2024 de Lille (`latitude=50.63`, `longitude=3.06`, `daily=temperature_2m_mean`). Rangez le JSON reçu dans un DataFrame avec `requests`, et explorez une **piste de corrélation** ventes/météo par catégorie (le Sport progresse-t-il l'été ? la Maison l'hiver ?).
- **Un troisième format.** Rechargez les objectifs depuis [`../data/objectifs_2024.xlsx`](../data/objectifs_2024.xlsx) avec `read_excel` pour vérifier que votre croisement donne le même résultat quel que soit le format d'entrée.
- **Ventilation par catégorie.** Étendez votre CTE pour calculer le taux d'atteinte non plus seulement par magasin, mais par magasin × catégorie de produit.

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le(s) fichier(s) `.sql` de vos requêtes (CTE + fenêtrage), commentés ;
  - un **notebook** (`extraction_multisources.ipynb`) exécuté de bout en bout : chargement du fichier d'objectifs, croisement, calcul du taux d'atteinte, table de synthèse ;
  - la **table finale exportée en CSV** (taux d'atteinte par magasin et par mois) ;
  - une **note de synthèse** (`SYNTHESE.md` ou PDF) rédigée pour un lecteur métier ;
  - un **`README.md`** : description du projet, technologies, instructions pour monter la base et rejouer la chaîne, auteur(s).

## Modalités d'évaluation

Évaluation en deux volets :

- **Requêtes, notebook et croisement (60 %)** : correction du SQL avancé (CTE + fenêtrage), justesse du croisement sur la clé composite, exactitude du taux d'atteinte, rejouabilité de la chaîne.
- **Restitution orale (40 %)** : 10 minutes de présentation des constats à un « comité de direction » (le formateur et un autre binôme) + 5 minutes de questions, dont une démonstration que la chaîne se rejoue.

**Validation partielle** : un binôme dont le volet bonus n'est pas traité mais dont l'extraction SQL, le croisement et le raisonnement sur le taux d'atteinte sont corrects et documentés peut valider partiellement les compétences travaillées.

## Critères de performance

**Extraire par SQL avancé**
- La base est montée à partir de `setup.sql` et les requêtes s'exécutent sans erreur.
- Une CTE (`WITH …`) calcule le CA mensuel par magasin via les bonnes jointures.
- Une fonction de fenêtrage (classement `RANK`/`ROW_NUMBER` et/ou cumul `SUM() OVER`) est utilisée correctement et à bon escient.

**Charger et croiser plusieurs sources**
- Le fichier d'objectifs est chargé dans pandas avec des clés du bon type.
- Le croisement est fait sur la clé composite `magasin_id` + `mois`, sans perte de ligne silencieuse.
- Les lignes sans correspondance (magasin/mois orphelins) sont repérées et commentées.

**Produire l'indicateur et l'interpréter**
- Le taux d'atteinte (CA réel / objectif) est calculé par magasin et par mois.
- La table finale est exportée en CSV et rejouable.
- Les magasins sur- et sous-performants sont identifiés, et la progression sur l'année est lue via le cumul glissant.

**Restituer**
- La note de synthèse répond explicitement à la question centrale.
- Elle est rédigée sans jargon technique, avec des constats actionnables.
- Le dépôt GitHub public est complet (requêtes + notebook exécutable + CSV + README).

## Ressources

- Module de cours — [Collecte de données](../../../15-Business-Intelligence/14-Collecte-Donnees/)
- Rappels SQL — [Jointures](../../../01-Fondamentaux/SQL/03-Jointures/) · [Fonctions avancées (fenêtrage)](../../../01-Fondamentaux/SQL/05-Fonctions-Avancees/) · [Extraction & analyse](../../../01-Fondamentaux/SQL/09-Extraction-Analyse/)
- Documentation pandas — `merge` : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
- SQLite — expressions de table communes : https://www.sqlite.org/lang_with.html · fonctions de fenêtrage : https://www.sqlite.org/windowfunctions.html
- [Open-Meteo — Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (gratuite, sans clé) — *pour le bonus*
- Prochaine étape du parcours — projet de fin de phase : [BRIEF_1 — Tableau de bord métier](../BRIEF_1_TABLEAU_DE_BORD_METIER.md)
