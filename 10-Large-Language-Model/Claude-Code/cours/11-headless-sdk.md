# Chapitre 11 : Mode Headless & SDK Agent

## Objectifs

- Maîtriser le mode headless pour l'automatisation
- Comprendre le Claude Code SDK pour créer des agents
- Construire des pipelines automatisés avec Claude Code
- Intégrer Claude Code dans des applications custom

---

## 1. Le mode Headless

### 1.1 Qu'est-ce que le mode headless ?

Le mode headless = Claude Code **sans interface interactive**. Il s'exécute comme un script, parfait pour l'automatisation :

```
Mode Interactif                   Mode Headless
┌─────────────────────┐          ┌─────────────────────────────────┐
│ Humain tape          │          │ Script envoie un prompt         │
│ Claude répond         │          │ Claude exécute                  │
│ Humain valide         │          │ Claude retourne le résultat     │
│ Claude continue       │          │ Script traite le résultat       │
│                      │          │                                 │
│ INTERACTIF           │          │ AUTOMATIQUE                     │
└─────────────────────┘          └─────────────────────────────────┘
```

### 1.2 Les flags essentiels

```bash
# Mode print : réponse texte simple (pas d'outils)
claude -p "explique ce code"

# Mode print avec outils (+ auto-accept des permissions)
claude -p --dangerously-skip-permissions "corrige les bugs dans src/"

# Format de sortie JSON
claude -p --output-format json "liste les fichiers Python"

# Format streaming JSON (pour le traitement en temps réel)
claude -p --output-format stream-json "analyse le projet"

# Timeout (en secondes)
claude -p --max-turns 10 "résous ce problème"

# Spécifier le modèle
claude -p --model claude-opus-4-6 "architecture ce système"
```

### 1.3 Entrée via stdin (pipe)

```bash
# Pipe un fichier
cat error.log | claude -p "explique ces erreurs"

# Pipe un diff
git diff | claude -p "review ce changement"

# Pipe une commande
curl -s api.example.com/health | claude -p "cette API est-elle saine ?"

# Pipe multi-lignes
echo "Contexte: API e-commerce
Question: Comment optimiser les requêtes de recherche produit ?" | claude -p
```

---

## 2. Automatisation avancée avec le mode Headless

### 2.1 Script de review quotidienne

```bash
#!/bin/bash
# daily-review.sh

echo "=== Review quotidienne $(date +%Y-%m-%d) ==="

# 1. Résumé des changements depuis hier
echo "## Changements récents"
git log --since="1 day ago" --oneline | \
  claude -p "Résume ces commits en catégories (features, fixes, chores)"

# 2. Analyse de la qualité
echo "## Qualité du code"
claude -p --max-turns 20 \
  "Analyse la qualité du code dans src/ :
   - Complexité cyclomatique élevée ?
   - Code dupliqué ?
   - Fonctions trop longues ?
   Donne un score /10 et les 3 points les plus urgents."

# 3. TODOs et FIXMEs
echo "## Actions à faire"
claude -p "Liste tous les TODO et FIXME avec le fichier et la ligne"
```

### 2.2 Génération de documentation automatique

```bash
#!/bin/bash
# generate-docs.sh

# Pour chaque fichier Python dans src/
for file in $(find src/ -name "*.py" -not -path "*/test*"); do
  echo "Documenting $file..."
  claude -p --dangerously-skip-permissions \
    "Ajoute des docstrings Google-style à toutes les fonctions publiques
     de $file qui n'en ont pas. Ne modifie PAS les docstrings existantes."
done

echo "Documentation générée !"
```

### 2.3 Migration de code automatique

```bash
#!/bin/bash
# migrate-to-typescript.sh

# Convertir chaque fichier JS en TS
for file in $(find src/ -name "*.js"); do
  ts_file="${file%.js}.ts"
  echo "Converting $file → $ts_file..."

  claude -p --dangerously-skip-permissions \
    "Convertis $file en TypeScript :
     - Ajoute les types aux paramètres et retours de fonctions
     - Remplace require() par import
     - Ajoute les interfaces nécessaires
     - Le fichier de sortie est $ts_file"
done
```

---

## 3. Format de sortie JSON

### 3.1 Output structuré

```bash
# Obtenir un résultat JSON structuré
claude -p --output-format json \
  "Analyse ce projet et retourne un JSON avec :
   - languages (array de strings)
   - frameworks (array de strings)
   - quality_score (number 1-10)
   - issues (array d'objets {file, line, description})"
```

Résultat :
```json
{
  "type": "result",
  "result": "```json\n{\"languages\": [\"Python\", \"JavaScript\"], ...}\n```",
  "cost_usd": 0.042,
  "input_tokens": 1523,
  "output_tokens": 287
}
```

### 3.2 Stream JSON pour le traitement en temps réel

```bash
# Chaque ligne est un événement JSON
claude -p --output-format stream-json "analyse le projet" | \
  while IFS= read -r line; do
    type=$(echo "$line" | jq -r '.type')
    case $type in
      "assistant")
        echo "Claude dit : $(echo $line | jq -r '.message')"
        ;;
      "tool_use")
        echo "Outil utilisé : $(echo $line | jq -r '.tool')"
        ;;
      "result")
        echo "Terminé ! Coût : $(echo $line | jq -r '.cost_usd')"
        ;;
    esac
  done
```

---

## 4. Le Claude Code SDK (Agent SDK)

### 4.1 Qu'est-ce que le SDK ?

Le SDK permet de **programmer Claude Code** depuis du code TypeScript/JavaScript. Vous construisez des agents custom :

```
CLI Claude Code                    SDK Claude Code
┌─────────────────────┐           ┌──────────────────────────────┐
│ Terminal interactif  │           │ Code TypeScript              │
│                      │           │                              │
│ Utilisateur humain   │           │ Votre application contrôle   │
│ tape des prompts     │           │ Claude programmatiquement    │
│                      │           │                              │
│ 1 conversation       │           │ N conversations en parallèle │
│                      │           │ Logique custom               │
│                      │           │ Orchestration multi-agents   │
└─────────────────────┘           └──────────────────────────────┘
```

### 4.2 Installation du SDK

```bash
npm install @anthropic-ai/claude-code
```

### 4.3 Usage basique

```typescript
import { claude } from "@anthropic-ai/claude-code";

// Simple query
const result = await claude("Explique ce fichier", {
  cwd: "/chemin/vers/projet",
  model: "claude-sonnet-4-5-20250929"
});

console.log(result.text);
console.log(`Coût : $${result.cost_usd}`);
```

### 4.4 Avec streaming

```typescript
import { claude } from "@anthropic-ai/claude-code";

// Streaming pour voir la progression
const stream = claude("Refactore src/app.py", {
  cwd: "/chemin/vers/projet",
  stream: true,
  dangerouslySkipPermissions: true  // attention !
});

for await (const event of stream) {
  if (event.type === "text") {
    process.stdout.write(event.text);
  } else if (event.type === "tool_use") {
    console.log(`\n[Outil: ${event.tool}]`);
  }
}
```

### 4.5 Multi-conversations

```typescript
import { claude } from "@anthropic-ai/claude-code";

// Lancer plusieurs analyses en parallèle
const results = await Promise.all([
  claude("Analyse la sécurité de src/auth/", { cwd: projectPath }),
  claude("Analyse la performance de src/api/", { cwd: projectPath }),
  claude("Analyse la qualité des tests/", { cwd: projectPath }),
]);

console.log("Sécurité :", results[0].text);
console.log("Performance :", results[1].text);
console.log("Tests :", results[2].text);
```

---

## 5. Construire un agent custom

### 5.1 Agent de monitoring de code

```typescript
import { claude } from "@anthropic-ai/claude-code";
import { watch } from "fs";

// Agent qui surveille les changements et donne du feedback
watch("./src", { recursive: true }, async (event, filename) => {
  if (!filename?.endsWith(".py")) return;

  console.log(`Fichier modifié : ${filename}`);

  const review = await claude(
    `Le fichier src/${filename} vient d'être modifié.
     Fais une review rapide : bugs, typos, style.
     Sois très concis (max 3 lignes).`,
    {
      cwd: process.cwd(),
      model: "claude-haiku-4-5-20251001"  // Rapide et pas cher
    }
  );

  console.log(`Review : ${review.text}\n`);
});
```

### 5.2 Agent de résolution d'issues

```typescript
import { claude } from "@anthropic-ai/claude-code";
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

async function resolveIssue(owner: string, repo: string, issueNumber: number) {
  // 1. Récupérer l'issue
  const { data: issue } = await octokit.issues.get({
    owner, repo, issue_number: issueNumber
  });

  // 2. Demander à Claude de résoudre
  const result = await claude(
    `Voici une issue GitHub à résoudre :
     Titre : ${issue.title}
     Description : ${issue.body}

     Analyse le code, propose et implémente une solution.
     Crée les tests nécessaires.`,
    {
      cwd: `/path/to/${repo}`,
      dangerouslySkipPermissions: true
    }
  );

  // 3. Créer une branche et un commit
  await claude(
    `Crée une branche fix/issue-${issueNumber} et committe les changements
     avec le message "fix: resolve #${issueNumber} - ${issue.title}"`,
    {
      cwd: `/path/to/${repo}`,
      dangerouslySkipPermissions: true
    }
  );

  console.log(`Issue #${issueNumber} résolue !`);
}
```

### 5.3 Pipeline multi-agents

```typescript
import { claude } from "@anthropic-ai/claude-code";

async function fullPipeline(feature: string) {
  const projectPath = "/path/to/project";

  // Agent 1 : Architecte (Opus pour la réflexion)
  console.log("Phase 1 : Architecture...");
  const plan = await claude(
    `Planifie l'implémentation de : "${feature}".
     Liste les fichiers à créer/modifier et le plan étape par étape.`,
    { cwd: projectPath, model: "claude-opus-4-6" }
  );

  // Agent 2 : Développeur (Sonnet pour le code)
  console.log("Phase 2 : Implémentation...");
  await claude(
    `Voici le plan d'implémentation :
     ${plan.text}

     Implémente-le.`,
    {
      cwd: projectPath,
      model: "claude-sonnet-4-5-20250929",
      dangerouslySkipPermissions: true
    }
  );

  // Agent 3 : Testeur (Sonnet)
  console.log("Phase 3 : Tests...");
  await claude(
    `Crée des tests complets pour la feature "${feature}"
     qui vient d'être implémentée.`,
    {
      cwd: projectPath,
      model: "claude-sonnet-4-5-20250929",
      dangerouslySkipPermissions: true
    }
  );

  // Agent 4 : Reviewer (Opus pour la rigueur)
  console.log("Phase 4 : Review...");
  const review = await claude(
    `Fais une code review complète des changements récents.
     Vérifie : bugs, sécurité, tests, documentation.`,
    { cwd: projectPath, model: "claude-opus-4-6" }
  );

  console.log("Review finale :", review.text);
}
```

---

## 6. Bonnes pratiques du mode Headless

### 6.1 Gestion des erreurs

```bash
# Toujours vérifier le code de sortie
if claude -p "vérifie la syntaxe de src/" 2>/dev/null; then
  echo "Tout est OK"
else
  echo "Erreur Claude Code"
  exit 1
fi
```

### 6.2 Limiter les coûts

```bash
# Limiter le nombre de tours
claude -p --max-turns 5 "analyse rapide"

# Utiliser Haiku pour les tâches simples
claude -p --model claude-haiku-4-5-20251001 "résume ce fichier"
```

### 6.3 Sécurité en headless

```
✅ Utilisez --dangerously-skip-permissions UNIQUEMENT dans :
   - Conteneurs Docker jetables
   - CI/CD avec sandbox
   - Environnements de test

❌ JAMAIS sur :
   - Votre machine de dev principale
   - Un serveur de production
   - Un environnement partagé
```

---

## Exercices pratiques

### Exercice 1 : Script headless
Créez un script bash qui :
1. Récupère les 5 derniers commits
2. Les envoie à Claude pour un résumé
3. Sauvegarde le résumé dans un fichier

### Exercice 2 : Pipeline CI
Créez un workflow GitHub Actions qui :
1. Se déclenche sur les PRs
2. Fait une code review automatique
3. Poste le résultat en commentaire

### Exercice 3 : Agent SDK
Avec le SDK TypeScript :
1. Créez un script qui analyse 3 dossiers en parallèle
2. Combine les résultats
3. Génère un rapport Markdown

---

## Résumé

```
Headless & SDK
│
├── Mode Headless
│   ├── -p (print mode)
│   ├── --output-format json/stream-json
│   ├── --max-turns (limiter)
│   ├── stdin pipe (cat, git diff...)
│   └── --dangerously-skip-permissions (CI only!)
│
├── SDK TypeScript
│   ├── import { claude } from "@anthropic-ai/claude-code"
│   ├── Simple query → claude("prompt", options)
│   ├── Streaming → for await (const event of stream)
│   └── Multi-conversations en parallèle
│
├── Agents custom
│   ├── Monitoring de code
│   ├── Résolution d'issues
│   └── Pipeline multi-agents
│
└── Sécurité
    └── Skip permissions = sandbox UNIQUEMENT
```

> **Prochain chapitre** : [Workflows Dieu - Patterns de Productivité Ultime](12-workflows-dieu.md)
