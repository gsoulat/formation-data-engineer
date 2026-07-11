# Introduction à Apache Kafka

## Qu'est-ce qu'Apache Kafka ?

Apache Kafka est une **plateforme de streaming d'événements distribuée** open-source, initialement développée par LinkedIn en 2011, puis cédée à l'Apache Software Foundation. Aujourd'hui, Kafka est utilisé par plus de 80% des entreprises du Fortune 100.

Kafka répond à un problème fondamental de l'ingénierie des données moderne : **comment transmettre, stocker et traiter des flux massifs d'événements en temps réel**, de manière fiable, scalable et durable ?

### Définition officielle

> Apache Kafka is an open-source distributed event streaming platform used for high-performance data pipelines, streaming analytics, data integration, and mission-critical applications.

En pratique, Kafka joue trois rôles simultanément :

1. **Système de messagerie** — transmet des messages entre producteurs et consommateurs
2. **Système de stockage** — persiste les événements sur disque avec durabilité garantie
3. **Moteur de traitement de flux** — permet de traiter les données au fil de leur arrivée

---

## L'event streaming : le paradigme central

### Qu'est-ce qu'un événement ?

Un **événement** (ou message) est la notification qu'il s'est passé quelque chose dans le système. Contrairement à une simple donnée statique, un événement est immuable et horodaté.

Exemples d'événements :
- `user_signed_up` — un utilisateur vient de créer son compte
- `order_placed` — une commande a été passée à 14h32
- `payment_failed` — un paiement a échoué
- `temperature_reading` — un capteur IoT a mesuré 23.4°C
- `page_viewed` — un utilisateur a consulté la page produit X

### L'event streaming vs le batch processing

| Caractéristique     | Batch Processing         | Event Streaming (Kafka)       |
|---------------------|--------------------------|-------------------------------|
| Latence             | Minutes à heures         | Millisecondes à secondes      |
| Traitement          | Fichiers en lot          | Flux continu d'événements     |
| Déclenchement       | Planifié (cron, etc.)    | Immédiat à la réception       |
| Cas d'usage         | Rapports nuiteux, ETL    | Alertes, recommandations live |
| Exemples d'outils   | Spark Batch, dbt         | Kafka, Faust, Spark Streaming |

---

## Kafka vs les systèmes de messagerie traditionnels

Avant Kafka, les entreprises utilisaient des **message queues** (files d'attente de messages) comme RabbitMQ, ActiveMQ ou IBM MQ. Kafka apporte des différences architecturales majeures.

### Tableau comparatif

| Critère                | Message Queue (RabbitMQ) | Apache Kafka                      |
|------------------------|--------------------------|-----------------------------------|
| Modèle                 | Queue (FIFO)             | Log distribué                     |
| Rétention des messages | Supprimés après lecture  | Conservés (configurable, ex. 7j)  |
| Rejouabilité           | Non                      | Oui — on peut relire l'historique |
| Scalabilité            | Verticale principalement | Horizontale par design            |
| Débit                  | Milliers/s               | Millions de messages/s            |
| Ordre garanti          | Par queue                | Par partition                     |
| Routing                | Complex (exchanges)      | Simple (topics + partitions)      |
| Consommateurs          | Compétitifs              | Groupes indépendants              |

### Le concept de "log distribué"

Dans Kafka, chaque **topic** est un **log append-only** : les messages sont toujours ajoutés à la fin, jamais modifiés ou supprimés immédiatement. Chaque message a un **offset** (position dans le log).

```
Position :  0    1    2    3    4    5    6    ...
           [M0] [M1] [M2] [M3] [M4] [M5] [M6] ← nouveaux messages
            ↑
         Consumer A lit depuis l'offset 0
                              ↑
                         Consumer B lit depuis l'offset 4
```

Ce modèle permet à **plusieurs consommateurs indépendants** de lire le même topic à leur propre rythme, et de rejouer des événements passés si nécessaire.

---

## Cas d'usage principaux

### 1. Pipeline de données en temps réel (Data Pipeline)

Kafka sert de **bus central** entre les systèmes sources et les systèmes cibles.

```
[Application web] ──┐
[Application mobile]──┤
[API externe]      ──┤──→ [Kafka] ──→ [Data Warehouse]
[Capteurs IoT]     ──┤              ──→ [Elasticsearch]
[Base de données]  ──┘              ──→ [Data Lake (S3)]
```

**Exemple concret** : Netflix ingère des milliards d'événements par jour (clics, vues, pauses) via Kafka pour alimenter ses systèmes de recommandation.

### 2. Intégration de microservices

Dans une architecture microservices, Kafka remplace les appels API synchrones par de la **communication asynchrone par événements**.

```
[Service Commandes] ──→ order.placed ──→ [Service Inventaire]
                                     ──→ [Service Facturation]
                                     ──→ [Service Notifications]
```

**Avantage** : le Service Commandes n'a pas besoin de connaître les autres services. Si le Service Notifications est en panne, l'événement est conservé et traité dès son redémarrage.

### 3. Event Sourcing

Kafka conserve **l'historique complet** des changements d'état d'une application. Au lieu de stocker l'état courant en base, on stocke chaque événement qui a modifié cet état.

```
[account.created]
[money.deposited: +100€]
[money.withdrawn: -30€]
[money.deposited: +50€]
→ Solde courant = 120€ (recalculé en rejouant les events)
```

### 4. Stream Processing (Traitement en flux)

Kafka permet de **transformer, agréger et enrichir** des données en temps réel.

```
[clics utilisateurs] ──→ [Faust/Kafka Streams] ──→ [score fraude]
[transactions]       ──→ [Faust/Kafka Streams] ──→ [alerte si seuil dépassé]
[logs applicatifs]   ──→ [Faust/Kafka Streams] ──→ [dashboard temps réel]
```

### 5. Change Data Capture (CDC)

Kafka, couplé à **Debezium**, capture automatiquement les changements dans une base de données (INSERT, UPDATE, DELETE) et les publie comme événements.

```
[PostgreSQL] ──→ [Debezium Connector] ──→ [Kafka] ──→ [Elasticsearch]
                                                    ──→ [Cache Redis]
                                                    ──→ [Analytics DB]
```

---

## Qui utilise Kafka ?

| Entreprise   | Usage                                                    |
|--------------|----------------------------------------------------------|
| LinkedIn     | Feed d'activité, métriques en temps réel (~ 7 trillions/jour) |
| Netflix       | Événements de streaming, recommandations, monitoring     |
| Uber          | Suivi GPS des chauffeurs, calcul du prix dynamique       |
| Airbnb        | Logs, analytics, détection de fraude                    |
| Twitter/X     | Timeline, notifications, analytics                      |
| Criteo        | Publicité en temps réel (bidding)                       |
| Société Générale | Transactions financières, conformité réglementaire  |

---

## Kafka dans l'écosystème data

```
                    ┌─────────────────────────────┐
                    │       APACHE KAFKA           │
                    │   (Event Streaming Platform)  │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   [Kafka Connect]      [Kafka Streams]        [ksqlDB]
   Sources & Sinks       Stream Processing    SQL sur flux
   (Debezium, S3,        (Java/Python)        (pour équipes SQL)
    JDBC, Elasticsearch)
```

Kafka est souvent au **centre** d'une architecture data moderne (Lambda ou Kappa Architecture).

---

## Points clés à retenir

- Kafka est une plateforme de **streaming d'événements**, pas une simple queue
- Les messages sont **persistés** et **rejouables** — pas supprimés après lecture
- Kafka supporte des **millions de messages par seconde** de façon native
- Plusieurs **consommateurs indépendants** peuvent lire le même topic simultanément
- Kafka est la **colonne vertébrale** des architectures microservices et data modernes

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir le site https://kafka.apache.org et montrer la page d'accueil, puis naviguer vers "Use Cases"
> **Expliquer :** Décrire à voix haute comment chaque cas d'usage listé correspond aux problèmes réels rencontrés en entreprise. Montrer le nombre de téléchargements et la liste des entreprises utilisatrices.

---

## Pour aller plus loin

- [Documentation officielle Kafka](https://kafka.apache.org/documentation/)
- [Confluent — Kafka 101 (vidéos)](https://developer.confluent.io/learn-kafka/)
- [The Log: What every software engineer should know about real-time data's unifying abstraction](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) — Jay Kreps (co-créateur de Kafka)

---

**Prochain module :** [02-architecture.md](./02-architecture.md) — Brokers, topics, partitions et consumer groups
