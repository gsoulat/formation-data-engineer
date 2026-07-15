# 01 — Autoencodeurs

[🏠 Accueil](README.md) | [02 — VAE →](02-vae.md)

### 🎥 En vidéo
▶️ Cherche « [autoencoder explained](https://www.youtube.com/results?search_query=autoencoder+explained) » et « [autoencodeur expliqué français](https://www.youtube.com/results?search_query=autoencodeur+explique+francais) ».

## 🎯 Objectifs
- Comprendre l'idée d'**encoder → code latent → decoder**.
- Voir à quoi sert un autoencodeur (compression, débruitage, détection d'anomalies).
- L'implémenter en PyTorch.

## 🧠 Intuition & analogie

Un **autoencodeur** apprend à **compresser** une donnée puis à la **reconstruire**. Il est fait de
deux moitiés :
- l'**encodeur** réduit l'entrée à un petit vecteur, le **code latent** (le goulot d'étranglement) ;
- le **décodeur** essaie de **reconstruire l'entrée d'origine** à partir de ce code.

> **Analogie** — Faire tenir une grosse valise dans un **sac de voyage minuscule** (le code latent),
> puis tout ressortir à l'arrivée. Pour réussir, le réseau est **forcé de ne garder que l'essentiel** :
> il apprend une représentation compacte du sens de la donnée, pas les détails inutiles.

Comme la cible = l'entrée elle-même, **aucune étiquette n'est nécessaire** : c'est de l'apprentissage
**non-supervisé**.

## 📐 Ce qui se passe

```
x ──►[ Encodeur ]──► z (code latent, petit) ──►[ Décodeur ]──► x̂ (reconstruction)
                                       loss = distance(x, x̂)   ← on minimise l'erreur de reconstruction
```

Le **goulot d'étranglement** (dimension de `z` << dimension de `x`) est essentiel : sans lui, le
réseau se contenterait de recopier l'entrée sans rien apprendre.

## 💻 En PyTorch

```python
import torch.nn as nn

class Autoencodeur(nn.Module):
    def __init__(self, dim_entree=784, dim_latent=32):
        super().__init__()
        self.encodeur = nn.Sequential(
            nn.Linear(dim_entree, 128), nn.ReLU(),
            nn.Linear(128, dim_latent)          # goulot d'étranglement
        )
        self.decodeur = nn.Sequential(
            nn.Linear(dim_latent, 128), nn.ReLU(),
            nn.Linear(128, dim_entree), nn.Sigmoid()   # pixels entre 0 et 1
        )

    def forward(self, x):
        z = self.encodeur(x)
        return self.decodeur(z)

# Entraînement : la cible EST l'entrée
# loss = nn.MSELoss()(model(x), x)
```

## 🛠️ À quoi ça sert vraiment
- **Débruitage** (*denoising autoencoder*) : on entraîne à reconstruire une image propre à partir
  d'une version bruitée → le réseau apprend à enlever le bruit.
- **Détection d'anomalies** : une donnée « anormale » se reconstruit mal (grosse erreur) → alerte.
- **Réduction de dimension** (une alternative non-linéaire à l'ACP/PCA).

> 🛑 **Erreur courante** — croire qu'un autoencodeur classique **génère** de nouvelles images. Non :
> son espace latent a des « trous ». Pour *générer*, il faut le **VAE** (leçon suivante).

## 🧪 Exercice
Sur Fashion-MNIST, entraîne l'autoencodeur ci-dessus, puis affiche des paires (image originale, image
reconstruite). Que se passe-t-il si tu réduis `dim_latent` de 32 à 4 ?

<details><summary>💡 Corrigé</summary>

Avec `dim_latent=4`, la reconstruction devient **floue** : le goulot est trop étroit pour garder assez
d'information. C'est le compromis **compression vs fidélité** — plus le code est petit, plus on perd de
détails, mais plus la représentation est « résumée ».
</details>

## ✅ À retenir
- Autoencodeur = **encodeur → code latent → décodeur**, entraîné à **reconstruire l'entrée**.
- Le **goulot d'étranglement** force à apprendre l'essentiel (non-supervisé).
- Usages : **débruitage**, **détection d'anomalies**, réduction de dimension — **pas** la génération pure.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Autoencoders explained](https://www.youtube.com/results?search_query=autoencoders+explained+deep+learning) | EN | EN | Le principe encoder/decoder |
| [Denoising autoencoder](https://www.youtube.com/results?search_query=denoising+autoencoder+explained) | EN | EN | Enlever le bruit |
