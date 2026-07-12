# Brief : Pipeline de streaming Kafka pour suivre les ventes flash de Bouquineo en temps réel

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | Apache Kafka (mode KRaft), Python (confluent-kafka), Docker & Docker Compose, PostgreSQL, SQL, Git |
| **Prérequis** | [Cours Python](../../../01-Fondamentaux/Python/) + [Cours SQL](../../../01-Fondamentaux/SQL/) + [Cours Docker](../../../02-Containerisation/Docker/) + [Cours Kafka](../../../06-Data-Engineering/Kafka/) |

## Contexte

### L'entreprise

**Bouquineo** est une librairie en ligne française créée en 2015. Depuis son siège de Lille, ses 45 salariés animent un catalogue d'environ 12 000 références vendues sur trois canaux : le site e-commerce, une marketplace de partenaires et 8 librairies physiques affiliées. L'équipe data est naissante : un data engineer (vous), une data analyst et un CTO sponsor du projet.

### Le problème

Depuis quelques mois, Bouquineo organise une **vente flash mensuelle** : pendant 48 heures, une sélection de titres est fortement remisée et la fréquentation explose, avec des pics d'environ 50 commandes par minute lors de la dernière édition.

Problème : toute la chaîne de reporting est en **batch**. Les commandes sont exportées chaque nuit, transformées le matin, et le tableau de bord de la data analyst n'est à jour que le lendemain. Pendant la vente flash, le marketing pilote donc à l'aveugle : impossible de savoir si la promotion sur la sélection « polar scandinave » fonctionne, si un titre part en rupture de stock ou si les ventes s'effondrent depuis une heure.

Le CTO a tranché : le batch quotidien reste en place pour le reporting officiel, mais il faut une **voie rapide, événementielle**, pour les ventes flash.

### La question centrale

La responsable marketing résume le besoin en une phrase, qui devient la question centrale du projet. Chaque choix technique de la semaine devra pouvoir être justifié par sa contribution à cette question :

> **« Que se passe-t-il sur le site en ce moment ? »**

### Les sources de données

- **Générateur d'événements Python** (fourni dans le kit de démarrage) : il simule le trafic d'une vente flash. Il émet des événements de **commande** (JSON : identifiant de commande, horodatage, référence du titre, quantité, prix unitaire, canal de vente) et des événements de **clickstream** (JSON : page vue, session, référence produit). Le débit est configurable jusqu'à environ 50 commandes par minute, avec des pièges réalistes : doublons d'événements, formats de date hétérogènes, montants parfois manquants.
- **Catalogue produits et état des stocks** : scripts DDL et données d'initialisation PostgreSQL fournis dans le kit (environ 12 000 références, quelques Mo).
- **Pour le bonus** : le flux public temps réel de **Wikimedia EventStreams** (https://stream.wikimedia.org/v2/stream/recentchange), un vrai flux mondial d'événements JSON, et le site bac à sable **Books to Scrape** (https://books.toscrape.com).

Ce brief est un épisode de la vie data de Bouquineo (le reporting batch quotidien y montrait ses limites), mais il est réalisable de façon **autonome** : le kit de démarrage contient le générateur d'événements, les scripts DDL et les données d'initialisation. Aucun livrable d'un brief précédent n'est nécessaire.

### Contraintes techniques

- **Kafka en local via Docker Compose, mode KRaft** (sans ZooKeeper), un seul broker suffit.
- Consommateurs et traitements en **Python** ; persistance dans **PostgreSQL**.
- **Prérequis machine** : Docker et Docker Compose installés, environ 4 Go de RAM libres. Vérifiez ce point dès la première heure du projet et signalez tout blocage au formateur.
- Le générateur d'événements fourni **n'est pas à réécrire**, mais vous devez savoir expliquer son fonctionnement.
- Tout le code est **versionné sur GitHub dès le premier jour**.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Concevoir l'architecture d'une plateforme de flux** : adapter un pattern de streaming publish/subscribe documenté au cas Bouquineo, distinguer voie batch et voie streaming dans un schéma, et comparer Kafka à des outils alternatifs au regard des 3V (volumétrie, vitesse, variété).
- **Intégrer les composants d'une infrastructure de flux** : monter Kafka (mode KRaft) et PostgreSQL via Docker Compose, créer et paramétrer les topics, et rédiger une procédure d'installation rejouable.
- **Automatiser la consommation de données en continu** depuis un broker Kafka : concevoir seul des consommateurs Python organisés en consumer group, avec gestion des erreurs, des offsets, de l'idempotence et journalisation — aucun exemple de consommateur n'est fourni.
- **Développer des règles d'agrégation** : concevoir des agrégations fenêtrées, le dédoublonnage et l'homogénéisation des formats sans modèle fourni, puis persister les résultats pour un suivi en quasi temps réel.

## Architecture cible

Le pattern attendu est un pipeline de streaming **publish/subscribe** : des **producteurs** émettent des événements au fil de l'eau vers un **broker Apache Kafka** (déployé en local via Docker Compose, mode KRaft, un seul broker), des **groupes de consommateurs Python** lisent ces flux, calculent des **agrégats fenêtrés** et persistent les résultats dans **PostgreSQL**, où une simple requête SQL rafraîchie fait office de mini-dashboard.

Vous situerez cette **voie rapide** par rapport à la **voie batch** existante dans votre schéma d'architecture (à joindre en image au rendu) et justifierez vos choix au regard des 3V : volumétrie, vitesse, variété.

```
                       +------------------------------------+
                       |  GÉNÉRATEUR D'ÉVÉNEMENTS (fourni)  |
                       |  commandes JSON + clickstream JSON |
                       +------------------+-----------------+
                                          |
                                  (producteurs)
                                          |
         +--------------------------------v--------------------------------+
         |                 BROKER APACHE KAFKA (mode KRaft)                |
         |                    Docker Compose, mono-broker                  |
         |   +------------------+   +------------------+   +------------+  |
         |   | topic commandes  |   | topic clickstream|   |   ...      |  |
         |   | (partitions, clé)|   |                  |   |            |  |
         |   +------------------+   +------------------+   +------------+  |
         +--------------------------------+--------------------------------+
                                          |
                              (consumer groups Python)
                                          |
         +--------------------------------v--------------------------------+
         |     CONSOMMATEURS PYTHON  (gestion erreurs / offsets /          |
         |     idempotence / logs)                                         |
         |   - ingestion brute des événements                             |
         |   - agrégations fenêtrées (CA/min, top ventes, alerte stock)   |
         +--------------------------------+--------------------------------+
                                          |
         +--------------------------------v--------------------------------+
         |                     PostgreSQL (Docker)                         |
         |   tables événements bruts + tables d'agrégats                  |
         +--------------------------------+--------------------------------+
                                          |
                              (requête SQL rafraîchie)
                                          |
         +--------------------------------v--------------------------------+
         |     MINI-DASHBOARD  « Que se passe-t-il en ce moment ? »       |
         +-----------------------------------------------------------------+

         ---------------------------------------------------------------
         VOIE BATCH EXISTANTE (conservée pour le reporting officiel) :
         export nuit -> transformation matin -> dashboard J+1
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu, en distinguant clairement la voie batch existante et la voie streaming cible.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `generator.py` — le **générateur d'événements** de vente flash (commandes + clickstream JSON). Vous le **configurez** (débit, destination) et le branchez sur vos topics : **il n'est pas à réécrire**, mais vous devez savoir expliquer son fonctionnement ;
- `ddl/01_catalogue.sql` — le **schéma catalogue et l'état des stocks** PostgreSQL (environ 12 000 références) : DDL et données d'initialisation.

> **Important** : le kit ne fournit **pas** de `docker-compose.yml` de base. C'est à vous de **construire et adapter votre propre `docker-compose.yml`** — un broker **Kafka en mode KRaft** (mono-broker, sans ZooKeeper) et un **PostgreSQL** — à partir des ressources officielles listées en fin de brief. La procédure d'installation qui en découle doit être documentée et rejouable.

## Travail demandé

Travail individuel sur 5 jours. L'entraide est encouragée : partagez blocages et astuces sur le canal de la promo, mais chacun conçoit, code et soutient son propre pipeline. Le brief distingue un **socle commun obligatoire** et des **pistes bonus** : les profils rapides approfondissent, les autres sécurisent le socle — un socle solide vaut mieux qu'un bonus bancal.

### Phase 1 — Cadrage et conception (J1)

Aucune ligne de code de pipeline. Clonez le kit de démarrage, lisez sa documentation, lancez le générateur en **mode observation** pour examiner les événements JSON produits, et documentez chaque source : structure des messages, champs et types, volumétrie attendue, pièges repérés (doublons ? formats de date ? montants manquants ?).

Comparez ensuite Kafka à au moins **2 outils de streaming alternatifs** (par exemple Redpanda, RabbitMQ ou un service cloud managé) au regard des besoins de Bouquineo, et justifiez le choix de Kafka — ou challengez-le.

Posez sur un **schéma d'architecture** (image, pas d'ASCII) la voie batch existante et la voie streaming cible : où passent les événements, qui les consomme, où atterrissent les agrégats ? C'est aussi le moment de trancher des questions structurantes :

- Combien de topics et comment les nommer ?
- Combien de partitions, et quelle **clé de partitionnement** garantit que les événements d'une même commande restent ordonnés ?

Formalisez votre plan dans un **Kanban public** avec des user stories.

**Résultat testable en fin de J1 :** schéma d'architecture, documentation des sources et Kanban présentés en 5 minutes au formateur.

### Phase 2 — Infrastructure de flux (J2)

Montez l'environnement. Construisez et adaptez votre `docker-compose.yml` pour obtenir un broker **Kafka en mode KRaft** et un **PostgreSQL** opérationnels, créez vos topics avec les paramètres décidés en phase 1 et rédigez au fil de l'eau la **procédure d'installation** : quelqu'un qui clone votre repo doit pouvoir tout relancer en moins de 10 minutes.

- Comment vérifierez-vous que le broker est réellement **sain** avant d'y brancher quoi que ce soit ?
- Si vous détruisez puis recréez les conteneurs, vos topics et vos données survivent-ils, et est-ce un problème ?

**Résultat testable en fin de J2 :** le démarrage de la stack puis la liste des topics fonctionnent sur une machine propre en suivant uniquement votre README.

### Phase 3 — Du producteur aux premiers consommateurs (J2-J3)

Branchez le générateur fourni sur vos topics (configurez-le, ne le réécrivez pas), puis développez vos premiers consommateurs Python organisés en **consumer group**. Commencez simple : consommer les commandes et les écrire brutes dans PostgreSQL. C'est ici que se joue la robustesse :

- Que devient un message JSON malformé — le pipeline s'arrête, l'ignore, le met de côté ?
- Quand validez-vous les **offsets**, et que se passe-t-il si le consommateur crashe entre la lecture d'un message et son écriture en base ?
- Si le même événement est relu après un redémarrage, votre insertion crée-t-elle un doublon ? (Pensez **idempotence** : clé primaire sur l'identifiant d'événement, upsert…)
- Vos **logs** permettent-ils de raconter ce qui s'est passé cette nuit-là ?

**Résultat testable :** le générateur tourne 10 minutes, vous arrêtez et relancez votre consommateur en cours de route, et vous démontrez qu'aucun événement n'est perdu ni dupliqué en base.

### Phase 4 — Agrégations fenêtrées et mini-dashboard (J3-J4)

Le cœur métier. Développez les **règles d'agrégation** qui répondent à la question centrale :

- chiffre d'affaires par **fenêtre d'une minute** ;
- **top des titres** vendus ;
- **alerte de rupture de stock** (stock projeté sous un seuil).

Vos agrégats doivent survivre aux pièges injectés par le générateur :

- Les **doublons** sont-ils écartés avant le calcul du CA ?
- Les **formats de date hétérogènes** sont-ils normalisés en un format unique en sortie ?
- Qu'affiche votre fenêtre « CA par minute » pour une minute **sans aucune vente** ?

Persistez les agrégats dans des tables dédiées et préparez la ou les requêtes SQL qui, rafraîchies, servent de **mini-dashboard** au marketing — le socle n'exige rien de plus qu'une requête rafraîchie à la main.

**Résultat testable :** pendant que le générateur tourne, la requête dashboard affiche le CA de la minute courante et l'alerte stock se déclenche sur un titre en tension.

### Phase 5 — Consolidation, documentation et démo (J5)

Finalisez le README (description, technologies, installation et lancement, architecture, auteur), vérifiez que la procédure d'installation est **rejouable de zéro**, mettez à jour le schéma d'architecture et le Kanban, puis répétez votre démonstration : scénario, ordre des terminaux, plan B si un composant refuse de démarrer le jour J.

### Socle commun (obligatoire)

- Infrastructure **Kafka + PostgreSQL rejouable** via Docker Compose.
- Topics conçus et justifiés.
- Générateur branché.
- Au moins **un consumer group robuste** (erreurs, offsets, idempotence, logs).
- Les **trois agrégats du socle** (CA par minute, top ventes, alerte stock) persistés.
- Requête SQL de dashboard.
- Repo public documenté avec schéma d'architecture et Kanban.

### Pour aller plus loin (bonus)

Dans l'ordre conseillé :

- Consommer un **flux réel** (Wikimedia EventStreams) avec votre architecture.
- Remplacer votre consommateur d'insertion brute par un **connecteur Kafka Connect sink** vers PostgreSQL.
- Exposer les agrégats dans un **dashboard Streamlit** auto-rafraîchi.
- Exprimer une agrégation en **SQL streaming avec ksqlDB**.
- Introduire un **schema registry** et le format **Avro** sur un topic.

Chaque bonus réalisé doit être documenté et démontrable, sinon il ne compte pas. Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables

À rendre au plus tard J5 à 17 h (lien du repo posté sur la plateforme) :

- Un **repo GitHub public** contenant l'ensemble du projet, avec un README structuré : description du projet et de la question métier, technologies utilisées, instructions d'installation et de lancement pas à pas (prérequis Docker et RAM inclus), architecture (schéma intégré au README), auteur.
- Le fichier **`docker-compose.yml`** (Kafka mode KRaft + PostgreSQL) et les scripts ou commandes documentées de création des topics.
- Les **scripts Python des consommateurs** (consumer groups) : ingestion brute et agrégations fenêtrées, avec gestion des erreurs et journalisation.
- Les **scripts SQL** : DDL des tables d'agrégats et la ou les requêtes du mini-dashboard, commentées.
- Le **schéma d'architecture au format image** (PNG ou export draw.io) : voie batch existante, voie streaming cible, topics, consumer groups, base de persistance. Pas de schéma ASCII.
- La **documentation des flux** : pour chaque topic, son nom, son nombre de partitions, sa clé de partitionnement, la structure des messages (champs et types) et la justification des choix.
- Le **comparatif d'outils de streaming** — Kafka face à au moins 2 alternatives (une page maximum, dans le repo).
- Le lien vers le **tableau Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et leur historique de progression.
- Pour chaque **bonus** réalisé : code, configuration et preuve de fonctionnement (capture d'écran ou extrait de log) dans un dossier `bonus/` clairement séparé du socle.

## Démonstration finale

L'évaluation a lieu en fin de semaine (J5) et repose sur deux volets pondérés :

- **Démonstration technique individuelle — 70 %** : 15 minutes de démonstration en direct + 10 minutes de questions. Vous démarrez votre environnement, lancez le générateur d'événements, prouvez que les événements circulent dans les topics, montrez les agrégats fenêtrés qui se mettent à jour dans PostgreSQL via la requête dashboard, et déclenchez au moins un **scénario de robustesse** (arrêt/relance d'un consommateur sans perte ni doublon, ou traitement d'un message malformé). Les questions portent sur les choix de conception : nombre de partitions, clé de partitionnement, gestion des offsets, idempotence, comportement en cas de panne.
- **Revue de code et d'architecture — 30 %** : examen du repo GitHub public (structure, lisibilité, gestion des erreurs, logs, qualité du README), du schéma d'architecture (distinction batch vs streaming, formalisme lisible) et du comparatif d'outils de streaming (pertinence des critères : volumétrie, vitesse, variété, coût d'exploitation).

> **Validation partielle** : un pipeline qui ne fonctionne pas en démonstration mais dont le code est structuré, versionné et documenté peut valider partiellement les compétences concernées. À l'inverse, une démonstration qui fonctionne mais dont le repo est dépourvu de documentation ne valide pas les critères documentaires.

Sans repo GitHub public accessible et sans code versionné, le travail ne peut pas être évalué.

## Critères de validation

### Conception de l'architecture de flux

- Le schéma d'architecture distingue clairement la voie batch existante et la voie streaming cible, avec un formalisme lisible.
- Les choix techniques sont justifiés au regard de la **volumétrie, de la vitesse et de la variété** des données de Bouquineo.
- Un comparatif d'au moins 2 outils de streaming alternatifs à Kafka est documenté avec des critères explicites.
- La conception des topics (nommage, partitions, clé de partitionnement) est documentée et argumentée.

### Intégration de l'infrastructure

- Kafka (mode KRaft) et PostgreSQL démarrent via Docker Compose sans erreur en environnement de test.
- La procédure d'installation du README se déroule sans erreur sur une machine propre.
- Les composants sont effectivement connectés : les événements produits arrivent dans les topics et les données atterrissent dans PostgreSQL.
- La documentation couvre la configuration des composants (ports, volumes, variables d'environnement).

### Automatisation des consommateurs

- Les consommateurs tournent en consumer group et lisent les topics en continu sans intervention manuelle.
- Un message malformé ne stoppe pas le pipeline : il est traité selon une stratégie explicite (rejet, mise de côté, journalisation).
- L'arrêt puis la relance d'un consommateur ne provoquent ni perte ni doublon en base (gestion des offsets et idempotence démontrées en démo).
- Les logs permettent de suivre le fonctionnement du pipeline et de diagnostiquer un incident.

### Règles d'agrégation

- Les trois agrégats du socle (CA par minute, top des ventes, alerte de rupture de stock) sont calculés et persistés correctement.
- Les événements dupliqués sont écartés avant agrégation (vérifiable en rejouant le flux).
- Les formats hétérogènes (dates, montants) sont homogénéisés en un format unique et documenté en sortie.
- La documentation explicite les règles de calcul de chaque agrégat (fenêtre, formule, cas limites).

## Ressources

- [Cours Python](../../../01-Fondamentaux/Python/)
- [Cours SQL](../../../01-Fondamentaux/SQL/)
- [Cours Docker](../../../02-Containerisation/Docker/)
- [Cours Kafka](../../../06-Data-Engineering/Kafka/)
- Documentation officielle Apache Kafka (concepts, configuration, KRaft) : https://kafka.apache.org/documentation/
- Quickstart Apache Kafka (dont lancement via Docker) : https://kafka.apache.org/quickstart
- Client Python confluent-kafka (producer, consumer, offsets) : https://docs.confluent.io/kafka-clients/python/current/overview.html
- PostgreSQL — INSERT ... ON CONFLICT (idempotence des écritures) : https://www.postgresql.org/docs/current/sql-insert.html
- Documentation Docker Compose : https://docs.docker.com/compose/
- Wikimedia EventStreams, flux temps réel public (bonus) : https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams
