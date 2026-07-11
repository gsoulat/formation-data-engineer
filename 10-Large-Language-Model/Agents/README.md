# Frameworks Multi-Agents — Vue d'ensemble

## Objectifs du module

Ce module couvre les principaux frameworks de construction d'agents IA en Python. À l'issue de cette formation, vous serez capable de :

- Comprendre ce qu'est un agent IA et en quoi il diffère d'un simple appel LLM
- Construire des agents avec **LangGraph** (contrôle fin, graphes d'état)
- Construire des équipes d'agents avec **CrewAI** (collaboration role-based)
- Choisir le bon framework en fonction du besoin

---

## Qu'est-ce qu'un agent IA ?

Un agent IA est un système capable de :

1. **Percevoir** un contexte (message utilisateur, résultat d'outil, état courant)
2. **Raisonner** sur ce contexte via un LLM
3. **Agir** en appelant des outils, des APIs, ou d'autres agents
4. **Boucler** jusqu'à atteindre un objectif

La différence fondamentale avec un simple appel LLM :

```
LLM simple :    Input → LLM → Output         (une passe)
Agent :         Input → LLM → Action → Observation → LLM → ... → Output  (boucle)
```

Le pattern de raisonnement le plus courant est **ReAct** (Reasoning + Acting) :

```
Thought: Je dois chercher des informations sur X
Action: search("X")
Observation: [résultats]
Thought: J'ai assez d'informations, je peux répondre
Answer: ...
```

---

## Les frameworks couverts

### LangGraph

**Développeur** : LangChain Inc.
**Paradigme** : Graphes d'état dirigés
**Point fort** : Contrôle total sur le flux d'exécution

LangGraph modélise un agent comme un **graphe** où :
- Les **nœuds** sont des fonctions (appels LLM, outils, logique)
- Les **arêtes** sont des transitions entre états
- L'**état** est un dictionnaire partagé entre tous les nœuds

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list
    step: int

graph = StateGraph(AgentState)
graph.add_node("reason", reason_node)
graph.add_node("act", act_node)
graph.add_edge("reason", "act")
graph.add_conditional_edges("act", should_continue, {"continue": "reason", "end": END})
```

**Quand utiliser LangGraph** :
- Workflows complexes avec branchements conditionnels
- Human-in-the-loop requis
- Débogage et observabilité critique
- Multi-agents avec communication fine

---

### CrewAI

**Développeur** : CrewAI Inc.
**Paradigme** : Équipes d'agents avec rôles
**Point fort** : Simplicité et collaboration naturelle

CrewAI modélise le problème comme une **équipe** où :
- Les **Agents** ont un rôle, un objectif et un background
- Les **Tasks** sont des missions assignées aux agents
- Le **Crew** orchestre l'exécution

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="Chercheur",
    goal="Trouver des informations précises sur le sujet",
    backstory="Expert en recherche documentaire avec 10 ans d'expérience",
    tools=[search_tool]
)

task = Task(
    description="Recherche les dernières tendances en IA générative",
    expected_output="Rapport de 3 paragraphes avec sources",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential)
result = crew.kickoff()
```

**Quand utiliser CrewAI** :
- Décomposition naturelle en rôles humains
- Pipelines séquentiels ou hiérarchiques
- Prototypage rapide
- Équipes d'agents spécialisés

---

### AutoGen (référence comparative)

**Développeur** : Microsoft
**Paradigme** : Conversations multi-agents
**Point fort** : Dialogues agent-à-agent très flexibles

AutoGen n'est pas couvert en détail dans ce module mais apparaît dans le comparatif. Il se distingue par son modèle de **conversation** entre agents, où chaque agent peut initier ou répondre à des messages d'autres agents.

---

## Tableau comparatif rapide

| Critère | LangGraph | CrewAI | AutoGen |
|---------|-----------|--------|---------|
| Paradigme | Graphe d'état | Équipe role-based | Conversation |
| Courbe d'apprentissage | Élevée | Faible | Moyenne |
| Contrôle du flux | Total | Limité | Moyen |
| Human-in-the-loop | Natif | Possible | Natif |
| Observabilité | Excellente (LangSmith) | Bonne | Bonne |
| Cas d'usage | Workflows complexes | Équipes spécialisées | Dialogues collaboratifs |
| Maturité | Très mature | Mature | Mature |
| Communauté | Grande | Croissante | Grande |

---

## Prérequis techniques

Avant de commencer, vous devez avoir :

```bash
# Python 3.11+
python --version

# Installer les dépendances
pip install langgraph langchain langchain-openai
pip install crewai crewai-tools
pip install python-dotenv

# Variables d'environnement
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."    # Pour la recherche web
export LANGCHAIN_API_KEY="ls__..."  # Pour LangSmith (optionnel)
export LANGCHAIN_TRACING_V2="true"  # Activer le tracing
```

Fichier `.env` recommandé :

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=formation-agents
```

---

## Structure du module

```
Agents/
├── README.md                          ← Ce fichier
├── LangGraph/
│   ├── 01-introduction.md             ← Concepts fondamentaux
│   ├── 02-state-nodes-edges.md        ← Construction d'un graphe
│   ├── 03-agent-reactif.md            ← Agent ReAct complet
│   ├── 04-multi-agents.md             ← Supervision et sous-graphes
│   └── 05-persistence.md             ← Mémoire et reprise
├── CrewAI/
│   ├── 01-introduction.md             ← Concepts CrewAI
│   ├── 02-agents-tasks.md             ← Définir agents et tâches
│   ├── 03-tools.md                    ← Outils intégrés et custom
│   ├── 04-processus.md                ← Sequential vs Hierarchical
│   └── 05-flows.md                    ← CrewAI Flows
├── Comparatif/
│   └── 01-quand-utiliser-quoi.md      ← Guide de décision
└── exercices/
    ├── exercice-01-agent-recherche.md ← LangGraph : agent de recherche
    └── exercice-02-crew-analyse.md    ← CrewAI : analyse de marché
```

---

## Ordre de lecture recommandé

Pour une première découverte :

1. Ce README
2. `LangGraph/01-introduction.md`
3. `LangGraph/02-state-nodes-edges.md`
4. `LangGraph/03-agent-reactif.md`
5. `CrewAI/01-introduction.md`
6. `CrewAI/02-agents-tasks.md`
7. `Comparatif/01-quand-utiliser-quoi.md`
8. Exercices

Pour une expérience avancée, lire tous les fichiers dans l'ordre puis faire les exercices.

---

## Ressources externes

- [Documentation LangGraph](https://langchain-ai.github.io/langgraph/)
- [Documentation CrewAI](https://docs.crewai.com/)
- [LangSmith](https://smith.langchain.com/) — observabilité LangChain/LangGraph
- [ReAct Paper](https://arxiv.org/abs/2210.03629) — le pattern de raisonnement fondateur
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
