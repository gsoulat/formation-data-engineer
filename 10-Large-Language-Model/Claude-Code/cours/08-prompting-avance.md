# Chapitre 8 : Prompting Avancé & Bonnes Pratiques

## Objectifs

- Écrire des prompts qui produisent exactement le résultat voulu
- Connaître les patterns de prompting les plus efficaces
- Éviter les erreurs courantes de prompting
- Maîtriser le prompting itératif pour les tâches complexes

---

## 1. Les niveaux de prompting

```
Niveau 1 : Vague              "Corrige le bug"
Niveau 2 : Précis             "Corrige le bug de calcul TVA dans billing.py"
Niveau 3 : Contextuel         "Le bug : la TVA est calculée avant la remise.
                                Corrige billing.py ligne ~45 pour appliquer
                                la remise AVANT la TVA."
Niveau 4 : Expert             "Dans billing.py, la fonction calculate_total()
                                applique la TVA (20%) sur le prix brut, puis
                                soustrait la remise. Le bon ordre est :
                                prix_net = prix - remise, puis total = prix_net * 1.20
                                Corrige et ajoute un test unitaire qui vérifie
                                les deux cas (avec et sans remise)."

Qualité du résultat :  ████░░░░░░  ██████░░░░  ████████░░  ██████████
```

---

## 2. Les 7 patterns de prompting essentiels

### Pattern 1 : Le Contexte-Action-Contrainte (CAC)

```
> **Contexte** : Notre API FastAPI renvoie des erreurs 500 quand
> la base de données est down.
>
> **Action** : Ajoute un middleware de health-check et un fallback
> qui renvoie une 503 avec un message explicite.
>
> **Contrainte** : Utilise le pattern existant dans src/middleware/
> et ajoute un test.
```

### Pattern 2 : Le "Regarde d'abord"

```
> Avant de modifier quoi que ce soit :
> 1. Lis src/auth/ et comprends comment l'auth fonctionne
> 2. Lis les tests existants
> 3. Explique-moi ta compréhension
> 4. Ensuite seulement, propose les changements
```

> **Pourquoi** : Claude Code est parfois trop empressé de modifier. Lui demander de comprendre d'abord donne de bien meilleurs résultats.

### Pattern 3 : Le Plan Avant l'Action

```
> Je veux migrer de REST à GraphQL.
> NE CODE PAS ENCORE.
> Propose-moi un plan en étapes avec les fichiers à modifier.
```

Claude va entrer en mode planification et vous présenter un plan structuré avant de toucher au code.

### Pattern 4 : L'exemple guidé

```
> Crée un nouveau endpoint POST /api/orders similaire à
> ce qui est fait dans @src/api/users.py pour POST /api/users.
> Suis exactement le même pattern : validation Pydantic,
> service layer, repository, et test.
```

### Pattern 5 : Le correctif ciblé

```
> Dans @src/utils/date.py ligne 23, la fonction parse_date
> ne gère pas le format ISO 8601 avec timezone.
> Corrige UNIQUEMENT cette fonction, ne touche à rien d'autre.
```

### Pattern 6 : Le multi-étapes séquentiel

```
> Étape par étape :
> 1. Crée le modèle Order dans src/models/
> 2. Crée le schéma Pydantic dans src/schemas/
> 3. Crée le repository dans src/repositories/
> 4. Crée le service dans src/services/
> 5. Crée la route dans src/api/
> 6. Crée les tests
>
> Montre-moi chaque étape et attends ma validation avant
> de passer à la suivante.
```

### Pattern 7 : Le "Comme un senior"

```
> Fais une review de @src/payments/stripe.py comme si tu étais
> un développeur senior spécialisé en sécurité des paiements.
> Focus sur : injection, validation des montants, gestion des erreurs Stripe.
```

---

## 3. Prompts par type de tâche

### 3.1 Debugging

```
# Mauvais
> Ça marche pas

# Bon
> L'endpoint POST /api/users renvoie une 422 quand j'envoie
> { "name": "Jean", "email": "jean@test.com" }.
> L'erreur dit "field required: password" mais le password
> devrait être optionnel pour les comptes OAuth.
> Vérifie le schéma Pydantic dans src/schemas/user.py.
```

### 3.2 Refactoring

```
# Mauvais
> Refactore ce fichier

# Bon
> src/services/order.py fait 500 lignes avec trop de responsabilités.
> Extrais :
> 1. La validation dans un validateur dédié
> 2. Les notifications email dans un service séparé
> 3. Le calcul de prix dans un module pricing
> Garde la même interface publique pour ne rien casser.
```

### 3.3 Tests

```
# Mauvais
> Ajoute des tests

# Bon
> Crée des tests unitaires pour src/services/pricing.py :
> - Test avec prix normal (100€, TVA 20% → 120€)
> - Test avec remise (100€, -10%, TVA → 108€)
> - Test avec remise qui dépasse le prix (edge case)
> - Test avec montant négatif (doit lever ValueError)
> Utilise pytest avec les fixtures de conftest.py
```

### 3.4 Documentation

```
# Mauvais
> Documente le code

# Bon
> Ajoute des docstrings Google-style aux fonctions publiques de
> src/services/pricing.py. Inclus :
> - Description d'une ligne
> - Args avec types
> - Returns
> - Raises
> - Un exemple d'utilisation
```

---

## 4. Techniques avancées

### 4.1 Le prompting itératif

Ne faites pas tout en un seul prompt. Itérez :

```
Tour 1 : > Explique-moi l'architecture du module auth
Tour 2 : > Ok, maintenant propose-moi comment ajouter le 2FA
Tour 3 : > J'aime l'approche TOTP. Implémente-le.
Tour 4 : > Ajoute les tests
Tour 5 : > /review
Tour 6 : > /commit
```

### 4.2 Les "stop words"

Dites à Claude quand s'arrêter :

```
> Implémente la validation. STOP si tu as besoin d'informations
> que tu ne trouves pas dans le code.
```

### 4.3 Le feedback négatif constructif

```
# Mauvais
> Non c'est nul, refais

# Bon
> Le résultat n'est pas ce que je voulais. Problèmes :
> 1. Tu as utilisé une classe mais je préfère des fonctions pures
> 2. Le nommage n'est pas cohérent avec le reste du projet
> 3. Il manque la gestion des cas d'erreur
> Reprends en corrigeant ces 3 points.
```

### 4.4 Le prompt "diff mental"

```
> Voici ce que j'ai actuellement :
> - L'utilisateur se connecte → session créée → cookie
>
> Voici ce que je veux :
> - L'utilisateur se connecte → JWT généré → header Authorization
>
> Fais la transition en gardant une rétro-compatibilité temporaire
> (les deux systèmes fonctionnent pendant la migration).
```

### 4.5 Le multi-fichier coordonné

```
> Je veux ajouter un système de notifications. Voici les fichiers
> à créer/modifier :
>
> CRÉER :
> - src/models/notification.py (modèle SQLAlchemy)
> - src/services/notification.py (logique d'envoi)
> - src/api/notifications.py (routes)
>
> MODIFIER :
> - src/services/order.py (envoyer une notif quand commande créée)
> - src/models/__init__.py (exporter le nouveau modèle)
>
> Commence par les créations, puis les modifications.
```

---

## 5. Les erreurs à éviter

### 5.1 Le prompt trop vague

```
❌ "Améliore ce code"
   → Claude ne sait pas QUOI améliorer

✅ "Améliore la performance de la requête SQL dans get_users() :
    elle fait un N+1 sur les rôles."
```

### 5.2 Le prompt trop long

```
❌ [3 paragraphes de contexte + 15 requirements + 8 contraintes]
   → Claude peut oublier des éléments

✅ Découpez en plusieurs étapes claires
```

### 5.3 Le micromanagement

```
❌ "À la ligne 42, remplace le = par ==, puis à la ligne 57
    ajoute un espace après la virgule..."
   → Autant le faire vous-même

✅ "Corrige les erreurs de syntaxe dans src/app.py"
   → Laissez Claude trouver et corriger
```

### 5.4 L'imprécision sur le scope

```
❌ "Mets à jour l'API"
   → Toute l'API ? Un endpoint ? Quoi exactement ?

✅ "Mets à jour l'endpoint GET /api/users pour supporter
    la pagination avec les paramètres page et limit"
```

---

## 6. Le méta-prompting

### 6.1 Demander à Claude comment l'utiliser

```
> Je veux implémenter un système de cache Redis dans ce projet.
> Avant de coder, dis-moi :
> 1. Quelles infos as-tu besoin de ma part ?
> 2. Quels fichiers devrais-tu lire d'abord ?
> 3. Quel serait le meilleur plan d'action ?
```

### 6.2 Le "rubber duck" IA

```
> Je ne suis pas sûr de mon approche. J'hésite entre :
> A) Un cache au niveau du service
> B) Un cache au niveau du repository
> C) Un middleware de cache HTTP
>
> Quels sont les avantages/inconvénients de chaque approche
> dans le contexte de CE projet ?
```

---

## 7. Tableau récapitulatif

| Situation | Pattern recommandé |
|-----------|-------------------|
| Nouveau feature | Plan Avant l'Action |
| Bug fix | Contexte-Action-Contrainte |
| Refactoring | Regarde d'abord + Multi-étapes |
| Tests | Exemple guidé + Cas précis |
| Architecture | Rubber duck + Plan |
| Review | Comme un senior |
| Migration | Diff mental |

---

## Exercices pratiques

### Exercice 1 : Réécrire un mauvais prompt
Transformez ce prompt vague en prompt expert :
```
"Ajoute de la sécurité à l'API"
```

### Exercice 2 : Prompt itératif
1. Choisissez une feature à ajouter
2. Écrivez 5 prompts séquentiels (comprendre → planifier → implémenter → tester → review)
3. Exécutez-les un par un

### Exercice 3 : Le pattern CAC
Pour 3 tâches différentes, écrivez un prompt suivant le pattern Contexte-Action-Contrainte.

---

## Résumé

```
Prompting Avancé
│
├── 7 Patterns
│   ├── CAC (Contexte-Action-Contrainte)
│   ├── Regarde d'abord
│   ├── Plan avant l'action
│   ├── Exemple guidé
│   ├── Correctif ciblé
│   ├── Multi-étapes séquentiel
│   └── Comme un senior
│
├── Techniques
│   ├── Itératif (plusieurs tours)
│   ├── Stop words
│   ├── Feedback constructif
│   ├── Diff mental
│   └── Méta-prompting
│
└── Erreurs à éviter
    ├── Trop vague
    ├── Trop long
    ├── Micromanagement
    └── Scope imprécis
```

> **Prochain chapitre** : [MCP Servers & Extensibilité](09-mcp-servers.md)
