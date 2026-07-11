# Exercice 1 — Pipeline e-commerce avec Producer et Consumer

## Contexte

Vous êtes data engineer chez **ShopStream**, un site e-commerce en croissance. L'équipe technique a décidé de migrer vers une architecture événementielle basée sur Kafka.

Votre mission : construire le **pipeline de base** qui capture tous les événements clients et les traite en temps réel.

---

## Objectifs pédagogiques

À l'issue de cet exercice, vous serez capable de :
- Créer des topics Kafka avec la configuration appropriée
- Produire des événements JSON typés avec une clé de partition pertinente
- Consommer des événements avec commit manuel
- Gérer les erreurs et les messages malformés
- Monitorer le lag d'un consumer group dans Kafka UI

---

## Prérequis

- Environnement Docker Compose démarré (`docker compose up -d`)
- Python 3.10+ avec `confluent-kafka` installé
- Kafka UI accessible sur http://localhost:8080

---

## Partie 1 — Modélisation des événements (20 min)

### 1.1 Définir les événements

Le site ShopStream génère les événements suivants :

| Événement           | Description                                              |
|---------------------|----------------------------------------------------------|
| `user.registered`   | Un nouvel utilisateur crée son compte                    |
| `product.viewed`    | Un utilisateur consulte une fiche produit                |
| `cart.item_added`   | Un article est ajouté au panier                          |
| `cart.item_removed` | Un article est retiré du panier                          |
| `order.placed`      | Une commande est passée                                  |
| `payment.success`   | Le paiement est validé                                   |
| `payment.failed`    | Le paiement est refusé                                   |

### 1.2 Créer les topics

Créez les topics suivants avec la commande CLI Kafka (depuis le conteneur) :

```bash
docker exec -it kafka bash

# Topic principal des événements utilisateurs (haute fréquence)
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partitions 6 \
  --replication-factor 1 \
  --config retention.ms=604800000  # 7 jours

# Topic des commandes
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic order-events \
  --partitions 3 \
  --replication-factor 1

# Topic des paiements
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic payment-events \
  --partitions 3 \
  --replication-factor 1

# Dead Letter Queue
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic shopstream.dlq \
  --partitions 1 \
  --replication-factor 1
```

**Question :** Pourquoi `user-events` a 6 partitions et `order-events` seulement 3 ?

---

## Partie 2 — Le Producteur d'événements (40 min)

### 2.1 Structure de base des événements

Créez un fichier `events.py` :

```python
# events.py
from dataclasses import dataclass, field
from typing import Optional, List, Any
from datetime import datetime, timezone
import uuid
import json


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class BaseEvent:
    """Classe de base pour tous les événements ShopStream."""
    event_id: str = field(default_factory=new_id)
    event_type: str = field(init=False, default='')
    timestamp: str = field(default_factory=utcnow)
    session_id: str = ''
    user_agent: str = ''

    def to_dict(self) -> dict:
        raise NotImplementedError

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict()).encode('utf-8')


@dataclass
class UserRegistered(BaseEvent):
    user_id: str = ''
    email: str = ''
    country: str = 'FR'

    def __post_init__(self):
        self.event_type = 'user.registered'

    def to_dict(self) -> dict:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'email': self.email,
            'country': self.country,
        }


@dataclass
class ProductViewed(BaseEvent):
    user_id: str = ''
    product_id: str = ''
    product_name: str = ''
    category: str = ''
    price: float = 0.0

    def __post_init__(self):
        self.event_type = 'product.viewed'

    def to_dict(self) -> dict:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'category': self.category,
            'price': self.price,
        }


@dataclass
class OrderPlaced(BaseEvent):
    user_id: str = ''
    order_id: str = ''
    items: List[dict] = field(default_factory=list)
    total_amount: float = 0.0
    currency: str = 'EUR'

    def __post_init__(self):
        self.event_type = 'order.placed'

    def to_dict(self) -> dict:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'items': self.items,
            'total_amount': self.total_amount,
            'currency': self.currency,
        }


@dataclass
class PaymentResult(BaseEvent):
    user_id: str = ''
    order_id: str = ''
    transaction_id: str = ''
    amount: float = 0.0
    success: bool = True
    failure_reason: Optional[str] = None

    def __post_init__(self):
        self.event_type = 'payment.success' if self.success else 'payment.failed'

    def to_dict(self) -> dict:
        d = {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'success': self.success,
        }
        if self.failure_reason:
            d['failure_reason'] = self.failure_reason
        return d
```

### 2.2 Le producteur

Créez `producer.py` :

```python
# producer.py
"""
Producteur d'événements ShopStream.
Simule le comportement d'utilisateurs sur le site.
"""
import random
import time
import uuid
from confluent_kafka import Producer, KafkaException
import logging
from events import UserRegistered, ProductViewed, OrderPlaced, PaymentResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class ShopStreamProducer:
    """
    Producteur Kafka pour les événements ShopStream.
    Configure automatiquement les topics et gère les erreurs.
    """

    TOPIC_MAP = {
        'user.registered': 'user-events',
        'product.viewed': 'user-events',
        'cart.item_added': 'user-events',
        'cart.item_removed': 'user-events',
        'order.placed': 'order-events',
        'payment.success': 'payment-events',
        'payment.failed': 'payment-events',
    }

    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self._producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'acks': 'all',
            'enable.idempotence': True,
            'retries': 3,
            'retry.backoff.ms': 300,
            'compression.type': 'snappy',
            'batch.size': 32768,
            'linger.ms': 5,
        })
        self._sent = 0
        self._errors = 0

    def _delivery_callback(self, err, msg):
        if err:
            self._errors += 1
            logger.error(
                f"Erreur livraison | topic={msg.topic()} | {err}"
            )
        else:
            self._sent += 1
            logger.debug(
                f"Livré | topic={msg.topic()} | "
                f"partition={msg.partition()} | offset={msg.offset()}"
            )

    def send_event(self, event) -> None:
        """Envoie un événement dans le topic correspondant."""
        data = event.to_dict()
        topic = self.TOPIC_MAP.get(data['event_type'])

        if not topic:
            logger.warning(f"Pas de topic pour : {data['event_type']}")
            return

        self._producer.poll(0)
        self._producer.produce(
            topic=topic,
            key=data.get('user_id', '').encode('utf-8'),
            value=event.to_json_bytes(),
            callback=self._delivery_callback,
        )

    def flush(self):
        self._producer.flush()
        logger.info(
            f"Flush terminé | Envoyés: {self._sent} | Erreurs: {self._errors}"
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()


# ─────────────────────────────────────────────
# Simulation de trafic
# ─────────────────────────────────────────────

PRODUCTS = [
    {'id': 'LAPTOP-X1', 'name': 'Laptop Pro X1', 'category': 'Electronics', 'price': 999.00},
    {'id': 'PHONE-S21', 'name': 'Smartphone S21', 'category': 'Electronics', 'price': 699.00},
    {'id': 'BOOK-PY3', 'name': 'Python 3 Avancé', 'category': 'Books', 'price': 34.99},
    {'id': 'HEADPHONES-Z', 'name': 'Casque Bluetooth Z', 'category': 'Electronics', 'price': 149.00},
    {'id': 'DESK-CHAIR', 'name': 'Chaise Bureau Pro', 'category': 'Furniture', 'price': 399.00},
]


def simulate_user_journey(producer: ShopStreamProducer, user_id: str):
    """
    Simule le parcours d'un utilisateur :
    1. Vue de produits
    2. Ajout au panier
    3. Commande
    4. Paiement (succès ou échec)
    """
    # Visualiser 1 à 3 produits
    viewed_products = random.sample(PRODUCTS, k=random.randint(1, 3))

    for product in viewed_products:
        producer.send_event(ProductViewed(
            user_id=user_id,
            product_id=product['id'],
            product_name=product['name'],
            category=product['category'],
            price=product['price'],
        ))
        time.sleep(random.uniform(0.1, 0.5))

    # 70% de chance de passer commande
    if random.random() > 0.3:
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        items = [
            {
                'product_id': p['id'],
                'product_name': p['name'],
                'quantity': random.randint(1, 3),
                'unit_price': p['price'],
            }
            for p in viewed_products[:random.randint(1, len(viewed_products))]
        ]
        total = sum(i['quantity'] * i['unit_price'] for i in items)

        producer.send_event(OrderPlaced(
            user_id=user_id,
            order_id=order_id,
            items=items,
            total_amount=round(total, 2),
        ))

        # 90% de chance de paiement réussi
        success = random.random() > 0.1
        producer.send_event(PaymentResult(
            user_id=user_id,
            order_id=order_id,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            amount=round(total, 2),
            success=success,
            failure_reason='INSUFFICIENT_FUNDS' if not success else None,
        ))


def run_simulation(n_users: int = 20, n_cycles: int = 3):
    """Lance la simulation avec n_users utilisateurs sur n_cycles tours."""
    # Créer des utilisateurs
    users = [f"user-{uuid.uuid4().hex[:8]}" for _ in range(n_users)]

    # Enregistrer les nouveaux utilisateurs
    with ShopStreamProducer() as producer:
        logger.info(f"Enregistrement de {n_users} utilisateurs...")
        for user_id in users:
            producer.send_event(UserRegistered(
                user_id=user_id,
                email=f"{user_id}@shopstream.fr",
                country=random.choice(['FR', 'BE', 'CH', 'CA']),
            ))

        # Simuler des cycles d'activité
        for cycle in range(n_cycles):
            logger.info(f"--- Cycle {cycle + 1}/{n_cycles} ---")
            active_users = random.sample(users, k=random.randint(5, n_users))

            for user_id in active_users:
                simulate_user_journey(producer, user_id)

            logger.info(
                f"Cycle {cycle + 1} terminé | "
                f"{len(active_users)} utilisateurs actifs"
            )
            time.sleep(2)

    logger.info("Simulation terminée.")


if __name__ == '__main__':
    run_simulation(n_users=15, n_cycles=5)
```

**À faire :** Exécutez `python producer.py` et vérifiez dans Kafka UI que les messages arrivent dans les 3 topics.

---

## Partie 3 — Les Consommateurs (40 min)

### 3.1 Consommateur de commandes

Créez `consumer_orders.py` :

```python
# consumer_orders.py
"""
Consommateur spécialisé dans le traitement des commandes et paiements.
"""
import json
import logging
from confluent_kafka import Consumer, KafkaError
from confluent_kafka import Producer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s — %(message)s'
)
logger = logging.getLogger('order-processor')

# TODO : compléter ce consommateur
# Consignes :
# 1. Créer un Consumer avec group.id = 'order-payment-processor'
# 2. S'abonner à order-events ET payment-events
# 3. Désactiver l'auto-commit
# 4. Pour chaque message :
#    a. Désérialiser le JSON
#    b. Appeler la fonction appropriée selon event_type
#    c. Commiter l'offset manuellement
# 5. Gérer les messages malformés (JSON invalide → DLQ)


def handle_order_placed(event: dict):
    """Traite un événement order.placed."""
    order_id = event.get('order_id', '?')
    user_id = event.get('user_id', '?')
    amount = event.get('total_amount', 0)
    items_count = len(event.get('items', []))

    logger.info(
        f"[COMMANDE] #{order_id} | Utilisateur: {user_id} | "
        f"Montant: {amount:.2f}€ | Articles: {items_count}"
    )
    # TODO : Ajouter logique métier (déclencher réservation stock, etc.)


def handle_payment_success(event: dict):
    """Traite un paiement réussi."""
    order_id = event.get('order_id', '?')
    amount = event.get('amount', 0)
    tx_id = event.get('transaction_id', '?')

    logger.info(
        f"[PAIEMENT OK] Commande #{order_id} | "
        f"Transaction: {tx_id} | Montant: {amount:.2f}€"
    )
    # TODO : Déclencher email de confirmation


def handle_payment_failed(event: dict):
    """Traite un paiement refusé."""
    order_id = event.get('order_id', '?')
    reason = event.get('failure_reason', 'inconnu')

    logger.warning(
        f"[PAIEMENT REFUSÉ] Commande #{order_id} | Raison: {reason}"
    )
    # TODO : Notifier l'utilisateur, proposer autre moyen de paiement


EVENT_HANDLERS = {
    'order.placed': handle_order_placed,
    'payment.success': handle_payment_success,
    'payment.failed': handle_payment_failed,
}


def run():
    # TODO : Implémenter le consommateur
    # Votre code ici
    pass


if __name__ == '__main__':
    run()
```

### 3.2 Consommateur d'analytics

Créez `consumer_analytics.py` :

```python
# consumer_analytics.py
"""
Consommateur analytics : agrège les événements pour produire des statistiques.
Lit tous les topics pour une vue globale du comportement utilisateur.
"""
import json
import logging
from collections import defaultdict
from confluent_kafka import Consumer

logger = logging.getLogger('analytics')
logging.basicConfig(level=logging.INFO)


class AnalyticsCollector:
    """Collecte et agrège les métriques en mémoire."""

    def __init__(self):
        self.event_counts = defaultdict(int)
        self.revenue_total = 0.0
        self.orders_count = 0
        self.failed_payments = 0
        self.users_registered = 0
        self.products_viewed = defaultdict(int)  # product_id → nb vues
        self.revenue_by_category = defaultdict(float)

    def process(self, event: dict):
        event_type = event.get('event_type', 'unknown')
        self.event_counts[event_type] += 1

        if event_type == 'user.registered':
            self.users_registered += 1

        elif event_type == 'product.viewed':
            self.products_viewed[event.get('product_id', '?')] += 1

        elif event_type == 'order.placed':
            self.orders_count += 1

        elif event_type == 'payment.success':
            self.revenue_total += event.get('amount', 0)

        elif event_type == 'payment.failed':
            self.failed_payments += 1

    def print_stats(self):
        print("\n" + "=" * 60)
        print("TABLEAU DE BORD TEMPS RÉEL — SHOPSTREAM")
        print("=" * 60)
        print(f"Utilisateurs inscrits    : {self.users_registered}")
        print(f"Commandes passées        : {self.orders_count}")
        print(f"Chiffre d'affaires       : {self.revenue_total:.2f}€")
        print(f"Paiements refusés        : {self.failed_payments}")

        if self.orders_count > 0:
            payment_success_rate = (
                (self.orders_count - self.failed_payments)
                / self.orders_count * 100
            )
            print(f"Taux succès paiement     : {payment_success_rate:.1f}%")

        print(f"\nTop 3 produits consultés :")
        top_products = sorted(
            self.products_viewed.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        for product_id, views in top_products:
            print(f"  - {product_id}: {views} vues")

        print(f"\nTotal événements par type :")
        for event_type, count in sorted(
            self.event_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {event_type}: {count}")
        print("=" * 60)


def run():
    # TODO : Implémenter le consommateur analytics
    # Consignes :
    # 1. Consumer avec group.id = 'analytics-dashboard'
    # 2. S'abonner à TOUS les topics : user-events, order-events, payment-events
    # 3. Pour chaque message, appeler collector.process(event)
    # 4. Toutes les 50 messages, appeler collector.print_stats()
    # 5. Auto-commit activé (on peut se permettre des doublons pour l'analytics)

    collector = AnalyticsCollector()

    # TODO : Votre code ici
    pass


if __name__ == '__main__':
    run()
```

---

## Partie 4 — Tests et validation (20 min)

### 4.1 Lancer l'ensemble du pipeline

Dans 3 terminaux séparés :

```bash
# Terminal 1 : consommateur des commandes
python consumer_orders.py

# Terminal 2 : consommateur analytics
python consumer_analytics.py

# Terminal 3 : producteur (simulation)
python producer.py
```

### 4.2 Questions de validation

Répondez aux questions suivantes en observant Kafka UI et les logs :

1. Combien de partitions a le topic `user-events` ? Comment sont-ils distribuées par rapport à la clé `user_id` ?

2. Dans Kafka UI > Consumer Groups, quel est le lag de chaque groupe après que le producteur a terminé ?

3. Que se passe-t-il si vous arrêtez et redémarrez `consumer_orders.py` ? Le lag remonte-t-il ? Pourquoi ?

4. Pouvez-vous identifier dans les logs quel utilisateur a eu le plus de paiements refusés ?

---

## Correction — consumer_orders.py

```python
# correction : consumer_orders.py run()
def run():
    dlq_producer = Producer({'bootstrap.servers': 'localhost:9092'})

    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'order-payment-processor',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        'session.timeout.ms': 30000,
    })
    consumer.subscribe(['order-events', 'payment-events'])

    logger.info("Consommateur démarré...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Erreur Kafka : {msg.error()}")
                continue

            try:
                event = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON invalide : {e}")
                dlq_producer.produce(
                    'shopstream.dlq',
                    value=msg.value(),
                    key=msg.key()
                )
                dlq_producer.flush()
                consumer.commit(asynchronous=False)
                continue

            event_type = event.get('event_type', '')
            handler = EVENT_HANDLERS.get(event_type)

            if handler:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Erreur handler {event_type} : {e}")
            else:
                logger.debug(f"Événement ignoré : {event_type}")

            consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        logger.info("Arrêt.")
    finally:
        consumer.commit(asynchronous=False)
        consumer.close()
```

---

## Critères d'évaluation

| Critère                                        | Points |
|------------------------------------------------|--------|
| Topics créés avec bonne configuration          | 2      |
| Producteur : clé de partition pertinente        | 2      |
| Producteur : gestion callback de livraison      | 2      |
| Consumer : commit manuel implémenté             | 3      |
| Consumer : gestion messages malformés → DLQ    | 3      |
| Consumer analytics : agrégats corrects         | 3      |
| Lag = 0 dans Kafka UI après traitement complet | 3      |
| Réponses aux questions de validation            | 2      |
| **Total**                                      | **20** |
