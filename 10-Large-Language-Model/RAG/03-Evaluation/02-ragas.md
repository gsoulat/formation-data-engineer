# 02 — RAGAS : Évaluation Automatisée du RAG

## Qu'est-ce que RAGAS ?

RAGAS (RAG Assessment) est un framework open-source spécialisé dans l'évaluation automatisée des pipelines RAG. Il calcule les métriques vues précédemment (faithfulness, answer relevancy, context recall, context precision) de façon standardisée, sans avoir besoin de labellisation humaine.

**Avantages de RAGAS :**
- Calcul automatique des métriques RAG standard
- Intégration native avec LangChain
- Génération automatique de jeux de test (TestsetGenerator)
- Rapports détaillés par question

```bash
pip install ragas datasets
```

---

## Structure d'un dataset d'évaluation RAGAS

RAGAS attend un format précis :

```python
from datasets import Dataset

# Format RAGAS
dataset = Dataset.from_dict({
    "question":          ["Q1", "Q2", "Q3"],          # Questions posées
    "answer":            ["R1", "R2", "R3"],           # Réponses générées par le RAG
    "contexts":          [["chunk1", "chunk2"],         # Chunks récupérés par le retriever
                          ["chunk3"],
                          ["chunk4", "chunk5", "chunk6"]],
    "ground_truth":      ["ref1", "ref2", "ref3"],     # Réponses de référence (optionnel)
})
```

Seuls `question`, `answer` et `contexts` sont requis pour les métriques sans référence.

---

## 1. Évaluation de base avec RAGAS

```python
from dotenv import load_dotenv
load_dotenv()

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

# Configurer les modèles pour RAGAS
llm_ragas = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
emb_ragas = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))

# Dataset d'exemple
data = {
    "question": [
        "Quelle est la durée de garantie ?",
        "Comment retourner un produit défectueux ?",
        "Quels modes de paiement sont acceptés ?",
    ],
    "answer": [
        "La garantie est de 2 ans sur les pièces et la main d'œuvre.",
        "Vous devez contacter le service client dans les 30 jours suivant la réception.",
        "Nous acceptons les cartes bancaires Visa, Mastercard, PayPal et le virement bancaire.",
    ],
    "contexts": [
        [
            "Tout produit bénéficie d'une garantie constructeur de 24 mois "
            "couvrant les défauts de fabrication sur les pièces d'origine et "
            "les frais de main d'œuvre associés."
        ],
        [
            "En cas de produit défectueux, le client dispose de 30 jours calendaires "
            "à compter de la date de réception pour contacter notre service après-vente "
            "via le formulaire en ligne ou par téléphone au 01 23 45 67 89."
        ],
        [
            "Les paiements sont acceptés par carte bancaire (Visa, Mastercard, American Express), "
            "PayPal et virement bancaire. Le règlement par chèque n'est pas disponible."
            # Note : American Express est dans le contexte mais pas dans la réponse — OK
            # Note : "chèque" n'est pas dans la réponse — OK, absence d'hallucination
        ],
    ],
    "ground_truth": [
        "La garantie est de 24 mois sur les pièces et la main d'œuvre.",
        "Contacter le SAV dans les 30 jours via le formulaire ou le téléphone.",
        "Visa, Mastercard, American Express, PayPal et virement bancaire.",
    ],
}

dataset = Dataset.from_dict(data)

# Lancer l'évaluation
resultats = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
    ],
    llm=llm_ragas,
    embeddings=emb_ragas,
)

print(resultats)
```

---

## 2. Analyser les résultats

```python
import pandas as pd

# Convertir en DataFrame pour l'analyse
df = resultats.to_pandas()
print(df.to_string())

# Métriques agrégées
print("\n=== Scores moyens ===")
metriques = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
for m in metriques:
    if m in df.columns:
        print(f"{m:30s}: {df[m].mean():.3f} (min: {df[m].min():.3f}, max: {df[m].max():.3f})")

# Identifier les questions problématiques
print("\n=== Questions avec faithfulness < 0.8 ===")
mauvaises = df[df["faithfulness"] < 0.8]
if len(mauvaises) > 0:
    for _, row in mauvaises.iterrows():
        print(f"\nQ: {row['question']}")
        print(f"R: {row['answer'][:100]}...")
        print(f"Faithfulness: {row['faithfulness']:.3f}")
else:
    print("Aucune.")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Sortie RAGAS dans le terminal avec le DataFrame des scores par question, puis les scores moyens agrégés
> **Expliquer :** Parcourir chaque ligne du DataFrame. Pointer une question où la faithfulness est faible et montrer pourquoi (la réponse contient une info non présente dans le contexte). Comparer les scores avant/après amélioration du prompt. Insister : RAGAS permet de faire de l'ingénierie pilotée par les données — on ne modifie pas le système au hasard, on mesure l'impact de chaque changement.

---

## 3. TestsetGenerator — générer un jeu de test automatiquement

RAGAS peut générer un jeu de test complet depuis vos documents, sans annotation humaine.

```python
from ragas.testset import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Charger les documents source
loader = PyPDFLoader("documentation.pdf")
documents = loader.load()

# Configurer le générateur
generator = TestsetGenerator.from_langchain(
    generator_llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
    critic_llm=ChatOpenAI(model="gpt-4o", temperature=0),
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
)

# Générer le jeu de test
# - simple : questions directes avec une seule source
# - reasoning : questions nécessitant une inférence
# - multi_context : questions nécessitant plusieurs sources
testset = generator.generate_with_langchain_docs(
    documents=documents,
    test_size=20,
    distributions={
        simple: 0.5,           # 50% de questions simples
        reasoning: 0.3,        # 30% de questions nécessitant du raisonnement
        multi_context: 0.2,    # 20% de questions multi-sources
    },
)

# Convertir en DataFrame
df_test = testset.to_pandas()
print(df_test[["question", "ground_truth", "evolution_type"]].to_string())
print(f"\nTotal : {len(df_test)} questions générées")
```

---

## 4. Pipeline d'évaluation complet — bout en bout

```python
# evaluation_pipeline.py
from dotenv import load_dotenv
load_dotenv()

from typing import List
from datasets import Dataset

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

import pandas as pd
import json
from datetime import datetime

# ---- Composants RAG ----
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Réponds à la question en te basant uniquement sur le contexte.\n\n{context}"),
    ("human", "{question}")
])

rag_chain = (
    {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
     "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

# ---- Exécuter le RAG sur le jeu de test ----
def executer_rag_sur_jeu_test(jeu_test: List[dict]) -> Dataset:
    """Exécute le RAG sur chaque question et collecte les données pour RAGAS."""
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in jeu_test:
        q = item["question"]
        gt = item.get("ground_truth", "")

        # Récupérer les chunks
        docs = retriever.invoke(q)
        ctx = [doc.page_content for doc in docs]

        # Générer la réponse
        reponse = rag_chain.invoke(q)

        questions.append(q)
        answers.append(reponse)
        contexts.append(ctx)
        ground_truths.append(gt)

        print(f"  Q: {q[:50]}... → {len(ctx)} chunks récupérés")

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })


# ---- Évaluer avec RAGAS ----
def evaluer_avec_ragas(dataset: Dataset) -> dict:
    """Lance l'évaluation RAGAS et retourne les scores."""
    llm_eval = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
    emb_eval = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

    resultats = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        llm=llm_eval,
        embeddings=emb_eval,
    )

    return resultats


# ---- Sauvegarder les résultats ----
def sauvegarder_resultats(resultats, nom_experience: str = None) -> str:
    """Sauvegarde les résultats d'évaluation avec timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom = nom_experience or f"evaluation_{timestamp}"

    df = resultats.to_pandas()
    chemin_csv = f"./evaluations/{nom}.csv"
    df.to_csv(chemin_csv, index=False, encoding="utf-8")

    scores = {
        "timestamp": timestamp,
        "nom": nom,
        "faithfulness": float(df["faithfulness"].mean()),
        "answer_relevancy": float(df["answer_relevancy"].mean()),
        "context_recall": float(df["context_recall"].mean()),
        "context_precision": float(df["context_precision"].mean()),
        "nb_questions": len(df),
    }

    chemin_json = f"./evaluations/{nom}_scores.json"
    with open(chemin_json, "w") as f:
        json.dump(scores, f, indent=2)

    print(f"\nRésultats sauvegardés : {chemin_csv}")
    return chemin_csv


# ---- Programme principal ----
if __name__ == "__main__":
    import os
    os.makedirs("./evaluations", exist_ok=True)

    # Charger le jeu de test
    with open("jeu_test_rag.json", encoding="utf-8") as f:
        jeu_test = json.load(f)

    print(f"=== Évaluation sur {len(jeu_test)} questions ===\n")

    print("1. Exécution du RAG...")
    dataset = executer_rag_sur_jeu_test(jeu_test)

    print("\n2. Évaluation RAGAS...")
    resultats = evaluer_avec_ragas(dataset)

    print("\n3. Résultats :")
    df = resultats.to_pandas()
    for m in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
        if m in df.columns:
            print(f"  {m:25s}: {df[m].mean():.3f}")

    sauvegarder_resultats(resultats, "baseline_v1")
```

---

## 5. Comparer différentes configurations

L'usage principal de RAGAS est de comparer objectivement différentes configurations du pipeline.

```python
# comparaison_configurations.py
import json
import pandas as pd
from pathlib import Path

def charger_scores(chemin_json: str) -> dict:
    with open(chemin_json) as f:
        return json.load(f)

# Charger les scores de plusieurs configurations
configurations = {
    "baseline": charger_scores("./evaluations/baseline_v1_scores.json"),
    "hybrid_retrieval": charger_scores("./evaluations/hybrid_v1_scores.json"),
    "reranking": charger_scores("./evaluations/reranking_v1_scores.json"),
    "semantic_chunking": charger_scores("./evaluations/semantic_chunk_v1_scores.json"),
}

# Tableau comparatif
metriques = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
df_comp = pd.DataFrame({
    nom: {m: scores[m] for m in metriques}
    for nom, scores in configurations.items()
}).T

print("=== Comparaison des configurations ===\n")
print(df_comp.to_string(float_format="{:.3f}".format))

# Identifier la meilleure configuration par métrique
print("\n=== Meilleure configuration par métrique ===")
for m in metriques:
    meilleur = df_comp[m].idxmax()
    score = df_comp[m].max()
    print(f"{m:30s}: {meilleur} ({score:.3f})")
```

---

## 6. Métriques RAGAS avancées

```python
# Métriques supplémentaires disponibles dans RAGAS
from ragas.metrics import (
    # Métriques principales
    faithfulness,             # Fidélité aux chunks
    answer_relevancy,         # Pertinence de la réponse
    context_recall,           # Rappel du contexte
    context_precision,        # Précision du contexte

    # Métriques avancées
    answer_correctness,       # Exactitude factuelle vs ground truth
    answer_similarity,        # Similarité sémantique avec la référence

    # Sans LLM (basées sur embeddings uniquement, plus rapides)
    context_entity_recall,    # Rappel des entités nommées
)

# answer_correctness : combinaison de similarité sémantique + recouvrement factuel
# Nécessite ground_truth dans le dataset

resultats_avances = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision,
        answer_correctness,
        answer_similarity,
    ],
    llm=llm_ragas,
    embeddings=emb_ragas,
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le tableau comparatif des configurations dans le terminal — colonnes = métriques, lignes = configurations (baseline vs hybrid vs reranking)
> **Expliquer :** Montrer concrètement que le reranking améliore le context_recall mais peut légèrement augmenter la latence. Que le semantic chunking améliore la faithfulness sur les documents hétérogènes. Insister : sans ce tableau, on ne peut pas prendre de décision éclairée sur quelle configuration déployer en production. C'est la différence entre "ça m'a l'air bien" et "les données montrent que c'est 12% meilleur".

---

## 7. Intégration dans un pipeline CI/CD

```python
# tests/test_rag_quality.py — À inclure dans votre CI/CD
import pytest
import json
from pathlib import Path

# Seuils minimums acceptables
SEUILS = {
    "faithfulness": 0.80,
    "answer_relevancy": 0.75,
    "context_recall": 0.70,
}

def charger_derniers_scores() -> dict:
    """Charge les scores de la dernière évaluation."""
    fichiers = sorted(Path("./evaluations").glob("*_scores.json"))
    if not fichiers:
        pytest.skip("Aucune évaluation disponible")
    with open(fichiers[-1]) as f:
        return json.load(f)

@pytest.fixture
def scores():
    return charger_derniers_scores()

def test_faithfulness_minimum(scores):
    """Le RAG ne doit pas halluciner plus de 20% du temps."""
    assert scores["faithfulness"] >= SEUILS["faithfulness"], (
        f"Faithfulness trop bas : {scores['faithfulness']:.2%} < {SEUILS['faithfulness']:.0%}"
    )

def test_answer_relevancy_minimum(scores):
    """Les réponses doivent être pertinentes dans au moins 75% des cas."""
    assert scores["answer_relevancy"] >= SEUILS["answer_relevancy"], (
        f"Answer relevancy trop bas : {scores['answer_relevancy']:.2%}"
    )

def test_context_recall_minimum(scores):
    """Le retriever doit trouver les bons chunks dans au moins 70% des cas."""
    assert scores["context_recall"] >= SEUILS["context_recall"], (
        f"Context recall trop bas : {scores['context_recall']:.2%}"
    )

# Lancer avec : pytest tests/test_rag_quality.py -v
```

---

## Récapitulatif RAGAS

| Aspect | Détail |
|--------|--------|
| Installation | `pip install ragas datasets` |
| Format dataset | `question`, `answer`, `contexts`, `ground_truth` (optionnel) |
| Métriques clés | faithfulness, answer_relevancy, context_recall, context_precision |
| TestsetGenerator | Génère des QA depuis vos documents automatiquement |
| Usage principal | Comparer des configurations, détecter les régressions |
| Coût | ~$0.01-0.05 par question évaluée (appels LLM internes) |
| Recommandation | Évaluer sur 20-50 questions représentatives minimum |

La suite : [Avance/01-rag-conversationnel.md](../Avance/01-rag-conversationnel.md) — RAG multi-tours avec historique
