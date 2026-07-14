# Mini-brief ML #10 — Naïve Bayes : classer du texte en quelques millisecondes

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [05 — Probabilités et incertitude](../cours/05-probabilites-incertitude.md) · [12 — Métriques](../cours/12-metriques-classification.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** Naïve Bayes sur du texte, pas à le découvrir.

## Objectif

À la fin, tu sais **quand** dégainer un Naïve Bayes, construire un pipeline **TF-IDF + MultinomialNB**, régler le lissage `alpha`, comprendre pourquoi le mot « naïf » (hypothèse d'indépendance) n'empêche pas ce modèle d'être redoutable sur du texte — et pourquoi il s'entraîne en une fraction de seconde.

## Contexte éclair

Une plateforme d'actualités reçoit des milliers d'articles par jour et veut les **trier automatiquement par thème** (sport, informatique, religion…). Elle veut un modèle **rapide à ré-entraîner** chaque nuit, capable de gérer des dizaines de milliers de mots en features. Naïve Bayes est le réflexe classique du tri de texte : léger, honnête, difficile à battre comme baseline.

## Données

`sklearn.datasets.fetch_20newsgroups` — messages **réels** de forums Usenet. On garde **2-3 catégories** bien distinctes pour rester lisible et rapide. Premier appel = petit téléchargement, ensuite ça vient du cache.

```python
from sklearn.datasets import fetch_20newsgroups
cats = ["rec.sport.hockey", "sci.space", "talk.religion.misc"]
train = fetch_20newsgroups(subset="train", categories=cats,
                           remove=("headers", "footers", "quotes"))
test  = fetch_20newsgroups(subset="test",  categories=cats,
                           remove=("headers", "footers", "quotes"))
# train.data = liste de textes bruts, train.target = labels
```

## Étapes

1. **Vectoriser dans un Pipeline.** Le texte brut n'est pas exploitable tel quel : assemble un `Pipeline([("tfidf", TfidfVectorizer(...)), ("clf", MultinomialNB())])`. Le `TfidfVectorizer` transforme chaque texte en vecteur de fréquences pondérées. Garde le tout **dans un Pipeline** pour ne pas apprendre le vocabulaire sur le test (cf. [chapitre 08](../cours/08-data-leakage.md)).
2. **Baseline.** Entraîne sur `train.data` / `train.target`, prédis sur le test. Note l'accuracy… et **chronomètre** le `.fit()` (`time.perf_counter`). Retiens ce chiffre : c'est l'argument massue de Naïve Bayes.
3. **Régler `alpha` (le lissage).** Fais varier `alpha` (ex. `0.001, 0.01, 0.1, 1.0`) via `GridSearchCV`. `alpha` est le lissage de Laplace : il évite qu'un mot **jamais vu** dans une classe mette la probabilité à zéro. Que se passe-t-il quand `alpha` est trop grand ? Trop petit ? C'est LE geste spécifique de Naïve Bayes.
4. **Comprendre « naïf ».** Naïve Bayes suppose les mots **indépendants** entre eux, ce qui est faux (« new » et « york »…). Explique en une phrase pourquoi cette hypothèse simpliste reste efficace pour classer du texte.
5. **Bonne variante, bonnes données.** Remplace `MultinomialNB` par `GaussianNB` dans le pipeline. Ça casse (ou ça chute). Pourquoi ? `MultinomialNB` attend des **comptes/fréquences** (features discrètes ≥ 0), `GaussianNB` suppose des features **continues gaussiennes**. Conclus sur le choix de variante selon la nature des données.
6. **Comparer à la régression logistique.** Branche une `LogisticRegression(max_iter=1000)` sur le **même** pipeline TF-IDF. Compare accuracy **et** temps d'entraînement. Qui gagne en score ? Qui gagne en vitesse ? Formule le compromis.

## Critères de réussite (OUI / NON)

- [ ] TF-IDF **et** classifieur enchaînés dans un seul `Pipeline` (zéro fuite de vocabulaire) : OUI / NON
- [ ] Effet de `alpha` observé et expliqué (rôle du lissage, extrêmes) : OUI / NON
- [ ] `MultinomialNB` vs `GaussianNB` testés, écart de score **expliqué par la nature des features** : OUI / NON
- [ ] Comparaison chiffrée à la régression logistique sur **score ET temps** : OUI / NON
- [ ] L'hypothèse d'indépendance (« naïf ») est formulée avec ses limites : OUI / NON

## Pièges à éviter

- **Vectoriser tout le corpus avant le split** → le vocabulaire du test fuit dans l'entraînement.
- Donner du **texte brut** à `MultinomialNB` : il lui faut des vecteurs numériques (d'où le `TfidfVectorizer` en amont).
- Passer une matrice TF-IDF à `GaussianNB` sans réfléchir : mauvaise hypothèse de distribution → score dégradé.
- Croire que `predict_proba` de Naïve Bayes donne des probabilités **calibrées** : elles sont souvent tassées vers 0 ou 1, à interpréter avec prudence.
- Oublier `remove=("headers", "footers", "quotes")` : sinon le modèle triche en lisant l'en-tête `Newsgroups:`.

## Pour aller plus loin

- Regarde `feature_log_prob_` pour sortir les **mots les plus caractéristiques** de chaque classe : Naïve Bayes est très lisible.
- Teste `CountVectorizer` au lieu de `TfidfVectorizer` : l'écart de score te dit ce que la pondération TF-IDF apporte.
- Essaie `ComplementNB`, conçu pour les jeux de texte **déséquilibrés**.

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
