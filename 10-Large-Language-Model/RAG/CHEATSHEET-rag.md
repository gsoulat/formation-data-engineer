# CHEATSHEET — RAG avec LangChain

## Installation rapide

```bash
pip install langchain langchain-openai langchain-chroma langchain-community
pip install pypdf tiktoken python-dotenv ragas datasets
# Pour le RAG local
pip install langchain-ollama sentence-transformers
```

---

## Pipeline RAG minimal

```python
from dotenv import load_dotenv; load_dotenv()
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Indexation
pages = PyPDFLoader("doc.pdf").load()
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(pages)
vs = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory="./db")
retriever = vs.as_retriever(search_kwargs={"k": 4})

# Chaîne
prompt = ChatPromptTemplate.from_messages([
    ("system", "Réponds en te basant uniquement sur :\n{context}"),
    ("human", "{question}")
])
chain = ({"context": retriever | (lambda d: "\n\n".join(x.page_content for x in d)),
          "question": RunnablePassthrough()} | prompt | ChatOpenAI() | StrOutputParser())

reponse = chain.invoke("Ma question ?")
```

---

## Document Loaders

```python
from langchain_community.document_loaders import (
    PyPDFLoader,                          # PDF
    TextLoader,                           # .txt
    WebBaseLoader,                        # URL web
    DirectoryLoader,                      # Répertoire entier
    UnstructuredWordDocumentLoader,       # DOCX
    CSVLoader,                            # CSV
    JSONLoader,                           # JSON
)

# Répertoire entier
loader = DirectoryLoader("./docs/", glob="**/*.pdf",
                          loader_cls=PyPDFLoader, show_progress=True)
docs = loader.load()
```

---

## Text Splitters

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,  # Défaut — coupe aux séparateurs naturels
    CharacterTextSplitter,           # Coupe fixe sur un séparateur
    TokenTextSplitter,               # Basé sur les tokens
    MarkdownHeaderTextSplitter,      # Respecte les titres Markdown
    HTMLHeaderTextSplitter,          # Respecte les balises HTML
)
from langchain_experimental.text_splitter import SemanticChunker  # Sémantique

# Le plus polyvalent (compter en tokens)
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=lambda t: len(enc.encode(t)),
)

# Markdown avec titres
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)
```

---

## Embedding Models

```python
# OpenAI (cloud)
from langchain_openai import OpenAIEmbeddings
emb = OpenAIEmbeddings(model="text-embedding-3-small")  # 1536 dim, $0.02/1M tokens

# Ollama (local)
from langchain_ollama import OllamaEmbeddings
emb = OllamaEmbeddings(model="nomic-embed-text")  # 768 dim, gratuit

# sentence-transformers (local)
from langchain_community.embeddings import HuggingFaceEmbeddings
emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # 384 dim, gratuit
emb = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")        # 1024 dim, multilingue
```

---

## Vector Stores

```python
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

# Chroma — créer
vs = Chroma.from_documents(chunks, embeddings, persist_directory="./db")
# Chroma — charger
vs = Chroma(collection_name="col", embedding_function=emb, persist_directory="./db")
# Chroma — ajouter des documents
vs.add_documents(nouveaux_chunks)
# Chroma — nombre de vecteurs
vs._collection.count()

# FAISS — créer
vs = FAISS.from_documents(chunks, embeddings)
vs.save_local("./faiss_index")
# FAISS — charger
vs = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
```

---

## Retrievers

```python
# Similarity search (défaut)
r = vs.as_retriever(search_kwargs={"k": 4})

# MMR (diversification)
r = vs.as_retriever(search_type="mmr",
                    search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.5})

# Avec filtre métadonnées
r = vs.as_retriever(search_kwargs={"k": 4, "filter": {"source": "doc.pdf"}})

# Hybrid BM25 + vectoriel
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
bm25 = BM25Retriever.from_documents(chunks); bm25.k = 4
hybrid = EnsembleRetriever(retrievers=[bm25, vs.as_retriever()], weights=[0.4, 0.6])

# Reranking
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
reranker = CohereRerank(model="rerank-multilingual-v3.0", top_n=4)
ranked_r = ContextualCompressionRetriever(base_compressor=reranker, base_retriever=base_r)

# Multi-query
from langchain.retrievers.multi_query import MultiQueryRetriever
mq_r = MultiQueryRetriever.from_llm(retriever=r, llm=llm)

# Parent Document
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
pdr = ParentDocumentRetriever(
    vectorstore=vs, docstore=InMemoryStore(),
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=200),
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=2000),
)
```

---

## Patterns LCEL RAG

```python
# Chaîne RAG simple
rag = ({"context": retriever | fmt_fn, "question": RunnablePassthrough()}
       | prompt | llm | StrOutputParser())

# Avec sources retournées
from langchain_core.runnables import RunnableParallel
rag_with_src = RunnableParallel(reponse=rag, sources=retriever)
result = rag_with_src.invoke("question")  # {"reponse": ..., "sources": [...]}

# Streaming
for token in rag.stream("question"):
    print(token, end="", flush=True)

# Batch
reponses = rag.batch(["Q1", "Q2", "Q3"])  # Traitement parallèle
```

---

## RAG Conversationnel

```python
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

PROMPT_CTX = ChatPromptTemplate.from_messages([
    ("system", "Reformule la question en standalone."),
    MessagesPlaceholder("chat_history"), ("human", "{input}")
])
PROMPT_ANS = ChatPromptTemplate.from_messages([
    ("system", "Réponds en te basant sur :\n{context}"),
    MessagesPlaceholder("chat_history"), ("human", "{input}")
])

history_retriever = create_history_aware_retriever(llm, retriever, PROMPT_CTX)
qa_chain = create_stuff_documents_chain(llm, PROMPT_ANS)
rag_chain = create_retrieval_chain(history_retriever, qa_chain)

store = {}
chatbot = RunnableWithMessageHistory(
    rag_chain, lambda sid: store.setdefault(sid, ChatMessageHistory()),
    input_messages_key="input", history_messages_key="chat_history",
    output_messages_key="answer",
)

r = chatbot.invoke({"input": "Question ?"}, config={"configurable": {"session_id": "s1"}})
print(r["answer"])
```

---

## RAGAS — Évaluation

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from datasets import Dataset

dataset = Dataset.from_dict({
    "question":    ["Q1", "Q2"],
    "answer":      ["R1 générée", "R2 générée"],
    "contexts":    [["chunk1a", "chunk1b"], ["chunk2a"]],
    "ground_truth":["R1 ref", "R2 ref"],
})

resultats = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    llm=LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini")),
    embeddings=LangchainEmbeddingsWrapper(OpenAIEmbeddings()),
)

df = resultats.to_pandas()
print(df[["question", "faithfulness", "answer_relevancy"]].to_string())
```

---

## Ingestion incrémentale

```python
from langchain.indexes import SQLRecordManager, index

record_manager = SQLRecordManager("chroma/col", db_url="sqlite:///rm.db")
record_manager.create_schema()

result = index(chunks, record_manager, vectorstore,
               cleanup="incremental", source_id_key="source")
# {"num_added": X, "num_updated": Y, "num_skipped": Z, "num_deleted": W}
```

---

## RAG local (Ollama)

```bash
# Setup
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings

llm = ChatOllama(model="llama3.2:3b", temperature=0)
emb = OllamaEmbeddings(model="nomic-embed-text")
# Ensuite : même code que RAG cloud
```

---

## Diagnostic rapide

| Problème | Cause probable | Solution |
|---------|----------------|----------|
| Réponses imprécises | Mauvais chunks récupérés | Augmenter k, essayer MMR ou hybrid |
| Hallucinations | Prompt trop permissif | Ajouter "Ne génère jamais d'info absente du contexte" |
| Réponses hors-sujet | Embeddings faibles | Changer de modèle d'embedding |
| Contexte trop long | k trop élevé | Réduire k ou utiliser le reranking |
| Chunks trop fragmentés | chunk_size trop petit | Augmenter chunk_size ou utiliser ParentDocumentRetriever |
| Mots-clés manqués | Embeddings sémantiques seuls | Ajouter BM25 (hybrid search) |
| Faithfulness RAGAS bas | LLM hallucine | Renforcer le prompt, réduire temperature |
| Context Recall RAGAS bas | Retriever insuffisant | Augmenter k, reranking |

---

## Coûts OpenAI (estimatifs 2024-2025)

| Opération | Modèle | Coût |
|-----------|--------|------|
| Embedding 1M tokens | text-embedding-3-small | $0.02 |
| Embedding 1M tokens | text-embedding-3-large | $0.13 |
| Génération 1M tokens input | gpt-4o-mini | $0.15 |
| Génération 1M tokens output | gpt-4o-mini | $0.60 |
| Génération 1M tokens input | gpt-4o | $2.50 |
| Indexation 1000 pages PDF | text-embedding-3-small | ~$0.01 |
| 1000 questions RAG | gpt-4o-mini | ~$0.10-0.50 |

---

## Checklist mise en production

```
Indexation
  ☐ Chunking testé et validé (distribution des tailles)
  ☐ Métadonnées enrichies (source, date, type)
  ☐ Ingestion incrémentale avec RecordManager
  ☐ Coût d'indexation estimé

Retrieval
  ☐ Recall@k mesuré sur jeu de test
  ☐ Stratégie choisie (simple / MMR / hybrid / reranking)
  ☐ Filtres par métadonnées si besoin

Génération
  ☐ Prompt testé avec des questions hors-sujet
  ☐ Sources retournées avec les réponses
  ☐ Troncature du contexte implémentée
  ☐ Temperature = 0 pour les réponses factuelles

Évaluation
  ☐ Jeu de test créé (min. 20 questions)
  ☐ RAGAS lancé sur le jeu de test
  ☐ Seuils définis : faithfulness > 0.80, context_recall > 0.75

Observabilité
  ☐ LangSmith activé (LANGCHAIN_TRACING_V2=true)
  ☐ Logs des erreurs implémentés
```
