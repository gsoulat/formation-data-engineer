# Brief — Classificateur d'images par Deep Learning (transfer learning)

## Contexte

Vous êtes Développeur IA chez **PetScan**, une jeune entreprise qui outille les cabinets
vétérinaires. Aujourd'hui, à l'accueil, on saisit la **race de l'animal à la main** : source
d'erreurs, de fautes de frappe et de lenteur. PetScan veut une brique qui, **à partir d'une simple
photo**, propose automatiquement la race — avec un niveau de confiance et une explication visuelle
que le vétérinaire peut vérifier d'un coup d'œil.

Vous n'allez pas entraîner un réseau depuis zéro (des millions d'images, des semaines de calcul) :
vous allez faire du **transfer learning**, c'est-à-dire **partir d'un réseau déjà entraîné** sur des
millions d'images et le **ré-adapter** à vos races.

> **Analogie** — Le transfer learning, c'est **recruter un photographe professionnel** (qui sait déjà
> voir formes, textures, contours) et lui apprendre **uniquement** à reconnaître vos races, plutôt que
> de former quelqu'un à voir depuis la naissance. On garde l'œil expert, on ne réapprend que la
> spécialité.

### Question centrale

**« À partir d'une photo, peut-on prédire la race de l'animal de façon fiable, mesurable et
explicable — sans entraîner un réseau depuis zéro ? »**

### Données

- **Oxford-IIIT Pet Dataset** — 37 races de chats et chiens, ~7 400 images annotées. Réel, libre,
  téléchargeable **directement via torchvision** :
  `torchvision.datasets.OxfordIIITPet(root, download=True)` → https://www.robots.ox.ac.uk/~vgg/data/pets/
- Alternative plus ambitieuse : **Stanford Dogs** (120 races) — http://vision.stanford.edu/aditya86/ImageNetDogs/

### Architecture attendue

```
Photos ──► Prétraitement/Augmentation ──► Modèle pré-entraîné (backbone gelé)
                                                │
                                     Nouvelle tête de classification (37 classes)
                                                │
                     Entraînement ──► Évaluation ──► Explicabilité (Grad-CAM) ──► Démo
```

Vous utiliserez **PyTorch** + **torchvision**, un backbone type **ResNet18/34** ou
**EfficientNet-B0** pré-entraîné sur ImageNet, et une **nouvelle tête** adaptée à vos classes.

---

## Modalités pédagogiques

Travail **individuel**, sur ~5 jours. Chaque phase produit un résultat vérifiable. Prérequis :
[Fondamentaux DL](../../../09-Deep-Learning/01-Fondamentaux-DL/) (surtout le
[chapitre 0 — intuition](../../../09-Deep-Learning/01-Fondamentaux-DL/cours/00-intuition-analogies.md))
et [CNN](../../../09-Deep-Learning/CNN/).

### Phase 1 — Cadrage & exploration des données (J1)

Pas de modèle encore. Téléchargez le dataset, **regardez vraiment les images** : combien par race ?
Le jeu est-il équilibré ? Quelles races se ressemblent (risque de confusion) ? Documentez la
répartition, quelques exemples par classe, et un `split` train/validation/test **stratifié**.
Comment allez-vous éviter que le modèle « voie » les images de test pendant l'entraînement ?

### Phase 2 — Prétraitement & augmentation (J2)

Mettez en place les transformations `torchvision.transforms` : redimensionnement, normalisation aux
statistiques d'ImageNet (indispensable pour un backbone pré-entraîné), et **augmentation de données**
sur le train (flips, rotations, variations de couleur). Pourquoi n'augmente-t-on **jamais** le jeu de
validation/test ? Quel est le lien entre augmentation et **overfitting** (chapitre intuition §9) ?

### Phase 3 — Transfer learning & entraînement (J3)

Chargez le backbone pré-entraîné, **gelez** ses poids, remplacez la dernière couche par une tête à
37 sorties, et entraînez d'abord **seulement la tête**. Puis pratiquez le **fine-tuning** : dégelez
les dernières couches avec un **learning rate plus faible**. Suivez les courbes de *loss* et
*accuracy* train **vs** validation : que vous disent-elles sur l'overfitting ? Comment choisissez-vous
quand arrêter (*early stopping*) ? Journalisez vos expériences (hyperparamètres, résultats).

### Phase 4 — Évaluation & explicabilité (J4)

Évaluez sur le **jeu de test** jamais vu : accuracy globale, mais surtout **matrice de confusion**
(quelles races se confondent ?) et précision/rappel par classe. Puis rendez le modèle **explicable**
avec **Grad-CAM** : une carte de chaleur qui montre **où** le réseau a regardé pour décider.

> **Analogie** — Grad-CAM, c'est demander au modèle de **surligner sur la photo** ce qui l'a
> convaincu. S'il classe « berger » en regardant… le canapé du fond, vous avez un problème de biais.

### Phase 5 — Démo & restitution (J5)

Emballez une **démo** simple (Gradio ou Streamlit) : on dépose une photo, on obtient les 3 races les
plus probables avec leur confiance **et** la carte Grad-CAM. Rédigez un rapport : choix
d'architecture, résultats, limites, et **honnêteté sur les biais** (races sous-représentées, photos
de mauvaise qualité).

---

## Modalités d'évaluation

- **Démonstration technique (60 %)** : la démo tourne, prédit correctement sur des photos nouvelles,
  affiche confiance + Grad-CAM. (15 min de démo + 10 min de questions.)
- **Revue de code & méthodologie (40 %)** : rigueur du split, augmentation, transfer learning vs
  fine-tuning maîtrisés, évaluation honnête (pas seulement l'accuracy), journal d'expériences.

> **Validation partielle** : un apprenant dont la démo n'est pas parfaite mais dont le pipeline, la
> méthodologie d'évaluation et l'explicabilité sont solides et documentés peut valider partiellement.

---

## Livrables

**Repo GitHub public** contenant :

- Le code d'entraînement (scripts ou notebooks) : données → augmentation → transfer learning →
  évaluation.
- Le **journal d'expériences** (hyperparamètres testés, courbes, meilleur modèle) — un tableau suffit.
- Les **visualisations** : courbes d'entraînement, matrice de confusion, exemples Grad-CAM (bons et mauvais).
- La **démo** (Gradio/Streamlit) + instructions de lancement.
- Un **README** : présentation, dataset, architecture, résultats, **limites & biais**, auteur.

---

## Critères de performance

**Préparer et explorer les données**
- Le split train/validation/test est stratifié et **étanche** (aucune fuite).
- L'augmentation n'est appliquée qu'au train ; la normalisation ImageNet est correcte.
- La répartition des classes et les confusions probables sont documentées.

**Entraîner par transfer learning**
- Le backbone pré-entraîné est réutilisé (tête remplacée), pas un réseau entraîné de zéro.
- La distinction *feature extraction* (backbone gelé) vs *fine-tuning* est mise en œuvre et justifiée.
- Le sur-apprentissage est surveillé (courbes train/val) et traité (early stopping, augmentation).

**Évaluer et expliquer**
- L'évaluation va au-delà de l'accuracy : matrice de confusion + métriques par classe.
- Grad-CAM est produit et **interprété** (le modèle regarde-t-il l'animal ou le décor ?).
- Le rapport discute honnêtement les **biais et limites**.

**Restituer**
- La démo fonctionne sur des images nouvelles et affiche confiance + explication.
- Le README permet de relancer le projet ; le code est propre et versionné.

---

## Ressources

- PyTorch — Transfer Learning tutorial : https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
- torchvision — modèles pré-entraînés : https://pytorch.org/vision/stable/models.html
- Oxford-IIIT Pet : https://www.robots.ox.ac.uk/~vgg/data/pets/
- Grad-CAM (pytorch-grad-cam) : https://github.com/jacobgil/pytorch-grad-cam
- Rappel intuition : [chapitre 0 — Comprendre le DL par l'intuition](../../../09-Deep-Learning/01-Fondamentaux-DL/cours/00-intuition-analogies.md)

> 🔎 **Pour aller plus loin** : comparer deux backbones (ResNet vs EfficientNet), gérer le
> déséquilibre de classes (pondération de la loss), exporter le modèle (TorchScript/ONNX) pour un
> déploiement — voir le brief [MLOps & Monitoring](../MLOps-Monitoring/BRIEF_MLOPS_MONITORING.md).
