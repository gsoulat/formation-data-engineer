# Brief : Concevoir « Fluxo », un petit framework d'ingestion orienté objet pour les données de mobilité de Vélizen

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Python 3.11+, programmation orientée objet (classes abstraites, héritage, polymorphisme), `requests`, `psycopg` (PostgreSQL), `pytest`, logging & fichiers de configuration (`.env` / YAML), Git |
| **Prérequis** | [POO – concepts](../../../01-Fondamentaux/Python/02-POO-Concepts/) + [POO en Python](../../../01-Fondamentaux/Python/03-POO-Python/) + [Bibliothèque standard](../../../01-Fondamentaux/Python/04-Bibliotheque-Standard/) + [Qualité & tests](../../../01-Fondamentaux/Python/05-Qualite-Tests/) + [Cours SQL](../../../01-Fondamentaux/SQL/) |

## Contexte

### L'entreprise

**Vélizen** est une scale-up française créée en 2018 à Nantes. Elle exploite un service d'abonnement à des vélos et trottinettes en libre-service pour le compte de collectivités de taille moyenne (agglomérations de 100 000 à 400 000 habitants). Ses 60 salariés opèrent une flotte de plusieurs milliers d'engins répartis sur une dizaine de villes. L'équipe data est jeune : deux data engineers (dont vous), une data analyst et un lead tech qui parraine le sujet.

### Le problème

Pour piloter l'exploitation (rééquilibrage des stations, prévision de la demande, facturation aux collectivités), Vélizen doit **agréger des données qui viennent de partout** : des exports CSV de bornes vieillissantes, des API REST de systèmes de vélos en libre-service, et une base PostgreSQL interne qui recense les stations et les abonnés.

Aujourd'hui, chaque source est traitée par un **script isolé**, écrit dans son coin, avec sa propre façon de se connecter, de lire, de gérer les erreurs réseau et d'écrire des logs. Résultat : quand une API change de format ou qu'un CSV arrive corrompu, personne ne sait où regarder, le code se duplique, et l'ajout d'une onzième ville prend une semaine. Le lead tech l'a formulé sans détour en réunion : *« On a dix tuyaux bricolés là où il nous faut une plomberie. »*

La décision est prise : avant d'ajouter la moindre nouvelle source, l'équipe se dote d'un **petit framework d'ingestion maison, orienté objet**, capable d'accueillir une nouvelle source par simple ajout d'une classe, avec une gestion des erreurs, une configuration et des tests **communs à toutes les sources**.

### La question centrale

Le lead tech résume l'enjeu en une phrase, qui devient la question centrale du projet. Chaque choix de conception de la semaine devra pouvoir être justifié par sa contribution à cette question :

> **« Comment ajouter une nouvelle source de données sans réécrire, ni casser, tout ce qui existe déjà ? »**

### Les sources de données

Vous travaillez sur trois familles de sources **réelles et publiques**, représentatives de l'hétérogénéité de Vélizen. Chacune est ingérée par un connecteur dédié de votre framework.

- **Fichier CSV — vélos en libre-service (open data)** : le jeu de données **« Vélib' Métropole – disponibilité temps réel »** exposé en CSV/JSON par la plateforme open data parisienne (https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/). Vous en récupérez un **export CSV** que vous placez dans le repo comme source « fichier » (états de stations : identifiant, nom, vélos disponibles, bornes libres, horodatage). C'est votre source « bornes vieillissantes ».
- **API REST — flux GBFS temps réel** : le standard **GBFS (General Bikeshare Feed Specification)**, utilisé mondialement par les opérateurs de vélos partagés. Le feed Vélib' est public et sans clé : `station_status` (https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json) et `station_information` (https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json). C'est votre source « API d'un système de VLS ».
- **Base de données — PostgreSQL interne** : une petite base que **vous initialisez vous-même** (script DDL + données d'amorçage fournis dans le kit de démarrage) recensant les stations et un référentiel de villes. C'est votre source « base interne ». Un PostgreSQL local (Docker ou installation native) suffit.

Ce brief est un épisode de la vie data de Vélizen, mais il est réalisable de façon **autonome** : les URLs ci-dessus sont publiques et le kit de démarrage contient le DDL et les données d'amorçage PostgreSQL. Aucun livrable d'un brief précédent n'est nécessaire.

### Contraintes techniques

- **Python 3.11+** uniquement pour le framework ; pas de framework d'ingestion tiers (le but est de concevoir le vôtre).
- Les bibliothèques `requests` (HTTP), `psycopg` (PostgreSQL) et `pytest` (tests) sont autorisées et attendues.
- Le framework doit exposer une **hiérarchie de classes abstraites** (`Source` / `Connector`) et des implémentations concrètes par type de source (CSV, API, DB).
- **Aucun secret en clair** dans le code : identifiants de base et éventuels paramètres sensibles passent par un fichier de configuration hors du dépôt (`.env` ignoré par Git, avec un `.env.example` versionné).
- Tout le code est **versionné sur GitHub dès le premier jour**, avec un environnement reproductible (`requirements.txt` ou `pyproject.toml`).

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Concevoir l'architecture objet d'un composant logiciel** : traduire un besoin d'ingestion hétérogène en une hiérarchie de classes, définir un **contrat commun** via des classes abstraites, et justifier vos choix d'héritage et de polymorphisme sur un diagramme.
- **Automatiser l'extraction de données depuis plusieurs types de sources** (fichier, service web / API REST, base de données) en programmant, pour chacune, une classe connecteur qui respecte le même contrat.
- **Rendre l'ingestion robuste et exploitable** : gérer les erreurs et exceptions par une hiérarchie d'exceptions maison, appliquer des tentatives (retry) sur les erreurs transitoires, produire des logs structurés et externaliser la configuration.
- **Homogénéiser des données issues de sources différentes** : normaliser les formats (dates, types, unités), écarter les enregistrements corrompus et produire un jeu de données final unifié quelle que soit la source d'origine.
- **Garantir la qualité par les tests** : écrire des tests unitaires (dont des tests de la logique de connexion avec doublures / mocks) et mesurer la couverture, afin qu'un ajout de source ne casse pas l'existant.

## Architecture cible

Le patron attendu est un framework d'ingestion en couches, articulé autour d'un **contrat commun** défini par des classes abstraites. Une classe abstraite `Connector` déclare le cycle de vie d'une connexion (`connect`, `read`, `close`) ; une classe abstraite `Source` déclare l'opération d'extraction normalisée (`extract` → enregistrements homogènes). Les sous-classes concrètes (`CsvSource`/`CsvConnector`, `ApiSource`/`ApiConnector`, `DbSource`/`DbConnector`) implémentent le contrat sans que le reste du code ait à connaître leur type — c'est tout l'intérêt du **polymorphisme**.

Un **orchestrateur** (une classe `Pipeline` ou une simple fonction de haut niveau) itère sur une liste de sources décrites dans la **configuration**, appelle `extract()` sur chacune, applique les règles de **normalisation** et d'**écartement des enregistrements corrompus**, puis produit le jeu unifié. Autour, une couche transverse : **exceptions maison**, **logging** et **configuration**.

```
                 +-------------------------------------------------+
                 |                 CONFIGURATION                   |
                 |     (.env + fichier YAML : liste des sources)   |
                 +-----------------------+-------------------------+
                                         |
                 +-----------------------v-------------------------+
                 |                   PIPELINE                      |
                 |   itère sur les sources déclarées en config     |
                 +-----------------------+-------------------------+
                                         |
        +--------------------------------+--------------------------------+
        |                                |                                |
   +----v-----+                    +-----v-----+                    +-----v-----+
   | CsvSource|                    | ApiSource |                    | DbSource  |
   | Csv-     |                    | Api-      |                    | Db-       |
   | Connector|                    | Connector |                    | Connector |
   +----+-----+                    +-----+-----+                    +-----+-----+
        |         héritent du contrat commun (classes abstraites)        |
        +--------------------------------+--------------------------------+
                                         |
                 +-----------------------v-------------------------+
                 |     NORMALISATION + ÉCARTEMENT DES CORROMPUS    |
                 |   (dates, types, unités -> enregistrements      |
                 |    homogènes ; lignes invalides rejetées)       |
                 +-----------------------+-------------------------+
                                         |
                 +-----------------------v-------------------------+
                 |              JEU DE DONNÉES UNIFIÉ              |
                 |          (fichier de sortie + logs)             |
                 +-------------------------------------------------+

   Couche transverse :  Exceptions maison  |  Logging  |  Configuration
```

> Vous produirez votre **propre diagramme de classes UML au format image** (draw.io, PlantUML exporté, ou équivalent — pas d'ASCII art) à joindre au rendu : classes abstraites, sous-classes concrètes, relations d'héritage, principales méthodes et la hiérarchie d'exceptions.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `ddl/01_referentiel.sql` — le **schéma et les données d'amorçage** PostgreSQL (référentiel de stations et de villes) : DDL + `INSERT`. C'est vous qui créez la base localement à partir de ce script.
- `sample/velib-sample.csv` — un **petit extrait CSV** pour amorcer le développement hors ligne, avec quelques pièges volontaires (une ligne à horodatage manquant, un champ numérique vide, un doublon).

> **Important** : le kit ne fournit **aucun** squelette du framework, ni classe de base, ni exemple de connecteur. La conception de la hiérarchie de classes est le cœur de l'exercice et vous revient entièrement.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient son propre framework. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et conception objet (J1)

Aucune ligne de code de framework. Explorez d'abord **chaque source** : ouvrez l'export CSV, appelez le feed GBFS dans un navigateur ou avec `curl`, parcourez le DDL fourni. Documentez, pour chacune : sa **structure** (champs, types), sa façon de se connecter (chemin de fichier ? URL ? chaîne de connexion ?), ses **modes de défaillance** (fichier absent, erreur HTTP, base injoignable) et les **pièges de données** repérés (dates au format ISO d'un côté et horodatage Unix de l'autre ? champs manquants ? doublons ?).

C'est ensuite le moment de **concevoir la hiérarchie de classes**, sur papier puis sous forme de diagramme UML. Les questions structurantes à trancher :

- Quel est le **contrat commun** que toute source doit respecter ? Que placez-vous dans la classe abstraite `Connector` (cycle de connexion) et dans la classe abstraite `Source` (extraction normalisée) ? Pourquoi deux abstractions plutôt qu'une seule ?
- Qu'est-ce qui est **factorisé dans la classe mère** (logging, retry, validation) et qu'est-ce qui est **spécifique à chaque sous-classe** (la façon de lire un CSV vs. d'appeler une API vs. d'interroger PostgreSQL) ?
- Comment votre code de haut niveau peut-il traiter une `CsvSource` et une `ApiSource` **exactement de la même manière** ? (C'est la définition même du polymorphisme : nommez le mécanisme Python que vous exploitez.)
- À quoi ressemble votre **hiérarchie d'exceptions** maison : une exception racine `IngestionError`, puis des sous-types (`ConnectionError`, `ParsingError`, `ValidationError`…) ? Que gagne-t-on à typer les erreurs ainsi ?

Formalisez votre plan dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** diagramme de classes UML, documentation des trois sources et Kanban présentés en 5 minutes au formateur.

### Phase 2 — Le socle abstrait et la configuration (J2)

Posez les fondations. Écrivez les **classes abstraites** `Connector` et `Source` (méthodes abstraites, docstrings du contrat), la **hiérarchie d'exceptions** maison, et la brique de **configuration** : la liste des sources à ingérer et leurs paramètres (chemin CSV, URL de l'API, connexion à la base) doit se lire depuis un fichier (YAML) et un `.env`, **jamais en dur** dans le code.

- Comment garantissez-vous qu'une sous-classe qui oublie d'implémenter une méthode du contrat **échoue à l'instanciation**, et non plus tard en production ?
- Où placez-vous le **logging** pour que chaque source hérite du même comportement de journalisation sans le réécrire ?
- Votre `.env` est-il bien **exclu du dépôt** (`.gitignore`) et remplacé par un `.env.example` versionné ?

**Résultat testable en fin de J2 :** les classes abstraites refusent d'être instanciées directement, la configuration se charge depuis les fichiers, et le logging écrit un premier message.

### Phase 3 — Les trois connecteurs concrets (J2-J3)

Implémentez les sous-classes concrètes, une par famille de source, **toutes conformes au même contrat** :

- `CsvConnector`/`CsvSource` : lit l'export CSV Vélib' (fichier local).
- `ApiConnector`/`ApiSource` : interroge le feed **GBFS** (`station_status` / `station_information`) en HTTP.
- `DbConnector`/`DbSource` : interroge votre **PostgreSQL** (référentiel stations/villes).

C'est ici que se joue la robustesse :

- Que se passe-t-il si le **fichier CSV est absent**, si l'**API renvoie une erreur HTTP 500 ou un timeout**, si la **base est injoignable** ? Chaque cas doit lever une exception **typée** de votre hiérarchie, pas planter avec une trace brute.
- Sur les erreurs **transitoires** (réseau, HTTP 5xx), appliquez une stratégie de **retry** (nombre de tentatives, attente entre deux essais) — factorisée, idéalement dans la classe mère.
- Vos **logs** permettent-ils de savoir quelle source a été lue, combien d'enregistrements, combien de rejets, et pourquoi une tentative a échoué ?

**Résultat testable :** les trois connecteurs extraient chacun leurs données ; couper le réseau ou renommer le CSV déclenche une exception maison lisible et un log explicite, sans faire tomber tout le programme.

### Phase 4 — Normalisation, jeu unifié et tests (J3-J4)

Le cœur métier. Faites converger les trois sources vers un **jeu de données unifié** :

- **Normalisation** : les horodatages (ISO côté CSV, Unix côté GBFS) sont convertis en un **format unique**, les types sont cohérents (identifiants, entiers de disponibilité), les noms de champs sont harmonisés — une station doit avoir le même schéma quelle que soit sa source.
- **Écartement des enregistrements corrompus** : les lignes invalides (horodatage manquant, champ numérique non convertible, doublons) sont **rejetées selon des règles explicites**, comptées et journalisées — pas silencieusement.
- Produisez le **jeu unifié en sortie** (CSV ou JSON) et un court **rapport d'ingestion** (par source : lus / retenus / rejetés).

En parallèle, écrivez les **tests** avec `pytest` :

- des tests **unitaires** sur la normalisation et l'écartement des corrompus (cas nominal et cas limites) ;
- un test de la **logique de connexion sans dépendre du réseau ni de la base**, en substituant la source par une **doublure (mock/fake)** — c'est ce qui garantit qu'ajouter une source ne casse pas l'existant ;
- une mesure de la **couverture** du code testé.

**Résultat testable :** un seul point d'entrée ingère les trois sources et produit le jeu unifié + le rapport ; `pytest` passe au vert et affiche un taux de couverture.

### Phase 5 — Consolidation, documentation et démo (J5)

Finalisez le README (description, question métier, technologies, installation et lancement, architecture, comment ajouter une nouvelle source, auteur), vérifiez que l'installation est **reproductible de zéro** (environnement, dépendances, `.env.example`, création de la base), mettez à jour le diagramme UML et le Kanban, puis répétez votre démonstration : scénario, ordre des commandes, plan B si l'API publique est indisponible le jour J (repli sur le CSV d'échantillon).

### Socle commun (obligatoire)

- Une **hiérarchie de classes abstraites** `Source` / `Connector` définissant un contrat commun.
- **Trois connecteurs concrets** conformes au contrat : CSV, API (GBFS), PostgreSQL.
- Une **hiérarchie d'exceptions maison** et une gestion des erreurs typée, avec **retry** sur les erreurs transitoires.
- **Configuration externalisée** (YAML + `.env`, aucun secret en dur) et **logging** commun à toutes les sources.
- **Normalisation** vers un jeu unifié et **écartement documenté** des enregistrements corrompus, avec rapport d'ingestion.
- Une **suite de tests `pytest`** (dont un test avec doublure/mock) et une **mesure de couverture**.
- Repo public documenté avec diagramme UML et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Rendre le framework **extensible par plugin** : ajouter une source via un **registre** (décorateur d'enregistrement ou fabrique) sans modifier l'orchestrateur — l'illustration parfaite de la question centrale.
- Ajouter un **quatrième connecteur** sur une nouvelle source publique (par exemple un autre feed GBFS de https://github.com/MobilityData/gbfs, ou une API open data data.gouv.fr) **sans toucher au socle**, pour prouver l'extensibilité.
- Empaqueter le framework en **package installable** (`pyproject.toml`, `pip install -e .`) avec un point d'entrée en ligne de commande.
- Ajouter une **validation de schéma** des enregistrements (par exemple avec `pydantic` ou des `dataclasses` typées) et faire échouer proprement les sources non conformes.
- Mettre en place l'**intégration continue** (GitHub Actions) qui lance `pytest` et l'analyse statique à chaque push.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables attendus

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un README structuré : description du projet et de la question métier, technologies utilisées, instructions d'installation et de lancement pas à pas (environnement Python, dépendances, `.env.example`, création de la base), architecture (diagramme intégré au README), **procédure d'ajout d'une nouvelle source**, auteur.
- Le **code du framework** : classes abstraites `Source`/`Connector`, les trois connecteurs concrets, la hiérarchie d'exceptions, la brique de configuration et le logging, l'orchestrateur produisant le jeu unifié.
- Les **fichiers de configuration** : `config.yaml` (ou équivalent) décrivant les sources, `.env.example` versionné, `.gitignore` excluant `.env`.
- Le **diagramme de classes UML au format image** (PNG ou export draw.io/PlantUML) : classes abstraites, sous-classes, héritage, hiérarchie d'exceptions. Pas de schéma ASCII.
- Le **jeu de données unifié** produit et le **rapport d'ingestion** (lus / retenus / rejetés par source).
- La **suite de tests `pytest`** (dont au moins un test avec doublure/mock) et le **rapport de couverture** (capture ou sortie textuelle).
- La **documentation des sources** : pour chacune, structure des champs, mode de connexion, modes de défaillance et pièges de données traités.
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Modalités d'évaluation

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous lancez l'ingestion des trois sources depuis un point d'entrée unique, montrez le jeu unifié et le rapport (lus / retenus / rejetés), déclenchez au moins un **scénario de robustesse** (fichier absent, API en erreur ou base coupée → exception maison + log lisible, avec retry visible), puis lancez `pytest` et présentez la couverture. Les questions portent sur les choix de conception : rôle des classes abstraites, ce qui est factorisé dans la mère, mécanisme du polymorphisme, hiérarchie d'exceptions, stratégie de retry, isolation des tests par mock.
- **Revue de code et de conception — 30 %** : examen du repo GitHub public (structure du package, lisibilité, respect du contrat par les sous-classes, gestion des erreurs, logs, qualité du README et de la procédure d'ajout de source), du diagramme UML (cohérence héritage / abstractions) et de la documentation des sources.

> **Validation partielle** : un framework qui ne s'exécute pas entièrement en démonstration mais dont le code est structuré, versionné et documenté (contrat abstrait clair, connecteurs présents, tests écrits) peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de documentation et de tests ne valide pas les critères correspondants.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de performance

### Conception de l'architecture objet

- Une hiérarchie de classes abstraites `Source` / `Connector` définit un contrat commun, matérialisé par des méthodes abstraites qui empêchent l'instanciation d'une classe incomplète.
- Le diagramme UML est cohérent avec le code : relations d'héritage, sous-classes concrètes et hiérarchie d'exceptions y figurent lisiblement.
- Les choix de conception (ce qui est factorisé dans la classe mère, ce qui est spécifique aux sous-classes) sont justifiés au regard de la question centrale.
- Le code de haut niveau traite les différentes sources de façon polymorphe, sans tester leur type concret (pas de chaîne de `if isinstance(...)`).

### Automatisation de l'extraction multi-sources

- Les trois connecteurs (CSV, API GBFS, PostgreSQL) sont fonctionnels : chacun extrait effectivement ses données à l'exécution.
- L'extraction couvre bien les trois familles imposées : un fichier de données, un service web / API REST, une base de données.
- Chaque connecteur respecte le contrat commun (mêmes méthodes, même signature d'extraction) sans réécrire la logique transverse.
- Le point d'entrée lit la liste des sources depuis la configuration, sans aucun paramètre sensible codé en dur.

### Robustesse, erreurs et configuration

- Les défaillances (fichier absent, erreur HTTP / timeout, base injoignable) lèvent une exception **typée** de la hiérarchie maison, pas une trace non gérée.
- Une stratégie de retry est appliquée sur les erreurs transitoires (nombre de tentatives et attente paramétrables).
- Les logs permettent de suivre l'ingestion (source lue, volumes, rejets, cause d'échec) et de diagnostiquer un incident.
- La configuration est externalisée (`.env` exclu du dépôt + `.env.example` versionné) ; aucun secret n'apparaît dans le code.

### Homogénéisation et jeu unifié

- Les enregistrements des trois sources sont normalisés vers un schéma unique (horodatages, types, noms de champs cohérents).
- Les enregistrements corrompus (horodatage manquant, champ non convertible, doublons) sont écartés selon des règles explicites, comptés et journalisés.
- Un jeu de données unifié et un rapport d'ingestion (lus / retenus / rejetés par source) sont produits en sortie.
- Les règles de normalisation et d'écartement sont documentées.

### Qualité par les tests

- Une suite `pytest` couvre la normalisation et l'écartement des enregistrements corrompus (cas nominal et cas limites).
- Au moins un test isole la logique de connexion à l'aide d'une doublure (mock / fake), sans dépendre du réseau ni de la base.
- La couverture de test est mesurée et son résultat est présenté (sortie ou capture).
- La suite de tests passe au vert sur une machine propre en suivant le README.

## Ressources

- [POO – concepts (paradigme objet, héritage, interfaces)](../../../01-Fondamentaux/Python/02-POO-Concepts/)
- [POO en Python (classes, héritage, méthodes spéciales, exceptions)](../../../01-Fondamentaux/Python/03-POO-Python/)
- [Bibliothèque standard (fichiers I/O, context managers, type hints, dataclasses, environnement)](../../../01-Fondamentaux/Python/04-Bibliotheque-Standard/)
- [Qualité & tests (pytest, couverture, logging structuré, analyse statique)](../../../01-Fondamentaux/Python/05-Qualite-Tests/)
- [Cours SQL](../../../01-Fondamentaux/SQL/)
- Python — module `abc`, classes de base abstraites : https://docs.python.org/3/library/abc.html
- Python — hiérarchie des exceptions et exceptions personnalisées : https://docs.python.org/3/tutorial/errors.html
- `requests` — envoi de requêtes HTTP et gestion des erreurs : https://requests.readthedocs.io/
- `psycopg` (PostgreSQL pour Python) : https://www.psycopg.org/psycopg3/docs/
- `pytest` — écriture de tests et fixtures : https://docs.pytest.org/
- `unittest.mock` — doublures de test : https://docs.python.org/3/library/unittest.mock.html
- Spécification GBFS (General Bikeshare Feed Specification) : https://github.com/MobilityData/gbfs
- Vélib' Métropole — open data disponibilité temps réel : https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/
