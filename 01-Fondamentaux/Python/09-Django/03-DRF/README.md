# Django REST Framework (DRF)

## Présentation

Django REST Framework est la bibliothèque de référence pour créer des API REST avec Django. Elle fournit :

- **Sérialiseurs** : conversion Python ↔ JSON + validation
- **Vues et ViewSets** : logique CRUD standardisée
- **Routeurs** : génération automatique des URLs
- **Authentification** : Token, Session, JWT
- **Permissions** : contrôle d'accès granulaire
- **Pagination** : gestion automatique des pages de résultats
- **Browsable API** : interface HTML pour explorer l'API

## Installation

```bash
pip install djangorestframework

# JWT (recommandé)
pip install djangorestframework-simplejwt

# Filtrage avancé
pip install django-filter
```

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',  # optionnel
]

REST_FRAMEWORK = {
    # Authentification par défaut
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Permissions par défaut
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Pagination par défaut
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Filtrage
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Rendu
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Retirer en prod
    ],
}
```

## Modules de cette section

| Module | Contenu |
|--------|---------|
| [01 — Introduction](01-introduction.md) | Premier endpoint, sérialiseurs basiques, routeurs |
| [02 — Sérialiseurs](02-serializers.md) | ModelSerializer, validation, imbrication |
| [03 — ViewSets](03-viewsets.md) | ViewSet, ModelViewSet, APIView |
| [04 — Authentification](04-authentification.md) | Token, JWT, session |
| [05 — Permissions](05-permissions.md) | Permissions intégrées et personnalisées |

## Architecture typique d'une API DRF

```
config/
├── urls.py              ← Inclut les URLs DRF

articles/
├── models.py            ← Modèles (inchangé)
├── serializers.py       ← NOUVEAU : sérialiseurs
├── views.py             ← Vues API (APIView, ViewSet)
├── urls.py              ← URLs API
├── permissions.py       ← Permissions personnalisées
└── filters.py           ← Filtres personnalisés
```
