# Chapitre 7 : CLAUDE.md & Configuration Projet

## Objectifs

- Comprendre le rôle et la puissance de CLAUDE.md
- Écrire un CLAUDE.md efficace pour n'importe quel projet
- Maîtriser la hiérarchie des fichiers CLAUDE.md
- Connaître les bonnes pratiques et les pièges à éviter

---

## 1. Qu'est-ce que CLAUDE.md ?

### 1.1 Le concept

CLAUDE.md est le **fichier d'instructions** que Claude Code lit **automatiquement** à chaque lancement. C'est comme un **README pour l'IA** :

```
README.md               CLAUDE.md
┌─────────────────┐    ┌─────────────────────────────────┐
│ Pour les humains │    │ Pour Claude Code                │
│                  │    │                                 │
│ "Comment         │    │ "Comment travailler sur ce      │
│  installer et    │    │  projet : conventions, stack,   │
│  utiliser ce     │    │  commandes, architecture,       │
│  projet"         │    │  pièges à éviter..."            │
└─────────────────┘    └─────────────────────────────────┘
```

### 1.2 Pourquoi c'est crucial

Sans CLAUDE.md, Claude Code doit **deviner** votre contexte à chaque conversation. Avec CLAUDE.md :

```
Sans CLAUDE.md                      Avec CLAUDE.md
┌──────────────────────┐           ┌──────────────────────────────┐
│ "Quel framework ?"   │           │ Framework : FastAPI           │
│ "Quelle DB ?"        │           │ DB : PostgreSQL + SQLAlchemy  │
│ "Quels tests ?"      │ Explore   │ Tests : pytest                │
│ "Quel style ?"       │ à chaque  │ Style : Black + Ruff          │
│ "Quelle branche ?"   │ fois      │ Branche : feature/* → main    │
│                      │           │ Deploy : Docker + k8s         │
│ 5-10 tours perdus    │           │                               │
│ pour comprendre      │           │ 0 tour perdu                  │
└──────────────────────┘           │ Claude sait TOUT dès le début │
                                   └──────────────────────────────┘
```

---

## 2. Créer un CLAUDE.md

### 2.1 Avec /init

```
> /init
```

Claude Code analyse votre projet et génère un CLAUDE.md initial. C'est un bon point de départ, mais vous devriez **le personnaliser**.

### 2.2 Manuellement

Créez un fichier `CLAUDE.md` à la racine de votre projet :

```markdown
# CLAUDE.md

## Projet
Application e-commerce en Python/FastAPI avec PostgreSQL.

## Stack technique
- **Backend** : Python 3.12, FastAPI, SQLAlchemy 2.0
- **Base de données** : PostgreSQL 16
- **Tests** : pytest + pytest-asyncio
- **Linter** : Ruff
- **Formatter** : Black (line-length=88)
- **CI** : GitHub Actions

## Commandes importantes
- `make test` : Lancer les tests
- `make lint` : Lancer le linter
- `make run` : Lancer l'app en dev
- `docker compose up` : Lancer avec Docker

## Structure du projet
```
src/
├── api/          # Routes FastAPI
├── models/       # Modèles SQLAlchemy
├── schemas/      # Schémas Pydantic
├── services/     # Logique métier
├── repositories/ # Accès base de données
└── core/         # Configuration, sécurité
tests/
├── unit/         # Tests unitaires
├── integration/  # Tests d'intégration
└── conftest.py   # Fixtures partagées
```

## Conventions de code
- Type hints obligatoires sur toutes les fonctions
- Docstrings Google-style pour les fonctions publiques
- Pas de `Any` sauf cas exceptionnels justifiés
- Nommage : snake_case pour tout (variables, fonctions, fichiers)

## Conventions Git
- Conventional Commits : feat/fix/docs/refactor/test/chore
- Branches : feature/xxx, fix/xxx, hotfix/xxx
- PR obligatoire pour merger dans main
- Squash merge uniquement

## Règles importantes
- Ne JAMAIS modifier les migrations Alembic existantes
- Toujours créer une nouvelle migration pour les changements de schéma
- Les variables d'environnement sont dans .env (pas committé)
- Le .env.example contient les variables sans les valeurs
```

---

## 3. La hiérarchie des CLAUDE.md

### 3.1 Trois niveaux

```
Hiérarchie CLAUDE.md (du plus global au plus spécifique)
│
├── ~/.claude/CLAUDE.md              ← Global (tous les projets)
│   "Je préfère le français"
│   "Utilise toujours des type hints"
│
├── ~/mon-projet/CLAUDE.md           ← Projet (racine du repo)
│   "Stack : Python/FastAPI"
│   "Tests : pytest"
│
└── ~/mon-projet/src/api/CLAUDE.md   ← Sous-dossier (spécifique)
    "Les routes suivent le pattern RESTful"
    "Toujours valider avec Pydantic"
```

### 3.2 Comment ils se combinent

```
Quand Claude travaille dans src/api/ :

Il lit dans cet ordre :
1. ~/.claude/CLAUDE.md          → Préférences globales
2. ~/projet/CLAUDE.md           → Contexte du projet
3. ~/projet/src/api/CLAUDE.md   → Règles spécifiques au dossier

Les instructions se CUMULENT (pas de remplacement).
En cas de conflit, le plus spécifique gagne.
```

### 3.3 CLAUDE.md global (préférences personnelles)

```markdown
# ~/.claude/CLAUDE.md

## Langue
- Réponds toujours en français
- Commentaires de code en anglais
- Messages de commit en anglais

## Style
- Je préfère le code concis et lisible
- Pas de sur-ingénierie
- DRY mais pas au détriment de la lisibilité

## Outils
- J'utilise VS Code
- Mon terminal est iTerm2/zsh
- J'utilise pnpm plutôt que npm
```

### 3.4 CLAUDE.md de sous-dossier (contexte local)

Utile pour les monorepos :

```
monorepo/
├── CLAUDE.md                    ← "Monorepo avec pnpm workspaces"
├── packages/
│   ├── frontend/
│   │   └── CLAUDE.md            ← "React 19, TailwindCSS, Vitest"
│   ├── backend/
│   │   └── CLAUDE.md            ← "Express, Prisma, Jest"
│   └── shared/
│       └── CLAUDE.md            ← "Types partagés, ne jamais modifier sans review"
```

---

## 4. Sections essentielles d'un bon CLAUDE.md

### 4.1 Template complet

```markdown
# CLAUDE.md

## Description du projet
[1-2 phrases décrivant le projet]

## Stack technique
[Liste des technologies avec versions]

## Commandes
[Les commandes que Claude doit connaître]

## Architecture
[Structure des dossiers avec descriptions]

## Conventions
[Style de code, nommage, patterns]

## Règles Git
[Branches, commits, PRs]

## Pièges / Attention
[Ce qu'il ne faut surtout PAS faire]

## Contexte métier (optionnel)
[Vocabulaire métier, règles business]
```

### 4.2 Section "Pièges" — La plus importante

C'est dans cette section que vous évitez les erreurs récurrentes :

```markdown
## Pièges / Attention

- ⚠️ Ne JAMAIS modifier `src/core/legacy.py` — module ancien mais critique
- ⚠️ Les migrations Alembic sont immuables une fois mergées
- ⚠️ Le champ `user.email` est nullable en DB mais requis en API
- ⚠️ Le module de paiement (src/payments/) a ses propres tests : `make test-payments`
- ⚠️ Les timestamps sont en UTC partout, la conversion se fait côté frontend
- ⚠️ Ne pas utiliser `datetime.now()`, toujours `datetime.utcnow()`
```

### 4.3 Section "Contexte métier"

Aide Claude à comprendre le **domaine** :

```markdown
## Contexte métier

### Vocabulaire
- **Workspace** : Un espace de travail qui contient des projets
- **Member** : Un utilisateur qui appartient à un workspace
- **Owner** : Le créateur du workspace (droits admin)
- **Billing cycle** : Du 1er au dernier jour du mois

### Règles métier
- Un utilisateur peut appartenir à max 5 workspaces
- Le plan gratuit permet 3 projets par workspace
- La suppression d'un workspace est soft-delete (30 jours de grâce)
```

---

## 5. Bonnes pratiques

### 5.1 Ce qui marche bien

```
✅ Instructions claires et concises
✅ Exemples concrets
✅ Commandes copy-pastables
✅ Structure du projet documentée
✅ Conventions explicites
✅ Pièges clairement identifiés
```

### 5.2 Ce qu'il faut éviter

```
❌ Trop long (> 500 lignes) — Claude a un contexte limité
❌ Trop vague ("écris du bon code")
❌ Informations obsolètes
❌ Secrets / clés API
❌ Instructions contradictoires
❌ Répéter ce qui est dans README.md
```

### 5.3 Taille idéale

```
Taille CLAUDE.md
│
├── Trop court (< 20 lignes)    → Claude doit deviner
├── Idéal (50-200 lignes)       → Assez de contexte, pas de bruit
└── Trop long (> 500 lignes)    → Mange le contexte, dilue les infos
```

---

## 6. Exemples par type de projet

### 6.1 Projet Python Data Engineering

```markdown
# CLAUDE.md

## Projet
Pipeline ETL pour ingestion de données e-commerce vers BigQuery.

## Stack
- Python 3.12, Apache Airflow 2.8, dbt-core 1.7
- Source : PostgreSQL (OLTP) → BigQuery (OLAP)
- Orchestration : Airflow sur Cloud Composer
- Tests : pytest + great_expectations

## Commandes
- `make test` : pytest
- `make dbt-run` : dbt run --target dev
- `make dbt-test` : dbt test
- `airflow dags test mon_dag 2024-01-01` : tester un DAG

## Structure
- dags/           : DAGs Airflow
- dbt/            : Projet dbt (models/, tests/, macros/)
- src/extractors/ : Scripts d'extraction
- src/loaders/    : Scripts de chargement

## Conventions
- Architecture Medallion : bronze → silver → gold
- Les DAGs doivent être idempotents
- Pas de SQL inline dans Python, tout dans dbt
```

### 6.2 Projet React/Next.js

```markdown
# CLAUDE.md

## Projet
Dashboard analytics SaaS en Next.js 15.

## Stack
- Next.js 15 (App Router), React 19, TypeScript 5.6
- Styling : TailwindCSS 4 + shadcn/ui
- State : Zustand + React Query
- Tests : Vitest + Playwright
- DB : Prisma + PostgreSQL

## Commandes
- `pnpm dev` : Serveur dev
- `pnpm test` : Tests unitaires
- `pnpm test:e2e` : Tests E2E Playwright
- `pnpm prisma studio` : GUI base de données

## Conventions
- Composants dans PascalCase : `UserCard.tsx`
- Hooks custom préfixés : `useAuth`, `useWorkspace`
- Server Components par défaut, "use client" seulement si nécessaire
- Pas de `any` TypeScript
```

---

## 7. Exercice : Créez votre CLAUDE.md

**Consigne** : Pour un de vos projets, créez un CLAUDE.md en suivant ce processus :

1. Lancez Claude Code dans votre projet
2. Tapez `/init` pour générer une base
3. Personnalisez avec :
   - Vos conventions de code
   - Les commandes importantes
   - Les pièges connus
   - Le contexte métier
4. Testez en demandant à Claude de faire une modification — il devrait suivre vos conventions

---

## Résumé

```
CLAUDE.md = Le README pour l'IA
│
├── Hiérarchie : Global (~/) → Projet (/) → Sous-dossier (/src/)
├── Sections clés :
│   ├── Stack technique
│   ├── Commandes
│   ├── Architecture
│   ├── Conventions
│   ├── Pièges ← LE PLUS IMPORTANT
│   └── Contexte métier
├── Taille idéale : 50-200 lignes
├── Création : /init puis personnaliser
└── Maintenance : Mettre à jour quand le projet évolue
```

> **Prochain chapitre** : [Prompting Avancé & Bonnes Pratiques](08-prompting-avance.md)
