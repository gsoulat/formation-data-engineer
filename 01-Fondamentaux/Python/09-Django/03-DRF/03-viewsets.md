# DRF — 03 : ViewSets et Vues

## Hiérarchie des vues DRF

```
APIView
├── GenericAPIView
│   ├── ListAPIView
│   ├── CreateAPIView
│   ├── RetrieveAPIView
│   ├── UpdateAPIView
│   ├── DestroyAPIView
│   ├── ListCreateAPIView
│   └── RetrieveUpdateDestroyAPIView
└── ViewSetMixin
    └── ViewSet
        ├── GenericViewSet
        │   ├── ReadOnlyModelViewSet  (list + retrieve)
        │   └── ModelViewSet          (CRUD complet)
        └── (ViewSet custom)
```

---

## APIView — Contrôle total

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Article
from .serializers import ArticleSerializer, ArticleDetailSerializer

class ArticleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        articles = Article.objects.select_related('auteur', 'categorie').all()

        # Pagination manuelle
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(articles, request)
        serializer = ArticleSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)  # Lève ValidationError si invalide
        serializer.save(auteur=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## Vues génériques

### ListCreateAPIView

```python
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

class ArticleListCreateView(ListCreateAPIView):
    queryset            = Article.objects.select_related('auteur', 'categorie')
    serializer_class    = ArticleSerializer
    permission_classes  = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        # Filtrer selon le paramètre ?statut=publie
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        return qs


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset           = Article.objects.all()
    serializer_class   = ArticleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field       = 'slug'  # Utiliser le slug plutôt que pk dans l'URL
    # URL: /api/articles/<slug>/

    def perform_update(self, serializer):
        # Vérifier que l'utilisateur est l'auteur
        if serializer.instance.auteur != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous n'êtes pas l'auteur de cet article.")
        serializer.save()
```

---

## ViewSet — Contrôle personnalisé

Un `ViewSet` regroupe plusieurs vues en une classe, sans la logique automatique de `ModelViewSet` :

```python
from rest_framework import viewsets
from rest_framework.response import Response

class ArticleViewSet(viewsets.ViewSet):
    """ViewSet minimal sans logique auto."""

    def list(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def create(self, request):
        serializer = ArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(auteur=request.user)
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        article = get_object_or_404(Article, pk=pk)
        article.delete()
        return Response(status=204)
```

---

## ModelViewSet — Le plus utilisé

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer, ArticleCreateSerializer
from .permissions import EstAuteurOuLectureSeule

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD complet pour les articles.

    list:   GET  /articles/          → Liste paginée
    create: POST /articles/          → Créer un article
    retrieve: GET /articles/{id}/    → Détail
    update: PUT /articles/{id}/      → Mise à jour complète
    partial_update: PATCH /articles/{id}/  → Mise à jour partielle
    destroy: DELETE /articles/{id}/  → Suppression
    """
    queryset            = Article.objects.select_related('auteur', 'categorie').prefetch_related('tags')
    permission_classes  = [IsAuthenticatedOrReadOnly, EstAuteurOuLectureSeule]
    filter_backends     = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields    = ['statut', 'categorie', 'mis_en_avant']
    search_fields       = ['titre', 'contenu', 'auteur__username']
    ordering_fields     = ['cree_le', 'nb_vues', 'titre']
    ordering            = ['-cree_le']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Les non-staff ne voient que les articles publiés (sauf les leurs)
        if not self.request.user.is_staff:
            if self.request.user.is_authenticated:
                from django.db.models import Q
                qs = qs.filter(Q(statut='publie') | Q(auteur=self.request.user))
            else:
                qs = qs.filter(statut='publie')
        return qs

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

    def perform_destroy(self, instance):
        # Logique avant suppression
        if instance.statut == 'publie':
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Impossible de supprimer un article publié.")
        instance.delete()

    # ---- Actions personnalisées ----

    @action(detail=True, methods=['post'], url_path='publier')
    def publier(self, request, pk=None):
        """POST /api/articles/{id}/publier/"""
        article = self.get_object()
        if article.auteur != request.user and not request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous n'êtes pas autorisé à publier cet article.")
        if article.statut == 'publie':
            return Response({'detail': 'Cet article est déjà publié.'}, status=400)
        article.statut = 'publie'
        article.save(update_fields=['statut'])
        return Response({'detail': 'Article publié avec succès.', 'statut': article.statut})

    @action(detail=True, methods=['post'], url_path='archiver')
    def archiver(self, request, pk=None):
        """POST /api/articles/{id}/archiver/"""
        article = self.get_object()
        article.statut = 'archive'
        article.save(update_fields=['statut'])
        return Response({'detail': 'Article archivé.', 'statut': article.statut})

    @action(detail=False, methods=['get'], url_path='mes-articles')
    def mes_articles(self, request):
        """GET /api/articles/mes-articles/ — Articles de l'utilisateur connecté."""
        articles = self.get_queryset().filter(auteur=request.user)
        page = self.paginate_queryset(articles)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='statistiques')
    def statistiques(self, request, pk=None):
        """GET /api/articles/{id}/statistiques/"""
        article = self.get_object()
        return Response({
            'nb_vues':          article.nb_vues,
            'nb_commentaires':  article.commentaires.count(),
            'nb_tags':          article.tags.count(),
            'nb_commentaires_approuves': article.commentaires.filter(approuve=True).count(),
        })
```

---

## Router — Génération automatique des URLs

```python
# articles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views

# DefaultRouter : inclut une page racine avec la liste des endpoints
router = DefaultRouter()
router.register('articles',   views.ArticleViewSet,   basename='article')
router.register('categories', views.CategorieViewSet, basename='categorie')
router.register('tags',       views.TagViewSet,       basename='tag')

# SimpleRouter : sans la page racine
# router = SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
]
```

URLs générées :
```
GET  /api/articles/                      article-list
POST /api/articles/                      article-list
GET  /api/articles/{id}/                 article-detail
PUT  /api/articles/{id}/                 article-detail
PATCH /api/articles/{id}/                article-detail
DELETE /api/articles/{id}/               article-detail
POST /api/articles/{id}/publier/         article-publier
POST /api/articles/{id}/archiver/        article-archiver
GET  /api/articles/mes-articles/         article-mes-articles
GET  /api/articles/{id}/statistiques/    article-statistiques
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur sur `/api/` (racine du DefaultRouter) montrant la liste de tous les endpoints disponibles, puis navigation vers `/api/articles/` et `/api/articles/1/`
> **Expliquer :** Le DefaultRouter génère automatiquement une page de navigation qui liste tous les ViewSets enregistrés. C'est très pratique pour la découverte de l'API. Montrer aussi les URLs nommées (article-list, article-detail) utilisées pour les reverse URLs.

---

## ReadOnlyModelViewSet — API en lecture seule

```python
from rest_framework.viewsets import ReadOnlyModelViewSet

class TagViewSet(ReadOnlyModelViewSet):
    """Fournit uniquement list() et retrieve()."""
    queryset         = Tag.objects.annotate(nb_articles=Count('articles'))
    serializer_class = TagSerializer

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """GET /api/tags/{id}/articles/"""
        tag = self.get_object()
        articles = tag.articles.filter(statut='publie')
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)
```

---

## Mixins — Composer des ViewSets

```python
from rest_framework import mixins, viewsets

# Seulement list + create (pas de detail, update, delete)
class CommentaireViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset         = Commentaire.objects.filter(approuve=True)
    serializer_class = CommentaireSerializer

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

# Seulement retrieve (détail sans modification)
class ArticlePublicViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset         = Article.objects.filter(statut='publie')
    serializer_class = ArticleDetailSerializer
```

---

## Réponses d'erreur standardisées

```python
# Personnaliser les réponses d'erreur globalement
# config/settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

# config/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'success': False,
            'erreur': {
                'code':    response.status_code,
                'message': response.data,
            }
        }

    return response
```

---

## `get_object()` et `get_queryset()`

```python
class ArticleViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        """
        Surcharger pour filtrer dynamiquement le queryset.
        Appelé automatiquement par list(), retrieve(), update(), destroy().
        """
        qs = Article.objects.all()
        # Filtrer par auteur si paramètre ?auteur=username
        auteur = self.request.query_params.get('auteur')
        if auteur:
            qs = qs.filter(auteur__username=auteur)
        return qs

    def get_object(self):
        """
        Surcharger pour personnaliser la récupération d'un objet.
        Appelé automatiquement par retrieve(), update(), partial_update(), destroy().
        """
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, **{self.lookup_field: self.kwargs[self.lookup_field]})
        # Vérifier les permissions au niveau objet
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_context(self):
        """Ajouter des données au contexte du sérialiseur."""
        context = super().get_serializer_context()
        context['articles_count'] = self.get_queryset().count()
        return context
```

---

## Exemple complet d'API

```python
# articles/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Article, Categorie, Tag
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateSerializer,
    CategorieSerializer, TagSerializer
)
from .permissions import EstAuteurOuReadOnly


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Categorie.objects.annotate(nb_articles=Count('articles'))
    serializer_class = CategorieSerializer

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        categorie = self.get_object()
        articles  = categorie.articles.filter(statut='publie').select_related('auteur')
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Tag.objects.annotate(nb_articles=Count('articles'))
    serializer_class = TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, EstAuteurOuReadOnly]
    ordering           = ['-cree_le']

    def get_queryset(self):
        qs = Article.objects.select_related('auteur', 'categorie').prefetch_related('tags')
        if not self.request.user.is_authenticated:
            return qs.filter(statut='publie')
        if self.request.user.is_staff:
            return qs
        from django.db.models import Q
        return qs.filter(Q(statut='publie') | Q(auteur=self.request.user))

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        article = self.get_object()
        article.statut = 'publie'
        article.save(update_fields=['statut'])
        return Response({'statut': 'publie'})
```

---

## Résumé

| Classe | Usage |
|--------|-------|
| `APIView` | Contrôle total, toute logique manuelle |
| `GenericAPIView` + mixins | Combinaison personnalisée |
| `ListCreateAPIView` | GET list + POST create |
| `RetrieveUpdateDestroyAPIView` | GET/PUT/PATCH/DELETE détail |
| `ModelViewSet` | CRUD complet auto |
| `ReadOnlyModelViewSet` | GET list + GET detail |

- `perform_create()`, `perform_update()`, `perform_destroy()` pour hook avant sauvegarde
- `get_queryset()` pour filtrage dynamique
- `get_serializer_class()` pour sérialiseur selon l'action
- `@action` pour endpoints supplémentaires sur un ViewSet

## Prochaine étape

Passez au module [04 — Authentification](04-authentification.md) pour sécuriser votre API.
