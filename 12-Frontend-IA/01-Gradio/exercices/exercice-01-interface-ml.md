# Exercice 01 — Interface Gradio pour un modèle scikit-learn

## Objectif

Construire une interface Gradio complète autour d'un modèle de classification scikit-learn. L'utilisateur entre les caractéristiques d'une fleur Iris et l'interface affiche la prédiction de l'espèce avec les probabilités par classe.

## Prérequis

- Avoir complété les chapitres 01 et 02 du module Gradio
- Avoir des notions de scikit-learn (module 08 — Machine Learning)

## Contexte

Vous êtes Data Scientist dans une startup de botanique. Votre équipe a entraîné un modèle de classification pour identifier les espèces d'iris à partir de leurs caractéristiques morphologiques. Vous devez créer une interface web permettant aux botanistes de terrain (qui ne savent pas coder) d'utiliser ce modèle depuis leur tablette.

## Partie 1 — Entraîner et sauvegarder le modèle

Créez un fichier `train_model.py` :

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import numpy as np

# Charger les données
iris = load_iris()
X, y = iris.data, iris.target
noms_classes = list(iris.target_names)  # ['setosa', 'versicolor', 'virginica']

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Entraîner
modele = RandomForestClassifier(n_estimators=100, random_state=42)
modele.fit(X_train, y_train)

# Évaluer
y_pred = modele.predict(X_test)
print(classification_report(y_test, y_pred, target_names=noms_classes))

# Sauvegarder
joblib.dump(modele, "iris_model.pkl")
joblib.dump(noms_classes, "iris_classes.pkl")
print("Modèle sauvegardé : iris_model.pkl")
print(f"Accuracy sur le test set : {modele.score(X_test, y_test):.2%}")
```

Lancez le script :

```bash
python train_model.py
```

## Partie 2 — Interface basique avec `gr.Interface`

Créez un fichier `app_v1.py` :

```python
import gradio as gr
import joblib
import numpy as np

# Charger le modèle une seule fois au démarrage
modele = joblib.load("iris_model.pkl")
noms_classes = joblib.load("iris_classes.pkl")

def predire_iris(longueur_sepal, largeur_sepal, longueur_petal, largeur_petal):
    """
    Prédit l'espèce d'iris à partir des 4 mesures morphologiques.
    Retourne : nom de l'espèce prédite (str)
    """
    # TODO : construire un array numpy avec les 4 features
    # TODO : appeler modele.predict()
    # TODO : retourner noms_classes[prediction]
    pass

demo = gr.Interface(
    fn=predire_iris,
    inputs=[
        # TODO : ajouter 4 composants Slider avec des valeurs min/max réalistes
        # Longueur sépale : entre 4.0 et 8.0 cm
        # Largeur sépale : entre 2.0 et 4.5 cm
        # Longueur pétale : entre 1.0 et 7.0 cm
        # Largeur pétale : entre 0.1 et 2.5 cm
    ],
    outputs=gr.Textbox(label="Espèce prédite"),
    title="Classificateur d'Iris",
    description="Entrez les mesures morphologiques pour identifier l'espèce d'iris.",
)

demo.launch()
```

### Critères de réussite Partie 2

- [ ] Les 4 sliders ont des plages de valeurs adaptées aux données Iris
- [ ] La prédiction s'affiche correctement : "setosa", "versicolor" ou "virginica"
- [ ] La valeur par défaut des sliders correspond à un exemple réel (vous pouvez prendre la moyenne)

## Partie 3 — Interface avancée avec probabilités

Créez `app_v2.py` avec `gr.Blocks` pour afficher les probabilités par classe en plus de la prédiction :

```python
import gradio as gr
import joblib
import numpy as np

modele = joblib.load("iris_model.pkl")
noms_classes = joblib.load("iris_classes.pkl")

def predire_avec_probabilites(longueur_sepal, largeur_sepal, longueur_petal, largeur_petal):
    """
    Retourne : (str espèce, dict probabilités)
    Le dict a le format attendu par gr.Label : {"setosa": 0.8, "versicolor": 0.1, ...}
    """
    features = np.array([[longueur_sepal, largeur_sepal, longueur_petal, largeur_petal]])

    # TODO : utiliser modele.predict_proba() pour obtenir les probabilités
    # TODO : construire le dict {nom_classe: proba} pour les 3 classes
    # TODO : identifier la classe avec la plus haute probabilité
    # TODO : retourner (nom_espece, dict_probas)
    pass

with gr.Blocks(title="Classificateur Iris Avancé") as demo:
    gr.Markdown("# Classificateur d'Iris")
    gr.Markdown("Ajustez les paramètres morphologiques pour identifier l'espèce.")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Mesures du sépale")
            # TODO : ajouter slider longueur_sepal
            # TODO : ajouter slider largeur_sepal

            gr.Markdown("### Mesures du pétale")
            # TODO : ajouter slider longueur_petal
            # TODO : ajouter slider largeur_petal

            btn = gr.Button("Classifier", variant="primary")

        with gr.Column():
            gr.Markdown("### Résultat")
            # TODO : gr.Textbox pour le nom de l'espèce
            # TODO : gr.Label pour les probabilités (num_top_classes=3)

    # TODO : connecter btn.click aux inputs et outputs

    gr.Markdown("---")
    gr.Markdown("### Exemples de test")
    gr.Examples(
        examples=[
            [5.1, 3.5, 1.4, 0.2],   # setosa typique
            [7.0, 3.2, 4.7, 1.4],   # versicolor typique
            [6.3, 3.3, 6.0, 2.5],   # virginica typique
        ],
        inputs=[],  # TODO : remplacer par la liste de vos sliders
    )

demo.launch()
```

### Critères de réussite Partie 3

- [ ] Les probabilités des 3 classes s'affichent via `gr.Label`
- [ ] Les exemples cliquables pré-remplissent les sliders
- [ ] La mise en page Row/Column est correcte

## Partie 4 — Bonus : explication de la prédiction

Ajoutez une section "Pourquoi cette prédiction ?" qui affiche les importances de features du Random Forest pour la prédiction courante :

```python
def expliquer_prediction(longueur_sepal, largeur_sepal, longueur_petal, largeur_petal):
    """
    Retourne un texte Markdown expliquant quelles features ont le plus influencé la prédiction.
    Utilise feature_importances_ du RandomForest.
    """
    feature_names = [
        "Longueur sépale",
        "Largeur sépale",
        "Longueur pétale",
        "Largeur pétale"
    ]
    importances = modele.feature_importances_

    # Trier par importance décroissante
    indices_tries = np.argsort(importances)[::-1]

    explication = "### Importance des caractéristiques\n\n"
    for i, idx in enumerate(indices_tries):
        barre = "█" * int(importances[idx] * 20)
        explication += f"**{i+1}. {feature_names[idx]}** : {importances[idx]:.1%} {barre}\n\n"

    return explication
```

Intégrez cette fonction dans votre interface avec un `gr.Accordion("Explication", open=False)`.

## Critères d'évaluation globaux

| Critère | Points |
|---------|--------|
| Le modèle est chargé hors de la fonction d'inférence | 2 |
| Les sliders ont des plages de valeurs réalistes | 2 |
| Les probabilités s'affichent avec `gr.Label` | 3 |
| La mise en page est claire et utilisable | 2 |
| Les exemples cliquables fonctionnent | 1 |
| **Bonus** : section d'explication avec `gr.Accordion` | 2 |
| **Total** | **10 (+2 bonus)** |

## Pour aller plus loin

- Remplacer Iris par vos propres données (ex : le dataset Titanic, Churn, etc.)
- Ajouter un onglet "À propos du modèle" avec les métriques d'évaluation (accuracy, matrice de confusion)
- Sauvegarder les prédictions dans un fichier CSV avec `gr.DownloadButton`
- Déployer sur Hugging Face Spaces (voir chapitre 05)
