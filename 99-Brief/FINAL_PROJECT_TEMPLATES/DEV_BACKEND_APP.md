# Projet Final — Développeur (Backend) Junior
## Sujet : API de gestion de stock pour une PME

> Projet de synthèse de fin de parcours. Vous assemblez tout ce que vous avez appris (Python/POO, SQL, tests, Docker, API) en **une application backend réelle, testée et déployée**.

## 📝 Scénario

**StockPro**, une PME de distribution, gère encore ses stocks dans un tableur partagé : erreurs de saisie, pas d'historique, impossible de savoir en temps réel ce qui reste en rayon. La direction veut une **API de gestion de stock** fiable sur laquelle brancher, plus tard, un site et une app mobile. On vous confie le **backend** : une API REST propre, sécurisée, testée et livrable en production.

## 🎯 Objectifs (ce que le projet prouve)

- Concevoir et exposer une **API REST** structurée (routes, validation, codes HTTP, documentation).
- Persister des données dans une **base relationnelle** via un **ORM** (relations, migrations).
- Sécuriser l'accès (**authentification**).
- Garantir la qualité par des **tests automatisés** et du code propre.
- **Conteneuriser** et **déployer** l'application.

## 🏗️ Architecture attendue

```
Client (Swagger / Postman)
        │  HTTP + JWT
        ▼
   API FastAPI ──────► Validation Pydantic
        │
   ORM SQLAlchemy
        │
   PostgreSQL (produits, stocks, mouvements, utilisateurs)
```

- **API** : FastAPI (routing, dépendances, middleware), documentation auto (Swagger).
- **Modèle métier** : `Produit`, `Mouvement de stock` (entrée/sortie), `Utilisateur`. Le stock courant se déduit de l'historique des mouvements (jamais un champ modifié « à la main »).
- **Base** : PostgreSQL via SQLAlchemy + migrations (Alembic). Relations et clés étrangères correctes, index sur les FK.
- **Sécurité** : authentification par **JWT**, mots de passe hashés (jamais en clair).
- **Industrialisation** : Docker + `docker-compose` (API + PostgreSQL), variables d'environnement, `.env.example`.

> Prérequis couverts par le parcours : [FastAPI](../../01-Fondamentaux/Python/08-FastAPI/), [SQL](../../01-Fondamentaux/SQL/), [Tests & Qualité](../../01-Fondamentaux/Python/05-Qualite-Tests/), [Docker](../../02-Containerisation/Docker/).

## 🧭 Travail demandé (par phases)

**Phase 1 — Cadrage & modèle (J1, sans code d'application).** Modélisez le schéma de données (entités, relations, contraintes). Quelles routes exposez-vous, avec quels verbes HTTP et quels codes de retour ? Écrivez le contrat d'API (endpoints, entrées/sorties) avant de coder.

**Phase 2 — API & persistance (J2-J3).** Implémentez le CRUD produits, la saisie de mouvements de stock (entrée/sortie avec contrôle : pas de sortie qui rend le stock négatif), et le calcul du stock courant. Branchez SQLAlchemy + migrations. Validez toutes les entrées avec Pydantic.

**Phase 3 — Sécurité & robustesse (J4).** Ajoutez l'inscription / connexion et protégez les routes sensibles par JWT. Gérez proprement les erreurs (404, 400, 409, 401) avec des messages clairs.

**Phase 4 — Tests & qualité (J4-J5).** Écrivez des tests automatisés (pytest + TestClient) couvrant les cas nominaux ET les cas d'erreur (stock insuffisant, accès non autorisé, doublon). Visez **> 80 % de couverture**. Passez un linter (ruff/flake8).

**Phase 5 — Conteneurisation & livraison (J5).** Écrivez le `Dockerfile` (multi-stage, user non-root) et le `docker-compose.yml` (API + PostgreSQL). L'application doit démarrer avec **une seule commande**. Rédigez le README. Bonus : un pipeline CI (GitHub Actions : tests + lint) et un déploiement sur un PaaS (Render/Railway).

## 📦 Livrables

- **Dépôt GitHub public** avec historique propre (Conventional Commits).
- **API fonctionnelle** documentée (Swagger accessible).
- **`docker-compose.yml`** lançant toute la stack en une commande.
- **Suite de tests** pytest (**couverture > 80 %**).
- **README** : description, stack, installation/lancement, schéma de données, exemples de requêtes, auteur.

## ✅ Critères de validation

- [ ] L'API expose un CRUD produits + mouvements de stock cohérent (stock jamais négatif).
- [ ] Les données persistent dans PostgreSQL via un ORM, avec migrations.
- [ ] Les routes sensibles sont protégées par authentification (JWT), mots de passe hashés.
- [ ] Toutes les entrées sont validées ; les erreurs renvoient le bon code HTTP.
- [ ] Tests automatisés (nominaux + erreurs), couverture > 80 %, linter au vert.
- [ ] `docker-compose up` lance l'application complète sans étape manuelle.
- [ ] README clair permettant à un tiers de lancer le projet en < 5 minutes.
- [ ] Historique Git propre (Conventional Commits).

## 🔗 Bonus (pour aller vers l'expertise)

- Pagination, filtres et tri sur la liste des produits.
- Alerte « seuil de réapprovisionnement » (stock < seuil).
- Pipeline CI/CD (GitHub Actions) + déploiement en ligne avec une URL publique.
- Export CSV de l'état des stocks / journal des mouvements.
