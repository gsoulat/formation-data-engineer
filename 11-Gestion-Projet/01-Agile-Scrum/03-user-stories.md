# User Stories

## Qu'est-ce qu'une User Story ?

Une **User Story** (histoire utilisateur) est une description courte d'une fonctionnalité du point de vue de l'utilisateur final. Elle capture **qui veut quoi et pourquoi**, sans entrer dans le détail technique de la mise en œuvre.

L'objectif n'est pas de remplacer les spécifications — c'est de **déclencher une conversation** entre le Product Owner, l'équipe de développement et les utilisateurs.

> "Une User Story est un rappel de conversation à avoir, pas une spécification à suivre."
> — Ron Jeffries (co-auteur d'XP et Agile)

---

## Le format standard

### Structure "En tant que... Je veux... Afin de..."

```
En tant que [type d'utilisateur],
Je veux [action / fonctionnalité],
Afin de [bénéfice / valeur métier].
```

**Exemples Data Engineering :**

```
En tant que data analyst,
Je veux accéder à un rapport de ventes journalier mis à jour à 8h,
Afin de préparer mes recommandations avant les réunions matinales.
```

```
En tant qu'ingénieur data,
Je veux recevoir une alerte Slack quand un pipeline Airflow échoue,
Afin de réagir rapidement sans avoir à surveiller l'interface en permanence.
```

```
En tant que directeur commercial,
Je veux visualiser le chiffre d'affaires par région sur les 12 derniers mois,
Afin de comparer les performances et identifier les marchés à développer.
```

```
En tant qu'administrateur système,
Je veux que les données sensibles soient chiffrées au repos dans le Data Warehouse,
Afin de garantir la conformité RGPD et protéger les données clients.
```

---

## Les critères d'acceptation

Les critères d'acceptation (Acceptance Criteria, AC) définissent **les conditions qui doivent être satisfaites pour que la User Story soit considérée comme terminée**.

### Format Given / When / Then (Gherkin)

```
Étant donné que [contexte initial],
Quand [action de l'utilisateur],
Alors [résultat attendu].
```

**Exemple :**

```
User Story : En tant que data analyst, je veux accéder à un rapport
de ventes journalier mis à jour à 8h, afin de préparer mes recommandations.

Critères d'acceptation :

AC1 — Disponibilité du rapport
  Étant donné que le pipeline de données nocturne s'est exécuté avec succès,
  Quand j'accède au dashboard à 8h05,
  Alors les données du jour précédent sont disponibles et complètes.

AC2 — Fraîcheur des données
  Étant donné que le pipeline a terminé son exécution,
  Quand je consulte l'horodatage de la dernière mise à jour,
  Alors l'horodatage affiche une heure comprise entre 7h30 et 8h00.

AC3 — Gestion de l'échec
  Étant donné que le pipeline a échoué pendant la nuit,
  Quand j'accède au dashboard,
  Alors un bandeau d'avertissement indique que les données ne sont pas à jour
  et affiche la date de la dernière mise à jour réussie.
```

### Format liste (moins formel, plus rapide)

```
User Story : En tant qu'ingénieur data, je veux recevoir une alerte Slack
quand un pipeline échoue.

Critères d'acceptation :
✅ Une notification Slack est envoyée dans le canal #data-alerts en moins de 5 minutes
   après l'échec du pipeline.
✅ La notification contient : nom du DAG, heure de l'échec, message d'erreur (100 premiers caractères).
✅ En cas de réussite après un échec, une notification de résolution est également envoyée.
✅ Les alertes peuvent être configurées par pipeline (certains pipelines ne déclenchent pas d'alerte).
```

---

## Le critère INVEST

INVEST est un acronyme qui définit les caractéristiques d'une **bonne User Story**.

### I — Indépendante (Independent)

Chaque User Story doit pouvoir être développée sans dépendre d'une autre. Les dépendances créent des goulots d'étranglement.

**Mauvais exemple :**
- US1 : "En tant qu'utilisateur, je veux me connecter" (dépend de la création de compte)
- US2 : "En tant qu'utilisateur, je veux créer un compte" (dépend du système d'auth)

**Bonne pratique :** Reformuler pour rendre indépendantes, ou regrouper en une seule epic.

### N — Négociable (Negotiable)

Une User Story n'est pas un contrat. Les détails sont négociables jusqu'au sprint planning.

**Ce qui est négociable :** l'interface, le format des données, la fréquence de mise à jour.
**Ce qui ne l'est pas :** la valeur métier (le "afin de").

### V — Valeur (Valuable)

Chaque User Story doit apporter une valeur directe à l'utilisateur final ou au client.

**Mauvais exemple :** "En tant que data engineer, je veux refactoriser le pipeline ETL" → technique, pas de valeur directe visible par l'utilisateur.

**Mieux :** "En tant que data analyst, je veux que les rapports se chargent en moins de 3 secondes, afin de pouvoir naviguer rapidement entre les vues." (la refactorisation est la solution technique, pas la story).

### E — Estimable (Estimable)

L'équipe doit pouvoir estimer l'effort nécessaire. Si ce n'est pas possible, c'est que la story est trop vague ou trop complexe.

**Quand une story n'est pas estimable :**
- Trop de zones d'ombre techniques → faire un spike (exploration technique)
- Trop grande → découper en stories plus petites

### S — Petite (Small)

Une User Story doit être réalisable en une seule itération (sprint). En pratique : moins de 8 story points, réalisable par 1 à 2 personnes en quelques jours.

**Épic vs User Story :**
- **Épic** : grande fonctionnalité qui ne tient pas dans un sprint ("Créer un Data Warehouse")
- **User Story** : petit incrément de valeur réalisable en quelques jours ("Ingérer les données de ventes depuis le CRM")

### T — Testable (Testable)

On doit pouvoir tester si la story est terminée. Les critères d'acceptation servent précisément à ça.

**Non testable :** "En tant qu'utilisateur, je veux une application rapide."
**Testable :** "En tant qu'utilisateur, je veux que la page de rapport se charge en moins de 2 secondes sur une connexion standard."

---

## Story Points et estimation

### Qu'est-ce qu'un story point ?

Un story point est une **unité relative d'effort** qui prend en compte :
- La **complexité** de la tâche
- Le **volume** de travail
- L'**incertitude** et le risque

Les story points ne sont PAS des heures. Ils permettent de comparer les stories entre elles.

### La suite de Fibonacci

L'estimation utilise généralement la suite de Fibonacci : **1, 2, 3, 5, 8, 13, 21**.

Pourquoi Fibonacci ? L'écart entre les valeurs augmente — on ne peut pas estimer précisément la différence entre 11 et 12 story points, mais on sait distinguer 8 de 13.

| Story Points | Interprétation |
|-------------|----------------|
| 1 | Trivial, bien compris |
| 2 | Simple avec quelques étapes |
| 3 | Clairement défini, effort modéré |
| 5 | Effort important, quelques incertitudes |
| 8 | Complexe, multiples composantes |
| 13 | Très complexe, à découper |
| 21 | Épic — doit être découpée |

### Planning Poker

Le Planning Poker est la technique d'estimation la plus courante en Scrum.

**Déroulé :**
1. Le PO lit la User Story et répond aux questions
2. Chaque membre de l'équipe choisit secrètement une carte (1, 2, 3, 5, 8, 13, 21...)
3. Tous révèlent leur carte simultanément
4. Si les estimations divergent (ex: 3 vs 13), discussion entre les extrêmes
5. Nouvelle estimation jusqu'au consensus

**Règle clé :** les désaccords sont révélateurs. Un développeur qui estime 13 a peut-être vu un risque que les autres n'ont pas identifié.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une session de Planning Poker en ligne (ex: planningpokeronline.com ou Jira Planning Poker) avec une User Story affichée et des participants en train d'estimer.
> **Expliquer :** Comment fonctionne la synchronisation (tous révèlent en même temps), pourquoi les divergences d'estimation sont utiles (révèlent des risques ou des incompréhensions), et comment le consensus est atteint.

---

## Épics, Features et Stories

```
Épic : Créer un tableau de bord de suivi des ventes
├── Feature : Rapport de ventes
│   ├── US : Afficher les ventes du jour
│   ├── US : Filtrer par région
│   └── US : Exporter en CSV
├── Feature : Alertes et notifications
│   ├── US : Alerter sur un seuil de CA quotidien
│   └── US : Rapport hebdomadaire automatique par email
└── Feature : Gestion des droits
    ├── US : Restreindre l'accès par région
    └── US : Rôles lecteur / éditeur / admin
```

---

## Exemples complets — contexte Data Engineering

### User Story avec contexte data pipeline

```
Titre : Ingestion données CRM vers Data Warehouse

En tant qu'ingénieur data,
Je veux qu'un pipeline automatisé extraie les données clients du CRM Salesforce
toutes les nuits à 2h du matin,
Afin que les analyses marketing soient basées sur des données fraîches le matin.

Story Points : 5

Critères d'acceptation :
✅ Le DAG Airflow s'exécute chaque nuit à 2h00 UTC
✅ Les données sont extraites depuis l'API Salesforce (contacts, opportunités, comptes)
✅ Les données brutes sont stockées dans la zone landing du Data Lake (S3/Bronze)
✅ Un log d'exécution est conservé (nombre d'enregistrements, durée, statut)
✅ En cas d'échec, une alerte est envoyée dans #data-alerts
✅ Les runs idempotents : relancer le DAG ne crée pas de doublons

Definition of Done :
☑ Code versionné dans Git avec PR review
☑ Tests unitaires sur la logique de transformation
☑ Documentation du DAG dans le README
☑ Pipeline testé sur l'environnement de staging
```

---

## Anti-patterns courants

| Anti-pattern | Problème | Solution |
|-------------|---------|----------|
| Story orientée tâche technique | "Migrer la BDD vers PostgreSQL" | Reformuler en valeur : "En tant qu'utilisateur, je veux des requêtes en moins de 1 seconde..." |
| Story trop grande | 40 story points | Découper en plusieurs stories indépendantes |
| Pas de critères d'acceptation | "En tant qu'admin, je veux gérer les utilisateurs" | Préciser : créer, modifier, désactiver, lister |
| Story technique sans utilisateur | "En tant que système, je veux..." | Identifier le vrai utilisateur humain |
| Critères non testables | "Le système doit être performant" | Préciser : "< 200ms pour 95% des requêtes" |

---

## Résumé

- Une User Story capture une valeur utilisateur, pas une tâche technique
- Format : **En tant que / Je veux / Afin de**
- Les **critères d'acceptation** définissent quand la story est terminée
- **INVEST** : Indépendante, Négociable, Valeur, Estimable, Petite, Testable
- Les **story points** mesurent l'effort relatif (pas des heures)
- Le **Planning Poker** aligne l'équipe et révèle les risques cachés
