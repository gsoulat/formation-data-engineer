# ORM Django — 03 : Migrations

## Qu'est-ce qu'une migration ?

Une migration est un fichier Python qui décrit une modification du schéma de base de données. Django les génère automatiquement à partir des changements de vos modèles et les applique dans l'ordre.

```
Modèle Python → makemigrations → Fichier de migration → migrate → SQL → BDD
```

---

## Commandes essentielles

```bash
# Détecter les changements et créer les fichiers de migration
python manage.py makemigrations

# Pour une app spécifique
python manage.py makemigrations articles

# Avec un nom explicite
python manage.py makemigrations articles --name="ajouter_champ_statut"

# Appliquer toutes les migrations en attente
python manage.py migrate

# Appliquer les migrations d'une app spécifique
python manage.py migrate articles

# Revenir à une migration précise (rollback)
python manage.py migrate articles 0003

# Revenir au début (annuler toutes les migrations d'une app)
python manage.py migrate articles zero

# Voir l'état des migrations
python manage.py showmigrations

# Voir le SQL qui serait exécuté (sans l'appliquer)
python manage.py sqlmigrate articles 0001

# Vérifier la cohérence des migrations
python manage.py migrate --check  # Exit code != 0 si migrations en attente
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant `python manage.py makemigrations` qui détecte les changements, puis `python manage.py migrate` qui les applique avec la sortie ligne par ligne "Applying articles.0001_initial... OK"
> **Expliquer :** Chaque migration a un numéro séquentiel. Django suit les migrations appliquées dans la table `django_migrations`. Montrer `python manage.py showmigrations` pour voir l'état ([ ] = non appliqué, [X] = appliqué).

---

## Anatomie d'un fichier de migration

```python
# articles/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True  # Marqueur : c'est la migration initiale

    dependencies = [
        # Migrations dont celle-ci dépend
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Liste des opérations SQL à effectuer
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('titre', models.CharField(max_length=200)),
                ('contenu', models.TextField()),
                ('statut', models.CharField(
                    choices=[('brouillon', 'Brouillon'), ('publie', 'Publié')],
                    default='brouillon',
                    max_length=20,
                )),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='articles',
                    to='auth.user',
                )),
            ],
        ),
    ]
```

---

## Cas courants de migration

### Ajouter un champ

```python
# models.py — ajouter le champ
class Article(models.Model):
    # ...
    nb_vues = models.PositiveIntegerField(default=0)  # Nouveau champ
```

```bash
python manage.py makemigrations articles --name="ajouter_nb_vues"
```

```python
# Migration générée : 0002_ajouter_nb_vues.py
class Migration(migrations.Migration):
    dependencies = [('articles', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='article',
            name='nb_vues',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
```

### Modifier un champ

```python
# models.py — changer max_length
titre = models.CharField(max_length=300)  # Était 200
```

```python
# Migration générée
migrations.AlterField(
    model_name='article',
    name='titre',
    field=models.CharField(max_length=300),
)
```

### Renommer un champ

```bash
python manage.py makemigrations articles --name="renommer_titre"
```

Django vous demandera : "Did you rename article.titre to article.heading? [y/N]"

```python
# Migration générée
migrations.RenameField(
    model_name='article',
    old_name='titre',
    new_name='heading',
)
```

### Supprimer un champ

```python
# Migration générée
migrations.RemoveField(
    model_name='article',
    name='champ_obsolete',
)
```

---

## Migrations de données (Data Migrations)

Les migrations de données modifient le contenu de la BDD, pas seulement le schéma.

### Créer une migration vide

```bash
python manage.py makemigrations --empty articles --name="populate_slugs"
```

```python
# articles/migrations/0005_populate_slugs.py
from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    """Remplit le champ slug pour les articles existants."""
    # IMPORTANT : utiliser apps.get_model, pas l'import direct
    # (le modèle doit être dans l'état de cette migration)
    Article = apps.get_model('articles', 'Article')
    for article in Article.objects.filter(slug=''):
        article.slug = slugify(article.titre)
        article.save(update_fields=['slug'])

def reverse_populate_slugs(apps, schema_editor):
    """Fonction inverse pour le rollback."""
    Article = apps.get_model('articles', 'Article')
    Article.objects.update(slug='')


class Migration(migrations.Migration):
    dependencies = [
        ('articles', '0004_article_slug'),
    ]

    operations = [
        migrations.RunPython(
            populate_slugs,
            reverse_populate_slugs,  # Fonction de rollback
        ),
    ]
```

### Migration de données avec SQL brut

```python
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            # SQL d'application
            sql="UPDATE articles_article SET statut='publie' WHERE publie=TRUE;",
            # SQL de rollback
            reverse_sql="UPDATE articles_article SET publie=TRUE WHERE statut='publie';",
        ),
    ]
```

---

## Squashmigrations — Consolider les migrations

Quand vous avez trop de fichiers de migration, vous pouvez les consolider :

```bash
# Squasher les migrations 0001 à 0010 en une seule
python manage.py squashmigrations articles 0001 0010

# Résultat : un fichier 0001_squashed_0010_....py
```

Après vérification, vous pouvez supprimer les anciennes migrations et renommer le fichier squashé.

---

## Dépendances entre migrations

```python
# articles/migrations/0003_commentaire.py
class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_ajouter_nb_vues'),   # Même app
        ('auth', '0012_alter_user_first_name'),  # App externe
    ]

    operations = [
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                # ...
                ('article', models.ForeignKey(
                    to='articles.article',
                    on_delete=models.CASCADE,
                )),
                ('auteur', models.ForeignKey(
                    to='auth.user',
                    on_delete=models.CASCADE,
                )),
            ],
        ),
    ]
```

---

## Gestion des conflits

Si deux développeurs créent des migrations en parallèle sur la même app :

```bash
# Détecter les conflits
python manage.py migrate --check

# Résoudre les conflits
python manage.py makemigrations --merge articles
```

Cela crée une migration de fusion qui déclare dépendre des deux migrations conflictuelles.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec `python manage.py showmigrations` montrant l'état des migrations de plusieurs apps, avec certaines [X] (appliquées) et d'autres [ ] (en attente)
> **Expliquer :** La table `django_migrations` en base de données est la source de vérité. Ouvrir `python manage.py dbshell` et faire `SELECT * FROM django_migrations;` pour montrer que Django stocke le nom de chaque migration appliquée.

---

## Migrations et environnements multiples

### Bonnes pratiques d'équipe

```bash
# 1. Toujours committer les migrations dans git
git add articles/migrations/
git commit -m "feat(articles): ajouter champ nb_vues"

# 2. Appliquer les migrations au démarrage en CI/CD
python manage.py migrate --check || python manage.py migrate

# 3. Ne JAMAIS modifier une migration déjà appliquée en production
# Créer une nouvelle migration à la place

# 4. Utiliser des noms explicites
python manage.py makemigrations articles --name="add_cover_image_to_article"
```

### Configuration multi-BDD

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monapp_db',
        'USER': 'postgres',
        'PASSWORD': 'motdepasse',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'analytics_db',
        # ...
    },
}

# Database router
class AnalyticsRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'analytics':
            return 'analytics'
        return None

DATABASE_ROUTERS = ['config.routers.AnalyticsRouter']
```

```bash
# Migrer une BDD spécifique
python manage.py migrate --database=analytics
```

---

## Cas spéciaux

### Champ avec contrainte NOT NULL sur table existante

```python
# Problème : ajouter un champ NOT NULL sur une table existante avec des données
# Solution 1 : valeur par défaut
nb_likes = models.PositiveIntegerField(default=0)

# Solution 2 : nullable d'abord, data migration, puis NOT NULL
# Étape 1 :
nb_likes = models.PositiveIntegerField(null=True)
# Migration + python manage.py migrate

# Étape 2 : data migration pour remplir les NULL
# Migration + python manage.py migrate

# Étape 3 :
nb_likes = models.PositiveIntegerField(null=False, default=0)
# Migration + python manage.py migrate
```

### Renommer un modèle

```python
# Migration générée
migrations.RenameModel(
    old_name='Billet',
    new_name='Article',
)
```

**Attention :** Toutes les ForeignKey qui pointaient vers `Billet` se mettent à jour automatiquement, mais les imports dans le code Python doivent être mis à jour manuellement.

---

## Résumé

| Commande | Usage |
|---------|-------|
| `makemigrations` | Détecter les changements et créer les fichiers |
| `migrate` | Appliquer les migrations en BDD |
| `showmigrations` | Voir l'état des migrations |
| `sqlmigrate` | Voir le SQL sans l'exécuter |
| `migrate app 000X` | Revenir à une migration précise |
| `squashmigrations` | Consolider des migrations |
| `--empty` | Créer une migration vide pour data migration |

- Les fichiers de migration sont du code — ils doivent être **committés dans git**
- Les **data migrations** utilisent `RunPython` avec `apps.get_model()`
- Ne jamais modifier une migration déjà appliquée en production
- En cas de conflit, utiliser `makemigrations --merge`

## Prochaine étape

Passez au module [DRF — Introduction](../DRF/01-introduction.md) pour apprendre à créer une API REST avec Django.
