# Déploiement — 01 : Settings de production

## Le problème des settings multiples

En développement et en production, les configurations sont très différentes. La bonne pratique est de séparer les settings :

```
config/
└── settings/
    ├── __init__.py      ← Vide ou importe base
    ├── base.py          ← Settings communs
    ├── development.py   ← Settings dev (DEBUG=True, SQLite, etc.)
    └── production.py    ← Settings prod (DEBUG=False, PostgreSQL, etc.)
```

---

## Settings de base (base.py)

```python
# config/settings/base.py
from pathlib import Path
import os
from decouple import config  # pip install python-decouple

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =====================
# SÉCURITÉ
# =====================
SECRET_KEY = config('SECRET_KEY')  # Depuis les variables d'environnement
DEBUG = config('DEBUG', default=False, cast=bool)

# =====================
# APPLICATIONS
# =====================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
]

LOCAL_APPS = [
    'articles.apps.ArticlesConfig',
    'users.apps.UsersConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =====================
# MIDDLEWARE
# =====================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Fichiers statiques
    'corsheaders.middleware.CorsMiddleware',        # CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =====================
# URLS
# =====================
ROOT_URLCONF = 'config.urls'

# =====================
# TEMPLATES
# =====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =====================
# INTERNATIONALISATION
# =====================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# =====================
# FICHIERS STATIQUES
# =====================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Pour collectstatic
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =====================
# MEDIA (fichiers uploadés)
# =====================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =====================
# AUTH
# =====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
AUTH_USER_MODEL = 'auth.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================
# EMAIL
# =====================
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@monapp.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@monapp.com')
ADMINS = [('Admin', config('ADMIN_EMAIL', default='admin@monapp.com'))]

# =====================
# DRF
# =====================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# =====================
# JWT
# =====================
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## Settings de développement

```python
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# BDD SQLite pour le dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email dans la console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache en mémoire
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# DRF — Browsable API en dev
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# CORS — tout autoriser en dev
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (optionnel)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
```

---

## Settings de production

```python
# config/settings/production.py
from .base import *

# =====================
# SÉCURITÉ — CRITIQUE
# =====================
DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
# Ex: ALLOWED_HOSTS=monapp.com,www.monapp.com

# HTTPS obligatoire
SECURE_SSL_REDIRECT              = True
SECURE_HSTS_SECONDS              = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SECURE_PROXY_SSL_HEADER          = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True
SECURE_BROWSER_XSS_FILTER        = True
SECURE_CONTENT_TYPE_NOSNIFF      = True
X_FRAME_OPTIONS                  = 'DENY'

# =====================
# BASE DE DONNÉES
# =====================
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 60,  # Connexions persistantes
        'OPTIONS': {
            'sslmode': 'require',  # SSL obligatoire
        },
    }
}

# =====================
# CACHE Redis
# =====================
CACHES = {
    'default': {
        'BACKEND':  'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,
        },
        'TIMEOUT':    300,
        'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='monapp'),
    }
}

SESSION_ENGINE      = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# =====================
# EMAIL
# =====================
EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST      = config('EMAIL_HOST')
EMAIL_PORT      = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS   = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# =====================
# DRF — Production
# =====================
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    # PAS de BrowsableAPIRenderer en prod
]

# =====================
# CORS
# =====================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True

# =====================
# LOGGING
# =====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'fichier_erreurs': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/erreurs.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'fichier_erreurs'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'WARNING',  # Pas les requêtes SQL en prod
        },
    },
}
```

---

## Fichier .env

```bash
# .env (NE JAMAIS COMMITTER — dans .gitignore)
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
DEBUG=False
ALLOWED_HOSTS=monapp.com,www.monapp.com

# Base de données
DB_NAME=monapp_prod
DB_USER=monapp_user
DB_PASSWORD=mot_de_passe_fort
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1
CACHE_KEY_PREFIX=monapp_prod

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@monapp.com
EMAIL_HOST_PASSWORD=app_password_gmail

# CORS
CORS_ALLOWED_ORIGINS=https://monapp.com,https://www.monapp.com

# Admin
ADMIN_EMAIL=admin@monapp.com
DEFAULT_FROM_EMAIL=noreply@monapp.com
```

```python
# Lire depuis le bon fichier selon l'environnement
# config/settings/__init__.py
import os
env = os.environ.get('DJANGO_ENV', 'development')
if env == 'production':
    from .production import *
elif env == 'test':
    from .development import *
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
else:
    from .development import *
```

```bash
# Lancer en production
DJANGO_ENV=production python manage.py runserver

# Ou avec Gunicorn
DJANGO_ENV=production gunicorn config.wsgi:application
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `python manage.py check --deploy` sur les settings de production, avec la liste des recommandations de sécurité Django
> **Expliquer :** La commande `--deploy` vérifie la configuration de sécurité. Montrer et expliquer chaque warning : HSTS, HTTPS redirect, cookie secure, etc. Toutes ces configurations protègent contre des attaques courantes (MITM, XSS, clickjacking).

---

## Générer une SECRET_KEY sécurisée

```python
# Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# ou
import secrets
print(secrets.token_urlsafe(50))
```

```bash
# En ligne de commande
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Checklist avant mise en production

```bash
# 1. Vérifier la config
python manage.py check --deploy

# 2. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer le superuser (si premier déploiement)
python manage.py createsuperuser

# 5. Vérifier les permissions des dossiers
chmod 755 media/ logs/

# 6. Tester la connexion BDD
python manage.py dbshell
```

---

## Résumé — Variables d'environnement obligatoires

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Clé secrète Django (min 50 chars) |
| `DEBUG` | `False` en production |
| `ALLOWED_HOSTS` | Domaines autorisés |
| `DB_*` | Connexion PostgreSQL |
| `REDIS_URL` | Connexion Redis |
| `EMAIL_*` | Configuration SMTP |
| `CORS_ALLOWED_ORIGINS` | Origines CORS autorisées |

## Prochaine étape

Passez au module [02 — Docker](02-docker.md) pour containeriser votre application.
