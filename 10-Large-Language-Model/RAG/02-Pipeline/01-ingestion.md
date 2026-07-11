# 01 — Pipeline d'Ingestion

## Vue d'ensemble

L'ingestion est la phase offline du RAG : on prend des documents bruts et on les transforme en vecteurs stockés dans une base vectorielle. Cette phase est exécutée une fois lors de la mise en place du système, puis de manière incrémentale à chaque ajout de nouveau document.

```
Sources                Document Loaders         Text Splitters
PDF, HTML, TXT ──────► page_content + metadata ──► chunks
DOCX, CSV, API                                       │
                                                      ▼
                                             Embedding Model
                                          chunk → [0.12, -0.34, ...]
                                                      │
                                                      ▼
                                              Vector Store
                                           (Chroma, FAISS, Qdrant)
```

---

## 1. Document Loaders — charger les sources

### Fichiers locaux

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    CSVLoader,
    JSONLoader,
)

# --- PDF ---
loader_pdf = PyPDFLoader("rapport_annuel.pdf")
pages = loader_pdf.load()
print(f"PDF chargé : {len(pages)} pages")
print(f"Métadonnées page 1 : {pages[0].metadata}")
# {'source': 'rapport_annuel.pdf', 'page': 0}

# --- Texte ---
loader_txt = TextLoader("notes.txt", encoding="utf-8")
docs_txt = loader_txt.load()

# --- Word (DOCX) ---
loader_docx = UnstructuredWordDocumentLoader("contrat.docx")
docs_docx = loader_docx.load()

# --- CSV ---
loader_csv = CSVLoader(
    file_path="produits.csv",
    csv_args={
        "delimiter": ";",
        "quotechar": '"',
    },
    source_column="nom_produit",  # Colonne utilisée comme source dans les métadonnées
)
docs_csv = loader_csv.load()
print(f"CSV chargé : {len(docs_csv)} lignes")
```

### Charger un répertoire entier

```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

# Charger tous les PDFs d'un répertoire
loader_dir = DirectoryLoader(
    path="./documents/",
    glob="**/*.pdf",           # Pattern de fichiers
    loader_cls=PyPDFLoader,    # Loader à utiliser
    show_progress=True,        # Barre de progression
    use_multithreading=True,   # Parallélisation
)

tous_les_docs = loader_dir.load()
print(f"Total documents chargés : {len(tous_les_docs)}")

# Regrouper par source
from collections import Counter
sources = Counter(doc.metadata["source"] for doc in tous_les_docs)
for source, count in sources.most_common(5):
    print(f"  {source}: {count} pages")
```

### Pages web

```python
from langchain_community.document_loaders import WebBaseLoader
import bs4

# Charger une page web avec filtrage HTML
loader_web = WebBaseLoader(
    web_paths=["https://python.langchain.com/docs/introduction/"],
    bs_kwargs={
        "parse_only": bs4.SoupStrainer(
            class_=("article", "main-content", "docusaurus-content")
        )
    },
)
docs_web = loader_web.load()
print(f"Page web chargée : {len(docs_web[0].page_content)} chars")

# Charger plusieurs URLs en parallèle
loader_multi = WebBaseLoader([
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
])
docs_multi = loader_multi.load()
```

### YouTube — transcriptions

```python
from langchain_community.document_loaders import YoutubeLoader

loader_yt = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    add_video_info=True,
    language=["fr", "en"],   # Langues préférées pour les sous-titres
)
transcription = loader_yt.load()
print(transcription[0].page_content[:500])
```

---

## 2. Preprocessing — nettoyer le texte

Avant de chunker, il est souvent nécessaire de nettoyer le texte extrait.

```python
import re

def nettoyer_texte(texte: str) -> str:
    """Nettoie le texte extrait d'un PDF."""
    # Supprimer les caractères de contrôle (sauf \n)
    texte = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', texte)

    # Normaliser les espaces multiples
    texte = re.sub(r' {2,}', ' ', texte)

    # Supprimer les lignes vides répétées (plus de 2)
    texte = re.sub(r'\n{3,}', '\n\n', texte)

    # Supprimer les numéros de page seuls sur une ligne
    texte = re.sub(r'^\s*\d+\s*$', '', texte, flags=re.MULTILINE)

    # Nettoyer les en-têtes/pieds de page répétitifs (heuristique)
    lignes = texte.split('\n')
    # Supprimer les lignes de moins de 5 caractères (souvent des artefacts)
    lignes = [l for l in lignes if len(l.strip()) > 5 or l.strip() == '']
    texte = '\n'.join(lignes)

    return texte.strip()


def preparer_documents(docs):
    """Applique le nettoyage à tous les documents chargés."""
    for doc in docs:
        doc.page_content = nettoyer_texte(doc.page_content)
    # Supprimer les documents vides après nettoyage
    docs = [doc for doc in docs if len(doc.page_content.strip()) > 50]
    return docs

# Utilisation
pages_propres = preparer_documents(pages)
print(f"Documents après nettoyage : {len(pages_propres)} (vs {len(pages)} avant)")
```

---

## 3. Text Splitting — découper en chunks

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Splitter avec comptage en tokens (plus précis que les caractères)
import tiktoken

def longueur_en_tokens(texte: str) -> int:
    """Compte les tokens GPT-4 dans un texte."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(texte))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,           # En tokens
    chunk_overlap=50,         # En tokens
    length_function=longueur_en_tokens,  # Fonction de mesure
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
)

chunks = splitter.split_documents(pages_propres)

# Statistiques
tailles = [longueur_en_tokens(c.page_content) for c in chunks]
print(f"Chunks produits : {len(chunks)}")
print(f"Tokens min/max/moy : {min(tailles)} / {max(tailles)} / {sum(tailles)//len(tailles)}")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant les chunks produits avec leurs métadonnées et tailles, après avoir affiché les statistiques de distribution
> **Expliquer :** Lancer le script en direct sur un vrai PDF. Montrer la différence entre `len(pages)` et `len(chunks)`. Afficher 2-3 chunks dans le terminal pour que les apprenants voient concrètement à quoi ressemble un chunk. Mettre en évidence les métadonnées (source, page). Modifier `chunk_size` en direct (200 vs 1000) et montrer l'impact.

---

## 4. Embedding Models — vectoriser

### OpenAI Embeddings (cloud)

```python
from langchain_openai import OpenAIEmbeddings
import time

# Modèles disponibles
# text-embedding-3-small : 1536 dim, $0.02/1M tokens — recommandé
# text-embedding-3-large : 3072 dim, $0.13/1M tokens — haute précision
# text-embedding-ada-002  : 1536 dim, $0.10/1M tokens — ancien modèle

embeddings_openai = OpenAIEmbeddings(
    model="text-embedding-3-small",
    # dimensions=512,  # Réduire la dimension (économise de la mémoire)
)

# Tester l'embedding d'un texte
test_texte = "Quelle est la politique de remboursement ?"
debut = time.time()
vecteur = embeddings_openai.embed_query(test_texte)
duree = time.time() - debut

print(f"Dimensions : {len(vecteur)}")           # 1536
print(f"Plage de valeurs : [{min(vecteur):.3f}, {max(vecteur):.3f}]")
print(f"Latence : {duree*1000:.0f}ms")
```

### Embeddings locaux avec Ollama

```python
from langchain_ollama import OllamaEmbeddings

# Prérequis : ollama pull nomic-embed-text
embeddings_local = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",
)

vecteur_local = embeddings_local.embed_query("Test d'embedding local")
print(f"Dimensions (nomic-embed-text) : {len(vecteur_local)}")  # 768
```

### Embeddings avec sentence-transformers

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

# Modèles multilingues performants
embeddings_hf = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",       # Multilingue, 1024 dim
    # model_name="all-MiniLM-L6-v2",  # Anglais, 384 dim, très rapide
    model_kwargs={"device": "cpu"},  # "cuda" si GPU disponible
    encode_kwargs={"normalize_embeddings": True},  # Normalisation L2
)

vecteur_hf = embeddings_hf.embed_query("Bonjour le monde")
print(f"Dimensions (bge-m3) : {len(vecteur_hf)}")  # 1024
```

### Calculer la similarité cosinus manuellement

```python
import numpy as np

def similarite_cosinus(v1: list[float], v2: list[float]) -> float:
    """Calcule la similarité cosinus entre deux vecteurs."""
    a = np.array(v1)
    b = np.array(v2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# Démonstration
phrases = [
    "La politique de remboursement prévoit 30 jours.",
    "Les conditions de retour permettent un remboursement sous un mois.",
    "Le chat mange une souris dans le jardin.",
]

vecteurs = embeddings_openai.embed_documents(phrases)

# Comparer les phrases deux à deux
for i in range(len(phrases)):
    for j in range(i+1, len(phrases)):
        sim = similarite_cosinus(vecteurs[i], vecteurs[j])
        print(f"Sim({i+1},{j+1}) = {sim:.3f}")
# Sim(1,2) = 0.921  ← très similaires (même sens)
# Sim(1,3) = 0.312  ← très différents
# Sim(2,3) = 0.298  ← très différents
```

---

## 5. Vector Stores — stocker et persister

### Chroma — le standard de développement

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# --- Créer depuis des documents ---
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="ma_collection",
    persist_directory="./chroma_db",  # Persistance sur disque
)

print(f"Collection : {vectorstore._collection.count()} documents")

# --- Charger une collection existante ---
vectorstore_existant = Chroma(
    collection_name="ma_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

# --- Ajouter des documents à une collection existante ---
nouveaux_chunks = splitter.split_documents(nouveaux_docs)
vectorstore_existant.add_documents(nouveaux_chunks)
```

### FAISS — pour la vitesse maximale

```python
from langchain_community.vectorstores import FAISS

# Créer l'index FAISS
vectorstore_faiss = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings,
)

# Sauvegarder sur disque
vectorstore_faiss.save_local("./faiss_index")

# Charger depuis le disque
vectorstore_faiss_loaded = FAISS.load_local(
    folder_path="./faiss_index",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,  # Requis depuis la 0.2.0
)
```

### Qdrant — pour la production

```python
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Client Qdrant local
client = QdrantClient(path="./qdrant_local")

# Créer la collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,           # Dimensions des embeddings OpenAI
        distance=Distance.COSINE,
    ),
)

vectorstore_qdrant = Qdrant(
    client=client,
    collection_name="documents",
    embeddings=embeddings,
)

vectorstore_qdrant.add_documents(chunks)
```

---

## 6. Ingestion incrémentale — éviter de ré-indexer

En production, on ne veut pas ré-indexer tous les documents à chaque mise à jour. LangChain propose un `RecordManager` pour gérer l'ingestion incrémentale.

```python
from langchain.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Vector store cible
vectorstore = Chroma(
    collection_name="docs_production",
    embedding_function=embeddings,
    persist_directory="./chroma_prod"
)

# Record manager : suit quels documents ont déjà été indexés
record_manager = SQLRecordManager(
    namespace="chroma/docs_production",
    db_url="sqlite:///record_manager.db",
)
record_manager.create_schema()

# Première ingestion
result = index(
    chunks,
    record_manager,
    vectorstore,
    cleanup="incremental",      # Ne supprime pas les anciens docs
    source_id_key="source",     # Clé de déduplication
)
print(f"Ajoutés : {result['num_added']}, Mis à jour : {result['num_updated']}, Ignorés : {result['num_skipped']}")

# Deuxième ingestion avec les mêmes documents → tout est ignoré
result2 = index(chunks, record_manager, vectorstore, cleanup="incremental", source_id_key="source")
print(f"Deuxième passe — Ignorés : {result2['num_skipped']}")  # Tous ignorés

# Ingestion avec nouveaux + anciens documents (cleanup="full" supprime les obsolètes)
result3 = index(
    chunks + nouveaux_chunks,
    record_manager,
    vectorstore,
    cleanup="full",         # Supprime les docs qui ne sont plus dans la liste
    source_id_key="source",
)
print(f"Suppressions : {result3['num_deleted']}")
```

---

## 7. Pipeline d'ingestion complet

Voici un pipeline d'ingestion production-ready, réutilisable :

```python
# ingestion_pipeline.py
from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from typing import Optional
import tiktoken

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.indexes import SQLRecordManager, index

# Configuration
DOCUMENTS_DIR = "./documents/"
CHROMA_DIR = "./chroma_db/"
CHUNK_SIZE = 500       # tokens
CHUNK_OVERLAP = 50     # tokens
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "knowledge_base"

enc = tiktoken.get_encoding("cl100k_base")

def nb_tokens(texte: str) -> int:
    return len(enc.encode(texte))


def charger_documents(dossier: str):
    """Charge tous les PDFs d'un dossier."""
    loader = DirectoryLoader(
        dossier,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    docs = loader.load()
    print(f"[Ingestion] {len(docs)} pages chargées depuis {dossier}")
    return docs


def chunker_documents(docs):
    """Découpe les documents en chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=nb_tokens,
    )
    chunks = splitter.split_documents(docs)
    print(f"[Ingestion] {len(chunks)} chunks produits")
    return chunks


def indexer_chunks(chunks, persist_directory: str = CHROMA_DIR):
    """Indexe les chunks dans Chroma avec gestion incrémentale."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    record_manager = SQLRecordManager(
        namespace=f"chroma/{COLLECTION_NAME}",
        db_url=f"sqlite:///{persist_directory}/record_manager.db",
    )
    record_manager.create_schema()

    result = index(
        chunks,
        record_manager,
        vectorstore,
        cleanup="incremental",
        source_id_key="source",
    )

    print(f"[Ingestion] Résultat :")
    print(f"  - Ajoutés   : {result['num_added']}")
    print(f"  - Mis à jour : {result['num_updated']}")
    print(f"  - Ignorés   : {result['num_skipped']}")
    print(f"  - Supprimés : {result['num_deleted']}")

    return vectorstore


def pipeline_ingestion(dossier: str = DOCUMENTS_DIR) -> Chroma:
    """Pipeline complet : charger → chunker → indexer."""
    print("=== Démarrage de l'ingestion ===")
    docs = charger_documents(dossier)
    chunks = chunker_documents(docs)
    vectorstore = indexer_chunks(chunks)
    print("=== Ingestion terminée ===")
    return vectorstore


if __name__ == "__main__":
    vs = pipeline_ingestion()
    # Test rapide
    resultats = vs.similarity_search("test query", k=2)
    print(f"\nTest retrieval : {len(resultats)} résultats trouvés")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution du pipeline complet `ingestion_pipeline.py` dans le terminal, avec le rapport d'indexation final (ajoutés/ignorés/supprimés) et le test de retrieval
> **Expliquer :** Lancer le pipeline sur un vrai dossier de PDFs. Montrer la progression (barre de chargement). Puis lancer une deuxième fois sans changer les fichiers → tous les chunks seront ignorés (pas de ré-indexation). Ajouter un nouveau PDF dans le dossier, relancer → seul le nouveau document est ajouté. C'est la démonstration de l'ingestion incrémentale.

---

## Estimation des coûts d'embedding

```python
import tiktoken

def estimer_cout_ingestion(dossier: str, prix_par_million: float = 0.02) -> None:
    """Estime le coût d'indexation d'un dossier de PDFs."""
    from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

    enc = tiktoken.get_encoding("cl100k_base")
    loader = DirectoryLoader(dossier, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    total_tokens = sum(len(enc.encode(doc.page_content)) for doc in docs)
    cout = (total_tokens / 1_000_000) * prix_par_million

    print(f"Documents     : {len(docs)} pages")
    print(f"Total tokens  : {total_tokens:,}")
    print(f"Coût estimé   : ${cout:.4f} (text-embedding-3-small)")

# Exemple : 1000 pages PDF ≈ 500 000 tokens ≈ $0.01
estimer_cout_ingestion("./documents/")
```

---

## Récapitulatif

| Étape | Outil LangChain | Points clés |
|-------|----------------|-------------|
| Chargement | `DirectoryLoader`, `PyPDFLoader` | Métadonnées source automatiques |
| Nettoyage | Custom | Supprimer artefacts PDF |
| Chunking | `RecursiveCharacterTextSplitter` | Mesure en tokens, pas en chars |
| Embedding | `OpenAIEmbeddings` | `text-embedding-3-small` = bon rapport qualité/prix |
| Stockage | `Chroma` | `persist_directory` pour la persistance |
| Incrémental | `SQLRecordManager` + `index()` | Évite la ré-indexation |

La suite : [02-retrieval.md](./02-retrieval.md) — Stratégies de recherche et reranking
