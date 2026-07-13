# Brief — Administration PostgreSQL pour une plateforme logistique

## Competences et niveaux

| Competence | Niveau |
|---|---|
| **C2.** Cartographier les donnees disponibles | Niveau 3 — Transposer |
| **C3.** Concevoir un cadre technique d'exploitation | Niveau 3 — Transposer |
| **C9.** Developper des requetes SQL | Niveau 3 — Transposer |
| **C10.** Developper des regles d'agregation | Niveau 3 — Transposer |
| **C11.** Creer une base de donnees | Niveau 3 — Transposer |
| **C16.** Gerer l'entrepot de donnees | Niveau 3 — Transposer |

---

## Description rapide

Vous etes recrute(e) comme Data Engineer chez TransFlow, une entreprise de logistique en pleine croissance. Votre mission : deployer une base de donnees PostgreSQL conteneurisee, modeliser et alimenter le schema de donnees, optimiser les performances via indexes, vues, partitions et clusters, puis mettre en place une strategie de sauvegarde fiable.

---

## Contexte

TransFlow est une entreprise de logistique basee a Lyon qui gere le transport de marchandises pour 350 clients a travers la France. L'entreprise opere une flotte de 120 vehicules et traite en moyenne 2 000 livraisons par jour depuis 3 entrepots regionaux (Lyon, Bordeaux, Lille).

Jusqu'a present, le suivi des operations reposait sur des fichiers Excel partages entre les equipes. Avec la croissance de l'activite (+40% en 2 ans), ce systeme atteint ses limites : donnees dupliquees, pas d'historique fiable, impossibilite de produire des tableaux de bord en temps reel.

La direction a decide de migrer vers une base de donnees PostgreSQL. Vous intervenez comme Data Engineer pour concevoir, deployer et administrer cette base.

Les donnees a modeliser couvrent :

- **Les clients** : coordonnees, contrats, volume mensuel
- **Les entrepots** : localisation, capacite, zones de stockage
- **La flotte de vehicules** : type, capacite, statut, maintenance
- **Les chauffeurs** : informations personnelles, permis, rattachement entrepot
- **Les commandes** : client, articles, poids, volume, date souhaitee
- **Les livraisons** : commande, vehicule, chauffeur, itineraire, statut, horodatages
- **Les incidents** : retards, avaries, retours

Le volume estime est de 700 000 livraisons par an, avec un historique de 3 ans a integrer (~2,1 millions de lignes sur la table livraisons).

L'infrastructure doit etre conteneurisee pour faciliter le deploiement sur les futurs environnements de staging et de production.

### Donnees fournies

Les fichiers CSV echantillons sont disponibles dans le dossier `data/`. Ils representent un sous-ensemble realiste des donnees (~1 000 livraisons). Un script Python `data/generate_full_dataset.py` est fourni pour generer le volume reel (2,1M lignes) directement dans PostgreSQL une fois la base deployee.

---

## Modalites pedagogiques

Travail **individuel** sur **5 jours**.

### Jour 1 — Infrastructure et decouverte des donnees

Deployer PostgreSQL via Docker Compose. Explorer les fichiers CSV fournis et produire une cartographie des donnees disponibles : sources, volumetrie, types, qualite, relations identifiees.

- Quelles informations manquent ou sont incoherentes dans les fichiers sources ?
- Comment structurer votre `docker-compose.yml` pour persister les donnees entre les redemarrages ?
- Quelle version de PostgreSQL choisir et pourquoi ?

### Jour 2 — Modelisation et creation du schema

Concevoir le modele de donnees (MCD/MLD), creer les tables avec contraintes (PK, FK, NOT NULL, CHECK, UNIQUE), charger les donnees depuis les CSV.

- Comment gerer les dependances entre tables lors du chargement ?
- Quelles contraintes CHECK sont pertinentes pour garantir la coherence metier ?
- Comment gerer les valeurs manquantes ou incoherentes identifiees au Jour 1 ?

### Jour 3 — Requetage et agregation

Ecrire des requetes SQL couvrant les besoins metier : jointures multi-tables, agregations, sous-requetes, CTE. Creer des vues pour les requetes recurrentes.

- Quand privilegier une CTE plutot qu'une sous-requete ?
- Quelle difference entre une vue standard et une vue materialisee ? Dans quel cas utiliser l'une ou l'autre ?
- Comment calculer des KPI logistiques (taux de livraison a l'heure, delai moyen, top clients) ?

### Jour 4 — Optimisation des performances

Analyser les plans d'execution (EXPLAIN ANALYZE), creer des indexes adaptes, mettre en place le partitionnement sur les tables volumineuses, utiliser CLUSTER pour reorganiser physiquement les donnees.

- Comment identifier les requetes qui necessitent un index ?
- Quel type de partitionnement est le plus adapte a la table livraisons ?
- Que se passe-t-il quand on execute CLUSTER sur une table en production ?
- Quelle difference entre un index B-tree et un index GIN/GiST ?

### Jour 5 — Sauvegarde, restauration et soutenance

Mettre en place une strategie de sauvegarde avec pg_dump et rsync vers un repertoire distant simule. Tester la restauration complete. Documenter l'ensemble et preparer la soutenance.

- Quelle difference entre pg_dump et une copie physique des fichiers ?
- Pourquoi faut-il utiliser `pg_start_backup`/`pg_stop_backup` avant un rsync sur les fichiers PostgreSQL ?
- Comment automatiser les sauvegardes avec un cron ?
- Comment verifier l'integrite d'une sauvegarde ?

---

## Modalites d'evaluation

Soutenance individuelle de **20 minutes** le jour 5 :

- **10 minutes** de demonstration technique (infrastructure, requetes, optimisations, sauvegarde/restauration)
- **10 minutes** de questions du jury

L'apprenant doit demontrer sa capacite a justifier chaque choix technique (modelisation, indexes, partitionnement, strategie de sauvegarde).

---

## Livrables attendus

Repo GitHub **public** contenant :

- `docker-compose.yml` fonctionnel (PostgreSQL + volume persistant)
- Scripts SQL : creation du schema (DDL), chargement des donnees, requetes metier, creation d'indexes/vues/partitions
- Script de sauvegarde (`pg_dump` + `rsync`)
- Cartographie des donnees (format libre : schema, tableau, markdown)
- Modele de donnees (MCD ou MLD au format image ou drawio)
- Captures d'ecran des EXPLAIN ANALYZE avant/apres optimisation
- `README.md` complet :
  - Description du projet
  - Technologies utilisees
  - Instructions d'installation / lancement
  - Architecture de la base
  - Choix techniques justifies
  - Auteur

---

## Criteres de performance

- Docker Compose fonctionnel : PostgreSQL demarre, les donnees persistent apres redemarrage
- Cartographie des donnees complete : toutes les sources identifiees, qualite evaluee, relations documentees
- Schema de base coherent : contraintes PK/FK/CHECK appliquees, types de donnees appropries
- Donnees chargees sans perte ni duplication depuis les CSV
- Requetes SQL fonctionnelles couvrant : jointures (INNER, LEFT, FULL), agregations (GROUP BY, HAVING), CTE, fonctions fenetres (ROW_NUMBER, RANK, LAG/LEAD)
- Vues creees pour au moins 3 cas d'usage metier
- Indexes pertinents crees avec justification basee sur EXPLAIN ANALYZE
- Partitionnement implemente sur au moins une table volumineuse
- CLUSTER execute avec impact mesure
- Sauvegarde pg_dump fonctionnelle et restauration testee
- Transfert rsync operationnel vers un repertoire distant simule
- Code versionne sur GitHub, README complet

---

## Ressources

- [Documentation PostgreSQL officielle](https://www.postgresql.org/docs/current/)
- [Docker Hub PostgreSQL](https://hub.docker.com/_/postgres)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [pg_dump documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
