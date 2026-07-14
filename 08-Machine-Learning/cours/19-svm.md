# Chapitre 19 : Support Vector Machines (SVM) — La Marge Maximale

## 🎯 Objectifs

- Comprendre le problème que résout le SVM : quelle frontière choisir parmi une infinité ?
- Saisir l'intuition de la **marge maximale** et le rôle des **vecteurs de support**
- Comprendre le **kernel trick** : passer du linéaire au non-linéaire (RBF)
- Maîtriser les deux boutons de réglage essentiels : **C** et **gamma**
- Comprendre pourquoi la **normalisation** est indispensable pour un SVM
- Savoir reconnaître les forces et les limites du SVM, et quand l'utiliser

**Phase 4 — Semaine 19**

---

## 1. 🧠 Le problème : quelle frontière choisir ?

### 1.1 Une infinité de séparateurs possibles

Imaginez un jeu de données de classification binaire parfaitement séparable : des e-mails « spam » (▲) d'un côté, des e-mails « légitimes » (●) de l'autre. Vous voulez tracer **une droite** qui sépare les deux groupes.

Le problème : il existe une **infinité de droites** qui séparent correctement les données d'entraînement. Toutes ont 100 % de précision sur l'entraînement. Alors, laquelle choisir ?

```
Trois frontières qui séparent TOUTES parfaitement l'entraînement :

  Frontière A (penchée) :      Frontière B (rasante) :      Frontière C (SVM) :

  ●  ●  ● \ ▲  ▲                 ●  ●  ● │▲  ▲                ●  ●  ● │ ▲  ▲
  ●  ●  ●  \  ▲ ▲                ●  ●  ●│ ▲ ▲                 ●  ●  ● │  ▲ ▲
  ●  ●  ●   \ ▲ ▲                ●  ●  │  ▲ ▲                 ●  ●  ● │ ▲  ▲
             \                          │                            │
  Frôle les ●            Colle aux ▲              Centrée, à égale
  côté droit             de gauche               distance des deux camps

  Test : un nouveau point tombe près de la frontière...
  A et B se trompent facilement. C reste robuste.
```

Le SVM répond à cette question de façon **géométrique et non ambiguë** : il choisit la frontière qui laisse **le plus d'espace possible** de chaque côté. C'est le principe de la **marge maximale**.

### 1.2 Analogie : tracer une route entre deux villages

```
Deux villages hostiles, vous devez tracer une route neutre entre eux :

  🏘️ 🏘️ 🏘️          🏘️ 🏘️ 🏘️
     Village ●            Village ▲

  Mauvaise route :  vous la collez contre le village ●.
                    → au premier écart, une maison ● se retrouve du mauvais côté.

  Route SVM :       vous la tracez pile au milieu du couloir vide,
                    aussi loin que possible des DEUX villages.
                    → marge de sécurité maximale des deux côtés.

  La largeur du couloir vide = la MARGE.
  Les maisons les plus proches de la route = les VECTEURS DE SUPPORT.
  Elles seules décident où passe la route. Les maisons du fond ne comptent pas.
```

> 💡 **Conseil** : « Le SVM ne cherche pas juste *une* frontière valide, il cherche la frontière la plus *prudente* : celle qui maximise la distance de sécurité aux points les plus proches. Cette prudence est précisément ce qui lui donne une bonne généralisation. »

---

## 2. 📊 Marge maximale et vecteurs de support

### 2.1 Visualiser la marge

Le SVM définit trois lignes parallèles :

- l'**hyperplan de séparation** (la frontière de décision, au centre) ;
- deux **hyperplans de marge**, un de chaque côté, qui touchent les points les plus proches.

La **marge** est la distance entre les deux hyperplans de marge. Le SVM la rend **la plus large possible**.

```
                marge de gauche       marge de droite
                       │                    │
  ●   ●   ●     ●     [●]   ┊     │     ┊   [▲]     ▲   ▲   ▲
  ●   ●     ●   ●      │    ┊     │     ┊    │      ▲     ▲
  ●     ●   ●   ●     [●]   ┊     │     ┊   [▲]     ▲   ▲   ▲
                       │    ┊     │     ┊    │
                       │  ← marge → │ ← marge →
                       │            │
              hyperplan de marge  hyperplan   hyperplan de marge
              (côté ●)            central     (côté ▲)

  [●] et [▲] = VECTEURS DE SUPPORT (ils touchent la marge)
  Les autres points sont "au fond" et n'influencent pas la frontière.
```

### 2.2 Le point clé : seuls les vecteurs de support comptent

C'est la propriété la plus surprenante du SVM. Si vous **déplacez ou supprimez** un point qui est loin de la frontière (un point du fond), **la frontière ne bouge pas d'un millimètre**. Seuls les points situés **sur la marge** — les **vecteurs de support** — déterminent la position de l'hyperplan.

```
Random Forest / KNN :  TOUS les points participent à la décision.

SVM :                  seuls quelques points-clés (souvent 5 à 20 %
                       du dataset) définissent la frontière.
                       → modèle compact et robuste au bruit "de fond".
```

Cela a une conséquence pratique importante : le SVM est **économe** — le modèle final ne « retient » que ces quelques vecteurs de support.

### 2.3 Formalisation légère

Un hyperplan s'écrit :

```
  w · x + b = 0
```

où `w` est le vecteur normal (orientation) et `b` le biais (décalage). La règle de décision est le **signe** de `w · x + b` : positif → une classe, négatif → l'autre.

On montre que la marge vaut `2 / ‖w‖`. Maximiser la marge revient donc à **minimiser `‖w‖`** sous la contrainte que chaque point soit du bon côté :

```
  minimiser   (1/2) ‖w‖²
  sous        yᵢ (w · xᵢ + b) ≥ 1   pour chaque point i

  (yᵢ = +1 ou -1 selon la classe)

  → problème d'optimisation convexe : UNE seule solution optimale.
    Pas de minima locaux, contrairement aux réseaux de neurones.
```

> 💡 **Conseil** : « Retenez l'image, pas la formule : *marge large = ‖w‖ petit*. Le SVM cherche l'orientation de frontière qui laisse le plus grand couloir vide entre les classes. »

---

## 3. ⚙️ C : la tolérance aux erreurs (marge souple)

### 3.1 Le problème : les données réelles se chevauchent

Le raisonnement précédent suppose des données **parfaitement séparables**. Dans la vraie vie, les classes se chevauchent : quelques ● traînent dans le camp des ▲, et inversement. Exiger une séparation parfaite est alors impossible… ou mène à une frontière tordue qui **surapprend le bruit**.

Le SVM introduit une **marge souple** (*soft margin*) : il **autorise** quelques points à être du mauvais côté, moyennant une pénalité. Le paramètre **C** contrôle le prix de ces violations.

```
C petit (ex. 0.01) :  "je tolère les erreurs, je veux une marge LARGE"
──────────────────────────────────────────────────────────────
  ●  ●  ●   ●  ▲ ●  ┊     │     ┊  ● ▲   ▲  ▲  ▲
                     ← grande marge, quelques points mal classés →
  → frontière lisse, régularisée
  → risque de SOUS-apprentissage (underfitting) si trop petit


C grand (ex. 1000) :  "aucune erreur tolérée, marge ÉTROITE"
──────────────────────────────────────────────────────────────
  ●  ●  ●   ● │▲ ●│ ▲   ▲  ▲   (frontière qui se contorsionne
                              pour classer chaque point)
  → petite marge, colle aux données
  → risque de SUR-apprentissage (overfitting) si trop grand
```

### 3.2 C en une phrase

| C | Comportement | Marge | Risque |
|---|--------------|-------|--------|
| **Petit** (0.001 → 0.1) | Tolérant aux erreurs | Large | Underfitting (trop simple) |
| **Moyen** (1 → 10) | Compromis | Moyenne | Souvent le bon choix |
| **Grand** (100 → 1000) | Intransigeant | Étroite | Overfitting (colle au bruit) |

`C` est en réalité un **paramètre de régularisation inversé** : `C` grand = peu de régularisation, `C` petit = beaucoup de régularisation. C'est l'inverse de `alpha` dans une Ridge/Lasso — attention au réflexe.

### 3.3 Code : voir l'effet de C sur des données réelles

On utilise le **Breast Cancer Wisconsin** (569 patients, 30 features, tumeur bénigne/maligne), un dataset réel fourni par scikit-learn.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Dataset réel
data = load_breast_cancer()
X, y = data.data, data.target  # 569 échantillons, 30 features

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# NORMALISATION obligatoire (voir section 5)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

print("=== Effet de C (kernel linéaire) ===\n")
print(f"{'C':>8} {'Train acc':>10} {'Test acc':>10} {'# supports':>12}")
print("─" * 42)
for C in [0.01, 0.1, 1, 10, 100]:
    svm = SVC(kernel='linear', C=C, random_state=42)
    svm.fit(X_train_s, y_train)
    acc_tr = accuracy_score(y_train, svm.predict(X_train_s))
    acc_te = accuracy_score(y_test, svm.predict(X_test_s))
    n_sv = svm.support_vectors_.shape[0]
    print(f"{C:>8} {acc_tr:>10.4f} {acc_te:>10.4f} {n_sv:>12}")
```

Lecture typique : quand `C` augmente, la précision d'entraînement grimpe vers 1.0 et le **nombre de vecteurs de support diminue** (marge plus étroite). Le meilleur test se situe généralement autour de `C=1` à `C=10` — au-delà, on surapprend.

> ⚠️ **Attention** : « `C` grand ne veut pas dire *meilleur modèle*. Un `C=1000` donne souvent 100 % en entraînement et chute en test. Réglez `C` par validation croisée, jamais à l'œil sur l'entraînement. »

---

## 4. 🌀 Le kernel trick : du linéaire au non-linéaire

### 4.1 Le problème : quand aucune droite ne marche

Certaines données ne sont **pas séparables par une droite**, quel que soit `C`. L'exemple canonique : une classe entourée par l'autre (des cercles concentriques).

```
En 2D, données "en cercles" :          Aucune droite ne sépare
                                        le rouge de l'intérieur !
        ▲  ▲  ▲  ▲
      ▲   ● ● ●   ▲
      ▲  ●     ●  ▲
      ▲   ● ● ●   ▲
        ▲  ▲  ▲  ▲

  Les ● sont au centre, les ▲ autour.
  Une droite ne pourra JAMAIS les séparer.
```

L'idée géniale du SVM : **projeter les données dans une dimension supérieure** où elles *deviennent* séparables par un hyperplan.

```
Projection φ : on ajoute une 3ᵉ dimension = distance au centre (x² + y²)

  Vue de côté après projection :

  hauteur (x²+y²)
     │        ▲   ▲   ▲   ▲        ← les ▲ (loin du centre) montent HAUT
     │      ────────────────────  ← un simple PLAN horizontal sépare !
     │            ● ● ● ●          ← les ● (près du centre) restent BAS
     └─────────────────────────── position

  En 3D, un plan sépare parfaitement.
  Reprojeté en 2D, ce plan devient un... CERCLE.
```

### 4.2 Le « trick » : la projection sans la calculer

Projeter en très haute dimension (voire dimension infinie) serait ruineux à calculer. Le **kernel trick** est l'astuce mathématique qui permet de calculer les **produits scalaires** dans l'espace projeté **sans jamais y projeter réellement**. On remplace `φ(xᵢ) · φ(xⱼ)` par une fonction noyau `K(xᵢ, xⱼ)` calculée directement dans l'espace d'origine.

```
Sans kernel trick :  projeter en dim 10 000  →  produit scalaire  →  💸 coûteux
Avec kernel trick :  K(xᵢ, xⱼ) calculé en dim 2  →  MÊME résultat  →  ✅ rapide
```

### 4.3 Linéaire vs RBF

Les deux noyaux à connaître :

| Kernel | Formule (intuition) | Quand l'utiliser |
|--------|---------------------|------------------|
| **linear** | `K = xᵢ · xⱼ` | Beaucoup de features (texte, haute dimension), relation ~linéaire |
| **rbf** (gaussien) | `K = exp(-γ ‖xᵢ - xⱼ‖²)` | Défaut pour les frontières courbes, données tabulaires |

Le noyau **RBF** (*Radial Basis Function*) mesure une **similarité** : deux points proches → `K ≈ 1`, deux points éloignés → `K ≈ 0`. Il crée des frontières **courbes et locales**.

### 4.4 Code : linéaire échoue, RBF réussit

```python
from sklearn.datasets import make_circles
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# Données non linéairement séparables : deux cercles concentriques
X, y = make_circles(n_samples=500, factor=0.4, noise=0.10, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

print("=== Kernel linéaire vs RBF sur des cercles ===\n")
for kernel in ['linear', 'rbf']:
    svm = SVC(kernel=kernel, C=1.0, gamma='scale', random_state=42)
    svm.fit(X_train_s, y_train)
    acc = accuracy_score(y_test, svm.predict(X_test_s))
    print(f"  kernel={kernel:>7} → accuracy test = {acc:.4f}")

# Résultat typique :
#   kernel= linear → accuracy test ≈ 0.50  (échec : aucune droite ne marche)
#   kernel=    rbf → accuracy test ≈ 0.98  (succès : frontière circulaire)
```

Le noyau linéaire plafonne autour de **50 %** (le hasard) : aucune droite ne sépare des cercles concentriques. Le noyau RBF atteint **~98 %** en épousant la forme circulaire.

> 💡 **Conseil** : « Commencez toujours par `kernel='linear'` comme baseline. S'il sous-performe alors que vos classes se chevauchent visuellement de façon courbe, passez à `rbf`. Le RBF est le couteau suisse, mais le linéaire est plus rapide et suffit souvent en haute dimension (texte). »

---

## 5. 📏 Gamma : la portée d'influence (kernel RBF)

### 5.1 Le problème : à quel point la frontière doit-elle « coller » ?

Pour le noyau RBF, **`gamma`** contrôle jusqu'où « rayonne » l'influence d'un point. C'est la portée de la similarité.

```
gamma PETIT (ex. 0.01) :  influence LARGE, frontière LISSE
──────────────────────────────────────────────────────────
  Chaque point influence une grande zone autour de lui.
  → frontière douce, généralisante
  → si trop petit : underfitting (frontière quasi droite)

       ●●●   ╱‾‾‾‾╲   ▲▲▲
      ●●●●  │      │  ▲▲▲▲     frontière large et arrondie
       ●●●   ╲____╱   ▲▲▲


gamma GRAND (ex. 10) :  influence LOCALE, frontière DÉCOUPÉE
──────────────────────────────────────────────────────────
  Chaque point n'influence qu'un petit voisinage.
  → frontière qui forme des "îlots" autour de chaque point
  → si trop grand : overfitting sévère (mémorise chaque point)

       ●○●   ▲ ●  ▲     petites bulles isolées
      ● ●○  ▲○▲ ●  ▲    autour de chaque exemple
```

### 5.2 C et gamma : les deux boutons à régler ensemble

| Paramètre | Ce qu'il contrôle | Trop petit | Trop grand |
|-----------|-------------------|-----------|-----------|
| **C** | Tolérance aux erreurs de marge | Underfitting (marge trop molle) | Overfitting (marge trop dure) |
| **gamma** | Portée d'influence d'un point (RBF) | Underfitting (frontière trop lisse) | Overfitting (frontière en îlots) |

Les deux interagissent : c'est pourquoi on les règle **ensemble** par recherche sur grille.

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.25, random_state=42, stratify=data.target
)

# Pipeline = scaler + SVM (évite le data leakage pendant la CV, voir ch. 08)
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(kernel='rbf', random_state=42))
])

grille = {
    'svm__C': [0.1, 1, 10, 100],
    'svm__gamma': [0.001, 0.01, 0.1, 'scale'],
}

search = GridSearchCV(pipe, grille, cv=5, scoring='accuracy', n_jobs=-1)
search.fit(X_train, y_train)

print("=== GridSearchCV SVM (C × gamma) ===")
print(f"Meilleurs paramètres : {search.best_params_}")
print(f"Score CV             : {search.best_score_:.4f}")
print(f"Score test           : {search.score(X_test, y_test):.4f}")
```

> 💡 **Conseil** : « `gamma='scale'` (le défaut depuis sklearn 0.22) est un excellent point de départ : il vaut `1 / (n_features × variance(X))`, donc il s'adapte automatiquement à l'échelle des données. Ne réglez `gamma` à la main qu'après l'avoir essayé. »

---

## 6. 🧮 Pourquoi la normalisation est indispensable

### 6.1 Le problème : le SVM raisonne en distances

Le SVM (et surtout le noyau RBF via `‖xᵢ - xⱼ‖²`) repose entièrement sur des **distances** entre points. Or une distance mélange toutes les features. Si une feature s'exprime en milliers et une autre entre 0 et 1, la première **écrase** totalement la seconde.

```
Deux features non normalisées :

  revenu (€)      : 20 000 → 90 000    (amplitude ≈ 70 000)
  nb_enfants      : 0 → 4              (amplitude ≈ 4)

  Distance entre deux clients :
     ‖Δ‖² = (Δrevenu)² + (Δenfants)²
          = (30 000)²   + (2)²
          = 900 000 000 + 4
                          ▲
              nb_enfants est INVISIBLE : 4 face à 900 millions.

  → le SVM ne "voit" que le revenu. La 2ᵉ feature est ignorée.
```

Après **StandardScaler** (moyenne 0, écart-type 1), toutes les features contribuent à la même échelle, et le SVM peut réellement les exploiter.

### 6.2 Démonstration chiffrée

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.25, random_state=42, stratify=data.target
)

# SANS normalisation
svm_brut = SVC(kernel='rbf', C=1, gamma='scale', random_state=42)
score_brut = cross_val_score(svm_brut, X_train, y_train, cv=5).mean()

# AVEC normalisation (dans un pipeline)
svm_norm = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(kernel='rbf', C=1, gamma='scale', random_state=42))
])
score_norm = cross_val_score(svm_norm, X_train, y_train, cv=5).mean()

print(f"SVM sans normalisation : {score_brut:.4f}")   # ≈ 0.90
print(f"SVM avec normalisation : {score_norm:.4f}")   # ≈ 0.97
print(f"Gain                   : +{(score_norm - score_brut)*100:.1f} points")
```

Sur ce dataset, la normalisation fait typiquement passer d'environ **90 %** à **97 %** — pour un simple `StandardScaler`. C'est l'un des meilleurs rapports effort/gain de tout le ML.

> ⚠️ **Attention** : « Toujours mettre le scaler **dans un `Pipeline`**, jamais `fit_transform` sur tout le dataset avant le split. Sinon les statistiques du test fuient dans l'entraînement (*data leakage*, voir chapitre 08). Le pipeline recalcule le scaler sur chaque pli de la validation croisée. »

---

## 7. ⚖️ Forces, limites et quand l'utiliser

### 7.1 Forces et limites

| ✅ Forces | ❌ Limites |
|-----------|-----------|
| Excellent en **petit dataset** (< 10 000 points) | **Lent** sur grand dataset : entraînement en O(n²)–O(n³) |
| Très efficace en **haute dimension** (features > échantillons) | **Boîte noire** avec RBF : peu interprétable |
| Robuste : seuls les vecteurs de support comptent | **Sensible à la normalisation** (obligatoire) |
| Solution **unique** (optimisation convexe, pas de minima locaux) | **2 hyperparamètres** couplés (C, gamma) à régler soigneusement |
| Frontières non linéaires via le **kernel trick** | Pas de `predict_proba` natif (nécessite `probability=True`, coûteux) |
| Marge maximale = **bonne généralisation** | Peu adapté aux **classes très déséquilibrées** sans réglage |

### 7.2 Quand l'utiliser (et quand l'éviter)

| Situation | SVM ? | Pourquoi |
|-----------|:-----:|----------|
| Petit dataset (< 10k), features informatives | ✅ Oui | Terrain de prédilection du SVM |
| Haute dimension (texte TF-IDF, génomique) | ✅ Oui (`linear`) | Excellent, souvent meilleur que le boosting |
| Frontière courbe, dataset moyen | ✅ Oui (`rbf`) | Le kernel trick brille |
| Grand dataset tabulaire (> 100k lignes) | ❌ Non | Trop lent → préférer LightGBM/XGBoost |
| Beaucoup de variables catégorielles | ❌ Non | Préférer CatBoost/LightGBM (gestion native) |
| Besoin d'interprétabilité forte | ❌ Non | Préférer régression logistique ou arbre |
| Besoin de probabilités calibrées | ⚠️ Moyen | `probability=True` est lent et approximatif |

### 7.3 Le piège du grand dataset

```
n = 1 000   → SVM RBF : quelques secondes           ✅
n = 10 000  → SVM RBF : quelques dizaines de sec.    🟡
n = 100 000 → SVM RBF : plusieurs heures... 😱       ❌

  Astuce si dataset moyen : LinearSVC (implémentation liblinear,
  bien plus rapide que SVC(kernel='linear')) pour le cas linéaire.
```

```python
from sklearn.svm import LinearSVC

# Pour un SVM LINÉAIRE sur dataset moyen/grand : LinearSVC est bien plus rapide
# (optimise directement, sans la machinerie des kernels)
lin_svm = LinearSVC(C=1.0, max_iter=5000, random_state=42)
# lin_svm.fit(X_train_s, y_train)  # à normaliser également
```

> 💡 **Conseil** : « Règle mnémotechnique : *SVM = small*. Petit dataset ou haute dimension → SVM est un excellent choix. Gros dataset tabulaire → boosting (chapitre 11). Sur les données textuelles vectorisées, un SVM linéaire reste une référence difficile à battre. »

---

## 8. 🧪 Récapitulatif : pipeline SVM complet

Un exemple bout-en-bout réutilisable : normalisation + SVM + recherche de C/gamma + évaluation propre.

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# Dataset réel : Wine (178 échantillons, 13 features, 3 classes de vins)
data = load_wine()
X, y = data.data, data.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# 1) Pipeline : scaler + SVM (le scaler est ré-appris sur chaque pli de CV)
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(kernel='rbf', random_state=42))
])

# 2) Recherche C × gamma
grille = {
    'svm__C': [0.1, 1, 10, 100],
    'svm__gamma': ['scale', 0.001, 0.01, 0.1],
}
search = GridSearchCV(pipe, grille, cv=5, scoring='accuracy', n_jobs=-1)
search.fit(X_train, y_train)

# 3) Évaluation sur le test (jamais touché avant)
best = search.best_estimator_
y_pred = best.predict(X_test)

print("=== SVM — pipeline complet (Wine) ===")
print(f"Meilleurs params : {search.best_params_}")
print(f"Score CV         : {search.best_score_:.4f}")
print(f"Accuracy test    : {accuracy_score(y_test, y_pred):.4f}\n")
print(classification_report(y_test, y_pred, target_names=data.target_names))

# Nombre de vecteurs de support par classe (le "coût mémoire" du modèle)
svm_final = best.named_steps['svm']
print(f"Vecteurs de support par classe : {svm_final.n_support_}")
```

Sur **Wine**, ce pipeline atteint typiquement **~97–100 %** en test : un dataset petit et bien structuré, exactement le terrain où le SVM excelle.

---

## 🎯 Points clés à retenir

1. **Le problème** : parmi une infinité de frontières valides, le SVM choisit celle qui maximise la **marge** (le couloir vide entre les classes).
2. **Vecteurs de support** : seuls les points sur la marge définissent la frontière ; déplacer un point du fond ne change rien.
3. **C** contrôle la tolérance aux erreurs : petit = marge large + régularisation (underfitting possible), grand = marge dure (overfitting possible).
4. **Kernel trick** : projeter les données en dimension supérieure pour rendre séparable ce qui ne l'était pas — sans jamais calculer la projection.
5. **linear vs RBF** : `linear` pour la haute dimension (texte), `rbf` pour les frontières courbes (défaut tabulaire).
6. **gamma** (RBF) règle la portée d'influence d'un point : petit = frontière lisse, grand = frontière découpée (overfitting).
7. **C et gamma se règlent ensemble** par `GridSearchCV` sur une grille logarithmique.
8. **Normalisation obligatoire** : le SVM raisonne en distances ; sans `StandardScaler`, les features à grande échelle écrasent les autres.
9. Toujours mettre le scaler **dans un `Pipeline`** pour éviter le *data leakage* pendant la validation croisée.
10. **SVM = small** : imbattable en petit dataset et haute dimension, mais trop lent (O(n²)–O(n³)) au-delà de ~100k lignes → boosting.

---

## ❓ Mini-quiz

**Q1.** Parmi plusieurs frontières séparant parfaitement l'entraînement, laquelle le SVM choisit-il ?
- A) La première trouvée
- B) Celle qui maximise la marge entre les classes
- C) Celle qui passe le plus près des points
- D) Une frontière au hasard

**Q2.** Qu'est-ce qu'un vecteur de support ?
- A) N'importe quel point du dataset
- B) Le centre de gravité d'une classe
- C) Un point situé sur (ou à l'intérieur de) la marge, qui influence la frontière
- D) Un point volontairement mal classé

**Q3.** On augmente fortement `C`. Que se passe-t-il le plus probablement ?
- A) La marge s'élargit et le modèle se régularise
- B) La marge se rétrécit et le risque d'overfitting augmente
- C) Le kernel devient automatiquement RBF
- D) Rien, `C` n'a aucun effet avec RBF

**Q4.** Vos deux classes forment des cercles concentriques. Quel kernel choisir ?
- A) `linear`, car il est plus rapide
- B) `rbf`, car une droite ne peut pas séparer des cercles
- C) Aucun, le SVM ne peut pas gérer ce cas
- D) `linear` avec un très grand `C`

**Q5.** À quoi sert `gamma` avec un kernel RBF ?
- A) À tolérer les erreurs de classification
- B) À normaliser les données
- C) À régler la portée d'influence de chaque point (lisse vs découpé)
- D) À choisir le nombre de vecteurs de support

**Q6.** Pourquoi normaliser avant un SVM ?
- A) Pour accélérer la lecture du fichier
- B) Parce que le SVM raisonne en distances : sans mise à l'échelle, les grandes features écrasent les petites
- C) Ce n'est jamais nécessaire
- D) Pour rendre le modèle interprétable

**Q7.** Pour un dataset tabulaire de 500 000 lignes, le SVM RBF est-il un bon choix ?
- A) Oui, c'est toujours le meilleur algorithme
- B) Non, il est trop lent (O(n²)–O(n³)) → préférer un boosting
- C) Oui, mais seulement avec `kernel='linear'` et `SVC`
- D) Oui, si on désactive la normalisation

**Q8.** Où doit-on placer le `StandardScaler` pour éviter le data leakage en validation croisée ?
- A) Appliqué sur tout le dataset avant le split
- B) Dans un `Pipeline` avec le SVM
- C) Uniquement sur le jeu de test
- D) Nulle part, le SVM le fait automatiquement

<details>
<summary>👉 Voir les réponses</summary>

| Question | Réponse | Explication |
|----------|:-------:|-------------|
| Q1 | **B** | Le SVM maximise la marge → meilleure généralisation. |
| Q2 | **C** | Seuls les points sur/dans la marge définissent la frontière. |
| Q3 | **B** | `C` grand = intransigeant = marge étroite = risque d'overfitting. |
| Q4 | **B** | Aucune droite ne sépare des cercles ; RBF crée une frontière courbe. |
| Q5 | **C** | `gamma` = portée d'influence : petit = lisse, grand = découpé. |
| Q6 | **B** | Le SVM utilise des distances ; les échelles doivent être comparables. |
| Q7 | **B** | Complexité O(n²)–O(n³) : sur 500k lignes, préférer LightGBM/XGBoost. |
| Q8 | **B** | Le `Pipeline` ré-apprend le scaler sur chaque pli → pas de fuite. |

</details>

---

## 📚 Ressources

- **Documentation scikit-learn — SVM** : https://scikit-learn.org/stable/modules/svm.html
- **RBF SVM parameters (C et gamma, visualisation)** : https://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html
- **Plot different SVM classifiers (kernels)** : https://scikit-learn.org/stable/auto_examples/svm/plot_iris_svc.html
- **Chapitre 08 — Data Leakage** (pourquoi le `Pipeline` est indispensable)
- **Chapitre 11 — Boosting** (l'alternative pour les grands datasets tabulaires)
- Cortes & Vapnik (1995), *Support-Vector Networks* — l'article fondateur du SVM à marge souple

---

## ✅ Checklist de validation

- [ ] Je sais expliquer le problème que résout le SVM (choisir *la* frontière parmi une infinité)
- [ ] Je sais définir la marge maximale et le rôle des vecteurs de support
- [ ] Je comprends l'effet de `C` (marge souple, tolérance aux erreurs, sur/sous-apprentissage)
- [ ] Je sais expliquer le kernel trick avec l'exemple des cercles concentriques
- [ ] Je sais choisir entre `linear` et `rbf` selon les données
- [ ] Je comprends le rôle de `gamma` (portée d'influence) et son interaction avec `C`
- [ ] Je sais régler `C` et `gamma` par `GridSearchCV` sur une grille logarithmique
- [ ] Je sais pourquoi la normalisation est indispensable et où placer le scaler (Pipeline)
- [ ] Je connais les forces/limites du SVM et je sais quand l'éviter (grands datasets)

---

**Précédent** : [Chapitre 18 : Data Drift](18-data-drift.md)

**Suivant** : [Cheat Sheet Machine Learning](CHEATSHEET-ml.md)
