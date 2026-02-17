# Module 04 — Algorithmes de recherche

## 🎯 Objectifs

- Comprendre et implémenter la recherche linéaire et binaire
- Maîtriser le parcours en largeur (BFS) et en profondeur (DFS)
- Savoir choisir le bon algorithme de recherche selon le contexte
- Appliquer ces algorithmes à des problèmes concrets

---

## 1. 🔍 Recherche linéaire

### 1.1 Principe

Parcourir chaque élément un par un, du début à la fin, jusqu'à trouver la cible ou atteindre la fin de la liste.

```
Chercher 7 dans [3, 8, 1, 7, 5, 2]

  3   8   1   7   5   2
  ↑
  ≠7
      ↑
      ≠7
          ↑
          ≠7
              ↑
              =7 → Trouvé à l'index 3 !
```

### 1.2 Implémentation

```python
def recherche_lineaire(liste: list, cible) -> int:
    """Recherche linéaire — O(n)."""
    for i, element in enumerate(liste):
        if element == cible:
            return i
    return -1


# Test
nombres = [3, 8, 1, 7, 5, 2]
print(recherche_lineaire(nombres, 7))   # 3
print(recherche_lineaire(nombres, 10))  # -1
```

### 1.3 Complexité

| Cas | Complexité |
|-----|-----------|
| Meilleur | O(1) — premier élément |
| Moyen | O(n/2) = O(n) |
| Pire | O(n) — dernier ou absent |
| Espace | O(1) |

### 1.4 Variantes utiles

```python
# Recherche de toutes les occurrences
def rechercher_toutes(liste: list, cible) -> list[int]:
    """Retourne tous les indices où la cible apparaît."""
    return [i for i, x in enumerate(liste) if x == cible]


# Recherche du minimum et maximum simultanés
def min_max(liste: list) -> tuple:
    """Trouve min et max en un seul parcours — O(n)."""
    if not liste:
        raise ValueError("Liste vide")
    val_min = val_max = liste[0]
    for x in liste[1:]:
        if x < val_min:
            val_min = x
        elif x > val_max:
            val_max = x
    return val_min, val_max


# Recherche avec condition (filtre)
def rechercher_condition(liste: list, condition) -> list:
    """Retourne les éléments satisfaisant une condition."""
    return [x for x in liste if condition(x)]


# Exemple : nombres pairs supérieurs à 5
nombres = [1, 8, 3, 12, 5, 6, 2, 10]
print(rechercher_condition(nombres, lambda x: x % 2 == 0 and x > 5))
# [8, 12, 6, 10]
```

---

## 2. 🎯 Recherche binaire (dichotomie)

### 2.1 Principe

> ⚠️ **Prérequis** : La liste **doit être triée**.

On compare la cible avec l'élément du milieu :
- Si égal → trouvé
- Si la cible est plus petite → chercher dans la moitié gauche
- Si la cible est plus grande → chercher dans la moitié droite

> 💡 **Analogie** : Chercher un mot dans un dictionnaire. On ouvre au milieu, puis on va à gauche ou à droite selon l'ordre alphabétique.

### 2.2 Visualisation

```
Chercher 7 dans [1, 2, 3, 5, 7, 8, 10, 12, 15]

Étape 1 : milieu = 7 (index 4)
[1, 2, 3, 5, 7, 8, 10, 12, 15]
  ↑           ↑              ↑
 début      milieu           fin
 7 == 7 → Trouvé à l'index 4 !

Chercher 3 :
Étape 1 : milieu = 7 → 3 < 7 → chercher à gauche
[1, 2, 3, 5]
Étape 2 : milieu = 2 → 3 > 2 → chercher à droite
[3, 5]
Étape 3 : milieu = 3 → Trouvé !
```

### 2.3 Implémentation itérative

```python
def recherche_binaire(liste: list, cible) -> int:
    """Recherche binaire itérative — O(log n)."""
    debut = 0
    fin = len(liste) - 1

    while debut <= fin:
        milieu = (debut + fin) // 2

        if liste[milieu] == cible:
            return milieu
        elif liste[milieu] < cible:
            debut = milieu + 1
        else:
            fin = milieu - 1

    return -1


# Test
nombres_tries = [1, 2, 3, 5, 7, 8, 10, 12, 15]
print(recherche_binaire(nombres_tries, 7))   # 4
print(recherche_binaire(nombres_tries, 6))   # -1
```

### 2.4 Implémentation récursive

```python
def recherche_binaire_recursive(liste: list, cible, debut: int = 0, fin: int | None = None) -> int:
    """Recherche binaire récursive — O(log n)."""
    if fin is None:
        fin = len(liste) - 1

    if debut > fin:
        return -1

    milieu = (debut + fin) // 2

    if liste[milieu] == cible:
        return milieu
    elif liste[milieu] < cible:
        return recherche_binaire_recursive(liste, cible, milieu + 1, fin)
    else:
        return recherche_binaire_recursive(liste, cible, debut, milieu - 1)
```

### 2.5 Complexité

| Cas | Complexité |
|-----|-----------|
| Meilleur | O(1) — l'élément est au milieu |
| Moyen | O(log n) |
| Pire | O(log n) |
| Espace (itératif) | O(1) |
| Espace (récursif) | O(log n) — pile de récursion |

### 2.6 Puissance du logarithme

| Taille (n) | Recherche linéaire O(n) | Recherche binaire O(log n) |
|-----------|------------------------|---------------------------|
| 100 | 100 opérations | 7 opérations |
| 10 000 | 10 000 | 14 |
| 1 000 000 | 1 000 000 | 20 |
| 1 000 000 000 | 1 milliard | 30 |

> 💡 **Pour le Data Engineer** : La recherche binaire est le principe derrière les index B-tree des bases de données. Un index sur 1 milliard de lignes nécessite ~30 comparaisons au lieu d'un milliard. C'est pourquoi `WHERE id = 42` avec un index est quasi instantané.

### 2.7 Module `bisect` de Python

```python
import bisect

# bisect gère les recherches et insertions dans des listes triées
nombres = [1, 3, 5, 7, 9, 11]

# Trouver le point d'insertion pour maintenir l'ordre
idx = bisect.bisect_left(nombres, 6)   # 3 (insérer avant 7)
print(idx)

# Insérer en maintenant le tri
bisect.insort(nombres, 6)
print(nombres)  # [1, 3, 5, 6, 7, 9, 11]

# Recherche avec bisect
def recherche_bisect(liste, cible):
    """Recherche binaire avec bisect."""
    idx = bisect.bisect_left(liste, cible)
    if idx < len(liste) and liste[idx] == cible:
        return idx
    return -1
```

---

## 3. 🌊 Parcours en largeur (BFS — Breadth-First Search)

### 3.1 Principe

BFS explore un graphe **niveau par niveau**, en visitant d'abord tous les voisins directs avant de passer aux voisins des voisins.

Utilise une **file (queue)** pour gérer l'ordre de visite.

### 3.2 Visualisation

```
Graphe :
        A
       / \
      B   C
     / \   \
    D   E   F

Ordre BFS depuis A : A → B → C → D → E → F
(niveau 0, puis niveau 1, puis niveau 2)
```

### 3.3 Implémentation

```python
from collections import deque


def bfs(graphe: dict, depart: str) -> list[str]:
    """Parcours en largeur (BFS) — O(V + E)."""
    visite = set()
    file = deque([depart])
    visite.add(depart)
    ordre = []

    while file:
        sommet = file.popleft()
        ordre.append(sommet)

        for voisin in graphe.get(sommet, []):
            if voisin not in visite:
                visite.add(voisin)
                file.append(voisin)

    return ordre


# Test
graphe = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B"],
    "F": ["C"],
}

print(bfs(graphe, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

### 3.4 Application : plus court chemin (non pondéré)

BFS garantit de trouver le **plus court chemin** dans un graphe non pondéré.

```python
def plus_court_chemin_bfs(graphe: dict, depart: str, arrivee: str) -> list[str] | None:
    """Trouve le plus court chemin entre deux sommets — O(V + E)."""
    if depart == arrivee:
        return [depart]

    visite = {depart}
    file = deque([(depart, [depart])])

    while file:
        sommet, chemin = file.popleft()

        for voisin in graphe.get(sommet, []):
            if voisin == arrivee:
                return chemin + [voisin]
            if voisin not in visite:
                visite.add(voisin)
                file.append((voisin, chemin + [voisin]))

    return None  # Pas de chemin


# Test
print(plus_court_chemin_bfs(graphe, "D", "F"))  # ['D', 'B', 'A', 'C', 'F']
```

### 3.5 Complexité BFS

| Aspect | Complexité |
|--------|-----------|
| Temps | O(V + E) |
| Espace | O(V) |

> V = sommets, E = arêtes

---

## 4. 🏔️ Parcours en profondeur (DFS — Depth-First Search)

### 4.1 Principe

DFS explore un graphe en allant le plus **loin possible** dans une branche avant de revenir en arrière (backtracking).

Utilise une **pile (stack)** — souvent via la récursion.

### 4.2 Visualisation

```
Graphe :
        A
       / \
      B   C
     / \   \
    D   E   F

Ordre DFS depuis A : A → B → D → E → C → F
(on descend le plus profond possible avant de remonter)
```

### 4.3 Implémentation récursive

```python
def dfs_recursif(graphe: dict, depart: str, visite: set | None = None) -> list[str]:
    """Parcours en profondeur récursif — O(V + E)."""
    if visite is None:
        visite = set()

    visite.add(depart)
    ordre = [depart]

    for voisin in graphe.get(depart, []):
        if voisin not in visite:
            ordre.extend(dfs_recursif(graphe, voisin, visite))

    return ordre


# Test
print(dfs_recursif(graphe, "A"))  # ['A', 'B', 'D', 'E', 'C', 'F']
```

### 4.4 Implémentation itérative (avec pile)

```python
def dfs_iteratif(graphe: dict, depart: str) -> list[str]:
    """Parcours en profondeur itératif — O(V + E)."""
    visite = set()
    pile = [depart]
    ordre = []

    while pile:
        sommet = pile.pop()
        if sommet not in visite:
            visite.add(sommet)
            ordre.append(sommet)
            # Ajouter les voisins dans l'ordre inverse pour respecter l'ordre
            for voisin in reversed(graphe.get(sommet, [])):
                if voisin not in visite:
                    pile.append(voisin)

    return ordre


print(dfs_iteratif(graphe, "A"))  # ['A', 'B', 'D', 'E', 'C', 'F']
```

### 4.5 Application : détection de cycle

```python
def a_un_cycle(graphe: dict) -> bool:
    """Détecte la présence d'un cycle dans un graphe orienté."""
    visite = set()
    en_cours = set()  # Sommets dans la pile de récursion actuelle

    def dfs(sommet):
        visite.add(sommet)
        en_cours.add(sommet)

        for voisin in graphe.get(sommet, []):
            if voisin not in visite:
                if dfs(voisin):
                    return True
            elif voisin in en_cours:
                return True  # Cycle détecté !

        en_cours.remove(sommet)
        return False

    for sommet in graphe:
        if sommet not in visite:
            if dfs(sommet):
                return True

    return False


# Test
graphe_avec_cycle = {"A": ["B"], "B": ["C"], "C": ["A"]}  # A→B→C→A
graphe_sans_cycle = {"A": ["B"], "B": ["C"], "C": []}      # A→B→C

print(a_un_cycle(graphe_avec_cycle))  # True
print(a_un_cycle(graphe_sans_cycle))  # False
```

> 💡 **Pour le Data Engineer** : La détection de cycle est essentielle dans les DAG (Airflow, dbt). Si une tâche A dépend de B, et B dépend de A, c'est un cycle impossible à résoudre.

### 4.6 Application : tri topologique

Le **tri topologique** ordonne les sommets d'un DAG de manière à respecter toutes les dépendances.

```python
def tri_topologique(graphe: dict) -> list[str]:
    """Tri topologique d'un DAG — O(V + E)."""
    visite = set()
    resultat = []

    def dfs(sommet):
        visite.add(sommet)
        for voisin in graphe.get(sommet, []):
            if voisin not in visite:
                dfs(voisin)
        resultat.append(sommet)

    for sommet in graphe:
        if sommet not in visite:
            dfs(sommet)

    return list(reversed(resultat))


# Exemple : dépendances de tâches data
# extract → transform → load
# extract → validate
# validate → transform
pipeline = {
    "extract": ["transform", "validate"],
    "validate": ["transform"],
    "transform": ["load"],
    "load": [],
}

print(tri_topologique(pipeline))  # ['extract', 'validate', 'transform', 'load']
```

> 💡 **Pour le Data Engineer** : Le tri topologique est exactement ce qu'Airflow fait pour déterminer l'ordre d'exécution des tâches dans un DAG. C'est aussi ce que `dbt` utilise pour compiler les modèles dans le bon ordre.

---

## 5. 📊 Comparaison BFS vs DFS

| Aspect | BFS | DFS |
|--------|-----|-----|
| **Structure** | File (FIFO) | Pile (LIFO) / Récursion |
| **Exploration** | Niveau par niveau | Branche par branche |
| **Plus court chemin** | ✅ Garanti (non pondéré) | ❌ Pas garanti |
| **Mémoire** | O(V) — stocke tout un niveau | O(h) — hauteur de l'arbre |
| **Détection de cycle** | ✅ Possible | ✅ Plus naturel |
| **Tri topologique** | ✅ (algorithme de Kahn) | ✅ Plus simple |
| **Graphe large et plat** | ❌ Beaucoup de mémoire | ✅ Peu de mémoire |
| **Graphe profond** | ✅ Pas de risque de stack overflow | ⚠️ Stack overflow possible |

### Quand utiliser lequel ?

| Situation | Algorithme |
|-----------|-----------|
| Plus court chemin (non pondéré) | **BFS** |
| Explorer tout un graphe | BFS ou DFS |
| Détecter un cycle | **DFS** |
| Tri topologique | **DFS** |
| Résoudre un labyrinthe | **BFS** (plus court) ou DFS |
| Parcourir un arbre de fichiers | **DFS** |
| Recherche de composantes connexes | BFS ou DFS |

---

## ✅ Checklist de validation

Avant de passer au module suivant, vérifiez que vous pouvez :

- [ ] Implémenter la recherche linéaire et binaire
- [ ] Expliquer pourquoi la recherche binaire nécessite une liste triée
- [ ] Calculer le nombre d'étapes d'une recherche binaire pour n éléments
- [ ] Implémenter BFS et DFS sur un graphe
- [ ] Expliquer la différence entre BFS et DFS
- [ ] Trouver le plus court chemin avec BFS
- [ ] Détecter un cycle avec DFS
- [ ] Appliquer le tri topologique à des dépendances de tâches

---

[← Algorithmes de tri](03-algorithmes-de-tri.md) | [🏠 Accueil](../README.md) | [Suivant → Récursivité et programmation dynamique](05-recursivite-programmation-dynamique.md)
