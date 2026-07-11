# CHEATSHEET — Vector Databases

Référence rapide pour les opérations courantes avec les vector databases.

---

## Embeddings

### Sentence-Transformers (local, gratuit)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')  # 768 dim, multilingue
# model = SentenceTransformer('all-MiniLM-L6-v2')                   # 384 dim, anglais, rapide

# Une phrase
vec = model.encode("Mon texte", normalize_embeddings=True)          # → ndarray (768,)

# Batch
vecs = model.encode(["texte1", "texte2"], normalize_embeddings=True) # → ndarray (2, 768)

# Similarité cosinus
from sentence_transformers import util
score = util.cos_sim(vec1, vec2).item()  # float entre -1 et 1
```

### OpenAI (cloud, payant)

```python
from openai import OpenAI
client = OpenAI()

# Une phrase
resp = client.embeddings.create(input="Mon texte", model="text-embedding-3-small")
vec = resp.data[0].embedding  # list[float] de 1536 dimensions

# Batch (jusqu'à 2048 inputs)
resp = client.embeddings.create(input=["texte1", "texte2"], model="text-embedding-3-small")
vecs = [item.embedding for item in sorted(resp.data, key=lambda x: x.index)]
```

---

## Chroma DB

### Setup

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")        # Persistant (recommandé)
client = chromadb.Client()                                      # In-memory (éphémère)
client = chromadb.HttpClient(host="localhost", port=8000)      # Serveur HTTP
```

### Collections

```python
# Créer
col = client.create_collection("ma_col", metadata={"hnsw:space": "cosine"})

# Obtenir ou créer (idempotent)
col = client.get_or_create_collection("ma_col", metadata={"hnsw:space": "cosine"})

# Lister / Supprimer
client.list_collections()
client.delete_collection("ma_col")

# Taille
col.count()
```

### CRUD

```python
# Ajouter (avec embeddings précalculés)
col.add(ids=["id1","id2"], embeddings=[[...],[...]], documents=["txt1","txt2"],
        metadatas=[{"cat":"a"},{"cat":"b"}])

# Ajouter (Chroma génère les embeddings automatiquement)
col.add(ids=["id1"], documents=["Mon texte"], metadatas=[{"src":"wiki"}])

# Mettre à jour
col.update(ids=["id1"], documents=["Nouveau texte"])

# Upsert (update + insert si inexistant)
col.upsert(ids=["id1"], documents=["Texte"], metadatas=[{"src":"v2"}])

# Supprimer
col.delete(ids=["id1", "id2"])
col.delete(where={"cat": "obsolete"})

# Récupérer par ID
col.get(ids=["id1"], include=["documents","metadatas"])
```

### Recherche

```python
# Par texte
results = col.query(query_texts=["ma requête"], n_results=5)

# Par vecteur
results = col.query(query_embeddings=[[0.1, 0.2, ...]], n_results=5)

# Avec filtre
results = col.query(
    query_texts=["requête"],
    n_results=5,
    where={"cat": "devops"},                        # Égalité
    # where={"score": {"$gte": 8.0}},              # Numérique
    # where={"$and": [{"cat":"dev"},{"yr":2024}]}, # AND
    # where={"cat": {"$in": ["dev","ops"]}},       # IN
    where_document={"$contains": "Docker"}         # Sur le texte brut
)

# Accéder aux résultats
for i in range(len(results['documents'][0])):
    doc  = results['documents'][0][i]
    dist = results['distances'][0][i]     # distance (cosine: 0=identique, 2=opposé)
    meta = results['metadatas'][0][i]
    id_  = results['ids'][0][i]
    sim  = 1 - dist                       # → similarité entre 0 et 1
```

---

## Qdrant

### Setup

```bash
docker run -d --name qdrant -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)     # Docker
client = QdrantClient(":memory:")                       # In-memory
client = QdrantClient(path="./qdrant_local")           # Fichier local
client = QdrantClient(url="https://...", api_key="...") # Cloud
```

### Collections

```python
from qdrant_client.models import Distance, VectorParams

# Créer
client.create_collection("ma_col", vectors_config=VectorParams(size=768, distance=Distance.COSINE))
# Distance.COSINE | Distance.EUCLID | Distance.DOT

# Lister / Supprimer
[c.name for c in client.get_collections().collections]
client.delete_collection("ma_col")

# Info
client.get_collection("ma_col")  # .points_count, .vectors_count, .status
```

### Upsert

```python
from qdrant_client.models import PointStruct

points = [
    PointStruct(id=1, vector=[0.1, 0.2, ...], payload={"text": "doc1", "cat": "dev"}),
    PointStruct(id=2, vector=[0.3, 0.4, ...], payload={"text": "doc2", "cat": "ops"}),
]
client.upsert(collection_name="ma_col", points=points, wait=True)
```

### Recherche

```python
# Basique
results = client.search("ma_col", query_vector=[0.1,...], limit=5, with_payload=True)

for r in results:
    print(r.score)           # float entre 0 et 1 (cosine)
    print(r.id)
    print(r.payload["text"])

# Avec filtre
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, MatchAny

results = client.search(
    "ma_col",
    query_vector=[0.1,...],
    query_filter=Filter(
        must=[
            FieldCondition(key="cat", match=MatchValue(value="devops")),    # Égalité
            FieldCondition(key="score", range=Range(gte=8.0)),              # Nombre
        ],
        should=[
            FieldCondition(key="cat", match=MatchAny(any=["dev","ops"])),   # IN
        ],
        must_not=[
            FieldCondition(key="active", match=MatchValue(value=False)),    # NOT
        ]
    ),
    limit=5
)
```

### Payload Index (pour accélérer les filtres)

```python
from qdrant_client.models import PayloadSchemaType

client.create_payload_index("ma_col", "cat",   PayloadSchemaType.KEYWORD)  # Strings exactes
client.create_payload_index("ma_col", "score", PayloadSchemaType.FLOAT)    # Nombres décimaux
client.create_payload_index("ma_col", "year",  PayloadSchemaType.INTEGER)  # Entiers
```

### Scroll (tous les points)

```python
offset = None
all_points = []
while True:
    result, offset = client.scroll("ma_col", limit=100, offset=offset, with_payload=True)
    all_points.extend(result)
    if offset is None:
        break
```

---

## LangChain — Vector Stores

### Chroma avec LangChain

```python
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

emb = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")

# Créer depuis documents
vs = Chroma.from_documents(docs, emb, persist_directory="./db", collection_name="col")

# Charger existant
vs = Chroma(persist_directory="./db", embedding_function=emb, collection_name="col")

# Recherche
vs.similarity_search("requête", k=5)
vs.similarity_search_with_score("requête", k=5)                    # → (doc, score)
vs.max_marginal_relevance_search("requête", k=4, fetch_k=20)       # MMR
```

### Qdrant avec LangChain

```python
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

qclient = QdrantClient(host="localhost", port=6333)

# Créer depuis documents
vs = QdrantVectorStore.from_documents(docs, emb, url="http://localhost:6333",
                                       collection_name="col")

# Charger existant
vs = QdrantVectorStore(client=qclient, collection_name="col", embedding=emb)
```

### Retriever

```python
# Similarity
ret = vs.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# MMR
ret = vs.as_retriever(search_type="mmr",
                       search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.5})

# Score threshold
ret = vs.as_retriever(search_type="similarity_score_threshold",
                       search_kwargs={"score_threshold": 0.7, "k": 10})

# Appel
docs = ret.invoke("ma requête")
```

---

## LangChain — Chunking

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_text(text)             # → list[str]
doc_chunks = splitter.split_documents(docs)    # → list[Document] (conserve metadata)
```

---

## Pipeline RAG minimal (LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

prompt = ChatPromptTemplate.from_template("""
Réponds à la question en te basant uniquement sur le contexte.
Si tu ne trouves pas l'info, dis-le clairement.

Contexte : {context}
Question : {question}
Réponse :""")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

answer = rag_chain.invoke("Ma question")
for chunk in rag_chain.stream("Ma question"):   # Streaming
    print(chunk, end="", flush=True)
```

---

## Métriques de distance — référence

| Métrique | Chroma | Qdrant | Plage | Meilleur score | Cas d'usage |
|----------|--------|--------|-------|---------------|-------------|
| Cosinus | `"hnsw:space": "cosine"` | `Distance.COSINE` | [0, 2] distance / [-1,1] sim | sim=1 / dist=0 | Texte |
| Euclidienne | `"hnsw:space": "l2"` | `Distance.EUCLID` | [0, +∞] | 0 | Images |
| Dot Product | `"hnsw:space": "ip"` | `Distance.DOT` | (-∞, +∞) | +∞ | Embeddings normalisés |

```python
# Convertir distance Chroma cosinus → similarité
similarity = 1 - chroma_distance   # distance ∈ [0,2] → sim ∈ [-1,1]

# Qdrant cosinus → déjà un score de similarité (0 à 1 après normalisation)
score = qdrant_result.score        # directement entre 0 et 1
```

---

## Choix rapide

```
Prototype/cours         → Chroma + sentence-transformers
Production self-hosted  → Qdrant + sentence-transformers ou OpenAI
Déjà sur PostgreSQL     → pgvector
SaaS, pas d'infra       → Pinecone
Large scale offline ML  → FAISS
Hybrid search avancé    → Weaviate
```

---

## Commandes Docker Qdrant

```bash
# Démarrer
docker run -d --name qdrant -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant

# Arrêter / Démarrer / Supprimer
docker stop qdrant
docker start qdrant
docker rm -f qdrant

# Dashboard web
open http://localhost:6333/dashboard

# Logs
docker logs qdrant -f

# API health check
curl http://localhost:6333/health
```

---

## Commandes Ollama

```bash
ollama serve                    # Démarrer le serveur Ollama
ollama list                     # Lister les modèles téléchargés
ollama pull llama3.2:3b         # Télécharger un modèle
ollama run llama3.2:3b          # Tester en interactif
ollama rm llama3.2:1b           # Supprimer un modèle
```

```python
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.2:3b", temperature=0)
```
