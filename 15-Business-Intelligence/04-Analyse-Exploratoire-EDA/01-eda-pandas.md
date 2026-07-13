# 01 — Python & pandas pour l'analyse exploratoire (EDA)

> **Le couteau suisse du Data Analyst.** Excel s'essouffle vers 100 000 lignes ; pandas en avale des millions sans broncher, et garde la trace exacte de chaque manipulation. C'est l'outil que tu ouvriras **tous les jours** dès qu'un fichier de données arrivera sur ton bureau.

---

> ## 🎬 Bienvenue à la Ch'ti Boutique
>
> Lundi matin, 9 h. Le gérant de la **Ch'ti Boutique** (une chaîne de magasins du Nord : Lille, Roubaix, Dunkerque) débarque, café à la main, et te tend une clé USB :
>
> > *« Voilà toutes les ventes de l'année. Je sais pas trop ce qu'il y a dedans… mais je sens qu'il y a un truc qui cloche dans les chiffres. Tu peux regarder ? »*
>
> Tu ouvres le fichier : **un gros tas de lignes en vrac**. Des dates, des montants, des magasins, des cases vides, peut-être des erreurs. Personne n'a jamais vraiment regardé ces données.
>
> **Ta mission : faire parler ces données.** 🕵️ Tu es l'enquêteur, le fichier est la scène de crime, et pandas est ta loupe. À la fin de ce module, tu sauras transformer ce chaos en **3 à 5 phrases qui font dire au gérant : « Ah ouais, je savais pas ça. »**
>
> C'est exactement ça, le métier de Data Analyst. On y va. 🔍

> ## 🔗 Le pont avec les maths (lis-le, c'est important)
>
> Souviens-toi du **Chapitre 3 « Statistiques descriptives »** en maths : tu calculais à la main une moyenne, une médiane, un écart-type, tu repérais des outliers avec la règle de l'IQR, tu dessinais des boxplots… sur **10 ou 20 chiffres**, à la calculatrice.
>
> **Ici, c'est exactement la même chose — mais en une ligne de code, sur 250 000 lignes.**
>
> | Au Chapitre 3 (à la main) | Ici en pandas (en une ligne) |
> |---|---|
> | Additionner et diviser pour la moyenne | `df["montant"].mean()` |
> | Ranger les valeurs et prendre celle du milieu | `df["montant"].median()` |
> | Calculer Q1, Q3, l'écart-type | `df.describe()` (tout d'un coup !) |
> | Tracer un boxplot à la règle | `sns.boxplot(...)` |
>
> **Tu ne réapprends rien de nouveau en stats.** Tu apprends juste à demander à l'ordinateur de faire les calculs que tu sais déjà poser. pandas, c'est la **calculatrice industrielle** de ton Chapitre 3. 💪
>
> À chaque fois que tu verras le symbole 🔗 dans ce cours, c'est un rappel : *« ça, tu l'as déjà vu en maths ».*

| | |
|---|---|
| **Phase** | Phase 1 — Construire un tableau de bord |
| **Durée** | ≈ 30 h |
| **Objectif** | Mener des analyses exploratoires (EDA) |
| **Pré-requis** | Module **0.5 « Initiation à Python »** (variables, types, listes/dictionnaires, conditions, boucles, fonctions, `import`, premier `read_csv`/`.head()`) — **indispensable** si tu n'as jamais programmé · Module **Maths — Chapitre 3 « Statistiques descriptives »** (moyenne/médiane, dispersion, quantiles, outliers, histogramme & boxplot) · Module 1.1 SQL (notion de table, ligne, colonne) |
| **Outils** | Python 3.11+, Jupyter / Anaconda, `pandas`, `numpy`, `matplotlib`, `seaborn` |

---

## Objectifs pédagogiques

À la fin de ce module, tu sauras :

1. **Charger** un jeu de données depuis un CSV ou un Excel dans un DataFrame pandas.
2. **Explorer** rapidement un fichier inconnu (`.head`, `.info`, `.shape`, `.dtypes`, `.describe`).
3. **Sélectionner et filtrer** des lignes et des colonnes (`loc`, `iloc`, masques booléens).
4. **Traiter les valeurs manquantes** (`isna`, `fillna`, `dropna`) en faisant le bon choix métier.
5. **Nettoyer légèrement** un jeu de données : renommer, convertir des types, supprimer les doublons.
6. **Agréger** avec `groupby` (somme, moyenne, comptage par catégorie) et **trier** les résultats.
7. **Produire les premières visualisations** (histogramme, barres, boxplot) avec matplotlib et seaborn.
8. **Mener une EDA complète** de bout en bout sur un jeu de données retail réel, et en tirer des constats métier.

> 🔗 **Lien direct avec les maths.** Tout ce que tu as calculé à la main au Chapitre 3 (moyenne, médiane, écart-type, IQR, quartiles, détection d'outliers), tu vas maintenant le **produire en une ligne de code** sur des milliers de lignes. pandas est la « calculatrice industrielle » de la statistique descriptive.

---

## Pourquoi pandas est l'outil du quotidien

Imagine la scène. Un responsable régional te transmet un fichier `ventes_magasins.csv` de 250 000 lignes : « Dis-moi ce qui se passe dans le Nord. » Tu as trois options.

| Outil | Ce qui se passe |
|---|---|
| **Excel** | Lent au-delà de ~100 000 lignes, plante, fige. Et surtout : impossible de **retracer** ce que tu as fait (clics non journalisés → analyse non reproductible). |
| **SQL** (module 1.1) | Excellent pour **extraire** les données depuis une base. Mais limité pour explorer, visualiser, itérer rapidement. |
| **pandas** | Charge le fichier en quelques secondes, te laisse tout filtrer/agréger/visualiser, et **garde une trace écrite** (ton notebook) de chaque étape → analyse **reproductible**. |

**pandas** (= « *panel data* ») est la bibliothèque Python de référence pour manipuler des données **en tableau**. Tu y trouves deux objets :

- la **Series** : une colonne (un tableau 1D avec un index) ;
- le **DataFrame** : un tableau 2D (lignes × colonnes), comme une feuille Excel ou une table SQL.

> ## ✂️ Le jargon pandas traduit en français simple
>
> Trois mots reviennent sans arrêt. Voici leur traduction « pour les humains » :
>
> | Mot savant | Traduction simple | Image |
> |---|---|---|
> | **DataFrame** | « un tableur en Python » | Une feuille Excel entière (lignes + colonnes) que tu pilotes au clavier |
> | **Series** | « une seule colonne » | Une colonne extraite de ce tableur (la colonne « montant » par exemple) |
> | **groupby** | « ranger par paquets puis compter chaque paquet » | Tu fais des tas par magasin, puis tu calcules sur chaque tas |
>
> Retiens juste ça : **DataFrame = le tableau entier, Series = une colonne.** Tout le reste en découle. 👍

> 🧭 **Image à retenir.** Le DataFrame, c'est **un tableur que tu pilotes au clavier**. Chaque manipulation est une ligne de code que tu peux relire, corriger, rejouer demain sur un nouveau fichier. C'est la différence entre « bricoler » et « analyser ».

Et ce n'est pas un outil de niche : pandas est aujourd'hui **le standard de l'analyse de données en entreprise**, en amont de Power BI, des modèles de Machine Learning et des rapports métier.

---

## Rappel Python utile (le strict nécessaire)

Pas besoin d'être développeur pour faire de l'analyse. Voici les briques Python que tu réutiliseras sans cesse.

### Variables et types de base

```python
nom_magasin = "Lille"        # str  (chaîne de caractères)
nb_ventes   = 1240           # int  (entier)
panier_moyen = 42.7          # float (décimal)
est_ouvert  = True           # bool (booléen : True / False)

print(nom_magasin, nb_ventes, panier_moyen, est_ouvert)
```

**Sortie :**
```
Lille 1240 42.7 True
```

> 💡 Les booléens (`True`/`False`) sont au cœur du **filtrage** dans pandas : un masque booléen est juste une colonne de `True`/`False`.

### Listes et dictionnaires

```python
# Une liste : une suite ordonnée de valeurs
magasins = ["Lille", "Roubaix", "Dunkerque"]
print(magasins[0])      # le premier élément (l'index commence à 0 !)

# Un dictionnaire : des paires clé → valeur
vente = {"ville": "Roubaix", "montant": 58.9, "categorie": "Textile"}
print(vente["montant"])
```

**Sortie :**
```
Lille
58.9
```

> ⚠️ **Erreur courante.** En Python, **on compte à partir de 0**. `magasins[0]` = « Lille », `magasins[1]` = « Roubaix ». `magasins[3]` lèverait une erreur (`IndexError`) car il n'y a que 3 éléments (index 0, 1, 2).

Le dictionnaire est important : un DataFrame se construit naturellement à partir d'un dictionnaire `{ "nom_colonne": [valeurs] }`.

```python
import pandas as pd

donnees = {
    "ville":  ["Lille", "Roubaix", "Dunkerque"],
    "ventes": [1240, 980, 760],
}
df = pd.DataFrame(donnees)
print(df)
```

**Sortie :**
```
       ville  ventes
0      Lille    1240
1    Roubaix     980
2  Dunkerque     760
```

> 🧠 Retiens la convention universelle : **`import pandas as pd`**. Tout le monde l'écrit ainsi, dans tous les tutos et toutes les entreprises.

---

## Charger des données

### Depuis un CSV

Le CSV (*Comma-Separated Values*) est le format d'échange le plus courant.

> 📁 **Le fichier de travail.** On utilise `ventes_magasins.csv`, le jeu de données de l'univers **NordRetail** (dossier `data/` du brief). Ses colonnes : `date`, `ville`, `type` (magasin ou e-commerce), `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`. Un fichier riche : on pourra donc croiser le CA par `categorie`, la `marge` par `ville`, etc.

```python
import pandas as pd

ventes = pd.read_csv("ventes_magasins.csv")
ventes.head()
```

**Sortie (extrait) :**
```
         date      ville      type      categorie        produit  quantite  prix_unitaire  remise   montant  marge  client_id
0  2023-01-01  Dunkerque   Magasin  Électroménager  Réfrigérateur         4         387.37     0.0   1549.48 451.12        252
1  2023-01-01     Lille    Magasin        Textile           Pull         1          58.90     0.1     53.01  15.90        118
2  2023-01-02   Roubaix E-commerce         Maison         Lampe         2          12.00     0.0     24.00   7.20        341
```

**Paramètres que tu rencontreras souvent :**

```python
ventes = pd.read_csv(
    "ventes_magasins.csv",
    sep=";",              # séparateur : virgule par défaut, mais souvent ; en France
    decimal=",",          # virgule décimale française (42,70 au lieu de 42.70)
    encoding="utf-8",     # ou "latin-1" si tu vois des caractères bizarres (Ã©…)
    parse_dates=["date"], # convertit directement la colonne date
)
```

> ⚠️ **Erreurs courantes au chargement**
> - **Accents cassés** (`Ã©` à la place de `é`) → essaie `encoding="latin-1"`.
> - **Tout dans une seule colonne** → mauvais séparateur, mets `sep=";"`.
> - **Montants devenus du texte** → décimale française, mets `decimal=","`.
> - **`FileNotFoundError`** → le chemin est faux. Vérifie avec `import os; os.getcwd()` où Python te place.

### Depuis un Excel

```python
ventes = pd.read_excel("ventes_2024.xlsx", sheet_name="Ventes")
```

> 💡 `read_excel` nécessite parfois le paquet `openpyxl` (`pip install openpyxl`). Si une erreur le réclame, installe-le.

**Exemple métier.** Les services financiers travaillent presque toujours en `.xlsx` avec plusieurs onglets (un par mois, un par région). `sheet_name=None` charge **tous les onglets** d'un coup dans un dictionnaire de DataFrames.

---

## Le DataFrame : anatomie

```
              colonnes (axis=1)
        ┌──────────┬─────────┬──────────┐
 index  │  ville   │ ventes  │ montant  │
 ───────┼──────────┼─────────┼──────────┤
   0    │  Lille   │  1240   │  23.40   │  ← une LIGNE = une observation (une vente)
   1    │ Roubaix  │   980   │  58.90   │
   2    │Dunkerque │   760   │  12.00   │
        └──────────┴─────────┴──────────┘
            ↑ une COLONNE = une variable (une Series)
```

- Une **ligne** = une observation (ici, une vente).
- Une **colonne** = une variable (cf. Maths ch.3 : quantitative ou qualitative).
- L'**index** = l'étiquette de chaque ligne (0, 1, 2… par défaut).

---

## Explorer un fichier inconnu (le réflexe des 10 premières minutes)

Avant **tout** calcul, on regarde à quoi ressemblent les données. Cinq commandes, toujours les mêmes.

```python
ventes.head(5)     # les 5 premières lignes — à quoi ça ressemble ?
ventes.tail(3)     # les 3 dernières
ventes.shape       # (nb_lignes, nb_colonnes)
ventes.info()      # types, valeurs manquantes, mémoire
ventes.dtypes      # type de chaque colonne
ventes.describe()  # stats descriptives des colonnes numériques
```

**`ventes.shape` → sortie :**
```
(250000, 11)
```
*250 000 lignes, 11 colonnes. (Inutile d'ouvrir ça dans Excel !)*

**`ventes.info()` → sortie :**
```
RangeIndex: 250000 entries, 0 to 249999
Data columns (total 11 columns):
 #   Column         Non-Null Count   Dtype
---  ------         --------------   -----
 0   date           250000 non-null  object      ← ⚠️ date stockée en texte, pas en date !
 1   ville          250000 non-null  object
 2   type           250000 non-null  object
 3   categorie      248120 non-null  object      ← ⚠️ 1 880 valeurs manquantes
 4   produit        250000 non-null  object
 5   quantite       250000 non-null  int64
 6   prix_unitaire  250000 non-null  float64
 7   remise         250000 non-null  float64
 8   montant        249500 non-null  float64
 9   marge          249500 non-null  float64
 10  client_id      250000 non-null  int64
dtypes: float64(4), int64(2), object(5)
```

> 🔎 **Lecture d'`info()`.** Compare le `Non-Null Count` au nombre total de lignes : si c'est inférieur, il y a des **valeurs manquantes**. Et `Dtype = object` = pandas voit du texte. Une date ou un montant en `object`, c'est un signal de nettoyage à venir.

> ## 🎲 Devine avant de regarder !
>
> Avant de lancer `describe()`, **fais un pari** (oui, vraiment, mentalement ou à voix haute). C'est l'attitude de l'enquêteur : on formule une hypothèse, *puis* on vérifie.
>
> Pour le panier moyen de la Ch'ti Boutique, à ton avis :
> - La **moyenne** des montants sera plutôt autour de… 15 € ? 40 € ? 100 € ?
> - La **moyenne et la médiane** seront-elles proches, ou très différentes ?
> - Y aura-t-il un **montant max** délirant (un outlier) ?
>
> Note ton pari, puis déroule la sortie ci-dessous. 👇

**`ventes.describe()` → sortie :**
```
            montant       quantite
count  249500.000000  250000.000000
mean       38.420000       2.310000   ← moyenne (cf. Maths ch.3)
std        29.870000       1.450000   ← écart-type
min         0.000000       1.000000
25%        18.500000       1.000000   ← Q1
50%        31.200000       2.000000   ← médiane (Q2)
75%        49.900000       3.000000   ← Q3
max       890.000000      40.000000   ← max suspect → outlier ?
```

> 🎲 **Alors, ton pari ?** Moyenne ≈ **38 €**, médiane ≈ **31 €** (elles ne sont PAS proches !), et un **max à 890 €** = un panier énorme, clairement suspect. Si tu avais deviné « moyenne et médiane différentes + un max délirant », bravo, tu as l'œil d'un analyste. 🎯

> 🔗 **Tu retrouves le Chapitre 3 en entier.** `mean` = moyenne, `std` = écart-type, `25%/50%/75%` = quartiles, `max = 890 €` sur un panier ⇒ valeur potentiellement aberrante à investiguer (règle de l'IQR vue en maths). **L'écart entre `mean` (38,4) et la médiane `50%` (31,2)** indique une distribution **étirée vers la droite** par quelques gros paniers.
>
> 🔗 **Rappel maths express.** Tu te souviens ? Quand **moyenne > médiane**, la distribution est *tirée vers la droite* par quelques grandes valeurs. C'est exactement le réflexe du Chapitre 3 — sauf qu'ici, `describe()` te l'a donné gratuitement en une ligne au lieu de te faire tout calculer à la main.

> 🎯 **Ça te servira pour…** repérer en 2 secondes si une colonne contient des valeurs aberrantes (le `max` qui dépasse), avant même de tracer le moindre graphique. C'est ton premier geste de contrôle qualité sur n'importe quel fichier reçu.

> 💡 `describe(include="all")` ajoute les colonnes **qualitatives** (modalité la plus fréquente `top`, sa fréquence `freq`, nombre de valeurs distinctes `unique`).

---

## Sélection et filtrage

### Sélectionner des colonnes

```python
ventes["montant"]                 # une colonne → une Series
ventes[["ville", "montant"]]      # plusieurs colonnes → un DataFrame (double crochet !)
```

> ⚠️ **Erreur courante.** `ventes["ville", "montant"]` (crochets simples) plante. Pour plusieurs colonnes, il faut **une liste** → **doubles crochets** `[[...]]`.

### `loc` et `iloc` : par étiquette ou par position

```python
ventes.loc[0]                       # la ligne d'index 0 (par ÉTIQUETTE)
ventes.loc[0, "montant"]            # case précise : ligne 0, colonne "montant"
ventes.loc[0:4, ["ville", "montant"]]  # lignes 0 à 4 (INCLUS), 2 colonnes

ventes.iloc[0]                      # la 1re ligne (par POSITION)
ventes.iloc[0:5, 0:3]              # 5 premières lignes, 3 premières colonnes (5 et 3 EXCLUS)
```

> 🧠 **À retenir.** `loc` = **lo**cation par **étiquette** (et la borne de fin est **incluse**). `iloc` = **i**nteger location par **position** (borne de fin **exclue**, comme les listes Python). C'est LA source de confusion n°1 chez les débutants.

### Masques booléens (filtrage)

C'est ici que pandas devient magique. On écrit une **condition**, pandas renvoie les lignes qui la satisfont.

```python
# Toutes les ventes de Lille
ventes[ventes["ville"] == "Lille"]

# Les gros paniers (> 100 €)
ventes[ventes["montant"] > 100]

# Combiner : Lille ET montant > 50  → & (ET), | (OU), ~ (NON)
ventes[(ventes["ville"] == "Lille") & (ventes["montant"] > 50)]

# Appartenance à une liste
ventes[ventes["ville"].isin(["Lille", "Roubaix"])]
```

**Comment ça marche, étape par étape :**

```python
masque = ventes["montant"] > 100
print(masque.head())
```
**Sortie :**
```
0    False
1    False
2    False
3     True
4    False
Name: montant, dtype: bool
```
*Le masque est une Series de `True`/`False`. `ventes[masque]` ne garde que les lignes `True`.*

> ⚠️ **Erreurs courantes sur les masques**
> - Utiliser `and`/`or` (Python pur) au lieu de **`&`/`|`** (pandas). → `ValueError`.
> - Oublier les **parenthèses** autour de chaque condition : `ventes["a"]>1 & ventes["b"]<2` est mal interprété. Toujours `(...) & (...)`.

**Exemple métier.** « Combien de lignes de vente sont incohérentes ? » (utile pour un contrôle qualité / anti-fraude). On chasse trois signaux : un `montant` négatif (impossible), une `remise` aberrante (> 0,8, soit plus de 80 % de rabais) ou une `marge` négative (on vendrait à perte) :
```python
suspectes = ventes[(ventes["montant"] < 0)
                   | (ventes["remise"] > 0.8)
                   | (ventes["marge"] < 0)]
print(len(suspectes))
```

> 🎯 **Ça te servira pour…** isoler les cas bizarres à montrer au gérant de la Ch'ti Boutique (« voici les 12 ventes vendues à perte ou avec une remise de 90 %, jette un œil »). Le masque booléen, c'est ta pince à épiler : tu attrapes précisément les lignes qui t'intéressent dans un fichier de 250 000.

---

## Les valeurs manquantes (NaN)

`NaN` (*Not a Number*) = une case vide. Les ignorer fausse les calculs.

### Les détecter et les compter

```python
ventes.isna().sum()        # nombre de NaN par colonne
```
**Sortie :**
```
date               0
ville              0
type               0
categorie       1880
produit            0
quantite           0
prix_unitaire      0
remise             0
montant          500
marge            500
client_id          0
dtype: int64
```

```python
# Taux de manquants en %
(ventes.isna().mean() * 100).round(1)
```

### Trois stratégies — et comment choisir

| Stratégie | Code | Quand l'utiliser |
|---|---|---|
| **Supprimer** les lignes | `ventes.dropna(subset=["montant"])` | Peu de manquants (<5 %) et la valeur est essentielle |
| **Remplir** par une valeur | `ventes["categorie"].fillna("Inconnu")` | Variable **qualitative** : créer une modalité « Inconnu » |
| **Remplir** par une stat | `ventes["montant"].fillna(ventes["montant"].median())` | Variable **quantitative** : médiane (robuste aux outliers, cf. maths ch.3) |

```python
# Exemple combiné
ventes = ventes.dropna(subset=["montant"])               # montant : on supprime (essentiel)
ventes["categorie"] = ventes["categorie"].fillna("Inconnu")  # catégorie : on étiquette
```

> ⚠️ **Erreurs courantes**
> - **Remplir par la moyenne sans réfléchir.** Si la distribution est étirée (notre cas : moyenne ≠ médiane), la **médiane** est plus honnête.
> - **`dropna()` sans `subset`** supprime toute ligne ayant **au moins un** NaN, parfois la quasi-totalité du fichier. Précise toujours `subset=[...]`.
> - **Oublier de réaffecter** : `ventes.dropna(...)` **ne modifie pas** `ventes` ; il faut `ventes = ventes.dropna(...)`.

---

## Nettoyage léger

### Renommer des colonnes

```python
ventes = ventes.rename(columns={"montant": "montant_ttc", "quantite": "nb_articles"})
```

### Corriger les types

```python
# La date était en texte (object) → on la convertit en vraie date
ventes["date"] = pd.to_datetime(ventes["date"], format="%Y-%m-%d")

# Une colonne qui devrait être un entier
ventes["nb_articles"] = ventes["nb_articles"].astype(int)
```

> 🔗 **Pourquoi c'est crucial.** Une date en texte ne permet ni tri chronologique, ni extraction du mois (`ventes["date"].dt.month`), ni graphique temporel. Convertir les types, c'est rendre les données **calculables** — exactement le « qualifier le type avant de calculer » du Chapitre 3.

### Nettoyer le texte

```python
# Homogénéiser : "lille", "Lille ", "LILLE" → "Lille"
ventes["ville"] = ventes["ville"].str.strip().str.capitalize()
print(ventes["ville"].unique())
```
**Sortie :**
```
['Lille' 'Roubaix' 'Tourcoing' 'Dunkerque' 'Valenciennes' 'Amiens']
```

### Doublons

```python
ventes.duplicated().sum()          # combien de lignes en double ?
ventes = ventes.drop_duplicates()  # on les supprime
```

> ⚠️ Attention : `duplicated()` cherche des lignes **entièrement** identiques. Pour des doublons « métier » (par exemple deux fois la même vente d'un client le même jour), précise un sous-ensemble de colonnes : `drop_duplicates(subset=["date", "client_id", "produit"])`.

---

## groupby et agrégations

C'est **le cœur de l'analyse** : « par magasin / par catégorie / par mois… combien ? quelle moyenne ? ». Le schéma est toujours **découper → calculer → recombiner** (*split-apply-combine*).

> ✂️ **`groupby` en image.** Imagine que tu vides un grand sac de tickets de caisse sur une table, puis que tu fais **trois tas** : un tas Lille, un tas Roubaix, un tas Dunkerque. Ensuite tu additionnes chaque tas séparément. Voilà, c'est tout ce que fait `groupby("ville")["montant"].sum()` : il **range par paquets** puis **calcule sur chaque paquet**.

> 🎲 **Devine avant de regarder.** Lequel des trois magasins de la Ch'ti Boutique va faire le plus gros chiffre d'affaires, à ton avis ? Et le plus petit ? Note ton pari, puis regarde la sortie.

```python
# Chiffre d'affaires total par ville
ventes.groupby("ville")["montant"].sum()
```
**Sortie :**
```
ville
Amiens        201380.10
Dunkerque     289450.30
Lille         512340.80
Roubaix       398120.50
Tourcoing     245900.60
Valenciennes  178220.40
Name: montant, dtype: float64
```

```python
# Plusieurs stats d'un coup
ventes.groupby("ville")["montant"].agg(["count", "sum", "mean", "median"])
```
**Sortie :**
```
              count        sum       mean  median
ville
Amiens        52000  201380.10      38.73    32.0
Dunkerque     76000  289450.30      38.08    31.0
Lille        102000  512340.80      50.23    41.5
Roubaix       71500  398120.50      55.68    46.0
Tourcoing     61000  245900.60      40.31    33.0
Valenciennes  47000  178220.40      37.92    31.0
```

```python
# Croiser deux dimensions : CA par ville ET par catégorie
ventes.groupby(["ville", "categorie"])["montant"].sum()

# La marge moyenne par ville (on exploite la colonne 'marge' du fichier)
ventes.groupby("ville")["marge"].mean()
```

> 🔗 **C'est de la statistique descriptive « par groupe ».** Le Chapitre 3 t'a appris à calculer une moyenne ; `groupby` la calcule pour **chaque sous-population** d'un coup. C'est ce qui transforme « le panier moyen est de 42 € » en « le panier moyen est de 50 € à Lille mais 38 € à Dunkerque » — un constat **actionnable**.

> 🎯 **Ça te servira pour…** remplir un tableau de bord. Chaque case « CA par magasin », « ventes par mois », « panier moyen par catégorie » que tu verras dans Power BI ou Looker Studio, c'est **un `groupby` qui tourne derrière**. Tu apprends ici le moteur de tous les KPI que tu présenteras demain.

> 💡 **`pivot_table`** fait la même chose façon tableau croisé Excel :
> ```python
> ventes.pivot_table(index="ville", columns="categorie",
>                    values="montant", aggfunc="sum")
> ```

---

## Tri

```python
# Les villes du plus gros CA au plus petit
ca = ventes.groupby("ville")["montant"].sum()
ca.sort_values(ascending=False)

# Trier un DataFrame sur une colonne
ventes.sort_values("montant", ascending=False).head(10)  # top 10 des plus gros paniers

# Trier sur plusieurs colonnes
ventes.sort_values(["ville", "montant"], ascending=[True, False])
```

> 💡 Pour un classement, `nlargest` / `nsmallest` sont plus directs : `ventes.nlargest(10, "montant")`.

---

## Premières visualisations

Un graphique révèle en un clin d'œil ce qu'un tableau de chiffres cache. On utilise **matplotlib** (la base) et **seaborn** (plus joli, plus rapide).

```python
import matplotlib.pyplot as plt
import seaborn as sns
```

### Histogramme — la forme d'une distribution

```python
sns.histplot(data=ventes, x="montant", bins=50)
plt.title("Distribution des montants de panier")
plt.xlabel("Montant (€)")
plt.show()
```
*Tu verras une courbe **étirée vers la droite** : beaucoup de petits paniers, quelques très gros. C'est cohérent avec moyenne > médiane (ch.3).*

### Diagramme en barres — comparer des catégories

```python
ca = ventes.groupby("ville")["montant"].sum().sort_values()
sns.barplot(x=ca.values, y=ca.index)
plt.title("Chiffre d'affaires par magasin")
plt.xlabel("CA (€)")
plt.show()
```

### Boxplot — repérer les outliers

> 🎲 **Devine avant de regarder.** Avant de tracer ce boxplot, parie : vas-tu voir des **points isolés tout en haut** (= des paniers anormalement gros) ? Le gérant t'a dit qu'il y avait « un truc qui cloche »… le boxplot est l'outil qui le révèle d'un coup d'œil.

```python
sns.boxplot(data=ventes, x="ville", y="montant")
plt.title("Dispersion des paniers par magasin")
plt.show()
```
*La « boîte » va de Q1 à Q3 (l'IQR du ch.3), le trait central est la médiane, les points isolés au-dessus sont les **valeurs aberrantes** détectées automatiquement.*

> 🔗 **Le boxplot, c'est le Chapitre 3 dessiné.** Boîte = IQR, ligne = médiane, moustaches = 1,5×IQR, points = outliers. Tu n'as plus besoin de calculer la règle de l'IQR à la main : seaborn la trace pour toi.

> ⚠️ **Erreurs courantes en viz**
> - **Oublier `plt.show()`** dans un script (rien ne s'affiche). Dans un notebook, ce n'est pas obligatoire.
> - **Titres et axes absents.** Un graphique sans titre ni unité est inexploitable pour un décideur. Toujours `title` + `xlabel` + `ylabel`.
> - **Trop de barres** (50 magasins) → illisible. Filtre ou agrège (top 10).

---

## La démarche EDA, en 6 étapes

L'EDA n'est pas une suite de commandes au hasard, c'est une **méthode** :

```
1. CHARGER       → read_csv, vérifier que ça s'est bien passé
2. DÉCOUVRIR     → shape, head, info, dtypes  (« qu'est-ce que j'ai ? »)
3. NETTOYER      → NaN, types, doublons, texte (« est-ce fiable ? »)
4. DÉCRIRE       → describe, groupby          (« que disent les chiffres ? »)
5. VISUALISER    → hist, barres, boxplot      (« à quoi ça ressemble ? »)
6. CONCLURE      → 3-5 constats métier écrits  (« et alors ? »)
```

> 🧭 L'étape 6 est **la plus importante et la plus oubliée**. Un Data Analyst n'est pas payé pour produire des graphiques, mais pour produire des **constats** : « Lille génère 41 % du CA mais a le plus de gros paniers aberrants en espèces → à vérifier. »

---

## 🏆 Défi du module — « Les 3 anomalies cachées de la Ch'ti Boutique »

Le gérant avait raison : il y a **3 trucs qui clochent** dans son fichier `ventes_magasins.csv`. Avant de faire les TP guidés, joue les détectives : **retrouve-les toi-même** à partir de ce que tu viens d'apprendre.

🕵️ **Ta mission :** ouvre le fichier (le générateur du corrigé TP1 plus bas te le fabrique si tu ne l'as pas), et débusque ces 3 anomalies. Indices :

1. **Anomalie de TYPE** — une colonne contient une information de date… mais pandas ne la voit pas comme une date. *(Indice : regarde `info()` et la colonne `Dtype`.)*
2. **Anomalie de TROUS** — deux colonnes ont des cases vides (`NaN`). Lesquelles, et combien ? *(Indice : `isna().sum()`.)*
3. **Anomalie de MONSTRE** — il existe des paniers au montant délirant (outliers) par rapport au panier typique. Où se cachent-ils, et dans quelle catégorie ? *(Indice : `describe()` + un boxplot + un masque booléen.)*

Tu as 4 commandes pour gagner : `info()`, `isna().sum()`, `describe()`, et un `boxplot`. À toi de jouer ! 🔍

<details>
<summary>🏆 Solution du défi (clique seulement après avoir essayé)</summary>

```python
import pandas as pd
ventes = pd.read_csv("ventes_magasins.csv")

# Anomalie 1 — TYPE : la colonne 'date' est en object (texte), pas en datetime
ventes.info()        # → 'date'  ... object   ← coupable !

# Anomalie 2 — TROUS : categorie (~5 %) et montant (quelques centaines) ont des NaN
print(ventes.isna().sum())

# Anomalie 3 — MONSTRE : des montants très au-dessus du panier médian
print(ventes["montant"].describe())          # max énorme vs médiane
gros = ventes[ventes["montant"] > 150]
print(gros["categorie"].value_counts())      # concentrés sur une catégorie → à investiguer
```

**Verdict de l'enquête :**
1. ✅ `date` est stockée en **texte** (`object`) → impossible de trier par mois tant qu'on ne convertit pas.
2. ✅ `categorie` (~5 % de vides) et `montant` (quelques centaines de vides) ont des **NaN**.
3. ✅ Des **paniers aberrants** (> 150 €, voire un max ~890 €) ressortent comme points isolés sur le boxplot, souvent sur une même catégorie → contrôle anti-fraude recommandé.

Tu viens de mener ta première mini-EDA en autonomie. C'est *littéralement* le métier. 🎉
</details>

---

## Travaux pratiques — mener une EDA sur le retail Nord

> **Dataset :** `ventes_magasins.csv` de l'univers **NordRetail** (ventes des magasins du Nord : Lille, Roubaix, Tourcoing, Dunkerque, Valenciennes, Amiens + e-commerce).
> Colonnes : `date`, `ville`, `type`, `categorie`, `produit`, `quantite`, `prix_unitaire`, `remise`, `montant`, `marge`, `client_id`.
> Pas le fichier sous la main ? Le formateur te le fournit (dossier `data/` du brief), ou utilise le générateur du corrigé du TP1.

### TP1 — Charger et découvrir

Charge le fichier, affiche sa forme, ses 5 premières lignes, ses types, et identifie : (a) combien de lignes/colonnes, (b) quelles colonnes ont des valeurs manquantes, (c) quelle colonne a un type incorrect.

<details>
<summary>✅ Corrigé</summary>

```python
import pandas as pd
import numpy as np

# --- Si tu n'as pas le fichier, génère un dataset réaliste (schéma NordRetail) : ---
rng = np.random.default_rng(42)
n = 20000
prix = np.round(rng.gamma(2.2, 18, n), 2)
qte = rng.integers(1, 6, n)
remise = rng.choice([0.0, 0.1, 0.2, 0.3], n, p=[.6, .2, .15, .05])
montant = np.round(prix * qte * (1 - remise), 2)
df = pd.DataFrame({
    "date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 365, n), "D"),
    "ville": rng.choice(["Lille", "Roubaix", "Tourcoing", "Dunkerque", "Valenciennes", "Amiens"],
                        n, p=[.28, .2, .15, .15, .12, .10]),
    "type": rng.choice(["Magasin", "E-commerce"], n, p=[.7, .3]),
    "categorie": rng.choice(["Alimentaire", "Textile", "Maison", "Électroménager", None],
                           n, p=[.4, .25, .2, .1, .05]),
    "produit": rng.choice(["Pull", "Lampe", "Réfrigérateur", "Café", "Chaise"], n),
    "quantite": qte,
    "prix_unitaire": prix,
    "remise": remise,
    "montant": montant,
    "marge": np.round(montant * rng.uniform(0.2, 0.4, n), 2),
    "client_id": rng.integers(1, 5000, n),
})
df.loc[rng.choice(n, 100, replace=False), ["montant", "marge"]] = np.nan  # injecte des NaN
df["date"] = df["date"].dt.strftime("%Y-%m-%d")                # date en TEXTE (volontaire)
df.to_csv("ventes_magasins.csv", index=False)
# -----------------------------------------------------------------

ventes = pd.read_csv("ventes_magasins.csv")

print("Forme :", ventes.shape)        # (a)
ventes.head()
ventes.info()                          # (b) categorie + montant + marge ont des NaN
ventes.dtypes                          # (c) 'date' est en object → à convertir
```
**Constats :** 20 000 lignes × 11 colonnes ; `categorie`, `montant` et `marge` ont des manquants ; `date` est stockée en texte (`object`).
</details>

### TP2 — Nettoyer

Convertis `date` en vraie date, remplis les `categorie` manquantes par « Inconnu », supprime les lignes sans `montant`, homogénéise la casse de `ville`, et vérifie qu'il ne reste plus de doublon.

<details>
<summary>✅ Corrigé</summary>

```python
ventes["date"] = pd.to_datetime(ventes["date"], format="%Y-%m-%d")
ventes["categorie"] = ventes["categorie"].fillna("Inconnu")
ventes = ventes.dropna(subset=["montant"])
ventes["ville"] = ventes["ville"].str.strip().str.capitalize()
ventes = ventes.drop_duplicates()

print(ventes.isna().sum())   # plus aucun NaN sur montant
print(ventes.dtypes)         # date est maintenant datetime64
```
**Constat :** données propres, types corrects, prêtes pour l'analyse.
</details>

### TP3 — Décrire et filtrer

(a) Affiche `describe()` sur `montant`. La moyenne et la médiane sont-elles proches ? Que conclure ? (b) Combien de ventes dépassent 150 € ? (c) Quel est le panier moyen **uniquement** pour les ventes en e-commerce (`type == "E-commerce"`) ?

<details>
<summary>✅ Corrigé</summary>

```python
print(ventes["montant"].describe())
# moyenne (~40) > médiane (~33) → distribution étirée à droite par les gros paniers

gros = ventes[ventes["montant"] > 150]
print("Ventes > 150 € :", len(gros))

ecommerce = ventes[ventes["type"] == "E-commerce"]
print("Panier moyen en e-commerce :", round(ecommerce["montant"].mean(), 2), "€")
```
**Constat :** moyenne > médiane ⇒ on privilégiera la **médiane** pour parler du panier « typique » au directeur (ch.3).
</details>

### TP4 — Agréger et trier

Calcule le chiffre d'affaires (`sum`), le nombre de ventes (`count`) et le panier médian par ville, trie par CA décroissant. Puis fais un tableau croisé CA par ville × catégorie.

<details>
<summary>✅ Corrigé</summary>

```python
synthese = (ventes.groupby("ville")["montant"]
            .agg(CA="sum", nb_ventes="count", panier_median="median")
            .sort_values("CA", ascending=False))
print(synthese)

croise = ventes.pivot_table(index="ville", columns="categorie",
                            values="montant", aggfunc="sum").round(0)
print(croise)
```
**Constat :** Lille domine le CA (≈45 % des ventes) ; l'Alimentaire est partout la 1re catégorie.
</details>

### TP5 — Visualiser

Produis : (a) l'histogramme des montants, (b) le diagramme en barres du CA par magasin, (c) le boxplot des montants par magasin. Commente les outliers visibles.

<details>
<summary>✅ Corrigé</summary>

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

sns.histplot(data=ventes, x="montant", bins=50, ax=axes[0])
axes[0].set_title("Distribution des montants")

ca = ventes.groupby("ville")["montant"].sum().sort_values()
sns.barplot(x=ca.values, y=ca.index, ax=axes[1])
axes[1].set_title("CA par magasin")

sns.boxplot(data=ventes, x="ville", y="montant", ax=axes[2])
axes[2].set_title("Dispersion par magasin")

plt.tight_layout()
plt.show()
```
**Constat :** distribution étirée à droite ; chaque magasin présente des points isolés au-dessus de la moustache haute = **paniers aberrants** à investiguer.
</details>

### TP6 — Synthèse métier (le livrable !)

Rédige (en français, en dehors du code) **5 constats** destinés au responsable régional, chacun appuyé sur un chiffre issu de ton analyse, plus **1 recommandation** et **1 point de vigilance** sur la qualité des données.

<details>
<summary>✅ Exemple de corrigé</summary>

> **Note d'analyse — Ventes magasins Nord (2024)**
> 1. **Lille concentre ~45 % du chiffre d'affaires régional** (≈512 k€), devant Roubaix puis Dunkerque.
> 2. **Le panier médian est de ~33 €**, mais la moyenne (~40 €) est tirée par une minorité de gros paniers : communiquer sur la **médiane** auprès des équipes.
> 3. **L'Alimentaire est la 1re catégorie partout**, mais le Textile pèse plus à Roubaix → opportunité d'assortiment local.
> 4. **~30 % des ventes passent par le e-commerce** (`type`) ; le canal magasin reste majoritaire, surtout à Dunkerque.
> 5. **Des paniers > 150 € apparaissent comme outliers** sur le boxplot, souvent sur l'Électroménager → contrôle recommandé.
>
> **Recommandation :** concentrer les opérations promotionnelles sur l'Alimentaire à Lille (effet volume).
> **Vigilance qualité :** 5 % des catégories étaient manquantes (recodées « Inconnu ») et la colonne date arrivait en texte → fiabiliser la saisie en caisse.

> 🎯 **C'est ça, le métier.** Les 5 commandes pandas ne valent rien sans ces 7 lignes de conclusion.
</details>

---

## Vidéos d'auto-formation

> ⚠️ Vérifie toujours que la vidéo correspond bien (les chaînes renomment parfois leurs vidéos). En cas de doute, utilise le lien de recherche.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Pandas Python Français — Introduction + Analyse du Titanic (17/30) | Machine Learnia | 🇫🇷 FR | ~20 min | https://www.youtube.com/watch?v=zZkNOdBWgFQ | Premiers pas pandas + mini-EDA sur un vrai dataset, en français |
| Apprendre Python, Numpy, Pandas pour la Data Science (cours complet débutant) | Machine Learnia | 🇫🇷 FR | ~1 h+ | https://www.youtube.com/watch?v=LwkWwxg10IU | Panorama Python/numpy/pandas pour démarrer la data |
| Python Pandas Tutorial (Part 1): Getting Started with Data Analysis | Corey Schafer | 🇬🇧 EN | ~30 min | https://www.youtube.com/watch?v=ZyhVh-qRZPA | DataFrame, Series, chargement et exploration — la référence anglophone |
| Exploratory Data Analysis in Pandas | Alex The Analyst | 🇬🇧 EN | ~30 min | https://www.youtube.com/watch?v=Liv6eeb1VfE | Une EDA complète pas à pas avec pandas |
| Réaliser une analyse exploratoire avec pandas-profiling | (recherche) | 🇫🇷 FR | ~15 min | https://www.youtube.com/results?search_query=analyse+exploratoire+python+pandas+profiling | Générer un rapport EDA automatique |

> 💡 Lien de secours pour explorer d'autres tutos : https://www.youtube.com/results?search_query=pandas+débutant+analyse+de+données

---

## Quiz — 5 QCM

**Q1.** Quelle commande donne le nombre de lignes et de colonnes d'un DataFrame `df` ?
- A) `df.size`  B) `df.shape`  C) `df.count()`  D) `df.len()`

**Q2.** Pour filtrer les ventes de Lille **dont le montant dépasse 50 €**, quelle écriture est correcte ?
- A) `df[df.ville=="Lille" and df.montant>50]`
- B) `df[(df.ville=="Lille") & (df.montant>50)]`
- C) `df[df.ville=="Lille" & df.montant>50]`
- D) `df.loc["Lille", 50]`

**Q3.** Une colonne `date` apparaît en `object` dans `info()`. Que faut-il faire avant de la trier chronologiquement ?
- A) Rien, `object` convient  B) `df["date"].astype(int)`
- C) `pd.to_datetime(df["date"])`  D) `df.dropna()`

**Q4.** Pour calculer le chiffre d'affaires total **par magasin**, on écrit :
- A) `df["montant"].sum()`
- B) `df.groupby("ville")["montant"].sum()`
- C) `df.sort_values("ville").sum()`
- D) `df["ville"].value_counts()`

**Q5.** La moyenne d'une colonne de montants est **nettement supérieure** à sa médiane. Que peux-tu en déduire (cf. Maths ch.3) ?
- A) Il y a des valeurs manquantes  B) La distribution est étirée vers la droite par de grandes valeurs
- C) Toutes les valeurs sont identiques  D) C'est une erreur de calcul

<details>
<summary>✅ Réponses</summary>

1. **B** — `df.shape` renvoie `(lignes, colonnes)`. (`size` = nombre total de cases.)
2. **B** — masques pandas : `&` (pas `and`) + parenthèses obligatoires autour de chaque condition.
3. **C** — `pd.to_datetime` convertit le texte en vraie date, prérequis au tri chronologique et à `.dt.month`.
4. **B** — `groupby` puis agrégation : c'est le schéma split-apply-combine.
5. **B** — moyenne > médiane ⇒ distribution asymétrique à droite (quelques grandes valeurs / outliers tirent la moyenne vers le haut).
</details>

---

## À retenir

- **`import pandas as pd`** : la convention universelle. Le **DataFrame** = un tableur piloté au clavier, reproductible.
- **Réflexe d'ouverture de fichier** : `shape` → `head` → `info` → `dtypes` → `describe`. Toujours, avant tout calcul.
- **`info()` est ton détecteur de problèmes** : valeurs manquantes (Non-Null Count) et mauvais types (`object` sur une date/un nombre).
- **Filtrage = masque booléen** : `df[(cond1) & (cond2)]` — `&`/`|`, jamais `and`/`or`, et **parenthèses** partout.
- **`loc`** = par étiquette (fin incluse) ; **`iloc`** = par position (fin exclue).
- **NaN** : supprimer (essentiel & rare), remplir par « Inconnu » (qualitatif), remplir par la médiane (quantitatif). Et **réaffecter** le résultat.
- **`groupby`** = la statistique descriptive **par groupe** ; c'est le cœur de l'analyse métier.
- **Viz** : histogramme (forme), barres (comparaison), boxplot (dispersion + outliers). Toujours titrer et légender.
- **L'EDA finit par des CONSTATS écrits**, pas par des graphiques. C'est là qu'est ta valeur.
- 🔗 Tout repose sur le **Chapitre 3 « Statistiques descriptives »** : pandas ne fait qu'industrialiser ce que tu sais déjà calculer à la main.

> ## 🎬 Fin de l'enquête à la Ch'ti Boutique
>
> Souviens-toi du lundi matin : une clé USB, un fichier en vrac, un gérant qui « sentait » un problème. Te voilà capable, en quelques lignes de pandas, de lui répondre :
>
> > *« Lille fait 45 % du CA, le panier typique est de 33 € (pas 40, la moyenne ment un peu), l'Alimentaire domine partout, et j'ai repéré des paniers en espèces anormalement gros à surveiller. »*
>
> Tu es passé du **chaos** à **3-5 phrases qui éclairent une décision**. C'est ça, faire parler les données. 🕵️➡️💡
>
> La suite logique : ces constats deviendront des **graphiques interactifs dans un tableau de bord** (Power BI / Looker Studio). Le `groupby` que tu maîtrises maintenant est le moteur caché de chacun de ces KPI. Bon enchaînement ! 🚀
