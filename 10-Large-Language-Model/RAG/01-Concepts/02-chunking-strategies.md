# 02 — Stratégies de Chunking

## Pourquoi le chunking est critique

Le chunking (découpage de documents en morceaux) est probablement la décision la plus impactante dans un pipeline RAG. Un mauvais chunking entraîne :

- Des chunks trop grands : dilution du signal, contexte hors-sujet injecté dans le prompt
- Des chunks trop petits : perte de cohérence, information incomplète, réponses fragmentées
- Des chunks qui coupent au mauvais endroit : phrases incomplètes, paragraphes disloqués

Il n'existe pas de stratégie universelle. Le bon chunking dépend du type de document, de la nature des questions, et du modèle d'embedding utilisé.

---

## Les paramètres fondamentaux

### chunk_size

La taille maximale d'un chunk. Exprimée en caractères (par défaut) ou en tokens.

**Règle pratique :**
- Questions courtes et factuelles → chunks petits (200-500 caractères)
- Questions de synthèse ou d'analyse → chunks grands (1000-2000 caractères)
- Modèle d'embedding `text-embedding-3-small` → optimal autour de 500-1000 caractères

### chunk_overlap

Le chevauchement entre deux chunks consécutifs. Il préserve le contexte aux frontières.

```
Document : |---chunk 1---|---chunk 2---|---chunk 3---|
Avec overlap :
  chunk 1 : |==========|
  chunk 2 :        |==========|
  chunk 3 :                |==========|
  (les = représentent le chevauchement)
```

**Règle pratique :** overlap = 10-20% de chunk_size. Trop d'overlap → duplication de données, coût plus élevé.

---

## Stratégie 1 — Fixed Size Chunking (taille fixe)

La stratégie la plus simple : couper tous les X caractères, sans considération de la structure du texte.

```python
from langchain.text_splitter import CharacterTextSplitter

# Chunking caractère par caractère
splitter = CharacterTextSplitter(
    separator="\n",      # Séparateur préférentiel
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

texte = """
Chapitre 1 : Introduction
La data engineering est le fondement de toute infrastructure de données moderne.
Elle englobe la collecte, le traitement, et le stockage des données à grande échelle.

Chapitre 2 : Les pipelines
Un pipeline de données transforme des données brutes en données exploitables.
Les étapes principales sont l'ingestion, la transformation et la livraison.
"""

chunks = splitter.split_text(texte)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1} ({len(chunk)} chars): {chunk[:80]}...")
```

**Avantages :** Simple, rapide, prévisible.

**Inconvénients :** Coupe souvent au milieu d'une phrase ou d'un paragraphe. Ignore totalement la structure sémantique du document.

**Quand l'utiliser :** Textes continus sans structure particulière (logs, transcriptions brutes).

---

## Stratégie 2 — Recursive Character Splitting

La stratégie par défaut dans LangChain. Elle tente de couper aux séparateurs naturels dans l'ordre suivant : `\n\n` → `\n` → `. ` → ` ` → caractère par caractère.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    # Séparateurs par ordre de priorité (défaut)
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)

# Charger et découper un PDF
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("documentation.pdf")
pages = loader.load()

chunks = splitter.split_documents(pages)

print(f"Pages originales : {len(pages)}")
print(f"Chunks produits  : {len(chunks)}")
print(f"\nExemple de chunk :")
print(chunks[0].page_content)
print(f"\nMétadonnées : {chunks[0].metadata}")
```

**Comportement :** L'algorithme essaie d'abord de couper sur les doubles sauts de ligne (paragraphes). Si le paragraphe est encore trop grand, il essaie les sauts de ligne simples, puis les points, etc.

**Avantages :** Préserve mieux la cohérence sémantique que le fixed-size. Bon compromis général.

**Inconvénients :** Ne comprend pas la structure logique du document (titres, sections, listes).

**Quand l'utiliser :** Cas par défaut pour la majorité des documents texte.

---

## Stratégie 3 — Token-Based Splitting

Utilise le nombre de tokens plutôt que le nombre de caractères. Plus précis car les LLM et les modèles d'embedding ont des limites en tokens.

```python
from langchain.text_splitter import TokenTextSplitter
import tiktoken

# Splitter basé sur les tokens GPT-4
splitter = TokenTextSplitter(
    encoding_name="cl100k_base",  # Encodage utilisé par GPT-4, text-embedding-3
    chunk_size=256,               # En tokens
    chunk_overlap=32,             # En tokens
)

# Vérifier le nombre de tokens d'un texte
enc = tiktoken.get_encoding("cl100k_base")
texte = "Voici un exemple de texte pour tester le découpage par tokens."
tokens = enc.encode(texte)
print(f"Nombre de tokens : {len(tokens)}")  # ~13 tokens

# Découper par tokens
chunks = splitter.split_text(texte_long)
for chunk in chunks:
    nb_tokens = len(enc.encode(chunk))
    print(f"Chunk : {nb_tokens} tokens, {len(chunk)} chars")
```

**Règle pratique pour les embeddings :**
- `text-embedding-3-small` : limite à 8191 tokens par texte
- La fenêtre "optimale" pour la qualité est autour de 256-512 tokens
- Plus un chunk est long, plus le vecteur est une "moyenne" — signal dilué

**Avantages :** Respect strict des limites des modèles. Coût prévisible.

**Inconvénients :** La notion de token est abstraite (un token ≈ 0.75 mot en anglais, ≈ 0.5-0.6 mot en français).

**Quand l'utiliser :** Quand les limites de tokens sont critiques (modèles d'embedding avec petite fenêtre).

---

## Stratégie 4 — Markdown / Code Splitting

Pour les documents structurés (Markdown, HTML, code source), il existe des splitters qui respectent la structure du document.

```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Découper en respectant la hiérarchie des titres Markdown
headers_to_split_on = [
    ("#",  "titre_1"),
    ("##", "titre_2"),
    ("###","titre_3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,  # Garder les titres dans le contenu
)

markdown_doc = """
# Guide d'installation

## Prérequis système
Python 3.10 ou supérieur est requis.
Vérifiez avec `python --version`.

## Installation des dépendances
Lancez la commande suivante dans votre terminal :
```bash
pip install langchain chromadb
```

## Configuration
Créez un fichier `.env` à la racine du projet.
"""

sections = markdown_splitter.split_text(markdown_doc)
for section in sections:
    print(f"Métadonnées : {section.metadata}")
    print(f"Contenu : {section.page_content[:100]}")
    print("---")
# Output :
# Métadonnées : {'titre_1': 'Guide d'installation', 'titre_2': 'Prérequis système'}
# Contenu : Python 3.10 ou supérieur est requis...
```

**Pour le code source :**

```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

# Splitter spécialisé Python
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100,
)

# Splitter JavaScript
js_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size=800,
    chunk_overlap=80,
)

code_python = """
def calculer_moyenne(notes: list[float]) -> float:
    \"\"\"Calcule la moyenne d'une liste de notes.\"\"\"
    if not notes:
        raise ValueError("La liste de notes ne peut pas être vide")
    return sum(notes) / len(notes)

class Etudiant:
    def __init__(self, nom: str, prenom: str):
        self.nom = nom
        self.prenom = prenom
        self.notes = []

    def ajouter_note(self, note: float) -> None:
        self.notes.append(note)

    def moyenne(self) -> float:
        return calculer_moyenne(self.notes)
"""

chunks = python_splitter.split_text(code_python)
for chunk in chunks:
    print(chunk)
    print("---")
```

---

## Stratégie 5 — Semantic Chunking

La stratégie la plus sophistiquée : utilise les embeddings pour détecter les ruptures sémantiques dans le texte. Au lieu de couper à taille fixe, on coupe là où le sens change.

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Mode breakpoint_threshold_type
# "percentile" : coupe aux N% de ruptures les plus fortes
# "standard_deviation" : coupe quand la dissimilarité dépasse mean + N*std
# "interquartile" : coupe selon les quartiles de dissimilarité

semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95,  # Coupe aux 5% de ruptures les plus fortes
)

texte_mixte = """
La photosynthèse est le processus par lequel les plantes transforment
la lumière solaire en énergie chimique. Elle se déroule dans les chloroplastes
et produit du glucose et de l'oxygène à partir de CO2 et d'eau.

L'intelligence artificielle a révolutionné de nombreux secteurs industriels.
Les modèles de deep learning permettent aujourd'hui de résoudre des problèmes
qui étaient impossibles il y a dix ans. Les LLM en particulier ont transformé
les interfaces homme-machine.

Le marché immobilier français est caractérisé par des disparités régionales fortes.
Les prix à Paris sont 3 à 5 fois supérieurs à ceux des villes moyennes.
La tension locative dans les grandes métropoles reste élevée malgré les politiques
de régulation des loyers.
"""

chunks = semantic_splitter.split_text(texte_mixte)
print(f"Nombre de chunks détectés : {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1} : {chunk[:100]}...")
# Le splitter détecte naturellement les 3 thèmes différents
```

**Comment ça fonctionne :**
1. Le texte est d'abord découpé en phrases
2. Chaque phrase est embarquée (vecteur)
3. La similarité cosinus entre phrases consécutives est calculée
4. Quand la similarité chute brutalement, c'est une rupture sémantique → nouvelle frontière de chunk

**Avantages :** Chunks cohérents sémantiquement. Excellent pour les documents qui mélangent plusieurs sujets.

**Inconvénients :** Coûteux (appel à l'API d'embeddings pour chaque phrase pendant l'indexation). Non-déterministe (légèrement variable selon les batches).

**Quand l'utiliser :** Documents longs et hétérogènes (rapports annuels, articles de blog, contenus mixtes).

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Visualisation côte à côte des 4 stratégies appliquées au même document — afficher le nombre de chunks produits et un extrait du premier chunk de chaque stratégie
> **Expliquer :** Prendre un même PDF de 10-20 pages et montrer comment chaque stratégie le découpe différemment. Faire varier `chunk_size` en direct (500 vs 1500) et montrer l'impact sur le nombre de chunks. Le semantic chunking sera visiblement différent des autres — ses frontières correspondent à des changements de sujet réels.

---

## Chunking document-aware — HTML et PDF structurés

Les documents réels ont une structure (titres, tableaux, listes) qu'il faut exploiter.

```python
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import HTMLHeaderTextSplitter

# Découper un HTML en respectant les balises de titre
headers_to_split_on = [
    ("h1", "section"),
    ("h2", "sous_section"),
    ("h3", "paragraphe"),
]

html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

html_content = """
<html>
<body>
<h1>Rapport Annuel 2024</h1>
<h2>Résultats financiers</h2>
<p>Le chiffre d'affaires a progressé de 12% pour atteindre 45M€.</p>
<p>La marge nette s'établit à 8,5%, en amélioration de 1,2 points.</p>
<h2>Perspectives 2025</h2>
<p>Nous anticipons une croissance organique de 8 à 10%.</p>
<h3>Marchés cibles</h3>
<p>L'expansion en Europe du Sud reste notre priorité stratégique.</p>
</body>
</html>
"""

sections = html_splitter.split_text(html_content)
for section in sections:
    print(f"Headers : {section.metadata}")
    print(f"Contenu : {section.page_content}")
    print("---")
```

**Enrichir les métadonnées des chunks :**

```python
# Ajouter des métadonnées utiles pour le retrieval filtré
from langchain_core.documents import Document

def enrichir_chunks(chunks, source_file, document_type, date_creation):
    """Ajoute des métadonnées contextuelles à chaque chunk."""
    for chunk in chunks:
        chunk.metadata.update({
            "source": source_file,
            "type": document_type,
            "date": date_creation,
            "nb_chars": len(chunk.page_content),
        })
    return chunks

# Utilisation
chunks_enrichis = enrichir_chunks(
    chunks=chunks,
    source_file="rapport_annuel_2024.pdf",
    document_type="rapport_financier",
    date_creation="2024-12-31"
)

# Plus tard, filtrer lors du retrieval
resultats = vectorstore.similarity_search(
    query="croissance 2024",
    k=5,
    filter={"type": "rapport_financier"}  # Filtrage par métadonnée
)
```

---

## Parent Document Retriever — le meilleur des deux mondes

Un pattern avancé : indexer des petits chunks (précis pour l'embedding) mais retourner les documents parents (riches en contexte) lors du retrieval.

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Petits chunks pour l'embedding (précision de recherche)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)

# Grands chunks retournés au LLM (richesse de contexte)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

# Store en mémoire pour les documents parents
parent_store = InMemoryStore()

vectorstore = Chroma(
    collection_name="parents_children",
    embedding_function=OpenAIEmbeddings()
)

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=parent_store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# Indexation
retriever.add_documents(pages, ids=None)

# Recherche : trouve les petits chunks précis, retourne les grands parents
docs = retriever.invoke("politique de remboursement")
print(f"Documents retournés : {len(docs)}")
for doc in docs:
    print(f"Taille : {len(doc.page_content)} chars")
```

**Pourquoi c'est puissant :**
- La recherche s'effectue sur les petits chunks → haute précision de correspondance
- Mais le LLM reçoit les grands chunks parents → contexte riche et complet
- Évite le dilemme "chunk petit pour l'embedding mais trop fragmenté pour la réponse"

---

## Guide de décision — quelle stratégie choisir ?

```
Type de document
       │
       ├─ Code source → from_language() splitter
       │
       ├─ Markdown / README → MarkdownHeaderTextSplitter
       │
       ├─ HTML avec structure → HTMLHeaderTextSplitter
       │
       ├─ PDF avec titres → RecursiveCharacterTextSplitter
       │   + enrichissement des métadonnées
       │
       ├─ Document long et hétérogène → SemanticChunker
       │   (si budget API disponible)
       │
       ├─ Texte simple / continu → RecursiveCharacterTextSplitter
       │   (défaut général)
       │
       └─ Questions factuelles sur docs longs → ParentDocumentRetriever
```

---

## Bonnes pratiques

### Toujours inspecter ses chunks

```python
# Analyser la distribution des tailles de chunks
import statistics

tailles = [len(chunk.page_content) for chunk in chunks]

print(f"Nombre de chunks  : {len(chunks)}")
print(f"Taille minimale   : {min(tailles)} chars")
print(f"Taille maximale   : {max(tailles)} chars")
print(f"Taille médiane    : {statistics.median(tailles):.0f} chars")
print(f"Taille moyenne    : {statistics.mean(tailles):.0f} chars")
print(f"Écart-type        : {statistics.stdev(tailles):.0f} chars")

# Identifier les chunks problématiques (trop courts)
chunks_courts = [c for c in chunks if len(c.page_content) < 50]
print(f"\nChunks trop courts (<50 chars) : {len(chunks_courts)}")
for c in chunks_courts[:3]:
    print(f"  '{c.page_content}'")
```

### Tester avec des questions réelles

La seule vraie validation d'une stratégie de chunking est de tester si les questions réelles des utilisateurs récupèrent les bons chunks :

```python
def tester_retrieval(vectorstore, questions_tests):
    """Teste si le retrieval renvoie des chunks pertinents."""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    for question, chunk_attendu_contient in questions_tests:
        docs = retriever.invoke(question)
        found = any(chunk_attendu_contient.lower() in d.page_content.lower()
                    for d in docs)
        status = "OK" if found else "FAIL"
        print(f"[{status}] {question[:60]}...")

# Exemple d'utilisation
questions_tests = [
    ("Quel est le délai de livraison ?", "délai"),
    ("Comment contacter le support ?", "support"),
    ("Quelles sont les conditions de garantie ?", "garantie"),
]

tester_retrieval(vectorstore, questions_tests)
```

---

## Récapitulatif des stratégies

| Stratégie | Complexité | Coût | Idéal pour |
|-----------|------------|------|-----------|
| Fixed size | Simple | Minimal | Textes bruts, logs |
| Recursive Character | Simple | Minimal | Cas général |
| Token-based | Simple | Minimal | Contrôle strict des tokens |
| Markdown headers | Moyen | Minimal | Documentation Markdown |
| HTML headers | Moyen | Minimal | Pages web structurées |
| Semantic | Élevé | Moyen (API) | Docs longs et hétérogènes |
| Parent Document | Élevé | Minimal | Synthèse sur docs longs |

La suite : [Pipeline/01-ingestion.md](../Pipeline/01-ingestion.md) — Ingestion complète d'un corpus documentaire
