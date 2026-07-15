# 🧠 Deep Learning – Des Fondamentaux aux Applications

## 🎯 Vue d'ensemble

Ce module vous forme au Deep Learning, des bases (neurones, backpropagation) aux applications avancées (vision par ordinateur, NLP).

## 📋 Prérequis

- Python (POO, bibliothèque standard) → Module 01-Fondamentaux/Python
- Machine Learning → Module 08-Machine-Learning
- Recommandé : notions de mathématiques (algèbre linéaire, calcul différentiel)

## 📚 Structure du module

### [01-Fondamentaux-DL](01-Fondamentaux-DL/)
*Base commune obligatoire avant CNN ou NLP.*
| # | Chapitre | Durée | Niveau |
|:--|:---------|:------|:-------|
| 01 | Introduction au Deep Learning | 2h | 🟢 Fondamental |
| 02 | Réseaux de neurones | 3h | 🟢 Fondamental |
| 03 | PyTorch | 3h | 🟡 Intermédiaire |
| 04 | Entraînement pratique | 3h | 🟡 Intermédiaire |

### [02-CNN – Vision par Ordinateur](CNN/)
*Réseaux convolutifs pour le traitement d'images.*
| # | Module | Durée | Niveau |
|:--|:-------|:------|:-------|
| 01 | Fondamentaux des CNN | 45 min | 🟢 Fondamental |
| 02 | Opérations de base | 1h30 | 🟢 Fondamental |
| 03 | Techniques avancées | 2h | 🟡 Intermédiaire |
| 04 | Architectures célèbres | 1h45 | 🟡 Intermédiaire |
| 05 | Applications pratiques | 1h30 | 🟡 Intermédiaire |
| 06 | Projets et exercices | 3h+ | 🔴 Avancé |
| 07 | Métriques et optimisation | 2h | 🔴 Avancé |
| 08 | Couches avancées | 2h | 🔴 Expert |

### [03-NLP – Traitement du Langage](NLP/)
*Du preprocessing au Transformers.*
| # | Module | Durée | Niveau |
|:--|:-------|:------|:-------|
| 01 | Introduction au NLP | 2h | 🟢 Fondamental |
| 02 | Preprocessing et Tokenisation | 4h | 🟢 Fondamental |
| 03 | Représentations textuelles (BoW, TF-IDF) | 3h | 🟡 Intermédiaire |
| 04 | Word Embeddings (Word2Vec, GloVe) | 3h | 🟡 Intermédiaire |
| 05 | Réseaux récurrents (RNN, LSTM) | 4h | 🟡 Intermédiaire |
| 06 | Attention et Transformers | 4h | 🔴 Avancé |
| 07 | BERT et GPT | 4h | 🔴 Avancé |
| 08 | Déploiement en production | 3h | 🔴 Avancé |

### [04-Génératif – Créer avec l'IA](Generatif/)
*Comment un réseau apprend à générer (images, sons).*
| # | Leçon | Durée | Niveau |
|:--|:------|:------|:-------|
| 01 | Autoencodeurs | 1h30 | 🟡 Intermédiaire |
| 02 | VAE (autoencodeurs variationnels) | 2h | 🔴 Avancé |
| 03 | GAN (réseaux antagonistes) | 2h | 🔴 Avancé |
| 04 | Modèles de diffusion (Stable Diffusion) | 2h | 🔴 Avancé |

### [05-Avancé – Au-delà des CNN et RNN](Avance/)
*Panorama conceptuel des architectures modernes.*
| # | Leçon | Durée | Niveau |
|:--|:------|:------|:-------|
| 01 | Vision Transformers (ViT) | 1h30 | 🔴 Avancé |
| 02 | Modèles multimodaux (CLIP) | 1h30 | 🔴 Avancé |
| 03 | Auto-supervision (BERT/GPT) | 1h30 | 🔴 Expert |
| 04 | Graph Neural Networks (GNN) | 1h30 | 🔴 Expert |

## 🛠️ Technologies utilisées

**PyTorch** | **torchvision** | **Hugging Face Transformers** | **NLTK** | **spaCy** | **NumPy**

## 🚀 Parcours recommandé

```
01-Fondamentaux-DL (obligatoire)
         │
    ┌────┴────┐
    │         │
 02-CNN    03-NLP
 (Vision)  (Texte)
    │         │
    └────┬────┘
         │
    10-LLM (suite)
```

**04-Génératif** (autoencodeurs, VAE, GAN, diffusion) se fait après CNN — c'est le pont naturel vers
les **LLM** (qui sont des modèles génératifs de texte). **05-Avancé** (ViT, multimodal, auto-supervision,
GNN) est un panorama conceptuel des architectures modernes, à faire en dernier.

Vous pouvez faire CNN et NLP en parallèle ou séquentiellement. Les deux nécessitent les Fondamentaux DL.

## 🎯 Briefs projet (un par module)

- **Fondamentaux** — [Ton premier réseau de neurones](../99-Brief/Dev-IA/Deep-Learning-Fondamentaux/BRIEF_PREMIER_RESEAU.md) (Fashion-MNIST, MLP→CNN).
- **Vision** — [Classificateur d'images (transfer learning)](../99-Brief/Dev-IA/Deep-Learning-Vision/BRIEF_CLASSIFICATION_IMAGES.md) + [YOLOv8 détection](CNN/yolo_brief.md).
- **NLP** — [Analyse de sentiments](../99-Brief/Dev-IA/Deep-Learning-NLP/BRIEF_ANALYSE_SENTIMENTS.md) (TF-IDF → Transformer).
- **Génératif** — [Générer des images](../99-Brief/Dev-IA/Deep-Learning-Generatif/BRIEF_GENERATIF.md) (autoencodeur, VAE, GAN).

---
[🏠 Retour à l'accueil](../README.md)
