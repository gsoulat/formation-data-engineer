# 04 — Probabilités

> **Formation** : Data Analyst — RNCP-38616 (Simplon)
> **Module** : 00 — Mathématiques pour la donnée
> **Public** : adultes en reconversion, remise à niveau
> **Compétences visées** : C5 (comprendre et décrire une distribution de données) — socle pour C7 (modélisation / machine learning)
> **Prérequis** : chapitre 3 (statistiques descriptives : moyenne, écart-type, histogramme)
> **Durée estimée** : 7 h — ✅ **Noyau essentiel ~4 h** (l'indispensable) + 🚀 **optionnel ~3 h** (Bayes, binomiale, théorème central limite). Tu peux valider le chapitre avec le noyau seul.

---

## 🎬 Accroche : bienvenue à la Ch'ti Boutique

> 🎬 **Le fil rouge du chapitre.** Tu viens d'être embauché·e comme Data Analyst à **la Ch'ti Boutique**, une petite enseigne du Nord qui vend en magasin et en ligne. Le patron, Gérard, t'arrête près de la machine à café :
> *« Dis donc, toi qui es bon en chiffres… Quand un client entre, quelles sont ses chances d'acheter ? Et sur mon dernier lot de 50 produits, combien seront défectueux ? Et ce nouveau détecteur de fraude "fiable à 99 %", je peux lui faire confiance ? »*
>
> 🎲 Bonne nouvelle : **toutes ces questions sont des probabilités**. Et la proba, c'est le chapitre le plus *jouable* des maths — on va l'apprendre avec des dés, des pièces, des cartes et des paris. À la fin, tu sauras répondre à Gérard. Et tu lui réserves une **surprise contre-intuitive** sur son détecteur de fraude… 😏

---

### De quoi parle ce chapitre ?

Les **statistiques descriptives** (chapitre 3) répondent à la question : *« qu'est-ce qui s'est passé dans mes données ? »* (moyenne, médiane, dispersion).

Les **probabilités** répondent à une question différente : *« qu'est-ce qui a des chances de se passer ? »*

Un Data Analyst utilise les probabilités tous les jours, souvent sans le dire :
- « Ce visiteur a **3 %** de chances d'acheter » → probabilité.
- « Les temps de réponse de l'API suivent une **courbe en cloche** » → loi normale.
- « Mon A/B test montre +2 % de conversion, mais est-ce du **hasard** ? » → on a besoin du raisonnement probabiliste (et du chapitre 5, l'inférence).

Ce chapitre te donne le langage et les outils pour **raisonner sous incertitude**.

> 🚀 **Parcours conseillé (ce chapitre est allégé pour toi).**
> Ce chapitre était dense (Bayes + binomiale + théorème central limite en 7 h, ouf). On l'a réorganisé en deux niveaux :
> - **✅ Noyau essentiel** : tout ce qui est indispensable pour la suite de la formation. Vise ça en priorité.
> - **🚀 Pour aller plus loin (optionnel)** : Bayes en profondeur, loi binomiale et démonstration du théorème central limite. Passionnant, mais tu peux y revenir plus tard sans bloquer la suite.
>
> **Si tu manques de temps : fais tout le ✅ Noyau, survole les 🚀 optionnels.** Rien n'est supprimé, juste rangé.

---

## Objectifs pédagogiques

À la fin de ce chapitre, tu sauras :

**✅ Le noyau essentiel (vise ça en priorité)**
1. Distinguer **fréquence observée** et **probabilité théorique**.
2. Décrire un **univers** et des **événements**, calculer des probabilités simples.
3. Manipuler **complémentaire, union, intersection**.
4. Comprendre l'**indépendance** et savoir repérer un piège d'analyse lié à une fausse indépendance.
5. Définir une **variable aléatoire** et calculer une **espérance**.
6. Maîtriser la **loi normale** : courbe en cloche, rôle de la moyenne et de l'écart-type, **règle 68-95-99,7**.

**🚀 Pour aller plus loin (optionnel, à ton rythme)**
7. Calculer une **probabilité conditionnelle** et démonter le **piège de Bayes**.
8. Reconnaître les **distributions discrètes** clés (uniforme, Bernoulli, binomiale).
9. Comprendre l'intuition du **théorème central limite**.

**Et partout** : implémenter tout cela en **Python** (`numpy`, `scipy.stats`, `matplotlib`) et par **simulation**.

---

## Pourquoi c'est utile au Data Analyst

| Notion de proba | Usage data concret |
|---|---|
| Probabilité simple | Taux de conversion attendu, taux de défaut produit, taux de churn |
| Événement complémentaire | « probabilité d'au moins une vente » = 1 − « aucune vente » |
| Union / intersection | Segmentation : clients « mobile **ET** abonnés newsletter » |
| Indépendance | Éviter le piège : croire que deux variables sont indépendantes alors qu'elles sont liées (corrélation cachée) |
| Probabilité conditionnelle / Bayes | Scoring, détection de fraude, filtres anti-spam, taux de vrais positifs d'un test |
| Variable aléatoire & espérance | Panier moyen espéré, valeur attendue d'une campagne, espérance de gain |
| Loi binomiale | Nombre de conversions sur N visiteurs, contrôle qualité (nb de défauts sur un lot) |
| **Loi normale** | Distribution des tailles, des temps de réponse, des montants ; base des intervalles de confiance et des z-scores (détection d'anomalies) |

> **À garder en tête** : en machine learning (C7), beaucoup de modèles produisent une **probabilité** (« 0,87 de chance que ce soit une fraude »). Comprendre ce chapitre, c'est comprendre la sortie de la moitié des modèles que tu rencontreras.

> 🎯 **Ça te servira pour…**
> - **Loi normale** → décrire la distribution des temps de réponse d'une API, des tailles, des montants ; repérer les **anomalies** (z-score) que ton patron veut traquer.
> - **Probabilité simple** → annoncer un **taux de conversion attendu** (« sur 1 000 visiteurs, attends-toi à ~30 ventes »).
> - **Bayes** → garder l'**intuition des faux positifs** : pourquoi un test « fiable à 99 % » peut crouler sous les fausses alertes. Le réflexe qui t'évitera des conclusions absurdes.

---

## Les notions

> 🎲 **Mode d'emploi ludique.** Chaque notion s'appuie sur un **jeu réel** (dé, pièce, cartes, tirage). Avant les révélations contre-intuitives, on te demandera de **parier** : note ta réponse mentalement, puis vérifie. C'est en se trompant qu'on retient ! Et n'oublie pas : pour toute proba, tu peux toujours **« simuler 10 000 fois et compter »** (méthode Monte-Carlo) — Python le fait en une ligne.

### ✅ Fréquence vs probabilité

> 🎲 **Le jeu de la pièce.** Lance une pièce 4 fois. Tu peux très bien tomber sur 3 « face » sur 4 (75 %). Pourtant la **vraie** proba de face est 50 %. Lance-la 1 000 fois : tu seras tout proche de 50 %. La **fréquence** (ce que tu observes) s'approche de la **probabilité** (la vraie valeur) quand tu répètes beaucoup. C'est toute la nuance de cette section.

**Définition.**
- La **fréquence** est ce qu'on **observe** : sur 1 000 visiteurs, 32 ont acheté → fréquence = 32/1000 = 3,2 %.
- La **probabilité** est ce qu'on **attend** à long terme, la « vraie » propension sous-jacente : par exemple un taux de conversion *réel* de 3 %.

La fréquence **estime** la probabilité. Plus l'échantillon est grand, plus la fréquence se rapproche de la probabilité (c'est la **loi des grands nombres**).

**Exemple métier chiffré.**
Lundi, 50 visiteurs, 3 achats → fréquence 6 %. Le mois entier, 20 000 visiteurs, 610 achats → fréquence 3,05 %. La vraie probabilité de conversion est sans doute proche de 3 %. Les 6 % du lundi étaient du **bruit** dû au petit échantillon.

**Erreur courante.** Tirer une conclusion d'un petit échantillon (« le lundi convertit mieux ! »). Avec 50 visiteurs, 3 achats au lieu de 1 ou 2, c'est juste le hasard.

**En Python — la fréquence converge vers la probabilité :**

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
proba_vraie = 0.03  # 3 % de conversion réelle

# On simule 20 000 visiteurs : 1 = achat, 0 = pas d'achat
visiteurs = rng.binomial(n=1, p=proba_vraie, size=20000)

# Fréquence cumulée au fil des visiteurs
freq_cumulee = np.cumsum(visiteurs) / np.arange(1, len(visiteurs) + 1)

plt.figure(figsize=(9, 4))
plt.plot(freq_cumulee, label="Fréquence observée")
plt.axhline(proba_vraie, color="red", linestyle="--", label="Probabilité vraie (3 %)")
plt.xlabel("Nombre de visiteurs")
plt.ylabel("Taux de conversion")
plt.title("La fréquence converge vers la probabilité")
plt.legend()
plt.show()
```

Tu verras la courbe bleue très instable au début (petit échantillon) puis se coller au pointillé rouge.

---

### ✅ Univers et événements

> 🎲 **Le jeu du dé.** Lance un dé à 6 faces. Tous les résultats possibles {1, 2, 3, 4, 5, 6}, c'est l'**univers**. « Faire un nombre pair » {2, 4, 6}, c'est un **événement** (une partie de l'univers). C'est tout le vocabulaire de cette section, rien de plus.

**Définition.**
- L'**univers** Ω (oméga) est l'ensemble de tous les résultats possibles d'une expérience.
- Un **événement** est un sous-ensemble de l'univers.

**Exemples.**
- Lancer un dé : Ω = {1, 2, 3, 4, 5, 6}. Événement « faire pair » = {2, 4, 6}.
- Un visiteur du site : Ω = {achète, n'achète pas}. Événement « achète » = {achète}.
- Une commande e-commerce : Ω = {payée, remboursée, abandonnée}.

**Vocabulaire utile :**
- Événement **certain** : tout l'univers (probabilité 1).
- Événement **impossible** : l'ensemble vide ∅ (probabilité 0).
- Événements **incompatibles** (ou disjoints) : ils ne peuvent pas se produire en même temps (ex : « payée » et « remboursée » sur une même ligne).

---

### ✅ Probabilités simples

> 🎲 **Le pari du dé.** Avant de lire : quelle est la proba de « faire pair » au dé ? Compte les cas qui t'arrangent (2, 4, 6 = 3 cas) sur les cas possibles (6 faces). 3/6 = 0,5. **Une proba simple, c'est juste : ce qui m'arrange ÷ tout ce qui peut arriver.** À condition que chaque résultat ait la même chance (un dé non pipé).

**Formule (cas d'équiprobabilité).**

$$P(A) = \frac{\text{nombre de cas favorables}}{\text{nombre de cas possibles}}$$

Propriétés fondamentales :
- $0 \le P(A) \le 1$
- $P(\Omega) = 1$ (quelque chose se produit forcément)
- $P(\emptyset) = 0$

**Calcul à la main.**
Dé équilibré, P(« faire pair ») = 3/6 = 0,5.
Un panier au hasard parmi 200 commandes, dont 14 ont été remboursées : P(remboursée) = 14/200 = 0,07 = 7 %.

**Exemple métier.** Sur une boutique du Nord, 200 ventes en magasin, 14 retours. La probabilité (estimée) qu'une vente donne lieu à un retour est 7 %.

**En Python :**

```python
commandes = 200
remboursees = 14
p_remboursement = remboursees / commandes
print(f"P(remboursement) = {p_remboursement:.2%}")  # 7.00 %
```

**Erreur courante.** Croire que tous les cas sont équiprobables. P(A) = favorables/possibles n'est valable **que si chaque résultat a la même chance**. Un dé pipé ou des visiteurs qui ne se valent pas → on doit estimer la proba par la fréquence, pas par un comptage théorique.

---

### ✅ Événement complémentaire

> 🎲 **L'astuce du « au moins un ».** Tu lances un dé 4 fois : quelle proba d'avoir **au moins un** 6 ? Calculer ça directement est pénible. Mais le **contraire** (« aucun 6 ») est facile. Et proba(au moins un) = 1 − proba(aucun). 🧠 **Mnémo : quand tu vois "au moins un", retourne le problème et calcule "aucun".**

**Définition.** Le complémentaire de A, noté $\bar{A}$ (ou $A^c$), est « A ne se produit pas ».

**Formule.**

$$P(\bar{A}) = 1 - P(A)$$

**Pourquoi c'est précieux.** Souvent, « au moins un » est pénible à calculer directement, mais « aucun » est facile.

**Exemple métier chiffré.**
Taux de conversion 3 %. Quelle est la probabilité d'avoir **au moins une vente** sur 100 visiteurs (en supposant les visiteurs indépendants) ?

- « Aucune vente » = chaque visiteur n'achète pas : $0{,}97^{100}$.
- Donc « au moins une vente » = $1 - 0{,}97^{100}$.

**Calcul à la main (ordre de grandeur).** $0{,}97^{100} \approx 0{,}048$, donc $P(\text{au moins une}) \approx 0{,}952 = 95{,}2\%$.

**En Python :**

```python
p = 0.03
n = 100
p_aucune = (1 - p) ** n
p_au_moins_une = 1 - p_aucune
print(f"P(au moins une vente sur {n}) = {p_au_moins_une:.2%}")  # ~95.2 %
```

---

### ✅ Union et intersection

> 🎲 **Le jeu des cartes.** Dans un jeu de 52 cartes, tu tires une carte. Proba qu'elle soit un **cœur OU une figure** ? Si tu additionnes bêtement (cœurs + figures), tu comptes le **valet de cœur** deux fois ! D'où la règle : on additionne, puis on **retire ce qui est compté deux fois** (l'intersection). C'est ça, l'union.

**Définitions.**
- **Intersection** $A \cap B$ : A **ET** B se produisent.
- **Union** $A \cup B$ : A **OU** B (ou les deux) se produit.

**Formule de l'union (toujours vraie) :**

$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$

On soustrait l'intersection pour ne pas la compter **deux fois**.

Si A et B sont **incompatibles** ($A \cap B = \emptyset$) :

$$P(A \cup B) = P(A) + P(B)$$

**Exemple métier chiffré.**
Sur les visiteurs d'un site :
- 60 % viennent sur **mobile** (M)
- 25 % sont **abonnés newsletter** (N)
- 18 % sont **mobile ET abonnés** ($M \cap N$)

Probabilité d'être mobile **OU** abonné :

$$P(M \cup N) = 0{,}60 + 0{,}25 - 0{,}18 = 0{,}67 = 67\%$$

**Calcul à la main.** 0,60 + 0,25 = 0,85, moins 0,18 → 0,67.

**En Python :**

```python
p_mobile = 0.60
p_news = 0.25
p_mobile_et_news = 0.18

p_union = p_mobile + p_news - p_mobile_et_news
print(f"P(mobile OU newsletter) = {p_union:.0%}")  # 67 %
```

**Erreur courante.** Additionner sans soustraire l'intersection → on dépasserait parfois 100 % (ici on aurait trouvé 85 %, faux).

---

### ✅ Indépendance

> 🎲 **Le jeu des deux pièces.** Tu lances deux pièces. La première tombe sur « face ». Est-ce que ça change la chance que la deuxième fasse « face » ? **Non** — les pièces ne se parlent pas. Ce sont des événements **indépendants**, et la proba des deux ensemble se **multiplie** (0,5 × 0,5 = 0,25). ⚠️ Le piège du métier : supposer cette indépendance alors qu'elle est fausse (la pluie et les ventes de parapluies, elles, se parlent !).

**Définition.** Deux événements A et B sont **indépendants** si la réalisation de l'un ne change rien à la probabilité de l'autre. Formellement :

$$P(A \cap B) = P(A) \times P(B)$$

**Exemple métier chiffré.**
Deux visiteurs distincts qui ne se connaissent pas : la conversion de l'un n'influence pas l'autre. P(les deux achètent) = 0,03 × 0,03 = 0,0009.

**Test rapide d'indépendance.** Reprenons mobile/newsletter :
- Si indépendants, on attendrait $P(M \cap N) = 0{,}60 \times 0{,}25 = 0{,}15$.
- Or on observe 0,18. **0,18 ≠ 0,15** → mobile et newsletter ne sont **pas** indépendants (être sur mobile augmente un peu la chance d'être abonné).

**Le piège d'analyse à connaître.** Beaucoup d'erreurs viennent de l'hypothèse d'indépendance posée à tort :
- Multiplier des probabilités d'événements en réalité **corrélés** (ex : « la pluie » et « les ventes de parapluies » ne sont pas indépendantes).
- Considérer que deux jours de visite d'un même utilisateur sont indépendants (le même utilisateur a des habitudes → corrélation).
- Le **paradoxe de Simpson** : une relation peut s'inverser selon qu'on regroupe ou non les données.

**En Python — vérifier l'indépendance sur des données :**

```python
import numpy as np

# Indépendance théorique attendue vs observée
p_m, p_n, p_mn_obs = 0.60, 0.25, 0.18
p_mn_attendu = p_m * p_n
print(f"P(M et N) attendu si indépendants = {p_mn_attendu:.2f}")
print(f"P(M et N) observé               = {p_mn_obs:.2f}")
print("Indépendants ?", np.isclose(p_mn_attendu, p_mn_obs))  # False
```

---

### 🚀 Probabilités conditionnelles & le piège de Bayes *(optionnel — pour aller plus loin)*

> 🚀 **Section optionnelle.** L'**intuition** de Bayes (« un test fiable peut quand même mentir quand la cible est rare ») est en or pour un Data Analyst. Mais la mécanique des conditionnelles est plus dense — si tu débutes, retiens surtout la **morale du pari ci-dessous** et reviens aux formules plus tard. Rien ici n'est requis pour la loi normale (✅) ni pour la suite immédiate.

---

> 🎲 **PARIE AVANT DE LIRE (ne triche pas !)**
>
> La Ch'ti Boutique installe un détecteur de fraude **fiable à 99 %**. Une commande vient d'être signalée « fraude ».
>
> **À ton avis, quelle est la probabilité qu'elle soit *vraiment* une fraude ?**
> Note ton pari : 99 % ? 90 % ? 50 % ?
>
> *(Garde ton chiffre en tête. La réponse va te surprendre — elle est plus bas, et elle est étonnamment basse. 😏)*

---

**Définition.** La probabilité de A **sachant que** B s'est produit, notée $P(A \mid B)$ :

$$P(A \mid B) = \frac{P(A \cap B)}{P(B)} \quad (\text{si } P(B) > 0)$$

On « réduit l'univers » à B et on regarde la part de A là-dedans.

**Exemple métier chiffré.**
Probabilité d'être abonné newsletter **sachant** qu'on est sur mobile :

$$P(N \mid M) = \frac{P(M \cap N)}{P(M)} = \frac{0{,}18}{0{,}60} = 0{,}30 = 30\%$$

Sur l'ensemble des visiteurs, 25 % sont abonnés ; mais **parmi les mobiles**, c'est 30 %. L'info « mobile » a changé la probabilité.

**Lien avec l'indépendance.** Si A et B sont indépendants, alors $P(A \mid B) = P(A)$ : savoir B n'apporte aucune information.

**Intuition de Bayes (sans la formule complète).**
Bayes répond à : *« je connais $P(B \mid A)$, mais je veux $P(A \mid B)$ »*. C'est le cœur de la **détection** (fraude, maladie, spam).

**🎲 LA RÉVÉLATION (compare à ton pari).**
Reprenons le détecteur de fraude de la Ch'ti Boutique :
- Une fraude touche **1 commande sur 1 000** (P(fraude) = 0,1 %).
- Un détecteur repère **99 %** des vraies fraudes (vrais positifs) et se trompe sur **5 %** des commandes saines (faux positifs).
- Une commande est signalée « fraude ». Quelle est la probabilité qu'elle soit **vraiment** une fraude ?

Imaginons **100 000 commandes** (compter sur de vraies têtes de clients, c'est plus parlant que des formules) :
- Fraudes réelles : 100 → 99 détectées.
- Saines : 99 900 → 5 % faussement signalées = 4 995 alertes.
- Total des alertes : 99 + 4 995 = 5 094.
- **Probabilité qu'une alerte soit une vraie fraude = 99 / 5 094 ≈ 1,9 %.**

> 🎉 **Alors, ton pari ?** Si tu avais misé 99 % ou 90 %, bienvenue au club : c'est l'erreur que font 9 personnes sur 10 (médecins inclus !). La vraie réponse est **~1,9 %**.
>
> Stupéfiant : malgré un détecteur « à 99 % », **98 % des alertes sont des fausses alertes**. Pourquoi ? Parce que la fraude est **rare**. Il y a tellement de commandes saines que même 5 % d'entre elles, faussement signalées, **écrasent** en nombre les vraies fraudes.
>
> 🧠 **C'est ça, l'intuition de Bayes** : la **rareté** de l'événement (la proba *a priori*) compte énormément. C'est exactement pourquoi tu dois te méfier des dépistages de masse, des filtres anti-spam trop zélés, et des modèles ML qui « détectent » un événement rare.

**🎲 Le réflexe Monte-Carlo (« simule 10 000 fois et compte »).**
Pas convaincu par le tableau ? Au lieu de raisonner, on peut **simuler** : on fabrique 100 000 fausses commandes au hasard, on les passe au détecteur, et on **compte** combien d'alertes sont de vraies fraudes. C'est ce que fait le code ci-dessous (version comptage), et tu peux le refaire en tirant chaque commande au hasard.

**En Python :**

```python
n = 100_000
taux_fraude = 0.001
sensibilite = 0.99   # P(alerte | fraude)
faux_positif = 0.05  # P(alerte | saine)

fraudes = n * taux_fraude            # 100
saines = n - fraudes                 # 99 900

vrais_positifs = fraudes * sensibilite       # 99
faux_positifs = saines * faux_positif        # 4 995
total_alertes = vrais_positifs + faux_positifs

p_fraude_sachant_alerte = vrais_positifs / total_alertes
print(f"P(vraie fraude | alerte) = {p_fraude_sachant_alerte:.1%}")  # ~1.9 %
```

**🎲 Version Monte-Carlo (« simule et compte ») — pour bien *sentir* le résultat :**

```python
import numpy as np
rng = np.random.default_rng(0)
n = 1_000_000

# 1) Chaque commande est-elle une vraie fraude ? (1 sur 1000)
est_fraude = rng.random(n) < 0.001
# 2) Le détecteur lève-t-il une alerte ?
#    - sur une fraude : alerte dans 99 % des cas
#    - sur une saine  : alerte dans 5 % des cas (faux positif)
p_alerte = np.where(est_fraude, 0.99, 0.05)
alerte = rng.random(n) < p_alerte

# 3) Parmi les commandes ALERTÉES, quelle part était vraiment frauduleuse ?
print(f"P(vraie fraude | alerte) ≈ {est_fraude[alerte].mean():.1%}")  # ~1.9 %
```

Aucune formule de Bayes ici : on **tire au hasard et on compte**. On retrouve ~1,9 %. C'est tout l'intérêt de Monte-Carlo : quand une proba te paraît contre-intuitive, simule-la.

**Erreur courante.** Confondre $P(\text{alerte} \mid \text{fraude})$ (99 %) avec $P(\text{fraude} \mid \text{alerte})$ (1,9 %). Ce sont deux choses totalement différentes — c'est la base du raisonnement de Bayes.

---

### ✅ Variables aléatoires et espérance

> 🎲 **Le jeu du casino (le pari à long terme).** À une roulette truquée, tu gagnes 0 € (70 % du temps), 30 € (25 %) ou 120 € (5 %). Si tu joues **mille fois**, combien gagnes-tu **en moyenne par partie** ? C'est l'**espérance** : chaque gain pondéré par sa chance. C'est LA notion business du chapitre : « combien me rapporte en moyenne un email, un client, une campagne ? »

**Définition.** Une **variable aléatoire** X associe un nombre à chaque résultat de l'expérience.
- Lancer un dé → X = la face obtenue (1 à 6).
- Une vente → X = le montant du panier en euros.
- Un visiteur → X = 1 s'il achète, 0 sinon.

**Espérance** $E[X]$ : la « moyenne attendue » à long terme, pondérée par les probabilités.

$$E[X] = \sum_i x_i \times P(X = x_i)$$

**Exemple métier chiffré — espérance d'une campagne.**
Un emailing : 70 % n'achètent rien (0 €), 25 % achètent un petit panier (30 €), 5 % un gros panier (120 €).

$$E[X] = 0{,}70 \times 0 + 0{,}25 \times 30 + 0{,}05 \times 120 = 0 + 7{,}5 + 6 = 13{,}5\ \text{€}$$

**Interprétation.** En moyenne, chaque email rapporte 13,50 €. Si l'email coûte moins que ça à envoyer, la campagne est rentable. C'est exactement le raisonnement « valeur attendue » utilisé en analyse business.

**En Python :**

```python
import numpy as np

valeurs = np.array([0, 30, 120])
probas  = np.array([0.70, 0.25, 0.05])

esperance = np.sum(valeurs * probas)
print(f"Espérance par email = {esperance:.2f} €")  # 13.50 €

# Vérification par simulation
rng = np.random.default_rng(0)
tirages = rng.choice(valeurs, size=1_000_000, p=probas)
print(f"Moyenne simulée     = {tirages.mean():.2f} €")  # ~13.5 €
```

---

### 🚀 Distributions discrètes : uniforme, Bernoulli, binomiale *(la binomiale est optionnelle)*

> 🚀 **Niveau.** Les deux premières (uniforme, Bernoulli) sont des **mots de vocabulaire** : tu les connais déjà sans le savoir (le dé, la pièce). Garde-les. La **loi binomiale** (calculer « combien de succès sur n essais ») est plus technique → **optionnelle**, à explorer quand tu seras à l'aise. Elle n'est pas requise pour la loi normale.

Une **distribution** décrit *quelles valeurs* prend une variable aléatoire et *avec quelle probabilité*.

#### a) Loi uniforme (discrète) — *« tout le monde a sa chance »*
🎲 C'est le **dé équilibré** ou le tirage au sort équitable : toutes les valeurs ont la même probabilité (chaque face 1/6).

#### b) Loi de Bernoulli — *« pile ou face, oui ou non »*
🎲 C'est **une seule épreuve à deux issues** : succès (1) avec probabilité p, échec (0) avec probabilité 1−p. Le lancer de pièce, ou « ce visiteur achète-t-il ? ».
> *Data* : « ce visiteur achète-t-il ? » p = 0,03. C'est la brique de base.
> Espérance : $E[X] = p$.

#### c) 🚀 Loi binomiale *(optionnel)* — *« combien de succès si je répète ? »*
🎲 On **répète n fois** une épreuve de Bernoulli indépendante (n lancers de pièce), et X compte le **nombre de succès** (de « face »).
> *Data* : « combien de conversions sur 100 visiteurs ? », « combien de produits défectueux dans un lot de 50 ? »

**Formule.**

$$P(X = k) = \binom{n}{k} \, p^k \, (1-p)^{n-k}$$

où $\binom{n}{k}$ (« k parmi n ») est le nombre de façons de choisir k succès parmi n.

Espérance : $E[X] = n \times p$.

**Exemple métier chiffré.** Contrôle qualité, retail Nord : un lot de 50 articles, taux de défaut 2 % (p = 0,02). Nombre **attendu** de défectueux : $E[X] = 50 \times 0{,}02 = 1$. Probabilité d'avoir **0** défectueux : $P(X=0) = 0{,}98^{50} \approx 0{,}364 = 36{,}4\%$.

**En Python :**

```python
from scipy.stats import binom
import numpy as np
import matplotlib.pyplot as plt

n, p = 50, 0.02

print("E[X] =", n * p)                         # 1.0 défectueux attendu
print("P(0 défaut) =", round(binom.pmf(0, n, p), 4))   # 0.3642
print("P(au moins 3 défauts) =", round(1 - binom.cdf(2, n, p), 4))

# Diagramme en bâtons de la loi binomiale
k = np.arange(0, 8)
plt.bar(k, binom.pmf(k, n, p))
plt.xlabel("Nombre de défectueux")
plt.ylabel("Probabilité")
plt.title("Loi binomiale n=50, p=0,02 (contrôle qualité)")
plt.show()
```

**Erreur courante.** Utiliser la binomiale quand les épreuves ne sont **pas indépendantes** ou que p change d'une épreuve à l'autre. La binomiale suppose n épreuves identiques et indépendantes.

---

### ✅ Distribution continue et LOI NORMALE ⭐ *(la star du chapitre)*

> ⭐ **La notion la plus importante de tout le chapitre.** Si tu ne devais retenir qu'une chose, ce serait celle-ci : la loi normale est partout en data, et c'est le socle des chapitres suivants. Lis cette section avec attention.

> 🧠 **Analogie : la sortie du cinéma.** Imagine la taille des gens qui sortent d'une salle. La plupart sont autour de la moyenne (1,70 m), **peu** sont très petits, **peu** sont très grands. Si tu les ranges du plus petit au plus grand et que tu comptes combien il y en a à chaque taille, tu dessines… une **cloche** : un gros tas au milieu, deux pentes qui descendent sur les côtés. **C'est ça, la loi normale.**
>
> 🧠 **Mnémo : « la courbe en cloche — la plupart au centre, peu aux extrêmes. »**

Quand une variable peut prendre des valeurs **continues** (un temps, une taille, un montant), on ne parle plus de P(X = valeur exacte) (qui vaut 0), mais de P(X dans un intervalle), via une **courbe de densité**. L'aire sous la courbe = la probabilité.

**La loi normale** (ou gaussienne, ou « courbe en cloche ») est LA distribution reine en data, parce qu'énormément de phénomènes naturels et de moyennes s'y conforment.

Elle est entièrement décrite par **2 paramètres** :
- la **moyenne μ** (mu) : le **centre** de la cloche (où est le sommet) ;
- l'**écart-type σ** (sigma) : la **largeur** de la cloche (à quel point les données sont étalées).

**Forme.** Symétrique autour de μ. Petit σ → cloche étroite et haute (données serrées) ; grand σ → cloche large et plate (données dispersées).

#### La règle 68-95-99,7 (à connaître par cœur)

> 🧠 **Mnémo : « presque tout le monde tient en 3 pas de chaque côté. »** Pars du centre (la moyenne) et fais des « pas » d'un écart-type :
> - **1 pas** de chaque côté → tu attrapes **68 %** des gens (les ⅔, la grosse foule du milieu).
> - **2 pas** → **95 %** (la quasi-totalité).
> - **3 pas** → **99,7 %** (tout le monde, ou presque). Au-delà de 3 pas, c'est un cas **rarissime** : une anomalie.

Pour une loi normale :
- **≈ 68 %** des valeurs sont dans **μ ± 1σ**
- **≈ 95 %** des valeurs sont dans **μ ± 2σ**
- **≈ 99,7 %** des valeurs sont dans **μ ± 3σ**

**Exemple métier chiffré — temps de réponse d'une API.**
Les temps de réponse suivent (à peu près) une loi normale de moyenne **μ = 200 ms** et d'écart-type **σ = 30 ms**.
- 68 % des requêtes répondent entre **170 et 230 ms** (200 ± 30).
- 95 % entre **140 et 260 ms** (200 ± 60).
- 99,7 % entre **110 et 290 ms** (200 ± 90).
- Une requête à **300 ms** est à plus de 3σ → **anomalie** très rare (< 0,15 % à droite). C'est exactement comme ça qu'on **détecte des outliers** : compter les écarts-types (le **z-score**).

**Le z-score.**

$$z = \frac{x - \mu}{\sigma}$$

« À combien d'écarts-types de la moyenne suis-je ? » Une requête à 300 ms : $z = (300 - 200)/30 \approx 3{,}33$ → au-delà de 3σ, suspecte.

**En Python — tracer la loi normale et appliquer la règle 68-95-99,7 :**

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

mu, sigma = 200, 30  # temps de réponse API en ms

x = np.linspace(mu - 4*sigma, mu + 4*sigma, 500)
y = norm.pdf(x, mu, sigma)  # densité

plt.figure(figsize=(10, 5))
plt.plot(x, y, color="black")

# Colorer les bandes 1σ / 2σ / 3σ
for k, alpha, label in [(1, 0.5, "68 %"), (2, 0.3, "95 %"), (3, 0.15, "99,7 %")]:
    plt.fill_between(x, y, where=(x >= mu - k*sigma) & (x <= mu + k*sigma),
                     alpha=alpha, label=f"±{k}σ ≈ {label}")

plt.axvline(mu, color="red", linestyle="--", label="moyenne μ")
plt.title("Loi normale des temps de réponse API (μ=200 ms, σ=30 ms)")
plt.xlabel("Temps de réponse (ms)")
plt.ylabel("Densité")
plt.legend()
plt.show()

# Vérifier numériquement la règle 68-95-99,7
for k in (1, 2, 3):
    proba = norm.cdf(mu + k*sigma, mu, sigma) - norm.cdf(mu - k*sigma, mu, sigma)
    print(f"P(μ ± {k}σ) = {proba:.4f}")   # 0.6827, 0.9545, 0.9973

# Probabilité qu'une requête dépasse 260 ms (lente)
p_lente = 1 - norm.cdf(260, mu, sigma)
print(f"P(temps > 260 ms) = {p_lente:.2%}")  # ~2.28 %

# z-score d'une requête à 300 ms
z = (300 - mu) / sigma
print(f"z-score de 300 ms = {z:.2f}")  # 3.33 → anomalie
```

#### 🚀 *Bonus optionnel* — pourquoi la cloche apparaît partout (théorème central limite)

> 🚀 **Section optionnelle (culture data).** Tu n'as pas besoin de la « démonstration » du théorème central limite (TCL) pour utiliser la loi normale. Mais l'intuition est belle et te resservira au chapitre 5. En une phrase : **dès qu'on fait des moyennes, une cloche apparaît — même si les données de départ ne sont pas du tout en cloche.**

**🎲 Simulation — la magie du TCL (« simule et regarde ») :**

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
# On prend une distribution PAS normale du tout (uniforme), puis on fait des moyennes
echantillons = rng.uniform(0, 1, size=(100_000, 30))  # 100k moyennes de 30 valeurs
moyennes = echantillons.mean(axis=1)

plt.hist(moyennes, bins=60, density=True, color="steelblue", edgecolor="white")
plt.title("Théorème central limite : la moyenne de 30 tirages uniformes → cloche")
plt.xlabel("Moyenne de l'échantillon")
plt.ylabel("Densité")
plt.show()
```

Même en partant d'une distribution plate, **les moyennes forment une cloche**. C'est pourquoi la loi normale est partout en data — et pourquoi le chapitre 5 (inférence) s'appuie dessus.

**Erreurs courantes.**
- Supposer que **toutes** les données sont normales. Beaucoup ne le sont pas (revenus, temps d'attente très étalés → souvent asymétriques). **Toujours tracer un histogramme avant.**
- Confondre densité et probabilité : sur une loi continue, la hauteur de la courbe n'est **pas** une probabilité ; seule l'**aire** en est une.
- Oublier que la règle 68-95-99,7 ne vaut **que** pour une loi normale.

---

## 🏆 Défi du chapitre — Le mini-casino de la Ch'ti Boutique

> Gérard veut animer son magasin avec un **jeu de grattage** pour les fêtes. La règle : le client paie **2 €** pour gratter, et il gagne selon ce tableau.
>
> | Résultat | Gain client | Probabilité |
> |---|---|---|
> | Rien | 0 € | 80 % |
> | Petit lot | 5 € | 18 % |
> | Gros lot | 50 € | 2 % |
>
> **🎲 Parie d'abord, calcule ensuite :**
> 1. À ton avis, à chaque grattage, est-ce **Gérard ou le client** qui gagne en moyenne ?
> 2. Calcule l'**espérance de gain du client** par grattage.
> 3. Sachant que le client paie 2 €, **combien Gérard gagne (ou perd) en moyenne** par ticket ?
> 4. **Bonus loi normale** : les temps de réponse de la caisse suivent une loi normale μ = 4 s, σ = 1 s. Au-delà de quelle durée une transaction est-elle « anormalement lente » (> 2 écarts-types) ? Quel % des transactions dépasse ce seuil ?

<details><summary>🏆 Solution du défi</summary>

**1 & 2 — Espérance de gain du client :**

$$E[\text{gain}] = 0{,}80 \times 0 + 0{,}18 \times 5 + 0{,}02 \times 50 = 0 + 0{,}90 + 1{,}00 = 1{,}90\ \text{€}$$

En moyenne, le client **récupère 1,90 €** par grattage… mais il a **payé 2 €**.

**3 — Le résultat pour Gérard :**
Le client perd en moyenne 2 − 1,90 = **0,10 € par ticket**, donc **Gérard gagne 0,10 € en moyenne par grattage**. La maison gagne toujours à long terme (c'est le principe de tout casino : une espérance légèrement en sa faveur). 🎰

**4 — Loi normale, transactions lentes :**
Seuil = μ + 2σ = 4 + 2×1 = **6 s**. Au-delà de +2σ, il reste ≈ (100 − 95)/2 = **2,5 %** des transactions (la moitié des 5 % hors de ±2σ, côté droit).

```python
from scipy.stats import norm
# Espérance du jeu
gains, probas = [0, 5, 50], [0.80, 0.18, 0.02]
E = sum(g*p for g, p in zip(gains, probas))
print(f"Gain moyen client = {E:.2f} € | Gérard gagne {2 - E:.2f} €/ticket")

# Transactions lentes (> 6 s)
print(f"P(transaction > 6 s) = {1 - norm.cdf(6, 4, 1):.2%}")  # ~2.28 %
```
</details>

---

## Vidéos d'auto-formation

> Regarde-les avec un papier à côté. Les liens directs ont été vérifiés ; les liens de recherche te mènent à la chaîne officielle.

| Titre | Chaîne | Langue | Durée | Lien | Ce que tu y apprends |
|---|---|---|---|---|---|
| The Normal Distribution, Clearly Explained!!! | StatQuest (Josh Starmer) | EN | ~5 min | https://www.youtube.com/watch?v=rzFX5NWojp0 | Ce qu'est la courbe en cloche, le rôle de μ et σ, intuition de la règle 68-95-99,7 |
| Conditional Probabilities, Clearly Explained!!! | StatQuest | EN | ~12 min | https://www.youtube.com/watch?v=_IgyaD7vOOA | Probabilité conditionnelle P(A\|B) avec exemples visuels |
| Bayes' Theorem, Clearly Explained!!! | StatQuest | EN | ~15 min | https://www.youtube.com/watch?v=9wCnvr7Xw4E | L'intuition de Bayes, pourquoi un test « à 99 % » trompe quand l'événement est rare |
| But what is the Central Limit Theorem? | 3Blue1Brown | EN | ~31 min | https://www.youtube.com/watch?v=zeJD6dqJ5lo | Pourquoi la loi normale apparaît partout (animations superbes) |
| LE COURS : Probabilités conditionnelles | Yvan Monka (maths-et-tiques) | FR | ~20 min | https://www.youtube.com/results?search_query=yvan+monka+le+cours+probabilités+conditionnelles | Cours FR clair : conditionnelles, arbres, indépendance |
| LE COURS : Loi binomiale | Yvan Monka | FR | ~25 min | https://www.youtube.com/results?search_query=yvan+monka+le+cours+loi+binomiale | Bernoulli, schéma de Bernoulli, loi binomiale, calculs |

---

## Exercices

> Fais-les d'abord à la main, puis vérifie en Python. Corrigés repliés ci-dessous.

**Exercice 1 — Probabilité simple et complémentaire.**
Un taux de conversion est de 4 %. Sur 50 visiteurs indépendants :
a) Quelle est la probabilité qu'**aucun** n'achète ?
b) Quelle est la probabilité qu'**au moins un** achète ?

<details><summary>Corrigé 1</summary>

a) $P(\text{aucun}) = 0{,}96^{50} \approx 0{,}130 = 13{,}0\%$.
b) $P(\text{au moins un}) = 1 - 0{,}96^{50} \approx 0{,}870 = 87{,}0\%$.

```python
p = 0.04; n = 50
aucun = (1-p)**n
print(round(aucun, 3), round(1-aucun, 3))  # 0.13 0.87
```
</details>

**Exercice 2 — Union et intersection.**
Sur les clients d'une boutique : 40 % achètent en magasin (M), 35 % en ligne (L), 12 % font les deux.
a) P(magasin OU en ligne) ?
b) Magasin et en ligne sont-ils indépendants ?

<details><summary>Corrigé 2</summary>

a) $P(M \cup L) = 0{,}40 + 0{,}35 - 0{,}12 = 0{,}63 = 63\%$.
b) Si indépendants : $0{,}40 \times 0{,}35 = 0{,}14 \neq 0{,}12$. **Non indépendants** (légèrement « anti-corrélés » : faire l'un réduit un peu l'autre).
</details>

**Exercice 3 — Probabilité conditionnelle.**
Reprends l'exercice 2. Quelle est la probabilité qu'un client achète **en ligne sachant qu'il achète en magasin** ?

<details><summary>Corrigé 3</summary>

$$P(L \mid M) = \frac{P(L \cap M)}{P(M)} = \frac{0{,}12}{0{,}40} = 0{,}30 = 30\%$$

Parmi ceux qui achètent en magasin, 30 % achètent aussi en ligne (contre 35 % en général).
</details>

**Exercice 4 — Espérance.**
Un jeu de fidélité : on tire une carte. 50 % → 0 €, 30 % → 5 €, 15 % → 10 €, 5 % → 50 €. Quelle est la valeur attendue d'un tirage ? Si chaque tirage coûte 6 € à l'enseigne, est-ce rentable pour elle ?

<details><summary>Corrigé 4</summary>

$$E[X] = 0{,}5 \times 0 + 0{,}3 \times 5 + 0{,}15 \times 10 + 0{,}05 \times 50 = 0 + 1{,}5 + 1{,}5 + 2{,}5 = 5{,}5\ \text{€}$$

L'enseigne distribue en moyenne 5,50 € par tirage. Si elle « paie » 6 € (coût/budget) par client, le dispositif reste sous le budget ; mais c'est surtout le **gain marketing** qui doit dépasser 5,50 €.
</details>

**Exercice 5 — 🚀 Loi binomiale (contrôle qualité Ch'ti Boutique) — *optionnel*.**
Un lot de 20 produits, taux de défaut p = 5 %.
a) Nombre attendu de défectueux ?
b) Probabilité d'avoir exactement 2 défectueux ?
c) Probabilité d'en avoir au moins 1 ?

<details><summary>Corrigé 5</summary>

a) $E[X] = 20 \times 0{,}05 = 1$.
b) $P(X=2) = \binom{20}{2} 0{,}05^2 0{,}95^{18} \approx 0{,}189$.
c) $P(X \ge 1) = 1 - 0{,}95^{20} \approx 0{,}642$.

```python
from scipy.stats import binom
n, p = 20, 0.05
print(n*p)                         # 1.0
print(round(binom.pmf(2, n, p),3)) # 0.189
print(round(1 - binom.pmf(0,n,p),3))  # 0.642
```
</details>

**Exercice 6 — Loi normale et règle 68-95-99,7.**
Les tailles des clients suivent une loi normale μ = 170 cm, σ = 8 cm.
a) Entre quelles tailles se trouvent ≈ 95 % des clients ?
b) Quel pourcentage mesure plus de 186 cm ?
c) Un client mesure 200 cm : quel est son z-score, est-ce une valeur courante ?

<details><summary>Corrigé 6</summary>

a) μ ± 2σ = 170 ± 16 → **entre 154 et 186 cm**.
b) 186 cm = μ + 2σ. Au-delà de +2σ : ≈ (100 − 95)/2 = **2,5 %**.
c) $z = (200 - 170)/8 = 3{,}75$. Au-delà de +3σ → extrêmement rare (< 0,1 %), **valeur atypique**.

```python
from scipy.stats import norm
mu, s = 170, 8
print(1 - norm.cdf(186, mu, s))       # ~0.0228 (≈2,3 %)
print((200-mu)/s)                     # 3.75
```
</details>

---

## Quiz (5 QCM)

**Q1.** Sur 30 visiteurs, 3 ont acheté. 32/30… pardon, le rapport 3/30 = 10 % est :
- A) la probabilité vraie de conversion
- B) une fréquence observée qui estime la probabilité
- C) impossible car > 5 %

**Q2.** $P(\bar{A})$ vaut :
- A) $1 + P(A)$
- B) $1 - P(A)$
- C) $1 / P(A)$

**Q3.** Pour A et B quelconques, $P(A \cup B)$ vaut :
- A) $P(A) + P(B)$
- B) $P(A) \times P(B)$
- C) $P(A) + P(B) - P(A \cap B)$

**Q4.** Un détecteur de fraude « à 99 % » génère surtout des fausses alertes quand :
- A) la fraude est très rare
- B) la fraude est très fréquente
- C) l'échantillon est grand

**Q5.** Pour une loi normale, environ 95 % des valeurs se situent dans :
- A) μ ± 1σ
- B) μ ± 2σ
- C) μ ± 3σ

<details><summary>Réponses</summary>

**Q1 : B** — c'est une fréquence (observée), estimation bruitée de la probabilité, surtout sur 30 personnes.
**Q2 : B** — le complémentaire : $1 - P(A)$.
**Q3 : C** — formule générale de l'union ; A) n'est vraie que si A et B sont incompatibles.
**Q4 : A** — quand l'événement cible est rare, même un bon détecteur produit majoritairement des faux positifs (intuition de Bayes).
**Q5 : B** — règle 68-95-99,7 : ±2σ ≈ 95 %.
</details>

---

## À retenir

**✅ Le noyau essentiel (à maîtriser absolument)**
- **Fréquence ≠ probabilité** : la fréquence observée *estime* la probabilité ; fie-toi aux grands échantillons. 🎲 *La pièce lancée 1 000 fois s'approche de 50 %.*
- **Probabilité simple** : ce qui m'arrange ÷ tout ce qui peut arriver (si équiprobable).
- **Complémentaire** : $P(\bar{A}) = 1 - P(A)$ — l'arme du « au moins un » (retourne le problème : calcule « aucun »).
- **Union** : $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ (ne pas double-compter le valet de cœur 🎲).
- **Indépendance** : $P(A \cap B) = P(A)P(B)$ ; supposer l'indépendance à tort est une erreur d'analyse classique (pluie ↔ parapluies).
- **Espérance** : $E[X] = \sum x_i P(X=x_i)$ = la valeur moyenne attendue (panier, campagne, ticket de grattage…).
- **Loi normale ⭐** : décrite par μ (centre) et σ (largeur). 🧠 *« La plupart au centre, peu aux extrêmes. »* **Règle 68-95-99,7** : « presque tout le monde tient en 3 pas de chaque côté. » Base des z-scores et de la détection d'anomalies — socle de l'inférence (chapitre 5) et du ML (C7).
- **Réflexe data** : toujours **tracer l'histogramme** avant de supposer une loi normale.

**🚀 Pour aller plus loin (optionnel)**
- **Conditionnelle / Bayes** : $P(A \mid B) = P(A \cap B)/P(B)$ ; ne **jamais** confondre $P(A\mid B)$ et $P(B\mid A)$. 🎲 Un test « à 99 % » ne donne que **~1,9 %** de vraies fraudes quand la cible est rare — l'intuition à garder à vie.
- **Binomiale** : nombre de succès sur n épreuves indépendantes ; $E[X] = np$. Idéale pour conversions et contrôle qualité.
- **Théorème central limite** : faire des moyennes fait apparaître la cloche — même à partir de données non-normales. C'est pourquoi la loi normale est partout.
