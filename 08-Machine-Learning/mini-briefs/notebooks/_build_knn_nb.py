import json

def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": list(lines)}

def code(*lines):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": list(lines)}

cells = []

# 1 - Titre + contexte
cells.append(md(
    "# Mini-brief ML #01 - K plus proches voisins (KNN) : classer par ressemblance\n",
    "\n",
    "**Objectif** : savoir *quand* choisir KNN, l'*entrainer*, choisir le bon **k**, regler `metric` et `weights`, comprendre pourquoi la **normalisation est obligatoire**, et **visualiser** la frontiere de decision.\n",
    "\n",
    "**Contexte eclair** : un caviste veut classer automatiquement ses bouteilles en **3 cepages** a partir d'analyses chimiques (alcool, acidite, phenols...). Pas de regle explicite : deux vins *chimiquement proches* sont probablement du meme cepage. C'est le pari de KNN : **la ressemblance vaut prediction**.\n",
    "\n",
    "**Duree** : ~1 h 30 - Niveau intermediaire."
))

# 2 - Imports
cells.append(md(
    "## Etape 0 - Imports\n",
    "\n",
    "On importe tout ce dont on aura besoin : chargement du dataset, pipeline, scaler, KNN, validation croisee et metriques."
))
cells.append(code(
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "from sklearn.datasets import load_wine\n",
    "from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV\n",
    "from sklearn.preprocessing import StandardScaler\n",
    "from sklearn.neighbors import KNeighborsClassifier\n",
    "from sklearn.pipeline import Pipeline\n",
    "from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, accuracy_score\n",
    "\n",
    "RANDOM_STATE = 42"
))

# 3 - Chargement des donnees
cells.append(md(
    "## Etape 1a - Charger les donnees\n",
    "\n",
    "`sklearn.datasets.load_wine` : **178 vins, 13 variables** chimiques reelles, cible a **3 classes** (3 cepages). Aucun telechargement.\n",
    "\n",
    "Attention : les variables ont des **echelles tres differentes** (ex. `proline` en centaines, `flavanoids` en unites)."
))
cells.append(code(
    "X, y = load_wine(return_X_y=True, as_frame=True)\n",
    "\n",
    "print('Dimensions X :', X.shape)\n",
    "print('Classes cible :', sorted(y.unique()))\n",
    "print('Repartition des classes :')\n",
    "print(y.value_counts().sort_index())\n",
    "X.head()"
))

# 3b - Observer les echelles
cells.append(md(
    "### Observer les echelles (pourquoi normaliser ?)\n",
    "\n",
    "Regarde l'ordre de grandeur des colonnes : `proline` se compte en centaines, `flavanoids` en unites. KNN mesure des **distances** : sans mise a l'echelle, `proline` ecraserait toutes les autres variables."
))
cells.append(code(
    "X.describe().loc[['mean', 'std', 'min', 'max']].T"
))

# 4 - Split stratifie
cells.append(md(
    "## Etape 1b - Separer (train_test_split stratifie)\n",
    "\n",
    "On separe **avant** toute normalisation. La stratification (`stratify=y`) garde la meme proportion des 3 cepages dans le train et le test."
))
cells.append(code(
    "X_train, X_test, y_train, y_test = train_test_split(\n",
    "    X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE\n",
    ")\n",
    "\n",
    "print('Train :', X_train.shape, '| Test :', X_test.shape)"
))

# 5 - Pipeline scaler + KNN
cells.append(md(
    "## Etape 1c - Normaliser DANS un Pipeline (indispensable)\n",
    "\n",
    "On place le `StandardScaler` **dans un `Pipeline`** avec le `KNeighborsClassifier`. Ainsi le scaler est ajuste uniquement sur le train a chaque fold : **zero fuite de donnees**.\n",
    "\n",
    "> Faire le scaling a la main sur tout le dataset avant le split = fuite de donnees = score trop optimiste."
))
cells.append(code(
    "pipe_knn = Pipeline([\n",
    "    ('scaler', StandardScaler()),\n",
    "    ('knn', KNeighborsClassifier(n_neighbors=5))\n",
    "])\n",
    "\n",
    "pipe_knn.fit(X_train, y_train)\n",
    "acc_pipe = accuracy_score(y_test, pipe_knn.predict(X_test))\n",
    "print(f'Accuracy test (pipeline normalise, k=5) : {acc_pipe:.3f}')"
))

# 6 - Baseline sans normalisation
cells.append(md(
    "## Etape 2 - Baseline : avec vs SANS normalisation\n",
    "\n",
    "On entraine un KNN **sans** scaler et on compare. L'ecart doit te faire comprendre pourquoi la normalisation n'est pas optionnelle."
))
cells.append(code(
    "knn_brut = KNeighborsClassifier(n_neighbors=5)\n",
    "knn_brut.fit(X_train, y_train)\n",
    "acc_brut = accuracy_score(y_test, knn_brut.predict(X_test))\n",
    "\n",
    "print(f'Accuracy SANS normalisation : {acc_brut:.3f}')\n",
    "print(f'Accuracy AVEC normalisation : {acc_pipe:.3f}')\n",
    "print(f'Gain apporte par la normalisation : {acc_pipe - acc_brut:+.3f}')"
))

# 7 - A toi de jouer : choisir k (TODO)
cells.append(md(
    "## Etape 3 - Choisir k par validation croisee : A TOI DE JOUER\n",
    "\n",
    "Un k trop petit **sur-apprend** (colle au bruit), un k trop grand **lisse trop**. On justifie le choix par une courbe, pas au hasard.\n",
    "\n",
    "**Consigne** : pour chaque `k` de 1 a 30, construis un pipeline (scaler + KNN a `n_neighbors=k`), calcule le score de **validation croisee** (`cross_val_score`, cv=5) sur le train, stocke la moyenne, puis trace la courbe."
))
cells.append(code(
    "# ============================================================\n",
    "# A TOI DE JOUER : trouver le meilleur k par validation croisee\n",
    "# ============================================================\n",
    "ks = range(1, 31)\n",
    "cv_scores = []\n",
    "\n",
    "for k in ks:\n",
    "    # TODO 1 : construire un Pipeline (StandardScaler + KNeighborsClassifier(n_neighbors=k))\n",
    "    # pipe = ...\n",
    "\n",
    "    # TODO 2 : calculer la moyenne des scores de validation croisee (cv=5) sur X_train, y_train\n",
    "    # score = cross_val_score(pipe, X_train, y_train, cv=5).mean()\n",
    "\n",
    "    # TODO 3 : ajouter score a la liste cv_scores\n",
    "    pass\n",
    "\n",
    "# TODO 4 : tracer cv_scores en fonction de ks (plt.plot), puis identifier le meilleur k\n",
    "# best_k = list(ks)[int(np.argmax(cv_scores))]\n",
    "# print('Meilleur k :', best_k)"
))

# 8 - Correction guidee de la courbe (fournie, runnable) pour donner best_k
cells.append(md(
    "### Reference : courbe de validation (pour continuer si besoin)\n",
    "\n",
    "Si tu es bloque sur l'etape precedente, cette cellule fait le meme travail et fournit `best_k` pour la suite du notebook. Compare-la a ta solution."
))
cells.append(code(
    "cv_scores = []\n",
    "for k in ks:\n",
    "    pipe_k = Pipeline([('scaler', StandardScaler()),\n",
    "                       ('knn', KNeighborsClassifier(n_neighbors=k))])\n",
    "    cv_scores.append(cross_val_score(pipe_k, X_train, y_train, cv=5).mean())\n",
    "\n",
    "best_k = list(ks)[int(np.argmax(cv_scores))]\n",
    "\n",
    "plt.figure(figsize=(7, 4))\n",
    "plt.plot(list(ks), cv_scores, marker='o')\n",
    "plt.axvline(best_k, color='red', linestyle='--', label=f'meilleur k = {best_k}')\n",
    "plt.xlabel('k (n_neighbors)')\n",
    "plt.ylabel('Accuracy validation croisee (5-fold)')\n",
    "plt.title('Choix de k par validation croisee')\n",
    "plt.legend()\n",
    "plt.grid(alpha=0.3)\n",
    "plt.show()\n",
    "\n",
    "print(f'Meilleur k = {best_k} (score CV = {max(cv_scores):.3f})')"
))

# 9 - A toi de jouer : GridSearch weights + metric (TODO)
cells.append(md(
    "## Etape 4 - Regler weights et metric via GridSearchCV : A TOI DE JOUER\n",
    "\n",
    "- `weights='uniform'` vs `'distance'` : les voisins proches doivent-ils peser plus ?\n",
    "- `metric='euclidean'` vs `'manhattan'` : quelle notion de distance ?\n",
    "\n",
    "**Consigne** : complete la grille `param_grid` puis lance un `GridSearchCV` sur le pipeline. Note bien le prefixe `knn__` pour cibler l'etape du pipeline."
))
cells.append(code(
    "# ============================================================\n",
    "# A TOI DE JOUER : optimiser n_neighbors, weights et metric\n",
    "# ============================================================\n",
    "pipe_grid = Pipeline([('scaler', StandardScaler()),\n",
    "                      ('knn', KNeighborsClassifier())])\n",
    "\n",
    "# TODO : completer la grille de recherche\n",
    "param_grid = {\n",
    "    'knn__n_neighbors': [3, 5, 7, 9, 11, 15],\n",
    "    # TODO : 'knn__weights': [...]   # 'uniform' vs 'distance'\n",
    "    # TODO : 'knn__metric': [...]    # 'euclidean' vs 'manhattan'\n",
    "}\n",
    "\n",
    "# TODO : instancier et entrainer GridSearchCV(pipe_grid, param_grid, cv=5)\n",
    "# grid = GridSearchCV(pipe_grid, param_grid, cv=5)\n",
    "# grid.fit(X_train, y_train)\n",
    "# print('Meilleurs parametres :', grid.best_params_)\n",
    "# print('Meilleur score CV    :', round(grid.best_score_, 3))"
))

# 10 - Reference GridSearch runnable -> best_model
cells.append(md(
    "### Reference : GridSearchCV complet (pour la suite)\n",
    "\n",
    "Cette cellule fournit `best_model`, le modele optimise reutilise pour l'evaluation. Compare les parametres retenus a ta solution."
))
cells.append(code(
    "param_grid_full = {\n",
    "    'knn__n_neighbors': [3, 5, 7, 9, 11, 15],\n",
    "    'knn__weights': ['uniform', 'distance'],\n",
    "    'knn__metric': ['euclidean', 'manhattan'],\n",
    "}\n",
    "\n",
    "grid = GridSearchCV(pipe_grid, param_grid_full, cv=5, n_jobs=-1)\n",
    "grid.fit(X_train, y_train)\n",
    "best_model = grid.best_estimator_\n",
    "\n",
    "print('Meilleurs parametres :', grid.best_params_)\n",
    "print('Meilleur score CV    :', round(grid.best_score_, 3))"
))

# 11 - Evaluation serieuse
cells.append(md(
    "## Etape 5 - Evaluer serieusement (confusion + report par classe)\n",
    "\n",
    "Sur 3 classes, l'accuracy globale peut **masquer** un cepage mal reconnu. On regarde la **matrice de confusion** et le **precision/rappel/F1 par classe**."
))
cells.append(code(
    "y_pred = best_model.predict(X_test)\n",
    "\n",
    "print('Accuracy test :', round(accuracy_score(y_test, y_pred), 3))\n",
    "print()\n",
    "print(classification_report(y_test, y_pred))\n",
    "\n",
    "cm = confusion_matrix(y_test, y_pred)\n",
    "ConfusionMatrixDisplay(cm, display_labels=sorted(y.unique())).plot(cmap='Blues')\n",
    "plt.title('Matrice de confusion - test')\n",
    "plt.show()"
))

# 12 - A toi de jouer : frontiere de decision (TODO)
cells.append(md(
    "## Etape 6 - Tracer la frontiere de decision : A TOI DE JOUER\n",
    "\n",
    "C'est **LE geste specifique de KNN** : rendre visible comment k deforme la frontiere. On ne garde que **2 variables** (`alcohol` + `flavanoids`), normalisees dans le pipeline.\n",
    "\n",
    "**Consigne** : complete la fonction pour predire sur la grille `np.meshgrid`, puis affiche `plt.contourf` + le nuage de points. La fonction est ensuite appelee pour **k=1 vs k=15** afin de comparer une frontiere qui sur-apprend a une frontiere lisse."
))
cells.append(code(
    "# ============================================================\n",
    "# A TOI DE JOUER : completer le trace de la frontiere de decision\n",
    "# ============================================================\n",
    "features_2d = ['alcohol', 'flavanoids']\n",
    "X2_train = X_train[features_2d]\n",
    "\n",
    "def plot_frontiere(k, ax):\n",
    "    model = Pipeline([('scaler', StandardScaler()),\n",
    "                      ('knn', KNeighborsClassifier(n_neighbors=k))])\n",
    "    model.fit(X2_train, y_train)\n",
    "\n",
    "    x_min, x_max = X2_train['alcohol'].min() - 0.5, X2_train['alcohol'].max() + 0.5\n",
    "    y_min, y_max = X2_train['flavanoids'].min() - 0.5, X2_train['flavanoids'].max() + 0.5\n",
    "    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),\n",
    "                         np.linspace(y_min, y_max, 300))\n",
    "\n",
    "    grid = pd.DataFrame({'alcohol': xx.ravel(), 'flavanoids': yy.ravel()})\n",
    "\n",
    "    # TODO 1 : predire les classes sur la grille -> Z (utiliser model.predict(grid))\n",
    "    # Z = model.predict(grid).reshape(xx.shape)\n",
    "\n",
    "    # TODO 2 : afficher la frontiere avec ax.contourf(xx, yy, Z, alpha=0.3, cmap='viridis')\n",
    "\n",
    "    # TODO 3 : superposer le nuage de points du train colore par y_train\n",
    "    #          ax.scatter(X2_train['alcohol'], X2_train['flavanoids'], c=y_train, edgecolor='k', cmap='viridis')\n",
    "\n",
    "    ax.set_title(f'Frontiere KNN (k={k})')\n",
    "    ax.set_xlabel('alcohol')\n",
    "    ax.set_ylabel('flavanoids')\n",
    "\n",
    "# fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
    "# plot_frontiere(1, axes[0])\n",
    "# plot_frontiere(15, axes[1])\n",
    "# plt.tight_layout(); plt.show()"
))

# 13 - Reference frontiere runnable
cells.append(md(
    "### Reference : frontiere k=1 vs k=15 (solution executable)\n",
    "\n",
    "Observe : a **k=1** la frontiere est decoupee et epouse chaque point (sur-apprentissage) ; a **k=15** elle est lisse. C'est exactement l'effet de k que la courbe de l'etape 3 mesurait."
))
cells.append(code(
    "def plot_frontiere_ref(k, ax):\n",
    "    model = Pipeline([('scaler', StandardScaler()),\n",
    "                      ('knn', KNeighborsClassifier(n_neighbors=k))])\n",
    "    model.fit(X2_train, y_train)\n",
    "    x_min, x_max = X2_train['alcohol'].min() - 0.5, X2_train['alcohol'].max() + 0.5\n",
    "    y_min, y_max = X2_train['flavanoids'].min() - 0.5, X2_train['flavanoids'].max() + 0.5\n",
    "    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),\n",
    "                         np.linspace(y_min, y_max, 300))\n",
    "    grid = pd.DataFrame({'alcohol': xx.ravel(), 'flavanoids': yy.ravel()})\n",
    "    Z = model.predict(grid).reshape(xx.shape)\n",
    "    ax.contourf(xx, yy, Z, alpha=0.3, cmap='viridis')\n",
    "    ax.scatter(X2_train['alcohol'], X2_train['flavanoids'],\n",
    "               c=y_train, edgecolor='k', cmap='viridis')\n",
    "    ax.set_title(f'Frontiere KNN (k={k})')\n",
    "    ax.set_xlabel('alcohol')\n",
    "    ax.set_ylabel('flavanoids')\n",
    "\n",
    "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
    "plot_frontiere_ref(1, axes[0])\n",
    "plot_frontiere_ref(15, axes[1])\n",
    "plt.tight_layout()\n",
    "plt.show()"
))

# 14 - Criteres de reussite + pieges
cells.append(md(
    "## Criteres de reussite\n",
    "\n",
    "- [ ] Normalisation faite **dans un Pipeline** (zero fuite de donnees)\n",
    "- [ ] Ecart de score **avec vs sans normalisation** mesure et commente\n",
    "- [ ] Valeur de k **justifiee par une courbe de validation croisee**\n",
    "- [ ] Effet de `weights` et `metric` teste via `GridSearchCV`\n",
    "- [ ] Frontiere de decision tracee sur 2 variables, avec comparaison **k=1 vs k grand**\n",
    "\n",
    "## Pieges a eviter\n",
    "\n",
    "- **Oublier de normaliser** -> `proline` domine tout, le modele devient absurde. Piege n.1 de KNN.\n",
    "- **Normaliser avant le split** -> fuite de donnees, score trop optimiste.\n",
    "- **k pair sur 2 classes** -> risque d'egalite de vote (moins critique ici en 3 classes, mais a connaitre).\n",
    "- **Croire que KNN n'apprend rien** : il ne s'entraine pas, mais il **stocke tout** -> prediction lente et gourmande sur gros volumes.\n",
    "- **Tracer la frontiere sans re-normaliser les 2 variables** -> grille incoherente.\n",
    "\n",
    "## Pour aller plus loin\n",
    "\n",
    "- Fais varier `p` avec `metric='minkowski'` (p=1 -> Manhattan, p=2 -> Euclidienne) : retrouves-tu tes resultats de l'etape 4 ?\n",
    "- Utilise `KNeighborsRegressor` sur un jeu de regression : la prediction devient une moyenne des voisins.\n",
    "- Compare le temps de prediction de KNN a celui d'une regression logistique sur les memes donnees."
))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out = "/Users/guillaume/workplace/formation_data_engineer/formation-data-engineer/08-Machine-Learning/mini-briefs/notebooks/mini-brief-01-knn.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("cells:", len(cells))
print("wrote:", out)
