# AWS AI — Vue d'ensemble, IAM et SDK boto3

## Introduction

Les services d'IA d'Amazon Web Services se distinguent par leur intégration profonde dans l'écosystème AWS. Chaque service s'authentifie via **AWS IAM** (Identity and Access Management), stocke ses données dans **S3**, peut être déclenché par **Lambda**, et s'observe via **CloudWatch**.

Ce fichier couvre les bases indispensables avant de travailler avec n'importe quel service AWS AI : configuration IAM, SDK boto3, gestion des credentials et patterns d'architecture.

---

## Configuration IAM pour les services AI

### Principe du moindre privilège

En AWS, chaque appel API est autorisé ou refusé par IAM. La bonne pratique est de créer un utilisateur ou un rôle IAM avec uniquement les permissions nécessaires.

### Créer un utilisateur IAM dédié (développement)

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console AWS → IAM → Users → Create user → attacher les policies AmazonTextractFullAccess et AmazonRekognitionFullAccess → créer les Access Keys → télécharger le CSV.
> **Expliquer :** Insister sur le fait de ne JAMAIS partager ces clés, de ne pas les mettre dans le code source, et de préférer les rôles IAM (pas de clés à gérer) en production sur EC2/Lambda/ECS.
---

```bash
# Créer un utilisateur IAM via CLI
aws iam create-user --user-name formation-ai-user

# Créer des Access Keys
aws iam create-access-key --user-name formation-ai-user

# Attacher les policies nécessaires
aws iam attach-user-policy \
  --user-name formation-ai-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonTextractFullAccess

aws iam attach-user-policy \
  --user-name formation-ai-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonRekognitionReadOnlyAccess

aws iam attach-user-policy \
  --user-name formation-ai-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### Policy IAM personnalisée (principe du moindre privilège)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "TextractActions",
            "Effect": "Allow",
            "Action": [
                "textract:DetectDocumentText",
                "textract:AnalyzeDocument",
                "textract:StartDocumentTextDetection",
                "textract:GetDocumentTextDetection",
                "textract:StartDocumentAnalysis",
                "textract:GetDocumentAnalysis"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3ReadForTextract",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::mon-bucket-documents",
                "arn:aws:s3:::mon-bucket-documents/*"
            ]
        },
        {
            "Sid": "RekognitionAnalysis",
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectLabels",
                "rekognition:DetectText",
                "rekognition:AnalyzeFaces",
                "rekognition:RecognizeCelebrities"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Configuration des credentials AWS

### Option 1 : AWS CLI configure (développement local)

```bash
# Configuration interactive
aws configure

# Les informations demandées :
# AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# Default region name: eu-west-3
# Default output format: json
```

Les credentials sont stockés dans `~/.aws/credentials` :

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = eu-west-3

[formation]
aws_access_key_id = AUTRE_KEY
aws_secret_access_key = AUTRE_SECRET
region = eu-west-3
```

### Option 2 : Variables d'environnement

```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="eu-west-3"
```

### Option 3 : Fichier .env avec python-dotenv

```bash
# .env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=eu-west-3
```

```python
from dotenv import load_dotenv
load_dotenv()  # Charge le .env avant d'instancier les clients boto3
```

---

## Installation et configuration de boto3

```bash
pip install boto3
```

### Clients boto3 — pattern de base

```python
import boto3
import os

# Client pour une région spécifique
textract_client = boto3.client(
    "textract",
    region_name="eu-west-3",  # Paris
)

# Client avec credentials explicites (éviter en production)
rekognition_client = boto3.client(
    "rekognition",
    region_name="eu-west-3",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
)

# Utiliser un profil nommé
session = boto3.Session(profile_name="formation")
bedrock_client = session.client("bedrock-runtime", region_name="us-east-1")
```

---

## Amazon S3 — Stockage des documents

Tous les services AI AWS peuvent lire depuis S3. Voici les patterns courants :

### Upload d'un document vers S3

```python
import boto3
from pathlib import Path

s3_client = boto3.client("s3", region_name="eu-west-3")
BUCKET_NAME = "mon-bucket-documents-ai"

def upload_document(local_path: str, s3_key: str = None) -> str:
    """
    Upload un fichier vers S3 et retourne la clé S3.
    """
    if s3_key is None:
        s3_key = f"documents/{Path(local_path).name}"

    s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
    print(f"Uploadé : s3://{BUCKET_NAME}/{s3_key}")
    return s3_key


def upload_bytes(data: bytes, s3_key: str, content_type: str = "application/pdf") -> str:
    """
    Upload des bytes directement vers S3.
    """
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=data,
        ContentType=content_type
    )
    return s3_key


def download_document(s3_key: str, local_path: str) -> None:
    """
    Télécharge un fichier depuis S3.
    """
    s3_client.download_file(BUCKET_NAME, s3_key, local_path)
    print(f"Téléchargé : {local_path}")
```

---

## Gestion des erreurs AWS

Les erreurs AWS suivent un pattern cohérent via `botocore.exceptions` :

```python
import boto3
from botocore.exceptions import (
    ClientError,
    NoCredentialsError,
    BotoCoreError,
    EndpointConnectionError
)

def handle_aws_error(func):
    """Décorateur pour gérer les erreurs AWS courantes."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoCredentialsError:
            raise RuntimeError(
                "Credentials AWS non trouvés. "
                "Vérifiez AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY."
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if error_code == "AccessDeniedException":
                raise PermissionError(f"Accès refusé : {error_message}")
            elif error_code == "ResourceNotFoundException":
                raise FileNotFoundError(f"Ressource introuvable : {error_message}")
            elif error_code == "ThrottlingException":
                import time
                print(f"Throttling AWS, attente 5s...")
                time.sleep(5)
                return func(*args, **kwargs)  # Retry simple
            elif error_code == "InvalidS3ObjectException":
                raise ValueError(f"Objet S3 invalide : {error_message}")
            else:
                raise RuntimeError(f"Erreur AWS ({error_code}): {error_message}")
        except EndpointConnectionError:
            raise ConnectionError("Impossible de se connecter à AWS. Vérifiez la région et la connectivité réseau.")
        except BotoCoreError as e:
            raise RuntimeError(f"Erreur boto3 : {e}")
    return wrapper


# Usage
@handle_aws_error
def analyze_document(document_path: str) -> dict:
    # ... votre code
    pass
```

---

## Monitoring avec CloudWatch

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client("cloudwatch", region_name="eu-west-3")

def get_textract_metrics(hours: int = 24) -> dict:
    """
    Récupère les métriques Textract des dernières N heures.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    metrics = {}
    metric_names = ["SuccessfulRequestCount", "UserErrorCount", "ServerErrorCount"]

    for metric_name in metric_names:
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/Textract",
            MetricName=metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 heure
            Statistics=["Sum"]
        )
        total = sum(dp["Sum"] for dp in response["Datapoints"])
        metrics[metric_name] = total

    return metrics


# Voir les métriques
metrics = get_textract_metrics()
print(f"Textract (dernières 24h):")
print(f"  Requêtes réussies : {metrics['SuccessfulRequestCount']:.0f}")
print(f"  Erreurs client    : {metrics['UserErrorCount']:.0f}")
print(f"  Erreurs serveur   : {metrics['ServerErrorCount']:.0f}")
```

---

## Résumé des services et leurs régions

Avant de commencer à coder, vérifiez toujours la disponibilité régionale :

| Service | eu-west-1 | eu-west-3 | eu-central-1 |
|---------|-----------|-----------|--------------|
| Textract | Oui | Oui | Oui |
| Rekognition | Oui | Oui | Oui |
| Comprehend | Oui | Oui | Oui |
| Translate | Oui | Oui | Oui |
| Transcribe | Oui | Oui | Oui |
| Polly | Oui | Oui | Oui |
| Bedrock | Oui | Non | Oui |

---

## Ressources officielles

- AWS AI Services : [https://aws.amazon.com/machine-learning/ai-services/](https://aws.amazon.com/machine-learning/ai-services/)
- Documentation boto3 : [https://boto3.amazonaws.com/v1/documentation/api/latest/index.html](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- AWS Free Tier : [https://aws.amazon.com/free/](https://aws.amazon.com/free/)
- IAM Best Practices : [https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
