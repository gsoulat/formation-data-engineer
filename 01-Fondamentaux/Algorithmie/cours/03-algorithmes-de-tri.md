# Module 03 — Algorithmes de tri

## 🎯 Objectifs

- Comprendre pourquoi le tri est fondamental en informatique
- Implémenter les algorithmes de tri classiques (bulles, sélection, insertion, fusion, rapide)
- Comparer leurs complexités et savoir quand utiliser chacun
- Comprendre le tri en Python avec `sorted()` et `.sort()`

---

## 1. 🧠 Pourquoi trier ?

Le tri est l'une des opérations les plus fondamentales en informatique. Il est utilisé partout :

- **Bases de données** : `ORDER BY` en SQL
- **Recherche** : La recherche binaire nécessite des données triées
- **Data Engineering** : Tri pour les jointures sort-merge, partitionnement
- **Algorithmes** : De nombreux algorithmes nécessitent des données triées en pré-traitement

> 💡 On estime que **25 à 50% du temps CPU** des ordinateurs est consacré au tri. Choisir le bon algorithme est donc crucial.

---

## 2. 🫧 Tri à bulles (Bubble Sort)

### 2.1 Principe

On parcourt la liste en comparant les éléments adjacents et on les échange s'ils sont dans le mauvais ordre. On répète jusqu'à ce que la liste soit triée.

### 2.2 Visualisation

```
Passage 1 :  [5, 3, 8, 1, 2]
              ↕↕
             [3, 5, 8, 1, 2]  → 5 et 3 échangés
                 ↕↕
             [3, 5, 8, 1, 2]  → 5 et 8 OK
                    ↕↕
             [3, 5, 1, 8, 2]  → 8 et 1 échangés
                       ↕↕
             [3, 5, 1, 2, 8]  → 8 et 2 échangés → 8 est à sa place

Passage 2 :  [3, 5, 1, 2, 8]
             [3, 1, 2, 5, 8]  → 5 remonte

Passage 3 :  [1, 2, 3, 5, 8]  → Trié !
```

### 2.3 Implémentation

```python
def tri_bulles(liste: list) -> list:
    """Tri à bulles — O(n²)."""
    n = len(liste)
    for i in range(n):
        echange = False
        for j in range(0, n - i - 1):
            if liste[j] > liste[j + 1]:
                liste[j], liste[j + 1] = liste[j + 1], liste[j]
                echange = True
        # Optimisation : si aucun échange, la liste est déjà triée
        if not echange:
            break
    return liste


# Test
print(tri_bulles([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### 2.4 Complexité

| Cas | Complexité |
|-----|-----------|
| Meilleur (déjà trié) | O(n) — grâce à l'optimisation |
| Moyen | O(n²) |
| Pire (tri inverse) | O(n²) |
| Espace | O(1) — tri en place |

> ⚠️ **En pratique** : Le tri à bulles est pédagogique mais **jamais utilisé en production**. Trop lent pour de grandes quantités de données.

---

## 3. 🎯 Tri par sélection (Selection Sort)

### 3.1 Principe

On cherche le **minimum** de la partie non triée et on le place au début. On répète pour chaque position.

### 3.2 Visualisation

```
[5, 3, 8, 1, 2]
 ↑           ↑     min=1 à l'index 3 → échange avec index 0
[1, 3, 8, 5, 2]
    ↑        ↑     min=2 à l'index 4 → échange avec index 1
[1, 2, 8, 5, 3]
       ↑     ↑     min=3 à l'index 4 → échange avec index 2
[1, 2, 3, 5, 8]
          ↕↕       min=5 déjà en place
[1, 2, 3, 5, 8]   → Trié !
```

### 3.3 Implémentation

```python
def tri_selection(liste: list) -> list:
    """Tri par sélection — O(n²)."""
    n = len(liste)
    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            if liste[j] < liste[idx_min]:
                idx_min = j
        liste[i], liste[idx_min] = liste[idx_min], liste[i]
    return liste


# Test
print(tri_selection([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### 3.4 Complexité

| Cas | Complexité |
|-----|-----------|
| Tous les cas | O(n²) |
| Espace | O(1) — tri en place |

> 💡 Avantage : fait un nombre minimal d'échanges (au plus n). Utile quand les échanges sont coûteux.

---

## 4. 📥 Tri par insertion (Insertion Sort)

### 4.1 Principe

On parcourt la liste de gauche à droite. Pour chaque élément, on l'**insère à sa bonne position** dans la partie déjà triée (à gauche).

> 💡 **Analogie** : C'est comme trier des cartes à jouer dans sa main. On prend chaque carte et on la place au bon endroit parmi les cartes déjà triées.

### 4.2 Visualisation

```
[5, 3, 8, 1, 2]
 ✓  ↑              On prend 3, on l'insère avant 5
[3, 5, 8, 1, 2]
 ✓  ✓  ↑           On prend 8, déjà à la bonne place
[3, 5, 8, 1, 2]
 ✓  ✓  ✓  ↑        On prend 1, on l'insère au début
[1, 3, 5, 8, 2]
 ✓  ✓  ✓  ✓  ↑     On prend 2, on l'insère entre 1 et 3
[1, 2, 3, 5, 8]    → Trié !
```

### 4.3 Implémentation

```python
def tri_insertion(liste: list) -> list:
    """Tri par insertion — O(n²) mais efficace sur petites listes."""
    for i in range(1, len(liste)):
        cle = liste[i]
        j = i - 1
        # Décaler les éléments plus grands vers la droite
        while j >= 0 and liste[j] > cle:
            liste[j + 1] = liste[j]
            j -= 1
        liste[j + 1] = cle
    return liste


# Test
print(tri_insertion([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### 4.4 Complexité

| Cas | Complexité |
|-----|-----------|
| Meilleur (déjà trié) | O(n) |
| Moyen | O(n²) |
| Pire (tri inverse) | O(n²) |
| Espace | O(1) — tri en place |

> 💡 **En pratique** : Le tri par insertion est excellent pour les **petites listes** (< 50 éléments) et les **listes presque triées**. C'est pourquoi Python l'utilise en combinaison avec le tri fusion dans Timsort.

---

## 5. 🔀 Tri fusion (Merge Sort)

### 5.1 Principe — Diviser pour régner

1. **Diviser** : couper la liste en deux moitiés
2. **Régner** : trier récursivement chaque moitié
3. **Combiner** : fusionner les deux moitiés triées

### 5.2 Visualisation

```
                [5, 3, 8, 1, 2, 7, 4, 6]
                         │
              ┌──────────┴──────────┐
        [5, 3, 8, 1]          [2, 7, 4, 6]
              │                      │
        ┌─────┴─────┐         ┌─────┴─────┐
     [5, 3]      [8, 1]    [2, 7]      [4, 6]
       │           │          │           │
    ┌──┴──┐     ┌──┴──┐   ┌──┴──┐     ┌──┴──┐
   [5]   [3]   [8]   [1] [2]   [7]   [4]   [6]
    └──┬──┘     └──┬──┘   └──┬──┘     └──┬──┘
     [3, 5]      [1, 8]    [2, 7]      [4, 6]
        └─────┬─────┘         └─────┬─────┘
        [1, 3, 5, 8]          [2, 4, 6, 7]
              └──────────┬──────────┘
           [1, 2, 3, 4, 5, 6, 7, 8]
```

### 5.3 Implémentation

```python
def tri_fusion(liste: list) -> list:
    """Tri fusion — O(n log n) garanti."""
    if len(liste) <= 1:
        return liste

    # Diviser
    milieu = len(liste) // 2
    gauche = tri_fusion(liste[:milieu])
    droite = tri_fusion(liste[milieu:])

    # Fusionner
    return fusionner(gauche, droite)


def fusionner(gauche: list, droite: list) -> list:
    """Fusionne deux listes triées en une seule liste triée."""
    resultat = []
    i = j = 0

    while i < len(gauche) and j < len(droite):
        if gauche[i] <= droite[j]:
            resultat.append(gauche[i])
            i += 1
        else:
            resultat.append(droite[j])
            j += 1

    # Ajouter les éléments restants
    resultat.extend(gauche[i:])
    resultat.extend(droite[j:])
    return resultat


# Test
print(tri_fusion([5, 3, 8, 1, 2, 7, 4, 6]))  # [1, 2, 3, 4, 5, 6, 7, 8]
```

### 5.4 Complexité

| Cas | Complexité |
|-----|-----------|
| Tous les cas | O(n log n) |
| Espace | O(n) — nécessite de la mémoire supplémentaire |

> 💡 **Pour le Data Engineer** : Le tri fusion est le principe derrière le **Sort-Merge Join** en SQL et Spark. Il est aussi la base du **tri externe** (external sort) quand les données ne tiennent pas en mémoire.

---

## 6. ⚡ Tri rapide (Quick Sort)

### 6.1 Principe — Diviser pour régner (version 2)

1. Choisir un **pivot** (souvent le dernier élément)
2. **Partitionner** : placer les éléments plus petits à gauche et plus grands à droite du pivot
3. Trier récursivement chaque partition

### 6.2 Visualisation

```
Pivot = 4
[5, 3, 8, 1, 2, 7, 4, 6]

Partition autour de 4 :
[3, 1, 2]  [4]  [5, 8, 7, 6]
  < pivot  pivot   > pivot

Récursion gauche (pivot = 2) :     Récursion droite (pivot = 6) :
[1] [2] [3]                        [5] [6] [8, 7]

Résultat : [1, 2, 3, 4, 5, 6, 7, 8]
```

### 6.3 Implémentation

```python
def tri_rapide(liste: list) -> list:
    """Tri rapide — O(n log n) en moyenne."""
    if len(liste) <= 1:
        return liste

    pivot = liste[-1]
    gauche = [x for x in liste[:-1] if x <= pivot]
    droite = [x for x in liste[:-1] if x > pivot]

    return tri_rapide(gauche) + [pivot] + tri_rapide(droite)


# Test
print(tri_rapide([5, 3, 8, 1, 2, 7, 4, 6]))  # [1, 2, 3, 4, 5, 6, 7, 8]
```

### 6.4 Version en place (plus efficace en mémoire)

```python
def tri_rapide_en_place(liste: list, debut: int = 0, fin: int | None = None) -> list:
    """Tri rapide en place — O(1) en espace supplémentaire."""
    if fin is None:
        fin = len(liste) - 1

    if debut < fin:
        pivot_idx = partitionner(liste, debut, fin)
        tri_rapide_en_place(liste, debut, pivot_idx - 1)
        tri_rapide_en_place(liste, pivot_idx + 1, fin)

    return liste


def partitionner(liste: list, debut: int, fin: int) -> int:
    """Place le pivot à sa position finale et retourne son index."""
    pivot = liste[fin]
    i = debut - 1

    for j in range(debut, fin):
        if liste[j] <= pivot:
            i += 1
            liste[i], liste[j] = liste[j], liste[i]

    liste[i + 1], liste[fin] = liste[fin], liste[i + 1]
    return i + 1
```

### 6.5 Complexité

| Cas | Complexité |
|-----|-----------|
| Meilleur | O(n log n) |
| Moyen | O(n log n) |
| Pire (liste déjà triée avec mauvais pivot) | O(n²) |
| Espace (en place) | O(log n) — pile de récursion |

---

## 7. 📊 Comparaison des algorithmes de tri

### 7.1 Tableau récapitulatif

| Algorithme | Meilleur | Moyen | Pire | Espace | Stable | En place |
|------------|----------|-------|------|--------|--------|----------|
| **Bulles** | O(n) | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| **Sélection** | O(n²) | O(n²) | O(n²) | O(1) | ❌ | ✅ |
| **Insertion** | O(n) | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| **Fusion** | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ | ❌ |
| **Rapide** | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | ✅ |
| **Timsort** | O(n) | O(n log n) | O(n log n) | O(n) | ✅ | ❌ |

> 💡 **Stable** = les éléments égaux gardent leur ordre relatif d'origine.

### 7.2 Quel tri choisir ?

| Situation | Algorithme recommandé |
|-----------|----------------------|
| Petite liste (< 50 éléments) | Insertion |
| Liste presque triée | Insertion |
| Garantie O(n log n) dans tous les cas | Fusion |
| Meilleure performance en moyenne | Rapide |
| Mémoire limitée | Rapide (en place) |
| Données qui ne tiennent pas en RAM | Fusion (tri externe) |
| En Python, toujours | `sorted()` / `.sort()` (Timsort) |

---

## 8. 🐍 Le tri en Python : Timsort

### 8.1 Qu'est-ce que Timsort ?

Python utilise **Timsort**, un algorithme hybride inventé par Tim Peters en 2002. Il combine :
- **Tri par insertion** pour les petites sous-listes
- **Tri fusion** pour combiner les sous-listes

### 8.2 Utilisation

```python
# sorted() — retourne une NOUVELLE liste triée
nombres = [5, 3, 8, 1, 2]
tri = sorted(nombres)       # [1, 2, 3, 5, 8]
print(nombres)               # [5, 3, 8, 1, 2] — original inchangé

# .sort() — trie EN PLACE (modifie la liste)
nombres.sort()
print(nombres)               # [1, 2, 3, 5, 8] — original modifié

# Tri décroissant
sorted(nombres, reverse=True)  # [8, 5, 3, 2, 1]

# Tri avec clé personnalisée
mots = ["banane", "abricot", "cerise", "datte"]
sorted(mots, key=len)          # ['datte', 'banane', 'cerise', 'abricot']

# Tri de dictionnaires
employes = [
    {"nom": "Alice", "age": 30},
    {"nom": "Bob", "age": 25},
    {"nom": "Charlie", "age": 35},
]
sorted(employes, key=lambda e: e["age"])
# [{'nom': 'Bob', 'age': 25}, {'nom': 'Alice', 'age': 30}, {'nom': 'Charlie', 'age': 35}]
```

### 8.3 Tri multi-critères

```python
# Trier par département puis par salaire décroissant
employes = [
    {"nom": "Alice", "dept": "IT", "salaire": 50000},
    {"nom": "Bob", "dept": "RH", "salaire": 45000},
    {"nom": "Charlie", "dept": "IT", "salaire": 55000},
    {"nom": "Diana", "dept": "RH", "salaire": 48000},
]

# Tri multi-critères : département croissant, salaire décroissant
resultat = sorted(employes, key=lambda e: (e["dept"], -e["salaire"]))
# IT: Charlie (55k), Alice (50k) puis RH: Diana (48k), Bob (45k)
```

> ⚠️ **Attention** : N'implémentez jamais votre propre tri en production Python. `sorted()` et `.sort()` utilisent Timsort, qui est extrêmement optimisé et écrit en C. Vos implémentations maison sont pédagogiques, pas pour la production.

---

## ✅ Checklist de validation

Avant de passer au module suivant, vérifiez que vous pouvez :

- [ ] Expliquer le principe de chaque algorithme de tri (bulles, sélection, insertion, fusion, rapide)
- [ ] Implémenter au moins le tri par insertion et le tri fusion
- [ ] Donner la complexité (meilleur/pire/moyen) de chaque algorithme
- [ ] Expliquer la différence entre un tri stable et instable
- [ ] Utiliser `sorted()` et `.sort()` avec des clés personnalisées
- [ ] Choisir le bon algorithme de tri selon le contexte

---

[← Structures de données](02-structures-de-donnees.md) | [🏠 Accueil](../README.md) | [Suivant → Algorithmes de recherche](04-algorithmes-de-recherche.md)
