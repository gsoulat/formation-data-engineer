# Chapitre 23 : Choisir son modèle et ses métriques

> 🎯 **Ce chapitre consolide** ce qui est dispersé dans les autres : une **méthode de décision** en 3
> temps pour ne plus jamais te demander *« quel modèle ? quelle métrique ? »* au hasard.

## 🧠 L'erreur de débutant : commencer par le modèle

Le réflexe naturel — *« j'utilise XGBoost, c'est le meilleur »* — est le **mauvais** ordre. Le bon
raisonnement va **du problème vers le modèle**, en **3 étapes** :

```
1. Quel TYPE de problème ?   →  2. Quelle MÉTRIQUE (selon le coût métier) ?  →  3. Quel MODÈLE ?
```

> **Analogie** — On ne choisit pas un véhicule avant de savoir **où on va** (déménager ? course en
> ville ?) et **comment on mesure le succès** (vitesse ? capacité ? prix ?). Le modèle, c'est le
> véhicule ; il se choisit **en dernier**.

---

## 1️⃣ Étape 1 — Quel type de problème ?

| Ta cible | Type | Exemple |
|---|---|---|
| Une **catégorie** (oui/non, classe) | **Classification** | churn, spam, race d'un animal |
| Un **nombre continu** | **Régression** | prix, température, CA |
| **Aucune étiquette**, trouver des groupes | **Clustering** | segments clients |
| Réduire le nombre de variables | **Réduction de dimension** | visualisation, compression |

Cette étape **détermine les métriques ET les modèles possibles**. Tout part de là.

---

## 2️⃣ Étape 2 — La métrique AVANT le modèle (le coût métier décide)

On choisit la métrique **avant** d'entraîner, car c'est elle qu'on cherche à optimiser. La question
clé : **quelle erreur coûte le plus cher ?**

### En classification : faux positif vs faux négatif

> **Analogie médicale** (chapitre 12) — Un **faux négatif** (rater un cancer) et un **faux positif**
> (alarmer un patient sain) n'ont pas le même coût. La métrique doit refléter **quelle erreur tu veux
> éviter en priorité**.

| Situation | Erreur à éviter | Métrique à viser |
|---|---|---|
| Classes **équilibrées**, erreurs symétriques | — | **Accuracy** |
| Un **faux positif** coûte cher (spam → mail important perdu) | FP | **Precision** |
| Un **faux négatif** coûte cher (cancer, fraude ratée) | FN | **Recall** |
| Compromis, classes **déséquilibrées** | les deux | **F1-score** |
| Comparer des modèles indépendamment du seuil | — | **AUC-ROC** (ou **PR-AUC** si très déséquilibré) |

> 🛑 **Le piège de l'accuracy** — sur un problème à 99 % de « non-fraude », un modèle qui prédit
> *toujours* « non-fraude » a **99 % d'accuracy** et ne sert à **rien**. Dès que les classes sont
> déséquilibrées, l'accuracy ment : passe au **F1** ou à l'**AUC**. (Détaillé au [chapitre 12](12-metriques-classification.md).)

### En régression : quelle métrique ?

| Métrique | Ce qu'elle privilégie | Quand l'utiliser |
|---|---|---|
| **MAE** | erreur moyenne, robuste aux outliers | quand toutes les erreurs comptent pareil |
| **RMSE** | pénalise **fort** les grosses erreurs | quand une grosse erreur est inacceptable |
| **MAPE** | erreur en **%** | quand l'échelle varie (comparer CA de petits/gros magasins) |
| **R²** | part de variance expliquée (0→1) | pour communiquer « le modèle explique 85 % » |

> **Analogie** — MAE = « je me trompe en moyenne de 5 € ». RMSE = « et je punis très fort les fois où
> je me trompe de 100 € ». Choisis selon que les **grosses erreurs** sont graves ou non.

---

## 3️⃣ Étape 3 — Choisir le modèle (du simple au complexe)

Règle d'or : **commence simple** (une baseline), complexifie **seulement si ça vaut le coup**.

> **Analogie** — On ne sort pas l'artillerie lourde pour ouvrir une boîte de conserve. Une **régression
> logistique** bien réglée bat souvent un réseau de neurones mal réglé — et elle est **interprétable**.

### Arbre de décision

```
Classification ?
├── Baseline (toujours commencer ici)      → Régression Logistique
├── Petit dataset, frontières complexes     → SVM
├── Interprétabilité prioritaire (métier)   → Arbre de décision
├── Robuste et polyvalent sans réglage      → Random Forest
└── Performance maximale (données tabulaires) → XGBoost / LightGBM

Régression ?
├── Baseline                                 → Régression Linéaire
├── Trop de features / colinéarité           → Ridge / Lasso
└── Performance maximale                      → XGBoost / LightGBM

Clustering ?
├── Nombre de groupes connu                  → K-Means
├── Formes arbitraires / bruit               → DBSCAN
└── Hiérarchie souhaitée                      → Agglomératif

Images / texte / son ?                        → Deep Learning (voir module 09)
```

### Les critères qui tranchent entre deux modèles

| Critère | Penche vers… |
|---|---|
| **Interprétabilité** exigée (banque, santé) | Régression, Arbre |
| **Performance** brute sur tabulaire | XGBoost / LightGBM |
| **Peu de données** | Modèles simples (Logistic, SVM) |
| **Beaucoup de données / images / texte** | Deep Learning |
| **Temps / ressources limités** | LightGBM (rapide), modèles linéaires |

> 🛑 **Erreur courante** — sauter la baseline. Sans point de comparaison simple, tu ne sais pas si ton
> XGBoost à 200 lignes **apporte vraiment** quelque chose. La baseline est ton **mètre-étalon**.

---

## 🔁 La boucle complète (avec validation)

1. Type de problème → 2. Métrique (coût métier) → 3. **Baseline** simple → 4. Modèle plus complexe →
5. **Validation croisée** sur la métrique choisie → 6. Réglage des hyperparamètres (`GridSearchCV`) →
7. Le meilleur **sur la validation** gagne, évalué une seule fois sur le **test**.

```python
from sklearn.model_selection import cross_val_score
# On valide sur LA métrique choisie à l'étape 2 (ici F1), pas l'accuracy par défaut
scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"F1 = {scores.mean():.3f} ± {scores.std():.3f}")
```

---

## 🧪 Exercice

Pour chacun de ces cas, donne **le type de problème, la métrique et un premier modèle** :
1. Détecter des transactions frauduleuses (0,2 % de fraudes).
2. Prédire le prix de vente d'un appartement.
3. Regrouper des clients pour le marketing (aucune étiquette).

<details><summary>💡 Corrigé</summary>

1. **Classification déséquilibrée** → métrique **Recall** (ne pas rater de fraude) ou **PR-AUC** ;
   modèle : baseline Logistic puis **XGBoost** (souvent + pondération de classes). L'accuracy est à
   **bannir** ici.
2. **Régression** → **RMSE** (une grosse erreur de prix est grave) + **R²** pour communiquer ; baseline
   **Régression Linéaire** puis XGBoost.
3. **Clustering** → pas de métrique supervisée ; on juge avec le **silhouette score** ; modèle **K-Means**
   (ou DBSCAN si formes irrégulières).
</details>

## ✅ À retenir

- **L'ordre est : problème → métrique → modèle.** Jamais l'inverse.
- La **métrique se choisit selon le coût métier** (quel faux — positif ou négatif — coûte le plus cher).
- L'**accuracy ment** sur les classes déséquilibrées → F1 / AUC / PR-AUC.
- **Commence par une baseline simple**, complexifie seulement si le gain le justifie.
- Valide **sur la métrique choisie**, pas sur l'accuracy par défaut.

## 🔗 Pour approfondir
- [Chapitre 12 — Métriques de classification](12-metriques-classification.md) (le détail de chaque métrique)
- [Chapitre 13 — Validation & généralisation](13-validation-generalisation.md)
- [Cheat Sheet ML](CHEATSHEET-ml.md) (tables de référence rapides)
