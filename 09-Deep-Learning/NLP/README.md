# 🤖 NLP — Traitement du Langage Naturel

Faire comprendre le langage humain aux ordinateurs, **des bases statistiques aux Transformers**
(BERT, GPT). Le cours de référence est la **version V3**, la plus complète : chaque module a ses
leçons **et ses notebooks exécutables**.

## 📚 Le cours (V3)

👉 **Index complet : [Cours NLP V3](V3/nlp_course_index.md)**

| Module | Sujet | Concepts durs → intuition |
|---|---|---|
| [Module 1](V3/Module1/index.md) | Introduction & évolution du NLP | — |
| [Module 2](V3/Module2/index.md) | Preprocessing & tokenisation *(notebooks)* | découper le texte en unités |
| [Module 3](V3/Module3/index.md) | Représentations : BoW, TF-IDF, n-grams *(notebooks)* | transformer des mots en nombres |
| [Module 4](V3/Module4/index.md) | Word embeddings : Word2Vec, GloVe, FastText *(notebooks)* | un mot = un point dans un espace de sens |
| [Module 5](V3/Module5/index.md) | Réseaux récurrents : RNN, LSTM, GRU *(notebooks)* | une mémoire qui lit mot à mot |
| [Module 6](V3/Module6/index.md) | **Attention & Transformers** *(notebooks)* | le surligneur qui pondère les mots ([chap. 0 §11](../01-Fondamentaux-DL/cours/00-intuition-analogies.md)) |
| [Module 7](V3/Module7/index.md) | **BERT & GPT**, fine-tuning *(notebooks)* | comprendre vs générer |
| [Module 8](V3/Module8/index.md) | Déploiement en production | servir un modèle NLP |

## 🧪 Mini-projet fourni (exemple entraîné)

Un petit modèle **déjà entraîné** pour se faire la main — un prédicteur de capitale de pays :

```bash
pip install -r requirements.txt
python predict.py        # utilise le modèle entraîné capital_model.pth
# ou ré-entraîner :
python train.py
```

Fichiers : `train.py`, `model.py`, `predict.py`, `data.py`, données `train_data.json` / `test_data.json`.

## 🎯 Brief

- [**Analyse de sentiments**](../../99-Brief/Dev-IA/Deep-Learning-NLP/BRIEF_ANALYSE_SENTIMENTS.md) — classer des avis clients (positif/négatif) du TF-IDF au Transformer.

---
[🏠 Retour au menu principal](../../README.md)
