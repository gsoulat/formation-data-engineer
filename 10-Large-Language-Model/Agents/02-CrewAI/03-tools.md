# CrewAI — Outils

## Objectifs

- Utiliser les outils intégrés de CrewAI (recherche web, fichiers, scraping)
- Créer des outils custom avec `@tool` et la classe `BaseTool`
- Assigner des outils aux bons agents
- Comprendre la délégation d'outils

---

## Les outils dans CrewAI

Un outil est une **capacité externe** qu'un agent peut utiliser pour accomplir sa tâche. Les outils permettent à l'agent d'interagir avec le monde réel : rechercher sur le web, lire des fichiers, appeler des APIs, faire des calculs.

```python
# L'agent décide seul quand et comment utiliser ses outils
agent = Agent(
    role="Chercheur",
    goal="...",
    backstory="...",
    tools=[outil_recherche, outil_lecture_fichier],  # Outils disponibles
    verbose=True
)
```

---

## Outils intégrés CrewAI (crewai-tools)

### SerperDevTool — Recherche Google

```bash
pip install crewai-tools
# Obtenir une clé API gratuite sur serper.dev
```

```python
from crewai_tools import SerperDevTool
import os

# Recherche Google (nécessite SERPER_API_KEY dans l'environnement)
outil_recherche = SerperDevTool(
    n_results=5,  # Nombre de résultats retournés
)

agent_chercheur = Agent(
    role="Chercheur Web",
    goal="Trouver des informations actuelles en utilisant Google",
    backstory="Expert en recherche web avec des techniques avancées de requêtage.",
    tools=[outil_recherche],
    verbose=True
)
```

### TavilySearchResults — Recherche avec résumés

```python
from langchain_community.tools.tavily_search import TavilySearchResults

# Tavily fournit des résultats avec résumés — plus utile que les snippets Google
outil_tavily = TavilySearchResults(
    max_results=3,
    search_depth="advanced",  # "basic" ou "advanced"
    include_answer=True,      # Inclure une réponse synthétisée
    include_raw_content=False  # Contenu HTML brut (lourd)
)
```

### ScrapeWebsiteTool — Extraire le contenu d'une URL

```python
from crewai_tools import ScrapeWebsiteTool

# Scraper une URL spécifique
outil_scraping = ScrapeWebsiteTool(
    website_url="https://example.com"  # URL fixe
)

# Ou un scraper générique (l'agent passe l'URL)
outil_scraping_generique = ScrapeWebsiteTool()

agent_scraper = Agent(
    role="Extracteur de Données Web",
    goal="Extraire le contenu textuel de pages web",
    backstory="Spécialiste en extraction de données web.",
    tools=[outil_scraping_generique],
    verbose=True
)
```

### FileReadTool — Lire des fichiers

```python
from crewai_tools import FileReadTool

# Lire un fichier spécifique
outil_lecture = FileReadTool(file_path="/chemin/vers/mon_fichier.txt")

# Ou lecture générique (l'agent précise le chemin)
outil_lecture_generique = FileReadTool()
```

### DirectoryReadTool — Explorer un répertoire

```python
from crewai_tools import DirectoryReadTool

outil_repertoire = DirectoryReadTool(directory="/chemin/vers/mon_projet")

agent_code_reviewer = Agent(
    role="Reviewer de Code",
    goal="Analyser la structure et la qualité d'un projet Python",
    backstory="Senior developer avec expertise en revue de code.",
    tools=[outil_repertoire, outil_lecture_generique],
    verbose=True
)
```

### PDFSearchTool — Recherche dans des PDFs

```python
from crewai_tools import PDFSearchTool

outil_pdf = PDFSearchTool(pdf="/chemin/vers/rapport.pdf")

agent_lecteur_pdf = Agent(
    role="Analyste Documentaire",
    goal="Extraire et analyser des informations de documents PDF",
    backstory="Expert en analyse documentaire.",
    tools=[outil_pdf],
    verbose=True
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un agent utilisant SerperDevTool dans le terminal — montrer le Thought: "I need to search for X", puis l'Action: SerperDevTool avec la requête, puis l'Observation: avec les résultats Google retournés. Enchaîner sur la réponse finale de l'agent.
> **Expliquer :** L'agent n'a pas été programmé pour appeler la recherche Google à un moment précis — il a décidé seul qu'il en avait besoin pour répondre. C'est la différence fondamentale avec une pipeline classique où chaque étape est explicitement codée. Montrer que si la question ne nécessite pas de recherche, l'agent répondra directement sans appeler l'outil.

---

## Créer des outils custom avec @tool

La façon la plus simple de créer un outil custom :

```python
from crewai.tools import tool
from langchain_core.tools import tool as langchain_tool
from typing import Optional

# Syntaxe CrewAI (recommandée)
@tool("Calculatrice Financière")
def calculer_ratio(valeur1: float, valeur2: float, type_ratio: str = "division") -> str:
    """Calcule des ratios financiers entre deux valeurs.

    Args:
        valeur1: Première valeur numérique
        valeur2: Deuxième valeur numérique
        type_ratio: Type de calcul ('division', 'variation', 'multiple')

    Returns:
        Le résultat formaté avec le type de ratio
    """
    if valeur2 == 0:
        return "Erreur : Division par zéro impossible."

    if type_ratio == "division":
        resultat = valeur1 / valeur2
        return f"Ratio {valeur1} / {valeur2} = {resultat:.4f}"
    elif type_ratio == "variation":
        variation = ((valeur1 - valeur2) / valeur2) * 100
        sens = "hausse" if variation > 0 else "baisse"
        return f"Variation : {abs(variation):.1f}% en {sens}"
    elif type_ratio == "multiple":
        return f"{valeur1} représente {valeur1/valeur2:.1f}x la valeur de {valeur2}"
    else:
        return f"Type de ratio inconnu : {type_ratio}"


@tool("Convertisseur de Devises")
def convertir_devise(montant: float, devise_source: str, devise_cible: str) -> str:
    """Convertit un montant d'une devise à une autre.
    Taux de change approximatifs (simulés - en production, appeler une vraie API).

    Args:
        montant: Le montant à convertir
        devise_source: Code de la devise source (EUR, USD, GBP, JPY...)
        devise_cible: Code de la devise cible
    """
    # Taux simulés (en production : API ExchangeRate, Open Exchange Rates, etc.)
    taux_vers_eur = {
        "USD": 0.92, "GBP": 1.17, "JPY": 0.0061, "CHF": 1.02,
        "EUR": 1.0, "CAD": 0.68, "AUD": 0.60
    }

    source = devise_source.upper()
    cible = devise_cible.upper()

    if source not in taux_vers_eur or cible not in taux_vers_eur:
        return f"Devise non supportée. Devises disponibles : {', '.join(taux_vers_eur.keys())}"

    montant_en_eur = montant * taux_vers_eur[source]
    montant_converti = montant_en_eur / taux_vers_eur[cible]

    return f"{montant:.2f} {source} = {montant_converti:.2f} {cible} (taux simulé)"


@tool("Analyseur de Sentiment")
def analyser_sentiment_texte(texte: str) -> str:
    """Analyse le sentiment d'un texte court (règles basées, sans LLM).
    Utile pour un classement rapide sans appel API supplémentaire.

    Args:
        texte: Le texte à analyser (max 500 mots)
    """
    mots_positifs = ["excellent", "super", "génial", "parfait", "réussi", "croissance", "hausse", "bénéfice", "succès"]
    mots_negatifs = ["mauvais", "échec", "perte", "baisse", "problème", "crise", "risque", "difficulté", "déclin"]

    texte_lower = texte.lower()
    score_positif = sum(texte_lower.count(mot) for mot in mots_positifs)
    score_negatif = sum(texte_lower.count(mot) for mot in mots_negatifs)

    if score_positif > score_negatif * 1.5:
        sentiment = "POSITIF"
    elif score_negatif > score_positif * 1.5:
        sentiment = "NÉGATIF"
    else:
        sentiment = "NEUTRE"

    return f"Sentiment : {sentiment} (positif={score_positif}, négatif={score_negatif})"
```

---

## Créer des outils avec BaseTool (plus de contrôle)

Pour des outils plus complexes (avec état, configuration, ou validation) :

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests
import json

class InputsAPIMeteo(BaseModel):
    """Paramètres de l'outil météo."""
    ville: str = Field(description="Nom de la ville (en français ou anglais)")
    pays: str = Field(default="FR", description="Code pays ISO 2 lettres (FR, US, GB...)")
    jours: int = Field(default=1, ge=1, le=7, description="Nombre de jours de prévision (1-7)")

class OutilMeteoAPI(BaseTool):
    """Outil de prévision météo utilisant l'API OpenWeatherMap."""
    name: str = "Prévision Météo"
    description: str = """Obtient les prévisions météo pour une ville.
    Utilise cet outil pour toute question météo ou planification dépendant du temps.
    Paramètres requis : ville (str), optionnel : pays (str, défaut FR), jours (int 1-7, défaut 1)."""

    api_key: Optional[str] = None

    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "demo")

    def _run(self, ville: str, pays: str = "FR", jours: int = 1) -> str:
        """Logique principale de l'outil."""
        # Simulation (en production : vraie requête API)
        meteos_simulees = {
            "paris": {"temp": 14, "description": "Nuageux", "humidite": 75},
            "lyon": {"temp": 18, "description": "Ensoleillé", "humidite": 50},
            "marseille": {"temp": 22, "description": "Partiellement nuageux", "humidite": 60},
        }

        cle = ville.lower()
        if cle in meteos_simulees:
            m = meteos_simulees[cle]
            return f"""Météo à {ville} ({pays}) :
            - Température : {m['temp']}°C
            - Conditions : {m['description']}
            - Humidité : {m['humidite']}%
            - Prévision pour {jours} jour(s) [données simulées]"""
        else:
            return f"Données météo non disponibles pour {ville}. Villes supportées : Paris, Lyon, Marseille."

    # Optionnel : version async
    async def _arun(self, ville: str, pays: str = "FR", jours: int = 1) -> str:
        return self._run(ville, pays, jours)


# Utilisation
outil_meteo = OutilMeteoAPI(api_key="ma_cle_api")

agent_planificateur = Agent(
    role="Planificateur d'Événements",
    goal="Planifier des événements en tenant compte de la météo et des contraintes logistiques",
    backstory="Expert en organisation d'événements avec 10 ans d'expérience.",
    tools=[outil_meteo, calculer_ratio, convertir_devise],
    verbose=True
)
```

---

## Exemple complet : crew de recherche avec outils réels

```python
# crew_recherche_outils.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# ---- Outils ----
outil_recherche = TavilySearchResults(max_results=3, include_answer=True)

@tool("Formatage Markdown")
def formater_markdown(contenu: str, titre: str, niveau_titre: int = 1) -> str:
    """Formate du contenu en markdown structuré.

    Args:
        contenu: Le texte à formater
        titre: Le titre principal de la section
        niveau_titre: Niveau du titre (1=H1, 2=H2, 3=H3)
    """
    prefix = "#" * min(max(niveau_titre, 1), 6)
    return f"{prefix} {titre}\n\n{contenu}\n"

@tool("Générateur de Résumé")
def generer_resume(texte_long: str, max_mots: int = 100) -> str:
    """Tronque et nettoie un texte pour en faire un résumé court.

    Args:
        texte_long: Le texte source
        max_mots: Nombre maximum de mots dans le résumé
    """
    mots = texte_long.split()
    if len(mots) <= max_mots:
        return texte_long
    return " ".join(mots[:max_mots]) + "... [tronqué]"

# ---- Agents ----
agent_veilleur = Agent(
    role="Veilleur Technologique",
    goal="Rechercher et collecter les informations les plus récentes sur les sujets demandés",
    backstory="""Expert en veille technologique, tu utilises systématiquement des recherches web
    pour t'assurer d'avoir des informations à jour. Tu ne fais jamais confiance à ta mémoire
    pour des données récentes — tu cherches TOUJOURS avant de répondre sur des faits actuels.""",
    tools=[outil_recherche],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

agent_analyste = Agent(
    role="Analyste Technologique",
    goal="Analyser les informations collectées pour en extraire des insights stratégiques",
    backstory="""Analyste senior avec expertise en évaluation de tendances technologiques.
    Tu reçois des données brutes de recherche et tu les transformes en analyses structurées
    avec des insights actionnables. Tu distingues les tendances de fond des effets de mode.""",
    tools=[generer_resume, formater_markdown],
    llm=llm,
    verbose=True
)

# ---- Tâches ----
tache_collecte = Task(
    description="""Recherche les 3 dernières annonces majeures dans le domaine des LLMs (Large Language Models).
    Pour chaque annonce :
    - Nom du modèle/produit
    - Entreprise
    - Date approximative
    - Innovation principale
    Utilise l'outil de recherche pour obtenir des informations récentes.""",
    expected_output="""Liste de 3 annonces récentes avec entreprise, date, et innovation principale.
    Les informations doivent être récentes (2024-2025) et sourcées depuis la recherche web.""",
    agent=agent_veilleur
)

tache_analyse = Task(
    description="""À partir des annonces collectées, produis une analyse de tendances.
    Identifie :
    1. Les patterns communs entre ces annonces (que font-elles toutes ?)
    2. Les entreprises leaders et challengers
    3. Ce que cela signifie pour les développeurs et data engineers
    4. Une prédiction pour les 6 prochains mois

    Utilise l'outil de formatage pour structurer ta réponse en markdown.""",
    expected_output="""Un rapport d'analyse en markdown avec 4 sections :
    Patterns communs, Acteurs clés, Implications pratiques, Prédictions.
    Chaque section doit être substantielle (3-5 phrases minimum).""",
    agent=agent_analyste,
    context=[tache_collecte]
)

# ---- Crew ----
crew_veille = Crew(
    agents=[agent_veilleur, agent_analyste],
    tasks=[tache_collecte, tache_analyse],
    process=Process.sequential,
    verbose=True
)

print("Démarrage de la veille technologique...\n")
resultat = crew_veille.kickoff()
print("\n" + "="*60)
print("RAPPORT DE VEILLE TECHNOLOGIQUE")
print("="*60)
print(resultat.raw)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution du crew avec `verbose=True`, en montrant spécifiquement l'agent `veilleur` qui fait un appel à `TavilySearchResults` (visible comme "Action: tavily_search_results_json") suivi de l'Observation avec les vrais résultats de recherche web.
> **Expliquer :** Comparer avec un appel LLM classique sans outil — le LLM aurait inventé des informations (hallucination). Avec l'outil de recherche, il dispose de vraies données récentes. C'est la différence entre un LLM qui "sait" et un agent qui "cherche".

---

## Partager des outils entre agents

```python
# Les outils peuvent être partagés
outil_recherche = TavilySearchResults(max_results=3)

agent_a = Agent(role="...", tools=[outil_recherche, ...])
agent_b = Agent(role="...", tools=[outil_recherche, ...])
# Les deux partagent la même instance d'outil
```

## Cache des outils

CrewAI peut mettre en cache les résultats des outils pour éviter des appels répétés :

```python
from crewai.tools import tool

@tool("Outil avec cache")
def rechercher_avec_cache(requete: str) -> str:
    """Recherche avec mise en cache des résultats.
    Args:
        requete: La requête de recherche
    """
    # CrewAI met automatiquement en cache si le même outil
    # est appelé avec les mêmes paramètres dans le même crew
    return f"Résultat pour : {requete}"

# Désactiver le cache pour un outil si les résultats changent
agent_temps_reel = Agent(
    role="...",
    tools=[outil_recherche],
    cache=False  # Désactive le cache pour cet agent
)
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans le terminal avec `verbose=True`, le raisonnement complet d'un agent utilisant un outil custom `@tool` : "Thought: I need to use the Formatage Markdown tool...", "Action: Formatage Markdown", "Action Input: {...}", "Observation: [résultat]", puis la réponse finale qui intègre le markdown généré.
> **Expliquer :** Montrer que la docstring de l'outil ("Formate du contenu en markdown...") apparaît dans le raisonnement de l'agent — c'est exactement le texte que le LLM lit pour décider quand appeler l'outil. Changer la docstring et relancer pour montrer que le comportement de l'agent change.

---

## Bonnes pratiques pour les outils

```python
# ✓ Description précise avec cas d'usage
@tool("Bon outil")
def bon_outil(parametre: str) -> str:
    """Décrit précisément QUAND utiliser cet outil (use cases).
    Mentionne les limites et contraintes.
    Args:
        parametre: Description précise du paramètre avec format attendu
    """
    pass

# ✗ Description vague
@tool("Mauvais outil")
def mauvais_outil(p: str) -> str:
    """Fait des choses."""  # L'agent ne saura pas quand l'utiliser !
    pass

# ✓ Toujours retourner une string (même en cas d'erreur)
@tool("Outil robuste")
def outil_robuste(valeur: float) -> str:
    """..."""
    try:
        resultat = effectuer_calcul(valeur)
        return f"Résultat : {resultat}"
    except Exception as e:
        return f"Erreur lors du calcul : {str(e)}. Essayez avec une valeur différente."

# ✗ Ne jamais retourner None ou lever une exception
@tool("Outil fragile")
def outil_fragile(valeur: float) -> str:
    """..."""
    return str(1 / valeur)  # ZeroDivisionError non gérée !
```

---

## Points clés à retenir

1. Les outils intégrés `crewai-tools` couvrent les cas d'usage communs — chercher avant de coder
2. `@tool("Nom")` est la façon la plus simple de créer un outil custom
3. La **docstring** de l'outil est ce que l'agent lit pour décider de l'utiliser — soignez-la
4. `BaseTool` offre plus de contrôle : validation Pydantic, async, état interne
5. Assigner les outils **au bon agent** — un agent ne doit avoir que les outils pertinents à son rôle
6. Toujours gérer les erreurs dans les outils et retourner une string descriptive

---

## Suite

Passez à `04-processus.md` pour comprendre la différence entre `Process.sequential` et `Process.hierarchical`, et quand utiliser chacun.
