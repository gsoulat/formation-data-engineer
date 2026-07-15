# 02 — Modèles multimodaux (image + texte)

[← 01 — ViT](01-vision-transformers.md) | [🏠 Accueil](README.md) | [03 — Self-supervised →](03-self-supervised.md)

### 🎥 En vidéo
▶️ Cherche « [CLIP openai explained](https://www.youtube.com/results?search_query=clip+openai+explained) ».

## 🎯 Objectifs
- Comprendre comment un modèle relie **plusieurs modalités** (image ↔ texte).
- Saisir l'idée d'un **espace d'embedding partagé** (le principe de CLIP, DALL·E, GPT-4o).

## 🧠 Intuition & analogie

Jusqu'ici, un modèle traitait **une** modalité (image **ou** texte). Un modèle **multimodal** les
relie. L'exemple fondateur, **CLIP**, apprend à **rapprocher une image de sa légende** dans un
**espace commun** : la photo d'un chat et le texte « un chat » finissent **au même endroit**.

> **Analogie** — Imagine un **espace où images et phrases parlent la même langue**. « une plage au
> coucher de soleil » (texte) et la photo correspondante atterrissent **côte à côte**. Du coup, on peut
> chercher des images avec des mots, ou décrire une image avec des mots — car tout vit dans le **même
> plan**.

## 📐 Comment CLIP apprend (contrastif)

```
Image ──►[ encodeur image ]──► vecteur_image ┐
                                              ├─► rapprocher si (image, texte) vont ensemble,
Texte ──►[ encodeur texte ]──► vecteur_texte ┘    éloigner sinon  (apprentissage contrastif)
```

Entraîné sur des **centaines de millions** de paires (image, légende) du web — **sans étiquettes
manuelles** (la légende EST le label).

## 💻 En pratique : classification *zero-shot*

CLIP peut classer une image **sans avoir été entraîné sur ces classes** — juste en comparant l'image
à des phrases :

```python
# pseudo-code
scores = clip.similarite(image, ["une photo de chat", "une photo de chien", "une voiture"])
# la phrase la plus proche gagne → prédiction, sans réentraînement
```

> 💡 **La famille** — **CLIP** (image↔texte), **DALL·E / Stable Diffusion** (texte→image, cf. module
> génératif), **GPT-4o / Gemini** (texte+image+audio). Le multimodal est la direction dominante de l'IA.

## ✅ À retenir
- Un modèle multimodal projette **plusieurs modalités dans un espace partagé**.
- **CLIP** apprend par **contraste** sur des paires (image, légende) → permet la recherche et la
  classification **zero-shot**.
- C'est la brique derrière la génération texte→image et les LLM multimodaux.

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [CLIP expliqué](https://www.youtube.com/results?search_query=openai+clip+contrastive+explained) | EN | EN | L'espace partagé image/texte |
| [Modèles multimodaux](https://www.youtube.com/results?search_query=multimodal+ai+models+explained) | EN | EN | Le panorama (CLIP, GPT-4o…) |
