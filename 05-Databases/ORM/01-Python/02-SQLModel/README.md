# SQLModel — SQLAlchemy + Pydantic en un seul modèle

SQLModel est une bibliothèque créée par **Sebastián Ramírez** (l'auteur de FastAPI) qui combine SQLAlchemy et Pydantic en un seul modèle unifié.

## Le problème que SQLModel résout

Sans SQLModel, dans une application FastAPI + SQLAlchemy, vous devez maintenir deux modèles séparés :

```python
# Sans SQLModel : duplication de code

# Modèle SQLAlchemy (pour la BDD)
class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(500))

# Modèle Pydantic (pour l'API)
class UserCreate(BaseModel):
    name: str
    email: str
    password: str  # Reçu en clair

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # Pas de password dans la réponse !
```

SQLModel permet d'unifier ces déclarations.

## Contenu du module

| Fichier | Description |
|---------|-------------|
| [01-introduction.md](./01-introduction.md) | Concepts, installation, modèles de base |
| [02-integration-fastapi.md](./02-integration-fastapi.md) | CRUD complet avec FastAPI |

## Installation rapide

```bash
pip install sqlmodel
# SQLModel installe automatiquement SQLAlchemy et Pydantic
```

## Quand choisir SQLModel vs SQLAlchemy ?

| Critère | SQLModel | SQLAlchemy pur |
|---------|----------|----------------|
| Application FastAPI | Excellent | Bien |
| Validation des données | Intégrée (Pydantic) | Externe |
| Documentation OpenAPI | Auto-générée | Manuelle |
| Fonctionnalités avancées | Sous-ensemble SQLAlchemy | Complet |
| Projets sans FastAPI | Possible mais verbeux | Recommandé |
| Équipe Pydantic v2 | Compatible | Séparé |
