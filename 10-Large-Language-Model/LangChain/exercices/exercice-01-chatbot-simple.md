# Exercice 01 — Chatbot avec Historique de Conversation

## Objectif

Construire un chatbot en ligne de commande qui :
- Maintient un historique de conversation entre les messages
- Permet de personnaliser la personnalité du bot via un system prompt
- Affiche des informations de debug (nombre de messages, tokens)
- Gère la sortie proprement

**Durée estimée :** 45 minutes
**Niveau :** Débutant
**Prérequis :** Modules 01 et 03

---

## Contexte

Vous travaillez pour une entreprise qui veut créer un assistant interne pour ses data engineers. Le chatbot doit se souvenir du contexte de la conversation pour répondre de manière cohérente aux questions techniques.

---

## Partie 1 — Chatbot basique (20 min)

### Objectif partiel

Créer un chatbot fonctionnel avec historique en mémoire.

### Instructions

Créez un fichier `chatbot_basique.py` et implémentez les éléments suivants :

**Étape 1.1 — Configurer le modèle**

```python
# chatbot_basique.py
from dotenv import load_dotenv
load_dotenv()

# TODO 1 : Importer ChatOpenAI (ou ChatOllama si pas de clé OpenAI)
# TODO 2 : Créer une instance du LLM avec temperature=0.7
```

**Étape 1.2 — Créer le prompt avec historique**

```python
# TODO 3 : Importer ChatPromptTemplate et MessagesPlaceholder
# TODO 4 : Créer un ChatPromptTemplate avec :
#   - Un message "system" qui définit la personnalité du bot
#   - Un MessagesPlaceholder pour "chat_history"
#   - Un message "human" pour "{input}"

SYSTEM_PROMPT = """Tu es DataBot, un assistant expert en data engineering.
Tu es spécialisé dans : Python, SQL, Spark, dbt, Airflow, et les architectures de données.
Tu te souviens de tout ce qui a été dit dans la conversation.
Tu adaptes tes réponses au niveau de l'utilisateur."""
```

**Étape 1.3 — Créer la chaîne et la mémoire**

```python
# TODO 5 : Importer StrOutputParser
# TODO 6 : Composer la chaîne (prompt | llm | parser)
# TODO 7 : Importer ChatMessageHistory et RunnableWithMessageHistory
# TODO 8 : Créer un store dict et une fonction get_session_history
# TODO 9 : Envelopper la chaîne avec RunnableWithMessageHistory
```

**Étape 1.4 — Boucle de conversation**

```python
# TODO 10 : Implémenter la boucle principale :
# - Lire l'input utilisateur avec input()
# - Sortir si l'utilisateur tape "quit" ou "exit"
# - Invoquer le chatbot avec le bon config (session_id)
# - Afficher la réponse

if __name__ == "__main__":
    print("DataBot est prêt ! (tapez 'quit' pour quitter)\n")
    # Votre code ici
```

### Résultat attendu

```
DataBot est prêt ! (tapez 'quit' pour quitter)

Vous : Bonjour, je m'appelle Marie et j'apprends Apache Spark.
DataBot : Bonjour Marie ! C'est super que vous appreniez Apache Spark...

Vous : Quelle est la différence entre les RDD et les DataFrames ?
DataBot : Bonjour Marie ! Pour répondre à votre question sur Spark...

Vous : Donne-moi un exemple de code pour mon niveau actuel.
DataBot : Bien sûr Marie, voici un exemple adapté à un débutant en Spark...
```

---

## Partie 2 — Améliorations (15 min)

### Objectif partiel

Ajouter des fonctionnalités utiles au chatbot.

### Amélioration 2.1 — Compteur de messages

Ajoutez un affichage qui montre l'état de l'historique après chaque message :

```python
# Après chaque réponse, afficher :
# [Session: session-001 | Messages: 4 | Tokens estimés: ~256]

def afficher_stats(session_id: str, store: dict):
    """Affiche les statistiques de la session courante."""
    nb_messages = len(store.get(session_id, {}).messages if hasattr(store.get(session_id, {}), 'messages') else [])
    # TODO : calculer une estimation des tokens (nb de mots * 1.3)
    print(f"[Messages: {nb_messages}]")
```

### Amélioration 2.2 — Commandes spéciales

Ajoutez des commandes préfixées par `/` :

```python
COMMANDES = {
    "/aide": "Affiche cette aide",
    "/clear": "Vide l'historique de conversation",
    "/history": "Affiche les N derniers messages",
    "/quit": "Quitte le chatbot",
}

def traiter_commande(commande: str, session_id: str, store: dict) -> bool:
    """
    Traite une commande spéciale.
    Retourne True si une commande a été traitée, False sinon.
    """
    if commande == "/aide":
        for cmd, desc in COMMANDES.items():
            print(f"  {cmd} — {desc}")
        return True

    elif commande == "/clear":
        # TODO : vider l'historique de la session
        print("Historique vidé.")
        return True

    elif commande.startswith("/history"):
        # TODO : afficher les derniers messages
        # Bonus : parser /history 5 pour les 5 derniers
        return True

    return False
```

### Amélioration 2.3 — Plusieurs sessions

Permettre de changer de session pendant l'exécution :

```python
# Commande : /session <nom>
# Ex : /session projet-a → change la session active
# Les conversations sont indépendantes par session

elif commande.startswith("/session"):
    parts = commande.split(" ", 1)
    if len(parts) > 1:
        nouvelle_session = parts[1].strip()
        # TODO : changer la session active
        print(f"Session changée : {nouvelle_session}")
    return True
```

---

## Partie 3 — Version fichier persistant (10 min)

### Objectif partiel

Remplacer le stockage en mémoire par un stockage persistant dans des fichiers JSON.

```python
# chatbot_persistant.py
import os
from langchain_community.chat_message_histories import FileChatMessageHistory

SESSIONS_DIR = "./sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def get_persistent_history(session_id: str):
    """
    TODO : Retourner un FileChatMessageHistory qui stocke
    la conversation dans ./sessions/{session_id}.json
    """
    pass

# TODO : Modifier le chatbot pour utiliser get_persistent_history
# Tester en relançant le script — la conversation doit persister !
```

**Test de persistance :**
1. Lancer le chatbot
2. Dire "Je m'appelle Thomas et j'adore le SQL."
3. Quitter avec `/quit`
4. Relancer le chatbot
5. Demander "Comment je m'appelle ?" → Le bot doit se souvenir !

---

## Corrigé commenté

### chatbot_basique.py — solution complète

```python
# chatbot_basique.py — CORRIGÉ
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# ─── Configuration ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es DataBot, un assistant expert en data engineering.
Tu es spécialisé dans : Python, SQL, Spark, dbt, Airflow, et les architectures de données.
Tu te souviens de tout ce qui a été dit dans la conversation.
Tu adaptes tes réponses au niveau de l'utilisateur.
Si tu ne connais pas quelque chose, tu le dis clairement."""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()

# ─── Gestion de la mémoire ───────────────────────────────────────────────────

store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# ─── Commandes ───────────────────────────────────────────────────────────────

COMMANDES_AIDE = {
    "/aide": "Affiche cette aide",
    "/clear": "Vide l'historique",
    "/history [N]": "Affiche les N derniers messages (défaut: 5)",
    "/session <nom>": "Change de session",
    "/quit": "Quitte le chatbot",
}

session_active = "default"

def traiter_commande(commande: str) -> bool:
    global session_active

    if commande == "/aide":
        print("\nCommandes disponibles :")
        for cmd, desc in COMMANDES_AIDE.items():
            print(f"  {cmd:20} — {desc}")
        print()
        return True

    elif commande == "/clear":
        if session_active in store:
            store[session_active].clear()
        print("[Historique vidé]\n")
        return True

    elif commande.startswith("/history"):
        parts = commande.split()
        n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
        history = store.get(session_active)
        if history and history.messages:
            print(f"\nDerniers {n} messages :")
            for msg in history.messages[-n:]:
                role = "Vous" if msg.type == "human" else "DataBot"
                print(f"  [{role}] : {msg.content[:100]}...")
        else:
            print("[Historique vide]")
        print()
        return True

    elif commande.startswith("/session"):
        parts = commande.split(" ", 1)
        if len(parts) > 1:
            session_active = parts[1].strip()
            print(f"[Session active : {session_active}]\n")
        return True

    return False

# ─── Boucle principale ───────────────────────────────────────────────────────

def main():
    global session_active

    print("=" * 50)
    print("  DataBot — Assistant Data Engineering")
    print("  Tapez /aide pour les commandes disponibles")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("Vous : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDataBot : À bientôt !")
            break

        if not user_input:
            continue

        # Commandes spéciales
        if user_input.startswith("/"):
            if user_input in ["/quit", "/exit"]:
                print("DataBot : À bientôt !")
                break
            traiter_commande(user_input)
            continue

        # Appel au chatbot
        try:
            config = {"configurable": {"session_id": session_active}}
            reponse = chatbot.invoke({"input": user_input}, config=config)

            print(f"\nDataBot : {reponse}\n")

            # Stats
            nb_msg = len(store.get(session_active, ChatMessageHistory()).messages)
            print(f"[Session: {session_active} | Messages: {nb_msg}]\n")

        except Exception as e:
            print(f"\n[ERREUR] : {e}\n")

if __name__ == "__main__":
    main()
```

---

## Points de validation

Avant de passer à l'exercice suivant, vérifiez que votre chatbot :

- [ ] Maintient le contexte entre plusieurs messages (test : donner votre nom, puis le demander 2 messages plus tard)
- [ ] La commande `/clear` vide bien l'historique (le bot oublie votre nom après /clear)
- [ ] La commande `/session projet-x` crée une nouvelle conversation indépendante
- [ ] Le bot répond en adaptant ses réponses au contexte (niveau mentionné, préférences, etc.)
- [ ] (Bonus) La version persistante se souvient après redémarrage

---

## Pour aller plus loin

- Ajouter un prompt système configurable via argument CLI (`--persona data-engineer`)
- Implémenter un résumé automatique quand l'historique dépasse 10 messages
- Ajouter un mode verbose qui affiche les tokens utilisés (cf. `response.usage_metadata`)
- Connecter le chatbot à un LLM local (Ollama) pour les tests hors ligne
