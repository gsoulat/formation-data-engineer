# 🧠 Parcours : Développeur IA

[🏠 Retour à l'accueil](README.md)

Ce parcours vous forme à concevoir, entraîner et déployer des modèles d'intelligence artificielle, du Machine Learning classique jusqu'aux agents LLM en production. Il couvre l'intégralité des compétences C1-C21 du référentiel RNCP Dev IA.

---

## 📅 Timeline de Formation (~30 semaines)

### 🟢 Phase 1 : Fondations (Semaines 1-4)
*Objectif : Maîtriser Python, les outils de base et les APIs web.*

- [ ] [Python Avancé](01-Fondamentaux/Python/) — POO, bibliothèque standard, scripts robustes
- [ ] [Python Data Engineering](01-Fondamentaux/Python/06-Data-Engineering/) — NumPy, Pandas, Pydantic, REST APIs
- [ ] [Git & GitHub](01-Fondamentaux/Git/) — Versionnage et collaboration
- [ ] [Docker](02-Containerisation/Docker/) — Conteneurisation des environnements ML
- [ ] [SQL](01-Fondamentaux/SQL/) — Requêtes analytiques pour extraire la donnée
- [ ] [FastAPI](01-Fondamentaux/Python/08-FastAPI/) — APIs REST, authentification, Swagger, tests **(C5, C9)**
- [ ] [Qualité & Tests](01-Fondamentaux/Python/05-Qualite-Tests/) — pytest, coverage, pre-commit
- [ ] [Veille Technologique](01-Fondamentaux/Veille-Technologique/) — Méthode de veille, rapports **(C6)**

---

### 🟡 Phase 2 : Machine Learning (Semaines 5-10)
*Objectif : Comprendre et implémenter les algorithmes fondamentaux du ML.*

- [ ] [Machine Learning](08-Machine-Learning/) — Régression, classification, feature engineering, évaluation **(C11, C12)**
- [ ] [MLflow](08-Machine-Learning/cours/17-mlflow.md) — Experiment tracking, model registry **(C11)**
- [ ] [Data Drift Detection](08-Machine-Learning/cours/18-data-drift.md) — Evidently AI, PSI, KS test **(C11)**
- [ ] [MLOps Pipeline](08-Machine-Learning/MLOps/) — DVC, GitHub Actions ML, Docker ML, monitoring **(C12, C13)**
- [ ] [ORM Python](05-Databases/ORM/Python/) — SQLAlchemy, SQLModel, Alembic **(C4)**

---

### 🔴 Phase 3 : Services IA Cloud & Intégration (Semaines 11-14)
*Objectif : Identifier, évaluer et intégrer des services IA managés.*

- [ ] [Cloud AI Services](04-Cloud-Platforms/AI-Services/) — Azure AI, AWS Textract/Rekognition/Bedrock, GCP Vision/Document AI **(C7, C8)**
- [ ] [Veille Technologique](01-Fondamentaux/Veille-Technologique/) — Rapport comparatif services IA **(C6)**
- [ ] [API FastAPI + Modèle ML](01-Fondamentaux/Python/08-FastAPI/) — Exposer un modèle scikit-learn **(C9)**
- [ ] [Streamlit](12-Frontend-IA/Streamlit/) — Interface cliente consommant une API modèle **(C10)**
- [ ] [Gradio](12-Frontend-IA/Gradio/) — Interface ML avec composants interactifs **(C10, C17)**

---

### 🚀 Phase 4 : Architecture & Gestion de Projet (Semaines 15-17)
*Objectif : Cadrer un projet IA, concevoir une architecture, coordonner une équipe.*

- [ ] [Agile / Scrum](11-Gestion-Projet/Agile-Scrum/) — User Stories, sprints, Kanban **(C16)**
- [ ] [ADR](11-Gestion-Projet/ADR/) — Architecture Decision Records **(C15)**
- [ ] [C4 Architecture](11-Gestion-Projet/C4-Architecture/) — Diagrammes C4, PlantUML, Structurizr **(C14, C15)**
- [ ] [Django](01-Fondamentaux/Python/09-Django/) — Application web, DRF, auth JWT **(C17)**

---

### 🔥 Phase 5 : Deep Learning & LLM (Semaines 18-24)
*Objectif : Maîtriser les réseaux de neurones, les LLM et les agents.*

- [ ] [CNN – Vision](09-Deep-Learning/CNN/) — Convolutions, transfer learning
- [ ] [NLP – Traitement du langage](09-Deep-Learning/NLP/) — BERT, GPT, Transformers
- [ ] [HuggingFace](10-Large-Language-Model/HuggingFace/) — Pipeline, fine-tuning, LoRA, sentence-transformers **(C17)**
- [ ] [Bases de données vectorielles](05-Databases/VectorDB/) — Chroma, Qdrant, FAISS, embeddings **(C17)**
- [ ] [LangChain](10-Large-Language-Model/LangChain/) — LCEL, mémoire, multi-providers **(C17)**
- [ ] [RAG](10-Large-Language-Model/RAG/) — Pipeline RAG, chunking, retrieval, évaluation RAGAS **(C17)**
- [ ] [LangGraph & CrewAI](10-Large-Language-Model/Agents/) — Agents multi-outils, graphes d'état, crews **(C17)**

---

### ⚙️ Phase 6 : Tests, CI/CD & Monitoring (Semaines 25-28)
*Objectif : Industrialiser une application IA en production.*

- [ ] [Tests & CI/CD Applicatif](07-DevOps/01-CI-CD/) — GitHub Actions, mocking LLM, couverture **(C18, C19)**
- [ ] [Monitoring Prometheus/Grafana](07-DevOps/02-Monitoring/) — Instrumentation, dashboards **(C20)**
- [ ] [MLOps Pipeline](08-Machine-Learning/MLOps/) — Drift en production, alertes, réentraînement **(C20, C21)**

---

### 🎯 Phase 7 : Projet Intégrateur (Semaines 29-30+)
*Objectif : Application IA end-to-end de la donnée à la production.*

- [ ] **[Projet Final End-to-End](99-Brief/FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md)** — Data → Modèle → API → UI → CI/CD → Monitoring

---

## 🎯 Passeport de Compétences

| Compétence | Module | Livrable |
| :--- | :--- | :--- |
| **C1-C4** Pipeline data | Python + FastAPI + SQL + Docker | Script ETL + API REST + schéma SQL |
| **C5** API REST données | FastAPI | API paginée avec auth et Swagger |
| **C6** Veille techno | Veille Technologique | Rapport comparatif + grille de sélection |
| **C7-C8** Services IA cloud | Cloud AI Services | Script d'intégration + Dockerfile |
| **C9** API modèle ML | FastAPI + ML | API exposant un RandomForest |
| **C10** Intégration client | Streamlit / Gradio | Interface consommant l'API |
| **C11-C12** Tests + monitoring ML | MLOps + Data Drift | pytest + MLflow + rapport Evidently |
| **C13** CI/CD ML | GitHub Actions | Workflow train → test → Docker Hub |
| **C14-C16** Architecture + coordination | C4 + ADR + Agile | Diagrammes C4 + ADRs + sprint plan |
| **C17** Composants applicatif IA | LangChain + Gradio | Chatbot avec mémoire et multi-providers |
| **C18-C19** Tests + livraison continue | CI/CD + pytest | 60%+ coverage + pipeline déploiement |
| **C20-C21** Monitoring + incidents | Prometheus + Grafana | Dashboard + post-mortem |

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
