# Déploiement — 02 : Docker

## Architecture cible

```
                    Internet
                       │
                  [Nginx :80/443]         ← Reverse proxy, SSL, fichiers statiques
                       │
              [Gunicorn :8000]            ← Serveur WSGI Python
                       │
              [Django Application]        ← Votre code
                       │
         ┌─────────────┴──────────────┐
    [PostgreSQL :5432]           [Redis :6379]
```

---

## Dockerfile

```dockerfile
# Dockerfile
# Étape 1 : Image de base Python slim
FROM python:3.11-slim

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1   # Pas de fichiers .pyc
ENV PYTHONUNBUFFERED=1          # Logs en temps réel (pas de buffer)

# Répertoire de travail dans le container
WORKDIR /app

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python d'abord (optimise le cache Docker)
COPY requirements/production.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput --settings=config.settings.production

# Créer un utilisateur non-root pour la sécurité
RUN addgroup --system django \
    && adduser --system --ingroup django django \
    && chown -R django:django /app

USER django

# Exposer le port
EXPOSE 8000

# Script de démarrage
COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Commande par défaut
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

---

## Script entrypoint.sh

```bash
#!/bin/sh
# docker/entrypoint.sh

set -e

# Attendre que PostgreSQL soit prêt
echo "Attente de PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "PostgreSQL disponible."

# Attendre Redis si configuré
if [ -n "$REDIS_URL" ]; then
  echo "Attente de Redis..."
  while ! nc -z redis 6379; do
    sleep 0.5
  done
  echo "Redis disponible."
fi

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate --noinput

# Créer un superuser si les variables sont définies
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL \
    2>/dev/null || echo "Superuser déjà existant."
fi

echo "Démarrage de l'application..."
exec "$@"
```

```bash
chmod +x docker/entrypoint.sh
```

---

## docker-compose.yml

```yaml
# docker-compose.yml
version: '3.9'

services:

  # ==================
  # Application Django
  # ==================
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: monapp:latest
    container_name: monapp_web
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - DJANGO_ENV=production
    volumes:
      - media_volume:/app/media
      - logs_volume:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - monapp_network
    expose:
      - "8000"

  # ==================
  # Nginx
  # ==================
  nginx:
    image: nginx:1.25-alpine
    container_name: monapp_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - certbot_conf:/etc/letsencrypt:ro
    depends_on:
      - web
    networks:
      - monapp_network

  # ==================
  # PostgreSQL
  # ==================
  postgres:
    image: postgres:15-alpine
    container_name: monapp_postgres
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - monapp_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================
  # Redis
  # ==================
  redis:
    image: redis:7-alpine
    container_name: monapp_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
    volumes:
      - redis_data:/data
    networks:
      - monapp_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================
  # Worker Celery (optionnel)
  # ==================
  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile
    image: monapp:latest
    container_name: monapp_celery
    restart: unless-stopped
    command: celery -A config worker -l info --concurrency=4
    env_file:
      - .env
    environment:
      - DJANGO_ENV=production
    volumes:
      - media_volume:/app/media
    depends_on:
      - postgres
      - redis
    networks:
      - monapp_network

# ==================
# Volumes
# ==================
volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  logs_volume:
  certbot_conf:

# ==================
# Réseau
# ==================
networks:
  monapp_network:
    driver: bridge
```

---

## Configuration Nginx

```nginx
# nginx/conf.d/monapp.conf

upstream django_app {
    server web:8000;
}

# Redirection HTTP → HTTPS
server {
    listen 80;
    server_name monapp.com www.monapp.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name monapp.com www.monapp.com;

    # Certificats SSL (Let's Encrypt)
    ssl_certificate     /etc/letsencrypt/live/monapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monapp.com/privkey.pem;

    # Configuration SSL sécurisée
    ssl_protocols             TLSv1.2 TLSv1.3;
    ssl_ciphers               ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache         shared:SSL:10m;

    # En-têtes de sécurité
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Taille max des uploads
    client_max_body_size 20M;

    # Fichiers statiques (servis directement par Nginx)
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Fichiers media
    location /media/ {
        alias /app/media/;
        expires 7d;
    }

    # Proxy vers Django
    location / {
        proxy_pass         http://django_app;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_redirect     off;
        proxy_read_timeout 120s;

        # WebSocket support (si nécessaire)
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
    }
}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `docker-compose up --build` avec tous les services qui démarrent : postgres, redis, web (avec le entrypoint qui attend PostgreSQL), nginx. Montrer les logs de chaque service dans des couleurs différentes
> **Expliquer :** L'ordre de démarrage est géré par `depends_on` avec `condition: service_healthy`. Les healthchecks garantissent que PostgreSQL est vraiment prêt (pas juste démarré) avant que Django tente de migrer. Montrer comment lire les logs : `docker-compose logs -f web`.

---

## Commandes Docker utiles

```bash
# ===============================
# Construction et démarrage
# ===============================
# Build et démarrer en arrière-plan
docker-compose up --build -d

# Démarrer sans rebuild
docker-compose up -d

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes (DANGER — perd les données)
docker-compose down -v

# ===============================
# Exécuter des commandes
# ===============================
# Shell dans le container web
docker-compose exec web bash

# Django shell
docker-compose exec web python manage.py shell

# Migrations
docker-compose exec web python manage.py migrate

# Créer superuser
docker-compose exec web python manage.py createsuperuser

# Collectstatic
docker-compose exec web python manage.py collectstatic

# ===============================
# Monitoring
# ===============================
# Logs en temps réel
docker-compose logs -f
docker-compose logs -f web      # Seulement le service web
docker-compose logs -f nginx    # Seulement nginx

# Status des containers
docker-compose ps

# Ressources utilisées
docker stats

# ===============================
# Base de données
# ===============================
# Accès psql
docker-compose exec postgres psql -U $DB_USER -d $DB_NAME

# Backup
docker-compose exec postgres pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME < backup.sql
```

---

## Fichier requirements structuré

```
requirements/
├── base.txt         ← Dépendances communes
├── development.txt  ← Outils de dev
└── production.txt   ← Production
```

```txt
# requirements/base.txt
django==4.2.11
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
django-filter==24.1
django-cors-headers==4.3.1
Pillow==10.2.0           # Pour ImageField
python-decouple==3.8     # Variables d'environnement
gunicorn==21.2.0         # Serveur WSGI
whitenoise==6.6.0        # Fichiers statiques
psycopg2-binary==2.9.9   # Driver PostgreSQL
django-redis==5.4.0      # Cache Redis
celery==5.3.6            # Tâches asynchrones (optionnel)
```

```txt
# requirements/development.txt
-r base.txt
django-debug-toolbar==4.3.0
pytest-django==4.8.0
factory-boy==3.3.0
```

```txt
# requirements/production.txt
-r base.txt
sentry-sdk==1.40.6       # Monitoring des erreurs
python-json-logger==2.0.7 # Logs JSON structurés
```

---

## docker-compose.override.yml (développement)

```yaml
# docker-compose.override.yml — Utilisé automatiquement en dev
version: '3.9'

services:
  web:
    build:
      context: .
    command: python manage.py runserver 0.0.0.0:8000
    environment:
      - DJANGO_ENV=development
    volumes:
      - .:/app        # Montage du code source — rechargement à chaud
    ports:
      - "8000:8000"   # Accès direct sans Nginx en dev

  postgres:
    ports:
      - "5432:5432"   # Accès direct depuis l'IDE en dev

  redis:
    ports:
      - "6379:6379"   # Accès depuis redis-cli en dev
```

```bash
# Dev : utilise docker-compose.yml + docker-compose.override.yml
docker-compose up

# Prod : utilise seulement docker-compose.yml
docker-compose -f docker-compose.yml up -d
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur ouvert sur `http://localhost` (port 80 via Nginx) montrant l'API Django qui répond, puis l'interface admin sur `/admin/`. Ouvrir aussi Docker Desktop ou `docker-compose ps` pour montrer tous les containers en état "Up"
> **Expliquer :** Expliquer la différence entre le port exposé (`ports`) et le port interne (`expose`). En production, seul Nginx expose les ports 80/443 vers l'extérieur. Django et Redis ne sont accessibles qu'au sein du réseau Docker interne `monapp_network`.

---

## Résumé

| Composant | Image | Rôle |
|-----------|-------|------|
| Django | Custom (Dockerfile) | Application principale |
| Gunicorn | Inclus dans Django | Serveur WSGI (remplace `runserver`) |
| Nginx | `nginx:1.25-alpine` | Reverse proxy, SSL, statiques |
| PostgreSQL | `postgres:15-alpine` | Base de données |
| Redis | `redis:7-alpine` | Cache + sessions |

- `entrypoint.sh` : attendre PostgreSQL, migrer, démarrer
- `docker-compose.override.yml` : configuration dev (volumes code, ports directs)
- `docker-compose -f docker-compose.yml up -d` : uniquement prod
- Toujours utiliser des volumes nommés pour persister les données PostgreSQL et Redis
- Le `.env` ne doit jamais être commité dans git
