# 03 — État de session, callbacks, formulaires et cache

## Le problème du modèle d'exécution

Rappel : Streamlit réexécute votre script **de haut en bas** à chaque interaction. Cela crée un problème : comment conserver des données entre les réexécutions ?

Sans gestion d'état, ce code est cassé :

```python
import streamlit as st

compteur = 0  # réinitialisé à 0 à chaque réexécution !

if st.button("Incrémenter"):
    compteur += 1  # ne fonctionne pas comme attendu

st.write(f"Compteur : {compteur}")  # affiche toujours 0 ou 1
```

La solution : `st.session_state`.

## `st.session_state`

`st.session_state` est un dictionnaire (ou un objet avec accès par attribut) qui **persiste entre les réexécutions** pour la session de l'utilisateur courant.

```python
import streamlit as st

# Initialiser l'état si pas encore défini
if "compteur" not in st.session_state:
    st.session_state.compteur = 0

# Modifier l'état
if st.button("Incrémenter"):
    st.session_state.compteur += 1

if st.button("Réinitialiser"):
    st.session_state.compteur = 0

st.write(f"Compteur : {st.session_state.compteur}")
```

### Deux syntaxes équivalentes

```python
# Par attribut (recommandé pour sa lisibilité)
st.session_state.ma_variable = "valeur"
print(st.session_state.ma_variable)

# Par clé de dictionnaire
st.session_state["ma_variable"] = "valeur"
print(st.session_state["ma_variable"])
```

### Bonne pratique : initialisation en haut du script

```python
import streamlit as st

# === Initialisation de l'état au début du script ===
def initialiser_etat():
    defaults = {
        "historique_messages": [],
        "modele_selectionne": "gpt-4o-mini",
        "nb_recherches": 0,
        "utilisateur_connecte": False,
        "donnees_chargees": None,
    }
    for cle, valeur in defaults.items():
        if cle not in st.session_state:
            st.session_state[cle] = valeur

initialiser_etat()

# Reste de l'application...
st.write(f"Modèle : {st.session_state.modele_selectionne}")
```

## Callbacks

Les callbacks permettent d'exécuter une fonction **avant** la réexécution du script principal. C'est utile pour modifier `st.session_state` en réponse à une interaction.

```python
import streamlit as st

if "texte_majuscule" not in st.session_state:
    st.session_state.texte_majuscule = ""

def mettre_en_majuscules():
    """Callback appelé quand le bouton est cliqué."""
    # On peut accéder à l'état du text_input via son key
    st.session_state.texte_majuscule = st.session_state.input_texte.upper()

st.text_input(
    "Entrez un texte",
    key="input_texte",          # clé qui lie ce widget à session_state
    on_change=mettre_en_majuscules,  # appelé à chaque changement
)

st.write(f"Majuscules : {st.session_state.texte_majuscule}")
```

### `key` — lier un widget à `session_state`

Quand vous donnez une `key` à un widget, sa valeur est automatiquement synchronisée avec `st.session_state` :

```python
import streamlit as st

# La valeur du slider est accessible via st.session_state.temperature
temperature = st.slider("Température", 0.0, 2.0, 0.7, key="temperature")

# Ces deux sont équivalents après la ligne ci-dessus :
# temperature == st.session_state.temperature  -> True
st.write(f"Valeur via variable : {temperature}")
st.write(f"Valeur via session_state : {st.session_state.temperature}")
```

### Exemple avec callback sur bouton

```python
import streamlit as st

if "likes" not in st.session_state:
    st.session_state.likes = 0

def aimer():
    st.session_state.likes += 1

st.button("J'aime ❤️", on_click=aimer)
st.write(f"{st.session_state.likes} personne(s) aiment cette application.")
```

## Formulaires

Les formulaires regroupent plusieurs widgets et n'envoient leur valeur qu'au clic sur le bouton Submit. Sans formulaire, chaque interaction (bouger un slider, taper un caractère) déclenche une réexécution. Avec un formulaire, la réexécution n'a lieu qu'à la soumission.

```python
import streamlit as st

with st.form("formulaire_recherche"):
    st.subheader("Paramètres de recherche")

    mot_cle = st.text_input("Mot-clé")
    categorie = st.selectbox("Catégorie", ["Tous", "Tech", "Science", "Art"])
    date_debut, date_fin = st.date_input(
        "Période",
        value=(datetime.date(2023, 1, 1), datetime.date.today()),
    )
    nb_resultats = st.slider("Nombre de résultats", 5, 100, 20)

    # Le bouton Submit est OBLIGATOIRE dans un formulaire
    soumis = st.form_submit_button("Rechercher", type="primary")

if soumis:
    st.write(f"Recherche : '{mot_cle}' dans '{categorie}'")
    st.write(f"Période : {date_debut} → {date_fin}, max {nb_resultats} résultats")
```

### Quand utiliser un formulaire ?

- Paramètres de recherche avec plusieurs filtres
- Formulaire de saisie (création d'un enregistrement)
- Configuration d'un modèle ML avant lancement

### Quand ne pas utiliser un formulaire ?

- Filtres qui doivent mettre à jour l'affichage en temps réel (préférer des widgets directs)
- Slider de température d'un LLM (l'utilisateur veut voir l'effet immédiatement)

## `@st.cache_data` — Mise en cache des données

Sans cache, les opérations lentes (lecture de fichier, requête SQL, téléchargement) s'exécutent à chaque réexécution du script :

```python
import streamlit as st
import pandas as pd

# SANS cache : rechargé à chaque interaction !
def charger_donnees():
    return pd.read_csv("https://exemple.com/gros-fichier.csv")  # lent

df = charger_donnees()  # 3 secondes à chaque clic
```

Avec `@st.cache_data`, la fonction n'est exécutée qu'une fois (ou quand ses arguments changent) :

```python
import streamlit as st
import pandas as pd

@st.cache_data
def charger_donnees():
    """Chargée une seule fois, résultat mis en cache."""
    return pd.read_csv("https://exemple.com/gros-fichier.csv")

@st.cache_data(ttl=3600)  # expire après 1 heure
def charger_depuis_api(endpoint: str) -> dict:
    import requests
    return requests.get(endpoint).json()

@st.cache_data(max_entries=10)  # garder au maximum 10 résultats en cache
def traiter_fichier(nom_fichier: str) -> pd.DataFrame:
    return pd.read_csv(nom_fichier)

# Ces appels utilisent le cache si disponible
df = charger_donnees()
st.dataframe(df)
```

### `@st.cache_resource` — Pour les ressources partagées

`@st.cache_resource` est utilisé pour les ressources qui ne doivent exister qu'en **une seule instance** partagée entre toutes les sessions (connexions DB, modèles ML, clients API) :

```python
import streamlit as st
from sqlalchemy import create_engine
import joblib
from openai import OpenAI

@st.cache_resource
def get_database_connection():
    """Une seule connexion partagée entre toutes les sessions."""
    engine = create_engine("postgresql://user:pass@localhost/db")
    return engine

@st.cache_resource
def charger_modele_ml():
    """Le modèle ML est chargé une fois, partagé entre tous les utilisateurs."""
    return joblib.load("model.pkl")

@st.cache_resource
def get_openai_client():
    """Un seul client OpenAI pour toute l'application."""
    import os
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Usage
engine = get_database_connection()
modele = charger_modele_ml()
client = get_openai_client()
```

### Différence `@st.cache_data` vs `@st.cache_resource`

| `@st.cache_data` | `@st.cache_resource` |
|-------------------|----------------------|
| Données sérialisables (DataFrame, dict, liste) | Objets non-sérialisables (connexions, modèles) |
| Copie par session | Instance partagée entre toutes les sessions |
| Peut avoir un TTL | Pas de TTL par défaut |
| Exemples : CSV, JSON, résultats de calculs | Exemples : DB engine, modèle ML, client API |

## Exemple complet — Application avec état

```python
import streamlit as st
import pandas as pd
import datetime

# === Configuration ===
st.set_page_config(page_title="Gestionnaire de tâches", layout="wide")

# === Initialisation de l'état ===
if "taches" not in st.session_state:
    st.session_state.taches = []

if "nb_taches_completes" not in st.session_state:
    st.session_state.nb_taches_completes = 0

# === Callbacks ===
def ajouter_tache():
    if st.session_state.nouvelle_tache.strip():
        st.session_state.taches.append({
            "titre": st.session_state.nouvelle_tache,
            "date": datetime.date.today().isoformat(),
            "complete": False,
        })
        st.session_state.nouvelle_tache = ""  # vider le champ

def supprimer_taches_completes():
    avant = len(st.session_state.taches)
    st.session_state.taches = [t for t in st.session_state.taches if not t["complete"]]
    apres = len(st.session_state.taches)
    st.session_state.nb_taches_completes += (avant - apres)

# === Interface ===
st.title("Gestionnaire de tâches")

col1, col2, col3 = st.columns(3)
col1.metric("Tâches en cours", len([t for t in st.session_state.taches if not t["complete"]]))
col2.metric("Tâches complètes", len([t for t in st.session_state.taches if t["complete"]]))
col3.metric("Total archivées", st.session_state.nb_taches_completes)

st.divider()

# Formulaire d'ajout
with st.form("ajout_tache", clear_on_submit=True):
    st.text_input("Nouvelle tâche", key="nouvelle_tache", placeholder="Décrire la tâche...")
    st.form_submit_button("Ajouter", on_click=ajouter_tache, type="primary")

# Liste des tâches
if not st.session_state.taches:
    st.info("Aucune tâche. Ajoutez-en une ci-dessus.")
else:
    for i, tache in enumerate(st.session_state.taches):
        col_check, col_titre, col_date = st.columns([1, 6, 2])
        tache["complete"] = col_check.checkbox("", tache["complete"], key=f"check_{i}")
        style = "~~" if tache["complete"] else ""
        col_titre.write(f"{style}{tache['titre']}{style}")
        col_date.caption(tache["date"])

    if any(t["complete"] for t in st.session_state.taches):
        st.button("Archiver les tâches complètes", on_click=supprimer_taches_completes)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Démonstration complète de l'application gestionnaire de tâches — ajouter des tâches, les cocher, les archiver
> **Expliquer :** Montrer que les tâches persistent entre les réexécutions grâce à `session_state`. Expliquer le pattern callback : la fonction `ajouter_tache` est appelée avant la réexécution, ce qui permet de vider le champ (en modifiant `st.session_state.nouvelle_tache = ""`). Sans callback, il serait impossible de vider un champ après soumission.
---

## Résumé du chapitre

- `st.session_state` persiste les données entre les réexécutions pour une session utilisateur
- Toujours initialiser `st.session_state` en haut du script avec un pattern `if "clé" not in st.session_state`
- Les callbacks (`on_click`, `on_change`) s'exécutent avant la réexécution principale
- La `key` d'un widget lie sa valeur à `st.session_state[key]` automatiquement
- `st.form` regroupe plusieurs widgets et n'envoie les valeurs qu'au clic sur Submit
- `@st.cache_data` met en cache les données sérialisables avec TTL optionnel
- `@st.cache_resource` met en cache les ressources partagées (DB, modèles, clients API)

**Prochain chapitre :** construire un vrai dashboard de visualisation de données.
