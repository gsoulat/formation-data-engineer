# CrewAI — Introduction

## Objectifs

- Comprendre le modèle conceptuel de CrewAI
- Distinguer les 4 abstractions fondamentales : Crew, Agent, Task, Process
- Comparer l'approche CrewAI avec LangGraph
- Écrire et exécuter une première équipe

---

## Le paradigme CrewAI

Là où LangGraph pense en **graphes et états**, CrewAI pense en **équipes de travail**.

L'analogie est intentionnelle : vous définissez des **collaborateurs** avec des rôles précis, vous leur donnez des **missions**, et vous les faites travailler ensemble dans un **processus** défini.

```
Monde réel            CrewAI
─────────────────     ────────────────────
Chef de projet    →   Crew (orchestrateur)
Consultant        →   Agent (role + goal + backstory)
Mission           →   Task (description + expected_output)
Méthode de travail→   Process (sequential / hierarchical)
Outils de travail →   Tools (intégrés ou custom)
```

Cette métaphore rend CrewAI **très intuitif** à appréhender, surtout quand on peut décomposer son problème en rôles métier distincts.

---

## Installation

```bash
pip install crewai crewai-tools python-dotenv

# Optionnel : interface CLI CrewAI
pip install crewai[cli]
```

Vérification :

```python
import crewai
print(crewai.__version__)  # 0.80.x ou supérieur
```

Variables d'environnement nécessaires :

```bash
# .env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...      # Pour SerperDevTool (recherche Google)
```

---

## Les 4 abstractions fondamentales

### 1. Agent

Un agent représente un **collaborateur** avec une identité, des compétences et un objectif.

Les trois attributs clés :
- `role` : le titre/rôle du collaborateur ("Chercheur Senior", "Analyste Financier")
- `goal` : l'objectif principal de cet agent (une phrase claire)
- `backstory` : le contexte et l'expérience (donne de la profondeur au personnage)

```python
from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

agent_chercheur = Agent(
    role="Chercheur Senior en Technologie",
    goal="Trouver et synthétiser des informations précises et actuelles sur les technologies émergentes",
    backstory="""Tu as 10 ans d'expérience en veille technologique.
    Tu sais identifier les sources fiables, distinguer le signal du bruit,
    et présenter des informations complexes de façon accessible.
    Tu es méthodique, sceptique vis-à-vis des sources non vérifiées,
    et tu cites toujours tes références.""",
    llm=llm,
    verbose=True,  # Affiche le raisonnement de l'agent
    allow_delegation=False  # Cet agent ne peut pas déléguer à d'autres
)
```

### 2. Task

Une tâche est une **mission concrète** avec un livrable attendu.

```python
from crewai import Task

tache_recherche = Task(
    description="""Recherche les 5 tendances majeures de l'IA générative en 2024.
    Pour chaque tendance :
    - Donne un nom clair
    - Explique en 2-3 phrases
    - Cite au moins un exemple concret (entreprise, produit, ou technologie)
    - Évalue l'impact potentiel sur une échelle de 1 à 5""",

    expected_output="""Un rapport structuré avec 5 tendances, chacune avec :
    nom, description (2-3 phrases), exemple concret, score d'impact.
    Format clair avec des titres et sous-titres.""",

    agent=agent_chercheur  # Assignée à cet agent
)
```

### 3. Crew

Le crew est **l'équipe** — il orchestre l'exécution des agents sur les tâches.

```python
from crewai import Crew, Process

equipe = Crew(
    agents=[agent_chercheur],
    tasks=[tache_recherche],
    process=Process.sequential,  # Les tâches s'exécutent dans l'ordre
    verbose=True
)
```

### 4. Process

Deux modes d'exécution principaux :

- `Process.sequential` : les tâches s'exécutent dans l'ordre, chaque résultat est passé à la suivante
- `Process.hierarchical` : un manager LLM orchestre dynamiquement les agents

---

## Premier crew complet

```python
# premier_crew.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# ---- Agents ----
chercheur = Agent(
    role="Chercheur en Intelligence Artificielle",
    goal="Collecter des informations factuelles et à jour sur les sujets demandés",
    backstory="""Expert en veille technologique avec une spécialisation en IA.
    Tu consultes régulièrement arxiv, les blogs techniques et les annonces des grandes entreprises.
    Tu es rigoureux sur les sources et tu signales clairement ce qui est incertain.""",
    llm=llm,
    verbose=True
)

redacteur = Agent(
    role="Rédacteur Technique Senior",
    goal="Transformer des données brutes en contenu structuré, clair et engageant",
    backstory="""Tu as rédigé des centaines d'articles techniques pour des publications spécialisées.
    Tu sais adapter le niveau de langage au public cible, structurer l'information
    avec des titres clairs, et rendre des concepts complexes accessibles.
    Tu travailles toujours à partir des recherches fournies — tu n'inventes pas.""",
    llm=llm,
    verbose=True
)

# ---- Tâches ----
tache_1 = Task(
    description="""Recherche les 3 modèles de langage les plus importants sortis en 2024.
    Pour chaque modèle :
    - Nom complet et entreprise créatrice
    - Date de sortie approximative
    - 2-3 capacités distinctives majeures
    - Cas d'usage principal""",
    expected_output="""Liste de 3 modèles avec leurs caractéristiques clés.
    Chaque modèle présenté avec son nom, créateur, date, capacités et cas d'usage.
    Présentation en bullet points, concise et factuelle.""",
    agent=chercheur
)

tache_2 = Task(
    description="""À partir des données de recherche fournies sur les modèles LLM de 2024,
    rédige un article de blog professionnel intitulé "Les LLMs qui ont marqué 2024".
    L'article doit :
    - Avoir une introduction accrocheuse (2-3 phrases)
    - Présenter chaque modèle dans une section dédiée avec un sous-titre
    - Avoir une conclusion avec une perspective sur 2025
    - Être écrit pour un public technique mais non expert
    - Faire entre 400 et 600 mots""",
    expected_output="""Un article de blog complet en markdown avec :
    - Un titre H1
    - Une introduction
    - 3 sections H2 (une par modèle)
    - Une conclusion
    Le tout entre 400 et 600 mots.""",
    agent=redacteur,
    context=[tache_1]  # Cette tâche utilise le résultat de tache_1
)

# ---- Crew ----
equipe = Crew(
    agents=[chercheur, redacteur],
    tasks=[tache_1, tache_2],
    process=Process.sequential,
    verbose=True
)

# ---- Exécution ----
print("Démarrage de l'équipe...\n")
resultat = equipe.kickoff()

print("\n" + "="*60)
print("ARTICLE FINAL :")
print("="*60)
print(resultat.raw)  # Accès au résultat brut (string)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `premier_crew.py` avec `verbose=True`. Montrer en particulier le bloc "Thought/Action/Observation" de l'agent chercheur qui réfléchit à sa stratégie avant de chercher, puis la réponse du rédacteur qui s'appuie explicitement sur les données du chercheur.
> **Expliquer :** C'est le "cerveau" de l'agent visible dans le terminal. CrewAI utilise le framework ReAct en interne, mais le code utilisateur n'a pas à s'en occuper — la complexité est abstraite. Comparer avec LangGraph où on doit tout câbler manuellement.

---

## Accéder aux résultats

```python
# Résultat final (toujours la dernière tâche)
resultat = equipe.kickoff()

# Accès au texte brut
print(resultat.raw)

# Si la tâche demande un JSON
# (en définissant output_json sur la Task)
# print(resultat.json_dict)

# Accéder aux résultats intermédiaires de chaque tâche
for i, tache in enumerate(equipe.tasks):
    print(f"\n--- Résultat tâche {i+1} ---")
    if tache.output:
        print(tache.output.raw[:300])
```

---

## CrewAI vs LangGraph : première comparaison

| Aspect | CrewAI | LangGraph |
|--------|--------|-----------|
| Définir un agent | `Agent(role, goal, backstory)` | Fonction Python + nœud |
| Définir une tâche | `Task(description, expected_output)` | Logique dans le nœud |
| Orchestration | `Crew(agents, tasks, process)` | Graphe + arêtes |
| Outils | Attribut `tools` de l'Agent | `@tool` + `ToolNode` |
| Contrôle du flux | Limité (sequential/hierarchical) | Total (conditionnel, parallèle) |
| Courbe d'apprentissage | Faible | Élevée |
| Code minimal pour démarrer | ~30 lignes | ~60 lignes |

**CrewAI gagne** quand : le problème se décompose naturellement en rôles métier distincts avec des missions séquentielles claires.

**LangGraph gagne** quand : le flux est complexe, conditionnel, et nécessite un contrôle précis.

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le résultat de `resultat.raw` affiché dans le terminal après `crew.kickoff()` — l'article markdown généré par le rédacteur, avec ses sections H1/H2 et sa conclusion.
> **Expliquer :** Comparer la longueur et la qualité de la sortie avec un simple `llm.invoke(prompt)`. L'agent rédacteur bénéficie du contexte structuré produit par le chercheur (via `context=[tache_1]`), ce qui lui permet de citer des exemples réels plutôt que d'inventer. C'est la valeur ajoutée de la décomposition en tâches.

---

## Initialiser un projet CrewAI avec la CLI

CrewAI fournit une CLI pour créer un projet structuré :

```bash
# Créer un nouveau projet
crewai create crew mon_equipe_analyse

# Structure générée :
# mon_equipe_analyse/
# ├── src/
# │   └── mon_equipe_analyse/
# │       ├── config/
# │       │   ├── agents.yaml      ← Configuration des agents
# │       │   └── tasks.yaml       ← Configuration des tâches
# │       ├── tools/
# │       │   └── custom_tool.py
# │       ├── crew.py              ← Définition du Crew
# │       └── main.py              ← Point d'entrée
# ├── tests/
# └── pyproject.toml
```

Configuration YAML des agents (`agents.yaml`) :

```yaml
chercheur:
  role: >
    Chercheur Senior en {sujet}
  goal: >
    Trouver des informations précises et actuelles sur {sujet}
  backstory: >
    Expert en recherche documentaire avec 10 ans d'expérience.
    Tu sais identifier les sources fiables et synthétiser l'information.

redacteur:
  role: >
    Rédacteur Technique
  goal: >
    Produire un contenu clair et structuré pour {public_cible}
  backstory: >
    Rédacteur technique avec expertise dans la vulgarisation scientifique.
```

Configuration YAML des tâches (`tasks.yaml`) :

```yaml
tache_recherche:
  description: >
    Recherche les informations clés sur : {sujet}
    Couvre : historique, état actuel, perspectives.
  expected_output: >
    Rapport de recherche structuré avec sources.
  agent: chercheur

tache_redaction:
  description: >
    Rédige un article basé sur la recherche effectuée.
    Public : {public_cible}
  expected_output: >
    Article professionnel entre 500 et 800 mots en markdown.
  agent: redacteur
  context:
    - tache_recherche
```

```python
# crew.py avec YAML
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class MonEquipe:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def chercheur(self) -> Agent:
        return Agent(config=self.agents_config["chercheur"], verbose=True)

    @agent
    def redacteur(self) -> Agent:
        return Agent(config=self.agents_config["redacteur"], verbose=True)

    @task
    def tache_recherche(self) -> Task:
        return Task(config=self.tasks_config["tache_recherche"])

    @task
    def tache_redaction(self) -> Task:
        return Task(config=self.tasks_config["tache_redaction"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

# main.py
from mon_equipe_analyse.crew import MonEquipe

equipe = MonEquipe().crew()
resultat = equipe.kickoff(inputs={"sujet": "Quantum Computing", "public_cible": "développeurs"})
print(resultat.raw)
```

---

## Points clés à retenir

1. CrewAI = métaphore d'**équipe de travail** : agents avec rôles, tâches avec livrables
2. Un `Agent` = `role` + `goal` + `backstory` — la qualité du prompt système détermine la qualité du résultat
3. Une `Task` = `description` (ce qu'il faut faire) + `expected_output` (ce qu'on attend)
4. `context=[tache_precedente]` passe le résultat d'une tâche à une autre
5. `Process.sequential` = en séquence, `Process.hierarchical` = manager LLM
6. `crew.kickoff()` lance l'exécution, `resultat.raw` accède au texte

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'accès aux résultats intermédiaires via `tache.output.raw` après `kickoff()` — montrer que chaque tâche a conservé son propre résultat, pas seulement la tâche finale.
> **Expliquer :** En mode séquentiel, CrewAI accumule les sorties de chaque tâche. La propriété `resultat.raw` ne donne que la dernière tâche, mais `crew.tasks[0].output.raw` donne la sortie du chercheur, `crew.tasks[1].output.raw` celle du rédacteur, etc. Utile pour le débogage et l'audit.

---

## Suite

Passez à `02-agents-tasks.md` pour explorer en profondeur la configuration des agents et des tâches.
