# Régression linéaire simple — de la corrélation à la prédiction

> 🎯 **Ça te servira pour…** prédire une valeur (le CA du mois prochain, le prix d'un logement),
> quantifier une relation (« +1 °C = combien de glaces vendues en plus ? »), et poser le premier pied
> dans le Machine Learning.

Au chapitre précédent, tu as appris à **mesurer** une relation entre deux variables (la corrélation).
Mais la corrélation dit seulement *« ça bouge ensemble »*. La **régression linéaire** va plus loin :
elle trace **la meilleure droite** dans le nuage de points pour pouvoir **prédire**.

> **Analogie** — La corrélation te dit que deux danseurs bougent en rythme. La régression écrit la
> **partition** : « quand l'un avance d'un pas, l'autre avance de 0,8 pas ». Avec la partition, tu peux
> **anticiper** le prochain mouvement.

---

## 1. L'idée : la meilleure droite dans le nuage

Reprenons NordRetail. On soupçonne que les **grands magasins** (surface au sol) font **plus de CA**.
On place chaque magasin sur un graphique : surface en `x`, CA en `y`. Ça forme un nuage de points
vaguement croissant. La régression cherche **la droite qui passe au plus près de tous les points** :

```text
CA
 │            •
 │        • •      ___/  ← la droite de régression
 │     •    __/•
 │   •  __/  •
 │ __/  •
 └─────────────────── surface (m²)
```

Cette droite a l'équation d'une fonction affine (vue au chapitre Algèbre) :

$$ \hat{y} = a \cdot x + b $$

- **`a`** = la **pente** : de combien `y` augmente quand `x` augmente de 1.
- **`b`** = l'**ordonnée à l'origine** : la valeur de `y` quand `x = 0`.
- **`ŷ`** (« y chapeau ») = la valeur **prédite** (à distinguer du `y` réellement observé).

> **Analogie** — `a`, c'est la **pente de la rampe de skate** : plus elle est raide, plus 1 m² de
> surface en plus rapporte de CA. `b`, c'est le point de départ de la rampe.

---

## 2. Comment trace-t-on « la meilleure » droite ? (moindres carrés)

Pour chaque point, l'écart entre le vrai `y` et la droite `ŷ` s'appelle le **résidu**. La droite des
**moindres carrés** est celle qui **minimise la somme des résidus au carré** (on met au carré pour que
les écarts négatifs et positifs ne s'annulent pas, et pour pénaliser les gros écarts).

> **Analogie** — Imagine un élastique tendu entre la droite et chaque point. La « bonne » droite est
> celle qui **fatigue le moins les élastiques** au total.

> 🎲 **Devine avant de calculer** — Si un magasin de 2 000 m² fait 500 k€ et un de 4 000 m² fait
> 900 k€, la pente est-elle plutôt proche de **0,2 €/m²** ou de **200 €/m²** ? *(Indice : (900−500) k€ ÷
> (4000−2000) m² = 400 000 € ÷ 2 000 m² = 200 €/m².)*

---

## 3. Interpréter : le R² (« quelle part le modèle explique »)

Une droite, c'est bien. Savoir si elle est **fiable**, c'est mieux. Le **coefficient de
détermination R²** (entre 0 et 1) répond à : *« quelle part de la variation de `y` mon modèle
explique-t-il ? »*

- **R² = 0,85** → 85 % de la variation du CA s'explique par la surface. Très bon.
- **R² = 0,10** → la surface n'explique presque rien ; d'autres facteurs dominent (emplacement,
  concurrence…). La droite existe mais ne sert à rien pour prédire.

> 🛑 **Erreur courante** — croire qu'un R² élevé prouve une **cause**. Le nombre de coups de soleil et
> les ventes de glaces ont un R² énorme… parce que les deux dépendent du soleil. **Corrélation ≠
> causalité**, même avec un beau R². (Revois le chapitre précédent.)

> 🛑 **Erreur courante n°2** — **extrapoler** hors de la plage observée. Ta droite calibrée sur des
> magasins de 500 à 4 000 m² ne dit **rien** de fiable sur un hypermarché de 20 000 m².

---

## 4. En Python

Trois façons, de la plus simple à la plus complète.

### numpy — juste la droite

```python
import numpy as np

surface = np.array([1200, 2400, 1800, 3200, 900, 2600])   # m²
ca      = np.array([320, 610, 480, 820, 240, 700])         # k€

a, b = np.polyfit(surface, ca, 1)   # degré 1 = droite
print(f"CA ≈ {a:.3f} × surface + {b:.1f}")

# Prédire le CA d'un futur magasin de 2 000 m²
print("Prédiction 2000 m² :", a * 2000 + b, "k€")
```

### statsmodels — la droite + le diagnostic complet

```python
import statsmodels.api as sm

X = sm.add_constant(surface)          # ajoute l'ordonnée à l'origine b
modele = sm.OLS(ca, X).fit()          # OLS = Ordinary Least Squares (moindres carrés)
print(modele.summary())               # coefficients, R², p-values…
print("R² =", round(modele.rsquared, 3))
```

Dans le `summary()`, lis en priorité : le **coef** de `x1` (la pente `a`), le **R-squared**, et la
**p-value** `P>|t|` de la pente (si elle est < 0,05, la pente est statistiquement différente de 0 —
voir le chapitre inférentiel).

### scikit-learn — la porte d'entrée du ML

```python
from sklearn.linear_model import LinearRegression

X = surface.reshape(-1, 1)            # sklearn attend une matrice (n lignes, 1 colonne)
modele = LinearRegression().fit(X, ca)
print("pente :", modele.coef_[0], "| origine :", modele.intercept_)
print("R² :", modele.score(X, ca))
print("Prédiction 2000 m² :", modele.predict([[2000]]))
```

> 🔗 **Pont vers le Machine Learning** — `LinearRegression`, `.fit()`, `.predict()` : c'est
> **exactement** l'interface de tous les modèles de ML. Tu viens d'entraîner ton premier modèle
> supervisé. La suite (plusieurs variables, autres algorithmes) est dans
> [08-Machine-Learning — modèles linéaires](../../../08-Machine-Learning/cours/09-modeles-lineaires.md).

---

## 🧪 Exercice

Un caviste pense que le **budget pub mensuel** explique son **chiffre d'affaires**. Il te donne :

| Pub (k€) | 2 | 3 | 5 | 8 | 10 |
|---|---|---|---|---|---|
| CA (k€) | 22 | 28 | 41 | 60 | 71 |

1. Estime la pente à la main entre le 1ᵉʳ et le dernier point.
2. Que prédit-on pour un budget de 6 k€ ?
3. Le R² sera-t-il plutôt proche de 0,3 ou de 0,95 ? Pourquoi ?

<details>
<summary>💡 Corrigé</summary>

1. Pente ≈ (71 − 22) ÷ (10 − 2) = 49 ÷ 8 ≈ **6,1 k€ de CA par k€ de pub**.
2. Avec `b` ≈ 22 − 6,1×2 ≈ 9,8 : `ŷ(6)` ≈ 6,1×6 + 9,8 ≈ **46 k€**.
3. Les points sont **quasi alignés** → R² proche de **0,95**. La pub explique presque toute la
   variation du CA *dans cet échantillon* (attention : corrélation ≠ causalité, et l'échantillon est
   minuscule).

Vérifie avec `np.polyfit([2,3,5,8,10],[22,28,41,60,71],1)`.
</details>

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Régression linéaire, l'intuition](https://www.youtube.com/results?search_query=r%C3%A9gression+lin%C3%A9aire+expliqu%C3%A9e+machine+learnia) | Machine Learnia | FR | Le principe des moindres carrés |
| [Linear Regression, clearly explained](https://www.youtube.com/results?search_query=statquest+linear+regression) | StatQuest | EN | R², résidus, ce que ça signifie |
| [R² expliqué simplement](https://www.youtube.com/results?search_query=statquest+r+squared) | StatQuest | EN | Bien lire le R² |

---

## À retenir

- La régression linéaire trace **la droite `ŷ = a·x + b`** qui minimise la somme des **résidus au
  carré** (moindres carrés).
- **`a`** = combien `y` gagne par unité de `x` ; **`b`** = valeur de `y` en `x = 0`.
- Le **R²** dit **quelle part de la variation** le modèle explique (0 = rien, 1 = tout).
- Un beau R² **ne prouve pas une cause**, et on **n'extrapole pas** hors de la plage observée.
- En Python : `np.polyfit` (rapide), `statsmodels.OLS` (diagnostic), `sklearn.LinearRegression`
  (porte d'entrée du ML).
