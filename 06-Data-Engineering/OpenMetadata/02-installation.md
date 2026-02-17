# Chapitre 2 : Installation et Configuration

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation avec Docker Compose](#installation-avec-docker-compose)
3. [Déploiement Kubernetes](#déploiement-kubernetes)
4. [Configuration de l'authentification](#configuration-de-lauthentification)
5. [Premier tour de l'interface](#premier-tour-de-linterface)
6. [Configuration avancée](#configuration-avancée)

---

## Prérequis

### Matériel minimum

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| **CPU** | 2 cores | 4 cores |
| **RAM** | 4 Go | 8 Go |
| **Disque** | 20 Go | 50 Go |

### Logiciels requis

| Logiciel | Version minimum |
|----------|----------------|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |
| Python | 3.8+ (pour le SDK) |
| Git | 2.0+ |

### Vérification de l'environnement

```bash
# Vérifier Docker
docker --version
# Docker version 24.x ou supérieur

# Vérifier Docker Compose
docker compose version
# Docker Compose version v2.x

# Vérifier la RAM disponible pour Docker
docker info | grep "Total Memory"
# Minimum 4 Go alloués à Docker
```

---

## Installation avec Docker Compose

### Méthode rapide (recommandée pour le cours)

```bash
# Créer un répertoire de travail
mkdir openmetadata-demo && cd openmetadata-demo

# Télécharger le fichier docker-compose
curl -sL https://github.com/open-metadata/OpenMetadata/releases/latest/download/docker-compose.yml -o docker-compose.yml

# Lancer OpenMetadata
docker compose up -d
```

### Vérification du déploiement

```bash
# Vérifier que tous les conteneurs tournent
docker compose ps
```

Vous devriez voir les services suivants :

| Service | Port | Rôle |
|---------|------|------|
| `openmetadata-server` | 8585 | API Server + UI |
| `openmetadata-ingestion` | 8080 | Airflow (ingestion) |
| `mysql` | 3306 | Stockage métadonnées |
| `elasticsearch` | 9200 | Moteur de recherche |

### Accès à l'interface

```
URL : http://localhost:8585
Login : admin
Password : admin
```

> ⚠️ **Important** : Changez le mot de passe admin dès la première connexion en production.

### Vérification de santé

```bash
# Vérifier l'API Server
curl -s http://localhost:8585/api/v1/system/version | python -m json.tool

# Réponse attendue
{
    "version": "1.x.x",
    "revision": "..."
}
```

### Arrêt et nettoyage

```bash
# Arrêter les services
docker compose down

# Arrêter et supprimer les volumes (reset complet)
docker compose down -v
```

---

## Déploiement Kubernetes

### Avec Helm (production)

```bash
# Ajouter le repo Helm
helm repo add open-metadata https://helm.open-metadata.org/
helm repo update

# Installer OpenMetadata (namespace dédié)
kubectl create namespace openmetadata
helm install openmetadata open-metadata/openmetadata \
  --namespace openmetadata \
  --values values.yaml
```

### Fichier `values.yaml` minimal

```yaml
# values.yaml
openmetadata:
  config:
    database:
      host: mysql
      port: 3306
      databaseName: openmetadata_db
      auth:
        username: openmetadata_user
        password: openmetadata_password
    elasticsearch:
      host: elasticsearch
      port: 9200

    authentication:
      provider: basic
      publicKeyUrls:
        - "http://localhost:8585/api/v1/system/config/jwks"

  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
```

> Pour ce cours, nous utiliserons **Docker Compose**. Le déploiement Kubernetes est présenté pour référence en vue d'une mise en production.

---

## Configuration de l'authentification

### Modes d'authentification supportés

| Mode | Usage | Complexité |
|------|-------|------------|
| **Basic** | Développement, POC | Simple |
| **OIDC (Google)** | Production avec Google Workspace | Moyenne |
| **OIDC (Azure AD)** | Production avec Azure/Microsoft | Moyenne |
| **OIDC (Okta)** | Production avec Okta | Moyenne |
| **LDAP** | Production avec Active Directory | Avancée |
| **SAML** | SSO d'entreprise | Avancée |

### Configuration OIDC avec Google (exemple)

Dans le fichier `docker-compose.yml`, modifiez les variables d'environnement :

```yaml
openmetadata-server:
  environment:
    AUTHENTICATION_PROVIDER: google
    AUTHENTICATION_PUBLIC_KEYS: '[
      "https://www.googleapis.com/oauth2/v3/certs",
      "http://localhost:8585/api/v1/system/config/jwks"
    ]'
    AUTHENTICATION_AUTHORITY: "https://accounts.google.com"
    AUTHENTICATION_CLIENT_ID: "votre-client-id.apps.googleusercontent.com"
    AUTHENTICATION_CALLBACK_URL: "http://localhost:8585/callback"
```

### Configuration OIDC avec Azure AD

```yaml
openmetadata-server:
  environment:
    AUTHENTICATION_PROVIDER: azure
    AUTHENTICATION_PUBLIC_KEYS: '[
      "https://login.microsoftonline.com/common/discovery/keys",
      "http://localhost:8585/api/v1/system/config/jwks"
    ]'
    AUTHENTICATION_AUTHORITY: "https://login.microsoftonline.com/{tenant-id}"
    AUTHENTICATION_CLIENT_ID: "votre-client-id"
    AUTHENTICATION_CALLBACK_URL: "http://localhost:8585/callback"
```

---

## Premier tour de l'interface

### Page d'accueil

Après connexion, la page d'accueil affiche :

```
┌──────────────────────────────────────────────────────┐
│  🔍 Barre de recherche globale                       │
├──────────────────────────────────────────────────────┤
│                                                       │
│  📊 My Data          │  🔔 Activity Feed             │
│  Tables récentes     │  Dernières modifications       │
│  Dashboards suivis   │  Conversations                 │
│  Pipelines           │  Tâches assignées              │
│                      │                                │
├──────────────────────────────────────────────────────┤
│  Navigation latérale                                  │
│  ├── Explore (tables, topics, dashboards...)         │
│  ├── Quality                                          │
│  ├── Insights                                         │
│  ├── Glossary                                         │
│  ├── Tags                                             │
│  └── Settings                                         │
└──────────────────────────────────────────────────────┘
```

### Navigation principale

| Section | Contenu |
|---------|---------|
| **Explore** | Parcourir tous les assets par catégorie |
| **Quality** | Tableaux de bord de qualité des données |
| **Insights** | Métriques d'utilisation et d'adoption |
| **Glossary** | Glossaire métier |
| **Tags** | Système de tags et classifications |
| **Settings** | Administration, services, utilisateurs |

### Premières actions recommandées

1. **Changer le mot de passe admin** : Settings → Users → Admin → Edit
2. **Explorer les exemples** : Des données d'exemple sont pré-chargées
3. **Parcourir Explore** : Découvrir les types d'assets disponibles
4. **Ajouter un service** : Settings → Services → Add New Service

---

## Configuration avancée

### Variables d'environnement utiles

```yaml
# Logging
LOG_LEVEL: INFO  # DEBUG, INFO, WARN, ERROR

# Limites
SEARCH_INDEX_LIMIT: 10000

# SMTP pour les notifications email
SMTP_SERVER_ENDPOINT: smtp.gmail.com
SMTP_SERVER_PORT: 587
SMTP_USERNAME: notifications@votredomaine.com
SMTP_PASSWORD: votre-password
```

### Personnalisation du docker-compose

```yaml
# docker-compose.override.yml
services:
  openmetadata-server:
    environment:
      # Augmenter la mémoire Java
      OPENMETADATA_HEAP_OPTS: "-Xms1g -Xmx2g"
    volumes:
      # Persister les configurations
      - ./config:/opt/openmetadata/conf
```

### Sauvegarde des données

```bash
# Sauvegarder la base MySQL
docker exec openmetadata_mysql \
  mysqldump -u openmetadata_user -p openmetadata_db > backup.sql

# Restaurer
docker exec -i openmetadata_mysql \
  mysql -u openmetadata_user -p openmetadata_db < backup.sql
```

---

## Résumé

| Étape | Commande / Action |
|-------|-------------------|
| Télécharger | `curl -sL ... -o docker-compose.yml` |
| Lancer | `docker compose up -d` |
| Accéder | `http://localhost:8585` (admin/admin) |
| Vérifier | `docker compose ps` |
| Arrêter | `docker compose down` |

---

> **Prochain chapitre** : [Connecteurs et Ingestion](03-connecteurs-ingestion.md) - Connecter vos premières sources de données
