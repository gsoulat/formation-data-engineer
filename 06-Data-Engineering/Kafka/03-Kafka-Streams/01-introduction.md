# Introduction au Stream Processing avec Kafka

## Qu'est-ce que le stream processing ?

Le **stream processing** (traitement en flux) consiste à traiter des données **au fur et à mesure de leur arrivée**, plutôt qu'en attendant d'en accumuler un lot.

```
Batch Processing :
[données] → attendre → [gros fichier] → traiter → [résultat]
                         (minutes/heures plus tard)

Stream Processing :
[événement] → traiter immédiatement → [résultat]
               (millisecondes plus tard)
```

### Opérations typiques en stream processing

- **Filtrage** : ne garder que les événements qui correspondent à un critère
- **Transformation** : modifier la structure d'un événement (map/flatMap)
- **Agrégation** : compter, sommer, moyenner sur une fenêtre temporelle
- **Jointure** : combiner deux flux en temps réel
- **Enrichissement** : ajouter des données depuis une source externe
- **Détection** : identifier des patterns (ex: 3 paiements refusés en 1 minute)

---

## Les options pour Python + Kafka

### 1. Kafka Streams (Java uniquement)

**Kafka Streams** est la bibliothèque officielle de stream processing de l'écosystème Kafka. Elle est puissante et mature, mais **uniquement disponible en Java/Scala**.

```java
// Kafka Streams (Java) — pour information
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders.created");
orders
    .filter((key, order) -> order.getAmount() > 100)
    .mapValues(order -> new HighValueOrder(order))
    .to("orders.high-value");
```

### 2. ksqlDB

**ksqlDB** est un moteur SQL pour Kafka. Il permet d'écrire des requêtes SQL qui s'exécutent en continu sur des flux.

```sql
-- ksqlDB — pour information
CREATE STREAM high_value_orders AS
SELECT order_id, customer_id, amount
FROM orders_created
WHERE amount > 100
EMIT CHANGES;
```

Avantages : accessible aux équipes SQL, pas besoin de coder.
Inconvénients : moins flexible, nécessite un serveur ksqlDB séparé.

### 3. Faust (Python) ✅ Notre choix

**Faust** est une bibliothèque Python de stream processing inspirée de Kafka Streams. Créée par Robinhood (la plateforme de trading), elle permet d'écrire des pipelines de traitement en flux directement en Python.

```python
# Faust — notre choix pour ce cours
import faust

app = faust.App('order-processor', broker='kafka://localhost:9092')
orders_topic = app.topic('orders.created')

@app.agent(orders_topic)
async def process_orders(orders):
    async for order in orders:
        if order['amount'] > 100:
            print(f"Commande haute valeur : {order['order_id']}")
```

### 4. Apache Spark Structured Streaming (Python)

Spark peut consommer depuis Kafka et traiter en micro-batch ou en streaming continu. C'est la solution pour les **très grands volumes** avec des transformations complexes.

```python
# Spark Structured Streaming — couvert dans Integration/
spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders.created") \
    .load()
```

---

## Comparaison des solutions Python

| Critère              | Faust             | Spark Streaming      | ksqlDB             |
|----------------------|-------------------|----------------------|--------------------|
| Langage              | Python pur        | Python (PySpark)     | SQL                |
| Latence              | < 100ms           | ~500ms (micro-batch) | < 100ms            |
| Facilité             | Élevée            | Moyenne              | Élevée pour SQL    |
| Scalabilité          | Moyenne           | Très haute           | Haute              |
| État (stateful)      | Oui (RocksDB)     | Oui                  | Oui                |
| Fenêtrage            | Oui               | Oui (plus complet)   | Oui                |
| Cas d'usage          | Microservices     | Big Data             | Analytics temps réel|
| Déploiement          | Simple            | Cluster Spark requis | Serveur ksqlDB     |

**Pour ce cours, nous utilisons Faust** car il est :
- Natif Python (pas de Java)
- Simple à installer et démarrer
- Parfait pour les microservices de taille moyenne
- Syntaxe claire et lisible

---

## Concepts fondamentaux du stream processing

### Temps : event time vs processing time

```
Event Time :    l'heure à laquelle l'événement s'est produit
                (timestamp dans le message)

Processing Time : l'heure à laquelle le système traite l'événement
                (heure système du worker)

Ingestion Time : l'heure à laquelle Kafka a reçu le message
```

En pratique, il peut y avoir un **décalage** (skew) entre ces trois temps :

```
14:00:00 → L'événement se produit (event time)
14:00:05 → Kafka reçoit le message (ingestion time)
14:00:08 → Le stream processor traite le message (processing time)
```

Ce skew est problématique pour les agrégations temporelles : si on compte les commandes de 14h à 15h, un événement de 14:59:50 peut arriver à 15:00:10 à cause de la latence réseau. C'est le problème des **données tardives** (late data).

### Fenêtres temporelles (Windowing)

Les fenêtres permettent de grouper des événements sur une période de temps pour les agréger.

#### Fenêtre Tumbling (Bascule)

```
Fenêtres de 1 minute, non superposées :

[14:00 - 14:01) → 42 commandes
[14:01 - 14:02) → 35 commandes
[14:02 - 14:03) → 58 commandes
```

#### Fenêtre Sliding (Glissante)

```
Fenêtres de 1 minute, se déplaçant toutes les 30 secondes :

[14:00:00 - 14:01:00) → 42 commandes
[14:00:30 - 14:01:30) → 48 commandes
[14:01:00 - 14:02:00) → 35 commandes
```

#### Fenêtre Session

```
Fenêtre qui s'étend tant que des événements arrivent
(avec timeout d'inactivité = 5 minutes) :

Session utilisateur A :
[14:00 - 14:23] → 15 actions (session active)
[gap > 5 min]
[14:35 - 14:41] → 3 actions (nouvelle session)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir un schéma visuel montrant les 3 types de fenêtres (tumbling, sliding, session) côte à côte. Utiliser un tableau blanc ou un diagramme projeté.
> **Expliquer :** Pour chaque type, donner un cas d'usage concret : tumbling pour les agrégats horaires de ventes, sliding pour la détection de fraude (5 transactions en 10 minutes), session pour l'analyse du comportement utilisateur sur un site e-commerce.

---

### Traitement stateful vs stateless

**Stateless** (sans état) : chaque message est traité indépendamment.

```python
# Stateless : filtrer les commandes > 100€ — pas de mémoire nécessaire
@app.agent(orders_topic)
async def filter_high_value(orders):
    async for order in orders:
        if order['amount'] > 100:
            await high_value_topic.send(value=order)
```

**Stateful** (avec état) : le traitement dépend de l'historique des messages.

```python
# Stateful : compter les commandes par client — nécessite de mémoriser le compteur
@app.agent(orders_topic)
async def count_by_customer(orders):
    async for order in orders:
        # Lire l'état actuel
        count = await order_counts[order['customer_id']]
        # Mettre à jour
        await order_counts.set(order['customer_id'], (count or 0) + 1)
```

Faust stocke l'état dans **RocksDB** (une base de données clé-valeur locale), ce qui permet de survivre aux redémarrages.

---

## Architecture d'un pipeline Faust

```
[Kafka Topic: orders.created]
          │
          ▼
[Faust Agent: enrich_order]
  - Ajouter les infos client depuis BDD
  - Calculer la TVA
          │
          ▼
[Kafka Topic: orders.enriched]
          │
    ┌─────┴──────┐
    ▼            ▼
[Agent:       [Agent:
 fraud_check]  analytics]
  - Analyser   - Agréger
    le pattern   par heure
    de paiement         │
         │              ▼
         ▼        [Table: hourly_stats]
[orders.flagged]
```

---

## Installation de Faust

```bash
# Version de base
pip install faust-streaming

# Avec support RocksDB (persistance de l'état)
pip install faust-streaming[rocksdb]

# Vérification
python -c "import faust; print(faust.__version__)"
```

> **Note :** Utiliser `faust-streaming` et non `faust` — le package original n'est plus maintenu. `faust-streaming` est le fork actif maintenu par la communauté.

---

## Premier agent Faust

```python
# premier_agent.py
import faust

# Créer l'application Faust
app = faust.App(
    id='premier-agent',
    broker='kafka://localhost:9092',
    value_serializer='json',
)

# Définir les topics
orders_topic = app.topic(
    'orders.created',
    value_type=dict,      # Type Python attendu
)

processed_topic = app.topic(
    'orders.processed',
    value_type=dict,
)

# Créer un agent (worker qui traite le flux)
@app.agent(orders_topic, sink=[processed_topic])
async def process_orders(orders):
    """
    Agent Faust : traite chaque commande du topic orders.created
    et envoie le résultat dans orders.processed.
    """
    async for order in orders:
        # Enrichir la commande
        enriched = {
            **order,
            'processed': True,
            'tax_amount': round(order['amount'] * 0.20, 2),  # TVA 20%
            'total_with_tax': round(order['amount'] * 1.20, 2),
        }

        print(f"Commande traitée : {enriched['order_id']} → {enriched['total_with_tax']:.2f}€ TTC")

        # L'agent retourne la valeur → envoyée dans processed_topic (sink)
        yield enriched


if __name__ == '__main__':
    app.main()
```

```bash
# Lancer l'agent Faust
python premier_agent.py worker -l info

# Dans un autre terminal, envoyer des commandes de test
python json_producer.py  # le producteur du module précédent
```

---

## Résumé des concepts

| Concept           | Description                                              |
|-------------------|----------------------------------------------------------|
| Stream processing | Traitement des données à leur arrivée (< 1s de latence) |
| Event time        | Timestamp dans le message (moment réel de l'événement)  |
| Processing time   | Heure système du worker                                  |
| Windowing         | Groupement temporel des événements                       |
| Stateless         | Traitement indépendant de l'historique                   |
| Stateful          | Traitement dépendant de l'état cumulé                    |
| Faust             | Bibliothèque Python de stream processing pour Kafka      |
| Agent             | Worker Faust qui traite un flux d'événements             |

**Module suivant :** [02-faust-python.md](./02-faust-python.md) — Faust en détail
