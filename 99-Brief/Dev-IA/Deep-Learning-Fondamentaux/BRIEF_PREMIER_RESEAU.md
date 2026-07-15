# Brief — Ton premier réseau de neurones (Fashion-MNIST)

## Contexte

Vous rejoignez l'équipe data d'un **site de mode en ligne**. Chaque jour, des milliers de photos de
vêtements arrivent, et il faut les **trier automatiquement par catégorie** (t-shirt, pull, chaussure,
sac…) pour les ranger dans le bon rayon. C'est votre **premier projet de Deep Learning** : vous allez
construire, entraîner et diagnostiquer un réseau de neurones **de vos propres mains**.

> **Analogie** — Vous n'allez pas coder « si beaucoup de pixels sombres en bas → chaussure ». Vous
> allez **montrer des milliers d'exemples** au réseau et le laisser **découvrir lui-même** ce qui
> distingue un pull d'un sac (le principe du [chapitre 0 — intuition](../../../09-Deep-Learning/01-Fondamentaux-DL/cours/00-intuition-analogies.md)).

### Question centrale

**« À partir d'une image 28×28 en niveaux de gris, peut-on prédire la catégorie du vêtement — et
comment reconnaître quand mon réseau *apprend vraiment* plutôt qu'il *mémorise* ? »**

### Données

- **Fashion-MNIST** — 70 000 images 28×28 de vêtements, 10 catégories. Réel, propre, téléchargeable
  **directement via PyTorch** : `torchvision.datasets.FashionMNIST(root, download=True)`.
  https://github.com/zalandoresearch/fashion-mnist

---

## Modalités pédagogiques

Travail **individuel**, ~4 jours. Prérequis : [Fondamentaux DL](../../../09-Deep-Learning/01-Fondamentaux-DL/)
(chapitres 0 à 4). Chaque phase produit un résultat vérifiable.

### Phase 1 — Comprendre et charger les données (J1)

Chargez Fashion-MNIST, **affichez des exemples** de chaque classe, vérifiez la répartition. Pourquoi
**normalise-t-on** les pixels (de 0-255 vers ~0-1) avant de les donner au réseau ? Séparez
proprement train / validation / test. Combien d'images dans chaque ?

### Phase 2 — Un MLP « à la main » puis en PyTorch (J2)

Construisez un **perceptron multicouche** (MLP) : on « aplatit » l'image 28×28 en un vecteur de 784
valeurs, puis 1-2 couches cachées, puis 10 sorties. Écrivez la **boucle d'entraînement** vous-même
(forward → loss → `backward()` → `optimizer.step()`). Que fait chacune de ces 4 lignes ? (Reliez-les
au chapitre 0 : loss = le GPS, `backward` = la backpropagation, `step` = un pas de descente de gradient.)

### Phase 3 — Diagnostiquer l'apprentissage (J3)

Tracez les courbes de **loss et accuracy, train vs validation**, au fil des epochs. **Provoquez
volontairement un overfitting** (réseau trop gros, trop d'epochs) et **observez-le** sur les courbes :
à quoi le reconnaît-on ? Puis combattez-le (dropout, early stopping, moins de paramètres). C'est le
cœur du métier : savoir **lire** ce que le réseau est en train de faire.

> **Analogie** — Overfitting = l'élève qui apprend le corrigé par cœur. Vos courbes doivent vous
> alerter quand le réseau « récite » au lieu de « comprendre » (train parfait, validation qui décroche).

### Phase 4 — Passer au CNN & restituer (J4)

Remplacez le MLP par un **petit CNN** (2 couches de convolution). Comparez les performances : pourquoi
le CNN fait-il mieux **sur des images** qu'un MLP (indice : chapitre 0 §10, le « détecteur de motif »
qui glisse) ? Rédigez un court rapport : architecture, courbes, meilleure accuracy test, et **les 3
choses que vous avez comprises** sur l'entraînement d'un réseau.

---

## Modalités d'évaluation

- **Démonstration technique (60 %)** : le réseau s'entraîne, atteint une accuracy test correcte
  (> 88 % visé), et vous savez expliquer chaque étape de la boucle d'entraînement en direct.
- **Revue de code & analyse (40 %)** : courbes train/val commentées, overfitting démontré **et** traité,
  comparaison MLP vs CNN argumentée.

> **Validation partielle** : un réseau imparfait mais dont l'analyse (courbes, diagnostic overfitting)
> est juste et documentée peut valider partiellement.

---

## Livrables

**Repo GitHub public** :

- Un notebook (ou scripts) : données → MLP → entraînement → diagnostic → CNN.
- Les **courbes** train/val (loss + accuracy) commentées.
- Le **rapport** (les 3 apprentissages + comparaison MLP/CNN + honnêteté sur les limites).
- Un **README** : présentation, comment lancer, résultats, auteur.

---

## Critères de performance

**Préparer les données**
- Les images sont normalisées et le split train/val/test est étanche.
- La nature du problème (classification multi-classes, 10 classes) est correctement posée.

**Construire et entraîner un réseau**
- La boucle d'entraînement (forward, loss, backward, step) est écrite et **comprise** (l'apprenant sait l'expliquer).
- Un MLP **et** un CNN sont entraînés et comparés.

**Diagnostiquer**
- Les courbes train/val sont tracées et **interprétées**.
- Un overfitting est **provoqué, identifié et traité** (dropout / early stopping).

**Restituer**
- Le rapport explique les choix et les résultats honnêtement ; le code est propre et versionné.

---

## Ressources

- Chapitre 0 — [Comprendre le DL par l'intuition](../../../09-Deep-Learning/01-Fondamentaux-DL/cours/00-intuition-analogies.md)
- PyTorch — Quickstart : https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
- Fashion-MNIST : https://github.com/zalandoresearch/fashion-mnist
- 3Blue1Brown — Neural Networks (série) : https://www.youtube.com/results?search_query=3blue1brown+neural+networks

> 🔎 **Pour aller plus loin** : brief suivant → [Classificateur d'images par transfer learning](../Deep-Learning-Vision/BRIEF_CLASSIFICATION_IMAGES.md) (vrai dataset, backbone pré-entraîné).
