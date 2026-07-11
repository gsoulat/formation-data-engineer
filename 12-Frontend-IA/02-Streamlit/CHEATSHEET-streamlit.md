# Cheatsheet Streamlit

## Installation & lancement

```bash
pip install streamlit          # installation
uv add streamlit               # avec uv
streamlit run app.py           # lancer l'application
streamlit run app.py --server.port 8502  # port personnalisé
```

## Configuration de la page

```python
import streamlit as st

# DOIT être le premier appel st.*
st.set_page_config(
    page_title="Mon App",
    page_icon="📊",            # emoji ou chemin image
    layout="wide",             # "centered" ou "wide"
    initial_sidebar_state="expanded",  # "expanded", "collapsed", "auto"
)
```

## Texte et affichage

```python
st.title("Titre (h1)")
st.header("En-tête (h2)")
st.subheader("Sous-en-tête (h3)")
st.write("Texte / Markdown / DataFrame / dict — auto-détection")
st.markdown("**Gras**, *italique*, `code`, [lien](url)")
st.text("Monospace, pas de Markdown")
st.caption("Petite légende")
st.code("print('hello')", language="python")
st.latex(r"E = mc^2")
st.divider()                   # ligne horizontale
st.empty()                     # placeholder réutilisable
```

## Données

```python
st.dataframe(df, use_container_width=True, height=300)
st.table(df)                   # tableau statique
st.metric("CA", "42 000 €", "+5%", delta_color="normal")
st.json({"clé": "valeur"})
```

## Graphiques

```python
st.line_chart(df)              # courbe
st.bar_chart(df)               # barres
st.scatter_chart(df, x="col1", y="col2")
st.area_chart(df)

import plotly.express as px
fig = px.scatter(df, x="x", y="y", color="groupe")
st.plotly_chart(fig, use_container_width=True)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3])
st.pyplot(fig)
plt.close(fig)
```

## Composants d'interaction

```python
# Saisie
texte = st.text_input("Label", value="", placeholder="...")
zone = st.text_area("Label", height=150)
nombre = st.number_input("Label", min_value=0, max_value=100, value=25, step=1)

# Sélection
option = st.selectbox("Label", options=["A", "B", "C"], index=0)
choix = st.multiselect("Label", options=["A", "B", "C"], default=["A"])
bouton = st.radio("Label", options=["Oui", "Non"], horizontal=True)
case = st.checkbox("Activer", value=False)

# Sliders
val = st.slider("Label", min_value=0, max_value=100, value=50, step=1)
debut, fin = st.slider("Plage", 0, 100, (20, 80))  # tuple = plage

# Fichier
fichier = st.file_uploader("Label", type=["csv", "xlsx"])
if fichier:
    df = pd.read_csv(fichier)

# Boutons
if st.button("Cliquer", type="primary"):   # type="primary" ou "secondary"
    ...

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Télécharger", csv, "fichier.csv", "text/csv")
```

## Mise en page

```python
# Colonnes
col1, col2, col3 = st.columns(3)
col1, col2 = st.columns([3, 1])  # proportions
with col1:
    st.write("...")

# Sidebar
with st.sidebar:
    st.header("Filtres")
    val = st.slider(...)
# ou : st.sidebar.write(...)

# Onglets
ong1, ong2, ong3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
with ong1:
    st.write("...")

# Accordéon
with st.expander("Détails", expanded=False):
    st.write("Contenu masqué par défaut")
```

## Multi-pages

```
app.py
pages/
├── 1_Page_Un.py
├── 2_Page_Deux.py
└── 3_Page_Trois.py
```

## État de session

```python
# Initialisation
if "compteur" not in st.session_state:
    st.session_state.compteur = 0

# Lecture
val = st.session_state.compteur
val = st.session_state["compteur"]  # équivalent

# Modification
st.session_state.compteur += 1
st.session_state["compteur"] = 0

# Lier un widget à session_state
st.slider("Label", 0, 100, 50, key="mon_slider")
# -> st.session_state.mon_slider == valeur du slider
```

## Callbacks

```python
def mon_callback():
    st.session_state.resultat = st.session_state.ma_saisie.upper()

st.text_input("Texte", key="ma_saisie", on_change=mon_callback)
st.button("Cliquer", on_click=mon_callback)

# Avec arguments
def incrementer(pas):
    st.session_state.compteur += pas

st.button("+10", on_click=incrementer, args=(10,))
```

## Formulaires

```python
with st.form("mon_form"):
    val1 = st.text_input("Nom")
    val2 = st.slider("Valeur", 0, 100, 50)
    soumis = st.form_submit_button("Envoyer", type="primary")

if soumis:
    st.write(f"Nom : {val1}, Valeur : {val2}")
```

## Cache

```python
# Données sérialisables (DataFrame, dict, liste...)
@st.cache_data
def charger_donnees():
    return pd.read_csv("donnees.csv")

@st.cache_data(ttl=3600)  # expire après 1h
def appel_api(endpoint):
    return requests.get(endpoint).json()

# Ressources partagées (connexion DB, modèle ML, client API)
@st.cache_resource
def get_db_engine():
    return create_engine("postgresql://...")

@st.cache_resource
def charger_modele():
    return joblib.load("model.pkl")
```

## Messages d'état

```python
st.success("Opération réussie !")
st.error("Une erreur s'est produite.")
st.warning("Attention !")
st.info("Information.")

with st.spinner("Chargement..."):
    time.sleep(2)

barre = st.progress(0)
for i in range(100):
    barre.progress(i + 1)
barre.empty()
```

## Chat

```python
# Afficher un message
with st.chat_message("user"):
    st.markdown("Message de l'utilisateur")

with st.chat_message("assistant"):
    st.markdown("Réponse de l'assistant")

# Zone de saisie (fixée en bas de page)
if prompt := st.chat_input("Votre message..."):
    # traiter prompt

# Streaming (avec OpenAI)
stream = client.chat.completions.create(model=..., messages=..., stream=True)
reponse = st.write_stream(
    (chunk.choices[0].delta.content or "" for chunk in stream)
)
```

## Pattern chatbot complet

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # streaming ou réponse directe
        reponse = "..."
        st.markdown(reponse)

    st.session_state.messages.append({"role": "assistant", "content": reponse})
```

## Contrôle du flux

```python
st.stop()       # interrompt l'exécution ici (si filtres vides, etc.)
st.rerun()      # force la réexécution immédiate du script
```

## Thème (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## Export Excel

```python
import io
import pandas as pd

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    return buf.getvalue()

st.download_button(
    "Excel",
    data=to_excel(df),
    file_name="export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
```
