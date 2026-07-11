# Change Data Capture (CDC) avec Debezium

## Qu'est-ce que le CDC ?

Le **Change Data Capture** (CDC) est une technique qui consiste à **capturer en temps réel les changements** effectués dans une base de données (INSERT, UPDATE, DELETE) et à les propager comme des événements.

### Le problème sans CDC

Dans une architecture microservices, plusieurs services ont besoin d'être notifiés quand les données changent dans une base :

```
Problème classique :

[Service Commandes]
    ↓
[PostgreSQL orders]  ← Comment notifier les autres services ?

Option 1 : Dual write (écrire en BDD ET dans Kafka)
    ❌ Risque d'incohérence si l'une des deux écritures échoue

Option 2 : Polling (vérifier toutes les X secondes si des données ont changé)
    ❌ Latence, charge inutile sur la BDD

Option 3 : CDC avec Debezium ✅
    ✅ Lit le WAL (Write-Ahead Log) de la BDD → atomique, fiable, zéro latence
```

### Le principe du CDC

```
[PostgreSQL]
    │
    ├── Écriture normale dans la table orders
    │
    └── Write-Ahead Log (WAL)  ← journal de toutes les opérations SQL
         │
         └── [Debezium Connector]  ← lit le WAL en temps réel
              │
              └── [Kafka Topic: postgres.public.orders]  ← publie les changements
                   │
                   ├── [Service Analytics]
                   ├── [Elasticsearch]
                   └── [Cache Redis]
```

---

## Debezium : présentation

**Debezium** est un framework open-source de CDC basé sur **Kafka Connect**. Il supporte :

| Base de données  | Connecteur               |
|------------------|--------------------------|
| PostgreSQL       | `debezium-connector-postgres` |
| MySQL / MariaDB  | `debezium-connector-mysql` |
| MongoDB          | `debezium-connector-mongodb` |
| Oracle           | `debezium-connector-oracle` |
| SQL Server       | `debezium-connector-sqlserver` |
| Cassandra        | `debezium-connector-cassandra` |

### Kafka Connect

Debezium s'intègre via **Kafka Connect**, un framework de connecteurs Kafka :

```
┌──────────────────────────────────────────────────────────┐
│                    Kafka Connect                         │
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────────────┐ │
│  │   Source Connectors │  │   Sink Connectors           │ │
│  │ (lire depuis BDD)  │  │ (écrire vers BDD/ES/S3...)  │ │
│  │                    │  │                             │ │
│  │ • Debezium/Postgres│  │ • Elasticsearch Sink        │ │
│  │ • Debezium/MySQL   │  │ • JDBC Sink                 │ │
│  │ • JDBC Source      │  │ • S3 Sink                   │ │
│  └────────────────────┘  └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Mise en place de l'environnement

### docker-compose.yml complet avec CDC

```yaml
# docker-compose-cdc.yml
version: '3.8'

services:

  # ─── Kafka (réutilisé depuis le module précédent) ───
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    container_name: kafka
    hostname: kafka
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"

  # ─── PostgreSQL (source CDC) ───
  postgres:
    image: postgres:15
    container_name: postgres-cdc
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    # IMPORTANT : activer le WAL pour Debezium
    command:
      - "postgres"
      - "-c"
      - "wal_level=logical"         # Nécessaire pour Debezium
      - "-c"
      - "max_replication_slots=10"  # Slots de réplication
      - "-c"
      - "max_wal_senders=10"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  # ─── Kafka Connect + Debezium ───
  kafka-connect:
    image: debezium/connect:2.5
    container_name: kafka-connect
    ports:
      - "8083:8083"  # API REST Kafka Connect
    depends_on:
      - kafka
      - postgres
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: debezium-connect-group
      CONFIG_STORAGE_TOPIC: connect-configs
      OFFSET_STORAGE_TOPIC: connect-offsets
      STATUS_STORAGE_TOPIC: connect-statuses
      CONFIG_STORAGE_REPLICATION_FACTOR: 1
      OFFSET_STORAGE_REPLICATION_FACTOR: 1
      STATUS_STORAGE_REPLICATION_FACTOR: 1
      KEY_CONVERTER: org.apache.kafka.connect.json.JsonConverter
      VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
      KEY_CONVERTER_SCHEMAS_ENABLE: "false"
      VALUE_CONVERTER_SCHEMAS_ENABLE: "false"

  # ─── Kafka UI ───
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_KAFKACONNECT_0_NAME: debezium
      KAFKA_CLUSTERS_0_KAFKACONNECT_0_ADDRESS: http://kafka-connect:8083

volumes:
  postgres_data:
```

### Script d'initialisation PostgreSQL

```sql
-- init-db.sql
-- Créer les tables de démonstration

CREATE TABLE IF NOT EXISTS customers (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    status      VARCHAR(50) DEFAULT 'PENDING',
    amount      DECIMAL(10,2) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- Insérer des données initiales
INSERT INTO customers (name, email) VALUES
    ('Alice Martin', 'alice@example.com'),
    ('Bob Dupont', 'bob@example.com'),
    ('Claire Bernard', 'claire@example.com');

INSERT INTO orders (customer_id, status, amount) VALUES
    (1, 'PENDING', 149.99),
    (2, 'CONFIRMED', 89.50),
    (1, 'SHIPPED', 299.00);
```

---

## Configurer le connecteur Debezium

### Via l'API REST de Kafka Connect

```bash
# Démarrer l'environnement
docker compose -f docker-compose-cdc.yml up -d

# Vérifier que Kafka Connect est prêt
curl http://localhost:8083/

# Lister les connecteurs disponibles (plugins)
curl http://localhost:8083/connector-plugins | python -m json.tool
```

```bash
# Créer le connecteur Debezium pour PostgreSQL
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-cdc-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",

      "database.hostname": "postgres-cdc",
      "database.port": "5432",
      "database.user": "postgres",
      "database.password": "postgres",
      "database.dbname": "ecommerce",
      "database.server.name": "ecommerce",

      "plugin.name": "pgoutput",

      "table.include.list": "public.orders,public.customers",

      "topic.prefix": "cdc",

      "transforms": "unwrap",
      "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
      "transforms.unwrap.drop.tombstones": "false",
      "transforms.unwrap.delete.handling.mode": "rewrite",
      "transforms.unwrap.add.fields": "op,table,lsn,source.ts_ms"
    }
  }'
```

```bash
# Vérifier l'état du connecteur
curl http://localhost:8083/connectors/postgres-cdc-connector/status | python -m json.tool

# Résultat attendu :
# {
#   "name": "postgres-cdc-connector",
#   "connector": {"state": "RUNNING", ...},
#   "tasks": [{"id": 0, "state": "RUNNING", ...}]
# }
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Montrer l'API REST Kafka Connect (http://localhost:8083/connectors) dans le navigateur, puis ouvrir Kafka UI et montrer les topics `cdc.public.orders` et `cdc.public.customers` qui apparaissent automatiquement après la création du connecteur.
> **Expliquer :** Expliquer que Debezium a lu le snapshot initial de PostgreSQL et publié tous les enregistrements existants comme événements `op: "r"` (read/snapshot). Les prochains changements apparaîtront en temps réel.

---

## Format des messages CDC

Après l'`ExtractNewRecordState` transform, chaque message ressemble à :

```json
{
  "id": 1,
  "customer_id": 1,
  "status": "CONFIRMED",
  "amount": "149.99",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T11:30:00Z",
  "__op": "u",
  "__table": "orders",
  "__source_ts_ms": 1705312800000,
  "__deleted": "false"
}
```

Le champ `__op` indique l'opération :
- `c` : CREATE (INSERT)
- `u` : UPDATE
- `d` : DELETE
- `r` : READ (snapshot initial)

---

## Consommer les événements CDC en Python

```python
# cdc_consumer.py
import json
from confluent_kafka import Consumer
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CDCEventProcessor:
    """
    Consomme les événements CDC depuis Kafka
    et les traite selon leur type (CREATE/UPDATE/DELETE).
    """

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'cdc-processor',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })

    def process_order_event(self, event: dict):
        """Traitement des événements sur la table orders."""
        op = event.get('__op', '?')
        order_id = event.get('id')
        status = event.get('status')
        amount = event.get('amount')
        deleted = event.get('__deleted') == 'true'

        if deleted or op == 'd':
            logger.warning(f"[DELETE] Commande supprimée : #{order_id}")
            self._handle_order_deleted(event)

        elif op == 'c':
            logger.info(
                f"[INSERT] Nouvelle commande #{order_id} | "
                f"Statut: {status} | Montant: {amount}€"
            )
            self._handle_order_created(event)

        elif op == 'u':
            logger.info(
                f"[UPDATE] Commande #{order_id} mise à jour | "
                f"Nouveau statut: {status}"
            )
            self._handle_order_updated(event)

        elif op == 'r':
            # Snapshot initial — ignorer ou traiter différemment
            logger.debug(f"[SNAPSHOT] Commande #{order_id} | Statut: {status}")

    def _handle_order_created(self, event: dict):
        """Réagir à la création d'une commande."""
        # Ex: envoyer un email de confirmation, notifier le service d'inventaire
        logger.info(f"→ Déclenchement email de confirmation pour commande #{event['id']}")

    def _handle_order_updated(self, event: dict):
        """Réagir à la mise à jour d'une commande."""
        if event.get('status') == 'SHIPPED':
            logger.info(f"→ Envoi notification d'expédition pour commande #{event['id']}")
        elif event.get('status') == 'DELIVERED':
            logger.info(f"→ Demande d'avis client pour commande #{event['id']}")
        elif event.get('status') == 'CANCELLED':
            logger.warning(f"→ Remboursement à déclencher pour commande #{event['id']}")

    def _handle_order_deleted(self, event: dict):
        """Réagir à la suppression d'une commande."""
        # RGPD : archiver avant suppression
        logger.warning(f"→ Archivage RGPD pour commande #{event['id']}")

    def process_customer_event(self, event: dict):
        """Traitement des événements sur la table customers."""
        op = event.get('__op', '?')
        customer_id = event.get('id')

        if op == 'c':
            logger.info(f"[INSERT] Nouveau client #{customer_id} : {event.get('email')}")
        elif op == 'u':
            logger.info(f"[UPDATE] Client #{customer_id} mis à jour")
        elif op == 'd' or event.get('__deleted') == 'true':
            logger.warning(f"[DELETE] Client #{customer_id} supprimé")

    def run(self):
        self.consumer.subscribe([
            'cdc.public.orders',
            'cdc.public.customers',
        ])

        logger.info("CDC Consumer démarré, en attente d'événements...")

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Erreur : {msg.error()}")
                    continue

                topic = msg.topic()
                event = json.loads(msg.value().decode('utf-8'))

                if topic == 'cdc.public.orders':
                    self.process_order_event(event)
                elif topic == 'cdc.public.customers':
                    self.process_customer_event(event)

                self.consumer.commit(asynchronous=False)

        except KeyboardInterrupt:
            logger.info("Arrêt du CDC consumer.")
        finally:
            self.consumer.close()


if __name__ == '__main__':
    processor = CDCEventProcessor()
    processor.run()
```

---

## Démonstration : changements en temps réel

```bash
# Dans un terminal : lancer le consommateur CDC
python cdc_consumer.py

# Dans un autre terminal : se connecter à PostgreSQL et faire des changements
docker exec -it postgres-cdc psql -U postgres -d ecommerce

# INSERT → déclenche un événement "c"
INSERT INTO orders (customer_id, status, amount)
VALUES (2, 'PENDING', 75.00);

# UPDATE → déclenche un événement "u"
UPDATE orders SET status = 'CONFIRMED' WHERE id = 1;
UPDATE orders SET status = 'SHIPPED' WHERE id = 1;

# DELETE → déclenche un événement "d"
DELETE FROM orders WHERE id = 4;
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Deux terminaux côte à côte : à gauche le shell PostgreSQL avec les requêtes SQL, à droite le CDC consumer Python affichant les événements en temps réel. Montrer qu'un UPDATE dans PostgreSQL apparaît dans le terminal Python en moins d'une seconde.
> **Expliquer :** C'est le pattern "Outbox" côté infrastructurel. Aucun code dans l'application n'a besoin de publier dans Kafka — c'est Debezium qui le fait automatiquement. Résultat : pas de dual-write, pas de risque d'incohérence. Montrer aussi dans Kafka UI les messages CDC avec leur structure JSON.

---

## Cas d'usage avancés

### 1. Synchronisation vers Elasticsearch

```python
# elasticsearch_sync.py
"""
Synchronise les commandes PostgreSQL vers Elasticsearch via CDC.
Chaque changement en BDD se reflète dans l'index ES en temps réel.
"""
import json
from confluent_kafka import Consumer

# Note : nécessite `pip install elasticsearch`
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])
INDEX_NAME = 'orders'

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'elasticsearch-sync',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
})
consumer.subscribe(['cdc.public.orders'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        event = json.loads(msg.value())
        order_id = str(event.get('id'))
        op = event.get('__op')
        deleted = event.get('__deleted') == 'true'

        if deleted or op == 'd':
            # Supprimer de l'index ES
            es.delete(index=INDEX_NAME, id=order_id, ignore=[404])
            print(f"[ES] Supprimé : order #{order_id}")

        else:
            # Indexer ou mettre à jour
            doc = {k: v for k, v in event.items() if not k.startswith('__')}
            es.index(index=INDEX_NAME, id=order_id, document=doc)
            print(f"[ES] Indexé : order #{order_id} | status={event.get('status')}")

        consumer.commit(asynchronous=False)

finally:
    consumer.close()
```

### 2. Invalidation de cache Redis

```python
# cache_invalidation.py
"""
Invalide automatiquement le cache Redis quand les données changent en BDD.
"""
import json
from confluent_kafka import Consumer
import redis

r = redis.Redis(host='localhost', port=6379)

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'cache-invalidator',
    'auto.offset.reset': 'latest',  # Seulement les nouveaux changements
    'enable.auto.commit': True,
})
consumer.subscribe(['cdc.public.orders', 'cdc.public.customers'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        event = json.loads(msg.value())
        topic = msg.topic()

        if 'orders' in topic:
            order_id = event.get('id')
            cache_key = f"order:{order_id}"
            r.delete(cache_key)
            print(f"[Cache] Invalidé : {cache_key}")

        elif 'customers' in topic:
            customer_id = event.get('id')
            # Invalider toutes les clés liées à ce client
            keys = r.keys(f"customer:{customer_id}:*")
            if keys:
                r.delete(*keys)
            print(f"[Cache] Invalidé : customer:{customer_id}:*")

finally:
    consumer.close()
```

---

## Bonnes pratiques CDC

| Pratique                      | Description                                                |
|-------------------------------|------------------------------------------------------------|
| Monitoring des connecteurs    | Surveiller l'état via `/connectors/{name}/status`          |
| Gestion du lag                | Monitorer le lag du consumer group Debezium                |
| Heartbeat topic               | Configurer `heartbeat.interval.ms` pour détecter les pauses|
| Snapshot initial              | Contrôler avec `snapshot.mode` (initial, never, always)    |
| Filtrage de tables            | `table.include.list` plutôt que de tout capturer           |
| Tombstone messages            | Gérer les messages de suppression (valeur null)            |
| Idempotence côté consommateur | Tolérer les doublons en cas de replay                      |

---

## Résumé

| Concept            | Description                                               |
|--------------------|-----------------------------------------------------------|
| CDC                | Capturer les changements BDD comme événements Kafka       |
| Debezium           | Framework CDC basé sur Kafka Connect                      |
| WAL                | Write-Ahead Log — journal des opérations PostgreSQL       |
| Outbox Pattern     | Alternative au CDC pour les applications existantes       |
| `__op`             | Opération CDC : `c`=create, `u`=update, `d`=delete        |
| Snapshot           | Lecture initiale de toute la table lors du démarrage      |

**Module suivant :** [Integration/01-kafka-spark.md](../Integration/01-kafka-spark.md)
