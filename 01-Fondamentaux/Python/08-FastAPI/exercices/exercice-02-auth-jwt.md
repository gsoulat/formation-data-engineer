# Exercice 02 — Authentification JWT

## Contexte

Vous reprenez l'API produits de l'exercice 01. Le CTO vous demande maintenant de sécuriser l'API : les opérations de modification (création, modification, suppression) doivent être réservées aux utilisateurs authentifiés. Certaines opérations (suppression définitive, gestion des utilisateurs) doivent être réservées aux administrateurs.

**Durée estimée** : 2h à 2h30

---

## Objectifs

À la fin de cet exercice, vous aurez :
- Créé un système d'inscription / connexion
- Implémenté les tokens JWT (access + refresh)
- Sécurisé les routes selon les rôles (user, admin)
- Testé le système d'authentification

---

## Spécifications fonctionnelles

### Règles d'accès

| Opération | Public | Utilisateur | Admin |
|---|---|---|---|
| Lister les produits | ✓ | ✓ | ✓ |
| Voir un produit | ✓ | ✓ | ✓ |
| Créer un produit | ✗ | ✓ | ✓ |
| Modifier un produit | ✗ | ✓ (seulement les siens) | ✓ |
| Supprimer un produit | ✗ | ✗ | ✓ |
| Voir son profil | ✗ | ✓ | ✓ |
| Lister les utilisateurs | ✗ | ✗ | ✓ |
| Désactiver un utilisateur | ✗ | ✗ | ✓ |

### Endpoints à implémenter

```
POST   /api/v1/auth/register     → Inscription
POST   /api/v1/auth/login        → Connexion → retourne JWT
POST   /api/v1/auth/refresh      → Renouveler le token
POST   /api/v1/auth/logout       → Déconnexion (invalidation côté client)
GET    /api/v1/users/me          → Profil de l'utilisateur connecté
PATCH  /api/v1/users/me          → Modifier son profil
GET    /api/v1/users/            → Lister tous les users (admin)
GET    /api/v1/users/{id}        → Voir un user (admin)
PATCH  /api/v1/users/{id}/toggle-active  → Activer/désactiver (admin)
```

### Modèle Utilisateur

| Champ | Type | Contraintes |
|---|---|---|
| `id` | int | Auto, PK |
| `username` | string | Unique, 3-50 chars, alphanumérique |
| `email` | EmailStr | Unique |
| `hashed_password` | string | Jamais renvoyé en réponse |
| `full_name` | string | Optionnel |
| `is_active` | bool | Défaut True |
| `is_admin` | bool | Défaut False |
| `created_at` | datetime | Auto |

---

## Instructions

### Étape 1 — Dépendances (5 min)

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

Ajoutez ces lignes à `requirements.txt`.

### Étape 2 — Modèle et schémas (20 min)

**Modèle SQLAlchemy** (`app/models/user.py`) :

Créez le modèle `User` avec les champs spécifiés.

Ajoutez la relation avec les produits si vous avez un champ `created_by` :
```python
products = relationship("Product", back_populates="creator")
```

**Schémas Pydantic** (`app/schemas/user.py`) :

Créez les schémas suivants :

```python
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        # Votre validation ici
        ...

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        # Votre validation ici : min 8 chars, 1 majuscule, 1 chiffre
        ...

class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_active: bool
    is_admin: bool
    created_at: datetime

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    current_password: str | None = None
    new_password: str | None = None
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'erreur 422 retournée par FastAPI quand le mot de passe ne respecte pas les règles
> **Expliquer :** Faire un POST /auth/register avec le mot de passe "abc" (trop court). Montrer la réponse 422 avec le message d'erreur détaillé de Pydantic. Puis faire un POST avec "Password1" (valide) et montrer le 201. Insister sur le fait que la validation est faite automatiquement par Pydantic avant d'entrer dans la fonction handler.

---

### Étape 3 — Module de sécurité (20 min)

Créez `app/core/security.py` avec les fonctions suivantes :

```python
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext

# Compléter ces fonctions :

def hash_password(password: str) -> str:
    """Hasher le mot de passe avec bcrypt."""
    ...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier le mot de passe."""
    ...

def create_access_token(
    subject: str | int,
    extra_data: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Créer un JWT d'accès valide 30 minutes."""
    ...

def create_refresh_token(subject: str | int) -> str:
    """Créer un JWT de refresh valide 7 jours."""
    ...

def decode_token(token: str) -> dict:
    """Décoder et valider un token JWT. Raise 401 si invalide."""
    ...
```

**Points de vérification :**
- Le payload doit contenir `sub`, `exp`, `iat`, `type`
- `type` doit valoir `"access"` ou `"refresh"`
- Lever `HTTPException(401)` si le token est expiré ou invalide

### Étape 4 — Dépendances d'authentification (20 min)

Créez `app/core/deps.py` :

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Extraire l'utilisateur depuis le token JWT."""
    # 1. Décoder le token
    # 2. Extraire user_id depuis payload["sub"]
    # 3. Requêter la DB
    # 4. Vérifier que l'utilisateur existe
    # 5. Retourner l'utilisateur
    ...

def get_current_active_user(...) -> User:
    """Vérifier que le compte est actif."""
    ...

def get_current_admin_user(...) -> User:
    """Vérifier que l'utilisateur est admin."""
    ...

# Types alias
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
```

### Étape 5 — Router d'authentification (30 min)

Créez `app/routers/auth.py` avec les endpoints `register` et `login`.

**Endpoint `/auth/register` :**
- Vérifier que username et email ne sont pas déjà pris (retourner 409 si oui)
- Hasher le mot de passe
- Créer l'utilisateur en base
- Retourner 201 avec un message de succès et l'ID de l'utilisateur créé

**Endpoint `/auth/login` :**
- Utiliser `OAuth2PasswordRequestForm` pour recevoir les données
- Accepter username OU email dans le champ `username`
- Vérifier le mot de passe avec `verify_password`
- Vérifier que le compte est actif (403 si inactif)
- Retourner les tokens access et refresh

**Endpoint `/auth/refresh` :**
- Recevoir le refresh token (dans le body, pas le header)
- Vérifier que le type est bien `"refresh"`
- Générer de nouveaux tokens
- Retourner les nouveaux tokens

**Schéma de réponse attendu pour login/refresh :**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Étape 6 — Sécuriser les routes produits (20 min)

Modifiez `app/routers/products.py` pour appliquer les restrictions :

```python
from app.core.deps import CurrentUser, AdminUser

# Route PUBLIQUE (pas de Depends sur l'auth)
@router.get("/")
def list_products(db: DBSession, ...):
    ...

# Route AUTHENTIFIÉE
@router.post("/", status_code=201)
def create_product(
    product_data: ProductCreate,
    current_user: CurrentUser,  # Ajouter ceci
    db: DBSession,
):
    ...

# Route ADMIN uniquement
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    admin: AdminUser,  # Vérifie que l'user est admin
    db: DBSession,
):
    ...
```

### Étape 7 — Router des utilisateurs (20 min)

Créez `app/routers/users.py` :

```python
@router.get("/me", response_model=UserPublic)
def get_my_profile(current_user: CurrentUser):
    """Récupérer son propre profil."""
    ...

@router.patch("/me", response_model=UserPublic)
def update_my_profile(
    user_data: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Modifier son profil.
    Si new_password est fourni, vérifier current_password.
    """
    ...

@router.get("/", response_model=list[UserPublic])
def list_users(admin: AdminUser, db: DBSession):
    """Lister tous les utilisateurs (admin uniquement)."""
    ...

@router.patch("/{user_id}/toggle-active", response_model=UserPublic)
def toggle_user_active(user_id: int, admin: AdminUser, db: DBSession):
    """Activer/désactiver un utilisateur (admin uniquement)."""
    ...
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La démonstration complète du flux dans Postman : register → login → utiliser le token
> **Expliquer :** 1) POST /auth/register avec des données valides. 2) POST /auth/login, copier l'access_token. 3) Tentative POST /products/ sans token → 401. 4) Même requête avec header "Authorization: Bearer <token>" → 201. 5) Tentative DELETE /products/1 avec token user normal → 403. 6) Créer un compte admin, se connecter, DELETE → 204. Expliquer chaque réponse.

---

### Étape 8 — Migration Alembic (10 min)

```bash
# Générer la migration pour la table users
alembic revision --autogenerate -m "add users table"

# Appliquer
alembic upgrade head
```

Vérifiez que la table `users` a été créée correctement.

### Étape 9 — Tests (30 min)

Écrivez des tests pour les scénarios suivants :

**`tests/test_auth.py`** :
```python
def test_register_success(client):
    """Inscription avec données valides → 201."""
    ...

def test_register_duplicate_email(client, existing_user):
    """Email déjà utilisé → 409."""
    ...

def test_register_weak_password(client):
    """Mot de passe sans majuscule → 422."""
    ...

def test_login_success(client, existing_user):
    """Connexion valide → retourne les tokens."""
    ...

def test_login_wrong_password(client, existing_user):
    """Mauvais mot de passe → 401."""
    ...

def test_access_protected_route_without_token(client):
    """POST /products/ sans token → 401."""
    ...

def test_access_protected_route_with_token(client, auth_headers):
    """POST /products/ avec token valide → 201."""
    ...

def test_admin_only_route_as_user(client, auth_headers):
    """DELETE /products/ en tant que user normal → 403."""
    ...

def test_admin_only_route_as_admin(client, admin_headers):
    """DELETE /products/ en tant qu'admin → 204."""
    ...

def test_expired_token(client, regular_user):
    """Token expiré → 401."""
    ...

def test_refresh_token(client, existing_user):
    """Refresh token valide → nouveaux tokens."""
    ...
```

---

## Critères d'évaluation

| Critère | Points |
|---|---|
| Modèle User et schémas Pydantic | 10 |
| Hachage mot de passe (bcrypt) | 5 |
| Génération et validation JWT (access + refresh) | 20 |
| Endpoint register avec vérifications | 15 |
| Endpoint login (OAuth2 Password Flow) | 15 |
| Dépendances auth (get_current_user, admin) | 15 |
| Routes sécurisées selon les rôles | 10 |
| Tests automatisés (min. 8 tests auth) | 10 |
| **Total** | **100** |

### Bonus

- Implémenter la liste noire de tokens (blocklist en Redis ou en DB)
- Ajouter un endpoint `/auth/me` qui retourne les infos du token (sans requête DB)
- Implémenter la réinitialisation de mot de passe par email
- Ajouter des logs pour les tentatives de connexion échouées (rate limiting)

---

## Aide et indices

### Gestion du changement de mot de passe

```python
@router.patch("/me")
def update_profile(user_data: UserUpdate, current_user: CurrentUser, db: DBSession):
    if user_data.new_password:
        # Vérifier que l'ancien mot de passe est fourni
        if not user_data.current_password:
            raise HTTPException(400, "Le mot de passe actuel est requis")
        # Vérifier qu'il est correct
        if not verify_password(user_data.current_password, current_user.hashed_password):
            raise HTTPException(400, "Mot de passe actuel incorrect")
        # Hasher le nouveau
        current_user.hashed_password = hash_password(user_data.new_password)

    # Appliquer les autres modifications
    update_data = user_data.model_dump(exclude={"current_password", "new_password"}, exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
```

### Test avec token expiré

```python
from datetime import timedelta
from app.core.security import create_access_token

def test_expired_token(client, regular_user):
    # Créer un token déjà expiré
    expired = create_access_token(
        subject=regular_user.id,
        expires_delta=timedelta(seconds=-1),  # Expiré dans le passé
    )
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401
```

---

## Ressources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 avec Password et Bearer](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [python-jose documentation](https://python-jose.readthedocs.io/en/latest/)
- [passlib documentation](https://passlib.readthedocs.io/en/stable/)
- [JWT.io](https://jwt.io/) — Déboguer vos tokens JWT
