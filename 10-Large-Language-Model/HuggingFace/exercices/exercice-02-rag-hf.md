# Exercice 02 — Construire un système RAG avec HuggingFace

## Objectif

Construire un système **RAG (Retrieval-Augmented Generation)** entièrement open-source qui :
1. Ingère une base de documents (PDF ou texte)
2. Les encode en embeddings avec `sentence-transformers`
3. Stocke les vecteurs dans FAISS
4. Répond à des questions en récupérant les passages pertinents
5. Génère une réponse avec un LLM local (via Transformers ou Ollama)

---

## Durée estimée

3h (dont 30 min de téléchargement de modèles)

---

## Prérequis

```bash
pip install transformers sentence-transformers faiss-cpu
pip install langchain langchain-community  # Pour le chunking
pip install pypdf                           # Pour lire les PDFs
```

---

## Architecture du système

```
Documents (PDF/TXT)
       ↓ chunking (découper en passages)
Passages de texte
       ↓ sentence-transformers (encoder)
Vecteurs d'embeddings
       ↓ FAISS (indexer)
Index vectoriel
       ↑
Requête utilisateur → Encode → Recherche Top-K → Passages pertinents
                                                          ↓
                                              LLM (GPT-2 / Mistral / Ollama)
                                                          ↓
                                              Réponse générée avec contexte
```

---

## Partie 1 — Préparation des documents (30 min)

### 1.1 Charger les documents

```python
import os
from pathlib import Path

# Pour cet exercice, nous utilisons un corpus de documents sur Python/ML
# Vous pouvez utiliser vos propres documents (PDFs, fichiers texte)

DOCUMENTS_RAW = [
    {
        "source": "python_intro",
        "content": """
Python est un langage de programmation interprété, multi-paradigme et multiplateformes.
Créé par Guido van Rossum et lancé en 1991, Python favorise la lisibilité du code
et sa syntaxe est conçue pour être claire et expressive.

Python supporte plusieurs paradigmes de programmation, notamment la programmation
orientée objet, la programmation fonctionnelle et la programmation impérative.
Sa bibliothèque standard est vaste et il dispose d'un écosystème riche en modules
tiers disponibles via PyPI (Python Package Index).

Les principaux usages de Python incluent : le développement web (Django, Flask, FastAPI),
la data science (NumPy, Pandas, Matplotlib), le machine learning (scikit-learn, PyTorch,
TensorFlow), l'automatisation de tâches, et le scripting système.
"""
    },
    {
        "source": "transformers_intro",
        "content": """
Hugging Face Transformers est une bibliothèque Python open-source qui donne accès à des
milliers de modèles pré-entraînés pour le traitement du langage naturel, la vision par
ordinateur et l'audio.

La bibliothèque est construite autour de l'architecture Transformer, introduite dans
l'article "Attention Is All You Need" (Vaswani et al., 2017). Le mécanisme d'attention
permet aux modèles de peser dynamiquement l'importance de chaque token par rapport aux autres.

Les modèles populaires incluent BERT (encodeur bidirectionnel), GPT (décodeur autorégressif),
T5 (encodeur-décodeur), et leurs nombreuses variantes (RoBERTa, DistilBERT, ALBERT, etc.).

Pour utiliser un modèle : from transformers import pipeline
pipe = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
"""
    },
    {
        "source": "rag_concept",
        "content": """
RAG (Retrieval-Augmented Generation) est une technique qui améliore les LLMs en leur donnant
accès à une base de connaissances externe au moment de l'inférence.

Problème que RAG résout : les LLMs ont une date de coupure (ils ne connaissent pas les
événements récents) et ne peuvent pas accéder à des documents privés. Ils peuvent aussi
"halluciner" des faits incorrects.

Le processus RAG se déroule en deux phases :
1. INDEXATION : les documents sont découpés en chunks, encodés en vecteurs, et stockés dans
   une base vectorielle (FAISS, Chroma, Qdrant, Pinecone...).
2. RETRIEVAL + GENERATION : la requête de l'utilisateur est encodée, les chunks les plus
   similaires sont récupérés, et le LLM génère une réponse en s'appuyant sur ces chunks
   comme contexte.

RAG améliore la factualité des réponses car le modèle peut "citer ses sources".
"""
    },
    {
        "source": "fine_tuning",
        "content": """
Le fine-tuning est le processus d'adaptation d'un modèle pré-entraîné à une tâche spécifique.
Il existe plusieurs stratégies selon les ressources disponibles.

Fine-tuning complet : tous les paramètres du modèle sont mis à jour. Nécessite beaucoup
de VRAM et de données, mais donne les meilleurs résultats.

LoRA (Low-Rank Adaptation) : seules de petites matrices de rang faible sont ajoutées au
modèle. Les poids originaux restent figés. Réduit le nombre de paramètres entraînables
de 100x avec une perte de performance minime.

QLoRA combine LoRA avec la quantization 4-bit (NF4) pour permettre le fine-tuning de
modèles 7B+ sur des GPU de 8-16GB. C'est la méthode recommandée pour le fine-tuning
de LLMs sur du matériel grand public.

Pour un modèle 7B :
- Full fine-tuning : ~128 GB VRAM (impossible sur GPU consumer)
- LoRA (FP16)      : ~14 GB VRAM (RTX 3090/4090)
- QLoRA (4-bit)    : ~5-8 GB VRAM (RTX 3080/4080)
"""
    },
    {
        "source": "embeddings",
        "content": """
Les embeddings sont des représentations vectorielles denses d'objets (textes, images, etc.)
dans un espace de haute dimension. Des objets sémantiquement similaires ont des vecteurs proches.

Sentence Transformers est la bibliothèque de référence pour calculer des embeddings de phrases.
Elle propose des modèles optimisés pour la comparaison sémantique.

Pour calculer la similarité entre deux phrases :
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("all-MiniLM-L6-v2")
emb1 = model.encode("Le chat est sur le tapis")
emb2 = model.encode("Le félin repose sur la moquette")
similarity = util.cos_sim(emb1, emb2)  # ~0.85

Les embeddings sont utilisés pour : la recherche sémantique, le clustering de documents,
la détection de duplicats, la recommandation, et comme composant du RAG.
"""
    },
]

print(f"Corpus chargé : {len(DOCUMENTS_RAW)} documents")
for doc in DOCUMENTS_RAW:
    print(f"  - {doc['source']} : {len(doc['content'])} caractères")
```

### 1.2 Découper en chunks

```python
# EXERCICE : Implémenter une fonction de chunking
# qui découpe les documents en passages de taille appropriée

def chunk_document(doc: dict, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """
    Découpe un document en chunks avec chevauchement.

    Args:
        doc: {"source": str, "content": str}
        chunk_size: nombre de mots par chunk
        overlap: nombre de mots de chevauchement entre chunks

    Returns:
        liste de {"source", "chunk_id", "text", "word_count"}
    """
    # TODO : Implémenter le chunking par mots
    # Hint :
    # 1. Diviser le contenu en mots (split)
    # 2. Créer des fenêtres glissantes de taille chunk_size avec overlap
    # 3. Reconstituer les chunks en texte
    # 4. Retourner la liste de chunks avec métadonnées

    words = doc["content"].split()
    chunks = []

    # Votre code ici :

    return chunks

# EXERCICE : Appliquer le chunking à tous les documents
all_chunks = []
for doc in DOCUMENTS_RAW:
    chunks = chunk_document(doc, chunk_size=150, overlap=30)
    all_chunks.extend(chunks)

print(f"\nTotal chunks : {len(all_chunks)}")
for chunk in all_chunks[:3]:
    print(f"\n[{chunk['source']}] Chunk {chunk['chunk_id']} ({chunk['word_count']} mots) :")
    print(f"  {chunk['text'][:100]}...")
```

---

## Partie 2 — Indexation vectorielle (30 min)

### 2.1 Encoder les chunks

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import time

# Charger le modèle d'embedding (multilingue pour le français)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# EXERCICE : Encoder tous les chunks
print(f"Encoding {len(all_chunks)} chunks avec {EMBEDDING_MODEL}...")

start = time.time()
# TODO : Encoder les textes de tous les chunks
# Hint : extraire les textes puis appeler embedding_model.encode()
chunk_texts = [chunk["text"] for chunk in all_chunks]
embeddings = # ...

elapsed = time.time() - start
print(f"Encodage terminé en {elapsed:.2f}s")
print(f"Shape des embeddings : {embeddings.shape}")
print(f"Vitesse : {len(all_chunks)/elapsed:.1f} chunks/sec")
```

### 2.2 Créer l'index FAISS

```python
import faiss

# EXERCICE : Construire l'index FAISS
def build_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Construit un index FAISS pour la recherche par similarité cosinus.

    Args:
        embeddings: array [n_chunks, embedding_dim]

    Returns:
        Index FAISS prêt pour la recherche
    """
    # TODO :
    # 1. S'assurer que le dtype est float32
    # 2. Normaliser les vecteurs (pour similarité cosinus)
    # 3. Créer un IndexFlatIP (Inner Product = cosinus sur vecteurs normalisés)
    # 4. Ajouter les vecteurs à l'index
    # 5. Retourner l'index

    # Votre code ici :
    pass

index = build_index(embeddings)
print(f"Index FAISS créé : {index.ntotal} vecteurs, dimension {index.d}")

# BONUS : Sauvegarder l'index pour éviter de recalculer
faiss.write_index(index, "./rag_index.faiss")
print("Index sauvegardé dans ./rag_index.faiss")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Un notebook montrant la progression du système RAG : d'abord les chunks affichés dans un tableau (source, chunk_id, longueur, extrait), puis l'encodage avec la barre de progression, puis la création de l'index FAISS et sa vérification
> **Expliquer :** L'importance du chunking (trop grand = contexte dilué, trop petit = perd le contexte), pourquoi l'overlap évite de couper une information en deux chunks, et la structure d'un index FAISS (quantization, IVF vs Flat selon la taille du corpus)

---

## Partie 3 — Retrieval (30 min)

### 3.1 Fonction de recherche

```python
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# EXERCICE : Implémenter la fonction de retrieval
def retrieve(
    query: str,
    index: faiss.Index,
    chunks: list[dict],
    embedding_model: SentenceTransformer,
    top_k: int = 3,
) -> list[dict]:
    """
    Recherche les passages les plus pertinents pour une requête.

    Args:
        query: question de l'utilisateur
        index: index FAISS
        chunks: liste des chunks avec métadonnées
        embedding_model: modèle d'embedding
        top_k: nombre de passages à récupérer

    Returns:
        liste des top_k chunks les plus pertinents avec leur score
    """
    # TODO :
    # 1. Encoder la requête
    # 2. Normaliser le vecteur
    # 3. Chercher dans l'index FAISS
    # 4. Retourner les chunks correspondants avec leur score

    # Votre code ici :
    pass

# Tester la recherche
test_queries = [
    "Comment utiliser les pipelines dans Transformers ?",
    "Quelle est la différence entre LoRA et QLoRA ?",
    "Comment calculer la similarité entre deux phrases ?",
    "Qu'est-ce que le RAG et pourquoi l'utiliser ?",
]

for query in test_queries:
    results = retrieve(query, index, all_chunks, embedding_model, top_k=2)
    print(f"\nQ: {query}")
    for r in results:
        print(f"  [{r['score']:.3f}] [{r['source']}] {r['text'][:100]}...")
```

### 3.2 Évaluation du retrieval

```python
# EXERCICE : Évaluer la qualité du retrieval
# Pour chaque requête de test, vérifier si le bon document est dans le top-3

# Paires (requête, source_attendue)
test_pairs = [
    ("Comment installer Hugging Face Transformers ?", "transformers_intro"),
    ("Quelle est la syntaxe de Python ?", "python_intro"),
    ("Comment fonctionne le fine-tuning avec QLoRA ?", "fine_tuning"),
    ("Qu'est-ce que la recherche sémantique ?", "embeddings"),
    ("Comment construire un système RAG ?", "rag_concept"),
]

correct = 0
for query, expected_source in test_pairs:
    results = retrieve(query, index, all_chunks, embedding_model, top_k=3)
    retrieved_sources = [r["source"] for r in results]
    is_correct = expected_source in retrieved_sources
    correct += int(is_correct)
    status = "✓" if is_correct else "✗"
    print(f"{status} [{expected_source}] {query[:50]}...")
    if not is_correct:
        print(f"  Récupéré : {retrieved_sources}")

print(f"\nRappel@3 : {correct}/{len(test_pairs)} = {correct/len(test_pairs):.0%}")
```

---

## Partie 4 — Génération (45 min)

### 4.1 Construire le prompt RAG

```python
# EXERCICE : Implémenter la construction du prompt RAG
def build_rag_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Construit le prompt pour le LLM à partir de la requête et des passages récupérés.

    Args:
        query: question de l'utilisateur
        retrieved_chunks: liste de chunks récupérés par FAISS

    Returns:
        prompt formaté pour le LLM
    """
    # TODO : Construire un prompt structuré contenant :
    # 1. Les passages de contexte (numérotés)
    # 2. Une instruction claire pour le LLM
    # 3. La question
    # 4. Un indicateur de début de réponse

    # Exemple de format Alpaca-style :
    """
    ### Contexte :
    [Passage 1] : ...
    [Passage 2] : ...

    ### Question :
    ...

    ### Réponse :
    """

    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(f"[Passage {i}] (source: {chunk['source']}) : {chunk['text']}")

    context = "\n\n".join(context_parts)

    # TODO : Compléter le template de prompt
    prompt = f"""### Contexte :
{context}

### Instruction :
En te basant UNIQUEMENT sur les passages de contexte ci-dessus, réponds à la question suivante.
Si la réponse ne se trouve pas dans le contexte, dis-le clairement.

### Question :
{query}

### Réponse :
"""
    return prompt

# Tester le prompt
query = "Comment utiliser LoRA pour réduire la consommation de VRAM ?"
chunks = retrieve(query, index, all_chunks, embedding_model, top_k=3)
prompt = build_rag_prompt(query, chunks)
print(prompt)
print(f"\nLongueur du prompt : {len(prompt)} caractères")
```

### 4.2 Intégrer le LLM

```python
# OPTION A : Utiliser GPT-2 (léger, pas besoin de GPU puissant)
from transformers import pipeline
import torch

def create_generator_gpt2():
    """Crée un générateur de texte avec GPT-2 (pour tests sans GPU)"""
    generator = pipeline(
        "text-generation",
        model="gpt2-medium",
        device=-1,  # CPU
    )
    def generate(prompt: str, max_new_tokens: int = 200) -> str:
        output = generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=50256,
        )
        # Extraire seulement le texte généré (pas le prompt)
        generated = output[0]["generated_text"]
        response = generated[len(prompt):].strip()
        return response
    return generate

# OPTION B : Utiliser Ollama (recommandé si disponible)
import requests

def create_generator_ollama(model: str = "mistral"):
    """Crée un générateur via l'API Ollama locale"""
    def generate(prompt: str, max_new_tokens: int = 256) -> str:
        # TODO : Implémenter l'appel à l'API Ollama
        # POST http://localhost:11434/api/generate
        # body: {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": max_new_tokens}}

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_new_tokens,
                    "temperature": 0.7,
                    "stop": ["### Question:", "### Contexte:"],
                }
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise RuntimeError(f"Erreur Ollama : {response.status_code}")
    return generate

# Choisir le générateur selon l'environnement
try:
    requests.get("http://localhost:11434/api/version", timeout=2)
    print("Ollama disponible → utilisation de Mistral")
    generate = create_generator_ollama("mistral")
except Exception:
    print("Ollama non disponible → utilisation de GPT-2 (qualité réduite)")
    generate = create_generator_gpt2()
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Le prompt RAG complet dans le terminal (contexte + question + début de réponse) suivi de la réponse générée par le LLM, en comparant une réponse sans contexte RAG (hallucination possible) vs avec contexte (réponse ancrée dans les faits)
> **Expliquer :** Pourquoi le contexte améliore la réponse (le LLM peut "citer" les passages), les limites du RAG (la qualité dépend du retrieval, le LLM peut ignorer le contexte), et comment la taille du contexte affect la génération (context window des LLMs)

---

## Partie 5 — Système RAG complet (30 min)

### 5.1 Assembler le pipeline

```python
# EXERCICE : Assembler toutes les parties en une classe RAG

class RAGSystem:
    """Système RAG complet : indexation + retrieval + génération"""

    def __init__(
        self,
        embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        llm_backend: str = "auto",  # "ollama" ou "gpt2" ou "auto"
    ):
        # TODO : Initialiser les composants
        # 1. Modèle d'embedding
        # 2. Index FAISS (vide au départ)
        # 3. Liste des chunks
        # 4. Générateur LLM

        # Votre code ici :
        pass

    def add_documents(self, documents: list[dict], chunk_size: int = 150, overlap: int = 30):
        """
        Ingère des documents : chunking + encodage + indexation.

        Args:
            documents: liste de {"source": str, "content": str}
            chunk_size: mots par chunk
            overlap: mots de chevauchement
        """
        # TODO : Implémenter l'ingestion complète
        # 1. Chunker tous les documents
        # 2. Encoder les chunks
        # 3. Créer ou mettre à jour l'index FAISS
        # 4. Sauvegarder les chunks dans self.chunks

        # Votre code ici :
        pass

    def query(self, question: str, top_k: int = 3, max_new_tokens: int = 256) -> dict:
        """
        Répond à une question en utilisant le RAG.

        Args:
            question: question de l'utilisateur
            top_k: nombre de passages à récupérer
            max_new_tokens: longueur max de la réponse

        Returns:
            {"answer": str, "sources": list[str], "context": list[dict]}
        """
        # TODO :
        # 1. Récupérer les passages pertinents
        # 2. Construire le prompt RAG
        # 3. Générer la réponse
        # 4. Retourner la réponse + les sources utilisées

        # Votre code ici :
        pass

    def interactive_mode(self):
        """Mode interactif pour tester le système en ligne de commande"""
        print("Système RAG prêt ! Tapez 'quit' pour quitter.")
        print(f"Base de connaissances : {len(self.chunks)} chunks indexés\n")

        while True:
            question = input("Votre question : ").strip()
            if question.lower() in ["quit", "exit", "q"]:
                break
            if not question:
                continue

            result = self.query(question)
            print(f"\nRéponse : {result['answer']}")
            print(f"Sources  : {result['sources']}")
            print("-" * 50)


# EXERCICE : Tester le système complet
rag = RAGSystem()
rag.add_documents(DOCUMENTS_RAW)

# Questions de test
test_questions = [
    "Qu'est-ce que CamemBERT et pour quoi est-il utilisé ?",
    "Comment réduire l'utilisation mémoire lors du fine-tuning d'un LLM ?",
    "Quelle bibliothèque utiliser pour calculer des embeddings de phrases en Python ?",
    "Quels sont les avantages du RAG par rapport à un LLM classique ?",
]

print("=== Test du système RAG ===\n")
for question in test_questions:
    result = rag.query(question)
    print(f"Q: {question}")
    print(f"R: {result['answer'][:200]}...")
    print(f"Sources: {result['sources']}")
    print()
```

---

## Partie 6 — Évaluation et améliorations (bonus)

### 6.1 Évaluer la qualité des réponses

```python
# EXERCICE BONUS : Implémenter une évaluation automatique

# Paires (question, réponse_attendue) pour évaluation
evaluation_set = [
    {
        "question": "Qu'est-ce que LoRA ?",
        "expected_keywords": ["rang", "matrices", "paramètres", "figé", "adaptat"],
    },
    {
        "question": "Comment utiliser Sentence Transformers ?",
        "expected_keywords": ["encode", "SentenceTransformer", "from", "similarité"],
    },
]

def evaluate_rag_answers(rag_system, eval_set):
    """Évalue les réponses du RAG sur un ensemble de test"""
    scores = []
    for item in eval_set:
        result = rag_system.query(item["question"])
        answer_lower = result["answer"].lower()

        # Compter les mots-clés attendus présents dans la réponse
        found = sum(1 for kw in item["expected_keywords"] if kw.lower() in answer_lower)
        score = found / len(item["expected_keywords"])
        scores.append(score)

        print(f"Q: {item['question'][:50]}...")
        print(f"Score : {score:.0%} ({found}/{len(item['expected_keywords'])} mots-clés)")
        print(f"Réponse : {result['answer'][:150]}...\n")

    print(f"Score moyen : {sum(scores)/len(scores):.0%}")
    return scores

# evaluate_rag_answers(rag, evaluation_set)
```

### 6.2 Pistes d'amélioration

```python
"""
Améliorations possibles à implémenter en bonus :

1. RERANKING :
   Utiliser un cross-encoder pour re-ranker les résultats FAISS avant de les passer au LLM
   from sentence_transformers import CrossEncoder
   reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

2. QUERY EXPANSION :
   Générer des requêtes alternatives pour améliorer le recall
   "Comment faire du fine-tuning efficace ?"
   → ["LoRA training", "QLoRA method", "parameter efficient training"]

3. HYBRID SEARCH :
   Combiner recherche sémantique (FAISS) et recherche lexicale (BM25)
   from rank_bm25 import BM25Okapi
   score_final = alpha * score_semantique + (1-alpha) * score_bm25

4. CONTEXTUAL COMPRESSION :
   Extraire uniquement les phrases pertinentes du chunk (pas tout le chunk)

5. STREAMING :
   Afficher la réponse token par token pour une meilleure UX
   for token in model.generate_streaming(prompt):
       print(token, end="", flush=True)
"""

# EXERCICE BONUS : Implémenter une des améliorations ci-dessus
# et mesurer l'impact sur le Rappel@3 calculé en Partie 3
```

---

## Barème et critères de réussite

| Critère | Points | Requis pour valider |
|---------|--------|---------------------|
| Chunking fonctionnel (avec overlap) | 15 | Chunks < 200 mots, chevauchement visible |
| Embeddings calculés (bonne shape) | 10 | Shape [n_chunks, 384] |
| Index FAISS créé et requêtable | 20 | Recherche retourne top-k résultats |
| Retrieval correct (Rappel@3 > 80%) | 15 | 4/5 requêtes de test réussies |
| Prompt RAG structuré | 10 | Contexte + instruction + question |
| Génération avec LLM local | 20 | Réponse non vide, ancrée dans le contexte |
| Classe RAGSystem complète | 10 | Méthodes add_documents + query fonctionnelles |
| **Bonus reranking** | **+10** | Amélioration du Rappel@3 |
| **Bonus évaluation** | **+5** | Score moyen calculé |

**Total : 100 points + 15 bonus**

---

## Ressources complémentaires

- [LangChain RAG tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [FAISS documentation](https://faiss.ai/)
- [Sentence Transformers docs](https://www.sbert.net/)
- [Hugging Face RAG models](https://huggingface.co/facebook/rag-token-nq)
- [Paper original RAG](https://arxiv.org/abs/2005.11401) (Lewis et al., 2020)

---

## Indices si blocage

**Partie 1 (chunking)** :
```python
# Exemple de chunking par mots
words = text.split()
for start in range(0, len(words), chunk_size - overlap):
    end = min(start + chunk_size, len(words))
    chunk_text = " ".join(words[start:end])
    chunks.append(chunk_text)
```

**Partie 2 (FAISS)** :
```python
embeddings_f32 = embeddings.astype(np.float32)
faiss.normalize_L2(embeddings_f32)  # In-place normalization
index = faiss.IndexFlatIP(embeddings_f32.shape[1])
index.add(embeddings_f32)
```

**Partie 3 (retrieval)** :
```python
query_emb = embedding_model.encode([query]).astype(np.float32)
faiss.normalize_L2(query_emb)
scores, indices = index.search(query_emb, top_k)
# scores[0] et indices[0] contiennent les résultats
```
