import json


def md(*lines):
    return {"cell_type": "markdown", "metadata": {}, "source": list(lines)}


def code(*lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": list(lines),
    }


cells = []

cells.append(md(
    "# Mini-brief ML #10 — Naïve Bayes : classer du texte en quelques millisecondes\n",
    "\n",
    "> ⏱️ ~1 h 30 · Niveau intermédiaire · Notebook **exécutable** (version pratique du mini-brief)\n",
    "\n",
    "**Objectif** : savoir **quand** dégainer un Naïve Bayes, construire un pipeline **TF-IDF + MultinomialNB**, régler le lissage `alpha`, comprendre pourquoi l'hypothèse « naïve » d'indépendance reste redoutable sur du texte — et pourquoi ce modèle s'entraîne en une fraction de seconde."
))

cells.append(md(
    "## Contexte éclair\n",
    "\n",
    "Une plateforme d'actualités reçoit des milliers d'articles par jour et veut les **trier automatiquement par thème** (sport, informatique, religion…). Elle veut un modèle **rapide à ré-entraîner** chaque nuit, capable de gérer des dizaines de milliers de mots en features.\n",
    "\n",
    "Naïve Bayes est le réflexe classique du tri de texte : léger, honnête, difficile à battre comme baseline."
))

cells.append(md(
    "## 1. Imports\n",
    "\n",
    "Tout `scikit-learn` + `time` pour chronométrer l'entraînement (l'argument massue de Naïve Bayes)."
))

cells.append(code(
    "import time\n",
    "\n",
    "import numpy as np\n",
    "\n",
    "from sklearn.datasets import fetch_20newsgroups\n",
    "from sklearn.feature_extraction.text import TfidfVectorizer\n",
    "from sklearn.naive_bayes import MultinomialNB, GaussianNB\n",
    "from sklearn.linear_model import LogisticRegression\n",
    "from sklearn.pipeline import Pipeline\n",
    "from sklearn.model_selection import GridSearchCV\n",
    "from sklearn.metrics import accuracy_score, classification_report\n",
    "\n",
    "print(\"Imports OK\")"
))

cells.append(md(
    "## 2. Charger les données\n",
    "\n",
    "`fetch_20newsgroups` : des messages **réels** de forums Usenet. On garde **3 catégories bien distinctes** pour rester lisible et rapide. Premier appel = petit téléchargement, ensuite ça vient du cache.\n",
    "\n",
    "⚠️ On enlève `headers`, `footers`, `quotes` : sinon le modèle triche en lisant l'en-tête `Newsgroups:`."
))

cells.append(code(
    "cats = [\"rec.sport.hockey\", \"sci.space\", \"talk.religion.misc\"]\n",
    "\n",
    "train = fetch_20newsgroups(subset=\"train\", categories=cats,\n",
    "                           remove=(\"headers\", \"footers\", \"quotes\"))\n",
    "test = fetch_20newsgroups(subset=\"test\", categories=cats,\n",
    "                          remove=(\"headers\", \"footers\", \"quotes\"))\n",
    "\n",
    "print(f\"Train : {len(train.data)} textes\")\n",
    "print(f\"Test  : {len(test.data)} textes\")\n",
    "print(f\"Classes : {train.target_names}\")"
))

cells.append(code(
    "# Un aperçu d'un message brut et de son label\n",
    "i = 0\n",
    "print(\"Label :\", train.target_names[train.target[i]])\n",
    "print(\"-\" * 60)\n",
    "print(train.data[i][:400])"
))

cells.append(md(
    "## 3. Vectoriser dans un Pipeline (TF-IDF + MultinomialNB)\n",
    "\n",
    "Le texte brut n'est pas exploitable tel quel. On assemble un `Pipeline` :\n",
    "\n",
    "- `TfidfVectorizer` transforme chaque texte en vecteur de fréquences pondérées (features discrètes ≥ 0) ;\n",
    "- `MultinomialNB` classe à partir de ces comptes.\n",
    "\n",
    "🔑 Tout **dans un Pipeline** : le vocabulaire est appris uniquement sur le train, jamais sur le test (évite la fuite de données)."
))

cells.append(code(
    "pipe_nb = Pipeline([\n",
    "    (\"tfidf\", TfidfVectorizer()),\n",
    "    (\"clf\", MultinomialNB()),\n",
    "])\n",
    "\n",
    "pipe_nb"
))

cells.append(md(
    "## 4. Baseline : entraîner, prédire… et **chronométrer** le `.fit()`\n",
    "\n",
    "On note l'accuracy sur le test **et** le temps d'entraînement (`time.perf_counter`). Retiens ce chiffre : c'est l'argument massue de Naïve Bayes."
))

cells.append(code(
    "t0 = time.perf_counter()\n",
    "pipe_nb.fit(train.data, train.target)\n",
    "fit_time_nb = time.perf_counter() - t0\n",
    "\n",
    "pred_nb = pipe_nb.predict(test.data)\n",
    "acc_nb = accuracy_score(test.target, pred_nb)\n",
    "\n",
    "print(f\"Accuracy MultinomialNB : {acc_nb:.3f}\")\n",
    "print(f\"Temps de fit           : {fit_time_nb * 1000:.1f} ms\")\n",
    "print()\n",
    "print(classification_report(test.target, pred_nb, target_names=train.target_names))"
))

cells.append(md(
    "## 5. 🎯 À toi de jouer — régler `alpha` (le lissage de Laplace)\n",
    "\n",
    "`alpha` est LE geste spécifique de Naïve Bayes : il évite qu'un mot **jamais vu** dans une classe mette sa probabilité à zéro.\n",
    "\n",
    "**Consigne** : lance un `GridSearchCV` sur `clf__alpha` avec les valeurs `[0.001, 0.01, 0.1, 1.0]`, puis affiche le meilleur `alpha` et le meilleur score de cross-validation."
))

cells.append(code(
    "# TODO 1 : définir la grille de recherche sur l'hyperparamètre alpha du classifieur\n",
    "# Indice : dans un Pipeline, on cible un param avec \"<nom_etape>__<param>\", ici \"clf__alpha\"\n",
    "param_grid = {\n",
    "    # \"clf__alpha\": [...],\n",
    "}\n",
    "\n",
    "# TODO 2 : instancier GridSearchCV(pipe_nb, param_grid, cv=5, scoring=\"accuracy\")\n",
    "#          puis .fit(train.data, train.target)\n",
    "grid = None  # <-- remplace\n",
    "\n",
    "# TODO 3 : afficher grid.best_params_ et grid.best_score_\n",
    "# print(\"Meilleur alpha :\", grid.best_params_)\n",
    "# print(\"Meilleur score CV :\", round(grid.best_score_, 3))"
))

cells.append(md(
    "💡 **À observer** : que se passe-t-il quand `alpha` est **trop grand** (lissage écrasant : toutes les classes se ressemblent, sous-apprentissage) ? Quand il est **trop petit** (aucun lissage : un mot rare peut faire exploser la décision, sur-apprentissage) ? Écris ta réponse ci-dessous."
))

cells.append(md(
    "## 6. Comprendre le mot « naïf »\n",
    "\n",
    "Naïve Bayes suppose les mots **indépendants** entre eux, ce qui est faux (« new » et « york », « space » et « shuttle »…).\n",
    "\n",
    "🔍 Pour voir à quel point le modèle reste lisible, sortons les **mots les plus caractéristiques** de chaque classe via `feature_log_prob_`."
))

cells.append(code(
    "vectorizer = pipe_nb.named_steps[\"tfidf\"]\n",
    "nb = pipe_nb.named_steps[\"clf\"]\n",
    "feature_names = np.array(vectorizer.get_feature_names_out())\n",
    "\n",
    "for idx, classe in enumerate(train.target_names):\n",
    "    top = np.argsort(nb.feature_log_prob_[idx])[-8:][::-1]\n",
    "    print(f\"{classe:22s} -> {', '.join(feature_names[top])}\")"
))

cells.append(md(
    "✍️ **À rédiger (1 phrase)** : pourquoi l'hypothèse d'indépendance, pourtant fausse, reste-t-elle **efficace pour classer** ?\n",
    "\n",
    "> _Piste : on n'a pas besoin de probabilités exactes, juste que la **bonne classe** ait le score le plus élevé ; les dépendances entre mots faussent l'amplitude mais rarement le classement final._"
))

cells.append(md(
    "## 7. 🎯 À toi de jouer — bonne variante, bonnes données (`GaussianNB`)\n",
    "\n",
    "**Consigne** : remplace `MultinomialNB` par `GaussianNB` dans un pipeline TF-IDF, entraîne, évalue. Ça chute (ou ça casse).\n",
    "\n",
    "- `MultinomialNB` attend des **comptes / fréquences** (features discrètes ≥ 0) ;\n",
    "- `GaussianNB` suppose des features **continues gaussiennes**.\n",
    "\n",
    "⚠️ `GaussianNB` n'accepte pas les matrices creuses : on passe `TfidfVectorizer` en dense (voir le `to_dense` fourni)."
))

cells.append(code(
    "from sklearn.preprocessing import FunctionTransformer\n",
    "\n",
    "to_dense = FunctionTransformer(lambda x: x.toarray(), accept_sparse=True)\n",
    "\n",
    "# TODO : construire pipe_gnb = Pipeline([\n",
    "#            (\"tfidf\", TfidfVectorizer(max_features=3000)),\n",
    "#            (\"dense\", to_dense),\n",
    "#            (\"clf\", GaussianNB()),\n",
    "#        ])\n",
    "#        puis .fit(train.data, train.target), prédire et calculer l'accuracy\n",
    "pipe_gnb = None  # <-- remplace\n",
    "\n",
    "# acc_gnb = accuracy_score(test.target, pipe_gnb.predict(test.data))\n",
    "# print(f\"Accuracy GaussianNB   : {acc_gnb:.3f}  (vs MultinomialNB : {acc_nb:.3f})\")"
))

cells.append(md(
    "💡 **À conclure** : l'écart de score s'explique par la **nature des features**. TF-IDF produit des valeurs ≥ 0 très creuses, mal décrites par une gaussienne → `MultinomialNB` est la variante adaptée au texte."
))

cells.append(md(
    "## 8. Comparer à la régression logistique (score **et** temps)\n",
    "\n",
    "Même pipeline TF-IDF, on branche une `LogisticRegression` à la place du classifieur. Qui gagne en score ? Qui gagne en vitesse ?"
))

cells.append(code(
    "pipe_lr = Pipeline([\n",
    "    (\"tfidf\", TfidfVectorizer()),\n",
    "    (\"clf\", LogisticRegression(max_iter=1000)),\n",
    "])\n",
    "\n",
    "t0 = time.perf_counter()\n",
    "pipe_lr.fit(train.data, train.target)\n",
    "fit_time_lr = time.perf_counter() - t0\n",
    "\n",
    "acc_lr = accuracy_score(test.target, pipe_lr.predict(test.data))\n",
    "\n",
    "print(f\"{'Modèle':<18}{'Accuracy':>10}{'Fit (ms)':>12}\")\n",
    "print(f\"{'MultinomialNB':<18}{acc_nb:>10.3f}{fit_time_nb * 1000:>12.1f}\")\n",
    "print(f\"{'LogisticRegression':<18}{acc_lr:>10.3f}{fit_time_lr * 1000:>12.1f}\")\n",
    "print()\n",
    "print(f\"Naïve Bayes est ~{fit_time_lr / fit_time_nb:.1f}x plus rapide à entraîner.\")"
))

cells.append(md(
    "✍️ **Compromis à formuler** : la régression logistique gagne souvent un peu en accuracy, mais Naïve Bayes s'entraîne bien plus vite — précieux pour un **ré-entraînement nocturne** sur des dizaines de milliers de features. Excellente baseline à battre avant de complexifier."
))

cells.append(md(
    "## ✅ Critères de réussite\n",
    "\n",
    "- [ ] TF-IDF **et** classifieur enchaînés dans un seul `Pipeline` (zéro fuite de vocabulaire)\n",
    "- [ ] Effet de `alpha` observé et expliqué (rôle du lissage, extrêmes trop grand / trop petit)\n",
    "- [ ] `MultinomialNB` vs `GaussianNB` testés, écart de score **expliqué par la nature des features**\n",
    "- [ ] Comparaison chiffrée à la régression logistique sur **score ET temps**\n",
    "- [ ] L'hypothèse d'indépendance (« naïf ») formulée avec ses limites\n",
    "\n",
    "## ⚠️ Pièges à éviter\n",
    "\n",
    "- **Vectoriser tout le corpus avant le split** → le vocabulaire du test fuit dans l'entraînement (le Pipeline l'évite).\n",
    "- Donner du **texte brut** à `MultinomialNB` : il lui faut des vecteurs numériques (d'où le `TfidfVectorizer` en amont).\n",
    "- Passer une matrice TF-IDF à `GaussianNB` sans réfléchir : mauvaise hypothèse de distribution → score dégradé.\n",
    "- Croire que `predict_proba` de Naïve Bayes donne des probabilités **calibrées** : elles sont souvent tassées vers 0 ou 1.\n",
    "- Oublier `remove=(\"headers\", \"footers\", \"quotes\")` : sinon le modèle triche en lisant l'en-tête `Newsgroups:`.\n",
    "\n",
    "## 🚀 Pour aller plus loin\n",
    "\n",
    "- Teste `CountVectorizer` au lieu de `TfidfVectorizer` : l'écart de score dit ce que la pondération TF-IDF apporte.\n",
    "- Essaie `ComplementNB`, conçu pour les jeux de texte **déséquilibrés**."
))

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = "/Users/guillaume/workplace/formation_data_engineer/formation-data-engineer/08-Machine-Learning/mini-briefs/notebooks/mini-brief-10-naive-bayes.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("cells:", len(cells))
print("written:", out)
