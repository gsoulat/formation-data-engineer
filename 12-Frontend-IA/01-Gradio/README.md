# Gradio — Interfaces Web pour vos Modèles IA

## Vue d'ensemble

Ce module vous apprend à créer des **interfaces web interactives** pour exposer vos modèles de machine learning et vos applications IA sans écrire une seule ligne de HTML ou JavaScript. Gradio transforme n'importe quelle fonction Python en application web partageable en quelques lignes de code.

La progression suit le principe : **fonctionnel d'abord, élaboré ensuite**. Vous aurez une interface qui tourne en 10 minutes, et vous la complexifierez au fil des chapitres.

## Objectifs pédagogiques

À la fin de ce module, vous serez capable de :

- Créer une interface Gradio simple autour d'une fonction Python ou d'un modèle ML
- Utiliser les composants principaux : texte, image, audio, fichier, dropdown, slider
- Construire un chatbot conversationnel avec historique et streaming
- Connecter Gradio à un LLM (OpenAI, Ollama) via des générateurs asynchrones
- Déployer une application Gradio sur Hugging Face Spaces et avec Docker
- Sécuriser une interface avec authentification basique

## Prérequis

- **Python 3.9+** avec pip ou uv
- **Bases Python** : fonctions, listes, dictionnaires, décorateurs
- **Notions de ML** : avoir entraîné au moins un modèle scikit-learn (module 08)
- **Optionnel** : connaissances LLM (module 10) pour le chapitre 04

## Contenu du module

| # | Chapitre | Durée | Niveau |
|---|----------|-------|--------|
| 01 | [Introduction à Gradio](01-introduction.md) | 1h30 | Débutant |
| 02 | [Composants et mise en page](02-composants.md) | 2h | Débutant |
| 03 | [Interface Chatbot](03-chatbot-interface.md) | 2h | Intermédiaire |
| 04 | [Intégration LLM](04-integration-llm.md) | 2h30 | Intermédiaire |
| 05 | [Déploiement](05-deploiement.md) | 2h | Intermédiaire |

## Exercices

| # | Exercice | Prérequis |
|---|----------|-----------|
| 01 | [Interface ML scikit-learn](exercices/exercice-01-interface-ml.md) | Chapitres 01-02 |

## Ressources complémentaires

- [Cheatsheet Gradio](CHEATSHEET-gradio.md)
- Documentation officielle : https://www.gradio.app/docs
- Hugging Face Spaces : https://huggingface.co/spaces

## Installation rapide

```bash
pip install gradio
# ou avec uv
uv add gradio
```

Vérifier l'installation :

```bash
python -c "import gradio as gr; print(gr.__version__)"
```
