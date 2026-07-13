# Brief : Tableau de bord BI de bout en bout : piloter l'activité commerciale d'un distributeur des Hauts-de-France

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 15 jours ouvrés (~3 semaines) |
| **Niveau** | Avancé — projet de synthèse de bout en bout |
| **Modalité** | Individuel |
| **Outils** | Power BI (prioritaire) ou Looker Studio (si contrainte macOS), Python/SQL, tableur, Kanban |
| **Prérequis** | [Cours Business Intelligence](../../15-Business-Intelligence/), [SQL](../../01-Fondamentaux/SQL/), [Python](../../01-Fondamentaux/Python/) |

## Description rapide

À partir d'un simple besoin métier exprimé par une direction commerciale, vous concevez en autonomie complète une solution data de bout en bout : collecte multi-sources (Kaggle + API publique + fichier Excel), nettoyage, modélisation en étoile, puis tableau de bord BI de niveau expert, accessible (WCAG) et actionnable. Vous formalisez un dossier projet et défendez vos choix devant un jury. Projet de synthèse individuel de fin de parcours.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Concevoir un processus de collecte de données** conforme au RGPD : cartographier les sources et documenter la base légale et la conservation.
- **Automatiser la collecte multi-sources (ETL)** : script d'extraction reproductible, appel d'API paramétré, import de fichier, avec gestion des erreurs et journalisation.
- **Mettre en œuvre des stratégies de nettoyage** : détecter et traiter doublons, valeurs manquantes et aberrantes, homogénéiser dates, casse, unités et clés de jointure.
- **Extraire et combiner des données de plusieurs sources hétérogènes** en contrôlant l'exactitude des résultats.
- **Transformer un besoin métier flou en problématique** et en KPI en toute autonomie, sans modèle fourni.
- **Concevoir un tableau de bord BI de niveau expert et accessible (WCAG)**, puis restituer et défendre vos choix devant un jury mêlant profils techniques et décideurs.

Ce brief est un projet de synthèse : vous êtes pleinement autonome, sans modèle fourni, à partir du seul besoin métier. C'est là que se joue la validation de fin de parcours.

## Contexte

**L'entreprise.** « NordRetail », enseigne de distribution omnicanale implantée dans les Hauts-de-France (magasins physiques + site e-commerce), réalise environ 180 M€ de chiffre d'affaires annuel. La direction commerciale pilote aujourd'hui son activité avec une mosaïque de fichiers Excel : chaque responsable de catégorie tient son propre tableau, les périmètres ne se recoupent pas, les chiffres divergent d'une réunion à l'autre, et le reporting mensuel mobilise deux jours de travail manuel. Personne ne sait dire, sur un même écran, quels produits tirent la marge, comment les ventes varient selon les régions et les saisons, ni quel est l'effet de la météo sur la fréquentation. La direction ne veut pas d'un énième fichier : elle veut **un tableau de bord BI unique, fiable, lisible en 30 secondes, et exploitable par des décideurs non techniciens**.

**Le commanditaire vous remet uniquement un besoin métier**, formulé en une phrase lors d'un échange de cadrage : « Je veux comprendre ce qui fait notre performance commerciale, par produit, par territoire et dans le temps, pour décider où concentrer nos efforts. » Tout le reste — problématique précise, indicateurs, visualisations, modèle de données, architecture — est à votre charge. C'est tout l'enjeu du projet : vous transformez, en pleine autonomie, un besoin flou en une solution complète et défendable.

**Question centrale (à affiner et à porter tout au long du projet).** « Qu'est-ce qui explique la performance commerciale de NordRetail, et où concentrer les efforts pour la faire progresser ? » Vous déclinerez cette question en sous-questions analytiques mesurables (par exemple : quels produits/catégories concentrent le chiffre d'affaires et la marge ? comment les ventes évoluent-elles dans le temps et selon la saisonnalité ? existe-t-il des écarts territoriaux ? la météo influence-t-elle les ventes ?). Chaque KPI et chaque visualisation devront répondre à l'une de ces sous-questions.

**Sources de données réelles (au moins ces trois, à combiner).**

- Source 1 — Transactions de ventes (Kaggle, CSV, plusieurs milliers à dizaines de milliers de lignes). Jeu de données e-commerce avec date de commande, catégorie, produit, quantité, prix unitaire, montant, région et moyen de paiement. URL : https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data — alternative possible : https://www.kaggle.com/datasets/prasad22/retail-transactions-dataset
- Source 2 — API publique gratuite, sans clé. Au choix selon votre angle : API Open-Meteo (météo historique, pour croiser ventes et conditions climatiques, JSON via requête HTTP GET) — https://open-meteo.com/en/docs/historical-weather-api ; ou API Découpage administratif (geo.api.gouv.fr) pour enrichir vos territoires (régions, départements, population, JSON) — https://geo.api.gouv.fr/decoupage-administratif
- Source 3 — Fichier Excel/CSV de référentiel territorial à constituer ou télécharger : table des communes/régions de France (population, codes INSEE, coordonnées) servant de dimension géographique. URL : https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather — portail régional complémentaire : https://www.data.gouv.fr/organizations/region-hauts-de-france/datasets

**Architecture attendue (flux complet, du brut à la décision).** Un flux clair en couches : collecte multi-sources (scripts + appel API + import fichier) vers une zone brute ; nettoyage et normalisation (dates, casse, unités, doublons, valeurs manquantes, aberrantes) vers une zone propre ; **modélisation en étoile** (une table de faits « ventes » + dimensions Temps, Produit, Géographie, et le cas échéant Météo) ; enfin restitution dans un **tableau de bord BI de niveau expert** (Power BI prioritaire, ou Looker Studio si contrainte macOS), avec interactivité (filtres, segments, drill-down, info-bulles) et **accessibilité WCAG** (contrastes, palettes adaptées au daltonisme, titres explicites, alternatives textuelles). Le schéma d'architecture et le schéma du modèle en étoile seront fournis en image dans le dépôt.

**RGPD.** Les données de transactions ne doivent comporter aucune donnée personnelle directement identifiante. Vous documenterez la nature des données mobilisées, leur base légale présumée, l'absence (ou la pseudonymisation) de données personnelles, et la durée de conservation. Toute donnée client sera agrégée ou anonymisée avant analyse.

## Modalités pédagogiques

Projet **individuel** mené sur **15 jours ouvrés** (~3 semaines), en autonomie encadrée. Vous tenez un **Kanban public** (Trello, GitHub Projects ou équivalent) dès le premier jour et vous y consignez vos décisions. Chaque phase produit un résultat visible et versionné sur le dépôt GitHub.

**Phase 1 — Cadrage et conception (J1-J3, sans code de production).** Vous partez du seul besoin métier. Comment allez-vous transformer cette phrase en problématique analytique ? Rédigez un mini cahier des charges : objectifs, périmètre, parties prenantes, livrables, contraintes. Formulez la question centrale et ses sous-questions mesurables. Quels KPI répondent à la décision visée — et lesquels sont des indicateurs d'activité plutôt que de résultat ? Documentez vos sources (format, volume, accès, fraîcheur), explorez-les manuellement pour valider leur pertinence, et tranchez l'architecture : quelles couches, quel grain pour la table de faits, quelles dimensions ? Rédigez la note RGPD. Posez votre Kanban et vos user stories. Aucun tableau de bord n'est construit ici : on conçoit.

**Phase 2 — Collecte et nettoyage (J4-J7).** Vous outillez la collecte des trois sources. Comment automatiser l'extraction reproductible (script Python/SQL, requête API paramétrée, import du fichier) plutôt que de copier-coller à la main ? Comment gérer les erreurs, les logs et la reprise ? Puis vous nettoyez : quelles incohérences, doublons, valeurs manquantes et aberrantes détectez-vous, et quelle stratégie (imputation, suppression, substitution) justifiez-vous au cas par cas ? Comment homogénéiser dates, casse, unités et clés de jointure entre sources hétérogènes ? Documentez chaque règle de nettoyage dans le dépôt.

**Phase 3 — Modélisation et analyse (J8-J10).** Vous construisez le **modèle en étoile** : une table de faits, des dimensions reliées par des clés. Comment éviter les relations ambiguës et garantir des agrégations justes ? Vous menez une analyse exploratoire suffisante pour fonder vos KPI : tendances temporelles, comparaisons par catégorie et par territoire, éventuelle corrélation ventes/météo — en distinguant corrélation et causalité. Quels résultats serviront de socle aux visualisations ? Validez l'exactitude (contrôle des totaux, des doublons, cohérence des montants).

**Phase 4 — Tableau de bord BI (J11-J13).** Vous construisez le tableau de bord de niveau expert. Comment structurer l'arborescence (vue direction synthétique → pages de détail) pour qu'on lise l'essentiel en 30 secondes ? À chaque intention (comparer, suivre une évolution, mesurer une répartition, montrer une relation, afficher un KPI vs cible), quel graphique choisissez-vous — et lequel évitez-vous (camembert surchargé, axe tronqué, 3D inutile) ? Comment garantir l'accessibilité WCAG (contraste suffisant, palette compatible daltonisme, titres parlants, info-bulles explicatives) ? Ajoutez l'interactivité : filtres, segments, drill-down. Construisez les mesures calculées (DAX ou équivalent) proprement nommées.

**Phase 5 — Dossier projet et soutenance (J14-J15).** Vous rédigez le **dossier projet** (démarche, choix justifiés, architecture, modèle, KPI, accessibilité, RGPD, limites et recommandations métier) et préparez le **support de soutenance**. Comment adapter votre discours à un jury mêlant profils techniques et décideurs ? Comment raconter une histoire data qui mène à des recommandations concrètes plutôt qu'à une simple liste de graphiques ? Répétez la démonstration en conditions réelles.

## Modalités d'évaluation

L'évaluation combine trois volets, alignés sur les attendus du projet de fin de parcours.

- Dossier projet écrit — 35 %. Évalue la démarche, la justification des choix (problématique, KPI, visualisations, modèle, architecture), la conformité RGPD et la qualité de la documentation. C'est la trace écrite de votre raisonnement mené en pleine autonomie.
- Tableau de bord BI livré — 35 %. Évalue la pertinence des indicateurs, le choix des visualisations, l'accessibilité WCAG, l'interactivité, la justesse des chiffres et la lisibilité « 30 secondes ».
- Soutenance orale devant jury — 30 %. Durée : 20 minutes de présentation et démonstration live du tableau de bord, suivies de 15 minutes de questions du jury. Évalue la clarté du storytelling, l'adaptation au public, la défense des choix et la formulation de recommandations métier.

Chaque acquis est validé si ses critères de performance (section « Critères de performance ») sont majoritairement remplis. Les capacités de cadrage, de définition des KPI, de choix des visualisations, de construction du tableau de bord et de restitution sont déterminantes pour la réussite du projet.

**Clause de validation partielle.** Un apprenant dont le tableau de bord présente des imperfections techniques, mais dont la démarche est rigoureuse, documentée et justifiée (problématique solide, KPI pertinents, modèle correct, choix de visualisations argumentés), peut valider partiellement les acquis concernés. À l'inverse, un tableau de bord visuellement abouti mais sans démarche ni justification ne suffit pas à valider une autonomie complète.

## Livrables attendus

- **Dépôt GitHub public** contenant l'intégralité du projet, avec un **README** structuré : description du projet, sources de données et URLs, technologies utilisées, instructions d'installation et de lancement, architecture, auteur.
- **Scripts de collecte** : extraction des trois sources (script Python/SQL, appel API paramétré, import du fichier Excel/CSV), reproductibles et commentés.
- **Scripts / notebook d'ETL et de nettoyage** : règles de transformation et de nettoyage documentées, avec journalisation.
- **Modèle de données en étoile** : schéma (image dans le dépôt) et fichiers de modélisation (table de faits + dimensions).
- **Schéma d'architecture** du flux complet (collecte → nettoyage → modèle → restitution), au format image.
- **Tableau de bord BI final** : fichier source (.pbix Power BI ou lien Looker Studio) + captures d'écran intégrées au dépôt.
- **DOSSIER PROJET** (PDF) : besoin métier et problématique, sources, démarche de collecte/nettoyage, modèle, KPI définis (formule, granularité, cible), choix de visualisations et accessibilité WCAG, note RGPD, analyse des tendances, limites et **recommandations métier**.
- **Support de soutenance** (slides) prêt pour la présentation devant jury.
- **Tableau Kanban** public (lien) retraçant l'organisation et l'historique des décisions.

Note RGPD : aucune donnée personnelle identifiante ne doit figurer dans le dépôt public.

## Critères de performance

**Concevoir un processus de collecte (RGPD)**
- Les sources sont cartographiées (format, volume, accès, fraîcheur) : OUI / NON
- La conformité RGPD est documentée (absence/pseudonymisation des données personnelles, base légale, conservation) : OUI / NON
- Les outils de centralisation choisis sont cohérents avec le besoin : OUI / NON

**Créer un système automatisé de collecte (ETL)**
- L'extraction est scriptée et reproductible (pas de copier-coller manuel) : OUI / NON
- L'appel API est paramétré et fonctionnel : OUI / NON
- La gestion des erreurs et la journalisation sont présentes : OUI / NON

**Mettre en œuvre des stratégies de nettoyage**
- Doublons, valeurs manquantes et aberrantes sont identifiés et traités : OUI / NON
- La stratégie (imputation/suppression/substitution) est justifiée par le contexte : OUI / NON
- Les règles de nettoyage sont documentées : OUI / NON

**Extraire des données multi-sources**
- Les trois sources sont effectivement extraites et combinées : OUI / NON
- Les clés de jointure sont cohérentes et les formats homogénéisés : OUI / NON
- L'exactitude des données extraites est contrôlée (totaux, doublons) : OUI / NON

**Élaborer la problématique métier**
- Le besoin métier est transformé en problématique et sous-questions mesurables : OUI / NON
- Un cahier des charges (objectifs, périmètre, livrables) est formalisé : OUI / NON
- La problématique pilote effectivement les choix du projet : OUI / NON

**Identifier les KPI**
- Les KPI sont définis (formule, granularité, fréquence, cible) : OUI / NON
- Indicateurs de résultat et d'activité sont distingués : OUI / NON
- L'arborescence du tableau de bord (direction → détail) est structurée : OUI / NON

**Choisir des visualisations pertinentes (WCAG)**
- Chaque graphique est adapté à l'intention et à la nature de la donnée : OUI / NON
- L'accessibilité WCAG est respectée (contraste, daltonisme, titres, alternatives) : OUI / NON
- Les pièges visuels (camembert surchargé, axe tronqué, 3D) sont évités : OUI / NON

**Créer un tableau de bord BI**
- Le modèle en étoile est correct et les agrégations sont justes : OUI / NON
- L'interactivité (filtres, segments, drill-down, info-bulles) fonctionne : OUI / NON
- Le tableau de bord est lisible « en 30 secondes » et publiable : OUI / NON

**Présenter les résultats**
- Le discours est adapté au public (technique et décideurs) : OUI / NON
- Le storytelling mène à des recommandations métier concrètes : OUI / NON
- L'accessibilité de la restitution est prise en compte : OUI / NON

## Ressources

- [Cours Business Intelligence](../../15-Business-Intelligence/) — métier de Data Analyst et fondamentaux BI
- [SQL](../../01-Fondamentaux/SQL/) — extraction et transformation des données
- [Python](../../01-Fondamentaux/Python/) — scripts de collecte et d'ETL
- Dataset ventes (Kaggle) : https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data
- Dataset ventes alternatif (Kaggle) : https://www.kaggle.com/datasets/prasad22/retail-transactions-dataset
- API météo historique Open-Meteo (sans clé) : https://open-meteo.com/en/docs/historical-weather-api
- API Découpage administratif (geo.api.gouv.fr) : https://geo.api.gouv.fr/decoupage-administratif
- Communes/villes de France (data.gouv.fr, CSV/Excel/Parquet) : https://www.data.gouv.fr/datasets/communes-et-villes-de-france-en-csv-excel-json-parquet-et-feather
- Open data Région Hauts-de-France : https://www.data.gouv.fr/organizations/region-hauts-de-france/datasets
- Power BI — modélisation et DAX : https://learn.microsoft.com/fr-fr/power-bi/
- Looker Studio (alternative cross-OS) : https://lookerstudio.google.com/
- Règles d'accessibilité WCAG 2.1 : https://www.w3.org/Translations/WCAG21-fr/
- Modélisation en étoile (star schema) : https://learn.microsoft.com/fr-fr/power-bi/guidance/star-schema
- RGPD — CNIL, base légale et données : https://www.cnil.fr/fr/reglement-europeen-protection-donnees
