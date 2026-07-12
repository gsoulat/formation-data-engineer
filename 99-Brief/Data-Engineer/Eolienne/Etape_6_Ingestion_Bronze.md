# Étape 2 : Ingestion des données (Bronze Layer)

**Durée estimée :** 45-60 minutes  
**Difficulté :** ⭐⭐ Moyen

---

## 🎯 Objectifs de cette étape

À la fin de cette étape, vous aurez :

- ✅ Créé votre premier Notebook PySpark
- ✅ Compris la logique d'ingestion incrémentale
- ✅ Téléchargé des données CSV depuis GitHub
- ✅ Chargé les données dans le Lakehouse Bronze
- ✅ Initialisé la table `wind_power` dans Bronze
- ✅ Versionné votre notebook sur GitHub

---

## 📋 Prérequis

- ✅ [Étape 1 : Création des Lakehouses](Etape_1_Creation_Lakehouses.md) complétée
- ✅ Les 3 Lakehouses (Bronze, Silver, Gold) créés

---

## 📚 Comprendre l'ingestion incrémentale

### Pourquoi l'ingestion incrémentale ?

Dans un contexte réel, les données arrivent progressivement (quotidiennement, horaire, etc.). L'ingestion incrémentale permet de :

- 💰 **Réduire les coûts** : On ne recharge pas tout à chaque fois
- ⚡ **Améliorer les performances** : Traitements plus rapides
- 🔄 **Faciliter la maintenance** : Moins de risques d'erreurs

### Logique de notre ingestion

Notre notebook va :
1. **Lire** la date la plus récente dans le Lakehouse Bronze
2. **Calculer** le jour suivant (date + 1)
3. **Télécharger** le fichier CSV correspondant depuis GitHub
4. **Ajouter** les nouvelles données (mode append)

---

## 🎨 Tâche 1 : Créer le Notebook d'ingestion

### 1.1 - Créer un nouveau Notebook

1. **Dans votre Workspace** `WindPowerAnalytics`
2. **Cliquez sur "+ New item"**
3. **Sélectionnez "Notebook"**
4. **Nom** : `NB_Get_Daily_Data_Python`
5. **Cliquez sur "Create"**

### 1.2 - Attacher le Lakehouse Bronze

Un notebook doit être attaché à un Lakehouse pour pouvoir y écrire des données.

1. **Dans le panneau de gauche** du notebook, recherchez **"Add lakehouse"**
2. **Cliquez sur "Add"**
3. **Sélectionnez "Existing lakehouse"**
4. **Choisissez** `LH_Wind_Power_Bronze`
5. **Cliquez sur "Add"**

> 💡 Vous devriez maintenant voir le Lakehouse Bronze dans le panneau de gauche avec ses sections Files et Tables.

---

## 💻 Tâche 2 : Écrire le code d'ingestion

### 2.1 - Cellule 1 : Imports

Créez une première cellule et ajoutez :

```python
import requests
import pandas as pd
from datetime import datetime, timedelta
```

**Exécutez** cette cellule (Shift+Enter ou cliquez sur le bouton Play).

### 2.2 - Cellule 2 : Configuration

Ajoutez une nouvelle cellule :

```python
# URL de base du repository GitHub
base_url = "https://raw.githubusercontent.com/gsoulat/data-training-fabric/main/eolienne/"

# Chemin vers la table Bronze
bronze_table_path = "abfss://WindPowerAnalytics@onelake.dfs.fabric.microsoft.com/LH_Wind_Power_Bronze.Lakehouse/Tables/dbo/wind_power"
```

**Exécutez** cette cellule.

> 📚 **Explication** : `abfss://` est le protocole Azure Blob File System utilisé par OneLake.

### 2.3 - Cellule 3 : Initialisation (PREMIÈRE FOIS UNIQUEMENT)

Ajoutez une nouvelle cellule pour charger le premier fichier :

```python
# ⚠️ CELLULE D'INITIALISATION - À exécuter UNE SEULE FOIS
# Cette cellule crée la table Bronze avec le premier fichier de données

initial_date = "20240601"  # Premier jour disponible
initial_url = f"{base_url}{initial_date}_wind_power_data.csv"

print(f"📥 Téléchargement du fichier initial : {initial_url}")

# Télécharger et charger le premier fichier
df_initial = pd.read_csv(initial_url)
df_initial['date'] = pd.to_datetime(df_initial['date'])

print(f"✅ Fichier chargé : {len(df_initial)} lignes")
print(f"📊 Aperçu des données :")
print(df_initial.head())

# Convertir en Spark DataFrame et sauvegarder
df_spark_initial = spark.createDataFrame(df_initial)
df_spark_initial.write.format('delta').mode("overwrite").save(bronze_table_path)

print("✅ Table Bronze initialisée avec succès !")
```

**Exécutez** cette cellule. Cela va prendre environ 30-60 secondes.

> ⚠️ **IMPORTANT** : Après avoir exécuté cette cellule UNE FOIS, vous pouvez la commenter ou la supprimer pour éviter de réinitialiser la table par accident.

### 2.4 - Vérification de l'initialisation

Ajoutez une cellule pour vérifier :

```python
# Vérifier que la table existe et afficher quelques statistiques
df_check = spark.read.format("delta").load(bronze_table_path)

print(f"📊 Nombre total de lignes : {df_check.count()}")
print(f"📅 Colonnes disponibles : {df_check.columns}")
print(f"🔍 Aperçu des 5 premières lignes :")
df_check.show(5)
```

**Exécutez** cette cellule.

Vous devriez voir environ 259 200 lignes (3 turbines × 86 400 secondes par jour).

### 2.5 - Cellule 4 : Chargement des données existantes

Maintenant, créons la logique incrémentale. Ajoutez une nouvelle cellule :

```python
# Charger les données existantes depuis Bronze
df_spark = spark.read.format("delta").load(bronze_table_path)

# Convertir en Pandas pour manipulation plus facile
df_pandas = df_spark.toPandas()

print(f"📊 Données actuelles dans Bronze : {len(df_pandas)} lignes")
```

### 2.6 - Cellule 5 : Identification de la prochaine date

```python
# Trouver la date la plus récente dans les données
most_recent_date = pd.to_datetime(df_pandas['date'], format="%Y%m%d").max()

# Calculer le jour suivant
next_date = (most_recent_date + timedelta(days=1)).strftime("%Y%m%d")

print(f"📅 Date la plus récente : {most_recent_date.strftime('%Y-%m-%d')}")
print(f"➡️  Prochaine date à charger : {next_date}")
```

### 2.7 - Cellule 6 : Téléchargement des nouvelles données

```python
# Construire l'URL du fichier CSV
file_url = f"{base_url}{next_date}_wind_power_data.csv"
print(f"🌐 URL du fichier : {file_url}")

try:
    # Télécharger le CSV depuis GitHub
    df_pandas_new = pd.read_csv(file_url)
    
    # Convertir la colonne date en datetime
    df_pandas_new['date'] = pd.to_datetime(df_pandas_new['date'])
    
    print(f"✅ Nouvelles données téléchargées : {len(df_pandas_new)} lignes")
    print(f"📊 Aperçu des nouvelles données :")
    print(df_pandas_new.head())
    
except Exception as e:
    print(f"❌ Erreur lors du téléchargement : {e}")
    print(f"💡 Cela peut signifier que le fichier pour la date {next_date} n'existe pas encore.")
```

### 2.8 - Cellule 7 : Sauvegarde dans Bronze

```python
# Convertir le DataFrame Pandas en Spark DataFrame
df_spark_new = spark.createDataFrame(df_pandas_new, schema=df_spark.schema)

# Ajouter les nouvelles données à la table Bronze (mode append)
df_spark_new.write.format('delta').mode("append").save(bronze_table_path)

print("✅ Données ajoutées avec succès dans le Lakehouse Bronze")
print(f"📊 Total après ajout : {spark.read.format('delta').load(bronze_table_path).count()} lignes")
```

---

## 📝 Tâche 3 : Documenter le notebook

### 3.1 - Ajouter une cellule Markdown au début

En haut du notebook, ajoutez une cellule Markdown (cliquez sur "+ Code" puis changez le type en "Markdown") :

```markdown
# Notebook : Ingestion quotidienne de données éoliennes

## 📋 Objectif
Charger de manière incrémentale les données de production éolienne depuis GitHub vers le Lakehouse Bronze.

## 🔄 Logique
1. Identifier la date la plus récente dans Bronze
2. Calculer le jour suivant (date + 1)
3. Télécharger le fichier CSV correspondant depuis GitHub
4. Ajouter les nouvelles données en mode append

## ⚙️ Exécution
- **Fréquence recommandée** : Quotidienne (via pipeline)
- **Durée moyenne** : 50-60 secondes
- **Dépendances** : Repository GitHub public accessible

## 📦 Dépendances
- Lakehouse : LH_Wind_Power_Bronze
- Source : https://github.com/gsoulat/data-training-fabric/tree/main/eolienne
```

---

## ✅ Tâche 4 : Tester le notebook

### 4.1 - Exécution complète

1. **Cliquez sur "Run all"** en haut du notebook
2. **Attendez** que toutes les cellules s'exécutent (environ 1-2 minutes)
3. **Vérifiez** qu'il n'y a pas d'erreurs

### 4.2 - Vérifier les données dans Bronze

1. **Retournez au Lakehouse Bronze**
2. **Naviguez vers Tables → dbo → wind_power**
3. **Cliquez sur la table** pour voir son contenu
4. **Notez le nombre de lignes**

Si tout s'est bien passé, vous devriez avoir environ 518 400 lignes (2 jours de données).

**📸 Capture d'écran à prendre :** `02_bronze_table_data.png`

---

## 🗂️ Tâche 5 : Versionner sur GitHub

### 5.1 - Télécharger le notebook

1. **Dans le notebook**, cliquez sur **"File" → "Download as .ipynb"**
2. **Sauvegardez** le fichier sur votre ordinateur

### 5.2 - Uploader sur GitHub

1. **Allez sur GitHub** → votre repository `fabric-wind-power-pipeline`
2. **Naviguez vers** `notebooks/bronze/`
3. **Cliquez sur "Add file" → "Upload files"**
4. **Glissez-déposez** votre fichier `.ipynb`
5. **Commit message** : `feat: Add Bronze layer ingestion notebook`
6. **Cliquez sur "Commit changes"**

**📸 Capture d'écran à prendre :** `02_github_notebook_uploaded.png`

---

## ✅ Vérification de l'étape

- [ ] ✅ Notebook `NB_Get_Daily_Data_Python` créé
- [ ] ✅ Lakehouse Bronze attaché au notebook
- [ ] ✅ Table `wind_power` initialisée dans Bronze
- [ ] ✅ Logique incrémentale implémentée et testée
- [ ] ✅ Au moins 2 jours de données chargés (≈518k lignes)
- [ ] ✅ Notebook documenté avec cellule Markdown
- [ ] ✅ Notebook versionné sur GitHub
- [ ] ✅ 2 captures d'écran prises

---

## 🎓 Ce que vous avez appris

- ✅ Créer et configurer un Notebook dans Fabric
- ✅ Attacher un Lakehouse à un Notebook
- ✅ Utiliser Pandas pour télécharger des données depuis une URL
- ✅ Convertir entre Pandas DataFrame et Spark DataFrame
- ✅ Écrire des données au format Delta Lake
- ✅ Implémenter une logique d'ingestion incrémentale
- ✅ Versionner du code sur GitHub

---

## 🎯 Prochaine étape

➡️ **[Étape 3 : Transformation Bronze → Silver](Etape_2_Transformation_Silver.md)**

*Étape 2 complétée ✅ | Temps : ~60 min | Total cumulé : ~135 min*
