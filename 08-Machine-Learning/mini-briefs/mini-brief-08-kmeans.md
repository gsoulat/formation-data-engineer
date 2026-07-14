# Mini-brief ML #08 — K-Means : trouver des groupes sans étiquettes

> ⏱️ **~1 h 30** · Niveau intermédiaire · Prérequis : [01 — Qu'est-ce que le ML (supervisé vs non supervisé)](../cours/01-quest-ce-que-le-ml.md) · [06 — Comprendre les données](../cours/06-comprendre-donnees.md)
> 🎯 Un modèle, une séance : ici on apprend à **utiliser** K-Means, pas à le découvrir.

## Objectif

À la fin, tu sais **quand** utiliser un clustering, **normaliser** correctement, **choisir le bon nombre de clusters** (méthode du coude + silhouette), lancer K-Means, puis **interpréter et nommer** les groupes obtenus. Le clustering ne donne pas la réponse : c'est toi qui donnes du sens aux clusters.

## Contexte éclair

Le service marketing d'un centre commercial a une base clients (revenu, score de dépense) mais **aucune segmentation**. Il veut cibler ses campagnes. Personne n'a étiqueté les clients : c'est un problème **non supervisé**. K-Means va proposer des segments — à toi de vérifier qu'ils tiennent debout et de les nommer.

## Données

**Mall Customers** — 200 clients, variables `Annual Income (k$)` et `Spending Score (1-100)` (jeu Kaggle public). Si le téléchargement échoue, replie-toi sur `load_iris` **sans les labels**.

```python
import pandas as pd
url = "https://raw.githubusercontent.com/SteffiPeTaffy/machineLearningAZ/master/Machine%20Learning%20A-Z%20Template%20Folder/Part%204%20-%20Clustering/Section%2024%20-%20K-Means%20Clustering/Mall_Customers.csv"
df = pd.read_csv(url)
X = df[["Annual Income (k$)", "Spending Score (1-100)"]]

# Repli hors ligne :
# from sklearn.datasets import load_iris
# X = load_iris(as_frame=True).data   # on ignore volontairement y
```

## Étapes

1. **Explorer.** Un `scatter` revenu × score de dépense. Devines-tu des groupes à l'œil ? Note ton hypothèse sur le nombre de clusters — tu la confronteras à la méthode plus loin.
2. **Normaliser.** K-Means utilise la **distance euclidienne** → il est sensible à l'échelle. Applique un `StandardScaler` sur `X` **avant** de clusteriser. Sans ça, la variable à la plus grande amplitude écrase les autres.
3. **Méthode du coude.** Fais varier `n_clusters` de 2 à 10, récupère `kmeans.inertia_` à chaque fois, trace la courbe. Le « coude » (là où la baisse ralentit franchement) suggère un `k` raisonnable.
4. **Confirmer avec la silhouette.** Pour les mêmes `k`, calcule `silhouette_score(X_scaled, labels)`. Le meilleur `k` maximise le score (proche de 1 = clusters nets, proche de 0 = clusters qui se chevauchent). Coude et silhouette sont-ils d'accord ?
5. **Régler les hyperparamètres clés.** Entraîne le K-Means final avec le `k` retenu. Vérifie l'effet de `init="k-means++"` (par défaut, malin) vs `init="random"`, et de `n_init` (nombre de démarrages, garde le meilleur) sur la stabilité. Relance 2-3 fois : les clusters bougent-ils ?
6. **Interpréter et nommer.** Récupère `kmeans.cluster_centers_` (dé-normalise-les pour les lire), colore le scatter par cluster, et **donne un nom métier à chaque groupe** (ex. « revenu élevé / dépense faible = clients prudents à réactiver »). C'est LE geste spécifique du clustering.

```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

X_scaled = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=..., init="k-means++", n_init=10, random_state=42)
labels = km.fit_predict(X_scaled)
```

## Critères de réussite (OUI / NON)

- [ ] Données **normalisées avant** le clustering : OUI / NON
- [ ] Courbe du coude (inertie vs k) tracée et un coude identifié : OUI / NON
- [ ] `silhouette_score` calculé pour plusieurs `k` et le `k` final justifié par les **deux** indicateurs : OUI / NON
- [ ] Effet de `n_init` / `init` sur la stabilité observé et commenté : OUI / NON
- [ ] Chaque cluster est **décrit et nommé** en langage métier (pas juste « cluster 0, 1, 2 ») : OUI / NON

## Pièges à éviter

- **Oublier de normaliser** → la variable de plus grande amplitude domine la distance, les clusters n'ont plus de sens.
- Prendre `k` **au hasard** : coude et silhouette sont là pour ça, ne devine pas.
- Croire que les **numéros de cluster** ont un ordre ou un sens : 0/1/2 sont des étiquettes arbitraires, elles changent d'une exécution à l'autre.
- Laisser `n_init=1` : K-Means peut tomber dans un mauvais optimum local. Augmente `n_init` pour fiabiliser.
- Appliquer K-Means à des formes **non sphériques** ou de densités très différentes : ce n'est pas fait pour ça (voir DBSCAN).

## Pour aller plus loin

- Compare avec **DBSCAN** : pas besoin de fixer `k`, et il détecte le bruit.
- Réduis à 2 dimensions avec **PCA** avant de clusteriser un jeu à nombreuses variables (ex. `load_iris` complet), puis visualise.
- Ajoute la variable `Age` et re-segmente : le nombre de clusters optimal change-t-il ?

---
> 💡 Un corrigé commenté (notebook) est disponible côté formateur dans le dépôt privé `formation-corrections`.
