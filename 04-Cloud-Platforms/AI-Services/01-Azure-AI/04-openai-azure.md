# Azure OpenAI Service — Déploiements, API et IA Responsable

## Introduction

**Azure OpenAI Service** est l'accès enterprise aux modèles OpenAI (GPT-4, DALL-E, Whisper, etc.) hébergé et opéré par Microsoft Azure. Contrairement à l'API OpenAI directe, Azure OpenAI offre :

- Hébergement dans des datacenters Azure (régions européennes disponibles)
- SLA Microsoft (99,9% uptime)
- Intégration avec Azure Active Directory, Key Vault, Private Link
- Conformité RGPD et engagements de non-utilisation des données pour l'entraînement
- Filtres de contenu configurables (Responsible AI)
- Accès aux modèles les plus récents via accès anticipé pour les clients enterprise

---

## Modèles disponibles

| Modèle | Type | Usage principal |
|--------|------|----------------|
| `gpt-4o` | Chat completion | Assistant polyvalent, analyse complexe, code |
| `gpt-4o-mini` | Chat completion | Tâches simples, rapport qualité/prix optimal |
| `gpt-4-turbo` | Chat completion | Contexte long (128K tokens), vision |
| `text-embedding-ada-002` | Embedding | RAG, recherche sémantique (legacy) |
| `text-embedding-3-small` | Embedding | Embeddings rapides et économiques |
| `text-embedding-3-large` | Embedding | Embeddings haute qualité |
| `dall-e-3` | Image generation | Génération d'images depuis du texte |
| `whisper` | Speech to text | Transcription audio |

---

## Différences : API OpenAI directe vs Azure OpenAI

| Critère | OpenAI API | Azure OpenAI |
|---------|------------|-------------|
| **Endpoint** | `https://api.openai.com/v1/` | `https://{resource}.openai.azure.com/` |
| **Authentification** | `Bearer {api_key}` | `api-key: {key}` ou Azure AD |
| **Versioning** | Implicite | Explicite `api-version=2024-02-01` |
| **Déploiement** | Direct par nom de modèle | Via "deployments" nommés |
| **Hébergement** | US uniquement | Choix de région (dont Europe) |
| **RGPD** | Données traitées aux US | Données en Europe si région EU |
| **Accès** | Immédiat (CB) | Sur demande / validation Microsoft |
| **Prix** | Prix OpenAI standard | Prix Azure (similaire ou légèrement supérieur) |

---

## Créer et configurer la ressource Azure OpenAI

### Prérequis

L'accès à Azure OpenAI nécessite une validation. Si vous n'avez pas encore accès :
1. Aller sur [https://aka.ms/oaiapply](https://aka.ms/oaiapply)
2. Remplir le formulaire de demande d'accès
3. Attendre l'approbation (quelques jours à quelques semaines)

### Création de la ressource

```bash
# Créer la ressource Azure OpenAI
az cognitiveservices account create \
  --name mon-azure-openai \
  --resource-group rg-formation-ai \
  --kind OpenAI \
  --sku S0 \
  --location francecentral
```

### Créer un déploiement

Un **déploiement** (deployment) est une instance d'un modèle que vous avez activée dans votre ressource. Vous devez créer un déploiement avant de pouvoir appeler le modèle.

```bash
# Déployer gpt-4o-mini
az cognitiveservices account deployment create \
  --name mon-azure-openai \
  --resource-group rg-formation-ai \
  --deployment-name gpt-4o-mini-deploy \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \  # 10K tokens par minute
  --sku-name Standard
```

---

## Installation et premier appel

```bash
pip install openai  # Le SDK OpenAI fonctionne avec Azure OpenAI
```

```python
from openai import AzureOpenAI
import os

# Initialisation du client Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

# Premier appel — Chat completion
response = client.chat.completions.create(
    model="gpt-4o-mini-deploy",  # Nom du déploiement, pas du modèle
    messages=[
        {"role": "system", "content": "Tu es un assistant expert en data engineering."},
        {"role": "user", "content": "Explique la différence entre ETL et ELT en 3 phrases."}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)
print(f"\nTokens utilisés : {response.usage.total_tokens}")
```

---

## Authentification via Azure Active Directory (recommandé en production)

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# Authentification sans clé API — utilise les identités Azure (Managed Identity, etc.)
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01"
)
```

---

## Exemples avancés

### Streaming des réponses

```python
def chat_stream(prompt: str, deployment: str = "gpt-4o-mini-deploy") -> None:
    """
    Affiche la réponse en streaming (token par token).
    Améliore la perception de rapidité dans les interfaces utilisateur.
    """
    stream = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # Saut de ligne final


chat_stream("Écris un haïku sur le cloud computing.")
```

### Analyse d'images avec GPT-4o Vision

```python
import base64

def analyze_image_with_gpt4o(image_path: str, question: str) -> str:
    """
    Analyse une image en posant une question en langage naturel.
    Nécessite un déploiement gpt-4o ou gpt-4-turbo.
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Détecter le type MIME selon l'extension
    ext = image_path.split(".")[-1].lower()
    mime_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif"}
    mime_type = mime_types.get(ext, "image/jpeg")

    response = client.chat.completions.create(
        model="gpt-4o-deploy",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}",
                            "detail": "high"  # "low" pour économiser des tokens
                        }
                    },
                    {"type": "text", "text": question}
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content


# Analyser une facture avec GPT-4o
answer = analyze_image_with_gpt4o(
    "./documents/facture.png",
    "Extrais le numéro de facture, la date, le montant total TTC et le nom du fournisseur. "
    "Réponds en JSON structuré."
)
print(answer)
```

### Génération d'embeddings

```python
def create_embeddings(texts: list[str], model: str = "text-embedding-3-small-deploy") -> list[list[float]]:
    """
    Génère des embeddings vectoriels pour une liste de textes.
    Utilisé pour la recherche sémantique et le RAG.
    """
    response = client.embeddings.create(
        input=texts,
        model=model
    )

    return [item.embedding for item in response.data]


# Exemple : comparer la similarité entre des textes
import numpy as np

def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    a, b = np.array(v1), np.array(v2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


texts = [
    "Azure OpenAI Service est une API cloud pour les modèles GPT.",
    "Les LLM sont des modèles de langage entraînés sur de grandes quantités de texte.",
    "La météo à Paris est souvent nuageuse en hiver.",
]

embeddings = create_embeddings(texts)

# Calculer les similarités 2 à 2
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"Similarité entre texte {i+1} et texte {j+1}: {sim:.4f}")
```

### Function calling (tool use)

```python
import json

# Définir des fonctions que le modèle peut appeler
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Obtenir la météo actuelle pour une ville",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Le nom de la ville (ex: Paris, Lyon)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Unité de température"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Appel avec tool use
response = client.chat.completions.create(
    model="gpt-4o-mini-deploy",
    messages=[{"role": "user", "content": "Quel temps fait-il à Paris et à Lyon ?"}],
    tools=tools,
    tool_choice="auto"
)

# Vérifier si le modèle veut appeler une fonction
if response.choices[0].finish_reason == "tool_calls":
    tool_calls = response.choices[0].message.tool_calls
    for call in tool_calls:
        print(f"Fonction demandée : {call.function.name}")
        args = json.loads(call.function.arguments)
        print(f"Arguments : {args}")
        # Ici vous exécuteriez la vraie fonction get_weather(args["city"])
```

---

## IA Responsable (Responsible AI)

Azure OpenAI intègre des filtres de contenu automatiques, configurables dans le portail.

### Catégories de filtre

| Catégorie | Description |
|-----------|-------------|
| **Hate** | Discours de haine, discrimination |
| **Violence** | Contenu violent, menaces |
| **Sexual** | Contenu sexuel explicite |
| **Self-harm** | Automutilation, suicide |
| **Jailbreak** | Tentatives de contournement des guardrails |
| **Indirect attack** | Prompt injection via documents |

### Niveaux de filtrage

- `Low` : tolère le contenu borderline
- `Medium` : équilibre (défaut)
- `High` : très strict, peut bloquer du contenu légitime

### Gérer les refus dans le code

```python
from openai import BadRequestError

def safe_chat(prompt: str) -> str | None:
    """
    Appel avec gestion explicite des refus de contenu.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-deploy",
            messages=[{"role": "user", "content": prompt}]
        )

        # Vérifier le finish_reason
        choice = response.choices[0]
        if choice.finish_reason == "content_filter":
            print("Le contenu a été filtré par les politiques Azure OpenAI.")
            return None

        return choice.message.content

    except BadRequestError as e:
        if e.code == "content_filter":
            print(f"Prompt refusé par le filtre de contenu : {e.message}")
            return None
        raise
```

### Monitoring des filtres dans Azure

Vous pouvez monitorer les déclenchements de filtres dans :
- Azure Monitor → Logs → `AzureOpenAIFilteredRequests`
- Azure AI Studio → Content Filters → Métriques

---

## Bonnes pratiques de déploiement

### Gestion des quotas et du débit

```python
import time
from openai import RateLimitError

def call_with_backoff(prompt: str, max_retries: int = 5) -> str:
    """
    Appel avec retry exponentiel pour gérer les dépassements de quota (429).
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini-deploy",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + 1
            print(f"Rate limit atteint. Attente {wait_time}s (tentative {attempt+1}/{max_retries})...")
            time.sleep(wait_time)
```

### Estimation des coûts avant production

```python
import tiktoken

def estimate_cost(prompt: str, response_tokens_estimate: int = 500,
                  model: str = "gpt-4o-mini") -> dict:
    """
    Estime le coût d'un appel avant de l'effectuer.
    """
    # Encodeur pour compter les tokens (approximatif pour Azure OpenAI)
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    input_tokens = len(enc.encode(prompt))

    # Prix approximatifs (vérifier les prix actuels Azure)
    prices = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},   # per 1K tokens
        "gpt-4o": {"input": 0.005, "output": 0.015},
    }

    price = prices.get(model, prices["gpt-4o-mini"])
    cost_input = (input_tokens / 1000) * price["input"]
    cost_output = (response_tokens_estimate / 1000) * price["output"]

    return {
        "input_tokens": input_tokens,
        "estimated_output_tokens": response_tokens_estimate,
        "estimated_cost_usd": round(cost_input + cost_output, 6)
    }


# Avant d'envoyer un gros batch
prompt_exemple = "Résume ce document de 5000 mots en 3 bullet points..." + " " * 5000
estimate = estimate_cost(prompt_exemple)
print(f"Tokens d'entrée : {estimate['input_tokens']}")
print(f"Coût estimé : ${estimate['estimated_cost_usd']}")
```

---

## Ressources officielles

- Documentation Azure OpenAI : [https://learn.microsoft.com/azure/ai-services/openai/](https://learn.microsoft.com/azure/ai-services/openai/)
- Azure AI Studio : [https://ai.azure.com](https://ai.azure.com)
- Quotas et limites : [https://learn.microsoft.com/azure/ai-services/openai/quotas-limits](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits)
- Responsible AI overview : [https://learn.microsoft.com/azure/ai-services/openai/concepts/responsible-ai-overview](https://learn.microsoft.com/azure/ai-services/openai/concepts/responsible-ai-overview)
- Comparaison Azure OpenAI vs OpenAI API : [https://learn.microsoft.com/azure/ai-services/openai/overview#comparing-azure-openai-and-openai](https://learn.microsoft.com/azure/ai-services/openai/overview#comparing-azure-openai-and-openai)
