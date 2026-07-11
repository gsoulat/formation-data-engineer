# Introduction au MLOps

## Qu'est-ce que le MLOps ?

Le **MLOps** (Machine Learning Operations) est l'ensemble des pratiques, outils et cultures visant à **fiabiliser et industrialiser le cycle de vie des modèles de Machine Learning** en production.

C'est la convergence de trois disciplines :

```
        Data Science
            ↕
DevOps ←→ MLOps ←→ Data Engineering
```

Sans MLOps, la réalité dans beaucoup d'organisations ressemble à ceci :

> "Le data scientist entraîne un modèle sur son ordinateur portable, l'envoie par email à l'ingénieur, qui passe deux semaines à essayer de le faire tourner en production, puis le modèle dérive silencieusement pendant six mois sans que personne ne s'en aperçoive."

Le MLOps répond à ce problème systématiquement.

---

## Le problème fondamental : ML ≠ Software classique

Le développement logiciel classique souffre de **Technical Debt**. Le ML y ajoute une dette supplémentaire : la **Model Debt** et la **Data Debt**.

### Ce qui rend le ML difficile à industrialiser

| Aspect | Software classique | Machine Learning |
|---|---|---|
| Input | Spécifications fixes | Données qui évoluent |
| Behavior | Déterministe | Probabiliste |
| Testing | Tests unitaires classiques | Difficile à tester rigoureusement |
| Debugging | Stack traces | Métriques, distributions, visuels |
| Versioning | Code uniquement | Code + données + modèle |
| Déploiement | 1 artefact | Modèle + preprocessing + config |
| Monitoring | Uptime, latence | Dérive, qualité des prédictions |

### Les défis spécifiques au ML

**1. Reproductibilité**
```
Modèle entraîné en janvier → résultats différents en juillet
Causes : données changées, version bibliothèque, aléa non seedé
```

**2. Versioning complexe**
```
Version d'un modèle = f(code, données, hyperparamètres, environnement)
```

**3. Dérive silencieuse**
```
Le modèle continue de "fonctionner" (pas d'erreur 500)
mais ses prédictions deviennent de moins en moins pertinentes
```

**4. Collaboration difficile**
```
Data scientist ≠ ingénieur logiciel ≠ ops
Chacun a ses outils, ses pratiques, ses formats
```

---

## Le cycle de vie ML

Un modèle en production passe par plusieurs étapes cycliques :

```
┌─────────────────────────────────────────────────────────────┐
│                    CYCLE DE VIE ML                          │
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │  Données │────▶│ Feature  │────▶│Entraînem.│            │
│  │ brutes   │     │Engineer. │     │          │            │
│  └──────────┘     └──────────┘     └────┬─────┘            │
│                                         │                  │
│  ┌──────────┐     ┌──────────┐     ┌────▼─────┐            │
│  │Monitoring│◀────│Déploiem. │◀────│Évaluation│            │
│  │Production│     │          │     │          │            │
│  └────┬─────┘     └──────────┘     └──────────┘            │
│       │                                                     │
│       └──────────────────────────────────────────────────▶ │
│                    (réentraînement si dérive)               │
└─────────────────────────────────────────────────────────────┘
```

### Détail de chaque étape

**1. Collecte et préparation des données**
- Ingestion depuis sources variées (BDD, API, fichiers)
- Nettoyage, validation de qualité
- Feature engineering
- Split train/validation/test

**2. Expérimentation**
- Sélection d'algorithmes
- Tuning d'hyperparamètres
- Comparaison de modèles
- Tracking des expériences (MLflow)

**3. Évaluation**
- Métriques de performance (RMSE, AUC, F1...)
- Tests de régression (le nouveau modèle est-il meilleur ?)
- Validation sur données out-of-time

**4. Packaging et déploiement**
- Conteneurisation (Docker)
- Exposition via API REST (FastAPI)
- Tests d'intégration

**5. Monitoring en production**
- Performance en temps réel
- Détection de dérive des données
- Alertes automatiques
- Décision de réentraînement

---

## Les niveaux de maturité MLOps

Google a défini un modèle de maturité MLOps en **3 niveaux**. La plupart des entreprises commencent au niveau 0.

---

### Niveau 0 — Manuel (No MLOps)

```
Data Scientist                         Production
    │                                       │
    ├── Explore données (notebook)          │
    ├── Entraîne modèle (notebook)          │
    ├── Évalue modèle (notebook)            │
    ├── Exporte modèle (pickle)             │
    │                    ──── email ────▶   │
    │                                  Ingénieur copie-colle
    │                                  le modèle manuellement
```

**Caractéristiques :**
- Processus entièrement manuel
- Notebooks non versionnés
- Pas de reproductibilité
- Déploiement rare (mois / années)
- Pas de monitoring

**Problèmes typiques :**
- "Le modèle marche sur mon ordi mais pas en prod"
- "Quelle version du modèle est en production ?"
- "Les données d'entraînement ont été écrasées"

---

### Niveau 1 — Pipeline ML automatisé

```
Git (code)  +  DVC (données)
    │
    ▼
Pipeline d'entraînement automatisé
    │
    ▼
MLflow (tracking + registry)
    │
    ▼
Déploiement semi-automatique
    │
    ▼
Monitoring basique
```

**Caractéristiques :**
- Pipeline d'entraînement automatisé
- Versioning des données (DVC)
- Tracking des expériences (MLflow)
- Registre de modèles
- Monitoring de performance

**Gains :**
- Reproductibilité garantie
- Déploiement en jours plutôt qu'en mois
- Historique traçable

---

### Niveau 2 — Pipeline CI/CD complet

```
Push code/données
    │
    ▼
GitHub Actions → Tests → Entraînement → Évaluation
                                            │
                              ┌─────────────┴──────────────┐
                              │ Modèle meilleur ?           │
                         OUI  │                    NON      │
                              ▼                             ▼
                    Déploiement auto              Rejet automatique
                    (Blue/Green ou               + notification
                     Canary)                       équipe
                              │
                              ▼
                    Monitoring + alertes
                    Réentraînement auto si dérive
```

**Caractéristiques :**
- CI/CD complet pour ML
- Tests automatiques (données, modèle, API)
- Déploiement automatique avec validation
- Réentraînement déclenché par monitoring
- Rollback automatique

---

## Comparaison DevOps vs MLOps

| Pratique DevOps | Équivalent MLOps |
|---|---|
| Source control (Git) | Git + DVC |
| Tests unitaires | Tests de données + modèle |
| CI/CD | CI/CD pour ML (GitHub Actions) |
| Artifacts (binaires) | Modèles + transformers |
| Monitoring (uptime/latence) | Monitoring données + performance |
| Rollback de code | Rollback de modèle |
| Feature flags | A/B testing de modèles |

---

## Les composants d'une plateforme MLOps

Une plateforme MLOps complète inclut :

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLATEFORME MLOPS                           │
├─────────────────┬───────────────────┬───────────────────────────┤
│   DONNÉES       │   EXPÉRIMENTATION │   DÉPLOIEMENT             │
│                 │                   │                           │
│ DVC             │ MLflow Tracking   │ Docker                    │
│ Great Expectations│ Notebooks      │ Kubernetes                 │
│ dbt             │ Hyperparameter   │ FastAPI                    │
│ Data validation │ optimization     │ Seldon / BentoML          │
├─────────────────┴───────────────────┴───────────────────────────┤
│                      MONITORING                                 │
│                                                                 │
│ Evidently AI (drift)  │  Prometheus (métriques)                 │
│ Grafana (dashboards)  │  PagerDuty (alertes)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir un navigateur et montrer la page d'accueil de MLflow (`http://localhost:5000`) avec une liste d'expériences et de runs.
> **Expliquer :** "Voici ce à quoi ressemble un système de tracking d'expériences. Chaque ligne est un entraînement de modèle différent, avec ses paramètres et ses métriques. Sans ça, on perd trace de ce qu'on a essayé."

---

## Outils du marché

### Plateformes cloud MLOps
- **AWS SageMaker** : MLOps géré sur AWS
- **Google Vertex AI** : plateforme ML de Google Cloud
- **Azure Machine Learning** : offre Microsoft
- **Databricks MLflow** : MLflow managé + Unity Catalog

### Outils open-source
- **MLflow** : tracking + registry + serving
- **DVC** : versioning données + pipelines
- **Kubeflow** : MLOps sur Kubernetes
- **Airflow** : orchestration de pipelines (aussi utilisé en ML)
- **Prefect / Dagster** : orchestration moderne

### Monitoring spécialisé
- **Evidently AI** : détection de dérive
- **WhyLogs** : profiling de données
- **Arize AI** : monitoring ML managé
- **Fiddler AI** : explicabilité + monitoring

---

## Pourquoi MLOps est une compétence critique

D'après le rapport Gartner 2024 :
- **85%** des projets ML n'arrivent jamais en production
- Le coût moyen d'un modèle "fantôme" (entraîné mais jamais déployé) : **500k€**
- Le délai moyen de mise en production sans MLOps : **6 à 12 mois**
- Avec MLOps mature : **1 à 2 semaines**

Les entreprises qui ont investi dans le MLOps rapportent :
- **4x** plus de modèles déployés par an
- **60%** de réduction du temps d'itération
- **50%** de réduction des incidents en production liés aux modèles

---

## Résumé

| Point clé | À retenir |
|---|---|
| MLOps = DevOps + Data | Pratiques DevOps adaptées aux contraintes du ML |
| 3 niveaux de maturité | Manuel → Pipeline auto → CI/CD complet |
| Versioning triple | Code (Git) + Données (DVC) + Modèle (MLflow) |
| Monitoring essentiel | Un modèle peut "fonctionner" tout en se dégradant |
| Reproductibilité | Même code + mêmes données = mêmes résultats |

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dessiner ou afficher le schéma des 3 niveaux de maturité MLOps sur un tableau blanc ou slide.
> **Expliquer :** "Demandez aux apprenants : 'Selon vous, à quel niveau est votre entreprise actuelle ou une entreprise que vous connaissez ?' Cela ancre le contenu dans le concret."

---

## Pour aller plus loin

- [Google MLOps Whitepaper](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Practitioners Guide to MLOps (Google)](https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf)
- [Hidden Technical Debt in ML Systems (NIPS 2015)](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)
- MLflow documentation : https://mlflow.org/docs/latest/index.html
- DVC documentation : https://dvc.org/doc
