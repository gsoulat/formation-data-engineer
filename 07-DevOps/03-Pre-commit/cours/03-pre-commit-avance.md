# Module 03 - Pre-commit Avance

## Objectifs du module

- Creer ses propres hooks personnalises
- Integrer pre-commit dans un pipeline CI/CD
- Maitriser les options de configuration avancees
- Appliquer les bonnes pratiques d'equipe

## Creer ses propres hooks

### Hook local (dans le meme repo)

La methode la plus simple pour un hook specifique a votre projet :

```yaml
# .pre-commit-config.yaml
repos:
  # ... hooks standards ...

  - repo: local
    hooks:
      - id: check-todo
        name: Verifier les TODO sans assignation
        entry: bash -c 'grep -rn "TODO[^(]" --include="*.py" "$@" && echo "❌ TODO sans assignation (format: TODO(nom))" && exit 1 || exit 0' --
        language: system
        types: [python]

      - id: check-migrations
        name: Verifier les migrations Alembic
        entry: python scripts/check_migrations.py
        language: python
        files: 'alembic/versions/.*\.py$'
        pass_filenames: false
```

### Structure d'un hook : les parametres

```yaml
- id: mon-hook
  name: Nom affiche pendant l'execution
  entry: commande a executer
  language: system | python | node | ruby | golang | rust | ...
  types: [python]              # Type de fichier (OU logique)
  types_or: [python, pyi]      # Equivalent plus explicite
  files: '\.py$'               # Regex sur le chemin du fichier
  exclude: 'tests/.*'          # Regex d'exclusion
  pass_filenames: true         # Passer les noms de fichiers en argument
  always_run: false            # Executer meme sans fichier concerne
  stages: [pre-commit]         # Stage(s) d'execution
  require_serial: false        # Desactiver le parallelisme
  verbose: false               # Afficher la sortie meme en cas de succes
```

### Hook dans un repo dedie

Pour partager des hooks entre plusieurs projets :

```
mon-org-hooks/
├── .pre-commit-hooks.yaml    ← Declaration des hooks
├── check_docstrings.py
├── validate_config.py
└── setup.py                  ← Necessaire pour les hooks Python
```

```yaml
# .pre-commit-hooks.yaml
- id: check-docstrings
  name: Verifier les docstrings
  entry: check-docstrings
  language: python
  types: [python]

- id: validate-config
  name: Valider la configuration
  entry: validate-config
  language: python
  files: 'config\.ya?ml$'
```

```python
# check_docstrings.py
import ast
import sys

def check_file(filename):
    with open(filename) as f:
        tree = ast.parse(f.read())

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                errors.append(f"{filename}:{node.lineno} - {node.name} manque de docstring")

    return errors

def main():
    exit_code = 0
    for filename in sys.argv[1:]:
        errors = check_file(filename)
        for error in errors:
            print(error)
            exit_code = 1
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
```

```python
# setup.py
from setuptools import setup

setup(
    name="mon-org-hooks",
    version="1.0.0",
    py_modules=["check_docstrings", "validate_config"],
    entry_points={
        "console_scripts": [
            "check-docstrings=check_docstrings:main",
            "validate-config=validate_config:main",
        ],
    },
)
```

Utilisation dans un autre repo :

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/mon-org/mon-org-hooks
    rev: v1.0.0
    hooks:
      - id: check-docstrings
      - id: validate-config
```

## Integration CI/CD

### Pourquoi aussi en CI ?

```
Developpeur A                    Developpeur B
(pre-commit installe)            (oublie d'installer pre-commit)
                                       │
✅ Hooks passent                       │ git commit --no-verify
✅ Code propre                         │ ou pas de hooks installes
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   CI Pipeline    │
                              │  pre-commit run  │ ← Filet de securite
                              │  --all-files     │
                              └─────────────────┘
```

### GitHub Actions

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # Cache des environnements pre-commit
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}

      - run: pip install pre-commit
      - run: pre-commit run --all-files --show-diff-on-failure
```

### GitLab CI

```yaml
# .gitlab-ci.yml
pre-commit:
  stage: lint
  image: python:3.12-slim
  variables:
    PRE_COMMIT_HOME: ${CI_PROJECT_DIR}/.cache/pre-commit
  cache:
    paths:
      - .cache/pre-commit
    key:
      files:
        - .pre-commit-config.yaml
  script:
    - pip install pre-commit
    - pre-commit run --all-files --show-diff-on-failure
```

### Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'

  - script: |
      pip install pre-commit
      pre-commit run --all-files --show-diff-on-failure
    displayName: 'Run pre-commit'
```

## Configuration avancee

### Options globales

```yaml
# .pre-commit-config.yaml

# Version minimum de pre-commit requise
minimum_pre_commit_version: '4.0.0'

# Langage par defaut
default_language_version:
  python: python3.12
  node: '20.11.0'

# Stage par defaut
default_stages: [pre-commit]

# Exclure globalement certains fichiers
exclude: '^(vendor/|third_party/|\.git/)'

# Echouer rapidement (arreter au premier hook en erreur)
fail_fast: false

repos:
  # ...
```

### Fichier `.pre-commit-config.yaml` par environnement

```yaml
# Configuration conditionnelle avec ci
ci:
  autofix_prs: true           # Creer des PR de fix automatiques
  autofix_commit_msg: 'style: auto-fix pre-commit hooks'
  autoupdate_schedule: weekly  # Mise a jour auto hebdomadaire
  autoupdate_commit_msg: 'chore: update pre-commit hooks'
  skip: [mypy]                # Hooks a skipper en CI (trop lents)
```

### Gestion des performances

```yaml
repos:
  # Les hooks rapides en premier
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  # Ruff est ultra-rapide, le mettre tot
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Les hooks lents en dernier et seulement en pre-push
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        stages: [pre-push]  # Trop lent pour pre-commit
        additional_dependencies: [types-requests]
```

## Bonnes pratiques

### 1. Onboarding d'equipe

Ajouter dans le `Makefile` ou le `README` :

```makefile
# Makefile
.PHONY: setup
setup:  ## Installer les dependances + pre-commit
	pip install -r requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Environnement configure !"
```

### 2. Mise a jour reguliere

```bash
# Mettre a jour tous les hooks vers la derniere version
pre-commit autoupdate

# Verifier que tout passe encore
pre-commit run --all-files
```

### 3. Politique de bypass

| Situation | Action recommandee |
|-----------|-------------------|
| Un hook est trop strict | Ajuster sa config, pas `--no-verify` |
| Urgence production | `--no-verify` + justification dans le commit msg |
| Hook qui bug | `SKIP=hook-id git commit` temporairement |
| Nouveau dans l'equipe | Executer `pre-commit run --all-files` d'abord |

### 4. Strategie progressive

```
Phase 1 (Semaine 1)     Phase 2 (Semaine 3)     Phase 3 (Mois 2)
├── trailing-whitespace  ├── + ruff              ├── + mypy
├── end-of-file-fixer    ├── + ruff-format       ├── + gitleaks
├── check-yaml           ├── + no-commit-to-     ├── + conventional-
└── check-merge-conflict │    branch             │    pre-commit
                         └── + check-added-      └── + hooks custom
                              large-files
```

## Exercices

### Exercice 1 : Hook local custom

Creer un hook local qui verifie que tout fichier Python contient un en-tete de licence :

```python
# Copyright (c) 2025 Mon Entreprise. Tous droits reserves.
```

### Exercice 2 : Integration CI

Ajouter la verification pre-commit dans un pipeline GitHub Actions existant. Verifier que :
- Le cache fonctionne
- La sortie affiche les diffs en cas d'erreur
- Le pipeline echoue correctement quand un hook echoue

### Exercice 3 : Migration progressive

Vous rejoignez un projet sans pre-commit. Proposer un plan de migration en 3 phases :
1. Quels hooks installer en premier ?
2. Comment gerer les erreurs existantes sur le codebase ?
3. Comment embarquer l'equipe ?

> **Astuce** : `pre-commit run --all-files` sur un vieux codebase va generer beaucoup d'erreurs. Utilisez `git add -A && git commit -m "style: apply pre-commit hooks"` pour tout corriger d'un coup lors de la migration initiale.

---

> **A retenir** : Un setup pre-commit mature combine hooks standards + hooks custom + integration CI. L'objectif est que **personne ne puisse pousser du code qui ne respecte pas les standards**, meme par oubli.
