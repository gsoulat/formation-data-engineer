# 03 — Mémoire et Contexte Conversationnel

## Pourquoi la mémoire est-elle nécessaire ?

Les LLM sont par nature **sans état** (stateless). Chaque appel à l'API est indépendant : le modèle ne se souvient de rien des échanges précédents. Pour construire un chatbot cohérent, il faut explicitement passer l'historique des messages à chaque requête.

```python
# Sans gestion de mémoire — le modèle oublie !
llm = ChatOpenAI(model="gpt-4o-mini")

r1 = llm.invoke([HumanMessage(content="Je m'appelle Alice.")])
print(r1.content)  # "Bonjour Alice !"

r2 = llm.invoke([HumanMessage(content="Comment je m'appelle ?")])
print(r2.content)  # "Je ne connais pas votre nom..."  ← oubli !
```

La gestion de la mémoire consiste à :
1. Stocker les messages échangés
2. Les injecter dans le prompt à chaque nouveau tour
3. Gérer la taille de l'historique (fenêtre de contexte limitée)

---

## Types de mémoire dans LangChain

| Type | Description | Usage |
|------|-------------|-------|
| `ChatMessageHistory` | Stockage brut de messages | Base pour tout le reste |
| `ConversationBufferMemory` | Tous les messages, non compressés | Conversations courtes |
| `ConversationBufferWindowMemory` | Fenêtre glissante des N derniers messages | Conversations longues |
| `ConversationSummaryMemory` | Résumé de la conversation | Très longues conversations |
| `ConversationSummaryBufferMemory` | Hybride : résumé + messages récents | Usage général recommandé |
| `VectorStoreRetrieverMemory` | Recherche par similarité dans l'historique | Conversations riches |

---

## ChatMessageHistory — le stockage de base

`ChatMessageHistory` est la brique fondamentale. Elle stocke une liste ordonnée de messages.

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Créer un historique
historique = ChatMessageHistory()

# Ajouter des messages
historique.add_user_message("Bonjour, je m'appelle Alice.")
historique.add_ai_message("Bonjour Alice ! Ravi de vous rencontrer.")
historique.add_user_message("Quel est mon prénom ?")
historique.add_ai_message("Votre prénom est Alice.")

# Accéder aux messages
for msg in historique.messages:
    print(f"[{msg.type}] : {msg.content}")

# Vider l'historique
historique.clear()
```

### Implémentations disponibles

```python
# En mémoire (par défaut — données perdues à l'arrêt du programme)
from langchain_community.chat_message_histories import ChatMessageHistory

# Dans un fichier JSON
from langchain_community.chat_message_histories import FileChatMessageHistory
historique = FileChatMessageHistory("conversation_123.json")

# Dans Redis (pour la production)
from langchain_community.chat_message_histories import RedisChatMessageHistory
historique = RedisChatMessageHistory(
    session_id="user-123",
    url="redis://localhost:6379"
)

# Dans une base SQL
from langchain_community.chat_message_histories import SQLChatMessageHistory
historique = SQLChatMessageHistory(
    session_id="session-abc",
    connection_string="sqlite:///conversations.db"
)
```

---

## ConversationBufferMemory

La mémoire la plus simple : conserve tous les messages de la conversation.

```python
from dotenv import load_dotenv
load_dotenv()

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Modèle
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Prompt avec espace pour l'historique
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant amical et bavard. Tu te souviens de tout ce qui a été dit."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# Chaîne de base
chain = prompt | llm | StrOutputParser()

# Store des historiques par session
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Chaîne avec mémoire
chain_avec_memoire = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Fonction utilitaire pour chatter
def chat(message: str, session_id: str = "default"):
    config = {"configurable": {"session_id": session_id}}
    reponse = chain_avec_memoire.invoke(
        {"input": message},
        config=config
    )
    return reponse

# Conversation
print(chat("Bonjour ! Je m'appelle Thomas et j'apprends Python."))
print(chat("Quelle est ma passion en ce moment ?"))  # Le modèle se souvient !
print(chat("Donne-moi un conseil pour progresser."))
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant la conversation avec mémoire en action, puis inspection du contenu de la mémoire
> **Expliquer :** Lancer la conversation étape par étape. Après chaque réponse, afficher `store["default"].messages` pour montrer l'état de l'historique. Insister sur le fait que la deuxième question ("Quelle est ma passion ?") obtient la bonne réponse PARCE QUE l'historique est injecté. Montrer aussi ce qui se passe si on change le session_id : une nouvelle conversation démarre depuis zéro.

---

## Gestion de la fenêtre de contexte

Les LLM ont une limite de tokens (fenêtre de contexte). Un historique très long peut dépasser cette limite et provoquer des erreurs ou des coûts élevés.

### Calculer l'utilisation de tokens

```python
import tiktoken

def compter_tokens_histoire(historique, model_name="gpt-4o-mini"):
    """Compte le nombre de tokens dans un historique."""
    encoder = tiktoken.encoding_for_model(model_name)
    total = 0
    for msg in historique.messages:
        total += len(encoder.encode(msg.content))
    return total

# Vérifier avant d'envoyer
nb_tokens = compter_tokens_histoire(store["default"])
print(f"Tokens dans l'historique : {nb_tokens}")
# gpt-4o-mini : 128k tokens de contexte
# Attention : plus de tokens = plus cher !
```

### ConversationBufferWindowMemory — fenêtre glissante

```python
from langchain.memory import ConversationBufferWindowMemory

# Conserver seulement les 5 derniers échanges (10 messages)
# Note : dans le pattern moderne avec RunnableWithMessageHistory,
# on gère ça avec une fonction personnalisée

def get_session_history_windowed(session_id: str, k: int = 5):
    """Retourne un historique limité aux k derniers échanges."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()

    history = store[session_id]
    # Garder uniquement les 2*k derniers messages (k échanges = k HumanMessage + k AIMessage)
    if len(history.messages) > 2 * k:
        # Créer un historique tronqué
        history_tronquee = ChatMessageHistory()
        for msg in history.messages[-(2 * k):]:
            history_tronquee.add_message(msg)
        return history_tronquee

    return history

chain_windowed = RunnableWithMessageHistory(
    chain,
    lambda sid: get_session_history_windowed(sid, k=3),
    input_messages_key="input",
    history_messages_key="chat_history"
)
```

---

## ConversationSummaryMemory

Au lieu de stocker tous les messages, cette mémoire utilise un LLM pour résumer progressivement la conversation. Idéale pour les longues sessions.

```python
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI

# Mémoire avec résumé automatique
llm_pour_resume = ChatOpenAI(model="gpt-4o-mini", temperature=0)

memory = ConversationSummaryMemory(
    llm=llm_pour_resume,
    return_messages=True  # Retourner comme objets Message
)

# Simuler une longue conversation
memory.save_context(
    {"input": "Je travaille sur un projet d'analyse de données pour une startup fintech."},
    {"output": "C'est intéressant ! Quel type de données analysez-vous ?"}
)
memory.save_context(
    {"input": "Des données de transactions bancaires, environ 10 millions de lignes par mois."},
    {"output": "À cette échelle, vous avez besoin d'un pipeline robuste. Spark ou Dask ?"}
)
memory.save_context(
    {"input": "Nous utilisons Spark sur Azure Databricks."},
    {"output": "Excellent choix. Databricks est très bien adapté pour ce cas d'usage."}
)

# Voir le résumé généré
print("Résumé actuel :")
print(memory.buffer)
# Output : "L'utilisateur travaille sur un projet d'analyse de données pour une startup fintech.
#           Il analyse des transactions bancaires (10M lignes/mois) avec Spark sur Azure Databricks."

# Utiliser la mémoire dans une chaîne
variables = memory.load_memory_variables({})
print(variables)
```

---

## ConversationSummaryBufferMemory — le meilleur des deux mondes

Combine la précision du buffer (messages récents intacts) et l'efficacité du résumé (messages anciens compressés).

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm_pour_resume,
    max_token_limit=200,    # Seuil en tokens avant de résumer
    return_messages=True
)

# Tant que l'historique fait moins de 200 tokens → stockage intégral
# Au-delà de 200 tokens → les plus anciens sont résumés automatiquement

# Charger les variables pour le prompt
variables = memory.load_memory_variables({})
# variables["history"] = [résumé en SystemMessage] + [messages récents]
```

### Intégration dans une chaîne LCEL moderne

```python
from langchain_core.messages import SystemMessage

def get_history_with_summary(session_id: str):
    """Gère un historique hybride résumé + récent."""
    if session_id not in store:
        store[session_id] = {
            "messages": ChatMessageHistory(),
            "summary": ""
        }
    return store[session_id]["messages"]

# Pour injecter le résumé dans le prompt, on peut utiliser une variante :
prompt_avec_resume = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant conversationnel.

    Résumé de la conversation précédente :
    {summary}

    Si le résumé est vide, c'est le début de la conversation."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration de ConversationSummaryMemory avec une longue conversation et affichage du résumé généré
> **Expliquer :** Créer une conversation de 6-8 échanges sur un sujet précis (ex: un projet de développement). Après chaque 2-3 messages, afficher `memory.buffer` pour montrer comment le résumé évolue. Montrer que le résumé capture les informations clés sans garder tous les tokens bruts. Comparer le nombre de tokens : résumé vs historique complet.

---

## Persistance multi-session

Dans une vraie application, plusieurs utilisateurs ont des conversations simultanées. Le `session_id` permet de les isoler.

```python
from langchain_community.chat_message_histories import FileChatMessageHistory
import os

CONVERSATIONS_DIR = "./conversations"
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_persistent_history(session_id: str) -> ChatMessageHistory:
    """Historique persistant dans un fichier JSON par session."""
    filepath = os.path.join(CONVERSATIONS_DIR, f"{session_id}.json")
    return FileChatMessageHistory(filepath)

# La chaîne utilise des fichiers pour persister entre les redémarrages
chain_persistant = RunnableWithMessageHistory(
    chain,
    get_persistent_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Chaque user a sa propre conversation persistée
chat_alice = lambda msg: chain_persistant.invoke(
    {"input": msg},
    config={"configurable": {"session_id": "alice-123"}}
)

chat_bob = lambda msg: chain_persistant.invoke(
    {"input": msg},
    config={"configurable": {"session_id": "bob-456"}}
)

# Conversations indépendantes
chat_alice("Je programme en Python depuis 3 ans.")
chat_bob("Je suis débutant en programmation.")
chat_alice("Quels sont mes points forts ?")   # Réponse différente de Bob
chat_bob("Quels sont mes points forts ?")      # Réponse adaptée au niveau
```

---

## Chatbot interactif complet

```python
# chatbot_complet.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Configuration
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)

SYSTEM_PROMPT = """Tu es Max, un assistant IA expert en data engineering.
Tu es enthousiaste, bienveillant et pédagogue.
Tu te souviens de tout ce que l'utilisateur t'a dit dans cette conversation.
Quand tu réponds, tu personnalises tes réponses en utilisant ce que tu sais de l'utilisateur."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

store = {}

def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

def main():
    session_id = "session-demo"
    config = {"configurable": {"session_id": session_id}}

    print("=== Chatbot Max (tapez 'quit' pour quitter) ===\n")

    while True:
        user_input = input("Vous : ").strip()

        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Max : À bientôt !")
            break

        try:
            reponse = chatbot.invoke({"input": user_input}, config=config)
            print(f"\nMax : {reponse}\n")

            # Stats de l'historique
            nb_messages = len(store[session_id].messages)
            print(f"[Historique : {nb_messages} messages]\n")

        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
```

---

## Patterns avancés

### Résumé automatique quand le contexte devient trop long

```python
import tiktoken
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

def get_or_create_history(session_id: str, max_tokens: int = 2000):
    """
    Retourne l'historique en compressant automatiquement
    si le seuil de tokens est dépassé.
    """
    if session_id not in store:
        store[session_id] = {"history": ChatMessageHistory(), "summary": ""}

    session = store[session_id]
    history = session["history"]

    # Compter les tokens
    encoder = tiktoken.encoding_for_model("gpt-4o-mini")
    total_tokens = sum(
        len(encoder.encode(msg.content))
        for msg in history.messages
    )

    if total_tokens > max_tokens and len(history.messages) > 4:
        # Résumer les messages anciens (garder les 4 derniers)
        anciens_messages = history.messages[:-4]
        messages_recents = history.messages[-4:]

        # Générer un résumé
        llm_resume = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        texte_historique = "\n".join(
            f"{msg.type}: {msg.content}" for msg in anciens_messages
        )
        resume = llm_resume.invoke(
            f"Résume cette conversation en 3 phrases max :\n{texte_historique}"
        )

        # Recréer l'historique avec le résumé
        nouvelle_history = ChatMessageHistory()
        nouvelle_history.add_message(
            SystemMessage(content=f"Résumé de la conversation précédente : {resume.content}")
        )
        for msg in messages_recents:
            nouvelle_history.add_message(msg)

        store[session_id]["history"] = nouvelle_history
        return nouvelle_history

    return history
```

### Injection de contexte externe

```python
# Enrichir la mémoire avec des données utilisateur depuis une BDD
def get_enriched_history(session_id: str, user_profile: dict = None):
    """Historique enrichi avec le profil utilisateur."""
    history = store.get(session_id, ChatMessageHistory())

    if user_profile and len(history.messages) == 0:
        # Premier message : injecter le profil
        profil_text = f"""Profil de l'utilisateur :
        - Nom : {user_profile.get('nom', 'Inconnu')}
        - Niveau : {user_profile.get('niveau', 'Débutant')}
        - Objectifs : {user_profile.get('objectifs', 'Non définis')}"""

        history.add_message(SystemMessage(content=profil_text))

    return history
```

---

## Récapitulatif

| Scénario | Solution recommandée |
|----------|---------------------|
| Conversation courte (< 20 messages) | `ChatMessageHistory` + `RunnableWithMessageHistory` |
| Conversation longue (20+ messages) | `ConversationSummaryBufferMemory` |
| Multi-utilisateurs web | `session_id` unique par user + stockage Redis/SQL |
| Persistance entre redémarrages | `FileChatMessageHistory` ou `SQLChatMessageHistory` |
| Production à grande échelle | `RedisChatMessageHistory` + limite de tokens |

La suite : [04-multi-providers.md](./04-multi-providers.md) — Travailler avec plusieurs fournisseurs LLM
