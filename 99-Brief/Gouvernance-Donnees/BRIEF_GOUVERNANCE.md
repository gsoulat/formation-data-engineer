# Brief : Cataloguer et gouverner les données de Bouquineo avec OpenMetadata

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire |
| **Modalité** | Individuel |
| **Technologies** | OpenMetadata, PostgreSQL, Docker, Docker Compose, SQL, RGPD, RBAC, Git |
| **Prérequis** | [Cours SQL](../../01-Fondamentaux/SQL/) + [Cours Docker](../../02-Containerisation/Docker/) + [RGPD & Gouvernance](../../01-Fondamentaux/RGPD-Gouvernance/) + [Data Warehouse](../../05-Databases/DataWarehouse/) |

## Contexte

### L'entreprise

**Bouquineo** est une librairie en ligne française créée en 2015. Depuis son siège de Lille, ses 45 salariés animent un catalogue d'environ 12 000 références vendues sur trois canaux : le site e-commerce, une marketplace de partenaires et un réseau de 8 librairies physiques affiliées. L'équipe data est réduite : le CTO, sponsor du projet, un data analyst... et vous, data engineer.

### Le problème

Après deux ans de croissance data, le PostgreSQL de l'entreprise est devenu un grenier : des dizaines de tables s'y sont accumulées (ventes, clients, catalogue, événements de navigation issus du streaming), créées au fil des besoins, rarement documentées, jamais supprimées. Plus personne ne sait d'où viennent les données, qui y accède, ni si elles sont fiables. Les symptômes sont quotidiens :

- le data analyst perd plusieurs heures par semaine à chercher « la bonne table » : trois tables contiennent des clients (`clients`, `clients_v2`, `crm_export`) et personne ne sait laquelle fait foi ;
- des emails et numéros de téléphone de clients (données personnelles, PII) traînent dans des tables accessibles à tous les comptes techniques, y compris celui du prestataire marketing ;
- le mois dernier, une campagne d'emailing est partie depuis `crm_export`, une table obsolète : 1 200 clients désinscrits ont été recontactés. Le CTO a géré les plaintes et redoute un contrôle CNIL ;
- aucune règle de qualité n'existe : quand une table cesse d'être alimentée, on s'en aperçoit des semaines plus tard.

Le CTO vous confie la mission : mettre en place un catalogue de données et des règles de gouvernance pour reprendre le contrôle de ce grenier.

### La question centrale

Tout votre travail doit permettre d'y répondre, et vous devez pouvoir vous y référer à chaque étape :

> **« Qui peut accéder à quoi, et peut-on faire confiance à cette donnée ? »**

Chaque décision — choix d'outil, tag, test, policy — devra pouvoir être justifiée par cette question.

### Les sources de données

Le projet est autoportant : un dépôt de démarrage fourni contient un `docker-compose` PostgreSQL, les scripts DDL et un générateur de données. Vous y trouverez :

- **Schéma `raw`** : `clients` (~8 000 lignes, avec emails, téléphones, adresses), `ventes` (~50 000 lignes sur les 3 canaux), `catalogue` (~12 000 références), `evenements_web` (flux de navigation, volumétrie la plus forte), plus les tables « fantômes » `clients_v2` et `crm_export`.
- **Schéma `marts`** : tables agrégées destinées au data analyst (`ventes_par_canal`, `top_titres`, etc.).
- **Veille concurrentielle** : pour sa veille, l'équipe scrape régulièrement le site du concurrent « Books to Scrape » (https://books.toscrape.com — bac à sable légal de scraping). La table `concurrent_prix` en est issue et devra elle aussi être cataloguée et documentée (source externe, fréquence, fiabilité).

### Architecture attendue

Le pattern visé est celui d'un catalogue de données centralisé avec gouvernance par rôles (RBAC) : ingestion automatisée des métadonnées depuis PostgreSQL → enrichissement (descriptions, glossaire métier, classification PII) → règles de qualité exécutées dans le catalogue → politiques d'accès appliquées à des groupes. Un schéma d'architecture, **au format image joint au rendu** (pas de schéma ASCII), devra représenter ces briques et leurs flux.

L'outil cible est **OpenMetadata** (open source, déployable via le Docker Compose officiel). Mais un data engineer ne retient jamais un outil par défaut : en phase de cadrage, vous comparerez trois catalogues open source — **OpenMetadata, DataHub, Amundsen** — au regard des contraintes de Bouquineo (équipe data d'une personne, budget licence nul, source PostgreSQL, exigences RGPD) et vous justifierez le choix retenu.

### Contraintes techniques

- OpenMetadata via Docker Compose demande environ **6 Go de RAM disponibles** : vérifiez votre machine dès le J1. À défaut, utilisez la sandbox en ligne officielle (https://sandbox.open-metadata.org) pour les fonctionnalités d'enrichissement, et documentez précisément ce qui a été fait où.
- Les droits d'accès sont portés par des **groupes** (équipes, rôles), jamais par des individus.
- **Aucun secret** (mot de passe, token) n'est versionné dans le dépôt.
- Toute la configuration d'ingestion est **reproductible** : fichiers de configuration versionnés ou procédure pas à pas documentée.
- Tout le travail est **versionné avec Git**, sur un repo GitHub public.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Cartographier les données disponibles** en référençant leurs usages, leurs sources et leurs métadonnées, et en formalisant une topographie en quatre parties adaptée au contexte de l'entreprise
- **Intégrer les composants d'infrastructure** : déployer un catalogue de données via Docker Compose, le connecter à une source PostgreSQL et documenter une procédure d'installation reproductible par un tiers
- **Gérer le catalogue des données** en tenant compte de leur nature, de leurs sources d'alimentation et de leur cycle de vie, dans le respect du RGPD (alimentation, suppression, monitorage conçus en autonomie et justifiés)
- **Implémenter les règles de gouvernance des données** en traduisant des besoins d'accès en groupes, rôles et policies conformes au RGPD
- **Comparer et choisir un outil** en confrontant plusieurs catalogues open source aux contraintes réelles d'une petite équipe data

## Architecture cible

Le CTO impose le pattern d'un **catalogue de données centralisé avec gouvernance par rôles (RBAC)**. Les métadonnées du PostgreSQL sont ingérées automatiquement, enrichies (glossaire métier, tags PII), soumises à des tests de qualité, puis protégées par des policies appliquées à des groupes d'utilisateurs :

```
                    +----------------------------------+
                    |   PostgreSQL Bouquineo (Docker)  |
                    |   schéma raw : clients, ventes,  |
                    |   catalogue, evenements_web,     |
                    |   clients_v2, crm_export         |
                    |   schéma marts + concurrent_prix |
                    +----------------+-----------------+
                                     |
                     [ Ingestion automatisée des métadonnées ]
                                     |
                    +----------------v-----------------+
                    |          OPENMETADATA            |
                    |   (Docker Compose officiel)      |
                    +----------------+-----------------+
                                     |
        +----------------------------+----------------------------+
        |                            |                            |
+-------v--------+          +--------v--------+          +--------v---------+
| ENRICHISSEMENT |          |    QUALITÉ      |          |     ACCÈS        |
| glossaire      |          | fraîcheur      |          | groupes / rôles  |
| descriptions   |          | complétude     |          | policies RBAC    |
| tags PII/RGPD  |          | unicité        |          | conformes RGPD   |
| table qui fait |          | (seuils +      |          | (data analyst,   |
| foi par domaine|          |  échecs)       |          |  marketing, DE)  |
+----------------+          +-----------------+          +------------------+
        |                            |                            |
        +----------------------------+----------------------------+
                                     |
                    +----------------v-----------------+
                    |  TOPOGRAPHIE + CYCLE DE VIE      |
                    |  sémantique / modèles / flux /   |
                    |  mise à disposition + registre   |
                    |  des traitements + suppression   |
                    +----------------------------------+
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art) à joindre au rendu : PostgreSQL, OpenMetadata, flux d'ingestion et groupes d'utilisateurs.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il met en place l'état initial « grenier » de Bouquineo — schémas `raw` et `marts`, tables redondantes `clients` / `clients_v2` / `crm_export`, PII accessibles à tous — que vous devrez cataloguer et gouverner. Il contient :

- `docker-compose.yml` — pour lancer **PostgreSQL** en local (la source du catalogue) ;
- `.env.example` — variables d'environnement d'exemple (aucun secret réel) ;
- `data/.gitkeep` — dossier de travail pour les données générées ;
- `scripts/generate_data.py` et `scripts/scrape_concurrent.py` — génèrent et peuplent les données du grenier ainsi que la table `concurrent_prix` issue de la veille ;
- `scripts/requirements.txt` — dépendances Python des scripts ;
- `sql/01_schemas_roles.sql` — création des schémas `raw` / `marts` et des rôles ;
- `sql/02_tables_raw.sql` — tables brutes, y compris les tables fantômes redondantes ;
- `sql/03_load_data.sql` — chargement des données dans le PostgreSQL ;
- `sql/04_marts_grants.sql` — tables agrégées `marts` et attributions d'accès initiales (PII accessibles, état à corriger).

> **L'outil cible OpenMetadata ne fait pas partie du kit** : il se déploie via son **propre Docker Compose officiel** (voir la section Ressources). Le kit fournit uniquement la source PostgreSQL et son contenu à cataloguer.

## Travail demandé

Travail individuel sur 5 jours (J1-J5). L'entraide est encouragée — confrontez vos comparatifs d'outils, débloquez-vous mutuellement sur Docker — mais chaque déploiement, chaque configuration et chaque livrable est personnel. Chaque phase produit un résultat vérifiable : ne passez à la suivante que lorsque celui de la phase courante est démontrable.

### Phase 1 — Cadrage et comparatif (J1)

Aucune ligne de code ni aucun déploiement de catalogue en Phase 1. Lancez uniquement le PostgreSQL du kit de démarrage et explorez-le comme le ferait un auditeur : quelles tables existent, lesquelles semblent redondantes, où se cachent les données personnelles, quelles tables ne sont plus alimentées ? Documentez cet inventaire brut : c'est la matière première de votre topographie.

Rédigez ensuite le comparatif **OpenMetadata / DataHub / Amundsen** : quels critères comptent vraiment pour une équipe data d'une personne — facilité de déploiement, connecteur PostgreSQL, gestion des rôles, tests de qualité intégrés, dynamisme de la communauté ? Un tableau de fonctionnalités recopié d'un blog ne suffit pas : chaque critère doit être relié à une contrainte de Bouquineo.

Ouvrez enfin votre **Kanban public** avec des user stories formulées du point de vue des utilisateurs (« En tant que data analyst, je veux trouver la table de ventes qui fait foi en moins de 2 minutes »).

**Résultat testable en fin de J1 :** inventaire des tables, comparatif argumenté avec choix justifié, Kanban alimenté.

### Phase 2 — Déploiement et ingestion des métadonnées (J2)

Déployez OpenMetadata avec le Docker Compose officiel (vérifiez vos 6 Go de RAM ; sinon, basculez sur la sandbox et notez-le). Connectez le PostgreSQL Bouquineo et lancez l'ingestion des métadonnées.

- Quels schémas et quelles tables incluez-vous ou excluez-vous, et pourquoi ?
- Faut-il ingérer les tables fantômes comme `crm_export` — et si oui, comment signaler qu'elles ne font pas foi ?
- Comment rejouer l'ingestion demain sans tout refaire à la main ?
- Documentez la procédure d'installation au fur et à mesure : un tiers doit pouvoir la dérouler sans erreur.

**Résultat testable en fin de J2 :** les tables Bouquineo sont visibles et navigables dans le catalogue, la procédure d'installation est rédigée.

### Phase 3 — Sémantique, topographie et classification (J2-J3)

Un catalogue est vide de sens tant qu'il ne parle pas le langage du métier.

- Construisez un **glossaire métier de 10 à 15 termes** — que signifie « vente » chez Bouquineo : une ligne de commande ou une commande entière ? qu'est-ce qu'un « client actif » ? — et rattachez ces termes aux tables et colonnes.
- Décrivez les tables et colonnes clés, désignez la **table qui fait foi** pour chaque domaine.
- Classez les colonnes sensibles avec des **tags PII/RGPD** : l'email est une évidence, mais l'historique d'achat d'un client identifiable ?
- Formalisez votre **topographie des données en quatre parties** : sémantique (glossaire), modèles de données, traitements et flux, mise à disposition et conditions d'accès.

**Résultat testable :** un camarade retrouve la bonne table de ventes en moins de 2 minutes via la recherche du catalogue.

### Phase 4 — Qualité, accès et cycle de vie (J3-J4)

Instaurez la confiance, puis le contrôle.

- **Qualité** : définissez des tests dans OpenMetadata — fraîcheur (la table est-elle encore alimentée ?), complétude (taux de valeurs manquantes sur les colonnes critiques), unicité (doublons d'identifiants). Quels seuils choisissez-vous, et que se passe-t-il quand un test échoue ?
- **Accès** : créez des groupes (data analyst, marketing, data engineering) et leurs policies : le data analyst lit les marts mais pas les colonnes PII ; le marketing n'accède jamais aux emails. Comment prouvez-vous concrètement qu'une policy fonctionne ?
- **Cycle de vie** : rédigez le **registre des traitements** de données personnelles (finalité, base légale, durée de conservation par table) et les procédures de suppression associées : que devient une ligne client 3 ans après sa dernière commande, et comment `crm_export` doit-elle disparaître ?

**Résultat testable :** tests de qualité exécutés avec résultats visibles, policies démontrées avec deux comptes distincts, registre et procédures rédigés.

### Phase 5 — Monitorage, documentation et démonstration (J5)

Assurez la durabilité : comment saurez-vous demain que l'ingestion ou le service s'est arrêté ? Finalisez le README, le schéma d'architecture (image), la topographie, et préparez une démonstration scénarisée qui répond à la question centrale : qui peut accéder à quoi, et peut-on faire confiance à cette donnée ?

**Résultat testable :** la démonstration se déroule sans improvisation.

### Socle commun (obligatoire)

- Comparatif argumenté des 3 catalogues open source.
- OpenMetadata déployé (ou sandbox justifiée).
- Métadonnées PostgreSQL ingérées et navigables.
- Glossaire de 10 à 15 termes rattachés aux tables/colonnes.
- Tags PII posés sur les colonnes sensibles.
- Tests de qualité couvrant fraîcheur, complétude et unicité.
- Au moins 2 groupes avec policies effectives.
- Registre des traitements et procédures de suppression.
- Topographie des données en 4 parties.

### Pour aller plus loin (bonus, pour les plus rapides)

- **Lignage automatisé** : ingérer le lignage depuis dbt ou les logs de requêtes pour visualiser les flux `raw` → `marts`.
- **Alertes qualité** : notifier (Slack, email, webhook) l'échec d'un test.
- **Seconde source** : brancher un data warehouse comme seconde source du catalogue.

Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables

À rendre au plus tard J5 à 12 h :

1. **Repo GitHub public** contenant :
   - un **README complet** : description du projet, technologies utilisées, instructions d'installation et de lancement (PostgreSQL du kit + OpenMetadata), architecture, auteur ;
   - les **fichiers de configuration versionnés** : `docker-compose` utilisé, configuration d'ingestion (YAML ou export), variables d'environnement d'exemple (`.env.example`) — aucun secret réel versionné ;
   - le **comparatif des 3 catalogues** open source (OpenMetadata, DataHub, Amundsen), critères reliés aux contraintes de Bouquineo et choix justifié ;
   - la **topographie des données en 4 parties** : sémantique (glossaire), modèles de données, traitements et flux, mise à disposition ;
   - le **registre des traitements** de données personnelles et les procédures de suppression liées au cycle de vie ;
   - la **documentation des groupes**, des droits associés et de la procédure de mise à jour des règles ;
   - la **procédure d'installation et de configuration pas à pas**, reproductible par un tiers.

2. **Livrables non-code** :
   - le **schéma d'architecture** au format image (PNG ou export draw.io) : PostgreSQL, OpenMetadata, flux d'ingestion, groupes d'utilisateurs — pas de schéma ASCII ;
   - le lien vers le **Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories et l'historique de la semaine ;
   - des **captures d'écran datées** versionnées dans le repo : glossaire, tags PII sur les colonnes, résultats des tests de qualité, écran des rôles et policies (indispensables si la sandbox est utilisée) ;
   - le **glossaire métier** de 10 à 15 termes visible dans le catalogue (captures ou export).

3. **Démonstration (J5)** : catalogue opérationnel et scénario de démonstration répondant à la question centrale.

Tout livrable absent du repo au moment de la revue est considéré comme non rendu.

## Démonstration finale

Préparez une démonstration de **15 minutes** (+ 10 minutes de questions), pilotée par la question centrale. Scénario attendu :

- présentation en 2 minutes du comparatif d'outils et du choix d'OpenMetadata ;
- recherche d'une table dans le catalogue et lecture de sa fiche : description, terme de glossaire, tags PII, table qui fait foi ;
- lecture des résultats des tests de qualité (fraîcheur, complétude, unicité) ;
- preuve du contrôle d'accès : montrer avec **deux comptes ou rôles distincts** que le data analyst lit les marts sans voir les PII et que le marketing n'accède pas aux emails ;
- présentation du registre des traitements et d'une procédure de suppression.

Les questions porteront sur vos choix : pourquoi ce seuil de complétude ? pourquoi des groupes plutôt que des droits individuels ? que se passe-t-il si le test de fraîcheur échoue ?

**Pondération de l'évaluation : 70 % démonstration technique / 30 % revue de dépôt et d'architecture.** La revue (30 %) porte sur la lisibilité du README, la reproductibilité de la procédure d'installation, la qualité du comparatif, la complétude de la topographie en 4 parties, la cohérence du schéma d'architecture, l'absence de secrets versionnés et un historique de commits réguliers témoignant de la progression sur la semaine.

**Cas de la sandbox :** le recours à la sandbox en ligne (machine disposant de moins de 6 Go de RAM) n'est pas pénalisant s'il est documenté, mais la procédure d'installation Docker doit malgré tout être rédigée et argumentée. Un catalogue non fonctionnel en démonstration (déploiement cassé, ingestion incomplète) mais accompagné d'un dépôt structuré et documenté — comparatif solide, topographie rédigée, registre des traitements et procédures conformes — permet une validation partielle. Inversement, une démonstration réussie sans documentation ni justification des choix ne suffit pas.

## Critères de validation

### Cartographie et topographie des données

- La topographie des données est complète et structurée en 4 parties : sémantique, modèles de données, traitements et flux, mise à disposition.
- Le glossaire métier compte 10 à 15 termes définis et rattachés à des tables ou colonnes du catalogue.
- Les usages, sources et métadonnées des tables du kit (y compris les tables redondantes) sont référencés, et la table qui fait foi est désignée pour chaque domaine.
- L'inventaire distingue explicitement les données personnelles (PII) des autres données.

### Intégration de l'infrastructure

- OpenMetadata est installé et fonctionnel (ou la sandbox est utilisée avec justification documentée et procédure Docker rédigée).
- Le catalogue est connecté au système de stockage PostgreSQL et l'ingestion s'exécute sans erreur.
- La documentation couvre l'installation et la configuration et permet à un tiers de dérouler la procédure sans erreur.
- Aucun secret n'est versionné dans le dépôt.

### Gestion du catalogue et cycle de vie RGPD

- Les métadonnées des tables Bouquineo sont intégrées dans le catalogue : descriptions, tags, termes de glossaire.
- Les choix d'alimentation du catalogue sont justifiés source par source (inclusions et exclusions argumentées).
- Les procédures de suppression sont rédigées, liées au cycle de vie des données et conformes au RGPD ; le registre des traitements couvre tous les traitements de données personnelles du périmètre.
- Un monitorage permet de détecter une rupture d'alimentation ou de service (test de fraîcheur, alerte ou procédure de contrôle documentée).

### Règles de gouvernance et accès

- Les droits sont appliqués à des groupes et non à des individus.
- Les accès répondent aux besoins exprimés et sont limités au nécessaire : le data analyst lit les marts sans accéder aux PII, le marketing n'accède pas aux emails — démontré avec deux comptes ou rôles distincts.
- Les accès sont conformes au RGPD (minimisation, finalité).
- La documentation couvre les groupes, les droits associés et la procédure de mise à jour des règles.

## Ressources

- [Cours SQL](../../01-Fondamentaux/SQL/)
- [Cours Docker](../../02-Containerisation/Docker/)
- [RGPD & Gouvernance](../../01-Fondamentaux/RGPD-Gouvernance/)
- [Data Warehouse](../../05-Databases/DataWarehouse/)
- Déploiement local d'OpenMetadata avec Docker (documentation officielle) : https://docs.open-metadata.org/latest/quick-start/local-docker-deployment
- Connecteur PostgreSQL d'OpenMetadata (documentation officielle) : https://docs.open-metadata.org/latest/connectors/database/postgres
- Sandbox OpenMetadata en ligne (alternative si machine < 6 Go de RAM) : https://sandbox.open-metadata.org
- DataHub, catalogue open source (site officiel, pour le comparatif) : https://datahubproject.io
- Amundsen, catalogue open source (dépôt officiel, pour le comparatif) : https://github.com/amundsen-io/amundsen
- CNIL — le registre des activités de traitement : https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement
