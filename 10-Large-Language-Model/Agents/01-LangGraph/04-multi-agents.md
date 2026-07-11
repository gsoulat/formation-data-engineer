# LangGraph — Multi-Agents

## Objectifs

- Comprendre le besoin d'architectures multi-agents
- Implémenter le pattern Superviseur
- Créer des sous-graphes (subgraphs) pour modulariser les agents
- Gérer la communication entre agents
- Construire un système avec délégation dynamique

---

## Pourquoi des multi-agents ?

Un agent unique a des limites :

1. **Fenêtre de contexte** : trop d'informations dans un seul contexte dégradent la performance
2. **Spécialisation** : un agent généraliste est moins efficace qu'un expert dans son domaine
3. **Parallélisme** : des tâches indépendantes peuvent s'exécuter simultanément
4. **Modularité** : des agents spécialisés sont plus faciles à tester et maintenir

La solution : décomposer le problème en **agents spécialisés** orchestrés par un **superviseur**.

---

## Architecture Superviseur

Le pattern superviseur est le plus courant pour les multi-agents :

```
                    ┌──────────────┐
                    │  SUPERVISEUR │
                    │    (LLM)     │
                    └──┬───────────┘
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Agent   │  │ Agent   │  │ Agent   │
   │Chercheur│  │Analyste │  │Rédacteur│
   └─────────┘  └─────────┘  └─────────┘
```

Le superviseur :
1. Reçoit la demande initiale
2. Décide quel agent appeler
3. Transmet les résultats entre agents
4. Détermine quand la tâche est terminée

---

## Implémentation du Superviseur

```python
# superviseur.py
import os
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# DÉFINITION DES AGENTS SPÉCIALISÉS
# ============================================================

def creer_agent_chercheur():
    """Crée un agent spécialisé dans la recherche d'informations."""

    @tool
    def rechercher(requete: str) -> str:
        """Recherche des informations sur un sujet. Args: requete (str)"""
        # Simulation de recherche
        resultats = {
            "ia": "L'IA générative en 2024 : GPT-4, Claude 3, Gemini Ultra. Marché valorisé à 200Md$ en 2025.",
            "cloud": "AWS domine avec 32% de parts, Azure 23%, GCP 11%. Croissance annuelle 20%.",
        }
        for cle, val in resultats.items():
            if cle in requete.lower():
                return val
        return f"Recherche sur '{requete}' : données de marché disponibles, tendance haussière confirmée."

    outils_chercheur = [rechercher]
    llm_chercheur = llm.bind_tools(outils_chercheur)

    class EtatChercheur(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

    def noeud_llm(etat):
        return {"messages": [llm_chercheur.invoke(etat["messages"])]}

    g = StateGraph(EtatChercheur)
    g.add_node("llm", noeud_llm)
    g.add_node("outils", ToolNode(outils_chercheur))
    g.set_entry_point("llm")

    def routeur(etat):
        dernier = etat["messages"][-1]
        if hasattr(dernier, "tool_calls") and dernier.tool_calls:
            return "outils"
        return END

    g.add_conditional_edges("llm", routeur, {"outils": "outils", END: END})
    g.add_edge("outils", "llm")

    return g.compile()


def creer_agent_analyste():
    """Crée un agent spécialisé dans l'analyse et les statistiques."""

    @tool
    def analyser_donnees(donnees: str) -> str:
        """Analyse des données et produit des insights. Args: donnees (str)"""
        return f"""Analyse de : {donnees}
        - Tendance : Croissance soutenue (+15% YoY)
        - Points forts : Innovation technologique, adoption enterprise
        - Risques : Régulation incertaine, consolidation du marché
        - Score attractivité : 8.2/10"""

    @tool
    def calculer_projections(base: str, taux_croissance: float = 0.15) -> str:
        """Calcule des projections financières. Args: base, taux_croissance"""
        try:
            valeur_base = float(''.join(c for c in base if c.isdigit() or c == '.'))
            proj_1an = valeur_base * (1 + taux_croissance)
            proj_3ans = valeur_base * ((1 + taux_croissance) ** 3)
            return f"Base: {valeur_base}Md$ | +1an: {proj_1an:.1f}Md$ | +3ans: {proj_3ans:.1f}Md$"
        except Exception:
            return "Impossible de calculer les projections sans données chiffrées."

    outils_analyste = [analyser_donnees, calculer_projections]
    llm_analyste = llm.bind_tools(outils_analyste)

    class EtatAnalyste(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

    def noeud_llm(etat):
        return {"messages": [llm_analyste.invoke(etat["messages"])]}

    g = StateGraph(EtatAnalyste)
    g.add_node("llm", noeud_llm)
    g.add_node("outils", ToolNode(outils_analyste))
    g.set_entry_point("llm")

    def routeur(etat):
        dernier = etat["messages"][-1]
        if hasattr(dernier, "tool_calls") and dernier.tool_calls:
            return "outils"
        return END

    g.add_conditional_edges("llm", routeur, {"outils": "outils", END: END})
    g.add_edge("outils", "llm")

    return g.compile()


def creer_agent_redacteur():
    """Crée un agent spécialisé dans la rédaction de rapports."""

    class EtatRedacteur(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

    systeme = """Tu es un rédacteur professionnel spécialisé dans les rapports d'analyse.
    Quand tu reçois des données de recherche et d'analyse, tu produis un rapport
    structuré, clair et professionnel en français."""

    def noeud_rediger(etat):
        messages = etat["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=systeme)] + messages
        reponse = llm.invoke(messages)
        return {"messages": [reponse]}

    g = StateGraph(EtatRedacteur)
    g.add_node("rediger", noeud_rediger)
    g.set_entry_point("rediger")
    g.add_edge("rediger", END)

    return g.compile()
```

---

## L'état global et le superviseur

```python
# (suite de superviseur.py)

# ============================================================
# ÉTAT GLOBAL DU SYSTÈME MULTI-AGENTS
# ============================================================

MEMBRES = ["chercheur", "analyste", "redacteur"]

class EtatSuperviseur(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    prochain_agent: str          # Quel agent appeler ensuite
    resultats_agents: dict       # Résultats accumulés par agent
    tache_initiale: str          # La demande originale
    iterations: int


# ============================================================
# NŒUD SUPERVISEUR
# ============================================================

PROMPT_SUPERVISEUR = """Tu es un superviseur qui coordonne une équipe d'agents spécialisés.

Équipe disponible :
- chercheur : Recherche des informations factuelles et des données de marché
- analyste : Analyse les données et produit des insights, calcule des projections
- redacteur : Rédige des rapports structurés à partir des informations collectées

Tâche en cours : {tache}

Résultats déjà obtenus :
{resultats}

Décide qui doit travailler ensuite. Réponds avec UNIQUEMENT le nom de l'agent
(chercheur, analyste, ou redacteur) ou "FINI" si le travail est terminé.
Le redacteur doit être le dernier à travailler, après que chercheur et analyste ont fourni leurs résultats."""

def noeud_superviseur(etat: EtatSuperviseur) -> dict:
    """Le superviseur décide qui travaille ensuite."""
    print(f"\n[SUPERVISEUR] Décision en cours...")

    tache = etat.get("tache_initiale", "")
    resultats = etat.get("resultats_agents", {})
    iterations = etat.get("iterations", 0)

    # Formatage des résultats existants
    resultats_str = "\n".join([
        f"- {agent}: {contenu[:200]}..."
        for agent, contenu in resultats.items()
    ]) or "Aucun résultat pour l'instant."

    prompt = PROMPT_SUPERVISEUR.format(
        tache=tache,
        resultats=resultats_str
    )

    reponse = llm.invoke([HumanMessage(content=prompt)])
    prochain = reponse.content.strip().lower()

    print(f"[SUPERVISEUR] → Prochain agent : {prochain}")

    # Validation
    agents_valides = MEMBRES + ["fini"]
    if prochain not in agents_valides:
        prochain = "fini"

    return {
        "prochain_agent": prochain,
        "iterations": iterations + 1
    }


# ============================================================
# NŒUDS POUR CHAQUE AGENT SPÉCIALISÉ
# ============================================================

# Instancier les agents
agent_chercheur = creer_agent_chercheur()
agent_analyste = creer_agent_analyste()
agent_redacteur = creer_agent_redacteur()

def executer_chercheur(etat: EtatSuperviseur) -> dict:
    """Lance le chercheur et récupère son résultat."""
    print(f"  [CHERCHEUR] Démarrage de la recherche...")
    tache = etat["tache_initiale"]

    resultat = agent_chercheur.invoke({
        "messages": [HumanMessage(content=f"Recherche des informations sur : {tache}")]
    })

    dernier_message = resultat["messages"][-1].content
    print(f"  [CHERCHEUR] Terminé : {dernier_message[:100]}...")

    resultats_mis_a_jour = {**etat.get("resultats_agents", {}), "chercheur": dernier_message}

    return {
        "resultats_agents": resultats_mis_a_jour,
        "messages": [AIMessage(content=f"[Chercheur] {dernier_message}")]
    }


def executer_analyste(etat: EtatSuperviseur) -> dict:
    """Lance l'analyste sur les données du chercheur."""
    print(f"  [ANALYSTE] Démarrage de l'analyse...")
    resultats = etat.get("resultats_agents", {})
    donnees_chercheur = resultats.get("chercheur", "Pas de données du chercheur.")

    contexte = f"""Analyse ces informations et produis des insights :
    Données : {donnees_chercheur}
    Tâche originale : {etat['tache_initiale']}"""

    resultat = agent_analyste.invoke({
        "messages": [HumanMessage(content=contexte)]
    })

    dernier_message = resultat["messages"][-1].content
    print(f"  [ANALYSTE] Terminé : {dernier_message[:100]}...")

    resultats_mis_a_jour = {**resultats, "analyste": dernier_message}

    return {
        "resultats_agents": resultats_mis_a_jour,
        "messages": [AIMessage(content=f"[Analyste] {dernier_message}")]
    }


def executer_redacteur(etat: EtatSuperviseur) -> dict:
    """Lance le rédacteur pour produire le rapport final."""
    print(f"  [RÉDACTEUR] Rédaction du rapport...")
    resultats = etat.get("resultats_agents", {})

    contexte = f"""Rédige un rapport professionnel basé sur ces informations :

    RECHERCHE :
    {resultats.get('chercheur', 'Non disponible')}

    ANALYSE :
    {resultats.get('analyste', 'Non disponible')}

    Tâche : {etat['tache_initiale']}

    Format : Introduction, Données clés, Analyse, Conclusion (4 sections max)."""

    resultat = agent_redacteur.invoke({
        "messages": [HumanMessage(content=contexte)]
    })

    rapport = resultat["messages"][-1].content
    print(f"  [RÉDACTEUR] Rapport généré ({len(rapport)} caractères)")

    resultats_mis_a_jour = {**resultats, "redacteur": rapport}

    return {
        "resultats_agents": resultats_mis_a_jour,
        "messages": [AIMessage(content=f"[Rapport Final]\n{rapport}")]
    }


# ============================================================
# GRAPHE PRINCIPAL
# ============================================================

def routeur_superviseur(etat: EtatSuperviseur) -> str:
    """Route vers le prochain agent selon la décision du superviseur."""
    prochain = etat.get("prochain_agent", "fini")
    iterations = etat.get("iterations", 0)

    # Protection anti-boucle
    if iterations >= 6:
        return "fin"

    mapping = {
        "chercheur": "chercheur",
        "analyste": "analyste",
        "redacteur": "redacteur",
        "fini": "fin",
    }
    return mapping.get(prochain, "fin")


g_principal = StateGraph(EtatSuperviseur)

# Nœuds
g_principal.add_node("superviseur", noeud_superviseur)
g_principal.add_node("chercheur", executer_chercheur)
g_principal.add_node("analyste", executer_analyste)
g_principal.add_node("redacteur", executer_redacteur)

# Entrée
g_principal.set_entry_point("superviseur")

# Routing depuis le superviseur
g_principal.add_conditional_edges(
    "superviseur",
    routeur_superviseur,
    {
        "chercheur": "chercheur",
        "analyste": "analyste",
        "redacteur": "redacteur",
        "fin": END
    }
)

# Chaque agent retourne au superviseur
g_principal.add_edge("chercheur", "superviseur")
g_principal.add_edge("analyste", "superviseur")
g_principal.add_edge("redacteur", "superviseur")

app_multi = g_principal.compile()

# Visualiser
print("Architecture multi-agents :")
print(app_multi.get_graph().draw_ascii())
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La représentation ASCII du graphe multi-agents montrant le superviseur au centre avec des flèches vers chaque agent spécialisé et des flèches de retour vers le superviseur.
> **Expliquer :** La visualisation montre clairement le pattern "hub-and-spoke" — le superviseur est le hub central. Insister sur le fait que chaque agent est lui-même un graphe complet (sous-graphe), ce qui permet de les développer et tester indépendamment.

---

```python
# (suite : exécution)

# Exécution du système multi-agents
print("\n" + "="*60)
print("DÉMARRAGE DU SYSTÈME MULTI-AGENTS")
print("="*60)

tache = "Analyse le marché de l'intelligence artificielle générative en 2024"

etat_initial = {
    "messages": [HumanMessage(content=tache)],
    "prochain_agent": "",
    "resultats_agents": {},
    "tache_initiale": tache,
    "iterations": 0
}

for event in app_multi.stream(etat_initial, stream_mode="updates"):
    for noeud, data in event.items():
        if noeud == "superviseur":
            print(f"\n[SUPERVISEUR] Prochain → {data.get('prochain_agent', '?')}")

print("\n" + "="*60)
print("RAPPORT FINAL")
print("="*60)
# Récupérer le rapport final
etat_final = app_multi.invoke(etat_initial)
rapport = etat_final.get("resultats_agents", {}).get("redacteur", "Aucun rapport généré.")
print(rapport)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution complète du système multi-agents dans le terminal, montrant la séquence des décisions du superviseur : `[SUPERVISEUR] → chercheur`, puis `[SUPERVISEUR] → analyste`, puis `[SUPERVISEUR] → redacteur`, puis `[SUPERVISEUR] → fini`. Inclure le rapport final généré.
> **Expliquer :** Montrer que le superviseur prend des décisions différentes à chaque tour selon l'état d'avancement. Si le chercheur a déjà travaillé, le superviseur ne le rappelle pas — il délègue à l'analyste. C'est une forme d'intelligence émergente basée sur le contexte accumulé.

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le flux d'exécution du système multi-agents avec `stream_mode="updates"`, montrant clairement la séquence : `[SUPERVISEUR] → chercheur` → nœud chercheur s'exécute → `[SUPERVISEUR] → analyste` → nœud analyste s'exécute → `[SUPERVISEUR] → redacteur` → nœud rédacteur s'exécute → `[SUPERVISEUR] → fini`. Enchaîner sur le rapport final.
> **Expliquer :** Comparer ce pattern avec un simple appel LLM qui ferait tout en une fois. Ici, chaque agent spécialisé apporte sa contribution dans son domaine d'expertise. Le superviseur ne fait pas le travail — il orchestre. C'est la différence entre un généraliste et une équipe d'experts.

---

## Sous-graphes (Subgraphs)

Les sous-graphes permettent de **réutiliser** et **composer** des graphes complexes :

```python
# subgraph_example.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---- Sous-graphe de validation ----
class EtatValidation(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    contenu_a_valider: str
    est_valide: bool
    raison_invalidite: str

def verifier_longueur(etat: EtatValidation) -> dict:
    contenu = etat["contenu_a_valider"]
    if len(contenu) < 10:
        return {"est_valide": False, "raison_invalidite": "Contenu trop court (< 10 chars)"}
    return {"est_valide": True, "raison_invalidite": ""}

def verifier_qualite(etat: EtatValidation) -> dict:
    if not etat["est_valide"]:
        return {}  # Déjà invalidé
    contenu = etat["contenu_a_valider"]
    mots_interdits = ["spam", "test123", "lorem ipsum"]
    for mot in mots_interdits:
        if mot in contenu.lower():
            return {"est_valide": False, "raison_invalidite": f"Contenu non autorisé : '{mot}'"}
    return {"est_valide": True}

g_validation = StateGraph(EtatValidation)
g_validation.add_node("longueur", verifier_longueur)
g_validation.add_node("qualite", verifier_qualite)
g_validation.set_entry_point("longueur")
g_validation.add_edge("longueur", "qualite")
g_validation.add_edge("qualite", END)

sous_graphe_validation = g_validation.compile()

# ---- Graphe principal utilisant le sous-graphe ----
class EtatPrincipal(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    contenu_a_valider: str   # Clé partagée avec le sous-graphe
    est_valide: bool          # Clé partagée avec le sous-graphe
    raison_invalidite: str    # Clé partagée avec le sous-graphe
    rapport: str

def preparer_contenu(etat: EtatPrincipal) -> dict:
    """Génère du contenu à valider."""
    reponse = llm.invoke([HumanMessage(content="Écris une phrase courte sur l'IA.")])
    return {"contenu_a_valider": reponse.content}

def generer_rapport(etat: EtatPrincipal) -> dict:
    """Génère le rapport final."""
    if etat["est_valide"]:
        rapport = f"Contenu validé ✓\n\n{etat['contenu_a_valider']}"
    else:
        rapport = f"Contenu rejeté ✗\nRaison : {etat['raison_invalidite']}"
    return {"rapport": rapport}

g_principal = StateGraph(EtatPrincipal)
g_principal.add_node("preparer", preparer_contenu)

# Ajouter le sous-graphe comme un nœud !
# Les clés partagées (contenu_a_valider, est_valide, raison_invalidite)
# sont automatiquement mappées
g_principal.add_node("valider", sous_graphe_validation)

g_principal.add_node("rapport", generer_rapport)
g_principal.set_entry_point("preparer")
g_principal.add_edge("preparer", "valider")
g_principal.add_edge("valider", "rapport")
g_principal.add_edge("rapport", END)

app = g_principal.compile()
resultat = app.invoke({
    "messages": [],
    "contenu_a_valider": "",
    "est_valide": False,
    "raison_invalidite": "",
    "rapport": ""
})
print(resultat["rapport"])
```

---

## Communication entre agents : passage de messages

```python
# Communication via l'état global — pattern recommandé

class EtatCommunication(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    # Canaux de communication dédiés par agent
    message_de_chercheur: str     # L'agent chercheur écrit ici
    message_de_analyste: str      # L'agent analyste écrit ici
    instructions_superviseur: str # Le superviseur écrit ici

    # Méta-données
    agent_actuel: str
    historique_agents: list[str]
```

---

## Points clés à retenir

1. Le pattern superviseur = un LLM central qui **délègue** à des agents spécialisés
2. Chaque agent spécialisé est un **graphe complet** compilé (sous-graphe)
3. L'état global **partagé** est le mécanisme de communication entre agents
4. Les sous-graphes se **branchent** comme des nœuds normaux si les clés d'état correspondent
5. Toujours prévoir une **protection anti-boucle** sur le superviseur (max iterations)
6. Les agents peuvent s'exécuter **en parallèle** si leurs tâches sont indépendantes

---

## Suite

Passez à `05-persistence.md` pour apprendre à sauvegarder et reprendre des conversations longues avec les checkpointers.
