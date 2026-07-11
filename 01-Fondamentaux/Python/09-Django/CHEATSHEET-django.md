# Cheat Sheet Django & DRF

## Commandes manage.py

```bash
# Projet
django-admin startproject config .
python manage.py startapp <nom_app>

# Serveur
python manage.py runserver
python manage.py runserver 0.0.0.0:8000

# Migrations
python manage.py makemigrations
python manage.py makemigrations <app> --name="description"
python manage.py migrate
python manage.py migrate <app> <000X>      # Rollback
python manage.py migrate <app> zero        # Annuler toutes les migrations
python manage.py showmigrations
python manage.py sqlmigrate <app> <000X>   # Voir le SQL

# Base de données
python manage.py dbshell
python manage.py flush                     # Vider toutes les tables

# Admin
python manage.py createsuperuser

# Shell
python manage.py shell
python manage.py shell_plus                # pip install django-extensions

# Statiques
python manage.py collectstatic

# Tests
python manage.py test
python manage.py test <app>
python manage.py test <app.tests.TestClass>

# Vérification
python manage.py check
python manage.py check --deploy
```

---

## ORM — QuerySet

```python
# Lire
Model.objects.all()
Model.objects.filter(champ=valeur)
Model.objects.exclude(champ=valeur)
Model.objects.get(pk=1)                      # Lève exception si absent/multiple
Model.objects.filter().first()               # None si absent
Model.objects.get_or_create(champ=val, defaults={...})
Model.objects.update_or_create(champ=val, defaults={...})

# Lookups
filter(champ__exact=val)           # =
filter(champ__iexact=val)          # = (insensible casse)
filter(champ__contains='mot')      # LIKE '%mot%'
filter(champ__icontains='mot')     # ILIKE '%mot%'
filter(champ__startswith='prefix') # LIKE 'prefix%'
filter(champ__in=[1, 2, 3])        # IN (...)
filter(champ__gt=val)              # >
filter(champ__gte=val)             # >=
filter(champ__lt=val)              # <
filter(champ__lte=val)             # <=
filter(champ__isnull=True)         # IS NULL
filter(champ__year=2024)           # YEAR(champ) = 2024
filter(relation__champ=val)        # JOIN + filtre

# Q objects
from django.db.models import Q
filter(Q(a=1) | Q(b=2))           # OR
filter(Q(a=1) & Q(b=2))           # AND
filter(~Q(a=1))                    # NOT

# Écrire
obj = Model.objects.create(**kwargs)
obj.champ = val; obj.save()
obj.save(update_fields=['champ'])
Model.objects.filter(...).update(champ=val)
Model.objects.filter(...).delete()
Model.objects.bulk_create([obj1, obj2])

# Trier
order_by('champ')        # ASC
order_by('-champ')       # DESC
order_by('a', '-b')      # Multi

# Couper
[:10]                    # 10 premiers
[10:20]                  # 11e au 20e

# Agrégation
from django.db.models import Count, Sum, Avg, Max, Min, F
.count()
.aggregate(total=Count('id'), somme=Sum('champ'))
.annotate(nb=Count('related'))
.filter(nb__gte=5)        # Filtrer sur annotation

# Optimisation
.select_related('fk', 'fk__autre_fk')   # JOIN (FK, O2O)
.prefetch_related('m2m', 'reverse_fk')  # Requêtes séparées (M2M, FK inverse)
.only('champ1', 'champ2')               # SELECT partiel
.defer('gros_champ')                    # Tout sauf...
.values('champ1', 'champ2')             # → liste de dicts
.values_list('champ', flat=True)        # → liste de valeurs
```

---

## Modèles — Types de champs

```python
CharField(max_length=N)
TextField()
EmailField()
URLField()
SlugField()
UUIDField(default=uuid.uuid4)
IntegerField()
PositiveIntegerField()
BigIntegerField()
FloatField()
DecimalField(max_digits=10, decimal_places=2)
BooleanField(default=False)
DateField()
TimeField()
DateTimeField(auto_now_add=True)    # Création
DateTimeField(auto_now=True)        # Mise à jour
ImageField(upload_to='images/')
FileField(upload_to='docs/')
ForeignKey(Model, on_delete=models.CASCADE, related_name='...')
ManyToManyField(Model, blank=True)
OneToOneField(Model, on_delete=models.CASCADE)
```

Options communes : `null=True`, `blank=True`, `default=...`, `unique=True`, `db_index=True`

---

## Admin

```python
from django.contrib import admin

@admin.register(MonModele)
class MonModelAdmin(admin.ModelAdmin):
    list_display     = ['champ1', 'champ2', 'methode_calculee']
    list_filter      = ['statut', 'categorie']
    search_fields    = ['titre', 'auteur__username']
    list_editable    = ['statut']
    ordering         = ['-cree_le']
    list_per_page    = 25
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields  = ['cree_le', 'modifie_le']
    date_hierarchy   = 'cree_le'
    list_select_related = ['auteur']

    fieldsets = [
        ('Section 1', {'fields': ('champ1', 'champ2')}),
        ('Avancé', {'fields': ('champ3',), 'classes': ('collapse',)}),
    ]

    @admin.display(description='Libellé', ordering='champ')
    def methode_calculee(self, obj):
        from django.utils.html import format_html
        return format_html('<b>{}</b>', obj.champ)

    @admin.action(description='Action personnalisée')
    def mon_action(self, request, queryset):
        queryset.update(statut='nouveau_statut')
        self.message_user(request, 'Action effectuée.')

    actions = ['mon_action']
```

---

## DRF — Sérialiseurs

```python
from rest_framework import serializers

class MonSerializer(serializers.ModelSerializer):
    champ_calcule = serializers.SerializerMethodField()
    champ_source  = serializers.CharField(source='related.champ', read_only=True)

    class Meta:
        model  = MonModele
        fields = ['id', 'champ1', 'champ2', 'champ_calcule', 'champ_source']
        read_only_fields  = ['id']
        extra_kwargs = {'champ2': {'min_length': 5}}

    def get_champ_calcule(self, obj):
        return obj.methode()

    def validate_champ1(self, value):
        if not value:
            raise serializers.ValidationError("Champ requis.")
        return value

    def validate(self, data):  # Validation croisée
        if data['a'] and not data['b']:
            raise serializers.ValidationError({'b': 'Requis si a est fourni.'})
        return data

    def create(self, validated_data):
        return MonModele.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
```

---

## DRF — ViewSet

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MonViewSet(viewsets.ModelViewSet):
    queryset           = MonModele.objects.all()
    serializer_class   = MonSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['statut']
    search_fields      = ['titre']
    ordering_fields    = ['cree_le']

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return MonListSerializer
        return MonDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='action-custom')
    def action_custom(self, request, pk=None):
        obj = self.get_object()
        # ...
        return Response({'status': 'ok'})

    @action(detail=False, methods=['get'])
    def mon_endpoint(self, request):
        qs = self.get_queryset().filter(...)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
```

```python
# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('ressource', MonViewSet, basename='ressource')
urlpatterns = [path('api/', include(router.urls))]
```

---

## DRF — JWT

```python
# Installation
# pip install djangorestframework-simplejwt

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('api/token/',         TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
]
```

```bash
# Obtenir un token
curl -X POST /api/token/ -d '{"username":"u","password":"p"}'
# → {"access": "eyJ...", "refresh": "eyJ..."}

# Utiliser le token
curl -H "Authorization: Bearer eyJ..." /api/endpoint/
```

---

## DRF — Permissions

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

class MaPermission(BasePermission):
    message = "Message d'erreur."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user

# Utilisation
class MaView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, MaPermission]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), MaPermission()]
```

---

## Codes de réponse HTTP

| Code | Signification | Usage |
|------|---------------|-------|
| 200 | OK | GET, PUT, PATCH réussi |
| 201 | Created | POST réussi |
| 204 | No Content | DELETE réussi |
| 400 | Bad Request | Données invalides |
| 401 | Unauthorized | Non authentifié |
| 403 | Forbidden | Authentifié mais non autorisé |
| 404 | Not Found | Ressource introuvable |
| 409 | Conflict | Ressource déjà existante |
| 422 | Unprocessable | Erreur de validation |
| 500 | Server Error | Erreur interne |

---

## Signaux

```python
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

@receiver(post_save, sender=MonModele)
def apres_sauvegarde(sender, instance, created, **kwargs):
    if created:
        pass  # Nouveau
    else:
        pass  # Mise à jour

@receiver(post_delete, sender=MonModele)
def apres_suppression(sender, instance, **kwargs):
    pass

# Enregistrer dans apps.py
class MonAppConfig(AppConfig):
    def ready(self):
        import mon_app.signals  # noqa
```

---

## Cache

```python
from django.core.cache import cache

cache.set('cle', valeur, timeout=300)
cache.get('cle', default=None)
cache.get_or_set('cle', valeur, timeout=300)
cache.delete('cle')
cache.delete_many(['cle1', 'cle2'])
cache.clear()

# Vue
from django.views.decorators.cache import cache_page
@cache_page(60 * 15)
def ma_vue(request): ...

# Template
{% load cache %}
{% cache 600 nom_du_cache %}...{% endcache %}
```

---

## .gitignore minimal

```
# Python
__pycache__/
*.py[cod]
*.pyo
venv/
.venv/

# Django
*.log
*.pot
db.sqlite3
media/
staticfiles/

# Environnement
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```
