# 01 — Introduction à Apache Airflow

## Qu'est-ce qu'Apache Airflow ?

Apache Airflow est une plateforme open-source d'**orchestration de workflows**. Créé par Airbnb en 2014 et donné à la fondation Apache en 2016, il est aujourd'hui l'un des outils les plus utilisés dans l'écosystème Data Engineering.

Airflow permet de :
- **Définir** des pipelines de données sous forme de code Python
- **Planifier** leur exécution (cron, intervalles, déclenchement manuel)
- **Surveiller** l'état de chaque tâche via une interface web
- **Rejouer** des exécutions passées en cas d'échec
- **Visualiser** les dépendances entre tâches

> Airflow n'est **pas** un outil de traitement de données. Il ne déplace pas, ne transforme pas les données lui-même. Il **orchestre** des outils qui le font (Spark, dbt, pandas, SQL...).

---

## Le concept fondamental : le DAG

Un **DAG** (Directed Acyclic Graph — Graphe Orienté Acyclique) est la brique de base d'Airflow.

### Définition formelle

Un DAG est un graphe dans lequel :
- Les **nœuds** représentent des **tâches** (tasks)
- Les **arêtes** représentent des **dépendances** entre tâches
- Le graphe est **orienté** (les tâches s'exécutent dans un sens)
- Le graphe est **acyclique** (pas de boucle infinie)

### Représentation visuelle

```
extract_data  ──►  transform_data  ──►  load_to_db
                         │
                         ▼
                   send_notification
```

Dans cet exemple :
- `extract_data` doit terminer avant `transform_data`
- `transform_data` déclenche ensuite `load_to_db` ET `send_notification` en parallèle
- Pas de cycle : aucune tâche ne dépend d'elle-même

### Règle fondamentale des DAGs

```
Un DAG = un pipeline logique
Une Task = une unité de travail atomique
```

---

## Cas d'usage typiques

### 1. Pipeline ETL quotidien

```
Extraction API  →  Nettoyage  →  Chargement Data Warehouse  →  Notification Slack
```

### 2. Pipeline de Machine Learning

```
Extraction données  →  Préparation features  →  Entraînement modèle
                                                        │
                              Évaluation métriques  ←──┘
                                        │
                           Enregistrement MLflow
```

### 3. Pipeline de reporting

```
Agrégation SQL  →  Export CSV  →  Upload S3  →  Email rapport
```

### 4. Orchestration dbt

```
dbt seed  →  dbt run  →  dbt test  →  dbt docs generate
```

---

## Architecture d'Airflow

Airflow est composé de plusieurs composants qui interagissent ensemble.

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    APACHE AIRFLOW                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │  Web Server  │    │  Scheduler   │                   │
│  │  (Flask/     │    │              │                   │
│  │   Gunicorn)  │    │              │                   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                            │
│         └────────┬──────────┘                            │
│                  │                                        │
│         ┌────────▼────────┐                              │
│         │    Metadata DB   │ (PostgreSQL / MySQL)         │
│         │                  │                              │
│         └─────────────────┘                              │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │              Executor                     │           │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │           │
│  │  │ Worker 1│  │ Worker 2│  │ Worker 3│  │           │
│  │  └─────────┘  └─────────┘  └─────────┘  │           │
│  └──────────────────────────────────────────┘           │
│                                                          │
│  ┌──────────────┐                                        │
│  │  DAGs Folder │ (répertoire Python partagé)            │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

### Le Scheduler

C'est le **cerveau** d'Airflow. Il :
- Scanne le dossier `dags/` en permanence (toutes les ~30 secondes)
- Analyse les DAGs et leurs planifications
- Crée des **DAG Runs** selon les schedules définis
- Soumet les tâches prêtes à l'**Executor**
- Gère les dépendances et les états des tâches

### Le Web Server

Interface web (Flask + Gunicorn) qui permet de :
- Visualiser tous les DAGs et leurs états
- Déclencher manuellement des DAG Runs
- Consulter les logs de chaque tâche
- Gérer les Variables et Connexions
- Configurer les alertes

Par défaut : `http://localhost:8080`

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interface web Airflow — page d'accueil (liste des DAGs) avec plusieurs DAGs dans différents états (running, success, failed)
> **Expliquer :** Présenter les colonnes de la vue DAGs : Owner, Schedule, Last Run, Recent Tasks, état global. Montrer comment filtrer par tags et par état.

---

### Le Worker

Un Worker est un processus qui **exécute** les tâches. Selon l'executor configuré :
- **LocalExecutor** : le Scheduler lui-même exécute les tâches (jusqu'à N en parallèle)
- **CeleryExecutor** : des workers Celery distincts récupèrent les tâches depuis une queue (Redis/RabbitMQ)
- **KubernetesExecutor** : chaque tâche est exécutée dans un Pod Kubernetes éphémère

### La Metadata Database

Base de données relationnelle (PostgreSQL recommandé en production) qui stocke :
- Les définitions de DAGs (métadonnées)
- L'historique des DAG Runs et Task Instances
- Les Variables et Connexions
- Les XComs (données échangées entre tâches)
- Les utilisateurs et leurs permissions

> La metadata DB ne contient **pas** vos données métier — seulement les métadonnées Airflow.

### Le Triggerer (Airflow 2.2+)

Composant optionnel pour les **Deferrable Operators**. Au lieu de bloquer un worker en attendant (ex: poll S3 toutes les 30s), le Triggerer gère les I/O asynchrones sans monopoliser un worker.

---

## Cycle de vie d'une tâche

```
                    ┌─────────┐
                    │ no_status│  (task définie mais pas encore planifiée)
                    └────┬────┘
                         │ Scheduler crée le DAG Run
                    ┌────▼────┐
                    │scheduled│
                    └────┬────┘
                         │ Executor prend en charge
                    ┌────▼────┐
                    │ queued  │
                    └────┬────┘
                         │ Worker commence
                    ┌────▼────┐
                    │ running │
                    └────┬────┘
                    ┌────┴──────┐
                    │           │
               ┌────▼───┐  ┌───▼──────┐
               │success │  │  failed  │
               └────────┘  └───┬──────┘
                                │ (si retries configurés)
                           ┌───▼──────┐
                           │up_for_retry│
                           └───┬──────┘
                                │
                           (retente)
```

---

## DAG Run vs Task Instance

| Concept | Définition |
|---|---|
| **DAG** | La définition statique du pipeline (le code Python) |
| **DAG Run** | Une exécution concrète du DAG à une date donnée |
| **Task** | La définition statique d'une tâche dans un DAG |
| **Task Instance** | Une exécution concrète d'une Task dans un DAG Run donné |

Exemple :
- Vous avez un DAG `etl_quotidien` planifié à 06h00 chaque jour
- Chaque matin à 06h00, Airflow crée un **DAG Run** pour ce DAG
- Chaque tâche dans ce DAG Run est une **Task Instance**
- Vous pouvez avoir 365 DAG Runs d'un même DAG sur une année

---

## La notion d'execution_date (logical_date)

> C'est un concept **crucial** et souvent source de confusion.

L'`execution_date` (renommée `logical_date` depuis Airflow 2.2) représente le **début de la période que le DAG traite**, pas le moment où il s'exécute.

Exemple :
```
DAG planifié à interval="@daily"
execution_date = 2024-01-15 00:00:00
→ Ce DAG traite les données du 15 janvier
→ Il s'exécute réellement le 16 janvier à 00:00:00
  (Airflow attend que la période soit terminée)
```

C'est ce qu'on appelle le comportement **"end of interval"** d'Airflow.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La vue "Graph" d'un DAG dans l'interface web, montrant les nœuds (tâches) et les arêtes (dépendances) avec des couleurs par état
> **Expliquer :** Pointer chaque nœud en expliquant que chaque couleur correspond à un état (vert=succès, rouge=échec, jaune=running, gris=skipped). Montrer comment cliquer sur un nœud pour voir les détails de la Task Instance.

---

## Comparaison avec d'autres outils

| Outil | Type | Points forts | Limites |
|---|---|---|---|
| **Airflow** | Orchestrateur de workflows | Flexibilité totale Python, UI riche, vaste écosystème | Complexité, courbe d'apprentissage |
| **Prefect** | Orchestrateur moderne | Plus simple, Cloud natif, meilleure UX | Moins mature, moins de providers |
| **Dagster** | Orchestrateur data-centric | Typage des assets, observabilité | Paradigme différent, plus récent |
| **dbt** | Transformation SQL | Excellent pour les transformations SQL | Uniquement SQL, pas d'orchestration générale |
| **Luigi** | Orchestrateur (Spotify) | Simple, léger | UI limitée, moins populaire |
| **Cron** | Planificateur basique | Natif Linux, zéro config | Pas de dépendances, pas de retry, pas de UI |

---

## Points clés à retenir

1. **Airflow orchestre, il n'exécute pas** — c'est un chef d'orchestre, pas un musicien
2. **Tout est du code Python** — les DAGs sont des fichiers `.py`, versionnables avec Git
3. **Idempotence** — chaque tâche doit pouvoir être rejouée sans effet de bord
4. **L'execution_date** est la date logique de traitement, pas d'exécution réelle
5. **Le Scheduler** est le composant central — s'il tombe, rien ne s'exécute
6. **La Metadata DB** est critique — la perdre = perdre tout l'historique

---

## Pour aller plus loin

- [Architecture Airflow (officiel)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html)
- [DAGs concepts (officiel)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Airflow dans le monde réel — Astronomer Blog](https://www.astronomer.io/blog/)
