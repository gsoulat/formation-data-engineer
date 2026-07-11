# LangGraph — Persistence et Mémoire

## Objectifs

- Comprendre le rôle des checkpointers dans LangGraph
- Utiliser `MemorySaver` pour la persistence en mémoire
- Utiliser `SqliteSaver` pour la persistence sur disque
- Gérer les `thread_id` pour des conversations multiples
- Reprendre une conversation interrompue

---

## Le problème sans persistence

Sans persistence, chaque appel à `invoke()` repart de zéro :

```python
# Sans checkpointer — pas de mémoire entre les appels
app = graphe.compile()  # Pas de checkpointer

# Premier appel
app.invoke({"messages": [HumanMessage(content="Mon nom est Alice")]})

# Deuxième appel — le graphe ne se souvient pas d'Alice
resultat = app.invoke({"messages": [HumanMessage(content="Comment je m'appelle ?")]})
print(resultat)  # "Je ne sais pas votre nom..."
```

Avec un checkpointer, chaque état est sauvegardé après chaque nœud :

```
Étape 1: noeud_a → état sauvegardé (checkpoint A)
Étape 2: noeud_b → état sauvegardé (checkpoint B)
Étape 3: noeud_c → état sauvegardé (checkpoint C)
         ↑
         On peut reprendre depuis n'importe quel checkpoint
```

---

## MemorySaver — Persistence en RAM

`MemorySaver` stocke les états en mémoire. Utile pour le développement et les sessions courtes.

```python
# memory_saver_demo.py
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- ÉTAT ---
class EtatConversation(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# --- NŒUD ---
SYSTEME = "Tu es un assistant conversationnel. Tu te souviens de tout ce qui a été dit dans la conversation."

def noeud_chat(etat: EtatConversation) -> dict:
    messages = etat["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEME)] + messages
    reponse = llm.invoke(messages)
    return {"messages": [reponse]}

# --- GRAPHE AVEC CHECKPOINTER ---
g = StateGraph(EtatConversation)
g.add_node("chat", noeud_chat)
g.set_entry_point("chat")
g.add_edge("chat", END)

# Créer le checkpointer
checkpointer = MemorySaver()

# Compiler AVEC le checkpointer
app = g.compile(checkpointer=checkpointer)

# --- GESTION DES THREADS ---
# Un thread_id = une conversation distincte
# Plusieurs utilisateurs peuvent avoir des conversations indépendantes

def chat(message: str, thread_id: str) -> str:
    """Envoie un message dans une conversation identifiée par thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    etat = app.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )
    return etat["messages"][-1].content


# Conversation 1 — Alice
print("=== Conversation Alice (thread: alice-001) ===")
print(chat("Bonjour ! Mon nom est Alice et j'adore Python.", thread_id="alice-001"))
print(chat("Quel est mon langage de programmation préféré ?", thread_id="alice-001"))
print(chat("Et comment je m'appelle ?", thread_id="alice-001"))

# Conversation 2 — Bob (indépendante d'Alice)
print("\n=== Conversation Bob (thread: bob-001) ===")
print(chat("Bonjour, je suis Bob.", thread_id="bob-001"))
print(chat("Est-ce qu'Alice est dans cette conversation ?", thread_id="bob-001"))
# Bob ne connaît pas Alice — les threads sont isolés
```

Résultat attendu :

```
=== Conversation Alice ===
Bonjour Alice ! Ravi de faire votre connaissance...
Votre langage de programmation préféré est Python !
Vous vous appelez Alice.

=== Conversation Bob ===
Bonjour Bob !
Non, je ne connais pas d'Alice dans notre conversation...
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `memory_saver_demo.py` montrant que Alice se souvient de son nom et de son langage préféré après plusieurs échanges, ET que Bob n'a pas accès aux informations d'Alice (isolation des threads).
> **Expliquer :** Les threads sont comme des "salles de conversation" indépendantes. Le thread_id est la clé d'isolation. En production, ce serait l'ID de l'utilisateur ou de la session. Insister sur le fait que MemorySaver perd tout à l'arrêt du programme — pour de la vraie persistence, utiliser SqliteSaver.

---

## Inspecter l'état d'un checkpoint

```python
# Lire l'état actuel d'un thread
config = {"configurable": {"thread_id": "alice-001"}}
etat_actuel = app.get_state(config)

print("Messages dans le thread alice-001 :")
for msg in etat_actuel.values["messages"]:
    role = "Humain" if isinstance(msg, HumanMessage) else "Assistant"
    print(f"  [{role}]: {msg.content[:80]}")

print(f"\nProchain(s) nœud(s) : {etat_actuel.next}")
print(f"ID du checkpoint : {etat_actuel.config['configurable']['checkpoint_id']}")

# Lister l'historique des checkpoints
print("\nHistorique des checkpoints :")
for checkpoint in app.get_state_history(config):
    print(f"  - {checkpoint.config['configurable']['checkpoint_id']}")
    print(f"    Messages: {len(checkpoint.values.get('messages', []))}")
```

---

## SqliteSaver — Persistence sur disque

`SqliteSaver` persiste les états dans une base SQLite. Les conversations survivent aux redémarrages.

```python
# sqlite_saver_demo.py
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class EtatConversation(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    nom_utilisateur: str
    nb_messages: int

def noeud_chat(etat: EtatConversation) -> dict:
    messages = etat["messages"]
    nb = etat.get("nb_messages", 0)

    systeme = f"""Tu es un assistant qui se souvient de tout.
    Tu parles à {etat.get('nom_utilisateur', 'un utilisateur')}.
    Vous avez échangé {nb} messages jusqu'ici."""

    msgs_avec_systeme = [SystemMessage(content=systeme)] + [
        m for m in messages if not isinstance(m, SystemMessage)
    ]
    reponse = llm.invoke(msgs_avec_systeme)
    return {
        "messages": [reponse],
        "nb_messages": nb + 1
    }

g = StateGraph(EtatConversation)
g.add_node("chat", noeud_chat)
g.set_entry_point("chat")
g.add_edge("chat", END)

# SqliteSaver — persistence sur disque
# Le fichier est créé automatiquement
DB_PATH = "/tmp/conversations_agents.db"

# Utilisation comme context manager pour fermeture propre
with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
    app = g.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "user-alice-permanent"}}
    etat_initial = {
        "messages": [],
        "nom_utilisateur": "Alice",
        "nb_messages": 0
    }

    # Première session
    print("=== SESSION 1 ===")
    r1 = app.invoke(
        {**etat_initial, "messages": [HumanMessage(content="Bonjour ! Je m'appelle Alice.")]},
        config=config
    )
    print(f"Réponse: {r1['messages'][-1].content[:100]}")
    print(f"Nb messages: {r1['nb_messages']}")

    r2 = app.invoke(
        {"messages": [HumanMessage(content="Mon film préféré est Inception.")]},
        config=config
    )
    print(f"Réponse: {r2['messages'][-1].content[:100]}")

print("\n[Programme redémarré - nouvelle instance SqliteSaver]")
print("=== SESSION 2 — Reprise depuis le disque ===")

# Nouvelle instance de SqliteSaver — relit depuis le même fichier
with SqliteSaver.from_conn_string(DB_PATH) as checkpointer2:
    app2 = g.compile(checkpointer=checkpointer2)

    config = {"configurable": {"thread_id": "user-alice-permanent"}}

    # Alice reprend la conversation — le graphe relit l'état depuis SQLite
    r3 = app2.invoke(
        {"messages": [HumanMessage(content="Quel est mon film préféré ?")]},
        config=config
    )
    print(f"Réponse: {r3['messages'][-1].content}")
    print(f"Nb messages cumulés: {r3['nb_messages']}")
```

---

## Reprendre après une interruption

Combiner persistence + interruption est le pattern le plus puissant :

```python
# reprise_interruption.py
import os
from typing import TypedDict, Annotated
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

# Outil avec effet de bord critique — nécessite approbation
@tool
def envoyer_email(destinataire: str, sujet: str, corps: str) -> str:
    """Envoie un email. ATTENTION : action irréversible.
    Args:
        destinataire: Adresse email du destinataire
        sujet: Sujet de l'email
        corps: Corps de l'email
    """
    print(f"\n[EMAIL ENVOYÉ]")
    print(f"  À: {destinataire}")
    print(f"  Sujet: {sujet}")
    print(f"  Corps: {corps[:100]}...")
    return f"Email envoyé à {destinataire} avec succès."

@tool
def supprimer_fichier(chemin: str) -> str:
    """Supprime un fichier. ATTENTION : action irréversible.
    Args:
        chemin: Chemin complet du fichier à supprimer
    """
    print(f"\n[FICHIER SUPPRIMÉ] {chemin}")
    return f"Fichier {chemin} supprimé."

outils_critiques = [envoyer_email, supprimer_fichier]
llm_avec_outils = llm.bind_tools(outils_critiques)

class EtatAvecApprobation(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    action_approuvee: bool

def agent(etat: EtatAvecApprobation) -> dict:
    reponse = llm_avec_outils.invoke(etat["messages"])
    return {"messages": [reponse]}

def routeur(etat: EtatAvecApprobation) -> str:
    dernier = etat["messages"][-1]
    if hasattr(dernier, "tool_calls") and dernier.tool_calls:
        return "outils"
    return END

g = StateGraph(EtatAvecApprobation)
g.add_node("agent", agent)
g.add_node("outils", ToolNode(outils_critiques))
g.set_entry_point("agent")
g.add_conditional_edges("agent", routeur, {"outils": "outils", END: END})
g.add_edge("outils", "agent")

checkpointer = MemorySaver()
app = g.compile(
    checkpointer=checkpointer,
    interrupt_before=["outils"]  # PAUSE avant tout appel d'outil
)

# --- WORKFLOW D'APPROBATION ---
def executer_avec_approbation(demande: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    etat_initial = {
        "messages": [HumanMessage(content=demande)],
        "action_approuvee": False
    }

    print(f"\n{'='*60}")
    print(f"DEMANDE : {demande}")
    print(f"{'='*60}")

    # Étape 1 : Le LLM décide quoi faire
    etat = None
    for event in app.stream(etat_initial, config, stream_mode="values"):
        etat = event

    # Vérifier si on est en attente
    etat_pause = app.get_state(config)
    if not etat_pause.next:
        print("Tâche terminée sans appel d'outil.")
        return etat["messages"][-1].content

    # Étape 2 : Afficher les actions planifiées
    dernier_message = etat["messages"][-1]
    print(f"\n[EN ATTENTE D'APPROBATION]")
    print("L'agent souhaite effectuer les actions suivantes :")
    for i, tc in enumerate(dernier_message.tool_calls, 1):
        print(f"  {i}. {tc['name']}({tc['args']})")

    # Étape 3 : Demander approbation
    print(f"\nProchains nœuds : {etat_pause.next}")
    reponse = input("\nApprouver ces actions ? (oui/non/modifier) : ").strip().lower()

    if reponse == "non":
        print("Actions annulées.")
        # Injecter un message d'annulation
        app.update_state(
            config,
            {"messages": [HumanMessage(content="L'utilisateur a refusé. Dis-lui poliment que tu n'as pas pu effectuer l'action.")]},
            as_node="agent"  # Reprendre depuis le nœud agent, pas outils
        )
        # Forcer la fin en sautant "outils"
        for event in app.stream(None, config, stream_mode="values"):
            etat_final = event
        return etat_final["messages"][-1].content

    elif reponse == "modifier":
        nouveau_contexte = input("Nouvelle instruction : ").strip()
        app.update_state(
            config,
            {"messages": [HumanMessage(content=nouveau_contexte)]},
        )
        print("Instruction mise à jour, reprise...")

    # Étape 4 : Reprendre l'exécution (approuvé ou modifié)
    print("\n[Reprise de l'exécution...]")
    etat_final = None
    for event in app.stream(None, config, stream_mode="values"):
        etat_final = event
        dernier = event["messages"][-1]
        if isinstance(dernier, ToolMessage):
            print(f"[OUTIL] {dernier.name}: {dernier.content[:100]}")

    if etat_final:
        reponse_finale = etat_final["messages"][-1]
        if isinstance(reponse_finale, AIMessage):
            print(f"\n[RÉPONSE FINALE]\n{reponse_finale.content}")
            return reponse_finale.content

    return "Exécution terminée."


# Tester
if __name__ == "__main__":
    executer_avec_approbation(
        "Envoie un email à alice@example.com avec le sujet 'Rapport mensuel' "
        "et comme corps 'Bonjour, veuillez trouver ci-joint le rapport du mois.'",
        thread_id="approbation-test-001"
    )
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'interaction complète de `reprise_interruption.py` : la demande initiale, la pause "EN ATTENTE D'APPROBATION" avec les détails de l'action planifiée, l'invite interactive, puis l'exécution de l'email après approbation.
> **Expliquer :** Ce pattern est essentiel pour les agents en production. Aucun agent ne devrait pouvoir envoyer des emails, supprimer des données ou faire des achats sans une approbation humaine. LangGraph est le seul framework qui rend cette interruption aussi naturelle.

---

## Revenir en arrière dans l'historique

LangGraph permet de "rembobiner" une conversation vers un checkpoint précédent :

```python
# time_travel.py

# Récupérer l'historique des checkpoints
config = {"configurable": {"thread_id": "alice-001"}}
historique = list(app.get_state_history(config))

print(f"Nombre de checkpoints : {len(historique)}")
for i, checkpoint in enumerate(historique):
    nb_messages = len(checkpoint.values.get("messages", []))
    print(f"  [{i}] Checkpoint {checkpoint.config['configurable']['checkpoint_id'][:8]}... — {nb_messages} messages")

# Reprendre depuis un checkpoint précédent (time travel)
ancien_checkpoint = historique[2]  # 3ème checkpoint en partant du plus récent
config_ancien = ancien_checkpoint.config

print(f"\nReprise depuis le checkpoint [{2}]...")
print(f"Messages à ce moment : {len(ancien_checkpoint.values.get('messages', []))}")

# Continuer depuis cet ancien état
for event in app.stream(
    {"messages": [HumanMessage(content="Rappelle-moi notre première conversation.")]},
    config_ancien,
    stream_mode="values"
):
    dernier = event["messages"][-1]
    if isinstance(dernier, AIMessage):
        print(f"Réponse depuis l'ancien checkpoint : {dernier.content[:200]}")
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution du time travel — afficher la liste des checkpoints avec leur ID et leur nombre de messages, puis montrer que la réponse obtenue depuis l'ancien checkpoint ne "connaît pas" les messages ajoutés après ce checkpoint.
> **Expliquer :** Le time travel est unique à LangGraph parmi les frameworks d'agents. C'est une feature critique pour le débogage de production : si un agent fait une mauvaise décision à l'étape 5, vous pouvez revenir à l'étape 4 et reprendre avec des instructions différentes. Comparer avec un système sans checkpoint où il faudrait tout rejouer depuis le début.

---

## Choisir le bon checkpointer

| Checkpointer | Usage | Avantages | Inconvénients |
|---|---|---|---|
| `MemorySaver` | Dev, tests | Simple, rapide | Perdu au redémarrage |
| `SqliteSaver` | Prod légère | Fichier unique, facile | Non scalable |
| `PostgresSaver` | Prod scalable | Robuste, partageable | Dépendance infra |
| `RedisSaver` | Haute dispo | Très rapide | Données volatiles si non configuré |

Installation pour PostgreSQL :

```bash
pip install langgraph-checkpoint-postgres
```

```python
from langgraph.checkpoint.postgres import PostgresSaver

POSTGRES_URI = "postgresql://user:password@localhost:5432/agents_db"

with PostgresSaver.from_conn_string(POSTGRES_URI) as checkpointer:
    checkpointer.setup()  # Crée les tables nécessaires
    app = graphe.compile(checkpointer=checkpointer)
    # ...
```

---

## Patterns avancés de persistence

### Session avec timeout automatique

```python
from datetime import datetime, timedelta

class EtatAvecExpiration(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    derniere_activite: str  # ISO format
    session_expiree: bool

def verifier_expiration(etat: EtatAvecExpiration) -> dict:
    """Vérifie si la session a expiré (inactivité > 30 minutes)."""
    derniere = etat.get("derniere_activite")
    if derniere:
        delta = datetime.now() - datetime.fromisoformat(derniere)
        if delta > timedelta(minutes=30):
            return {"session_expiree": True}
    return {
        "derniere_activite": datetime.now().isoformat(),
        "session_expiree": False
    }
```

### Résumé automatique pour longues conversations

```python
def compresser_historique(etat: EtatConversation) -> dict:
    """Compresse les vieux messages en un résumé pour économiser des tokens."""
    messages = etat["messages"]

    # Si moins de 10 messages, pas besoin de compresser
    if len(messages) <= 10:
        return {}

    # Résumer les messages anciens
    anciens_messages = messages[:-5]  # Garder les 5 derniers intacts
    prompt = f"Résume ces {len(anciens_messages)} messages en 3 phrases : {anciens_messages}"
    resume = llm.invoke([HumanMessage(content=prompt)]).content

    # Remplacer les anciens messages par le résumé
    nouveau_debut = [SystemMessage(content=f"Résumé des échanges précédents : {resume}")]
    messages_compresses = nouveau_debut + messages[-5:]

    return {"messages": messages_compresses}
```

---

## Points clés à retenir

1. Sans checkpointer : chaque `invoke()` repart de zéro — **pas de mémoire**
2. Avec checkpointer : l'état est sauvegardé après **chaque nœud**
3. Le `thread_id` est la **clé d'isolation** entre conversations
4. `MemorySaver` pour le **dev**, `SqliteSaver` ou `PostgresSaver` pour la **prod**
5. `get_state(config)` lit l'état actuel, `get_state_history(config)` liste tous les checkpoints
6. `update_state(config, ...)` modifie l'état **avant** de reprendre l'exécution
7. Passer `None` à `stream()` reprend depuis le **dernier checkpoint** du thread

---

## Suite

Vous avez terminé le module LangGraph ! Passez à `CrewAI/01-introduction.md` pour découvrir une approche radicalement différente : les équipes d'agents role-based.
