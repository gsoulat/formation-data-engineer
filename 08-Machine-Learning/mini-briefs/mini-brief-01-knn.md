# Mini-brief ML #01 — K plus proches voisins (KNN) : classer par ressemblance

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [03 — Vecteurs, matrices et KNN](../cours/03-vecteurs-matrices-knn.md) · [12 — Métriques](../cours/12-metriques-classification.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** KNN, pas à le découvrir.

## Objectif

À la fin, tu sais **quand** choisir KNN, l'**entraîner**, choisir le bon **k**, régler `metric` et `weights`, comprendre pourquoi la **normalisation est obligatoire**, et **visualiser** la frontière de décision qu'il trace.

## Contexte éclair

Un caviste veut classer automatiquement ses bouteilles en **3 cépages** à partir d'analyses chimiques (alcool, acidité, phénols…). Pas de règle explicite : deux vins « chimiquement proches » sont probablement du même cépage. C'est exactement le pari de KNN — **la ressemblance vaut prédiction**.

## Données

`sklearn.datasets.load_wine` — **178 vins, 13 variables** chimiques réelles, cible à **3 classes** (3 cépages). Aucun téléchargement. Attention : les variables ont des **échelles très différentes** (ex. `proline` en centaines, `flavanoids` en unités).

```python
from sklearn.datasets import load_wine
X, y = load_wine(return_X_y=True, as_frame=True)
```

## Étapes

1. **Séparer & normaliser (indispensable).** `train_test_split` (stratifié). KNN mesure des **distances** : une variable à grande échelle écrase toutes les autres. Applique un `StandardScaler` **dans un `Pipeline`** avec le `KNeighborsClassifier` (pas à la main, pour éviter la fuite de données — cf. [chapitre 08](../cours/08-data-leakage.md)).
2. **Baseline vs sans normalisation.** Entraîne le pipeline complet, puis un KNN **sans** scaler. Compare l'accuracy : l'écart doit te faire comprendre pourquoi la normalisation n'est pas optionnelle ici.
3. **Choisir k par validation.** Fais varier `n_neighbors` (ex. 1 → 30) et trace le score de **validation croisée** en fonction de k. Un k trop petit sur-apprend (bruit), un k trop grand lisse trop. Justifie ton choix par la courbe, pas au hasard.
4. **Régler les autres hyperparamètres.** Compare `weights='uniform'` vs `'distance'` (les voisins proches pèsent-ils plus ?) et `metric='euclidean'` vs `'manhattan'`. Utilise un `GridSearchCV` sur `n_neighbors`, `weights`, `metric`.
5. **Évaluer sérieusement.** Matrice de confusion + **précision/rappel/F1 par classe** (`classification_report`). Sur 3 classes, l'accuracy globale peut masquer un cépage mal reconnu.
6. **Tracer la frontière de décision.** Ré-entraîne sur **2 variables seulement** (ex. `alcohol` + `flavanoids`, normalisées), crée une grille `np.meshgrid`, prédis sur la grille et affiche `plt.contourf` + le nuage de points. C'est LE geste spécifique de KNN : rendre visible **comment k déforme la frontière** (compare k=1 et k=15).

## Critères de réussite (OUI / NON)

- [ ] Normalisation faite **dans un Pipeline** (zéro fuite de données) : OUI / NON
- [ ] Écart de score **avec vs sans normalisation** mesuré et commenté : OUI / NON
- [ ] Valeur de k **justifiée par une courbe de validation croisée** : OUI / NON
- [ ] Effet de `weights` et `metric` testé via `GridSearchCV` : OUI / NON
- [ ] Frontière de décision tracée sur 2 variables, avec comparaison **k=1 vs k grand** : OUI / NON

## Pièges à éviter

- **Oublier de normaliser** → `proline` domine tout, le modèle devient absurde. Piège n°1 de KNN.
- **Normaliser avant le split** → fuite de données, score trop optimiste.
- **k pair sur 2 classes** → risque d'égalité de vote (moins critique ici en 3 classes, mais à connaître).
- **Croire que KNN « n'apprend rien »** : il ne s'entraîne pas, mais il **stocke tout** → prédiction lente et gourmande en mémoire sur gros volumes.
- Tracer la frontière sans re-normaliser les 2 variables → grille incohérente.

## Pour aller plus loin

- Fais varier `p` avec `metric='minkowski'` (p=1 → Manhattan, p=2 → Euclidienne) : retrouve-tu tes résultats de l'étape 4 ?
- Utilise `KNeighborsRegressor` sur un jeu de régression : même logique, la prédiction devient une moyenne des voisins.
- Compare le temps de prédiction de KNN à celui d'une régression logistique sur les mêmes données.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
