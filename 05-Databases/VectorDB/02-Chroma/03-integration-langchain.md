# Chroma — Intégration avec LangChain

LangChain abstrait la vector database derrière une interface uniforme. Vous pouvez changer de vector DB (Chroma → Qdrant → Pinecone) avec un minimum de changements.

---

## 1. Création depuis des documents

```python
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configurer le modèle d'embedding
embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-mpnet-base-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Préparer les documents
documents = [
    Document(page_content="Python est utilisé pour le data engineering.", metadata={"source": "guide_python.txt"}),
    Document(page_content="SQL est le langage standard des bases de données relationnelles.", metadata={"source": "guide_sql.txt"}),
    Document(page_content="Docker permet de containeriser les applications.", metadata={"source": "guide_docker.txt"}),
    Document(page_content="Kafka est une plateforme de streaming de données.", metadata={"source": "guide_kafka.txt"}),
    Document(page_content="Spark traite les données massives en parallèle.", metadata={"source": "guide_spark.txt"}),
]

# Chunker les documents (ici déjà courts, mais c'est le bon pattern)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(documents)

# Créer/charger le vector store
vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory="./chroma_langchain_db",
    collection_name="tech_docs"
)

print(f"Documents stockés : {vectorstore._collection.count()}")
```

---

## 2. Recherche avec LangChain

```python
# Recherche par similarité
docs = vectorstore.similarity_search(
    query="Comment containeriser une application ?",
    k=3
)

for doc in docs:
    print(f"\nSource : {doc.metadata.get('source')}")
    print(f"Contenu : {doc.page_content[:100]}")

# Recherche avec scores
docs_with_scores = vectorstore.similarity_search_with_score(
    query="base de données",
    k=3
)

for doc, score in docs_with_scores:
    print(f"Score : {score:.4f} | {doc.page_content[:60]}")

# Recherche avec filtre
docs = vectorstore.similarity_search(
    query="technologie de streaming",
    k=3,
    filter={"source": "guide_kafka.txt"}
)
```

---

## 3. Utiliser Chroma comme Retriever dans une chaîne RAG

```python
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Charger le vectorstore existant
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
vectorstore = Chroma(
    persist_directory="./chroma_langchain_db",
    embedding_function=embeddings,
    collection_name="tech_docs"
)

# Configurer le retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",   # ou "mmr" ou "similarity_score_threshold"
    search_kwargs={
        "k": 4,                    # Nombre de documents à récupérer
        # "fetch_k": 20,           # Pour MMR : nombre de candidats à considérer
        # "lambda_mult": 0.5,      # Pour MMR : diversité (0=max diversité, 1=max similarité)
    }
)

# Prompt personnalisé en français
prompt_template = """Vous êtes un assistant technique. Utilisez le contexte suivant pour répondre
à la question. Si vous ne trouvez pas la réponse dans le contexte, dites-le clairement.

Contexte :
{context}

Question : {question}

Réponse :"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Chaîne RAG complète
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff" = concat tous les docs dans le prompt
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)

# Interroger
response = qa_chain.invoke({"query": "Comment traiter des données massives ?"})

print("Réponse :", response['result'])
print("\nSources utilisées :")
for doc in response['source_documents']:
    print(f"  - {doc.metadata.get('source')} : {doc.page_content[:60]}...")
```

---

## 4. Chargement de fichiers PDF et ingestion

```python
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

def ingest_pdf_folder(pdf_folder: str, db_path: str, collection_name: str):
    """
    Ingère tous les PDFs d'un dossier dans Chroma.
    """
    # 1. Charger tous les PDFs
    loader = DirectoryLoader(
        pdf_folder,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    print(f"Chargés : {len(documents)} pages depuis {pdf_folder}")

    # 2. Chunker
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True  # Ajoute la position du chunk dans la métadonnée
    )
    chunks = splitter.split_documents(documents)
    print(f"Chunks générés : {len(chunks)}")

    # 3. Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-mpnet-base-v2"
    )

    # 4. Insérer dans Chroma
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=db_path,
        collection_name=collection_name
    )

    print(f"Ingestion terminée. {vectorstore._collection.count()} vecteurs stockés dans '{db_path}'")
    return vectorstore

# Utilisation
# pip install pypdf
vectorstore = ingest_pdf_folder(
    pdf_folder="./documents_pdf/",
    db_path="./chroma_pdf_db",
    collection_name="pdf_docs"
)
```

---

## Résumé

Chroma DB est l'outil idéal pour :
- Développer rapidement un prototype de recherche sémantique ou RAG
- Travailler en local sans infrastructure lourde
- Intégrer facilement avec LangChain

Ses limites :
- Non conçu pour des volumes très larges (> quelques millions de vecteurs)
- Pas d'interface web native
- Moins de fonctionnalités avancées que Qdrant (filtres complexes, sharding)
