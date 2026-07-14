# Mini-brief ML #02 — Régression linéaire : prédire un nombre et l'expliquer

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [09 — Modèles linéaires et logiques](../cours/09-modeles-lineaires.md) · [08 — Data leakage](../cours/08-data-leakage.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** la régression linéaire, pas à la découvrir.

## Objectif

À la fin, tu sais **entraîner** une régression linéaire, **l'évaluer** avec les bonnes métriques (R² et R² ajusté), **lire ses résidus** pour vérifier qu'elle est fiable, **interpréter ses coefficients** en langage métier, et **comparer** une version brute à Ridge et Lasso pour dompter la régularisation.

## Contexte éclair

Une clinique veut estimer la **progression du diabète** d'un patient un an après un bilan, à partir de mesures simples (âge, IMC, pression, dosages sanguins). Le médecin ne veut pas une boîte noire : il veut un **nombre** prédit **et** savoir **quelles mesures pèsent** le plus. La régression linéaire est taillée pour ça.

## Données

`sklearn.datasets.load_diabetes` — **442 patients, 10 variables** réelles (âge, sexe, IMC, pression, 6 dosages sanguins), cible **continue** (progression de la maladie). Aucun téléchargement.

```python
from sklearn.datasets import load_diabetes
X, y = load_diabetes(return_X_y=True, as_frame=True)
```

## Étapes

1. **Séparer.** `train_test_split` (par ex. 80/20, `random_state` fixé). Les variables sont déjà centrées-réduites, mais pense au `StandardScaler` **dans un `Pipeline`** dès que tu ajoutes Ridge/Lasso — pour éviter la fuite de données (cf. [chapitre 08](../cours/08-data-leakage.md)).
2. **Baseline.** Entraîne une `LinearRegression`. Prédis sur le test, calcule le **RMSE** (`mean_squared_error`) et le **R²** (`r2_score`). Que vaut « 0,45 de R² » pour un médecin ?
3. **R² ajusté.** Le R² monte mécaniquement quand on ajoute des variables. Calcule le **R² ajusté** à la main : `1 - (1 - R²) * (n - 1) / (n - p - 1)` avec `n` = nb d'observations, `p` = nb de variables. Compare-le au R² brut : que dit l'écart ?
4. **Analyser les résidus.** Trace `y_test - y_pred` en fonction de `y_pred`. Cherche un **nuage centré sur 0 sans forme** : un cône ⇒ hétéroscédasticité, une courbe ⇒ relation non linéaire. Ajoute un **QQ-plot** (`scipy.stats.probplot`) pour la normalité. C'est LE geste spécifique de la régression linéaire : sans résidus lus, tu ne sais pas si ton modèle est valide.
5. **Interpréter les coefficients.** Récupère `model.coef_`. Quelles variables augmentent la progression ? Formule une phrase compréhensible par un médecin (« à IMC constant, +1 unité de … ⇒ +X de progression »). Attention à l'échelle des variables avant de comparer deux coefficients.
6. **Régulariser : Ridge vs Lasso.** Remplace le modèle par `Ridge` puis `Lasso`. Fais varier l'hyperparamètre **`alpha`** (par ex. `np.logspace(-3, 2, 30)`) avec `GridSearchCV` ou `RidgeCV`/`LassoCV`. Observe : Ridge **rétrécit** les coefficients, Lasso en **annule** certains (sélection de variables). Combien de variables Lasso met-il à zéro ? Lequel des trois généralise le mieux (R² test) ?

## Critères de réussite (OUI / NON)

- [ ] Baseline évaluée avec **RMSE + R²** sur le jeu de test (pas le train) : OUI / NON
- [ ] **R² ajusté** calculé et comparé au R² brut, écart commenté : OUI / NON
- [ ] Résidus tracés et **interprétés** (centré sur 0 ? forme ? normalité) : OUI / NON
- [ ] Au moins 2 coefficients **interprétés en langage métier** : OUI / NON
- [ ] `alpha` optimal trouvé par validation croisée pour Ridge **et** Lasso : OUI / NON
- [ ] Nombre de coefficients annulés par Lasso identifié + meilleur modèle justifié : OUI / NON

## Pièges à éviter

- **Lire le R² sur le train** : il est toujours flatteur. Seul le test compte.
- **Comparer des coefficients** sans variables à la même échelle → conclusions fausses.
- Croire qu'un **bon R² garantit un bon modèle** : des résidus en cône ou courbés invalident l'inférence.
- **Oublier de scaler** avant Ridge/Lasso : la régularisation pénalise alors les variables selon leur unité, pas leur importance.
- Confondre les rôles : `alpha` grand ⇒ **plus** de régularisation (coefficients plus petits), l'inverse du `C` de la régression logistique.

## Pour aller plus loin

- Trace la **trajectoire des coefficients** (regularization path) de Lasso quand `alpha` varie : regarde-les tomber à zéro un par un.
- Teste `ElasticNet` (mélange Ridge + Lasso) et son ratio `l1_ratio`.
- Ajoute des **features polynomiales** (`PolynomialFeatures`) : le R² grimpe-t-il sur le train sans surajuster le test ?

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
