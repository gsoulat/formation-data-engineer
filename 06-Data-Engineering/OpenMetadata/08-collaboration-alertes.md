# Chapitre 8 : Collaboration et Alertes

## Table des matières

1. [Conversations sur les assets](#conversations-sur-les-assets)
2. [Système de tâches](#système-de-tâches)
3. [Notifications et alertes](#notifications-et-alertes)
4. [Intégrations (Slack, Teams, Email)](#intégrations-slack-teams-email)
5. [Activity Feed et audit](#activity-feed-et-audit)

---

## Conversations sur les assets

### Principe

OpenMetadata intègre un système de **conversations** directement sur chaque asset (table, colonne, dashboard, pipeline). Cela évite les discussions éparpillées sur Slack, email ou Jira.

### Démarrer une conversation

1. Ouvrir un asset (table, dashboard, etc.)
2. Aller dans l'onglet **Activity Feed**
3. Cliquer **Start a conversation**
4. Rédiger le message en Markdown
5. Mentionner des utilisateurs avec `@username`

### Cas d'usage

| Cas | Exemple de conversation |
|-----|------------------------|
| Question sur une colonne | "@alice Que représente `ltv_30d` dans `dim_customers` ?" |
| Signalement de problème | "Les données de `daily_sales` du 15/01 semblent incorrectes. @data-engineering pouvez-vous vérifier ?" |
| Demande de documentation | "@bob Peux-tu documenter les colonnes de `stg_payments` ?" |
| Annonce de changement | "⚠️ La colonne `status` va être renommée en `order_status` le 20/01. @all" |

### Conversations au niveau colonne

Vous pouvez démarrer une conversation spécifiquement sur une **colonne** :

1. Ouvrir la table → Onglet **Schema**
2. Survoler la colonne → Cliquer sur l'icône de conversation
3. La conversation est liée à cette colonne spécifique

---

## Système de tâches

### Types de tâches

OpenMetadata permet de créer des **tâches** assignables :

| Type | Description | Exemple |
|------|-------------|---------|
| **Request Description** | Demander la documentation | "Ajouter une description à `raw.events`" |
| **Request Tag** | Demander une classification | "Classifier les colonnes PII de `raw.users`" |
| **Update Description** | Mettre à jour la doc existante | "La description de `status` est obsolète" |
| **Update Tag** | Modifier une classification | "Changer le tier de Tier3 à Tier2" |
| **Generic** | Tâche libre | "Vérifier le lineage de `fact_revenue`" |

### Créer une tâche

**Via l'UI** :

1. Sur un asset, cliquer **Create Task** (icône ✓)
2. Sélectionner le type
3. Remplir :
   - **Assignee** : personne responsable
   - **Description** : détail de la demande
4. Soumettre

**Via l'API** :

```python
task = {
    "message": "Ajouter les descriptions manquantes aux colonnes de raw.customers",
    "about": "<#E::table::demo-postgres.ecommerce.raw.customers>",
    "taskType": "RequestDescription",
    "assignees": [
        {"id": "user-uuid", "type": "user"}
    ]
}

response = requests.post(
    f"{API_URL}/feed",
    headers=headers,
    json=task
)
```

### Workflow des tâches

```
Créée → Assignée → En cours → Complétée
                       │
                       └──→ Réassignée (si besoin)
```

### Résolution d'une tâche

1. L'assigné ouvre la tâche dans son feed
2. Effectue le travail demandé (documenter, classifier, etc.)
3. Marque la tâche comme **Resolved**
4. Le demandeur reçoit une notification

---

## Notifications et alertes

### Types d'événements

| Événement | Description |
|-----------|-------------|
| **Entity Created** | Nouvelle table, dashboard, pipeline détecté |
| **Entity Updated** | Modification de schéma, description, owner |
| **Entity Deleted** | Suppression d'un asset |
| **Test Failed** | Échec d'un test de qualité |
| **Test Passed** | Test précédemment en échec qui repasse |
| **Conversation** | Nouveau message ou mention |
| **Task Assigned** | Nouvelle tâche assignée |
| **Schema Change** | Ajout/suppression/modification de colonne |

### Configurer les alertes

1. **Settings** → **Notifications** → **Add Alert**
2. Configuration :

```
Alert Configuration
├── Name: "Schema Changes - Production"
├── Description: "Alerter sur les changements de schéma en prod"
│
├── Trigger:
│   └── Event: entityUpdated
│       └── Field: columns
│
├── Filter:
│   ├── Service: bigquery-prod
│   └── Tags: Tier.Tier1, Tier.Tier2
│
└── Destination:
    ├── Type: Slack
    └── Channel: #data-alerts
```

### Alertes recommandées

| Alerte | Trigger | Filtre | Destination |
|--------|---------|--------|-------------|
| Schema changes (prod) | `entityUpdated.columns` | Tier 1-2 | Slack #data-alerts |
| Test failures | `testCaseFailure` | Tier 1 | Slack #data-quality |
| New tables detected | `entityCreated` | All | Email résumé quotidien |
| Ownership missing | `entityCreated` | Tier 1-3 | Tâche auto-assignée |
| PII detected | `tagAdded.PII.*` | All | Slack #data-governance |

---

## Intégrations (Slack, Teams, Email)

### Slack

#### Configuration du webhook

1. Créer une [Slack App](https://api.slack.com/apps) ou un webhook entrant
2. Copier l'URL du webhook
3. Dans OpenMetadata : **Settings** → **Notifications** → Destination **Slack**
4. Coller l'URL du webhook

#### Format des messages Slack

```
🔔 OpenMetadata Alert
━━━━━━━━━━━━━━━━━━━━
📊 Table: demo-postgres.ecommerce.raw.customers
🔄 Event: Schema Changed
📝 Details:
  - Column added: loyalty_points (INTEGER)
  - Column removed: old_status
👤 Changed by: alice.martin
🕐 Time: 2024-01-16 14:30 UTC

🔗 View in OpenMetadata
```

### Microsoft Teams

#### Configuration

1. Créer un webhook entrant dans le canal Teams
2. Dans OpenMetadata : **Settings** → **Notifications** → Destination **MS Teams**
3. Coller l'URL du webhook

### Email (SMTP)

#### Configuration

Dans le `docker-compose.yml` :

```yaml
openmetadata-server:
  environment:
    SMTP_SERVER_ENDPOINT: smtp.gmail.com
    SMTP_SERVER_PORT: 587
    SMTP_USERNAME: openmetadata-alerts@votredomaine.com
    SMTP_PASSWORD: votre-app-password
    SMTP_SENDER_MAIL: openmetadata-alerts@votredomaine.com
```

#### Types d'emails

| Email | Contenu | Fréquence |
|-------|---------|-----------|
| Résumé quotidien | Changements, tests, tâches | Quotidien |
| Alerte critique | Test Tier 1 en échec | Immédiat |
| Tâche assignée | Nouvelle tâche à traiter | Immédiat |
| Mention | Quelqu'un vous a mentionné | Immédiat |

### Webhook générique

Pour les intégrations custom (PagerDuty, Opsgenie, etc.) :

```json
{
    "name": "custom-webhook",
    "endpoint": "https://your-service.com/webhook",
    "eventFilters": [
        {
            "eventType": "entityUpdated",
            "entities": ["table"]
        }
    ],
    "headers": {
        "Authorization": "Bearer your-token",
        "Content-Type": "application/json"
    }
}
```

---

## Activity Feed et audit

### Activity Feed

Le feed d'activité centralise **tous les événements** :

```
Activity Feed
├── 14:30 - alice.martin updated description of raw.customers
├── 14:25 - Schema change detected: raw.orders (column added: tracking_id)
├── 14:00 - Test PASSED: columnValuesToBeNotNull on raw.customers.email
├── 13:45 - bob.dupont commented on analytics.daily_sales
├── 13:30 - Ingestion completed: demo-postgres (Metadata)
├── 13:00 - Test FAILED: tableRowCountToBeBetween on raw.orders
└── ...
```

### Filtres du feed

| Filtre | Usage |
|--------|-------|
| **My Activity** | Actions effectuées par vous |
| **Mentions** | Conversations où vous êtes mentionné |
| **Tasks** | Tâches qui vous sont assignées |
| **All** | Tout le feed |
| **By Service** | Filtrer par source |
| **By Team** | Filtrer par équipe |

### Audit trail

OpenMetadata conserve un **historique complet** de toutes les modifications :

```python
# Récupérer l'historique d'une table via l'API
response = requests.get(
    f"{API_URL}/feed",
    params={
        "entityLink": "<#E::table::demo-postgres.ecommerce.raw.customers>",
        "type": "Conversation"
    },
    headers=headers
)

for event in response.json()["data"]:
    print(f"{event['updatedAt']} - {event['updatedBy']} - {event['message']}")
```

### Métriques d'adoption

La page **Insights** fournit des métriques sur l'utilisation d'OpenMetadata :

| Métrique | Description |
|----------|-------------|
| Most viewed tables | Tables les plus consultées |
| Most active users | Utilisateurs les plus actifs |
| Documentation coverage | % d'assets documentés |
| Ownership coverage | % d'assets avec un owner |
| Tag coverage | % d'assets classifiés |

---

## Résumé

| Fonctionnalité | À retenir |
|---------------|-----------|
| Conversations | Discussions contextuelles sur chaque asset |
| Tâches | Assignation de travail (documentation, classification) |
| Alertes | Notifications sur changements, échecs, anomalies |
| Intégrations | Slack, Teams, Email, Webhook |
| Activity Feed | Historique complet de tous les événements |
| Audit | Traçabilité de qui a modifié quoi et quand |

---

> **Prochain chapitre** : [API REST et SDK Python](09-api-sdk.md) - Automatiser et étendre OpenMetadata
