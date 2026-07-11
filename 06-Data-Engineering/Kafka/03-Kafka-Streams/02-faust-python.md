# Faust : Stream Processing en Python

## Architecture de Faust

Faust est construit autour de trois primitives :

```
┌──────────────────────────────────────────────────────────┐
│                      App Faust                           │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Topics    │  │   Agents    │  │     Tables      │ │
│  │ (Kafka)     │  │ (Workers)   │  │ (État distribué)│ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │   Timers    │  │   Crons     │                       │
│  │ (fenêtres)  │  │ (planifié)  │                       │
│  └─────────────┘  └─────────────┘                       │
└──────────────────────────────────────────────────────────┘
```

---

## Configuration de l'application

```python
# config.py
import faust
from faust.types import StreamT

app = faust.App(
    # Identifiant unique de l'application (utilisé comme consumer group prefix)
    id='ecommerce-stream-processor',

    # Adresse du broker Kafka
    broker='kafka://localhost:9092',

    # Format de sérialisation par défaut
    value_serializer='json',
    key_serializer='raw',

    # Nombre de partitions pour les topics internes (état)
    # Doit être ≤ au nombre de partitions des topics consommés
    topic_partitions=3,

    # Réplication des topics internes (mettre à 1 en dev)
    topic_replication_factor=1,

    # Port HTTP pour l'interface de monitoring Faust
    web_port=6066,

    # Activer les logs structurés
    loghandlers=[],
)
```

---

## Définir des modèles de données

Faust supporte les **Records** — des classes de données typées :

```python
# models.py
import faust
from datetime import datetime
from typing import Optional, List

class OrderItem(faust.Record, serializer='json'):
    product_id: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


class Order(faust.Record, serializer='json'):
    order_id: str
    customer_id: str
    amount: float
    status: str = 'PENDING'
    created_at: Optional[str] = None
    items: List[OrderItem] = []

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def is_high_value(self) -> bool:
        return self.amount > 200.0


class EnrichedOrder(faust.Record, serializer='json'):
    """Commande enrichie avec des données calculées."""
    order_id: str
    customer_id: str
    amount: float
    tax_amount: float
    total_with_tax: float
    status: str
    is_high_value: bool
    processed_at: str
```

---

## Agents : les workers du flux

### Agent simple (stateless)

```python
# agents_simple.py
import faust
from models import Order, EnrichedOrder
from datetime import datetime, timezone

app = faust.App('order-processor', broker='kafka://localhost:9092')

orders_topic = app.topic('orders.created', value_type=Order)
enriched_topic = app.topic('orders.enriched', value_type=EnrichedOrder)
high_value_topic = app.topic('orders.high-value', value_type=EnrichedOrder)
dlq_topic = app.topic('orders.dlq', value_type=dict)


@app.agent(orders_topic, sink=[enriched_topic])
async def enrich_order(orders):
    """
    Enrichit chaque commande avec des données calculées.
    Stateless : ne dépend pas de l'historique.
    """
    async for order in orders:
        try:
            tax_rate = 0.20  # TVA 20%
            tax = round(order.amount * tax_rate, 2)

            enriched = EnrichedOrder(
                order_id=order.order_id,
                customer_id=order.customer_id,
                amount=order.amount,
                tax_amount=tax,
                total_with_tax=round(order.amount + tax, 2),
                status=order.status,
                is_high_value=order.is_high_value,
                processed_at=datetime.now(timezone.utc).isoformat()
            )

            app.logger.info(
                f"Enrichi | {order.order_id} | "
                f"{enriched.total_with_tax:.2f}€ TTC"
            )
            yield enriched

        except Exception as e:
            app.logger.error(f"Erreur traitement {order.order_id}: {e}")
            await dlq_topic.send(value={
                'order_id': order.order_id,
                'error': str(e),
                'original': order.to_representation()
            })


@app.agent(enriched_topic, sink=[high_value_topic])
async def detect_high_value(orders):
    """Filtre les commandes à haute valeur."""
    async for order in orders:
        if order.is_high_value:
            app.logger.warning(
                f"HAUTE VALEUR | {order.order_id} | {order.amount:.2f}€"
            )
            yield order


if __name__ == '__main__':
    app.main()
```

---

## Tables : état distribué

Les **tables Faust** sont des stores clé-valeur persistés dans **RocksDB**, distribués sur les workers.

```python
# agents_stateful.py
import faust
from models import Order
from datetime import datetime, timezone

app = faust.App(
    'stateful-processor',
    broker='kafka://localhost:9092',
    store='rocksdb://',  # Persistance locale avec RocksDB
)

orders_topic = app.topic('orders.created', value_type=Order)

# Table : nombre de commandes par client
order_count_table = app.Table(
    'order-counts',
    default=int,  # Valeur par défaut = 0
    partitions=3,
)

# Table : montant total dépensé par client
total_spent_table = app.Table(
    'customer-total-spent',
    default=float,
    partitions=3,
)

# Table : dernière commande par client
last_order_table = app.Table(
    'last-order',
    default=dict,
    partitions=3,
)


@app.agent(orders_topic)
async def track_customer_stats(orders):
    """
    Maintient des statistiques par client.
    Stateful : accumule des données au fil du temps.
    """
    async for order in orders:
        cid = order.customer_id

        # Incrémenter le compteur
        order_count_table[cid] += 1

        # Accumuler le montant
        total_spent_table[cid] = (total_spent_table[cid] or 0.0) + order.amount

        # Mémoriser la dernière commande
        last_order_table[cid] = {
            'order_id': order.order_id,
            'amount': order.amount,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        count = order_count_table[cid]
        total = total_spent_table[cid]

        app.logger.info(
            f"Client {cid} | "
            f"Commandes: {count} | "
            f"Total: {total:.2f}€ | "
            f"Moyenne: {total/count:.2f}€"
        )

        # Détecter les clients VIP (> 5 commandes OU > 500€ dépensés)
        if count >= 5 or total >= 500:
            app.logger.warning(f"CLIENT VIP : {cid} | {count} cmd | {total:.2f}€")


if __name__ == '__main__':
    app.main()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer l'agent stateful, envoyer plusieurs commandes pour le même client, et montrer les logs indiquant l'accumulation des compteurs. Puis arrêter et redémarrer l'agent pour montrer que l'état est persisté (les compteurs ne sont pas réinitialisés).
> **Expliquer :** C'est la différence fondamentale avec une simple variable Python : l'état survit aux redémarrages car il est stocké dans RocksDB sur le disque. En production, cela permet de ne pas perdre l'état d'agrégation même en cas de crash.

---

## Fenêtres temporelles avec Faust

```python
# windowed_aggregation.py
import faust
from datetime import timedelta
from models import Order

app = faust.App(
    'windowed-analytics',
    broker='kafka://localhost:9092',
)

orders_topic = app.topic('orders.created', value_type=Order)

# ─────────────────────────────────────────────
# Fenêtre Tumbling : agrégat sur des tranches fixes
# ─────────────────────────────────────────────

# Table fenêtrée : somme des montants par tranche de 1 minute
hourly_revenue = app.Table(
    'hourly-revenue',
    default=float,
    partitions=3,
).tumbling(
    size=timedelta(minutes=1),   # Fenêtre de 1 minute
    expires=timedelta(hours=24), # Conserver les résultats 24h
)

# Compteur de commandes par fenêtre de 1 minute
order_count_window = app.Table(
    'order-count-per-minute',
    default=int,
).tumbling(
    size=timedelta(minutes=1),
    expires=timedelta(hours=1),
)


@app.agent(orders_topic)
async def aggregate_revenue(orders):
    """
    Calcule le chiffre d'affaires par tranche de 1 minute.
    Fenêtre Tumbling : [00:00-01:00), [01:00-02:00), etc.
    """
    async for order in orders:
        # Clé de la fenêtre = customer_id pour agréger par client
        customer_key = order.customer_id

        # Accumuler le montant dans la fenêtre courante
        hourly_revenue[customer_key] += order.amount
        order_count_window[customer_key] += 1

        # Récupérer la valeur actuelle de la fenêtre
        current_revenue = hourly_revenue[customer_key].current()
        current_count = order_count_window[customer_key].current()

        app.logger.info(
            f"[Fenêtre minute] Client {customer_key} | "
            f"CA: {current_revenue:.2f}€ | "
            f"Commandes: {current_count}"
        )


# ─────────────────────────────────────────────
# Fenêtre Hopping (Glissante)
# ─────────────────────────────────────────────

# Commandes des 10 dernières minutes, mise à jour toutes les 1 minute
sliding_count = app.Table(
    'sliding-order-count',
    default=int,
).hopping(
    size=timedelta(minutes=10),  # Fenêtre de 10 minutes
    step=timedelta(minutes=1),   # Avance de 1 minute à la fois
    expires=timedelta(hours=1),
)


@app.agent(orders_topic)
async def detect_anomalies(orders):
    """
    Détecte un volume anormal de commandes (fenêtre glissante de 10 min).
    """
    async for order in orders:
        sliding_count['total'] += 1
        total_10min = sliding_count['total'].current()

        if total_10min > 50:
            app.logger.warning(
                f"ALERTE : {total_10min} commandes en 10 minutes ! "
                f"Possible attaque ou pic de trafic."
            )


if __name__ == '__main__':
    app.main()
```

---

## Jointure de flux (Stream Join)

```python
# stream_join.py
import faust
from faust import Record
from typing import Optional

app = faust.App('stream-join', broker='kafka://localhost:9092')


class Order(faust.Record):
    order_id: str
    customer_id: str
    amount: float


class CustomerProfile(faust.Record):
    customer_id: str
    name: str
    email: str
    vip: bool = False


class EnrichedOrderWithCustomer(faust.Record):
    order_id: str
    customer_name: str
    customer_email: str
    amount: float
    is_vip: bool


orders_topic = app.topic('orders.created', value_type=Order)
customers_topic = app.topic('customers.updated', value_type=CustomerProfile)
enriched_topic = app.topic('orders.enriched-with-customer', value_type=EnrichedOrderWithCustomer)

# Table pour stocker les profils clients (matérialisée depuis le topic)
customer_table = app.Table(
    'customer-profiles',
    default=None,
)


@app.agent(customers_topic)
async def update_customer_table(customers):
    """
    Maintient une table à jour des profils clients.
    Chaque mise à jour du topic écrase l'entrée dans la table.
    """
    async for customer in customers:
        customer_table[customer.customer_id] = customer.to_representation()
        app.logger.info(f"Profil mis à jour : {customer.customer_id}")


@app.agent(orders_topic, sink=[enriched_topic])
async def enrich_with_customer(orders):
    """
    Enrichit chaque commande avec le profil client.
    Jointure Kafka Stream ↔ Table (Stream-Table Join).
    """
    async for order in orders:
        # Lookup dans la table (clé-valeur en mémoire/RocksDB)
        customer_data = customer_table.get(order.customer_id)

        if customer_data:
            yield EnrichedOrderWithCustomer(
                order_id=order.order_id,
                customer_name=customer_data['name'],
                customer_email=customer_data['email'],
                amount=order.amount,
                is_vip=customer_data.get('vip', False),
            )
        else:
            # Client inconnu → enrichissement partiel
            app.logger.warning(
                f"Client inconnu : {order.customer_id} | "
                f"Commande {order.order_id} non enrichie"
            )
            yield EnrichedOrderWithCustomer(
                order_id=order.order_id,
                customer_name='Inconnu',
                customer_email='',
                amount=order.amount,
                is_vip=False,
            )


if __name__ == '__main__':
    app.main()
```

---

## Timers et tâches planifiées

```python
# timers_and_crons.py
import faust
from datetime import timedelta

app = faust.App('timers-demo', broker='kafka://localhost:9092')

# Table pour suivre le temps de la dernière commande par client
last_seen = app.Table('last-seen', default=float)

orders_topic = app.topic('orders.created', value_type=dict)


@app.agent(orders_topic)
async def track_last_seen(orders):
    import time
    async for order in orders:
        last_seen[order['customer_id']] = time.time()


# Tâche planifiée : s'exécute toutes les 30 secondes
@app.timer(interval=30.0)
async def check_inactive_customers():
    """Détecte les clients inactifs depuis plus de 5 minutes."""
    import time
    now = time.time()
    inactive_threshold = 5 * 60  # 5 minutes

    inactive = [
        cid for cid, last_ts in last_seen.items()
        if now - last_ts > inactive_threshold
    ]

    if inactive:
        app.logger.info(
            f"Clients inactifs depuis >5min : {inactive}"
        )


# Tâche CRON : s'exécute tous les jours à minuit
@app.crontab('0 0 * * *')
async def daily_summary():
    """Rapport quotidien envoyé à minuit."""
    total_customers = len(list(last_seen.keys()))
    app.logger.info(
        f"[Rapport quotidien] Clients actifs aujourd'hui : {total_customers}"
    )


if __name__ == '__main__':
    app.main()
```

---

## Lancer et monitorer Faust

```bash
# Lancer un worker Faust
python agents_simple.py worker -l info

# Lancer avec plusieurs threads (concurrence)
python agents_simple.py worker -l info --concurrency=4

# Lancer plusieurs workers (scalabilité)
python agents_simple.py worker -l info &  # Worker 1
python agents_simple.py worker -l info &  # Worker 2
python agents_simple.py worker -l info &  # Worker 3

# Interface web Faust (monitoring)
# http://localhost:6066
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancer un pipeline Faust complet (enrich_order + detect_high_value), produire des messages dans `orders.created`, et montrer les logs en temps réel dans le terminal + le résultat dans `orders.enriched` visible dans Kafka UI.
> **Expliquer :** Montrer le flux complet : message entrant dans orders.created, transformation dans l'agent, message sortant dans orders.enriched. Ouvrir les deux topics dans Kafka UI et montrer comment comparer un message avant et après transformation. Insister sur la latence : < 100ms entre l'entrée et la sortie.

---

## Application complète : pipeline e-commerce

```python
# ecommerce_pipeline.py
"""
Pipeline complet de traitement des commandes e-commerce :
1. Enrichissement (TVA, classification)
2. Détection de fraude
3. Agrégats en temps réel
4. Alertes
"""
import faust
import time
from datetime import timedelta
from dataclasses import dataclass


app = faust.App(
    'ecommerce-pipeline',
    broker='kafka://localhost:9092',
    topic_partitions=3,
)

# Topics
orders_in = app.topic('orders.created', value_type=dict)
orders_enriched = app.topic('orders.enriched', value_type=dict)
orders_flagged = app.topic('orders.flagged', value_type=dict)
alerts_topic = app.topic('alerts', value_type=dict)

# Tables
customer_order_count = app.Table('customer-order-count', default=int)
customer_total = app.Table('customer-total', default=float)
revenue_per_minute = app.Table('revenue-per-minute', default=float).tumbling(
    timedelta(minutes=1), expires=timedelta(hours=1)
)


@app.agent(orders_in, sink=[orders_enriched])
async def enrich(orders):
    """Étape 1 : Enrichissement TVA et classification."""
    async for order in orders:
        amount = order.get('amount', 0)
        yield {
            **order,
            'tax': round(amount * 0.20, 2),
            'total': round(amount * 1.20, 2),
            'tier': 'premium' if amount > 200 else 'standard',
            'processed_at': time.time(),
        }


@app.agent(orders_enriched)
async def fraud_detection(orders):
    """Étape 2 : Détection de fraude basique."""
    async for order in orders:
        cid = order['customer_id']

        customer_order_count[cid] += 1
        customer_total[cid] = (customer_total[cid] or 0) + order['amount']

        count = customer_order_count[cid]
        total = customer_total[cid]

        # Règle : plus de 10 commandes en peu de temps = suspect
        if count > 10:
            await alerts_topic.send(value={
                'type': 'FRAUD_SUSPICION',
                'customer_id': cid,
                'order_count': count,
                'total_amount': total,
                'order_id': order['order_id'],
                'timestamp': time.time(),
            })
            app.logger.warning(f"FRAUDE POSSIBLE : {cid} ({count} commandes)")


@app.agent(orders_enriched)
async def realtime_analytics(orders):
    """Étape 3 : Agrégats en temps réel."""
    async for order in orders:
        revenue_per_minute['global'] += order['amount']
        current = revenue_per_minute['global'].current()
        app.logger.info(f"CA minute courante : {current:.2f}€")


if __name__ == '__main__':
    app.main()
```

```bash
# Lancer le pipeline
python ecommerce_pipeline.py worker -l info

# Dans un autre terminal, envoyer des commandes
python json_producer.py
```

---

## Résumé

| Concept            | Description                                              |
|--------------------|----------------------------------------------------------|
| `app.agent()`      | Décorateur qui définit un worker de traitement de flux   |
| `app.Table()`      | Store clé-valeur persisté (état distribué)               |
| `.tumbling()`      | Fenêtre de taille fixe, sans chevauchement               |
| `.hopping()`       | Fenêtre glissante, avec chevauchement                    |
| `app.timer()`      | Tâche périodique en secondes                             |
| `app.crontab()`    | Tâche planifiée via expression cron                      |
| `sink=[topic]`     | Envoyer automatiquement la sortie dans un topic          |
| `yield`            | Émettre un message de sortie depuis un agent             |

**Module suivant :** [Patterns/01-event-sourcing.md](../Patterns/01-event-sourcing.md)
