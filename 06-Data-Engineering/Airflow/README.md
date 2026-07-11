# Formation Apache Airflow

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Comprendre l'architecture et les concepts fondamentaux d'Apache Airflow
- Créer et orchestrer des pipelines de données (DAGs) complexes
- Utiliser les opérateurs courants (Python, SQL, HTTP, fichiers)
- Maîtriser les mécanismes avancés : XCom, Variables, Connexions, branchement conditionnel
- Écrire des DAGs dynamiques et testables
- Déployer Airflow en production avec Docker ou Kubernetes

---

## Prérequis

- Python 3.8+ (maîtrise des fonctions, décorateurs, modules)
- Notions de base en SQL
- Docker et Docker Compose installés
- Connaissances basiques en ligne de commande Linux/macOS

---

## Structure de la formation

```
Airflow/
├── README.md                          ← Ce fichier
├── Fondamentaux/
│   ├── 01-introduction.md             ← Architecture, concepts clés, cas d'usage
│   ├── 02-installation.md             ← Docker Compose, configuration, exécuteurs
│   └── 03-premier-dag.md              ← Premiers pas avec les DAGs
├── Operateurs/
│   ├── 01-operateurs-python.md        ← PythonOperator, TaskFlow API
│   ├── 02-operateurs-sql.md           ← PostgresOperator, SQLExecuteQueryOperator
│   ├── 03-operateurs-fichiers.md      ← FileSensor, S3Operator
│   └── 04-operateurs-http.md          ← SimpleHttpOperator, HttpSensor
├── Concepts-Avances/
│   ├── 01-xcom.md                     ← Passage de données entre tâches
│   ├── 02-variables-connections.md    ← Variables et connexions Airflow
│   ├── 03-branching.md                ← Workflows conditionnels
│   └── 04-dynamic-dags.md             ← DAGs et tâches dynamiques
├── Bonnes-Pratiques/
│   ├── 01-idempotence.md              ← Idempotence, catchup, re-exécution
│   └── 02-tests-dags.md               ← Tests unitaires et validation
├── Deploiement/
│   └── 01-production.md               ← Kubernetes, CI/CD, supervision
└── exercices/
    ├── exercice-01-pipeline-etl.md    ← Pipeline ETL complet
    └── exercice-02-pipeline-ml.md     ← Pipeline ML avec MLflow
```

---

## Durée estimée

| Module | Durée |
|---|---|
| Fondamentaux | 3h |
| Opérateurs | 2h30 |
| Concepts avancés | 3h |
| Bonnes pratiques | 1h30 |
| Déploiement | 1h30 |
| Exercices pratiques | 3h |
| **Total** | **~14h** |

---

## Versions utilisées dans cette formation

| Outil | Version |
|---|---|
| Apache Airflow | 2.9.x |
| Python | 3.11 |
| PostgreSQL | 15 |
| Docker | 24+ |
| Docker Compose | 2.x |

---

## Ressources complémentaires

- [Documentation officielle Airflow](https://airflow.apache.org/docs/)
- [Airflow GitHub](https://github.com/apache/airflow)
- [Astronomer Registry (providers)](https://registry.astronomer.io/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
