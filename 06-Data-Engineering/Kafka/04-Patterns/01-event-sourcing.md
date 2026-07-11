# Event Sourcing avec Apache Kafka

## Qu'est-ce que l'Event Sourcing ?

L'**Event Sourcing** est un pattern d'architecture qui consiste à **stocker l'état d'une application sous la forme d'une séquence d'événements** plutôt que de stocker uniquement l'état courant.

### Modèle traditionnel (CRUD)

```
Base de données classique :
┌──────────────────────────────────┐
│ orders                           │
├────────┬────────┬────────────────┤
│ id     │ status │ updated_at     │
├────────┼────────┼────────────────┤
│ ORD-01 │ SHIPPED│ 2024-01-15 14h │  ← seul l'état courant
└────────┴────────┴────────────────┘
```

**Problèmes :**
- Impossible de savoir QUAND le statut a changé de PENDING à CONFIRMED
- Impossible de rejouer l'historique
- Audit log complexe à maintenir

### Modèle Event Sourcing

```
Kafka Topic "order-events" :
┌────┬───────────────────┬──────────────────────────────────────┐
│ #  │ timestamp         │ event                                │
├────┼───────────────────┼──────────────────────────────────────┤
│ 0  │ 2024-01-15 10:00  │ OrderCreated {id: ORD-01, ...}      │
│ 1  │ 2024-01-15 10:05  │ PaymentProcessed {id: ORD-01, ...}  │
│ 2  │ 2024-01-15 11:00  │ OrderConfirmed {id: ORD-01}         │
│ 3  │ 2024-01-15 14:00  │ OrderShipped {id: ORD-01, tracking} │
└────┴───────────────────┴──────────────────────────────────────┘

État courant = rejouer tous les événements depuis le début
```

---

## Avantages de l'Event Sourcing

| Avantage                | Description                                                       |
|-------------------------|-------------------------------------------------------------------|
| **Audit trail complet** | Chaque changement est tracé avec son timestamp et son auteur      |
| **Time travel**         | Reconstituer l'état à n'importe quel moment passé                 |
| **Rejouabilité**        | Corriger un bug et rejouer les events pour recalculer l'état      |
| **Découplage**          | Plusieurs consommateurs peuvent construire leur propre projection  |
| **CQRS naturel**        | Séparation des lectures (projections) et des écritures (events)   |
| **Débogage**            | Reproducible : reproduire exactement un bug en production         |

---

## Vocabulaire de l'Event Sourcing

| Terme           | Description                                                     |
|-----------------|-----------------------------------------------------------------|
| **Event**       | Fait passé, immuable (ce qui s'est passé)                       |
| **Command**     | Intention d'action (ce qu'on veut faire) — peut être rejetée    |
| **Aggregate**   | Entité qui applique les events pour maintenir son état           |
| **Projection**  | Vue calculée à partir des events (peut être reconstruite)        |
| **Snapshot**    | Capture de l'état à un moment T (pour éviter de rejouer tout)   |
| **Event Store** | Stockage append-only des events (Kafka est idéal pour ça)        |

---

## Implémentation avec Kafka

### Définition des événements

```python
# events.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid
import json


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BaseEvent:
    """Classe de base pour tous les événements."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(default_factory=utcnow)
    event_type: str = field(init=False)

    def to_dict(self) -> dict:
        d = {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'occurred_at': self.occurred_at,
        }
        d.update(self._payload())
        return d

    def _payload(self) -> dict:
        raise NotImplementedError

    def to_json(self) -> bytes:
        return json.dumps(self.to_dict()).encode('utf-8')


@dataclass
class OrderCreated(BaseEvent):
    order_id: str = ''
    customer_id: str = ''
    items: list = field(default_factory=list)
    shipping_address: str = ''

    def __post_init__(self):
        self.event_type = 'order.created'

    def _payload(self) -> dict:
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'items': self.items,
            'shipping_address': self.shipping_address,
        }


@dataclass
class PaymentProcessed(BaseEvent):
    order_id: str = ''
    amount: float = 0.0
    payment_method: str = ''
    transaction_id: str = ''

    def __post_init__(self):
        self.event_type = 'order.payment_processed'

    def _payload(self) -> dict:
        return {
            'order_id': self.order_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
        }


@dataclass
class OrderConfirmed(BaseEvent):
    order_id: str = ''
    confirmed_by: str = 'system'

    def __post_init__(self):
        self.event_type = 'order.confirmed'

    def _payload(self) -> dict:
        return {
            'order_id': self.order_id,
            'confirmed_by': self.confirmed_by,
        }


@dataclass
class OrderShipped(BaseEvent):
    order_id: str = ''
    tracking_number: str = ''
    carrier: str = ''
    estimated_delivery: str = ''

    def __post_init__(self):
        self.event_type = 'order.shipped'

    def _payload(self) -> dict:
        return {
            'order_id': self.order_id,
            'tracking_number': self.tracking_number,
            'carrier': self.carrier,
            'estimated_delivery': self.estimated_delivery,
        }


@dataclass
class OrderCancelled(BaseEvent):
    order_id: str = ''
    reason: str = ''
    cancelled_by: str = ''

    def __post_init__(self):
        self.event_type = 'order.cancelled'

    def _payload(self) -> dict:
        return {
            'order_id': self.order_id,
            'reason': self.reason,
            'cancelled_by': self.cancelled_by,
        }
```

---

### L'Aggregate : reconstituer l'état

```python
# aggregate.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json


@dataclass
class OrderAggregate:
    """
    Aggregate Order : reconstitue l'état d'une commande
    en appliquant les événements dans l'ordre.
    """
    order_id: str
    status: str = 'NEW'
    customer_id: str = ''
    items: List[dict] = field(default_factory=list)
    shipping_address: str = ''
    amount: float = 0.0
    payment_method: str = ''
    transaction_id: str = ''
    tracking_number: str = ''
    carrier: str = ''
    cancellation_reason: str = ''
    version: int = 0  # Numéro du dernier événement appliqué

    # Transitions d'état valides
    VALID_TRANSITIONS = {
        'NEW':       ['PAYMENT_PENDING', 'CANCELLED'],
        'PAYMENT_PENDING': ['CONFIRMED', 'PAYMENT_FAILED', 'CANCELLED'],
        'CONFIRMED': ['PREPARING', 'CANCELLED'],
        'PREPARING': ['SHIPPED', 'CANCELLED'],
        'SHIPPED':   ['DELIVERED'],
        'DELIVERED': [],
        'CANCELLED': [],
        'PAYMENT_FAILED': ['PAYMENT_PENDING', 'CANCELLED'],
    }

    def apply(self, event: dict) -> 'OrderAggregate':
        """
        Applique un événement et retourne le nouvel état de l'aggregate.
        Les méthodes apply_* sont des handlers par type d'événement.
        """
        event_type = event.get('event_type', '')
        handler_name = f"apply_{event_type.replace('.', '_')}"
        handler = getattr(self, handler_name, None)

        if handler:
            handler(event)
        else:
            print(f"Handler inconnu pour l'événement : {event_type}")

        self.version += 1
        return self

    def apply_order_created(self, event: dict):
        self.customer_id = event['customer_id']
        self.items = event['items']
        self.shipping_address = event['shipping_address']
        self.amount = sum(
            item['quantity'] * item['unit_price']
            for item in self.items
        )
        self.status = 'PAYMENT_PENDING'

    def apply_order_payment_processed(self, event: dict):
        self.amount = event['amount']
        self.payment_method = event['payment_method']
        self.transaction_id = event['transaction_id']
        # Le statut sera mis à jour par OrderConfirmed

    def apply_order_confirmed(self, event: dict):
        self.status = 'CONFIRMED'

    def apply_order_shipped(self, event: dict):
        self.tracking_number = event['tracking_number']
        self.carrier = event['carrier']
        self.status = 'SHIPPED'

    def apply_order_cancelled(self, event: dict):
        self.cancellation_reason = event['reason']
        self.status = 'CANCELLED'

    @classmethod
    def rebuild_from_events(cls, order_id: str, events: List[dict]) -> 'OrderAggregate':
        """
        Reconstruit l'état d'une commande à partir de sa liste d'événements.
        Time travel : passer events[:n] pour l'état à l'événement n.
        """
        aggregate = cls(order_id=order_id)
        for event in events:
            aggregate.apply(event)
        return aggregate

    def to_dict(self) -> dict:
        return {
            'order_id': self.order_id,
            'status': self.status,
            'customer_id': self.customer_id,
            'items': self.items,
            'amount': self.amount,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'tracking_number': self.tracking_number,
            'version': self.version,
        }
```

---

### L'Event Store : écrire et lire les événements

```python
# event_store.py
import json
from confluent_kafka import Producer, Consumer, TopicPartition
from typing import List, Optional, Iterator


class KafkaEventStore:
    """
    Event Store basé sur Kafka.
    Kafka est idéal : append-only, durée de rétention configurable,
    rejoue depuis un offset précis, partitionne par aggregate_id.
    """

    EVENT_TOPIC = 'order-events'

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'acks': 'all',
            'enable.idempotence': True,
        })

    def append(self, aggregate_id: str, event: dict) -> None:
        """
        Persiste un événement dans le topic Kafka.
        La clé = aggregate_id garantit que tous les events
        d'une même commande sont dans la même partition → ordre garanti.
        """
        self.producer.produce(
            topic=self.EVENT_TOPIC,
            key=aggregate_id.encode('utf-8'),
            value=json.dumps(event).encode('utf-8'),
            callback=lambda err, msg: (
                print(f"Erreur : {err}") if err
                else None
            )
        )
        self.producer.flush()
        print(f"Event persisté : {event['event_type']} pour {aggregate_id}")

    def get_events_for_aggregate(
        self,
        aggregate_id: str,
        from_version: int = 0
    ) -> List[dict]:
        """
        Récupère tous les événements d'un aggregate depuis une version.

        Note : en production, on utiliserait une table de lookup
        (offset_id → Kafka offset) pour éviter de lire tout le topic.
        Ici, version simplifiée pour la pédagogie.
        """
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': f'event-reader-{aggregate_id}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })

        events = []
        consumer.subscribe([self.EVENT_TOPIC])

        # Lire tous les messages du topic pour trouver ceux de cet aggregate
        # En production : indexer les offsets par aggregate_id dans Redis/PostgreSQL
        try:
            end_reached = False
            empty_polls = 0

            while not end_reached and empty_polls < 3:
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    empty_polls += 1
                    continue

                if msg.error():
                    continue

                empty_polls = 0
                key = msg.key().decode('utf-8') if msg.key() else ''

                if key == aggregate_id:
                    event = json.loads(msg.value().decode('utf-8'))
                    events.append(event)

        finally:
            consumer.close()

        return events[from_version:]


# ─────────────────────────────────────────────
# Utilisation complète
# ─────────────────────────────────────────────

def demo_event_sourcing():
    store = KafkaEventStore()

    # Cycle de vie d'une commande
    order_id = 'ORD-2024-001'

    # 1. Commande créée
    store.append(order_id, OrderCreated(
        order_id=order_id,
        customer_id='CUST-42',
        items=[
            {'product_id': 'LAPTOP-PRO', 'quantity': 1, 'unit_price': 999.00}
        ],
        shipping_address='42 rue de la Paix, Paris'
    ).to_dict())

    # 2. Paiement traité
    store.append(order_id, PaymentProcessed(
        order_id=order_id,
        amount=999.00,
        payment_method='carte_bancaire',
        transaction_id='TXN-789456'
    ).to_dict())

    # 3. Commande confirmée
    store.append(order_id, OrderConfirmed(
        order_id=order_id,
        confirmed_by='payment-service'
    ).to_dict())

    # 4. Expédition
    store.append(order_id, OrderShipped(
        order_id=order_id,
        tracking_number='FR123456789',
        carrier='La Poste',
        estimated_delivery='2024-01-20'
    ).to_dict())

    # Reconstituer l'état courant
    print("\n--- État courant ---")
    events = store.get_events_for_aggregate(order_id)
    current_state = OrderAggregate.rebuild_from_events(order_id, events)
    import json
    print(json.dumps(current_state.to_dict(), indent=2))

    # Time travel : état après le 2ème événement
    print("\n--- État après paiement (time travel) ---")
    state_after_payment = OrderAggregate.rebuild_from_events(order_id, events[:2])
    print(json.dumps(state_after_payment.to_dict(), indent=2))


if __name__ == '__main__':
    demo_event_sourcing()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécuter `demo_event_sourcing()` et montrer dans Kafka UI le topic `order-events` avec tous les événements de la commande ORD-2024-001. Cliquer sur chaque message pour afficher le JSON.
> **Expliquer :** Montrer comment tous les messages d'une même commande sont dans la même partition (grâce à la clé order_id). Démontrer le "time travel" : passer `events[:2]` reconstruit l'état après paiement, `events[:3]` après confirmation. En production, c'est utilisé pour l'audit réglementaire (RGPD, compliance bancaire).

---

## Projections : construire des vues

Une **projection** est une vue calculée à partir des événements, optimisée pour les lectures :

```python
# projections.py
import json
from confluent_kafka import Consumer
from typing import Dict
from aggregate import OrderAggregate


class OrderProjection:
    """
    Projection qui maintient un dictionnaire en mémoire
    de toutes les commandes avec leur état courant.
    Reconstruite en lisant le topic d'événements depuis le début.
    """

    def __init__(self):
        self._orders: Dict[str, dict] = {}
        self._event_log: Dict[str, list] = {}

    def handle_event(self, aggregate_id: str, event: dict):
        """Applique un événement à la projection."""
        if aggregate_id not in self._event_log:
            self._event_log[aggregate_id] = []

        self._event_log[aggregate_id].append(event)

        # Reconstruire l'état de la commande
        aggregate = OrderAggregate.rebuild_from_events(
            aggregate_id,
            self._event_log[aggregate_id]
        )
        self._orders[aggregate_id] = aggregate.to_dict()

    def get_order(self, order_id: str) -> dict:
        return self._orders.get(order_id, {})

    def get_orders_by_status(self, status: str) -> list:
        return [
            order for order in self._orders.values()
            if order.get('status') == status
        ]

    def get_stats(self) -> dict:
        statuses = {}
        for order in self._orders.values():
            s = order.get('status', 'UNKNOWN')
            statuses[s] = statuses.get(s, 0) + 1
        return {
            'total': len(self._orders),
            'by_status': statuses
        }

    def rebuild_from_kafka(self):
        """
        Reconstruit toute la projection en lisant
        le topic d'événements depuis le début.
        """
        consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'projection-rebuilder',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
        })
        consumer.subscribe(['order-events'])

        print("Reconstruction de la projection...")
        count = 0
        empty_polls = 0

        try:
            while empty_polls < 3:
                msg = consumer.poll(1.0)
                if msg is None:
                    empty_polls += 1
                    continue
                if msg.error():
                    continue
                empty_polls = 0

                key = msg.key().decode('utf-8') if msg.key() else ''
                event = json.loads(msg.value().decode('utf-8'))
                self.handle_event(key, event)
                count += 1

        finally:
            consumer.close()

        print(f"Projection reconstruite : {count} événements, {len(self._orders)} commandes")


# Utilisation
projection = OrderProjection()
projection.rebuild_from_kafka()

print(f"\nStatistiques : {projection.get_stats()}")
print(f"Commandes expédiées : {projection.get_orders_by_status('SHIPPED')}")
```

---

## Snapshotting

Pour les aggregates avec de nombreux événements, rejouer depuis le début est lent. Les **snapshots** permettent de repartir d'un état récent :

```python
# snapshot.py
import json
import time

class SnapshotStore:
    """
    Stocke des snapshots périodiques des aggregates.
    En production : Redis, DynamoDB, ou table PostgreSQL.
    Ici : dictionnaire en mémoire pour la démo.
    """

    def __init__(self):
        self._snapshots: dict = {}

    def save(self, aggregate_id: str, state: dict, version: int):
        self._snapshots[aggregate_id] = {
            'state': state,
            'version': version,
            'saved_at': time.time()
        }
        print(f"Snapshot sauvegardé : {aggregate_id} @ v{version}")

    def load(self, aggregate_id: str) -> tuple[dict, int] | None:
        """Retourne (state, version) ou None si pas de snapshot."""
        snap = self._snapshots.get(aggregate_id)
        if snap:
            return snap['state'], snap['version']
        return None


def rebuild_with_snapshot(
    aggregate_id: str,
    event_store: KafkaEventStore,
    snapshot_store: SnapshotStore
) -> OrderAggregate:
    """
    Reconstruit un aggregate en utilisant le snapshot le plus récent.
    """
    snapshot = snapshot_store.load(aggregate_id)

    if snapshot:
        state, version = snapshot
        # Repartir du snapshot
        aggregate = OrderAggregate(**state)
        aggregate.version = version

        # Rejouer seulement les events APRÈS le snapshot
        recent_events = event_store.get_events_for_aggregate(
            aggregate_id,
            from_version=version
        )
        for event in recent_events:
            aggregate.apply(event)

        print(f"Rebuilt from snapshot v{version} + {len(recent_events)} nouveaux events")
    else:
        # Pas de snapshot : rejouer depuis le début
        events = event_store.get_events_for_aggregate(aggregate_id)
        aggregate = OrderAggregate.rebuild_from_events(aggregate_id, events)
        print(f"Rebuilt from scratch : {len(events)} events")

    return aggregate
```

---

## Résumé

| Concept         | Description                                               |
|-----------------|-----------------------------------------------------------|
| Event Sourcing  | Stocker l'historique des événements, pas l'état courant   |
| Event           | Fait passé, immuable, horodaté                            |
| Aggregate       | Entité qui applique les events pour maintenir son état    |
| Projection      | Vue optimisée reconstruite depuis les événements           |
| Snapshot        | Capture périodique pour accélérer la reconstruction       |
| Time travel     | Rejouer les events jusqu'à un point T pour audit          |

**Module suivant :** [02-cdc.md](./02-cdc.md) — Change Data Capture avec Debezium
