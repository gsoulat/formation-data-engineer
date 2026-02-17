# Module 03a - Modélisation dimensionnelle : les fondamentaux

> **Question business :** Le directeur vous demande "quel est le CA par produit, par région, par mois ?". Pour répondre, il faut structurer les données. Mais comment organiser des millions de transactions pour que cette requête soit simple et rapide ? La réponse : le Star Schema.

---

## Avant de commencer : l'analogie du ticket de caisse

<!-- 🔴 IMAGE : Un vrai ticket de caisse annoté avec des flèches colorées -->
<!-- 🟢 PROMPT IMAGE : "Photo réaliste d'un ticket de caisse de supermarché français (Carrefour ou Leclerc) avec des annotations colorées superposées en flat design. Des flèches pointent vers : la date → label bleu 'DIM_DATE', le nom du magasin → label orange 'DIM_MAGASIN', chaque produit → label vert 'DIM_PRODUIT', le total et les quantités → label rouge 'MESURES (table de faits)', le numéro de carte fidélité → label violet 'DIM_CLIENT'. En bas du ticket, un encadré : 'Ce ticket = 1 ligne dans FACT_VENTES'. Format portrait, haute résolution." -->

<!-- 🔴 VIDÉO : Animation "Du ticket de caisse au Star Schema" -->
<!-- 🟢 PROMPT VIDÉO : "Animation motion design de 60 secondes. Scène 1 (15s) : un ticket de caisse apparaît, on zoome sur chaque élément (date, magasin, produits, montant, client). Scène 2 (20s) : chaque élément se détache et vole vers une boîte colorée (DIM_DATE, DIM_MAGASIN, DIM_PRODUIT, DIM_CLIENT). Les montants restent au centre dans FACT_VENTES. Scène 3 (15s) : les boîtes se positionnent en étoile autour de FACT_VENTES, des lignes de connexion apparaissent → c'est un Star Schema ! Scène 4 (10s) : le ticket se multiplie en milliers de tickets, tous connectés au même schéma. Texte : 'Un Star Schema = des millions de tickets de caisse organisés'. Style flat design, couleurs vives." -->

Prenez un **ticket de caisse** de supermarché. Vous y trouvez :

- **Les chiffres** (ce qu'on mesure) : prix total, quantité, remise → ce sont les **mesures** d'une **table de faits**
- **Le contexte** (qui, quoi, quand, où) :
  - **Quand ?** → la date et l'heure → `DIM_DATE`
  - **Où ?** → le magasin, la ville → `DIM_MAGASIN`
  - **Quoi ?** → les produits achetés → `DIM_PRODUIT`
  - **Qui ?** → le client (carte fidélité) → `DIM_CLIENT`
  - **Comment ?** → CB, espèces, chèque → `DIM_PAIEMENT`

Le ticket de caisse EST un fait. Les informations autour sont les dimensions. **Un Star Schema, c'est un ticket de caisse généralisé à des millions de transactions.**

```
          DIM_DATE
              │
DIM_MAGASIN ──┼── DIM_PRODUIT
              │
         FAIT_VENTE          (le ticket de caisse)
         (montant,
          quantité,          (les chiffres)
          remise)
              │
DIM_CLIENT ───┼── DIM_PAIEMENT
```

---

## Tables de faits (Fact Tables)

Les tables de faits contiennent les **mesures quantitatives** du business :
- Montants
- Quantités
- Comptages
- Ratios

![Tables de Faits vs Dimensions](./images/03/fact-vs-dimension.png)

### Types de mesures

Pour savoir comment agréger une mesure, il faut connaître son type :

| Type | Description | Exemple concret | Agrégation |
|------|-------------|-----------------|------------|
| **Additive** | Peut être sommée sur toutes dimensions | Revenue, Quantity | SUM() partout |
| **Semi-additive** | Sommable sur certaines dimensions | Solde de compte bancaire | SUM() sauf sur le temps (on prend le dernier) |
| **Non-additive** | Ne peut pas être sommée | Prix unitaire, pourcentage | AVG(), ou dernière valeur |

**Exemple concret :** Vous avez 3 magasins. Chacun a vendu 100€ aujourd'hui.
- Le CA total = 100 + 100 + 100 = **300€** (additive, on peut sommer)
- Le prix unitaire moyen d'un produit = 15€ dans chaque magasin. Le prix unitaire total N'EST PAS 45€ ! (non-additive)
- Le stock en fin de journée = 50 unités par magasin. Le stock total = 150 (additive sur les magasins), mais le stock "total sur la semaine" n'est pas la somme des stocks de chaque jour (semi-additive)

---

## Tables de dimensions (Dimension Tables)

Les dimensions fournissent le **contexte descriptif** — elles répondent aux questions : Qui ? Quoi ? Quand ? Où ? Comment ?

```
┌────────────────────────────────────────┐
│           DIM_CUSTOMER                  │
├────────────────────────────────────────┤
│ customer_key     (PK, Surrogate)       │
│ customer_id      (Natural Key)         │
├────────────────────────────────────────┤
│ first_name                             │
│ last_name                              │
│ email                                  │
│ birth_date                             │
│ gender                                 │
│ segment          (Gold, Silver, Bronze)│
│ acquisition_date                       │
│ region                                 │
│ country                                │
└────────────────────────────────────────┘
```

### Clés surrogate vs naturelles

| Type | Description | Exemple | Analogie |
|------|-------------|---------|----------|
| **Natural Key** | Clé business originale | `customer_id = "C12345"` | Votre numéro de sécu |
| **Surrogate Key** | Clé technique générée | `customer_key = 42` | Votre numéro de dossier interne à l'hôpital |

**Pourquoi des surrogate keys ?**
- **Performance** : un entier (4 octets) est plus rapide à joindre qu'un VARCHAR
- **Indépendance** : si le système source change ses identifiants, vos jointures ne cassent pas
- **Historique** : un même client peut avoir plusieurs lignes (SCD Type 2) avec des surrogate keys différentes

---

## Schéma en étoile (Star Schema)

Le pattern **le plus utilisé** pour le Data Warehouse. Le nom vient de sa forme : une table de faits centrale entourée de dimensions, comme une étoile.

![Star Schema](./images/02/star-schema.png)

### Pourquoi le Star Schema est-il si populaire ?

1. **Simple à comprendre** : un analyste peut lire le modèle sans documentation
2. **Performant** : peu de jointures (1 JOIN par dimension)
3. **Compatible BI** : tous les outils (Power BI, Tableau, Looker) l'attendent
4. **SQL lisible** : les requêtes s'écrivent naturellement

### Requête typique Star Schema

```sql
-- "Quel est le CA par trimestre, catégorie et segment client en 2024 ?"
SELECT
    d.year,
    d.quarter,
    p.category,
    c.segment,
    SUM(f.amount) as total_sales,
    COUNT(*) as transaction_count
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE d.year = 2024
GROUP BY d.year, d.quarter, p.category, c.segment
ORDER BY total_sales DESC;
```

Remarquez : la requête est **lisible** même sans connaître le modèle. `fact_sales JOIN dim_date JOIN dim_product JOIN dim_customer` se lit comme une phrase.

---

## Schéma en flocon (Snowflake Schema)

Le Snowflake est un Star Schema dont les **dimensions sont normalisées** : on extrait les hiérarchies en sous-tables.

![Snowflake Schema](./images/03/snowflake-schema.png)

### Exemple concret : la dimension Cinema

```
Star Schema (dénormalisé) :          Snowflake (normalisé) :

┌──────────────────┐                ┌──────────────┐
│   DIM_CINEMA     │                │  DIM_REGION  │
├──────────────────┤                ├──────────────┤
│ cinema_key       │                │ region_key   │◄──┐
│ nom              │                │ nom_region   │   │
│ ville       ─────┼── redondant   └──────────────┘   │
│ region      ─────┤   si 5 cinémas                    │
│ pays        ─────┤   dans la même                    │
│ directeur        │   région      ┌──────────────┐   │
└──────────────────┘                │  DIM_CINEMA  │   │
                                    ├──────────────┤   │
                                    │ cinema_key   │   │
                                    │ nom          │   │
                                    │ ville        │   │
                                    │ region_key FK│───┘
                                    │ directeur    │
                                    └──────────────┘
```

### Quand choisir Star vs Snowflake ?

| Aspect | Star | Snowflake |
|--------|------|-----------|
| **Complexité** | Simple | Plus complexe |
| **Performance** | Meilleure (moins de JOINs) | Plus de JOINs |
| **Stockage** | Plus d'espace (redondance) | Moins de redondance |
| **Maintenance** | Plus simple | Plus structuré |
| **Recommandé** | Par défaut, 90% des cas | Très grandes dimensions avec hiérarchies profondes |

**Règle : commencez toujours par un Star Schema.** Passez au Snowflake uniquement si une dimension dépasse les 100 colonnes ou si la redondance pose un vrai problème de stockage.

---

## Dimension Date

La dimension **incontournable** de tout Data Warehouse. Elle est pré-générée pour plusieurs années et contient des attributs qu'on ne peut pas calculer facilement (vacances scolaires, jours fériés, année fiscale).

```sql
CREATE TABLE dim_date (
    date_key        INT PRIMARY KEY,      -- 20240215
    date            DATE NOT NULL,        -- 2024-02-15
    day             INT NOT NULL,         -- 15
    day_name        VARCHAR(10),          -- "Thursday"
    day_of_week     INT,                  -- 4
    day_of_year     INT,                  -- 46
    week_of_year    INT,                  -- 7
    month           INT,                  -- 2
    month_name      VARCHAR(10),          -- "February"
    quarter         INT,                  -- 1
    year            INT,                  -- 2024
    is_weekend      BOOLEAN,              -- false
    is_holiday      BOOLEAN,              -- false
    holiday_name    VARCHAR(50),          -- NULL
    fiscal_year     INT,                  -- 2024
    fiscal_quarter  INT                   -- 4
);
```

**Pourquoi ne pas juste utiliser une colonne DATE dans la table de faits ?**
Parce que des requêtes comme "CA les jours fériés vs jours normaux" ou "CA pendant les vacances scolaires" seraient impossibles sans ces attributs pré-calculés.

---

## Bonnes pratiques

### DO

- Utiliser des surrogate keys (entiers) dans les tables de faits
- Préférer le Star Schema au Snowflake par défaut
- Créer une dimension Date complète avec jours fériés, vacances, etc.
- Nommer clairement : `dim_*` pour les dimensions, `fact_*` pour les faits, `_key` pour les surrogate keys, `_id` pour les natural keys

### DON'T

- Mettre des mesures dans les dimensions (le CA n'a rien à faire dans DIM_CLIENT)
- Créer des tables de faits sans dimensions (un fait sans contexte est inutile)
- Utiliser des clés composites complexes dans les faits
- Négliger la qualité des données sources

---

## Points clés à retenir

- **Faits** = mesures quantitatives (SUM, COUNT, AVG)
- **Dimensions** = contexte descriptif (WHO, WHAT, WHERE, WHEN)
- 3 types de mesures : **additive**, **semi-additive**, **non-additive**
- **Star Schema** = simple, performant, recommandé dans 90% des cas
- **Snowflake** = dimensions normalisées, plus complexe, pour les cas spécifiques
- **Surrogate keys** = clés techniques (entiers) pour la performance et l'indépendance
- **Dimension Date** = pré-générée, incontournable

---

**Prochain module :** [03b - Modélisation avancée (SCD, Factless Facts, Data Vault)](./03b-modelisation-avancee.md)

[Module précédent](./02-oltp-vs-olap.md) | [Retour au sommaire](./README.md)
