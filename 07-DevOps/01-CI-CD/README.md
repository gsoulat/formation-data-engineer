# Formation CI/CD - Intégration et Déploiement Continus

Bienvenue dans le cours complet sur le CI/CD (Continuous Integration / Continuous Deployment).

## Vue d'ensemble

Ce cours couvre l'ensemble des pratiques, outils et stratégies pour mettre en place des pipelines CI/CD efficaces et fiables.

## Objectifs d'apprentissage

À la fin de ce cours, vous serez capable de :

- Comprendre les principes fondamentaux du CI/CD
- Mettre en place des workflows Git efficaces
- Configurer des pipelines CI/CD sur différentes plateformes
- Implémenter des tests automatisés
- Déployer des applications de manière automatisée et sécurisée
- Appliquer les bonnes pratiques DevOps

## Structure du cours

### [01-Introduction](./01-Introduction/README.md)
- Qu'est-ce que le CI/CD ?
- Pourquoi utiliser le CI/CD ?
- Concepts et terminologie
- Architecture des pipelines
- Outils populaires

### [02-Git-Workflows](./02-Git-Workflows/README.md)
- Git Flow
- GitHub Flow
- GitLab Flow
- Trunk-Based Development
- Pull Requests et Code Review
- Conventions de nommage

### [03-GitHub-Actions](./03-GitHub-Actions/README.md)
- Introduction à GitHub Actions
- Syntaxe et structure des workflows
- Workflows de base et avancés
- Secrets et variables
- Actions réutilisables
- Exemples pratiques complets

**Fichiers d'exemple :**
- [ci-basic.yml](./03-GitHub-Actions/ci-basic.yml) - Pipeline CI basique
- [docker-build.yml](./03-GitHub-Actions/docker-build.yml) - Build et push Docker
- [terraform-deploy.yml](./03-GitHub-Actions/terraform-deploy.yml) - Déploiement Terraform

### [04-GitLab-CI](./04-GitLab-CI/README.md)
- Introduction à GitLab CI/CD
- Syntaxe .gitlab-ci.yml
- Pipelines et jobs
- GitLab Runners
- Exemples pratiques

**Fichiers d'exemple :**
- [.gitlab-ci.yml](./04-GitLab-CI/.gitlab-ci.yml) - Pipeline GitLab complet

### [05-Azure-DevOps](./05-Azure-DevOps/README.md)
- Introduction à Azure DevOps
- Azure Pipelines
- Syntaxe YAML
- Déploiement vers Azure
- Intégration avec les services Azure

**Fichiers d'exemple :**
- [azure-pipelines.yml](./05-Azure-DevOps/azure-pipelines.yml) - Pipeline Azure complet

> 🔧 **Jenkins** n'a pas de module dédié ici — il est traité en comparaison dans le tableau plus bas. Un lab Jenkins dédié fait partie des ajouts prévus.

### Bonnes pratiques CI/CD *(module dédié à venir)*
Les principes clés — sécurité (scan d'images, gestion des secrets), tests & qualité, stratégies de déploiement, monitoring — sont pour l'instant intégrés dans les modules **03-GitHub-Actions** et **04-GitLab-CI** ci-dessus (voir leurs workflows avec Trivy, Snyk, environnements et approbations).

---

## Parcours recommandé

### Débutant (2-3 jours)
1. 01-Introduction
2. 02-Git-Workflows (GitHub Flow uniquement)
3. 03-GitHub-Actions (workflows de base)

### Intermédiaire (1 semaine)
1. Parcours Débutant
2. 02-Git-Workflows (tous les workflows)
3. 03-GitHub-Actions (workflows avancés)
4. 04-GitLab-CI ou 05-Azure-DevOps (selon votre stack)

### Avancé (2 semaines)
1. Parcours Intermédiaire
2. Implémenter un pipeline complet de A à Z (multi-environnements, scan de sécurité, déploiement sur approbation)
3. Projet pratique : CI/CD pour une application complète

---

## Prérequis

### Connaissances

- **Git** : Commandes de base (clone, commit, push, pull, branch, merge)
- **CLI** : Utilisation du terminal/shell
- **Développement** : Au moins un langage de programmation (Node.js, Python, Java, etc.)
- **Docker** : Concepts de base (recommandé)
- **Cloud** : Notions de base AWS/Azure/GCP (optionnel)

### Outils à installer

```bash
# Git
git --version

# Docker (recommandé)
docker --version

# Un éditeur de code
code --version  # VS Code
```

### Comptes nécessaires

- Compte GitHub (gratuit) - **Obligatoire**
- Compte GitLab (gratuit) - Optionnel
- Compte Azure (essai gratuit) - Optionnel

---

## Exercices pratiques

Chaque section contient des exercices pratiques. Voici quelques projets complets suggérés :

### Projet 1 : Application Node.js simple
- Créer un pipeline CI/CD complet
- Tests unitaires et d'intégration
- Build Docker
- Déploiement automatique

### Projet 2 : API REST avec base de données
- Pipeline multi-stages
- Tests avec base de données
- Gestion des secrets
- Déploiement blue/green

### Projet 3 : Infrastructure as Code
- Pipeline Terraform
- Validation et plan automatiques
- Déploiement sur cloud provider
- Tests post-déploiement

---

## Comparaison des outils

| Critère | GitHub Actions | GitLab CI | Jenkins | Azure DevOps |
|---------|---------------|-----------|---------|--------------|
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Interface** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Flexibilité** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Prix** | Gratuit* | Gratuit* | Gratuit | Gratuit* |
| **Cloud** | ✅ | ✅ | ❌ | ✅ |
| **Self-hosted** | ✅ | ✅ | ✅ | ✅ |
| **Marketplace** | 13000+ | 1000+ | 1800+ | 1000+ |

*avec limitations pour repos privés

### Quand utiliser quoi ?

**GitHub Actions**
- Projet hébergé sur GitHub
- Équipe petite/moyenne
- Besoin de simplicité

**GitLab CI**
- Projet hébergé sur GitLab
- Besoin d'une solution complète DevOps
- Auto-hébergement souhaité

**Jenkins**
- Besoin de flexibilité maximale
- Infrastructure existante complexe
- Grande entreprise avec besoins spécifiques

**Azure DevOps**
- Écosystème Microsoft/.NET
- Intégration Azure
- Grandes équipes entreprise

---

## Ressources supplémentaires

### Livres
- **"Continuous Delivery"** - Jez Humble & David Farley
- **"The DevOps Handbook"** - Gene Kim et al.
- **"Accelerate"** - Nicole Forsgren et al.
- **"The Phoenix Project"** - Gene Kim et al.

### Documentation officielle
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Azure Pipelines Docs](https://docs.microsoft.com/en-us/azure/devops/pipelines/)

### Communautés
- [DevOps subreddit](https://reddit.com/r/devops)
- [CNCF Slack](https://cloud-native.slack.com)
- [DevOps Discord](https://discord.gg/devops)

### Blogs et sites
- [Martin Fowler - CI](https://martinfowler.com/articles/continuousIntegration.html)
- [DevOps.com](https://devops.com)
- [The New Stack](https://thenewstack.io)

---

## Métriques de succès

Mesurez votre progression CI/CD avec ces métriques (DORA) :

1. **Deployment Frequency** (Fréquence de déploiement)
   - Élite : Plusieurs fois par jour
   - Haute : Entre une fois par jour et une fois par semaine
   - Moyenne : Entre une fois par semaine et une fois par mois
   - Faible : Moins d'une fois par mois

2. **Lead Time for Changes** (Délai pour les changements)
   - Élite : Moins d'une heure
   - Haute : Entre un jour et une semaine
   - Moyenne : Entre une semaine et un mois
   - Faible : Plus d'un mois

3. **Time to Restore Service** (Temps de restauration)
   - Élite : Moins d'une heure
   - Haute : Moins d'un jour
   - Moyenne : Entre un jour et une semaine
   - Faible : Plus d'une semaine

4. **Change Failure Rate** (Taux d'échec)
   - Élite : 0-15%
   - Haute : 16-30%
   - Moyenne : 31-45%
   - Faible : Plus de 45%

---

## Certification et évaluation

À la fin de ce cours, vous devriez être capable de :

- [ ] Expliquer les concepts CI/CD
- [ ] Choisir et justifier un workflow Git
- [ ] Créer un pipeline CI/CD complet
- [ ] Implémenter des tests automatisés
- [ ] Configurer un déploiement automatique
- [ ] Appliquer les bonnes pratiques de sécurité
- [ ] Monitorer et optimiser vos pipelines
- [ ] Gérer les secrets de manière sécurisée

---

## Support et contribution

Pour toute question ou suggestion d'amélioration :

1. Ouvrir une issue sur le repository
2. Proposer une pull request
3. Contacter l'équipe pédagogique

---

## Licence et utilisation

Ce cours est fourni à des fins éducatives.

---

## Changelog

- **2024-01** : Création du cours
- Version initiale avec 7 modules complets

---

**Bonne formation et bon coding ! 🚀**
