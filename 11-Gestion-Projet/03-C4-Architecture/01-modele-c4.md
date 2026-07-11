# Le Modèle C4

## Origine et philosophie

Le modèle C4 a été créé par **Simon Brown** au début des années 2010. Il est inspiré de la cartographie : on zoome progressivement depuis une vue globale jusqu'au détail.

Tout comme une carte routière montre les villes et les autoroutes (mais pas les rues secondaires), puis un plan de ville montre les rues (mais pas les pièces des immeubles), le modèle C4 permet de montrer l'architecture à différents niveaux de granularité.

**C4 signifie :** Context, Containers, Components, Code.

---

## Les quatre niveaux

### Niveau 1 — Context (Contexte)

**Question :** "Quel est notre système et qui l'utilise ?"

Le diagramme de contexte est le plus abstrait. Il montre :
- **Le système à construire** (une boîte centrale)
- **Les acteurs** qui l'utilisent (utilisateurs humains)
- **Les systèmes externes** avec lesquels il interagit

C'est le diagramme qu'on montre à **n'importe quelle partie prenante** — même non technique. Un manager, un client, un product owner peut le comprendre.

**Éléments :**
- Person (acteur humain)
- Software System (le système à décrire)
- External System (systèmes tiers)
- Relations (flèches avec description)

**Exemple — Plateforme DataFlow :**

```
[Data Analyst]     [Directeur Commercial]
      │                      │
      ▼                      ▼
┌─────────────────────────────────────┐
│         Plateforme DataFlow         │
│    (plateforme d'analyse de données) │
└─────────────────────────────────────┘
      │                      │
      ▼                      ▼
[Salesforce CRM]      [Système ERP]
  (externe)           (externe)
```

**À qui le montrer :** tout le monde.
**Niveau de détail :** aucune technologie, aucune infrastructure.

---

### Niveau 2 — Containers (Conteneurs)

**Question :** "Quelles sont les grandes parties du système ?"

Le terme "Container" dans C4 ne signifie pas Docker. Il désigne **une unité déployable** : une application web, une API, une base de données, un service de traitement batch, un job cron, etc.

Ce diagramme zoome dans le système identifié au niveau 1 et montre :
- Les applications et services qui le composent
- Les bases de données et stockages
- Les technologies utilisées
- Les interactions entre ces conteneurs

**Éléments :**
- Container (application, API, BDD, job, message broker...)
- Person (acteurs, inchangés)
- External System (systèmes tiers, inchangés)
- Relations (protocoles, données échangées)

**Exemple — Plateforme DataFlow :**

```
[Data Analyst]
      │ utilise (HTTPS)
      ▼
┌──────────────────────────────────────────────┐
│              Plateforme DataFlow              │
│                                              │
│  ┌────────────┐    ┌──────────────────────┐  │
│  │  Metabase  │    │   API FastAPI         │  │
│  │ (dashboard)│    │  (port 8000, Python) │  │
│  └────────────┘    └──────────────────────┘  │
│        │                    │                │
│        ▼                    ▼                │
│  ┌──────────────────────────────────────┐    │
│  │     PostgreSQL (Data Warehouse)       │    │
│  │         (port 5432)                  │    │
│  └──────────────────────────────────────┘    │
│        ▲                                     │
│        │ écrit                               │
│  ┌──────────────────────────────────────┐    │
│  │         Apache Airflow               │    │
│  │     (orchestrateur, Python)          │    │
│  └──────────────────────────────────────┘    │
│        ▲                                     │
└────────┼─────────────────────────────────────┘
         │ lit (HTTPS/API)
    [Salesforce CRM]
```

**À qui le montrer :** équipe technique, architectes, devops, tech leads.
**Niveau de détail :** technologies visibles, pas de code.

---

### Niveau 3 — Components (Composants)

**Question :** "Comment est organisé un conteneur spécifique ?"

Ce niveau zoome dans un seul conteneur (par exemple, l'API FastAPI) et montre les composants internes qui le constituent.

Un "Component" C4 correspond généralement à :
- Un module ou package Python
- Un service, un contrôleur, un repository
- Une interface ou une classe importante

**Éléments :**
- Component (modules, services, controllers...)
- Container (les autres containers avec lesquels le component interagit)
- Person (acteurs, si pertinent)

**Exemple — API FastAPI décomposée :**

```
                [Client HTTP]
                      │
                      ▼
         ┌─────────────────────┐
         │       API FastAPI   │
         │                     │
         │  ┌───────────────┐  │
         │  │   Routers     │  │
         │  │ /pipelines    │  │
         │  │ /reports      │  │
         │  │ /alerts       │  │
         │  └───────┬───────┘  │
         │          │          │
         │  ┌───────▼───────┐  │
         │  │   Services    │  │
         │  │ PipelineService│  │
         │  │ ReportService │  │
         │  └───────┬───────┘  │
         │          │          │
         │  ┌───────▼───────┐  │
         │  │  Repositories │  │
         │  │ PipelineRepo  │  │
         │  │ ReportRepo    │  │
         │  └───────┬───────┘  │
         └──────────┼──────────┘
                    │
                    ▼
            [PostgreSQL DWH]
```

**À qui le montrer :** l'équipe qui développe ce conteneur spécifique.
**Niveau de détail :** modules, interfaces, patterns d'architecture interne.

---

### Niveau 4 — Code

**Question :** "Comment est implémenté un composant spécifique ?"

C'est le niveau des diagrammes de classes UML traditionnels. Il montre le code lui-même : classes, interfaces, méthodes.

**Attention :** Ce niveau est souvent **inutile en pratique** car :
- Les IDEs génèrent automatiquement des diagrammes de classes
- Il vieillit très vite et devient obsolète
- Le code lui-même est la meilleure documentation à ce niveau

**Quand l'utiliser :**
- Algorithme ou pattern complexe à expliquer
- Interface publique d'une bibliothèque
- Onboarding d'un nouveau membre sur un domaine critique

---

## Quand utiliser chaque niveau ?

| Niveau | Audience | Fréquence de mise à jour | Outil recommandé |
|--------|----------|------------------------|-----------------|
| Context | Tout le monde | Rare (changements majeurs) | Whiteboard, Structurizr |
| Container | Équipe technique | Modéré (nouvelles fonctionnalités) | PlantUML, Structurizr |
| Component | Développeurs du service | Fréquent | PlantUML, code review |
| Code | Développeurs | Très fréquent (quasi-inutile) | IDE auto-génération |

**Règle pratique :** Le niveau Context et Container sont essentiels. Le niveau Component est utile pour les systèmes complexes. Le niveau Code est optionnel.

---

## Les éléments de notation C4

### Personnes (People)

Les acteurs humains qui interagissent avec le système.

```
┌──────────────────┐
│                  │
│   [Icône user]   │
│                  │
│   Nom du rôle    │
│   Description    │
└──────────────────┘
```

**Convention :** Utiliser le rôle métier, pas le nom de la personne. "Data Analyst" plutôt que "Marie".

### Systèmes logiciels (Software Systems)

Les systèmes entiers — le vôtre et les externes.

```
┌──────────────────────────────────────┐
│                                      │
│          Nom du système              │
│      [optionnel: technologie]        │
│         Description                  │
│                                      │
└──────────────────────────────────────┘
```

**Convention :** Les systèmes externes sont généralement en gris ou avec une bordure différente.

### Conteneurs (Containers)

Une unité déployable au sein d'un système.

```
┌──────────────────────────────────────┐
│                                      │
│          Nom du conteneur            │
│         [Technologie]                │
│         Description                  │
│                                      │
└──────────────────────────────────────┘
```

### Relations

Les flèches montrent les interactions. Elles doivent toujours être **étiquetées** avec :
- Le type d'interaction (lit, écrit, appelle, envoie...)
- Le protocole si pertinent (HTTPS, gRPC, AMQP, SQL...)

```
[Système A] ──── "envoie des events (AMQP)" ────► [Kafka]
[Airflow]   ──── "lit les données (JDBC)" ─────► [PostgreSQL]
[Metabase]  ──── "exécute des requêtes SQL" ───► [PostgreSQL]
```

---

## Bonnes pratiques du modèle C4

### Ce qu'il faut faire

**Titrer chaque diagramme.** Un diagramme sans titre est ambigu. Exemples de titres :
- "Diagramme de contexte — Plateforme DataFlow"
- "Diagramme de conteneurs — API DataFlow (détail)"

**Ajouter une légende.** Si des couleurs ou des formes ont une signification, l'expliquer.

**Être cohérent entre les niveaux.** Un système nommé "PostgreSQL DWH" au niveau Container doit apparaître avec le même nom au niveau Component.

**Documenter les relations bidirectionnelles séparément.** Si A appelle B et B répond à A, deux flèches distinctes valent mieux qu'une double flèche.

### Ce qu'il ne faut pas faire

**Ne pas tout mettre dans un seul diagramme.** Si le diagramme Container a plus de 15 boîtes, il est trop chargé — créer plusieurs diagrammes.

**Ne pas inclure des détails d'implémentation au mauvais niveau.** Le niveau Context ne montre pas les technologies.

**Ne pas utiliser C4 pour remplacer la documentation.** Les diagrammes complètent la documentation — ils ne la remplacent pas.

**Ne pas dessiner à la main sans le versionner.** Un diagramme non versionné dans Git devient obsolète en quelques mois.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le site c4model.com ouvert sur la page principale, montrant les illustrations officielles des 4 niveaux C4 côte à côte.
> **Expliquer :** Comment chaque niveau zoome dans le précédent (analogie avec les cartes géographiques), pourquoi le niveau Context peut être montré à un non-technicien alors que le niveau Component est réservé aux développeurs, et pourquoi le niveau Code est souvent omis en pratique.

---

## C4 vs UML

Le modèle C4 n'est pas en opposition avec UML — il est complémentaire.

| Modèle C4 | UML équivalent |
|-----------|---------------|
| Context diagram | Use Case Diagram (partiel) |
| Container diagram | Deployment Diagram + Component Diagram |
| Component diagram | Component Diagram |
| Code diagram | Class Diagram |

**Avantage C4 sur UML :** C4 est plus accessible aux non-techniciens et moins verbeux. Un diagramme de contexte C4 est compréhensible en 30 secondes.

**Avantage UML sur C4 :** UML est plus précis pour les détails d'implémentation (multiplicités, stéréotypes, séquences).

**Pratique courante :** Utiliser C4 pour les niveaux 1-3, UML Sequence pour les flux d'interactions complexes.

---

## Résumé

| Niveau | Nom | Question | Audience |
|--------|-----|---------|---------|
| 1 | Context | Qui utilise le système ? | Tout le monde |
| 2 | Container | Quelles sont ses parties ? | Équipe technique |
| 3 | Component | Comment est organisé un service ? | Développeurs |
| 4 | Code | Comment est implémenté un composant ? | Développeurs (rarement) |
