# Chapitre 4 : Gestion de Fichiers & Codebase

## Objectifs

- Maîtriser la lecture, l'écriture et la modification de fichiers
- Comprendre comment Claude Code explore un codebase
- Savoir guider Claude Code vers les bons fichiers
- Apprendre à gérer les gros projets efficacement

---

## 1. Comment Claude Code voit votre projet

### 1.1 La découverte automatique

Quand vous lancez Claude Code, il **ne lit PAS** tout votre projet d'un coup. Il explore **à la demande** :

```
Étape 1 : Vous posez une question
          "Comment fonctionne l'authentification ?"

Étape 2 : Claude explore
          Glob("**/auth*")  → trouve src/auth/, middleware/auth.js
          Read(src/auth/index.js)  → lit le fichier principal
          Grep("login", "**/*.js")  → cherche les références
          Read(src/auth/jwt.js)  → lit un fichier connexe

Étape 3 : Claude comprend et répond
          "L'authentification utilise JWT avec..."
```

### 1.2 Ce que Claude Code respecte

```
Fichiers ignorés automatiquement
├── .gitignore          → Tout ce qui est ignoré par Git
├── node_modules/       → Jamais lu
├── .git/               → Jamais lu
├── dist/ build/        → Ignorés si dans .gitignore
└── Fichiers binaires   → Images, PDFs, .pyc, etc.
```

---

## 2. Lire des fichiers

### 2.1 Lecture implicite

```
> Que fait le fichier src/app.py ?
```

Claude va automatiquement lire le fichier et vous l'expliquer.

### 2.2 Lecture explicite avec @

```
> Lis @src/config/database.yml et dis-moi les paramètres de connexion
```

### 2.3 Lecture de plusieurs fichiers

```
> Compare @src/api/v1/users.py et @src/api/v2/users.py
> Quelles sont les différences ?
```

### 2.4 Lire des images

Claude Code est **multimodal** — il peut lire des images :

```
> Regarde @mockup.png et implémente ce design en HTML/CSS
```

---

## 3. Rechercher dans le codebase

### 3.1 Recherche par nom de fichier (Glob)

```
> Trouve tous les fichiers de test dans le projet
```
Claude utilise : `Glob("**/test_*.py")` ou `Glob("**/*.test.js")`

### 3.2 Recherche par contenu (Grep)

```
> Trouve tous les endroits où on utilise deprecated_function()
```
Claude utilise : `Grep("deprecated_function", "**/*.py")`

### 3.3 Recherche sémantique (le vrai pouvoir)

```
> Où est-ce que la validation des emails est implémentée ?
```

Claude ne cherche pas juste le mot "email" — il comprend le **concept** et cherche intelligemment :
- `Grep("email.*valid", "**/*.py")`
- `Grep("is_valid_email", "**/*.py")`
- `Glob("**/validators*")`
- etc.

### 3.4 Astuce : Guider la recherche

Si Claude ne trouve pas, aidez-le :

```
# Trop vague
> Où est le bug ?

# Beaucoup mieux
> Il y a un bug dans le calcul des taxes dans le module de facturation.
> Le total TTC est parfois négatif. Cherche dans src/billing/
```

---

## 4. Modifier des fichiers

### 4.1 L'outil Edit (remplacement ciblé)

Claude Code utilise **Edit** pour des modifications chirurgicales :

```python
# Avant
def greet():
    print("hello")

# Prompt : "Ajoute un paramètre name à la fonction greet"

# Claude exécute :
# Edit(
#   file: "src/app.py",
#   old: 'def greet():\n    print("hello")',
#   new: 'def greet(name: str):\n    print(f"hello {name}")'
# )

# Après
def greet(name: str):
    print(f"hello {name}")
```

### 4.2 L'outil Write (création de fichier)

Pour les **nouveaux fichiers**, Claude utilise Write :

```
> Crée un fichier de configuration Docker pour ce projet Python
```

Claude crée `Dockerfile` avec le contenu approprié.

### 4.3 Modifications en masse

```
> Renomme toutes les variables camelCase en snake_case dans src/utils/
```

Claude va :
1. Lister les fichiers dans `src/utils/`
2. Lire chaque fichier
3. Identifier les variables camelCase
4. Les remplacer une par une avec Edit

### 4.4 Validation des modifications

Toujours vérifier après une modification :

```
> Montre-moi le diff des changements que tu viens de faire
```

Ou mieux :

```
> Lance les tests pour vérifier que tes modifications n'ont rien cassé
```

---

## 5. Patterns efficaces pour gros codebase

### 5.1 Le problème des gros projets

```
Petit projet (< 50 fichiers)     Gros projet (> 1000 fichiers)
┌─────────────────────┐          ┌─────────────────────────────────┐
│ Claude peut explorer │          │ Claude doit être guidé          │
│ efficacement tout    │          │                                 │
│ seul                 │          │ Trop de fichiers à explorer     │
│                      │          │ Risque de se perdre             │
│                      │          │ Contexte limité                 │
└─────────────────────┘          └─────────────────────────────────┘
```

### 5.2 Stratégies pour gros projets

**Stratégie 1 : Pointer vers le bon dossier**
```
> Dans le dossier src/payments/, explique-moi le flux de paiement
```

**Stratégie 2 : Nommer les fichiers clés**
```
> Regarde @src/payments/stripe.py et @src/payments/webhook.py
> Comment le webhook confirme-t-il le paiement ?
```

**Stratégie 3 : Utiliser CLAUDE.md** (voir chapitre 7)
```markdown
# Architecture
- src/payments/ : Module de paiement (Stripe)
- src/auth/     : Authentification (JWT)
- src/api/      : Routes API (FastAPI)
```

**Stratégie 4 : Le mode Plan**

Pour les tâches complexes, demandez à Claude de **planifier avant d'agir** :

```
> Je veux ajouter le support des webhooks Stripe.
> Avant de coder, analyse le projet et propose-moi un plan.
```

---

## 6. Gestion des erreurs courantes

### 6.1 "Je ne trouve pas ce fichier"

```
# Claude ne trouve pas ? Donnez le chemin exact
> Le fichier est dans src/legacy/old_auth.py
```

### 6.2 "Le fichier est trop gros"

Claude peut lire des gros fichiers mais le contexte a des limites :

```
# Pour un gros fichier
> Lis seulement les lignes 100 à 200 de @src/big_file.py
```

### 6.3 Modifications qui échouent

L'outil Edit échoue si le texte à remplacer n'est pas trouvé exactement :

```
# Si Claude rate un Edit, il va :
# 1. Re-lire le fichier pour voir l'état actuel
# 2. Réessayer avec le bon contenu
# C'est automatique, vous n'avez rien à faire
```

---

## 7. Exercices pratiques

### Exercice 1 : Exploration
```
> Donne-moi un inventaire complet de ce projet :
> - Langages utilisés
> - Frameworks
> - Structure des dossiers
> - Points d'entrée
```

### Exercice 2 : Recherche ciblée
```
> Trouve tous les endpoints API de ce projet et liste-les
> avec leur méthode HTTP et leur URL
```

### Exercice 3 : Modification simple
```
> Ajoute des type hints à toutes les fonctions dans src/utils.py
```

### Exercice 4 : Création
```
> Crée un fichier .env.example avec toutes les variables
> d'environnement utilisées dans ce projet
```

### Exercice 5 : Refactoring
```
> Extrais la logique de validation de src/api/routes.py
> dans un nouveau fichier src/validators.py
```

---

## Résumé

```
Gestion Fichiers Claude Code
│
├── Lecture   : Automatique, @fichier, images
├── Recherche : Glob (noms), Grep (contenu), sémantique
├── Écriture  : Write (nouveau), Edit (modifier)
├── Gros projets : Pointer, nommer, CLAUDE.md, planifier
└── Erreurs   : Claude retente automatiquement
```

> **Prochain chapitre** : [Git & GitHub Intégré](05-git-github.md)
