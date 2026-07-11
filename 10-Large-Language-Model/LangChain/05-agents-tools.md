# 05 — Agents et Outils LangChain

## Qu'est-ce qu'un agent ?

Jusqu'à présent, les chaînes LCEL suivent un flux déterministe : chaque étape est définie à l'avance. Un **agent** est différent : il utilise le LLM comme moteur de raisonnement pour décider dynamiquement quelles actions effectuer et dans quel ordre.

```
Chaîne classique :
Input → Étape 1 → Étape 2 → Étape 3 → Output
(flux fixe, prévisible)

Agent :
Input → LLM réfléchit → choisit un outil → exécute → observe → LLM réfléchit → ... → Output
(flux dynamique, adaptatif)
```

**Quand utiliser un agent ?**
- Quand le nombre d'étapes n'est pas connu à l'avance
- Quand l'agent doit prendre des décisions conditionnelles
- Quand l'agent doit utiliser des outils externes (APIs, calculs, recherches)
- Quand les étapes dépendent des résultats précédents

---

## Le pattern ReAct

LangChain implémente principalement le pattern **ReAct** (Reasoning + Acting). Le LLM alterne entre :

1. **Thought** (Réflexion) — "Je dois calculer X, je vais utiliser l'outil calculatrice"
2. **Action** — Appel à l'outil avec les paramètres appropriés
3. **Observation** — Résultat retourné par l'outil
4. Répétition jusqu'à avoir une réponse finale

```
Question : "Quel est l'âge de la Tour Eiffel en 2024, multiplié par 3 ?"

Thought: Je dois trouver l'année de construction de la Tour Eiffel.
Action: search("année construction Tour Eiffel")
Observation: La Tour Eiffel a été construite en 1889.

Thought: L'âge en 2024 est 2024 - 1889 = 135 ans. Je dois multiplier par 3.
Action: calculator("135 * 3")
Observation: 405

Thought: J'ai la réponse.
Final Answer: L'âge de la Tour Eiffel en 2024 multiplié par 3 est 405.
```

---

## Créer des outils

### Décorateur `@tool`

```python
from langchain_core.tools import tool

@tool
def multiplier(a: float, b: float) -> float:
    """Multiplie deux nombres ensemble. Utilise cet outil pour toute multiplication."""
    return a * b

@tool
def obtenir_meteo(ville: str) -> str:
    """Obtient la météo actuelle pour une ville donnée."""
    # En réalité, vous appelleriez une vraie API météo ici
    meteos_fictives = {
        "Paris": "Ensoleillé, 22°C",
        "Lyon": "Nuageux, 18°C",
        "Marseille": "Ensoleillé, 25°C",
    }
    return meteos_fictives.get(ville, f"Données météo indisponibles pour {ville}")

# Les outils ont des métadonnées
print(multiplier.name)         # "multiplier"
print(multiplier.description)  # "Multiplie deux nombres ensemble..."
print(multiplier.args)         # {'a': {'type': 'number'}, 'b': {'type': 'number'}}

# Appeler un outil directement (pour tester)
print(multiplier.invoke({"a": 3, "b": 7}))  # 21.0
print(obtenir_meteo.invoke({"ville": "Paris"}))  # "Ensoleillé, 22°C"
```

### Tool avec validation Pydantic

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

class SearchInput(BaseModel):
    query: str = Field(description="La requête de recherche")
    max_results: Optional[int] = Field(default=5, description="Nombre maximum de résultats")

@tool("web_search", args_schema=SearchInput)
def recherche_web(query: str, max_results: int = 5) -> str:
    """Effectue une recherche sur le web et retourne les résultats pertinents."""
    # Simulation — en réalité : appel à l'API Tavily, SerpAPI, etc.
    return f"Résultats pour '{query}' (top {max_results}) : ..."
```

### Créer un outil depuis une classe

```python
from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import math

class CalculatriceInput(BaseModel):
    expression: str = Field(description="Expression mathématique à évaluer (ex: '2 + 3 * 4')")

class CalculatriceTool(BaseTool):
    name: str = "calculatrice"
    description: str = "Évalue des expressions mathématiques. Utilise-la pour tous les calculs."
    args_schema: Type[BaseModel] = CalculatriceInput

    def _run(self, expression: str) -> str:
        """Évalue une expression mathématique de façon sécurisée."""
        # Fonctions mathématiques autorisées
        safe_dict = {
            "__builtins__": {},
            "abs": abs, "round": round,
            "sqrt": math.sqrt, "pi": math.pi,
            "sin": math.sin, "cos": math.cos,
        }
        try:
            result = eval(expression, safe_dict)
            return str(result)
        except Exception as e:
            return f"Erreur de calcul : {e}"

    async def _arun(self, expression: str) -> str:
        """Version asynchrone."""
        return self._run(expression)

# Instancier l'outil
calc = CalculatriceTool()
print(calc.invoke({"expression": "sqrt(144) + pi"}))
```

---

## Créer un agent avec create_tool_calling_agent

La façon moderne (et recommandée) de créer des agents dans LangChain :

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
import datetime
import requests

# 1. Définir les outils
@tool
def date_actuelle() -> str:
    """Retourne la date et l'heure actuelles."""
    return datetime.datetime.now().strftime("%A %d %B %Y à %H:%M")

@tool
def convertir_devise(montant: float, de: str, vers: str) -> str:
    """
    Convertit un montant d'une devise à une autre.
    Devises supportées : EUR, USD, GBP, JPY, CHF.
    """
    # Taux de conversion fictifs (en réalité : appel API)
    taux = {
        ("EUR", "USD"): 1.08,
        ("USD", "EUR"): 0.93,
        ("EUR", "GBP"): 0.86,
        ("GBP", "EUR"): 1.16,
        ("EUR", "JPY"): 162.5,
        ("USD", "JPY"): 150.2,
    }
    taux_change = taux.get((de.upper(), vers.upper()))
    if taux_change:
        resultat = montant * taux_change
        return f"{montant} {de} = {resultat:.2f} {vers}"
    return f"Conversion {de} → {vers} non disponible"

@tool
def rechercher_doc_python(terme: str) -> str:
    """
    Recherche dans la documentation Python officielle.
    Utile pour trouver des informations sur les fonctions et modules Python.
    """
    # Simulation — en réalité : appel à docs.python.org
    docs_fictifs = {
        "list": "list() : Crée une liste. Méthodes : append(), extend(), insert(), remove(), pop(), sort()...",
        "dict": "dict() : Crée un dictionnaire. Méthodes : keys(), values(), items(), get(), update()...",
        "string": "str : Type chaîne de caractères. Méthodes : split(), join(), strip(), format(), upper()...",
    }
    for cle, valeur in docs_fictifs.items():
        if cle in terme.lower():
            return valeur
    return f"Documentation pour '{terme}' : consultez https://docs.python.org"

outils = [date_actuelle, convertir_devise, rechercher_doc_python]

# 2. Définir le modèle (doit supporter le tool calling)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. Définir le prompt de l'agent
prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant polyvalent expert en données et en Python.
    Tu utilises les outils à ta disposition pour répondre précisément aux questions.
    Tu expliques toujours tes raisonnements.
    Réponds en français."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # ← espace de réflexion de l'agent
])

# 4. Créer l'agent
agent = create_tool_calling_agent(llm, outils, prompt)

# 5. Créer l'exécuteur
agent_executor = AgentExecutor(
    agent=agent,
    tools=outils,
    verbose=True,        # ← affiche les étapes de raisonnement
    max_iterations=5,    # Limite le nombre d'actions
    handle_parsing_errors=True
)

# 6. Utiliser l'agent
print(agent_executor.invoke({"input": "Quelle heure est-il ? Et combien font 150 USD en EUR ?"}))
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal avec verbose=True montrant le raisonnement complet de l'agent : Thought → Action → Observation pour chaque étape
> **Expliquer :** Lancer l'agent avec une question qui nécessite plusieurs outils. Montrer dans le terminal les étapes intermédiaires : l'agent décide d'utiliser l'outil `date_actuelle`, reçoit l'observation, puis décide d'utiliser `convertir_devise`. Insister sur le fait que l'agent "raisonne" — il choisit ses outils de façon autonome. Comparer avec une chaîne LCEL classique qui aurait un flux fixe.

---

## Agent avec mémoire

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Envelopper l'agent executor avec la gestion d'historique
agent_avec_memoire = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

config = {"configurable": {"session_id": "user-demo"}}

# Tour 1
r1 = agent_avec_memoire.invoke(
    {"input": "Je veux convertir 500 EUR. Garde cette info en tête."},
    config=config
)

# Tour 2 — l'agent se souvient des 500 EUR
r2 = agent_avec_memoire.invoke(
    {"input": "Convertis ce montant en USD et en GBP."},
    config=config
)
```

---

## Outils avec APIs réelles

### Tavily Search (recherche web)

```bash
pip install langchain-tavily
```

```python
# .env
# TAVILY_API_KEY=tvly-...

from langchain_community.tools.tavily_search import TavilySearchResults

# Outil de recherche web réel
recherche = TavilySearchResults(
    max_results=3,
    search_depth="advanced"
)

# Intégrer dans les outils de l'agent
outils_avec_search = [recherche, date_actuelle, convertir_devise]
```

### Wikipedia

```bash
pip install wikipedia
```

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="fr"))

@tool
def chercher_wikipedia(query: str) -> str:
    """Recherche des informations sur Wikipedia en français."""
    return wikipedia.run(query)
```

### Outil Python REPL (exécuteur de code)

```python
from langchain_experimental.tools import PythonREPLTool

# ATTENTION : cet outil exécute du vrai code Python !
# À utiliser uniquement dans des environnements contrôlés
python_repl = PythonREPLTool()

# L'agent peut écrire et exécuter du code Python
reponse = agent_executor_avec_repl.invoke({
    "input": "Calcule la somme des 100 premiers nombres entiers avec Python."
})
```

---

## Agent de type "Data Analysis"

Un exemple pratique pour les data engineers :

```python
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import json
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Données de démo
DONNEES = pd.DataFrame({
    "region": ["Nord", "Sud", "Est", "Ouest", "Centre"] * 20,
    "ventes": [1200, 1800, 950, 2100, 1500, 1100, 1700, 900, 2000, 1400] * 10,
    "mois": list(range(1, 13)) * (100 // 12) + list(range(1, 9)),
})

@tool
def stats_ventes() -> str:
    """Retourne les statistiques générales sur les ventes."""
    stats = DONNEES["ventes"].describe()
    return f"Statistiques des ventes :\n{stats.to_string()}"

@tool
def ventes_par_region() -> str:
    """Retourne le total des ventes par région."""
    par_region = DONNEES.groupby("region")["ventes"].sum().sort_values(ascending=False)
    return f"Ventes par région :\n{par_region.to_string()}"

@tool
def top_mois(n: int = 3) -> str:
    """Retourne les N meilleurs mois en termes de ventes totales."""
    par_mois = DONNEES.groupby("mois")["ventes"].sum().nlargest(n)
    return f"Top {n} mois :\n{par_mois.to_string()}"

@tool
def filtrer_ventes(seuil_min: float) -> str:
    """Retourne les lignes où les ventes dépassent le seuil minimum donné."""
    filtrees = DONNEES[DONNEES["ventes"] > seuil_min]
    return f"{len(filtrees)} enregistrements avec ventes > {seuil_min}. Exemple :\n{filtrees.head(3).to_string()}"

outils_data = [stats_ventes, ventes_par_region, top_mois, filtrer_ventes]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu es un analyste de données expert.
    Tu analyses les données de vente en utilisant les outils disponibles.
    Tu formules toujours une synthèse claire et actionnables de tes analyses.
    Réponds en français."""),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, outils_data, prompt)
analyste = AgentExecutor(agent=agent, tools=outils_data, verbose=True)

# Analyse complète en une question
reponse = analyste.invoke({
    "input": "Fais-moi une analyse complète des ventes : stats générales, performance par région, et identifie les mois les plus forts."
})
print(reponse["output"])
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution de l'agent d'analyse avec verbose=True, montrant comment il enchaîne plusieurs outils de façon autonome
> **Expliquer :** Lancer l'agent analyste et montrer dans le terminal la séquence d'actions : l'agent appelle d'abord `stats_ventes`, puis `ventes_par_region`, puis `top_mois` de son propre chef. Souligner qu'on n'a pas dit à l'agent dans quel ordre utiliser les outils — c'est lui qui a décidé. Ouvrir ensuite LangSmith pour montrer la trace complète de l'agent avec toutes les étapes.

---

## Contrôler le comportement de l'agent

### Limiter les itérations

```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=outils,
    max_iterations=10,           # Limite absolue
    max_execution_time=30,       # Timeout en secondes
    early_stopping_method="generate",  # Si limite atteinte, forcer une réponse
    verbose=True
)
```

### Callbacks pour observer les étapes

```python
from langchain_core.callbacks import BaseCallbackHandler

class AgentLogger(BaseCallbackHandler):
    """Logger personnalisé pour les étapes de l'agent."""

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"\n🔧 Utilisation de l'outil : {serialized['name']}")
        print(f"   Paramètres : {input_str}")

    def on_tool_end(self, output, **kwargs):
        print(f"   Résultat : {output[:100]}...")

    def on_agent_action(self, action, **kwargs):
        print(f"\n💭 Raisonnement : {action.log[:200]}...")

    def on_agent_finish(self, finish, **kwargs):
        print(f"\n✅ Réponse finale : {finish.return_values['output'][:100]}...")

# Utiliser le logger
agent_executor_avec_logs = AgentExecutor(
    agent=agent,
    tools=outils,
    callbacks=[AgentLogger()],
    verbose=False  # On désactive verbose, notre callback fait mieux
)
```

---

## Outils personnalisés avancés — appel d'API

```python
import httpx
from langchain_core.tools import tool

@tool
def appeler_api_meteo(ville: str) -> str:
    """
    Récupère la météo réelle d'une ville en utilisant l'API Open-Meteo (gratuite).
    Retourne la température actuelle et les conditions météo.
    """
    # Geocoding pour obtenir les coordonnées
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ville}&count=1&language=fr"

    try:
        geo_response = httpx.get(geo_url, timeout=10)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Ville '{ville}' introuvable."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Météo actuelle
        meteo_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,wind_speed_10m,weather_code"
            f"&language=fr"
        )
        meteo_response = httpx.get(meteo_url, timeout=10)
        meteo_data = meteo_response.json()

        current = meteo_data["current"]
        temp = current["temperature_2m"]
        vent = current["wind_speed_10m"]

        return f"Météo à {ville} : {temp}°C, vent {vent} km/h"

    except Exception as e:
        return f"Erreur lors de la récupération météo : {e}"
```

---

## Structured Output Agent

Forcer l'agent à retourner une réponse structurée :

```python
from pydantic import BaseModel, Field
from typing import List

class RapportAnalyse(BaseModel):
    titre: str = Field(description="Titre du rapport")
    resume: str = Field(description="Résumé exécutif en 2-3 phrases")
    points_cles: List[str] = Field(description="Liste des points clés identifiés")
    recommandations: List[str] = Field(description="Actions recommandées")
    score_confiance: float = Field(description="Score de confiance entre 0 et 1")

# LLM avec structured output
llm_structure = ChatOpenAI(model="gpt-4o-mini").with_structured_output(RapportAnalyse)

# Chaîne qui retourne un objet Pydantic
prompt_rapport = ChatPromptTemplate.from_messages([
    ("system", "Tu es un analyste expert. Génère un rapport structuré."),
    ("human", "{question}")
])

chain_rapport = prompt_rapport | llm_structure

rapport = chain_rapport.invoke({
    "question": "Analyse les performances de notre équipe commerciale ce trimestre."
})

print(f"Titre : {rapport.titre}")
print(f"Résumé : {rapport.resume}")
print(f"Points clés : {rapport.points_cles}")
```

---

## Récapitulatif

| Concept | Rôle | Code |
|---------|------|------|
| `@tool` | Créer un outil simple | `@tool\ndef mon_outil(...): ...` |
| `BaseTool` | Outil avec validation avancée | Hériter de `BaseTool` |
| `create_tool_calling_agent` | Créer un agent | `agent = create_tool_calling_agent(llm, tools, prompt)` |
| `AgentExecutor` | Exécuter l'agent | `executor = AgentExecutor(agent, tools, verbose=True)` |
| `verbose=True` | Voir le raisonnement | Dans `AgentExecutor` |
| `max_iterations` | Limiter les étapes | Dans `AgentExecutor` |
| `agent_scratchpad` | Espace de réflexion | Dans le `MessagesPlaceholder` du prompt |

**Quand chaîne vs agent ?**
- Flux connu à l'avance → Chaîne LCEL
- Flux dynamique, outils multiples → Agent
- Performance critique → Chaîne (plus rapide et prévisible)
- Flexibilité maximale → Agent
