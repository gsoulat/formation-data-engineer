# Amazon Rekognition — Analyse d'images et de vidéos

## Introduction

**Amazon Rekognition** est le service AWS de vision par ordinateur. Il permet d'analyser des images et des vidéos pour détecter des objets, des textes, des visages, des activités et des contenus inappropriés, sans requérir de compétences en machine learning.

Rekognition est l'un des services AWS les plus matures dans ce domaine, utilisé dans des secteurs variés : e-commerce (catalogage automatique), médias (modération de contenu), sécurité (contrôle d'accès), et divertissement (analyse de vidéos).

---

## Fonctionnalités principales

| Fonctionnalité | API | Description |
|---------------|-----|-------------|
| **Détection d'objets et de scènes** | `DetectLabels` | Tags automatiques : "chien", "plage", "voiture"... |
| **OCR sur images** | `DetectText` | Extraction de texte depuis des images naturelles |
| **Analyse de visages** | `DetectFaces` | Âge estimé, émotions, lunettes, genre... |
| **Comparaison de visages** | `CompareFaces` | Mesure de similarité entre deux visages |
| **Collections de visages** | `IndexFaces` / `SearchFaces` | Reconnaissance faciale avec base de données |
| **Modération de contenu** | `DetectModerationLabels` | Détection de contenu adulte, violent, haineux |
| **Équipement de protection** | `DetectProtectiveEquipment` | Casques, masques, gants sur les lieux de travail |
| **Analyse de vidéo** | `StartLabelDetection` | Analyse asynchrone de vidéos depuis S3 |
| **Célébrités** | `RecognizeCelebrities` | Identification de personnalités publiques |

---

## Configuration

```python
import boto3
import os
import base64

rekognition = boto3.client(
    "rekognition",
    region_name=os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")
)

s3 = boto3.client("s3", region_name="eu-west-3")
BUCKET = os.environ.get("S3_BUCKET_NAME", "mon-bucket-images")
```

---

## Exemple 1 : Détection d'objets et de scènes

```python
def detect_labels(image_path: str, min_confidence: float = 70.0) -> list[dict]:
    """
    Détecte les objets, scènes et activités dans une image.
    Retourne les labels avec leur confiance et les bounding boxes si disponibles.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = rekognition.detect_labels(
        Image={"Bytes": image_bytes},
        MaxLabels=20,
        MinConfidence=min_confidence,
        Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"]  # Inclure les propriétés de couleur
    )

    labels = []
    for label in response["Labels"]:
        label_info = {
            "name": label["Name"],
            "confidence": label["Confidence"],
            "categories": [cat["Name"] for cat in label.get("Categories", [])],
            "parents": [p["Name"] for p in label.get("Parents", [])],
            "instances": []
        }

        # Bounding boxes si le label a des instances localisées
        for instance in label.get("Instances", []):
            bbox = instance.get("BoundingBox", {})
            label_info["instances"].append({
                "confidence": instance.get("Confidence", 0),
                "bounding_box": {
                    "left": bbox.get("Left", 0),
                    "top": bbox.get("Top", 0),
                    "width": bbox.get("Width", 0),
                    "height": bbox.get("Height", 0)
                }
            })

        labels.append(label_info)

    # Propriétés de l'image (couleurs dominantes)
    image_props = response.get("ImageProperties", {})
    if image_props:
        dominant_colors = [
            {
                "hex": color.get("HexCode", ""),
                "css": color.get("CSSColor", ""),
                "pixel_percent": color.get("PixelPercent", 0)
            }
            for color in image_props.get("DominantColors", [])[:3]
        ]

    print(f"Labels détectés ({len(labels)}) :")
    for label in sorted(labels, key=lambda l: l["confidence"], reverse=True):
        instances_str = f" ({len(label['instances'])} instance(s))" if label["instances"] else ""
        print(f"  {label['name']:30s} {label['confidence']:.1f}%{instances_str}")

    return labels


# Usage
labels = detect_labels("./images/scene_rue.jpg")
```

---

## Exemple 2 : Extraction de texte depuis des images

```python
def detect_text_in_image(image_path: str) -> dict:
    """
    Extrait le texte visible dans une image naturelle.
    Meilleur que Textract pour les photos de terrain (panneaux, affiches, etc.).
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = rekognition.detect_text(
        Image={"Bytes": image_bytes}
    )

    text_detections = response["TextDetections"]

    # Séparer les lignes et les mots
    lines = [t for t in text_detections if t["Type"] == "LINE"]
    words = [t for t in text_detections if t["Type"] == "WORD"]

    result = {
        "full_text": "\n".join([l["DetectedText"] for l in sorted(
            lines, key=lambda l: l["Geometry"]["BoundingBox"]["Top"]
        )]),
        "lines": [
            {
                "text": line["DetectedText"],
                "confidence": line["Confidence"],
                "position": line["Geometry"]["BoundingBox"]
            }
            for line in lines
        ],
        "word_count": len(words)
    }

    print(f"Texte extrait ({len(lines)} lignes, {len(words)} mots):")
    print(result["full_text"])

    return result


# Usage : photo d'un panneau de rue, d'une affiche publicitaire, d'un ticket
text_result = detect_text_in_image("./images/panneau_rue.jpg")
```

---

## Exemple 3 : Analyse de visages

```python
def analyze_faces(image_path: str) -> list[dict]:
    """
    Analyse les attributs des visages détectés dans l'image.
    Utile pour les analytics d'audience, la vérification d'identité, etc.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = rekognition.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"]  # "DEFAULT" pour les attributs de base uniquement
    )

    faces = []
    for i, face in enumerate(response["FaceDetails"]):
        # Émotions détectées
        emotions = sorted(
            face.get("Emotions", []),
            key=lambda e: e["Confidence"],
            reverse=True
        )
        top_emotion = emotions[0] if emotions else {"Type": "UNKNOWN", "Confidence": 0}

        # Attributs
        face_info = {
            "face_id": i + 1,
            "confidence": face["Confidence"],
            "age_range": {
                "low": face.get("AgeRange", {}).get("Low", 0),
                "high": face.get("AgeRange", {}).get("High", 0)
            },
            "emotion": top_emotion["Type"],
            "emotion_confidence": top_emotion["Confidence"],
            "gender": face.get("Gender", {}).get("Value", ""),
            "gender_confidence": face.get("Gender", {}).get("Confidence", 0),
            "smile": face.get("Smile", {}).get("Value", False),
            "eyeglasses": face.get("Eyeglasses", {}).get("Value", False),
            "sunglasses": face.get("Sunglasses", {}).get("Value", False),
            "beard": face.get("Beard", {}).get("Value", False),
            "mustache": face.get("Mustache", {}).get("Value", False),
            "eyes_open": face.get("EyesOpen", {}).get("Value", False),
            "mouth_open": face.get("MouthOpen", {}).get("Value", False),
            "face_occluded": face.get("FaceOccluded", {}).get("Value", False),
            "bounding_box": face.get("BoundingBox", {})
        }

        faces.append(face_info)

        # Affichage
        print(f"\nVisage {i+1} (confiance: {face_info['confidence']:.1f}%) :")
        print(f"  Âge estimé : {face_info['age_range']['low']}-{face_info['age_range']['high']} ans")
        print(f"  Émotion    : {face_info['emotion']} ({face_info['emotion_confidence']:.1f}%)")
        print(f"  Sourire    : {'Oui' if face_info['smile'] else 'Non'}")

    return faces


# ATTENTION RGPD : L'analyse faciale est une donnée biométrique
# Nécessite consentement explicite en Europe
faces = analyze_faces("./images/portrait.jpg")
```

---

## Exemple 4 : Modération de contenu

```python
def moderate_content(image_path: str, threshold: float = 50.0) -> dict:
    """
    Vérifie si une image contient du contenu inapproprié.
    Utilisé pour la modération de plateformes UGC (user-generated content).
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = rekognition.detect_moderation_labels(
        Image={"Bytes": image_bytes},
        MinConfidence=threshold
    )

    moderation_labels = response.get("ModerationLabels", [])

    # Organiser par catégorie parente
    categories = {}
    for label in moderation_labels:
        parent = label.get("ParentName", "Autre")
        if parent not in categories:
            categories[parent] = []
        categories[parent].append({
            "name": label["Name"],
            "confidence": label["Confidence"]
        })

    result = {
        "is_safe": len(moderation_labels) == 0,
        "labels_count": len(moderation_labels),
        "categories": categories
    }

    if result["is_safe"]:
        print("Image approuvée - Aucun contenu inapproprié détecté")
    else:
        print(f"Image signalée - {len(moderation_labels)} label(s) de modération :")
        for category, labels in categories.items():
            print(f"  {category}:")
            for label in labels:
                print(f"    - {label['name']} ({label['confidence']:.1f}%)")

    return result


# Pipeline de modération avant publication
def auto_moderate_upload(image_path: str) -> bool:
    """
    Retourne True si l'image est approuvée pour publication.
    """
    result = moderate_content(image_path, threshold=60.0)

    if not result["is_safe"]:
        # Logger pour revue manuelle
        print(f"REJETÉ : {image_path} — mise en queue de revue manuelle")
        return False

    return True
```

---

## Exemple 5 : Analyse de vidéo (asynchrone)

```python
import time

def analyze_video_labels(s3_video_key: str) -> list[dict]:
    """
    Analyse les labels d'une vidéo stockée sur S3.
    La vidéo est traitée de manière asynchrone.
    """
    # Lancer l'analyse
    response = rekognition.start_label_detection(
        Video={
            "S3Object": {
                "Bucket": BUCKET,
                "Name": s3_video_key
            }
        },
        MinConfidence=70.0,
        Features=["GENERAL_LABELS"]
    )

    job_id = response["JobId"]
    print(f"Analyse vidéo lancée : {job_id}")

    # Attendre la fin
    while True:
        result = rekognition.get_label_detection(
            JobId=job_id,
            SortBy="TIMESTAMP"
        )
        status = result["JobStatus"]

        if status == "SUCCEEDED":
            print(f"Analyse terminée - {len(result['Labels'])} détections")
            break
        elif status == "FAILED":
            raise RuntimeError(f"Analyse vidéo échouée : {result.get('StatusMessage')}")
        else:
            print(f"  En cours... attente 10s")
            time.sleep(10)

    # Résumer les labels par temps
    labels_timeline = []
    for detection in result["Labels"]:
        labels_timeline.append({
            "timestamp_ms": detection["Timestamp"],
            "label": detection["Label"]["Name"],
            "confidence": detection["Label"]["Confidence"],
            "time_formatted": f"{detection['Timestamp'] // 1000}s"
        })

    return labels_timeline


# Générer un résumé de vidéo
def summarize_video(s3_video_key: str) -> dict:
    """
    Génère un résumé textuel du contenu d'une vidéo.
    """
    detections = analyze_video_labels(s3_video_key)

    # Agréger les labels uniques
    from collections import Counter
    label_counts = Counter(d["label"] for d in detections)

    # Top 10 objets/scènes les plus présents
    top_labels = label_counts.most_common(10)

    summary = {
        "total_detections": len(detections),
        "duration_seconds": max(d["timestamp_ms"] for d in detections) / 1000 if detections else 0,
        "top_content": [{"label": l, "occurrences": c} for l, c in top_labels]
    }

    print(f"\nRésumé de la vidéo :")
    print(f"Durée analysée : {summary['duration_seconds']:.0f}s")
    print("Contenu principal :")
    for item in summary["top_content"][:5]:
        print(f"  {item['label']:30s} — {item['occurrences']} détection(s)")

    return summary
```

---

## Considérations RGPD et éthique

### Analyse faciale en Europe

L'analyse faciale constitue un **traitement de données biométriques** au sens du RGPD (article 9). Les obligations sont strictes :

- Consentement **explicite** et **éclairé** de la personne
- Base légale documentée (consentement, intérêt légitime, obligation légale...)
- Droit d'opposition respecté
- Durée de conservation limitée
- Documentation dans le registre des traitements (CNIL)

```python
# Bonne pratique : logger tous les traitements de données biométriques
import logging
from datetime import datetime

biometric_logger = logging.getLogger("biometric_audit")

def logged_face_analysis(image_id: str, purpose: str, consent_id: str) -> list[dict]:
    """
    Analyse faciale avec traçabilité pour conformité RGPD.
    """
    biometric_logger.info(
        f"BIOMETRIC_PROCESSING | image={image_id} | "
        f"purpose={purpose} | consent={consent_id} | "
        f"timestamp={datetime.utcnow().isoformat()}"
    )

    # ... appel réel à Rekognition
    return []
```

### AWS Rekognition et reconnaissance faciale

Amazon a imposé en 2020 un **moratoire d'un an** sur la vente de Rekognition aux forces de l'ordre, suite aux controverses sur les biais raciaux. Ce moratoire a ensuite évolué en politique permanente.

Prenez en compte ces limitations dans vos choix d'architecture pour les projets sensibles.

---

## Ressources officielles

- Documentation Rekognition : [https://docs.aws.amazon.com/rekognition/](https://docs.aws.amazon.com/rekognition/)
- Best practices (visage) : [https://docs.aws.amazon.com/rekognition/latest/dg/best-practices-visage.html](https://docs.aws.amazon.com/rekognition/latest/dg/best-practices-visage.html)
- Pricing : [https://aws.amazon.com/rekognition/pricing/](https://aws.amazon.com/rekognition/pricing/)
