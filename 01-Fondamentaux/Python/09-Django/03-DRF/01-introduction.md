# DRF — 01 : Introduction

## Pourquoi Django REST Framework ?

Sans DRF, exposer une API JSON en Django nécessite beaucoup de code répétitif :

```python
# Sans DRF — laborieux et fragile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def articles_api(request):
    if request.method == 'GET':
        articles = Article.objects.all()
        data = [{'id': a.id, 'titre': a.titre} for a in articles]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        body = json.loads(request.body)
        # Validation manuelle...
        if 'titre' not in body:
            return JsonResponse({'error': 'titre requis'}, status=400)
        # ...
```

Avec DRF, c'est beaucoup plus court et robuste :

```python
# Avec DRF
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
```

---

## Installation et configuration

```bash
pip install djangorestframework
```

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Pour commencer
    ],
}
```

---

## Votre premier sérialiseur

Un sérialiseur convertit un objet Django en JSON (sérialisation) et du JSON en objet Django validé (désérialisation).

```python
# articles/serializers.py
from rest_framework import serializers
from .models import Article, Categorie

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug']

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'slug', 'contenu',
            'statut', 'mis_en_avant', 'nb_vues',
            'categorie', 'cree_le', 'modifie_le',
        ]
        read_only_fields = ['id', 'nb_vues', 'cree_le', 'modifie_le']
```

---

## Votre première vue API

### APIView (contrôle total)

```python
# articles/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Article
from .serializers import ArticleSerializer

class ArticleListAPIView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(auteur=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailAPIView(APIView):
    def get_object(self, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Article, pk=pk)

    def get(self, request, pk):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, pk):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        article = self.get_object(pk)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = self.get_object(pk)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### URLs

```python
# articles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.ArticleListAPIView.as_view()),
    path('articles/<int:pk>/', views.ArticleDetailAPIView.as_view()),
]
```

```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('articles.urls')),
]
```

---

## La Browsable API

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur ouvert sur `http://127.0.0.1:8000/api/articles/` montrant l'interface HTML de la Browsable API avec le JSON rendu, le formulaire POST en bas, et les boutons GET/POST
> **Expliquer :** La Browsable API est une fonctionnalité unique de DRF qui génère une interface HTML interactive pour explorer l'API. Elle est activée par `BrowsableAPIRenderer` dans les settings. À désactiver en production pour des raisons de sécurité et de performance.

---

## ViewSet + Router (approche recommandée)

Le `ModelViewSet` génère automatiquement toutes les opérations CRUD :

```python
# articles/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    """
    Fournit automatiquement :
    - GET  /articles/           → list()
    - POST /articles/           → create()
    - GET  /articles/{id}/      → retrieve()
    - PUT  /articles/{id}/      → update()
    - PATCH /articles/{id}/     → partial_update()
    - DELETE /articles/{id}/    → destroy()
    """
    queryset = Article.objects.select_related('auteur', 'categorie').all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Attacher l'auteur automatiquement
        serializer.save(auteur=self.request.user)
```

```python
# articles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet, basename='article')
router.register('categories', views.CategorieViewSet, basename='categorie')

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('articles.urls')),
    # URLs d'auth DRF (login/logout pour la browsable API)
    path('api-auth/', include('rest_framework.urls')),
]
```

### URLs générées par le Router

```
GET    /api/articles/           → ArticleViewSet.list()
POST   /api/articles/           → ArticleViewSet.create()
GET    /api/articles/1/         → ArticleViewSet.retrieve()
PUT    /api/articles/1/         → ArticleViewSet.update()
PATCH  /api/articles/1/         → ArticleViewSet.partial_update()
DELETE /api/articles/1/         → ArticleViewSet.destroy()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman ou curl montrant une séquence de requêtes : POST pour créer un article, GET pour le lister, PATCH pour le modifier, DELETE pour le supprimer, avec les status codes (201, 200, 200, 204)
> **Expliquer :** Montrer les headers de requête (Content-Type: application/json) et de réponse. Expliquer les codes HTTP sémantiques : 201 Created, 204 No Content. Montrer aussi une requête invalide (sans titre) qui retourne un 400 Bad Request avec les erreurs de validation.

---

## Réponses et codes HTTP

```python
from rest_framework.response import Response
from rest_framework import status

# 200 OK
return Response(serializer.data)
return Response(serializer.data, status=status.HTTP_200_OK)

# 201 Created
return Response(serializer.data, status=status.HTTP_201_CREATED)

# 204 No Content (DELETE)
return Response(status=status.HTTP_204_NO_CONTENT)

# 400 Bad Request
return Response({'error': 'Données invalides'}, status=status.HTTP_400_BAD_REQUEST)
return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 401 Unauthorized
return Response({'error': 'Authentification requise'}, status=status.HTTP_401_UNAUTHORIZED)

# 403 Forbidden
return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

# 404 Not Found
return Response({'error': 'Non trouvé'}, status=status.HTTP_404_NOT_FOUND)

# 409 Conflict
return Response({'error': 'Ressource déjà existante'}, status=status.HTTP_409_CONFLICT)
```

### Raccourcis d'erreur

```python
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
)

# Ces exceptions sont gérées automatiquement par DRF
raise NotFound("Article non trouvé")
raise PermissionDenied("Vous n'êtes pas l'auteur de cet article")
raise ValidationError({'titre': ['Ce titre est déjà utilisé.']})
```

---

## Actions personnalisées sur un ViewSet

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # Action sur une liste : GET /articles/mis_en_avant/
    @action(detail=False, methods=['get'], url_path='mis-en-avant')
    def mis_en_avant(self, request):
        articles = self.get_queryset().filter(mis_en_avant=True)
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    # Action sur un objet : POST /articles/1/publier/
    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        article = self.get_object()
        if article.statut == 'publie':
            return Response({'message': 'Déjà publié'}, status=400)
        article.statut = 'publie'
        article.save(update_fields=['statut'])
        return Response({'message': 'Article publié', 'statut': article.statut})

    # Action avec sérialiseur différent
    @action(detail=True, methods=['get'], url_path='statistiques')
    def statistiques(self, request, pk=None):
        article = self.get_object()
        return Response({
            'nb_vues': article.nb_vues,
            'nb_commentaires': article.commentaires.count(),
            'nb_tags': article.tags.count(),
        })
```

---

## Pagination

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

Réponse paginée :
```json
{
    "count": 150,
    "next": "http://api.example.com/articles/?page=3",
    "previous": "http://api.example.com/articles/?page=1",
    "results": [...]
}
```

Pagination personnalisée :
```python
# articles/pagination.py
from rest_framework.pagination import PageNumberPagination, CursorPagination

class ArticlePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # ?page_size=50
    max_page_size = 100
    page_query_param = 'page'            # ?page=2

class ArticleCursorPagination(CursorPagination):
    """Pour les flux chronologiques (plus performant sur les grandes tables)."""
    page_size = 20
    ordering = '-cree_le'
    cursor_query_param = 'cursor'
```

```python
class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = ArticlePagination  # Override la pagination globale
```

---

## Filtrage et recherche

```bash
pip install django-filter
```

```python
# articles/filters.py
import django_filters
from .models import Article

class ArticleFilter(django_filters.FilterSet):
    titre       = django_filters.CharFilter(lookup_expr='icontains')
    statut      = django_filters.ChoiceFilter(choices=Article.STATUTS)
    auteur      = django_filters.CharFilter(field_name='auteur__username')
    cree_apres  = django_filters.DateFilter(field_name='cree_le', lookup_expr='gte')
    cree_avant  = django_filters.DateFilter(field_name='cree_le', lookup_expr='lte')

    class Meta:
        model = Article
        fields = ['statut', 'categorie', 'mis_en_avant']


# articles/views.py
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ArticleFilter

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['titre', 'contenu', 'auteur__username']  # ?search=django
    ordering_fields = ['cree_le', 'nb_vues', 'titre']         # ?ordering=-nb_vues
    ordering = ['-cree_le']                                    # Tri par défaut
```

Requêtes possibles :
```
GET /api/articles/?statut=publie
GET /api/articles/?auteur=alice
GET /api/articles/?search=django
GET /api/articles/?ordering=-nb_vues
GET /api/articles/?cree_apres=2024-01-01&cree_avant=2024-12-31
```

---

## Résumé

- DRF = sérialiseurs + vues + routeurs + auth + permissions
- `APIView` : contrôle total, méthodes GET/POST/PUT/PATCH/DELETE
- `ModelViewSet` : CRUD automatique + `@action` pour des endpoints supplémentaires
- `DefaultRouter` : génère toutes les URLs CRUD automatiquement
- La Browsable API permet de tester l'API dans le navigateur
- La pagination est configurée globalement dans `REST_FRAMEWORK`

## Prochaine étape

Passez au module [02 — Sérialiseurs](02-serializers.md) pour maîtriser la validation et la transformation des données.
