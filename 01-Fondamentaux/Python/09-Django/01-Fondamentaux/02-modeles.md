# 02 — Modèles Django

## Qu'est-ce qu'un modèle ?

Un modèle Django est une classe Python qui représente une table en base de données. Chaque attribut de la classe correspond à une colonne. Django génère automatiquement le SQL à partir de vos modèles.

```python
# articles/models.py
from django.db import models

class Article(models.Model):
    titre   = models.CharField(max_length=200)
    contenu = models.TextField()
    publie  = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    # Django crée automatiquement :
    # - une colonne id (BigAutoField, clé primaire)
    # - la table "articles_article" en base
```

---

## Les types de champs principaux

### Champs texte

```python
class Exemple(models.Model):
    # Chaîne courte obligatoire — max_length requis
    nom = models.CharField(max_length=100)

    # Chaîne courte optionnelle
    surnom = models.CharField(max_length=50, blank=True, default='')

    # Texte long sans limite
    biographie = models.TextField()

    # Texte optionnel (peut être NULL en BDD)
    notes = models.TextField(blank=True, null=True)

    # Email validé automatiquement
    email = models.EmailField(unique=True)

    # URL validée
    site_web = models.URLField(blank=True)

    # UUID — utile pour les IDs publics
    import uuid
    identifiant = models.UUIDField(default=uuid.uuid4, editable=False)

    # Slug (url-friendly)
    slug = models.SlugField(max_length=200, unique=True)
```

### Champs numériques

```python
class Produit(models.Model):
    # Entiers
    quantite   = models.IntegerField(default=0)
    stock      = models.PositiveIntegerField()       # >= 0
    ref_interne = models.SmallIntegerField()          # -32768 à 32767
    gros_nombre = models.BigIntegerField()

    # Décimaux — TOUJOURS utiliser DecimalField pour l'argent
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    # Float (imprécis, éviter pour l'argent)
    note = models.FloatField()
```

### Champs date/heure

```python
class Evenement(models.Model):
    # Date seule : 2024-01-15
    date_debut = models.DateField()

    # Heure seule : 14:30:00
    heure_debut = models.TimeField()

    # Date + heure : 2024-01-15 14:30:00+01:00
    cree_le = models.DateTimeField(auto_now_add=True)  # Rempli à la création
    modifie_le = models.DateTimeField(auto_now=True)   # Mis à jour à chaque save()

    # Date choisie par l'utilisateur
    date_publication = models.DateTimeField(null=True, blank=True)

    # Durée
    duree = models.DurationField()
```

### Autres champs

```python
class Parametre(models.Model):
    actif      = models.BooleanField(default=True)
    image      = models.ImageField(upload_to='images/', blank=True)
    fichier    = models.FileField(upload_to='documents/')
    ip_address = models.GenericIPAddressField()

    # Choix limités (enum)
    STATUTS = [
        ('brouillon',   'Brouillon'),
        ('publie',      'Publié'),
        ('archive',     'Archivé'),
    ]
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
```

---

## Options des champs

| Option | Description | Exemple |
|--------|-------------|---------|
| `null=True` | Autorise NULL en BDD | `TextField(null=True)` |
| `blank=True` | Autorise vide dans les formulaires | `CharField(blank=True)` |
| `default=...` | Valeur par défaut | `BooleanField(default=True)` |
| `unique=True` | Contrainte d'unicité | `EmailField(unique=True)` |
| `db_index=True` | Créer un index SQL | `CharField(db_index=True)` |
| `editable=False` | Masqué dans les formulaires | `UUIDField(editable=False)` |
| `verbose_name` | Libellé lisible | `CharField(verbose_name="Prénom")` |
| `help_text` | Texte d'aide formulaire | `CharField(help_text="Ex: Jean")` |

> **Règle importante** : Pour les champs texte, ne pas utiliser `null=True`. Préférer `blank=True, default=''`. Cela évite d'avoir deux valeurs "vide" possibles (NULL et "").

---

## La classe Meta

La classe interne `Meta` permet de configurer le comportement du modèle :

```python
class Article(models.Model):
    titre        = models.CharField(max_length=200)
    date_creation = models.DateTimeField(auto_now_add=True)
    auteur       = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        # Nom de la table en BDD (par défaut : appname_modelname)
        db_table = 'blog_articles'

        # Tri par défaut (- = décroissant)
        ordering = ['-date_creation']

        # Contrainte d'unicité composite
        unique_together = [['titre', 'auteur']]

        # Nom lisible dans l'admin (singulier / pluriel)
        verbose_name = 'article'
        verbose_name_plural = 'articles'

        # Permissions personnalisées
        permissions = [
            ('can_publish', 'Peut publier des articles'),
        ]

        # Index composites
        indexes = [
            models.Index(fields=['titre', '-date_creation'], name='article_titre_date_idx'),
        ]
```

---

## La méthode `__str__`

Toujours définir `__str__` pour avoir un affichage lisible dans l'admin et le shell :

```python
class Article(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titre} — par {self.auteur.username}"

class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Shell Django avec `python manage.py shell`, puis `from articles.models import Article; Article.objects.all()` montrant la représentation `__str__`
> **Expliquer :** Montrer la différence entre un modèle avec et sans `__str__`. Sans : `<QuerySet [<Article: Article object (1)>]>`. Avec : `<QuerySet [<Article: Mon premier article — par admin]>`. L'admin Django utilise aussi `__str__` partout.

---

## Les relations

### ForeignKey (Many-to-One)

```python
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

class Article(models.Model):
    titre     = models.CharField(max_length=200)
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,      # Supprime les articles si la catégorie est supprimée
        related_name='articles',        # Nom pour accéder en sens inverse
        null=True,
        blank=True,
    )

# Utilisation
article = Article.objects.first()
print(article.categorie.nom)      # Accès à la catégorie

categorie = Categorie.objects.first()
print(categorie.articles.all())   # Tous les articles de cette catégorie (related_name)
```

Options `on_delete` :

| Option | Comportement |
|--------|-------------|
| `CASCADE` | Supprime les objets liés |
| `PROTECT` | Empêche la suppression si des objets liés existent |
| `SET_NULL` | Met la FK à NULL (requiert `null=True`) |
| `SET_DEFAULT` | Met la valeur par défaut |
| `DO_NOTHING` | Ne fait rien (risque d'erreur d'intégrité) |

### ManyToManyField

```python
class Tag(models.Model):
    nom = models.CharField(max_length=50)

class Article(models.Model):
    titre = models.CharField(max_length=200)
    tags  = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,
    )

# Utilisation
article = Article.objects.first()
article.tags.add(Tag.objects.get(nom='python'))    # Ajouter un tag
article.tags.remove(Tag.objects.get(nom='django')) # Retirer un tag
article.tags.set([tag1, tag2])                      # Remplacer tous les tags
article.tags.clear()                                # Retirer tous les tags
article.tags.all()                                  # Tous les tags de l'article
```

### OneToOneField

```python
# Étendre le modèle User sans le modifier
class ProfilUtilisateur(models.Model):
    user      = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    bio       = models.TextField(blank=True)
    avatar    = models.ImageField(upload_to='avatars/', blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

# Accès
user = User.objects.get(username='alice')
print(user.profilutilisateur.bio)  # Accès via related_name par défaut
```

---

## Les Managers

Le manager par défaut est `objects`. Vous pouvez en créer des personnalisés :

```python
class ArticleManager(models.Manager):
    def publies(self):
        return self.filter(statut='publie')

    def par_auteur(self, auteur):
        return self.filter(auteur=auteur)

class Article(models.Model):
    titre  = models.CharField(max_length=200)
    statut = models.CharField(max_length=20, default='brouillon')
    auteur = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    # Remplace le manager par défaut
    objects = ArticleManager()

# Utilisation
Article.objects.publies()              # SELECT ... WHERE statut='publie'
Article.objects.par_auteur(user)       # SELECT ... WHERE auteur_id=1
Article.objects.publies().count()      # Chaînable avec QuerySet
```

---

## Méthodes personnalisées sur les modèles

```python
from django.utils.text import slugify
from django.urls import reverse

class Article(models.Model):
    titre        = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True, blank=True)
    contenu      = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    statut       = models.CharField(max_length=20, default='brouillon')
    auteur       = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Auto-générer le slug à la création
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # URL canonique de l'objet — utilisée par l'admin
        return reverse('articles:detail', kwargs={'slug': self.slug})

    @property
    def est_publie(self):
        return self.statut == 'publie'

    @property
    def extrait(self):
        return self.contenu[:200] + '...' if len(self.contenu) > 200 else self.contenu

    def publier(self):
        self.statut = 'publie'
        self.save(update_fields=['statut'])

    def __str__(self):
        return self.titre
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** `python manage.py makemigrations` puis `python manage.py migrate` avec la sortie montrant les tables créées
> **Expliquer :** Chaque modification de modèle nécessite une migration. Django génère le SQL automatiquement. Montrer le fichier de migration généré dans `migrations/0001_initial.py` et expliquer que ce fichier doit être commité dans git.

---

## Exemple complet : modèles d'un blog

```python
# articles/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()  # Toujours utiliser get_user_model() plutôt que User directement


class Categorie(models.Model):
    nom         = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'catégorie'
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
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom


class ArticleManager(models.Manager):
    def publies(self):
        return self.filter(statut='publie')


class Article(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('publie',    'Publié'),
        ('archive',   'Archivé'),
    ]

    titre          = models.CharField(max_length=200, verbose_name='Titre')
    slug           = models.SlugField(max_length=200, unique=True, blank=True)
    contenu        = models.TextField()
    image_couverture = models.ImageField(upload_to='articles/covers/', blank=True)
    statut         = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    mis_en_avant   = models.BooleanField(default=False)
    nb_vues        = models.PositiveIntegerField(default=0)

    auteur         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    categorie      = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    tags           = models.ManyToManyField(Tag, related_name='articles', blank=True)

    cree_le        = models.DateTimeField(auto_now_add=True)
    modifie_le     = models.DateTimeField(auto_now=True)
    publie_le      = models.DateTimeField(null=True, blank=True)

    objects = ArticleManager()

    class Meta:
        verbose_name = 'article'
        ordering = ['-cree_le']
        indexes = [
            models.Index(fields=['statut', '-cree_le']),
        ]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    @property
    def est_publie(self):
        return self.statut == 'publie'


class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    auteur  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentaires')
    contenu = models.TextField()
    approuve = models.BooleanField(default=False)
    cree_le  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['cree_le']

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur '{self.article.titre}'"
```

---

## Résumé

- Les modèles héritent de `models.Model`
- Chaque champ est un type Python mappé vers un type SQL
- `__str__` est obligatoire pour tout modèle
- La classe `Meta` configure le tri, les contraintes, les noms
- Les managers permettent d'encapsuler des requêtes fréquentes
- Après toute modification : `makemigrations` + `migrate`

## Prochaine étape

Passez au module [03 — Vues](03-vues.md) pour apprendre à exposer vos données.
