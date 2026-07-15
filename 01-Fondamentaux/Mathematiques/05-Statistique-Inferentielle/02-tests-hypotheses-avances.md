# Tests d'hypothèses avancés — t de Student & χ²

> 🎯 **Ça te servira pour…** répondre à des questions métier tranchées : « le magasin A vend-il
> vraiment **plus** que le B, ou est-ce le hasard ? », « le **canal d'achat dépend-il de la ville** ? ».
> Ce sont les tests que les recruteurs attendent d'un Data Analyst.

Au chapitre précédent, tu as vu la logique du test d'hypothèse (H₀, p-value, seuil à 5 %) sur une
**proportion**. On l'étend ici à deux situations très fréquentes : **comparer deux moyennes**
(test t) et **relier deux variables qualitatives** (test du χ²).

> **Rappel du raisonnement** — On suppose que « rien ne se passe » (H₀). On calcule la probabilité
> d'observer nos données **si H₀ était vraie** (la p-value). Si cette probabilité est **très faible**
> (< 5 %), on rejette H₀ : l'effet est **statistiquement significatif**.

---

## 1. Le test t de Student — comparer deux moyennes

**Question type** : *« Le panier moyen est-il plus élevé à Lille (78 €) qu'à Roubaix (71 €), ou ces
7 € d'écart sont-ils du bruit ? »*

- **H₀** : les deux moyennes sont égales (l'écart observé = hasard d'échantillonnage).
- **H₁** : les moyennes diffèrent.

> **Analogie** — Deux classes ont 12,5 et 12,0 de moyenne. Est-ce une vraie différence de niveau, ou
> juste que ce jour-là une classe avait un élève grippé ? Le test t regarde **l'écart des moyennes
> rapporté à la dispersion et à la taille des groupes** : un petit écart entre deux gros groupes très
> réguliers peut être significatif ; un gros écart entre deux minuscules groupes très dispersés ne
> l'est pas.

```python
from scipy import stats

lille   = [82, 75, 90, 68, 79, 88, 72, 95, 70, 81]   # paniers (€)
roubaix = [70, 65, 74, 60, 72, 68, 66, 71, 63, 69]

t, p = stats.ttest_ind(lille, roubaix, equal_var=False)   # Welch (n'exige pas des variances égales)
print(f"t = {t:.2f} | p-value = {p:.4f}")
# p < 0.05 → différence significative ; p ≥ 0.05 → on ne peut pas conclure à une différence
```

> 🛑 **Erreur courante** — conclure « les magasins sont **identiques** » quand `p ≥ 0,05`. Non : on
> dit seulement qu'on **n'a pas assez de preuves** pour affirmer une différence. Absence de preuve ≠
> preuve d'absence.

### L'intervalle de confiance sur une moyenne (loi de Student)

Le même contexte permet d'encadrer la vraie moyenne. Avec un petit échantillon, on utilise la **loi
de Student** (plus prudente que la loi normale) :

```python
import numpy as np
from scipy import stats

x = np.array(lille)
moy, n = x.mean(), len(x)
err = stats.sem(x)                                   # erreur-type de la moyenne
ic = stats.t.interval(0.95, df=n-1, loc=moy, scale=err)
print(f"Panier moyen Lille : {moy:.1f} € — IC 95 % = [{ic[0]:.1f} ; {ic[1]:.1f}]")
```

> **Analogie** (rappel) — L'IC, c'est le **filet du pêcheur** : sur 100 échantillons, environ 95 IC
> attrapent la vraie moyenne.

---

## 2. Le test du χ² — deux variables qualitatives sont-elles liées ?

**Question type** : *« Le **canal d'achat** (magasin / web) dépend-il de la **ville** ? »* ou *« la
**catégorie** achetée dépend-elle du fait que ce soit un **week-end** ? »*. Ici, pas de moyenne : on
compare des **effectifs** dans un **tableau de contingence**.

|  | Magasin | Web | Total |
|---|---:|---:|---:|
| **Lille** | 120 | 80 | 200 |
| **Roubaix** | 150 | 50 | 200 |
| **Total** | 270 | 130 | 400 |

- **H₀** : les deux variables sont **indépendantes** (le canal ne dépend pas de la ville).
- **H₁** : elles sont **liées**.

Le test compare les effectifs **observés** aux effectifs **attendus si H₀ était vraie** (répartition
au prorata des totaux). Plus l'écart est grand, plus le χ² est élevé, plus la p-value est faible.

> **Analogie** — Si le canal ne dépendait pas de la ville, chaque ville devrait avoir **la même
> proportion** de web (ici 130/400 = 32,5 %). Le χ² mesure **à quel point la réalité s'écarte de ce
> monde « sans lien »**. Grand écart → il y a un lien.

```python
import numpy as np
from scipy import stats

contingence = np.array([[120, 80],
                        [150, 50]])
chi2, p, ddl, attendus = stats.chi2_contingency(contingence)
print(f"χ² = {chi2:.2f} | p-value = {p:.4f} | ddl = {ddl}")
print("Effectifs attendus si indépendance :\n", attendus.round(1))
# p < 0.05 → le canal DÉPEND de la ville
```

Pour construire le tableau à partir de données brutes (pandas) :

```python
import pandas as pd
contingence = pd.crosstab(df["ville"], df["canal"])   # tableau de contingence en une ligne
```

> 🛑 **Erreur courante** — appliquer le χ² quand des cases attendues sont **< 5**. Le test devient peu
> fiable ; regroupe des catégories ou utilise un test exact (Fisher).

---

## 3. Quel test choisir ? (mémo)

| Ta question | Variables | Test |
|---|---|---|
| Une proportion diffère-t-elle d'une référence ? | 1 qualitative | test **z** sur proportion (chap. 01) |
| Deux **moyennes** diffèrent-elles ? | 1 quantitative + 1 qualitative (2 groupes) | test **t** de Student |
| Deux **variables qualitatives** sont-elles liées ? | 2 qualitatives | test du **χ²** d'indépendance |
| Deux variables **quantitatives** varient-elles ensemble ? | 2 quantitatives | **corrélation** / régression (chap. 03) |

> 🎲 **Devine avant de calculer** — « Le segment client (Particulier / Pro) est-il lié à la ville ? »
> Quel test ? *(Deux variables qualitatives → **χ²**.)*

---

## 🧪 Exercice

Une responsable veut savoir si le **taux de remise** moyen diffère entre deux enseignes, et si le
**type de produit** (Sport / Bricolage) est lié à la **saison** (été / hiver).

1. Quel test pour la première question ? Pour la seconde ?
2. Pour la première, `scipy` renvoie `p = 0.21`. Conclusion ?

<details>
<summary>💡 Corrigé</summary>

1. Comparaison de deux **moyennes** de remise → **test t** (`ttest_ind`). Lien entre deux variables
   **qualitatives** (type × saison) → **χ²** (`chi2_contingency` sur un `crosstab`).
2. `p = 0,21 ≥ 0,05` → on **ne peut pas conclure** à une différence de remise. Ce n'est **pas** une
   preuve qu'elles sont égales : peut-être l'échantillon est-il trop petit (manque de puissance).
</details>

---

## 🎥 Vidéos pour approfondir

| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Test t expliqué](https://www.youtube.com/results?search_query=statquest+t+test) | StatQuest | EN | Comparer deux moyennes |
| [Le test du khi-deux](https://www.youtube.com/results?search_query=test+khi+deux+ind%C3%A9pendance+fran%C3%A7ais) | Machine Learnia / M. Monka | FR | Tableau de contingence & indépendance |
| [p-value, ce que ça veut dire](https://www.youtube.com/results?search_query=statquest+p+value+clearly+explained) | StatQuest | EN | Éviter les contresens classiques |

---

## À retenir

- **Test t de Student** : deux **moyennes** diffèrent-elles ? `scipy.stats.ttest_ind` (Welch si les
  variances diffèrent).
- **IC sur une moyenne** : loi de **Student** (`stats.t.interval`) pour les petits échantillons.
- **Test du χ²** : deux variables **qualitatives** sont-elles liées ? `chi2_contingency` sur un
  tableau de contingence (`pd.crosstab`).
- Une **p-value ≥ 0,05** ne prouve **pas** l'égalité : c'est une absence de preuve, pas une preuve
  d'absence.
- Le bon test dépend de la **nature des variables** — garde le mémo sous les yeux.
