# Chapitre 9 : MCP Servers & Extensibilité

## Objectifs

- Comprendre le protocole MCP (Model Context Protocol)
- Installer et configurer des serveurs MCP
- Connecter Claude Code à des outils externes (Slack, DB, APIs)
- Créer son propre serveur MCP basique

---

## 1. Qu'est-ce que MCP ?

### 1.1 Le concept

**MCP (Model Context Protocol)** est un protocole ouvert qui permet à Claude Code de se connecter à des **outils et sources de données externes** :

```
SANS MCP                              AVEC MCP
┌─────────────────────┐              ┌──────────────────────────────────┐
│   Claude Code       │              │   Claude Code                    │
│                     │              │                                  │
│   Outils intégrés : │              │   Outils intégrés : Read, Edit...│
│   Read, Edit, Bash  │              │                                  │
│   Glob, Grep...     │              │   + MCP Servers :                │
│                     │              │   ┌──────────┐ ┌──────────┐     │
│   C'est tout.       │              │   │ Postgres │ │  Slack   │     │
│                     │              │   │ (SQL)    │ │ (message)│     │
│                     │              │   └──────────┘ └──────────┘     │
│                     │              │   ┌──────────┐ ┌──────────┐     │
│                     │              │   │ Sentry   │ │ Jira     │     │
│                     │              │   │ (errors) │ │ (tickets)│     │
│                     │              │   └──────────┘ └──────────┘     │
└─────────────────────┘              └──────────────────────────────────┘
```

### 1.2 Comment ça marche

```
Vous : "Quelles sont les erreurs fréquentes en production ?"

Claude Code                     Serveur MCP Sentry
    │                                │
    │  ← Quels outils dispo ? ──────│
    │  ─── list_errors, get_error ──▶│
    │                                │
    │  ← list_errors(last_24h) ─────│
    │  ─── [Error1, Error2, ...] ──▶│
    │                                │
    │  ← get_error(Error1.id) ──────│
    │  ─── {stack, count, users} ──▶│
    │                                │
    ▼
"Les 3 erreurs les plus fréquentes sont..."
```

---

## 2. Configurer des serveurs MCP

### 2.1 Configuration globale

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb"
      }
    }
  }
}
```

### 2.2 Configuration par projet

```json
// mon-projet/.claude/settings.json
{
  "mcpServers": {
    "mon-api": {
      "command": "node",
      "args": ["./mcp-server/index.js"],
      "env": {
        "API_URL": "http://localhost:3000"
      }
    }
  }
}
```

### 2.3 Vérifier les serveurs connectés

```
> /mcp
```

Affiche la liste des serveurs MCP actifs et leurs outils.

---

## 3. Serveurs MCP populaires

### 3.1 Base de données : PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb"
      }
    }
  }
}
```

Usage :
```
> Montre-moi les 10 dernières commandes avec un total > 100€
> Quel est le schéma de la table users ?
> Combien d'utilisateurs se sont inscrits cette semaine ?
```

### 3.2 Filesystem étendu

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "/chemin/vers/dossier/autorisé"]
    }
  }
}
```

### 3.3 GitHub avancé

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

### 3.4 Slack

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "SLACK_TEAM_ID": "T..."
      }
    }
  }
}
```

Usage :
```
> Envoie un message dans #dev avec le résumé des changements d'aujourd'hui
> Quels sont les derniers messages dans #incidents ?
```

### 3.5 Puppeteer (navigateur web)

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

Usage :
```
> Va sur http://localhost:3000 et fais une capture d'écran
> Teste le formulaire de login avec les identifiants de test
```

### 3.6 Tableau récapitulatif

| Serveur MCP | Usage | Package |
|-------------|-------|---------|
| **PostgreSQL** | Requêtes SQL directes | `@modelcontextprotocol/server-postgres` |
| **SQLite** | Base locale | `@modelcontextprotocol/server-sqlite` |
| **Filesystem** | Accès fichiers hors projet | `@modelcontextprotocol/server-filesystem` |
| **GitHub** | Issues, PRs, repos | `@modelcontextprotocol/server-github` |
| **Slack** | Messages, channels | `@anthropic-ai/mcp-server-slack` |
| **Puppeteer** | Navigation web | `@modelcontextprotocol/server-puppeteer` |
| **Brave Search** | Recherche web | `@anthropic-ai/mcp-server-brave-search` |
| **Memory** | Mémoire persistante | `@modelcontextprotocol/server-memory` |
| **Fetch** | Requêtes HTTP | `@modelcontextprotocol/server-fetch` |

---

## 4. Architecture MCP

### 4.1 Les composants

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Claude Code  │     │  MCP Server  │     │   Resource   │
│   (Client)   │◄───▶│  (Bridge)    │◄───▶│  (External)  │
└──────────────┘     └──────────────┘     └──────────────┘

                     Le serveur MCP est
                     un "traducteur" entre
                     Claude et la resource
                     externe.
```

### 4.2 Ce qu'un serveur MCP expose

```
Un serveur MCP peut exposer :
│
├── Tools (outils)
│   ├── Actions que Claude peut appeler
│   └── Ex: "query_database", "send_message"
│
├── Resources (ressources)
│   ├── Données que Claude peut lire
│   └── Ex: "schema://tables", "file://config.yml"
│
└── Prompts (templates)
    ├── Templates de prompts prédéfinis
    └── Ex: "analyze_table", "review_query"
```

---

## 5. Créer un serveur MCP basique

### 5.1 Avec le SDK TypeScript

```typescript
// mon-mcp-server/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "mon-serveur",
  version: "1.0.0"
});

// Définir un outil
server.tool(
  "get_weather",
  "Récupère la météo d'une ville",
  {
    city: z.string().describe("Nom de la ville")
  },
  async ({ city }) => {
    // Ici, appeler votre API météo
    const weather = await fetchWeather(city);
    return {
      content: [{
        type: "text",
        text: JSON.stringify(weather)
      }]
    };
  }
);

// Lancer le serveur
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 5.2 Avec le SDK Python

```python
# mon_mcp_server/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("mon-serveur")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Récupère la météo d'une ville",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Nom de la ville"}
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        weather = await fetch_weather(arguments["city"])
        return [TextContent(type="text", text=str(weather))]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 5.3 Configurer le serveur custom

```json
// .claude/settings.json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["./mon_mcp_server/server.py"]
    }
  }
}
```

---

## 6. Cas d'usage avancés

### 6.1 Pipeline complet avec MCP

```
Scénario : "Analyse les erreurs de prod et propose des fixes"

Claude Code
    │
    ├── MCP Sentry → Liste les erreurs récentes
    │
    ├── MCP Postgres → Vérifie les données associées
    │
    ├── Outils intégrés → Lit le code source concerné
    │
    ├── Outils intégrés → Écrit le fix
    │
    ├── Bash → Lance les tests
    │
    ├── Outils intégrés → Commit & PR
    │
    └── MCP Slack → Notifie l'équipe dans #fixes
```

### 6.2 MCP + CLAUDE.md

Documentez vos serveurs MCP dans CLAUDE.md :

```markdown
## Serveurs MCP disponibles

### PostgreSQL (base de prod)
- Accès en lecture seule à la DB de production
- Tables principales : users, orders, products
- Utilise `query_database` pour les requêtes SQL

### Slack
- Canal #dev pour les notifications de déploiement
- Canal #incidents pour les alertes
```

---

## 7. Sécurité MCP

### 7.1 Bonnes pratiques

```
✅ Limiter les permissions (lecture seule pour les DB de prod)
✅ Utiliser des tokens avec des scopes minimaux
✅ Ne JAMAIS mettre de secrets dans les fichiers committés
✅ Préférer les variables d'environnement
✅ Auditer régulièrement les serveurs MCP actifs

❌ Accès en écriture à la DB de production
❌ Tokens avec tous les scopes
❌ Secrets en dur dans settings.json
```

### 7.2 Variables d'environnement

```bash
# Plutôt que de mettre les secrets dans settings.json,
# définissez-les dans votre shell :
export POSTGRES_URL="postgresql://..."
export SLACK_TOKEN="xoxb-..."
export GITHUB_TOKEN="ghp_..."
```

```json
// settings.json référence les variables
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "${POSTGRES_URL}"
      }
    }
  }
}
```

---

## Exercices pratiques

### Exercice 1 : Installer un serveur MCP
1. Configurez le serveur MCP Filesystem
2. Donnez accès à un dossier de données
3. Demandez à Claude d'analyser les fichiers

### Exercice 2 : PostgreSQL via MCP
1. Lancez une base PostgreSQL locale (Docker)
2. Configurez le serveur MCP PostgreSQL
3. Demandez à Claude d'explorer le schéma et de faire des requêtes

### Exercice 3 : Créer un serveur MCP
1. Créez un serveur MCP basique qui expose un outil
2. Configurez-le dans Claude Code
3. Testez-le avec `/tools` et un prompt

---

## Résumé

```
MCP (Model Context Protocol)
│
├── Concept : Connecter Claude Code à des outils externes
├── Config  : settings.json → mcpServers
├── Populaires :
│   ├── PostgreSQL (requêtes SQL)
│   ├── GitHub (issues, PRs)
│   ├── Slack (messages)
│   ├── Puppeteer (navigateur)
│   └── Filesystem (fichiers hors projet)
├── Custom  : SDK TypeScript ou Python
├── Sécurité : Tokens minimaux, pas de secrets en dur
└── Vérifier : /mcp et /tools
```

> **Prochain chapitre** : [Hooks, Automatisation & CI/CD](10-hooks-automatisation.md)
