# Module 06 — Authentification et sécurité

## Sommaire
1. [Concepts de sécurité pour les APIs](#1-concepts-de-sécurité-pour-les-apis)
2. [Authentification par clé API](#2-authentification-par-clé-api)
3. [Hachage des mots de passe](#3-hachage-des-mots-de-passe)
4. [Tokens JWT — concepts](#4-tokens-jwt--concepts)
5. [Implémentation JWT avec python-jose](#5-implémentation-jwt-avec-python-jose)
6. [Flux OAuth2 Password](#6-flux-oauth2-password)
7. [Dépendances de sécurité](#7-dépendances-de-sécurité)
8. [Rôles et permissions](#8-rôles-et-permissions)
9. [Sécurité en production](#9-sécurité-en-production)

---

## 1. Concepts de sécurité pour les APIs

### Les différents mécanismes d'authentification

| Mécanisme | Cas d'usage | Avantages | Inconvénients |
|---|---|---|---|
| **API Key** | Services B2B, bots | Simple | Pas de granularité, révocation difficile |
| **Basic Auth** | Développement, API internes | Ultra-simple | Mot de passe en clair (base64) |
| **JWT** | Applications web/mobile | Stateless, scalable | Révocation complexe |
| **OAuth2** | Délégation d'autorisation | Standard industriel | Complexe à implémenter |
| **Session** | Applications web traditionnelles | Simple | Stateful, pas REST |

### Ce que nous allons implémenter

1. **API Key** : pour les clients de service
2. **JWT** : pour les utilisateurs de l'application
3. **OAuth2 Password Flow** : le standard FastAPI recommandé

### Installation des dépendances

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

---

## 2. Authentification par clé API

L'authentification par clé API est la plus simple. Le client envoie une clé secrète dans un header.

### Clé API dans le header

```python
# app/core/api_key.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

# Définir le schéma de sécurité (header "X-API-Key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Liste des clés valides (en pratique : depuis la DB)
VALID_API_KEYS = {
    "key-service-a-1234": "Service A",
    "key-service-b-5678": "Service B",
}

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Dépendance qui vérifie la clé API."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante. Fournissez le header X-API-Key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide ou révoquée.",
        )

    return VALID_API_KEYS[api_key]  # Retourne le nom du service
```

```python
# Utilisation dans une route
from fastapi import FastAPI, Depends
from app.core.api_key import verify_api_key

app = FastAPI()

@app.get("/internal/stats")
def get_stats(service_name: str = Depends(verify_api_key)):
    return {
        "accessed_by": service_name,
        "total_users": 1000,
        "total_orders": 5000,
    }
```

### Clé API dans les paramètres de requête (moins sécurisé)

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyQuery

api_key_query = APIKeyQuery(name="api_key", auto_error=False)

async def verify_api_key_query(api_key: str = Security(api_key_query)):
    if api_key != "secret-key":
        raise HTTPException(status_code=403, detail="Clé API invalide")
    return api_key

# GET /data?api_key=secret-key
@app.get("/data")
def get_data(key: str = Depends(verify_api_key_query)):
    return {"data": "..."}
```

---

## 3. Hachage des mots de passe

**Règle absolue** : ne jamais stocker les mots de passe en clair. Toujours les hasher.

```python
# app/core/security.py
from passlib.context import CryptContext

# Configurer passlib avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """Hasher un mot de passe en clair."""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier qu'un mot de passe correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

```python
# Utilisation
from app.core.security import hash_password, verify_password

# À la création du compte
hashed = hash_password("MonMotDePasse123!")
# Résultat : "$2b$12$..." (hash bcrypt)

# À la connexion
is_valid = verify_password("MonMotDePasse123!", hashed)  # True
is_valid = verify_password("mauvais", hashed)             # False
```

---

## 4. Tokens JWT — concepts

### Qu'est-ce qu'un JWT ?

Un **JSON Web Token** (JWT) est un token auto-contenu qui encode des informations (claims) et est signé cryptographiquement.

Structure : `header.payload.signature`

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  ← header (base64)
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.  ← payload (base64)
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← signature (HMAC-SHA256)
```

Le payload (décodé) ressemble à :
```json
{
  "sub": "1",           // Subject = user_id
  "email": "alice@example.com",
  "role": "admin",
  "iat": 1516239022,    // Issued At
  "exp": 1516242622     // Expiration
}
```

### Pourquoi JWT ?

1. **Stateless** : le serveur n'a pas besoin de stocker les sessions
2. **Scalable** : n'importe quel serveur peut valider le token
3. **Portable** : fonctionne entre services (microservices)
4. **Auto-contenu** : contient les informations nécessaires

### Limites du JWT

- Ne peut pas être révoqué avant expiration (sans liste noire)
- Ne pas stocker de données sensibles dans le payload (il est seulement encodé, pas chiffré)
- La durée de validité doit être courte (15 min à 1h)

---

## 5. Implémentation JWT avec python-jose

```python
# app/core/security.py (version complète)
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Configuration
SECRET_KEY = "votre-clé-secrète-très-longue-et-aléatoire"  # Depuis .env en prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int,
    extra_data: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Créer un token JWT d'accès.

    Args:
        subject: L'identifiant du sujet (user_id ou username)
        extra_data: Données supplémentaires à inclure dans le token
        expires_delta: Durée de validité (défaut: ACCESS_TOKEN_EXPIRE_MINUTES)
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    if extra_data:
        payload.update(extra_data)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str | int) -> str:
    """Créer un token de refresh (durée de vie plus longue)."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Décoder et valider un token JWT.

    Raises:
        HTTPException 401 si le token est invalide ou expiré
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide ou expiré : {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

---

## 6. Flux OAuth2 Password

C'est le flux recommandé par FastAPI pour les APIs avec authentification utilisateur.

### Les schémas Pydantic

```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Réponse du endpoint de connexion."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Données extraites du token."""
    user_id: int | None = None

class LoginRequest(BaseModel):
    """Requête de connexion."""
    username: str  # Email ou username
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
```

### Le router d'authentification

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.auth import Token, UserCreate
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Authentification"])
DBSession = Annotated[Session, Depends(get_db)]


@router.post("/register", status_code=201)
def register(user_data: UserCreate, db: DBSession):
    """Créer un nouveau compte utilisateur."""
    # Vérifier que le username n'existe pas
    if db.query(UserModel).filter(UserModel.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur est déjà pris"
        )

    # Vérifier que l'email n'existe pas
    if db.query(UserModel).filter(UserModel.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà utilisé"
        )

    # Créer l'utilisateur
    db_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "Compte créé avec succès", "user_id": db_user.id}


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """
    Se connecter et obtenir un token JWT.

    Compatible avec le flux OAuth2 Password (utilisé par Swagger UI).
    """
    # Chercher l'utilisateur par username ou email
    user = (
        db.query(UserModel)
        .filter(
            (UserModel.username == form_data.username) |
            (UserModel.email == form_data.username)
        )
        .first()
    )

    # Vérifier l'existence et le mot de passe
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )

    # Générer les tokens
    access_token = create_access_token(
        subject=user.id,
        extra_data={"username": user.username, "is_admin": user.is_admin},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: DBSession):
    """Renouveler les tokens à partir d'un refresh token."""
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de type invalide"
        )

    user_id = int(payload["sub"])
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable ou inactif")

    new_access = create_access_token(
        subject=user.id,
        extra_data={"username": user.username, "is_admin": user.is_admin},
    )
    new_refresh = create_refresh_token(subject=user.id)

    return Token(access_token=new_access, refresh_token=new_refresh)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Postman ou Swagger UI — démonstration complète du flux de connexion JWT
> **Expliquer :** 1) Montrer la route POST /auth/register avec un payload JSON. 2) Montrer la route POST /auth/login avec username/password. Copier le access_token retourné. 3) Montrer une route protégée retournant 401. 4) Ajouter le header `Authorization: Bearer <token>` dans Postman et refaire la requête — montrer le succès 200. 5) Dans Swagger, utiliser le bouton "Authorize" et entrer les identifiants.

---

## 7. Dépendances de sécurité

### La dépendance `get_current_user`

```python
# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User as UserModel
from app.core.security import decode_token

# Schéma OAuth2 — pointe vers notre endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    """
    Dépendance qui extrait et valide l'utilisateur depuis le token JWT.

    Raises:
        401 si le token est invalide
        401 si l'utilisateur n'existe pas en base
    """
    payload = decode_token(token)

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : champ 'sub' manquant"
        )

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"
        )

    return user


def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
) -> UserModel:
    """Dépendance qui vérifie que l'utilisateur est actif."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    return current_user


def get_current_admin_user(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
) -> UserModel:
    """Dépendance qui vérifie que l'utilisateur est admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user


# Alias pratiques
CurrentUser = Annotated[UserModel, Depends(get_current_active_user)]
AdminUser = Annotated[UserModel, Depends(get_current_admin_user)]
```

### Utilisation dans les routes

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import CurrentUser, AdminUser
from app.models.user import User as UserModel

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_my_profile(current_user: CurrentUser):
    """Récupérer son propre profil (authentification requise)."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }


@router.get("/", dependencies=[Depends(get_current_admin_user)])
def list_all_users(db: Annotated[Session, Depends(get_db)]):
    """Lister tous les utilisateurs (admin seulement)."""
    return db.query(UserModel).all()


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, admin: AdminUser, db: Annotated[Session, Depends(get_db)]):
    """Supprimer un utilisateur (admin seulement)."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Empêcher l'admin de se supprimer lui-même
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")

    db.delete(user)
    db.commit()
```

### Configurer l'app principale avec OAuth2

```python
# app/main.py
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routers import auth, users, products

app = FastAPI(
    title="Mon API Sécurisée",
    # Configuration pour Swagger UI : bouton Authorize avec OAuth2
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La Swagger UI avec le bouton "Authorize" et le processus d'authentification
> **Expliquer :** Montrer le bouton cadenas vert/rouge sur chaque route. Cliquer "Authorize" en haut à droite. Entrer username et password. Montrer que le cadenas devient vert. Tester une route protégée avant et après la connexion. Montrer le header Authorization: Bearer dans les détails de la requête.

---

## 8. Rôles et permissions

### Système de permissions basé sur les rôles

```python
# app/core/permissions.py
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status, Depends
from typing import Annotated
from app.models.user import User
from app.core.deps import get_current_active_user

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


def require_role(*roles: Role):
    """
    Factory de dépendances pour vérifier les rôles.

    Usage: @router.get("/...", dependencies=[Depends(require_role(Role.ADMIN))])
    """
    def check_role(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        user_roles = set(current_user.roles or [Role.USER])
        allowed_roles = set(roles)

        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis : {', '.join(r.value for r in roles)}"
            )
        return current_user

    return check_role


# Usage dans les routes
@router.get(
    "/admin/stats",
    dependencies=[Depends(require_role(Role.ADMIN, Role.MODERATOR))]
)
def get_admin_stats():
    return {"stats": "données sensibles"}
```

---

## 9. Sécurité en production

### Configuration sécurisée

```python
# app/config.py — version production
from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    # Clé secrète : DOIT être longue et aléatoire en prod
    # Générer avec : python -c "import secrets; print(secrets.token_urlsafe(64))"
    secret_key: str = secrets.token_urlsafe(64)  # Défaut aléatoire (dev only)

    # Durées des tokens
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # HTTPS uniquement en production
    secure_cookies: bool = True

    # CORS strict en production
    allowed_origins: list[str] = ["https://mon-frontend.com"]

    # Rate limiting
    max_requests_per_minute: int = 60
```

### Checklist de sécurité

```markdown
## Avant de mettre en production

- [ ] SECRET_KEY longue et aléatoire (min 32 chars)
- [ ] SECRET_KEY dans les variables d'environnement (pas dans le code)
- [ ] Mots de passe hashés avec bcrypt
- [ ] HTTPS obligatoire (pas de HTTP)
- [ ] CORS configuré avec les domaines exacts
- [ ] Durée des tokens courte (30 min pour access, 7j pour refresh)
- [ ] Validation de toutes les entrées avec Pydantic
- [ ] Logs des tentatives de connexion échouées
- [ ] Rate limiting sur les routes d'authentification
- [ ] Docs Swagger désactivées en production (docs_url=None)
```

### Désactiver la doc en production

```python
from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="Mon API",
    # En production, désactiver les docs
    docs_url=None if not settings.debug else "/docs",
    redoc_url=None if not settings.debug else "/redoc",
    openapi_url=None if not settings.debug else "/openapi.json",
)
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `APIKeyHeader` | Authentification par clé API dans un header |
| `passlib` + `bcrypt` | Hasher les mots de passe |
| JWT | Token auto-contenu, signé, avec expiration |
| `python-jose` | Créer et valider des tokens JWT |
| `OAuth2PasswordBearer` | Schéma OAuth2 pour FastAPI |
| `Depends(get_current_user)` | Injection de l'utilisateur courant |
| `OAuth2PasswordRequestForm` | Formulaire de connexion (username/password) |
| `SECRET_KEY` | Ne jamais hardcoder en production |

---

**Précédent** : [Module 05 — Bases de données](./05-bases-de-donnees.md)
**Suite** : [Module 07 — Tests](./07-tests.md)
