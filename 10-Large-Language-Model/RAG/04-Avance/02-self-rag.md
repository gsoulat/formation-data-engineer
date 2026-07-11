# 02 — Self-RAG et Corrective RAG

## Au-delà du RAG naïf

Le RAG standard a un problème fondamental : il récupère toujours des documents, même quand ce n'est pas nécessaire, et n'évalue jamais la qualité de ce qu'il récupère. Deux patterns avancés adressent ce problème :

- **Self-RAG** : le LLM décide lui-même s'il a besoin de retrieval, évalue la pertinence des chunks récupérés, et contrôle la qualité de sa propre réponse
- **Corrective RAG (CRAG)** : après un premier retrieval, si les chunks sont insuffisants, le système effectue une recherche web complémentaire

---

## Self-RAG — principes

Le papier original Self-RAG (Asai et al., 2023) définit quatre types de tokens de réflexion :

| Token | Signification |
|-------|--------------|
| `[Retrieve]` | Décider si un retrieval est nécessaire |
| `[ISREL]` | Ce chunk est-il pertinent pour la question ? |
| `[ISSUP]` | La réponse est-elle supportée par ce chunk ? |
| `[ISUSE]` | La réponse finale est-elle utile ? |

En pratique avec LangChain, on implémente ces décisions via des chaînes de classification.

---

## 1. Décision de retrieval — est-ce nécessaire ?

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class DecisionRetrieval(BaseModel):
    besoin_retrieval: bool = Field(
        description="True si la question nécessite une recherche documentaire"
    )
    justification: str = Field(description="Raison de la décision")

parser_decision = JsonOutputParser(pydantic_object=DecisionRetrieval)

PROMPT_DECISION = ChatPromptTemplate.from_messages([
    ("system", """Détermine si la question nécessite une recherche dans une base documentaire.

Une recherche est NÉCESSAIRE si la question :
- Porte sur des faits spécifiques à l'entreprise ou au produit
- Nécessite des informations récentes ou privées
- Demande des détails procéduraux (comment faire X ?)

Une recherche est INUTILE si la question :
- Est une salutation ou conversation générale
- Porte sur des connaissances générales et universelles
- A déjà été répondue dans l'historique récent

{format_instructions}"""),
    ("human", "Question : {question}")
]).partial(format_instructions=parser_decision.get_format_instructions())

chaine_decision = PROMPT_DECISION | llm | parser_decision

# Tests
questions_tests = [
    "Bonjour, comment ça va ?",
    "Quelle est la politique de retour de 30 jours ?",
    "Qu'est-ce que Python ?",
    "Comment activer ma garantie pour la commande #12345 ?",
]

for q in questions_tests:
    d = chaine_decision.invoke({"question": q})
    print(f"{'[RETRIEVAL]' if d['besoin_retrieval'] else '[NO RETRIEVAL]'} {q}")
```

---

## 2. Évaluation de pertinence des chunks

```python
class EvaluationPertinence(BaseModel):
    est_pertinent: bool = Field(
        description="True si le document est pertinent pour répondre à la question"
    )
    score: float = Field(description="Score de pertinence entre 0.0 et 1.0")
    explication: str = Field(description="Pourquoi le document est ou n'est pas pertinent")

parser_pertinence = JsonOutputParser(pydantic_object=EvaluationPertinence)

PROMPT_PERTINENCE = ChatPromptTemplate.from_messages([
    ("system", """Évalue si le document fourni contient des informations pertinentes
pour répondre à la question posée.

Un document est pertinent s'il contient des informations qui aident à répondre,
même partiellement, à la question.

{format_instructions}"""),
    ("human", "Question : {question}\n\nDocument : {document}")
]).partial(format_instructions=parser_pertinence.get_format_instructions())

chaine_pertinence = PROMPT_PERTINENCE | llm | parser_pertinence

def filtrer_chunks_pertinents(question: str, docs, seuil: float = 0.5):
    """Filtre les chunks selon leur pertinence évaluée par le LLM."""
    chunks_pertinents = []
    chunks_non_pertinents = []

    for doc in docs:
        eval_result = chaine_pertinence.invoke({
            "question": question,
            "document": doc.page_content[:500]  # Limiter pour économiser les tokens
        })

        if eval_result["est_pertinent"] and eval_result["score"] >= seuil:
            chunks_pertinents.append(doc)
        else:
            chunks_non_pertinents.append(doc)

    print(f"Chunks pertinents : {len(chunks_pertinents)}/{len(docs)}")
    return chunks_pertinents, chunks_non_pertinents
```

---

## 3. Self-RAG complet — pipeline de décision

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.documents import Document
from typing import List, Optional

# Setup
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prompt de génération RAG
PROMPT_GENERATION = ChatPromptTemplate.from_messages([
    ("system", """Réponds à la question en te basant sur le contexte.
Si l'information est absente, dis-le.

Contexte :
{context}"""),
    ("human", "{question}")
])

# Prompt de génération sans retrieval
PROMPT_DIRECT = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant utile. Réponds de façon concise et honnête."),
    ("human", "{question}")
])

parser = StrOutputParser()


def self_rag_pipeline(question: str, verbose: bool = True) -> dict:
    """
    Pipeline Self-RAG complet :
    1. Décider si retrieval nécessaire
    2. Si oui : récupérer + filtrer + générer avec contexte
    3. Si non : générer directement
    """
    # Étape 1 : Décision de retrieval
    decision = chaine_decision.invoke({"question": question})

    if verbose:
        action = "RETRIEVAL" if decision["besoin_retrieval"] else "DIRECT"
        print(f"[Décision] {action} — {decision['justification']}")

    if not decision["besoin_retrieval"]:
        # Réponse directe sans retrieval
        chain_direct = PROMPT_DIRECT | llm | parser
        reponse = chain_direct.invoke({"question": question})
        return {
            "reponse": reponse,
            "mode": "direct",
            "chunks_utilises": [],
        }

    # Étape 2 : Retrieval
    docs_candidats = retriever.invoke(question)
    if verbose:
        print(f"[Retrieval] {len(docs_candidats)} chunks candidats récupérés")

    # Étape 3 : Filtrage des chunks non pertinents
    docs_pertinents, docs_rejetes = filtrer_chunks_pertinents(question, docs_candidats)
    if verbose:
        print(f"[Filtrage] {len(docs_pertinents)} pertinents, {len(docs_rejetes)} rejetés")

    if not docs_pertinents:
        # Aucun chunk pertinent trouvé
        return {
            "reponse": "Je ne trouve pas d'information pertinente sur ce sujet dans la documentation.",
            "mode": "no_relevant_docs",
            "chunks_utilises": [],
        }

    # Étape 4 : Génération avec les chunks pertinents
    context = "\n\n---\n\n".join(
        f"[Source : {doc.metadata.get('source', '?')}, p.{doc.metadata.get('page', '?')}]\n"
        f"{doc.page_content}"
        for doc in docs_pertinents
    )

    chain_rag = PROMPT_GENERATION | llm | parser
    reponse = chain_rag.invoke({"context": context, "question": question})

    return {
        "reponse": reponse,
        "mode": "rag",
        "chunks_utilises": docs_pertinents,
    }


# Démonstration
questions = [
    "Bonjour !",
    "Quelle est la durée de garantie ?",
    "La garantie couvre-t-elle les dommages accidentels ?",
    "Quelle est la formule chimique de l'eau ?",
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"Question : {q}")
    resultat = self_rag_pipeline(q)
    print(f"Mode : {resultat['mode']}")
    print(f"Réponse : {resultat['reponse']}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution du pipeline Self-RAG sur les 4 questions — montrer les logs de décision ([Décision] DIRECT vs RETRIEVAL) et les modes retournés
> **Expliquer :** Montrer que "Bonjour !" déclenche le mode DIRECT (pas de retrieval, réponse immédiate), "Quelle est la durée de garantie ?" déclenche le RETRIEVAL avec filtrage, et "formule chimique de l'eau" déclenche DIRECT. Insister sur l'économie de tokens : les questions simples n'appelle pas du tout le retriever. En production sur 1000 questions/jour, cela peut représenter une économie significative.

---

## 4. Corrective RAG (CRAG)

CRAG ajoute une étape de recherche web complémentaire quand le retrieval interne est insuffisant.

```python
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.documents import Document

# Outil de recherche web
search_tool = DuckDuckGoSearchRun()

class DecisionQualiteRetrieval(BaseModel):
    qualite: str = Field(description="'suffisant', 'partiel', ou 'insuffisant'")
    score: float = Field(description="Score de qualité entre 0.0 et 1.0")
    explication: str

parser_qualite = JsonOutputParser(pydantic_object=DecisionQualiteRetrieval)

PROMPT_QUALITE = ChatPromptTemplate.from_messages([
    ("system", """Évalue si les documents récupérés sont suffisants pour répondre à la question.

- 'suffisant' (>0.7) : les documents contiennent toutes les informations nécessaires
- 'partiel' (0.4-0.7) : les documents contiennent des informations partielles
- 'insuffisant' (<0.4) : les documents ne permettent pas de répondre à la question

{format_instructions}"""),
    ("human", "Question : {question}\n\nDocuments récupérés :\n{contexte}")
]).partial(format_instructions=parser_qualite.get_format_instructions())

chaine_qualite = PROMPT_QUALITE | llm | parser_qualite


def corrective_rag_pipeline(question: str, verbose: bool = True) -> dict:
    """
    Corrective RAG :
    1. Retrieval interne
    2. Évaluation de la qualité
    3. Si insuffisant → recherche web
    4. Génération avec les meilleures sources
    """
    # Étape 1 : Retrieval interne
    docs_internes = retriever.invoke(question)
    contexte_interne = "\n\n".join(d.page_content[:300] for d in docs_internes)

    # Étape 2 : Évaluation de la qualité
    evaluation = chaine_qualite.invoke({
        "question": question,
        "contexte": contexte_interne,
    })

    if verbose:
        print(f"[Qualité retrieval] {evaluation['qualite']} (score: {evaluation['score']:.2f})")
        print(f"  → {evaluation['explication']}")

    docs_finaux = docs_internes.copy()
    sources_web = []

    # Étape 3 : Recherche web si nécessaire
    if evaluation["qualite"] in ("partiel", "insuffisant"):
        if verbose:
            print(f"[CRAG] Déclenchement de la recherche web complémentaire...")

        try:
            resultats_web = search_tool.run(question)
            doc_web = Document(
                page_content=resultats_web,
                metadata={"source": "web_search", "type": "web"}
            )
            sources_web = [doc_web]

            if evaluation["qualite"] == "insuffisant":
                # Si vraiment insuffisant, n'utiliser que le web
                docs_finaux = [doc_web]
                if verbose:
                    print("[CRAG] Sources internes abandonnées — utilisation du web uniquement")
            else:
                # Si partiel, combiner interne + web
                docs_finaux = docs_internes + [doc_web]
                if verbose:
                    print("[CRAG] Sources internes + web combinées")
        except Exception as e:
            if verbose:
                print(f"[CRAG] Erreur recherche web : {e} — utilisation des sources internes uniquement")

    # Étape 4 : Génération
    context = "\n\n---\n\n".join(
        f"[{doc.metadata.get('type', 'doc')}: {doc.metadata.get('source', '?')}]\n{doc.page_content}"
        for doc in docs_finaux
    )

    chain = PROMPT_GENERATION | llm | parser
    reponse = chain.invoke({"context": context, "question": question})

    return {
        "reponse": reponse,
        "qualite_retrieval": evaluation["qualite"],
        "sources_internes": len(docs_internes),
        "sources_web": len(sources_web),
        "docs_utilises": docs_finaux,
    }
```

---

## 5. Adaptive RAG — routing intelligent

Un pattern encore plus avancé : router la question vers la meilleure stratégie de retrieval selon le type de question.

```python
from typing import Literal

class StrategieRetrieval(BaseModel):
    strategie: Literal["vectorstore", "web_search", "direct", "hybrid"] = Field(
        description="Stratégie de retrieval optimale"
    )
    justification: str

parser_strategie = JsonOutputParser(pydantic_object=StrategieRetrieval)

PROMPT_ROUTING = ChatPromptTemplate.from_messages([
    ("system", """Tu es un routeur de questions pour un système RAG.

Choisis la stratégie optimale :
- 'vectorstore' : question sur la documentation interne (produits, services, politiques)
- 'web_search' : question sur des événements récents ou des faits généraux récents
- 'direct' : question ne nécessitant pas de recherche (salutations, maths, notions générales stables)
- 'hybrid' : question mixant interne + externe

{format_instructions}"""),
    ("human", "Question : {question}")
]).partial(format_instructions=parser_strategie.get_format_instructions())

chaine_routing = PROMPT_ROUTING | llm | parser_strategie


def adaptive_rag(question: str, verbose: bool = True) -> str:
    """Adaptive RAG : choisit la stratégie selon la question."""
    routing = chaine_routing.invoke({"question": question})

    if verbose:
        print(f"[Routing] Stratégie : {routing['strategie']}")

    if routing["strategie"] == "direct":
        chain = PROMPT_DIRECT | llm | parser
        return chain.invoke({"question": question})

    elif routing["strategie"] == "vectorstore":
        docs = retriever.invoke(question)
        context = "\n\n".join(d.page_content for d in docs)
        chain = PROMPT_GENERATION | llm | parser
        return chain.invoke({"context": context, "question": question})

    elif routing["strategie"] == "web_search":
        resultats = search_tool.run(question)
        context = f"[Résultats web]\n{resultats}"
        chain = PROMPT_GENERATION | llm | parser
        return chain.invoke({"context": context, "question": question})

    elif routing["strategie"] == "hybrid":
        docs = retriever.invoke(question)
        web_result = search_tool.run(question)
        context = (
            "\n\n".join(d.page_content for d in docs)
            + f"\n\n[Résultats web]\n{web_result}"
        )
        chain = PROMPT_GENERATION | llm | parser
        return chain.invoke({"context": context, "question": question})
```

---

## 6. Résumé des patterns avancés

```
RAG Standard
├── Avantages  : Simple, rapide, fiable
└── Limites    : Toujours retrieve, ne filtre pas les chunks non pertinents

Self-RAG
├── Avantages  : Évite les retrieval inutiles, filtre les chunks
└── Limites    : Plus lent (décisions LLM), plus cher

Corrective RAG
├── Avantages  : Filet de sécurité web si la KB est insuffisante
└── Limites    : Dépendance web, latence élevée

Adaptive RAG
├── Avantages  : Optimal pour chaque type de question
└── Limites    : Complexité accrue, maintenance du routeur
```

**Recommandations :**
- **Prototype/MVP** → RAG Standard
- **Production avec questions variées** → Self-RAG (décision de retrieval)
- **KB potentiellement incomplète** → Corrective RAG
- **Système multi-sources** → Adaptive RAG

---

## Récapitulatif

| Pattern | Décision clé | Complexité | Coût |
|---------|-------------|------------|------|
| RAG Standard | Toujours retrieve | Faible | Faible |
| Self-RAG | Retrieve si nécessaire + filtre chunks | Élevé | Moyen |
| Corrective RAG | Fallback web si KB insuffisante | Moyen | Moyen |
| Adaptive RAG | Router vers la meilleure stratégie | Très élevé | Élevé |

Retour au début : [Concepts/01-introduction-rag.md](../Concepts/01-introduction-rag.md)
Passer aux exercices : [exercices/exercice-01-rag-documents.md](../exercices/exercice-01-rag-documents.md)
