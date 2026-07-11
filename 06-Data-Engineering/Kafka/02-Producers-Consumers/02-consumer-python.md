# Consommer des messages en Python

## Premier consommateur

```python
# hello_consumer.py
from confluent_kafka import Consumer, KafkaException

# Configuration minimale
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'mon-premier-groupe',       # Obligatoire
    'auto.offset.reset': 'earliest',        # Lire depuis le début si pas d'offset sauvegardé
}

consumer = Consumer(config)

# S'abonner au topic
consumer.subscribe(['orders.created'])

print("Consommateur démarré, en attente de messages...")

try:
    while True:
        # poll() attend un message (timeout = 1 seconde)
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            # Pas de message dans le délai imparti
            continue

        if msg.error():
            print(f"Erreur : {msg.error()}")
            continue

        # Traitement du message
        print(
            f"Reçu | "
            f"topic={msg.topic()} | "
            f"partition={msg.partition()} | "
            f"offset={msg.offset()} | "
            f"clé={msg.key().decode('utf-8') if msg.key() else None} | "
            f"valeur={msg.value().decode('utf-8')}"
        )

except KeyboardInterrupt:
    print("\nArrêt du consommateur.")
finally:
    # IMPORTANT : toujours fermer proprement
    consumer.close()
```

---

## Consumer Groups en détail

### Concept de rebalancing

Quand des consommateurs rejoignent ou quittent un groupe, Kafka effectue un **rebalancing** : il réassigne les partitions entre les consommateurs actifs.

```
Avant rebalancing (2 consumers, 4 partitions) :
  Consumer A : P0, P1
  Consumer B : P2, P3

Un 3ème consumer rejoint → rebalancing :
  Consumer A : P0
  Consumer B : P1, P2
  Consumer C : P3

Consumer B crash → rebalancing :
  Consumer A : P0, P1
  Consumer C : P2, P3
```

### Démonstration avec plusieurs consommateurs

```python
# multi_consumer.py
import json
import threading
from confluent_kafka import Consumer

def run_consumer(consumer_id: int, group_id: str, topic: str):
    """Lance un consommateur dans un thread."""
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 1000,
    })
    consumer.subscribe([topic])

    print(f"[Consumer {consumer_id}] Démarré dans le groupe '{group_id}'")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"[Consumer {consumer_id}] Erreur : {msg.error()}")
                continue

            data = json.loads(msg.value())
            print(
                f"[Consumer {consumer_id}] "
                f"P{msg.partition()} | "
                f"offset={msg.offset()} | "
                f"order_id={data.get('order_id', '?')}"
            )

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        print(f"[Consumer {consumer_id}] Fermé.")

# Lancer 3 consommateurs dans le même groupe
threads = []
for i in range(3):
    t = threading.Thread(
        target=run_consumer,
        args=(i, 'order-processors', 'orders.created'),
        daemon=True
    )
    threads.append(t)
    t.start()

# Attendre Ctrl+C
try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    print("\nArrêt de tous les consommateurs.")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer 3 consumers dans le groupe `order-processors`, puis dans Kafka UI afficher le Consumer Group avec les 3 membres et les partitions assignées à chacun. Envoyer une série de messages et montrer leur distribution.
> **Expliquer :** Montrer que chaque message est traité par un seul consumer du groupe. Arrêter un consumer et montrer le rebalancing automatique dans Kafka UI (les partitions du consumer mort sont réassignées aux survivants).

---

## Auto-commit vs commit manuel

### Problème avec l'auto-commit

```
Timeline avec auto-commit :

t=0  Consumer lit message offset=10
t=2  Auto-commit : offset=11 sauvegardé
t=3  CRASH du consumer pendant le traitement !

Conséquence : le message offset=10 a été "marqué comme lu"
mais n'a jamais été traité → perte de message !
```

### Commit manuel : at-least-once

```python
# manual_commit_consumer.py
import json
import logging
from confluent_kafka import Consumer, TopicPartition, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReliableConsumer:
    """
    Consommateur avec commit manuel.
    Garantit le traitement at-least-once :
    - Jamais de perte de message
    - Peut y avoir des doublons si crash après traitement mais avant commit
    """

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str]
    ):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',

            # Désactiver l'auto-commit : c'est nous qui committons
            'enable.auto.commit': False,

            # Session timeout : si le consumer ne poll pas pendant ce délai,
            # Kafka considère qu'il est mort et déclenche un rebalancing
            'session.timeout.ms': 30000,

            # Heartbeat : intervalle d'envoi de "je suis vivant"
            'heartbeat.interval.ms': 3000,

            # Max de messages à lire sans commit (protection contre les loops)
            'max.poll.interval.ms': 300000,  # 5 minutes max entre deux poll()
        })
        self.consumer.subscribe(topics)

    def process_message(self, data: dict) -> bool:
        """
        Traite un message. Retourne True si succès, False sinon.
        À surcharger dans les sous-classes.
        """
        logger.info(f"Traitement : {data}")
        return True

    def run(self):
        """Boucle principale du consommateur."""
        logger.info("Démarrage du consommateur...")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # Fin de partition atteinte (pas une vraie erreur)
                        logger.debug(
                            f"Fin de partition : "
                            f"{msg.topic()}/{msg.partition()} @ {msg.offset()}"
                        )
                    else:
                        logger.error(f"Erreur Kafka : {msg.error()}")
                    continue

                # Désérialisation
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                except json.JSONDecodeError as e:
                    logger.error(f"Impossible de désérialiser le message : {e}")
                    # Message malformé → on commit quand même pour ne pas bloquer
                    self.consumer.commit(asynchronous=False)
                    continue

                # Traitement
                success = self.process_message(data)

                if success:
                    # Commit synchrone : on attend la confirmation de Kafka
                    # Plus lent mais garantit que l'offset est bien sauvegardé
                    self.consumer.commit(asynchronous=False)
                    logger.debug(
                        f"Commit offset={msg.offset()+1} "
                        f"[{msg.topic()}/{msg.partition()}]"
                    )
                else:
                    # Échec du traitement : on ne commite pas
                    # Le message sera relu après le prochain rebalancing
                    logger.warning(
                        f"Traitement échoué pour offset={msg.offset()}, "
                        f"pas de commit."
                    )

        except KeyboardInterrupt:
            logger.info("Arrêt demandé.")
        finally:
            # Commit final des offsets non committé avant fermeture
            try:
                self.consumer.commit(asynchronous=False)
            except Exception:
                pass
            self.consumer.close()
            logger.info("Consommateur fermé proprement.")


# Utilisation
class OrderProcessor(ReliableConsumer):
    """Processeur de commandes avec logique métier."""

    def process_message(self, data: dict) -> bool:
        try:
            order_id = data['order_id']
            amount = data['amount']
            customer_id = data['customer_id']

            logger.info(
                f"Commande {order_id} | Client {customer_id} | "
                f"Montant : {amount:.2f}€"
            )

            # Simuler un traitement (appel API, BDD, etc.)
            if amount > 1000:
                logger.warning(f"Commande à haut montant : {order_id}")

            return True

        except KeyError as e:
            logger.error(f"Champ manquant dans le message : {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")
            return False


if __name__ == '__main__':
    processor = OrderProcessor(
        bootstrap_servers='localhost:9092',
        group_id='order-processors-v2',
        topics=['orders.created']
    )
    processor.run()
```

---

## Commit par batch (optimisation)

Commiter après chaque message est fiable mais lent. En production, on commite après un **batch** de messages :

```python
# batch_commit_consumer.py
import json
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'batch-processor',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    # Lire jusqu'à 500 messages par poll()
    'max.poll.records': 500,
})

consumer.subscribe(['orders.created'])

BATCH_SIZE = 100  # Commiter tous les 100 messages

batch = []
try:
    while True:
        msg = consumer.poll(timeout=0.1)

        if msg and not msg.error():
            data = json.loads(msg.value())
            batch.append(data)

        # Commit quand le batch est plein ou après un timeout
        if len(batch) >= BATCH_SIZE:
            # Traiter tout le batch
            for item in batch:
                process(item)

            # Un seul commit pour tout le batch
            consumer.commit(asynchronous=True)
            print(f"Batch de {len(batch)} messages commité.")
            batch.clear()

except KeyboardInterrupt:
    pass
finally:
    consumer.commit(asynchronous=False)
    consumer.close()
```

---

## Seek : contrôler manuellement les offsets

```python
# seek_example.py
from confluent_kafka import Consumer, TopicPartition
import json

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'reprocess-group',
    'enable.auto.commit': False,
})

# S'abonner et attendre l'assignation des partitions
consumer.subscribe(['orders.created'])

# Callback de rebalancing pour effectuer le seek APRÈS l'assignation
def on_assign(consumer, partitions):
    print(f"Partitions assignées : {partitions}")

    # Rejouer depuis le début
    for p in partitions:
        p.offset = 0  # OFFSET_BEGINNING

    consumer.assign(partitions)
    print("Offsets réinitialisés au début.")

consumer.subscribe(['orders.created'], on_assign=on_assign)

# Ou seek manuel sur une partition spécifique
consumer.poll(1.0)  # Premier poll pour déclencher l'assignation

# Aller à un offset spécifique
tp = TopicPartition('orders.created', partition=0, offset=42)
consumer.seek(tp)

# Ou aller à l'offset timestamp
from confluent_kafka import TIMESTAMP_CREATE_TIME
import time

# Rejouer depuis il y a 1 heure
one_hour_ago_ms = int((time.time() - 3600) * 1000)
partitions = [
    TopicPartition('orders.created', p, one_hour_ago_ms)
    for p in range(3)
]

# offsets_for_times retourne l'offset correspondant au timestamp
offsets = consumer.offsets_for_times(partitions)
for tp in offsets:
    print(f"Partition {tp.partition} → offset {tp.offset} depuis il y a 1h")
    consumer.seek(tp)

consumer.close()
```

---

## Gestion des erreurs avancée

```python
# error_handling_consumer.py
import json
import time
from confluent_kafka import Consumer, KafkaError
from dataclasses import dataclass, field
from typing import Callable
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetryConfig:
    max_retries: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 10000
    backoff_multiplier: float = 2.0


class ConsumerWithRetry:
    """Consommateur avec retry exponentiel sur les erreurs de traitement."""

    def __init__(
        self,
        group_id: str,
        topics: list[str],
        handler: Callable[[dict], None],
        dlq_topic: str = None,
        retry_config: RetryConfig = None,
    ):
        from confluent_kafka import Producer

        self.handler = handler
        self.dlq_topic = dlq_topic
        self.retry_config = retry_config or RetryConfig()

        self.consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })
        self.consumer.subscribe(topics)

        # Producteur pour la DLQ
        if dlq_topic:
            self.dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})

    def _handle_with_retry(self, data: dict) -> bool:
        """Tente de traiter un message avec retry exponentiel."""
        backoff_ms = self.retry_config.initial_backoff_ms

        for attempt in range(self.retry_config.max_retries):
            try:
                self.handler(data)
                return True
            except Exception as e:
                if attempt < self.retry_config.max_retries - 1:
                    logger.warning(
                        f"Tentative {attempt+1} échouée : {e}. "
                        f"Retry dans {backoff_ms}ms..."
                    )
                    time.sleep(backoff_ms / 1000)
                    backoff_ms = min(
                        backoff_ms * self.retry_config.backoff_multiplier,
                        self.retry_config.max_backoff_ms
                    )
                else:
                    logger.error(
                        f"Toutes les tentatives ont échoué pour : {data}. "
                        f"Dernière erreur : {e}"
                    )
                    self._send_to_dlq(data, str(e))
        return False

    def _send_to_dlq(self, data: dict, error: str):
        """Envoie un message vers la Dead Letter Queue."""
        if not self.dlq_topic or not hasattr(self, 'dlq_producer'):
            return

        dlq_payload = {
            'original_message': data,
            'error': error,
            'failed_at': time.time(),
        }
        self.dlq_producer.produce(
            topic=self.dlq_topic,
            value=json.dumps(dlq_payload).encode('utf-8')
        )
        self.dlq_producer.flush()
        logger.info(f"Message envoyé en DLQ : {self.dlq_topic}")

    def run(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Erreur broker : {msg.error()}")
                    continue

                try:
                    data = json.loads(msg.value().decode('utf-8'))
                except json.JSONDecodeError:
                    logger.error("Message non désérialisable → DLQ")
                    self._send_to_dlq({}, "JSON invalide")
                    self.consumer.commit(asynchronous=False)
                    continue

                success = self._handle_with_retry(data)
                # Commiter même en cas d'échec (après envoi en DLQ)
                self.consumer.commit(asynchronous=False)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.commit(asynchronous=False)
            self.consumer.close()


# Utilisation
def process_order(order: dict):
    """Handler métier — peut lever des exceptions."""
    if order.get('amount', 0) < 0:
        raise ValueError(f"Montant négatif : {order['amount']}")
    logger.info(f"Commande traitée : {order['order_id']}")


runner = ConsumerWithRetry(
    group_id='robust-order-processor',
    topics=['orders.created'],
    handler=process_order,
    dlq_topic='orders.created.dlq',
    retry_config=RetryConfig(max_retries=3, initial_backoff_ms=200),
)
runner.run()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant le consommateur recevoir des messages en temps réel avec les logs de commit. Dans un autre terminal, produire des messages et montrer le lag descendre à 0 dans Kafka UI.
> **Expliquer :** Ouvrir Kafka UI > Consumer Groups > votre groupe > afficher le lag par partition. Expliquer que le lag est le KPI le plus important pour monitorer un pipeline Kafka. Montrer ce qui se passe quand le consommateur est arrêté : le lag monte, puis redescend à la reprise.

---

## Résumé

| Concept                  | Description                                              |
|--------------------------|----------------------------------------------------------|
| `group.id`               | Identifiant du consumer group (obligatoire)              |
| `auto.offset.reset`      | `earliest` (début) ou `latest` (nouveaux seulement)      |
| `enable.auto.commit`     | `False` recommandé pour la fiabilité                     |
| `consumer.commit()`      | Commit synchrone (lent mais sûr)                         |
| `consumer.commit(async)` | Commit asynchrone (rapide, léger risque de doublon)      |
| `consumer.seek()`        | Repositionner l'offset manuellement                      |
| Rebalancing              | Réassignation automatique des partitions                 |
| DLQ                      | Topic séparé pour les messages non traitables            |

**Module suivant :** [03-avro-schema-registry.md](./03-avro-schema-registry.md) — Sérialisation Avro
