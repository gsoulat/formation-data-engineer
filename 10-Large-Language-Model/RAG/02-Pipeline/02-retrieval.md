# 02 — Stratégies de Retrieval

## Vue d'ensemble

Le retrieval est le cœur du RAG. C'est lui qui détermine quels chunks seront fournis au LLM pour générer la réponse. Un retrieval de mauvaise qualité produit des réponses mauvaises même avec le meilleur LLM du monde.

Il existe plusieurs stratégies de retrieval, du plus simple au plus sophistiqué :

```
Recherche vectorielle simple (similarity search)
    → Recherche avec MMR (diversification)
        → Recherche hybride (dense + sparse)
            → Reranking (reclassement post-retrieval)
                → Multi-query retrieval (reformulation)
```

---

## 1. Similarity Search — la base

La recherche par similarité cosinus est la stratégie par défaut. La question est embeddinée, puis les k vecteurs les plus proches dans la base sont retournés.

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# --- Recherche simple ---
question = "Quelles sont les conditions de garantie ?"
docs = vectorstore.similarity_search(question, k=4)

for i, doc in enumerate(docs):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Source : {doc.metadata.get('source', 'N/A')} | Page : {doc.metadata.get('page', 'N/A')}")
    print(doc.page_content[:200])

# --- Recherche avec score de similarité ---
docs_with_scores = vectorstore.similarity_search_with_score(question, k=4)

for doc, score in docs_with_scores:
    # Chroma retourne une distance (0 = identique, 2 = opposé)
    # Pour une similarité : sim = 1 - (distance / 2)
    similarite = 1 - (score / 2)
    print(f"Score : {similarite:.3f} | {doc.page_content[:100]}")
```

### Filtrage par métadonnées

```python
# Filtrer les résultats par métadonnée avant la recherche
docs_filtres = vectorstore.similarity_search(
    query="conditions de garantie",
    k=4,
    filter={"source": "contrat_vente.pdf"}  # Chroma filter
)

# Filtrage plus complexe avec $and, $or, $in
docs_filtres_2 = vectorstore.similarity_search(
    query="remboursement",
    k=4,
    filter={
        "$and": [
            {"type": {"$in": ["contrat", "cgu"]}},
            {"date": {"$gte": "2024-01-01"}}
        ]
    }
)
```

---

## 2. Le Retriever — abstraction sur le vectorstore

Un `Retriever` est l'interface standard LangChain pour la recherche. Il expose la méthode `.invoke(query)` et s'intègre dans les chaînes LCEL.

```python
# Créer un retriever depuis le vectorstore
retriever = vectorstore.as_retriever(
    search_type="similarity",      # Par défaut
    search_kwargs={
        "k": 4,                    # Nombre de résultats
        "filter": None,            # Filtre métadonnées optionnel
    }
)

# Utiliser le retriever
docs = retriever.invoke("politique de remboursement")
print(f"{len(docs)} chunks retournés")

# Le retriever s'intègre naturellement dans LCEL
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Réponds à la question en te basant sur le contexte :\n\n{context}"),
    ("human", "{question}")
])

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

reponse = chain.invoke("Quelles sont les conditions de garantie ?")
print(reponse)
```

---

## 3. MMR — Maximal Marginal Relevance

La recherche par similarité simple peut retourner des chunks redondants (très similaires entre eux). MMR diversifie les résultats en cherchant des chunks à la fois pertinents ET différents les uns des autres.

```python
# Retriever avec MMR
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,           # Nombre de résultats FINAUX retournés
        "fetch_k": 20,    # Nombre de candidats récupérés avant le re-scoring MMR
        "lambda_mult": 0.5,  # Équilibre pertinence (1.0) vs diversité (0.0)
    }
)

# Comparer similarity vs MMR sur la même question
question = "Comment fonctionne le système de paiement ?"

docs_sim = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(question)
docs_mmr = retriever_mmr.invoke(question)

print("=== Similarity Search ===")
for doc in docs_sim:
    print(f"  - {doc.page_content[:80]}...")

print("\n=== MMR Search ===")
for doc in docs_mmr:
    print(f"  - {doc.page_content[:80]}...")
```

**Quand utiliser MMR :**
- Documents avec beaucoup de répétitions ou de sections similaires
- Questions qui peuvent être traitées sous plusieurs angles
- Quand les k premiers résultats sont tous très similaires

---

## 4. Hybrid Search — combinaison dense + sparse

La recherche vectorielle (dense) est excellente pour la similarité sémantique mais peut manquer des mots-clés exacts. La recherche BM25 (sparse/keyword) est parfaite pour les mots exacts mais ignore le sens. La recherche hybride combine les deux.

```python
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

# Retriever BM25 (keyword-based)
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 4

# Retriever vectoriel (semantic)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Retriever hybride : moyenne pondérée des deux
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6],  # 40% BM25, 60% vectoriel
)

docs_hybrid = hybrid_retriever.invoke("article 12 prime exceptionnelle")
print(f"Hybrid search : {len(docs_hybrid)} résultats")
```

**Cas d'usage typiques pour la recherche hybride :**
- Documents techniques avec des noms propres, références, codes spécifiques
- Requêtes incluant des mots-clés précis ("article 12", "code produit XY-42")
- Base documentaire très large où les embeddings peuvent rater des termes rares

---

## 5. Self-Query Retriever — filtrage automatique

Le Self-Query Retriever utilise un LLM pour analyser la question et générer automatiquement les filtres de métadonnées appropriés.

```python
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_openai import ChatOpenAI

# Décrire les métadonnées disponibles
metadata_field_info = [
    AttributeInfo(
        name="source",
        description="Nom du fichier source (ex: 'rapport_2024.pdf', 'contrat_client.pdf')",
        type="string",
    ),
    AttributeInfo(
        name="page",
        description="Numéro de page dans le document source",
        type="integer",
    ),
    AttributeInfo(
        name="type",
        description="Type de document : 'contrat', 'rapport', 'faq', 'politique'",
        type="string",
    ),
    AttributeInfo(
        name="date",
        description="Date de création du document au format YYYY-MM-DD",
        type="string",
    ),
]

document_content_description = "Documents d'entreprise : contrats, rapports, FAQ, politiques"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

self_query_retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    document_contents=document_content_description,
    metadata_field_info=metadata_field_info,
    verbose=True,  # Afficher les filtres générés
)

# Le LLM décompose automatiquement la question en query + filtres
docs = self_query_retriever.invoke(
    "Trouve les clauses de résiliation dans les contrats de 2024"
)
# → query: "clauses de résiliation"
# → filter: {"type": "contrat", "date": {"$gte": "2024-01-01"}}
```

---

## 6. Multi-Query Retriever — reformulation

Quand une question est ambiguë ou formulée de façon sous-optimale pour la recherche vectorielle, le Multi-Query Retriever demande au LLM de générer plusieurs reformulations puis agrège les résultats.

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
import logging

# Activer les logs pour voir les reformulations
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    llm=llm,
)

# La question originale est reformulée en plusieurs variantes
docs = multi_query_retriever.invoke("Comment je me fais rembourser ?")
# Le LLM génère par ex. :
# → "procédure de remboursement"
# → "conditions pour obtenir un remboursement"
# → "délais et modalités de remboursement client"
# → Chaque variante est recherchée, les résultats sont dédupliqués

print(f"Documents trouvés : {len(docs)}")
```

**Prompt personnalisé pour les reformulations :**

```python
from langchain_core.prompts import PromptTemplate

prompt_reformulation = PromptTemplate(
    input_variables=["question"],
    template="""Tu es un expert en recherche documentaire.
Génère 3 versions différentes de la question suivante pour optimiser
la recherche dans une base de documents d'entreprise.
Sépare les questions par des sauts de ligne.

Question originale : {question}

3 versions alternatives :"""
)

multi_query_custom = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm,
    prompt=prompt_reformulation,
)
```

---

## 7. Reranking — reclasser les résultats

Le reranking est une étape post-retrieval : on récupère d'abord beaucoup de candidats (k élevé), puis on les reclasse avec un modèle plus précis (cross-encoder) et on ne garde que les meilleurs.

```
Retriever (k=20) → [c1, c2, ..., c20]
                         │
                    Reranker
                    (cross-encoder)
                         │
                  [c3, c7, c1, c15, c2] (reranqués)
                         │
                   Garder top-k=4
                         │
                   [c3, c7, c1, c15]
```

```python
# Reranker avec Cohere
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# API Cohere pour le reranking (tier gratuit disponible)
compressor = CohereRerank(
    model="rerank-multilingual-v3.0",  # Supporte le français
    top_n=4,                            # Garder les 4 meilleurs après reranking
)

# Retriever de base avec k élevé
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# Retriever avec reranking
reranking_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever,
)

docs_reranked = reranking_retriever.invoke("politique de remboursement")
print(f"Documents après reranking : {len(docs_reranked)}")
```

**Reranker local avec sentence-transformers :**

```python
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# Cross-encoder local (pas besoin d'API)
model = HuggingFaceCrossEncoder(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    # Pour le français : "antoinelouis/crossencoder-camembert-base-mmarcoFR"
)

cross_encoder_compressor = CrossEncoderReranker(
    model=model,
    top_n=4
)

reranking_retriever_local = ContextualCompressionRetriever(
    base_compressor=cross_encoder_compressor,
    base_retriever=base_retriever,
)

docs_reranked_local = reranking_retriever_local.invoke("garantie produit")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Comparaison côte à côte dans le terminal : similarity search (k=4) vs reranking (fetch k=20, return k=4) sur la même question — montrer les chunks retournés et leurs scores
> **Expliquer :** Lancer les deux retrievers sur la même question et afficher les résultats. Le reranking retourne souvent un ordre très différent. Expliquer la différence entre bi-encoder (embedding de la question seule) et cross-encoder (score conjoint question+document, plus précis mais plus lent). Insister : le reranking est l'une des améliorations à plus fort impact en RAG.

---

## 8. Contextual Compression — filtrage des chunks

Au lieu de retourner des chunks complets, le Contextual Compression extrait uniquement les passages directement pertinents à la question.

```python
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Compresseur : demande au LLM d'extraire le passage pertinent
compressor = LLMChainExtractor.from_llm(llm)

# Filtrer les chunks vides (quand aucun passage n'est pertinent)
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_openai import OpenAIEmbeddings

embeddings_filter = EmbeddingsFilter(
    embeddings=OpenAIEmbeddings(),
    similarity_threshold=0.76,   # Seuil de similarité minimum
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,  # Plus rapide (pas de LLM)
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 6}),
)

docs_compressed = compression_retriever.invoke("délai de livraison express")
for doc in docs_compressed:
    print(f"[{len(doc.page_content)} chars] {doc.page_content[:150]}")
```

---

## 9. Retriever pipeline — combiner les stratégies

En production, on combine plusieurs stratégies :

```python
# Pipeline de retrieval avancé : Hybrid + Reranking

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

def creer_retriever_production(
    vectorstore,
    chunks,
    k_final: int = 5,
    k_candidates: int = 20,
):
    """
    Pipeline de retrieval production :
    1. BM25 (keyword) + Vectoriel (semantic) → Hybrid
    2. Reranking Cohere sur les candidats hybrides
    """
    # Étape 1 : Retrieval hybride
    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = k_candidates // 2

    vector = vectorstore.as_retriever(
        search_kwargs={"k": k_candidates // 2}
    )

    hybrid = EnsembleRetriever(
        retrievers=[bm25, vector],
        weights=[0.3, 0.7],
    )

    # Étape 2 : Reranking
    reranker = CohereRerank(
        model="rerank-multilingual-v3.0",
        top_n=k_final,
    )

    final_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=hybrid,
    )

    return final_retriever


# Utilisation
retriever_prod = creer_retriever_production(vectorstore, chunks, k_final=5)
docs = retriever_prod.invoke("quelles sont les conditions de garantie premium ?")
```

---

## 10. Évaluer la qualité du retrieval

Avant d'évaluer la réponse finale, on peut évaluer indépendamment la qualité du retrieval.

```python
def evaluer_retrieval(retriever, questions_avec_reponses_attendues: list[dict]) -> dict:
    """
    Évalue un retriever sur un jeu de test.

    Args:
        questions_avec_reponses_attendues: liste de dicts avec
            {"question": str, "passage_attendu": str}
    """
    hits = 0
    total = len(questions_avec_reponses_attendues)

    for item in questions_avec_reponses_attendues:
        question = item["question"]
        passage_attendu = item["passage_attendu"].lower()

        docs = retriever.invoke(question)

        # Hit@k : est-ce que le passage attendu est dans les k résultats ?
        found = any(passage_attendu in doc.page_content.lower() for doc in docs)
        if found:
            hits += 1

    recall_at_k = hits / total
    print(f"Recall@{len(docs)} : {recall_at_k:.2%} ({hits}/{total})")
    return {"recall_at_k": recall_at_k, "hits": hits, "total": total}


# Jeu de test minimal
test_set = [
    {"question": "Quel est le délai de remboursement ?", "passage_attendu": "30 jours"},
    {"question": "Comment contacter le support ?", "passage_attendu": "support@entreprise.com"},
    {"question": "Quelles sont les conditions de garantie ?", "passage_attendu": "deux ans"},
]

# Comparer plusieurs retrievers
print("--- Similarity simple ---")
evaluer_retrieval(vectorstore.as_retriever(search_kwargs={"k": 4}), test_set)

print("--- MMR ---")
evaluer_retrieval(vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 4}), test_set)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Tableau comparatif des Recall@k pour chaque stratégie de retrieval affiché dans le terminal
> **Expliquer :** Montrer que le même corpus avec des stratégies différentes donne des Recall@4 très différents (typiquement 60% similarity simple vs 80%+ avec reranking). C'est la démonstration que le choix du retriever est aussi important que le choix du LLM. Si le retriever rate le bon chunk, le LLM ne peut pas y suppléer.

---

## Récapitulatif des stratégies

| Stratégie | Précision | Vitesse | Coût | Quand l'utiliser |
|-----------|-----------|---------|------|-----------------|
| Similarity Search | Moyenne | Très rapide | Minimal | Développement, prototype |
| MMR | Moyenne+ | Rapide | Minimal | Docs répétitifs |
| Hybrid (BM25+Vector) | Haute | Rapide | Minimal | Termes techniques/propres |
| Multi-Query | Haute | Lent | Moyen (LLM) | Questions ambiguës |
| Reranking | Très haute | Moyen | Moyen (API) | Production |
| Self-Query | Haute | Moyen | Moyen (LLM) | Filtrage métadonnées |

La suite : [03-generation.md](./03-generation.md) — Construction du prompt et synthèse de réponse
