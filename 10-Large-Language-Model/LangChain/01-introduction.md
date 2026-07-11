# 01 — Introduction à LangChain

## Qu'est-ce que LangChain ?

LangChain est un framework open-source créé en 2022 par Harrison Chase. Son objectif principal est de fournir une couche d'abstraction pour construire des applications alimentées par des LLM (Large Language Models) de manière modulaire, composable et maintenable.

Sans LangChain, intégrer un LLM dans une application nécessite de gérer manuellement :
- Les appels HTTP vers différentes API (OpenAI, Anthropic, etc.)
- Le formatage des prompts et des messages
- L'historique des conversations
- La gestion des erreurs et des retries
- L'orchestration de plusieurs étapes de traitement

LangChain résout ces problèmes en fournissant des abstractions standardisées et des composants réutilisables.

---

## L'écosystème LangChain

L'écosystème LangChain est composé de plusieurs packages complémentaires :

### langchain-core
Le package fondamental. Contient les interfaces abstraites (Runnable, BaseMessage, etc.) sans dépendances lourdes.

```bash
pip install langchain-core
```

### langchain
Le package principal avec les chaînes prédéfinies, les agents, et les utilitaires de haut niveau.

```bash
pip install langchain
```

### langchain-openai
Intégration spécifique pour OpenAI (ChatOpenAI, OpenAIEmbeddings).

```bash
pip install langchain-openai
```

### langchain-community
Intégrations tierces maintenues par la communauté (plus de 300 intégrations).

```bash
pip install langchain-community
```

### langchain-anthropic
Intégration pour les modèles Claude d'Anthropic.

```bash
pip install langchain-anthropic
```

### LangSmith
Plateforme de tracing, debugging et évaluation (service cloud séparé).

### LangServe
Pour déployer des chaînes LangChain comme APIs REST.

---

## Installation complète

```bash
# Environnement de développement complet
pip install langchain langchain-openai langchain-anthropic langchain-community
pip install python-dotenv  # pour gérer les variables d'environnement

# Pour les modèles locaux avec Ollama
pip install langchain-ollama

# Pour le tracing avec LangSmith
pip install langsmith
```

### Fichier .env

```bash
# .env — ne jamais committer ce fichier !
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=mon-projet
```

```python
# Charger les variables d'environnement au début de chaque script
from dotenv import load_dotenv
load_dotenv()
```

---

## Vérifier l'installation

```python
# test_installation.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = llm.invoke("Dis bonjour en une phrase.")
print(response.content)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec l'installation des packages pip et l'exécution de `test_installation.py`
> **Expliquer :** Montrer la commande pip install, vérifier qu'il n'y a pas d'erreurs, puis lancer le script et montrer que le LLM répond. Insister sur la nécessité du fichier `.env` et du `load_dotenv()`. Montrer aussi `pip show langchain` pour vérifier la version installée.

---

## LangChain vs appels API bruts

### Approche sans LangChain

```python
# Approche traditionnelle : appel direct à l'API OpenAI
import openai
import os

client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def chat_with_history(messages, user_message):
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})
    return assistant_message, messages

# Utilisation
history = [{"role": "system", "content": "Tu es un assistant utile."}]
response, history = chat_with_history(history, "Quelle est la capitale de France ?")
print(response)
```

**Problèmes de cette approche :**
- Code fortement couplé à OpenAI
- Gestion manuelle de l'historique
- Formatage des messages à la main
- Difficile de changer de provider
- Pas de gestion des erreurs robuste
- Pas de tracing ni d'observabilité

### Approche avec LangChain

```python
# Approche LangChain : abstraction et composabilité
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Modèle — peut être remplacé par n'importe quel autre LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Prompt avec historique intégré
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant utile et concis."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Chaîne composée
chain = prompt | llm

# Utilisation
history = []
response = chain.invoke({
    "history": history,
    "input": "Quelle est la capitale de France ?"
})
print(response.content)

# Mettre à jour l'historique
history.append(HumanMessage(content="Quelle est la capitale de France ?"))
history.append(AIMessage(content=response.content))
```

### Tableau comparatif

| Aspect | API brute | LangChain |
|--------|-----------|-----------|
| Portabilité | Couplé au provider | Abstraction multi-provider |
| Gestion historique | Manuelle | Composants dédiés |
| Composition | Code spaghetti | Chaînes LCEL |
| Debugging | `print()` | LangSmith traces |
| Prompts | Strings ad-hoc | Templates structurés |
| Parsing | Manuel | Output parsers |
| Retry/erreurs | À coder | Intégré |

---

## Concepts fondamentaux

### 1. Runnables — l'interface universelle

En LangChain, presque tout implémente l'interface `Runnable`. Cette interface définit des méthodes standardisées :

```python
# Toutes les méthodes disponibles sur un Runnable
runnable.invoke(input)           # Appel synchrone unique
runnable.batch([input1, input2]) # Appel synchrone sur plusieurs inputs
runnable.stream(input)           # Streaming token par token (sync)

await runnable.ainvoke(input)    # Appel asynchrone unique
await runnable.abatch([...])     # Appel asynchrone batch
runnable.astream(input)          # Streaming asynchrone

# Introspection
runnable.input_schema            # Schéma d'entrée
runnable.output_schema           # Schéma de sortie
```

### 2. Messages — les types de communication

```python
from langchain_core.messages import (
    HumanMessage,     # Message de l'utilisateur
    AIMessage,        # Message du modèle
    SystemMessage,    # Instruction système
    ToolMessage,      # Résultat d'un outil
    FunctionMessage,  # Appel de fonction (legacy)
)

# Créer des messages
human_msg = HumanMessage(content="Bonjour !")
system_msg = SystemMessage(content="Tu es un expert Python.")
ai_msg = AIMessage(content="Bonjour ! Comment puis-je vous aider ?")

# Les messages ont des attributs utiles
print(human_msg.type)       # "human"
print(human_msg.content)    # "Bonjour !"
```

### 3. Prompts — les templates structurés

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    MessagesPlaceholder
)

# Template simple
simple_prompt = PromptTemplate.from_template(
    "Résume ce texte en {nb_mots} mots : {texte}"
)

# Vérifier les variables
print(simple_prompt.input_variables)  # ['nb_mots', 'texte']

# Formater le prompt
formatted = simple_prompt.format(nb_mots=50, texte="Long texte ici...")
print(formatted)

# Template de chat
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en {domaine}."),
    ("human", "{question}")
])

# Invoquer le template
messages = chat_prompt.invoke({
    "domaine": "machine learning",
    "question": "Qu'est-ce que le gradient descent ?"
})
print(messages)
```

### 4. Output Parsers — structurer les sorties

```python
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    CommaSeparatedListOutputParser
)

# Parser string simple
str_parser = StrOutputParser()
# Transforme AIMessage("Bonjour") → "Bonjour"

# Parser liste
list_parser = CommaSeparatedListOutputParser()
# Transforme "chat, chien, lapin" → ["chat", "chien", "lapin"]

# Parser JSON
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class PersonneInfo(BaseModel):
    nom: str = Field(description="Nom de la personne")
    age: int = Field(description="Âge en années")
    profession: str = Field(description="Profession")

pydantic_parser = PydanticOutputParser(pydantic_object=PersonneInfo)
print(pydantic_parser.get_format_instructions())
```

---

## Premier exemple complet

```python
# premier_exemple.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Définir le modèle
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. Définir le prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en {domaine}. Tes réponses sont claires et concises."),
    ("human", "{question}")
])

# 3. Définir le parser
parser = StrOutputParser()

# 4. Composer la chaîne (LCEL)
chain = prompt | llm | parser

# 5. Invoquer
reponse = chain.invoke({
    "domaine": "astronomie",
    "question": "Combien de planètes dans le système solaire ?"
})

print(reponse)
# Output: "Le système solaire compte 8 planètes : Mercure, Vénus, la Terre..."
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution de `premier_exemple.py` dans le terminal, puis ouverture de LangSmith pour voir la trace générée
> **Expliquer :** Montrer le code étape par étape (LLM → prompt → parser → chaîne), lancer le script, afficher le résultat dans le terminal. Ensuite, ouvrir le dashboard LangSmith sur smith.langchain.com, naviguer vers le projet, et montrer la trace complète avec les tokens utilisés, la latence, et les inputs/outputs de chaque étape.

---

## LangSmith — tracing et debugging

LangSmith est l'outil de monitoring pour les applications LangChain. Il enregistre automatiquement toutes les exécutions lorsque le tracing est activé.

### Configuration

```python
# Option 1 : via .env (recommandé)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=ls__...
# LANGCHAIN_PROJECT=mon-projet

# Option 2 : programmatique
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "formation-langchain"
```

### Ce que LangSmith trace automatiquement

- Chaque appel à un LLM (input, output, tokens, coût estimé)
- Chaque étape d'une chaîne LCEL
- Les appels aux outils dans les agents
- La latence de chaque composant
- Les erreurs et exceptions

```python
# Ajouter des métadonnées à une trace
from langchain_core.callbacks import tracing_v2_enabled

with tracing_v2_enabled(project_name="test-projet"):
    reponse = chain.invoke({"domaine": "chimie", "question": "Qu'est-ce que le pH ?"})
```

---

## Architecture interne — comment LangChain fonctionne

```
Application Python
      │
      ▼
  LangChain Core
  ┌─────────────────────────────────────┐
  │  Runnable (interface universelle)   │
  │  ┌──────┐  ┌──────┐  ┌──────────┐ │
  │  │Prompt│→ │ LLM  │→ │  Parser  │ │
  │  └──────┘  └──────┘  └──────────┘ │
  └─────────────────────────────────────┘
      │
      ▼
  Provider (OpenAI / Anthropic / Ollama)
      │
      ▼
  API externe / Modèle local
```

Le flux d'exécution :
1. L'input (dict) entre dans la chaîne
2. Le PromptTemplate le transforme en messages formatés
3. Le LLM reçoit ces messages et génère une réponse (AIMessage)
4. L'output parser transforme l'AIMessage en format final (str, JSON, objet Pydantic...)

---

## Bonnes pratiques dès le départ

### Toujours utiliser des variables d'environnement

```python
# Mauvais
llm = ChatOpenAI(api_key="sk-proj-...")  # NE JAMAIS faire ça !

# Bon
from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI()  # Lit OPENAI_API_KEY depuis l'environnement
```

### Versionner les prompts

```python
# Mauvais — prompt inline difficile à maintenir
chain = ChatPromptTemplate.from_template("fais {task}") | llm

# Bon — prompt nommé et documenté
SYSTEM_PROMPT = """Tu es un assistant expert en data engineering.
Tu réponds toujours en français, de manière précise et concise.
Si tu n'es pas sûr d'une information, tu le signales clairement."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])
```

### Gérer les erreurs

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.exceptions import LangChainException

try:
    reponse = chain.invoke({"question": "..."})
except LangChainException as e:
    print(f"Erreur LangChain : {e}")
except Exception as e:
    print(f"Erreur inattendue : {e}")
```

---

## Récapitulatif

| Concept | Rôle |
|---------|------|
| `ChatOpenAI` / `ChatOllama` | Interface vers le LLM |
| `ChatPromptTemplate` | Structurer les entrées |
| `StrOutputParser` | Transformer la sortie |
| `chain = prompt \| llm \| parser` | Composer les étapes |
| `chain.invoke({...})` | Exécuter la chaîne |
| LangSmith | Observer et déboguer |

La suite : [02-lcel-chains.md](./02-lcel-chains.md) — Aller plus loin avec LCEL
