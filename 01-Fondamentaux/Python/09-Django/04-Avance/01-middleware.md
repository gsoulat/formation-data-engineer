# Avancé — 01 : Middleware

## Qu'est-ce qu'un Middleware ?

Un middleware est un composant qui s'intercale entre la requête HTTP et la vue Django. Il permet d'exécuter du code avant et/ou après le traitement de chaque requête.

```
Requête HTTP
     ↓
[Middleware 1] before
     ↓
[Middleware 2] before
     ↓
  Vue Django
     ↓
[Middleware 2] after
     ↓
[Middleware 1] after
     ↓
Réponse HTTP
```

---

## Middlewares Django intégrés

```python
# config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',        # Headers de sécurité
    'django.contrib.sessions.middleware.SessionMiddleware', # Gestion des sessions
    'django.middleware.common.CommonMiddleware',            # Slash final, etc.
    'django.middleware.csrf.CsrfViewMiddleware',           # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Attach user à request
    'django.contrib.messages.middleware.MessageMiddleware', # Messages flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # X-Frame-Options
]
```

L'**ordre** est important : les middlewares sont exécutés dans l'ordre de la liste pour les requêtes, et en ordre inverse pour les réponses.

---

## Créer un middleware simple

### Middleware fonctionnel (style modern)

```python
# config/middleware.py
import time
import logging

logger = logging.getLogger(__name__)

def middleware_timer(get_response):
    """Middleware mesurant le temps de traitement de chaque requête."""

    def middleware(request):
        # Code exécuté AVANT la vue
        debut = time.time()

        # Appel de la vue (et des middlewares suivants)
        response = get_response(request)

        # Code exécuté APRÈS la vue
        duree = (time.time() - debut) * 1000  # en ms
        logger.info(f"{request.method} {request.path} — {response.status_code} — {duree:.1f}ms")

        # Ajouter un header de durée
        response['X-Response-Time'] = f"{duree:.1f}ms"

        return response

    return middleware
```

### Middleware sous forme de classe

```python
class MiddlewareTimer:
    def __init__(self, get_response):
        self.get_response = get_response
        # Code exécuté une seule fois au démarrage (one-time config)
        logger.info("MiddlewareTimer initialisé")

    def __call__(self, request):
        # Code exécuté avant chaque requête
        debut = time.time()

        response = self.get_response(request)

        # Code exécuté après chaque requête
        duree = (time.time() - debut) * 1000
        response['X-Response-Time'] = f"{duree:.1f}ms"
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Optionnel : appelé juste avant la vue."""
        pass

    def process_exception(self, request, exception):
        """Optionnel : appelé si la vue lève une exception."""
        logger.error(f"Exception dans {request.path}: {exception}")
        return None  # Laisser Django gérer l'exception

    def process_template_response(self, request, response):
        """Optionnel : appelé si la vue retourne un TemplateResponse."""
        return response
```

---

## Enregistrer un middleware

```python
# config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'config.middleware.MiddlewareTimer',  # Votre middleware
    # ...
]
```

---

## Exemples pratiques

### Middleware de journalisation des requêtes

```python
# config/middleware.py
import json
import logging
import time

logger = logging.getLogger('api.access')

class JournalisationAPIMiddleware:
    """Log toutes les requêtes API avec les détails."""

    CORPS_MAX_TAILLE = 1000  # Ne pas logger les gros corps

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        debut = time.time()

        # Capturer le corps de la requête (avant que la vue le consume)
        corps_requete = ''
        if request.content_type == 'application/json' and request.body:
            try:
                corps = json.loads(request.body)
                corps_str = json.dumps(corps)[:self.CORPS_MAX_TAILLE]
                # Masquer les mots de passe
                if 'password' in corps:
                    corps['password'] = '***'
                corps_requete = json.dumps(corps)[:self.CORPS_MAX_TAILLE]
            except Exception:
                corps_requete = request.body[:self.CORPS_MAX_TAILLE].decode('utf-8', errors='replace')

        response = self.get_response(request)

        duree_ms = (time.time() - debut) * 1000

        log_data = {
            'method':    request.method,
            'path':      request.path,
            'status':    response.status_code,
            'duree_ms':  round(duree_ms, 1),
            'user':      str(request.user),
            'ip':        self._get_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
        }

        if request.path.startswith('/api/'):
            logger.info(json.dumps(log_data))

        return response

    def _get_ip(self, request):
        """Récupère l'IP réelle (derrière un proxy)."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
```

---

### Middleware de maintenance

```python
from django.http import HttpResponse
from django.conf import settings

class MaintenanceMiddleware:
    """Affiche une page de maintenance si activé dans les settings."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Laisser passer les admins
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)

            # Laisser passer certains IPs
            ip = request.META.get('REMOTE_ADDR')
            ips_autorisees = getattr(settings, 'MAINTENANCE_ALLOWED_IPS', [])
            if ip in ips_autorisees:
                return self.get_response(request)

            return HttpResponse(
                "<h1>Site en maintenance</h1><p>Revenez dans quelques minutes.</p>",
                status=503,
                content_type='text/html; charset=utf-8',
            )

        return self.get_response(request)
```

```python
# config/settings.py
MAINTENANCE_MODE = True  # ou False
MAINTENANCE_ALLOWED_IPS = ['127.0.0.1', '192.168.1.1']
```

---

### Middleware d'en-têtes de sécurité (API)

```python
class SecuriteAPIMiddleware:
    """Ajoute des headers de sécurité sur toutes les réponses API."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/api/'):
            response['X-Content-Type-Options']  = 'nosniff'
            response['X-Frame-Options']         = 'DENY'
            response['X-XSS-Protection']        = '1; mode=block'
            response['Referrer-Policy']         = 'strict-origin-when-cross-origin'
            # CORS (si pas déjà géré par django-cors-headers)
            response['Access-Control-Allow-Origin'] = 'https://monapp.com'

        return response
```

---

### Middleware CORS simple

```python
class CORSMiddleware:
    """Middleware CORS minimal (préférer django-cors-headers en prod)."""

    ORIGINES_AUTORISEES = [
        'http://localhost:3000',
        'https://monapp.com',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origine = request.META.get('HTTP_ORIGIN', '')

        # Requête preflight OPTIONS
        if request.method == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = HttpResponse()
            if origine in self.ORIGINES_AUTORISEES:
                response['Access-Control-Allow-Origin']  = origine
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response['Access-Control-Max-Age']       = '86400'
            return response

        response = self.get_response(request)

        if origine in self.ORIGINES_AUTORISEES:
            response['Access-Control-Allow-Origin'] = origine
            response['Vary'] = 'Origin'

        return response
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant les logs du `JournalisationAPIMiddleware` dans la console, avec le JSON structuré par requête (method, path, status, duree_ms, user)
> **Expliquer :** Ces logs sont essentiels pour monitorer une API en production. Montrer comment configurer le logging Django dans settings.py avec différents handlers (console, fichier, Sentry). En production, on envoie ces logs vers un ELK Stack (Elasticsearch + Logstash + Kibana) ou CloudWatch.

---

## Middleware avec `process_exception`

```python
import traceback
import json
import logging

logger = logging.getLogger(__name__)

class GestionErreurMiddleware:
    """Intercepte toutes les exceptions et retourne une réponse JSON propre."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Appelé quand une exception non gérée est levée dans une vue."""
        from django.http import JsonResponse

        # Logger l'erreur
        logger.error(
            f"Exception non gérée sur {request.method} {request.path}: {exception}",
            exc_info=True,
        )

        # En développement : afficher le traceback
        from django.conf import settings
        if settings.DEBUG:
            return None  # Laisser Django afficher la page d'erreur debug

        # En production : réponse JSON propre
        if request.path.startswith('/api/'):
            return JsonResponse(
                {'erreur': 'Une erreur interne est survenue.'},
                status=500,
            )

        return None  # Laisser Django gérer avec ses pages d'erreur (404.html, 500.html)
```

---

## Résumé

- Les middlewares s'intercalent entre la requête et la vue
- L'ordre dans `MIDDLEWARE` est important
- Style recommandé : classe avec `__init__(get_response)` et `__call__(request)`
- `process_view` : avant la vue
- `process_exception` : en cas d'exception
- `process_template_response` : si la vue retourne `TemplateResponse`
- Cas d'usage : logging, performance, sécurité, maintenance, CORS

## Prochaine étape

Passez au module [02 — Signaux](02-signals.md).
