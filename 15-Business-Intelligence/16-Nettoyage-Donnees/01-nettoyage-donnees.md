# 01 — Stratégies de nettoyage de données

| | |
|---|---|
| **Phase** | Phase 3 — Flux & BI |
| **Durée estimée** | ~25 h |
| **Compétence visée** | **C3** — Nettoyer et préparer les données (niveau 1) |
| **Pré-requis** | Module **1.2** (manipulation pandas : `read_csv`, `DataFrame`, `Series`, filtres, `groupby`) · **Maths chapitre 3** (statistiques descriptives : moyenne, médiane, mode, quartiles, IQR, écart-type) |
| **Format** | Cours + TP guidés + quiz |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

1. **Définir** ce qu'est la qualité des données et citer ses 5 dimensions (complétude, exactitude, cohérence, unicité, validité).
2. **Détecter** les problèmes classiques d'un jeu de données : valeurs manquantes, doublons, formats erronés, incohérences, valeurs aberrantes.
3. **Choisir et justifier** une stratégie de traitement des valeurs manquantes (suppression vs imputation moyenne / médiane / mode vs substitution) selon le contexte métier.
4. **Dédoublonner** un jeu de données proprement (doublons stricts et doublons « flous »).
5. **Normaliser / uniformiser** dates, casse, unités et encodage.
6. **Traiter** les valeurs aberrantes (outliers) avec la méthode IQR et le z-score (rappel Maths ch.3).
7. **Documenter** tes règles de nettoyage et **valider** la qualité du jeu après traitement.

---

## Pourquoi le nettoyage = 80 % du travail

On le résume souvent par une phrase : **« Garbage in, garbage out »** (des déchets en entrée → des déchets en sortie). Le dashboard le plus joli, le modèle le plus sophistiqué ne valent rien si les données qui les alimentent sont fausses.

Plusieurs enquêtes métier (CrowdFlower, Anaconda, Forbes) reviennent toutes au même ordre de grandeur : **un·e data analyst passe 60 à 80 % de son temps à collecter, nettoyer et préparer les données**, et seulement 20 % à les analyser.

> **Exemple concret.** Une enseigne de prêt-à-porter du Nord (magasins à Lille, Roubaix, Valenciennes) exporte ses ventes depuis 3 caisses différentes. La caisse de Lille écrit les villes en majuscules (`LILLE`), celle de Roubaix en minuscules (`roubaix`), celle de Valenciennes avec des fautes (`Valencienne`). Si tu fais un `groupby("ville")` sans nettoyer, tu obtiens **6 villes au lieu de 3** et ton CA par ville est faux. C'est exactement le genre d'erreur invisible qui fausse une décision business.

Nettoyer, ce n'est pas « faire le ménage pour faire joli » : c'est **rendre les données fiables pour décider**. C'est une compétence cœur du métier, pas une corvée annexe.

---

## La qualité des données : 5 dimensions

Avant de nettoyer, il faut savoir **ce qu'on évalue**. La qualité d'un jeu de données se mesure sur 5 dimensions.

| Dimension | Question posée | Exemple de défaut (retail) |
|---|---|---|
| **Complétude** | Toutes les valeurs attendues sont-elles présentes ? | 12 % des clients sans email |
| **Exactitude** | Les valeurs reflètent-elles la réalité ? | Un prix de `-15 €`, un âge de `200` ans |
| **Cohérence** | Les données se contredisent-elles entre elles / entre sources ? | `date_livraison` antérieure à `date_commande` |
| **Unicité** | Chaque entité n'apparaît-elle qu'une fois ? | Le même client présent 3 fois |
| **Validité** | Les valeurs respectent-elles le format / les règles attendus ? | Email `jean@@mail`, code postal `5900` (4 chiffres) |

> **Mémo.** Complétude / Exactitude / Cohérence / Unicité / Validité → **« CECUV »**. Garde ce checklist en tête : pour chaque colonne, demande-toi laquelle de ces 5 dimensions est menacée.

---

## Identifier et traiter chaque type de problème

On va dérouler chaque problème selon le même schéma : **Détection → Stratégie → Code → Justification → Erreurs courantes**.

Le jeu de données fil rouge : un export `ventes.csv` d'une boutique e-commerce du Nord.

```python
import pandas as pd
import numpy as np

df = pd.read_csv("ventes.csv")

# Premier réflexe : toujours observer AVANT de toucher
print(df.shape)        # (lignes, colonnes)
print(df.info())       # types + valeurs non-nulles par colonne
print(df.describe(include="all"))  # stats descriptives
df.head(10)
```

> **Règle d'or n°1 : on observe avant d'agir.** Ne lance jamais un `dropna()` ou un `fillna()` sans avoir d'abord regardé l'ampleur et la nature du problème.

---

### Valeurs manquantes (dimension : complétude)

#### Détection

```python
# Nombre de valeurs manquantes par colonne
df.isna().sum()

# Pourcentage de manquants par colonne (plus parlant)
(df.isna().mean() * 100).round(1).sort_values(ascending=False)

# Visualiser les lignes concernées
df[df["email"].isna()]
```

Attention : les manquants ne sont pas toujours des `NaN` « propres ». Ils se cachent souvent sous forme de chaînes : `""`, `" "`, `"NA"`, `"N/A"`, `"inconnu"`, `"-"`, `"null"`, `0` parfois. **Repère-les et convertis-les en vrais `NaN`** avant de compter :

```python
valeurs_nulles = ["", " ", "NA", "N/A", "null", "inconnu", "-"]
df = df.replace(valeurs_nulles, np.nan)
```

#### Stratégies (et comment choisir)

| Stratégie | Quand l'utiliser | Risque |
|---|---|---|
| **Suppression de lignes** (`dropna`) | Peu de lignes touchées (< ~5 %) **et** manquants aléatoires | Perte d'info, biais si non aléatoire |
| **Suppression de colonnes** | Colonne quasi vide (> ~50-70 % de manquants) et peu utile | Perte d'une variable |
| **Imputation par la moyenne** | Variable **numérique** ~symétrique, sans outliers | Sensible aux valeurs extrêmes |
| **Imputation par la médiane** | Variable **numérique** asymétrique ou avec outliers | Choix par défaut le plus sûr |
| **Imputation par le mode** | Variable **catégorielle** (ville, catégorie produit) | Sur-représente la modalité dominante |
| **Substitution métier** | Une valeur a un sens connu (`remise` manquante = `0`) | Faux si l'hypothèse est mauvaise |

#### Code

```python
# 1) Suppression : lignes sans identifiant client (donnée critique)
df = df.dropna(subset=["client_id"])

# 2) Suppression d'une colonne quasi vide
taux = df.isna().mean()
df = df.drop(columns=taux[taux > 0.7].index)

# 3) Imputation médiane (numérique, robuste aux outliers)
df["age"] = df["age"].fillna(df["age"].median())

# 4) Imputation moyenne (numérique symétrique)
df["note_satisfaction"] = df["note_satisfaction"].fillna(
    df["note_satisfaction"].mean()
)

# 5) Imputation mode (catégorielle)
df["ville"] = df["ville"].fillna(df["ville"].mode()[0])

# 6) Substitution métier : pas de remise = 0
df["remise"] = df["remise"].fillna(0)
```

#### Justification

Le choix se **justifie toujours par le contexte**, pas par habitude :

- `client_id` manquant → on **supprime** : sans identifiant, la ligne est inexploitable pour une analyse client, et on ne peut pas inventer un ID.
- `age` → **médiane** plutôt que moyenne : si quelques clients ont saisi `120` ans (erreur), la moyenne serait tirée vers le haut, pas la médiane.
- `ville` → **mode** : c'est une catégorie, la moyenne n'a aucun sens ; on attribue la ville la plus fréquente (ou mieux : `"Inconnu"` si on ne veut pas fausser la répartition géographique).
- `remise` → **0** : métier, une absence de remise = pas de remise. Ici imputer par la moyenne serait une **faute** (on inventerait des promos).

> **Encadré — erreurs courantes (valeurs manquantes)**
> - **Imputer par la moyenne une variable catégorielle** (`ville`, `catégorie`) → non-sens, utilise le mode.
> - **Imputer une donnée critique** (identifiant, clé) au lieu de la supprimer → tu fabriques de la fausse donnée.
> - **Imputer avant de séparer train/test** en ML → fuite de données (vu plus tard, mais à connaître).
> - **Oublier les faux manquants** (`"NA"`, `""`, `0`) → tes comptes de `isna()` sont sous-estimés.
> - **Imputer 40 % d'une colonne par la médiane** → tu écrases la variance, la colonne devient quasi constante. Mieux vaut alors créer un indicateur `age_manquant` (booléen) ou supprimer la colonne.

---

### Doublons (dimension : unicité)

#### Détection

```python
# Doublons stricts (lignes 100 % identiques)
df.duplicated().sum()
df[df.duplicated(keep=False)].sort_values("client_id")

# Doublons "métier" : même client/même commande sur quelques colonnes clés
df.duplicated(subset=["client_id", "date_commande", "produit"]).sum()
```

#### Stratégie

- **Doublon strict** → on supprime, on garde une occurrence.
- **Doublon métier** (clé fonctionnelle dupliquée) → on définit la clé d'unicité et on déduplique dessus, en décidant **laquelle garder** (la plus récente, la plus complète…).
- **Doublon flou** (`Jean Dupont` vs `jean dupont` vs `Jean  Dupont`) → on **normalise d'abord** (casse, espaces) puis on déduplique.

#### Code

```python
# Doublons stricts : on garde la première occurrence
df = df.drop_duplicates()

# Doublons métier : une seule ligne par (client, commande, produit),
# on garde la dernière (la plus à jour)
df = df.sort_values("date_maj").drop_duplicates(
    subset=["client_id", "date_commande", "produit"],
    keep="last"
)
```

#### Justification

`keep="last"` parce que la colonne `date_maj` indique que la dernière ligne est la version la plus récente : si un prix a été corrigé, on garde la correction. Le choix `first` / `last` n'est **jamais neutre** : il faut savoir quelle ligne porte la bonne information.

> **Encadré — erreurs courantes (doublons)**
> - **`drop_duplicates()` sans réfléchir à la clé** → tu peux supprimer des lignes légitimes (un client peut commander 2 fois le même produit à 2 dates différentes : ce n'est PAS un doublon).
> - **Dédoublonner avant de normaliser** → les doublons flous (`LILLE` / `lille`) passent au travers.
> - **Oublier `keep`** → tu gardes la première au hasard, peut-être la périmée.

---

### Formats erronés & uniformisation (dimensions : validité, cohérence)

C'est le gros morceau du nettoyage retail. On uniformise **casse, espaces, dates, unités, encodage**.

#### Casse et espaces (texte)

```python
# Détection : combien de variantes d'une même ville ?
df["ville"].value_counts()
# -> LILLE 120, Lille 80, lille 15, Roubaix 60, roubaix 10, Valencienne 5 ...

# Stratégie : tout passer en Title Case + retirer espaces parasites
df["ville"] = (
    df["ville"]
    .str.strip()        # espaces début/fin
    .str.replace(r"\s+", " ", regex=True)  # espaces multiples internes
    .str.title()        # Lille, Roubaix...
)

# Corrections ciblées des fautes connues (table de mapping)
corrections = {"Valencienne": "Valenciennes", "Lile": "Lille"}
df["ville"] = df["ville"].replace(corrections)
```

#### Dates

```python
# Détection : la colonne est en texte, formats mélangés
df["date_commande"].head()
# -> "2024-03-01", "01/03/2024", "1 mars 2024"...

# Conversion en vrai datetime (formats mixtes)
df["date_commande"] = pd.to_datetime(
    df["date_commande"],
    errors="coerce",   # les dates illisibles -> NaT (à traiter ensuite)
    dayfirst=True      # format FR : jour en premier
)

# Cohérence : repérer les dates impossibles
df[df["date_commande"] > pd.Timestamp.today()]  # dans le futur
```

#### Unités & types numériques

```python
# Prix stocké en texte "12,50 €" -> float 12.50
df["prix"] = (
    df["prix"].astype(str)
    .str.replace("€", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

# Forcer les types attendus (validité)
df["client_id"] = df["client_id"].astype("Int64")  # entier nullable
df["quantite"]  = pd.to_numeric(df["quantite"], errors="coerce")
```

> 📌 **`Int64` (I majuscule) vs `int64` (i minuscule)**
> Ce n'est **pas** une coquille : la casse change tout.
> - **`"Int64"` (I majuscule)** = type entier **nullable** de pandas. Il accepte les valeurs manquantes (`pd.NA`) tout en restant un entier — indispensable quand une colonne d'entiers contient des trous (un `client_id` manquant reste un entier, pas un `7.0` flottant).
> - **`"int64"` (i minuscule)** = entier NumPy classique, qui **ne supporte pas les NaN**. `df["client_id"].astype("int64")` **plante** (`IntCastingNaNError` / `ValueError`) dès qu'il y a une seule valeur manquante.
>
> Règle pratique : pour un entier susceptible d'avoir des manquants, utilise toujours **`"Int64"`**. À défaut, pandas rétrograde silencieusement la colonne en `float64` et tes identifiants s'affichent en `12.0` au lieu de `12`.

#### Encodage

L'encodage casse les accents (`Ã©` au lieu de `é`, `RouBaix` illisible). À traiter **dès la lecture** :

```python
# Si tu vois des caractères bizarres, c'est l'encodage à la lecture
df = pd.read_csv("ventes.csv", encoding="utf-8")
# Fichiers Windows/Excel FR souvent en latin-1 ou cp1252 :
# df = pd.read_csv("ventes.csv", encoding="latin-1")
```

#### Justification

On uniformise **avant** de dédoublonner et d'agréger : sinon `groupby("ville")` éclate une même ville en plusieurs. On convertit les dates en `datetime` (pas en texte) pour pouvoir filtrer, trier, calculer des délais. `errors="coerce"` transforme l'illisible en `NaT`/`NaN` : c'est volontaire, on préfère un manquant explicite à un plantage ou à une valeur fausse.

> **Encadré — erreurs courantes (formats)**
> - **Oublier `dayfirst=True`** sur des dates FR → `03/01/2024` interprété comme 1er mars ou 3 janvier selon la config = silencieusement faux.
> - **`astype(float)` direct sur `"12,50 €"`** → erreur ; il faut nettoyer la chaîne d'abord.
> - **Title Case aveugle** → `Mcdonald'S`, `Saint-Andre` mal capitalisés. Garde une table de corrections pour les cas particuliers.
> - **Régler l'encodage après coup** → impossible de récupérer proprement, traite-le à la lecture.

---

### Incohérences logiques (dimension : cohérence)

Ce sont des valeurs individuellement valides mais qui se **contredisent**.

```python
# Date de livraison avant la commande : impossible
incoherences = df[df["date_livraison"] < df["date_commande"]]

# Prix négatif ou quantité négative
df[(df["prix"] < 0) | (df["quantite"] < 0)]

# Total ligne != prix * quantité (tolérance arrondi)
df["total_calcule"] = (df["prix"] * df["quantite"]).round(2)
df[(df["total"] - df["total_calcule"]).abs() > 0.01]
```

**Stratégie** : selon le cas, corriger (recalculer le total), mettre en `NaN` (date impossible), ou écarter et signaler la ligne au métier. On **ne supprime jamais en silence** une incohérence sans la documenter.

---

### Valeurs aberrantes / outliers (dimension : exactitude — rappel Maths ch.3)

Une valeur aberrante est anormalement éloignée des autres. Deux méthodes vues en maths.

#### Méthode IQR (écart interquartile) — robuste, recommandée

```python
Q1 = df["prix"].quantile(0.25)
Q3 = df["prix"].quantile(0.75)
IQR = Q3 - Q1

borne_basse = Q1 - 1.5 * IQR
borne_haute = Q3 + 1.5 * IQR

outliers = df[(df["prix"] < borne_basse) | (df["prix"] > borne_haute)]
print(f"{len(outliers)} outliers détectés sur 'prix'")
```

#### Méthode z-score — pour données ~normales

```python
moyenne = df["prix"].mean()
ecart_type = df["prix"].std()
df["z_prix"] = (df["prix"] - moyenne) / ecart_type

outliers_z = df[df["z_prix"].abs() > 3]  # au-delà de 3 écarts-types
```

#### Stratégies face à un outlier

1. **Erreur de saisie** (`prix = 99999 €` sur un t-shirt) → corriger ou mettre en `NaN`.
2. **Valeur vraie mais extrême** (un client a acheté pour `8 000 €`, c'est un grossiste) → **on garde**, on ne supprime pas une vraie donnée.
3. **Capping / winsorisation** → ramener aux bornes (`prix = min(prix, borne_haute)`) quand on veut limiter l'influence sans perdre la ligne.

```python
# Capping aux bornes IQR
df["prix"] = df["prix"].clip(lower=borne_basse, upper=borne_haute)
```

#### Justification

**Un outlier n'est pas forcément une erreur.** La question n'est jamais « comment je le supprime ? » mais « est-ce une faute ou une vraie valeur ? ». On supprime/corrige seulement les outliers **non plausibles** ; les valeurs extrêmes réelles racontent souvent quelque chose d'important pour le métier.

> **Encadré — erreurs courantes (outliers)**
> - **Supprimer tous les outliers par défaut** → tu effaces tes meilleurs clients ou des pics de vente réels (soldes, Black Friday).
> - **Utiliser le z-score sur une distribution non normale** → fausse détection ; préfère l'IQR.
> - **Confondre outlier et manquant** → ce sont deux problèmes distincts.

---

## Documenter & valider

### Documenter ses règles de nettoyage

Chaque décision de nettoyage doit être **traçable**. Tiens un journal (commentaires, notebook Markdown, ou tableau) :

| Colonne | Problème détecté | Règle appliquée | Justification |
|---|---|---|---|
| `client_id` | 8 manquants | Suppression des lignes | Donnée critique non imputable |
| `age` | 45 manquants, 3 valeurs >110 | Médiane + plafonnement à 100 | Robuste aux saisies erronées |
| `ville` | 6 variantes de casse, 1 faute | `.str.title()` + mapping corrections | Uniformiser avant `groupby` |
| `prix` | format `"12,50 €"`, 4 négatifs | Conversion float, négatifs → NaN | Validité + exactitude |
| `date_commande` | formats mixtes | `to_datetime(dayfirst=True)` | Permettre calculs de délais |

Pourquoi ? Pour la **reproductibilité** (un collègue peut rejouer le nettoyage), la **transparence** (le métier comprend ce qui a été modifié) et l'**audit** (revenir en arrière si une règle était mauvaise).

### Valider la qualité après nettoyage

On re-mesure les 5 dimensions et on vérifie qu'on n'a rien cassé :

```python
# Complétude
assert df["client_id"].notna().all(), "Des client_id sont encore vides"
print("Manquants restants :\n", df.isna().sum())

# Unicité
assert df.duplicated(subset=["client_id", "date_commande", "produit"]).sum() == 0

# Validité / exactitude
assert (df["prix"] >= 0).all(), "Prix négatifs restants"
assert (df["date_livraison"] >= df["date_commande"]).all()

# Comparatif avant/après
print(f"Lignes : {n_avant} -> {len(df)}  (supprimées : {n_avant - len(df)})")
```

> **Règle d'or n°2 : un nettoyage se valide.** Si tu ne peux pas prouver que la qualité a augmenté, tu n'as pas fini.

---

## Travaux pratiques

> **Dataset.** Crée un fichier `ventes_sales.csv` (ou récupère-le auprès du formateur) représentant les ventes d'une boutique e-commerce du Nord. Il contient volontairement : faux manquants (`"NA"`, `""`), doublons, casse incohérente sur `ville`, prix en texte `"19,90 €"`, dates en formats mixtes, quelques prix négatifs et un âge à `150`.

```python
import pandas as pd
import numpy as np

donnees = {
    "client_id": [1, 2, 2, 3, 4, 5, np.nan, 7, 8, 8],
    "nom":       ["Dupont", "Martin", "Martin", "Lefebvre", "Dubois",
                  "Moreau", "Petit", "Garcia", "Roux", "Roux"],
    "ville":     ["LILLE", "roubaix", "roubaix", "Valencienne", "Lille ",
                  "  Lille", "Roubaix", "VALENCIENNES", "Lille", "Lille"],
    "age":       ["34", "28", "28", "NA", "45", "150", "", "39", "52", "52"],
    "prix":      ["19,90 €", "120,00 €", "120,00 €", "-5,00 €", "45,50 €",
                  "12,00 €", "8000,00 €", "29,99 €", "15,00 €", "15,00 €"],
    "quantite":  [2, 1, 1, 3, 1, 2, 1, 4, 1, 1],
    "date_commande": ["2024-03-01", "01/03/2024", "01/03/2024", "2024-02-30",
                      "15/01/2024", "2024-04-10", "10 avril 2024",
                      "2024-05-01", "2024-05-02", "2024-05-02"],
    "remise":    [np.nan, 0.1, 0.1, np.nan, np.nan, 0.2, np.nan, np.nan, 0.05, 0.05],
}
df = pd.DataFrame(donnees)
df.to_csv("ventes_sales.csv", index=False, encoding="utf-8")
```

---

### TP 1 — Diagnostic (audit qualité)

Charge `ventes_sales.csv` et produis un **rapport de qualité** : dimensions du jeu, types, % de manquants par colonne (en tenant compte des faux manquants), nombre de doublons stricts. Conclus en une phrase par dimension CECUV.

<details>
<summary>Corrigé</summary>

```python
df = pd.read_csv("ventes_sales.csv")

# Convertir les faux manquants AVANT de compter
df = df.replace(["", " ", "NA", "N/A", "null", "-"], np.nan)

print("Dimensions :", df.shape)
print("\nTypes :\n", df.dtypes)
print("\n% manquants :\n", (df.isna().mean() * 100).round(1))
print("\nDoublons stricts :", df.duplicated().sum())
print("\nVariantes ville :\n", df["ville"].value_counts(dropna=False))
```

**Lecture CECUV :**
- *Complétude* : `client_id`, `age`, `remise` ont des manquants.
- *Exactitude* : `age=150`, `prix` négatif et un `8000 €` suspect.
- *Cohérence* : une date `2024-02-30` n'existe pas.
- *Unicité* : la ligne client 2 et la ligne client 8 sont dupliquées.
- *Validité* : `prix` est en texte avec `€`, dates en formats mixtes.

</details>

---

### TP 2 — Valeurs manquantes

Traite les manquants : supprime les lignes sans `client_id`, impute `age` par la médiane (après l'avoir converti en numérique), impute `remise` par `0` (règle métier). Justifie chaque choix en commentaire.

<details>
<summary>Corrigé</summary>

```python
# client_id critique -> suppression
df = df.dropna(subset=["client_id"])

# age en numérique puis médiane (robuste à la valeur 150)
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["age"] = df["age"].fillna(df["age"].median())

# remise : absence = pas de remise -> 0 (métier)
df["remise"] = df["remise"].fillna(0)
```

Justifications : `client_id` non imputable (clé) ; médiane car `150` tirerait la moyenne ; `0` car une remise absente n'est pas une remise inconnue.

</details>

---

### TP 3 — Formats & uniformisation

Uniformise `ville` (casse + espaces + faute `Valencienne`), convertis `prix` en float, et `date_commande` en datetime (gère la date impossible).

<details>
<summary>Corrigé</summary>

```python
# Ville
df["ville"] = (df["ville"].str.strip()
                          .str.replace(r"\s+", " ", regex=True)
                          .str.title())
df["ville"] = df["ville"].replace({"Valencienne": "Valenciennes"})

# Prix -> float
df["prix"] = (df["prix"].astype(str)
                        .str.replace("€", "", regex=False)
                        .str.replace(",", ".", regex=False)
                        .str.strip().astype(float))

# Dates (la 2024-02-30 deviendra NaT grâce à coerce)
df["date_commande"] = pd.to_datetime(df["date_commande"],
                                     errors="coerce", dayfirst=True)
print(df[["ville", "prix", "date_commande"]])
```

Après ça, `value_counts()` sur `ville` ne montre plus que 3 villes.

</details>

---

### TP 4 — Doublons

Supprime les doublons. Identifie d'abord s'il s'agit de doublons stricts ou métier, choisis ta clé, et justifie le `keep`.

<details>
<summary>Corrigé</summary>

```python
print("Doublons stricts :", df.duplicated().sum())
# Les lignes des clients 2 et 8 sont 100% identiques -> doublons stricts
df = df.drop_duplicates(keep="first")
print("Après :", df.shape)
```

Ici doublons stricts (lignes identiques) → `drop_duplicates()` suffit. Si on avait eu une colonne `date_maj`, on aurait trié dessus et gardé `keep="last"`.

</details>

---

### TP 5 — Outliers & incohérences

Détecte les outliers sur `prix` (IQR), traite le prix négatif, vérifie qu'aucune date n'est dans le futur. Décide pour le `8000 €` : erreur ou vraie valeur ?

<details>
<summary>Corrigé</summary>

```python
# Prix négatif = impossible -> NaN puis on décide (ici suppression de la ligne)
df.loc[df["prix"] < 0, "prix"] = np.nan
df = df.dropna(subset=["prix"])

# IQR
Q1, Q3 = df["prix"].quantile([0.25, 0.75])
IQR = Q3 - Q1
bh = Q3 + 1.5 * IQR
print("Borne haute :", bh)
print(df[df["prix"] > bh][["nom", "prix"]])
```

Décision : le `8000 €` est un **outlier détecté** mais sans contexte (grossiste ?) on ne le supprime pas par défaut — on le **signale au métier**. Le prix négatif, lui, est une **erreur certaine** → écarté.

</details>

---

### TP 6 — Documentation & validation

Rédige le tableau de règles de nettoyage (colonne / problème / règle / justification) et écris 3 `assert` de validation finale.

<details>
<summary>Corrigé</summary>

```python
assert df["client_id"].notna().all()
assert df.duplicated().sum() == 0
assert (df["prix"] >= 0).all()
assert df["ville"].nunique() == 3
print("Validation OK — jeu propre :", df.shape)
```

Le tableau de règles reprend le modèle de la section 5. L'essentiel : **chaque transformation est justifiée et rejouable**.

</details>

---

## Vidéos d'auto-formation

> Les liens ci-dessous ont été vérifiés. Si une vidéo a été déplacée ou retirée, utilise le lien de recherche YouTube fourni.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Data Cleaning in Pandas \| Python Pandas Tutorials | Alex The Analyst | EN | ~38 min | https://www.youtube.com/watch?v=bDhvCp3_lYw | Cas réel de bout en bout : doublons, `strip`, standardisation de numéros de téléphone, split de colonnes, gestion des nulls, filtrage |
| Python Pandas Tutorial 5: Handle Missing Data (fillna, dropna, interpolate) | codebasics | EN | ~23 min | https://www.youtube.com/watch?v=EaGbS7eWSs0 | Les 3 outils clés des valeurs manquantes : `dropna`, `fillna` (moyenne/forward-fill), `interpolate` |
| Pré-traitement de données avec Python (28/30) | Machine Learnia | FR | ~30 min | https://www.youtube.com/watch?v=x8yu8sq8mdw | Pipeline de préparation : nettoyage, encodage, traitement des manquants, normalisation |
| Sklearn Imputer : nettoyage de données | Machine Learnia | FR | ~20 min | https://www.youtube.com/watch?v=QVEJJNsz-eM | Imputation des manquants avec `SimpleImputer` (moyenne/médiane/mode) — pont vers le ML |
| Recherche : « data cleaning pandas tutorial » (secours) | — | FR/EN | — | https://www.youtube.com/results?search_query=data+cleaning+pandas+tutorial | À utiliser si un lien ci-dessus est cassé |

---

## Quiz (5 QCM)

**Q1.** Une colonne `ville` est catégorielle et contient des valeurs manquantes. Quelle imputation est la plus adaptée ?
- A. La moyenne
- B. La médiane
- C. Le mode
- D. Le z-score

**Q2.** Tu as une variable numérique `age` avec quelques valeurs aberrantes (saisies à 150). Quel indicateur d'imputation est le plus robuste ?
- A. La moyenne
- B. La médiane
- C. La somme
- D. Le maximum

**Q3.** Que fait `pd.to_datetime(col, errors="coerce")` sur une date illisible ?
- A. Lève une erreur et stoppe le script
- B. La remplace par la date du jour
- C. La transforme en `NaT` (date manquante)
- D. La laisse en texte

**Q4.** Parmi ces situations, laquelle relève de la dimension **cohérence** ?
- A. 12 % d'emails manquants
- B. Un email écrit `jean@@mail`
- C. Une `date_livraison` antérieure à la `date_commande`
- D. Le même client présent 3 fois

**Q5.** Face à un outlier détecté par la méthode IQR, quelle est la bonne attitude ?
- A. Le supprimer systématiquement
- B. Vérifier si c'est une erreur ou une vraie valeur extrême avant de décider
- C. Le remplacer toujours par la moyenne
- D. L'ignorer, l'IQR se trompe souvent

<details>
<summary>Réponses</summary>

1. **C** — Le mode : la moyenne/médiane n'ont pas de sens sur une catégorie.
2. **B** — La médiane, insensible aux valeurs extrêmes (contrairement à la moyenne).
3. **C** — `coerce` transforme l'illisible en `NaT` (manquant explicite), sans planter.
4. **C** — Deux dates qui se contredisent = incohérence. (A = complétude, B = validité, D = unicité.)
5. **B** — Un outlier n'est pas forcément une erreur ; on enquête avant d'agir.

</details>

---

## À retenir

- **« Garbage in, garbage out »** : 60-80 % du travail d'un·e data analyst, c'est nettoyer. Données fiables = décisions fiables.
- **5 dimensions de qualité — CECUV** : Complétude, Exactitude, Cohérence, Unicité, Validité.
- **On observe avant d'agir** : `info()`, `describe()`, `isna().mean()`, `value_counts()`.
- **Valeurs manquantes** : supprimer (peu / critique), imputer (moyenne ≈symétrique, **médiane** robuste, **mode** catégoriel) ou substituer (métier). **Toujours justifier.**
- **Doublons** : définir la clé d'unicité, choisir le `keep` consciemment.
- **Uniformiser** (casse, espaces, dates, unités, encodage) **avant** de dédoublonner et d'agréger.
- **Outliers** : IQR (robuste) ou z-score (≈normal) ; un outlier ≠ une erreur → enquêter avant de supprimer.
- **Documenter + valider** : chaque règle est tracée et rejouable ; on re-mesure la qualité (`assert`) pour prouver l'amélioration.
