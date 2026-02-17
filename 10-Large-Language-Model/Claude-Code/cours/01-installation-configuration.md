# Chapitre 1 : Installation & Configuration

## Objectifs

- Installer Claude Code sur macOS, Linux et Windows (WSL2)
- Comprendre les différentes méthodes d'authentification
- Configurer son environnement de travail optimal
- Vérifier que tout fonctionne correctement

---

## 1. Qu'est-ce que Claude Code ?

Claude Code est le **CLI officiel d'Anthropic** qui permet d'interagir avec Claude directement depuis le terminal. Contrairement à l'interface web, Claude Code :

```
Interface Web Claude              Claude Code (CLI)
┌─────────────────────┐          ┌─────────────────────────────────┐
│                     │          │                                 │
│  Chat classique     │          │  Accès direct au filesystem     │
│  Copier/coller code │          │  Exécution de commandes shell   │
│  Pas de contexte    │          │  Lecture/écriture de fichiers   │
│  projet             │          │  Intégration Git native         │
│                     │          │  Compréhension du projet entier │
│                     │          │  Exécution de tests             │
│                     │          │  Création de commits/PRs        │
│                     │          │                                 │
└─────────────────────┘          └─────────────────────────────────┘
    "Aide-moi avec                    "Travaille DANS mon projet"
     du code"
```

> **En résumé** : Claude Code ne se contente pas de répondre à des questions — il **agit** dans votre codebase.

---

## 2. Prérequis

### 2.1 Node.js (version 18+)

Claude Code est distribué comme un package npm. Vous avez besoin de Node.js >= 18.

```bash
# Vérifier votre version
node --version
# Doit afficher v18.x.x ou supérieur

# Si pas installé, utiliser nvm (recommandé)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc  # ou ~/.zshrc
nvm install 22
nvm use 22
```

### 2.2 Système d'exploitation

| OS | Support | Notes |
|----|---------|-------|
| **macOS** | Natif | Fonctionne directement |
| **Linux** | Natif | Toutes distributions |
| **Windows** | Via WSL2 | **Windows natif non supporté** |

### 2.3 Pour Windows : Installer WSL2

```powershell
# Dans PowerShell en tant qu'administrateur
wsl --install

# Redémarrer, puis dans le terminal WSL :
sudo apt update && sudo apt upgrade -y
sudo apt install -y nodejs npm
```

> **Attention** : Claude Code ne fonctionne **PAS** nativement sur Windows. WSL2 est **obligatoire**.

---

## 3. Installation

### 3.1 Installation via npm (recommandée)

```bash
# Installation globale
npm install -g @anthropic-ai/claude-code

# Vérifier l'installation
claude --version
```

### 3.2 Mise à jour

```bash
# Mettre à jour vers la dernière version
npm update -g @anthropic-ai/claude-code

# Ou forcer une version spécifique
npm install -g @anthropic-ai/claude-code@latest
```

### 3.3 Résolution des problèmes courants

#### Erreur de permissions npm

```bash
# Si vous avez une erreur EACCES
# Option 1 : Changer le prefix npm (recommandé)
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Option 2 : Utiliser npx sans installation globale
npx @anthropic-ai/claude-code
```

#### Node.js trop ancien

```bash
# Vérifier la version
node --version

# Si < 18, mettre à jour avec nvm
nvm install 22
nvm alias default 22
```

---

## 4. Authentification

Claude Code supporte **3 méthodes d'authentification** :

```
Méthodes d'authentification
├── 1. Compte Anthropic (OAuth)     ← Le plus simple
├── 2. Clé API Anthropic            ← Pour l'automatisation
└── 3. API tiers (AWS Bedrock,      ← Pour les entreprises
│      Google Vertex AI)
```

### 4.1 Méthode 1 : Connexion OAuth (recommandée pour débuter)

```bash
# Lancer Claude Code
claude

# Au premier lancement, il ouvre votre navigateur
# pour vous connecter à votre compte Anthropic
# Suivez les instructions à l'écran
```

> Nécessite un abonnement **Claude Max** ($100/mois) ou **Claude Pro** ($20/mois) + crédits API.

### 4.2 Méthode 2 : Clé API

```bash
# Définir la variable d'environnement
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Ajouter au profil shell pour persister
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc

# Lancer Claude Code
claude
```

> Pour obtenir une clé API : https://console.anthropic.com/settings/keys

### 4.3 Méthode 3 : AWS Bedrock

```bash
# Configurer les variables d'environnement
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."

claude
```

### 4.4 Méthode 3 bis : Google Vertex AI

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=us-east5
export ANTHROPIC_VERTEX_PROJECT_ID="mon-projet-gcp"

claude
```

---

## 5. Premier lancement

```bash
# Se placer dans un projet
cd ~/mes-projets/mon-app

# Lancer Claude Code
claude
```

Vous devriez voir :

```
╭──────────────────────────────────────╮
│                                      │
│   Claude Code                        │
│                                      │
│   /help for help                     │
│                                      │
╰──────────────────────────────────────╯

 >
```

### 5.1 Test rapide

Tapez votre première commande :

```
> Décris-moi ce projet en 3 lignes
```

Claude va automatiquement :
1. Scanner la structure du projet
2. Lire les fichiers clés (README, package.json, etc.)
3. Vous donner un résumé

---

## 6. Configuration initiale

### 6.1 Fichier de configuration global

Les settings globaux se trouvent dans `~/.claude/settings.json` :

```json
{
  "permissions": {
    "allow": [],
    "deny": []
  },
  "env": {
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "16000"
  }
}
```

### 6.2 Le thème et l'affichage

```bash
# Changer le thème (clair/sombre)
claude config set theme dark

# Configurer la verbosité
claude config set verbose true
```

### 6.3 Configuration du modèle

```bash
# Par défaut, Claude Code utilise claude-sonnet-4-5
# Pour utiliser Opus (plus puissant mais plus lent/cher) :
claude config set model claude-opus-4-6

# Pour utiliser Haiku (plus rapide et économique) :
claude config set model claude-haiku-4-5-20251001
```

| Modèle | Vitesse | Qualité | Coût | Usage recommandé |
|--------|---------|---------|------|-------------------|
| **Haiku 4.5** | Très rapide | Bon | $ | Tâches simples, questions rapides |
| **Sonnet 4.5** | Rapide | Très bon | $$ | Usage quotidien (défaut) |
| **Opus 4.6** | Plus lent | Excellent | $$$$ | Tâches complexes, architecture |

---

## 7. Intégration IDE

### 7.1 VS Code

Claude Code s'intègre nativement dans VS Code :

```bash
# Installer l'extension depuis le terminal
claude ide install vscode
```

Ensuite dans VS Code :
- `Ctrl+Shift+P` > "Claude Code: Open"
- Ou utiliser le raccourci `Ctrl+Esc` (configurable)

### 7.2 JetBrains (IntelliJ, PyCharm, etc.)

```bash
claude ide install jetbrains
```

### 7.3 Terminal intégré

Vous pouvez aussi simplement utiliser Claude Code dans le terminal intégré de n'importe quel IDE.

---

## 8. Vérification de l'installation

Checklist finale :

```bash
# 1. Claude Code est installé
claude --version
# ✓ Doit afficher la version

# 2. L'authentification fonctionne
claude "dis bonjour"
# ✓ Doit répondre sans erreur

# 3. Depuis un projet
cd ~/un-projet-existant
claude "décris ce projet"
# ✓ Doit lire et analyser le projet
```

---

## Exercice pratique

1. Installez Claude Code sur votre machine
2. Authentifiez-vous avec votre méthode préférée
3. Naviguez dans un de vos projets existants
4. Demandez à Claude Code de décrire le projet
5. Demandez-lui de trouver un fichier spécifique

---

## Résumé

```
Installation Claude Code
│
├── Prérequis : Node.js >= 18
├── Install   : npm install -g @anthropic-ai/claude-code
├── Auth      : OAuth (simple) / API Key (auto) / Cloud (entreprise)
├── Lancer    : cd mon-projet && claude
└── Config    : ~/.claude/settings.json
```

> **Prochain chapitre** : [Premiers Pas & Concepts Fondamentaux](02-premiers-pas.md)
