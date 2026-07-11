# Structurizr

## Qu'est-ce que Structurizr ?

Structurizr est une plateforme créée par **Simon Brown** (l'auteur du modèle C4) pour modéliser, visualiser et documenter l'architecture logicielle en utilisant le modèle C4.

Contrairement à PlantUML où on décrit des diagrammes individuels, Structurizr permet de décrire **un modèle d'architecture unique** et d'en générer automatiquement plusieurs vues (Context, Container, Component, Deployment).

**Avantage fondamental :** Modifier un élément une seule fois met à jour toutes les vues qui l'utilisent.

---

## Les versions de Structurizr

| Version | Description | Usage |
|---------|-------------|-------|
| **Structurizr Lite** | Application Docker self-hosted, gratuite | Développement, équipes |
| **Structurizr Cloud** | SaaS payant | Organisations, collaboration |
| **Structurizr CLI** | Outil en ligne de commande | CI/CD, export |
| **Structurizr for .NET/Java** | SDK programmatique | Génération via code |

**Ce cours couvre Structurizr Lite + DSL**, la combinaison recommandée pour les équipes techniques.

---

## Lancer Structurizr Lite

```bash
# Créer un répertoire de travail
mkdir structurizr-workspace
cd structurizr-workspace

# Lancer Structurizr Lite
docker run -it --rm \
  -p 8080:8080 \
  -v $(pwd):/usr/local/structurizr \
  structurizr/lite

# Accéder à l'interface
open http://localhost:8080
```

Structurizr Lite cherche automatiquement un fichier `workspace.dsl` dans le répertoire monté.

---

## Le DSL Structurizr

Le DSL (Domain Specific Language) Structurizr est un langage textuel pour décrire l'architecture.

### Structure générale

```dsl
workspace "Nom du workspace" "Description" {

    model {
        // Définition des personnes, systèmes, conteneurs, composants
    }

    views {
        // Définition des vues (Context, Container, Component...)
    }

    configuration {
        // Configuration optionnelle
    }
}
```

---

## Exemple complet — Plateforme DataFlow

### workspace.dsl

```dsl
workspace "Plateforme DataFlow" "Architecture de la plateforme d'analyse de données." {

    model {

        # ─── Acteurs (Personnes) ───────────────────────────────────────────

        dataAnalyst = person "Data Analyst" {
            description "Analyse les données de ventes et crée des rapports et dashboards."
            tags "Interne"
        }

        directeurCommercial = person "Directeur Commercial" {
            description "Consulte les KPIs et tableaux de bord pour piloter l'activité."
            tags "Interne"
        }

        # ─── Systèmes externes ─────────────────────────────────────────────

        salesforce = softwareSystem "Salesforce CRM" {
            description "Gestion de la relation client. Source principale des données commerciales."
            tags "Externe"
        }

        erp = softwareSystem "Système ERP (SAP)" {
            description "Gestion des commandes, stocks et facturation."
            tags "Externe"
        }

        emailSystem = softwareSystem "Système Email" {
            description "Envoi des rapports automatiques aux équipes métier."
            tags "Externe"
        }

        # ─── Système principal ─────────────────────────────────────────────

        dataflow = softwareSystem "Plateforme DataFlow" {
            description "Collecte, transforme et expose les données métier de l'entreprise."

            # Conteneurs du système
            metabase = container "Metabase" {
                description "Interface web de visualisation et création de dashboards."
                technology "JavaScript, React"
                tags "Frontend"
            }

            api = container "API DataFlow" {
                description "Expose les données et déclenche les pipelines via REST."
                technology "Python, FastAPI 0.109"
                tags "Backend"

                # Composants de l'API
                router = component "API Routers" {
                    description "Routes HTTP : /pipelines, /reports, /alerts, /health"
                    technology "FastAPI Routers"
                }

                authMiddleware = component "Auth Middleware" {
                    description "Valide les tokens JWT et les droits d'accès."
                    technology "Python, python-jose"
                }

                pipelineService = component "Pipeline Service" {
                    description "Logique métier pour déclencher et suivre les pipelines."
                    technology "Python"
                }

                reportService = component "Report Service" {
                    description "Génère et expose les rapports agrégés."
                    technology "Python"
                }

                pipelineRepo = component "Pipeline Repository" {
                    description "Accès aux données des pipelines en base."
                    technology "Python, SQLAlchemy"
                }

                reportRepo = component "Report Repository" {
                    description "Accès aux rapports et agrégats."
                    technology "Python, SQLAlchemy"
                }
            }

            dwh = container "Data Warehouse" {
                description "Stocke les données transformées et agrégées."
                technology "PostgreSQL 15"
                tags "Base de données"
            }

            airflow = container "Apache Airflow" {
                description "Orchestre les pipelines d'ingestion et de transformation."
                technology "Python, Airflow 2.7"
                tags "Orchestration"
            }

            dataLake = container "Data Lake" {
                description "Stockage brut des données sources avant transformation."
                technology "MinIO (compatible S3)"
                tags "Stockage"
            }

            dbt = container "dbt" {
                description "Transformations SQL et modélisation des données."
                technology "Python, dbt Core 1.7"
                tags "Transformation"
            }

            redis = container "Redis" {
                description "Cache des résultats de requêtes fréquentes."
                technology "Redis 7"
                tags "Cache"
            }
        }

        # ─── Relations ─────────────────────────────────────────────────────

        # Utilisateurs → Interface
        dataAnalyst -> metabase "Consulte les dashboards" "HTTPS"
        directeurCommercial -> metabase "Consulte les KPIs" "HTTPS"
        dataAnalyst -> api "Déclenche des pipelines" "HTTPS / REST"

        # Interface → Données
        metabase -> dwh "Exécute des requêtes" "SQL / JDBC"
        metabase -> redis "Lit le cache" "Redis Protocol"

        # API → Services
        api -> airflow "Déclenche les DAGs" "HTTP REST"
        api -> dwh "Lit les données" "SQL"
        api -> redis "Cache les réponses" "Redis Protocol"

        # Airflow → Sources externes
        airflow -> salesforce "Extrait les données" "API REST HTTPS"
        airflow -> erp "Extrait les données" "JDBC"

        # Pipeline de données
        airflow -> dataLake "Stocke les données brutes" "S3 API"
        airflow -> dbt "Exécute les transformations" "CLI subprocess"
        dbt -> dwh "Écrit les données transformées" "SQL"
        dbt -> dataLake "Lit les données brutes" "S3 API"

        # Notifications
        dataflow -> emailSystem "Envoie les rapports" "SMTP"

        # Relations composants internes
        router -> authMiddleware "Vérifie l'authentification"
        router -> pipelineService "Délègue les appels pipelines"
        router -> reportService "Délègue les appels rapports"
        pipelineService -> airflow "Déclenche les DAGs" "HTTP"
        pipelineService -> pipelineRepo "Lit/écrit les métadonnées"
        reportService -> reportRepo "Lit les données"
        pipelineRepo -> dwh "SQL" "JDBC"
        reportRepo -> dwh "SQL" "JDBC"
    }

    views {

        # Vue Contexte
        systemContext dataflow "Contexte" {
            include *
            autoLayout lr
            title "Diagramme de Contexte — Plateforme DataFlow"
            description "Vue d'ensemble des utilisateurs et systèmes qui interagissent avec la plateforme."
        }

        # Vue Conteneurs
        container dataflow "Conteneurs" {
            include *
            autoLayout lr
            title "Diagramme de Conteneurs — Plateforme DataFlow"
            description "Composants déployables de la plateforme DataFlow."
        }

        # Vue Composants — API uniquement
        component api "ComposantsAPI" {
            include *
            autoLayout
            title "Diagramme de Composants — API DataFlow"
            description "Architecture interne du service API FastAPI."
        }

        # Vue dynamique — flux d'ingestion
        dynamic dataflow "FluxIngestion" "Flux d'ingestion Salesforce → DWH" {
            airflow -> salesforce "1. Extrait les données via API"
            airflow -> dataLake "2. Stocke en zone brute (S3)"
            airflow -> dbt "3. Lance les transformations"
            dbt -> dataLake "4. Lit les données brutes"
            dbt -> dwh "5. Écrit les données transformées"
            metabase -> dwh "6. Requête les données pour le dashboard"
            autoLayout
        }

        # Styles
        styles {
            element "Person" {
                shape Person
                background "#1168BD"
                color "#ffffff"
            }
            element "Externe" {
                background "#999999"
                color "#ffffff"
            }
            element "Base de données" {
                shape Cylinder
                background "#f5a623"
            }
            element "Stockage" {
                shape Cylinder
                background "#7ec8e3"
            }
            element "Frontend" {
                background "#85c1e9"
            }
            element "Backend" {
                background "#82e0aa"
            }
            element "Orchestration" {
                background "#c39bd3"
            }
        }

        theme default
    }
}
```

---

## Navigation dans Structurizr Lite

Une fois le workspace lancé sur `http://localhost:8080` :

1. **Dashboard :** Liste toutes les vues disponibles
2. **Cliquer sur une vue** pour l'afficher
3. **Double-cliquer sur un système** pour "zoomer" vers la vue enfant (Context → Container → Component)
4. **Panneau de droite :** Propriétés de l'élément sélectionné
5. **Bouton "Export"** : PNG, SVG, PlantUML, Mermaid

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Structurizr Lite dans le navigateur, montrant le dashboard avec plusieurs vues listées (Context, Containers, Components), puis naviguer depuis la vue Context en double-cliquant sur le système pour arriver automatiquement dans la vue Container.
> **Expliquer :** Comment le modèle unique génère plusieurs vues cohérentes, comment la navigation par drill-down fonctionne, et comment modifier le fichier `workspace.dsl` dans VSCode et recharger Structurizr pour voir les changements en temps réel.

---

## Export et intégration

### Export des diagrammes

```bash
# Installation de la CLI Structurizr
docker pull structurizr/cli:latest

# Exporter en PNG
docker run --rm \
  -v $(pwd):/usr/local/structurizr \
  structurizr/cli:latest export \
  -workspace /usr/local/structurizr/workspace.dsl \
  -format png

# Exporter en SVG
docker run --rm \
  -v $(pwd):/usr/local/structurizr \
  structurizr/cli:latest export \
  -workspace /usr/local/structurizr/workspace.dsl \
  -format svg

# Exporter en PlantUML (pour intégration avec d'autres outils)
docker run --rm \
  -v $(pwd):/usr/local/structurizr \
  structurizr/cli:latest export \
  -workspace /usr/local/structurizr/workspace.dsl \
  -format plantuml/c4plantuml

# Exporter en Mermaid
docker run --rm \
  -v $(pwd):/usr/local/structurizr \
  structurizr/cli:latest export \
  -workspace /usr/local/structurizr/workspace.dsl \
  -format mermaid
```

### Intégration CI/CD

```yaml
# .github/workflows/architecture.yml
name: Generate Architecture Diagrams

on:
  push:
    paths:
      - 'docs/architecture/workspace.dsl'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Export diagrams
        run: |
          docker run --rm \
            -v ${{ github.workspace }}/docs/architecture:/usr/local/structurizr \
            structurizr/cli:latest export \
            -workspace /usr/local/structurizr/workspace.dsl \
            -format png \
            -output /usr/local/structurizr/output/

      - name: Commit generated diagrams
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "chore: regenerate architecture diagrams"
          file_pattern: "docs/architecture/output/*.png"
```

---

## Fonctionnalités avancées du DSL

### Déployments (environnements)

```dsl
deploymentEnvironment "Production" {
    deploymentNode "AWS eu-west-1" {
        technology "Amazon Web Services"

        deploymentNode "ECS Fargate" {
            technology "AWS ECS"
            containerInstance api
            containerInstance airflow
        }

        deploymentNode "RDS" {
            technology "AWS RDS"
            containerInstance dwh
        }

        deploymentNode "ElastiCache" {
            technology "AWS ElastiCache"
            containerInstance redis
        }
    }
}
```

### Propriétés et documentation

```dsl
api = container "API DataFlow" {
    description "..."
    technology "Python, FastAPI"

    # Documentation inline
    docs {
        content "L'API expose les endpoints REST pour..."
    }

    # Décisions d'architecture liées
    decisions {
        decision "ADR-0002 — Utiliser FastAPI" "accepted"
    }

    # Propriétés personnalisées
    properties {
        "owner" "equipe-backend"
        "sla" "99.9%"
        "maintenu-depuis" "2024-01"
    }
}
```

---

## Structurizr vs PlantUML C4

| Critère | Structurizr DSL | PlantUML C4 |
|---------|----------------|-------------|
| Modèle unique | Oui — une source, plusieurs vues | Non — un fichier par diagramme |
| Cohérence | Automatique | Manuelle |
| Navigation drill-down | Oui (interface web) | Non |
| Courbe d'apprentissage | Modérée | Faible |
| Infrastructure | Docker nécessaire | Extension VSCode |
| Export | PNG, SVG, PlantUML, Mermaid | PNG, SVG |
| Intégration Markdown | Via images exportées | Via serveur ou plugin |

**Recommandation :** Utiliser **PlantUML C4** pour des diagrammes ponctuels ou en début de projet. Migrer vers **Structurizr** quand l'architecture devient complexe ou quand l'équipe grandit.

---

## Résumé

- Structurizr permet de modéliser une architecture complète dans un **fichier DSL unique**
- Un modèle → N vues (Context, Container, Component, Deployment)
- Structurizr Lite fonctionne avec **Docker en local**, sans compte cloud
- La CLI permet d'**exporter les diagrammes en CI/CD** (PNG, SVG, Mermaid, PlantUML)
- L'avantage principal sur PlantUML : la **cohérence automatique** entre les vues
