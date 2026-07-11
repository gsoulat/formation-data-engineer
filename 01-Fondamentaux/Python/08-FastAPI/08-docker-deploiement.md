# Module 08 — Docker et déploiement

## Sommaire
1. [Pourquoi Docker pour une API FastAPI ?](#1-pourquoi-docker-pour-une-api-fastapi-)
2. [Dockerfile optimisé](#2-dockerfile-optimisé)
3. [docker-compose avec PostgreSQL](#3-docker-compose-avec-postgresql)
4. [Variables d'environnement et secrets](#4-variables-denvironnement-et-secrets)
5. [Health checks](#5-health-checks)
6. [Configuration de production](#6-configuration-de-production)
7. [Multi-stage build](#7-multi-stage-build)
8. [CI/CD basique avec GitHub Actions](#8-cicd-basique-avec-github-actions)
9. [Déploiement sur un VPS](#9-déploiement-sur-un-vps)

---

## 1. Pourquoi Docker pour une API FastAPI ?

### Avantages

| Problème sans Docker | Solution avec Docker |
|---|---|
| "Ça marche sur ma machine" | Environnement identique partout |
| Gestion des dépendances complexe | Tout est dans l'image |
| Configuration manuelle du serveur | Infrastructure as code |
| Déploiement fragile | Déploiement reproductible |
| Rollback difficile | `docker pull image:v1.2` |

### Structure du projet

```
mon-projet/
├── app/
│   ├── main.py
│   └── ...
├── tests/
├── alembic/
├── alembic.ini
├── Dockerfile              ← Image de l'application
├── docker-compose.yml      ← Stack locale (app + DB)
├── docker-compose.prod.yml ← Override pour la production
├── .dockerignore           ← Fichiers à exclure
├── requirements.txt        ← Dépendances
└── .env                    ← Variables d'environnement (ne pas committer)
```

---

## 2. Dockerfile optimisé

### Version de base

```dockerfile
# Dockerfile
# Utiliser une image Python officielle slim (plus légère)
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    # Ne pas créer les fichiers .pyc
    PYTHONUNBUFFERED=1
    # Sortie non bufferisée (logs en temps réel)

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libpq-dev \
    # Bibliothèque PostgreSQL (pour psycopg2)
    gcc \
    # Compilateur C (pour certains packages)
    && rm -rf /var/lib/apt/lists/*
    # Nettoyer le cache apt (réduit la taille de l'image)

# Copier et installer les dépendances Python
# (Étape séparée pour profiter du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.dockerignore`

```
# .dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.git/
.gitignore
.env
.env.*
venv/
.venv/
env/
*.egg-info/
dist/
build/
.pytest_cache/
htmlcov/
.coverage
*.log
.DS_Store
Thumbs.db

# Documentation
*.md
docs/

# Tests (pas nécessaires dans l'image de production)
tests/
```

### `requirements.txt`

```
# requirements.txt
fastapi[standard]==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.36
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic-settings==2.5.0
python-dotenv==1.0.0
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant `docker build -t mon-api .` montrant les étapes de build
> **Expliquer :** Montrer les étapes du build (`Step 1/9`, etc.). Expliquer le cache Docker : si on relance sans modifier requirements.txt, les étapes jusqu'à pip install sont en cache (plus rapide). Modifier requirements.txt et remontrer que le cache est invalidé. Puis montrer `docker images` pour voir l'image créée avec sa taille.

---

## 3. docker-compose avec PostgreSQL

### `docker-compose.yml` (développement)

```yaml
# docker-compose.yml
version: '3.9'

services:
  # ==========================================
  # SERVICE : Base de données PostgreSQL
  # ==========================================
  db:
    image: postgres:16-alpine   # Image légère
    container_name: myapi_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-myuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-mypassword}
      POSTGRES_DB: ${POSTGRES_DB:-mydb}
    volumes:
      - postgres_data:/var/lib/postgresql/data   # Persistance des données
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # Script init (optionnel)
    ports:
      - "5432:5432"   # Exposé en dev pour accès direct (PgAdmin, psql...)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-myuser} -d ${POSTGRES_DB:-mydb}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ==========================================
  # SERVICE : API FastAPI
  # ==========================================
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapi_app
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-myuser}:${POSTGRES_PASSWORD:-mypassword}@db:5432/${POSTGRES_DB:-mydb}
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      DEBUG: "true"
    ports:
      - "8000:8000"
    volumes:
      - .:/app   # Hot reload en dev (monte le code local)
    depends_on:
      db:
        condition: service_healthy  # Attendre que PostgreSQL soit prêt
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # ==========================================
  # SERVICE : PgAdmin (optionnel, interface web PostgreSQL)
  # ==========================================
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: myapi_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - db
    profiles:
      - tools   # Lancer seulement avec: docker-compose --profile tools up

# ==========================================
# VOLUMES NOMMÉS
# ==========================================
volumes:
  postgres_data:
    driver: local
```

### Commandes essentielles

```bash
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f api

# Arrêter les services (sans supprimer les données)
docker-compose down

# Arrêter ET supprimer les volumes (reset complet)
docker-compose down -v

# Reconstruire l'image après modification du Dockerfile
docker-compose up -d --build

# Exécuter une commande dans un conteneur
docker-compose exec api bash
docker-compose exec api alembic upgrade head

# Lancer les migrations
docker-compose exec api alembic upgrade head

# Voir l'état des services
docker-compose ps

# Lancer seulement la DB
docker-compose up -d db
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant `docker-compose up -d` et `docker-compose logs -f`
> **Expliquer :** Lancer `docker-compose up -d`. Montrer les étapes : pull des images, build de l'API, démarrage. Puis `docker-compose logs -f` pour voir les logs des deux services en temps réel. Montrer le health check PostgreSQL (waiting..., puis healthy). Montrer `docker-compose ps` avec le status de chaque service. Ouvrir le navigateur sur `http://localhost:8000/docs` pour confirmer que l'API tourne.

---

## 4. Variables d'environnement et secrets

### Fichier `.env`

```bash
# .env — NE JAMAIS COMMITTER CE FICHIER
# Ajouter .env dans .gitignore

# Base de données
POSTGRES_USER=myuser
POSTGRES_PASSWORD=super_secret_password_123
POSTGRES_DB=mydb

# Application
SECRET_KEY=une-cle-tres-longue-et-aleatoire-generee-avec-openssl
DEBUG=false
APP_NAME="Mon API Production"

# Email (si applicable)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=monapi@gmail.com
SMTP_PASSWORD=mot_de_passe_app_google

# Logging
LOG_LEVEL=INFO
```

```bash
# .env.example — Committer ce fichier (valeurs factices)
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
SECRET_KEY=generate-with-openssl-rand-hex-32
DEBUG=false
```

```bash
# Générer une SECRET_KEY sécurisée
openssl rand -hex 32
# ou
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Utilisation avec Pydantic Settings

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Base de données
    database_url: str
    postgres_user: str = "postgres"
    postgres_password: str
    postgres_db: str = "mydb"

    # Sécurité
    secret_key: str
    access_token_expire_minutes: int = 30

    # Application
    app_name: str = "Mon API"
    debug: bool = False
    log_level: str = "INFO"

    # Computed property (construire l'URL DB)
    @property
    def full_database_url(self) -> str:
        if hasattr(self, 'database_url') and self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@db:5432/{self.postgres_db}"
        )

settings = Settings()
```

---

## 5. Health checks

Un health check est essentiel pour que l'orchestrateur (Docker, Kubernetes) sache si l'app est prête.

### Route health check dans FastAPI

```python
# app/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
import time

from app.database import get_db

router = APIRouter(tags=["Health"])

# Timestamp de démarrage
start_time = time.time()


@router.get("/health")
def health_check():
    """
    Health check basique — vérifie que l'application répond.
    Utilisé par les load balancers et orchestrateurs.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - start_time, 2),
    }


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Health check avec vérification de la base de données.
    Plus lent, mais vérifie la connectivité complète.
    """
    try:
        # Exécuter une requête simple
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check — vérifie que l'app est prête à recevoir du trafic.
    Différent du liveness check (qui vérifie que l'app est vivante).
    """
    checks = {}

    # Vérifier la DB
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Ajouter d'autres vérifications si nécessaire
    # checks["redis"] = check_redis()
    # checks["external_api"] = check_external_api()

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

### Health check dans Docker

```dockerfile
# Dans le Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

```yaml
# Dans docker-compose.yml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s     # Vérifier toutes les 30 secondes
      timeout: 10s      # Timeout de 10 secondes
      retries: 3        # 3 échecs avant de marquer unhealthy
      start_period: 10s # Attendre 10s avant la première vérification
```

---

## 6. Configuration de production

### Différences dev / production

| Aspect | Développement | Production |
|---|---|---|
| `--reload` | Oui | Non |
| Workers | 1 | CPU × 2 + 1 |
| Docs Swagger | Activées | Désactivées |
| `DEBUG` | True | False |
| DB | SQLite ou local PG | PG managé (RDS, CloudSQL...) |
| Secrets | `.env` local | Vault, AWS Secrets Manager |
| HTTPS | Non | Obligatoire |
| Logs | Console | Fichier / service de logs |

### `docker-compose.prod.yml`

```yaml
# docker-compose.prod.yml — Override pour la production
version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: production    # Multi-stage build (voir section 7)
    restart: always
    environment:
      DEBUG: "false"
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
    volumes: []  # Pas de montage de code en production
    command: >
      uvicorn app.main:app
      --host 0.0.0.0
      --port 8000
      --workers 4
      --no-access-log
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'

  # En production, la DB est souvent externe (RDS, etc.)
  # Mais si on la déploie soi-même :
  db:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports: []   # Ne pas exposer le port 5432 en production !
```

```bash
# Déployer en production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Script `entrypoint.sh`

```bash
#!/bin/bash
# entrypoint.sh — Script de démarrage du conteneur

set -e  # Arrêter si une commande échoue

echo "Démarrage de l'application..."
echo "Environnement : ${APP_ENV:-development}"

# Attendre que PostgreSQL soit prêt
echo "Attente de PostgreSQL..."
while ! pg_isready -h db -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" 2>/dev/null; do
    echo "PostgreSQL pas encore prêt, attente..."
    sleep 1
done
echo "PostgreSQL est prêt !"

# Lancer les migrations
echo "Application des migrations Alembic..."
alembic upgrade head
echo "Migrations terminées."

# Démarrer l'application
echo "Démarrage d'uvicorn..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "${WORKERS:-1}" \
    ${DEBUG:+--reload}
```

```dockerfile
# Dans le Dockerfile, utiliser l'entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

---

## 7. Multi-stage build

Les builds multi-stage permettent d'avoir une image de production plus légère.

```dockerfile
# Dockerfile (multi-stage)

# ==========================================
# Stage 1 : Builder (installe les dépendances)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer les dépendances de build
RUN apt-get update && apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances dans un venv
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# ==========================================
# Stage 2 : Development (avec outils de dev)
# ==========================================
FROM python:3.11-slim AS development

WORKDIR /app

# Copier les binaires PostgreSQL nécessaires
RUN apt-get update && apt-get install -y libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copier le venv depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Activer le venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dépendances de dev (pytest, etc.)
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ==========================================
# Stage 3 : Production (image finale légère)
# ==========================================
FROM python:3.11-slim AS production

WORKDIR /app

# Uniquement les bibliothèques runtime nécessaires
RUN apt-get update && apt-get install -y libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copier le venv depuis le builder (pas d'outils de compilation)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Créer un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copier uniquement le code de l'application
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser entrypoint.sh .

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
```

```bash
# Builder une image spécifique
docker build --target production -t mon-api:latest .
docker build --target development -t mon-api:dev .

# Vérifier la taille des images
docker images mon-api
# REPOSITORY   TAG        IMAGE ID       CREATED        SIZE
# mon-api      latest     abc123         2 minutes ago  180MB
# mon-api      dev        def456         3 minutes ago  450MB
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal pendant `docker build --target production` et la comparaison des tailles d'images
> **Expliquer :** Montrer le build multi-stage étape par étape. Puis `docker images` pour comparer les tailles dev vs production. Insister sur le fait que l'image de production ne contient pas les outils de compilation (gcc, etc.) ni les tests. Expliquer comment l'utilisateur non-root améliore la sécurité.

---

## 8. CI/CD basique avec GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ==========================================
  # JOB 1 : Tests
  # ==========================================
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Checkout du code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Installer les dépendances
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lancer les tests
        env:
          DATABASE_URL: postgresql://testuser:testpassword@localhost:5432/testdb
          SECRET_KEY: test-secret-key-not-for-production
        run: |
          pytest --cov=app --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  # ==========================================
  # JOB 2 : Build Docker (seulement sur main)
  # ==========================================
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Login Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build et push
        uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: true
          tags: |
            monuser/mon-api:latest
            monuser/mon-api:${{ github.sha }}
```

---

## 9. Déploiement sur un VPS

### Script de déploiement

```bash
#!/bin/bash
# deploy.sh — Déployer l'application sur le serveur

set -e

SERVER="user@mon-serveur.com"
APP_DIR="/opt/mon-api"

echo "Déploiement en cours..."

# 1. Push sur le serveur
ssh $SERVER "cd $APP_DIR && git pull origin main"

# 2. Reconstruire l'image
ssh $SERVER "cd $APP_DIR && docker-compose -f docker-compose.yml -f docker-compose.prod.yml build api"

# 3. Redémarrer sans downtime (si plusieurs réplicas)
ssh $SERVER "cd $APP_DIR && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps api"

# 4. Lancer les migrations
ssh $SERVER "cd $APP_DIR && docker-compose exec -T api alembic upgrade head"

echo "Déploiement terminé !"
```

### Nginx comme reverse proxy

```nginx
# /etc/nginx/sites-available/mon-api
server {
    listen 80;
    server_name api.mondomaine.com;

    # Rediriger HTTP vers HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.mondomaine.com;

    # Certificats SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.mondomaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.mondomaine.com/privkey.pem;

    # Proxy vers FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `FROM python:3.11-slim` | Image de base légère |
| `.dockerignore` | Exclure les fichiers inutiles |
| `docker-compose.yml` | Orchestrer app + DB + services |
| `depends_on: condition: service_healthy` | Attendre que la DB soit prête |
| `HEALTHCHECK` | Vérifier l'état du conteneur |
| Multi-stage build | Image de production plus légère |
| `docker-compose -f ... -f ...` | Combiner plusieurs compose files |
| `entrypoint.sh` | Migrations + démarrage automatiques |
| `USER appuser` | Ne pas tourner en root en production |

---

**Précédent** : [Module 07 — Tests](./07-tests.md)
**Suite** : [Exercice 01 — API Produits](./exercices/exercice-01-api-produits.md)
