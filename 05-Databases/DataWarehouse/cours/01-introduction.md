# Module 01 - Introduction au Data Warehouse

> **Question business :** Le directeur marketing veut comprendre pourquoi les ventes baissent en Île-de-France depuis 3 mois, mais les données sont éparpillées entre le CRM, l'ERP et Google Analytics. Comment lui donner une réponse fiable ? C'est exactement le problème que résout un Data Warehouse.

---

## Avant de commencer : l'analogie de la bibliothèque

<!-- 🔴 IMAGE/VIDÉO : Schéma animé "Librairies vs Bibliothèque" -->
<!-- 🟢 PROMPT IMAGE : "Illustration infographique en flat design montrant à gauche 4 petites librairies désorganisées (Fnac, Amazon, librairie locale) avec des fiches en désordre, et à droite une grande bibliothèque municipale moderne et ordonnée avec un catalogue numérique unifié. Une flèche relie les librairies à la bibliothèque avec le label 'ETL'. Style : éducatif, couleurs vives, texte en français. Format paysage 16:9." -->
<!-- 🟢 PROMPT VIDÉO : "Animation motion design de 30 secondes : on voit 4 magasins (CRM, ERP, Site Web, Excel) chacun avec ses propres données désordonnées. Les données sortent de chaque magasin, passent par un entonnoir labellisé 'ETL', et arrivent dans un grand bâtiment central labellisé 'Data Warehouse', où elles sont rangées proprement sur des étagères par catégorie (Ventes, Clients, Produits). Un analyste consulte ensuite un écran 'Power BI' relié au bâtiment. Style flat design, couleurs bleues et vertes." -->

Imaginez une **bibliothèque municipale** :

- Les **librairies** de la ville (Fnac, Amazon, petites librairies) = les **systèmes opérationnels** (CRM, ERP, site web). Chacun vend des livres dans son coin, avec ses propres fiches.
- La **bibliothèque municipale** = le **Data Warehouse**. Elle ne vend rien, mais elle a récupéré un exemplaire de chaque livre, les a classés par genre, auteur, année, et créé un catalogue unifié.
- Le **catalogue en ligne** de la bibliothèque = les **outils de BI** (Power BI, Tableau). Il permet à n'importe qui de chercher, filtrer, comparer.

Sans la bibliothèque, pour savoir "quel auteur français a le plus publié en 2024", il faudrait appeler chaque librairie une par une. Avec la bibliothèque, c'est une recherche de 10 secondes.

**Un Data Warehouse, c'est la bibliothèque de votre entreprise.**

---

## Qu'est-ce qu'un Data Warehouse ?

Un **Data Warehouse** (entrepôt de données) est un système de stockage centralisé conçu pour l'analyse et le reporting. Il consolide les données provenant de multiples sources pour permettre la prise de décision.

### Définition formelle (Bill Inmon, 1992)

> "Un Data Warehouse est une collection de données orientées sujet, intégrées, non volatiles et historisées, organisées pour supporter le processus de prise de décision."

### Les 4 caractéristiques fondamentales

| Caractéristique | Description | Exemple |
|-----------------|-------------|---------|
| **Orienté sujet** | Organisé autour des sujets métier | Ventes, Clients, Produits |
| **Intégré** | Données uniformisées de sources variées | Codes pays standardisés |
| **Non volatile** | Données en lecture seule, pas de modification | Historique préservé |
| **Historisé** | Conservation de l'évolution temporelle | Prix au fil du temps |

## Pourquoi un Data Warehouse ?

### Le problème des silos de données

![Le problème des silos de données](./images/01/silos-donnees.png)

**Problèmes :**
- Données dispersées et incohérentes
- Difficile de croiser les informations
- Pas de vue consolidée du business
- Requêtes analytiques impactent les systèmes opérationnels

### La solution : centralisation

![La solution : centralisation via ETL et Data Warehouse](./images/01/centralisation-dw.png)

## Composants d'un Data Warehouse

### 1. Sources de données

Les systèmes opérationnels qui alimentent le DW :
- Bases transactionnelles (ERP, CRM)
- Fichiers plats (CSV, Excel)
- APIs externes
- Logs applicatifs
- Données IoT

### 2. Zone de staging (Landing Zone)

Zone temporaire pour le chargement initial des données brutes avant transformation.

### 3. ETL / ELT

| Approche | Description | Quand l'utiliser |
|----------|-------------|------------------|
| **ETL** | Extract → Transform → Load | DW traditionnels, transformations complexes |
| **ELT** | Extract → Load → Transform | Cloud moderne, puissance de calcul dans le DW |

### 4. Data Warehouse (stockage)

Le coeur du système : stockage optimisé pour l'analytique.

### 5. Data Marts

Sous-ensembles du DW dédiés à un département ou sujet spécifique :
- Data Mart Finance
- Data Mart Marketing
- Data Mart RH

### 6. Couche de présentation

Outils de visualisation et reporting :
- Power BI
- Tableau
- Looker
- Data Studio

## Cas d'usage typiques

### Business Intelligence

- Tableaux de bord exécutifs
- Reporting mensuel/trimestriel
- Analyse des ventes et revenus
- Suivi des KPIs

### Analyse ad-hoc

- Exploration de données
- Questions business ponctuelles
- Segmentation client
- Analyse de cohortes

### Data Science

- Préparation de datasets pour le ML
- Feature engineering
- Analyse prédictive
- Modélisation statistique

## Data Warehouse vs Data Lake

| Aspect | Data Warehouse | Data Lake |
|--------|----------------|-----------|
| **Structure** | Données structurées | Toutes données (brutes) |
| **Schema** | Schema-on-write | Schema-on-read |
| **Utilisateurs** | Analystes, BI | Data Scientists, ML |
| **Traitement** | SQL | SQL, Python, Spark |
| **Coût** | Plus élevé (optimisé) | Plus bas (stockage brut) |
| **Qualité** | Haute (curatée) | Variable |

### L'évolution : le Lakehouse

Le **Lakehouse** combine le meilleur des deux mondes :
- Stockage économique du Data Lake
- Performance et gouvernance du Data Warehouse
- Support SQL et ML
- Exemples : Databricks, Delta Lake, Microsoft Fabric

## Points clés à retenir

- Un Data Warehouse centralise les données pour l'analyse
- 4 caractéristiques : orienté sujet, intégré, non volatile, historisé
- ETL/ELT transforme et charge les données
- Data Marts = sous-ensembles spécialisés
- Lakehouse = convergence DW + Data Lake

---

**Prochain module :** [02 - OLTP vs OLAP](./02-oltp-vs-olap.md)

[Retour au sommaire](./README.md)

