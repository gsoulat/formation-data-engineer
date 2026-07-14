# 🗺️ Carte de la pratique — tous les projets, briefs, ateliers et notebooks

Ce dépôt organise la pratique **par fonction pédagogique**, pas par type de fichier. Trois familles :

| Famille | Rôle | Où elle vit |
|---|---|---|
| **Brief / projet** | mission scénarisée, évaluable, montrable en portfolio | **`99-Brief/`** (ci-dessous) |
| **Atelier / mini-brief** | pratique **guidée couplée à un chapitre** | **dans le module de cours** |
| **Exercice** | drill « applique tout de suite » après la leçon | **dans le module de cours** (`<module>/exercices/`) |
| **Notebook** | cours ou atelier **exécutable** (`.ipynb`) | **dans le module de cours** |

> Les exercices ne sont pas listés un par un : **chaque module de cours a son dossier
> [`exercices/`](../)**. Cette carte recense les **projets** et la **pratique couplée** (ateliers, notebooks) qui, sinon, seraient difficiles à trouver.

---

## 📊 Data Analyst
Parcours détaillé semaine par semaine : **[PATH_DATA_ANALYST](../PATH_DATA_ANALYST.md)**

- **Briefs hebdomadaires (22)** → [`Data-Analyst/briefs-hebdo/`](Data-Analyst/briefs-hebdo/) · index : [README](Data-Analyst/README.md)
- **Projets capstone (4)** → [BRIEF 0](Data-Analyst/BRIEF_0_PRAIRIE.md) · [BRIEF 1](Data-Analyst/BRIEF_1_TABLEAU_DE_BORD_METIER.md) · [BRIEF 2](Data-Analyst/BRIEF_2_SOLUTION_BI_AVANCEE.md) · [BRIEF 3 — Projet final](Data-Analyst/BRIEF_3_PROJET_FINAL.md)
- **Notebooks exécutables (complément cours)** :
  - [EDA pandas](../15-Business-Intelligence/04-Analyse-Exploratoire-EDA/) · [Stats descriptives](../01-Fondamentaux/Mathematiques/03-Statistiques-Descriptives/) · [Stats inférentielle](../01-Fondamentaux/Mathematiques/05-Statistique-Inferentielle/) · [SQL d'analyse](../01-Fondamentaux/SQL/09-Extraction-Analyse/)
- **Données** : [`Data-Analyst/data/`](Data-Analyst/data/) (univers NordRetail)

## 🔧 Data Engineer
Parcours : **[PATH_DATA_ENGINEER](../PATH_DATA_ENGINEER.md)**

- **Briefs métier** → [`Data-Engineer/`](Data-Engineer/) : Clean Code, POO, Terraform+CI/CD, PostgreSQL, API+Scraping, Data Lake, BigQuery, Snowflake+dbt, Éolienne (Fabric), ECO2-RTE, Maintenance DWH, Gouvernance, Kafka, Qualité de l'eau, Pipeline NYC.
- **Capstone couplé au cours** → [Data Warehouse & Data Marts BigQuery](../05-Databases/DataWarehouse/brief/Brief.md) (module DataWarehouse)
- **Projet final** → [Pipeline ETL E-Commerce](FINAL_PROJECT_TEMPLATES/DATA_ENGINEER_ETL.md)

## 🧠 Dev IA
Parcours : **[PATH_DEV_IA](../PATH_DEV_IA.md)**

- **Briefs** → [`Dev-IA/`](Dev-IA/) : ML/MLflow, Services IA cloud, Architecture (C4/ADR/Agile), RAG, MLOps/Monitoring.
- **Mini-briefs ML mono-modèle (10)** → [`08-Machine-Learning/mini-briefs/`](../08-Machine-Learning/mini-briefs/) — KNN, régressions, arbre, forêt, XGBoost, SVM, KMeans, PCA, Naive Bayes (+ versions **notebook** `mini-briefs/notebooks/`).
- **Capstone couplé au cours** → [Scoring de churn client (fil rouge ML)](../08-Machine-Learning/briefs/brief-churn-scoring.md)
- **Notebooks ML** → [`08-Machine-Learning/notebooks/`](../08-Machine-Learning/notebooks/)
- **Projet final** → [Assistant RAG end-to-end](FINAL_PROJECT_TEMPLATES/DEV_IA_ASSISTANT_RAG.md)

## 🧩 Tronc commun
- **Briefs outillage** → [`00-Tronc-Commun/`](00-Tronc-Commun/) : Bash/Zsh, Git, GitHub, Docker, Kubernetes.

---

> **Note d'organisation** : les capstones « couplés au cours » (churn ML, DWH BigQuery, briefs Python en notebook) restent **dans leur module** à dessein — ils sont l'aboutissement de ce cours précis. Cette carte les rend simplement **trouvables** depuis un point unique, sans casser la logique « on pratique là où on apprend ».
