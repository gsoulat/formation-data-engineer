# Mini-brief ML #07 — SVM : maximiser la marge, dompter C et gamma

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [09 — Modèles linéaires et logiques](../cours/09-modeles-lineaires.md) · [12 — Métriques](../cours/12-metriques-classification.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** une machine à vecteurs de support (SVM), pas à la découvrir.

## Objectif

À la fin, tu sais **quand** choisir un SVM, l'**entraîner** (avec normalisation obligatoire), régler ses trois leviers — `kernel`, `C`, `gamma` — et **visualiser** l'effet de ces réglages sur la **marge** et la **frontière de décision**.

## Contexte éclair

Le même laboratoire veut un second classifieur d'**aide au diagnostic** tumeur maligne/bénigne. Cette fois, on ne cherche pas une probabilité lisible mais la **frontière la plus robuste** : celle qui laisse la plus grande marge entre les deux classes. C'est exactement ce que fait un SVM. Attention : sans mise à l'échelle, il est aveugle.

## Données

`sklearn.datasets.load_breast_cancer` — **569 patientes, 30 variables** réelles (rayon, texture, concavité…), cible binaire (malin/bénin). Aucun téléchargement.

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
```

## Étapes

1. **Séparer & normaliser (non négociable).** `train_test_split` (stratifié), puis `StandardScaler` **dans un `Pipeline`** avec le `SVC`. Le SVM raisonne sur des **distances** : une variable à grande échelle écrase les autres. Sans scaler, ton modèle est faux — pas juste moins bon (cf. [chapitre 08](../cours/08-data-leakage.md) pour la fuite de données).
2. **Baseline linéaire.** Entraîne un `SVC(kernel="linear")`. Note l'accuracy et le nombre de **vecteurs de support** (`model.support_vectors_`). Ce sont les seuls points qui définissent la frontière.
3. **Passer au noyau RBF.** Remplace par `SVC(kernel="rbf")`. Le noyau RBF permet une frontière **non linéaire**. Compare les scores linéaire vs RBF.
4. **Régler `C` (la tolérance aux erreurs).** Fais varier `C` (ex. `0.01`, `1`, `100`). Un **petit `C`** = marge large, tolérante (risque de sous-apprentissage) ; un **grand `C`** = marge étroite qui colle aux points (risque de sur-apprentissage). Observe l'effet sur le score de test.
5. **Régler `gamma` (la portée du noyau RBF).** Fais varier `gamma` (`"scale"`, `0.001`, `1`, `10`). Un **grand `gamma`** = influence très locale → frontière tourmentée, sur-apprentissage. Utilise un `GridSearchCV` sur le couple (`C`, `gamma`).
6. **Visualiser la frontière (le geste du jour).** Choisis **2 variables** (ex. `mean radius`, `mean texture`), ré-entraîne un SVM dessus, et trace la **frontière de décision** + la **marge** sur une grille (`np.meshgrid`, `contourf`). Fais **2 figures** : un `C`/`gamma` faible vs élevé. Montre visuellement le sous- vs sur-apprentissage.

## Critères de réussite (OUI / NON)

- [ ] Normalisation faite **dans un Pipeline** (le SVM ne tourne jamais sur données brutes) : OUI / NON
- [ ] Comparaison explicite `kernel="linear"` vs `"rbf"` sur les scores : OUI / NON
- [ ] Effet de `C` décrit : petit C = marge large, grand C = marge étroite : OUI / NON
- [ ] Effet de `gamma` (RBF) décrit et meilleur couple (`C`, `gamma`) trouvé via `GridSearchCV` : OUI / NON
- [ ] Frontière de décision tracée sur 2 variables, avec **2 réglages contrastés** commentés : OUI / NON

## Pièges à éviter

- **Oublier de normaliser** → le SVM est cassé, pas juste sous-optimal (les distances n'ont plus de sens).
- Croire que `gamma` sert au noyau `linear` : il **n'agit que sur `rbf`/`poly`**.
- Confondre les rôles : `C` = tolérance aux erreurs, `gamma` = portée du noyau. Les deux surajustent, mais autrement.
- Vouloir des probabilités « gratuites » : `SVC` ne les donne qu'avec `probability=True` (coûteux, recalibré à part).
- Lancer un `GridSearchCV` **sans scaler dans le pipeline** → fuite via la normalisation.

## Pour aller plus loin

- Teste `kernel="poly"` et son paramètre `degree` : quand une frontière polynomiale bat-elle le RBF ?
- Sur un très gros jeu de données, remplace `SVC` par `LinearSVC` (bien plus rapide) : que perds-tu ?
- Ajoute `class_weight="balanced"` et observe l'effet sur le rappel des cas malins.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
