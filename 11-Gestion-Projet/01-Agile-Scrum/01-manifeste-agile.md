# Le Manifeste Agile

## Introduction

En 2001, dix-sept experts du développement logiciel se réunissent à Snowbird, dans l'Utah. Frustrés par les lourdeurs des méthodes traditionnelles de gestion de projet, ils publient le **Manifeste pour le développement Agile de logiciels**. Ce document de quelques paragraphes va transformer durablement l'industrie.

Le Manifeste ne prescrit pas une méthode. Il énonce des **valeurs** et des **principes** qui guident la façon de penser et d'agir dans un projet.

---

## Les quatre valeurs Agile

Le Manifeste pose quatre comparaisons. Dans chaque cas, les deux éléments ont de la valeur, mais le premier est **privilégié** sur le second.

### 1. Les individus et leurs interactions **plutôt que** les processus et les outils

Les processus et les outils sont utiles. Mais ce sont les personnes qui font avancer un projet. Une équipe soudée, qui communique bien, surpassera toujours une équipe qui suit scrupuleusement un processus mais ne se parle pas.

**Conséquence pratique :** privilégier les discussions directes (daily standup, pair programming) sur les tickets Jira ou les emails.

### 2. Des logiciels opérationnels **plutôt que** une documentation exhaustive

La documentation est nécessaire. Mais un logiciel qui fonctionne apporte plus de valeur qu'un dossier de spécifications de 200 pages. La documentation doit servir l'équipe, pas la paralyser.

**Conséquence pratique :** livrer un incrément fonctionnel à chaque sprint plutôt qu'attendre un produit "parfait" documenté en détail.

### 3. La collaboration avec les clients **plutôt que** la négociation contractuelle

Les contrats cadrent les responsabilités. Mais un client engagé dans le projet, qui donne du feedback régulièrement, conduit à un produit qui répond réellement à ses besoins.

**Conséquence pratique :** inviter le Product Owner (représentant client) à la sprint review, impliquer les utilisateurs dans les tests.

### 4. L'adaptation au changement **plutôt que** le suivi d'un plan

Les plans sont utiles au démarrage. Mais les besoins évoluent. Un projet Agile accepte le changement comme une réalité, pas comme un problème.

**Conséquence pratique :** revoir le backlog à chaque sprint, ne pas considérer une modification de priorité comme un échec.

---

## Les douze principes Agile

Le Manifeste est accompagné de douze principes qui précisent concrètement comment appliquer ces valeurs.

### Principes orientés client et valeur

**Principe 1 — Satisfaction du client**
> "Notre priorité est de satisfaire le client en livrant rapidement et régulièrement des fonctionnalités à forte valeur ajoutée."

**Principe 2 — Accueil du changement**
> "Accueillez positivement les changements de besoins, même tard dans le projet. Agile capitalise sur le changement pour donner un avantage compétitif au client."

**Principe 3 — Livraisons fréquentes**
> "Livrez fréquemment un logiciel opérationnel avec des cycles de quelques semaines à quelques mois et une préférence pour les cycles courts."

**Principe 4 — Coopération**
> "Les utilisateurs ou leurs représentants et les développeurs doivent travailler ensemble quotidiennement tout au long du projet."

### Principes orientés équipe

**Principe 5 — Motivation**
> "Réalisez les projets avec des personnes motivées. Fournissez-leur l'environnement et le soutien dont elles ont besoin et faites-leur confiance pour atteindre les objectifs fixés."

**Principe 6 — Communication directe**
> "La méthode la plus simple et la plus efficace pour transmettre de l'information à l'équipe de développement et à l'intérieur de celle-ci est le dialogue en face à face."

**Principe 7 — Logiciel fonctionnel comme mesure d'avancement**
> "Un logiciel opérationnel est la principale mesure d'avancement."

**Principe 8 — Rythme soutenable**
> "Les processus Agile encouragent un rythme de développement soutenable. Ensemble, les commanditaires, les développeurs et les utilisateurs devraient être indéfiniment capables de maintenir un rythme constant."

### Principes orientés qualité et technique

**Principe 9 — Excellence technique**
> "Une attention continue à l'excellence technique et à une bonne conception renforce l'agilité."

**Principe 10 — Simplicité**
> "La simplicité – c'est-à-dire l'art de minimiser la quantité de travail inutile – est essentielle."

**Principe 11 — Auto-organisation**
> "Les meilleures architectures, spécifications et conceptions émergent d'équipes auto-organisées."

**Principe 12 — Amélioration continue**
> "À intervalles réguliers, l'équipe réfléchit aux moyens de devenir plus efficace, puis règle et modifie son comportement en conséquence."

---

## Agile vs Waterfall (Cascade)

### Le modèle Waterfall

Le modèle en cascade est une approche **linéaire et séquentielle**. Chaque phase doit être terminée avant que la suivante commence.

```
Analyse des besoins
       ↓
  Conception
       ↓
  Développement
       ↓
      Tests
       ↓
  Déploiement
       ↓
 Maintenance
```

**Points forts du Waterfall :**
- Planification initiale détaillée, budget prévisible
- Documentation exhaustive
- Adapté aux projets à exigences stables (construction, industrie)
- Responsabilités claires par phase

**Points faibles du Waterfall :**
- Le client ne voit le produit qu'à la fin
- Le changement est coûteux et résisté
- Les risques sont découverts tardivement
- Le délai entre expression du besoin et livraison peut être de 12 à 24 mois

### Le modèle Agile

Agile découpe le projet en **itérations courtes** (sprints de 1 à 4 semaines). À chaque itération, un incrément fonctionnel est livré et validé.

```
Sprint 1 → [Planif → Dev → Test → Review] → Incrément 1
Sprint 2 → [Planif → Dev → Test → Review] → Incrément 2
Sprint 3 → [Planif → Dev → Test → Review] → Incrément 3
...
```

**Points forts de l'Agile :**
- Feedback client à chaque sprint
- Adaptation rapide aux changements
- Risques identifiés et traités tôt
- Livraisons de valeur régulières

**Points faibles de l'Agile :**
- Budget difficile à prévoir sur le long terme
- Nécessite un Product Owner disponible et impliqué
- Documentation parfois négligée
- Moins adapté aux projets à contraintes légales ou réglementaires fixes

### Tableau comparatif

| Critère | Waterfall | Agile |
|---------|-----------|-------|
| Planification | Complète au départ | Itérative |
| Flexibilité | Faible | Élevée |
| Feedback client | À la fin | À chaque sprint |
| Visibilité d'avancement | Difficile | Continue (burndown) |
| Documentation | Exhaustive | "Juste suffisante" |
| Livraison | Unique, à la fin | Régulière, par incrément |
| Adapté à | Besoins stables, contraintes légales | Besoins évolutifs, innovation |
| Gestion du risque | Tardive | Continue |

---

## Agile en Data Engineering

Les principes Agile s'appliquent très bien aux projets data :

- **Livraisons fréquentes** : livrer un pipeline fonctionnel par sprint (même partiel) plutôt qu'un entrepôt de données complet en 18 mois.
- **Feedback continu** : les data analysts testent les dashboards et remontent des anomalies à chaque sprint.
- **Adaptation au changement** : les sources de données changent, les besoins métier évoluent — Agile absorbe ces changements.
- **Auto-organisation** : l'équipe data décide des technologies (dbt, Airflow, Kafka) selon les besoins réels.

**Exemple concret :** Un projet de création d'un Data Warehouse peut être découpé en sprints :
- Sprint 1 : ingestion d'une première source (CRM)
- Sprint 2 : modélisation de la couche staging
- Sprint 3 : première vue métier (chiffre d'affaires mensuel)
- Sprint 4 : dashboard opérationnel pour le commercial

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un tableau Jira ou Trello montrant un backlog avec des tickets organisés en sprints pour un projet data engineering fictif.
> **Expliquer :** Comment les tickets sont priorisés, ce que représente chaque colonne (To Do / In Progress / Done), et comment chaque sprint correspond à un incrément de valeur livré au client.

---

## Frameworks Agile : au-delà de Scrum

Scrum est le framework Agile le plus utilisé, mais il n'est pas le seul.

| Framework | Description | Adapté pour |
|-----------|-------------|-------------|
| **Scrum** | Sprints fixes, rôles définis, cérémonies structurées | Équipes produit, développement logiciel |
| **Kanban** | Flux continu, limites WIP, pas de sprints | Support, maintenance, ops |
| **SAFe** | Scrum à l'échelle (grandes organisations) | Projets multi-équipes |
| **LeSS** | Scrum simplifié pour plusieurs équipes | Produits complexes |
| **XP** | Pratiques techniques (TDD, pair programming) | Développement logiciel de qualité |

---

## Résumé

- Le Manifeste Agile (2001) énonce **4 valeurs** et **12 principes**
- Agile ne rejette pas les outils, la documentation ou les plans — il les met au service de la livraison de valeur
- Waterfall convient aux projets stables ; Agile convient aux projets évolutifs
- En Data Engineering, Agile permet de livrer de la valeur progressivement et d'adapter les pipelines aux besoins réels
