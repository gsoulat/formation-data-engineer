# Chapitre 22 : Réduction de dimension — PCA (Analyse en Composantes Principales)

## 🎯 Objectifs

- Comprendre le problème de la **malédiction de la dimension** et pourquoi trop de features nuit aux modèles
- Saisir la notion de **variance portée par un axe** (l'information contenue dans une direction)
- Comprendre ce que sont les **composantes principales** et comment elles sont construites
- Savoir lire et exploiter la **variance expliquée cumulée** pour choisir le bon nombre de composantes
- Utiliser la PCA pour **visualiser en 2D/3D** des données à haute dimension
- Intégrer la PCA comme **étape de prétraitement** dans un pipeline scikit-learn
- Connaître les **pièges** de la PCA et savoir quand (ne pas) l'utiliser

---

## 1. 🧠 Le problème avant la solution : trop de dimensions, ça coince

### 1.1 Le point de départ concret

Vous travaillez sur un jeu de données de tumeurs (le célèbre `breast_cancer` de scikit-learn). Chaque tumeur est décrite par **30 mesures** : rayon moyen, texture, périmètre, aire, compacité, symétrie... pour chaque cellule mesurée.

30 colonnes, c'est déjà **impossible à visualiser** (on ne dessine pas un nuage de points en 30 dimensions). Et quand vous entraînez un modèle, vous remarquez trois choses gênantes :

- il est **lent** (30 features × des milliers de calculs) ;
- il **surapprend** facilement (trop de degrés de liberté) ;
- beaucoup de colonnes semblent **dire la même chose** (le rayon, le périmètre et l'aire d'une tumeur sont fortement corrélés — ils grandissent ensemble).

> 💡 **Conseil** : "Avoir beaucoup de features n'est pas toujours une richesse. Souvent, plusieurs colonnes portent la **même information** sous des habits différents. La réduction de dimension cherche à garder l'essentiel en jetant la redondance."

### 1.2 La malédiction de la dimension

Quand le nombre de dimensions augmente, l'espace devient **immense et vide**. Vos points, eux, restent en nombre limité : ils se retrouvent **noyés**, tous à peu près à la même distance les uns des autres.

```
   1D : 10 points sur une ligne         → l'espace est bien "rempli"
   ●─●─●─●─●─●─●─●─●─●

   2D : 10 points sur un carré          → déjà plus clairsemé
   ●     ●          ●
      ●        ●
   ●        ●    ●
        ●            ●

   10D : 10 points dans un hypercube    → l'espace est quasi VIDE
   (chaque point est "seul dans son coin", loin de tous les autres)
```

Concrètement, plus la dimension monte :

| Conséquence | Pourquoi c'est un problème |
|-------------|----------------------------|
| Les distances **se ressemblent toutes** | KNN, k-means... perdent leur sens (plus de "proche" ni "loin") |
| L'espace est **vide** | Il faudrait exponentiellement plus de données pour le remplir |
| Le modèle **surapprend** | Trop de features = trop de liberté pour "coller" au bruit |
| Les calculs sont **lents** | Temps et mémoire explosent |

> ⚠️ **Attention** : "La malédiction de la dimension explique pourquoi KNN (chapitre 3) fonctionne bien en 2D mais s'effondre en 100D : en haute dimension, tous les voisins sont à peu près à la même distance, la notion de 'plus proche' devient vide de sens."

Illustrons que la distance s'homogénéise quand la dimension grimpe :

```python
import numpy as np

rng = np.random.default_rng(42)

for d in [2, 10, 100, 1000]:
    # 500 points aléatoires en dimension d
    points = rng.random((500, d))
    # distances de chaque point au premier point
    dists = np.linalg.norm(points - points[0], axis=1)[1:]
    ratio = dists.max() / dists.min()  # écart entre le + loin et le + proche
    print(f"dim={d:4d} | dist min={dists.min():.2f}"
          f" | dist max={dists.max():.2f} | ratio max/min={ratio:.2f}")
```

```
dim=   2 | dist min=0.02 | dist max=1.13 | ratio max/min=56.50
dim=  10 | dist min=0.55 | dist max=1.87 | ratio max/min=3.40
dim= 100 | dist min=2.96 | dist max=4.79 | ratio max/min=1.62
dim=1000 | dist min=11.5 | dist max=13.9 | ratio max/min=1.21
```

En 2D, le point le plus loin est 56× plus loin que le plus proche : la notion de proximité est **nette**. En 1000D, le ratio tombe à 1,2 : tout est à la **même distance**, la notion de proximité s'est **évaporée**.

### 1.3 L'idée de la solution

La **PCA** (Principal Component Analysis, ou Analyse en Composantes Principales) répond à ce problème avec une idée simple :

> Trouver de **nouveaux axes**, moins nombreux, qui capturent le **maximum d'information** des données originales. On projette ensuite les données sur ces quelques axes et on jette le reste.

Passer de 30 features à 2 ou 3 axes bien choisis, c'est :
- pouvoir **visualiser** le nuage,
- **accélérer** les modèles,
- **réduire le surapprentissage** en enlevant le bruit et la redondance.

Reste à définir ce qu'on appelle "l'information" contenue dans une direction. C'est la **variance**.

---

## 2. 📊 L'intuition centrale : la variance portée par un axe

### 2.1 Variance = information = "l'axe qui étale les points"

La variance mesure à quel point les points sont **étalés** le long d'une direction. Et l'intuition clé de la PCA est :

> **Une direction où les points sont bien étalés porte beaucoup d'information. Une direction où tous les points sont tassés au même endroit n'apporte presque rien.**

Imaginez un nuage de points en forme de cigare allongé :

```
      y
      │        ●  ●
      │     ●  ●  ●  ●
      │   ●  ●  ●  ●  ●  ●         ← le nuage s'étire "en diagonale"
      │  ●  ●  ●  ●  ●
      │    ●  ●  ●
      └──────────────────── x

  Axe le plus étalé (grande variance) ────►  ↗  = 1re composante principale
  Axe perpendiculaire (peu de variance) ──►  ↖  = 2e composante principale
```

- La direction **la plus étalée** (le long du cigare) porte le plus d'information : c'est la **1re composante principale (PC1)**.
- La direction **perpendiculaire** (l'épaisseur du cigare) porte peu d'information : c'est la **2e composante principale (PC2)**.

Si on ne devait garder **qu'un seul axe** pour résumer ce nuage, on garderait évidemment le long du cigare (PC1) : on perd juste "l'épaisseur", quasi négligeable.

> 💡 **Conseil** : "PCA cherche les directions dans lesquelles vos données **varient le plus**. C'est là que se cache l'information qui distingue vos observations les unes des autres. Une feature (ou une direction) constante ne distingue rien : sa variance est nulle."

### 2.2 Projeter, c'est aplatir en gardant le maximum

"Réduire la dimension", c'est **projeter** (aplatir) le nuage sur les axes qu'on garde. Le bon axe est celui qui, après projection, **conserve le plus d'étalement**.

```
   Nuage 2D           Projeté sur PC1 (bon axe)     Projeté sur PC2 (mauvais axe)
     ●  ●                                                 
   ●  ●  ●     ──►   ●─●─●─●─●─●─●─●   (bien étalé)   ──► ●●●●●● (tout tassé)
     ●  ●              points bien séparés               points confondus
```

Projeter sur PC1 garde les points **distincts** ; projeter sur PC2 les **écrase les uns sur les autres**. PCA choisit donc automatiquement PC1.

### 2.3 Les composantes principales, en résumé

- Les composantes principales sont de **nouveaux axes**, construits comme des **combinaisons des features d'origine**.
- Elles sont **classées** de la plus informative (PC1, variance max) à la moins informative.
- Elles sont **perpendiculaires** (orthogonales) entre elles : chacune capture une information **nouvelle**, non redondante avec les précédentes.
- On en garde **quelques-unes** (les premières) et on jette les dernières.

---

## 3. 🔬 Formalisation légère (juste ce qu'il faut)

Pas de démonstration ici, juste la mécanique à connaître pour ne pas utiliser la PCA comme une boîte noire.

### 3.1 Les étapes de la PCA

```
Algorithme PCA :
─────────────────────────────────────────────────────────────
1. CENTRER (et standardiser) les données
   → chaque feature a une moyenne de 0 (et un écart-type de 1)
2. Calculer la matrice de covariance
   → qui varie avec quoi ? quelles features bougent ensemble ?
3. Trouver les directions principales
   → ce sont les "vecteurs propres" de cette matrice
4. Les classer par variance décroissante
   → PC1 = plus grande variance, PC2 = 2e, etc.
5. Garder les k premières composantes
6. Projeter les données dessus → nouvelles coordonnées (k dimensions)
─────────────────────────────────────────────────────────────
```

Les mots "matrice de covariance" et "vecteurs propres" cachent des maths, mais **scikit-learn fait tout ça pour vous**. Ce qu'il faut retenir :

> Chaque composante principale est une **direction** de l'espace d'origine, et à chaque composante est associée une **quantité de variance** (l'information qu'elle capture).

### 3.2 La variance expliquée

Pour chaque composante, scikit-learn donne le **ratio de variance expliquée** : la part de l'information totale qu'elle capture.

```
variance_expliquée(PC_i) = variance le long de PC_i / variance totale
```

Exemple pour un jeu à 4 features :

```
PC1 : 72 %   ████████████████████████████████████░░░░░░░░░░  ← domine
PC2 : 19 %   █████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
PC3 :  6 %   ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
PC4 :  3 %   █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
             ────────────────────────────────────────────
             PC1 + PC2 = 91 % de l'information avec 2 axes sur 4 !
```

### 3.3 Pourquoi il faut standardiser AVANT

La PCA se base sur la variance. Or, une feature exprimée dans une grande échelle (un salaire en euros, 20 000–100 000) a mécaniquement une **variance énorme** comparée à une feature en petite échelle (un âge, 20–60). Sans précaution, la PCA croirait que le salaire est "l'axe le plus important" **juste à cause de son unité**.

> ⚠️ **Attention** : "La PCA est **extrêmement sensible aux échelles**. Il faut presque toujours passer un `StandardScaler` avant. Oublier cette étape est l'erreur n°1 : votre première composante ne fera que refléter la feature ayant les plus grands chiffres, pas la plus informative."

---

## 4. 🧪 PCA en pratique avec scikit-learn

### 4.1 Un premier exemple complet sur Iris

Le dataset **Iris** (150 fleurs, 4 mesures : longueur/largeur des pétales et sépales) est parfait pour débuter : 4 dimensions qu'on va réduire à 2.

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 1. Charger les données
iris = load_iris()
X, y = iris.data, iris.target
print(f"Données d'origine : {X.shape}")   # (150, 4)

# 2. TOUJOURS standardiser avant une PCA
X_scaled = StandardScaler().fit_transform(X)

# 3. Appliquer la PCA en gardant 2 composantes
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
print(f"Après PCA          : {X_pca.shape}")   # (150, 2)

# 4. Combien d'information a-t-on gardée ?
print(f"\nVariance expliquée par composante : {pca.explained_variance_ratio_}")
print(f"Variance expliquée cumulée        : {pca.explained_variance_ratio_.sum():.2%}")
```

```
Données d'origine : (150, 4)
Après PCA          : (150, 2)

Variance expliquée par composante : [0.72962445 0.22850762]
Variance expliquée cumulée        : 95.81%
```

**En passant de 4 dimensions à 2, on conserve près de 96 % de l'information.** On a divisé le nombre de features par deux presque gratuitement.

### 4.2 Attributs utiles de l'objet PCA

```python
# Ratio de variance expliquée par chaque composante
print("explained_variance_ratio_ :", pca.explained_variance_ratio_)

# Les "poids" de chaque feature dans chaque composante (les directions)
print("\ncomponents_ (shape) :", pca.components_.shape)  # (2, 4) : 2 PC × 4 features

# Interprétation : de quoi est faite PC1 ?
import pandas as pd
loadings = pd.DataFrame(
    pca.components_.T,
    columns=['PC1', 'PC2'],
    index=iris.feature_names
)
print("\nContribution de chaque feature aux composantes :")
print(loadings.round(3))
```

```
Contribution de chaque feature aux composantes :
                   PC1    PC2
sepal length (cm) 0.521 -0.377
sepal width (cm) -0.269 -0.923
petal length (cm) 0.580 -0.024
petal width (cm)  0.565 -0.067
```

Lecture : **PC1** est portée surtout par la longueur et la largeur des **pétales** (poids ~0,58 et 0,57) — c'est l'axe "taille de la fleur". **PC2** est dominée par la **largeur des sépales** (−0,92). PCA a donc "inventé" un axe résumant la taille globale de la fleur.

---

## 5. 📈 Choisir le nombre de composantes : la variance expliquée cumulée

### 5.1 Le problème : combien d'axes garder ?

Réduire à 2 dimensions, c'est pratique pour visualiser. Mais pour **prétraiter avant un modèle**, on veut souvent garder plus (5, 10...) sans en garder trop. Comment choisir ?

On regarde la **variance expliquée cumulée** : on empile les composantes une à une et on regarde combien d'information totale on atteint.

### 5.2 Le graphe "coude" (scree plot / courbe cumulée)

Sur le dataset `breast_cancer` (30 features), traçons la courbe cumulée :

```python
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X, y = load_breast_cancer(return_X_y=True)
X_scaled = StandardScaler().fit_transform(X)

# PCA sans limiter le nombre de composantes → on les garde toutes (30)
pca_full = PCA().fit(X_scaled)
cumul = np.cumsum(pca_full.explained_variance_ratio_)

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cumul) + 1), cumul, 'o-', color='steelblue')
plt.axhline(y=0.95, color='red', linestyle='--', label='Seuil 95 %')
plt.xlabel("Nombre de composantes")
plt.ylabel("Variance expliquée cumulée")
plt.title("Variance expliquée cumulée — breast_cancer (30 features)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# À partir de combien de composantes atteint-on 95 % ?
n_95 = np.argmax(cumul >= 0.95) + 1
print(f"Il faut {n_95} composantes pour atteindre 95 % de variance.")
print(f"Variance avec 2 composantes : {cumul[1]:.2%}")
```

```
Il faut 10 composantes pour atteindre 95 % de variance.
Variance avec 2 composantes : 63.24%
```

```
   Variance cumulée
   1.0 │                         ● ● ● ● ● ● ● ●
       │                 ● ● ● ●
  0.95 │──────────●─●─●────────────────────── seuil 95 %
       │      ●
       │    ●
   0.6 │  ●
       │ ●   ← "coude" : après, chaque composante n'ajoute presque rien
       └────────────────────────────────── nb composantes
         1  3  5  7  9  11 ...          30
```

Sur les 30 features de départ, **10 composantes suffisent** pour garder 95 % de l'information. On divise par 3 le nombre de dimensions.

### 5.3 Laisser scikit-learn choisir automatiquement

Astuce très pratique : passer un **float entre 0 et 1** à `n_components`, et PCA garde juste assez de composantes pour atteindre ce seuil de variance.

```python
# "Garde-moi assez de composantes pour conserver 95 % de la variance"
pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X_scaled)

print(f"Composantes retenues : {pca.n_components_}")   # 10
print(f"Dimension finale     : {X_reduced.shape}")     # (569, 10)
print(f"Variance conservée   : {pca.explained_variance_ratio_.sum():.2%}")
```

```
Composantes retenues : 10
Dimension finale     : (569, 10)
Variance conservée   : 95.16%
```

> 💡 **Conseil** : "Pour la **visualisation**, on force `n_components=2` ou `3`. Pour le **prétraitement**, préférez `n_components=0.95` (ou 0.99) : vous laissez PCA garder juste ce qu'il faut d'information, sans choisir le nombre d'axes à la main."

---

## 6. 👁️ Visualiser des données à haute dimension en 2D / 3D

### 6.1 Visualisation 2D

L'un des usages les plus courants de la PCA : **projeter un nuage de haute dimension sur un plan** pour le voir enfin. Reprenons Iris (4D → 2D).

```python
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

iris = load_iris()
X_scaled = StandardScaler().fit_transform(iris.data)
X_pca = PCA(n_components=2).fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
for classe, nom, couleur in zip([0, 1, 2], iris.target_names,
                                ['#e41a1c', '#377eb8', '#4daf4a']):
    mask = iris.target == classe
    plt.scatter(X_pca[mask, 0], X_pca[mask, 1],
                c=couleur, label=nom, edgecolors='black', alpha=0.8)

plt.xlabel("Composante principale 1 (73 % de variance)")
plt.ylabel("Composante principale 2 (23 % de variance)")
plt.title("Iris projeté en 2D par PCA")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

```
   PC2
    │        setosa
    │      ● ●● ●
    │     ● ●● ●●         versicolor    virginica
    │      ● ● ●        ▲ ▲ ▲          ■ ■ ■
    │                  ▲ ▲▲ ▲▲        ■ ■■ ■■
    │                   ▲ ▲▲ ▲ ■■ ■ ■■
    └──────────────────────────────────── PC1

  → setosa (●) est TRÈS séparée des deux autres,
    même après avoir réduit 4D à 2D.
```

On voit d'un coup d'œil que la classe *setosa* est parfaitement isolée, alors que *versicolor* et *virginica* se chevauchent un peu. Cette information était invisible en 4 dimensions.

### 6.2 Visualisation 3D

Avec `n_components=3`, on peut faire un nuage 3D — utile quand 2 composantes ne suffisent pas à séparer les groupes.

```python
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

wine = load_wine()   # 178 vins, 13 features chimiques, 3 cépages
X_scaled = StandardScaler().fit_transform(wine.data)
X_pca = PCA(n_components=3).fit_transform(X_scaled)

fig = plt.figure(figsize=(11, 8))
ax = fig.add_subplot(111, projection='3d')
for classe, couleur in zip([0, 1, 2], ['#e41a1c', '#377eb8', '#4daf4a']):
    mask = wine.target == classe
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1], X_pca[mask, 2],
               c=couleur, label=wine.target_names[classe],
               edgecolors='black', alpha=0.8)

ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")
ax.set_title("Wine (13 features) projeté en 3D par PCA")
ax.legend()
plt.show()

print("Variance cumulée (3 PC) :",
      f"{PCA(n_components=3).fit(X_scaled).explained_variance_ratio_.sum():.2%}")
```

```
Variance cumulée (3 PC) : 66.53%
```

Ici 3 composantes ne capturent que ~67 % de la variance : Wine est plus "complexe" qu'Iris, mais les 3 cépages se distinguent déjà nettement dans ce nuage 3D.

> 💡 **Conseil** : "Pour visualiser des **clusters** ou des **classes**, PCA est un excellent premier réflexe. Si les groupes se mélangent trop après projection, essayez **t-SNE** ou **UMAP**, conçus pour préserver la structure locale au prix de l'interprétabilité."

---

## 7. ⚙️ PCA en prétraitement avant un modèle

### 7.1 Pourquoi mettre une PCA avant un modèle ?

Réduire la dimension avant d'entraîner permet de :
- **accélérer** l'entraînement (moins de features),
- **réduire le surapprentissage** en supprimant bruit et redondance,
- **régulariser** implicitement le modèle.

Le tout est de mettre la PCA **dans un pipeline**, pour qu'elle soit apprise uniquement sur le train (voir chapitre sur le data leakage).

### 7.2 Le pipeline correct

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Pipeline : standardisation → PCA (95 % de variance) → régression logistique
pipe_pca = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=0.95)),
    ('clf', LogisticRegression(max_iter=1000)),
])

pipe_pca.fit(X_train, y_train)

print(f"Composantes retenues : {pipe_pca.named_steps['pca'].n_components_}")
print(f"Accuracy (test)      : {pipe_pca.score(X_test, y_test):.2%}")
```

```
Composantes retenues : 10
Accuracy (test)      : 97.37%
```

> ⚠️ **Attention** : "La PCA **doit** être `fit` uniquement sur les données d'entraînement, puis appliquée (`transform`) au test. La mettre dans un `Pipeline` garantit ça automatiquement. Faire un `pca.fit_transform` sur **tout** le dataset avant le split est un **data leakage** classique."

### 7.3 Avec ou sans PCA : ça change quoi ?

Comparons un même modèle avec et sans PCA, en validation croisée :

```python
from sklearn.model_selection import cross_val_score

# SANS PCA
pipe_sans = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression(max_iter=1000)),
])

scores_sans = cross_val_score(pipe_sans, X, y, cv=5, scoring='accuracy')
scores_avec = cross_val_score(pipe_pca, X, y, cv=5, scoring='accuracy')

print(f"Sans PCA (30 features) : {scores_sans.mean():.2%} (+/- {scores_sans.std():.2%})")
print(f"Avec PCA (10 comp.)    : {scores_avec.mean():.2%} (+/- {scores_avec.std():.2%})")
```

```
Sans PCA (30 features) : 97.72% (+/- 0.99%)
Avec PCA (10 comp.)    : 97.72% (+/- 1.30%)
```

Même performance avec **3× moins de features** : la PCA a supprimé la redondance (rayon/périmètre/aire corrélés) sans perdre de pouvoir prédictif, tout en rendant le modèle plus léger et plus rapide.

> 💡 **Conseil** : "La PCA n'améliore pas *toujours* le score. Son bénéfice principal est souvent la **vitesse** et la **robustesse** (moins de surapprentissage), surtout quand on a beaucoup de features corrélées ou peu d'échantillons."

### 7.4 Optimiser le nombre de composantes par recherche

Le nombre de composantes est un hyperparamètre : on peut le régler par `GridSearchCV`.

```python
from sklearn.model_selection import GridSearchCV

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA()),
    ('clf', LogisticRegression(max_iter=1000)),
])

param_grid = {'pca__n_components': [2, 5, 10, 15, 20]}

grid = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy')
grid.fit(X_train, y_train)

print(f"Meilleur nb de composantes : {grid.best_params_['pca__n_components']}")
print(f"Meilleure accuracy (CV)    : {grid.best_score_:.2%}")
print(f"Accuracy sur le test       : {grid.score(X_test, y_test):.2%}")
```

```
Meilleur nb de composantes : 15
Meilleure accuracy (CV)    : 97.58%
Accuracy sur le test       : 97.37%
```

---

## 8. 🚧 Pièges, limites et quand l'utiliser

### 8.1 Les pièges classiques

| Piège | Conséquence | Solution |
|-------|-------------|----------|
| Oublier de **standardiser** | PC1 ne reflète que la feature aux plus grands chiffres | Toujours `StandardScaler` avant PCA |
| Faire `fit` sur **tout** le dataset | Data leakage, score trompeusement optimiste | Mettre la PCA dans un `Pipeline`, `fit` sur le train seul |
| Réduire **trop** agressivement | Perte d'information, chute de performance | Vérifier la variance cumulée (viser 90–99 %) |
| Interpréter les composantes comme des features "réelles" | PC1 n'a pas d'unité métier | Ce sont des combinaisons, pas des variables physiques |
| Appliquer PCA sur des **catégories** encodées brutalement | Résultats absurdes | PCA suppose des données **numériques continues** |

### 8.2 Ce que PCA ne fait PAS

- PCA **ne connaît pas** votre `y` : c'est une méthode **non supervisée**. Elle maximise la variance, pas la séparation des classes. Une direction très variable n'est pas forcément celle qui distingue vos classes (pour ça, regardez la **LDA**, supervisée).
- PCA suppose des relations **linéaires**. Si la structure de vos données est très courbe/entortillée, une PCA linéaire la manquera (voir **Kernel PCA**, t-SNE, UMAP).
- PCA **détruit l'interprétabilité** : après projection, "PC1 = 0,58×pétale + 0,52×sépale − ..." n'a pas de sens métier direct.

> ⚠️ **Attention** : "PCA maximise la **variance**, pas la **séparabilité des classes**. Il arrive qu'une composante à faible variance soit pourtant celle qui sépare le mieux vos classes — et PCA la jetterait ! Ne l'utilisez jamais aveuglément sur un problème supervisé sans vérifier."

### 8.3 Quand utiliser la PCA (et quand s'abstenir)

**Utilisez la PCA quand :**
- vous avez **beaucoup de features corrélées** (redondance à éliminer) ;
- vous voulez **visualiser** un nuage de haute dimension en 2D/3D ;
- vous voulez **accélérer** un modèle ou **réduire le bruit** avant l'entraînement ;
- vos features sont **numériques et continues**.

**Évitez (ou méfiez-vous) quand :**
- vous avez **peu de features** déjà pertinentes (rien à gagner) ;
- l'**interprétabilité** de chaque feature est essentielle (santé, finance réglementée) ;
- vos features sont majoritairement **catégorielles** ;
- vous soupçonnez des relations **fortement non linéaires** (préférez t-SNE / UMAP / Kernel PCA).

| Méthode | Type | Usage privilégié |
|---------|------|------------------|
| **PCA** | Linéaire, non supervisée | Réduction générale, prétraitement, viz rapide |
| **LDA** | Linéaire, **supervisée** | Maximiser la séparation entre classes |
| **t-SNE** | Non linéaire, viz | Visualiser des clusters (2D/3D), non pour prétraiter |
| **UMAP** | Non linéaire, viz | Comme t-SNE, plus rapide, préserve mieux le global |
| **Kernel PCA** | Non linéaire | PCA sur données courbes (noyau RBF, etc.) |

---

## 9. 🏋️ Exercices pratiques

### Exercice 1 : Variance expliquée sur les chiffres manuscrits

```python
from sklearn.datasets import load_digits
# digits : 1797 images 8x8 = 64 features (pixels), 10 classes (chiffres 0-9)

# TODO : Charger le dataset et standardiser
# TODO : Appliquer une PCA complète, tracer la variance expliquée cumulée
# TODO : Combien de composantes pour atteindre 90 % de variance ?
#        (indice : normalement ~21 au lieu de 64)
```

### Exercice 2 : Visualiser les chiffres en 2D

```python
# TODO : Réduire digits à 2 composantes avec PCA
# TODO : Faire un scatter 2D coloré par chiffre (0 à 9)
# TODO : Quels chiffres se chevauchent le plus ? (indice : 3, 5, 8...)
# TODO : Recommencer en 3D — la séparation est-elle meilleure ?
```

### Exercice 3 : PCA en prétraitement, gain de vitesse

```python
import time
from sklearn.svm import SVC
# TODO : Sur digits, mesurer le temps d'entraînement d'un SVC SANS PCA
# TODO : Puis AVEC une PCA(n_components=0.90) en amont
# TODO : Comparer temps ET accuracy — que gagne-t-on / perd-on ?
```

### Exercice 4 : Le piège de la standardisation

```python
from sklearn.datasets import load_wine
# TODO : Appliquer PCA(n_components=2) SANS standardiser au préalable
# TODO : Appliquer PCA(n_components=2) AVEC StandardScaler
# TODO : Comparer les deux nuages 2D — pourquoi sont-ils si différents ?
#        (indice : regardez l'échelle de 'proline' vs les autres features)
```

### Exercice 5 : Choisir n_components par GridSearch

```python
# TODO : Sur breast_cancer, construire un Pipeline scaler → PCA → RandomForest
# TODO : Chercher le meilleur n_components parmi [2, 5, 10, 15, 20, 25]
# TODO : Comparer au même modèle sans PCA
# TODO : La PCA aide-t-elle un modèle non linéaire comme la Random Forest ?
```

---

## 🎯 Points clés à retenir

1. La **malédiction de la dimension** : en haute dimension, l'espace est vide et toutes les distances se ressemblent — les modèles basés sur la distance s'effondrent.
2. La **variance portée par un axe** = l'information : une direction très étalée est informative, une direction "plate" ne l'est pas.
3. Les **composantes principales** sont de nouveaux axes, combinaisons des features d'origine, **orthogonaux** et **classés** par variance décroissante.
4. La **variance expliquée cumulée** permet de choisir le nombre de composantes (viser 90–99 %).
5. **Standardiser AVANT** la PCA est quasi obligatoire : sinon PC1 ne reflète que l'échelle des features.
6. `PCA(n_components=2 ou 3)` permet de **visualiser** un nuage de haute dimension.
7. `PCA(n_components=0.95)` laisse scikit-learn **garder juste assez** de composantes pour 95 % de variance.
8. En **prétraitement**, PCA se met dans un `Pipeline` (`fit` sur le train seul) pour éviter le **data leakage**.
9. PCA **accélère** et **régularise** souvent le modèle, sans forcément améliorer le score brut.
10. PCA est **linéaire et non supervisée** : elle ignore `y`. Pour la séparation de classes, pensez **LDA** ; pour du non linéaire, **t-SNE / UMAP / Kernel PCA**.

---

## ✅ Checklist de validation

- [ ] Je sais expliquer la malédiction de la dimension avec un exemple concret
- [ ] Je comprends que "variance le long d'un axe" = "information portée par cet axe"
- [ ] Je sais ce qu'est une composante principale et pourquoi elles sont orthogonales et classées
- [ ] Je sais lire `explained_variance_ratio_` et calculer la variance cumulée
- [ ] Je sais choisir le nombre de composantes avec un scree plot ou `n_components=0.95`
- [ ] Je sais pourquoi il faut standardiser avant une PCA
- [ ] Je sais projeter des données en 2D/3D avec PCA pour les visualiser
- [ ] Je sais intégrer une PCA dans un `Pipeline` sans provoquer de data leakage
- [ ] Je connais les limites de la PCA (linéaire, non supervisée, peu interprétable)
- [ ] Je sais quand préférer LDA, t-SNE ou UMAP à la PCA

---

## 📚 Ressources

- Documentation scikit-learn — [`sklearn.decomposition.PCA`](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)
- Guide scikit-learn — [Decomposing signals in components](https://scikit-learn.org/stable/modules/decomposition.html)
- Comparaison des méthodes de réduction — [Manifold learning (t-SNE, UMAP...)](https://scikit-learn.org/stable/modules/manifold.html)
- Datasets utilisés : `load_iris`, `load_wine`, `load_breast_cancer`, `load_digits` (tous intégrés à scikit-learn)
- Article de référence — Jolliffe & Cadima (2016), *Principal component analysis: a review and recent developments*

---

*Ce cours fait partie de la formation Data Engineer — Module 08 Machine Learning.*
