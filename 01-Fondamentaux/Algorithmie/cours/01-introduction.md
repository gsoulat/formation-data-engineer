# Module 01 — Introduction à l'algorithmie

## 🎯 Objectifs

- Comprendre ce qu'est un algorithme
- Savoir écrire un algorithme en pseudo-code
- Comprendre et calculer la complexité algorithmique (Big O)
- Distinguer complexité temporelle et spatiale

---

## 1. 🧠 Qu'est-ce qu'un algorithme ?

### 1.1 Définition

Un **algorithme** est une suite finie et ordonnée d'instructions permettant de résoudre un problème ou d'accomplir une tâche.

> 💡 **Analogie** : Une recette de cuisine est un algorithme. Elle décrit des étapes précises (ingrédients = entrées, plat = sortie, étapes = instructions).

### 1.2 Caractéristiques d'un bon algorithme

| Caractéristique | Description |
|----------------|-------------|
| **Finitude** | L'algorithme se termine en un nombre fini d'étapes |
| **Précision** | Chaque étape est définie sans ambiguïté |
| **Entrées** | Zéro ou plusieurs données en entrée |
| **Sorties** | Au moins un résultat en sortie |
| **Efficacité** | Chaque opération est réalisable en temps fini |

### 1.3 Exemple concret : trouver le maximum d'une liste

**Problème** : Étant donné une liste de nombres, trouver le plus grand.

**En langage naturel** :
1. Prendre le premier élément comme maximum temporaire
2. Parcourir chaque élément restant
3. Si l'élément courant est plus grand que le maximum, le remplacer
4. À la fin du parcours, le maximum temporaire est le résultat

---

## 2. ✏️ Le pseudo-code

Le pseudo-code est une manière d'écrire un algorithme de façon structurée, indépendamment de tout langage de programmation.

### 2.1 Conventions du pseudo-code

```
ALGORITHME nom_algorithme
  ENTRÉES : description des entrées
  SORTIES : description des sorties
DÉBUT
  instruction 1
  instruction 2
  ...
FIN
```

### 2.2 Structures de contrôle

**Condition** :
```
SI condition ALORS
  instructions
SINON
  instructions
FIN SI
```

**Boucle POUR** :
```
POUR i DE 1 À n FAIRE
  instructions
FIN POUR
```

**Boucle TANT QUE** :
```
TANT QUE condition FAIRE
  instructions
FIN TANT QUE
```

### 2.3 Exemple : trouver le maximum

```
ALGORITHME trouver_maximum
  ENTRÉES : liste[] — un tableau de n nombres
  SORTIES : max — le plus grand nombre

DÉBUT
  max ← liste[0]

  POUR i DE 1 À longueur(liste) - 1 FAIRE
    SI liste[i] > max ALORS
      max ← liste[i]
    FIN SI
  FIN POUR

  RETOURNER max
FIN
```

### 2.4 Traduction en Python

```python
def trouver_maximum(liste: list[int]) -> int:
    """Trouve le plus grand élément d'une liste."""
    max_val = liste[0]

    for i in range(1, len(liste)):
        if liste[i] > max_val:
            max_val = liste[i]

    return max_val


# Test
nombres = [3, 7, 2, 9, 4, 1]
print(trouver_maximum(nombres))  # 9
```

---

## 3. 📊 Complexité algorithmique

### 3.1 Pourquoi mesurer la complexité ?

Deux algorithmes peuvent résoudre le même problème mais avec des performances très différentes. La complexité permet de les comparer **indépendamment de la machine**.

> 💡 **En data engineering**, la différence entre un algorithme O(n) et O(n²) peut signifier un pipeline qui prend 1 minute vs 1 jour sur 1 million de lignes.

### 3.2 Notation Big O

La notation **Big O** décrit le comportement d'un algorithme dans le **pire cas** quand la taille des données (n) grandit.

On s'intéresse à l'**ordre de grandeur** : on ignore les constantes et les termes de faible degré.

```
3n² + 5n + 10  →  O(n²)
2n + 100       →  O(n)
5              →  O(1)
```

### 3.3 Les complexités courantes

| Notation | Nom | Exemple | Performance |
|----------|-----|---------|-------------|
| **O(1)** | Constante | Accès à un élément par index | 🟢 Excellente |
| **O(log n)** | Logarithmique | Recherche binaire | 🟢 Très bonne |
| **O(n)** | Linéaire | Parcours d'une liste | 🟡 Bonne |
| **O(n log n)** | Linéarithmique | Tri fusion, tri rapide | 🟡 Correcte |
| **O(n²)** | Quadratique | Tri à bulles, double boucle | 🟠 Médiocre |
| **O(2ⁿ)** | Exponentielle | Sous-ensembles, force brute | 🔴 Mauvaise |
| **O(n!)** | Factorielle | Permutations | 🔴 Catastrophique |

### 3.4 Illustration avec des valeurs concrètes

Pour n = 1 000 000 (1 million) :

| Complexité | Nombre d'opérations | Temps estimé (1 GHz) |
|------------|--------------------|-----------------------|
| O(1) | 1 | 1 ns |
| O(log n) | 20 | 20 ns |
| O(n) | 1 000 000 | 1 ms |
| O(n log n) | 20 000 000 | 20 ms |
| O(n²) | 1 000 000 000 000 | ~17 min |
| O(2ⁿ) | ... | ∞ (impossible) |

> ⚠️ **Attention** : Avec des volumes de données typiques en data engineering (millions/milliards de lignes), la complexité fait toute la différence.

### 3.5 Calculer la complexité

**Règles de base** :

1. **Opération simple** → O(1)
```python
x = 5          # O(1)
y = x + 3      # O(1)
```

2. **Boucle simple** → O(n)
```python
for i in range(n):    # O(n)
    print(i)          # O(1) × n = O(n)
```

3. **Boucles imbriquées** → O(n²)
```python
for i in range(n):        # O(n)
    for j in range(n):    # O(n) × O(n) = O(n²)
        print(i, j)
```

4. **Boucle avec division** → O(log n)
```python
i = n
while i > 1:     # O(log n)
    i = i // 2   # On divise par 2 à chaque itération
```

5. **Séquence** → On prend le maximum
```python
for i in range(n):        # O(n)
    print(i)

for i in range(n):        # O(n)
    for j in range(n):    # O(n²)
        print(i, j)

# Total : O(n) + O(n²) = O(n²)
```

### 3.6 Exercice guidé : analyser la complexité

```python
def mystere(liste):
    n = len(liste)              # O(1)
    total = 0                   # O(1)

    for i in range(n):          # O(n)
        for j in range(i, n):   # O(n) dans le pire cas
            total += liste[j]   # O(1)

    return total                # O(1)
```

**Analyse** :
- La boucle externe s'exécute n fois
- La boucle interne s'exécute (n-i) fois pour chaque i
- Total d'opérations : n + (n-1) + (n-2) + ... + 1 = n(n+1)/2
- Complexité : **O(n²)**

---

## 4. 📦 Complexité spatiale

### 4.1 Définition

La complexité spatiale mesure la **quantité de mémoire** utilisée par un algorithme en fonction de la taille des données.

### 4.2 Exemples

```python
# O(1) en espace — on ne crée pas de structure additionnelle
def somme(liste):
    total = 0
    for x in liste:
        total += x
    return total

# O(n) en espace — on crée une nouvelle liste
def doubler(liste):
    resultat = []
    for x in liste:
        resultat.append(x * 2)
    return resultat

# O(n²) en espace — on crée une matrice
def matrice_identite(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
```

### 4.3 Compromis temps-espace

> 💡 **Conseil** : En algorithmie, il existe souvent un **compromis** entre temps et espace. On peut parfois accélérer un algorithme en utilisant plus de mémoire (ex : mémoïsation, tables de hachage).

| Stratégie | Temps | Espace |
|-----------|-------|--------|
| Calcul direct (recalculer à chaque fois) | Plus lent | Moins de mémoire |
| Cache / Mémoïsation (stocker les résultats) | Plus rapide | Plus de mémoire |

---

## 5. 🔍 Meilleures, pire et moyenne complexité

### 5.1 Les trois cas

Pour un même algorithme, la complexité peut varier selon les données d'entrée :

| Cas | Description | Notation |
|-----|-------------|----------|
| **Meilleur cas** | L'entrée la plus favorable | Ω (Omega) |
| **Pire cas** | L'entrée la plus défavorable | O (Big O) |
| **Cas moyen** | Moyenne sur toutes les entrées possibles | Θ (Theta) |

### 5.2 Exemple : recherche linéaire

```python
def recherche_lineaire(liste, cible):
    for i, element in enumerate(liste):
        if element == cible:
            return i
    return -1
```

| Cas | Situation | Complexité |
|-----|-----------|------------|
| Meilleur | L'élément est le premier | O(1) |
| Pire | L'élément est le dernier ou absent | O(n) |
| Moyen | L'élément est au milieu en moyenne | O(n/2) = O(n) |

> 💡 En pratique, on utilise presque toujours la notation **Big O (pire cas)** car elle donne la garantie de performance maximale.

---

## 6. 🐍 Complexité des opérations Python courantes

### 6.1 Listes (list)

| Opération | Complexité | Exemple |
|-----------|-----------|---------|
| Accès par index | O(1) | `liste[i]` |
| Ajout en fin | O(1) amorti | `liste.append(x)` |
| Insertion au milieu | O(n) | `liste.insert(i, x)` |
| Suppression par index | O(n) | `liste.pop(i)` |
| Recherche (in) | O(n) | `x in liste` |
| Tri | O(n log n) | `liste.sort()` |

### 6.2 Dictionnaires (dict)

| Opération | Complexité | Exemple |
|-----------|-----------|---------|
| Accès par clé | O(1) moyen | `d[clé]` |
| Insertion | O(1) moyen | `d[clé] = valeur` |
| Suppression | O(1) moyen | `del d[clé]` |
| Recherche (in) | O(1) moyen | `clé in d` |

### 6.3 Ensembles (set)

| Opération | Complexité | Exemple |
|-----------|-----------|---------|
| Ajout | O(1) moyen | `s.add(x)` |
| Recherche (in) | O(1) moyen | `x in s` |
| Union | O(len(s1) + len(s2)) | `s1 \| s2` |
| Intersection | O(min(len(s1), len(s2))) | `s1 & s2` |

> 💡 **Pour le Data Engineer** : Quand vous devez vérifier l'appartenance d'un élément, utilisez un `set` ou un `dict` (O(1)) plutôt qu'une `list` (O(n)). Sur 1 million d'éléments, c'est 1 opération vs 1 million !

---

## ✅ Checklist de validation

Avant de passer au module suivant, vérifiez que vous pouvez :

- [ ] Définir ce qu'est un algorithme et ses caractéristiques
- [ ] Écrire un algorithme simple en pseudo-code
- [ ] Expliquer la notation Big O et ce qu'elle mesure
- [ ] Identifier la complexité d'un code simple (boucles, conditions)
- [ ] Classer les complexités de la meilleure à la pire
- [ ] Distinguer complexité temporelle et spatiale
- [ ] Connaître la complexité des opérations Python courantes

---

[🏠 Accueil](../README.md) | [Suivant → Structures de données](02-structures-de-donnees.md)
