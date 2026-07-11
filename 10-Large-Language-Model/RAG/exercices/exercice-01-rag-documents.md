# Exercice 01 — RAG sur une Collection de PDFs

## Objectif

Construire un système RAG complet permettant d'interroger une collection de documents PDF. Vous utiliserez LangChain, Chroma comme vector store, et OpenAI pour les embeddings et la génération.

## Durée estimée : 90 minutes

## Prérequis

```bash
pip install langchain langchain-openai langchain-chroma langchain-community
pip install pypdf tiktoken python-dotenv
```

Fichier `.env` :
```
OPENAI_API_KEY=sk-proj-...
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=exercice-rag-01
```

---

## Partie 1 — Préparation des documents (20 min)

### Étape 1.1 — Créer des documents de test

Si vous n'avez pas de PDFs sous la main, créez des fichiers texte fictifs pour l'exercice :

```python
# setup_documents.py
import os

os.makedirs("./documents", exist_ok=True)

# Document 1 : politique de retour
with open("./documents/politique_retour.txt", "w", encoding="utf-8") as f:
    f.write("""POLITIQUE DE RETOUR ET REMBOURSEMENT

Article 1 - Délai de rétractation
Le client dispose d'un délai de 30 jours calendaires à compter de la date de réception
du colis pour exercer son droit de rétractation, sans avoir à justifier de motifs.

Article 2 - Conditions de retour
Les produits doivent être retournés dans leur emballage d'origine, non utilisés,
avec tous les accessoires et la documentation fournie.

Article 3 - Procédure de retour
Pour initier un retour, le client doit :
1. Se connecter à son espace client sur notre site
2. Sélectionner la commande concernée
3. Cliquer sur "Initier un retour"
4. Choisir le motif du retour
5. Imprimer le bon de retour prépayé
Le colis doit être déposé dans un point relais dans les 14 jours suivant la demande.

Article 4 - Remboursement
Le remboursement sera effectué dans les 14 jours ouvrés suivant la réception du
produit retourné dans nos entrepôts, via le moyen de paiement utilisé lors de l'achat.
""")

# Document 2 : garantie
with open("./documents/garantie.txt", "w", encoding="utf-8") as f:
    f.write("""CONDITIONS DE GARANTIE

Durée de la garantie
Tous nos produits bénéficient d'une garantie légale de conformité de 24 mois
à compter de la date d'achat. Les produits reconditionnés bénéficient d'une
garantie de 12 mois.

Ce que couvre la garantie
La garantie couvre les défauts de fabrication et les pannes survenues dans
des conditions normales d'utilisation. Elle inclut les pièces de rechange et
la main d'œuvre pour les réparations effectuées dans nos centres agréés.

Ce que ne couvre pas la garantie
La garantie ne couvre pas :
- Les dommages résultant d'une chute ou d'un choc
- Les dommages causés par une utilisation non conforme
- L'oxydation due à une exposition à l'humidité
- Les réparations effectuées par des tiers non agréés

Activation de la garantie
Pour bénéficier de la garantie, le client doit conserver sa preuve d'achat.
L'enregistrement du produit sur notre site permet de faciliter les démarches SAV.

Contact SAV
Service Après-Vente : sav@entreprise-exemple.fr
Téléphone : 01 23 45 67 89 (lun-ven, 9h-18h)
""")

# Document 3 : FAQ livraison
with open("./documents/faq_livraison.txt", "w", encoding="utf-8") as f:
    f.write("""FAQ LIVRAISON ET MODES DE LIVRAISON

Délais de livraison
- Livraison standard (Colissimo) : 3 à 5 jours ouvrés — Gratuite dès 49€
- Livraison express (Chronopost) : 24h — 9,90€
- Livraison en point relais : 2 à 4 jours ouvrés — 3,90€ ou gratuite dès 49€
- Livraison internationale (Europe) : 5 à 10 jours ouvrés — selon pays

Suivi de commande
Un email de confirmation avec le numéro de suivi est envoyé dès l'expédition.
Le suivi en temps réel est disponible sur notre site ou directement sur le
site du transporteur. Des SMS de notification sont envoyés aux étapes clés.

Que faire si mon colis n'arrive pas ?
Si votre colis n'est pas arrivé dans les délais indiqués, attendez 2 jours
ouvrés supplémentaires avant de nous contacter. En cas de perte confirmée par
le transporteur, nous procédons au renvoi du colis ou au remboursement intégral.

Modes de paiement acceptés
Nous acceptons : Carte bancaire (Visa, Mastercard, American Express),
PayPal, virement bancaire (délai +2 jours ouvrés), et chèque (délai +7 jours ouvrés).
""")

print("Documents de test créés dans ./documents/")
```

### Étape 1.2 — Charger et inspecter les documents

```python
# partie1_chargement.py
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Charger tous les fichiers texte du répertoire
loader = DirectoryLoader(
    "./documents/",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
    show_progress=True,
)

documents = loader.load()

print(f"=== Rapport de chargement ===")
print(f"Nombre de documents : {len(documents)}")
print()
for doc in documents:
    print(f"Source : {doc.metadata['source']}")
    print(f"Taille : {len(doc.page_content)} caractères")
    print(f"Aperçu : {doc.page_content[:100]}...")
    print()
```

**Question :** Combien de documents avez-vous chargé ? Notez la taille de chacun.

---

## Partie 2 — Indexation (25 min)

### Étape 2.1 — Chunker les documents

```python
# partie2_indexation.py
from dotenv import load_dotenv
load_dotenv()

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 1. Chargement
loader = DirectoryLoader("./documents/", glob="**/*.txt",
                          loader_cls=TextLoader,
                          loader_kwargs={"encoding": "utf-8"})
documents = loader.load()
print(f"Documents chargés : {len(documents)}")

# 2. Chunking
enc = tiktoken.get_encoding("cl100k_base")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    length_function=lambda t: len(enc.encode(t)),
)

chunks = splitter.split_documents(documents)
print(f"Chunks produits  : {len(chunks)}")

# Inspecter les chunks
for i, chunk in enumerate(chunks[:3]):
    nb_tokens = len(enc.encode(chunk.page_content))
    print(f"\nChunk {i+1} ({nb_tokens} tokens) — Source : {chunk.metadata['source']}")
    print(chunk.page_content[:150])
```

**Question :** Notez le nombre de chunks produits. Essayez avec `chunk_size=150` et `chunk_size=600`. Comment évolue le nombre de chunks ?

### Étape 2.2 — Créer le vector store

```python
# Continuer dans partie2_indexation.py

# 3. Embedding et indexation
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

print("\nIndexation en cours...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="exercice_01",
    persist_directory="./chroma_exercice_01",
)

print(f"Vector store créé : {vectorstore._collection.count()} vecteurs")

# Test : recherche manuelle
resultats_test = vectorstore.similarity_search_with_score(
    "délai de remboursement",
    k=3
)

print("\n=== Test de recherche ===")
for doc, score in resultats_test:
    similarite = 1 - score / 2
    print(f"Similarité : {similarite:.3f} | Source : {doc.metadata['source']}")
    print(f"  {doc.page_content[:100]}...")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant les chunks produits (avec leurs tailles en tokens) et les résultats du test de recherche avec les scores de similarité
> **Expliquer :** Montrer comment les chunks sont numérotés et quelles sources ils proviennent. Expliquer le score de similarité cosinus (proche de 1 = très similaire). Faire observer que "délai de remboursement" trouve des chunks de `politique_retour.txt` — le retrieval fonctionne déjà.

---

## Partie 3 — Pipeline RAG (25 min)

### Étape 3.1 — Construire la chaîne RAG

```python
# partie3_rag_chain.py
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document
from typing import List

# Charger le vector store existant
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="exercice_01",
    embedding_function=embeddings,
    persist_directory="./chroma_exercice_01"
)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prompt RAG
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant service client. Réponds aux questions
en te basant exclusivement sur la documentation fournie.
Si l'information n'est pas dans la documentation, dis-le clairement.
Sois concis et précis.

Documentation :
{context}"""),
    ("human", "{question}")
])

# Formatter les docs avec sources
def format_docs(docs: List[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[Source : {doc.metadata.get('source', '?')}]\n{doc.page_content}"
        for doc in docs
    )

# Chaîne RAG complète avec sources
rag_chain_complet = RunnableParallel(
    reponse=(
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT | llm | StrOutputParser()
    ),
    sources=retriever,
)

# Fonction de test
def interroger(question: str) -> None:
    print(f"\n{'='*50}")
    print(f"Q: {question}")
    resultat = rag_chain_complet.invoke(question)
    print(f"\nR: {resultat['reponse']}")
    print(f"\nSources ({len(resultat['sources'])} chunks) :")
    sources_uniques = set(
        doc.metadata.get("source", "?")
        for doc in resultat["sources"]
    )
    for s in sources_uniques:
        print(f"  • {s}")
```

### Étape 3.2 — Tester le système

```python
# Continuer dans partie3_rag_chain.py

# Questions de test
questions = [
    "Quel est le délai pour retourner un produit ?",
    "La garantie couvre-t-elle les dommages par chute ?",
    "Combien coûte la livraison express ?",
    "Comment contacter le service après-vente ?",
    "Puis-je payer en chèque ?",
    "Quelle est la météo à Paris aujourd'hui ?",  # Question hors-sujet
]

for q in questions:
    interroger(q)
```

**Question :** La dernière question (météo) reçoit-elle une bonne réponse ? Que dit le LLM ?

---

## Partie 4 — Comparaison avec/sans RAG (10 min)

```python
# partie4_comparaison.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Chaîne SANS RAG
prompt_sans_rag = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant service client."),
    ("human", "{question}")
])
chain_sans_rag = prompt_sans_rag | llm | StrOutputParser()

# Comparer
questions_sensibles = [
    "Quel est le délai exact pour retourner un produit ?",
    "La garantie des produits reconditionnés dure combien de temps ?",
    "À quel numéro peut-on appeler le SAV ?",
]

for q in questions_sensibles:
    print(f"\nQuestion : {q}")
    print(f"\nSANS RAG :")
    print(chain_sans_rag.invoke({"question": q}))
    print(f"\nAVEC RAG :")
    resultat = rag_chain_complet.invoke(q)
    print(resultat["reponse"])
    print("-" * 60)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Les réponses côte à côte SANS RAG vs AVEC RAG pour la question sur le numéro de téléphone SAV
> **Expliquer :** La réponse SANS RAG sera soit un refus ("je n'ai pas accès à vos données internes") soit une hallucination (un numéro inventé). La réponse AVEC RAG donne le numéro exact `01 23 45 67 89` car c'est dans le document. C'est le cas d'usage parfait pour justifier l'utilisation du RAG en entreprise.

---

## Partie 5 — Amélioration avancée (10 min)

### Exercice bonus : Ajouter le filtrage par source

```python
# Créer des retrievers spécialisés par type de document
retriever_garantie = vectorstore.as_retriever(
    search_kwargs={
        "k": 4,
        "filter": {"source": "./documents/garantie.txt"}
    }
)

retriever_retours = vectorstore.as_retriever(
    search_kwargs={
        "k": 4,
        "filter": {"source": "./documents/politique_retour.txt"}
    }
)

# Test : question sur la garantie → utiliser le retriever spécialisé
docs = retriever_garantie.invoke("durée de garantie produits reconditionnés")
print(f"Chunks récupérés depuis garantie.txt : {len(docs)}")
```

### Exercice bonus : MMR pour éviter la redondance

```python
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 15, "lambda_mult": 0.5}
)

# Comparer les résultats
q = "procédure de retour"
docs_sim = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(q)
docs_mmr = retriever_mmr.invoke(q)

print("=== Similarity ===")
for d in docs_sim:
    print(f"  {d.page_content[:80]}...")

print("\n=== MMR ===")
for d in docs_mmr:
    print(f"  {d.page_content[:80]}...")
```

---

## Grille d'évaluation

| Critère | Points |
|---------|--------|
| Chargement des documents sans erreur | 10 pts |
| Chunking avec inspection des tailles | 15 pts |
| Vector store créé et persisté | 15 pts |
| Chaîne RAG fonctionnelle | 25 pts |
| Sources affichées dans la réponse | 10 pts |
| Comparaison avec/sans RAG | 15 pts |
| Bonus MMR ou filtrage par source | 10 pts |

**Total : 100 pts (+ 10 bonus)**

---

## Solution de référence

```
chroma_exercice_01/     ← Créé automatiquement par Chroma
documents/
├── politique_retour.txt
├── garantie.txt
└── faq_livraison.txt
setup_documents.py
partie1_chargement.py
partie2_indexation.py
partie3_rag_chain.py
partie4_comparaison.py
```

Les réponses attendues :
- Délai de retour → "30 jours calendaires"
- Garantie reconditionnés → "12 mois"
- Numéro SAV → "01 23 45 67 89"
- Météo Paris → "Cette information n'est pas disponible dans la documentation."

Passez à l'exercice suivant : [exercice-02-rag-local.md](./exercice-02-rag-local.md)
