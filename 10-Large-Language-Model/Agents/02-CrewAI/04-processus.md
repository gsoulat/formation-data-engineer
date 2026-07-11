# CrewAI — Processus d'Exécution

## Objectifs

- Comprendre `Process.sequential` et `Process.hierarchical`
- Configurer le `manager_llm` pour le processus hiérarchique
- Choisir le bon processus selon le cas d'usage
- Gérer les dépendances entre tâches dans les deux modes

---

## Vue d'ensemble des processus

CrewAI propose deux modes d'orchestration :

```
SÉQUENTIEL                    HIÉRARCHIQUE
─────────────────────         ────────────────────────────
Tâche 1 → Agent A             Manager LLM
    ↓                              ↙        ↘
Tâche 2 → Agent B          Agent A       Agent B
    ↓                       (Tâche 1)    (Tâche 2)
Tâche 3 → Agent C               ↘        ↙
    ↓                          Manager LLM
 Résultat                      (Synthèse)
```

---

## Process.sequential — Exécution en séquence

C'est le mode par défaut. Les tâches s'exécutent **dans l'ordre**, chaque résultat étant disponible pour les tâches suivantes.

```python
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# --- Équipe de production de contenu ---
agent_recherche = Agent(
    role="Chercheur de Contenu",
    goal="Trouver des informations précises et documentées sur le sujet demandé",
    backstory="Expert en recherche documentaire avec un réseau de sources fiables.",
    llm=llm,
    verbose=True
)

agent_planification = Agent(
    role="Planificateur Éditorial",
    goal="Structurer un plan de contenu cohérent et engageant",
    backstory="Directeur éditorial avec 15 ans d'expérience en média digital.",
    llm=llm,
    verbose=True
)

agent_redaction = Agent(
    role="Rédacteur Principal",
    goal="Produire un contenu de haute qualité basé sur le plan éditorial",
    backstory="Rédacteur senior avec expertise en contenu technique et vulgarisation.",
    llm=llm,
    verbose=True
)

agent_revision = Agent(
    role="Réviseur et Éditeur",
    goal="Assurer la qualité, la cohérence et l'exactitude du contenu produit",
    backstory="Ancien correcteur de presse avec œil pour le détail et la précision.",
    llm=llm,
    verbose=True
)

# --- Tâches séquentielles ---
sujet = "L'impact de l'IA sur les métiers de la data en 2025"

tache_recherche = Task(
    description=f"""Recherche approfondie sur : "{sujet}"

    Collecte :
    - Statistiques récentes (taux d'adoption, emploi, salaires)
    - Témoignages ou études de cas d'entreprises
    - Opinions d'experts reconnus du domaine
    - Tendances pour les 2 prochaines années

    Sois factuel et cites des sources précises.""",
    expected_output="""Notes de recherche structurées avec :
    - 5-8 points factuels avec sources
    - 2-3 citations d'experts
    - Liste de tendances identifiées""",
    agent=agent_recherche
)

tache_plan = Task(
    description=f"""À partir de la recherche effectuée, crée un plan éditorial détaillé
    pour un article sur : "{sujet}"

    Le plan doit :
    - Identifier l'angle éditorial le plus percutant
    - Définir la structure (intro, développement, conclusion)
    - Préciser pour chaque section : objectif, points clés à couvrir, données à utiliser
    - Estimer la longueur idéale de chaque section""",
    expected_output="""Plan éditorial structuré avec :
    - Angle éditorial choisi et justification
    - 4-6 sections avec objectifs et contenus prévus
    - Longueurs estimées
    - Points de données clés à intégrer""",
    agent=agent_planification,
    context=[tache_recherche]  # Utilise les notes de recherche
)

tache_redaction = Task(
    description=f"""Rédige l'article complet sur : "{sujet}"
    en suivant exactement le plan éditorial fourni.

    Contraintes :
    - Entre 800 et 1200 mots
    - Format markdown avec titres H2/H3
    - Intégrer les données factuelles de la recherche
    - Ton professionnel mais accessible
    - Introduction accrocheuse, conclusion actionnable""",
    expected_output="""Article complet en markdown avec :
    - Titre H1 accrocheur
    - Introduction (150-200 mots)
    - Corps (4-5 sections H2)
    - Conclusion avec call-to-action
    Entre 800 et 1200 mots au total.""",
    agent=agent_redaction,
    context=[tache_recherche, tache_plan]  # Utilise la recherche ET le plan
)

tache_revision = Task(
    description="""Révise et finalise l'article rédigé.

    Vérifie et corrige :
    1. Exactitude factuelle (les données correspondent-elles à la recherche ?)
    2. Cohérence et fluidité (les transitions sont-elles naturelles ?)
    3. Orthographe et grammaire
    4. Respect du plan éditorial
    5. Ton et niveau de langue adaptés

    Fournis l'article final corrigé + un rapport de révision court (3-5 points).""",
    expected_output="""L'article final corrigé (complet, pas uniquement les corrections)
    suivi d'un rapport de révision en 3-5 bullet points indiquant les changements effectués.""",
    agent=agent_revision,
    context=[tache_recherche, tache_plan, tache_redaction]
)

# --- Crew séquentiel ---
crew_contenu = Crew(
    agents=[agent_recherche, agent_planification, agent_redaction, agent_revision],
    tasks=[tache_recherche, tache_plan, tache_redaction, tache_revision],
    process=Process.sequential,
    verbose=True
)

print("Démarrage de la production de contenu...\n")
resultat = crew_contenu.kickoff()

print("\n" + "="*70)
print("ARTICLE FINAL")
print("="*70)
print(resultat.raw)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** La progression séquentielle dans le terminal : "Working Agent: Chercheur" → terminé → "Working Agent: Planificateur" → terminé → etc. Montrer que chaque agent commence APRÈS que le précédent a terminé.
> **Expliquer :** En mode séquentiel, les résultats circulent automatiquement via le `context`. L'agent rédacteur "voit" à la fois les notes de recherche ET le plan éditorial sans que le développeur ait besoin de les copier-coller manuellement. C'est le flux de données implicite de CrewAI.

---

## Process.hierarchical — Manager LLM

En mode hiérarchique, un **manager LLM** orchestre dynamiquement les agents. Il décide qui fait quoi, dans quel ordre, en fonction des résultats intermédiaires.

```python
# Avantages du mode hiérarchique :
# - Gestion adaptative des dépendances
# - Redistribution si un agent échoue
# - Tâches plus flexibles (pas besoin d'ordre strict)
# - Adapté aux workflows complexes ou ambigus

# Inconvénients :
# - Plus lent (appels LLM supplémentaires pour le manager)
# - Moins prévisible (le manager peut prendre des décisions inattendues)
# - Plus coûteux en tokens

# --- Crew hiérarchique ---
llm_manager = ChatOpenAI(model="gpt-4o", temperature=0)  # Manager = LLM plus puissant

crew_hierarchique = Crew(
    agents=[agent_recherche, agent_planification, agent_redaction, agent_revision],
    tasks=[tache_recherche, tache_plan, tache_redaction, tache_revision],
    process=Process.hierarchical,
    manager_llm=llm_manager,  # REQUIS pour le mode hiérarchique
    verbose=True
)

resultat_h = crew_hierarchique.kickoff()
```

### Différences comportementales

```python
# Mode séquentiel — ordre garanti, déterministe
# Tâche 1 → Tâche 2 → Tâche 3 (toujours dans cet ordre)

# Mode hiérarchique — le manager peut décider de :
# - Paralléliser certaines tâches
# - Reprendre une tâche si le résultat est insuffisant
# - Changer l'assignation d'une tâche selon le contexte
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution du crew séquentiel de production de contenu, en montrant le passage de relais entre agents : "Working Agent: Chercheur de Contenu" → résultat affiché → "Working Agent: Planificateur Éditorial" → etc. Montrer également l'accès aux métriques `resultat.token_usage` après l'exécution.
> **Expliquer :** En mode séquentiel, la barre de progression CrewAI affiche clairement quel agent travaille. Chaque agent reçoit implicitement le résultat des agents précédents via `context`. Pointer le fait que le planificateur "voit" les notes du chercheur sans que le développeur ait eu à copier-coller quoi que ce soit.

---

## Exemple : Crew d'analyse concurrentielle (hiérarchique)

```python
# analyse_concurrentielle.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm_standard = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
llm_manager = ChatOpenAI(model="gpt-4o", temperature=0)

# Outils
@tool("Analyse de Prix")
def analyser_prix(produit: str, concurrent: str) -> str:
    """Compare les prix entre un produit et son concurrent.
    Args:
        produit: Le nom de notre produit
        concurrent: Le nom du produit concurrent
    """
    # Simulation
    return f"Comparaison {produit} vs {concurrent} : prix similaires (+/-10%), {concurrent} a un meilleur rapport qualité/prix sur l'entrée de gamme."

@tool("Analyse des Avis Clients")
def analyser_avis(entreprise: str) -> str:
    """Analyse les avis clients d'une entreprise.
    Args:
        entreprise: Nom de l'entreprise à analyser
    """
    scores = {"OpenAI": 4.2, "Anthropic": 4.5, "Google": 3.8, "Microsoft": 3.9}
    score = scores.get(entreprise, 3.5)
    return f"Score moyen {entreprise} : {score}/5 (satisfaction client, basé sur 1000+ avis)"

# Agents spécialisés
agent_marche = Agent(
    role="Analyste de Marché",
    goal="Analyser les tendances de marché et les parts de marché des acteurs clés",
    backstory="Consultant en stratégie avec expertise dans l'analyse de marchés technologiques émergents.",
    tools=[analyser_prix],
    llm=llm_standard,
    verbose=True
)

agent_clients = Agent(
    role="Analyste Expérience Client",
    goal="Évaluer la satisfaction client et les points de friction chez les concurrents",
    backstory="Spécialiste en Customer Experience avec accès à des données d'avis et de feedback.",
    tools=[analyser_avis],
    llm=llm_standard,
    verbose=True
)

agent_technologie = Agent(
    role="Analyste Technologique",
    goal="Évaluer les capacités techniques et l'innovation des acteurs du marché",
    backstory="Ex-ingénieur senior reconverti en analyste tech, avec 10 ans dans l'industrie IA.",
    llm=llm_standard,
    verbose=True
)

agent_stratege = Agent(
    role="Stratège Senior",
    goal="Synthétiser les analyses pour produire des recommandations stratégiques actionnables",
    backstory="Partner en cabinet de conseil, spécialiste en stratégie compétitive pour entreprises tech.",
    llm=llm_standard,
    verbose=True,
    allow_delegation=False
)

# Tâches
tache_marche = Task(
    description="""Analyse le marché des assistants IA pour entreprises en 2024.
    Focus : OpenAI, Anthropic, Google, Microsoft.
    Évalue les parts de marché, positionnement prix, et tendances.""",
    expected_output="""Rapport de marché avec tableau comparatif des 4 acteurs,
    parts de marché estimées, et 3 tendances majeures identifiées.""",
    agent=agent_marche
)

tache_clients = Task(
    description="""Analyse la satisfaction client des 4 acteurs principaux (OpenAI, Anthropic, Google, Microsoft).
    Identifie les forces et faiblesses perçues par les utilisateurs enterprise.""",
    expected_output="""Tableau des scores de satisfaction avec les 3 principales forces
    et 3 principales faiblesses par acteur.""",
    agent=agent_clients
)

tache_tech = Task(
    description="""Évalue les capacités techniques distinctives de chaque acteur.
    Focus : performance des modèles, APIs, outils developers, infrastructure.""",
    expected_output="""Grille d'évaluation technique avec notes 1-5 par critère
    pour chacun des 4 acteurs.""",
    agent=agent_technologie
)

tache_synthese = Task(
    description="""À partir de toutes les analyses (marché, clients, technologie),
    produis un rapport de positionnement stratégique.

    Le rapport doit :
    - Identifier les opportunités de différenciation
    - Proposer 3 axes stratégiques prioritaires
    - Évaluer les risques concurrentiels principaux
    - Formuler des recommandations pour entrer ou se renforcer sur ce marché""",
    expected_output="""Rapport stratégique complet avec :
    - Résumé exécutif (200 mots)
    - Tableau SWOT synthétique du marché
    - 3 recommandations stratégiques détaillées
    - Matrice risques/opportunités""",
    agent=agent_stratege,
    context=[tache_marche, tache_clients, tache_tech]
)

# --- Crew hiérarchique ---
crew_analyse = Crew(
    agents=[agent_marche, agent_clients, agent_technologie, agent_stratege],
    tasks=[tache_marche, tache_clients, tache_tech, tache_synthese],
    process=Process.hierarchical,
    manager_llm=llm_manager,
    verbose=True
)

print("Démarrage de l'analyse concurrentielle (mode hiérarchique)...\n")
resultat = crew_analyse.kickoff()

print("\n" + "="*70)
print("RAPPORT STRATÉGIQUE FINAL")
print("="*70)
print(resultat.raw)
```

---

## Tableau de décision : Sequential vs Hierarchical

| Critère | Sequential | Hierarchical |
|---------|-----------|--------------|
| Ordre des tâches | Fixe, prédéfini | Adaptatif |
| Coût LLM | Moindre | Plus élevé (+1 LLM) |
| Prédictibilité | Haute | Moyenne |
| Flexibilité | Limitée | Élevée |
| Debugging | Simple | Complexe |
| Cas d'usage | Pipelines clairs, ETL, rédaction | Analyse complexe, décision adaptative |
| Manager requis | Non | Oui (`manager_llm`) |
| Recommandé pour débutants | Oui | Non |

**Règle pratique** :
- Si les étapes sont claires et linéaires → `sequential`
- Si le workflow dépend des résultats intermédiaires et peut changer → `hierarchical`

---

## Passer des inputs dynamiques

```python
# Réutiliser un crew avec des inputs différents
crew_contenu = Crew(
    agents=[...],
    tasks=[...],
    process=Process.sequential
)

# Templates dans les descriptions de tâches
tache_recherche = Task(
    description="Recherche sur : {sujet}. Public cible : {public}.",
    expected_output="...",
    agent=...
)

# Kickoff avec des variables
resultat_1 = crew_contenu.kickoff(inputs={
    "sujet": "Machine Learning en production",
    "public": "data engineers débutants"
})

resultat_2 = crew_contenu.kickoff(inputs={
    "sujet": "Kubernetes pour ML",
    "public": "DevOps confirmés"
})
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Deux exécutions successives de `crew.kickoff(inputs={...})` avec des sujets différents ("Machine Learning en production" puis "Kubernetes pour ML"), montrant que le même crew produit des résultats totalement différents adaptés à chaque sujet et public cible.
> **Expliquer :** Les templates `{sujet}` et `{public}` dans les descriptions de tâches permettent de réutiliser la même équipe pour des contextes variés. C'est le pattern le plus scalable en production — définir l'équipe une fois, la déployer pour des centaines de cas d'usage différents. Comparer avec une approche sans templates où il faudrait re-coder les tâches à chaque fois.

---

## Exécution asynchrone

```python
import asyncio

async def lancer_plusieurs_crews():
    """Lance plusieurs crews en parallèle."""

    crew_a = Crew(agents=[...], tasks=[...], process=Process.sequential)
    crew_b = Crew(agents=[...], tasks=[...], process=Process.sequential)

    # Exécution parallèle
    resultats = await asyncio.gather(
        asyncio.to_thread(crew_a.kickoff, {"sujet": "IA"}),
        asyncio.to_thread(crew_b.kickoff, {"sujet": "Cloud"}),
    )

    for i, r in enumerate(resultats):
        print(f"Résultat crew {i+1}: {r.raw[:200]}")

asyncio.run(lancer_plusieurs_crews())
```

---

## Monitoring et métriques

```python
# Après kickoff(), accéder aux métriques
resultat = crew.kickoff()

# Utilisation des tokens
print(f"Tokens prompt : {resultat.token_usage.prompt_tokens}")
print(f"Tokens completion : {resultat.token_usage.completion_tokens}")
print(f"Tokens total : {resultat.token_usage.total_tokens}")

# Durée d'exécution (mesurée manuellement)
import time
debut = time.time()
resultat = crew.kickoff()
duree = time.time() - debut
print(f"Durée totale : {duree:.1f}s")

# Résultats intermédiaires par tâche
for task in crew.tasks:
    if task.output:
        print(f"Tâche '{task.description[:40]}...' → {len(task.output.raw)} caractères")
```

---

## Points clés à retenir

1. `Process.sequential` = ordre fixe, déterministe, recommandé pour démarrer
2. `Process.hierarchical` = orchestration adaptative, nécessite `manager_llm`
3. En mode hiérarchique, choisir un modèle **puissant** pour le manager (GPT-4o, Claude 3.5)
4. `kickoff(inputs={...})` permet de **paramétrer** les tâches à l'exécution
5. `resultat.token_usage` donne le coût en tokens pour optimiser les dépenses LLM
6. Les tâches sans `context` peuvent s'exécuter indépendamment en mode hiérarchique

---

## Suite

Passez à `05-flows.md` pour découvrir CrewAI Flows, la couche de programmation événementielle qui complète les Crews.
