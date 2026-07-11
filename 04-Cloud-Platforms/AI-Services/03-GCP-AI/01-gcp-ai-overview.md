# GCP AI — Vertex AI et Vue d'ensemble des services Google AI

## Introduction

Google Cloud Platform a structuré son offre IA autour de **Vertex AI**, une plateforme unifiée lancée en 2021 pour regrouper les outils de machine learning et les services IA sous une même interface. Avant Vertex AI, Google proposait des services épars (AI Platform, AutoML, Natural Language API...) ; Vertex les consolide.

Deux niveaux d'utilisation :
- **APIs prêtes à l'emploi** : appels simples via REST ou SDK, pas de ML requis
- **Vertex AI** : pour l'entraînement, le déploiement et l'accès aux grands modèles (Gemini)

---

## Prérequis : Créer un projet GCP et activer les APIs

### Étapes initiales

1. Créer un compte Google Cloud : [https://cloud.google.com](https://cloud.google.com)
2. Créer un nouveau projet dans la console
3. Activer la facturation (nécessaire même pour les tiers gratuits)
4. Activer les APIs nécessaires

```bash
# Via gcloud CLI

# Installer gcloud SDK
# https://cloud.google.com/sdk/docs/install

# Connexion
gcloud auth login

# Configurer le projet
gcloud config set project MON_PROJET_ID

# Activer les APIs
gcloud services enable vision.googleapis.com
gcloud services enable documentai.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable translate.googleapis.com
gcloud services enable language.googleapis.com
```

---

## Authentification GCP

GCP propose plusieurs méthodes d'authentification selon l'environnement :

### Application Default Credentials (ADC) — Recommandé

```bash
# Authentification locale pour le développement
gcloud auth application-default login

# Les credentials sont stockés dans :
# ~/.config/gcloud/application_default_credentials.json
```

```python
# En Python, les SDK GCP utilisent ADC automatiquement
from google.cloud import vision

# Pas besoin de spécifier de credentials explicitement si ADC est configuré
client = vision.ImageAnnotatorClient()
```

### Service Account (Production)

```bash
# Créer un service account
gcloud iam service-accounts create sa-formation-ai \
  --description="Service account pour les services AI" \
  --display-name="Formation AI SA"

# Attribuer les rôles nécessaires
gcloud projects add-iam-policy-binding MON_PROJET_ID \
  --member="serviceAccount:sa-formation-ai@MON_PROJET_ID.iam.gserviceaccount.com" \
  --role="roles/vision.serviceAgent"

gcloud projects add-iam-policy-binding MON_PROJET_ID \
  --member="serviceAccount:sa-formation-ai@MON_PROJET_ID.iam.gserviceaccount.com" \
  --role="roles/documentai.viewer"

# Créer et télécharger la clé JSON
gcloud iam service-accounts keys create ./sa-key.json \
  --iam-account=sa-formation-ai@MON_PROJET_ID.iam.gserviceaccount.com
```

```python
import os
from google.oauth2 import service_account
from google.cloud import vision

# Option 1 : Variable d'environnement (recommandé)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/sa-key.json"
client = vision.ImageAnnotatorClient()  # Utilise automatiquement le fichier

# Option 2 : Credentials explicites
credentials = service_account.Credentials.from_service_account_file(
    "/path/to/sa-key.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
client = vision.ImageAnnotatorClient(credentials=credentials)
```

### Workload Identity Federation (GKE / autres clouds)

Pour les workloads sur GKE ou en cross-cloud sans clé JSON :

```bash
# Configurer Workload Identity sur GKE
gcloud container clusters update MON_CLUSTER \
  --workload-pool=MON_PROJET_ID.svc.id.goog
```

---

## Installation des SDK Python GCP

```bash
# Services spécifiques
pip install google-cloud-vision        # Cloud Vision API
pip install google-cloud-documentai    # Document AI
pip install google-cloud-language      # Natural Language API
pip install google-cloud-translate     # Translation API
pip install google-cloud-speech        # Speech-to-Text

# Vertex AI (Gemini, Embeddings, etc.)
pip install google-cloud-aiplatform vertexai
```

---

## Vertex AI — Gemini

**Gemini** est le modèle fondational multimodal de Google. Il est accessible via Vertex AI.

### Modèles Gemini disponibles

| Modèle | Forces | Contexte max | Usage recommandé |
|--------|--------|-------------|----------------|
| `gemini-1.5-pro` | Raisonnement complexe, long contexte | 2M tokens | Analyse de documents longs, code complexe |
| `gemini-1.5-flash` | Rapidité, économique | 1M tokens | Tâches courantes, traitement en masse |
| `gemini-1.0-pro` | Modèle précédent, stable | 32K tokens | Applications existantes |

### Premier appel Gemini

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialisation Vertex AI
PROJECT_ID = "mon-projet-gcp"
LOCATION = "europe-west9"  # Paris

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Charger le modèle
model = GenerativeModel("gemini-1.5-flash")

# Appel simple
response = model.generate_content(
    "Explique le concept de data lineage en data engineering en 5 lignes."
)
print(response.text)
```

### Gemini avec contexte système

```python
from vertexai.generative_models import GenerativeModel, Content, Part

model = GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=[
        "Tu es un expert en data engineering et architecture cloud.",
        "Réponds toujours en français.",
        "Fournis des exemples de code Python quand c'est pertinent."
    ]
)

chat = model.start_chat()
response = chat.send_message("Comment implémenter un pipeline CDC avec Debezium ?")
print(response.text)

# Continuer la conversation
response2 = chat.send_message("Et pour la gestion des erreurs de connexion ?")
print(response2.text)
```

### Gemini Vision (analyse d'images)

```python
from vertexai.generative_models import GenerativeModel, Part
import base64

def analyze_image_with_gemini(image_path: str, question: str) -> str:
    """
    Analyse une image avec Gemini Vision.
    """
    model = GenerativeModel("gemini-1.5-flash")

    with open(image_path, "rb") as f:
        image_data = f.read()

    # Créer la partie image
    image_part = Part.from_data(
        data=image_data,
        mime_type="image/jpeg"
    )

    response = model.generate_content([
        image_part,
        question
    ])

    return response.text


# Analyser une facture
answer = analyze_image_with_gemini(
    "./documents/facture.jpg",
    "Extrais le numéro de facture, la date, le montant total et le nom du fournisseur. "
    "Réponds en JSON."
)
print(answer)
```

---

## Embeddings avec Vertex AI

```python
from vertexai.language_models import TextEmbeddingModel

def get_vertex_embeddings(texts: list[str],
                           model_name: str = "text-embedding-005") -> list[list[float]]:
    """
    Génère des embeddings avec le modèle Google.
    text-embedding-005 : modèle actuel recommandé (768 dimensions par défaut)
    text-multilingual-embedding-002 : pour les textes multilingues
    """
    model = TextEmbeddingModel.from_pretrained(model_name)

    embeddings = model.get_embeddings(
        texts=texts,
        task_type="RETRIEVAL_DOCUMENT",  # ou RETRIEVAL_QUERY, SEMANTIC_SIMILARITY, etc.
        output_dimensionality=768
    )

    return [e.values for e in embeddings]


# Usage
documents = [
    "Vertex AI est la plateforme ML unifiée de Google Cloud.",
    "BigQuery permet d'analyser des pétaoctets de données via SQL.",
    "Cloud Run héberge des conteneurs sans gestion d'infrastructure.",
]

vectors = get_vertex_embeddings(documents)
print(f"Embeddings : {len(vectors)} vecteurs de dimension {len(vectors[0])}")
```

---

## Natural Language API — NLP basique

```python
from google.cloud import language_v2

def analyze_text_nlp(text: str) -> dict:
    """
    Analyse NLP complète : sentiment, entités, catégories.
    """
    nl_client = language_v2.LanguageServiceClient()

    document = language_v2.Document(
        content=text,
        type_=language_v2.Document.Type.PLAIN_TEXT,
        language_code="fr"
    )

    # Analyse du sentiment
    sentiment_response = nl_client.analyze_sentiment(
        request={"document": document}
    )
    sentiment = sentiment_response.document_sentiment

    # Extraction d'entités
    entities_response = nl_client.analyze_entities(
        request={"document": document}
    )

    return {
        "sentiment": {
            "score": sentiment.score,       # -1 (négatif) à +1 (positif)
            "magnitude": sentiment.magnitude # 0 à +inf : intensité
        },
        "entities": [
            {
                "name": entity.name,
                "type": language_v2.Entity.Type(entity.type_).name,
                "salience": entity.salience  # Importance dans le texte
            }
            for entity in entities_response.entities
            if entity.salience > 0.1
        ]
    }


# Test
text = "Google Cloud a présenté Gemini 1.5 Pro en mars 2024 lors du Google Next à Las Vegas."
result = analyze_text_nlp(text)
print(f"Sentiment : {result['sentiment']['score']:.2f} (magnitude: {result['sentiment']['magnitude']:.2f})")
print("Entités importantes :")
for entity in result["entities"]:
    print(f"  {entity['name']:25s} [{entity['type']:15s}] saillance: {entity['salience']:.2f}")
```

---

## Google Cloud Storage — Prérequis pour Document AI

Document AI requiert que les documents soient stockés dans Google Cloud Storage (GCS) pour les traitements en lot.

```python
from google.cloud import storage

gcs_client = storage.Client()
BUCKET_NAME = "mon-bucket-documents-ai"

def upload_to_gcs(local_path: str, gcs_path: str = None) -> str:
    """
    Upload un fichier vers GCS.
    Retourne l'URI gs:// du fichier.
    """
    from pathlib import Path

    if gcs_path is None:
        gcs_path = f"documents/{Path(local_path).name}"

    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)

    uri = f"gs://{BUCKET_NAME}/{gcs_path}"
    print(f"Uploadé : {uri}")
    return uri


def download_from_gcs(gcs_path: str, local_path: str) -> None:
    """
    Télécharge un fichier depuis GCS.
    """
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(gcs_path)
    blob.download_to_filename(local_path)
    print(f"Téléchargé : {local_path}")
```

---

## Ressources officielles

- Documentation Vertex AI : [https://cloud.google.com/vertex-ai/docs](https://cloud.google.com/vertex-ai/docs)
- Google AI Studio (Gemini en ligne) : [https://aistudio.google.com](https://aistudio.google.com)
- Pricing Calculator : [https://cloud.google.com/products/calculator](https://cloud.google.com/products/calculator)
- SDK Python Vertex AI : [https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
