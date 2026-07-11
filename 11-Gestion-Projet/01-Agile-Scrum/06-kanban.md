# Kanban

## Origine et philosophie

Kanban (看板) est un mot japonais signifiant "panneau visuel" ou "signal". La méthode est née dans les usines Toyota dans les années 1950 dans le cadre du Toyota Production System (TPS), ancêtre du Lean Manufacturing.

L'idée centrale est simple : **visualiser le travail et limiter le travail en cours** pour améliorer le flux et identifier les goulots d'étranglement.

En développement logiciel, Kanban a été adapté par David J. Anderson au début des années 2000 et est aujourd'hui l'une des approches Agile les plus utilisées.

---

## Le Board Kanban

### Structure de base

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   BACKLOG    │   IN PROGRESS│   IN REVIEW  │     DONE     │
│              │   WIP: 3     │   WIP: 2     │              │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │
│ │ Pipeline │ │ │ Ingestion│ │ │Dashboard │ │ │Alertes   │ │
│ │ CRM v2   │ │ │ Salesf.  │ │ │ventes    │ │ │Slack     │ │
│ └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘ │
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │
│ │ Export   │ │ │ Tests    │ │ │Code rev. │ │ │Modèle    │ │
│ │ CSV      │ │ │ qualité  │ │ │pipeline  │ │ │dbt base  │ │
│ └──────────┘ │ └──────────┘ │ └──────────┘ │ └──────────┘ │
│ ┌──────────┐ │ ┌──────────┐ │              │              │
│ │ SSO      │ │ │ Schéma   │ │              │              │
│ │ entreprise│ │ │ docs     │ │              │              │
│ └──────────┘ │ └──────────┘ │              │              │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### Colonnes typiques

| Colonne | Description |
|---------|-------------|
| Backlog / To Do | Items identifiés, pas encore démarrés |
| In Progress / En cours | Travail actif |
| In Review / Revue | En attente de code review, de validation |
| Testing / QA | En cours de test |
| Blocked / Bloqué | Stoppage pour cause externe |
| Done / Terminé | Répondant à la Definition of Done |

**Conseil :** Adapter les colonnes au workflow réel de l'équipe, pas à un modèle théorique.

---

## Les limites WIP (Work In Progress)

### Principe fondamental

WIP Limit = **nombre maximum d'items simultanément dans une colonne**.

**Loi de Little :** `Temps moyen de traitement = En-cours / Débit`

Plus il y a d'items en cours, plus chaque item met du temps à être terminé. Réduire le WIP augmente le débit global.

### Pourquoi limiter le WIP ?

**Sans limite WIP — multitâche nocif :**
```
Alice :  ████▒▒▒▒████▒▒▒▒████▒▒▒▒████  (3 tâches en parallèle)
          ↕ context switching
Résultat : toutes les tâches livrent tard
```

**Avec limite WIP — focus :**
```
Alice : ████████ ████████ ████████  (1 tâche à la fois)
Résultat : livraison continue, délai réduit
```

**Autres bénéfices :**
- Révèle les goulots d'étranglement (si une colonne est souvent pleine, c'est un bottleneck)
- Encourage la collaboration (si je ne peux pas prendre une nouvelle tâche, j'aide un collègue)
- Réduit le stress (moins de choses à suivre en même temps)

### Fixer les limites WIP

**Règle de départ :** `WIP max = (nb membres équipe) × 1.5`

Pour une équipe de 4 : WIP max In Progress ≈ 6.

Ajuster progressivement selon les observations. Commencer généreux, réduire progressivement.

**Signaux indiquant que la limite est trop haute :**
- La colonne est souvent pleine à la limite
- Beaucoup de context switching observé
- Les items mettent longtemps à traverser le board

**Signaux indiquant que la limite est trop basse :**
- L'équipe est souvent bloquée, ne peut pas tirer de nouvelles tâches
- Des personnes sont régulièrement sans travail

---

## Métriques Kanban

### Cycle Time (Temps de cycle)

Le cycle time est le **temps écoulé entre le début du travail effectif et la livraison**.

```
Item A :  │──────────────────│  Cycle time : 4 jours
Item B :  │───────│           Cycle time : 2 jours
Item C :  │─────────────────────────│  Cycle time : 8 jours

Cycle time moyen : (4 + 2 + 8) / 3 = 4.7 jours
```

**Réduire le cycle time** = livrer plus vite de la valeur.

### Lead Time (Délai de livraison)

Le lead time commence **dès que la demande est créée** (même en attente dans le backlog).

```
Demande créée ──────────────────────────── Livraison
│                                          │
│   Attente backlog    │   Cycle time      │
│◄────────────────────►│◄──────────────────►│
│       10 jours       │      4 jours      │
│◄─────────────────── Lead time : 14 j ───►│
```

**Lead time** = attente + cycle time. Réduire l'attente passe par une meilleure priorisation du backlog.

### Throughput (Débit)

Le throughput est le **nombre d'items terminés par unité de temps**.

```
Semaine 1 : 6 items terminés
Semaine 2 : 8 items terminés
Semaine 3 : 5 items terminés
Semaine 4 : 7 items terminés
Débit moyen : 6.5 items/semaine
```

### Cumulative Flow Diagram (CFD)

Le CFD est le graphique Kanban par excellence. Il montre l'accumulation d'items dans chaque état au fil du temps.

```
Items
50 |████████████████████████ (Done)
40 |▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (In Review)
30 |░░░░░░░░░░░░░░░░░░░░░░░ (In Progress)
20 |▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ (Backlog)
    Sem1 Sem2 Sem3 Sem4 Sem5 Sem6
```

**Lectures du CFD :**
- Bandes horizontales stables = flux régulier
- Bande "In Progress" qui grossit = accumulation, goulot en aval
- Bande "In Review" qui grossit = pas assez de reviewers

---

## Kanban vs Scrum — Comparaison détaillée

### Différences fondamentales

| Aspect | Scrum | Kanban |
|--------|-------|--------|
| Itérations | Sprints fixes (1-4 semaines) | Flux continu, pas de sprints |
| Engagement | Engagement sur un Sprint Goal | Pas d'engagement — flux |
| Rôles | PO, SM, Dev Team définis | Aucun rôle prescrit |
| Cérémonies | Planning, Daily, Review, Rétro (obligatoires) | Aucune cérémonie prescrite |
| Estimation | Story points obligatoires | Optionnelle |
| Changements | Pas pendant le sprint | À tout moment |
| Planification | Par sprint | Continue |
| Métriques clés | Vélocité, Burndown | Cycle time, Throughput, CFD |

### Quand choisir Scrum ?

- Produit avec des fonctionnalités à développer de façon planifiée
- Équipe stable, dédiée à un produit
- Besoin de cadence et de prévisibilité
- Product Owner disponible et impliqué
- Projets data engineering avec des livrables réguliers (dashboards, pipelines)

### Quand choisir Kanban ?

- Activité de support ou de maintenance
- Demandes imprévisibles et urgentes (incidents, bugs de production)
- Équipe ops ou data ops
- Travail continu sans notion de "release"
- Pipeline data de traitement continu (streaming, événements)

### Kanban pour le DataOps

Kanban est particulièrement adapté aux équipes **DataOps** :

```
DataOps Kanban Board
───────────────────────────────────────────────────────
 INCOMING    │ ANALYSE  │ EN COURS  │  EN TEST  │  DONE
  ISSUES     │          │  WIP: 3   │  WIP: 2   │
─────────────┼──────────┼───────────┼───────────┼──────
 Bug pipeline│          │ Fix       │ Correction│ Optim.
 CRM null    │ Analyse  │ schéma    │ pipeline  │ requête
             │ impact   │ dbt       │ Salesf.   │ dbt
─────────────┼──────────┼───────────┼───────────┼──────
 Perf.       │          │ Optim.    │           │ Ajout
 dashboard   │          │ index     │           │ colonne
 lente       │          │ postgres  │           │ dim_date
─────────────┼──────────┼───────────┼───────────┼──────
 Nouveau     │          │           │           │
 format API  │          │           │           │
 partenaire  │          │           │           │
───────────────────────────────────────────────────────
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un board Trello ou Jira configuré en mode Kanban pour une équipe data/ops, avec des limites WIP visibles sur les colonnes et quelques tickets en cours.
> **Expliquer :** Comment les limites WIP sont configurées dans l'outil, ce qui se passe quand une colonne atteint sa limite (l'équipe doit aider à débloquer avant de tirer de nouvelles tâches), et comment identifier visuellement un goulot d'étranglement.

---

## Scrumban

### Qu'est-ce que c'est ?

Scrumban est un **hybride entre Scrum et Kanban**. Il combine la structure de Scrum (sprints, rétrospectives) avec la flexibilité de Kanban (flux continu, WIP limits).

**Adapté pour :**
- Équipes qui passent de Scrum à Kanban progressivement
- Projets mi-produit, mi-support
- Équipes data qui gèrent à la fois des développements planifiés et des incidents

**Caractéristiques :**
- Sprints conservés pour la cadence et la planification
- WIP limits appliquées sur le board
- Pas de commitment ferme sur le sprint backlog (les items peuvent changer)
- Métriques des deux mondes : vélocité + cycle time

---

## Flux vs Sprints — Perspectives sur la livraison de valeur

### La vision "flux"

En Kanban, la valeur est livrée **en continu** dès qu'un item est terminé. Pas de release groupée à la fin d'un sprint.

**Avantage :** Une feature terminée le mardi peut être en production le jeudi.
**Risque :** Moins de coordination, besoin d'un pipeline de déploiement continu robuste (CI/CD).

### La vision "sprint"

En Scrum, la valeur est livrée **par incrément** à la fin de chaque sprint. Le Sprint Review permet une validation cohérente.

**Avantage :** Coordination, démos groupées, feedback structuré.
**Risque :** Une feature prête le Lundi J2 attend jusqu'à la fin du sprint pour être livrée.

### Le choix selon le contexte data

| Contexte | Recommandation |
|----------|---------------|
| Data Warehouse en construction | Scrum (livraisons planifiées par sprint) |
| DataOps / maintenance pipelines | Kanban (réactivité aux incidents) |
| ML en production | Kanban (monitoring continu, correction rapide) |
| Dashboard de reporting | Scrum (releases groupées avec les équipes métier) |
| API data interne | Scrum ou Scrumban |

---

## Résumé

| Concept | Définition |
|---------|-----------|
| Board Kanban | Visualisation du flux de travail par colonnes |
| WIP Limit | Nombre maximum d'items en cours dans une colonne |
| Cycle Time | Durée entre début du travail et livraison |
| Lead Time | Durée entre création de la demande et livraison |
| Throughput | Nombre d'items livrés par période |
| CFD | Graphique d'accumulation par état dans le temps |
| Scrumban | Hybride Scrum + Kanban |

**Principe fondamental Kanban :** Visualiser, Limiter le WIP, Gérer le flux, Rendre explicites les politiques, Implémenter les boucles de feedback, Améliorer collaborativement.
