# Module 01 - Introduction au Pre-commit

## Objectifs du module

- Comprendre pourquoi la qualite du code doit etre verifiee **avant** le commit
- Decouvrir le concept de hooks Git
- Identifier les problemes que le pre-commit resout
- Connaitre l'ecosysteme des outils de pre-commit

## Le probleme : du code "sale" qui arrive en production

### Scenario classique

```
Developpeur A                    Pipeline CI/CD                  Production
+-----------+                    +-------------+                 +----------+
| Ecrit du  |   git push        | Linting...  |                 |          |
| code avec | ───────────────>   | FAIL ❌     |   ───────X      |          |
| des       |                    | "trailing   |                 |          |
| erreurs   |                    |  whitespace"|                 |          |
+-----------+                    +-------------+                 +----------+

     ⏱️ 5 min d'attente pour decouvrir une erreur triviale
```

### Les problemes courants detectables avant un commit

| Probleme | Impact | Temps perdu |
|----------|--------|-------------|
| **Trailing whitespace** | Diff pollues, conflits inutiles | 5-10 min |
| **Fichiers trop gros** | Repo lent, stockage gaspille | 15-30 min |
| **Secrets dans le code** | Faille de securite critique | Heures/jours |
| **Erreurs de syntaxe** | CI qui echoue, PR bloquee | 10-20 min |
| **Mauvais formatage** | Reviews pollues, debats de style | 20-30 min |
| **YAML/JSON invalide** | Deploiement casse | 15-30 min |

### Le cout reel

```
Cout de detection d'un bug :

Pre-commit (local)     →  1x   (cout minimal, correction immediate)
CI/CD (pipeline)       →  10x  (attente pipeline, push correctif)
Code Review (PR)       →  25x  (aller-retour entre devs, contexte perdu)
Production             → 100x  (incident, rollback, post-mortem)
```

> **Principe du "Shift Left"** : Plus on detecte un probleme tot dans le cycle de developpement, moins il coute cher a corriger.

## Les hooks Git : le mecanisme sous-jacent

### Qu'est-ce qu'un hook Git ?

Un **hook Git** est un script qui s'execute automatiquement a un moment precis du workflow Git.

```
git commit -m "feat: ajout login"
       │
       ▼
┌──────────────────┐
│  pre-commit hook │ ← Avant que le commit soit cree
│  (votre script)  │
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Succes? │
    └────┬────┘
    Oui  │  Non
    │    │    │
    ▼    │    ▼
 Commit  │  ABORT
 cree    │  (rien n'est commite)
```

### Les differents hooks Git

| Hook | Moment d'execution | Cas d'usage |
|------|-------------------|-------------|
| **pre-commit** | Avant la creation du commit | Linting, formatage, secrets |
| **commit-msg** | Apres saisie du message | Validation du message de commit |
| **pre-push** | Avant le push | Tests, verification de branche |
| **post-commit** | Apres la creation du commit | Notifications |
| **prepare-commit-msg** | Avant l'editeur de message | Template de message |

### Hooks natifs vs frameworks

**Hook natif (`.git/hooks/pre-commit`) :**

```bash
#!/bin/sh
# Verifier qu'il n'y a pas de console.log
if git diff --cached --name-only | xargs grep -l "console.log" 2>/dev/null; then
    echo "ERREUR: console.log detecte !"
    exit 1
fi
```

**Problemes des hooks natifs :**

- Pas versionnes avec le repo (le dossier `.git/hooks/` est local)
- Difficile a partager avec l'equipe
- Maintenance manuelle de chaque script
- Pas de gestion des dependances
- Pas de mise a jour automatique

> C'est pour resoudre ces problemes que des frameworks comme **pre-commit** et **prek** ont ete crees.

## L'ecosysteme des outils

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────┐
│                  Hooks Git natifs                     │
│                  (.git/hooks/)                        │
├──────────────────────┬──────────────────────────────┤
│                      │                               │
│   pre-commit         │         prek                  │
│   (Python)           │         (Rust)                │
│                      │                               │
│   ✅ Ecosysteme      │   ✅ Rapide                   │
│      enorme          │   ✅ Zero config              │
│   ✅ 1000+ hooks     │   ✅ Simple                   │
│   ✅ Standard        │   ✅ Pas de Python            │
│      industrie       │      necessaire               │
│                      │                               │
└──────────────────────┴──────────────────────────────┘
```

### Comparaison rapide

| Critere | pre-commit | prek |
|---------|-----------|------|
| **Langage** | Python | Rust |
| **Vitesse** | Correct | Tres rapide |
| **Ecosysteme** | 1000+ hooks | Plus limite |
| **Configuration** | `.pre-commit-config.yaml` | `prek.toml` |
| **Installation** | `pip install pre-commit` | Binary standalone |
| **Dependance Python** | Oui | Non |
| **Adoption industrie** | Tres large | Emergent |

## Que va-t-on apprendre ?

### Plan du module

1. **pre-commit framework** (module 02) : installation, configuration, hooks populaires
2. **pre-commit avance** (module 03) : hooks custom, integration CI, bonnes pratiques
3. **prek** (module 04) : alternative rapide en Rust, configuration, comparaison

### Prerequis

- **Git** : savoir faire des commits, connaitre les bases
- **Terminal** : etre a l'aise avec la ligne de commande
- **Python** : installation de base (pour pre-commit)
- **Un projet existant** : pour tester en conditions reelles

---

## Exercice d'introduction

### Exercice 1 : Observer les hooks Git natifs

```bash
# Creer un repo de test
mkdir test-hooks && cd test-hooks
git init

# Lister les hooks exemples fournis par Git
ls .git/hooks/

# Examiner un hook exemple
cat .git/hooks/pre-commit.sample
```

### Exercice 2 : Creer un hook natif simple

```bash
# Creer un hook pre-commit basique
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
echo "🔍 Verification avant commit..."

# Verifier les fichiers Python pour des print()
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -n "$FILES" ]; then
    if grep -n "print(" $FILES; then
        echo "⚠️  ATTENTION: print() detecte dans les fichiers staged"
        echo "Utilisez logging a la place."
        echo "Pour forcer le commit: git commit --no-verify"
        exit 1
    fi
fi

echo "✅ Tout est bon !"
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### Exercice 3 : Tester le hook

```bash
# Creer un fichier Python avec un print
echo 'print("debug")' > main.py
git add main.py
git commit -m "test"  # Devrait etre bloque !

# Corriger et recommencer
echo 'import logging\nlogging.info("debug")' > main.py
git add main.py
git commit -m "test"  # Devrait passer !
```

> **Conclusion** : Les hooks natifs fonctionnent, mais on voit vite leurs limites. Dans le prochain module, on decouvre **pre-commit**, le framework qui rend tout ca simple et partageable.
