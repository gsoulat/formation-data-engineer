# AWS AI — Vue d'ensemble

## Qu'est-ce que AWS AI ?

Amazon Web Services propose un catalogue de services d'intelligence artificielle parmi les plus larges du marché. Contrairement à Azure qui regroupe ses services sous la bannière "Azure AI Services", AWS distribue ses services IA sous des noms distincts, chacun étant un produit indépendant.

L'avantage de l'approche AWS est la maturité et la profondeur de chaque service. Les services d'IA AWS s'intègrent nativement avec l'écosystème AWS (S3, Lambda, SQS, Kinesis, etc.), ce qui les rend particulièrement efficaces dans une architecture cloud-native AWS.

---

## Services couverts dans ce module

| Fichier | Service | Usage principal |
|---------|---------|----------------|
| `01-aws-ai-overview.md` | Vue d'ensemble | Architecture, IAM, SDK boto3 |
| `02-textract.md` | Amazon Textract | Extraction de texte et données structurées depuis des documents |
| `03-rekognition.md` | Amazon Rekognition | Analyse d'images et de vidéos |
| `04-bedrock.md` | Amazon Bedrock | Accès aux modèles fondationnels (Claude, Llama, Titan...) |

---

## Catalogue complet des services AWS AI

```
AWS AI/ML Services
├── Vision
│   ├── Amazon Rekognition       ← Analyse d'images/vidéo
│   └── Amazon Textract          ← OCR + extraction de formulaires/tables
├── Langage
│   ├── Amazon Comprehend        ← NLP : sentiment, entités, topics
│   ├── Amazon Translate         ← Traduction automatique
│   ├── Amazon Transcribe        ← Speech to Text
│   └── Amazon Polly             ← Text to Speech
├── Recherche & Recommandation
│   ├── Amazon Kendra            ← Moteur de recherche IA sur documents
│   └── Amazon Personalize       ← Recommandations personnalisées
├── Modèles fondationnels
│   └── Amazon Bedrock           ← Accès Claude, Llama, Titan, etc.
└── ML Platform
    └── Amazon SageMaker         ← Entraînement et déploiement de modèles
```

---

## Régions disponibles en Europe

| Région AWS | Localisation | Code |
|------------|-------------|------|
| EU (Irlande) | Dublin | `eu-west-1` |
| EU (Londres) | Londres | `eu-west-2` |
| EU (Paris) | Paris | `eu-west-3` |
| EU (Francfort) | Francfort | `eu-central-1` |
| EU (Stockholm) | Stockholm | `eu-north-1` |

> Note : Certains services AWS AI ne sont disponibles qu'en `us-east-1`. Vérifiez la disponibilité régionale avant de choisir votre architecture.

---

## Pour commencer

1. [01-aws-ai-overview.md](./01-aws-ai-overview.md) — Setup IAM, boto3, premiers appels
2. [02-textract.md](./02-textract.md) — Extraction documentaire avec Textract
3. [03-rekognition.md](./03-rekognition.md) — Vision par ordinateur avec Rekognition
4. [04-bedrock.md](./04-bedrock.md) — LLMs avec Amazon Bedrock
