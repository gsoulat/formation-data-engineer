# Mini-brief ML #09 — PCA : compresser sans perdre l'essentiel

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [03 — Vecteurs, matrices et KNN](../cours/03-vecteurs-matrices-knn.md) · [07 — Feature engineering](../cours/07-feature-engineering.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** la PCA, pas à la découvrir.

## Objectif

À la fin, tu sais **quand** appliquer une PCA, **choisir le bon nombre de composantes** avec la variance expliquée, **projeter des données en 2D** pour les visualiser, et **brancher une PCA en amont d'un modèle** pour gagner en vitesse sans casser la performance.

## Contexte éclair

Un service de tri de courrier numérise des chiffres manuscrits : chaque image fait 8×8 pixels, soit **64 dimensions**. Impossible à visualiser, coûteux à entraîner. On te demande de **compresser** cette information : garder l'essentiel du signal avec bien moins de variables, prouver que la structure des chiffres reste lisible, et vérifier qu'un classifieur reste bon — mais plus rapide.

## Données

`sklearn.datasets.load_digits` — **1 797 images 8×8 (64 variables)**, cible = le chiffre (0 à 9). Aucun téléchargement.

```python
from sklearn.datasets import load_digits
X, y = load_digits(return_X_y=True, as_frame=True)
```

## Étapes

1. **Normaliser d'abord.** La PCA raisonne sur la variance → applique un `StandardScaler` **dans un `Pipeline`** avant la PCA. Pourquoi centrer/réduire change tout ici ?
2. **PCA complète + variance expliquée.** Ajuste une `PCA()` sans fixer `n_components`. Récupère `explained_variance_ratio_`, calcule la **variance cumulée** (`np.cumsum`) et trace-la. Combien de composantes pour atteindre **95 %** ? C'est LE geste : choisir `n_components` par la courbe, pas au hasard.
3. **Choisir `n_components` par un seuil.** Astuce : `PCA(n_components=0.95)` sélectionne automatiquement le nombre de composantes couvrant 95 % de la variance. Compare avec ta lecture de la courbe.
4. **Projeter en 2D et visualiser.** Refais une `PCA(n_components=2)`, projette (`fit_transform`) et fais un `scatter` coloré par `y`. Quels chiffres se séparent bien ? Lesquels se chevauchent (ex. 3/5/8) ? Décris ce que 2 composantes capturent.
5. **PCA en amont d'un modèle (le gain).** Compare un `LogisticRegression` sur les **64 dimensions brutes** vs sur une **PCA à ~30 composantes**, tous deux dans un `Pipeline`. Mesure l'**accuracy** (via `cross_val_score`) **et le temps d'entraînement** (`time.perf_counter`). Combien de dimensions perdues pour quel coût en score ?
6. **Conclure.** Formule le compromis : combien de composantes tu retiens, pourquoi, et ce que tu gagnes (vitesse) vs ce que tu perds (interprétabilité, un peu de score).

## Critères de réussite (OUI / NON)

- [ ] Standardisation faite **dans un Pipeline**, avant la PCA : OUI / NON
- [ ] Courbe de **variance cumulée** tracée et seuil (ex. 95 %) lu dessus : OUI / NON
- [ ] `n_components` **justifié** par la variance expliquée, pas choisi arbitrairement : OUI / NON
- [ ] Projection **2D colorée par classe** produite et commentée (chiffres qui se mélangent) : OUI / NON
- [ ] Comparaison brut vs PCA sur **accuracy + temps**, avec un compromis explicite : OUI / NON

## Pièges à éviter

- **Oublier de standardiser** : une variable à forte échelle domine les composantes et fausse tout.
- **`fit` la PCA sur tout le jeu** (train + test) → fuite de données. La PCA s'apprend sur le train, via le Pipeline.
- Croire qu'une composante = une variable d'origine : c'est une **combinaison linéaire**, non interprétable directement.
- Viser trop peu de composantes « pour faire joli » : 2D c'est pour l'œil, pas pour le modèle.
- Confondre `explained_variance_` (valeurs propres) et `explained_variance_ratio_` (la **proportion**, celle qu'on cumule).

## Pour aller plus loin

- Compare la projection 2D de la PCA à celle de **t-SNE** ou **UMAP** : PCA est linéaire, les autres non.
- Reconstruis des images depuis peu de composantes (`inverse_transform`) et regarde la dégradation visuelle.
- Teste `PCA(whiten=True)` en amont d'un `SVC` : quel effet sur le score ?

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
