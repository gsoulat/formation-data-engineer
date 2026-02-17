# Chapitre 2 : Premiers Pas & Concepts Fondamentaux

## Objectifs

- Comprendre le fonctionnement interne de Claude Code
- Maîtriser le cycle de base : prompt > outils > réponse
- Connaître les outils internes que Claude Code utilise
- Savoir lire et interpréter les outputs
- Apprendre les raccourcis clavier essentiels

---

## 1. Comment Claude Code fonctionne

### 1.1 L'architecture

Claude Code n'est **pas** un simple chat. C'est un **agent autonome** qui utilise des outils :

```
Vous tapez un prompt
        │
        ▼
┌───────────────────┐
│   Claude Code     │
│   (Agent IA)      │
│                   │
│  "J'ai besoin de  │
│   lire ce fichier"│
│        │          │
│        ▼          │
│  ┌────────────┐   │     ┌──────────────────┐
│  │  Outil:    │───┼────▶│  Votre système   │
│  │  Read      │   │     │  de fichiers     │
│  └────────────┘   │     └──────────────────┘
│        │          │
│        ▼          │
│  "Maintenant je   │
│   dois modifier"  │
│        │          │
│        ▼          │
│  ┌────────────┐   │     ┌──────────────────┐
│  │  Outil:    │───┼────▶│  Votre système   │
│  │  Edit      │   │     │  de fichiers     │
│  └────────────┘   │     └──────────────────┘
│        │          │
│        ▼          │
│  "Résultat final" │
└───────────────────┘
        │
        ▼
  Réponse affichée
```

### 1.2 Les outils internes

Claude Code dispose d'un arsenal d'outils qu'il utilise automatiquement :

| Outil | Fonction | Exemple |
|-------|----------|---------|
| **Read** | Lire un fichier | Lire `src/app.py` |
| **Write** | Créer un fichier | Créer `tests/test_app.py` |
| **Edit** | Modifier un fichier | Changer une ligne dans un fichier existant |
| **Glob** | Chercher des fichiers par nom | Trouver tous les `*.py` |
| **Grep** | Chercher dans le contenu | Trouver "TODO" dans le code |
| **Bash** | Exécuter des commandes | `npm test`, `git status` |
| **Task** | Lancer des sous-agents | Recherche parallèle dans un gros codebase |
| **WebFetch** | Récupérer du contenu web | Lire une documentation en ligne |
| **WebSearch** | Rechercher sur le web | Chercher une solution à une erreur |

> **Point clé** : Vous ne choisissez pas quel outil utiliser. Claude Code décide automatiquement en fonction de votre demande.

### 1.3 Le système de "turns"

Chaque interaction = une série de **tours** (turns) :

```
Turn 1 : Claude lit votre prompt, décide d'utiliser Glob
Turn 2 : Claude reçoit les résultats de Glob, utilise Read
Turn 3 : Claude reçoit le contenu, utilise Edit
Turn 4 : Claude confirme la modification, vous répond
```

Claude Code peut enchaîner **des dizaines de turns** automatiquement pour accomplir des tâches complexes.

---

## 2. Les types de prompts

### 2.1 Questions simples

```
> Que fait la fonction calculateTotal dans ce projet ?
```

Claude va chercher la fonction, la lire, et vous expliquer.

### 2.2 Demandes de modification

```
> Ajoute une validation email dans le formulaire d'inscription
```

Claude va :
1. Trouver le formulaire
2. Comprendre le code existant
3. Ajouter la validation
4. Vous montrer les changements

### 2.3 Demandes complexes multi-étapes

```
> Refactore le module d'authentification pour utiliser JWT au lieu des sessions,
> mets à jour les tests, et crée une migration pour la base de données
```

Claude va planifier et exécuter chaque étape séquentiellement.

### 2.4 Prompts multi-lignes

Pour écrire un prompt sur plusieurs lignes, utilisez `Shift+Enter` ou `\` en fin de ligne :

```
> Je veux que tu crées une API REST avec :     (Shift+Enter)
> - Un endpoint GET /users                      (Shift+Enter)
> - Un endpoint POST /users                     (Shift+Enter)
> - Validation avec Pydantic                    (Enter pour envoyer)
```

---

## 3. Comprendre les outputs

### 3.1 Les indicateurs d'outils

Quand Claude Code utilise un outil, vous voyez :

```
● Read src/app.py                          ← Lecture de fichier
● Glob **/*.py                             ← Recherche de fichiers
● Bash npm test                            ← Exécution de commande
● Edit src/app.py                          ← Modification de fichier
  ├─ old_string: "def hello():"
  └─ new_string: "def hello(name: str):"
```

### 3.2 Les demandes de permission

Claude Code **demande votre autorisation** avant certaines actions :

```
Claude wants to run: npm install express

Allow? (y/n/always)
```

- **y** : Autoriser cette fois
- **n** : Refuser
- **always** : Toujours autoriser cette commande

### 3.3 Les diffs

Quand Claude modifie un fichier, il montre un diff :

```diff
- def calculate(a, b):
-     return a + b
+ def calculate(a: int, b: int) -> int:
+     """Additionne deux entiers."""
+     return a + b
```

---

## 4. Raccourcis clavier essentiels

| Raccourci | Action |
|-----------|--------|
| `Entrée` | Envoyer le message |
| `Shift+Entrée` | Nouvelle ligne (multi-ligne) |
| `Escape` | Annuler l'action en cours / Quitter |
| `Escape` (x2) | Annuler en cours de génération |
| `Tab` | Autocomplétion des fichiers dans le prompt |
| `Ctrl+C` | Interrompre Claude Code |
| `Ctrl+L` | Effacer l'écran |
| `↑` / `↓` | Naviguer dans l'historique des prompts |

---

## 5. Le contexte de travail

### 5.1 Le répertoire de travail

Claude Code travaille **toujours** relativement au répertoire courant :

```bash
# Claude Code voit TOUT le projet
cd ~/mon-projet
claude

# Claude Code ne voit QUE le sous-dossier
cd ~/mon-projet/src/api
claude
```

> **Bonne pratique** : Lancez toujours Claude Code depuis la **racine** de votre projet.

### 5.2 La fenêtre de contexte

Claude Code a une **fenêtre de contexte** limitée (200K tokens pour Sonnet). Quand la conversation devient longue :

```
Début de conversation                    Conversation longue
┌─────────────────────┐                 ┌─────────────────────┐
│ Message 1           │                 │ [Messages anciens   │
│ Message 2           │                 │  compressés auto-   │
│ Message 3           │                 │  matiquement]       │
│                     │                 │ Message 47          │
│ [Espace libre]      │                 │ Message 48          │
│                     │                 │ Message 49          │
│                     │                 │ Message 50          │
└─────────────────────┘                 └─────────────────────┘
```

Claude Code **compresse automatiquement** les anciens messages. Si vous sentez qu'il "oublie" des choses, c'est normal sur les très longues sessions.

### 5.3 Démarrer une nouvelle conversation

```bash
# Nouvelle conversation propre
claude

# Reprendre la dernière conversation
claude --continue

# Reprendre avec un prompt
claude --continue "maintenant ajoute les tests"

# Lister les conversations récentes
claude --resume
```

---

## 6. Les modes de sortie

### 6.1 Mode interactif (par défaut)

```bash
claude
# Vous êtes dans le REPL, tapez vos prompts un par un
```

### 6.2 Mode one-shot

```bash
# Exécuter une seule commande et quitter
claude "combien de fichiers Python dans ce projet ?"

# Avec un pipe
echo "explique ce code" | claude

# Depuis un fichier
claude < prompt.txt
```

### 6.3 Mode print (pas d'outils, juste du texte)

```bash
# Claude répond sans utiliser d'outils (pas de lecture de fichiers, etc.)
claude -p "explique-moi les design patterns"

# Utile pour des questions générales qui ne concernent pas le projet
```

---

## 7. Exercices pratiques

### Exercice 1 : Explorer un projet
```
> Donne-moi la structure de ce projet avec les technologies utilisées
```

### Exercice 2 : Chercher du code
```
> Trouve toutes les fonctions qui n'ont pas de docstring dans ce projet
```

### Exercice 3 : Comprendre du code
```
> Explique-moi le flux d'exécution quand un utilisateur se connecte
```

### Exercice 4 : Multi-lignes
```
> Je veux comprendre :
> 1. Comment les routes sont organisées
> 2. Où sont les middlewares
> 3. Comment la base de données est connectée
```

### Exercice 5 : One-shot
```bash
claude "liste tous les TODO dans le code" > todos.txt
```

---

## Résumé

```
Claude Code = Agent IA avec des Outils
│
├── Outils : Read, Write, Edit, Glob, Grep, Bash, Task...
├── Cycle  : Prompt → Outils → Réponse (multi-turns)
├── Modes  : Interactif / One-shot / Print
├── Input  : Multi-lignes avec Shift+Enter
├── Output : Diffs, permissions, indicateurs d'outils
└── Contexte : Basé sur le répertoire courant
```

> **Prochain chapitre** : [Les Commandes Slash & Navigation](03-commandes-slash.md)
