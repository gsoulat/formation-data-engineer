# Brief : Solution BI avancée — Modèle en étoile, mesures DAX et tableau de bord décisionnel e-commerce

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | Environ 2 semaines (J1 à J10) |
| **Niveau** | Niveau 2 — ADAPTER (Phase 2) |
| **Modalité** | Binôme ou petit groupe (2 à 3 personnes) |
| **Outils** | Power BI : Power Query + DAX ; modèle en étoile (alternative : Looker Studio) ; Python (pandas) pour l'analyse exploratoire |
| **Certification** | RNCP-38616 — Concepteur développeur en IA et analyse big data, option Data Analyse, bloc BC06 |
| **Prérequis** | [Cours Business Intelligence](../../15-Business-Intelligence/), [SQL](../../01-Fondamentaux/SQL/), [Python](../../01-Fondamentaux/Python/) |

## Description rapide

Vous intégrez la cellule data d'un acteur e-commerce des Hauts-de-France. Votre mission, en binôme ou petit groupe sur deux semaines : transformer un jeu de données multi-tables en une véritable solution de Business Intelligence. Vous modéliserez les données en étoile, construirez des mesures avancées (DAX ou équivalent), concevrez un tableau de bord interactif répondant à une question de décision, et accompagnerez une équipe métier dans sa prise en main. Vous traiterez aussi les enjeux de conformité RGPD et de biais. À la clé : passer d'un tableur figé à un outil d'aide à la décision fiable, lisible et partageable.

## Compétences visées et niveaux

- C5. Réaliser des analyses exploratoires → Niveau 2 (ADAPTER)
- C6. Identifier et interpréter des tendances → Niveau 2 (ADAPTER)
- C11. Élaborer la problématique métier → Niveau 2 (ADAPTER)
- C12. Évaluer les risques (RGPD, éthique, biais) → Niveau 1 (IMITER)
- C16. Identifier les indicateurs clés (KPI) → Niveau 2 (ADAPTER)
- C17. Choisir des visualisations pertinentes → Niveau 2 (ADAPTER)
- C18. Créer un tableau de bord BI → Niveau 2 (ADAPTER)
- C15. Présenter les résultats → Niveau 2 (ADAPTER)

Rappel des niveaux : Niveau 1 (IMITER) = vous reproduisez à partir d'un exemple fourni ; Niveau 2 (ADAPTER) = vous adaptez à ce nouveau contexte avec les ressources fournies.

## Contexte

NordShop est une enseigne e-commerce fictive mais réaliste, basée à Roubaix, spécialisée dans la vente en ligne de produits maison, mode et loisirs. En forte croissance, elle a centralisé ces dernières années toutes ses commandes, ses paiements et ses avis clients dans une base de données opérationnelle. Le problème : la direction et les responsables métier n'ont aujourd'hui aucune vision consolidée. Chaque service produit ses propres extractions Excel, les chiffres ne concordent jamais d'une réunion à l'autre, et personne ne sait dire en quelques secondes quels produits, quelles régions ou quels modes de paiement tirent réellement la croissance. Le reporting mensuel se fabrique à la main en deux jours et n'est jamais à jour.

La direction de NordShop vous mandate, en tant que cellule data, pour concevoir une solution de Business Intelligence pérenne. L'enjeu n'est pas un simple graphique : c'est une vraie modélisation analytique, des indicateurs fiables et un outil que les équipes métier pourront s'approprier.

Question centrale qui doit guider tout votre projet :
« Quels sont les leviers de performance commerciale de NordShop — par produit, par région et par parcours d'achat — et comment leur évolution dans le temps doit-elle orienter les décisions de la direction ? »

Tout choix d'indicateur, de visualisation ou d'analyse devra pouvoir se justifier au regard de cette question.

Source de données réelle imposée : le Brazilian E-Commerce Public Dataset by Olist, publié sur Kaggle. Vous le rebaptiserez NordShop et le ré-contextualiserez aux Hauts-de-France pour le storytelling (les villes/états brésiliens jouent le rôle de zones de livraison).
URL : https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Caractéristiques de la source :
- Format : 9 fichiers CSV liés entre eux par des clés.
- Volume : environ 100 000 commandes, plus de 110 000 lignes d'articles, sur la période 2016-2018.
- Tables principales : olist\_orders\_dataset (commandes), olist\_order\_items\_dataset (lignes d'articles), olist\_products\_dataset (produits), olist\_customers\_dataset (clients), olist\_sellers\_dataset (vendeurs), olist\_order\_payments\_dataset (paiements), olist\_order\_reviews\_dataset (avis), olist\_geolocation\_dataset (géolocalisation) et product\_category\_name\_translation (libellés de catégories).
- Anomalies naturelles présentes : valeurs manquantes sur certaines dates de livraison, doublons de géolocalisation, catégories non traduites, avis sans commentaire. Ces imperfections font partie de l'exercice.

Architecture analytique attendue : un modèle en étoile (star schema). Vous devrez identifier une table de faits centrale (par exemple les lignes d'articles de commande, porteuses des mesures : prix, frais de port, quantité) entourée de tables de dimensions (Date, Produit/Catégorie, Client, Vendeur, Géographie, Paiement). Les tables très dénormalisées d'Olist devront être restructurées pour servir cette modélisation. C'est ce modèle qui rendra possibles des mesures avancées performantes.

Conformité : bien que les données Olist soient anonymisées, vous traiterez le projet comme s'il portait sur des clients réels de NordShop. Vous devrez donc identifier les données à caractère personnel, vérifier la base légale et la durée de conservation au sens du RGPD, et repérer les biais possibles (sur-représentation de certaines régions, périodes incomplètes) qui pourraient fausser les décisions.

Vous ne disposez pas d'une solution clé en main : ce brief pose le cadre, à vous de construire le contenu.

## Modalités pédagogiques

Projet en binôme ou petit groupe (2 à 3 personnes), sur environ deux semaines (J1 à J10). Le travail s'organise autour d'un dépôt GitHub commun et d'un tableau de suivi (Kanban). Chaque phase produit un résultat concret et présentable.

Phase 1 — Cadrage et modélisation sur papier (J1-J2). Aucune construction d'outil à ce stade. Vous commencez par un atelier de recueil du besoin : le formateur jouera le rôle du commanditaire métier (direction NordShop) lors d'un court entretien. À vous de poser les bonnes questions pour cerner ce que la direction veut vraiment décider. Qu'attend précisément le commanditaire ? Quelles décisions le tableau de bord doit-il éclairer ? Vous formaliserez ensuite un cahier des charges : objectifs, périmètre, public visé, indicateurs pressentis et livrables. Puis vous explorerez les 9 fichiers CSV pour comprendre leur contenu et leurs liens, et vous dessinerez votre modèle en étoile sur papier ou sur un outil de schéma. Quelle table choisissez-vous comme table de faits et pourquoi ? Quelles dimensions allez-vous construire ? Comment relier produits, clients et géographie ? Ce schéma validé conditionne toute la suite.

Phase 2 — Analyse exploratoire et tendances (J3-J4). Avant de visualiser, comprenez vos données avec Python (pandas, matplotlib/seaborn). Vous menez une analyse exploratoire : statistiques descriptives (tendance centrale, dispersion), distributions, détection de valeurs aberrantes sur les montants et les délais. Quelles variables présentent des outliers ? Faut-il les écarter ou les conserver, et pourquoi ? Vous analysez ensuite les tendances : évolution du chiffre d'affaires dans le temps, saisonnalité, comparaison entre régions ou catégories, éventuelles corrélations (par exemple entre délai de livraison et note d'avis). Attention à ne pas confondre corrélation et causalité. Que racontent ces tendances au regard de la question centrale ?

Phase 3 — Modèle en étoile et mesures avancées (J5-J7). Vous construisez la solution BI dans Power BI (recommandé pour l'employabilité) ou Looker Studio. Vous importez et préparez les tables (Power Query), puis vous implémentez votre modèle en étoile : relations entre faits et dimensions, table de dates dédiée. Vous développez ensuite des mesures avancées : chiffre d'affaires total, panier moyen, cumul à date, évolution par rapport à la période précédente, taux de retour ou de satisfaction, classement des catégories. En Power BI ces mesures s'écrivent en DAX ; documentez chacune (nom, formule, intention métier). Comment gérez-vous l'intelligence temporelle ? Vos mesures donnent-elles les mêmes totaux que votre analyse Python ? Cette cohérence est un gage de fiabilité.

Phase 4 — Tableau de bord interactif et choix des visualisations (J7-J8). Vous concevez le tableau de bord en partant des KPI identifiés. Structurez une arborescence lisible : une vue direction synthétique (les KPI clés visibles en 30 secondes) puis des vues de détail. Pour chaque indicateur, choisissez la visualisation adaptée à l'intention (comparaison, évolution, répartition, distribution, relation) et évitez les pièges (camembert surchargé, axe tronqué, 3D inutile). Ajoutez de l'interactivité : filtres, segments, drill-down, info-bulles. Pensez accessibilité (contrastes, palettes adaptées au daltonisme, titres explicites).

Phase 5 — RGPD, biais et atelier métier (J9). Vous rédigez une note de conformité : quelles données sont personnelles, quelle base légale, quelle durée de conservation, quelles mesures de minimisation ? Vous identifiez les biais du jeu de données (représentativité régionale, période incomplète) et leur impact sur les décisions. Puis vous animez un atelier de prise en main : vous accompagnez une équipe métier (vos pairs ou le formateur) dans l'utilisation du tableau de bord, recueillez leurs retours et ajustez. Comment expliquez-vous un KPI à une personne non technique ?

Phase 6 — Restitution (J10). Vous préparez et répétez une présentation orientée décision, adaptée à un public de direction, avec un fil narratif clair (storytelling data).

## Modalités d'évaluation

L'évaluation se déroule en fin de projet, par binôme/groupe, et combine deux volets pondérés :

- Démonstration et soutenance (70 %) : 15 minutes de présentation live du tableau de bord et des analyses, face à un jury jouant le rôle de la direction NordShop, suivies de 10 minutes de questions. Sont évalués : la pertinence des KPI et des visualisations, l'interactivité du tableau de bord, la qualité de l'analyse des tendances, la clarté du storytelling et l'adaptation du discours au public métier, ainsi que la prise en compte du RGPD et des biais.

- Revue du dépôt et des livrables (30 %) : examen du dépôt GitHub, du cahier des charges, du modèle de données, de la documentation des mesures DAX, du notebook d'analyse et de la note RGPD/biais. Sont évaluées la structuration, la reproductibilité et la qualité de documentation.

Chaque membre du groupe doit pouvoir expliquer l'ensemble de la solution : des questions individuelles pourront être posées.

Clause de validation partielle : un groupe dont le tableau de bord présente des limites en démonstration (mesure incomplète, interactivité partielle) mais dont la démarche est structurée, le modèle en étoile cohérent et les livrables documentés pourra valider partiellement les compétences concernées. Le travail rigoureux et documenté est valorisé, pas seulement le résultat parfait.

## Livrables attendus

Livrable principal : un dépôt GitHub public commun au groupe, contenant un README structuré :
- Description du projet et question centrale
- Technologies utilisées
- Instructions de reproduction (chargement des données, ouverture du fichier BI)
- Architecture (modèle en étoile)
- Auteurs (membres du groupe)

Le dépôt et les livrables associés doivent inclure :
- Le cahier des charges issu de la phase de cadrage (objectifs, périmètre, public, KPI, livrables).
- Le modèle de données : schéma du modèle en étoile (image ou fichier de schéma) avec faits, dimensions et relations, et une brève justification des choix.
- Le notebook Python d'analyse exploratoire et de tendances (statistiques descriptives, détection d'outliers, analyse temporelle, corrélations), commenté.
- La documentation des mesures avancées : pour chaque mesure DAX (ou équivalent), son nom, sa formule et son intention métier.
- Le fichier du tableau de bord interactif (fichier .pbix ou lien Looker Studio partagé) avec une vue synthèse et des vues de détail, filtres et drill-down. Joindre des captures d'écran dans le dépôt.
- La note RGPD et biais : données personnelles identifiées, base légale, durée de conservation, mesures de minimisation, biais repérés et leur impact sur la décision.
- Le tableau de bord de suivi (Kanban) du projet, avec les tâches et leur historique.
- Les supports de l'atelier métier et de la restitution finale.

## Critères de performance

C5. Réaliser des analyses exploratoires (Niveau 2)
- Les statistiques descriptives (tendance centrale et dispersion) sont calculées sur les variables clés. OUI / NON
- Les distributions sont visualisées (histogramme, boxplot). OUI / NON
- Les valeurs aberrantes sont détectées et le traitement choisi est justifié. OUI / NON

C6. Identifier et interpréter des tendances (Niveau 2)
- Une analyse temporelle (évolution, saisonnalité) est réalisée et interprétée. OUI / NON
- Au moins une comparaison de groupes ou une corrélation est produite. OUI / NON
- Les résultats sont reliés à la question centrale sans confondre corrélation et causalité. OUI / NON

C11. Élaborer la problématique métier (Niveau 2)
- Un entretien de recueil du besoin a été conduit. OUI / NON
- Un cahier des charges formalise objectifs, périmètre, public et livrables. OUI / NON
- Le besoin est traduit en questions analytiques mesurables. OUI / NON

C12. Évaluer les risques RGPD, éthique et biais (Niveau 1)
- Les données à caractère personnel sont identifiées. OUI / NON
- Base légale et durée de conservation sont mentionnées. OUI / NON
- Au moins un biais du jeu de données est identifié avec son impact. OUI / NON

C16. Identifier les indicateurs clés (Niveau 2)
- Les KPI sont définis (formule, granularité, fréquence, cible). OUI / NON
- Les KPI répondent directement à la question centrale. OUI / NON
- Une arborescence vue direction puis détail est proposée. OUI / NON

C17. Choisir des visualisations pertinentes (Niveau 2)
- Chaque visualisation est adaptée à l'intention et à la nature de la donnée. OUI / NON
- Les pièges courants sont évités (camembert surchargé, axe tronqué, 3D). OUI / NON
- L'accessibilité est prise en compte (contraste, palette, titres explicites). OUI / NON

C18. Créer un tableau de bord BI (Niveau 2)
- Un modèle en étoile (faits + dimensions + relations) est implémenté. OUI / NON
- Des mesures avancées (DAX ou équivalent) sont créées et documentées. OUI / NON
- Le tableau de bord est interactif (filtres, segments, drill-down). OUI / NON
- Les totaux du tableau de bord concordent avec l'analyse Python. OUI / NON

C15. Présenter les résultats (Niveau 2)
- Le discours est adapté à un public de direction non technique. OUI / NON
- Un fil narratif (storytelling data) structure la présentation. OUI / NON
- Un atelier d'accompagnement de l'équipe métier a été mené. OUI / NON

## Ressources

- Brazilian E-Commerce Public Dataset by Olist (Kaggle) : https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Schéma en étoile (Microsoft Learn) : https://learn.microsoft.com/fr-fr/power-bi/guidance/star-schema
- Vue d'ensemble de DAX (Microsoft Learn) : https://learn.microsoft.com/fr-fr/dax/dax-overview
- Fonctions d'intelligence temporelle DAX : https://learn.microsoft.com/fr-fr/dax/time-intelligence-functions-dax
- Power Query, documentation : https://learn.microsoft.com/fr-fr/power-query/
- Looker Studio, aide officielle : https://support.google.com/looker-studio
- RGPD, le site de la CNIL : https://www.cnil.fr/fr/rgpd-par-ou-commencer
- pandas, documentation : https://pandas.pydata.org/docs/
- Accessibilité des couleurs (WCAG / daltonisme) : https://www.w3.org/WAI/WCAG21/quickref/
- [Cours Business Intelligence](../../15-Business-Intelligence/) — métier de Data Analyst et fondamentaux BI
