# CrewAI — Agents et Tâches en profondeur

## Objectifs

- Maîtriser toutes les options de configuration d'un Agent
- Concevoir des tâches précises avec `description`, `expected_output`, et `context`
- Utiliser `output_json` et `output_pydantic` pour des sorties structurées
- Comprendre `allow_delegation` et le mécanisme de sous-tâches
- Debugger les sorties avec les callbacks

---

## Configuration avancée des Agents

```python
from crewai import Agent
from langchain_openai import ChatOpenAI

llm_puissant = ChatOpenAI(model="gpt-4o", temperature=0.1)
llm_rapide = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# Agent complet avec toutes les options
agent_expert = Agent(
    # Identité — ce sont les paramètres les plus importants
    role="Expert en Analyse Financière et Stratégique",
    goal="""Produire des analyses financières précises et actionnables
    pour des décideurs d'entreprise, basées sur des données vérifiables.""",
    backstory="""Tu es un analyste financier senior avec 15 ans d'expérience
    en banque d'investissement et conseil stratégique.
    Tu as travaillé pour des entreprises du CAC 40 et des startups en hypercroissance.
    Tu combines rigueur analytique et vision stratégique.
    Tu signales toujours tes hypothèses et les limites de ton analyse.
    Tu présentes les données avec des chiffres précis quand ils sont disponibles.""",

    # LLM — choisir selon le besoin (qualité vs coût)
    llm=llm_puissant,

    # Comportement
    verbose=True,              # Afficher le raisonnement (conseillé en dev)
    allow_delegation=True,     # Peut déléguer des sous-tâches à d'autres agents
    max_iterations=10,         # Nombre max de tours de raisonnement
    max_rpm=10,                # Limite de requêtes par minute (rate limiting)

    # Mémoire — l'agent se souvient entre les tâches du même crew
    memory=True,

    # Outils (voir fichier 03-tools.md)
    tools=[],
)
```

### Le rôle du backstory

La `backstory` est **critique** pour la qualité des réponses. Elle donne au LLM un cadre de référence :

```python
# ❌ Backstory trop vague — l'agent sera générique
mauvais_backstory = "Tu es un expert."

# ✓ Backstory précise — l'agent aura un comportement cohérent
bon_backstory = """Tu es un ingénieur data senior avec 8 ans d'expérience
en Python, SQL, et architecture cloud (AWS, GCP).
Tu as construit des pipelines de données pour des plateformes traitant
plusieurs téraoctets par jour.
Tu préconises les bonnes pratiques : tests unitaires, documentation inline,
gestion des erreurs. Tu expliques tes choix techniques."""

# Backstory avec contraintes explicites
backstory_contraint = """Tu es un juriste spécialisé en droit des affaires.
Tu DOIS toujours préciser que tes réponses ne constituent pas un conseil juridique officiel.
Tu cites les articles de loi pertinents (code civil, code de commerce).
En cas de doute, tu recommandes de consulter un avocat."""
```

---

## Configuration avancée des Tâches

### Attributs complets d'une Task

```python
from crewai import Task
from pydantic import BaseModel
from typing import List, Optional

# Définir un modèle Pydantic pour la sortie structurée
class AnalyseEntreprise(BaseModel):
    nom_entreprise: str
    secteur: str
    score_attractivite: float  # 0.0 à 10.0
    points_forts: List[str]
    risques: List[str]
    recommandation: str
    sources: Optional[List[str]] = None

tache_analyse = Task(
    # Description — le "cahier des charges" de la tâche
    description="""Analyse l'entreprise suivante : {entreprise}

    Tu dois évaluer :
    1. La position concurrentielle dans son secteur
    2. La solidité financière (si données disponibles)
    3. Les opportunités de croissance
    4. Les risques principaux (technologique, réglementaire, concurrentiel)

    Contexte : cette analyse est destinée à un comité d'investissement.
    Sois factuel, cité tes sources quand possible, et utilise des données 2024.""",

    # Livrable attendu — soyez très précis !
    expected_output="""Une analyse structurée de l'entreprise avec :
    - Score d'attractivité de 0 à 10 avec justification
    - 3 à 5 points forts
    - 2 à 4 risques identifiés
    - Une recommandation d'investissement (acheter / attendre / éviter)
    Toutes les données chiffrées doivent être sourcées.""",

    # Agent assigné
    agent=agent_expert,

    # Sortie structurée Pydantic — le LLM génère un JSON validé
    output_pydantic=AnalyseEntreprise,

    # Contexte — résultats d'autres tâches transmis automatiquement
    context=[],  # Sera rempli avec d'autres tâches si nécessaire

    # Callback — appelé quand la tâche se termine
    callback=lambda output: print(f"\n[CALLBACK] Tâche terminée: {output.description[:50]}"),
)
```

### Tâches avec sortie JSON

```python
from crewai import Task

tache_extraction = Task(
    description="""Extrais les entités suivantes du texte ci-dessous :
    - Organisations mentionnées
    - Personnes citées
    - Dates importantes
    - Montants financiers

    Texte : {texte_source}""",

    expected_output="""Un objet JSON valide avec les clés :
    organisations (liste), personnes (liste), dates (liste), montants (liste).""",

    agent=agent_expert,

    # Forcer une sortie JSON valide
    output_json=EntitesExtraites,  # Classe Pydantic pour validation
)

# Accès après exécution
# resultat.json_dict  → dict Python
# resultat.pydantic   → instance Pydantic
```

### Chaîner les tâches avec context

```python
# Pipeline en 3 étapes

tache_collecte = Task(
    description="Collecte des données financières sur {entreprise} pour l'année 2024.",
    expected_output="Données financières brutes : CA, résultat net, dette, effectifs.",
    agent=agent_collecteur
)

tache_analyse = Task(
    description="""Analyse les données financières collectées.
    Calcule les ratios clés : marge nette, ROE, ratio d'endettement.
    Compare avec les moyennes du secteur.""",
    expected_output="Tableau des ratios avec comparaison sectorielle.",
    agent=agent_analyste,
    context=[tache_collecte]  # Reçoit automatiquement le résultat de tache_collecte
)

tache_rapport = Task(
    description="""Rédige un rapport d'investissement basé sur l'analyse.
    Inclure : résumé exécutif, analyse détaillée, recommandation.""",
    expected_output="Rapport professionnel en markdown, 600-800 mots.",
    agent=agent_redacteur,
    context=[tache_collecte, tache_analyse]  # Reçoit les deux résultats précédents
)
```

---

## Exemple concret : pipeline d'analyse d'article

```python
# pipeline_analyse_article.py
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# ---- Modèles Pydantic pour sorties structurées ----
class EntitesArticle(BaseModel):
    titre: str
    auteur: str
    date_publication: str
    themes_principaux: List[str]
    technologies_mentionnees: List[str]
    sentiment: str  # positif / neutre / négatif / mixte

class SyntheseArticle(BaseModel):
    resume_court: str       # 1 phrase
    points_cles: List[str]  # 3-5 points
    public_cible: str
    niveau_technique: str   # débutant / intermédiaire / avancé
    recommandation: str     # "À lire si..." ou "Passer si..."

# ---- Agents ----
agent_lecteur = Agent(
    role="Lecteur et Extracteur d'Information",
    goal="Extraire avec précision toutes les informations structurées d'un article",
    backstory="""Tu es spécialisé dans l'analyse de contenu textuel.
    Tu identifies les entités nommées, les thèmes et les informations factuelles
    avec une précision chirurgicale. Tu ne fais pas de suppositions.""",
    llm=llm,
    verbose=True
)

agent_synthétiseur = Agent(
    role="Synthétiseur et Éditeur",
    goal="Transformer des informations brutes en synthèses utiles et actionnables",
    backstory="""Expert en communication professionnelle, tu excelles à condenser
    l'information complexe en messages clairs. Tu adaptes ton discours au public cible
    et tu hiérarchises l'information par importance.""",
    llm=llm,
    verbose=True
)

agent_evaluateur = Agent(
    role="Évaluateur de Qualité et Critique",
    goal="Évaluer objectivement la qualité et la pertinence du contenu",
    backstory="""Ancien rédacteur en chef d'une revue technique, tu as développé
    un sens critique acéré. Tu évalues la rigueur factuelle, la clarté de l'argumentation,
    et la valeur ajoutée pour le lecteur. Tu n'es pas complaisant.""",
    llm=llm,
    verbose=True
)

# ---- Tâches ----
article_exemple = """
Titre : "GPT-4o : Une Architecture Multimodale Révolutionnaire"
Auteur : Jean-Paul Martin
Date : 15 mars 2024

OpenAI a dévoilé GPT-4o (prononcé "omni"), un modèle fondamentalement différent
de ses prédécesseurs. Contrairement aux systèmes précédents qui traitaient text,
image et audio séparément via des pipelines distincts, GPT-4o intègre ces modalités
dans un seul modèle de bout en bout.

Les benchmarks publiés montrent des performances supérieures à GPT-4 Turbo sur les
tâches de raisonnement, avec une latence réduite de 320ms en moyenne pour les
réponses audio — proche du temps de réaction humain naturel (200-300ms).

La grande innovation : le modèle "voit" et "entend" directement, sans transcrire
d'abord en texte. Cela permet des nuances émotionnelles dans la voix, la détection
d'expressions faciales en temps réel, et une cohérence multimodale inédite.

Cependant, des chercheurs en sécurité IA notent que cette intégration profonde
des modalités crée de nouveaux vecteurs d'attaque adversariaux, notamment via
des instructions cachées dans les images (prompt injection visuelle).
"""

tache_extraction = Task(
    description=f"""Analyse cet article et extrait toutes les informations structurées.

    Article :
    {article_exemple}

    Extrais rigoureusement :
    - Le titre exact
    - L'auteur
    - La date de publication
    - Les 3-5 thèmes principaux
    - Les technologies/produits mentionnés
    - Le sentiment général (positif / neutre / négatif / mixte)""",

    expected_output="""Un objet structuré avec titre, auteur, date,
    liste de thèmes, liste de technologies, et sentiment.
    Sois factuel — n'invente rien qui n'est pas dans l'article.""",

    output_pydantic=EntitesArticle,
    agent=agent_lecteur
)

tache_synthese = Task(
    description="""À partir de l'extraction réalisée, produis une synthèse utile.

    Tu dois déterminer :
    - Un résumé en une seule phrase percutante
    - Les 3 à 5 points vraiment importants (pas juste une répétition)
    - Le public qui bénéficierait le plus de cet article
    - Le niveau technique requis pour comprendre l'article
    - Une recommandation honnête : qui devrait le lire et pourquoi""",

    expected_output="""Une synthèse structurée avec résumé, points clés,
    profil du lecteur idéal, niveau requis, et recommandation de lecture.""",

    output_pydantic=SyntheseArticle,
    agent=agent_synthétiseur,
    context=[tache_extraction]  # Utilise l'extraction précédente
)

tache_evaluation = Task(
    description="""En t'appuyant sur l'extraction et la synthèse effectuées,
    évalue cet article selon ces critères :

    1. Rigueur factuelle (1-5) : les affirmations sont-elles vérifiables ?
    2. Clarté (1-5) : l'article est-il bien structuré et lisible ?
    3. Valeur informative (1-5) : apporte-t-il quelque chose de nouveau ?
    4. Biais détectés : y a-t-il des biais éditoriaux apparents ?

    Formule une note globale /20 avec justification.""",

    expected_output="""Un rapport d'évaluation avec :
    - 4 scores critériés avec justification de 1-2 phrases chacun
    - Les biais détectés (ou 'Aucun biais majeur détecté')
    - Note globale /20 avec résumé de l'évaluation en 2-3 phrases""",

    agent=agent_evaluateur,
    context=[tache_extraction, tache_synthese]
)

# ---- Crew ----
crew_analyse = Crew(
    agents=[agent_lecteur, agent_synthétiseur, agent_evaluateur],
    tasks=[tache_extraction, tache_synthese, tache_evaluation],
    process=Process.sequential,
    verbose=True
)

# ---- Exécution ----
print("Démarrage de l'analyse d'article...\n")
resultat = crew_analyse.kickoff()

# Accès aux résultats structurés
print("\n" + "="*60)
print("RÉSULTATS STRUCTURÉS")
print("="*60)

# Résultat de la tâche 1 (Pydantic)
if tache_extraction.output and tache_extraction.output.pydantic:
    entites = tache_extraction.output.pydantic
    print(f"\nThèmes identifiés : {entites.themes_principaux}")
    print(f"Technologies : {entites.technologies_mentionnees}")
    print(f"Sentiment : {entites.sentiment}")

# Résultat de la tâche 2 (Pydantic)
if tache_synthese.output and tache_synthese.output.pydantic:
    synthese = tache_synthese.output.pydantic
    print(f"\nRésumé : {synthese.resume_court}")
    print(f"Public cible : {synthese.public_cible}")
    print(f"Recommandation : {synthese.recommandation}")

# Résultat final (tâche 3 — texte brut)
print(f"\n{'='*60}")
print("ÉVALUATION FINALE :")
print(resultat.raw)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'exécution de `pipeline_analyse_article.py` avec `verbose=True`, en particulier le moment où l'agent `synthétiseur` utilise explicitement les résultats de l'agent `lecteur` dans son raisonnement (visible dans le Thought: ...). Afficher aussi les résultats Pydantic structurés à la fin.
> **Expliquer :** Pointer le mécanisme `context=[tache_extraction]` — CrewAI injecte automatiquement le résultat de la tâche précédente dans le prompt de la tâche suivante. C'est la "mémoire" entre tâches. Montrer aussi la validation Pydantic qui garantit le format de sortie.

---

## Délégation entre agents

Quand `allow_delegation=True`, un agent peut demander de l'aide à un autre :

```python
# Démo délégation
agent_generaliste = Agent(
    role="Chef de Projet",
    goal="Coordonner et produire des livrables de qualité",
    backstory="Coordinateur expérimenté qui sait déléguer aux bons experts.",
    llm=llm,
    verbose=True,
    allow_delegation=True  # Peut déléguer
)

agent_specialiste_data = Agent(
    role="Data Scientist",
    goal="Analyser des données et produire des insights statistiques",
    backstory="Expert en statistiques et machine learning.",
    llm=llm,
    verbose=True,
    allow_delegation=False  # Ne délègue pas — exécute
)

# Dans un crew avec les deux agents, le chef de projet peut déléguer
# une analyse statistique au data scientist automatiquement
crew_avec_delegation = Crew(
    agents=[agent_generaliste, agent_specialiste_data],
    tasks=[tache_complexe],  # Assignée au chef de projet
    process=Process.sequential
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dans le terminal avec `verbose=True`, le moment où un agent avec `allow_delegation=True` émet une action "Delegate work to coworker" avec le nom de l'agent délégué et les instructions — visible dans le flux de raisonnement ReAct.
> **Expliquer :** La délégation est un outil interne de CrewAI — l'agent principal appelle un "outil" spécial qui transfère la sous-tâche à un autre agent. C'est automatique, le développeur n'a rien à programmer. Attention : peut créer des boucles si mal configuré — en général, préférer une orchestration explicite via les tâches et le context.

---

## Callbacks et monitoring

```python
from crewai.tasks.task_output import TaskOutput

def on_task_complete(output: TaskOutput):
    """Callback appelé après chaque tâche."""
    print(f"\n[MONITORING] Tâche terminée")
    print(f"  Description : {output.description[:60]}...")
    print(f"  Agent : {output.agent}")
    print(f"  Longueur sortie : {len(output.raw)} caractères")
    # En production : logger dans un fichier, envoyer une notification, etc.

tache_avec_callback = Task(
    description="...",
    expected_output="...",
    agent=mon_agent,
    callback=on_task_complete
)
```

---

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** L'accès aux résultats Pydantic après `crew.kickoff()` — montrer `tache_extraction.output.pydantic.themes_principaux` et `tache_synthese.output.pydantic.recommandation` pour illustrer qu'on obtient des objets Python typés, pas du texte brut.
> **Expliquer :** `output_pydantic` est l'une des features les plus précieuses de CrewAI pour la production. Sans elle, le LLM peut retourner du texte qui ressemble à du JSON mais n'est pas parsable. Avec Pydantic, la validation est automatique — si le LLM ne respecte pas le format, CrewAI le force à recommencer (max_retries implicite).

---

## Bonnes pratiques

### Concevoir de bons agents

```python
# ✓ Role précis — un domaine d'expertise clair
bon_role = "Analyste en Cybersécurité spécialisé OWASP Top 10"

# ✗ Role trop vague
mauvais_role = "Expert"

# ✓ Goal actionnable et mesurable
bon_goal = "Identifier toutes les vulnérabilités OWASP dans le code fourni et proposer des correctifs concrets"

# ✗ Goal vague
mauvais_goal = "Faire du bon travail"
```

### Concevoir de bonnes tâches

```python
# ✓ Description avec contexte + contraintes + format implicite
bonne_description = """Analyse ce code Python pour les vulnérabilités de sécurité.

Code :
{code}

Cherche particulièrement :
- Injections SQL
- XSS potentielles
- Secrets en dur
- Dépendances avec CVE connus

Pour chaque vulnérabilité trouvée, fournis : localisation (ligne), description, niveau de sévérité (critique/haute/moyenne/faible), et correctif proposé."""

# ✓ Expected output spécifique et vérifiable
bon_expected_output = """Une liste numérotée de vulnérabilités, chacune avec :
[numéro] [SÉVÉRITÉ] - Ligne X : Description de la vulnérabilité
Correctif : Code corrigé ou recommandation précise.
Si aucune vulnérabilité trouvée : confirmer explicitement "Aucune vulnérabilité détectée."
```

---

## Points clés à retenir

1. La qualité du `backstory` détermine la **cohérence comportementale** de l'agent
2. Le `goal` doit être **actionnable** et refléter le rôle dans l'équipe
3. `expected_output` précis = moins d'hallucinations et de dérives de format
4. `output_pydantic` garantit une **sortie structurée et validée** — indispensable en prod
5. `context=[autres_taches]` est le mécanisme de **transmission de résultats** entre tâches
6. `allow_delegation=True` permet à un agent de **sous-traiter** à ses collègues
7. Les `callback` permettent de **monitorer** l'exécution sans modifier la logique

---

## Suite

Passez à `03-tools.md` pour apprendre à donner des capacités concrètes aux agents (recherche web, lecture de fichiers, APIs).
