# 04 — Templates Django

## Introduction au système de templates

Django inclut un moteur de templates puissant. Un template est un fichier texte (généralement HTML) avec une syntaxe spéciale pour afficher des données dynamiques.

### Configuration

```python
# config/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Templates globaux du projet
        'APP_DIRS': True,                  # Cherche aussi dans chaque app/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### Structure des templates

```
templates/               ← Templates globaux (config/settings.py DIRS)
├── base.html
├── navbar.html
└── footer.html

articles/
└── templates/
    └── articles/        ← Convention : app_name/template_name.html
        ├── liste.html
        ├── detail.html
        └── form.html
```

---

## Syntaxe de base

### Variables

```html
<!-- Afficher une variable -->
{{ variable }}

<!-- Accès à un attribut ou une clé de dictionnaire -->
{{ article.titre }}
{{ article.auteur.username }}
{{ dictionnaire.cle }}
{{ liste.0 }}    <!-- Premier élément d'une liste -->

<!-- Variable avec valeur par défaut si None/vide -->
{{ nom|default:"Anonyme" }}
```

### Tags de template

Les tags sont entourés de `{% %}` :

```html
<!-- Condition if/elif/else -->
{% if user.is_authenticated %}
  <p>Bonjour, {{ user.username }} !</p>
{% elif user.is_anonymous %}
  <p>Vous n'êtes pas connecté.</p>
{% else %}
  <p>Situation inconnue.</p>
{% endif %}

<!-- Boucle for -->
{% for article in articles %}
  <article>
    <h2>{{ article.titre }}</h2>
    <p>{{ article.auteur }}</p>
  </article>
{% empty %}
  <p>Aucun article pour le moment.</p>
{% endfor %}

<!-- Variables spéciales dans for -->
{% for article in articles %}
  {{ forloop.counter }}       <!-- Index 1, 2, 3... -->
  {{ forloop.counter0 }}      <!-- Index 0, 1, 2... -->
  {{ forloop.revcounter }}    <!-- Compte à rebours -->
  {{ forloop.first }}         <!-- True pour le premier -->
  {{ forloop.last }}          <!-- True pour le dernier -->
{% endfor %}
```

---

## Les filtres

Les filtres transforment les valeurs : `{{ valeur|filtre }}` ou `{{ valeur|filtre:argument }}`

```html
<!-- Texte -->
{{ titre|upper }}                     <!-- MAJUSCULES -->
{{ titre|lower }}                     <!-- minuscules -->
{{ titre|capfirst }}                  <!-- Première lettre majuscule -->
{{ titre|title }}                     <!-- Chaque Mot En Majuscule -->
{{ contenu|truncatewords:30 }}        <!-- Tronque à 30 mots -->
{{ contenu|truncatechars:150 }}       <!-- Tronque à 150 caractères -->
{{ contenu|linebreaks }}              <!-- Convertit \n en <br> et <p> -->
{{ contenu|linebreaksbr }}            <!-- Convertit \n en <br> seulement -->
{{ html|safe }}                       <!-- Marque comme HTML sûr (ne pas échapper) -->
{{ html|escape }}                     <!-- Échappe les caractères HTML -->
{{ texte|striptags }}                 <!-- Retire les balises HTML -->
{{ texte|wordcount }}                 <!-- Nombre de mots -->
{{ liste|join:", " }}                 <!-- Joint une liste : "a, b, c" -->

<!-- Nombres -->
{{ prix|floatformat:2 }}              <!-- 12.50 -->
{{ grand_nombre|intcomma }}           <!-- 1,234,567 -->

<!-- Dates -->
{{ article.cree_le|date:"d/m/Y" }}        <!-- 15/01/2024 -->
{{ article.cree_le|date:"d F Y à H:i" }}  <!-- 15 janvier 2024 à 14:30 -->
{{ article.cree_le|timesince }}            <!-- "3 jours" -->
{{ article.cree_le|timeuntil }}            <!-- "dans 2 heures" -->

<!-- Divers -->
{{ liste|length }}                    <!-- Longueur -->
{{ valeur|yesno:"oui,non,peut-être" }}  <!-- Oui/Non/Peut-être selon True/False/None -->
{{ liste|first }}                     <!-- Premier élément -->
{{ liste|last }}                      <!-- Dernier élément -->
{{ liste|slice:":3" }}                <!-- 3 premiers éléments -->
{{ dictionnaire|dictsort:"cle" }}     <!-- Trier un dict -->
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Page HTML dans le navigateur montrant un article avec le titre, la date formatée avec `|date:"d F Y"` et le contenu tronqué avec `|truncatewords:50`
> **Expliquer :** Les filtres Django sont composables : `{{ contenu|truncatewords:50|linebreaks }}` applique d'abord la troncature puis convertit les sauts de ligne. Attention à l'ordre des filtres enchaînés.

---

## Héritage de templates

L'héritage permet de définir une structure de base et de la spécialiser dans les templates enfants.

### Template de base

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Mon Blog{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  {% include 'partials/navbar.html' %}

  <main class="container">
    {% if messages %}
      <div class="messages">
        {% for message in messages %}
          <div class="alert alert-{{ message.tags }}">
            {{ message }}
          </div>
        {% endfor %}
      </div>
    {% endif %}

    {% block content %}
    <!-- Le contenu de chaque page va ici -->
    {% endblock %}
  </main>

  {% include 'partials/footer.html' %}

  <script src="{% static 'js/app.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### Template enfant

```html
<!-- articles/templates/articles/liste.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Articles — Mon Blog{% endblock %}

{% block content %}
<h1>Tous les articles</h1>

<div class="articles-grid">
  {% for article in articles %}
    <div class="card">
      {% if article.image_couverture %}
        <img src="{{ article.image_couverture.url }}" alt="{{ article.titre }}">
      {% endif %}

      <div class="card-body">
        <span class="badge">{{ article.categorie.nom }}</span>
        <h2><a href="{{ article.get_absolute_url }}">{{ article.titre }}</a></h2>
        <p>{{ article.contenu|truncatewords:30 }}</p>
        <div class="meta">
          Par {{ article.auteur.get_full_name|default:article.auteur.username }}
          le {{ article.cree_le|date:"d F Y" }}
          · {{ article.nb_vues }} vue{{ article.nb_vues|pluralize }}
        </div>
        <div class="tags">
          {% for tag in article.tags.all %}
            <span class="tag">{{ tag.nom }}</span>
          {% endfor %}
        </div>
      </div>
    </div>
  {% empty %}
    <p class="empty">Aucun article publié pour le moment.</p>
  {% endfor %}
</div>

<!-- Pagination -->
{% if is_paginated %}
  <nav class="pagination">
    {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}">&laquo; Précédent</a>
    {% endif %}
    <span>{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
    {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}">Suivant &raquo;</a>
    {% endif %}
  </nav>
{% endif %}
{% endblock %}

{% block extra_js %}
<script>
  // JavaScript spécifique à cette page
  console.log('Page liste articles chargée');
</script>
{% endblock %}
```

---

## Tags avancés

### `{% include %}` — Inclure un sous-template

```html
<!-- Inclure un template partiel -->
{% include 'partials/article_card.html' %}

<!-- Passer des variables au template inclus -->
{% include 'partials/article_card.html' with article=article %}

<!-- Inclure avec seulement les variables passées (isole le contexte) -->
{% include 'partials/article_card.html' with article=article only %}
```

### `{% url %}` — Générer des URLs

```html
<!-- URL simple -->
<a href="{% url 'articles:liste' %}">Tous les articles</a>

<!-- URL avec paramètre -->
<a href="{% url 'articles:detail' slug=article.slug %}">{{ article.titre }}</a>

<!-- URL avec namespace -->
<a href="{% url 'admin:index' %}">Administration</a>

<!-- Stocker dans une variable -->
{% url 'articles:detail' slug=article.slug as url_article %}
<a href="{{ url_article }}">Lien</a>
```

### `{% static %}` — Fichiers statiques

```html
{% load static %}

<!-- CSS -->
<link rel="stylesheet" href="{% static 'css/main.css' %}">

<!-- JavaScript -->
<script src="{% static 'js/app.js' %}"></script>

<!-- Image -->
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

### `{% with %}` — Variables temporaires

```html
<!-- Éviter de recalculer une valeur -->
{% with total=commande.lignes.count %}
  <p>Votre commande contient {{ total }} article{{ total|pluralize }}.</p>
{% endwith %}
```

### `{% csrf_token %}` — Protection CSRF

```html
<!-- OBLIGATOIRE dans tout formulaire POST -->
<form method="post" action="{% url 'articles:creer' %}">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Enregistrer</button>
</form>
```

---

## Créer des tags et filtres personnalisés

### Structure requise

```
articles/
└── templatetags/
    ├── __init__.py    ← Fichier vide obligatoire
    └── articles_extras.py
```

### Filtres personnalisés

```python
# articles/templatetags/articles_extras.py
from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def jours_depuis(date):
    """Retourne le nombre de jours depuis une date."""
    from django.utils import timezone
    delta = timezone.now().date() - date.date()
    return delta.days

@register.filter
def initiales(user):
    """Retourne les initiales d'un utilisateur."""
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    return user.username[:2].upper()

@register.filter(name='couleur_statut')
def couleur_statut(statut):
    """Retourne une classe CSS selon le statut."""
    couleurs = {
        'brouillon': 'badge-secondary',
        'publie': 'badge-success',
        'archive': 'badge-danger',
    }
    return couleurs.get(statut, 'badge-secondary')
```

### Tags simples

```python
@register.simple_tag
def url_article_admin(article):
    """Retourne l'URL admin d'un article."""
    from django.urls import reverse
    return reverse('admin:articles_article_change', args=[article.pk])

@register.simple_tag(takes_context=True)
def url_actuelle(context):
    """Retourne l'URL courante."""
    return context['request'].path

@register.inclusion_tag('partials/articles_recents.html')
def articles_recents(nombre=5):
    """Tag qui rend un template avec les articles récents."""
    from articles.models import Article
    articles = Article.objects.publies()[:nombre]
    return {'articles': articles}
```

### Utilisation dans les templates

```html
{% load articles_extras %}

<!-- Filtre -->
<p>Publié il y a {{ article.cree_le|jours_depuis }} jours</p>
<span class="badge {{ article.statut|couleur_statut }}">{{ article.statut }}</span>
<span class="avatar">{{ article.auteur|initiales }}</span>

<!-- Tag simple -->
{% url_article_admin article as url_admin %}
<a href="{{ url_admin }}">Modifier dans l'admin</a>

<!-- Inclusion tag -->
{% articles_recents 3 %}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Page de liste d'articles rendue dans le navigateur avec la pagination, les badges de catégorie colorés (via un filtre personnalisé) et les initiales des auteurs
> **Expliquer :** Montrer l'inspecteur d'éléments du navigateur pour expliquer comment les templates génèrent du HTML statique côté serveur (SSR). Comparer avec une approche SPA (Vue/React) pour illustrer les cas d'usage de chacun.

---

## Context Processors

Les context processors ajoutent des variables disponibles dans TOUS les templates :

```python
# articles/context_processors.py
def parametres_site(request):
    """Disponible dans tous les templates."""
    from .models import Categorie
    return {
        'categories_nav': Categorie.objects.all()[:10],
        'nom_site': 'Mon Blog',
        'annee_actuelle': 2024,
    }
```

```python
# config/settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ...
            'articles.context_processors.parametres_site',
        ],
    },
}]
```

Utilisation dans tout template sans passer les variables depuis la vue :

```html
<!-- Dans n'importe quel template -->
<title>{{ nom_site }}</title>
<nav>
  {% for categorie in categories_nav %}
    <a href="{% url 'articles:par_categorie' slug=categorie.slug %}">
      {{ categorie.nom }}
    </a>
  {% endfor %}
</nav>
```

---

## Bonnes pratiques

### Template de formulaire réutilisable

```html
<!-- partials/form_field.html -->
<div class="form-group {% if field.errors %}has-error{% endif %}">
  <label for="{{ field.id_for_label }}">
    {{ field.label }}
    {% if field.field.required %}<span class="required">*</span>{% endif %}
  </label>
  {{ field }}
  {% if field.help_text %}
    <small class="help-text">{{ field.help_text }}</small>
  {% endif %}
  {% for error in field.errors %}
    <span class="error">{{ error }}</span>
  {% endfor %}
</div>
```

```html
<!-- Dans un formulaire -->
<form method="post">
  {% csrf_token %}
  {% for field in form %}
    {% include 'partials/form_field.html' with field=field %}
  {% endfor %}
  <button type="submit">Enregistrer</button>
</form>
```

---

## Résumé

- Les templates utilisent `{{ var }}` pour afficher et `{% tag %}` pour la logique
- L'**héritage** (`extends` + `block`) évite la duplication du layout
- Les **filtres** transforment les valeurs : `|date`, `|truncatewords`, `|upper`
- `{% include %}` permet de découper les templates en composants réutilisables
- `{% url %}` génère des URLs — ne jamais coder les URLs en dur
- `{% csrf_token %}` est obligatoire dans tout formulaire POST
- Les tags/filtres personnalisés s'écrivent dans `templatetags/`

## Prochaine étape

Passez au module [05 — Admin](05-admin.md) pour découvrir l'interface d'administration Django.
