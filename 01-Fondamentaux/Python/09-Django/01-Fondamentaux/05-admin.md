# 05 — Interface d'Administration Django

## Présentation

L'admin Django est une interface web CRUD générée automatiquement à partir de vos modèles. C'est l'une des fonctionnalités les plus puissantes de Django : en quelques lignes de code, vous disposez d'une interface complète pour gérer vos données.

### Accès

```bash
# 1. Créer un superutilisateur
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: xxxxxxxx

# 2. Lancer le serveur
python manage.py runserver

# 3. Ouvrir dans le navigateur
# http://127.0.0.1:8000/admin/
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur ouvert sur `http://127.0.0.1:8000/admin/` montrant la page de connexion, puis après connexion, le dashboard admin avec les sections "Authentication and Authorization"
> **Expliquer :** L'admin est automatiquement disponible grâce à `django.contrib.admin` dans `INSTALLED_APPS`. Montrer les sections Users et Groups qui sont gérées nativement. Insister sur le fait que c'est un outil de back-office, pas une interface publique.

---

## Enregistrer des modèles

### Enregistrement simple

```python
# articles/admin.py
from django.contrib import admin
from .models import Article, Categorie, Tag, Commentaire

# Méthode 1 : simple (pas de personnalisation)
admin.site.register(Categorie)
admin.site.register(Tag)

# Méthode 2 : avec décorateur (recommandée)
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass
```

### ModelAdmin basique

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ['titre', 'auteur', 'statut', 'cree_le', 'nb_vues']

    # Colonnes sur lesquelles on peut cliquer pour aller au détail
    list_display_links = ['titre']

    # Filtres dans la sidebar droite
    list_filter = ['statut', 'categorie', 'cree_le']

    # Barre de recherche (SQL LIKE sur ces champs)
    search_fields = ['titre', 'contenu', 'auteur__username']

    # Champs modifiables directement dans la liste
    list_editable = ['statut']

    # Tri par défaut
    ordering = ['-cree_le']

    # Nombre d'éléments par page
    list_per_page = 25

    # Sélectionner les objets liés en un seul JOIN (optimisation)
    list_select_related = ['auteur', 'categorie']
```

---

## Personnalisation avancée

### Organisation des champs dans le formulaire

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'statut', 'mis_en_avant', 'cree_le']
    list_filter = ['statut', 'mis_en_avant', 'categorie', 'tags']
    search_fields = ['titre', 'contenu']
    list_editable = ['statut', 'mis_en_avant']
    prepopulated_fields = {'slug': ('titre',)}  # Auto-remplir le slug depuis le titre
    date_hierarchy = 'cree_le'                   # Navigation par date en haut
    list_select_related = ['auteur', 'categorie']

    # Organisation par sections
    fieldsets = [
        ('Contenu', {
            'fields': ('titre', 'slug', 'contenu', 'image_couverture'),
        }),
        ('Classification', {
            'fields': ('categorie', 'tags'),
            'classes': ('wide',),
        }),
        ('Publication', {
            'fields': ('statut', 'mis_en_avant', 'publie_le'),
        }),
        ('Métadonnées', {
            'fields': ('auteur',),
            'classes': ('collapse',),  # Section repliée par défaut
        }),
    ]

    # Champs en lecture seule
    readonly_fields = ['cree_le', 'modifie_le', 'nb_vues']

    # Auto-remplir l'auteur avec l'utilisateur connecté
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Seulement à la création
            obj.auteur = request.user
        super().save_model(request, obj, form, change)
```

### Colonnes calculées dans `list_display`

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'afficher_statut_colore', 'nb_commentaires', 'cree_le']

    @admin.display(description='Statut', ordering='statut')
    def afficher_statut_colore(self, obj):
        from django.utils.html import format_html
        couleurs = {
            'brouillon': '#999',
            'publie': '#28a745',
            'archive': '#dc3545',
        }
        couleur = couleurs.get(obj.statut, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            couleur,
            obj.get_statut_display(),
        )

    @admin.display(description='Commentaires')
    def nb_commentaires(self, obj):
        return obj.commentaires.count()
```

---

## Actions personnalisées

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    actions = ['publier_articles', 'archiver_articles', 'mettre_en_avant']

    @admin.action(description='Publier les articles sélectionnés')
    def publier_articles(self, request, queryset):
        nb = queryset.update(statut='publie')
        self.message_user(request, f'{nb} article(s) publié(s) avec succès.')

    @admin.action(description='Archiver les articles sélectionnés')
    def archiver_articles(self, request, queryset):
        nb = queryset.update(statut='archive')
        self.message_user(
            request,
            f'{nb} article(s) archivé(s).',
            level='warning',
        )

    @admin.action(description='Mettre en avant les articles sélectionnés')
    def mettre_en_avant(self, request, queryset):
        queryset.update(mis_en_avant=True)
        self.message_user(request, 'Articles mis en avant.')
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface admin avec la liste des articles, montrant les colonnes personnalisées avec la couleur du statut, puis la sélection de plusieurs articles et l'utilisation de l'action "Publier les articles sélectionnés"
> **Expliquer :** Les actions sont des opérations en masse très utiles. Montrer aussi le menu déroulant d'actions et l'alerte de confirmation qui apparaît après l'action. Comparer avec ce qu'il faudrait coder manuellement sans l'admin Django.

---

## Inline Admin

Les inlines permettent d'éditer des objets liés dans la même page que l'objet parent :

```python
from django.contrib import admin
from .models import Article, Commentaire

class CommentaireInline(admin.TabularInline):
    model = Commentaire
    extra = 1           # Nombre de formulaires vides à afficher
    fields = ['auteur', 'contenu', 'approuve']
    readonly_fields = ['cree_le']
    can_delete = True
    show_change_link = True  # Lien vers la page de modification du commentaire

# Alternative : StackedInline (formulaire empilé, plus verbeux)
class CommentaireStackedInline(admin.StackedInline):
    model = Commentaire
    extra = 0
    fields = ['auteur', 'contenu', 'approuve']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [CommentaireInline]
    # ...
```

### Inline Many-to-Many avec table intermédiaire

```python
class ArticleTagInline(admin.TabularInline):
    model = Article.tags.through  # Table intermédiaire M2M
    extra = 1
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'
```

---

## Filtres personnalisés

```python
from django.contrib.admin import SimpleListFilter

class ArticleRicheFilter(SimpleListFilter):
    title = 'contenu riche'
    parameter_name = 'contenu_riche'

    def lookups(self, request, model_admin):
        return [
            ('oui', 'Plus de 500 mots'),
            ('non', 'Moins de 500 mots'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'oui':
            # Filtrage en Python (pas idéal pour les grands jeux de données)
            ids = [a.pk for a in queryset if len(a.contenu.split()) > 500]
            return queryset.filter(pk__in=ids)
        if self.value() == 'non':
            ids = [a.pk for a in queryset if len(a.contenu.split()) <= 500]
            return queryset.filter(pk__in=ids)
        return queryset


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_filter = ['statut', 'categorie', ArticleRicheFilter]
```

---

## Personnalisation de l'interface

### Titre et en-tête

```python
# articles/admin.py ou config/admin.py
from django.contrib import admin

admin.site.site_header = "Administration Mon Blog"
admin.site.site_title = "Mon Blog"
admin.site.index_title = "Tableau de bord"
```

### AdminSite personnalisé

```python
# config/admin.py
from django.contrib.admin import AdminSite

class MonAdminSite(AdminSite):
    site_header = "Mon Blog — Administration"
    site_title = "Mon Blog"
    index_title = "Bienvenue dans l'espace administration"

    def has_permission(self, request):
        # Personnaliser l'accès (ici : staff seulement)
        return request.user.is_active and request.user.is_staff

mon_admin = MonAdminSite(name='mon_admin')
```

---

## Exemple complet

```python
# articles/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Categorie, Tag, Commentaire

admin.site.site_header = "Administration — Mon Blog"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nb_articles', 'slug']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}

    @admin.display(description="Nombre d'articles")
    def nb_articles(self, obj):
        return obj.articles.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}


class CommentaireInline(admin.TabularInline):
    model = Commentaire
    extra = 0
    fields = ['auteur', 'contenu', 'approuve', 'cree_le']
    readonly_fields = ['cree_le']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'auteur', 'categorie', 'badge_statut', 'mis_en_avant', 'nb_vues', 'cree_le']
    list_filter   = ['statut', 'mis_en_avant', 'categorie', 'tags']
    search_fields = ['titre', 'contenu', 'auteur__username', 'auteur__email']
    list_editable = ['mis_en_avant']
    ordering      = ['-cree_le']
    list_per_page = 20
    date_hierarchy = 'cree_le'
    list_select_related = ['auteur', 'categorie']
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ['cree_le', 'modifie_le', 'nb_vues']
    inlines = [CommentaireInline]
    actions = ['publier', 'archiver']

    fieldsets = [
        ('Contenu', {
            'fields': ('titre', 'slug', 'contenu', 'image_couverture'),
        }),
        ('Classification', {
            'fields': ('categorie', 'tags'),
        }),
        ('Publication', {
            'fields': ('statut', 'mis_en_avant', 'publie_le'),
        }),
        ('Auteur & Méta', {
            'fields': ('auteur', 'cree_le', 'modifie_le', 'nb_vues'),
            'classes': ('collapse',),
        }),
    ]

    @admin.display(description='Statut', ordering='statut')
    def badge_statut(self, obj):
        couleurs = {
            'brouillon': ('#ffc107', '#212529'),
            'publie':    ('#28a745', '#fff'),
            'archive':   ('#6c757d', '#fff'),
        }
        bg, fg = couleurs.get(obj.statut, ('#999', '#fff'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:4px;font-size:11px;">{}</span>',
            bg, fg, obj.get_statut_display(),
        )

    @admin.action(description='Publier les articles sélectionnés')
    def publier(self, request, queryset):
        nb = queryset.update(statut='publie')
        self.message_user(request, f'{nb} article(s) publié(s).')

    @admin.action(description='Archiver les articles sélectionnés')
    def archiver(self, request, queryset):
        nb = queryset.update(statut='archive')
        self.message_user(request, f'{nb} article(s) archivé(s).', level='warning')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.auteur = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Les non-superusers ne voient que leurs articles
        return qs.filter(auteur=request.user)


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display  = ['article', 'auteur', 'approuve', 'cree_le']
    list_filter   = ['approuve', 'cree_le']
    search_fields = ['contenu', 'auteur__username', 'article__titre']
    list_editable = ['approuve']
    actions       = ['approuver_commentaires']

    @admin.action(description='Approuver les commentaires sélectionnés')
    def approuver_commentaires(self, request, queryset):
        nb = queryset.update(approuve=True)
        self.message_user(request, f'{nb} commentaire(s) approuvé(s).')
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Page de modification d'un article dans l'admin, montrant les fieldsets repliables, les champs en lecture seule, le inline des commentaires en bas, et le champ slug qui s'auto-remplit à la saisie du titre
> **Expliquer :** Décrire le JavaScript natif de l'admin qui gère le prepopulated_fields. Montrer aussi que les changements sont tracés (via django.contrib.admin et le log). L'admin logge toutes les actions des utilisateurs staff.

---

## Accès au log d'administration

Django logue automatiquement toutes les actions dans `LogEntry` :

```python
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

# Voir les 10 dernières actions
derniers_logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:10]

for log in derniers_logs:
    print(f"{log.action_time} — {log.user} — {log.get_action_flag_display()} — {log.object_repr}")
```

---

## Résumé

- `admin.site.register()` ou `@admin.register()` pour enregistrer un modèle
- `ModelAdmin` personnalise l'affichage : `list_display`, `list_filter`, `search_fields`
- `fieldsets` organise le formulaire en sections
- Les **actions** permettent des opérations en masse sur des sélections
- Les **inlines** éditent les objets liés dans la même page
- `format_html()` pour afficher du HTML sécurisé dans les colonnes
- L'admin Django est un back-office puissant, pas une interface publique

## Prochaine étape

Passez au module [ORM Django — 01 Requêtes](../ORM-Django/01-requetes.md) pour maîtriser l'interrogation de la base de données.
