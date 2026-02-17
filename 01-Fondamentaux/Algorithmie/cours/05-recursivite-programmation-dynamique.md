# Module 05 — Récursivité et programmation dynamique

## 🎯 Objectifs

- Comprendre le principe de la récursivité et savoir l'appliquer
- Identifier les cas de base et les cas récursifs
- Comprendre les limites de la récursivité naïve
- Maîtriser la mémoïsation pour optimiser les algorithmes récursifs
- Comprendre la programmation dynamique (approche bottom-up)
- Résoudre des problèmes classiques avec ces techniques

---

## 1. 🔄 La récursivité

### 1.1 Définition

Un algorithme est **récursif** quand il s'appelle lui-même pour résoudre des sous-problèmes plus petits.

Toute fonction récursive a deux composantes :
1. **Cas de base** : la condition d'arrêt (sans récursion)
2. **Cas récursif** : l'appel à soi-même avec un sous-problème réduit

> 💡 **Analogie** : Les poupées russes. Chaque poupée contient une version plus petite d'elle-même, jusqu'à la plus petite (cas de base).

### 1.2 Premier exemple : factorielle

```
n! = n × (n-1) × (n-2) × ... × 1
5! = 5 × 4 × 3 × 2 × 1 = 120

Décomposition récursive :
5! = 5 × 4!
4! = 4 × 3!
3! = 3 × 2!
2! = 2 × 1!
1! = 1          ← cas de base
```

```python
def factorielle(n: int) -> int:
    """Calcule n! récursivement."""
    # Cas de base
    if n <= 1:
        return 1
    # Cas récursif
    return n * factorielle(n - 1)


print(factorielle(5))  # 120
```

### 1.3 Visualisation de la pile d'appels

```
factorielle(5)
  → 5 * factorielle(4)
    → 4 * factorielle(3)
      → 3 * factorielle(2)
        → 2 * factorielle(1)
          → return 1          ← cas de base atteint
        → return 2 * 1 = 2
      → return 3 * 2 = 6
    → return 4 * 6 = 24
  → return 5 * 24 = 120
```

> ⚠️ **Attention** : Chaque appel récursif ajoute un cadre (frame) à la **pile d'appels**. Python limite cette pile à ~1000 appels par défaut (`RecursionError`).

### 1.4 Règles pour écrire un algorithme récursif

1. **Définir le cas de base** — Quand s'arrêter ?
2. **Définir le cas récursif** — Comment réduire le problème ?
3. **Vérifier la convergence** — Chaque appel rapproche-t-il du cas de base ?
4. **Vérifier qu'il n'y a pas de travail redondant** — Sinon, optimiser

### 1.5 Exemples classiques

#### Somme des éléments d'une liste

```python
def somme_recursive(liste: list) -> int:
    """Somme récursive — O(n)."""
    if not liste:           # Cas de base : liste vide
        return 0
    return liste[0] + somme_recursive(liste[1:])  # Cas récursif


print(somme_recursive([1, 2, 3, 4, 5]))  # 15
```

#### Puissance

```python
def puissance(base: int, exposant: int) -> int:
    """Calcule base^exposant récursivement — O(n)."""
    if exposant == 0:
        return 1
    return base * puissance(base, exposant - 1)


print(puissance(2, 10))  # 1024
```

#### Puissance rapide (exponentiation rapide)

```python
def puissance_rapide(base: int, exposant: int) -> int:
    """Calcule base^exposant en O(log n) — diviser pour régner."""
    if exposant == 0:
        return 1
    if exposant % 2 == 0:
        demi = puissance_rapide(base, exposant // 2)
        return demi * demi
    else:
        return base * puissance_rapide(base, exposant - 1)


print(puissance_rapide(2, 10))  # 1024
```

> 💡 L'exponentiation rapide réduit la complexité de O(n) à O(log n) en divisant l'exposant par 2 à chaque étape.

---

## 2. 🐌 Le problème de la récursivité naïve : Fibonacci

### 2.1 Fibonacci naïf

```
F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2)

Séquence : 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
```

```python
def fibonacci_naif(n: int) -> int:
    """Fibonacci récursif naïf — O(2^n) ⚠️ LENT."""
    if n <= 1:
        return n
    return fibonacci_naif(n - 1) + fibonacci_naif(n - 2)


# Fonctionne mais TRÈS lent pour n > 35
print(fibonacci_naif(10))  # 55
```

### 2.2 Pourquoi c'est lent ?

L'arbre d'appels montre des **calculs redondants** massifs :

```
                     fib(5)
                    /      \
               fib(4)      fib(3)
              /     \       /    \
          fib(3)  fib(2)  fib(2) fib(1)
          /   \    /  \    /  \
      fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)
      /   \
  fib(1) fib(0)
```

- `fib(3)` est calculé **2 fois**
- `fib(2)` est calculé **3 fois**
- `fib(1)` est calculé **5 fois**

Pour `fib(n)`, la complexité est **O(2ⁿ)** — exponentielle !

| n | Appels récursifs |
|---|-----------------|
| 10 | 177 |
| 20 | 21 891 |
| 30 | 2 692 537 |
| 40 | 331 160 281 |
| 50 | ~40 milliards |

---

## 3. 💾 La mémoïsation (top-down)

### 3.1 Principe

La **mémoïsation** consiste à stocker les résultats déjà calculés dans un cache (dictionnaire) pour éviter les calculs redondants.

C'est l'approche **top-down** : on commence par le problème principal et on descend récursivement, en cachant les résultats au passage.

### 3.2 Fibonacci avec mémoïsation manuelle

```python
def fibonacci_memo(n: int, cache: dict | None = None) -> int:
    """Fibonacci avec mémoïsation — O(n)."""
    if cache is None:
        cache = {}

    if n in cache:
        return cache[n]

    if n <= 1:
        return n

    cache[n] = fibonacci_memo(n - 1, cache) + fibonacci_memo(n - 2, cache)
    return cache[n]


print(fibonacci_memo(50))  # 12586269025 — instantané !
```

### 3.3 Avec `functools.lru_cache`

Python fournit un décorateur pour automatiser la mémoïsation :

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fibonacci_cache(n: int) -> int:
    """Fibonacci avec lru_cache — O(n)."""
    if n <= 1:
        return n
    return fibonacci_cache(n - 1) + fibonacci_cache(n - 2)


print(fibonacci_cache(100))  # 354224848179261915075 — instantané !
```

### 3.4 Impact de la mémoïsation

```
Sans mémoïsation (fib(5)) :         Avec mémoïsation (fib(5)) :

         fib(5)                              fib(5)
        /      \                            /      \
    fib(4)    fib(3)                    fib(4)    fib(3) ← cache
    /    \     /   \                    /    \
fib(3) fib(2) ...  ...             fib(3) fib(2) ← cache
  ...    ...                        /   \
                                fib(2) fib(1)
                                /   \
                            fib(1) fib(0)

15 appels                          9 appels (et croît linéairement)
```

| Approche | Complexité temps | Complexité espace |
|----------|-----------------|-------------------|
| Naïve | O(2ⁿ) | O(n) — pile |
| Mémoïsation | O(n) | O(n) — pile + cache |

---

## 4. 📐 Programmation dynamique (bottom-up)

### 4.1 Principe

La **programmation dynamique** (PD) résout le problème en partant des **sous-problèmes les plus simples** et en construisant la solution vers le haut.

C'est l'approche **bottom-up** : on remplit un tableau de manière itérative.

> 💡 **Différence avec la mémoïsation** : la mémoïsation est top-down (récursive), la PD est bottom-up (itérative). Les deux évitent les calculs redondants.

### 4.2 Fibonacci en programmation dynamique

```python
def fibonacci_dp(n: int) -> int:
    """Fibonacci en programmation dynamique — O(n) temps, O(n) espace."""
    if n <= 1:
        return n

    dp = [0] * (n + 1)
    dp[0] = 0
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


print(fibonacci_dp(50))  # 12586269025
```

### 4.3 Optimisation de l'espace

On n'a besoin que des **deux dernières valeurs**, pas de tout le tableau :

```python
def fibonacci_optimal(n: int) -> int:
    """Fibonacci optimisé — O(n) temps, O(1) espace."""
    if n <= 1:
        return n

    precedent, courant = 0, 1
    for _ in range(2, n + 1):
        precedent, courant = courant, precedent + courant

    return courant


print(fibonacci_optimal(50))  # 12586269025
```

### 4.4 Quand utiliser la programmation dynamique ?

Un problème est adapté à la PD quand il possède :

1. **Sous-structure optimale** : la solution optimale contient les solutions optimales des sous-problèmes
2. **Sous-problèmes chevauchants** : les mêmes sous-problèmes sont résolus plusieurs fois

---

## 5. 🎒 Problèmes classiques

### 5.1 Le problème du sac à dos (Knapsack)

**Énoncé** : On a un sac à dos de capacité `W` et `n` objets, chacun avec un poids et une valeur. Maximiser la valeur totale sans dépasser la capacité.

```python
def sac_a_dos(capacite: int, poids: list[int], valeurs: list[int]) -> int:
    """Sac à dos 0/1 — programmation dynamique — O(n × W)."""
    n = len(poids)
    # dp[i][w] = valeur maximale avec les i premiers objets et capacité w
    dp = [[0] * (capacite + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacite + 1):
            # Ne pas prendre l'objet i
            dp[i][w] = dp[i - 1][w]
            # Prendre l'objet i (si possible)
            if poids[i - 1] <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i - 1][w - poids[i - 1]] + valeurs[i - 1],
                )

    return dp[n][capacite]


# Exemple
poids =   [2, 3, 4, 5]
valeurs = [3, 4, 5, 6]
capacite = 8

print(sac_a_dos(capacite, poids, valeurs))  # 10 (objets 1+3 : poids 2+4=6, valeur 3+5=8... non)
# En fait : objets de poids 3+5=8, valeur 4+6=10
```

### 5.2 Plus longue sous-séquence commune (LCS)

**Énoncé** : Trouver la plus longue sous-séquence commune à deux chaînes.

```
"ABCBDAB" et "BDCAB"
LCS = "BCAB" (longueur 4)
```

```python
def lcs(texte1: str, texte2: str) -> int:
    """Plus longue sous-séquence commune — O(m × n)."""
    m, n = len(texte1), len(texte2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if texte1[i - 1] == texte2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


print(lcs("ABCBDAB", "BDCAB"))  # 4
```

> 💡 **Pour le Data Engineer** : Le LCS est utilisé dans les outils de diff (comme `git diff`) pour comparer deux versions d'un fichier.

### 5.3 Montée d'escalier

**Énoncé** : On peut monter 1 ou 2 marches à la fois. Combien de façons pour atteindre la marche n ?

```python
def monter_escalier(n: int) -> int:
    """Nombre de façons de monter n marches — O(n)."""
    if n <= 2:
        return n

    precedent, courant = 1, 2
    for _ in range(3, n + 1):
        precedent, courant = courant, precedent + courant

    return courant


# C'est en fait Fibonacci décalé !
print(monter_escalier(5))   # 8 façons
print(monter_escalier(10))  # 89 façons
```

### 5.4 Distance d'édition (Levenshtein)

**Énoncé** : Nombre minimum d'opérations (insertion, suppression, remplacement) pour transformer une chaîne en une autre.

```python
def distance_edition(mot1: str, mot2: str) -> int:
    """Distance de Levenshtein — O(m × n)."""
    m, n = len(mot1), len(mot2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Cas de base : transformer une chaîne vide
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if mot1[i - 1] == mot2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # Pas d'opération
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # Suppression
                    dp[i][j - 1],      # Insertion
                    dp[i - 1][j - 1],  # Remplacement
                )

    return dp[m][n]


print(distance_edition("kitten", "sitting"))  # 3
# kitten → sitten (remplacement k→s)
# sitten → sittin (remplacement e→i)
# sittin → sitting (insertion g)
```

> 💡 **Pour le Data Engineer** : La distance de Levenshtein est utilisée pour le **fuzzy matching** — rapprocher des données similaires mais pas identiques (ex : "Jhon Smith" → "John Smith").

---

## 6. 📋 Méthodologie pour résoudre un problème de PD

### 6.1 Les 5 étapes

```
┌─────────────────────────────────────────────┐
│  1. Identifier les sous-problèmes           │
│     → Que calcule-t-on ? Quels paramètres ? │
├─────────────────────────────────────────────┤
│  2. Définir la relation de récurrence        │
│     → Comment un sous-problème dépend des   │
│       sous-problèmes plus petits ?          │
├─────────────────────────────────────────────┤
│  3. Identifier les cas de base               │
│     → Quels sont les sous-problèmes triviaux│
├─────────────────────────────────────────────┤
│  4. Choisir l'approche                       │
│     → Top-down (mémoïsation) ou             │
│       Bottom-up (tableau) ?                 │
├─────────────────────────────────────────────┤
│  5. Optimiser l'espace si possible           │
│     → Peut-on ne garder que les dernières   │
│       lignes/valeurs ?                      │
└─────────────────────────────────────────────┘
```

### 6.2 Comparaison top-down vs bottom-up

| Aspect | Mémoïsation (top-down) | PD (bottom-up) |
|--------|----------------------|----------------|
| **Style** | Récursif + cache | Itératif + tableau |
| **Facilité** | Plus intuitif | Nécessite de penser au remplissage |
| **Sous-problèmes** | Ne calcule que les nécessaires | Calcule tous les sous-problèmes |
| **Espace** | Pile de récursion + cache | Tableau (optimisable) |
| **Risque** | Stack overflow pour n grand | Pas de risque |
| **Performance** | Overhead récursion | Légèrement plus rapide |

---

## ✅ Checklist de validation

Avant de passer au module suivant, vérifiez que vous pouvez :

- [ ] Écrire une fonction récursive avec cas de base et cas récursif
- [ ] Identifier les calculs redondants dans une récursivité naïve
- [ ] Appliquer la mémoïsation (manuelle et avec `lru_cache`)
- [ ] Implémenter une solution en programmation dynamique (bottom-up)
- [ ] Résoudre le problème de Fibonacci avec les 3 approches
- [ ] Expliquer la différence entre mémoïsation et programmation dynamique
- [ ] Identifier si un problème se prête à la programmation dynamique

---

[← Algorithmes de recherche](04-algorithmes-de-recherche.md) | [🏠 Accueil](../README.md) | [Suivant → Algorithmes de graphes](06-algorithmes-de-graphes.md)
