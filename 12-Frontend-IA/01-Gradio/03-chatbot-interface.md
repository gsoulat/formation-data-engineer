# 03 — Interface Chatbot avec Gradio

## Pourquoi un chapitre dédié au chatbot ?

Le composant `gr.Chatbot` est de loin le plus utilisé dans les applications IA modernes. Sa logique est légèrement différente des composants vus précédemment : il gère un **historique de conversation** qui doit être maintenu entre les appels, et il supporte le **streaming** (affichage progressif des tokens). Ce chapitre couvre tous ces aspects avec des exemples progressifs.

## Le format de messages en Gradio 4.x

Avant tout, il faut comprendre le format attendu par `gr.Chatbot`.

En Gradio 4.x, le format recommandé est la liste de dictionnaires :

```python
historique = [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"},
    {"role": "user", "content": "Quel est le résultat de 2 + 2 ?"},
    {"role": "assistant", "content": "2 + 2 = 4."},
]
```

Chaque message est un dictionnaire avec deux clés :
- `"role"` : `"user"` (message de l'utilisateur) ou `"assistant"` (réponse du bot)
- `"content"` : le contenu du message, une chaîne de caractères

> **Note :** l'ancien format `[[user_msg, bot_msg], ...]` (liste de paires) est encore supporté mais déprécié. Utilisez toujours le format dictionnaire.

## Interface chatbot minimale

```python
import gradio as gr

def repondre(message, historique):
    """
    message : str — le dernier message de l'utilisateur
    historique : list[dict] — l'historique complet de la conversation
    Retourne : (str ou None, list[dict]) — (vider la zone de saisie, historique mis à jour)
    """
    historique = historique or []
    historique.append({"role": "user", "content": message})

    # Logique de réponse (ici simulée)
    reponse = f"Echo : {message}"
    historique.append({"role": "assistant", "content": reponse})

    return "", historique  # vider le textbox, mettre à jour le chatbot

with gr.Blocks(title="Chatbot Gradio") as demo:
    gr.Markdown("# Mon premier Chatbot")

    chatbot = gr.Chatbot(
        label="Conversation",
        type="messages",
        height=450,
        bubble_full_width=False,  # bulles de taille adaptée au contenu
    )
    state = gr.State([])

    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="Tapez votre message...",
            show_label=False,
            scale=4,
            autofocus=True,
        )
        submit_btn = gr.Button("Envoyer", variant="primary", scale=1)

    # Déclencher sur clic OU sur Entrée
    submit_btn.click(
        fn=repondre,
        inputs=[msg_input, state],
        outputs=[msg_input, chatbot],  # vide le textbox, met à jour chatbot
    )
    msg_input.submit(
        fn=repondre,
        inputs=[msg_input, state],
        outputs=[msg_input, chatbot],
    )

demo.launch()
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancement de l'interface chatbot, envoi de plusieurs messages, affichage de la conversation
> **Expliquer :** Montrer que l'historique se construit message par message. Expliquer pourquoi on retourne `""` pour le premier output (vider le textbox). Montrer que `.submit()` sur le Textbox permet d'envoyer avec la touche Entrée, ce qui est le comportement attendu par les utilisateurs.
---

## Bouton de remise à zéro

Un chatbot doit toujours proposer un bouton "Nouvelle conversation" :

```python
import gradio as gr

def repondre(message, historique):
    historique = historique or []
    historique.append({"role": "user", "content": message})
    historique.append({"role": "assistant", "content": f"Echo : {message}"})
    return "", historique

def reinitialiser():
    return [], []  # vider chatbot et state

with gr.Blocks(title="Chatbot avec reset") as demo:
    chatbot = gr.Chatbot(type="messages", height=400)
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(placeholder="Votre message...", show_label=False, scale=4)
        btn_send = gr.Button("Envoyer", variant="primary", scale=1)

    btn_clear = gr.Button("Nouvelle conversation", variant="secondary")

    btn_send.click(repondre, [msg, state], [msg, chatbot])
    msg.submit(repondre, [msg, state], [msg, chatbot])
    btn_clear.click(reinitialiser, outputs=[chatbot, state])

demo.launch()
```

## Streaming des réponses

Le streaming (affichage progressif des tokens) est crucial pour l'expérience utilisateur avec les LLMs. Sans streaming, l'utilisateur attend plusieurs secondes sans feedback. Avec streaming, les tokens apparaissent au fur et à mesure.

En Gradio, le streaming utilise un **générateur Python** (`yield`) :

```python
import gradio as gr
import time

def repondre_en_streaming(message, historique):
    historique = historique or []
    historique.append({"role": "user", "content": message})

    # Simuler une réponse token par token
    reponse_complete = f"Voici ma réponse à votre question : '{message}'. Je génère cette réponse progressivement pour simuler le comportement d'un LLM réel."

    reponse_partielle = ""
    for caractere in reponse_complete:
        reponse_partielle += caractere
        time.sleep(0.02)  # simuler la latence de génération

        # On yield l'historique avec la réponse partielle
        historique_temp = historique + [
            {"role": "assistant", "content": reponse_partielle}
        ]
        yield "", historique_temp

    # À la fin, on met à jour l'historique complet avec la réponse finale
    historique.append({"role": "assistant", "content": reponse_complete})

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages", height=400)
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(placeholder="Votre message...", show_label=False, scale=4)
        btn = gr.Button("Envoyer", variant="primary", scale=1)

    btn.click(repondre_en_streaming, [msg, state], [msg, chatbot])
    msg.submit(repondre_en_streaming, [msg, state], [msg, chatbot])

demo.launch()
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Envoi d'un message et affichage du streaming token par token dans l'interface
> **Expliquer :** Expliquer le mécanisme du générateur Python (`yield`). À chaque `yield`, Gradio envoie une mise à jour partielle au navigateur via WebSocket. L'utilisateur voit les tokens apparaître en temps réel. Comparer avec la version non-streaming pour montrer la différence d'expérience.
---

## Gérer l'état avec le système de messages

Pour une application plus réaliste, l'historique doit être géré avec soin. Voici un pattern propre qui sépare clairement l'affichage et l'état :

```python
import gradio as gr

def construire_reponse(message: str, historique: list[dict]) -> str:
    """Logique métier séparée — appelable depuis les tests aussi"""
    # On peut accéder à tout l'historique pour le contexte
    nb_echanges = len([m for m in historique if m["role"] == "user"])
    return f"[Échange #{nb_echanges + 1}] Vous m'avez dit : '{message}'"

def traiter_message(message: str, historique: list[dict]):
    if not message.strip():
        return "", historique  # ignorer les messages vides

    historique = list(historique)  # copie pour éviter la mutation en place
    historique.append({"role": "user", "content": message})

    reponse = construire_reponse(message, historique)
    historique.append({"role": "assistant", "content": reponse})

    return "", historique

with gr.Blocks(title="Chatbot Structuré") as demo:
    gr.Markdown("## Chatbot avec historique structuré")

    chatbot = gr.Chatbot(
        type="messages",
        height=450,
        show_copy_button=True,       # bouton copier sur chaque message
        avatar_images=(None, "🤖"),  # avatars pour user et assistant
    )
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Posez votre question...",
            show_label=False,
            scale=4,
            max_lines=3,  # zone de saisie extensible
        )
        with gr.Column(scale=1, min_width=120):
            btn_send = gr.Button("Envoyer", variant="primary")
            btn_clear = gr.Button("Effacer")

    btn_send.click(traiter_message, [msg, state], [msg, chatbot])
    msg.submit(traiter_message, [msg, state], [msg, chatbot])
    btn_clear.click(lambda: ([], []), outputs=[chatbot, state])

demo.launch()
```

## Afficher du Markdown dans les messages

`gr.Chatbot` supporte le rendu Markdown dans les messages. Vous pouvez retourner du Markdown depuis votre fonction :

```python
def repondre_avec_markdown(message, historique):
    historique = historique or []
    historique.append({"role": "user", "content": message})

    reponse = """
Voici les **points clés** :

1. Premier point important
2. Deuxième point important
3. Troisième point

```python
# Exemple de code
def bonjour():
    return "Hello World"
```

> *Source : documentation officielle*
"""
    historique.append({"role": "assistant", "content": reponse})
    return "", historique
```

## Messages système et contexte initial

Pour pré-charger un contexte (instructions système, historique existant) :

```python
import gradio as gr

MESSAGES_INITIAUX = [
    {
        "role": "assistant",
        "content": "Bonjour ! Je suis votre assistant spécialisé en Data Engineering. Je peux répondre à vos questions sur Python, SQL, Spark, et les architectures de données. Comment puis-je vous aider ?"
    }
]

def repondre(message, historique):
    historique.append({"role": "user", "content": message})
    historique.append({"role": "assistant", "content": f"Réponse à : {message}"})
    return "", historique

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        value=MESSAGES_INITIAUX,  # messages affichés dès l'ouverture
        type="messages",
        height=400,
    )
    state = gr.State(list(MESSAGES_INITIAUX))  # état initial aussi

    msg = gr.Textbox(placeholder="Votre question...", show_label=False)
    btn = gr.Button("Envoyer", variant="primary")

    btn.click(repondre, [msg, state], [msg, chatbot])
    msg.submit(repondre, [msg, state], [msg, chatbot])

demo.launch()
```

## Pattern : désactiver l'interface pendant la génération

Pour éviter que l'utilisateur envoie plusieurs messages pendant que le bot génère sa réponse :

```python
import gradio as gr
import time

def repondre(message, historique):
    historique = historique or []
    historique.append({"role": "user", "content": message})

    reponse = ""
    mots = f"Réponse à '{message}' avec plusieurs mots générés progressivement.".split()

    for mot in mots:
        reponse += mot + " "
        time.sleep(0.1)
        historique_temp = historique + [{"role": "assistant", "content": reponse.strip()}]
        yield "", historique_temp, gr.update(interactive=False), gr.update(interactive=False)

    historique.append({"role": "assistant", "content": reponse.strip()})
    yield "", historique, gr.update(interactive=True), gr.update(interactive=True)

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages", height=400)
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(placeholder="Votre message...", show_label=False, scale=4)
        btn = gr.Button("Envoyer", variant="primary", scale=1)

    btn.click(
        repondre,
        [msg, state],
        [msg, chatbot, msg, btn],  # on met à jour msg ET btn
    )

demo.launch()
```

## Résumé du chapitre

- Le format moderne Gradio 4.x utilise `{"role": "user"|"assistant", "content": str}`
- `gr.State` stocke l'historique par session, indépendant entre les utilisateurs
- Le streaming utilise `yield` — la fonction devient un générateur Python
- Retourner `""` pour le Textbox le vide après envoi
- On peut désactiver les composants pendant la génération avec `gr.update(interactive=False)`
- `show_copy_button=True` et `avatar_images` améliorent l'expérience utilisateur

**Prochain chapitre :** connecter ce chatbot à un vrai LLM (OpenAI, Ollama) avec streaming asynchrone.
