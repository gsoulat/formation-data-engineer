# Exercice 02 — RAG 100% Local

## Objectif

Construire un système RAG entièrement local : aucune clé API, aucune donnée envoyée à l'extérieur. Vous utiliserez Ollama pour les LLM et les embeddings, Chroma comme vector store, et sentence-transformers comme alternative d'embedding.

Ce pattern est indispensable pour :
- Les projets avec des données confidentielles (santé, finance, RH)
- Les environnements sans accès internet
- Les budgets limités

## Durée estimée : 90 minutes

## Prérequis

### Installation d'Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows : télécharger depuis https://ollama.ai/download

# Vérifier l'installation
ollama --version
```

### Téléchargement des modèles

```bash
# LLM pour la génération (choisir selon votre RAM disponible)
ollama pull llama3.2:3b       # 2.0 GB — recommandé si < 8GB RAM
ollama pull llama3.1:8b       # 4.7 GB — meilleur si ≥ 8GB RAM
ollama pull mistral:7b        # 4.1 GB — alternative performante

# Modèle d'embedding
ollama pull nomic-embed-text  # 274 MB — très efficace

# Vérifier les modèles disponibles
ollama list
```

### Packages Python

```bash
pip install langchain langchain-ollama langchain-chroma langchain-community
pip install sentence-transformers chromadb python-dotenv tiktoken
```

Pas besoin de fichier `.env` pour les clés API — tout est local !

---

## Partie 1 — Vérifier les modèles locaux (10 min)

```python
# verification_locale.py
from langchain_ollama import ChatOllama, OllamaEmbeddings
import time

print("=== Vérification des modèles Ollama ===\n")

# 1. Test du LLM
print("1. Test du LLM (llama3.2:3b)...")
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434",
)

debut = time.time()
reponse = llm.invoke("Dis 'Bonjour' en une phrase.")
duree = time.time() - debut
print(f"   Réponse : {reponse.content}")
print(f"   Latence : {duree:.1f}s\n")

# 2. Test des embeddings
print("2. Test des embeddings (nomic-embed-text)...")
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434",
)

debut = time.time()
vecteur = embeddings.embed_query("Test d'embedding local")
duree = time.time() - debut
print(f"   Dimensions : {len(vecteur)}")
print(f"   Latence    : {duree:.1f}s\n")

# 3. Test sentence-transformers (alternative)
print("3. Test sentence-transformers (all-MiniLM-L6-v2)...")
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_hf = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)
debut = time.time()
vecteur_hf = embeddings_hf.embed_query("Test sentence-transformers")
duree = time.time() - debut
print(f"   Dimensions : {len(vecteur_hf)}")
print(f"   Latence    : {duree:.1f}s")

print("\n=== Tous les modèles sont opérationnels ===")
```

**Question :** Comparez les latences entre Ollama embeddings et sentence-transformers. Lequel est le plus rapide sur votre machine ?

---

## Partie 2 — Indexation locale (25 min)

### Étape 2.1 — Charger et chunker les documents

Réutilisez les documents créés dans l'exercice 01, ou créez-en de nouveaux.

```python
# indexation_locale.py
import os
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# === Configuration ===
# Choisissez votre modèle d'embedding local
EMBEDDING_MODE = "sentence_transformers"  # ou "ollama"

CHROMA_DIR = "./chroma_local"
COLLECTION_NAME = "exercice_local"

# === 1. Chargement ===
loader = DirectoryLoader(
    "./documents/",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
documents = loader.load()
print(f"Documents chargés : {len(documents)}")

# === 2. Chunking ===
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
)
chunks = splitter.split_documents(documents)
print(f"Chunks produits  : {len(chunks)}")

# === 3. Embeddings ===
print(f"\nCréation des embeddings ({EMBEDDING_MODE})...")
debut = time.time()

if EMBEDDING_MODE == "ollama":
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434",
    )
else:
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

# === 4. Indexation ===
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_DIR,
)

duree = time.time() - debut
print(f"Indexation terminée en {duree:.1f}s")
print(f"Vecteurs stockés : {vectorstore._collection.count()}")

# === 5. Test de recherche ===
print("\n=== Test de recherche ===")
resultats = vectorstore.similarity_search("garantie produit défectueux", k=3)
for doc in resultats:
    print(f"Source : {doc.metadata['source']}")
    print(f"  {doc.page_content[:120]}...")
    print()
```

**Question :** Comparez le temps d'indexation entre les deux modes d'embedding (ollama vs sentence-transformers). Lequel est plus rapide ?

---

## Partie 3 — Pipeline RAG local (30 min)

### Étape 3.1 — Chaîne RAG avec Ollama

```python
# rag_local.py
import time
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document
from typing import List

# === Configuration ===
LLM_MODEL = "llama3.2:3b"        # Changer selon le modèle téléchargé
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DIR = "./chroma_local"
COLLECTION_NAME = "exercice_local"

# === Composants ===
print(f"Chargement du LLM ({LLM_MODEL})...")
llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
    base_url="http://localhost:11434",
    # num_ctx=4096,    # Taille de la fenêtre de contexte (défaut selon le modèle)
)

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("Composants chargés.\n")

# === Prompt ===
# Note : les modèles locaux sont moins robustes que GPT-4o
# Les instructions doivent être plus simples et directes
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant service client. Réponds en français.
Utilise uniquement les informations du contexte ci-dessous.
Si la réponse n'est pas dans le contexte, dis 'Information non disponible'.

Contexte :
{context}"""),
    ("human", "Question : {question}\nRéponse :")
])

# === Formatage ===
def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(
        f"[{doc.metadata.get('source', '?')}]\n{doc.page_content}"
        for doc in docs
    )

# === Chaîne RAG ===
rag_chain_local = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | PROMPT
    | llm
    | StrOutputParser()
)

# === Test ===
def interroger_local(question: str) -> None:
    print(f"\nQ: {question}")
    debut = time.time()
    reponse = rag_chain_local.invoke(question)
    duree = time.time() - debut
    print(f"R: {reponse}")
    print(f"   (Temps de réponse : {duree:.1f}s)")


# Questions de test
questions = [
    "Quel est le délai pour retourner un produit ?",
    "La garantie couvre-t-elle les dommages par chute ?",
    "Comment contacter le SAV ?",
    "Puis-je payer en chèque ?",
]

print("=== Tests du RAG local ===")
for q in questions:
    interroger_local(q)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le terminal montrant les réponses du RAG local avec les temps de réponse pour chaque question
> **Expliquer :** Comparer les temps de réponse du RAG local (typiquement 3-15 secondes sur CPU) vs le RAG OpenAI (< 2 secondes). Montrer que malgré la latence plus élevée, les réponses sont correctes. Expliquer le trade-off : vitesse vs confidentialité vs coût. Pour des données médicales ou RH, la latence supplémentaire est acceptable.

---

### Étape 3.2 — Streaming pour compenser la latence

```python
# streaming_local.py

# Le streaming améliore l'UX même si la réponse totale prend le même temps
def interroger_streaming(question: str) -> str:
    print(f"\nQ: {question}")
    print("R: ", end="", flush=True)
    reponse_complete = ""
    for token in rag_chain_local.stream(question):
        print(token, end="", flush=True)
        reponse_complete += token
    print()
    return reponse_complete

# Le streaming donne une impression de réactivité
interroger_streaming("Quel est le délai de remboursement après un retour ?")
```

---

## Partie 4 — Comparaison OpenAI vs Local (15 min)

Si vous avez une clé OpenAI, comparez les deux approches :

```python
# comparaison_openai_vs_local.py
import time
from dotenv import load_dotenv
load_dotenv()

# === Configuration OpenAI ===
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma as ChromaOAI

embeddings_oai = OpenAIEmbeddings(model="text-embedding-3-small")
vs_oai = ChromaOAI(
    collection_name="exercice_01",  # Créé dans l'exercice 01
    embedding_function=embeddings_oai,
    persist_directory="./chroma_exercice_01"
)
retriever_oai = vs_oai.as_retriever(search_kwargs={"k": 3})
llm_oai = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# === Configuration Locale ===
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma as ChromaLocal

embeddings_local = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vs_local = ChromaLocal(
    collection_name="exercice_local",
    embedding_function=embeddings_local,
    persist_directory="./chroma_local"
)
retriever_local = vs_local.as_retriever(search_kwargs={"k": 3})
llm_local = ChatOllama(model="llama3.2:3b", temperature=0)

# === Prompt commun ===
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

PROMPT_COMMUN = ChatPromptTemplate.from_messages([
    ("system", "Réponds en français en te basant uniquement sur le contexte.\n\nContexte : {context}"),
    ("human", "Question : {question}\nRéponse :")
])

def creer_chain(retriever, llm):
    return (
        {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
         "question": RunnablePassthrough()}
        | PROMPT_COMMUN | llm | StrOutputParser()
    )

chain_oai = creer_chain(retriever_oai, llm_oai)
chain_local = creer_chain(retriever_local, llm_local)

# === Comparaison ===
questions = [
    "Quelle est la durée de garantie pour les produits reconditionnés ?",
    "Comment initier un retour produit ?",
    "Quels modes de livraison sont disponibles et à quel prix ?",
]

resultats = []

for q in questions:
    print(f"\n{'='*60}")
    print(f"Q: {q}")

    # OpenAI
    debut = time.time()
    r_oai = chain_oai.invoke(q)
    t_oai = time.time() - debut

    # Local
    debut = time.time()
    r_local = chain_local.invoke(q)
    t_local = time.time() - debut

    print(f"\n[OpenAI GPT-4o-mini] ({t_oai:.1f}s)")
    print(f"  {r_oai}")
    print(f"\n[Local llama3.2:3b] ({t_local:.1f}s)")
    print(f"  {r_local}")

    resultats.append({
        "question": q,
        "openai": {"reponse": r_oai, "latence": t_oai},
        "local": {"reponse": r_local, "latence": t_local},
    })

# Résumé
print(f"\n{'='*60}")
print("RÉSUMÉ DES PERFORMANCES")
print(f"{'='*60}")
latences_oai = [r["openai"]["latence"] for r in resultats]
latences_local = [r["local"]["latence"] for r in resultats]
print(f"Latence moyenne OpenAI : {sum(latences_oai)/len(latences_oai):.1f}s")
print(f"Latence moyenne Local  : {sum(latences_local)/len(latences_local):.1f}s")
print(f"Ratio vitesse          : {sum(latences_local)/sum(latences_oai):.1f}x plus lent en local")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le tableau de comparaison final avec les latences moyennes OpenAI vs Local
> **Expliquer :** Analyser les résultats ensemble. Les réponses sont-elles équivalentes en qualité ? Où le modèle local fait-il des erreurs ou des imprécisions par rapport à GPT-4o-mini ? Discuter des cas d'usage : pour des données de santé, la confidentialité prime sur la latence. Pour une application publique à fort volume, OpenAI est plus adapté.

---

## Partie 5 — Optimisation du RAG local (10 min)

### Astuce 1 : Ajuster les paramètres Ollama

```python
# Optimisation pour les modèles locaux
llm_optimise = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    num_predict=256,     # Limiter la longueur de génération (plus rapide)
    num_ctx=2048,        # Réduire la fenêtre de contexte si mémoire limitée
    repeat_penalty=1.1,  # Réduire les répétitions
)
```

### Astuce 2 : Utiliser un modèle d'embedding plus performant

```python
# bge-m3 : multilingue, excellent pour le français
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_bge = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# Première utilisation : télécharge ~1.2GB
# Utilisation suivante : chargement depuis le cache local
```

### Astuce 3 : Cache des embeddings

```python
from langchain.storage import InMemoryByteStore
from langchain.embeddings import CacheBackedEmbeddings

# Créer un cache pour éviter de recalculer les embeddings
store = InMemoryByteStore()
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=store,
    query_embedding_cache=store,
)

# Première indexation : calcule les embeddings
# Indexations suivantes : lecture depuis le cache (10x plus rapide)
```

---

## Grille d'évaluation

| Critère | Points |
|---------|--------|
| Ollama fonctionnel avec modèles téléchargés | 15 pts |
| Embeddings locaux fonctionnels | 15 pts |
| Indexation dans Chroma avec embeddings locaux | 20 pts |
| Chaîne RAG avec LLM local fonctionnelle | 25 pts |
| Streaming implémenté | 10 pts |
| Comparaison OpenAI vs Local (si disponible) | 15 pts |

**Total : 100 pts**

---

## Résumé : Quand choisir le RAG local ?

| Critère | RAG Cloud (OpenAI) | RAG Local (Ollama) |
|---------|-------------------|-------------------|
| Vitesse | Rapide (1-2s) | Plus lent (3-15s CPU) |
| Coût | ~$0.01-0.10/requête | Gratuit après setup |
| Confidentialité | Données envoyées à OpenAI | Données 100% locales |
| Qualité réponses | Excellente | Bonne à très bonne |
| Setup | 5 minutes | 30-60 minutes |
| Offline | Non | Oui |
| **Cas d'usage** | Apps publiques, prototype | Santé, RH, finance, offline |

Retour à la liste des exercices : [../README.md](../README.md)
