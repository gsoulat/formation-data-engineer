# 04 — Modèles de diffusion

[← 03 — GAN](03-gan.md) | [🏠 Accueil](README.md)

### 🎥 En vidéo
▶️ Cherche « [diffusion models explained](https://www.youtube.com/results?search_query=diffusion+models+explained) ».

## 🎯 Objectifs
- Comprendre l'idée **bruiter → apprendre à débruiter → générer**.
- Savoir pourquoi c'est la technologie derrière **Stable Diffusion, DALL·E, Midjourney**.

## 🧠 Intuition & analogie

Les modèles de **diffusion** sont l'état de l'art de la génération d'images. L'idée est étonnamment
simple :
1. On prend une vraie image et on lui ajoute **progressivement du bruit**, étape par étape, jusqu'à ce
   qu'elle devienne du **bruit pur** (une image de neige TV).
2. On entraîne un réseau à faire **l'inverse** : à chaque étape, **enlever un peu de bruit**.
3. Pour **générer**, on part de **bruit pur** et on applique le réseau plein de fois → une image nette
   apparaît.

> **Analogie** — Un **sculpteur** qui part d'un bloc de marbre brut (le bruit) et **retire de la
> matière petit à petit** jusqu'à révéler la statue. Le modèle de diffusion « sculpte » une image en
> **retirant du bruit** graduellement. Autre image : un **Polaroid inversé** — au lieu de voir l'image
> apparaître, on part du grain et on la fait émerger étape par étape.

## 📐 Les deux processus

```
Forward (fixe, pas d'apprentissage) :  image ──+bruit──+bruit──...──► bruit pur
Reverse (appris par le réseau)      :  bruit pur ──débruite──...──► image nette
```

Le réseau (souvent un **U-Net**) apprend une seule chose : *« quel bruit a été ajouté à cette étape ? »*.
En le retirant à rebours des dizaines de fois, on reconstruit une image.

## 💻 Idée du code (schéma)

```python
# Entraînement : apprendre à prédire le bruit ajouté
t = torch.randint(0, T, (batch,))          # une étape de bruitage au hasard
bruit = torch.randn_like(x)
x_bruite = racine_alpha[t] * x + racine_un_moins_alpha[t] * bruit
bruit_predit = unet(x_bruite, t)
loss = mse(bruit_predit, bruit)            # on prédit LE BRUIT, pas l'image

# Génération : partir du bruit et débruiter T fois (boucle inverse)
```

> 💡 **Text-to-image** (Stable Diffusion) : on **conditionne** le débruitage par un texte (via un
> encodeur type CLIP) — le réseau débruite « vers » ce que décrit le prompt. C'est ainsi qu'« un chat
> astronaute en aquarelle » devient une image.

## ⚖️ Diffusion vs GAN vs VAE
| | Qualité | Diversité | Stabilité d'entraînement | Vitesse de génération |
|---|:--:|:--:|:--:|:--:|
| VAE | moyenne (flou) | bonne | facile | rapide |
| GAN | nette | limitée (mode collapse) | difficile | rapide |
| **Diffusion** | **excellente** | **excellente** | **stable** | lente (beaucoup d'étapes) |

## 🧪 Exercice (réflexion)
Pourquoi la génération par diffusion est-elle **lente** comparée à un GAN, et comment les modèles
récents (ex. *latent diffusion*, *DDIM*) accélèrent-ils cela ?

<details><summary>💡 Corrigé</summary>

Lente car il faut **répéter le débruitage** des dizaines à des centaines de fois (un GAN génère en
**un seul passage**). Accélérations : travailler dans un **espace latent** compressé (*latent
diffusion*, le principe de Stable Diffusion) plutôt que sur les pixels, et des schémas
d'échantillonnage qui **sautent des étapes** (DDIM) → quelques dizaines d'étapes au lieu de mille.
</details>

## ✅ À retenir
- Diffusion = **ajouter du bruit** puis **apprendre à l'enlever** ; générer = débruiter du bruit pur.
- Le réseau prédit **le bruit** à chaque étape (souvent un U-Net).
- **État de l'art** en qualité et diversité (Stable Diffusion, DALL·E) ; plus **lent** à générer.
- Le **text-to-image** = diffusion **conditionnée** par un texte.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [Diffusion models explained](https://www.youtube.com/results?search_query=diffusion+models+explained+simply) | EN | EN | Bruiter/débruiter |
| [How Stable Diffusion works](https://www.youtube.com/results?search_query=how+stable+diffusion+works) | EN | EN | Text-to-image, latent diffusion |
