# 02 — Installation et Configuration

## Options d'installation

Il existe plusieurs façons d'installer Airflow :

| Méthode | Usage | Complexité |
|---|---|---|
| `pip install apache-airflow` | Développement local rapide | Faible |
| Docker Compose officiel | Formation, dev, petits projets | Moyenne |
| Helm Chart (Kubernetes) | Production, scalabilité | Élevée |
| Astronomer (SaaS/on-prem) | Production managée | Faible (opérationnel) |

Dans cette formation, nous utilisons **Docker Compose** — c'est la méthode recommandée pour le développement et la formation.

---

## Installation avec Docker Compose

### Prérequis

```bash
# Vérifier Docker
docker --version
# Docker version 24.0.x ou supérieur

# Vérifier Docker Compose
docker compose version
# Docker Compose version 2.x

# Vérifier la mémoire disponible (minimum 4 Go recommandés)
docker info | grep -i memory
```

### Récupérer le fichier Docker Compose officiel

```bash
# Créer le répertoire de travail
mkdir ~/airflow-formation && cd ~/airflow-formation

# Télécharger le docker-compose.yaml officiel d'Airflow 2.9
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.9.0/docker-compose.yaml'
```

### Structure du projet

```bash
mkdir -p ./dags ./logs ./plugins ./config

# Ce fichier est nécessaire pour que le container ait les bons droits
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

L'arborescence doit ressembler à :

```
airflow-formation/
├── docker-compose.yaml
├── .env
├── dags/            ← Vos fichiers DAG Python
├── logs/            ← Logs des task instances
├── plugins/         ← Opérateurs/hooks personnalisés
└── config/          ← airflow.cfg personnalisé (optionnel)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal avec la commande `docker compose up airflow-init` en cours d'exécution, montrant les logs d'initialisation
> **Expliquer :** Que fait `airflow-init` : il crée les tables de la metadata DB, crée l'utilisateur admin par défaut, et prépare l'environnement. Montrer que c'est une opération one-shot.

---

### Initialisation et démarrage

```bash
# Initialiser la base de données (à faire une seule fois)
docker compose up airflow-init

# Démarrer tous les services en arrière-plan
docker compose up -d

# Vérifier que tout tourne
docker compose ps
```

Résultat attendu de `docker compose ps` :

```
NAME                          STATUS
airflow-formation-airflow-scheduler-1   Up (healthy)
airflow-formation-airflow-webserver-1   Up (healthy)
airflow-formation-airflow-triggerer-1   Up (healthy)
airflow-formation-airflow-worker-1      Up (healthy)
airflow-formation-postgres-1            Up (healthy)
airflow-formation-redis-1               Up (healthy)
```

### Accéder à l'interface web

```
URL : http://localhost:8080
Login : airflow
Password : airflow
```

---

## Anatomie du docker-compose.yaml

Voici les sections clés à comprendre :

```yaml
# docker-compose.yaml (extraits commentés)

version: '3'

x-airflow-common:
  # Image de base — peut être remplacée par une image custom
  &airflow-common
  image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.9.0}

  environment:
    # Type d'executor (LocalExecutor, CeleryExecutor, KubernetesExecutor)
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor

    # Connexion à la metadata DB
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow

    # Connexion au broker Celery (Redis ici)
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0

    # Clé de chiffrement des connexions (Fernet)
    AIRFLOW__CORE__FERNET_KEY: ''

    # Désactive le chargement des exemples par défaut
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'

  volumes:
    # Monte vos DAGs dans le container
    - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
    - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
    - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
    - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  redis:
    image: redis:latest
    # Sert de broker de messages pour Celery

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler

  airflow-worker:
    <<: *airflow-common
    command: celery worker

  airflow-triggerer:
    <<: *airflow-common
    command: triggerer
```

---

## Les Executors

L'Executor détermine **comment et où** les tâches sont exécutées.

### SequentialExecutor

```
Airflow Scheduler
      │
      └──► Tâche 1 (bloque jusqu'à la fin)
      └──► Tâche 2 (ensuite seulement)
      └──► Tâche 3
```

- Exécute **une seule tâche à la fois**
- Utilisé uniquement avec SQLite
- **Ne jamais utiliser en production**
- Utile uniquement pour des tests rapides

```ini
# airflow.cfg
[core]
executor = SequentialExecutor
```

### LocalExecutor

```
Airflow Scheduler
      ├──► Process 1 (Tâche A)
      ├──► Process 2 (Tâche B)  ← exécution parallèle
      └──► Process 3 (Tâche C)
```

- Utilise des **sous-processus locaux** sur la même machine que le Scheduler
- Supporte la **parallélisation** (configurable via `max_active_tasks_per_dag`)
- Nécessite PostgreSQL ou MySQL (pas SQLite)
- **Adapté pour le développement et les petits déploiements**

```ini
[core]
executor = LocalExecutor

[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost/airflow
```

Docker Compose simplifié pour LocalExecutor :

```yaml
# docker-compose-local.yaml
version: '3'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow

  airflow:
    image: apache/airflow:2.9.0
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: >-
        postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
    ports:
      - "8080:8080"
    command: >
      bash -c "airflow db init &&
               airflow users create --username airflow --password airflow
                 --firstname Admin --lastname User --role Admin
                 --email admin@example.com &&
               airflow scheduler & airflow webserver"
```

### CeleryExecutor

```
Airflow Scheduler
      │
      └──► Redis/RabbitMQ (queue)
               ├──► Worker 1 (machine A)
               ├──► Worker 2 (machine A)
               ├──► Worker 3 (machine B)   ← scalabilité horizontale
               └──► Worker 4 (machine B)
```

- Distribue les tâches sur des **workers Celery** (potentiellement sur plusieurs machines)
- Supporte la **scalabilité horizontale**
- Nécessite un **broker de messages** (Redis ou RabbitMQ)
- **Standard en production** pour les workloads importants

### KubernetesExecutor

```
Airflow Scheduler
      │
      └──► Kubernetes API
               ├──► Pod Task A (créé à la demande, détruit après)
               ├──► Pod Task B
               └──► Pod Task C
```

- Chaque tâche = un Pod Kubernetes éphémère
- **Isolation maximale** entre les tâches
- Scalabilité quasi illimitée
- Coûte plus cher en latence (création du pod ~30s)
- Adapté aux workloads Kubernetes natifs

---

## Configuration via airflow.cfg

Le fichier `airflow.cfg` (ou variables d'environnement `AIRFLOW__SECTION__KEY`) permet de personnaliser le comportement d'Airflow.

### Paramètres importants

```ini
[core]
# Répertoire des DAGs
dags_folder = /opt/airflow/dags

# Nombre maximum de tâches actives simultanément (tous DAGs confondus)
max_active_tasks_per_dag = 16

# Parallélisme global (toutes tâches, tous DAGs)
parallelism = 32

# Combien de DAG Runs actifs par DAG au maximum
max_active_runs_per_dag = 16

# Charger ou non les exemples Airflow
load_examples = False

[scheduler]
# Fréquence de scan du dossier dags (secondes)
dag_dir_list_interval = 30

# Nombre de threads du scheduler
parsing_processes = 2

[webserver]
# Port du webserver
web_server_port = 8080

# Nombre de workers Gunicorn
workers = 4

# Authentification
authenticate = True
auth_backends = airflow.api.auth.backend.basic_auth

[database]
# Connexion à la metadata DB
sql_alchemy_conn = postgresql+psycopg2://user:pass@host/dbname

# Nombre de connexions dans le pool
sql_alchemy_pool_size = 5
```

### Surcharge par variables d'environnement

Toutes les valeurs de `airflow.cfg` peuvent être surchargées par des variables d'environnement suivant ce pattern :

```
AIRFLOW__{SECTION}__{KEY}
```

Exemples :
```bash
# Équivalent à [core] load_examples = False
AIRFLOW__CORE__LOAD_EXAMPLES=False

# Équivalent à [webserver] web_server_port = 8080
AIRFLOW__WEBSERVER__WEB_SERVER_PORT=8080

# Connexion DB
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
```

C'est la méthode recommandée avec Docker Compose :

```yaml
environment:
  AIRFLOW__CORE__EXECUTOR: LocalExecutor
  AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
  AIRFLOW__CORE__PARALLELISM: '32'
  AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
```

---

## Installer des providers (packages supplémentaires)

Airflow utilise un système de **providers** — des packages pip séparés pour chaque intégration externe.

```bash
# Lister les providers installés
pip show apache-airflow-providers-google

# Providers courants
pip install apache-airflow-providers-postgres    # PostgreSQL
pip install apache-airflow-providers-amazon       # AWS (S3, Redshift...)
pip install apache-airflow-providers-google       # GCP (BigQuery, GCS...)
pip install apache-airflow-providers-http         # HTTP/REST
pip install apache-airflow-providers-slack        # Slack notifications
pip install apache-airflow-providers-dbt-cloud    # dbt Cloud
```

### Avec Docker — image custom

```dockerfile
# Dockerfile
FROM apache/airflow:2.9.0

# Installer des providers supplémentaires
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.7.1 \
    apache-airflow-providers-amazon==8.19.0 \
    apache-airflow-providers-http==4.9.1 \
    pandas==2.1.4 \
    scikit-learn==1.3.2
```

```yaml
# docker-compose.yaml — utiliser l'image custom
x-airflow-common:
  &airflow-common
  build: .    # au lieu de image: apache/airflow:2.9.0
```

```bash
# Rebuild l'image
docker compose build
docker compose up -d
```

---

## Commandes CLI essentielles

```bash
# Entrer dans un container Airflow
docker compose exec airflow-scheduler bash

# ---- Commandes DAGs ----
# Lister tous les DAGs
airflow dags list

# Déclencher manuellement un DAG
airflow dags trigger mon_dag

# Déclencher avec une date logique spécifique
airflow dags trigger mon_dag --exec-date 2024-01-15T00:00:00

# Tester un DAG (sans enregistrer en DB)
airflow dags test mon_dag 2024-01-15

# Mettre en pause/relancer un DAG
airflow dags pause mon_dag
airflow dags unpause mon_dag

# ---- Commandes Tasks ----
# Tester une tâche spécifique
airflow tasks test mon_dag ma_tache 2024-01-15

# Lister les tâches d'un DAG
airflow tasks list mon_dag

# ---- Commandes DB ----
# Initialiser la base de données
airflow db init

# Mettre à jour la base de données (après upgrade Airflow)
airflow db upgrade

# Réinitialiser la base de données (DANGER : efface tout)
airflow db reset

# ---- Commandes Variables ----
airflow variables set ma_variable "ma_valeur"
airflow variables get ma_variable

# ---- Commandes Connections ----
airflow connections list
airflow connections get ma_connexion
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec `docker compose ps` montrant tous les services en état "healthy", puis ouverture du navigateur sur http://localhost:8080
> **Expliquer :** Identifier chaque service dans la liste (scheduler, webserver, worker, postgres, redis). Expliquer que "healthy" signifie que le healthcheck Docker passe. Ouvrir l'interface et se connecter avec les identifiants par défaut.

---

## Vérification de l'installation

```bash
# Vérifier la version d'Airflow
docker compose exec airflow-scheduler airflow version

# Vérifier la santé des composants
curl http://localhost:8080/health

# Réponse attendue :
# {
#   "metadatabase": {"status": "healthy"},
#   "scheduler": {"status": "healthy", "latest_dag_heartbeat": "..."},
#   "triggerer": {"status": "healthy", "latest_triggerer_heartbeat": "..."}
# }
```

---

## Résolution des problèmes courants

### Le webserver ne démarre pas

```bash
# Voir les logs
docker compose logs airflow-webserver

# Problème courant : droits sur le dossier logs
chmod -R 777 ./logs

# Problème : UID mismatch
echo "AIRFLOW_UID=$(id -u)" > .env
docker compose down && docker compose up -d
```

### "DAG not found" après avoir créé un fichier

```bash
# Le scheduler scan les DAGs toutes les 30 secondes
# Attendre ou forcer le rechargement :
docker compose exec airflow-scheduler airflow dags reserialize

# Vérifier les erreurs de parsing :
docker compose exec airflow-scheduler airflow dags list-import-errors
```

### Erreur de connexion à la DB

```bash
# Vérifier que postgres est bien démarré
docker compose ps postgres

# Tester la connexion
docker compose exec airflow-scheduler airflow db check
```

---

## Points clés à retenir

1. **Docker Compose** est la méthode recommandée pour débuter
2. **LocalExecutor** pour le développement, **CeleryExecutor** pour la production simple, **KubernetesExecutor** pour Kubernetes
3. La configuration se fait via `airflow.cfg` ou variables d'environnement `AIRFLOW__SECTION__KEY`
4. Les **providers** sont des packages pip séparés pour chaque intégration
5. Le dossier `dags/` est **monté en volume** — tout fichier `.py` ajouté est automatiquement détecté
