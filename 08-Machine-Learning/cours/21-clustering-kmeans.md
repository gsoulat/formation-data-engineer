# Chapitre 21 : Clustering non supervisé — K-Means

## 🎯 Objectifs

- Comprendre la différence fondamentale entre apprentissage supervisé et non supervisé
- Saisir intuitivement ce que résout le clustering (avant de voir l'algorithme)
- Dérouler l'algorithme de Lloyd (K-Means) pas à pas, à la main
- Savoir choisir le nombre de clusters `k` (méthode du coude + score de silhouette)
- Comprendre pourquoi la normalisation est indispensable pour K-Means
- Connaître les limites (formes non sphériques, `k` imposé, sensibilité aux échelles)
- Appliquer K-Means à un cas réel de segmentation client

**Phase 4 — Semaine 21**

---

## 1. 🧭 Le problème : je n'ai pas d'étiquettes

### 1.1 L'intuition métier

Jusqu'ici, tous nos modèles étaient **supervisés** : on avait une colonne "réponse" (le prix d'une maison, le fait qu'un client churne, l'espèce d'une fleur). On apprenait à **prédire cette réponse**.

Mais imaginez la situation suivante, très fréquente en entreprise :

> Le directeur marketing arrive avec un fichier de **200 000 clients** (âge, revenu, fréquence d'achat, panier moyen…) et vous dit :
> *"Je suis sûr qu'il y a plusieurs types de clients là-dedans. Trouve-les moi, je veux adapter mes campagnes."*

Le problème : **personne n'a jamais étiqueté** ces clients. Il n'y a pas de colonne "type_de_client". On ne cherche pas à prédire quelque chose de connu — on cherche à **découvrir une structure cachée** dans les données.

C'est exactement ce que fait le **clustering** : regrouper des observations qui se ressemblent, **sans qu'on lui dise à l'avance** à quoi ressemble chaque groupe.

### 1.2 Supervisé vs non supervisé

```
APPRENTISSAGE SUPERVISÉ                 APPRENTISSAGE NON SUPERVISÉ
─────────────────────────               ───────────────────────────

Données AVEC étiquettes                 Données SANS étiquettes
X ──► y (on connaît la réponse)         X ──► ???  (on cherche la structure)

Exemple :                               Exemple :
  âge, revenu ──► churn (oui/non)         âge, revenu ──► quels groupes ?

Question :                              Question :
  "Ce client va-t-il partir ?"            "Combien de types de clients ?
                                           Lesquels se ressemblent ?"

On peut MESURER l'erreur                 Pas de "bonne réponse" de référence
(comparer prédiction vs vérité)          → l'évaluation est plus subtile
```

| | Supervisé | Non supervisé |
|---|-----------|---------------|
| **Étiquettes `y`** | Oui | Non |
| **But** | Prédire une valeur connue | Découvrir une structure |
| **Exemples de tâches** | Classification, régression | Clustering, réduction de dimension, détection d'anomalies |
| **Évaluation** | Accuracy, RMSE… (vs vérité) | Silhouette, inertie, jugement métier |
| **Algorithmes** | KNN, arbres, régression… | K-Means, DBSCAN, hiérarchique… |

> 💡 **Conseil** : "En non supervisé, il n'y a pas de 'score de test' évident car il n'y a pas de vérité terrain. Le juge final est souvent **métier** : est-ce que les groupes trouvés ont du sens et sont actionnables ?"

---

## 2. 🎨 L'intuition du clustering : rapprocher ce qui se ressemble

### 2.1 Le nuage de points

Imaginez que chaque client soit un point sur un graphique. En abscisse son revenu, en ordonnée sa dépense annuelle. Naturellement, votre œil regroupe les points :

```
  dépense
   annuelle
      │              🔵🔵🔵
      │             🔵🔵🔵🔵      ← groupe A : gros revenus,
      │              🔵🔵🔵          grosses dépenses
      │
      │   🟢🟢
      │  🟢🟢🟢          🟠🟠🟠🟠
      │   🟢🟢          🟠🟠🟠🟠   ← groupe C : gros revenus,
      │  (petits revenus,   🟠🟠🟠     petites dépenses (prudents)
      │   petites dépenses)
      └──────────────────────────────► revenu
         groupe B
```

Votre cerveau vient de faire du clustering : il a repéré **3 groupes** en se basant sur une idée simple : *"les points proches se ressemblent"*.

K-Means formalise exactement cette intuition avec une notion mathématique de **distance** (la distance euclidienne, vue au chapitre 3 avec KNN).

### 2.2 Un cluster = un point autour d'un centre

L'idée centrale de K-Means (le nom vient de là) : chaque groupe est résumé par son **centre**, appelé **centroïde** (la moyenne des points du groupe).

```
Un cluster = un nuage de points + son centre (le ✚)

        🔵   🔵
      🔵   ✚   🔵      ← le ✚ est la MOYENNE des positions des 🔵
        🔵   🔵           C'est le "client type" de ce groupe

Un point appartient au cluster dont le centre est le PLUS PROCHE.
```

Le "client type" d'un groupe (le centroïde) est directement interprétable pour le métier : *"Le groupe A, c'est un client à 75 000 € de revenu qui dépense 4 200 € par an."*

---

## 3. ⚙️ L'algorithme de Lloyd, pas à pas

K-Means repose sur l'**algorithme de Lloyd**. Il est étonnamment simple : deux étapes répétées en boucle.

### 3.1 Les deux étapes en boucle

```
ÉTAPE 0 — Initialisation
  Choisir k (ex : k=3) et placer k centres au hasard.

┌─► ÉTAPE 1 — ASSIGNATION (affecter)
│     Chaque point rejoint le centre le plus proche.
│     → on obtient k groupes provisoires
│
│   ÉTAPE 2 — MISE À JOUR (recentrer)
│     Chaque centre se déplace à la MOYENNE de son groupe.
│     → les centres bougent
│
└─── Les centres ont-ils bougé ?
        OUI → recommencer étape 1
        NON → STOP, c'est terminé (convergence)
```

C'est tout. On alterne "j'affecte les points au centre le plus proche" puis "je recalcule les centres", jusqu'à ce que plus rien ne bouge.

### 3.2 Déroulé visuel

```
ITÉRATION 1                        ITÉRATION 2                    CONVERGENCE
───────────                        ───────────                    ───────────

Centres placés au hasard :         Centres recalculés :           Plus de mouvement :

  ●  ●    ○                          ●   ●    ○                     ●●●   ○○○
 ● ✚●   ○ ○                         ●● ✚    ○✚○                    ●●✚●  ○✚○○
  ●  ●  ○  ○                         ●  ●   ○  ○                    ●●●   ○○○
      ✚                                 ✚                             ✚
   △ △ △                              △△△                           △△△
  △ △ △                             △ ✚ △                          △✚△△
   △ △                               △△△                            △△△

Chaque point rejoint         Chaque ✚ se déplace vers        Assignations stables :
le ✚ le plus proche.         la moyenne de son groupe.       les ✚ ne bougent plus.
(assignations approximatives) (les groupes se précisent)      → l'algo s'arrête.
```

### 3.3 Calcul à la main (mini-exemple 1D)

Prenons 6 points sur une seule dimension pour bien voir les nombres, et `k=2`.

```
Points : 1, 2, 3, 10, 11, 12
Objectif : trouver 2 clusters (k=2)

── Init : centres au hasard → c1 = 2, c2 = 11 ──────────────────

Itération 1 — ASSIGNATION (distance à chaque centre)
  point 1  : |1-2|=1  vs |1-11|=10  → cluster 1
  point 2  : |2-2|=0  vs |2-11|=9   → cluster 1
  point 3  : |3-2|=1  vs |3-11|=8   → cluster 1
  point 10 : |10-2|=8 vs |10-11|=1  → cluster 2
  point 11 : |11-2|=9 vs |11-11|=0  → cluster 2
  point 12 : |12-2|=10 vs |12-11|=1 → cluster 2

  Cluster 1 = {1, 2, 3}      Cluster 2 = {10, 11, 12}

Itération 1 — MISE À JOUR (moyenne de chaque groupe)
  c1 = (1+2+3)/3   = 2.0
  c2 = (10+11+12)/3 = 11.0

── Les centres n'ont pas bougé (2.0 et 11.0) → CONVERGENCE ✅
```

Deux clusters nets : les "petits" et les "grands". L'algorithme a convergé en une itération car l'initialisation était déjà bonne. Avec une mauvaise init, il aurait fallu quelques tours de plus.

### 3.4 Ce que K-Means minimise réellement (l'inertie)

Formellement, K-Means cherche à minimiser l'**inertie** (aussi appelée WCSS, *Within-Cluster Sum of Squares*) : la somme des distances au carré entre chaque point et le centre de son cluster.

**Formule** :

```
Inertie = Σ    Σ      ‖ x − centre(c) ‖²
         clusters points x
           c    du cluster c
```

En clair : *"À quel point mes groupes sont-ils compacts ?"* Plus l'inertie est basse, plus les points sont serrés autour de leur centre.

```
Inertie ÉLEVÉE (mauvais)          Inertie BASSE (bon)
─────────────────────            ──────────────────

   ●        ●                        ●●●
      ✚                              ●✚●        Les points sont
   ●     ●                           ●●●        serrés autour du ✚
        ●
(points dispersés)               (points compacts)
```

> ⚠️ **Attention** : "L'algorithme de Lloyd ne garantit **pas** l'optimum global — il peut se coincer dans un minimum local selon l'initialisation. C'est pourquoi sklearn relance l'algo plusieurs fois (`n_init`) avec des inits différentes et garde la meilleure. L'initialisation intelligente `k-means++` (le défaut) réduit fortement ce risque."

---

## 4. 🐍 K-Means avec scikit-learn

### 4.1 Premier exemple sur un dataset réel

Utilisons le dataset **Iris** (fourni par sklearn) : 150 fleurs décrites par 4 mesures. On va faire semblant de **ne pas connaître** les espèces (clustering = non supervisé) et laisser K-Means retrouver la structure.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# 1. Charger les données (on IGNORE volontairement y : c'est du non supervisé)
iris = load_iris()
X = iris.data                     # 150 fleurs × 4 features
feature_names = iris.feature_names

# 2. Normaliser (INDISPENSABLE, voir section 6)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 3. Appliquer K-Means avec k=3
kmeans = KMeans(
    n_clusters=3,        # on demande 3 groupes
    init='k-means++',    # initialisation intelligente (défaut)
    n_init=10,           # 10 relances, on garde la meilleure
    max_iter=300,        # nb max d'itérations de Lloyd
    random_state=42
)
labels = kmeans.fit_predict(X_scaled)   # étiquette de cluster pour chaque fleur

print("Répartition des clusters :", np.bincount(labels))
print("Inertie finale :", round(kmeans.inertia_, 2))
print("Nombre d'itérations jusqu'à convergence :", kmeans.n_iter_)
```

```
Sortie typique :
  Répartition des clusters : [53 50 47]
  Inertie finale : 139.82
  Nombre d'itérations jusqu'à convergence : 6
```

Les trois groupes sont presque équilibrés (~50 chacun), ce qui colle avec les 3 espèces réelles d'Iris. K-Means a retrouvé la structure **sans jamais voir les étiquettes**.

### 4.2 Visualiser les clusters et les centroïdes

Iris a 4 dimensions ; on projette sur 2 pour visualiser.

```python
# On visualise sur 2 des 4 features (longueur/largeur des pétales)
f1, f2 = 2, 3   # indices "petal length" et "petal width"

plt.figure(figsize=(9, 6))
scatter = plt.scatter(X_scaled[:, f1], X_scaled[:, f2],
                      c=labels, cmap='viridis', s=40, alpha=0.7)

# Les centroïdes (centres de chaque cluster)
centres = kmeans.cluster_centers_
plt.scatter(centres[:, f1], centres[:, f2],
            c='red', marker='X', s=250, edgecolors='black',
            linewidths=1.5, label='Centroïdes')

plt.xlabel(feature_names[f1] + " (normalisé)")
plt.ylabel(feature_names[f2] + " (normalisé)")
plt.title("K-Means sur Iris (k=3) — clusters et centroïdes")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

Vous verrez trois nuages nets, chacun marqué de son ✚ rouge : le "client type" (ici, la "fleur type") de chaque groupe.

### 4.3 Attributs utiles de l'objet `KMeans`

| Attribut / méthode | Rôle |
|--------------------|------|
| `.labels_` | Cluster attribué à chaque point d'entraînement |
| `.cluster_centers_` | Coordonnées des `k` centroïdes |
| `.inertia_` | Inertie finale (WCSS) — plus bas = clusters plus compacts |
| `.n_iter_` | Nombre d'itérations avant convergence |
| `.fit_predict(X)` | Entraîne **et** renvoie les labels en une fois |
| `.predict(X_new)` | Affecte de **nouveaux** points au centre le plus proche |

> 💡 **Conseil** : "`predict()` est puissant : une fois les centroïdes appris, un nouveau client entrant est classé instantanément dans le groupe dont le centre est le plus proche. C'est ce qui rend K-Means déployable en production."

---

## 5. 🔢 Choisir le bon `k`

C'est **le** problème pratique de K-Means : il faut donner `k` à l'avance, alors qu'on ne le connaît pas. Deux outils complémentaires aident à le choisir.

### 5.1 La méthode du coude (elbow)

**Idée** : tracer l'inertie en fonction de `k`. Plus `k` augmente, plus l'inertie baisse (avec `k = nombre de points`, l'inertie tomberait à 0 — un point par cluster !). On cherche le **coude** : le point où ajouter un cluster de plus n'apporte plus grand-chose.

```
Inertie
   │●
   │  ●
   │    ●
   │     ●  ← LE COUDE (ici k=3)
   │       ●___
   │          ●___●___●___●
   │
   └──────────────────────────► k
     1  2  3  4  5  6  7  8

Avant le coude : chaque cluster ajouté fait beaucoup baisser l'inertie.
Après le coude : gain marginal → clusters "artificiels".
```

```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

inerties = []
ks = range(1, 11)

for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X_scaled)
    inerties.append(km.inertia_)

plt.figure(figsize=(9, 5))
plt.plot(ks, inerties, 'o-', linewidth=2)
plt.axvline(x=3, color='red', linestyle='--', label='Coude (k=3)')
plt.xlabel("Nombre de clusters k")
plt.ylabel("Inertie (WCSS)")
plt.title("Méthode du coude sur Iris")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

> ⚠️ **Attention** : "Le coude est parfois **flou** : la courbe descend en douceur sans angle net. Ne vous reposez jamais dessus seul — croisez-le toujours avec la silhouette et le bon sens métier."

### 5.2 Le score de silhouette

Le score de silhouette est plus rigoureux. Pour chaque point, il compare :

- **a** = distance moyenne aux points de **son propre** cluster (cohésion — on veut petit)
- **b** = distance moyenne aux points du cluster voisin le **plus proche** (séparation — on veut grand)

**Formule** (pour un point) :

```
silhouette = (b − a) / max(a, b)
```

```
Interprétation du score (moyenne sur tous les points) :

  proche de +1  ✅  point bien dans son cluster, loin des autres
  proche de  0  😐  point à la frontière entre deux clusters
  négatif      ❌  point probablement mal classé (plus proche d'un autre cluster)
```

```python
from sklearn.metrics import silhouette_score

print("Silhouette pour différents k :")
for k in range(2, 8):          # silhouette impossible pour k=1
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels_k = km.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels_k)
    print(f"  k={k} : silhouette = {score:.3f}")
```

```
Sortie typique (Iris) :
  k=2 : silhouette = 0.582   ← le plus haut, mais fusionne 2 espèces proches
  k=3 : silhouette = 0.459   ← correspond aux 3 vraies espèces
  k=4 : silhouette = 0.386
  k=5 : silhouette = 0.345
  ...
```

> 💡 **Conseil** : "Sur Iris, la silhouette préfère `k=2` (deux des trois espèces sont très proches et se fondent). Le coude et la connaissance métier (3 espèces) pointent vers `k=3`. C'est un cas d'école : **les outils ne sont pas toujours d'accord** — le clustering reste un dialogue entre statistiques et sens métier."

### 5.3 Combiner les deux

```
DÉMARCHE RECOMMANDÉE POUR CHOISIR k
────────────────────────────────────

1. Tracer la méthode du coude    → repère une zone plausible (ex : 3-4)
2. Calculer la silhouette         → départage dans cette zone
3. Regarder les clusters obtenus  → ont-ils un sens métier ? sont-ils actionnables ?
4. Trancher                       → le métier a le dernier mot
```

---

## 6. 📏 Pourquoi la normalisation est indispensable

C'est **l'erreur numéro 1** avec K-Means. Contrairement aux arbres (chapitre 10) qui se moquent de l'échelle, K-Means repose entièrement sur des **distances** — donc sur les échelles.

### 6.1 Le problème des échelles

```
Deux features aux échelles très différentes :

  âge       : de 18 à 70      (amplitude ≈ 52)
  revenu    : de 15000 à 90000 (amplitude ≈ 75000)

Distance entre deux clients A(25 ans, 30000€) et B(60 ans, 32000€) :

  Δâge    = 60 − 25   =    35
  Δrevenu = 32000 − 30000 = 2000

  distance² = 35² + 2000² = 1225 + 4 000 000

           └─┬─┘   └───┬────┘
          négligeable  ÉCRASE tout

→ Le revenu domine complètement. L'âge n'a AUCUN poids.
→ K-Means clusterise en réalité SUR LE REVENU SEUL.
```

La feature avec la plus grande amplitude **dicte** les distances, donc les clusters. Ce n'est presque jamais ce qu'on veut.

### 6.2 La solution : StandardScaler

On ramène chaque feature à moyenne 0 et écart-type 1, pour qu'elles pèsent **à égalité**.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

# Données jouet avec échelles très différentes
rng = np.random.RandomState(42)
age = rng.randint(18, 70, size=300)
revenu = rng.randint(15000, 90000, size=300)
X_brut = np.column_stack([age, revenu])

# --- SANS normalisation ---
km_sans = KMeans(n_clusters=3, n_init=10, random_state=42)
labels_sans = km_sans.fit_predict(X_brut)

# --- AVEC normalisation ---
X_scaled = StandardScaler().fit_transform(X_brut)
km_avec = KMeans(n_clusters=3, n_init=10, random_state=42)
labels_avec = km_avec.fit_predict(X_scaled)

print("Silhouette SANS scaling :", round(silhouette_score(X_brut, labels_sans), 3))
print("Silhouette AVEC scaling :", round(silhouette_score(X_scaled, labels_avec), 3))
# Sans scaling, les clusters se découpent quasi uniquement selon le revenu.
```

> 💡 **Conseil** : "Règle d'or : **toujours** `StandardScaler` (ou `MinMaxScaler`) avant K-Means, sauf si vos features sont déjà dans la même unité et la même plage. Encapsulez le tout dans un `Pipeline` pour ne jamais l'oublier."

```python
from sklearn.pipeline import make_pipeline

# Pipeline propre : scaler + kmeans enchaînés
pipe = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=3, n_init=10, random_state=42)
)
labels = pipe.fit_predict(X_brut)   # scaling appliqué automatiquement
```

---

## 7. 🚧 Limites de K-Means (et quand ne pas l'utiliser)

K-Means est simple, rapide et scalable, mais il fait des **hypothèses fortes**. Les connaître évite de gros contre-sens.

### 7.1 Il suppose des clusters sphériques et de taille comparable

K-Means affecte chaque point au centre le plus proche → les frontières entre clusters sont **rectilignes** (droites). Résultat : il ne sait modéliser que des groupes **grosso modo ronds** et de tailles similaires.

```
✅ K-Means marche bien              ❌ K-Means échoue
   (clusters ronds, séparés)          (formes allongées / imbriquées)

   ●●●        ○○○                      ●●●●●●●●●●●●●
  ●●✚●●      ○✚○○                     ●             ○○○○
   ●●●        ○○○                      ●●●●●●●     ○✚○○○
                                             ●●●●●● ○○○○
   △△△                                 (deux "lunes" imbriquées :
  △✚△△                                  K-Means les coupe DROIT au milieu,
   △△△                                  au lieu de suivre leur forme)
```

Sur des données en "lunes" ou en cercles concentriques, K-Means découpe le plan en parts droites et se trompe. Là, un algorithme **basé densité** comme **DBSCAN** est bien plus adapté.

```python
# Démonstration classique : K-Means vs formes non convexes
from sklearn.datasets import make_moons
from sklearn.cluster import KMeans, DBSCAN

X_moons, _ = make_moons(n_samples=300, noise=0.06, random_state=42)

labels_km = KMeans(n_clusters=2, n_init=10, random_state=42).fit_predict(X_moons)
labels_db = DBSCAN(eps=0.25, min_samples=5).fit_predict(X_moons)
# En affichant les deux : K-Means coupe les lunes en travers,
# DBSCAN suit correctement la forme de chaque croissant.
```

### 7.2 Le nombre `k` doit être fixé à l'avance

K-Means **ne peut pas** décider tout seul du nombre de groupes. Si vous demandez `k=4` sur des données qui en contiennent naturellement 3, il découpera artificiellement un vrai groupe en deux. D'où l'importance de la section 5 (coude + silhouette).

### 7.3 Sensible à l'initialisation et aux outliers

- **Initialisation** : de mauvais centres de départ mènent à un minimum local médiocre. Mitigé par `k-means++` et `n_init`.
- **Outliers** : comme les centroïdes sont des **moyennes**, un point aberrant tire le centre vers lui et déforme le cluster. Nettoyez les outliers en amont, ou envisagez K-Medoids (centres = vrais points, plus robustes).

### 7.4 Tableau récapitulatif : quand utiliser quoi

| Situation | Algorithme conseillé |
|-----------|----------------------|
| Groupes ronds, séparés, `k` estimable | **K-Means** ✅ |
| Formes allongées, imbriquées, clusters de densités variées | **DBSCAN** |
| On veut une **hiérarchie** de groupes (dendrogramme) | **Clustering hiérarchique** |
| Beaucoup d'outliers, besoin de robustesse | **K-Medoids** |
| Clusters qui se chevauchent, appartenance "floue" | **Gaussian Mixture (GMM)** |

> 💡 **Conseil** : "K-Means est le **premier réflexe** : rapide, scalable, interprétable. Si les résultats sont incohérents (clusters coupés bizarrement, un cluster géant qui avale tout), interrogez ses hypothèses avant de le blâmer — c'est souvent la forme des données ou l'oubli du scaling."

---

## 8. 🛍️ Cas d'usage complet : segmentation client

Mettons tout en pratique sur un cas métier réaliste : segmenter une base de clients pour cibler des campagnes marketing. On utilise un jeu de données de clients de vente en ligne récupérable via **OpenML** (`fetch_openml`), avec une génération de secours locale pour rester exécutable partout.

### 8.1 Le problème métier

> *"Nous avons les données d'achat de nos clients. Le marketing veut 3 à 5 segments distincts pour personnaliser les offres. À vous de les trouver et de les décrire."*

Pas d'étiquette, un objectif métier clair, un livrable actionnable : c'est le terrain de jeu idéal du clustering.

### 8.2 Pipeline complet

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# ── 1. Charger des données clients réalistes ──────────────────────
# On tente OpenML ; sinon on génère un jeu réaliste (reproductible).
try:
    from sklearn.datasets import fetch_openml
    data = fetch_openml("Wholesale-customers", version=1, as_frame=True)
    df = data.frame
    features = ["Fresh", "Milk", "Grocery", "Frozen",
                "Detergents_Paper", "Delicassen"]
    df = df[features].astype(float)
except Exception:
    rng = np.random.RandomState(42)
    n = 500
    df = pd.DataFrame({
        "recence_jours":  rng.randint(1, 365, n),      # jours depuis dernier achat
        "frequence":      rng.poisson(8, n) + 1,       # nb de commandes / an
        "montant_total":  rng.gamma(2.0, 400, n),      # dépense annuelle €
    })
    features = list(df.columns)

print("Aperçu des données :")
print(df.head())
print("\nStatistiques :")
print(df.describe().round(1))

# ── 2. Normaliser (indispensable : les features ont des échelles ≠) ─
X = df[features].values
X_scaled = StandardScaler().fit_transform(X)

# ── 3. Choisir k : coude + silhouette ─────────────────────────────
inerties, silhouettes, ks = [], [], range(2, 9)
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    lab = km.fit_predict(X_scaled)
    inerties.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, lab))

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
axes[0].plot(list(ks), inerties, 'o-')
axes[0].set(xlabel="k", ylabel="Inertie", title="Méthode du coude")
axes[0].grid(True, alpha=0.3)
axes[1].plot(list(ks), silhouettes, 's-', color='green')
axes[1].set(xlabel="k", ylabel="Silhouette", title="Score de silhouette")
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

best_k = list(ks)[int(np.argmax(silhouettes))]
print(f"\nk retenu (meilleure silhouette) : {best_k}")

# ── 4. Clustering final ───────────────────────────────────────────
kmeans = KMeans(n_clusters=best_k, n_init=10, random_state=42)
df["segment"] = kmeans.fit_predict(X_scaled)

# ── 5. Décrire les segments (le livrable pour le métier) ──────────
profils = df.groupby("segment")[features].mean().round(0)
profils["taille"] = df["segment"].value_counts().sort_index()
print("\n=== PROFIL DES SEGMENTS (moyennes par groupe) ===")
print(profils)
```

### 8.3 De centroïdes à personas

Le tableau `profils` est le cœur du livrable. On **traduit** chaque centroïde en un persona marketing parlant :

```
Exemple d'interprétation (jeu de secours recence/frequence/montant) :

  Segment 0 : récence FAIBLE, fréquence HAUTE, montant HAUT
    → "Clients VIP fidèles"  ► programme de fidélité premium

  Segment 1 : récence HAUTE, fréquence BASSE, montant BAS
    → "Clients endormis"     ► campagne de réactivation / promo de retour

  Segment 2 : récence MOYENNE, fréquence MOYENNE, montant MOYEN
    → "Clients réguliers"    ► montée en gamme (cross-sell)
```

> 💡 **Conseil** : "Un segment n'a de valeur que s'il est **actionnable**. Le livrable n'est pas la liste des labels, mais la **description des personas** (le tableau des centroïdes traduit en langage métier) et l'action associée à chacun. C'est cette table que le marketing utilise."

### 8.4 Affecter un nouveau client

En production, chaque nouveau client est classé instantanément :

```python
# Nouveau client : récence=15 j, fréquence=12 commandes, montant=2500 €
nouveau = np.array([[15, 12, 2500]])

# ⚠️ On applique le MÊME scaler que sur l'entraînement (à conserver !)
scaler = StandardScaler().fit(X)          # en vrai : réutiliser le scaler entraîné
nouveau_scaled = scaler.transform(nouveau)

segment = kmeans.predict(nouveau_scaled)
print(f"Ce client appartient au segment : {segment[0]}")
```

> ⚠️ **Attention** : "Le scaler ajusté sur les données d'entraînement **doit** être réutilisé tel quel sur les nouveaux points — jamais un `fit` recalculé sur un seul client. En pratique, on sérialise le `Pipeline` (scaler + kmeans) ensemble avec `joblib`."

---

## 🎯 Points clés à retenir

1. **Non supervisé = pas d'étiquettes** : on découvre une structure au lieu de prédire une valeur connue.
2. **Le clustering regroupe ce qui se ressemble**, en se basant sur une notion de distance.
3. **K-Means résume chaque groupe par son centroïde** (la moyenne du groupe) = le "client type", directement interprétable.
4. **L'algorithme de Lloyd** alterne deux étapes : *assigner* (chaque point au centre le plus proche) puis *recentrer* (chaque centre à la moyenne de son groupe), jusqu'à convergence.
5. **Il minimise l'inertie (WCSS)** : la compacité des clusters — sans garantie d'optimum global (d'où `n_init` + `k-means++`).
6. **Choisir `k`** se fait avec la méthode du **coude** (inertie vs k) ET le **score de silhouette**, arbitrés par le **sens métier**.
7. **Normaliser est indispensable** : sans scaling, la feature de plus grande amplitude écrase toutes les autres.
8. **Limites** : clusters supposés ronds et équilibrés, `k` imposé, sensibilité aux outliers et à l'init.
9. **Pour les formes non sphériques**, préférer **DBSCAN** ; pour une hiérarchie, le **clustering hiérarchique**.
10. **Le livrable de la segmentation** n'est pas les labels, mais les **personas actionnables** issus des centroïdes.

---

## 🧠 Mini-quiz

**1.** Quelle est la différence fondamentale entre apprentissage supervisé et non supervisé ?
<details><summary>Réponse</summary>
Le supervisé dispose d'étiquettes `y` (une réponse connue à prédire) et peut mesurer son erreur ; le non supervisé n'a **pas** d'étiquettes et cherche à découvrir une structure cachée (ici, des groupes). Il n'y a pas de "bonne réponse" de référence pour l'évaluer directement.
</details>

**2.** Décrivez les deux étapes répétées par l'algorithme de Lloyd.
<details><summary>Réponse</summary>
(1) **Assignation** : chaque point rejoint le centroïde le plus proche. (2) **Mise à jour** : chaque centroïde se déplace à la moyenne des points de son groupe. On répète jusqu'à ce que les centres ne bougent plus (convergence).
</details>

**3.** Que mesure l'inertie (WCSS), et la veut-on grande ou petite ?
<details><summary>Réponse</summary>
La somme des distances au carré entre chaque point et le centre de son cluster : c'est la **compacité** des clusters. On la veut **petite** (points serrés autour de leur centre). Mais attention : elle décroît toujours quand `k` augmente, d'où la méthode du coude.
</details>

**4.** La méthode du coude suggère `k=4`, la silhouette est maximale à `k=2`. Que faites-vous ?
<details><summary>Réponse</summary>
On ne tranche pas mécaniquement : on **regarde les clusters obtenus** pour chaque `k`, on vérifie lesquels ont un **sens métier** et sont actionnables, et le métier arbitre. Coude et silhouette sont des indices, pas une vérité absolue.
</details>

**5.** Pourquoi faut-il normaliser avant K-Means, alors que ce n'était pas nécessaire pour un arbre de décision ?
<details><summary>Réponse</summary>
K-Means repose sur des **distances** : une feature à grande amplitude (ex : revenu en €) écrase les autres et dicte seule les clusters. Un arbre ne compare que des seuils feature par feature ("x < seuil ?") : seul l'ordre compte, pas l'échelle, donc le scaling est inutile pour lui.
</details>

**6.** Sur des données en forme de deux "lunes" imbriquées, K-Means échoue. Pourquoi, et quel algorithme préférer ?
<details><summary>Réponse</summary>
K-Means affecte chaque point au centre le plus proche → frontières **droites** → il ne sait modéliser que des groupes ronds. Deux lunes imbriquées sont non convexes, il les coupe en travers. On préfère un algorithme basé **densité** comme **DBSCAN**, qui suit la forme des groupes.
</details>

**7.** Dans un projet de segmentation, quel est le vrai livrable ?
<details><summary>Réponse</summary>
Pas la simple liste des labels de cluster, mais la **description des personas** : le tableau des centroïdes traduit en langage métier (ex : "VIP fidèles", "clients endormis") avec, pour chacun, l'action marketing associée.
</details>

---

## 📚 Ressources

- **Documentation scikit-learn — Clustering** : https://scikit-learn.org/stable/modules/clustering.html
- **`KMeans` (API sklearn)** : https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- **Analyse de silhouette (exemple officiel sklearn)** : https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
- **Comparaison des algorithmes de clustering** : https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html
- **DBSCAN (pour aller plus loin sur les formes non sphériques)** : https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
- **Datasets OpenML** : https://www.openml.org/

---

## ✅ Checklist de validation

- [ ] Je sais distinguer apprentissage supervisé et non supervisé
- [ ] Je peux expliquer ce que résout le clustering avant même de citer un algorithme
- [ ] Je sais dérouler l'algorithme de Lloyd à la main sur un petit exemple
- [ ] Je comprends ce qu'est un centroïde et l'inertie (WCSS)
- [ ] Je sais tracer une courbe du coude et l'interpréter
- [ ] Je sais calculer et lire un score de silhouette
- [ ] Je sais pourquoi la normalisation est indispensable pour K-Means
- [ ] Je connais les limites de K-Means (formes, `k` imposé, outliers)
- [ ] Je sais quand préférer DBSCAN ou le clustering hiérarchique
- [ ] Je sais transformer des centroïdes en personas actionnables

---

**Précédent** : [Chapitre 18 : Data Drift](18-data-drift.md)

**Suivant** : *(à venir)*

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [K-Means clustering](https://www.youtube.com/results?search_query=statquest+k+means+clustering) | StatQuest | EN | Le fonctionnement pas à pas |
| [Clustering K-Means (FR)](https://www.youtube.com/results?search_query=machine+learnia+k+means+francais) | Machine Learnia | FR | Segmenter sans étiquettes |
| [Choisir le nombre de clusters](https://www.youtube.com/results?search_query=statquest+k+means+elbow+method) | StatQuest | EN | La méthode du coude |
