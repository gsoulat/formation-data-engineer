# Chapitre 20 : Naive Bayes — Classer avec des Probabilités

## 🎯 Objectifs

- Comprendre le théorème de Bayes avec une intuition simple, sans peur des probabilités
- Saisir pourquoi l'hypothèse d'indépendance (le fameux « naïf ») rend l'algorithme utilisable en pratique
- Distinguer les trois variantes GaussianNB, MultinomialNB et BernoulliNB et savoir laquelle choisir
- Appliquer Naive Bayes à la classification de texte (le cas d'usage historique : le spam)
- Comprendre pourquoi Naive Bayes est aussi rapide, en entraînement comme en prédiction
- Connaître ses forces, ses faiblesses et les pièges classiques (probabilité nulle, features corrélées)

**Phase 4 — Algorithmes probabilistes**

---

## 1. 🧩 Le problème avant la solution

Imaginez que vous êtes une boîte mail. Chaque seconde, des dizaines de milliers de messages arrivent. Pour **chacun**, il faut décider en une fraction de milliseconde : *spam* ou *légitime* ?

```
Message reçu :
"FÉLICITATIONS !!! Vous avez GAGNÉ 1 000 000 € — cliquez ICI maintenant"

Question : spam ou pas spam ?
```

Un humain répond instantanément « spam, évidemment ». Mais **sur quoi** repose cette intuition ? Sur des indices accumulés : le mot « GAGNÉ », les majuscules, « cliquez ICI », le montant énorme. Chacun de ces mots est *plus fréquent* dans les spams que dans les vrais messages.

Naive Bayes formalise exactement cette intuition : **compter à quel point chaque indice penche vers une classe**, puis combiner tous les indices pour décider.

### 1.1 Pourquoi pas un modèle linéaire ou KNN ?

| Contrainte du problème | Régression logistique | KNN | Naive Bayes |
|------------------------|-----------------------|-----|-------------|
| **Des milliers de features** (un mot = une feature) | Lente à entraîner | Curse of dimensionality | Très à l'aise |
| **Entraînement sur des millions de mails** | Itératif, coûteux | Stocke tout | Un seul passage de comptage |
| **Prédiction en temps réel** | Rapide | Lente | Ultra-rapide |
| **Peu de données étiquetées** | Sur-apprend vite | Peu fiable | Reste robuste |

Naive Bayes n'est presque jamais le modèle le plus **précis**. Mais il est souvent le meilleur compromis **rapidité / simplicité / robustesse**, et c'est un excellent point de départ (baseline) pour tout problème de classification, surtout textuelle.

> 💡 **Conseil** : « Avant de sortir un gros modèle, entraînez un Naive Bayes en 3 lignes. Si votre modèle sophistiqué ne bat pas cette baseline, c'est qu'il y a un problème. »

---

## 2. 🧠 Le théorème de Bayes, expliqué simplement

### 2.1 L'intuition : mettre à jour une croyance

Le théorème de Bayes répond à une question du quotidien : **« Compte tenu de ce que je viens d'observer, que dois-je croire maintenant ? »**

```
AVANT d'ouvrir le mail :
   → 20 % des mails sont des spams (ma croyance de départ = "a priori")

J'observe le mot "GAGNÉ" dans le mail :
   → ce mot apparaît dans 80 % des spams, mais seulement 2 % des mails légitimes

APRÈS avoir vu "GAGNÉ" :
   → ma croyance se met à jour → il est maintenant TRÈS probable que ce soit un spam
```

C'est tout Bayes : partir d'une croyance de départ (l'*a priori*), observer une preuve, et **réviser** sa croyance en conséquence (l'*a posteriori*).

### 2.2 La formule, décortiquée

```
              P(preuve | classe) × P(classe)
P(classe | preuve) = ─────────────────────────────
                            P(preuve)

En français :
  P(classe | preuve)  = ce que je veux savoir (a posteriori)
                         "Proba que ce soit un SPAM sachant que j'ai vu 'GAGNÉ'"

  P(preuve | classe)  = la vraisemblance (likelihood)
                         "Proba de voir 'GAGNÉ' dans un SPAM" → facile à compter !

  P(classe)           = l'a priori (prior)
                         "Proportion de SPAMS en général" → facile à compter !

  P(preuve)           = l'évidence (constante de normalisation)
                         → identique pour toutes les classes, on peut l'ignorer
```

Le point crucial : les deux ingrédients de droite — `P(preuve | classe)` et `P(classe)` — se calculent **par simple comptage** dans les données d'entraînement. Pas de descente de gradient, pas d'itérations : on compte, on divise, c'est fini.

### 2.3 Un exemple chiffré à la main

Reprenons le mot « GAGNÉ » avec des chiffres concrets :

```
Données : 1000 mails, dont 200 spams et 800 légitimes

P(spam)            = 200 / 1000 = 0.20        (a priori)
P(legit)           = 800 / 1000 = 0.80

"GAGNÉ" apparaît dans 160 des 200 spams   → P(GAGNÉ | spam)  = 160/200 = 0.80
"GAGNÉ" apparaît dans  16 des 800 legit   → P(GAGNÉ | legit) = 16/800  = 0.02

Score spam  ∝ P(GAGNÉ | spam)  × P(spam)  = 0.80 × 0.20 = 0.160
Score legit ∝ P(GAGNÉ | legit) × P(legit) = 0.02 × 0.80 = 0.016

Score spam (0.160) >> Score legit (0.016)  → PRÉDICTION : SPAM

Probabilité normalisée de spam = 0.160 / (0.160 + 0.016) = 0.909 → 91 %
```

On n'a même pas eu besoin de calculer `P(GAGNÉ)` : comme elle est identique pour les deux scores, elle se simplifie dans la comparaison. On garde seulement le **numérateur** et on compare.

> 💡 **Conseil** : « Pour classer, on n'a pas besoin de la vraie probabilité, seulement de savoir **quelle classe a le plus gros score**. C'est pourquoi Naive Bayes ignore le dénominateur P(preuve) : c'est le secret de sa simplicité. »

---

## 3. 🎲 L'hypothèse « naïve » d'indépendance

### 3.1 Le problème : plusieurs indices à la fois

Un mail n'a pas un seul mot. Il en a des centaines. Comment combiner « GAGNÉ » **et** « cliquez » **et** « gratuit » ?

En théorie, il faudrait connaître `P(GAGNÉ ET cliquez ET gratuit | spam)`, c'est-à-dire la probabilité de voir cette **combinaison exacte** de mots. Mais le nombre de combinaisons possibles explose :

```
Avec 10 000 mots de vocabulaire, le nombre de combinaisons de mots possibles
dépasse le nombre d'atomes dans l'univers observable.

→ Impossible de compter chaque combinaison dans les données.
→ Il faudrait des milliards de milliards d'exemples.
```

### 3.2 La solution naïve : faire semblant que les mots sont indépendants

L'astuce de Naive Bayes — et c'est de là que vient le mot « naïf » — est de **supposer que chaque mot est indépendant des autres**, une fois la classe connue. On casse alors la probabilité conjointe en un simple produit :

```
Hypothèse d'indépendance conditionnelle :

P(GAGNÉ ET cliquez ET gratuit | spam)
   ≈ P(GAGNÉ | spam) × P(cliquez | spam) × P(gratuit | spam)

On multiplie simplement les vraisemblances de chaque mot, une par une.
```

Visuellement, on passe d'un enchevêtrement à une structure en étoile :

```
   RÉALITÉ (mots corrélés)          HYPOTHÈSE NAÏVE (mots indépendants)

     mot1 ─── mot2                        classe
       │  ╲   ╱  │                       ╱  │  ╲  ╲
       │   ╲ ╱   │                      ╱   │   ╲  ╲
     mot4 ─ ╳ ─ mot3                  mot1 mot2 mot3 mot4
       │   ╱ ╲   │                    (chacun ne dépend QUE de la classe,
     classe        pas les uns des autres)
```

### 3.3 Est-ce vrai ? Non. Est-ce grave ? Rarement.

L'hypothèse est **presque toujours fausse** : dans un vrai texte, « New » et « York » ne sont clairement pas indépendants. Pourtant, Naive Bayes fonctionne étonnamment bien. Pourquoi ?

```
Ce qui compte pour CLASSER, c'est de savoir quelle classe a le plus gros score,
pas d'estimer la probabilité EXACTE.

Même si les probabilités sont biaisées (à cause des mots corrélés comptés
plusieurs fois), le CLASSEMENT des classes reste souvent correct.

→ Naive Bayes se trompe sur les probabilités, mais souvent pas sur la décision.
```

> ⚠️ **Attention** : « À cause de l'indépendance supposée, les probabilités de `predict_proba()` sont souvent trop extrêmes (0.9999 ou 0.0001). Ne les prenez PAS pour argent comptant. Utilisez-les pour **classer**, pas pour estimer un vrai niveau de confiance. »

---

## 4. 🔢 Le problème du produit de petits nombres (log)

### 4.1 Le piège numérique

Multiplier des centaines de probabilités (toutes entre 0 et 1) donne un nombre **minuscule** :

```
0.02 × 0.01 × 0.05 × ... (300 fois) ≈ 10^(-450)

Un ordinateur en float64 arrondit tout nombre < 10^(-308) à ZÉRO.
→ underflow : on perd toute l'information, tous les scores deviennent 0.
```

### 4.2 La solution : travailler avec les logarithmes

On applique le logarithme, qui transforme le **produit** en **somme** (et un tout petit nombre en un nombre négatif gérable) :

```
log(a × b × c) = log(a) + log(b) + log(c)

Score(classe) = log P(classe) + Σ log P(mot_i | classe)
                                 i

→ Addition de nombres raisonnables (ex : -3.9 - 4.6 - 3.0 ...)
→ Le classement est préservé (log est croissant : si A > B alors log A > log B)
```

C'est exactement ce que fait scikit-learn en interne (`_joint_log_likelihood`). Vous n'avez rien à coder, mais c'est bon de savoir pourquoi les modèles Naive Bayes exposent une méthode `predict_log_proba()`.

---

## 5. 🧪 Les trois variantes : Gaussian, Multinomial, Bernoulli

Le principe de Bayes est toujours le même. Ce qui change d'une variante à l'autre, c'est **la façon de calculer `P(feature | classe)`** — la vraisemblance — selon le **type de features**.

| Variante | Type de features | Question posée | Exemple |
|----------|------------------|----------------|---------|
| **GaussianNB** | Continues (nombres réels) | « Quelle est la densité de cette valeur ? » | Longueur d'un pétale, taux de glucose |
| **MultinomialNB** | Comptages (entiers ≥ 0) | « Combien de fois apparaît ce mot ? » | Fréquences de mots (bag-of-words, TF-IDF) |
| **BernoulliNB** | Binaires (0 / 1) | « Ce mot est-il présent, oui ou non ? » | Présence/absence de mots, features on/off |

### 5.1 GaussianNB — features continues

Pour une feature continue (une longueur, une température), on ne peut pas « compter » la probabilité d'une valeur exacte. On suppose donc que, **dans chaque classe**, la feature suit une **loi normale** (une cloche gaussienne). On estime juste sa moyenne et son écart-type par classe.

```
Feature "longueur du pétale" pour l'iris :

  densité
    |        Setosa        Versicolor      Virginica
    |         /\              /\              /\
    |        /  \            /  \            /  \
    |       /    \          /    \          /    \
    |______/______\________/______\________/______\____→ longueur (cm)
          1.5              4.3             5.5

Pour une nouvelle fleur avec pétale = 5.0 cm :
  → densité la plus haute sous la cloche "Virginica" → penche vers Virginica
```

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report

# --- Dataset réel : Iris (150 fleurs, 4 mesures continues, 3 espèces) ---
iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# --- Entraînement (instantané : juste des moyennes et écarts-types) ---
gnb = GaussianNB()
gnb.fit(X_train, y_train)

# --- Ce que le modèle a "appris" : moyenne de chaque feature par classe ---
import numpy as np
print("=== Moyennes apprises (theta_) par classe et par feature ===")
print(np.round(gnb.theta_, 2))
print("\nClasses :", iris.target_names)

# --- Évaluation ---
y_pred = gnb.predict(X_test)
print("\n=== Rapport de classification (Iris) ===")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

> 💡 **Conseil** : « GaussianNB suppose que chaque feature est à peu près en cloche. Si une feature est très asymétrique (revenu, prix), pensez à la transformer (log) avant, sinon la gaussienne colle mal. »

### 5.2 MultinomialNB — comptages (le roi du texte)

Pour du texte transformé en **comptages de mots** (combien de fois chaque mot apparaît), on utilise MultinomialNB. C'est LA variante par défaut pour la classification de documents.

```
Document transformé en "bag-of-words" (sac de mots) :

"gratuit gagnez gratuit maintenant"  →  {gratuit: 2, gagnez: 1, maintenant: 1}

MultinomialNB apprend, pour chaque classe :
  P(mot | classe) = (nb de fois où le mot apparaît dans la classe + α)
                    ─────────────────────────────────────────────────
                    (total de tous les mots de la classe + α × |vocab|)

  α = lissage de Laplace (voir section 6) — évite les probabilités nulles
```

### 5.3 BernoulliNB — présence / absence

BernoulliNB ne regarde pas *combien de fois* un mot apparaît, mais seulement **s'il apparaît ou non** (0/1). Différence subtile mais importante : BernoulliNB **pénalise explicitement l'absence** d'un mot attendu, ce que MultinomialNB ne fait pas.

```
Même document, deux visions :

  MultinomialNB (comptage) : {gratuit: 2, gagnez: 1, ...}
  BernoulliNB  (présence)  : {gratuit: 1, gagnez: 1, argent: 0, réunion: 0, ...}
                                                     ▲ l'absence de "réunion" est une info !
```

BernoulliNB brille sur des **textes courts** (SMS, titres, tweets) où la présence d'un mot compte plus que sa fréquence.

### 5.4 Résumé : quelle variante pour quel type de données ?

```
Vos features sont... ?

  ├── des nombres réels continus (mesures)        → GaussianNB
  │
  ├── des comptages / fréquences (texte, TF-IDF)  → MultinomialNB
  │
  └── des indicateurs binaires 0/1 (présence)     → BernoulliNB
```

---

## 6. 📝 Cas d'usage phare : la classification de texte

C'est le terrain de jeu naturel de Naive Bayes. On va classer de vrais articles de forums Usenet à partir du dataset **20 Newsgroups** (fourni par scikit-learn).

### 6.1 De texte brut à features : le bag-of-words

Un modèle ne comprend pas les mots, seulement des nombres. On transforme donc chaque document en un vecteur de comptages :

```
Corpus :
  Doc 1 : "le chat mange"
  Doc 2 : "le chien mange le chat"

Vocabulaire (colonnes) : [chat, chien, le, mange]

Matrice bag-of-words (lignes = documents) :
        chat  chien  le  mange
  Doc 1   1     0     1    1
  Doc 2   1     1     2    1

→ Chaque colonne (mot) devient une feature. Voilà nos milliers de features.
```

### 6.2 Le problème de la probabilité nulle et le lissage de Laplace

Que se passe-t-il si un mot n'a **jamais** été vu dans une classe pendant l'entraînement ?

```
Le mot "hockey" n'apparaît JAMAIS dans les mails de la classe "medecine".

P(hockey | medecine) = 0 / total = 0

Score(medecine) = P(...) × P(...) × 0 × P(...) = 0   ← TOUT est annulé !

→ Un seul mot inconnu suffit à mettre le score à zéro. Catastrophe.
```

La solution est le **lissage de Laplace** (paramètre `alpha`) : on fait comme si chaque mot avait été vu `alpha` fois de plus. Aucune probabilité ne peut plus être nulle.

```
Sans lissage :  P(hockey | medecine) = 0 / 5000          = 0
Avec alpha=1 :  P(hockey | medecine) = (0 + 1) / (5000 + |vocab|) = tout petit, mais > 0

→ Le mot inconnu affaiblit le score sans l'anéantir.
```

> ⚠️ **Attention** : « Ne mettez JAMAIS `alpha=0` en production. Un seul mot du jeu de test absent de l'entraînement suffirait à casser toute la prédiction. La valeur par défaut `alpha=1.0` (lissage de Laplace) est un bon point de départ. »

### 6.3 Code complet : classifier des articles avec MultinomialNB

```python
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# --- Dataset réel : 20 Newsgroups (on prend 4 catégories pour aller vite) ---
categories = ['sci.med', 'rec.sport.hockey', 'comp.graphics', 'soc.religion.christian']

train = fetch_20newsgroups(subset='train', categories=categories,
                           remove=('headers', 'footers', 'quotes'), random_state=42)
test = fetch_20newsgroups(subset='test', categories=categories,
                          remove=('headers', 'footers', 'quotes'), random_state=42)

print(f"Documents d'entraînement : {len(train.data)}")
print(f"Documents de test        : {len(test.data)}")
print(f"Catégories               : {train.target_names}")

# --- Pipeline : texte → comptages → Naive Bayes ---
model = Pipeline([
    ('vectorizer', CountVectorizer(stop_words='english', min_df=2)),
    ('classifier', MultinomialNB(alpha=1.0)),  # alpha = lissage de Laplace
])

# --- Entraînement (rapide même sur des milliers de documents) ---
model.fit(train.data, train.target)

# --- Évaluation ---
y_pred = model.predict(test.data)
print("\n=== Rapport de classification (20 Newsgroups) ===")
print(classification_report(test.target, y_pred, target_names=test.target_names))

# --- Tester sur des phrases inventées ---
exemples = [
    "The goalie made an incredible save in the third period of the game",
    "The patient was prescribed antibiotics to treat the infection",
    "I rendered the 3D model using ray tracing and OpenGL shaders",
]
predictions = model.predict(exemples)
for phrase, pred in zip(exemples, predictions):
    print(f"\n'{phrase[:55]}...'\n   → {train.target_names[pred]}")
```

Exécution mentale attendue : la première phrase (goalie, save, period, game) tombe sur `rec.sport.hockey`, la deuxième (patient, antibiotics, infection) sur `sci.med`, la troisième (3D, ray tracing, OpenGL) sur `comp.graphics`. Le rapport de classification affiche typiquement un f1-score global autour de 0.85–0.90 sur ces 4 catégories bien séparées.

### 6.4 CountVectorizer vs TfidfVectorizer

```python
# Variante avec TF-IDF : pondère les mots rares (souvent plus discriminants)
model_tfidf = Pipeline([
    ('vectorizer', TfidfVectorizer(stop_words='english', min_df=2)),
    ('classifier', MultinomialNB(alpha=0.1)),
])
model_tfidf.fit(train.data, train.target)
y_pred_tfidf = model_tfidf.predict(test.data)

from sklearn.metrics import accuracy_score
print(f"Accuracy CountVectorizer : {accuracy_score(test.target, y_pred):.4f}")
print(f"Accuracy TfidfVectorizer : {accuracy_score(test.target, y_pred_tfidf):.4f}")
```

> 💡 **Conseil** : « Sur du texte, TF-IDF donne souvent un petit gain par rapport aux comptages bruts, car il diminue le poids des mots ultra-fréquents. Testez les deux — ça coûte trois lignes de code. »

### 6.5 Les mots les plus révélateurs de chaque classe

Naive Bayes est **interprétable** : on peut lire directement quels mots poussent le plus vers chaque catégorie.

```python
# Réentraîner sans pipeline pour accéder aux composants
vectorizer = CountVectorizer(stop_words='english', min_df=2)
X_train_counts = vectorizer.fit_transform(train.data)
clf = MultinomialNB(alpha=1.0).fit(X_train_counts, train.target)

feature_names = np.array(vectorizer.get_feature_names_out())

print("=== Top 10 des mots par catégorie ===")
for i, categorie in enumerate(train.target_names):
    # feature_log_prob_ : log P(mot | classe), une ligne par classe
    top10 = np.argsort(clf.feature_log_prob_[i])[-10:]
    print(f"\n{categorie} :")
    print("  ", ", ".join(feature_names[top10]))
```

---

## 7. ⚡ Pourquoi Naive Bayes est-il si rapide ?

### 7.1 Entraînement = un seul passage de comptage

Contrairement à la régression logistique (itérative, descente de gradient) ou au SVM (optimisation quadratique), Naive Bayes n'optimise **rien**. Il lui suffit de parcourir les données **une seule fois** pour compter.

```
┌─────────────────────────────────────────────────────────────────┐
│                      NAIVE BAYES — .fit(X, y)                    │
├─────────────────────────────────────────────────────────────────┤
│  → Pour chaque classe : compter les occurrences (ou moyenne/std) │
│  → Un SEUL passage sur les données                               │
│  → Aucune itération, aucune convergence à attendre               │
│  → Complexité : O(n × d)  (n échantillons, d features)           │
│  → Stocke : class_log_prior_, feature_log_prob_ (ou theta_/var_) │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Prédiction = additions de logs

```
┌─────────────────────────────────────────────────────────────────┐
│                    NAIVE BAYES — .predict(X)                     │
├─────────────────────────────────────────────────────────────────┤
│  → Pour chaque classe : additionner les log-probabilités         │
│      score(c) = log P(c) + Σ log P(feature_i | c)                │
│  → Choisir la classe au plus gros score                          │
│  → Que des additions → extrêmement rapide                        │
│  → Complexité : O(nb_classes × d) par prédiction                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Démonstration : Naive Bayes vs Régression Logistique

```python
import time
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

cats = ['sci.med', 'rec.sport.hockey', 'comp.graphics', 'soc.religion.christian']
train = fetch_20newsgroups(subset='train', categories=cats,
                           remove=('headers', 'footers', 'quotes'), random_state=42)
test = fetch_20newsgroups(subset='test', categories=cats,
                          remove=('headers', 'footers', 'quotes'), random_state=42)

vec = TfidfVectorizer(stop_words='english', min_df=2)
X_train = vec.fit_transform(train.data)
X_test = vec.transform(test.data)

modeles = {
    'MultinomialNB': MultinomialNB(alpha=0.1),
    'LogisticRegression': LogisticRegression(max_iter=1000),
}

print("=== Vitesse d'entraînement vs performance ===\n")
for nom, modele in modeles.items():
    start = time.time()
    modele.fit(X_train, train.target)
    duree = time.time() - start
    acc = accuracy_score(test.target, modele.predict(X_test))
    print(f"{nom:>20} : fit={duree*1000:6.1f} ms | accuracy={acc:.4f}")
```

Résultat attendu : Naive Bayes s'entraîne typiquement **10 à 50 fois plus vite** que la régression logistique, pour une accuracy très proche (souvent à 1–2 points près). C'est ce rapport rapidité/performance qui en fait la baseline idéale.

---

## 8. ⚠️ Pièges et « quand l'utiliser »

### 8.1 Les pièges classiques

| Piège | Symptôme | Remède |
|-------|----------|--------|
| **Probabilité nulle** | Un mot inconnu met tout le score à 0 | Lissage (`alpha ≥ 1`), jamais `alpha=0` |
| **Features corrélées** | Un signal compté 2× → proba trop extrême | Retirer les doublons ; ne pas croire `predict_proba` |
| **`predict_proba` surconfiant** | Probabilités à 0.9999 systématiques | Calibrer (`CalibratedClassifierCV`) si besoin de vraies probas |
| **Mauvaise variante** | Texte passé à GaussianNB → mauvais scores | Multinomial/Bernoulli pour du texte, Gaussian pour du continu |
| **Valeurs négatives dans MultinomialNB** | Erreur `Negative values in data` | MultinomialNB exige des features ≥ 0 (pas de StandardScaler !) |
| **Classes déséquilibrées** | Tout classé dans la classe majoritaire | Ajuster `class_prior` ou rééchantillonner |

> ⚠️ **Attention** : « Ne standardisez PAS (StandardScaler) les données avant un MultinomialNB : il attend des comptages positifs. Le scaling est inutile pour Naive Bayes en général, car chaque feature est traitée indépendamment. »

### 8.2 Forces et faiblesses

| ✅ Forces | ❌ Faiblesses |
|-----------|---------------|
| Extrêmement rapide (fit et predict) | Hypothèse d'indépendance irréaliste |
| Excellent avec beaucoup de features (texte) | Probabilités mal calibrées (trop extrêmes) |
| Marche avec peu de données d'entraînement | Ne capte pas les interactions entre features |
| Robuste aux features non pertinentes | GaussianNB suppose des features en cloche |
| Interprétable (log-probabilités par mot) | Souvent dépassé en précision par des modèles plus lourds |
| Incrémental possible (`partial_fit`) | Sensible aux features fortement corrélées |

### 8.3 L'arbre de décision : « dois-je utiliser Naive Bayes ? »

```
Mon problème est-il une CLASSIFICATION ?
   │
   ├── NON → Naive Bayes n'est pas fait pour ça (c'est un classifieur)
   │
   └── OUI
        │
        ├── Beaucoup de features / du texte ?     → OUI, excellent choix
        │
        ├── Besoin d'une baseline rapide en 3 lignes ?  → OUI, idéal
        │
        ├── Peu de données étiquetées ?           → OUI, plus robuste que la régression logistique
        │
        ├── Besoin de VRAIES probabilités calibrées ?   → NON, ou calibrer après
        │
        └── Features fortement corrélées / interactions clés ?  → NON, préférer arbres/boosting
```

> 💡 **Conseil** : « Naive Bayes est rarement le modèle final, mais presque toujours le bon **premier** modèle. Il vous donne en quelques secondes un plancher de performance et un point de comparaison honnête. »

---

## 9. 🧮 Comparaison des trois variantes en pratique

```python
import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.preprocessing import Binarizer

# --- Dataset réel : Breast Cancer Wisconsin (features continues) ---
data = load_breast_cancer()
X, y = data.data, data.target

# GaussianNB : adapté aux features continues → devrait être le meilleur ici
gnb_score = cross_val_score(GaussianNB(), X, y, cv=5, scoring='accuracy').mean()

# MultinomialNB : exige des valeurs >= 0 (ici les features le sont déjà)
mnb_score = cross_val_score(MultinomialNB(), X, y, cv=5, scoring='accuracy').mean()

# BernoulliNB : binarise autour d'un seuil → perd de l'information sur du continu
bnb_score = cross_val_score(BernoulliNB(binarize=np.median(X)), X, y,
                            cv=5, scoring='accuracy').mean()

print("=== Breast Cancer (features continues) — accuracy CV ===")
print(f"  GaussianNB    : {gnb_score:.4f}   ← attendu le meilleur (features continues)")
print(f"  MultinomialNB : {mnb_score:.4f}")
print(f"  BernoulliNB   : {bnb_score:.4f}")
```

> 💡 **Conseil** : « Sur ce dataset de mesures continues, GaussianNB domine largement les deux autres. La leçon : **choisir la variante en fonction du type de features** compte plus que n'importe quel réglage d'hyperparamètre. »

---

## 10. ⚙️ Ce que Naive Bayes stocke après .fit()

```python
from sklearn.datasets import load_iris
from sklearn.naive_bayes import GaussianNB
import numpy as np

iris = load_iris()
gnb = GaussianNB().fit(iris.data, iris.target)

print("GaussianNB stocke, par classe et par feature :")
print(f"  class_prior_ (a priori P(classe)) : {np.round(gnb.class_prior_, 3)}")
print(f"  theta_ (moyennes) shape           : {gnb.theta_.shape}")   # (3 classes, 4 features)
print(f"  var_   (variances) shape          : {gnb.var_.shape}")
print(f"\n  → Total paramètres : {gnb.theta_.size + gnb.var_.size + gnb.class_prior_.size}")
print("  → Aucune donnée brute conservée (contrairement à KNN) !")
```

À la différence de KNN (qui garde tout le dataset), Naive Bayes ne conserve que des **statistiques résumées** : quelques moyennes, variances et proportions. Le modèle final tient dans quelques kilo-octets, même après entraînement sur des millions de documents.

---

## 🎯 Points clés à retenir

1. **Le théorème de Bayes** met à jour une croyance : `P(classe | preuve) ∝ P(preuve | classe) × P(classe)`, et ces deux termes se calculent par **simple comptage**.
2. Pour classer, on **ignore le dénominateur** `P(preuve)` : on compare seulement les numérateurs (scores) entre classes.
3. Le **« naïf »** vient de l'hypothèse que les features sont **indépendantes** sachant la classe — fausse en pratique, mais souvent sans conséquence sur la décision.
4. On travaille en **logarithmes** (somme au lieu de produit) pour éviter l'underflow numérique.
5. **Trois variantes** selon le type de features : GaussianNB (continu), MultinomialNB (comptages / texte), BernoulliNB (binaire / présence).
6. Le **lissage de Laplace** (`alpha`) évite les probabilités nulles ; ne jamais mettre `alpha=0`.
7. Naive Bayes est **ultra-rapide** : un seul passage de comptage à l'entraînement, des additions à la prédiction.
8. Ses **probabilités sont mal calibrées** (trop extrêmes) : utilisez-les pour classer, pas comme vrai niveau de confiance.
9. C'est la **baseline idéale**, surtout pour le texte : quelques lignes, quelques secondes, un plancher de performance honnête.
10. **Ne pas standardiser** avant MultinomialNB (features ≥ 0 exigées) ; le scaling est de toute façon inutile pour Naive Bayes.

---

## ✅ Checklist de validation

- [ ] Je sais énoncer le théorème de Bayes et nommer a priori, vraisemblance, a posteriori
- [ ] Je comprends pourquoi on ignore le dénominateur `P(preuve)` pour classer
- [ ] Je sais expliquer l'hypothèse d'indépendance et pourquoi on l'appelle « naïve »
- [ ] Je comprends pourquoi elle fausse les probabilités mais rarement la décision
- [ ] Je sais pourquoi Naive Bayes travaille en logarithmes
- [ ] Je sais choisir entre GaussianNB, MultinomialNB et BernoulliNB selon le type de features
- [ ] Je sais transformer du texte en features avec CountVectorizer / TfidfVectorizer
- [ ] Je comprends le problème de la probabilité nulle et le rôle du lissage `alpha`
- [ ] Je sais entraîner un MultinomialNB sur du texte et lire les mots discriminants
- [ ] Je sais expliquer pourquoi Naive Bayes est si rapide (comptage + additions de logs)
- [ ] Je connais ses forces, ses faiblesses et les pièges (probas surconfiantes, pas de StandardScaler)

---

## 📚 Ressources

- **scikit-learn — Naive Bayes** : https://scikit-learn.org/stable/modules/naive_bayes.html
- **scikit-learn — Working with text data** : https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html
- **Dataset 20 Newsgroups** : https://scikit-learn.org/stable/datasets/real_world.html#newsgroups-dataset
- **CountVectorizer / TfidfVectorizer** : https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- **Article fondateur (spam)** — Sahami et al., *A Bayesian Approach to Filtering Junk E-Mail* (1998)

---

## 🧠 Mini-quiz

**1. Dans `P(classe | preuve) ∝ P(preuve | classe) × P(classe)`, comment appelle-t-on le terme `P(classe)` ?**
<details><summary>Réponse</summary>L'<strong>a priori</strong> (prior) : la croyance de départ, c'est-à-dire la proportion de chaque classe dans les données, avant même de regarder la preuve.</details>

**2. Pourquoi l'algorithme est-il qualifié de « naïf » ?**
<details><summary>Réponse</summary>Parce qu'il suppose que toutes les features sont <strong>indépendantes les unes des autres sachant la classe</strong>. Cette hypothèse est presque toujours fausse (les mots d'un texte sont corrélés), mais elle simplifie énormément le calcul et nuit rarement à la décision finale.</details>

**3. Vous classez des e-mails représentés par des comptages de mots (bag-of-words). Quelle variante choisir ?**
<details><summary>Réponse</summary><strong>MultinomialNB</strong>, la variante conçue pour des features de comptage (entiers ≥ 0). GaussianNB est pour du continu, BernoulliNB pour de la présence/absence binaire.</details>

**4. Que se passe-t-il si un mot du jeu de test n'a jamais été vu dans une classe à l'entraînement, sans lissage ?**
<details><summary>Réponse</summary>Sa vraisemblance `P(mot | classe)` vaut 0, ce qui annule <strong>tout le produit</strong> et met le score de la classe à zéro. Le <strong>lissage de Laplace</strong> (`alpha ≥ 1`) corrige ce problème en garantissant des probabilités strictement positives.</details>

**5. Pourquoi Naive Bayes calcule-t-il des sommes de logarithmes plutôt qu'un produit de probabilités ?**
<details><summary>Réponse</summary>Pour éviter l'<strong>underflow numérique</strong> : multiplier des centaines de probabilités entre 0 et 1 donne un nombre si petit qu'il est arrondi à zéro. Le log transforme le produit en somme et préserve le classement des classes.</details>

**6. Peut-on faire confiance à une probabilité de 0.9999 renvoyée par `predict_proba()` d'un Naive Bayes ?**
<details><summary>Réponse</summary>Non. À cause de l'hypothèse d'indépendance (features corrélées comptées plusieurs fois), les probabilités sont <strong>mal calibrées</strong> et souvent trop extrêmes. Elles sont fiables pour <strong>classer</strong>, mais pas pour estimer un vrai niveau de confiance. Si de vraies probabilités sont nécessaires, calibrer avec `CalibratedClassifierCV`.</details>

**7. Pourquoi Naive Bayes est-il beaucoup plus rapide à entraîner qu'une régression logistique ?**
<details><summary>Réponse</summary>Parce qu'il n'optimise rien : un <strong>seul passage de comptage</strong> sur les données suffit à estimer toutes les probabilités. La régression logistique, elle, est itérative (descente de gradient) et doit converger.</details>

---

*Ce cours fait partie de la formation Data Engineer — Module 08 Machine Learning.*
