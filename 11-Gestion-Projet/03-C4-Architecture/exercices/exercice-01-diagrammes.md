# Exercice 01 — Créer des diagrammes C4 Context et Container

## Contexte

Vous venez d'intégrer l'équipe technique de **HealthMetrics**, une startup qui développe une plateforme de suivi de santé pour les entreprises. La plateforme collecte des données de bien-être des employés (avec leur consentement), les analyse et produit des rapports pour les responsables RH et les médecins du travail.

### Description du système à modéliser

**HealthMetrics Platform** est composée des éléments suivants :

#### Sources de données (systèmes externes)
- **Withings API** : données des montres connectées (fréquence cardiaque, sommeil, activité)
- **Google Fit / Apple HealthKit** : données des smartphones des employés
- **Workday SIRH** : informations RH (département, équipe, ancienneté) — sans données personnelles sensibles
- **Système de gestion des rendez-vous médicaux** (extern)

#### Acteurs (personnes)
- **Employé** : consulte son propre tableau de bord santé, autorise le partage de données
- **Responsable RH** : accède aux rapports anonymisés par département
- **Médecin du travail** : accède aux données agrégées et aux alertes de santé
- **Administrateur HealthMetrics** : gère la plateforme, les tenants, la conformité RGPD

#### Services internes à modéliser
- **Application web employé** (React) : dashboard personnel, gestion des consentements
- **Application web RH** (Vue.js) : rapports agrégés par département
- **API Backend** (Python FastAPI) : API REST centrale
- **Service d'ingestion** (Python + Airflow) : collecte des données depuis Withings, Google Fit, Apple Health
- **Data Warehouse** (PostgreSQL) : stockage des données agrégées et anonymisées
- **Base de données opérationnelle** (PostgreSQL) : comptes utilisateurs, consentements, configurations
- **Cache** (Redis) : sessions, données fréquemment consultées
- **File d'attente** (RabbitMQ ou Kafka — à justifier dans un ADR) : traitement asynchrone des imports de données
- **Service d'email** : notifications, rapports automatiques (utilise SendGrid)
- **Service RGPD** (Python) : gestion des demandes de suppression, exports de données personnelles

---

## Partie 1 — Diagramme de Contexte (40 min)

### Consignes

Créez un diagramme de contexte C4 pour **HealthMetrics Platform** en utilisant **PlantUML C4** ou **Structurizr DSL** (au choix).

**Le diagramme doit montrer :**
- Les 4 acteurs humains listés ci-dessus
- Le système HealthMetrics (boîte centrale)
- Les systèmes externes pertinents
- Les relations avec un label et un protocole

**Points de vigilance :**
- Ne pas montrer les technologies internes dans le diagramme de contexte
- Les labels des relations doivent être des verbes d'action ("Consulte", "Soumet", "Importe")
- Le protocole doit être réaliste (HTTPS, OAuth 2.0, API REST, JDBC...)

### Template de départ PlantUML

```plantuml
@startuml HealthMetrics-Contexte

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title Diagramme de Contexte — HealthMetrics Platform

LAYOUT_WITH_LEGEND()

' À compléter :

' Personnes
Person(employe, "Employé", "...")
' ... ajouter les autres acteurs

' Système principal
System(healthmetrics, "HealthMetrics Platform", "...")

' Systèmes externes
System_Ext(withings, "Withings API", "...")
' ... ajouter les autres systèmes externes

' Relations
Rel(employe, healthmetrics, "...", "HTTPS")
' ... ajouter les autres relations

@enduml
```

### Questions de réflexion

Avant de dessiner, répondez à ces questions :

1. Quels systèmes externes sont des **sources** de données (flèche vers HealthMetrics) ?
2. Quels systèmes externes sont des **destinations** (flèche depuis HealthMetrics) ?
3. Le Médecin du travail et le Responsable RH utilisent-ils le même système ou des applications distinctes ?
4. Doit-on montrer un système SSO (authentification) dans le diagramme de contexte ?

---

## Partie 2 — Diagramme de Conteneurs (50 min)

### Consignes

Créez un diagramme de conteneurs C4 pour **HealthMetrics Platform**.

**Le diagramme doit montrer :**
- Tous les services internes listés dans la description
- Les bases de données et systèmes de stockage
- Les technologies (FastAPI, PostgreSQL, Redis, etc.)
- Les relations entre services avec le protocole

**Contraintes de conception :**

1. **Séparation des préoccupations RGPD :** Le Data Warehouse ne doit pas contenir de données directement identifiantes. Les données sont anonymisées avant d'arriver dans le DWH.

2. **Cohérence des flux :** Les données Withings passent par le Service d'Ingestion → Queue → DWH. Modélisez ce flux.

3. **Cache :** Redis est utilisé pour les sessions et les pages les plus consultées. Montrez les connexions pertinentes.

### Template de départ PlantUML

```plantuml
@startuml HealthMetrics-Conteneurs

!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title Diagramme de Conteneurs — HealthMetrics Platform

LAYOUT_WITH_LEGEND()

' Acteurs
Person(employe, "Employé", "")
Person(rh, "Responsable RH", "")
Person(medecin, "Médecin du travail", "")
Person(admin, "Administrateur", "")

' Systèmes externes
System_Ext(withings, "Withings API", "")
System_Ext(googleFit, "Google Fit / Apple Health", "")
System_Ext(sendgrid, "SendGrid", "Email")

' Système HealthMetrics — à compléter
System_Boundary(hm, "HealthMetrics Platform") {

    Container(webEmploye, "App Web Employé", "React", "...")
    Container(webRH, "App Web RH", "Vue.js", "...")
    Container(api, "API Backend", "Python, FastAPI", "...")
    ' ... ajouter les autres services

    ContainerDb(dwh, "Data Warehouse", "PostgreSQL", "...")
    ContainerDb(operDb, "Base Opérationnelle", "PostgreSQL", "...")
    ContainerDb(cache, "Cache", "Redis", "...")
    ContainerQueue(queue, "Message Queue", "RabbitMQ ou Kafka", "...")
}

' Relations — à compléter
Rel(employe, webEmploye, "Consulte son dashboard", "HTTPS")
' ...

@enduml
```

---

## Partie 3 — Justification des choix (20 min)

Répondez aux questions suivantes par écrit (5-10 lignes chacune) :

### Question 1 — Séparation des bases de données

Pourquoi avoir séparé la **Base Opérationnelle** (comptes, consentements) du **Data Warehouse** (données de santé agrégées) ?

Quels risques cela évite-t-il ? En quoi est-ce important pour la conformité RGPD ?

### Question 2 — Choix de la queue de messages

Vous avez le choix entre **RabbitMQ** et **Kafka** pour la file d'attente. Quel outil choisiriez-vous pour HealthMetrics et pourquoi ?

Rédigez un ADR simplifié (format Nygard) pour documenter ce choix.

### Question 3 — Relations manquantes

Regardez votre diagramme de conteneurs. Identifiez :
- 2 relations que vous avez peut-être oubliées
- 1 service qui devrait être ajouté (mais qui n'était pas dans la description initiale)

---

## Partie 4 — Extension : Déploiement Cloud (Bonus — 30 min)

Si vous avez terminé les parties 1 à 3, modélisez un **Deployment Diagram** Structurizr montrant le déploiement de HealthMetrics sur AWS :

```
Contexte de déploiement :
- API et services Python → ECS Fargate (conteneurs sans serveur)
- PostgreSQL (DWH + Opérationnel) → AWS RDS Multi-AZ
- Redis → AWS ElastiCache
- Kafka → AWS MSK (Managed Streaming for Kafka)
- Applications web (React/Vue) → CloudFront + S3
- Région : eu-west-3 (Paris) pour la conformité RGPD
```

---

## Critères d'évaluation

| Critère | Barème |
|---------|--------|
| **Diagramme Context** | |
| Tous les acteurs présents et correctement typés | 2 pts |
| Systèmes externes pertinents identifiés | 2 pts |
| Relations labelisées avec verbe + protocole | 2 pts |
| Lisibilité (titre, légende, pas de surcharge) | 1 pt |
| **Diagramme Container** | |
| Tous les services identifiés | 3 pts |
| Technologies correctement renseignées | 2 pts |
| Relations avec protocoles corrects | 3 pts |
| Flux RGPD respecté (anonymisation avant DWH) | 2 pts |
| **Justifications écrites** | |
| Justification séparation des BDD | 2 pts |
| ADR queue de messages (format correct + arguments) | 3 pts |
| Relations manquantes identifiées | 2 pts |
| **Total** | **24 pts** |

---

## Livrables attendus

1. Fichier `healthmetrics-context.puml` (ou équivalent Structurizr)
2. Fichier `healthmetrics-containers.puml` (ou équivalent Structurizr)
3. Images PNG générées des deux diagrammes
4. Document texte avec les réponses aux 3 questions de justification

---

## Ressources

- Templates PlantUML C4 : [https://github.com/plantuml-stdlib/C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- Référence Structurizr DSL : [https://docs.structurizr.com/dsl](https://docs.structurizr.com/dsl)
- Serveur PlantUML en ligne : [https://www.plantuml.com/plantuml/uml/](https://www.plantuml.com/plantuml/uml/)
- Exemples du cours : `../exemples/`
- Introduction C4 : `../01-modele-c4.md`
