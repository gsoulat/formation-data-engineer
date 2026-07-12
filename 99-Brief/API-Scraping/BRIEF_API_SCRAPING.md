# Brief : Veille concurrentielle et enrichissement catalogue — pipeline batch API + scraping vers PostgreSQL

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Débutant-Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Python (Requests, BeautifulSoup), API REST, Web Scraping, PostgreSQL, Docker, SQL, Merise, Git |
| **Prérequis** | [Cours Python](../../01-Fondamentaux/Python/) + [Cours SQL](../../01-Fondamentaux/SQL/) + [Cours Docker](../../02-Containerisation/Docker/) |

## Contexte

### L'entreprise

**Bouquineo** est une librairie en ligne française créée en 2015. Son siège est à Lille, elle compte 45 salariés et environ 12 000 références au catalogue. Elle vend sur trois canaux : son site e-commerce, une marketplace de partenaires et un réseau de 8 librairies physiques affiliées. L'équipe data vient de naître : Karim, data analyst, Claire, CTO et sponsor du projet... et vous, premier data engineer de l'entreprise.

### Le problème

Chaque lundi, Karim ouvre le site du principal concurrent et recopie à la main les prix et disponibilités de plusieurs centaines de livres dans un classeur Excel. Cela lui prend une journée entière par semaine, la donnée est obsolète dès le mardi, et personne ne peut reproduire ni vérifier sa méthode. En parallèle, le catalogue interne souffre : environ un tiers des fiches livres n'ont ni nombre de pages, ni date de première publication, ni auteur normalisé — ce qui dégrade le référencement du site et fausse les analyses. Enfin, les 8 librairies affiliées envoient chacune leurs ventes par mail, dans des CSV aux colonnes et formats différents, que personne ne consolide sérieusement.

Claire vous confie votre première mission : remplacer ces bricolages par un **pipeline de collecte batch fiable, rejouable et documenté**.

### La question centrale

Tout votre travail doit permettre d'y répondre, et vous devez pouvoir vous y référer à chaque étape :

> **« Comment nous positionnons-nous en prix et en couverture catalogue face à la concurrence, canal par canal ? »**

### Les sources de données

Le mix est imposé (extraire depuis au moins un service web API REST, un fichier de données, un scraping et une base de données) :

- **Scraping — le concurrent** : https://books.toscrape.com. Vitrine du concurrent (bac à sable légal conçu pour l'entraînement au scraping) : 1 000 livres, 50 catégories, pagination, HTML statique sans authentification. À collecter : titre, prix, disponibilité, note, catégorie, URL de la fiche.
- **API REST — Open Library** : https://openlibrary.org/developers/api. API publique réelle, sans authentification, réponses JSON. Elle permet d'enrichir le catalogue Bouquineo par ISBN (nombre de pages, date de publication, auteurs, etc.).
- **Fichiers — ventes des librairies affiliées** : 8 exports CSV fournis dans le kit de démarrage (environ 10 000 lignes cumulées). Attention : colonnes hétérogènes d'une librairie à l'autre, doublons, formats de dates incohérents, données partielles. C'est volontaire : c'est votre matière première pour le nettoyage.
- **Base de données — PostgreSQL** : la cible du pipeline. Instance conteneurisée avec Docker, dans laquelle vous chargez le jeu de données final consolidé, puis exécutez vos requêtes SQL d'extraction et d'analyse.

### Contraintes techniques

- Langage : Python (bibliothèques au choix, choix justifiés dans le README).
- Le pipeline doit être **rejouable de bout en bout**, par une ou plusieurs commandes documentées, depuis un clone propre du repo.
- Gestion des erreurs, mécanisme de **retry** et **journalisation (logs)** obligatoires sur les extractions : le site et l'API peuvent être lents ou indisponibles.
- Respect du site scrapé : temporisation entre les requêtes.
- PostgreSQL via Docker uniquement (aucune installation locale de SGBD).
- Tout le code est **versionné avec Git dès le premier jour**, sur un repo GitHub public.
- **RGPD** : les CSV de ventes contiennent des données pseudo-personnelles (email client). Vous tenez un registre des traitements basique et décrivez une procédure de tri.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Automatiser l'extraction de données** depuis un service web (API REST), une page web (scraping) et des fichiers de données — cœur du brief : aucun exemple de script fourni, vous concevez seul votre extraction complète (point de lancement, gestion des erreurs, retry, logs, sauvegarde des résultats, versionnée avec Git)
- **Développer des requêtes SQL** d'extraction (sélections, filtrages, jointures) adaptées à votre propre schéma, en explicitant vos optimisations dans la documentation
- **Développer des règles d'agrégation et de nettoyage** : gérer les doublons, dates incohérentes et entrées corrompues pour produire un jeu de données final unique et documenté
- **Créer une base de données** : modélisation selon la méthode Merise (MCD/MPD) appliquée à un contexte nouveau, avec script d'import versionné et registre RGPD basique
- Structurer un pipeline batch en couches (`raw` / `staging` / finale), inspiré de l'architecture Medallion

## Architecture cible

Claire impose un pattern de pipeline batch en trois couches, inspiré de l'architecture Medallion :

- couche `raw` : les données brutes telles que collectées, fichiers datés, jamais modifiés ;
- couche `staging` : les données nettoyées et homogénéisées, source par source ;
- couche finale : un jeu de données unique consolidé, chargé dans PostgreSQL.

```
+-----------------+  +-----------------+  +------------------+
| books.toscrape  |  |  Open Library   |  |  8 CSV ventes    |
|   (scraping)    |  |   (API REST)    |  |  librairies      |
+--------+--------+  +--------+--------+  +---------+--------+
         |                    |                     |
         +---------+----------+----------+----------+
                   |                     |
         +---------v---------------------v---------+
         |        SCRIPTS D'EXTRACTION (Python)    |
         |   retry, gestion d'erreurs, logs        |
         +---------+-------------------------------+
                   |
         +---------v-------------------------------+
         |  COUCHE RAW                             |
         |  Fichiers bruts, datés, immuables       |
         +---------+-------------------------------+
                   |
         [Nettoyage / homogénéisation (Python)]
                   |
         +---------v-------------------------------+
         |  COUCHE STAGING                         |
         |  Données nettoyées, source par source   |
         +---------+-------------------------------+
                   |
         [Agrégation / consolidation]
                   |
         +---------v-------------------------------+
         |  JEU DE DONNÉES FINAL UNIQUE            |
         +---------+-------------------------------+
                   |
         +---------v-------------------------------+
         |  PostgreSQL (Docker)                    |
         |  Modèle Merise (MCD/MPD) + import       |
         |  Requêtes SQL d'analyse                 |
         +-----------------------------------------+
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `data/ventes_librairies/*.csv` — les 8 fichiers CSV de ventes des librairies affiliées (~10 000 lignes cumulées) : colonnes hétérogènes, formats de dates incohérents, doublons, encodages variés, prix négatifs et ISBN manquants sur certaines librairies ;
- `data/catalogue_bouquineo.csv` — un extrait du catalogue Bouquineo (environ 1 000 références avec ISBN, métadonnées incomplètes sur ~1/3 des fiches) ;
- `docker-compose.yml` — pour lancer PostgreSQL 16 en local (`docker compose up -d`) ;
- **aucun code d'extraction ni de nettoyage : c'est votre travail.**

## Travail demandé

Travail individuel sur toute la semaine. L'entraide est encouragée (partage d'astuces, debug entre pairs), mais chacun rend son propre code et doit pouvoir l'expliquer ligne par ligne.

### Phase 1 — Cadrage et exploration des sources (J1)

Aucune ligne de code de production. Explorez les quatre sources :

- Naviguez sur books.toscrape.com et repérez la structure des pages : combien de pages au total, comment passe-t-on de l'une à l'autre, où se trouvent le prix et la disponibilité dans le HTML ?
- Testez l'API Open Library dans le navigateur ou avec curl : que renvoie-t-elle pour un ISBN présent dans `catalogue_bouquineo.csv` ? Et pour un ISBN inconnu ?
- Ouvrez les 8 CSV de ventes et listez toutes les différences de structure (noms de colonnes, formats de dates, doublons).
- Documentez chaque source dans `docs/sources.md` : format, volume, champs disponibles, pièges identifiés.
- Créez votre **Kanban public** (GitHub Projects, Trello...) avec des user stories tirées de la question centrale — par exemple : « En tant que data analyst, je veux comparer le prix moyen par catégorie entre Bouquineo et le concurrent ».
- Initialisez le repo GitHub public avec un premier README.

**Résultat testable en fin de J1 :** documentation des sources relue par un pair, Kanban rempli, repo initialisé.

### Phase 2 — Extraction automatisée multi-sources (J2-J3)

Développez les scripts d'extraction, source par source, en commençant par celle qui vous semble la plus simple.

- Pour le scraping : comment parcourir les 50 pages sans écrire 50 URL en dur ? Que se passe-t-il si la requête échoue à la page 37 — votre script s'arrête-t-il, réessaie-t-il, journalise-t-il l'échec ?
- Pour l'API : comment gérer un ISBN sans réponse (404) sans faire planter le lot entier, et à quel rythme appeler l'API sans l'agresser ?
- Chaque script doit avoir un **point de lancement clair**, initialiser ses dépendances et connexions externes, appliquer ses règles logiques de traitement, gérer erreurs et exceptions, écrire des **logs exploitables** et sauvegarder ses résultats bruts, datés, dans la couche `raw`.
- Committez petit et souvent : **l'historique Git fait partie de l'évaluation**.

**Résultat testable en fin de J3 :** chaque extraction se relance par une commande unique et produit ses fichiers `raw` ; les logs racontent le déroulement.

### Phase 3 — Agrégation, nettoyage et homogénéisation (J3-J4)

Transformez les données brutes en couche `staging`, puis en un jeu de données final unique.

- Quelles entrées considérez-vous comme corrompues (vente sans ISBN ? prix négatif ? doublon strict ou partiel ?) et pourquoi ?
- Comment homogénéisez-vous les formats de dates des 8 librairies ?
- Les prix du concurrent sont en livres sterling : dans quelle unité consolidez-vous, avec quel taux, documenté où ?
- Chaque règle de nettoyage est **écrite en code** (aucune correction manuelle dans un tableur) et documentée : quelle règle, appliquée à quelles données, combien de lignes affectées.

**Résultat testable :** un script d'agrégation rejouable qui produit le jeu final et un décompte des lignes supprimées ou corrigées.

### Phase 4 — Modélisation Merise, base de données et requêtes SQL (J4-J5)

- Modélisez la base cible selon la méthode **Merise** : MCD puis MPD, exportés en images. Quelles entités distinguez-vous — un livre du catalogue, une observation de prix concurrent, une vente ? Une observation de prix est-elle un attribut du livre ou une entité datée à part entière ?
- Créez la base dans PostgreSQL (**script DDL versionné**), programmez le script d'import du jeu final.
- Rédigez le **registre RGPD basique** : quelles données personnelles, quelle finalité, quelle durée de conservation, quelle procédure de tri.
- Écrivez enfin les **requêtes SQL** qui répondent à la question centrale : écart de prix moyen par catégorie face au concurrent, taux de couverture du catalogue, top des ventes par canal... Chaque requête est documentée : sélections, filtrages, jointures, optimisations et leur justification.

**Résultat testable :** base recréable depuis zéro (conteneur + DDL + import) et requêtes exécutables.

### Phase 5 — Consolidation et préparation de la démo (J5)

Finalisez le README et le schéma d'architecture, vérifiez que tout se rejoue depuis un clone propre du repo, préparez une démonstration de 15 minutes articulée autour de la question centrale.

### Socle commun (obligatoire)

- Les extractions fonctionnelles sur le mix imposé : scraping, API REST, fichiers CSV.
- Le jeu final consolidé, chargé dans PostgreSQL, interrogé par des requêtes SQL documentées.
- MCD/MPD, registre RGPD, `docs/sources.md`, README, schéma d'architecture, Kanban public.

### Pour aller plus loin (bonus, pour les plus rapides)

- Planification du pipeline : cron ou DAG Airflow local.
- Petite API FastAPI exposant le jeu final en lecture.
- Tests unitaires sur les fonctions de nettoyage.
- Rate limiting propre : backoff exponentiel sur le scraping et l'API.

Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables

À rendre au plus tard J5 à 12 h :

- Un **repo GitHub public** contenant l'intégralité du travail, avec un README structuré :
  - description du projet et rappel de la question centrale ;
  - technologies utilisées et justification rapide des choix ;
  - instructions d'installation et de lancement depuis zéro (clone, dépendances, lancement de PostgreSQL via Docker, commandes du pipeline) ;
  - architecture du pipeline (renvoi vers le schéma) ;
  - auteur.
- Le **code du pipeline** : scripts d'extraction (scraping, API, fichiers), script d'agrégation et de nettoyage, script DDL de création de la base, script d'import — avec un historique de commits régulier sur la semaine (pas un commit unique final).
- Le **schéma d'architecture** du pipeline au format image (PNG ou JPG, réalisé avec draw.io ou équivalent — pas d'ASCII art), montrant les couches `raw`, `staging` et finale.
- Les **modèles de données** : MCD et MPD au format image, accompagnés d'une courte note expliquant les choix de modélisation.
- La **documentation des sources** (`docs/sources.md`) rédigée en Phase 1 : format, volume, champs, pièges de chaque source.
- La **documentation des requêtes SQL** : pour chaque requête d'analyse, son objectif métier, ses sélections/filtrages/jointures et ses optimisations explicités.
- Le **registre RGPD basique** des traitements de données personnelles et la procédure de tri associée (fichiers markdown dans le repo).
- Le lien vers le **Kanban public** (dans le README), avec les user stories et leur historique de progression.
- Le **jeu de données final**, exporté en CSV dans le repo ou reconstructible via la base.
- Le cas échéant, les **bonus** (crontab ou DAG, API FastAPI, tests unitaires), clairement identifiés dans une section dédiée du README.

## Démonstration finale

Préparez une démonstration de **15 minutes** (+ 10 minutes de questions) : relancez votre pipeline en direct (extractions, agrégation, import), montrez les logs produits, la base PostgreSQL peuplée, puis exécutez 2 ou 3 requêtes SQL qui répondent à la question centrale.

Pour tenir les 15 minutes, les scripts d'extraction peuvent prévoir un **mode échantillon** (paramètre limitant le nombre de pages ou d'appels API), à condition de présenter aussi les preuves d'une exécution complète (logs datés, volumes collectés). Les questions porteront sur vos choix techniques : stratégie de gestion des erreurs et de retry, règles de nettoyage, choix de modélisation.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué : les scripts d'extraction et d'agrégation doivent être versionnés et accessibles depuis un dépôt Git.

## Critères de validation

### Extraction automatisée de données (conception en autonomie complète, aucun modèle fourni)

- Le script d'extraction est fonctionnel : toutes les données visées sont effectivement récupérées à l'issue de l'exécution (1 000 livres scrapés avec leurs catégories, catalogue enrichi via l'API, 8 fichiers CSV lus).
- L'extraction couvre le mix imposé : un service web (API REST), un scraping, des fichiers de données, et l'alimentation d'une base de données.
- Le script comprend un point de lancement, l'initialisation des dépendances et des connexions externes, les règles logiques de traitement, la gestion des erreurs et des exceptions (avec retry), des logs exploitables, la fin du traitement et la sauvegarde des résultats.
- Le script est versionné et accessible depuis un dépôt Git public, avec un historique de commits régulier.

### Requêtes SQL d'extraction

- Les requêtes sont fonctionnelles : les données visées sont effectivement extraites à l'exécution.
- Les requêtes mobilisent sélections, filtrages, conditions et jointures en lien direct avec la question centrale.
- La documentation met en lumière les choix de sélections, filtrages et jointures en fonction des objectifs de collecte, et explicite les optimisations appliquées.

### Règles d'agrégation et de nettoyage

- Le script d'agrégation est fonctionnel : les données sont nettoyées, homogénéisées et agrégées en un seul jeu de données final à l'issue de l'exécution.
- Les entrées corrompues sont identifiées et supprimées par le code, selon des règles explicites, avec décompte des lignes affectées.
- Les formats sont homogénéisés de façon vérifiable : dates, unités monétaires, doublons.
- La documentation du script est complète : dépendances, commandes d'exécution, enchaînements logiques, choix de nettoyage et d'homogénéisation.
- Le script d'agrégation est versionné et accessible depuis le même dépôt Git public.

### Création de la base de données

- Les modélisations respectent la méthode et le formalisme Merise ; MCD et MPD sont cohérents entre eux.
- Le choix du SGBD (PostgreSQL) est justifié dans le README au regard de la modélisation des données et des contraintes du projet.
- Le modèle physique est fonctionnel : la base se crée sans erreur depuis le script DDL versionné.
- Le script d'import est fonctionnel : il insère le jeu de données final dans la base mise en place ; sa documentation (dépendances, commandes) est versionnée dans le même dépôt Git.
- Le registre RGPD couvre l'ensemble des traitements de données personnelles de la base ; la procédure de tri détaille les traitements de conformité (automatisés ou non) et leur fréquence d'exécution.

## Ressources

- [Cours Python](../../01-Fondamentaux/Python/)
- [Cours SQL](../../01-Fondamentaux/SQL/)
- [Cours Docker](../../02-Containerisation/Docker/)
- Books to Scrape — le « concurrent » à scraper : https://books.toscrape.com
- Open Library — portail développeurs de l'API (documentation officielle) : https://openlibrary.org/developers/api
- Requests (page officielle PyPI, avec lien vers la documentation) : https://pypi.org/project/requests/
- Beautiful Soup 4 (documentation officielle) : https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Image Docker officielle PostgreSQL : https://hub.docker.com/_/postgres
- CNIL — Le registre des activités de traitement : https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement
