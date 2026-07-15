# 03 — Apprentissage auto-supervisé (self-supervised)

[← 02 — Multimodal](02-multimodal.md) | [🏠 Accueil](README.md) | [04 — GNN →](04-gnn.md)

### 🎥 En vidéo
▶️ Cherche « [self-supervised learning explained](https://www.youtube.com/results?search_query=self+supervised+learning+explained) ».

## 🎯 Objectifs
- Comprendre comment un modèle apprend **sans étiquettes humaines**.
- Voir pourquoi c'est ce qui a rendu possibles **BERT, GPT et les grands modèles**.

## 🧠 Intuition & analogie

Étiqueter des millions d'exemples à la main coûte une fortune. L'**auto-supervision** contourne le
problème : le modèle **fabrique lui-même sa tâche** à partir de données brutes, en **cachant une
partie** et en apprenant à la **retrouver**.

> **Analogie** — Un **texte à trous** : « Le chat dort sur le ___ ». Personne n'a étiqueté quoi que ce
> soit ; le mot manquant **est** la réponse. En jouant à ce jeu des milliards de fois, le modèle apprend
> la structure du langage (c'est **exactement** l'entraînement de BERT). Le modèle **se donne ses propres
> exercices et son propre corrigé**.

## 📐 Les grandes recettes

| Méthode | Le « jeu » que le modèle se donne | Exemple |
|---|---|---|
| **Masquage** (masked) | cacher des mots/pixels et les prédire | **BERT** (texte), MAE (images) |
| **Autoregressif** | prédire le mot **suivant** | **GPT** |
| **Contrastif** | rapprocher deux vues de la même donnée, éloigner les autres | SimCLR, **CLIP** |

Résultat : un modèle **pré-entraîné** qui « comprend » déjà le domaine. On le **fine-tune** ensuite
sur une petite tâche étiquetée (analyse de sentiments, classification…) — c'est le transfer learning.

> 💡 **Le déclic historique** — c'est l'auto-supervision (masquage pour BERT, mot-suivant pour GPT) qui
> a permis d'entraîner des modèles sur **tout le web sans étiquetage**, donnant les LLM d'aujourd'hui.

## ✅ À retenir
- L'auto-supervision **crée la tâche à partir des données brutes** (cacher → retrouver) → **pas
  d'étiquetage humain**.
- Trois familles : **masquage** (BERT), **autoregressif** (GPT), **contrastif** (CLIP/SimCLR).
- C'est le moteur du **pré-entraînement** des grands modèles, avant le fine-tuning.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Self-supervised learning](https://www.youtube.com/results?search_query=self+supervised+learning+explained) | EN | EN | Le principe cacher/retrouver |
| [Comment BERT s'entraîne](https://www.youtube.com/results?search_query=bert+masked+language+model+training) | EN | EN | Le masquage en pratique |
