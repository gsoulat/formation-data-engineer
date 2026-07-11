# Architecture Apache Kafka

## Vue d'ensemble

L'architecture de Kafka repose sur quelques concepts fondamentaux qu'il est essentiel de maîtriser avant d'écrire la moindre ligne de code. Ce module les présente dans l'ordre logique de leur interdépendance.

```
┌─────────────────────────────────────────────────────────────────┐
│                         KAFKA CLUSTER                           │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │ Broker 1 │    │ Broker 2 │    │ Broker 3 │                  │
│  │          │    │          │    │          │                  │
│  │ Topic A  │    │ Topic A  │    │ Topic A  │                  │
│  │ Part. 0  │    │ Part. 1  │    │ Part. 2  │                  │
│  │ (Leader) │    │ (Leader) │    │ (Leader) │                  │
│  └──────────┘    └──────────┘    └──────────┘                  │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │           ZooKeeper / KRaft             │                   │
│  │        (Coordination du cluster)        │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
         ↑                              ↓
   [Producers]                    [Consumers]
   (publient)                     (consomment)
```

---

## Les Brokers

Un **broker** est un serveur Kafka. C'est lui qui :
- Reçoit les messages des producteurs
- Stocke les messages sur disque
- Sert les messages aux consommateurs

### Cluster Kafka

Un **cluster** est un ensemble de brokers qui travaillent ensemble. En production, on déploie généralement **3 brokers minimum** pour garantir la haute disponibilité.

Chaque broker a un **identifiant unique** (broker ID). Un broker peut gérer des centaines de milliers de partitions et traiter des millions de messages par seconde.

```
Cluster de 3 brokers :

Broker 1 (ID: 1)  ←→  Broker 2 (ID: 2)  ←→  Broker 3 (ID: 3)
     ↕                      ↕                      ↕
  Partitions            Partitions              Partitions
  du topic A            du topic A              du topic A
  (Leader P0)           (Leader P1)             (Leader P2)
  (Replica P1)          (Replica P2)            (Replica P0)
```

---

## ZooKeeper et KRaft

### ZooKeeper (mode legacy)

Historiquement, Kafka utilisait **Apache ZooKeeper** pour :
- Maintenir la liste des brokers actifs
- Gérer l'élection du controller (broker coordinateur)
- Stocker la configuration des topics
- Suivre les offsets des consommateurs (ancienne méthode)

### KRaft (Kafka Raft — mode moderne)

Depuis Kafka 2.8+ (production depuis 3.3), Kafka peut fonctionner **sans ZooKeeper** grâce au mode **KRaft**. Les métadonnées sont gérées en interne via le protocole Raft.

```
Mode KRaft (recommandé) :
┌────────────────────────────────────┐
│           KAFKA CLUSTER            │
│                                    │
│  ┌────────┐  ┌────────┐  ┌──────┐ │
│  │Broker 1│  │Broker 2│  │Broker│ │
│  │+KRaft  │  │+KRaft  │  │  3   │ │
│  │(voter) │  │(voter) │  │+KRaft│ │
│  └────────┘  └────────┘  └──────┘ │
│                                    │
│  Pas besoin de ZooKeeper !         │
└────────────────────────────────────┘
```

Dans ce cours, nous utilisons **KRaft** via Docker (plus simple à déployer).

---

## Topics

Un **topic** est une **catégorie ou un flux de messages** nommé. C'est l'unité logique de stockage dans Kafka.

Analogies :
- Un topic ~ une **table** en base de données (mais append-only)
- Un topic ~ un **dossier** dans un système de fichiers
- Un topic ~ un **canal** Slack (mais persistant)

### Nommage des topics

Par convention, les topics sont nommés avec des tirets ou underscores :

```
orders.created
orders.processed
payments.failed
user-activity-logs
sensor-data-temperature
```

### Création d'un topic

```bash
# Via la CLI Kafka
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic orders.created \
  --partitions 3 \
  --replication-factor 3

# Lister les topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Décrire un topic
kafka-topics.sh --describe \
  --bootstrap-server localhost:9092 \
  --topic orders.created
```

---

## Partitions

Chaque topic est divisé en **partitions**. Une partition est un **log ordonné et immuable** de messages.

```
Topic "orders.created" avec 3 partitions :

Partition 0:  [M0] [M3] [M6] [M9]  ←
Partition 1:  [M1] [M4] [M7] [M10] ←  nouveaux messages
Partition 2:  [M2] [M5] [M8] [M11] ←
```

### Pourquoi partitionner ?

1. **Scalabilité** : les partitions peuvent être réparties sur plusieurs brokers
2. **Parallélisme** : plusieurs consommateurs peuvent lire en parallèle
3. **Débit** : plus de partitions = plus de débit potentiel

### Ordre des messages

L'ordre est **garanti au sein d'une partition**, mais **pas entre partitions**.

```
Besoin d'ordre strict pour les commandes d'un même client ?
→ Utiliser order_id comme clé de partition
→ Toutes les commandes du même client iront dans la même partition
→ L'ordre sera garanti pour ce client
```

### Clé de partition (Partition Key)

Quand un producteur envoie un message avec une **clé** :
- Kafka applique `hash(clé) % nb_partitions` pour choisir la partition
- Tous les messages avec la même clé arrivent dans la même partition
- Garantit l'ordre pour une entité donnée (ex: un client, un appareil IoT)

```python
# Message avec clé → toujours dans la même partition
producer.produce(
    topic="orders.created",
    key="customer-42",        # tous les events du client 42 → même partition
    value={"order_id": 1001}
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans Kafka UI (http://localhost:8080), naviguer vers un topic et afficher l'onglet "Partitions". Montrer la distribution des messages par partition et les offsets.
> **Expliquer :** Montrer à voix haute comment les messages avec la même clé atterrissent toujours dans la même partition. Créer un topic avec 3 partitions et envoyer des messages avec des clés différentes pour visualiser la distribution.

---

## Offsets

Un **offset** est un **numéro de séquence unique** attribué à chaque message dans une partition. Les offsets sont :
- Immutables (jamais modifiés)
- Croissants (toujours +1)
- Spécifiques à une partition (offset 5 de la partition 0 ≠ offset 5 de la partition 1)

```
Partition 0:
┌─────┬─────┬─────┬─────┬─────┬─────┐
│  0  │  1  │  2  │  3  │  4  │  5  │
│ M0  │ M1  │ M2  │ M3  │ M4  │ M5  │
└─────┴─────┴─────┴─────┴─────┴─────┘
  ↑                          ↑
Consumer A                Consumer B
(offset: 0)               (offset: 5)
```

### Rétention des messages

Kafka ne supprime pas les messages immédiatement. La rétention est configurable :

```
# Par temps (défaut : 7 jours)
log.retention.hours=168

# Par taille
log.retention.bytes=1073741824  # 1 Go par partition

# Les deux (la condition remplie en premier s'applique)
```

### Rejouer des événements

Grâce aux offsets, on peut **rejouer** tous les événements depuis n'importe quel point :

```python
# Reprendre depuis le début du topic
consumer.seek_to_beginning()

# Reprendre depuis un offset spécifique
consumer.seek(TopicPartition("orders", 0), offset=42)
```

---

## Réplication

### Facteur de réplication

Chaque partition peut être **répliquée** sur plusieurs brokers. Le **facteur de réplication** (replication factor) indique combien de copies existent.

```
Topic "orders" avec replication-factor=3, 2 partitions :

Broker 1: Partition 0 (LEADER) | Partition 1 (Follower)
Broker 2: Partition 0 (Follower) | Partition 1 (LEADER)
Broker 3: Partition 0 (Follower) | Partition 1 (Follower)
```

### Leader et Followers

Pour chaque partition :
- Un seul broker est le **Leader** — il reçoit toutes les écritures et lectures
- Les autres brokers sont des **Followers** — ils répliquent les données du Leader
- Si le Leader tombe, Kafka élit automatiquement un nouveau Leader parmi les Followers

### ISR (In-Sync Replicas)

Les **ISR** sont les répliques qui sont **à jour** par rapport au Leader. Kafka garantit qu'un message n'est considéré comme "commité" que lorsqu'il a été répliqué sur **toutes les ISR**.

```
min.insync.replicas=2 (recommandé pour replication-factor=3)
→ Le message est commité seulement si au moins 2 répliques l'ont reçu
→ Garantit la durabilité même si 1 broker tombe
```

---

## Producers (Producteurs)

Un **producteur** est une application qui **publie des messages** dans un topic Kafka.

### Fonctionnement

```
[Producer]
    |
    ├── Sérialise la clé et la valeur
    ├── Choisit la partition (via clé ou round-robin)
    ├── Envoie au broker Leader de cette partition
    └── Gère les retries en cas d'erreur
```

### Paramètres importants

| Paramètre    | Valeur   | Description                                                  |
|--------------|----------|--------------------------------------------------------------|
| `acks`       | `0`      | Fire and forget — pas de confirmation (risque de perte)      |
| `acks`       | `1`      | Confirmation du Leader seulement (défaut)                    |
| `acks`       | `all`    | Confirmation de toutes les ISR (le plus sûr)                 |
| `retries`    | `3`      | Nombre de tentatives en cas d'échec                          |
| `batch.size` | `16384`  | Taille max d'un batch avant envoi (en octets)                |
| `linger.ms`  | `5`      | Délai d'attente avant d'envoyer un batch (optimise le débit) |

---

## Consumers (Consommateurs)

Un **consommateur** est une application qui **lit des messages** depuis un topic Kafka.

### Consumer Groups

Un **consumer group** est un ensemble de consommateurs qui **coopèrent** pour consommer un topic. Chaque partition n'est assignée qu'à **un seul consommateur** du groupe à la fois.

```
Topic "orders" avec 3 partitions :

Consumer Group A :
  Consumer A1 ← Partition 0
  Consumer A2 ← Partition 1
  Consumer A3 ← Partition 2

Consumer Group B (indépendant) :
  Consumer B1 ← Partition 0 + Partition 1
  Consumer B2 ← Partition 2
```

### Règles des consumer groups

1. **1 partition → 1 seul consommateur** dans un groupe (pas de doublon)
2. **1 consommateur peut lire plusieurs partitions** si le groupe est plus petit
3. **Si le groupe > partitions** : certains consommateurs seront inactifs
4. **Plusieurs groupes** peuvent lire le même topic indépendamment

```
Optimal (3 partitions, 3 consumers):
  C1 ← P0 | C2 ← P1 | C3 ← P2  ✅

Sous-optimal (3 partitions, 2 consumers):
  C1 ← P0 + P1 | C2 ← P2  ⚠️ (C1 surchargé)

Gaspillage (3 partitions, 4 consumers):
  C1 ← P0 | C2 ← P1 | C3 ← P2 | C4 ← (rien)  ❌
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans Kafka UI, afficher l'onglet "Consumer Groups". Montrer un groupe actif avec la liste des membres, les partitions assignées et le lag (retard) de chaque consommateur.
> **Expliquer :** Expliquer le concept de "lag" : c'est la différence entre le dernier offset produit et le dernier offset commité par le consommateur. Un lag élevé = le consommateur est en retard. C'est un KPI critique à surveiller en production.

---

## Commits d'offsets

### Qu'est-ce que commiter un offset ?

Quand un consommateur lit un message, il doit **commiter son offset** — informer Kafka de sa position de lecture. Kafka stocke ces offsets dans un topic interne `__consumer_offsets`.

```
[Consumer lit message à l'offset 42]
      ↓
[Commit offset 43 (prochain à lire)]
      ↓
[Kafka stocke: group=my-app, topic=orders, partition=0, offset=43]
```

### Auto-commit vs manuel

**Auto-commit** (`enable.auto.commit=true`) :
- Kafka commite automatiquement l'offset toutes les N secondes
- Simple mais risque de perte de messages si le consumer crash entre la lecture et le commit

**Manuel** (`enable.auto.commit=false`) :
- Le développeur contrôle exactement quand commiter
- Garantit le traitement au moins une fois (at-least-once)
- Plus complexe mais plus fiable

```python
# Auto-commit (simple, moins fiable)
consumer = Consumer({'enable.auto.commit': True, 'auto.commit.interval.ms': 5000})

# Manuel (recommandé en production)
consumer = Consumer({'enable.auto.commit': False})
msg = consumer.poll()
process(msg)  # traitement
consumer.commit()  # commit seulement après traitement réussi
```

---

## Sémantiques de livraison

| Sémantique          | Description                             | Configuration                    |
|---------------------|-----------------------------------------|----------------------------------|
| At-most-once        | Peut perdre des messages, jamais de doublon | Auto-commit avant traitement |
| At-least-once       | Jamais de perte, peut avoir des doublons | Commit manuel après traitement   |
| Exactly-once        | Ni perte ni doublon                     | Transactions Kafka (complexe)    |

En pratique, **at-least-once** avec idempotence côté consommateur est le compromis le plus courant.

---

## Récapitulatif des concepts

```
CLUSTER
└── BROKERS (serveurs)
    └── TOPICS (flux de données nommés)
        └── PARTITIONS (logs ordonnés)
            └── MESSAGES (avec offset + clé + valeur + timestamp)

PRODUCERS → publient dans des TOPICS
CONSUMERS → lisent depuis des TOPICS (via CONSUMER GROUPS)
OFFSETS → position de lecture dans une PARTITION
REPLICATION → copies des partitions sur plusieurs BROKERS
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dessiner ou afficher un schéma du cluster complet (brokers, partitions, leaders/followers, producers, consumers) sur le tableau ou à l'écran.
> **Expliquer :** Parcourir le cycle de vie complet d'un message : depuis la production par le producer, le choix de la partition, la réplication sur les brokers, jusqu'à la consommation par un consumer group. Insister sur ce qui se passe quand un broker tombe.

---

**Module suivant :** [03-installation.md](./03-installation.md) — Mise en place de l'environnement Docker
