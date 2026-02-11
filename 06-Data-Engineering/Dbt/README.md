# Formation DBT – Cloud et Core

Ce cours vous guidera à travers l'utilisation de **dbt Cloud** et **dbt Core** pour transformer et analyser des données. Vous apprendrez à construire un pipeline de données robuste en utilisant les bonnes pratiques de l'ingénierie des données, d'abord avec dbt Cloud connecté à Snowflake (chapitres 0-8), puis avec dbt Core en local (chapitre 9).

## 🎯 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :
- Configurer un projet DBT Cloud connecté à Snowflake
- Créer des modèles de transformation de données
- Implémenter différents types de matérialisations
- Gérer les dépendances et la lignée des données
- Mettre en place des tests de qualité
- Développer des modèles incrémentaux
- Utiliser des variables pour paramétrer les modèles
- Installer et configurer dbt Core en local
- Orchestrer dbt sans dbt Cloud (Airflow, GitHub Actions, Makefile)

## 📊 Le jeu de données Airbnb

### Source
Le jeu de données provient de [Inside Airbnb](https://insideairbnb.com/get-the-data/) pour la ville d'Amsterdam, extrait du 11 Mars 2024.

### Structure des données
1. **listings** : Informations sur les logements Airbnb
2. **hosts** : Données sur les hôtes
3. **reviews** : Dates des commentaires par listing

## 📚 Contenu du cours

### [Chapitre 0 : Guide des commandes DBT](docs/chapitre-0-commandes-dbt.md)
- Commandes essentielles de développement
- Workflows typiques et bonnes pratiques
- Sélecteurs avancés et optimisations

### [Chapitre 1 : Configuration de l'environnement](docs/chapitre-1-environnement.md)
- Configuration de Snowflake
- Chargement des données
- Préparation de DBT Cloud

### [Chapitre 2 : Initialisation du projet DBT Cloud](docs/chapitre-2-initialisation.md)
- Création du projet
- Configuration de la connexion Snowflake
- Structure du projet

### [Chapitre 3 : Premiers modèles](docs/chapitre-3-premiers-modeles.md)
- Création des modèles de curation
- Transformation des données hosts et listings
- Bonnes pratiques SQL

### [Chapitre 4 : Matérialisations](docs/chapitre-4-materialisations.md)
- Types de matérialisations (view, table, incremental)
- Configuration des schémas
- Optimisation des performances

### [Chapitre 5 : Lignée et dépendances](docs/chapitre-5-lineage.md)
- Définition des sources
- Gestion des seeds
- Snapshots et historisation

### [Chapitre 6 : Tests de qualité](docs/chapitre-6-tests.md)
- Tests de sources
- Tests de modèles
- Tests unitaires
- Packages DBT Utils

### [Chapitre 7 : Modèles incrémentaux](07-incremental.md)
- Configuration incremental
- Gestion des mises à jour
- Optimisation des performances

### [Chapitre 8 : Variables DBT](08-variables.md)
- Variables de projet, de ligne de commande et de profil
- Filtres dynamiques et configuration par environnement
- Macros de validation et variables avancées

### [Chapitre 9 : dbt Core – Installation et Utilisation en Local](09-dbt-core.md)
- dbt Cloud vs dbt Core : comparaison détaillée
- Installation et configuration de `profiles.yml`
- Workflow de développement local complet
- Exemple complet avec PostgreSQL (Docker)
- Orchestration sans dbt Cloud (Airflow, GitHub Actions, Makefile)

### [Chapitre 12 : Jinja et Macros dans dbt](12-jinja-macros.md)
- Moteur de templating Jinja2 : expressions, instructions, commentaires
- Filtres, tests et structures de contrôle (if, for, set)
- Création de macros réutilisables (safe_divide, pivot, SCD Type 2)
- Macros dynamiques avec `run_query()` et `dispatch()`
- Organisation, documentation et bonnes pratiques
- Packages de la communauté (dbt_utils, codegen, expectations)

### [Exercices dbt](10-exercices.md)
- Exercice 1 : Modélisation staging et marts
- Exercice 2 : Tests et documentation
- Exercice 3 : Modèle incrémental
- Exercice 4 : Macros et packages
- Exercice 5 : Pipeline dbt Core complet

### [Brief : Pipeline dbt pour l'Analyse des Ventes](11-brief.md)
- Projet complet avec dbt Core + PostgreSQL
- Architecture staging → intermediate → mart
- Tests de qualité, documentation, snapshot SCD Type 2
- Livrables : Makefile, docker-compose, README, Git

## 🚀 Prérequis

- Accès à Snowflake (chapitres 0-8)
- Compte DBT Cloud (chapitres 0-8)
- Python 3.9+ et Docker (chapitre 9, exercices, brief)
- Connaissance de base en SQL
- Familiarité avec les concepts de data warehousing

## 🛠️ Architecture cible

```
RAW (Sources) → CURATION (Nettoyage) → ANALYTICS (Agrégations)
```

## 📁 Structure du projet

```
dbt-cloud-airbnb/
├── models/
│   ├── sources/
│   ├── curation/
│   └── analytics/
├── seeds/
├── snapshots/
├── tests/
├── macros/
└── docs/
```

---