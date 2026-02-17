# Chapitre 10 : Exercices Pratiques

## Table des matières

1. [Exercice 1 : Mise en place d'un Data Catalog](#exercice-1--mise-en-place-dun-data-catalog)
2. [Exercice 2 : Ingestion multi-sources](#exercice-2--ingestion-multi-sources)
3. [Exercice 3 : Qualité et Lineage](#exercice-3--qualité-et-lineage)
4. [Exercice 4 : Gouvernance et Glossaire](#exercice-4--gouvernance-et-glossaire)
5. [Exercice 5 : Automatisation via l'API](#exercice-5--automatisation-via-lapi)

---

## Exercice 1 : Mise en place d'un Data Catalog

### Objectif
Installer OpenMetadata, connecter une base de données et explorer l'interface.

### Contexte
Vous êtes Data Engineer dans une entreprise e-commerce. La direction vous demande de mettre en place un data catalog pour centraliser la documentation et améliorer la découvrabilité des données.

### Étapes

#### 1.1 Installation

- [ ] Créer un répertoire de travail `openmetadata-lab`
- [ ] Télécharger le `docker-compose.yml` officiel
- [ ] Lancer OpenMetadata avec `docker compose up -d`
- [ ] Vérifier que tous les services sont en bonne santé
- [ ] Accéder à l'interface sur `http://localhost:8585`
- [ ] Se connecter avec `admin` / `admin`

#### 1.2 Préparer la base PostgreSQL

- [ ] Ajouter un service PostgreSQL au `docker-compose.yml`
- [ ] Créer le script `init-db.sql` avec les tables suivantes :
  - `raw.customers` (customer_id, first_name, last_name, email, phone, created_at)
  - `raw.products` (product_id, name, category, price, stock_quantity)
  - `raw.orders` (order_id, customer_id, order_date, total_amount, status)
  - `raw.order_items` (item_id, order_id, product_id, quantity, unit_price)
  - `analytics.daily_sales` (vue)
- [ ] Insérer des données d'exemple (minimum 10 lignes par table)

#### 1.3 Connecter la source

- [ ] Ajouter le service PostgreSQL dans OpenMetadata
- [ ] Tester la connexion
- [ ] Lancer une ingestion de métadonnées
- [ ] Vérifier que toutes les tables et colonnes apparaissent dans Explore

### Livrables
- Screenshot de la page Explore montrant les tables ingérées
- Fichiers `docker-compose.yml` et `init-db.sql`

### Critères de validation
- ✅ OpenMetadata accessible sur le port 8585
- ✅ PostgreSQL connecté et ingéré
- ✅ 5 tables (4 tables + 1 vue) visibles dans Explore
- ✅ Toutes les colonnes avec leurs types corrects

---

## Exercice 2 : Ingestion multi-sources

### Objectif
Connecter plusieurs sources et explorer les métadonnées croisées.

### Contexte
L'entreprise utilise PostgreSQL pour les données transactionnelles et possède des transformations dbt. Vous devez connecter toutes ces sources.

### Étapes

#### 2.1 Ajouter des tables analytiques

- [ ] Créer un schéma `analytics` dans PostgreSQL
- [ ] Ajouter les tables :

```sql
-- Table des métriques clients
CREATE TABLE analytics.customer_metrics AS
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS full_name,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS lifetime_value,
    MAX(o.order_date) AS last_order_date,
    CASE
        WHEN MAX(o.order_date) > CURRENT_DATE - INTERVAL '90 days' THEN 'active'
        WHEN MAX(o.order_date) > CURRENT_DATE - INTERVAL '365 days' THEN 'inactive'
        ELSE 'churned'
    END AS segment
FROM raw.customers c
LEFT JOIN raw.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name;

-- Table des métriques produits
CREATE TABLE analytics.product_performance AS
SELECT
    p.product_id,
    p.name AS product_name,
    p.category,
    COUNT(oi.item_id) AS times_ordered,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    AVG(oi.unit_price) AS avg_selling_price
FROM raw.products p
LEFT JOIN raw.order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.category;
```

#### 2.2 Relancer l'ingestion

- [ ] Relancer l'ingestion de métadonnées
- [ ] Vérifier les nouvelles tables dans Explore
- [ ] Lancer une ingestion de **Lineage**
- [ ] Vérifier le lineage automatique détecté

#### 2.3 Profiling

- [ ] Configurer une ingestion de type **Profiler**
- [ ] Exécuter le profiling sur toutes les tables
- [ ] Explorer les statistiques dans l'onglet Profiler de chaque table
- [ ] Identifier les colonnes avec des valeurs NULL

### Livrables
- Screenshot du lineage détecté
- Screenshot du profiling d'au moins 2 tables
- Note sur les anomalies détectées par le profiling

### Critères de validation
- ✅ Schéma `analytics` avec 2+ tables
- ✅ Lineage visible entre `raw.*` et `analytics.*`
- ✅ Profiling exécuté avec statistiques visibles

---

## Exercice 3 : Qualité et Lineage

### Objectif
Mettre en place des tests de qualité et enrichir le lineage.

### Contexte
L'équipe data a identifié des problèmes de qualité. Vous devez mettre en place des contrôles pour détecter et prévenir les anomalies.

### Étapes

#### 3.1 Tests de qualité sur `raw.customers`

- [ ] Créer les tests suivants :
  - `customer_id` : non null, unique
  - `email` : non null, unique, format email (regex)
  - `first_name` : non null
  - `created_at` : non null
  - Table : nombre de lignes entre 1 et 1 000 000

#### 3.2 Tests de qualité sur `raw.orders`

- [ ] Créer les tests suivants :
  - `order_id` : non null, unique
  - `customer_id` : non null
  - `total_amount` : valeurs entre 0 et 100 000
  - `status` : valeurs dans l'ensemble `['pending', 'completed', 'cancelled', 'refunded']`
  - Test SQL custom : intégrité référentielle (aucun `customer_id` orphelin)

#### 3.3 Test SQL avancé : fraîcheur

- [ ] Créer un test SQL pour vérifier la fraîcheur de `raw.orders` :
  - La dernière commande ne doit pas dater de plus de 7 jours
  - Formule : `EXTRACT(EPOCH FROM (NOW() - MAX(order_date))) / 86400`

#### 3.4 Exécuter et analyser

- [ ] Exécuter tous les tests
- [ ] Identifier les tests en échec
- [ ] Documenter les résultats

### Livrables
- Liste des tests créés avec leurs résultats (pass/fail)
- Screenshot du tableau de bord de qualité
- Analyse des échecs et recommandations

### Critères de validation
- ✅ Minimum 10 tests créés
- ✅ Au moins 1 test SQL custom
- ✅ Tests exécutés avec résultats documentés
- ✅ Tableau de bord de qualité consulté

---

## Exercice 4 : Gouvernance et Glossaire

### Objectif
Créer un glossaire métier, classifier les données sensibles et mettre en place la gouvernance.

### Contexte
L'entreprise doit se conformer au RGPD. Vous devez identifier et classifier les données personnelles, et créer un vocabulaire commun.

### Étapes

#### 4.1 Créer le glossaire

- [ ] Créer un glossaire **"E-Commerce"** avec les termes suivants :

| Terme | Définition | Synonymes |
|-------|------------|-----------|
| Client Actif | Client avec au moins une commande dans les 90 derniers jours | Active Customer |
| Client Churné | Client sans commande depuis plus de 365 jours | Churned Customer |
| Lifetime Value (LTV) | Somme totale des commandes d'un client | CLV, Valeur Vie Client |
| Panier Moyen | Montant moyen d'une commande | Average Order Value, AOV |
| Taux de Churn | Pourcentage de clients perdus sur une période | Churn Rate, Attrition |

#### 4.2 Lier les termes aux colonnes

- [ ] Associer **"Lifetime Value"** à `analytics.customer_metrics.lifetime_value`
- [ ] Associer **"Client Actif"** / **"Client Churné"** à `analytics.customer_metrics.segment`
- [ ] Associer **"Panier Moyen"** à `analytics.daily_sales.revenue`

#### 4.3 Classifier les données PII

- [ ] Identifier toutes les colonnes contenant des données personnelles
- [ ] Appliquer les tags PII appropriés :

| Table | Colonne | Classification |
|-------|---------|---------------|
| `raw.customers` | `email` | PII.Sensitive |
| `raw.customers` | `phone` | PII.Sensitive |
| `raw.customers` | `first_name` | PersonalData.Personal |
| `raw.customers` | `last_name` | PersonalData.Personal |
| `analytics.customer_metrics` | `full_name` | PersonalData.Personal |

#### 4.4 Assigner les owners et tiers

- [ ] Créer les équipes : `data-engineering`, `data-analytics`, `data-governance`
- [ ] Assigner les owners :
  - Tables `raw.*` → `data-engineering`
  - Tables `analytics.*` → `data-analytics`
- [ ] Assigner les tiers :
  - `raw.customers`, `raw.orders` → Tier 1
  - `analytics.*` → Tier 2
  - `raw.order_items`, `raw.products` → Tier 3

### Livrables
- Screenshot du glossaire avec les termes créés
- Liste des colonnes PII classifiées
- Screenshot montrant les owners et tiers assignés

### Critères de validation
- ✅ Glossaire avec 5+ termes
- ✅ Termes liés aux colonnes
- ✅ 5+ colonnes classifiées PII
- ✅ Owners assignés à toutes les tables
- ✅ Tiers assignés à toutes les tables

---

## Exercice 5 : Automatisation via l'API

### Objectif
Utiliser le SDK Python pour automatiser les tâches de gouvernance.

### Contexte
L'entreprise grandit et il n'est plus possible de gérer la documentation et la classification manuellement. Vous devez écrire des scripts d'automatisation.

### Étapes

#### 5.1 Setup

- [ ] Installer le SDK : `pip install openmetadata-ingestion`
- [ ] Créer un bot dans OpenMetadata et récupérer le JWT Token
- [ ] Écrire un script de connexion et vérifier le health check

#### 5.2 Script de rapport

- [ ] Écrire un script Python `rapport_gouvernance.py` qui génère :
  - Nombre total de tables
  - % de tables avec description
  - % de tables avec owner
  - % de tables avec tier
  - Liste des tables non conformes (sans description ET Tier 1-2)

**Output attendu :**

```
📊 Rapport de Gouvernance - 2024-01-16
══════════════════════════════════════
Tables totales          : 7
Avec description        : 5/7 (71.4%)
Avec owner             : 7/7 (100.0%)
Avec tier              : 7/7 (100.0%)

⚠️  Tables non conformes (Tier 1-2 sans description) :
  - demo-postgres.ecommerce.raw.order_items
  - demo-postgres.ecommerce.analytics.daily_sales
```

#### 5.3 Script de classification automatique

- [ ] Écrire un script `auto_classify.py` qui :
  - Parcourt toutes les tables
  - Détecte les colonnes PII par leur nom (`email`, `phone`, `name`, etc.)
  - Applique les tags PII appropriés
  - Affiche un résumé des classifications appliquées

#### 5.4 Script d'export

- [ ] Écrire un script `export_catalog.py` qui exporte en JSON :
  - Toutes les tables avec leurs métadonnées
  - Descriptions, owners, tags, colonnes
  - Résultats des tests de qualité

### Livrables
- 3 scripts Python fonctionnels :
  - `rapport_gouvernance.py`
  - `auto_classify.py`
  - `export_catalog.json` (résultat de l'export)
- Output de chaque script

### Critères de validation
- ✅ Scripts exécutables sans erreur
- ✅ Rapport de gouvernance avec métriques correctes
- ✅ Classification PII automatique fonctionnelle
- ✅ Export JSON complet et lisible

---

## Barème global

| Exercice | Points | Compétences évaluées |
|----------|--------|---------------------|
| Exercice 1 | /20 | Installation, configuration, ingestion de base |
| Exercice 2 | /20 | Multi-sources, profiling, lineage automatique |
| Exercice 3 | /20 | Tests de qualité, SQL custom, monitoring |
| Exercice 4 | /20 | Glossaire, classification PII, gouvernance |
| Exercice 5 | /20 | SDK Python, automatisation, scripting |
| **Total** | **/100** | |

### Bonus (jusqu'à +10 points)

- [ ] (+3) Configurer une alerte Slack ou webhook sur les échecs de tests
- [ ] (+3) Intégrer dbt avec le lineage des modèles
- [ ] (+2) Créer un test de qualité inter-tables (intégrité référentielle)
- [ ] (+2) Écrire un script qui génère un rapport Markdown du catalogue

---
