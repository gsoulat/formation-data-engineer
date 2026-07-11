# 02 — LCEL et Composition de Chaînes

## Qu'est-ce que LCEL ?

LCEL (LangChain Expression Language) est la syntaxe moderne de LangChain pour composer des pipelines de traitement. Introduit en 2023, il remplace les anciennes classes de chaînes (`LLMChain`, `SequentialChain`, etc.) par une approche déclarative et fonctionnelle.

Le principe fondamental : chaque composant est un `Runnable`, et les `Runnable` se composent avec l'opérateur `|` (pipe), comme en shell Unix.

```python
chain = composant_1 | composant_2 | composant_3
```

L'output de chaque composant devient l'input du suivant.

---

## L'opérateur pipe `|`

### Analogie avec Unix

```bash
# Shell Unix : sortie de cat → entrée de grep → entrée de wc
cat fichier.txt | grep "motclé" | wc -l

# LCEL : même logique
chain = prompt | llm | parser
```

### Comment ça marche en Python

LangChain surcharge l'opérateur `|` sur la classe `Runnable`. En interne, `A | B` crée un `RunnableSequence(A, B)`.

```python
from langchain_core.runnables import RunnableSequence

# Ces deux écritures sont équivalentes :
chain1 = prompt | llm | parser
chain2 = RunnableSequence(first=prompt, middle=[llm], last=parser)

# Vérifier le type
print(type(chain1))  # <class 'langchain_core.runnables.base.RunnableSequence'>
```

---

## L'interface Runnable

Tout composant LCEL implémente cette interface :

```python
# Méthodes disponibles sur n'importe quel Runnable
chain.invoke(input)              # Appel synchrone → retourne le résultat final
chain.batch([input1, input2])    # Appel batch → retourne une liste de résultats
chain.stream(input)              # Streaming → itérateur sur les tokens

# Versions asynchrones
await chain.ainvoke(input)
await chain.abatch([...])
async for chunk in chain.astream(input): ...

# Introspection
chain.input_schema               # Pydantic model du schéma d'entrée
chain.output_schema              # Pydantic model du schéma de sortie
chain.get_graph()                # Graphe de l'exécution
chain.get_graph().print_ascii()  # Affichage ASCII du graphe
```

### Exemple concret de streaming

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("Explique {concept} en 3 phrases.")
chain = prompt | llm | StrOutputParser()

# Streaming token par token
print("Réponse en streaming :")
for chunk in chain.stream({"concept": "le machine learning"}):
    print(chunk, end="", flush=True)
print()  # Nouvelle ligne finale
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant l'exécution du streaming avec les tokens qui apparaissent progressivement
> **Expliquer :** Lancer le script de streaming et montrer comment les tokens s'affichent au fur et à mesure (pas en une seule fois). Expliquer la différence entre `invoke` (attendre la réponse complète) et `stream` (afficher au fil de l'eau). Montrer l'utilité du `flush=True` pour forcer l'affichage immédiat dans le terminal.

---

## PromptTemplate en détail

### PromptTemplate (texte simple)

```python
from langchain_core.prompts import PromptTemplate

# Template basique
template = PromptTemplate.from_template(
    "Traduis ce texte en {langue} : {texte}"
)

# Formatter manuellement
result = template.format(langue="espagnol", texte="Bonjour le monde")
print(result)
# "Traduis ce texte en espagnol : Bonjour le monde"

# Avec des valeurs par défaut
template_avec_defaut = PromptTemplate(
    template="Génère {nb} idées pour {sujet}",
    input_variables=["sujet"],
    partial_variables={"nb": "5"}  # valeur par défaut
)

# nb est déjà rempli, seul sujet est requis
print(template_avec_defaut.format(sujet="une startup tech"))
```

### ChatPromptTemplate

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Format tuple (type, contenu)
prompt1 = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en {domaine}."),
    ("human", "{question}")
])

# Format avec objets Message
from langchain_core.messages import SystemMessage, HumanMessage
prompt2 = ChatPromptTemplate.from_messages([
    SystemMessage(content="Tu es un assistant."),
    HumanMessage(content="{question}")
])

# Avec espace réservé pour l'historique
prompt_avec_historique = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant conversationnel."),
    MessagesPlaceholder(variable_name="chat_history"),  # ← historique injecté ici
    ("human", "{input}")
])

# Partial — pré-remplir certaines variables
prompt_partiel = prompt1.partial(domaine="cybersécurité")
# Maintenant, seul "question" est requis
messages = prompt_partiel.invoke({"question": "Qu'est-ce qu'un SQL injection ?"})
```

### FewShotChatMessagePromptTemplate

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate

# Exemples pour guider le modèle
examples = [
    {"input": "2 + 2", "output": "4"},
    {"input": "3 × 7", "output": "21"},
    {"input": "100 ÷ 4", "output": "25"},
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es une calculatrice. Réponds uniquement avec le résultat numérique."),
    few_shot_prompt,
    ("human", "{question}")
])
```

---

## Output Parsers en détail

### StrOutputParser

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# Input : AIMessage(content="Bonjour")
# Output : "Bonjour"  (simple string)
```

### CommaSeparatedListOutputParser

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate

parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate(
    template="Liste 5 {categorie} séparés par des virgules.\n{format_instructions}",
    input_variables=["categorie"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

# Output : ["Python", "JavaScript", "Rust", "Go", "TypeScript"]
result = chain.invoke({"categorie": "langages de programmation populaires"})
print(result)  # liste Python
```

### PydanticOutputParser — sortie structurée

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class AnalyseSentiment(BaseModel):
    sentiment: str = Field(description="positif, négatif, ou neutre")
    score: float = Field(description="Score de confiance entre 0 et 1")
    mots_cles: List[str] = Field(description="Mots-clés qui justifient le sentiment")
    resume: str = Field(description="Résumé en une phrase")

parser = PydanticOutputParser(pydantic_object=AnalyseSentiment)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en analyse de sentiment."),
    ("human", """Analyse le sentiment de ce texte :

    {texte}

    {format_instructions}""")
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser

# Texte à analyser
texte = "Ce produit est absolument fantastique ! Je l'ai reçu rapidement et la qualité dépasse mes attentes."
result = chain.invoke({"texte": texte})

print(f"Sentiment : {result.sentiment}")
print(f"Score : {result.score}")
print(f"Mots-clés : {result.mots_cles}")
print(f"Résumé : {result.resume}")
```

### JsonOutputParser

```python
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template(
    """Génère des informations sur un pays fictif au format JSON.
    Inclure: nom, capitale, population, langue_officielle, monnaie.
    Réponds UNIQUEMENT avec le JSON, sans markdown.

    Pays : {pays}"""
)

chain = prompt | llm | parser
result = chain.invoke({"pays": "Valdorie"})
print(result)  # dict Python
```

---

## Composition avancée

### RunnablePassthrough — passer l'input tel quel

```python
from langchain_core.runnables import RunnablePassthrough

# Passer une valeur sans transformation
chain = RunnablePassthrough() | llm | StrOutputParser()

# Très utile dans les chaînes parallèles pour conserver l'input original
```

### RunnableParallel — exécution en parallèle

```python
from langchain_core.runnables import RunnableParallel

# Exécuter deux chaînes en parallèle, combiner les résultats
chain_resume = (
    ChatPromptTemplate.from_template("Résume en 2 phrases : {texte}") | llm | StrOutputParser()
)
chain_mots_cles = (
    ChatPromptTemplate.from_template("Extrais 5 mots-clés de : {texte}. Sépare par des virgules.") | llm | StrOutputParser()
)

# Les deux chaînes s'exécutent en parallèle
parallel_chain = RunnableParallel(
    resume=chain_resume,
    mots_cles=chain_mots_cles
)

# Même syntaxe avec dict
parallel_chain2 = {
    "resume": chain_resume,
    "mots_cles": chain_mots_cles
}

texte = "L'intelligence artificielle transforme de nombreux secteurs industriels..."
result = parallel_chain.invoke({"texte": texte})

print("Résumé :", result["resume"])
print("Mots-clés :", result["mots_cles"])
```

### RunnableLambda — fonctions Python comme Runnables

```python
from langchain_core.runnables import RunnableLambda

# Transformer une fonction en Runnable
def nettoyer_texte(text: str) -> str:
    """Nettoie un texte avant de l'envoyer au LLM."""
    return text.strip().lower().replace("\n\n", "\n")

def compter_mots(text: str) -> dict:
    """Retourne le texte avec un comptage de mots."""
    return {
        "texte": text,
        "nb_mots": len(text.split()),
        "nb_chars": len(text)
    }

# Convertir en Runnable
nettoyer = RunnableLambda(nettoyer_texte)
compter = RunnableLambda(compter_mots)

# Utiliser dans une chaîne
pipeline = nettoyer | compter
result = pipeline.invoke("  Bonjour le Monde  \n\n  Comment ça va ?  ")
print(result)
# {'texte': 'bonjour le monde\ncomment ça va ?', 'nb_mots': 6, 'nb_chars': 34}
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution d'une chaîne RunnableParallel avec deux branches, et la trace LangSmith montrant l'exécution parallèle
> **Expliquer :** Montrer le code de la chaîne parallèle, l'exécuter, afficher le résultat. Puis ouvrir LangSmith et montrer la trace : les deux branches apparaissent au même niveau, ce qui confirme leur exécution simultanée. Expliquer l'avantage en termes de latence (temps total = max des deux, pas la somme).

---

## Pattern RAG simplifié avec LCEL

Un exemple complet montrant la puissance de LCEL pour construire un RAG (Retrieval Augmented Generation) minimal :

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 1. Créer une base de documents (normalement chargée depuis des fichiers)
documents = [
    Document(page_content="LangChain est un framework pour construire des apps LLM."),
    Document(page_content="LCEL utilise l'opérateur pipe | pour composer des chaînes."),
    Document(page_content="LangSmith permet de tracer et déboguer les applications LangChain."),
    Document(page_content="Les agents LangChain peuvent utiliser des outils comme des APIs et des calculs."),
]

# 2. Créer le vecteur store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 3. Template RAG
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """Tu es un assistant expert. Réponds en te basant uniquement
    sur le contexte fourni. Si l'information n'est pas dans le contexte,
    dis-le clairement.

    Contexte :
    {context}"""),
    ("human", "{question}")
])

# 4. Fonction pour formater les documents récupérés
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. Chaîne RAG complète
llm = ChatOpenAI(model="gpt-4o-mini")

rag_chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# 6. Utilisation
reponse = rag_chain.invoke("Qu'est-ce que LangSmith ?")
print(reponse)
```

---

## Gestion des erreurs dans les chaînes

### with_fallbacks

```python
from langchain_openai import ChatOpenAI

# Modèle principal + fallback en cas d'erreur
llm_principal = ChatOpenAI(model="gpt-4o")
llm_backup = ChatOpenAI(model="gpt-4o-mini")

llm_robuste = llm_principal.with_fallbacks([llm_backup])

chain = prompt | llm_robuste | StrOutputParser()
```

### with_retry

```python
# Réessayer en cas d'erreur réseau
llm_avec_retry = llm.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)
```

### catch_exceptions dans RunnableLambda

```python
def traitement_securise(input_dict):
    try:
        return traitement_normal(input_dict)
    except ValueError as e:
        return {"erreur": str(e), "input_original": input_dict}

chain = RunnableLambda(traitement_securise) | llm | parser
```

---

## Inspecter une chaîne

```python
# Afficher le schéma d'entrée attendu
print(chain.input_schema.schema())

# Afficher le schéma de sortie
print(chain.output_schema.schema())

# Visualiser le graphe de la chaîne (ASCII)
chain.get_graph().print_ascii()
# Output :
# +-----------------------+
# | ChatPromptTemplate    |
# +-----------------------+
#            *
#            *
#            *
#    +---------------+
#    | ChatOpenAI    |
#    +---------------+
#            *
#            *
#            *
#  +------------------+
#  | StrOutputParser  |
#  +------------------+
```

---

## Chaînes avec état — RunnableWithMessageHistory

Cette fonctionnalité est détaillée dans le module suivant (Mémoire). Voici un aperçu :

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Store des sessions en mémoire
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Envelopper la chaîne avec la gestion d'historique
chain_avec_memoire = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Appeler avec un session_id
config = {"configurable": {"session_id": "user-123"}}
chain_avec_memoire.invoke({"input": "Bonjour !"}, config=config)
chain_avec_memoire.invoke({"input": "Comment tu t'appelles ?"}, config=config)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Exécution du script RAG complet avec affichage de la réponse et de la trace LangSmith
> **Expliquer :** Lancer le script RAG pas à pas. D'abord montrer que le retriever trouve les bons documents (print des docs récupérés), puis montrer la réponse finale. Dans LangSmith, ouvrir la trace et montrer les étapes : retrieval → prompt construction → LLM call → parsing. Mettre en évidence comment le contexte des documents est injecté dans le prompt.

---

## Récapitulatif LCEL

| Composant | Rôle | Exemple |
|-----------|------|---------|
| `\|` | Composer deux Runnables | `prompt \| llm \| parser` |
| `RunnablePassthrough()` | Passer l'input sans modification | Conserver la question originale |
| `RunnableParallel({})` | Exécuter des branches en parallèle | Résumé ET extraction |
| `RunnableLambda(fn)` | Transformer une fonction Python en Runnable | Nettoyage de texte |
| `.invoke()` | Exécuter de façon synchrone | Usage standard |
| `.stream()` | Exécuter avec streaming | Interface chat |
| `.batch()` | Exécuter sur plusieurs inputs | Traitement en lot |
| `.with_fallbacks()` | Ajouter un LLM de secours | Robustesse en production |

La suite : [03-memoire-conversation.md](./03-memoire-conversation.md) — Gérer la mémoire des conversations
