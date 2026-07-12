# 01 — Arithmétique & pré-requis

> **Durée estimée** : 4 h (3 h en présentiel + 1 h d'auto-formation)
> **Compétence visée** : socle pour **C5** (analyser des données, produire des indicateurs) et **C6** (restituer des résultats chiffrés fiables). RNCP-38616 — option Data Analyse.
> **Pré-requis** : savoir poser une addition, une multiplication, une division. Aucune connaissance avancée n'est attendue.

---

## 🎬 Bienvenue à la Ch'ti Boutique

> Imagine. On est lundi matin à Lille. Tu viens d'être embauché·e comme Data Analyst à **la Ch'ti Boutique**, un commerce du Nord qui vend de tout : vélos, textile, café, jeux de société.
>
> La patronne, Mme Vandenberghe, débarque avec son café : *« Dis donc, ch'ti, le mois dernier on a fait 12 % de plus, ou 12 points de plus ? Et si je baisse mes prix de 20 % puis que je les remonte de 20 %, je reviens au même prix, hein ? Et là, sur 12 jours j'ai fait 84 000 € — ça fait combien sur le mois, à ton avis ? »*
>
> Tu transpires. Toutes ses questions tiennent dans **un seul chapitre** : l'arithmétique. Pourcentages, variations, proportions, ratios, arrondis. C'est exactement ce que tu vas dérouler ici. À la fin, tu répondras à Mme Vandenberghe **sans hésiter** — et tu sauras le refaire en Python.
>
> 💡 **À toi de jouer** : si la Ch'ti Boutique ne te parle pas, remplace-la mentalement par **un commerce que tu connais** (la boulangerie du coin, ton ancien job, une boutique en ligne). Les chiffres seront plus vivants.

---

## Objectifs pédagogiques

À la fin de ce chapitre, tu sauras :

- Calculer un **pourcentage**, une **variation en %** et faire la différence entre un **point de pourcentage** et un **pourcentage**.
- Utiliser une **proportion** et la **règle de trois** pour extrapoler une valeur.
- Manipuler **fractions** et **décimaux** sans te tromper de virgule.
- Comprendre et calculer un **ratio**.
- Utiliser les **puissances** et les **racines carrées**.
- Lire et écrire un nombre en **notation scientifique**.
- Estimer un **ordre de grandeur** pour détecter une erreur de calcul.
- Gérer les **arrondis** et reconnaître les **erreurs d'arrondi** dans un tableau de chiffres.
- Refaire chacun de ces calculs **à la main** ET **en Python (pandas / numpy)**.

---

## Pourquoi c'est utile au Data Analyst

Le métier de Data Analyst, c'est **transformer des données en chiffres compréhensibles** pour des décideurs. Or 90 % de ce que tu vas produire repose sur de l'arithmétique de base : « le chiffre d'affaires a progressé de **+12 %** », « le taux de conversion est passé de 2 % à 3 % (soit **+1 point**, ou **+50 %** en relatif !) », « on estime 320 000 visiteurs sur l'année par règle de trois ». Si tu te trompes d'une virgule, d'un point de % ou d'un arrondi, **tout ton tableau de bord devient faux** et la décision business derrière aussi. Ce chapitre, c'est ton assurance qualité : maîtriser ces fondamentaux te permet de produire des indicateurs **justes**, **vérifiables** et **expliqués**.

---

## Les pourcentages

### Calculer un pourcentage

**Définition simple.** Un pourcentage, c'est une part sur **100**. « 20 % » signifie « 20 sur 100 », soit la fraction 20/100 = 0,20.

> 🎯 **Ça te servira pour…** répondre à « quelle part du CA vient des vélos ? », « quel % de clients reviennent ? ». Le pourcentage rend deux chiffres **comparables** même si les totaux diffèrent. C'est la brique de base de tous tes tableaux de bord.

**Exemple métier.** Un magasin Decathlon de Villeneuve-d'Ascq a vendu **840 vélos** sur un total de **3 500 articles de sport** ce mois-ci. Quelle part représentent les vélos ?

**Formule.**

```
pourcentage = (partie / total) × 100
```

**Calcul à la main.**

```
840 / 3500 = 0,24
0,24 × 100 = 24 %
```

Les vélos représentent **24 %** des articles vendus.

> Pour appliquer un pourcentage à une valeur : `valeur × (pourcentage / 100)`. Exemple : 15 % de 3 500 = 3 500 × 0,15 = 525.

**Calcul en Python.**

```python
import pandas as pd

ventes = pd.DataFrame({
    "categorie": ["Vélos", "Textile", "Chaussures", "Camping"],
    "quantite": [840, 1260, 980, 420],
})

total = ventes["quantite"].sum()          # 3500
ventes["part_pct"] = ventes["quantite"] / total * 100

print(ventes)
#     categorie  quantite  part_pct
# 0       Vélos       840      24.0
# 1     Textile      1260      36.0
# 2  Chaussures       980      28.0
# 3     Camping       420      12.0
```

> 🛑 **Erreurs courantes**
> - Oublier de multiplier par 100 (tu obtiens 0,24 au lieu de 24 %).
> - Diviser la partie par la **mauvaise** base (ex : diviser par les vélos au lieu du total).
> - En Python, faire `quantite / total` sans `* 100` puis afficher « 0,24 % » : c'est 24 %, pas 0,24 %.

### La variation en % (évolution)

**Définition simple.** La variation en % mesure **de combien une valeur a augmenté ou diminué** par rapport à une valeur de départ. C'est LE calcul roi du Data Analyst (évolution du CA, du trafic, des ventes…).

> 🎲 **Devine avant de calculer !**
> Mme Vandenberghe affiche un article à **100 €**. Pour les soldes, elle fait **−20 %**. Puis, soldes finies, elle remonte de **+20 %**.
> **Parie maintenant** (avant de lire la suite) : le prix est-il revenu à 100 € ? Plus haut ? Plus bas ?
>
> <details><summary>👀 Révélation</summary>
>
> ```
> 100 € − 20 %  = 100 × 0,80 = 80 €
> 80 €  + 20 %  =  80 × 1,20 = 96 €   ← et non 100 € !
> ```
> **Surprise : 96 €, on a perdu 4 €.** Pourquoi ? Le +20 % se calcule sur 80 €, pas sur 100 €. Une hausse et une baisse du même % **ne s'annulent jamais**. Retiens ce piège : il revient sans arrêt dans les rapports business.
> </details>

> 🎯 **Ça te servira pour…** mesurer l'évolution du CA, du trafic, du nombre de commandes d'un mois sur l'autre. La phrase « le CA a fait **+12 %** » dans un dashboard, c'est exactement ce calcul. C'est l'indicateur que ton manager regardera en premier.

**Exemple métier.** Le CA d'un hypermarché Auchan était de **1 250 000 €** en 2024 et de **1 400 000 €** en 2025. Quelle est l'évolution ?

**Formule.**

```
variation (%) = (valeur_finale − valeur_initiale) / valeur_initiale × 100
```

**Calcul à la main.**

```
1 400 000 − 1 250 000 = 150 000
150 000 / 1 250 000 = 0,12
0,12 × 100 = +12 %
```

Le CA a augmenté de **+12 %**.

> **Astuce du coefficient multiplicateur.** Augmenter de 12 % = multiplier par **1,12**. Diminuer de 12 % = multiplier par **0,88** (1 − 0,12). Très utile pour les évolutions successives : +10 % puis −10 % donne 1,10 × 0,90 = **0,99**, soit −1 % au total (et non 0 % !).

**Calcul en Python.**

```python
import pandas as pd

ca = pd.DataFrame({
    "annee": [2023, 2024, 2025],
    "ca": [1_180_000, 1_250_000, 1_400_000],
})

# variation d'une année sur l'autre
ca["variation_pct"] = ca["ca"].pct_change() * 100

print(ca)
#    annee        ca  variation_pct
# 0   2023   1180000            NaN
# 1   2024   1250000       5.932203
# 2   2025   1400000      12.000000
```

`pct_change()` calcule automatiquement `(valeur − valeur_précédente) / valeur_précédente`.

> 🛑 **Erreurs courantes**
> - Diviser par la valeur **finale** au lieu de l'initiale.
> - Confondre « le CA a augmenté de 12 % » et « le CA est à 12 % ».
> - Croire que +10 % puis −10 % = retour au point de départ. **FAUX** : on perd 1 %.

### Point de pourcentage vs pourcentage

**Définition simple.** C'est le piège le plus fréquent. Quand on compare deux pourcentages, la différence brute s'exprime en **points de pourcentage (pts)**, pas en %. La variation **relative**, elle, s'exprime en %.

> 🧠 **Analogie pour ne plus jamais confondre.** Imagine un thermomètre gradué de 0 à 100. Passer de **2** à **3** sur le thermomètre, c'est avancer d'**1 cran** = **1 point**. Mais en partant de 2, ce petit cran représente **la moitié de la distance déjà parcourue** = **+50 %**. Le « point » mesure le **déplacement** ; le « % » mesure **par rapport à d'où tu pars**.
>
> 🪄 **Moyen mnémotechnique** : *« on **soustrait** → on dit **points** ; on **divise** → on dit **pourcent** ».* Dès que tu fais une soustraction de deux taux, le résultat est en **points**.

> 🎯 **Ça te servira pour…** commenter un taux de conversion, un taux de churn, un taux de retour. Dire « le taux est passé de 2 % à 3 %, soit **+1 point (+50 %)** » au lieu de « +1 % » = la différence entre un Data Analyst crédible et un rapport qu'on rejette.

**Exemple métier.** Le **taux de conversion** d'un site e-commerce (part des visiteurs qui achètent) passe de **2 %** à **3 %**.

**Calcul à la main.**

```
Différence absolue : 3 % − 2 % = 1 point de pourcentage (+1 pt)
Variation relative : (3 − 2) / 2 × 100 = +50 %
```

Donc on peut dire **« +1 point »** OU **« +50 % »** — les deux sont vrais mais ne disent pas la même chose ! Dire « le taux a augmenté de 1 % » serait **faux**.

**Calcul en Python.**

```python
taux_avant = 2.0   # en %
taux_apres = 3.0   # en %

points = taux_apres - taux_avant                       # 1.0 point de %
variation_relative = (taux_apres - taux_avant) / taux_avant * 100  # 50.0 %

print(f"+{points} point(s) de pourcentage")   # +1.0 point(s) de pourcentage
print(f"+{variation_relative} % en relatif")  # +50.0 % en relatif
```

> 🛑 **Erreurs courantes**
> - Dire « le taux de conversion a gagné 1 % » alors qu'il a gagné **1 point** (et +50 % en relatif).
> - C'est l'erreur la plus courante dans les rapports business. Toujours préciser **« points »** quand tu soustrais deux pourcentages.

---

## Proportions et règle de trois

**Définition simple.** Une proportion, c'est une égalité entre deux rapports. La **règle de trois** (ou « produit en croix ») permet de trouver une quatrième valeur quand on en connaît trois. C'est l'outil d'**extrapolation** par excellence.

> 🎲 **Devine avant de calculer !** La Ch'ti Boutique a fait **84 000 €** en **12 jours**. Sur **30 jours**, tu paries combien à vue de nez ? Note ton chiffre, puis vérifie plus bas. (Indice : 30 jours, c'est plus du double de 12…)

> 🎯 **Ça te servira pour…** extrapoler une tendance (« à ce rythme, on finira l'année à X »), redresser un échantillon, convertir des unités. C'est ton outil d'**estimation rapide** — mais souviens-toi : une extrapolation reste une estimation, jamais une certitude.

**Exemple métier.** Un magasin a réalisé **84 000 €** de ventes en **12 jours** d'ouverture. Si le rythme reste constant, combien fera-t-il sur un mois complet de **30 jours** ?

**Formule (produit en croix).**

```
84 000 € → 12 jours
   x €   → 30 jours

x = (84 000 × 30) / 12
```

**Calcul à la main.**

```
84 000 × 30 = 2 520 000
2 520 000 / 12 = 210 000
```

Estimation : **210 000 €** sur 30 jours.

**Calcul en Python.**

```python
ventes_12j = 84_000
jours_observes = 12
jours_cibles = 30

estimation = ventes_12j / jours_observes * jours_cibles
print(estimation)   # 210000.0
```

> 🛑 **Erreurs courantes**
> - Croiser les valeurs au mauvais endroit (mélanger € et jours).
> - **Extrapoler aveuglément** : la règle de trois suppose une proportionnalité parfaite. En vrai, un mois contient des week-ends, des soldes, des jours fériés → une extrapolation est une **estimation**, pas une vérité. Toujours le préciser.

---

## Fractions et décimaux

**Définition simple.** Une fraction (`3/4`) et un décimal (`0,75`) sont deux écritures du même nombre. Passer de l'un à l'autre : on **divise** le numérateur par le dénominateur.

**Exemple métier.** Sur les retours produits d'un drive Auchan, **3 commandes sur 4** contiennent au moins un article manquant. Exprime ce taux en décimal et en %.

**Calcul à la main.**

```
3 / 4 = 0,75   (décimal)
0,75 × 100 = 75 %
```

Conversion inverse (d'un % vers une fraction) : 75 % = 75/100 = 3/4 (en simplifiant par 25).

**Calcul en Python.**

```python
from fractions import Fraction

f = Fraction(3, 4)
print(float(f))        # 0.75
print(float(f) * 100)  # 75.0

# attention au piège des flottants :
print(0.1 + 0.2)       # 0.30000000000000004  (et non 0.3 !)
print(round(0.1 + 0.2, 2))  # 0.3
```

> 🛑 **Erreurs courantes**
> - Confondre virgule (notation française `0,75`) et point (notation informatique `0.75`). **En Python et dans les CSV, c'est TOUJOURS le point.**
> - Le piège des nombres flottants : `0.1 + 0.2` ne donne pas exactement `0.3` en machine. Pour de l'argent, arrondis ou utilise des entiers en centimes.

---

## Ratios

**Définition simple.** Un ratio compare deux grandeurs entre elles, souvent sous la forme `a:b` ou `a/b`. Contrairement au pourcentage (part d'un tout), le ratio met en regard **deux quantités distinctes**.

> 🎯 **Ça te servira pour…** calculer le **panier moyen** (CA / nb tickets), le **coût par acquisition**, le **chiffre par employé**. Le ratio met deux mondes différents en regard et révèle l'efficacité. C'est un KPI star des restitutions Data.

**Exemple métier.** Dans un magasin, il y a **1 200 clients** pour **8 caissiers** ouverts en heure de pointe. Quel est le ratio clients/caissier ?

**Calcul à la main.**

```
1 200 / 8 = 150
```

Ratio = **150 clients par caissier**. (On écrit aussi 1200:8, simplifié en 150:1.)

Autre ratio utile : le **panier moyen** = CA / nombre de tickets. Si CA = 18 000 € pour 600 tickets → 18 000 / 600 = **30 € par ticket**.

**Calcul en Python.**

```python
import pandas as pd

df = pd.DataFrame({
    "magasin": ["Lille", "Roubaix", "Tourcoing"],
    "ca": [18_000, 22_500, 15_000],
    "nb_tickets": [600, 750, 480],
})

df["panier_moyen"] = df["ca"] / df["nb_tickets"]
print(df)
#      magasin     ca  nb_tickets  panier_moyen
# 0      Lille  18000         600          30.0
# 1    Roubaix  22500         750          30.0
# 2  Tourcoing  15000         480          31.25
```

> 🛑 **Erreurs courantes**
> - Confondre ratio et pourcentage : un ratio peut dépasser 100 % (150:1 n'a pas de sens en %).
> - Inverser numérateur et dénominateur (clients/caissiers ≠ caissiers/clients).

---

## Puissances et racines

**Définition simple.** Une puissance, c'est une multiplication répétée : `10³ = 10 × 10 × 10 = 1000`. La **racine carrée** fait l'inverse du carré : `√144 = 12` car `12² = 144`.

**Exemple métier.** Tu calcules un **écart-type** (chapitre statistiques) : il faut élever des écarts au carré, puis prendre une racine. Autre cas : une croissance qui **double tous les ans** pendant 4 ans → multipliée par `2⁴ = 16`.

**Calcul à la main.**

```
2⁴ = 2 × 2 × 2 × 2 = 16
√144 = 12   (car 12 × 12 = 144)
10⁻² = 1 / 10² = 1 / 100 = 0,01
```

**Calcul en Python.**

```python
import numpy as np

print(2 ** 4)          # 16     (opérateur ** = puissance)
print(np.sqrt(144))    # 12.0   (racine carrée)
print(144 ** 0.5)      # 12.0   (racine = puissance 0,5)
print(10 ** -2)        # 0.01   (puissance négative)

# sur une colonne pandas
import pandas as pd
s = pd.Series([4, 9, 16, 25])
print(np.sqrt(s).tolist())   # [2.0, 3.0, 4.0, 5.0]
```

> 🛑 **Erreurs courantes**
> - Confondre `2 ** 4` (puissance = 16) et `2 * 4` (multiplication = 8).
> - Croire que la racine carrée d'un nombre négatif existe dans les réels (elle n'existe pas).
> - `10 ** -2` est bien `0.01`, pas `-100`.

### La notation somme Σ (sigma)

**Définition simple.** Le symbole **Σ** (sigma majuscule, la lettre grecque « S » comme « Somme ») est un raccourci pour écrire « additionne tous ces termes ». Au lieu d'écrire `12 + 15 + 9 + 20`, on écrit `Σ` avec un compteur qui parcourt les valeurs.

**Comment le lire.**

$$\sum_{i=1}^{n} x_i \;=\; x_1 + x_2 + \dots + x_n$$

- en dessous du Σ : `i = 1` → le compteur `i` **démarre à 1** ;
- au-dessus du Σ : `n` → il **s'arrête à n** (le dernier indice) ;
- à droite : `x_i` → le terme à additionner, où `i` prend successivement chaque valeur.

**Exemple chiffré simple.** Soit la série de ventes `x = [12, 15, 9, 20]` (donc `n = 4`, `x_1 = 12`, `x_2 = 15`, …) :

```
Σ x_i (de i=1 à 4) = x_1 + x_2 + x_3 + x_4
                   = 12 + 15 + 9 + 20
                   = 56
```

La **moyenne** s'écrit alors très compactement `x̄ = (1/n) × Σ x_i = 56 / 4 = 14`.

**Calcul en Python.**

```python
x = [12, 15, 9, 20]
print(sum(x))          # 56   (Σ = la fonction sum())
print(sum(x) / len(x)) # 14.0 (la moyenne)
```

> 💡 Tu retrouveras Σ dans presque toutes les formules de statistiques (moyenne, variance, covariance…). Retiens juste : **Σ = « fais la somme de tout ça »**.

---

## Notation scientifique

**Définition simple.** La notation scientifique écrit un nombre sous la forme `a × 10ⁿ`, où `a` est compris entre 1 et 10. Elle sert à lire facilement des très grands ou très petits nombres.

**Exemple métier.** Un site de e-commerce génère **2 400 000 000** lignes de logs par an. En notation scientifique : `2,4 × 10⁹`. Inversement, une probabilité de fraude de `0,000037` s'écrit `3,7 × 10⁻⁵`.

**Calcul à la main.**

```
2 400 000 000 = 2,4 × 1 000 000 000 = 2,4 × 10⁹
(on déplace la virgule de 9 rangs vers la gauche)

0,000037 = 3,7 × 0,00001 = 3,7 × 10⁻⁵
(on déplace la virgule de 5 rangs vers la droite → exposant négatif)
```

**Calcul en Python.**

```python
n = 2_400_000_000
print(f"{n:.2e}")     # 2.40e+09   (notation scientifique, e = ×10^)

p = 0.000037
print(f"{p:.2e}")     # 3.70e-05

# l'inverse : écrire un nombre en notation scientifique littérale
x = 2.4e9
print(x)              # 2400000000.0
```

> 🛑 **Erreurs courantes**
> - Mettre un `a` qui n'est pas entre 1 et 10 (ex : `24 × 10⁸` n'est pas correct, c'est `2,4 × 10⁹`).
> - Se tromper de signe d'exposant (grand nombre → exposant **positif** ; petit nombre < 1 → exposant **négatif**).
> - En Python, `2.4e9` se lit « 2,4 fois 10 puissance 9 », le `e` n'est pas le nombre d'Euler.

---

## Ordre de grandeur

**Définition simple.** L'ordre de grandeur, c'est la puissance de 10 la plus proche d'un nombre. Il sert à **estimer rapidement** et surtout à **vérifier qu'un résultat est plausible** (détection d'erreur).

**Exemple métier.** On te dit que le CA mensuel d'un petit magasin est de **15 000 000 €**. Ordre de grandeur : 10⁷ (dizaines de millions). C'est **invraisemblable** pour un petit magasin → il y a probablement une erreur (15 000 € attendu, ordre de grandeur 10⁴).

**Calcul à la main.**

```
15 000 € ≈ 10⁴   (ordre des dizaines de milliers)
840 ≈ 10³        (ordre du millier)
0,024 ≈ 10⁻²     (ordre du centième)
```

**Calcul en Python.**

```python
import numpy as np

valeurs = [15_000, 840, 0.024, 2_400_000_000]
for v in valeurs:
    ordre = int(np.floor(np.log10(abs(v))))
    print(f"{v} → ordre de grandeur 10^{ordre}")
# 15000 → ordre de grandeur 10^4
# 840 → ordre de grandeur 10^2
# 0.024 → ordre de grandeur 10^-2
# 2400000000 → ordre de grandeur 10^9
```

> 🛑 **Erreurs courantes**
> - Ne JAMAIS vérifier l'ordre de grandeur d'un résultat. C'est ton premier réflexe anti-bug : un CA à 15 millions pour un magasin de quartier doit te faire tiquer immédiatement.

---

## Arrondis et erreurs d'arrondi

**Définition simple.** Arrondir, c'est remplacer un nombre par une valeur proche plus simple. Règle : si le chiffre suivant est ≥ 5, on arrondit au-dessus ; sinon en dessous. L'**erreur d'arrondi**, c'est l'écart introduit — et ces petits écarts peuvent **s'additionner** et fausser un total.

> 🧠 **Analogie.** Arrondir chaque ligne avant de faire le total, c'est comme rendre la monnaie en arrondissant à chaque achat : sur un caddie entier, tu finis avec quelques centimes en trop ou en moins. La règle d'or : **calcule juste jusqu'au bout, arrondis seulement à l'affichage.**

> 🎯 **Ça te servira pour…** présenter des camemberts qui font bien 100 %, afficher des montants en euros propres, éviter qu'un total ne « cloche » de 1 % dans un rapport. L'arrondi mal géré, c'est la fuite d'eau invisible de tes tableaux.

**Exemple métier.** Tu présentes des parts de marché : 33,333 % + 33,333 % + 33,333 % = 99,999 %, arrondies à **33 % + 33 % + 33 % = 99 %**… il manque 1 % ! C'est l'erreur d'arrondi classique des camemberts qui « ne font pas 100 % ».

**Calcul à la main.**

```
33,333 % arrondi à l'entier → 33 %
3 × 33 % = 99 %  (et non 100 %)

127,856 € arrondi au centime → 127,86 €  (car le 3ᵉ chiffre est 6 ≥ 5)
127,854 € arrondi au centime → 127,85 €  (car le 3ᵉ chiffre est 4 < 5)
```

**Calcul en Python.**

```python
print(round(127.856, 2))   # 127.86
print(round(127.854, 2))   # 127.85

# ⚠️ piège : Python utilise l'arrondi "au pair le plus proche" (banker's rounding)
print(round(2.5))          # 2  (et non 3 !)
print(round(0.5))          # 0
print(round(1.5))          # 2

# dans un DataFrame
import pandas as pd
s = pd.Series([33.333, 33.333, 33.333])
print(s.round(0).sum())    # 99.0  → l'arrondi fait perdre 1 point
print(s.sum().round(0))    # 100.0 → arrondir le total, pas les parts
```

> 🛑 **Erreurs courantes**
> - Arrondir **chaque ligne** puis sommer → le total ne tombe pas juste. Préfère sommer les valeurs exactes PUIS arrondir le résultat.
> - Oublier que `round()` en Python fait l'arrondi « au pair » (`round(2.5)` = 2). Pour de l'argent, c'est souvent invisible, mais sache-le.
> - Arrondir trop tôt dans une chaîne de calculs → les erreurs s'accumulent. Garde la précision jusqu'au dernier moment (l'**affichage**).

---

## Vidéos d'auto-formation

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|-------|--------|--------|-------|------|----------------------|
| LE COURS : Pourcentages (Seconde) | Yvan Monka (Maths et tiques) | 🇫🇷 FR | ~20 min | [Recherche YouTube](https://www.youtube.com/results?search_query=yvan+monka+le+cours+pourcentages+seconde) | Proportion, évolution, taux d'évolution, évolutions successives et réciproques |
| Calculer un taux de variation | Yvan Monka (Maths et tiques) | 🇫🇷 FR | ~8 min | [Recherche YouTube](https://www.youtube.com/results?search_query=yvan+monka+calculer+un+taux+de+variation) | La formule de la variation en % expliquée pas à pas |
| LE COURS : Les puissances + notation scientifique | Yvan Monka (Maths et tiques) | 🇫🇷 FR | ~17 min | [Recherche YouTube](https://www.youtube.com/results?search_query=yvan+monka+le+cours+les+puissances+notation+scientifique) | Puissances, puissances de 10, écriture scientifique |
| Prendre un pourcentage — exemple | Khan Academy (FR) | 🇫🇷 FR | ~5 min | [fr.khanacademy.org](https://fr.khanacademy.org/math/algebra-basics/basic-alg-foundations/alg-basics-decimals/v/taking-a-percentage-example) | Appliquer un pourcentage à une quantité, deux méthodes |
| Scientific notation examples | Khan Academy | 🇬🇧 EN | ~6 min | [khanacademy.org](https://www.khanacademy.org/math/cc-eighth-grade-math/cc-8th-numbers-operations/cc-8th-scientific-notation/v/scientific-notation) | Lire et écrire en notation scientifique (grands/petits nombres) |
| Significant figures | Khan Academy | 🇬🇧 EN | ~10 min | [youtube.com](https://www.youtube.com/watch?v=eCJ76hz7jPM) | Chiffres significatifs, arrondis et précision |

> Toutes les vidéos d'Yvan Monka sont aussi accessibles depuis sa chaîne : [youtube.com/@YMONKA/videos](https://www.youtube.com/@YMONKA/videos) et son site [maths-et-tiques.fr](https://www.maths-et-tiques.fr).

---

## Exercices

### Exercice 1 — Variation du CA
Un magasin Decathlon a réalisé **920 000 €** de CA en 2024 et **874 000 €** en 2025. Calcule la variation en %. S'agit-il d'une hausse ou d'une baisse ?

<details><summary>Corrigé</summary>

```
(874 000 − 920 000) / 920 000 × 100
= −46 000 / 920 000 × 100
= −0,05 × 100
= −5 %
```
**Baisse de 5 %** du chiffre d'affaires.
</details>

### Exercice 2 — Points de % vs %
Le taux de retour produit d'un drive est passé de **4 %** à **5 %** entre deux trimestres. Exprime cette évolution (a) en points de pourcentage et (b) en variation relative.

<details><summary>Corrigé</summary>

```
(a) Points : 5 % − 4 % = +1 point de pourcentage
(b) Relatif : (5 − 4) / 4 × 100 = +25 %
```
On dit donc **+1 point** (et **+25 %** en relatif). Dire « +1 % » serait une erreur classique.
</details>

### Exercice 3 — Règle de trois
Un rayon a vendu **156 articles en 4 heures** d'ouverture. À ce rythme, combien d'articles sur une journée de **10 heures** ? Pourquoi ce chiffre est-il une estimation ?

<details><summary>Corrigé</summary>

```
x = 156 × 10 / 4 = 1 560 / 4 = 390 articles
```
**Estimation : 390 articles.** C'est une extrapolation : elle suppose un rythme constant, ce qui est rarement vrai (heures creuses/pointe, pause déjeuner…).
</details>

### Exercice 4 — Panier moyen (ratio)
Trois magasins : Lille (CA 24 000 €, 800 tickets), Lens (CA 18 600 €, 620 tickets), Amiens (CA 31 000 €, 1 000 tickets). Calcule le panier moyen de chacun et dis lequel a le plus élevé.

<details><summary>Corrigé</summary>

```
Lille  : 24 000 / 800  = 30 €
Lens   : 18 600 / 620  = 30 €
Amiens : 31 000 / 1000 = 31 €
```
**Amiens** a le panier moyen le plus élevé (31 €).
</details>

### Exercice 5 — Notation scientifique & ordre de grandeur
Écris en notation scientifique : (a) 3 200 000 visiteurs, (b) 0,00045 (taux de clics). Donne l'ordre de grandeur de chacun.

<details><summary>Corrigé</summary>

```
(a) 3 200 000 = 3,2 × 10⁶   → ordre de grandeur 10⁶
(b) 0,00045   = 4,5 × 10⁻⁴  → ordre de grandeur 10⁻⁴
```
</details>

### Exercice 6 — Piège de l'arrondi
Trois catégories pèsent chacune 16,666 % des ventes (1/6), et trois autres 16,666 % aussi (total 6 × 16,666 %). Arrondies à l'entier, leur somme fait combien ? Que vaut-elle si tu arrondis le total ?

<details><summary>Corrigé</summary>

```
Valeur exacte : chaque part vaut 1/6, donc 6 × (1/6) = 100 % pile.
(Avec la valeur tronquée 16,666 %, on retombe sur 6 × 16,666 % = 99,996 %, soit ≈ 100 %.)
Mais 16,666 % arrondi à l'entier = 17 %
6 × 17 % = 102 %  → écart de +2 points dû à l'arrondi !
```
**Leçon** : n'arrondis pas chaque part séparément si tu veux que le total tombe à 100 %. Arrondis intelligemment (méthode du plus grand reste) ou affiche une décimale.
</details>

---

## Quiz d'auto-évaluation

1. Le CA passe de 200 000 € à 250 000 €. Quelle est la variation ?
   - a) +25 %   b) +50 %   c) +20 %   d) +50 000 %

2. Un taux de conversion passe de 2 % à 4 %. C'est :
   - a) +2 %   b) +2 points et +100 %   c) +100 points   d) +200 %

3. `2 ** 3` en Python vaut :
   - a) 6   b) 8   c) 5   d) 9

4. `0,000058` en notation scientifique s'écrit :
   - a) 5,8 × 10⁵   b) 58 × 10⁻⁶   c) 5,8 × 10⁻⁵   d) 0,58 × 10⁻⁴

5. Tu arrondis chaque part d'un camembert puis tu sommes, et tu obtiens 101 %. C'est :
   - a) un bug Python   b) une erreur d'arrondi normale   c) impossible   d) une faute de frappe

<details><summary>Réponses</summary>

1. **a)** (250 000 − 200 000) / 200 000 = +25 %
2. **b)** +2 points de pourcentage, soit +100 % en relatif
3. **b)** 8 (2×2×2)
4. **c)** 5,8 × 10⁻⁵
5. **b)** erreur d'arrondi normale (les arrondis ligne par ligne ne se somment pas exactement)
</details>

---

## 🏆 Défi du chapitre — « Sauve le rapport de Mme Vandenberghe »

> Vendredi 17 h. Mme Vandenberghe doit envoyer son bilan au comptable… et il est **bourré d'erreurs**. À toi de jouer au détective : trouve les **3 bourdes** et corrige-les. Chaque bonne réponse = 1 point. **3/3 = tu maîtrises le chapitre !**
>
> Voici son brouillon :
>
> 1. *« Notre taux de clients fidèles est passé de **8 %** à **10 %** : on a gagné **2 %** de fidélité ! »*
> 2. *« On a fait **84 000 €** en 12 jours, donc sur 30 jours on visera **210 000 €** garantis, c'est mathématique. »*
> 3. *« Nos 3 rayons pèsent chacun **33,3 %** des ventes. Arrondi : 33 % + 33 % + 33 % = **100 %**. Nickel. »*
>
> 🎯 Repère l'erreur dans chaque phrase, explique-la en une ligne, puis donne la version correcte.
>
> <details><summary>🏆 Solution (ne triche pas avant d'avoir parié !)</summary>
>
> **Phrase 1 — erreur : points vs %.** De 8 % à 10 %, c'est **+2 points de pourcentage**, pas +2 %. En relatif, c'est même **+25 %** ((10−8)/8 × 100). ✅ Version correcte : *« +2 points, soit +25 % de fidèles en plus. »*
>
> **Phrase 2 — erreur : extrapolation présentée comme une certitude.** Le calcul (84 000 × 30 / 12 = 210 000 €) est juste, mais le mot **« garantis »** est faux : la règle de trois suppose un rythme constant (or il y a week-ends, soldes, jours fériés). ✅ Version correcte : *« on **estime** environ 210 000 €, sous réserve d'un rythme stable. »*
>
> **Phrase 3 — erreur d'arrondi.** 33 % + 33 % + 33 % = **99 %**, pas 100 % ! En arrondissant chaque part, on perd 1 point. ✅ Version correcte : *« arrondir le total, pas chaque part »* → on affiche 100 % (ou on garde une décimale : 33,3 % × 3 = 99,9 %).
>
> **Ton score** : 3/3 = 🥇 Data Analyst confirmé · 2/3 = 🥈 presque · 1/3 ou 0 = relis les sections 3.3, 4 et 10, tu vas tout déchirer au 2ᵉ essai.
> </details>

---

## À retenir

- **Pourcentage** = part / total × 100. Appliquer un % = multiplier par (%/100).
- **Variation en %** = (final − initial) / **initial** × 100. Toujours diviser par la valeur de départ.
- **Coefficient multiplicateur** : +x % = ×(1 + x/100), −x % = ×(1 − x/100). Les évolutions successives se **multiplient**.
- **Point de % ≠ %** : la différence de deux taux est en **points** ; la variation relative est en **%**. Erreur la plus fréquente en entreprise.
- **Règle de trois** = produit en croix pour extrapoler ; c'est toujours une **estimation**.
- **Fraction ↔ décimal** : on divise numérateur/dénominateur. Attention virgule (FR) vs point (Python).
- **Ratio** = comparaison de deux grandeurs (ex : panier moyen = CA / nb tickets).
- **Puissance** : `**` en Python. **Racine** : `np.sqrt()` ou `** 0.5`.
- **Notation scientifique** : `a × 10ⁿ` avec 1 ≤ a < 10. Grand nombre → exposant +, petit → exposant −.
- **Ordre de grandeur** : ton réflexe anti-bug pour repérer un résultat aberrant.
- **Arrondis** : arrondis **à la fin**, pas à chaque étape ; le total des parts arrondies ne fait pas toujours 100 %.
