# Streamlit — Applications de Data Science Interactives

## Vue d'ensemble

Streamlit est un framework Python open source qui transforme des scripts de data science en applications web interactives en quelques minutes. Là où Gradio est optimisé pour exposer des fonctions ML, Streamlit est optimisé pour la **visualisation de données, les dashboards, et les applications IA complètes**.

La philosophie de Streamlit est radicale : l'application se réexécute de haut en bas à chaque interaction de l'utilisateur. Pas de callbacks complexes, pas de gestion d'état explicite dans la plupart des cas — juste du Python séquentiel.

## Objectifs pédagogiques

À la fin de ce module, vous serez capable de :

- Créer une application Streamlit avec navigation multi-pages
- Utiliser les composants d'affichage et d'interaction principaux
- Gérer l'état de session avec `st.session_state`
- Optimiser les performances avec `@st.cache_data`
- Construire un dashboard de visualisation avec Pandas et Plotly
- Intégrer un LLM avec `st.chat_message` et `st.chat_input`

## Prérequis

- **Python 3.9+** avec pip ou uv
- **Bases Python** : fonctions, listes, dictionnaires
- **Pandas basique** : DataFrame, read_csv, groupby (module 01)
- **Optionnel** : Plotly ou Matplotlib pour la visualisation

## Contenu du module

| # | Chapitre | Durée | Niveau |
|---|----------|-------|--------|
| 01 | [Introduction à Streamlit](01-introduction.md) | 1h30 | Débutant |
| 02 | [Composants et affichage](02-composants.md) | 2h | Débutant |
| 03 | [État de session et formulaires](03-state-sessions.md) | 2h | Intermédiaire |
| 04 | [Dashboard de données](04-dashboard-data.md) | 2h30 | Intermédiaire |
| 05 | [Application IA avec chat](05-app-ia.md) | 2h | Intermédiaire |

## Exercices

| # | Exercice | Prérequis |
|---|----------|-----------|
| 01 | [Dashboard d'exploration de données](exercices/exercice-01-dashboard.md) | Chapitres 01-04 |

## Ressources complémentaires

- [Cheatsheet Streamlit](CHEATSHEET-streamlit.md)
- Documentation officielle : https://docs.streamlit.io
- Galerie de composants : https://streamlit.io/components
- Streamlit Cloud (hébergement gratuit) : https://share.streamlit.io

## Installation rapide

```bash
pip install streamlit
# ou avec uv
uv add streamlit

# Vérifier
streamlit --version
```

## Différences avec Gradio

| Critère | Streamlit | Gradio |
|---------|-----------|--------|
| Point fort | Dashboards, exploration de données | Démos ML, chatbots |
| Modèle d'exécution | Réexécution complète à chaque interaction | Callbacks ciblés |
| Mise en page | Flexible, multi-pages | Simple ou Blocks |
| Visualisation | Natif (Pandas, Plotly, Matplotlib) | Limité |
| Chatbot | Oui (st.chat_message) | Oui (gr.Chatbot) |
| Courbe d'apprentissage | Très douce | Très douce |
