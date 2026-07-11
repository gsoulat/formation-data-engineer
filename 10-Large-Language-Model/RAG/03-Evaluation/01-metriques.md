# 01 — Métriques d'Évaluation RAG

## Pourquoi évaluer un système RAG ?

Évaluer un système RAG est fondamentalement différent d'évaluer un modèle de classification classique. Il n'y a pas de label binaire correct/incorrect — la qualité d'une réponse est multidimensionnelle.

Sans évaluation rigoureuse :
- Impossible de savoir si une modification améliore ou dégrade le système
- Impossible de comparer différentes stratégies de retrieval ou de chunking
- Impossible de détecter les régressions en production
- Impossible de justifier les choix techniques à une équipe

---

## Les trois axes d'évaluation RAG

Un système RAG peut être évalué selon trois axes indépendants :

```
                    ┌─────────────────────────────────┐
                    │        QUALITÉ RAG               │
                    │                                   │
    Question ──────►│  Retrieval Quality               │
                    │  (les bons chunks sont-ils        │
                    │   récupérés ?)                    │
                    │                                   │
    Chunks ────────►│  Generation Quality              │
                    │  (la réponse est-elle fidèle      │
                    │   aux chunks ?)                   │
                    │                                   │
    Réponse ────────►│ Answer Quality                  │
    + Question      │  (la réponse répond-elle          │
                    │   bien à la question ?)           │
                    └─────────────────────────────────┘
```

---

## Métrique 1 — Context Recall (qualité du retrieval)

Le Context Recall mesure si les informations nécessaires pour répondre à la question sont présentes dans les chunks récupérés.

**Définition :** Proportion des informations de la réponse de référence qui se trouvent dans le contexte récupéré.

```
Context Recall = (informations de la référence présentes dans le contexte) / (total informations de la référence)
```

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class EvaluationContextRecall(BaseModel):
    claims_reference: List[str] = Field(
        description="Liste des affirmations distinctes dans la réponse de référence"
    )
    claims_trouvees_dans_contexte: List[str] = Field(
        description="Affirmations effectivement présentes dans le contexte"
    )
    score: float = Field(description="Score entre 0.0 et 1.0")
    explication: str = Field(description="Explication du score")

parser = JsonOutputParser(pydantic_object=EvaluationContextRecall)
llm_eval = ChatOpenAI(model="gpt-4o", temperature=0)  # LLM plus puissant pour évaluation

PROMPT_CONTEXT_RECALL = ChatPromptTemplate.from_messages([
    ("system", """Tu évalues la qualité d'un retrieval RAG.

Ta tâche :
1. Extraire toutes les affirmations factuelles de la réponse de référence
2. Vérifier si chaque affirmation est présente (ou peut être déduite) du contexte
3. Calculer le score = affirmations trouvées / affirmations totales

Question : {question}
Réponse de référence : {reference}
Contexte récupéré : {context}

{format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

chain_context_recall = PROMPT_CONTEXT_RECALL | llm_eval | parser

# Exemple d'utilisation
question = "Quelle est la durée de garantie et quelles pièces couvre-t-elle ?"
reference = "La garantie est de 2 ans. Elle couvre les pièces d'origine et la main d'œuvre."
context = "Tout appareil bénéficie d'une garantie constructeur de 24 mois couvrant les défauts de fabrication sur les composants d'origine ainsi que les frais de main d'œuvre."

resultat = chain_context_recall.invoke({
    "question": question,
    "reference": reference,
    "context": context,
})

print(f"Context Recall : {resultat['score']:.2f}")
print(f"Explication : {resultat['explication']}")
```

---

## Métrique 2 — Faithfulness (fidélité au contexte)

La Faithfulness mesure si la réponse générée est fidèle aux chunks fournis, c'est-à-dire l'absence d'hallucinations.

**Définition :** Proportion des affirmations de la réponse qui peuvent être vérifiées dans le contexte.

```
Faithfulness = (affirmations de la réponse vérifiables dans le contexte) / (affirmations totales de la réponse)
```

```python
class EvaluationFaithfulness(BaseModel):
    affirmations_reponse: List[str] = Field(
        description="Liste de toutes les affirmations factuelles dans la réponse"
    )
    affirmations_verifiees: List[str] = Field(
        description="Affirmations qui peuvent être vérifiées dans le contexte"
    )
    affirmations_non_verifiees: List[str] = Field(
        description="Affirmations qui ne peuvent PAS être vérifiées (hallucinations)"
    )
    score: float = Field(description="Score entre 0.0 et 1.0")

parser_faith = JsonOutputParser(pydantic_object=EvaluationFaithfulness)

PROMPT_FAITHFULNESS = ChatPromptTemplate.from_messages([
    ("system", """Tu évalues la fidélité d'une réponse RAG à son contexte source.

Tâche :
1. Extraire chaque affirmation factuelle de la réponse
2. Pour chaque affirmation : vérifier si elle est supportée par le contexte
3. Une affirmation est "supportée" si le contexte contient l'information, même formulée différemment
4. Score = affirmations supportées / total affirmations

Contexte : {context}
Réponse à évaluer : {reponse}

{format_instructions}""")
]).partial(format_instructions=parser_faith.get_format_instructions())

chain_faithfulness = PROMPT_FAITHFULNESS | llm_eval | parser_faith

reponse_test = "La garantie est de 2 ans. Elle couvre aussi les dommages accidentels."
# "dommages accidentels" n'est pas dans le contexte → hallucination

resultat_faith = chain_faithfulness.invoke({
    "context": context,
    "reponse": reponse_test,
})

print(f"Faithfulness : {resultat_faith['score']:.2f}")
print(f"Hallucinations détectées : {resultat_faith['affirmations_non_verifiees']}")
```

---

## Métrique 3 — Answer Relevancy (pertinence de la réponse)

L'Answer Relevancy mesure si la réponse répond bien à la question posée — indépendamment de sa véracité.

**Définition :** Similitude sémantique entre la question originale et des questions synthétiques générées à partir de la réponse.

```python
from langchain_openai import OpenAIEmbeddings
import numpy as np

def calculer_answer_relevancy(
    question: str,
    reponse: str,
    n_questions: int = 3,
) -> float:
    """
    Génère N questions à partir de la réponse,
    puis mesure leur similarité avec la question originale.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Générer des questions synthétiques depuis la réponse
    prompt_gen = ChatPromptTemplate.from_messages([
        ("system", f"""Génère exactement {n_questions} questions différentes auxquelles
cette réponse pourrait répondre. Une question par ligne, sans numérotation."""),
        ("human", "Réponse : {reponse}")
    ])

    from langchain_core.output_parsers import StrOutputParser
    chain_gen = prompt_gen | llm | StrOutputParser()
    questions_generees_str = chain_gen.invoke({"reponse": reponse})
    questions_generees = [q.strip() for q in questions_generees_str.strip().split("\n") if q.strip()]

    # Calculer la similarité cosinus entre la question originale et les questions générées
    vecteur_question = embeddings.embed_query(question)
    vecteurs_gen = embeddings.embed_documents(questions_generees)

    def cosinus(a, b):
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    similarites = [cosinus(vecteur_question, v) for v in vecteurs_gen]
    score = float(np.mean(similarites))

    print(f"Questions générées depuis la réponse :")
    for q in questions_generees:
        print(f"  - {q}")
    print(f"Answer Relevancy : {score:.3f}")
    return score


# Test
question = "Quelles sont les conditions de garantie ?"
bonne_reponse = "La garantie couvre 2 ans les pièces et la main d'œuvre."
mauvaise_reponse = "Le service client est disponible du lundi au vendredi de 9h à 18h."

print("=== Bonne réponse ===")
score_bon = calculer_answer_relevancy(question, bonne_reponse)

print("\n=== Mauvaise réponse (hors-sujet) ===")
score_mauvais = calculer_answer_relevancy(question, mauvaise_reponse)
```

---

## Métrique 4 — Context Precision

La Context Precision mesure si les chunks récupérés sont tous utiles, ou s'il y a du "bruit".

**Définition :** Proportion des chunks récupérés qui sont effectivement pertinents pour la question.

```python
class EvaluationChunk(BaseModel):
    chunk_id: int
    est_pertinent: bool
    justification: str

class EvaluationContextPrecision(BaseModel):
    evaluations: List[EvaluationChunk]
    score: float
    chunks_non_pertinents: List[int]

parser_precision = JsonOutputParser(pydantic_object=EvaluationContextPrecision)

PROMPT_CONTEXT_PRECISION = ChatPromptTemplate.from_messages([
    ("system", """Tu évalues la précision des résultats de retrieval d'un système RAG.

Pour chaque chunk numéroté, détermine s'il est pertinent pour répondre à la question.
Un chunk est pertinent s'il contient des informations utiles pour répondre à la question.

Question : {question}
Chunks récupérés :
{chunks_numerotes}

Score = chunks pertinents / total chunks

{format_instructions}""")
]).partial(format_instructions=parser_precision.get_format_instructions())

def evaluer_context_precision(question: str, docs) -> dict:
    """Évalue si les chunks récupérés sont tous pertinents."""
    chunks_numerotes = "\n\n".join(
        f"[Chunk {i+1}]\n{doc.page_content[:300]}"
        for i, doc in enumerate(docs)
    )

    chain = PROMPT_CONTEXT_PRECISION | llm_eval | parser_precision
    return chain.invoke({
        "question": question,
        "chunks_numerotes": chunks_numerotes,
    })
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Tableau récapitulatif des 4 métriques calculées sur le même exemple — afficher les scores pour une bonne réponse vs une réponse avec hallucination
> **Expliquer :** Construire manuellement deux scénarios : (1) un RAG qui fonctionne bien — tous les scores sont élevés, (2) un RAG avec hallucination — Faithfulness chute mais Context Recall reste élevé. Montrer que les métriques permettent de diagnostiquer précisément quel composant du pipeline pose problème.

---

## Évaluation end-to-end sur un jeu de test

```python
from typing import List, Dict
import json

def evaluer_rag_complet(
    rag_chain,
    retriever,
    jeu_de_test: List[Dict],
) -> Dict:
    """
    Évalue un pipeline RAG sur un jeu de test.

    jeu_de_test : liste de dicts avec les clés :
        - question : str
        - reponse_reference : str (réponse attendue de référence)
    """
    resultats = []

    for item in jeu_de_test:
        question = item["question"]
        reference = item["reponse_reference"]

        # Récupérer les chunks
        docs = retriever.invoke(question)
        context = "\n\n".join(doc.page_content for doc in docs)

        # Générer la réponse
        reponse = rag_chain.invoke(question)

        # Calculer les métriques
        # (simplifiées pour l'exemple — RAGAS les calcule automatiquement)
        faithfulness_result = chain_faithfulness.invoke({
            "context": context,
            "reponse": reponse,
        })

        resultats.append({
            "question": question,
            "reponse_generee": reponse,
            "reponse_reference": reference,
            "faithfulness": faithfulness_result["score"],
            "nb_chunks": len(docs),
        })

    # Calculer les moyennes
    scores = {
        "faithfulness_mean": sum(r["faithfulness"] for r in resultats) / len(resultats),
        "nb_questions": len(resultats),
    }

    print("\n=== Rapport d'évaluation ===")
    print(f"Questions testées : {scores['nb_questions']}")
    print(f"Faithfulness moyen : {scores['faithfulness_mean']:.2%}")

    return {"scores": scores, "details": resultats}


# Jeu de test minimal
JEU_TEST = [
    {
        "question": "Quelle est la durée de garantie ?",
        "reponse_reference": "La garantie est de 2 ans sur les pièces et la main d'œuvre."
    },
    {
        "question": "Comment retourner un produit ?",
        "reponse_reference": "Vous disposez de 30 jours pour retourner votre produit en bon état."
    },
    {
        "question": "Quels sont les modes de paiement acceptés ?",
        "reponse_reference": "Nous acceptons les cartes bancaires, PayPal et le virement."
    },
]
```

---

## Créer un jeu de test avec LLM

En l'absence de jeu de test humain, on peut en générer un automatiquement.

```python
def generer_jeu_test_depuis_chunks(chunks, n_questions: int = 20) -> List[Dict]:
    """Génère un jeu de test question/réponse depuis les chunks indexés."""
    llm_gen = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    PROMPT_GEN_QA = ChatPromptTemplate.from_messages([
        ("system", """À partir du document fourni, génère une question précise
et sa réponse de référence basée uniquement sur ce document.

Format JSON :
{{"question": "...", "reponse_reference": "..."}}

Génère UNE SEULE paire question/réponse."""),
        ("human", "Document : {chunk}")
    ])

    from langchain_core.output_parsers import JsonOutputParser
    chain_gen = PROMPT_GEN_QA | llm_gen | JsonOutputParser()

    # Sélectionner des chunks représentatifs
    import random
    chunks_selectionnes = random.sample(chunks, min(n_questions, len(chunks)))

    jeu_test = []
    for chunk in chunks_selectionnes:
        try:
            qa = chain_gen.invoke({"chunk": chunk.page_content[:500]})
            qa["source_chunk"] = chunk.metadata.get("source", "?")
            jeu_test.append(qa)
        except Exception as e:
            print(f"Erreur génération QA : {e}")
            continue

    print(f"Jeu de test généré : {len(jeu_test)} paires Q/R")
    return jeu_test


# Sauvegarder le jeu de test pour réutilisation
def sauvegarder_jeu_test(jeu_test: List[Dict], chemin: str = "jeu_test_rag.json") -> None:
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(jeu_test, f, ensure_ascii=False, indent=2)
    print(f"Jeu de test sauvegardé : {chemin}")

def charger_jeu_test(chemin: str = "jeu_test_rag.json") -> List[Dict]:
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)
```

---

## Dashboard d'évaluation simple

```python
def afficher_rapport(resultats: List[Dict]) -> None:
    """Affiche un rapport d'évaluation formaté dans le terminal."""
    print("\n" + "="*60)
    print("RAPPORT D'ÉVALUATION DU SYSTÈME RAG")
    print("="*60)

    scores_faith = [r.get("faithfulness", 0) for r in resultats]
    scores_rel = [r.get("answer_relevancy", 0) for r in resultats]

    print(f"\nNombre de questions testées : {len(resultats)}")
    print(f"\nFaithfulness (fidélité au contexte) :")
    print(f"  Moyenne : {sum(scores_faith)/len(scores_faith):.2%}")
    print(f"  Min     : {min(scores_faith):.2%}")
    print(f"  Max     : {max(scores_faith):.2%}")

    if scores_rel:
        print(f"\nAnswer Relevancy (pertinence de la réponse) :")
        print(f"  Moyenne : {sum(scores_rel)/len(scores_rel):.2%}")

    # Identifier les cas problématiques
    problemes = [r for r in resultats if r.get("faithfulness", 1) < 0.7]
    print(f"\nRéponses problématiques (faithfulness < 70%) : {len(problemes)}")
    for p in problemes[:3]:
        print(f"\n  Q: {p['question'][:60]}...")
        print(f"  R: {p['reponse_generee'][:100]}...")
        print(f"  Score faithfulness: {p['faithfulness']:.2%}")

    print("\n" + "="*60)


# Interprétation des scores
SEUILS = {
    "faithfulness": {
        "excellent": 0.90,
        "bon": 0.75,
        "acceptable": 0.60,
    },
    "answer_relevancy": {
        "excellent": 0.85,
        "bon": 0.70,
        "acceptable": 0.55,
    },
    "context_recall": {
        "excellent": 0.90,
        "bon": 0.75,
        "acceptable": 0.60,
    },
}

def interpreter_score(metrique: str, score: float) -> str:
    seuils = SEUILS.get(metrique, {})
    if score >= seuils.get("excellent", 0.9):
        return "Excellent"
    elif score >= seuils.get("bon", 0.75):
        return "Bon"
    elif score >= seuils.get("acceptable", 0.6):
        return "Acceptable"
    else:
        return "A améliorer"
```

---

## Récapitulatif des métriques

| Métrique | Ce qu'elle mesure | Composant diagnostiqué |
|----------|------------------|----------------------|
| Context Recall | Les bons chunks sont récupérés ? | Retriever |
| Context Precision | Tous les chunks sont utiles ? | Retriever |
| Faithfulness | La réponse est fidèle aux chunks ? | LLM + Prompt |
| Answer Relevancy | La réponse répond bien à la question ? | LLM + Prompt |

**Lecture des diagnostics :**
- Context Recall bas → améliorer le retriever (k plus élevé, MMR, hybrid)
- Context Precision bas → trop de bruit dans les chunks (meilleur chunking, reranking)
- Faithfulness bas → hallucinations → renforcer le prompt
- Answer Relevancy bas → réponses hors-sujet → améliorer le prompt

La suite : [02-ragas.md](./02-ragas.md) — Automatiser l'évaluation avec RAGAS
