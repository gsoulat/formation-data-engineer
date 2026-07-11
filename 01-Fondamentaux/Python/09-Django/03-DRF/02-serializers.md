# DRF — 02 : Sérialiseurs

## Rôle des sérialiseurs

Un sérialiseur DRF a deux rôles :

1. **Sérialisation** : Convertir un objet Python/Django en JSON (pour la réponse API)
2. **Désérialisation** : Valider les données JSON entrantes et les convertir en objet Python (pour la requête API)

```python
# Sérialisation : objet → dict → JSON
article = Article.objects.first()
serializer = ArticleSerializer(article)
serializer.data  # OrderedDict prêt pour la réponse JSON

# Désérialisation : JSON → validation → objet
serializer = ArticleSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
article = serializer.save()  # Crée ou met à jour l'objet
```

---

## Serializer de base

```python
# articles/serializers.py
from rest_framework import serializers

class ArticleSimpleSerializer(serializers.Serializer):
    """Sérialiseur manuel — rarement utilisé directement."""
    id      = serializers.IntegerField(read_only=True)
    titre   = serializers.CharField(max_length=200)
    contenu = serializers.CharField()
    statut  = serializers.ChoiceField(choices=['brouillon', 'publie', 'archive'])
    cree_le = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.titre   = validated_data.get('titre', instance.titre)
        instance.contenu = validated_data.get('contenu', instance.contenu)
        instance.save()
        return instance
```

---

## ModelSerializer

Le `ModelSerializer` génère automatiquement les champs à partir du modèle :

```python
from rest_framework import serializers
from .models import Article, Categorie, Tag

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'          # Tous les champs — déconseillé en prod

        # Ou spécifier explicitement
        fields = [
            'id', 'titre', 'slug', 'contenu', 'statut',
            'mis_en_avant', 'nb_vues', 'auteur', 'categorie',
            'cree_le', 'modifie_le',
        ]

        # Ou exclure certains champs
        exclude = ['image_couverture']

        # Champs en lecture seule
        read_only_fields = ['id', 'nb_vues', 'cree_le', 'modifie_le', 'slug']

        # Options supplémentaires par champ
        extra_kwargs = {
            'contenu': {'min_length': 50, 'help_text': 'Minimum 50 caractères'},
            'auteur':  {'read_only': True},
        }
```

---

## Champs personnalisés

```python
class ArticleSerializer(serializers.ModelSerializer):
    # Champ calculé (lecture seule)
    nb_commentaires = serializers.SerializerMethodField()
    auteur_nom      = serializers.SerializerMethodField()
    url             = serializers.SerializerMethodField()

    # Champ source — utilise un attribut différent
    nom_categorie   = serializers.CharField(source='categorie.nom', read_only=True)
    auteur_email    = serializers.EmailField(source='auteur.email', read_only=True)

    # Champ avec valeur par défaut
    statut_affiche  = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'contenu', 'statut', 'statut_affiche',
            'auteur_nom', 'auteur_email', 'nom_categorie',
            'nb_commentaires', 'url', 'cree_le',
        ]

    def get_nb_commentaires(self, obj):
        return obj.commentaires.filter(approuve=True).count()

    def get_auteur_nom(self, obj):
        return obj.auteur.get_full_name() or obj.auteur.username

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.get_absolute_url())
        return obj.get_absolute_url()
```

---

## Validation

### Validation de champ

```python
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'statut']

    def validate_titre(self, value):
        """Validation d'un champ spécifique — méthode validate_<fieldname>."""
        if len(value) < 5:
            raise serializers.ValidationError("Le titre doit faire au moins 5 caractères.")
        if value.lower() == 'test':
            raise serializers.ValidationError("Le titre 'test' n'est pas autorisé.")
        # Vérifier l'unicité par auteur
        auteur = self.context['request'].user
        qs = Article.objects.filter(titre__iexact=value, auteur=auteur)
        if self.instance:  # Mise à jour : exclure l'objet actuel
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Vous avez déjà un article avec ce titre.")
        return value

    def validate_contenu(self, value):
        if len(value.split()) < 10:
            raise serializers.ValidationError("Le contenu doit contenir au moins 10 mots.")
        return value
```

### Validation croisée (plusieurs champs)

```python
class ArticleSerializer(serializers.ModelSerializer):
    publie_le = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'statut', 'publie_le']

    def validate(self, data):
        """Validation globale — accès à tous les champs."""
        statut    = data.get('statut', getattr(self.instance, 'statut', 'brouillon'))
        publie_le = data.get('publie_le')

        if statut == 'publie' and not publie_le:
            raise serializers.ValidationError({
                'publie_le': 'La date de publication est obligatoire pour un article publié.'
            })

        if statut == 'archive' and data.get('mis_en_avant'):
            raise serializers.ValidationError(
                'Un article archivé ne peut pas être mis en avant.'
            )

        return data
```

### Validators

```python
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class ArticleSerializer(serializers.ModelSerializer):
    titre = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Article.objects.all(),
                message="Un article avec ce titre existe déjà.",
                lookup='iexact',  # Insensible à la casse
            )
        ]
    )

    class Meta:
        model = Article
        fields = ['titre', 'slug', 'contenu', 'auteur']
        validators = [
            UniqueTogetherValidator(
                queryset=Article.objects.all(),
                fields=['titre', 'auteur'],
                message="Vous avez déjà un article avec ce titre.",
            )
        ]
```

---

## Sérialiseurs imbriqués (nested)

### Lecture seule

```python
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nom', 'slug']

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug']

class ArticleDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur avec relations imbriquées — pour la lecture."""
    auteur    = serializers.StringRelatedField()  # Affiche __str__()
    categorie = CategorieSerializer(read_only=True)
    tags      = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'slug', 'contenu', 'statut',
            'auteur', 'categorie', 'tags', 'cree_le',
        ]
```

Réponse JSON :
```json
{
    "id": 1,
    "titre": "Introduction à Django",
    "categorie": {"id": 2, "nom": "Python", "slug": "python"},
    "tags": [
        {"id": 1, "nom": "django", "slug": "django"},
        {"id": 3, "nom": "python", "slug": "python"}
    ]
}
```

### Écriture avec relations imbriquées

```python
class ArticleCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création/modification avec IDs."""
    # Écriture : envoyer des IDs
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(),
        source='categorie',
        write_only=True,
        required=False,
        allow_null=True,
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False,
    )

    # Lecture : données complètes
    categorie = CategorieSerializer(read_only=True)
    tags      = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'contenu', 'statut',
            'categorie_id', 'tag_ids',  # Écriture
            'categorie', 'tags',         # Lecture
            'cree_le',
        ]
        read_only_fields = ['id', 'cree_le']
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman envoyant un POST avec un body JSON invalide (titre trop court) et recevant la réponse 400 avec les erreurs de validation JSON : `{"titre": ["Le titre doit faire au moins 5 caractères."]}`
> **Expliquer :** Les erreurs de validation DRF sont structurées par champ — très utile pour les frontends qui veulent afficher les erreurs sous chaque champ de formulaire. Montrer aussi qu'une erreur dans `validate()` apparaît sous la clé `non_field_errors`.

---

## Sérialiseurs multiples selon le contexte

```python
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()

    def get_serializer_class(self):
        """Utiliser un sérialiseur différent selon l'action."""
        if self.action == 'list':
            return ArticleListSerializer      # Léger pour la liste
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateSerializer    # Pour l'écriture
        return ArticleDetailSerializer        # Complet pour le détail

class ArticleListSerializer(serializers.ModelSerializer):
    """Léger — pour les listes."""
    class Meta:
        model = Article
        fields = ['id', 'titre', 'slug', 'statut', 'cree_le']

class ArticleDetailSerializer(serializers.ModelSerializer):
    """Complet — pour le détail."""
    categorie = CategorieSerializer(read_only=True)
    tags      = TagSerializer(many=True, read_only=True)
    nb_commentaires = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_nb_commentaires(self, obj):
        return obj.commentaires.count()
```

---

## `save()` — create et update

```python
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', 'statut', 'categorie']

    def create(self, validated_data):
        """Appelé par save() lors d'une création."""
        # validated_data ne contient PAS l'auteur (non dans les fields)
        # L'auteur est passé via perform_create dans le ViewSet
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        """Appelé par save() lors d'une mise à jour."""
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
```

Dans le ViewSet :
```python
def perform_create(self, serializer):
    serializer.save(auteur=self.request.user)  # Données supplémentaires passées à create()
```

---

## Champs de relation

```python
class ArticleSerializer(serializers.ModelSerializer):
    # 1. PrimaryKeyRelatedField — retourne les IDs (défaut)
    categorie = serializers.PrimaryKeyRelatedField(queryset=Categorie.objects.all())
    # Entrée/Sortie : {"categorie": 3}

    # 2. StringRelatedField — retourne __str__()
    categorie = serializers.StringRelatedField()
    # Sortie : {"categorie": "Python"}  (read_only)

    # 3. SlugRelatedField — retourne une valeur spécifique
    categorie = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categorie.objects.all(),
    )
    # Entrée/Sortie : {"categorie": "python"}

    # 4. HyperlinkedRelatedField — retourne une URL
    categorie = serializers.HyperlinkedRelatedField(
        view_name='categorie-detail',
        read_only=True,
    )
    # Sortie : {"categorie": "http://api.example.com/categories/3/"}
```

---

## SerializerMethodField avancé

```python
class ArticleSerializer(serializers.ModelSerializer):
    permissions_utilisateur = serializers.SerializerMethodField()
    tags_noms               = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'titre', 'permissions_utilisateur', 'tags_noms']

    def get_permissions_utilisateur(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return {'can_edit': False, 'can_delete': False}
        return {
            'can_edit':   obj.auteur == request.user or request.user.is_staff,
            'can_delete': obj.auteur == request.user or request.user.is_superuser,
        }

    def get_tags_noms(self, obj):
        return list(obj.tags.values_list('nom', flat=True))
```

---

## Résumé

| Champ | Usage |
|-------|-------|
| `CharField`, `IntegerField`, etc. | Champs simples |
| `SerializerMethodField` | Valeur calculée (lecture seule) |
| `PrimaryKeyRelatedField` | Relation par ID |
| `StringRelatedField` | Relation par `__str__()` |
| `SlugRelatedField` | Relation par un champ |
| Sérialiseur imbriqué | Objet JSON complet |

- `validate_<field>()` pour valider un champ
- `validate()` pour la validation croisée
- `create()` et `update()` pour personnaliser la sauvegarde
- Utiliser des sérialiseurs différents pour list/detail/create

## Prochaine étape

Passez au module [03 — ViewSets](03-viewsets.md) pour maîtriser les vues API DRF.
