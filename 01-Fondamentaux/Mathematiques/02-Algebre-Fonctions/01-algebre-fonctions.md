# 02 — Algèbre & fonctions

> **Cours apprenant** — Formation Data Analyst (RNCP-38616, Simplon)

---

## 🎬 Accroche — Lundi matin à la Ch'ti Boutique

Il est 9 h. Tu arrives avec ton café, tu pousses la porte de la **Ch'ti Boutique** (prêt-à-porter à Lille, Roubaix et Dunkerque) et la patronne, Martine, te tend une feuille griffonnée :

> « Dis donc, toi qui es data analyst… Mon CA monte chaque mois, mais de **combien** au juste ? Et si ça continue, à quel mois je passe les **30 000 €** ? Et la boutique de Dunkerque, pourquoi elle me fait la tête ? »

Tu n'as pas encore ouvert un seul tableur, mais tu vas répondre à **toutes** ces questions… avec juste une droite et son équation : `y = ax + b`. C'est ça, l'algèbre des fonctions : transformer une intuition (« ça monte ») en **chiffre précis** (« +1 200 €/mois ») et en **prévision** (« 30 000 € au mois 10 »).

> 💡 **Rends-le tien.** Pas fan du prêt-à-porter ? Remplace mentalement « pulls » par tes abonnements Twitch, tes ventes de cookies, tes likes Insta… Les maths sont exactement les mêmes. Choisis le décor qui te parle, le fil rouge t'accompagne tout le chapitre.

---

## Présentation

| | |
|---|---|
| **Titre** | Algèbre & Fonctions : modéliser une tendance |
| **Durée estimée** | 4 h (2 h théorie + 2 h pratique Python) |
| **Compétence visée** | Socle mathématique + **C17** (lire et interpréter des graphiques) |
| **Pré-requis** | Chapitre 1 (arithmétique : pourcentages, proportions, opérations de base) |
| **Outils** | Python 3, `numpy`, `matplotlib`, papier + crayon |

---

## Objectifs pédagogiques

À la fin de ce chapitre, tu seras capable de :

1. **Manipuler des variables et des expressions** algébriques (remplacer, simplifier, évaluer).
2. **Résoudre une équation du 1er degré** (`ax + b = 0`) à la main et en Python.
3. **Comprendre la notion de fonction** : un mécanisme entrée → sortie.
4. **Reconnaître et tracer une fonction linéaire (`y = ax`) et affine (`y = ax + b`)**.
5. **Interpréter la pente `a` comme un taux de variation** (vitesse d'évolution).
6. **Interpréter l'ordonnée à l'origine `b`** comme une valeur de départ.
7. **Lire un repère cartésien et un graphique** : axes, points, droites, tendances.
8. **Décrire la croissance / décroissance** d'une courbe.

---

## Pourquoi c'est utile au Data Analyst ?

L'algèbre et les fonctions ne sont pas de la décoration : ce sont **les briques de base de l'analyse de données**.

- **La fonction affine = le premier modèle de tendance.** Quand tu dis « le chiffre d'affaires augmente régulièrement de 1 200 € par mois », tu décris une fonction affine. C'est exactement ce que fait une **régression linéaire** (que tu verras au chapitre 5).
- **La pente = la vitesse d'évolution.** Une pente de `+1200` veut dire « +1 200 € chaque mois ». Une pente négative veut dire que ça baisse. C'est l'indicateur le plus parlant pour un décideur.
- **Lire un graphe = la base de la dataviz.** Un dashboard Power BI, Tableau ou Looker Studio n'est qu'un empilement de graphiques. Si tu ne sais pas lire un repère, tu ne sais pas faire parler une donnée.
- **Les variables et équations** sont partout : calculer un seuil de rentabilité, trouver à quel mois on atteindra 100 000 € de CA, résoudre `prix × quantité = objectif`…

> 🧭 **Fil rouge du chapitre** : tu suis **« Ch'ti Boutique »**, une enseigne de prêt-à-porter implantée à Lille, Roubaix et Dunkerque. On modélise son chiffre d'affaires (CA), ses coûts et ses ventes.

> 🔗 **Lien aval important (à garder en tête).** La **pente `a`** (le taux de variation) que tu vas apprendre ici n'est pas un truc qui reste dans ce chapitre. C'est **exactement** l'outil que tu réutiliseras dans le **module 1.3 (Phase 1) pour analyser les TENDANCES** d'un vrai jeu de données : « le trafic du site augmente-t-il ? de combien par semaine ? la courbe s'essouffle-t-elle ? ». Bref : la pente d'aujourd'hui = ton détecteur de tendance de demain. Soigne cette notion, tu la croiseras partout.

---

## 🎲 Devine avant de calculer

Avant de sortir la moindre formule, **fais une prédiction à l'instinct**. Note ta réponse, puis vérifie en lisant le cours. Deviner d'abord fait *coller* la notion bien mieux qu'une démonstration passive.

1. **Le pari de la pente.** Le CA de Lille passe de **18 000 € au mois 0** à **24 000 € au mois 5**. À ton avis, de combien augmente-t-il **par mois** en moyenne ? (Indice : répartis l'augmentation totale sur le nombre de mois.) Garde ton chiffre… on le calcule en 4.5.
2. **Le pari du point mort.** Un pull est vendu **35 €**, et la boutique a **150 €** de frais fixes par jour. Combien de pulls faut-il vendre, à la louche, pour **ne pas perdre d'argent** ? 2 ? 5 ? 10 ? Note ton chiffre… réponse en 4.2.

> 🎁 Si tes deux prédictions tombent juste (ou pas loin), c'est que ton intuition est déjà bonne — le cours va juste te donner la **méthode exacte** pour le prouver à Martine.

---

## Notions

### Variables et expressions

#### Définition
Une **variable** est une lettre qui représente une valeur **qui peut changer** (souvent `x`). Une **expression** est une combinaison de nombres, de variables et d'opérations : `3x + 5`, `2(a − b)`, `prix × quantité`.

> En data, une variable algébrique `x` correspond à une **colonne** de ton jeu de données (ex : le mois, la quantité vendue).

> 🧠 **Analogie du quotidien.** Une variable, c'est une **case d'étiquette** sur un bocal : aujourd'hui le bocal contient 12 bonbons, demain 20. L'étiquette (`q`) ne change pas, le contenu si. Une expression (`35×q − 150`) c'est la **recette** qui dit quoi faire avec le contenu du bocal.

> 🎯 **Ça te servira pour…** créer des **colonnes calculées**. En vrai, écrire `CA = 35*quantite - 150` sur un DataFrame, c'est *littéralement* ce que tu feras en pandas (`df["ca"] = 35*df["quantite"] - 150`) ou en DAX dans Power BI. Une expression algébrique = une colonne dérivée.

#### Exemple chiffré métier
Ch'ti Boutique vend des pulls à **35 €** l'unité, avec **150 €** de frais fixes par jour (loyer, électricité). Le chiffre d'affaires net d'un jour s'écrit :

```
CA = 35 × q − 150
```

où `q` = nombre de pulls vendus. Si `q = 20` : `CA = 35 × 20 − 150 = 700 − 150 = 550 €`.

#### Formule
Évaluer une expression = **remplacer la variable par sa valeur**, puis calculer en respectant les priorités (× et ÷ avant + et −).

#### Calcul à la main
Pour `q = 12` :
```
CA = 35 × 12 − 150
   = 420 − 150
   = 270 €
```

#### Calcul en Python
```python
import numpy as np

# Une seule valeur
q = 12
ca = 35 * q - 150
print(ca)          # 270

# Toute une colonne de données d'un coup (le réflexe data !)
quantites = np.array([12, 20, 5, 0, 35])
ca = 35 * quantites - 150
print(ca)          # [ 270  550   25 -150 1075]
```
👉 Remarque le pouvoir de `numpy` : une seule ligne applique l'expression à **toutes** les lignes du jeu de données.

#### Erreurs courantes
- ❌ Oublier les priorités : `35 × q − 150` ≠ `35 × (q − 150)`.
- ❌ Confondre `2x` (qui veut dire `2 × x`) avec `2 + x`.
- ❌ En Python, écrire `35q` au lieu de `35 * q` (le `*` est obligatoire).

---

### Équations du 1er degré

#### Définition
Une **équation du 1er degré** est une égalité du type `ax + b = 0` (ou `ax + b = c`) où l'on cherche la valeur de `x` qui rend l'égalité vraie. « 1er degré » = la variable est à la puissance 1 (pas de `x²`).

> 🧠 **Moyen mnémo.** Résoudre une équation = **balance à deux plateaux** ⚖️. Ce que tu fais d'un côté du `=`, tu le fais de l'autre, sinon la balance penche. Un terme qui **traverse** le `=` **change de signe** (le `−150` devient `+150`) : il « saute par-dessus » et atterrit à l'envers.

> 🎯 **Ça te servira pour…** répondre aux questions à **seuil** : « à partir de combien de clients je suis rentable ? », « à quel mois j'atteins l'objectif annuel ? ». Le point mort (seuil de rentabilité) est l'un des KPIs les plus demandés en analyse business.

#### Exemple chiffré métier
**Question business** : combien de pulls faut-il vendre par jour pour **atteindre l'équilibre** (CA = 0, on couvre juste les frais fixes) ?

> 🎲 *Reviens à ta prédiction du « pari du point mort » : avais-tu deviné autour de 5 ? La méthode exacte le confirme ci-dessous.*

On résout : `35 × q − 150 = 0`.

#### Formule
Pour `ax + b = 0` : la solution est
```
x = −b / a       (à condition que a ≠ 0)
```

#### Calcul à la main
```
35 q − 150 = 0
35 q = 150          (on ajoute 150 des deux côtés)
q = 150 / 35
q = 4,28...         → il faut vendre au moins 5 pulls pour être bénéficiaire
```

Autre exemple — **objectif de CA** : à combien de pulls atteint-on 1 000 € ?
```
35 q − 150 = 1000
35 q = 1150
q = 1150 / 35 ≈ 32,9   → 33 pulls
```

#### Calcul en Python
```python
import numpy as np

# Résoudre 35*q - 150 = 0  -->  q = -b/a avec a=35, b=-150
a, b = 35, -150
q_seuil = -b / a
print(round(q_seuil, 2))      # 4.29

# Objectif : 35*q - 150 = 1000
objectif = 1000
q_objectif = (objectif - b) / a
print(round(q_objectif, 2))   # 32.86

# Avec numpy.roots pour ax + b = 0 (forme polynomiale [a, b])
racines = np.roots([35, -150])
print(racines)                # [4.28571429]
```

#### Erreurs courantes
- ❌ Changer un terme de côté **sans changer son signe** (`+150` devient `−150` quand il traverse le `=`).
- ❌ Diviser par `a` en oubliant que `a` doit être différent de 0.
- ❌ Donner un résultat décimal (4,28 pulls) sans **l'interpréter métier** : on ne vend pas un tiers de pull → on arrondit au bon sens (ici **vers le haut**, 5).

---

### La notion de fonction (entrée → sortie)

#### Définition
Une **fonction** est une **machine** : tu lui donnes une entrée `x`, elle renvoie **une seule** sortie `y`. On note `f(x)` la sortie (« f de x »).

```
   x  ──►  [ fonction f ]  ──►  y = f(x)
 entrée                          sortie
```

> En data, une fonction relie une **variable explicative** (entrée) à une **variable cible** (sortie). Ex : `f(mois) = CA prévu`.

> 🧠 **Analogie du quotidien.** Une fonction, c'est un **distributeur automatique** 🥤 : tu mets une pièce (entrée `x`), tu reçois **une** canette (sortie `y`). Même pièce → même canette, toujours. Et il ne te crache **jamais deux canettes** pour une seule pièce (c'est la règle d'or : une entrée = une seule sortie).

> 🎯 **Ça te servira pour…** comprendre tout modèle prédictif. Un modèle de machine learning, au fond, c'est une fonction géante : tu lui donnes des entrées (âge, ville, historique…) et il renvoie une prédiction (`f(entrées) = churn probable ?`).

#### Exemple chiffré métier
Soit `f(q) = 35q − 150` (le CA en fonction du nombre de pulls). C'est une fonction :
- entrée `q = 10` → sortie `f(10) = 200`
- entrée `q = 30` → sortie `f(30) = 900`

#### Formule
`y = f(x)`. À **chaque** entrée correspond **une et une seule** sortie.

#### Calcul à la main
`f(8) = 35 × 8 − 150 = 280 − 150 = 130 €`.

#### Calcul en Python
```python
# Définir une fonction en Python = exactement la même idée qu'en maths
def f(q):
    return 35 * q - 150

print(f(8))    # 130
print(f(30))   # 900

# Appliquer la fonction à plusieurs entrées
import numpy as np
quantites = np.array([0, 10, 20, 30])
print(f(quantites))   # [-150  200  550  900]
```

#### Erreurs courantes
- ❌ Croire qu'une entrée peut donner deux sorties différentes (interdit pour une fonction).
- ❌ Confondre `f(x)` (la sortie) avec `f` (la fonction elle-même).

---

### Fonctions linéaires et affines (`y = ax + b`)

#### Définition
- **Fonction linéaire** : `y = ax`. La droite **passe par l'origine** (0, 0). Modélise une **proportionnalité** (ex : prix total = prix unitaire × quantité).
- **Fonction affine** : `y = ax + b`. Une droite qui **ne passe pas forcément par l'origine**. C'est la fonction linéaire + un décalage `b`.

Deux paramètres clés :
- **`a` = la pente** (coefficient directeur) → l'inclinaison de la droite.
- **`b` = l'ordonnée à l'origine** → la valeur de `y` quand `x = 0` (le point de départ).

> 🧠 **Le moyen mnémo à graver — la rampe de skate** 🛹. Dans `y = ax + b` :
> - **`a` = la pente de la rampe** : plus `a` est grand, plus ça grimpe vite (et si `a` est négatif, ça descend).
> - **`b` = là où tu démarres** : la hauteur du sol au point de départ (quand `x = 0`).
>
> « **`a` la pente, `b` le départ** » — répète-le, c'est l'aimant de tout le chapitre.

> 🎯 **Ça te servira pour…** la **régression linéaire** (chapitre 5) et toute analyse de **tendance**. Quand un outil te sort « droite de tendance : y = 1200x + 18000 », tu sauras *immédiatement* lire « ça part de 18 000 et ça gagne 1 200 par pas de temps ». C'est le modèle de prévision le plus utilisé en entreprise.

#### Exemple chiffré métier
Le CA mensuel de Ch'ti Boutique à Lille suit une tendance modélisée par :
```
CA(mois) = 1200 × mois + 18000
```
- `b = 18 000` → CA de départ (mois 0, point de référence janvier) : 18 000 €.
- `a = 1200` → le CA gagne **1 200 € par mois** (tendance haussière).

Prévision pour le mois 6 (juin) : `CA(6) = 1200 × 6 + 18000 = 7200 + 18000 = 25 200 €`.

#### Formule
```
y = a·x + b
a = pente (taux de variation)   b = ordonnée à l'origine (valeur en x=0)
```

#### Calcul à la main
Tracer `y = 1200x + 18000` : on calcule **deux points** suffisent (une droite = 2 points).
- `x = 0` → `y = 18 000` → point (0 ; 18 000)
- `x = 5` → `y = 1200×5 + 18000 = 24 000` → point (5 ; 24 000)

On relie les deux points à la règle.

#### Calcul en Python
```python
import numpy as np
import matplotlib.pyplot as plt

a, b = 1200, 18000
mois = np.arange(0, 13)          # de janvier (0) à décembre (12)
ca = a * mois + b                # la fonction affine appliquée

plt.figure(figsize=(8, 5))
plt.plot(mois, ca, marker='o', color='#0072B2')
plt.title("CA mensuel prévu — Ch'ti Boutique (Lille)")
plt.xlabel("Mois (0 = janvier)")
plt.ylabel("Chiffre d'affaires (€)")
plt.axhline(b, color='gray', ls='--', lw=1)   # ordonnée à l'origine b
plt.text(0.2, b + 400, f"b = {b} € (départ)", color='gray')
plt.grid(True, alpha=0.3)
plt.show()

print("CA en juin (mois 6) :", a * 6 + b, "€")   # 25200 €
```

#### Erreurs courantes
- ❌ Confondre **linéaire** (passe par 0) et **affine** (décalée de `b`). En statistiques, le terme « régression linéaire » désigne en réalité une fonction **affine** !
- ❌ Inverser `a` et `b` dans `y = ax + b`.
- ❌ Oublier que `b` = la valeur quand `x = 0`, pas « la première valeur du tableau » si ton tableau ne commence pas à 0.

---

### La pente comme taux de variation

#### Définition
La **pente `a`** mesure **de combien `y` change quand `x` augmente de 1**. C'est le **taux de variation** :
```
a = (variation de y) / (variation de x) = Δy / Δx
```
(le symbole `Δ`, « delta », signifie « variation de »).

> 🔑 **C'est LA notion clé du data analyst.** La pente, c'est la **vitesse d'évolution** : +1 200 €/mois, −3 % de churn par trimestre, +50 visiteurs/jour…

> 🧠 **Analogie du quotidien.** La pente, c'est le **compteur de vitesse** de ta voiture 🚗. La hauteur (le CA total) te dit *où tu es* ; la pente te dit *à quelle vitesse tu y vas*. Deux boutiques peuvent être au même CA — l'une fonce (pente forte), l'autre est à l'arrêt (pente nulle).

> 🎯 **Ça te servira pour…** **analyser les tendances** — et ce dès le module 1.3 (Phase 1) ! Repérer si une métrique accélère, ralentit ou décline est le geste data analyst n°1. Le « +1 200 €/mois » d'aujourd'hui devient le « +8 % de trafic par semaine » de ton premier vrai dataset.

> 🎲 *Reviens à ton « pari de la pente » du début : 18 000 → 24 000 sur 5 mois. Réponse = (24000−18000)/5 = **1 200 €/mois**. Tu avais bon ?*

#### Exemple chiffré métier
Le CA de la boutique de Roubaix passe de **20 000 €** au mois 2 à **26 000 €** au mois 5.
```
a = (26000 − 20000) / (5 − 2) = 6000 / 3 = 2000 €/mois
```
La boutique de Roubaix croît **plus vite** (2 000 €/mois) que celle de Lille (1 200 €/mois) : pente plus forte = droite plus « raide ».

#### Formule
```
a = (y₂ − y₁) / (x₂ − x₁)
```
- `a > 0` → croissance (la droite monte)
- `a < 0` → décroissance (la droite descend)
- `a = 0` → constante (droite horizontale)

#### Calcul à la main
Boutique de Dunkerque : CA de **15 000 €** au mois 1, **12 000 €** au mois 4.
```
a = (12000 − 15000) / (4 − 1) = −3000 / 3 = −1000 €/mois
```
Pente **négative** → le CA **baisse** de 1 000 €/mois. Alerte business !

#### Calcul en Python
```python
import numpy as np

# Deux points (x1, y1) et (x2, y2)
def pente(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)

print(pente(2, 20000, 5, 26000))   # 2000.0  -> Roubaix, croissance
print(pente(1, 15000, 4, 12000))   # -1000.0 -> Dunkerque, décroissance

# Calculer la pente entre points consécutifs d'une série (np.diff)
ca = np.array([18000, 19200, 20400, 21600, 22800])   # mensuel
variations = np.diff(ca)            # différences d'un mois à l'autre
print(variations)                   # [1200 1200 1200 1200] -> pente constante = affine !
```
👉 Si `np.diff` donne des écarts **constants**, c'est le signe que la tendance est **affine**.

#### Erreurs courantes
- ❌ Inverser numérateur et dénominateur : c'est `Δy / Δx`, pas `Δx / Δy`.
- ❌ Oublier l'unité du taux de variation (€/mois, %/an…) → un nombre seul ne veut rien dire.
- ❌ Confondre pente forte et valeur élevée : une droite peut être haute (gros CA) mais plate (pente nulle, pas de croissance).

---

### Repère cartésien & lecture de graphiques (C17)

#### Définition
Un **repère cartésien** est formé de deux axes perpendiculaires :
- l'axe **horizontal** = **abscisses** (`x`), souvent le temps ou la variable d'entrée ;
- l'axe **vertical** = **ordonnées** (`y`), souvent la mesure (CA, ventes…).

Un **point** se note `(x ; y)` : on lit d'abord l'abscisse, puis l'ordonnée.

> 🧠 **Moyen mnémo.** « **x avant y, comme dans l'alphabet** » : on cite toujours l'horizontal (x) en premier, le vertical (y) ensuite. Et pour l'origine `b` : c'est là où la courbe **perce l'axe vertical** (la « porte d'entrée » du graphe, à gauche).

> 🎯 **Ça te servira pour…** **toute la dataviz**. Un dashboard Power BI / Tableau / Looker Studio n'est qu'un empilement de repères cartésiens. Savoir lire (et faire dire) un point, une pente, une échelle = la compétence **C17**, celle qu'on te demandera de prouver en jury.

#### Exemple chiffré métier
Sur le graphe du CA de Lille, le point `(6 ; 25200)` se lit : « **en juin (mois 6), le CA prévu est 25 200 €** ». Lire un graphe = traduire un point en phrase métier.

#### Formule / méthode de lecture
1. **Repère les axes** : que représentent x et y ? quelle unité ? quelle échelle ?
2. **Lis l'ordonnée à l'origine** (où la courbe coupe l'axe vertical) = point de départ.
3. **Repère la tendance** : ça monte (croissance), ça descend (décroissance), c'est plat ?
4. **Estime la pente** : sur 1 unité en x, de combien monte/descend y ?
5. **Traduis en phrase métier.**

#### Calcul à la main
Pour lire la pente sur un graphe : choisis 2 points faciles à lire, applique `a = Δy / Δx`. Si la courbe passe par (0 ; 18000) et (5 ; 24000) → `a = (24000−18000)/5 = 1200 €/mois`.

#### Calcul en Python
```python
import numpy as np
import matplotlib.pyplot as plt

mois = np.array([0, 1, 2, 3, 4, 5, 6])
lille    = 1200 * mois + 18000
roubaix  = 2000 * mois + 14000
dunkerque = -1000 * mois + 16000   # en baisse

plt.figure(figsize=(9, 5))
plt.plot(mois, lille,     marker='o', label="Lille (+1200 €/mois)")
plt.plot(mois, roubaix,   marker='s', label="Roubaix (+2000 €/mois)")
plt.plot(mois, dunkerque, marker='^', label="Dunkerque (−1000 €/mois)")
plt.title("Comparaison des tendances de CA — 3 boutiques")
plt.xlabel("Mois (0 = janvier)")
plt.ylabel("Chiffre d'affaires (€)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```
👉 D'un coup d'œil : Roubaix monte le plus vite (pente raide), Dunkerque décline (pente négative). **C'est ça, faire parler un graphe.**

#### Erreurs courantes
- ❌ Lire le point dans le mauvais ordre : `(6 ; 25200)` ≠ `(25200 ; 6)`.
- ❌ Ne pas regarder l'**échelle** : un axe `y` qui ne commence pas à 0 exagère visuellement les variations (piège classique de dataviz trompeuse !).
- ❌ Confondre une **valeur élevée** avec une **forte croissance** (cf. pente vs hauteur).

---

## Vidéos d'auto-formation

> ⚠️ Les liens directs vers une vidéo précise peuvent changer. En cas de doute, utilise le lien de **recherche YouTube** fourni, qui te mènera toujours à la bonne chaîne.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| LE COURS : Fonctions affines (3e–2nde) | Yvan Monka (maths-et-tiques) | 🇫🇷 FR | ~18 min | [Recherche YouTube](https://www.youtube.com/results?search_query=yvan+monka+le+cours+fonctions+affines) | Définition, pente, ordonnée à l'origine, croissance — le cours complet et clair |
| Déterminer une fonction affine avec le taux d'accroissement | Yvan Monka | 🇫🇷 FR | ~7 min | [Recherche YouTube](https://www.youtube.com/results?search_query=yvan+monka+fonction+affine+taux+d%27accroissement) | Calculer la pente `a` à partir de 2 points (le taux de variation en pratique) |
| Déterminer graphiquement la pente d'une droite | Khan Academy (FR) | 🇫🇷 FR | ~5 min | [YouTube](https://www.youtube.com/watch?v=jzbNANey-58) | Lire et calculer la pente directement sur un graphique (compétence C17) |
| Intro to slope-intercept form (y = mx + b) | Khan Academy | 🇬🇧 EN | ~10 min | [Khan Academy](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:forms-of-linear-equations/x2f8bb11595b61c86:intro-to-slope-intercept-form/v/slope-intercept-form) | La forme `y = mx + b` : rôle de la pente `m` et de l'ordonnée `b` |
| Slope-intercept form (Algebra I) | Khan Academy | 🇬🇧 EN | ~14 min | [YouTube](https://www.youtube.com/watch?v=IL3UCuXrUzE) | Construire l'équation d'une droite à partir d'infos partielles |

---

## Exercices

> Contexte : enseigne **Ch'ti Boutique** (Lille / Roubaix / Dunkerque). Fais d'abord à la main, puis vérifie en Python.

### Exercice 1 — Évaluer une expression
Le CA journalier d'une boutique est `CA = 28q − 120` (pulls à 28 €, 120 € de frais fixes).
Calcule le CA pour `q = 6`, `q = 15`, `q = 0`.

<details><summary>✅ Corrigé</summary>

- `q = 6` : `28×6 − 120 = 168 − 120 = 48 €`
- `q = 15` : `28×15 − 120 = 420 − 120 = 300 €`
- `q = 0` : `28×0 − 120 = −120 €` (on perd les frais fixes : aucune vente)

```python
import numpy as np
q = np.array([6, 15, 0])
print(28*q - 120)   # [  48  300 -120]
```
</details>

---

### Exercice 2 — Équation du 1er degré (seuil de rentabilité)
Avec `CA = 28q − 120`, combien de pulls faut-il vendre pour atteindre l'équilibre (CA = 0) ? Et pour atteindre 500 € ?

<details><summary>✅ Corrigé</summary>

**Équilibre** : `28q − 120 = 0` → `q = 120/28 ≈ 4,29` → **5 pulls** (arrondi au-dessus).
**500 €** : `28q − 120 = 500` → `28q = 620` → `q = 620/28 ≈ 22,1` → **23 pulls**.

```python
a, b = 28, -120
print(-b/a)            # 4.2857...
print((500 - b)/a)     # 22.14...
```
</details>

---

### Exercice 3 — Identifier pente et ordonnée à l'origine
Soit la tendance `CA(mois) = 950·mois + 21000`.
a) Quelle est l'ordonnée à l'origine ? Que signifie-t-elle ?
b) Quelle est la pente ? Interprète-la en langage métier.
c) Prévois le CA au mois 9.

<details><summary>✅ Corrigé</summary>

a) `b = 21 000` → CA de départ (mois 0) = 21 000 €.
b) `a = 950` → le CA augmente de **950 € chaque mois** (croissance, pente positive).
c) `CA(9) = 950×9 + 21000 = 8550 + 21000 = 29 550 €`.

```python
a, b = 950, 21000
print(a*9 + b)    # 29550
```
</details>

---

### Exercice 4 — Calculer une pente à partir de 2 points
La boutique de Roubaix a fait **22 000 €** au mois 2 et **31 000 €** au mois 7.
a) Calcule la pente (taux de variation). b) La tendance est-elle croissante ou décroissante ? c) Écris l'équation affine complète `y = ax + b`.

<details><summary>✅ Corrigé</summary>

a) `a = (31000 − 22000)/(7 − 2) = 9000/5 = 1800 €/mois`.
b) `a > 0` → **croissante**.
c) On a `a = 1800`. Pour `b` : au mois 2, `y = 22000`, donc `22000 = 1800×2 + b` → `b = 22000 − 3600 = 18400`.
→ `CA(mois) = 1800·mois + 18400`.

```python
x1, y1, x2, y2 = 2, 22000, 7, 31000
a = (y2 - y1)/(x2 - x1)         # 1800.0
b = y1 - a*x1                   # 18400.0
print(a, b)
```
</details>

---

### Exercice 5 — Lecture de graphique
On te donne la série mensuelle du CA de Dunkerque : `[16000, 15000, 14000, 13000, 12000]` (mois 0 à 4).
a) La tendance monte-t-elle ou descend-elle ? b) Quel est le taux de variation par mois ? c) Si la tendance continue, à quel mois le CA atteindra-t-il 9 000 € ?

<details><summary>✅ Corrigé</summary>

a) Les valeurs **diminuent** → tendance décroissante.
b) Écart constant de −1 000 €/mois → `a = −1000`. (`np.diff` le confirme.)
c) Équation : `CA = −1000·mois + 16000`. On résout `−1000·mois + 16000 = 9000` → `−1000·mois = −7000` → `mois = 7`. → **mois 7**.

```python
import numpy as np
ca = np.array([16000, 15000, 14000, 13000, 12000])
print(np.diff(ca))             # [-1000 -1000 -1000 -1000]
# mois pour atteindre 9000
a, b = -1000, 16000
print((9000 - b)/a)            # 7.0
```
</details>

---

### Exercice 6 — Comparer deux modèles
Boutique A : `CA = 1500·mois + 10000`. Boutique B : `CA = 800·mois + 20000`.
a) Laquelle démarre le plus haut ? b) Laquelle croît le plus vite ? c) À quel mois ont-elles le même CA ?

<details><summary>✅ Corrigé</summary>

a) Ordonnées à l'origine : A = 10 000 €, B = 20 000 € → **B démarre plus haut**.
b) Pentes : A = 1500, B = 800 → **A croît plus vite**.
c) On résout `1500·mois + 10000 = 800·mois + 20000` :
`1500·mois − 800·mois = 20000 − 10000` → `700·mois = 10000` → `mois ≈ 14,3` → vers le **mois 15**, A rattrape puis dépasse B.

```python
import numpy as np
# 1500m + 10000 = 800m + 20000  ->  700m - 10000 = 0
print(np.roots([700, -10000]))   # [14.2857...]
```
</details>

---

## Quiz (5 QCM)

**Q1.** Dans `y = ax + b`, que représente `b` ?
- A) La pente
- B) La valeur de `y` quand `x = 0` (ordonnée à l'origine)
- C) La valeur de `x` quand `y = 0`

**Q2.** Une pente `a = −500 €/mois` signifie :
- A) Le CA est de 500 €
- B) Le CA augmente de 500 €/mois
- C) Le CA diminue de 500 €/mois

**Q3.** Quelle fonction passe obligatoirement par l'origine (0, 0) ?
- A) La fonction affine `y = ax + b`
- B) La fonction linéaire `y = ax`
- C) Aucune des deux

**Q4.** Sur un repère cartésien, le point `(4 ; 9000)` se lit :
- A) x = 9000 et y = 4
- B) x = 4 et y = 9000
- C) pente = 4, ordonnée = 9000

**Q5.** Pour résoudre `35q − 150 = 0`, on trouve :
- A) `q = 35/150`
- B) `q = 150/35 ≈ 4,29`
- C) `q = 150 × 35`

<details><summary>✅ Réponses</summary>

1. **B** — `b` est l'ordonnée à l'origine.
2. **C** — pente négative = décroissance, donc le CA diminue de 500 €/mois.
3. **B** — la fonction linéaire `y = ax` passe par (0,0) ; l'affine est décalée de `b`.
4. **B** — on lit toujours `(abscisse ; ordonnée)`, donc x = 4, y = 9000.
5. **B** — `35q = 150` donc `q = 150/35 ≈ 4,29`.
</details>

---

## À retenir

- 🔤 **Variable** = lettre qui varie (une colonne en data). **Expression** = combinaison de variables et d'opérations ; on l'**évalue** en remplaçant.
- ⚖️ **Équation du 1er degré** `ax + b = 0` → solution `x = −b/a` (si `a ≠ 0`). Sert à trouver un **seuil** ou un **objectif**.
- 🤖 **Fonction** = machine entrée → sortie ; à chaque `x`, une seule sortie `f(x)`.
- 📈 **Fonction affine** `y = ax + b` = **le modèle de tendance linéaire de base** (cœur de la régression linéaire).
  - **`a` = pente = taux de variation** = vitesse d'évolution (€/mois, %/an…). `a > 0` monte, `a < 0` descend.
  - **`b` = ordonnée à l'origine** = valeur de départ (en `x = 0`).
- 🧮 **Pente entre 2 points** : `a = (y₂ − y₁)/(x₂ − x₁) = Δy/Δx`. En Python : `np.diff` repère une tendance affine (écarts constants).
- 🗺️ **Lire un graphe (C17)** : identifier axes + échelle → ordonnée à l'origine → tendance → pente → **traduire en phrase métier**. Attention à l'échelle qui peut tromper l'œil.
- 🐍 **Réflexe data** : avec `numpy`, on applique une expression/fonction à **toute une colonne** en une ligne ; avec `matplotlib`, on visualise la tendance.
- 🔗 **Et après ?** Garde ta **pente** au chaud : elle revient dès le **module 1.3 (Phase 1)** pour **analyser les tendances** d'un vrai jeu de données. Ce chapitre est la rampe de lancement de toute ton analyse de données.

---

## 🏆 Défi du chapitre — « Sauve la boutique de Dunkerque »

Martine débarque, inquiète : **« Dunkerque coule ! Aide-moi. »** Voici les chiffres réels du CA de Dunkerque :

| Mois | 0 | 3 | 6 |
|---|---|---|---|
| CA (€) | 16 000 | 13 000 | 10 000 |

À toi de jouer (fais-le **à la main d'abord**, puis vérifie en Python) :

1. 🎲 **Devine d'abord** : la tendance monte ou descend ? Et à la louche, de combien par mois ?
2. **Calcule la pente** `a` (taux de variation, en €/mois).
3. **Trouve l'ordonnée à l'origine `b`** et écris l'équation affine complète `CA(mois) = a·mois + b`.
4. **Prédis** le CA au **mois 10** si rien ne change.
5. **Le couperet** : à quel mois le CA atteindra-t-il **0 €** (la boutique ferme) ?
6. 💬 **Une phrase pour Martine** : traduis tes résultats en langage métier (et propose une action !).

> 🥇 **Barème perso** : 3/6 → tu tiens la notion. 5/6 → tu es prêt pour la dataviz. 6/6 + la phrase métier → tu raisonnes déjà comme un data analyst.

<details><summary>🏆 Solution complète</summary>

**1. Prédiction** : ça **descend** (les valeurs baissent), d'environ −1 000 €/mois.

**2. Pente** — entre les points (0 ; 16000) et (6 ; 10000) :
```
a = (10000 − 16000) / (6 − 0) = −6000 / 6 = −1000 €/mois
```
Pente **négative** → décroissance confirmée.

**3. Ordonnée à l'origine & équation** : au mois 0, le CA vaut 16 000, donc `b = 16000`.
```
CA(mois) = −1000 · mois + 16000
```

**4. Prévision mois 10** :
```
CA(10) = −1000 × 10 + 16000 = −10000 + 16000 = 6 000 €
```

**5. Le couperet (CA = 0)** — on résout `−1000·mois + 16000 = 0` :
```
−1000·mois = −16000   →   mois = 16
```
→ Au **mois 16**, le CA tombe à 0 si rien ne change.

**6. Phrase pour Martine** : *« Le CA de Dunkerque perd 1 200… pardon, **1 000 € chaque mois** (pente −1000). Au rythme actuel, on passe sous **6 000 € au mois 10** et la boutique atteint 0 € au **mois 16**. Il faut réagir maintenant : promo locale, révision des frais fixes ou réallocation de stock vers Roubaix qui, elle, cartonne. »*

```python
import numpy as np

mois = np.array([0, 3, 6])
ca   = np.array([16000, 13000, 10000])

# 2. pente (vérif : écarts constants ?)
a = (ca[-1] - ca[0]) / (mois[-1] - mois[0])
print("pente a =", a)            # -1000.0

# 3. ordonnée à l'origine
b = ca[0]                        # mois 0 -> b
print("b =", b)                  # 16000

# 4. prévision mois 10
print("CA(10) =", a*10 + b)      # 6000.0

# 5. mois où CA = 0  -> a*m + b = 0  ->  m = -b/a
print("CA=0 au mois", -b/a)      # 16.0
```
</details>

---
