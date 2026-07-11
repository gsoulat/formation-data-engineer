# Formation FastAPI — API REST Modernes en Python

## Présentation

Cette formation vous guide pas à pas dans la création d'APIs REST robustes, performantes et sécurisées avec **FastAPI**, le framework Python le plus rapide et le plus populaire pour construire des services web modernes.

FastAPI est aujourd'hui le standard de l'industrie pour développer des APIs en Python. Il combine la simplicité de Python avec des performances proches de Node.js et Go, tout en générant automatiquement une documentation interactive.

---

## Objectifs pédagogiques

À l'issue de cette formation, vous serez capable de :

- Créer une API REST complète avec FastAPI
- Valider les données d'entrée et de sortie avec Pydantic
- Connecter votre API à une base de données PostgreSQL via SQLAlchemy
- Sécuriser votre API avec des clés API et des tokens JWT
- Écrire des tests automatisés pour vos routes
- Déployer votre API avec Docker et docker-compose
- Lire et utiliser la documentation Swagger générée automatiquement

---

## Prérequis

### Connaissances requises

| Domaine | Niveau requis |
|---|---|
| Python | Intermédiaire (fonctions, classes, décorateurs) |
| HTTP / REST | Notions de base (GET, POST, PUT, DELETE, codes de statut) |
| JSON | Savoir lire et écrire du JSON |
| SQL | Bases (SELECT, INSERT, UPDATE, DELETE) |
| Terminal / ligne de commande | Utilisation basique |

### Environnement technique

- Python 3.11 ou supérieur
- pip ou uv (gestionnaire de paquets)
- Un éditeur de code (VS Code recommandé avec l'extension Python)
- Docker Desktop (pour le module déploiement)
- Postman ou Bruno (pour tester les APIs)
- Git

### Installation de l'environnement

```bash
# Vérifier la version de Python
python --version  # doit afficher 3.11+

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Linux/macOS)
source venv/bin/activate

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Installer FastAPI et ses dépendances
pip install "fastapi[standard]"
```

---

## Structure de la formation

```
FastAPI/
├── README.md                        ← Ce fichier
├── CHEATSHEET-fastapi.md            ← Référence rapide
│
├── 01-introduction.md               ← Présentation de FastAPI
├── 02-premiers-pas.md               ← Première application
├── 03-routing-parametres.md         ← Routage et paramètres
├── 04-pydantic-validation.md        ← Validation des données
├── 05-bases-de-donnees.md           ← SQLAlchemy + PostgreSQL
├── 06-authentification.md           ← Sécurité et JWT
├── 07-tests.md                      ← Tests automatisés
├── 08-docker-deploiement.md         ← Docker et déploiement
│
└── exercices/
    ├── exercice-01-api-produits.md  ← CRUD Produits + PostgreSQL
    └── exercice-02-auth-jwt.md      ← Ajout authentification JWT
```

---

## Table des matières détaillée

### Module 01 — Introduction à FastAPI
- Qu'est-ce que FastAPI ?
- Comparaison Flask / Django / FastAPI
- ASGI vs WSGI
- Installation et configuration

### Module 02 — Premiers pas
- Votre première application
- Lancer le serveur avec uvicorn
- Le rechargement automatique
- Structure d'un projet FastAPI

### Module 03 — Routing et paramètres
- Paramètres de chemin (path parameters)
- Paramètres de requête (query parameters)
- Corps de la requête (request body)
- Modèles de réponse
- Les méthodes HTTP

### Module 04 — Pydantic et validation
- Les modèles Pydantic
- Validation des champs
- Modèles imbriqués
- Validateurs personnalisés
- Gestion des erreurs de validation

### Module 05 — Bases de données
- SQLAlchemy avec FastAPI
- Sessions asynchrones
- Injection de dépendances pour la DB
- Migrations avec Alembic

### Module 06 — Authentification
- Authentification par clé API
- Tokens JWT avec python-jose
- Flux OAuth2 Password
- Dépendances de sécurité

### Module 07 — Tests
- TestClient de FastAPI
- Fixtures pytest
- Tester les routes
- Mocker les dépendances

### Module 08 — Docker et déploiement
- Dockerfile optimisé
- docker-compose avec PostgreSQL
- Configuration de production
- Health checks

---

## Durée estimée

| Module | Durée théorie | Durée pratique |
|---|---|---|
| 01 — Introduction | 30 min | — |
| 02 — Premiers pas | 45 min | 30 min |
| 03 — Routing | 1h | 45 min |
| 04 — Pydantic | 1h | 45 min |
| 05 — Bases de données | 1h30 | 1h |
| 06 — Authentification | 1h30 | 1h |
| 07 — Tests | 1h | 1h |
| 08 — Docker | 1h | 45 min |
| Exercices | — | 3h |
| **Total** | **~8h** | **~9h** |

---

## Ressources complémentaires

- [Documentation officielle FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Pydantic v2](https://docs.pydantic.dev/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentation Alembic](https://alembic.sqlalchemy.org/)
- [python-jose](https://python-jose.readthedocs.io/)
- [Tutoriel officiel FastAPI (très complet)](https://fastapi.tiangolo.com/tutorial/)

---

## Convention de code

Tout au long de cette formation, nous utilisons les conventions suivantes :

- **PEP 8** pour le style de code Python
- **Type hints** partout (obligatoire avec FastAPI)
- **Nommage snake_case** pour les variables et fonctions
- **Nommage PascalCase** pour les classes Pydantic et SQLAlchemy
- Les exemples de code sont testés et fonctionnels

---

> **Note formateur** : Cette formation est conçue pour être suivie dans l'ordre. Chaque module s'appuie sur le précédent. Les exercices en fin de formation consolident l'ensemble des notions abordées.
