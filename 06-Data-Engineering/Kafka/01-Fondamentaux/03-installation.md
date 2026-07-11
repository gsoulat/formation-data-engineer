# Installation et premier démarrage

## Approche retenue : Docker Compose

Pour ce cours, nous utilisons **Docker Compose**. C'est l'approche la plus rapide pour obtenir un environnement Kafka complet sans configurer manuellement Java, les variables d'environnement ou les fichiers de configuration.

Notre stack Docker comprend :
- **Kafka** (avec KRaft — sans ZooKeeper)
- **Schema Registry** — pour la gestion des schémas Avro
- **Kafka UI** — interface graphique pour explorer topics, messages et consumer groups

---

## Prérequis

```bash
# Vérifier Docker
docker --version
# Docker version 24.x.x ou supérieur requis

# Vérifier Docker Compose
docker compose version
# Docker Compose version v2.x.x ou supérieur requis

# Vérifier Python
python --version
# Python 3.10+ requis
```

---

## Fichier docker-compose.yml

Créez un fichier `docker-compose.yml` dans votre répertoire de travail :

```yaml
# docker-compose.yml
version: '3.8'

services:

  # ─────────────────────────────────────────────
  # Kafka Broker (mode KRaft, sans ZooKeeper)
  # ─────────────────────────────────────────────
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    container_name: kafka
    hostname: kafka
    ports:
      - "9092:9092"       # Port pour les clients externes (votre code Python)
      - "9093:9093"       # Port KRaft (communication interne)
    environment:
      # Mode KRaft (pas de ZooKeeper)
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT

      # Configuration des topics et logs
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_LOG_RETENTION_HOURS: 168           # 7 jours de rétention
      KAFKA_LOG_SEGMENT_BYTES: 1073741824      # 1 Go par segment

      # Identifiant du cluster (à générer une fois, rester constant)
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
    volumes:
      - kafka_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions.sh --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

  # ─────────────────────────────────────────────
  # Schema Registry (pour Avro)
  # ─────────────────────────────────────────────
  schema-registry:
    image: confluentinc/cp-schema-registry:7.6.0
    container_name: schema-registry
    hostname: schema-registry
    depends_on:
      kafka:
        condition: service_healthy
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: "kafka:9092"
      SCHEMA_REGISTRY_LISTENERS: "http://0.0.0.0:8081"
      SCHEMA_REGISTRY_DEBUG: "true"

  # ─────────────────────────────────────────────
  # Kafka UI (interface graphique)
  # ─────────────────────────────────────────────
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      kafka:
        condition: service_healthy
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_SCHEMAREGISTRY: http://schema-registry:8081
      DYNAMIC_CONFIG_ENABLED: "true"

volumes:
  kafka_data:
    driver: local
```

---

## Démarrage de l'environnement

```bash
# Démarrer tous les services en arrière-plan
docker compose up -d

# Vérifier que les conteneurs sont bien démarrés
docker compose ps
```

Résultat attendu :
```
NAME              IMAGE                                   STATUS
kafka             confluentinc/cp-kafka:7.6.0             Up (healthy)
schema-registry   confluentinc/cp-schema-registry:7.6.0   Up
kafka-ui          provectuslabs/kafka-ui:latest            Up
```

```bash
# Voir les logs en temps réel
docker compose logs -f kafka

# Voir les logs d'un service spécifique
docker compose logs kafka-ui
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `docker compose up -d` puis `docker compose ps` avec les 3 services en état "Up". Ensuite ouvrir http://localhost:8080 dans le navigateur et montrer la page d'accueil de Kafka UI avec le cluster "local" visible.
> **Expliquer :** Expliquer chaque service qui démarre, pourquoi on a choisi KRaft plutôt que ZooKeeper, et naviguer dans Kafka UI pour montrer l'interface : onglets Topics, Brokers, Consumer Groups, Schema Registry.

---

## Kafka UI — Exploration

Ouvrez http://localhost:8080 dans votre navigateur.

### Navigation

| Onglet             | Description                                          |
|--------------------|------------------------------------------------------|
| Dashboard          | Vue d'ensemble du cluster                            |
| Brokers            | Liste des brokers, métriques JVM                     |
| Topics             | Liste des topics, contenu des messages               |
| Consumer Groups    | Groupes actifs, lag par partition                    |
| Schema Registry    | Schémas Avro enregistrés                             |
| Kafka Connect      | Connecteurs (si Kafka Connect est déployé)           |

---

## Premiers pas avec la CLI Kafka

La CLI Kafka est disponible directement dans le conteneur :

```bash
# Se connecter au conteneur Kafka
docker exec -it kafka bash

# Une fois dans le conteneur, toutes les commandes kafka-* sont disponibles
```

### Gestion des topics

```bash
# Créer un topic
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas \
  --partitions 3 \
  --replication-factor 1

# Lister tous les topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Décrire un topic (partitions, leaders, replicas)
kafka-topics.sh --describe \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas

# Supprimer un topic
kafka-topics.sh --delete \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas
```

Exemple de sortie de `--describe` :
```
Topic: premiers-pas  TopicId: abc123  PartitionCount: 3  ReplicationFactor: 1
  Topic: premiers-pas  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
  Topic: premiers-pas  Partition: 1  Leader: 1  Replicas: 1  Isr: 1
  Topic: premiers-pas  Partition: 2  Leader: 1  Replicas: 1  Isr: 1
```

---

### Produire des messages depuis la CLI

```bash
# Producteur console interactif
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas

# Taper des messages, un par ligne, Enter pour envoyer
> Bonjour Kafka !
> Mon premier message
> {"user": "alice", "action": "login"}
# Ctrl+C pour quitter
```

```bash
# Produire avec une clé (séparateur : la virgule par défaut)
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas \
  --property "key.separator=:" \
  --property "parse.key=true"

# Format : clé:valeur
> user-42:{"action": "login", "timestamp": "2024-01-15T10:00:00"}
> user-13:{"action": "purchase", "item": "laptop"}
> user-42:{"action": "logout"}
```

---

### Consommer des messages depuis la CLI

```bash
# Consommer depuis le début (--from-beginning)
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas \
  --from-beginning

# Consommer seulement les nouveaux messages
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas

# Afficher la clé et la valeur
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas \
  --from-beginning \
  --property "print.key=true" \
  --property "key.separator= → "

# Consommer dans un consumer group
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic premiers-pas \
  --group mon-premier-groupe \
  --from-beginning
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Deux terminaux côte à côte : à gauche le producteur console envoyant des messages, à droite le consommateur console les recevant en temps réel.
> **Expliquer :** Montrer le flux en direct : taper un message dans le terminal producteur et le voir apparaître immédiatement dans le terminal consommateur. Insister sur la latence quasi-nulle (< 100ms). Puis ouvrir Kafka UI et montrer le message dans l'interface graphique.

---

### Gestion des consumer groups

```bash
# Lister tous les consumer groups
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list

# Décrire un groupe (voir le lag par partition)
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group mon-premier-groupe
```

Exemple de sortie :
```
GROUP                TOPIC          PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
mon-premier-groupe   premiers-pas   0          15              15              0
mon-premier-groupe   premiers-pas   1          12              12              0
mon-premier-groupe   premiers-pas   2          8               8               0
```

- **CURRENT-OFFSET** : dernier offset lu par le consommateur
- **LOG-END-OFFSET** : dernier offset disponible dans la partition
- **LAG** : retard du consommateur (0 = à jour)

```bash
# Réinitialiser les offsets (attention : irréversible !)
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group mon-premier-groupe \
  --topic premiers-pas \
  --reset-offsets \
  --to-earliest \
  --execute
```

---

## Installation des dépendances Python

```bash
# Quitter le conteneur Docker si vous y étiez
exit

# Dans votre environnement Python local
pip install confluent-kafka fastavro requests faust-streaming

# Ou avec un requirements.txt
```

Créez un fichier `requirements.txt` :

```txt
# requirements.txt
confluent-kafka==2.3.0
fastavro==1.9.4
requests==2.31.0
faust-streaming==0.10.14
pydantic==2.6.0
```

```bash
pip install -r requirements.txt
```

### Vérification de l'installation

```python
# test_connexion.py
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient

def test_connexion():
    """Teste la connexion au broker Kafka."""
    admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

    # Récupérer les métadonnées du cluster
    metadata = admin.list_topics(timeout=5)

    print(f"Connexion réussie !")
    print(f"Nombre de brokers : {len(metadata.brokers)}")
    print(f"Topics existants : {list(metadata.topics.keys())}")

if __name__ == "__main__":
    test_connexion()
```

```bash
python test_connexion.py
# Connexion réussie !
# Nombre de brokers : 1
# Topics existants : ['premiers-pas', '__consumer_offsets']
```

---

## Arrêter et nettoyer l'environnement

```bash
# Arrêter les services (garde les données)
docker compose stop

# Arrêter ET supprimer les conteneurs (garde les volumes)
docker compose down

# Arrêter ET supprimer tout (conteneurs + volumes = perte des données)
docker compose down -v
```

---

## Résumé des commandes essentielles

| Action                    | Commande                                                         |
|---------------------------|------------------------------------------------------------------|
| Démarrer l'env.           | `docker compose up -d`                                           |
| Créer un topic            | `kafka-topics.sh --create --bootstrap-server localhost:9092 ...` |
| Lister les topics         | `kafka-topics.sh --list --bootstrap-server localhost:9092`       |
| Produire (CLI)            | `kafka-console-producer.sh --bootstrap-server localhost:9092 ...`|
| Consommer (CLI)           | `kafka-console-consumer.sh --bootstrap-server localhost:9092 ...`|
| Voir le lag               | `kafka-consumer-groups.sh --describe --group ...`                |
| Interface graphique       | http://localhost:8080                                            |
| Schema Registry API       | http://localhost:8081                                            |

---

**Module suivant :** [Producers-Consumers/01-producer-python.md](../Producers-Consumers/01-producer-python.md)
