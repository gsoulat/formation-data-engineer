# 05 — Application IA avec Streamlit

## Vue d'ensemble

Ce chapitre montre comment intégrer des modèles d'IA dans Streamlit : prédictions ML, chatbot LLM avec streaming, et interface d'analyse de données assistée par IA. Streamlit fournit des composants natifs dédiés au chat (`st.chat_message`, `st.chat_input`) qui rendent la construction de chatbots très naturelle.

## Affichage de prédictions ML

### Interface de prédiction simple

```python
import streamlit as st
import numpy as np
import joblib

@st.cache_resource
def charger_modele():
    return joblib.load("modele_iris.pkl")

modele = charger_modele()
noms_classes = ["Setosa", "Versicolor", "Virginica"]

st.title("Classificateur d'Iris")
st.write("Entrez les mesures morphologiques pour prédire l'espèce.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sépale")
    long_sepal = st.slider("Longueur (cm)", 4.0, 8.0, 5.8, 0.1)
    larg_sepal = st.slider("Largeur (cm)", 2.0, 4.5, 3.0, 0.1)

with col2:
    st.subheader("Pétale")
    long_petal = st.slider("Longueur (cm)", 1.0, 7.0, 3.8, 0.1)
    larg_petal = st.slider("Largeur (cm)", 0.1, 2.5, 1.2, 0.1)

# Prédiction en temps réel (mise à jour à chaque déplacement de slider)
features = np.array([[long_sepal, larg_sepal, long_petal, larg_petal]])
probas = modele.predict_proba(features)[0]
classe_predite = noms_classes[probas.argmax()]
confiance = probas.max()

st.markdown("---")
st.subheader("Résultat de la prédiction")

col_pred, col_jauge = st.columns([1, 2])

with col_pred:
    couleur = {"Setosa": "🟢", "Versicolor": "🟡", "Virginica": "🔵"}
    st.metric(
        label="Espèce prédite",
        value=classe_predite,
        delta=f"Confiance : {confiance:.1%}",
    )

with col_jauge:
    # Afficher les probabilités sous forme de barres
    for nom, proba in zip(noms_classes, probas):
        st.write(f"**{nom}** : {proba:.1%}")
        st.progress(float(proba))
```

### Prédiction par lot avec upload de fichier

```python
import streamlit as st
import pandas as pd
import numpy as np
import joblib

@st.cache_resource
def charger_modele():
    return joblib.load("modele_churn.pkl")

modele = charger_modele()

st.title("Prédiction de churn — Mode lot")

st.write("""
Uploadez un fichier CSV contenant les colonnes :
`age`, `anciennete_mois`, `nb_produits`, `solde`, `salaire_estime`
""")

fichier = st.file_uploader("Fichier clients (CSV)", type="csv")

if fichier:
    df = pd.read_csv(fichier)

    colonnes_requises = ["age", "anciennete_mois", "nb_produits", "solde", "salaire_estime"]
    colonnes_manquantes = [c for c in colonnes_requises if c not in df.columns]

    if colonnes_manquantes:
        st.error(f"Colonnes manquantes : {', '.join(colonnes_manquantes)}")
    else:
        with st.spinner("Calcul des prédictions..."):
            X = df[colonnes_requises]
            df["probabilite_churn"] = modele.predict_proba(X)[:, 1]
            df["prediction"] = (df["probabilite_churn"] > 0.5).map(
                {True: "Churn probable", False: "Client stable"}
            )

        # Résumé
        nb_churn = (df["prediction"] == "Churn probable").sum()
        st.success(f"Prédictions calculées : {nb_churn}/{len(df)} clients à risque ({nb_churn/len(df):.1%})")

        # Tableau résultats
        st.dataframe(
            df.sort_values("probabilite_churn", ascending=False),
            column_config={
                "probabilite_churn": st.column_config.ProgressColumn(
                    "Risque de churn", min_value=0, max_value=1, format="%.1%"
                ),
                "prediction": st.column_config.SelectboxColumn(
                    "Prédiction",
                    options=["Churn probable", "Client stable"],
                ),
            },
            use_container_width=True,
        )

        # Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger les résultats", csv, "predictions_churn.csv", "text/csv")
```

## `st.chat_message` et `st.chat_input`

Streamlit fournit des composants natifs pour les interfaces de chat.

### Composants de base

```python
# Afficher un message
with st.chat_message("user"):
    st.write("Bonjour ! Pouvez-vous m'expliquer le machine learning ?")

with st.chat_message("assistant"):
    st.write("Bien sûr ! Le machine learning est...")
    st.code("from sklearn.linear_model import LinearRegression", language="python")

# Zone de saisie en bas de page
prompt = st.chat_input("Posez votre question...")
if prompt:
    st.write(f"Vous avez écrit : {prompt}")
```

### Chatbot complet avec historique

```python
import streamlit as st

st.set_page_config(page_title="Assistant IA", page_icon="🤖", layout="wide")

st.title("Assistant IA — Data Engineering")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour ! Je suis votre assistant spécialisé en Data Engineering. Comment puis-je vous aider ?"
        }
    ]

# Afficher l'historique complet
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie (toujours en bas grâce à st.chat_input)
if prompt := st.chat_input("Posez votre question..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Générer la réponse (simulée ici)
    reponse = f"Votre question '{prompt}' est très pertinente. Voici ma réponse..."

    with st.chat_message("assistant"):
        st.markdown(reponse)

    st.session_state.messages.append({"role": "assistant", "content": reponse})
```

## Chatbot avec LLM et streaming

```python
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Assistant Data Engineering", page_icon="🤖", layout="wide")

@st.cache_resource
def get_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

client = get_client()

SYSTEM_PROMPT = """Tu es un expert en Data Engineering et IA.
Tu réponds en français, de manière concise et technique.
Tu donnes des exemples de code Python quand c'est pertinent.
Tu es bienveillant et pédagogue."""

# Sidebar avec paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    modele = st.selectbox("Modèle", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    temperature = st.slider("Température", 0.0, 2.0, 0.7, 0.05)
    max_tokens = st.slider("Max tokens", 100, 4000, 1000, 100)

    st.markdown("---")
    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(f"Modèle actif : {modele}")

st.title("🤖 Assistant Data Engineering")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Saisie utilisateur
if prompt := st.chat_input("Posez votre question sur le Data Engineering..."):
    # Afficher le message utilisateur immédiatement
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Générer et streamer la réponse
    with st.chat_message("assistant"):
        messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages_api.extend(st.session_state.messages)

        # st.write_stream accepte un générateur et affiche les tokens progressivement
        stream = client.chat.completions.create(
            model=modele,
            messages=messages_api,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        reponse_complete = st.write_stream(
            (chunk.choices[0].delta.content or "" for chunk in stream)
        )

    st.session_state.messages.append({"role": "assistant", "content": reponse_complete})
```

> **`st.write_stream`** est la manière la plus simple de streamer du texte dans Streamlit. Il accepte n'importe quel itérable de chaînes et les affiche progressivement. Retourne la chaîne complète à la fin.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration du chatbot avec streaming — poser une question technique sur le Data Engineering et montrer les tokens qui apparaissent progressivement
> **Expliquer :** Expliquer le rôle de `st.write_stream` : il consomme le générateur OpenAI et affiche chaque token au fur et à mesure. La valeur retournée est la chaîne complète, qu'on stocke dans `session_state`. Montrer la différence avec et sans streaming (si le temps le permet). Expliquer le rôle du System Prompt : il configure le comportement et la personnalité du modèle.
---

## Application IA complète : analyse de données assistée

Voici un exemple d'application plus avancée qui combine analyse de données et LLM :

```python
import streamlit as st
import pandas as pd
from openai import OpenAI
import os

@st.cache_resource
def get_client():
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

client = get_client()

st.set_page_config(page_title="Analyse IA", layout="wide")
st.title("Analyse de données assistée par IA")

# Upload du dataset
fichier = st.file_uploader("Chargez votre dataset CSV", type="csv")

if fichier:
    df = pd.read_csv(fichier)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Aperçu des données")
        st.dataframe(df.head(10), use_container_width=True)

    with col2:
        st.subheader("Statistiques")
        st.write(f"**Lignes :** {len(df):,}")
        st.write(f"**Colonnes :** {len(df.columns)}")
        st.write(f"**Valeurs manquantes :** {df.isnull().sum().sum():,}")

    st.markdown("---")
    st.subheader("Questions sur vos données")

    if "messages_analyse" not in st.session_state:
        st.session_state.messages_analyse = []

    # Contexte du dataset pour le LLM
    contexte_dataset = f"""
Tu as accès à un dataset CSV avec les caractéristiques suivantes :
- Nombre de lignes : {len(df)}
- Colonnes : {', '.join(df.columns.tolist())}
- Types de données : {df.dtypes.to_dict()}
- Statistiques descriptives :
{df.describe().to_string()}
- Valeurs manquantes par colonne :
{df.isnull().sum().to_dict()}

Réponds aux questions de l'utilisateur sur ce dataset.
Suggère des analyses pertinentes.
Propose du code Python/Pandas si nécessaire.
"""

    for msg in st.session_state.messages_analyse:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Posez une question sur vos données..."):
        st.session_state.messages_analyse.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            messages_api = [
                {"role": "system", "content": contexte_dataset},
            ] + st.session_state.messages_analyse

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_api,
                stream=True,
                temperature=0.3,  # moins créatif, plus précis pour l'analyse
            )
            reponse = st.write_stream(
                (chunk.choices[0].delta.content or "" for chunk in stream)
            )

        st.session_state.messages_analyse.append(
            {"role": "assistant", "content": reponse}
        )
else:
    st.info("Uploadez un fichier CSV pour commencer l'analyse.")
    st.write("**Exemples de questions que vous pourrez poser :**")
    questions_exemples = [
        "Quelles colonnes contiennent des valeurs manquantes et comment les traiter ?",
        "Y a-t-il des corrélations intéressantes entre les variables ?",
        "Quelles analyses exploratoires recommandes-tu pour ce dataset ?",
        "Génère le code Python pour créer une visualisation de distribution.",
    ]
    for q in questions_exemples:
        st.write(f"- *{q}*")
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Upload d'un dataset CSV, puis poser une question au LLM sur les données (ex : "Y a-t-il des corrélations intéressantes ?") et montrer la réponse contextualisée
> **Expliquer :** Expliquer la technique du "context injection" : on inclut les statistiques descriptives du dataset dans le System Prompt. Ainsi, le LLM répond sur les vraies caractéristiques du dataset sans avoir besoin de le voir entièrement. C'est une approche pratique pour les petits datasets. Pour les grands datasets, il faudrait utiliser des techniques RAG (embeddings + recherche vectorielle).
---

## Résumé du chapitre

- `st.progress` affiche les probabilités de classe de manière visuelle
- `@st.cache_resource` garantit qu'un seul modèle est chargé pour toute l'application
- `st.chat_message(role)` affiche une bulle de conversation avec l'avatar approprié
- `st.chat_input` affiche une zone de saisie fixe en bas de page
- `st.write_stream` consomme un générateur et affiche les tokens progressivement
- Le context injection (inclure les stats du dataset dans le system prompt) permet d'analyser des données avec un LLM sans envoyer tout le fichier
- `st.rerun()` force la réexécution du script (utile pour réinitialiser l'état)

Ce chapitre conclut le module Streamlit. Passez aux exercices et consultez la cheatsheet pour une référence rapide.
