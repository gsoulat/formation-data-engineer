# GCP AI — Vue d'ensemble

## Qu'est-ce que GCP AI ?

Google Cloud Platform propose ses services d'IA sous deux formes :

1. **APIs pré-entraînées** (Vision API, Natural Language API, Translation API, etc.) : accessibles directement via API REST, sans configuration ML
2. **Vertex AI** : plateforme ML unifiée pour entraîner, déployer et appeler des modèles (y compris Gemini)

Google est historiquement à l'origine de nombreuses avancées en IA (TensorFlow, Transformer architecture, BERT, PaLM, Gemini). Les services cloud GCP bénéficient directement de ces recherches.

---

## Services couverts dans ce module

| Fichier | Service | Usage principal |
|---------|---------|----------------|
| `01-gcp-ai-overview.md` | Vue d'ensemble | Architecture, authentification, SDK Python |
| `02-document-ai.md` | Google Document AI | Extraction documentaire structurée |
| `03-vision-api.md` | Cloud Vision API | OCR, analyse d'images, détection d'objets |

---

## Architecture GCP AI

```
GCP AI Services
├── APIs pré-entraînées (simples)
│   ├── Cloud Vision API          ← Analyse d'images, OCR
│   ├── Cloud Natural Language    ← NLP : sentiment, entités, syntaxe
│   ├── Cloud Translation         ← Traduction automatique
│   ├── Cloud Speech-to-Text      ← Transcription audio
│   ├── Cloud Text-to-Speech      ← Synthèse vocale
│   └── Document AI               ← Traitement de documents (formulaires, factures)
└── Vertex AI (plateforme ML)
    ├── Gemini (1.5 Pro, Flash, Ultra)  ← LLM multimodal de Google
    ├── Model Garden              ← Accès à des modèles tiers (Llama, Mistral...)
    ├── AutoML                    ← Entraînement sans code
    ├── Custom Training           ← Training avec votre propre code
    └── Feature Store             ← Gestion des features ML
```

---

## Régions disponibles en Europe

| Région | Localisation | Code |
|--------|-------------|------|
| EU West 1 | Belgique | `europe-west1` |
| EU West 3 | Francfort | `europe-west3` |
| EU West 4 | Pays-Bas | `europe-west4` |
| EU West 9 | Paris | `europe-west9` |
| EU Central 2 | Varsovie | `europe-central2` |
| EU North 1 | Finlande | `europe-north1` |

> Pour les projets RGPD, préférez `europe-west9` (Paris) ou `europe-west3` (Francfort).

---

## Pour commencer

1. [01-gcp-ai-overview.md](./01-gcp-ai-overview.md) — Setup, authentification, SDK
2. [02-document-ai.md](./02-document-ai.md) — Extraction documentaire avec Document AI
3. [03-vision-api.md](./03-vision-api.md) — Analyse d'images avec Cloud Vision API
