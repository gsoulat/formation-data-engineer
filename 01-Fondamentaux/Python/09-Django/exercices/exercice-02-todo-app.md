# Exercice 02 — Application Todo complète

## Objectifs

Construire une application Todo full-stack Django avec :
- Interface HTML avec Django templates (pas de SPA)
- API REST DRF en parallèle
- Authentification par formulaire (Django natif) + JWT pour l'API
- Catégories de tâches, priorités, dates d'échéance
- Filtres et recherche
- Tests unitaires

**Durée estimée :** 3 à 5 heures

---

## Spécifications

### Modèles

```
ProjetTodo
├── nom
├── description
├── couleur (hex)
├── proprietaire → User (FK)
├── membres → User (M2M)
└── cree_le

TacheTodo
├── titre
├── description
├── statut : a_faire | en_cours | termine | annule
├── priorite : basse | normale | haute | urgente
├── date_echeance (nullable)
├── projet → ProjetTodo (FK)
├── assignee → User (FK, nullable)
├── cree_par → User (FK)
├── ordre : int (pour drag & drop)
├── cree_le
└── modifie_le
```

### Fonctionnalités

- CRUD complet sur les projets et les tâches
- Seul le propriétaire ou les membres peuvent voir un projet
- Changer le statut d'une tâche (toggle)
- Filtrer par statut, priorité, assigné
- Tâches en retard (date_echeance < aujourd'hui et pas terminées)
- Tableau de bord avec statistiques

---

## Étape 1 — Projet et modèles

```bash
django-admin startproject config .
python manage.py startapp todos
```

```python
# todos/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

COULEURS = [
    ('#3B82F6', 'Bleu'),
    ('#10B981', 'Vert'),
    ('#F59E0B', 'Orange'),
    ('#EF4444', 'Rouge'),
    ('#8B5CF6', 'Violet'),
    ('#6B7280', 'Gris'),
]


class ProjetTodo(models.Model):
    nom          = models.CharField(max_length=100)
    description  = models.TextField(blank=True)
    couleur      = models.CharField(max_length=7, choices=COULEURS, default='#3B82F6')
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projets_possedes')
    membres      = models.ManyToManyField(User, related_name='projets_membre', blank=True)
    cree_le      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return self.nom

    def est_accessible_par(self, user):
        return user == self.proprietaire or self.membres.filter(pk=user.pk).exists()

    @property
    def nb_taches_total(self):
        return self.taches.count()

    @property
    def nb_taches_terminees(self):
        return self.taches.filter(statut='termine').count()

    @property
    def progression(self):
        total = self.nb_taches_total
        if total == 0:
            return 0
        return int(self.nb_taches_terminees / total * 100)


class TacheTodo(models.Model):
    STATUTS = [
        ('a_faire',  'À faire'),
        ('en_cours', 'En cours'),
        ('termine',  'Terminé'),
        ('annule',   'Annulé'),
    ]
    PRIORITES = [
        ('basse',    'Basse'),
        ('normale',  'Normale'),
        ('haute',    'Haute'),
        ('urgente',  'Urgente'),
    ]
    PRIORITE_ORDRE = {'basse': 1, 'normale': 2, 'haute': 3, 'urgente': 4}

    titre          = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    statut         = models.CharField(max_length=20, choices=STATUTS, default='a_faire')
    priorite       = models.CharField(max_length=20, choices=PRIORITES, default='normale')
    date_echeance  = models.DateField(null=True, blank=True)
    projet         = models.ForeignKey(ProjetTodo, on_delete=models.CASCADE, related_name='taches')
    assignee       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taches_assignees')
    cree_par       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taches_creees')
    ordre          = models.PositiveIntegerField(default=0)
    cree_le        = models.DateTimeField(auto_now_add=True)
    modifie_le     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', '-priorite', 'date_echeance']

    def __str__(self):
        return self.titre

    @property
    def est_en_retard(self):
        return (
            self.date_echeance is not None and
            self.date_echeance < timezone.now().date() and
            self.statut not in ['termine', 'annule']
        )

    @property
    def priorite_valeur(self):
        return self.PRIORITE_ORDRE.get(self.priorite, 0)
```

---

## Étape 2 — Admin

```python
# todos/admin.py
from django.contrib import admin
from .models import ProjetTodo, TacheTodo

class TacheInline(admin.TabularInline):
    model = TacheTodo
    extra = 0
    fields = ['titre', 'statut', 'priorite', 'assignee', 'date_echeance']


@admin.register(ProjetTodo)
class ProjetAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'proprietaire', 'couleur', 'nb_taches_total', 'progression', 'cree_le']
    list_filter   = ['couleur', 'cree_le']
    search_fields = ['nom', 'proprietaire__username']
    inlines       = [TacheInline]

    @admin.display(description='Progression')
    def progression(self, obj):
        return f"{obj.progression}%"


@admin.register(TacheTodo)
class TacheAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'projet', 'statut', 'priorite', 'assignee', 'date_echeance', 'est_en_retard']
    list_filter   = ['statut', 'priorite', 'projet']
    search_fields = ['titre', 'description']
    list_editable = ['statut', 'priorite']

    @admin.display(description='En retard', boolean=True)
    def est_en_retard(self, obj):
        return obj.est_en_retard
```

---

## Étape 3 — Sérialiseurs DRF

```python
# todos/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProjetTodo, TacheTodo

User = get_user_model()


class UtilisateurSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name']


class TacheListSerializer(serializers.ModelSerializer):
    assignee    = UtilisateurSimpleSerializer(read_only=True)
    est_en_retard = serializers.BooleanField(read_only=True)

    class Meta:
        model  = TacheTodo
        fields = ['id', 'titre', 'statut', 'priorite', 'date_echeance', 'assignee', 'est_en_retard', 'ordre']


class TacheDetailSerializer(serializers.ModelSerializer):
    assignee  = UtilisateurSimpleSerializer(read_only=True)
    cree_par  = UtilisateurSimpleSerializer(read_only=True)
    est_en_retard = serializers.BooleanField(read_only=True)

    class Meta:
        model = TacheTodo
        fields = '__all__'


class TacheCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', required=False, allow_null=True
    )

    class Meta:
        model  = TacheTodo
        fields = ['titre', 'description', 'statut', 'priorite', 'date_echeance', 'assignee_id', 'ordre']

    def validate_date_echeance(self, value):
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("La date d'échéance ne peut pas être dans le passé.")
        return value


class ProjetSerializer(serializers.ModelSerializer):
    proprietaire  = UtilisateurSimpleSerializer(read_only=True)
    membres       = UtilisateurSimpleSerializer(many=True, read_only=True)
    nb_taches     = serializers.IntegerField(source='nb_taches_total', read_only=True)
    progression   = serializers.IntegerField(read_only=True)
    taches        = TacheListSerializer(many=True, read_only=True)

    class Meta:
        model  = ProjetTodo
        fields = ['id', 'nom', 'description', 'couleur', 'proprietaire', 'membres', 'nb_taches', 'progression', 'taches', 'cree_le']
        read_only_fields = ['proprietaire', 'cree_le']
```

---

## Étape 4 — ViewSets et Permissions

```python
# todos/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class EstMembreProjet(BasePermission):
    """Seuls les membres (+ propriétaire) peuvent accéder au projet."""
    message = "Vous n'êtes pas membre de ce projet."

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, TacheTodo):
            projet = obj.projet
        else:
            projet = obj
        return projet.est_accessible_par(request.user)


class EstProprietaire(BasePermission):
    """Seul le propriétaire peut modifier/supprimer un projet."""
    message = "Seul le propriétaire peut effectuer cette action."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, TacheTodo):
            return obj.projet.proprietaire == request.user
        return obj.proprietaire == request.user
```

```python
# todos/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ProjetTodo, TacheTodo
from .serializers import ProjetSerializer, TacheListSerializer, TacheDetailSerializer, TacheCreateSerializer
from .permissions import EstMembreProjet, EstProprietaire


class ProjetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, EstMembreProjet]
    serializer_class   = ProjetSerializer

    def get_queryset(self):
        user = self.request.user
        return ProjetTodo.objects.filter(
            Q(proprietaire=user) | Q(membres=user)
        ).distinct().prefetch_related('membres', 'taches')

    def perform_create(self, serializer):
        serializer.save(proprietaire=self.request.user)

    @action(detail=True, methods=['post'], url_path='ajouter-membre')
    def ajouter_membre(self, request, pk=None):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        projet = self.get_object()
        if projet.proprietaire != request.user:
            return Response({'detail': 'Seul le propriétaire peut gérer les membres.'}, status=403)
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            projet.membres.add(user)
            return Response({'detail': f'{username} ajouté au projet.'})
        except User.DoesNotExist:
            return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    @action(detail=True, methods=['get'], url_path='statistiques')
    def statistiques(self, request, pk=None):
        projet = self.get_object()
        taches = projet.taches.all()
        return Response({
            'total':     taches.count(),
            'par_statut': {
                s: taches.filter(statut=s).count()
                for s, _ in TacheTodo.STATUTS
            },
            'en_retard': sum(1 for t in taches if t.est_en_retard),
            'progression': projet.progression,
        })


class TacheViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, EstMembreProjet, EstProprietaire]
    filterset_fields   = ['statut', 'priorite', 'assignee']
    search_fields      = ['titre', 'description']
    ordering_fields    = ['priorite', 'date_echeance', 'cree_le', 'ordre']

    def get_queryset(self):
        projet_id = self.kwargs.get('projet_pk')
        user = self.request.user
        qs = TacheTodo.objects.filter(
            Q(projet__proprietaire=user) | Q(projet__membres=user)
        ).distinct().select_related('assignee', 'cree_par', 'projet')
        if projet_id:
            qs = qs.filter(projet_id=projet_id)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return TacheListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return TacheCreateSerializer
        return TacheDetailSerializer

    def perform_create(self, serializer):
        projet_id = self.kwargs.get('projet_pk')
        projet = ProjetTodo.objects.get(pk=projet_id)
        serializer.save(cree_par=self.request.user, projet=projet)

    @action(detail=True, methods=['post'], url_path='changer-statut')
    def changer_statut(self, request, pk=None, projet_pk=None):
        tache  = self.get_object()
        statut = request.data.get('statut')
        statuts_valides = [s for s, _ in TacheTodo.STATUTS]
        if statut not in statuts_valides:
            return Response({'detail': f'Statut invalide. Valeurs : {statuts_valides}'}, status=400)
        tache.statut = statut
        tache.save(update_fields=['statut'])
        return Response({'statut': tache.statut})
```

---

## Étape 5 — URLs imbriquées

```python
# todos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from . import views

# pip install drf-nested-routers
router = DefaultRouter()
router.register('projets', views.ProjetViewSet, basename='projet')

projets_router = nested_routers.NestedDefaultRouter(router, 'projets', lookup='projet')
projets_router.register('taches', views.TacheViewSet, basename='projet-taches')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projets_router.urls)),
]

# URLs générées :
# /api/projets/
# /api/projets/{id}/
# /api/projets/{id}/statistiques/
# /api/projets/{id}/ajouter-membre/
# /api/projets/{projet_pk}/taches/
# /api/projets/{projet_pk}/taches/{id}/
# /api/projets/{projet_pk}/taches/{id}/changer-statut/
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman montrant la création d'un projet, puis d'une tâche imbriquée avec l'URL `/api/projets/1/taches/`, puis l'appel à `changer-statut` pour marquer la tâche comme terminée
> **Expliquer :** Les URLs imbriquées (`/projets/{id}/taches/`) expriment la relation parent-enfant dans l'URL. C'est une convention REST recommandée pour les ressources qui n'existent que dans le contexte d'une autre ressource.

---

## Étape 6 — Tests

```python
# todos/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import ProjetTodo, TacheTodo

User = get_user_model()


class ProjetTodoTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.alice = User.objects.create_user(username='alice', password='test1234')
        self.bob   = User.objects.create_user(username='bob', password='test1234')
        self.client.force_authenticate(user=self.alice)

    def test_creer_projet(self):
        response = self.client.post('/api/projets/', {
            'nom': 'Mon projet',
            'couleur': '#3B82F6',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjetTodo.objects.count(), 1)
        self.assertEqual(ProjetTodo.objects.first().proprietaire, self.alice)

    def test_liste_projets_filtree(self):
        """Alice ne voit que ses projets."""
        ProjetTodo.objects.create(nom='Projet Alice', proprietaire=self.alice)
        ProjetTodo.objects.create(nom='Projet Bob', proprietaire=self.bob)
        response = self.client.get('/api/projets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nom'], 'Projet Alice')

    def test_bob_ne_peut_pas_voir_projet_alice(self):
        projet = ProjetTodo.objects.create(nom='Projet Alice', proprietaire=self.alice)
        self.client.force_authenticate(user=self.bob)
        response = self.client.get(f'/api/projets/{projet.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_membre_peut_voir_projet(self):
        projet = ProjetTodo.objects.create(nom='Projet partagé', proprietaire=self.alice)
        projet.membres.add(self.bob)
        self.client.force_authenticate(user=self.bob)
        response = self.client.get(f'/api/projets/{projet.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_tache_en_retard(self):
        from datetime import date, timedelta
        projet = ProjetTodo.objects.create(nom='Projet', proprietaire=self.alice)
        tache = TacheTodo.objects.create(
            titre='Tâche urgente',
            projet=projet,
            cree_par=self.alice,
            date_echeance=date.today() - timedelta(days=1),
            statut='a_faire',
        )
        self.assertTrue(tache.est_en_retard)

    def test_non_authentifie_refuse(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/projets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

```bash
# Lancer les tests
python manage.py test todos

# Avec coverage
pip install coverage
coverage run manage.py test todos
coverage report
coverage html  # Rapport HTML dans htmlcov/
```

---

## Critères de validation

- [ ] Un utilisateur ne voit que ses projets (propriétaire ou membre)
- [ ] Les URLs imbriquées fonctionnent : `GET /api/projets/1/taches/`
- [ ] `est_en_retard` retourne `True` pour les tâches en retard
- [ ] `progression` retourne le pourcentage correct
- [ ] L'endpoint `statistiques` retourne les bonnes données
- [ ] Les tests unitaires passent tous

## Pour aller plus loin

- Ajouter des sous-tâches (ForeignKey auto-référentielle)
- Implémenter le drag & drop (endpoint pour réordonner les tâches)
- Notifications par email quand une tâche est assignée
- Exporter les tâches en CSV (`StreamingHttpResponse`)
- Interface Kanban en HTML avec JavaScript natif
