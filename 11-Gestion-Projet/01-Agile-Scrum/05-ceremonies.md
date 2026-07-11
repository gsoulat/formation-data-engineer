# Les Cérémonies Scrum

## Vue d'ensemble

Les cérémonies (ou événements) Scrum sont des **moments formels de synchronisation et d'inspection**. Ils ne sont pas optionnels — chaque cérémonie a un objectif précis et une durée maximale (timebox).

| Cérémonie | Quand | Timebox (sprint 2 semaines) | Participants |
|-----------|-------|---------------------------|--------------|
| Sprint Planning | Début de sprint | 4 heures | PO + SM + Dev Team |
| Daily Scrum | Chaque jour | 15 minutes | Dev Team (SM optionnel) |
| Sprint Review | Fin de sprint | 2 heures | Équipe + parties prenantes |
| Sprint Retrospective | Après la review | 1h30 | Équipe Scrum |

*(voir le module 04 pour le Sprint Planning — il est couvert en détail avec le backlog)*

---

## Le Daily Scrum (Mêlée Quotidienne)

### Objectif

Le Daily Scrum est une **synchronisation de l'équipe de développement** pour inspecter la progression vers le Sprint Goal et adapter le plan si nécessaire.

Ce n'est PAS :
- Un rapport de statut pour le management
- Une réunion de résolution de problèmes
- Un moment pour le PO d'assigner du travail

### Déroulé

**Format classique — 3 questions (5 min/personne max) :**

```
1. Qu'est-ce que j'ai accompli hier qui aide à atteindre le Sprint Goal ?
2. Que vais-je faire aujourd'hui pour contribuer au Sprint Goal ?
3. Y a-t-il des obstacles sur mon chemin ?
```

**Format moderne — orienté objectifs :**

Certaines équipes préfèrent une structure moins rigide :
- "Voici où j'en suis sur ma tâche..."
- "J'ai besoin d'aide sur..."
- "Attention, j'ai découvert que..."

**Règles de base :**
- Même heure, même endroit chaque jour
- Debout (stand-up) pour maintenir la brièveté
- 15 minutes maximum, sans exception
- Si un sujet nécessite une discussion approfondie → "parking lot" (discussion après le Daily, entre les personnes concernées)

### Exemple — Équipe data engineering

```
Daily Scrum — Sprint 2, Jour 4 — 9h00

Alice :
"Hier j'ai terminé le DAG Airflow pour l'ingestion CRM, les tests passent
en local. Aujourd'hui je configure le déploiement sur l'environnement staging.
J'ai un blocage : je n'ai pas encore les credentials de prod pour l'API Salesforce."

Bob :
"Hier j'ai finalisé le modèle dbt pour les ventes journalières.
Aujourd'hui je branche le dashboard Metabase sur les nouvelles tables.
Rien à signaler."

Carla :
"Hier j'ai rencontré un souci : les données de janvier ont des nulls
sur le champ montant_ht. Aujourd'hui je valide avec le PO si c'est
une anomalie ou des données légitimes. C'est potentiellement un blocage
pour l'US-02."

Scrum Master :
"Alice, je prends en charge la récupération des credentials — je contacte
l'infra ce matin.
Carla, voyons ça avec Thomas (PO) juste après le Daily."
```

### Impediments courants en data

| Impediment | Exemple | Action SM |
|-----------|---------|-----------|
| Accès aux données | "Je n'ai pas accès à la base de prod" | Contacter la DSI, escalade si besoin |
| Dépendance externe | "L'API partenaire est down" | Identifier un plan B, prévenir le PO |
| Ambiguïté métier | "Je ne sais pas quelle formule de CA utiliser" | Planifier une discussion PO + dev |
| Environnement cassé | "Le cluster Spark ne répond plus depuis hier" | Contacter l'équipe infra immédiatement |
| Conflit de priorités | "Mon manager me demande de traiter une urgence" | Discussion SM + manager pour protéger le sprint |

---

## La Sprint Review

### Objectif

La Sprint Review est une **démonstration de l'incrément réalisé** aux parties prenantes, suivie d'une discussion sur les prochaines priorités. C'est un moment d'inspection et d'adaptation du Product Backlog.

**Ce n'est PAS :**
- Une réunion de validation formelle
- Un événement de présentation PowerPoint
- Un moment de jugement de l'équipe

### Participants

- **Équipe Scrum** (PO, SM, Dev Team)
- **Parties prenantes invitées** : clients, utilisateurs métier, management, autres équipes

La liste des invités est gérée par le PO. Tout le monde peut être invité — y compris des partenaires externes si pertinent.

### Déroulé

```
1. Introduction (5 min)
   └── PO rappelle le Sprint Goal et les items sélectionnés

2. Démo de l'incrément (40-60 min)
   └── L'équipe démontre chaque User Story terminée
   └── Démo LIVE sur l'environnement de staging (jamais de captures d'écran !)
   └── Les parties prenantes peuvent interagir

3. Discussion et feedback (20-30 min)
   └── Questions des parties prenantes
   └── Feedback intégré au Product Backlog
   └── Discussion sur les prochaines priorités

4. État du backlog (10 min)
   └── PO présente les prochains items prioritaires
   └── Ajustements suite au feedback
```

### Règles d'or de la Sprint Review

**Montrer uniquement ce qui répond à la Definition of Done.** Une fonctionnalité "à 90%" n'est pas démontrée — elle sera dans le prochain sprint.

**Démo live, pas de slides.** Un rapport dans Metabase, un pipeline Airflow qui tourne, une API qui répond — le travail réel, pas une présentation.

**Le feedback est un cadeau.** Si une partie prenante dit "ce n'est pas ce que je voulais", c'est précieux — mieux vaut l'apprendre maintenant qu'en phase de recette finale.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une Sprint Review en cours : un data engineer partage son écran et montre un dashboard Metabase ou un DAG Airflow fonctionnel à une salle de parties prenantes (ou en visio).
> **Expliquer :** La différence entre une démo live et une présentation, comment le PO recueille le feedback et comment ce feedback est transformé en items de backlog ou en modifications de priorité.

---

## La Sprint Retrospective

### Objectif

La rétrospective est le moment où **l'équipe s'améliore elle-même**. Elle inspecte son processus de travail, ses interactions et ses pratiques, puis décide d'actions concrètes pour le prochain sprint.

### Pourquoi c'est essentiel

La rétrospective est souvent la première cérémonie supprimée quand l'équipe est sous pression. C'est une erreur grave : c'est précisément dans les moments difficiles qu'il faut s'améliorer.

> "Si vous n'avez pas le temps de faire une rétrospective, vous n'avez pas le temps de ne pas en faire."

### Format Start / Stop / Continue

C'est le format le plus simple et le plus utilisé.

```
┌─────────────────────────────────────────────────────────┐
│                    RÉTROSPECTIVE SPRINT 2                │
├─────────────────┬───────────────────┬───────────────────┤
│   START         │      STOP         │    CONTINUE       │
│ (commencer à    │ (arrêter de       │ (continuer à      │
│  faire)         │  faire)           │  faire)           │
├─────────────────┼───────────────────┼───────────────────┤
│ Écrire les      │ Merger sans       │ Daily à 9h debout │
│ tests avant le  │ review de code    │                   │
│ code (TDD)      │                   │ Partage de        │
│                 │ Découvrir les     │ documentation     │
│ Documenter les  │ schémas de        │ technique         │
│ schémas de      │ données trop tard │                   │
│ données en      │                   │ Alertes Slack     │
│ début de sprint │ Sous-estimer les  │ pour les          │
│                 │ stories liées     │ pipelines         │
│ Code review     │ à l'infra         │                   │
│ en binôme       │                   │                   │
└─────────────────┴───────────────────┴───────────────────┘
```

### Autres formats de rétrospective

**4L — Liked / Learned / Lacked / Longed For**
- **Liked :** Ce que j'ai aimé dans ce sprint
- **Learned :** Ce que j'ai appris
- **Lacked :** Ce qui manquait
- **Longed for :** Ce que j'aurais voulu avoir

**Mad / Sad / Glad**
- **Mad :** Ce qui m'a mis en colère / frustré
- **Sad :** Ce qui m'a déçu
- **Glad :** Ce qui m'a rendu heureux

**La timeline du sprint**
L'équipe reconstruit chronologiquement le sprint sur un tableau blanc et note les événements positifs (au-dessus de la ligne) et négatifs (en dessous). Utile pour identifier les patterns.

**Sailboat (Voilier)**
- **Vent (ce qui nous fait avancer)** : bonnes pratiques à conserver
- **Ancre (ce qui nous ralentit)** : impediments, dettes techniques
- **Rochers (risques)** : dangers à venir
- **Soleil (ce vers quoi on va)** : objectif long terme

### Déroulé d'une rétrospective

```
1. Set the stage (5 min)
   └── Ice breaker ou question d'ouverture
   └── Rappel de l'accord de confidentialité ("Vegas rule")
   └── Prime directive : "Chacun a fait de son mieux avec ce qu'il savait"

2. Collecte des données (10-15 min)
   └── Chaque membre écrit sur des post-its (ou outil numérique)
   └── Affichage sur le board sans discussion

3. Regroupement et vote (10 min)
   └── Regrouper les post-its similaires en thèmes
   └── Dot voting pour prioriser les sujets

4. Discussion (20-30 min)
   └── Approfondir les sujets prioritaires
   └── Comprendre les causes racines (5 Pourquoi)

5. Décisions et actions (10 min)
   └── Définir 2-3 actions concrètes maximum
   └── Chaque action a un responsable et une deadline
   └── Revu au début de la prochaine rétrospective

6. Clôture (5 min)
   └── ROTI (Return On Time Invested) — vote de 1 à 5
```

### Exemple d'actions issues d'une rétro data

```
Actions Sprint 3 — issu de la rétro Sprint 2

Action 1 : Tests de qualité de données systématiques
  Responsable : Bob
  Quand : Dès le premier ticket de Sprint 3
  Comment : Ajouter des tests dbt (not_null, unique, range) pour chaque nouveau modèle

Action 2 : Documentation des schémas en début de sprint
  Responsable : Toute l'équipe
  Quand : Sprint Planning de Sprint 3
  Comment : Créer une page Confluence "Schéma des sources" avant le premier commit

Action 3 : Code review obligatoire avant merge
  Responsable : Carla (met en place la règle sur GitHub)
  Quand : Avant J1 de Sprint 3
  Comment : Configurer la branche protection rule sur GitHub (1 reviewer obligatoire)
```

---

## La Definition of Done (DoD)

### Qu'est-ce que c'est ?

La Definition of Done est une **liste de critères que tout incrément doit satisfaire** pour être considéré comme "terminé". Elle est définie par l'équipe et s'applique à toutes les User Stories.

**La DoD n'est pas** :
- Les critères d'acceptation d'une story (qui varient selon la story)
- Un checklist bureaucratique
- Quelque chose que le PO définit seul

### Exemple de DoD — Équipe Data Engineering

```
Definition of Done — Équipe Data Platform
Version 1.2 — Mise à jour Sprint 5

Une User Story est "Done" quand :

Code & Qualité
☑ Code soumis en Pull Request et approuvé par au moins 1 reviewer
☑ Pas de conflits de merge
☑ Le pipeline CI/CD est vert (tests, linting, sécurité)
☑ Tests unitaires écrits et passants (couverture ≥ 80%)
☑ Pas de secrets hardcodés dans le code

Data Engineering
☑ Schéma de données documenté (source, destination, transformations)
☑ Tests de qualité dbt ajoutés (not_null, unique, accepted_values)
☑ Idempotence vérifiée pour les pipelines batch
☑ Alertes configurées en cas d'échec

Documentation
☑ README mis à jour si nécessaire
☑ Changelog mis à jour
☑ Critères d'acceptation vérifiés et validés par le PO

Déploiement
☑ Déployé sur l'environnement de staging
☑ Testé manuellement sur staging
☑ Prêt pour le déploiement en production (peut nécessiter une validation séparée)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un board de rétrospective sur Miro ou FunRetro avec des post-its répartis dans les colonnes Start/Stop/Continue, et le résultat du dot voting pour prioriser les actions.
> **Expliquer :** Comment animer la rétrospective de façon sécurisante (la prime directive, la règle de confidentialité), comment les post-its sont regroupés en thèmes, et comment on transforme les constats en actions concrètes et mesurables.

---

## Résumé des cérémonies

| Cérémonie | Objectif principal | Output |
|-----------|-------------------|--------|
| Sprint Planning | Planifier le sprint | Sprint Backlog + Sprint Goal |
| Daily Scrum | Synchroniser l'équipe | Plan du jour + impediments identifiés |
| Sprint Review | Inspecter l'incrément | Feedback intégré au backlog |
| Rétrospective | Améliorer le processus | Actions d'amélioration concrètes |

**Règle d'or :** Aucune cérémonie n'est optionnelle. Toutes contribuent à l'inspection et à l'adaptation qui font la force d'Agile.
