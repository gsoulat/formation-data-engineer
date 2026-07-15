# Cheatsheet Machine Learning

> Aide-mémoire à garder sous la main pendant tout le parcours

---

## 🔧 Setup rapide

```bash
# Installation des dépendances
uv add numpy pandas matplotlib seaborn scikit-learn xgboost lightgbm shap fastapi uvicorn joblib
```

```python
# Imports standards
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, classification_report,
                             confusion_matrix, mean_squared_error, r2_score)
```

---

## 📊 Exploration des données

```python
df = pd.read_csv("data.csv")

# Vue d'ensemble
df.shape                    # (lignes, colonnes)
df.info()                   # Types + valeurs manquantes
df.describe()               # Stats numériques
df.describe(include='object')  # Stats catégorielles
df.head()                   # Premières lignes
df.dtypes                   # Types de colonnes

# Qualité
df.isnull().sum()           # Manquants par colonne
df.isnull().mean() * 100    # % manquants
df.duplicated().sum()       # Doublons
df['col'].value_counts()    # Distribution catégorielle
df['col'].nunique()         # Nombre de valeurs uniques

# Corrélations
df.corr()                   # Matrice de corrélation
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')
```

---

## 🔄 Preprocessing

### Split Train/Test

```python
X = df.drop('target', axis=1)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

### Scaling

| Scaler | Formule | Quand |
|--------|---------|-------|
| `StandardScaler` | (x - μ) / σ | Défaut, outliers modérés |
| `MinMaxScaler` | (x - min) / (max - min) | Borner entre 0 et 1 |
| `RobustScaler` | (x - médiane) / IQR | Beaucoup d'outliers |

### Encodage

| Méthode | Quand | Code |
|---------|-------|------|
| One-Hot | < 5 catégories, modèles linéaires | `OneHotEncoder(drop='first')` |
| Ordinal | Ordre naturel (low/med/high) | `OrdinalEncoder(categories=...)` |
| Label | Arbres de décision | `LabelEncoder()` |

### Pipeline complet

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

num_features = ['age', 'salary', 'tenure']
cat_features = ['contract', 'payment']

num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

cat_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(drop='first', handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', num_pipeline, num_features),
    ('cat', cat_pipeline, cat_features)
])

# Pipeline complet avec modèle
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', LogisticRegression(max_iter=1000))
])

full_pipeline.fit(X_train, y_train)
y_pred = full_pipeline.predict(X_test)
```

---

## 🤖 Algorithmes

### Classification

| Algorithme | sklearn | Normaliser ? | Forces |
|-----------|---------|-------------|--------|
| Régression Logistique | `LogisticRegression(max_iter=1000)` | Oui | Baseline, interprétable |
| KNN | `KNeighborsClassifier(n_neighbors=5)` | **Oui** | Simple, non-paramétrique |
| SVM | `SVC(kernel='rbf')` | **Oui** | Petits datasets |
| Arbre de Décision | `DecisionTreeClassifier(max_depth=5)` | Non | Interprétable |
| Random Forest | `RandomForestClassifier(n_estimators=100)` | Non | Robuste, polyvalent |
| Gradient Boosting | `GradientBoostingClassifier()` | Non | Performant |
| XGBoost | `XGBClassifier(n_estimators=100)` | Non | Champion Kaggle |
| LightGBM | `LGBMClassifier(n_estimators=100)` | Non | Rapide, grands datasets |

### Régression

| Algorithme | sklearn | Normaliser ? |
|-----------|---------|-------------|
| Régression Linéaire | `LinearRegression()` | Oui (pour Ridge/Lasso) |
| Ridge | `Ridge(alpha=1.0)` | Oui |
| Lasso | `Lasso(alpha=1.0)` | Oui |
| Random Forest | `RandomForestRegressor()` | Non |
| XGBoost | `XGBRegressor()` | Non |

### Pattern universel sklearn

```python
model = Algorithm(hyperparams)
model.fit(X_train, y_train)        # Entraîner
y_pred = model.predict(X_test)     # Prédire
score = model.score(X_test, y_test)  # Évaluer
```

---

## 📏 Métriques

### Classification

| Métrique | Formule | Quand l'utiliser | Code |
|----------|---------|-----------------|------|
| Accuracy | (TP+TN)/Total | Classes équilibrées | `accuracy_score(y, y_pred)` |
| Precision | TP/(TP+FP) | FP coûteux (spam) | `precision_score(y, y_pred)` |
| Recall | TP/(TP+FN) | FN coûteux (cancer) | `recall_score(y, y_pred)` |
| F1 | 2*P*R/(P+R) | Défaut | `f1_score(y, y_pred)` |
| AUC-ROC | Aire sous ROC | Vue d'ensemble | `roc_auc_score(y, y_proba)` |

```python
# Rapport complet
print(classification_report(y_test, y_pred))

# Matrice de confusion
from sklearn.metrics import ConfusionMatrixDisplay
ConfusionMatrixDisplay.from_predictions(y_test, y_pred, cmap='Blues')
```

### Régression

| Métrique | Code | Idéal |
|----------|------|-------|
| MSE | `mean_squared_error(y, y_pred)` | → 0 |
| RMSE | `mean_squared_error(y, y_pred, squared=False)` | → 0 |
| MAE | `mean_absolute_error(y, y_pred)` | → 0 |
| R² | `r2_score(y, y_pred)` | → 1 |

---

## 🔍 Validation

```python
# Cross-validation
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"F1: {scores.mean():.4f} ± {scores.std():.4f}")

# GridSearch
from sklearn.model_selection import GridSearchCV
grid = GridSearchCV(model, param_grid, cv=5, scoring='f1', n_jobs=-1)
grid.fit(X_train, y_train)
print(grid.best_params_)
print(grid.best_score_)

# Courbe d'apprentissage
from sklearn.model_selection import learning_curve
train_sizes, train_scores, test_scores = learning_curve(
    model, X, y, cv=5, scoring='f1',
    train_sizes=np.linspace(0.1, 1.0, 10)
)
```

---

## 🧠 Interprétabilité

```python
# Feature Importance (arbres)
importances = model.feature_importances_
pd.Series(importances, index=feature_names).sort_values().plot.barh()

# Permutation Importance (tous modèles)
from sklearn.inspection import permutation_importance
result = permutation_importance(model, X_test, y_test, n_repeats=10)

# SHAP
import shap
explainer = shap.TreeExplainer(model)  # ou shap.Explainer(model)
shap_values = explainer(X_test)
shap.summary_plot(shap_values, X_test)            # Global
shap.plots.waterfall(shap_values[0])               # Individuel
shap.plots.dependence(shap_values, "feature_name") # Dépendance
```

---

## 🚀 Production

### Sérialisation

```python
import joblib

# Sauvegarder
joblib.dump(full_pipeline, 'models/pipeline.joblib')

# Charger
pipeline = joblib.load('models/pipeline.joblib')
prediction = pipeline.predict(new_data)
```

### API FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()
pipeline = joblib.load("models/pipeline.joblib")

class ClientData(BaseModel):
    tenure: int
    monthly_charges: float
    contract: str
    # ...

@app.post("/predict")
def predict(client: ClientData):
    df = pd.DataFrame([client.model_dump()])
    proba = pipeline.predict_proba(df)[0][1]
    return {"churn_probability": round(proba, 4),
            "prediction": "churn" if proba > 0.5 else "no_churn"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install .
COPY src/ src/
COPY models/ models/
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ⚠️ Erreurs courantes

| Erreur | Problème | Solution |
|--------|----------|----------|
| Accuracy de 99% | Data leakage probable | Vérifier le pipeline, les features |
| KNN mauvais score | Pas de normalisation | `StandardScaler` avant KNN |
| fit_transform sur test | Leakage | `fit_transform(train)` puis `transform(test)` |
| Modèle instable | Overfitting | Réduire complexité, plus de données, régularisation |
| Score train >> test | Overfitting | `max_depth`, `min_samples`, cross-validation |
| Score train ≈ test ≈ bas | Underfitting | Modèle trop simple, plus de features |
| Mémoire saturée | One-Hot sur haute cardinalité | Target encoding ou feature hashing |

---

## 🗺️ Guide de choix rapide

> 📖 Pour la **méthode de décision complète** (problème → métrique selon le coût métier → modèle),
> voir le [chapitre 23 — Choisir son modèle et ses métriques](23-choisir-modele-et-metriques.md).

```
Quel type de problème ?
├── Classification (catégorie)
│   ├── Baseline → Logistic Regression
│   ├── Petit dataset → SVM
│   ├── Interprétabilité requise → Decision Tree
│   └── Performance max → XGBoost / LightGBM
│
├── Régression (nombre)
│   ├── Baseline → Linear Regression
│   ├── Régularisation → Ridge / Lasso
│   └── Performance max → XGBoost / LightGBM
│
└── Clustering (groupes)
    ├── Nombre de clusters connu → KMeans
    ├── Forme arbitraire → DBSCAN
    └── Hiérarchie → Agglomerative Clustering
```
