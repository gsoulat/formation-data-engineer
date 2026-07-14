# 🧠 Parcours : Développeur IA

[🏠 Retour à l'accueil](README.md)

Ce parcours vous forme à concevoir, entraîner et déployer des modèles d'intelligence artificielle, du Machine Learning classique jusqu'aux agents LLM en production. Il couvre l'ensemble des compétences du métier de Développeur IA.

---

## 📅 Timeline de Formation (~30 semaines)

### 🟢 Phase 1 : Fondations (Semaines 1-4)
*Objectif : Maîtriser Python, les outils de base et les APIs web.*

- [ ] [Python Avancé](01-Fondamentaux/Python/) — POO, bibliothèque standard, scripts robustes
- [ ] [Python Data Engineering](01-Fondamentaux/Python/06-Data-Engineering/) — NumPy, Pandas, Pydantic, REST APIs
- [ ] [Git & GitHub](01-Fondamentaux/Git/) — Versionnage et collaboration
- [ ] [Docker](02-Containerisation/Docker/) — Conteneurisation des environnements ML
- [ ] [SQL](01-Fondamentaux/SQL/) — Requêtes analytiques pour extraire la donnée
- [ ] [FastAPI](01-Fondamentaux/Python/08-FastAPI/) — APIs REST, authentification, Swagger, tests
- [ ] [Qualité & Tests](01-Fondamentaux/Python/05-Qualite-Tests/) — pytest, coverage, pre-commit
- [ ] [Veille Technologique](01-Fondamentaux/Veille-Technologique/) — Méthode de veille, rapports

> 🎯 **Briefs** :
> - [Git](99-Brief/00-Tronc-Commun/brief-git.md) — Versionnage et bonnes pratiques de commit
> - [GitHub](99-Brief/00-Tronc-Commun/brief-github.md) — Collaboration, Pull Requests, workflow d'équipe
> - [Bash / Zsh](99-Brief/00-Tronc-Commun/brief-bash-zsh.md) — Automatisation shell et scripting
> - [Docker](99-Brief/00-Tronc-Commun/brief-docker.md) — Conteneurisation des environnements ML

---

### 🟡 Phase 2 : Machine Learning (Semaines 5-10)
*Objectif : Comprendre et implémenter les algorithmes fondamentaux du ML.*

- [ ] [Machine Learning](08-Machine-Learning/) — Régression, classification, feature engineering, évaluation
- [ ] [MLflow](08-Machine-Learning/cours/17-mlflow.md) — Experiment tracking, model registry
- [ ] [Data Drift Detection](08-Machine-Learning/cours/18-data-drift.md) — Evidently AI, PSI, KS test
- [ ] [MLOps Pipeline](08-Machine-Learning/MLOps/) — DVC, GitHub Actions ML, Docker ML, monitoring
- [ ] [ORM Python](05-Databases/ORM/Python/) — SQLAlchemy, SQLModel, Alembic

> 🎯 **[Brief — Prédiction de churn & industrialisation MLflow](99-Brief/Dev-IA/ML-Classification/BRIEF_ML_CLASSIFICATION.md)** — classification supervisée end-to-end, MLflow (tracking + registry) et détection de drift.

---

### 🔴 Phase 3 : Services IA Cloud & Intégration (Semaines 11-14)
*Objectif : Identifier, évaluer et intégrer des services IA managés.*

- [ ] [Cloud AI Services](04-Cloud-Platforms/AI-Services/) — Azure AI, AWS Textract/Rekognition/Bedrock, GCP Vision/Document AI
- [ ] [Veille Technologique](01-Fondamentaux/Veille-Technologique/) — Rapport comparatif services IA
- [ ] [API FastAPI + Modèle ML](01-Fondamentaux/Python/08-FastAPI/) — Exposer un modèle scikit-learn
- [ ] [Streamlit](12-Frontend-IA/Streamlit/) — Interface cliente consommant une API modèle
- [ ] [Gradio](12-Frontend-IA/Gradio/) — Interface ML avec composants interactifs

> 🎯 **[Brief — Intégration d'un service IA cloud managé](99-Brief/Dev-IA/Services-IA-Cloud/BRIEF_SERVICES_IA_CLOUD.md)** — service OCR/vision/génération exposé via une API FastAPI + interface Streamlit/Gradio.

---

### 🚀 Phase 4 : Architecture & Gestion de Projet (Semaines 15-17)
*Objectif : Cadrer un projet IA, concevoir une architecture, coordonner une équipe.*

- [ ] [Agile / Scrum](11-Gestion-Projet/Agile-Scrum/) — User Stories, sprints, Kanban
- [ ] [ADR](11-Gestion-Projet/ADR/) — Architecture Decision Records
- [ ] [C4 Architecture](11-Gestion-Projet/C4-Architecture/) — Diagrammes C4, PlantUML, Structurizr
- [ ] [Django](01-Fondamentaux/Python/09-Django/) — Application web, DRF, auth JWT

> 🎯 **[Brief — Cadrage & architecture d'un projet IA](99-Brief/Dev-IA/Architecture-Projet/BRIEF_ARCHITECTURE_PROJET.md)** — diagrammes C4, ADRs et découpage Agile (user stories, sprints).

---

### 🔥 Phase 5 : Deep Learning & LLM (Semaines 18-24)
*Objectif : Maîtriser les réseaux de neurones, les LLM et les agents.*

- [ ] [CNN – Vision](09-Deep-Learning/CNN/) — Convolutions, transfer learning
- [ ] [NLP – Traitement du langage](09-Deep-Learning/NLP/) — BERT, GPT, Transformers
- [ ] [HuggingFace](10-Large-Language-Model/HuggingFace/) — Pipeline, fine-tuning, LoRA, sentence-transformers
- [ ] [Bases de données vectorielles](05-Databases/VectorDB/) — Chroma, Qdrant, FAISS, embeddings
- [ ] [LangChain](10-Large-Language-Model/LangChain/) — LCEL, mémoire, multi-providers
- [ ] [RAG](10-Large-Language-Model/RAG/) — Pipeline RAG, chunking, retrieval, évaluation RAGAS
- [ ] [LangGraph & CrewAI](10-Large-Language-Model/Agents/) — Agents multi-outils, graphes d'état, crews

> 🎯 **[Brief — Assistant conversationnel RAG](99-Brief/Dev-IA/RAG-LLM/BRIEF_RAG_LLM.md)** — chunking, base vectorielle, retrieval, mémoire, évaluation RAGAS.

---

### ⚙️ Phase 6 : Tests, CI/CD & Monitoring (Semaines 25-28)
*Objectif : Industrialiser une application IA en production.*

- [ ] [Tests & CI/CD Applicatif](07-DevOps/01-CI-CD/) — GitHub Actions, mocking LLM, couverture
- [ ] [Monitoring Prometheus/Grafana](07-DevOps/02-Monitoring/) — Instrumentation, dashboards
- [ ] [MLOps Pipeline](08-Machine-Learning/MLOps/) — Drift en production, alertes, réentraînement

> 🎯 **[Brief — Industrialiser une API IA](99-Brief/Dev-IA/MLOps-Monitoring/BRIEF_MLOPS_MONITORING.md)** — CI/CD (GitHub Actions, tests, Docker) + monitoring Prometheus/Grafana + alerting.

---

### 🎯 Phase 7 : Projet Intégrateur (Semaines 29-30+)
*Objectif : Application IA end-to-end de la donnée à la production.*

- [ ] **[Projet Final End-to-End](99-Brief/FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md)** — Data → Modèle → API → UI → CI/CD → Monitoring

> 🎯 **Brief** : [Assistant RAG end-to-end](99-Brief/FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md) — projet intégrateur couvrant toute la chaîne, de la donnée à la production.

---

## 🎯 Objectifs & Livrables

| Objectif | Module | Livrable |
| :--- | :--- | :--- |
| **Pipeline data** | Python + FastAPI + SQL + Docker | Script ETL + API REST + schéma SQL |
| **API REST données** | FastAPI | API paginée avec auth et Swagger |
| **Veille techno** | Veille Technologique | Rapport comparatif + grille de sélection |
| **Services IA cloud** | Cloud AI Services | Script d'intégration + Dockerfile |
| **API modèle ML** | FastAPI + ML | API exposant un RandomForest |
| **Intégration client** | Streamlit / Gradio | Interface consommant l'API |
| **Tests + monitoring ML** | MLOps + Data Drift | pytest + MLflow + rapport Evidently |
| **CI/CD ML** | GitHub Actions | Workflow train → test → Docker Hub |
| **Architecture + coordination** | C4 + ADR + Agile | Diagrammes C4 + ADRs + sprint plan |
| **Composants applicatif IA** | LangChain + Gradio | Chatbot avec mémoire et multi-providers |
| **Tests + livraison continue** | CI/CD + pytest | 60%+ coverage + pipeline déploiement |
| **Monitoring + incidents** | Prometheus + Grafana | Dashboard + post-mortem |

---

## 🏁 Modules complémentaires (selon profil)

- [ ] [Java](01-Fondamentaux/Java/) — Spring Boot, JPA/Hibernate
- [ ] [Rust](01-Fondamentaux/Rust/) — Ownership, Axum, Serde
- [ ] [JavaScript / React](13-Developpement-Web/) — Frontend web
- [ ] [React Native](14-Mobile/React-Native/) — Application mobile
- [ ] [Airflow](06-Data-Engineering/Airflow/) — Orchestration de pipelines
- [ ] [Kafka](06-Data-Engineering/Kafka/) — Streaming temps réel

---

[🏠 Retour à l'accueil](README.md)
