# DRF — 04 : Authentification

## Les mécanismes d'authentification

L'authentification répond à la question : **"Qui êtes-vous ?"**
La permission répond à la question : **"Avez-vous le droit de faire cela ?"**

DRF supporte plusieurs mécanismes :

| Mécanisme | Usage |
|-----------|-------|
| `SessionAuthentication` | Applications web Django classiques |
| `BasicAuthentication` | Tests / scripts simples (jamais en prod) |
| `TokenAuthentication` | API mobile et SPA (simple) |
| **JWT** via simplejwt | API moderne (recommandé) |
| OAuth2 / OpenID | Connexion via Google, GitHub, etc. |

---

## TokenAuthentication

### Installation

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework.authtoken',  # Ajouter
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

```bash
python manage.py migrate  # Crée la table authtoken_token
```

### Endpoints de token

```python
# config/urls.py
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/token/', obtain_auth_token),  # POST → {"token": "abc123..."}
]
```

### Utilisation

```bash
# Obtenir un token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "motdepasse"}'
# Réponse : {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}

# Utiliser le token dans les requêtes
curl http://localhost:8000/api/articles/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Gestion des tokens

```python
# Créer un token pour un utilisateur
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='alice')
token, cree = Token.objects.get_or_create(user=user)
print(token.key)

# Signal : créer automatiquement un token à la création d'un user
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def creer_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
```

---

## JWT avec djangorestframework-simplejwt (recommandé)

JWT (JSON Web Token) est plus sécurisé que les tokens simples car :
- Pas de BDD nécessaire pour valider le token
- Expiration configurable
- Refresh token pour renouveler sans re-authentifier

### Installation

```bash
pip install djangorestframework-simplejwt
```

```python
# config/settings.py
from datetime import timedelta

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    # Durée de vie du token d'accès
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    # Durée de vie du token de rafraîchissement
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Rotation des refresh tokens
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    # Algorithme de signature
    'ALGORITHM': 'HS256',
    # Header HTTP à utiliser
    'AUTH_HEADER_TYPES': ('Bearer',),
    # Champ utilisé comme identifiant dans le token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

### URLs JWT

```python
# config/urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/token/',         TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/token/verify/',  TokenVerifyView.as_view(),      name='token_verify'),
    path('api/',               include('articles.urls')),
]
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman montrant la séquence complète : POST /api/token/ pour obtenir access + refresh tokens, puis GET /api/articles/ avec le Bearer token dans le header Authorization, puis GET /api/articles/ sans token recevant un 401
> **Expliquer :** Décoder le JWT sur jwt.io pour montrer les claims (user_id, exp, iat). Expliquer la différence entre access token (courte durée, 15min-1h) et refresh token (longue durée, 7-30 jours). Le frontend stocke le refresh token en httpOnly cookie pour la sécurité.

---

### Flux JWT

```
1. Login
   POST /api/token/
   {"username": "alice", "password": "motdepasse"}
   → {"access": "eyJ...", "refresh": "eyJ..."}

2. Requête API
   GET /api/articles/
   Authorization: Bearer eyJ...
   → 200 OK + données

3. Access Token expiré
   GET /api/articles/
   Authorization: Bearer eyJ... (expiré)
   → 401 {"detail": "Given token not valid for any token type"}

4. Rafraîchissement
   POST /api/token/refresh/
   {"refresh": "eyJ..."}
   → {"access": "eyJ...nouveau..."}

5. Déconnexion (blacklist)
   POST /api/token/blacklist/
   {"refresh": "eyJ..."}
   → 205 Reset Content
```

### Personnaliser les claims du token

```python
# articles/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MonTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ajouter des claims personnalisés
        token['username']   = user.username
        token['email']      = user.email
        token['is_staff']   = user.is_staff
        token['first_name'] = user.first_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Ajouter des données dans la réponse JSON
        data['user'] = {
            'id':         self.user.id,
            'username':   self.user.username,
            'email':      self.user.email,
            'is_staff':   self.user.is_staff,
        }
        return data


class MonTokenObtainPairView(TokenObtainPairView):
    serializer_class = MonTokenObtainPairSerializer
```

```python
# config/urls.py
from .serializers import MonTokenObtainPairView

urlpatterns = [
    path('api/token/', MonTokenObtainPairView.as_view()),
    # ...
]
```

---

## Inscription et profil utilisateur

### Vue d'inscription

```python
# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class InscriptionSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hache le mot de passe
        user.save()
        return user


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']


class ChangerMotDePasseSerializer(serializers.Serializer):
    ancien_mot_de_passe  = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, min_length=8)
    confirmation         = serializers.CharField(write_only=True)

    def validate_ancien_mot_de_passe(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value

    def validate(self, data):
        if data['nouveau_mot_de_passe'] != data['confirmation']:
            raise serializers.ValidationError({'confirmation': "Les mots de passe ne correspondent pas."})
        return data
```

```python
# users/views.py
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import InscriptionSerializer, ProfilSerializer, ChangerMotDePasseSerializer

class InscriptionView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class   = InscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Générer un token JWT pour l'utilisateur créé
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    ProfilSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class MonProfilView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ProfilSerializer

    def get_object(self):
        return self.request.user


class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['nouveau_mot_de_passe'])
        request.user.save()
        return Response({'message': 'Mot de passe modifié avec succès.'})
```

---

## Blacklist des tokens (déconnexion)

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt.token_blacklist',
]
```

```bash
python manage.py migrate
```

```python
# users/views.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Token de rafraîchissement manquant.'}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnecté avec succès.'})
        except TokenError:
            return Response({'error': 'Token invalide ou déjà blacklisté.'}, status=400)
```

---

## Authentification mixte

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Pour la browsable API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## URLs utilisateurs complètes

```python
# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    # Authentification JWT
    path('auth/token/',         TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),     name='token_refresh'),
    path('auth/token/verify/',  TokenVerifyView.as_view(),      name='token_verify'),
    # Inscription / profil
    path('auth/inscription/',   views.InscriptionView.as_view(),       name='inscription'),
    path('auth/deconnexion/',   views.DeconnexionView.as_view(),       name='deconnexion'),
    path('auth/profil/',        views.MonProfilView.as_view(),         name='profil'),
    path('auth/mot-de-passe/',  views.ChangerMotDePasseView.as_view(), name='changer_mdp'),
]
```

---

## Résumé

| Mécanisme | Avantages | Inconvénients |
|-----------|-----------|---------------|
| Session | Intégré Django, révocable | Nécessite cookies, pas pour SPA |
| Token DRF | Simple, révocable | 1 token/user, BDD nécessaire |
| JWT | Stateless, rapide, claims | Révocation complexe (blacklist) |

- JWT avec `simplejwt` est la solution recommandée pour les API modernes
- Access token : courte durée (15-60 min)
- Refresh token : longue durée (7-30 jours), stocké en httpOnly cookie
- La blacklist permet la révocation (déconnexion)
- Personnaliser `TokenObtainPairSerializer` pour ajouter des claims au token

## Prochaine étape

Passez au module [05 — Permissions](05-permissions.md) pour contrôler les droits d'accès.
