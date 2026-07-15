# 🎨 Modèles génératifs

*Comment un réseau apprend à **créer** — images, sons, textes — plutôt qu'à seulement classer.*

> Sous-module du parcours [Deep Learning](../README.md). Prérequis : [Fondamentaux DL](../01-Fondamentaux-DL/)
> et [CNN](../CNN/).

Jusqu'ici, les réseaux **discriminaient** (« c'est un chat »). Ici, ils **génèrent** (« crée un chat
qui n'existe pas »). On parcourt les 4 grandes familles, de la plus simple à l'état de l'art.

## 📚 Cours

| # | Leçon | Idée en une phrase |
|---|---|---|
| 01 | [Autoencodeurs](01-autoencodeurs.md) | compresser puis reconstruire (débruitage, anomalies) |
| 02 | [VAE](02-vae.md) | un espace latent continu → **générer** en douceur |
| 03 | [GAN](03-gan.md) | un **duel** faussaire/policier → images nettes |
| 04 | [Diffusion](04-diffusion.md) | **débruiter** du bruit pur → Stable Diffusion, DALL·E |

## ⚖️ En un coup d'œil

| Modèle | Analogie | Force | Faiblesse |
|---|---|---|---|
| Autoencodeur | valise compressée | simple, débruitage | ne génère pas vraiment |
| VAE | quartiers au lieu d'adresses | stable, espace continu | images floues |
| GAN | faussaire vs policier | images nettes | instable (mode collapse) |
| Diffusion | sculpteur qui retire le bruit | qualité + diversité (SOTA) | génération lente |

## 🎯 Brief

- [**Génération d'images**](../../99-Brief/Dev-IA/Deep-Learning-Generatif/BRIEF_GENERATIF.md) — construire un autoencodeur puis un GAN sur MNIST, et comparer.

## ➡️ Après ce module
Les modèles génératifs de **texte** à grande échelle sont les **LLM** → [10-Large-Language-Model](../../10-Large-Language-Model/).

---
[🏠 Retour au module Deep Learning](../README.md)
