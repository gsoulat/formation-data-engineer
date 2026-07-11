# 01 — RAG Conversationnel Multi-tours

## Le problème du RAG sans mémoire

Un RAG simple traite chaque question indépendamment. Dans une vraie conversation, les questions se réfèrent souvent aux réponses précédentes :

```
Tour 1 : "Quelles sont les conditions de garantie ?"
Tour 2 : "Et si je l'achète en ligne, c'est pareil ?"
           ↑ "c'est" réfère à la garantie du tour 1
Tour 3 : "Combien de temps ça prend pour avoir un remboursement ?"
           ↑ "ça" peut référer au processus de retour discuté avant
```

Un RAG simple ne comprend pas ces références contextuelles. Il faut gérer l'historique.

---

## Architecture du RAG conversationnel

```
Histoire de la conversation
[HumanMessage("Garantie ?"), AIMessage("2 ans..."), HumanMessage("En ligne ?")]
                              │
                              ▼
                  Question Reformulation
                  (LLM reformule la question en standalone)
                  "Est-ce que la garantie de 2 ans s'applique aussi aux achats en ligne ?"
                              │
                              ▼
                          Retriever
                    (contexte documentaire)
                              │
                              ▼
              Prompt = historique + chunks + question reformulée
                              │
                              ▼
                             LLM
                              │
                              ▼
                    Réponse + mise à jour historique
```

---

## 1. Reformulation de la question

La clé du RAG conversationnel est de reformuler chaque question en une question "autonome" (standalone) qui intègre le contexte de la conversation.

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prompt de reformulation : transforme question + historique → question standalone
PROMPT_REFORMULATION = ChatPromptTemplate.from_messages([
    ("system", """Étant donné l'historique de conversation ci-dessous et une question de suivi,
reformule la question de suivi en une question autonome et complète, compréhensible
sans l'historique de la conversation.

Si la question est déjà complète et indépendante, retourne-la telle quelle.
Ne réponds PAS à la question — reformule-la seulement.

Réponds uniquement avec la question reformulée, sans explication."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Question de suivi : {question}")
])

chain_reformulation = PROMPT_REFORMULATION | llm | StrOutputParser()

# Test
historique = [
    HumanMessage(content="Quelles sont les conditions de garantie ?"),
    AIMessage(content="La garantie est de 2 ans sur les pièces et la main d'œuvre."),
]

question_suivante = "Et si je l'achète en ligne, c'est pareil ?"

question_reformulee = chain_reformulation.invoke({
    "chat_history": historique,
    "question": question_suivante,
})
print(f"Question originale   : {question_suivante}")
print(f"Question reformulée  : {question_reformulee}")
# → "Est-ce que la garantie de 2 ans sur les pièces et la main d'œuvre s'applique également aux achats effectués en ligne ?"
```

---

## 2. create_history_aware_retriever

LangChain fournit une fonction dédiée pour créer un retriever conscient de l'historique.

```python
from langchain.chains import create_history_aware_retriever
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Composants de base
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prompt de contextualisation (reformulation)
PROMPT_CONTEXTUALISATION = ChatPromptTemplate.from_messages([
    ("system", """Étant donné l'historique de la conversation, reformule la question
en une question standalone compréhensible sans historique. Si déjà standalone, retourne-la."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Retriever conscient de l'historique
history_aware_retriever = create_history_aware_retriever(
    llm=llm,
    retriever=retriever,
    prompt=PROMPT_CONTEXTUALISATION,
)

# Test
from langchain_core.messages import HumanMessage, AIMessage

historique = [
    HumanMessage(content="Quelles sont les conditions de garantie ?"),
    AIMessage(content="La garantie est de 2 ans sur les pièces et la main d'œuvre."),
]

docs = history_aware_retriever.invoke({
    "input": "Et pour les achats en ligne ?",
    "chat_history": historique,
})
print(f"Chunks récupérés : {len(docs)}")
```

---

## 3. create_retrieval_chain — chaîne complète

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Prompt de réponse finale (avec historique et contexte)
PROMPT_REPONSE = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant expert qui répond aux questions sur notre documentation.

Règles :
- Base ta réponse exclusivement sur le contexte documentaire fourni.
- Tiens compte de l'historique de conversation pour une réponse cohérente.
- Si l'information n'est pas dans le contexte, dis-le clairement.

Contexte documentaire :
{context}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Chaîne de génération (combine les documents et génère la réponse)
chaine_generation = create_stuff_documents_chain(llm, PROMPT_REPONSE)

# Chaîne RAG complète avec historique
rag_chain_avec_historique = create_retrieval_chain(
    retriever=history_aware_retriever,
    combine_docs_chain=chaine_generation,
)

# Utilisation
def poser_question(question: str, historique: list) -> dict:
    """Pose une question et retourne la réponse + les documents sources."""
    resultat = rag_chain_avec_historique.invoke({
        "input": question,
        "chat_history": historique,
    })
    return {
        "reponse": resultat["answer"],
        "sources": resultat["context"],
        "question_standalone": resultat.get("input", question),
    }
```

---

## 4. Gestion de l'historique avec RunnableWithMessageHistory

Pour une application réelle, l'historique doit être persisté par session utilisateur.

```python
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import List

# Store en mémoire (session_id → historique)
# En production : remplacer par Redis, PostgreSQL, etc.
store: dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Retourne ou crée l'historique pour une session."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Wrapper avec gestion automatique de l'historique
conversational_rag = RunnableWithMessageHistory(
    runnable=rag_chain_avec_historique,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# Utilisation avec session_id
config_session1 = {"configurable": {"session_id": "utilisateur_alice"}}

reponse1 = conversational_rag.invoke(
    {"input": "Quelles sont les conditions de garantie ?"},
    config=config_session1,
)
print(f"R1: {reponse1['answer']}\n")

reponse2 = conversational_rag.invoke(
    {"input": "Et ça s'applique aux produits reconditionnés ?"},
    config=config_session1,
)
print(f"R2: {reponse2['answer']}\n")

reponse3 = conversational_rag.invoke(
    {"input": "Quelle est la procédure si je veux l'activer ?"},
    config=config_session1,
)
print(f"R3: {reponse3['answer']}\n")

# L'historique d'Alice est isolé de celui de Bob
config_session2 = {"configurable": {"session_id": "utilisateur_bob"}}
reponse_bob = conversational_rag.invoke(
    {"input": "Bonjour, j'ai une question sur les retours."},
    config=config_session2,
)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Une conversation de 4-5 tours dans le terminal, montrant que les questions de suivi ("Et pour ça ?", "Combien de temps ?") reçoivent des réponses cohérentes avec le contexte établi
> **Expliquer :** Lancer la conversation de démonstration. Après le tour 2 ("Et ça s'applique aux reconditionnés ?"), afficher la question reformulée pour montrer ce que le LLM a compris du contexte. Montrer que sans reformulation, le retriever ne trouverait pas les bons chunks pour une question aussi vague que "Et ça s'applique ?".

---

## 5. Limiter la taille de l'historique

En production, l'historique peut devenir très long et dépasser la fenêtre de contexte du LLM.

```python
from langchain_core.messages import BaseMessage, trim_messages
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

# Garder seulement les N derniers messages
def tronquer_historique(historique: List[BaseMessage], max_messages: int = 10) -> List[BaseMessage]:
    """Garde les N derniers messages (par paires human/AI)."""
    if len(historique) <= max_messages:
        return historique
    # Garder les messages pairs pour avoir human + AI ensemble
    n = max_messages if max_messages % 2 == 0 else max_messages - 1
    return historique[-n:]

# Alternative : tronquer par tokens
def tronquer_par_tokens(historique: List[BaseMessage], max_tokens: int = 2000):
    """Utilise trim_messages de LangChain pour respecter une limite en tokens."""
    return trim_messages(
        historique,
        max_tokens=max_tokens,
        token_counter=llm,           # Utilise le tokenizer du LLM
        strategy="last",             # Garder les plus récents
        start_on="human",            # Commencer sur un message humain
        include_system=True,         # Garder le message système si présent
    )

# Intégration dans la chaîne
from langchain_core.runnables import RunnableLambda

def preparer_historique(inputs: dict) -> dict:
    inputs["chat_history"] = tronquer_historique(
        inputs.get("chat_history", []),
        max_messages=8
    )
    return inputs

rag_chain_avec_historique_limite = (
    RunnableLambda(preparer_historique)
    | rag_chain_avec_historique
)
```

---

## 6. Historique persistant avec Redis

En production, l'historique doit survivre aux redémarrages du serveur.

```python
from langchain_community.chat_message_histories import RedisChatMessageHistory

# Redis pour la persistance distribuée
def get_session_history_redis(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url="redis://localhost:6379",
        ttl=3600,  # Expiration après 1 heure d'inactivité
        key_prefix="rag_session:",
    )

conversational_rag_redis = RunnableWithMessageHistory(
    runnable=rag_chain_avec_historique,
    get_session_history=get_session_history_redis,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)
```

---

## 7. Application chatbot complète

```python
# chatbot_rag.py
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Setup
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prompts
PROMPT_CONTEXT = ChatPromptTemplate.from_messages([
    ("system", "Reformule la question en standalone en tenant compte de l'historique."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

PROMPT_REPONSE = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant documentation. Réponds en français, de façon concise.
Utilise uniquement le contexte fourni. Si l'info est absente, dis-le.

Contexte : {context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# Chaîne
history_retriever = create_history_aware_retriever(llm, retriever, PROMPT_CONTEXT)
qa_chain = create_stuff_documents_chain(llm, PROMPT_REPONSE)
rag_chain = create_retrieval_chain(history_retriever, qa_chain)

store = {}

def get_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    rag_chain, get_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


def chat(question: str, session_id: str = "default") -> str:
    """Interface simple pour le chatbot."""
    config = {"configurable": {"session_id": session_id}}
    result = chatbot.invoke({"input": question}, config=config)
    return result["answer"]


if __name__ == "__main__":
    print("=== Chatbot RAG Conversationnel ===")
    print("Tapez 'quit' pour quitter, 'reset' pour effacer l'historique\n")

    session = "demo_session"

    while True:
        question = input("Vous : ").strip()
        if question.lower() == "quit":
            break
        if question.lower() == "reset":
            store.pop(session, None)
            print("Historique effacé.\n")
            continue
        if not question:
            continue

        reponse = chat(question, session_id=session)
        print(f"Assistant : {reponse}\n")
```

---

## Récapitulatif

| Concept | Outil LangChain | Description |
|---------|----------------|-------------|
| Reformulation | `create_history_aware_retriever` | Question → Question standalone |
| Génération | `create_stuff_documents_chain` | Chunks + historique → Réponse |
| Pipeline complet | `create_retrieval_chain` | Combine les deux |
| Gestion sessions | `RunnableWithMessageHistory` | Historique par session_id |
| Persistance | `RedisChatMessageHistory` | Historique en Redis |
| Troncature | `tronquer_historique()` | Éviter la surcharge de contexte |

La suite : [02-self-rag.md](./02-self-rag.md) — Self-RAG et Corrective RAG
