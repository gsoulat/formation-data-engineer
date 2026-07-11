# Exercice 01 — Dashboard d'exploration de données

## Objectif

Construire un dashboard Streamlit multi-pages complet permettant d'explorer un dataset de votre choix. Le dashboard inclut des filtres, des KPIs, des graphiques interactifs, et une section d'analyse assistée par LLM.

## Prérequis

- Avoir complété les chapitres 01 à 04 du module Streamlit
- Un dataset CSV (idéalement celui de votre brief ou projet)
- Pour la partie bonus : une clé API OpenAI ou Ollama installé localement

## Contexte

Vous êtes Data Analyst dans une entreprise. Votre manager vous demande de créer un dashboard interactif pour que l'équipe métier puisse explorer les données sans écrire une seule ligne de code. L'interface doit être intuitive, rapide, et exportable.

## Dataset recommandé

Si vous n'avez pas de dataset propre, utilisez ce dataset de ventes e-commerce (décrit dans le chapitre 04) :

```python
# generate_data.py — à exécuter une fois
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

nb_lignes = 1500
categories = ["Électronique", "Vêtements", "Livres", "Maison", "Sport", "Beauté"]
regions = ["Île-de-France", "Provence", "Bretagne", "Occitanie", "Normandie", "PACA"]
canaux = ["Web", "Mobile", "Magasin", "Téléphone"]

data = {
    "date": [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
             for _ in range(nb_lignes)],
    "categorie": [random.choice(categories) for _ in range(nb_lignes)],
    "region": [random.choice(regions) for _ in range(nb_lignes)],
    "canal": [random.choice(canaux) for _ in range(nb_lignes)],
    "montant": [round(random.uniform(10, 500), 2) for _ in range(nb_lignes)],
    "quantite": [random.randint(1, 10) for _ in range(nb_lignes)],
    "note_client": [random.choice([1, 2, 3, 4, 4, 4, 5, 5, 5, 5]) for _ in range(nb_lignes)],
    "retour": [random.random() < 0.08 for _ in range(nb_lignes)],  # 8% de retours
}

df = pd.DataFrame(data)
df["chiffre_affaires"] = df["montant"] * df["quantite"]
df.to_csv("data/ventes.csv", index=False)
print(f"Dataset créé : {len(df)} lignes")
```

## Structure attendue

```
mon-dashboard/
├── app.py                        # page d'accueil
├── pages/
│   ├── 1_Vue_Generale.py         # KPIs et graphiques globaux
│   ├── 2_Analyse_Detaillee.py    # exploration par dimension
│   └── 3_Export.py               # export et téléchargement
├── utils/
│   ├── __init__.py
│   └── data_loader.py            # chargement et filtrage
├── data/
│   └── ventes.csv
└── requirements.txt
```

## Partie 1 — Page d'accueil (`app.py`)

La page d'accueil présente le projet et donne des statistiques générales sur le dataset.

```python
import streamlit as st

st.set_page_config(
    page_title="Dashboard Ventes",
    page_icon="📊",
    layout="wide",
)

# TODO : ajouter st.title et st.markdown avec une description du projet

# TODO : charger le dataset avec @st.cache_data
# df = charger_donnees()

# TODO : afficher 4 métriques dans st.columns(4) :
# - Nombre total de commandes
# - Chiffre d'affaires total
# - Note client moyenne (arrondie à 1 décimale)
# - Taux de retour (en %)

# TODO : afficher un aperçu du dataset avec st.dataframe (5 premières lignes)
```

### Critères Partie 1

- [ ] `st.set_page_config` avec titre, icône, et layout wide
- [ ] Les 4 métriques sont affichées dans une ligne de 4 colonnes
- [ ] `@st.cache_data` est utilisé pour le chargement des données
- [ ] L'aperçu du dataset est affiché

## Partie 2 — Vue Générale (`pages/1_Vue_Generale.py`)

Cette page combine une sidebar de filtres et des graphiques.

```python
import streamlit as st
import plotly.express as px

# TODO : Sidebar avec les filtres suivants :
#   - Sélection de la période (date_input avec valeur initiale = tout le dataset)
#   - Multiselect des catégories (toutes sélectionnées par défaut)
#   - Multiselect des régions (toutes sélectionnées par défaut)
#   - Multiselect des canaux (tous sélectionnés par défaut)

# TODO : Appliquer les filtres sur le DataFrame

# TODO : Afficher un indicateur du nombre de lignes filtrées vs total
# Exemple : "1 234 commandes affichées sur 1 500 au total"

# TODO : KPIs dynamiques (mis à jour selon les filtres) :
#   - CA total avec delta vs période précédente
#   - Panier moyen
#   - Commandes

# TODO : Graphique 1 — Évolution du CA par mois (st.line_chart ou px.line)

# TODO : Graphique 2 — Répartition par catégorie (px.pie ou px.bar)

# TODO : Graphique 3 — CA par région (px.bar horizontal)
```

### Critères Partie 2

- [ ] Les filtres de la sidebar modifient tous les graphiques
- [ ] Un indicateur de lignes filtrées est affiché
- [ ] Au moins 3 graphiques avec Plotly
- [ ] Les graphiques ont des titres et des labels lisibles

## Partie 3 — Analyse Détaillée (`pages/2_Analyse_Detaillee.py`)

Page d'exploration plus fine.

```python
import streamlit as st
import plotly.express as px

# TODO : Onglets (st.tabs) avec au moins 3 analyses :
#   - Onglet "Satisfaction" : distribution des notes, note moyenne par catégorie
#   - Onglet "Canaux" : comparaison des canaux (CA, quantité, taux de retour)
#   - Onglet "Temporel" : analyse par jour de semaine ou par mois

# TODO : Dans l'onglet Satisfaction :
#   Histogramme des notes clients avec px.histogram
#   Note moyenne par catégorie avec px.bar (trié par note décroissante)

# TODO : Dans l'onglet Canaux :
#   Tableau récapitulatif avec st.dataframe :
#   canal | nb_commandes | CA_total | CA_moyen | taux_retour
#   Graphique barres groupées canal x métrique

# TODO : Utiliser st.expander pour masquer/afficher les tableaux de données brutes
```

### Critères Partie 3

- [ ] `st.tabs` avec au moins 3 onglets
- [ ] `st.expander` utilisé au moins une fois
- [ ] Les graphiques sont cohérents avec le contenu de l'onglet

## Partie 4 — Export (`pages/3_Export.py`)

Page permettant de filtrer et d'exporter les données.

```python
import streamlit as st
import pandas as pd

# TODO : Formulaire (st.form) avec filtres de sélection
#   On veut pouvoir exporter un sous-ensemble du dataset

# TODO : Après soumission du formulaire :
#   Afficher le tableau filtré avec st.dataframe
#   Afficher le nombre de lignes sélectionnées

# TODO : Bouton de téléchargement CSV (st.download_button)
#   Nom du fichier incluant la date d'export

# TODO : Bonus — bouton de téléchargement Excel
#   Utiliser df.to_excel() avec un BytesIO
```

Pour l'export Excel :

```python
import io
from datetime import date

def convertir_en_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Données")
    return buffer.getvalue()

# Dans votre code :
excel_data = convertir_en_excel(df_filtre)
st.download_button(
    label="Télécharger en Excel",
    data=excel_data,
    file_name=f"export_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
```

### Critères Partie 4

- [ ] `st.form` utilisé pour le formulaire d'export
- [ ] `st.download_button` pour le CSV
- [ ] **Bonus :** export Excel fonctionnel

## Partie 5 — Bonus : Assistant IA

Ajoutez une page `pages/4_Assistant_IA.py` avec un chatbot capable de répondre à des questions sur le dataset (voir chapitre 05).

L'assistant doit :
- Connaître les statistiques du dataset (injectées dans le system prompt)
- Répondre en streaming (`st.write_stream`)
- Permettre de démarrer une nouvelle conversation
- Suggérer 3 questions d'analyse pertinentes au démarrage

## Critères d'évaluation globaux

| Critère | Points |
|---------|--------|
| Structure multi-pages correcte | 2 |
| `@st.cache_data` utilisé pour le chargement | 2 |
| Sidebar avec filtres fonctionnels | 3 |
| Au moins 5 graphiques Plotly pertinents | 4 |
| `st.form` utilisé pour l'export | 2 |
| `st.download_button` CSV fonctionnel | 2 |
| Mise en page soignée (columns, tabs, expander) | 2 |
| `st.metric` avec deltas | 1 |
| **Bonus :** Assistant IA avec streaming | 3 |
| **Bonus :** Export Excel | 1 |
| **Total** | **18 (+4 bonus)** |

## Pour aller plus loin

- Ajouter `@st.cache_data(ttl=300)` pour simuler des données rafraîchies toutes les 5 minutes
- Déployer sur Streamlit Cloud (https://share.streamlit.io) avec votre dépôt GitHub
- Ajouter des graphiques de carte géographique avec `px.choropleth` ou `folium`
- Implémenter une authentification avec `st.secrets` et une liste d'utilisateurs autorisés
