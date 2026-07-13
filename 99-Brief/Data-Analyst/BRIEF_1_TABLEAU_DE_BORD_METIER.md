# Brief : Monitorer l'activité commerciale d'une enseigne retail avec SQL, Python et un tableau de bord BI

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | Environ une semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Binôme |
| **Outils** | SQL (SQLite ou PostgreSQL), Python (pandas), Power BI ou Looker Studio |
| **Prérequis** | [Cours Business Intelligence](../../15-Business-Intelligence/), [SQL](../../01-Fondamentaux/SQL/), [Python](../../01-Fondamentaux/Python/) |

## Description rapide

En binôme, vous incarnez une cellule data missionnée par une enseigne de vente en ligne des Hauts-de-France. À partir d'un besoin métier de monitorage, vous extrayez les données de ventes (SQL + Python), menez une analyse exploratoire, identifiez les indicateurs clés, puis construisez un tableau de bord BI lisible (Power BI ou Looker Studio) que vous analysez et présentez. Objectif : passer d'un suivi manuel sur Excel à un monitorage fiable, visuel et reproductible de l'activité commerciale. Projet d'environ une semaine.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Extraire des données via des scripts** SQL (SQLite ou PostgreSQL) et/ou Python (pandas), de façon reproductible et vérifiable.
- **Mener une analyse exploratoire** : produire et interpréter des statistiques descriptives (tendance centrale, dispersion, distribution des montants).
- **Identifier et interpréter des tendances** : évolution temporelle, saisonnalité, comparaisons entre villes, canaux et produits, sans confondre corrélation et causalité.
- **Élaborer une problématique métier** : reformuler un besoin flou en question centrale et en questions analytiques mesurables.
- **Définir des indicateurs clés (KPI)** adaptés au besoin, avec pour chacun une formule, une granularité et une cible éventuelle.
- **Concevoir un tableau de bord BI lisible et accessible** (Power BI ou Looker Studio), puis restituer les résultats à un public métier sans jargon.

## Contexte

**L'entreprise et son problème**

« NordRetail » est une enseigne de distribution des Hauts-de-France : six magasins (Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes, Amiens) et un canal e-commerce, sur plusieurs catégories de produits. L'activité a fortement grandi mais le pilotage commercial est resté artisanal : chaque responsable tient son propre fichier Excel, les chiffres ne sont jamais consolidés de la même façon, et la direction attend chaque mois un reporting qui prend deux jours à fabriquer à la main. Résultat : personne ne sait dire en réunion quels produits tirent réellement le chiffre d'affaires, quels magasins ou canaux décrochent, ni quel poids prennent les retours. Les décisions se prennent « au feeling ».

La direction commerciale vous mandate, en binôme, comme cellule data. Votre mission : remplacer ce suivi manuel par un monitorage fiable, visuel et reproductible de l'activité commerciale, restitué dans un tableau de bord BI lisible « en 30 secondes » par un décideur non technique.

**La question centrale**

Une seule question doit guider tout votre travail, de l'extraction à la restitution :
« Comment se porte l'activité commerciale de l'enseigne — quel chiffre d'affaires, sur quels produits, quels marchés et quelles périodes — et quelles tendances ou anomalies méritent l'attention de la direction ? »

À chaque étape, demandez-vous si ce que vous produisez aide à répondre à cette question. Tout ce qui n'y répond pas est hors périmètre pour cette phase.

**La source de données (fournie)**

Vous travaillez sur le jeu de données **NordRetail** fourni dans le dossier [`data/`](data/) de ce brief (univers fictif mais réaliste, 100 % reproductible, aucune donnée personnelle réelle). Vous partez de la version **brute** des ventes :
- Fichier : `data/ventes_sales.csv` (version « sale » des ventes ; la version propre `data/ventes_magasins.csv` peut servir de contrôle).
- Volume : ~12 000 ventes sur 2023-2024, chiffre d'affaires ~14,4 M€.
- Colonnes : `date, ville, type, categorie, produit, quantite, prix_unitaire, remise, montant, marge, client_id`.
- **Aucun téléchargement** : les fichiers sont déjà dans `data/` (voir `data/README.md`).

Ce fichier contient quelques imperfections simples qu'il faudra repérer puis traiter avec un nettoyage léger : **retours** (montants ou quantités négatifs, à filtrer pour le calcul du CA), lignes sans `client_id`, casse incohérente des villes (`LILLE` / `roubaix` / `Valencienne`), formats de date mélangés, décimales à virgule, prix ou remises aberrants, et doublons de lignes. Le traitement attendu se limite à du filtrage, à la suppression de doublons, à la gestion basique des valeurs manquantes et à des conversions de types/formats simples avec pandas (ou en SQL). Le montant d'une ligne est fourni (`montant`) ; vous pouvez le recontrôler à partir de `quantite`, `prix_unitaire` et `remise`.

Le nettoyage attendu reste léger (valeurs manquantes, doublons, types/formats simples) ; le nettoyage avancé (imputation sophistiquée, détection statistique d'anomalies, stratégies de traitement complexes) sera vu en Phase 3.

**Architecture et attendu**

Le flux attendu est simple et linéaire : Source (Excel) → Extraction & nettoyage léger (SQL et/ou Python pandas) → Analyse exploratoire (statistiques descriptives + tendances) → Tableau de bord BI (Power BI ou Looker Studio) → Note d'analyse. Vous chargerez le fichier dans une base SQL (SQLite ou PostgreSQL) pour écrire vos requêtes d'extraction, et/ou vous l'explorerez avec pandas. Le tableau de bord final est alimenté par un jeu de données propre, exporté en CSV. Il n'est pas demandé d'automatiser le pipeline à ce stade : la priorité est la justesse des chiffres, la pertinence des KPI et la lisibilité de la restitution.

## Modalités pédagogiques

Projet en BINÔME, sur environ une semaine (cinq jours). Le travail se fait sur un repository GitHub public partagé entre les deux membres. Répartissez-vous les tâches mais veillez à ce que chacun touche à l'extraction, à l'analyse et à la BI.

### Phase 1 — Cadrage et exploration, SANS CODE (J1)

On ne produit aucune ligne de code ce jour-là. Vous commencez par reformuler le besoin de la direction et la question centrale avec vos propres mots, comme si vous restituiez un entretien de recueil de besoin : qui consulte le tableau de bord, pour décider de quoi, à quelle fréquence ? Ouvrez le fichier fourni `data/ventes_sales.csv` et explorez-le « à la main » (tableur ou aperçu pandas) pour comprendre ce que représente une ligne. Que signifient les montants ou quantités négatifs (des retours) ? Pourquoi une même ville est-elle parfois écrite `LILLE`, `roubaix`, `Valencienne` ? Que faire des lignes sans `client_id` ? Documentez chaque colonne, son type, et les anomalies repérées dans une fiche source.

C'est aussi le moment de choisir vos indicateurs clés AVANT de coder. Quels trois à six KPI répondent réellement à la question centrale (par exemple chiffre d'affaires total, panier moyen, nombre de commandes, taux de retour, top produits, répartition par ville ou par canal) ? Pour chaque KPI, écrivez sa définition : sa formule exacte, sa granularité, son éventuelle cible. Maquettez enfin votre tableau de bord sur papier ou sur un outil de croquis : quelle information en haut pour le décideur, quel détail en dessous ? Quel graphique pour quelle intention ? Finalisez la phase par un petit plan de travail (qui fait quoi, dans quel ordre).

### Phase 2 — Extraction et nettoyage des données (J2)

Vous passez au code. Chargez le fichier dans une base SQL (SQLite suffit) et/ou dans un DataFrame pandas. En vous appuyant sur les exemples fournis, écrivez des requêtes d'extraction ciblées : agrégations par mois, par produit ou catégorie, par ville et par canal (`type`). Le nettoyage reste léger et se fait avec les outils déjà vus (pandas / SQL de base) : filtrer les retours (montants ou quantités négatifs) du calcul du chiffre d'affaires, écarter les lignes manifestement invalides (prix nul ou négatif), supprimer les doublons, gérer simplement les valeurs manquantes (suppression ou marquage, sans imputation sophistiquée) et corriger les types/formats simples (dates, montants). Comment vérifiez-vous que vos totaux sont justes (contrôle de cohérence, comptage des lignes écartées) ? Documentez les règles de nettoyage que vous appliquez et le volume de données concerné. À la fin de la phase, vous disposez d'un jeu de données propre, exportable en CSV, et de vos scripts versionnés. (Le nettoyage avancé sera abordé en Phase 3.)

### Phase 3 — Analyse exploratoire et tendances (J3)

Menez l'EDA sur les données nettoyées. Calculez les statistiques descriptives pertinentes : tendance centrale (moyenne, médiane du panier), dispersion (écart-type, IQR), distribution des montants. La moyenne ou la médiane décrit-elle mieux le panier typique, et pourquoi ? Visualisez l'évolution mensuelle du chiffre d'affaires : voyez-vous une saisonnalité, un pic de fin d'année, une rupture ? Comparez les villes et les canaux (magasin vs e-commerce), identifiez les produits et catégories qui concentrent les ventes. Attention à ne pas confondre corrélation et causalité dans vos interprétations. Notez au fil de l'eau les constats qui parlent au métier : ce sont eux qui nourriront la note d'analyse.

### Phase 4 — Construction du tableau de bord BI (J4)

Construisez le tableau de bord dans Power BI ou Looker Studio, en partant de votre maquette du J1 et en adaptant le modèle de données et les indicateurs au contexte. Le décideur doit comprendre la situation en quelques secondes : KPI principaux en évidence (cartes), puis évolution dans le temps (courbe), comparaisons (barres), répartition géographique par ville. Chaque graphique sert-il l'intention de lecture ? Vos titres sont-ils explicites, vos couleurs accessibles, vos axes honnêtes (pas tronqués) ? Ajoutez au moins un élément d'interactivité (filtre par période, par ville ou par canal). Reliez chaque visuel à un KPI défini en phase 1.

### Phase 5 — Analyse, restitution et présentation (J5)

Rédigez la note d'analyse qui répond explicitement à la question centrale et formule deux à trois recommandations concrètes pour la direction. Préparez une présentation courte adaptée à un public métier (storytelling data, pas de jargon). Entraînez-vous : vous devez pouvoir défendre vos choix de KPI et de visualisations.

## Modalités d'évaluation

L'évaluation se fait en binôme, sous deux formes complémentaires et pondérées.

**Démonstration et présentation orale (60 %)** : 12 minutes de présentation et démonstration live du tableau de bord, suivies de 8 minutes de questions. Vous présentez la question centrale, faites vivre le tableau de bord (filtres, lecture des KPI), exposez les tendances et anomalies détectées, et formulez vos recommandations. L'adaptation du discours au public métier est évaluée ici.

**Revue technique et documentation (40 %)** : examen du repository GitHub, des scripts SQL/Python, des règles de nettoyage documentées, des définitions de KPI et de la note d'analyse. La justesse des chiffres, la lisibilité du code et la traçabilité des choix priment.

Les deux membres du binôme doivent pouvoir expliquer n'importe quelle partie du travail ; une question peut être adressée individuellement.

**Clause de validation partielle** : un binôme dont le tableau de bord n'est pas totalement abouti en démonstration, mais dont les scripts d'extraction et d'analyse sont structurés, justes et documentés, peut valider partiellement les acquis liés à l'extraction et à l'analyse exploratoire. À l'inverse, un tableau de bord soigné mais bâti sur des chiffres faux (retours comptés dans le CA, doublons non traités) ne valide pas la définition des KPI ni la construction du tableau de bord. Chaque acquis est évalué indépendamment des autres.

## Livrables attendus

Un repository GitHub public, partagé par le binôme, contenant l'ensemble du travail. Il doit inclure :

- Un README.md complet : description du projet et de la question centrale, technologies utilisées, instructions pour reproduire l'analyse (les données sont fournies dans `data/`, lancement des scripts), aperçu du tableau de bord (capture d'écran ou lien), et les deux auteurs.
- Les scripts SQL d'extraction et d'agrégation (fichiers .sql) et/ou le notebook Python (pandas) d'extraction et de nettoyage, exécutables et commentés.
- Le notebook ou script d'analyse exploratoire (statistiques descriptives, graphiques, interprétations).
- Le jeu de données nettoyé exporté en CSV (ou le script qui le régénère).
- Le fichier du tableau de bord : fichier Power BI (.pbix) OU lien public partageable vers le rapport Looker Studio. Joindre dans tous les cas une capture d'écran du tableau de bord dans le repo.
- La fiche source et le dictionnaire des KPI : description de chaque colonne, anomalies repérées, et pour chaque KPI sa formule, sa granularité et sa cible éventuelle (fichier Markdown).
- La note d'analyse (1 à 2 pages, Markdown ou PDF) : réponse argumentée à la question centrale, tendances et anomalies, et deux à trois recommandations pour la direction.
- Le support de présentation orale (PDF ou lien).

Pas de données personnelles réelles : le jeu NordRetail est 100 % synthétique (`client_id` numérique fictif).

## Critères de performance

**Extraire des données via des scripts**
- Le dataset est chargé dans une base SQL et/ou un DataFrame pandas de façon reproductible : OUI / NON
- Des requêtes d'extraction et d'agrégation (par mois, produit, ville, canal) sont écrites et fonctionnent : OUI / NON
- Les retours (montants ou quantités négatifs) sont correctement exclus du calcul du chiffre d'affaires : OUI / NON
- L'exactitude des données extraites est vérifiée (comptages, contrôles de cohérence) : OUI / NON

**Mener une analyse exploratoire**
- Les statistiques de tendance centrale (moyenne, médiane) sont calculées et correctes : OUI / NON
- La dispersion est mesurée (écart-type et/ou IQR) : OUI / NON
- La distribution des montants est explorée (histogramme, quantiles) : OUI / NON
- Les valeurs manifestement aberrantes sont repérées et signalées (sans traitement statistique avancé, réservé à la Phase 3) : OUI / NON

**Identifier et interpréter des tendances**
- L'évolution temporelle du chiffre d'affaires est analysée (saisonnalité, pics) : OUI / NON
- Des comparaisons entre groupes (villes, canaux, produits) sont menées : OUI / NON
- Les interprétations sont contextualisées pour le métier sans confondre corrélation et causalité : OUI / NON

**Élaborer la problématique métier**
- Le besoin de la direction est reformulé et la question centrale est explicitée : OUI / NON
- Le périmètre, les utilisateurs et la fréquence de consultation sont précisés : OUI / NON
- Le besoin flou est traduit en questions analytiques mesurables : OUI / NON

**Identifier les indicateurs clés (KPI)**
- Trois à six KPI pertinents répondant à la question centrale sont définis : OUI / NON
- Chaque KPI dispose d'une formule, d'une granularité et d'une cible éventuelle : OUI / NON
- Les KPI sont choisis et structurés avant la construction du tableau de bord : OUI / NON

**Choisir des visualisations pertinentes**
- Chaque graphique est adapté à la nature de la donnée et à l'intention : OUI / NON
- Les pièges visuels sont évités (camembert surchargé, axe tronqué, 3D inutile) : OUI / NON
- Les choix d'accessibilité sont respectés (titres explicites, contrastes, palette) : OUI / NON

**Créer un tableau de bord BI**
- Le tableau de bord est construit dans Power BI ou Looker Studio à partir de données propres : OUI / NON
- Les KPI principaux sont mis en évidence et lisibles « en 30 secondes » : OUI / NON
- Au moins un élément d'interactivité fonctionne (filtre, segment) : OUI / NON
- Les chiffres affichés sont exacts et cohérents avec l'analyse : OUI / NON

**Présenter les résultats**
- La présentation répond explicitement à la question centrale : OUI / NON
- Le discours est adapté à un public métier (storytelling, pas de jargon) : OUI / NON
- Deux à trois recommandations concrètes sont formulées : OUI / NON

## Ressources

- Jeux de données **NordRetail** fournis : [`data/`](data/) (voir `data/README.md` pour le dictionnaire des colonnes)
- Documentation pandas : https://pandas.pydata.org/docs/
- Power BI — Apprentissage Microsoft Learn : https://learn.microsoft.com/fr-fr/power-bi/
- Looker Studio — Aide officielle : https://support.google.com/looker-studio
- SQLite — documentation : https://www.sqlite.org/docs.html
- Choisir le bon graphique (From Data to Viz) : https://www.data-to-viz.com/
- Statistiques descriptives (rappels) : https://fr.wikipedia.org/wiki/Statistique_descriptive
