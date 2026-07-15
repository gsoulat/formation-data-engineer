# Brief — Générer des images (autoencodeur puis GAN)

## Contexte

Vous rejoignez un **studio créatif** qui veut expérimenter la **génération d'images par IA**. Avant
d'attaquer Stable Diffusion, l'équipe veut que vous **compreniez les briques** : vous allez construire
vous-même deux générateurs sur un jeu simple (des chiffres manuscrits), puis les **comparer**.

> **Analogie** — Avant de sculpter le marbre (diffusion), on apprend à modeler la pâte à modeler
> (autoencodeur) et à jouer au faussaire (GAN). Objectif : **comprendre** ce que « générer » veut dire
> pour un réseau.

### Question centrale

**« Comment un réseau apprend-il à *créer* des images qui n'existent pas — et qu'est-ce qui distingue
concrètement un autoencodeur, un VAE et un GAN ? »**

### Données

- **MNIST** (chiffres manuscrits) — parfait pour la génération, léger, via
  `torchvision.datasets.MNIST(root, download=True)`. Option : **Fashion-MNIST** (vêtements).

---

## Modalités pédagogiques

Travail **individuel**, ~5 jours. Prérequis : [module Modèles génératifs](../../../09-Deep-Learning/Generatif/)
et [Fondamentaux DL](../../../09-Deep-Learning/01-Fondamentaux-DL/).

### Phase 1 — Autoencodeur & reconstruction (J1)

Construisez un **autoencodeur** ([leçon 01](../../../09-Deep-Learning/Generatif/01-autoencodeurs.md)) et
entraînez-le à reconstruire les chiffres. Affichez des paires (original, reconstruction). Faites varier
la **taille du code latent** : quel est l'effet sur la qualité ? Testez la version **débruitage** (on
ajoute du bruit en entrée, la cible reste l'image propre).

### Phase 2 — VAE & génération (J2-J3)

Passez au **VAE** ([leçon 02](../../../09-Deep-Learning/Generatif/02-vae.md)) : espace latent
probabiliste, terme KL. **Générez** de nouveaux chiffres en tirant `z ~ N(0,1)`. Faites une
**interpolation** entre deux chiffres dans l'espace latent : la transition est-elle fluide ? C'est la
preuve que le VAE génère (pas seulement reconstruit).

### Phase 3 — GAN (J4)

Construisez un **DCGAN** ([leçon 03](../../../09-Deep-Learning/Generatif/03-gan.md)) : générateur vs
discriminateur. Surveillez l'entraînement (les deux pertes) et **détectez un éventuel mode collapse**.
Affichez une grille d'images générées au fil des epochs.

### Phase 4 — Comparaison & restitution (J5)

Comparez **autoencodeur / VAE / GAN** sur les mêmes chiffres : netteté, diversité, stabilité
d'entraînement. Rédigez un rapport avec des **exemples générés** par chaque méthode et vos conclusions
(quand utiliser quoi ?). Positionnez la **diffusion** ([leçon 04](../../../09-Deep-Learning/Generatif/04-diffusion.md))
dans ce paysage — sans forcément l'implémenter.

---

## Modalités d'évaluation

- **Démonstration technique (60 %)** : au moins **deux** générateurs (autoencodeur/VAE + GAN)
  fonctionnent et produisent des images reconnaissables ; génération et interpolation démontrées.
- **Revue de code & analyse (40 %)** : compréhension des différences (espace latent, duel adversarial),
  détection du mode collapse, comparaison argumentée avec exemples.

> **Validation partielle** : un VAE qui génère correctement + une analyse solide des différences, même
> sans GAN parfaitement stable, peut valider partiellement (les GAN sont réputés difficiles).

---

## Livrables

**Repo GitHub public** :

- Le code des générateurs (autoencodeur/VAE + GAN).
- Des **grilles d'images générées** par chaque méthode + une **interpolation latente** (VAE).
- Un **rapport comparatif** (netteté / diversité / stabilité + quand utiliser quoi).
- Un **README** : approches, résultats, limites, auteur.

---

## Critères de performance

**Reconstruire & comprendre l'espace latent**
- L'autoencodeur reconstruit correctement ; l'effet de la taille du code latent est montré.
- Le VAE **génère** (échantillonnage `z ~ N(0,1)`) et l'**interpolation** latente est fluide.

**Générer par duel (GAN)**
- Un GAN est entraîné ; le générateur et le discriminateur sont correctement mis en opposition.
- Le **mode collapse** est surveillé et discuté.

**Comparer & restituer**
- Les 3 approches sont comparées avec des **exemples générés** à l'appui.
- Le rapport situe la **diffusion** dans le paysage ; le code est propre et versionné.

---

## Ressources

- Module [Modèles génératifs](../../../09-Deep-Learning/Generatif/) (autoencodeurs, VAE, GAN, diffusion)
- PyTorch DCGAN tutorial : https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html
- VAE (exemple PyTorch) : https://github.com/pytorch/examples/tree/main/vae
- MNIST : https://pytorch.org/vision/stable/generated/torchvision.datasets.MNIST.html

> 🔎 **Pour aller plus loin** : implémenter un **mini modèle de diffusion** sur MNIST, ou explorer
> Stable Diffusion via `diffusers` (Hugging Face) et le lien avec les [LLM](../../../10-Large-Language-Model/).
