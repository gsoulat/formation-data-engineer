# Formation Apache Kafka

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Comprendre l'architecture et les concepts fondamentaux d'Apache Kafka
- Produire et consommer des messages en Python avec gestion des erreurs
- Utiliser Avro et le Schema Registry pour la sérialisation des données
- Implémenter du stream processing avec Faust
- Appliquer les patterns Event Sourcing et CDC (Change Data Capture)
- Intégrer Kafka avec Apache Spark Structured Streaming

## Prérequis

- Python 3.10+
- Docker et Docker Compose installés
- Notions de bases de données relationnelles
- Connaissances de base en Python (classes, async/await apprécié)

## Structure du cours

```
Kafka/
├── README.md                          ← Ce fichier
├── Fondamentaux/
│   ├── 01-introduction.md             ← Qu'est-ce que Kafka, cas d'usage
│   ├── 02-architecture.md             ← Brokers, topics, partitions, offsets
│   └── 03-installation.md             ← Docker Compose, premiers pas
├── Producers-Consumers/
│   ├── 01-producer-python.md          ← Produire des messages en Python
│   ├── 02-consumer-python.md          ← Consommer, groupes, commit manuel
│   └── 03-avro-schema-registry.md     ← Avro, Schema Registry, évolution
├── Kafka-Streams/
│   ├── 01-introduction.md             ← Kafka Streams vs Faust vs KSQL
│   └── 02-faust-python.md             ← Stream processing avec Faust
├── Patterns/
│   ├── 01-event-sourcing.md           ← Event Sourcing avec Kafka
│   └── 02-cdc.md                      ← CDC avec Debezium
├── Integration/
│   └── 01-kafka-spark.md              ← Kafka + Spark Structured Streaming
└── exercices/
    ├── exercice-01-producer-consumer.md   ← Exercice e-commerce events
    └── exercice-02-stream-processing.md  ← Agrégation temps réel avec Faust
```

## Environnement de travail

Tous les exemples de ce cours utilisent Docker Compose. Le fichier de configuration
se trouve dans `Fondamentaux/03-installation.md`.

### Lancer l'environnement

```bash
# Depuis le répertoire contenant votre docker-compose.yml
docker compose up -d

# Vérifier que tout est démarré
docker compose ps
```

### Services disponibles

| Service         | Port  | URL                        |
|-----------------|-------|----------------------------|
| Kafka Broker    | 9092  | localhost:9092             |
| Zookeeper       | 2181  | localhost:2181             |
| Kafka UI        | 8080  | http://localhost:8080      |
| Schema Registry | 8081  | http://localhost:8081      |

### Installer les dépendances Python

```bash
pip install confluent-kafka fastavro requests faust-streaming
```

## Ordre de lecture recommandé

1. `Fondamentaux/01-introduction.md` — Comprendre le contexte
2. `Fondamentaux/02-architecture.md` — Maîtriser les concepts
3. `Fondamentaux/03-installation.md` — Mettre en place l'environnement
4. `Producers-Consumers/01-producer-python.md` — Premier code
5. `Producers-Consumers/02-consumer-python.md` — Recevoir des messages
6. `Producers-Consumers/03-avro-schema-registry.md` — Sérialisation avancée
7. `Kafka-Streams/01-introduction.md` — Introduction au stream processing
8. `Kafka-Streams/02-faust-python.md` — Faust en pratique
9. `Patterns/01-event-sourcing.md` — Patterns architecturaux
10. `Patterns/02-cdc.md` — CDC avec Debezium
11. `Integration/01-kafka-spark.md` — Intégration Spark
12. `exercices/` — Mise en pratique

## Durée estimée

| Module                  | Durée   |
|-------------------------|---------|
| Fondamentaux            | 3h      |
| Producers / Consumers   | 3h      |
| Kafka Streams / Faust   | 2h      |
| Patterns                | 2h      |
| Intégration Spark       | 1h30    |
| Exercices               | 3h      |
| **Total**               | **~15h**|
