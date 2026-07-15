# Chapitre 2 : Anatomie d'un Problème ML

## 🎯 Objectifs — Phase 0 · Semaine 2 · Comprendre avant de calculer

- Analyser un cas concret de bout en bout : **prédire si un client va partir** (churn)
- Explorer un dataset réel avec Python et Pandas
- Se poser les bonnes questions **avant** de toucher au ML
- Comprendre intuitivement comment mesurer la qualité d'une prédiction
- Maîtriser les commandes Pandas essentielles pour l'exploration
- Créer des visualisations simples avec Matplotlib et Seaborn
- Connaître le workflow ML complet en 8 étapes
- Identifier les pièges classiques du débutant

> ⚠️ **Attention** : "Ce chapitre ne contient **aucun modèle ML**. Zéro. On explore, on questionne, on visualise. C'est la partie la plus importante — et la plus souvent négligée."

**Livrable attendu** : un rapport d'exploration en français, 0 ligne de ML.

---

## 1. 🎯 Cas concret : prédire si un client va partir (churn)

### 1.1 Le contexte business

Vous êtes Data Engineer dans une entreprise de télécommunications. Le directeur commercial vous dit :

> « Chaque mois, on perd 15 % de nos clients. Ça nous coûte une fortune en acquisition. Si on pouvait **prédire** quels clients vont partir **avant** qu'ils partent, on pourrait les contacter et leur proposer une offre de rétention. »

C'est un problème de **classification binaire** (supervisé) :
- **Target** : le client va-t-il partir ? → `oui` (1) ou `non` (0)
- **Features** : tout ce qu'on sait sur le client (ancienneté, factures, appels au service client, etc.)

### 1.2 Pourquoi ce cas est parfait pour apprendre

| Raison | Détail |
|--------|--------|
| **Concret** | Tout le monde a été client d'un opérateur télécom |
| **Binaire** | Deux réponses possibles seulement (part / ne part pas) |
| **Impact mesurable** | On peut calculer l'argent économisé |
| **Données disponibles** | Beaucoup de datasets publics existent |
| **Vraies difficultés** | Données manquantes, déséquilibre, variables catégorielles |

### 1.3 Ce qu'on va faire dans ce chapitre

```
╔══════════════════════════════════════════════════════════╗
║                  PLAN DU CHAPITRE                        ║
║                                                          ║
║  1. Charger les données              (pd.read_csv)       ║
║  2. Regarder les données             (head, info)        ║
║  3. Comprendre chaque colonne        (describe, unique)  ║
║  4. Chercher les problèmes           (NaN, déséquilibre) ║
║  5. Visualiser                       (histogrammes)      ║
║  6. Rédiger un rapport d'exploration                     ║
║                                                          ║
║  ❌ PAS de modèle ML                                    ║
║  ❌ PAS de prédiction                                   ║
║  ✅ 100 % exploration et compréhension                  ║
╚══════════════════════════════════════════════════════════╝
```

---

## 2. 📂 À quoi ressemblent les données ?

### 2.1 Le dataset `clients_churn.csv`

Pour cet exercice, nous allons simuler un dataset réaliste de clients télécom. En production, ces données viendraient de votre data warehouse.

```python
import pandas as pd
import numpy as np

# ── Créer un dataset réaliste de churn télécom ──
np.random.seed(42)
n = 1000

data = {
    "client_id": range(1, n + 1),
    "anciennete_mois": np.random.randint(1, 72, n),
    "forfait_mensuel": np.round(np.random.uniform(15, 120, n), 2),
    "nb_appels_support": np.random.poisson(1.5, n),
    "data_utilisee_go": np.round(np.random.uniform(0.5, 50, n), 1),
    "contrat": np.random.choice(["mensuel", "annuel", "2 ans"], n, p=[0.5, 0.3, 0.2]),
    "moyen_paiement": np.random.choice(
        ["carte", "virement", "prelevement"], n, p=[0.4, 0.25, 0.35]
    ),
    "satisfaction": np.random.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.1, 0.3, 0.35, 0.2]),
}

df = pd.DataFrame(data)

# Créer la target (churn) avec une logique réaliste
proba_churn = (
    0.1
    + 0.3 * (df["contrat"] == "mensuel").astype(int)
    + 0.15 * (df["nb_appels_support"] > 3).astype(int)
    + 0.2 * (df["satisfaction"] <= 2).astype(int)
    - 0.1 * (df["anciennete_mois"] > 24).astype(int)
)
proba_churn = proba_churn.clip(0, 1)
df["churn"] = (np.random.random(n) < proba_churn).astype(int)

# Introduire des valeurs manquantes (réaliste !)
mask_satisfaction = np.random.random(n) < 0.08
df.loc[mask_satisfaction, "satisfaction"] = np.nan

mask_data = np.random.random(n) < 0.05
df.loc[mask_data, "data_utilisee_go"] = np.nan

# Sauvegarder
df.to_csv("clients_churn.csv", index=False)
print(f"Dataset créé : {len(df)} lignes, {len(df.columns)} colonnes")
print(f"Fichier sauvegardé : clients_churn.csv")
```

### 2.2 Charger et inspecter les données

```python
import pandas as pd

# ── Étape 1 : Charger les données ──
df = pd.read_csv("clients_churn.csv")

# ── Étape 2 : Premières lignes ──
print("=== 5 premières lignes ===")
print(df.head())
```

```
   client_id  anciennete_mois  forfait_mensuel  nb_appels_support  data_utilisee_go  contrat moyen_paiement  satisfaction  churn
0          1               52            89.73                  2              23.4  mensuel          carte           4.0      0
1          2               15            34.56                  0              45.2   annuel     prelevement           3.0      0
2          3               71            78.12                  4              12.8    2 ans       virement           5.0      0
3          4                8           110.45                  3               8.9  mensuel          carte           2.0      1
4          5               33            55.67                  1              31.5  mensuel     prelevement           NaN      1
```

```python
# ── Étape 3 : Structure du dataset ──
print("\n=== Informations sur le dataset ===")
print(df.info())
```

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1000 entries, 0 to 999
Data columns (total 9 columns):
 #   Column             Non-Null Count  Dtype
---  ------             --------------  -----
 0   client_id          1000 non-null   int64
 1   anciennete_mois    1000 non-null   int64
 2   forfait_mensuel    1000 non-null   float64
 3   nb_appels_support  1000 non-null   int64
 4   data_utilisee_go   952 non-null    float64    ← 48 valeurs manquantes !
 5   contrat            1000 non-null   object
 6   moyen_paiement     1000 non-null   object
 7   satisfaction       921 non-null    float64    ← 79 valeurs manquantes !
 8   churn              1000 non-null   int64
dtypes: float64(3), int64(4), object(2)
```

> 💡 **Conseil** : "`df.info()` est votre meilleur ami. En une commande, vous voyez le nombre de lignes, les types de données et les valeurs manquantes. Exécutez-le **toujours** en premier."

```python
# ── Étape 4 : Statistiques descriptives ──
print("\n=== Statistiques numériques ===")
print(df.describe())
```

```
       client_id  anciennete_mois  forfait_mensuel  nb_appels_support  data_utilisee_go  satisfaction       churn
count    1000.00          1000.00          1000.00            1000.00            952.00        921.00     1000.00
mean      500.50            35.89            67.32               1.52             25.18          3.54        0.28
std       288.82            20.64            30.41               1.23             14.38          1.02        0.45
min         1.00             1.00            15.01               0.00              0.50          1.00        0.00
25%       250.75            18.00            41.23               1.00             13.10          3.00        0.00
50%       500.50            36.00            67.45               1.00             25.20          4.00        0.00
75%       750.25            54.00            93.67               2.00             37.30          4.00        1.00
max      1000.00            71.00           119.98               8.00             49.90          5.00        1.00
```

### 2.3 Comprendre chaque colonne

| Colonne | Type | Description | Rôle ML |
|---------|------|-------------|---------|
| `client_id` | int | Identifiant unique du client | **À exclure** (pas prédictif) |
| `anciennete_mois` | int | Nombre de mois depuis l'inscription | Feature numérique |
| `forfait_mensuel` | float | Montant mensuel en euros | Feature numérique |
| `nb_appels_support` | int | Nombre d'appels au service client | Feature numérique |
| `data_utilisee_go` | float | Consommation de données en Go | Feature numérique |
| `contrat` | str | Type de contrat (mensuel/annuel/2 ans) | Feature catégorielle |
| `moyen_paiement` | str | Carte, virement ou prélèvement | Feature catégorielle |
| `satisfaction` | float | Note de 1 à 5 | Feature ordinale |
| `churn` | int | 0 = reste, 1 = parti | **TARGET** |

> ⚠️ **Attention** : "L'identifiant `client_id` ne doit **jamais** être utilisé comme feature. Le modèle pourrait apprendre que « le client 42 part toujours » — ce qui ne veut rien dire pour un nouveau client."

---

## 3. ❓ Quelles questions se poser ?

Avant de toucher au ML, un bon Data Engineer / Data Scientist pose **systématiquement** ces questions.

### 3.1 Y a-t-il des valeurs manquantes ?

```python
# ── Valeurs manquantes par colonne ──
print("=== Valeurs manquantes ===")
missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)

missing_df = pd.DataFrame({
    "nb_manquantes": missing,
    "pourcentage": missing_pct
})
print(missing_df[missing_df["nb_manquantes"] > 0])
```

```
                  nb_manquantes  pourcentage
data_utilisee_go            48         4.80
satisfaction                79         7.90
```

**Que faire ?** Plusieurs stratégies existent (on les verra en détail au chapitre suivant) :

| Stratégie | Quand l'utiliser | Risque |
|-----------|-----------------|--------|
| Supprimer les lignes | Très peu de valeurs manquantes (< 1 %) | Perte d'information |
| Remplir par la moyenne/médiane | Valeurs numériques, peu de manquants | Réduit la variance |
| Remplir par le mode | Valeurs catégorielles | Introduit un biais |
| Créer une catégorie « inconnu » | Quand le fait d'être manquant est informatif | Complexifie le modèle |
| Utiliser un algorithme robuste | Quand on ne peut pas se permettre de perdre de données | Dépend de l'algorithme |

### 3.2 La target est-elle déséquilibrée ?

```python
# ── Répartition de la target ──
print("=== Répartition du churn ===")
print(df["churn"].value_counts())
print()
print(df["churn"].value_counts(normalize=True).round(3))
```

```
=== Répartition du churn ===
churn
0    720
1    280
Name: count, dtype: int64

churn
0    0.72
1    0.28
Name: proportion, dtype: float64
```

**28 % de churn.** C'est un déséquilibre modéré. Voyons pourquoi c'est important :

```
╔═══════════════════════════════════════════════════════════════╗
║              POURQUOI LE DÉSÉQUILIBRE POSE PROBLÈME           ║
║                                                               ║
║  Si 95 % des clients restent et 5 % partent :                ║
║                                                               ║
║  Un modèle qui prédit TOUJOURS "reste" a 95 % de précision ! ║
║  Mais il ne détecte AUCUN départ → inutile pour le business. ║
║                                                               ║
║  C'est comme un détecteur d'incendie qui ne sonne jamais :   ║
║  il a raison 99.99 % du temps... jusqu'à l'incendie.         ║
╚═══════════════════════════════════════════════════════════════╝
```

> 💡 **Conseil** : "Vérifiez **toujours** la répartition de votre target en tout premier. Si elle est très déséquilibrée (ex : 99 % / 1 %), il faudra adapter votre approche."

### 3.3 Quels sont les types de variables ?

```python
# ── Types de variables ──
print("=== Variables numériques ===")
print(df.select_dtypes(include=["number"]).columns.tolist())

print("\n=== Variables catégorielles ===")
print(df.select_dtypes(include=["object"]).columns.tolist())

# ── Valeurs uniques des catégorielles ──
for col in df.select_dtypes(include=["object"]).columns:
    print(f"\n{col} : {df[col].unique()}")
    print(f"  → {df[col].nunique()} valeurs uniques")
```

```
=== Variables numériques ===
['client_id', 'anciennete_mois', 'forfait_mensuel', 'nb_appels_support',
 'data_utilisee_go', 'satisfaction', 'churn']

=== Variables catégorielles ===
['contrat', 'moyen_paiement']

contrat : ['mensuel' 'annuel' '2 ans']
  → 3 valeurs uniques

moyen_paiement : ['carte' 'virement' 'prelevement']
  → 3 valeurs uniques
```

| Type de variable | Exemples dans notre dataset | Traitement nécessaire |
|-----------------|---------------------------|----------------------|
| **Numérique continue** | forfait_mensuel, data_utilisee_go | Normalisation possible |
| **Numérique discrète** | anciennete_mois, nb_appels_support | Souvent utilisable tel quel |
| **Catégorielle nominale** | contrat, moyen_paiement | Encodage (one-hot, label) |
| **Catégorielle ordinale** | satisfaction (1 → 5) | Encodage ordinal |

### 3.4 Y a-t-il des valeurs aberrantes ?

```python
# ── Détecter les valeurs aberrantes (outliers) ──
print("=== Statistiques pour détecter les outliers ===")
for col in ["anciennete_mois", "forfait_mensuel", "nb_appels_support", "data_utilisee_go"]:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    borne_basse = q1 - 1.5 * iqr
    borne_haute = q3 + 1.5 * iqr
    outliers = df[(df[col] < borne_basse) | (df[col] > borne_haute)]
    print(f"{col:25s} : {len(outliers):3d} outliers  (bornes: [{borne_basse:.1f}, {borne_haute:.1f}])")
```

```
anciennete_mois           :   0 outliers  (bornes: [-36.0, 108.0])
forfait_mensuel           :   0 outliers  (bornes: [-37.4, 172.3])
nb_appels_support         :  23 outliers  (bornes: [-0.5, 3.5])
data_utilisee_go          :   0 outliers  (bornes: [-23.2, 73.6])
```

> 💡 **Conseil** : "Un outlier n'est pas forcément une erreur. Un client qui appelle 8 fois le support est peut-être très mécontent — et c'est une information **précieuse** pour prédire le churn."

---

## 4. 📏 Comment mesurer si notre prédiction est bonne ?

On ne construit pas encore de modèle, mais comprenons **intuitivement** comment on jugera sa qualité.

### 4.1 L'analogie du médecin

Imaginez un test médical pour détecter une maladie :

```
                        RÉALITÉ
                   Malade    Pas malade
                ┌──────────┬──────────┐
   TEST   Positif │  TP ✅   │  FP ❌   │   TP = Vrai Positif (bien détecté)
   dit :          ├──────────┼──────────┤   FP = Faux Positif (fausse alarme)
          Négatif │  FN ❌   │  TN ✅   │   FN = Faux Négatif (raté !)
                └──────────┴──────────┘   TN = Vrai Négatif (bien exclu)
```

Appliqué à notre cas de churn :

| Situation | Signification | Conséquence |
|-----------|--------------|-------------|
| **Vrai Positif (TP)** | On prédit « part » et le client part vraiment | On peut le retenir ! |
| **Faux Positif (FP)** | On prédit « part » mais le client reste | On dépense une offre inutilement |
| **Faux Négatif (FN)** | On prédit « reste » mais le client part | On perd le client — le pire cas ! |
| **Vrai Négatif (TN)** | On prédit « reste » et le client reste | Tout va bien |

### 4.2 Les métriques essentielles (sans formule)

| Métrique | Question qu'elle pose | Analogie |
|----------|----------------------|----------|
| **Accuracy** | « Sur l'ensemble, combien de prédictions sont correctes ? » | Note globale à un examen |
| **Précision** | « Parmi ceux qu'on a identifiés comme "part", combien partent vraiment ? » | Fiabilité des alarmes |
| **Rappel** | « Parmi tous ceux qui partent, combien a-t-on détectés ? » | Sensibilité du radar |
| **F1-score** | « Compromis entre précision et rappel » | Note harmonisée |

```python
# ── Exemple intuitif avec des chiffres ──

# Imaginons 100 clients : 30 partent, 70 restent
# Notre modèle prédit :

predictions = {
    "vrais_positifs":  22,  # on a bien détecté 22 des 30 qui partent
    "faux_positifs":   8,   # 8 clients qu'on pensait partants restent
    "faux_negatifs":   8,   # 8 clients partent sans qu'on les ait détectés
    "vrais_negatifs":  62,  # 62 clients restent comme prévu
}

tp = predictions["vrais_positifs"]
fp = predictions["faux_positifs"]
fn = predictions["faux_negatifs"]
tn = predictions["vrais_negatifs"]

accuracy  = (tp + tn) / (tp + fp + fn + tn)
precision = tp / (tp + fp)
rappel    = tp / (tp + fn)
f1        = 2 * (precision * rappel) / (precision + rappel)

print(f"Accuracy  : {accuracy:.1%}")   # 84.0%
print(f"Précision : {precision:.1%}")  # 73.3%
print(f"Rappel    : {rappel:.1%}")     # 73.3%
print(f"F1-score  : {f1:.1%}")         # 73.3%
```

> ⚠️ **Attention** : "L'accuracy **seule** est souvent trompeuse. Un modèle qui prédit toujours « reste » sur notre dataset aurait 72 % d'accuracy — mais détecterait 0 % des départs. Regardez toujours **plusieurs** métriques."

---

## 5. 🐍 Premier contact avec Python/Pandas

### 5.1 Les commandes essentielles à connaître

```python
import pandas as pd

df = pd.read_csv("clients_churn.csv")

# ── Les 10 commandes que vous utiliserez tous les jours ──

# 1. Premières et dernières lignes
df.head(10)        # 10 premières lignes
df.tail(5)         # 5 dernières lignes

# 2. Dimensions
print(f"Taille : {df.shape[0]} lignes × {df.shape[1]} colonnes")

# 3. Types et valeurs manquantes
df.info()

# 4. Statistiques numériques
df.describe()

# 5. Valeurs uniques d'une colonne
df["contrat"].value_counts()

# 6. Filtrage
clients_mensuels = df[df["contrat"] == "mensuel"]
print(f"Clients mensuels : {len(clients_mensuels)}")

# 7. Groupement et agrégation
df.groupby("contrat")["churn"].mean()

# 8. Tri
df.sort_values("forfait_mensuel", ascending=False).head()

# 9. Sélection de colonnes
df[["anciennete_mois", "forfait_mensuel", "churn"]].head()

# 10. Corrélation entre variables numériques
df.select_dtypes(include="number").corr()["churn"].sort_values()
```

### 5.2 Calculer des statistiques simples

```python
# ── Statistiques par groupe ──
print("=== Taux de churn par type de contrat ===")
churn_par_contrat = df.groupby("contrat")["churn"].agg(["mean", "count"])
churn_par_contrat.columns = ["taux_churn", "nb_clients"]
churn_par_contrat["taux_churn"] = (churn_par_contrat["taux_churn"] * 100).round(1)
print(churn_par_contrat)
```

```
         taux_churn  nb_clients
contrat
2 ans          12.5         200
annuel         18.7         300
mensuel        40.2         500
```

```python
# ── Statistiques descriptives par segment ──
print("\n=== Forfait mensuel moyen selon le churn ===")
print(df.groupby("churn")["forfait_mensuel"].agg(["mean", "median"]).round(2))

print("\n=== Ancienneté moyenne selon le churn ===")
print(df.groupby("churn")["anciennete_mois"].agg(["mean", "median"]).round(1))

print("\n=== Nombre moyen d'appels support selon le churn ===")
print(df.groupby("churn")["nb_appels_support"].agg(["mean", "median"]).round(2))
```

```
=== Forfait mensuel moyen selon le churn ===
        mean  median
churn
0      66.18   65.34
1      70.25   71.12

=== Ancienneté moyenne selon le churn ===
       mean  median
churn
0      37.2    37.0
1      32.5    31.0

=== Nombre moyen d'appels support selon le churn ===
        mean  median
churn
0       1.38    1.00
1       1.88    2.00
```

> 💡 **Conseil** : "Ces statistiques simples donnent déjà des indices : les clients qui partent ont en moyenne un forfait plus élevé, une ancienneté plus faible et appellent plus souvent le support. On n'a pas eu besoin de ML pour ça !"

### 5.3 Visualiser avec Matplotlib et Seaborn

```python
import matplotlib.pyplot as plt
import seaborn as sns

# ── Configuration globale ──
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("Set2")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Exploration du dataset Churn Télécom", fontsize=16, fontweight="bold")

# ── 1. Répartition de la target ──
ax = axes[0, 0]
df["churn"].value_counts().plot(kind="bar", ax=ax, color=["#66c2a5", "#fc8d62"])
ax.set_title("Répartition du Churn")
ax.set_xticklabels(["Reste (0)", "Part (1)"], rotation=0)
ax.set_ylabel("Nombre de clients")

# ── 2. Distribution de l'ancienneté ──
ax = axes[0, 1]
sns.histplot(data=df, x="anciennete_mois", hue="churn", bins=20, ax=ax, kde=True)
ax.set_title("Ancienneté par statut de churn")
ax.set_xlabel("Ancienneté (mois)")

# ── 3. Forfait mensuel par churn ──
ax = axes[0, 2]
sns.boxplot(data=df, x="churn", y="forfait_mensuel", ax=ax)
ax.set_title("Forfait mensuel par churn")
ax.set_xticklabels(["Reste", "Part"])

# ── 4. Churn par type de contrat ──
ax = axes[1, 0]
churn_rate = df.groupby("contrat")["churn"].mean().sort_values()
churn_rate.plot(kind="barh", ax=ax, color="#8da0cb")
ax.set_title("Taux de churn par contrat")
ax.set_xlabel("Taux de churn")

# ── 5. Nombre d'appels support ──
ax = axes[1, 1]
sns.countplot(data=df, x="nb_appels_support", hue="churn", ax=ax)
ax.set_title("Appels support par churn")
ax.set_xlabel("Nombre d'appels")

# ── 6. Satisfaction vs Churn ──
ax = axes[1, 2]
df_satisfaction = df.dropna(subset=["satisfaction"])
sns.countplot(data=df_satisfaction, x="satisfaction", hue="churn", ax=ax)
ax.set_title("Satisfaction par churn")
ax.set_xlabel("Note de satisfaction")

plt.tight_layout()
plt.savefig("exploration_churn.png", dpi=150, bbox_inches="tight")
plt.show()
print("Graphique sauvegardé : exploration_churn.png")
```

### 5.4 Matrice de corrélation

```python
# ── Matrice de corrélation ──
plt.figure(figsize=(10, 8))
correlation = df.select_dtypes(include="number").corr()

sns.heatmap(
    correlation,
    annot=True,          # afficher les valeurs
    fmt=".2f",           # 2 décimales
    cmap="coolwarm",     # palette de couleurs
    center=0,            # centrer sur 0
    square=True,
    linewidths=0.5,
)
plt.title("Matrice de corrélation — Variables numériques", fontsize=14)
plt.tight_layout()
plt.savefig("correlation_churn.png", dpi=150)
plt.show()
```

> 💡 **Conseil** : "La matrice de corrélation montre les relations **linéaires** entre variables. Une corrélation de 0 ne signifie pas « pas de relation » — elle peut être non-linéaire. Mais c'est un excellent point de départ."

---

## 6. 🔄 Le workflow ML complet (8 étapes)

Même si on ne fait pas de ML dans ce chapitre, voici la vue d'ensemble du processus complet. Chaque étape fera l'objet d'un chapitre dédié.

### 6.1 Diagramme du workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                   WORKFLOW ML EN 8 ÉTAPES                        │
│                                                                 │
│  ┌──────────────────────┐                                       │
│  │ 1. DÉFINIR LE        │  « Qu'est-ce qu'on veut prédire ? »  │
│  │    PROBLÈME          │  « Quelle métrique de succès ? »      │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 2. COLLECTER LES     │  SQL, API, CSV, scraping...           │
│  │    DONNÉES           │  C'est le rôle du Data Engineer !     │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 3. EXPLORER          │  ← VOUS ÊTES ICI (ce chapitre)       │
│  │    (EDA)             │  head(), describe(), visualisations   │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 4. PRÉPARER LES      │  Nettoyage, encodage, normalisation  │
│  │    DONNÉES           │  Feature engineering                  │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 5. SÉPARER           │  Train / Validation / Test            │
│  │    TRAIN/TEST        │  Ne JAMAIS tricher !                  │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 6. ENTRAÎNER         │  Choisir un algorithme, fit()         │
│  │    LE MODÈLE         │  Ajuster les hyperparamètres          │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 7. ÉVALUER           │  Accuracy, précision, rappel, F1     │
│  │    LE MODÈLE         │  Matrice de confusion                 │
│  └──────────┬───────────┘                                       │
│             ▼                                                   │
│  ┌──────────────────────┐                                       │
│  │ 8. DÉPLOYER          │  API, batch, monitoring               │
│  │    EN PRODUCTION     │  MLOps                                │
│  └──────────────────────┘                                       │
│                                                                 │
│  ⟲ Itératif : on revient souvent aux étapes 3-4 !              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Description de chaque étape

| Étape | Nom | Qui la fait ? | Temps passé (%) |
|-------|-----|---------------|-----------------|
| 1 | Définir le problème | Business + Data Scientist | 5 % |
| 2 | Collecter les données | **Data Engineer** | 20 % |
| 3 | Explorer (EDA) | Data Scientist / Data Analyst | 15 % |
| 4 | Préparer les données | **Data Engineer** + Data Scientist | 30 % |
| 5 | Séparer train/test | Data Scientist | 2 % |
| 6 | Entraîner le modèle | Data Scientist | 10 % |
| 7 | Évaluer le modèle | Data Scientist | 8 % |
| 8 | Déployer en production | **Data Engineer** / MLOps | 10 % |

> ⚠️ **Attention** : "Les étapes 2, 3 et 4 (données) représentent **65 % du travail** d'un projet ML. C'est pourquoi le rôle du Data Engineer est **fondamental** dans le ML — sans données propres, aucun modèle ne peut être bon."

---

## 7. 🚨 Les pièges classiques du débutant

### 7.1 Piège n°1 — Sauter l'exploration

```
❌ MAUVAISE APPROCHE                    ✅ BONNE APPROCHE

"J'ai des données, je lance            "J'ai des données, je regarde
 un Random Forest tout de suite !"       à quoi elles ressemblent,
                                         je comprends chaque colonne,
 → Résultat : 45% d'accuracy            je nettoie, PUIS je modélise."
 → 3 jours de perdu
                                         → Résultat : 87% d'accuracy
                                         → Temps total plus court
```

### 7.2 Piège n°2 — Ignorer les valeurs manquantes

```python
# ❌ Ne JAMAIS faire ça sans y réfléchir :
df_nettoye = df.dropna()  # on perd potentiellement beaucoup de lignes !
print(f"Avant : {len(df)} lignes")
print(f"Après : {len(df_nettoye)} lignes")
print(f"Perdu : {len(df) - len(df_nettoye)} lignes ({(len(df) - len(df_nettoye))/len(df)*100:.1f}%)")
```

```
Avant : 1000 lignes
Après : 879 lignes
Perdu : 121 lignes (12.1%)
```

### 7.3 Piège n°3 — Utiliser l'identifiant comme feature

```python
# ❌ Le modèle apprend que "client 42 part" — non-sens !
# X = df[["client_id", "anciennete_mois", "forfait_mensuel"]]

# ✅ Exclure l'identifiant
X = df[["anciennete_mois", "forfait_mensuel", "nb_appels_support"]]
```

### 7.4 Piège n°4 — Ne pas vérifier le déséquilibre de la target

```python
# ❌ Si 99% des clients restent et on ne vérifie pas :
# Le modèle prédit TOUJOURS "reste" → 99% d'accuracy, 0% d'utilité

# ✅ Toujours vérifier :
print(df["churn"].value_counts(normalize=True))
```

### 7.5 Piège n°5 — Confondre corrélation et causalité

```
╔═══════════════════════════════════════════════════════════════╗
║            CORRÉLATION ≠ CAUSALITÉ                            ║
║                                                               ║
║  « Les clients qui appellent souvent le support partent       ║
║    plus souvent. »                                            ║
║                                                               ║
║  → Cela NE VEUT PAS DIRE que les appels CAUSENT le churn.    ║
║  → C'est peut-être l'inverse : les clients mécontents         ║
║    appellent ET partent (cause commune : mauvais service).    ║
║                                                               ║
║  Le ML détecte des CORRÉLATIONS, pas des CAUSES.              ║
║  Les décisions business doivent en tenir compte.              ║
╚═══════════════════════════════════════════════════════════════╝
```

### 7.6 Piège n°6 — Négliger les variables catégorielles

```python
# ❌ Oublier d'encoder les variables texte
# La plupart des algorithmes ML ne comprennent PAS le texte brut

# ✅ Vérifier les types AVANT de modéliser
print("Types de données :")
print(df.dtypes)
print()
print("Variables à encoder :", df.select_dtypes(include="object").columns.tolist())
```

### 7.7 Piège n°7 — Ne pas séparer les données correctement

```
╔═══════════════════════════════════════════════════════════════╗
║     ❌ ENTRAÎNER ET ÉVALUER SUR LES MÊMES DONNÉES            ║
║                                                               ║
║  C'est comme donner l'examen avec le corrigé sous les yeux.  ║
║  Le modèle aura 99 % de précision... mais échouera sur       ║
║  de nouvelles données qu'il n'a jamais vues.                  ║
║                                                               ║
║  ✅ Toujours séparer :                                       ║
║  ┌──────────────────────────────────────────┐                 ║
║  │  Données totales (100%)                  │                 ║
║  │  ┌──────────────────┬───────────────┐    │                 ║
║  │  │  Train (70-80%)  │  Test (20-30%)│    │                 ║
║  │  │  Le modèle       │  On évalue    │    │                 ║
║  │  │  apprend ici     │  ici          │    │                 ║
║  │  └──────────────────┴───────────────┘    │                 ║
║  └──────────────────────────────────────────┘                 ║
╚═══════════════════════════════════════════════════════════════╝
```

### 7.8 Résumé des pièges

| Piège | Conséquence | Solution |
|-------|-------------|----------|
| Sauter l'exploration | Mauvais modèle, temps perdu | Toujours commencer par `df.info()` et `df.describe()` |
| Ignorer les NaN | Erreurs ou perte de données | Analyser le pattern de valeurs manquantes |
| Utiliser l'ID comme feature | Le modèle apprend du bruit | Exclure les identifiants |
| Ignorer le déséquilibre | Métrique trompeuse | Vérifier `value_counts(normalize=True)` |
| Corrélation = causalité | Mauvaises décisions business | Toujours raisonner sur la causalité |
| Oublier l'encodage | Algorithme qui plante | Vérifier les `dtypes` |
| Évaluer sur les données d'entraînement | Surestimation des performances | Toujours séparer train/test |

---

## 🎯 Points clés à retenir

1. **Explorer avant de modéliser** : 65 % du travail ML, c'est comprendre et préparer les données.
2. `df.info()`, `df.describe()`, `df.head()` sont vos **trois premières commandes** sur tout nouveau dataset.
3. Vérifiez **toujours** : les valeurs manquantes, le déséquilibre de la target, les types de variables.
4. Les visualisations (histogrammes, boxplots, heatmaps) révèlent des patterns que les chiffres seuls ne montrent pas.
5. Le workflow ML comporte **8 étapes** — le modèle n'arrive qu'à l'étape 6. Les 5 premières sont de la préparation.
6. Les **pièges classiques** (déséquilibre, fuite de données, corrélation vs causalité) coûtent plus cher que le choix de l'algorithme.
7. En tant que Data Engineer, votre rôle couvre les étapes 2, 4 et 8 — les **fondations** sur lesquelles tout le reste repose.

---

## ✅ Checklist de validation

Avant de passer au chapitre suivant, vérifiez que vous pouvez :

- [ ] Charger un fichier CSV avec `pd.read_csv()` et afficher les 5 premières lignes
- [ ] Utiliser `df.info()` pour identifier les types de données et les valeurs manquantes
- [ ] Utiliser `df.describe()` pour obtenir les statistiques descriptives
- [ ] Calculer le taux de churn (ou toute target) avec `value_counts(normalize=True)`
- [ ] Identifier les variables numériques et catégorielles dans un dataset
- [ ] Créer au moins 3 types de graphiques : histogramme, boxplot, countplot
- [ ] Calculer des statistiques par groupe avec `groupby().agg()`
- [ ] Lister les 8 étapes du workflow ML dans l'ordre
- [ ] Nommer au moins 5 pièges classiques du débutant ML
- [ ] Rédiger un rapport d'exploration synthétique à partir de vos observations

---

**Précédent** : [← Chapitre 1 — Qu'est-ce que le ML ?](01-quest-ce-que-le-ml.md) | **Suivant** : [Chapitre 3 — Préparation des données →](03-preprocessing.md)

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Les étapes d'un projet ML](https://www.youtube.com/results?search_query=machine+learnia+etapes+projet+machine+learning) | Machine Learnia | FR | Du problème métier au modèle |
| [Train / Test split expliqué](https://www.youtube.com/results?search_query=statquest+training+testing+data) | StatQuest | EN | Pourquoi séparer les données |
| [Anatomie d'un modèle](https://www.youtube.com/results?search_query=machine+learnia+train+test+split+francais) | Machine Learnia | FR | Features, cible, jeu d'entraînement |
