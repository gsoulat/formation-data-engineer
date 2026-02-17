# Chapitre 3 : Les Commandes Slash & Navigation

## Objectifs

- Maîtriser toutes les commandes slash disponibles
- Comprendre quand et pourquoi utiliser chaque commande
- Savoir gérer efficacement ses conversations et sessions
- Utiliser les commandes de configuration, diagnostics et agents

---

## 1. Vue d'ensemble des commandes slash

Les commandes slash sont des **raccourcis intégrés** qui commencent par `/`. Elles permettent de contrôler Claude Code sans passer par un prompt en langage naturel.

> **Astuce** : Tapez `/` dans Claude Code pour voir la liste complète en temps réel, y compris les commandes ajoutées par vos serveurs MCP et vos skills personnalisés.

```
Commandes Slash
│
├── Session & Navigation
│   ├── /help              → Aide intégrée
│   ├── /clear             → Effacer la conversation
│   ├── /compact           → Compresser le contexte
│   ├── /resume            → Reprendre une session passée
│   ├── /rename            → Renommer la session
│   ├── /rewind            → Revenir en arrière dans la conversation
│   ├── /fork              → Dupliquer la session courante
│   ├── /export            → Exporter la conversation
│   └── /quit (/exit)      → Quitter
│
├── Modèle & Configuration
│   ├── /model             → Changer de modèle
│   ├── /config            → Ouvrir les paramètres
│   ├── /permissions       → Gérer les permissions
│   ├── /fast              → Mode rapide on/off
│   ├── /theme             → Changer le thème de couleurs
│   ├── /vim               → Mode édition vim
│   ├── /plan              → Entrer en mode Plan
│   └── /output-style      → Configurer le format de réponse
│
├── Contexte & Mémoire
│   ├── /init              → Créer un fichier CLAUDE.md
│   ├── /memory            → Éditer les instructions mémorisées
│   ├── /context           → Visualiser l'utilisation du contexte
│   ├── /add-dir           → Ajouter un répertoire au contexte
│   └── /todos             → Lister les tâches en cours
│
├── Diagnostics & Infos
│   ├── /cost              → Coût de la session
│   ├── /stats             → Statistiques d'utilisation
│   ├── /usage             → Limites du plan (abonnement)
│   ├── /status            → Informations système
│   ├── /doctor            → Vérifier l'installation
│   └── /debug             → Dépanner la session
│
├── Outils & Intégrations
│   ├── /tools             → Lister les outils disponibles
│   ├── /mcp               → Gérer les serveurs MCP
│   ├── /hooks             → Configurer les hooks
│   ├── /statusline        → Configurer la barre de statut
│   └── /terminal-setup    → Installer les raccourcis terminal
│
├── Agents & Tâches
│   ├── /agents            → Voir et gérer les sous-agents
│   └── /tasks             → Gérer les tâches en arrière-plan
│
├── Transfert de session
│   ├── /teleport          → Importer une session depuis claude.ai
│   └── /desktop           → Transférer vers Claude Code Desktop
│
└── Workflow & Utilitaires
    ├── /commit            → Créer un commit intelligent
    ├── /review            → Code review automatique
    ├── /copy              → Copier la dernière réponse
    └── /bug               → Signaler un bug à Anthropic
```

---

## 2. Session & Navigation

### 2.1 `/help` — Aide intégrée

```
> /help
```

Affiche la liste de toutes les commandes disponibles et un guide rapide.

### 2.2 `/clear` — Effacer la conversation

```
> /clear
```

Remet à zéro la conversation **sans quitter Claude Code**. Utile quand :
- Vous changez complètement de sujet
- Le contexte est pollué par des erreurs précédentes
- Vous voulez repartir à zéro

```
Avant /clear                    Après /clear
┌─────────────────────┐        ┌─────────────────────┐
│ Message 1           │        │                     │
│ Message 2           │        │ [Conversation vide] │
│ ...erreurs...       │        │                     │
│ Message 15          │        │                     │
│ [Contexte pollué]   │        │ [Contexte propre]   │
└─────────────────────┘        └─────────────────────┘
```

### 2.3 `/compact` — Compresser le contexte

```
> /compact

# Avec des instructions spécifiques
> /compact garde uniquement le contexte sur l'API REST
```

**Compacte** la conversation en résumant les échanges précédents. Différent de `/clear` :

| | `/clear` | `/compact` |
|--|----------|------------|
| Efface tout | Oui | Non |
| Garde un résumé | Non | Oui |
| Perd le contexte | Totalement | Partiellement |
| Quand l'utiliser | Changement de sujet | Longue session |

> **Astuce pro** : Utilisez `/compact` régulièrement lors de longues sessions pour éviter que Claude "oublie" des éléments importants. Vous pouvez orienter le résumé avec des instructions : `/compact focus sur les décisions d'architecture`.

### 2.4 `/resume` — Reprendre une session passée

```
> /resume

# Ou directement avec un ID de session
> /resume abc123
```

Permet de **reprendre une conversation précédente** là où vous l'aviez laissée. Sans argument, ouvre un sélecteur interactif listant vos sessions récentes.

```
┌─────────────────────────────────────────────────┐
│  Select a session to resume                      │
│                                                   │
│  > 2024-01-16 14:30  "Refactoring auth module"  │
│    2024-01-16 10:15  "Fix API endpoints"         │
│    2024-01-15 16:45  "Add payment integration"   │
│    2024-01-15 09:00  "Setup CI/CD pipeline"      │
└─────────────────────────────────────────────────┘
```

> **Cas d'usage** : Vous avez commencé un refactoring hier, vous le reprenez aujourd'hui avec tout le contexte intact.

### 2.5 `/rename` — Renommer la session

```
> /rename Refactoring module auth
```

Donne un **nom explicite** à la session en cours. Facilite l'identification lors d'un `/resume` ultérieur. Sans nom, les sessions sont identifiées par date et heure.

### 2.6 `/rewind` — Revenir en arrière

```
> /rewind
```

Permet de **remonter dans le temps** dans la conversation et/ou les modifications de code. Deux usages :
- **Annuler des messages** : revenir à un point précédent de la conversation
- **Annuler des changements de code** : restaurer les fichiers à un état antérieur

```
Conversation                     Après /rewind (message 3)
┌─────────────────────┐         ┌─────────────────────┐
│ 1. "Ajoute un login"│         │ 1. "Ajoute un login"│
│ 2. [Claude code...] │         │ 2. [Claude code...] │
│ 3. "Change l'UI"    │         │ 3. "Change l'UI"    │
│ 4. [Claude modifie] │ ──────▶ │                     │
│ 5. "Non, pas ça !"  │         │ [Code restauré]     │
└─────────────────────┘         └─────────────────────┘
```

> **Quand utiliser** : Claude a pris une mauvaise direction et vous voulez revenir avant cette décision plutôt que de tenter de corriger.

### 2.7 `/fork` — Dupliquer la session

```
> /fork
```

Crée une **branche** de la session courante. La session originale est préservée et une nouvelle session démarre avec le même contexte. Utile pour :
- Tester une approche alternative sans perdre la conversation actuelle
- Explorer deux solutions en parallèle

### 2.8 `/export` — Exporter la conversation

```
> /export

# Ou vers un fichier spécifique
> /export conversation-auth.md
```

Exporte la conversation complète dans un fichier ou dans le presse-papier. Formats supportés : Markdown. Utile pour :
- Documenter une session de travail
- Partager une conversation avec un collègue
- Archiver des décisions techniques

### 2.9 `/quit` ou `/exit`

```
> /quit
> /exit
```

Quitte Claude Code proprement. Vous pouvez aussi utiliser `Ctrl+C` (deux fois).

---

## 3. Modèle & Configuration

### 3.1 `/model` — Changer de modèle à la volée

```
> /model

# Claude affiche les modèles disponibles :
# 1. claude-opus-4-6        (le plus puissant)
# 2. claude-sonnet-4-5      (équilibré - défaut)
# 3. claude-haiku-4-5       (rapide et économique)
```

**Stratégie de switch de modèle** :

```
Tâche simple                    Tâche complexe
(question rapide, petit fix)    (refactoring, architecture)
        │                               │
        ▼                               ▼
   claude-haiku-4-5               claude-opus-4-6
   Rapide, pas cher               Lent, cher, mais excellent
```

> **Astuce** : Avec Opus 4.6, utilisez les flèches gauche/droite pour ajuster le **niveau d'effort** (thinking tokens). Plus d'effort = réponse plus réfléchie mais plus lente.

### 3.2 `/config` — Configuration en session

```
> /config
```

Ouvre l'interface de configuration interactive (onglet Config). Permet de modifier les settings sans quitter la session.

### 3.3 `/permissions` — Gérer les permissions

```
> /permissions
```

Affiche et permet de modifier les permissions accordées (quels outils peuvent s'exécuter sans demander confirmation).

### 3.4 `/fast` — Mode rapide

```
> /fast
```

Active/désactive le mode fast. Ce mode utilise **le même modèle** mais avec une sortie plus rapide (moins de tokens de réflexion). Idéal pour les tâches simples où la vitesse prime sur la profondeur de raisonnement.

### 3.5 `/theme` — Changer le thème

```
> /theme
```

Change le **thème de couleurs** de l'interface Claude Code dans le terminal. Propose plusieurs thèmes (clair, sombre, etc.).

### 3.6 `/vim` — Mode édition vim

```
> /vim
```

Active/désactive le mode **vim** pour l'édition des prompts. Si vous êtes habitué aux raccourcis vim (`hjkl`, `i`, `Esc`, etc.), ce mode vous sera familier.

### 3.7 `/plan` — Mode Plan

```
> /plan
```

Entre en **mode Plan** (lecture seule). Dans ce mode, Claude analyse le code et propose un plan d'implémentation **sans modifier** aucun fichier. Utile pour :
- Évaluer la complexité d'une tâche avant de coder
- Obtenir une vision architecturale
- Valider une approche avant de l'implémenter

```
Mode normal                     Mode Plan
┌─────────────────────┐        ┌─────────────────────┐
│ Claude lit + écrit   │        │ Claude lit SEULEMENT│
│ les fichiers         │        │ et propose un plan  │
│                      │        │                     │
│ ✅ Read, Write, Edit │        │ ✅ Read, Glob, Grep │
│ ✅ Bash              │        │ ❌ Write, Edit      │
│                      │        │ ❌ Bash (écriture)  │
└─────────────────────┘        └─────────────────────┘
```

### 3.8 `/output-style` — Format des réponses

```
> /output-style
```

Configure **comment Claude formate ses réponses** : verbeux, concis, technique, pédagogique, etc. Ajuste le style de sortie sans affecter les capacités.

---

## 4. Contexte & Mémoire

### 4.1 `/init` — Initialiser CLAUDE.md

```
> /init
```

Crée un fichier `CLAUDE.md` à la racine du projet. Ce fichier est **lu automatiquement** par Claude Code à chaque lancement. C'est la **mémoire persistante** du projet.

```
Avant /init                     Après /init
┌─────────────────────┐        ┌─────────────────────┐
│ mon-projet/         │        │ mon-projet/         │
│ ├── src/            │        │ ├── src/            │
│ ├── tests/          │        │ ├── tests/          │
│ └── package.json    │        │ ├── package.json    │
└─────────────────────┘        │ └── CLAUDE.md ← NEW │
                               └─────────────────────┘
```

> On verra CLAUDE.md en détail au **Chapitre 7**.

### 4.2 `/memory` — Instructions mémorisées

```
> /memory
```

Ouvre un éditeur pour ajouter des instructions persistantes dans `~/.claude/CLAUDE.md` (global) ou dans le `CLAUDE.md` du projet.

Exemples d'instructions mémorisées :
```markdown
# Mes préférences
- Toujours écrire en français dans les commentaires
- Utiliser des type hints Python
- Préférer les f-strings aux .format()
- Ne jamais utiliser var en JavaScript, toujours const/let
```

### 4.3 `/context` — Visualiser l'utilisation du contexte

```
> /context
```

Affiche une **grille colorée** représentant visuellement ce qui consomme votre fenêtre de contexte :

```
Context Window Usage (87% used)
┌──────────────────────────────────────────┐
│ ████████████████████████████████████░░░░░ │
│                                          │
│ 🟦 System prompt    : 12%               │
│ 🟩 CLAUDE.md        :  5%               │
│ 🟨 Conversation     : 45%               │
│ 🟥 Tool results     : 25%               │
│ ⬜ Disponible       : 13%               │
└──────────────────────────────────────────┘
```

> **Quand utiliser** : Quand Claude commence à "oublier" des choses ou quand les réponses perdent en qualité — signe que le contexte est saturé. Faites suivre d'un `/compact` si nécessaire.

### 4.4 `/add-dir` — Ajouter un répertoire au contexte

```
> /add-dir /chemin/vers/autre-projet
```

Ajoute un **répertoire supplémentaire** au contexte de travail de Claude Code. Par défaut, Claude Code opère dans le répertoire courant. Cette commande permet d'étendre la portée à d'autres dossiers.

**Cas d'usage** :
- Travailler sur un **monorepo** avec plusieurs packages
- Référencer une **bibliothèque interne** dans un autre répertoire
- Accéder à des **fichiers de configuration** partagés
- Travailler sur un **frontend** et un **backend** dans des repos séparés

```
Sans /add-dir                   Avec /add-dir ../shared-lib
┌─────────────────────┐        ┌─────────────────────┐
│ Claude voit :       │        │ Claude voit :       │
│ ./mon-projet/       │        │ ./mon-projet/       │
│   ├── src/          │        │   ├── src/          │
│   └── tests/        │        │   └── tests/        │
│                     │        │ ../shared-lib/      │
│                     │        │   ├── utils/        │
│                     │        │   └── types/        │
└─────────────────────┘        └─────────────────────┘
```

### 4.5 `/todos` — Liste des tâches

```
> /todos
```

Affiche les **tâches (TODO)** en cours de la session. Claude peut créer des tâches pendant qu'il travaille pour organiser les étapes d'un travail complexe.

---

## 5. Diagnostics & Informations

### 5.1 `/cost` — Coût de la session

```
> /cost
```

Affiche le **coût cumulé** de la session en cours :
- Nombre de tokens utilisés (input + output)
- Coût estimé en dollars
- Répartition par modèle si vous avez switché

### 5.2 `/stats` — Statistiques d'utilisation

```
> /stats
```

Affiche des **statistiques détaillées** sur votre utilisation de Claude Code :
- Utilisation quotidienne (graphique)
- Historique des sessions
- Séries d'utilisation consécutive (streaks)
- Préférences de modèles

```
📊 Usage Stats (last 30 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sessions   : 127
Total cost : $42.35
Avg/session: $0.33
Top model  : claude-sonnet-4-5 (78%)
Streak     : 12 jours consécutifs 🔥
```

### 5.3 `/usage` — Limites du plan

```
> /usage
```

**Réservé aux abonnements** (Claude Max/Pro/Teams/Enterprise). Affiche :
- Limites de votre plan
- Utilisation actuelle vs quota
- Statut de rate limiting

### 5.4 `/status` — Informations système

```
> /status
```

Ouvre l'interface Settings sur l'onglet **Status**. Affiche :
- Version de Claude Code installée
- Modèle actif
- Informations de compte
- Statut de connectivité

### 5.5 `/doctor` — Diagnostic de l'installation

```
> /doctor
```

Lance un **health check** complet de votre installation Claude Code :
- Vérifie la connectivité réseau
- Vérifie l'authentification
- Vérifie les dépendances (Node.js, Git, etc.)
- Vérifie la configuration
- Identifie les problèmes potentiels

```
🩺 Claude Code Doctor
━━━━━━━━━━━━━━━━━━━━
✅ Node.js v20.11.0
✅ Git v2.43.0
✅ Authentication valid
✅ API connectivity OK
✅ MCP servers healthy (2/2)
⚠️  Terminal: Shift+Enter not configured (run /terminal-setup)
```

> **Quand utiliser** : Dès que quelque chose ne fonctionne pas comme prévu. C'est le premier réflexe de troubleshooting.

### 5.6 `/debug` — Dépanner la session

```
> /debug

# Avec une description du problème
> /debug Claude ne voit pas mes fichiers TypeScript
```

Lit le **log de debug** de la session en cours et analyse les problèmes. Optionnellement, décrivez le problème pour que Claude concentre son diagnostic.

---

## 6. Outils & Intégrations

### 6.1 `/tools` — Outils disponibles

```
> /tools
```

Affiche la liste complète des outils que Claude Code peut utiliser, y compris ceux ajoutés par les serveurs MCP.

### 6.2 `/mcp` — Serveurs MCP

```
> /mcp
```

Gère les serveurs **MCP** (Model Context Protocol) connectés :
- Liste les serveurs actifs et leur statut
- Permet de connecter/déconnecter des serveurs
- Gère l'authentification OAuth pour les serveurs qui le requièrent

### 6.3 `/hooks` — Configurer les hooks

```
> /hooks
```

Ouvre un menu de configuration pour les **hooks** — des commandes shell qui s'exécutent automatiquement en réponse à des événements Claude Code (avant/après un outil, au démarrage, etc.).

Exemples de hooks :
- Lancer les tests automatiquement après chaque modification de code
- Formatter le code après chaque écriture de fichier
- Logger les actions dans un fichier

### 6.4 `/statusline` — Barre de statut

```
> /statusline
```

Configure la **barre de statut** affichée dans votre terminal pendant l'utilisation de Claude Code. Peut afficher : modèle actif, coût, tokens utilisés, etc.

### 6.5 `/terminal-setup` — Raccourcis terminal

```
> /terminal-setup
```

Installe les **bindings de terminal** nécessaires pour certains raccourcis clavier :

| Raccourci | Action |
|-----------|--------|
| `Shift+Enter` | Saut de ligne dans le prompt (multiligne) |
| `Alt+T` | Toggle du mode thinking (réflexion visible) |

> **Important** : Sans `/terminal-setup`, certains raccourcis comme `Shift+Enter` ne fonctionneront pas dans votre terminal.

---

## 7. Agents & Tâches de fond

### 7.1 `/agents` — Gérer les sous-agents

```
> /agents
```

Affiche et gère les **sous-agents** configurés. Les sous-agents sont des instances spécialisées de Claude qui peuvent être lancées en parallèle pour traiter des sous-tâches.

```
Agents actifs
├── Explorer Agent      → Recherche dans le codebase
├── Bash Agent          → Exécution de commandes
├── Plan Agent          → Planification architecturale
└── Custom Agent (MCP)  → Agents personnalisés
```

Les agents sont particulièrement utiles pour :
- **Paralléliser** des recherches dans un grand codebase
- **Isoler** des tâches longues sans bloquer la conversation principale
- **Spécialiser** certaines tâches (tests, déploiement, review)

### 7.2 `/tasks` — Tâches en arrière-plan

```
> /tasks
```

Liste et gère les **tâches en arrière-plan**. Quand Claude lance des opérations longues (tests, builds, recherches), elles apparaissent ici.

```
Background Tasks
├── #1 [running]   npm test (started 2 min ago)
├── #2 [completed] grep -r "TODO" src/ (15 results)
└── #3 [running]   Agent: exploring auth module
```

---

## 8. Transfert de session

### 8.1 `/teleport` — Importer depuis claude.ai

```
> /teleport
```

**Réservé aux abonnés** (Claude Max/Pro). Permet de **reprendre dans le terminal** une conversation commencée sur claude.ai. Le contexte et l'historique sont transférés.

```
claude.ai (navigateur)          Claude Code (terminal)
┌─────────────────────┐        ┌─────────────────────┐
│ Conversation avec   │  ───▶  │ Session reprise      │
│ du code complexe    │teleport│ avec tout le contexte│
│ (limité dans le     │        │ et accès au code     │
│  navigateur)        │        │ local                │
└─────────────────────┘        └─────────────────────┘
```

### 8.2 `/desktop` — Transférer vers l'app Desktop

```
> /desktop
```

Transfère la session CLI vers **Claude Code Desktop** (macOS, Windows). Utile si vous préférez continuer dans l'application de bureau avec son interface graphique.

---

## 9. Workflow & Utilitaires

### 9.1 `/commit` — Créer un commit intelligent

```
> /commit
```

Claude Code va :
1. Analyser les changements (`git diff`)
2. Comprendre **le sens** des modifications
3. Générer un message de commit pertinent
4. Créer le commit

```
git diff → Claude analyse → Message de commit → Commit créé
                             "feat(auth): add JWT
                              token refresh logic
                              with automatic retry"
```

### 9.2 `/review` — Code review automatique

```
> /review
```

Lance une revue de code complète sur les changements en cours. Claude va :
- Identifier les bugs potentiels
- Vérifier les bonnes pratiques
- Suggérer des améliorations
- Vérifier la sécurité

### 9.3 `/copy` — Copier la dernière réponse

```
> /copy
```

Copie la **dernière réponse de Claude** dans le presse-papier. Utile pour coller un snippet de code, une explication ou une commande dans un autre outil.

### 9.4 `/bug` — Signaler un bug

```
> /bug
```

Envoie un **rapport de bug** directement à Anthropic. Inclut automatiquement des informations de diagnostic (anonymisées) pour aider à identifier le problème.

---

## 10. Commandes dynamiques

### 10.1 Commandes MCP

Les serveurs MCP peuvent exposer leurs propres commandes slash :

```
/mcp__<nom-serveur>__<nom-commande>

# Exemples
/mcp__github__search-issues
/mcp__postgres__query
/mcp__jira__create-ticket
```

### 10.2 Skills personnalisés

Tout **skill** (commande personnalisée) devient automatiquement une commande slash :

```
# Skills personnels (tous les projets)
~/.claude/commands/
├── mon-review.md        → /mon-review
└── generate-tests.md    → /generate-tests

# Skills du projet (partagés via Git)
.claude/commands/
├── deploy.md            → /deploy
└── security-check.md    → /security-check
```

---

## 11. Référencer des fichiers dans les prompts

### 11.1 Avec @ pour mentionner un fichier

Vous pouvez utiliser `@` suivi d'un chemin de fichier pour référencer explicitement un fichier :

```
> Explique le code dans @src/auth/middleware.ts
```

### 11.2 Avec Tab pour l'autocomplétion

Tapez le début d'un chemin et appuyez sur `Tab` :

```
> Lis le fichier src/  [Tab]
# Affiche : src/app.py  src/auth/  src/models/  ...
```

### 11.3 Glisser-déposer (drag & drop)

Dans les terminaux compatibles, vous pouvez **glisser un fichier** directement dans le prompt.

### 11.4 Copier-coller d'images

Claude Code supporte les **images** copiées dans le presse-papier. Utile pour :
- Montrer une maquette UI à implémenter
- Partager une capture d'erreur
- Montrer un diagramme d'architecture

---

## 12. Tableau récapitulatif

### Session & Navigation

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/clear` | Reset total de la conversation | Occasionnel |
| `/compact [instructions]` | Compresser le contexte (orientable) | Fréquent |
| `/resume [session]` | Reprendre une session passée | Fréquent |
| `/rename <nom>` | Nommer la session courante | Occasionnel |
| `/rewind` | Revenir en arrière (messages + code) | Occasionnel |
| `/fork` | Dupliquer la session | Rare |
| `/export [fichier]` | Exporter la conversation | Occasionnel |
| `/quit` / `/exit` | Quitter Claude Code | — |

### Modèle & Configuration

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/model` | Changer de modèle / ajuster l'effort | Fréquent |
| `/config` | Ouvrir les paramètres | Rare |
| `/permissions` | Gérer les permissions des outils | Rare |
| `/fast` | Mode rapide on/off | Occasionnel |
| `/theme` | Changer le thème de couleurs | Rare |
| `/vim` | Mode édition vim | Rare |
| `/plan` | Entrer en mode Plan (lecture seule) | Occasionnel |
| `/output-style` | Configurer le format de réponse | Rare |

### Contexte & Mémoire

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/init` | Créer CLAUDE.md dans le projet | Une fois/projet |
| `/memory` | Éditer les instructions persistantes | Occasionnel |
| `/context` | Visualiser l'utilisation du contexte | Fréquent |
| `/add-dir <chemin>` | Ajouter un répertoire au contexte | Occasionnel |
| `/todos` | Lister les tâches de la session | Occasionnel |

### Diagnostics & Infos

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/cost` | Voir les coûts de la session | Fréquent |
| `/stats` | Statistiques globales d'utilisation | Occasionnel |
| `/usage` | Limites du plan (abonnement) | Rare |
| `/status` | Infos système (version, modèle, compte) | Rare |
| `/doctor` | Diagnostic de l'installation | En cas de problème |
| `/debug [description]` | Dépanner la session courante | En cas de problème |

### Outils & Intégrations

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/tools` | Lister les outils disponibles | Rare |
| `/mcp` | Gérer les serveurs MCP | Rare |
| `/hooks` | Configurer les hooks | Rare |
| `/statusline` | Configurer la barre de statut | Une fois |
| `/terminal-setup` | Installer les raccourcis terminal | Une fois |

### Agents, Tâches & Transfert

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/agents` | Voir/gérer les sous-agents | Occasionnel |
| `/tasks` | Gérer les tâches en arrière-plan | Occasionnel |
| `/teleport` | Importer session depuis claude.ai | Rare |
| `/desktop` | Transférer vers l'app Desktop | Rare |

### Workflow & Utilitaires

| Commande | Usage | Fréquence |
|----------|-------|-----------|
| `/commit` | Créer un commit intelligent | Très fréquent |
| `/review` | Code review automatique | Fréquent |
| `/copy` | Copier la dernière réponse | Occasionnel |
| `/bug` | Signaler un bug à Anthropic | Rare |
| `/help` | Aide intégrée | Rare |

---

## Exercices pratiques

1. Lancez Claude Code et explorez `/help`
2. Exécutez `/doctor` pour vérifier votre installation
3. Lancez `/terminal-setup` pour activer `Shift+Enter`
4. Posez 5 questions, puis utilisez `/compact` — observez le résumé
5. Utilisez `/context` pour voir combien de contexte est utilisé
6. Switchez entre Haiku et Sonnet avec `/model` et comparez les réponses
7. Utilisez `/cost` puis `/stats` pour analyser votre utilisation
8. Initialisez un CLAUDE.md avec `/init` dans un projet
9. Renommez votre session avec `/rename` puis quittez et reprenez avec `/resume`
10. Lancez `/plan` et demandez une analyse sans modification de code

---

## Résumé

```
Commandes Slash = Contrôle complet de Claude Code
│
├── Session     : /clear, /compact, /resume, /rewind, /fork, /export
├── Modèle      : /model, /fast, /plan, /output-style
├── Mémoire     : /init, /memory, /context, /add-dir
├── Diagnostics : /doctor, /debug, /cost, /stats, /status
├── Outils      : /mcp, /hooks, /tools, /terminal-setup
├── Agents      : /agents, /tasks
├── Transfert   : /teleport, /desktop
├── Workflow    : /commit, /review, /copy
├── Dynamiques  : /mcp__*__*, skills personnalisés
└── Fichiers    : @chemin, Tab, drag & drop, images
```

> **Prochain chapitre** : [Gestion de Fichiers & Codebase](04-gestion-fichiers.md)
