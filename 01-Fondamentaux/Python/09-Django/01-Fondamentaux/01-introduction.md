# 01 — Introduction à Django

## Qu'est-ce que Django ?

Django est un framework web Python haut niveau qui encourage le développement rapide et un design propre et pragmatique. Il suit le principe **"batteries included"** : tout ce dont vous avez besoin est inclus dans le framework.

### Historique

- Créé en 2003 par Adrian Holovaty et Simon Willison au journal Lawrence Journal-World
- Open source depuis 2005
- Version actuelle stable : **Django 4.2 LTS** (Long Term Support jusqu'en avril 2026)
- Django 5.x est aussi disponible (sans LTS)

### Pourquoi Django ?

| Avantage | Description |
|----------|-------------|
| Rapide | Conçu pour aller de l'idée à la mise en prod rapidement |
| Sécurisé | Protection CSRF, XSS, injection SQL par défaut |
| Scalable | Utilisé par Instagram, Pinterest, Disqus à grande échelle |
| Versatile | Sites web, API REST, applications temps réel |
| Communauté | Enormous écosystème de packages tiers |

---

## Le patron MVT (Model-View-Template)

Django utilise une variante du patron MVC appelée **MVT** :

```
Requête HTTP
     │
     ▼
  URL Router (urls.py)
     │
     ▼
  View (views.py)          ←→  Model (models.py)
     │                              │
     │                        Base de données
     ▼
  Template (*.html)
     │
     ▼
  Réponse HTTP
```

### Les trois composants

**Model** — La couche données
```python
# models.py
from django.db import models

class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
```

**View** — La couche logique
```python
# views.py
from django.shortcuts import render
from .models import Article

def liste_articles(request):
    articles = Article.objects.all()
    return render(request, 'articles/liste.html', {'articles': articles})
```

**Template** — La couche présentation
```html
<!-- articles/liste.html -->
{% for article in articles %}
  <h2>{{ article.titre }}</h2>
  <p>{{ article.contenu }}</p>
{% endfor %}
```

---

## Installation

### Prérequis

```bash
# Vérifier la version Python
python --version  # Python 3.10+ requis

# Vérifier pip
pip --version
```

### Créer un environnement virtuel

```bash
# Créer le venv
python -m venv venv

# Activer (Linux/macOS)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate

# Vérifier l'activation (le prompt change)
# (venv) $
```

### Installer Django

```bash
# Installation de base
pip install django

# Vérifier l'installation
python -m django --version
# 4.2.x

# Installer aussi DRF pour la suite
pip install djangorestframework

# Figer les dépendances
pip freeze > requirements.txt
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant l'activation du venv et la sortie de `python -m django --version`
> **Expliquer :** Insister sur l'importance des environnements virtuels — chaque projet doit avoir le sien pour isoler les dépendances. Montrer la différence entre `python` global et `python` dans le venv.

---

## Créer votre premier projet

### La commande `django-admin startproject`

```bash
# Créer le projet (convention : appeler le dossier config)
django-admin startproject config .
# Le point "." place les fichiers dans le dossier courant

# Structure créée :
# .
# ├── config/
# │   ├── __init__.py
# │   ├── asgi.py
# │   ├── settings.py
# │   ├── urls.py
# │   └── wsgi.py
# └── manage.py
```

### Rôle de chaque fichier

| Fichier | Rôle |
|---------|------|
| `manage.py` | CLI Django — toutes les commandes de gestion |
| `config/settings.py` | Configuration globale du projet |
| `config/urls.py` | Routeur principal — point d'entrée des URLs |
| `config/wsgi.py` | Interface WSGI pour le déploiement (Gunicorn) |
| `config/asgi.py` | Interface ASGI pour l'async (Channels, Daphne) |

### Lancer le serveur de développement

```bash
# Appliquer les migrations initiales (indispensable)
python manage.py migrate

# Lancer le serveur
python manage.py runserver

# Lancer sur un port spécifique
python manage.py runserver 8080

# Lancer pour être accessible depuis le réseau local
python manage.py runserver 0.0.0.0:8000
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur ouvert sur `http://127.0.0.1:8000/` montrant la page d'accueil Django ("The install worked successfully!")
> **Expliquer :** Décrire ce que fait Django par défaut. Montrer aussi la sortie du terminal avec les requêtes HTTP loggées (status 200, 404, etc.).

---

## Créer une application Django

Un projet Django est composé d'**applications**. Chaque application est un module Python autonome qui gère une fonctionnalité précise.

### La commande `startapp`

```bash
# Créer une application "articles"
python manage.py startapp articles

# Structure créée :
# articles/
# ├── __init__.py
# ├── admin.py        ← Enregistrement des modèles dans l'admin
# ├── apps.py         ← Configuration de l'application
# ├── migrations/     ← Fichiers de migration de la BDD
# │   └── __init__.py
# ├── models.py       ← Définition des modèles de données
# ├── tests.py        ← Tests unitaires
# └── views.py        ← Logique des vues
```

### Enregistrer l'application

```python
# config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Vos applications
    'articles',          # forme courte
    # ou
    # 'articles.apps.ArticlesConfig',  # forme complète (recommandée)
]
```

### Créer une vue simple

```python
# articles/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Bienvenue sur mon blog !</h1>")
```

### Créer les URLs de l'application

```python
# articles/urls.py  ← créer ce fichier
from django.urls import path
from . import views

app_name = 'articles'  # namespace pour les reverse URLs

urlpatterns = [
    path('', views.index, name='index'),
]
```

### Brancher les URLs dans le projet

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('articles/', include('articles.urls')),
]
```

---

## Le fichier settings.py en détail

```python
# config/settings.py

# Clé secrète — NE JAMAIS la committer en production
SECRET_KEY = 'django-insecure-xxxxxxxxxxxxxxxxxxxx'

# Mode debug — FALSE en production OBLIGATOIREMENT
DEBUG = True

# Hôtes autorisés — vide en dev, rempli en prod
ALLOWED_HOSTS = []

# Applications installées
INSTALLED_APPS = [...]

# Middlewares (traitement des requêtes/réponses)
MIDDLEWARE = [...]

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Langue et fuseau horaire
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Fichiers statiques (CSS, JS, images)
STATIC_URL = 'static/'

# Champ clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## La commande `manage.py`

```bash
# Commandes les plus utilisées
python manage.py runserver          # Lancer le serveur dev
python manage.py migrate            # Appliquer les migrations
python manage.py makemigrations     # Créer les fichiers de migration
python manage.py createsuperuser    # Créer un admin
python manage.py shell              # Shell Python interactif avec Django chargé
python manage.py startapp <nom>     # Créer une application
python manage.py collectstatic      # Collecter les fichiers statiques
python manage.py test               # Lancer les tests
python manage.py showmigrations     # Voir l'état des migrations
python manage.py dbshell            # Accès direct à la base de données
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec `python manage.py shell` ouvert, puis taper quelques commandes Python pour montrer l'accès au contexte Django (ex: `from django.conf import settings; print(settings.DEBUG)`)
> **Expliquer :** Le shell Django est un outil indispensable pour tester du code, explorer les modèles, et déboguer sans avoir à créer une vue.

---

## Structure recommandée d'un projet Django

Pour un projet professionnel, voici la structure conseillée :

```
monprojet/
├── config/                 ← Configuration du projet
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py        ← Settings communs
│   │   ├── development.py ← Settings dev
│   │   └── production.py  ← Settings prod
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   ← Toutes les applications
│   ├── articles/
│   ├── users/
│   └── comments/
├── static/                 ← Fichiers statiques globaux
├── media/                  ← Fichiers uploadés
├── templates/              ← Templates globaux
│   └── base.html
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
└── .env                    ← Variables d'environnement (dans .gitignore !)
```

---

## Résumé

- Django suit le patron **MVT** : Model, View, Template
- Un projet est composé de plusieurs **applications** autonomes
- La commande principale est `manage.py`
- En développement, `python manage.py runserver` suffit
- **Ne jamais** mettre `DEBUG = True` ni le `SECRET_KEY` en dur en production

## Prochaine étape

Passez au module [02 — Modèles](02-modeles.md) pour apprendre à définir vos données avec l'ORM Django.
