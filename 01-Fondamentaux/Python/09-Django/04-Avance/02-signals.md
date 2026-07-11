# Avancé — 02 : Signaux Django

## Qu'est-ce qu'un signal ?

Les signaux Django permettent à des composants découplés d'être notifiés quand certains événements se produisent. C'est le patron **Observer**.

```
Modèle.save() → Django envoie le signal post_save → Toutes les fonctions connectées sont appelées
```

---

## Signaux intégrés

### Signaux des modèles

```python
from django.db.models.signals import (
    pre_save,           # Avant Model.save()
    post_save,          # Après Model.save()
    pre_delete,         # Avant Model.delete()
    post_delete,        # Après Model.delete()
    m2m_changed,        # Quand une relation M2M change
    pre_migrate,        # Avant les migrations
    post_migrate,       # Après les migrations
)
```

### Signaux de requêtes

```python
from django.core.signals import (
    request_started,    # Début de traitement d'une requête
    request_finished,   # Fin de traitement
    got_request_exception,  # Exception non gérée
)
```

---

## Utiliser les signaux

### Avec le décorateur `@receiver`

```python
# articles/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Article, ProfilUtilisateur

User = get_user_model()

@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance, created, **kwargs):
    """Crée automatiquement un profil à la création d'un utilisateur."""
    if created:
        ProfilUtilisateur.objects.create(user=instance)


@receiver(post_save, sender=User)
def sauvegarder_profil_utilisateur(sender, instance, created, **kwargs):
    """Sauvegarde le profil quand l'utilisateur est sauvegardé."""
    if not created:  # Mise à jour (pas création)
        try:
            instance.profilutilisateur.save()
        except ProfilUtilisateur.DoesNotExist:
            ProfilUtilisateur.objects.create(user=instance)


@receiver(post_save, sender=Article)
def notifier_publication(sender, instance, created, **kwargs):
    """Envoie une notification quand un article est publié."""
    if not created and instance.statut == 'publie':
        # Vérifier si le statut vient de changer
        try:
            ancien = Article.objects.get(pk=instance.pk)
        except Article.DoesNotExist:
            return

        # Envoyer email de notification
        from django.core.mail import send_mail
        send_mail(
            subject=f"Nouvel article publié : {instance.titre}",
            message=f"L'article '{instance.titre}' a été publié.",
            from_email='noreply@monblog.com',
            recipient_list=['equipe@monblog.com'],
            fail_silently=True,
        )
```

---

### Enregistrer les signaux dans `apps.py`

```python
# articles/apps.py
from django.apps import AppConfig

class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'
    verbose_name = 'Articles'

    def ready(self):
        """Appelé quand Django a terminé de charger toutes les apps."""
        import articles.signals  # noqa: F401 — Enregistre les signaux
```

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'articles.apps.ArticlesConfig',  # Forme complète nécessaire pour ready()
]
```

---

## Signaux post_save — paramètres

```python
@receiver(post_save, sender=Article)
def signal_article(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    sender        : La classe du modèle (Article)
    instance      : L'objet sauvegardé
    created       : True si nouvel objet, False si mise à jour
    raw           : True si sauvegardé via loaddata (fixtures)
    using         : Alias de la base de données ('default')
    update_fields : Set des champs mis à jour (si save(update_fields=[...]))
    """
    if raw:
        return  # Ne pas traiter les fixtures

    if created:
        print(f"Nouvel article créé : {instance.titre}")
    else:
        if update_fields and 'statut' in update_fields:
            print(f"Statut de {instance.titre} changé en {instance.statut}")
```

---

## Signaux m2m_changed

```python
@receiver(m2m_changed, sender=Article.tags.through)
def tags_modifies(sender, instance, action, pk_set, **kwargs):
    """
    action   : 'pre_add', 'post_add', 'pre_remove', 'post_remove', 'pre_clear', 'post_clear'
    pk_set   : Set des PKs ajoutés/retirés (None pour clear)
    instance : L'objet Article
    """
    if action == 'post_add':
        print(f"Tags ajoutés à '{instance.titre}' : {pk_set}")
    elif action == 'post_remove':
        print(f"Tags retirés de '{instance.titre}' : {pk_set}")
    elif action == 'post_clear':
        print(f"Tous les tags retirés de '{instance.titre}'")
```

---

## Signaux pre_delete

```python
@receiver(pre_delete, sender=Article)
def nettoyer_avant_suppression(sender, instance, **kwargs):
    """Nettoyage avant suppression d'un article."""
    # Supprimer les fichiers media associés
    if instance.image_couverture:
        import os
        if os.path.isfile(instance.image_couverture.path):
            os.remove(instance.image_couverture.path)

    # Archiver l'article au lieu de supprimer (exemple)
    # ArchivedArticle.objects.create(
    #     original_id=instance.pk,
    #     titre=instance.titre,
    #     contenu=instance.contenu,
    #     supprime_le=timezone.now(),
    # )

    print(f"Article '{instance.titre}' sur le point d'être supprimé")
```

---

## Créer des signaux personnalisés

```python
# articles/signals.py
from django.dispatch import Signal

# Définir un signal personnalisé
article_publie     = Signal()  # Peut accepter des arguments
article_archive    = Signal()
commentaire_signale = Signal()


# Émettre le signal depuis un modèle ou une vue
def publier_article(article, publie_par):
    article.statut = 'publie'
    article.save(update_fields=['statut'])
    # Émettre le signal
    article_publie.send(
        sender=article.__class__,
        article=article,
        publie_par=publie_par,
    )


# Connecter un récepteur
@receiver(article_publie)
def apres_publication(sender, article, publie_par, **kwargs):
    print(f"{publie_par.username} a publié '{article.titre}'")
    # Envoyer notification, mettre en cache, etc.


@receiver(article_publie)
def indexer_article(sender, article, **kwargs):
    """Indexer l'article dans le moteur de recherche."""
    # search_engine.index(article)
    pass
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Shell Django montrant la création d'un utilisateur via `User.objects.create_user(...)` et la table `articles_profilutilisateur` montrant que le profil a été créé automatiquement grâce au signal `post_save`
> **Expliquer :** Les signaux sont parfaits pour déclencher des effets de bord sans coupler les composants. Mais attention : les signaux ne sont pas exécutés lors des `bulk_create`, `bulk_update`, ou `QuerySet.update()`. Pour ces cas, coder explicitement la logique.

---

## Connecter des signaux manuellement (sans décorateur)

```python
# Connexion manuelle — moins recommandée mais parfois nécessaire
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

def handler_creation_user(sender, instance, created, **kwargs):
    if created:
        print(f"User créé : {instance.username}")

User = get_user_model()
post_save.connect(handler_creation_user, sender=User)

# Déconnecter
post_save.disconnect(handler_creation_user, sender=User)
```

---

## Bonnes pratiques

### Ce qu'on fait avec les signaux

- Créer des objets liés automatiquement (profil utilisateur, etc.)
- Envoyer des emails/notifications asynchrones
- Invalider le cache
- Indexer dans un moteur de recherche
- Journaliser les changements

### Ce qu'on évite

```python
# MAUVAIS : logique métier complexe dans un signal
@receiver(post_save, sender=Commande)
def traiter_paiement(sender, instance, created, **kwargs):
    if created:
        # Appel API paiement, envoi email, mise à jour stock...
        # Difficile à tester, à debugger, et à transactionner
        pass

# MIEUX : méthode de service appelée explicitement
class CommandeService:
    @staticmethod
    def creer_commande(user, produits):
        with transaction.atomic():
            commande = Commande.objects.create(user=user)
            # traiter paiement...
            # envoyer email...
        return commande
```

---

## Désactiver temporairement les signaux

```python
from unittest.mock import patch

# Dans les tests — désactiver le signal pour tester la vue seule
with patch('articles.signals.notifier_publication'):
    Article.objects.create(titre='Test', auteur=user, statut='publie')
    # Le signal ne sera pas déclenché

# Via disconnect
post_save.disconnect(notifier_publication, sender=Article)
Article.objects.create(...)
post_save.connect(notifier_publication, sender=Article)
```

---

## Résumé

- Les signaux implémentent le patron Observer
- `@receiver(signal, sender=Modele)` pour connecter un récepteur
- Toujours enregistrer les signaux dans `AppConfig.ready()`
- `post_save(created=True)` pour les créations, `created=False` pour les mises à jour
- `m2m_changed` pour les relations Many-to-Many
- Les signaux ne se déclenchent PAS avec `bulk_create`, `bulk_update`, `QuerySet.update()`

## Prochaine étape

Passez au module [03 — Cache](03-cache.md).
