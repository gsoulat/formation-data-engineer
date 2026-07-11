# Exercice 01 — Blog API REST avec authentification

## Objectifs

Construire une API REST complète pour un blog avec :
- Authentification JWT
- CRUD articles, catégories, commentaires
- Permissions basées sur les rôles (auteur / modérateur / admin)
- Filtrage et recherche
- Tests de l'API avec Postman ou curl

**Durée estimée :** 4 à 6 heures

---

## Spécifications

### Modèles

```
User (Django natif + extensions)
├── ProfilUtilisateur (OneToOne)
│   ├── bio
│   └── avatar

Categorie
├── nom (unique)
├── slug (unique, auto)
└── description

Tag
├── nom (unique)
└── slug (unique, auto)

Article
├── titre
├── slug (unique, auto depuis titre)
├── contenu
├── image_couverture (optionnelle)
├── statut : brouillon | publie | archive
├── mis_en_avant : bool
├── nb_vues : int (incrémenté automatiquement)
├── auteur → User (FK)
├── categorie → Categorie (FK, nullable)
├── tags → Tag (M2M)
├── cree_le (auto)
└── modifie_le (auto)

Commentaire
├── article → Article (FK)
├── auteur → User (FK)
├── contenu
├── approuve : bool (défaut False)
└── cree_le (auto)
```

### Endpoints requis

```
# Auth
POST /api/auth/inscription/          ← Créer un compte
POST /api/auth/token/                ← Login → access + refresh tokens
POST /api/auth/token/refresh/        ← Renouveler le token
POST /api/auth/deconnexion/          ← Blacklister le refresh token
GET  /api/auth/profil/               ← Mon profil (auth requise)
PUT  /api/auth/profil/               ← Modifier mon profil

# Articles
GET  /api/articles/                  ← Liste (publics non-auth, tous si auth)
POST /api/articles/                  ← Créer (auth requise)
GET  /api/articles/{id}/             ← Détail + incrément nb_vues
PUT  /api/articles/{id}/             ← Modifier (auteur ou staff)
PATCH /api/articles/{id}/            ← Modification partielle
DELETE /api/articles/{id}/           ← Supprimer (auteur ou staff)
POST /api/articles/{id}/publier/     ← Publier (auteur ou staff)
POST /api/articles/{id}/archiver/    ← Archiver (auteur ou staff)
GET  /api/articles/mes-articles/     ← Mes articles (auth requise)

# Catégories
GET  /api/categories/                ← Liste avec nb_articles
GET  /api/categories/{id}/articles/  ← Articles d'une catégorie (publiés)

# Tags
GET  /api/tags/                      ← Liste avec nb_articles

# Commentaires
GET  /api/articles/{id}/commentaires/ ← Commentaires approuvés d'un article
POST /api/articles/{id}/commentaires/ ← Commenter (auth requise)
```

---

## Étape 1 — Initialisation du projet

```bash
# Créer et activer le venv
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install django djangorestframework djangorestframework-simplejwt \
            django-filter django-cors-headers Pillow python-decouple

# Créer le projet
django-admin startproject config .

# Créer les applications
python manage.py startapp articles
python manage.py startapp users
```

```python
# config/settings.py — Configuration minimale
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    # Local
    'articles.apps.ArticlesConfig',
    'users.apps.UsersConfig',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## Étape 2 — Modèles

```python
# articles/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Categorie(models.Model):
    nom         = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'catégories'
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Tag(models.Model):
    nom  = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Article(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('publie',    'Publié'),
        ('archive',   'Archivé'),
    ]

    titre      = models.CharField(max_length=200)
    slug       = models.SlugField(max_length=200, unique=True, blank=True)
    contenu    = models.TextField()
    image_couverture = models.ImageField(upload_to='articles/', blank=True)
    statut     = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    mis_en_avant = models.BooleanField(default=False)
    nb_vues    = models.PositiveIntegerField(default=0)
    auteur     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    categorie  = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags       = models.ManyToManyField(Tag, related_name='articles', blank=True)
    cree_le    = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)


class Commentaire(models.Model):
    article  = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    auteur   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    contenu  = models.TextField()
    approuve = models.BooleanField(default=False)
    cree_le  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cree_le']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.article}"
```

---

## Étape 3 — Sérialiseurs

```python
# articles/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article, Categorie, Tag, Commentaire

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    nb_articles = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Tag
        fields = ['id', 'nom', 'slug', 'nb_articles']
        read_only_fields = ['slug']


class CategorieSerializer(serializers.ModelSerializer):
    nb_articles = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Categorie
        fields = ['id', 'nom', 'slug', 'description', 'nb_articles']
        read_only_fields = ['slug']


class AuteurSerializer(serializers.ModelSerializer):
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'nom_complet']

    def get_nom_complet(self, obj):
        return obj.get_full_name() or obj.username


class ArticleListSerializer(serializers.ModelSerializer):
    auteur_nom   = serializers.CharField(source='auteur.username', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    tags_noms    = serializers.SerializerMethodField()

    class Meta:
        model  = Article
        fields = [
            'id', 'titre', 'slug', 'statut', 'mis_en_avant',
            'nb_vues', 'auteur_nom', 'categorie_nom', 'tags_noms', 'cree_le',
        ]

    def get_tags_noms(self, obj):
        return list(obj.tags.values_list('nom', flat=True))


class ArticleDetailSerializer(serializers.ModelSerializer):
    auteur    = AuteurSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)
    tags      = TagSerializer(many=True, read_only=True)
    nb_commentaires = serializers.SerializerMethodField()
    peut_modifier   = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'slug', 'contenu', 'image_couverture',
            'statut', 'mis_en_avant', 'nb_vues',
            'auteur', 'categorie', 'tags',
            'nb_commentaires', 'peut_modifier',
            'cree_le', 'modifie_le',
        ]

    def get_nb_commentaires(self, obj):
        return obj.commentaires.filter(approuve=True).count()

    def get_peut_modifier(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.auteur == request.user or request.user.is_staff


class ArticleCreateSerializer(serializers.ModelSerializer):
    tag_ids       = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags', many=True, required=False
    )
    categorie_id  = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(), source='categorie', required=False, allow_null=True
    )

    class Meta:
        model  = Article
        fields = ['titre', 'contenu', 'image_couverture', 'statut', 'mis_en_avant', 'categorie_id', 'tag_ids']

    def validate_titre(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Le titre doit faire au moins 5 caractères.")
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class CommentaireSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source='auteur.username', read_only=True)

    class Meta:
        model  = Commentaire
        fields = ['id', 'auteur_nom', 'contenu', 'approuve', 'cree_le']
        read_only_fields = ['approuve', 'cree_le']
```

---

## Étape 4 — Permissions et Vues

```python
# articles/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class EstAuteurOuReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.auteur == request.user or request.user.is_staff
```

```python
# articles/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Count, Q
from .models import Article, Categorie, Tag, Commentaire
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer, ArticleCreateSerializer,
    CategorieSerializer, TagSerializer, CommentaireSerializer
)
from .permissions import EstAuteurOuReadOnly


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.annotate(nb_articles=Count('articles'))
    serializer_class = CategorieSerializer

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        categorie = self.get_object()
        articles = categorie.articles.filter(statut='publie').select_related('auteur')
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.annotate(nb_articles=Count('articles'))
    serializer_class = TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, EstAuteurOuReadOnly]
    filterset_fields   = ['statut', 'categorie', 'mis_en_avant']
    search_fields      = ['titre', 'contenu', 'auteur__username']
    ordering_fields    = ['cree_le', 'nb_vues']
    ordering           = ['-cree_le']

    def get_queryset(self):
        qs = Article.objects.select_related('auteur', 'categorie').prefetch_related('tags')
        if not self.request.user.is_authenticated:
            return qs.filter(statut='publie')
        if self.request.user.is_staff:
            return qs
        return qs.filter(Q(statut='publie') | Q(auteur=self.request.user))

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateSerializer
        return ArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter les vues (atomique)
        Article.objects.filter(pk=instance.pk).update(nb_vues=F('nb_vues') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publier(self, request, pk=None):
        article = self.get_object()
        if article.statut == 'publie':
            return Response({'detail': 'Déjà publié.'}, status=400)
        article.statut = 'publie'
        article.save(update_fields=['statut'])
        return Response({'statut': article.statut})

    @action(detail=True, methods=['post'])
    def archiver(self, request, pk=None):
        article = self.get_object()
        article.statut = 'archive'
        article.save(update_fields=['statut'])
        return Response({'statut': article.statut})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mes_articles(self, request):
        articles = Article.objects.filter(auteur=request.user)
        page = self.paginate_queryset(articles)
        serializer = ArticleListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='commentaires')
    def commentaires(self, request, pk=None):
        article = self.get_object()
        if request.method == 'GET':
            commentaires = article.commentaires.filter(approuve=True)
            serializer = CommentaireSerializer(commentaires, many=True)
            return Response(serializer.data)
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=401)
        serializer = CommentaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(article=article, auteur=request.user)
        return Response(serializer.data, status=201)
```

---

## Étape 5 — URLs

```python
# articles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('articles',   views.ArticleViewSet,   basename='article')
router.register('categories', views.CategorieViewSet, basename='categorie')
router.register('tags',       views.TagViewSet,       basename='tag')

urlpatterns = [path('', include(router.urls))]
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/',         TokenObtainPairView.as_view()),
    path('api/auth/token/refresh/', TokenRefreshView.as_view()),
    path('api/',                    include('articles.urls')),
    path('api/auth/',               include('users.urls')),
]
```

---

## Étape 6 — Tests Postman

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Collection Postman avec les requêtes organisées en dossiers : Auth, Articles, Catégories, Tags. Montrer la variable d'environnement `{{token}}` utilisée dans tous les headers Authorization
> **Expliquer :** Montrer comment utiliser les "Tests" Postman pour extraire automatiquement le token JWT de la réponse de login et le stocker dans une variable d'environnement : `pm.environment.set("token", pm.response.json().access)`.

---

### Séquence de test manuelle

```bash
# 1. Inscription
curl -X POST http://localhost:8000/api/auth/inscription/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@test.com", "password": "pass1234!", "password_confirm": "pass1234!"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass1234!"}'
# → Copier le token "access"

TOKEN="eyJ..."  # Votre token

# 3. Créer un article
curl -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titre": "Mon premier article", "contenu": "Contenu de test avec suffisamment de mots."}'

# 4. Lister les articles
curl http://localhost:8000/api/articles/

# 5. Publier
curl -X POST http://localhost:8000/api/articles/1/publier/ \
  -H "Authorization: Bearer $TOKEN"

# 6. Recherche
curl "http://localhost:8000/api/articles/?search=premier&ordering=-nb_vues"
```

---

## Critères de validation

- [ ] L'inscription crée un utilisateur et retourne des tokens JWT
- [ ] Les articles non publiés ne sont visibles que par leur auteur
- [ ] La publication via l'endpoint `/publier/` fonctionne
- [ ] Un utilisateur ne peut pas modifier l'article d'un autre (403)
- [ ] La pagination fonctionne (`?page=2`)
- [ ] La recherche fonctionne (`?search=mot`)
- [ ] Les commentaires ne s'affichent qu'approuvés
- [ ] L'endpoint `/mes-articles/` retourne uniquement les articles de l'utilisateur connecté

## Pour aller plus loin

- Ajouter l'envoi d'email à la publication d'un article (signal post_save)
- Implémenter l'upload d'image de couverture
- Ajouter un champ `likes` avec une relation M2M vers User
- Écrire des tests unitaires avec `pytest-django`
