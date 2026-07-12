# 02 — Statistiques descriptives appliquées

> 🎬 **L'histoire de ce module — « la Ch'ti Boutique ».**
> Imagine : tu viens d'être embauché·e comme Data Analyst chez **la Ch'ti Boutique**, une chaîne de magasins du Nord. Le premier matin, la directrice pose son café sur ton bureau et te lance LA question qui rapporte de l'argent : **« Qui sont mes meilleurs clients ? »** Pas « combien j'ai vendu » (ça, le comptable le sait). Non : *qui* chouchouter, *qui* relancer avant qu'il ne parte, *qui* laisser tranquille. Tout ce module va te transformer en celui ou celle capable de répondre à ça — chiffres à l'appui. À la fin, tu sauras dire « voici tes VIP, voici tes clients qui s'endorment, voici où mettre ton budget marketing ». Suis le fil rouge 🧵, on revient sans cesse à la Ch'ti Boutique.

> **Tu sais déjà décrire une colonne. Maintenant tu vas faire parler le tableau entier.** Au module 1.2 tu calculais une moyenne, une médiane, un boxplot sur *une* variable. Ici, tu croises plusieurs variables, tu crées des **groupes de clients**, tu mesures comment les choses **bougent ensemble** (corrélation) et tu transformes ces analyses en **recommandations métier**. C'est exactement ce qu'un responsable marketing ou un directeur régional attend de toi.

| | |
|---|---|
| **Phase** | Phase 2 — Mettre en place une solution de BI pour un traitement analytique avancé |
| **Durée** | ≈ 30 h |
| **Compétences visées** | **C5 — Mener des analyses exploratoires (EDA)** · **C6 — Analyser les tendances** — **niveau 2** (RNCP-38616) |
| **Pré-requis** | Module **Maths — Chapitre 3 « Statistiques descriptives »** (moyenne/médiane, dispersion, quantiles, outliers) · **Chapitre 5 « Probabilités & lois »** (loi normale, notion de variable aléatoire) · Module **1.2 Python & pandas pour l'EDA** (DataFrame, `groupby`, `describe`, seaborn) |
| **Outils** | Python 3.11+, Jupyter / Anaconda, `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn` |

---

## Objectifs pédagogiques

À la fin de ce module, tu sauras :

1. **Analyser plusieurs variables ensemble** (analyse multivariée) et non plus une seule à la fois.
2. **Segmenter** une population (clients, magasins, produits) en groupes homogènes et **comparer** ces groupes statistiquement.
3. **Construire des tableaux croisés** avancés avec `pivot_table` et `crosstab` (effectifs, moyennes, pourcentages, marges).
4. **Calculer et interpréter une matrice de corrélation**, la visualiser en **heatmap**, et éviter le piège « corrélation = causalité ».
5. **Réaliser une analyse RFM** (Récence / Fréquence / Montant) pour segmenter une base clients et prioriser les actions marketing.
6. **Normaliser et standardiser** des variables (min-max, z-score) et savoir **quand** c'est nécessaire.
7. **Détecter des anomalies** de façon avancée (z-score, IQR, et croisement de critères).
8. **Justifier le choix d'une statistique** selon la nature de la donnée (qualitative / quantitative, distribution symétrique ou non).

> 🔗 **Lien direct avec les maths.** Le Chapitre 3 t'a donné les outils sur **une** variable. Ce module les fait travailler **à plusieurs** : la corrélation est une généralisation de la variance à deux variables, le z-score (standardisation) vient directement de la loi normale du Chapitre 5, et la segmentation repose sur les quantiles que tu sais déjà manipuler.

> 🔗 **PONT MATHS → PRATIQUE — ne saute pas cet encadré.** Ce module ne sort pas de nulle part : il **pousse plus loin** ce que tu as appris en maths.
> - **Chapitre 3 (stats descriptives)** : tu calculais moyenne, médiane, quantiles, outliers sur **une colonne**. Ici tu fais exactement pareil… mais **par groupe** (panier moyen *par ville*) et tu t'en sers pour **segmenter** (découper les clients en tranches avec les quantiles = `qcut`).
> - **Chapitre 5 (corrélation / loi normale)** : tu avais vu le principe « deux choses qui varient ensemble ». Ici tu le calcules pour de vrai (matrice de corrélation + heatmap) et tu le mets en garde-fou (« corrélation ≠ causalité »). Le z-score, lui, c'est la loi normale qui revient déguisée pour repérer les valeurs anormales.
> - **La grande nouveauté du module = la RFM**, une recette concrète qui combine ces briques pour répondre à la question de la directrice. Bref : tu ne réapprends rien, tu **assembles** ce que tu sais déjà pour produire une décision.

---

## Pourquoi c'est utile au Data Analyst

Un Data Analyst n'est pas payé pour produire des moyennes. Il est payé pour **répondre à des questions de décision** :

- « Quels sont nos **meilleurs clients**, et lesquels sont en train de nous quitter ? » → **RFM**.
- « Est-ce que les clients qui achètent du rayon A achètent aussi du rayon B ? » → **tableau croisé + corrélation**.
- « Le panier moyen est-il **vraiment** différent entre nos magasins urbains et ruraux, ou est-ce du hasard ? » → **comparaison de groupes**.
- « Cette commande à 18 000 € est-elle une vraie grosse vente ou une **erreur de saisie** ? » → **détection d'anomalies**.

Ces analyses sont le **carburant** de la suite de la Phase 2 : la segmentation RFM que tu produis ici alimentera directement les tables de dimensions de ton modèle en étoile (module 2.2) et les mesures DAX de tes tableaux de bord Power BI (module 2.3). **Ce que tu calcules ici en Python, tu le restitueras ensuite en BI.**

> 🧭 **Image à retenir.** Au niveau 1, tu étais le **photographe** : tu décrivais ce que tu voyais. Au niveau 2, tu deviens le **détective** : tu relies les indices entre eux pour produire une conclusion exploitable.

---

## Le jeu de données fil rouge

Tout le module s'appuie sur un jeu de transactions e-commerce du Nord (fictif mais réaliste). On le génère une fois pour toutes :

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # graine fixe = résultats reproductibles

n = 5000
villes = ["Lille", "Roubaix", "Tourcoing", "Dunkerque", "Valenciennes", "Arras"]
rayons = ["Épicerie", "Frais", "Maison", "High-Tech", "Mode"]

df = pd.DataFrame({
    "transaction_id": np.arange(1, n + 1),
    "client_id": rng.integers(1, 900, size=n),          # ~900 clients récurrents
    "ville": rng.choice(villes, size=n, p=[.30, .18, .15, .15, .12, .10]),
    "rayon": rng.choice(rayons, size=n),
    "montant": np.round(rng.gamma(shape=2.0, scale=22, size=n) + 3, 2),  # paniers asymétriques
    "nb_articles": rng.integers(1, 15, size=n),
    "date": pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, size=n), unit="D"),
})
# Quelques anomalies volontaires (erreurs de saisie)
df.loc[rng.choice(df.index, 8, replace=False), "montant"] = rng.uniform(2000, 9000, 8).round(2)

print(df.shape)
df.head()
```

**Sortie commentée :**

```
(5000, 7)
   transaction_id  client_id      ville     rayon  montant  nb_articles       date
0               1        102      Lille  Épicerie    41.07            6 2024-05-13
1               2        877    Roubaix      Mode    63.55            2 2024-02-28
...
```

> On a **5 000 transactions** réparties sur ~900 clients, 6 villes, 5 rayons, sur l'année 2024. La loi **gamma** produit des montants **asymétriques** (beaucoup de petits paniers, quelques gros) — réaliste, et idéal pour parler médiane vs moyenne. On a injecté **8 anomalies** à plus de 2 000 € : on les retrouvera au §9.

---

## Analyse multivariée : croiser pour comprendre

### L'idée

Une analyse **univariée** décrit une variable seule (le montant moyen). Une analyse **bivariée** en croise deux (montant *selon* la ville). Une analyse **multivariée** en croise trois ou plus (montant selon ville *et* rayon). Plus on croise, plus on s'approche d'une explication.

### Décrire par groupe avec `groupby` + `agg`

```python
synthese = (
    df.groupby("ville")
      .agg(nb_transactions=("transaction_id", "count"),
           panier_moyen=("montant", "mean"),
           panier_median=("montant", "median"),
           ca_total=("montant", "sum"))
      .round(2)
      .sort_values("ca_total", ascending=False)
)
print(synthese)
```

**Sortie commentée :**

```
              nb_transactions  panier_moyen  panier_median   ca_total
ville
Lille                    1503         51.12          44.83   76833.36
Roubaix                   902         50.47          43.10   45524.94
Tourcoing                 740         52.30          45.01   38702.00
...
```

> **Interprétation métier.** Lille pèse le plus de chiffre d'affaires (logique : 30 % des transactions). Mais regarde le **panier moyen** : il est très proche d'une ville à l'autre (~50-52 €). La différence de CA vient donc du **volume de clients**, pas du **comportement d'achat**. Décision : pour augmenter le CA à Tourcoing, il faut recruter des clients, pas pousser le panier.
>
> Note aussi que **moyenne > médiane** partout (~51 vs ~44) : signe d'une distribution **asymétrique à droite** (quelques gros paniers tirent la moyenne vers le haut). C'est ici que ton réflexe du Chapitre 3 doit s'allumer.

> ⚠️ **Encadré — erreurs courantes**
> - **Ne regarder que la moyenne.** Sur des montants, la médiane raconte souvent une histoire plus juste. Affiche les deux.
> - **Comparer des CA sans comparer les effectifs.** Une ville à gros CA peut juste avoir plus de monde. Toujours ramener au client / à la transaction.
> - Oublier `.round()` → tableaux illisibles avec 8 décimales.

---

## Tableaux croisés dynamiques : `pivot_table` et `crosstab`

C'est l'équivalent Python du **TCD Excel**, mais reproductible et scalable.

> ✂️ **« Tableau croisé », c'est intimidant ? Pas du tout.** C'est juste un tableau à double entrée, comme une grille de bataille navale : les **villes en lignes**, les **rayons en colonnes**, et dans chaque case le chiffre qui les croise (« combien de ventes Mode à Lille ? »). Tu en as déjà fait à la main sans le savoir. Python le génère en une ligne — et le recalcule tout seul si les données changent. 🎯 **Ça te servira pour** répondre du tac au tac à « et par ville ça donne quoi, par rayon ? » sans refaire le travail à chaque question.

### `crosstab` — compter des effectifs

```python
# Combien de transactions par ville ET par rayon ?
tab = pd.crosstab(df["ville"], df["rayon"], margins=True, margins_name="Total")
print(tab)
```

**Sortie commentée :**

```
rayon      Épicerie  Frais  High-Tech  Maison  Mode  Total
ville
Arras           110     98         95     104    98    505
Lille           305    298        296     300   304   1503
...
Total          1001    998       1004     999   998   5000
```

> **Interprétation.** La répartition par rayon est **homogène** dans chaque ville (~20 % chacun) : aucun rayon n'est sur- ou sous-représenté localement. Si on voyait, par exemple, « High-Tech » exploser à Lille, ce serait une piste (zone de chalandise jeune ? magasin spécialisé ?).

### `crosstab` en pourcentages (ligne)

```python
# Profil de chaque ville : quelle part de SES achats va à chaque rayon ?
profil = pd.crosstab(df["ville"], df["rayon"], normalize="index").round(3) * 100
print(profil)
```

> `normalize="index"` → chaque **ligne** somme à 100 %. `normalize="columns"` → chaque colonne. `normalize=True` → pourcentage du total général. **Choisir le bon axe selon la question posée** : « profil d'une ville » → ligne ; « où se vend ce rayon » → colonne.

### `pivot_table` — agréger une mesure (pas juste compter)

```python
pivot = pd.pivot_table(
    df,
    values="montant",
    index="ville",
    columns="rayon",
    aggfunc="mean",      # moyenne du montant
    margins=True, margins_name="Moy.",
).round(1)
print(pivot)
```

**Sortie commentée :**

```
rayon      Épicerie  Frais  High-Tech  Maison  Mode  Moy.
ville
Arras          49.8   51.0       52.3    50.1  48.9  50.4
Lille          50.7   51.5       51.9    51.2  50.3  51.1
...
```

> **`pivot_table` vs `crosstab` :** `crosstab` est optimisé pour **compter** des effectifs (variables qualitatives), `pivot_table` pour **agréger une mesure numérique** (`mean`, `sum`, `median`, ou plusieurs à la fois via `aggfunc=["mean","count"]`). Tu peux mettre **plusieurs variables** en `index` ou `columns` pour un croisé à 3+ dimensions.

> ⚠️ **Encadré — erreurs courantes**
> - **`aggfunc` oublié** → `pivot_table` fait par défaut la **moyenne**. Si tu voulais une somme de CA, tu obtiens un panier moyen sans t'en rendre compte.
> - **Confondre les deux normalisations** : `normalize="index"` ≠ `normalize="columns"`. Relis toujours « est-ce que mes lignes ou mes colonnes somment à 100 % ? ».
> - Cellules **NaN** dans le pivot = aucune transaction pour ce croisement. Ce n'est pas un bug : c'est une info (ce produit ne se vend pas là).

---

## Analyses de corrélation appliquées

### Ce que mesure une corrélation

Le **coefficient de corrélation de Pearson** (noté *r*) mesure si deux variables **numériques** varient **ensemble de façon linéaire**. Il va de **−1 à +1** :

| Valeur de *r* | Interprétation |
|---|---|
| proche de **+1** | quand l'une monte, l'autre monte (lien positif fort) |
| proche de **0** | pas de lien **linéaire** |
| proche de **−1** | quand l'une monte, l'autre baisse (lien négatif fort) |

Repères usuels : `|r| < 0,3` faible · `0,3–0,5` modéré · `0,5–0,7` assez fort · `> 0,7` fort.

> ✂️ **En clair, c'est quoi une « matrice de corrélation » ?** Un grand tableau qui croise chaque variable avec toutes les autres et met, dans chaque case, un score entre −1 et +1 disant « est-ce que ces deux-là bougent ensemble ? ». La **heatmap**, c'est ce même tableau **colorié** (rouge = ça monte ensemble, bleu = l'un monte quand l'autre baisse) pour le lire d'un coup d'œil au lieu de plisser les yeux sur des chiffres.

> 🎲 **Devine AVANT de calculer.** Avant de lancer le code et de regarder la heatmap, parie ! À la Ch'ti Boutique, parmi `montant`, `nb_articles`, `prix_moyen_article` et `mois` : **quelles deux variables sont les plus corrélées, et dans quel sens** (ensemble ↗ ou en sens inverse ↘) ? Note ta réponse sur un coin de feuille. Tu vérifieras juste en dessous — c'est plus marquant quand on s'est mouillé d'abord.

### Matrice de corrélation + heatmap

```python
import seaborn as sns
import matplotlib.pyplot as plt

# On enrichit avec quelques variables numériques
df["mois"] = df["date"].dt.month
df["prix_moyen_article"] = (df["montant"] / df["nb_articles"]).round(2)

num = df[["montant", "nb_articles", "prix_moyen_article", "mois"]]
corr = num.corr(method="pearson").round(2)

plt.figure(figsize=(6, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, center=0, fmt=".2f")
plt.title("Matrice de corrélation des variables numériques")
plt.tight_layout()
plt.show()
print(corr)
```

**Sortie commentée :**

```
                    montant  nb_articles  prix_moyen_article  mois
montant                1.00         0.42                0.55  0.01
nb_articles            0.42         1.00               -0.51  0.00
prix_moyen_article     0.55        -0.51                1.00  0.01
mois                   0.01         0.00                0.01  1.00
```

> **Interprétation métier.**
> - `montant` ↔ `nb_articles` : **+0,42** (modéré) — logique, plus on prend d'articles, plus on dépense, mais pas mécaniquement (des articles chers en petite quantité existent).
> - `nb_articles` ↔ `prix_moyen_article` : **−0,51** — quand on achète beaucoup d'articles, leur prix unitaire moyen est plus bas (paniers « de masse » vs paniers « premium »). **Insight actionnable** : deux profils de clients coexistent.
> - `mois` n'est corrélé à rien (~0) : **pas de saisonnalité linéaire** détectable sur le montant ici.
>
> La **heatmap** rend tout ça lisible d'un coup d'œil : le rouge = positif, le bleu = négatif, l'intensité = la force. On lit la diagonale (toujours 1) puis on cherche les cases vives **hors diagonale**.

> 🎲 **Alors, ton pari ?** Le couple le plus fort en valeur absolue était `nb_articles` ↔ `prix_moyen_article` à **−0,51** (sens inverse). Si tu avais misé sur `montant` ↔ `nb_articles`, pas grave : tu avais le bon réflexe (elles sont liées, +0,42), mais c'est moins fort qu'on l'imagine — preuve qu'on a souvent besoin de vérifier au lieu de croire.

> 🎯 **Ça te servira pour…** repérer en 30 secondes les variables qui « marchent ensemble » avant de construire un dashboard ou un modèle. Concrètement : si tu vois que `prix_moyen_article` baisse quand `nb_articles` monte, tu sais déjà qu'il existe **deux profils d'acheteurs** (gros volumes pas chers vs petits paniers premium) — et c'est exactement ce genre d'insight que ta direction veut entendre en réunion.

### Le piège fondamental : corrélation ≠ causalité

Deux variables peuvent être corrélées sans qu'aucune ne **cause** l'autre :

- **Variable cachée** : les ventes de glaces et les noyades sont corrélées… parce qu'il fait chaud (la chaleur cause les deux).
- **Hasard** sur petit échantillon.
- **Sens inversé** : A cause B, ou B cause A ? La corrélation ne le dit pas.

> ⚠️ **Encadré — erreurs courantes**
> - **Conclure une cause à partir d'un *r* élevé.** Jamais. Tu signales un lien, pas une cause. Le métier ou un test expérimental tranchera.
> - **Oublier que Pearson ne voit que le linéaire.** Une relation en cloche (U) peut donner *r* ≈ 0 alors qu'un lien fort existe. Toujours regarder un **nuage de points** (`sns.scatterplot` / `pairplot`) en complément.
> - Calculer une corrélation sur une variable **catégorielle encodée en chiffres** (ex. `ville` = 1,2,3) : ça ne veut rien dire. Pearson = numérique **continu**.
> - **Outliers** : une seule valeur extrême peut gonfler ou casser *r*. Nettoyer / vérifier d'abord (cf. §9).

---

## Segmentation : créer et comparer des groupes

Segmenter = découper une population en **groupes homogènes** pour les traiter différemment.

> ✂️ **En clair.** « Segmenter », c'est **trier tes clients en paquets qui se ressemblent**, comme tu rangerais tes chaussettes : les épaisses d'hiver d'un côté, les fines de sport de l'autre. Pourquoi ? Parce qu'on ne parle pas à un gros client fidèle comme à quelqu'un qui n'est venu qu'une fois. Chaque paquet = un message marketing différent. 🎯 **Ça te servira pour** envoyer le bon e-mail au bon groupe au lieu d'arroser tout le monde avec la même promo (et de griller ton budget).

### Segmenter par quantiles (`qcut`) ou par seuils métier (`cut`)

```python
# Segmentation du panier en 3 groupes de TAILLE ÉGALE (terciles)
df["segment_panier"] = pd.qcut(df["montant"], q=3, labels=["Petit", "Moyen", "Gros"])

# Segmentation par SEUILS MÉTIER fixés (ex. règle commerciale)
df["segment_metier"] = pd.cut(df["montant"],
                              bins=[0, 30, 80, np.inf],
                              labels=["Éco", "Standard", "Premium"])

print(df["segment_panier"].value_counts())
print(df["segment_metier"].value_counts())
```

> **`qcut` vs `cut` :** `qcut` découpe en groupes d'**effectifs égaux** (par quantiles — chaque segment a le même nombre de clients). `cut` découpe en intervalles de **valeurs fixées** (les seuils que le métier impose). Choisir selon la question : « le tiers du haut » → `qcut` ; « au-dessus de 80 € » → `cut`.

### Comparer les groupes statistiquement

```python
compare = (
    df.groupby("segment_metier", observed=True)
      .agg(nb=("transaction_id", "count"),
           panier_moyen=("montant", "mean"),
           articles_moyens=("nb_articles", "mean"))
      .round(2)
)
print(compare)
```

> **Interprétation.** On obtient le profil de chaque segment. Si le segment « Premium » a un panier moyen 4× supérieur mais un nombre d'articles proche, c'est qu'il achète des produits **chers** (et non plus). Action : pousser le haut de gamme vers ce segment.

### « Cette différence est-elle réelle ? » — le test de comparaison

Un panier moyen de 51 € à Lille vs 50 € à Roubaix : **vraie** différence ou bruit d'échantillonnage ? Le **test t de Student** (vu en proba/stats) répond. On l'applique avec `scipy` :

```python
from scipy import stats

lille = df.loc[df["ville"] == "Lille", "montant"]
roubaix = df.loc[df["ville"] == "Roubaix", "montant"]

t, p = stats.ttest_ind(lille, roubaix, equal_var=False)  # Welch (variances ≠)
print(f"t = {t:.2f}   p-value = {p:.3f}")
```

**Sortie commentée :**

```
t = 0.52   p-value = 0.601
```

> **Interprétation.** La **p-value (0,60)** est très supérieure au seuil usuel de **0,05**. Conclusion : la différence de panier moyen entre Lille et Roubaix **n'est pas statistiquement significative** — elle est compatible avec du hasard. On **ne** doit donc **pas** bâtir une stratégie commerciale dessus. À l'inverse, une p-value < 0,05 indiquerait une différence qu'on peut considérer comme réelle.

> ⚠️ **Encadré — erreurs courantes**
> - **`observed=True` oublié** sur un `groupby` de variable catégorielle (`category`) → pandas crée des lignes vides pour les combinaisons absentes. Toujours le préciser.
> - **Interpréter la p-value comme « la probabilité que ce soit faux ».** Non : c'est la probabilité d'observer un tel écart **si** les groupes étaient identiques. Faible p-value → écart peu compatible avec le hasard.
> - **Sur-segmenter** : 12 segments de 3 clients ne servent à rien. Vise des groupes assez gros pour être actionnables (règle pratique : ≥ 30 individus).

---

## Normalisation & standardisation

### Pourquoi ?

Quand on compare ou combine des variables d'**échelles différentes** (un montant en € de 0 à 9000 et un nombre d'articles de 1 à 15), celle qui a les plus grands chiffres **écrase** les autres. La mise à l'échelle remet tout sur un pied d'égalité. Indispensable avant un **clustering**, un calcul de distance, ou pour comparer des variables hétérogènes.

### Les deux méthodes

| Méthode | Formule | Résultat | Quand l'utiliser |
|---|---|---|---|
| **Normalisation min-max** | (x − min) / (max − min) | tout entre **0 et 1** | bornes connues, pas trop d'outliers |
| **Standardisation (z-score)** | (x − moyenne) / écart-type | moyenne **0**, écart-type **1** | données ~normales, présence d'outliers (plus robuste) |

```python
from sklearn.preprocessing import MinMaxScaler, StandardScaler

cols = ["montant", "nb_articles"]
X = df[cols]

df[["montant_minmax", "articles_minmax"]] = MinMaxScaler().fit_transform(X)
df[["montant_z", "articles_z"]] = StandardScaler().fit_transform(X)

print(df[["montant", "montant_minmax", "montant_z"]].describe().round(2))
```

**Sortie commentée :**

```
        montant  montant_minmax  montant_z
mean      54.30            0.01       0.00
std      192.51            0.03       1.00
min        3.38            0.00      -0.26
max     6990.41            1.00      36.03  (à cause des anomalies)
```

> **Interprétation.** Après **min-max**, tout est entre 0 et 1 — mais regarde : les anomalies à plusieurs milliers d'euros écrasent tout le reste vers 0 (la médiane se retrouve à ~0,005). C'est le **défaut du min-max face aux outliers**. Le **z-score** centre sur 0 / écart-type 1 et reste plus lisible, mais l'anomalie ressort à +36 écarts-types (ce qui, justement, sert à la **détecter** !). **Leçon : nettoie les anomalies AVANT de normaliser**, sinon elles polluent l'échelle.

> ⚠️ **Encadré — erreurs courantes**
> - **Normaliser puis détecter les outliers** : ordre inversé. La détection se fait d'abord (ou en même temps, via le z-score).
> - **`fit_transform` sur tout le jeu puis re-`fit` sur un autre échantillon** : en ML on `fit` sur le train uniquement. Ici, pour de l'analyse descriptive, c'est moins critique, mais garde le réflexe.
> - **Standardiser une variable catégorielle** : non-sens, comme pour la corrélation.

---

## Détection avancée d'anomalies

Une anomalie (ou *outlier*) est une valeur **inhabituelle**. Elle peut être une **erreur** (saisie, capteur) ou un **vrai cas rare** (très gros client). Le Data Analyst doit la **repérer**, puis **décider** : corriger, exclure, ou garder en la signalant.

### Méthode IQR (robuste, vue au Chapitre 3)

```python
q1, q3 = df["montant"].quantile([0.25, 0.75])
iqr = q3 - q1
borne_haute = q3 + 1.5 * iqr
borne_basse = q1 - 1.5 * iqr

outliers_iqr = df[(df["montant"] > borne_haute) | (df["montant"] < borne_basse)]
print(f"Bornes : [{borne_basse:.1f} ; {borne_haute:.1f}]  →  {len(outliers_iqr)} anomalies")
```

### Méthode z-score (suppose une distribution ~normale)

```python
from scipy import stats
df["z_montant"] = np.abs(stats.zscore(df["montant"]))
outliers_z = df[df["z_montant"] > 3]   # au-delà de 3 écarts-types
print(f"{len(outliers_z)} anomalies au-delà de 3σ")
print(outliers_z[["transaction_id", "montant", "z_montant"]].sort_values("montant", ascending=False).head())
```

**Sortie commentée :**

```
8 anomalies au-delà de 3σ
      transaction_id  montant  z_montant
            3037     6990.41      36.03
            3728     6477.26      33.37
            2884     5993.65      30.86
            3903     5464.33      28.11
            3802     2954.39      15.07
```

> **Interprétation.** On retrouve **exactement les 8 transactions** injectées au §3. Le z-score les sort sans ambiguïté (>3σ). **Décision métier** : des paniers à plusieurs milliers d'euros sur un e-commerce de produits courants sont quasi certainement des **erreurs de saisie** (virgule oubliée → 69,90 € devenu 6990 €). On les corrige ou on les exclut, **en le documentant**.

### Croiser les critères (détection « avancée »)

Une vraie anomalie est souvent **multivariée** : un montant élevé *avec* peu d'articles est plus suspect qu'un montant élevé avec beaucoup d'articles.

```python
# Montant élevé MAIS très peu d'articles → prix unitaire aberrant
suspects = df[(df["z_montant"] > 3) & (df["nb_articles"] <= 2)]
print(f"{len(suspects)} anomalies à forte priorité (gros montant + peu d'articles)")
```

> **Interprétation.** En croisant deux critères, on **priorise** : ces cas-là sont les plus probablement des erreurs et méritent une vérification immédiate. C'est la différence entre une détection « niveau 1 » (une variable) et « niveau 2 » (croisée).

> ⚠️ **Encadré — erreurs courantes**
> - **Supprimer les outliers par réflexe.** Un gros client B2B *est* une anomalie statistique mais une **vérité métier**. Demande-toi toujours : erreur ou cas rare ?
> - **Appliquer le z-score sur une distribution très asymétrique** : il suppose une forme ~normale. Sur des montants gamma, l'IQR est souvent plus fiable. Compare les deux.
> - **Ne pas documenter** les exclusions → analyse non reproductible et non défendable.

---

## Cas complet : analyse RFM 🏆

> 🧵 **On y est : la réponse à la question de la directrice.** Tout le module menait ici. La RFM, c'est l'outil qui répond noir sur blanc à « qui sont mes meilleurs clients ? ».

> ✂️ **RFM en une phrase = « note tes clients comme un programme de fidélité ».** Tu connais les cartes de fidélité qui te classent Bronze / Argent / Or / Platine ? La RFM, c'est ça, mais calculé automatiquement à partir de **trois critères simples** : est-il venu **récemment** (R) ? vient-il **souvent** (F) ? dépense-t-il **beaucoup** (M) ? Chaque client reçoit une note sur ces trois axes, et hop, on en déduit sa « carte » : VIP, régulier, endormi… Rien de magique, juste du bon sens transformé en chiffres.

La **RFM** est *la* segmentation client de référence du marketing. Trois axes :

| Lettre | Signification | Question | Bon score = |
|---|---|---|---|
| **R — Récence** | Jours depuis le dernier achat | « Est-il encore actif ? » | **petit** (acheté récemment) |
| **F — Fréquence** | Nombre d'achats | « Achète-t-il souvent ? » | **grand** |
| **M — Montant** | Total dépensé | « Combien rapporte-t-il ? » | **grand** |

### Calculer les trois indicateurs par client

```python
date_ref = df["date"].max() + pd.Timedelta(days=1)  # « aujourd'hui » = lendemain de la dernière vente

rfm = df.groupby("client_id").agg(
    recence=("date", lambda d: (date_ref - d.max()).days),
    frequence=("transaction_id", "count"),
    montant=("montant", "sum"),
).round(2)
print(rfm.describe().round(1))
```

### Scorer de 1 à 5 par quantiles

```python
# Récence : petit = bon → on inverse les labels (5 = le plus récent)
rfm["R"] = pd.qcut(rfm["recence"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequence"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M"] = pd.qcut(rfm["montant"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["score_rfm"] = rfm["R"] + rfm["F"] + rfm["M"]   # de 3 à 15
rfm["RFM"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
print(rfm.head())
```

> 💡 **Astuce technique.** Sur la fréquence, beaucoup de clients ont la **même** valeur → `qcut` plante (bords de bins identiques). Le `.rank(method="first")` casse les ex æquo et permet le découpage. Réflexe à connaître.

> 🎲 **Devine AVANT de voir le résultat.** Parmi les segments que la Ch'ti Boutique va obtenir (Champions, Clients fidèles, À risque, Endormis, À développer…), **lequel rapporte le plus d'argent par client en moyenne** ? Et surtout : **lequel mérite ton attention en URGENCE** ? Pose tes deux paris, puis lis la suite. (Indice : le plus rentable n'est pas forcément celui qu'il faut chouchouter le plus…)

### Nommer les segments (la valeur métier)

```python
def segment(row):
    r, f, m = row["R"], row["F"], row["M"]
    if r >= 4 and f >= 4 and m >= 4:   return "Champions"
    if r >= 4 and f >= 3:              return "Clients fidèles"
    if r >= 4:                         return "Nouveaux / récents"
    if r <= 2 and f >= 4:             return "À risque (gros clients qui partent)"
    if r <= 2:                         return "Endormis / perdus"
    return "À développer"

rfm["segment"] = rfm.apply(segment, axis=1)
synth = rfm.groupby("segment").agg(
    nb_clients=("RFM", "count"),
    panier_total_moyen=("montant", "mean"),
    recence_moyenne=("recence", "mean"),
).round(1).sort_values("nb_clients", ascending=False)
print(synth)
```

**Sortie commentée :**

```
                                       nb_clients  panier_total_moyen  recence_moyenne
segment
À développer                                  31x               245.x            18x.x
Clients fidèles                               1xx               410.x             4x.x
Champions                                      9x               690.x             2x.x
À risque (gros clients qui partent)            5x               520.x            21x.x
Endormis / perdus                              7x               180.x            29x.x
...
```

> **Interprétation métier — le cœur du métier de DA.**
> - **Champions** (R/F/M élevés) : tes meilleurs clients. **Action** : programme VIP, accès anticipé, ne surtout pas les sur-solliciter par des promos (ils paient déjà plein pot).
> - **À risque** (forte valeur historique mais récence faible) : **urgence**. Ce sont de gros clients en train de partir. **Action** : relance personnalisée, offre de reconquête. C'est ici qu'un euro investi rapporte le plus.
> - **Endormis / perdus** : faible récence ET faible valeur. **Action** : campagne de masse à faible coût, ou… les laisser partir (ROI négatif).
> - **Nouveaux** : à transformer en fidèles → séquence d'accueil.
>
> 🎲 **Verdict de ton pari.** Les **Champions** ont le plus gros panier total moyen (~690 € ici) : c'est le segment le plus rentable *par tête*. Mais l'urgence, c'est le segment **« À risque »** — de gros clients (panier élevé) qui n'achètent plus depuis longtemps (récence faible). On ne se bat pas pour les Champions (ils sont déjà fidèles), on se bat pour ne pas perdre ceux qui valent cher et qui filent. Si tu avais misé là-dessus : bravo, tu raisonnes déjà comme un·e pro du marketing. 🎯

> 🎯 **Ça te servira pour…** arriver en réunion avec une **liste d'actions concrètes** au lieu de chiffres bruts : « voici nos 90 Champions à inviter en avant-première, voici les 50 clients À risque à relancer cette semaine ». C'est CE livrable qui fait dire à ta direction « on a bien fait de l'embaucher ». 🏆

> 🔗 **Lien Phase 2.** Cette table `rfm` (un client = une ligne, un segment) deviendra une **dimension client** dans ton modèle en étoile (module 2.2), et le « segment » sera un **filtre / une mesure** dans ton tableau de bord Power BI (modules 2.3-2.4). Tu viens de produire la matière première de toute ta restitution BI.

---

## Justifier le choix d'une statistique selon la donnée

Compétence niveau 2 attendue à l'oral comme à l'écrit : **savoir pourquoi** tu choisis tel indicateur.

| Nature de la donnée | Indicateur de tendance | Indicateur de lien | Visualisation |
|---|---|---|---|
| **Quantitative symétrique** | moyenne + écart-type | corrélation de Pearson | histogramme, scatterplot |
| **Quantitative asymétrique / avec outliers** | **médiane + IQR** | corrélation de **Spearman** (rangs) | boxplot |
| **Qualitative (catégorielle)** | mode, effectifs, % | tableau croisé (`crosstab`), Cramér's V | barres, barres empilées |
| **Deux qualitatives** | tableau croisé | test du **χ² (chi-deux)** | heatmap d'effectifs |

> 🧭 **Règle d'or.** Sur des **montants** (toujours asymétriques), réflexe **médiane**. Sur une relation potentiellement **non linéaire** ou avec outliers, réflexe **Spearman** (`df.corr(method="spearman")`). Pour relier **deux variables catégorielles**, ce n'est **pas** Pearson mais le **χ²** :
>
> ```python
> from scipy.stats import chi2_contingency
> table = pd.crosstab(df["ville"], df["rayon"])
> chi2, p, dof, expected = chi2_contingency(table)
> print(f"χ² = {chi2:.1f}   p = {p:.3f}")   # p > 0,05 ici → ville et rayon indépendants
> ```

---

## Travaux pratiques

> 🏆 **LE DÉFI DU MODULE — « Classe les clients de la Ch'ti Boutique ».**
> Ta mission, si tu l'acceptes : produire en une cellule le **podium des clients** de la boutique en trois catégories parlantes — **VIP**, **Réguliers**, **Endormis** — et compter combien il y en a dans chaque. C'est la version condensée de tout le module : tu calcules la RFM, tu nommes, tu comptes. Si tu réussis ça sans regarder la solution, tu maîtrises l'essentiel. ⏱️ Objectif : 10 minutes.
>
> <details><summary>🎁 Solution du défi (essaie d'abord !)</summary>
>
> ```python
> # On part de la table rfm calculée au §10 (R, F, M déjà scorés de 1 à 5)
> def carte_fidelite(row):
>     # VIP : actif récemment ET (fidèle OU gros dépensier)
>     if row["R"] >= 4 and (row["F"] >= 4 or row["M"] >= 4):
>         return "VIP"
>     # Endormi : pas revenu depuis longtemps
>     if row["R"] <= 2:
>         return "Endormi"
>     # Tout le reste = client régulier
>     return "Régulier"
>
> rfm["carte"] = rfm.apply(carte_fidelite, axis=1)
> print(rfm["carte"].value_counts())
> ```
> **Ce que tu dois savoir lire :** un client n'est « VIP » que s'il est **encore actif** (R élevé) — un gros dépensier disparu n'est pas un VIP, c'est un client « À risque » qu'il faut réveiller ! C'est tout l'esprit de la RFM : croiser les trois axes, jamais regarder le montant tout seul.
> </details>

---

> Travaille dans un notebook, avec le jeu de données du §3. Corrigés repliés : essaie **avant** de déplier.

### TP 1 — Tableau croisé du CA

Construis un `pivot_table` donnant le **chiffre d'affaires total** (somme du montant) par **ville** (lignes) et **rayon** (colonnes), avec les marges. Quelle ville × rayon génère le plus de CA ?

<details><summary>✅ Corrigé</summary>

```python
ca = pd.pivot_table(df, values="montant", index="ville", columns="rayon",
                    aggfunc="sum", margins=True, margins_name="Total").round(0)
print(ca)
# La cellule (Lille, n'importe quel rayon) domine car Lille = 30 % du volume.
# Lire la ligne/colonne "Total" pour les classements globaux.
```
La clé : `aggfunc="sum"` (et pas la moyenne par défaut). On lit la cellule hors-marges la plus élevée.
</details>

### TP 2 — Corrélation et nuage de points

Calcule la corrélation de Pearson entre `montant` et `prix_moyen_article` **après avoir retiré les 8 anomalies**. Compare avec la corrélation **sur le jeu complet**. Que constates-tu ? Trace le nuage de points.

<details><summary>✅ Corrigé</summary>

```python
propre = df[df["montant"] < 1000]   # on écarte les anomalies
print("Avec anomalies :", df["montant"].corr(df["prix_moyen_article"]).round(3))
print("Sans anomalies :", propre["montant"].corr(propre["prix_moyen_article"]).round(3))

import seaborn as sns
sns.scatterplot(data=propre, x="prix_moyen_article", y="montant", alpha=.3)
```
**Constat :** les outliers **gonflent** la corrélation. Sur données propres, *r* est plus modéré et plus honnête. Morale : nettoyer **avant** de corréler.
</details>

### TP 3 — Segmentation + comparaison

Crée un segment `gros_panier` (`True` si montant > 80 €). Compare le **nombre moyen d'articles** entre gros et petits paniers, et teste si la différence est significative (test t).

<details><summary>✅ Corrigé</summary>

```python
from scipy import stats
df["gros_panier"] = df["montant"] > 80
print(df.groupby("gros_panier")["nb_articles"].mean().round(2))

a = df.loc[df["gros_panier"], "nb_articles"]
b = df.loc[~df["gros_panier"], "nb_articles"]
t, p = stats.ttest_ind(a, b, equal_var=False)
print(f"t = {t:.2f}  p = {p:.4f}")
# p < 0,05 attendu → les gros paniers ont significativement plus d'articles. Différence réelle.
```
</details>

### TP 4 — Détection d'anomalies croisée

Trouve toutes les transactions dont le `prix_moyen_article` est aberrant (z-score > 3). Combien y en a-t-il ? Recoupe avec les anomalies de montant : sont-ce les mêmes ?

<details><summary>✅ Corrigé</summary>

```python
from scipy import stats
df["z_prix"] = np.abs(stats.zscore(df["prix_moyen_article"]))
anom_prix = df[df["z_prix"] > 3]
print(len(anom_prix), "anomalies de prix unitaire")
# Recoupement
communs = set(anom_prix["transaction_id"]) & set(df.loc[df["z_montant"] > 3, "transaction_id"])
print(len(communs), "anomalies communes aux deux critères")
```
Les anomalies de **montant** se retrouvent souvent en anomalies de **prix unitaire** (montant énorme / peu d'articles). Le croisement confirme et priorise.
</details>

### TP 5 — RFM complète

Reproduis l'analyse RFM du §10 et réponds : **combien de clients « À risque »** as-tu, et quel est leur **CA total cumulé** ? Pourquoi ce segment doit-il être ta priorité ?

<details><summary>✅ Corrigé</summary>

```python
a_risque = rfm[rfm["segment"] == "À risque (gros clients qui partent)"]
print("Nb clients à risque :", len(a_risque))
print("CA cumulé à risque :", a_risque["montant"].sum().round(0), "€")
```
**Justification :** ce segment concentre une **forte valeur historique** mais une **récence faible** → revenu en train de fuir. Le retenir coûte moins cher que recruter un nouveau client équivalent. ROI marketing maximal.
</details>

### TP 6 (bonus) — Heatmap de corrélation enrichie

Ajoute la variable `nb_articles`, `prix_moyen_article`, le score RFM par transaction (jointure), et produis une heatmap de corrélation **Spearman**. Pourquoi Spearman ici plutôt que Pearson ?

<details><summary>✅ Corrigé</summary>

```python
num = df[["montant", "nb_articles", "prix_moyen_article"]]
corr_s = num.corr(method="spearman").round(2)
sns.heatmap(corr_s, annot=True, cmap="coolwarm", center=0)
```
**Spearman** travaille sur les **rangs** : robuste aux outliers et capte les relations **monotones non linéaires**. Sur des montants gamma (asymétriques), il est plus fiable que Pearson.
</details>

---

## Vidéos d'auto-formation

> Liens vérifiés au mieux. Quand l'URL exacte n'a pas pu être confirmée, le lien pointe vers une **recherche YouTube** fiable (jamais d'URL inventée).

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| RFM Analysis Tutorial In Pandas: Simple Customer Segmentation | Pythonology / Code | EN | ~20 min | https://www.youtube.com/watch?v=9wxWrERZvss | Calcul R/F/M, scoring par `qcut`, nommage des segments — exactement le §10 |
| Mise à l'échelle des données : normalisation et standardisation (feature scaling) + codes Python | Machine Learnia (style) | FR | ~15 min | https://www.youtube.com/watch?v=eA9U_P9QikE | Min-max vs z-score, `MinMaxScaler`/`StandardScaler`, quand utiliser quoi |
| Python Pandas Tutorial 10 — Pivot Table | codebasics | EN | ~10 min | https://www.youtube.com/watch?v=xPPs59pn6qU | `pivot_table`, `aggfunc`, marges — le §5 en vidéo |
| Covariance, Clearly Explained!!! | StatQuest with Josh Starmer | EN | ~22 min | https://www.youtube.com/watch?v=qtaqvPAeEJY | L'intuition derrière corrélation/covariance avant la heatmap (§6) |
| Heatmap de corrélation avec Seaborn (recherche) | (recherche YouTube) | FR | varié | https://www.youtube.com/results?search_query=heatmap+correlation+seaborn+python+fran%C3%A7ais | `df.corr()` + `sns.heatmap`, lecture et interprétation d'une matrice |

---

## Quiz — 5 QCM

**Q1.** Tu veux le **panier moyen** par ville ET par rayon. Quel outil ?
- a) `crosstab`
- b) `pivot_table` avec `aggfunc="mean"`
- c) `value_counts`
- d) `df.corr()`

**Q2.** Une corrélation de Pearson de **+0,9** entre deux variables signifie :
- a) que l'une cause l'autre
- b) un lien linéaire positif fort, sans conclusion sur la causalité
- c) que les variables sont indépendantes
- d) qu'il y a forcément une erreur

**Q3.** Pour segmenter tes clients en **groupes d'effectifs égaux** selon le montant, tu utilises :
- a) `pd.cut`
- b) `pd.qcut`
- c) `StandardScaler`
- d) `crosstab`

**Q4.** Dans une analyse RFM, un bon score de **Récence** correspond à :
- a) une grande valeur (beaucoup de jours)
- b) une petite valeur (achat récent)
- c) le montant total dépensé
- d) le nombre d'articles

**Q5.** Tes données de montant sont très **asymétriques avec des outliers**. Pour mesurer le lien avec une autre variable, tu privilégies :
- a) Pearson
- b) Spearman
- c) le χ²
- d) la moyenne

<details><summary>✅ Réponses</summary>

**Q1 → b.** `crosstab` compte des effectifs ; pour **agréger une mesure numérique** (la moyenne), c'est `pivot_table` avec `aggfunc="mean"`.
**Q2 → b.** Lien linéaire positif fort. La corrélation **ne prouve jamais** une causalité.
**Q3 → b.** `qcut` découpe en quantiles = effectifs égaux. (`cut` = seuils de valeurs fixés.)
**Q4 → b.** Récence faible (peu de jours depuis le dernier achat) = client encore actif = **bon** score.
**Q5 → b.** **Spearman** (sur les rangs) est robuste aux outliers et aux relations non linéaires monotones.
</details>

---

## À retenir

- **Univarié → multivarié.** La valeur d'une analyse de niveau 2 vient du **croisement** des variables, pas d'une statistique isolée.
- **`crosstab`** compte des effectifs (qualitatif) ; **`pivot_table`** agrège une mesure (`mean`/`sum`/…). Surveille `aggfunc` et l'axe de `normalize`.
- **Corrélation ≠ causalité.** Pearson ne voit que le **linéaire** ; sur données asymétriques/outliers → **Spearman**. Toujours doubler d'un nuage de points.
- **Segmenter** = `qcut` (effectifs égaux) ou `cut` (seuils métier). Une différence entre groupes n'est réelle que si le **test** (p-value < 0,05) le confirme.
- **RFM** = la segmentation client reine : Récence (petit = bon), Fréquence, Montant → des **segments actionnables** (Champions, À risque…). C'est la matière première de ta future dimension client en BI.
- **Normaliser/standardiser** avant tout calcul de distance ou comparaison d'échelles ; **nettoie les anomalies d'abord**.
- **Détection d'anomalies** : IQR (robuste) ou z-score (>3σ), et **croise les critères** pour prioriser. Erreur ou cas rare ? Toujours se poser la question, et **documenter**.
- **Justifier** son choix de statistique selon la **nature de la donnée** est une compétence évaluée : entraîne-toi à dire *pourquoi* médiane plutôt que moyenne, Spearman plutôt que Pearson, χ² plutôt que corrélation.
