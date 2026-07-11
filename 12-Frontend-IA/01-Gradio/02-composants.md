# 02 — Composants Gradio

## Vue d'ensemble

Les composants sont les briques de base d'une interface Gradio. Chaque composant gère à la fois l'affichage (ce que voit l'utilisateur) et la sérialisation (comment la valeur est transmise à votre fonction Python). Ce chapitre couvre les composants les plus utilisés avec leurs paramètres clés et des exemples pratiques.

## Composants de texte

### `gr.Textbox`

Le composant de texte le plus courant. Peut être utilisé en entrée et en sortie.

```python
import gradio as gr

# En entrée : zone de saisie
gr.Textbox(
    label="Votre texte",
    placeholder="Tapez quelque chose...",
    lines=1,          # 1 = champ monoligne, >1 = zone multiligne
    max_lines=10,     # limite la hauteur maximale
    value="",         # valeur par défaut
    interactive=True, # l'utilisateur peut modifier
    info="Texte d'aide affiché sous le composant",
)

# En sortie : affichage en lecture seule
gr.Textbox(label="Résultat", interactive=False)
```

### `gr.Markdown`

Affiche du texte formaté. Utilisé uniquement en sortie ou comme élément statique.

```python
with gr.Blocks() as demo:
    gr.Markdown("# Titre principal")
    gr.Markdown("Texte avec **gras**, *italique* et `code`.")

    output = gr.Markdown()  # zone de sortie dynamique

    def generer():
        return "## Résultat généré\n\nVoici le contenu **dynamique**."

    gr.Button("Générer").click(generer, outputs=output)
```

### `gr.Code`

Affiche du code avec coloration syntaxique.

```python
gr.Code(
    label="Code généré",
    language="python",  # "python", "javascript", "sql", "bash", etc.
    lines=20,
    interactive=True,   # l'utilisateur peut modifier le code
)
```

## Composants numériques

### `gr.Number`

```python
gr.Number(
    label="Âge",
    value=25,
    minimum=0,
    maximum=120,
    step=1,
    precision=0,  # 0 = entier, 2 = 2 décimales
)
```

### `gr.Slider`

```python
gr.Slider(
    minimum=0,
    maximum=1.0,
    value=0.7,
    step=0.05,
    label="Température (créativité du LLM)",
    info="0 = déterministe, 1 = très créatif",
)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Interface avec un Slider et un Number côte à côte, montrer l'interaction en temps réel
> **Expliquer :** Faire glisser le slider et montrer que la valeur change. Expliquer que `step` contrôle la granularité et que la valeur transmise à Python est un `float` ou `int` selon `precision`.
---

## Composants de sélection

### `gr.Dropdown`

```python
gr.Dropdown(
    choices=["GPT-4", "GPT-3.5", "Claude", "Mistral"],
    label="Modèle LLM",
    value="GPT-4",        # valeur par défaut
    multiselect=False,    # True pour sélection multiple
    allow_custom_value=False,  # True pour saisir une valeur non listée
)
```

### `gr.Radio`

```python
gr.Radio(
    choices=["Classification", "Régression", "Clustering"],
    label="Type de problème ML",
    value="Classification",
)
```

### `gr.CheckboxGroup`

```python
gr.CheckboxGroup(
    choices=["Normalisation", "PCA", "SMOTE", "Feature selection"],
    label="Prétraitements à appliquer",
    value=["Normalisation"],  # cases cochées par défaut
)
```

### `gr.Checkbox`

```python
gr.Checkbox(label="Activer le mode verbose", value=False)
```

## Composants média

### `gr.Image`

Très utilisé pour les modèles de vision par ordinateur.

```python
# En entrée
gr.Image(
    type="numpy",   # "numpy" (array), "pil" (PIL Image), "filepath" (chemin)
    label="Image source",
    sources=["upload", "webcam", "clipboard"],
    image_mode="RGB",
)

# En sortie
gr.Image(label="Image traitée")
```

Exemple complet avec traitement d'image :

```python
import gradio as gr
import numpy as np

def inverser_image(image):
    # image est un numpy array (H, W, C) avec valeurs 0-255
    if image is None:
        return None
    return 255 - image

demo = gr.Interface(
    fn=inverser_image,
    inputs=gr.Image(type="numpy", label="Image originale"),
    outputs=gr.Image(label="Image inversée"),
    title="Inverseur d'image",
    examples=[["exemple.jpg"]],
)
demo.launch()
```

### `gr.Audio`

```python
# En entrée
gr.Audio(
    type="numpy",     # (sample_rate, data) ou "filepath"
    label="Fichier audio",
    sources=["upload", "microphone"],
)

# En sortie
gr.Audio(label="Audio généré", autoplay=False)
```

Exemple avec traitement audio :

```python
import gradio as gr
import numpy as np

def inverser_audio(audio):
    if audio is None:
        return None
    sample_rate, data = audio
    # Inverser le signal dans le temps
    return (sample_rate, data[::-1])

demo = gr.Interface(
    fn=inverser_audio,
    inputs=gr.Audio(type="numpy", label="Audio source"),
    outputs=gr.Audio(label="Audio inversé"),
)
demo.launch()
```

### `gr.File`

```python
# En entrée : upload de fichier
gr.File(
    label="Fichier CSV",
    file_types=[".csv", ".xlsx"],
    file_count="single",  # "multiple" pour plusieurs fichiers
)

# La valeur reçue par la fonction est le chemin vers le fichier uploadé
```

```python
import gradio as gr
import pandas as pd

def analyser_csv(fichier):
    if fichier is None:
        return "Aucun fichier fourni."
    df = pd.read_csv(fichier.name)
    info = f"**{len(df)} lignes**, **{len(df.columns)} colonnes**\n\n"
    info += f"Colonnes : {', '.join(df.columns.tolist())}\n\n"
    info += f"**Aperçu :**\n```\n{df.head(3).to_string()}\n```"
    return info

demo = gr.Interface(
    fn=analyser_csv,
    inputs=gr.File(label="Fichier CSV", file_types=[".csv"]),
    outputs=gr.Markdown(label="Analyse"),
)
demo.launch()
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Upload d'un fichier CSV dans l'interface, puis affichage de l'analyse en Markdown
> **Expliquer :** Montrer le drag-and-drop du fichier, expliquer que Gradio stocke temporairement le fichier et passe son chemin à la fonction Python. Le `fichier.name` donne le chemin complet. Insister sur `file_types` pour restreindre les formats acceptés.
---

## Composants de mise en page (dans `gr.Blocks`)

### `gr.Row` et `gr.Column`

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        # Les éléments dans une Row sont côte à côte
        input1 = gr.Textbox(label="Entrée 1")
        input2 = gr.Textbox(label="Entrée 2")

    with gr.Row():
        with gr.Column(scale=2):  # prend 2/3 de la largeur
            output_principal = gr.Textbox(label="Résultat principal", lines=5)
        with gr.Column(scale=1):  # prend 1/3 de la largeur
            output_stats = gr.Textbox(label="Statistiques")

demo.launch()
```

### `gr.Tabs` et `gr.Tab`

```python
import gradio as gr

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.Tab("Prédiction"):
            input_pred = gr.Textbox(label="Données")
            output_pred = gr.Label(label="Classe prédite")
            gr.Button("Prédire").click(lambda x: "Positif", input_pred, output_pred)

        with gr.Tab("Explication"):
            input_explain = gr.Textbox(label="Données")
            output_explain = gr.Markdown()
            gr.Button("Expliquer").click(
                lambda x: "**Raison :** la valeur X est élevée.",
                input_explain,
                output_explain
            )

        with gr.Tab("À propos"):
            gr.Markdown("## Ce modèle\nDécrivez votre modèle ici.")

demo.launch()
```

### `gr.Accordion`

Pour masquer/afficher des options avancées :

```python
import gradio as gr

with gr.Blocks() as demo:
    prompt = gr.Textbox(label="Prompt")

    with gr.Accordion("Paramètres avancés", open=False):
        temperature = gr.Slider(0, 2, value=0.7, label="Température")
        max_tokens = gr.Slider(100, 4000, value=500, step=100, label="Max tokens")
        top_p = gr.Slider(0, 1, value=0.9, step=0.05, label="Top-p")

    output = gr.Textbox(label="Réponse")
    gr.Button("Générer").click(lambda p, t, m, tp: f"Réponse avec T={t}",
                                [prompt, temperature, max_tokens, top_p], output)

demo.launch()
```

## Le composant `gr.Chatbot`

`gr.Chatbot` est un composant spécial pour afficher des conversations. Il mérite une attention particulière car son format a changé entre les versions de Gradio.

### Format des messages (Gradio 4.x)

En Gradio 4.x, le format recommandé utilise des dictionnaires :

```python
# Format moderne (Gradio 4.x)
messages = [
    {"role": "user", "content": "Bonjour !"},
    {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"},
    {"role": "user", "content": "Explique-moi le machine learning."},
]
```

```python
import gradio as gr

def repondre(message, historique):
    # historique est une liste de dict {"role", "content"}
    historique.append({"role": "user", "content": message})
    # Ici on appellerait le LLM, pour l'exemple on simule
    reponse = f"Vous avez dit : '{message}'. Je suis un bot de démonstration."
    historique.append({"role": "assistant", "content": reponse})
    return historique, historique

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        label="Assistant IA",
        type="messages",  # format dictionnaire
        height=400,
    )
    state = gr.State([])  # stocke l'historique

    with gr.Row():
        msg = gr.Textbox(
            label="Votre message",
            placeholder="Tapez votre message ici...",
            scale=4,
            show_label=False,
        )
        btn = gr.Button("Envoyer", scale=1, variant="primary")

    btn.click(repondre, [msg, state], [chatbot, state])
    msg.submit(repondre, [msg, state], [chatbot, state])  # Enter pour envoyer

demo.launch()
```

## L'état avec `gr.State`

`gr.State` stocke des données côté serveur entre les appels, associées à la session de l'utilisateur. C'est essentiel pour les chatbots (historique) ou tout état persistant.

```python
import gradio as gr

def incrementer(compteur):
    compteur += 1
    return compteur, f"Clics : {compteur}"

with gr.Blocks() as demo:
    compteur = gr.State(0)  # état initial
    label = gr.Textbox(label="Résultat", value="Clics : 0")
    btn = gr.Button("Cliquer")
    btn.click(incrementer, inputs=compteur, outputs=[compteur, label])

demo.launch()
```

Chaque utilisateur a son propre `gr.State` : si deux personnes utilisent l'application simultanément, leurs compteurs sont indépendants.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Ouvrir deux onglets du navigateur sur la même application avec `gr.State`, montrer que les états sont indépendants
> **Expliquer :** Cliquer plusieurs fois dans l'onglet 1, puis dans l'onglet 2. Montrer que le compteur de chaque onglet est indépendant. C'est la différence fondamentale avec une variable globale Python : `gr.State` est par session, une variable globale est partagée entre tous les utilisateurs.
---

## Galerie de composants utiles supplémentaires

```python
# Affichage de DataFrame
gr.Dataframe(
    value=df,
    label="Données",
    interactive=False,
    wrap=True,
)

# Label de classification avec probabilités
gr.Label(
    value={"Chat": 0.85, "Chien": 0.12, "Lapin": 0.03},
    label="Prédiction",
    num_top_classes=3,
)

# Galerie d'images
gr.Gallery(
    label="Images générées",
    columns=3,
    rows=2,
    height="auto",
)

# Bouton de téléchargement
gr.DownloadButton(
    label="Télécharger le résultat",
    value="fichier.csv",  # chemin vers le fichier
)
```

## Résumé du chapitre

- Les composants gèrent à la fois l'affichage et la conversion Python des données
- `gr.Image`, `gr.Audio`, `gr.File` permettent de traiter des médias
- `gr.Row`, `gr.Column`, `gr.Tabs`, `gr.Accordion` structurent la mise en page dans `gr.Blocks`
- `gr.Chatbot` avec `type="messages"` utilise le format dictionnaire `{"role", "content"}`
- `gr.State` stocke l'état par session utilisateur, indépendamment entre les connexions

**Prochain chapitre :** construire une interface chatbot complète avec historique de conversation.
