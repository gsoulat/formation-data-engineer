# 01 — Introduction à Streamlit

## Qu'est-ce que Streamlit ?

Streamlit est un framework Python open source créé en 2018, racheté par Snowflake en 2022. Son objectif est de permettre aux data scientists et ingénieurs de créer des **applications web de données** sans apprendre le développement web.

La philosophie fondamentale est simple : **votre script Python est votre application**. Streamlit réexécute votre script de haut en bas à chaque interaction de l'utilisateur. Cette approche, appelée "script model" ou "reactive model", est radicalement différente des frameworks web traditionnels.

### Le problème qu'il résout

En data science, on produit souvent des analyses sous forme de notebooks Jupyter ou de scripts Python. Partager ces résultats avec des non-techniciens est compliqué : ils ne peuvent pas exécuter votre code. Avec Streamlit, votre analyse devient une application web interactive en quelques minutes.

### Comparaison avec les alternatives

| Framework | Cible | Cas d'usage |
|-----------|-------|-------------|
| Streamlit | Data Scientists | Dashboards, exploration, apps IA |
| Gradio | ML Engineers | Démos de modèles, chatbots |
| Dash (Plotly) | Data Analysts | Dashboards complexes, KPIs |
| Flask/FastAPI | Développeurs | APIs, applications complètes |

## Installation

```bash
# Avec pip
pip install streamlit

# Avec uv (recommandé)
uv add streamlit

# Packages complémentaires utiles
pip install pandas plotly scikit-learn

# Vérifier l'installation
streamlit --version
```

## Première application

Créez un fichier `app.py` :

```python
import streamlit as st

st.title("Ma première application Streamlit")
st.write("Bienvenue ! Cette application a été créée avec Streamlit.")

nom = st.text_input("Quel est votre prénom ?")
if nom:
    st.write(f"Bonjour, **{nom}** ! Ravi de vous rencontrer.")
    st.balloons()  # animation de ballons 🎈
```

Lancez l'application :

```bash
streamlit run app.py
```

Streamlit ouvre automatiquement votre navigateur sur `http://localhost:8501`.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Lancement de `streamlit run app.py` dans le terminal, ouverture automatique du navigateur, saisie d'un prénom et affichage du message de bienvenue avec l'animation de ballons
> **Expliquer :** Montrer que le navigateur s'ouvre automatiquement. Taper un prénom et montrer la réaction immédiate de l'interface. Expliquer que Streamlit réexécute tout le script à chaque saisie. Ce comportement est différent de ce qu'on attend — il n'y a pas de bouton "Submit" nécessaire par défaut.
---

## `st.run` et la configuration de la page

La fonction `st.set_page_config` doit être le **premier appel Streamlit** de votre script. Elle configure le titre, l'icône, et la mise en page :

```python
import streamlit as st

# DOIT être en premier, avant tout autre appel st.*
st.set_page_config(
    page_title="Mon Dashboard",        # titre dans l'onglet du navigateur
    page_icon="📊",                    # emoji ou chemin vers une image
    layout="wide",                     # "centered" (défaut) ou "wide"
    initial_sidebar_state="expanded",  # "expanded", "collapsed", "auto"
    menu_items={
        "Get Help": "https://mon-site.com/aide",
        "Report a bug": "https://github.com/mon-repo/issues",
        "About": "# Mon Application\nVersion 1.0.0",
    }
)

st.title("Dashboard Principal")
st.write("Le reste de votre application...")
```

> **Erreur fréquente :** Appeler `st.set_page_config` après d'autres commandes Streamlit provoque une erreur. Mettez-le toujours en premier.

## Le modèle d'exécution de Streamlit

Comprendre le modèle d'exécution est fondamental pour éviter les bugs et les lenteurs.

```python
import streamlit as st
import time

st.write("1. Ce code s'exécute à chaque interaction")

valeur = st.slider("Choisissez une valeur", 0, 100, 50)

st.write(f"2. La valeur est {valeur}")

# Ce bloc s'exécute aussi à chaque fois que le slider bouge
time.sleep(0.1)  # Si vous avez une opération lente ICI, l'app sera lente

st.write("3. Fin du script")
```

Quand l'utilisateur bouge le slider :
1. Streamlit réexécute le script **depuis le début**
2. Les résultats précédents sont effacés
3. Les nouveaux résultats sont affichés

C'est pour ça que les opérations lentes (chargement de données, entraînement de modèles) doivent être **cachées** avec `@st.cache_data` (voir chapitre 03).

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Application simple avec un slider et un `st.write` qui affiche la valeur, montrer la mise à jour en temps réel
> **Expliquer :** Bouger le slider lentement et montrer que la valeur affichée suit en temps réel. Expliquer que ce comportement vient de la réexécution complète du script. C'est la force de Streamlit : simple à comprendre, mais il faut éviter les opérations lentes dans le flux principal.
---

## Structure d'une application multi-pages

Streamlit supporte nativement les applications multi-pages. Il suffit de créer un dossier `pages/` :

```
mon-app/
├── app.py              # page principale (affiché en premier)
├── pages/
│   ├── 1_Accueil.py    # le préfixe numérique détermine l'ordre
│   ├── 2_Dashboard.py
│   ├── 3_Modele.py
│   └── 4_A_propos.py
└── utils.py            # fonctions partagées
```

```python
# app.py
import streamlit as st

st.set_page_config(page_title="Mon App Data", page_icon="🔬", layout="wide")

st.title("Bienvenue sur Mon Application Data")
st.write("Utilisez le menu de gauche pour naviguer.")
```

```python
# pages/2_Dashboard.py
import streamlit as st

# Pas besoin de set_page_config ici, il est hérité
st.title("Dashboard")
st.write("Contenu du dashboard...")
```

Streamlit génère automatiquement un menu de navigation dans la barre latérale avec les noms de vos fichiers (le préfixe numérique et les underscores sont remplacés par des espaces).

## Rechargement automatique

Streamlit surveille les modifications de vos fichiers et recharge automatiquement l'application :

```bash
# Lancement standard (rechargement automatique inclus)
streamlit run app.py

# Options utiles
streamlit run app.py --server.port 8502    # changer le port
streamlit run app.py --server.headless true  # sans ouvrir le navigateur (pour Docker)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Modifier le titre de l'application dans `app.py` et sauvegarder, montrer le rechargement automatique dans le navigateur
> **Expliquer :** Un bouton "Rerun" apparaît en haut à droite quand le fichier change. On peut cliquer dessus ou configurer le rechargement automatique. En développement, le rechargement automatique est activé par défaut. Montrer comment le désactiver dans les paramètres si besoin.
---

## Configuration avec `.streamlit/config.toml`

Pour personnaliser le comportement de Streamlit dans un projet :

```toml
# .streamlit/config.toml

[server]
port = 8501
headless = false
runOnSave = true

[theme]
primaryColor = "#1f77b4"       # couleur principale (boutons, sliders)
backgroundColor = "#ffffff"    # fond de la page
secondaryBackgroundColor = "#f0f2f6"  # fond de la sidebar
textColor = "#262730"          # couleur du texte
font = "sans serif"            # "sans serif", "serif", "monospace"

[browser]
gatherUsageStats = false       # désactiver la télémétrie
```

Exemple de thème sombre personnalisé :

```toml
[theme]
primaryColor = "#ff6b35"
backgroundColor = "#1a1a2e"
secondaryBackgroundColor = "#16213e"
textColor = "#eaeaea"
```

## Résumé du chapitre

- Streamlit transforme un script Python en application web en une commande : `streamlit run app.py`
- `st.set_page_config` doit être le premier appel — il configure titre, icône, et mise en page
- Le modèle d'exécution réexécute tout le script à chaque interaction
- Les applications multi-pages s'organisent dans un dossier `pages/`
- Le rechargement automatique est activé par défaut en développement
- `.streamlit/config.toml` permet de personnaliser le thème et les paramètres serveur

**Prochain chapitre :** explorer tous les composants d'affichage et d'interaction disponibles.
