# Le Framework Scrum

## Qu'est-ce que Scrum ?

Scrum est un **framework léger** pour gérer des projets complexes en livrant de la valeur par itérations courtes appelées **sprints**. Le nom vient du rugby : la "mêlée" (scrum) où l'équipe entière pousse dans la même direction.

Scrum ne dit pas comment développer un produit. Il définit :
- **Trois rôles** (qui fait quoi)
- **Cinq événements** (quand se retrouver)
- **Trois artefacts** (quoi suivre)

Le reste — choix techniques, organisation interne, outils — appartient à l'équipe.

---

## Les trois rôles Scrum

### Product Owner (PO)

Le Product Owner est **la voix du client au sein de l'équipe**. Il représente les parties prenantes (clients, utilisateurs, direction) et est garant de la valeur produite.

**Responsabilités :**
- Définir et prioriser le Product Backlog
- Clarifier les User Stories pour l'équipe de développement
- Décider quelles fonctionnalités entrent dans chaque sprint
- Accepter ou refuser les incréments lors de la Sprint Review
- Gérer les attentes des parties prenantes

**Profil typique :** Chef de produit, représentant métier, analyste fonctionnel.

**Ce que le PO n'est PAS :**
- Il ne gère pas l'équipe au quotidien (c'est le rôle du Scrum Master)
- Il ne conçoit pas les solutions techniques (c'est l'équipe de développement)
- Il n'est pas disponible uniquement pour les réunions — il doit être joignable quotidiennement

**Dans un projet data :**
- Le PO représente les data analysts ou les équipes métier
- Il priorise : "J'ai besoin du taux de conversion avant le pipeline de stock"
- Il valide que le dashboard produit correspond bien au besoin exprimé

---

### Scrum Master (SM)

Le Scrum Master est **le gardien du processus Scrum**. Il n'est pas un chef de projet. Il est au service de l'équipe, du PO et de l'organisation.

**Responsabilités :**
- Faciliter les cérémonies Scrum
- Supprimer les obstacles (impediments) qui bloquent l'équipe
- Coacher l'équipe sur les pratiques Agile
- Protéger l'équipe des interruptions externes
- Favoriser l'amélioration continue

**Le Scrum Master n'assigne pas de tâches.** L'équipe est auto-organisée.

**Profil typique :** Souvent un développeur senior ou un ancien chef de projet converti à l'Agile. Peut être certifié (CSM, PSM).

**Impediments courants en data :**
- Accès aux données de production bloqué par la DSI
- Dépendance à un système externe non disponible
- Manque de clarté sur le format d'une source de données
- Outil de CI/CD non configuré pour les jobs data

---

### L'équipe de développement (Dev Team)

L'équipe de développement est **pluridisciplinaire et auto-organisée**. Elle comprend toutes les compétences nécessaires pour livrer un incrément fonctionnel.

**Caractéristiques :**
- **Pluridisciplinaire** : data engineers, data analysts, data scientists, DevOps, QA
- **Auto-organisée** : elle décide elle-même comment réaliser le travail
- **Responsable collective** : pas de "ce n'est pas ma partie"
- **Taille idéale** : 3 à 9 personnes (Scrum Guide 2020 : "10 personnes ou moins")

**Règle des "T-shaped people" :** Chaque membre a une compétence principale forte (le vertical du T) mais peut contribuer à d'autres domaines (le horizontal). Un data engineer peut faire de la QA sur un dashboard.

---

## Les cinq événements Scrum

Tous les événements ont une durée maximale (timebox). Dépasser la timebox est considéré comme un dysfonctionnement.

### 1. Le Sprint

Le sprint est le **conteneur de tous les autres événements**. C'est une itération de durée fixe (1 à 4 semaines, généralement 2 semaines).

**Règles du sprint :**
- Durée fixe et constante (pas de sprint de 3 jours ou de 3 semaines selon les humeurs)
- Un seul Sprint Goal par sprint
- Le sprint ne peut pas être annulé sauf par le PO (cas extrême)
- Aucune modification ne remet en question le Sprint Goal en cours

### 2. Sprint Planning

**Quand :** Au début de chaque sprint.
**Durée :** Maximum 8 heures pour un sprint de 4 semaines (4h pour 2 semaines).
**Participants :** Toute l'équipe Scrum (PO + SM + Dev Team).

**Déroulé :**
1. Le PO présente les items prioritaires du Product Backlog
2. L'équipe sélectionne les items qu'elle peut réaliser (Sprint Backlog)
3. L'équipe définit un **Sprint Goal** (objectif du sprint, une phrase)
4. L'équipe décompose les items en tâches

**Sortie :** Sprint Backlog + Sprint Goal

### 3. Daily Scrum

**Quand :** Tous les jours, à la même heure.
**Durée :** Maximum 15 minutes.
**Participants :** L'équipe de développement (le SM peut assister, le PO est optionnel).

**Structure classique (3 questions) :**
1. Qu'est-ce que j'ai fait hier pour avancer vers le Sprint Goal ?
2. Que vais-je faire aujourd'hui ?
3. Y a-t-il des obstacles sur mon chemin ?

**Attention :** Le Daily Scrum n'est pas un rapport au management. C'est une synchronisation d'équipe.

### 4. Sprint Review

**Quand :** À la fin de chaque sprint.
**Durée :** Maximum 4 heures pour un sprint de 4 semaines.
**Participants :** Équipe Scrum + parties prenantes invitées.

**Déroulé :**
1. L'équipe démontre l'incrément réalisé (démo live, pas de slides !)
2. Les parties prenantes posent des questions et donnent du feedback
3. Le PO présente l'état du Product Backlog
4. Discussion sur les prochaines priorités

**Sortie :** Incrément validé, Product Backlog mis à jour.

### 5. Sprint Retrospective

**Quand :** Après la Sprint Review, avant le prochain Sprint Planning.
**Durée :** Maximum 3 heures pour un sprint de 4 semaines.
**Participants :** Équipe Scrum (les parties prenantes ne sont généralement pas invitées).

**Objectif :** Améliorer le processus de travail de l'équipe.

**Format classique Start/Stop/Continue :**
- **Start** : Que devrait-on commencer à faire ?
- **Stop** : Que devrait-on arrêter de faire ?
- **Continue** : Que fait-on bien et qu'on doit conserver ?

**Sortie :** Liste d'actions d'amélioration à mettre en place dès le prochain sprint.

---

## Les trois artefacts Scrum

### Product Backlog

Le Product Backlog est la **liste ordonnée de tout ce qui pourrait être fait** dans le produit. Il est la seule source de travail pour l'équipe Scrum.

**Caractéristiques :**
- Géré et priorisé par le Product Owner
- Jamais terminé — évolue constamment
- Les items en haut sont plus précis et plus petits
- Les items en bas sont plus vagues et plus grands (épics)

**Contenu typique :**
- User Stories
- Bugs
- Spikes (exploration technique)
- Améliorations non fonctionnelles (performance, sécurité)

**Refinement :** Activité de découpage et d'estimation des items du backlog. Pas un événement officiel Scrum, mais une pratique recommandée (environ 10% de la capacité de l'équipe).

### Sprint Backlog

Le Sprint Backlog est **l'ensemble des items sélectionnés pour le sprint** + le plan pour les réaliser.

**Caractéristiques :**
- Appartient à l'équipe de développement
- Mis à jour quotidiennement
- Peut être visualisé sur un board (colonnes : To Do / In Progress / Done)
- Sert à tracer le burndown chart

### Increment (Incrément)

L'incrément est **la somme de tous les items complétés** pendant le sprint + tous les sprints précédents. Il doit être utilisable et répondre à la Definition of Done.

**Definition of Done (DoD) :** Critères que tout incrément doit satisfaire pour être considéré "terminé". Exemple :
- Le code est mergé sur la branche principale
- Les tests unitaires passent
- La documentation technique est à jour
- Le pipeline CI/CD est vert
- Le PO a validé la fonctionnalité

---

## Schéma récapitulatif du cycle Scrum

```
Product Backlog
      │
      ▼
Sprint Planning ──────────────────────────────┐
      │                                        │
      ▼                                        │
Sprint Backlog                                 │
      │                                        │
      ▼                                        │
   SPRINT (1-4 semaines)                       │
   ┌────────────────────────────────────┐      │
   │  Daily Scrum (15 min/jour)         │      │
   │  ┌──────────────────────────────┐  │      │
   │  │  Dev → Test → Intégration    │  │      │
   │  └──────────────────────────────┘  │      │
   └────────────────────────────────────┘      │
      │                                        │
      ▼                                        │
  Incrément                                    │
      │                                        │
      ▼                                        │
Sprint Review ──► Feedback parties prenantes   │
      │                                        │
      ▼                                        │
Sprint Retrospective ──► Actions amélioration  │
      │                                        │
      └──────────────────── Sprint suivant ────┘
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un board Jira d'une équipe data en cours de sprint, avec les colonnes To Do / In Progress / In Review / Done et au moins 6-8 tickets répartis.
> **Expliquer :** Comment lire le board, ce que représente chaque colonne, comment l'équipe met à jour ses tickets au quotidien lors du Daily Scrum, et comment le SM identifie les blocages depuis ce board.

---

## Scrum en Data Engineering — adaptation pratique

| Événement Scrum | Adaptation data |
|----------------|-----------------|
| Sprint Planning | Sélectionner les pipelines à développer, les données à modéliser |
| Daily Scrum | "Mon job Airflow est en échec depuis hier, besoin d'aide" |
| Sprint Review | Démontrer le pipeline en live (Airflow → DWH → Dashboard) |
| Rétrospective | "Nos tests de qualité de données sont insuffisants" |

**Sprint Goal typique data :**
> "À la fin de ce sprint, les équipes commerciales peuvent consulter le chiffre d'affaires mensuel par région dans le dashboard."

---

## Résumé

| Composante | Éléments |
|-----------|---------|
| Rôles | Product Owner, Scrum Master, Dev Team |
| Événements | Sprint, Sprint Planning, Daily Scrum, Sprint Review, Rétrospective |
| Artefacts | Product Backlog, Sprint Backlog, Incrément |
| Durée sprint | 1 à 4 semaines (2 semaines recommandées) |
