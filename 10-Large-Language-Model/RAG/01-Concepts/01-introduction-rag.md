# 01 — Introduction au RAG

## Qu'est-ce que le RAG ?

Le **RAG** (Retrieval-Augmented Generation) est une architecture qui améliore les réponses d'un LLM en lui fournissant, au moment de la requête, des documents pertinents récupérés depuis une base de connaissances externe.

Le terme a été introduit dans le papier de recherche de Meta AI en 2020 : *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"* (Lewis et al.). Depuis, c'est devenu l'approche standard pour construire des applications LLM sur des données privées ou récentes.

---

## Le problème que résout le RAG

Les LLM ont trois limitations fondamentales en production :

### 1. Connaissance figée dans le temps

Un modèle GPT-4o a une date de coupure de connaissance. Il ne sait rien des événements postérieurs à son entraînement. Un modèle entraîné en avril 2024 ignore les données de mai 2024 et au-delà.

### 2. Absence de données privées

Un LLM public n'a pas été entraîné sur les documents internes de votre entreprise : vos contrats, vos rapports, votre documentation technique, vos e-mails. Il ne peut pas répondre à des questions spécifiques à votre contexte.

### 3. Hallucinations

Sans source de vérité externe, le LLM invente des réponses plausibles mais fausses. Il confabule des dates, des noms, des faits — avec une assurance trompeuse.

---

## RAG vs Fine-tuning — quand choisir quoi ?

| Critère | RAG | Fine-tuning |
|---------|-----|-------------|
| Données mises à jour fréquemment | Idéal | Difficile (ré-entraîner) |
| Données privées volumineuses | Idéal | Coûteux en VRAM |
| Besoin de citations/sources | Natif | Impossible |
| Nouveau style ou comportement | Limité | Idéal |
| Coût de mise en place | Faible | Élevé |
| Délai de mise en production | Jours | Semaines |
| Contrôle des hallucinations | Excellent | Moyen |

**Règle pratique :** commencez toujours par le RAG. Le fine-tuning est pertinent uniquement pour changer le comportement ou le style du modèle, pas pour lui injecter des connaissances.

---

## Architecture RAG — deux phases

Un système RAG fonctionne en deux phases distinctes :

### Phase 1 — Indexation (offline)

Cette phase est exécutée une fois (ou lors de mises à jour de la base documentaire). Elle peut prendre minutes à heures selon le volume.

```
Documents bruts (PDF, DOCX, HTML, CSV...)
         │
         ▼
    [Document Loader]
    Extraction du texte brut
         │
         ▼
    [Text Splitter]
    Découpage en chunks (morceaux) de taille fixe
         │
         ▼
    [Embedding Model]
    Chaque chunk → vecteur de 1536 dimensions (float)
         │
         ▼
    [Vector Store]
    Stockage des vecteurs + textes (Chroma, FAISS, Pinecone...)
```

### Phase 2 — Requête (online)

Cette phase est exécutée à chaque question utilisateur. Elle doit être rapide (< 2s).

```
Question utilisateur : "Quelle est notre politique de remboursement ?"
         │
         ▼
    [Embedding Model]
    Question → vecteur de 1536 dimensions
         │
         ▼
    [Similarity Search]
    Trouver les k chunks les plus proches dans le vector store
         │
         ▼
    [Prompt Construction]
    Assembler : system prompt + chunks récupérés + question
         │
         ▼
    [LLM]
    Générer une réponse basée sur les chunks fournis
         │
         ▼
    Réponse finale (avec optionnellement les sources citées)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Schéma des deux phases dessiné au tableau ou sur un outil de diagramme (draw.io, Excalidraw), avec des flèches colorées distinguant offline (bleu) et online (vert)
> **Expliquer :** Insister sur la séparation offline/online. La phase d'indexation coûte cher (temps, tokens d'embedding) mais ne se fait qu'une fois. La phase online doit être rapide. Donner un exemple concret : une entreprise qui indexe 10 000 pages de documentation le weekend, et ses employés interrogent le système toute la semaine.

---

## Les composants d'un pipeline RAG

### Document Loaders — charger les sources

LangChain propose plus de 100 loaders différents :

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import (
    PyPDFLoader,          # Fichiers PDF
    TextLoader,           # Fichiers .txt
    WebBaseLoader,        # Pages web
    UnstructuredWordDocumentLoader,  # DOCX
    CSVLoader,            # Fichiers CSV
    JSONLoader,           # Fichiers JSON
    DirectoryLoader,      # Charger tout un répertoire
)

# Exemple : charger un PDF
loader = PyPDFLoader("document.pdf")
pages = loader.load()

print(f"Nombre de pages : {len(pages)}")
print(f"Contenu page 1 : {pages[0].page_content[:200]}")
print(f"Métadonnées : {pages[0].metadata}")
# {'source': 'document.pdf', 'page': 0}
```

Chaque document chargé est un objet `Document` avec :
- `page_content` : le texte extrait
- `metadata` : dict avec la source, le numéro de page, etc.

### Text Splitters — découper intelligemment

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Taille max en caractères
    chunk_overlap=200,    # Chevauchement entre chunks consécutifs
    length_function=len,
)

chunks = splitter.split_documents(pages)
print(f"Nombre de chunks : {len(chunks)}")
print(f"Premier chunk : {chunks[0].page_content[:100]}")
```

### Embedding Models — vectoriser le texte

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Embarquer un seul texte
vecteur = embeddings.embed_query("Quelle est la capitale de France ?")
print(f"Dimensions du vecteur : {len(vecteur)}")  # 1536

# Embarquer plusieurs documents
textes = ["Paris est la capitale.", "Berlin est en Allemagne."]
vecteurs = embeddings.embed_documents(textes)
print(f"Nombre de vecteurs : {len(vecteurs)}")  # 2
```

### Vector Store — stocker et rechercher

```python
from langchain_chroma import Chroma

# Créer le vector store et indexer les chunks
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # Sauvegarde sur disque
)

# Rechercher les chunks pertinents
resultats = vectorstore.similarity_search(
    query="politique de remboursement",
    k=4  # Retourner les 4 chunks les plus proches
)

for doc in resultats:
    print(doc.page_content[:100])
    print(f"Source : {doc.metadata}")
    print("---")
```

---

## Premier RAG complet en 30 lignes

Voici le pipeline RAG minimal fonctionnel :

```python
# rag_minimal.py
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- Phase 1 : Indexation ---
loader = PyPDFLoader("mon_document.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(pages)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# --- Phase 2 : Pipeline de requête ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui répond aux questions en te basant
exclusivement sur le contexte fourni. Si la réponse ne se trouve pas dans
le contexte, dis-le clairement.

Contexte :
{context}"""),
    ("human", "{question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- Interroger le système ---
reponse = rag_chain.invoke("Quelle est la politique de remboursement ?")
print(reponse)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution de `rag_minimal.py` dans le terminal, en montrant les étapes (indexation puis requête) avec les logs affichés
> **Expliquer :** Dérouler le code ligne par ligne. Montrer que la phase d'indexation prend quelques secondes (appels à l'API d'embeddings), puis que la requête est quasi-instantanée. Comparer une question dont la réponse est dans le PDF (bonne réponse) vs une question hors-sujet (le modèle dit qu'il ne sait pas). Insister : le modèle ne génère pas depuis sa mémoire, il lit les chunks.

---

## RAG vs LLM seul — démonstration comparative

Il est crucial de comprendre la différence de qualité entre une réponse avec et sans RAG.

```python
# comparaison_rag_vs_llm.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

# Question sur un document spécifique et privé
question = "Quel est le montant de la prime exceptionnelle prévue à l'article 12 du contrat ?"

# --- Réponse SANS RAG ---
prompt_sans_rag = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant utile."),
    ("human", "{question}")
])
chain_sans_rag = prompt_sans_rag | llm | parser
reponse_sans_rag = chain_sans_rag.invoke({"question": question})

print("=== SANS RAG ===")
print(reponse_sans_rag)
# Réponse probable : hallucination ou "Je n'ai pas accès au contrat"

# --- Réponse AVEC RAG ---
# (en supposant que le contrat a été indexé)
reponse_avec_rag = rag_chain.invoke(question)

print("\n=== AVEC RAG ===")
print(reponse_avec_rag)
# Réponse précise tirée du document
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Les deux réponses côte à côte dans le terminal (ou dans deux fenêtres)
> **Expliquer :** Montrer d'abord la réponse sans RAG — soit une hallucination confiante, soit un refus de répondre. Puis montrer la réponse avec RAG qui cite précisément le document. C'est le moment "wow" de la démonstration. Insister : le LLM est le même dans les deux cas, seul le contexte change.

---

## Les limites du RAG

Comprendre les limites dès le départ évite des surprises en production.

### Limite 1 — La qualité dépend du retrieval

Si les bons chunks ne sont pas récupérés, la réponse sera mauvaise même avec un excellent LLM. C'est le problème de retrieval : `garbage in, garbage out`.

### Limite 2 — La fenêtre de contexte

Un LLM a une fenêtre de contexte limitée (128k tokens pour GPT-4o, 8k pour certains modèles locaux). Si on récupère trop de chunks, on dépasse la limite. Si on en récupère trop peu, on manque des informations.

### Limite 3 — Les documents mal structurés

Les PDFs scannés (images), les tableaux complexes, les formules mathématiques sont difficiles à extraire fidèlement. La qualité du loader impacte directement la qualité du RAG.

### Limite 4 — Les questions multi-hop

Une question comme "Comparer les politiques de congés des filiales A et B" nécessite de récupérer des chunks de deux documents différents et de les synthétiser. Le RAG simple ne gère pas bien ce cas.

### Limite 5 — Le coût des embeddings

Indexer 1 million de tokens avec `text-embedding-3-small` coûte ~$0.02. C'est négligeable, mais ré-indexer fréquemment un corpus volumineux peut devenir coûteux.

---

## Les dimensions d'un bon système RAG

```
Qualité RAG = f(qualité_chunking, qualité_embeddings, qualité_retrieval, qualité_prompt, qualité_llm)
```

Chaque composant contribue à la qualité finale. Un composant défaillant dégrade l'ensemble du système, peu importe la qualité des autres.

| Composant | Impact | Levier principal |
|-----------|--------|-----------------|
| Chunking | Élevé | Taille des chunks, chevauchement, stratégie |
| Embeddings | Élevé | Choix du modèle, domaine spécialisé |
| Retrieval | Très élevé | k, MMR, reranking, hybrid search |
| Prompt | Moyen | Instructions claires, format de sortie |
| LLM | Moyen | Modèle choisi, température |

---

## L'écosystème d'outils RAG

### Vector Stores

| Outil | Type | Usage |
|-------|------|-------|
| **Chroma** | Local / Cloud | Développement, production légère |
| **FAISS** | Local | Recherche ultrarapide en mémoire |
| **Pinecone** | Cloud managé | Production à grande échelle |
| **Qdrant** | Local / Cloud | Production, typage fort |
| **Weaviate** | Local / Cloud | Recherche hybride native |
| **pgvector** | PostgreSQL | Si vous avez déjà Postgres |

### Embedding Models

| Modèle | Fournisseur | Dimensions | Coût |
|--------|-------------|------------|------|
| text-embedding-3-small | OpenAI | 1536 | $0.02/1M tokens |
| text-embedding-3-large | OpenAI | 3072 | $0.13/1M tokens |
| nomic-embed-text | Ollama (local) | 768 | Gratuit |
| all-MiniLM-L6-v2 | sentence-transformers | 384 | Gratuit |
| bge-m3 | BAAI (local) | 1024 | Gratuit, multilingue |

### Frameworks

| Framework | Forces |
|-----------|--------|
| **LangChain** | Écosystème complet, nombreux loaders, LCEL |
| **LlamaIndex** | Spécialisé RAG, index avancés |
| **Haystack** | Production-ready, pipelines déclaratifs |

---

## Récapitulatif

| Concept | Définition |
|---------|------------|
| RAG | Enrichir le prompt LLM avec des documents récupérés dynamiquement |
| Indexation (offline) | Charger → Découper → Embedder → Stocker |
| Requête (online) | Embedder la question → Chercher → Construire le prompt → Générer |
| Vector Store | Base de données spécialisée dans la recherche par similarité vectorielle |
| Retriever | Composant qui encapsule la logique de recherche |
| `k` | Nombre de chunks retournés par le retriever |

La suite : [02-chunking-strategies.md](./02-chunking-strategies.md) — Stratégies de découpage de documents
