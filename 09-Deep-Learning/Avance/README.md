# 🚀 Sujets avancés

*Panorama des architectures qui définissent le Deep Learning d'aujourd'hui — au-delà des CNN et RNN.*

> Sous-module du parcours [Deep Learning](../README.md). Prérequis : [CNN](../CNN/), [NLP](../NLP/)
> (attention/Transformers) et [Fondamentaux](../01-Fondamentaux-DL/). Ce module est plus **conceptuel**
> (comprendre l'idée et savoir quand l'utiliser) que « from scratch ».

## 📚 Cours

| # | Leçon | Idée en une phrase |
|---|---|---|
| 01 | [Vision Transformers (ViT)](01-vision-transformers.md) | lire une image **comme une phrase** de patches |
| 02 | [Modèles multimodaux](02-multimodal.md) | image **et** texte dans un **espace partagé** (CLIP) |
| 03 | [Auto-supervision](03-self-supervised.md) | apprendre **sans étiquettes** (cacher → retrouver) |
| 04 | [Graph Neural Networks](04-gnn.md) | apprendre sur des **graphes** (molécules, réseaux) |

## 🧭 Comment ça s'articule

- **ViT** relie la **vision** (CNN) et les **Transformers** (NLP).
- L'**auto-supervision** explique **comment** on entraîne BERT/GPT sans étiquetage → mène aux **LLM**.
- Le **multimodal** (CLIP) est la brique derrière la génération texte→image et les LLM multimodaux.
- Les **GNN** ouvrent le DL à des données **non-grilles** (graphes).

## ➡️ Après ce module
La suite naturelle de l'auto-supervision et des Transformers à grande échelle, ce sont les **LLM** →
[10-Large-Language-Model](../../10-Large-Language-Model/).

---
[🏠 Retour au module Deep Learning](../README.md)
