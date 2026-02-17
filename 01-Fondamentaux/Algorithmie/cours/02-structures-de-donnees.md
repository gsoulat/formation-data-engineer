# Module 02 — Structures de données

## 🎯 Objectifs

- Comprendre le rôle des structures de données dans la performance des algorithmes
- Maîtriser les structures linéaires : tableaux, listes chaînées, piles, files
- Comprendre les tables de hachage et leur fonctionnement interne
- Découvrir les arbres et les graphes
- Savoir choisir la bonne structure selon le contexte

---

## 1. 🧱 Introduction

### 1.1 Pourquoi les structures de données sont importantes

> 💡 **Principe fondamental** : Un algorithme est aussi performant que la structure de données qu'il utilise. Choisir la mauvaise structure peut transformer un traitement rapide en un cauchemar de performance.

Une structure de données est une manière d'**organiser et stocker** des données pour permettre des opérations efficaces (lecture, insertion, suppression, recherche).

### 1.2 Classification

```
Structures de données
├── Linéaires
│   ├── Tableau (Array)
│   ├── Liste chaînée (Linked List)
│   ├── Pile (Stack)
│   └── File (Queue)
├── Associatives
│   └── Table de hachage (Hash Table / Dict)
└── Hiérarchiques / Relationnelles
    ├── Arbre (Tree)
    └── Graphe (Graph)
```

---

## 2. 📏 Structures linéaires

### 2.1 Tableau (Array / List)

Le tableau est la structure la plus simple : une collection ordonnée d'éléments stockés de manière **contiguë en mémoire**.

```
Index :   0     1     2     3     4
        ┌─────┬─────┬─────┬─────┬─────┐
Valeur: │  10  │  20  │  30  │  40  │  50  │
        └─────┴─────┴─────┴─────┴─────┘
```

**En Python** : la `list` est un tableau dynamique.

```python
# Création
nombres = [10, 20, 30, 40, 50]

# Accès par index — O(1)
print(nombres[2])  # 30

# Ajout en fin — O(1) amorti
nombres.append(60)

# Insertion au milieu — O(n) (décalage des éléments)
nombres.insert(2, 25)  # [10, 20, 25, 30, 40, 50, 60]

# Suppression — O(n) (décalage des éléments)
nombres.pop(2)  # Supprime l'élément à l'index 2
```

**Quand utiliser un tableau ?**
- ✅ Accès fréquent par index
- ✅ Parcours séquentiel
- ❌ Insertions/suppressions fréquentes au milieu

### 2.2 Liste chaînée (Linked List)

Une liste chaînée est composée de **nœuds**, chaque nœud contenant une valeur et un pointeur vers le nœud suivant.

```
┌───┬───┐    ┌───┬───┐    ┌───┬───┐    ┌───┬──────┐
│ 10│ ──┼───>│ 20│ ──┼───>│ 30│ ──┼───>│ 40│ None │
└───┴───┘    └───┴───┘    └───┴───┘    └───┴──────┘
 Tête                                     Queue
```

```python
class Noeud:
    """Un noeud d'une liste chaînée."""

    def __init__(self, valeur, suivant=None):
        self.valeur = valeur
        self.suivant = suivant


class ListeChainee:
    """Liste chaînée simple."""

    def __init__(self):
        self.tete = None

    def ajouter_debut(self, valeur):
        """Ajoute un élément en tête — O(1)."""
        nouveau = Noeud(valeur, self.tete)
        self.tete = nouveau

    def ajouter_fin(self, valeur):
        """Ajoute un élément en queue — O(n)."""
        nouveau = Noeud(valeur)
        if self.tete is None:
            self.tete = nouveau
            return
        courant = self.tete
        while courant.suivant:
            courant = courant.suivant
        courant.suivant = nouveau

    def afficher(self):
        """Affiche tous les éléments."""
        courant = self.tete
        elements = []
        while courant:
            elements.append(str(courant.valeur))
            courant = courant.suivant
        print(" -> ".join(elements))

    def rechercher(self, valeur):
        """Recherche un élément — O(n)."""
        courant = self.tete
        while courant:
            if courant.valeur == valeur:
                return True
            courant = courant.suivant
        return False


# Utilisation
ll = ListeChainee()
ll.ajouter_debut(30)
ll.ajouter_debut(20)
ll.ajouter_debut(10)
ll.ajouter_fin(40)
ll.afficher()  # 10 -> 20 -> 30 -> 40
```

**Comparaison Tableau vs Liste chaînée** :

| Opération | Tableau | Liste chaînée |
|-----------|---------|---------------|
| Accès par index | O(1) | O(n) |
| Insertion en tête | O(n) | O(1) |
| Insertion en fin | O(1) amorti | O(n)* |
| Recherche | O(n) | O(n) |
| Mémoire | Contiguë | Fragmentée |

> \* O(1) si on maintient un pointeur vers la queue.

### 2.3 Pile (Stack) — LIFO

La pile fonctionne en **Last In, First Out** : le dernier élément ajouté est le premier retiré.

```
        ┌─────┐
push →  │  40 │  ← pop
        ├─────┤
        │  30 │
        ├─────┤
        │  20 │
        ├─────┤
        │  10 │
        └─────┘
```

> 💡 **Analogie** : Une pile d'assiettes. On pose (push) et on retire (pop) toujours par le dessus.

```python
class Pile:
    """Implémentation d'une pile avec une liste Python."""

    def __init__(self):
        self._elements = []

    def empiler(self, valeur):
        """Ajoute un élément au sommet — O(1)."""
        self._elements.append(valeur)

    def depiler(self):
        """Retire et retourne l'élément au sommet — O(1)."""
        if self.est_vide():
            raise IndexError("La pile est vide")
        return self._elements.pop()

    def sommet(self):
        """Retourne l'élément au sommet sans le retirer — O(1)."""
        if self.est_vide():
            raise IndexError("La pile est vide")
        return self._elements[-1]

    def est_vide(self):
        """Vérifie si la pile est vide — O(1)."""
        return len(self._elements) == 0

    def taille(self):
        """Retourne le nombre d'éléments — O(1)."""
        return len(self._elements)


# Utilisation
pile = Pile()
pile.empiler(10)
pile.empiler(20)
pile.empiler(30)
print(pile.sommet())  # 30
print(pile.depiler())  # 30
print(pile.depiler())  # 20
```

**Cas d'usage courants** :
- Gestion de l'historique (undo/redo)
- Évaluation d'expressions mathématiques
- Vérification de parenthèses équilibrées
- Parcours en profondeur (DFS) dans les graphes

#### Exemple pratique : vérifier les parenthèses

```python
def parentheses_valides(expression: str) -> bool:
    """Vérifie si les parenthèses sont correctement équilibrées."""
    pile = Pile()
    correspondances = {")": "(", "]": "[", "}": "{"}

    for caractere in expression:
        if caractere in "([{":
            pile.empiler(caractere)
        elif caractere in ")]}":
            if pile.est_vide():
                return False
            if pile.depiler() != correspondances[caractere]:
                return False

    return pile.est_vide()


# Tests
print(parentheses_valides("(([{}]))"))   # True
print(parentheses_valides("([)]"))       # False
print(parentheses_valides("((())"))      # False
```

### 2.4 File (Queue) — FIFO

La file fonctionne en **First In, First Out** : le premier élément ajouté est le premier retiré.

```
enfiler →  ┌────┬────┬────┬────┐  → défiler
           │ 40 │ 30 │ 20 │ 10 │
           └────┴────┴────┴────┘
          Arrière              Avant
```

> 💡 **Analogie** : Une file d'attente au supermarché. Le premier arrivé est le premier servi.

```python
from collections import deque


class File:
    """Implémentation d'une file avec deque pour des performances O(1)."""

    def __init__(self):
        self._elements = deque()

    def enfiler(self, valeur):
        """Ajoute un élément à l'arrière — O(1)."""
        self._elements.append(valeur)

    def defiler(self):
        """Retire et retourne l'élément à l'avant — O(1)."""
        if self.est_vide():
            raise IndexError("La file est vide")
        return self._elements.popleft()

    def avant(self):
        """Retourne l'élément à l'avant sans le retirer — O(1)."""
        if self.est_vide():
            raise IndexError("La file est vide")
        return self._elements[0]

    def est_vide(self):
        return len(self._elements) == 0

    def taille(self):
        return len(self._elements)


# Utilisation
file = File()
file.enfiler("Tâche A")
file.enfiler("Tâche B")
file.enfiler("Tâche C")
print(file.defiler())  # Tâche A
print(file.defiler())  # Tâche B
```

> ⚠️ **Attention** : En Python, n'utilisez jamais `list.pop(0)` pour une file — c'est O(n) car tous les éléments sont décalés. Utilisez `collections.deque` qui offre `popleft()` en O(1).

**Cas d'usage courants** :
- Files de messages (Kafka, RabbitMQ)
- Ordonnancement de tâches (pipelines data)
- Parcours en largeur (BFS) dans les graphes
- Buffers de données

---

## 3. 🗂️ Table de hachage (Hash Table)

### 3.1 Principe

Une table de hachage associe des **clés** à des **valeurs** via une **fonction de hachage**. Elle permet des opérations en O(1) en moyenne.

```
Clé        Fonction      Index    Valeur
           de hachage
"Paris"  ──→  hash()  ──→  3  ──→ "France"
"Berlin" ──→  hash()  ──→  7  ──→ "Allemagne"
"Madrid" ──→  hash()  ──→  1  ──→ "Espagne"
"Rome"   ──→  hash()  ──→  5  ──→ "Italie"
```

### 3.2 Fonctionnement interne

1. La clé est passée dans une **fonction de hachage** qui produit un entier
2. Cet entier est converti en **index** dans un tableau interne
3. La valeur est stockée à cet index

```python
# Exemple simplifié d'une fonction de hachage
def hash_simple(cle: str, taille_table: int) -> int:
    """Fonction de hachage simple basée sur la somme des codes ASCII."""
    return sum(ord(c) for c in cle) % taille_table


print(hash_simple("Paris", 10))   # Un index entre 0 et 9
print(hash_simple("Berlin", 10))  # Un autre index
```

### 3.3 Gestion des collisions

Quand deux clés produisent le même index, il y a **collision**. Deux stratégies principales :

**Chaînage** : chaque case du tableau contient une liste de paires (clé, valeur).

```
Index 0: []
Index 1: [("Madrid", "Espagne")]
Index 2: []
Index 3: [("Paris", "France"), ("Tokyo", "Japon")]  ← collision
Index 4: []
```

**Adressage ouvert** : on cherche la prochaine case libre.

### 3.4 En Python : le dictionnaire

Le `dict` Python est une table de hachage optimisée.

```python
# Le dict est la structure la plus utilisée en Python
capitales = {
    "France": "Paris",
    "Allemagne": "Berlin",
    "Espagne": "Madrid",
}

# Accès — O(1) en moyenne
print(capitales["France"])  # Paris

# Insertion — O(1) en moyenne
capitales["Italie"] = "Rome"

# Recherche — O(1) en moyenne
print("France" in capitales)  # True

# Suppression — O(1) en moyenne
del capitales["Espagne"]
```

> 💡 **Pour le Data Engineer** : Les dictionnaires sont essentiels pour les lookups rapides. Quand vous devez enrichir des données avec des jointures en Python, utilisez un dict plutôt qu'une boucle imbriquée.

```python
# ❌ Mauvais : O(n × m) — double boucle
def enrichir_lent(commandes, clients):
    for commande in commandes:
        for client in clients:
            if client["id"] == commande["client_id"]:
                commande["nom_client"] = client["nom"]

# ✅ Bon : O(n + m) — lookup par dictionnaire
def enrichir_rapide(commandes, clients):
    clients_dict = {c["id"]: c["nom"] for c in clients}  # O(m)
    for commande in commandes:                             # O(n)
        commande["nom_client"] = clients_dict.get(commande["client_id"])
```

---

## 4. 🌳 Arbres

### 4.1 Concepts de base

Un arbre est une structure **hiérarchique** composée de nœuds reliés par des arêtes, avec un nœud racine unique.

```
            ┌───┐
            │ A │  ← Racine
            └─┬─┘
          ┌───┴───┐
        ┌─┴─┐   ┌─┴─┐
        │ B │   │ C │  ← Nœuds internes
        └─┬─┘   └─┬─┘
       ┌──┴──┐    │
     ┌─┴─┐┌─┴─┐┌─┴─┐
     │ D ││ E ││ F │  ← Feuilles
     └───┘└───┘└───┘
```

**Vocabulaire** :

| Terme | Définition |
|-------|-----------|
| **Racine** | Nœud sans parent (sommet de l'arbre) |
| **Feuille** | Nœud sans enfant |
| **Nœud interne** | Nœud avec au moins un enfant |
| **Profondeur** | Distance d'un nœud à la racine |
| **Hauteur** | Plus grande profondeur de l'arbre |
| **Sous-arbre** | Arbre formé par un nœud et ses descendants |

### 4.2 Arbre binaire

Un arbre binaire est un arbre où chaque nœud a **au maximum 2 enfants** (gauche et droit).

```python
class NoeudBinaire:
    """Nœud d'un arbre binaire."""

    def __init__(self, valeur, gauche=None, droit=None):
        self.valeur = valeur
        self.gauche = gauche
        self.droit = droit


# Construction d'un arbre
#        10
#       /  \
#      5    15
#     / \     \
#    3   7    20

arbre = NoeudBinaire(
    10,
    gauche=NoeudBinaire(
        5,
        gauche=NoeudBinaire(3),
        droit=NoeudBinaire(7),
    ),
    droit=NoeudBinaire(
        15,
        droit=NoeudBinaire(20),
    ),
)
```

### 4.3 Arbre binaire de recherche (BST)

Un **BST** (Binary Search Tree) respecte la propriété : pour chaque nœud, tous les éléments du sous-arbre gauche sont **plus petits** et ceux du sous-arbre droit sont **plus grands**.

```python
class ArbreBinaireRecherche:
    """Arbre binaire de recherche."""

    def __init__(self):
        self.racine = None

    def inserer(self, valeur):
        """Insère une valeur dans l'arbre — O(log n) en moyenne."""
        self.racine = self._inserer_recursif(self.racine, valeur)

    def _inserer_recursif(self, noeud, valeur):
        if noeud is None:
            return NoeudBinaire(valeur)
        if valeur < noeud.valeur:
            noeud.gauche = self._inserer_recursif(noeud.gauche, valeur)
        elif valeur > noeud.valeur:
            noeud.droit = self._inserer_recursif(noeud.droit, valeur)
        return noeud

    def rechercher(self, valeur):
        """Recherche une valeur — O(log n) en moyenne."""
        return self._rechercher_recursif(self.racine, valeur)

    def _rechercher_recursif(self, noeud, valeur):
        if noeud is None:
            return False
        if valeur == noeud.valeur:
            return True
        if valeur < noeud.valeur:
            return self._rechercher_recursif(noeud.gauche, valeur)
        return self._rechercher_recursif(noeud.droit, valeur)

    def parcours_infixe(self):
        """Parcours infixe (gauche, racine, droit) → éléments triés."""
        elements = []
        self._infixe(self.racine, elements)
        return elements

    def _infixe(self, noeud, elements):
        if noeud:
            self._infixe(noeud.gauche, elements)
            elements.append(noeud.valeur)
            self._infixe(noeud.droit, elements)


# Utilisation
bst = ArbreBinaireRecherche()
for val in [10, 5, 15, 3, 7, 20]:
    bst.inserer(val)

print(bst.rechercher(7))       # True
print(bst.rechercher(12))      # False
print(bst.parcours_infixe())   # [3, 5, 7, 10, 15, 20] — trié !
```

### 4.4 Parcours d'arbres

Trois parcours classiques pour un arbre binaire :

| Parcours | Ordre | Utilisation |
|----------|-------|-------------|
| **Préfixe** (pré-order) | Racine → Gauche → Droit | Copie d'arbre, sérialisation |
| **Infixe** (in-order) | Gauche → Racine → Droit | Obtenir les éléments triés (BST) |
| **Postfixe** (post-order) | Gauche → Droit → Racine | Suppression d'arbre, évaluation |

```python
def parcours_prefixe(noeud):
    if noeud:
        print(noeud.valeur, end=" ")
        parcours_prefixe(noeud.gauche)
        parcours_prefixe(noeud.droit)


def parcours_infixe(noeud):
    if noeud:
        parcours_infixe(noeud.gauche)
        print(noeud.valeur, end=" ")
        parcours_infixe(noeud.droit)


def parcours_postfixe(noeud):
    if noeud:
        parcours_postfixe(noeud.gauche)
        parcours_postfixe(noeud.droit)
        print(noeud.valeur, end=" ")
```

> 💡 **Pour le Data Engineer** : Les arbres B (B-trees) sont la structure utilisée par les **index de bases de données**. Comprendre les arbres aide à comprendre pourquoi un index accélère les requêtes de O(n) à O(log n).

---

## 5. 🕸️ Graphes

### 5.1 Concepts de base

Un graphe est un ensemble de **sommets** (nœuds) reliés par des **arêtes** (liens).

```
Non orienté :          Orienté (digraphe) :

  A --- B                A --> B
  |     |                |     |
  |     |                ▼     ▼
  C --- D                C --> D
```

**Vocabulaire** :

| Terme | Définition |
|-------|-----------|
| **Sommet / Nœud** | Entité du graphe |
| **Arête** | Lien entre deux sommets (non orienté) |
| **Arc** | Lien orienté entre deux sommets |
| **Degré** | Nombre d'arêtes connectées à un sommet |
| **Chemin** | Séquence de sommets reliés par des arêtes |
| **Cycle** | Chemin dont le début et la fin sont identiques |
| **Graphe pondéré** | Graphe dont les arêtes ont des poids |
| **DAG** | Directed Acyclic Graph — graphe orienté sans cycle |

> 💡 **Pour le Data Engineer** : Les DAG (Directed Acyclic Graphs) sont partout en data engineering ! Apache Airflow utilise des DAG pour ordonnancer les tâches, dbt modélise les dépendances entre modèles comme un DAG, et Spark optimise les plans d'exécution comme des DAG.

### 5.2 Représentation

#### Liste d'adjacence (la plus utilisée)

```python
# Graphe non orienté avec liste d'adjacence (dict)
graphe = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C"],
}

# Graphe orienté pondéré
graphe_pondere = {
    "Paris": [("Lyon", 465), ("Marseille", 775)],
    "Lyon": [("Marseille", 315)],
    "Marseille": [],
}
```

#### Matrice d'adjacence

```python
import numpy as np

#     A  B  C  D
# A [ 0, 1, 1, 0 ]
# B [ 1, 0, 0, 1 ]
# C [ 1, 0, 0, 1 ]
# D [ 0, 1, 1, 0 ]

matrice = np.array([
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 0],
])
```

**Comparaison** :

| Aspect | Liste d'adjacence | Matrice d'adjacence |
|--------|------------------|---------------------|
| Mémoire | O(V + E) | O(V²) |
| Vérifier si arête existe | O(degré) | O(1) |
| Lister les voisins | O(degré) | O(V) |
| Graphe creux | ✅ Efficace | ❌ Gaspillage |
| Graphe dense | ❌ Moins efficace | ✅ Adapté |

> V = nombre de sommets, E = nombre d'arêtes

### 5.3 Implémentation d'un graphe

```python
class Graphe:
    """Graphe non orienté avec liste d'adjacence."""

    def __init__(self):
        self.adjacence = {}

    def ajouter_sommet(self, sommet):
        """Ajoute un sommet au graphe."""
        if sommet not in self.adjacence:
            self.adjacence[sommet] = []

    def ajouter_arete(self, sommet1, sommet2):
        """Ajoute une arête entre deux sommets."""
        self.ajouter_sommet(sommet1)
        self.ajouter_sommet(sommet2)
        self.adjacence[sommet1].append(sommet2)
        self.adjacence[sommet2].append(sommet1)

    def voisins(self, sommet):
        """Retourne les voisins d'un sommet."""
        return self.adjacence.get(sommet, [])

    def afficher(self):
        """Affiche le graphe."""
        for sommet, voisins in self.adjacence.items():
            print(f"{sommet} -> {voisins}")


# Utilisation
g = Graphe()
g.ajouter_arete("A", "B")
g.ajouter_arete("A", "C")
g.ajouter_arete("B", "D")
g.ajouter_arete("C", "D")
g.afficher()
# A -> ['B', 'C']
# B -> ['A', 'D']
# C -> ['A', 'D']
# D -> ['B', 'C']
```

---

## 6. 📋 Résumé comparatif

| Structure | Accès | Insertion | Suppression | Recherche | Cas d'usage |
|-----------|-------|-----------|-------------|-----------|-------------|
| **Tableau** | O(1) | O(n) | O(n) | O(n) | Accès indexé, parcours |
| **Liste chaînée** | O(n) | O(1)* | O(1)* | O(n) | Insertions fréquentes |
| **Pile** | O(1)** | O(1) | O(1) | O(n) | LIFO, undo, DFS |
| **File** | O(1)** | O(1) | O(1) | O(n) | FIFO, BFS, messages |
| **Table de hachage** | O(1) | O(1) | O(1) | O(1) | Lookups, comptages |
| **BST** | O(log n) | O(log n) | O(log n) | O(log n) | Données triées |
| **Graphe** | — | O(1) | O(E) | O(V+E) | Relations, réseaux |

> \* Si on a un pointeur vers le nœud
> \*\* Accès uniquement au sommet/avant

---

## ✅ Checklist de validation

Avant de passer au module suivant, vérifiez que vous pouvez :

- [ ] Expliquer la différence entre un tableau et une liste chaînée
- [ ] Implémenter une pile et une file en Python
- [ ] Expliquer le principe de hachage et les collisions
- [ ] Choisir entre `list`, `dict` et `set` selon le besoin
- [ ] Dessiner un arbre binaire et identifier racine, feuilles, profondeur
- [ ] Implémenter un arbre binaire de recherche basique
- [ ] Représenter un graphe par liste d'adjacence
- [ ] Distinguer graphe orienté, non orienté, pondéré et DAG

---

[← Introduction](01-introduction.md) | [🏠 Accueil](../README.md) | [Suivant → Algorithmes de tri](03-algorithmes-de-tri.md)
