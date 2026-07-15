# Chapitre 13 : Validation et Généralisation

## 🎯 Objectifs

- Maîtriser les stratégies de découpage train/validation/test
- Comprendre et implémenter la **cross-validation** (K-Fold, Stratified, Time Series)
- Savoir diagnostiquer l'**overfitting** et l'**underfitting** avec les courbes d'apprentissage
- Utiliser les courbes de validation pour trouver les bons hyperparamètres
- Maîtriser **GridSearchCV** et **RandomizedSearchCV** pour le tuning

> **Phase 4 - Semaine 13**

---

## 1. 🔀 Train/Test Split

### 1.1 Pourquoi séparer les données ?

Un modèle qui s'évalue sur les données qu'il a vues pendant l'entraînement est comme un étudiant qui connaît les réponses à l'avance : il aura 20/20 mais ne saura rien faire en situation réelle. C'est l'**overfitting**.

```
SANS split (MAUVAIS) :
┌──────────────────────────────────┐
│         Données complètes        │
│     Train dessus + Évalue dessus │  → Score artificiellement élevé
└──────────────────────────────────┘

AVEC split (BON) :
┌──────────────────────┬───────────┐
│   Train (80%)        │ Test (20%)│
│   Apprend ici        │ Évalue ici│  → Score honnête
└──────────────────────┴───────────┘
```

### 1.2 Proportions classiques

| Split | Train | Test | Usage |
|-------|-------|------|-------|
| 80/20 | 80% | 20% | Le plus courant |
| 70/30 | 70% | 30% | Petits datasets (< 5000) |
| 90/10 | 90% | 10% | Grands datasets (> 100 000) |

### 1.3 Implémentation

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer

# --- Charger les données ---
cancer = load_breast_cancer()
X = pd.DataFrame(cancer.data, columns=cancer.feature_names)
y = cancer.target

print(f"Dataset : {X.shape[0]} échantillons, {X.shape[1]} features")
print(f"Distribution des classes : {np.bincount(y)}")

# --- Split basique ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% pour le test
    random_state=42       # Reproductibilité !
)

print(f"\nTrain : {X_train.shape[0]} échantillons")
print(f"Test  : {X_test.shape[0]} échantillons")
```

### 1.4 Stratification pour classes déséquilibrées

Sans stratification, le split aléatoire peut créer un déséquilibre entre train et test :

```python
# --- SANS stratification (risqué) ---
X_train_ns, X_test_ns, y_train_ns, y_test_ns = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Train - Classe 0 : {(y_train_ns == 0).mean():.2%}")
print(f"Test  - Classe 0 : {(y_test_ns == 0).mean():.2%}")

# --- AVEC stratification (recommandé) ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # ← ICI
)
print(f"\nAvec stratification :")
print(f"Train - Classe 0 : {(y_train == 0).mean():.2%}")
print(f"Test  - Classe 0 : {(y_test == 0).mean():.2%}")
# Les proportions sont identiques entre train et test
```

> 💡 **Conseil** : "Utilisez **toujours** `stratify=y` pour la classification. Cela garantit que chaque split a la même proportion de classes que le dataset complet."

### 1.5 random_state pour la reproductibilité

```python
# Sans random_state → résultats différents à chaque exécution
X_train_1, _, _, _ = train_test_split(X, y, test_size=0.2)
X_train_2, _, _, _ = train_test_split(X, y, test_size=0.2)
print(f"Mêmes données ? {(X_train_1.index == X_train_2.index).all()}")  # False

# Avec random_state → résultats identiques
X_train_3, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)
X_train_4, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Mêmes données ? {(X_train_3.index == X_train_4.index).all()}")  # True
```

> ⚠️ **Attention** : "Fixez **toujours** `random_state` pour que vos résultats soient reproductibles. Cela ne biaise pas les données, ça fixe juste le tirage aléatoire."

---

## 2. 📊 Validation Set (Train / Validation / Test)

### 2.1 Pourquoi 3 ensembles ?

Avec seulement train/test, si vous tuner vos hyperparamètres en vous basant sur le score test, vous **overfittez sur le test set** ! C'est comme si vous ajustiez vos réponses après avoir vu la correction.

```
┌────────────────────┬──────────┬───────────┐
│   Train (60%)      │ Val (20%)│ Test (20%)│
│                    │          │           │
│ Entraîner le       │ Tuner    │ Évaluation│
│ modèle             │ hyper-   │ FINALE    │
│                    │ paramètres│ (1 seule │
│                    │          │  fois !)  │
└────────────────────┴──────────┴───────────┘
```

### 2.2 Workflow complet

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# Étape 1 : Séparer le test set (on n'y touche PLUS)
X_temp, X_test, y_temp, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Étape 2 : Séparer train et validation
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
)
# 0.25 * 0.80 = 0.20 → on a bien 60/20/20

print(f"Train : {X_train.shape[0]} | Val : {X_val.shape[0]} | Test : {X_test.shape[0]}")

# Étape 3 : Tester plusieurs hyperparamètres sur le validation set
for n_est in [50, 100, 200]:
    for depth in [3, 5, 10, None]:
        rf = RandomForestClassifier(n_estimators=n_est, max_depth=depth, random_state=42)
        rf.fit(X_train, y_train)
        score_val = f1_score(y_val, rf.predict(X_val))
        print(f"n_estimators={n_est}, max_depth={depth} → F1 val = {score_val:.4f}")

# Étape 4 : Meilleur modèle → évaluer UNE SEULE FOIS sur le test set
best_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
best_model.fit(X_train, y_train)
score_test = f1_score(y_test, best_model.predict(X_test))
print(f"\n=== Score FINAL sur test set : F1 = {score_test:.4f} ===")
```

> ⚠️ **Attention** : "Le test set ne doit être utilisé qu'UNE SEULE FOIS, à la toute fin. Si vous l'utilisez plusieurs fois pour ajuster votre modèle, votre estimation de performance est biaisée."

---

## 3. 🔄 Cross-Validation

### 3.1 K-Fold expliqué visuellement

Le problème du validation set : on perd 20% de données pour la validation. Avec peu de données, c'est dommage.

La **cross-validation** résout ce problème : chaque échantillon sert **à la fois** à l'entraînement et à la validation.

```
K-Fold avec K=5 :

Fold 1: [VAL][TRAIN][TRAIN][TRAIN][TRAIN] → Score 1
Fold 2: [TRAIN][VAL][TRAIN][TRAIN][TRAIN] → Score 2
Fold 3: [TRAIN][TRAIN][VAL][TRAIN][TRAIN] → Score 3
Fold 4: [TRAIN][TRAIN][TRAIN][VAL][TRAIN] → Score 4
Fold 5: [TRAIN][TRAIN][TRAIN][TRAIN][VAL] → Score 5

Score final = moyenne(Score 1, Score 2, ..., Score 5) ± écart-type
```

Chaque donnée est utilisée **exactement 1 fois** pour la validation et **K-1 fois** pour l'entraînement.

### 3.2 Code avec cross_val_score

```python
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier
import numpy as np

model = RandomForestClassifier(n_estimators=100, random_state=42)

# --- Cross-validation basique (5-Fold) ---
scores = cross_val_score(
    model, X, y,
    cv=5,                  # Nombre de folds
    scoring='f1',          # Métrique
    n_jobs=-1              # Paralléliser
)

print(f"Scores par fold : {scores}")
print(f"F1 moyen : {scores.mean():.4f} (± {scores.std():.4f})")
```

### 3.3 Stratified K-Fold pour classes déséquilibrées

Le K-Fold classique ne garantit pas que chaque fold ait la même proportion de classes. Le **Stratified K-Fold** le fait.

```python
from sklearn.model_selection import StratifiedKFold

# --- Stratified K-Fold (recommandé pour la classification) ---
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores_strat = cross_val_score(
    model, X, y,
    cv=skf,                # Utiliser StratifiedKFold
    scoring='f1',
    n_jobs=-1
)

print(f"Stratified K-Fold - F1 : {scores_strat.mean():.4f} (± {scores_strat.std():.4f})")

# Vérifier les proportions dans chaque fold
for i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    prop = y[val_idx].mean()
    print(f"  Fold {i+1} - Proportion classe 1 : {prop:.2%}")
```

> 💡 **Conseil** : "Pour la classification, utilisez **toujours** `StratifiedKFold` ou passez `cv=StratifiedKFold(5)` à `cross_val_score`. C'est le comportement par défaut de sklearn quand vous passez un entier, mais c'est mieux d'être explicite."

### 3.4 Leave-One-Out (LOO)

Le LOO est un K-Fold où K = N (nombre d'échantillons). Chaque fold utilise **un seul échantillon** comme validation.

```python
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()

# Attention : très lent sur de gros datasets !
# Utilisez seulement avec < 200 échantillons
# scores_loo = cross_val_score(model, X, y, cv=loo, scoring='f1')
print(f"Nombre de folds avec LOO : {loo.get_n_splits(X)}")
```

| Méthode | K | Variance | Biais | Temps |
|---------|---|----------|-------|-------|
| 5-Fold | 5 | Modérée | Modéré | Rapide |
| 10-Fold | 10 | Faible | Faible | Modéré |
| LOO | N | Très faible | Très faible | Très lent |

### 3.5 Repeated K-Fold

Pour réduire la variance, on peut répéter le K-Fold avec des shuffles différents :

```python
from sklearn.model_selection import RepeatedStratifiedKFold

rskf = RepeatedStratifiedKFold(
    n_splits=5,      # K = 5
    n_repeats=10,    # Répéter 10 fois
    random_state=42
)

scores_repeated = cross_val_score(model, X, y, cv=rskf, scoring='f1', n_jobs=-1)
print(f"Repeated 5-Fold (x10) - F1 : {scores_repeated.mean():.4f} (± {scores_repeated.std():.4f})")
print(f"Nombre total de fits : {len(scores_repeated)}")  # 50
```

---

## 4. ⏰ Time Series Split

### 4.1 Pourquoi K-Fold ne marche pas pour les séries temporelles

En séries temporelles, les données futures dépendent des données passées. Si le fold de validation contient des données **passées** et le train des données **futures**, on a une **fuite de données** (data leakage).

```
K-Fold CLASSIQUE (MAUVAIS pour séries temporelles) :
Fold 1: [VAL_jan][TRAIN_fev][TRAIN_mar][TRAIN_avr][TRAIN_mai]
         ↑ Le modèle voit le futur avant le passé ! FUITE !

Time Series Split (BON) :
Fold 1: [TRAIN_jan][VAL_fev]
Fold 2: [TRAIN_jan][TRAIN_fev][VAL_mar]
Fold 3: [TRAIN_jan][TRAIN_fev][TRAIN_mar][VAL_avr]
Fold 4: [TRAIN_jan][TRAIN_fev][TRAIN_mar][TRAIN_avr][VAL_mai]
         ↑ Le modèle voit TOUJOURS le passé avant le futur ✓
```

### 4.2 TimeSeriesSplit de sklearn

```python
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
import numpy as np

# Simuler des données temporelles
n_samples = 100
X_ts = np.arange(n_samples).reshape(-1, 1)
y_ts = np.sin(X_ts.ravel() / 10) + np.random.normal(0, 0.1, n_samples)

# --- TimeSeriesSplit ---
tscv = TimeSeriesSplit(n_splits=5)

# Visualisation des folds
fig, ax = plt.subplots(figsize=(12, 5))
for i, (train_idx, val_idx) in enumerate(tscv.split(X_ts)):
    ax.scatter(train_idx, [i] * len(train_idx), c='blue', s=10, label='Train' if i == 0 else '')
    ax.scatter(val_idx, [i] * len(val_idx), c='red', s=10, label='Validation' if i == 0 else '')

ax.set_xlabel('Index temporel')
ax.set_ylabel('Fold')
ax.set_yticks(range(5))
ax.set_yticklabels([f'Fold {i+1}' for i in range(5)])
ax.set_title('TimeSeriesSplit - Visualisation des folds')
ax.legend(loc='upper left')
plt.tight_layout()
plt.show()

# Utilisation avec cross_val_score
from sklearn.linear_model import LinearRegression

scores_ts = cross_val_score(
    LinearRegression(), X_ts, y_ts,
    cv=tscv,
    scoring='neg_mean_squared_error'
)
print(f"MSE par fold : {-scores_ts}")
print(f"MSE moyen : {-scores_ts.mean():.4f}")
```

> ⚠️ **Attention** : "Pour les séries temporelles, n'utilisez **JAMAIS** un K-Fold classique. Utilisez toujours `TimeSeriesSplit` pour respecter l'ordre chronologique des données."

---

## 5. 📉 Courbes d'apprentissage

### 5.1 Diagnostic : underfitting vs overfitting

Les courbes d'apprentissage tracent le score en fonction du **nombre d'échantillons d'entraînement**. Elles permettent de diagnostiquer les problèmes du modèle.

```
CAS 1 : BON MODÈLE                     CAS 2 : OVERFITTING
Score                                   Score
1.0 │───── Train                        1.0 │───── Train
    │                                       │
    │                                       │
    │  ───── Validation                     │     Grand écart !
    │                                       │
    │  Les deux convergent                  │  ───── Validation
0.5 │                                   0.5 │
    └──────────────── Taille            └──────────────── Taille


CAS 3 : UNDERFITTING                   CAS 4 : BESOIN DE PLUS DE DONNÉES
Score                                   Score
1.0 │                                   1.0 │───── Train
    │                                       │
    │                                       │
    │                                       │  Converge mais pas encore
    │  ───── Train                          │
    │  ───── Validation                     │  ───── Validation
0.5 │  Les deux sont bas !              0.5 │  Encore en train de monter
    └──────────────── Taille            └──────────────── Taille
```

| Diagnostic | Symptôme | Solution |
|-----------|----------|----------|
| **Bon modèle** | Train et Val convergent à un score élevé | Rien à faire ! |
| **Overfitting** | Train élevé, Val bien plus bas | Régulariser, plus de données, simplifier |
| **Underfitting** | Train et Val tous deux bas | Modèle plus complexe, plus de features |
| **Besoin de données** | Val monte encore à la fin | Collecter plus de données |

### 5.2 Code complet avec visualisation

```python
from sklearn.model_selection import learning_curve
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import matplotlib.pyplot as plt

model = RandomForestClassifier(n_estimators=100, random_state=42)

# --- Calculer les courbes d'apprentissage ---
train_sizes, train_scores, val_scores = learning_curve(
    model, X, y,
    train_sizes=np.linspace(0.1, 1.0, 10),  # De 10% à 100% des données
    cv=5,
    scoring='f1',
    n_jobs=-1,
    random_state=42
)

# Moyennes et écarts-types
train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
val_mean = val_scores.mean(axis=1)
val_std = val_scores.std(axis=1)

# --- Visualiser ---
plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, 'b-o', label='Score Train')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='blue')
plt.plot(train_sizes, val_mean, 'r-o', label='Score Validation')
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color='red')
plt.xlabel("Nombre d'échantillons d'entraînement")
plt.ylabel('F1-Score')
plt.title("Courbe d'apprentissage — Random Forest")
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --- Interprétation automatique ---
gap = train_mean[-1] - val_mean[-1]
print(f"Score train final : {train_mean[-1]:.4f}")
print(f"Score val final   : {val_mean[-1]:.4f}")
print(f"Écart (gap)       : {gap:.4f}")

if gap > 0.1:
    print("→ OVERFITTING : le modèle mémorise les données d'entraînement.")
elif val_mean[-1] < 0.7:
    print("→ UNDERFITTING : le modèle est trop simple.")
else:
    print("→ BON MODÈLE : les scores convergent à un niveau élevé.")
```

---

## 6. 📈 Courbes de validation

### 6.1 Trouver le bon hyperparamètre

La courbe de validation trace le score en fonction de **la valeur d'un hyperparamètre**. Elle permet de trouver la valeur optimale.

```python
from sklearn.model_selection import validation_curve
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import matplotlib.pyplot as plt

# --- Courbe de validation pour max_depth ---
param_range = [1, 2, 3, 5, 7, 10, 15, 20, None]
param_range_plot = [1, 2, 3, 5, 7, 10, 15, 20, 25]  # Pour le plot

train_scores, val_scores = validation_curve(
    RandomForestClassifier(n_estimators=100, random_state=42),
    X, y,
    param_name='max_depth',
    param_range=param_range,
    cv=5,
    scoring='f1',
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

plt.figure(figsize=(10, 6))
plt.plot(param_range_plot, train_mean, 'b-o', label='Score Train')
plt.plot(param_range_plot, val_mean, 'r-o', label='Score Validation')
plt.xlabel('max_depth')
plt.ylabel('F1-Score')
plt.title('Courbe de validation — max_depth du Random Forest')
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Meilleur max_depth
best_idx = np.argmax(val_mean)
print(f"Meilleur max_depth : {param_range[best_idx]}")
print(f"F1 validation      : {val_mean[best_idx]:.4f}")
```

```
Score
1.0 │──────── Train
    │     ╱╲
    │    ╱  ╲───── Validation
    │   ╱
    │  ╱
    │ ╱        ← Zone optimale
0.5 │╱            (juste avant que Val baisse)
    └────────────────────────── max_depth
     1  2  3  5  7  10  15  20
     ← Underfitting  Overfitting →
```

---

## 7. ⚖️ Bias-Variance Tradeoff revisité

### 7.1 Lien avec underfitting/overfitting

```
Erreur totale = Biais² + Variance + Bruit irréductible

Erreur
  │
  │  ╲ Biais²                    ╱ Variance
  │   ╲                         ╱
  │    ╲                      ╱
  │     ╲        ╱──────────╱
  │      ╲      ╱ Erreur totale
  │       ╲   ╱
  │        ╲╱  ← Sweet spot
  │
  └──────────────────────── Complexité du modèle
     Simple                    Complexe
     (Underfitting)            (Overfitting)
     Biais élevé               Variance élevée
```

| | Biais élevé (Underfitting) | Variance élevée (Overfitting) |
|---|---|---|
| **Symptôme** | Score train ET val bas | Score train élevé, val bas |
| **Le modèle** | Est trop simple | Est trop complexe |
| **Solution** | Plus de features, modèle plus complexe | Régularisation, plus de données, simplifier |
| **Courbe d'apprentissage** | Les deux courbes convergent bas | Grand écart entre les courbes |

### 7.2 Comment diagnostiquer

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

# --- Modèle trop simple (underfitting) ---
tree_simple = DecisionTreeClassifier(max_depth=1, random_state=42)
scores_simple = cross_val_score(tree_simple, X, y, cv=5, scoring='f1')
tree_simple.fit(X_train, y_train)
train_score_simple = f1_score(y_train, tree_simple.predict(X_train))

# --- Modèle trop complexe (overfitting) ---
tree_complex = DecisionTreeClassifier(max_depth=None, random_state=42)
scores_complex = cross_val_score(tree_complex, X, y, cv=5, scoring='f1')
tree_complex.fit(X_train, y_train)
train_score_complex = f1_score(y_train, tree_complex.predict(X_train))

# --- Modèle équilibré ---
tree_balanced = DecisionTreeClassifier(max_depth=5, random_state=42)
scores_balanced = cross_val_score(tree_balanced, X, y, cv=5, scoring='f1')
tree_balanced.fit(X_train, y_train)
train_score_balanced = f1_score(y_train, tree_balanced.predict(X_train))

print("=== Diagnostic ===")
print(f"Simple  (depth=1)    : Train={train_score_simple:.3f}, Val={scores_simple.mean():.3f} → Underfitting")
print(f"Complexe (depth=None): Train={train_score_complex:.3f}, Val={scores_complex.mean():.3f} → Overfitting")
print(f"Équilibré (depth=5)  : Train={train_score_balanced:.3f}, Val={scores_balanced.mean():.3f} → Bon compromis")
```

---

## 8. 🔧 GridSearchCV et RandomizedSearchCV

### 8.1 GridSearchCV : la recherche exhaustive

GridSearchCV teste **toutes les combinaisons** d'hyperparamètres et utilise la cross-validation pour évaluer chacune.

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# --- Définir la grille ---
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 10, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Nombre total de combinaisons
n_combinaisons = 3 * 4 * 3 * 3  # = 108
print(f"Nombre de combinaisons : {n_combinaisons}")
print(f"Avec 5-Fold CV : {n_combinaisons * 5} = {n_combinaisons * 5} fits !")

# --- GridSearchCV ---
grid = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,                    # 5-Fold CV
    scoring='f1',            # Métrique à optimiser
    n_jobs=-1,               # Paralléliser
    verbose=1,
    return_train_score=True  # Pour diagnostiquer l'overfitting
)
grid.fit(X_train, y_train)

# --- Résultats ---
print(f"\nMeilleurs paramètres : {grid.best_params_}")
print(f"Meilleur F1 (CV)     : {grid.best_score_:.4f}")

# Évaluer sur le test set
y_pred_best = grid.best_estimator_.predict(X_test)
print(f"F1 test              : {f1_score(y_test, y_pred_best):.4f}")

# Analyser les résultats
import pandas as pd
results = pd.DataFrame(grid.cv_results_)
print("\n=== Top 5 combinaisons ===")
cols = ['rank_test_score', 'mean_test_score', 'std_test_score', 'params']
print(results.nsmallest(5, 'rank_test_score')[cols].to_string(index=False))
```

### 8.2 RandomizedSearchCV : la recherche intelligente

Quand l'espace de recherche est trop grand, RandomizedSearchCV tire **aléatoirement** un nombre fixe de combinaisons.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

# --- Distributions d'hyperparamètres ---
param_distributions = {
    'n_estimators': randint(50, 500),          # Entier entre 50 et 500
    'max_depth': [3, 5, 7, 10, 15, 20, None], # Liste de choix
    'min_samples_split': randint(2, 20),       # Entier entre 2 et 20
    'min_samples_leaf': randint(1, 10),        # Entier entre 1 et 10
    'max_features': uniform(0.1, 0.9),         # Float entre 0.1 et 1.0
}

# --- RandomizedSearchCV ---
random_search = RandomizedSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_distributions=param_distributions,
    n_iter=50,               # Tester 50 combinaisons (au lieu de toutes)
    cv=5,
    scoring='f1',
    n_jobs=-1,
    random_state=42,
    verbose=1,
    return_train_score=True
)
random_search.fit(X_train, y_train)

print(f"\nMeilleurs paramètres : {random_search.best_params_}")
print(f"Meilleur F1 (CV)     : {random_search.best_score_:.4f}")

y_pred_random = random_search.best_estimator_.predict(X_test)
print(f"F1 test              : {f1_score(y_test, y_pred_random):.4f}")
```

### 8.3 Quand utiliser quoi ?

| Critère | GridSearchCV | RandomizedSearchCV |
|---------|-------------|-------------------|
| **Espace de recherche** | Petit (< 100 combinaisons) | Grand (> 1000 combinaisons) |
| **Exhaustivité** | Teste TOUT | Échantillonne aléatoirement |
| **Temps** | Long si beaucoup de paramètres | Contrôlé via `n_iter` |
| **Garantie** | Trouve le meilleur de la grille | Peut rater le meilleur |
| **Distributions** | Listes de valeurs | Distributions continues |
| **Premier choix** | Tuning fin (2-3 paramètres) | Exploration large (> 4 paramètres) |

> 💡 **Conseil** : "Stratégie recommandée : commencez par un `RandomizedSearchCV` avec `n_iter=100` pour explorer largement, puis affinez avec un `GridSearchCV` sur une grille réduite autour des meilleurs paramètres trouvés."

---

## 🎯 Points clés à retenir

1. **Toujours** séparer train/test avant toute modélisation pour estimer honnêtement les performances
2. **Stratifier** le split pour conserver les proportions de classes (`stratify=y`)
3. **random_state** garantit la reproductibilité des résultats
4. **3 ensembles** (train/val/test) : le test set ne sert qu'UNE seule fois à la fin
5. **Cross-validation** utilise chaque donnée pour l'entraînement ET la validation
6. **StratifiedKFold** est indispensable pour les classes déséquilibrées
7. **TimeSeriesSplit** est obligatoire pour les données temporelles (pas de K-Fold !)
8. **Courbes d'apprentissage** : diagnostic overfitting (gap) vs underfitting (scores bas)
9. **GridSearchCV** pour explorer exhaustivement un petit espace de paramètres
10. **RandomizedSearchCV** pour explorer efficacement un grand espace de paramètres

---

## ✅ Checklist de validation

- [ ] Je sais faire un train/test split avec stratification et random_state
- [ ] Je comprends pourquoi il faut 3 ensembles (train/val/test)
- [ ] Je sais implémenter un K-Fold et un Stratified K-Fold
- [ ] Je sais utiliser `cross_val_score` pour évaluer un modèle
- [ ] Je comprends pourquoi K-Fold ne marche pas pour les séries temporelles
- [ ] Je sais utiliser `TimeSeriesSplit`
- [ ] Je sais tracer et interpréter les courbes d'apprentissage (4 cas)
- [ ] Je sais tracer une courbe de validation pour trouver le bon hyperparamètre
- [ ] Je comprends le bias-variance tradeoff et son lien avec under/overfitting
- [ ] Je sais utiliser GridSearchCV et RandomizedSearchCV
- [ ] Je connais la stratégie "RandomizedSearch large → GridSearch fin"

---

**Précédent** : [Chapitre 12 : Métriques — Au-delà de l'Accuracy](12-metriques-classification.md)

**Suivant** : [Chapitre 14 : Interpréter ses Modèles et Éthique du ML](14-interpretabilite-ethique.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Overfitting & underfitting](https://www.youtube.com/results?search_query=machine+learnia+overfitting+underfitting+francais) | Machine Learnia | FR | Le sur/sous-apprentissage |
| [Validation croisée](https://www.youtube.com/results?search_query=statquest+cross+validation) | StatQuest | EN | Évaluer sans se mentir |
| [Compromis biais-variance](https://www.youtube.com/results?search_query=statquest+bias+variance+tradeoff) | StatQuest | EN | Le dilemme central du ML |
