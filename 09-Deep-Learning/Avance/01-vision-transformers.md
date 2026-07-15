# 01 — Vision Transformers (ViT)

[🏠 Accueil](README.md) | [02 — Multimodal →](02-multimodal.md)

### 🎥 En vidéo
▶️ Cherche « [vision transformer explained](https://www.youtube.com/results?search_query=vision+transformer+vit+explained) ».

## 🎯 Objectifs
- Comprendre comment on applique un **Transformer** (né pour le texte) à des **images**.
- Savoir quand un ViT bat un CNN — et quand non.

## 🧠 Intuition & analogie

Le CNN regarde une image avec des **filtres locaux** qui glissent (chapitre 0 §10). Le **Vision
Transformer** fait autre chose : il **découpe l'image en petits carrés** (*patches*, ex. 16×16), les
met en file comme des **mots**, et applique le mécanisme d'**attention** (chapitre 0 §11) pour que
chaque patch « regarde » tous les autres.

> **Analogie** — Un CNN lit l'image avec une **loupe** qui balaie les détails proches. Un ViT lit
> l'image **comme une phrase** : chaque patch est un « mot », et l'attention relie directement le coin
> haut-gauche au coin bas-droite. D'où sa force pour les **relations à longue distance** dans l'image.

## 📐 Le pipeline

```
Image ──► découpe en patches ──► chaque patch → un vecteur (token)
      ──► + encodage de position ──► [ Transformer (attention) ] ──► classification
```

## 💻 En pratique (Hugging Face)

```python
from transformers import ViTForImageClassification, ViTImageProcessor

proc = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

inputs = proc(images=mon_image, return_tensors="pt")
logits = model(**inputs).logits          # prédiction sur 1000 classes ImageNet
```

## ⚖️ ViT vs CNN

| | CNN | Vision Transformer |
|---|---|---|
| Biais intégré | localité (bords, textures) | aucun a priori → apprend tout |
| Besoin en données | modéré | **gros** (ou pré-entraînement massif) |
| Relations longue distance | indirect (couches profondes) | **direct** (attention) |
| Petit dataset | ✅ souvent meilleur | ❌ a besoin de transfer learning |

> 🛑 **Erreur courante** — entraîner un ViT *from scratch* sur un petit dataset : il sera **battu par un
> simple CNN**. Les ViT brillent avec **beaucoup de données** ou en **fine-tuning** d'un modèle pré-entraîné.

## ✅ À retenir
- Un ViT traite l'image comme une **séquence de patches** + **attention** (le Transformer du NLP appliqué à la vision).
- Fort sur les **relations globales**, mais **gourmand en données** → on l'utilise surtout **pré-entraîné**.
- C'est le pont entre la **vision** (module CNN) et les **Transformers** (module NLP).

## 🎥 Vidéos pour approfondir
| Vidéo | Chaîne | Langue | Ce que tu y apprends |
|---|---|:---:|---|
| [ViT expliqué](https://www.youtube.com/results?search_query=vision+transformer+explained+patches) | EN | EN | Patches, tokens, attention sur images |
| [ViT vs CNN](https://www.youtube.com/results?search_query=vision+transformer+vs+cnn) | EN | EN | Quand l'un bat l'autre |
