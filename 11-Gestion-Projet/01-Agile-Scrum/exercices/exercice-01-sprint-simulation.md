# Exercice 01 — Simulation d'un Sprint Data Engineering

## Contexte

Vous êtes une équipe de data engineering chez **DataFlow SAS**, une PME spécialisée dans le e-commerce. L'entreprise souhaite construire une plateforme de données pour analyser ses ventes, suivre ses stocks et détecter les clients à risque de churn.

**Stack technique cible :**
- Sources : API e-commerce (REST), base MySQL legacy, exports CSV depuis l'ERP
- Ingestion : Python + Airflow
- Stockage : PostgreSQL (Data Warehouse)
- Transformation : dbt
- Visualisation : Metabase
- CI/CD : GitHub Actions

---

## Composition de l'équipe

| Rôle | Personne |
|------|---------|
| Product Owner | Marie (responsable marketing) |
| Scrum Master | Vous (ou désigné par le groupe) |
| Data Engineer | Participant A |
| Data Engineer | Participant B |
| Data Analyst | Participant C |

---

## Partie 1 — Rédaction du Product Backlog (30 min)

### Instructions

À partir des besoins ci-dessous, rédigez **8 à 10 User Stories** au format "En tant que / Je veux / Afin de" et ajoutez des critères d'acceptation à chacune.

### Besoins exprimés par Marie (PO)

> "Je voudrais que mes équipes puissent voir les ventes du jour en temps quasi-réel dans un dashboard. Il faut aussi qu'on puisse filtrer par catégorie de produit et par canal de vente (web, mobile, téléphone). Les données viennent de notre API e-commerce qui est mise à jour toutes les heures.
>
> En plus, on a des problèmes de stock : on ne sait jamais quand un produit va être en rupture. Il faudrait une alerte quand le stock passe en dessous d'un seuil.
>
> Et pour le churn, on a une liste de clients qui n'ont pas commandé depuis 6 mois. Je voudrais la recevoir chaque semaine par email pour que les commerciaux puissent les rappeler."

**Bonus :** identifiez 2 User Stories techniques (infrastructure, qualité des données) non exprimées par Marie mais nécessaires à l'équipe.

### Template à compléter

```
US-[XX] : [Titre court]

En tant que [utilisateur],
Je veux [fonctionnalité],
Afin de [bénéfice].

Critères d'acceptation :
AC1 : ...
AC2 : ...
AC3 : ...

Story Points : [1/2/3/5/8/13]
Priorité : [Haute/Moyenne/Basse]
```

---

## Partie 2 — Planning Poker (20 min)

### Instructions

1. Imprimez ou affichez les cartes Planning Poker (valeurs : 1, 2, 3, 5, 8, 13, 21, ? )
2. Le Scrum Master lit chaque User Story à voix haute
3. Le PO répond aux questions de clarification
4. L'équipe estime simultanément
5. Discussion si écart > 2x entre la plus haute et la plus basse estimation
6. Consensus sur chaque story

### Questions guide pour l'estimation

Pendant le Planning Poker, posez-vous ces questions :

- Combien de composantes techniques implique cette story ? (Airflow DAG, modèle dbt, dashboard Metabase...)
- Y a-t-il des incertitudes techniques ? (API non documentée, schéma de données inconnu...)
- Cette story a-t-elle des dépendances sur d'autres stories ?
- A-t-on déjà fait quelque chose de similaire ?

---

## Partie 3 — Sprint Planning (20 min)

### Contraintes

- Sprint de **2 semaines** (10 jours ouvrés)
- Capacité équipe : **3 data engineers × 8 jours = 24 jours-homme** (en tenant compte des jours de réunion et du refinement)
- Vélocité historique (simulée) : **22 story points**

### Instructions

1. Priorisez le backlog avec Marie (PO)
2. Sélectionnez les stories pour le Sprint 1 en respectant la vélocité
3. Rédigez un **Sprint Goal** en une phrase
4. Décomposez chaque story sélectionnée en **tâches techniques** (2-4h chacune)
5. Attribuez les tâches (ou laissez l'équipe se les approprier)

### Sprint Goal — guide de rédaction

Un bon Sprint Goal répond à la question : **"Quelle valeur métier sera disponible à la fin de ce sprint ?"**

```
Exemple de bons Sprint Goals :
✅ "Les équipes commerciales peuvent consulter les ventes du jour par canal depuis Metabase."
✅ "Les alertes de rupture de stock sont configurées et testées pour les 50 références prioritaires."

Exemples de mauvais Sprint Goals :
❌ "Terminer les US-01, US-02 et US-03."
❌ "Installer Airflow et créer les premiers DAGs."
```

### Tableau de Sprint Planning à remplir

```
Sprint 1 — Goal : _______________________________________________

Story     │ Points │ Tâches                          │ Assigné à
──────────┼────────┼─────────────────────────────────┼──────────
US-[XX]   │        │ 1. ____________________________  │
          │        │ 2. ____________________________  │
          │        │ 3. ____________________________  │
──────────┼────────┼─────────────────────────────────┼──────────
US-[XX]   │        │ 1. ____________________________  │
          │        │ 2. ____________________________  │
──────────┼────────┼─────────────────────────────────┼──────────
US-[XX]   │        │ 1. ____________________________  │
──────────┼────────┼─────────────────────────────────┼──────────
Total     │        │                                  │
```

---

## Partie 4 — Simulation du Daily Scrum (10 min)

### Scénario J4 du sprint

Le formateur lit les situations suivantes. Chaque participant joue son rôle et répond aux 3 questions du Daily.

**Situation Alice (Data Engineer) :**
> "J'ai configuré la connexion à l'API e-commerce et j'ai récupéré les premières données. Mais j'ai découvert que l'API ne renvoie que les commandes des 30 derniers jours — impossible de récupérer l'historique autrement qu'en CSV."

**Situation Bob (Data Engineer) :**
> "J'ai commencé le modèle dbt pour les ventes journalières. Tout va bien, mais je suis bloqué en attente de la table staging qu'Alice doit créer."

**Situation Carla (Data Analyst) :**
> "Je prépare les maquettes du dashboard Metabase avec Marie. On a identifié 3 métriques supplémentaires qu'elle souhaite — mais elles ne sont pas dans le backlog actuel."

**Questions à traiter :**
1. Que doit faire le Scrum Master face au blocage d'Alice ?
2. Comment gérer la dépendance Bob → Alice ?
3. Que faire des 3 nouvelles métriques demandées par Marie pendant le sprint ?

---

## Partie 5 — Rétrospective (25 min)

### Instructions

À la fin de la simulation, tenez une vraie rétrospective sur **l'exercice lui-même** (pas sur un sprint fictif).

**Format : Start / Stop / Continue**

Chaque participant écrit sur des post-its (physiques ou Miro/Klaxoon) :

- **Start :** Que devrait-on commencer à faire dans nos futures sessions ?
- **Stop :** Qu'est-ce qui ne fonctionnait pas dans cet exercice ?
- **Continue :** Qu'est-ce qui a bien fonctionné ?

**Étapes :**
1. 5 min : Écriture individuelle silencieuse
2. 5 min : Affichage et regroupement par thème
3. 5 min : Dot voting (3 votes par personne)
4. 10 min : Discussion sur les 2-3 sujets prioritaires
5. Définir 1 action concrète avant la prochaine session

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| User Stories bien formulées (format + valeur) | 4 pts |
| Critères d'acceptation clairs et testables | 3 pts |
| Sprint Goal exprimant une valeur métier | 2 pts |
| Tâches techniques cohérentes et suffisamment fines | 3 pts |
| Participation active au Daily et à la rétro | 3 pts |
| Gestion des imprévus (Alice, Bob, Carla) | 5 pts |
| **Total** | **20 pts** |

---

## Livrables attendus

À rendre à l'issue de l'exercice :

1. Le Product Backlog complet (8-10 stories avec critères d'acceptation et estimations)
2. Le Sprint Backlog du Sprint 1 (stories sélectionnées + tâches décomposées)
3. Le Sprint Goal rédigé
4. Les réponses aux questions du Daily Scrum (gestion des blocages et imprévus)
5. Les actions issues de la rétrospective

---

## Ressources utiles

- [Planning Poker en ligne](https://planningpokeronline.com)
- [Template Miro Rétrospective Start/Stop/Continue](https://miro.com/templates/start-stop-continue-retrospective/)
- [Jira — Créer un sprint gratuit](https://www.atlassian.com/fr/software/jira)
- [Template User Story — Atlassian](https://www.atlassian.com/fr/agile/project-management/user-stories)
