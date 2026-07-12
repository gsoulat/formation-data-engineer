# Brief : Monitorer l'activité commerciale d'une enseigne retail avec SQL, Python et un tableau de bord BI

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | Environ une semaine (5 jours) |
| **Niveau** | Niveau 1 — IMITER / Niveau 2 — ADAPTER (selon les compétences) |
| **Modalité** | Binôme |
| **Outils** | SQL (SQLite ou PostgreSQL), Python (pandas), Power BI ou Looker Studio |
| **Certification** | RNCP-38616 — Concepteur développeur en IA et analyse big data, option Data Analyse, bloc BC06 |
| **Prérequis** | [Cours Business Intelligence](../../15-Business-Intelligence/), [SQL](../../01-Fondamentaux/SQL/), [Python](../../01-Fondamentaux/Python/) |

## Description rapide

En binôme, vous incarnez une cellule data missionnée par une enseigne de vente en ligne des Hauts-de-France. À partir d'un besoin métier de monitorage, vous extrayez les données de ventes (SQL + Python), menez une analyse exploratoire, identifiez les indicateurs clés, puis construisez un tableau de bord BI lisible (Power BI ou Looker Studio) que vous analysez et présentez. Objectif : passer d'un suivi manuel sur Excel à un monitorage fiable, visuel et reproductible de l'activité commerciale. Projet d'environ une semaine.

## Compétences visées et niveaux

- **C4.** Extraire des données via des scripts (SQL / Python) → Niveau 1 (IMITER)
- **C5.** Mener des analyses exploratoires (statistiques descriptives) → Niveau 1 (IMITER)
- **C6.** Identifier et interpréter des tendances → Niveau 1 (IMITER)
- **C11.** Élaborer la problématique métier → Niveau 1 (IMITER)
- **C16.** Identifier les indicateurs clés (KPI) → Niveau 2 (ADAPTER)
- **C17.** Choisir des visualisations pertinentes → Niveau 2 (ADAPTER)
- **C18.** Créer un tableau de bord BI → Niveau 2 (ADAPTER)
- **C15.** Présenter les résultats → Niveau 1 (IMITER)

## Contexte

**L'entreprise et son problème**

« NordGift » est une enseigne de vente en ligne basée à Roubaix (Hauts-de-France), spécialisée dans les objets cadeaux et la décoration, qui vend à la fois à des particuliers et à des revendeurs (clientèle grossiste). L'activité a fortement grandi mais le pilotage commercial est resté artisanal : chaque chargé de comptes tient son propre fichier Excel, les chiffres ne sont jamais consolidés de la même façon, et la direction attend chaque mois un reporting qui prend deux jours à fabriquer à la main. Résultat : personne ne sait dire en réunion quels produits tirent réellement le chiffre d'affaires, quels mois décrochent, ni quel poids prennent les retours et les annulations. Les décisions se prennent « au feeling ».

La direction commerciale vous mandate, en binôme, comme cellule data. Votre mission : remplacer ce suivi manuel par un monitorage fiable, visuel et reproductible de l'activité commerciale, restitué dans un tableau de bord BI lisible « en 30 secondes » par un décideur non technique.

**La question centrale**

Une seule question doit guider tout votre travail, de l'extraction à la restitution :
« Comment se porte l'activité commerciale de l'enseigne — quel chiffre d'affaires, sur quels produits, quels marchés et quelles périodes — et quelles tendances ou anomalies méritent l'attention de la direction ? »

À chaque étape, demandez-vous si ce que vous produisez aide à répondre à cette question. Tout ce qui n'y répond pas est hors périmètre pour cette phase.

**La source de données (réelle)**

Vous travaillez sur le jeu de données public « Online Retail » de l'UCI Machine Learning Repository : les transactions réelles d'un détaillant en ligne britannique entre le 01/12/2010 et le 09/12/2011.
- URL : https://archive.ics.uci.edu/dataset/352/online+retail
- Format : un fichier Excel (Online Retail.xlsx), environ 22 Mo.
- Volume : environ 541 909 lignes de transactions.
- Licence : Creative Commons Attribution 4.0.
- Colonnes : InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country.

Ce jeu contient quelques imperfections simples qu'il faudra repérer puis traiter avec un nettoyage léger : factures d'annulation (InvoiceNo commençant par « C ») et quantités négatives correspondant à des retours (à filtrer pour le calcul du CA), lignes sans CustomerID, prix unitaires nuls ou négatifs, descriptions manquantes, et éventuels doublons de lignes. Le traitement attendu se limite à du filtrage, à la suppression de doublons, à la gestion basique des valeurs manquantes et à des conversions de types/formats simples avec pandas (ou en SQL). Le montant d'une ligne se calcule par Quantity multiplié par UnitPrice.

Le nettoyage attendu reste léger (valeurs manquantes, doublons, types/formats simples) ; le nettoyage avancé (imputation sophistiquée, détection statistique d'anomalies, stratégies de traitement complexes) sera vu en Phase 3.

**Architecture et attendu**

Le flux attendu est simple et linéaire : Source (Excel) → Extraction & nettoyage léger (SQL et/ou Python pandas) → Analyse exploratoire (statistiques descriptives + tendances) → Tableau de bord BI (Power BI ou Looker Studio) → Note d'analyse. Vous chargerez le fichier dans une base SQL (SQLite ou PostgreSQL) pour écrire vos requêtes d'extraction, et/ou vous l'explorerez avec pandas. Le tableau de bord final est alimenté par un jeu de données propre, exporté en CSV. Il n'est pas demandé d'automatiser le pipeline à ce stade : la priorité est la justesse des chiffres, la pertinence des KPI et la lisibilité de la restitution.

## Modalités pédagogiques

Projet en BINÔME, sur environ une semaine (cinq jours). Le travail se fait sur un repository GitHub public partagé entre les deux membres. Répartissez-vous les tâches mais veillez à ce que chacun touche à l'extraction, à l'analyse et à la BI.

### Phase 1 — Cadrage et exploration, SANS CODE (J1)

On ne produit aucune ligne de code ce jour-là. Vous commencez par reformuler le besoin de la direction et la question centrale avec vos propres mots, comme si vous restituiez un entretien de recueil de besoin : qui consulte le tableau de bord, pour décider de quoi, à quelle fréquence ? Téléchargez le fichier et explorez-le « à la main » (Excel ou un aperçu rapide) pour comprendre ce que représente une ligne. Que signifie une facture qui commence par « C » ? Pourquoi certaines quantités sont-elles négatives ? Que faire des lignes sans CustomerID ? Documentez chaque colonne, son type, et les anomalies repérées dans une fiche source.

C'est aussi le moment de choisir vos indicateurs clés AVANT de coder. Quels trois à six KPI répondent réellement à la question centrale (par exemple chiffre d'affaires total, panier moyen, nombre de commandes, taux de retour, top produits, répartition par pays) ? Pour chaque KPI, écrivez sa définition : sa formule exacte, sa granularité, son éventuelle cible. Maquettez enfin votre tableau de bord sur papier ou sur un outil de croquis : quelle information en haut pour le décideur, quel détail en dessous ? Quel graphique pour quelle intention ? Finalisez la phase par un petit plan de travail (qui fait quoi, dans quel ordre).

### Phase 2 — Extraction et nettoyage des données (J2)

Vous passez au code. Chargez le fichier dans une base SQL (SQLite suffit) et/ou dans un DataFrame pandas. En vous appuyant sur les exemples fournis, écrivez des requêtes d'extraction ciblées : agrégations par mois, par produit, par pays. Le nettoyage reste léger et se fait avec les outils déjà vus (pandas / SQL de base) : filtrer les annulations et les retours du calcul du chiffre d'affaires, écarter les lignes manifestement invalides (prix nul ou négatif), supprimer les doublons, gérer simplement les valeurs manquantes (suppression ou marquage, sans imputation sophistiquée) et corriger les types/formats simples (dates, montants). Comment vérifiez-vous que vos totaux sont justes (contrôle de cohérence, comptage des lignes écartées) ? Documentez les règles de nettoyage que vous appliquez et le volume de données concerné. À la fin de la phase, vous disposez d'un jeu de données propre, exportable en CSV, et de vos scripts versionnés. (Le nettoyage avancé sera abordé en Phase 3.)

### Phase 3 — Analyse exploratoire et tendances (J3)

Menez l'EDA sur les données nettoyées. Calculez les statistiques descriptives pertinentes : tendance centrale (moyenne, médiane du panier), dispersion (écart-type, IQR), distribution des montants. La moyenne ou la médiane décrit-elle mieux le panier typique, et pourquoi ? Visualisez l'évolution mensuelle du chiffre d'affaires : voyez-vous une saisonnalité, un pic de fin d'année, une rupture ? Comparez les pays, identifiez les produits qui concentrent les ventes. Attention à ne pas confondre corrélation et causalité dans vos interprétations. Notez au fil de l'eau les constats qui parlent au métier : ce sont eux qui nourriront la note d'analyse.

### Phase 4 — Construction du tableau de bord BI (J4)

Construisez le tableau de bord dans Power BI ou Looker Studio, en partant de votre maquette du J1 et en adaptant le modèle de données et les indicateurs au contexte. Le décideur doit comprendre la situation en quelques secondes : KPI principaux en évidence (cartes), puis évolution dans le temps (courbe), comparaisons (barres), répartition géographique. Chaque graphique sert-il l'intention de lecture ? Vos titres sont-ils explicites, vos couleurs accessibles, vos axes honnêtes (pas tronqués) ? Ajoutez au moins un élément d'interactivité (filtre par période ou par pays). Reliez chaque visuel à un KPI défini en phase 1.

### Phase 5 — Analyse, restitution et présentation (J5)

Rédigez la note d'analyse qui répond explicitement à la question centrale et formule deux à trois recommandations concrètes pour la direction. Préparez une présentation courte adaptée à un public métier (storytelling data, pas de jargon). Entraînez-vous : vous devez pouvoir défendre vos choix de KPI et de visualisations.

## Modalités d'évaluation

L'évaluation se fait en binôme, sous deux formes complémentaires et pondérées.

**Démonstration et présentation orale (60 %)** : 12 minutes de présentation et démonstration live du tableau de bord, suivies de 8 minutes de questions. Vous présentez la question centrale, faites vivre le tableau de bord (filtres, lecture des KPI), exposez les tendances et anomalies détectées, et formulez vos recommandations. L'adaptation du discours au public métier est évaluée ici.

**Revue technique et documentation (40 %)** : examen du repository GitHub, des scripts SQL/Python, des règles de nettoyage documentées, des définitions de KPI et de la note d'analyse. La justesse des chiffres, la lisibilité du code et la traçabilité des choix priment.

Les deux membres du binôme doivent pouvoir expliquer n'importe quelle partie du travail ; une question peut être adressée individuellement.

**Clause de validation partielle** : un binôme dont le tableau de bord n'est pas totalement abouti en démonstration, mais dont les scripts d'extraction et d'analyse sont structurés, justes et documentés, peut valider partiellement les compétences C4, C5 et C6. À l'inverse, un tableau de bord soigné mais bâti sur des chiffres faux (annulations non exclues, retours comptés en CA) ne valide pas C16 et C18. Les compétences sont évaluées indépendamment les unes des autres.

## Livrables attendus

Un repository GitHub public, partagé par le binôme, contenant l'ensemble du travail. Il doit inclure :

- Un README.md complet : description du projet et de la question centrale, technologies utilisées, instructions pour reproduire l'analyse (téléchargement du dataset, lancement des scripts), aperçu du tableau de bord (capture d'écran ou lien), et les deux auteurs.
- Les scripts SQL d'extraction et d'agrégation (fichiers .sql) et/ou le notebook Python (pandas) d'extraction et de nettoyage, exécutables et commentés.
- Le notebook ou script d'analyse exploratoire (statistiques descriptives, graphiques, interprétations).
- Le jeu de données nettoyé exporté en CSV (ou le script qui le régénère).
- Le fichier du tableau de bord : fichier Power BI (.pbix) OU lien public partageable vers le rapport Looker Studio. Joindre dans tous les cas une capture d'écran du tableau de bord dans le repo.
- La fiche source et le dictionnaire des KPI : description de chaque colonne, anomalies repérées, et pour chaque KPI sa formule, sa granularité et sa cible éventuelle (fichier Markdown).
- La note d'analyse (1 à 2 pages, Markdown ou PDF) : réponse argumentée à la question centrale, tendances et anomalies, et deux à trois recommandations pour la direction.
- Le support de présentation orale (PDF ou lien).

Pas de données personnelles sensibles : le dataset est public et anonymisé (CustomerID numérique).

## Critères de performance

**C4. Extraire des données via des scripts (Niveau 1)**
- Le dataset est chargé dans une base SQL et/ou un DataFrame pandas de façon reproductible : OUI / NON
- Des requêtes d'extraction et d'agrégation (par mois, produit, pays) sont écrites et fonctionnent : OUI / NON
- Les annulations et retours sont correctement exclus du calcul du chiffre d'affaires : OUI / NON
- L'exactitude des données extraites est vérifiée (comptages, contrôles de cohérence) : OUI / NON

**C5. Mener des analyses exploratoires (Niveau 1)**
- Les statistiques de tendance centrale (moyenne, médiane) sont calculées et correctes : OUI / NON
- La dispersion est mesurée (écart-type et/ou IQR) : OUI / NON
- La distribution des montants est explorée (histogramme, quantiles) : OUI / NON
- Les valeurs manifestement aberrantes sont repérées et signalées (sans traitement statistique avancé, réservé à la Phase 3) : OUI / NON

**C6. Identifier et interpréter des tendances (Niveau 1)**
- L'évolution temporelle du chiffre d'affaires est analysée (saisonnalité, pics) : OUI / NON
- Des comparaisons entre groupes (pays, produits) sont menées : OUI / NON
- Les interprétations sont contextualisées pour le métier sans confondre corrélation et causalité : OUI / NON

**C11. Élaborer la problématique métier (Niveau 1)**
- Le besoin de la direction est reformulé et la question centrale est explicitée : OUI / NON
- Le périmètre, les utilisateurs et la fréquence de consultation sont précisés : OUI / NON
- Le besoin flou est traduit en questions analytiques mesurables : OUI / NON

**C16. Identifier les indicateurs clés (Niveau 2)**
- Trois à six KPI pertinents répondant à la question centrale sont définis : OUI / NON
- Chaque KPI dispose d'une formule, d'une granularité et d'une cible éventuelle : OUI / NON
- Les KPI sont choisis et structurés avant la construction du tableau de bord : OUI / NON

**C17. Choisir des visualisations pertinentes (Niveau 2)**
- Chaque graphique est adapté à la nature de la donnée et à l'intention : OUI / NON
- Les pièges visuels sont évités (camembert surchargé, axe tronqué, 3D inutile) : OUI / NON
- Les choix d'accessibilité sont respectés (titres explicites, contrastes, palette) : OUI / NON

**C18. Créer un tableau de bord BI (Niveau 2)**
- Le tableau de bord est construit dans Power BI ou Looker Studio à partir de données propres : OUI / NON
- Les KPI principaux sont mis en évidence et lisibles « en 30 secondes » : OUI / NON
- Au moins un élément d'interactivité fonctionne (filtre, segment) : OUI / NON
- Les chiffres affichés sont exacts et cohérents avec l'analyse : OUI / NON

**C15. Présenter les résultats (Niveau 1)**
- La présentation répond explicitement à la question centrale : OUI / NON
- Le discours est adapté à un public métier (storytelling, pas de jargon) : OUI / NON
- Deux à trois recommandations concrètes sont formulées : OUI / NON

## Ressources

- Jeu de données Online Retail (UCI) : https://archive.ics.uci.edu/dataset/352/online+retail
- Alternative — Brazilian E-Commerce Olist (Kaggle) : https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Documentation pandas : https://pandas.pydata.org/docs/
- Power BI — Apprentissage Microsoft Learn : https://learn.microsoft.com/fr-fr/power-bi/
- Looker Studio — Aide officielle : https://support.google.com/looker-studio
- SQLite — documentation : https://www.sqlite.org/docs.html
- Choisir le bon graphique (From Data to Viz) : https://www.data-to-viz.com/
- Statistiques descriptives (rappels) : https://fr.wikipedia.org/wiki/Statistique_descriptive
