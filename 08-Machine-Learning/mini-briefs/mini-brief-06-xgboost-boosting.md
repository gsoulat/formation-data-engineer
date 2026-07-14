# Mini-brief ML #06 — Gradient Boosting / XGBoost : arrêter au bon moment

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [11 — Boosting](../cours/11-boosting.md) · [13 — Validation et généralisation](../cours/13-validation-generalisation.md)
> 🎯 Un modèle, une séance : ici on apprend à **régler** un modèle de boosting sans le laisser sur-apprendre, pas à réexpliquer ce qu'est un arbre.

## Objectif

À la fin, tu sais **entraîner** un modèle de gradient boosting, **surveiller** l'apprentissage avec un set de validation, **couper l'entraînement au bon moment** (early stopping), lire une **courbe train vs validation**, et **hiérarchiser les variables** — bref, piloter le compromis biais/variance à la main.

## Contexte éclair

Une équipe RH veut prédire si le **revenu annuel d'une personne dépasse 50 k\$** à partir de ses caractéristiques (âge, secteur, éducation, heures travaillées…). Le boosting excelle sur ce genre de données tabulaires mixtes, mais s'il tourne trop longtemps il **mémorise le bruit**. Ton job : trouver le nombre d'arbres qui généralise le mieux.

## Données

`fetch_openml('adult', version=2)` — **~48 800 individus, 14 variables** (numériques + catégorielles), cible binaire `>50K` / `<=50K`. Un seul téléchargement, mis en cache ensuite.

```python
from sklearn.datasets import fetch_openml
adult = fetch_openml("adult", version=2, as_frame=True)
X, y = adult.data, (adult.target == ">50K").astype(int)
```

## Étapes

1. **Préparer les données.** `train_test_split` **stratifié**, puis un troisième bloc de **validation** (train / val / test). Encode les catégorielles (`OrdinalEncoder` ou `get_dummies`) — le boosting d'arbres n'a **pas** besoin de normalisation. Gère les `NaN` (certaines colonnes en ont).
2. **Baseline.** Entraîne un `GradientBoostingClassifier` (sklearn) ou `XGBClassifier` avec les valeurs par défaut. Note l'AUC sur la validation : c'est ton point de référence.
3. **`n_estimators` vs `learning_rate`.** Comprends leur couplage : un `learning_rate` faible **exige plus d'arbres**. Fais varier les deux et observe. Un petit pas + beaucoup d'arbres = plus robuste mais plus lent.
4. **Early stopping — LE geste.** Passe un `eval_set=[(X_val, y_val)]` et active l'arrêt anticipé (`early_stopping_rounds` avec XGBoost, ou `n_iter_no_change` en sklearn). Récupère le **nombre d'arbres réellement retenu** (`best_iteration`). C'est lui qui a « décidé » quand s'arrêter, pas toi.
5. **Courbe train vs validation.** Trace l'erreur (log-loss ou 1−AUC) sur train **et** validation en fonction du nombre d'arbres (`evals_result_`). Repère l'endroit où la courbe validation remonte alors que train continue de baisser : **c'est le sur-apprentissage qui commence**.
6. **`max_depth` & compromis biais/variance.** Fais varier `max_depth` (2 → 8). Arbres peu profonds = plus de biais (sous-apprend) ; arbres profonds = plus de variance (sur-apprend). Relie ce que tu vois à l'écart train/validation de l'étape 5.
7. **Importance des variables.** Récupère `feature_importances_` et trie-les. Quelles 3-4 variables portent la prédiction ? Formule une phrase métier (« l'éducation et le nombre d'heures pèsent le plus »).

## Critères de réussite (OUI / NON)

- [ ] Trois blocs distincts train / validation / test (pas de fuite du test) : OUI / NON
- [ ] Early stopping activé et **nombre d'arbres retenu** récupéré (`best_iteration`) : OUI / NON
- [ ] Courbe train vs validation tracée et point de divergence identifié : OUI / NON
- [ ] Effet de `max_depth` sur l'écart train/validation observé et commenté (biais/variance) : OUI / NON
- [ ] Top 3-4 des variables importantes identifié et **interprété en langage métier** : OUI / NON
- [ ] Métrique finale (AUC) mesurée **une seule fois** sur le set de test : OUI / NON

## Pièges à éviter

- **Faire l'early stopping sur le set de test** → tu règles sur le test, il n'est plus « aveugle ». Utilise un set de **validation** dédié.
- **Normaliser les données** : inutile pour le boosting d'arbres, tu perds ton temps.
- Augmenter `n_estimators` **sans** baisser `learning_rate` → tu sur-apprends plus vite, pas mieux.
- Lire l'importance des variables comme une **causalité** : c'est une contribution au modèle, pas une preuve.
- Comparer AUC train et test et conclure « ça marche » : c'est l'écart **train vs validation** qui révèle le sur-apprentissage.

## Pour aller plus loin

- Compare `XGBClassifier`, `LGBMClassifier` et `HistGradientBoostingClassifier` (sklearn) : vitesse et AUC.
- Ajoute une régularisation (`reg_lambda`, `subsample`, `colsample_bytree`) et observe l'effet sur la courbe de validation.
- Passe l'importance des variables aux **valeurs SHAP** pour une explication par individu.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
