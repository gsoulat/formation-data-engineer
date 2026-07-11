# Introduction aux ADRs

## Le problème que les ADRs résolvent

### Scénario classique sans ADR

> **Nouveau développeur (6 mois après le démarrage du projet) :**
> "Pourquoi on utilise Kafka pour ce pipeline ? Une simple queue PostgreSQL aurait suffi."
>
> **Développeur senior :**
> "Bonne question... À l'époque, on avait discuté de ça pendant 3 heures. Je me souviens qu'il y avait une raison liée à la scalabilité et aux partenaires externes, mais les détails... je ne m'en souviens plus."
>
> **Nouveau développeur :**
> "OK, je vais ouvrir une PR pour remplacer Kafka par PostgreSQL alors."
>
> **Développeur senior (3 heures de debug plus tard) :**
> "Ah oui, maintenant je me souviens — on avait besoin du replay des messages pour les partenaires qui se connectent avec un délai. Reviens à Kafka."

Ce scénario se répète des dizaines de fois dans chaque projet. La solution ? **Documenter les décisions structurantes au moment où elles sont prises.**

---

## Qu'est-ce qu'un ADR ?

Un **Architecture Decision Record** (ADR) est un document court qui capture une décision d'architecture importante, son contexte et ses conséquences.

Le concept a été formalisé par **Michael Nygard** en 2011 dans son article *"Documenting Architecture Decisions"*.

### Ce qu'un ADR capture

| Élément | Question |
|---------|---------|
| Titre | Quelle décision a été prise ? |
| Statut | Est-ce en vigueur ? Remplacée ? Proposée ? |
| Contexte | Quelle situation a nécessité une décision ? |
| Décision | Qu'avons-nous décidé exactement ? |
| Conséquences | Quels sont les impacts (positifs et négatifs) ? |
| Alternatives | Quelles options ont été écartées et pourquoi ? |

---

## Pourquoi documenter les décisions d'architecture ?

### 1. La mémoire collective est défaillante

Les équipes changent. Les développeurs qui ont pris une décision en 2022 ne sont peut-être plus là en 2025. Même ceux qui restent oublient les détails.

**Statistique :** Dans une équipe de 5 personnes, en 12 mois, en moyenne 1 à 2 personnes ont changé de poste. En 24 mois : 2 à 3.

### 2. Les décisions ont un contexte qui évolue

Une décision prise en contexte de startup (contrainte de temps, budget limité, équipe de 3) peut ne plus être adaptée 2 ans plus tard (équipe de 20, scalabilité requise).

Sans ADR, on ne sait pas si la contrainte qui a guidé la décision est toujours valable.

### 3. Éviter les guerres de tranchées

Sans trace des discussions passées, chaque nouveau membre peut remettre en question les mêmes décisions. Avec un ADR, on peut simplement dire : "La décision a été prise, elle est documentée, si tu veux la remettre en question, ouvre un nouveau ADR avec les arguments actuels."

### 4. Onboarding accéléré

Un nouveau membre qui lit les ADRs d'un projet comprend rapidement :
- Les choix technologiques et pourquoi
- Les problèmes qui ont été rencontrés
- Les alternatives qui ont été écartées

### 5. Revue de code plus efficace

Quand une PR référence un ADR, les reviewers comprennent le contexte technique sans avoir à demander des explications dans les commentaires.

---

## Quelles décisions documenter ?

### Décisions à documenter

- **Choix technologiques majeurs** : quel framework, quelle base de données, quel broker de messages
- **Patterns d'architecture** : microservices vs monolithe, event-driven vs requête/réponse
- **Stratégies de déploiement** : Kubernetes vs VMs, CI/CD, GitOps
- **Décisions de modélisation de données** : schéma en étoile vs snowflake, choix des clés primaires
- **Intégrations externes** : choix d'un fournisseur cloud, d'une API partenaire
- **Choix de sécurité** : stratégie d'authentification, chiffrement, gestion des secrets
- **Décisions de performance** : stratégie de cache, partitionnement des données

### Décisions à NE PAS documenter

- Décisions triviales ou réversibles facilement : "On utilise 4 espaces au lieu de 2 pour l'indentation"
- Décisions purement opérationnelles : "On déploie vendredi soir"
- Décisions qui changent toutes les semaines : "Ce sprint on travaille sur le module X"
- Documentation technique standard (à mettre dans le README ou les docs techniques)

**Règle pratique :** Si la décision vous a pris plus de 30 minutes à débattre en équipe, elle mérite un ADR.

---

## Le cycle de vie d'un ADR

### Les statuts

```
Proposed ──→ Accepted ──→ Deprecated ──→ Superseded
    │              │
    └──→ Rejected  └──→ (reste en vigueur)
```

| Statut | Signification |
|--------|--------------|
| **Proposed** | L'ADR est en cours de discussion, pas encore validé |
| **Accepted** | L'ADR a été validé et est en vigueur |
| **Rejected** | L'ADR a été proposé mais rejeté — garder quand même pour historique |
| **Deprecated** | La décision n'est plus en vigueur mais n'a pas été remplacée |
| **Superseded** | Remplacé par un nouvel ADR (avec référence croisée) |

### Transitions de statut

**Proposed → Accepted :**
L'ADR est soumis via PR, l'équipe le revoit et l'approuve. Merger la PR = accepter l'ADR.

**Accepted → Superseded :**
Une nouvelle décision contredit l'ancienne. On crée un nouvel ADR qui prend le statut "Accepted" et l'ancien passe à "Superseded" avec un lien vers le nouveau.

**Ne jamais supprimer un ADR.** Même les ADRs rejetés ou superseded ont de la valeur historique.

---

## L'ADR dans le workflow de développement

### Intégration Git

La pratique recommandée est de stocker les ADRs dans le dépôt Git du projet, dans un dossier dédié.

```
projet/
├── src/
├── tests/
├── docs/
│   └── adr/
│       ├── 0001-utiliser-postgresql.md
│       ├── 0002-utiliser-fastapi.md
│       ├── 0003-containerisation-docker.md
│       └── 0004-utiliser-kafka.md
└── README.md
```

**Avantages :**
- Versionnés avec le code — on sait à quelle version du code correspond chaque ADR
- Visible dans la PR qui implémente la décision
- Historique Git = historique des décisions

### ADR dans les Pull Requests

**Bonnes pratiques :**

1. **Ouvrir un ADR en même temps que la PR d'implémentation :**
   - PR contient : code + ADR en statut "Proposed"
   - La revue de code inclut la revue de l'ADR
   - Merger la PR = valider la décision + l'implémentation

2. **ADR avant l'implémentation (idéal pour les décisions majeures) :**
   - Ouvrir une PR "ADR only" pour discussion
   - Discussion dans les commentaires de la PR
   - Merger la PR ADR = accord de l'équipe
   - Ouvrir ensuite la PR d'implémentation

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un dépôt GitHub montrant un dossier `docs/adr/` avec plusieurs fichiers ADR numérotés, et une Pull Request ouverte qui inclut à la fois du code et un nouveau fichier ADR en statut "Proposed".
> **Expliquer :** Comment les commentaires de revue sur la PR servent à débattre de la décision, comment l'approbation de la PR signifie l'acceptation de l'ADR, et comment naviguer dans l'historique Git pour voir l'évolution des décisions dans le temps.

---

## Outils pour gérer les ADRs

### adr-tools (CLI)

```bash
# Installation (macOS)
brew install adr-tools

# Initialiser les ADRs dans un projet
adr init docs/adr

# Créer un nouvel ADR
adr new "Utiliser PostgreSQL comme base de données principale"
# → Crée : docs/adr/0001-utiliser-postgresql.md

# Lister les ADRs
adr list

# Marquer un ADR comme superseded
adr supersede 0001 0005
```

### Log4brains

Log4brains génère un site web statique à partir des ADRs Markdown.

```bash
# Installation
npm install -g log4brains

# Initialiser
log4brains init

# Prévisualiser
log4brains preview

# Build statique
log4brains build
```

---

## Résumé

- Un ADR documente **une décision d'architecture** : contexte, décision, conséquences, alternatives
- Les ADRs sont stockés **dans le dépôt Git** du projet
- Le cycle de vie : Proposed → Accepted → Deprecated / Superseded
- **Ne jamais supprimer** un ADR — même les rejetés ont de la valeur
- Intégrer les ADRs dans le **workflow de PR** pour une revue collaborative
- Documenter les décisions importantes (> 30 min de débat), pas les décisions triviales
