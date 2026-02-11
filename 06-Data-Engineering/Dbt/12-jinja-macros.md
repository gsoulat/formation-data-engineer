# Chapitre 12 : Jinja et Macros dans dbt

## Objectifs

- Comprendre le moteur de templating **Jinja2** utilise par dbt
- Maitriser la syntaxe Jinja : expressions, instructions, commentaires
- Utiliser les **filtres**, **tests** et **structures de controle** Jinja
- Creer des **macros** reutilisables pour eviter la duplication SQL
- Developper des macros avancees : generiques, dynamiques, recursives
- Organiser et documenter un projet de macros professionnel

## Jinja2 : le moteur de templating de dbt

### Qu'est-ce que Jinja ?

**Jinja2** est un moteur de templating Python. dbt l'utilise pour transformer vos fichiers `.sql` en SQL pur avant de les envoyer a la base de donnees.

```
Votre modele (.sql)          dbt compile           SQL final
+---------------------+     +----------+     +-------------------+
| SELECT *            |     |          |     | SELECT *          |
| FROM {{ ref(       |---->|  Jinja   |---->| FROM schema.table |
|   'my_model'        |     |  Engine  |     | WHERE date >=     |
| ) }}                |     |          |     |   '2024-01-01'    |
| WHERE date >=       |     +----------+     +-------------------+
|  '{{ var("start") }}'|                       Envoye a la BDD
+---------------------+
```

### Les 3 delimiteurs Jinja

| Delimiteur | Usage | Exemple |
|------------|-------|---------|
| `{{ ... }}` | **Expressions** : afficher une valeur | `{{ ref('orders') }}` |
| `{% ... %}` | **Instructions** : logique (if, for, set) | `{% if is_incremental() %}` |
| `{# ... #}` | **Commentaires** : ignores a la compilation | `{# Ceci est un commentaire #}` |

```sql
{# Commentaire : ce modele calcule le CA mensuel #}
{% set start = var("start_date", "2024-01-01") %}

SELECT
    date_trunc('month', order_date) AS mois,
    SUM(amount) AS chiffre_affaires
FROM {{ ref('orders') }}
WHERE order_date >= '{{ start }}'
GROUP BY 1
```

**Apres compilation (`dbt compile`) :**
```sql
SELECT
    date_trunc('month', order_date) AS mois,
    SUM(amount) AS chiffre_affaires
FROM analytics.orders
WHERE order_date >= '2024-01-01'
GROUP BY 1
```

## Syntaxe Jinja dans dbt

### Variables avec `{% set %}`

`set` permet de definir des variables locales dans un modele ou une macro.

```sql
{# Variable simple #}
{% set my_table = 'orders' %}
{% set max_price = 500 %}

SELECT * FROM {{ my_table }} WHERE price <= {{ max_price }}

{# Variable avec du SQL #}
{% set payment_methods = ['credit_card', 'bank_transfer', 'paypal'] %}

{# Variable multi-ligne (bloc set) #}
{% set my_query %}
    SELECT DISTINCT status FROM {{ ref('orders') }}
{% endset %}
```

### Structures conditionnelles : `{% if %}`

```sql
SELECT
    order_id,
    amount,
    status
FROM {{ ref('orders') }}

{% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}

{% if var("environment", "dev") == "dev" %}
    LIMIT 1000
{% elif var("environment") == "staging" %}
    LIMIT 100000
{% else %}
    {# Production : pas de limite #}
{% endif %}
```

### Operateurs de comparaison et logique

| Operateur | Description | Exemple |
|-----------|-------------|---------|
| `==` | Egal | `{% if status == 'active' %}` |
| `!=` | Different | `{% if env != 'prod' %}` |
| `>`, `<`, `>=`, `<=` | Comparaison | `{% if count > 100 %}` |
| `and` | ET logique | `{% if a > 0 and b > 0 %}` |
| `or` | OU logique | `{% if env == 'dev' or env == 'staging' %}` |
| `not` | Negation | `{% if not is_incremental() %}` |
| `in` | Appartenance | `{% if col in columns %}` |
| `is` | Test d'identite | `{% if value is none %}` |

### Boucles : `{% for %}`

Les boucles sont extremement puissantes pour generer du SQL dynamique.

```sql
{# Boucle simple : generer des colonnes #}
{% set payment_methods = ['credit_card', 'bank_transfer', 'paypal'] %}

SELECT
    order_id,
    {% for method in payment_methods %}
        SUM(CASE WHEN payment_method = '{{ method }}' THEN amount ELSE 0 END)
            AS {{ method }}_total
        {% if not loop.last %},{% endif %}
    {% endfor %}
FROM {{ ref('payments') }}
GROUP BY 1
```

**Resultat compile :**
```sql
SELECT
    order_id,
    SUM(CASE WHEN payment_method = 'credit_card' THEN amount ELSE 0 END)
        AS credit_card_total,
    SUM(CASE WHEN payment_method = 'bank_transfer' THEN amount ELSE 0 END)
        AS bank_transfer_total,
    SUM(CASE WHEN payment_method = 'paypal' THEN amount ELSE 0 END)
        AS paypal_total
FROM analytics.payments
GROUP BY 1
```

### La variable `loop` dans les boucles

| Attribut | Description | Exemple |
|----------|-------------|---------|
| `loop.index` | Iteration courante (commence a 1) | `{{ loop.index }}` |
| `loop.index0` | Iteration courante (commence a 0) | `{{ loop.index0 }}` |
| `loop.first` | `true` si premiere iteration | `{% if loop.first %}` |
| `loop.last` | `true` si derniere iteration | `{% if not loop.last %},{% endif %}` |
| `loop.length` | Nombre total d'iterations | `{{ loop.length }}` |
| `loop.revindex` | Iterations restantes (depuis la fin) | `{{ loop.revindex }}` |

```sql
{% set columns = ['name', 'email', 'phone', 'city'] %}

SELECT
    id,
    {% for col in columns %}
        COALESCE({{ col }}, 'N/A') AS {{ col }}_clean
        {%- if not loop.last -%},{%- endif %}
    {% endfor %}
FROM {{ ref('raw_customers') }}
```

### Controle des espaces : `-`

Le tiret `-` dans les delimiteurs supprime les espaces/sauts de ligne autour du tag.

```sql
{# SANS controle des espaces (espaces generes) #}
{% for col in columns %}
    {{ col }}
{% endfor %}

{# AVEC controle des espaces (compact) #}
{%- for col in columns -%}
    {{ col }}
{%- endfor -%}
```

| Syntaxe | Effet |
|---------|-------|
| `{% ... %}` | Conserve les espaces autour |
| `{%- ... %}` | Supprime les espaces AVANT |
| `{% ... -%}` | Supprime les espaces APRES |
| `{%- ... -%}` | Supprime les espaces des DEUX cotes |

**Regle pratique :** Utilisez `{%- ... -%}` dans les boucles pour eviter les lignes vides dans le SQL compile.

## Filtres Jinja

Les filtres transforment une valeur. Ils s'appliquent avec le pipe `|`.

### Filtres les plus utiles dans dbt

| Filtre | Description | Exemple | Resultat |
|--------|-------------|---------|----------|
| `upper` | Majuscules | `{{ 'hello' \| upper }}` | `HELLO` |
| `lower` | Minuscules | `{{ 'HELLO' \| lower }}` | `hello` |
| `trim` | Supprimer espaces | `{{ '  hi  ' \| trim }}` | `hi` |
| `replace` | Remplacer | `{{ 'a-b' \| replace('-', '_') }}` | `a_b` |
| `default` | Valeur par defaut | `{{ x \| default('N/A') }}` | `N/A` si x est indefini |
| `string` | Convertir en string | `{{ 42 \| string }}` | `'42'` |
| `int` | Convertir en entier | `{{ '42' \| int }}` | `42` |
| `float` | Convertir en float | `{{ '3.14' \| float }}` | `3.14` |
| `length` | Longueur | `{{ list \| length }}` | Nombre d'elements |
| `join` | Joindre une liste | `{{ ['a','b'] \| join(', ') }}` | `a, b` |
| `first` | Premier element | `{{ list \| first }}` | Premier element |
| `last` | Dernier element | `{{ list \| last }}` | Dernier element |
| `sort` | Trier | `{{ list \| sort }}` | Liste triee |
| `unique` | Dedupliquer | `{{ list \| unique \| list }}` | Sans doublons |

### Exemples concrets

```sql
{# Joindre une liste en SQL IN clause #}
{% set countries = ['FR', 'ES', 'IT'] %}
SELECT * FROM customers
WHERE country IN ('{{ countries | join("', '") }}')
-- Resultat : WHERE country IN ('FR', 'ES', 'IT')

{# Generer des noms de colonnes propres #}
{% set raw_name = "Montant Total TTC" %}
{% set clean_name = raw_name | lower | replace(' ', '_') %}
SELECT amount AS {{ clean_name }}
-- Resultat : SELECT amount AS montant_total_ttc

{# Valeur par defaut avec filtre #}
{% set schema = var("target_schema") | default("public") %}
```

## Tests Jinja (is)

Les tests Jinja permettent de verifier des conditions sur les valeurs.

| Test | Description | Exemple |
|------|-------------|---------|
| `defined` | Variable definie | `{% if x is defined %}` |
| `none` | Valeur est None | `{% if x is none %}` |
| `string` | Est une chaine | `{% if x is string %}` |
| `number` | Est un nombre | `{% if x is number %}` |
| `iterable` | Est iterable (liste) | `{% if x is iterable %}` |
| `mapping` | Est un dictionnaire | `{% if x is mapping %}` |

```sql
{% set value = var("filter_value", none) %}

{% if value is not none %}
    {% if value is iterable and value is not string %}
        WHERE col IN ('{{ value | join("', '") }}')
    {% elif value is number %}
        WHERE col = {{ value }}
    {% else %}
        WHERE col = '{{ value }}'
    {% endif %}
{% endif %}
```

## Les Macros dbt

### Qu'est-ce qu'une macro ?

Une macro est une **fonction reutilisable** ecrite en Jinja + SQL. Elle se place dans le dossier `macros/` du projet dbt.

```
Analogy :
Python   -->  def ma_fonction():       -->  appel : ma_fonction()
dbt/Jinja -->  {% macro ma_macro() %}  -->  appel : {{ ma_macro() }}
```

### Anatomie d'une macro

```sql
{# macros/cents_to_euros.sql #}

{% macro cents_to_euros(column_name, precision=2) %}
    ROUND({{ column_name }} / 100.0, {{ precision }})
{% endmacro %}
```

**Utilisation dans un modele :**
```sql
SELECT
    order_id,
    {{ cents_to_euros('amount_cents') }} AS amount_euros,
    {{ cents_to_euros('tax_cents', 4) }} AS tax_euros
FROM {{ ref('raw_orders') }}
```

**SQL compile :**
```sql
SELECT
    order_id,
    ROUND(amount_cents / 100.0, 2) AS amount_euros,
    ROUND(tax_cents / 100.0, 4) AS tax_euros
FROM analytics.raw_orders
```

### Macro avec valeur par defaut et logique

```sql
{# macros/safe_divide.sql #}

{% macro safe_divide(numerator, denominator, default_value=0) %}
    CASE
        WHEN {{ denominator }} = 0 OR {{ denominator }} IS NULL
        THEN {{ default_value }}
        ELSE {{ numerator }}::FLOAT / {{ denominator }}
    END
{% endmacro %}
```

```sql
{# Utilisation #}
SELECT
    product_id,
    {{ safe_divide('total_revenue', 'total_orders') }} AS avg_order_value,
    {{ safe_divide('returns', 'total_orders', 'NULL') }} AS return_rate
FROM {{ ref('product_metrics') }}
```

### Macro qui retourne une valeur avec `return`

```sql
{# macros/get_custom_schema.sql #}

{% macro generate_schema_name(custom_schema_name, node) %}
    {% set default_schema = target.schema %}

    {% if custom_schema_name is none %}
        {{ default_schema }}
    {% elif target.name == 'prod' %}
        {{ custom_schema_name | trim }}
    {% else %}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {% endif %}
{% endmacro %}
```

## Macros pratiques courantes

### 1. Generateur de surrogate key

```sql
{# macros/generate_surrogate_key.sql #}

{% macro generate_surrogate_key(columns) %}
    MD5(
        {%- for column in columns -%}
            COALESCE(CAST({{ column }} AS VARCHAR), '_null_')
            {%- if not loop.last -%} || '-' || {%- endif -%}
        {%- endfor -%}
    )
{% endmacro %}
```

```sql
{# Utilisation #}
SELECT
    {{ generate_surrogate_key(['customer_id', 'order_date']) }} AS sk_order,
    customer_id,
    order_date,
    amount
FROM {{ ref('raw_orders') }}
```

### 2. Pivot dynamique

```sql
{# macros/pivot.sql #}

{% macro pivot(column, values, alias=true, agg='SUM', then_value=1, else_value=0, prefix='', suffix='') %}
    {%- for value in values %}
        {{ agg }}(
            CASE
                WHEN {{ column }} = '{{ value }}'
                THEN {{ then_value }}
                ELSE {{ else_value }}
            END
        )
        {% if alias %}
            AS {{ prefix }}{{ value | lower | replace(' ', '_') | replace('-', '_') }}{{ suffix }}
        {% endif %}
        {%- if not loop.last -%},{%- endif -%}
    {%- endfor %}
{% endmacro %}
```

```sql
{# Utilisation #}
SELECT
    customer_id,
    {{ pivot(
        column='payment_method',
        values=['credit_card', 'bank_transfer', 'paypal'],
        agg='SUM',
        then_value='amount',
        else_value='0',
        suffix='_total'
    ) }}
FROM {{ ref('payments') }}
GROUP BY 1
```

**Resultat compile :**
```sql
SELECT
    customer_id,
    SUM(CASE WHEN payment_method = 'credit_card' THEN amount ELSE 0 END) AS credit_card_total,
    SUM(CASE WHEN payment_method = 'bank_transfer' THEN amount ELSE 0 END) AS bank_transfer_total,
    SUM(CASE WHEN payment_method = 'paypal' THEN amount ELSE 0 END) AS paypal_total
FROM analytics.payments
GROUP BY 1
```

### 3. Generateur de clause WHERE dynamique

```sql
{# macros/build_where_clause.sql #}

{% macro build_where_clause(filters) %}
    {# filters : dictionnaire {colonne: valeur} #}
    {# Les valeurs None sont ignorees #}

    {% set conditions = [] %}

    {% for column, value in filters.items() %}
        {% if value is not none %}
            {% if value is iterable and value is not string %}
                {% do conditions.append(column ~ " IN ('" ~ value | join("', '") ~ "')") %}
            {% elif value is number %}
                {% do conditions.append(column ~ " = " ~ value | string) %}
            {% else %}
                {% do conditions.append(column ~ " = '" ~ value ~ "'") %}
            {% endif %}
        {% endif %}
    {% endfor %}

    {% if conditions | length > 0 %}
        WHERE {{ conditions | join(' AND ') }}
    {% endif %}
{% endmacro %}
```

```sql
{# Utilisation #}
SELECT *
FROM {{ ref('listings') }}
{{ build_where_clause({
    'city': var('city', none),
    'status': var('status', 'active'),
    'property_type': var('property_types', none)
}) }}
```

### 4. Macro de logging et debug

```sql
{# macros/log_model_info.sql #}

{% macro log_model_info() %}
    {% if execute %}
        {% set model_name = this.name %}
        {% set schema_name = this.schema %}
        {% set target_name = target.name %}

        {{ log("=" * 60, info=true) }}
        {{ log("Modele     : " ~ model_name, info=true) }}
        {{ log("Schema     : " ~ schema_name, info=true) }}
        {{ log("Target     : " ~ target_name, info=true) }}
        {{ log("Timestamp  : " ~ modules.datetime.datetime.now(), info=true) }}
        {{ log("=" * 60, info=true) }}
    {% endif %}
{% endmacro %}
```

```sql
{# Utilisation dans un modele #}
{{ log_model_info() }}

SELECT * FROM {{ ref('orders') }}
```

### 5. Union de tables par pattern

```sql
{# macros/union_tables.sql #}

{% macro union_tables(schema, table_prefix, exclude=[]) %}
    {# Genere un UNION ALL de toutes les tables commencant par table_prefix #}

    {% set tables = dbt_utils.get_relations_by_prefix(
        schema=schema,
        prefix=table_prefix,
        exclude=exclude
    ) %}

    {% set query %}
        {%- for table in tables %}
            SELECT
                '{{ table.identifier }}' AS _source_table,
                *
            FROM {{ table }}
            {%- if not loop.last %} UNION ALL {% endif -%}
        {%- endfor %}
    {% endset %}

    {{ return(query) }}
{% endmacro %}
```

## Macros avec requetes SQL (statement + run_query)

### Executer une requete et utiliser le resultat

```sql
{# macros/get_column_values.sql #}

{% macro get_column_values(table, column) %}
    {% set query %}
        SELECT DISTINCT {{ column }}
        FROM {{ table }}
        WHERE {{ column }} IS NOT NULL
        ORDER BY 1
    {% endset %}

    {% set results = run_query(query) %}

    {% if execute %}
        {% set values = results.columns[0].values() %}
        {{ return(values) }}
    {% else %}
        {{ return([]) }}
    {% endif %}
{% endmacro %}
```

```sql
{# Utilisation : pivot dynamique base sur les donnees reelles #}
{% set statuses = get_column_values(ref('orders'), 'status') %}

SELECT
    customer_id,
    {{ pivot(
        column='status',
        values=statuses,
        agg='COUNT',
        then_value='1',
        prefix='nb_'
    ) }}
FROM {{ ref('orders') }}
GROUP BY 1
```

### La variable `execute`

**Important :** `execute` est `false` pendant le parsing et `true` pendant l'execution. Les requetes SQL (`run_query`) ne fonctionnent que quand `execute` est `true`.

```sql
{% if execute %}
    {# Ce bloc s'execute uniquement a l'execution, pas au parsing #}
    {% set result = run_query("SELECT COUNT(*) FROM " ~ ref('orders')) %}
    {% set row_count = result.columns[0].values()[0] %}
    {{ log("Nombre de lignes: " ~ row_count, info=true) }}
{% endif %}
```

## Macros dbt natives a connaitre

dbt fournit des macros internes que vous utilisez deja :

| Macro | Usage | Exemple |
|-------|-------|---------|
| `ref()` | Reference un modele dbt | `{{ ref('orders') }}` |
| `source()` | Reference une source | `{{ source('raw', 'orders') }}` |
| `config()` | Configure le modele | `{{ config(materialized='table') }}` |
| `var()` | Lire une variable | `{{ var('start_date') }}` |
| `env_var()` | Lire une variable d'environnement | `{{ env_var('DB_PASSWORD') }}` |
| `this` | Reference le modele courant | `{{ this }}` (incremental) |
| `target` | Info sur la connexion cible | `{{ target.name }}`, `{{ target.schema }}` |
| `is_incremental()` | Test si mode incremental actif | `{% if is_incremental() %}` |
| `log()` | Afficher un message dans les logs | `{{ log("message", info=true) }}` |
| `exceptions.raise_compiler_error()` | Lever une erreur | Stopper la compilation |
| `run_query()` | Executer du SQL et lire le resultat | Requetes dynamiques |
| `statement()` | Executer du SQL (sans resultat) | DDL, operations |
| `adapter.dispatch()` | Multi-database | SQL different selon le DW |

## Ecrire des macros multi-database avec `dispatch`

Si votre projet dbt doit fonctionner sur **plusieurs bases de donnees** (Snowflake, BigQuery, PostgreSQL), utilisez `dispatch` :

```sql
{# macros/date_trunc.sql #}

{% macro date_trunc(datepart, date_column) %}
    {{ return(adapter.dispatch('date_trunc')(datepart, date_column)) }}
{% endmacro %}

{# Implementation Snowflake / PostgreSQL #}
{% macro default__date_trunc(datepart, date_column) %}
    DATE_TRUNC('{{ datepart }}', {{ date_column }})
{% endmacro %}

{# Implementation BigQuery #}
{% macro bigquery__date_trunc(datepart, date_column) %}
    DATE_TRUNC({{ date_column }}, {{ datepart }})
{% endmacro %}
```

```sql
{# Utilisation (fonctionne sur tous les DW) #}
SELECT
    {{ date_trunc('month', 'order_date') }} AS order_month,
    COUNT(*) AS nb_orders
FROM {{ ref('orders') }}
GROUP BY 1
```

## Executer une macro en standalone : `run-operation`

Vous pouvez executer une macro directement depuis la ligne de commande sans la lier a un modele :

```sql
{# macros/grant_select.sql #}

{% macro grant_select(schema, role) %}
    {% set query %}
        GRANT SELECT ON ALL TABLES IN SCHEMA {{ schema }} TO ROLE {{ role }};
    {% endset %}

    {{ log("Executing: " ~ query, info=true) }}
    {% do run_query(query) %}
    {{ log("Grant OK pour " ~ role ~ " sur " ~ schema, info=true) }}
{% endmacro %}
```

```bash
# Execution depuis le terminal
dbt run-operation grant_select --args '{"schema": "analytics", "role": "analyst_role"}'
```

**Cas d'usage de `run-operation` :**
- Administration de la base (GRANT, CREATE SCHEMA)
- Nettoyage (DROP tables obsoletes)
- Seeding de donnees de reference
- Debug et inspection

## Organisation des macros dans un projet

### Structure recommandee

```
macros/
+-- _macros.yml                  <-- Documentation des macros
+-- utils/
|   +-- safe_divide.sql
|   +-- cents_to_euros.sql
|   +-- generate_surrogate_key.sql
+-- sql_generation/
|   +-- pivot.sql
|   +-- build_where_clause.sql
|   +-- union_tables.sql
+-- schema/
|   +-- generate_schema_name.sql
|   +-- generate_alias_name.sql
+-- operations/
|   +-- grant_select.sql
|   +-- drop_old_tables.sql
+-- tests/
    +-- test_not_negative.sql
    +-- test_valid_email.sql
```

### Documenter les macros

```yaml
# macros/_macros.yml
version: 2

macros:
  - name: safe_divide
    description: "Division securisee qui retourne une valeur par defaut si le denominateur est 0 ou NULL"
    arguments:
      - name: numerator
        type: string
        description: "Nom de la colonne ou expression du numerateur"
      - name: denominator
        type: string
        description: "Nom de la colonne ou expression du denominateur"
      - name: default_value
        type: string
        description: "Valeur retournee si division impossible (defaut: 0)"

  - name: pivot
    description: "Genere un pivot dynamique avec agregation configurable"
    arguments:
      - name: column
        type: string
        description: "Colonne a pivoter"
      - name: values
        type: list
        description: "Liste des valeurs a pivoter"
      - name: agg
        type: string
        description: "Fonction d'agregation (SUM, COUNT, AVG). Defaut: SUM"
```

## Tests personnalises (generic tests) avec des macros

Les tests generiques sont des macros speciales qui retournent des lignes en echec.

```sql
{# tests/generic/test_not_negative.sql #}

{% test not_negative(model, column_name) %}

    SELECT
        {{ column_name }} AS invalid_value,
        COUNT(*) AS occurrences
    FROM {{ model }}
    WHERE {{ column_name }} < 0
    GROUP BY 1

{% endtest %}
```

```yaml
# Utilisation dans schema.yml
models:
  - name: orders
    columns:
      - name: amount
        tests:
          - not_negative
      - name: quantity
        tests:
          - not_negative
```

```sql
{# Test generique plus avance : valeur dans un range #}
{# tests/generic/test_in_range.sql #}

{% test in_range(model, column_name, min_value=0, max_value=1000000) %}

    SELECT
        {{ column_name }} AS out_of_range_value,
        COUNT(*) AS occurrences
    FROM {{ model }}
    WHERE {{ column_name }} < {{ min_value }}
       OR {{ column_name }} > {{ max_value }}
    GROUP BY 1

{% endtest %}
```

```yaml
# Utilisation
columns:
  - name: price
    tests:
      - in_range:
          min_value: 0
          max_value: 50000
```

## Packages dbt : macros de la communaute

### dbt_utils : le package essentiel

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
```

```bash
dbt deps  # Installer les packages
```

**Macros dbt_utils les plus utilisees :**

| Macro | Usage | Exemple |
|-------|-------|---------|
| `generate_surrogate_key` | Cle de substitution | `{{ dbt_utils.generate_surrogate_key(['id', 'date']) }}` |
| `star` | Toutes les colonnes sauf... | `{{ dbt_utils.star(ref('orders'), except=['created_at']) }}` |
| `pivot` | Pivot de colonnes | `{{ dbt_utils.pivot('status', values) }}` |
| `unpivot` | Inverse du pivot | `{{ dbt_utils.unpivot(ref('wide_table'), ...) }}` |
| `union_relations` | UNION de tables | `{{ dbt_utils.union_relations([ref('a'), ref('b')]) }}` |
| `get_column_values` | Valeurs distinctes | `{{ dbt_utils.get_column_values(ref('orders'), 'status') }}` |
| `date_spine` | Generer une serie de dates | Table calendrier |

```sql
{# Exemple : generer un calendrier #}
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2020-01-01' as date)",
    end_date="cast('2025-12-31' as date)"
) }}
```

### Autres packages utiles

| Package | Usage |
|---------|-------|
| `dbt-labs/codegen` | Generer du code dbt (YAML, staging models) |
| `calogica/dbt_expectations` | Tests de qualite type Great Expectations |
| `dbt-labs/audit_helper` | Comparer des tables (regression testing) |
| `dbt-labs/dbt_external_tables` | Gerer les tables externes (S3, GCS) |

## Bonnes pratiques

### 1. Nommage et conventions

```
Convention de nommage des macros :
- Utiliser snake_case : safe_divide, generate_surrogate_key
- Prefixer les macros de test generiques : test_not_negative
- Prefixer les macros internes (privees) : _helper_build_query
- Nom explicite : generate_schema_name, not : gsn
```

### 2. Paramètres et valeurs par defaut

```sql
{# BON : parametres explicites avec defaults #}
{% macro my_macro(column_name, precision=2, include_nulls=false) %}
    ...
{% endmacro %}

{# MAUVAIS : pas de defaults, parametres peu clairs #}
{% macro my_macro(c, p, n) %}
    ...
{% endmacro %}
```

### 3. Quand creer une macro ?

| Situation | Macro ? | Pourquoi |
|-----------|---------|----------|
| Logique dupliquee dans 3+ modeles | Oui | DRY (Don't Repeat Yourself) |
| SQL complexe reutilisable | Oui | Lisibilite et maintenance |
| Test personnalise | Oui | Tests generiques reutilisables |
| Logique specifique a 1 seul modele | Non | Pas besoin d'abstraction |
| 3 lignes de SQL simple | Non | Macro plus complexe que le SQL |

### 4. Tester ses macros

```bash
# Compiler pour verifier le SQL genere (sans executer)
dbt compile --select my_model

# Regarder le SQL genere
cat target/compiled/my_project/models/my_model.sql

# Executer une macro standalone
dbt run-operation my_macro --args '{"param1": "value1"}'
```

## Exercice pratique : creer une macro de SCD Type 2

Voici un exercice avance pour mettre en pratique les concepts vus dans ce chapitre.

**Objectif :** Creer une macro qui genere le SQL pour une Slowly Changing Dimension Type 2.

```sql
{# macros/scd_type2.sql #}

{% macro scd_type2(source_table, unique_key, tracked_columns) %}

    WITH source AS (
        SELECT
            *,
            MD5(
                {%- for col in tracked_columns -%}
                    COALESCE(CAST({{ col }} AS VARCHAR), '')
                    {%- if not loop.last -%} || '|' || {%- endif -%}
                {%- endfor -%}
            ) AS _row_hash
        FROM {{ source_table }}
    ),

    existing AS (
        SELECT *
        FROM {{ this }}
        WHERE _valid_to IS NULL
    ),

    changes AS (
        SELECT
            s.*,
            CASE
                WHEN e.{{ unique_key }} IS NULL THEN 'INSERT'
                WHEN s._row_hash != e._row_hash THEN 'UPDATE'
                ELSE 'NO_CHANGE'
            END AS _change_type
        FROM source s
        LEFT JOIN existing e
            ON s.{{ unique_key }} = e.{{ unique_key }}
    )

    -- Nouvelles lignes et mises a jour
    SELECT
        {{ unique_key }},
        {%- for col in tracked_columns %}
        {{ col }},
        {%- endfor %}
        _row_hash,
        CURRENT_TIMESTAMP() AS _valid_from,
        NULL AS _valid_to,
        TRUE AS _is_current
    FROM changes
    WHERE _change_type IN ('INSERT', 'UPDATE')

{% endmacro %}
```

## Points cles a retenir

1. **Jinja** est le moteur de templating qui rend dbt puissant : `{{ }}` pour les expressions, `{% %}` pour la logique
2. Les **filtres** (`|`) transforment les valeurs : `upper`, `lower`, `join`, `default`
3. Le **controle des espaces** (`{%- ... -%}`) est essentiel pour un SQL compile propre
4. Les **macros** sont des fonctions reutilisables dans `macros/` : elles eliminent la duplication SQL
5. `run_query()` permet d'executer du SQL et d'utiliser le resultat dans la logique Jinja
6. La variable `execute` distingue le parsing de l'execution : proteger les `run_query()` avec `{% if execute %}`
7. `dispatch()` permet d'ecrire des macros **multi-database**
8. Le package **dbt_utils** fournit des macros essentielles a installer dans tout projet
9. Les **tests generiques** sont des macros speciales pour la qualite des donnees
10. Toujours **documenter** ses macros dans `_macros.yml`

---

**Prochaine etape :** [Exercices dbt](10-exercices.md) (Exercice 4 : Macros et packages)

[Retour au sommaire](./README.md)
