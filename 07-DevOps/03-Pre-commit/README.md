# Formation Pre-commit - Qualite du code avant le commit

Bienvenue dans le cours sur les outils de pre-commit : verifiez et corrigez automatiquement votre code avant chaque commit.

## Vue d'ensemble

Ce cours couvre les outils et pratiques pour mettre en place des verifications automatiques avant chaque commit Git, garantissant la qualite et la securite du code.

## Objectifs d'apprentissage

A la fin de ce cours, vous serez capable de :

- Comprendre le fonctionnement des hooks Git
- Configurer le framework pre-commit sur un projet
- Choisir et combiner les hooks adaptes a votre stack
- Creer des hooks personnalises
- Integrer les verifications pre-commit dans un pipeline CI/CD
- Utiliser prek comme alternative performante

## Structure du cours

### [01 - Introduction](./cours/01-introduction.md)
- Le probleme du code "sale" qui arrive en CI
- Les hooks Git natifs : fonctionnement et limites
- L'ecosysteme des outils (pre-commit, prek)
- Exercices decouverte

### [02 - Le Framework pre-commit](./cours/02-pre-commit-framework.md)
- Installation et configuration
- Le fichier `.pre-commit-config.yaml`
- Les hooks essentiels (ruff, gitleaks, conventional commits)
- Configuration complete recommandee
- Utilisation quotidienne

### [03 - Pre-commit Avance](./cours/03-pre-commit-avance.md)
- Creer des hooks personnalises (locaux et partages)
- Integration CI/CD (GitHub Actions, GitLab CI, Azure DevOps)
- Configuration avancee et optimisation des performances
- Bonnes pratiques et strategie de deploiement en equipe

### [04 - Prek](./cours/04-prek.md)
- Presentation et positionnement
- Installation et configuration (YAML et TOML)
- Benchmarks de performance
- Comparaison detaillee pre-commit vs prek
- Guide de migration

## Prerequis

- **Git** : Commandes de base (commit, push, branch)
- **Terminal** : Etre a l'aise avec la ligne de commande
- **Python** : Installation de base (pour le framework pre-commit)

## Parcours recommande

### Debutant (1 jour)
1. 01-Introduction
2. 02-Pre-commit Framework (installation + hooks de base)

### Intermediaire (2 jours)
1. Parcours Debutant
2. 02-Pre-commit Framework (configuration complete)
3. 03-Pre-commit Avance (hooks custom + CI)

### Avance (3 jours)
1. Parcours Intermediaire
2. 04-Prek (alternative Rust)
3. Mise en place complete sur un projet reel

---

**Bonne formation !**
