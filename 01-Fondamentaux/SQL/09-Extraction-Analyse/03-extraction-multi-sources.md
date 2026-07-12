# 03 - Extraction multi-sources

[← 02 - SQL avancé pour l'analyse](02-sql-avance-analyse.md) | [🏠 Accueil](../README.md) | [📂 Module 09](README.md)

---

| | |
|---|---|
| **Durée indicative** | ~14 heures (pratique incluse) |
| **Compétence visée** | **C4 (niveau 2)** — Extraire des données de sources variées |
| **Prérequis** | [01 - Extraction ciblée](01-extraction-ciblee.md), [02 - SQL avancé pour l'analyse](02-sql-avance-analyse.md), bases de Python et de pandas (DataFrame, lecture de fichiers) |
| **Outils** | Python 3 (`requests`, `pandas`, `openpyxl`), l'API [Open-Meteo](https://open-meteo.com/) (gratuite, sans clé), SQLite |

---

## 1. Objectifs

À la fin de ce chapitre, tu seras capable de :

- **Consommer une API REST** en Python avec la librairie `requests` : envoyer une requête GET, lire une réponse JSON, gérer la **pagination** et une **clé API**.
- **Combiner plusieurs sources** hétérogènes (base SQL + API + fichier Excel) dans pandas avec `merge` et `concat`.
- **Valider l'exactitude** des données extraites : contrôle des doublons, vérification des totaux, repérage des valeurs manquantes ou aberrantes.

---

## 2. Pourquoi c'est utile au Data Analyst

Dans la vraie vie, les données ne sont **jamais** déjà rangées dans un seul fichier propre. Sur une mission retail dans le Nord, tu vas typiquement devoir :

- aller chercher les **ventes** dans la base de données du magasin (SQL),
- récupérer la **météo** de Lille pour expliquer les pics de fréquentation (API publique),
- croiser avec les **objectifs commerciaux** que le directeur t'a envoyés dans un Excel.

Ces trois sources n'ont ni le même format, ni la même granularité. Ton métier, c'est de les **extraire**, les **réconcilier** et de **garantir** que le résultat est juste avant de produire le moindre graphique. Une erreur d'extraction (un doublon de ligne, une jointure mal faite, une page d'API oubliée) fausse toute l'analyse en aval. C'est exactement la compétence C4 : savoir extraire de **sources variées** de façon **fiable**.

> On réutilise la table `ventes` du chapitre [02 - SQL avancé pour l'analyse](02-sql-avance-analyse.md) (colonnes : `vente_id`, `date_vente`, `magasin`, `vendeur`, `categorie`, `produit`, `quantite`, `montant`).

---

## 3. Consommer une API REST en Python

Une **API REST** est un service web qu'on interroge via une URL pour récupérer des données, le plus souvent au format **JSON**. On utilise la librairie `requests`.

### 3.1 Première requête GET

On utilise [Open-Meteo](https://open-meteo.com/), une API météo **gratuite et sans clé** — parfaite pour s'entraîner.

```python
import requests

# Coordonnées de Lille
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 50.63,
    "longitude": 3.06,
    "daily": "temperature_2m_max,precipitation_sum",
    "timezone": "Europe/Paris",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
}

reponse = requests.get(url, params=params, timeout=10)
reponse.raise_for_status()          # lève une erreur si le statut HTTP n'est pas 200
donnees = reponse.json()            # convertit le JSON en dictionnaire Python

print(donnees["daily"]["time"][:3])
print(donnees["daily"]["temperature_2m_max"][:3])
```

```text
['2024-01-01', '2024-01-02', '2024-01-03']
[6.4, 5.1, 8.2]
```

**Points clés :**
- `params=` construit proprement l'URL (`?latitude=50.63&...`) — ne **jamais** concaténer à la main.
- `timeout=10` évite que le script reste bloqué indéfiniment.
- `raise_for_status()` transforme un échec (404, 500...) en exception claire.
- `.json()` te rend un `dict` Python directement exploitable.

### 3.2 Transformer le JSON en DataFrame

```python
import pandas as pd

meteo = pd.DataFrame({
    "date": donnees["daily"]["time"],
    "temp_max": donnees["daily"]["temperature_2m_max"],
    "precipitation": donnees["daily"]["precipitation_sum"],
})
meteo["date"] = pd.to_datetime(meteo["date"])
print(meteo.head())
```

### 3.3 La pagination et les clés API

Beaucoup d'API renvoient les résultats **par pages** (100 lignes à la fois). Il faut boucler tant qu'il reste des pages.

```python
import requests

API_KEY = "ta_cle_secrete"          # en vrai : à lire depuis une variable d'environnement, jamais en dur !
headers = {"Authorization": f"Bearer {API_KEY}"}

tous_les_resultats = []
page = 1

while True:
    reponse = requests.get(
        "https://api.exemple.com/v1/ventes",
        headers=headers,
        params={"page": page, "per_page": 100},
        timeout=10,
    )
    reponse.raise_for_status()
    data = reponse.json()

    lignes = data["results"]
    if not lignes:                  # plus aucune ligne → on s'arrête
        break

    tous_les_resultats.extend(lignes)
    page += 1

print(f"{len(tous_les_resultats)} enregistrements récupérés")
```

> ⚠️ **Erreurs courantes avec les API**
> - **Oublier la pagination** → tu ne récupères que la 1re page (souvent 100 lignes) et tu crois avoir tout. Vérifie toujours le nombre total attendu.
> - **Clé API en dur dans le code** → si tu pousses sur GitHub, ta clé est volée. Utilise `os.environ` ou un fichier `.env` (avec `python-dotenv`).
> - **Pas de gestion du rate limit** → trop de requêtes trop vite → l'API renvoie un statut `429`. Respecte les quotas, ajoute un petit `time.sleep()` si besoin.
> - **Boucle infinie** → toujours prévoir une condition d'arrêt (`if not lignes: break`).

---

## 4. Combiner plusieurs sources avec pandas

On a maintenant 3 DataFrames :
- `ventes` (lu depuis SQL),
- `meteo` (lu depuis l'API),
- `objectifs` (lu depuis Excel).

### 4.1 `merge` — jointure entre sources

`merge` joint deux DataFrames sur une ou plusieurs colonnes communes — l'équivalent du `JOIN` SQL vu au [Module 03 - Jointures](../03-Jointures/README.md).

```python
# Agréger les ventes par jour, puis joindre la météo du même jour
ventes_jour = (
    ventes.groupby("date_vente", as_index=False)["montant"].sum()
          .rename(columns={"montant": "ca_jour", "date_vente": "date"})
)
ventes_jour["date"] = pd.to_datetime(ventes_jour["date"])

# Jointure ventes + météo sur la date
analyse = ventes_jour.merge(meteo, on="date", how="left")
print(analyse.head())
```

| date | ca_jour | temp_max | precipitation |
|---|---|---|---|
| 2024-01-01 | 4200.50 | 6.4 | 0.0 |
| 2024-01-02 | 3890.00 | 5.1 | 2.3 |
| 2024-01-03 | 5120.80 | 8.2 | 0.0 |

> `how="left"` garde **toutes** les lignes de ventes même si la météo manque pour un jour. Choisir le bon `how` (`left`, `inner`, `outer`) est crucial — c'est la même décision d'analyse que `LEFT JOIN` vs `INNER JOIN` en SQL (voir l'encadré plus bas).

### 4.2 Ajouter les objectifs (Excel)

```python
objectifs = pd.read_excel("objectifs_2024.xlsx")  # colonnes : mois, objectif_ca

analyse["mois"] = analyse["date"].dt.to_period("M").astype(str)
ca_mensuel = analyse.groupby("mois", as_index=False)["ca_jour"].sum()
suivi = ca_mensuel.merge(objectifs, on="mois", how="left")
suivi["taux_atteinte"] = (suivi["ca_jour"] / suivi["objectif_ca"] * 100).round(1)
print(suivi)
```

| mois | ca_jour | objectif_ca | taux_atteinte |
|---|---|---|---|
| 2024-01 | 42000.00 | 40000 | 105.0 |
| 2024-02 | 38500.00 | 42000 | 91.7 |

### 4.3 `concat` — empiler des sources de même structure

`concat` empile verticalement — l'équivalent du [`UNION ALL` SQL](02-sql-avance-analyse.md#45-union--empiler-des-résultats).

```python
# Empiler les exports de plusieurs magasins (mêmes colonnes)
lille   = pd.read_csv("ventes_lille.csv")
roubaix = pd.read_csv("ventes_roubaix.csv")
tout = pd.concat([lille, roubaix], ignore_index=True)
```

> ⚠️ **`merge` : la jointure qui duplique ou qui perd des lignes.** Si la colonne de jointure n'est pas unique d'un côté, `merge` crée un **produit cartésien** (explosion de lignes). Et `how="inner"` (par défaut) **supprime** silencieusement les lignes sans correspondance. **Toujours** vérifier `len(df)` avant/après une jointure et contrôler les `NaN` apparus.

---

## 5. Valider l'exactitude des données extraites

Extraire ne suffit pas : il faut **prouver** que le résultat est juste. Quatre contrôles incontournables :

```python
# 1) Doublons : ne doit pas y avoir deux fois la même vente
nb_doublons = ventes.duplicated(subset=["vente_id"]).sum()
print("Doublons :", nb_doublons)   # attendu : 0

# 2) Valeurs manquantes apparues après la jointure
print(analyse.isna().sum())

# 3) Cohérence des totaux : le CA après jointure = CA avant jointure ?
ca_source = ventes["montant"].sum()
ca_apres  = analyse["ca_jour"].sum()
print("Écart de total :", round(ca_source - ca_apres, 2))  # attendu : ~0

# 4) Valeurs aberrantes : pas de montant négatif, pas de quantité nulle
print("Montants négatifs :", (ventes["montant"] < 0).sum())
```

Côté SQL, le même réflexe :

```sql
-- Détecter les doublons éventuels sur une clé censée être unique
SELECT vente_id, COUNT(*) AS n
FROM ventes
GROUP BY vente_id
HAVING COUNT(*) > 1;
```

> 💡 **Le contrôle du total est ton meilleur ami.** Avant et après chaque transformation (jointure, agrégation, dédoublonnage), compare une grandeur globale (somme du CA, nombre de lignes). Si le total change sans raison, tu as une jointure dupliquante ou une perte de lignes. C'est le contrôle qui attrape 80 % des bugs d'extraction.

---

## 6. Travaux pratiques

> Pour l'API, **Open-Meteo** ne nécessite aucune clé. Pour la partie SQL, réutilise la base de ventes retail du chapitre [02](02-sql-avance-analyse.md) (via DB Browser for SQLite ou la librairie `sqlite3` de Python).

### TP 1 — Appel API météo

Récupère la température max et les précipitations quotidiennes de **Roubaix** (lat 50.69, lon 3.18) pour janvier 2024 via Open-Meteo, et charge le résultat dans un DataFrame propre.

<details><summary>✅ Corrigé</summary>

```python
import requests
import pandas as pd

reponse = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": 50.69,
        "longitude": 3.18,
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "Europe/Paris",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    },
    timeout=10,
)
reponse.raise_for_status()
d = reponse.json()["daily"]

meteo = pd.DataFrame({
    "date": pd.to_datetime(d["time"]),
    "temp_max": d["temperature_2m_max"],
    "precipitation": d["precipitation_sum"],
})
print(meteo.shape)   # (31, 3)
print(meteo.head())
```

*Vérification : on attend **31 lignes** (jours de janvier). Si tu en as moins, vérifie `start_date`/`end_date`.*
</details>

### TP 2 — Croiser ventes + météo (merge)

À partir d'un DataFrame `ventes` (CA quotidien) et du DataFrame `meteo` du TP 1, joins les deux sur la date et calcule la corrélation entre température et CA.

<details><summary>✅ Corrigé</summary>

```python
# CA quotidien
ventes_jour = (
    ventes.groupby("date_vente", as_index=False)["montant"].sum()
          .rename(columns={"montant": "ca_jour", "date_vente": "date"})
)
ventes_jour["date"] = pd.to_datetime(ventes_jour["date"])

# Jointure
analyse = ventes_jour.merge(meteo, on="date", how="inner")

# Contrôle qualité AVANT d'analyser
assert analyse["ca_jour"].notna().all(), "CA manquant après jointure"
print("Lignes après jointure :", len(analyse))

# Corrélation
print(analyse[["ca_jour", "temp_max"]].corr())
```

*On utilise `how="inner"` ici car on ne veut analyser que les jours où on a **à la fois** ventes et météo. On contrôle le nombre de lignes après jointure pour repérer une éventuelle perte massive.*
</details>

### TP 3 — Validation et réconciliation finale

Tu as fusionné ventes (SQL) + objectifs (Excel). Écris les contrôles qui garantissent que la fusion n'a ni perdu ni dupliqué de CA, et que tous les mois ont bien un objectif associé.

<details><summary>✅ Corrigé</summary>

```python
# CA mensuel issu des ventes
ca_mensuel = (
    ventes.assign(mois=pd.to_datetime(ventes["date_vente"]).dt.to_period("M").astype(str))
          .groupby("mois", as_index=False)["montant"].sum()
          .rename(columns={"montant": "ca_jour"})
)

objectifs = pd.read_excel("objectifs_2024.xlsx")
suivi = ca_mensuel.merge(objectifs, on="mois", how="left")

# 1) Aucun CA perdu/dupliqué : total avant == total après
total_avant = ventes["montant"].sum()
total_apres = suivi["ca_jour"].sum()
assert round(total_avant - total_apres, 2) == 0, "Le CA total a changé après la jointure !"

# 2) Tous les mois ont un objectif
mois_sans_objectif = suivi[suivi["objectif_ca"].isna()]["mois"].tolist()
print("Mois sans objectif :", mois_sans_objectif)   # attendu : []

# 3) Pas de doublon de mois
assert suivi["mois"].is_unique, "Mois en double après la jointure !"

print("Tous les contrôles sont passés.")
```

*Les `assert` font **échouer** le script si un contrôle ne passe pas — c'est exactement le comportement voulu : mieux vaut un script qui s'arrête qu'un dashboard faux.*
</details>

---

## 7. Vidéos d'auto-formation

> Quand l'URL exacte d'une vidéo n'est pas certaine, le lien pointe vers une **recherche YouTube** : choisis la vidéo la plus vue et récente.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Interagir avec des API REST en Python (requests) | (recherche) | FR | variable | [Recherche YouTube](https://www.youtube.com/results?search_query=API+REST+Python+requests+tutoriel+fran%C3%A7ais) | GET/POST, JSON, pagination et clés API avec `requests` |
| Merging DataFrames in pandas | (recherche) | EN | variable | [Recherche YouTube](https://www.youtube.com/results?search_query=pandas+merge+join+concat+tutorial) | `merge`, `concat` et le choix du `how` (`left`, `inner`, `outer`) avec exemples |
| Cacher ses clés API en Python (.env) | (recherche) | FR | variable | [Recherche YouTube](https://www.youtube.com/results?search_query=python+dotenv+variable+environnement+cl%C3%A9+API) | Sortir les secrets du code avec `os.environ` et `python-dotenv` |

---

## 8. Quiz — 5 QCM

**Q1.** Que fait `reponse.raise_for_status()` après un appel `requests.get` ?
- a) Convertit la réponse en JSON
- b) Relance automatiquement la requête
- c) Lève une exception si le code HTTP indique une erreur (404, 500...)
- d) Affiche le statut dans la console

**Q2.** Une API doit te renvoyer ~2 000 ventes, mais ton DataFrame n'en contient que 100. Cause la plus probable ?
- a) L'API est en panne
- b) Tu n'as lu que la première page : il faut gérer la **pagination**
- c) pandas a supprimé des lignes
- d) La clé API est invalide

**Q3.** Après un `merge`, le nombre de lignes a doublé alors que tu ne l'attendais pas. Cause la plus probable ?
- a) Tu as utilisé `how="left"`
- b) La colonne de jointure n'est pas unique d'un côté → produit cartésien partiel
- c) pandas est buggé
- d) Le fichier source était vide

**Q4.** Tu veux garder **tous les jours de vente**, même ceux sans météo correspondante. Quel `how` pour ton `merge` (ventes à gauche) ?
- a) `how="inner"`
- b) `how="left"`
- c) `how="right"`
- d) Peu importe, le résultat est le même

**Q5.** Quel contrôle attrape le plus efficacement une jointure dupliquante ou une perte de lignes ?
- a) Relire le code attentivement
- b) Afficher les 5 premières lignes avec `head()`
- c) Comparer une grandeur globale (somme du CA, nombre de lignes) **avant et après** la transformation
- d) Vérifier le type des colonnes

<details><summary>✅ Réponses</summary>

1. **c)** Il transforme un échec HTTP en exception Python explicite.
2. **b)** Beaucoup d'API paginent leurs résultats (souvent 100 lignes par page) : il faut boucler jusqu'à épuisement des pages et vérifier le total attendu.
3. **b)** Une clé non unique côté droit (ou gauche) provoque une multiplication des lignes ; toujours vérifier l'unicité de la clé de jointure.
4. **b)** `how="left"` conserve toutes les lignes du DataFrame de gauche (les ventes), avec `NaN` quand la météo manque — l'équivalent du `LEFT JOIN` SQL.
5. **c)** Le contrôle des totaux avant/après attrape 80 % des bugs d'extraction : un total qui change révèle une duplication ou une perte.
</details>

---

## 9. À retenir

- **API REST en Python** : `requests.get(url, params=, headers=, timeout=)`, puis `.raise_for_status()` et `.json()`. **Gère la pagination** et **ne mets jamais ta clé API en dur**.
- **Combiner les sources** : `merge` (jointure, = `JOIN`) et `concat` (empilement, = `UNION ALL`). Choisis bien le `how`.
- **Valider, toujours** : doublons, valeurs manquantes, **contrôle des totaux** avant/après chaque transformation. C'est ce qui sépare un DA fiable d'un DA qui produit des dashboards faux.

**Aide-mémoire express :**

| Je veux… | J'utilise… |
|---|---|
| Interroger une API | `requests.get(url, params=..., timeout=10)` |
| Détecter un échec HTTP | `reponse.raise_for_status()` |
| Lire la réponse | `reponse.json()` → `dict` Python |
| Récupérer toutes les pages | boucle `while` + condition d'arrêt (`if not lignes: break`) |
| Protéger une clé API | `os.environ` / fichier `.env` (`python-dotenv`) |
| Joindre deux sources | `df1.merge(df2, on="cle", how="left")` |
| Empiler deux sources identiques | `pd.concat([df1, df2], ignore_index=True)` |
| Contrôler les doublons | `df.duplicated(subset=["cle"]).sum()` |
| Contrôler les manquants | `df.isna().sum()` |
| Contrôler les totaux | comparer `sum()` / `len()` avant et après |

> 🎯 **La phrase à graver :** *« Extraire, réconcilier, prouver. Un total qui change sans raison, c'est une jointure qui duplique ou qui perd. »*

---

[← 02 - SQL avancé pour l'analyse](02-sql-avance-analyse.md) | [🏠 Accueil](../README.md) | [📂 Module 09](README.md)
