# Exemples d'ADRs

Ce document présente quatre ADRs complets pour un projet de **plateforme data engineering**. Ces exemples sont volontairement détaillés pour servir de référence.

---

## ADR-0001 — Utiliser PostgreSQL comme base de données principale

```markdown
# ADR-0001 — Utiliser PostgreSQL comme base de données principale

* Status: accepted
* Date: 2024-01-15
* Deciders: Alice Martin (Tech Lead), Bob Dupont (Data Engineer),
            Marie Laurent (PO)
* Technical Story: https://github.com/dataflow/platform/issues/12

## Contexte et énoncé du problème

La plateforme DataFlow doit stocker et exposer des données analytiques
à une vingtaine d'utilisateurs métier simultanés. Le volume de données
initial est estimé à 50 GB avec une croissance de 20 GB par mois.

Le système actuel utilise SQLite pour les environnements de développement,
ce qui n'est pas scalable en production (pas de connexions concurrentes,
pas de réplication).

Nous avons besoin d'une base de données relationnelle capable de :
- Gérer les accès concurrents (20+ utilisateurs simultanés)
- Supporter des requêtes analytiques complexes (agrégations, fenêtrages)
- S'intégrer avec dbt pour les transformations
- Fonctionner sous Docker en développement et sur Cloud en production

## Facteurs de décision

* Performance pour les requêtes analytiques (agrégations sur 10M+ lignes)
* Support des types JSON et tableaux pour les données semi-structurées
* Maturité de l'écosystème (ORMs, outils de migration, monitoring)
* Licence open source
* Connaissance de l'équipe
* Compatibilité avec dbt, Airflow, et les outils BI (Metabase, Superset)

## Options considérées

* PostgreSQL
* MySQL / MariaDB
* ClickHouse
* DuckDB

## Résultat de la décision

Option retenue : **PostgreSQL**, car c'est la base relationnelle open source
la plus mature, avec le meilleur support des requêtes analytiques complexes,
une intégration native avec tous nos outils data, et une expertise déjà
présente dans l'équipe.

### Conséquences positives

* Support natif du JSON (JSONB) pour les données semi-structurées
* Extensions analytiques (pg_stat_statements, TimescaleDB si besoin)
* Compatible nativement avec dbt, Airflow (hooks), Metabase
* Réplication native pour la haute disponibilité
* Grande communauté, documentation abondante
* Disponible sur tous les clouds majeurs (RDS, Cloud SQL, Azure DB)

### Conséquences négatives

* Moins performant que ClickHouse pour des requêtes OLAP pures
  sur des volumes >1TB (à réévaluer si le volume dépasse 500 GB)
* Nécessite une gestion du connection pooling (PgBouncer) à partir
  de 100+ connexions simultanées
* Pas de columnar storage natif (extension possible avec cstore_fdw)

## Analyse des options

### Option 1 : PostgreSQL

Base relationnelle open source, référence du marché depuis 30 ans.

* Avantage : Support complet SQL:2016, JSONB, CTEs récursives
* Avantage : Intégration native avec tous nos outils (dbt, Airflow, Metabase)
* Avantage : Équipe déjà formée (3/4 membres ont > 2 ans d'expérience)
* Avantage : Extensions nombreuses (PostGIS, TimescaleDB, pg_cron)
* Inconvénient : OLAP limité face aux bases columnar pour >500GB
* Inconvénient : Connection pooling manuel nécessaire

### Option 2 : MySQL / MariaDB

* Avantage : Très répandu, documentation abondante
* Avantage : Performant pour les charges OLTP
* Inconvénient : Support JSON inférieur à PostgreSQL
* Inconvénient : Moins bon support des window functions
* Inconvénient : Intégration dbt moins mature (certains tests ne fonctionnent pas)

### Option 3 : ClickHouse

Base columnar orientée OLAP, conçue pour l'analytique haute performance.

* Avantage : Performances exceptionnelles sur les requêtes analytiques
* Avantage : Compression columnar native (ratio 5-10x)
* Inconvénient : Pas de transactions ACID complètes
* Inconvénient : Pas d'ORM standard (migration difficile)
* Inconvénient : Aucun membre de l'équipe n'a d'expérience ClickHouse
* Inconvénient : Surdimensionné pour notre volume initial (50 GB)

### Option 4 : DuckDB

Base OLAP embarquée, excellente pour l'analyse locale et les pipelines.

* Avantage : Performances impressionnantes pour les analyses locales
* Avantage : Très bien intégré avec Python et pandas/Arrow
* Inconvénient : Pas adapté aux accès multi-utilisateurs simultanés
* Inconvénient : Pas de mode serveur stable en production
* Inconvénient : Adapté au développement local, pas à la production partagée

## Liens

* dbt PostgreSQL adapter : https://docs.getdbt.com/docs/core/connect-data-platform/postgres-setup
* Comparaison PostgreSQL vs MySQL pour le data engineering : [...]
* Décision de réviser en faveur de ClickHouse si volume > 500 GB : ADR-0011 (futur)
```

---

## ADR-0002 — Utiliser FastAPI pour l'API REST

```markdown
# ADR-0002 — Utiliser FastAPI pour l'API REST interne

* Status: accepted
* Date: 2024-01-22
* Deciders: Alice Martin (Tech Lead), Carla Petit (Backend)
* Technical Story: https://github.com/dataflow/platform/issues/18

## Contexte et énoncé du problème

La plateforme doit exposer des endpoints REST pour :
- Déclencher des pipelines Airflow à la demande
- Exposer les données du Data Warehouse aux applications frontend
- Permettre aux outils tiers de s'intégrer (webhooks, exports)

L'équipe est composée de data engineers Python. Nous cherchons
un framework API Python moderne, avec génération automatique de
documentation et support natif de la validation de données.

## Facteurs de décision

* Performance (async natif)
* Documentation automatique (OpenAPI/Swagger)
* Validation des données (typing, Pydantic)
* Courbe d'apprentissage pour une équipe data Python
* Maturité et support communautaire
* Facilité de test

## Options considérées

* FastAPI
* Flask
* Django REST Framework

## Résultat de la décision

Option retenue : **FastAPI**, car sa combinaison d'async natif, de validation
Pydantic et de génération OpenAPI automatique correspond exactement
aux besoins d'une équipe data Python sans expérience backend dédiée.

### Conséquences positives

* Documentation OpenAPI générée automatiquement — aucun effort supplémentaire
* Validation des entrées/sorties via Pydantic intégrée au typing Python
* Async natif — idéal pour les appels vers Airflow et PostgreSQL
* Très facile à tester (TestClient synchrone)
* Rapidement adopté par la communauté data (intégrations MLflow, DVC...)

### Conséquences négatives

* Moins d'abstractions ORM que Django (mais on utilise SQLAlchemy séparément)
* Middleware plus limité que Django pour les fonctionnalités enterprise
* Toujours en version < 1.0 (stabilité API non garantie entre mineures)

## Analyse des options

### Option 1 : FastAPI

* Avantage : Async natif (ASGI), performances comparables à Node.js/Go
* Avantage : Pydantic v2 intégré — validation automatique des requêtes
* Avantage : Swagger UI + ReDoc générés sans configuration
* Avantage : Syntaxe Python moderne (type hints, async/await)
* Inconvénient : Moins mature que Flask/Django (depuis 2018)

### Option 2 : Flask

* Avantage : Très mature, énorme communauté, documentation extensive
* Avantage : Flexible, peu opinionné
* Inconvénient : Pas d'async natif (extensions tierce nécessaires)
* Inconvénient : Pas de validation intégrée — nécessite marshmallow ou autre
* Inconvénient : OpenAPI via flask-swagger, moins bien intégré

### Option 3 : Django REST Framework

* Avantage : Très complet (auth, permissions, serializers, pagination)
* Avantage : Admin Django inclus
* Inconvénient : Lourd pour une API simple
* Inconvénient : Courbe d'apprentissage importante pour l'équipe
* Inconvénient : ORM Django imposé — conflits potentiels avec SQLAlchemy

## Liens

* Documentation FastAPI : https://fastapi.tiangolo.com
* Benchmark ASGI frameworks : https://www.techempower.com/benchmarks/
```

---

## ADR-0003 — Containeriser avec Docker

```markdown
# ADR-0003 — Containeriser tous les services avec Docker

* Status: accepted
* Date: 2024-02-01
* Deciders: Alice Martin, Bob Dupont, DevOps Team (Jean)
* Technical Story: https://github.com/dataflow/platform/issues/24

## Contexte et énoncé du problème

L'équipe travaille sur des machines macOS, Linux et Windows.
Les pipelines Airflow, la base PostgreSQL et l'API FastAPI
doivent fonctionner de manière identique en développement,
staging et production.

Sans isolation, les problèmes de dépendances Python, versions de
PostgreSQL et configurations système entraînent des incohérences
entre les environnements ("ça marche sur ma machine").

## Facteurs de décision

* Reproductibilité des environnements (dev = staging = prod)
* Facilité d'onboarding des nouveaux membres
* Support multi-OS (macOS, Linux, Windows WSL2)
* Intégration CI/CD (GitHub Actions)
* Compétences existantes dans l'équipe

## Options considérées

* Docker + Docker Compose
* Machines virtuelles (VMs)
* Environnements Python virtuels uniquement (venv/conda)
* Nix

## Résultat de la décision

Option retenue : **Docker + Docker Compose**, car c'est le standard
de l'industrie pour l'isolation des services, avec une intégration
native dans tous les outils data (Airflow, dbt, Metabase) et
une courbe d'apprentissage maîtrisée pour l'équipe.

### Conséquences positives

* `docker compose up` suffit pour lancer tout l'environnement
* Images officielles disponibles pour PostgreSQL, Airflow, Redis, Metabase
* Intégration native GitHub Actions (docker buildx, cache layers)
* Facilite le passage à Kubernetes si besoin ultérieur
* Environnements reproductibles garantis

### Conséquences négatives

* Overhead mémoire sur macOS (Docker Desktop consomme ~2-4 GB RAM)
* Courbe d'apprentissage pour les membres sans expérience Docker
* Latence réseau légèrement plus élevée entre services que native
* Docker Desktop nécessite une licence pro pour les entreprises >250 employés
  → Alternative : Colima (macOS) ou Rancher Desktop

## Analyse des options

### Option 1 : Docker + Docker Compose

Standard de facto pour la containerisation des applications.

* Avantage : Images officielles pour tous nos composants
* Avantage : Docker Compose pour orchestrer les services localement
* Avantage : Portable vers Kubernetes (même images)
* Inconvénient : RAM overhead sur macOS

### Option 2 : Machines virtuelles

* Avantage : Isolation complète
* Inconvénient : Lourdes (plusieurs GB par VM), démarrage lent (minutes)
* Inconvénient : Partage difficile entre équipes

### Option 3 : venv uniquement

* Avantage : Simple, aucun overhead
* Inconvénient : Pas d'isolation système (versions système, variables d'env)
* Inconvénient : PostgreSQL et Airflow installés différemment sur chaque OS

### Option 4 : Nix

* Avantage : Reproductibilité totale, même plus précise que Docker
* Inconvénient : Courbe d'apprentissage très élevée
* Inconvénient : Aucune connaissance Nix dans l'équipe actuellement

## Liens

* Airflow Docker Compose officiel : https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
* Colima (alternative Docker Desktop macOS) : https://github.com/abiosoft/colima
* Rancher Desktop (alternative Docker Desktop) : https://rancherdesktop.io
```

---

## ADR-0004 — Utiliser Apache Kafka pour les événements en temps réel

```markdown
# ADR-0004 — Utiliser Apache Kafka pour la gestion des événements

* Status: accepted
* Date: 2024-02-14
* Deciders: Alice Martin, Bob Dupont, Carla Petit, Marie Laurent (PO)
* Technical Story: https://github.com/dataflow/platform/issues/35

## Contexte et énoncé du problème

La plateforme doit ingérer des événements de comportement utilisateur
(clics, paniers, commandes) depuis le site e-commerce en quasi-temps réel
pour alimenter des dashboards opérationnels (<5 minutes de latence).

Le volume estimé est de 500 événements/seconde en pic,
avec des partenaires commerciaux externes qui ont besoin
de consommer ces événements pour leurs propres systèmes,
potentiellement avec un délai (jusqu'à 24h de retard).

Un simple webhook HTTP ne suffit pas car :
1. Les partenaires peuvent être indisponibles temporairement
2. Le rejouer (replay) les événements est nécessaire en cas d'erreur
3. Plusieurs consommateurs doivent recevoir le même événement

## Facteurs de décision

* Débit : minimum 500 events/seconde en pic
* Durabilité : les événements doivent être persistés (pas de perte)
* Replay : capacité à rejouer des événements (correction d'erreurs)
* Multi-consommateurs : N consommateurs indépendants pour le même topic
* Latence : < 5 minutes end-to-end
* Compétences équipe et complexité opérationnelle

## Options considérées

* Apache Kafka
* RabbitMQ
* AWS SQS / SNS (ou équivalent cloud)
* PostgreSQL LISTEN/NOTIFY + pg_notify

## Résultat de la décision

Option retenue : **Apache Kafka**, car c'est la seule option qui répond
simultanément au besoin de replay, de multi-consommateurs indépendants
et du débit requis, malgré une complexité opérationnelle plus élevée.

### Conséquences positives

* Rétention configurable des messages (replay sur 7 jours par défaut)
* Multi-consommateurs : chaque consommateur a son propre offset
* Débit horizontal (partitions) — peut scaler à des millions d'events/s
* Ecosystem riche : Kafka Streams, ksqlDB, Kafka Connect
* Standard de l'industrie data streaming

### Conséquences négatives

* Complexité opérationnelle importante (ZooKeeper/KRaft, réplication, offset)
* Ressources requises : minimum 3 brokers en production (HA)
* Courbe d'apprentissage : concepts partitions, offsets, consumer groups
* Alternative managée recommandée en production : Confluent Cloud ou MSK
  pour réduire la charge opérationnelle

## Analyse des options

### Option 1 : Apache Kafka

* Avantage : Replay natif (rétention configurable)
* Avantage : Consumer groups indépendants (multi-consommateurs)
* Avantage : Débit très élevé (millions d'events/s avec partitions)
* Inconvénient : Complexité opérationnelle (ZooKeeper, réplication)
* Inconvénient : Over-engineering pour de faibles volumes

### Option 2 : RabbitMQ

* Avantage : Plus simple à opérer que Kafka
* Avantage : Protocols multiples (AMQP, STOMP, MQTT)
* Inconvénient : Pas de replay natif (messages supprimés après consommation)
* Inconvénient : Scaling horizontal plus limité
* Inconvénient : Pas adapté au multi-consommateurs indépendants

### Option 3 : AWS SQS / SNS

* Avantage : Managé, pas d'infrastructure à gérer
* Avantage : SQS + SNS fan-out pour le multi-consommateurs
* Inconvénient : Lock-in AWS
* Inconvénient : Replay limité (max 14 jours SQS, pas de replay sur offset)
* Inconvénient : Coût à l'usage (imprévisible en cas de pic)

### Option 4 : PostgreSQL LISTEN/NOTIFY

* Avantage : Aucune infrastructure supplémentaire
* Avantage : Déjà en place (PostgreSQL est notre BDD principale)
* Inconvénient : Pas de persistance des messages — si le consommateur
  est hors ligne, les événements sont perdus
* Inconvénient : Débit limité par PostgreSQL (~10k events/s max)
* Inconvénient : Pas de replay

## Liens

* Kafka documentation : https://kafka.apache.org/documentation/
* Confluent Cloud (Kafka managé) : https://www.confluent.io
* Module Kafka de cette formation : [../../Kafka/README.md]
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La liste des ADRs dans un dépôt GitHub (dossier `docs/adr/`) affichant les 4 fichiers ci-dessus, puis ouvrir l'ADR-0004 Kafka et faire défiler pour montrer les sections.
> **Expliquer :** Comment la numérotation séquentielle permet de retrouver l'ordre chronologique des décisions, comment les liens entre ADRs créent une traçabilité (ADR-0001 référençant un futur ADR-0011), et comment le statut "accepted" est visible immédiatement en haut du document.

---

## Observations sur ces exemples

### Ce qu'on remarque

1. **Chaque ADR documente des alternatives réelles.** PostgreSQL n'était pas le seul candidat — on a comparé avec MySQL, ClickHouse et DuckDB.

2. **Les conséquences négatives sont honnêtes.** PostgreSQL a des limites pour l'OLAP >500 GB. Kafka est complexe à opérer. L'ADR le dit clairement.

3. **Le contexte est quantifié quand possible.** "50 GB initial, 500k req/jour prévus" est plus utile que "le système doit être scalable".

4. **Les ADRs se referencent entre eux.** ADR-0001 anticipe qu'un ADR-0011 pourrait réviser la décision si le volume dépasse 500 GB.

5. **Les "Deciders" sont listés.** En cas de question, on sait qui contacter.
