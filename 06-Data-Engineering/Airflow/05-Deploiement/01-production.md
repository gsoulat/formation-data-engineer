# 01 — Déploiement en Production

## Vue d'ensemble des options de déploiement

| Option | Usage | Complexité | Scalabilité |
|---|---|---|---|
| Docker Compose | Dev, petites équipes | Faible | Limitée |
| Docker Swarm | Production simple | Moyenne | Modérée |
| Kubernetes (KubernetesExecutor) | Production, grandes équipes | Élevée | Illimitée |
| Astronomer (Cloud/On-prem) | Managé | Faible (opérationnel) | Élevée |
| AWS MWAA | AWS managé | Faible | Élevée |
| Google Cloud Composer | GCP managé | Faible | Élevée |

---

## Déploiement Kubernetes avec KubernetesExecutor

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                          │
│  ┌─────────────────┐    ┌──────────────────────────┐   │
│  │   Deployment    │    │       Deployment          │   │
│  │   Webserver     │    │        Scheduler          │   │
│  │  (1 replica)    │    │       (1 replica)         │   │
│  └────────┬────────┘    └──────────────┬────────────┘   │
│           │                            │                  │
│           └──────────────┬─────────────┘                 │
│                          │                                │
│                ┌─────────▼──────────┐                   │
│                │  PostgreSQL (StatefulSet)│               │
│                │  (Metadata DB)     │                   │
│                └────────────────────┘                   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Pods Tâches (créés dynamiquement)        │   │
│  │  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐   │   │
│  │  │Task A │  │Task B │  │Task C │  │Task D │   │   │
│  │  │(Pod)  │  │(Pod)  │  │(Pod)  │  │(Pod)  │   │   │
│  │  └───────┘  └───────┘  └───────┘  └───────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Helm Chart officiel

```bash
# Ajouter le repo Helm Airflow
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Installer Airflow avec le KubernetesExecutor
helm install airflow apache-airflow/airflow \
    --namespace airflow \
    --create-namespace \
    --set executor=KubernetesExecutor \
    --set webserver.service.type=LoadBalancer \
    -f values-production.yaml
```

### values-production.yaml

```yaml
# values-production.yaml

# Executor
executor: KubernetesExecutor

# Image personnalisée (avec nos providers installés)
images:
  airflow:
    repository: mon-registry.company.fr/airflow
    tag: "2.9.0-custom"
    pullPolicy: IfNotPresent

# Secrets Kubernetes pour la Fernet key et la DB
secret:
  - envName: AIRFLOW__CORE__FERNET_KEY
    secretName: airflow-secrets
    secretKey: fernet-key
  - envName: AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
    secretName: airflow-secrets
    secretKey: db-connection

# Configuration de la DB externe (PostgreSQL RDS, Cloud SQL...)
data:
  metadataConnection:
    user: airflow
    pass: ~    # géré par le secret
    host: airflow-db.company.fr
    port: 5432
    db: airflow
    sslmode: require

# Réplication du webserver
webserver:
  replicas: 2
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "2"
  service:
    type: ClusterIP

# Scheduler
scheduler:
  replicas: 1
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "4Gi"
      cpu: "2"

# Synchronisation des DAGs depuis Git
dags:
  gitSync:
    enabled: true
    repo: https://github.com/company/airflow-dags.git
    branch: main
    rev: HEAD
    depth: 1
    period: 30s   # Pull toutes les 30 secondes
    subPath: dags/

# PostgreSQL intégré (désactivé si DB externe)
postgresql:
  enabled: false

# Logs dans S3
logs:
  persistence:
    enabled: false  # Utiliser S3 à la place

# Variables d'environnement supplémentaires
env:
  - name: AIRFLOW__CORE__LOAD_EXAMPLES
    value: "false"
  - name: AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL
    value: "30"
  - name: AIRFLOW__CORE__PARALLELISM
    value: "64"
  - name: AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG
    value: "16"
```

---

## CI/CD pour les DAGs

### Stratégie de déploiement

```
Developer
    │
    ├──[git push] → GitHub/GitLab
    │                    │
    │              GitHub Actions
    │                    │
    │         ┌──────────┴──────────┐
    │         │                     │
    │     Lint/Tests          Build & Push
    │    (pytest, ruff)        Image Docker
    │         │                     │
    │         └──────────┬──────────┘
    │                    │ (si main branch)
    │              Helm upgrade
    │           (mise à jour Airflow)
    │
    └──[git-sync] → Airflow lit les DAGs depuis Git
                    (synchronisation automatique toutes les 30s)
```

### Pipeline CI/CD complet

```yaml
# .github/workflows/deploy-airflow.yml
name: Deploy Airflow DAGs

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/airflow

jobs:
  # ---- Job 1 : Lint et tests ----
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff apache-airflow==2.9.0 pytest pytest-mock
          pip install -r requirements.txt

      - name: Lint avec Ruff
        run: ruff check dags/ tests/

      - name: Tester les DAGs
        env:
          AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////tmp/airflow.db
          AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
        run: |
          airflow db init
          pytest tests/ -v

  # ---- Job 2 : Build et push de l'image Docker ----
  build-and-push:
    needs: lint-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ---- Job 3 : Déploiement Kubernetes ----
  deploy:
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBECONFIG }}

      - name: Deploy with Helm
        run: |
          helm upgrade airflow apache-airflow/airflow \
            --namespace airflow \
            --set images.airflow.tag=${{ github.sha }} \
            --wait \
            --timeout 10m \
            -f helm/values-production.yaml
```

---

## Dockerfile de production

```dockerfile
# Dockerfile
FROM apache/airflow:2.9.0-python3.11

USER root
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Installer les providers et dépendances
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir \
    -c https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.11.txt \
    -r /requirements.txt

# Copier le code des utilitaires (pas les DAGs — ils viennent de git-sync)
COPY --chown=airflow:root dags/utils/ /opt/airflow/dags/utils/
```

```txt
# requirements.txt
apache-airflow-providers-postgres==5.7.1
apache-airflow-providers-amazon==8.19.0
apache-airflow-providers-http==4.9.1
apache-airflow-providers-slack==8.4.0
apache-airflow-providers-dbt-cloud==3.5.0
pandas==2.1.4
pyarrow==14.0.2
scikit-learn==1.3.2
mlflow==2.9.2
```

---

## Supervision et Alertes

### Métriques Airflow avec Prometheus

```ini
# airflow.cfg
[metrics]
statsd_on = True
statsd_host = prometheus-statsd-exporter
statsd_port = 9125
statsd_prefix = airflow
```

### Alertes sur échec de DAG

```python
# dags/utils/alerting.py

def alerter_sur_echec(context):
    """
    Callback d'alerte Slack à appeler en cas d'échec.
    Usage : on_failure_callback=alerter_sur_echec dans le default_args
    """
    import json
    from airflow.providers.http.hooks.http import HttpHook

    ti = context['task_instance']
    dag = context['dag']
    exception = context.get('exception')

    message = {
        "text": f":red_circle: *Échec Pipeline Airflow*",
        "attachments": [{
            "color": "danger",
            "fields": [
                {"title": "DAG", "value": dag.dag_id, "short": True},
                {"title": "Tâche", "value": ti.task_id, "short": True},
                {"title": "Date", "value": context['ds'], "short": True},
                {"title": "Run ID", "value": context['run_id'], "short": False},
                {"title": "Erreur", "value": str(exception)[:500] if exception else "Inconnue", "short": False},
                {"title": "Logs", "value": ti.log_url, "short": False},
            ]
        }]
    }

    hook = HttpHook(method='POST', http_conn_id='slack_webhook')
    hook.run(
        endpoint='/hooks/TXXXXX/BXXXXX/XXXXXXXX',
        data=json.dumps(message),
        headers={'Content-Type': 'application/json'},
    )


# Utilisation dans les DAGs
default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': alerter_sur_echec,  # ← Alerte sur chaque tâche
}

with DAG(
    dag_id='pipeline_critique',
    default_args=default_args,
    on_failure_callback=alerter_sur_echec,  # ← Alerte sur le DAG Run entier
    ...
) as dag:
    pass
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une notification Slack reçue suite à l'échec d'une tâche Airflow — montrant les détails (DAG, tâche, erreur, lien vers les logs)
> **Expliquer :** Montrer que la notification contient directement le lien vers les logs Airflow (`ti.log_url`). Expliquer la différence entre `on_failure_callback` sur une tâche (se déclenche à chaque retry raté) vs sur le DAG (se déclenche uniquement quand le DAG Run échoue définitivement). Montrer comment simuler un échec pour tester l'alerte.

---

## Gestion des logs en production

### Logs vers S3

```ini
# airflow.cfg
[logging]
remote_logging = True
remote_base_log_folder = s3://mon-bucket-logs/airflow
remote_log_conn_id = aws_production
encrypt_s3_logs = True
```

```yaml
# Kubernetes — variables d'environnement
env:
  - name: AIRFLOW__LOGGING__REMOTE_LOGGING
    value: "true"
  - name: AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER
    value: "s3://mon-bucket-logs/airflow"
  - name: AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID
    value: "aws_production"
```

### Rotation des logs locaux

```ini
[logging]
# Durée de rétention des logs en jours
log_retention_days = 7

# Nettoyage automatique des DAG Runs anciens
max_dag_run_fetch_num = 1000
```

---

## Checklist de mise en production

```
Infrastructure
□ PostgreSQL externe (RDS, Cloud SQL, etc.) — jamais SQLite
□ Fernet key configurée et sauvegardée
□ Secrets dans Kubernetes Secrets ou Vault (jamais en clair dans les manifests)
□ Ingress HTTPS configuré pour le webserver
□ Monitoring (Prometheus + Grafana) connecté

DAGs
□ Tests unitaires passent (pytest)
□ Tests d'intégrité DAG passent (DagBag)
□ catchup configuré intentionnellement
□ Toutes les tâches idempotentes
□ on_failure_callback configuré pour les DAGs critiques
□ Timeouts définis sur les tâches longues
□ Retries configurés avec backoff exponentiel

CI/CD
□ Pipeline CI/CD qui valide les DAGs avant merge
□ Build de l'image Docker automatisé
□ Déploiement Helm automatisé sur la branche main
□ Environnements dev/staging/prod séparés

Opérations
□ Alertes Slack/PagerDuty sur les échecs critiques
□ Rotation des logs activée
□ Backup de la metadata DB planifié
□ Plan de disaster recovery documenté
□ Runbooks pour les incidents courants
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le tableau de bord Grafana montrant les métriques Airflow (nombre de DAG Runs actifs, tâches en échec, latence du Scheduler)
> **Expliquer :** Pointer les métriques clés : `airflow.scheduler.heartbeat` (le scheduler est vivant), `airflow.dag.*.task_instance_created_*` (throughput), `airflow.task_instance.failures` (taux d'erreur). Expliquer comment créer des alertes Grafana sur ces métriques.

---

## Points clés à retenir

1. **KubernetesExecutor** = scalabilité maximale, chaque tâche dans un Pod éphémère
2. **Helm Chart officiel** pour déployer Airflow sur Kubernetes
3. **git-sync** pour synchroniser les DAGs depuis Git automatiquement
4. Le CI/CD doit : linter → tester → build image → déployer
5. Configurer des **alertes Slack** via `on_failure_callback` pour les pipelines critiques
6. En production : PostgreSQL externe, Fernet key, logs distants (S3), monitoring Prometheus
