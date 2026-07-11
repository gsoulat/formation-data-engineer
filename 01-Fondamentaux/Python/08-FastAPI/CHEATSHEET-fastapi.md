# Cheatsheet FastAPI — Référence rapide

## Installation et démarrage

```bash
pip install "fastapi[standard]"          # Installation complète
pip install sqlalchemy asyncpg alembic   # DB
pip install python-jose[cryptography] passlib[bcrypt]  # Auth
pip install pytest httpx pytest-cov      # Tests

uvicorn main:app --reload                # Dev
uvicorn main:app --host 0.0.0.0 --workers 4  # Prod
```

---

## Application de base

```python
from fastapi import FastAPI

app = FastAPI(title="Mon API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "ok"}
```

---

## Routes HTTP

```python
@app.get("/items/")       # Lister
@app.post("/items/")      # Créer       (status_code=201)
@app.put("/items/{id}")   # Remplacer
@app.patch("/items/{id}") # Modifier partiellement
@app.delete("/items/{id}") # Supprimer  (status_code=204)
```

---

## Paramètres

```python
# Path parameter (typé automatiquement)
@app.get("/items/{item_id}")
def get_item(item_id: int): ...

# Query parameter (valeur par défaut = optionnel)
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10, q: str | None = None): ...

# Query avec validation
from fastapi import Query
from typing import Annotated
def list_items(q: Annotated[str, Query(min_length=3, max_length=50)] = None): ...

# Path avec validation
from fastapi import Path
def get_item(item_id: Annotated[int, Path(ge=1)]): ...

# Request body (modèle Pydantic)
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item): ...
```

---

## Pydantic

```python
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from datetime import datetime
from typing import Annotated

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0, le=10000)
    email: EmailStr
    tags: list[str] = []
    created_at: datetime = None

    # Validator sur un champ
    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().title()

    # Validator inter-champs
    @model_validator(mode="after")
    def check_logic(self) -> "Product":
        # Vos vérifications ici
        return self

# Sérialisation
product.model_dump()                        # → dict
product.model_dump(exclude={"password"})    # Exclure un champ
product.model_dump(exclude_unset=True)      # Seulement les champs définis
product.model_dump_json()                   # → JSON string

# Création depuis dict/JSON
Product.model_validate({"name": "Test", "price": 9.99})
Product.model_validate_json('{"name": "Test", "price": 9.99}')

# Config courante
from pydantic.config import ConfigDict
class MyModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,   # Pour SQLAlchemy
        populate_by_name=True,  # Pour les alias
        extra="forbid",         # Refuser les champs inconnus
    )
```

---

## Response Model

```python
# Filtrer la réponse (ex: exclure le mot de passe)
@app.post("/users/", response_model=UserPublic)
def create_user(user: UserCreate): ...

# Liste
@app.get("/users/", response_model=list[UserPublic])
def list_users(): ...

# Exclure les champs non définis
@app.get("/items/{id}", response_model=Item, response_model_exclude_unset=True)
def get_item(id: int): ...
```

---

## Codes de statut

```python
from fastapi import status

status.HTTP_200_OK          # 200
status.HTTP_201_CREATED     # 201
status.HTTP_204_NO_CONTENT  # 204
status.HTTP_400_BAD_REQUEST # 400
status.HTTP_401_UNAUTHORIZED # 401
status.HTTP_403_FORBIDDEN   # 403
status.HTTP_404_NOT_FOUND   # 404
status.HTTP_409_CONFLICT    # 409
status.HTTP_422_UNPROCESSABLE_ENTITY # 422

# Lever une erreur HTTP
from fastapi import HTTPException
raise HTTPException(status_code=404, detail="Introuvable")
raise HTTPException(status_code=401, detail="Non authentifié",
                    headers={"WWW-Authenticate": "Bearer"})
```

---

## APIRouter

```python
# app/routers/products.py
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/")
def list_products(): ...

# app/main.py
app.include_router(products.router)
app.include_router(users.router, prefix="/api/v1")
```

---

## Injection de dépendances

```python
from fastapi import Depends
from typing import Annotated

# Définir une dépendance
def get_settings():
    return {"debug": True}

# L'utiliser
@app.get("/info")
def info(settings: Annotated[dict, Depends(get_settings)]):
    return settings

# Dépendance sans retour (juste vérifier)
def check_auth(token: str = Header(...)):
    if token != "secret":
        raise HTTPException(401)

@app.get("/secure", dependencies=[Depends(check_auth)])
def secure(): ...
```

---

## SQLAlchemy

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine("postgresql://user:pass@localhost/db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# CRUD
db.query(Product).all()                                    # SELECT *
db.query(Product).filter(Product.id == id).first()         # WHERE id = x
db.query(Product).filter(Product.is_active == True).all()  # WHERE active
db.query(Product).filter(Product.name.ilike("%test%")).all() # LIKE

new = Product(name="Test", price=9.99)
db.add(new)
db.commit()
db.refresh(new)  # Recharger (pour avoir l'ID auto)

setattr(product, "price", 14.99)
db.commit()

db.delete(product)
db.commit()
```

---

## JWT Authentication

```python
# core/security.py
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: int | str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({"sub": str(subject), "exp": expire}, SECRET_KEY, ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Token invalide")


# core/deps.py
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = decode_token(token)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(401, "Utilisateur introuvable")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


# Login endpoint
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/auth/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBSession):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Identifiants incorrects",
                           headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```

---

## Tests

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    conn = engine.connect()
    trans = conn.begin()
    Session = sessionmaker(bind=conn)
    session = Session()
    yield session
    session.close()
    trans.rollback()
    conn.close()

@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# test_products.py
def test_create_product(client):
    r = client.post("/products/", json={"name": "Test", "price": 9.99})
    assert r.status_code == 201
    assert r.json()["name"] == "Test"

def test_not_found(client):
    r = client.get("/products/99999")
    assert r.status_code == 404

def test_validation_error(client):
    r = client.post("/products/", json={"name": "Test"})  # price manquant
    assert r.status_code == 422
```

```bash
pytest                        # Lancer tous les tests
pytest -v                     # Mode verbose
pytest -k "test_create"       # Filtrer par nom
pytest --cov=app              # Avec couverture
pytest --cov=app --cov-report=html  # Rapport HTML
```

---

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://monsite.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Alembic

```bash
alembic init alembic                                  # Initialiser
alembic revision --autogenerate -m "create users"     # Créer migration
alembic upgrade head                                  # Appliquer tout
alembic upgrade +1                                    # +1 migration
alembic downgrade -1                                  # -1 migration
alembic downgrade base                                # Tout annuler
alembic current                                       # État actuel
alembic history --verbose                             # Historique
```

---

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 5s
      retries: 5

  api:
    build: .
    ports: ["8000:8000"]
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://myuser:mypassword@db:5432/mydb
```

```bash
docker-compose up -d          # Démarrer
docker-compose down           # Arrêter
docker-compose down -v        # Arrêter + supprimer les volumes
docker-compose logs -f api    # Voir les logs
docker-compose exec api bash  # Shell dans le conteneur
docker-compose ps             # État des services
```

---

## Réponses utiles

```python
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse, PlainTextResponse

# JSON avec headers custom
return JSONResponse(content={"ok": True}, headers={"X-Custom": "value"})

# Redirection
return RedirectResponse(url="/new-url", status_code=302)

# Texte brut
return PlainTextResponse("Hello world")
```

---

## Lifecycle / Events

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Démarrage")    # Code de démarrage
    yield
    print("Arrêt")        # Code d'arrêt

app = FastAPI(lifespan=lifespan)
```

---

## Middleware de logging

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    response.headers["X-Process-Time"] = str(duration)
    return response
```

---

## URLs importantes en développement

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI (docs interactives) |
| `http://localhost:8000/redoc` | ReDoc (docs lisibles) |
| `http://localhost:8000/openapi.json` | Schéma OpenAPI JSON |
