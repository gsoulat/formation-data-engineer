# Amazon Textract — Extraction documentaire, tableaux et formulaires

## Introduction

**Amazon Textract** est le service AWS d'extraction de texte et de données structurées depuis des documents. Son nom vient de "text" + "extract". Là où un OCR traditionnel retourne du texte brut, Textract comprend la structure des documents et peut extraire :

- Le texte ligne par ligne
- Les **tableaux** (en préservant les lignes, colonnes et cellules)
- Les **formulaires** (paires clé-valeur comme "Nom : Jean Dupont")
- Les **signatures** (détection de présence)
- Les **requêtes personnalisées** (en langage naturel : "Quel est le numéro de commande ?")

---

## Modes d'opération

| Mode | API | Usage | Latence |
|------|-----|-------|---------|
| **Synchrone** | `DetectDocumentText` / `AnalyzeDocument` | Images JPEG/PNG, PDF 1 page | Immédiat (< 5s) |
| **Asynchrone** | `StartDocument*` + `GetDocument*` | PDF multi-pages, gros volumes | Quelques secondes à minutes |

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console AWS → Textract → "Try Amazon Textract" → uploader un PDF de facture ou un formulaire → montrer les onglets "Raw text", "Forms", "Tables" dans l'interface de démo → montrer le JSON brut de la réponse API.
> **Expliquer :** Insister sur la différence entre les trois modes de détection. Montrer visuellement comment Textract identifie les cellules d'un tableau et les paires clé-valeur d'un formulaire, avec les bounding boxes visibles dans l'interface.
---

---

## Installation

```bash
pip install boto3 amazon-textract-response-parser
```

La bibliothèque `amazon-textract-response-parser` simplifie le parsing de la réponse JSON de Textract, qui peut être assez verbeux.

---

## Configuration

```python
import boto3
import os

textract = boto3.client(
    "textract",
    region_name=os.environ.get("AWS_DEFAULT_REGION", "eu-west-3")
)

s3 = boto3.client("s3", region_name="eu-west-3")
BUCKET = os.environ.get("S3_BUCKET_NAME", "mon-bucket-documents")
```

---

## Exemple 1 : Extraction de texte brut (synchrone)

```python
def extract_text_sync(image_path: str) -> str:
    """
    Extrait le texte d'une image (JPEG/PNG) de manière synchrone.
    Idéal pour les images uniques traitement en temps réel.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = textract.detect_document_text(
        Document={"Bytes": image_bytes}
    )

    lines = []
    for block in response["Blocks"]:
        if block["BlockType"] == "LINE":
            lines.append(block["Text"])

    return "\n".join(lines)


# Usage
text = extract_text_sync("./images/photo_document.jpg")
print(f"Texte extrait ({len(text)} caractères):")
print(text[:500])
```

---

## Exemple 2 : Extraction de formulaires (paires clé-valeur)

```python
def extract_forms_sync(image_path: str) -> dict[str, str]:
    """
    Extrait les paires clé-valeur d'un formulaire (champs et leurs valeurs).
    Ex: {"Nom": "Jean Dupont", "Date de naissance": "01/01/1990"}
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = textract.analyze_document(
        Document={"Bytes": image_bytes},
        FeatureTypes=["FORMS"]
    )

    # Construire un index des blocs par ID
    blocks_by_id = {block["Id"]: block for block in response["Blocks"]}

    def get_text_from_block(block_id: str) -> str:
        """Récupère le texte d'un bloc WORD ou LINE."""
        block = blocks_by_id.get(block_id, {})
        if block.get("BlockType") in ["WORD", "LINE"]:
            return block.get("Text", "")
        elif block.get("BlockType") == "KEY_VALUE_SET":
            words = []
            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for child_id in rel["Ids"]:
                        words.append(get_text_from_block(child_id))
            return " ".join(words)
        return ""

    form_data = {}

    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", []):
            key_text = get_text_from_block(block["Id"])

            # Trouver la valeur associée
            value_text = ""
            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for value_id in rel["Ids"]:
                        value_block = blocks_by_id.get(value_id, {})
                        value_text = get_text_from_block(value_block["Id"])

            if key_text:
                form_data[key_text.strip()] = value_text.strip()

    return form_data


# Usage
form_data = extract_forms_sync("./images/formulaire.jpg")
print("Données du formulaire :")
for key, value in form_data.items():
    print(f"  {key}: {value}")
```

---

## Exemple 3 : Extraction de tableaux

```python
def extract_tables_sync(image_path: str) -> list[list[list[str]]]:
    """
    Extrait tous les tableaux d'un document.
    Retourne une liste de matrices (tableau → ligne → cellule).
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = textract.analyze_document(
        Document={"Bytes": image_bytes},
        FeatureTypes=["TABLES"]
    )

    blocks_by_id = {block["Id"]: block for block in response["Blocks"]}

    def get_cell_text(cell_block: dict) -> str:
        """Récupère le texte d'une cellule de tableau."""
        words = []
        for rel in cell_block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    child = blocks_by_id.get(child_id, {})
                    if child.get("BlockType") == "WORD":
                        words.append(child.get("Text", ""))
        return " ".join(words)

    tables = []

    for block in response["Blocks"]:
        if block["BlockType"] == "TABLE":
            # Trouver toutes les cellules de ce tableau
            cells = {}
            max_row = 0
            max_col = 0

            for rel in block.get("Relationships", []):
                if rel["Type"] == "CHILD":
                    for cell_id in rel["Ids"]:
                        cell_block = blocks_by_id.get(cell_id, {})
                        if cell_block.get("BlockType") == "CELL":
                            row = cell_block["RowIndex"]
                            col = cell_block["ColumnIndex"]
                            cells[(row, col)] = get_cell_text(cell_block)
                            max_row = max(max_row, row)
                            max_col = max(max_col, col)

            # Construire la matrice
            matrix = []
            for row in range(1, max_row + 1):
                row_data = []
                for col in range(1, max_col + 1):
                    row_data.append(cells.get((row, col), ""))
                matrix.append(row_data)

            tables.append(matrix)

    return tables


# Affichage tabulaire
def print_table(table: list[list[str]]) -> None:
    if not table:
        return
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]
    for i, row in enumerate(table):
        row_str = " | ".join(str(cell).ljust(col_widths[j]) for j, cell in enumerate(row))
        print(f"  {row_str}")
        if i == 0:
            print(f"  {'-' * len(row_str)}")


tables = extract_tables_sync("./images/rapport_avec_tableau.jpg")
print(f"{len(tables)} tableau(x) trouvé(s)")
for i, table in enumerate(tables):
    print(f"\nTableau {i+1} ({len(table)} lignes x {len(table[0]) if table else 0} colonnes):")
    print_table(table)
```

---

## Exemple 4 : Traitement asynchrone de PDFs multi-pages

Pour les PDFs multi-pages, Textract impose le mode asynchrone. Le document doit d'abord être uploadé sur S3.

```python
import time
import json

def start_document_analysis(s3_key: str, feature_types: list[str] = None) -> str:
    """
    Lance l'analyse asynchrone d'un document S3.
    Retourne le Job ID pour suivre la progression.
    """
    if feature_types is None:
        feature_types = ["TABLES", "FORMS"]

    response = textract.start_document_analysis(
        DocumentLocation={
            "S3Object": {
                "Bucket": BUCKET,
                "Name": s3_key
            }
        },
        FeatureTypes=feature_types,
        NotificationChannel={  # Optionnel : notification SNS à la fin
            "RoleArn": "arn:aws:iam::123456789:role/textract-role",
            "SNSTopicArn": "arn:aws:sns:eu-west-3:123456789:textract-done"
        } if False else None  # Activer si SNS configuré
    )

    job_id = response["JobId"]
    print(f"Job Textract lancé : {job_id}")
    return job_id


def wait_for_job(job_id: str, poll_interval: int = 5) -> dict:
    """
    Attend la fin du job Textract en polling.
    Retourne le résultat complet.
    """
    print(f"Attente du job {job_id}...")

    while True:
        response = textract.get_document_analysis(JobId=job_id)
        status = response["JobStatus"]

        if status == "SUCCEEDED":
            print(f"Job terminé avec succès.")
            return collect_all_pages(job_id)
        elif status == "FAILED":
            error = response.get("StatusMessage", "Erreur inconnue")
            raise RuntimeError(f"Job Textract échoué : {error}")
        elif status in ["IN_PROGRESS", "PARTIAL_SUCCESS"]:
            print(f"  Statut : {status}... attente {poll_interval}s")
            time.sleep(poll_interval)
        else:
            raise RuntimeError(f"Statut inattendu : {status}")


def collect_all_pages(job_id: str) -> list[dict]:
    """
    Récupère tous les blocs d'un job (gestion de la pagination AWS).
    AWS retourne max 1000 blocs par appel, il faut paginer avec NextToken.
    """
    all_blocks = []
    next_token = None

    while True:
        params = {"JobId": job_id, "MaxResults": 1000}
        if next_token:
            params["NextToken"] = next_token

        response = textract.get_document_analysis(**params)
        all_blocks.extend(response["Blocks"])

        next_token = response.get("NextToken")
        if not next_token:
            break

    print(f"Total blocs récupérés : {len(all_blocks)}")
    return all_blocks


def process_pdf_from_s3(pdf_local_path: str) -> dict:
    """
    Pipeline complet : upload → analyse asynchrone → récupération des résultats.
    """
    from pathlib import Path

    # 1. Upload vers S3
    s3_key = f"textract-input/{Path(pdf_local_path).name}"
    s3.upload_file(pdf_local_path, BUCKET, s3_key)
    print(f"Document uploadé : s3://{BUCKET}/{s3_key}")

    # 2. Lancer l'analyse
    job_id = start_document_analysis(s3_key, feature_types=["TABLES", "FORMS"])

    # 3. Attendre et récupérer
    blocks = wait_for_job(job_id)

    # 4. Parser les résultats
    results = {
        "total_blocks": len(blocks),
        "lines": [b["Text"] for b in blocks if b["BlockType"] == "LINE"],
        "tables_count": sum(1 for b in blocks if b["BlockType"] == "TABLE"),
        "key_value_pairs_count": sum(
            1 for b in blocks
            if b["BlockType"] == "KEY_VALUE_SET" and "KEY" in b.get("EntityTypes", [])
        )
    }

    return results


# Usage
results = process_pdf_from_s3("./documents/rapport_financier.pdf")
print(f"\nRésultats d'analyse :")
print(f"  Lignes de texte : {len(results['lines'])}")
print(f"  Tableaux : {results['tables_count']}")
print(f"  Paires clé-valeur : {results['key_value_pairs_count']}")
```

---

## Requêtes personnalisées (Queries)

La fonctionnalité **Queries** permet de poser des questions en langage naturel sur un document :

```python
def extract_with_queries(image_path: str, questions: list[str]) -> dict[str, str]:
    """
    Extrait des informations spécifiques en posant des questions au document.
    Beaucoup plus simple que de parser les blocs manuellement.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    queries = [{"Text": q, "Alias": f"q{i}"} for i, q in enumerate(questions)]

    response = textract.analyze_document(
        Document={"Bytes": image_bytes},
        FeatureTypes=["QUERIES"],
        QueriesConfig={"Queries": queries}
    )

    results = {}
    blocks_by_id = {b["Id"]: b for b in response["Blocks"]}

    for block in response["Blocks"]:
        if block["BlockType"] == "QUERY":
            question = block["Query"]["Text"]
            answer = ""

            for rel in block.get("Relationships", []):
                if rel["Type"] == "ANSWER":
                    for answer_id in rel["Ids"]:
                        answer_block = blocks_by_id.get(answer_id, {})
                        if answer_block.get("BlockType") == "QUERY_RESULT":
                            answer = answer_block.get("Text", "")
                            break

            results[question] = answer

    return results


# Usage sur une facture
questions = [
    "Quel est le numéro de facture ?",
    "Quelle est la date de la facture ?",
    "Quel est le montant total TTC ?",
    "Quel est le nom du fournisseur ?",
    "Quelle est l'adresse de livraison ?",
]

answers = extract_with_queries("./images/facture.jpg", questions)
print("Extraction par requêtes :")
for question, answer in answers.items():
    print(f"  Q: {question}")
    print(f"  R: {answer}\n")
```

---

## Comparaison : Textract vs Azure Document Intelligence vs Google Document AI

| Critère | Amazon Textract | Azure Doc Intelligence | Google Document AI |
|---------|----------------|----------------------|-------------------|
| **Modèles pré-entraînés** | Limités (général) | Nombreux (invoice, receipt, ID...) | Nombreux (form parser, invoice...) |
| **Requêtes en langage naturel** | Oui (Queries) | Non | Non |
| **Tableaux complexes** | Très bon | Excellent | Bon |
| **Prix par page (standard)** | ~0,0015 $ | ~0,001-0,01 $ | ~0,001-0,065 $ |
| **Intégration native** | S3, Lambda, Step Functions | Azure Blob, Logic Apps | GCS, Cloud Functions |
| **SDK Python** | boto3 | azure-ai-documentintelligence | google-cloud-documentai |

---

## Ressources officielles

- Documentation Textract : [https://docs.aws.amazon.com/textract/](https://docs.aws.amazon.com/textract/)
- Textract console (demo) : [https://us-east-1.console.aws.amazon.com/textract/home](https://us-east-1.console.aws.amazon.com/textract/home)
- amazon-textract-response-parser : [https://github.com/aws-samples/amazon-textract-response-parser](https://github.com/aws-samples/amazon-textract-response-parser)
- Pricing : [https://aws.amazon.com/textract/pricing/](https://aws.amazon.com/textract/pricing/)
