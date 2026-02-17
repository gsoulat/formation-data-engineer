# Chapitre 6 : Modes de Permissions & Sécurité

## Objectifs

- Comprendre le système de permissions de Claude Code
- Configurer les niveaux d'autonomie adaptés à votre workflow
- Sécuriser l'utilisation en environnement d'équipe
- Connaître les protections intégrées

---

## 1. Le système de permissions

### 1.1 Pourquoi des permissions ?

Claude Code peut **lire, écrire, supprimer des fichiers** et **exécuter des commandes shell**. Sans garde-fou, ce serait dangereux :

```
SANS permissions                    AVEC permissions
┌─────────────────────┐            ┌─────────────────────────────────┐
│ "supprime les logs"  │            │ "supprime les logs"             │
│         │            │            │         │                       │
│         ▼            │            │         ▼                       │
│  rm -rf /var/log/*   │            │  Claude veut exécuter :         │
│                      │            │  rm -rf /var/log/*              │
│  EXÉCUTÉ sans        │            │                                 │
│  demander            │            │  Autoriser ? (y/n/always)       │
│                      │            │  → n                            │
│  Oups.               │            │  → Opération annulée            │
└─────────────────────┘            └─────────────────────────────────┘
```

### 1.2 Les trois types de permissions

```
Outils de Claude Code
│
├── Lecture seule (toujours autorisé)
│   ├── Read     → Lire des fichiers
│   ├── Glob     → Chercher des fichiers
│   └── Grep     → Chercher dans le contenu
│
├── Écriture (demande confirmation par défaut)
│   ├── Write    → Créer des fichiers
│   └── Edit     → Modifier des fichiers
│
└── Exécution (demande toujours confirmation)
    └── Bash     → Exécuter des commandes shell
```

---

## 2. Les modes de permission

### 2.1 Mode "Ask" (défaut — recommandé pour débuter)

Demande confirmation pour **chaque action** d'écriture et d'exécution :

```
> Installe express

Claude veut exécuter : npm install express
Autoriser ? (y) oui / (n) non / (a) toujours autoriser
```

### 2.2 Mode "Auto-edit"

Autorise automatiquement les **modifications de fichiers** mais demande confirmation pour les commandes shell :

```
> Ajoute une route /health

Claude modifie src/app.js automatiquement ✓ (pas de demande)
Claude veut exécuter : npm test           ← demande confirmation
```

### 2.3 Mode "Full auto" (Yolo mode)

Autorise **tout** automatiquement. Claude agit sans demander :

```
# Lancer en mode full auto
claude --dangerously-skip-permissions
```

> **Attention** : Ce mode est dangereux. Ne l'utilisez que :
> - Dans un conteneur Docker jetable
> - Dans un environnement CI/CD isolé
> - Pour des tâches bien définies où vous avez confiance

### 2.4 Comparaison des modes

```
                    Ask          Auto-edit      Full auto
                    ─────        ─────────      ─────────
Read fichiers       ✅ Auto      ✅ Auto        ✅ Auto
Glob/Grep           ✅ Auto      ✅ Auto        ✅ Auto
Edit fichiers       ❓ Demande   ✅ Auto        ✅ Auto
Write fichiers      ❓ Demande   ✅ Auto        ✅ Auto
Bash commandes      ❓ Demande   ❓ Demande     ✅ Auto
Bash destructif     ❓ Demande   ❓ Demande     ✅ Auto

Sécurité :          ██████████   ██████░░░░     ██░░░░░░░░
Productivité :      ██████░░░░   ████████░░     ██████████
```

---

## 3. Configuration des permissions

### 3.1 Fichier settings.json global

```json
// ~/.claude/settings.json
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(python -m pytest*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Bash(curl*)"
    ]
  }
}
```

### 3.2 Fichier .claude/settings.json (par projet)

```json
// mon-projet/.claude/settings.json
{
  "permissions": {
    "allow": [
      "Bash(docker compose up*)",
      "Bash(make *)",
      "Bash(cargo test*)"
    ],
    "deny": [
      "Bash(docker system prune*)"
    ]
  }
}
```

### 3.3 Les patterns de permissions

```
Syntaxe des permissions
│
├── Exact match     : "Bash(npm test)"           → uniquement "npm test"
├── Wildcard        : "Bash(npm *)"              → tout ce qui commence par "npm "
├── Outil seul      : "Edit"                     → toute modification de fichier
└── Outil + pattern : "Bash(git commit*)"        → git commit avec n'importe quels args
```

### 3.4 Autoriser pendant la session

Quand Claude demande une permission, vous pouvez répondre :

| Réponse | Effet |
|---------|-------|
| `y` (yes) | Autorise cette fois uniquement |
| `n` (no) | Refuse cette fois |
| `a` (always) | Autorise toujours cette commande exacte |

Les permissions "always" sont sauvegardées dans le fichier settings.json du projet.

---

## 4. Protections intégrées

### 4.1 Ce que Claude Code refuse toujours

Même en mode "full auto", certaines protections existent :

```
Protections permanentes
│
├── Git
│   ├── ❌ git push --force sur main/master
│   ├── ❌ git reset --hard sans confirmation
│   ├── ❌ git branch -D sans confirmation
│   └── ⚠️  Avertissement si commit de .env / secrets
│
├── Fichiers sensibles
│   ├── ⚠️  Avertissement pour .env, credentials.json
│   ├── ⚠️  Avertissement pour clés privées SSH
│   └── ⚠️  Avertissement pour tokens/secrets
│
└── Commandes destructives
    ├── ⚠️  rm -rf avec chemins larges
    └── ⚠️  Commandes irréversibles
```

### 4.2 Le principe de moindre surprise

Claude Code suit le principe : **ne jamais faire plus que ce qui est demandé**.

```
Demande : "Corrige le bug dans login.py"

CE QUE CLAUDE FAIT :                CE QUE CLAUDE NE FAIT PAS :
✅ Lit login.py                     ❌ Refactore tout le module
✅ Identifie le bug                 ❌ Ajoute des features
✅ Corrige le bug                   ❌ Modifie d'autres fichiers
✅ Explique la correction           ❌ Push les changements
```

### 4.3 Sandbox et isolation

Claude Code s'exécute dans un **sandbox** limité :
- Accès uniquement au répertoire du projet et ses sous-dossiers
- Pas d'accès réseau sauf via les outils dédiés (WebFetch)
- Les commandes Bash sont sandboxées

---

## 5. Sécurité en équipe

### 5.1 Configuration partagée

Utilisez `.claude/settings.json` dans le repo pour partager les règles :

```json
// .claude/settings.json (committé dans le repo)
{
  "permissions": {
    "allow": [
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)"
    ],
    "deny": [
      "Bash(npm publish*)",
      "Bash(rm -rf *)"
    ]
  }
}
```

### 5.2 Hiérarchie des configurations

```
Priorité des settings (du plus prioritaire au moins) :

1. Flags en ligne de commande     (--dangerously-skip-permissions)
2. .claude/settings.json local    (dans le projet, non committé)
3. .claude/settings.json repo     (committé, partagé)
4. ~/.claude/settings.json        (global utilisateur)
5. Paramètres par défaut          (mode "Ask")
```

### 5.3 Bonnes pratiques d'équipe

```
✅ Committez .claude/settings.json avec des permissions raisonnables
✅ Documentez les permissions dans CLAUDE.md
✅ Utilisez le mode "Ask" pour les nouveaux membres
✅ Autorisez uniquement les commandes de test/lint en "always"

❌ Ne mettez jamais --dangerously-skip-permissions en CI sans sandbox
❌ Ne donnez pas "always" à des commandes destructives
❌ Ne partagez pas de clés API via CLAUDE.md
```

---

## 6. Audit et traçabilité

### 6.1 Historique des conversations

Chaque conversation est sauvegardée dans `~/.claude/projects/`. Vous pouvez auditer ce que Claude a fait :

```bash
# Les conversations sont stockées localement
ls ~/.claude/projects/
```

### 6.2 Logs des commandes

Chaque commande exécutée par Claude est visible dans le terminal avec l'indicateur :

```
● Bash npm test                    ← Vous voyez chaque commande
● Edit src/app.py                  ← Vous voyez chaque modification
```

---

## Exercices pratiques

### Exercice 1 : Configuration de permissions
1. Créez un fichier `.claude/settings.json` dans un projet
2. Autorisez `npm test` et `npm run lint`
3. Bloquez `rm -rf`
4. Testez que les permissions fonctionnent

### Exercice 2 : Test des protections
1. Demandez à Claude de `git push --force main`
2. Demandez à Claude de commit un fichier `.env`
3. Observez les avertissements

### Exercice 3 : Mode auto-edit
1. Basculez en mode auto-edit
2. Demandez des modifications de code
3. Observez que les edits passent sans confirmation
4. Observez que les commandes Bash demandent toujours

---

## Résumé

```
Permissions Claude Code
│
├── Modes     : Ask (sûr) → Auto-edit (confort) → Full auto (YOLO)
├── Config    : ~/.claude/settings.json (global)
│               .claude/settings.json (projet)
├── Patterns  : "Bash(commande*)" — allow / deny
├── Sécurité  : Push force interdit, alertes secrets
├── Équipe    : Config partagée via repo
└── Audit     : Historique conversations + logs commandes
```

> **Prochain chapitre** : [CLAUDE.md & Configuration Projet](07-claude-md.md)
