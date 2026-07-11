# LangGraph — Agent Réactif (ReAct)

## Objectifs

- Comprendre le pattern ReAct (Reasoning + Acting)
- Définir des outils compatibles LangGraph avec `@tool`
- Utiliser `ToolNode` pour l'exécution automatique des outils
- Implémenter un agent ReAct complet avec boucle décisionnelle
- Ajouter le mécanisme human-in-the-loop avec `interrupt_before`

---

## Le pattern ReAct

ReAct (Reasoning and Acting) est le pattern de raisonnement le plus utilisé pour les agents LLM. Il alterne entre :

```
Thought   → Le LLM réfléchit à ce qu'il doit faire
Action    → Le LLM choisit un outil et ses paramètres
Observation → L'outil s'exécute, le résultat est retourné
Thought   → Le LLM évalue le résultat et décide de la suite
...
Answer    → Le LLM produit la réponse finale
```

Dans LangGraph, ce pattern se traduit par :

```
┌─────────┐    appel outil    ┌───────────┐
│  agent  │ ───────────────► │   outils  │
│  (LLM)  │ ◄─────────────── │ (ToolNode)│
└────┬────┘    observation    └───────────┘
     │
     │ pas d'appel outil
     ▼
   END
```

---

## Définir des outils

Les outils LangGraph utilisent le décorateur `@tool` de LangChain. La **docstring** est cruciale — le LLM l'utilise pour décider quand appeler l'outil.

```python
# tools.py
from langchain_core.tools import tool
import requests
import json

@tool
def rechercher_web(requete: str) -> str:
    """Recherche des informations sur le web.
    Utilise cet outil quand tu as besoin d'informations récentes ou factuelles.

    Args:
        requete: La question ou le sujet à rechercher

    Returns:
        Les résultats de recherche sous forme de texte
    """
    # En production : utiliser Tavily, SerpAPI, etc.
    # Exemple avec Tavily :
    from tavily import TavilyClient
    client = TavilyClient()
    resultats = client.search(requete, max_results=3)

    texte = ""
    for r in resultats.get("results", []):
        texte += f"Titre: {r['title']}\n"
        texte += f"URL: {r['url']}\n"
        texte += f"Contenu: {r['content'][:300]}\n\n"
    return texte or "Aucun résultat trouvé."


@tool
def calculer(expression: str) -> str:
    """Effectue un calcul mathématique.
    Utilise cet outil pour toute opération arithmétique ou algébrique.

    Args:
        expression: L'expression mathématique à évaluer (ex: '2 + 2', '15 * 7 / 3')

    Returns:
        Le résultat du calcul
    """
    try:
        # Sécurité basique : n'autoriser que les opérations mathématiques
        allowed = set('0123456789+-*/()., ')
        if all(c in allowed for c in expression):
            resultat = eval(expression)
            return f"Résultat de '{expression}' = {resultat}"
        else:
            return "Expression invalide : seules les opérations arithmétiques de base sont autorisées."
    except Exception as e:
        return f"Erreur de calcul : {str(e)}"


@tool
def sauvegarder_note(contenu: str, titre: str = "Note sans titre") -> str:
    """Sauvegarde une note ou un résultat important.
    Utilise cet outil pour mémoriser des informations importantes pendant la session.

    Args:
        contenu: Le contenu de la note
        titre: Le titre de la note (optionnel)

    Returns:
        Confirmation de la sauvegarde
    """
    # En production : sauvegarder dans une base de données
    print(f"\n[NOTE SAUVEGARDÉE]\nTitre: {titre}\nContenu: {contenu}\n")
    return f"Note '{titre}' sauvegardée avec succès."
```

---

## Agent ReAct complet

```python
# agent_react.py
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

# --- OUTILS ---
from langchain_core.tools import tool

@tool
def calculer(expression: str) -> str:
    """Effectue un calcul mathématique. Utilise pour tout calcul numérique.
    Args:
        expression: Expression Python valide (ex: '2**10', '15 * 7')
    """
    try:
        allowed = set('0123456789+-*/()., ')
        if all(c in allowed for c in expression):
            return f"{expression} = {eval(expression)}"
        return "Expression non autorisée"
    except Exception as e:
        return f"Erreur: {str(e)}"

@tool
def obtenir_meteo(ville: str) -> str:
    """Obtient la météo actuelle pour une ville.
    Utilise quand l'utilisateur demande des informations météo.
    Args:
        ville: Nom de la ville
    """
    # Simulation — en production, appeler une vraie API météo
    meteos = {
        "paris": "Nuageux, 12°C, vent 15km/h",
        "lyon": "Ensoleillé, 18°C, vent 8km/h",
        "marseille": "Partiellement nuageux, 22°C, vent 20km/h",
        "default": "Données non disponibles pour cette ville"
    }
    return meteos.get(ville.lower(), meteos["default"])

@tool
def rechercher_info(sujet: str) -> str:
    """Recherche des informations générales sur un sujet.
    Utilise pour répondre à des questions factuelles ou obtenir des données.
    Args:
        sujet: Le sujet ou la question à rechercher
    """
    # Simulation — en production, utiliser Tavily ou autre API
    infos = {
        "langgraph": "LangGraph est un framework de construction d'agents IA basé sur des graphes d'état, développé par LangChain Inc.",
        "python": "Python est un langage de programmation interprété, multi-paradigme, créé par Guido van Rossum en 1991.",
    }
    for cle, valeur in infos.items():
        if cle in sujet.lower():
            return valeur
    return f"Information sur '{sujet}': Sujet complexe nécessitant une recherche approfondie. [Simulation]"

# Liste des outils disponibles
outils = [calculer, obtenir_meteo, rechercher_info]

# --- LLM AVEC OUTILS ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_avec_outils = llm.bind_tools(outils)

# --- ÉTAT ---
class EtatAgent(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- NOEUDS ---
PROMPT_SYSTEME = """Tu es un assistant IA utile et précis.
Tu as accès aux outils suivants pour t'aider à répondre :
- calculer : pour les calculs mathématiques
- obtenir_meteo : pour la météo des villes
- rechercher_info : pour des informations générales

Utilise les outils quand c'est nécessaire. Si tu peux répondre directement, fais-le sans appeler d'outil."""

def noeud_agent(etat: EtatAgent) -> dict:
    """Nœud principal : le LLM décide quoi faire."""
    messages = etat["messages"]

    # Ajouter le message système si c'est le premier appel
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=PROMPT_SYSTEME)] + messages

    reponse = llm_avec_outils.invoke(messages)
    return {"messages": [reponse]}

# ToolNode gère automatiquement l'exécution des outils appelés par le LLM
noeud_outils = ToolNode(outils)

# --- ROUTEUR ---
def continuer_ou_terminer(etat: EtatAgent) -> str:
    """Vérifie si le dernier message contient des appels d'outils."""
    dernier_message = etat["messages"][-1]

    # Si le LLM a fait des appels d'outils, les exécuter
    if hasattr(dernier_message, "tool_calls") and dernier_message.tool_calls:
        return "utiliser_outils"

    # Sinon, c'est la réponse finale
    return "terminer"

# --- GRAPHE ---
constructeur = StateGraph(EtatAgent)

constructeur.add_node("agent", noeud_agent)
constructeur.add_node("outils", noeud_outils)

constructeur.set_entry_point("agent")

constructeur.add_conditional_edges(
    "agent",
    continuer_ou_terminer,
    {
        "utiliser_outils": "outils",
        "terminer": END
    }
)

# Après exécution des outils, retour vers l'agent
constructeur.add_edge("outils", "agent")

application = constructeur.compile()

# --- VISUALISATION ---
print("Structure du graphe :")
print(application.get_graph().draw_ascii())

# Générer le diagramme Mermaid
print("\nDiagramme Mermaid :")
print(application.get_graph().draw_mermaid())
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La visualisation ASCII du graphe ReAct : le diagramme doit montrer le nœud `agent` avec deux arêtes conditionnelles sortantes (une vers `outils`, une vers `__end__`) et une arête de retour `outils → agent`.
> **Expliquer :** Ce diagramme est exactement le pattern ReAct classique : le nœud agent est le "cerveau", le nœud outils est le "bras". La boucle agent → outils → agent se répète jusqu'à ce que le LLM décide de ne plus appeler d'outils. Comparer avec le diagramme d'un simple LLM (deux nœuds, une arête) pour montrer la complexité ajoutée.

---

```python
# --- TEST ---
def poser_question(question: str):
    print(f"\n{'='*60}")
    print(f"Question : {question}")
    print(f"{'='*60}")

    etat_initial = {"messages": [HumanMessage(content=question)]}

    for event in application.stream(etat_initial, stream_mode="values"):
        dernier_message = event["messages"][-1]

        if isinstance(dernier_message, AIMessage):
            if dernier_message.tool_calls:
                for tc in dernier_message.tool_calls:
                    print(f"\n[APPEL OUTIL] {tc['name']}({tc['args']})")
            elif dernier_message.content:
                print(f"\n[RÉPONSE FINALE]\n{dernier_message.content}")

        elif isinstance(dernier_message, ToolMessage):
            print(f"[RÉSULTAT OUTIL] {dernier_message.content[:200]}")

# Tests
poser_question("Combien font 1234 * 5678 ?")
poser_question("Quelle est la météo à Paris et à Lyon ? Compare les deux.")
poser_question("Qu'est-ce que LangGraph ? Et combien font 42 * 42 ?")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `agent_react.py` pour la question "Quelle est la météo à Paris et à Lyon ? Compare les deux." — montrer les deux appels d'outils successifs `[APPEL OUTIL] obtenir_meteo(...)` puis la réponse finale de comparaison.
> **Expliquer :** Montrer que le LLM appelle les deux outils séquentiellement (Paris puis Lyon), lit les observations, et synthétise une comparaison sans qu'on ait programmé cette logique explicitement — c'est le LLM qui raisonne sur quand et comment utiliser les outils.

---

## Human-in-the-loop avec interrupt_before

Le human-in-the-loop permet d'**interrompre** le graphe avant l'exécution d'un nœud pour obtenir une validation humaine.

```python
# agent_avec_validation.py
from langgraph.checkpoint.memory import MemorySaver

# Créer un checkpointer pour sauvegarder l'état
checkpointer = MemorySaver()

# Compiler avec interruption AVANT le nœud "outils"
application_avec_pause = constructeur.compile(
    checkpointer=checkpointer,
    interrupt_before=["outils"]  # Pause avant d'exécuter les outils
)

# Configuration d'une session (thread_id = identifiant de conversation)
config = {"configurable": {"thread_id": "session-001"}}

# --- Première exécution ---
print("=== Démarrage ===")
question = "Cherche la météo à Marseille et calcule 99 * 88"
etat_initial = {"messages": [HumanMessage(content=question)]}

# Le graphe s'arrête avant "outils"
for event in application_avec_pause.stream(etat_initial, config, stream_mode="values"):
    dernier_message = event["messages"][-1]
    if isinstance(dernier_message, AIMessage) and dernier_message.tool_calls:
        print(f"\nL'agent veut appeler :")
        for tc in dernier_message.tool_calls:
            print(f"  - {tc['name']} avec {tc['args']}")

# Vérifier que le graphe est en attente
etat_actuel = application_avec_pause.get_state(config)
print(f"\nProchain(s) nœud(s) : {etat_actuel.next}")

# --- Demander confirmation ---
confirmation = input("\nApprouver les appels d'outils ? (oui/non) : ").strip().lower()

if confirmation == "oui":
    # Reprendre l'exécution depuis l'état sauvegardé
    print("\n=== Reprise de l'exécution ===")
    for event in application_avec_pause.stream(None, config, stream_mode="values"):
        dernier_message = event["messages"][-1]
        if isinstance(dernier_message, ToolMessage):
            print(f"[OUTIL] {dernier_message.name}: {dernier_message.content[:100]}")
        elif isinstance(dernier_message, AIMessage) and dernier_message.content:
            print(f"\n[RÉPONSE FINALE]\n{dernier_message.content}")
else:
    print("Appels d'outils annulés par l'utilisateur.")
```

### Modifier l'état avant de reprendre

Vous pouvez aussi **modifier l'état** avant de reprendre :

```python
# Lire l'état actuel
etat_actuel = application_avec_pause.get_state(config)

# Injecter une instruction supplémentaire
from langchain_core.messages import HumanMessage
application_avec_pause.update_state(
    config,
    {"messages": [HumanMessage(content="[Ajout humain] Aussi mentionner l'heure locale.")]},
)

# Reprendre
for event in application_avec_pause.stream(None, config, stream_mode="values"):
    ...
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution interactive avec la pause "L'agent veut appeler :" qui s'affiche, l'invite `Approuver les appels d'outils ? (oui/non) :` qui attend une saisie, puis la reprise après saisie de "oui".
> **Expliquer :** C'est un cas d'usage critique pour les applications de production où les outils ont des effets de bord (envoi d'email, modification de base de données, appels API payants). L'interruption permet une supervision humaine avant l'action.

---

## Utiliser ToolNode correctement

`ToolNode` est un nœud préfabriqué qui :
1. Lit les `tool_calls` du dernier message `AIMessage`
2. Exécute chaque outil
3. Retourne des `ToolMessage` avec les résultats

```python
from langgraph.prebuilt import ToolNode

# Créer un ToolNode avec la liste des outils
noeud_outils = ToolNode(outils)

# ToolNode gère automatiquement les erreurs
noeud_outils_robuste = ToolNode(
    outils,
    handle_tool_errors=True  # Les erreurs d'outils sont capturées et retournées comme ToolMessage
)
```

Comportement interne de ToolNode :

```python
# Ce que ToolNode fait en substance (version simplifiée)
def tool_node_manuel(etat: EtatAgent) -> dict:
    dernier_message = etat["messages"][-1]
    resultats = []

    for appel in dernier_message.tool_calls:
        outil_correspondant = next(o for o in outils if o.name == appel["name"])
        try:
            resultat = outil_correspondant.invoke(appel["args"])
        except Exception as e:
            resultat = f"Erreur: {str(e)}"

        resultats.append(ToolMessage(
            content=str(resultat),
            tool_call_id=appel["id"],
            name=appel["name"]
        ))

    return {"messages": resultats}
```

---

## Agent avec outils réels (Tavily)

Version production avec la vraie recherche web via Tavily :

```python
# agent_production.py
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# Outil de recherche Tavily (nécessite TAVILY_API_KEY)
outil_recherche = TavilySearchResults(
    max_results=3,
    search_depth="advanced",
    include_answer=True,
)

# Calculatrice simple
from langchain_core.tools import tool

@tool
def calculatrice(expression: str) -> str:
    """Effectue des calculs mathématiques. Args: expression (str): Expression Python."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Erreur: {e}"

outils = [outil_recherche, calculatrice]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_avec_outils = llm.bind_tools(outils)

class EtatAgent(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEME = "Tu es un assistant utile qui utilise les outils disponibles pour répondre précisément."

def agent(etat: EtatAgent) -> dict:
    msgs = etat["messages"]
    if not any(isinstance(m, SystemMessage) for m in msgs):
        msgs = [SystemMessage(content=SYSTEME)] + msgs
    return {"messages": [llm_avec_outils.invoke(msgs)]}

# tools_condition est une fonction de routage préfabriquée
# Elle remplace notre fonction continuer_ou_terminer
from langgraph.prebuilt import tools_condition

g = StateGraph(EtatAgent)
g.add_node("agent", agent)
g.add_node("outils", ToolNode(outils))
g.set_entry_point("agent")
g.add_conditional_edges("agent", tools_condition)
g.add_edge("outils", "agent")
app = g.compile()

# Test
resultat = app.invoke({
    "messages": [HumanMessage(content="Quelle est la population de Paris en 2024 ? Et combien font 8_500_000 * 1.03 ?")]
})
print(resultat["messages"][-1].content)
```

---

## Gestion des erreurs d'outils

```python
from langchain_core.messages import ToolMessage

def noeud_agent_robuste(etat: EtatAgent) -> dict:
    """Agent avec gestion d'erreur — si un outil échoue, l'agent peut réessayer."""
    messages = etat["messages"]

    # Vérifier si le dernier message était une erreur d'outil
    if messages and isinstance(messages[-1], ToolMessage):
        if "Erreur" in messages[-1].content or "error" in messages[-1].content.lower():
            # Ajouter une instruction pour que le LLM gère l'erreur
            messages = messages + [HumanMessage(
                content="L'outil précédent a échoué. Essaie une approche différente ou réponds directement."
            )]

    reponse = llm_avec_outils.invoke(messages)
    return {"messages": [reponse]}
```

---

## Points clés à retenir

1. Le décorateur `@tool` avec une **docstring précise** est crucial — le LLM la lit pour décider quand appeler l'outil
2. `ToolNode` gère l'exécution automatique des outils — pas besoin de le faire manuellement
3. Le routeur `continuer_ou_terminer` (ou `tools_condition`) détecte la présence de `tool_calls` dans le dernier message
4. `interrupt_before=["outils"]` permet d'interrompre avant l'exécution pour validation humaine
5. `MemorySaver` comme checkpointer est requis pour la persistence entre les étapes interrompues
6. `stream(mode="values")` permet de voir l'état complet après chaque nœud

---

## Suite

Passez à `04-multi-agents.md` pour apprendre à orchestrer plusieurs agents spécialisés avec le pattern superviseur.
