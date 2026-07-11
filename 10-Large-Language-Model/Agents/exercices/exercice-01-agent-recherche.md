# Exercice 01 — Agent de Recherche avec LangGraph

## Contexte

Vous êtes data engineer dans une entreprise de conseil. Votre manager souhaite un **agent de recherche intelligent** capable de répondre à des questions complexes en combinant une recherche web et une capacité de résumé. L'agent doit également pouvoir sauvegarder les résultats importants et demander confirmation avant de lancer des recherches coûteuses.

---

## Objectifs pédagogiques

À l'issue de cet exercice, vous aurez :

- Construit un agent ReAct complet de bout en bout avec LangGraph
- Défini au moins 3 outils avec `@tool`
- Implémenté un routeur conditionnel
- Ajouté la persistence via `MemorySaver` et un `thread_id`
- Intégré un mécanisme d'interruption avant l'exécution des outils
- Utilisé `stream()` pour afficher le raisonnement pas à pas

---

## Prérequis

```bash
pip install langgraph langchain-openai langchain-community tavily-python python-dotenv

# .env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...  # Optionnel — simulé si absent
```

---

## Partie 1 — Structure de base (warmup)

### Étape 1.1 — Définir l'état

Créez un fichier `agent_recherche.py` et définissez l'état de l'agent :

```python
# agent_recherche.py
import os
from typing import TypedDict, Annotated, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# TODO 1.1 : Définir l'état
# L'état doit contenir :
# - messages : historique des messages (avec réducteur add_messages)
# - recherches_effectuees : liste des requêtes déjà recherchées (avec réducteur)
# - notes_sauvegardees : liste des notes sauvegardées (avec réducteur)
# - iterations : compteur d'itérations (entier simple)

class EtatAgent(TypedDict):
    # À compléter...
    pass
```

**Solution attendue :**

```python
def accumuler(existant: list, nouveau: list) -> list:
    return existant + nouveau

class EtatAgent(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    recherches_effectuees: Annotated[list[str], accumuler]
    notes_sauvegardees: Annotated[list[str], accumuler]
    iterations: int
```

---

### Étape 1.2 — Définir les outils

Créez 3 outils :

```python
# TODO 1.2 : Définir les 3 outils suivants

# Outil 1 : rechercher_web(requete: str) -> str
# - Si TAVILY_API_KEY est disponible, utiliser TavilySearchResults
# - Sinon, simuler avec un dictionnaire de résultats prédéfinis
# - Enregistrer la requête dans l'état (hint : utiliser une variable globale temporaire
#   ou retourner l'info dans la réponse)

# Outil 2 : sauvegarder_note(contenu: str, titre: str = "Note") -> str
# - Afficher la note dans le terminal avec print()
# - Retourner un message de confirmation

# Outil 3 : calculer_statistiques(valeurs: str) -> str
# - Accepter une liste de nombres séparés par des virgules
# - Calculer : min, max, moyenne, somme
# - Retourner un résumé formaté

@tool
def rechercher_web(requete: str) -> str:
    """Recherche des informations actuelles sur le web.
    Utilise cet outil pour toute question nécessitant des données récentes ou factuelles.
    Args:
        requete: La question ou le sujet à rechercher
    """
    # À implémenter...
    pass

@tool
def sauvegarder_note(contenu: str, titre: str = "Note sans titre") -> str:
    """Sauvegarde une information importante pour référence future.
    Utilise cet outil pour mémoriser des résultats clés de la recherche.
    Args:
        contenu: Le contenu à sauvegarder
        titre: Titre descriptif de la note
    """
    # À implémenter...
    pass

@tool
def calculer_statistiques(valeurs: str) -> str:
    """Calcule des statistiques descriptives sur une série de nombres.
    Utilise cet outil quand des calculs numériques sont nécessaires.
    Args:
        valeurs: Nombres séparés par des virgules (ex: '10, 25, 30, 15')
    """
    # À implémenter...
    pass
```

**Solution attendue :**

```python
@tool
def rechercher_web(requete: str) -> str:
    """Recherche des informations actuelles sur le web.
    Utilise cet outil pour toute question nécessitant des données récentes ou factuelles.
    Args:
        requete: La question ou le sujet à rechercher
    """
    # Vérifier si Tavily est disponible
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key != "demo":
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily = TavilySearchResults(max_results=3)
        resultats = tavily.invoke({"query": requete})
        if isinstance(resultats, list):
            return "\n\n".join([f"Source: {r.get('url','?')}\n{r.get('content','')[:300]}" for r in resultats])
        return str(resultats)

    # Simulation sans API
    db_simulee = {
        "langgraph": "LangGraph est un framework de LangChain Inc. pour construire des agents sous forme de graphes d'état. Version 0.2+, Python 3.11+. Très utilisé en production pour les workflows complexes.",
        "crewai": "CrewAI permet de définir des équipes d'agents avec des rôles. Version 0.80+. Points forts : facilité d'utilisation, Process.sequential et hierarchical.",
        "openai": "OpenAI a sorti GPT-4o en mai 2024, modèle multimodal. Également GPT-4o-mini pour les usages économiques. API compatible langchain.",
        "python": "Python 3.12 est la dernière version stable (2024). Nouvelles fonctionnalités : type hints améliorés, performance JIT expérimentale.",
    }

    for cle, valeur in db_simulee.items():
        if cle in requete.lower():
            return f"Résultat pour '{requete}':\n{valeur}"

    return f"Résultat simulé pour '{requete}':\nInformation disponible mais nécessite une vraie clé API Tavily pour des données réelles."


@tool
def sauvegarder_note(contenu: str, titre: str = "Note sans titre") -> str:
    """Sauvegarde une information importante pour référence future.
    Utilise cet outil pour mémoriser des résultats clés de la recherche.
    Args:
        contenu: Le contenu à sauvegarder
        titre: Titre descriptif de la note
    """
    print(f"\n{'─'*40}")
    print(f"📝 NOTE SAUVEGARDÉE : {titre}")
    print(f"{'─'*40}")
    print(contenu)
    print(f"{'─'*40}\n")
    return f"Note '{titre}' sauvegardée avec succès ({len(contenu)} caractères)."


@tool
def calculer_statistiques(valeurs: str) -> str:
    """Calcule des statistiques descriptives sur une série de nombres.
    Utilise cet outil quand des calculs numériques sont nécessaires.
    Args:
        valeurs: Nombres séparés par des virgules (ex: '10, 25, 30, 15')
    """
    try:
        nombres = [float(v.strip()) for v in valeurs.split(",") if v.strip()]
        if not nombres:
            return "Aucun nombre valide fourni."

        n = len(nombres)
        total = sum(nombres)
        moyenne = total / n
        minimum = min(nombres)
        maximum = max(nombres)

        return f"""Statistiques sur {n} valeurs :
- Minimum : {minimum}
- Maximum : {maximum}
- Somme : {total}
- Moyenne : {moyenne:.2f}
- Écart (max-min) : {maximum - minimum}"""
    except ValueError as e:
        return f"Erreur de parsing : {str(e)}. Fournir des nombres séparés par des virgules."
```

---

## Partie 2 — Construction du graphe

### Étape 2.1 — Nœuds

```python
# TODO 2.1 : Définir les 2 nœuds de l'agent

outils = [rechercher_web, sauvegarder_note, calculer_statistiques]
llm_avec_outils = llm.bind_tools(outils)

SYSTEME_PROMPT = """Tu es un assistant de recherche expert.
Tu as accès aux outils suivants :
- rechercher_web : pour les informations récentes
- sauvegarder_note : pour mémoriser des résultats importants
- calculer_statistiques : pour les calculs numériques

Instructions :
1. Toujours chercher sur le web avant de donner des faits récents
2. Sauvegarder les résultats importants quand demandé
3. Être concis dans tes réponses finales
4. Citer tes sources quand tu as effectué une recherche"""

# Nœud 1 : noeud_agent(etat) → dict
# - Ajouter le message système si absent
# - Appeler le LLM avec outils
# - Incrémenter le compteur d'itérations
# - Retourner les modifications d'état

# Nœud 2 : Utiliser ToolNode directement
```

**Solution attendue :**

```python
def noeud_agent(etat: EtatAgent) -> dict:
    """Nœud LLM principal — raisonne et décide des actions."""
    messages = etat["messages"]
    iterations = etat.get("iterations", 0)

    # Ajouter le système si premier appel
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEME_PROMPT)] + messages

    reponse = llm_avec_outils.invoke(messages)

    return {
        "messages": [reponse],
        "iterations": iterations + 1
    }

noeud_outils = ToolNode(outils)
```

### Étape 2.2 — Routeur et graphe

```python
# TODO 2.2 : Définir le routeur et construire le graphe

MAX_ITERATIONS = 10

def routeur(etat: EtatAgent) -> str:
    """Décide si l'agent doit utiliser des outils ou terminer."""
    # Condition 1 : si trop d'itérations → forcer la fin
    # Condition 2 : si le dernier message a des tool_calls → outils
    # Sinon → fin
    pass

# Construire le graphe avec StateGraph
# Ajouter les nœuds "agent" et "outils"
# Définir le point d'entrée
# Ajouter les arêtes conditionnelles avec le routeur
# Ajouter l'arête de retour outils → agent
# Compiler AVEC MemorySaver et interrupt_before=["outils"]
```

**Solution attendue :**

```python
MAX_ITERATIONS = 10

def routeur(etat: EtatAgent) -> str:
    iterations = etat.get("iterations", 0)
    if iterations >= MAX_ITERATIONS:
        print(f"\n[⚠️] Limite d'itérations atteinte ({iterations})")
        return "fin"

    dernier = etat["messages"][-1]
    if hasattr(dernier, "tool_calls") and dernier.tool_calls:
        return "outils"
    return "fin"

# Construction
g = StateGraph(EtatAgent)
g.add_node("agent", noeud_agent)
g.add_node("outils", noeud_outils)
g.set_entry_point("agent")
g.add_conditional_edges("agent", routeur, {"outils": "outils", "fin": END})
g.add_edge("outils", "agent")

checkpointer = MemorySaver()
app = g.compile(
    checkpointer=checkpointer,
    interrupt_before=["outils"]
)

print("Graphe compilé :")
print(app.get_graph().draw_ascii())
```

---

## Partie 3 — Interface et tests

### Étape 3.1 — Fonction de chat avec approbation

```python
# TODO 3.1 : Implémenter une fonction de chat interactive

def chat_avec_approbation(question: str, thread_id: str, auto_approve: bool = False) -> str:
    """
    Envoie une question à l'agent avec possibilité d'approuver les actions d'outils.

    Args:
        question: La question à poser
        thread_id: Identifiant de session
        auto_approve: Si True, approuver automatiquement sans demander

    Returns:
        La réponse finale de l'agent
    """
    # 1. Préparer la config et l'état initial
    # 2. Streamer jusqu'à l'interruption ou la fin
    # 3. Si interruption (nœud "outils" en attente) :
    #    - Afficher les outils qui vont être appelés
    #    - Demander confirmation (ou auto-approuver)
    #    - Si approuvé : reprendre l'exécution
    #    - Si refusé : injecter un message d'annulation
    # 4. Retourner la réponse finale
    pass
```

**Solution attendue :**

```python
def chat_avec_approbation(question: str, thread_id: str, auto_approve: bool = False) -> str:
    config = {"configurable": {"thread_id": thread_id}}

    etat_initial = {
        "messages": [HumanMessage(content=question)],
        "recherches_effectuees": [],
        "notes_sauvegardees": [],
        "iterations": 0
    }

    reponse_finale = ""

    # Boucle principale (peut y avoir plusieurs cycles outil → agent)
    premier_appel = True
    while True:
        flux = app.stream(
            etat_initial if premier_appel else None,
            config,
            stream_mode="values"
        )
        premier_appel = False

        dernier_etat = None
        for event in flux:
            dernier_etat = event
            dernier = event["messages"][-1]

            if isinstance(dernier, AIMessage) and dernier.content:
                reponse_finale = dernier.content

        # Vérifier si en attente d'approbation
        etat_pause = app.get_state(config)
        if not etat_pause.next:
            break  # Terminé naturellement

        if "outils" in etat_pause.next:
            # Afficher les outils planifiés
            dernier_msg = dernier_etat["messages"][-1]
            print(f"\n[🔧 OUTILS PLANIFIÉS]")
            for tc in dernier_msg.tool_calls:
                print(f"  → {tc['name']}({tc['args']})")

            if auto_approve:
                print("[Auto-approbation activée]")
                approuve = True
            else:
                reponse = input("\nApprouver ces actions ? (o/n) : ").strip().lower()
                approuve = reponse in ["o", "oui", "y", "yes"]

            if not approuve:
                print("[Actions annulées]")
                app.update_state(
                    config,
                    {"messages": [HumanMessage(content="[SYSTÈME] L'utilisateur a refusé les actions d'outils. Réponds directement sans les appeler.")]},
                    as_node="agent"
                )
                # Reprendre sans les outils
                for event in app.stream(None, config, stream_mode="values"):
                    dernier = event["messages"][-1]
                    if isinstance(dernier, AIMessage) and dernier.content:
                        reponse_finale = dernier.content
                break
        else:
            break

    return reponse_finale
```

---

### Étape 3.2 — Tests complets

```python
# TODO 3.2 : Exécuter les tests suivants

if __name__ == "__main__":
    print("="*60)
    print("TEST 1 : Question factuelle sans outil nécessaire")
    print("="*60)
    r1 = chat_avec_approbation(
        "Quelle est la capitale de la France ?",
        thread_id="test-001",
        auto_approve=True  # Pas d'outil nécessaire normalement
    )
    print(f"Réponse : {r1}\n")

    print("="*60)
    print("TEST 2 : Recherche + sauvegarde")
    print("="*60)
    r2 = chat_avec_approbation(
        "Qu'est-ce que LangGraph ? Sauvegarde la définition en note.",
        thread_id="test-002",
        auto_approve=True
    )
    print(f"Réponse : {r2}\n")

    print("="*60)
    print("TEST 3 : Calcul statistique")
    print("="*60)
    r3 = chat_avec_approbation(
        "Calcule les statistiques pour ces valeurs : 12, 45, 23, 78, 34, 56, 9",
        thread_id="test-003",
        auto_approve=True
    )
    print(f"Réponse : {r3}\n")

    print("="*60)
    print("TEST 4 : Mémoire inter-session (thread persistant)")
    print("="*60)
    chat_avec_approbation(
        "Mon sujet de recherche préféré est l'IA éthique.",
        thread_id="test-memo",
        auto_approve=True
    )
    r4 = chat_avec_approbation(
        "Quel était mon sujet de recherche préféré ?",
        thread_id="test-memo",
        auto_approve=True
    )
    print(f"Réponse (doit mentionner IA éthique) : {r4}\n")

    print("="*60)
    print("TEST 5 : Test d'approbation interactive (refus)")
    print("="*60)
    print("(Taper 'n' quand demandé pour refuser les outils)")
    r5 = chat_avec_approbation(
        "Recherche des informations sur Python 3.12",
        thread_id="test-refus",
        auto_approve=False  # Mode interactif
    )
    print(f"Réponse après refus : {r5}")
```

---

## Partie 4 — Bonus (si le temps le permet)

### Bonus A — Streaming du raisonnement

Modifiez `noeud_agent` pour afficher le raisonnement token par token :

```python
# Hint : utiliser llm_avec_outils.stream() au lieu de .invoke()
# et yield les tokens si dans un contexte de streaming LangGraph
```

### Bonus B — Métriques d'utilisation

Ajoutez un nœud de logging qui s'exécute après chaque outil :

```python
def noeud_metriques(etat: EtatAgent) -> dict:
    """Logge les métriques après chaque appel d'outil."""
    dernier = etat["messages"][-1]
    if isinstance(dernier, ToolMessage):
        print(f"[MÉTRIQUE] Outil '{dernier.name}' → {len(dernier.content)} chars de résultat")
    return {}
```

### Bonus C — Visualisation avec LangSmith

```python
# Activer le tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "exercice-01-agent-recherche"
# Toutes les exécutions apparaîtront sur smith.langchain.com
```

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| État TypedDict correct avec réducteurs | 2 |
| 3 outils fonctionnels avec docstrings | 3 |
| Routeur avec protection anti-boucle | 2 |
| Graphe compilé avec MemorySaver | 2 |
| interrupt_before opérationnel | 2 |
| Mémoire inter-session (thread_id) | 2 |
| Tests 1-4 passants | 4 |
| Code propre et commenté | 3 |
| **Total** | **20** |

---

## Solution complète

Le fichier solution complet (`agent_recherche_solution.py`) est disponible dans ce même dossier. N'y regardez qu'après avoir tenté de résoudre les étapes vous-même.

---

## Questions de réflexion

1. Pourquoi utilise-t-on `add_messages` comme réducteur pour la liste de messages, et non un simple remplacement ?

2. Si un utilisateur ouvre deux onglets et envoie des messages en parallèle, que se passe-t-il si les deux utilisent le même `thread_id` ?

3. Comment protégeriez-vous cet agent contre des questions hors-sujet (out-of-scope) ?

4. Dans quel cas `interrupt_before=["outils"]` ne serait PAS suffisant comme mécanisme de sécurité ?
