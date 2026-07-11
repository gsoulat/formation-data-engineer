# Cheatsheet Gradio

## Installation

```bash
pip install gradio          # pip
uv add gradio               # uv
gradio app.py               # lancement avec rechargement auto
```

## gr.Interface — Syntaxe minimale

```python
import gradio as gr

demo = gr.Interface(
    fn=ma_fonction,
    inputs=[...],
    outputs=[...],
    title="Mon App",
    description="Description en Markdown",
    examples=[[val1, val2], [val3, val4]],
)
demo.launch()
```

## gr.Blocks — Syntaxe minimale

```python
with gr.Blocks(title="Mon App") as demo:
    with gr.Row():
        inp = gr.Textbox(label="Entrée")
        out = gr.Textbox(label="Sortie")
    btn = gr.Button("Lancer", variant="primary")
    btn.click(fn=ma_fonction, inputs=inp, outputs=out)

demo.launch()
```

## Composants courants

### Texte
```python
gr.Textbox(label="", placeholder="", lines=1, max_lines=5, value="")
gr.Markdown("## Titre **gras** `code`")
gr.Code(language="python", lines=10)
```

### Numérique
```python
gr.Number(label="", value=0, minimum=0, maximum=100, precision=2)
gr.Slider(minimum=0, maximum=1, value=0.5, step=0.01, label="")
```

### Sélection
```python
gr.Dropdown(choices=["A", "B"], value="A", label="", multiselect=False)
gr.Radio(choices=["A", "B"], value="A", label="")
gr.CheckboxGroup(choices=["A", "B"], value=["A"], label="")
gr.Checkbox(label="Activer", value=False)
```

### Média
```python
gr.Image(type="numpy", label="", sources=["upload", "webcam"])
gr.Audio(type="numpy", label="", sources=["upload", "microphone"])
gr.File(label="", file_types=[".csv", ".xlsx"], file_count="single")
```

### Affichage
```python
gr.Label(value={"Classe A": 0.8, "Classe B": 0.2}, num_top_classes=3)
gr.Dataframe(value=df, interactive=False)
gr.Gallery(label="", columns=3, rows=2)
gr.Plot(label="")
```

## Mise en page (gr.Blocks uniquement)

```python
with gr.Row():             # côte à côte
    ...

with gr.Column(scale=2):   # proportion relative (scale=2 = 2x plus large)
    ...

with gr.Tabs():
    with gr.Tab("Onglet 1"):
        ...
    with gr.Tab("Onglet 2"):
        ...

with gr.Accordion("Options avancées", open=False):
    ...
```

## État et events

```python
# State par session
etat = gr.State([])        # valeur initiale
btn.click(fn, inputs=[inp, etat], outputs=[out, etat])

# Events disponibles
btn.click(fn, inputs, outputs)
textbox.submit(fn, inputs, outputs)      # touche Entrée
slider.change(fn, inputs, outputs)       # changement en temps réel
dropdown.select(fn, inputs, outputs)

# Mise à jour dynamique d'un composant
def fn():
    return gr.update(visible=False)      # cacher
    return gr.update(choices=["A", "B"]) # mettre à jour choices
    return gr.update(interactive=False)  # désactiver
```

## Chatbot

```python
# Format messages Gradio 4.x
historique = [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour !"},
]

chatbot = gr.Chatbot(
    type="messages",
    height=450,
    show_copy_button=True,
    bubble_full_width=False,
    avatar_images=(None, "🤖"),
)
```

## Streaming (générateur)

```python
def repondre_stream(message, historique):
    historique.append({"role": "user", "content": message})
    reponse = ""
    for token in generer_tokens():       # votre générateur LLM
        reponse += token
        yield "", historique + [{"role": "assistant", "content": reponse}]
    historique.append({"role": "assistant", "content": reponse})
    yield "", historique
```

## Streaming avec OpenAI

```python
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def repondre(message, historique):
    historique.append({"role": "user", "content": message})
    messages_api = [{"role": "system", "content": "..."}] + historique

    stream = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages_api, stream=True
    )
    reponse = ""
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        reponse += token
        yield "", historique + [{"role": "assistant", "content": reponse}]

    historique.append({"role": "assistant", "content": reponse})
    yield "", historique
```

## Streaming avec Ollama

```python
import ollama

def repondre(message, historique):
    historique.append({"role": "user", "content": message})
    stream = ollama.chat(model="mistral", messages=historique, stream=True)
    reponse = ""
    for chunk in stream:
        reponse += chunk["message"]["content"]
        yield "", historique + [{"role": "assistant", "content": reponse}]
    historique.append({"role": "assistant", "content": reponse})
    yield "", historique
```

## Launch — options utiles

```python
demo.launch(
    server_name="0.0.0.0",   # écouter sur toutes les interfaces
    server_port=7860,
    share=True,               # lien public temporaire (72h)
    auth=("user", "pass"),    # auth basique
    show_api=True,            # doc API auto
    debug=True,
)
```

## Dockerfile minimal

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
CMD ["python", "app.py"]
```

## README.md pour Hugging Face Spaces

```yaml
---
title: Mon App
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---
```

## Patterns courants

```python
# Vider le textbox après envoi
btn.click(fn, inputs=[msg, state], outputs=[msg, chatbot])
# fn retourne ("", historique) — "" vide le textbox

# Nouvelle conversation
btn_clear.click(lambda: ([], []), outputs=[chatbot, state])

# Bouton actif/inactif pendant génération
yield ..., gr.update(interactive=False)
# ... génération ...
yield ..., gr.update(interactive=True)

# Composant conditionnel
def toggle(actif):
    return gr.update(visible=actif)
checkbox.change(toggle, checkbox, composant_optionnel)
```
