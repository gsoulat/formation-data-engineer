# 02 — Composants et affichage

## Vue d'ensemble

Streamlit fournit une riche bibliothèque de composants couvrant l'affichage de texte, de données, de graphiques, et les éléments d'interaction. Ce chapitre les passe en revue avec des exemples pratiques et les paramètres les plus utiles.

## Affichage de texte

### `st.write` — le couteau suisse

`st.write` est la fonction la plus polyvalente de Streamlit. Elle détecte automatiquement le type de données et l'affiche de manière appropriée :

```python
import streamlit as st
import pandas as pd

# Texte simple
st.write("Texte simple")

# Markdown
st.write("**Gras**, *italique*, `code`")

# Nombre
st.write(3.14159)

# DataFrame
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
st.write(df)

# Dictionnaire
st.write({"clé": "valeur", "nombre": 42})

# Plusieurs éléments en une fois
st.write("Résultat :", 42, "| Score :", 0.95)
```

### Fonctions de texte spécialisées

```python
st.title("Titre principal (h1)")
st.header("En-tête (h2)")
st.subheader("Sous-en-tête (h3)")

st.markdown("## Titre en Markdown\n\n**Texte gras** avec `code` et [lien](https://exemple.com)")

st.text("Texte en police monospace, pas de formatage Markdown")

st.caption("Texte en petite taille, pour les légendes ou notes de bas de page")

st.code("""
def bonjour(nom):
    return f"Bonjour, {nom} !"
""", language="python")

st.latex(r"E = mc^2")
st.latex(r"\hat{y} = \sum_{i=1}^{n} w_i x_i + b")
```

## Affichage de données

### `st.dataframe` — tableau interactif

```python
import streamlit as st
import pandas as pd
import numpy as np

df = pd.DataFrame(
    np.random.randn(50, 5),
    columns=["A", "B", "C", "D", "E"]
)

st.dataframe(
    df,
    use_container_width=True,  # prend toute la largeur disponible
    height=300,                 # hauteur fixe avec scroll
    hide_index=False,           # cacher l'index
    column_config={             # configuration des colonnes
        "A": st.column_config.NumberColumn(
            "Colonne A",
            format="%.2f",
            min_value=-5,
            max_value=5,
        ),
        "B": st.column_config.ProgressColumn(
            "Progression",
            min_value=-3,
            max_value=3,
        ),
    }
)
```

### `st.table` — tableau statique

```python
# Tableau simple, non interactif
st.table(df.head(10))
```

### `st.metric` — indicateurs KPI

```python
col1, col2, col3 = st.columns(3)

col1.metric(
    label="Précision du modèle",
    value="94.2%",
    delta="+2.1%",           # variation (vert si positif)
    delta_color="normal",    # "normal", "inverse", "off"
)
col2.metric("Erreur moyenne", "0.031", "-0.005")
col3.metric("Temps d'inférence", "12 ms", "+3 ms", delta_color="inverse")
```

## Graphiques et visualisation

### Graphiques natifs Streamlit

```python
import streamlit as st
import pandas as pd
import numpy as np

# Données d'exemple
dates = pd.date_range("2024-01-01", periods=90)
df = pd.DataFrame({
    "ventes": np.random.randint(50, 200, 90),
    "coûts": np.random.randint(30, 120, 90),
}, index=dates)

# Courbe linéaire
st.line_chart(df, use_container_width=True, height=300)

# Barres
st.bar_chart(df["ventes"], use_container_width=True)

# Nuage de points
st.scatter_chart(df, x="coûts", y="ventes", use_container_width=True)

# Carte de chaleur (données géographiques)
# st.map(df_avec_lat_lon)
```

### Graphiques Plotly (recommandé pour plus de contrôle)

```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Exemple avec Plotly Express
df = px.data.gapminder().query("year == 2007")

fig = px.scatter(
    df,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,
    title="PIB par habitant vs Espérance de vie (2007)",
    labels={"gdpPercap": "PIB par habitant", "lifeExp": "Espérance de vie"},
)

st.plotly_chart(fig, use_container_width=True)
```

### Graphiques Matplotlib

```python
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

x = np.linspace(0, 10, 100)
axes[0].plot(x, np.sin(x), label="sin(x)")
axes[0].plot(x, np.cos(x), label="cos(x)")
axes[0].legend()
axes[0].set_title("Fonctions trigonométriques")

axes[1].hist(np.random.randn(1000), bins=30, color="steelblue", edgecolor="white")
axes[1].set_title("Distribution normale")

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)  # libérer la mémoire
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Affichage d'un graphique Plotly interactif dans Streamlit — montrer le hover, le zoom, le pan
> **Expliquer :** Passer la souris sur les points du scatter plot pour montrer le tooltip. Zoomer avec la molette de la souris. Expliquer que Plotly est interactif nativement dans Streamlit via `st.plotly_chart`. C'est un avantage majeur par rapport aux graphiques Matplotlib statiques.
---

## Composants d'interaction

### Saisie de texte

```python
# Champ monoligne
nom = st.text_input("Votre nom", value="", placeholder="Jean Dupont", max_chars=50)

# Zone multiligne
bio = st.text_area(
    "Décrivez votre projet",
    value="",
    placeholder="Votre description...",
    height=150,
    max_chars=1000,
)

# Saisie de nombre
age = st.number_input("Votre âge", min_value=0, max_value=150, value=25, step=1)

# Saisie de date
import datetime
date = st.date_input(
    "Date de naissance",
    value=datetime.date(1990, 1, 1),
    min_value=datetime.date(1900, 1, 1),
    max_value=datetime.date.today(),
)
```

### Sélection

```python
# Sélection unique dans une liste
pays = st.selectbox(
    "Pays",
    options=["France", "Belgique", "Suisse", "Canada"],
    index=0,  # valeur par défaut (index dans la liste)
)

# Sélection multiple
langages = st.multiselect(
    "Langages maîtrisés",
    options=["Python", "SQL", "Scala", "Java", "R"],
    default=["Python", "SQL"],
)

# Boutons radio
niveau = st.radio(
    "Niveau d'expérience",
    options=["Débutant", "Intermédiaire", "Avancé"],
    index=1,
    horizontal=True,  # affichage horizontal
)

# Checkbox
accepte_cgu = st.checkbox("J'accepte les conditions générales d'utilisation")
if accepte_cgu:
    st.success("Merci d'avoir accepté les CGU.")
```

### Sliders

```python
# Slider simple
temperature = st.slider(
    "Température du modèle",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.05,
    help="0 = déterministe, 2 = très créatif",  # infobulle
)

# Slider de plage (sélectionner un intervalle)
age_min, age_max = st.slider(
    "Tranche d'âge",
    min_value=0,
    max_value=100,
    value=(25, 45),  # tuple = mode plage
)
st.write(f"Âges sélectionnés : {age_min} - {age_max} ans")

# Slider de date
import datetime
plage_dates = st.slider(
    "Période d'analyse",
    min_value=datetime.date(2020, 1, 1),
    max_value=datetime.date.today(),
    value=(datetime.date(2023, 1, 1), datetime.date.today()),
)
```

### Upload de fichier

```python
fichier = st.file_uploader(
    "Chargez votre fichier CSV",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
    help="Formats acceptés : CSV, Excel",
)

if fichier is not None:
    # Le fichier est un objet BytesIO
    df = pd.read_csv(fichier)
    st.write(f"Fichier chargé : **{fichier.name}** ({len(df)} lignes)")
    st.dataframe(df.head())
```

### Boutons et actions

```python
# Bouton simple
if st.button("Lancer l'analyse", type="primary"):
    with st.spinner("Analyse en cours..."):
        import time
        time.sleep(2)  # simuler une opération longue
    st.success("Analyse terminée !")

# Bouton de téléchargement
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Télécharger les résultats (CSV)",
    data=csv_data,
    file_name="resultats.csv",
    mime="text/csv",
)
```

## La barre latérale (`st.sidebar`)

La sidebar est idéale pour les filtres, les paramètres, et la navigation :

```python
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Contenu de la sidebar
with st.sidebar:
    st.header("Filtres")

    pays_selectionne = st.selectbox(
        "Pays",
        options=["Tous", "France", "Belgique", "Suisse"],
    )

    annee = st.slider("Année", 2020, 2024, 2023)

    st.markdown("---")
    st.caption("Application v1.0.0")

# Contenu principal
st.title("Dashboard Principal")
st.write(f"Affichage pour : {pays_selectionne} — {annee}")
```

On peut aussi utiliser `st.sidebar.` comme préfixe :

```python
st.sidebar.title("Configuration")
st.sidebar.selectbox("Modèle", ["GPT-4", "Claude", "Mistral"])
```

## Colonnes et mise en page

```python
import streamlit as st

# Deux colonnes égales
col1, col2 = st.columns(2)

with col1:
    st.header("Colonne gauche")
    st.write("Contenu gauche...")

with col2:
    st.header("Colonne droite")
    st.write("Contenu droite...")

# Colonnes avec proportions
col_large, col_petite = st.columns([3, 1])  # ratio 3:1

# Trois colonnes
c1, c2, c3 = st.columns(3)
c1.metric("Métrique 1", "42")
c2.metric("Métrique 2", "87%")
c3.metric("Métrique 3", "1.2k")
```

## Onglets

```python
import streamlit as st

onglet1, onglet2, onglet3 = st.tabs(["Données", "Graphiques", "Modèle"])

with onglet1:
    st.write("Contenu de l'onglet Données")
    st.dataframe(pd.DataFrame({"A": [1, 2, 3]}))

with onglet2:
    st.write("Contenu de l'onglet Graphiques")
    st.line_chart([1, 2, 3, 2, 4, 3])

with onglet3:
    st.write("Contenu de l'onglet Modèle")
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application complète avec sidebar, colonnes et onglets — naviguer entre les onglets et modifier les filtres de la sidebar
> **Expliquer :** Montrer comment les filtres de la sidebar influencent le contenu principal. Cliquer sur les onglets pour naviguer. Expliquer que la sidebar est idéale pour les paramètres globaux (filtres de date, sélection de pays, choix du modèle) qui s'appliquent à toute la page.
---

## Messages d'état

```python
st.success("Opération réussie ! Le modèle a été entraîné.")
st.error("Erreur : impossible de charger le fichier.")
st.warning("Attention : certaines valeurs manquantes ont été ignorées.")
st.info("Information : les données ont été mises en cache.")

# Spinner pendant une opération longue
with st.spinner("Chargement en cours..."):
    import time
    time.sleep(2)
st.write("Chargement terminé !")

# Barre de progression
import time
barre = st.progress(0, text="Traitement en cours...")
for i in range(100):
    time.sleep(0.01)
    barre.progress(i + 1, text=f"Traitement en cours... {i+1}%")
barre.empty()  # supprimer la barre une fois terminé
st.success("Traitement terminé !")
```

## Résumé du chapitre

- `st.write` gère automatiquement la plupart des types Python (texte, DataFrame, dict, graphiques)
- `st.dataframe` est le composant recommandé pour les tableaux interactifs avec `column_config`
- `st.metric` affiche des KPIs avec delta et couleur automatique
- `st.plotly_chart` est le meilleur choix pour des graphiques interactifs
- La sidebar (`st.sidebar`) est idéale pour les filtres et paramètres globaux
- `st.columns`, `st.tabs` et `st.expander` organisent la mise en page
- Les composants d'interaction (`st.slider`, `st.selectbox`, `st.file_uploader`) retournent directement la valeur sélectionnée

**Prochain chapitre :** gérer l'état de session et les formulaires pour des applications plus complexes.
