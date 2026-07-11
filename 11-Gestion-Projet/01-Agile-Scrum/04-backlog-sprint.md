# Backlog et Sprint Planning

## Le Product Backlog

### Définition

Le Product Backlog est la **liste vivante et ordonnée de tout ce qui pourrait être réalisé** dans le produit. C'est la seule source d'entrée pour le travail de l'équipe Scrum. Il appartient au Product Owner.

**"Vivante"** signifie que le backlog évolue constamment :
- Nouvelles User Stories ajoutées quand les besoins émergent
- Stories modifiées quand les priorités changent
- Stories supprimées quand elles ne sont plus pertinentes
- Stories estimées et découpées lors du refinement

### Structure du Product Backlog

```
Product Backlog — Plateforme Data
─────────────────────────────────────────────────────────────────
Priorité │ ID    │ Titre                            │ Points │ Status
─────────────────────────────────────────────────────────────────
   1     │ US-01 │ Ingestion données CRM (nuit)     │  5     │ Prêt
   2     │ US-02 │ Dashboard ventes journalier       │  8     │ Prêt
   3     │ US-03 │ Alertes Slack pipeline échec      │  3     │ Prêt
   4     │ US-04 │ Export CSV des rapports           │  2     │ Prêt
   5     │ US-05 │ Filtre par région sur dashboard   │  3     │ Raffinement
   6     │ US-06 │ Rapport hebdomadaire email        │  5     │ Raffinement
   7     │ US-07 │ Chiffrement données au repos      │  8     │ À raffiner
   8     │ US-08 │ Connexion SSO entreprise          │ 13     │ À raffiner
   9     │ US-09 │ Intégration Salesforce v2         │ ???    │ À définir
  10     │ EP-01 │ [EPIC] Module prédiction churn    │ ???    │ À définir
─────────────────────────────────────────────────────────────────
```

**Observation :** Plus on descend dans le backlog, plus les items sont vagues et plus grands. C'est normal — on ne raffine pas ce qui ne sera peut-être jamais fait.

### Statuts d'un item

| Statut | Description |
|--------|-------------|
| À définir | Idée brute, pas encore formulée en User Story |
| À raffiner | Formulée mais pas encore estimée ni découpée |
| Raffinement | En cours d'affinage (séance de refinement) |
| Prêt (Ready) | Estimée, découpée, critères d'acceptation clairs |
| En cours | Sélectionnée dans le Sprint Backlog |
| Terminée (Done) | Satisfait la Definition of Done |

---

## Le Refinement (Backlog Grooming)

Le refinement est l'activité de **découpage et d'estimation des items** du Product Backlog. Ce n'est pas un événement officiel Scrum mais une pratique essentielle.

**Quand :** 1 à 2 fois par sprint, en milieu de sprint (prépare le prochain sprint planning).
**Durée :** 1 à 2 heures.
**Participants :** PO + Dev Team (le SM facilite).
**Règle de base :** Ne pas consacrer plus de 10% de la vélocité au refinement.

**Activités du refinement :**
1. Le PO présente les prochains items prioritaires
2. L'équipe pose des questions de clarification
3. Découpage des épics en User Stories
4. Estimation (Planning Poker)
5. Définition des critères d'acceptation

**Un item est "Prêt" quand (critère READY) :**
- La User Story est formulée clairement
- Les critères d'acceptation sont définis et testables
- L'item est assez petit pour tenir dans un sprint
- Les dépendances sont identifiées
- L'équipe peut l'estimer

---

## Le Sprint Planning

### Objectif

Le Sprint Planning répond à deux questions fondamentales :
1. **Pourquoi** ce sprint ? → Sprint Goal
2. **Quoi** livrer ? → Sprint Backlog
3. **Comment** le faire ? → Plan de tâches

### Déroulé en deux parties

**Partie 1 — Qu'allons-nous livrer ? (1-2h)**

1. Le PO présente le contexte business et les priorités
2. L'équipe examine les items "Prêts" en haut du backlog
3. L'équipe sélectionne les items qu'elle peut réaliser (en fonction de sa vélocité et sa capacité)
4. Le Sprint Goal est défini collectivement

**Partie 2 — Comment allons-nous le faire ? (1-2h)**

1. L'équipe décompose chaque User Story en tâches (issues ou sous-tâches Jira)
2. Chaque tâche est estimée en heures (optionnel)
3. Les membres de l'équipe s'approprient les tâches (ou le font au fur et à mesure du sprint)

### Le Sprint Goal

Le Sprint Goal est une **phrase qui exprime la valeur que ce sprint va apporter**. Il guide les décisions de l'équipe quand des imprévus surviennent.

**Exemples de Sprint Goals :**

```
Sprint 1 : "Les ingénieurs data peuvent surveiller l'état de tous les pipelines
depuis un seul dashboard."

Sprint 2 : "Les data analysts disposent des ventes journalières du CRM
dans le Data Warehouse avant 8h chaque matin."

Sprint 3 : "L'équipe commerciale peut filtrer les rapports de ventes
par région, produit et période depuis le dashboard."
```

**Un mauvais Sprint Goal :**
> "Terminer les US-01, US-02, US-03."

→ Trop orienté liste de tâches, pas de valeur exprimée.

---

## La vélocité

### Définition

La vélocité est le **nombre moyen de story points** réalisés par l'équipe par sprint. Elle se stabilise après 3-5 sprints.

**Calcul :**
```
Vélocité sprint 1 : 18 points
Vélocité sprint 2 : 22 points
Vélocité sprint 3 : 20 points
Vélocité sprint 4 : 21 points
─────────────────────────────
Vélocité moyenne  : 20.25 ≈ 20 points/sprint
```

### Utilisation de la vélocité

**Pour planifier :** Si la vélocité est de 20 points, l'équipe sélectionne des items totalisant environ 20 points lors du Sprint Planning.

**Pour prévoir :** Si le backlog contient 120 story points et que la vélocité est de 20, on peut estimer 6 sprints de 2 semaines = environ 3 mois.

**Attention — erreurs fréquentes :**
- Comparer les vélocités entre équipes (les points ne sont pas universels)
- Pousser l'équipe à augmenter sa vélocité (le but est la valeur, pas les points)
- Utiliser la vélocité comme mesure de performance individuelle
- Planifier au maximum de capacité (garder une marge pour les imprévus)

### Capacité vs Vélocité

La **capacité** est le temps disponible de l'équipe pour le sprint.

```
Sprint de 2 semaines = 10 jours ouvrés

Membre    │ Jours dispo │ Notes
──────────────────────────────────────────
Alice     │     8       │ 2 jours congés
Bob       │    10       │ Disponible à 100%
Carla     │     7       │ Partage avec autre projet (30%)
──────────────────────────────────────────
Capacité  │    25 jours │
```

Si historiquement l'équipe produit 20 points avec 30 jours de capacité, un sprint à 25 jours donnera approximativement 17 points.

---

## Le Sprint Backlog

### Structure

```
Sprint 2 — "Ventes journalières CRM disponibles à 8h"
═══════════════════════════════════════════════════════

US-01 : Ingestion données CRM (5 pts) — Alice
├── Configurer la connexion API Salesforce (2h)
├── Écrire le DAG Airflow d'extraction (3h)
├── Créer les tables landing dans le Data Lake (2h)
├── Tester l'idempotence du pipeline (2h)
└── Rédiger la documentation du DAG (1h)

US-02 : Dashboard ventes journalier (8 pts) — Bob + Carla
├── Concevoir le modèle de données dbt (3h)
├── Créer les tables de faits et dimensions (3h)
├── Développer la vue dbt agrégée par jour (2h)
├── Connecter le dashboard Metabase (2h)
└── Tester avec les data analysts (2h)

US-03 : Alertes Slack pipeline échec (3 pts) — Alice
├── Configurer le webhook Slack (1h)
├── Ajouter les callbacks Airflow on_failure (1h)
└── Tester les alertes sur environnement staging (1h)

───────────────────────────────────────────────
Total : 16 story points / Capacité 25 jours
```

---

## Le Burndown Chart

### Qu'est-ce que c'est ?

Le burndown chart est un graphique qui montre **le travail restant** (en story points ou en tâches) au fil des jours du sprint.

**Axe X :** Jours du sprint (ex: J1 à J10 pour un sprint de 2 semaines)
**Axe Y :** Points restants

### Lecture du burndown

```
Points restants
30 |●
   |  ·
25 |    ●         ← Ligne idéale (tirets)
   |      ·
20 |        ●
   |          ·
15 |            ·
   |              ●  ←  Avancement réel (ronds)
10 |                ·
   |                  ·  ●
 5 |                        ·
   |                          ●   ●
 0 |_________________________________
    J1  J2  J3  J4  J5  J6  J7  J8  J9  J10
```

**Interprétations :**
- **Courbe au-dessus de l'idéale :** L'équipe est en retard
- **Courbe en dessous de l'idéale :** L'équipe avance plus vite que prévu (ou sous-estimation)
- **Plateau :** Travail non complété pendant 1-2 jours (bloquer = contacter le SM)
- **Ligne qui monte :** De nouvelles tâches ont été ajoutées au sprint (à éviter !)

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un burndown chart dans Jira pour un sprint de 2 semaines, idéalement avec un léger retard mid-sprint puis un rattrapage en fin de sprint.
> **Expliquer :** Comment lire la courbe idéale vs réelle, ce que signifie un plateau (blocage), pourquoi la courbe peut monter (scope creep), et comment le SM utilise ce graphique pour intervenir rapidement.

---

## Velocity Chart et Release Planning

### Velocity Chart

Le velocity chart montre la vélocité sprint après sprint. Il permet d'identifier les tendances.

```
Story Points
30 |         █
25 |   █     █     █
20 | █ █   █ █   █ █ █
15 | █ █ █ █ █   █ █ █ █
   |_________________________
     S1 S2 S3 S4 S5 S6 S7 S8
```

### Release Planning

Avec la vélocité stabilisée, on peut planifier une release :

```
Backlog restant : 80 story points
Vélocité moyenne : 20 points/sprint
Sprints nécessaires : 80 / 20 = 4 sprints
Durée sprint : 2 semaines
Livraison estimée : 8 semaines = fin du mois M+2
```

**Important :** C'est une estimation, pas un engagement. La vélocité peut varier.

---

## Résumé

| Concept | Description |
|---------|-------------|
| Product Backlog | Liste ordonnée et vivante de tout le travail à faire |
| Refinement | Affinage, découpage et estimation des items |
| Sprint Planning | Sélection des items + Sprint Goal + plan d'exécution |
| Sprint Backlog | Items sélectionnés + tâches décomposées |
| Vélocité | Moyenne de story points réalisés par sprint |
| Burndown Chart | Visualisation du travail restant dans le sprint |
