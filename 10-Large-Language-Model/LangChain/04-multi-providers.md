# 04 — Multi-fournisseurs LLM

## Pourquoi abstraire les fournisseurs ?

L'un des atouts majeurs de LangChain est de fournir une interface unifiée pour tous les fournisseurs LLM. Quel que soit le modèle utilisé — OpenAI GPT-4o, Anthropic Claude, un modèle local via Ollama, ou Mistral — votre code LCEL reste identique.

**Avantages de l'abstraction :**
- Changer de modèle sans réécrire le code
- Comparer facilement les performances de différents modèles
- Basculer vers des modèles moins chers selon les cas d'usage
- Utiliser des modèles locaux pour les données sensibles
- Tester en local gratuitement avant de déployer en production

---

## Vue d'ensemble des providers

```
┌─────────────────────────────────────────────────────┐
│                    Votre code LCEL                  │
│          chain = prompt | llm | parser              │
└─────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
     ChatOpenAI   ChatAnthropic  ChatOllama
          │            │            │
     GPT-4o/4o-mini  Claude      Llama/Mistral
     (cloud payant)  (cloud payant) (local gratuit)
```

---

## ChatOpenAI — OpenAI GPT

### Installation et configuration

```bash
pip install langchain-openai
```

```bash
# .env
OPENAI_API_KEY=sk-proj-...
```

### Utilisation de base

```python
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

# Modèles disponibles (mai 2024)
# gpt-4o          — plus puissant, multimodal
# gpt-4o-mini     — plus rapide et moins cher
# gpt-4-turbo     — GPT-4 optimisé
# gpt-3.5-turbo   — legacy, très économique

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,          # 0 = déterministe, 2 = très créatif
    max_tokens=1000,          # Limite de tokens en sortie
    timeout=30,               # Timeout en secondes
    max_retries=2,            # Nombre de retries automatiques
)

# Appel direct
from langchain_core.messages import HumanMessage
response = llm.invoke([HumanMessage(content="Bonjour !")])
print(response.content)
print(f"Tokens utilisés : {response.usage_metadata}")
```

### Paramètres importants

```python
# Pour des tâches déterministes (extraction, classification)
llm_deterministique = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Pour des tâches créatives (rédaction, brainstorming)
llm_creatif = ChatOpenAI(model="gpt-4o-mini", temperature=1.0)

# Pour les embeddings (vecteurs de texte)
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Multimodal — envoyer des images
from langchain_core.messages import HumanMessage

llm_vision = ChatOpenAI(model="gpt-4o")
msg = HumanMessage(content=[
    {"type": "text", "text": "Décris cette image :"},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
])
response = llm_vision.invoke([msg])
```

---

## ChatAnthropic — Claude

### Installation et configuration

```bash
pip install langchain-anthropic
```

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

### Utilisation

```python
from langchain_anthropic import ChatAnthropic

# Modèles disponibles
# claude-3-5-sonnet-20241022   — le plus équilibré (recommandé)
# claude-3-5-haiku-20241022    — rapide et économique
# claude-3-opus-20240229       — le plus puissant (mais lent et cher)

llm_claude = ChatAnthropic(
    model="claude-3-5-haiku-20241022",
    temperature=0.7,
    max_tokens=1000
)

response = llm_claude.invoke("Explique le machine learning en 2 phrases.")
print(response.content)

# Claude est particulièrement bon pour :
# - L'analyse de longs documents (200k tokens de contexte)
# - La rédaction structurée et nuancée
# - Le code et les explications techniques
# - Le respect de consignes complexes
```

### Comparaison GPT-4o vs Claude

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explique ce concept technique en termes simples : {concept}"
)

# Deux chaînes avec des modèles différents
chain_gpt = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
chain_claude = prompt | ChatAnthropic(model="claude-3-5-haiku-20241022") | StrOutputParser()

concept = "le garbage collector en Python"

print("=== GPT-4o-mini ===")
print(chain_gpt.invoke({"concept": concept}))

print("\n=== Claude 3.5 Haiku ===")
print(chain_claude.invoke({"concept": concept}))
```

---

## ChatOllama — Modèles locaux

Ollama permet de faire tourner des modèles open-source localement, sans coût et sans envoyer de données à des services cloud.

### Installer Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows : télécharger depuis https://ollama.ai/

# Démarrer le serveur Ollama
ollama serve  # Lance le serveur sur localhost:11434

# Télécharger des modèles
ollama pull llama3.2           # Llama 3.2 3B (léger, ~2GB)
ollama pull llama3.2:8b        # Llama 3.2 8B (plus puissant, ~5GB)
ollama pull mistral             # Mistral 7B (~4GB)
ollama pull mistral-nemo        # Mistral Nemo 12B (~7GB)
ollama pull nomic-embed-text    # Pour les embeddings

# Lister les modèles installés
ollama list

# Tester en ligne de commande
ollama run llama3.2 "Bonjour, comment ça va ?"
```

### Utilisation avec LangChain

```bash
pip install langchain-ollama
```

```python
from langchain_ollama import ChatOllama

# Ollama tourne localement — pas besoin de clé API !
llm_local = ChatOllama(
    model="llama3.2",
    temperature=0.7,
    # base_url="http://localhost:11434"  # URL par défaut
)

response = llm_local.invoke("Explique le machine learning en 2 phrases.")
print(response.content)
```

### Embeddings avec Ollama

```python
from langchain_ollama import OllamaEmbeddings

embeddings_local = OllamaEmbeddings(model="nomic-embed-text")
vecteur = embeddings_local.embed_query("Qu'est-ce que LangChain ?")
print(f"Dimension du vecteur : {len(vecteur)}")  # 768
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Terminal montrant Ollama en fonctionnement : `ollama list`, puis exécution d'un script Python qui utilise ChatOllama
> **Expliquer :** Montrer d'abord `ollama list` pour voir les modèles téléchargés. Lancer le script Python avec ChatOllama et montrer que ça marche sans clé API, entièrement en local. Expliquer les cas d'usage : données sensibles, développement offline, économies sur les coûts. Comparer la vitesse de réponse avec OpenAI.

---

## Pattern d'abstraction avec .env

Le pattern le plus propre pour gérer les providers consiste à utiliser une variable d'environnement pour sélectionner le provider et le modèle.

### Configuration .env

```bash
# .env — changer ces valeurs pour switcher de provider

# Option 1 : OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...

# Option 2 : Anthropic
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-5-haiku-20241022
# ANTHROPIC_API_KEY=sk-ant-...

# Option 3 : Ollama (local, gratuit)
# LLM_PROVIDER=ollama
# LLM_MODEL=llama3.2
```

### Factory function

```python
# llm_factory.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.language_models import BaseChatModel

def get_llm(
    provider: str = None,
    model: str = None,
    temperature: float = 0.7,
    **kwargs
) -> BaseChatModel:
    """
    Factory pour créer un LLM selon la configuration.
    Par défaut, lit LLM_PROVIDER et LLM_MODEL depuis .env
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, temperature=temperature, **kwargs)

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, temperature=temperature, **kwargs)

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, temperature=temperature, **kwargs)

    else:
        raise ValueError(f"Provider inconnu : {provider}. Choisir parmi : openai, anthropic, ollama")


# Utilisation
llm = get_llm()  # Utilise la config du .env
# ou
llm = get_llm(provider="ollama", model="mistral")  # Override explicite
```

### Application avec factory

```python
# app.py — code indépendant du provider
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_factory import get_llm

# Le LLM est créé depuis la config — zero changement de code nécessaire
llm = get_llm()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un expert en Python. Réponds de façon concise."),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()

# Cette chaîne fonctionne avec n'importe quel provider !
reponse = chain.invoke({"question": "Quelle est la différence entre list et tuple ?"})
print(reponse)
```

---

> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration du switch de provider via .env : modifier la variable LLM_PROVIDER de "openai" à "ollama" et relancer le script sans changer une ligne de code
> **Expliquer :** Ouvrir le fichier .env dans l'éditeur. Commenter la ligne OpenAI et décommenter la ligne Ollama. Relancer `python app.py` et montrer que le résultat arrive depuis un modèle différent, sans aucun changement dans app.py. C'est la puissance de l'abstraction LangChain.

---

## Benchmarking des providers

```python
# benchmark.py — Comparer vitesse et qualité entre providers
import time
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

QUESTION = "Explique la différence entre supervised et unsupervised learning en 3 phrases."

providers = {
    "GPT-4o-mini": ChatOpenAI(model="gpt-4o-mini", temperature=0),
    "Claude Haiku": ChatAnthropic(model="claude-3-5-haiku-20241022", temperature=0),
    "Llama 3.2 (local)": ChatOllama(model="llama3.2", temperature=0),
}

prompt = ChatPromptTemplate.from_template("{question}")

for nom, llm in providers.items():
    chain = prompt | llm | StrOutputParser()
    debut = time.time()
    try:
        reponse = chain.invoke({"question": QUESTION})
        duree = time.time() - debut
        print(f"\n{'='*50}")
        print(f"Provider : {nom} ({duree:.2f}s)")
        print(f"Réponse : {reponse[:200]}...")
    except Exception as e:
        print(f"Provider {nom} : ERREUR - {e}")
```

---

## Mistral AI

```bash
pip install langchain-mistralai
```

```bash
# .env
MISTRAL_API_KEY=...
```

```python
from langchain_mistralai import ChatMistralAI

llm_mistral = ChatMistralAI(
    model="mistral-small-latest",   # ou mistral-large-latest
    temperature=0.7
)

# Intégration identique dans les chaînes LCEL
chain = prompt | llm_mistral | StrOutputParser()
```

---

## Google Gemini

```bash
pip install langchain-google-genai
```

```bash
# .env
GOOGLE_API_KEY=...
```

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7
)
```

---

## Tableau comparatif des providers

| Provider | Modèles | Contexte | Avantages | Inconvénients |
|----------|---------|----------|-----------|---------------|
| OpenAI | GPT-4o, GPT-4o-mini | 128k tokens | Qualité top, multimodal, outils natifs | Coût, données envoyées hors UE |
| Anthropic | Claude 3.5 Sonnet/Haiku | 200k tokens | Très long contexte, nuancé, sûr | Plus cher que GPT-4o-mini |
| Ollama (local) | Llama, Mistral, etc. | Dépend du modèle | Gratuit, privé, offline | Plus lent, qualité moindre |
| Mistral | Mistral Small/Large | 128k tokens | Bon rapport qualité/prix, EU | Moins d'intégrations |
| Google Gemini | Gemini Flash/Pro | 1M tokens | Contexte énorme, multimodal | Ecosystem moins mature |

---

## Bonnes pratiques

### Séparer les modèles par usage

```python
# config.py — assigner les bons modèles aux bons usages
from llm_factory import get_llm

# Pour du code : modèle fort
llm_code = get_llm(provider="openai", model="gpt-4o", temperature=0)

# Pour des résumés : modèle économique
llm_resume = get_llm(provider="openai", model="gpt-4o-mini", temperature=0)

# Pour de l'analyse créative : Claude
llm_analyse = get_llm(provider="anthropic", model="claude-3-5-sonnet-20241022", temperature=0.5)

# Pour les tests en développement : local
llm_dev = get_llm(provider="ollama", model="llama3.2", temperature=0)
```

### Circuit breaker avec fallbacks

```python
# Si OpenAI est indisponible, basculer sur Anthropic, puis Ollama
llm_principal = ChatOpenAI(model="gpt-4o-mini")
llm_backup_1 = ChatAnthropic(model="claude-3-5-haiku-20241022")
llm_backup_2 = ChatOllama(model="llama3.2")

llm_robuste = llm_principal.with_fallbacks([llm_backup_1, llm_backup_2])

chain = prompt | llm_robuste | StrOutputParser()
# Si OpenAI échoue → essaie Anthropic → essaie Ollama
```

---

## Récapitulatif

| Import | Package | API Key |
|--------|---------|---------|
| `ChatOpenAI` | `langchain-openai` | `OPENAI_API_KEY` |
| `ChatAnthropic` | `langchain-anthropic` | `ANTHROPIC_API_KEY` |
| `ChatOllama` | `langchain-ollama` | Aucune (local) |
| `ChatMistralAI` | `langchain-mistralai` | `MISTRAL_API_KEY` |
| `ChatGoogleGenerativeAI` | `langchain-google-genai` | `GOOGLE_API_KEY` |

La suite : [05-agents-tools.md](./05-agents-tools.md) — Agents et outils LangChain
