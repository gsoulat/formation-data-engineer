# Produire des messages en Python

## La bibliothèque confluent-kafka

Il existe deux bibliothèques Python populaires pour Kafka :

| Bibliothèque       | Avantages                                         | Inconvénients                        |
|--------------------|---------------------------------------------------|--------------------------------------|
| `kafka-python`     | Pure Python, facile à installer                   | Performances limitées, moins maintenu|
| `confluent-kafka`  | Wrapping de `librdkafka` (C), très performante    | Nécessite librdkafka                 |

Nous utilisons **`confluent-kafka`** — c'est la bibliothèque recommandée pour la production. Elle est développée et maintenue par Confluent (l'entreprise fondée par les créateurs de Kafka).

```bash
pip install confluent-kafka
```

---

## Premier producteur : "Hello Kafka"

```python
# hello_producer.py
from confluent_kafka import Producer

# Configuration du producteur
config = {
    'bootstrap.servers': 'localhost:9092',  # Adresse du broker
}

# Créer le producteur
producer = Producer(config)

def delivery_callback(err, msg):
    """Callback appelé après chaque envoi (succès ou échec)."""
    if err:
        print(f"Erreur de livraison : {err}")
    else:
        print(
            f"Message livré → topic={msg.topic()}, "
            f"partition={msg.partition()}, "
            f"offset={msg.offset()}"
        )

# Envoyer un message
producer.produce(
    topic='hello-kafka',
    value='Bonjour depuis Python !',
    callback=delivery_callback
)

# IMPORTANT : flush() attend que tous les messages soient envoyés
producer.flush()
```

```bash
python hello_producer.py
# Message livré → topic=hello-kafka, partition=0, offset=0
```

> **Note :** Kafka crée automatiquement le topic `hello-kafka` si `auto.create.topics.enable=true` (activé dans notre docker-compose).

---

## Sérialisation des messages

Kafka transmet des **bytes** — il ne connaît pas le format de vos données. La sérialisation est votre responsabilité.

### JSON (le plus courant)

```python
# json_producer.py
import json
import uuid
from datetime import datetime
from confluent_kafka import Producer

config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(config)

def send_event(topic: str, key: str, payload: dict) -> None:
    """Sérialise et envoie un événement JSON."""
    producer.produce(
        topic=topic,
        key=key.encode('utf-8'),              # La clé doit aussi être bytes
        value=json.dumps(payload).encode('utf-8'),
        callback=lambda err, msg: (
            print(f"Erreur : {err}") if err
            else print(f"Envoyé offset={msg.offset()}")
        )
    )

# Exemple : événements e-commerce
events = [
    {
        "event_id": str(uuid.uuid4()),
        "event_type": "order.created",
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": "cust-42",
        "order": {
            "id": "ord-1001",
            "items": [
                {"product_id": "prod-123", "quantity": 2, "price": 29.99}
            ],
            "total": 59.98
        }
    },
    {
        "event_id": str(uuid.uuid4()),
        "event_type": "order.created",
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": "cust-13",
        "order": {
            "id": "ord-1002",
            "items": [
                {"product_id": "prod-456", "quantity": 1, "price": 149.00}
            ],
            "total": 149.00
        }
    }
]

for event in events:
    # La clé = customer_id → garantit l'ordre par client
    send_event("orders.created", event["customer_id"], event)

producer.flush()
print(f"{len(events)} événements envoyés.")
```

---

## Producteur avec configuration avancée

```python
# robust_producer.py
from confluent_kafka import Producer, KafkaException
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaEventProducer:
    """Producteur Kafka robuste avec configuration production-ready."""

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.config = {
            'bootstrap.servers': bootstrap_servers,

            # Fiabilité : attendre la confirmation de toutes les ISR
            'acks': 'all',

            # Retries automatiques en cas d'erreur réseau
            'retries': 5,
            'retry.backoff.ms': 300,

            # Idempotence : évite les doublons en cas de retry
            'enable.idempotence': True,

            # Performance : grouper les messages avant envoi
            'batch.size': 32768,        # 32 Ko
            'linger.ms': 10,            # Attendre 10ms pour remplir le batch

            # Compression (réduit la bande passante de 60-80%)
            'compression.type': 'snappy',

            # Timeout
            'delivery.timeout.ms': 30000,
            'request.timeout.ms': 10000,

            # Logs côté librdkafka
            'log_level': 3,
        }
        self._producer = Producer(self.config)
        self._pending = 0

    def _on_delivery(self, err, msg):
        """Callback appelé pour chaque message après tentative d'envoi."""
        self._pending -= 1
        if err:
            logger.error(
                f"Échec livraison | topic={msg.topic()} | "
                f"partition={msg.partition()} | erreur={err}"
            )
        else:
            logger.debug(
                f"Message livré | topic={msg.topic()} | "
                f"partition={msg.partition()} | offset={msg.offset()}"
            )

    def send(self, topic: str, value: dict, key: str = None) -> None:
        """
        Envoie un message JSON dans un topic Kafka.

        Args:
            topic: Nom du topic cible
            value: Dictionnaire à sérialiser en JSON
            key: Clé de partition (optionnelle)
        """
        # Sérialisation JSON → bytes
        value_bytes = json.dumps(value, ensure_ascii=False).encode('utf-8')
        key_bytes = key.encode('utf-8') if key else None

        try:
            # poll(0) traite les callbacks en attente sans bloquer
            self._producer.poll(0)

            self._producer.produce(
                topic=topic,
                key=key_bytes,
                value=value_bytes,
                callback=self._on_delivery
            )
            self._pending += 1

        except KafkaException as e:
            logger.error(f"Impossible d'envoyer le message : {e}")
            raise

    def flush(self, timeout: float = 30.0) -> None:
        """Attend que tous les messages en attente soient livrés."""
        remaining = self._producer.flush(timeout)
        if remaining > 0:
            logger.warning(f"{remaining} messages non livrés après flush()")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garantit le flush même en cas d'exception."""
        self.flush()


# Utilisation
if __name__ == '__main__':
    with KafkaEventProducer() as producer:
        # Envoyer 100 commandes simulées
        for i in range(100):
            producer.send(
                topic='orders.created',
                key=f'customer-{i % 10}',   # 10 clients différents
                value={
                    'order_id': f'ORD-{i:04d}',
                    'customer_id': f'customer-{i % 10}',
                    'amount': round(10 + i * 1.5, 2),
                    'status': 'pending'
                }
            )
        # flush() automatique grâce au context manager
    print("100 commandes envoyées avec succès.")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter `robust_producer.py` dans le terminal, puis dans Kafka UI (http://localhost:8080) naviguer vers le topic `orders.created` et afficher les messages reçus avec leur clé, valeur, partition et offset.
> **Expliquer :** Montrer comment les messages avec la même clé (`customer-0`, `customer-1`, etc.) se retrouvent tous dans la même partition. Cliquer sur un message pour afficher le JSON décodé. Montrer le compteur de messages par partition.

---

## Produire des messages en masse (high-throughput)

Pour des charges élevées, il ne faut pas appeler `flush()` après chaque message :

```python
# batch_producer.py
from confluent_kafka import Producer
import json
import time

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': '1',               # Seulement le leader confirme (plus rapide)
    'batch.size': 65536,       # 64 Ko par batch
    'linger.ms': 50,           # Attendre jusqu'à 50ms pour remplir un batch
    'compression.type': 'lz4', # LZ4 : meilleur ratio vitesse/compression
    'queue.buffering.max.messages': 100000,
})

def generate_sensor_events(n: int):
    """Génère n événements de capteurs IoT."""
    import random
    sensors = [f"sensor-{i:03d}" for i in range(10)]
    for _ in range(n):
        yield {
            'sensor_id': random.choice(sensors),
            'temperature': round(random.uniform(18.0, 35.0), 1),
            'humidity': round(random.uniform(40.0, 90.0), 1),
            'timestamp': time.time()
        }

# Envoyer 10 000 événements
start = time.time()
count = 0

for event in generate_sensor_events(10_000):
    # poll() traite les callbacks sans bloquer — évite de saturer le buffer
    producer.poll(0)

    producer.produce(
        topic='sensor.readings',
        key=event['sensor_id'],
        value=json.dumps(event).encode('utf-8')
    )
    count += 1

# Un seul flush() à la fin
producer.flush()

elapsed = time.time() - start
print(f"{count} messages envoyés en {elapsed:.2f}s ({count/elapsed:.0f} msg/s)")
```

---

## Gestion des erreurs et retry

```python
# error_handling_producer.py
from confluent_kafka import Producer, KafkaException, KafkaError
import json
import time
import logging

logger = logging.getLogger(__name__)

def send_with_retry(
    producer: Producer,
    topic: str,
    key: str,
    value: dict,
    max_retries: int = 3,
    backoff_ms: int = 500
) -> bool:
    """
    Envoie un message avec retry manuel.
    Retourne True si succès, False sinon.
    """
    value_bytes = json.dumps(value).encode('utf-8')
    delivered = [False]
    error_holder = [None]

    def callback(err, msg):
        if err:
            error_holder[0] = err
        else:
            delivered[0] = True

    for attempt in range(max_retries):
        try:
            producer.produce(
                topic=topic,
                key=key.encode('utf-8'),
                value=value_bytes,
                callback=callback
            )
            producer.flush(timeout=5.0)

            if delivered[0]:
                return True

            if error_holder[0]:
                # Erreur non-retriable (ex: topic inconnu, message trop grand)
                if error_holder[0].code() in (
                    KafkaError.MSG_SIZE_TOO_LARGE,
                    KafkaError.UNKNOWN_TOPIC_OR_PART
                ):
                    logger.error(f"Erreur non-retriable : {error_holder[0]}")
                    return False

                # Erreur retriable
                logger.warning(
                    f"Tentative {attempt+1}/{max_retries} échouée : "
                    f"{error_holder[0]}. Retry dans {backoff_ms}ms..."
                )
                time.sleep(backoff_ms / 1000)
                error_holder[0] = None

        except KafkaException as e:
            logger.error(f"Exception Kafka : {e}")
            if attempt < max_retries - 1:
                time.sleep(backoff_ms / 1000)

    logger.error(f"Échec après {max_retries} tentatives.")
    return False


# Dead Letter Queue (DLQ) — messages non livrables
def send_to_dlq(producer: Producer, original_msg: dict, error: str):
    """Envoie un message en échec vers une Dead Letter Queue."""
    dlq_message = {
        'original_message': original_msg,
        'error': error,
        'failed_at': time.time()
    }
    producer.produce(
        topic='orders.created.dlq',
        value=json.dumps(dlq_message).encode('utf-8')
    )
    producer.flush()
    logger.warning(f"Message envoyé en DLQ : {dlq_message}")
```

---

## Résumé des bonnes pratiques

| Pratique                      | Configuration                                           | Pourquoi                              |
|-------------------------------|---------------------------------------------------------|---------------------------------------|
| Fiabilité maximale            | `acks=all` + `enable.idempotence=True`                  | Évite les pertes et doublons          |
| Performance                   | `batch.size=65536` + `linger.ms=20`                     | Réduit le nombre d'I/O réseau         |
| Compression                   | `compression.type=snappy` ou `lz4`                      | Réduit la bande passante de ~70%      |
| Clé de partition              | Utiliser un identifiant métier (`customer_id`, `user_id`)| Garantit l'ordre par entité           |
| Context manager               | `with KafkaEventProducer() as p:`                       | Garantit le flush même si exception   |
| Dead Letter Queue             | Topic séparé pour les messages en échec                 | Traçabilité des erreurs               |
| Monitoring                    | Suivre le lag des consommateurs                         | Détecter un producteur trop rapide    |

---

**Module suivant :** [02-consumer-python.md](./02-consumer-python.md) — Consommer des messages
