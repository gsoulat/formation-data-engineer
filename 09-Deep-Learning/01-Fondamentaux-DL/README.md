# Fondamentaux du Deep Learning

## Vue d'ensemble

Ce module pose les bases du Deep Learning avant de plonger dans les architectures specialisees (CNN, NLP). Vous y apprendrez les concepts fondamentaux, depuis le neurone artificiel jusqu'a l'entrainement complet d'un reseau de neurones avec PyTorch.

## Prerequis

- **Machine Learning (Module 08)** : regressions, classification, metriques (accuracy, precision, recall)
- **Python** : programmation orientee objet, NumPy
- **Mathematiques** : algebre lineaire de base (matrices, produit matriciel), derivees

## Contenu

| # | Chapitre | Duree | Niveau | Description |
|---|----------|-------|--------|-------------|
| 00 | [🧭 Comprendre le DL par l'intuition](./cours/00-intuition-analogies.md) | 1h | Fondamental | **À lire en premier** — analogies pour tous les concepts durs (neurone, activation, loss, gradient, backprop, convolution, attention) |
| 01 | [Introduction au Deep Learning](./cours/01-introduction-deep-learning.md) | 2h | Fondamental | ML vs DL, neurone artificiel, architectures, GPU |
| 02 | [Reseaux de neurones](./cours/02-reseaux-neurones.md) | 3h | Fondamental | Forward/backward propagation, activations, loss, optimizers |
| 03 | [PyTorch](./cours/03-frameworks-pytorch.md) | 3h | Intermediaire | Tensors, autograd, nn.Module, DataLoader, boucle d'entrainement |
| 04 | [Entrainement pratique](./cours/04-entrainement-pratique.md) | 3h | Intermediaire | Hyperparametres, overfitting, Transfer Learning, methodologie |

## Progression recommandee

```
Chapitre 00 (Intuition & analogies)  ← pose les images mentales
     |
     v
Chapitre 01 (Introduction)
     |
     v
Chapitre 02 (Theorie des reseaux)
     |
     v
Chapitre 03 (PyTorch en pratique)
     |
     v
Chapitre 04 (Entrainement et methodologie)
```

## Apres ce module

- **02-CNN/** : Vision par ordinateur (Convolutional Neural Networks)
- **03-NLP/** : Traitement du langage naturel (Transformers, BERT, GPT)
