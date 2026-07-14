# Brief S23 — Examen blanc NordRetail : traiter un cas data de bout en bout en temps limité

## Informations

| Critère | Valeur |
|---------|--------|
| **Semaine** | S23 — Phase 3 : Se préparer à l'évaluation finale |
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire → avancé |
| **Modalité** | Individuel |
| **Technologies** | Python 3, pandas, SQL (SQLite/PostgreSQL), Power BI ou Looker Studio, Git/GitHub |
| **Prérequis** | [Extraction & analyse SQL](../../../15-Business-Intelligence/03-Analyse-Besoin-Metier/) · [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/) · [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) · [Préparation à l'évaluation finale](../../../15-Business-Intelligence/18-Preparation-Certification/) |

## Contexte

### L'entreprise

**NordRetail** est une enseigne de distribution implantée dans les Hauts-de-France : un réseau de magasins physiques (Dunkerque, Roubaix, Valenciennes, Tourcoing…) doublé d'un canal e-commerce. Depuis plusieurs semaines, vous accompagnez son équipe data naissante : vous avez audité les exports de ventes, consolidé les sources, bâti un modèle en étoile et un tableau de bord de pilotage qui prend forme réunion après réunion. La direction commence à s'appuyer sur vos analyses pour piloter l'activité.

### Le problème

L'équipe recrute. Pour se structurer, la responsable data a décidé de **standardiser la manière de traiter une demande**, du fichier brut jusqu'à la restitution. Elle vous confie donc un **cas de qualification interne** : reproduire, en temps limité et en autonomie complète, l'enchaînement complet d'un projet d'analyse — nettoyer une source dégradée, l'interroger en SQL, calculer les indicateurs clés, esquisser un tableau de bord et défendre vos choix. L'exercice sert à deux choses : vérifier que vous savez tenir la chaîne de bout en bout **sans aide**, et repérer, pendant qu'il est encore temps, les gestes que vous devez consolider.

Ce cas reprend volontairement des ingrédients déjà rencontrés, mais **rassemblés en une seule épreuve** et **chronométrés**. L'enjeu n'est pas d'inventer une méthode nouvelle : c'est de prouver que vous maîtrisez la vôtre, du début à la fin, dans des conditions proches du réel.

### La question centrale

Toute la semaine, chaque production doit contribuer à répondre à la question que la responsable data vous pose :

> **« Êtes-vous capable de traiter, seul(e) et en temps limité, une demande data NordRetail de bout en bout — de la donnée brute à une restitution défendable ? »**

### Les données

Un extrait dégradé des ventes, celui que reçoit l'équipe quand un export tourne mal, plus la base relationnelle de référence :

- [`../data/ventes_sales.csv`](../data/ventes_sales.csv) — **~12 000 lignes** de ventes « sales » (au sens *données non nettoyées*). Colonnes : `date`, `ville`, `type`, `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`. Formats de dates hétérogènes, doublons, valeurs manquantes et incohérences vous attendent.
- [`../data/setup.sql`](../data/setup.sql) — script de création et de chargement de la base NordRetail (tables `magasins`, `produits`, `clients`, `commandes`). À exécuter dans SQLite ou PostgreSQL pour la partie requêtage.
- [`../data/objectifs_2024.csv`](../data/objectifs_2024.csv) — objectifs mensuels de chiffre d'affaires par magasin, utiles pour un indicateur d'atteinte.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Enchaîner une chaîne de traitement complète en autonomie** : partir d'une source dégradée et aller jusqu'à une restitution, sans consigne pas-à-pas.
- **Nettoyer un jeu de données réel sous contrainte de temps** : traiter formats hétérogènes, doublons, valeurs manquantes et incohérences en documentant chaque décision.
- **Extraire l'information avec SQL** : écrire des requêtes correctes (jointures, agrégations, filtres) répondant à un besoin métier formulé.
- **Calculer et interpréter des indicateurs de performance** alignés sur un besoin, et non « parce qu'ils sont calculables ».
- **Esquisser une restitution défendable** : maquette de tableau de bord répondant à une question métier, et justification orale de vos choix.
- **Vous auto-évaluer avec lucidité** : situer vos points forts et vos fragilités, et transformer ce constat en plan d'action.

## Données fournies

Les fichiers sont déjà présents dans le dépôt : [`99-Brief/Data-Analyst/data/`](../data/). Aucune donnée n'est à télécharger. Vous travaillez en lecture seule sur les sources ; vos corrections restent dans votre code ou votre base de travail (on ne modifie jamais le fichier d'origine). Un besoin métier précis (la « commande » à traiter) vous est remis en début de journée d'épreuve par le formateur.

## Travail demandé

Travail **individuel sur 5 jours**. La semaine s'articule autour d'une **journée d'épreuve en conditions réelles** (temps limité, sans aide), encadrée par une phase de cadrage en amont et une phase de restitution et de remédiation en aval. L'entraide est suspendue le jour de l'épreuve ; elle reprend pour le débrief. Un **socle commun** est obligatoire ; des **pistes bonus** attendent les plus rapides.

### Phase 1 — Cadrage et gréement, SANS traitement de données (J1)

Avant toute épreuve, préparez le terrain. Relisez le déroulé d'un projet data tel que vous l'avez pratiqué depuis le début : dans quel ordre enchaînez-vous nettoyage, requêtage, indicateurs, restitution ? Où perdez-vous habituellement du temps ? Rédigez votre **procédure personnelle** — une check-list en quelques lignes de ce que vous ferez, dans quel ordre, avec quels garde-fous. Interrogez-vous : face à une source dégradée sous chronomètre, vaut-il mieux tout nettoyer d'abord ou avancer par itérations ? Comment saurez-vous qu'une requête SQL est *juste* et pas seulement *exécutable* ? Préparez votre environnement (Python, base SQL prête à charger via `setup.sql`, outil de dashboard ouvert) et initialisez votre dépôt GitHub dès aujourd'hui, pour n'avoir à penser, le jour J, qu'au fond du sujet.

### Phase 2 — Épreuve, volet préparation des données (J2, temps limité)

Le besoin métier vous est remis. Chargez [`ventes_sales.csv`](../data/ventes_sales.csv) avec pandas et **auditez-le rapidement** : volume, types, période, valeurs manquantes, doublons, incohérences (dates au format mélangé, montants ou quantités négatifs, remises hors bornes). Nettoyez ce qui doit l'être pour répondre au besoin, en **documentant chaque décision** (quelle anomalie, combien de lignes, garder / corriger / écarter, pourquoi). Le temps est compté : priorisez les corrections qui pèsent sur le résultat plutôt que la perfection. En parallèle, chargez la base avec [`setup.sql`](../data/setup.sql) pour préparer le volet requêtage.

### Phase 3 — Épreuve, volet requêtage et indicateurs (J2-J3, temps limité)

Sur la base NordRetail, écrivez **au moins deux requêtes SQL** répondant au besoin remis (par exemple : chiffre d'affaires par magasin sur une période, top catégories, panier moyen par canal). Vos requêtes doivent mobiliser au moins une jointure et une agrégation. À partir de vos données nettoyées et de vos requêtes, calculez **au moins trois indicateurs** pertinents pour la demande — pas les plus faciles, les plus utiles. Si l'un d'eux se compare aux objectifs, servez-vous de [`objectifs_2024.csv`](../data/objectifs_2024.csv). Pour chaque indicateur, une phrase : que dit-il, et pourquoi la direction devrait le regarder ?

### Phase 4 — Épreuve, volet restitution (J3, temps limité)

Esquissez une **maquette de tableau de bord** (dans Power BI / Looker Studio, ou sur papier si le temps manque) qui répond à la question métier posée. Peu importe le fini : ce qui compte, c'est que la maquette **réponde au besoin**, hiérarchise l'information et soit lisible par un décideur non technique. Rendez ce que vous avez produit à la fin du temps imparti, **même incomplet** — un travail structuré et inachevé vaut mieux qu'un travail bâclé pour « finir ».

### Phase 5 — Débrief, auto-évaluation et plan d'action (J4-J5)

L'épreuve terminée, prenez du recul. **Auto-évaluez-vous honnêtement** sur chaque étape de la chaîne (préparation des données, SQL, indicateurs, restitution, tenue du temps) : pour chacune, êtes-vous à l'aise, en progrès, ou fragile ? Justifiez chaque position par un élément concret de votre journée d'épreuve — pas une impression, un fait (« ma jointure était fausse », « je n'ai pas fini la maquette »). Identifiez ensuite vos **trois points les plus fragiles** et fixez, pour chacun, **une action concrète et datée** avant le projet final. Consolidez le tout dans votre dépôt : code de l'épreuve, requêtes, maquette (ou photo), auto-évaluation justifiée, plan d'action. Soignez le README : quelqu'un doit comprendre ce que vous avez fait et où vous en êtes.

### Socle commun (obligatoire)

Phases 1 à 5 complètes : procédure personnelle rédigée, source nettoyée avec décisions documentées, ≥ 2 requêtes SQL correctes, ≥ 3 indicateurs interprétés, maquette de tableau de bord répondant au besoin (même esquissée), auto-évaluation justifiée sur toute la chaîne, plan d'action de 3 remédiations datées, dépôt public à jour.

### Pour aller plus loin (bonus)

- Ajoutez un indicateur d'**atteinte des objectifs** (réalisé / objectif) en croisant vos ventes avec [`objectifs_2024.csv`](../data/objectifs_2024.csv).
- Rendez votre maquette **accessible** : palette lisible par un décideur daltonien, information non codée par la seule couleur (voir [Visualisations avancées](../../../15-Business-Intelligence/11-Visualisations-Avancees/)).
- Chronométrez chaque volet et analysez votre **répartition du temps** : où avez-vous dérapé, et comment vous organiserez-vous mieux au projet final ?

## Livrables attendus

- **Un dépôt GitHub public** contenant :
  - le **code de l'épreuve** (notebook ou scripts pandas de nettoyage + fichier `.sql` des requêtes) exécutable de bout en bout ;
  - la **maquette de tableau de bord** (fichier `.pbix` / lien Looker, export image, ou photo de la maquette papier) ;
  - une **auto-évaluation** justifiée couvrant toute la chaîne (`AUTO-EVAL.md`) ;
  - un **plan d'action** de 3 remédiations datées (dans l'auto-évaluation ou à part) ;
  - un **`README.md`** : description du cas, technologies, instructions de lancement, auteur.
- Une **fiche de décisions de nettoyage** (tableau : anomalie, volume, décision, justification) — dans le code ou le README.

## Modalités d'évaluation

Évaluation en deux volets :

- **Production de l'épreuve (60 %)** : qualité et rapidité du nettoyage, justesse des requêtes SQL, pertinence et interprétation des indicateurs, adéquation de la maquette au besoin métier.
- **Débrief et lucidité (40 %)** : 10 minutes de présentation de votre démarche et de vos choix à la responsable data (le formateur), défense de vos décisions et honnêteté de l'auto-évaluation + 5 minutes de questions.

**Validation partielle** : un(e) apprenant(e) dont la production de l'épreuve n'est pas entièrement finalisée, mais dont la démarche est structurée, les décisions documentées et l'auto-évaluation lucide, peut valider partiellement les capacités travaillées. La capacité à identifier soi-même ses fragilités est ici valorisée autant que la performance brute.

## Critères de performance

**Préparer et fiabiliser les données**
- La source est chargée et auditée (volume, types, manquants, doublons, incohérences).
- Les formats hétérogènes (dates notamment) et les anomalies sont corrigés ou écartés sous contrainte de temps.
- Chaque décision de nettoyage est documentée (anomalie, volume, choix, justification).

**Interroger et calculer**
- Au moins 2 requêtes SQL correctes (jointure + agrégation) répondent au besoin remis.
- Au moins 3 indicateurs pertinents pour la demande sont calculés.
- Chaque indicateur est interprété (ce qu'il dit, pourquoi il compte pour la direction).

**Restituer**
- Une maquette de tableau de bord répond explicitement à la question métier posée.
- L'information y est hiérarchisée et lisible par un décideur non technique.
- La démarche et les choix sont défendus à l'oral de façon argumentée.

**Prendre du recul**
- L'auto-évaluation couvre toute la chaîne et chaque position est justifiée par un fait de la session.
- Les 3 fragilités principales sont identifiées, chacune avec une action de remédiation datée.
- Le dépôt GitHub public est complet (code exécutable + maquette + README).

## Ressources

- Module de cours — [Préparation à l'évaluation finale](../../../15-Business-Intelligence/18-Preparation-Certification/)
- Rappels — [Nettoyage des données](../../../15-Business-Intelligence/16-Nettoyage-Donnees/) · [KPI & indicateurs](../../../15-Business-Intelligence/06-KPI-Indicateurs/) · [Tableaux de bord](../../../15-Business-Intelligence/07-Dashboards-Fondamentaux/)
- Documentation pandas : https://pandas.pydata.org/docs/
- Documentation SQLite : https://www.sqlite.org/docs.html
- Étape suivante du parcours — [S24 — soutenance blanche](semaine-24-soutenance-blanche.md)
</content>
</invoke>
