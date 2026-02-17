# Chapitre 7 : Glossaire Métier et Classification

## Table des matières

1. [Pourquoi un glossaire métier ?](#pourquoi-un-glossaire-métier)
2. [Créer un glossaire](#créer-un-glossaire)
3. [Termes, synonymes et relations](#termes-synonymes-et-relations)
4. [Classification des données sensibles](#classification-des-données-sensibles)
5. [Politiques de gouvernance](#politiques-de-gouvernance)
6. [Conformité RGPD](#conformité-rgpd)

---

## Pourquoi un glossaire métier ?

### Le problème du vocabulaire

Dans une organisation, les mêmes concepts sont souvent nommés différemment :

| Équipe | Comment ils appellent le "chiffre d'affaires" |
|--------|-----------------------------------------------|
| Finance | `revenue` |
| Commerce | `chiffre_affaires` |
| Marketing | `total_sales` |
| Data Engineering | `gmv` (Gross Merchandise Value) |
| Direction | "le CA" |

**Résultat** : 5 dashboards différents avec 5 chiffres différents pour le même KPI.

### Le glossaire résout ce problème

```
Glossaire métier
├── "Chiffre d'Affaires" (terme officiel)
│   ├── Définition : Somme des ventes HT sur une période
│   ├── Formule : SUM(order_items.quantity * order_items.unit_price)
│   ├── Synonymes : Revenue, CA, Total Sales, GMV
│   ├── Owner : Finance Team
│   └── Lié aux colonnes :
│       ├── fact_revenue.total_revenue
│       ├── analytics.daily_sales.revenue
│       └── reporting.monthly_kpis.ca_mensuel
```

---

## Créer un glossaire

### Via l'interface

1. Aller dans **Glossary** (menu latéral)
2. Cliquer **Add Glossary**
3. Remplir :

| Champ | Exemple |
|-------|---------|
| **Name** | `E-Commerce` |
| **Display Name** | `Glossaire E-Commerce` |
| **Description** | `Termes métier liés à l'activité e-commerce` |
| **Owner** | `data-governance` |
| **Reviewers** | `finance-team`, `product-team` |

### Structure recommandée

Organisez vos glossaires par domaine métier :

```
Glossaires
├── 📖 E-Commerce
│   ├── Clients
│   │   ├── Client Actif
│   │   ├── Client Churné
│   │   └── Lifetime Value (LTV)
│   ├── Commandes
│   │   ├── Panier Moyen
│   │   ├── Taux de Conversion
│   │   └── Taux d'Abandon
│   └── Produits
│       ├── SKU
│       ├── Stock Disponible
│       └── Rupture de Stock
│
├── 📖 Finance
│   ├── Chiffre d'Affaires
│   ├── Marge Brute
│   ├── EBITDA
│   └── Coût d'Acquisition Client (CAC)
│
└── 📖 Marketing
    ├── Impression
    ├── Click-Through Rate (CTR)
    ├── Coût Par Clic (CPC)
    └── Return On Ad Spend (ROAS)
```

---

## Termes, synonymes et relations

### Créer un terme

1. Ouvrir un glossaire → **Add Term**
2. Remplir :

| Champ | Exemple |
|-------|---------|
| **Name** | `churn-rate` |
| **Display Name** | `Taux de Churn` |
| **Description** | Pourcentage de clients perdus sur une période |
| **Synonymes** | Attrition Rate, Taux d'Attrition |
| **Related Terms** | Client Actif, Lifetime Value |
| **References** | Lien vers la doc interne |
| **Reviewers** | `product-manager` |
| **Tags** | `KPI`, `Finance` |

### Définition riche d'un terme

```markdown
## Taux de Churn

### Définition
Le taux de churn mesure le pourcentage de clients qui cessent d'utiliser
le service sur une période donnée.

### Formule
```
Churn Rate = (Clients perdus dans la période / Clients au début de la période) × 100
```

### Règles métier
- Un client est considéré "perdu" après 12 mois sans commande
- Calculé mensuellement sur une base glissante
- Exclut les comptes de test et les comptes internes

### Seuils
- 🟢 < 5% : Bon
- 🟡 5-10% : Attention
- 🔴 > 10% : Critique

### Tables associées
- `analytics.monthly_churn` (colonne: `churn_rate`)
- `reporting.executive_dashboard` (KPI: "Churn mensuel")
```

### Types de relations entre termes

| Relation | Description | Exemple |
|----------|-------------|---------|
| **Synonyme** | Même concept, nom différent | Churn Rate ↔ Taux d'Attrition |
| **Related To** | Concepts liés | Churn Rate ↔ Retention Rate |
| **Parent/Child** | Hiérarchie | KPIs → KPIs Clients → Churn Rate |
| **Has A** | Composition | Commande has a Ligne de commande |
| **Is A** | Spécialisation | Client Premium is a Client |

### Lier un terme à une colonne

1. Ouvrir une table dans **Explore**
2. Sur la colonne concernée, cliquer **+ Tag**
3. Sélectionner **Glossary Term**
4. Rechercher et sélectionner le terme

Cela crée un lien bidirectionnel :
- La colonne affiche le terme de glossaire
- Le terme de glossaire liste toutes les colonnes associées

---

## Classification des données sensibles

### Catégories de données sensibles

| Classification | Description | Exemples |
|---------------|-------------|----------|
| **PII** (Personal Identifiable Information) | Données identifiant une personne | Nom, email, téléphone, adresse |
| **PHI** (Protected Health Information) | Données de santé | Dossier médical, allergies |
| **PCI** (Payment Card Industry) | Données de paiement | Numéro de carte, CVV |
| **Confidentiel** | Données internes sensibles | Salaires, stratégie, contrats |
| **Public** | Données ouvertes | Catalogue produits, prix publics |

### Classifications dans OpenMetadata

OpenMetadata fournit des classifications pré-configurées :

```
Classifications
├── PersonalData
│   ├── Personal          → Nom, prénom, date de naissance
│   ├── Sensitive         → Numéro sécu, passeport
│   └── SpecialCategory   → Origine ethnique, opinions politiques, santé
│
├── PII
│   ├── Sensitive         → Email, téléphone, adresse
│   └── NonSensitive      → Ville, code postal
│
└── Custom
    ├── Confidentiel      → Données internes sensibles
    ├── Interne           → Usage interne uniquement
    └── Public            → Données publiques
```

### Appliquer une classification

**Via l'UI** :
1. Ouvrir la table → Onglet **Schema**
2. Sur la colonne `email` → Cliquer **+ Tag**
3. Sélectionner `PII.Sensitive`

**Via l'API** :

```python
# Classifier automatiquement les colonnes PII
pii_patterns = {
    "email": "PII.Sensitive",
    "phone": "PII.Sensitive",
    "address": "PII.Sensitive",
    "first_name": "PersonalData.Personal",
    "last_name": "PersonalData.Personal",
    "ssn": "PersonalData.Sensitive",
    "credit_card": "PCI.CardNumber",
    "ip_address": "PII.NonSensitive",
}

for column_name, tag_fqn in pii_patterns.items():
    # Rechercher les colonnes matchant le pattern
    response = requests.get(
        f"{API_URL}/search/query?q=column:{column_name}&index=table_search_index",
        headers=headers
    )
    # Appliquer le tag à chaque colonne trouvée
    for hit in response.json().get("hits", {}).get("hits", []):
        table_fqn = hit["_source"]["fullyQualifiedName"]
        # ... appliquer le tag via PATCH
```

### Auto-classification

OpenMetadata peut **auto-classifier** les colonnes basé sur :
- **Nom de la colonne** : `email`, `phone`, `ssn` → PII
- **Pattern des données** : Format email, numéro de téléphone → PII
- **Échantillonnage** : Analyse des valeurs pour détecter les patterns

---

## Politiques de gouvernance

### Définir des politiques

| Politique | Règle | Action |
|-----------|-------|--------|
| PII Protection | Toute colonne PII doit avoir un owner | Alerte si non conforme |
| Data Quality | Les tables Tier 1 doivent avoir des tests | Alerte hebdomadaire |
| Documentation | Les tables Tier 1-2 doivent être documentées | Tâche assignée |
| Freshness | Les tables Tier 1 doivent être mises à jour quotidiennement | Alerte si > 24h |
| Access Control | Les données PII ne sont accessibles qu'aux owners | Restriction d'accès |

### Workflow de gouvernance

```
1. Classification automatique
   ↓
2. Revue par le Data Steward
   ↓
3. Application des politiques
   ↓
4. Monitoring continu
   ↓
5. Alertes et remédiation
```

### Rôles de gouvernance

| Rôle | Responsabilité | Dans OpenMetadata |
|------|---------------|-------------------|
| **Data Owner** | Responsable de la qualité et de la documentation | Owner de la table |
| **Data Steward** | Définit les standards et les politiques | Reviewer du glossaire |
| **Data Governor** | Vision globale, conformité | Admin OpenMetadata |
| **Data Consumer** | Utilise les données | Viewer |

---

## Conformité RGPD

### RGPD et data catalog

Le RGPD (Règlement Général sur la Protection des Données) impose :

| Exigence RGPD | Comment OpenMetadata aide |
|---------------|---------------------------|
| **Registre des traitements** | Inventaire de toutes les tables avec PII |
| **Droit d'accès** | Lineage montre où sont stockées les données d'un individu |
| **Droit à l'effacement** | Lineage identifie toutes les tables à purger |
| **Minimisation des données** | Classification PII identifie les données excessives |
| **Limitation de la conservation** | Tags de rétention + alertes de fraîcheur |
| **Responsabilité** | Ownership et audit trail |

### Inventaire RGPD avec OpenMetadata

```python
# Lister toutes les tables contenant des données PII
response = requests.get(
    f"{API_URL}/search/query",
    params={
        "q": "*",
        "index": "table_search_index",
        "query_filter": '{"query":{"bool":{"must":[{"term":{"tags.tagFQN":"PII.Sensitive"}}]}}}',
        "size": 100
    },
    headers=headers
)

pii_tables = response.json()["hits"]["hits"]
for table in pii_tables:
    print(f"Table: {table['_source']['fullyQualifiedName']}")
    print(f"Owner: {table['_source'].get('owner', {}).get('name', 'NON ASSIGNÉ')}")
    print(f"Colonnes PII: ...")
    print("---")
```

### Rapport de conformité

```
📋 Rapport RGPD - OpenMetadata
══════════════════════════════
Date : 2024-01-16

Tables avec données PII : 23
├── Avec owner assigné : 21 ✅
├── Sans owner : 2 ❌  → raw.legacy_users, tmp.export_clients
│
Colonnes PII identifiées : 67
├── Classifiées : 62 ✅
├── Non classifiées : 5 ❌  → À classifier
│
Lineage PII complet : 18/23 tables ✅
├── Lineage manquant : 5 tables ⚠️
│
Documentation PII : 19/23 tables ✅
├── Non documentées : 4 tables ⚠️
```

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| Glossaire | Vocabulaire métier standardisé et partagé |
| Termes | Définition, synonymes, formules, relations |
| Classification | PII, PHI, PCI, Confidentiel, Public |
| Auto-classification | Détection automatique basée sur noms et patterns |
| Gouvernance | Politiques, rôles, workflow |
| RGPD | Inventaire PII, lineage, droit à l'effacement |

---

> **Prochain chapitre** : [Collaboration et Alertes](08-collaboration-alertes.md) - Travailler en équipe autour de vos données
