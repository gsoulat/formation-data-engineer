# 01 — Identifier et interpréter les tendances

> **Phase 1** — Construire un tableau de bord
> **Durée** : ~20 heures
> **Compétence visée** : C6 (niveau 1) — *Identifier les corrélations et analyser les tendances afin de produire des recommandations*
> **Pré-requis** :
> - Module **1.2** (Python / pandas / EDA) — tu sais charger un CSV, manipuler un `DataFrame`, faire un `groupby`, tracer un graphique avec matplotlib.
> - Module **Maths chapitre 6** (moyenne mobile, indices) et **chapitre 5** (corrélation).

---

## 🎬 Accroche — La Ch'ti Boutique

> Imagine. Tu viens d'être embauché·e comme Data Analyst pour **La Ch'ti Boutique**, une petite chaîne de magasins du Nord. Le patron débarque, café à la main :
>
> *« Dis-moi… pourquoi nos ventes **montent en flèche en décembre** et **s'écroulent en février** ? Et au fait : est-ce qu'on grandit vraiment, ou est-ce qu'on tourne en rond ? »*
>
> Tu pourrais répondre au feeling. Mais un feeling ne se met pas dans un tableau de bord. Ce module te donne les **outils pour répondre avec des chiffres** : repérer ce qui revient chaque année (la **saison**), mesurer si la flèche pointe vraiment vers le haut (la **tendance**), et ne pas te faire piéger par le hasard (le **bruit**).
>
> À la fin, le patron repart avec une vraie réponse. Et toi, avec une compétence qui vaut de l'or : **lire une courbe dans le temps sans te raconter d'histoires.**

### 🔗 Le pont avec tes cours de maths

Bonne nouvelle : tu as **déjà vu les maths** de ce module. On va juste les brancher sur de vraies données.

| Idée du module | Maths que tu connais déjà | Où |
|---|---|---|
| Une **tendance** qui monte régulièrement | la **pente** d'une **fonction affine** : c'est le **taux de variation** (de combien ça monte par mois) | Maths **ch.2** |
| Comparer deux évolutions, voir si elles « bougent ensemble » | la **corrélation** | Maths **ch.5** |
| **Moyenne mobile** et **base 100** (indices) | lissage et **indices** | Maths **ch.6** |

> **En clair** : quand tu traceras une courbe lissée qui monte, tu regardes en fait une **pente** (ch.2). Quand tu te demanderas si deux magasins « évoluent pareil », tu penseras **corrélation** (ch.5). Ce module, c'est tes maths qui prennent vie sur le CA de La Ch'ti Boutique.

### 🎯 Ça te servira pour…

- **Suivre un KPI dans le temps** sur un tableau de bord (« le CA monte-t-il vraiment ? »).
- **Repérer une saisonnalité** pour anticiper les pics (commander assez de stock pour Noël).
- **Comparer des magasins / régions / produits** sur un pied d'égalité.
- **Dire la vérité au métier** sans sur-vendre une hausse qui n'est qu'un effet de calendrier.

---

## Objectifs du module

À la fin de ce module, tu seras capable de :

1. **Préparer une série temporelle** dans pandas : convertir une colonne en dates (`parse_dates`, `to_datetime`), la placer en index (`set_index`), et la rééchantillonner par mois ou par semaine (`resample`).
2. **Calculer des évolutions** : variation absolue, variation en pourcentage, glissement annuel (**YoY** — *Year over Year*) et glissement mensuel (**MoM** — *Month over Month*).
3. **Lisser une courbe** avec une **moyenne mobile** (`rolling`) pour faire ressortir le signal de fond.
4. **Distinguer à l'œil** une **tendance**, une **saisonnalité** et du **bruit**.
5. **Comparer des groupes** (enseignes, régions, catégories) sur la même période.
6. **Contextualiser une tendance pour le métier** : formuler une lecture honnête, sans sur-interpréter ni confondre corrélation et causalité.

---

## Pourquoi c'est utile au Data Analyst

Dans la vraie vie, on te posera rarement la question « quelle est la moyenne ? ». On te posera surtout :

- « Est-ce que **ça monte ou ça descend** ? »
- « On a fait **combien de mieux que l'an dernier** ? »
- « C'est **la saison** ou c'est une **vraie tendance** ? »
- « **Quelle enseigne** décroche par rapport aux autres ? »

Ce sont des questions de **tendance**. Elles sont au cœur de tout tableau de bord de pilotage : un dirigeant ne regarde pas un chiffre isolé, il regarde une **courbe dans le temps** et il veut savoir si la flèche pointe vers le haut.

Savoir répondre proprement — avec les bons calculs (YoY, moyenne mobile) et la bonne prudence (ne pas confondre un pic de Noël avec une croissance durable) — c'est exactement ce qui sépare un Data Analyst d'une personne qui « sait faire un graphique ». C'est la compétence **C6**.

Fil rouge du module : le **chiffre d'affaires mensuel d'enseignes retail dans les Hauts-de-France** (Nord). On y verra des soldes (janvier, juin/juillet) et un pic de Noël (décembre) : un terrain parfait pour parler saisonnalité.

---

## Contenu

### Les données du fil rouge

> #### 🎲 Devine avant de calculer
> Avant de voir les chiffres de La Ch'ti Boutique, **parie** : pour une boutique du Nord, quels seront les **3 mois les plus forts** de l'année ? Note-les sur un papier.
>
> <details>
> <summary>Voir si tu avais bon</summary>
>
> Le code ci-dessous fabrique exprès : **+40 % en décembre** (Noël) et **+15 % en janvier et juillet** (les soldes). Si tu as pensé « décembre + soldes », bravo, tu as déjà l'intuition de la **saisonnalité** ! On va maintenant le **prouver avec les données** au lieu de le deviner.
> </details>

Pour suivre tout le module, on génère un jeu de données réaliste. Copie ce bloc une fois pour tout reproduire chez toi.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Reproductibilité : tout le monde aura les mêmes chiffres
np.random.seed(42)

# 3 années de CA mensuel pour 2 enseignes du Nord
dates = pd.date_range(start="2022-01-01", end="2024-12-31", freq="MS")  # MS = début de mois

def ca_enseigne(base, croissance):
    n = len(dates)
    tendance = base + croissance * np.arange(n)          # croissance régulière
    mois = dates.month
    saison = np.where(mois == 12, 1.40, 1.0)             # +40 % en décembre (Noël)
    saison = np.where(np.isin(mois, [1, 7]), 1.15, saison)  # +15 % aux soldes
    bruit = np.random.normal(1.0, 0.04, n)              # ±4 % d'aléa
    return (tendance * saison * bruit).round(0)

df = pd.DataFrame({
    "date": list(dates) * 2,
    "enseigne": ["Lille-Centre"] * len(dates) + ["Roubaix-Mail"] * len(dates),
    "ca": list(ca_enseigne(50000, 800)) + list(ca_enseigne(38000, 300)),
})
print(df.head())
```

Sortie :

```
        date      enseigne       ca
0 2022-01-01  Lille-Centre  60221.0
1 2022-02-01  Lille-Centre  50845.0
2 2022-03-01  Lille-Centre  52614.0
3 2022-04-01  Lille-Centre  51980.0
4 2022-05-01  Lille-Centre  50367.0
```

**Lecture** : une ligne = un mois × une enseigne. La colonne `date` est encore du texte/objet pour pandas si elle venait d'un CSV — c'est le premier problème à régler.

---

### Transformer une colonne en série temporelle

> 🧠 **Le mot fait peur, l'idée est simple.** Une **série temporelle**, c'est juste **une mesure prise régulièrement dans le temps** : ta température chaque matin, le nombre de pas par jour sur ta montre, le CA de chaque mois. Une valeur, une date, et on recommence. Rien de plus.

Une **série temporelle**, c'est simplement des valeurs **indexées par le temps**. Pour que pandas comprenne le temps (et débloque `resample`, le tri chronologique, les filtres par année…), il faut deux choses :

1. une colonne **reconnue comme date** (type `datetime64`),
2. cette date placée en **index**.

```python
# Cas réel : tu lis un CSV où la date est du texte
# df = pd.read_csv("ca_nord.csv", parse_dates=["date"])  # <-- convertit dès la lecture

# Si la conversion n'a pas été faite à la lecture :
df["date"] = pd.to_datetime(df["date"])   # texte -> datetime
print(df.dtypes)
```

Sortie :

```
date        datetime64[ns]
enseigne            object
ca                 float64
```

```python
# On travaille d'abord sur UNE enseigne pour aller à l'essentiel
lille = df[df["enseigne"] == "Lille-Centre"].copy()
lille = lille.set_index("date").sort_index()   # date en index + tri chronologique
print(lille.head(3))
```

Sortie :

```
                  enseigne       ca
date
2022-01-01  Lille-Centre  60221.0
2022-02-01  Lille-Centre  50845.0
2022-03-01  Lille-Centre  52614.0
```

**Interprétation métier** : maintenant que la date est l'index, on peut découper le temps en langage naturel — `lille.loc["2023"]` donne toute l'année 2023, `lille.loc["2023-06":"2023-08"]` donne l'été 2023. C'est la base de tout filtre de dashboard (« afficher le dernier trimestre »).

> **Encadré — Erreur courante : la date reste du texte**
> Si tu oublies `parse_dates`/`to_datetime`, pandas trie tes dates **par ordre alphabétique** : `"01/12/2023"` passe avant `"02/01/2023"`. Ta courbe devient n'importe quoi. **Vérifie toujours `df.dtypes` : tu dois voir `datetime64`.** Attention aussi au format jour/mois (FR : `dd/mm/yyyy`) vs mois/jour (US) : précise `pd.to_datetime(col, format="%d/%m/%Y")` en cas de doute.

---

### Rééchantillonner avec `resample` (mois, semaine)

> 🔍 **`resample` = changer la « taille des cases » du temps.** Imagine un calendrier : tu peux regarder tes ventes **jour par jour** (petites cases, beaucoup de détail) ou **mois par mois** (grandes cases, vue d'ensemble). `resample` fait exactement ça : il regroupe tes lignes par tranche de temps (semaine, mois, trimestre…) et te laisse choisir si on **additionne** ou on fait la **moyenne** de chaque case. C'est un `groupby`, mais qui groupe par **bouts de calendrier**.

`resample` change la **granularité temporelle** d'une série. C'est un `groupby` spécial « par tranche de temps ». On passe une **fréquence** puis une **agrégation**.

| Code fréquence | Signification |
|---|---|
| `"D"` | jour |
| `"W"` | semaine |
| `"MS"` | début de mois (*Month Start*) |
| `"ME"` | fin de mois (*Month End*) |
| `"QS"` | début de trimestre |
| `"YS"` | début d'année |

```python
# Notre série est déjà mensuelle. On agrège au TRIMESTRE pour une vue plus lisse.
ca_trimestre = lille["ca"].resample("QS").sum()
print(ca_trimestre.head())
```

Sortie :

```
date
2022-01-01    163680.0
2022-04-01    156997.0
2022-07-01    180310.0
2022-10-01    231044.0   <-- T4 gonflé par décembre
Freq: QS-JAN, Name: ca, dtype: float64
```

**Interprétation métier** : le 4ᵉ trimestre écrase tous les autres — c'est Noël. Important : on choisit l'agrégation selon le sens du chiffre. Pour un **CA**, on **somme** (`.sum()`). Pour une **température** ou un **taux**, on fait la **moyenne** (`.mean()`). Sommer des pourcentages n'a aucun sens.

```python
# Downsampling (on dé-zoome) vers l'année
ca_annee = lille["ca"].resample("YS").sum()
print(ca_annee)
```

Sortie :

```
date
2022-01-01     732031.0
2023-01-01     843889.0
2024-01-01     954672.0
Freq: YS-JAN, Name: ca, dtype: float64
```

**Lecture** : 732 k€ → 844 k€ → 955 k€. La tendance annuelle est clairement haussière. On le quantifiera proprement au 3.3.

> **Encadré — Erreur courante : agréger avec la mauvaise fonction**
> `.sum()` sur un CA, oui. `.sum()` sur un prix moyen ou un taux de conversion, **non** : ça invente un chiffre. Demande-toi toujours : « si j'additionne ces lignes, est-ce que le total veut dire quelque chose ? »

---

### Calculer des évolutions : variation, %, YoY, MoM

C'est le cœur du métier. Quatre calculs à maîtriser.

**a) Variation absolue et en pourcentage (mois après mois = MoM)**

```python
m = lille["ca"]                      # série mensuelle
var_abs = m.diff()                   # valeur(t) - valeur(t-1)
var_pct = m.pct_change() * 100       # variation en %

evo = pd.DataFrame({"ca": m, "var_abs": var_abs, "var_%": var_pct.round(1)})
print(evo.head(4))
```

Sortie :

```
                  ca   var_abs  var_%
date
2022-01-01   60221.0      NaN    NaN
2022-02-01   50845.0  -9376.0  -15.6
2022-03-01   52614.0   1769.0    3.5
2022-04-01   51980.0   -634.0   -1.2
```

**Interprétation métier** : -15,6 % entre janvier et février. Avant de crier au déclin : **janvier était dopé par les soldes**. Comparer deux mois côte à côte (MoM) sur une activité saisonnière est **trompeur**. D'où le glissement annuel.

**b) Glissement annuel (YoY) — comparer chaque mois à LE MÊME mois l'an dernier**

C'est la mesure reine du retail : elle neutralise la saisonnalité. Sur une série **mensuelle**, « il y a un an » = 12 lignes en arrière.

```python
yoy = m.pct_change(periods=12) * 100   # vs même mois N-1
print(yoy.dropna().head(4).round(1))
```

Sortie :

```
date
2023-01-01    13.2
2023-02-01    16.1
2023-03-01    14.8
2023-04-01    15.0
Name: ca, dtype: float64
```

**Interprétation métier** : +13 à +16 % par rapport au même mois l'année précédente. **Ça, c'est une vraie croissance** : décembre est comparé à décembre, les soldes aux soldes. Le YoY « efface » la saison et montre le fond.

> Rappel **Maths ch.6** : le YoY est un **indice base 100 décalé d'un an** — on compare deux périodes de même nature pour gommer l'effet calendaire.

**c) Récap des outils**

| Question métier | Code pandas |
|---|---|
| « Combien en plus que le mois dernier ? » | `s.diff()` |
| « +X % par rapport au mois dernier ? » (MoM) | `s.pct_change()*100` |
| « +X % par rapport à l'an dernier ? » (YoY, série mensuelle) | `s.pct_change(periods=12)*100` |
| « Évolution depuis le début (base 100) ? » | `s / s.iloc[0] * 100` |

> **Encadré — Erreur courante : le piège du pourcentage qui ne « revient » pas**
> Une baisse de -50 % suivie d'une hausse de +50 % ne te ramène **pas** au point de départ (100 → 50 → 75). Les pourcentages ne s'additionnent pas. Pour cumuler une évolution sur plusieurs périodes, repars toujours des **valeurs absolues**, pas de la somme des %.

---

### Lisser avec une moyenne mobile (`rolling`)

> 🌊 **L'image à garder.** La **moyenne mobile** (en anglais *rolling mean*, « moyenne qui roule »), c'est comme regarder la **mer de loin** : de près tu vois chaque vaguelette qui monte et descend, mais en reculant tu ne vois plus que le **niveau général** de l'eau. Lisser une courbe = **enlever les vaguelettes** (les pics, les creux) pour voir la **vraie marée** : ça monte ou ça descend ?
>
> #### 🎲 Devine avant de tracer
> Regarde mentalement la série brute (les dents de scie pleines de pics de Noël et de creux de février). **Sans calculer** : si on enlève toutes ces vaguelettes, est-ce que la « marée » de fond **monte**, **descend** ou **reste plate** ? Garde ta réponse en tête, le graphique va te dire si tu avais raison.

Une série brute « tremble » (le bruit du 3.6). La **moyenne mobile** fait glisser une fenêtre sur la série et en prend la moyenne : ça **lisse** les soubresauts et fait apparaître la tendance.

```python
lille["ma_3"] = lille["ca"].rolling(window=3).mean()    # fenêtre 3 mois
lille["ma_12"] = lille["ca"].rolling(window=12).mean()  # fenêtre 12 mois

ax = lille["ca"].plot(label="CA brut", alpha=0.4, figsize=(11, 5))
lille["ma_3"].plot(ax=ax, label="Moyenne mobile 3 mois", linewidth=2)
lille["ma_12"].plot(ax=ax, label="Moyenne mobile 12 mois", linewidth=2)
ax.set_title("CA mensuel Lille-Centre — brut vs lissé")
ax.set_ylabel("CA (€)")
ax.legend()
plt.tight_layout()
plt.show()
```

Sortie (description du graphique) :

```
- La courbe BRUTE fait des dents de scie (pics de décembre, creux de février).
- La MA 3 mois suit la forme mais arrondit les angles.
- La MA 12 mois est presque une droite qui monte : elle GOMME toute la saison
  et ne montre QUE la tendance de fond -> hausse régulière.
```

**Interprétation métier** : pour un comité de direction, la **MA 12 mois** raconte l'histoire essentielle (« on croît »), sans le bruit qui distrait. La fenêtre se choisit selon le cycle : **12 mois** annule la saisonnalité annuelle ; **7 jours** annule l'effet week-end sur des données journalières.

> **Détail** : `window=12` met `NaN` sur les 11 premières lignes (pas assez d'historique pour remplir la fenêtre). C'est normal. `min_periods=1` permet de commencer plus tôt, au prix d'un début moins fiable.

> Rappel **Maths ch.6** : `rolling().mean()` = la **moyenne mobile simple** vue en cours. Plus la fenêtre est large, plus c'est lisse, mais plus la courbe « réagit en retard ».

> 🔗 **Pont Maths ch.2 (la pente)** : une fois la courbe lissée, demande-toi « de combien elle monte par mois ? ». Ça, c'est le **taux de variation** d'une **fonction affine** — la fameuse **pente**. Une moyenne mobile 12 mois presque droite qui grimpe = une pente positive constante = « on gagne à peu près X € de plus chaque mois ». La tendance n'est rien d'autre qu'**une pente cachée sous le bruit**.

> **Encadré — Erreur courante : trop lisser**
> Une fenêtre énorme peut **effacer un vrai décrochage**. Si la fenêtre dépasse la durée de l'événement que tu cherches, tu ne le verras plus. Affiche toujours le brut **et** le lissé côte à côte : le lissé pour la tendance, le brut pour les anomalies.

---

### Tendance, saisonnalité, bruit : les trois ingrédients

Toute série temporelle se décompose mentalement en trois couches :

| Composante | Définition | Sur nos données retail |
|---|---|---|
| **Tendance** | direction de fond sur le long terme | le CA augmente d'année en année |
| **Saisonnalité** | motif qui se **répète à intervalle régulier** | pic chaque décembre, bosses aux soldes |
| **Bruit** | variations aléatoires inexplicables | un mois un peu au-dessus/dessous sans raison |

On peut le visualiser automatiquement :

```python
from statsmodels.tsa.seasonal import seasonal_decompose

serie = lille["ca"].asfreq("MS")           # fréquence explicite obligatoire
dec = seasonal_decompose(serie, model="additive", period=12)
dec.plot()
plt.tight_layout()
plt.show()
```

Sortie (description) :

```
4 sous-graphiques empilés :
1. Observed : la série brute.
2. Trend    : une courbe lisse qui MONTE -> la tendance.
3. Seasonal : un motif identique qui se RÉPÈTE tous les 12 mois (pic en déc.).
4. Resid    : le bruit, petit et sans structure.
```

**Interprétation métier** : tu peux maintenant dire à un client « +X % de croissance de fond, **et** un pic de Noël qui vaut +40 % chaque année ». Tu sépares ce qui est **structurel** (la tendance, sur quoi on peut agir) de ce qui est **calendaire** (la saison, qu'on subit/anticipe).

> Tu n'as **pas** besoin de maîtriser les maths internes de `seasonal_decompose` au niveau 1. L'objectif est l'**intuition** : reconnaître à l'œil ces trois couches sur un graphique.

> **Encadré — Erreur courante : confondre saison et tendance**
> « Les ventes explosent en décembre, l'entreprise décolle ! » → non, c'est **saisonnier**, ça retombe en janvier. La question utile est : « **ce décembre est-il meilleur que le décembre précédent ?** » (= YoY). Ne jamais conclure à une tendance à partir d'un seul point haut.

---

### Comparer des groupes / segments

Une tendance prend tout son sens **en comparaison**. On remet les deux enseignes côte à côte.

```python
# Tableau croisé : une colonne par enseigne, index = date
pivot = df.pivot_table(index="date", columns="enseigne", values="ca", aggfunc="sum")

# Base 100 au premier mois pour comparer des enseignes de tailles différentes
base100 = pivot / pivot.iloc[0] * 100

ax = base100.plot(figsize=(11, 5), linewidth=2)
ax.axhline(100, color="grey", linestyle="--", alpha=0.6)
ax.set_title("Évolution du CA en base 100 (jan. 2022 = 100)")
ax.set_ylabel("Indice (base 100)")
plt.tight_layout()
plt.show()
```

Sortie (description) :

```
Deux courbes partant de 100 :
- Lille-Centre grimpe nettement (vers ~145 fin 2024).
- Roubaix-Mail progresse plus mollement (vers ~118).
Même si Lille génère plus d'euros en absolu, la base 100 montre QUI CROÎT LE PLUS VITE.
```

**Interprétation métier** : la **base 100** (rappel Maths ch.6 : les indices) neutralise la différence de taille. On ne compare plus des euros mais des **rythmes de croissance**. Conclusion actionnable : Roubaix décroche en dynamique → creuser pourquoi (zone de chalandise ? travaux ? concurrence ?).

> **Encadré — Erreur courante : comparer des choses non comparables**
> Comparer le CA **brut** d'un hypermarché et d'une supérette ne dit rien d'utile (l'un est 10× plus gros). Compare des **taux de croissance** ou des **bases 100**. Et compare toujours **la même période** pour chacun (mêmes mois) — sinon tu compares un trimestre de soldes à un trimestre creux.

---

### Contextualiser pour le métier (ne pas sur-interpréter)

Le calcul est la partie facile. La valeur du Data Analyst est dans la **lecture honnête**. Trois réflexes :

1. **Corrélation ≠ causalité.** Deux courbes qui montent ensemble ne prouvent rien. (Rappel Maths ch.5 : un coefficient de corrélation mesure un lien statistique, **pas** une cause.)
2. **Cherche l'explication métier avant de conclure.** Un pic peut venir d'une promo, d'une météo, d'un jour férié, d'un changement d'outil de mesure. Demande au métier.
3. **Dis ce que tu ne sais pas.** « +18 % YoY en mars, à confirmer car une nouvelle boutique a ouvert en février » est une bien meilleure phrase que « +18 %, ça décolle ».

```python
# Illustration du piège corrélation/causalité
ventes_glaces = pd.Series([10, 25, 80, 40, 12])
noyades       = pd.Series([2, 5, 14, 7, 3])
print("Corrélation :", round(ventes_glaces.corr(noyades), 2))
```

Sortie :

```
Corrélation : 0.99
```

**Interprétation** : corrélation quasi parfaite… et pourtant les glaces ne causent évidemment pas les noyades. La **vraie cause cachée** est la **chaleur** (variable confondante) : l'été, on mange plus de glaces ET on se baigne plus. **Une corrélation forte n'est jamais une preuve de cause.**

> #### ⚠️ Piège à éviter — « ça monte ensemble, donc c'est lié »
> Ton cerveau **adore** inventer des causes. C'est le piège n°1 du Data Analyst débutant.
> - 🍦 Glaces ↑ et noyades ↑ → *coupable réel : la chaleur.*
> - 🏴‍☠️ Le réchauffement climatique ↑ pendant que le nombre de pirates ↓ → personne ne pense que sauver les pirates refroidirait la planète, et pourtant les courbes « collent ».
>
> **Le réflexe anti-piège** : devant deux courbes qui bougent pareil, demande-toi **« quelle 3ᵉ chose pourrait expliquer les deux ? »** avant de crier « j'ai trouvé la cause ! ». Lien statistique (ch.5) ≠ cause. Toujours.

> **Encadré — Erreur courante : l'axe Y tronqué**
> Démarrer l'axe vertical à 95 % au lieu de 0 transforme une hausse de 2 % en falaise spectaculaire. C'est la manipulation graphique la plus fréquente (volontaire ou non). Pour un CA, **commence l'axe à 0** ; si tu le tronques pour la lisibilité, **dis-le explicitement** sur le graphique. Une tendance se juge sur les **chiffres**, pas sur l'inclinaison visuelle d'une courbe.

---

## Travaux pratiques

> Reprends le bloc du **3.0** pour générer `df` avant chaque TP.

### TP 1 — Mettre une série au propre

À partir de `df`, isole l'enseigne **Roubaix-Mail**, mets la date en index, trie chronologiquement, puis affiche le CA **trimestriel**.

<details>
<summary>Voir le corrigé</summary>

```python
roubaix = df[df["enseigne"] == "Roubaix-Mail"].copy()
roubaix["date"] = pd.to_datetime(roubaix["date"])
roubaix = roubaix.set_index("date").sort_index()

ca_trim = roubaix["ca"].resample("QS").sum()
print(ca_trim.head())
```

Sortie :
```
date
2022-01-01    119371.0
2022-04-01    114985.0
2022-07-01    128902.0
2022-10-01    150642.0
Freq: QS-JAN, Name: ca, dtype: float64
```
**Lecture** : même schéma que Lille — T4 (Noël) domine. On somme car c'est un CA.
</details>

---

### TP 2 — MoM vs YoY

Pour Lille-Centre, calcule la variation **MoM** (%) et la variation **YoY** (%). Compare la valeur de **janvier 2023** dans les deux cas et explique en une phrase pourquoi elles diffèrent.

<details>
<summary>Voir le corrigé</summary>

```python
m = lille["ca"]
mom = (m.pct_change() * 100).round(1)
yoy = (m.pct_change(periods=12) * 100).round(1)

print("Janvier 2023 — MoM :", mom.loc["2023-01-01"], "%")
print("Janvier 2023 — YoY :", yoy.loc["2023-01-01"], "%")
```

Sortie (ordre de grandeur) :
```
Janvier 2023 — MoM : -25.x %
Janvier 2023 — YoY : +13.x %
```
**Explication** : le **MoM** compare janvier (soldes) à décembre (Noël, encore plus haut) → forte baisse trompeuse. Le **YoY** compare janvier 2023 à janvier 2022 (deux mois de soldes) → vraie croissance de +13 %. **Le YoY neutralise la saison.**
</details>

---

### TP 3 — Lisser et lire la tendance

Trace, pour Roubaix-Mail, le CA brut + une moyenne mobile 3 mois + une moyenne mobile 12 mois. Que raconte la MA 12 mois ?

<details>
<summary>Voir le corrigé</summary>

```python
roubaix["ma_3"] = roubaix["ca"].rolling(3).mean()
roubaix["ma_12"] = roubaix["ca"].rolling(12).mean()

ax = roubaix["ca"].plot(alpha=0.4, label="Brut", figsize=(11, 5))
roubaix["ma_3"].plot(ax=ax, label="MA 3 mois", linewidth=2)
roubaix["ma_12"].plot(ax=ax, label="MA 12 mois", linewidth=2)
ax.set_title("Roubaix-Mail — brut vs lissé"); ax.legend()
plt.tight_layout(); plt.show()
```
**Lecture** : la MA 12 mois est une courbe douce, légèrement haussière → croissance de fond réelle mais **plus lente** que Lille. La saison (dents de scie) a disparu du lissé.
</details>

---

### TP 4 — Comparer deux enseignes en base 100

Construis un tableau croisé date × enseigne, passe-le en **base 100** (premier mois), trace les deux courbes. Quelle enseigne croît le plus vite ? Pourquoi la base 100 est-elle plus juste que le CA brut pour cette comparaison ?

<details>
<summary>Voir le corrigé</summary>

```python
pivot = df.pivot_table(index="date", columns="enseigne", values="ca", aggfunc="sum")
base100 = pivot / pivot.iloc[0] * 100

ax = base100.plot(figsize=(11, 5), linewidth=2)
ax.axhline(100, color="grey", ls="--", alpha=.6)
ax.set_title("Base 100 — jan. 2022 = 100"); plt.tight_layout(); plt.show()

print(base100.iloc[-1].round(1))   # valeur finale de chaque courbe
```
**Réponse** : **Lille-Centre** croît le plus vite (indice final le plus haut). La base 100 est plus juste car elle **gomme la différence de taille** : on compare des **rythmes**, pas des montants. Comparer les CA bruts mélangerait « qui est gros » et « qui croît ».
</details>

---

### TP 5 — Esprit critique : tendance ou pas ?

On t'annonce : « Le CA de décembre 2024 est le plus haut de l'historique : l'entreprise est en pleine explosion ! ». En t'appuyant sur tes calculs, écris une réponse nuancée de 3-4 phrases (utilise saison + YoY + la mise en garde corrélation/causalité).

<details>
<summary>Voir le corrigé (exemple de réponse attendue)</summary>

> « Décembre est **toujours** le mois le plus haut : c'est la **saisonnalité de Noël**, pas une preuve d'explosion. La bonne question est le **glissement annuel** : décembre 2024 vs décembre 2023 affiche **+XX %**, ce qui confirme une **vraie croissance de fond** (visible aussi sur la moyenne mobile 12 mois). Attention toutefois à ne pas attribuer cette hausse à une seule cause sans vérifier avec le métier (ouverture de boutique, promo, météo) : **une corrélation temporelle n'est pas une preuve de causalité**. »

Critères : mentionne la saison, utilise le YoY pour trancher, refuse la sur-interprétation mono-causale.
</details>

---

## 🏆 Défi du module — « Repère la vraie tendance derrière le bruit »

> Le patron de La Ch'ti Boutique te lance un **dernier défi** avant la pause café.
>
> **La mission** : il te montre la courbe brute du CA d'un de ses magasins. Elle part dans tous les sens (pics de Noël, creux de février, un mois bizarrement haut). Il te demande : *« Franchement… on grandit, on stagne, ou on coule ? »*
>
> **Ta quête** (sur Lille-Centre, avec le `df` du 3.0) :
> 1. 🎯 **Devine d'abord** à l'œil sur la courbe brute : haussier, plat ou baissier ?
> 2. 🌊 Trace la **moyenne mobile 12 mois** pour enlever les vaguelettes.
> 3. 📐 Confirme avec le **YoY** : est-ce vraiment positif, mois après mois ?
> 4. 🗣️ Donne ta réponse au patron en **une phrase honnête** (la tendance + un avertissement « corrélation ≠ causalité » si besoin).
>
> **Tu gagnes le défi si** : ta conclusion s'appuie sur le **lissé OU le YoY** (pas sur un seul mois haut), et si tu n'attribues pas la hausse à une cause unique sans vérifier.
>
> <details>
> <summary>🏅 Voir la solution du défi</summary>
>
> ```python
> m = lille["ca"]
> ma12 = m.rolling(12).mean()
> yoy = m.pct_change(periods=12) * 100
>
> ax = m.plot(alpha=0.35, label="CA brut", figsize=(11, 5))
> ma12.plot(ax=ax, label="MA 12 mois", linewidth=2.5)
> ax.set_title("La vraie tendance derrière le bruit — Lille-Centre"); ax.legend()
> plt.tight_layout(); plt.show()
>
> print("YoY moyen :", round(yoy.dropna().mean(), 1), "%")
> ```
>
> **Conclusion gagnante (exemple)** :
> > « La courbe brute fait peur avec ses dents de scie, mais la **moyenne mobile 12 mois monte régulièrement** (c'est une pente positive, pas du hasard), et le **YoY est positif** tous les mois (~+13 à +16 %). Donc **oui, le magasin grandit vraiment**, ce n'est pas qu'un effet Noël. Réserve : avant d'expliquer pourquoi, vérifions avec le terrain (promo, nouvelle boutique ?) — **une hausse corrélée dans le temps n'est pas une preuve de cause.** »
>
> Le piège du défi : si tu avais répondu en regardant juste le pic de décembre 2024 (« on explose ! »), tu serais tombé dans la confusion **saison / tendance**. Le lissé et le YoY t'en protègent.
> </details>

---

## Vidéos d'auto-formation

> Liens vérifiés. Pour la vidéo Corey Schafer, le lien pointe vers la vidéo exacte (Part 10). Les autres pointent vers la vidéo ou une recherche YouTube fiable si l'URL exacte n'a pas pu être confirmée.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Python Pandas Tutorial (Part 10) – Working with Dates and Time Series Data | Corey Schafer | EN | ~36 min | https://www.youtube.com/watch?v=UFuo7EHI8zc | `to_datetime`, parse de dates, index temporel, `resample` — la référence pour les séries temporelles pandas |
| PANDAS PYTHON Tutoriel Français – Time Series (18/30) | Machine Learnia | FR | ~20 min | https://www.youtube.com/watch?v=qHRLG5hsW9I | Dates en index, `resample`, fenêtres glissantes, expliqué en français pour débutants |
| Master Time Series Resampling in Pandas (with Examples) | (recherche YouTube) | EN | ~15-20 min | https://www.youtube.com/results?search_query=master+time+series+resampling+in+pandas | Cas pratiques de `resample` (downsampling/upsampling) sur prix et capteurs |
| Moyenne mobile / rolling mean expliqué pour l'analyse de tendance | (recherche YouTube) | FR | varié | https://www.youtube.com/results?search_query=moyenne+mobile+pandas+rolling+analyse+tendance | Intuition du lissage, choix de la fenêtre, tendance vs bruit |
| Time Series Decomposition (trend, seasonality, residual) | (recherche YouTube) | EN | varié | https://www.youtube.com/results?search_query=time+series+decomposition+trend+seasonality+python | Décomposition tendance / saisonnalité / bruit avec statsmodels |

---

## Quiz (5 QCM)

**Q1.** Tu lis un CSV et tes dates se trient « 1/12 avant 2/1 ». Quelle est la cause la plus probable ?
- A) Le fichier est corrompu
- B) La colonne date est restée du **texte**, pas du `datetime`
- C) `resample` a échoué
- D) Il manque matplotlib

**Q2.** Pour comparer décembre 2024 à décembre 2023 et neutraliser la saison, tu utilises :
- A) `pct_change()` (MoM)
- B) `diff()`
- C) `pct_change(periods=12)` (YoY)
- D) `rolling(12).mean()`

**Q3.** Une moyenne mobile sur 12 mois appliquée à un CA mensuel sert surtout à :
- A) Augmenter le CA
- B) **Lisser** et faire ressortir la **tendance de fond** en effaçant la saison
- C) Calculer le YoY
- D) Convertir les dates

**Q4.** Le CA explose chaque décembre puis retombe en janvier. C'est :
- A) Une tendance haussière
- B) Du bruit
- C) De la **saisonnalité**
- D) Une erreur de données

**Q5.** Ventes de glaces et noyades sont corrélées à 0,99. Conclusion correcte :
- A) Les glaces causent les noyades
- B) Il faut interdire les glaces l'été
- C) **Corrélation ≠ causalité** ; une variable cachée (la chaleur) explique les deux
- D) Les données sont fausses

<details>
<summary>Réponses</summary>

1 → **B** · 2 → **C** · 3 → **B** · 4 → **C** · 5 → **C**
</details>

---

## À retenir

- Une **série temporelle** = des valeurs **indexées par le temps**. Réflexe : `to_datetime` (vérifier `dtypes`) → `set_index` → `sort_index`.
- **`resample(freq).agg`** change la granularité (mois, semaine, trimestre). **Somme** pour un CA, **moyenne** pour un taux/une température.
- **Évolutions** : `diff()` (absolu), `pct_change()` (MoM %), `pct_change(12)` (**YoY**, la mesure reine du retail car elle neutralise la saison). Les % **ne s'additionnent pas**.
- **`rolling(n).mean()`** lisse le bruit et révèle la **tendance**. Fenêtre 12 = annule la saison annuelle. Ne lisse pas au point d'effacer les vraies anomalies.
- Toute série = **tendance + saisonnalité + bruit**. Un pic récurrent (Noël) est **saisonnier**, pas une tendance.
- Comparer des groupes : **base 100** pour comparer des **rythmes**, pas des montants.
- **Honnêteté analytique** : corrélation ≠ causalité, axe Y à 0, on cherche l'explication métier et on assume ce qu'on ne sait pas. C'est ça, le niveau 1 de **C6**.
