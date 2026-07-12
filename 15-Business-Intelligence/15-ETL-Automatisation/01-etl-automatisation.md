# 01 — Automatiser la collecte : ETL

| | |
|---|---|
| **Phase** | Phase 3 — Flux & BI avancée |
| **Durée indicative** | ~30 h |
| **Compétence visée** | **C2 — Automatiser l'extraction et la préparation des données** (niveau 1) |
| **Pré-requis** | Module **1.2** (Python & pandas / EDA) · Module **3.1** (Processus de collecte) |
| **Certification** | RNCP-38616 — Concepteur développeur en IA et analyse big data (option Data Analyse) |

---

## Objectifs pédagogiques

À la fin de ce module, tu seras capable de :

- **Expliquer** ce qu'est un processus **ETL** et **ELT**, et choisir le bon selon le contexte.
- **Construire un flux Power Query pas à pas** : importer un dossier de fichiers, appliquer des étapes de transformation, **fusionner** et **ajouter** des requêtes, créer des **paramètres**, et **actualiser** automatiquement.
- **Écrire un mini-ETL en Python** : un script d'**extraction**, une **transformation** pandas, et un **chargement** (CSV / base SQLite).
- **Situer les connecteurs no-code** (Fivetran, Stitch) : ce qu'ils font, leurs limites, et quand les préférer à du code maison.
- **Mettre en place l'orchestration et la planification** d'un rafraîchissement automatique.
- **Gérer les erreurs et produire des logs** exploitables pour fiabiliser ton pipeline.

---

## Pourquoi c'est utile au Data Analyst

Au quotidien, tu ne fais pas une analyse *une fois* : tu la refais **chaque semaine, chaque mois**. Si tu copies-colles à la main 12 fichiers Excel de 12 magasins tous les lundis, tu perds 2 h, tu fais des erreurs, et personne ne peut reprendre ton travail si tu es absent.

L'ETL répond exactement à ça : **tu construis le flux une fois, il se rejoue tout seul**. C'est ce qui transforme un tableau de bord « bricolé » en **produit data fiable et reproductible**.

> 💡 Le réflexe DA : *« Si je dois refaire cette manip plus de deux fois, je l'automatise. »*

**Cas fil rouge du module :** consolider automatiquement les **fichiers de ventes de plusieurs magasins** d'une enseigne retail du Nord (Lille, Roubaix, Tourcoing, Valenciennes…) en une seule table propre, prête pour Power BI.

---

## Contenu

### ETL vs ELT : de quoi parle-t-on ?

**ETL = Extract, Transform, Load.** Trois étapes :

1. **Extract (Extraire)** — récupérer les données brutes depuis leurs sources : fichiers CSV/Excel, base de données, API, scraping…
2. **Transform (Transformer)** — nettoyer, normaliser, dédupliquer, calculer, joindre. C'est le cœur de la valeur.
3. **Load (Charger)** — écrire le résultat propre dans la cible : un entrepôt, une base, un fichier, un modèle Power BI.

```
SOURCES                ETL                          CIBLE
┌──────────┐
│ ventes_  │ ──Extract──┐
│ lille.csv│            │
├──────────┤            ▼
│ ventes_  │      ┌─────────────┐        ┌──────────────────┐
│ roubaix..│ ───► │ Transform   │ ─Load─►│ table_ventes     │
├──────────┤      │ (nettoyage, │        │ consolidée       │
│ API CRM  │ ───► │  jointures) │        │ (BDD / Power BI) │
└──────────┘      └─────────────┘        └──────────────────┘
```

**ELT = Extract, Load, Transform.** On inverse les deux dernières étapes : on **charge d'abord** les données brutes dans un entrepôt cloud puissant (BigQuery, Snowflake, Redshift), **puis** on transforme directement dedans avec du SQL.

| Critère | **ETL** | **ELT** |
|---|---|---|
| Ordre | Transforme **avant** de charger | Charge brut, transforme **après** |
| Où se fait la transfo | Sur ta machine / un serveur ETL | Dans l'entrepôt cloud |
| Volumétrie idéale | Petite à moyenne | Très grande (cloud scalable) |
| Outils typiques | Power Query, scripts Python, Talend | BigQuery + dbt, Snowflake + dbt |
| Pour un DA junior | **Le plus courant** (Power Query, pandas) | À connaître, croisé en équipe data |

> 📌 **À retenir :** en tant que DA, tu feras surtout de l'**ETL** (Power Query, Python). L'**ELT** est plutôt le terrain du Data Engineer, mais le vocabulaire revient sans cesse en réunion : sache le situer.

---

### Power Query, pas à pas

Power Query est le moteur ETL **intégré à Excel ET à Power BI**. Tu décris une suite de transformations ; il les **enregistre** et les **rejoue** à chaque actualisation. C'est de l'automatisation **sans écrire de code** (le langage M est généré pour toi).

#### a) Importer un dossier entier (le geste-clé du fil rouge)

Plutôt que d'importer 12 fichiers un par un, on importe **le dossier** qui les contient. Quand un 13ᵉ magasin arrive, il suffit de **déposer son fichier** dans le dossier et de cliquer sur Actualiser.

1. Dans Power BI Desktop : **Accueil → Obtenir les données → Plus… → Dossier** (dans Excel : **Données → Obtenir des données → À partir d'un fichier → À partir d'un dossier**).
2. Sélectionne le dossier `ventes_magasins/`.
3. Dans la fenêtre d'aperçu, clique sur **Combiner et transformer**.
4. Power Query détecte le format, te demande quelle feuille/table prendre comme **fichier exemple**, puis crée automatiquement :
   - une requête **« Transformer le fichier exemple »** (les transfos appliquées à chaque fichier),
   - une fonction **« Transformer le fichier »**,
   - la requête finale qui empile tous les fichiers.

> 💡 Une colonne `Source.Name` apparaît : elle contient le **nom du fichier d'origine**. Garde-la pour tracer de quel magasin vient chaque ligne.

#### b) Les étapes appliquées

À droite, le volet **« Étapes appliquées »** liste *tout* ce que tu fais, dans l'ordre. Chaque clic = une étape. Tu peux :

- **renommer** une étape (clic droit → Renommer) pour la rendre lisible (`Filtre dates 2025` plutôt que `Lignes filtrées`),
- **revenir en arrière** en cliquant sur une étape antérieure (tu vois l'état des données à ce moment-là),
- **supprimer** une étape avec la croix,
- **réordonner** (avec prudence : l'ordre compte !).

> ⚠️ **Erreur courante :** supprimer une colonne *tôt* puis la réutiliser *plus tard* dans une autre étape → l'étape casse (`La colonne 'X' du tableau est introuvable`). Pense l'ordre comme une recette.

#### c) Transformations les plus utiles

| Transformation | Où | À quoi ça sert |
|---|---|---|
| Promouvoir les en-têtes | Transformer → Utiliser la 1ʳᵉ ligne comme en-têtes | La 1ʳᵉ ligne devient les noms de colonnes |
| Modifier le type | Clic sur l'icône du type (colonne) | Forcer Date, Nombre décimal, Texte… |
| Remplacer les valeurs | Transformer → Remplacer les valeurs | Corriger `N/A` → vide, virgule → point |
| Supprimer les doublons | Accueil → Supprimer les lignes → doublons | Dédupliquer |
| Colonne conditionnelle | Ajouter une colonne → Colonne conditionnelle | Créer une catégorie (ex. région) |
| Fractionner colonne | Transformer → Fractionner la colonne | Séparer `2025-06-21` ou `Nom Prénom` |
| Remplir vers le bas | Transformer → Remplir → Vers le bas | Propager une valeur de regroupement |

> ⚠️ **Erreur courante :** laisser Power Query **détecter le type automatiquement** sur un fichier puis recevoir un fichier où la colonne est légèrement différente. Définis **explicitement** les types à la fin de tes transfos.

#### d) Ajouter des requêtes (append) vs Fusionner des requêtes (merge)

C'est **la** distinction à maîtriser :

- **Ajouter des requêtes (Append)** = empiler **verticalement**. Mêmes colonnes, on met les lignes les unes sous les autres. → *« Je colle les ventes de Lille SOUS celles de Roubaix. »*
  - Accueil → **Ajouter des requêtes**.
- **Fusionner des requêtes (Merge)** = joindre **horizontalement**, comme un `JOIN` SQL. On ajoute des **colonnes** venant d'une autre table, mises en correspondance par une **clé commune**. → *« J'ajoute le libellé du produit à partir d'une table référentiel, via `code_produit`. »*
  - Accueil → **Fusionner des requêtes**.

Types de fusion (jointures) disponibles : **Externe gauche** (garde tout à gauche, défaut), Externe droite, Externe complète, **Interne** (que les correspondances), Anti gauche / Anti droite (les non-correspondances — utile pour détecter les codes orphelins).

> 💡 **Règle mémo :** *Append = plus de **lignes**. Merge = plus de **colonnes**.*

> ⚠️ **Erreur courante :** une fusion qui **multiplie les lignes**. Si la clé n'est pas unique dans la table de droite, chaque ligne de gauche se duplique. Vérifie l'unicité de ta clé avant de fusionner.

#### e) Paramètres

Un **paramètre** rend ton flux réutilisable. Au lieu d'écrire en dur `C:\Users\moi\ventes_magasins`, tu crées un paramètre `CheminDossier`.

- **Accueil → Gérer les paramètres → Nouveau paramètre.**
- Type : Texte. Valeur actuelle : le chemin.
- Dans ta requête « Source », remplace le chemin en dur par le paramètre.

Avantage : quand le flux change de poste/serveur, tu modifies **une seule valeur**. On utilise aussi des paramètres pour une date de début, un nom de magasin à filtrer, une URL d'API…

#### f) Actualiser

- **Manuel :** Accueil → Actualiser l'aperçu (dans l'éditeur) ; ou bouton **Actualiser** sur le rapport.
- **Automatique :** une fois publié sur **Power BI Service**, configure une **actualisation planifiée** (ex. tous les jours à 6 h) via une **passerelle de données** (gateway) si la source est sur un poste/réseau local. → on rejoint l'orchestration (§3.5).

---

### ETL en Python

Power Query couvre 80 % des besoins d'un DA. Mais dès que tu as besoin de **logique complexe**, d'appels **API**, de **réutilisation** ou de **planification serveur**, **Python** prend le relais. Le principe reste **E → T → L**.

#### a) Extraction — lire les fichiers de tous les magasins

```python
from pathlib import Path
import pandas as pd

DOSSIER_SOURCE = Path("data/ventes_magasins")

def extraire(dossier: Path) -> pd.DataFrame:
    """Lit tous les CSV du dossier et les empile (équivalent 'Append' Power Query)."""
    fichiers = sorted(dossier.glob("ventes_*.csv"))
    if not fichiers:
        raise FileNotFoundError(f"Aucun fichier 'ventes_*.csv' dans {dossier}")

    dfs = []
    for f in fichiers:
        df = pd.read_csv(f, sep=";", encoding="utf-8")
        df["magasin"] = f.stem.replace("ventes_", "")  # trace l'origine (= Source.Name)
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)
    print(f"[EXTRACT] {len(fichiers)} fichiers, {len(data)} lignes au total")
    return data
```

#### b) Transformation — nettoyer et enrichir avec pandas

```python
def transformer(data: pd.DataFrame, referentiel: pd.DataFrame) -> pd.DataFrame:
    """Nettoie, type, déduplique, calcule le CA, joint le référentiel produit."""
    df = data.copy()

    # 1. Normaliser les noms de colonnes (minuscules, sans espaces)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # 2. Typer proprement
    df["date_vente"] = pd.to_datetime(df["date_vente"], format="%Y-%m-%d", errors="coerce")
    df["quantite"] = pd.to_numeric(df["quantite"], errors="coerce")
    df["prix_unitaire"] = (
        df["prix_unitaire"].astype(str).str.replace(",", ".").astype(float)
    )

    # 3. Supprimer les lignes inexploitables
    avant = len(df)
    df = df.dropna(subset=["date_vente", "code_produit", "quantite"])
    print(f"[TRANSFORM] {avant - len(df)} lignes invalides supprimées")

    # 4. Dédupliquer
    df = df.drop_duplicates()

    # 5. Calculer le chiffre d'affaires
    df["ca"] = df["quantite"] * df["prix_unitaire"]

    # 6. Joindre le référentiel produit (équivalent 'Merge' Power Query, jointure gauche)
    df = df.merge(referentiel, on="code_produit", how="left")
    orphelins = df["libelle_produit"].isna().sum()
    if orphelins:
        print(f"[TRANSFORM] ⚠️ {orphelins} ventes sans produit au référentiel")

    return df
```

#### c) Chargement — écrire le résultat

```python
import sqlite3

def charger_csv(df: pd.DataFrame, chemin: str) -> None:
    df.to_csv(chemin, index=False, encoding="utf-8")
    print(f"[LOAD] {len(df)} lignes écrites dans {chemin}")

def charger_sqlite(df: pd.DataFrame, base: str, table: str) -> None:
    with sqlite3.connect(base) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"[LOAD] table '{table}' rechargée dans {base}")
```

#### d) Orchestrer le tout (le `main`)

```python
def main():
    referentiel = pd.read_csv("data/referentiel_produits.csv", sep=";")
    brut = extraire(DOSSIER_SOURCE)
    propre = transformer(brut, referentiel)
    charger_csv(propre, "data/ventes_consolidees.csv")
    charger_sqlite(propre, "data/retail.db", "ventes")
    print("[OK] ETL terminé")

if __name__ == "__main__":
    main()
```

> 💡 Cette structure **E / T / L en fonctions séparées** est exactement ce qu'on attend en certification : c'est **lisible, testable et réutilisable**.

---

### Les connecteurs no-code : Fivetran, Stitch

Quand les sources sont **standard et nombreuses** (Salesforce, Shopify, Google Analytics, Stripe, une base Postgres…), réécrire un connecteur à la main est une perte de temps. Des plateformes managées le font pour toi.

- **Fivetran** — leader du marché. Connecteurs pré-construits, gestion automatique des changements de schéma, mode **ELT** (charge dans l'entrepôt puis transforme, souvent avec dbt). Robuste mais **payant** (au volume de lignes traitées).
- **Stitch** (Talend) — plus léger, basé sur le standard open-source **Singer**, orienté petites/moyennes équipes, tarif plus accessible.

**Ce qu'ils apportent :** zéro maintenance de connecteur, reprise sur erreur, planification intégrée, supervision.

**Quand les utiliser :**

| Situation | Choix recommandé |
|---|---|
| Sources SaaS standard (Shopify, Salesforce…), équipe sans dev | **No-code** (Fivetran / Stitch) |
| Logique métier très spécifique, source maison exotique | **Code** (Python) |
| Budget serré, petit volume, un seul fichier | **Power Query** ou script Python |
| Gros volume cloud + équipe data engineer | **No-code (ELT) + dbt** |

> 📌 En tant que DA junior, tu ne **configures** pas forcément Fivetran, mais tu dois **savoir qu'il existe** et expliquer le compromis *« acheter un connecteur vs le coder »*.

---

### Orchestration et planification

Un ETL n'a de valeur que s'il se **rejoue tout seul, au bon moment, dans le bon ordre**. C'est le rôle de l'**orchestration**.

- **Planification simple :**
  - **Power BI Service** : actualisation planifiée (+ passerelle pour sources locales).
  - **Tâches système** : `cron` (Linux/Mac) ou **Planificateur de tâches** (Windows) pour lancer ton script Python à heure fixe.
    ```bash
    # cron : tous les jours à 6h00 → exécute l'ETL et journalise la sortie
    0 6 * * * /usr/bin/python3 /opt/etl/etl_ventes.py >> /var/log/etl_ventes.log 2>&1
    ```
- **Orchestrateurs dédiés** (quand il y a **plusieurs étapes dépendantes**) : **Apache Airflow**, **Dagster**, **Prefect**. Ils gèrent les dépendances (extraire **avant** de charger), les relances en cas d'échec, les alertes, l'historique. C'est surtout le terrain du Data Engineer, mais le concept de **DAG** (graphe des tâches) est à connaître.

> 📌 **À retenir :** planifier = *« à 6 h »*. Orchestrer = *« d'abord A, puis B si A a réussi, sinon alerte »*.

---

### Gestion des erreurs et logs

Un pipeline automatisé **échoue forcément un jour** (fichier manquant, colonne renommée, API en panne). Ce qui distingue un pro : **savoir que ça a échoué, et pourquoi**.

#### a) Logging propre en Python

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log", encoding="utf-8"),
        logging.StreamHandler(),  # affiche aussi dans la console
    ],
)
logger = logging.getLogger("etl_ventes")

def extraire(dossier):
    fichiers = sorted(dossier.glob("ventes_*.csv"))
    if not fichiers:
        logger.error("Aucun fichier source trouvé dans %s", dossier)
        raise FileNotFoundError(dossier)
    logger.info("%d fichiers à traiter", len(fichiers))
    # ...
```

> 💡 `print` disparaît ; un **log** est horodaté, hiérarchisé (`INFO`/`WARNING`/`ERROR`) et **conservé dans un fichier** que tu peux relire après coup.

#### b) Capturer les erreurs sans tout faire planter

```python
def lire_fichier(chemin):
    try:
        return pd.read_csv(chemin, sep=";", encoding="utf-8")
    except Exception as e:
        logger.warning("Fichier ignoré %s : %s", chemin, e)
        return None  # on continue avec les autres fichiers
```

> ⚠️ **Erreur courante :** un `try/except` trop large (`except: pass`) qui **avale les erreurs en silence**. Tu crois que tout va bien… alors qu'un magasin manque dans le rapport. Logue **toujours** ce que tu captures.

> ⚠️ **Erreur courante :** ne pas distinguer une erreur **bloquante** (référentiel introuvable → on arrête) d'un **avertissement** (un magasin sur 12 absent → on continue mais on signale).

#### Encadré — Top 5 des erreurs qui cassent un ETL

1. **Encodage** : `UnicodeDecodeError` → un fichier en `latin-1`/`cp1252` au milieu d'UTF-8. → préciser/tester l'encodage.
2. **Séparateur** : CSV en `,` au lieu de `;` → tout dans une seule colonne. → vérifier `sep`.
3. **Schéma qui change** : une colonne renommée à la source → le `merge` ou le typage casse. → valider les colonnes attendues.
4. **Type implicite** : `prix` lu comme texte (`"12,50"`) → calculs faux. → typer explicitement.
5. **Clé non unique** en fusion → explosion du nombre de lignes. → vérifier l'unicité avant `merge`.

---

## Travaux pratiques

> 🎯 Objectif global : construire un **mini-ETL** qui consolide les ventes de plusieurs magasins, **en Power Query** puis **en Python**.
>
> **Jeu de données** : crée un dossier `data/ventes_magasins/` avec 3 fichiers (`ventes_lille.csv`, `ventes_roubaix.csv`, `ventes_tourcoing.csv`), colonnes `date_vente;code_produit;quantite;prix_unitaire`, plus un `referentiel_produits.csv` (`code_produit;libelle_produit;categorie`). Mets volontairement quelques pièges (une virgule décimale, une ligne vide, un code produit absent du référentiel).

### TP1 — Consolidation Power Query (import de dossier + actualisation)

Importe le dossier `ventes_magasins/` dans Power BI (ou Excel), combine les fichiers, ajoute la colonne d'origine, type les colonnes, puis ajoute un 4ᵉ fichier et actualise.

<details>
<summary>Corrigé TP1</summary>

1. **Obtenir les données → Dossier** → sélectionner `ventes_magasins/` → **Combiner et transformer**.
2. Choisir le fichier exemple, valider → Power Query crée la requête empilée + la fonction de transformation.
3. Vérifier la colonne `Source.Name` ; la renommer `magasin` puis **Remplacer les valeurs** pour retirer `ventes_` et `.csv` (ou Fractionner / Extraire).
4. **Modifier le type** de chaque colonne : `date_vente` → Date, `quantite` → Nombre entier, `prix_unitaire` → Nombre décimal (penser à remplacer `,` par `.` si nécessaire via Remplacer les valeurs).
5. **Renommer les étapes appliquées** pour les rendre lisibles.
6. **Fermer & appliquer.**
7. Déposer `ventes_valenciennes.csv` dans le dossier → **Actualiser** → la nouvelle ligne apparaît **sans aucune autre manip** : c'est ça l'automatisation. ✅
</details>

### TP2 — Append + Merge en Power Query

À partir des ventes consolidées, **fusionne** (merge) la requête `referentiel_produits` sur `code_produit` (jointure externe gauche) pour ajouter `libelle_produit` et `categorie`. Identifie les ventes sans produit au référentiel.

<details>
<summary>Corrigé TP2</summary>

1. Importer aussi `referentiel_produits.csv` comme requête.
2. Sur la requête de ventes : **Accueil → Fusionner des requêtes** → table de droite = `referentiel_produits`, clé = `code_produit`, type **Externe gauche**.
3. Cliquer sur l'icône d'expansion de la colonne fusionnée → cocher `libelle_produit` et `categorie` (décocher « utiliser le nom d'origine comme préfixe »).
4. **Détecter les orphelins** : filtrer `libelle_produit` = `null`, ou faire une fusion **Anti gauche** pour isoler les codes absents du référentiel.
5. ⚠️ Vérifier que le nombre de lignes **n'a pas augmenté** (clé unique côté référentiel). ✅
</details>

### TP3 — Mini-ETL Python (E / T / L)

Écris `etl_ventes.py` reprenant les fonctions `extraire`, `transformer`, `charger_csv`, `charger_sqlite` du cours. Lance-le et vérifie le fichier `ventes_consolidees.csv` et la table SQLite.

<details>
<summary>Corrigé TP3</summary>

Reprendre les blocs §3.3 a → d dans un seul fichier. Points de validation :

```python
import pandas as pd, sqlite3
df = pd.read_csv("data/ventes_consolidees.csv")
assert "ca" in df.columns                       # CA calculé
assert df["date_vente"].notna().all()           # dates valides
assert df.duplicated().sum() == 0               # pas de doublons

with sqlite3.connect("data/retail.db") as c:
    n = pd.read_sql("SELECT COUNT(*) n FROM ventes", c)["n"][0]
print("Lignes en base :", n)
```

Sortie attendue (exemple) :
```
[EXTRACT] 3 fichiers, 1542 lignes au total
[TRANSFORM] 4 lignes invalides supprimées
[TRANSFORM] ⚠️ 2 ventes sans produit au référentiel
[LOAD] 1536 lignes écrites dans data/ventes_consolidees.csv
[LOAD] table 'ventes' rechargée dans data/retail.db
[OK] ETL terminé
```
</details>

### TP4 — Robustesse : logs + gestion d'erreurs

Ajoute le `logging` (fichier `logs/etl.log`) à ton script, et un `try/except` par fichier qui **ignore et loggue** un fichier illisible sans faire planter le pipeline. Teste en mettant un fichier corrompu dans le dossier.

<details>
<summary>Corrigé TP4</summary>

1. Configurer `logging.basicConfig` (cf. §3.6 a) avec un `FileHandler` + `StreamHandler`.
2. Remplacer les `print` par `logger.info / warning / error`.
3. Entourer la lecture de chaque fichier d'un `try/except` qui `logger.warning(...)` et retourne `None` ; filtrer les `None` avant `concat`.
4. Distinguer **bloquant** (référentiel absent → `logger.error` + `raise`) et **non bloquant** (un magasin illisible → `warning` + on continue).
5. Vérifier que `logs/etl.log` contient bien l'horodatage et le fichier ignoré. ✅
</details>

### TP5 (bonus) — Planification

Planifie ton script pour qu'il s'exécute tous les jours à 6 h (cron sur Mac/Linux, Planificateur de tâches sur Windows), avec la sortie redirigée vers un log.

<details>
<summary>Corrigé TP5</summary>

- **Mac/Linux :** `crontab -e` puis
  ```
  0 6 * * * /usr/bin/python3 /chemin/etl_ventes.py >> /chemin/logs/cron.log 2>&1
  ```
- **Windows :** Planificateur de tâches → Créer une tâche de base → Déclencheur quotidien 6 h → Action « Démarrer un programme » → `python.exe` avec argument le chemin du script.
- Vérifier le lendemain que le log s'est bien rempli et que le CSV a été régénéré. ✅
</details>

---

## Vidéos d'auto-formation

> ⚠️ Vérifie toujours que la vidéo correspond bien (les chaînes renomment / suppriment parfois). En cas de doute, utilise le **lien de recherche**.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Qu'est-ce qu'un processus ETL ? Définition & fonctionnement | (DataScientest / divers) | 🇫🇷 FR | ~10 min | https://www.youtube.com/watch?v=C8VGO2vZeVQ | Le concept ETL expliqué simplement, vocabulaire de base |
| ETL vs ELT : les Différences Clés (expliqué simplement) | (recherche) | 🇫🇷 FR | ~8 min | https://www.youtube.com/watch?v=-dZ617wt61c | La distinction ETL/ELT, quand utiliser l'un ou l'autre |
| Power Query : fusionner des requêtes | (recherche) | 🇫🇷 FR | ~10 min | https://www.youtube.com/watch?v=tQhaB6ftkbM | Merge pas à pas, types de jointures, clé commune |
| Combine Excel Files from a Folder Dynamically in Power Query | (recherche) | 🇬🇧 EN | ~15 min | https://www.youtube.com/watch?v=0UsaRPBBTS0 | Import de dossier + actualisation auto (le geste du fil rouge) |
| Automated ELT Explained: Why Do Top Data Teams Rely on Fivetran? | Fivetran | 🇬🇧 EN | ~12 min | https://www.youtube.com/watch?v=fO1GtUyPVEU | Ce qu'apporte un connecteur no-code managé (Fivetran / ELT) |

> 💡 Liens de secours pour explorer :
> - Power Query FR : https://www.youtube.com/results?search_query=power+query+français+débutant+ETL
> - ETL Python : https://www.youtube.com/results?search_query=ETL+python+pandas+tutorial
> - Fivetran / ELT : https://www.youtube.com/results?search_query=fivetran+ELT+explained

---

## Quiz — 5 QCM

**Q1.** Dans « ETL », que signifie le **T** ?
- a) Transfer
- b) Transform
- c) Trigger
- d) Table

**Q2.** Quelle différence entre **ETL** et **ELT** ?
- a) ELT n'a pas d'étape de chargement
- b) ELT charge d'abord les données brutes puis les transforme dans l'entrepôt
- c) ETL ne fonctionne qu'avec Python
- d) Il n'y a aucune différence

**Q3.** Dans Power Query, pour **empiler verticalement** plusieurs tables ayant les mêmes colonnes, j'utilise :
- a) Fusionner des requêtes (Merge)
- b) Ajouter des requêtes (Append)
- c) Une colonne conditionnelle
- d) Remplir vers le bas

**Q4.** Quel est le risque principal d'une **fusion (merge)** sur une clé **non unique** côté table de droite ?
- a) La requête devient plus rapide
- b) Les lignes de gauche se **dupliquent** (explosion du nombre de lignes)
- c) Power Query supprime les doublons automatiquement
- d) Rien, c'est sans conséquence

**Q5.** Pour fiabiliser un ETL automatisé, la **meilleure pratique** est :
- a) Mettre `except: pass` partout pour ne jamais planter
- b) Utiliser des `print` que personne ne lit
- c) Logger les événements (INFO/WARNING/ERROR) dans un fichier horodaté
- d) Ne jamais gérer les erreurs, c'est plus simple

<details>
<summary>Réponses</summary>

1. **b** — Transform.
2. **b** — ELT = Extract, **Load**, **Transform** : on charge brut puis on transforme dans l'entrepôt.
3. **b** — Append empile les lignes (mêmes colonnes). Merge ajoute des colonnes.
4. **b** — Une clé non unique à droite multiplie les lignes de gauche : toujours vérifier l'unicité.
5. **c** — Des logs horodatés et hiérarchisés rendent les échecs visibles et diagnosticables.
</details>

---

## À retenir

- **ETL = Extract → Transform → Load.** **ELT** inverse les deux derniers (charge brut, transforme dans l'entrepôt cloud). Le DA fait surtout de l'ETL.
- **Power Query** automatise sans code : **import de dossier**, **étapes appliquées** rejouables, **Append** (plus de lignes) vs **Merge** (plus de colonnes), **paramètres** et **actualisation planifiée**.
- **Python** prend le relais pour la logique complexe : structure en **fonctions E / T / L** lisibles et testables.
- **Fivetran / Stitch** = connecteurs no-code managés : à privilégier pour des **sources SaaS standard**, à connaître même sans les configurer.
- **Orchestrer** ≠ planifier : planifier c'est « à 6 h », orchestrer c'est « A puis B si A réussit, sinon alerte ».
- **Logs + gestion d'erreurs** distinguent un script bricolé d'un pipeline pro : jamais d'`except: pass`, toujours horodater et hiérarchiser.
- **Réflexe DA :** si tu fais une manip plus de deux fois, **automatise-la**.
