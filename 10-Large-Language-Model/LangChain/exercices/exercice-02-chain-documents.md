# Exercice 02 — Chaîne d'Analyse de Documents

## Objectif

Construire une chaîne LCEL qui analyse des documents texte et produit des sorties structurées. L'application devra :

- Charger et découper des documents en chunks
- Extraire des informations structurées (résumé, entités, sentiment, points clés)
- Comparer plusieurs documents entre eux
- Exporter les résultats en JSON

**Durée estimée :** 60 minutes
**Niveau :** Intermédiaire
**Prérequis :** Modules 01, 02, 04

---

## Contexte

Vous êtes data engineer dans une entreprise qui reçoit des rapports quotidiens de ses équipes commerciales. Ces rapports sont en texte libre et vous devez les analyser automatiquement pour alimenter un dashboard de management.

---

## Documents de travail

Utilisez ces rapports fictifs pour les exercices :

```python
# documents.py — données de démo
RAPPORTS = {
    "rapport_nord": """
    Rapport commercial — Région Nord — Semaine 42

    Cette semaine a été particulièrement productive pour notre équipe de 8 commerciaux.
    Nous avons réalisé 45 visites clients et signé 12 nouveaux contrats représentant
    un chiffre d'affaires de 187 000 euros.

    Points positifs : L'ouverture du nouveau bureau de Lille a généré 3 contrats
    dès la première semaine. Le secteur industriel continue de performer avec
    une croissance de 23% par rapport au même trimestre l'année dernière.

    Difficultés rencontrées : Le secteur retail est en ralentissement. Plusieurs
    clients historiques ont reporté leurs décisions d'achat au Q1 prochain.
    La concurrence de notre principal concurrent, TechPro, s'intensifie sur les
    contrats supérieurs à 50 000 euros.

    Objectifs semaine prochaine : Finaliser 5 propositions commerciales en attente,
    former 2 nouveaux commerciaux sur notre gamme premium, et organiser une
    journée portes ouvertes clients le jeudi 24 octobre.
    """,

    "rapport_sud": """
    Rapport commercial — Région Sud — Semaine 42

    La région Sud traverse une période de transformation. Suite au départ de
    3 commerciaux expérimentés en septembre, nous reconstruisons notre équipe
    avec 2 nouvelles recrues encore en formation.

    Résultats de la semaine : 28 visites clients, 6 nouveaux contrats pour
    un CA de 94 000 euros. Ces chiffres sont en dessous de nos objectifs
    habituels mais s'expliquent par la période de transition.

    Point positif notable : Le partenariat signé avec le distributeur MedSud
    ouvre l'accès à 150 nouveaux prospects dans le secteur médical.
    Les premiers rendez-vous sont très prometteurs.

    Actions correctives en cours : Accélération du programme de formation,
    mise en place d'un système de mentorat avec les commerciaux seniors de
    la région Nord, et révision de notre stratégie de prospection sur la
    Côte d'Azur.

    Prévisions : Retour à la normale prévu pour la semaine 46 avec l'arrivée
    d'une commerciale senior qui rejoint depuis la concurrence.
    """,

    "rapport_est": """
    Rapport commercial — Région Est — Semaine 42

    Excellente semaine pour la région Est ! Nous avons dépassé nos objectifs
    trimestriels avec une semaine d'avance.

    Résultats exceptionnels : 52 visites clients, 18 contrats signés pour
    un CA record de 312 000 euros. Le méga-contrat avec le Groupe Alsatec
    (180 000 euros sur 3 ans) est la principale réussite de la semaine.

    Facteurs de succès : Notre approche consultative, développée ces 6 derniers
    mois, porte ses fruits. Les clients apprécient particulièrement nos
    démonstrations personnalisées et notre support technique réactif.

    Équipe : Félicitations à Jean-Marc Hubert pour son 3ème contrat >100k€
    cette année, et à toute l'équipe pour sa mobilisation exceptionnelle.

    Vigilance : Surveiller de près la situation avec 2 clients importants qui
    ont des difficultés financières. Mettre en place des paiements échelonnés
    pour sécuriser les créances.
    """,
}
```

---

## Partie 1 — Extraction d'informations structurées (25 min)

### Objectif

Créer une chaîne qui extrait des données structurées de chaque rapport.

### Étape 1.1 — Définir le schéma de sortie

```python
# analyse_documents.py
from pydantic import BaseModel, Field
from typing import List, Optional

class RapportAnalyse(BaseModel):
    # TODO : Définir le schéma Pydantic avec les champs suivants :
    region: str = Field(description="Nom de la région")
    semaine: int = Field(description="Numéro de semaine")
    nb_visites: int = Field(description="Nombre de visites clients")
    nb_contrats: int = Field(description="Nombre de contrats signés")
    chiffre_affaires: float = Field(description="CA en euros")
    sentiment_global: str = Field(description="positif, neutre, ou négatif")
    score_performance: int = Field(description="Score de performance de 1 à 10")
    points_positifs: List[str] = Field(description="Liste des éléments positifs mentionnés")
    points_negatifs: List[str] = Field(description="Liste des difficultés ou risques")
    actions_prioritaires: List[str] = Field(description="Actions à mener en priorité")
    resume_executif: str = Field(description="Résumé en une phrase pour le management")
```

### Étape 1.2 — Créer la chaîne d'extraction

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# TODO 1 : Créer l'instance du LLM (temperature=0 pour des extractions déterministes)

# TODO 2 : Créer le parser Pydantic pour RapportAnalyse

# TODO 3 : Créer le prompt avec les instructions de format
PROMPT_EXTRACTION = """Tu es un analyste commercial expert. Analyse ce rapport et
extrait les informations de façon précise et structurée.

Si une information n'est pas explicitement mentionnée, utilise -1 pour les nombres
et "Non spécifié" pour les chaînes.

{format_instructions}

Rapport à analyser :
{rapport}"""

# TODO 4 : Composer la chaîne prompt | llm | parser

# TODO 5 : Analyser les 3 rapports et stocker les résultats
resultats = {}
for nom, texte in RAPPORTS.items():
    print(f"Analyse de {nom}...")
    # TODO : appeler la chaîne et stocker le résultat Pydantic
    pass
```

### Résultat attendu

```python
# Exemple de résultat pour rapport_nord
RapportAnalyse(
    region="Nord",
    semaine=42,
    nb_visites=45,
    nb_contrats=12,
    chiffre_affaires=187000.0,
    sentiment_global="positif",
    score_performance=8,
    points_positifs=["Ouverture bureau Lille", "Croissance secteur industriel +23%"],
    points_negatifs=["Ralentissement retail", "Concurrence TechPro sur gros contrats"],
    actions_prioritaires=["Finaliser 5 propositions", "Former 2 nouveaux commerciaux"],
    resume_executif="Bonne semaine avec 12 contrats et 187k€ de CA malgré des tensions concurrentielles."
)
```

---

## Partie 2 — Traitement en parallèle (15 min)

### Objectif

Utiliser `RunnableParallel` pour générer plusieurs analyses simultanément.

```python
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# Créer 3 chaînes spécialisées

# Chaîne 1 : Résumé exécutif court
prompt_resume = ChatPromptTemplate.from_template(
    "Résume ce rapport commercial en exactement 2 phrases pour un directeur pressé :\n{rapport}"
)

# Chaîne 2 : Identification des risques
prompt_risques = ChatPromptTemplate.from_template(
    """Identifie UNIQUEMENT les risques et points d'attention dans ce rapport.
    Format : liste à puces, maximum 4 points.
    Rapport :\n{rapport}"""
)

# Chaîne 3 : Recommandations d'actions
prompt_actions = ChatPromptTemplate.from_template(
    """Propose 3 actions concrètes basées sur ce rapport.
    Chaque action doit avoir : QUOI faire, POURQUOI, et QUAND (délai).
    Rapport :\n{rapport}"""
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# TODO : Créer une chaîne parallèle qui exécute les 3 analyses simultanément
# et retourne un dict avec les clés "resume", "risques", "actions"

# TODO : Mesurer le temps d'exécution (doit être proche du max des 3 chaînes, pas la somme)
```

---

## Partie 3 — Comparaison de documents (15 min)

### Objectif

Créer une chaîne qui compare plusieurs rapports analysés.

```python
class ComparaisonRegions(BaseModel):
    meilleure_region: str = Field(description="Région avec les meilleures performances")
    region_attention: str = Field(description="Région nécessitant le plus d'attention")
    total_ca: float = Field(description="CA total de toutes les régions")
    total_contrats: int = Field(description="Total des contrats signés")
    tendance_globale: str = Field(description="Tendance générale : croissance, stable, déclin")
    insights_cles: List[str] = Field(description="3 insights clés pour le management")
    recommandation_prioritaire: str = Field(description="Une action prioritaire à mener immédiatement")

def comparer_rapports(analyses: dict) -> ComparaisonRegions:
    """
    TODO : Créer une chaîne qui prend les analyses structurées
    et génère une comparaison globale.

    Hint : convertir les objets Pydantic en dict/JSON pour le prompt
    """
    # Préparer le contexte
    contexte = "\n\n".join([
        f"=== {nom} ===\n{analyse.json(ensure_ascii=False, indent=2)}"
        for nom, analyse in analyses.items()
    ])

    prompt_comparaison = ChatPromptTemplate.from_messages([
        ("system", "Tu es un directeur commercial qui compare les performances de ses régions."),
        ("human", """Voici les analyses de nos 3 régions cette semaine.
        Génère une comparaison globale et des recommandations stratégiques.

        {format_instructions}

        Données des régions :
        {contexte}""")
    ])

    # TODO : Compléter la chaîne et retourner l'objet ComparaisonRegions
    pass
```

---

## Partie 4 — Export et pipeline complet (5 min)

```python
import json
from datetime import datetime

def exporter_rapport_complet(analyses: dict, comparaison: ComparaisonRegions, semaine: int):
    """Exporte toutes les analyses en JSON."""
    rapport_complet = {
        "metadata": {
            "semaine": semaine,
            "date_generation": datetime.now().isoformat(),
            "nb_regions": len(analyses),
        },
        "analyses_par_region": {
            nom: analyse.dict()
            for nom, analyse in analyses.items()
        },
        "synthese_globale": comparaison.dict()
    }

    filename = f"rapport_semaine_{semaine}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(rapport_complet, f, ensure_ascii=False, indent=2)

    print(f"Rapport exporté : {filename}")
    return rapport_complet

# Pipeline complet
def pipeline_analyse_complete():
    """
    TODO : Assembler le pipeline complet :
    1. Analyser chaque rapport (Partie 1)
    2. Générer les analyses parallèles (Partie 2)
    3. Comparer les régions (Partie 3)
    4. Exporter en JSON (Partie 4)
    """
    pass

if __name__ == "__main__":
    pipeline_analyse_complete()
```

---

## Corrigé — Partie 1

```python
# CORRIGÉ Partie 1
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class RapportAnalyse(BaseModel):
    region: str = Field(description="Nom de la région")
    semaine: int = Field(description="Numéro de semaine")
    nb_visites: int = Field(description="Nombre de visites clients")
    nb_contrats: int = Field(description="Nombre de contrats signés")
    chiffre_affaires: float = Field(description="CA en euros")
    sentiment_global: str = Field(description="positif, neutre, ou négatif")
    score_performance: int = Field(description="Score de performance de 1 à 10")
    points_positifs: List[str] = Field(description="Éléments positifs")
    points_negatifs: List[str] = Field(description="Difficultés ou risques")
    actions_prioritaires: List[str] = Field(description="Actions prioritaires")
    resume_executif: str = Field(description="Résumé en une phrase")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = PydanticOutputParser(pydantic_object=RapportAnalyse)

prompt = ChatPromptTemplate.from_template(
    """Tu es un analyste commercial expert. Analyse ce rapport et
extrait les informations précisément.

Si une information n'est pas mentionnée : -1 pour les nombres, "Non spécifié" pour les textes.

{format_instructions}

Rapport :
{rapport}"""
).partial(format_instructions=parser.get_format_instructions())

chaine_extraction = prompt | llm | parser

resultats = {}
for nom, texte in RAPPORTS.items():
    print(f"Analyse de {nom}...", end=" ")
    resultats[nom] = chaine_extraction.invoke({"rapport": texte})
    print(f"✓ ({resultats[nom].nb_contrats} contrats, {resultats[nom].chiffre_affaires}€)")

print("\nRécapitulatif :")
for nom, r in resultats.items():
    print(f"  {r.region}: {r.nb_contrats} contrats | {r.chiffre_affaires:,.0f}€ | Score: {r.score_performance}/10")
```

---

## Points de validation

- [ ] La chaîne extrait correctement les données numériques (CA, contrats, visites)
- [ ] Le schéma Pydantic valide les données (score entre 1-10, sentiment parmi les valeurs acceptées)
- [ ] Les 3 rapports sont analysés et les résultats stockés
- [ ] La comparaison identifie correctement la meilleure et la moins bonne région
- [ ] L'export JSON est lisible et correctement structuré
- [ ] Le pipeline parallèle est plus rapide que 3 appels séquentiels

---

## Aller plus loin

- Ajouter un chargement depuis de vrais fichiers PDF ou Word
- Implémenter un cache pour ne pas re-analyser des rapports déjà traités
- Créer une visualisation des scores avec matplotlib ou plotly
- Connecter le pipeline à une base de données pour historiser les analyses
