# Mini-brief ML #03 — Régression logistique : décider avec une probabilité

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [09 — Modèles linéaires et logiques](../cours/09-modeles-lineaires.md) · [12 — Métriques](../cours/12-metriques-classification.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** la régression logistique, pas à la découvrir.

## Objectif

À la fin, tu sais **quand** choisir une régression logistique, l'**entraîner**, la **régler**, l'**évaluer** avec les bonnes métriques, et surtout **interpréter** ce qu'elle dit — parce que sa force, c'est d'être lisible.

## Contexte éclair

Un laboratoire veut un outil d'**aide au diagnostic** qui, à partir de mesures d'une tumeur, estime la **probabilité** qu'elle soit maligne. Un médecin ne veut pas juste « oui/non » : il veut une probabilité et savoir **quels facteurs pèsent**. La régression logistique est taillée pour ça.

## Données

`sklearn.datasets.load_breast_cancer` — **569 patientes, 30 variables** réelles (rayon, texture, concavité…), cible binaire (malin/bénin). Aucun téléchargement.

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
```

## Étapes

1. **Séparer & normaliser.** `train_test_split` (stratifié). La régression logistique est sensible à l'échelle → applique un `StandardScaler` **dans un `Pipeline`** (pas à la main, pour éviter la fuite de données — cf. [chapitre 08](../cours/08-data-leakage.md)).
2. **Baseline.** Entraîne une `LogisticRegression`. Note l'accuracy… puis oublie-la : sur un problème médical déséquilibré, elle ment.
3. **Interpréter le modèle.** Récupère `model.coef_`. Quelles variables augmentent la probabilité de malignité ? Convertis un coefficient en **odds ratio** (`exp(coef)`) et formule une phrase compréhensible par un médecin.
4. **Régler les hyperparamètres clés.** Fais varier `C` (inverse de la régularisation) et `penalty` (`l1` vs `l2`). Que se passe-t-il sur les coefficients quand `C` diminue ? Quand `l1` est-il utile ? Utilise `GridSearchCV` avec un scoring adapté (voir étape 5).
5. **Évaluer sérieusement.** Matrice de confusion, **précision/rappel/F1**, et surtout **ROC-AUC**. Ici un **faux négatif** (tumeur maligne ratée) est bien plus grave qu'un faux positif : commente le compromis.
6. **Déplacer le seuil.** Par défaut on classe à p ≥ 0,5. Trace `predict_proba` et choisis un **seuil** qui privilégie le rappel. Montre l'impact sur la matrice de confusion. C'est LE geste spécifique de la régression logistique.

## Critères de réussite (OUI / NON)

- [ ] Normalisation faite **dans un Pipeline** (zéro fuite de données) : OUI / NON
- [ ] Au moins 3 variables les plus influentes identifiées et **interprétées en langage métier** (odds ratio) : OUI / NON
- [ ] Effet de `C` sur les coefficients observé et expliqué : OUI / NON
- [ ] Évaluation via ROC-AUC + précision/rappel (pas seulement l'accuracy) : OUI / NON
- [ ] Un seuil de décision autre que 0,5 est justifié par le coût métier des erreurs : OUI / NON

## Pièges à éviter

- **Normaliser avant le split** → fuite de données, score trop optimiste.
- **Se fier à l'accuracy** sur des classes déséquilibrées.
- Confondre **coefficient** (échelle log-odds) et **probabilité** : l'un s'interprète via `exp()`.
- Oublier que `LogisticRegression` régularise **par défaut** (`C=1.0`) — ce n'est pas une régression « brute ».

## Pour aller plus loin

- Compare à un `SGDClassifier(loss="log_loss")` : même modèle, autre optimisation.
- Trace la **courbe de calibration** : les probabilités prédites sont-elles fiables ?
- Passe en **multiclasses** sur `load_wine` (`multi_class="multinomial"`).

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
