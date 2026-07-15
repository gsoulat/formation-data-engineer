# 🟢 Parcours : Développeur Backend

[🏠 Retour à l'accueil](README.md)

Ce parcours forme des **développeurs backend** capables de livrer une **API propre, testée et déployée en production** — de zéro à un vrai projet employable. On ne survole pas dix sujets : on construit, du début à la fin, des services web solides.

## 📅 Timeline de Formation (4-5 mois)

> **Rythme** : chaque module s'accompagne d'un **brief**. Le fil rouge n'est pas un pipeline de données mais une **application backend** qui grandit jusqu'au projet final.

### 🟢 Phase 1 — Fondations (Mois 1)
*Le terminal, le versioning, le code propre, et Python en objet.*
- [ ] [Bash & Zsh](01-Fondamentaux/Bash-Zsh/)
- [ ] [Git & GitHub](01-Fondamentaux/Git/)
- [ ] [Bonnes Pratiques](01-Fondamentaux/Bonne%20pratique/) — Clean Code & architecture
- [ ] [Python : syntaxe & POO](01-Fondamentaux/Python/)

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Bash & Zsh** | [Automatisation CLI](99-Brief/00-Tronc-Commun/brief-bash-zsh.md) |
| **Git / GitHub** | [Versionnage](99-Brief/00-Tronc-Commun/brief-git.md) · [Collaboration](99-Brief/00-Tronc-Commun/brief-github.md) |
| **Python POO** | [Gestionnaire de bibliothèque (POO)](01-Fondamentaux/Python/briefs/brief-02-gestionnaire-bibliotheque.ipynb) |

### 🟡 Phase 2 — Données & persistance (Mois 2)
*Modéliser et manipuler une vraie base relationnelle depuis le code.*
- [ ] [SQL](01-Fondamentaux/SQL/) — schéma, requêtes, jointures, transactions, index
- [ ] [ORM Python](05-Databases/ORM/) — SQLAlchemy, migrations (Alembic)

### 🔵 Phase 3 — API backend (Mois 3)
*Le cœur du métier : concevoir et exposer une API REST.*
- [ ] [FastAPI](01-Fondamentaux/Python/08-FastAPI/) — routing, Pydantic, dépendances, **auth JWT**, doc auto, tests
- [ ] *(optionnel)* [Django / DRF](01-Fondamentaux/Python/09-Django/) — framework alternatif, ORM intégré

| Module associé | 🎯 Brief |
| :--- | :--- |
| **FastAPI** | API REST complète (CRUD + auth + tests) — voir les [exercices du module](01-Fondamentaux/Python/08-FastAPI/) |

### 🟠 Phase 4 — Qualité (Mois 3-4)
*Un backend sans tests n'est pas livrable.*
- [ ] [Tests & Qualité](01-Fondamentaux/Python/05-Qualite-Tests/) — pytest, fixtures, mocking, coverage, lint, pre-commit

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Tests & Qualité** | [Fiabiliser et tester une base de code](01-Fondamentaux/Python/briefs/brief-03-qualite-code.ipynb) |

### 🔴 Phase 5 — Industrialisation (Mois 4-5)
*Conteneuriser et automatiser la livraison.*
- [ ] [Docker](02-Containerisation/Docker/) — image optimisée, `docker-compose`
- [ ] [CI/CD](07-DevOps/01-CI-CD/) — tests + lint automatisés à chaque push

| Module associé | 🎯 Brief |
| :--- | :--- |
| **Docker** | [Conteneuriser une application](99-Brief/00-Tronc-Commun/brief-docker.md) |

---

## 🎯 Ce que vous saurez faire

| Domaine | Compétence clé | Livrable |
| :--- | :--- | :--- |
| **API** | Concevoir et exposer une API REST documentée | API FastAPI (CRUD + auth) |
| **Persistance** | Modéliser et manipuler une base via un ORM | Schéma + migrations |
| **Qualité** | Tester et fiabiliser le code | Suite pytest (coverage > 80 %) |
| **Versioning** | Gérer branches et PR proprement | Historique Git (Conventional Commits) |
| **Livraison** | Conteneuriser et déployer | `docker-compose` + pipeline CI |

---

## 🎓 Évaluation : le projet final
Vous assemblez tout dans une application backend réelle :
👉 **[Projet Final — API de gestion de stock](99-Brief/FINAL_PROJECT_TEMPLATES/DEV_JUNIOR_APP.md)**
(FastAPI + PostgreSQL/ORM + auth JWT + tests > 80 % + Docker).

---
[🏠 Retour à l'accueil](README.md)
