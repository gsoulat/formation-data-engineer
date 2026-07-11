# Module 07 — Tests automatisés

## Sommaire
1. [Pourquoi tester son API ?](#1-pourquoi-tester-son-api-)
2. [TestClient de FastAPI](#2-testclient-de-fastapi)
3. [Configuration pytest](#3-configuration-pytest)
4. [Fixtures pytest](#4-fixtures-pytest)
5. [Tester les routes CRUD](#5-tester-les-routes-crud)
6. [Tester l'authentification](#6-tester-lauthentification)
7. [Mocker les dépendances](#7-mocker-les-dépendances)
8. [Tests asynchrones](#8-tests-asynchrones)
9. [Couverture de code (coverage)](#9-couverture-de-code-coverage)

---

## 1. Pourquoi tester son API ?

### Les types de tests

```
Tests d'intégration (TestClient)
├── Testent toute la pile : routing → validation → logique → DB
├── Lents (accès DB réel ou mockée)
└── Fiables pour détecter les régressions

Tests unitaires
├── Testent une fonction isolément
├── Rapides
└── Idéaux pour la logique métier complexe

Tests de bout en bout (E2E)
├── Testent le système complet (API + frontend)
├── Très lents
└── Peu nombreux, pour les chemins critiques
```

### Installation

```bash
pip install pytest pytest-asyncio httpx

# Pour la couverture de code
pip install pytest-cov

# Pour les mocks
pip install pytest-mock
```

---

## 2. TestClient de FastAPI

`TestClient` est un client HTTP synchrone basé sur `httpx` qui permet de tester votre API sans démarrer un vrai serveur.

### Premier test

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

# Créer le client de test
client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API !"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_not_found():
    response = client.get("/cette-route-nexiste-pas")
    assert response.status_code == 404
```

```bash
# Lancer les tests
pytest

# Avec sortie détaillée
pytest -v

# Un fichier spécifique
pytest tests/test_main.py

# Une fonction spécifique
pytest tests/test_main.py::test_root
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal montrant l'exécution de `pytest -v` avec des tests qui passent
> **Expliquer :** Lancer `pytest -v` et montrer le résultat avec les tests en vert. Montrer les points (`.`) pour chaque test réussi, les `F` pour les échecs. Expliquer la structure du message d'erreur quand un test échoue. Montrer comment relancer seulement les tests en échec avec `pytest --last-failed`.

---

### TestClient — méthodes disponibles

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# GET avec paramètres de requête
response = client.get("/items/", params={"skip": 0, "limit": 10, "search": "test"})

# POST avec corps JSON
response = client.post("/items/", json={"name": "Test", "price": 9.99})

# PUT
response = client.put("/items/1", json={"name": "Modifié", "price": 14.99})

# PATCH
response = client.patch("/items/1", json={"price": 12.99})

# DELETE
response = client.delete("/items/1")

# Avec headers
response = client.get(
    "/protected/",
    headers={"Authorization": "Bearer mon-token-jwt"}
)

# Avec cookies
response = client.get("/profile/", cookies={"session": "abc123"})

# Upload de fichier
with open("test.txt", "rb") as f:
    response = client.post("/upload/", files={"file": ("test.txt", f, "text/plain")})

# Formulaire
response = client.post("/login/", data={"username": "alice", "password": "secret"})
```

---

## 3. Configuration pytest

### `conftest.py` — fichier de configuration central

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Base de données SQLite en mémoire pour les tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="session")
def engine():
    """Créer le moteur SQLite en mémoire (une seule fois par session de tests)."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Connexion partagée pour SQLite en mémoire
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Session DB propre pour chaque test (rollback après chaque test)."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()  # Annuler toutes les modifications du test
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient FastAPI avec la base de données de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Remplacer la dépendance get_db par notre version de test
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
```

### `pytest.ini` ou `pyproject.toml`

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = ["-v", "--tb=short"]
asyncio_mode = "auto"
```

---

## 4. Fixtures pytest

### Fixtures de données (factories)

```python
# tests/factories.py
from app.models.user import User
from app.models.product import Product
from app.core.security import hash_password
from sqlalchemy.orm import Session


def create_user(
    db: Session,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPassword123!",
    is_admin: bool = False,
    is_active: bool = True,
) -> User:
    """Créer un utilisateur de test en base."""
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_admin=is_admin,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_product(
    db: Session,
    name: str = "Produit Test",
    price: float = 9.99,
    stock: int = 100,
    is_active: bool = True,
) -> Product:
    """Créer un produit de test en base."""
    product = Product(
        name=name,
        price=price,
        stock=stock,
        is_active=is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
```

```python
# tests/conftest.py (avec fixtures de données)
import pytest
from tests.factories import create_user, create_product
from app.core.security import create_access_token


@pytest.fixture
def regular_user(db_session):
    """Fixture : utilisateur standard."""
    return create_user(db_session, username="alice", email="alice@test.com")


@pytest.fixture
def admin_user(db_session):
    """Fixture : utilisateur admin."""
    return create_user(db_session, username="admin", email="admin@test.com", is_admin=True)


@pytest.fixture
def auth_headers(regular_user):
    """Fixture : headers d'authentification pour regular_user."""
    token = create_access_token(subject=regular_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user):
    """Fixture : headers d'authentification pour admin."""
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_products(db_session):
    """Fixture : liste de produits de test."""
    products = [
        create_product(db_session, name="Marteau", price=29.99),
        create_product(db_session, name="Tournevis", price=9.99),
        create_product(db_session, name="Perceuse", price=149.99),
    ]
    return products
```

---

## 5. Tester les routes CRUD

### Tests des produits

```python
# tests/test_products.py
import pytest
from fastapi.testclient import TestClient


class TestListProducts:
    def test_list_products_empty(self, client: TestClient):
        """Liste vide quand aucun produit en base."""
        response = client.get("/products/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_products(self, client: TestClient, sample_products):
        """Liste retourne tous les produits actifs."""
        response = client.get("/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_products_pagination(self, client: TestClient, sample_products):
        """Pagination fonctionne correctement."""
        # Première page
        response = client.get("/products/?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Deuxième page
        response = client.get("/products/?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_products_search(self, client: TestClient, sample_products):
        """Recherche filtre correctement."""
        response = client.get("/products/?search=marteau")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Marteau"


class TestGetProduct:
    def test_get_existing_product(self, client: TestClient, sample_products):
        """Récupérer un produit existant."""
        product_id = sample_products[0].id
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Marteau"
        assert data["price"] == 29.99

    def test_get_nonexistent_product(self, client: TestClient):
        """Retourne 404 pour un ID inexistant."""
        response = client.get("/products/99999")
        assert response.status_code == 404
        assert "introuvable" in response.json()["detail"].lower()

    def test_get_product_invalid_id(self, client: TestClient):
        """Retourne 422 pour un ID non entier."""
        response = client.get("/products/abc")
        assert response.status_code == 422


class TestCreateProduct:
    def test_create_product_success(self, client: TestClient, auth_headers):
        """Créer un produit avec données valides."""
        payload = {
            "name": "Nouveau Produit",
            "price": 49.99,
            "stock": 10,
        }
        response = client.post("/products/", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Nouveau Produit"
        assert data["price"] == 49.99
        assert "id" in data
        assert data["id"] is not None

    def test_create_product_without_auth(self, client: TestClient):
        """Retourne 401 sans authentification."""
        payload = {"name": "Test", "price": 9.99}
        response = client.post("/products/", json=payload)
        assert response.status_code == 401

    def test_create_product_missing_required_field(self, client: TestClient, auth_headers):
        """Retourne 422 si price manquant."""
        payload = {"name": "Sans prix"}
        response = client.post("/products/", json=payload, headers=auth_headers)
        assert response.status_code == 422
        errors = response.json()["detail"]
        field_names = [e["loc"][-1] for e in errors]
        assert "price" in field_names

    def test_create_product_negative_price(self, client: TestClient, auth_headers):
        """Retourne 422 si price négatif."""
        payload = {"name": "Test", "price": -10.0}
        response = client.post("/products/", json=payload, headers=auth_headers)
        assert response.status_code == 422

    def test_create_product_duplicate_sku(self, client: TestClient, auth_headers, sample_products):
        """Retourne 409 si SKU déjà utilisé."""
        payload = {
            "name": "Produit 1",
            "price": 9.99,
            "sku": "ABC-1234"
        }
        client.post("/products/", json=payload, headers=auth_headers)  # Premier
        response = client.post("/products/", json=payload, headers=auth_headers)  # Doublon
        assert response.status_code == 409


class TestUpdateProduct:
    def test_update_product_success(self, client: TestClient, auth_headers, sample_products):
        """Mise à jour réussie."""
        product_id = sample_products[0].id
        payload = {"name": "Marteau Modifié", "price": 24.99}
        response = client.patch(f"/products/{product_id}", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Marteau Modifié"
        assert data["price"] == 24.99

    def test_update_nonexistent_product(self, client: TestClient, auth_headers):
        """Retourne 404 pour un produit inexistant."""
        response = client.patch("/products/99999", json={"price": 5.0}, headers=auth_headers)
        assert response.status_code == 404


class TestDeleteProduct:
    def test_delete_product_success(self, client: TestClient, admin_headers, sample_products):
        """Suppression par un admin réussie."""
        product_id = sample_products[0].id
        response = client.delete(f"/products/{product_id}", headers=admin_headers)
        assert response.status_code == 204

        # Vérifier que le produit n'existe plus
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == 404

    def test_delete_product_non_admin(self, client: TestClient, auth_headers, sample_products):
        """Retourne 403 pour un non-admin."""
        product_id = sample_products[0].id
        response = client.delete(f"/products/{product_id}", headers=auth_headers)
        assert response.status_code == 403
```

---

## 6. Tester l'authentification

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        """Inscription réussie."""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data

    def test_register_duplicate_username(self, client: TestClient, regular_user):
        """Erreur si username déjà pris."""
        payload = {
            "username": regular_user.username,  # même username
            "email": "autre@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_register_weak_password(self, client: TestClient):
        """Erreur si mot de passe trop faible."""
        payload = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "123",  # Trop court
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_invalid_email(self, client: TestClient):
        """Erreur si email invalide."""
        payload = {
            "username": "testuser3",
            "email": "pas-un-email",
            "password": "SecurePass123!",
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient, regular_user):
        """Connexion réussie, retourne un token JWT."""
        response = client.post(
            "/auth/login",
            data={  # OAuth2 utilise form data, pas JSON
                "username": regular_user.username,
                "password": "TestPassword123!",  # Voir la fixture create_user
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10  # Token non vide

    def test_login_wrong_password(self, client: TestClient, regular_user):
        """401 si mot de passe incorrect."""
        response = client.post(
            "/auth/login",
            data={"username": regular_user.username, "password": "mauvais_mdp"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """401 si utilisateur inexistant."""
        response = client.post(
            "/auth/login",
            data={"username": "userquiexistepas", "password": "nimportequoi"}
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, client: TestClient, db_session):
        """403 si compte désactivé."""
        from tests.factories import create_user
        inactive = create_user(
            db_session,
            username="inactive",
            email="inactive@test.com",
            is_active=False,
        )
        response = client.post(
            "/auth/login",
            data={"username": "inactive", "password": "TestPassword123!"}
        )
        assert response.status_code == 403


class TestProtectedRoutes:
    def test_access_without_token(self, client: TestClient):
        """401 sans token."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_access_with_valid_token(self, client: TestClient, auth_headers, regular_user):
        """200 avec un token valide."""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == regular_user.id

    def test_access_with_invalid_token(self, client: TestClient):
        """401 avec un token invalide."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer token-completement-invalide"}
        )
        assert response.status_code == 401

    def test_access_with_expired_token(self, client: TestClient, regular_user):
        """401 avec un token expiré."""
        from datetime import timedelta
        from app.core.security import create_access_token
        expired_token = create_access_token(
            subject=regular_user.id,
            expires_delta=timedelta(seconds=-1),  # Déjà expiré
        )
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
```

---

## 7. Mocker les dépendances

### Remplacer une dépendance FastAPI

```python
# tests/test_with_mocks.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.core.deps import get_current_active_user
from app.database import get_db


def test_with_mocked_user():
    """Tester une route protégée en mockant l'utilisateur."""
    # Créer un faux utilisateur
    fake_user = MagicMock()
    fake_user.id = 42
    fake_user.username = "fakeuser"
    fake_user.email = "fake@test.com"
    fake_user.is_active = True
    fake_user.is_admin = False

    # Remplacer la dépendance
    app.dependency_overrides[get_current_active_user] = lambda: fake_user

    with TestClient(app) as client:
        response = client.get("/users/me")
        assert response.status_code == 200
        assert response.json()["username"] == "fakeuser"

    # Nettoyer
    app.dependency_overrides.clear()


class TestWithMockedDB:
    """Tests qui mockent entièrement la base de données."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self, client):
        """Fixture qui s'exécute automatiquement avant chaque test."""
        self.mock_db = MagicMock()

    def test_service_with_mock_db(self):
        """Tester la logique métier sans vraie DB."""
        from app.crud.product import get_product

        # Configurer le mock
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Produit Mocké"
        mock_product.price = 99.99

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_product

        # Appeler la fonction
        result = get_product(self.mock_db, product_id=1)

        # Vérifier
        assert result.name == "Produit Mocké"
        self.mock_db.query.assert_called_once()
```

### Mocker des services externes

```python
# tests/test_email_service.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


def test_register_sends_welcome_email():
    """Vérifier qu'un email est envoyé lors de l'inscription."""
    with patch("app.services.email.send_email") as mock_send:
        mock_send.return_value = True

        with TestClient(app) as client:
            response = client.post("/auth/register", json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "SecurePass123!",
            })

        assert response.status_code == 201
        mock_send.assert_called_once_with(
            to="new@example.com",
            subject="Bienvenue !",
        )


def test_register_handles_email_failure():
    """L'inscription réussit même si l'envoi d'email échoue."""
    with patch("app.services.email.send_email") as mock_send:
        mock_send.side_effect = Exception("SMTP error")

        with TestClient(app) as client:
            response = client.post("/auth/register", json={
                "username": "newuser2",
                "email": "new2@example.com",
                "password": "SecurePass123!",
            })

        # L'inscription doit quand même réussir
        assert response.status_code == 201
```

---

## 8. Tests asynchrones

```python
# tests/test_async.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_async_root():
    """Test async avec AsyncClient."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_async_create_and_get():
    """Test async : créer puis récupérer un produit."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Créer
        create_response = await client.post(
            "/products/",
            json={"name": "Test Async", "price": 9.99}
        )
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        # Récupérer
        get_response = await client.get(f"/products/{product_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Test Async"
```

---

## 9. Couverture de code (coverage)

```bash
# Lancer les tests avec couverture
pytest --cov=app --cov-report=term-missing

# Générer un rapport HTML
pytest --cov=app --cov-report=html

# Avec un seuil minimum (échoue si < 80%)
pytest --cov=app --cov-fail-under=80
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal montrant le rapport de couverture de code après `pytest --cov=app --cov-report=term-missing`
> **Expliquer :** Montrer les colonnes du rapport (Stmts, Miss, Cover, Missing). Pointer les lignes non couvertes. Expliquer comment ouvrir le rapport HTML avec `open htmlcov/index.html`. Montrer dans le navigateur les lignes de code non testées surlignées en rouge. Expliquer que 80-90% de couverture est un bon objectif.

---

### Exclure du code de la couverture

```python
# Exclure une ligne
x = some_function()  # pragma: no cover

# Exclure un bloc
if TYPE_CHECKING:  # pragma: no cover
    from app.models import SomeModel
```

```ini
# setup.cfg ou .coveragerc
[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
    raise NotImplementedError
    if TYPE_CHECKING:
```

---

## Récapitulatif

| Concept | À retenir |
|---|---|
| `TestClient(app)` | Client HTTP pour tester sans démarrer le serveur |
| `conftest.py` | Fichier de fixtures partagées |
| `@pytest.fixture` | Définir une fixture réutilisable |
| `db_session` | Session DB avec rollback après chaque test |
| `dependency_overrides` | Remplacer une dépendance FastAPI dans les tests |
| `@patch(...)` | Mocker des fonctions externes (unittest.mock) |
| `pytest --cov=app` | Mesurer la couverture de code |
| SQLite en mémoire | Base de données rapide pour les tests |

---

**Précédent** : [Module 06 — Authentification](./06-authentification.md)
**Suite** : [Module 08 — Docker et déploiement](./08-docker-deploiement.md)
