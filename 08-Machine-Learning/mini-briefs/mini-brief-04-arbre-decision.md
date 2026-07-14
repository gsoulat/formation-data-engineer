# Mini-brief ML #04 — Arbre de décision : des règles qu'on peut lire

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [10 — Arbres et forêts](../cours/10-arbres-forets.md) · [13 — Validation et généralisation](../cours/13-validation-generalisation.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** l'arbre de décision, pas à le découvrir.

## Objectif

À la fin, tu sais **entraîner** un arbre de décision, **le régler** avec `max_depth`, `min_samples_leaf` et `criterion`, **voir de tes yeux** l'overfitting quand il devient trop profond, et **lire** les règles qu'il produit (`plot_tree`, `feature_importances_`). Sa force : il se dessine et s'explique.

## Contexte éclair

Une association d'historiens rejoue le naufrage du Titanic : à partir du profil d'un passager (classe, sexe, âge, prix du billet…), peut-on prédire qui a **survécu** ? Ils ne veulent pas une boîte noire : ils veulent un **arbre de règles lisibles** (« si femme et 1re classe → survie ») qu'ils pourront montrer dans une expo.

## Données

`seaborn.load_dataset('titanic')` — **891 passagers**, un mélange de variables **catégorielles** (`sex`, `class`, `embarked`) et **numériques**, avec de vrais **valeurs manquantes** (`age`, `deck`). Cible binaire `survived` (0/1). Aucun téléchargement (dataset embarqué dans seaborn).

```python
import seaborn as sns
df = sns.load_dataset('titanic')
features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']
X, y = df[features], df['survived']
```

## Étapes

1. **Préparer les données.** Sépare avec `train_test_split` (stratifié). Traite les manquants (`age`, `embarked`) et encode les catégorielles (`sex`, `embarked`) — un `ColumnTransformer` avec `SimpleImputer` + `OneHotEncoder` dans un `Pipeline` est propre. Un arbre **n'a pas besoin** de normalisation : ne perds pas de temps là-dessus.
2. **Baseline sans limite.** Entraîne un `DecisionTreeClassifier()` par défaut (arbre non contraint). Compare l'accuracy **sur le train** et **sur le test** : l'écart énorme, c'est l'overfitting qui te saute aux yeux.
3. **Visualiser l'arbre — le geste clé.** Avec `plot_tree(model, feature_names=..., class_names=['mort','survie'], filled=True)`, dessine un arbre **peu profond** (`max_depth=3`). Lis à voix haute la première règle : quel critère l'arbre choisit-il en premier ? Redessine sans limite de profondeur → observe le monstre illisible : c'est ça, un arbre qui apprend le bruit.
4. **Régler les hyperparamètres clés.** Fais varier `max_depth` (3, 5, 10, None), `min_samples_leaf` (1, 5, 20) et `criterion` (`gini` vs `entropy`). Trace, pour plusieurs `max_depth`, le score train **et** test sur le même graphe : où les deux courbes divergent, tu as trouvé la profondeur qui overfit. Utilise `GridSearchCV` pour confirmer la meilleure combinaison.
5. **Lire les feature_importances_.** Sur ton meilleur modèle, récupère `model.feature_importances_` et trie-les. Quelles 2-3 variables décident vraiment de la survie ? Formule une phrase pour les historiens (« le sexe et la classe pèsent le plus »).
6. **Évaluer et conclure.** Matrice de confusion + précision/rappel/F1 sur le test. L'arbre réglé est-il moins précis que la baseline overfittée ? Explique **pourquoi c'est mieux quand même** (généralisation).

## Critères de réussite (OUI / NON)

- [ ] Catégorielles encodées et manquants traités **dans un Pipeline** (pas à la main) : OUI / NON
- [ ] Overfitting montré chiffres à l'appui (écart train/test sur l'arbre non contraint) : OUI / NON
- [ ] Un arbre est **dessiné** avec `plot_tree` et sa première règle est expliquée : OUI / NON
- [ ] Effet de `max_depth` sur le compromis train/test observé et commenté : OUI / NON
- [ ] Les 2-3 variables les plus importantes identifiées via `feature_importances_` et interprétées en langage métier : OUI / NON

## Pièges à éviter

- **Normaliser les variables** : inutile pour un arbre, tu gaspilles du temps (contrairement à la régression logistique).
- **Laisser l'arbre sans limite** en croyant qu'un bon score train = bon modèle : c'est l'overfitting typique de l'arbre.
- Encoder les catégorielles **avant le split** ou fit l'`OneHotEncoder` sur tout le jeu → fuite de données.
- Confondre **`feature_importances_`** (importance globale dans l'arbre) et **coefficient signé** : ici pas de signe, juste « à quel point la variable sert à découper ».
- Comparer accuracy train/test **sans stratifier** le split sur une cible déséquilibrée.

## Pour aller plus loin

- Remplace l'arbre par un `RandomForestClassifier` : le score bouge-t-il ? Peut-on encore dessiner l'arbre ? (spoiler : non, c'est le prix de la performance).
- Exporte les règles en texte avec `export_text` pour un rendu sans image.
- Fais varier `ccp_alpha` (élagage) : une autre façon de lutter contre l'overfitting que `max_depth`.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
