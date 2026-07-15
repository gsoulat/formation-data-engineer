import json

def md(text):
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "markdown", "metadata": {}, "source": src}

def code(text):
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}

cells = []

# 1 - Titre + contexte
cells.append(md(
"""# Mini-brief ML #07 — SVM : maximiser la marge, dompter C et gamma

> ⏱️ ~1 h 30 · Niveau intermédiaire · Notebook **exécutable** (pratique)

## Objectif
À la fin, tu sais **quand** choisir un SVM, l'**entraîner** (avec normalisation obligatoire),
régler ses trois leviers — `kernel`, `C`, `gamma` — et **visualiser** l'effet de ces réglages
sur la **marge** et la **frontière de décision**.

## Contexte éclair
Le laboratoire veut un second classifieur d'**aide au diagnostic** tumeur maligne/bénigne.
On ne cherche pas une probabilité lisible mais la **frontière la plus robuste** : celle qui laisse
la plus grande marge entre les deux classes. C'est exactement ce que fait un SVM.
Attention : **sans mise à l'échelle, il est aveugle** (il raisonne sur des distances)."""))

# 2 - Imports
cells.append(code(
"""# Imports
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

RANDOM_STATE = 42"""))

# 3 - Données markdown
cells.append(md(
"""## Données
`sklearn.datasets.load_breast_cancer` — **569 patientes, 30 variables** réelles
(rayon, texture, concavité…), cible binaire (malin = 0 / bénin = 1). Aucun téléchargement."""))

# 4 - Chargement
cells.append(code(
"""# Chargement du jeu de données (as_frame pour garder les noms de colonnes)
X, y = load_breast_cancer(return_X_y=True, as_frame=True)

print("Dimensions X :", X.shape)
print("Classes cible :", np.bincount(y), "(0 = malin, 1 = bénin)")
X.head()"""))

# 5 - Etape 1 markdown : split + scaler
cells.append(md(
"""## Étape 1 — Séparer & normaliser (non négociable)
On sépare **de façon stratifiée**, puis on met le `StandardScaler` **dans un `Pipeline`** avec le `SVC`.
Le SVM raisonne sur des **distances** : une variable à grande échelle écrase les autres.
Mettre le scaler *dans* le pipeline évite la **fuite de données** : le scaler n'apprend que sur le train à chaque fold."""))

# 6 - Split code
cells.append(code(
"""# Séparation train / test stratifiée
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
)
print("Train :", X_train.shape[0], "| Test :", X_test.shape[0])"""))

# 7 - Etape 2 markdown : baseline linéaire
cells.append(md(
"""## Étape 2 — Baseline linéaire
On entraîne un `SVC(kernel="linear")` dans un pipeline avec le scaler.
On note l'accuracy et le nombre de **vecteurs de support** : ce sont les seuls points qui définissent la frontière."""))

# 8 - Baseline code
cells.append(code(
"""# SVM linéaire (scaler DANS le pipeline)
svm_linear = make_pipeline(StandardScaler(), SVC(kernel="linear", C=1.0))
svm_linear.fit(X_train, y_train)

acc_linear = accuracy_score(y_test, svm_linear.predict(X_test))
n_sv = svm_linear.named_steps["svc"].support_vectors_.shape[0]

print(f"Accuracy test (linear) : {acc_linear:.3f}")
print(f"Nombre de vecteurs de support : {n_sv} / {X_train.shape[0]} points d'entraînement")"""))

# 9 - Etape 3 markdown + TODO RBF
cells.append(md(
"""## Étape 3 — 🎯 À toi de jouer : passer au noyau RBF
Le noyau **RBF** permet une frontière **non linéaire**. Construis un pipeline
`StandardScaler` + `SVC(kernel="rbf")`, entraîne-le et compare son accuracy à la baseline linéaire.

> Consigne : réutilise `make_pipeline` comme à l'étape 2, mais avec `kernel="rbf"`."""))

# 10 - RBF TODO code
cells.append(code(
"""# 🎯 À toi de jouer
# TODO 1 : crée un pipeline scaler + SVC(kernel="rbf", C=1.0, gamma="scale")
# svm_rbf = make_pipeline(...)
# TODO 2 : entraîne-le sur (X_train, y_train)
# TODO 3 : calcule acc_rbf = accuracy_score(...) sur le test
# TODO 4 : compare avec acc_linear (print des deux)

# svm_rbf = ...
# svm_rbf.fit(...)
# acc_rbf = ...
# print(f"Linear : {acc_linear:.3f} | RBF : {acc_rbf:.3f}")"""))

# 11 - Etape 4 markdown : régler C
cells.append(md(
"""## Étape 4 — Régler `C` (la tolérance aux erreurs)
On fait varier `C` sur un SVM RBF.
- **petit `C`** = marge large, tolérante aux erreurs → risque de **sous-apprentissage** ;
- **grand `C`** = marge étroite qui colle aux points → risque de **sur-apprentissage**.

Observe l'effet sur le score de test."""))

# 12 - C sweep code
cells.append(code(
"""# Effet de C (gamma fixé à "scale")
for C in [0.01, 1, 100]:
    model = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=C, gamma="scale"))
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"C = {C:>6} -> accuracy test = {acc:.3f}")"""))

# 13 - Etape 5 markdown + TODO GridSearch
cells.append(md(
"""## Étape 5 — 🎯 À toi de jouer : régler `gamma` via `GridSearchCV`
`gamma` = **portée** du noyau RBF. Un **grand `gamma`** = influence très locale → frontière
tourmentée, sur-apprentissage. Cherche le meilleur couple (`C`, `gamma`) avec un `GridSearchCV`.

> Consigne : le pipeline (avec le scaler !) est déjà là. Complète la **grille** et lance la recherche.
> Attention : les clés de la grille sont préfixées par le nom de l'étape (`svc__C`, `svc__gamma`)."""))

# 14 - GridSearch TODO code
cells.append(code(
"""# 🎯 À toi de jouer
pipe = make_pipeline(StandardScaler(), SVC(kernel="rbf"))

# TODO 1 : complète la grille avec plusieurs valeurs de C et de gamma
param_grid = {
    "svc__C": [0.1, 1, 10, 100],       # tu peux ajuster
    "svc__gamma": ["scale", 0.001, 1, 10],  # "scale", et valeurs numériques
}

# TODO 2 : crée le GridSearchCV (cv=5, scoring="accuracy") et fit-le sur le train
# grid = GridSearchCV(pipe, param_grid, cv=5, scoring="accuracy")
# grid.fit(X_train, y_train)

# TODO 3 : affiche grid.best_params_ et l'accuracy sur le test
# print("Meilleur couple :", grid.best_params_)
# print("Accuracy test  :", accuracy_score(y_test, grid.predict(X_test)))"""))

# 15 - Etape 6 markdown : visualisation + helper
cells.append(md(
"""## Étape 6 — Visualiser la frontière (le geste du jour)
On choisit **2 variables** (`mean radius`, `mean texture`), on ré-entraîne un SVM dessus,
et on trace la **frontière de décision** + la **marge** sur une grille (`np.meshgrid`, `contourf`).

La fonction ci-dessous fait le tracé pour un pipeline donné : zones colorées (décision),
courbe centrale (frontière) et lignes pointillées (**marges**), plus les points d'entraînement."""))

# 16 - helper plot code
cells.append(code(
"""# Sous-jeu à 2 variables + fonction de tracé
feat = ["mean radius", "mean texture"]
X2_train = X_train[feat].values
X2_test = X_test[feat].values

def plot_svm_boundary(clf, X2, y2, title, ax):
    clf.fit(X2, y2)
    x_min, x_max = X2[:, 0].min() - 1, X2[:, 0].max() + 1
    y_min, y_max = X2[:, 1].min() - 1, X2[:, 1].max() + 1
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 300),
        np.linspace(y_min, y_max, 300),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    # valeur de décision (distance signée) pour tracer marge + frontière
    Z = clf.decision_function(grid).reshape(xx.shape)
    ax.contourf(xx, yy, Z > 0, alpha=0.2, cmap=plt.cm.coolwarm)
    ax.contour(xx, yy, Z, levels=[-1, 0, 1],
               colors="k", linestyles=["--", "-", "--"], linewidths=[1, 2, 1])
    ax.scatter(X2[:, 0], X2[:, 1], c=y2, cmap=plt.cm.coolwarm,
               s=15, edgecolors="k", linewidths=0.3)
    ax.set_xlabel(feat[0]); ax.set_ylabel(feat[1]); ax.set_title(title)"""))

# 17 - two contrasted figures code
cells.append(code(
"""# Deux réglages contrastés : sous-apprentissage vs sur-apprentissage
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

soft = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=0.1, gamma=0.1))
hard = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=100, gamma=10))

plot_svm_boundary(soft, X2_train, y_train.values,
                  "C=0.1, gamma=0.1 (marge large, lisse)", axes[0])
plot_svm_boundary(hard, X2_train, y_train.values,
                  "C=100, gamma=10 (frontiere tourmentee)", axes[1])

plt.tight_layout()
plt.show()"""))

# 18 - Etape 6bis markdown + TODO interpretation
cells.append(md(
"""### 🎯 À toi de jouer : lire et commenter les deux figures
Compare **visuellement** les deux frontières ci-dessus, puis quantifie le sur-apprentissage
en regardant l'écart **train vs test** de chaque réglage.

> Consigne : entraîne `soft` et `hard` sur les 2 variables, puis affiche l'accuracy **train** ET **test**
> pour chacun. Un gros écart train ≫ test = sur-apprentissage."""))

# 19 - interpretation TODO code
cells.append(code(
"""# 🎯 À toi de jouer
# TODO : pour soft puis hard, calcule accuracy train et test sur les 2 variables
# et repere lequel sur-apprend (train tres haut, test plus bas).
#
# for name, clf in [("soft", soft), ("hard", hard)]:
#     clf.fit(X2_train, y_train)
#     acc_tr = accuracy_score(y_train, clf.predict(X2_train))
#     acc_te = accuracy_score(y_test,  clf.predict(X2_test))
#     print(f"{name:>4} | train={acc_tr:.3f}  test={acc_te:.3f}  ecart={acc_tr-acc_te:+.3f}")"""))

# 20 - Critères de réussite + pièges
cells.append(md(
"""## Critères de réussite

- [ ] Normalisation faite **dans un Pipeline** (le SVM ne tourne jamais sur données brutes)
- [ ] Comparaison explicite `kernel="linear"` vs `"rbf"` sur les scores
- [ ] Effet de `C` décrit : petit C = marge large, grand C = marge étroite
- [ ] Effet de `gamma` (RBF) décrit et meilleur couple (`C`, `gamma`) trouvé via `GridSearchCV`
- [ ] Frontière de décision tracée sur 2 variables, avec **2 réglages contrastés** commentés

## Pièges à éviter

- **Oublier de normaliser** → le SVM est cassé, pas juste sous-optimal (les distances n'ont plus de sens).
- Croire que `gamma` sert au noyau `linear` : il **n'agit que sur `rbf`/`poly`**.
- Confondre les rôles : `C` = tolérance aux erreurs, `gamma` = portée du noyau. Les deux surajustent, mais autrement.
- Vouloir des probabilités « gratuites » : `SVC` ne les donne qu'avec `probability=True` (coûteux, recalibré à part).
- Lancer un `GridSearchCV` **sans scaler dans le pipeline** → fuite via la normalisation.

## Pour aller plus loin
- Teste `kernel="poly"` et son paramètre `degree` : quand une frontière polynomiale bat-elle le RBF ?
- Sur un très gros jeu de données, remplace `SVC` par `LinearSVC` (bien plus rapide) : que perds-tu ?
- Ajoute `class_weight="balanced"` et observe l'effet sur le rappel des cas malins."""))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = "/Users/guillaume/workplace/formation_data_engineer/formation-data-engineer/08-Machine-Learning/mini-briefs/notebooks/mini-brief-07-svm.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("cells:", len(cells))
print("written:", out)
