# MLOps — De l'expérimentation à la production

## Objectifs pédagogiques

Ce module couvre l'ensemble des pratiques et outils permettant de **industrialiser les modèles de Machine Learning** : de l'expérimentation reproductible jusqu'au déploiement en production avec monitoring continu.

À l'issue de ce module, vous serez capables de :
- Comprendre le cycle de vie complet d'un modèle ML en production
- Versionner expériences, données et modèles avec MLflow et DVC
- Conteneuriser et déployer des modèles avec Docker et FastAPI
- Automatiser les pipelines ML avec GitHub Actions
- Détecter la dérive des données et monitorer les modèles en production

---

## Structure du module

```
MLOps/
├── Concepts/
│   └── 01-introduction-mlops.md        ← Fondamentaux MLOps, cycle de vie, maturité
├── MLflow/
│   ├── 01-tracking.md                  ← Suivi d'expériences, métriques, artefacts
│   ├── 02-model-registry.md            ← Registre de modèles, staging/production
│   └── 03-serving.md                   ← Servir un modèle via REST API
├── DVC/
│   ├── 01-introduction.md              ← Versioning de données, remote storage
│   └── 02-pipelines.md                 ← Pipelines reproductibles avec dvc.yaml
├── GitHub-Actions-ML/
│   ├── 01-workflow-entrainement.md     ← CI pour l'entraînement automatisé
│   └── 02-workflow-deploiement.md      ← CD pour le déploiement en production
├── Docker-ML/
│   ├── 01-containeriser-modele.md      ← Dockerfile ML + FastAPI
│   └── 02-docker-compose-stack.md      ← Stack complète multi-services
├── Monitoring-Modele/
│   ├── 01-drift-detection.md           ← Data drift, concept drift, Evidently
│   └── 02-metriques-production.md      ← Prometheus + Grafana pour ML
└── exercices/
    ├── exercice-01-pipeline-complet.md ← Pipeline end-to-end
    └── exercice-02-monitoring.md       ← Monitoring d'un modèle en production
```

---

## Prérequis

- Python 3.10+
- Notions de Machine Learning (entraînement, évaluation, métriques)
- Docker installé et fonctionnel
- Compte GitHub
- Modules précédents : cours ML de base, Docker

---

## Stack technologique

| Outil | Rôle |
|---|---|
| **MLflow** | Tracking d'expériences, registre de modèles, serving |
| **DVC** | Versioning de données et pipelines reproductibles |
| **GitHub Actions** | CI/CD pour les pipelines ML |
| **Docker** | Conteneurisation des modèles |
| **FastAPI** | API REST pour servir les prédictions |
| **Evidently AI** | Détection de dérive des données |
| **Prometheus** | Collecte de métriques production |
| **Grafana** | Tableaux de bord de monitoring |

---

## Durée estimée

| Section | Durée |
|---|---|
| Concepts MLOps | 1h |
| MLflow (tracking + registry + serving) | 3h |
| DVC | 2h |
| GitHub Actions ML | 2h |
| Docker ML | 2h |
| Monitoring | 2h |
| Exercices | 3h |
| **Total** | **~15h** |

---

## Installation de l'environnement

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Installer toutes les dépendances du module
pip install mlflow dvc scikit-learn pandas numpy fastapi uvicorn
pip install evidently prometheus-client docker
pip install pytest great-expectations
```

Ou avec un fichier `requirements.txt` complet :

```text
mlflow==2.14.0
dvc==3.50.0
dvc-s3==3.2.0
scikit-learn==1.5.0
pandas==2.2.0
numpy==1.26.0
fastapi==0.111.0
uvicorn==0.30.0
evidently==0.4.30
prometheus-client==0.20.0
httpx==0.27.0
pytest==8.2.0
```

---

## Fil rouge pédagogique

Tout au long du module, nous travaillons avec le même projet : **un modèle de prédiction du prix de l'immobilier**. Ce fil rouge permet de voir comment les outils s'intègrent les uns aux autres dans un vrai pipeline de production.

```
Données brutes → DVC → Entraînement → MLflow → Docker → GitHub Actions → Production
                                                                              ↓
                                                                         Monitoring
```
