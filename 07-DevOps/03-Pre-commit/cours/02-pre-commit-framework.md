# Module 02 - Le Framework pre-commit

## Objectifs du module

- Installer et configurer pre-commit
- Comprendre le fichier `.pre-commit-config.yaml`
- Connaitre et utiliser les hooks les plus populaires
- Savoir ajouter et configurer des hooks

## Qu'est-ce que pre-commit ?

**pre-commit** est un framework multi-langage pour gerer et maintenir des hooks Git. Il :

- Gere les dependances de chaque hook automatiquement
- Isole chaque hook dans son propre environnement
- Se configure via un fichier YAML versionne
- Propose un ecosysteme de 1000+ hooks prets a l'emploi

```
.pre-commit-config.yaml     ← Fichier de configuration (versionne)
         │
         ▼
┌─────────────────┐
│   pre-commit    │
│   framework     │
│                 │
│  ┌───────────┐  │
│  │ Hook 1    │  │  ← Environnement isole (venv, node_modules, etc.)
│  │ (ruff)    │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Hook 2    │  │
│  │ (black)   │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ Hook 3    │  │
│  │ (mypy)    │  │
│  └───────────┘  │
└─────────────────┘
```

## Installation

### Avec pip

```bash
pip install pre-commit

# Verifier l'installation
pre-commit --version
# pre-commit 4.x.x
```

### Avec pipx (recommande)

```bash
# pipx installe dans un environnement isole
pipx install pre-commit
```

### Avec Homebrew (macOS)

```bash
brew install pre-commit
```

### Avec conda

```bash
conda install -c conda-forge pre-commit
```

## Configuration : `.pre-commit-config.yaml`

### Structure de base

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0  # Version du repo de hooks
    hooks:
      - id: trailing-whitespace  # ID du hook
      - id: end-of-file-fixer
      - id: check-yaml
```

### Anatomie d'une entree

```yaml
repos:
  - repo: <URL du depot Git contenant les hooks>
    rev: <tag ou SHA du commit a utiliser>
    hooks:
      - id: <identifiant du hook>
        name: <nom affiche (optionnel)>
        args: [<arguments supplementaires>]
        files: <regex des fichiers a cibler>
        exclude: <regex des fichiers a exclure>
        types: [<types de fichiers>]
        stages: [pre-commit, pre-push, commit-msg]
        language_version: <version du langage>
```

### Initialiser pre-commit dans un projet

```bash
# Se placer dans le repo
cd mon-projet

# Generer un fichier de config de base
pre-commit sample-config > .pre-commit-config.yaml

# Installer les hooks dans .git/hooks/
pre-commit install

# (Optionnel) Installer aussi pour d'autres stages
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push
```

## Les hooks essentiels

### 1. pre-commit-hooks (hooks de base)

Le repo officiel de hooks generiques, indispensables sur tout projet :

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      # --- Formatage ---
      - id: trailing-whitespace      # Supprime les espaces en fin de ligne
      - id: end-of-file-fixer        # Assure un newline en fin de fichier
      - id: mixed-line-ending        # Unifie les fins de ligne (LF/CRLF)
        args: ['--fix=lf']

      # --- Validation ---
      - id: check-yaml               # Valide la syntaxe YAML
      - id: check-json               # Valide la syntaxe JSON
      - id: check-toml               # Valide la syntaxe TOML
      - id: check-xml                # Valide la syntaxe XML

      # --- Securite ---
      - id: detect-private-key       # Detecte les cles privees
      - id: check-added-large-files  # Bloque les gros fichiers
        args: ['--maxkb=500']

      # --- Git ---
      - id: check-merge-conflict     # Detecte les marqueurs de conflit
      - id: no-commit-to-branch      # Empeche de commit sur main/master
        args: ['--branch', 'main', '--branch', 'master']
```

### 2. Ruff (linting + formatage Python)

Ruff remplace avantageusement flake8, isort, black et bien d'autres, en etant **10-100x plus rapide** :

```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff           # Linting (remplace flake8, isort, etc.)
        args: [--fix]      # Auto-fix les erreurs corrigeables
      - id: ruff-format    # Formatage (remplace black)
```

### 3. MyPy (typage Python)

```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]  # Stubs de typage
```

### 4. Hooks pour d'autres langages

```yaml
  # JavaScript / TypeScript
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.17.0
    hooks:
      - id: eslint

  # Terraform
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint

  # Docker
  - repo: https://github.com/hadolint/hadolint
    rev: v2.13.1-beta
    hooks:
      - id: hadolint

  # SQL
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.3.0
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix
```

### 5. Securite

```yaml
  # Detection de secrets
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.0
    hooks:
      - id: gitleaks

  # Vulnerabilites des dependances Python
  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.3
    hooks:
      - id: python-safety-dependencies-check
```

### 6. Conventional Commits (messages de commit)

```yaml
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.0.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci]
```

## Configuration complete recommandee (projet Python)

```yaml
# .pre-commit-config.yaml
default_language_version:
  python: python3.12

repos:
  # Hooks de base
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: no-commit-to-branch
        args: ['--branch', 'main']

  # Ruff (linting + format)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Securite
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.0
    hooks:
      - id: gitleaks

  # Conventional Commits
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.0.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, docs, style, refactor, test, chore, ci]
```

## Utilisation quotidienne

### Commandes essentielles

```bash
# Executer sur les fichiers staged (automatique au commit)
pre-commit run

# Executer sur tous les fichiers du repo
pre-commit run --all-files

# Executer un hook specifique
pre-commit run ruff --all-files

# Mettre a jour les versions des hooks
pre-commit autoupdate

# Nettoyer le cache
pre-commit clean

# Desinstaller les hooks
pre-commit uninstall
```

### Comprendre la sortie

```
$ git commit -m "feat: ajout authentification"

Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
Check Yaml...............................................................Passed
Check JSON...........................................(no files to check)Skipped
Check for added large files..............................................Passed
Check for merge conflicts................................................Passed
Detect Private Key.......................................................Passed
Don't commit to branch...................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
gitleaks.................................................................Passed
conventional-pre-commit..................................................Passed
```

### Bypass temporaire

```bash
# En cas d'urgence, vous pouvez contourner les hooks
# ⚠️  A utiliser avec parcimonie !
git commit --no-verify -m "hotfix: correction urgente"

# Ou pour un hook specifique
SKIP=ruff git commit -m "feat: wip"
```

## Exercices

### Exercice 1 : Setup complet

1. Creer un nouveau projet Python avec `git init`
2. Installer pre-commit avec `pip install pre-commit`
3. Copier la configuration recommandee ci-dessus
4. Installer les hooks avec `pre-commit install`
5. Creer un fichier Python mal formate et tenter un commit

### Exercice 2 : Observer les corrections automatiques

```bash
# Creer un fichier avec des problemes
cat > example.py << 'EOF'
import os
import sys
import json

def hello_world(  ):
    x=1
    y = [1,2,3]
    print( "hello"  )

EOF

# Ajouter et commit
git add example.py
git commit -m "test"

# Observer les corrections de ruff-format
# Puis re-ajouter et recommiter
git add example.py
git commit -m "feat: ajout example"
```

### Exercice 3 : Conventional Commits

Avec la config `conventional-pre-commit` active, tester ces messages :

```bash
git commit -m "ajout feature"        # ❌ Pas conventionnel
git commit -m "feat: ajout feature"  # ✅ OK
git commit -m "fix: correction bug"  # ✅ OK
git commit -m "wip: en cours"        # ❌ "wip" n'est pas un type valide
```

---

> **A retenir** : pre-commit transforme les regles de qualite de code en verifications automatiques et partagees. La configuration est versionnee, les hooks sont isoles, et l'equipe entiere beneficie des memes standards.
