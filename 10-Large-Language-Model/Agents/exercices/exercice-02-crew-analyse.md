# Exercice 02 — Crew d'Analyse de Marché avec CrewAI

## Contexte

Vous travaillez dans le département stratégie d'une entreprise tech. La direction vous demande de construire un **système automatisé d'analyse de marché** qui, pour un secteur donné, produit un rapport complet incluant : données de marché, analyse concurrentielle, et recommandations stratégiques.

---

## Objectifs pédagogiques

À l'issue de cet exercice, vous aurez :

- Défini 3 agents avec des rôles, objectifs et backstories soignés
- Créé 3 tâches avec des livrables précis et du `context` entre elles
- Ajouté un outil custom créé avec `@tool`
- Utilisé `output_pydantic` pour garantir la structure de sortie
- Comparé l'exécution en mode `sequential` et `hierarchical`
- Paramétré l'exécution avec `kickoff(inputs={...})`

---

## Prérequis

```bash
pip install crewai crewai-tools langchain-openai pydantic python-dotenv

# .env
OPENAI_API_KEY=sk-...
# SERPER_API_KEY=... (optionnel — des outils simulés sont fournis)
```

---

## Partie 1 — Modèles de données

### Étape 1.1 — Définir les structures Pydantic

```python
# analyse_marche.py
import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# TODO 1.1 : Définir 3 modèles Pydantic

# Modèle 1 : DonneesMarche
# - secteur : str
# - taille_marche_milliards : float (taille du marché en Md$)
# - taux_croissance_annuel : float (CAGR en %)
# - acteurs_principaux : List[str] (top 5)
# - tendances : List[str] (3-5 tendances)

# Modèle 2 : AnalyseConcurrentielle
# - leaders_marche : List[str]
# - challengers : List[str]
# - points_differenciation : List[str]
# - barrieres_entree : List[str]
# - niveau_concurrence : str  # "faible" | "modéré" | "élevé" | "très élevé"

# Modèle 3 : RapportStrategique
# - resume_executif : str (max 200 mots)
# - opportunites : List[str] (3-5)
# - risques : List[str] (3-5)
# - recommandations : List[str] (3 recommandations numérotées)
# - score_attractivite : float (0.0 à 10.0)
# - horizon_investissement : str  # "court terme" | "moyen terme" | "long terme"
```

**Solution attendue :**

```python
class DonneesMarche(BaseModel):
    secteur: str
    taille_marche_milliards: float = Field(description="Taille du marché en milliards de dollars")
    taux_croissance_annuel: float = Field(description="CAGR estimé en pourcentage")
    acteurs_principaux: List[str] = Field(min_length=3, max_length=7)
    tendances: List[str] = Field(min_length=3, max_length=6)

class AnalyseConcurrentielle(BaseModel):
    leaders_marche: List[str]
    challengers: List[str]
    points_differenciation: List[str]
    barrieres_entree: List[str]
    niveau_concurrence: str  # "faible" | "modéré" | "élevé" | "très élevé"

class RapportStrategique(BaseModel):
    resume_executif: str
    opportunites: List[str] = Field(min_length=3, max_length=5)
    risques: List[str] = Field(min_length=3, max_length=5)
    recommandations: List[str] = Field(min_length=3, max_length=3)
    score_attractivite: float = Field(ge=0.0, le=10.0)
    horizon_investissement: str
```

---

## Partie 2 — Outils custom

### Étape 2.1 — Créer des outils métier

```python
# TODO 2.1 : Créer 3 outils avec @tool

# Outil 1 : rechercher_donnees_secteur(secteur: str) -> str
# - Retourne des données de marché simulées pour un secteur
# - Doit contenir des chiffres plausibles (taille, croissance, acteurs)
# - Secteurs simulés : IA, Cloud, Cybersécurité, FinTech, SaaS, IoT

# Outil 2 : analyser_tendances(secteur: str, horizon: str = "2024-2026") -> str
# - Retourne les tendances du secteur
# - Différentes selon le secteur

# Outil 3 : evaluer_attractivite(
#     taille_marche: float,
#     taux_croissance: float,
#     nb_concurrents: int,
#     barriere_entree: str
# ) -> str
# - Calcule un score d'attractivité basé sur une formule
# - Formule suggérée : score = (min(taux_croissance/2, 5) + min(taille_marche/50, 3) +
#   (3 if nb_concurrents < 5 else 2 if nb_concurrents < 10 else 1) +
#   (2 if barriere_entree == "haute" else 1)) / 1.1
```

**Solution attendue :**

```python
@tool("Données de Marché Sectorielles")
def rechercher_donnees_secteur(secteur: str) -> str:
    """Recherche des données de marché pour un secteur technologique.
    Fournit taille du marché, taux de croissance et acteurs principaux.
    Utilise pour collecter les données économiques d'un secteur.
    Args:
        secteur: Nom du secteur (IA, Cloud, Cybersécurité, FinTech, SaaS, IoT)
    """
    donnees = {
        "ia": {
            "taille": "200 milliards $",
            "croissance": "38% CAGR",
            "acteurs": "OpenAI, Anthropic, Google DeepMind, Microsoft, Meta AI, Amazon AWS AI",
            "detail": "Marché en hypercroissance, dominé par l'IA générative (GPT-4, Claude, Gemini). Forte adoption enterprise."
        },
        "cloud": {
            "taille": "680 milliards $",
            "croissance": "17% CAGR",
            "acteurs": "Amazon AWS (32%), Microsoft Azure (23%), Google Cloud (11%), Alibaba Cloud, IBM",
            "detail": "Marché mature mais en croissance. Migration vers multi-cloud et edge computing."
        },
        "cybersécurité": {
            "taille": "190 milliards $",
            "croissance": "13% CAGR",
            "acteurs": "Palo Alto Networks, CrowdStrike, Fortinet, Cisco, Check Point",
            "detail": "Demande portée par l'augmentation des cyberattaques. Segment Zero Trust en forte croissance."
        },
        "fintech": {
            "taille": "340 milliards $",
            "croissance": "25% CAGR",
            "acteurs": "Stripe, Square/Block, PayPal, Revolut, N26, Adyen",
            "detail": "Disruption des banques traditionnelles. Paiements, néobanques, DeFi."
        },
        "saas": {
            "taille": "280 milliards $",
            "croissance": "18% CAGR",
            "acteurs": "Salesforce, ServiceNow, Workday, HubSpot, Notion, Figma",
            "detail": "Modèle récurrent dominant. Consolidation en cours avec acquisitions."
        },
        "iot": {
            "taille": "120 milliards $",
            "croissance": "22% CAGR",
            "acteurs": "Cisco, Siemens, Honeywell, Bosch, PTC, ABB",
            "detail": "Industrie 4.0 en déploiement. Convergence IoT + IA (Edge AI)."
        }
    }

    secteur_lower = secteur.lower()
    for cle, val in donnees.items():
        if cle in secteur_lower or secteur_lower in cle:
            return f"""Données secteur {secteur} :
- Taille du marché : {val['taille']}
- Taux de croissance : {val['croissance']}
- Acteurs principaux : {val['acteurs']}
- Contexte : {val['detail']}"""

    return f"Données pour le secteur '{secteur}' : marché estimé à 50-100 Md$, croissance 10-20% CAGR. Données détaillées requièrent une étude de marché approfondie."


@tool("Analyse des Tendances Sectorielles")
def analyser_tendances(secteur: str, horizon: str = "2024-2026") -> str:
    """Identifie les tendances majeures d'un secteur technologique.
    Utilise pour comprendre les évolutions du marché sur un horizon donné.
    Args:
        secteur: Nom du secteur technologique
        horizon: Période d'analyse (ex: '2024-2026', '2025-2030')
    """
    tendances_par_secteur = {
        "ia": [
            "Agents IA autonomes remplacent les chatbots simples",
            "Modèles multimodaux (texte + image + audio + vidéo)",
            "IA embarquée sur mobile et edge devices",
            "Régulation IA : EU AI Act en vigueur, autres pays suivent",
            "Réduction des coûts : GPT-4o-mini 100x moins cher que GPT-4"
        ],
        "cloud": [
            "Multi-cloud et cloud hybride comme standard enterprise",
            "FinOps : optimisation des coûts cloud priorité #1",
            "Souveraineté cloud en Europe (RGPD, données sensibles)",
            "Green cloud : réduction empreinte carbone datacenters",
            "Serverless et containers pour déploiement applicatif"
        ],
        "cybersécurité": [
            "Zero Trust Architecture remplace le périmètre réseau",
            "IA défensive vs IA offensive : course aux armements",
            "Ransomware-as-a-Service : démocratisation des attaques",
            "Supply chain security : sécuriser toute la chaîne logicielle",
            "Cyber-assurance en forte croissance"
        ],
    }

    secteur_lower = secteur.lower()
    for cle, tendances in tendances_par_secteur.items():
        if cle in secteur_lower:
            return f"Tendances {secteur} ({horizon}) :\n" + "\n".join([f"• {t}" for t in tendances])

    return f"Tendances générales tech ({horizon}) :\n• IA dans tous les secteurs\n• Cloud-first obligatoire\n• Cybersécurité renforcée\n• Développement durable\n• Consolidation du marché"


@tool("Calculateur d'Attractivité Investissement")
def evaluer_attractivite(
    taille_marche: float,
    taux_croissance: float,
    nb_concurrents: int,
    barriere_entree: str
) -> str:
    """Calcule un score d'attractivité pour un investissement dans un secteur.
    Utilise pour obtenir une évaluation quantitative du potentiel d'investissement.
    Args:
        taille_marche: Taille du marché en milliards de dollars
        taux_croissance: Taux de croissance annuel en pourcentage
        nb_concurrents: Nombre de concurrents majeurs (acteurs significatifs)
        barriere_entree: Niveau des barrières à l'entrée ('faible', 'moyenne', 'haute', 'très haute')
    """
    # Composantes du score (sur 10)
    score_taille = min(taille_marche / 50.0, 3.0)        # Max 3 pts si > 150 Md$
    score_croissance = min(taux_croissance / 8.0, 4.0)    # Max 4 pts si > 32%
    score_competition = (
        2.0 if nb_concurrents < 5 else
        1.5 if nb_concurrents < 10 else
        1.0 if nb_concurrents < 20 else
        0.5
    )
    score_barriere = {
        "faible": 0.5,
        "moyenne": 1.0,
        "haute": 1.5,
        "très haute": 2.0
    }.get(barriere_entree.lower(), 1.0)

    score_total = min(score_taille + score_croissance + score_competition + score_barriere, 10.0)

    interpretation = (
        "TRÈS ATTRACTIF — opportunité d'investissement majeure" if score_total >= 8.0 else
        "ATTRACTIF — bon potentiel, due diligence recommandée" if score_total >= 6.0 else
        "MODÉRÉ — potentiel limité, prudence conseillée" if score_total >= 4.0 else
        "FAIBLE — marché mature ou difficile d'accès"
    )

    return f"""Score d'attractivité : {score_total:.1f}/10
Interprétation : {interpretation}
Détail du calcul :
- Taille de marché ({taille_marche} Md$) : +{score_taille:.1f} pts
- Croissance ({taux_croissance}% CAGR) : +{score_croissance:.1f} pts
- Concurrence ({nb_concurrents} acteurs) : +{score_competition:.1f} pts
- Barrières d'entrée ({barriere_entree}) : +{score_barriere:.1f} pts"""
```

---

## Partie 3 — Agents et Tâches

### Étape 3.1 — Définir les agents

```python
# TODO 3.1 : Définir 3 agents spécialisés

# Agent 1 : agent_economiste
# - Rôle : Économiste de Marché Senior
# - Goal : Collecter et analyser les données économiques et financières d'un marché
# - Backstory : Économiste avec expérience en cabinets de conseil, expert en analyse sectorielle
# - Outils : rechercher_donnees_secteur, evaluer_attractivite
# - verbose=True

# Agent 2 : agent_stratege_concurrence
# - Rôle : Stratège Concurrentiel
# - Goal : Analyser le paysage concurrentiel et identifier les avantages différenciateurs
# - Backstory : Consultant en stratégie, ancien chez McKinsey, spécialiste Porter's Five Forces
# - Outils : analyser_tendances
# - verbose=True

# Agent 3 : agent_directeur_strategie
# - Rôle : Directeur de la Stratégie
# - Goal : Synthétiser les analyses pour produire des recommandations stratégiques actionnables
# - Backstory : Ex-partner cabinet conseil, boardroom experience, vision long terme
# - Outils : evaluer_attractivite (pour valider le score final)
# - verbose=True
# - allow_delegation=False (synthétiseur final — ne délègue pas)
```

**Solution attendue :**

```python
agent_economiste = Agent(
    role="Économiste de Marché Senior",
    goal="Collecter et analyser les données économiques et financières pour évaluer objectivement un marché sectoriel",
    backstory="""Économiste avec 12 ans d'expérience en analyse macroéconomique et sectorielle.
    Passé par l'INSEE, la Banque de France, et plusieurs cabinets de conseil (BCG, Roland Berger).
    Expert en modélisation de marchés, analyse de flux financiers et prévision de tendances.
    Méthodique, tu bases toujours ton analyse sur des données chiffrées vérifiables.
    Tu signales explicitement quand une donnée est une estimation.""",
    tools=[rechercher_donnees_secteur, evaluer_attractivite],
    llm=llm,
    verbose=True
)

agent_stratege_concurrence = Agent(
    role="Stratège Concurrentiel",
    goal="Analyser le paysage concurrentiel pour identifier opportunités et menaces dans un marché donné",
    backstory="""Consultant en stratégie avec 15 ans d'expérience, formé à l'INSEAD.
    Spécialiste du framework Porter's Five Forces et de l'analyse SWOT.
    Tu as analysé des centaines de secteurs pour des Fortune 500.
    Tu identifies avec précision les barrières à l'entrée, les avantages concurrentiels durables,
    et les zones de création de valeur. Tu es direct dans tes évaluations, même quand elles sont défavorables.""",
    tools=[analyser_tendances],
    llm=llm,
    verbose=True
)

agent_directeur_strategie = Agent(
    role="Directeur de la Stratégie",
    goal="Produire des recommandations stratégiques actionnables basées sur une synthèse rigoureuse des analyses",
    backstory="""Ex-Partner chez McKinsey avec 20 ans d'expérience board-level.
    Tu as conseillé des groupes CAC 40, des licornes européennes, et des fonds d'investissement.
    Tu excelles à transformer des analyses complexes en recommandations claires et hiérarchisées.
    Tu penses toujours en termes de ROI, de délai de mise en œuvre, et de risque d'exécution.
    Tes recommandations sont réalistes : ni trop optimistes, ni trop conservatrices.""",
    tools=[evaluer_attractivite],
    llm=llm,
    verbose=True,
    allow_delegation=False
)
```

### Étape 3.2 — Définir les tâches

```python
# TODO 3.2 : Définir 3 tâches avec output_pydantic et context appropriés

# Tâche 1 : tache_analyse_marche
# - Description : analyser le secteur {secteur} sous l'angle économique
# - Agent : agent_economiste
# - output_pydantic : DonneesMarche
# - Doit utiliser les outils pour chercher des données réelles

# Tâche 2 : tache_analyse_concurrence
# - Description : analyser la concurrence sur le marché {secteur}
# - Agent : agent_stratege_concurrence
# - output_pydantic : AnalyseConcurrentielle
# - context : [tache_analyse_marche]

# Tâche 3 : tache_rapport_strategique
# - Description : produire le rapport stratégique final sur {secteur}
# - Agent : agent_directeur_strategie
# - output_pydantic : RapportStrategique
# - context : [tache_analyse_marche, tache_analyse_concurrence]
```

**Solution attendue :**

```python
tache_analyse_marche = Task(
    description="""Réalise une analyse économique approfondie du marché {secteur}.

    Utilise l'outil 'Données de Marché Sectorielles' pour collecter les données.
    Ensuite, utilise l'outil 'Calculateur d'Attractivité' pour évaluer le potentiel.

    Tu dois déterminer avec précision :
    - La taille actuelle du marché mondial (en milliards de dollars)
    - Le taux de croissance annuel composé (CAGR) pour 2024-2027
    - Les 5 acteurs principaux du marché
    - Les 4 à 5 tendances majeures qui façonnent ce marché

    Sois factuel et basé sur les données des outils — ne pas inventer de chiffres.""",

    expected_output="""Données de marché structurées avec :
    - Taille du marché en milliards de dollars (nombre précis)
    - CAGR en pourcentage (nombre précis)
    - Liste des 5 acteurs principaux
    - Liste de 4-5 tendances majeures
    Toutes les données chiffrées basées sur les résultats des outils.""",

    output_pydantic=DonneesMarche,
    agent=agent_economiste
)

tache_analyse_concurrence = Task(
    description="""Réalise une analyse concurrentielle du marché {secteur} en utilisant le framework Porter.

    Utilise l'outil 'Analyse des Tendances' pour enrichir ta compréhension du marché.
    Appuie-toi sur les données de marché déjà collectées.

    Identifie :
    - Les leaders qui dominent le marché (top 3-5 avec justification)
    - Les challengers qui gagnent des parts de marché
    - Les 3-4 facteurs de différenciation clés dans ce secteur
    - Les 2-3 barrières à l'entrée principales
    - Le niveau de concurrence global (faible/modéré/élevé/très élevé)""",

    expected_output="""Analyse concurrentielle structurée avec :
    - Leaders marché (liste avec noms)
    - Challengers (liste)
    - Facteurs de différenciation clés
    - Barrières à l'entrée
    - Niveau de concurrence évalué avec justification""",

    output_pydantic=AnalyseConcurrentielle,
    agent=agent_stratege_concurrence,
    context=[tache_analyse_marche]
)

tache_rapport_strategique = Task(
    description="""Synthétise l'ensemble des analyses pour produire un rapport stratégique
    sur le secteur {secteur} destiné au comité de direction.

    Utilise l'outil d'attractivité pour calculer et valider le score final.

    Le rapport doit inclure :
    1. Un résumé exécutif percutant (100-150 mots maximum)
    2. Les 3-5 opportunités les plus prometteuses
    3. Les 3-5 risques principaux avec leur niveau de sévérité
    4. Exactement 3 recommandations stratégiques prioritaires et actionnables
    5. Un score d'attractivité global sur 10 (basé sur l'outil de calcul)
    6. L'horizon d'investissement recommandé

    Sois direct et actionnable — ce rapport sera lu par des décideurs pressés.""",

    expected_output="""Rapport stratégique complet avec :
    - Résumé exécutif (100-150 mots)
    - 3-5 opportunités concrètes
    - 3-5 risques identifiés
    - 3 recommandations stratégiques numérotées
    - Score d'attractivité /10 avec justification
    - Horizon d'investissement (court/moyen/long terme)""",

    output_pydantic=RapportStrategique,
    agent=agent_directeur_strategie,
    context=[tache_analyse_marche, tache_analyse_concurrence]
)
```

---

## Partie 4 — Crew et exécution

### Étape 4.1 — Assembler et exécuter

```python
# TODO 4.1 : Créer le crew et exécuter pour deux secteurs différents

# Créer le crew en mode séquentiel
# Exécuter pour le secteur "Intelligence Artificielle"
# Afficher les résultats structurés
# Comparer avec le secteur "Cybersécurité"
```

**Solution attendue :**

```python
def analyser_secteur(secteur: str, mode: str = "sequential") -> dict:
    """Lance l'analyse d'un secteur et retourne les résultats structurés."""
    import time

    process = Process.sequential if mode == "sequential" else Process.hierarchical
    manager_llm = ChatOpenAI(model="gpt-4o", temperature=0) if mode == "hierarchical" else None

    crew_config = {
        "agents": [agent_economiste, agent_stratege_concurrence, agent_directeur_strategie],
        "tasks": [tache_analyse_marche, tache_analyse_concurrence, tache_rapport_strategique],
        "process": process,
        "verbose": True
    }
    if manager_llm:
        crew_config["manager_llm"] = manager_llm

    crew_analyse = Crew(**crew_config)

    print(f"\n{'='*70}")
    print(f"ANALYSE DU SECTEUR : {secteur.upper()} (mode: {mode})")
    print(f"{'='*70}\n")

    debut = time.time()
    resultat = crew_analyse.kickoff(inputs={"secteur": secteur})
    duree = time.time() - debut

    # Extraire les résultats Pydantic
    resultats = {
        "secteur": secteur,
        "duree_secondes": round(duree, 1),
        "donnees_marche": None,
        "analyse_concurrence": None,
        "rapport": None
    }

    if tache_analyse_marche.output and tache_analyse_marche.output.pydantic:
        resultats["donnees_marche"] = tache_analyse_marche.output.pydantic

    if tache_analyse_concurrence.output and tache_analyse_concurrence.output.pydantic:
        resultats["analyse_concurrence"] = tache_analyse_concurrence.output.pydantic

    if tache_rapport_strategique.output and tache_rapport_strategique.output.pydantic:
        resultats["rapport"] = tache_rapport_strategique.output.pydantic

    # Afficher le résumé
    print(f"\n{'='*70}")
    print(f"RÉSULTATS POUR {secteur.upper()}")
    print(f"{'='*70}")
    print(f"Durée d'exécution : {duree:.1f}s")

    if resultats["donnees_marche"]:
        dm = resultats["donnees_marche"]
        print(f"\n📊 DONNÉES DE MARCHÉ :")
        print(f"  Taille : {dm.taille_marche_milliards} Md$")
        print(f"  CAGR : {dm.taux_croissance_annuel}%")
        print(f"  Acteurs : {', '.join(dm.acteurs_principaux[:3])}...")

    if resultats["rapport"]:
        r = resultats["rapport"]
        print(f"\n📋 RAPPORT STRATÉGIQUE :")
        print(f"  Score attractivité : {r.score_attractivite}/10")
        print(f"  Horizon : {r.horizon_investissement}")
        print(f"\n  Résumé exécutif :")
        print(f"  {r.resume_executif[:200]}...")
        print(f"\n  Recommandations :")
        for rec in r.recommandations:
            print(f"  → {rec}")

    if resultats["donnees_marche"] and resultats["rapport"]:
        print(f"\n📈 TOKENS UTILISÉS : {resultat.token_usage.total_tokens}")

    return resultats


if __name__ == "__main__":
    # Analyser deux secteurs en mode séquentiel
    resultats_ia = analyser_secteur("Intelligence Artificielle", mode="sequential")
    resultats_cyber = analyser_secteur("Cybersécurité", mode="sequential")

    # Comparaison rapide
    print("\n" + "="*70)
    print("COMPARAISON SECTEURS")
    print("="*70)

    for res, nom in [(resultats_ia, "IA"), (resultats_cyber, "Cybersécurité")]:
        if res["rapport"]:
            print(f"\n{nom} :")
            print(f"  Score attractivité : {res['rapport'].score_attractivite}/10")
            print(f"  Horizon : {res['rapport'].horizon_investissement}")
            print(f"  Durée analyse : {res['duree_secondes']}s")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `analyser_secteur("Intelligence Artificielle")` avec `verbose=True`, en montrant le raisonnement de chaque agent dans l'ordre : l'économiste qui appelle `rechercher_donnees_secteur` puis `evaluer_attractivite`, le stratège qui utilise `analyser_tendances`, et le directeur qui synthétise. Finir par l'affichage des résultats Pydantic structurés.
> **Expliquer :** Pointer le moment où le contexte passe de l'économiste au stratège — CrewAI injecte automatiquement le résultat de la tâche précédente. Le stratège ne "cherche" pas à nouveau les données : il les reçoit via le contexte. C'est la transmission de connaissance entre agents.

---

## Partie 5 — Comparaison Sequential vs Hierarchical

### Étape 5.1 — Comparer les deux modes

```python
# TODO 5.1 : Exécuter le même secteur en mode hiérarchique et comparer

# Attention : le mode hiérarchique nécessite un LLM plus puissant comme manager
# Comparer :
# - L'ordre d'exécution des tâches
# - La qualité des résultats
# - Le nombre de tokens utilisés
# - Le temps d'exécution

# Note : pour voir la différence, désactiver verbose sur les agents
# et activer uniquement sur le crew
```

```python
import time

print("\n" + "="*70)
print("COMPARAISON SEQUENTIAL vs HIERARCHICAL")
print("="*70)

# Mode séquentiel
t0 = time.time()
crew_seq = Crew(
    agents=[agent_economiste, agent_stratege_concurrence, agent_directeur_strategie],
    tasks=[tache_analyse_marche, tache_analyse_concurrence, tache_rapport_strategique],
    process=Process.sequential,
    verbose=True
)
r_seq = crew_seq.kickoff(inputs={"secteur": "Cloud Computing"})
temps_seq = time.time() - t0

print(f"\n[SÉQUENTIEL] Durée: {temps_seq:.1f}s | Tokens: {r_seq.token_usage.total_tokens}")

# Mode hiérarchique
t0 = time.time()
crew_hier = Crew(
    agents=[agent_economiste, agent_stratege_concurrence, agent_directeur_strategie],
    tasks=[tache_analyse_marche, tache_analyse_concurrence, tache_rapport_strategique],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4o", temperature=0),
    verbose=True
)
r_hier = crew_hier.kickoff(inputs={"secteur": "Cloud Computing"})
temps_hier = time.time() - t0

print(f"\n[HIÉRARCHIQUE] Durée: {temps_hier:.1f}s | Tokens: {r_hier.token_usage.total_tokens}")

# Résumé de la comparaison
print(f"\nRÉSUMÉ COMPARATIF :")
print(f"  Séquentiel : {temps_seq:.0f}s, {r_seq.token_usage.total_tokens} tokens")
print(f"  Hiérarchique : {temps_hier:.0f}s, {r_hier.token_usage.total_tokens} tokens")
print(f"  Delta tokens : +{r_hier.token_usage.total_tokens - r_seq.token_usage.total_tokens} tokens pour le mode hiérarchique")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le tableau comparatif final montrant la différence de temps et de tokens entre les deux modes. Idéalement, capturer aussi un exemple de décision du Manager LLM en mode hiérarchique (visible dans les logs verbose) qui montre comment il orchestre les agents différemment.
> **Expliquer :** Le mode hiérarchique coûte plus de tokens à cause des appels supplémentaires au Manager LLM. En revanche, il peut être plus flexible sur des tâches complexes où l'ordre optimal n'est pas connu à l'avance. Pour ce cas d'usage précis (pipeline séquentiel bien défini), le mode séquentiel est plus efficace.

---

## Critères d'évaluation

| Critère | Points |
|---------|--------|
| 3 modèles Pydantic corrects | 3 |
| 3 outils @tool fonctionnels | 3 |
| 3 agents avec backstory précise | 3 |
| 3 tâches avec expected_output et context | 3 |
| output_pydantic sur les 3 tâches | 2 |
| kickoff(inputs={...}) fonctionnel | 1 |
| Comparaison sequential vs hierarchical | 2 |
| Affichage des résultats structurés | 2 |
| Code propre et commenté | 1 |
| **Total** | **20** |

---

## Questions de réflexion

1. Pourquoi la `backstory` d'un agent influence-t-elle réellement sa réponse ? N'est-ce pas qu'un "habillage" textuel ?

2. Que se passe-t-il si vous définissez `context=[tache_rapport_strategique]` sur `tache_analyse_marche` (référence circulaire) ?

3. Dans quel cas précis le mode `hierarchical` produirait-il de meilleurs résultats que `sequential` pour ce use case ?

4. Comment testeriez-vous la robustesse de ce crew face à un secteur que les agents ne connaissent pas (ex: "Aquaculture verticale") ?

5. Si `tache_analyse_marche` échoue (output invalide par rapport au modèle Pydantic), que se passe-t-il pour les tâches suivantes ?
