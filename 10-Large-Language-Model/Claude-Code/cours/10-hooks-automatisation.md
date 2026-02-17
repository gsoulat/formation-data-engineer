# Chapitre 10 : Hooks, Automatisation & CI/CD

## Objectifs

- Comprendre le système de hooks de Claude Code
- Créer des hooks pour automatiser des vérifications
- Intégrer Claude Code dans des pipelines CI/CD
- Automatiser des workflows de développement

---

## 1. Qu'est-ce que les Hooks ?

### 1.1 Le concept

Les hooks sont des **commandes shell** qui s'exécutent automatiquement en réponse à des **événements** de Claude Code :

```
Événement Claude Code          Hook (votre commande)
┌─────────────────────┐       ┌─────────────────────────────┐
│ Claude veut modifier │──────▶│ Linter automatique          │
│ un fichier           │       │ "eslint --fix fichier.js"   │
└─────────────────────┘       └─────────────────────────────┘

┌─────────────────────┐       ┌─────────────────────────────┐
│ Claude a exécuté     │──────▶│ Notification Slack          │
│ une commande Bash    │       │ "curl -X POST slack.com/..."│
└─────────────────────┘       └─────────────────────────────┘

┌─────────────────────┐       ┌─────────────────────────────┐
│ Nouvelle conversation│──────▶│ Charger contexte custom     │
│ démarre              │       │ "cat .project-context"      │
└─────────────────────┘       └─────────────────────────────┘
```

### 1.2 Les types d'événements

```
Événements de hooks
│
├── PreToolUse     → Avant qu'un outil soit utilisé
│                    (peut bloquer l'exécution)
│
├── PostToolUse    → Après qu'un outil a été utilisé
│                    (peut donner du feedback)
│
├── Notification   → Quand Claude envoie une notification
│
└── Stop           → Quand Claude finit de répondre
```

---

## 2. Configurer des hooks

### 2.1 Dans settings.json

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Un fichier va être modifié : $CLAUDE_FILE_PATH'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix $CLAUDE_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 2.2 Structure d'un hook

```json
{
  "matcher": "NomDeLOutil",   // Quel outil déclenche le hook
  "hooks": [
    {
      "type": "command",       // Type : commande shell
      "command": "ma-commande" // La commande à exécuter
    }
  ]
}
```

### 2.3 Les matchers disponibles

| Matcher | Déclencheur |
|---------|-------------|
| `"Edit"` | Modification de fichier |
| `"Write"` | Création de fichier |
| `"Bash"` | Exécution de commande |
| `"Read"` | Lecture de fichier |
| `""` (vide) | Tous les outils |

---

## 3. Exemples de hooks pratiques

### 3.1 Linter automatique après chaque modification

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null; npx eslint --fix $CLAUDE_FILE_PATH 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### 3.2 Bloquer les modifications sur certains fichiers

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if echo $CLAUDE_FILE_PATH | grep -q 'migrations/'; then echo 'BLOCKED: Ne pas modifier les migrations existantes' && exit 1; fi"
          }
        ]
      }
    ]
  }
}
```

### 3.3 Lancer les tests après chaque modification

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npm test --silent 2>&1 | tail -5"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Ajouter du contexte au démarrage

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Session terminée à $(date). Tokens utilisés : voir /cost'"
          }
        ]
      }
    ]
  }
}
```

---

## 4. Claude Code en CI/CD

### 4.1 Le mode Headless (non-interactif)

Pour utiliser Claude Code en CI/CD, utilisez le mode **non-interactif** :

```bash
# Mode print : juste une réponse texte
claude -p "analyse ce code et liste les problèmes"

# Mode non-interactif avec outils mais auto-accept
claude --dangerously-skip-permissions -p "lance les tests et corrige les erreurs"
```

### 4.2 GitHub Actions : Code Review automatique

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Run Code Review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Récupérer le diff de la PR
          DIFF=$(git diff origin/main...HEAD)

          # Demander à Claude de reviewer
          claude -p "Voici le diff d'une PR. Fais une code review concise.
          Focus : bugs, sécurité, performance.
          Diff:
          $DIFF" > review.md

          # Poster le commentaire sur la PR
          gh pr comment ${{ github.event.pull_request.number }} \
            --body "$(cat review.md)"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4.3 GitHub Actions : Génération de tests

```yaml
# .github/workflows/claude-tests.yml
name: Claude Generate Tests

on:
  workflow_dispatch:
    inputs:
      file:
        description: 'Fichier à tester'
        required: true

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Generate Tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --dangerously-skip-permissions \
            "Crée des tests unitaires complets pour ${{ inputs.file }}.
             Utilise les conventions de test existantes du projet."

      - name: Create PR with tests
        run: |
          git checkout -b auto/tests-$(date +%s)
          git add -A
          git commit -m "test: auto-generated tests for ${{ inputs.file }}"
          git push -u origin HEAD
          gh pr create --title "Auto-generated tests" \
            --body "Tests générés par Claude Code pour ${{ inputs.file }}"
```

### 4.4 GitLab CI

```yaml
# .gitlab-ci.yml
claude-review:
  stage: review
  image: node:22
  script:
    - npm install -g @anthropic-ai/claude-code
    - |
      claude -p "Review le diff suivant et donne un score de qualité /10 :
      $(git diff origin/main...HEAD)" > review.txt
    - cat review.txt
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
```

---

## 5. Automatisation locale

### 5.1 Script de développement quotidien

```bash
#!/bin/bash
# dev-start.sh — Script de démarrage quotidien

# 1. Mettre à jour le projet
git pull origin main

# 2. Demander à Claude un résumé des changements récents
claude -p "Résume les changements des 3 derniers commits en bullet points"

# 3. Lister les TODOs
claude -p "Liste tous les TODO et FIXME dans le code source"
```

### 5.2 Script de pre-commit

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Demander à Claude de vérifier les changements
DIFF=$(git diff --cached)

if [ -n "$DIFF" ]; then
  REVIEW=$(claude -p "Vérifie ce diff pour des bugs évidents,
  des secrets exposés, ou des problèmes de sécurité.
  Réponds UNIQUEMENT 'OK' si tout va bien, ou liste les problèmes.
  Diff: $DIFF")

  if [ "$REVIEW" != "OK" ]; then
    echo "Claude a détecté des problèmes :"
    echo "$REVIEW"
    echo ""
    echo "Commit quand même ? (utilisez git commit --no-verify pour forcer)"
    exit 1
  fi
fi
```

### 5.3 Alias shell utiles

```bash
# ~/.bashrc ou ~/.zshrc

# Review rapide des changements
alias cr='claude -p "Review rapide de mes changements : $(git diff)"'

# Générer un message de commit
alias ccm='claude -p "Génère un message de commit Conventional Commits pour : $(git diff --staged)"'

# Expliquer une erreur
alias cexplain='claude -p "Explique cette erreur et propose une solution :"'

# Documentation rapide
alias cdoc='claude -p "Génère la documentation pour"'
```

---

## 6. Patterns d'automatisation avancés

### 6.1 Le "Guardian" — Protection continue

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '(rm -rf|drop table|truncate)'; then echo 'BLOCKED: Commande destructive détectée' && exit 1; fi"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python -m py_compile \"$CLAUDE_FILE_PATH\" 2>&1 || echo 'WARNING: Erreur de syntaxe Python'"
          }
        ]
      }
    ]
  }
}
```

### 6.2 Le "Reporter" — Logs d'activité

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date +%H:%M:%S) - $CLAUDE_TOOL_NAME: $CLAUDE_FILE_PATH\" >> .claude/activity.log"
          }
        ]
      }
    ]
  }
}
```

---

## 7. Exercices pratiques

### Exercice 1 : Hook de linting
1. Configurez un hook PostToolUse qui lance le linter après chaque Edit
2. Testez en demandant à Claude de modifier un fichier
3. Vérifiez que le linter s'exécute

### Exercice 2 : Hook de protection
1. Créez un hook PreToolUse qui bloque les modifications dans le dossier `migrations/`
2. Testez en demandant à Claude de modifier un fichier de migration
3. Vérifiez que c'est bloqué

### Exercice 3 : GitHub Actions
1. Créez un workflow qui fait une code review automatique sur les PRs
2. Testez en créant une PR

### Exercice 4 : Alias shell
1. Créez 3 alias Claude Code utiles pour votre workflow
2. Testez-les sur votre projet

---

## Résumé

```
Hooks & Automatisation
│
├── Hooks
│   ├── PreToolUse  → Avant (peut bloquer)
│   ├── PostToolUse → Après (feedback, lint, tests)
│   ├── Notification → Messages
│   └── Stop        → Fin de réponse
│
├── CI/CD
│   ├── Mode -p (print) pour les scripts
│   ├── GitHub Actions → Code review auto
│   ├── GitLab CI → Review en pipeline
│   └── --dangerously-skip-permissions pour CI isolée
│
├── Automatisation locale
│   ├── Scripts de dev
│   ├── Pre-commit hooks
│   └── Alias shell
│
└── Patterns
    ├── Guardian (protection)
    └── Reporter (logs)
```

> **Prochain chapitre** : [Mode Headless & SDK Agent](11-headless-sdk.md)
