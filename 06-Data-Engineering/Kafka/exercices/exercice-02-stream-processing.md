# Exercice 2 — Traitement de flux en temps réel avec Faust

## Contexte

Suite à l'exercice 1, l'équipe ShopStream veut aller plus loin : en plus de simplement recevoir les événements, elle veut les **traiter en temps réel** pour :

1. Détecter les comportements suspects (fraude potentielle)
2. Maintenir un tableau de bord de ventes en temps réel
3. Identifier les produits les plus populaires sur les 5 dernières minutes
4. Envoyer des alertes automatiques

Votre outil : **Faust**, le framework de stream processing Python.

---

## Objectifs pédagogiques

À l'issue de cet exercice, vous serez capable de :
- Structurer une application Faust multi-agents
- Implémenter des Tables Faust pour maintenir un état
- Utiliser les fenêtres temporelles (tumbling, hopping)
- Chaîner des agents (sortie d'un agent = entrée d'un autre)
- Déclencher des alertes basées sur des règles métier

---

## Prérequis

- Exercice 1 terminé (topics créés, producteur fonctionnel)
- `faust-streaming` installé : `pip install faust-streaming`
- L'environnement Docker est toujours démarré

---

## Architecture cible

```
[user-events] ──→ [agent: enrich_user_event]  ──→ [user-events.enriched]
[order-events] ──┐                                       │
                 ├──→ [agent: fraud_detector]  ──→ [alerts]
[payment-events]─┘                                       │
                                                         ↓
[user-events.enriched] ──→ [agent: product_tracker]  ──→ [Table: trending_products]
                        ──→ [agent: revenue_tracker]  ──→ [Table: revenue_window]
```

---

## Partie 1 — Structure de l'application (15 min)

Créez le fichier principal `stream_app.py` :

```python
# stream_app.py
"""
Application Faust de stream processing pour ShopStream.
Lance avec : python stream_app.py worker -l info
"""
import faust
from datetime import timedelta

# ─────────────────────────────────────────────
# Configuration de l'application
# ─────────────────────────────────────────────
app = faust.App(
    id='shopstream-processor',
    broker='kafka://localhost:9092',
    value_serializer='json',
    topic_partitions=3,
    topic_replication_factor=1,
    web_port=6066,
)

# ─────────────────────────────────────────────
# Définition des topics
# ─────────────────────────────────────────────
user_events_topic = app.topic('user-events', value_type=dict)
order_events_topic = app.topic('order-events', value_type=dict)
payment_events_topic = app.topic('payment-events', value_type=dict)
enriched_topic = app.topic('user-events.enriched', value_type=dict)
alerts_topic = app.topic('shopstream.alerts', value_type=dict)

# ─────────────────────────────────────────────
# Tables de stockage de l'état
# ─────────────────────────────────────────────

# Compteur de commandes par utilisateur (détection fraude)
user_order_count = app.Table(
    'user-order-count',
    default=int,
    partitions=3,
)

# Montant total par utilisateur
user_total_spent = app.Table(
    'user-total-spent',
    default=float,
    partitions=3,
)

# Paiements refusés consécutifs par utilisateur
user_failed_payments = app.Table(
    'user-failed-payments',
    default=int,
    partitions=3,
)

# Produits les plus consultés — fenêtre de 5 minutes
product_views_window = app.Table(
    'product-views-5min',
    default=int,
).hopping(
    size=timedelta(minutes=5),
    step=timedelta(minutes=1),
    expires=timedelta(hours=1),
)

# Chiffre d'affaires — fenêtre de 1 minute (tumbling)
revenue_window = app.Table(
    'revenue-per-minute',
    default=float,
).tumbling(
    size=timedelta(minutes=1),
    expires=timedelta(hours=6),
)

# Compteur commandes — fenêtre de 1 minute (tumbling)
orders_window = app.Table(
    'orders-per-minute',
    default=int,
).tumbling(
    size=timedelta(minutes=1),
    expires=timedelta(hours=6),
)
```

---

## Partie 2 — Agent d'enrichissement (25 min)

Ajoutez dans `stream_app.py` l'agent qui enrichit les événements :

```python
# ─────────────────────────────────────────────
# Agent 1 : Enrichissement des événements
# ─────────────────────────────────────────────

import time
from typing import Optional

# Catalogue produits (en production : appel API ou table Faust)
PRODUCT_CATALOG = {
    'LAPTOP-X1':    {'name': 'Laptop Pro X1',        'category': 'Electronics', 'margin': 0.15},
    'PHONE-S21':    {'name': 'Smartphone S21',        'category': 'Electronics', 'margin': 0.12},
    'BOOK-PY3':     {'name': 'Python 3 Avancé',       'category': 'Books',       'margin': 0.40},
    'HEADPHONES-Z': {'name': 'Casque Bluetooth Z',    'category': 'Electronics', 'margin': 0.25},
    'DESK-CHAIR':   {'name': 'Chaise Bureau Pro',     'category': 'Furniture',   'margin': 0.30},
}


@app.agent(user_events_topic, sink=[enriched_topic])
async def enrich_user_event(events):
    """
    Enrichit chaque événement utilisateur avec :
    - Heure de traitement
    - Données produit (si applicable)
    - Classification du type d'événement
    """
    async for event in events:
        enriched = {
            **event,
            'processed_at': time.time(),
            'processing_lag_ms': 0,  # TODO : calculer le lag réel
        }

        # Enrichir les vues de produits avec les données du catalogue
        if event.get('event_type') == 'product.viewed':
            product_id = event.get('product_id', '')
            catalog_data = PRODUCT_CATALOG.get(product_id, {})
            enriched['category'] = catalog_data.get('category', event.get('category', 'Unknown'))
            enriched['margin'] = catalog_data.get('margin', 0.0)

        yield enriched
```

**À faire :** Calculez le lag réel en millisecondes. Le timestamp de l'événement est dans `event['timestamp']` (format ISO 8601). La différence entre `time.time()` et le timestamp de l'événement donne le lag de traitement.

---

## Partie 3 — Détection de fraude (30 min)

Ajoutez l'agent de détection de fraude :

```python
# ─────────────────────────────────────────────
# Agent 2 : Détection de fraude
# ─────────────────────────────────────────────

# Règles de fraude
FRAUD_RULES = {
    'max_orders_per_session': 5,     # Max 5 commandes en peu de temps
    'max_failed_payments': 3,         # Max 3 paiements refusés consécutifs
    'high_value_threshold': 500.0,    # Commande > 500€ = vérification
    'rapid_order_threshold_s': 60,    # 3+ commandes en moins de 60 secondes
}

# Table pour tracker les timestamps des dernières commandes
user_last_order_time = app.Table(
    'user-last-order-time',
    default=float,
)


async def send_alert(alert_type: str, user_id: str, details: dict):
    """Envoie une alerte dans le topic alerts."""
    await alerts_topic.send(value={
        'alert_type': alert_type,
        'user_id': user_id,
        'details': details,
        'timestamp': time.time(),
    })
    app.logger.warning(
        f"ALERTE [{alert_type}] Utilisateur {user_id} | {details}"
    )


@app.agent(order_events_topic)
async def fraud_detector_orders(events):
    """
    Détecte les comportements suspects sur les commandes.

    Règles :
    - Trop de commandes en peu de temps (velocity check)
    - Montant anormalement élevé
    """
    async for event in events:
        if event.get('event_type') != 'order.placed':
            continue

        user_id = event.get('user_id', '')
        amount = event.get('total_amount', 0)
        now = time.time()

        # Incrémenter le compteur de commandes
        user_order_count[user_id] += 1
        count = user_order_count[user_id]

        # Règle 1 : trop de commandes en peu de temps
        last_order_time = user_last_order_time.get(user_id, 0)
        if (
            count >= 3
            and now - last_order_time < FRAUD_RULES['rapid_order_threshold_s']
        ):
            await send_alert('RAPID_ORDERING', user_id, {
                'order_count': count,
                'seconds_since_last_order': round(now - last_order_time, 1),
                'order_id': event.get('order_id'),
            })

        # Règle 2 : commande à haute valeur
        if amount > FRAUD_RULES['high_value_threshold']:
            await send_alert('HIGH_VALUE_ORDER', user_id, {
                'amount': amount,
                'order_id': event.get('order_id'),
            })

        user_last_order_time[user_id] = now


@app.agent(payment_events_topic)
async def fraud_detector_payments(events):
    """
    Détecte les patterns de paiements suspects.

    Règles :
    - Trop de paiements refusés consécutifs
    """
    async for event in events:
        user_id = event.get('user_id', '')
        success = event.get('success', True)

        if not success:
            user_failed_payments[user_id] += 1
            failed_count = user_failed_payments[user_id]

            if failed_count >= FRAUD_RULES['max_failed_payments']:
                await send_alert('MULTIPLE_PAYMENT_FAILURES', user_id, {
                    'consecutive_failures': failed_count,
                    'last_order_id': event.get('order_id'),
                    'failure_reason': event.get('failure_reason'),
                })
        else:
            # Réinitialiser le compteur d'échecs si paiement réussi
            user_failed_payments[user_id] = 0
```

---

## Partie 4 — Analytics temps réel (30 min)

Ajoutez les agents d'analytics :

```python
# ─────────────────────────────────────────────
# Agent 3 : Suivi des produits populaires
# ─────────────────────────────────────────────

@app.agent(enriched_topic)
async def product_tracker(events):
    """
    Maintient un compteur de vues par produit sur une fenêtre de 5 minutes.
    """
    async for event in events:
        if event.get('event_type') != 'product.viewed':
            continue

        product_id = event.get('product_id', 'unknown')
        category = event.get('category', 'Unknown')

        # Incrémenter dans la fenêtre glissante
        product_views_window[product_id] += 1

        current_views = product_views_window[product_id].current()
        app.logger.debug(
            f"Produit {product_id} | "
            f"Catégorie: {category} | "
            f"Vues (5min): {current_views}"
        )


# ─────────────────────────────────────────────
# Agent 4 : Suivi du chiffre d'affaires
# ─────────────────────────────────────────────

@app.agent(payment_events_topic)
async def revenue_tracker(events):
    """
    Calcule le CA par fenêtre de 1 minute.
    """
    async for event in events:
        if event.get('event_type') != 'payment.success':
            continue

        amount = event.get('amount', 0)

        # Accumuler dans la fenêtre tumbling
        revenue_window['global'] += amount
        orders_window['global'] += 1

        current_revenue = revenue_window['global'].current()
        current_orders = orders_window['global'].current()

        app.logger.info(
            f"[CA Minute] {current_revenue:.2f}€ | "
            f"Commandes: {current_orders} | "
            f"Panier moyen: {current_revenue/max(current_orders,1):.2f}€"
        )


# ─────────────────────────────────────────────
# Timer : rapport toutes les 30 secondes
# ─────────────────────────────────────────────

@app.timer(interval=30.0)
async def periodic_report():
    """
    Affiche un rapport synthétique toutes les 30 secondes.
    """
    # TODO : Compléter ce rapport avec les données des Tables
    # Consignes :
    # 1. Afficher le nombre total d'utilisateurs (via user_order_count)
    # 2. Afficher le CA de la minute courante (revenue_window)
    # 3. Afficher les 3 produits les plus vus (product_views_window)
    # 4. Afficher le nombre d'alertes envoyées (créer un compteur global)

    app.logger.info("=" * 50)
    app.logger.info("RAPPORT PÉRIODIQUE — 30 SECONDES")
    app.logger.info("=" * 50)

    # TODO : implémenter
    pass


if __name__ == '__main__':
    app.main()
```

---

## Partie 5 — Consommateur d'alertes (15 min)

Créez un consommateur séparé `alert_consumer.py` qui lit le topic `shopstream.alerts` :

```python
# alert_consumer.py
"""
Consommateur d'alertes : affiche et logue toutes les alertes générées
par le moteur de détection de fraude.
"""
import json
import logging
from datetime import datetime, timezone
from confluent_kafka import Consumer

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s 🚨 ALERTE — %(message)s'
)
logger = logging.getLogger('alerts')


def format_alert(alert: dict) -> str:
    """Formate une alerte pour affichage lisible."""
    alert_type = alert.get('alert_type', '?')
    user_id = alert.get('user_id', '?')
    details = alert.get('details', {})
    ts = alert.get('timestamp', 0)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%H:%M:%S')

    lines = [
        f"[{dt}] TYPE: {alert_type} | USER: {user_id}",
    ]
    for k, v in details.items():
        lines.append(f"  → {k}: {v}")
    return "\n".join(lines)


def run():
    # TODO : Implémenter le consommateur d'alertes
    # Consignes :
    # 1. Consumer avec group.id = 'alert-monitor'
    # 2. S'abonner au topic shopstream.alerts
    # 3. Pour chaque alerte, appeler format_alert() et l'afficher
    # 4. Compter les alertes par type et afficher un résumé toutes les 20 alertes
    pass


if __name__ == '__main__':
    run()
```

---

## Partie 6 — Tests de charge et validation (20 min)

### 6.1 Lancer tout le pipeline

```bash
# Terminal 1 : Application Faust (stream processing)
python stream_app.py worker -l info

# Terminal 2 : Consommateur d'alertes
python alert_consumer.py

# Terminal 3 : Producteur (simulation de charge)
python producer.py  # depuis l'exercice 1
```

### 6.2 Simuler de la fraude

Modifiez temporairement le producteur pour simuler un comportement suspect :

```python
# test_fraud_simulation.py
"""Simule des comportements suspects pour tester la détection de fraude."""
from producer import ShopStreamProducer
from events import OrderPlaced, PaymentResult
import time
import uuid

with ShopStreamProducer() as producer:
    # Scénario 1 : beaucoup de commandes rapides pour un même utilisateur
    fraud_user = f"SUSPICIOUS-{uuid.uuid4().hex[:6]}"
    print(f"Simulation fraude pour l'utilisateur : {fraud_user}")

    for i in range(6):  # 6 commandes en moins de 10 secondes
        order_id = f"FRAUD-ORD-{i:03d}"
        producer.send_event(OrderPlaced(
            user_id=fraud_user,
            order_id=order_id,
            items=[{'product_id': 'LAPTOP-X1', 'quantity': 1, 'unit_price': 999.00}],
            total_amount=999.00,
        ))
        print(f"Commande #{i+1} envoyée")
        time.sleep(0.5)  # 0.5 seconde entre chaque commande

    # Scénario 2 : paiements refusés répétés
    bad_payer = f"BAD-PAYER-{uuid.uuid4().hex[:6]}"
    for i in range(4):
        producer.send_event(PaymentResult(
            user_id=bad_payer,
            order_id=f"BP-ORD-{i:03d}",
            transaction_id=f"TXN-FAIL-{i:03d}",
            amount=150.00,
            success=False,
            failure_reason='CARD_DECLINED',
        ))
        time.sleep(1)

print("Simulation terminée. Vérifiez les alertes !")
```

### 6.3 Questions de validation

1. Combien d'alertes `RAPID_ORDERING` ont été générées pour l'utilisateur suspect ?

2. Dans Kafka UI, ouvrez le topic `shopstream.alerts`. Quel est le contenu JSON d'une alerte `MULTIPLE_PAYMENT_FAILURES` ?

3. Que contient la Table Faust `user-order-count` après la simulation ? Comment accéder à une Table Faust depuis l'extérieur de l'application ?

4. Vérifiez le monitoring Faust sur http://localhost:6066. Quels agents sont actifs et combien d'événements ont-ils traités ?

5. Arrêtez et redémarrez l'application Faust. Les compteurs d'utilisateurs sont-ils conservés ? Pourquoi ?

---

## Correction — periodic_report

```python
@app.timer(interval=30.0)
async def periodic_report():
    app.logger.info("=" * 50)
    app.logger.info("RAPPORT PÉRIODIQUE — SHOPSTREAM")
    app.logger.info("=" * 50)

    # Nombre d'utilisateurs avec au moins 1 commande
    nb_users = len(list(user_order_count.keys()))
    app.logger.info(f"Utilisateurs actifs : {nb_users}")

    # CA de la minute courante
    try:
        current_revenue = revenue_window['global'].current()
        current_orders = orders_window['global'].current()
        avg_basket = current_revenue / max(current_orders, 1)
        app.logger.info(
            f"CA minute courante : {current_revenue:.2f}€ "
            f"({current_orders} commandes, "
            f"panier moyen: {avg_basket:.2f}€)"
        )
    except Exception:
        app.logger.info("Pas encore de données de CA")

    # Top produits (fenêtre 5 min)
    # Note : product_views_window.items() non disponible directement
    # En pratique, il faudrait une Table séparée non-fenêtrée pour le classement
    app.logger.info("(Top produits non affiché — voir Table product-views-5min)")

    app.logger.info("=" * 50)
```

---

## Bonus : enrichissement avec appel API externe

```python
# bonus_external_enrichment.py
"""
Bonus : enrichir les événements avec des données externes (async HTTP).
"""
import faust
import aiohttp  # pip install aiohttp

app = faust.App('enrichment-bonus', broker='kafka://localhost:9092')

@app.agent(app.topic('product.viewed', value_type=dict))
async def enrich_with_inventory(events):
    """
    Appelle une API externe pour récupérer le stock disponible.
    Exemple avec aiohttp (HTTP async).
    """
    async with aiohttp.ClientSession() as session:
        async for event in events:
            product_id = event.get('product_id', '')

            try:
                async with session.get(
                    f"http://inventory-api:8000/products/{product_id}/stock",
                    timeout=aiohttp.ClientTimeout(total=0.5)  # 500ms max
                ) as response:
                    if response.status == 200:
                        stock_data = await response.json()
                        event['stock_available'] = stock_data.get('quantity', -1)
                    else:
                        event['stock_available'] = -1

            except asyncio.TimeoutError:
                event['stock_available'] = -1
                app.logger.warning(f"Timeout API stock pour {product_id}")

            yield event
```

---

## Critères d'évaluation

| Critère                                                    | Points |
|------------------------------------------------------------|--------|
| Structure Faust correcte (App, Topics, Tables)             | 3      |
| Agent enrich_user_event fonctionnel (avec lag calculé)     | 3      |
| Détection fraude : velocity check implémenté               | 3      |
| Détection fraude : paiements refusés implémenté            | 3      |
| Analytics : revenue_tracker avec fenêtre tumbling          | 3      |
| Analytics : product_tracker avec fenêtre hopping           | 3      |
| Rapport périodique avec données des Tables                 | 2      |
| Test de fraude et alertes visibles dans Kafka UI           | 3      |
| Réponses aux questions de validation                       | 5      |
| **Total**                                                  | **28** |

---

## Pour aller plus loin

- Ajouter un agent qui consomme `shopstream.alerts` et envoie un email via SMTP async
- Intégrer un dashboard Grafana qui lit les métriques depuis les Tables Faust via l'API HTTP (port 6066)
- Ajouter la persistance RocksDB : `store='rocksdb://'` dans la config App
- Implémenter le pattern "saga" : suivre l'état d'une commande à travers plusieurs topics
