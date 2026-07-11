# Avro et Schema Registry

## Pourquoi Avro ?

Jusqu'ici, nos messages étaient du JSON brut. C'est simple, mais pose plusieurs problèmes en production :

| Problème                  | Description                                                        |
|---------------------------|--------------------------------------------------------------------|
| Taille des messages       | JSON est verbeux (noms de champs répétés dans chaque message)      |
| Pas de validation         | N'importe quel JSON est accepté, même malformé                     |
| Évolution de schéma       | Comment gérer un champ renommé sans casser les consommateurs ?     |
| Pas de typage             | `"price": "29.99"` vs `"price": 29.99` — les deux sont valides   |
| Fragmentation des équipes | Producteur et consommateur doivent se synchroniser manuellement    |

**Apache Avro** résout ces problèmes : c'est un format de sérialisation binaire **avec schéma**, qui permet la validation et l'évolution contrôlée.

### Avro vs JSON vs Protobuf

| Critère              | JSON     | Avro (binaire) | Protobuf |
|----------------------|----------|----------------|----------|
| Taille message       | Grande   | Petite (~60%)  | Petite (~70%) |
| Lisibilité humaine   | Oui      | Non (binaire)  | Non      |
| Validation de schéma | Non      | Oui            | Oui      |
| Évolution de schéma  | Manuelle | Automatique    | Oui      |
| Popularité en Kafka  | Haute    | Très haute     | Haute    |

---

## Apache Avro : les bases

Un **schéma Avro** est un fichier JSON qui décrit la structure des données :

```json
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.ecommerce.events",
  "doc": "Événement déclenché lors de la création d'une commande",
  "fields": [
    {
      "name": "order_id",
      "type": "string",
      "doc": "Identifiant unique de la commande"
    },
    {
      "name": "customer_id",
      "type": "string"
    },
    {
      "name": "amount",
      "type": "double",
      "doc": "Montant total en euros"
    },
    {
      "name": "status",
      "type": {
        "type": "enum",
        "name": "OrderStatus",
        "symbols": ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
      },
      "default": "PENDING"
    },
    {
      "name": "created_at",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      }
    },
    {
      "name": "items",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            {"name": "product_id", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "unit_price", "type": "double"}
          ]
        }
      }
    },
    {
      "name": "metadata",
      "type": ["null", {"type": "map", "values": "string"}],
      "default": null,
      "doc": "Champs optionnels supplémentaires"
    }
  ]
}
```

### Types Avro fondamentaux

| Type Avro          | Python equivalent   | Exemple                                |
|--------------------|---------------------|----------------------------------------|
| `null`             | `None`              | `"type": "null"`                       |
| `boolean`          | `bool`              | `true`                                 |
| `int`              | `int` (32 bits)     | `42`                                   |
| `long`             | `int` (64 bits)     | `1705312800000`                        |
| `float`            | `float` (32 bits)   | `3.14`                                 |
| `double`           | `float` (64 bits)   | `3.141592653589793`                    |
| `string`           | `str`               | `"hello"`                              |
| `bytes`            | `bytes`             | champs binaires                        |
| `record`           | `dict`              | objet imbriqué                         |
| `array`            | `list`              | `[1, 2, 3]`                            |
| `map`              | `dict`              | `{"key": "value"}`                     |
| `enum`             | `str` (valeur)      | valeur parmi une liste fixe            |
| `union`            | multiple types      | `["null", "string"]` (optionnel)       |

---

## Schema Registry

Le **Schema Registry** est un service centralisé qui :
1. **Stocke** les schémas Avro (et JSON Schema, Protobuf)
2. **Versionne** les schémas (v1, v2, v3...)
3. **Valide** la compatibilité avant enregistrement
4. **Distribue** les schémas aux producteurs et consommateurs

### Fonctionnement avec Kafka

```
[Producer]
    │
    ├── 1. Récupère/enregistre le schéma dans Schema Registry
    │        GET/POST http://localhost:8081/subjects/orders.created-value/versions
    │
    ├── 2. Sérialise le message en Avro binaire
    │        [magic byte: 0x00][schema_id: 4 bytes][avro_bytes]
    │
    └── 3. Envoie dans Kafka

[Consumer]
    │
    ├── 1. Reçoit le message binaire
    ├── 2. Lit le schema_id (octets 1-4)
    ├── 3. Récupère le schéma depuis Schema Registry (mis en cache)
    └── 4. Désérialise le message Avro
```

### API REST du Schema Registry

```bash
# Lister tous les sujets (topics avec schémas)
curl http://localhost:8081/subjects

# Enregistrer un schéma
curl -X POST http://localhost:8081/subjects/orders.created-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{
    "schema": "{\"type\":\"record\",\"name\":\"OrderCreated\",\"fields\":[{\"name\":\"order_id\",\"type\":\"string\"}]}"
  }'

# Récupérer la dernière version d'un schéma
curl http://localhost:8081/subjects/orders.created-value/versions/latest

# Lister les versions d'un sujet
curl http://localhost:8081/subjects/orders.created-value/versions

# Vérifier la compatibilité avant d'enregistrer
curl -X POST http://localhost:8081/compatibility/subjects/orders.created-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}'
```

---

## Producteur Avro avec Schema Registry

```python
# avro_producer.py
import io
import json
import time
import struct
import requests
import fastavro
from confluent_kafka import Producer
from dataclasses import dataclass

# ─────────────────────────────────────────────
# Définition du schéma
# ─────────────────────────────────────────────
ORDER_SCHEMA = {
    "type": "record",
    "name": "OrderCreated",
    "namespace": "com.ecommerce.events",
    "fields": [
        {"name": "order_id", "type": "string"},
        {"name": "customer_id", "type": "string"},
        {"name": "amount", "type": "double"},
        {"name": "status", "type": "string", "default": "PENDING"},
        {"name": "created_at", "type": "long"},
        {
            "name": "items",
            "type": {
                "type": "array",
                "items": {
                    "type": "record",
                    "name": "OrderItem",
                    "fields": [
                        {"name": "product_id", "type": "string"},
                        {"name": "quantity", "type": "int"},
                        {"name": "unit_price", "type": "double"}
                    ]
                }
            }
        }
    ]
}

# ─────────────────────────────────────────────
# Client Schema Registry
# ─────────────────────────────────────────────
class SchemaRegistryClient:
    """Client léger pour le Schema Registry."""

    def __init__(self, url: str = "http://localhost:8081"):
        self.url = url
        self._schema_cache: dict[int, dict] = {}

    def register_schema(self, subject: str, schema: dict) -> int:
        """Enregistre un schéma et retourne son ID."""
        response = requests.post(
            f"{self.url}/subjects/{subject}/versions",
            headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
            json={"schema": json.dumps(schema)}
        )
        response.raise_for_status()
        schema_id = response.json()["id"]
        print(f"Schéma enregistré : subject={subject}, id={schema_id}")
        return schema_id

    def get_schema_by_id(self, schema_id: int) -> dict:
        """Récupère un schéma par son ID (avec cache)."""
        if schema_id in self._schema_cache:
            return self._schema_cache[schema_id]

        response = requests.get(f"{self.url}/schemas/ids/{schema_id}")
        response.raise_for_status()
        schema = json.loads(response.json()["schema"])
        self._schema_cache[schema_id] = schema
        return schema


# ─────────────────────────────────────────────
# Sérialisation Avro (format Confluent Wire Format)
# ─────────────────────────────────────────────
MAGIC_BYTE = b'\x00'  # Confluent Wire Format magic byte

def serialize_avro(record: dict, schema: dict, schema_id: int) -> bytes:
    """
    Sérialise un enregistrement en Avro selon le format Confluent Wire Format :
    [0x00][schema_id (4 bytes big-endian)][avro_bytes]
    """
    parsed_schema = fastavro.parse_schema(schema)

    buffer = io.BytesIO()
    # Magic byte
    buffer.write(MAGIC_BYTE)
    # Schema ID (4 bytes, big-endian)
    buffer.write(struct.pack('>I', schema_id))
    # Données Avro
    fastavro.schemaless_writer(buffer, parsed_schema, record)

    return buffer.getvalue()


def deserialize_avro(data: bytes, registry: SchemaRegistryClient) -> dict:
    """
    Désérialise un message Avro au format Confluent Wire Format.
    """
    if data[0:1] != MAGIC_BYTE:
        raise ValueError("Magic byte manquant — message non Avro")

    schema_id = struct.unpack('>I', data[1:5])[0]
    schema = registry.get_schema_by_id(schema_id)
    parsed_schema = fastavro.parse_schema(schema)

    buffer = io.BytesIO(data[5:])
    return fastavro.schemaless_reader(buffer, parsed_schema)


# ─────────────────────────────────────────────
# Producteur Avro
# ─────────────────────────────────────────────
class AvroProducer:
    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.registry = SchemaRegistryClient(schema_registry_url)
        self._schema_ids: dict[str, int] = {}

    def _get_schema_id(self, subject: str, schema: dict) -> int:
        """Récupère ou enregistre le schema_id pour un sujet."""
        if subject not in self._schema_ids:
            self._schema_ids[subject] = self.registry.register_schema(subject, schema)
        return self._schema_ids[subject]

    def produce(self, topic: str, record: dict, schema: dict, key: str = None):
        subject = f"{topic}-value"
        schema_id = self._get_schema_id(subject, schema)
        value_bytes = serialize_avro(record, schema, schema_id)

        self.producer.produce(
            topic=topic,
            key=key.encode('utf-8') if key else None,
            value=value_bytes,
            callback=lambda err, msg: (
                print(f"Erreur : {err}") if err
                else print(f"Livré | partition={msg.partition()}, offset={msg.offset()}")
            )
        )

    def flush(self):
        self.producer.flush()


# ─────────────────────────────────────────────
# Programme principal
# ─────────────────────────────────────────────
if __name__ == '__main__':
    avro_producer = AvroProducer(
        bootstrap_servers='localhost:9092',
        schema_registry_url='http://localhost:8081'
    )

    # Créer quelques commandes
    orders = [
        {
            "order_id": "ORD-001",
            "customer_id": "cust-42",
            "amount": 149.99,
            "status": "PENDING",
            "created_at": int(time.time() * 1000),
            "items": [
                {"product_id": "LAPTOP-X1", "quantity": 1, "unit_price": 149.99}
            ]
        },
        {
            "order_id": "ORD-002",
            "customer_id": "cust-13",
            "amount": 59.98,
            "status": "CONFIRMED",
            "created_at": int(time.time() * 1000),
            "items": [
                {"product_id": "BOOK-PY3", "quantity": 2, "unit_price": 29.99}
            ]
        }
    ]

    for order in orders:
        avro_producer.produce(
            topic='orders.avro',
            record=order,
            schema=ORDER_SCHEMA,
            key=order['customer_id']
        )

    avro_producer.flush()
    print("Commandes Avro envoyées.")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir Schema Registry UI dans Kafka UI (http://localhost:8080 > Schema Registry). Montrer le schéma `orders.avro-value` enregistré avec sa version et son ID. Cliquer sur le schéma pour afficher la structure complète.
> **Expliquer :** Expliquer le format Confluent Wire Format : les 5 premiers octets d'un message Avro. Montrer que dans Kafka UI, les messages Avro sont automatiquement décodés en JSON lisible grâce au Schema Registry intégré. Insister sur l'intérêt : les consommateurs n'ont pas besoin d'avoir le schéma localement.

---

## Consommateur Avro

```python
# avro_consumer.py
from confluent_kafka import Consumer
import json

# Réutiliser les fonctions définies dans avro_producer.py
# from avro_producer import deserialize_avro, SchemaRegistryClient

def run_avro_consumer():
    registry = SchemaRegistryClient('http://localhost:8081')

    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'avro-order-consumer',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
    })
    consumer.subscribe(['orders.avro'])

    print("Consommateur Avro démarré...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur : {msg.error()}")
                continue

            # Désérialisation Avro
            record = deserialize_avro(msg.value(), registry)

            print(
                f"Commande reçue | "
                f"order_id={record['order_id']} | "
                f"customer={record['customer_id']} | "
                f"montant={record['amount']:.2f}€ | "
                f"articles={len(record['items'])}"
            )

            consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

run_avro_consumer()
```

---

## Évolution de schéma

L'évolution de schéma est l'une des fonctionnalités les plus importantes de Avro + Schema Registry.

### Règles de compatibilité

Schema Registry supporte plusieurs modes de compatibilité :

| Mode                | Règle                                                    |
|---------------------|----------------------------------------------------------|
| `BACKWARD`          | Nouveau schéma peut lire les anciens messages (défaut)   |
| `FORWARD`           | Ancien schéma peut lire les nouveaux messages             |
| `FULL`              | Les deux directions (BACKWARD + FORWARD)                 |
| `NONE`              | Aucune vérification                                      |

### Modifications compatibles BACKWARD

```python
# ✅ Ajouter un champ avec valeur par défaut → BACKWARD compatible
ORDER_SCHEMA_V2 = {
    "type": "record",
    "name": "OrderCreated",
    "namespace": "com.ecommerce.events",
    "fields": [
        {"name": "order_id", "type": "string"},
        {"name": "customer_id", "type": "string"},
        {"name": "amount", "type": "double"},
        {"name": "status", "type": "string", "default": "PENDING"},
        {"name": "created_at", "type": "long"},
        {"name": "items", "type": {"type": "array", "items": {
            "type": "record", "name": "OrderItem",
            "fields": [
                {"name": "product_id", "type": "string"},
                {"name": "quantity", "type": "int"},
                {"name": "unit_price", "type": "double"}
            ]
        }}},
        # NOUVEAU CHAMP avec valeur par défaut ← OK !
        {
            "name": "discount_percent",
            "type": "double",
            "default": 0.0,
            "doc": "Pourcentage de remise appliqué (0.0 = pas de remise)"
        },
        # NOUVEAU CHAMP optionnel (union avec null) ← OK !
        {
            "name": "coupon_code",
            "type": ["null", "string"],
            "default": null
        }
    ]
}
```

### Modifications incompatibles (à éviter)

```python
# ❌ Supprimer un champ sans default → BACKWARD incompatible
# Les anciens messages n'auront pas ce champ et ça cassera

# ❌ Changer le type d'un champ → incompatible
# "amount": "string"  au lieu de "amount": "double"

# ❌ Renommer un champ → incompatible
# "customer_id" → "client_id"  (solution : utiliser "aliases")

# ✅ Renommer avec aliases → compatible
{
    "name": "client_id",
    "type": "string",
    "aliases": ["customer_id"]  # L'ancien nom est reconnu
}
```

### Configurer la compatibilité dans Schema Registry

```bash
# Définir la compatibilité pour un sujet spécifique
curl -X PUT http://localhost:8081/config/orders.avro-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility": "BACKWARD"}'

# Vérifier la configuration
curl http://localhost:8081/config/orders.avro-value
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Tenter d'enregistrer un schéma incompatible (supprimer un champ sans default) via l'API REST et montrer l'erreur retournée. Puis montrer l'enregistrement réussi d'un schéma compatible (ajout d'un champ avec default).
> **Expliquer :** Ce mécanisme empêche les producteurs de "casser" les consommateurs existants sans le savoir. En entreprise, c'est essentiel quand plusieurs équipes partagent les mêmes topics. Montrer l'historique des versions d'un schéma dans Kafka UI.

---

## Utiliser confluent-kafka avec Schema Registry natif

La bibliothèque `confluent-kafka` propose des sérialiseurs intégrés :

```python
# confluent_avro_producer.py
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
import time

SCHEMA_STR = json.dumps(ORDER_SCHEMA)  # Schéma défini précédemment

# Créer le client Schema Registry
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Créer les sérialiseurs
avro_serializer = AvroSerializer(
    schema_registry_client,
    SCHEMA_STR,
    # Fonction de conversion objet → dict (optionnel si déjà un dict)
    lambda obj, ctx: obj
)
string_serializer = StringSerializer('utf_8')

# Créer le producteur
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Produire un message
order = {
    "order_id": "ORD-100",
    "customer_id": "cust-99",
    "amount": 89.90,
    "status": "PENDING",
    "created_at": int(time.time() * 1000),
    "items": [{"product_id": "PROD-1", "quantity": 3, "unit_price": 29.97}]
}

producer.produce(
    topic='orders.avro',
    key=string_serializer("cust-99", SerializationContext('orders.avro', MessageField.KEY)),
    value=avro_serializer(order, SerializationContext('orders.avro', MessageField.VALUE)),
    on_delivery=lambda err, msg: print(f"Erreur : {err}" if err else f"OK offset={msg.offset()}")
)
producer.flush()
```

---

## Résumé

| Concept            | Description                                                  |
|--------------------|--------------------------------------------------------------|
| Avro               | Format binaire avec schéma — compact, typé, validé           |
| Schema Registry    | Registre centralisé des schémas avec versioning              |
| Wire Format        | `[0x00][schema_id][avro_bytes]` — format Confluent           |
| BACKWARD compat.   | Ajouter des champs avec default = modification sûre          |
| Union `["null", X]`| Rendre un champ optionnel                                    |
| Aliases            | Renommer un champ de façon compatible                        |

**Module suivant :** [Kafka-Streams/01-introduction.md](../Kafka-Streams/01-introduction.md) — Stream processing
