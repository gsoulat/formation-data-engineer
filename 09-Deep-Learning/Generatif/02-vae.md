# 02 — VAE (Autoencodeurs variationnels)

[← 01 — Autoencodeurs](01-autoencodeurs.md) | [🏠 Accueil](README.md) | [03 — GAN →](03-gan.md)

### 🎥 En vidéo
▶️ Cherche « [variational autoencoder explained](https://www.youtube.com/results?search_query=variational+autoencoder+explained) ».

## 🎯 Objectifs
- Comprendre pourquoi un autoencodeur classique ne **génère** pas, et comment le VAE corrige ça.
- Saisir l'idée d'un **espace latent continu et probabiliste**.

## 🧠 Intuition & analogie

Le problème de l'autoencodeur : son espace latent est **plein de trous**. Si tu piochbes un point au
hasard, le décodeur produit souvent n'importe quoi. Le **VAE** rend cet espace **lisse et continu**,
de sorte que **n'importe quel point** donne une image plausible → on peut **générer**.

L'astuce : au lieu d'encoder une image en **un point fixe**, le VAE l'encode en **un petit nuage**
(une distribution : une moyenne μ et une dispersion σ). On **pioche** un point dans ce nuage pour
décoder.

> **Analogie** — Un autoencodeur range chaque visage à une **adresse précise**. Le VAE lui attribue un
> **quartier** (un nuage). Résultat : l'espace n'a plus de terrains vagues entre les adresses — se
> promener d'un quartier à l'autre fait **varier l'image en douceur** (un visage souriant → neutre).

## 📐 Ce qui change

Deux ingrédients par rapport à l'autoencodeur :
1. L'encodeur sort **μ et σ** (pas un simple `z`). On échantillonne `z = μ + σ·ε` (*reparam. trick*).
2. La loss = **reconstruction** + un terme **KL** qui force les nuages à rester proches d'une
   gaussienne standard (c'est ce qui **bouche les trous** et rend l'espace continu).

```
loss = reconstruction(x, x̂)  +  β · KL( N(μ,σ) || N(0,1) )
```

## 💻 En PyTorch (le cœur)

```python
def reparametrer(mu, logvar):
    sigma = torch.exp(0.5 * logvar)
    eps = torch.randn_like(sigma)      # bruit aléatoire
    return mu + sigma * eps            # on pioche dans le "nuage"

# perte KL (garde l'espace latent bien organisé)
kl = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
loss = mse(x_reconstruit, x) + beta * kl
```

**Générer** devient trivial : on tire `z ~ N(0,1)` et on décode → une image nouvelle.

## 🛑 Erreur courante
Un `β` (poids du terme KL) **trop grand** → l'espace est parfait mais les images sont **floues**
(*posterior collapse*). Trop petit → on retombe sur un autoencodeur qui ne génère pas bien. C'est un
équilibre à régler.

## 🧪 Exercice
Après entraînement sur MNIST, prends deux chiffres, encode-les en `z1` et `z2`, puis décode des points
**intermédiaires** (interpolation `z = (1-t)·z1 + t·z2`). Que vois-tu ?

<details><summary>💡 Corrigé</summary>

Tu vois un chiffre **se transformer en douceur** en un autre (ex. un 3 qui devient un 8). C'est la
preuve que l'espace latent du VAE est **continu et signifiant** — impossible avec un autoencodeur
classique.
</details>

## ✅ À retenir
- Le VAE encode en **distribution** (μ, σ), pas en point → espace latent **continu**.
- La **perte KL** organise l'espace pour qu'on puisse **générer** en piochant `z ~ N(0,1)`.
- Génère des images plus **floues** que les GAN, mais plus **stable** à entraîner.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [VAE clearly explained](https://www.youtube.com/results?search_query=variational+autoencoder+clearly+explained) | EN | EN | μ/σ, KL, génération |
| [Le VAE en français](https://www.youtube.com/results?search_query=vae+autoencodeur+variationnel+francais) | FR | FR | L'espace latent probabiliste |
