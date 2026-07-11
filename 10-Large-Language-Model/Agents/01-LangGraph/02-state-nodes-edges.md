# LangGraph — État, Nœuds et Arêtes

## Objectifs

- Maîtriser la définition d'un état TypedDict avec réducteurs
- Comprendre `add_node`, `add_edge`, `add_conditional_edges`
- Construire des graphes avec boucles et branchements
- Compiler et inspecter un graphe

---

## L'état TypedDict en profondeur

L'état est le cœur de tout graphe LangGraph. Bien le concevoir est crucial.

### Définition de base

```python
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class EtatAnalyse(TypedDict):
    # Messages LLM — accumulés avec add_messages
    messages: Annotated[list[BaseMessage], add_messages]

    # Données de travail — remplacées à chaque modification
    sujet: str
    analyse: Optional[str]
    score_confiance: float

    # Compteur d'itérations — pour éviter les boucles infinies
    iterations: int

    # Indicateurs de contrôle
    besoin_clarification: bool
    analyse_terminee: bool
```

### Réducteurs personnalisés

Un réducteur est une fonction qui détermine comment combiner une ancienne valeur et une nouvelle valeur. Vous pouvez créer vos propres réducteurs :

```python
from typing import Annotated

def fusionner_listes(existant: list, nouveau: list) -> list:
    """Fusionne deux listes sans doublons."""
    return list(set(existant + nouveau))

def incrementer(existant: int, increment: int) -> int:
    """Additionne au lieu de remplacer."""
    return existant + increment

class EtatAvecReducteurs(TypedDict):
    # Accumule les tags sans doublons
    tags: Annotated[list[str], fusionner_listes]

    # Additionne les tokens utilisés
    tokens_utilises: Annotated[int, incrementer]

    # Accumule les messages (réducteur intégré)
    messages: Annotated[list[BaseMessage], add_messages]
```

Démonstration du comportement :

```python
from langgraph.graph import StateGraph, END

def noeud_a(etat):
    return {
        "tags": ["python", "ia"],
        "tokens_utilises": 150,
    }

def noeud_b(etat):
    return {
        "tags": ["langgraph", "python"],  # "python" ne sera pas dupliqué
        "tokens_utilises": 200,           # Sera ajouté : total = 350
    }

g = StateGraph(EtatAvecReducteurs)
g.add_node("a", noeud_a)
g.add_node("b", noeud_b)
g.set_entry_point("a")
g.add_edge("a", "b")
g.add_edge("b", END)

app = g.compile()
resultat = app.invoke({"tags": [], "tokens_utilises": 0, "messages": []})
print(resultat["tags"])           # ['python', 'ia', 'langgraph']
print(resultat["tokens_utilises"]) # 350
```

---

## Nœuds avancés

### Nœud avec logique conditionnelle interne

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def noeud_analyser_sentiment(etat: EtatAnalyse) -> dict:
    """Analyse le sentiment du sujet et met à jour l'état."""
    sujet = etat["sujet"]
    iterations = etat.get("iterations", 0)

    prompt = f"""Analyse le sentiment de ce texte sur une échelle de 0 à 1
    (0 = très négatif, 1 = très positif).
    Texte : {sujet}
    Réponds UNIQUEMENT avec un nombre décimal entre 0 et 1."""

    messages = [
        SystemMessage(content="Tu es un expert en analyse de sentiment."),
        HumanMessage(content=prompt)
    ]

    reponse = llm.invoke(messages)

    try:
        score = float(reponse.content.strip())
        score = max(0.0, min(1.0, score))  # Clamp entre 0 et 1
    except ValueError:
        score = 0.5  # Valeur par défaut si parsing échoue

    return {
        "score_confiance": score,
        "iterations": iterations + 1,
        "messages": messages + [reponse]
    }
```

### Nœud de décision pure (sans LLM)

```python
def noeud_verifier_qualite(etat: EtatAnalyse) -> dict:
    """Vérifie si l'analyse est satisfaisante sans appeler de LLM."""
    score = etat.get("score_confiance", 0)
    iterations = etat.get("iterations", 0)

    # Logique de validation
    if score is None:
        besoin_clarification = True
    elif abs(score - 0.5) < 0.1 and iterations < 3:
        # Score trop ambigu et on peut encore itérer
        besoin_clarification = True
    else:
        besoin_clarification = False

    return {
        "besoin_clarification": besoin_clarification,
        "analyse_terminee": not besoin_clarification
    }
```

---

## Arêtes conditionnelles

### Pattern de base

```python
from langgraph.graph import StateGraph, END

def routeur(etat: EtatAnalyse) -> str:
    """Décide quelle branche emprunter.
    Retourne une CHAÎNE correspondant à une clé dans le mapping."""
    if etat.get("besoin_clarification") and etat.get("iterations", 0) < 3:
        return "clarifier"
    elif etat.get("analyse_terminee"):
        return "terminer"
    else:
        return "reessayer"

graphe = StateGraph(EtatAnalyse)
graphe.add_node("analyser", noeud_analyser_sentiment)
graphe.add_node("verifier", noeud_verifier_qualite)
graphe.add_node("clarifier", noeud_demander_clarification)
graphe.add_node("formatter", noeud_formatter_resultat)

# Arêtes directes
graphe.set_entry_point("analyser")
graphe.add_edge("analyser", "verifier")
graphe.add_edge("clarifier", "analyser")  # Boucle !

# Arête conditionnelle
graphe.add_conditional_edges(
    "verifier",           # Depuis ce nœud
    routeur,              # Cette fonction détermine la destination
    {
        "clarifier": "clarifier",   # Si routeur() retourne "clarifier"
        "terminer": "formatter",    # Si routeur() retourne "terminer"
        "reessayer": "analyser",    # Si routeur() retourne "reessayer"
    }
)

graphe.add_edge("formatter", END)
```

### Protection contre les boucles infinies

Toujours prévoir une sortie de secours quand il y a des boucles :

```python
MAX_ITERATIONS = 5

def routeur_securise(etat: EtatAnalyse) -> str:
    iterations = etat.get("iterations", 0)

    # Sortie forcée si trop d'itérations
    if iterations >= MAX_ITERATIONS:
        print(f"[ATTENTION] Nombre maximum d'itérations atteint ({iterations})")
        return "forcer_fin"

    if etat.get("besoin_clarification"):
        return "clarifier"
    return "terminer"

graphe.add_conditional_edges(
    "verifier",
    routeur_securise,
    {
        "clarifier": "clarifier",
        "terminer": "formatter",
        "forcer_fin": END          # Sortie directe sans passer par formatter
    }
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le graphe Mermaid d'un StateGraph avec une boucle (analyser → verifier → clarifier → analyser), montrant la flèche de retour clairement visible dans le diagramme.
> **Expliquer :** Montrer que LangGraph détecte automatiquement les cycles dans le graphe et les représente correctement. Insister sur l'importance de la condition de sortie pour éviter les boucles infinies.

---

## Exemple complet : pipeline d'analyse qualité

Voici un graphe complet qui analyse un texte, vérifie la qualité de l'analyse, et boucle si nécessaire :

```python
# analyse_qualite.py
import os
from typing import TypedDict, Annotated, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- ÉTAT ---
class EtatPipeline(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    texte_source: str
    analyse: Optional[str]
    score_qualite: Optional[float]
    iterations: int
    erreurs: list[str]

# --- NOEUDS ---
def analyser_texte(etat: EtatPipeline) -> dict:
    """Nœud 1 : Analyse le texte avec le LLM."""
    print(f"  [analyser_texte] Itération {etat.get('iterations', 0) + 1}")

    prompt = f"""Analyse ce texte et fournis :
1. Un résumé en 2 phrases
2. Les thèmes principaux (liste de 3 max)
3. Le ton général (positif/neutre/négatif)

Texte : {etat['texte_source']}

Réponds en JSON avec les clés : resume, themes, ton"""

    msg = HumanMessage(content=prompt)
    reponse = llm.invoke([SystemMessage(content="Tu es un analyste de texte expert."), msg])

    return {
        "analyse": reponse.content,
        "iterations": etat.get("iterations", 0) + 1,
        "messages": [msg, reponse]
    }

def evaluer_qualite(etat: EtatPipeline) -> dict:
    """Nœud 2 : Évalue la qualité de l'analyse."""
    print(f"  [evaluer_qualite] Évaluation de l'analyse...")

    if not etat.get("analyse"):
        return {"score_qualite": 0.0, "erreurs": ["Analyse vide"]}

    analyse = etat["analyse"]
    erreurs = []

    # Vérifications simples
    if "resume" not in analyse.lower() and "{" not in analyse:
        erreurs.append("Format JSON non respecté")
        score = 0.3
    elif len(analyse) < 50:
        erreurs.append("Analyse trop courte")
        score = 0.4
    else:
        score = 0.9

    return {"score_qualite": score, "erreurs": erreurs}

def affiner_analyse(etat: EtatPipeline) -> dict:
    """Nœud 3 : Demande une correction au LLM."""
    print(f"  [affiner_analyse] Correction demandée...")
    erreurs = etat.get("erreurs", [])
    analyse_precedente = etat.get("analyse", "")

    prompt = f"""L'analyse précédente avait ces problèmes : {', '.join(erreurs)}

Analyse précédente : {analyse_precedente}

Corrige l'analyse en respectant strictement le format JSON demandé avec les clés resume, themes, ton.
Texte original : {etat['texte_source']}"""

    msg = HumanMessage(content=prompt)
    reponse = llm.invoke([msg])

    return {
        "analyse": reponse.content,
        "messages": [msg, reponse]
    }

def formater_sortie(etat: EtatPipeline) -> dict:
    """Nœud 4 : Formate la sortie finale."""
    print(f"  [formater_sortie] Formatage final...")
    print(f"\n{'='*50}")
    print(f"ANALYSE FINALE (après {etat['iterations']} itération(s))")
    print(f"Score qualité : {etat.get('score_qualite', 0):.1%}")
    print(f"{'='*50}")
    print(etat.get("analyse", "Aucune analyse disponible"))
    return {}

# --- ROUTEUR ---
def decider_suite(etat: EtatPipeline) -> str:
    score = etat.get("score_qualite", 0)
    iterations = etat.get("iterations", 0)

    if score >= 0.8:
        return "qualite_ok"
    elif iterations < 3:
        return "affiner"
    else:
        return "forcer_fin"

# --- GRAPHE ---
constructeur = StateGraph(EtatPipeline)

constructeur.add_node("analyser", analyser_texte)
constructeur.add_node("evaluer", evaluer_qualite)
constructeur.add_node("affiner", affiner_analyse)
constructeur.add_node("formater", formater_sortie)

constructeur.set_entry_point("analyser")
constructeur.add_edge("analyser", "evaluer")
constructeur.add_conditional_edges(
    "evaluer",
    decider_suite,
    {
        "qualite_ok": "formater",
        "affiner": "affiner",
        "forcer_fin": "formater"
    }
)
constructeur.add_edge("affiner", "evaluer")
constructeur.add_edge("formater", END)

app = constructeur.compile()

# Visualiser
print("Graphe :")
print(app.get_graph().draw_ascii())

# Exécuter
texte = """
L'intelligence artificielle générative a connu une expansion sans précédent
en 2024. Des modèles comme GPT-4 et Claude ont transformé des secteurs entiers,
de la création de contenu au développement logiciel. Cependant, des questions
éthiques persistantes sur les biais et la propriété intellectuelle soulèvent
des débats importants dans la société.
"""

etat_initial = {
    "texte_source": texte,
    "messages": [],
    "analyse": None,
    "score_qualite": None,
    "iterations": 0,
    "erreurs": []
}

print("\nDémarrage de l'analyse...\n")
resultat = app.invoke(etat_initial)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution complète du script `analyse_qualite.py` dans le terminal, montrant les prints de chaque nœud avec le numéro d'itération, puis le résultat final formaté.
> **Expliquer :** Pointer le moment où le routeur `decider_suite` prend une décision. Si l'analyse est bonne au premier coup, montrer que le graphe prend le chemin direct "qualite_ok → formater". Sinon, montrer la boucle "affiner → evaluer".

---

## Inspecter l'exécution pas à pas

LangGraph fournit `stream()` pour voir chaque étape :

```python
# Exécution avec streaming des étapes
print("\nExécution pas à pas :")
for event in app.stream(etat_initial, stream_mode="updates"):
    for noeud, modifications in event.items():
        print(f"\n--- Nœud : {noeud} ---")
        for cle, valeur in modifications.items():
            if cle != "messages":  # Éviter d'afficher les messages complets
                print(f"  {cle}: {valeur}")
```

Résultat :

```
--- Nœud : analyser ---
  analyse: {"resume": "...", "themes": [...], "ton": "..."}
  iterations: 1

--- Nœud : evaluer ---
  score_qualite: 0.9
  erreurs: []

--- Nœud : formater ---
```

---

## Graphes avec nœuds parallèles

LangGraph supporte l'exécution **parallèle** de nœuds indépendants :

```python
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Annotated

def reduire_resultats(a: dict, b: dict) -> dict:
    """Fusionne deux dictionnaires."""
    return {**a, **b}

class EtatParallele(TypedDict):
    texte: str
    # Ces deux champs seront remplis en parallèle
    analyse_sentiment: Annotated[dict, reduire_resultats]
    analyse_entites: Annotated[dict, reduire_resultats]
    rapport_final: str

def analyser_sentiment_parallel(etat):
    # Simulé — en réalité, appel LLM
    return {"analyse_sentiment": {"ton": "positif", "score": 0.8}}

def analyser_entites_parallel(etat):
    # Simulé — en réalité, appel LLM ou NER
    return {"analyse_entites": {"organisations": ["OpenAI"], "lieux": ["Paris"]}}

def combiner_analyses(etat):
    sentiment = etat.get("analyse_sentiment", {})
    entites = etat.get("analyse_entites", {})
    rapport = f"Sentiment: {sentiment.get('ton')} | Entités: {entites.get('organisations')}"
    return {"rapport_final": rapport}

g = StateGraph(EtatParallele)
g.add_node("sentiment", analyser_sentiment_parallel)
g.add_node("entites", analyser_entites_parallel)
g.add_node("combiner", combiner_analyses)

# Les deux nœuds partent du START en parallèle
g.add_edge(START, "sentiment")
g.add_edge(START, "entites")

# Les deux convergent vers "combiner"
g.add_edge("sentiment", "combiner")
g.add_edge("entites", "combiner")
g.add_edge("combiner", END)

app_parallele = g.compile()

resultat = app_parallele.invoke({
    "texte": "OpenAI annonce GPT-5 à Paris",
    "analyse_sentiment": {},
    "analyse_entites": {},
    "rapport_final": ""
})
print(resultat["rapport_final"])
# Sentiment: positif | Entités: ['OpenAI']
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La visualisation Mermaid du graphe parallèle (fan-out / fan-in) généré par `app_parallele.get_graph().draw_mermaid()`, montrant les deux arêtes depuis START vers "sentiment" et "entites", puis les deux arêtes convergentes vers "combiner".
> **Expliquer :** Ce pattern fan-out/fan-in est très utile pour les analyses multi-dimensionnelles où les tâches sont indépendantes. LangGraph les exécute en parallèle automatiquement dès que plusieurs nœuds partent du même nœud source. Comparer avec un pipeline séquentiel qui les exécuterait l'un après l'autre — la parallélisation réduit la latence de moitié.

---

## Résumé des patterns d'arêtes

```python
# 1. Arête simple
graphe.add_edge("noeud_a", "noeud_b")

# 2. Depuis START (explicite)
from langgraph.graph import START
graphe.add_edge(START, "premier_noeud")
# Équivalent à :
graphe.set_entry_point("premier_noeud")

# 3. Vers END
graphe.add_edge("dernier_noeud", END)

# 4. Conditionnelle avec mapping
graphe.add_conditional_edges("noeud", fonction_routeur, {"cle1": "dest1", "cle2": "dest2"})

# 5. Conditionnelle sans mapping (la fonction retourne directement le nom du nœud)
def routeur_direct(etat) -> str:
    return "noeud_suivant"  # Retourne directement le nom

graphe.add_conditional_edges("noeud", routeur_direct)
# Pas de mapping nécessaire si la fonction retourne un nom de nœud valide

# 6. Nœuds parallèles (fan-out)
graphe.add_edge(START, "noeud_a")
graphe.add_edge(START, "noeud_b")
# Les deux s'exécutent en parallèle
```

---

## Points clés à retenir

1. Le `TypedDict` d'état est le **contrat** entre tous les nœuds — bien le concevoir en début de projet
2. Les réducteurs permettent l'**accumulation** (add_messages) vs le **remplacement** (défaut)
3. `add_conditional_edges` prend (nœud_source, fonction_routeur, mapping_optionnel)
4. Toujours prévoir une **protection anti-boucle infinie** avec un compteur d'itérations
5. `stream(mode="updates")` permet de **tracer** l'exécution nœud par nœud
6. Les nœuds peuvent s'exécuter en **parallèle** si plusieurs arêtes partent du même nœud

---

## Suite

Passez à `03-agent-reactif.md` pour construire un véritable agent ReAct avec des outils, en utilisant `ToolNode` et la gestion des appels de fonctions.
