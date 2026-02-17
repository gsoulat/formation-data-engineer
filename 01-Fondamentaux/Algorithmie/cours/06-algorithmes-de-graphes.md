# Module 06 — Algorithmes de graphes

## 🎯 Objectifs

- Maîtriser l'algorithme de Dijkstra pour le plus court chemin pondéré
- Comprendre les algorithmes d'arbre couvrant minimum (Prim, Kruskal)
- Appliquer les algorithmes de graphes à des problèmes de data engineering
- Comprendre les DAG et leur importance dans les pipelines de données

---

## 1. 🛤️ Plus court chemin : Dijkstra

### 1.1 Problème

Trouver le **plus court chemin** entre un sommet source et tous les autres sommets dans un graphe **pondéré avec des poids positifs**.

> 💡 BFS trouve le plus court chemin en nombre d'arêtes. Dijkstra trouve le plus court chemin en **somme des poids**.

### 1.2 Principe

1. Initialiser la distance de la source à 0, toutes les autres à ∞
2. Marquer tous les sommets comme non visités
3. Choisir le sommet non visité avec la plus petite distance
4. Mettre à jour les distances de ses voisins
5. Marquer le sommet comme visité
6. Répéter jusqu'à ce que tous les sommets soient visités

### 1.3 Visualisation

```
Graphe pondéré :

     A ──(4)── B
     |         |
    (1)       (2)
     |         |
     C ──(5)── D ──(3)── E
     |                    |
    (8)                  (1)
     |                    |
     F ────────(6)────── G

Dijkstra depuis A :

Étape 1 : A=0, B=∞, C=∞, D=∞, E=∞, F=∞, G=∞
          Visite A → met à jour B=4, C=1

Étape 2 : A=0, B=4, C=1*, D=∞, E=∞, F=∞, G=∞
          Visite C (plus petit) → met à jour D=6, F=9

Étape 3 : A=0, B=4*, C=1, D=6, E=∞, F=9, G=∞
          Visite B → met à jour D=min(6, 4+2)=6

Étape 4 : A=0, B=4, C=1, D=6*, E=∞, F=9, G=∞
          Visite D → met à jour E=9

Étape 5 : A=0, B=4, C=1, D=6, E=9*, F=9, G=∞
          Visite E → met à jour G=10

Étape 6 : A=0, B=4, C=1, D=6, E=9, F=9*, G=10
          Visite F → G=min(10, 9+6)=10

Résultat : A→C=1, A→B=4, A→D=6, A→E=9, A→F=9, A→G=10
```

### 1.4 Implémentation

```python
import heapq


def dijkstra(graphe: dict, source: str) -> tuple[dict, dict]:
    """
    Algorithme de Dijkstra — O((V + E) log V) avec heap.

    Args:
        graphe: dict de listes d'adjacence {sommet: [(voisin, poids), ...]}
        source: sommet de départ

    Returns:
        (distances, predecesseurs) pour reconstruire les chemins
    """
    # Initialisation
    distances = {sommet: float("inf") for sommet in graphe}
    distances[source] = 0
    predecesseurs = {sommet: None for sommet in graphe}

    # File de priorité (min-heap) : (distance, sommet)
    heap = [(0, source)]
    visite = set()

    while heap:
        dist_courante, sommet = heapq.heappop(heap)

        if sommet in visite:
            continue
        visite.add(sommet)

        for voisin, poids in graphe.get(sommet, []):
            nouvelle_dist = dist_courante + poids

            if nouvelle_dist < distances[voisin]:
                distances[voisin] = nouvelle_dist
                predecesseurs[voisin] = sommet
                heapq.heappush(heap, (nouvelle_dist, voisin))

    return distances, predecesseurs


def reconstruire_chemin(predecesseurs: dict, destination: str) -> list[str]:
    """Reconstruit le chemin depuis la source vers la destination."""
    chemin = []
    courant = destination

    while courant is not None:
        chemin.append(courant)
        courant = predecesseurs[courant]

    return list(reversed(chemin))


# Exemple
graphe = {
    "A": [("B", 4), ("C", 1)],
    "B": [("A", 4), ("D", 2)],
    "C": [("A", 1), ("D", 5), ("F", 8)],
    "D": [("B", 2), ("C", 5), ("E", 3)],
    "E": [("D", 3), ("G", 1)],
    "F": [("C", 8), ("G", 6)],
    "G": [("E", 1), ("F", 6)],
}

distances, predecesseurs = dijkstra(graphe, "A")
print("Distances depuis A :", distances)
# {'A': 0, 'B': 4, 'C': 1, 'D': 6, 'E': 9, 'F': 9, 'G': 10}

print("Chemin A → G :", reconstruire_chemin(predecesseurs, "G"))
# ['A', 'C', 'D', 'E', 'G']
```

### 1.5 Complexité

| Implémentation | Complexité |
|----------------|-----------|
| Avec tableau (recherche linéaire du min) | O(V²) |
| Avec heap binaire | O((V + E) log V) |
| Avec heap de Fibonacci | O(E + V log V) |

> ⚠️ **Limitation** : Dijkstra ne fonctionne **pas avec des poids négatifs**. Pour les poids négatifs, utiliser l'algorithme de Bellman-Ford.

---

## 2. 🌲 Arbre couvrant minimum (MST)

### 2.1 Définition

Un **arbre couvrant minimum** (Minimum Spanning Tree) est un sous-ensemble d'arêtes qui connecte tous les sommets d'un graphe avec le **poids total minimal**, sans former de cycle.

```
Graphe original :                Arbre couvrant minimum :

  A──(4)──B                        A       B
  |       |                        |       |
 (1)     (2)                      (1)     (2)
  |       |                        |       |
  C──(5)──D──(3)──E                C       D──(3)──E

Poids total : 4+1+2+5+3 = 15      Poids MST : 1+2+3 = 6 (+ une arête pour A-B)
```

> 💡 **Pour le Data Engineer** : Les MST sont utilisés pour optimiser les réseaux (minimiser les coûts de câblage, de connexion entre data centers, etc.).

### 2.2 Algorithme de Kruskal

**Principe** : Trier toutes les arêtes par poids croissant, puis les ajouter une par une si elles ne créent pas de cycle.

Utilise la structure **Union-Find** pour détecter les cycles efficacement.

```python
class UnionFind:
    """Structure Union-Find (Disjoint Set) pour Kruskal."""

    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rang = {e: 0 for e in elements}

    def trouver(self, x):
        """Trouve la racine de x avec compression de chemin."""
        if self.parent[x] != x:
            self.parent[x] = self.trouver(self.parent[x])
        return self.parent[x]

    def unir(self, x, y) -> bool:
        """Unit les ensembles de x et y. Retourne False si déjà unis (cycle)."""
        racine_x = self.trouver(x)
        racine_y = self.trouver(y)

        if racine_x == racine_y:
            return False  # Même composante → ajout créerait un cycle

        # Union par rang
        if self.rang[racine_x] < self.rang[racine_y]:
            self.parent[racine_x] = racine_y
        elif self.rang[racine_x] > self.rang[racine_y]:
            self.parent[racine_y] = racine_x
        else:
            self.parent[racine_y] = racine_x
            self.rang[racine_x] += 1

        return True


def kruskal(sommets: list, aretes: list[tuple]) -> list[tuple]:
    """
    Algorithme de Kruskal — O(E log E).

    Args:
        sommets: liste des sommets
        aretes: liste de (poids, sommet1, sommet2)

    Returns:
        Liste des arêtes du MST
    """
    # Trier les arêtes par poids
    aretes_triees = sorted(aretes, key=lambda a: a[0])

    uf = UnionFind(sommets)
    mst = []

    for poids, u, v in aretes_triees:
        if uf.unir(u, v):
            mst.append((poids, u, v))
            if len(mst) == len(sommets) - 1:
                break  # MST complet

    return mst


# Exemple
sommets = ["A", "B", "C", "D", "E"]
aretes = [
    (4, "A", "B"),
    (1, "A", "C"),
    (2, "B", "D"),
    (5, "C", "D"),
    (3, "D", "E"),
    (7, "B", "E"),
]

mst = kruskal(sommets, aretes)
print("Arêtes du MST :", mst)
# [(1, 'A', 'C'), (2, 'B', 'D'), (3, 'D', 'E'), (4, 'A', 'B')]

poids_total = sum(p for p, _, _ in mst)
print(f"Poids total : {poids_total}")  # 10
```

### 2.3 Algorithme de Prim

**Principe** : Partir d'un sommet et ajouter à chaque étape l'arête de poids minimal qui connecte un sommet de l'arbre à un sommet extérieur.

```python
def prim(graphe: dict, depart: str) -> list[tuple]:
    """
    Algorithme de Prim — O((V + E) log V) avec heap.

    Args:
        graphe: dict de listes d'adjacence {sommet: [(voisin, poids), ...]}
        depart: sommet de départ

    Returns:
        Liste des arêtes du MST [(poids, source, destination)]
    """
    visite = {depart}
    mst = []

    # Heap : (poids, sommet_source, sommet_destination)
    heap = [(poids, depart, voisin) for voisin, poids in graphe[depart]]
    heapq.heapify(heap)

    while heap and len(visite) < len(graphe):
        poids, source, dest = heapq.heappop(heap)

        if dest in visite:
            continue

        visite.add(dest)
        mst.append((poids, source, dest))

        for voisin, p in graphe[dest]:
            if voisin not in visite:
                heapq.heappush(heap, (p, dest, voisin))

    return mst


# Exemple (même graphe, format adjacence)
graphe = {
    "A": [("B", 4), ("C", 1)],
    "B": [("A", 4), ("D", 2), ("E", 7)],
    "C": [("A", 1), ("D", 5)],
    "D": [("B", 2), ("C", 5), ("E", 3)],
    "E": [("B", 7), ("D", 3)],
}

mst = prim(graphe, "A")
print("MST (Prim) :", mst)
poids_total = sum(p for p, _, _ in mst)
print(f"Poids total : {poids_total}")
```

### 2.4 Kruskal vs Prim

| Aspect | Kruskal | Prim |
|--------|---------|------|
| **Approche** | Globale (toutes les arêtes) | Locale (croissance depuis un sommet) |
| **Complexité** | O(E log E) | O((V + E) log V) |
| **Meilleur pour** | Graphes creux (peu d'arêtes) | Graphes denses (beaucoup d'arêtes) |
| **Structure** | Union-Find | Heap (file de priorité) |

---

## 3. 📊 Algorithmes de graphes pour le Data Engineering

### 3.1 Tri topologique et ordonnancement de pipelines

Le tri topologique (vu au module 04) est la base des orchestrateurs de données.

```python
def ordonnancer_pipeline(taches: dict) -> list[str]:
    """
    Ordonnance les tâches d'un pipeline en respectant les dépendances.
    Utilise l'algorithme de Kahn (BFS-based topological sort).

    Args:
        taches: {tache: [dependances]}

    Returns:
        Ordre d'exécution
    """
    from collections import deque

    # Calculer le degré entrant de chaque tâche
    degre_entrant = {t: 0 for t in taches}
    for tache, deps in taches.items():
        for dep in deps:
            degre_entrant[tache] = degre_entrant.get(tache, 0)

    # Construire le graphe inversé (dépendance → tâche)
    graphe = {t: [] for t in taches}
    for tache, deps in taches.items():
        for dep in deps:
            graphe[dep].append(tache)
            degre_entrant[tache] += 1

    # Commencer par les tâches sans dépendances
    file = deque([t for t, d in degre_entrant.items() if d == 0])
    ordre = []

    while file:
        tache = file.popleft()
        ordre.append(tache)

        for suivante in graphe[tache]:
            degre_entrant[suivante] -= 1
            if degre_entrant[suivante] == 0:
                file.append(suivante)

    if len(ordre) != len(taches):
        raise ValueError("Cycle détecté dans le pipeline !")

    return ordre


# Pipeline de données typique
pipeline = {
    "extract_clients": [],
    "extract_commandes": [],
    "clean_clients": ["extract_clients"],
    "clean_commandes": ["extract_commandes"],
    "join_client_commande": ["clean_clients", "clean_commandes"],
    "aggregate_ventes": ["join_client_commande"],
    "export_dashboard": ["aggregate_ventes"],
    "export_rapport": ["aggregate_ventes"],
}

ordre = ordonnancer_pipeline(pipeline)
print("Ordre d'exécution :")
for i, tache in enumerate(ordre, 1):
    print(f"  {i}. {tache}")
```

### 3.2 Détection de composantes connexes

Identifier des groupes isolés dans les données (clustering, détection de communautés).

```python
def composantes_connexes(graphe: dict) -> list[set]:
    """Trouve toutes les composantes connexes d'un graphe — O(V + E)."""
    visite = set()
    composantes = []

    def dfs(sommet, composante):
        visite.add(sommet)
        composante.add(sommet)
        for voisin in graphe.get(sommet, []):
            if voisin not in visite:
                dfs(voisin, composante)

    for sommet in graphe:
        if sommet not in visite:
            composante = set()
            dfs(sommet, composante)
            composantes.append(composante)

    return composantes


# Exemple : réseau social
reseau = {
    "Alice": ["Bob", "Charlie"],
    "Bob": ["Alice"],
    "Charlie": ["Alice"],
    "David": ["Eve"],
    "Eve": ["David"],
    "Frank": [],
}

groupes = composantes_connexes(reseau)
print(f"Nombre de groupes : {len(groupes)}")
for i, groupe in enumerate(groupes, 1):
    print(f"  Groupe {i} : {groupe}")
# Groupe 1 : {'Alice', 'Bob', 'Charlie'}
# Groupe 2 : {'David', 'Eve'}
# Groupe 3 : {'Frank'}
```

### 3.3 PageRank simplifié

Le principe de base de l'algorithme de Google.

```python
def pagerank(graphe: dict, iterations: int = 20, damping: float = 0.85) -> dict:
    """
    Algorithme PageRank simplifié.

    Args:
        graphe: {page: [pages_liées]}
        iterations: nombre d'itérations
        damping: facteur d'amortissement (typiquement 0.85)

    Returns:
        Scores PageRank pour chaque page
    """
    n = len(graphe)
    scores = {page: 1.0 / n for page in graphe}

    for _ in range(iterations):
        nouveaux_scores = {}
        for page in graphe:
            # Score reçu des pages qui pointent vers cette page
            score_entrant = 0
            for autre_page, liens in graphe.items():
                if page in liens:
                    score_entrant += scores[autre_page] / len(liens)

            nouveaux_scores[page] = (1 - damping) / n + damping * score_entrant

        scores = nouveaux_scores

    return scores


# Exemple : mini web
web = {
    "page_A": ["page_B", "page_C"],
    "page_B": ["page_C"],
    "page_C": ["page_A"],
    "page_D": ["page_C"],
}

scores = pagerank(web)
for page, score in sorted(scores.items(), key=lambda x: -x[1]):
    print(f"  {page}: {score:.4f}")
```

---

## 4. 🔧 La bibliothèque NetworkX

Pour les cas réels, utilisez `networkx` plutôt que de tout implémenter :

```python
# pip install networkx
import networkx as nx

# Créer un graphe
G = nx.Graph()
G.add_weighted_edges_from([
    ("Paris", "Lyon", 465),
    ("Paris", "Marseille", 775),
    ("Lyon", "Marseille", 315),
    ("Lyon", "Toulouse", 540),
    ("Marseille", "Toulouse", 405),
    ("Toulouse", "Bordeaux", 245),
    ("Paris", "Bordeaux", 585),
])

# Plus court chemin (Dijkstra)
chemin = nx.dijkstra_path(G, "Paris", "Toulouse")
distance = nx.dijkstra_path_length(G, "Paris", "Toulouse")
print(f"Plus court chemin Paris → Toulouse : {chemin} ({distance} km)")

# Arbre couvrant minimum
mst = nx.minimum_spanning_tree(G)
print(f"Poids MST : {mst.size(weight='weight')} km")

# Composantes connexes
print(f"Composantes : {nx.number_connected_components(G)}")

# Centralité (importance des nœuds)
centralite = nx.betweenness_centrality(G)
for ville, score in sorted(centralite.items(), key=lambda x: -x[1]):
    print(f"  {ville}: {score:.3f}")
```

> 💡 **Pour le Data Engineer** : En production, utilisez toujours des bibliothèques éprouvées (`networkx`, `igraph`, `graph-tool`) plutôt que des implémentations maison. Vos implémentations maison sont pour l'apprentissage.

---

## 5. 📋 Résumé des algorithmes de graphes

| Algorithme | Problème | Complexité | Cas d'usage DE |
|------------|----------|-----------|----------------|
| **BFS** | Plus court chemin (non pondéré) | O(V + E) | Parcours de DAG |
| **DFS** | Exploration, cycle, tri topo | O(V + E) | Dépendances dbt/Airflow |
| **Dijkstra** | Plus court chemin (pondéré) | O((V+E) log V) | Routage réseau |
| **Kruskal** | MST | O(E log E) | Optimisation réseau |
| **Prim** | MST | O((V+E) log V) | Optimisation réseau |
| **Kahn** | Tri topologique | O(V + E) | Ordonnancement pipeline |
| **PageRank** | Importance des nœuds | O(V + E) × iter | Ranking, recommandation |

---

## ✅ Checklist de validation

Avant de passer aux exercices, vérifiez que vous pouvez :

- [ ] Expliquer l'algorithme de Dijkstra et ses limitations
- [ ] Implémenter Dijkstra avec une file de priorité
- [ ] Expliquer la différence entre Kruskal et Prim
- [ ] Appliquer le tri topologique à un pipeline de données
- [ ] Détecter des composantes connexes dans un graphe
- [ ] Utiliser NetworkX pour résoudre des problèmes de graphes
- [ ] Identifier quels problèmes de data engineering sont des problèmes de graphes

---

[← Récursivité et PD](05-recursivite-programmation-dynamique.md) | [🏠 Accueil](../README.md) | [Suivant → Architecture et patterns](07-architecture-patterns.md)
