# 01 — Introduction à Gradio

## Qu'est-ce que Gradio ?

Gradio est une bibliothèque Python open source qui permet de créer des **interfaces web interactives** pour n'importe quelle fonction Python en quelques lignes de code. Développée initialement par une équipe de chercheurs en ML, elle est aujourd'hui maintenue par Hugging Face et est devenue le standard de facto pour démontrer des modèles d'IA.

Le problème qu'elle résout est simple : vous avez entraîné un modèle, vous voulez le montrer à un client ou le partager avec un collègue, mais vous n'êtes pas développeur web. Avec Gradio, vous transformez votre fonction `predict()` en application web en 5 lignes.

### Ce que Gradio n'est pas

- Ce n'est **pas** un framework de production à haute charge (Streamlit ou FastAPI sont plus adaptés)
- Ce n'est **pas** un outil de visualisation de données (Streamlit ou Dash sont plus adaptés)
- Ce n'est **pas** un remplacement pour une vraie application web (Vue, React, etc.)

C'est un outil de **démonstration rapide** et de **prototypage**, idéal pour les data scientists et ingénieurs IA.

## Installation

```bash
# Avec pip
pip install gradio

# Avec uv (recommandé)
uv add gradio

# Vérifier
python -c "import gradio as gr; print(gr.__version__)"
```

Pour ce module, nous utiliserons Gradio 4.x (la version actuelle). Les API diffèrent significativement des versions 3.x.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec l'installation de gradio via `pip install gradio` puis vérification de la version
> **Expliquer :** Montrer la commande, le téléchargement des dépendances, et la confirmation de version. Préciser que gradio installe plusieurs dépendances (fastapi, uvicorn, etc.) car il embarque un vrai serveur web.
---

## Première interface : le Hello World

Créez un fichier `app.py` :

```python
import gradio as gr

def saluer(nom):
    return f"Bonjour, {nom} !"

demo = gr.Interface(
    fn=saluer,
    inputs=gr.Textbox(label="Votre prénom"),
    outputs=gr.Textbox(label="Salutation"),
    title="Mon premier Gradio",
    description="Entrez votre prénom pour recevoir une salutation personnalisée."
)

demo.launch()
```

Lancez l'application :

```bash
python app.py
```

Gradio démarre un serveur local et affiche une URL du type `http://127.0.0.1:7860`. Ouvrez cette URL dans votre navigateur.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancement de `python app.py` dans le terminal, puis ouverture du navigateur sur `http://127.0.0.1:7860`
> **Expliquer :** Montrer l'interface générée automatiquement — la zone de saisie, le bouton Submit, la zone de résultat. Taper un prénom et cliquer Submit pour montrer que la fonction Python est appelée en temps réel.
---

### Ce qui se passe en coulisses

Quand vous appelez `demo.launch()`, Gradio :
1. Démarre un serveur **FastAPI** en arrière-plan
2. Sert une application web JavaScript qui appelle ce serveur
3. Mappe automatiquement vos types Python aux composants HTML appropriés

## `gr.Interface` — l'approche déclarative

`gr.Interface` est le point d'entrée le plus simple. Il prend :

| Paramètre | Type | Description |
|-----------|------|-------------|
| `fn` | callable | La fonction Python à exposer |
| `inputs` | Component ou liste | Les composants d'entrée |
| `outputs` | Component ou liste | Les composants de sortie |
| `title` | str | Titre affiché en haut |
| `description` | str | Description en Markdown |
| `examples` | liste | Exemples cliquables |
| `flagging_mode` | str | `"never"`, `"manual"`, `"auto"` |

### Fonction avec plusieurs entrées et sorties

```python
import gradio as gr

def analyser_texte(texte, langue, max_mots):
    mots = texte.split()
    nb_mots = len(mots)
    nb_chars = len(texte)
    resume = " ".join(mots[:max_mots]) + "..." if nb_mots > max_mots else texte
    return nb_mots, nb_chars, resume

demo = gr.Interface(
    fn=analyser_texte,
    inputs=[
        gr.Textbox(label="Texte à analyser", lines=5),
        gr.Dropdown(["fr", "en", "es"], label="Langue", value="fr"),
        gr.Slider(10, 100, value=30, step=10, label="Nombre max de mots du résumé"),
    ],
    outputs=[
        gr.Number(label="Nombre de mots"),
        gr.Number(label="Nombre de caractères"),
        gr.Textbox(label="Résumé"),
    ],
    title="Analyseur de texte",
    examples=[
        ["Le machine learning est une branche de l'intelligence artificielle.", "fr", 5],
        ["Deep learning has revolutionized computer vision.", "en", 4],
    ]
)

demo.launch()
```

### Les exemples cliquables

Le paramètre `examples` est très utile en démonstration. Chaque élément de la liste correspond à une combinaison de valeurs pour vos entrées. L'utilisateur clique sur un exemple et les champs se remplissent automatiquement.

## `gr.Blocks` — l'approche impérative

`gr.Interface` est pratique mais limité. Pour des interfaces plus complexes (mise en page personnalisée, logique conditionnelle, plusieurs boutons), on utilise `gr.Blocks`.

```python
import gradio as gr

with gr.Blocks(title="Mon app Blocks") as demo:
    gr.Markdown("# Bienvenue sur mon application")
    gr.Markdown("Cette interface utilise `gr.Blocks` pour plus de flexibilité.")

    with gr.Row():
        with gr.Column():
            texte_input = gr.Textbox(label="Entrée", lines=3)
            btn = gr.Button("Analyser", variant="primary")
        with gr.Column():
            texte_output = gr.Textbox(label="Résultat", lines=3)

    def traiter(texte):
        return texte.upper()

    btn.click(fn=traiter, inputs=texte_input, outputs=texte_output)

demo.launch()
```

### Différences clés entre Interface et Blocks

| Critère | `gr.Interface` | `gr.Blocks` |
|---------|----------------|-------------|
| Simplicité | Très simple, 3 lignes | Plus verbeux |
| Mise en page | Automatique | Totalement contrôlée |
| Plusieurs boutons | Non | Oui |
| Logique conditionnelle | Non | Oui |
| Onglets | Non | Oui |
| Cas d'usage | Démo rapide | Application complète |

### Quand utiliser quoi ?

- **`gr.Interface`** : vous avez une seule fonction, une seule action, et vous voulez aller vite
- **`gr.Blocks`** : vous avez besoin de mise en page, de plusieurs interactions, d'onglets, ou d'une logique plus complexe

## Le rechargement automatique

Pendant le développement, relancer le serveur manuellement à chaque modification est fastidieux. Gradio supporte le rechargement automatique :

```bash
# Mode développement avec rechargement automatique
gradio app.py
```

Ou dans le code :

```python
demo.launch(reload=True)  # uniquement pour les tests locaux
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Modifier une ligne du fichier `app.py` (par exemple changer le titre), sauvegarder, et montrer que le navigateur se recharge automatiquement
> **Expliquer :** Le mode `gradio app.py` surveille les modifications du fichier et recharge le serveur automatiquement. C'est équivalent à `--reload` dans uvicorn. Très utile pendant le développement.
---

## Options de lancement courantes

```python
demo.launch(
    server_name="0.0.0.0",  # écouter sur toutes les interfaces (utile en Docker)
    server_port=7860,        # port par défaut
    share=False,             # ne pas créer de lien public temporaire
    auth=("user", "password"),  # authentification basique
    show_api=True,           # afficher la doc API automatique
    debug=True,              # logs détaillés
)
```

## Structure d'un projet Gradio

Pour un projet un peu plus sérieux, organisez votre code ainsi :

```
mon-projet-gradio/
├── app.py           # point d'entrée principal
├── model.py         # chargement et inférence du modèle
├── utils.py         # fonctions utilitaires
├── requirements.txt # dépendances
└── README.md        # description pour Hugging Face Spaces
```

```python
# model.py
import joblib

def load_model(path="model.pkl"):
    return joblib.load(path)

def predict(model, features):
    return model.predict([features])[0]
```

```python
# app.py
import gradio as gr
from model import load_model, predict

model = load_model()  # chargé une seule fois au démarrage

def inference(feature1, feature2, feature3):
    result = predict(model, [feature1, feature2, feature3])
    return f"Prédiction : {result}"

demo = gr.Interface(fn=inference, inputs=[...], outputs=[...])
demo.launch()
```

Charger le modèle **en dehors** de la fonction d'inférence est crucial : si vous le chargez dans la fonction, il sera rechargé à chaque appel, ce qui sera très lent.

## Résumé du chapitre

- Gradio transforme une fonction Python en interface web en quelques lignes
- `gr.Interface` est l'approche la plus simple pour une seule fonction
- `gr.Blocks` donne un contrôle total sur la mise en page et la logique
- `gradio app.py` active le rechargement automatique pendant le développement
- Chargez toujours vos modèles en dehors des fonctions d'inférence

**Prochain chapitre :** découvrir tous les composants disponibles pour créer des interfaces riches.
