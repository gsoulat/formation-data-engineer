---
title: 13_introduction_finetuning
tags:
  - LLM
  - 10-Large-Language-Model
category: 10-Large-Language-Model
---

# Jour 3 - Module 7 : Introduction au Fine-Tuning

Bienvenue dans cette dernière journée de formation ! Après avoir exploré le RAG pour étendre les connaissances d'un LLM, nous allons découvrir une autre technique de personnalisation : le **fine-tuning** (ou affinage).

> 🧭 **Introduction vs production** — ce chapitre **introduit** le fine-tuning. Pour la **pratique approfondie** (Transformers, LoRA/PEFT, préparation de datasets), voir le module dédié [**HuggingFace/04-Fine-Tuning**](../../HuggingFace/04-Fine-Tuning/). Voir la [carte des deux pistes](../../README.md).

## Qu'est-ce que le Fine-Tuning ?

Le fine-tuning est le processus qui consiste à prendre un modèle de base pré-entraîné (comme `llama3`) et à continuer son entraînement sur un jeu de données plus petit et spécifique à une tâche.

L'objectif n'est pas d'apprendre de nouvelles connaissances au modèle, mais de **modifier son comportement**. On cherche à l'adapter à un style, un format de réponse, ou une compétence particulière.

Par exemple, on peut fine-tuner un modèle pour qu'il :
-   Réponde toujours au format JSON.
-   Adopte un ton ou une personnalité spécifique (par exemple, parler comme un pirate).
-   Se spécialise dans une tâche très précise, comme la classification de sentiments ou l'extraction d'informations spécifiques d'un texte.

## Fine-Tuning vs. RAG : Quand utiliser quoi ?

C'est une question cruciale. Les deux techniques permettent de personnaliser un LLM, mais elles ne résolvent pas le même problème.

| Caractéristique | RAG (Retrieval-Augmented Generation) | Fine-Tuning | 
| :--- | :--- | :--- |
| **Objectif principal** | Fournir des connaissances externes et à jour. | Adapter le style, le format ou la compétence du modèle. |
| **Comment ça marche ?** | Ajoute du contexte au prompt au moment de la requête. | Modifie les poids internes du modèle lors d'une phase d'entraînement. |
| **Idéal pour...** | Répondre à des questions sur des documents spécifiques (FAQs, rapports, etc.). | Changer le comportement du LLM, le spécialiser. |
| **Mise à jour** | Facile : il suffit de mettre à jour la base de données documentaire. | Difficile : nécessite de relancer un processus d'entraînement. |

**Règle générale :**
-   Si vous voulez que votre modèle **connaisse** quelque chose de nouveau, utilisez le **RAG**.
-   Si vous voulez que votre modèle **soit** quelque chose de nouveau (un expert en SQL, un poète, un classificateur de texte), utilisez le **fine-tuning**.

Les deux approches peuvent même être combinées pour obtenir des résultats encore plus performants.

---

Maintenant que nous savons ce qu'est le fine-tuning et à quoi il sert, passons au module suivant pour voir comment le mettre en pratique avec Ollama et un `Modelfile`.

**[Prochain Module : Pratique du Fine-Tuning avec Ollama](./8_pratique_finetuning.md)**
