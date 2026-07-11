# Avancé — 03 : Cache Django

## Pourquoi mettre en cache ?

Le cache stocke le résultat d'opérations coûteuses pour les servir directement sans recalcul :

```
Sans cache : Requête → BDD (20ms) → Calculs (50ms) → Rendu (30ms) → Réponse (100ms)
Avec cache : Requête → Cache (1ms) → Réponse (1ms)
```

---

## Backends de cache

```python
# config/settings.py

# 1. Mémoire locale (dev uniquement — perdu au redémarrage, pas partageable)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 2. Fichier (simple mais lent)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# 3. Redis (recommandé en production)
# pip install django-redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,  # Dégradation gracieuse si Redis down
        },
        'TIMEOUT': 300,  # 5 minutes par défaut
        'KEY_PREFIX': 'monapp',
    }
}

# 4. Memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

---

## API de cache bas niveau

```python
from django.core.cache import cache

# SET — stocker
cache.set('ma_cle', 'ma_valeur')
cache.set('ma_cle', 'ma_valeur', timeout=60)     # Expire dans 60 secondes
cache.set('ma_cle', 'ma_valeur', timeout=None)   # Ne jamais expirer
cache.set('ma_cle', {'id': 1, 'nom': 'test'})    # Objets sérialisables

# GET — lire
valeur = cache.get('ma_cle')               # None si absent
valeur = cache.get('ma_cle', default='')   # Valeur par défaut

# GET ou SET — pattern courant
valeur = cache.get_or_set('ma_cle', 'valeur_defaut', timeout=300)

# DELETE — supprimer
cache.delete('ma_cle')

# EXISTS
if cache.has_key('ma_cle'):  # noqa
    pass

# Opérations atomiques
cache.incr('compteur')          # Incrémenter (doit exister et être un int)
cache.decr('compteur')          # Décrémenter
cache.incr('compteur', delta=5) # Incrémenter de 5

# Opérations en masse (plus efficace pour Redis)
cache.set_many({'cle1': 'val1', 'cle2': 'val2'}, timeout=300)
cache.get_many(['cle1', 'cle2'])  # {'cle1': 'val1', 'cle2': 'val2'}
cache.delete_many(['cle1', 'cle2'])

# Tout effacer (DANGEREUX en production !)
cache.clear()
```

---

## Cacher les QuerySets

```python
from django.core.cache import cache
from .models import Article, Categorie

def get_articles_recents():
    """Récupère les articles récents depuis le cache ou la BDD."""
    cle = 'articles_recents_5'
    articles = cache.get(cle)

    if articles is None:
        # Cache miss : requête BDD
        articles = list(
            Article.objects.filter(statut='publie')
                          .select_related('auteur', 'categorie')
                          .order_by('-cree_le')[:5]
        )
        # Stocker en cache 10 minutes
        cache.set(cle, articles, timeout=600)

    return articles


def get_categories():
    """Cache les catégories avec le nombre d'articles."""
    return cache.get_or_set(
        'categories_avec_comptage',
        lambda: list(
            Categorie.objects.annotate(nb=Count('articles'))
                             .filter(nb__gt=0)
                             .order_by('nom')
        ),
        timeout=3600,  # 1 heure
    )
```

---

## Invalidation du cache

```python
# Invalider manuellement
def publier_article(article):
    article.statut = 'publie'
    article.save()
    # Invalider les caches concernés
    cache.delete('articles_recents_5')
    cache.delete(f'article_{article.pk}')
    cache.delete(f'article_slug_{article.slug}')


# Invalidation via signal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Article)
def invalider_cache_article(sender, instance, **kwargs):
    """Invalider les caches liés aux articles à chaque modification."""
    cache.delete('articles_recents_5')
    cache.delete('articles_mis_en_avant')
    cache.delete(f'article_{instance.pk}')
    cache.delete(f'article_slug_{instance.slug}')
    # Invalider la liste de la catégorie si elle existe
    if instance.categorie:
        cache.delete(f'articles_categorie_{instance.categorie.slug}')
```

---

## Décorateur `@cache_page` — Cacher une vue entière

```python
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator

# Cacher la vue 15 minutes
@cache_page(60 * 15)
def liste_articles(request):
    articles = Article.objects.filter(statut='publie')
    return render(request, 'articles/liste.html', {'articles': articles})


# Sur une CBV
@method_decorator(cache_page(60 * 15), name='dispatch')
class ArticleListView(ListView):
    model = Article
    template_name = 'articles/liste.html'


# Ne jamais mettre en cache (données personnalisées)
@never_cache
def tableau_de_bord(request):
    return render(request, 'dashboard.html', {'user': request.user})
```

---

## Décorateur `@cache_control` et `Vary`

```python
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

# Indiquer au navigateur de cacher 1 heure
@cache_control(max_age=3600, public=True)
def page_statique(request):
    return render(request, 'static_page.html')

# Varier le cache selon le header Accept-Language
@vary_on_headers('Accept-Language')
def page_i18n(request):
    return render(request, 'page.html')

# Varier selon le cookie (utilisateurs différents = cache différent)
@vary_on_cookie
def page_personnalisee(request):
    return render(request, 'perso.html')
```

---

## Cacher des fragments de template

```html
{% load cache %}

<!-- Cacher ce bloc 600 secondes avec la clé 'sidebar' -->
{% cache 600 sidebar %}
  <aside>
    {% for categorie in categories %}
      <a href="{{ categorie.get_absolute_url }}">{{ categorie.nom }}</a>
    {% endfor %}
  </aside>
{% endcache %}

<!-- Clé de cache personnalisée par utilisateur -->
{% cache 600 user_menu request.user.pk %}
  <nav>Bonjour {{ request.user.username }}</nav>
{% endcache %}

<!-- Clé composite -->
{% cache 300 article_tags article.pk %}
  {% for tag in article.tags.all %}
    <span>{{ tag.nom }}</span>
  {% endfor %}
{% endcache %}
```

---

## Cache pour les API DRF

```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache

class ArticleViewSet(viewsets.ModelViewSet):

    def list(self, request):
        """Liste avec cache."""
        # Clé de cache incluant les paramètres de filtre
        cle = f"articles_list_{request.query_params.urlencode()}"
        data = cache.get(cle)

        if data is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            cache.set(cle, data, timeout=300)  # 5 minutes
            return self.get_paginated_response(data)

        return Response(data)

    def retrieve(self, request, pk=None):
        """Détail avec cache."""
        cle = f"article_{pk}"
        data = cache.get(cle)

        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cle, data, timeout=600)  # 10 minutes

        return Response(data)

    @action(detail=False, methods=['get'], url_path='statistiques')
    @method_decorator(cache_page(60 * 60))  # 1 heure
    def statistiques(self, request):
        """Statistiques globales mises en cache 1 heure."""
        from django.db.models import Sum, Avg
        stats = Article.objects.aggregate(
            total=Count('id'),
            publies=Count('id', filter=Q(statut='publie')),
            vues_totales=Sum('nb_vues'),
        )
        return Response(stats)
```

---

## Sessions avec Redis

```python
# config/settings.py
# Stocker les sessions dans Redis (au lieu des cookies ou de la BDD)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'  # Utilise le cache Redis configuré

# Durée de vie de la session (en secondes)
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `redis-cli` avec `KEYS monapp:*` listant toutes les clés Django en cache, puis `TTL monapp:articles_recents_5` montrant le temps avant expiration, et `GET monapp:articles_recents_5` montrant la valeur sérialisée
> **Expliquer :** Redis CLI est l'outil de monitoring indispensable pour le cache. Montrer aussi `redis-cli monitor` qui affiche en temps réel toutes les commandes Redis reçues — utile pour vérifier que le cache est bien utilisé et qu'il n'y a pas de cache miss excessifs.

---

## Résumé

| Backend | Usage |
|---------|-------|
| `LocMemCache` | Développement |
| `FileBasedCache` | Petit site, simple |
| Redis via `django-redis` | Production (recommandé) |
| Memcached | Production (alternative) |

- `cache.set(clé, valeur, timeout)` / `cache.get(clé)` / `cache.delete(clé)`
- `@cache_page(secondes)` pour cacher une vue entière
- `{% cache seconds key %}` pour cacher un fragment de template
- Invalider le cache à chaque modification (signaux `post_save`/`post_delete`)
- Le cache ne doit jamais être la source de vérité — toujours vérifiable depuis la BDD

## Prochaine étape

Passez au module [Déploiement — Settings production](../Deploiement/01-settings-prod.md).
