# Pipeline RAG : Connecter une Vector DB à un LLM

## Introduction

RAG — **Retrieval-Augmented Generation** — est aujourd'hui le pattern architectural dominant pour construire des applications LLM en production. Il combine la puissance générative des LLM avec la capacité des vector databases à retrouver des informations pertinentes et à jour.

Ce chapitre vous guide dans la construction d'un pipeline RAG complet, étape par étape.

---

## 1. Pourquoi RAG plutôt que fine-tuning ?

### Le problème des LLM seuls

```
LLM seul (GPT-4, Llama 3...) :
- Connaissance figée à la date d'entraînement
- Peut "halluciner" des informations plausibles mais fausses
- Ne connaît pas vos documents internes
- Pas de source citable
- Fine-tuning = coûteux et complexe à maintenir
```

### RAG résout ces problèmes

```
RAG = LLM + Vector DB :
✅ Connaissances mises à jour en temps réel (ajouter des documents sans réentraîner)
✅ Sources citables (on sait d'où vient l'information)
✅ Moins d'hallucinations (le LLM s'appuie sur des textes réels)
✅ Fonctionne avec vos documents privés
✅ Coût bien inférieur au fine-tuning
✅ Modifiable sans toucher au modèle
```

---

## 2. Architecture complète d'un pipeline RAG

```
═══════════════════════════════════════════════════════════════
PHASE 1 : INGESTION (offline, une fois ou périodiquement)
═══════════════════════════════════════════════════════════════

Documents (PDF, TXT, HTML, CSV...)
        │
        ▼
  ┌─────────────┐
  │  Loader     │  → LangChain DocumentLoader (PDF, Web, CSV...)
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Splitter   │  → RecursiveCharacterTextSplitter(chunk_size=1000, overlap=200)
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Embedder   │  → HuggingFaceEmbeddings ou OpenAIEmbeddings
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Vector DB  │  → Chroma, Qdrant, pgvector...
  └─────────────┘

═══════════════════════════════════════════════════════════════
PHASE 2 : REQUÊTE (online, à chaque question utilisateur)
═══════════════════════════════════════════════════════════════

Question utilisateur
        │
        ▼
  ┌─────────────┐
  │  Embedder   │  → Même modèle que lors de l'ingestion (IMPORTANT)
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Retriever  │  → Recherche les K documents les plus proches
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │   Prompt    │  → "Réponds à cette question en te basant sur ce contexte..."
  │  Template   │     + documents récupérés + question
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │    LLM      │  → GPT-4, Claude, Llama 3, Mistral...
  └─────────────┘
        │
        ▼
  Réponse sourcée avec références aux documents utilisés
```

---

## 3. Pipeline RAG minimal avec Chroma + OpenAI

```python
# pip install langchain langchain-openai langchain-chroma sentence-transformers pypdf
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
DOCS_PATH = "./documents/"
DB_PATH = "./rag_chroma_db"
COLLECTION_NAME = "knowledge_base"
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
LLM_MODEL = "gpt-4o-mini"

# ─────────────────────────────────────────────────────────────
# PHASE 1 : INGESTION
# ─────────────────────────────────────────────────────────────
def build_vector_store():
    """Charge les documents, les chunk, les embed et les stocke dans Chroma."""

    print("1. Chargement des documents...")
    loader = DirectoryLoader(DOCS_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"   → {len(documents)} pages chargées")

    print("2. Découpage en chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = splitter.split_documents(documents)
    print(f"   → {len(chunks)} chunks générés")

    print("3. Génération des embeddings et stockage dans Chroma...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True}
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH,
        collection_name=COLLECTION_NAME
    )

    print(f"   → {vectorstore._collection.count()} vecteurs stockés dans '{DB_PATH}'")
    return vectorstore


# ─────────────────────────────────────────────────────────────
# PHASE 2 : REQUÊTE
# ─────────────────────────────────────────────────────────────
def load_rag_chain():
    """Charge le vector store existant et construit la chaîne RAG."""

    # Charger le vector store
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    # Configurer le retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Prompt en français
    prompt = PromptTemplate(
        template="""Tu es un assistant expert qui répond aux questions en te basant uniquement
sur les documents fournis. Si l'information ne se trouve pas dans les documents,
dis-le clairement en commençant par "Je ne trouve pas cette information dans les documents fournis."

N'invente jamais d'informations non présentes dans le contexte.

Documents pertinents :
{context}

Question : {question}

Réponse (en français) :""",
        input_variables=["context", "question"]
    )

    # LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0,          # 0 = déterministe, pas de créativité
        max_tokens=1000
    )

    # Chaîne RAG
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    return chain


# ─────────────────────────────────────────────────────────────
# UTILISATION
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os

    # Construire le vector store si non existant
    if not os.path.exists(DB_PATH):
        build_vector_store()

    # Charger la chaîne RAG
    rag_chain = load_rag_chain()

    # Interroger
    questions = [
        "Quelle est la politique de remboursement ?",
        "Comment contacter le support technique ?",
        "Quelles sont les fonctionnalités disponibles en plan gratuit ?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question : {question}")
        print("─" * 60)

        response = rag_chain.invoke({"query": question})

        print(f"Réponse : {response['result']}")
        print(f"\nSources ({len(response['source_documents'])} chunks) :")
        for doc in response['source_documents']:
            source = doc.metadata.get('source', 'Inconnu')
            page = doc.metadata.get('page', '?')
            print(f"  - {source} (page {page}) : {doc.page_content[:80]}...")
```

---

## 4. Stratégies de retrieval

### 4.1 Similarity Search (par défaut)

Retourne les K documents les plus proches selon la métrique de distance choisie. Simple et efficace dans la majorité des cas.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)
```

### 4.2 MMR — Maximal Marginal Relevance

MMR équilibre **pertinence** et **diversité**. Il évite de retourner 4 fois le même document légèrement paraphrasé.

```
Algorithme MMR :
1. Trouver le document le plus similaire à la requête → ajouter aux résultats
2. Parmi les documents restants, choisir celui qui est à la fois :
   - Le plus similaire à la requête (pertinence)
   - Le plus différent des documents déjà sélectionnés (diversité)
3. Répéter jusqu'à obtenir K documents

Paramètre lambda_mult :
  0.0 = maximise la diversité (ignore la pertinence)
  1.0 = maximise la pertinence (équivalent à similarity search)
  0.5 = équilibre optimal (valeur recommandée)
```

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,           # Documents finaux à retourner
        "fetch_k": 20,    # Candidats à considérer pour MMR (doit être > k)
        "lambda_mult": 0.5  # Balance pertinence/diversité
    }
)

# Tester la différence
query = "Comment configurer Python ?"

# Similarity : peut retourner des documents très similaires entre eux
docs_sim = vectorstore.similarity_search(query, k=4)

# MMR : retourne des documents pertinents mais diversifiés
docs_mmr = vectorstore.max_marginal_relevance_search(query, k=4, fetch_k=20)
```

### 4.3 Similarity Score Threshold

Retourne uniquement les documents dont le score dépasse un seuil minimal.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.7,  # Exclure les documents peu pertinents
        "k": 10
    }
)
# Si aucun document ne dépasse le seuil → retourne une liste vide
# → Le LLM répond alors "Je n'ai pas trouvé d'information pertinente"
```

### 4.4 Hybrid Search (vectoriel + BM25 keyword)

```python
# pip install langchain-community rank_bm25
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# Retriever BM25 (keyword-based)
bm25_retriever = BM25Retriever.from_documents(all_docs)
bm25_retriever.k = 5

# Retriever vectoriel
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Combiner les deux (50% / 50%)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
    # BM25 est fort sur les termes exacts (noms propres, codes, numéros)
    # Vectoriel est fort sur la sémantique et les paraphrases
)

docs = ensemble_retriever.invoke("erreur 404 dans l'API REST")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démontrer en live la différence entre similarity search et MMR. Prendre un corpus où plusieurs documents parlent du même sujet. Montrer que similarity retourne 4 documents quasi-identiques, alors que MMR retourne 4 documents diversifiés mais tous pertinents.
> **Expliquer :** "MMR est crucial pour un bon RAG. Si vous injectez 4 fois la même information dans le prompt, vous gaspillez de l'espace de contexte. MMR vous assure de couvrir différents angles de la question."

---

## 5. Pipeline RAG avec Qdrant

```python
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ─────────────────────────────────────────────────────────────
# Connexion Qdrant
# ─────────────────────────────────────────────────────────────
qdrant_client = QdrantClient(host="localhost", port=6333)
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")

# ─────────────────────────────────────────────────────────────
# Ingestion (si la collection n'existe pas)
# ─────────────────────────────────────────────────────────────
COLLECTION_NAME = "rag_docs"
existing = [c.name for c in qdrant_client.get_collections().collections]

if COLLECTION_NAME not in existing:
    print("Ingestion des documents...")
    loader = DirectoryLoader("./documents/", glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vectorstore = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME
    )
    print(f"Ingestion terminée : {len(chunks)} chunks")
else:
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    print(f"Collection '{COLLECTION_NAME}' chargée.")

# ─────────────────────────────────────────────────────────────
# Chaîne RAG
# ─────────────────────────────────────────────────────────────
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 15}
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = PromptTemplate(
    template="""Réponds à la question en te basant uniquement sur le contexte fourni.
Cite les sources quand c'est pertinent.

Contexte :
{context}

Question : {question}

Réponse :""",
    input_variables=["context", "question"]
)

chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

# Interroger
result = chain.invoke({"query": "Quels sont les principaux avantages du produit ?"})
print(result['result'])
```

---

## 6. RAG avancé : LCEL (LangChain Expression Language)

LCEL offre une syntaxe plus flexible et modulaire que `RetrievalQA`. C'est l'approche recommandée pour les pipelines complexes.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ─────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
vectorstore = Chroma(persist_directory="./rag_chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ─────────────────────────────────────────────────────────────
# Prompt template
# ─────────────────────────────────────────────────────────────
prompt = ChatPromptTemplate.from_template("""
Tu es un assistant expert. Réponds à la question en te basant uniquement sur le contexte.

Contexte :
{context}

Question : {question}

Réponse :
""")

# ─────────────────────────────────────────────────────────────
# Fonction de formatage du contexte
# ─────────────────────────────────────────────────────────────
def format_docs(docs):
    """Formater les documents récupérés en un seul bloc de texte."""
    formatted = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get('source', 'Inconnu')
        page = doc.metadata.get('page', '?')
        formatted.append(f"[Source {i+1} : {source}, page {page}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)

# ─────────────────────────────────────────────────────────────
# Chaîne LCEL
# ─────────────────────────────────────────────────────────────
rag_chain = (
    {
        "context": retriever | format_docs,  # Récupérer et formater le contexte
        "question": RunnablePassthrough()     # Passer la question telle quelle
    }
    | prompt       # Injecter dans le prompt template
    | llm          # Appeler le LLM
    | StrOutputParser()  # Extraire le texte de la réponse
)

# Utilisation
response = rag_chain.invoke("Comment fonctionne la facturation ?")
print(response)

# Avec streaming (pour une UX type ChatGPT)
for chunk in rag_chain.stream("Quelle est la politique de confidentialité ?"):
    print(chunk, end="", flush=True)
print()  # Nouvelle ligne à la fin
```

---

## 7. Évaluation de la qualité RAG

### 7.1 Métriques clés

```
Retrieval quality (qualité du retrieval) :
  - Precision@K : parmi les K documents récupérés, combien sont vraiment pertinents ?
  - Recall@K    : parmi tous les documents pertinents, combien ont été récupérés ?

Generation quality (qualité de la génération) :
  - Faithfulness : la réponse est-elle fidèle aux sources récupérées ? (pas d'hallucination)
  - Relevance    : la réponse répond-elle à la question posée ?
  - Groundedness : les affirmations sont-elles supportées par le contexte ?
```

### 7.2 Évaluation basique avec RAGAS

```python
# pip install ragas
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

# Préparer les données d'évaluation
eval_data = {
    "question": [
        "Quelle est la politique de remboursement ?",
        "Comment contacter le support ?"
    ],
    "answer": [
        "La politique de remboursement est de 30 jours...",
        "Vous pouvez contacter le support par email à..."
    ],
    "contexts": [
        ["Les remboursements sont acceptés sous 30 jours...", "Conditions générales..."],
        ["Email support: support@example.com", "Heures d'ouverture: 9h-17h"]
    ],
    "ground_truth": [
        "La politique est 30 jours",
        "support@example.com"
    ]
}

dataset = Dataset.from_dict(eval_data)

results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)

print(results)
# → {'faithfulness': 0.92, 'answer_relevancy': 0.87, 'context_precision': 0.90}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démontrer un pipeline RAG complet en live : charger des documents PDF, les ingérer dans Chroma, puis poser des questions. Montrer côte à côte la question posée, les chunks récupérés, et la réponse du LLM avec les sources.
> **Expliquer :** "Regardez : quand je pose une question sur la politique de remboursement, le system récupère exactement le chunk qui parle de ça. Le LLM ne 'sait' pas la réponse dans ses paramètres — il lit le chunk récupéré et résume. Si demain la politique change, il suffit de réingérer le document mis à jour pour que les réponses changent. Pas de fine-tuning."

---

## 8. Patterns avancés

### 8.1 Query Decomposition (décomposition de questions complexes)

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Décomposer une question complexe en sous-questions
decompose_prompt = ChatPromptTemplate.from_template("""
Tu es un assistant qui décompose les questions complexes en 3 sous-questions plus simples.
Retourne uniquement les 3 sous-questions séparées par des sauts de ligne, sans numérotation.

Question complexe : {question}
""")

decompose_chain = decompose_prompt | llm | StrOutputParser()

def rag_with_decomposition(question: str, retriever, llm):
    # 1. Décomposer la question
    sub_questions_text = decompose_chain.invoke({"question": question})
    sub_questions = [q.strip() for q in sub_questions_text.split("\n") if q.strip()]
    print(f"Sous-questions générées : {sub_questions}")

    # 2. Récupérer des documents pour chaque sous-question
    all_docs = []
    for sq in sub_questions:
        docs = retriever.invoke(sq)
        all_docs.extend(docs)

    # Dédupliquer
    seen = set()
    unique_docs = []
    for doc in all_docs:
        key = doc.page_content[:100]
        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    # 3. Répondre avec le contexte agrégé
    context = "\n\n".join([d.page_content for d in unique_docs[:6]])
    answer_prompt = ChatPromptTemplate.from_template("""
Réponds à cette question complexe en te basant sur le contexte.

Contexte : {context}
Question principale : {question}

Réponse :""")

    chain = answer_prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})
```

### 8.2 Contextual Compression (compression du contexte)

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Compresseur : extrait uniquement la partie pertinente de chaque document
compressor = LLMChainExtractor.from_llm(llm)

# Retriever avec compression
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever  # Votre retriever classique
)

# Les documents retournés sont des extraits ultra-pertinents, pas les chunks entiers
docs = compression_retriever.invoke("Comment installer l'application ?")
for doc in docs:
    print(doc.page_content[:200])  # Beaucoup plus ciblé que le chunk complet
```

### 8.3 Self-RAG avec vérification de pertinence

```python
def rag_with_relevance_check(question: str, retriever, llm, threshold: float = 0.5):
    """
    Pipeline RAG avec vérification automatique de la pertinence des documents.
    Si les documents ne sont pas pertinents, répond sans contexte.
    """
    # 1. Récupérer des documents
    docs = retriever.invoke(question)

    if not docs:
        return "Désolé, je n'ai pas trouvé d'informations pertinentes dans la base de connaissance."

    # 2. Vérifier la pertinence
    grading_prompt = ChatPromptTemplate.from_template("""
Évalue si ce document est pertinent pour répondre à la question.
Réponds uniquement par "oui" ou "non".

Document : {document}
Question : {question}

Pertinent ?""")

    grader = grading_prompt | llm | StrOutputParser()

    relevant_docs = []
    for doc in docs:
        grade = grader.invoke({"document": doc.page_content[:500], "question": question})
        if "oui" in grade.lower():
            relevant_docs.append(doc)

    if not relevant_docs:
        return "Désolé, je n'ai pas trouvé d'informations pertinentes dans mes documents pour cette question."

    # 3. Générer la réponse
    context = "\n\n".join([d.page_content for d in relevant_docs])
    answer_prompt = ChatPromptTemplate.from_template(
        "Réponds à la question en te basant sur ce contexte.\n\nContexte : {context}\n\nQuestion : {question}\n\nRéponse :"
    )
    chain = answer_prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})
```

---

## 9. Exemple complet : chatbot documentaire interactif

```python
#!/usr/bin/env python3
"""
Chatbot documentaire RAG complet avec historique de conversation.
"""
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()

# Setup
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
vectorstore = Chroma(persist_directory="./rag_chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 20})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# Mémoire conversationnelle (garde les 5 derniers échanges)
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# Chaîne conversationnelle RAG (prend en compte l'historique)
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,
    verbose=False
)

def chat(question: str) -> str:
    result = conversation_chain.invoke({"question": question})
    answer = result['answer']
    sources = list(set([
        doc.metadata.get('source', 'Inconnu')
        for doc in result.get('source_documents', [])
    ]))
    if sources:
        answer += f"\n\n*Sources : {', '.join(sources)}*"
    return answer

# Interface CLI simple
print("=== Chatbot documentaire ===")
print("Tapez 'quit' pour quitter\n")

while True:
    question = input("Vous : ").strip()
    if question.lower() in ['quit', 'exit', 'q']:
        print("Au revoir !")
        break
    if not question:
        continue

    response = chat(question)
    print(f"\nAssistant : {response}\n")
```

---

## Résumé du pipeline RAG

| Étape | Outil recommandé | Point d'attention |
|-------|-----------------|-------------------|
| Chargement | LangChain DocumentLoaders | Conserver les métadonnées source |
| Chunking | RecursiveCharacterTextSplitter | chunk_size=1000, overlap=200 |
| Embedding | sentence-transformers (local) ou OpenAI | Même modèle ingestion/requête |
| Stockage | Chroma (dev) ou Qdrant (prod) | Métrique cosinus pour le texte |
| Retrieval | MMR avec k=4, fetch_k=15 | Ajuster selon la longueur des chunks |
| Génération | GPT-4o-mini ou Llama 3 via Ollama | Temperature=0 pour les faits |
| Évaluation | RAGAS | Faithfulness + Answer Relevancy |

Le pipeline RAG est le point d'entrée le plus concret pour mettre les vector databases en production. Maîtrisez ce pattern et vous serez capable de construire des assistants documentaires, des chatbots FAQ, des moteurs de recherche intelligents — le tout avec vos propres données privées.
