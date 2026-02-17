# Chapitre 5 : Git & GitHub Intégré

## Objectifs

- Utiliser Claude Code pour automatiser les opérations Git
- Créer des commits avec des messages intelligents
- Créer et gérer des Pull Requests depuis le terminal
- Faire des code reviews automatiques
- Résoudre des conflits de merge avec l'aide de l'IA

---

## 1. Pourquoi Git + Claude Code = puissant

```
Git classique                        Git + Claude Code
┌─────────────────────────┐         ┌─────────────────────────────────┐
│                         │         │                                 │
│ git add .               │         │ "commit mes changements"        │
│ git diff --staged       │         │                                 │
│ *réfléchit au message*  │         │ Claude analyse le diff,         │
│ git commit -m "fix bug" │         │ comprend LE SENS des changes,   │
│                         │         │ écrit un message pertinent,     │
│ *ouvre GitHub*           │         │ et commit.                      │
│ *crée la PR à la main*  │         │                                 │
│ *écrit la description*  │         │ "crée une PR"                   │
│                         │         │ → PR créée avec description     │
│ *relit le code*         │         │   détaillée automatiquement     │
│ *écrit les commentaires*│         │                                 │
└─────────────────────────┘         └─────────────────────────────────┘
     5-10 minutes                          30 secondes
```

---

## 2. Commits intelligents

### 2.1 La commande `/commit`

```
> /commit
```

Claude Code va :
1. Exécuter `git status` pour voir les fichiers modifiés
2. Exécuter `git diff` pour voir les changements
3. Lire les commits récents pour respecter le style
4. Analyser le **sens** des modifications
5. Générer un message de commit approprié
6. Créer le commit

### 2.2 Commit en langage naturel

```
> Commit les changements avec un message qui décrit bien ce que j'ai fait
```

### 2.3 Conventions de commit

Claude Code respecte automatiquement les **Conventional Commits** s'il détecte que le projet les utilise :

```
feat(auth): add JWT token refresh with automatic retry
^    ^      ^
│    │      └── Description
│    └── Scope (module concerné)
└── Type (feat, fix, docs, refactor, test, chore)
```

Types courants :
| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `refactor` | Refactoring sans changement fonctionnel |
| `test` | Ajout/modification de tests |
| `chore` | Maintenance (deps, config, CI) |
| `style` | Formatage, espaces, points-virgules |
| `perf` | Amélioration de performance |

### 2.4 Commit sélectif

```
> Commit seulement les fichiers dans src/auth/ avec le message
> "feat(auth): implement password reset flow"
```

Claude va `git add` uniquement les fichiers concernés.

---

## 3. Pull Requests automatiques

### 3.1 Créer une PR

```
> Crée une pull request pour cette branche
```

Claude Code va :
1. Vérifier les changements par rapport à la branche principale
2. Pousser la branche si nécessaire
3. Générer un titre et une description
4. Créer la PR via `gh pr create`

### 3.2 Format de PR généré

```markdown
## Summary
- Add JWT token refresh mechanism
- Implement automatic retry on 401 responses
- Add unit tests for token refresh flow

## Test plan
- [ ] Run existing auth test suite
- [ ] Test token expiration scenario
- [ ] Verify retry logic with mock server
```

### 3.3 PR avec contexte personnalisé

```
> Crée une PR qui explique :
> - Pourquoi on migre de sessions vers JWT
> - Les impacts sur les clients existants
> - Comment tester la migration
```

---

## 4. Code Review automatique

### 4.1 Review des changements locaux

```
> /review
```

Claude analyse vos changements non commités et donne un feedback détaillé.

### 4.2 Review d'une PR existante

```
> Fais une code review de la PR #42
```

Claude va :
1. Récupérer les détails de la PR via `gh pr view 42`
2. Lire le diff complet
3. Analyser chaque changement
4. Fournir un feedback structuré

### 4.3 Ce que Claude vérifie dans une review

```
Code Review Claude Code
│
├── Bugs potentiels
│   ├── Null pointer / undefined
│   ├── Race conditions
│   ├── Edge cases non gérés
│   └── Erreurs de logique
│
├── Sécurité
│   ├── Injection SQL/XSS
│   ├── Secrets exposés
│   ├── Validation des inputs
│   └── Authentification/autorisation
│
├── Qualité
│   ├── Code dupliqué
│   ├── Complexité excessive
│   ├── Nommage peu clair
│   └── Patterns anti-patterns
│
├── Performance
│   ├── Requêtes N+1
│   ├── Boucles inefficaces
│   └── Mémoire / fuites
│
└── Maintenabilité
    ├── Tests manquants
    ├── Documentation
    └── Cohérence avec le style existant
```

---

## 5. Gestion des branches

### 5.1 Créer une branche

```
> Crée une branche feature/user-profile à partir de main
```

### 5.2 Naviguer entre les branches

```
> Quelles branches existent et sur laquelle je suis ?
```

### 5.3 Comparer des branches

```
> Montre-moi les différences entre main et feature/auth
```

---

## 6. Résolution de conflits

### 6.1 Identifier les conflits

```
> J'ai des conflits de merge, aide-moi à les résoudre
```

Claude va :
1. Identifier les fichiers en conflit
2. Lire les deux versions
3. Comprendre l'intention de chaque modification
4. Proposer une résolution

### 6.2 Résolution intelligente

```
# Claude comprend le SENS des deux modifications :

<<<<<<< HEAD
def calculate_price(item):
    return item.base_price * 1.20  # TVA 20%
=======
def calculate_price(item, discount=0):
    return item.base_price - discount
>>>>>>> feature/discounts

# Claude propose :
def calculate_price(item, discount=0):
    return (item.base_price - discount) * 1.20  # TVA 20%
```

---

## 7. Opérations Git avancées

### 7.1 Analyser l'historique

```
> Quand est-ce que le bug dans calculate_price a été introduit ?
> Quel commit a cassé les tests ?
```

Claude utilise `git log`, `git blame`, et `git bisect` pour investiguer.

### 7.2 Cherry-pick intelligent

```
> Applique le fix du commit abc123 sur la branche release/2.0
```

### 7.3 Rebase interactif assisté

```
> Nettoie l'historique de ma branche :
> - Squash les commits "WIP"
> - Garde les commits significatifs
> - Réécris les messages si nécessaire
```

### 7.4 Gestion des tags

```
> Crée un tag v2.1.0 avec un changelog basé sur les commits depuis v2.0.0
```

---

## 8. Intégration GitHub (via `gh` CLI)

Claude Code utilise le CLI GitHub (`gh`) pour interagir avec GitHub :

### 8.1 Issues

```
> Liste les issues ouvertes labellées "bug"
> Crée une issue pour le bug de calcul de TVA
```

### 8.2 Pull Requests

```
> Liste mes PRs ouvertes
> Montre-moi les commentaires sur la PR #42
> Merge la PR #42 en squash
```

### 8.3 Actions / CI

```
> Quel est le statut du CI sur ma branche ?
> Pourquoi le workflow de test a échoué ?
```

### 8.4 Releases

```
> Crée une release v2.1.0 avec les notes basées sur les PRs mergées
```

---

## 9. Bonnes pratiques Git avec Claude Code

### 9.1 Workflow recommandé

```
1. Créer une branche         > "crée une branche feature/xxx"
2. Implémenter               > "implémente la fonctionnalité xxx"
3. Tester                    > "lance les tests"
4. Review                    > /review
5. Commit                    > /commit
6. Push + PR                 > "crée une PR"
```

### 9.2 Ce qu'il ne faut PAS faire

```
# JAMAIS : Push force sur main sans réfléchir
> push force sur main                    ← Claude refusera

# JAMAIS : Commit de secrets
> commit le fichier .env                 ← Claude vous avertira

# JAMAIS : Commit sans vérifier
> commit tout sans regarder              ← Toujours /review avant
```

> **Sécurité** : Claude Code refuse automatiquement les opérations destructives comme `push --force` sur main/master et vous avertit si vous essayez de commit des fichiers sensibles.

---

## Exercices pratiques

### Exercice 1 : Commit intelligent
1. Faites quelques modifications dans un projet
2. Utilisez `/commit`
3. Observez le message généré

### Exercice 2 : Code review
1. Modifiez intentionnellement du code avec un bug subtil
2. Utilisez `/review`
3. Vérifiez si Claude détecte le bug

### Exercice 3 : Pull Request
1. Créez une branche, faites des changements
2. Demandez à Claude de créer une PR
3. Examinez la description générée

### Exercice 4 : Résolution de conflits
1. Créez un conflit de merge volontairement
2. Demandez à Claude de le résoudre
3. Vérifiez que la résolution est logique

---

## Résumé

```
Git + Claude Code
│
├── Commits     : /commit → message intelligent automatique
├── PRs         : Description auto, titre pertinent
├── Reviews     : Bugs, sécurité, qualité, performance
├── Conflits    : Résolution sémantique (comprend le sens)
├── Historique  : git log/blame/bisect assisté
├── GitHub      : Issues, PRs, CI, Releases via gh CLI
└── Sécurité    : Refuse push --force main, alerte sur secrets
```

> **Prochain chapitre** : [Modes de Permissions & Sécurité](06-permissions-securite.md)
