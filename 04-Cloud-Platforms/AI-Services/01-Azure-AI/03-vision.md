# Azure Computer Vision — OCR et Analyse d'images

## Introduction

**Azure Computer Vision** est le service de vision par ordinateur d'Azure. Il permet d'analyser des images et des documents visuels pour en extraire du sens : texte, objets, personnes, scènes, couleurs, et bien plus.

Depuis 2023, Microsoft a intégré le modèle **Florence** (son modèle de vision fondational) dans Computer Vision, améliorant considérablement les performances sur les tâches de description d'images et de recherche visuelle.

---

## Fonctionnalités principales

| Fonctionnalité | Description | Use case |
|---------------|-------------|----------|
| **OCR (Read API)** | Extraction de texte depuis images/PDFs | Numérisation de documents, plaques, panneaux |
| **Image Analysis** | Description, tags, objets, personnes | Catalogage automatique, modération |
| **Smart Crops** | Recadrage intelligent orienté sur le sujet | Vignettes pour sites web |
| **Object Detection** | Localisation d'objets avec bounding boxes | Inventaire, contrôle qualité |
| **Image Captioning** | Description textuelle automatique d'une image | Accessibilité, recherche visuelle |
| **Background Removal** | Suppression du fond d'une image | E-commerce, photos produits |

---

## Installation

```bash
pip install azure-cognitiveservices-vision-computervision azure-ai-vision-imageanalysis
```

> Note : Il existe deux SDK selon la version de l'API :
> - `azure-cognitiveservices-vision-computervision` : SDK legacy (API v3.2)
> - `azure-ai-vision-imageanalysis` : SDK nouvelle génération (API 2024-02-01)
> Les exemples ci-dessous utilisent le nouveau SDK.

---

## Configuration

```python
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["AZURE_VISION_ENDPOINT"]
key = os.environ["AZURE_VISION_KEY"]

client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Portail Azure → ouvrir la ressource Computer Vision → "Try it out" ou "Vision Studio" → uploader une photo contenant du texte (photo d'une affiche, d'un document, d'un panneau de rue) → montrer les résultats OCR en temps réel dans l'interface → puis tester l'analyse d'image classique sur une photo de paysage ou de produit.
> **Expliquer :** Pointer les bounding boxes sur le texte détecté, les confidence scores, et la différence entre l'OCR orienté document (Document Intelligence) et l'OCR orienté image naturelle (Computer Vision Read API). Montrer aussi la section "tags" et "objects" sur une photo standard.
---

---

## OCR — Extraction de texte depuis des images

### Utilisation simple

```python
def ocr_from_image_url(image_url: str) -> str:
    """
    Extrait le texte d'une image accessible via URL.
    """
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.READ]
    )

    if result.read is None:
        return ""

    lines = []
    for block in result.read.blocks:
        for line in block.lines:
            lines.append(line.text)

    return "\n".join(lines)


# Exemple avec une image de texte
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Bill_of_Rights_Pg1of1_AC.jpg/800px-Bill_of_Rights_Pg1of1_AC.jpg"
text = ocr_from_image_url(url)
print(text[:300])
```

### OCR depuis un fichier local avec positions

```python
def ocr_with_positions(image_path: str) -> list[dict]:
    """
    Extrait le texte avec les positions (bounding boxes) de chaque mot.
    Utile pour reconstruire la mise en page ou extraire des zones spécifiques.
    """
    with open(image_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.READ]
    )

    words_with_positions = []

    if result.read:
        for block in result.read.blocks:
            for line in block.lines:
                for word in line.words:
                    words_with_positions.append({
                        "text": word.text,
                        "confidence": word.confidence,
                        "bounding_box": {
                            "x": word.bounding_polygon[0].x,
                            "y": word.bounding_polygon[0].y,
                            "width": word.bounding_polygon[2].x - word.bounding_polygon[0].x,
                            "height": word.bounding_polygon[2].y - word.bounding_polygon[0].y,
                        }
                    })

    return words_with_positions


# Usage
words = ocr_with_positions("./images/photo_document.jpg")
print(f"Mots détectés : {len(words)}")
for word in words[:10]:
    print(f"  '{word['text']}' (confiance: {word['confidence']:.2%}) "
          f"à ({word['bounding_box']['x']:.0f}, {word['bounding_box']['y']:.0f})")
```

---

## Analyse d'images — Détection d'objets et description

### Description et tags automatiques

```python
def analyze_image_full(image_path: str) -> dict:
    """
    Analyse complète d'une image : description, tags, objets, personnes.
    """
    with open(image_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[
            VisualFeatures.CAPTION,
            VisualFeatures.DENSE_CAPTIONS,
            VisualFeatures.TAGS,
            VisualFeatures.OBJECTS,
            VisualFeatures.PEOPLE,
            VisualFeatures.READ,
            VisualFeatures.SMART_CROPS,
        ],
        gender_neutral_caption=True,  # Légendes sans biais de genre
        language="fr"  # Sortie en français si disponible
    )

    analysis = {}

    # Caption principale
    if result.caption:
        analysis["description"] = {
            "text": result.caption.text,
            "confidence": result.caption.confidence
        }
        print(f"Description : {result.caption.text} ({result.caption.confidence:.2%})")

    # Tags
    if result.tags:
        analysis["tags"] = [
            {"name": t.name, "confidence": t.confidence}
            for t in result.tags.list
            if t.confidence > 0.7  # Filtrer les tags peu fiables
        ]
        tag_names = [t["name"] for t in analysis["tags"]]
        print(f"Tags (confiance > 70%) : {', '.join(tag_names)}")

    # Objets détectés
    if result.objects:
        analysis["objects"] = []
        for obj in result.objects.list:
            analysis["objects"].append({
                "name": obj.tags[0].name if obj.tags else "unknown",
                "confidence": obj.tags[0].confidence if obj.tags else 0,
                "bounding_box": {
                    "x": obj.bounding_box.x,
                    "y": obj.bounding_box.y,
                    "w": obj.bounding_box.width,
                    "h": obj.bounding_box.height
                }
            })
        print(f"Objets détectés : {len(analysis['objects'])}")
        for obj in analysis["objects"]:
            print(f"  - {obj['name']} ({obj['confidence']:.2%})")

    # Personnes détectées
    if result.people:
        analysis["people_count"] = len(result.people.list)
        print(f"Personnes détectées : {analysis['people_count']}")

    return analysis
```

### Légendes détaillées (Dense Captions)

```python
def get_dense_captions(image_path: str) -> list[dict]:
    """
    Génère des descriptions pour différentes zones de l'image.
    Utile pour l'accessibilité ou la recherche visuelle granulaire.
    """
    with open(image_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.DENSE_CAPTIONS]
    )

    captions = []
    if result.dense_captions:
        for caption in result.dense_captions.list:
            captions.append({
                "text": caption.text,
                "confidence": caption.confidence,
                "region": {
                    "x": caption.bounding_box.x,
                    "y": caption.bounding_box.y,
                    "width": caption.bounding_box.width,
                    "height": caption.bounding_box.height
                }
            })

    return sorted(captions, key=lambda c: c["confidence"], reverse=True)
```

---

## Suppression de fond (Background Removal)

Fonctionnalité utile pour l'e-commerce et la mise en scène de produits :

```python
import requests

def remove_background(image_path: str, output_path: str) -> None:
    """
    Supprime le fond d'une image.
    Le résultat est une image PNG avec fond transparent.
    """
    endpoint = os.environ["AZURE_VISION_ENDPOINT"]
    key = os.environ["AZURE_VISION_KEY"]

    api_url = f"{endpoint}computervision/imageanalysis:segment"
    params = {
        "api-version": "2023-02-01-preview",
        "mode": "backgroundRemoval"  # ou "foregroundMatting"
    }
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "image/jpeg"
    }

    with open(image_path, "rb") as f:
        image_data = f.read()

    response = requests.post(api_url, params=params, headers=headers, data=image_data)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Image sans fond sauvegardée : {output_path}")


# Usage
remove_background("./images/produit.jpg", "./images/produit_sans_fond.png")
```

---

## Cas d'usage avancé : pipeline OCR sur dossier d'images

```python
import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_image_folder(folder: str, output_json: str) -> None:
    """
    Traite toutes les images d'un dossier et génère un JSON de résultats.
    Utilise le multithreading pour accélérer le traitement.
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    image_files = [
        p for p in Path(folder).iterdir()
        if p.suffix.lower() in image_extensions
    ]

    print(f"Traitement de {len(image_files)} images avec 4 threads...")

    results = {}

    def process_single(image_path: Path) -> tuple[str, dict]:
        with open(image_path, "rb") as f:
            image_data = f.read()

        analysis_result = client.analyze(
            image_data=image_data,
            visual_features=[VisualFeatures.READ, VisualFeatures.TAGS, VisualFeatures.CAPTION]
        )

        extracted = {
            "text": "",
            "caption": "",
            "tags": []
        }

        if analysis_result.read:
            lines = []
            for block in analysis_result.read.blocks:
                for line in block.lines:
                    lines.append(line.text)
            extracted["text"] = "\n".join(lines)

        if analysis_result.caption:
            extracted["caption"] = analysis_result.caption.text

        if analysis_result.tags:
            extracted["tags"] = [t.name for t in analysis_result.tags.list if t.confidence > 0.8]

        return image_path.name, extracted

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_single, img): img for img in image_files}

        for future in as_completed(futures):
            filename, data = future.result()
            results[filename] = data
            print(f"  Traité : {filename}")

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nRésultats sauvegardés dans : {output_json}")


# Usage
process_image_folder("./photos_produits/", "./resultats_ocr.json")
```

---

## Comparaison : Computer Vision Read API vs Document Intelligence

| Critère | Computer Vision Read API | Document Intelligence |
|---------|--------------------------|----------------------|
| **Optimisé pour** | Images naturelles, photos | Documents PDF, formulaires |
| **Structure extraite** | Texte brut + positions | Tableaux, paires clé-valeur, champs sémantiques |
| **Modèles spécialisés** | Non | Oui (invoice, receipt, ID...) |
| **Langues** | 164 langues | 73 langues |
| **Prix (F0)** | 5 000 transactions/mois | 500 pages/mois |
| **Prix production** | ~1,50 $/1000 images | ~0,01 $/page (Read) |
| **Latence** | Faible (synchrone) | Variable (async pour PDF multi-pages) |
| **Idéal pour** | Photos de terrain, OCR live | Traitement de masse de documents |

---

## Vision Studio — Interface no-code

Microsoft propose **Vision Studio** ([vision.azure.com](https://vision.azure.com)) pour tester toutes les fonctionnalités sans écrire de code :

1. Connectez votre ressource Azure Computer Vision
2. Sélectionnez une fonctionnalité (OCR, analyse, suppression de fond...)
3. Uploadez une image ou entrez une URL
4. Visualisez les résultats et le JSON de réponse

---

## Ressources officielles

- Documentation Azure Computer Vision : [https://docs.microsoft.com/azure/cognitive-services/computer-vision/](https://docs.microsoft.com/azure/cognitive-services/computer-vision/)
- Vision Studio : [https://vision.azure.com](https://vision.azure.com)
- SDK Python : `pip install azure-ai-vision-imageanalysis`
- Quickstart officiel : [https://learn.microsoft.com/azure/ai-services/computer-vision/quickstarts-sdk/image-analysis-client-library-40](https://learn.microsoft.com/azure/ai-services/computer-vision/quickstarts-sdk/image-analysis-client-library-40)
