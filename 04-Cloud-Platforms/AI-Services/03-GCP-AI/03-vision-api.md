# Google Cloud Vision API — OCR, détection d'objets et analyse d'images

## Introduction

**Google Cloud Vision API** est l'API de vision par ordinateur de GCP. Elle est l'une des plus anciennes et des plus matures du marché, lancée en 2015. Elle permet d'analyser des images pour détecter des objets, du texte, des visages, des logos, des lieux, et bien plus.

La Vision API se distingue par ses très bonnes performances sur l'OCR multilingue (plus de 50 langues), sa détection de labels précise grâce aux modèles Google, et son intégration simple via l'API REST ou le SDK Python.

---

## Fonctionnalités (features)

| Feature | Constante | Description |
|---------|-----------|-------------|
| **OCR basique** | `TEXT_DETECTION` | Extrait tout le texte, retourne des mots |
| **OCR structuré** | `DOCUMENT_TEXT_DETECTION` | OCR orienté documents, préserve la structure |
| **Labels** | `LABEL_DETECTION` | Tags décrivant le contenu de l'image |
| **Objets** | `OBJECT_LOCALIZATION` | Localisation d'objets avec bounding boxes |
| **Visages** | `FACE_DETECTION` | Détection et attributs de visages |
| **Logos** | `LOGO_DETECTION` | Reconnaissance de logos de marques |
| **Landmarks** | `LANDMARK_DETECTION` | Identification de lieux célèbres |
| **Propriétés** | `IMAGE_PROPERTIES` | Couleurs dominantes, qualité |
| **Safe Search** | `SAFE_SEARCH_DETECTION` | Modération de contenu (adulte, violence...) |
| **Crop Hints** | `CROP_HINTS` | Suggestions de recadrage |
| **Web Detection** | `WEB_DETECTION` | Pages web contenant des images similaires |

---

## Installation et configuration

```bash
pip install google-cloud-vision
```

```python
from google.cloud import vision
import os

# Client Vision — utilise ADC ou GOOGLE_APPLICATION_CREDENTIALS
vision_client = vision.ImageAnnotatorClient()
```

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console GCP → APIs & Services → Cloud Vision API → "Try this API" ou utiliser le Vision API Explorer → uploader une photo contenant du texte et des objets → montrer les résultats pour TEXT_DETECTION et LABEL_DETECTION → comparer avec une photo d'une facture pour DOCUMENT_TEXT_DETECTION.
> **Expliquer :** Montrer la différence entre TEXT_DETECTION (mots isolés avec positions) et DOCUMENT_TEXT_DETECTION (texte structuré avec paragraphes). Pointer les confidence scores sur chaque label. Montrer aussi le résultat de SAFE_SEARCH_DETECTION sur une image anodine pour expliquer la modération automatique.
---

---

## Exemple 1 : OCR sur image

### TEXT_DETECTION vs DOCUMENT_TEXT_DETECTION

```python
def ocr_simple(image_path: str) -> str:
    """
    OCR standard : extraie tous les mots de l'image.
    Optimal pour les images naturelles avec peu de texte.
    """
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    texts = response.text_annotations
    if not texts:
        return ""

    # Le premier élément est le texte complet, les suivants sont les mots individuels
    full_text = texts[0].description
    print(f"Texte complet ({len(texts)-1} mots détectés):")
    return full_text


def ocr_document(image_path: str) -> dict:
    """
    OCR orienté document : préserve mieux la structure (paragraphes, blocs).
    Optimal pour les documents scannés, formulaires, factures.
    """
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = vision_client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    text_annotation = response.full_text_annotation

    result = {
        "full_text": text_annotation.text,
        "pages": []
    }

    for page in text_annotation.pages:
        page_data = {
            "blocks": [],
            "detected_languages": [
                {"language": lang.language_code, "confidence": lang.confidence}
                for lang in page.property.detected_languages
            ]
        }

        for block in page.blocks:
            block_text = ""
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    block_text += word_text + " "
                block_text += "\n"

            page_data["blocks"].append({
                "text": block_text.strip(),
                "confidence": block.confidence,
                "block_type": vision.Block.BlockType(block.block_type).name
            })

        result["pages"].append(page_data)

    return result


# Comparaison
print("=== TEXT_DETECTION ===")
text1 = ocr_simple("./images/document.jpg")
print(text1[:200])

print("\n=== DOCUMENT_TEXT_DETECTION ===")
result2 = ocr_document("./images/document.jpg")
print(result2["full_text"][:200])
```

---

## Exemple 2 : Détection de labels et d'objets

```python
def detect_labels_and_objects(image_path: str) -> dict:
    """
    Détecte les labels (tags) et les objets localisés dans une image.
    """
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)

    # Requête multi-features en un seul appel
    features = [
        vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=15),
        vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
        vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
    ]

    request = vision.AnnotateImageRequest(image=image, features=features)
    response = vision_client.annotate_image(request=request)

    # Labels
    labels = [
        {"description": label.description, "score": label.score, "topicality": label.topicality}
        for label in response.label_annotations
        if label.score > 0.7
    ]

    # Objets localisés
    objects = []
    for obj in response.localized_object_annotations:
        vertices = obj.bounding_poly.normalized_vertices
        objects.append({
            "name": obj.name,
            "score": obj.score,
            "bounding_box": {
                "x_min": vertices[0].x if vertices else 0,
                "y_min": vertices[0].y if vertices else 0,
                "x_max": vertices[2].x if len(vertices) > 2 else 1,
                "y_max": vertices[2].y if len(vertices) > 2 else 1,
            }
        })

    # Couleurs dominantes
    colors = []
    if response.image_properties_annotation:
        for color_info in response.image_properties_annotation.dominant_colors.colors[:3]:
            color = color_info.color
            colors.append({
                "rgb": (int(color.red), int(color.green), int(color.blue)),
                "score": color_info.score,
                "pixel_fraction": color_info.pixel_fraction
            })

    print(f"Labels (score > 70%) : {', '.join([l['description'] for l in labels])}")
    print(f"Objets localisés : {', '.join([o['name'] for o in objects])}")
    print(f"Couleurs dominantes : {colors}")

    return {"labels": labels, "objects": objects, "dominant_colors": colors}
```

---

## Exemple 3 : Détection de logos et de lieux

```python
def detect_logos_and_landmarks(image_path: str) -> dict:
    """
    Détecte les logos de marques et les lieux célèbres.
    Utile pour le brand monitoring et le géotagging automatique.
    """
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)

    features = [
        vision.Feature(type_=vision.Feature.Type.LOGO_DETECTION, max_results=5),
        vision.Feature(type_=vision.Feature.Type.LANDMARK_DETECTION, max_results=5),
    ]

    request = vision.AnnotateImageRequest(image=image, features=features)
    response = vision_client.annotate_image(request=request)

    logos = [
        {"name": logo.description, "score": logo.score}
        for logo in response.logo_annotations
    ]

    landmarks = []
    for landmark in response.landmark_annotations:
        lat_lng = None
        if landmark.locations:
            loc = landmark.locations[0].lat_lng
            lat_lng = {"lat": loc.latitude, "lng": loc.longitude}

        landmarks.append({
            "name": landmark.description,
            "score": landmark.score,
            "location": lat_lng
        })

    if logos:
        print(f"Logos détectés : {', '.join([l['name'] for l in logos])}")
    if landmarks:
        print(f"Lieux détectés : {', '.join([l['name'] for l in landmarks])}")

    return {"logos": logos, "landmarks": landmarks}
```

---

## Exemple 4 : Safe Search (modération de contenu)

```python
from google.cloud.vision import Likelihood

def check_safe_search(image_path: str) -> dict:
    """
    Vérifie si une image contient du contenu inapproprié.
    Retourne les niveaux de probabilité pour chaque catégorie.
    """
    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = vision_client.safe_search_detection(image=image)
    safe = response.safe_search_annotation

    # Likelihood : UNKNOWN, VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY
    def likelihood_str(likelihood_value) -> str:
        return Likelihood(likelihood_value).name

    result = {
        "adult": likelihood_str(safe.adult),
        "spoof": likelihood_str(safe.spoof),
        "medical": likelihood_str(safe.medical),
        "violence": likelihood_str(safe.violence),
        "racy": likelihood_str(safe.racy),
    }

    # Décision de modération
    unsafe_thresholds = {"POSSIBLE", "LIKELY", "VERY_LIKELY"}
    is_safe = not any(v in unsafe_thresholds for v in [result["adult"], result["violence"]])

    result["is_approved"] = is_safe

    print(f"Safe Search :")
    for category, level in result.items():
        if category != "is_approved":
            flag = "🔴" if level in unsafe_thresholds else "🟢"
            print(f"  {flag} {category:10s}: {level}")
    print(f"  Décision : {'APPROUVÉ' if is_safe else 'REJETÉ'}")

    return result
```

---

## Exemple 5 : Analyse d'une URL (sans télécharger l'image)

```python
def analyze_image_from_url(image_url: str) -> dict:
    """
    Analyse une image directement depuis une URL publique.
    Plus rapide que de télécharger et re-uploader l'image.
    """
    image = vision.Image(source=vision.ImageSource(image_uri=image_url))

    features = [
        vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
        vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
        vision.Feature(type_=vision.Feature.Type.SAFE_SEARCH_DETECTION),
    ]

    request = vision.AnnotateImageRequest(image=image, features=features)
    response = vision_client.annotate_image(request=request)

    return {
        "text": response.text_annotations[0].description if response.text_annotations else "",
        "labels": [l.description for l in response.label_annotations],
        "safe": {
            "adult": response.safe_search_annotation.adult,
            "violence": response.safe_search_annotation.violence
        }
    }


# Usage
result = analyze_image_from_url(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
)
print(f"Labels : {', '.join(result['labels'][:5])}")
```

---

## Traitement en lot via l'API REST (batch)

```python
def batch_annotate_images(image_paths: list[str]) -> list[dict]:
    """
    Traite plusieurs images en un seul appel API.
    Plus efficace que des appels individuels.
    Maximum 16 images par batch selon la documentation.
    """
    requests = []
    for image_path in image_paths[:16]:
        with open(image_path, "rb") as f:
            content = f.read()

        requests.append(
            vision.AnnotateImageRequest(
                image=vision.Image(content=content),
                features=[
                    vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=5),
                    vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                ]
            )
        )

    response = vision_client.batch_annotate_images(requests=requests)

    results = []
    for i, res in enumerate(response.responses):
        results.append({
            "image": image_paths[i],
            "labels": [l.description for l in res.label_annotations],
            "text": res.text_annotations[0].description if res.text_annotations else "",
            "error": res.error.message if res.error.message else None
        })

    return results


# Usage
image_dir = "./images/"
import os
images = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".jpg")]
results = batch_annotate_images(images)
for r in results:
    print(f"{os.path.basename(r['image'])}: {', '.join(r['labels'][:3])}")
```

---

## Comparaison Cloud Vision API vs Rekognition vs Azure Computer Vision

| Critère | GCP Cloud Vision | AWS Rekognition | Azure Computer Vision |
|---------|-----------------|------------------|-----------------------|
| **OCR multilingue** | Excellent (50+ langues) | Bon | Très bon (164 langues) |
| **Labels précision** | Excellent (modèles Google) | Très bon | Très bon (Florence) |
| **Détection de logos** | Oui (excellente) | Non | Non |
| **Détection de lieux** | Oui (Landmark) | Non | Oui |
| **Analyse vidéo** | Via Video Intelligence API | Oui (natif Rekognition) | Via Video Indexer |
| **Safe search** | 5 catégories | Nombreuses catégories | Oui |
| **Background removal** | Non | Non | Oui (Computer Vision 4.0) |
| **Free tier** | 1 000 unités/mois/feature | 1 000 images/mois (1 an) | 5 000 transactions/mois |
| **Prix standard** | ~1,50 $/1000 images | ~1,00 $/1000 images | ~1,00 $/1000 images |

---

## Ressources officielles

- Documentation Cloud Vision : [https://cloud.google.com/vision/docs](https://cloud.google.com/vision/docs)
- Vision API Explorer : [https://cloud.google.com/vision/docs/drag-and-drop](https://cloud.google.com/vision/docs/drag-and-drop)
- Fonctionnalités détaillées : [https://cloud.google.com/vision/docs/features-list](https://cloud.google.com/vision/docs/features-list)
- SDK Python : `pip install google-cloud-vision`
- Pricing : [https://cloud.google.com/vision/pricing](https://cloud.google.com/vision/pricing)
