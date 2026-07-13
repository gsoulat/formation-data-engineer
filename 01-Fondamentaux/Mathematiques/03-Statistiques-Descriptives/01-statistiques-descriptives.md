# 03 — Statistiques descriptives

> **Le chapitre central de tout le module.** C'est ici que les mathématiques deviennent ton métier. Quand tu ouvres un fichier de ventes pour la première fois, c'est ce chapitre que tu utilises dans les 10 premières minutes.

---

## 🎬 L'histoire de ce chapitre : « La Ch'ti Boutique »

> 🛒 **Tu viens d'être embauché·e comme Data Analyst à *La Ch'ti Boutique***, une petite chaîne de 3 magasins (Lille, Roubaix, Dunkerque). Premier jour, le directeur t'envoie un fichier `ventes.csv` et te lance : *« Dis-moi ce qui se passe dans mes magasins. »*
>
> Pas de modèle d'IA, pas de dashboard sophistiqué. Juste toi, un fichier, et une question floue. **Tout ce chapitre, c'est ta boîte à outils pour répondre.** À la fin, tu sauras dire au directeur quel est son client typique, quel magasin est le plus régulier, et où se cachent les erreurs de saisie. On suit la Ch'ti Boutique du début à la fin. 🟦⬜
>
> *(Tu peux remplacer « La Ch'ti Boutique » par le commerce de ton choix : une pizzeria, un site e-commerce, une salle de sport… le fil rouge marche pour tout.)*

---

| | |
|---|---|
| **Durée** | 2 jours (≈ 14 h) |
| **Objectif** | Mener des analyses exploratoires |
| **Pré-requis** | Chapitre 1 (calcul, pourcentages, sommes Σ) · Chapitre 2 (lecture de graphiques) · bases Python/pandas |
| **Outils** | Papier + calculatrice, puis Python (`pandas`, `numpy`, `scipy.stats`, `matplotlib`, `seaborn`) |

---

## 🗺️ Ton parcours en deux niveaux (à lire avant de commencer)

Ce chapitre est riche. Pour ne pas te noyer, il est rangé en **deux niveaux** :

| Niveau | Ce que c'est | Sections |
|---|---|---|
| **✅ Noyau essentiel** | Ce que **tout** Data Analyst doit maîtriser. Tu l'utiliseras dès ta première mission. | Types de variables · Tendance centrale · Dispersion / écart-type · Quantiles / IQR · Distribution · Outliers · Boxplot |
| **🚀 Pour aller plus loin (optionnel)** | Utile, mais peut attendre. Reviens-y quand le Noyau est solide. | Coefficient de variation détaillé · Skewness chiffrée · Statistiques bivariées (covariance, tableau croisé) |

> 🧭 **Parcours conseillé.** **Fais d'abord TOUT le Noyau** (sections marquées ✅), refais les exercices correspondants, et seulement ensuite attaque l'optionnel (🚀). L'optionnel n'est pas au programme du premier projet : il prépare les chapitres 4 et 5. Pas de panique si tu le sautes au premier passage.

---

## Objectifs pédagogiques

À la fin de ce chapitre, tu sauras :

1. **Identifier le type de chaque variable** d'un jeu de données (quantitatif / qualitatif) et en déduire les bons calculs.
2. **Calculer et interpréter** moyenne, médiane et mode — et surtout **savoir lequel choisir** selon la situation.
3. **Mesurer la dispersion** d'une série (étendue, variance, écart-type, coefficient de variation) et en tirer une conclusion métier.
4. **Découper une distribution en quantiles** (Q1, médiane, Q3, IQR, percentiles).
5. **Construire et lire un tableau de fréquences, un histogramme, un boxplot.**
6. **Détecter des valeurs aberrantes** (règle de l'IQR, z-score) et **décider quoi en faire**.
7. **Démarrer une analyse à deux variables** (covariance, tableau croisé).
8. Reproduire **tous ces calculs en Python**, à la main d'abord, en code ensuite.

---

## Pourquoi c'est LE cœur du métier de Data Analyst

Un Data Analyst ne passe pas ses journées à construire des modèles d'IA. Il passe l'essentiel de son temps à **comprendre des données qu'il découvre**. Cette étape s'appelle l'**analyse exploratoire** (EDA, *Exploratory Data Analysis*).

Concrètement, dès qu'un fichier arrive sur ton bureau, tu te poses **toujours** les mêmes questions :

- « Combien de lignes ? Quelles colonnes ? De quel type ? »
- « Quelle est la valeur typique ? » → **tendance centrale**
- « Est-ce que les valeurs sont regroupées ou éparpillées ? » → **dispersion**
- « Y a-t-il des valeurs bizarres, des erreurs de saisie ? » → **outliers**
- « À quoi ressemble la forme générale des données ? » → **distribution**

> 🧭 **Image à retenir.** La statistique descriptive, c'est **le tableau de bord d'une voiture**. Avant de partir (avant un modèle, un dashboard Power BI, une recommandation métier), tu regardes la vitesse, le niveau d'essence, la température. Tu ne « décris » pas pour faire joli : tu **vérifies que les données sont saines** et tu **repères ce qui mérite attention**.

Et l'enjeu est concret. Si tu présentes au directeur d'un magasin un « panier moyen de 87 € » alors que **la moitié des clients dépensent moins de 40 €**, tu lui donnes une fausse image et il prendra de mauvaises décisions. Savoir choisir entre **moyenne et médiane** n'est pas un détail mathématique : c'est ce qui sépare une analyse juste d'une analyse trompeuse.

---

## Les types de variables ✅ *Noyau essentiel*

Avant tout calcul, **la première question** est : *de quel type est cette variable ?* Car on ne calcule pas une moyenne sur des codes postaux, et on ne fait pas un histogramme sur des noms de villes.

> 🎯 **Ça te servira pour…** trier les colonnes du fichier de la Ch'ti Boutique. Avant de lancer le moindre calcul, tu sépares ce qui se compte (les paniers, en €) de ce qui s'étiquette (le magasin, le moyen de paiement). Te tromper ici, c'est calculer un « code postal moyen » et passer pour un débutant.

### La grande division

```
                    VARIABLE
            ┌───────────┴────────────┐
      QUANTITATIVE              QUALITATIVE
      (des nombres            (des catégories,
       qu'on calcule)          des étiquettes)
      ┌─────┴─────┐           ┌─────┴──────┐
   DISCRÈTE    CONTINUE    NOMINALE     ORDINALE
  (compte,    (mesure,     (sans         (avec
   entiers)   décimales)   ordre)        ordre)
```

| Type | Définition | Exemples retail / e-commerce | Calculs autorisés |
|---|---|---|---|
| **Quantitative continue** | Une mesure qui peut prendre une infinité de valeurs (avec décimales) | montant d'un panier (87,40 €), poids d'un colis (1,23 kg), temps passé sur le site (4,7 min) | moyenne, médiane, écart-type, tout |
| **Quantitative discrète** | Un comptage, en valeurs entières | nombre d'articles dans un panier, nombre de clients/jour, nombre de retours produit | moyenne, médiane, etc. (avec bon sens : « 2,3 articles en moyenne » est correct) |
| **Qualitative nominale** | Catégories **sans ordre** | magasin (Lille, Roubaix, Dunkerque), moyen de paiement (CB, espèces, chèque), catégorie produit | **mode** (la plus fréquente), fréquences, **pas de moyenne** |
| **Qualitative ordinale** | Catégories **avec un ordre** logique | taille (S < M < L < XL), satisfaction (Mauvais < Moyen < Bon < Excellent), classe d'âge | mode, **médiane** (l'ordre le permet), fréquences |

### Le piège des « faux nombres »

Certaines colonnes **ressemblent** à des nombres mais sont en réalité qualitatives :

- Un **code postal** (59000) : on ne calcule pas un code postal moyen.
- Un **numéro de magasin** (Magasin 1, 2, 3) : c'est une étiquette nominale déguisée en nombre.
- Une **note de 1 à 5** : c'est de l'**ordinal** (on connaît l'ordre, mais l'écart entre 4 et 5 n'est pas forcément le même qu'entre 1 et 2).

> ⚠️ **Erreur courante n°1 du débutant.** Faire `df.mean()` sur tout le DataFrame et obtenir « code postal moyen = 59 347 ». Toujours qualifier le type **avant** de calculer.

### En Python : reconnaître les types

```python
import pandas as pd

ventes = pd.read_csv("ventes_magasins.csv")

# Aperçu rapide des types détectés par pandas
print(ventes.dtypes)
print(ventes.info())   # types + valeurs manquantes en un coup d'œil

# Forcer un "faux nombre" en catégorie (bonne pratique)
ventes["code_postal"] = ventes["code_postal"].astype("category")
ventes["magasin"]     = ventes["magasin"].astype("category")

# Combien de catégories différentes ?
print(ventes["magasin"].nunique())          # ex. 3 magasins
print(ventes["magasin"].value_counts())     # effectif par magasin
```

> 💡 **Réflexe métier.** `object` ou `category` → variable qualitative. `int64` / `float64` → potentiellement quantitative, **à confirmer** (un code postal est `int64` mais reste qualitatif).

---

## La tendance centrale : trouver la « valeur typique » ✅ *Noyau essentiel*

La tendance centrale répond à : *« si je devais résumer toute cette série par un seul nombre, lequel choisir ? »*

> 🎲 **Devine avant de calculer !** Le directeur de la Ch'ti Boutique te demande le « panier typique ». Un mardi matin, 7 clients dépensent : `32 ; 41 ; 38 ; 45 ; 29 ; 50 ; 47 €`. **À l'œil nu, à ton avis, la valeur typique tourne autour de combien ?** Note ton pari sur un papier. On vérifie juste en dessous. (Et garde ton chiffre : on ajoutera bientôt un client qui va tout chambouler 👀.)

### La moyenne (arithmétique)

**Définition.** La somme de toutes les valeurs divisée par leur nombre.

**Formule.**

$$\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i = \frac{x_1 + x_2 + \dots + x_n}{n}$$

**Exemple métier détaillé.** Voici les **paniers de 7 clients** un mardi matin dans un magasin de Roubaix (en €) :

```
32 ; 41 ; 38 ; 45 ; 29 ; 50 ; 47
```

**Calcul à la main, pas à pas :**

1. Somme : `32 + 41 + 38 + 45 + 29 + 50 + 47 = 282`
2. Nombre de valeurs : `n = 7`
3. Moyenne : `282 / 7 = 40,29 €`

➡️ **Le panier moyen est de 40,29 €.** Information utile pour estimer le chiffre d'affaires : `CA ≈ panier moyen × nombre de clients`.

**Le défaut majeur — la sensibilité aux valeurs extrêmes.** Imagine qu'un 8ᵉ client passe et achète un gros électroménager à **560 €** :

```
32 ; 41 ; 38 ; 45 ; 29 ; 50 ; 47 ; 560
```

- Nouvelle somme : `282 + 560 = 842`
- Nouvelle moyenne : `842 / 8 = 105,25 €`

➡️ La moyenne **double presque** (40 € → 105 €) à cause d'**un seul client**. Or **aucun** des autres clients ne dépense 105 €. La moyenne est devenue **trompeuse**. C'est LE moment où il faut sortir la médiane.

### La médiane

**Définition.** La valeur qui **partage la série triée en deux moitiés égales** : 50 % des valeurs en dessous, 50 % au-dessus.

> 🧠 **Analogie : le client du milieu de la file.** Imagine tous tes clients alignés du plus petit panier au plus gros. La médiane, c'est **le panier de la personne pile au milieu de la file**. Peu importe que le dernier de la file ait dépensé 50 € ou 5 000 € : la personne du milieu, elle, ne bouge pas. C'est pour ça que la médiane est **insensible aux extrêmes**.
>
> 🎲 **Devine !** Reprends le client surprise à **560 €** ajouté plus haut. La **moyenne** vient de bondir à 105 €. À ton avis, de combien la **médiane** va-t-elle bouger : beaucoup, un peu, ou presque pas ? Réponds avant de lire le calcul.

**Méthode à la main :**

1. **Trier** les valeurs dans l'ordre croissant.
2. Si `n` est **impair** → la médiane est la valeur du milieu (position `(n+1)/2`).
3. Si `n` est **pair** → la médiane est la **moyenne des deux valeurs centrales**.

**Exemple (les 7 paniers d'origine) :**

```
Trié : 29 ; 32 ; 38 ; [41] ; 45 ; 47 ; 50
```

`n = 7` (impair), position du milieu = `(7+1)/2 = 4ᵉ valeur` → **médiane = 41 €**.

**Exemple avec le client à 560 € (n = 8, pair) :**

```
Trié : 29 ; 32 ; 38 ; [41 ; 45] ; 47 ; 50 ; 560
```

Les deux valeurs centrales (4ᵉ et 5ᵉ) sont **41 et 45**. Médiane = `(41 + 45)/2 = 43 €`.

➡️ **La médiane passe de 41 € à 43 € seulement**, alors que la moyenne avait bondi à 105 €. La médiane est **robuste** : un seul gros achat ne la déstabilise pas. Elle représente bien « le client typique ».

> 🎯 **La règle d'or du métier.**
> - Données **symétriques, sans valeurs extrêmes** → **moyenne**.
> - Données **asymétriques ou avec outliers** (salaires, prix immobiliers, paniers, durées) → **médiane**.
> - Les médias et l'INSEE parlent toujours de **salaire médian** (≈ 2 100 € net en France) précisément parce que quelques très hauts salaires tirent la **moyenne** vers le haut artificiellement.

> 🎯 **Ça te servira pour…** ne pas mentir au directeur sans le vouloir. Si tu annonces « panier moyen 105 € » à cause d'un seul gros achat, il va sur-stocker des produits chers que personne n'achète. En annonçant « panier médian 43 € », tu décris le vrai client. **Choisir moyenne ou médiane = ton premier vrai geste d'analyste.**

### Le mode

**Définition.** La valeur (ou la catégorie) **la plus fréquente**.

**Exemple métier.** Sur les tailles de t-shirts vendues : `M, L, M, S, M, L, XL, M`. Le mode est **M** (4 occurrences). C'est **la seule mesure de tendance centrale utilisable sur du qualitatif nominal** (« le moyen de paiement le plus courant », « le magasin qui vend le plus »).

Une série peut être **bimodale** (deux pics) — un signal intéressant : par exemple un magasin avec un pic de petits paniers (achat dépannage) ET un pic de gros paniers (courses hebdo).

### Comparatif : quand utiliser quoi ?

| Mesure | Idéale pour | Sensible aux extrêmes ? | Marche sur du qualitatif ? |
|---|---|---|---|
| **Moyenne** | données régulières, calcul de totaux (CA = moyenne × n) | ⚠️ **Oui, très** | Non |
| **Médiane** | données asymétriques, salaires, paniers, prix | ✅ Non (robuste) | Ordinal seulement |
| **Mode** | catégories, données qualitatives | Non | ✅ Oui |

### En Python

```python
import numpy as np
import pandas as pd
from scipy import stats

paniers = pd.Series([32, 41, 38, 45, 29, 50, 47, 560])  # avec le gros achat

print("Moyenne :", paniers.mean())      # 105.25  -> tirée par le 560
print("Médiane :", paniers.median())    # 43.0    -> robuste, "client typique"
print("Mode    :", paniers.mode()[0])   # première valeur la plus fréquente

# Le mode sur du qualitatif
ventes["moyen_paiement"].mode()         # ex. "CB"
ventes["magasin"].value_counts().idxmax()  # le magasin le plus fréquent
```

> ⚠️ **Erreur courante n°2.** Présenter une moyenne sans regarder si la distribution est asymétrique. **Réflexe : toujours comparer moyenne et médiane.** Si elles sont très différentes → il y a de l'asymétrie ou des outliers, et la médiane est plus honnête.

---

## La dispersion : les données sont-elles regroupées ou éparpillées ? ✅ *Noyau essentiel*

Deux séries peuvent avoir **exactement la même moyenne** mais raconter des histoires totalement différentes.

```
Magasin A (ventes/jour, k€) :  48  50  52  49  51   →  moyenne 50, très régulier
Magasin B (ventes/jour, k€) :  10  90  20  80  50   →  moyenne 50, en montagnes russes
```

Même moyenne (50), mais le magasin A est **prévisible** et le B est **chaotique**. La dispersion mesure exactement cette différence. **C'est une information de gestion capitale** : un magasin régulier est plus facile à planifier (stock, personnel).

> 🎲 **Devine avant de calculer !** Sans faire un seul calcul, regarde les deux séries du magasin A et du magasin B ci-dessus. **Lequel des deux a, selon toi, le plus grand écart-type ?** (Indice : lequel part dans tous les sens ?) Note ton pari. On le confirmera avec les chiffres dans quelques lignes — tu verras, ton intuition était sûrement bonne, et c'est exactement ce que l'écart-type met en nombre.

> 🧠 **Analogie : à quel point la classe est homogène.** Imagine deux classes avec la **même moyenne** de 12/20. Dans l'une, tout le monde a entre 11 et 13 (classe homogène). Dans l'autre, la moitié a 4 et l'autre 20 (classe éclatée). **L'écart-type, c'est ça** : à quel point les valeurs sont serrées autour de la moyenne. Petit écart-type = tout le monde proche de la moyenne. Grand écart-type = ça part dans tous les sens.

### L'étendue

**Définition.** `Étendue = valeur max − valeur min`.

- Magasin A : `52 − 48 = 4`
- Magasin B : `90 − 10 = 80`

Simple et parlant, mais **ultra-sensible** : une seule valeur extrême gonfle l'étendue. On l'utilise comme premier indice, jamais seule.

### La variance

**Définition.** La moyenne des **carrés des écarts à la moyenne**. Elle mesure « à quel point, en moyenne, les valeurs s'éloignent de la moyenne ».

**Formule (variance de population) :**

$$\sigma^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i - \bar{x})^2$$

**Pourquoi des carrés ?** Si on additionnait simplement les écarts `(x_i − x̄)`, les écarts positifs et négatifs s'annuleraient (la somme fait toujours 0). On les met **au carré** pour les rendre tous positifs et pour pénaliser fortement les gros écarts.

**Calcul à la main, pas à pas — Magasin A :** moyenne = 50.

| Valeur | Écart `(x − 50)` | Écart² |
|---|---|---|
| 48 | −2 | 4 |
| 50 | 0 | 0 |
| 52 | +2 | 4 |
| 49 | −1 | 1 |
| 51 | +1 | 1 |
| **Somme des carrés** | | **10** |

Variance = `10 / 5 = 2`.

**Le problème de la variance** : elle est en **unités au carré** (ici « k€ au carré »), donc **non interprétable** directement. D'où l'écart-type.

### L'écart-type — LA mesure reine

**Définition.** La **racine carrée de la variance**. On revient ainsi dans **l'unité d'origine**, ce qui le rend interprétable.

$$\sigma = \sqrt{\sigma^2}$$

- Magasin A : `√2 ≈ 1,41 k€`
- Magasin B : la variance (de population, ÷n, comme pour le magasin A) vaut `(40² + 40² + 30² + 30² + 0²) / 5 = 5000 / 5 = 1000`, donc `√1000 ≈ 31,6 k€`

➡️ **Interprétation métier concrète.** L'écart-type, c'est la **régularité**. « Les ventes du magasin A s'écartent en moyenne de **1,4 k€** de leur moyenne de 50 k€ : c'est très régulier. Celles du B s'écartent de **32 k€** : imprévisible. » Un petit écart-type = **régularité, prévisibilité**. Un grand écart-type = **volatilité, risque**.

> 🎲 **Pari gagné ?** Tu avais parié sur le magasin B comme le plus dispersé. ✅ Confirmé : 31,6 k€ contre 1,41 k€ pour A. Ton œil avait raison — l'écart-type ne fait que mettre **un chiffre précis** sur ce que tu voyais déjà.

> 🎯 **Ça te servira pour…** juger la **régularité des ventes** d'un magasin. Tu diras au directeur : « Lille est ultra-prévisible (faible écart-type), tu peux planifier les stocks sereinement. Roubaix est en montagnes russes (gros écart-type), prévois de la marge. » L'écart-type transforme une intuition floue en argument chiffré.

> 🧠 **Variance n−1 ou n ?** Quand tu calcules l'écart-type sur un **échantillon** pour estimer celui de la population (le cas le plus fréquent en data), on divise par **`n − 1`** (correction de Bessel) au lieu de `n`. C'est ce que fait **pandas par défaut** (`ddof=1`), tandis que **numpy** divise par `n` par défaut (`ddof=0`). **Source classique d'écarts entre tes résultats** — voir l'erreur courante plus bas.

### Le coefficient de variation (CV) 🚀 *Pour aller plus loin (optionnel)*

> 🚀 **Optionnel au premier passage.** L'écart-type (5.3) suffit largement pour ta première analyse. Le CV devient utile **seulement** quand tu compares deux choses de tailles très différentes. Tu peux y revenir plus tard sans rien rater de l'essentiel.

**Problème.** Peut-on comparer la régularité d'un magasin qui vend pour 50 k€/jour et d'une boutique qui vend pour 2 k€/jour ? Comparer leurs écarts-types bruts n'a pas de sens (les échelles diffèrent).

**Définition.** Le CV exprime l'écart-type **en pourcentage de la moyenne** — c'est une mesure **relative**, sans unité.

$$CV = \frac{\sigma}{\bar{x}} \times 100$$

- Magasin A : `1,41 / 50 × 100 ≈ 2,8 %` → extrêmement régulier.
- Petite boutique avec σ = 0,3 et moyenne 2 : `0,3 / 2 × 100 = 15 %` → plus irrégulière, **alors que son écart-type brut est plus petit**.

➡️ **Usage métier.** Comparer la régularité/le risque de produits ou magasins **d'échelles différentes**. Un CV < 15 % est généralement jugé « stable ». Indispensable pour comparer des choses qui n'ont pas la même grandeur.

### En Python

```python
import numpy as np
import pandas as pd

a = pd.Series([48, 50, 52, 49, 51])
b = pd.Series([10, 90, 20, 80, 50])

print(a.max() - a.min())          # étendue : 4
print(a.var(ddof=0))              # variance population : 2.0
print(a.std(ddof=0))              # écart-type population : ~1.41

# Attention au ddof ! pandas=1 par défaut, numpy=0 par défaut
print(a.std())                    # pandas par défaut ddof=1 -> ~1.58
print(np.std(a))                  # numpy par défaut ddof=0  -> ~1.41

# Coefficient de variation (en %)
cv_a = a.std(ddof=0) / a.mean() * 100
cv_b = b.std(ddof=0) / b.mean() * 100
print(f"CV A = {cv_a:.1f}%  |  CV B = {cv_b:.1f}%")
```

> ⚠️ **Erreur courante n°3.** Confondre variance et écart-type. La **variance** sert aux calculs (c'est l'objet mathématique), l'**écart-type** sert à **parler aux humains** (même unité que les données). On communique toujours en écart-type.

---

## Les quantiles : découper la distribution ✅ *Noyau essentiel*

Les quantiles **divisent une série triée en parts égales**. C'est l'outil n°1 pour résumer une distribution **sans se faire piéger par les extrêmes**.

> 🧠 **Analogie : couper le gâteau des clients en parts.** Tu alignes tous les clients du plus petit au plus gros panier (comme pour la médiane), puis tu **coupes la file en 4 parts égales**. Les 3 traits de coupe sont Q1, la médiane (Q2) et Q3. Le **cœur des clients** (les 50 % du milieu) tient entre Q1 et Q3 : c'est l'IQR.

> 🎯 **Ça te servira pour…** **repérer une saisie erronée** sans te faire piéger. L'IQR délimite la zone « normale » des paniers. Toute valeur très en dehors → suspecte (virgule oubliée, doublon, robot). C'est la base de la détection d'outliers de la section 8.

### Les quartiles

Les quartiles découpent la série en **4 parts de 25 %** :

```
   25%      25%      25%      25%
[------|---------|---------|------]
min   Q1   médiane(Q2)   Q3      max
```

- **Q1 (1ᵉʳ quartile)** : 25 % des valeurs sont en dessous.
- **Q2 (2ᵉ quartile)** : c'est la **médiane** (50 %).
- **Q3 (3ᵉ quartile)** : 75 % des valeurs sont en dessous.

### L'IQR — l'écart interquartile

**Définition.** `IQR = Q3 − Q1`. C'est l'**étendue des 50 % centraux** de la série, le « cœur » des données. **Robuste** : il ignore les 25 % du bas et les 25 % du haut, donc les extrêmes n'ont aucun effet sur lui.

### Calcul à la main, pas à pas

Paniers de 11 clients d'un magasin de Lille (triés, en €) :

```
20 ; 25 ; 30 ; 35 ; 40 ; 45 ; 50 ; 55 ; 60 ; 80 ; 200
```

(`n = 11`. Le 200 € est un client suspect — on y revient.)

> 🎲 **Devine !** Le client à **200 €** est très au-dessus des autres. À ton avis, va-t-il **changer le Q3** (la borne du « cœur » des clients) ? Beaucoup, un peu, ou pas du tout ? Compare ton intuition au résultat ci-dessous.

1. **Médiane (Q2)** : position `(11+1)/2 = 6ᵉ` valeur → **45 €**.
2. **Q1** : médiane de la **moitié basse** `20;25;30;35;40` → valeur centrale = **30 €**.
3. **Q3** : médiane de la **moitié haute** `50;55;60;80;200` → valeur centrale = **60 €**.
4. **IQR** = `Q3 − Q1 = 60 − 30 = 30 €`.

➡️ **Lecture métier.** « La moitié centrale des clients dépense entre **30 et 60 €** (IQR = 30 €). » Remarque que le client à 200 € **n'a pas bougé le Q3** : c'est toute la force des quantiles.

> ℹ️ Il existe plusieurs **méthodes d'interpolation** des quantiles. Ton calcul manuel et `numpy`/`pandas` peuvent différer de quelques décimales selon la méthode (`linear` par défaut). C'est normal et sans gravité pour l'interprétation.

### Les percentiles

Même principe, mais on découpe en **100 parts**. Le percentile P90 = la valeur en dessous de laquelle se trouvent 90 % des données.

**Usage métier ultra-fréquent :**
- **P90 / P95 des temps de chargement** d'un site : « 95 % des pages chargent en moins de 1,8 s » (les SLA web se mesurent en percentiles, pas en moyenne, car la moyenne cache les pires cas).
- **P90 des paniers** : « les 10 % de meilleurs clients dépensent plus de X € » → cible marketing prioritaire.

> Q1 = P25, médiane = P50, Q3 = P75. Les quartiles **sont** des percentiles particuliers.

### En Python

```python
paniers = pd.Series([20, 25, 30, 35, 40, 45, 50, 55, 60, 80, 200])

print(paniers.quantile(0.25))   # Q1
print(paniers.quantile(0.50))   # médiane
print(paniers.quantile(0.75))   # Q3

q1, q3 = paniers.quantile(0.25), paniers.quantile(0.75)
iqr = q3 - q1
print(f"Q1={q1}  Q3={q3}  IQR={iqr}")

# Percentiles personnalisés
print(paniers.quantile([0.10, 0.90, 0.95]))

# La synthèse complète d'un coup — l'outil n°1 de l'analyste
print(paniers.describe())
# count, mean, std, min, 25%, 50% (médiane), 75%, max
```

> 💡 **`df.describe()` est ton premier réflexe sur tout nouveau jeu de données.** Il te donne en une ligne : nombre de valeurs, moyenne, écart-type, min, Q1, médiane, Q3, max. Pour les colonnes qualitatives : `df.describe(include="object")` donne le nombre de catégories, le mode et sa fréquence.

---

## La distribution : la forme des données ✅ *Noyau essentiel*

> 🎯 **Ça te servira pour…** *voir* d'un coup d'œil la forme des paniers de la Ch'ti Boutique : sont-ils tous serrés autour de 40 € (cloche) ou y a-t-il une longue traîne de gros acheteurs ? La forme te dit immédiatement s'il faut communiquer en moyenne ou en médiane.

### Le tableau de fréquences

Pour résumer une variable, on compte combien de valeurs tombent dans chaque catégorie ou chaque tranche.

**Exemple — répartition des paniers d'une journée (200 clients) par tranches :**

| Tranche de panier | Effectif (fréquence absolue) | Fréquence relative | Fréquence cumulée |
|---|---|---|---|
| [0–20[ € | 30 | 15 % | 15 % |
| [20–40[ € | 80 | 40 % | 55 % |
| [40–60[ € | 50 | 25 % | 80 % |
| [60–80[ € | 25 | 12,5 % | 92,5 % |
| [80 €+[ | 15 | 7,5 % | 100 % |
| **Total** | **200** | **100 %** | |

➡️ **Lecture métier.** La fréquence cumulée dit que **55 % des clients dépensent moins de 40 €**. Donc une promo « 5 € offerts dès 50 € d'achat » concerne surtout les 20 % du haut — peut-être pas la bonne cible.

### L'histogramme

L'histogramme est la **traduction visuelle** du tableau de fréquences : des barres dont la hauteur représente l'effectif de chaque tranche. C'est **le graphique pour visualiser la forme** d'une variable quantitative.

> ⚠️ Histogramme ≠ diagramme en barres. L'**histogramme** sert au **quantitatif** (les barres se touchent, l'axe X est continu). Le **diagramme en barres** sert au **qualitatif** (barres séparées, catégories). Erreur de vocabulaire fréquente en jury.

### L'asymétrie (skewness)

> ✅ **À garder du Noyau :** le **test express** « moyenne > médiane → queue à droite → utilise la médiane ». C'est tout ce dont tu as besoin au quotidien.
> 🚀 **Optionnel :** la **valeur chiffrée** du skew (`.skew()`, le signe exact, les schémas détaillés). Utile pour les chapitres suivants, pas indispensable pour ta première EDA.

La **forme** d'une distribution te dit immédiatement quelle mesure de tendance centrale privilégier.

```
  Symétrique          Asymétrie à droite       Asymétrie à gauche
 (skew ≈ 0)            (skew > 0, positive)     (skew < 0, négative)
     ▁▃▅█▅▃▁              █▅▃▂▁▁▁                  ▁▁▁▂▃▅█
   moy = méd          moy > médiane            moy < médiane
                      (queue à droite)         (queue à gauche)
```

- **Symétrique** (skew ≈ 0) : moyenne ≈ médiane (ex. tailles humaines, la fameuse « cloche »).
- **Asymétrie positive / à droite** (skew > 0) : une longue queue vers les grandes valeurs tire la **moyenne au-dessus de la médiane**. **Très fréquent en business** : salaires, paniers, prix, durées. → **utilise la médiane.**
- **Asymétrie négative / à gauche** (skew < 0) : queue vers les petites valeurs (ex. âge au décès, notes d'un examen facile).

> 🎯 **Le test express.** Si **moyenne > médiane** → asymétrie à droite → présente la médiane. Si elles sont proches → la moyenne est fiable. Tu peux diagnostiquer une distribution **avant même de tracer un graphique**, juste avec `describe()`.

### En Python (seaborn / matplotlib)

```python
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Histogramme + courbe de densité (KDE)
sns.histplot(data=ventes, x="panier", bins=20, kde=True)
plt.title("Distribution des paniers")
plt.xlabel("Montant du panier (€)")
plt.ylabel("Nombre de clients")
plt.show()

# Tableau de fréquences par tranches
tranches = pd.cut(ventes["panier"], bins=[0, 20, 40, 60, 80, 1000])
freq = ventes.groupby(tranches, observed=True).size()
print(freq)
print((freq / freq.sum() * 100).round(1))   # fréquences relatives en %

# Mesurer l'asymétrie
print("Skewness :", ventes["panier"].skew())     # >0 = queue à droite
print("Moyenne :", ventes["panier"].mean(),
      "| Médiane :", ventes["panier"].median())
```

---

## Les valeurs aberrantes (outliers) ✅ *Noyau essentiel*

> 🧠 **Analogie : le client qui détonne.** Dans la file de clients de la Ch'ti Boutique, l'outlier c'est **celui qui pousse un caddie de 200 € au milieu de gens qui prennent un sandwich**. Soit il existe vraiment (achat pro), soit c'est une erreur de caisse. Ton job : enquêter, pas supprimer en douce.

> 🎯 **Ça te servira pour…** **repérer une saisie erronée** (virgule oubliée : 2 000 € au lieu de 20,00 €) avant qu'elle ne pollue toutes tes moyennes. C'est le pont direct vers le **nettoyage des données**.

Une **valeur aberrante** est une observation anormalement éloignée des autres. Pour un Data Analyst c'est **double enjeu** :

1. **Une erreur de saisie** à corriger (un panier à 2 000 € au lieu de 20,00 € — virgule oubliée), un âge de 200 ans, une vente négative. → lien direct avec le **nettoyage des données**.
2. **Un vrai phénomène à comprendre** (un achat professionnel en gros, une fraude, un client exceptionnel). → à **analyser**, pas à jeter aveuglément.

### Méthode 1 — La règle de l'IQR (1,5 × IQR)

C'est la méthode **standard**, robuste, et celle qui dessine les moustaches du boxplot. On définit deux bornes :

$$\text{Borne basse} = Q_1 - 1{,}5 \times IQR \qquad \text{Borne haute} = Q_3 + 1{,}5 \times IQR$$

Toute valeur **hors de ces bornes** est signalée comme outlier potentiel.

**Reprenons les paniers de Lille** : `Q1 = 30`, `Q3 = 60`, `IQR = 30`.

- Borne basse = `30 − 1,5 × 30 = 30 − 45 = −15 €` (impossible, donc aucun outlier bas).
- Borne haute = `60 + 1,5 × 30 = 60 + 45 = 105 €`.

➡️ Le client à **200 € dépasse 105 €** : c'est un **outlier** détecté. Tu vas alors enquêter : erreur de saisie ? achat groupé ? On ne supprime jamais sans comprendre.

### Méthode 2 — Le z-score

Le **z-score** mesure « à combien d'écarts-types de la moyenne se trouve une valeur ».

$$z = \frac{x - \bar{x}}{\sigma}$$

Convention usuelle : si **|z| > 3**, la valeur est suspecte (au-delà de 3 écarts-types, on est dans les ~0,3 % les plus extrêmes pour une distribution en cloche).

**Exemple.** Une série de paniers de moyenne 45 € et d'écart-type 18 €. Pour le client à 200 € :

$$z = \frac{200 - 45}{18} = \frac{155}{18} \approx 8{,}6$$

`|z| = 8,6 > 3` → **valeur très anormale**, à investiguer en priorité.

> ⚠️ **Limite du z-score.** Il utilise moyenne et écart-type, **eux-mêmes tirés par les outliers**. Sur des données **très asymétriques**, préfère la **règle de l'IQR** (robuste). Le z-score est plus adapté aux distributions à peu près symétriques (en cloche).

### Que faire d'un outlier ?

| Situation | Décision |
|---|---|
| Erreur évidente (panier 2 000 € = virgule oubliée, âge 200 ans) | **Corriger** si possible, sinon supprimer/mettre en `NaN` (→ nettoyage) |
| Valeur réelle mais extrême (gros achat pro, client VIP) | **Conserver**, et **documenter**. Éventuellement analyser à part |
| Doute | Garder, **signaler dans le rapport**, calculer les stats **avec et sans** pour mesurer l'impact |

> 🧭 **Règle d'or absolue.** **On ne supprime JAMAIS un outlier en silence.** On enquête, on décide, et on **trace la décision** dans le rapport d'analyse. Supprimer des données sans justification est une faute professionnelle.

### En Python

```python
import numpy as np
from scipy import stats

x = ventes["panier"]

# --- Méthode IQR ---
q1, q3 = x.quantile(0.25), x.quantile(0.75)
iqr = q3 - q1
borne_basse = q1 - 1.5 * iqr
borne_haute = q3 + 1.5 * iqr
outliers_iqr = ventes[(x < borne_basse) | (x > borne_haute)]
print(f"Bornes : [{borne_basse:.1f} ; {borne_haute:.1f}]")
print(outliers_iqr[["client", "panier"]])

# --- Méthode z-score ---
ventes["zscore"] = np.abs(stats.zscore(x))
outliers_z = ventes[ventes["zscore"] > 3]
print(outliers_z[["client", "panier", "zscore"]])

# Comparer l'impact : stats avec et sans outliers
sans = ventes[(x >= borne_basse) & (x <= borne_haute)]
print("Moyenne avec :", x.mean(), "| sans :", sans["panier"].mean())
```

---

## Le boxplot (boîte à moustaches) ✅ *Noyau essentiel*

Le boxplot est **le résumé visuel ultime** d'une distribution : il affiche d'un coup la médiane, les quartiles, la dispersion **et les outliers**. C'est l'outil préféré pour **comparer plusieurs groupes** (magasins, mois, catégories).

> 🧠 **Analogie : la carte d'identité d'un magasin en une image.** Le boxplot rassemble tout ce que tu as appris : la **boîte** = le cœur des clients (Q1→Q3), le **trait** = le client du milieu (médiane), les **points isolés** = les clients qui détonnent (outliers). Une seule image et tu lis la médiane, la dispersion ET les anomalies.

> 🎯 **Ça te servira pour…** **comparer les 3 magasins de la Ch'ti Boutique côte à côte** en une seule figure dans ton rapport. Le directeur voit instantanément qui est régulier, qui est dispersé, et où sont les achats suspects. C'est LE graphique que tu mettras dans ta présentation.

### Anatomie d'un boxplot

```
  outlier
    ○                              ← point isolé au-delà de la moustache
    │
  ──┴──   ← moustache haute (jusqu'au max DANS la limite Q3+1,5·IQR)
 ┌─────┐
 │     │  ← Q3 (haut de la boîte)
 ├─────┤  ← MÉDIANE (trait dans la boîte)
 │     │  ← Q1 (bas de la boîte)
 └─────┘
  ──┬──   ← moustache basse (jusqu'au min DANS la limite Q1−1,5·IQR)
```

- **La boîte** = de Q1 à Q3 → contient les **50 % centraux** (sa hauteur = IQR).
- **Le trait dans la boîte** = la **médiane**.
- **Les moustaches** = jusqu'à la dernière valeur **dans** la limite des 1,5×IQR.
- **Les points isolés** = les **outliers** (au-delà des moustaches).

### Comment lire un boxplot (réflexes métier)

- **Boîte courte** → données regroupées, **régulières**. **Boîte longue** → données dispersées.
- **Médiane décentrée dans la boîte** → distribution **asymétrique** (proche de Q1 = queue vers le haut).
- **Beaucoup de points isolés** → présence d'outliers, données à vérifier.
- **Comparer deux boîtes côte à côte** : « Le magasin de Lille a une médiane plus haute mais une boîte plus longue → il vend plus en moyenne mais de façon moins régulière que Dunkerque. »

### En Python (seaborn)

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Un seul groupe
sns.boxplot(data=ventes, y="panier")
plt.title("Distribution des paniers")
plt.show()

# Comparaison entre magasins — le vrai cas d'usage
sns.boxplot(data=ventes, x="magasin", y="panier")
plt.title("Paniers par magasin")
plt.ylabel("Montant du panier (€)")
plt.show()
```

> 💡 **Boxplot vs histogramme.** L'histogramme montre la **forme détaillée** d'**une** variable. Le boxplot est plus **compact** et **idéal pour comparer plusieurs groupes** et **repérer les outliers** d'un coup d'œil. En EDA, on utilise souvent les deux.

---

## Statistiques bivariées : introduction à deux variables 🚀 *Pour aller plus loin (optionnel)*

> 🚀 **Toute cette section est optionnelle au premier passage.** Elle ouvre la porte à l'analyse de **deux variables à la fois**, qui sera vraiment développée au **chapitre 5 (corrélation)**. Tu peux la garder pour quand le Noyau (sections 3 à 9) est parfaitement digéré. Rien ici n'est nécessaire pour boucler une première EDA propre.

Jusqu'ici, une variable à la fois. Mais l'analyse devient vraiment utile quand on regarde **deux variables ensemble** : *« le budget marketing influence-t-il les ventes ? »*, *« le moyen de paiement dépend-il du magasin ? »*

### La covariance (variables quantitatives) 🚀 *(optionnel)*

**Définition.** La covariance mesure si **deux variables varient ensemble** :

- Covariance **positive** → quand l'une monte, l'autre tend à monter (budget pub ↑ et ventes ↑).
- Covariance **négative** → quand l'une monte, l'autre tend à baisser (prix ↑ et quantité vendue ↓).
- Covariance **≈ 0** → pas de lien linéaire apparent.

**Formule :**

$$\text{cov}(x,y) = \frac{1}{n}\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})$$

**La grande limite.** La covariance dépend des **unités** (en €×unités…) : un gros nombre ne dit pas si le lien est fort. C'est pourquoi on lui préfère le **coefficient de corrélation** (covariance normalisée entre −1 et +1) — qui sera **détaillé au chapitre 5**. Retiens pour l'instant : la **covariance donne le signe** (sens du lien), la **corrélation donnera la force**.

```python
ventes[["budget_pub", "ventes"]].cov()     # matrice de covariance
ventes[["budget_pub", "ventes"]].corr()    # aperçu de la corrélation (chap. 5)
```

### Le tableau croisé (variables qualitatives)

Pour croiser **deux variables qualitatives**, on compte les effectifs de chaque combinaison.

**Exemple — moyen de paiement par magasin :**

| | CB | Espèces | Chèque | **Total** |
|---|---|---|---|---|
| **Lille** | 120 | 30 | 10 | 160 |
| **Roubaix** | 60 | 70 | 20 | 150 |
| **Dunkerque** | 80 | 25 | 5 | 110 |
| **Total** | 260 | 125 | 35 | **420** |

➡️ **Lecture métier.** À Roubaix, les espèces dominent presque autant que la CB — info utile pour dimensionner les fonds de caisse. À Lille, la CB écrase tout. Le tableau croisé est la base de l'analyse de **dépendance entre catégories** (le test du χ² viendra plus tard).

```python
# Tableau croisé des effectifs
pd.crosstab(ventes["magasin"], ventes["moyen_paiement"])

# En pourcentages par ligne (profil de chaque magasin)
pd.crosstab(ventes["magasin"], ventes["moyen_paiement"], normalize="index").round(3) * 100

# Avec les totaux
pd.crosstab(ventes["magasin"], ventes["moyen_paiement"], margins=True)
```

---

## 🏆 Le Défi du chapitre — « Sauve la réunion du directeur »

> 🎮 **Mission finale.** Le directeur de la Ch'ti Boutique entre dans ton bureau dans 5 minutes. Il a sous les yeux un fichier des **paniers du magasin de Roubaix** (un samedi) :
>
> ```
> 38 ; 42 ; 35 ; 40 ; 45 ; 39 ; 41 ; 37 ; 44 ; 1 950
> ```
>
> Il s'apprête à annoncer en réunion : **« Notre panier moyen est de 231 € ! On vise le haut de gamme ! »**
>
> **Sans Python, juste avec ta tête et ce chapitre, réponds aux 4 questions avant qu'il ne parle :**
>
> 1. 🎲 *Devine d'abord :* le 1 950 € est-il un client réel ou une erreur de saisie probable ? Pourquoi ?
> 2. La moyenne (231 €) est-elle un bon résumé ? Calcule la **médiane** et compare.
> 3. Applique la **règle 1,5 × IQR** : le 1 950 € est-il officiellement un outlier ?
> 4. **Que dis-tu au directeur** en une phrase pour sauver la réunion ?
>
> 🥉 Tu réponds à 2 questions · 🥈 tu réponds à 3 · 🥇 tu réponds aux 4 ET ta phrase finale mentionne médiane + outlier + une action concrète.

<details>
<summary>🏆 Voir la solution du Défi</summary>

**1. Réel ou erreur ?** Très probablement une **erreur de saisie** (ex. 19,50 € tapé sans virgule, ou un doublon). Un panier 45× plus gros que tous les autres un samedi ordinaire est suspect. → On enquête, on ne supprime pas en silence.

**2. Moyenne vs médiane.**
- Moyenne = `(38+42+35+40+45+39+41+37+44+1950)/10 = 2 311/10 = 231,1 €` → absurde, aucun client ne dépense ça.
- Médiane (n=10, pair) : série triée `35;37;38;39;[40;41];42;44;45;1950`. Les 2 valeurs centrales (5ᵉ et 6ᵉ) sont **40 et 41** → médiane = `(40+41)/2 = 40,5 €`. **Voilà le vrai panier typique.**

**3. Règle 1,5 × IQR** (sur la série triée, n=10) :
- Moitié basse `35;37;38;39;40` → **Q1 = 38**. Moitié haute `41;42;44;45;1950` → **Q3 = 44**.
- IQR = `44 − 38 = 6`. Borne haute = `44 + 1,5×6 = 44 + 9 = 53 €`.
- `1 950 € ≫ 53 €` → **outlier confirmé**, et de très loin.

**4. Phrase pour sauver la réunion :** *« Attention, le panier moyen de 231 € est faussé par une valeur à 1 950 € qui est presque sûrement une erreur de saisie (le panier typique est de 40,5 €, médiane). Je vérifie cette ligne avant qu'on communique quoi que ce soit. »* 🎯 Médiane + outlier + action = tu viens d'éviter une grosse boulette de com'.

</details>

---

## Vidéos d'auto-formation

> Visionne-les en **complément** : la statistique se comprend mieux en voyant les graphiques s'animer. StatQuest (Josh Starmer) est la référence mondiale, claire et visuelle.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| The Mean, The Median, and The Mode | StatQuest (Josh Starmer) | 🇬🇧 EN | ≈ 8 min | https://www.youtube.com/watch?v=-14BImgVENA | Comprendre visuellement les 3 tendances centrales et **quand chacune trompe** |
| Quantiles and Percentiles, Clearly Explained!!! | StatQuest (Josh Starmer) | 🇬🇧 EN | ≈ 7 min | https://www.youtube.com/watch?v=IFKQLDmRK0Y | Quartiles, percentiles et leur logique de découpage, en images |
| LE COURS : Statistiques (Seconde) — moyenne, médiane, étendue, quartiles, écart-type | Yvan Monka | 🇫🇷 FR | ≈ 30 min | https://www.youtube.com/watch?v=dZ1arqz41Bg | Le cours complet en français, toutes les notions du chapitre pas à pas |
| EXERCICE : Calculer une moyenne, une médiane, des quartiles (Seconde) | Yvan Monka | 🇫🇷 FR | ≈ 8 min | https://www.youtube.com/watch?v=qKrgLZKGE8o | S'entraîner au **calcul à la main** des quartiles sur une vraie série |
| EXERCICE : Calculer la variance et l'écart-type (Seconde) | Yvan Monka | 🇫🇷 FR | ≈ 7 min | https://www.youtube.com/watch?v=b4w0POaFVJQ | Méthode détaillée pour **variance et écart-type** à la main |
| Calculer l'écart interquartile (IQR) — Seconde | Yvan Monka | 🇫🇷 FR | ≈ 6 min | https://www.youtube.com/watch?v=IjsDK0ODwlw | L'**IQR** expliqué et calculé étape par étape |
| StatQuest : recherche « histograms / boxplots » | StatQuest (Josh Starmer) | 🇬🇧 EN | playlist | https://www.youtube.com/results?search_query=statquest+boxplots+histograms | Histogrammes et boxplots animés (lien de recherche, choisis la dernière vidéo officielle) |

> Tous ces liens sont des liens **réels** (sauf le dernier, volontairement un lien de recherche YouTube). Si une URL ne fonctionne plus, cherche le titre exact sur YouTube.

---

## Exercices

> Fais-les **dans l'ordre**, papier d'abord, Python ensuite. Les corrigés sont sous les flèches `▶`.
>
> ✅ **Priorité Noyau :** les exercices 1 à 8 couvrent tout le Noyau essentiel (types, moyenne/médiane, écart-type, quartiles/IQR, z-score, asymétrie, EDA Python, boxplot). Fais-les tous : ce sont exactement les gestes de ta première mission. 🎲 Pour chacun, **devine le résultat avant de calculer** — tu muscles ton intuition d'analyste.

### Exercice 1 — Types de variables (échauffement)

Pour chaque colonne d'un fichier de ventes, donne le type (quantitatif continu/discret, qualitatif nominal/ordinal) :
`montant_panier` · `nombre_articles` · `magasin` · `taille_tshirt (S/M/L/XL)` · `code_postal` · `note_satisfaction (1 à 5)`.

<details>
<summary>▶ Corrigé</summary>

- `montant_panier` → **quantitatif continu** (montant avec décimales)
- `nombre_articles` → **quantitatif discret** (comptage entier)
- `magasin` → **qualitatif nominal** (catégories sans ordre)
- `taille_tshirt` → **qualitatif ordinal** (S < M < L < XL)
- `code_postal` → **qualitatif nominal** (faux nombre, pas de moyenne possible)
- `note_satisfaction` → **qualitatif ordinal** (ordre oui, mais écarts non garantis égaux)

</details>

### Exercice 2 — Moyenne vs médiane

Salaires nets mensuels (€) d'une petite équipe : `1 800 ; 1 900 ; 2 000 ; 2 100 ; 2 200 ; 9 500` (le dernier = le gérant).
1. Calcule la moyenne et la médiane.
2. Laquelle représente le mieux « le salaire typique » de l'équipe ? Justifie.

<details>
<summary>▶ Corrigé</summary>

1. **Moyenne** = `(1800+1900+2000+2100+2200+9500)/6 = 19 500/6 = 3 250 €`.
   **Médiane** (n=6, pair) = moyenne des 2 centrales `(2000+2100)/2 = 2 050 €`.
2. La **médiane (2 050 €)** est bien plus représentative. La moyenne (3 250 €) est **tirée vers le haut** par le salaire du gérant (9 500 €) : aucun employé ne gagne 3 250 €. C'est exactement pourquoi l'INSEE communique en **salaire médian**.

</details>

### Exercice 3 — Variance et écart-type à la main

Ventes journalières (k€) d'une boutique sur 5 jours : `12 ; 15 ; 14 ; 13 ; 16`.
Calcule la moyenne, la variance (population, ÷n) et l'écart-type. Conclus sur la régularité.

<details>
<summary>▶ Corrigé</summary>

- Moyenne = `(12+15+14+13+16)/5 = 70/5 = 14 k€`.
- Écarts au carré : `(12−14)²=4 ; (15−14)²=1 ; (14−14)²=0 ; (13−14)²=1 ; (16−14)²=4`. Somme = `10`.
- Variance = `10/5 = 2`. Écart-type = `√2 ≈ 1,41 k€`.
- **Conclusion** : les ventes s'écartent en moyenne de seulement 1,41 k€ d'une moyenne de 14 k€ → **boutique très régulière** (CV ≈ 10 %).

</details>

### Exercice 4 — Quartiles et IQR

Série triée de durées de visite (min) : `2 ; 3 ; 4 ; 5 ; 6 ; 7 ; 8 ; 9 ; 30`.
Calcule Q1, médiane, Q3, IQR, puis applique la règle 1,5×IQR. Y a-t-il un outlier ?

<details>
<summary>▶ Corrigé</summary>

- `n = 9`. Médiane = 5ᵉ valeur = **6**.
- Moitié basse `2;3;4;5` → Q1 = `(3+4)/2 = 3,5`.
- Moitié haute `7;8;9;30` → Q3 = `(8+9)/2 = 8,5`.
- IQR = `8,5 − 3,5 = 5`.
- Borne haute = `8,5 + 1,5×5 = 8,5 + 7,5 = 16`. La valeur **30 > 16** → **outlier** détecté (visite anormalement longue : robot ? onglet oublié ouvert ?).

</details>

### Exercice 5 — Z-score

Une série de paniers a une moyenne de 50 € et un écart-type de 12 €. Un client a dépensé 92 €.
Calcule son z-score. Est-ce un outlier au seuil |z| > 3 ?

<details>
<summary>▶ Corrigé</summary>

`z = (92 − 50)/12 = 42/12 = 3,5`. Comme `|3,5| > 3`, ce panier est **un outlier** au sens du z-score : il se situe à 3,5 écarts-types de la moyenne, à investiguer.

</details>

### Exercice 6 — Asymétrie

Sur un jeu de paniers, tu obtiens : moyenne = 78 €, médiane = 52 €.
1. La distribution est-elle symétrique ? Sinon, dans quel sens ?
2. Quelle mesure communiquer au directeur ?

<details>
<summary>▶ Corrigé</summary>

1. **Moyenne (78) > médiane (52)** → **asymétrie à droite (positive)** : une queue de gros paniers tire la moyenne vers le haut. Typique du retail.
2. Communiquer la **médiane (52 €)** comme « panier typique », et **mentionner** la moyenne en précisant qu'elle est gonflée par quelques très gros achats.

</details>

### Exercice 7 — Python : EDA express ⚙️

Avec ce DataFrame, calcule en Python : `describe()`, l'écart-type, le CV, et trouve les outliers par la règle IQR.

```python
import pandas as pd
ventes = pd.DataFrame({
    "client": range(1, 13),
    "panier": [22, 35, 28, 41, 39, 33, 45, 30, 38, 36, 250, 31]
})
```

<details>
<summary>▶ Corrigé</summary>

```python
print(ventes["panier"].describe())

cv = ventes["panier"].std(ddof=0) / ventes["panier"].mean() * 100
print(f"CV = {cv:.1f}%")

q1, q3 = ventes["panier"].quantile([0.25, 0.75])
iqr = q3 - q1
bh = q3 + 1.5 * iqr
bb = q1 - 1.5 * iqr
print(f"Bornes : [{bb:.1f} ; {bh:.1f}]")
print(ventes[(ventes["panier"] < bb) | (ventes["panier"] > bh)])
# -> le client 11 (panier 250 €) ressort comme outlier
```

Le panier de **250 €** dépasse largement la borne haute → outlier. La médiane (~35 €) reste fiable, la moyenne (~52 €) est gonflée par cette valeur.

</details>

### Exercice 8 — Python : boxplot comparatif ⚙️

Trace un boxplot des paniers **par magasin** et interprète en une phrase métier.

```python
import pandas as pd, numpy as np
np.random.seed(0)
df = pd.DataFrame({
    "magasin": np.repeat(["Lille", "Roubaix", "Dunkerque"], 100),
    "panier": np.concatenate([
        np.random.normal(50, 8, 100),
        np.random.normal(42, 20, 100),
        np.random.normal(48, 5, 100),
    ])
})
```

<details>
<summary>▶ Corrigé</summary>

```python
import seaborn as sns, matplotlib.pyplot as plt
sns.boxplot(data=df, x="magasin", y="panier")
plt.title("Paniers par magasin")
plt.show()

df.groupby("magasin")["panier"].agg(["median", "std"])
```

Interprétation type : « Dunkerque a la **boîte la plus courte** (écart-type ≈ 5) → ventes les plus **régulières** ; Roubaix a une **boîte très large** (écart-type ≈ 20) → clientèle **hétérogène**, paniers imprévisibles, à analyser de plus près. »

</details>

---

## Quiz (6 QCM)

**Q1.** Un fichier contient une colonne `niveau_satisfaction` avec les valeurs « Faible / Moyen / Élevé ». De quel type est-elle ?
- A) Quantitative continue — B) Quantitative discrète — C) Qualitative nominale — D) Qualitative ordinale

**Q2.** Une série de salaires a une moyenne de 3 200 € et une médiane de 2 100 €. Que peut-on dire ?
- A) Erreur de calcul — B) Distribution symétrique — C) Asymétrie à droite, présence de hauts salaires — D) Tous gagnent pareil

**Q3.** L'écart-type d'une série de ventes journalières vaut 0,8 k€ pour une moyenne de 40 k€. Cela signifie :
- A) Les ventes sont très irrégulières — B) Les ventes sont très régulières — C) Il y a beaucoup d'outliers — D) La médiane vaut 0,8

**Q4.** Pour Q1 = 30, Q3 = 70, la borne haute de la règle 1,5×IQR vaut :
- A) 100 — B) 110 — C) 130 — D) 90

**Q5.** Dans un boxplot, le trait à l'intérieur de la boîte représente :
- A) La moyenne — B) Le mode — C) La médiane (Q2) — D) L'écart-type

**Q6.** Tu veux comparer la régularité des ventes d'un hypermarché (50 k€/j) et d'une supérette (3 k€/j). Quel indicateur utiliser ?
- A) L'étendue — B) L'écart-type brut — C) Le coefficient de variation — D) La moyenne

<details>
<summary>▶ Réponses</summary>

**Q1 : D** (catégories avec un ordre logique → ordinale).
**Q2 : C** (moyenne > médiane → asymétrie positive, des hauts salaires tirent la moyenne).
**Q3 : B** (écart-type minuscule devant la moyenne, CV = 0,8/40 = 2 % → très régulier).
**Q4 : C** (IQR = 70−30 = 40 ; borne haute = 70 + 1,5×40 = 70+60 = **130**).
**Q5 : C** (la médiane ; la moyenne n'apparaît pas sur un boxplot standard).
**Q6 : C** (le CV, car il neutralise la différence d'échelle entre les deux commerces).

</details>

---

## À retenir — carte mémo des formules

> 🃏 **À photographier et garder sous les yeux pendant les exercices Python.**
>
> ✅ = Noyau essentiel (à maîtriser absolument) · 🚀 = pour aller plus loin (optionnel au premier passage).

| Notion | Formule | Réflexe métier |
|---|---|---|
| ✅ **Moyenne** | $\bar{x} = \dfrac{1}{n}\sum x_i$ | Sensible aux extrêmes. Bonne pour les totaux (CA = moyenne × n) |
| ✅ **Médiane** | valeur centrale de la série triée | **Robuste** → salaires, paniers, prix, durées · *« le client du milieu de la file »* |
| ✅ **Mode** | valeur la plus fréquente | Seule mesure pour le **qualitatif** |
| ✅ **Étendue** | $\max - \min$ | Indice rapide, très sensible |
| ✅ **Variance** | $\sigma^2 = \dfrac{1}{n}\sum(x_i-\bar{x})^2$ | Pour les calculs (unité au carré) |
| ✅ **Écart-type** | $\sigma = \sqrt{\sigma^2}$ | **Régularité** (même unité). On communique avec ça |
| 🚀 **Coef. de variation** | $CV = \dfrac{\sigma}{\bar{x}}\times 100$ | Comparer des **échelles différentes** |
| ✅ **IQR** | $Q_3 - Q_1$ | Cœur des 50 % centraux, **robuste** |
| ✅ **Outlier IQR** | hors de $[Q_1 - 1{,}5\,IQR \;;\; Q_3 + 1{,}5\,IQR]$ | Détection standard (boxplot) |
| ✅ **Z-score** | $z = \dfrac{x - \bar{x}}{\sigma}$ | Outlier si $\lvert z\rvert > 3$ (données ≈ symétriques) |
| 🚀 **Covariance** | $\dfrac{1}{n}\sum(x_i-\bar{x})(y_i-\bar{y})$ | **Signe** du lien (force → corrélation, chap. 5) |

**Les 3 réflexes du Data Analyst à la découverte d'un fichier :**

1. **`df.info()` + `df.dtypes`** → quels types de variables ?
2. **`df.describe()`** → tendance centrale + dispersion + quantiles d'un coup. **Compare toujours moyenne et médiane.**
3. **Histogramme + boxplot** → forme, asymétrie, outliers → décision de nettoyage.

> 🚀 **Prochaine étape :** au **chapitre 4** tu verras les probabilités et la loi normale, et au **chapitre 5** la **corrélation** (la force du lien entre deux variables, dont on a posé la première pierre ici avec la covariance).
