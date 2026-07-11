# 03 — Génération : Prompt, Synthèse et Citations

## Vue d'ensemble

La génération est la dernière étape du pipeline RAG. Une fois les chunks pertinents récupérés, il faut :
1. Construire un prompt efficace qui inclut ces chunks et la question
2. Appeler le LLM pour synthétiser une réponse
3. Optionnellement, inclure des citations vers les sources

La qualité de la génération dépend autant du prompt que du retrieval. Un bon retrieval avec un mauvais prompt donne une mauvaise réponse — et vice versa.

---

## 1. Construction du prompt RAG

### Le prompt minimal

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate

# Prompt RAG basique
PROMPT_RAG_BASE = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui répond aux questions en te basant
exclusivement sur le contexte documentaire fourni.

Règles :
- Si la réponse se trouve dans le contexte, réponds de façon précise et concise.
- Si la réponse ne se trouve PAS dans le contexte, dis clairement :
  "Je ne trouve pas d'information sur ce sujet dans les documents disponibles."
- Ne génère jamais d'information qui n'est pas dans le contexte.
- Réponds toujours en français.

Contexte documentaire :
{context}"""),
    ("human", "{question}")
])
```

### Prompt avec instructions de format

```python
PROMPT_RAG_STRUCTURE = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant expert qui analyse des documents d'entreprise.

DOCUMENTS DE RÉFÉRENCE :
{context}

INSTRUCTIONS :
1. Réponds directement à la question en 2-4 phrases maximum.
2. Base-toi uniquement sur les documents fournis.
3. Si plusieurs documents apportent des informations complémentaires, synthétise-les.
4. Si l'information est absente des documents, indique-le explicitement.
5. Utilise un langage professionnel mais accessible."""),
    ("human", "Question : {question}")
])
```

### Prompt avec contexte de rôle

```python
# Adapter le prompt selon le domaine métier
def creer_prompt_domaine(domaine: str, ton: str = "professionnel") -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", f"""Tu es un assistant spécialisé en {domaine}.
Tu réponds aux questions en te basant exclusivement sur la documentation fournie.
Ton style de communication est {ton}.

Documentation disponible :
{{context}}

Si une information n'est pas dans la documentation, dis-le clairement
plutôt que de deviner."""),
        ("human", "{{question}}")
    ])

# Exemples d'utilisation
prompt_juridique = creer_prompt_domaine("droit des contrats", "formel et précis")
prompt_support = creer_prompt_domaine("support client", "chaleureux et pédagogue")
prompt_technique = creer_prompt_domaine("documentation technique", "technique et concis")
```

---

## 2. Formatage des chunks dans le contexte

La façon dont on formate les chunks dans le prompt impacte la qualité des réponses.

```python
from langchain_core.documents import Document
from typing import List

# Format basique : texte brut concaténé
def format_docs_simple(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

# Format avec séparateurs numérotés
def format_docs_numeros(docs: List[Document]) -> str:
    return "\n\n".join(
        f"[Document {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

# Format avec métadonnées (source + page)
def format_docs_avec_sources(docs: List[Document]) -> str:
    parties = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "source inconnue")
        page = doc.metadata.get("page", "")
        ref = f"{source}, page {page}" if page != "" else source
        parties.append(f"[Source {i+1} : {ref}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parties)

# Format XML (parfois mieux parsé par les LLM)
def format_docs_xml(docs: List[Document]) -> str:
    parties = ["<documents>"]
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "inconnu")
        parties.append(f"""  <document id="{i+1}" source="{source}">
    {doc.page_content}
  </document>""")
    parties.append("</documents>")
    return "\n".join(parties)
```

---

## 3. Chaîne RAG complète avec LCEL

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Composants
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Réponds à la question en te basant uniquement sur le contexte.
Si l'information n'est pas disponible, dis-le clairement.

Contexte :
{context}"""),
    ("human", "{question}")
])

# Chaîne LCEL
rag_chain = (
    {
        "context": retriever | format_docs_avec_sources,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

reponse = rag_chain.invoke("Quelle est la durée de garantie ?")
print(reponse)
```

### Streaming de la réponse

```python
# Streamer token par token
print("Réponse : ", end="", flush=True)
for token in rag_chain.stream("Quelles sont les conditions de retour ?"):
    print(token, end="", flush=True)
print()  # Nouvelle ligne à la fin
```

---

## 4. Réponses avec citations

Inclure des citations dans les réponses est essentiel pour la confiance et la vérifiabilité.

```python
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Optional

# Définir le format de sortie structuré
class Citation(BaseModel):
    source: str = Field(description="Nom du fichier source")
    page: Optional[int] = Field(description="Numéro de page")
    extrait: str = Field(description="Extrait exact du texte source qui supporte la réponse")

class ReponseAvecCitations(BaseModel):
    reponse: str = Field(description="Réponse complète à la question")
    citations: List[Citation] = Field(description="Liste des sources utilisées")
    confiance: str = Field(
        description="Niveau de confiance : 'élevé', 'moyen', 'faible'",
    )

# Parser structuré
parser = JsonOutputParser(pydantic_object=ReponseAvecCitations)

PROMPT_CITATIONS = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui répond aux questions avec des citations précises.

Pour chaque affirmation dans ta réponse, tu dois citer la source documentaire.

Documents disponibles :
{context}

{format_instructions}"""),
    ("human", "{question}")
]).partial(format_instructions=parser.get_format_instructions())

# Chaîne avec citations
chain_citations = (
    {
        "context": retriever | format_docs_avec_sources,
        "question": RunnablePassthrough()
    }
    | PROMPT_CITATIONS
    | llm
    | parser
)

resultat = chain_citations.invoke("Quelle est la politique de retour ?")
print(f"Réponse : {resultat['reponse']}\n")
print("Citations :")
for cite in resultat['citations']:
    print(f"  - {cite['source']} (p.{cite.get('page', '?')})")
    print(f"    « {cite['extrait'][:100]}... »")
print(f"\nConfiance : {resultat['confiance']}")
```

---

## 5. Retourner les sources avec la réponse

Une approche plus simple pour exposer les sources sans JSON structuré :

```python
from langchain_core.runnables import RunnableParallel

# Chaîne qui retourne à la fois la réponse ET les documents source
rag_chain_with_source = RunnableParallel(
    {"reponse": rag_chain, "documents_source": retriever}
)

# Résultat : dict avec "reponse" et "documents_source"
resultat = rag_chain_with_source.invoke("Quels sont les délais de livraison ?")

print("=== Réponse ===")
print(resultat["reponse"])

print("\n=== Sources utilisées ===")
for doc in resultat["documents_source"]:
    source = doc.metadata.get("source", "inconnue")
    page = doc.metadata.get("page", "?")
    print(f"  • {source}, page {page}")
```

---

## 6. Gestion de la fenêtre de contexte

Quand on a beaucoup de chunks, on peut dépasser la fenêtre de contexte du LLM. Voici comment gérer ce cas.

```python
import tiktoken

def compter_tokens(texte: str, modele: str = "gpt-4o-mini") -> int:
    """Compte les tokens pour un modèle donné."""
    enc = tiktoken.encoding_for_model(modele)
    return len(enc.encode(texte))

def tronquer_contexte(
    docs: List[Document],
    max_tokens: int = 6000,
    modele: str = "gpt-4o-mini"
) -> List[Document]:
    """
    Tronque la liste de documents pour respecter la limite de tokens.
    Priorise les premiers documents (les plus pertinents selon le retriever).
    """
    total_tokens = 0
    docs_selectionnes = []

    for doc in docs:
        tokens_doc = compter_tokens(doc.page_content, modele)
        if total_tokens + tokens_doc <= max_tokens:
            docs_selectionnes.append(doc)
            total_tokens += tokens_doc
        else:
            break

    if len(docs_selectionnes) < len(docs):
        print(f"[Warning] Contexte tronqué : {len(docs_selectionnes)}/{len(docs)} docs"
              f" ({total_tokens} tokens)")

    return docs_selectionnes

# Intégrer dans la chaîne
from langchain_core.runnables import RunnableLambda

rag_chain_safe = (
    {
        "context": retriever
                   | RunnableLambda(lambda docs: tronquer_contexte(docs, max_tokens=6000))
                   | format_docs_avec_sources,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

---

## 7. Détection de l'absence de réponse

Il faut gérer le cas où les documents ne contiennent pas la réponse — et éviter que le LLM hallucine.

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional

class ReponseRAG(BaseModel):
    reponse_trouvee: bool = Field(
        description="True si la réponse est dans les documents, False sinon"
    )
    reponse: str = Field(
        description="La réponse si trouvée, ou l'explication de l'absence d'information"
    )
    confiance: float = Field(
        description="Score de confiance entre 0.0 et 1.0"
    )

parser_check = JsonOutputParser(pydantic_object=ReponseRAG)

PROMPT_AVEC_CHECK = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui répond aux questions en analysant des documents.

Documents :
{context}

Analyse d'abord si la réponse se trouve dans les documents, puis réponds.

{format_instructions}"""),
    ("human", "{question}")
]).partial(format_instructions=parser_check.get_format_instructions())

chain_avec_check = (
    {
        "context": retriever | format_docs_avec_sources,
        "question": RunnablePassthrough()
    }
    | PROMPT_AVEC_CHECK
    | llm
    | parser_check
)

# Test avec une question hors-sujet
resultat = chain_avec_check.invoke("Quelle est la météo à Paris aujourd'hui ?")
if not resultat["reponse_trouvee"]:
    print(f"Information non disponible : {resultat['reponse']}")
else:
    print(f"Réponse (confiance {resultat['confiance']:.0%}) : {resultat['reponse']}")
```

---

## 8. Chaîne RAG production complète

```python
# rag_production.py
from dotenv import load_dotenv
load_dotenv()

from typing import List, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.documents import Document
import tiktoken

# ---- Configuration ----
CHROMA_DIR = "./chroma_db"
COLLECTION = "knowledge_base"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
K_RETRIEVE = 5
MAX_CONTEXT_TOKENS = 6000

# ---- Composants ----
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(
    collection_name=COLLECTION,
    embedding_function=embeddings,
    persist_directory=CHROMA_DIR,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": K_RETRIEVE})
llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

# ---- Helpers ----
enc = tiktoken.encoding_for_model(LLM_MODEL)

def format_contexte(docs: List[Document]) -> str:
    """Formate les chunks avec références de source."""
    return "\n\n---\n\n".join(
        f"[Ref {i+1} — {doc.metadata.get('source','?')}, p.{doc.metadata.get('page','?')}]\n"
        f"{doc.page_content}"
        for i, doc in enumerate(docs)
    )

def tronquer(docs: List[Document]) -> List[Document]:
    total, result = 0, []
    for doc in docs:
        n = len(enc.encode(doc.page_content))
        if total + n <= MAX_CONTEXT_TOKENS:
            result.append(doc)
            total += n
    return result

# ---- Prompt ----
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant expert qui répond aux questions en te basant
exclusivement sur la documentation fournie.

RÈGLES :
- Réponds de façon précise et concise (maximum 5 phrases).
- Si la réponse est dans plusieurs sources, synthétise-les.
- Indique les numéros de référence [Ref N] dans ta réponse quand c'est utile.
- Si l'information est absente, dis clairement : "Cette information n'est pas disponible dans la documentation."
- Ne génère jamais d'information non présente dans le contexte.

DOCUMENTATION :
{context}"""),
    ("human", "{question}")
])

# ---- Chaîne principale ----
_prep_contexte = (
    retriever
    | RunnableLambda(tronquer)
    | RunnableLambda(format_contexte)
)

rag_chain = (
    RunnableParallel({
        "context": _prep_contexte,
        "question": RunnablePassthrough(),
    })
    | PROMPT
    | llm
    | StrOutputParser()
)

# ---- Interface publique ----
def interroger(question: str, stream: bool = False) -> str:
    """Point d'entrée principal du RAG."""
    if stream:
        reponse = ""
        for token in rag_chain.stream(question):
            print(token, end="", flush=True)
            reponse += token
        print()
        return reponse
    else:
        return rag_chain.invoke(question)


if __name__ == "__main__":
    print("=== Système RAG prêt ===\n")
    questions = [
        "Quelles sont les conditions de garantie ?",
        "Quel est le délai de livraison standard ?",
        "Comment contacter le service client ?",
        "Quelle est la météo à Paris ?",  # Question hors-sujet
    ]
    for q in questions:
        print(f"Q: {q}")
        reponse = interroger(q)
        print(f"R: {reponse}\n")
        print("-" * 60 + "\n")
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution de `rag_production.py` dans le terminal, montrant les 4 questions — en particulier la différence entre une question avec réponse disponible et la question hors-sujet
> **Expliquer :** Montrer que la question sur la météo reçoit "Cette information n'est pas disponible", tandis que les autres reçoivent des réponses précises avec des références [Ref N]. Modifier le prompt en direct pour supprimer la règle "ne génère jamais d'information" et montrer ce qui se passe (hallucination probable) — puis remettre la règle.

---

## 9. Optimiser la qualité des réponses

### Ajuster la température

```python
# Temperature 0 = réponse déterministe, factuelle — idéal pour RAG
llm_factuel = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Temperature 0.3 = légèrement créatif, utile pour la rédaction
llm_redacteur = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Temperature 0 est presque toujours le bon choix pour un RAG
```

### Choisir le bon modèle

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

# GPT-4o-mini : bon rapport qualité/prix, idéal pour RAG standard
llm_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# GPT-4o : pour les synthèses complexes, documents longs
llm_gpt4o = ChatOpenAI(model="gpt-4o", temperature=0)

# Claude 3.5 Haiku : très rapide, bon pour les questions courtes
llm_haiku = ChatAnthropic(model="claude-3-5-haiku-20241022", temperature=0)

# Llama 3.1 local : 100% gratuit, confidentialité maximale
llm_local = ChatOllama(model="llama3.1:8b", temperature=0)
```

### Prompt engineering avancé

```python
# Technique : Few-shot examples dans le prompt RAG
PROMPT_FEW_SHOT = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant qui répond aux questions sur la documentation.

EXEMPLE DE BONNE RÉPONSE :
Question : "Quel est le délai de retour ?"
Contexte : "Les clients disposent de 14 jours calendaires pour retourner tout article..."
Réponse : "Le délai de retour est de 14 jours calendaires à compter de la réception."

EXEMPLE DE RÉPONSE QUAND L'INFO EST ABSENTE :
Question : "Quelle est l'adresse du siège social ?"
Contexte : [documents sur les produits, pas d'adresse]
Réponse : "Cette information n'est pas disponible dans la documentation fournie."

DOCUMENTATION ACTUELLE :
{context}"""),
    ("human", "{question}")
])
```

---

## Récapitulatif

| Aspect | Recommandation |
|--------|---------------|
| Prompt | Instructions claires sur le comportement en l'absence d'info |
| Format contexte | Inclure les sources/numéros de référence |
| Gestion contexte | Tronquer si > limite tokens du modèle |
| Citations | Retourner `documents_source` en parallèle de la réponse |
| Température | 0 pour les RAG factuels |
| Absence d'info | Détecter et refuser explicitement (pas d'hallucination) |
| Streaming | Préférer `.stream()` pour les UIs en temps réel |

La suite : [Evaluation/01-metriques.md](../Evaluation/01-metriques.md) — Mesurer la qualité de votre système RAG
