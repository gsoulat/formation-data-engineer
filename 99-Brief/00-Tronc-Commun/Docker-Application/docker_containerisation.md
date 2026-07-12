# Brief Projet Data Engineering
## Conteneurisation d'Application avec Docker

---

## Titre

**Dockerisation d'Application : Du Développement au Déploiement**

---

## Description rapide

Conteneurisez une application existante en créant une image Docker personnalisée, orchestrez-la avec Docker Compose et publiez-la sur DockerHub pour un déploiement professionnel.

---

## Contexte

### Situation Professionnelle

Vous êtes Data Engineer dans une entreprise en pleine transformation digitale. L'équipe de développement a créé une application de traitement de données qui fonctionne parfaitement sur leurs machines locales. Cependant, lors du déploiement sur les serveurs de production, de nombreux problèmes surviennent :

- **Incompatibilités de versions** : Les dépendances Python diffèrent entre les environnements
- **Configuration manuelle** : Chaque déploiement nécessite une configuration fastidieuse
- **Non-reproductibilité** : "Ça marche sur ma machine" est devenu le quotidien de l'équipe
- **Scalabilité limitée** : Impossible de déployer rapidement plusieurs instances

Votre mission est de **conteneuriser cette application** pour garantir :
- Un environnement identique du développement à la production
- Un déploiement reproductible et automatisable
- Une documentation claire de l'infrastructure
- Une distribution facilitée via un registre d'images (DockerHub)

### Objectif Pédagogique

Maîtriser le cycle complet de conteneurisation d'une application : de la création du Dockerfile à la publication sur un registre Docker.

### Compétences Visées

- Rédiger un Dockerfile optimisé et sécurisé
- Créer des images Docker multi-couches efficaces
- Orchestrer des services avec Docker Compose
- Gérer les volumes et réseaux Docker
- Publier des images sur DockerHub
- Appliquer les bonnes pratiques de conteneurisation

### Architecture Cible

```
Application Locale → Dockerfile → Image Docker → DockerHub
                          ↓
              Docker Compose (orchestration)
                    ↓           ↓
              Application   Base de données
                    └─────┬─────┘
                       Réseau Docker
```

---

## Modalités pédagogiques

### Durée : 1 jour

### Organisation du travail

- **Travail individuel**
- Utilisation de l'application développée précédemment (ou application fournie si nécessaire)
- Accès à la documentation Docker officielle autorisé

### Phases du projet

#### Phase 1 : Analyse et Préparation (1h)
- Analyser l'application existante (dépendances, configuration, points d'entrée)
- Identifier les besoins en termes de volumes, réseaux et variables d'environnement
- Planifier la structure du Dockerfile

#### Phase 2 : Création du Dockerfile (2h)
- Écrire un Dockerfile complet avec :
  - Image de base appropriée (version slim recommandée)
  - Installation des dépendances système et Python
  - Configuration de l'environnement de travail
  - Définition du point d'entrée
- Construire et tester l'image localement
- Optimiser la taille de l'image (multi-stage build si pertinent) Bonus

#### Phase 3 : Docker Compose (2h)
- Créer un fichier `docker-compose.yml` avec :
  - Service applicatif basé sur le Dockerfile
  - Service de base de données (PostgreSQL; mysql. etc...)
  - Configuration des volumes pour la persistance
  - Définition du réseau inter-services
  - Gestion des variables d'environnement via fichier `.env`
  - Healthchecks pour garantir l'ordre de démarrage
- Tester l'orchestration complète

#### Phase 4 : Publication sur DockerHub (1h)
- Créer un compte DockerHub (si nécessaire)
- Tagger l'image correctement (username/app:version)
- Pousser l'image sur DockerHub
- Documenter le processus dans le README

#### Phase 5 : Documentation et Finalisation (1h)
- Rédiger un README complet avec :
  - Instructions de build
  - Instructions de déploiement
  - Variables d'environnement requises
  - Commandes Docker Compose utiles
- Vérifier le bon fonctionnement de bout en bout

### Ressources

- [Documentation Docker officielle](https://docs.docker.com/)
- [Best practices Dockerfile](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [DockerHub](https://hub.docker.com/)
- Cours Docker de la formation (02-Containerisation/Docker/cours/)

---

## Modalités d'évaluation

### Évaluation formative
- Points d'étape réguliers avec le formateur
- Revue de code du Dockerfile
- Démonstration du fonctionnement de la stack

### Évaluation sommative
- Soutenance orale de 10 minutes :
  - Présentation de l'architecture Docker mise en place
  - Démonstration du build et du déploiement
  - Explication des choix techniques
  - Questions/réponses

---

## Livrables attendus

### Repository GitHub contenant :

1. **Application source** : Le code de l'application à conteneuriser

2. **Dockerfile** :
   - Image de base officielle et versionnée
   - Labels de métadonnées

3. **docker-compose.yml** :
   - Service applicatif
   - Service base de données PostgreSQL, MySQL, etc...
   - Volumes nommés pour la persistance
   - Réseau personnalisé
   - Gestion des dépendances (depends_on + healthcheck)

4. **Fichier .env.example** :
   - Template des variables d'environnement requises

5. **Fichier .dockerignore** :
   - Exclusion des fichiers inutiles (venv, __pycache__, .git, etc.)

6. **README.md** :
   - Description du projet
   - Prérequis (Docker, Docker Compose)
   - Instructions d'installation et de déploiement
   - Lien vers l'image DockerHub
   - Commandes utiles

7. **Image DockerHub** :
   - Image publiée et accessible publiquement
   - Tag versionné (ex: v1.0)

---

## Critères de performance

### Dockerfile (30 points)


Image de base officielle et version slim                                      
Installation des dépendances optimisée (requirements.txt copié avant le code) 
Variables d'environnement configurées                                         
Répertoire de travail défini (WORKDIR)                                        
Labels de métadonnées présents                                                
Image fonctionnelle (build + run sans erreur)                                 

### Docker Compose (30 points)

Structure YAML valide et bien organisée       
Service applicatif correctement configuré 
Service PostgreSQL avec healthcheck       
Volumes nommés pour la persistance  
Réseau personnalisé configuré         
Gestion des dépendances (depends_on + condition)
Variables d'environnement via .env 

### Publication DockerHub (20 points)

Compte DockerHub créé                            
Image correctement taguée (username/app:version) 
Image publique et accessible                     
Pull et run fonctionnels depuis DockerHub        

### Documentation et Bonnes Pratiques (20 points)

README clair et complet                    
Fichier .dockerignore présent et pertinent 
Fichier .env.example fourni                
Code versionné sur GitHub                  
Respect des conventions de nommage         
Sécurité (pas de secrets en clair)         

### Bonus (jusqu'à 10 points supplémentaires)

Multi-stage build pour optimiser la taille

---

## Exemple de structure attendue

```
mon-projet/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── ...
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Ressources complémentaires

### Commandes utiles

```bash
# Build de l'image
docker build -t mon-app:v1 .

# Lancer avec Docker Compose
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter la stack
docker-compose down

# Pousser sur DockerHub
docker login
docker tag mon-app:v1 username/mon-app:v1
docker push username/mon-app:v1
```

### Checklist avant soumission

- [ ] Le Dockerfile build sans erreur
- [ ] L'application démarre correctement dans le conteneur
- [ ] Docker Compose lance toute la stack
- [ ] La base de données est accessible depuis l'application
- [ ] L'image est publiée sur DockerHub
- [ ] Le README contient toutes les instructions
- [ ] Aucun secret n'est présent dans le code

---

*Brief Docker pour Data Engineering - 2024*
