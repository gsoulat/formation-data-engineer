# Azure AI Services — Cognitive Services, API Keys et Endpoints

## Introduction

**Azure AI Services** (anciennement Azure Cognitive Services) est la porte d'entrée vers les capacités IA de Microsoft Azure. Il s'agit d'un ensemble de services REST accessibles via des clés d'API, sans nécessiter de compétences en machine learning.

L'idée centrale : Microsoft a entraîné des modèles sur des milliards de données. Vous les consommez via une simple requête HTTP, et vous payez à l'usage.

---

## Créer une ressource Azure AI Services

### Via le portail Azure

La création d'une ressource Azure AI Services se fait en quelques clics depuis le portail.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Naviguer dans le portail Azure → "Créer une ressource" → rechercher "Azure AI Services" → remplir le formulaire (nom, région France Central, pricing tier F0) → bouton Créer.
> **Expliquer :** Insister sur le choix de la région (France Central pour RGPD), la différence entre le tier F0 (gratuit, limité) et S0 (production). Montrer la page de validation et le déploiement en cours.
---

**Étapes résumées :**

1. Connectez-vous au portail Azure : [https://portal.azure.com](https://portal.azure.com)
2. Cliquez sur **"Créer une ressource"**
3. Recherchez **"Azure AI Services"** (multi-service) ou un service spécifique
4. Remplissez le formulaire :
   - **Abonnement** : votre abonnement Azure
   - **Groupe de ressources** : créez-en un nouveau ou utilisez un existant
   - **Région** : `France Central` (recommandé pour RGPD)
   - **Nom** : nom unique (ex: `mon-projet-ai-services`)
   - **Niveau tarifaire** : `F0` (gratuit) pour les tests, `S0` pour la production
5. Validez et attendez le déploiement (~1 minute)

### Via Azure CLI

```bash
# Connexion à Azure
az login

# Créer un groupe de ressources si nécessaire
az group create \
  --name rg-formation-ai \
  --location francecentral

# Créer une ressource Azure AI Services (multi-service)
az cognitiveservices account create \
  --name mon-ai-services \
  --resource-group rg-formation-ai \
  --kind CognitiveServices \
  --sku S0 \
  --location francecentral \
  --yes

# Récupérer les clés
az cognitiveservices account keys list \
  --name mon-ai-services \
  --resource-group rg-formation-ai
```

---

## Récupérer les clés API et l'endpoint

Après la création, vous avez besoin de deux informations pour appeler les APIs :

1. **L'endpoint** : URL de base de votre ressource
2. **La clé API** : clé d'authentification (deux clés disponibles pour rotation)

### Depuis le portail

Accédez à votre ressource → section **"Clés et point de terminaison"** dans le menu gauche.

Vous verrez :
- `KEY 1` et `KEY 2` (deux clés identiques pour permettre la rotation sans interruption)
- `Endpoint` : URL du type `https://mon-projet-ai-services.cognitiveservices.azure.com/`
- `Emplacement/Région` : confirme la région choisie

### Bonnes pratiques de gestion des clés

```python
# MAUVAISE PRATIQUE : clé en dur dans le code
client = AzureClient(api_key="abc123...")  # Ne jamais faire ça !

# BONNE PRATIQUE 1 : variables d'environnement
import os
api_key = os.environ["AZURE_AI_KEY"]
endpoint = os.environ["AZURE_AI_ENDPOINT"]

# BONNE PRATIQUE 2 : Azure Key Vault (production)
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
kv_client = SecretClient(vault_url="https://mon-keyvault.vault.azure.net/", credential=credential)
api_key = kv_client.get_secret("azure-ai-key").value
```

### Fichier `.env` pour le développement local

```bash
# .env (à ajouter dans .gitignore !)
AZURE_AI_KEY=votre_cle_ici
AZURE_AI_ENDPOINT=https://mon-projet-ai-services.cognitiveservices.azure.com/
AZURE_REGION=francecentral
```

```python
# Chargement avec python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_KEY = os.getenv("AZURE_AI_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
```

---

## Structure des endpoints Azure AI Services

### Pattern général

Les URLs d'Azure AI Services suivent un pattern cohérent :

```
https://{nom-ressource}.cognitiveservices.azure.com/{service}/{version}/{operation}
```

Exemples :

```
# Text Analytics (analyse de sentiment)
https://mon-ai.cognitiveservices.azure.com/text/analytics/v3.1/sentiment

# Computer Vision (OCR)
https://mon-ai.cognitiveservices.azure.com/vision/v3.2/read/analyze

# Translator
https://api.cognitive.microsofttranslator.com/translate?api-version=3.0
```

> Note : Le service Translator utilise un endpoint global différent. Consultez toujours la documentation officielle pour chaque service.

---

## Premier appel API — Text Analytics

Pour illustrer le fonctionnement général, voici un exemple complet avec le service d'analyse de texte.

### Installation du SDK

```bash
pip install azure-ai-textanalytics
```

### Exemple : analyse de sentiment

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

# Configuration
endpoint = os.environ["AZURE_AI_ENDPOINT"]
key = os.environ["AZURE_AI_KEY"]

# Création du client
credential = AzureKeyCredential(key)
client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

# Textes à analyser
documents = [
    "Ce service Azure est vraiment impressionnant, j'adore la facilité d'intégration !",
    "La documentation est parfois difficile à suivre, mais les exemples aident.",
    "Catastrophique, ça ne fonctionne pas du tout, perte de temps.",
]

# Appel API
response = client.analyze_sentiment(documents=documents, language="fr")

# Traitement des résultats
for i, doc in enumerate(response):
    if not doc.is_error:
        print(f"\nDocument {i+1}:")
        print(f"  Sentiment global : {doc.sentiment}")
        print(f"  Scores : positif={doc.confidence_scores.positive:.2f}, "
              f"neutre={doc.confidence_scores.neutral:.2f}, "
              f"négatif={doc.confidence_scores.negative:.2f}")
        for sentence in doc.sentences:
            print(f"  Phrase : '{sentence.text[:50]}...'")
            print(f"    Sentiment : {sentence.sentiment}")
    else:
        print(f"Erreur sur le document {i+1}: {doc.error}")
```

### Exemple : détection de langue

```python
# Détection automatique de langue
documents_multilingues = [
    "Bonjour, comment allez-vous ?",
    "Hello, how are you?",
    "Hola, ¿cómo estás?",
    "Guten Tag, wie geht es Ihnen?",
]

response = client.detect_language(documents=documents_multilingues)

for i, doc in enumerate(response):
    if not doc.is_error:
        lang = doc.primary_language
        print(f"Texte {i+1}: {lang.name} ({lang.iso6391_name}) - confiance: {lang.confidence_score:.2f}")
```

### Exemple : extraction d'entités nommées (NER)

```python
# NER : extraction de noms, lieux, organisations, dates...
texts = [
    "Microsoft Azure a été lancé en 2010 par Satya Nadella depuis Redmond, Washington.",
    "La réunion avec Air France se tient le 15 mars 2025 à Paris.",
]

response = client.recognize_entities(documents=texts, language="fr")

for i, doc in enumerate(response):
    print(f"\nDocument {i+1}:")
    for entity in doc.entities:
        print(f"  {entity.text:30s} | Catégorie: {entity.category:20s} | Confiance: {entity.confidence_score:.2f}")
```

---

## Appels directs via l'API REST (sans SDK)

Vous pouvez aussi appeler les APIs directement avec `requests` :

```python
import requests
import json
import os

endpoint = os.environ["AZURE_AI_ENDPOINT"]
key = os.environ["AZURE_AI_KEY"]

# Headers communs à tous les appels Azure AI Services
headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/json"
}

# Exemple : traduction de texte
translate_url = "https://api.cognitive.microsofttranslator.com/translate"
params = {
    "api-version": "3.0",
    "from": "fr",
    "to": ["en", "es", "de"]
}
body = [{"text": "Bonjour, comment puis-je vous aider aujourd'hui ?"}]

response = requests.post(translate_url, headers=headers, params=params, json=body)
translations = response.json()

for result in translations:
    for translation in result["translations"]:
        print(f"{translation['to']}: {translation['text']}")
```

---

## Gestion des erreurs et retry

Les APIs Azure AI Services retournent des codes HTTP standard. Il est important de gérer correctement les erreurs.

```python
import time
from azure.core.exceptions import HttpResponseError, ServiceRequestError

def call_with_retry(client_func, *args, max_retries=3, **kwargs):
    """Wrapper générique avec retry exponentiel."""
    for attempt in range(max_retries):
        try:
            return client_func(*args, **kwargs)
        except HttpResponseError as e:
            if e.status_code == 429:
                # Rate limit atteint
                retry_after = int(e.response.headers.get("Retry-After", 60))
                print(f"Rate limit atteint. Attente {retry_after}s...")
                time.sleep(retry_after)
            elif e.status_code == 401:
                raise ValueError("Clé API invalide ou expirée") from e
            elif e.status_code >= 500:
                wait = 2 ** attempt
                print(f"Erreur serveur Azure (tentative {attempt+1}/{max_retries}). Attente {wait}s...")
                time.sleep(wait)
            else:
                raise
        except ServiceRequestError as e:
            print(f"Erreur réseau: {e}. Tentative {attempt+1}/{max_retries}")
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Échec après {max_retries} tentatives")
```

---

## Quotas et limites

Chaque service a ses propres limites. Voici les limites courantes :

| Service | Tier F0 (gratuit) | Tier S0 (standard) |
|---------|-------------------|---------------------|
| Text Analytics | 5 000 transactions/mois | 1 000 TPS |
| Computer Vision | 5 000 transactions/mois | 10 TPS |
| Document Intelligence | 500 pages/mois | 15 pages/sec |
| Translator | 2 M caractères/mois | Illimité (facturation) |

> Pour la production, configurez des alertes de coût dans Azure Cost Management.

---

## Ressources officielles

- Documentation Azure AI Services : [https://docs.microsoft.com/azure/cognitive-services/](https://docs.microsoft.com/azure/cognitive-services/)
- Pricing calculator : [https://azure.microsoft.com/pricing/calculator/](https://azure.microsoft.com/pricing/calculator/)
- Azure AI Studio (interface no-code) : [https://ai.azure.com](https://ai.azure.com)
- SDK Python Azure AI : [https://pypi.org/project/azure-ai-textanalytics/](https://pypi.org/project/azure-ai-textanalytics/)
