# 03 — Vues Django

## Qu'est-ce qu'une vue ?

Une vue Django est une fonction (ou une classe) qui reçoit une requête HTTP et retourne une réponse HTTP. C'est le "C" du MVC, renommé "V" dans le MVT de Django.

```
Requête HTTP → URLs → View → (Model + Template) → Réponse HTTP
```

---

## Function-Based Views (FBV)

### Vue simple

```python
# articles/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from .models import Article

def liste_articles(request):
    """Vue listant tous les articles publiés."""
    articles = Article.objects.publies().select_related('auteur', 'categorie')
    return render(request, 'articles/liste.html', {
        'articles': articles,
        'titre_page': 'Tous les articles',
    })

def detail_article(request, slug):
    """Vue affichant le détail d'un article."""
    article = get_object_or_404(Article, slug=slug, statut='publie')
    # Incrémenter le compteur de vues
    Article.objects.filter(pk=article.pk).update(nb_vues=models.F('nb_vues') + 1)
    return render(request, 'articles/detail.html', {'article': article})
```

### Gérer les méthodes HTTP

```python
from django.views.decorators.http import require_http_methods, require_POST, require_GET

@require_GET
def liste_articles(request):
    # Seulement GET — retourne 405 Method Not Allowed pour POST
    articles = Article.objects.all()
    return render(request, 'articles/liste.html', {'articles': articles})

@require_http_methods(["GET", "POST"])
def creer_article(request):
    if request.method == 'POST':
        # Traiter le formulaire
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        article = Article.objects.create(
            titre=titre,
            contenu=contenu,
            auteur=request.user,
        )
        return redirect('articles:detail', slug=article.slug)
    # GET : afficher le formulaire vide
    return render(request, 'articles/creer.html')
```

### Redirections et messages

```python
from django.shortcuts import redirect
from django.contrib import messages

def supprimer_article(request, pk):
    article = get_object_or_404(Article, pk=pk, auteur=request.user)

    if request.method == 'POST':
        titre = article.titre
        article.delete()
        messages.success(request, f'L\'article "{titre}" a été supprimé.')
        return redirect('articles:liste')

    return render(request, 'articles/confirmer_suppression.html', {'article': article})
```

---

## Les décorateurs

### `@login_required`

```python
from django.contrib.auth.decorators import login_required, permission_required

@login_required(login_url='/auth/connexion/')
def mon_tableau_de_bord(request):
    articles = Article.objects.filter(auteur=request.user)
    return render(request, 'dashboard.html', {'articles': articles})

@permission_required('articles.can_publish', raise_exception=True)
def publier_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.publier()
    messages.success(request, 'Article publié.')
    return redirect(article.get_absolute_url())
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigateur montrant une redirection vers la page de login quand on accède à une vue protégée par `@login_required` sans être connecté
> **Expliquer :** Django gère automatiquement la redirection vers `settings.LOGIN_URL` et conserve l'URL de destination dans le paramètre `?next=`. Après connexion, l'utilisateur est redirigé vers l'URL d'origine.

---

## Class-Based Views (CBV)

Les CBV encapsulent le pattern "vue" dans une classe pour favoriser la réutilisation et l'héritage.

### Les vues génériques de base

```python
# articles/views.py
from django.views import View
from django.views.generic import (
    TemplateView, ListView, DetailView,
    CreateView, UpdateView, DeleteView,
)
from django.urls import reverse_lazy
from .models import Article

# TemplateView — Affiche simplement un template
class AccueilView(TemplateView):
    template_name = 'accueil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_recents'] = Article.objects.publies()[:5]
        return context


# ListView — Liste des objets
class ArticleListView(ListView):
    model = Article
    template_name = 'articles/liste.html'
    context_object_name = 'articles'   # Nom dans le template (défaut: object_list)
    paginate_by = 10                   # Pagination automatique

    def get_queryset(self):
        # Surchargeable pour filtrer
        return Article.objects.publies().select_related('auteur')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre_page'] = 'Tous les articles'
        return context


# DetailView — Détail d'un objet
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/detail.html'
    context_object_name = 'article'
    slug_field = 'slug'           # Champ utilisé pour récupérer l'objet
    slug_url_kwarg = 'slug'       # Nom du paramètre URL

    def get_queryset(self):
        return Article.objects.filter(statut='publie')
```

### Les vues d'édition

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = 'articles/form.html'
    fields = ['titre', 'contenu', 'categorie', 'tags', 'statut']

    def form_valid(self, form):
        # Attacher l'auteur avant la sauvegarde
        form.instance.auteur = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'articles/form.html'
    fields = ['titre', 'contenu', 'categorie', 'tags', 'statut']

    def get_queryset(self):
        # Un auteur ne peut modifier que ses propres articles
        return Article.objects.filter(auteur=self.request.user)


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/confirmer_suppression.html'
    success_url = reverse_lazy('articles:liste')

    def get_queryset(self):
        return Article.objects.filter(auteur=self.request.user)
```

### Configurer les URLs pour les CBV

```python
# articles/urls.py
from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='liste'),
    path('nouveau/', views.ArticleCreateView.as_view(), name='creer'),
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<slug:slug>/modifier/', views.ArticleUpdateView.as_view(), name='modifier'),
    path('<slug:slug>/supprimer/', views.ArticleDeleteView.as_view(), name='supprimer'),
]
```

---

## Vue générique avec View (contrôle total)

```python
from django.views import View
from django.http import JsonResponse
import json

class ArticleAPIView(View):
    """Vue avec contrôle complet sur les méthodes HTTP."""

    def get(self, request, pk=None):
        if pk:
            article = get_object_or_404(Article, pk=pk)
            data = {'id': article.pk, 'titre': article.titre}
        else:
            articles = Article.objects.publies()
            data = list(articles.values('id', 'titre', 'cree_le'))
        return JsonResponse(data, safe=False)

    def post(self, request):
        body = json.loads(request.body)
        article = Article.objects.create(
            titre=body['titre'],
            contenu=body['contenu'],
            auteur=request.user,
        )
        return JsonResponse({'id': article.pk, 'titre': article.titre}, status=201)

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk, auteur=request.user)
        article.delete()
        return JsonResponse({'message': 'Supprimé'}, status=204)
```

---

## Les Mixins

Les mixins sont des classes réutilisables qui ajoutent des comportements aux CBV :

```python
from django.contrib.auth.mixins import LoginRequiredMixin

# LoginRequiredMixin — Exige l'authentification
class VueProtegee(LoginRequiredMixin, View):
    login_url = '/auth/connexion/'
    redirect_field_name = 'next'


# PermissionRequiredMixin — Exige une permission
class VueAdmin(PermissionRequiredMixin, View):
    permission_required = 'articles.can_publish'
    raise_exception = True  # 403 au lieu de redirection login


# UserPassesTestMixin — Test personnalisé
from django.contrib.auth.mixins import UserPassesTestMixin

class VueAuteur(UserPassesTestMixin, UpdateView):
    model = Article

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.auteur


# Mixin personnalisé
class AutoeurRequisMixin:
    """S'assure que l'utilisateur est l'auteur de l'objet."""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.auteur != request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

---

## Pagination

```python
# Dans une FBV
from django.core.paginator import Paginator

def liste_articles(request):
    tous_articles = Article.objects.publies()
    paginator = Paginator(tous_articles, 10)  # 10 articles par page

    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)  # get_page gère les erreurs

    return render(request, 'articles/liste.html', {
        'page_obj': page_obj,
        'articles': page_obj.object_list,
    })
```

```html
<!-- Template de pagination -->
{% if page_obj.has_other_pages %}
<nav>
  {% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}">Précédent</a>
  {% endif %}

  <span>Page {{ page_obj.number }} sur {{ page_obj.paginator.num_pages }}</span>

  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}">Suivant</a>
  {% endif %}
</nav>
{% endif %}
```

---

## Objet `request`

```python
def ma_vue(request):
    # Méthode HTTP
    request.method          # 'GET', 'POST', 'PUT', 'DELETE'

    # Paramètres GET (?cle=valeur)
    request.GET.get('cle', 'valeur_defaut')
    request.GET.getlist('tags')  # Plusieurs valeurs : ?tags=python&tags=django

    # Données POST (formulaires)
    request.POST.get('titre')
    request.POST.getlist('tags')

    # Corps de la requête brut (JSON API)
    import json
    data = json.loads(request.body)

    # Fichiers uploadés
    request.FILES.get('image')

    # Utilisateur connecté
    request.user            # AnonymousUser si non connecté
    request.user.is_authenticated

    # Session
    request.session['panier'] = []
    request.session.get('panier', [])

    # Cookies
    request.COOKIES.get('langue', 'fr')

    # Headers
    request.headers.get('Content-Type')
    request.META.get('HTTP_USER_AGENT')
    request.META.get('REMOTE_ADDR')  # IP client
```

---

## Réponses HTTP

```python
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseServerError,
    JsonResponse,
    StreamingHttpResponse,
    FileResponse,
)

# Réponse texte simple
return HttpResponse("Hello, World!", content_type='text/plain')

# Réponse HTML
return HttpResponse("<h1>Bonjour</h1>")

# Réponse JSON
return JsonResponse({'status': 'ok', 'data': [1, 2, 3]})
return JsonResponse({'error': 'Non trouvé'}, status=404)

# Redirection
return HttpResponseRedirect('/articles/')
from django.shortcuts import redirect
return redirect('articles:liste')             # Nom de route
return redirect(article.get_absolute_url())   # URL d'objet
return redirect('articles:detail', slug='mon-slug')

# Codes d'erreur
return HttpResponseNotFound("Page introuvable")  # 404
return HttpResponseForbidden("Accès refusé")     # 403
return HttpResponseServerError("Erreur serveur") # 500

# Téléchargement de fichier
response = FileResponse(open('rapport.pdf', 'rb'))
response['Content-Disposition'] = 'attachment; filename="rapport.pdf"'
return response
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Django Debug Toolbar (ou DevTools navigateur) montrant les requêtes SQL générées par une vue et le temps de réponse
> **Expliquer :** Montrer l'importance du `select_related()` et `prefetch_related()` pour éviter le problème N+1. Comparer une vue sans optimisation (20 requêtes SQL) vs une vue optimisée (2 requêtes).

---

## FBV vs CBV — Quand utiliser quoi ?

| Situation | Recommandation |
|-----------|----------------|
| CRUD simple et standard | CBV (`ListView`, `CreateView`, etc.) |
| Logique métier complexe | FBV ou CBV personnalisée |
| API REST (sans DRF) | FBV avec `JsonResponse` |
| Formulaires multi-étapes | FBV |
| Vues réutilisables entre apps | CBV avec Mixins |
| Débutant Django | FBV d'abord |

---

## Résumé

- **FBV** : simples, explicites, idéales pour débuter
- **CBV** : réutilisables, moins de code pour les cas standards
- Les **Mixins** évitent la duplication de code de sécurité
- L'objet `request` contient tout sur la requête HTTP entrante
- Toujours utiliser `get_object_or_404` plutôt que `objects.get()` dans les vues

## Prochaine étape

Passez au module [04 — Templates](04-templates.md) pour apprendre à afficher vos données en HTML.
