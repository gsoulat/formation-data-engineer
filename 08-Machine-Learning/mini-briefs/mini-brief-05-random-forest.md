# Mini-brief ML #05 — Random Forest : la sagesse de la foule d'arbres

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [10 — Arbres et forêts](../cours/10-arbres-forets.md) · [13 — Validation et généralisation](../cours/13-validation-generalisation.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** une forêt aléatoire, pas à la découvrir.

## Objectif

À la fin, tu sais **entraîner** une `RandomForestClassifier`, la **régler** avec ses hyperparamètres clés, lire son **classement d'importance des variables**, valider « gratuitement » avec le **score OOB**, et surtout **montrer** pourquoi une forêt est plus stable qu'un arbre unique — c'est tout l'intérêt de l'ensemble.

## Contexte éclair

Le même laboratoire qu'au brief #03 veut un modèle d'**aide au diagnostic** plus robuste : un seul arbre de décision donne des résultats qui changent beaucoup selon les données, et le médecin s'en méfie. On lui propose une **forêt** — des centaines d'arbres qui votent — et on doit démontrer que ça réduit cette instabilité tout en restant **interprétable** au niveau des variables.

## Données

`sklearn.datasets.load_breast_cancer` — **569 patientes, 30 variables** réelles (rayon, texture, concavité…), cible binaire (malin/bénin). Aucun téléchargement.

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
```

## Étapes

1. **Séparer.** `train_test_split` **stratifié** sur `y`. Pas besoin de `StandardScaler` : une forêt d'arbres est insensible à l'échelle des variables (c'est un avantage à noter).
2. **Baseline arbre unique.** Entraîne un `DecisionTreeClassifier` non contraint. Relance-le **5 fois avec des `random_state` différents** et observe combien le score de test **varie** d'un tirage à l'autre. Garde ce chiffre en tête.
3. **La forêt.** Entraîne une `RandomForestClassifier`. Refais le même test des 5 `random_state` : le score **bouge-t-il autant** ? C'est LA démonstration de la réduction de variance par agrégation (bagging).
4. **Régler les hyperparamètres clés.** Fais varier `n_estimators` (10 → 300 : à partir de quand le gain plafonne ?), `max_features` (`"sqrt"`, `"log2"`, une valeur fixe : plus il est petit, plus les arbres sont décorrélés) et `max_depth` (limiter la profondeur pour contrôler le surapprentissage). Utilise `GridSearchCV` avec `scoring="roc_auc"`.
5. **Validation OOB (out-of-bag).** Passe `oob_score=True, bootstrap=True` et lis `model.oob_score_`. Explique en une phrase pourquoi ce score est une estimation « gratuite » de la généralisation, et compare-le à ton score de validation croisée. C'est le second geste spécifique de la forêt.
6. **Importance des variables.** Récupère `model.feature_importances_`, trie et affiche le **top 10**. Quelles mesures pèsent le plus dans le diagnostic ? Formule une phrase compréhensible par un médecin — et compare ce top aux coefficients de la régression logistique du brief #03.

## Critères de réussite (OUI / NON)

- [ ] Variabilité du score d'un **arbre unique** mesurée sur plusieurs `random_state` : OUI / NON
- [ ] Forêt montrée comme **plus stable** que l'arbre unique (variance réduite) : OUI / NON
- [ ] Effet de `n_estimators` observé (plateau) et rôle de `max_features` expliqué : OUI / NON
- [ ] `oob_score_` obtenu et **rapproché** d'un score de validation croisée : OUI / NON
- [ ] Top variables issu de `feature_importances_` identifié et **interprété en langage métier** : OUI / NON

## Pièges à éviter

- Croire qu'**augmenter `n_estimators` améliore toujours** : au-delà d'un seuil, on ne gagne plus que du temps de calcul.
- **Comparer un arbre profond non élagué à une forêt** sans jamais regarder la variance : c'est justement là que la forêt gagne.
- Prendre `feature_importances_` (impureté) pour une **vérité causale** : elles sont biaisées vers les variables à forte cardinalité et corrélées entre elles (cf. permutation importance).
- Activer `oob_score=True` **sans** `bootstrap=True` → pas d'échantillons out-of-bag, erreur.
- Régler les hyperparamètres sur le **jeu de test** au lieu d'une validation croisée → score trop optimiste.

## Pour aller plus loin

- Remplace l'importance par impureté par une **permutation importance** (`permutation_importance`) et compare les classements.
- Trace la courbe **score de test vs `n_estimators`** pour visualiser le plateau.
- Compare la forêt à un `ExtraTreesClassifier` (encore plus de hasard) sur le même jeu.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
