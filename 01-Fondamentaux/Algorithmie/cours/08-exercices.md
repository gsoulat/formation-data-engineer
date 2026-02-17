# Module 07 — Exercices pratiques

## 🎯 Objectifs

- Mettre en pratique les concepts vus dans les modules 01 à 06
- Résoudre des problèmes progressifs, du fondamental au concret
- Appliquer l'algorithmie à des cas réels de data engineering

> 💡 **Conseil** : Pour chaque exercice, commencez par écrire le pseudo-code avant de coder. Identifiez la complexité de votre solution et cherchez à l'optimiser si nécessaire.

---

## 🟢 Niveau 1 — Fondamentaux (Modules 01-02)

### Exercice 1.1 : Analyse de complexité

Déterminez la complexité temporelle (Big O) de chaque fonction :

```python
# Fonction A
def fonction_a(n):
    total = 0
    for i in range(n):
        total += i
    return total

# Fonction B
def fonction_b(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += i * j
    return total

# Fonction C
def fonction_c(n):
    total = 0
    i = n
    while i > 0:
        total += i
        i //= 2
    return total

# Fonction D
def fonction_d(n):
    total = 0
    for i in range(n):
        for j in range(i):
            total += 1
    return total

# Fonction E
def fonction_e(liste):
    if len(liste) <= 1:
        return liste
    milieu = len(liste) // 2
    return fonction_e(liste[:milieu]) + fonction_e(liste[milieu:])
```

**Questions** :
1. Quelle est la complexité de chaque fonction ?
2. Pour n = 1 000 000, quelles fonctions seraient utilisables en pratique ?

---

### Exercice 1.2 : Pile — Évaluateur d'expressions

Implémentez un évaluateur d'expressions en **notation polonaise inverse** (RPN).

En RPN, les opérateurs viennent après les opérandes :
- `3 4 +` → 7
- `5 3 - 2 *` → 4
- `2 3 + 4 *` → 20

```python
def evaluer_rpn(expression: str) -> float:
    """
    Évalue une expression en notation polonaise inverse.

    Args:
        expression: chaîne de tokens séparés par des espaces
                   Exemple : "3 4 + 2 *"

    Returns:
        Le résultat du calcul

    Indice :
        - Utilisez une pile
        - Si le token est un nombre, empilez-le
        - Si c'est un opérateur, dépilez 2 nombres, calculez, empilez le résultat
    """
    # À compléter
    pass


# Tests attendus
assert evaluer_rpn("3 4 +") == 7
assert evaluer_rpn("5 3 - 2 *") == 4
assert evaluer_rpn("2 3 + 4 *") == 20
assert evaluer_rpn("10 2 / 3 +") == 8
print("Tous les tests passent !")
```

---

### Exercice 1.3 : File — Simulation de file d'attente

Simulez une file d'attente de traitement de fichiers.

```python
from collections import deque
import random


def simuler_file_traitement(fichiers: list[dict]) -> list[dict]:
    """
    Simule le traitement de fichiers avec des priorités.

    Chaque fichier est un dict : {"nom": str, "taille_mo": int, "priorite": int}
    - Priorité 1 = haute, 2 = moyenne, 3 = basse

    Règles :
    - Traiter les fichiers par priorité (1 avant 2 avant 3)
    - À priorité égale, traiter dans l'ordre d'arrivée (FIFO)
    - Le temps de traitement = taille_mo * 0.1 secondes

    Returns:
        Liste des fichiers dans l'ordre de traitement,
        avec un champ "temps_debut" ajouté
    """
    # À compléter
    pass


# Test
fichiers = [
    {"nom": "data_clients.csv", "taille_mo": 100, "priorite": 2},
    {"nom": "logs_urgents.json", "taille_mo": 50, "priorite": 1},
    {"nom": "archive_2023.parquet", "taille_mo": 500, "priorite": 3},
    {"nom": "dim_produits.csv", "taille_mo": 10, "priorite": 1},
    {"nom": "fact_ventes.parquet", "taille_mo": 200, "priorite": 2},
]

resultat = simuler_file_traitement(fichiers)
for f in resultat:
    print(f"  [{f['priorite']}] {f['nom']} — début à {f['temps_debut']:.1f}s")
```

---

### Exercice 1.4 : Dictionnaire — Compteur de fréquences optimisé

```python
def top_n_mots(texte: str, n: int) -> list[tuple[str, int]]:
    """
    Retourne les n mots les plus fréquents d'un texte.

    Règles :
    - Ignorer la casse (tout en minuscule)
    - Ignorer la ponctuation
    - Ignorer les mots de moins de 3 caractères

    Quelle est la complexité de votre solution ?
    Pouvez-vous faire mieux que O(m log m) où m = nombre de mots uniques ?

    Indice : Utilisez un dictionnaire pour compter, puis heapq.nlargest()
    """
    # À compléter
    pass


# Test
texte = """
Le data engineer construit des pipelines de données.
Le data engineer transforme les données brutes en données exploitables.
Les données sont au coeur du travail du data engineer.
"""

print(top_n_mots(texte, 5))
# Attendu : [('données', 4), ('data', 3), ('engineer', 3), ...]
```

---

## 🟡 Niveau 2 — Intermédiaire (Modules 03-04)

### Exercice 2.1 : Tri personnalisé

```python
def tri_par_criteres(enregistrements: list[dict], criteres: list[tuple]) -> list[dict]:
    """
    Trie des enregistrements selon plusieurs critères.

    Args:
        enregistrements: liste de dictionnaires
        criteres: liste de (nom_champ, "asc"|"desc")

    Exemple :
        criteres = [("departement", "asc"), ("salaire", "desc")]
        → Trie par département croissant, puis par salaire décroissant

    Indice : Utilisez sorted() avec une clé composée.
    Comment gérer le tri décroissant pour les chaînes de caractères ?
    """
    # À compléter
    pass


# Test
employes = [
    {"nom": "Alice", "departement": "IT", "salaire": 55000, "anciennete": 3},
    {"nom": "Bob", "departement": "RH", "salaire": 48000, "anciennete": 5},
    {"nom": "Charlie", "departement": "IT", "salaire": 62000, "anciennete": 7},
    {"nom": "Diana", "departement": "RH", "salaire": 51000, "anciennete": 2},
    {"nom": "Eve", "departement": "IT", "salaire": 55000, "anciennete": 1},
]

resultat = tri_par_criteres(employes, [("departement", "asc"), ("salaire", "desc")])
for e in resultat:
    print(f"  {e['departement']} | {e['nom']:10s} | {e['salaire']}€")
# IT | Charlie   | 62000€
# IT | Alice     | 55000€
# IT | Eve       | 55000€
# RH | Diana     | 51000€
# RH | Bob       | 48000€
```

---

### Exercice 2.2 : Recherche binaire avancée

```python
def recherche_plage(liste_triee: list[int], min_val: int, max_val: int) -> list[int]:
    """
    Trouve tous les éléments dans [min_val, max_val] dans une liste triée.

    Complexité attendue : O(log n + k) où k = nombre de résultats
    (et non O(n) comme un parcours linéaire)

    Indice :
    - Utilisez bisect_left pour trouver le début de la plage
    - Utilisez bisect_right pour trouver la fin de la plage
    """
    # À compléter
    pass


# Test
donnees = list(range(0, 1000000, 3))  # [0, 3, 6, 9, ..., 999999]
resultat = recherche_plage(donnees, 100, 200)
print(f"Éléments entre 100 et 200 : {len(resultat)} trouvés")
print(f"Premier : {resultat[0]}, Dernier : {resultat[-1]}")
# Éléments entre 100 et 200 : 34 trouvés
# Premier : 102, Dernier : 198
```

---

### Exercice 2.3 : BFS — Degrés de séparation

```python
def degres_de_separation(reseau: dict, personne1: str, personne2: str) -> int | None:
    """
    Calcule le nombre de degrés de séparation entre deux personnes
    dans un réseau social.

    Retourne None si les personnes ne sont pas connectées.
    Retourne 0 si c'est la même personne.

    Indice : C'est un plus court chemin dans un graphe non pondéré → BFS
    """
    # À compléter
    pass


# Test
reseau_social = {
    "Alice": ["Bob", "Charlie"],
    "Bob": ["Alice", "David", "Eve"],
    "Charlie": ["Alice", "Frank"],
    "David": ["Bob"],
    "Eve": ["Bob", "Grace"],
    "Frank": ["Charlie"],
    "Grace": ["Eve"],
    "Henri": ["Isabelle"],  # Groupe isolé
    "Isabelle": ["Henri"],
}

print(degres_de_separation(reseau_social, "Alice", "Grace"))   # 3
print(degres_de_separation(reseau_social, "Alice", "Bob"))     # 1
print(degres_de_separation(reseau_social, "Alice", "Alice"))   # 0
print(degres_de_separation(reseau_social, "Alice", "Henri"))   # None
```

---

## 🔴 Niveau 3 — Avancé (Modules 05-06)

### Exercice 3.1 : Programmation dynamique — Découpe optimale

```python
def decoupe_optimale(longueur: int, prix: list[int]) -> tuple[int, list[int]]:
    """
    Problème de la découpe de barres (Rod Cutting Problem).

    Une barre de longueur n peut être découpée en morceaux.
    Chaque longueur de morceau a un prix.
    Trouver la découpe qui maximise le revenu total.

    Args:
        longueur: longueur de la barre
        prix: prix[i] = prix d'un morceau de longueur i+1

    Returns:
        (revenu_max, liste_des_longueurs_de_découpe)

    Exemple :
        prix = [1, 5, 8, 9, 10, 17, 17, 20]
        longueur = 4
        → Meilleure découpe : 2 + 2 = prix 5 + 5 = 10
          (mieux que 4 → prix 9)

    Indice :
        - Relation de récurrence : revenu(n) = max(prix[i] + revenu(n-i-1)) pour i de 0 à n-1
        - Utilisez la programmation dynamique bottom-up
        - Gardez une trace des découpes pour reconstruire la solution
    """
    # À compléter
    pass


# Test
prix = [1, 5, 8, 9, 10, 17, 17, 20]

for longueur in range(1, 9):
    revenu, decoupes = decoupe_optimale(longueur, prix)
    print(f"  Longueur {longueur} : revenu max = {revenu}, découpe = {decoupes}")
```

---

### Exercice 3.2 : Graphe — Chemin critique d'un pipeline

```python
def chemin_critique(taches: dict[str, dict]) -> tuple[list[str], int]:
    """
    Trouve le chemin critique d'un projet / pipeline de données.

    Le chemin critique est le plus long chemin dans un DAG pondéré,
    qui détermine la durée minimale totale du projet.

    Args:
        taches: {
            "nom_tache": {
                "duree": int,         # durée en minutes
                "dependances": [str]  # tâches qui doivent être finies avant
            }
        }

    Returns:
        (chemin_critique, duree_totale)

    Indice :
        1. Faire un tri topologique
        2. Calculer le temps de début au plus tôt pour chaque tâche
        3. Le chemin critique = le chemin avec le temps le plus long
    """
    # À compléter
    pass


# Pipeline de données réaliste
pipeline = {
    "extract_postgres": {"duree": 10, "dependances": []},
    "extract_api": {"duree": 15, "dependances": []},
    "extract_s3": {"duree": 5, "dependances": []},
    "clean_postgres": {"duree": 20, "dependances": ["extract_postgres"]},
    "clean_api": {"duree": 8, "dependances": ["extract_api"]},
    "clean_s3": {"duree": 3, "dependances": ["extract_s3"]},
    "join_pg_api": {"duree": 25, "dependances": ["clean_postgres", "clean_api"]},
    "enrich_with_s3": {"duree": 10, "dependances": ["join_pg_api", "clean_s3"]},
    "aggregate": {"duree": 15, "dependances": ["enrich_with_s3"]},
    "export_bq": {"duree": 5, "dependances": ["aggregate"]},
    "export_dashboard": {"duree": 3, "dependances": ["aggregate"]},
    "send_alert": {"duree": 1, "dependances": ["export_bq", "export_dashboard"]},
}

chemin, duree = chemin_critique(pipeline)
print(f"Chemin critique : {' → '.join(chemin)}")
print(f"Durée totale minimale : {duree} minutes")
```

---

### Exercice 3.3 : Graphe — Détection d'anomalies dans les dépendances

```python
def analyser_dependances(modeles: dict[str, list[str]]) -> dict:
    """
    Analyse les dépendances d'un projet dbt et détecte des problèmes.

    Args:
        modeles: {nom_modele: [modeles_dont_il_dépend]}

    Returns:
        {
            "cycles": list[list[str]],          # Cycles détectés
            "orphelins": list[str],              # Modèles sans dépendances entrantes ni sortantes
            "profondeur_max": int,               # Plus longue chaîne de dépendances
            "modeles_critiques": list[str],      # Modèles dont le plus grand nombre dépend
            "ordre_compilation": list[str],      # Ordre de compilation (tri topologique)
        }

    Indice :
        - Construisez le graphe et le graphe inversé
        - Utilisez DFS pour détecter les cycles
        - Comptez le degré sortant dans le graphe inversé pour les modèles critiques
        - Le plus long chemin dans un DAG = profondeur maximale
    """
    # À compléter
    pass


# Modèles dbt
modeles_dbt = {
    "stg_clients": [],
    "stg_commandes": [],
    "stg_produits": [],
    "stg_paiements": [],
    "int_commandes_enrichies": ["stg_commandes", "stg_produits"],
    "int_clients_enrichis": ["stg_clients", "stg_paiements"],
    "fct_ventes": ["int_commandes_enrichies", "int_clients_enrichis"],
    "dim_clients": ["int_clients_enrichis"],
    "dim_produits": ["stg_produits"],
    "agg_ventes_mensuelles": ["fct_ventes"],
    "agg_top_clients": ["fct_ventes", "dim_clients"],
    "rpt_dashboard": ["agg_ventes_mensuelles", "agg_top_clients", "dim_produits"],
}

analyse = analyser_dependances(modeles_dbt)
print(f"Cycles : {analyse['cycles']}")
print(f"Orphelins : {analyse['orphelins']}")
print(f"Profondeur max : {analyse['profondeur_max']}")
print(f"Modèles critiques : {analyse['modeles_critiques']}")
print(f"Ordre de compilation : {analyse['ordre_compilation']}")
```

---

## 🏆 Projet final — Moteur de recommandation simplifié

### Contexte

Vous êtes data engineer et devez implémenter un moteur de recommandation basé sur la **similarité collaborative**.

### Principe

Si Alice et Bob aiment les mêmes films, et Bob aime un film qu'Alice n'a pas vu, on recommande ce film à Alice.

```python
def recommander(
    notes: dict[str, dict[str, float]],
    utilisateur: str,
    n: int = 5,
) -> list[tuple[str, float]]:
    """
    Recommande n items à un utilisateur basé sur la similarité collaborative.

    Args:
        notes: {utilisateur: {item: note_sur_5}}
        utilisateur: nom de l'utilisateur cible
        n: nombre de recommandations

    Returns:
        Liste de (item, score_prédit) triée par score décroissant

    Algorithme suggéré :
    1. Calculer la similarité (cosinus) entre l'utilisateur cible et tous les autres
    2. Pour chaque item non noté par l'utilisateur cible :
       a. Calculer un score prédictif = moyenne pondérée des notes des utilisateurs similaires
       b. Le poids = similarité cosinus
    3. Retourner les n items avec les meilleurs scores prédits

    Structures de données à utiliser :
    - Dict pour les notes et les similarités
    - Heap pour le top-n

    Complexité attendue : O(U × I) où U = utilisateurs, I = items
    """
    # À compléter
    pass


# Dataset de test
notes_utilisateurs = {
    "Alice":   {"Matrix": 5, "Inception": 4, "Interstellar": 5, "Titanic": 2, "Avatar": 3},
    "Bob":     {"Matrix": 4, "Inception": 5, "Interstellar": 4, "Star Wars": 5, "Dune": 4},
    "Charlie": {"Titanic": 5, "Avatar": 4, "Matrix": 2, "Inception": 3, "Notebook": 5},
    "Diana":   {"Matrix": 3, "Star Wars": 4, "Dune": 5, "Interstellar": 4, "Inception": 4},
    "Eve":     {"Titanic": 4, "Notebook": 4, "Avatar": 5, "Inception": 2, "Matrix": 1},
}

print("Recommandations pour Alice :")
recommandations = recommander(notes_utilisateurs, "Alice", n=3)
for item, score in recommandations:
    print(f"  {item} — score prédit : {score:.2f}/5")
# Attendu : Star Wars et Dune devraient être bien classés (Alice aime la SF)
```

---

## 📋 Grille d'évaluation

| Exercice | Points | Critères |
|----------|--------|----------|
| 1.1 Complexité | /5 | Réponses correctes + justifications |
| 1.2 Pile RPN | /10 | Implémentation correcte + gestion d'erreurs |
| 1.3 File traitement | /10 | Logique de priorité + ordre correct |
| 1.4 Compteur mots | /10 | Complexité optimale + edge cases |
| 2.1 Tri critères | /10 | Multi-critères + asc/desc |
| 2.2 Recherche plage | /10 | Utilisation de bisect + complexité O(log n + k) |
| 2.3 Degrés séparation | /10 | BFS correct + edge cases |
| 3.1 Découpe optimale | /15 | PD correct + reconstruction solution |
| 3.2 Chemin critique | /15 | Tri topo + plus long chemin |
| 3.3 Analyse dépendances | /20 | Tous les critères d'analyse |
| Projet final | /25 | Algorithme complet + tests + complexité |
| **Total** | **/140** | |

---

[← Architecture et patterns](07-architecture-patterns.md) | [🏠 Accueil](../README.md)
