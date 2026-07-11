# 04 — Intégration LLM avec Gradio

## Vue d'ensemble

Ce chapitre vous montre comment connecter votre interface Gradio à de vrais modèles de langage. On couvre trois cas d'usage :
1. **OpenAI** (API cloud, modèles GPT)
2. **Ollama** (LLM local, pas de coût, confidentialité des données)
3. **LangChain** (abstraction pour changer de fournisseur facilement)

Dans chaque cas, on implémente le **streaming** pour une expérience utilisateur optimale.

## Prérequis

```bash
# Pour OpenAI
pip install openai

# Pour Ollama (après avoir installé Ollama sur votre machine)
pip install ollama

# Pour LangChain
pip install langchain langchain-openai langchain-ollama

# Tout en une fois avec uv
uv add gradio openai ollama langchain langchain-openai langchain-ollama
```

## Intégration OpenAI

### Configuration de base

```python
import os
from openai import OpenAI

# Charger la clé API depuis les variables d'environnement (jamais en dur dans le code)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

> **Bonne pratique :** Stockez votre clé API dans un fichier `.env` et chargez-la avec `python-dotenv`. Ne la committez jamais dans git.

```bash
# .env (ajouté dans .gitignore)
OPENAI_API_KEY=sk-...
```

```python
from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

### Chatbot OpenAI avec streaming

```python
import gradio as gr
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """Tu es un assistant spécialisé en Data Engineering.
Tu réponds en français, de manière concise et technique.
Tu utilises des exemples de code Python quand c'est pertinent."""

def repondre_openai(message: str, historique: list[dict], model: str, temperature: float):
    """Génère une réponse OpenAI avec streaming."""
    historique = historique or []
    historique.append({"role": "user", "content": message})

    # Construire les messages pour l'API OpenAI
    messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_api.extend(historique)

    # Appel OpenAI avec streaming
    stream = client.chat.completions.create(
        model=model,
        messages=messages_api,
        temperature=temperature,
        stream=True,
        max_tokens=1000,
    )

    reponse_complete = ""
    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token is not None:
            reponse_complete += token
            historique_temp = historique + [
                {"role": "assistant", "content": reponse_complete}
            ]
            yield "", historique_temp

    # Historique final avec la réponse complète
    historique.append({"role": "assistant", "content": reponse_complete})
    yield "", historique

with gr.Blocks(title="Chatbot OpenAI") as demo:
    gr.Markdown("# Chatbot GPT — Data Engineering Assistant")

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                type="messages",
                height=500,
                show_copy_button=True,
                bubble_full_width=False,
            )
            state = gr.State([])

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Posez votre question sur le Data Engineering...",
                    show_label=False,
                    scale=4,
                    max_lines=4,
                )
                btn = gr.Button("Envoyer", variant="primary", scale=1)

            btn_clear = gr.Button("Nouvelle conversation", variant="secondary")

        with gr.Column(scale=1):
            gr.Markdown("### Paramètres")
            model_select = gr.Dropdown(
                choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                value="gpt-4o-mini",
                label="Modèle",
            )
            temperature = gr.Slider(0, 2, value=0.7, step=0.05, label="Température")
            gr.Markdown("---")
            gr.Markdown("**Exemples de questions :**")
            gr.Examples(
                examples=[
                    "Explique la différence entre un Data Lake et un Data Warehouse.",
                    "Comment optimiser une requête SQL avec des JOINs sur de grandes tables ?",
                    "Quand utiliser Spark plutôt que Pandas ?",
                ],
                inputs=msg,
            )

    btn.click(repondre_openai, [msg, state, model_select, temperature], [msg, chatbot])
    msg.submit(repondre_openai, [msg, state, model_select, temperature], [msg, chatbot])
    btn_clear.click(lambda: ([], []), outputs=[chatbot, state])

demo.launch()
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration du chatbot OpenAI avec streaming, montrer les tokens qui apparaissent progressivement
> **Expliquer :** Expliquer le flux : message utilisateur → construction du contexte complet (system + historique) → appel API OpenAI avec `stream=True` → itération sur les chunks → `yield` de chaque mise à jour partielle vers Gradio. Insister sur le fait que l'API OpenAI renvoie des chunks de quelques tokens, pas des caractères.
---

## Intégration Ollama (LLM local)

Ollama permet de faire tourner des LLMs open source localement (Llama, Mistral, Qwen, etc.). Aucun coût, aucune donnée envoyée à des serveurs externes.

### Installation d'Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Démarrer le serveur Ollama
ollama serve

# Télécharger un modèle (dans un autre terminal)
ollama pull mistral        # ~4 GB
ollama pull llama3.2       # ~2 GB (plus léger)
ollama pull qwen2.5:7b     # ~4.7 GB, très bon rapport qualité/poids

# Lister les modèles disponibles
ollama list
```

### Chatbot Ollama avec streaming

```python
import gradio as gr
import ollama

def lister_modeles_ollama() -> list[str]:
    """Récupère la liste des modèles installés sur Ollama."""
    try:
        modeles = ollama.list()
        return [m.model for m in modeles.models]
    except Exception:
        return ["mistral", "llama3.2"]  # fallback

def repondre_ollama(message: str, historique: list[dict], model: str, temperature: float):
    """Génère une réponse Ollama avec streaming."""
    historique = historique or []
    historique.append({"role": "user", "content": message})

    # Ollama accepte le même format de messages qu'OpenAI
    messages_api = [
        {"role": "system", "content": "Tu es un assistant utile. Réponds en français."}
    ]
    messages_api.extend(historique)

    stream = ollama.chat(
        model=model,
        messages=messages_api,
        stream=True,
        options={"temperature": temperature},
    )

    reponse_complete = ""
    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            reponse_complete += token
            historique_temp = historique + [
                {"role": "assistant", "content": reponse_complete}
            ]
            yield "", historique_temp

    historique.append({"role": "assistant", "content": reponse_complete})
    yield "", historique

modeles_disponibles = lister_modeles_ollama()

with gr.Blocks(title="Chatbot Ollama — 100% Local") as demo:
    gr.Markdown("# Chatbot Local avec Ollama")
    gr.Markdown("Toutes vos conversations restent sur votre machine. Aucune donnée envoyée à des serveurs externes.")

    chatbot = gr.Chatbot(type="messages", height=450, show_copy_button=True)
    state = gr.State([])

    with gr.Row():
        model_select = gr.Dropdown(
            choices=modeles_disponibles,
            value=modeles_disponibles[0] if modeles_disponibles else "mistral",
            label="Modèle local",
            scale=2,
        )
        temperature = gr.Slider(0, 2, value=0.7, step=0.1, label="Température", scale=2)
        btn_refresh = gr.Button("Actualiser les modèles", scale=1)

    with gr.Row():
        msg = gr.Textbox(placeholder="Votre message...", show_label=False, scale=4)
        btn = gr.Button("Envoyer", variant="primary", scale=1)

    btn_clear = gr.Button("Nouvelle conversation", variant="secondary")

    btn.click(repondre_ollama, [msg, state, model_select, temperature], [msg, chatbot])
    msg.submit(repondre_ollama, [msg, state, model_select, temperature], [msg, chatbot])
    btn_clear.click(lambda: ([], []), outputs=[chatbot, state])
    btn_refresh.click(lister_modeles_ollama, outputs=model_select)

demo.launch()
```

## Intégration LangChain

LangChain est une abstraction qui vous permet de changer de fournisseur LLM sans modifier la logique de votre application.

```python
import gradio as gr
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

# Changer juste cette ligne pour passer d'OpenAI à Ollama
# llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)
llm = ChatOllama(model="mistral", streaming=True)

SYSTEM = SystemMessage(content="Tu es un expert en Data Engineering. Réponds en français.")

def convertir_historique_langchain(historique: list[dict]) -> list:
    """Convertit le format Gradio en format LangChain."""
    messages = [SYSTEM]
    for msg in historique:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages

def repondre_langchain(message: str, historique: list[dict]):
    historique = historique or []
    historique.append({"role": "user", "content": message})

    messages_lc = convertir_historique_langchain(historique)

    reponse_complete = ""
    for chunk in llm.stream(messages_lc):
        reponse_complete += chunk.content
        historique_temp = historique + [
            {"role": "assistant", "content": reponse_complete}
        ]
        yield "", historique_temp

    historique.append({"role": "assistant", "content": reponse_complete})
    yield "", historique

with gr.Blocks(title="Chatbot LangChain") as demo:
    gr.Markdown("# Chatbot LangChain")

    chatbot = gr.Chatbot(type="messages", height=450)
    state = gr.State([])

    with gr.Row():
        msg = gr.Textbox(placeholder="Votre message...", show_label=False, scale=4)
        btn = gr.Button("Envoyer", variant="primary", scale=1)

    btn_clear = gr.Button("Nouvelle conversation")

    btn.click(repondre_langchain, [msg, state], [msg, chatbot])
    msg.submit(repondre_langchain, [msg, state], [msg, chatbot])
    btn_clear.click(lambda: ([], []), outputs=[chatbot, state])

demo.launch()
```

## Générateurs asynchrones pour le streaming

Pour des applications à haute charge ou avec plusieurs utilisateurs simultanés, les générateurs asynchrones (`async def` + `yield`) sont plus performants :

```python
import gradio as gr
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
async_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

async def repondre_async(message: str, historique: list[dict]):
    """Version asynchrone — meilleure pour la scalabilité."""
    historique = historique or []
    historique.append({"role": "user", "content": message})

    messages_api = [
        {"role": "system", "content": "Tu es un assistant Data Engineering. Réponds en français."}
    ] + historique

    stream = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_api,
        stream=True,
    )

    reponse_complete = ""
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token is not None:
            reponse_complete += token
            historique_temp = historique + [
                {"role": "assistant", "content": reponse_complete}
            ]
            yield "", historique_temp

    historique.append({"role": "assistant", "content": reponse_complete})
    yield "", historique

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages", height=450)
    state = gr.State([])

    msg = gr.Textbox(placeholder="Votre message...", show_label=False)
    btn = gr.Button("Envoyer", variant="primary")

    btn.click(repondre_async, [msg, state], [msg, chatbot])
    msg.submit(repondre_async, [msg, state], [msg, chatbot])

demo.launch()
```

> **Quand utiliser async ?** Pour des applications avec plusieurs utilisateurs simultanés. Gradio gère nativement les générateurs async. En mode local avec un seul utilisateur, la différence n'est pas perceptible.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Comparaison côte à côte entre réponse synchrone (attente complète) et streaming (tokens progressifs)
> **Expliquer :** Ouvrir deux onglets — un avec streaming, un sans. Poser la même question. Montrer la différence d'expérience utilisateur. Expliquer que le streaming ne génère pas la réponse plus vite : il l'affiche au fur et à mesure. Le temps total de génération est identique, mais l'utilisateur a un retour immédiat.
---

## Gestion des erreurs

Un chatbot en production doit gérer les erreurs de l'API :

```python
import gradio as gr
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

def repondre_avec_gestion_erreurs(message: str, historique: list[dict]):
    historique = historique or []
    historique.append({"role": "user", "content": message})

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Tu es un assistant."}] + historique,
            stream=True,
        )

        reponse = ""
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                reponse += token
                yield "", historique + [{"role": "assistant", "content": reponse}]

        historique.append({"role": "assistant", "content": reponse})
        yield "", historique

    except RateLimitError:
        msg_erreur = "Limite de débit atteinte. Attendez quelques secondes avant de réessayer."
        historique.append({"role": "assistant", "content": f"**Erreur :** {msg_erreur}"})
        yield "", historique

    except APIConnectionError:
        msg_erreur = "Impossible de se connecter à l'API OpenAI. Vérifiez votre connexion internet."
        historique.append({"role": "assistant", "content": f"**Erreur :** {msg_erreur}"})
        yield "", historique

    except APIError as e:
        msg_erreur = f"Erreur API : {str(e)}"
        historique.append({"role": "assistant", "content": f"**Erreur :** {msg_erreur}"})
        yield "", historique
```

## Résumé du chapitre

- OpenAI et Ollama acceptent le même format de messages `[{"role": ..., "content": ...}]`
- Le streaming utilise `stream=True` côté API et `yield` côté Gradio
- LangChain abstrait le fournisseur LLM — un seul changement de ligne pour switcher
- Les générateurs `async def` + `yield` améliorent la scalabilité pour plusieurs utilisateurs
- Toujours gérer les exceptions API (RateLimit, connexion, erreurs génériques)
- Ne jamais mettre une clé API en dur dans le code — utiliser des variables d'environnement

**Prochain chapitre :** déployer l'application en production avec Docker et Hugging Face Spaces.
