# DRF — 05 : Permissions

## Concept

Les permissions DRF contrôlent l'accès aux vues et aux objets. Elles s'exécutent après l'authentification :

```
Requête → Authentification ("Qui êtes-vous ?") → Permission ("Avez-vous le droit ?") → Vue
```

---

## Permissions intégrées

```python
from rest_framework.permissions import (
    AllowAny,            # Tout le monde (y compris anonymes)
    IsAuthenticated,     # Utilisateurs connectés seulement
    IsAdminUser,         # Utilisateurs avec is_staff=True
    IsAuthenticatedOrReadOnly,  # GET sans auth, POST/PUT/DELETE avec auth
    DjangoModelPermissions,     # Suit les permissions Django (add/change/delete)
    DjangoObjectPermissions,    # Idem au niveau objet
)
```

### Configuration globale

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Surcharge par vue

```python
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Surcharge le global

class ArticlePublicView(APIView):
    permission_classes = [AllowAny]         # Public

class AdminView(APIView):
    permission_classes = [IsAdminUser]      # Staff seulement
```

### Permission conditionnelle selon l'action

```python
class ArticleViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        """Permissions différentes selon l'action."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated()]
        # update, partial_update, destroy
        return [IsAuthenticated(), EstAuteurOuAdmin()]
```

---

## Créer des permissions personnalisées

### Permission au niveau vue

```python
# articles/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class EstStaff(BasePermission):
    """Seuls les utilisateurs staff peuvent accéder."""
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class LectureSeuleSinonAuthentifie(BasePermission):
    """Lecture libre, écriture réservée aux authentifiés."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_authenticated


class APermission(BasePermission):
    """Vérifie une permission Django spécifique."""
    message = "Vous n'avez pas la permission nécessaire."

    def has_permission(self, request, view):
        return request.user.has_perm('articles.can_publish')
```

### Permission au niveau objet

```python
class EstAuteurOuReadOnly(BasePermission):
    """
    Permission au niveau objet :
    - GET/HEAD/OPTIONS : tout le monde
    - POST/PUT/PATCH/DELETE : auteur ou staff
    """
    message = "Seul l'auteur peut modifier cet article."

    def has_permission(self, request, view):
        # Toujours appelée en premier
        return True  # Déléguer au niveau objet

    def has_object_permission(self, request, view, obj):
        # Appelée seulement pour retrieve, update, partial_update, destroy
        if request.method in SAFE_METHODS:
            return True
        # L'auteur ou un admin peut modifier/supprimer
        return obj.auteur == request.user or request.user.is_staff


class ProprietaireOuAdmin(BasePermission):
    """L'objet doit appartenir à l'utilisateur ou l'utilisateur doit être admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # Chercher l'attribut 'user' ou 'auteur' sur l'objet
        owner = getattr(obj, 'user', None) or getattr(obj, 'auteur', None)
        return owner == request.user
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman montrant deux requêtes DELETE identiques : une avec le token de l'auteur (204 No Content) et une avec le token d'un autre utilisateur (403 Forbidden avec `{"detail": "Seul l'auteur peut modifier cet article."}`)
> **Expliquer :** `has_permission()` est appelée pour toutes les requêtes, `has_object_permission()` seulement pour les actions sur un objet spécifique (retrieve, update, destroy). Le message `message` est retourné dans la réponse 403.

---

## Combiner les permissions

```python
# Toutes les permissions doivent être True (AND logique par défaut)
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, EstAuteurOuReadOnly]

# Créer un opérateur OR
from rest_framework.permissions import BasePermission

class EstAuteurOuAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.auteur == request.user or request.user.is_staff
```

### Opérateurs logiques (DRF >= 3.9)

```python
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# OU : l'un ou l'autre
permission_classes = [IsAuthenticated | IsAdminUser]

# ET : les deux
permission_classes = [IsAuthenticated & IsAdminUser]

# NOT
permission_classes = [~IsAdminUser]

# Combinaison complexe
permission_classes = [(IsAuthenticated & IsAdminUser) | (IsAuthenticated & EstAuteurOuReadOnly)]
```

---

## Permissions au niveau de l'objet : utilisation

```python
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, EstAuteurOuReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # Appelle check_object_permissions()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # get_object() appelle automatiquement check_object_permissions()
    # Pour les actions manuelles, l'appeler explicitement :
    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        article = self.get_object()  # Vérifie les permissions objet
        # ...
```

---

## Permissions Django (DjangoModelPermissions)

```python
# Suit le système de permissions Django :
# articles.add_article → POST
# articles.change_article → PUT/PATCH
# articles.delete_article → DELETE
# articles.view_article → GET (optionnel)

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

Attribuer des permissions dans l'admin Django :
- Users > Choisir un utilisateur > Permissions utilisateur
- Ajouter : `articles | article | Can add article`

```python
# Créer des permissions personnalisées sur le modèle
class Article(models.Model):
    class Meta:
        permissions = [
            ('can_publish',  'Peut publier des articles'),
            ('can_feature',  'Peut mettre en avant des articles'),
            ('view_metrics', 'Peut voir les statistiques'),
        ]
```

```bash
python manage.py migrate  # Crée les permissions en BDD
```

---

## Throttling (limitation de requêtes)

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',       # 100 requêtes/jour pour les anonymes
        'user': '1000/day',      # 1000 requêtes/jour par utilisateur
    },
}
```

### Throttling personnalisé

```python
# config/throttling.py
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """Limite les rafales : 10 requêtes/minute."""
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    """Limite globale : 1000 requêtes/jour."""
    scope = 'sustained'
```

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'config.throttling.BurstRateThrottle',
        'config.throttling.SustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'burst':     '10/min',
        'sustained': '1000/day',
    },
}
```

```python
# Surcharge par vue
class ArticlePublicationView(APIView):
    throttle_classes = [BurstRateThrottle]
```

---

## Exemple complet : système de rôles

```python
# articles/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class EstModerateur(BasePermission):
    """Vérifie que l'utilisateur est dans le groupe 'Moderateurs'."""
    message = "Accès réservé aux modérateurs."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.groups.filter(name='Moderateurs').exists() or request.user.is_staff)
        )


class PeutPublier(BasePermission):
    message = "Vous n'avez pas la permission de publier."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm('articles.can_publish') or request.user.is_staff


class ArticlePermission(BasePermission):
    """
    Logique complète :
    - GET (liste/détail) : tout le monde pour les publiés
    - POST (créer) : utilisateurs authentifiés
    - PUT/PATCH : auteur ou modérateur
    - DELETE : auteur ou staff
    """
    message = "Action non autorisée."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # Seuls les articles publiés sont visibles par les non-authentifiés
            if not request.user.is_authenticated:
                return obj.statut == 'publie'
            return True

        if request.method == 'DELETE':
            return obj.auteur == request.user or request.user.is_staff

        # PUT/PATCH
        return (
            obj.auteur == request.user or
            request.user.is_staff or
            request.user.groups.filter(name='Moderateurs').exists()
        )
```

```python
# articles/views.py
class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [ArticlePermission]
    queryset = Article.objects.all()

    def get_queryset(self):
        qs = Article.objects.all()
        if not self.request.user.is_authenticated:
            return qs.filter(statut='publie')
        if self.request.user.is_staff:
            return qs
        from django.db.models import Q
        return qs.filter(Q(statut='publie') | Q(auteur=self.request.user))
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal shell Django montrant `user.has_perm('articles.can_publish')` retournant False, puis ajout de la permission via `user.user_permissions.add(...)` et retournant True après rechargement
> **Expliquer :** Django cache les permissions en mémoire. Après modification, il faut recharger l'utilisateur : `user = User.objects.get(pk=user.pk)` ou vider le cache de permissions : `user._perm_cache.clear()`. En production, cela nécessite une nouvelle requête API.

---

## Résumé

| Permission | Usage |
|-----------|-------|
| `AllowAny` | Routes publiques |
| `IsAuthenticated` | Nécessite un token valide |
| `IsAdminUser` | Staff Django |
| `IsAuthenticatedOrReadOnly` | Lecture publique, écriture protégée |
| `DjangoModelPermissions` | Suit les permissions Django |
| `BasePermission` | Permission personnalisée |

- `has_permission()` : vérifié pour toutes les requêtes
- `has_object_permission()` : vérifié seulement pour les actions sur un objet (`get_object()`)
- `get_permissions()` pour des permissions différentes selon l'action
- Les opérateurs `|`, `&`, `~` permettent de combiner les permissions (DRF >= 3.9)
- Le `throttling` limite le nombre de requêtes par unité de temps

## Prochaine étape

Passez au module [Avancé — Middleware](../Avance/01-middleware.md) pour approfondir les fonctionnalités Django.
