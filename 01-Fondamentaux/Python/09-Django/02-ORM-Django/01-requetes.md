# ORM Django — 01 : Requêtes et QuerySet

## Qu'est-ce qu'un QuerySet ?

Un `QuerySet` est une collection d'objets Django issus d'une table. Il est **paresseux** (lazy) : la requête SQL n'est exécutée que lorsque les données sont réellement nécessaires.

```python
# La requête SQL n'est PAS encore envoyée ici
articles = Article.objects.filter(statut='publie')

# La requête est exécutée ici (itération)
for article in articles:
    print(article.titre)

# Ou ici (évaluation)
liste = list(articles)
nombre = articles.count()
premier = articles.first()
```

---

## Récupérer des objets

### Tous les objets

```python
# SELECT * FROM articles_article;
Article.objects.all()

# Ordonné
Article.objects.all().order_by('-cree_le')  # DESC
Article.objects.all().order_by('titre', '-cree_le')  # Multi-champs
```

### Filtrage

```python
# WHERE statut = 'publie'
Article.objects.filter(statut='publie')

# WHERE statut != 'archive'
Article.objects.exclude(statut='archive')

# Plusieurs filtres (AND implicite)
Article.objects.filter(statut='publie', mis_en_avant=True)

# Équivalent avec enchaînement
Article.objects.filter(statut='publie').filter(mis_en_avant=True)

# Récupérer un objet unique — lève DoesNotExist ou MultipleObjectsReturned
Article.objects.get(pk=1)
Article.objects.get(slug='mon-article')

# Sécurisé — retourne None si absent
Article.objects.filter(pk=1).first()

# get ou créer — retourne (objet, créé_bool)
article, cree = Article.objects.get_or_create(
    slug='mon-article',
    defaults={'titre': 'Mon article', 'auteur': user},
)

# Créer ou mettre à jour
Article.objects.update_or_create(
    slug='mon-article',
    defaults={'titre': 'Titre mis à jour'},
)
```

### Raccourcis

```python
# get_object_or_404 — pour les vues (lève Http404)
from django.shortcuts import get_object_or_404
article = get_object_or_404(Article, slug='mon-article', statut='publie')

# get_list_or_404 — lève Http404 si la liste est vide
from django.shortcuts import get_list_or_404
articles = get_list_or_404(Article, statut='publie')
```

---

## Les lookups (opérateurs de filtrage)

```python
# Égalité (par défaut)
Article.objects.filter(statut='publie')
Article.objects.filter(statut__exact='publie')  # équivalent

# Comparaisons
Article.objects.filter(nb_vues__gt=100)    # >
Article.objects.filter(nb_vues__gte=100)   # >=
Article.objects.filter(nb_vues__lt=10)     # <
Article.objects.filter(nb_vues__lte=10)    # <=

# Texte
Article.objects.filter(titre__contains='Django')       # LIKE '%Django%'
Article.objects.filter(titre__icontains='django')      # ILIKE '%django%'
Article.objects.filter(titre__startswith='Django')     # LIKE 'Django%'
Article.objects.filter(titre__istartswith='django')    # ILIKE 'django%'
Article.objects.filter(titre__endswith='Python')       # LIKE '%Python'
Article.objects.filter(titre__regex=r'^[A-Z]')         # Regex case-sensitive
Article.objects.filter(titre__iregex=r'^[a-z]')        # Regex case-insensitive

# Listes
Article.objects.filter(statut__in=['publie', 'archive'])
Article.objects.exclude(statut__in=['brouillon'])

# Null / non-null
Article.objects.filter(image_couverture__isnull=True)
Article.objects.filter(image_couverture__isnull=False)

# Dates
from datetime import date, timedelta
Article.objects.filter(cree_le__date=date.today())
Article.objects.filter(cree_le__year=2024)
Article.objects.filter(cree_le__month=1)
Article.objects.filter(cree_le__day=15)
Article.objects.filter(cree_le__week=3)
Article.objects.filter(cree_le__gte=date.today() - timedelta(days=7))

# Traversée de relations (double underscore)
Article.objects.filter(auteur__username='alice')
Article.objects.filter(auteur__email__endswith='@gmail.com')
Article.objects.filter(categorie__nom='Python')
Article.objects.filter(tags__nom__in=['python', 'django'])
```

---

## Opérateurs logiques Q

```python
from django.db.models import Q

# OR
Article.objects.filter(Q(statut='publie') | Q(mis_en_avant=True))

# AND explicite
Article.objects.filter(Q(statut='publie') & Q(mis_en_avant=True))

# NOT
Article.objects.filter(~Q(statut='archive'))

# Combinaison complexe
Article.objects.filter(
    (Q(statut='publie') | Q(mis_en_avant=True)) & ~Q(categorie__nom='Non classé')
)
```

---

## Mise à jour et suppression

```python
# Mise à jour d'un seul objet
article = Article.objects.get(pk=1)
article.titre = 'Nouveau titre'
article.save()

# Mise à jour de champs spécifiques seulement (plus efficace)
article.save(update_fields=['titre', 'statut'])

# Mise à jour en masse (SQL UPDATE direct — ne déclenche pas save())
Article.objects.filter(statut='brouillon').update(statut='archive')

# Incrémenter avec F() (atomique, sans race condition)
from django.db.models import F
Article.objects.filter(pk=1).update(nb_vues=F('nb_vues') + 1)

# Suppression d'un objet
article.delete()

# Suppression en masse
Article.objects.filter(statut='archive', cree_le__year=2022).delete()
# Retourne : (nombre_supprimés, {'articles.Article': N, 'articles.Commentaire': M})
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec `python manage.py shell` ouvert, en train d'exécuter plusieurs requêtes QuerySet et d'afficher le SQL généré avec `.query`
> **Expliquer :** Taper `str(Article.objects.filter(statut='publie').query)` pour afficher le SQL généré. Montrer comment les QuerySets sont composables et que le SQL n'est envoyé qu'à l'évaluation. C'est un outil de débogage précieux.

---

## Agrégation et annotation

### Aggregate — résultat unique

```python
from django.db.models import Count, Sum, Avg, Max, Min

# Compter les articles publiés
Article.objects.filter(statut='publie').count()

# Aggregate — retourne un dictionnaire
from django.db.models import Avg, Sum, Max, Min, Count

stats = Article.objects.aggregate(
    total=Count('id'),
    vues_totales=Sum('nb_vues'),
    vues_moyennes=Avg('nb_vues'),
    vues_max=Max('nb_vues'),
    vues_min=Min('nb_vues'),
)
# {'total': 42, 'vues_totales': 12500, 'vues_moyennes': 297.6, ...}
```

### Annotate — valeur par objet

```python
# Ajouter le nombre de commentaires sur chaque article
articles = Article.objects.annotate(
    nb_commentaires=Count('commentaires'),
).order_by('-nb_commentaires')

for article in articles:
    print(f"{article.titre} : {article.nb_commentaires} commentaires")

# Filtrer sur une annotation
Article.objects.annotate(
    nb_commentaires=Count('commentaires')
).filter(nb_commentaires__gte=5)

# Annoter avec une sous-requête
from django.db.models import OuterRef, Subquery
dernier_commentaire = Commentaire.objects.filter(
    article=OuterRef('pk')
).order_by('-cree_le').values('contenu')[:1]

articles = Article.objects.annotate(
    dernier_commentaire=Subquery(dernier_commentaire)
)
```

---

## Optimisation des requêtes

### Le problème N+1

```python
# MAL : 1 requête pour les articles + N requêtes pour chaque auteur
articles = Article.objects.all()
for article in articles:
    print(article.auteur.username)  # Requête SQL à chaque itération !
```

### `select_related` — pour ForeignKey et OneToOne

```python
# BIEN : 1 seule requête avec JOIN
articles = Article.objects.select_related('auteur', 'categorie').all()
for article in articles:
    print(article.auteur.username)  # Pas de requête supplémentaire

# Traversal profond
Article.objects.select_related('auteur__profile', 'categorie')
```

### `prefetch_related` — pour ManyToMany et FK inverse

```python
# BIEN : 2 requêtes (articles + tags) au lieu de N+1
articles = Article.objects.prefetch_related('tags').all()
for article in articles:
    for tag in article.tags.all():  # Utilise le prefetch
        print(tag.nom)

# Prefetch avec filtre
from django.db.models import Prefetch
commentaires_approuves = Commentaire.objects.filter(approuve=True)

articles = Article.objects.prefetch_related(
    Prefetch('commentaires', queryset=commentaires_approuves, to_attr='bons_commentaires')
).all()

for article in articles:
    print(article.bons_commentaires)  # Liste Python, pas QuerySet
```

### `only` et `defer` — charger seulement certains champs

```python
# Charger seulement titre et auteur_id (évite de charger TextField contenu)
Article.objects.only('titre', 'auteur_id')

# Charger tout SAUF le gros TextField
Article.objects.defer('contenu')
```

### `values` et `values_list` — récupérer des dictionnaires

```python
# Dictionnaires au lieu d'objets Python
Article.objects.values('id', 'titre', 'statut')
# [{'id': 1, 'titre': '...', 'statut': 'publie'}, ...]

# Tuples (plus léger)
Article.objects.values_list('id', 'titre')
# [(1, 'Mon article'), (2, 'Autre article'), ...]

# Colonne unique : flat=True
Article.objects.values_list('titre', flat=True)
# ['Mon article', 'Autre article', ...]

# Très utile pour les lookups __in
ids_publies = Article.objects.filter(statut='publie').values_list('id', flat=True)
Commentaire.objects.filter(article_id__in=ids_publies)
```

---

## Opérations de set

```python
# Union (UNION SQL)
qs1 = Article.objects.filter(statut='publie')
qs2 = Article.objects.filter(mis_en_avant=True)
tous = qs1.union(qs2)

# Intersection
communs = qs1.intersection(qs2)

# Différence
seulement_qs1 = qs1.difference(qs2)
```

---

## Expressions F() et Value()

```python
from django.db.models import F, Value, ExpressionWrapper, IntegerField
from django.db.models.functions import Concat, Upper, Lower, Length

# Comparer deux champs entre eux
Article.objects.filter(modifie_le__gt=F('cree_le'))

# Calculer une expression
Article.objects.annotate(
    ratio_vues=ExpressionWrapper(
        F('nb_vues') / (F('nb_commentaires') + 1),
        output_field=IntegerField(),
    )
)

# Fonctions SQL
Article.objects.annotate(
    titre_long=Length('titre'),
    titre_majuscule=Upper('titre'),
)

# Concaténation
from django.contrib.auth.models import User
User.objects.annotate(
    nom_complet=Concat('first_name', Value(' '), 'last_name')
)
```

---

## Transactions

```python
from django.db import transaction

# Transaction atomique — tout ou rien
with transaction.atomic():
    article = Article.objects.create(titre='Nouvel article', auteur=user)
    Tag.objects.create(nom='nouveau-tag')
    # Si une erreur est levée ici, les deux créations sont annulées

# Décorateur
@transaction.atomic
def creer_article_avec_tags(titre, tags, auteur):
    article = Article.objects.create(titre=titre, auteur=auteur)
    for nom_tag in tags:
        tag, _ = Tag.objects.get_or_create(nom=nom_tag)
        article.tags.add(tag)
    return article

# Savepoint
with transaction.atomic():
    article = Article.objects.create(titre='Article', auteur=user)
    sid = transaction.savepoint()
    try:
        article.publier()
    except Exception:
        transaction.savepoint_rollback(sid)
    transaction.savepoint_commit(sid)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Django Debug Toolbar montrant la différence entre une liste de vues sans `select_related` (20+ requêtes SQL) et avec (2 requêtes SQL), avec les temps d'exécution
> **Expliquer :** Le problème N+1 est l'une des causes les plus fréquentes de performances médiocres dans les applications Django. Toujours utiliser `select_related` pour les FK et `prefetch_related` pour les M2M quand on boucle sur des objets.

---

## Résumé des méthodes QuerySet

| Méthode | SQL généré | Retourne |
|---------|-----------|---------|
| `.all()` | SELECT * | QuerySet |
| `.filter(**kwargs)` | WHERE | QuerySet |
| `.exclude(**kwargs)` | WHERE NOT | QuerySet |
| `.order_by(field)` | ORDER BY | QuerySet |
| `.distinct()` | DISTINCT | QuerySet |
| `.values(*fields)` | SELECT fields | QuerySet de dicts |
| `.values_list(*fields)` | SELECT fields | QuerySet de tuples |
| `.select_related(*fields)` | JOIN | QuerySet |
| `.prefetch_related(*fields)` | + requêtes séparées | QuerySet |
| `.annotate(**expr)` | + colonnes calculées | QuerySet |
| `.aggregate(**expr)` | SELECT agrégat | Dictionnaire |
| `.count()` | COUNT | Entier |
| `.exists()` | EXISTS | Booléen |
| `.first()` | LIMIT 1 | Objet ou None |
| `.last()` | LIMIT 1 ORDER BY DESC | Objet ou None |
| `.get(**kwargs)` | WHERE | Objet (ou exception) |
| `.create(**kwargs)` | INSERT | Objet |
| `.update(**kwargs)` | UPDATE | Entier (nb modifiés) |
| `.delete()` | DELETE | Tuple (nb, dict) |
| `.bulk_create(list)` | INSERT en masse | Liste d'objets |
| `.bulk_update(list, fields)` | UPDATE en masse | Entier |

## Prochaine étape

Passez au module [02 — Relations](02-relations.md) pour maîtriser les requêtes sur les objets liés.
