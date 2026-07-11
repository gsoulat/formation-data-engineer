# ORM Django — 02 : Relations

## Vue d'ensemble des relations

Django supporte les trois types de relations SQL :

| Type | Django | SQL |
|------|--------|-----|
| Many-to-One | `ForeignKey` | Clé étrangère dans la table enfant |
| Many-to-Many | `ManyToManyField` | Table de jointure automatique |
| One-to-One | `OneToOneField` | Clé étrangère unique |

---

## ForeignKey (Many-to-One)

### Définition

```python
# articles/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Categorie(models.Model):
    nom = models.CharField(max_length=100)

class Article(models.Model):
    titre     = models.CharField(max_length=200)
    auteur    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',       # Pour accès inverse : user.articles.all()
        related_query_name='article',  # Pour filtres : User.objects.filter(article__statut=...)
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
```

### Accès direct (sens FK)

```python
article = Article.objects.get(pk=1)

# Accès à l'objet lié
article.auteur          # Objet User (1 requête SQL si pas de select_related)
article.auteur_id       # Juste l'ID — PAS de requête SQL supplémentaire !
article.categorie       # Objet Categorie ou None

# Toujours utiliser _id quand vous n'avez besoin que de l'ID
if article.auteur_id == request.user.pk:  # Efficace
    pass
if article.auteur == request.user:         # Déclenche une requête si auteur non chargé
    pass
```

### Accès inverse (depuis le parent)

```python
user = User.objects.get(username='alice')

# related_name permet l'accès inverse
user.articles.all()                    # QuerySet de ses articles
user.articles.filter(statut='publie') # Articles publiés d'Alice
user.articles.count()                  # Nombre d'articles

# Sans related_name défini, Django crée automatiquement : article_set
# user.article_set.all()

categorie = Categorie.objects.first()
categorie.articles.all()               # Tous les articles de cette catégorie
categorie.articles.select_related('auteur')
```

---

## ManyToManyField

### Définition simple

```python
class Tag(models.Model):
    nom  = models.CharField(max_length=50, unique=True)

class Article(models.Model):
    titre = models.CharField(max_length=200)
    tags  = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,          # Pas obligatoire d'avoir des tags
    )
    # Django crée automatiquement la table articles_article_tags
    # avec les colonnes article_id et tag_id
```

### Opérations M2M

```python
article = Article.objects.get(pk=1)
tag_python = Tag.objects.get(nom='python')
tag_django = Tag.objects.get(nom='django')

# Ajouter
article.tags.add(tag_python)
article.tags.add(tag_python, tag_django)          # Plusieurs à la fois
article.tags.add(*Tag.objects.filter(nom__in=['a', 'b']))  # Depuis un QuerySet

# Retirer
article.tags.remove(tag_python)

# Remplacer tous les tags
article.tags.set([tag_python, tag_django])

# Vider
article.tags.clear()

# Vérifier
article.tags.exists()
article.tags.filter(nom='python').exists()

# Lire
article.tags.all()
article.tags.filter(nom__startswith='py')
article.tags.count()

# Accès inverse
tag_python.articles.all()  # Tous les articles avec ce tag
```

### Table de jointure personnalisée (through)

Utile quand on veut stocker des données sur la relation elle-même :

```python
class Article(models.Model):
    titre = models.CharField(max_length=200)
    tags  = models.ManyToManyField(
        'Tag',
        through='ArticleTag',      # Table intermédiaire explicite
        related_name='articles',
        blank=True,
    )

class Tag(models.Model):
    nom = models.CharField(max_length=50)

class ArticleTag(models.Model):
    """Table de jointure avec données supplémentaires."""
    article   = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag       = models.ForeignKey(Tag, on_delete=models.CASCADE)
    ajoute_le = models.DateTimeField(auto_now_add=True)
    ajoute_par = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    pertinence = models.PositiveSmallIntegerField(default=5)  # 1 à 10

    class Meta:
        unique_together = [['article', 'tag']]
        ordering = ['-pertinence']

# Avec through, on utilise la table intermédiaire directement :
ArticleTag.objects.create(
    article=article,
    tag=tag_python,
    ajoute_par=request.user,
    pertinence=9,
)

# L'API .add() n'est plus disponible avec through (sauf si through_defaults)
article.tags.add(tag, through_defaults={'ajoute_par': user, 'pertinence': 8})
```

---

## OneToOneField

```python
class ProfilUtilisateur(models.Model):
    user      = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
    )
    bio       = models.TextField(blank=True)
    avatar    = models.ImageField(upload_to='avatars/', blank=True)
    telephone = models.CharField(max_length=20, blank=True)

# Accès
user = User.objects.get(pk=1)
user.profil             # L'objet ProfilUtilisateur (lève RelatedObjectDoesNotExist si absent)
user.profil.bio

profil = ProfilUtilisateur.objects.get(user=user)
profil.user             # L'objet User associé
```

### Créer automatiquement le profil

```python
# Via signal post_save
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        ProfilUtilisateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def sauvegarder_profil(sender, instance, **kwargs):
    try:
        instance.profil.save()
    except ProfilUtilisateur.DoesNotExist:
        ProfilUtilisateur.objects.create(user=instance)
```

---

## Requêtes sur les relations

### Traversée en profondeur

```python
# Articles dont l'auteur a un email Gmail
Article.objects.filter(auteur__email__endswith='@gmail.com')

# Articles avec un tag dont le nom commence par 'py'
Article.objects.filter(tags__nom__startswith='py')

# Articles d'une catégorie avec au moins 5 articles (annotation + filtre)
from django.db.models import Count
Article.objects.filter(
    categorie__articles__count__gte=5  # Pas valide : il faut annoter
)
# Correct :
categories_riches = Categorie.objects.annotate(
    nb=Count('articles')
).filter(nb__gte=5)
Article.objects.filter(categorie__in=categories_riches)
```

### `select_related` — optimiser les FK et O2O

```python
# 1 requête avec JOIN plutôt que N+1
articles = Article.objects.select_related(
    'auteur',           # JOIN sur User
    'auteur__profil',   # JOIN en profondeur
    'categorie',        # JOIN sur Categorie
)

# Depuis l'accès inverse : utiliser select_related côté enfant
Commentaire.objects.select_related('article', 'article__auteur', 'auteur')
```

### `prefetch_related` — optimiser les M2M et FK inverse

```python
# 2 requêtes : une pour articles, une pour tags
articles = Article.objects.prefetch_related('tags')

# 3 requêtes : articles + tags + commentaires
articles = Article.objects.prefetch_related('tags', 'commentaires')

# Prefetch personnalisé avec filtre
from django.db.models import Prefetch

commentaires_approuves = Commentaire.objects.filter(approuve=True).select_related('auteur')

articles = Article.objects.prefetch_related(
    Prefetch(
        'commentaires',
        queryset=commentaires_approuves,
        to_attr='commentaires_approuves',  # Accessible via article.commentaires_approuves
    )
)

# Accès
for article in articles:
    print(article.commentaires_approuves)  # Liste Python directe
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Shell Django montrant la différence entre `connection.queries` avant et après une requête avec et sans `select_related`, affichant le nombre de requêtes SQL
> **Expliquer :** Taper ces commandes dans le shell : `from django.db import connection`, `connection.queries`, `connection.reset_queries()`. Ensuite, boucler sur des articles sans et avec select_related pour voir le nombre de requêtes.

---

## Relations auto-référentielles

Un modèle peut avoir une relation sur lui-même :

```python
class Categorie(models.Model):
    nom    = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',                         # Référence au même modèle
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_categories',
    )

# Arbres de catégories
informatique = Categorie.objects.get(nom='Informatique')
informatique.sous_categories.all()  # Python, Django, JavaScript, ...

python = Categorie.objects.get(nom='Python')
python.parent                        # Informatique
```

### Hiérarchie d'employés

```python
class Employe(models.Model):
    nom     = models.CharField(max_length=100)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordonnés',
    )

def get_hierarchie(employe, niveau=0):
    print("  " * niveau + employe.nom)
    for subordonné in employe.subordonnés.all():
        get_hierarchie(subordonné, niveau + 1)
```

---

## Relations génériques (ContentTypes)

```python
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Commentaire(models.Model):
    """Commentaire générique pouvant être attaché à n'importe quel objet."""
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    auteur  = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    titre       = models.CharField(max_length=200)
    commentaires = GenericRelation(Commentaire)  # Accès inverse optionnel

class Produit(models.Model):
    nom          = models.CharField(max_length=200)
    commentaires = GenericRelation(Commentaire)

# Utilisation
article = Article.objects.get(pk=1)
produit = Produit.objects.get(pk=5)

# Créer un commentaire générique
Commentaire.objects.create(
    content_object=article,  # Django gère content_type et object_id
    auteur=user,
    contenu="Super article !",
)

# Accéder aux commentaires
article.commentaires.all()
produit.commentaires.filter(auteur=user)
```

---

## Bonnes pratiques

### Nommage des `related_name`

```python
# Convention recommandée : pluriel du modèle
class Article(models.Model):
    auteur    = models.ForeignKey(User, related_name='articles', ...)
    categorie = models.ForeignKey(Categorie, related_name='articles', ...)
    # user.articles.all(), categorie.articles.all()

# Si plusieurs FK vers le même modèle, éviter les conflits
class Commande(models.Model):
    acheteur  = models.ForeignKey(User, related_name='commandes_achat', ...)
    vendeur   = models.ForeignKey(User, related_name='commandes_vente', ...)
    # user.commandes_achat.all(), user.commandes_vente.all()

# Pour désactiver le related_name (si accès inverse inutile)
models.ForeignKey(User, related_name='+', ...)
```

### Éviter les imports circulaires

```python
# Utiliser une chaîne de caractères pour référencer un modèle pas encore défini
class Article(models.Model):
    auteur = models.ForeignKey(
        'auth.User',    # 'appname.ModelName' — pas besoin d'import
        on_delete=models.CASCADE,
    )
    categorie = models.ForeignKey(
        'Categorie',    # Dans la même app
        on_delete=models.CASCADE,
    )
```

---

## Résumé

| Relation | Direction | Accès | Optimisation |
|----------|-----------|-------|--------------|
| `ForeignKey` | Objet → Parent | `obj.parent` | `select_related` |
| `ForeignKey` inverse | Parent → Objets | `parent.objets.all()` | `prefetch_related` |
| `ManyToManyField` | Les deux | `obj.tags.all()` | `prefetch_related` |
| `OneToOneField` | Objet → Lié | `obj.profil` | `select_related` |
| `OneToOneField` inverse | Lié → Objet | `user.profil` | `select_related` |

## Prochaine étape

Passez au module [03 — Migrations](03-migrations.md) pour gérer l'évolution de votre schéma de base de données.
