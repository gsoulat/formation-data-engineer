# Module 04 - Prek : Pre-commit en Rust

## Objectifs du module

- Comprendre ce qu'est Prek et son positionnement
- Installer et configurer Prek
- Connaitre les differences avec pre-commit
- Savoir quand choisir Prek vs pre-commit

## Qu'est-ce que Prek ?

**Prek** est un gestionnaire de hooks Git ecrit en **Rust**, concu comme une alternative rapide et legere a pre-commit. Son objectif : offrir la meme experience avec des performances superieures et sans dependance Python.

```
pre-commit (Python)                    prek (Rust)
┌─────────────────────┐               ┌─────────────────────┐
│ pip install          │               │ Binary standalone   │
│ pre-commit           │               │ (pas de runtime)    │
│                      │               │                     │
│ Necessite Python     │               │ Zero dependance     │
│ ~200ms de startup    │               │ ~10ms de startup    │
│ Ecosysteme mature    │               │ Compatible hooks    │
│ 1000+ hooks          │               │ pre-commit          │
└─────────────────────┘               └─────────────────────┘
```

### Pourquoi Prek ?

| Motivation | Explication |
|-----------|-------------|
| **Performance** | Demarrage quasi instantane grace a Rust |
| **Zero dependance** | Pas besoin de Python installe |
| **Compatibilite** | Lit le meme `.pre-commit-config.yaml` |
| **Simplicite** | Un seul binaire a installer |
| **Environnements contraints** | Ideal pour les images Docker legeres, CI minimales |

## Installation

### Via Homebrew (macOS/Linux)

```bash
brew install prek
```

### Via Cargo (Rust)

```bash
cargo install prek
```

### Via le binaire pre-compile

```bash
# Linux
curl -L https://github.com/prek-org/prek/releases/latest/download/prek-linux-x86_64 -o /usr/local/bin/prek
chmod +x /usr/local/bin/prek

# macOS (Apple Silicon)
curl -L https://github.com/prek-org/prek/releases/latest/download/prek-darwin-aarch64 -o /usr/local/bin/prek
chmod +x /usr/local/bin/prek
```

### Verification

```bash
prek --version
```

## Configuration

### Compatibilite avec pre-commit

Le gros avantage de Prek : il lit **le meme fichier** `.pre-commit-config.yaml` que pre-commit. Vous pouvez donc passer de l'un a l'autre sans changer votre configuration.

```bash
# Si vous avez deja un .pre-commit-config.yaml
# Il suffit d'installer les hooks avec prek
prek install
```

### Configuration dediee : `prek.toml`

Prek supporte aussi sa propre configuration en TOML :

```toml
# prek.toml

[settings]
fail_fast = false
parallel = true  # Execution parallele des hooks

[[repos]]
repo = "https://github.com/pre-commit/pre-commit-hooks"
rev = "v5.0.0"
hooks = [
    { id = "trailing-whitespace" },
    { id = "end-of-file-fixer" },
    { id = "check-yaml" },
    { id = "check-json" },
    { id = "check-merge-conflict" },
]

[[repos]]
repo = "https://github.com/astral-sh/ruff-pre-commit"
rev = "v0.9.0"
hooks = [
    { id = "ruff", args = ["--fix"] },
    { id = "ruff-format" },
]

[[repos]]
repo = "local"
hooks = [
    { id = "custom-check", name = "Mon check custom", entry = "python scripts/check.py", language = "system", types = ["python"] },
]
```

## Utilisation

### Commandes principales

```bash
# Installer les hooks
prek install

# Executer sur les fichiers staged
prek run

# Executer sur tous les fichiers
prek run --all-files

# Executer un hook specifique
prek run trailing-whitespace

# Mettre a jour les hooks
prek autoupdate

# Desinstaller
prek uninstall
```

### Comparaison des commandes

| Action | pre-commit | prek |
|--------|-----------|------|
| Installer les hooks | `pre-commit install` | `prek install` |
| Executer | `pre-commit run` | `prek run` |
| Tous les fichiers | `pre-commit run --all-files` | `prek run --all-files` |
| Mettre a jour | `pre-commit autoupdate` | `prek autoupdate` |
| Nettoyer | `pre-commit clean` | `prek clean` |
| Desinstaller | `pre-commit uninstall` | `prek uninstall` |

> La plupart des commandes sont identiques — la transition est transparente.

## Performance : benchmarks

### Temps de demarrage

```
pre-commit run (rien a faire) :  ~400ms
prek run (rien a faire) :         ~30ms
                                  ────────
                                  ~13x plus rapide
```

### Execution sur un projet moyen (50 fichiers staged)

```
pre-commit run :  ~2.5s
prek run :        ~0.8s
                  ────────
                  ~3x plus rapide
```

### Impact sur le workflow quotidien

```
En moyenne, un developpeur commit 10 fois par jour.

Avec pre-commit : 10 x 2.5s = 25s/jour
Avec prek :       10 x 0.8s =  8s/jour

Sur une equipe de 10, sur un an :
pre-commit : ~17h d'attente cumulee
prek :       ~5.5h d'attente cumulee
```

> Les gains sont modestes individuellement mais s'accumulent. Le vrai avantage est le **feeling** : prek est quasi instantane, ce qui reduit la tentation de `--no-verify`.

## Comparaison detaillee : pre-commit vs prek

| Critere | pre-commit | prek |
|---------|-----------|------|
| **Langage** | Python | Rust |
| **Vitesse** | Correcte | Tres rapide |
| **Installation** | `pip install` | Binary / `brew` / `cargo` |
| **Dependance Python** | Oui | Non |
| **Format config** | YAML | YAML + TOML |
| **Ecosysteme hooks** | 1000+ natifs | Compatible pre-commit |
| **Hooks locaux** | Oui | Oui |
| **CI/CD support** | Excellent | Bon |
| **Documentation** | Tres complete | En croissance |
| **Communaute** | Tres large | En croissance |
| **pre-commit.ci** | Oui (service gratuit) | Non |
| **Maturite** | 10+ ans | Recent |

### Quand choisir pre-commit ?

- Projet qui utilise deja Python (la dependance n'est pas un probleme)
- Besoin du service `pre-commit.ci` (auto-fix en PR)
- Equipe habituee a pre-commit
- Besoin de hooks tres specifiques uniquement disponibles pour pre-commit

### Quand choisir prek ?

- Projet sans Python (Go, Rust, JS, etc.)
- Images Docker minimales ou CI contrainte
- Performance critique (gros monorepo)
- Preference pour les outils sans runtime
- Nouveau projet, pas de contrainte historique

## Migration de pre-commit vers prek

### Etape 1 : Installer prek

```bash
brew install prek
# ou
cargo install prek
```

### Etape 2 : Tester la compatibilite

```bash
# Garder pre-commit installe en parallele
prek run --all-files

# Comparer les resultats avec
pre-commit run --all-files
```

### Etape 3 : Basculer

```bash
# Desinstaller les hooks pre-commit
pre-commit uninstall

# Installer les hooks prek
prek install

# Verifier
ls -la .git/hooks/pre-commit
```

### Etape 4 : Mettre a jour la documentation

```makefile
# Makefile - Avant
setup:
	pip install pre-commit
	pre-commit install

# Makefile - Apres
setup:
	brew install prek || cargo install prek
	prek install
```

## Exercices

### Exercice 1 : Installation et decouverte

1. Installer prek sur votre machine
2. Creer un projet de test avec `git init`
3. Copier un `.pre-commit-config.yaml` existant
4. Installer les hooks avec `prek install`
5. Tester un commit avec des erreurs volontaires

### Exercice 2 : Configuration TOML

1. Creer un `prek.toml` equivalent a votre `.pre-commit-config.yaml`
2. Comparer les deux formats
3. Ajouter un hook local dans le `prek.toml`

### Exercice 3 : Benchmark

1. Sur un projet existant, mesurer le temps de `pre-commit run --all-files`
2. Installer prek et mesurer `prek run --all-files`
3. Comparer et documenter les resultats

```bash
# Mesurer
time pre-commit run --all-files
time prek run --all-files
```

---

> **A retenir** : Prek est une alternative performante a pre-commit, compatible avec le meme format de configuration. Le choix entre les deux depend surtout de votre ecosysteme (Python ou non) et de vos contraintes de performance. Les deux outils repondent au meme besoin : garantir la qualite du code avant chaque commit.
