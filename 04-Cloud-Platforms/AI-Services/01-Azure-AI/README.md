# Azure AI — Vue d'ensemble

## Qu'est-ce que Azure AI ?

Azure AI est l'ensemble des services d'intelligence artificielle proposés par Microsoft sur sa plateforme cloud Azure. Ces services permettent d'intégrer des capacités IA dans vos applications sans avoir besoin de former vous-même des modèles d'apprentissage automatique.

Microsoft a structuré son offre IA autour de deux grandes familles :

1. **Azure AI Services** (anciennement Cognitive Services) : services pré-entraînés accessibles via API REST, couvrant la vision, le langage, la parole, la décision et la recherche
2. **Azure Machine Learning** : plateforme MLOps pour entraîner, déployer et monitorer vos propres modèles

Ce module se concentre sur les **Azure AI Services** (services managés prêts à l'emploi).

---

## Services couverts dans ce module

| Fichier | Service | Usage principal |
|---------|---------|----------------|
| `01-azure-ai-services.md` | Azure AI Services (overview) | Comprendre l'architecture, les clés API, les endpoints |
| `02-document-intelligence.md` | Azure Document Intelligence | Extraire des données structurées de PDFs et images |
| `03-vision.md` | Azure Computer Vision | OCR, analyse d'images, détection d'objets |
| `04-openai-azure.md` | Azure OpenAI Service | GPT-4, embeddings, DALL-E en environnement enterprise |

---

## Architecture générale d'Azure AI Services

```
┌─────────────────────────────────────────────────────────────────┐
│                        AZURE AI SERVICES                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   LANGAGE    │   VISION     │   PAROLE     │    DÉCISION        │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│ Text         │ Computer     │ Speech to    │ Anomaly            │
│ Analytics    │ Vision       │ Text         │ Detector           │
│              │              │              │                    │
│ Language     │ Custom       │ Text to      │ Content            │
│ Understanding│ Vision       │ Speech       │ Moderator          │
│ (CLU)        │              │              │                    │
│              │ Face API     │ Speaker      │ Personalizer       │
│ Translator   │              │ Recognition  │                    │
│              │ Document     │              │                    │
│ Question     │ Intelligence │ Translation  │                    │
│ Answering    │              │              │                    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  AZURE OPENAI     │
                    │  (service séparé) │
                    │  GPT-4o, DALL-E,  │
                    │  Whisper, etc.    │
                    └───────────────────┘
```

---

## Régions disponibles en Europe

Pour les projets soumis au RGPD, privilégiez ces régions :

| Région Azure | Localisation | Code |
|--------------|-------------|------|
| France Central | Paris | `francecentral` |
| France South | Marseille | `francesouth` |
| West Europe | Amsterdam | `westeurope` |
| North Europe | Dublin | `northeurope` |
| Switzerland North | Zurich | `switzerlandnorth` |

> Note : Tous les services Azure AI ne sont pas disponibles dans toutes les régions. France Central est recommandée pour les projets français.

---

## Modèle de facturation

Azure AI Services utilise un modèle **pay-as-you-go** :

- Pas d'abonnement fixe obligatoire
- Facturation à l'utilisation (par page, par image, par caractère, par token)
- Free tier disponible sur la plupart des services (F0)
- Standard tier (S0/S1) pour la production avec SLA

---

## Pour commencer

1. [01-azure-ai-services.md](./01-azure-ai-services.md) — Créer votre première ressource et appeler l'API
2. [02-document-intelligence.md](./02-document-intelligence.md) — Extraire des données de documents PDF
3. [03-vision.md](./03-vision.md) — Analyser des images avec Computer Vision
4. [04-openai-azure.md](./04-openai-azure.md) — Utiliser GPT-4 via Azure OpenAI
