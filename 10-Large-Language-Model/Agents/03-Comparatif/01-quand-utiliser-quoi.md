# Comparatif — LangGraph vs CrewAI vs AutoGen

## Objectifs

- Comprendre les philosophies de design de chaque framework
- Identifier les critères de choix selon le cas d'usage
- Appliquer un arbre de décision structuré
- Connaître les patterns d'intégration entre frameworks

---

## Vue d'ensemble des paradigmes

Chaque framework répond à une question fondamentale différente :

```
LangGraph  : "Comment contrôler précisément le flux d'un agent ?"
CrewAI     : "Comment faire collaborer des agents spécialisés comme une équipe ?"
AutoGen    : "Comment faire dialoguer des agents entre eux librement ?"
```

Ces questions ne sont pas concurrentes — elles reflètent des besoins différents.

---

## Tableau comparatif détaillé

| Critère | LangGraph | CrewAI | AutoGen |
|---------|-----------|--------|---------|
| **Paradigme** | Graphe d'état | Équipe role-based | Conversation multi-agents |
| **Abstraction** | Bas niveau | Haut niveau | Moyen niveau |
| **Courbe apprentissage** | Élevée | Faible | Moyenne |
| **Contrôle du flux** | Total | Limité | Moyen |
| **Débogage** | Excellent (LangSmith) | Bon | Bon |
| **Human-in-the-loop** | Natif (interrupt_before) | Possible (moins élégant) | Natif |
| **Persistence** | Natif (checkpointers) | Limité | Limité |
| **Parallélisme** | Natif | Via Flows | Limité |
| **Rôles d'agents** | Manuel | Natif (role/goal/backstory) | Manuel |
| **Outils** | @tool + ToolNode | crewai-tools + @tool | Module tools |
| **Observabilité** | LangSmith intégré | Callbacks | Logs basiques |
| **Tests unitaires** | Simple (fonctions Python) | Plus complexe | Complexe |
| **Production-ready** | Très mature | Mature | Mature |
| **Prototypage rapide** | Moyen | Excellent | Bon |
| **Multi-LLM** | Simple | Simple | Simple |
| **Coût tokens** | Optimisable finement | Moins granulaire | Optimisable |

---

## LangGraph en détail

### Forces

**1. Contrôle total du flux**

```python
# LangGraph : vous définissez précisément chaque transition
graphe.add_conditional_edges(
    "agent",
    lambda etat: "outils" if etat["messages"][-1].tool_calls else END,
    {"outils": "outils", END: END}
)
# Rien n'est implicite — tout est explicitement programmé
```

**2. Human-in-the-loop natif**

```python
app = graphe.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["action_critique"]  # Pause pour validation humaine
)
# Reprise transparente depuis le même état
app.stream(None, config)
```

**3. Time travel et débogage**

```python
# Rembobiner jusqu'à un checkpoint précédent
historique = list(app.get_state_history(config))
app.stream(nouveau_message, historique[3].config)  # Reprendre depuis l'étape 3
```

**4. Observabilité avec LangSmith**

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls__...
# Chaque run est automatiquement tracé sur app.smith.langchain.com
```

### Faiblesses

- Verbose : beaucoup de code pour des cas simples
- Pas de concept de "rôle" — à implémenter manuellement
- La gestion des outils nécessite du câblage explicite

### Cas d'usage idéaux

```
✓ Agent de support client avec escalade humaine
✓ Pipeline de vérification de conformité avec approbation
✓ Workflow de génération de code avec test automatique
✓ Agent financier avec validation avant exécution d'ordres
✓ Système de RAG avec boucle de reformulation
✓ Chatbot avec mémoire persistante multi-session
```

---

## CrewAI en détail

### Forces

**1. Démarrage ultra-rapide**

```python
# 10 lignes suffisent pour une équipe fonctionnelle
from crewai import Agent, Task, Crew, Process

crew = Crew(
    agents=[Agent(role="...", goal="...", backstory="...")],
    tasks=[Task(description="...", expected_output="...", agent=...)],
    process=Process.sequential
).kickoff()
```

**2. Collaboration naturelle via roles**

```python
# Le rôle/backstory guide le comportement sans code supplémentaire
directeur = Agent(
    role="Directeur Marketing",
    goal="Maximiser l'impact des campagnes marketing",
    backstory="20 ans dans le marketing digital, expert ROI et conversion.",
    allow_delegation=True  # Peut déléguer à l'équipe
)
```

**3. Sorties structurées**

```python
# Garantir un format JSON valide automatiquement
tache = Task(output_pydantic=MonModele, ...)
resultat.pydantic  # Instance Pydantic directement utilisable
```

**4. Flows pour l'orchestration**

```python
class MonFlow(Flow[EtatFlow]):
    @start()
    def classifier(self): ...

    @router(classifier)
    def router(self, type) -> str: return type

    @listen("type_a")
    def traiter_a(self): ...
```

### Faiblesses

- Moins de contrôle sur le flux entre agents
- La délégation implicite peut créer des comportements imprévisibles
- Debugging plus difficile sans LangSmith
- `Process.hierarchical` peut être coûteux et moins prévisible

### Cas d'usage idéaux

```
✓ Pipeline de création de contenu (recherche → rédaction → révision)
✓ Analyse multi-facettes (marché + client + technique → synthèse)
✓ Système de génération de rapports avec rôles métier clairs
✓ Équipe de code review (reviewer sécurité + reviewer qualité + tech lead)
✓ Pipeline SEO (recherche mots-clés → brief → rédaction → optimisation)
✓ Analyse de CV et matching candidat/poste
```

---

## AutoGen en détail

AutoGen (Microsoft) n'est pas couvert en profondeur dans ce module, mais voici les éléments clés pour la comparaison :

### Concept fondateur

AutoGen modélise les agents comme des **participants à une conversation**. Chaque agent peut :
- Initier des messages
- Répondre à des messages d'autres agents
- Exécuter du code
- S'arrêter selon une condition de terminaison

```python
# AutoGen — exemple simplifié
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="assistant",
    system_message="Tu es un assistant IA utile.",
    llm_config={"model": "gpt-4o-mini"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # Ou "ALWAYS" pour human-in-the-loop
    code_execution_config={"work_dir": "/tmp"}  # Exécution de code !
)

# Démarrer la conversation
user_proxy.initiate_chat(
    assistant,
    message="Écris un script Python qui trie une liste de nombres."
)
```

### Forces AutoGen

- Exécution de code native (analyse de données, tests)
- Conversation très naturelle entre agents
- GroupChat pour plusieurs agents simultanés
- Intégration avec Docker pour sandboxing

### Faiblesses AutoGen

- Moins de contrôle sur le flux que LangGraph
- Pas de concept de "tâche" structurée comme CrewAI
- Convergence moins garantie (la conversation peut dériver)

### Cas d'usage idéaux AutoGen

```
✓ Génération et test de code automatique
✓ Résolution de problèmes par dialogue entre experts simulés
✓ Agent d'analyse de données avec exécution Python
✓ Pair-programming automatisé (développeur + reviewer)
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Côte à côte (deux terminaux ou split-screen) : la même question posée à un agent LangGraph (verbose, montrant le graphe d'exécution) et à un crew CrewAI (verbose, montrant le raisonnement role-based). La question : "Analyse le marché de l'IA en 3 points."
> **Expliquer :** LangGraph montre des nœuds, des états, des transitions. CrewAI montre des agents avec des rôles, des thoughts, des actions. Ce sont deux façons radicalement différentes de penser le même problème. LangGraph = programmeur qui modélise un automate. CrewAI = manager qui constitue une équipe.

---

## Arbre de décision

```
Mon cas d'usage nécessite-t-il :
│
├── Du code qui s'exécute automatiquement ?
│   └── OUI → AutoGen (code execution natif)
│
├── Des rôles métier clairs (chercheur, analyste, rédacteur...) ?
│   ├── OUI + Pipeline séquentiel ou hiérarchique → CrewAI
│   └── OUI + Flux complexe/conditionnel → LangGraph + agents spécialisés
│
├── Un contrôle précis du flux ?
│   └── OUI → LangGraph
│
├── Une validation humaine en cours d'exécution ?
│   └── OUI → LangGraph (interrupt_before)
│
├── Une mémoire persistante entre sessions ?
│   └── OUI → LangGraph (checkpointers)
│
├── Un prototypage rapide (poc, démo) ?
│   └── OUI → CrewAI (moins de code)
│
├── Une orchestration de plusieurs Crews avec logique Python ?
│   └── OUI → CrewAI Flows
│
└── Difficile à décomposer en rôles ou en graphe ?
    └── Revisiter le besoin — décomposer le problème différemment
```

---

## Comparaison par type de projet

### Projet 1 : Assistant de support client

```
Besoin :
- Répondre aux questions clients
- Escalader vers un humain si nécessaire
- Mémoriser les préférences et historique
- Consulter une base de connaissances

→ LANGGRAPH : interrupt_before pour l'escalade, MemorySaver/SqliteSaver
  pour la mémoire, RAG via outils
```

```python
# Squelette LangGraph pour support client
class EtatSupport(TypedDict):
    messages: Annotated[list, add_messages]
    besoin_escalade: bool
    ticket_id: str

def agent_support(etat): ...
def evaluer_escalade(etat): ...  # Logique : score de frustration, mots-clés
def notifier_humain(etat): ...

g = StateGraph(EtatSupport)
g.add_node("agent", agent_support)
g.add_node("evaluer", evaluer_escalade)
g.add_node("escalade", notifier_humain)
app = g.compile(
    checkpointer=SqliteSaver.from_conn_string("support.db"),
    interrupt_before=["escalade"]
)
```

---

### Projet 2 : Production de newsletter hebdomadaire

```
Besoin :
- Collecter les actualités de la semaine
- Synthétiser par thème
- Rédiger les sections
- Réviser et formater
- Envoyer par email

→ CREWAI : pipeline séquentiel naturel avec rôles bien définis
```

```python
# Squelette CrewAI pour newsletter
veilleur = Agent(role="Veilleur d'actualités", ...)
synthétiseur = Agent(role="Synthétiseur thématique", ...)
redacteur = Agent(role="Rédacteur newsletter", ...)
reviseur = Agent(role="Réviseur", ...)

crew_newsletter = Crew(
    agents=[veilleur, synthétiseur, redacteur, reviseur],
    tasks=[t1_veille, t2_synthese, t3_redaction, t4_revision],
    process=Process.sequential
)
```

---

### Projet 3 : Analyse de données exploratoire

```
Besoin :
- Charger un CSV
- Comprendre la structure
- Générer et exécuter du code Python d'analyse
- Interpréter les résultats
- Suggérer des visualisations

→ AUTOGEN : code execution natif, dialogue naturel pour l'exploration
```

---

### Projet 4 : Workflow de validation de contrats

```
Besoin :
- Extraire les clauses d'un contrat PDF
- Vérifier la conformité juridique
- Identifier les risques
- Proposer des modifications
- Obtenir une validation humaine avant envoi

→ LANGGRAPH : PDFSearchTool + interrupt_before + checkpointer
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La trace LangSmith d'une exécution LangGraph (nécessite `LANGCHAIN_TRACING_V2=true`) montrant le graphe d'exécution avec les durées par nœud, les tokens utilisés, et les inputs/outputs de chaque nœud. Comparer avec les logs verbose de CrewAI qui montrent le raisonnement textuel des agents.
> **Expliquer :** LangSmith offre une observabilité que CrewAI n'a pas nativement. En production, pour déboguer "pourquoi l'agent a fait X au lieu de Y", LangSmith permet de remonter à l'exact moment de la décision, voir le prompt complet, les tokens utilisés, et le raisonnement. Pointer que cette observabilité est une raison majeure de choisir LangGraph pour les applications critiques.

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le tableau de comparaison de coûts tokens entre un agent LangGraph simple (2 000 tokens) et un Crew CrewAI 3 agents (12 000 tokens) pour la même question. Utiliser `resultat.token_usage.total_tokens` dans CrewAI et les compteurs de callbacks dans LangGraph.
> **Expliquer :** Le coût en tokens est 5-6x plus élevé avec CrewAI multi-agents car chaque agent reçoit un contexte complet incluant les résultats précédents. Ce n'est pas un problème si la qualité justifie le coût — mais il faut en être conscient pour l'estimation des coûts d'exploitation.

---

## Utiliser les deux ensemble

LangGraph et CrewAI peuvent coexister dans le même projet :

```python
# Pattern : CrewAI pour les tâches complexes, LangGraph pour l'orchestration globale

from crewai import Agent, Task, Crew, Process
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool

# Créer un Crew comme un outil LangGraph
@tool("Crew d'Analyse Approfondie")
def lancer_crew_analyse(sujet: str) -> str:
    """Lance une équipe d'agents spécialisés pour analyser un sujet en profondeur.
    Utilise quand l'utilisateur demande une analyse multi-facettes.
    Args:
        sujet: Le sujet à analyser
    """
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini")

    analyste = Agent(
        role="Analyste Expert",
        goal="Analyser le sujet en profondeur",
        backstory="Expert polyvalent.",
        llm=llm
    )
    tache = Task(
        description=f"Analyse approfondie de : {sujet}",
        expected_output="Rapport d'analyse complet.",
        agent=analyste
    )
    crew = Crew(agents=[analyste], tasks=[tache], process=Process.sequential, verbose=False)
    return crew.kickoff().raw


# Ce crew devient un outil dans un agent LangGraph
outils = [lancer_crew_analyse, autre_outil]
llm_avec_outils = ChatOpenAI(model="gpt-4o-mini").bind_tools(outils)

# L'agent LangGraph décide quand appeler le crew CrewAI
class EtatHybride(TypedDict):
    messages: Annotated[list, add_messages]

def agent_principal(etat):
    return {"messages": [llm_avec_outils.invoke(etat["messages"])]}

# ...graphe LangGraph classique...
```

---

## Critères de performance et coût

### Estimation du coût par requête

```
LangGraph (agent simple, 3 tours) :
- Tokens : ~2 000 - 5 000 tokens
- Coût GPT-4o-mini : ~$0.001 - $0.003

CrewAI (crew 3 agents, process.sequential) :
- Tokens : ~8 000 - 20 000 tokens (chaque agent a son contexte)
- Coût GPT-4o-mini : ~$0.004 - $0.010

AutoGen (5 tours de conversation) :
- Tokens : ~5 000 - 15 000 tokens
- Coût GPT-4o-mini : ~$0.002 - $0.008
```

### Conseils d'optimisation

```python
# CrewAI — utiliser gpt-4o-mini pour les agents non-critiques
agent_redacteur = Agent(
    role="...",
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # Moins cher
)

# Manager hiérarchique CrewAI — utiliser gpt-4o (plus de raisonnement)
crew = Crew(..., manager_llm=ChatOpenAI(model="gpt-4o"))

# LangGraph — contrôler max_iterations pour éviter les boucles infinies
MAX_ITER = 5
def routeur(etat):
    if etat.get("iterations", 0) >= MAX_ITER:
        return END
    ...
```

---

## Points clés à retenir

1. **LangGraph** = contrôle maximal, verbeux, production-grade — pour les workflows complexes, sensibles et avec human-in-the-loop
2. **CrewAI** = abstraction naturelle, rapide à démarrer — pour les pipelines avec rôles métier clairs
3. **AutoGen** = dialogue naturel, exécution de code — pour les tâches exploratoires et la génération de code
4. Les frameworks sont **complémentaires** — un Crew CrewAI peut être un outil dans LangGraph
5. Toujours estimer le **coût en tokens** avant de choisir le nombre d'agents
6. Pour un **PoC** : commencer par CrewAI ; pour la **prod** : migrer vers LangGraph si le contrôle manque

---

## Suite

Passez aux exercices pratiques :
- `exercices/exercice-01-agent-recherche.md` : Agent de recherche avec LangGraph
- `exercices/exercice-02-crew-analyse.md` : Crew d'analyse de marché avec CrewAI
