# Chapitre 9 : API REST et SDK Python

## Table des matières

1. [Architecture de l'API](#architecture-de-lapi)
2. [Authentification](#authentification)
3. [Explorer l'API (Swagger)](#explorer-lapi-swagger)
4. [CRUD sur les entités](#crud-sur-les-entités)
5. [SDK Python](#sdk-python)
6. [Automatisation et scripts](#automatisation-et-scripts)
7. [Exemples pratiques](#exemples-pratiques)

---

## Architecture de l'API

### API-first design

OpenMetadata est conçu **API-first** : tout ce que fait l'UI est disponible via l'API REST.

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│    UI    │────▶│   API    │────▶│  Database    │
│  (React) │     │  Server  │     │  (MySQL/PG)  │
└──────────┘     └────▲─────┘     └──────────────┘
                      │
┌──────────┐          │
│  SDK     │──────────┘
│ (Python) │
└──────────┘
```

### Endpoints principaux

| Endpoint | Description |
|----------|-------------|
| `/api/v1/tables` | Gestion des tables |
| `/api/v1/databases` | Gestion des bases de données |
| `/api/v1/databaseSchemas` | Gestion des schémas |
| `/api/v1/services/databaseServices` | Services de bases de données |
| `/api/v1/dashboards` | Gestion des dashboards |
| `/api/v1/pipelines` | Gestion des pipelines |
| `/api/v1/topics` | Gestion des topics (Kafka) |
| `/api/v1/mlmodels` | Gestion des modèles ML |
| `/api/v1/glossaryTerms` | Gestion du glossaire |
| `/api/v1/tags` | Gestion des tags |
| `/api/v1/teams` | Gestion des équipes |
| `/api/v1/users` | Gestion des utilisateurs |
| `/api/v1/feed` | Activity feed et conversations |
| `/api/v1/search/query` | Recherche full-text |
| `/api/v1/lineage` | Gestion du lineage |
| `/api/v1/dataQuality/testCases` | Tests de qualité |

---

## Authentification

### Obtenir un JWT Token

#### Via l'UI

1. **Settings** → **Bots** → **ingestion-bot** (ou créer un nouveau bot)
2. Copier le **JWT Token**

#### Via l'API

```bash
# Authentification basique
curl -X POST "http://localhost:8585/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@openmetadata.org",
    "password": "admin"
  }'

# Réponse
{
    "tokenType": "Bearer",
    "accessToken": "eyJhbGciOiJSUzI1NiJ9...",
    "expiryDuration": 3600
}
```

### Utiliser le token

```bash
# Toutes les requêtes doivent inclure le header Authorization
curl -X GET "http://localhost:8585/api/v1/tables?limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiJ9..."
```

### Créer un bot dédié

Pour les scripts d'automatisation, créez un bot dédié :

1. **Settings** → **Bots** → **Add Bot**
2. Nommer le bot (ex: `automation-bot`)
3. Générer un JWT Token
4. Stocker le token de manière sécurisée (variable d'environnement, secret manager)

---

## Explorer l'API (Swagger)

### Documentation interactive

OpenMetadata fournit une documentation Swagger complète :

```
URL : http://localhost:8585/swagger.html
```

### Tester une requête dans Swagger

1. Ouvrir Swagger UI
2. Cliquer **Authorize** → Entrer le JWT Token
3. Naviguer vers l'endpoint souhaité
4. Cliquer **Try it out**
5. Remplir les paramètres
6. Cliquer **Execute**

---

## CRUD sur les entités

### Lister les tables

```bash
# Lister les 10 premières tables
curl -X GET "http://localhost:8585/api/v1/tables?limit=10&fields=owner,tags,columns" \
  -H "Authorization: Bearer $TOKEN"
```

### Obtenir une table par FQN

```bash
# Obtenir une table spécifique
curl -X GET "http://localhost:8585/api/v1/tables/name/demo-postgres.ecommerce.raw.customers?fields=owner,tags,columns,dataQualityTests" \
  -H "Authorization: Bearer $TOKEN"
```

### Mettre à jour la description

```bash
# PATCH : mise à jour partielle
curl -X PATCH "http://localhost:8585/api/v1/tables/name/demo-postgres.ecommerce.raw.customers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json-patch+json" \
  -d '[
    {
      "op": "add",
      "path": "/description",
      "value": "Table des clients e-commerce. Source : CRM Salesforce."
    }
  ]'
```

### Ajouter un tag à une colonne

```bash
curl -X PATCH "http://localhost:8585/api/v1/tables/name/demo-postgres.ecommerce.raw.customers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json-patch+json" \
  -d '[
    {
      "op": "add",
      "path": "/columns/3/tags/0",
      "value": {
        "tagFQN": "PII.Sensitive",
        "labelType": "Manual",
        "state": "Confirmed",
        "source": "Classification"
      }
    }
  ]'
```

### Recherche full-text

```bash
# Rechercher "customers" dans toutes les tables
curl -X GET "http://localhost:8585/api/v1/search/query?q=customers&index=table_search_index&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## SDK Python

### Installation

```bash
pip install openmetadata-ingestion
```

### Connexion au serveur

```python
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)

server_config = OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    authProvider=AuthProvider.openmetadata,
    securityConfig=OpenMetadataJWTClientConfig(
        jwtToken="votre-jwt-token"
    ),
)

metadata = OpenMetadata(server_config)

# Vérifier la connexion
health = metadata.health_check()
print(f"Connecté : {health}")
```

### Lister les tables

```python
from metadata.generated.schema.entity.data.table import Table

# Lister toutes les tables
tables = metadata.list_entities(entity=Table, limit=100)

for table in tables.entities:
    print(f"Table: {table.fullyQualifiedName.__root__}")
    print(f"  Owner: {table.owner.name if table.owner else 'Non assigné'}")
    print(f"  Colonnes: {len(table.columns)}")
    print()
```

### Obtenir une table par FQN

```python
table = metadata.get_by_name(
    entity=Table,
    fqn="demo-postgres.ecommerce.raw.customers",
    fields=["owner", "tags", "columns"]
)

print(f"Table: {table.name.__root__}")
print(f"Description: {table.description.__root__}")
for col in table.columns:
    print(f"  - {col.name.__root__} ({col.dataType.value})")
```

### Mettre à jour une description

```python
from metadata.generated.schema.type.basic import Markdown

# Mettre à jour la description
metadata.patch_description(
    entity=Table,
    source=table,
    description=Markdown("Table des clients. Mise à jour quotidienne depuis le CRM."),
    force=True
)
```

### Ajouter un tag

```python
from metadata.generated.schema.type.tagLabel import TagLabel, LabelType, State, TagSource

tag = TagLabel(
    tagFQN="PII.Sensitive",
    labelType=LabelType.Manual,
    state=State.Confirmed,
    source=TagSource.Classification,
)

metadata.patch_column_tag(
    table=table,
    column_name="email",
    tag_label=tag,
)
```

### Ajouter un lineage

```python
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type.entityReference import EntityReference

source_table = metadata.get_by_name(entity=Table, fqn="demo-postgres.ecommerce.raw.orders")
target_table = metadata.get_by_name(entity=Table, fqn="demo-postgres.ecommerce.analytics.daily_sales")

lineage = AddLineageRequest(
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=source_table.id, type="table"),
        toEntity=EntityReference(id=target_table.id, type="table"),
    )
)

metadata.add_lineage(lineage)
```

---

## Automatisation et scripts

### Script de documentation automatique

```python
"""
Script pour documenter automatiquement les tables non documentées
basé sur les conventions de nommage.
"""

DESCRIPTION_TEMPLATES = {
    "raw_": "Table brute importée depuis la source. À ne pas modifier directement.",
    "stg_": "Table de staging avec nettoyage et typage de base.",
    "int_": "Table intermédiaire de transformation.",
    "dim_": "Table dimensionnelle (référentiel).",
    "fact_": "Table de faits (événements / transactions).",
    "agg_": "Table d'agrégation pré-calculée.",
    "rpt_": "Table de reporting pour les dashboards.",
}

tables = metadata.list_entities(entity=Table, limit=1000)

for table in tables.entities:
    if table.description:
        continue  # Déjà documentée

    table_name = table.name.__root__
    for prefix, description in DESCRIPTION_TEMPLATES.items():
        if table_name.startswith(prefix):
            metadata.patch_description(
                entity=Table,
                source=table,
                description=Markdown(description),
                force=False
            )
            print(f"Documenté : {table.fullyQualifiedName.__root__}")
            break
```

### Script de classification PII automatique

```python
"""
Script pour auto-classifier les colonnes PII
basé sur le nom de la colonne.
"""

PII_COLUMNS = {
    "email": "PII.Sensitive",
    "phone": "PII.Sensitive",
    "phone_number": "PII.Sensitive",
    "address": "PII.Sensitive",
    "first_name": "PersonalData.Personal",
    "last_name": "PersonalData.Personal",
    "full_name": "PersonalData.Personal",
    "date_of_birth": "PersonalData.Personal",
    "ssn": "PersonalData.Sensitive",
    "social_security": "PersonalData.Sensitive",
    "ip_address": "PII.NonSensitive",
}

pii_tag = lambda fqn: TagLabel(
    tagFQN=fqn,
    labelType=LabelType.Automated,
    state=State.Suggested,
    source=TagSource.Classification,
)

tables = metadata.list_entities(entity=Table, limit=1000, fields=["columns", "tags"])

classified_count = 0
for table in tables.entities:
    for column in table.columns:
        col_name = column.name.__root__.lower()
        if col_name in PII_COLUMNS:
            # Vérifier si pas déjà classifié
            existing_tags = [t.tagFQN.__root__ for t in (column.tags or [])]
            tag_fqn = PII_COLUMNS[col_name]
            if tag_fqn not in existing_tags:
                metadata.patch_column_tag(
                    table=table,
                    column_name=column.name.__root__,
                    tag_label=pii_tag(tag_fqn),
                )
                classified_count += 1
                print(f"Classifié: {table.fullyQualifiedName.__root__}.{col_name} → {tag_fqn}")

print(f"\nTotal classifié : {classified_count} colonnes")
```

### Script de rapport de qualité

```python
"""
Script pour générer un rapport de qualité des données.
"""

from metadata.generated.schema.tests.testCase import TestCase

test_cases = metadata.list_entities(entity=TestCase, limit=1000)

total = 0
passed = 0
failed = 0

print("=" * 60)
print("RAPPORT QUALITÉ DES DONNÉES")
print("=" * 60)

for test in test_cases.entities:
    total += 1
    status = test.testCaseResult.testCaseStatus if test.testCaseResult else "Unknown"
    if status == "Success":
        passed += 1
        icon = "✅"
    elif status == "Failed":
        failed += 1
        icon = "❌"
    else:
        icon = "⚪"

    print(f"{icon} {test.fullyQualifiedName.__root__} → {status}")

print("=" * 60)
print(f"Total: {total} | Passés: {passed} | Échoués: {failed}")
print(f"Taux de succès: {(passed/total*100):.1f}%" if total > 0 else "Aucun test")
```

---

## Exemples pratiques

### Exemple 1 : Migration de documentation

Migrer la documentation depuis un fichier CSV vers OpenMetadata :

```python
import csv

# CSV format: table_fqn, column_name, description
with open("documentation.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        table = metadata.get_by_name(
            entity=Table,
            fqn=row["table_fqn"],
            fields=["columns"]
        )
        if table:
            if row["column_name"]:
                # Documentation de colonne
                metadata.patch_column_description(
                    table=table,
                    column_name=row["column_name"],
                    description=Markdown(row["description"]),
                )
            else:
                # Documentation de table
                metadata.patch_description(
                    entity=Table,
                    source=table,
                    description=Markdown(row["description"]),
                    force=True,
                )
```

### Exemple 2 : Export du catalogue

```python
import json

# Exporter toutes les tables avec leurs métadonnées
catalog = []

tables = metadata.list_entities(
    entity=Table,
    limit=1000,
    fields=["owner", "tags", "columns"]
)

for table in tables.entities:
    entry = {
        "fqn": table.fullyQualifiedName.__root__,
        "description": table.description.__root__ if table.description else None,
        "owner": table.owner.name if table.owner else None,
        "tags": [t.tagFQN.__root__ for t in (table.tags or [])],
        "columns": [
            {
                "name": col.name.__root__,
                "type": col.dataType.value,
                "description": col.description.__root__ if col.description else None,
                "tags": [t.tagFQN.__root__ for t in (col.tags or [])],
            }
            for col in table.columns
        ],
    }
    catalog.append(entry)

with open("catalog_export.json", "w") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Exporté {len(catalog)} tables")
```

### Exemple 3 : Monitoring de la couverture

```python
"""
Script de monitoring : vérifier que les standards de gouvernance sont respectés.
"""

tables = metadata.list_entities(
    entity=Table,
    limit=1000,
    fields=["owner", "tags", "columns"]
)

no_owner = []
no_description = []
no_tier = []

for table in tables.entities:
    fqn = table.fullyQualifiedName.__root__

    if not table.owner:
        no_owner.append(fqn)

    if not table.description:
        no_description.append(fqn)

    tags = [t.tagFQN.__root__ for t in (table.tags or [])]
    if not any(t.startswith("Tier.") for t in tags):
        no_tier.append(fqn)

print(f"📊 Rapport de gouvernance")
print(f"{'='*50}")
print(f"Tables sans owner      : {len(no_owner)}/{len(tables.entities)}")
print(f"Tables sans description : {len(no_description)}/{len(tables.entities)}")
print(f"Tables sans tier       : {len(no_tier)}/{len(tables.entities)}")

if no_owner:
    print(f"\n⚠️  Tables sans owner :")
    for t in no_owner[:10]:
        print(f"   - {t}")
```

---

## Résumé

| Concept | À retenir |
|---------|-----------|
| API REST | Tout est accessible via `/api/v1/*` |
| Auth | JWT Token via bot ou login |
| Swagger | Documentation interactive à `/swagger.html` |
| SDK Python | `openmetadata-ingestion` pour scripts et automatisation |
| CRUD | GET, POST, PATCH, DELETE sur toutes les entités |
| Automatisation | Documentation, classification, reporting automatisés |

---

> **Prochain chapitre** : [Exercices Pratiques](10-exercices.md) - Mettre en pratique tous les concepts
