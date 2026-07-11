# 04 — Dashboard de données avec Pandas et Plotly

## Vue d'ensemble

Ce chapitre est entièrement pratique : nous construisons un **dashboard de ventes e-commerce** complet, étape par étape. À la fin, vous aurez une application réelle avec filtres, KPIs, graphiques interactifs, et export de données.

## Le dataset : ventes e-commerce

Commençons par créer des données réalistes pour notre dashboard :

```python
# generate_data.py — exécuter une fois pour créer le dataset
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# Paramètres
nb_commandes = 2000
categories = ["Électronique", "Vêtements", "Livres", "Maison & Jardin", "Sport"]
pays = ["France", "Belgique", "Suisse", "Luxembourg", "Canada"]
statuts = ["Livré", "En cours", "Annulé", "Remboursé"]

# Générer les commandes
commandes = []
date_debut = datetime(2023, 1, 1)
for i in range(nb_commandes):
    date = date_debut + timedelta(days=random.randint(0, 364))
    categorie = random.choice(categories)

    # Prix selon catégorie
    prix_base = {"Électronique": 200, "Vêtements": 60, "Livres": 20,
                 "Maison & Jardin": 80, "Sport": 90}
    prix = round(prix_base[categorie] * random.uniform(0.5, 3.0), 2)

    commandes.append({
        "id_commande": f"CMD-{i+1:05d}",
        "date": date,
        "categorie": categorie,
        "pays": random.choice(pays),
        "montant": prix,
        "quantite": random.randint(1, 5),
        "statut": random.choices(statuts, weights=[60, 25, 10, 5])[0],
        "client_id": f"CLI-{random.randint(1, 500):04d}",
    })

df = pd.DataFrame(commandes)
df.to_csv("ventes_ecommerce.csv", index=False)
print(f"Dataset créé : {len(df)} commandes")
```

## Structure du dashboard

```
dashboard/
├── app.py                  # application principale
├── pages/
│   ├── 1_Vue_Generale.py
│   ├── 2_Analyse_Produits.py
│   └── 3_Analyse_Clients.py
├── data/
│   └── ventes_ecommerce.csv
└── utils/
    ├── __init__.py
    └── data_loader.py
```

## Module utilitaire : chargement des données

```python
# utils/data_loader.py
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def charger_donnees(chemin: str = "data/ventes_ecommerce.csv") -> pd.DataFrame:
    """Charge et prépare le dataset."""
    df = pd.read_csv(chemin, parse_dates=["date"])

    # Colonnes dérivées
    df["annee"] = df["date"].dt.year
    df["mois"] = df["date"].dt.month
    df["mois_nom"] = df["date"].dt.strftime("%B")
    df["semaine"] = df["date"].dt.isocalendar().week
    df["chiffre_affaires"] = df["montant"] * df["quantite"]

    return df

def filtrer_donnees(
    df: pd.DataFrame,
    categories: list,
    pays: list,
    date_debut,
    date_fin,
    statuts: list,
) -> pd.DataFrame:
    """Applique les filtres de la sidebar."""
    masque = (
        (df["categorie"].isin(categories)) &
        (df["pays"].isin(pays)) &
        (df["date"] >= pd.Timestamp(date_debut)) &
        (df["date"] <= pd.Timestamp(date_fin)) &
        (df["statut"].isin(statuts))
    )
    return df[masque].copy()
```

## Page principale et sidebar de filtres

```python
# app.py
import streamlit as st
import pandas as pd
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import charger_donnees, filtrer_donnees

st.set_page_config(
    page_title="Dashboard Ventes E-commerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Chargement des données (cachées)
df_complet = charger_donnees()

# ===================== SIDEBAR : FILTRES =====================
with st.sidebar:
    st.title("🔍 Filtres")
    st.markdown("---")

    # Filtre date
    date_min = df_complet["date"].min().date()
    date_max = df_complet["date"].max().date()
    date_debut, date_fin = st.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    # Filtre catégories
    toutes_categories = sorted(df_complet["categorie"].unique())
    categories = st.multiselect(
        "Catégories",
        options=toutes_categories,
        default=toutes_categories,
    )

    # Filtre pays
    tous_pays = sorted(df_complet["pays"].unique())
    pays = st.multiselect(
        "Pays",
        options=tous_pays,
        default=tous_pays,
    )

    # Filtre statuts
    tous_statuts = sorted(df_complet["statut"].unique())
    statuts = st.multiselect(
        "Statuts",
        options=tous_statuts,
        default=["Livré", "En cours"],
    )

    st.markdown("---")
    st.caption(f"Données mises à jour : {date_max}")

# Appliquer les filtres
if not categories or not pays or not statuts:
    st.warning("Sélectionnez au moins une catégorie, un pays, et un statut.")
    st.stop()

df = filtrer_donnees(df_complet, categories, pays, date_debut, date_fin, statuts)

# ===================== PAGE PRINCIPALE =====================
st.title("Dashboard Ventes E-commerce 🛒")
st.caption(f"{len(df):,} commandes affichées sur {len(df_complet):,} au total")

# ===================== KPIs =====================
ca_total = df["chiffre_affaires"].sum()
ca_moyen = df["chiffre_affaires"].mean()
nb_commandes = len(df)
nb_clients = df["client_id"].nunique()

# Calcul des deltas (vs période précédente)
duree = (date_fin - date_debut).days
date_debut_precedent = date_debut - datetime.timedelta(days=duree)
df_precedent = filtrer_donnees(
    df_complet, categories, pays,
    date_debut_precedent, date_debut, statuts
)
ca_precedent = df_precedent["chiffre_affaires"].sum()
delta_ca = ca_total - ca_precedent

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires", f"{ca_total:,.0f} €", f"{delta_ca:+,.0f} €")
col2.metric("Panier moyen", f"{ca_moyen:.2f} €")
col3.metric("Commandes", f"{nb_commandes:,}")
col4.metric("Clients uniques", f"{nb_clients:,}")
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Dashboard avec les KPIs affichés, modifier les filtres de la sidebar et montrer la mise à jour des métriques
> **Expliquer :** Changer la période pour montrer que les deltas des KPIs se recalculent automatiquement. Expliquer le calcul des deltas : on compare avec la même durée précédant la période sélectionnée. Montrer que `st.stop()` interrompt l'exécution proprement quand les filtres sont vides.
---

## Graphiques d'analyse temporelle

```python
# Évolution mensuelle du CA
import plotly.express as px
import plotly.graph_objects as go

st.markdown("---")
st.header("Évolution du chiffre d'affaires")

df_mensuel = (
    df.groupby(["annee", "mois"])
    .agg(ca=("chiffre_affaires", "sum"), nb=("id_commande", "count"))
    .reset_index()
)
df_mensuel["periode"] = pd.to_datetime(
    df_mensuel[["annee", "mois"]].assign(day=1)
)

col_graph, col_options = st.columns([4, 1])

with col_options:
    metrique = st.radio("Métrique", ["Chiffre d'affaires", "Nombre de commandes"])
    afficher_moyenne = st.checkbox("Afficher la moyenne mobile", value=True)

with col_graph:
    y_col = "ca" if metrique == "Chiffre d'affaires" else "nb"
    y_label = "CA (€)" if metrique == "Chiffre d'affaires" else "Commandes"

    fig = px.line(
        df_mensuel,
        x="periode",
        y=y_col,
        title=f"Évolution mensuelle — {metrique}",
        labels={"periode": "Période", y_col: y_label},
        markers=True,
    )

    if afficher_moyenne:
        df_mensuel["moyenne_mobile"] = df_mensuel[y_col].rolling(3, center=True).mean()
        fig.add_scatter(
            x=df_mensuel["periode"],
            y=df_mensuel["moyenne_mobile"],
            mode="lines",
            name="Moyenne mobile (3 mois)",
            line=dict(dash="dash", color="red"),
        )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
```

## Graphiques de répartition

```python
st.markdown("---")
st.header("Répartition par catégorie et pays")

col_gauche, col_droite = st.columns(2)

with col_gauche:
    # Camembert des catégories
    df_cat = df.groupby("categorie")["chiffre_affaires"].sum().reset_index()

    fig_pie = px.pie(
        df_cat,
        values="chiffre_affaires",
        names="categorie",
        title="Part du CA par catégorie",
        hole=0.4,  # donut chart
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_droite:
    # Barres groupées par pays et statut
    df_pays_statut = (
        df.groupby(["pays", "statut"])
        .size()
        .reset_index(name="nb_commandes")
    )

    fig_bar = px.bar(
        df_pays_statut,
        x="pays",
        y="nb_commandes",
        color="statut",
        title="Commandes par pays et statut",
        barmode="group",
        labels={"nb_commandes": "Nombre de commandes", "pays": "Pays"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)
```

## Tableau de données avec export

```python
st.markdown("---")
st.header("Données détaillées")

# Afficher le tableau
st.dataframe(
    df.sort_values("date", ascending=False).head(100),
    use_container_width=True,
    column_config={
        "id_commande": "ID",
        "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "chiffre_affaires": st.column_config.NumberColumn(
            "CA (€)", format="€%.2f"
        ),
        "statut": st.column_config.SelectboxColumn(
            "Statut",
            options=["Livré", "En cours", "Annulé", "Remboursé"],
        ),
    }
)

# Export CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Télécharger les données filtrées (CSV)",
    data=csv,
    file_name=f"ventes_{date_debut}_{date_fin}.csv",
    mime="text/csv",
    use_container_width=True,
)
```

## Heatmap de corrélation

```python
# Page 2 — Analyse produits (pages/2_Analyse_Produits.py)
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_loader import charger_donnees

st.title("Analyse Produits")

df = charger_donnees()

# Distribution des montants par catégorie
st.subheader("Distribution des montants par catégorie")

fig_box = px.box(
    df,
    x="categorie",
    y="montant",
    color="categorie",
    title="Distribution des prix par catégorie",
    points="outliers",  # afficher seulement les outliers
)
st.plotly_chart(fig_box, use_container_width=True)

# Heatmap catégorie x pays
st.subheader("CA moyen : Catégorie × Pays")

pivot = df.pivot_table(
    values="chiffre_affaires",
    index="categorie",
    columns="pays",
    aggfunc="mean",
).round(0)

fig_heat = px.imshow(
    pivot,
    title="CA moyen par catégorie et pays (€)",
    color_continuous_scale="Blues",
    text_auto=True,
    aspect="auto",
)
st.plotly_chart(fig_heat, use_container_width=True)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Navigation entre les deux pages du dashboard (Vue Générale et Analyse Produits), montrer les graphiques interactifs et la heatmap
> **Expliquer :** Montrer la navigation automatique dans la sidebar gauche de Streamlit. Survoler la heatmap pour lire les valeurs. Expliquer le `pivot_table` : chaque cellule est la moyenne du CA pour une combinaison catégorie/pays. C'est un usage classique en analyse de données business.
---

## Résumé du chapitre

- Structurez vos applications en plusieurs pages avec le dossier `pages/`
- Centralisez le chargement et la préparation des données dans un module `utils/` avec `@st.cache_data`
- Appliquez les filtres de la sidebar avec une fonction `filtrer_donnees` dédiée
- `st.stop()` interrompt proprement l'exécution (par exemple si les filtres sont vides)
- Plotly Express (`px`) produit des graphiques interactifs en une ligne
- `st.dataframe` avec `column_config` améliore significativement la lisibilité des tableaux
- `st.download_button` permet d'exporter les données filtrées

**Prochain chapitre :** intégrer un LLM dans Streamlit avec `st.chat_message` et `st.chat_input`.
