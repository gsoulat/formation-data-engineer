# 03 — GAN (Réseaux antagonistes génératifs)

[← 02 — VAE](02-vae.md) | [🏠 Accueil](README.md) | [04 — Diffusion →](04-diffusion.md)

### 🎥 En vidéo
▶️ Cherche « [GAN explained](https://www.youtube.com/results?search_query=generative+adversarial+network+explained) ».

## 🎯 Objectifs
- Comprendre le **duel** générateur vs discriminateur.
- Savoir pourquoi les GAN produisent des images **nettes** mais sont **difficiles** à entraîner.

## 🧠 Intuition & analogie

Un **GAN** fait s'affronter **deux réseaux** :
- le **générateur** part de bruit aléatoire et fabrique une fausse image ;
- le **discriminateur** reçoit des images (vraies et fausses) et doit dire **« vraie ou fausse ? »**.

Ils progressent **l'un contre l'autre** : le générateur essaie de tromper le discriminateur, le
discriminateur essaie de ne pas se faire avoir.

> **Analogie** — Un **faussaire** (générateur) fabrique des faux billets ; un **policier**
> (discriminateur) apprend à les repérer. À force de se confronter, le faussaire devient **si bon**
> que ses faux sont indiscernables des vrais. C'est exactement l'entraînement d'un GAN.

À la fin, on **jette le discriminateur** et on garde le générateur : il sait créer des images
réalistes à partir de simple bruit.

## 📐 Le jeu à somme nulle

```
bruit z ──►[ Générateur ]──► fausse image ─┐
                                            ├─►[ Discriminateur ]──► vrai / faux
vraies images ──────────────────────────────┘

Générateur : veut MAXIMISER l'erreur du discriminateur
Discriminateur : veut MINIMISER son erreur
```

## 💻 En PyTorch (la boucle, simplifiée)

```python
# À chaque étape, on entraîne les deux tour à tour :

# 1) Le discriminateur : bien classer vrai (1) et faux (0)
perte_D = bce(D(vraies), uns) + bce(D(G(bruit).detach()), zeros)

# 2) Le générateur : faire passer ses faux pour des vrais
perte_G = bce(D(G(bruit)), uns)      # il VEUT que D dise "vrai"
```

## 🛑 Les pièges (les GAN sont réputés instables)
- **Mode collapse** : le générateur trouve **une seule** image qui trompe le discriminateur et ne
  produit plus que celle-là (aucune diversité).
- **Déséquilibre** : si le discriminateur devient trop fort trop vite, le générateur n'a plus de
  signal pour progresser. L'entraînement est un **équilibre fragile**.

> 💡 Variantes clés à connaître : **DCGAN** (convolutif), **Conditional GAN** (génère une classe
> précise), **StyleGAN** (visages photoréalistes), **CycleGAN** (traduction d'image, ex. cheval↔zèbre).

## 🧪 Exercice
Entraîne un DCGAN sur MNIST et affiche une grille d'images générées toutes les quelques epochs.
Comment reconnais-tu un **mode collapse** sur la grille ?

<details><summary>💡 Corrigé</summary>

En cas de mode collapse, la grille montre **des images quasi identiques** (le générateur répète le même
chiffre). Une bonne génération montre au contraire de la **diversité** (des chiffres variés et nets).
</details>

## ✅ À retenir
- GAN = **générateur vs discriminateur**, entraînés en **duel** (faussaire vs policier).
- Images **plus nettes** que le VAE, mais entraînement **instable** (mode collapse, déséquilibre).
- On garde le **générateur** à la fin.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [GANs explained](https://www.youtube.com/results?search_query=gan+generative+adversarial+network+explained) | EN | EN | Le duel générateur/discriminateur |
| [StyleGAN / visages](https://www.youtube.com/results?search_query=stylegan+explained+faces) | EN | EN | Les GAN photoréalistes |
