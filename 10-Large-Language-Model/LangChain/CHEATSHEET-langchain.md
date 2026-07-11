# LangChain — Aide-Mémoire Complet

## Installation rapide

```bash
pip install langchain langchain-openai langchain-anthropic langchain-ollama langchain-community python-dotenv
```

```bash
# .env
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=mon-projet
```

```python
from dotenv import load_dotenv
load_dotenv()  # Toujours en premier !
```

---

## LLM — Créer un modèle

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Anthropic Claude
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-haiku-20241022", temperature=0.7)

# Ollama (local, gratuit)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2", temperature=0.7)

# Appel direct
from langchain_core.messages import HumanMessage
response = llm.invoke([HumanMessage(content="Bonjour !")])
print(response.content)
```

---

## Prompts

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Prompt simple
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en {domaine}."),
    ("human", "{question}")
])

# Prompt avec historique
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Partial (pré-remplir des variables)
prompt_partiel = prompt.partial(domaine="Python")
# Maintenant seul "question" est requis

# PromptTemplate texte simple
from langchain_core.prompts import PromptTemplate
pt = PromptTemplate.from_template("Explique {concept} en {n} phrases.")
```

---

## Output Parsers

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.output_parsers import CommaSeparatedListOutputParser, PydanticOutputParser

# String
parser = StrOutputParser()
# AIMessage("Bonjour") → "Bonjour"

# Liste CSV
parser = CommaSeparatedListOutputParser()
# "a, b, c" → ["a", "b", "c"]

# Pydantic (sortie structurée)
from pydantic import BaseModel, Field
class MonSchema(BaseModel):
    titre: str = Field(description="...")
    score: int = Field(description="...")

parser = PydanticOutputParser(pydantic_object=MonSchema)
format_instructions = parser.get_format_instructions()
# Injecter dans le prompt : {format_instructions}

# Structured output (méthode moderne)
llm_structure = ChatOpenAI(model="gpt-4o-mini").with_structured_output(MonSchema)
```

---

## LCEL — Composer des chaînes

```python
# Chaîne basique
chain = prompt | llm | StrOutputParser()

# Exécuter
result = chain.invoke({"domaine": "Python", "question": "Qu'est-ce que PEP8 ?"})
result = chain.batch([{"domaine": "SQL"}, {"domaine": "Spark"}])
for chunk in chain.stream({"domaine": "Python", "question": "..."}): print(chunk, end="")

# RunnablePassthrough — passer l'input sans modification
from langchain_core.runnables import RunnablePassthrough
chain = {"question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

# RunnableParallel — exécuter en parallèle
from langchain_core.runnables import RunnableParallel
parallel = RunnableParallel(
    resume=chain_resume,
    mots_cles=chain_mots_cles
)
result = parallel.invoke({"texte": "..."})
# result["resume"], result["mots_cles"]

# RunnableLambda — fonction Python en Runnable
from langchain_core.runnables import RunnableLambda
nettoyer = RunnableLambda(lambda x: x.strip().lower())

# Fallbacks
llm_robuste = llm_principal.with_fallbacks([llm_backup])

# Retry
llm_retry = llm.with_retry(stop_after_attempt=3)
```

---

## Messages

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

human = HumanMessage(content="Bonjour")
ai = AIMessage(content="Bonjour !")
system = SystemMessage(content="Tu es un assistant.")

# Attributs utiles
msg.type      # "human", "ai", "system", "tool"
msg.content   # Contenu du message
```

---

## Mémoire conversationnelle

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Store en mémoire
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Envelopper la chaîne
chain_avec_memoire = RunnableWithMessageHistory(
    chain,                              # votre chaîne LCEL
    get_session_history,
    input_messages_key="input",         # clé de l'input dans le dict
    history_messages_key="chat_history" # nom du MessagesPlaceholder
)

# Appeler avec un session_id
config = {"configurable": {"session_id": "user-123"}}
result = chain_avec_memoire.invoke({"input": "Bonjour"}, config=config)

# Persistant dans un fichier
from langchain_community.chat_message_histories import FileChatMessageHistory
get_persistent = lambda sid: FileChatMessageHistory(f"./sessions/{sid}.json")

# Persistant dans Redis
from langchain_community.chat_message_histories import RedisChatMessageHistory
get_redis = lambda sid: RedisChatMessageHistory(sid, url="redis://localhost:6379")
```

---

## Agents et Outils

```python
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder

# Créer un outil
@tool
def mon_outil(param: str) -> str:
    """Description de ce que fait l'outil. Soyez précis !"""
    return f"Résultat pour {param}"

# Prompt pour l'agent (obligatoire : agent_scratchpad)
prompt_agent = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant. Utilise les outils disponibles."),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),  # ← NE PAS OUBLIER
])

# Créer l'agent (LLM doit supporter le tool calling)
outils = [mon_outil]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_tool_calling_agent(llm, outils, prompt_agent)

# Exécuter
executor = AgentExecutor(
    agent=agent,
    tools=outils,
    verbose=True,           # Afficher le raisonnement
    max_iterations=5,
    handle_parsing_errors=True
)
result = executor.invoke({"input": "Ta question ici"})
print(result["output"])
```

---

## Factory multi-providers

```python
# llm_factory.py
import os

def get_llm(provider=None, model=None, temperature=0.7):
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, temperature=temperature)
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, temperature=temperature)
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, temperature=temperature)
    raise ValueError(f"Provider inconnu : {provider}")
```

---

## Streaming

```python
# Streaming synchrone
for chunk in chain.stream({"input": "..."}):
    print(chunk, end="", flush=True)

# Streaming asynchrone
async for chunk in chain.astream({"input": "..."}):
    print(chunk, end="", flush=True)
```

---

## Debugging

```python
# Visualiser la chaîne
chain.get_graph().print_ascii()

# Inspecter les schémas
print(chain.input_schema.schema())
print(chain.output_schema.schema())

# LangSmith : activer le tracing (via .env)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=ls__...

# Tracing sur une section spécifique
from langchain_core.callbacks import tracing_v2_enabled
with tracing_v2_enabled(project_name="mon-projet"):
    result = chain.invoke({"input": "..."})
```

---

## Modèles OpenAI — Référence rapide

| Modèle | Contexte | Vitesse | Coût | Cas d'usage |
|--------|----------|---------|------|-------------|
| `gpt-4o` | 128k | Moyen | Élevé | Tâches complexes, multimodal |
| `gpt-4o-mini` | 128k | Rapide | Faible | Usage général (recommandé) |

## Modèles Anthropic — Référence rapide

| Modèle | Contexte | Vitesse | Coût | Cas d'usage |
|--------|----------|---------|------|-------------|
| `claude-3-5-sonnet-20241022` | 200k | Moyen | Moyen | Analyse complexe, code |
| `claude-3-5-haiku-20241022` | 200k | Rapide | Faible | Usage général économique |

## Modèles Ollama — Référence rapide

| Modèle | Taille | RAM min | Qualité |
|--------|--------|---------|---------|
| `llama3.2` | 2GB | 8GB | Bonne pour débutant |
| `llama3.2:8b` | 5GB | 16GB | Très bonne |
| `mistral` | 4GB | 8GB | Excellente pour le code |
| `mistral-nemo` | 7GB | 16GB | Très bonne, multilingue |

---

## Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `AuthenticationError` | Clé API manquante ou invalide | Vérifier `.env` et `load_dotenv()` |
| `RateLimitError` | Trop d'appels | Ajouter `with_retry()` |
| `ValidationError` | Schéma Pydantic non respecté | Vérifier `format_instructions` dans le prompt |
| `KeyError: 'agent_scratchpad'` | Placeholder manquant | Ajouter `MessagesPlaceholder("agent_scratchpad")` |
| Pas de mémoire | `history_messages_key` incorrect | Doit correspondre au `MessagesPlaceholder` |
| Ollama timeout | Serveur non démarré | `ollama serve` dans un autre terminal |

---

## Recettes rapides

### Résumé d'un texte

```python
chain = (
    ChatPromptTemplate.from_template("Résume en {n} phrases :\n{texte}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
result = chain.invoke({"n": 3, "texte": mon_texte})
```

### Classification

```python
from typing import Literal
class Classification(BaseModel):
    categorie: Literal["technique", "commercial", "rh", "autre"]
    confiance: float

llm_classe = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Classification)
result = llm_classe.invoke(f"Classifie ce texte : {texte}")
```

### Q&A sur des données

```python
chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Tu es un analyste. Réponds uniquement depuis les données fournies."),
        ("human", "Données :\n{donnees}\n\nQuestion : {question}")
    ])
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
```

### Traduction avec détection de langue

```python
chain = (
    ChatPromptTemplate.from_template(
        "Détecte la langue puis traduis en {cible} :\n{texte}"
    )
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)
```
