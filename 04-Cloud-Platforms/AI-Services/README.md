# Services d'IA Cloud — Vue d'ensemble

## Objectifs du module

Ce module vous permet de comprendre, comparer et utiliser les principaux services d'intelligence artificielle proposés par les trois grands fournisseurs cloud : **Microsoft Azure**, **Amazon Web Services (AWS)** et **Google Cloud Platform (GCP)**.

À l'issue de ce module, vous serez capable de :

- Identifier les services d'IA disponibles sur chaque cloud et leur équivalent fonctionnel
- Choisir le bon service selon le contexte métier (extraction documentaire, vision par ordinateur, LLM)
- Consommer ces services via API Python
- Appliquer les règles RGPD et de souveraineté des données dans un contexte cloud IA
- Estimer les coûts et comparer les offres tarifaires

---

## Structure du module

```
AI-Services/
├── README.md                        ← Ce fichier
├── Azure-AI/
│   ├── README.md                    ← Vue d'ensemble Azure AI
│   ├── 01-azure-ai-services.md      ← Cognitive Services, API keys, endpoints
│   ├── 02-document-intelligence.md  ← Form Recognizer / Document Intelligence
│   ├── 03-vision.md                 ← Computer Vision, OCR, analyse d'image
│   └── 04-openai-azure.md           ← Azure OpenAI Service
├── AWS-AI/
│   ├── README.md                    ← Vue d'ensemble AWS AI
│   ├── 01-aws-ai-overview.md        ← Panorama des services AWS AI
│   ├── 02-textract.md               ← Amazon Textract
│   ├── 03-rekognition.md            ← Amazon Rekognition
│   └── 04-bedrock.md                ← Amazon Bedrock
├── GCP-AI/
│   ├── README.md                    ← Vue d'ensemble GCP AI
│   ├── 01-gcp-ai-overview.md        ← Vertex AI, panorama
│   ├── 02-document-ai.md            ← Google Document AI
│   └── 03-vision-api.md             ← Google Cloud Vision API
└── exercices/
    ├── exercice-01-comparatif.md    ← Comparatif OCR multi-cloud
    └── exercice-02-integration.md   ← Intégration Python + Docker
```

---

## Comparatif général : Azure AI vs AWS AI vs GCP AI

### Positionnement de chaque acteur

| Dimension | Azure AI | AWS AI | GCP AI |
|-----------|----------|--------|--------|
| **Point fort** | Intégration Microsoft 365, OpenAI exclusivité | Ecosystem AWS, maturité, catalogue large | Modèles Google/DeepMind, TensorFlow natif |
| **Public cible** | Entreprises Microsoft, secteur public FR | Startups cloud-native, e-commerce | Recherche, ML avancé, data-driven |
| **Modèle LLM phare** | GPT-4o via Azure OpenAI | Claude (Anthropic) via Bedrock, Llama | Gemini via Vertex AI |
| **OCR documentaire** | Document Intelligence (Form Recognizer) | Amazon Textract | Document AI |
| **Vision** | Computer Vision + Florence | Rekognition | Cloud Vision API |
| **Speech** | Azure Speech Services | Amazon Transcribe / Polly | Speech-to-Text / Text-to-Speech |
| **Traduction** | Azure Translator | Amazon Translate | Cloud Translation |

---

## Comparatif tarifaire (référence 2024-2025)

Les prix varient selon les régions, les volumes et les engagements. Les exemples ci-dessous sont indicatifs pour la région Europe.

### OCR / Extraction documentaire

| Service | Free tier | Prix par page (volume moyen) | Notes |
|---------|-----------|------------------------------|-------|
| Azure Document Intelligence | 500 pages/mois | ~0,001 $ à 0,01 $/page selon modèle | Modèles pré-entraînés vs custom |
| Amazon Textract | 1 000 pages/mois (1 an) | ~0,0015 $ à 0,05 $/page | Tables et formulaires facturés séparément |
| Google Document AI | 1 000 pages/mois (certains processeurs) | ~0,001 $ à 0,065 $/page | Prix variables selon processeur |

### LLM / Modèles de langage

| Service | Modèle | Input (1M tokens) | Output (1M tokens) |
|---------|--------|-------------------|--------------------|
| Azure OpenAI | GPT-4o | ~5 $ | ~15 $ |
| Azure OpenAI | GPT-4o mini | ~0,15 $ | ~0,60 $ |
| AWS Bedrock | Claude 3.5 Sonnet | ~3 $ | ~15 $ |
| AWS Bedrock | Llama 3.1 70B | ~0,72 $ | ~0,72 $ |
| GCP Vertex AI | Gemini 1.5 Pro | ~1,25 $ | ~5 $ |
| GCP Vertex AI | Gemini 1.5 Flash | ~0,075 $ | ~0,30 $ |

> Les prix sont susceptibles d'évoluer. Toujours vérifier les pages de tarification officielles avant tout chiffrage projet.

---

## Considérations RGPD et souveraineté

### Principes fondamentaux

Le RGPD (Règlement Général sur la Protection des Données) impose des obligations strictes dès lors que des données personnelles sont traitées. L'utilisation de services cloud IA ne déroge pas à cette règle.

**Questions clés à se poser avant d'envoyer des données à une API cloud IA :**

1. **Les données contiennent-elles des informations personnelles ?**
   - Noms, adresses, numéros de sécurité sociale, données de santé, etc.
   - Dans les documents analysés (factures, contrats, formulaires médicaux)

2. **Où sont hébergées les données ?**
   - Les trois providers ont des régions en Europe (West Europe, eu-west, europe-west)
   - Il faut explicitement choisir une région européenne dans la configuration

3. **Les données sont-elles utilisées pour entraîner les modèles ?**
   - Par défaut : **Azure** et **AWS** s'engagent à ne pas utiliser les données API pour l'entraînement
   - **GCP** : vérifier les conditions spécifiques selon le service
   - Toujours lire les Data Processing Addendum (DPA) des contrats

### Résumé par provider

| Critère RGPD | Azure | AWS | GCP |
|--------------|-------|-----|-----|
| **Régions EU disponibles** | Oui (France Central, West Europe) | Oui (eu-west-1, eu-west-3) | Oui (europe-west1, 3, 9) |
| **DPA disponible** | Oui (Microsoft DPA) | Oui (AWS DPA) | Oui (Google DPA) |
| **Certifications** | ISO 27001, SOC 2, HDS | ISO 27001, SOC 2, HDS | ISO 27001, SOC 2 |
| **No training sur données API** | Oui (par contrat) | Oui (par contrat) | Dépend du service |
| **Offre souveraine FR** | Azure France (SecNumCloud en cours) | Non (AWS GovCloud US uniquement) | Non |

### Cas particuliers : données de santé

Pour les projets impliquant des données de santé (DMP, ordonnances, imagerie médicale) :
- L'hébergement doit être confié à un **Hébergeur de Données de Santé (HDS)** certifié
- Azure possède la certification HDS pour certains services en France
- Vérifier systématiquement avant tout projet santé

### Bonnes pratiques

```python
# Avant d'envoyer des données sensibles à une API cloud IA :

# 1. Anonymiser / pseudonymiser si possible
import re

def anonymize_text(text: str) -> str:
    """Remplace les patterns courants de données personnelles."""
    # Numéros de sécurité sociale français
    text = re.sub(r'\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b', '[NSS]', text)
    # Emails
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Numéros de téléphone français
    text = re.sub(r'\b0[1-9](\s?\d{2}){4}\b', '[TEL]', text)
    return text

# 2. Utiliser une région européenne
AZURE_ENDPOINT = "https://monservice.cognitiveservices.azure.com/"  # région choisie à la création
AWS_REGION = "eu-west-3"   # Paris
GCP_LOCATION = "europe-west1"  # Belgique

# 3. Logger les appels API pour audit RGPD
import logging
logger = logging.getLogger("cloud_ai_audit")
logger.info(f"Appel API OCR - document_id={doc_id} - region=EU - données_perso=False")
```

---

## Comment choisir le bon provider ?

### Arbre de décision

```
Vous avez déjà un contrat Microsoft / Azure ?
├── OUI → Commencer par Azure AI (facturation unifiée, support)
└── NON → Continuer...

Votre infrastructure est sur AWS ?
├── OUI → AWS AI (IAM natif, VPC, pas d'egress cross-cloud)
└── NON → Continuer...

Besoin de modèles Google (Gemini, PaLM) ou intégration GCP ?
├── OUI → Vertex AI / GCP AI
└── NON → Comparer les prix et les features spécifiques au use case
```

### Par use case

| Use case | Recommandation | Raison |
|----------|---------------|--------|
| Extraction de factures PDF | Azure Document Intelligence | Modèle Invoice pré-entraîné, excellent sur documents FR |
| Analyse de vidéo surveillance | AWS Rekognition | Maturité, intégration Kinesis Video |
| Chatbot d'entreprise avec GPT | Azure OpenAI | Accès GPT-4 en environnement enterprise, SLA |
| Classification d'images e-commerce | GCP Vision API | AutoML Vision facile à utiliser |
| RAG sur documents internes | AWS Bedrock (Knowledge Bases) | Intégration native S3, Kendra |
| Fine-tuning de modèle custom | Vertex AI | Pipelines ML, Kubeflow intégré |

---

## Prérequis techniques

Avant de commencer les travaux pratiques, assurez-vous d'avoir :

- Python 3.10+
- Un compte sur au moins un des trois providers (Azure, AWS, GCP)
- Les SDK Python installés selon le provider utilisé
- Docker (pour les exercices d'intégration)

```bash
# Installation des SDK
pip install azure-ai-documentintelligence azure-cognitiveservices-vision-computervision openai
pip install boto3 amazon-textract-response-parser
pip install google-cloud-vision google-cloud-documentai vertexai
```

---

## Navigation du module

1. Commencez par le provider que vous utilisez en priorité dans votre contexte professionnel
2. Faites au moins un provider en entier (README + tous les fichiers) avant de comparer
3. Réalisez l'exercice comparatif (exercice-01) après avoir vu au moins deux providers
4. L'exercice d'intégration (exercice-02) peut être réalisé avec le provider de votre choix
