# 03 — Initiation à Python

> **Avant les maths, avant l'analyse de données : on apprend à parler à la machine.** Tout le reste de ta formation (statistiques, pandas, visualisation) repose sur du code Python. Ce module est là pour qu'à partir de maintenant, le code ne te fasse plus peur. On part de **zéro absolu** : aucune ligne de code n'est supposée connue.

| | |
|---|---|
| **Phase** | Phase 0 — La Prairie (semaine 1–2) |
| **Place dans le parcours** | **Tout au début**, AVANT le module de Maths et AVANT le module « pandas » |
| **Durée indicative** | ≈ 14 h |
| **Objectif** | Pré-requis technique transversal (socle Python pour les analyses exploratoires) |
| **Pré-requis** | le module « posture & méthode ». Savoir allumer un ordinateur, naviguer sur le web, créer un compte. **Aucun pré-requis en programmation.** |
| **Outils** | Un navigateur web + **Google Colab** (gratuit, rien à installer) ou Jupyter/Anaconda |

---

## Objectifs du module

À la fin de ce module, tu seras capable de :

- **Comprendre ce qu'est un programme** et une instruction, et **exécuter du code** dans un notebook.
- **Créer et utiliser des variables**, et reconnaître les **types de base** (`int`, `float`, `str`, `bool`).
- **Faire des opérations** et **afficher** des résultats proprement avec les **f-strings**.
- **Stocker plusieurs valeurs** dans des **listes** et des **dictionnaires** (notions).
- **Prendre des décisions** avec `if / elif / else`.
- **Répéter une action** avec une boucle `for` (notion simple).
- **Écrire et appeler une fonction** (`def`, `return`, arguments).
- **Importer une bibliothèque** (ex. `import numpy as np`) et comprendre à quoi ça sert.
- **Lire un tout petit fichier de données** avec pandas (`read_csv`, `.head()`) — un avant-goût du module « analyse exploratoire (EDA) ».
- **Lire un message d'erreur** sans paniquer et **commenter ton code**.

> 🎯 **L'objectif n'est PAS de devenir développeur.** L'objectif est que tu puisses **lire, comprendre et modifier** du code data. Tu n'as pas besoin de tout retenir par cœur : tu as besoin de **comprendre la logique**.

---

## Pourquoi Python pour un Data Analyst ?

Tu es là pour devenir Data Analyst, pas codeur. Alors pourquoi apprendre à programmer ?

1. **Excel atteint vite ses limites.** Au-delà de ~100 000 lignes, Excel rame ou plante. Python avale des millions de lignes sans broncher.
2. **Python est LE langage de la data.** Les bibliothèques `pandas` (tableaux de données), `numpy` (calcul), `matplotlib`/`seaborn` (graphiques) sont des standards mondiaux du métier. Les offres d'emploi de Data Analyst le demandent quasiment toutes.
3. **Le code est reproductible et traçable.** Avec Excel, si tu cliques 40 fois pour nettoyer un fichier, personne ne peut refaire exactement la même chose. Avec Python, tes manipulations sont **écrites** : tu peux les rejouer, les corriger, les partager.
4. **C'est plus simple qu'on ne le croit.** Python a été conçu pour être **lisible**, proche de l'anglais courant. `if age >= 18:` se lit « si âge supérieur ou égal à 18 ». Tu vas voir, ça se dompte.

> 💡 **Le pont avec la suite.** Tout ce que tu calcules au module de Maths (moyenne, médiane, écart-type…), tu le **reproduiras en une ligne de code** au module « analyse exploratoire (EDA) » avec pandas. Ce module te donne les fondations pour que ce moment se passe bien — sans décrochage.

> ⚠️ **Le piège qu'on veut t'éviter.** Sans cette initiation, le code surgit brutalement dès les maths puis « explose » avec pandas. Beaucoup décrochent à ce moment-là. C'est exactement pour **toi** que ce module existe : prends-le au sérieux et tu aborderas la suite sereinement.

---

## Mise en route : ton premier environnement de code

### Qu'est-ce qu'un programme ? Une instruction ?

Un **ordinateur ne fait que ce qu'on lui dit**, dans l'ordre, sans rien deviner. Un **programme** est une **liste d'instructions** que la machine exécute **de haut en bas**, une par une.

Une **instruction**, c'est un ordre élémentaire : « affiche ce texte », « range cette valeur dans cette boîte », « si telle condition est vraie, fais ceci ».

> 🧠 **Image mentale.** Programmer, c'est écrire une **recette de cuisine** très précise pour quelqu'un qui ne réfléchit pas du tout : si tu oublies « préchauffer le four », il ne le fera pas. La machine est rapide et obéissante, mais bête : la précision, c'est ton travail.

### Le notebook : ton terrain de jeu

En data, on n'écrit pas du code dans un gros fichier compliqué : on utilise un **notebook** (Jupyter, ou **Google Colab** dans ton navigateur). Un notebook est fait de **cellules**. Tu écris du code dans une cellule, tu l'exécutes, et le **résultat s'affiche juste en dessous**. Parfait pour explorer des données étape par étape.

**Comment exécuter une cellule :** tu cliques dedans, puis tu fais **Maj + Entrée** (Shift + Enter).

```python
# Ceci est ton tout premier programme.
# Tout ce qui suit un "#" est un COMMENTAIRE : la machine l'ignore, c'est pour les humains.
print("Bonjour, je commence Python !")  # print() affiche un message à l'écran
```

Résultat affiché :

```
Bonjour, je commence Python !
```

`print(...)` est une **instruction** qui veut dire « affiche à l'écran ce qu'il y a entre les parenthèses ».

> 🎯 **Mini-exercice 1.** Ouvre un notebook (Colab) et fais afficher : `Je m'appelle [ton prénom] et je deviens Data Analyst`. Exécute la cellule avec Maj + Entrée.

<details>
<summary>✅ Correction</summary>

```python
print("Je m'appelle Camille et je deviens Data Analyst")
```

Le texte doit être **entre guillemets** `"..."`. Si tu oublies les guillemets, Python croit que c'est du code et renvoie une erreur. Remplace simplement `Camille` par ton prénom.
</details>

---

## Les variables et les types de base

### Une variable = une boîte étiquetée

Une **variable** est une **boîte** dans laquelle tu ranges une valeur, avec une **étiquette** (son nom) pour la retrouver. On range une valeur avec le signe `=` (qu'on lit « reçoit » ou « prend la valeur »).

```python
age = 30              # une boîte nommée "age" qui contient 30
prenom = "Camille"    # une boîte nommée "prenom" qui contient le texte Camille
taille = 1.75         # une boîte "taille" qui contient un nombre à virgule
print(age)            # affiche 30
print(prenom)         # affiche Camille
```

> ⚠️ `=` n'est PAS « égal » au sens des maths. C'est une **affectation** : « range la valeur de droite dans la boîte de gauche ». On verra plus loin que « tester l'égalité » s'écrit `==` (double signe).

### Les 4 types de base

Chaque valeur a un **type**. Les quatre essentiels :

| Type | Nom complet | C'est quoi | Exemple |
|---|---|---|---|
| `int` | entier | un nombre entier, sans virgule | `42`, `-7`, `0` |
| `float` | flottant | un nombre **à virgule** (le point décimal !) | `1.75`, `3.14`, `-0.5` |
| `str` | chaîne (string) | du **texte**, toujours entre guillemets | `"bonjour"`, `"75000"` |
| `bool` | booléen | une valeur **Vrai/Faux** | `True`, `False` |

```python
nb_ventes = 120        # int  (entier)
prix = 19.99           # float (à virgule -> on écrit un POINT, pas une virgule)
ville = "Toulouse"     # str  (texte entre guillemets)
est_client = True      # bool (Vrai/Faux : True / False avec une majuscule)

# La fonction type() te dit le type d'une valeur :
print(type(nb_ventes))   # <class 'int'>
print(type(prix))        # <class 'float'>
print(type(ville))       # <class 'str'>
print(type(est_client))  # <class 'bool'>
```

> ⚠️ **Piège n°1 des débutants en data.** En Python, le séparateur décimal est le **point** (`19.99`), pas la virgule. Une virgule a un autre sens (elle sépare des éléments).

> ⚠️ **Piège n°2.** `"75000"` (avec guillemets) est du **texte**, pas un nombre. Tu ne pourras pas l'additionner ! C'est une cause d'erreur très fréquente quand on importe des données.

> 🎯 **Mini-exercice 2.** Crée trois variables : ton prénom (texte), ton année de naissance (entier), et `True` ou `False` selon que tu aimes (déjà) Python. Affiche le type de chacune.

<details>
<summary>✅ Correction</summary>

```python
prenom = "Camille"
annee_naissance = 1994
aime_python = True

print(type(prenom))           # <class 'str'>
print(type(annee_naissance))  # <class 'int'>
print(type(aime_python))      # <class 'bool'>
```
</details>

---

## Opérations et affichage (f-strings)

### Les opérations

Python est une super calculatrice :

```python
print(10 + 3)    # 13   addition
print(10 - 3)    # 7    soustraction
print(10 * 3)    # 30   multiplication (étoile)
print(10 / 3)    # 3.333...  division (donne toujours un float)
print(10 // 3)   # 3    division entière (le quotient sans virgule)
print(10 % 3)    # 1    modulo (le RESTE de la division) -> très utile (pair/impair)
print(10 ** 2)   # 100  puissance (10 au carré)
```

On peut aussi « additionner » du texte (on appelle ça **concaténer**) :

```python
prenom = "Camille"
message = "Bonjour " + prenom + " !"
print(message)   # Bonjour Camille !
```

### Les f-strings : la bonne façon d'afficher

Mélanger texte et variables avec des `+` devient vite pénible (et plante si on oublie de convertir un nombre en texte). La solution moderne et propre : la **f-string**. On met un `f` juste avant les guillemets, et on glisse les variables entre **accolades** `{}`.

```python
prenom = "Camille"
age = 30
ventes = 120
prix = 19.99

# f-string : un f devant les guillemets, les variables entre { }
print(f"{prenom} a {age} ans.")
# Camille a 30 ans.

print(f"Total : {ventes * prix} euros")   # on peut même calculer dans les accolades
# Total : 2398.8 euros

# Bonus : arrondir à 2 décimales avec :.2f
print(f"Total : {ventes * prix:.2f} euros")
# Total : 2398.80 euros
```

> 💡 **Retiens l'f-string : tu l'utiliseras tout le temps** pour afficher des résultats d'analyse (« moyenne des ventes : 2398.80 € »).

> 🎯 **Mini-exercice 3.** Tu as vendu `45` produits à `12.50 €` l'unité. Avec une f-string, affiche : `J'ai vendu 45 produits pour un total de 562.50 euros`.

<details>
<summary>✅ Correction</summary>

```python
quantite = 45
prix = 12.50
print(f"J'ai vendu {quantite} produits pour un total de {quantite * prix:.2f} euros")
# J'ai vendu 45 produits pour un total de 562.50 euros
```
</details>

---

## Stocker plusieurs valeurs : listes et dictionnaires

Jusqu'ici une variable = une seule valeur. Mais en data, on manipule des **collections** de valeurs. Deux structures essentielles.

### La liste : une suite ordonnée de valeurs

Une **liste** range plusieurs valeurs **dans l'ordre**, entre **crochets** `[ ]`, séparées par des virgules.

```python
ventes = [120, 95, 200, 75, 180]      # une liste de 5 nombres
villes = ["Paris", "Lyon", "Toulouse"] # une liste de textes

# On accède à un élément par sa POSITION (l'index), qui COMMENCE À 0 !
print(ventes[0])    # 120  -> le PREMIER élément (index 0)
print(ventes[1])    # 95   -> le deuxième
print(villes[-1])   # Toulouse -> le DERNIER (index -1)

# Quelques actions utiles :
print(len(ventes))      # 5     -> len() = nombre d'éléments
ventes.append(300)      # ajoute 300 à la fin
print(ventes)           # [120, 95, 200, 75, 180, 300]
print(sum(ventes))      # 970   -> somme de tous les nombres
print(max(ventes))      # 300   -> le plus grand
```

> ⚠️ **Piège classique : on compte à partir de 0.** Le premier élément est à l'index `0`, pas `1`. Le 5e élément d'une liste est donc à l'index `4`. C'est déroutant au début, c'est normal.

### Le dictionnaire : des paires clé → valeur

Un **dictionnaire** range des valeurs avec une **étiquette (clé)** au lieu d'une position. On utilise des **accolades** `{ }` et des paires `clé: valeur`. Pratique pour décrire **un objet** (un client, un produit…).

```python
client = {
    "nom": "Camille",
    "age": 30,
    "ville": "Toulouse",
    "fidele": True
}

# On accède à une valeur par sa CLÉ (et non par une position) :
print(client["nom"])     # Camille
print(client["ville"])   # Toulouse

# Modifier ou ajouter une info :
client["age"] = 31           # modifie
client["email"] = "c@x.fr"   # ajoute une nouvelle clé
print(client)
```

> 💡 **Pourquoi c'est utile en data ?** Un tableau de données (un DataFrame pandas) ressemble beaucoup à une **liste de dictionnaires** : chaque ligne est un dictionnaire `{colonne: valeur}`. Tu retrouveras cette logique au module « analyse exploratoire (EDA) ».

> 🎯 **Mini-exercice 4.** (a) Crée une liste `temperatures = [18, 21, 25, 19, 22]` et affiche la **dernière** valeur et la **moyenne** (somme / nombre). (b) Crée un dictionnaire `produit` avec les clés `nom`, `prix`, `stock`, puis affiche le prix.

<details>
<summary>✅ Correction</summary>

```python
# (a)
temperatures = [18, 21, 25, 19, 22]
print(temperatures[-1])                       # 22  (dernier élément)
print(sum(temperatures) / len(temperatures))  # 21.0  (moyenne)

# (b)
produit = {"nom": "Café", "prix": 4.5, "stock": 120}
print(produit["prix"])   # 4.5
```
</details>

---

## Les conditions : if / elif / else

Une **condition** permet à ton programme de **prendre une décision** : faire une chose **si** quelque chose est vrai, sinon une autre.

On teste avec des **comparaisons** qui renvoient `True` ou `False` :

| Opérateur | Signification |
|---|---|
| `==` | est égal à (⚠️ DOUBLE signe, à ne pas confondre avec `=`) |
| `!=` | est différent de |
| `>` `<` | supérieur / inférieur |
| `>=` `<=` | supérieur ou égal / inférieur ou égal |

```python
age = 20

if age >= 18:
    print("Tu es majeur.")     # exécuté SI la condition est vraie
else:
    print("Tu es mineur.")     # exécuté SINON
```

Avec plusieurs cas, on ajoute `elif` (« sinon si ») :

```python
note = 14

if note >= 16:
    print("Très bien")
elif note >= 12:
    print("Bien")          # ce cas est retenu pour 14
elif note >= 10:
    print("Passable")
else:
    print("Insuffisant")
```

> ⚠️ **L'INDENTATION est obligatoire en Python.** Le code « à l'intérieur » d'un `if` doit être **décalé vers la droite** (4 espaces, ou une tabulation). Ce décalage n'est pas décoratif : c'est lui qui dit à Python « ceci appartient au if ». Un mauvais alignement = une erreur `IndentationError`.

> ⚠️ **N'oublie pas les deux-points `:`** à la fin de la ligne `if ...:`, `elif ...:`, `else:`.

> 🎯 **Mini-exercice 5.** Une variable `ca` (chiffre d'affaires) vaut `7500`. Affiche `"Objectif atteint"` si `ca >= 5000`, sinon `"En dessous de l'objectif"`. Teste aussi avec `ca = 3000`.

<details>
<summary>✅ Correction</summary>

```python
ca = 7500

if ca >= 5000:
    print("Objectif atteint")
else:
    print("En dessous de l'objectif")
# Avec ca = 7500 -> "Objectif atteint"
# Avec ca = 3000 -> "En dessous de l'objectif"
```
</details>

---

## Les boucles : for (notion simple)

Une **boucle** répète une action **sans copier-coller**. La boucle `for` parcourt **chaque élément** d'une liste, un par un.

```python
ventes = [120, 95, 200]

for v in ventes:        # "pour chaque v dans la liste ventes"
    print(v)            # ce bloc (indenté !) est répété pour chaque valeur
# Affiche 120, puis 95, puis 200
```

À chaque tour, la variable `v` prend la valeur suivante de la liste. On peut faire un calcul dans la boucle :

```python
ventes = [120, 95, 200, 75]
total = 0                  # on part de 0

for v in ventes:
    total = total + v      # on AJOUTE chaque vente au total
    # on aurait pu écrire : total += v  (raccourci équivalent)

print(f"Total des ventes : {total}")   # Total des ventes : 490
```

Pour répéter un nombre fixe de fois, on utilise `range(n)` qui génère les nombres de 0 à n-1 :

```python
for i in range(3):     # i prend les valeurs 0, 1, 2
    print(f"Tour numéro {i}")
# Tour numéro 0 / Tour numéro 1 / Tour numéro 2
```

> 💡 **Bonne nouvelle.** En data avec pandas, tu écriras **peu de boucles** : pandas fait les opérations sur toute une colonne d'un coup. Mais comprendre la boucle `for` t'aide à **lire** du code et à raisonner « pour chaque ligne… ».

> 🎯 **Mini-exercice 6.** Avec une boucle `for`, affiche le carré (`x ** 2`) de chaque nombre de la liste `[1, 2, 3, 4, 5]`.

<details>
<summary>✅ Correction</summary>

```python
nombres = [1, 2, 3, 4, 5]
for x in nombres:
    print(x ** 2)
# 1, 4, 9, 16, 25
```
</details>

---

## Les fonctions : def, return, arguments

Une **fonction** est un **bloc de code réutilisable** auquel on donne un nom. Tu l'écris **une fois**, tu l'appelles autant de fois que tu veux. Tu en as déjà utilisé : `print()`, `len()`, `sum()` sont des fonctions toutes prêtes.

### Définir sa propre fonction

On la **définit** avec `def`, on lui donne un **nom**, des **arguments** (les entrées entre parenthèses), et on renvoie un résultat avec `return`.

```python
def carre(x):          # def = "je définis" une fonction nommée carre, qui prend un argument x
    resultat = x * x
    return resultat    # return = "je renvoie" le résultat à celui qui appelle

# On APPELLE la fonction (on l'utilise) :
print(carre(5))    # 25
print(carre(10))   # 100
```

### Plusieurs arguments

```python
def moyenne(a, b):          # prend deux arguments
    return (a + b) / 2

print(moyenne(10, 20))      # 15.0
```

Un exemple plus « data » : calculer le chiffre d'affaires.

```python
def chiffre_affaires(quantite, prix_unitaire):
    """Renvoie le CA = quantité x prix unitaire."""   # ce texte décrit la fonction (docstring)
    return quantite * prix_unitaire

ca = chiffre_affaires(45, 12.50)
print(f"Chiffre d'affaires : {ca:.2f} euros")   # Chiffre d'affaires : 562.50 euros
```

> ⚠️ **`return` n'est pas `print`.** `print` **affiche** à l'écran (pour l'humain). `return` **renvoie** une valeur que ton programme pourra **réutiliser** (stocker, recalculer). Une fonction qui calcule devrait `return`, pas seulement `print`.

> 🎯 **Mini-exercice 7.** Écris une fonction `tva(prix_ht)` qui renvoie le prix TTC (TVA 20 %, donc `prix_ht * 1.20`). Appelle-la avec `100` et affiche le résultat avec une f-string.

<details>
<summary>✅ Correction</summary>

```python
def tva(prix_ht):
    return prix_ht * 1.20

prix_ttc = tva(100)
print(f"Prix TTC : {prix_ttc:.2f} euros")   # Prix TTC : 120.00 euros
```
</details>

---

## Les bibliothèques : import

Tu ne vas pas tout réécrire toi-même. D'autres ont déjà codé des outils puissants et les ont rangés dans des **bibliothèques** (aussi appelées **modules** ou **packages**). Pour t'en servir, tu les **importes**.

> 🧠 **Image mentale.** Une bibliothèque, c'est une **caisse à outils** prête à l'emploi. `import`, c'est ouvrir la caisse pour avoir le droit d'utiliser ses outils.

```python
import numpy as np      # on importe numpy, et on lui donne le SURNOM "np" (convention universelle)

notes = [12, 15, 9, 18, 11]
print(np.mean(notes))   # 13.0  -> mean() = moyenne, fournie par numpy
print(np.max(notes))    # 18
```

Le `as np` crée un **surnom** : au lieu d'écrire `numpy.mean(...)` à chaque fois, on écrit `np.mean(...)`. Ce sont des **conventions** que tu retrouveras partout :

| Bibliothèque | À quoi ça sert | Import conventionnel |
|---|---|---|
| `numpy` | calcul numérique rapide | `import numpy as np` |
| `pandas` | manipuler des tableaux de données | `import pandas as pd` |
| `matplotlib.pyplot` | faire des graphiques | `import matplotlib.pyplot as plt` |
| `seaborn` | graphiques statistiques jolis | `import seaborn as sns` |

> 💡 Ces quatre lignes d'import seront les **premières lignes** de presque tous tes notebooks de data analyst. Tu les connaîtras vite par cœur.

> 🎯 **Mini-exercice 8.** Importe `numpy as np`, crée la liste `temperatures = [18, 21, 25, 19, 22]`, et affiche sa **moyenne** et son **maximum** avec numpy.

<details>
<summary>✅ Correction</summary>

```python
import numpy as np

temperatures = [18, 21, 25, 19, 22]
print(np.mean(temperatures))   # 21.0
print(np.max(temperatures))    # 25
```
</details>

---

## Le pont vers pandas : ta première manipulation de données 🐼

Voici un **tout petit aperçu** de `pandas`, l'outil-roi du Data Analyst. **On ne fait que regarder** : tu approfondiras tout au module « analyse exploratoire (EDA) ». L'objectif ici est juste de **voir à quoi ça ressemble** pour ne pas être surpris.

`pandas` range les données dans un **DataFrame** : un **tableau** avec des lignes et des colonnes, comme dans Excel — mais piloté par du code.

```python
import pandas as pd     # convention : pandas s'importe en "pd"

# Lire un fichier CSV (un tableau de données) et le ranger dans un DataFrame :
df = pd.read_csv("ventes.csv")   # df est le nom qu'on donne très souvent à un DataFrame

# Regarder les 5 PREMIÈRES lignes pour découvrir le fichier :
df.head()
```

`df.head()` pourrait afficher quelque chose comme :

```
       date     ville  produit  quantite   prix
0  2024-01-02     Paris    Café        12   4.50
1  2024-01-02     Lyon     Thé          7   3.80
2  2024-01-03  Toulouse    Café        20   4.50
3  2024-01-03     Paris    Sucre        5   2.10
4  2024-01-04     Lyon     Café        15   4.50
```

Quelques commandes que tu utiliseras pour **découvrir un fichier inconnu** (juste pour info ici) :

```python
df.head()       # les 5 premières lignes
df.shape        # (nombre de lignes, nombre de colonnes)
df.columns      # la liste des noms de colonnes
df["ville"]     # une seule colonne (on l'appelle par son nom)
df.describe()   # statistiques automatiques (moyenne, min, max...) sur les colonnes numériques
```

> 🔗 **Tu vois le lien ?** Un DataFrame = un tableau. Chaque colonne ressemble à une **liste**, chaque ligne à un **dictionnaire** `{colonne: valeur}`. Tout ce que tu viens d'apprendre (variables, types, listes, dicos, fonctions, import) sert directement ici. **C'est exactement la porte d'entrée du module « analyse exploratoire (EDA) ».**

> ⚠️ Pas de panique si `read_csv` te renvoie une erreur « FileNotFoundError » quand tu testeras : ça veut juste dire que le fichier `ventes.csv` n'existe pas à l'endroit attendu. C'est normal, tu auras de vrais fichiers fournis au module « analyse exploratoire (EDA) ».

> 🎯 **Mini-exercice 9 (lecture).** Sans rien exécuter, réponds : dans `df.head()`, combien de lignes sont affichées par défaut ? Et que renvoie `df.shape` ?

<details>
<summary>✅ Correction</summary>

- `df.head()` affiche **5 lignes** par défaut (les 5 premières).
- `df.shape` renvoie un couple **(nombre de lignes, nombre de colonnes)**, par ex. `(250, 5)` = 250 lignes et 5 colonnes.
</details>

---

## Bonnes pratiques : lire une erreur, commenter

### Lire un message d'erreur (sans paniquer)

**Une erreur n'est pas un échec : c'est un message d'aide.** Python te dit où ça coince et pourquoi. Il faut juste apprendre à le lire — **toujours en partant du bas**.

```python
print(prix_inconnu)
```
```
NameError: name 'prix_inconnu' is not defined
```

Décryptage :
- **`NameError`** → le **type** d'erreur (ici : un nom n'existe pas).
- **`name 'prix_inconnu' is not defined`** → l'explication : la variable `prix_inconnu` n'a jamais été créée (faute de frappe ? oubli ?).

Les erreurs que tu croiseras le plus en débutant :

| Erreur | Ce que ça veut (souvent) dire | Réflexe |
|---|---|---|
| `SyntaxError` | une faute de « grammaire » (parenthèse, `:` ou guillemet manquant) | relis la ligne **et celle d'avant** |
| `NameError` | tu utilises une variable qui n'existe pas (faute de frappe ?) | vérifie l'orthographe exacte |
| `TypeError` | tu mélanges des types (ex. additionner du texte et un nombre) | vérifie les types avec `type()` |
| `IndentationError` | mauvais décalage (espaces) | aligne proprement le bloc |
| `KeyError` | tu demandes une clé qui n'existe pas dans un dictionnaire | vérifie le nom de la clé |
| `FileNotFoundError` | le fichier n'est pas là où tu l'as demandé | vérifie le chemin / le nom du fichier |

> 💡 **Réflexe gagnant.** Copie-colle le message d'erreur **exact** (entre guillemets) dans ton moteur de recherche, ou demande à une IA de te l'expliquer (sans jamais coller de données confidentielles — cf. le module « posture & méthode »). Tu n'es jamais le premier à tomber dessus.

### Commenter son code

Un **commentaire** commence par `#` : Python l'ignore, c'est pour les humains (toi dans deux semaines, ou un collègue). Bien commenter, c'est expliquer le **pourquoi**, pas paraphraser le code.

```python
tva = 0.20   # taux de TVA en vigueur (20 %)

# Mauvais commentaire (inutile, dit ce qu'on voit déjà) :
x = x + 1    # ajoute 1 à x

# Bon commentaire (explique l'intention) :
compteur_clients = compteur_clients + 1   # un client de plus a été traité
```

> 📌 **Règle d'or.** Du code bien nommé (`chiffre_affaires` plutôt que `ca2`) + quelques commentaires utiles = du code que tu comprendras encore dans 6 mois. C'est une **vraie compétence pro**, pas un détail.

---

## Vidéos d'auto-formation

> ⚠️ Quand l'URL exacte d'une vidéo n'a pas pu être vérifiée, le lien pointe vers une **chaîne**, une **playlist** ou une **recherche YouTube** : choisis l'épisode débutant le plus récent et le mieux noté.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| Apprendre le Python #1 — Les bases & prérequis | Graven | 🇫🇷 FR | ~15 min | https://www.youtube.com/watch?v=psaDHhZ0cPs | Premiers pas, `print`, installation/notebook — idéal grand débutant. |
| Apprendre le Python #2 — Les variables | Graven | 🇫🇷 FR | ~15 min | https://www.youtube.com/watch?v=nvyX8JfoOWY | Variables et types de base, affectation, affichage. |
| Apprendre le Python #3 — Les conditions | Graven | 🇫🇷 FR | ~15 min | https://www.youtube.com/watch?v=_AgUOsvMt8s | `if / elif / else`, comparaisons, indentation. |
| Apprendre le Python (playlist complète A→Z) | Graven | 🇫🇷 FR | série | https://www.youtube.com/playlist?list=PLwIeJQbjgLC6gIxxaPlnXiPlR9NDAhCay | Listes, boucles, fonctions… toute la base, dans l'ordre. |
| Python spécial Machine Learning (intro + numpy/pandas) | Machine Learnia | 🇫🇷 FR | série | https://www.youtube.com/playlist?list=PLO_fdPEVlfKqMDNmCFzQISI2H_nJcEDJq | Orientation **data** : numpy, pandas — fait le pont vers le module « analyse exploratoire (EDA) ». |
| Cours / exercices Python débutant | Docstring | 🇫🇷 FR | varié | https://www.youtube.com/@docstring_fr | Tutos courts et exercices corrigés pour consolider chaque notion. |

> 💡 **Conseil.** Ne regarde pas en mode « film ». **Mets en pause, recopie le code dans ton notebook, modifie une valeur, observe.** On apprend à coder en codant, pas en regardant.

---

## Quiz (5 QCM)

**Q1.** Quel type correspond à un nombre **à virgule** comme `19.99` ?
- a) `int`
- b) `str`
- c) `float`
- d) `bool`

**Q2.** Que signifie `==` en Python ?
- a) Ranger une valeur dans une variable (affectation)
- b) Tester si deux valeurs sont **égales** (comparaison)
- c) Additionner deux nombres
- d) Définir une fonction

**Q3.** Dans la liste `ventes = [120, 95, 200]`, que renvoie `ventes[0]` ?
- a) `200`
- b) `95`
- c) `120`
- d) Une erreur

**Q4.** À quoi sert le mot-clé `return` dans une fonction ?
- a) À afficher un message à l'écran
- b) À renvoyer un résultat réutilisable par le reste du programme
- c) À importer une bibliothèque
- d) À créer une boucle

**Q5.** Que veut probablement dire l'erreur `NameError: name 'prix' is not defined` ?
- a) Le fichier `prix` est introuvable
- b) La variable `prix` n'a jamais été créée (ou faute de frappe)
- c) `prix` n'est pas un nombre
- d) Il manque une parenthèse

### Réponses

| Question | Réponse | Justification |
|---|---|---|
| Q1 | **c) `float`** | Un nombre à virgule (avec un point décimal) est un `float`. |
| Q2 | **b)** | `==` compare (égalité). `=` (simple) range une valeur dans une variable. |
| Q3 | **c) `120`** | Les index commencent à **0** : `ventes[0]` est le premier élément. |
| Q4 | **b)** | `return` renvoie une valeur ; `print` se contente de l'afficher. |
| Q5 | **b)** | `NameError` = un nom inconnu : variable non créée ou mal orthographiée. |

---

## À retenir

- **Un programme = une liste d'instructions** exécutées de haut en bas. On code dans un **notebook**, cellule par cellule (Maj + Entrée).
- **Variable = boîte étiquetée** ; `=` range une valeur. **4 types de base** : `int`, `float` (point décimal !), `str` (texte entre guillemets), `bool` (`True`/`False`).
- **Affiche proprement avec les f-strings** : `f"Total : {x:.2f} €"`.
- **Listes** `[ ]` (par position, index dès **0**) et **dictionnaires** `{ }` (par clé) = les deux façons de stocker plusieurs valeurs. Un DataFrame, c'est un mélange des deux.
- **Conditions** `if / elif / else` (n'oublie pas le `:` et l'**indentation**). **Boucle `for`** = répéter pour chaque élément.
- **Fonction** : `def nom(arguments): ... return resultat`. `return` ≠ `print`.
- **`import ... as ...`** charge une **bibliothèque** (`numpy as np`, `pandas as pd`) : la caisse à outils de la data.
- **pandas** range les données dans un **DataFrame** ; `read_csv` + `.head()` = ta porte d'entrée vers le **module « analyse exploratoire (EDA) »**.
- **Une erreur est un message d'aide** : lis-la du bas vers le haut. **Commente le pourquoi**, nomme bien tes variables.

> 🚀 **Tu as posé les fondations.** Tu n'as pas besoin de tout maîtriser : tu as besoin de **reconnaître** ces briques quand elles réapparaîtront. À partir d'ici, le code des modules de Maths puis de pandas ne sera plus du chinois — ce seront des assemblages de ce que tu viens de voir. Bravo, le plus dur (oser commencer) est fait.
