# Guide Jupyter Notebook

## Qu'est-ce qu'un Notebook Jupyter ?

Un **notebook Jupyter** (fichier `.ipynb`) est un document interactif qui combine :

- **Code executable** : des cellules de code Python (ou autre langage)
- **Texte enrichi** : du Markdown pour les explications, titres, listes
- **Resultats** : les sorties du code (texte, tableaux, graphiques) sont sauvegardees dans le fichier

> Tous les cours de cette formation sont au format notebook (`.ipynb`).

## Installation

### 1. Installer Python

Verifiez que Python 3.10+ est installe :

```bash
python3 --version
```

Si Python n'est pas installe, telechargez-le depuis [python.org](https://www.python.org/downloads/).

### 2. Creer un environnement virtuel

Un **environnement virtuel** (venv) isole les dependances de chaque projet. C'est une bonne pratique pour eviter les conflits entre packages.

#### Avec `uv` (recommande)

```bash
# Installer uv (gestionnaire de packages moderne)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Creer un environnement virtuel
uv venv

# Activer l'environnement
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\activate       # Windows
```

#### Avec `venv` (standard)

```bash
python3 -m venv .venv
source .venv/bin/activate    # Linux / macOS
.venv\Scripts\activate       # Windows
```

### 3. Installer Jupyter

#### Option A : JupyterLab (interface web complete)

```bash
# Avec uv
uv pip install jupyterlab

# Avec pip
pip install jupyterlab
```

Lancer JupyterLab :

```bash
jupyter lab
```

Un navigateur s'ouvre automatiquement sur `http://localhost:8888`.

#### Option B : VS Code (recommande pour cette formation)

1. Installez [VS Code](https://code.visualstudio.com/)
2. Installez les extensions :
   - **Python** (Microsoft)
   - **Jupyter** (Microsoft)
3. Ouvrez un fichier `.ipynb` directement dans VS Code

> **Avantage VS Code** : pas besoin de lancer un serveur Jupyter separement. L'extension gere tout.

## Les Kernels

### Qu'est-ce qu'un kernel ?

Un **kernel** est le processus qui execute le code dans un notebook. Chaque kernel est lie a un **environnement Python** (et donc a un ensemble de packages installes).

```
┌──────────────┐       ┌──────────────┐
│   Notebook   │──────>│    Kernel    │
│  (interface) │       │  (Python)    │
│              │<──────│              │
│  Cellule 1   │       │  Execute le  │
│  Cellule 2   │       │  code et     │
│  Cellule 3   │       │  renvoie les │
│              │       │  resultats   │
└──────────────┘       └──────────────┘
```

### Installer un kernel depuis un venv

Pour utiliser un environnement virtuel comme kernel dans Jupyter :

```bash
# 1. Activer l'environnement virtuel
source .venv/bin/activate

# 2. Installer ipykernel
uv pip install ipykernel       # avec uv
pip install ipykernel           # avec pip

# 3. Enregistrer le kernel avec un nom explicite
python -m ipykernel install --user --name="formation-data-engineer" --display-name="Python (Formation DE)"
```

- `--name` : identifiant technique du kernel (sans espaces)
- `--display-name` : nom affiche dans l'interface Jupyter / VS Code

### Lister les kernels disponibles

```bash
jupyter kernelspec list
```

Exemple de sortie :

```
Available kernels:
  python3                    /usr/local/share/jupyter/kernels/python3
  formation-data-engineer    /Users/user/Library/Jupyter/kernels/formation-data-engineer
```

### Supprimer un kernel

```bash
jupyter kernelspec remove formation-data-engineer
```

### Changer de kernel

#### Dans JupyterLab

Menu **Kernel** > **Change Kernel...** > Selectionnez le kernel souhaite.

#### Dans VS Code

Cliquez sur le nom du kernel en haut a droite du notebook, puis selectionnez le kernel dans la liste.

## Utilisation des Notebooks

### Types de cellules

| Type | Usage | Raccourci |
|------|-------|-----------|
| **Code** | Ecrire et executer du Python | `Y` (en mode commande) |
| **Markdown** | Ecrire du texte, titres, listes | `M` (en mode commande) |

### Raccourcis essentiels

| Action | JupyterLab | VS Code |
|--------|-----------|---------|
| Executer une cellule | `Shift + Enter` | `Shift + Enter` |
| Executer sans avancer | `Ctrl + Enter` | `Ctrl + Enter` |
| Ajouter cellule au-dessus | `A` (mode commande) | `Ctrl + Shift + Enter` |
| Ajouter cellule en-dessous | `B` (mode commande) | -- |
| Supprimer cellule | `D, D` (mode commande) | -- |
| Mode commande | `Echap` | `Echap` |
| Mode edition | `Enter` | `Enter` |

### Redemarrer le kernel

Si votre code se bloque ou produit des resultats incoherents, redemarrez le kernel :

- **JupyterLab** : Menu **Kernel** > **Restart Kernel**
- **VS Code** : Icone de redemarrage en haut du notebook

> **Attention** : redemarrer le kernel efface toutes les variables en memoire. Il faut re-executer les cellules depuis le debut.

### Executer toutes les cellules

Pour s'assurer que le notebook fonctionne de A a Z :

- **JupyterLab** : Menu **Run** > **Run All Cells**
- **VS Code** : **Run All** (bouton en haut du notebook)

## Depannage

### "No kernel found" / Aucun kernel disponible

```bash
# Verifier que ipykernel est installe dans le venv
source .venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name="mon-projet"
```

### "ModuleNotFoundError" dans le notebook

Le package n'est pas installe dans l'environnement du kernel actif :

```bash
# Verifier quel Python est utilise par le kernel
# (executer cette cellule dans le notebook)
import sys
print(sys.executable)
```

Puis installer le package dans cet environnement :

```bash
# Activer le bon venv, puis :
uv pip install nom-du-package
```

### Le notebook ne se lance pas (JupyterLab)

```bash
# Verifier que jupyter est installe
jupyter --version

# Relancer en precisant le port
jupyter lab --port=8889
```

### VS Code ne detecte pas le kernel

1. Ouvrez la palette de commandes (`Ctrl + Shift + P` / `Cmd + Shift + P`)
2. Tapez : **"Python: Select Interpreter"**
3. Selectionnez l'interpreteur de votre `.venv`
4. Rouvrez le fichier `.ipynb`
