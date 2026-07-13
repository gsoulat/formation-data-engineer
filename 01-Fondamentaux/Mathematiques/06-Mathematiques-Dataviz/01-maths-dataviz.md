# 06 — Mathématiques pour la dataviz

> **Objectif : Choisir des visualisations pertinentes**
> Formation Data Analyst
> Bloc « Mathématiques pour l'analyse de données »

---

## Présentation

### 🎬 Bienvenue à la Ch'ti Boutique

> *Imagine. Tu viens d'être embauché·e comme Data Analyst de la **Ch'ti Boutique**, une chaîne de magasins du Nord (Lille, Valenciennes, Roubaix…). Ton job : faire parler les chiffres en réunion. Sauf que ton patron adore les graphiques… et que le commercial du rez-de-chaussée ADORE les graphiques qui mentent pour gonfler ses résultats. Ta mission tout au long de ce chapitre : produire des graphiques **honnêtes**, et surtout **démasquer ceux qui trichent**. Enfile ton imperméable de détective. 🕵️*

Une visualisation de données, ce n'est pas de la décoration. C'est un **argument mathématique** rendu visible. Quand tu choisis une échelle, une origine d'axe, une moyenne plutôt qu'une médiane, tu prends une décision qui change ce que ton lecteur va comprendre — et parfois ce qu'il va croire.

Ce chapitre te donne les outils mathématiques pour produire des graphiques **honnêtes et pertinents** dans Power BI, Looker Studio ou matplotlib. L'angle est toujours le même : *comment représenter visuellement un chiffre sans mentir, et sans se laisser mentir.*

> 🕵️ **L'IDÉE PHARE DU CHAPITRE — Détective des graphiques menteurs.**
> Ce chapitre est une **enquête**. À chaque notion, le commercial de la Ch'ti Boutique va te montrer un graphique louche. À toi de **repérer l'arnaque** avant la révélation. Cinq mensonges classiques t'attendent (axe Y tronqué, échelle log cachée, double axe trompeur, camembert déformé, moyenne qui cache tout). Le **Défi du chapitre** (section 7 bis) te demandera de les démasquer tous les cinq. Garde l'œil ouvert. 👀

---

## Objectifs

À la fin de ce chapitre, tu sauras :

- choisir entre une **échelle linéaire et logarithmique**, et justifier ton choix ;
- détecter et éviter le **piège de l'axe tronqué** (origine qui ne commence pas à zéro) ;
- **normaliser** (min-max) et **standardiser** (z-score) des données, et savoir lequel utiliser ;
- construire un **indice base 100** pour comparer des évolutions ;
- calculer un **taux de croissance** et un **CAGR** (taux de croissance annuel moyen) ;
- utiliser une **moyenne pondérée** et une **moyenne mobile** (lissage de séries temporelles) ;
- choisir la bonne **agrégation** (somme / moyenne / médiane) selon le contexte ;
- reconnaître les grands **pièges mathématiques de la dataviz** : paradoxe de Simpson, moyenne trompeuse, échelles mensongères.

---

## Pourquoi c'est utile au Data Analyst

Tu passes une grande partie de ton temps à **restituer** : un dashboard, une slide, un rapport. Le moment où tu choisis un graphique est le moment où l'analyse rencontre la décision métier.

Concrètement :

- Ton responsable retail te demande de comparer le CA de 8 magasins du Nord. Si tu mets un **axe tronqué**, le magasin de Lille semble écraser celui de Valenciennes alors qu'il fait 5 % de plus. Tu induis une décision (fermeture ?) sur une illusion d'optique.
- Tu compares la croissance de produits vendus à des prix très différents (un café à 2 € et une machine à 600 €). Sur une échelle linéaire, le café est invisible. Sur une **échelle log**, les deux croissances se lisent.
- Tu présentes « le panier moyen est de 47 € ». Si trois gros clients B2B tirent la moyenne vers le haut, la **médiane** (32 €) raconte une histoire plus juste de ton client typique.

Bref : maîtriser ces notions, c'est la différence entre un analyste à qui on fait confiance et un analyste dont on doit recontrôler chaque graphe.

---

## Les notions

### Échelles : linéaire vs logarithmique

> 🕵️ **ENQUÊTE n°1 — « Notre petit produit ne se vend pas. »**
> Le commercial te montre une courbe : « Regardez, la machine à grains pro est une ligne plate collée au sol, ce produit est mort, on l'arrête. » Sur le même graphe, le café cartonne. **Tu sens l'arnaque ?** Note ton intuition, on révèle juste en dessous.
>
> 🎲 **Devine avant de regarder.** Le café progresse de +2 %/mois, la machine pro de +20 %/mois. Sur le graphe linéaire du commercial, lequel **monte le plus à l'œil** ? Et qui grandit vraiment le plus vite ?
>
> 🎯 **Ça te servira pour…** afficher honnêtement dans Power BI / Looker des produits ou des pays d'échelles très différentes (un café à 2 € à côté d'une machine à 600 €) sans écraser le petit.

**Définition.**
Sur une **échelle linéaire**, un même écart visuel représente toujours le même écart de valeur : de 0 à 100, c'est la même distance que de 100 à 200.
Sur une **échelle logarithmique**, un même écart visuel représente le même **rapport** (multiplication) : de 1 à 10, c'est la même distance que de 10 à 100, ou de 100 à 1 000. Chaque graduation est ×10 (log base 10).

**Quand utiliser le log ?**
- Quand tes données couvrent **plusieurs ordres de grandeur** (de quelques unités à plusieurs millions).
- Quand ce qui compte est le **taux de variation** (croissance en %) plutôt que la valeur absolue. Sur une échelle log, une croissance exponentielle apparaît comme une **droite**.
- Exemples classiques : population, revenus, contaminations en épidémie, capitalisations boursières.

**Exemple chiffré métier.**
Tu suis les ventes mensuelles de 3 références dans une enseigne du Nord :

| Référence | Ventes / mois |
|---|---|
| Sachet de café | 12 000 € |
| Cafetière filtre | 1 800 € |
| Machine à grains pro | 95 € |

Sur une échelle linéaire (axe de 0 à 12 000), la machine à grains pro est une ligne collée au sol : impossible de voir si elle progresse. Sur une échelle log, les trois courbes deviennent lisibles et comparables.

**Formule.**
Passer une valeur en log base 10 :

```
y_log = log10(y)
```

`log10(95) ≈ 1,98` · `log10(1800) ≈ 3,26` · `log10(12000) ≈ 4,08`
Les trois tiennent maintenant sur un axe allant de ~2 à ~4 : tout est visible.

**Calcul à la main.**
`log10(100) = 2` (car 10² = 100), `log10(1000) = 3`, `log10(10) = 1`.
Donc passer de 100 à 1000 (×10) ajoute toujours **+1** sur l'axe log. C'est ça, l'idée : le log transforme une multiplication en addition.

> 🧠 **Analogie.** L'échelle log, c'est un **ascenseur où chaque étage = ×10**. Du sous-sol (1) au 4ᵉ étage (10 000), il n'y a que 4 boutons à monter, même si la distance « réelle » est énorme. Le petit produit et le géant prennent le même ascenseur : on les compare enfin.
>
> ✅ **Révélation de l'enquête n°1.** Le commercial mentait par omission. En **linéaire**, la machine pro paraît plate uniquement parce que le café est 100× plus gros et écrase l'axe. En **log**, surprise : la machine pro grimpe le plus raide (+20 %/mois) — c'est la pépite, surtout pas à arrêter ! Le bon graphe (log) inverse complètement la décision business.

**EN PYTHON — viz honnête vs trompeuse.**

```python
import numpy as np
import matplotlib.pyplot as plt

mois = np.arange(1, 13)
cafe      = 12000 * (1.02 ** mois)   # +2 %/mois
cafetiere = 1800  * (1.05 ** mois)   # +5 %/mois
machine   = 95    * (1.20 ** mois)   # +20 %/mois (forte croissance !)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# TROMPEUR : échelle linéaire -> la machine pro semble plate
ax1.plot(mois, cafe, label="Café")
ax1.plot(mois, cafetiere, label="Cafetière")
ax1.plot(mois, machine, label="Machine pro")
ax1.set_title("Linéaire : la machine pro semble stagner (FAUX)")
ax1.set_ylabel("Ventes (€)")
ax1.legend()

# HONNÊTE : échelle log -> on voit que la machine pro explose
ax2.plot(mois, cafe, label="Café")
ax2.plot(mois, cafetiere, label="Cafetière")
ax2.plot(mois, machine, label="Machine pro")
ax2.set_yscale("log")           # <-- échelle logarithmique
ax2.set_title("Log : la croissance réelle apparaît (VRAI)")
ax2.set_ylabel("Ventes (€, échelle log)")
ax2.legend()

plt.tight_layout()
plt.show()
```

> Dans **Power BI** : propriété de l'axe Y → *Type d'échelle* → **Log**.
> Dans **Looker Studio** : Style du graphique → cocher *Axe → Échelle logarithmique*.

**Erreurs courantes.**
- Mettre du log sans le **dire clairement** sur l'axe : le lecteur croit lire du linéaire et surinterprète.
- Utiliser le log avec des **valeurs nulles ou négatives** : `log10(0)` n'existe pas. Filtre ou décale tes données.
- Mettre du log « pour faire savant » alors que les données sont sur un seul ordre de grandeur : ça complique pour rien.

---

### Axes et choix d'origine — le piège de l'axe tronqué

> 🕵️ **ENQUÊTE n°2 — « Lille écrase Valenciennes ! »**
> Le commercial débarque en réunion avec un diagramme en barres : la barre de Lille fait **deux fois la hauteur** de celle de Valenciennes. « Lille est notre champion, fermons Valenciennes. » **Repère l'arnaque** : regarde où commence son axe vertical avant de le croire.
>
> 🎲 **Devine avant de calculer.** Lille = 520 000 €, Valenciennes = 495 000 €. À ton avis, l'écart réel est plutôt de **5 %** ou de **100 %** ? Parie, puis vérifie.

**Définition.**
Un **axe tronqué** est un axe dont l'origine ne commence pas à zéro. Sur un **graphique en barres**, c'est presque toujours **trompeur** : la hauteur d'une barre est censée représenter la valeur ; si la base n'est pas à 0, les écarts visuels sont mensongers.

**Exemple chiffré métier.**
CA annuel de deux magasins :

| Magasin | CA |
|---|---|
| Lille | 520 000 € |
| Valenciennes | 495 000 € |

Écart réel : `(520000 − 495000) / 495000 ≈ 5 %`.

- **Axe commençant à 480 000** : la barre de Lille paraît **2 fois plus haute** que celle de Valenciennes. Mensonge visuel.
- **Axe commençant à 0** : les deux barres sont quasi identiques, l'écart de 5 % est honnête.

> ✅ **Révélation de l'enquête n°2.** L'écart réel n'est que de **5 %**. L'illusion vient de l'axe qui démarre à 480 000 au lieu de 0 : on ne voit plus que le petit bout du haut des barres, donc 25 000 € de différence ont l'air gigantesques. **Fermer Valenciennes sur cette base serait une erreur de management déclenchée par un graphique truqué.**

> 🧠 **Mnémo.** Axe tronqué = **« zoomer pour dramatiser »**. Couper le bas d'une barre, c'est comme filmer une dispute en gros plan : ça paraît énorme alors qu'il ne s'est presque rien passé. Sur des **barres, l'origine commence à 0, point.**
>
> 🎯 **Ça te servira pour…** garantir une restitution honnête dans Power BI / Looker : vérifie systématiquement *Axe Y → Début = 0* sur tout graphique en barres avant de l'envoyer à ton patron.

**Règle de décision.**
- **Barres / histogrammes / aires** → l'origine **doit** être à zéro. La surface code l'information.
- **Courbes (lignes)** → on **peut** tronquer pour montrer une variation fine, à condition de l'**annoter** et de ne pas tromper. La position code l'information, pas la surface.

**EN PYTHON — viz honnête vs trompeuse.**

```python
import matplotlib.pyplot as plt

magasins = ["Lille", "Valenciennes"]
ca = [520_000, 495_000]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

# TROMPEUR : axe tronqué à 480 000
ax1.bar(magasins, ca, color=["#c0392b", "#2980b9"])
ax1.set_ylim(480_000, 525_000)   # <-- l'arnaque
ax1.set_title("Axe tronqué : Lille écrase Valenciennes (FAUX)")

# HONNÊTE : axe à zéro
ax2.bar(magasins, ca, color=["#c0392b", "#2980b9"])
ax2.set_ylim(0, 600_000)         # base à 0
ax2.set_title("Axe à 0 : écart réel ~5 % (VRAI)")

plt.tight_layout()
plt.show()
```

> Dans **Power BI** : sur un graphique en barres, vérifie que *Axe Y → Début = 0*. Power BI peut tronquer automatiquement : c'est à toi de remettre 0.

**Erreurs courantes.**
- Laisser l'outil choisir l'axe automatiquement sur des **barres** (il tronque souvent).
- Tronquer **sans le signaler** sur une courbe.
- Comparer deux graphiques côte à côte avec des **échelles différentes** : faux jumeaux trompeurs.

---

### Normalisation et standardisation

**Pourquoi normaliser ?**
Quand tu veux **comparer des variables d'unités différentes** (un CA en €, un nombre de visites, une note de satisfaction sur 5), tu ne peux pas les superposer telles quelles : l'échelle écrase tout. Tu les ramènes sur une **base commune**.

> 🧠 **L'image qui débloque tout.** Comparer un CA en euros, un trafic en visiteurs et une note sur 5, c'est comparer des mètres, des kilos et des litres. Impossible tel quel. **Normaliser = tout ramener sur la même règle de 0 à 1**, comme convertir tout le monde en pourcentage avant de comparer. Une fois sur la même règle, on compare les **profils**, pas les unités.
>
> 🎯 **Ça te servira pour…** superposer sur une seule jauge (ou un radar) des indicateurs d'échelles incomparables dans ton dashboard. Sans normalisation, le CA (en centaines de milliers) écraserait toujours la satisfaction (sur 5).
>
> ✂️ **En une phrase chacun.** *Normalisation min-max* = je rapetisse tout entre **0 et 1** (la plus petite valeur devient 0, la plus grande devient 1). *Standardisation z-score* = je mesure chaque valeur en **« nombre d'écarts-types par rapport à la moyenne »** (0 = pile la moyenne, +2 = bien au-dessus, −2 = bien en dessous).

#### a) Normalisation min-max

**Définition.** Ramène chaque valeur dans l'intervalle **[0, 1]**.

**Formule.**
```
x_norm = (x − min) / (max − min)
```

**Exemple chiffré.** Satisfaction de 4 magasins : `[2, 3, 4, 5]` (sur 5).
`min = 2`, `max = 5`, étendue = 3.
- `(2−2)/3 = 0,00`
- `(3−2)/3 = 0,33`
- `(4−2)/3 = 0,67`
- `(5−2)/3 = 1,00`

#### b) Standardisation (z-score)

**Définition.** Recentre les données sur une **moyenne de 0** et un **écart-type de 1**. Le z-score dit « à combien d'écarts-types de la moyenne se situe cette valeur ».

**Formule.**
```
z = (x − moyenne) / écart-type
```

**Exemple chiffré.** Mêmes notes `[2, 3, 4, 5]`. Moyenne = 3,5 ; écart-type (population) ≈ 1,118.
- `(2−3,5)/1,118 ≈ −1,34`
- `(5−3,5)/1,118 ≈ +1,34`
Une valeur z = +2 est « anormalement haute » (au-delà de 95 % des cas si distribution normale).

**Min-max vs z-score : lequel choisir ?**

| Critère | Min-max | Z-score |
|---|---|---|
| Sortie | bornée [0, 1] | non bornée, centrée sur 0 |
| Sensible aux **valeurs extrêmes** | **Oui** (un outlier écrase tout) | moins |
| Bon pour | jauges, heatmaps, barres comparatives | détecter des anomalies, comparer des distributions |
| Garde la forme de la distribution | oui | oui (juste recentrée/réduite) |

**Calcul à la main (z-score).**
1. Moyenne : `(2+3+4+5)/4 = 3,5`
2. Écarts au carré : `(2−3,5)² + (3−3,5)² + (4−3,5)² + (5−3,5)² = 2,25+0,25+0,25+2,25 = 5`
3. Variance = `5/4 = 1,25` ; écart-type = `√1,25 ≈ 1,118`
4. z de 2 = `(2−3,5)/1,118 ≈ −1,34`

**EN PYTHON.**

```python
import numpy as np

notes = np.array([2, 3, 4, 5], dtype=float)

# Min-max -> [0, 1]
minmax = (notes - notes.min()) / (notes.max() - notes.min())

# Z-score -> centré réduit
zscore = (notes - notes.mean()) / notes.std()  # std() = écart-type population

print("Min-max :", np.round(minmax, 2))   # [0.   0.33 0.67 1.  ]
print("Z-score :", np.round(zscore, 2))   # [-1.34 -0.45  0.45  1.34]
```

Sur un dashboard où tu superposes *CA*, *trafic* et *satisfaction*, normalise chaque série en min-max pour les afficher sur la même jauge 0–100 % : on compare alors les **profils**, pas les unités.

**Erreurs courantes.**
- **Confondre** les deux : « normaliser » (min-max, borne [0,1]) ≠ « standardiser » (z-score, centré-réduit). En entretien, c'est un grand classique.
- Faire du min-max quand il y a un **outlier** : il devient 1 et écrase tout le reste vers 0.
- Standardiser puis présenter les z-scores **bruts** à un métier : « −1,34 » ne parle à personne. Réserve le z-score à la détection d'anomalies, pas à la restitution grand public.

---

### Indice base 100

> 🎯 **Ça te servira pour…** comparer la **dynamique** de deux choses de tailles très différentes (un gros magasin et un petit) : qui progresse le plus vite, indépendamment du niveau absolu. C'est l'outil préféré des analystes financiers.

**Définition.** On choisit une période de **référence** = 100, et on exprime toutes les autres valeurs **relativement** à elle. Idéal pour comparer des **évolutions** de grandeurs de tailles différentes.

**Formule.**
```
indice = (valeur / valeur_référence) × 100
```

**Exemple chiffré métier.** CA de deux magasins, base 100 en janvier :

| Mois | Lille (€) | Indice Lille | Valenciennes (€) | Indice Val. |
|---|---|---|---|---|
| Jan | 500 000 | 100 | 200 000 | 100 |
| Fév | 525 000 | 105 | 220 000 | 110 |
| Mar | 540 000 | 108 | 250 000 | 125 |

En valeur absolue, Lille domine. Mais en base 100, **Valenciennes croît plus vite** (+25 % vs +8 %). L'indice révèle la dynamique que l'absolu cachait.

**Calcul à la main.** Indice Val. mars = `250000 / 200000 × 100 = 125`.

**EN PYTHON.**

```python
import pandas as pd

df = pd.DataFrame({
    "mois": ["Jan", "Fév", "Mar"],
    "lille": [500_000, 525_000, 540_000],
    "valenciennes": [200_000, 220_000, 250_000],
})

# Base 100 sur la première ligne
df["idx_lille"] = df["lille"] / df["lille"].iloc[0] * 100
df["idx_val"]   = df["valenciennes"] / df["valenciennes"].iloc[0] * 100

print(df[["mois", "idx_lille", "idx_val"]])
```

**Erreurs courantes.**
- Oublier de préciser **la base** (« base 100 = janvier 2024 »).
- Comparer deux indices avec des **bases différentes**.

---

### Taux de croissance et CAGR

**Taux de croissance simple.**
```
taux = (valeur_fin − valeur_début) / valeur_début × 100
```
De 200 000 à 250 000 : `(250000−200000)/200000 = 25 %`.

**Le piège de la moyenne des taux.**
Si une grandeur fait +50 % une année puis −50 % l'année suivante, la « moyenne » naïve est 0 %. Faux ! Pars de 100 → +50 % = 150 → −50 % = 75. Tu as **perdu 25 %**. On ne fait jamais la moyenne arithmétique de taux de croissance.

**CAGR — taux de croissance annuel moyen.**
C'est le taux **constant** qui, appliqué chaque année, mène de la valeur de départ à la valeur d'arrivée. C'est une **moyenne géométrique**.

> ✂️ **Le CAGR en langage humain.** « Si ma croissance avait été **régulière** (le même % chaque année), ça aurait été combien par an ? » C'est le « rythme de croisière » qui efface les années en dents de scie. On ne fait JAMAIS la moyenne classique des % (voir le piège juste au-dessus) : on remonte le temps à l'envers avec une racine.
>
> 🎲 **Devine avant de calculer.** Un CA passe de 200 k€ à 320 k€ en 3 ans. À vue de nez, le rythme annuel, c'est plutôt **10 %**, **17 %** ou **30 %** par an ? Parie, puis lis l'exemple.
>
> 🎯 **Ça te servira pour…** répondre à « notre croissance annuelle moyenne, c'est combien ? » sans te ridiculiser avec une fausse moyenne arithmétique.

**Formule.**
```
CAGR = (valeur_fin / valeur_début)^(1 / nombre_d_années) − 1
```

**Exemple chiffré métier.** CA passé de 200 000 € (2021) à 320 000 € (2024) → 3 ans.
```
CAGR = (320000 / 200000)^(1/3) − 1 = (1,6)^(0,333) − 1 ≈ 1,1696 − 1 ≈ 0,1696 = 16,96 %
```
Le CA a crû en moyenne de **~17 % par an**.

**Calcul à la main.** `1,6^(1/3)` = racine cubique de 1,6 ≈ 1,1696. Donc CAGR ≈ 16,96 %.

**EN PYTHON.**

```python
debut, fin, annees = 200_000, 320_000, 3
cagr = (fin / debut) ** (1 / annees) - 1
print(f"CAGR = {cagr:.2%}")   # CAGR = 16.96%
```

> Dans **Power BI (DAX)**, on calcule souvent le CAGR avec `POWER(fin/debut, 1/annees) - 1`.

**Erreurs courantes.**
- Faire la **moyenne arithmétique** des taux annuels au lieu du CAGR.
- Annoncer un taux de croissance **sans préciser la période** (mensuel ? annuel ?).
- CAGR sur une grandeur qui passe par **zéro ou négatif** : la formule perd son sens.

---

### Moyenne pondérée

**Définition.** Chaque valeur compte selon un **poids** (effectif, volume, chiffre d'affaires…). Indispensable quand les groupes n'ont pas la même taille.

**Formule.**
```
moyenne_pondérée = Σ(valeur × poids) / Σ(poids)
```

**Exemple chiffré métier.** Panier moyen par magasin et nombre de tickets :

| Magasin | Panier moyen (€) | Nb tickets |
|---|---|---|
| Lille | 40 | 10 000 |
| Valenciennes | 25 | 2 000 |

Moyenne **simple** des paniers : `(40+25)/2 = 32,5 €`. **Trompeur** : Lille pèse 5× plus.
Moyenne **pondérée** par les tickets :
```
(40×10000 + 25×2000) / (10000+2000) = (400000 + 50000) / 12000 = 37,5 €
```
Le panier moyen réel de l'enseigne est **37,5 €**, pas 32,5 €.

**EN PYTHON.**

```python
import numpy as np

paniers = np.array([40, 25])
tickets = np.array([10_000, 2_000])
print(np.average(paniers, weights=tickets))   # 37.5
```

**Erreurs courantes.**
- Faire la moyenne des **moyennes** sans pondérer (c'est l'entrée du paradoxe de Simpson, §4.9).

---

### Moyenne mobile (lissage de séries temporelles)

**Définition.** Remplace chaque point par la **moyenne des N points autour** (ou des N précédents). Lisse le bruit et fait ressortir la **tendance**. Très utilisé sur les ventes journalières, où le bruit week-end/semaine masque le fond.

> 🧠 **Analogie.** La moyenne mobile, c'est des **lunettes anti-tremblement** sur ta courbe : les petits soubresauts du quotidien (gros samedi, lundi mou) disparaissent, et la vraie pente apparaît. Trop fortes (fenêtre trop large), elles floutent aussi les vrais événements.
>
> 🎯 **Ça te servira pour…** lisser une courbe de ventes journalières zigzagantes et montrer au métier « la tendance de fond monte » sans le noyer dans le bruit week-end.

**Formule (moyenne mobile simple sur N périodes).**
```
MM_t = (x_t + x_(t−1) + ... + x_(t−N+1)) / N
```

**Exemple chiffré.** Ventes journalières : `[100, 120, 90, 110, 130, 95, 105]`.
Moyenne mobile sur 3 jours :
- jour 3 : `(100+120+90)/3 = 103,3`
- jour 4 : `(120+90+110)/3 = 106,7`
- jour 5 : `(90+110+130)/3 = 110,0`
La courbe lissée monte régulièrement alors que la brute zigzague.

**EN PYTHON.**

```python
import pandas as pd

ventes = pd.Series([100, 120, 90, 110, 130, 95, 105])
mm3 = ventes.rolling(window=3).mean()       # fenêtre de 3 jours
print(mm3.round(1))
```

> Dans **Looker Studio** / **Power BI**, on ajoute souvent une moyenne mobile pour lisser une courbe de ventes bruitée et montrer la tendance au métier.

**Erreurs courantes.**
- Fenêtre **trop large** : tu lisses tellement que tu écrases les vrais signaux (un pic de soldes disparaît).
- Oublier que les **premiers points** sont vides (`NaN`) tant que la fenêtre n'est pas pleine.
- Présenter la courbe lissée **seule** comme si c'était la donnée réelle, sans la brute en fond.

---

### Agrégations : somme, moyenne, médiane selon le contexte

**Définitions.**
- **Somme** : total. Pour des grandeurs additives (CA, quantités).
- **Moyenne** : total / effectif. Sensible aux **valeurs extrêmes**.
- **Médiane** : valeur du milieu (50 % en dessous, 50 % au-dessus). **Robuste** aux extrêmes.

> 🕵️ **ENQUÊTE n°3 — « Notre panier moyen est de 181 € ! »**
> Le commercial jubile : « Nos clients dépensent en moyenne 181 € ! » Les paniers du jour sont `[20, 25, 30, 32, 800]`. **Repère l'arnaque** : un seul chiffre te saute aux yeux. Quel client réel a dépensé 181 € ? … Aucun. La moyenne est tirée par un gros achat B2B isolé.
>
> 🎲 **Devine avant de calculer.** Le client **typique** de ce jour-là dépense plutôt **30 €** ou **181 €** ? Parie, puis regarde la médiane ci-dessous.

**Exemple chiffré métier.** Paniers : `[20, 25, 30, 32, 800]` (un gros achat B2B).
- Moyenne = `(20+25+30+32+800)/5 = 181,4 €` → ne décrit **aucun** client réel.
- Médiane = `30 €` → décrit bien le client **typique**.

> ✅ **Révélation de l'enquête n°3.** Le client typique dépense **30 €** (la médiane), pas 181 €. La moyenne ment ici parce que la distribution est **asymétrique** (un outlier énorme). Mnémo : *la moyenne est un mauvais joueur de poker — un seul gros tapis et elle bluffe tout le tableau.* Sur des paniers, revenus, prix immobiliers → réflexe **médiane**.

**Règle de décision.**
- Distribution symétrique sans extrêmes → **moyenne** OK.
- Distribution **asymétrique** ou avec outliers (revenus, paniers, prix immobiliers) → **médiane**.
- Tu veux un **total** (CA global) → **somme**, jamais la moyenne.

**EN PYTHON.**

```python
import numpy as np

paniers = np.array([20, 25, 30, 32, 800])
print("Somme   :", paniers.sum())       # 907
print("Moyenne :", paniers.mean())      # 181.4
print("Médiane :", np.median(paniers))  # 30.0
```

**Erreurs courantes.**
- Afficher une **moyenne** sur une distribution asymétrique (le fameux « salaire moyen »).
- **Sommer** des moyennes ou des pourcentages (un % de % n'a pas de sens additif).

---

### Les pièges mathématiques de la dataviz

#### Le paradoxe de Simpson (en intuition)

Une tendance visible dans **chaque sous-groupe** peut **s'inverser** quand on agrège.

> 🕵️ **ENQUÊTE n°4 — « La campagne B est meilleure partout, mais A gagne ! »**
> Deux campagnes pub. La campagne **B convertit mieux sur mobile ET mieux sur desktop**. Pourtant, au total, c'est **A** qui affiche le meilleur taux. **Repère l'arnaque** : où se cache le piège quand « meilleur partout » ≠ « meilleur au total » ?
>
> 🎲 **Devine l'inversion AVANT la révélation.** Sans calculer : crois-tu vraiment qu'un produit peut perdre dans chaque catégorie et gagner au global ? (Spoiler : oui, et c'est contre-intuitif au point d'avoir un nom.) Note ton pari.
>
> ✅ **Révélation.** Oui, c'est possible — c'est le **paradoxe de Simpson**. Une **variable cachée** (ici la répartition du trafic) fausse l'agrégat : A a surtout du trafic mobile, qui convertit mieux pour tout le monde, donc sa moyenne globale grimpe. **Leçon détective : ne conclus jamais sur un total sans segmenter d'abord.** (Détail chiffré juste en dessous.)

**Exemple métier.** Taux de conversion de deux campagnes pub :

| | Campagne A | Campagne B |
|---|---|---|
| Mobile | 8 % (sur 1 000) | 9 % (sur 100) |
| Desktop | 4 % (sur 100) | 5 % (sur 1 000) |
| **Global agrégé** | **~7,6 %** | **~5,4 %** |

B gagne sur mobile **et** sur desktop, mais A gagne au global ! Pourquoi ? A a surtout du trafic mobile (qui convertit mieux), B surtout du desktop. La **structure du trafic** (variable cachée) inverse le résultat.
**Leçon dataviz :** méfie-toi des agrégats. Segmente avant de conclure.

#### La moyenne trompeuse

Voir §4.8 : une moyenne sur une distribution asymétrique ment. Toujours regarder la **distribution** (histogramme, médiane) avant d'afficher une moyenne.

#### Les échelles mensongères

- **Axe tronqué** sur des barres (§4.2).
- **Double axe Y** avec deux échelles arbitraires → on peut faire « coïncider » n'importe quelles courbes.
- **Échelle log non signalée** → croissance modérée présentée comme explosive (ou l'inverse).
- **Aire d'une bulle** proportionnelle au **rayon** au lieu de la **surface** → exagère le ratio.

> 🕵️ **ENQUÊTE n°5 — le double axe & le camembert déformé.**
> a) Le commercial superpose « ventes » et « météo » sur un **double axe Y** : les deux courbes se suivent à merveille. « La pluie booste nos ventes ! » **Repère l'arnaque** : il a réglé chaque axe à sa guise pour faire coller n'importe quoi. ✅ Deux échelles arbitraires peuvent faire « coïncider » des courbes sans aucun lien réel — corrélation visuelle ≠ causalité.
> b) Il te montre un **camembert en perspective 3D incliné** : la part « Lille » à l'avant paraît énorme. **Repère l'arnaque** : la 3D grossit les parts du premier plan. ✅ Un camembert honnête est **plat**, et au-delà de 4-5 parts on préfère un diagramme en barres. Mnémo : *un bon camembert ne se mange pas en 3D.*

**EN PYTHON — illustration du paradoxe de Simpson.**

```python
import pandas as pd

df = pd.DataFrame({
    "campagne": ["A","A","B","B"],
    "support":  ["mobile","desktop","mobile","desktop"],
    "conv":     [80, 4, 9, 50],       # conversions
    "vues":     [1000, 100, 100, 1000],
})

# Par sous-groupe : B est meilleure partout
df["taux"] = df["conv"] / df["vues"]
print(df)

# Agrégé : A repasse devant !
agg = df.groupby("campagne").apply(
    lambda g: g["conv"].sum() / g["vues"].sum()
)
print(agg)   # A ~0.076  >  B ~0.054
```

**Erreurs courantes.**
- Conclure sur un **agrégat global** sans vérifier les sous-groupes.
- Utiliser un **double axe** pour suggérer une corrélation qui n'existe pas.
- Confondre **corrélation visuelle** et causalité.

---

## Vidéos d'auto-formation

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| 200 Countries, 200 Years, 4 Minutes (The Joy of Stats) | BBC | EN | ~5 min | https://www.youtube.com/watch?v=jbkSRLYSojo | Le chef-d'œuvre de Hans Rosling : data animée, échelles et bulles pour raconter 200 ans d'évolution mondiale. Référence absolue de la dataviz pertinente. |
| Calling Bullshit 6.2: Misleading Axes | Carl Bergstrom (Calling Bullshit) | EN | ~10 min | https://www.youtube.com/watch?v=9pNWVMxaFuM | Le piège de l'axe tronqué et des échelles trompeuses, exemples réels décortiqués. Indispensable pour choisir des visualisations pertinentes. |
| How to Lie with Data \| Misleading Graphs | (recherche) | EN | ~10 min | https://www.youtube.com/watch?v=hgp91KvbJV4 | Panorama des graphiques mensongers : axes, surfaces, troncatures — et comment les repérer. |
| L'échelle logarithmique, utilisation et construction | (recherche) | FR | ~15 min | https://www.youtube.com/watch?v=6fMLp5WOx08 | Qu'est-ce qu'une échelle log, comment elle se construit, et quand l'utiliser. En français. |
| StatQuest (chaîne) — Normalization, Standardization, Z-scores | StatQuest with Josh Starmer | EN | varié | https://www.youtube.com/@statquest/search?query=normalization | Min-max, standardisation et z-score expliqués simplement et visuellement. Cherche « normalization » ou « standardization » sur la chaîne. |

> Si un lien direct ne fonctionne plus, utilise la recherche YouTube : par ex. https://www.youtube.com/results?search_query=misleading+graphs+truncated+axis

---

## Exercices

### Exercice 1 — Échelle log ou linéaire ?
Pour chaque cas, dis si tu choisirais une échelle **linéaire** ou **logarithmique** :
a) Comparer le CA de 5 magasins tous entre 480 k€ et 540 k€.
b) Afficher sur un même graphe les ventes d'un produit à 2 € et d'un produit à 5 000 €.
c) Montrer une croissance exponentielle de comptes utilisateurs (100 → 1M en 2 ans).

<details><summary>Corrigé</summary>

a) **Linéaire** : un seul ordre de grandeur, le log compliquerait pour rien.
b) **Log** : ordres de grandeur très différents, le linéaire écrase le petit produit.
c) **Log** : la croissance exponentielle devient une droite, lisible et comparable.
</details>

### Exercice 2 — Axe tronqué
Deux magasins : Lille 102 k€, Roubaix 100 k€. Tu fais un **diagramme en barres** avec un axe de 99 k à 103 k. Quel est le problème ? Quelle correction ?

<details><summary>Corrigé</summary>

L'écart réel est de 2 % seulement, mais avec un axe démarrant à 99 k, la barre de Lille paraît ~2× plus haute → **mensonge visuel**. Sur des barres, l'origine **doit** être à 0. Corrige : `ylim(0, 110000)`. Les deux barres seront quasi identiques, ce qui est honnête.
</details>

### Exercice 3 — Min-max et z-score
Données : `[10, 20, 30, 40, 100]`.
a) Calcule la normalisation min-max.
b) Calcule le z-score de la valeur 100 (écart-type population ≈ 32,0 ; moyenne = 40).
c) Que remarques-tu sur l'effet de l'outlier 100 dans chaque méthode ?

<details><summary>Corrigé</summary>

a) min=10, max=100, étendue=90 → `[0, 0,11, 0,22, 0,33, 1,0]`. L'outlier 100 = 1 écrase les autres vers le bas.
b) `z = (100−40)/32 = 1,875`.
c) En **min-max**, l'outlier devient 1 et compresse toutes les autres valeurs entre 0 et 0,33 → distorsion forte. En **z-score**, l'outlier ressort comme « +1,9 écarts-types » sans écraser les autres → meilleur pour repérer une anomalie.
</details>

### Exercice 4 — Indice base 100 et CAGR
Un magasin : 150 k€ en 2021, 240 k€ en 2024.
a) Indice 2024 (base 100 = 2021).
b) CAGR sur 3 ans.

<details><summary>Corrigé</summary>

a) `240/150 × 100 = 160` → indice 160.
b) `(240/150)^(1/3) − 1 = 1,6^(0,333) − 1 ≈ 0,1696 = 16,96 %` par an.
</details>

### Exercice 5 — Moyenne simple vs pondérée
Trois agences. Taux de satisfaction et nb de répondants :

| Agence | Satisfaction | Répondants |
|---|---|---|
| A | 90 % | 1 000 |
| B | 60 % | 100 |
| C | 70 % | 50 |

Calcule la satisfaction moyenne **simple** puis **pondérée**. Laquelle communiquer ?

<details><summary>Corrigé</summary>

Simple : `(90+60+70)/3 = 73,3 %`.
Pondérée : `(90×1000 + 60×100 + 70×50)/(1150) = (90000+6000+3500)/1150 = 99500/1150 ≈ 86,5 %`.
Communiquer la **pondérée (86,5 %)** : elle reflète l'expérience réelle des répondants, dominée par l'agence A qui a 1 000 réponses.
</details>

### Exercice 6 — Médiane ou moyenne ?
Paniers du jour : `[18, 22, 24, 25, 27, 30, 1 200]`. Le marketing veut afficher « le panier moyen de nos clients ». Quel chiffre choisis-tu et pourquoi ?

<details><summary>Corrigé</summary>

Moyenne = `(18+22+24+25+27+30+1200)/7 ≈ 192,3 €` → tirée par l'achat B2B de 1 200 €, ne décrit aucun client réel.
Médiane = **25 €** (valeur du milieu) → décrit le client typique.
On affiche la **médiane (25 €)**, éventuellement en mentionnant l'outlier à part.
</details>

---

## 🏆 Défi du chapitre — Démasque les 5 graphiques menteurs

Le commercial de la Ch'ti Boutique a préparé 5 slides pour la grande réunion. Chacune contient **exactement un mensonge** vu dans ce chapitre. Avant de cliquer sur la solution, écris pour chaque slide : *quel est le truc, et comment tu le corriges.*

1. **Slide « CA par magasin »** — diagramme en barres, axe Y de 480 k€ à 525 k€. Lille semble écraser tout le monde.
2. **Slide « Croissance de nos produits »** — une courbe est plate au sol, le commercial veut arrêter ce produit. Aucune mention d'échelle sur l'axe.
3. **Slide « Ventes vs météo »** — deux courbes sur un double axe Y qui se suivent parfaitement. « La pluie fait vendre. »
4. **Slide « Répartition des ventes »** — un camembert en 3D incliné où la part avant paraît géante.
5. **Slide « Panier moyen client »** — un gros « 181 € » en titre, calculé sur `[20, 25, 30, 32, 800]`.

<details><summary>🔓 Solution du détective</summary>

1. **Axe tronqué** (§4.2). L'écart réel est ~5 %, pas ×2. Correction : `ylim` débute à **0**.
2. **Échelle log cachée / linéaire trompeuse** (§4.1). Le petit produit paraît plat parce que l'axe linéaire est écrasé par le gros. Correction : passer l'axe Y en **log** (et l'indiquer) → le produit « plat » est en fait le plus dynamique.
3. **Double axe trompeur** (§4.9). Deux échelles réglées sur mesure font coïncider n'importe quoi. Corrélation visuelle ≠ causalité. Correction : une seule échelle, ou un vrai test de corrélation, ou normalisation (indice base 100) avant de comparer.
4. **Camembert déformé** (§4.9). La 3D grossit le premier plan. Correction : camembert **plat**, ou mieux un **diagramme en barres** au-delà de 4-5 parts.
5. **Moyenne qui cache tout** (§4.8). L'outlier B2B à 800 € gonfle la moyenne. Le client typique = **médiane = 30 €**. Correction : afficher la **médiane**, signaler l'outlier à part.

🎉 5/5 ? Tu es officiellement **détective des graphiques menteurs**. C'est exactement l'art de choisir des visualisations pertinentes.
</details>

---

## Quiz (5 QCM)

**Q1.** Sur un **diagramme en barres**, l'axe vertical doit commencer à :
a) la valeur minimale des données
b) zéro
c) la moyenne
d) n'importe quelle valeur, ça n'a pas d'importance

**Q2.** La **standardisation z-score** transforme les données pour qu'elles aient :
a) un minimum de 0 et un maximum de 1
b) une moyenne de 0 et un écart-type de 1
c) une somme de 100
d) une médiane de 0

**Q3.** Un CA passe de 100 k€ à 144 k€ en 2 ans. Le **CAGR** est :
a) 22 %
b) 44 %
c) 20 %
d) 12 %

**Q4.** Le **paradoxe de Simpson** signifie que :
a) la moyenne est toujours fausse
b) une tendance dans chaque sous-groupe peut s'inverser une fois agrégée
c) le log ment toujours
d) la médiane est meilleure que la moyenne

**Q5.** Pour comparer sur un même graphe les **évolutions** d'un produit à 2 € et d'un produit à 5 000 €, tu utilises :
a) une moyenne mobile
b) un axe tronqué
c) une échelle logarithmique (ou un indice base 100)
d) une moyenne pondérée

<details><summary>Réponses</summary>

**Q1 : b** — sur des barres, la surface code la valeur, l'origine doit être 0.
**Q2 : b** — z-score = centré (moyenne 0), réduit (écart-type 1). Le min-max, lui, borne en [0,1].
**Q3 : c** — `(144/100)^(1/2) − 1 = 1,44^0,5 − 1 = 1,2 − 1 = 20 %`.
**Q4 : b** — l'agrégation peut inverser la tendance à cause d'une variable cachée (structure des groupes).
**Q5 : c** — log ou indice base 100 ramènent des ordres de grandeur différents sur une base comparable.
</details>

---

## À retenir

- **Échelle log** quand les données couvrent plusieurs ordres de grandeur ou quand le **taux de croissance** compte. Toujours l'**indiquer** sur l'axe.
- **Barres → origine à zéro, toujours.** L'axe tronqué est le mensonge n°1 de la dataviz.
- **Normaliser (min-max, [0,1])** ≠ **standardiser (z-score, centré-réduit)**. Min-max pour comparer/afficher, z-score pour détecter les anomalies. Le min-max craint les outliers.
- **Indice base 100** pour comparer des **évolutions** de grandeurs de tailles différentes.
- **CAGR = moyenne géométrique** : `(fin/début)^(1/n) − 1`. On ne fait **jamais** la moyenne arithmétique de taux de croissance.
- **Moyenne pondérée** dès que les groupes ont des tailles différentes.
- **Moyenne mobile** pour lisser le bruit d'une série temporelle — sans cacher la donnée brute.
- **Médiane** plutôt que moyenne sur les distributions **asymétriques** (paniers, revenus).
- **Paradoxe de Simpson** : segmente avant de conclure sur un agrégat.
- Une viz honnête = bon choix d'**échelle**, d'**origine**, d'**agrégation**. C'est ça, choisir des visualisations pertinentes.

> 🕵️ **Le serment du détective des graphiques.** *Avant d'envoyer un graphe : « Mon axe de barres part-il de 0 ? Mon échelle est-elle annoncée ? Ma moyenne cache-t-elle un outlier ? Mon total cache-t-il une inversion de Simpson ? Mon double axe ment-il ? »* Si tu te poses ces 5 questions à chaque dashboard, tu ne te feras plus jamais avoir — et tu ne feras plus jamais avaler une décision business sur une illusion d'optique à ton patron de la Ch'ti Boutique. 🎬
