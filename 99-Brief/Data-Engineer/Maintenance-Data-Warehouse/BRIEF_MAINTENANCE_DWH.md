# Brief : Maintenir et faire évoluer l'entrepôt de données ventes — SCD, marketplace et supervision sous PostgreSQL

## Informations

| Critère | Valeur |
|---------|--------|
| **Durée** | 1 semaine (5 jours) |
| **Niveau** | Intermédiaire-Avancé |
| **Modalité** | Individuel |
| **Technologies** | PostgreSQL, Python, SQL, Schéma en étoile, SCD Type 2, ETL, Docker, cron, SMTP (Mailtrap/MailHog), Git |
| **Prérequis** | [Cours SQL](../../../01-Fondamentaux/SQL/) + [Cours Python](../../../01-Fondamentaux/Python/) + [Cours Docker](../../../02-Containerisation/Docker/) + [Data Warehouse](../../../05-Databases/DataWarehouse/) |

## Contexte

### L'entreprise

**Bouquineo** est une librairie en ligne française créée en 2015. Depuis son siège de Lille, ses 45 salariés animent un catalogue d'environ 12 000 références, vendues sur trois canaux : le site e-commerce, une marketplace de partenaires et un réseau de 8 librairies physiques affiliées. L'équipe data est naissante : un data engineer (vous), une data analyst et un CTO sponsor.

### Le problème

Il y a six mois, votre prédécesseur a mis en production l'entrepôt de données des ventes : un schéma en étoile sous PostgreSQL, avec une table de faits `fait_ventes` entourée de quatre dimensions (`dim_client`, `dim_produit`, `dim_temps`, `dim_canal`), alimenté chaque nuit par un ETL Python. Il fonctionne… la plupart du temps. Et c'est précisément le problème.

Le quotidien est devenu douloureux. En mars, l'équipe pricing a ajusté les prix de centaines de références après sa veille concurrentielle (le concurrent est simulé par Books to Scrape : https://books.toscrape.com). L'ETL a **écrasé les anciens prix** dans `dim_produit` : impossible aujourd'hui de recalculer la marge réelle de mars. Le directeur marketing tempête : « la marge de mars est fausse, on a écrasé les anciens prix ». Même défaut sur `dim_client` : quand un client change de segment, tout son historique d'achats change de segment avec lui, faussant les analyses de cohortes.

Le mois dernier, le pipeline nocturne a par ailleurs **planté deux fois en silence** : personne n'a été prévenu et le CODIR a présenté des chiffres vieux de quatre jours sans le savoir.

Enfin, la DSI vient d'acter l'intégration du **nouveau canal marketplace** : un export CSV quotidien arrive désormais, avec des colonnes renommées par rapport à vos conventions et des formats hétérogènes.

### La question centrale

Une question doit guider chacun de vos choix, et vous devez pouvoir vous y référer à chaque étape :

> **« Comment garantir un entrepôt fiable qui absorbe les évolutions métier sans casser l'existant ? »**

### Les trois demandes

Trois demandes atterrissent dans le même sprint :

- **Demande 1 (marketing)** : historiser les changements de prix produits et de segment client, pour que les analyses passées restent justes.
- **Demande 2 (DSI)** : intégrer la nouvelle source marketplace et créer un datamart « performance marketplace » pour la data analyst, sans casser l'existant.
- **Demande 3 (CTO)** : plus jamais d'incident silencieux — journalisation, alertes, sauvegardes, indicateurs de service et conformité RGPD.

### Sources de données et kit de démarrage

Vous n'inventez rien, vous **héritez**. Le kit de démarrage fourni contient :

- les scripts DDL du schéma en étoile PostgreSQL (tables, contraintes, index) ;
- six mois de données d'activité (environ 180 000 lignes de ventes, 4 500 clients, 12 000 produits, 3 canaux), au format SQL/CSV ;
- l'ETL Python nocturne actuel : chargement quotidien des ventes et mise à jour des dimensions par écrasement (c'est lui, le coupable de la marge de mars) ;
- un générateur de fichiers CSV marketplace (environ 2 000 lignes par jour) : colonnes renommées par rapport à vos conventions, doublons, montants en centimes au lieu d'euros, dates au format américain, plus un fichier volontairement corrompu ;
- des scénarios de rejeu : des séries de changements de prix et de segments datés, pour tester votre historisation.

### Architecture et patterns attendus

- L'entrepôt reste un **schéma en étoile sous PostgreSQL**.
- Pour l'historisation, le pattern attendu est le **Slowly Changing Dimension (SCD) de Type 2** — nouvelles lignes versionnées avec dates de validité et drapeau « courant » ; à vous de déterminer où il s'applique et si un autre type serait localement plus pertinent.
- L'intégration marketplace suit le découpage **staging → entrepôt → datamart**.
- La supervision repose sur une **journalisation catégorisée**, un **système d'alerte par e-mail**, des **sauvegardes planifiées** (partielles et complètes) et un **tableau de bord d'indicateurs de service** adossés à des **SLA** que vous définirez (fraîcheur des données, volumétrie chargée, taux d'erreur).

### Contraintes techniques

- **PostgreSQL imposé** (c'est l'existant) ; **Python** pour les ETL.
- Toute évolution se conçoit et se valide dans un **environnement de test avant application** : l'existant doit continuer à fonctionner à chaque étape (**non-régression**).
- Les **migrations de schéma sont scriptées, numérotées et rejouables** : aucune modification manuelle non tracée.
- L'alerte e-mail s'appuie sur un **serveur SMTP de test** (Mailtrap, MailHog ou équivalent) ; **aucun identifiant en clair dans le code**.
- **Volet RGPD** : registre des traitements de données personnelles et procédure de purge des clients inactifs depuis plus de trois ans.
- Tout le travail est **versionné sur Git dès le premier jour**, avec des commits réguliers.

## Objectifs pédagogiques

À l'issue de ce brief, vous serez capable de :

- **Faire évoluer les ETL d'un entrepôt existant** : adapter un ETL fourni à une nouvelle source (marketplace) et à de nouvelles règles de nettoyage (dédoublonnage, conversion des unités, homogénéisation des dates), en respectant les schémas physiques des zones de sortie (staging, entrepôt, datamart) ;
- **Historiser les dimensions d'un entrepôt** en implémentant un SCD Type 2 (dates de validité, drapeau courant, versions successives) sur des dimensions existantes, sans perdre l'historique déjà accumulé ;
- **Gérer et superviser un entrepôt en production** : concevoir une journalisation catégorisée, un système d'alerte, des sauvegardes planifiées et testées, des indicateurs de service adossés à des SLA ;
- **Assurer la non-régression** : faire évoluer un système existant sans jamais casser ce qui fonctionne, en validant chaque changement dans un environnement de test ;
- **Documenter l'exploitation** d'un entrepôt par cas d'usage et assurer la **conformité RGPD** (registre des traitements, procédure de purge ou d'anonymisation).

## Architecture cible

L'entrepôt reste un schéma en étoile sous PostgreSQL. Vous le faites évoluer en ajoutant l'historisation SCD Type 2 sur les dimensions concernées, une chaîne d'intégration marketplace en `staging → entrepôt → datamart`, et une couche de supervision (journalisation, alertes, sauvegardes, SLA).

```
                          +----------------------+
   Ventes quotidiennes    |   ETL NOCTURNE       |   Export CSV marketplace
   (fichiers quotidien/)  |   (Python)           |   (marketplace/, ~2000 l/j)
          |               |  détection changement|          |
          |               |  + historisation SCD |          |
          +-------+-------+----------+-----------+----+------+
                  |                  |                |
                  |         +--------v--------+       |
                  |         |  ZONE STAGING   |<------+
                  |         |  mapping cols,  |  nettoyage : dédoublonnage,
                  |         |  nettoyages     |  centimes -> euros, dates
                  |         +--------+--------+  (chargement idempotent)
                  |                  |
       +----------v------------------v--------------------------+
       |  ENTREPOT — SCHEMA EN ETOILE (PostgreSQL)              |
       |                                                        |
       |    dim_client*      dim_produit*      dim_temps        |
       |   (SCD Type 2)      (SCD Type 2)                       |
       |         \               |               /             |
       |          \              |              /               |
       |           +----> fait_ventes <--------+                |
       |          /                                             |
       |    dim_canal (enrichie : e-commerce, affiliés,         |
       |               marketplace)                             |
       +----------+---------------------------------+-----------+
                  |                                   |
        +---------v----------+            +-----------v-----------+
        |  DATAMART          |            |  SUPERVISION          |
        |  "performance      |            |  - journal categorise |
        |   marketplace"     |            |  - alerte e-mail SMTP |
        |  (agregations pour |            |  - sauvegardes plan.  |
        |   la data analyst) |            |  - SLA + tableau bord |
        +--------------------+            +-----------------------+

  * dimensions historisees en SCD Type 2 (dates de validite + drapeau courant)
```

> Vous produirez votre propre schéma d'architecture **au format image** (draw.io ou équivalent, pas d'ASCII art), montrant l'entrepôt **avant et après évolution**, à joindre au rendu.

## Données fournies

Le kit de démarrage se trouve dans le dossier [`starter-kit/`](starter-kit/) de ce brief. Il contient :

- `ddl/01_schema_etoile.sql` — les scripts DDL du schéma en étoile PostgreSQL existant (tables de faits et de dimensions, contraintes, index) ;
- `chargement_initial.sql` — le chargement initial des six mois de données dans l'entrepôt ;
- `etl_nocturne.py` — **l'ETL nocturne hérité, volontairement défaillant** : il met à jour les dimensions **par écrasement** (c'est le coupable de la marge de mars), ne produit **aucun log** et n'est **pas idempotent**. Vous devez l'**auditer puis le remplacer** ; ne cherchez pas à l'améliorer tel quel ;
- `data/` — six mois de données d'activité et les jeux de rejeu :
  - `dim_client.csv`, `dim_produit.csv`, `dim_temps.csv` — les dimensions ;
  - `ventes.csv` — les faits (environ 180 000 lignes) ;
  - `scenario_prix.csv` + `scenario_segments.csv` — scénarios de rejeu : changements de prix et de segments datés pour tester votre historisation ;
  - `quotidien/` — les fichiers de ventes quotidiens à charger d'affilée ;
  - `marketplace/` — les fichiers CSV marketplace quotidiens (colonnes renommées, doublons, montants en centimes, dates au format américain), dont un fichier `_corrompu.csv` volontairement invalide ;
- `generate_data.py` + `generate_marketplace.py` — les générateurs permettant de reproduire ou d'étendre les jeux de données (activité de base et flux marketplace).

## Travail demandé

Travail individuel sur la semaine. L'entraide est encouragée — revue de pair, débogage à deux —, mais chacun rend son propre travail et doit pouvoir expliquer chaque ligne de son code. Le formateur joue le rôle du CTO : sollicitez-le pour arbitrer des priorités ou valider vos SLA, comme vous le feriez en entreprise.

### Phase 1 — Cadrage et audit de l'existant (J1)

Aucune ligne de code de production dans cette phase : on commence par comprendre ce dont on hérite.

- Installez le kit de démarrage, chargez les six mois de données, faites tourner l'ETL existant et explorez le modèle en étoile.
- Documentez chaque source (format, volume, fréquence, qualité constatée), y compris le nouveau CSV marketplace.
- Auditez l'existant à la lumière de la question centrale : que se passe-t-il exactement, table par table, quand un prix change aujourd'hui ? Pourquoi la marge de mars est-elle irrécupérable en l'état ? Et si l'ETL plante à 3 h du matin, qui le sait, quand, et quelles données manqueront au CODIR ?
- Formalisez un court **rapport d'audit** et ouvrez un **Kanban public** : les trois demandes deviennent des user stories découpées, priorisées et estimées — laquelle traiter en premier, et comment justifierez-vous cet arbitrage devant le CTO ?

**Résultat testable en fin de J1 :** environnement fonctionnel démontrable, documentation des sources, audit et Kanban publiés.

### Phase 2 — Historiser les dimensions (J2-J3)

Attaquez la demande marketing : historisation des prix dans `dim_produit` et des segments dans `dim_client`.

- Quel type de SCD correspond à chaque type de changement, et pourquoi le Type 2 (dates de validité, drapeau courant) est-il ici attendu ?
- Quelles colonnes ajouter, et faut-il introduire une clé de substitution — auquel cas, que deviennent les jointures de `fait_ventes` ?
- Comment migrer les données déjà en place sans perdre les six mois d'historique ?
- Mettez à jour l'ETL nocturne pour qu'il détecte les changements et crée de nouvelles versions au lieu d'écraser.

**Résultat testable en fin de J3 :** en rejouant le scénario de changements fourni dans le kit, une requête SQL démontre que la marge de mars se recalcule avec les prix en vigueur en mars, la version courante restant immédiatement accessible.

### Phase 3 — Intégrer la marketplace et son datamart (J3-J4)

Place à la demande DSI.

- Créez une zone de **staging** pour l'export CSV quotidien, établissez le **mapping** des colonnes renommées vers vos conventions et appliquez les nettoyages nécessaires : dédoublonnage, conversion des centimes en euros, homogénéisation des dates.
- Comment rendre le chargement **idempotent**, c'est-à-dire qu'un même fichier rejoué deux fois ne crée aucun doublon ?
- Quelles lignes rejeter, et où tracer ces rejets pour pouvoir en rendre compte ?
- Enrichissez `dim_canal`, puis construisez le **datamart « performance marketplace »** destiné à la data analyst — quelles agrégations lui seront réellement utiles ?
- Et surtout, comment prouvez-vous que l'existant n'a pas régressé ?

**Résultat testable en fin de J4 :** plusieurs fichiers quotidiens chargés d'affilée, datamart interrogeable, ETL historiques toujours fonctionnels.

### Phase 4 — Superviser, sauvegarder, se conformer (J4-J5)

La demande du CTO : plus jamais d'incident silencieux.

- Mettez en place une **journalisation** qui catégorise a minima les alertes et les erreurs — au fait, qu'est-ce qui distingue une alerte d'une simple erreur journalisée ?
- Branchez un **envoi d'e-mail automatique** en cas d'erreur.
- Planifiez des **sauvegardes** partielle et complète, et testez une **restauration** dans une base vierge : une sauvegarde jamais restaurée n'existe pas.
- Définissez au moins trois **SLA** (fraîcheur des données, volumétrie chargée, taux d'erreur) — quels seuils déclarez-vous acceptables, et au nom de quel besoin métier ? Restituez les indicateurs correspondants dans un tableau de bord de service.
- Complétez le volet **RGPD** : registre des traitements et procédure de purge des clients inactifs depuis plus de trois ans — purge ou anonymisation, que choisir et pourquoi ?

**Résultat testable :** provoquez une panne avec le fichier corrompu du kit et montrez la chaîne complète **journal → alerte → diagnostic**, puis restaurez une sauvegarde.

### Phase 5 — Documenter et démontrer (J5)

- Rédigez la **documentation d'exploitation** structurée par cas d'usage : que faire quand le pipeline plante ? Comment ajouter une nouvelle source ? Comment restaurer une sauvegarde ? Comment purger un client ?
- Mettez à jour le **schéma d'architecture** (image jointe au repo, pas de schéma ASCII) et les **modèles de données** (colonnes SCD comprises).
- Répétez votre démonstration : elle suivra le scénario imposé décrit dans la section « Démonstration finale ».

### Socle commun (obligatoire)

Tout apprenant livre :

- **SCD Type 2 fonctionnel** sur `dim_produit` et `dim_client` ;
- source **marketplace intégrée** et **datamart** créé ;
- **journalisation catégorisée** et **alerte e-mail** active ;
- une **sauvegarde complète planifiée et restaurée** avec succès ;
- **trois SLA** et leur **tableau de bord** (une page HTML, un notebook ou un dashboard simple suffisent) ;
- **registre RGPD** et **procédure de purge** ;
- **documentation par cas d'usage**.

### Pour aller plus loin (bonus)

Pour celles et ceux qui vont vite :

- implémenter les SCD avec des **snapshots dbt** et couvrir les modèles de tests dbt ;
- remplacer la planification cron par un **DAG Airflow** ;
- identifier un attribut où un **SCD Type 3** serait plus pertinent que le Type 2, l'implémenter et argumenter le choix ;
- ajouter une **sauvegarde incrémentale** ou une **stratégie PITR**.

Les bonus ne compensent jamais un socle incomplet : **terminez d'abord le socle**.

## Livrables

**Repo GitHub PUBLIC (obligatoire)**, contenant :

- un **README complet** : description du projet, technologies utilisées, instructions d'installation et de lancement pas à pas depuis le kit de démarrage, architecture, auteur ;
- les **scripts de migration SQL** numérotés et rejouables (évolutions du schéma : colonnes SCD, `dim_canal`, datamart) ;
- les **ETL Python mis à jour** : détection des changements et historisation, chargement marketplace idempotent avec nettoyages ;
- la **configuration de journalisation et d'alerte e-mail** (fichier `.env.example` fourni, aucun secret commité) ;
- les **scripts de sauvegarde** partielle et complète et leur planification (cron ou équivalent), plus la **procédure de restauration** ;
- les **requêtes ou scripts de vérification** : rejeu du scénario d'historisation, contrôle de non-régression.

**Livrables non-code :**

- le **schéma d'architecture** au format image (PNG ou export draw.io) montrant l'entrepôt avant et après évolution — joint au repo, jamais en ASCII ;
- le lien vers le **Kanban public** (Trello, GitHub Projects ou équivalent) avec les user stories des trois demandes, priorisées, et l'historique de leur avancement ;
- la **documentation d'exploitation** structurée par cas d'usage : pipeline en panne, ajout d'une source, restauration d'une sauvegarde, purge d'un client ;
- le **dictionnaire des modèles de données** à jour, colonnes d'historisation comprises ;
- le **registre RGPD** des traitements et la **procédure de purge** des clients inactifs de plus de trois ans ;
- le **tableau de bord des indicateurs de service** (lien d'accès ou captures dans le repo) avec la **définition écrite des SLA** retenus.

## Démonstration finale

L'évaluation reproduit le format d'une étude de cas : maintenir un entrepôt existant en conditions opérationnelles. Elle se compose de deux volets pondérés.

**Volet 1 — Démonstration technique individuelle : 70 %**

Durée : **15 minutes** de démonstration en direct + **10 minutes** de questions-réponses. Le formateur, dans le rôle du CTO, impose le scénario suivant :

- **rejouer un changement de prix** et prouver, requête à l'appui, que l'historique est conservé et que la marge passée se recalcule correctement ;
- **charger un fichier marketplace valide**, puis le **fichier corrompu**, et montrer la chaîne **journalisation → alerte e-mail → diagnostic** ;
- **présenter le tableau de bord** des indicateurs de service et **restaurer une sauvegarde** dans une base vierge ;
- **présenter le registre RGPD** et dérouler la **procédure de purge** sur un client de test.

Les questions portent sur la justification des choix : type de SCD retenu, seuils des SLA, priorisation des demandes.

**Volet 2 — Revue de code et d'architecture : 30 %**

Réalisée sur le repo GitHub public après la démonstration : structure et lisibilité du code, migrations scriptées et rejouables, qualité de la documentation par cas d'usage, modèles de données à jour, cohérence du schéma d'architecture, historique de commits témoignant d'un travail régulier.

> Un apprenant dont le pipeline ne fonctionne pas en démonstration mais dont le code est structuré et documenté peut valider partiellement les compétences concernées. L'historisation, l'intégration marketplace et la supervision sont évaluées indépendamment : un échec sur l'une n'entraîne pas l'échec des autres. Les éléments bonus (dbt, Airflow, SCD Type 3) ne conditionnent la validation d'aucune compétence.

## Critères de validation

### Intégration des ETL

- Les formats et les volumes de chaque source (entrepôt existant, CSV marketplace) sont documentés, connus et expliqués.
- Les ETL appliquent les traitements de nettoyage attendus : doublons éliminés, montants convertis en euros, formats de dates homogénéisés — vérifiable en rejouant deux fois le même fichier.
- Les données en sortie respectent les schémas physiques des zones de sortie (staging, entrepôt, datamart).
- Le fonctionnement général et les règles de traitement de chaque ETL sont explicités sans ambiguïté dans la documentation.

### Gestion et supervision de l'entrepôt

- Une journalisation de l'activité de l'entrepôt est en place et catégorise a minima les alertes et les erreurs.
- Un système d'alerte e-mail est activé et envoie effectivement un message en cas d'erreur notifiée dans les journaux (démontré en direct).
- Les tâches de maintenance sont priorisées selon les objectifs et les exigences de maintenance (Kanban et justification de l'arbitrage à l'appui).
- Des tâches planifiées de sauvegarde partielle et complète sont programmées et produisent les résultats attendus (restauration démontrée dans une base vierge).
- Les indicateurs de service s'appuient sur des SLA explicites restitués dans un tableau de bord ; la documentation est structurée par cas d'usage, le registre RGPD est complet et la procédure de tri des données personnelles (purge ou anonymisation) est rédigée.

### Historisation des dimensions (SCD)

- Le type de SCD retenu est adapté à chaque type de changement et le choix est justifié dans la documentation.
- L'historisation est fonctionnelle : le rejeu du scénario fourni crée de nouvelles versions datées (dates de validité, drapeau courant) et les anciennes valeurs restent interrogeables.
- Les ETL sont mis à jour en fonction des variations et leur intégration respecte la modélisation initiale (non-régression démontrée sur l'existant).
- La documentation des modèles de données est à jour, variations comprises.

## Ressources

- [Cours SQL](../../../01-Fondamentaux/SQL/)
- [Cours Python](../../../01-Fondamentaux/Python/)
- [Cours Docker](../../../02-Containerisation/Docker/)
- [Data Warehouse](../../../05-Databases/DataWarehouse/)
- Documentation PostgreSQL — sauvegarde et restauration : https://www.postgresql.org/docs/current/backup.html
- Documentation PostgreSQL — `pg_dump` : https://www.postgresql.org/docs/current/app-pgdump.html
- Kimball Group — Slowly Changing Dimension Type 2 : https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/
- Python — tutoriel officiel du module logging : https://docs.python.org/3/howto/logging.html
- CNIL — le registre des activités de traitement : https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement
- dbt — documentation des snapshots (pour le bonus) : https://docs.getdbt.com/docs/build/snapshots
