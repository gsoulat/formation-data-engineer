# 05 — Statistique inférentielle

> **Formation Data Analyst**
> **Objectif : Identifier et interpréter des tendances**
> Module : Mathématiques pour la donnée · Niveau : remise à niveau, accessible

---

## 🎬 L'histoire : sondage à la Ch'ti Boutique

> **Lundi matin, la Ch'ti Boutique (notre fil rouge).** La patronne débarque, café à la main : *« J'ai un million de clients dans mon fichier. Je veux savoir s'ils sont contents… mais je ne vais pas appeler un million de personnes ! »*
>
> Tu sors ton téléphone, tu interroges **600 clients au hasard** à la sortie du magasin. **468 disent « content ».** Soit 78 %.
>
> La patronne veut imprimer sur la vitrine : **« 78 % de nos clients sont satisfaits ! »**
>
> Et là, ton réflexe d'analyste s'allume : *« Attends… 78 % sur 600 personnes. Sur le million, c'est peut-être 75 %, peut-être 81 %. Je n'ai pas le droit d'affirmer un chiffre sec. »*
>
> **C'est exactement ça, la statistique inférentielle :** deviner ce que pense TOUT le monde à partir d'un PETIT groupe — et savoir dire **à quel point** on peut y faire confiance. Tout ce chapitre tient dans ce café du lundi matin. ☕

---

## Présentation

Jusqu'ici (chapitre statistique descriptive), tu as appris à **décrire** un jeu de données : moyenne, médiane, écart-type, histogramme. Tu décrivais ce que tu avais **sous les yeux**.

La statistique **inférentielle** fait un pas de plus : à partir d'un **petit échantillon**, elle te permet de **tirer des conclusions sur un ensemble beaucoup plus grand** (toute ta clientèle, tout un marché, tous les visiteurs d'un site). C'est exactement ce qu'on te demandera en tant que Data Analyst : « D'après ce sondage de 600 clients, peux-tu nous dire si **tous** nos clients sont satisfaits ? »

Ce chapitre est volontairement **léger** : pas de démonstrations lourdes, mais l'**intuition** juste et les **réflexes métier** indispensables. Le message le plus important du chapitre — celui qui te fera respecter comme analyste — tient en trois mots : **corrélation ≠ causalité**.

---

## Objectifs

À la fin de ce chapitre, tu sauras :

- Distinguer une **population** d'un **échantillon**, et reconnaître les **biais d'échantillonnage**.
- Comprendre ce qu'est une **estimation** et l'**erreur d'échantillonnage**.
- Lire et calculer (cas simple) un **intervalle de confiance** sur une proportion (ex. un taux de satisfaction).
- Comprendre l'**intuition** d'un test d'hypothèse : H0 / H1, p-value, seuil de 5 %.
- Calculer et interpréter un **coefficient de corrélation** (Pearson et Spearman).
- Construire et lire un **nuage de points**.
- **Ne jamais confondre corrélation et causalité**, et repérer les **corrélations fallacieuses**.
- Faire tout cela **en Python** avec `pandas`, `scipy.stats` et `seaborn`.

---

## Pourquoi c'est utile au Data Analyst

Tu n'analyseras presque jamais la donnée de **100 % de la population** : c'est trop cher, trop long, parfois impossible. Tu travailles sur des **échantillons** (un sondage, un mois de ventes, un panel de testeurs). L'inférence te dit **jusqu'où tu as le droit de généraliser**.

Trois situations très concrètes du métier :

1. **Sondage de satisfaction.** « 78 % des 600 clients interrogés sont satisfaits. » Le marketing veut écrire « 78 % de nos clients sont satisfaits » sur la plaquette. Toi, tu sais qu'il faut dire **« entre 74,7 % et 81,3 % avec 95 % de confiance »**. C'est l'intervalle de confiance qui te protège juridiquement et professionnellement.

2. **A/B test.** Tu testes deux versions d'une page produit. La version B convertit à 5,2 %, la A à 4,8 %. Est-ce une **vraie** amélioration ou juste du **hasard** ? C'est le test d'hypothèse (et la p-value) qui tranche.

3. **Relation entre deux variables.** « Quand on baisse le prix, les ventes montent-elles vraiment ? » « La météo influence-t-elle le panier moyen ? » C'est la corrélation. Et c'est là que tu dois garder la tête froide : **ce n'est pas parce que deux courbes montent ensemble que l'une cause l'autre.**

> En entretien et en mission, ce qui distingue un bon analyste d'un débutant, ce n'est pas de savoir calculer un coefficient — Python le fait. C'est de savoir **dire ce qu'il ne prouve pas**.

---

### 🎯 « Ça te servira pour… » — la traduction métier des 3 mots compliqués

Ce chapitre a 3 mots qui font peur. Voici à quoi ils servent VRAIMENT au quotidien :

| Mot savant | En clair | Tu t'en sers quand… |
|---|---|---|
| **Intervalle de confiance (IC)** | La **fourchette** où se cache la vraie valeur. « 78 % ±3 points. » | Tu rends un sondage client et tu dois donner une **marge d'erreur** (comme à la télé pendant les élections). |
| **p-value** | « Est-ce un **vrai effet** ou juste un coup de chance ? » | Tu compares deux versions d'une page web (A/B test) et tu dois dire si la nouvelle est **vraiment** meilleure. |
| **Corrélation** | Deux trucs qui **bougent ensemble** (prix et ventes, météo et panier moyen). | Tu cherches des **liens** dans tes données… **sans conclure trop vite** que l'un cause l'autre. |

Retiens juste ça pour l'instant. Le reste du chapitre, c'est du détail pour bien manier ces trois outils.

---

## Les notions

### Population vs échantillon

**Définition.**
- La **population** : l'ensemble **complet** des individus/objets qui t'intéressent (ex. *tous* les clients du magasin Auchan de Villeneuve-d'Ascq sur l'année).
- L'**échantillon** : un **sous-ensemble** de cette population, celui que tu observes réellement (ex. les 600 clients interrogés à la sortie).

On utilise des notations différentes selon le niveau :

| | Population | Échantillon |
|---|---|---|
| Taille | N | n |
| Moyenne | μ (mu) | x̄ (« x barre ») |
| Proportion | p | p̂ (« p chapeau ») |
| Écart-type | σ (sigma) | s |

Les lettres **grecques** (μ, σ, p) désignent les valeurs **vraies mais inconnues** de la population. Les lettres latines (x̄, s, p̂) désignent ce qu'on **calcule sur l'échantillon**. Tout le jeu de l'inférence : **estimer μ ou p à partir de x̄ ou p̂.**

**Exemple chiffré métier.**
Un e-commerçant du Nord (vente de vêtements en ligne) a 120 000 clients (= population, N = 120 000). Il interroge 600 d'entre eux (= échantillon, n = 600). 468 se disent satisfaits.
→ Proportion observée dans l'échantillon : p̂ = 468 / 600 = **0,78 = 78 %**.
On veut en déduire **p**, le taux de satisfaction réel des 120 000 clients.

**Erreurs courantes.**
- Confondre N (population) et n (échantillon).
- Prendre le taux de l'échantillon (78 %) pour la vérité absolue sur toute la population.

---

### Échantillonnage et biais

**Définition.**
Un bon échantillon doit être **représentatif** de la population : sa composition (âge, sexe, type d'achat…) doit ressembler à celle de la population. La meilleure garantie est l'**échantillon aléatoire** : chaque individu a la **même chance** d'être choisi.

Un **biais d'échantillonnage** survient quand certains profils sont sur- ou sous-représentés. Le résultat est alors faux, **même avec un énorme échantillon**.

**Exemples de biais (à connaître par cœur) :**

| Biais | Description | Exemple métier |
|---|---|---|
| **Biais de sélection** | L'échantillon n'est pas tiré au hasard | Sondage de satisfaction envoyé **uniquement par email** → on rate les clients âgés peu connectés |
| **Biais de non-réponse** | Seuls certains répondent | Seuls les clients **très contents** ou **très fâchés** prennent le temps de répondre → résultats polarisés |
| **Biais du survivant** | On n'observe que les « survivants » | Analyser la satisfaction des clients **actuels** en oubliant ceux qui sont **partis** (les plus insatisfaits, justement) |
| **Biais de couverture** | La base interrogée ne couvre pas tout le monde | Sonder en magasin à 14h en semaine → on rate les actifs qui viennent le samedi |

**Le mythe à casser :** un gros échantillon **biaisé** est PIRE qu'un petit échantillon **aléatoire**. La taille ne corrige jamais le biais.

**Exemple historique célèbre :** en 1936, un magazine américain (*Literary Digest*) a interrogé **2,4 millions** de personnes pour prédire l'élection présidentielle… et s'est trompé lourdement, car son fichier (propriétaires de téléphone et d'automobile) sur-représentait les riches. Gallup, avec **50 000** personnes bien tirées au sort, a eu juste.

**Erreurs courantes.**
- Croire que « beaucoup de répondants » = « résultat fiable ».
- Oublier ceux qui ne répondent pas (les silencieux disent souvent autre chose).

---

### Estimation et erreur d'échantillonnage

**Définition.**
**Estimer**, c'est utiliser la valeur de l'échantillon (p̂ = 78 %) comme **meilleure approximation** de la valeur inconnue de la population (p). Mais cette estimation n'est jamais parfaite : si tu interrogeais **600 autres** clients, tu obtiendrais peut-être 76 % ou 80 %. Cette variation naturelle d'un échantillon à l'autre s'appelle l'**erreur d'échantillonnage** (ou fluctuation d'échantillonnage).

**L'idée clé :** plus l'échantillon est **grand**, plus l'erreur d'échantillonnage est **petite**. Mais attention — elle diminue en **√n** (racine de n), pas en n. Pour diviser l'erreur par 2, il faut multiplier la taille de l'échantillon par **4**.

**Erreur courante.**
- Penser qu'on supprime l'erreur d'échantillonnage en augmentant n. On la **réduit**, on ne l'efface jamais. Et elle ne corrige **pas** le biais (deux choses différentes : le biais te trompe systématiquement dans une direction ; l'erreur d'échantillonnage est le bruit aléatoire autour de la vraie valeur).

---

### Intervalle de confiance (IC)

> 🧠 **Analogie du pêcheur.** La vraie valeur (le taux de satisfaction de TOUS tes clients) est un **poisson** que tu ne vois pas. Tu lances un **filet** (= ton intervalle). Un IC à 95 %, c'est un filet construit de telle façon que **si tu pêchais 100 fois, 95 fois le poisson serait dedans**. Tu ne sais pas si CE filet-ci l'a attrapé, mais ta méthode marche 95 fois sur 100.
>
> **Mnémo :** *IC = la fourchette dans laquelle se cache la vraie valeur.* 🍴

**Définition (intuition).**
Plutôt que d'annoncer une seule valeur (« 78 % »), on annonce une **fourchette** qui a de **grandes chances** de contenir la vraie valeur p. Un **intervalle de confiance à 95 %** signifie, en gros : *« si je répétais mon sondage un grand nombre de fois, 95 % des fourchettes que je construirais contiendraient la vraie valeur. »*

En pratique métier, on le lit simplement : **« On est à 95 % confiants que le vrai taux de satisfaction est entre 74,7 % et 81,3 %. »**

**Formule (cas d'une proportion, le cas le plus fréquent en sondage).**

$$ IC_{95\%} = \hat{p} \pm 1{,}96 \times \sqrt{\frac{\hat{p}\,(1-\hat{p})}{n}} $$

- p̂ : proportion observée dans l'échantillon
- n : taille de l'échantillon
- **1,96** : la valeur magique pour un niveau de confiance de **95 %** (pour 90 % ce serait 1,645 ; pour 99 %, 2,576)
- La partie après le ± s'appelle la **marge d'erreur**.

**Calcul à la main (exemple satisfaction).**
p̂ = 0,78, n = 600.

1. Numérateur sous la racine : 0,78 × (1 − 0,78) = 0,78 × 0,22 = 0,1716
2. Divisé par n : 0,1716 / 600 = 0,000286
3. Racine carrée : √0,000286 ≈ 0,0169
4. × 1,96 : 1,96 × 0,0169 ≈ **0,0331** → marge d'erreur ≈ **3,3 points**
5. IC : 0,78 ± 0,033 → **[0,747 ; 0,813]** soit **[74,7 % ; 81,3 %]**

**Conclusion métier :** « 78 % de clients satisfaits, marge d'erreur ±3,3 points (IC 95 %). »

**En Python.**

```python
import numpy as np
from scipy import stats

p_hat = 0.78
n = 600

# Méthode "à la main"
marge = 1.96 * np.sqrt(p_hat * (1 - p_hat) / n)
ic_bas, ic_haut = p_hat - marge, p_hat + marge
print(f"Taux estimé : {p_hat:.1%}")
print(f"Marge d'erreur : ±{marge:.1%}")
print(f"IC 95% : [{ic_bas:.1%} ; {ic_haut:.1%}]")

# Méthode avec statsmodels (recommandée en production)
from statsmodels.stats.proportion import proportion_confint
nb_satisfaits = 468
bas, haut = proportion_confint(count=nb_satisfaits, nobs=n, alpha=0.05, method="normal")
print(f"IC 95% (statsmodels) : [{bas:.1%} ; {haut:.1%}]")
```

**Interprétation.**
- Plus n est grand → IC plus **étroit** → estimation plus **précise**.
- Plus on veut être confiant (99 % au lieu de 95 %) → IC plus **large**.
- L'IC ne dit **rien** sur le biais ! Un sondage biaisé donne un IC précis… autour d'une mauvaise valeur.

**Erreurs courantes.**
- Dire « il y a 95 % de chances que la vraie valeur soit dans CET intervalle ». Formulation tolérée en vulgarisation, mais techniquement la vraie valeur est fixe ; c'est l'intervalle qui est aléatoire. Pour le métier, dire **« on est confiants à 95 % »** suffit.
- Annoncer « 78 % » sans la marge d'erreur. Un taux sans marge n'a aucune valeur scientifique.

---

### Introduction aux tests d'hypothèses

**Définition (intuition).**
Un test d'hypothèse répond à : *« Ce que j'observe est-il un vrai effet, ou juste du hasard ? »*

On pose toujours **deux hypothèses opposées** :
- **H0 (hypothèse nulle)** : « il ne se passe rien », « pas de différence », « le statu quo ». C'est l'hypothèse qu'on cherche à **rejeter**.
- **H1 (hypothèse alternative)** : « il se passe quelque chose », « il y a une différence ». C'est ce qu'on **espère souvent** montrer.

**Analogie du tribunal :** H0 = « l'accusé est innocent » (présumé vrai par défaut). On ne le condamne (rejet de H0) que si les **preuves sont assez fortes**. L'absence de condamnation ne prouve pas l'innocence : juste qu'on n'a pas assez de preuves.

**La p-value, version « pile ou face truqué ».**

Imagine que ton copain dit : *« cette pièce est normale »* (= H0, « rien d'anormal »). Tu la lances **10 fois → 10 fois pile.** Tu te dis : *« si la pièce était vraiment normale, sortir 10 piles d'affilée serait HYPER improbable… donc je ne crois plus à "elle est normale". »*

Cette petite probabilité — *« quelle chance d'obtenir un résultat aussi extrême SI rien d'anormal ? »* — **c'est la p-value.**

- p-value **minuscule** → « ce serait trop dingue par pur hasard » → tu **rejettes H0** (il se passe vraiment un truc).
- p-value **grande** → « bah, ça arrive facilement par hasard » → tu **ne conclus rien**.

> 🧠 **Mnémo :** **p-value < 5 % = « trop beau pour être un hasard »** → tu y crois. p-value ≥ 5 % = « ça peut très bien être de la chance » → tu te méfies.
>
> ⚠️ **Le piège mortel à NE PAS faire :** la p-value n'est **PAS** « la probabilité que H0 soit vraie ». Elle *part du principe* que H0 est vraie, puis mesure à quel point tes données seraient surprenantes dans ce monde-là. Sens unique, jamais l'inverse.

**La p-value (définition exacte).**
La **p-value** est la probabilité d'observer un résultat **au moins aussi extrême** que le tien **si H0 était vraie** (= si tout était dû au hasard).

- **p-value petite** (proche de 0) → ce que tu observes serait **très improbable** par pur hasard → tu **rejettes H0** (« il se passe vraiment quelque chose »).
- **p-value grande** → ton résultat est **compatible avec le hasard** → tu **ne rejettes pas H0**.

**Le seuil de 5 % (α = 0,05).**
Par convention, on fixe un seuil **α = 0,05** :
- **p-value < 0,05** → résultat « **statistiquement significatif** » → on rejette H0.
- **p-value ≥ 0,05** → on ne rejette pas H0.

**Exemple métier : A/B test.**
Un site e-commerce teste deux pages produit.
- Page A (actuelle) : 4,8 % de conversion.
- Page B (nouvelle) : 5,2 % de conversion.

- **H0** : les deux pages convertissent pareil (la différence est due au hasard).
- **H1** : les deux pages ne convertissent pas pareil.

```python
import numpy as np
from scipy import stats

# Conversions observées
# Page A : 480 conversions sur 10 000 visiteurs
# Page B : 520 conversions sur 10 000 visiteurs
from statsmodels.stats.proportion import proportions_ztest

conversions = np.array([480, 520])
visiteurs   = np.array([10000, 10000])

stat, p_value = proportions_ztest(count=conversions, nobs=visiteurs)
print(f"p-value = {p_value:.3f}")

if p_value < 0.05:
    print("Significatif : la page B fait une vraie différence. On garde B.")
else:
    print("Non significatif : la différence peut être due au hasard. On ne tranche pas.")
```

**Interprétation prudente.**
- « Significatif » ne veut **pas** dire « gros effet ». Avec un échantillon énorme, une différence minuscule et sans intérêt business peut être « significative ».
- p ≥ 0,05 ne **prouve pas** que H0 est vraie. Ça veut juste dire « pas assez de preuves pour la rejeter ».

**Erreurs courantes (les plus fréquentes en entreprise !).**
- **Lire la p-value comme « la probabilité que H0 soit vraie ».** FAUX. La p-value suppose H0 vraie au départ ; elle ne calcule pas sa probabilité.
- Arrêter l'A/B test « dès qu'on voit p < 0,05 » (le *peeking*) : ça gonfle artificiellement les faux positifs. On fixe la durée du test **à l'avance**.
- Confondre **significativité statistique** et **importance métier**.

---

### Corrélation : nuage de points, Pearson, Spearman

**Définition.**
La **corrélation** mesure si **deux variables varient ensemble**, et dans quel sens.

Le **coefficient de corrélation** est un nombre **entre −1 et +1** :

| Valeur | Signification |
|---|---|
| **+1** | corrélation positive parfaite (quand l'un monte, l'autre monte, parfaitement aligné) |
| **+0,7 à +0,9** | forte corrélation positive |
| **0** | aucune corrélation linéaire |
| **−0,7 à −0,9** | forte corrélation négative (l'un monte, l'autre descend) |
| **−1** | corrélation négative parfaite |

**Le nuage de points (scatter plot).** AVANT tout calcul, on **dessine** : chaque point = un individu, en abscisse une variable, en ordonnée l'autre. C'est le réflexe n°1 de l'analyste.

> 🎲 **Devine avant de calculer — « lis le nuage à l'œil ».** Pas besoin de Python pour deviner le coefficient ! Entraîne ton œil :
>
> ```
>  (A) points qui montent      (B) nuage en patate        (C) points qui descendent
>      en ligne                    sans direction              en ligne
>        •                          •   •  •                          •
>      •                         •  •   •                              •
>    •                              •  •   •                              •
>  •                            •  •  •                                     •
>  → r proche de +1            → r proche de 0             → r proche de −1
> ```
>
> Avant chaque calcul, **parie** : « je dirais r ≈ +0,8 ». Puis vérifie avec Python. En 10 essais ton œil sera calibré — et tu repéreras d'un coup d'œil les nuages où le chiffre seul mentirait (relation en U, outlier isolé). C'est ça, le métier.

**Pearson vs Spearman.**

- **Pearson (r)** : mesure une relation **linéaire** (en ligne droite). Sensible aux valeurs extrêmes. À utiliser quand la relation a l'air droite et les variables sont numériques.
- **Spearman (ρ, « rho »)** : mesure une relation **monotone** (qui va toujours dans le même sens, même si elle est courbée). Calculé sur les **rangs**, donc robuste aux valeurs extrêmes et aux relations non linéaires. À utiliser en cas de doute, d'outliers, ou de variables ordinales (notes, classements).

**Exemple chiffré métier : prix vs quantités vendues.**
Une boutique du Nord relève, sur 8 semaines, le prix moyen d'un produit et le nombre d'unités vendues :

| Semaine | Prix (€) | Ventes (unités) |
|---|---|---|
| 1 | 20 | 100 |
| 2 | 22 | 92 |
| 3 | 19 | 110 |
| 4 | 25 | 80 |
| 5 | 21 | 95 |
| 6 | 24 | 85 |
| 7 | 18 | 120 |
| 8 | 23 | 88 |

On s'attend à une corrélation **négative** : plus le prix monte, moins on vend.

**Formule (Pearson).**

$$ r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2}\;\sqrt{\sum (y_i - \bar{y})^2}} $$

Au numérateur, la **covariance** (varient-ils ensemble ?) ; au dénominateur, le produit des écarts-types (pour ramener le résultat entre −1 et +1).

**Calcul à la main (extrait, principe).**
1. Calculer x̄ (prix moyen) et ȳ (ventes moyennes). Ici x̄ = 21,5 €, ȳ = 96,25.
2. Pour chaque semaine, calculer (xᵢ − x̄) et (yᵢ − ȳ).
3. Multiplier les deux écarts et tout sommer → numérateur (sera **négatif** car quand le prix est au-dessus de la moyenne, les ventes sont en dessous).
4. Calculer les deux sommes de carrés, prendre les racines, multiplier → dénominateur.
5. Diviser. On obtient ici **r ≈ −0,98** : très forte corrélation négative.

(En pratique, on ne fait jamais ce calcul à la main au-delà de l'exercice pédagogique — Python s'en charge.)

**En Python.**

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

df = pd.DataFrame({
    "prix":   [20, 22, 19, 25, 21, 24, 18, 23],
    "ventes": [100, 92, 110, 80, 95, 85, 120, 88],
})

# 1) Réflexe n°1 : on DESSINE le nuage de points + droite de régression
sns.regplot(data=df, x="prix", y="ventes")
plt.title("Prix vs ventes")
plt.show()

# 2) Matrice de corrélation (Pearson par défaut)
print(df.corr())                  # ou df.corr(method="pearson")
print(df.corr(method="spearman")) # version sur les rangs

# 3) Coefficient + p-value (la corrélation est-elle significative ?)
r, p = stats.pearsonr(df["prix"], df["ventes"])
print(f"Pearson r = {r:.2f}  (p-value = {p:.4f})")

rho, p_s = stats.spearmanr(df["prix"], df["ventes"])
print(f"Spearman rho = {rho:.2f}  (p-value = {p_s:.4f})")

# Bonus : heatmap visuelle pour un dataset avec plein de colonnes
sns.heatmap(df.corr(), annot=True, cmap="coolwarm", center=0)
plt.show()
```

**Interprétation.**
- r ≈ −0,98 → forte relation négative : le prix et les ventes évoluent en sens inverse. Logique business.
- La **p-value** associée dit si cette corrélation est significative (peu probable d'arriver par hasard).
- Pour visualiser plusieurs variables d'un coup : `df.corr()` + `sns.heatmap`.

**Erreurs courantes.**
- Calculer r **sans dessiner le nuage** : un r de 0 peut cacher une belle relation **en U** (Pearson ne voit que les droites). Inversement, **un seul outlier** peut créer ou détruire une corrélation. **Dessine toujours.**
- Utiliser Pearson sur des données très non linéaires ou pleines d'outliers (préfère Spearman).
- Et surtout… la section suivante.

---

### LE message crucial : corrélation ≠ causalité 🎯 (le passage le plus fun du chapitre)

> 🎲 **Devine avant de lire : vraie cause ou coïncidence bidon ?**
> Pour chacune, parie « LIEN RÉEL » ou « N'IMPORTE QUOI » avant de regarder la réponse :
>
> 1. Plus il y a de **pompiers** sur un incendie, plus les **dégâts** sont importants. 🔥
> 2. Les villes avec beaucoup d'**églises** ont beaucoup de **crimes**. ⛪
> 3. Les enfants avec de **grands pieds** lisent mieux. 👟📖
>
> <details><summary>Révéler les réponses</summary>
>
> **Aucune n'est un vrai lien de cause à effet !** À chaque fois, une **3ᵉ variable cachée** tire les ficelles :
> 1. La **taille de l'incendie** → fait venir plus de pompiers ET cause plus de dégâts. (Ce ne sont pas les pompiers qui détruisent la maison !)
> 2. La **taille de la ville** → grande population = plus d'églises ET plus de crimes.
> 3. L'**âge** → un enfant plus âgé a de plus grands pieds ET lit mieux.
>
> Cette 3ᵉ variable cachée porte un nom : la **variable confondante**. C'est l'ennemie n°1 de l'analyste. </details>

**Définition.**
Deux variables peuvent être **fortement corrélées** sans qu'aucune ne **cause** l'autre. C'est l'erreur la plus dangereuse — et la plus fréquente — du métier.

**Trois explications possibles d'une corrélation A–B :**
1. A cause B (causalité directe).
2. B cause A (causalité inverse).
3. **Une troisième variable C cause A *et* B** (variable confondante). ← la plus piégeuse.
4. Ou… **pur hasard** (coïncidence, surtout quand on teste plein de variables).

**Exemple métier (variable confondante) :**
Tu observes que **les ventes de crème solaire** et **les ventes de glaces** sont très corrélées dans tes magasins. La crème solaire fait-elle vendre des glaces ? Non. La variable cachée, c'est la **chaleur / l'ensoleillement** : elle pousse à acheter les deux. C est la cause commune.

**Exemple métier (causalité inverse) :**
« Les magasins avec le plus de vendeurs ont le plus de chiffre d'affaires. » Embaucher plus de vendeurs fait-il monter le CA… ou bien les magasins à fort CA ont-ils simplement les moyens d'embaucher plus ? Les deux sens sont plausibles : la corrélation ne tranche pas.

**Exemples de fausses corrélations (pour rire et comprendre) :**
Le site *Spurious Correlations* de Tyler Vigen compile des corrélations **absurdes mais bien réelles** mathématiquement :
- Le nombre de films avec Nicolas Cage corrélé au nombre de noyades dans des piscines.
- La consommation de fromage par personne corrélée au nombre de gens morts étranglés dans leurs draps.
- Le taux de divorce dans le Maine corrélé à la consommation de margarine.

Personne ne pense que Nicolas Cage provoque des noyades. Ces exemples sont là pour graver en toi le réflexe : **un beau coefficient ne prouve JAMAIS un lien de cause à effet.**

> 🎲 **Mini-jeu « trouve la vraie cause cachée ».** Pour chaque corrélation bidon, devine la variable confondante :
>
> | Corrélation observée (réelle !) | La vraie cause cachée, c'est… |
> |---|---|
> | Ventes de **glaces** ↑ et **noyades** ↑ | <details><summary>?</summary>La **chaleur de l'été** : il fait chaud → on mange des glaces ET on se baigne (donc plus de noyades).</details> |
> | Plus de **pirates** dans le monde = planète moins chaude (avant) | <details><summary>?</summary>Le **temps qui passe** : les pirates ont disparu pendant que l'industrialisation réchauffait le climat. Deux tendances parallèles, zéro lien.</details> |
> | Pays qui mangent beaucoup de **chocolat** ont plus de **prix Nobel** | <details><summary>?</summary>La **richesse du pays** : un pays riche peut s'offrir chocolat ET universités/recherche.</details> |
>
> **Réflexe à graver :** dès que tu vois deux courbes monter ensemble, demande-toi *« quelle 3ᵉ chose pourrait expliquer les deux ? »*

**Comment établir une causalité, alors ?**
On ne peut PAS la prouver avec une simple corrélation observée. Il faut :
- une **expérience contrôlée / randomisée** (ex. un vrai A/B test où on assigne les visiteurs au hasard),
- ou des méthodes statistiques avancées qui dépassent ce cours.

**Ce que tu dois écrire dans un rapport :**
- ✅ « On observe une **forte corrélation** (r = −0,98) entre le prix et les ventes. »
- ✅ « Cette corrélation **suggère** une piste à explorer. »
- ❌ « La hausse du prix **a causé** la baisse des ventes. » (sauf si tu l'as démontré par une expérience)

**Erreurs courantes.**
- Présenter une corrélation comme une preuve de cause à effet dans une réunion de direction → décision business potentiellement coûteuse et fausse.
- Oublier les variables confondantes (la cause cachée).
- Tester 50 variables, en trouver une « significative » par hasard, et y croire (multiplication des tests → faux positifs).

---

## 🏆 Défi du chapitre — « Démasque les 3 intrus »

> La patronne de la **Ch'ti Boutique** a fait analyser ses données par un stagiaire pressé. Il revient avec **6 affirmations**. **3 sont des pièges classiques** (corrélation prise pour causalité, p-value mal lue, IC oublié). À toi de **démasquer les 3 intrus** et de dire pourquoi.
>
> 1. *« Les jours où on vend plus de parapluies, le café se vend mieux. Mettons des parapluies près de la machine à café pour booster le café ! »*
> 2. *« 64 % des 500 clients sondés veulent le rayon bio. On l'écrit : entre 60 % et 68 % (IC 95 %). »*
> 3. *« L'A/B test sur la newsletter donne p = 0,40. Donc il y a 40 % de chances que les deux versions soient identiques. »*
> 4. *« On a un échantillon aléatoire de 800 clients, marge d'erreur ±3,5 points. »*
> 5. *« Les magasins avec le plus de plantes vertes ont le plus de chiffre d'affaires. Achetons des plantes pour tous les magasins ! »*
> 6. *« p = 0,01 sur le nouveau bouton "Acheter" rouge : c'est significatif, le rouge convertit mieux. »*
>
> <details><summary>🎖️ Voir qui sont les 3 intrus</summary>
>
> **Affirmations CORRECTES : 2, 4, 6.** (Sondage avec IC bien posé ✅ · échantillon aléatoire + marge d'erreur ✅ · p < 0,05 = significatif ✅.)
>
> **Les 3 INTRUS :**
> - **❌ n°1 — Corrélation ≠ causalité.** Parapluies et café montent ensemble à cause d'une **variable cachée** : le mauvais temps (on reste, on traîne, on consomme). Les parapluies ne *causent* pas le café.
> - **❌ n°3 — p-value mal lue.** p = 0,40 n'est **PAS** « 40 % de chances qu'elles soient identiques ». C'est la proba d'observer une telle différence **si** elles étaient identiques. Et 0,40 ≥ 0,05 → on ne conclut **rien** (pas de preuve d'effet).
> - **❌ n°5 — Causalité inverse / variable confondante.** Ce sont sûrement les magasins déjà **riches** (gros CA, dans de beaux quartiers) qui s'offrent des plantes. Acheter des plantes ne créera pas de CA.
>
> **Score : 3/3 ?** Tu as le réflexe d'or du Data Analyst. 🥇 </details>

---

## Vidéos d'auto-formation

> Toutes les vidéos ci-dessous ont été vérifiées. Les chaînes StatQuest (Josh Starmer), Yvan Monka et Tyler Vigen sont des références reconnues. Quand un lien direct n'est pas garanti, un lien de recherche YouTube est fourni.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Confidence Intervals, Clearly Explained!!! | StatQuest (Josh Starmer) | EN | ~7 min | https://www.youtube.com/watch?v=TqOeMYtOc1w | L'intuition de l'intervalle de confiance via le bootstrapping, sans formule lourde |
| Hypothesis Testing and The Null Hypothesis + p-values | StatQuest (Josh Starmer) | EN | ~14 min | https://www.youtube.com/results?search_query=statquest+hypothesis+testing+null+hypothesis+p-value | H0/H1, ce qu'est vraiment une p-value et comment l'interpréter |
| Covariance and Correlation Part 2: Pearson's Correlation | StatQuest (Josh Starmer) | EN | ~19 min | https://www.youtube.com/watch?v=xZ_z8KWkhXE | Le coefficient de Pearson expliqué visuellement, de la covariance à r |
| TOUT sur les statistiques inférentielles (Échantillonnage et Estimation) | (recherche YouTube FR) | FR | ~20 min | https://www.youtube.com/watch?v=nIk7wjUYyDc | Population/échantillon, échantillonnage et estimation, en français simple |
| Estimer une proportion à l'aide d'un intervalle de confiance | Yvan Monka (maths-et-tiques) | FR | ~10 min | https://www.youtube.com/watch?v=cU5cJlCVAM8 | Le calcul d'un IC sur une proportion, étape par étape (cas du sondage) |
| Spurious correlations / corrélation ≠ causalité | Recherche YouTube | EN/FR | varié | https://www.youtube.com/results?search_query=spurious+correlations+correlation+causation+explained | Pourquoi des variables absurdes peuvent être corrélées — le réflexe anti-piège |

> Astuce : sur les vidéos StatQuest en anglais, active les **sous-titres traduits automatiquement** (icône engrenage → sous-titres → traduire → français). Le vocabulaire est simple et très visuel.

---

## Exercices

> Fais l'exercice **avant** d'ouvrir le corrigé. Une calculatrice et/ou un notebook Python suffisent.

### Exercice 1 — Population ou échantillon ?
Pour chaque cas, dis si on parle de population ou d'échantillon, et nomme N ou n :
a) Tous les 45 000 abonnés à la newsletter d'une enseigne.
b) Les 300 abonnés tirés au sort pour un test produit.
c) Les 12 caisses d'un hypermarché analysées sur la journée d'hier (l'enseigne en a 12).

<details><summary>Voir le corrigé</summary>

a) **Population**, N = 45 000 (on parle de *tous* les abonnés).
b) **Échantillon**, n = 300 (sous-ensemble tiré de la population des abonnés).
c) **Population**, N = 12 — si l'objectif est d'analyser *ces 12 caisses-là* et qu'il n'y en a pas d'autres, elles constituent la population complète. (Si on voulait généraliser à d'autres magasins, ce serait un échantillon.)
</details>

---

### Exercice 2 — Repérer le biais
Une enseigne envoie un sondage de satisfaction **par SMS** uniquement aux clients ayant fait un achat **en ligne** le mois dernier, et seuls 8 % répondent. Cite **deux** biais possibles et explique en une phrase pourquoi le résultat risque d'être faux.

<details><summary>Voir le corrigé</summary>

- **Biais de couverture / sélection** : on ignore complètement les clients qui achètent **en magasin** → l'échantillon ne représente pas toute la clientèle.
- **Biais de non-réponse** : avec seulement 8 % de répondants, ce sont probablement les très satisfaits ou très mécontents qui répondent → résultat polarisé, pas représentatif des 92 % silencieux.
Conclusion : même avec beaucoup de SMS envoyés, le taux de satisfaction obtenu ne reflète pas la vraie population.
</details>

---

### Exercice 3 — Intervalle de confiance à la main
Sur un sondage, **n = 400** clients, **240** se disent prêts à recommander la marque.
a) Calcule p̂.
b) Calcule la marge d'erreur à 95 %.
c) Donne l'IC 95 % et rédige la phrase métier.

<details><summary>Voir le corrigé</summary>

a) p̂ = 240 / 400 = **0,60 = 60 %**.
b) Marge = 1,96 × √(0,60 × 0,40 / 400) = 1,96 × √(0,24/400) = 1,96 × √0,0006 = 1,96 × 0,02449 ≈ **0,048** → **±4,8 points**.
c) IC = 0,60 ± 0,048 → **[0,552 ; 0,648]** soit **[55,2 % ; 64,8 %]**.
Phrase : « 60 % des clients se disent prêts à recommander la marque, avec une marge d'erreur de ±4,8 points (IC 95 %). On est confiants à 95 % que le vrai taux est entre 55 % et 65 %. »
</details>

---

### Exercice 4 — Lire une p-value (A/B test)
Un A/B test sur deux bannières publicitaires donne **p-value = 0,32**. Le directeur marketing dit : « p = 0,32, donc il y a 32 % de chances que les deux bannières soient identiques, déployons quand même la nouvelle ! »
Que réponds-tu ? (deux erreurs à corriger)

<details><summary>Voir le corrigé</summary>

1. **Erreur d'interprétation de la p-value** : 0,32 n'est PAS « la probabilité que H0 soit vraie ». C'est la probabilité d'observer une différence au moins aussi grande **si** les deux bannières étaient identiques. On ne peut pas la lire comme « 32 % de chances qu'elles soient identiques ».
2. **Décision** : p = 0,32 ≥ 0,05 → **non significatif**. On n'a **aucune preuve** que la nouvelle bannière soit meilleure. La différence observée est compatible avec le hasard. Réponse : « On ne peut pas conclure que la nouvelle bannière est meilleure ; déployer un changement non prouvé est un risque inutile. Soit on garde l'actuelle, soit on relance un test avec plus de trafic. »
</details>

---

### Exercice 5 — Corrélation en Python
Tu disposes d'un DataFrame `df` avec les colonnes `budget_pub` (budget publicitaire mensuel) et `ca` (chiffre d'affaires). Écris le code pour : (a) afficher le nuage de points avec droite de régression, (b) calculer la corrélation de Pearson et sa p-value.

<details><summary>Voir le corrigé</summary>

```python
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# (a) Nuage de points + régression
sns.regplot(data=df, x="budget_pub", y="ca")
plt.title("Budget publicitaire vs chiffre d'affaires")
plt.show()

# (b) Pearson + p-value
r, p = stats.pearsonr(df["budget_pub"], df["ca"])
print(f"Pearson r = {r:.2f}  (p-value = {p:.4f})")
```
Et la phrase d'interprétation prudente : « On observe une corrélation positive (r = …). Attention : cela ne prouve pas que la pub *cause* le CA — d'autres facteurs (saisonnalité, promotions) peuvent jouer. »
</details>

---

### Exercice 6 — Corrélation ≠ causalité
On constate dans les données d'une chaîne de magasins que **le nombre de parapluies vendus** et **le nombre de bottes en caoutchouc vendues** sont fortement corrélés (r = 0,91).
a) Les parapluies font-ils vendre des bottes ?
b) Quelle est probablement la vraie explication ?
c) Comment nomme-t-on cette variable ?

<details><summary>Voir le corrigé</summary>

a) **Non.** Une forte corrélation ne prouve aucun lien de cause à effet.
b) La vraie explication est la **pluie / la météo** : quand il pleut, les gens achètent à la fois des parapluies ET des bottes.
c) C'est une **variable confondante** (ou variable cachée / cause commune). Elle influence les deux variables observées et crée la corrélation entre elles.
</details>

---

## Quiz (5 QCM)

**Q1.** Dans un sondage, on interroge 500 personnes parmi 80 000 clients. Que vaut n ?
- A) 80 000
- B) 500
- C) 79 500
- D) On ne peut pas savoir

**Q2.** Un intervalle de confiance à 95 % devient plus **étroit** quand…
- A) on augmente la taille de l'échantillon
- B) on diminue la taille de l'échantillon
- C) on passe de 95 % à 99 % de confiance
- D) le taux observé est exactement 50 %

**Q3.** Une p-value de 0,02 (seuil 5 %) signifie qu'on…
- A) accepte H0
- B) rejette H0 : résultat significatif
- C) ne peut rien conclure
- D) a 2 % de chances que H1 soit vraie

**Q4.** Le coefficient de Pearson vaut −0,85. Cela indique…
- A) aucune relation
- B) une forte relation positive
- C) une forte relation négative
- D) une relation de cause à effet

**Q5.** Les ventes de glaces et les coups de soleil sont corrélés. La meilleure conclusion est :
- A) les glaces provoquent les coups de soleil
- B) les coups de soleil donnent envie de glaces
- C) une variable confondante (la chaleur) explique les deux
- D) c'est une erreur de calcul

<details><summary>Voir les réponses</summary>

**Q1 : B** — n est la taille de l'échantillon (500). N = 80 000 est la population.
**Q2 : A** — plus n est grand, plus l'IC est étroit (estimation plus précise). Passer à 99 % l'élargit.
**Q3 : B** — p = 0,02 < 0,05 → on rejette H0, résultat significatif. (D est faux : la p-value ne donne pas la proba de H1.)
**Q4 : C** — proche de −1 = forte relation négative. Et NON, jamais de causalité depuis une corrélation (D faux).
**Q5 : C** — variable confondante = la chaleur. C'est l'illustration type de corrélation ≠ causalité.
</details>

---

## À retenir

- **Population (N, μ, p)** = tout le monde ; **échantillon (n, x̄, p̂)** = ce qu'on observe. L'inférence généralise de l'échantillon vers la population.
- Un **bon échantillon est aléatoire et représentatif**. Un **biais** (sélection, non-réponse, survivant) fausse tout, **même avec un gros échantillon**. La taille ne corrige jamais le biais.
- L'**erreur d'échantillonnage** est la fluctuation naturelle d'un échantillon à l'autre ; elle diminue en **√n** (×4 la taille pour ÷2 l'erreur).
- **Intervalle de confiance** : on annonce une **fourchette**, pas une valeur sèche. Formule proportion : **p̂ ± 1,96 √(p̂(1−p̂)/n)**. Toujours donner la **marge d'erreur**.
- **Test d'hypothèse** : H0 (« rien ») vs H1 (« quelque chose »). **p-value < 0,05 → on rejette H0** (significatif). La p-value n'est **PAS** la probabilité que H0 soit vraie.
- **Corrélation** entre −1 et +1. **Pearson** = relation linéaire ; **Spearman** = relation monotone, robuste aux outliers. **Dessine toujours le nuage de points avant de conclure.**
- En Python : `df.corr()`, `scipy.stats.pearsonr` / `spearmanr`, `sns.regplot`, `sns.heatmap`.
- 🚨 **LE réflexe du Data Analyst : corrélation ≠ causalité.** Pense toujours à la **variable confondante** et à la **causalité inverse**. On ne prouve une cause qu'avec une **expérience contrôlée**, jamais avec une simple corrélation observée.

> 🧠 **Les 3 mnémos à emporter (les seules choses à ne JAMAIS oublier) :**
> 1. **IC = la fourchette où se cache la vraie valeur.** 🍴 (jamais un chiffre sec sans marge d'erreur)
> 2. **p-value < 5 % = trop beau pour être un hasard.** (mais ce n'est PAS « la proba que H0 soit vraie »)
> 3. **Deux courbes qui montent ensemble ≠ l'une cause l'autre.** Cherche toujours la 3ᵉ chose cachée (glaces 🍦 + noyades ← chaleur ☀️).
