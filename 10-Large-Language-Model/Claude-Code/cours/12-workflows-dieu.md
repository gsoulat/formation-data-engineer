# Chapitre 12 : Workflows Dieu - Patterns de Productivité Ultime

## Objectifs

- Maîtriser les workflows qui font la différence entre un utilisateur et un expert
- Combiner toutes les techniques des chapitres précédents
- Atteindre une productivité 10x sur des tâches complexes
- Connaître les patterns utilisés par les meilleurs développeurs avec Claude Code

---

## 1. La philosophie "Dieu"

### 1.1 Les 3 niveaux d'utilisation

```
Niveau "Touriste"          Niveau "Pro"              Niveau "Dieu"
─────────────────          ────────────              ─────────────
"Écris-moi une             CLAUDE.md configuré       Multi-agents parallèles
 fonction"                 Prompts structurés        Hooks automatiques
                           /commit, /review          Pipeline CI/CD intégré
Productivité : x2          Git intégré               MCP servers connectés
                           Productivité : x5         Scripts headless
                                                     Productivité : x10-x20
```

### 1.2 Le principe fondamental

> **Ne faites RIEN que Claude Code pourrait faire pour vous.**
> Votre rôle : réfléchir, décider, valider.
> Le rôle de Claude : explorer, implémenter, tester, documenter.

---

## 2. Workflow Dieu #1 : Le "Full Feature"

### 2.1 De l'idée à la PR en une session

```
Phase 1 : Compréhension              "Explique-moi comment fonctionne
          (2 min)                      le module X actuel"

Phase 2 : Planification              "Je veux ajouter Y. Propose-moi
          (3 min)                      un plan sans coder."

Phase 3 : Validation du plan         Vous lisez, ajustez, validez
          (2 min)

Phase 4 : Implémentation             "Implémente le plan étape par étape.
          (5-15 min)                   Montre-moi chaque étape."

Phase 5 : Tests                       "Ajoute les tests unitaires
          (3 min)                      et d'intégration"

Phase 6 : Review                      /review
          (1 min)

Phase 7 : Fix review                  "Corrige les points soulevés
          (2 min)                      par la review"

Phase 8 : Commit + PR                 /commit puis "crée la PR"
          (1 min)

Total : 20-30 min pour une feature complète avec tests et PR
```

### 2.2 Exemple concret

```
> Explique-moi comment le système de notifications fonctionne actuellement.

[Claude explore et explique]

> Je veux ajouter les notifications par webhook en plus de l'email.
> Avant de coder, propose-moi un plan avec les fichiers à modifier.

[Claude propose un plan]

> Le plan me va. Implémente-le étape par étape. Commence par le modèle,
> puis le service, puis la route API, puis les tests.

[Claude implémente chaque étape]

> /review

[Claude review son propre code — oui, ça marche et c'est utile !]

> Corrige le point sur la validation du payload webhook.

[Claude corrige]

> /commit

[Commit avec message intelligent]

> Crée une PR vers main

[PR créée avec description détaillée]
```

---

## 3. Workflow Dieu #2 : Le "Debugger Expert"

### 3.1 Résolution systématique de bugs

```
Étape 1 : Reproduire
> "Voici l'erreur : [coller l'erreur/stacktrace].
>  Trouve le fichier et la ligne responsable."

Étape 2 : Comprendre
> "Explique-moi POURQUOI ce bug se produit.
>  Quel est le flux d'exécution qui mène à cette erreur ?"

Étape 3 : Explorer
> "Y a-t-il d'autres endroits dans le code qui ont le même problème ?"

Étape 4 : Corriger
> "Corrige le bug ICI et dans tous les autres endroits similaires."

Étape 5 : Prévenir
> "Ajoute un test qui aurait attrapé ce bug."

Étape 6 : Documenter
> /commit (le message expliquera la cause et la correction)
```

### 3.2 Le prompt magique de debug

```
> Voici une erreur de production :
>
> [coller la stacktrace]
>
> 1. Identifie la cause racine
> 2. Montre-moi le chemin d'exécution
> 3. Propose 2-3 solutions (avec tradeoffs)
> 4. Implémente la meilleure solution
> 5. Ajoute un test de régression
```

---

## 4. Workflow Dieu #3 : Le "Refactoring Massif"

### 4.1 Refactoring sûr en 6 étapes

```
Étape 1 : Cartographier
> "Cartographie le module X : dépendances, points d'entrée,
>  couplages. Dessine l'architecture actuelle."

Étape 2 : Cibler
> "Je veux séparer la logique métier de l'accès données.
>  Quels fichiers sont concernés ? Quel est le risque ?"

Étape 3 : Tester d'abord
> "Avant de toucher au code, assure-toi que les tests existants
>  couvrent le comportement actuel. Ajoute les tests manquants."

Étape 4 : Refactorer incrémentalement
> "Refactore UNIQUEMENT [fichier X]. Lance les tests après."
> (Répéter pour chaque fichier)

Étape 5 : Valider
> "Lance TOUS les tests. Vérifie qu'il n'y a aucune régression."

Étape 6 : Review finale
> /review
```

> **Clé** : Jamais de big-bang refactoring. Fichier par fichier, test entre chaque étape.

---

## 5. Workflow Dieu #4 : Le "Multi-modèle"

### 5.1 Utiliser le bon modèle au bon moment

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   OPUS 4.6      │     │   SONNET 4.5     │     │   HAIKU 4.5     │
│                 │     │                  │     │                 │
│  Architecture   │     │  Implémentation  │     │  Questions      │
│  Décisions      │     │  Code review     │     │  rapides        │
│  Bugs complexes │     │  Tests           │     │  Formatage      │
│  Planification  │     │  Refactoring     │     │  Renommage      │
│                 │     │  Features        │     │  Doc simple     │
│  $$$$ mais top  │     │  $$ bon rapport  │     │  $ rapide       │
└─────────────────┘     └──────────────────┘     └─────────────────┘

Stratégie optimale :
1. /model → Opus    : "Planifie l'architecture de la feature X"
2. /model → Sonnet  : "Implémente le plan"
3. /model → Opus    : "Review le code"
4. /model → Sonnet  : "Corrige les issues"
5. /model → Haiku   : "Ajoute les commentaires manquants"
```

### 5.2 Le pattern "Architecte + Ouvrier"

```
# Session 1 : L'Architecte (Opus)
> /model → claude-opus-4-6
> Analyse ce projet et propose une architecture pour ajouter
> le système de permissions RBAC. Ne code pas, juste le plan.
> Mets le plan dans un fichier PLAN.md.

# Session 2 : L'Ouvrier (Sonnet)
> /model → claude-sonnet-4-5
> Lis PLAN.md et implémente le plan étape par étape.
```

---

## 6. Workflow Dieu #5 : Le "Onboarding Projet"

### 6.1 Comprendre un nouveau codebase en 15 minutes

```
Tour 1 :
> Donne-moi une vue d'ensemble de ce projet :
> - Stack technique
> - Architecture
> - Flux de données principal
> - Points d'entrée

Tour 2 :
> Dessine le diagramme de dépendances entre les modules principaux.

Tour 3 :
> Quels sont les patterns de design utilisés ?
> Y a-t-il des anti-patterns ou de la dette technique évidente ?

Tour 4 :
> Montre-moi le flux d'exécution pour [cas d'usage principal].
> Du point d'entrée à la réponse.

Tour 5 :
> Crée un CLAUDE.md complet pour ce projet.
```

### 6.2 Le CLAUDE.md "vivant"

```
> Je viens de passer 15 minutes à explorer le projet avec toi.
> Crée un CLAUDE.md qui capture TOUT ce qu'on a appris :
> - Architecture
> - Conventions
> - Pièges
> - Commandes
> - Flux principaux
```

---

## 7. Workflow Dieu #6 : Le "Test-Driven AI"

### 7.1 TDD assisté par Claude

```
Étape 1 : Écrire les tests d'abord
> "Écris les tests pour une fonction qui calcule le prix
>  avec TVA, remise, et frais de livraison.
>  Cas : normal, remise > prix, livraison gratuite > 50€."

Étape 2 : Vérifier que les tests échouent
> "Lance les tests — ils doivent tous échouer."

Étape 3 : Implémenter le minimum
> "Implémente la fonction pour faire passer TOUS les tests.
>  Le code le plus simple possible."

Étape 4 : Refactorer
> "Les tests passent. Maintenant refactore la fonction
>  pour la rendre plus lisible, sans casser les tests."

Étape 5 : Edge cases
> "Ajoute des tests pour les edge cases que tu imagines
>  et assure-toi qu'ils passent aussi."
```

---

## 8. Workflow Dieu #7 : Le "Pair Programming IA"

### 8.1 L'alternance Humain/IA

```
Le meilleur workflow pour les tâches complexes :

Vous :   "Je veux implémenter X. Voici mon approche : [...]"
Claude : "Bonne approche. Je suggère aussi Y. Voici le plan."
Vous :   "OK, implémente la partie A."
Claude : [implémente A]
Vous :   "Bien. Pour la partie B, je préfère utiliser Z parce que [...]"
Claude : "Compris, j'implémente B avec Z."
Vous :   "Hmm, cette partie me semble fragile. Pourquoi ce choix ?"
Claude : "Parce que [...]. Alternative : [...]"
Vous :   "Utilise l'alternative."
Claude : [modifie]
Vous :   "/review"
Claude : [review]
Vous :   "/commit"
```

**Le secret** : Vous prenez les **décisions**, Claude fait l'**exécution**. C'est du pair programming où vous êtes le senior et Claude le junior ultra-rapide.

---

## 9. Workflow Dieu #8 : Le "Codebase Whisperer"

### 9.1 Maîtriser un codebase de 100K+ lignes

```
Phase 1 : La carte
> "Génère une arborescence des 3 premiers niveaux de dossiers
>  avec une description d'une ligne pour chaque dossier."

Phase 2 : Les points chauds
> "Quels sont les fichiers les plus modifiés selon git log ?
>  Ce sont probablement les plus importants."

Phase 3 : Les connexions
> "Comment le module auth communique-t-il avec le module billing ?
>  Trace le flux de données."

Phase 4 : Les secrets
> "Y a-t-il du code mort ? Des dépendances inutilisées ?
>  Des fichiers de config obsolètes ?"

Phase 5 : Le CLAUDE.md ultime
> "Avec tout ce qu'on a appris, crée le CLAUDE.md le plus complet
>  possible. Il doit permettre à n'importe quel développeur
>  d'être productif en 30 minutes."
```

---

## 10. Les anti-patterns à éviter

### 10.1 L'anti-pattern "Tout en un"

```
❌ "Implémente un système complet de e-commerce avec auth,
    paiement, panier, recherche, et admin panel"

✅ Découpez en 10 sessions de 20 minutes chacune
```

### 10.2 L'anti-pattern "Pas de contexte"

```
❌ Lancer claude dans un nouveau projet sans CLAUDE.md
   → Claude perd 50% de son efficacité

✅ Toujours /init en premier sur un nouveau projet
```

### 10.3 L'anti-pattern "Jamais de review"

```
❌ Implémenter → commit → push → prier

✅ Implémenter → /review → corriger → tests → /commit → PR
```

### 10.4 L'anti-pattern "Un seul modèle"

```
❌ Utiliser Opus pour tout ($$$$ et lent)
❌ Utiliser Haiku pour tout (qualité insuffisante)

✅ Opus pour penser, Sonnet pour coder, Haiku pour les tâches simples
```

### 10.5 L'anti-pattern "Context overflow"

```
❌ Une seule conversation de 2 heures
   → Claude oublie le début

✅ Sessions de 20-30 min
   /compact régulièrement
   Nouveau /clear quand on change de sujet
```

---

## 11. La configuration "Dieu" complète

### 11.1 CLAUDE.md global optimal

```markdown
# ~/.claude/CLAUDE.md

## Préférences
- Répondre en français
- Code et commentaires en anglais
- Concis et direct

## Conventions globales
- Type hints partout (Python)
- TypeScript strict (JS/TS)
- Tests pour tout nouveau code
- Conventional Commits

## Workflow
- Toujours lire avant de modifier
- Toujours tester après modification
- /review avant /commit
- Ne JAMAIS push sans demander
```

### 11.2 Settings.json optimal

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test*)",
      "Bash(npm run lint*)",
      "Bash(pytest*)",
      "Bash(make test*)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git branch*)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if echo $CLAUDE_FILE_PATH | grep -q '\\.py$'; then python -m py_compile $CLAUDE_FILE_PATH 2>&1; fi"
          }
        ]
      }
    ]
  }
}
```

---

## 12. Cheat Sheet — Commandes Dieu

```
Quotidien :
  claude                              → Lancer une session
  claude --continue                   → Reprendre la dernière session
  /compact                            → Libérer du contexte
  /model                              → Switcher de modèle
  /cost                               → Vérifier le coût
  /review                             → Review avant commit
  /commit                             → Commit intelligent

Headless :
  claude -p "prompt"                  → One-shot texte
  cmd | claude -p "prompt"            → Pipe d'entrée
  claude -p --output-format json      → Sortie JSON
  claude -p --max-turns 5             → Limiter les tours

Contexte :
  /init                               → Créer CLAUDE.md
  /memory                             → Éditer les instructions
  @fichier                            → Référencer un fichier
  Tab                                 → Autocompléter les chemins

Raccourcis :
  Escape                              → Annuler l'action en cours
  Escape (x2)                         → Interrompre la génération
  Shift+Enter                         → Nouvelle ligne
  ↑ / ↓                               → Historique des prompts
  Ctrl+C                              → Quitter
```

---

## 13. Dernier conseil

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Le développeur "Dieu" avec Claude Code n'est pas celui qui     │
│  tape le plus vite ou qui connaît toutes les commandes.         │
│                                                                 │
│  C'est celui qui :                                              │
│  1. Sait QUOI demander (vision claire)                          │
│  2. Sait QUAND valider (jugement critique)                      │
│  3. Sait COMMENT itérer (feedback loop rapide)                  │
│                                                                 │
│  Claude Code est un amplificateur.                              │
│  Il amplifie vos compétences, pas les remplace.                 │
│                                                                 │
│  Un développeur moyen + Claude Code = bon développeur           │
│  Un bon développeur + Claude Code = développeur 10x             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Exercice final : Le défi Dieu

**En une session de 30 minutes maximum :**

1. Choisissez un projet existant (le vôtre ou un open source)
2. Créez un CLAUDE.md complet avec `/init` + personnalisation
3. Identifiez un bug ou une feature manquante
4. Utilisez le workflow "Full Feature" :
   - Comprendre → Planifier → Implémenter → Tester → Review → Commit → PR
5. Utilisez au moins 2 modèles différents
6. Utilisez `/compact` au moins une fois
7. Terminez avec `/cost` pour voir combien ça a coûté

**Résultat attendu** : Une PR propre, testée et documentée en 30 minutes.

---

## Résumé final de la formation

```
De Zéro à Dieu — Claude Code
│
├── DÉBUTANT
│   ├── Ch.1  : Installation (npm install -g @anthropic-ai/claude-code)
│   └── Ch.2  : Premiers pas (outils, turns, modes)
│
├── INTERMÉDIAIRE
│   ├── Ch.3  : Commandes slash (/compact, /model, /commit)
│   ├── Ch.4  : Gestion fichiers (Read, Edit, Glob, Grep)
│   ├── Ch.5  : Git & GitHub (commits, PRs, reviews)
│   └── Ch.6  : Permissions (Ask, Auto-edit, Full auto)
│
├── AVANCÉ
│   ├── Ch.7  : CLAUDE.md (le README pour l'IA)
│   ├── Ch.8  : Prompting avancé (7 patterns essentiels)
│   └── Ch.9  : MCP Servers (connecter des outils externes)
│
├── EXPERT
│   ├── Ch.10 : Hooks & CI/CD (automatisation)
│   └── Ch.11 : Headless & SDK (agents programmatiques)
│
└── DIEU
    └── Ch.12 : Workflows ultimes (8 patterns de productivité 10x)
```

---

> **Félicitations !** Vous avez complété la formation "Claude Code : De Zéro à Dieu".
>
> Maintenant, la seule façon de progresser est de **pratiquer**. Utilisez Claude Code
> quotidiennement, expérimentez les patterns, et trouvez VOS workflows optimaux.
