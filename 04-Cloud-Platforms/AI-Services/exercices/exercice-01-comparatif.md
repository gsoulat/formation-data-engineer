# Exercice 01 — Comparatif OCR multi-cloud

## Contexte

Vous travaillez pour une PME française qui reçoit chaque mois plusieurs centaines de factures fournisseurs au format PDF. L'équipe comptable passe actuellement 2 heures par jour à saisir manuellement les données (numéro de facture, fournisseur, montant HT/TTC, date d'échéance) dans leur ERP.

La direction vous demande d'évaluer les services d'IA cloud pour automatiser cette extraction. Vous devez comparer Azure Document Intelligence, Amazon Textract et Google Document AI sur la même tâche.

---

## Objectifs

- Consommer les trois APIs sur un document commun
- Comparer les résultats (complétude, précision, confiance)
- Comparer les performances (temps de réponse, facilité d'intégration)
- Rédiger une recommandation argumentée

---

## Prérequis

- Python 3.10+
- Un compte sur au moins **deux** des trois providers (idéalement les trois)
- Un fichier PDF de facture de test (vous pouvez utiliser [ce PDF de demo](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf))
- Les variables d'environnement configurées

```bash
# Azure
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="https://..."
export AZURE_DOCUMENT_INTELLIGENCE_KEY="..."

# AWS
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="eu-west-3"
export S3_BUCKET_NAME="mon-bucket-ocr-test"

# GCP
export GCP_PROJECT_ID="mon-projet"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"
export GCP_DOCAI_PROCESSOR_ID="..."  # ID de votre processeur Invoice Parser
```

---

## Partie 1 — Mise en place

### 1.1 Installation des dépendances

```bash
pip install azure-ai-documentintelligence boto3 google-cloud-documentai
pip install python-dotenv pandas tabulate time
```

### 1.2 Préparer le document de test

Téléchargez une facture de test ou utilisez l'une de vos factures (pensez à anonymiser les données sensibles si vous l'uploadez sur des services cloud tiers).

Pour les tests, vous pouvez utiliser cet exemple de facture disponible publiquement :

```python
import requests
from pathlib import Path

SAMPLE_INVOICE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"

def download_sample_invoice(output_path: str = "./test_invoice.pdf") -> str:
    """Télécharge la facture de demo Microsoft."""
    response = requests.get(SAMPLE_INVOICE_URL)
    Path(output_path).write_bytes(response.content)
    print(f"Facture téléchargée : {output_path} ({len(response.content)} bytes)")
    return output_path

invoice_path = download_sample_invoice()
```

---

## Partie 2 — Extraction avec chaque service

### 2.1 Azure Document Intelligence

```python
import os
import time
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

def extract_with_azure(pdf_path: str) -> dict:
    """
    Extrait les données de facture avec Azure Document Intelligence.
    Retourne un dict standardisé avec les champs principaux et le temps d'exécution.
    """
    client = DocumentIntelligenceClient(
        endpoint=os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"])
    )

    start = time.time()

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        analyze_request=pdf_bytes,
        content_type="application/octet-stream"
    )
    result = poller.result()

    elapsed = time.time() - start

    # Normaliser les résultats
    extracted = {
        "provider": "Azure Document Intelligence",
        "duration_seconds": round(elapsed, 2),
        "fields": {},
        "raw_fields_count": 0
    }

    if result.documents:
        doc = result.documents[0]
        extracted["raw_fields_count"] = len(doc.fields)

        field_mapping = {
            "VendorName": "vendor_name",
            "InvoiceId": "invoice_number",
            "InvoiceDate": "invoice_date",
            "DueDate": "due_date",
            "SubTotal": "subtotal",
            "TotalTax": "tax_amount",
            "InvoiceTotal": "total_amount",
            "CustomerName": "customer_name",
        }

        for azure_field, standard_field in field_mapping.items():
            field = doc.fields.get(azure_field)
            if field:
                extracted["fields"][standard_field] = {
                    "value": str(field.content or ""),
                    "confidence": round(field.confidence or 0, 3)
                }

    return extracted
```

### 2.2 Amazon Textract

```python
import boto3
import time

def extract_with_textract(pdf_path: str, bucket_name: str) -> dict:
    """
    Extrait les données de facture avec Amazon Textract.
    Utilise les Queries pour cibler les champs importants.
    """
    textract = boto3.client("textract", region_name=os.environ.get("AWS_DEFAULT_REGION", "eu-west-3"))
    s3 = boto3.client("s3", region_name="eu-west-3")

    # Upload vers S3
    s3_key = f"ocr-test/invoice_{int(time.time())}.pdf"
    s3.upload_file(pdf_path, bucket_name, s3_key)

    start = time.time()

    # Requêtes ciblées
    queries = [
        {"Text": "What is the vendor name?", "Alias": "vendor_name"},
        {"Text": "What is the invoice number?", "Alias": "invoice_number"},
        {"Text": "What is the invoice date?", "Alias": "invoice_date"},
        {"Text": "What is the due date?", "Alias": "due_date"},
        {"Text": "What is the subtotal?", "Alias": "subtotal"},
        {"Text": "What is the tax amount?", "Alias": "tax_amount"},
        {"Text": "What is the total amount?", "Alias": "total_amount"},
        {"Text": "What is the customer name?", "Alias": "customer_name"},
    ]

    response = textract.analyze_document(
        Document={"S3Object": {"Bucket": bucket_name, "Name": s3_key}},
        FeatureTypes=["QUERIES", "FORMS"],
        QueriesConfig={"Queries": queries}
    )

    elapsed = time.time() - start

    # Parser les résultats
    blocks_by_id = {b["Id"]: b for b in response["Blocks"]}
    extracted = {
        "provider": "Amazon Textract",
        "duration_seconds": round(elapsed, 2),
        "fields": {},
        "raw_fields_count": len([b for b in response["Blocks"] if b["BlockType"] == "QUERY"])
    }

    for block in response["Blocks"]:
        if block["BlockType"] == "QUERY":
            alias = block["Query"].get("Alias", "unknown")
            answer_text = ""
            confidence = 0

            for rel in block.get("Relationships", []):
                if rel["Type"] == "ANSWER":
                    for answer_id in rel["Ids"]:
                        answer_block = blocks_by_id.get(answer_id, {})
                        if answer_block.get("BlockType") == "QUERY_RESULT":
                            answer_text = answer_block.get("Text", "")
                            confidence = answer_block.get("Confidence", 0) / 100

            if answer_text:
                extracted["fields"][alias] = {
                    "value": answer_text,
                    "confidence": round(confidence, 3)
                }

    return extracted
```

### 2.3 Google Document AI

```python
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
import time

def extract_with_docai(pdf_path: str) -> dict:
    """
    Extrait les données de facture avec Google Document AI (Invoice Parser).
    """
    project_id = os.environ["GCP_PROJECT_ID"]
    processor_id = os.environ["GCP_DOCAI_PROCESSOR_ID"]
    location = "eu"

    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    processor_name = client.processor_path(project_id, location, processor_id)

    with open(pdf_path, "rb") as f:
        content = f.read()

    start = time.time()

    result = client.process_document(request=documentai.ProcessRequest(
        name=processor_name,
        raw_document=documentai.RawDocument(content=content, mime_type="application/pdf")
    ))

    elapsed = time.time() - start

    # Normaliser les résultats
    entity_mapping = {
        "supplier_name": "vendor_name",
        "invoice_id": "invoice_number",
        "invoice_date": "invoice_date",
        "due_date": "due_date",
        "net_amount": "subtotal",
        "total_tax_amount": "tax_amount",
        "total_amount": "total_amount",
        "receiver_name": "customer_name",
    }

    extracted = {
        "provider": "Google Document AI",
        "duration_seconds": round(elapsed, 2),
        "fields": {},
        "raw_fields_count": len(result.document.entities)
    }

    for entity in result.document.entities:
        standard_field = entity_mapping.get(entity.type_, entity.type_)
        if not entity.properties:  # Champs simples uniquement
            extracted["fields"][standard_field] = {
                "value": entity.mention_text,
                "confidence": round(entity.confidence, 3)
            }

    return extracted
```

---

## Partie 3 — Comparaison et analyse

### 3.1 Grille de comparaison

Complétez ce tableau après avoir exécuté les trois extractions :

```python
import pandas as pd
from tabulate import tabulate

def compare_results(results: list[dict]) -> pd.DataFrame:
    """
    Génère une grille de comparaison des résultats.
    """
    standard_fields = [
        "vendor_name", "invoice_number", "invoice_date",
        "due_date", "subtotal", "tax_amount", "total_amount", "customer_name"
    ]

    rows = []
    for field in standard_fields:
        row = {"Champ": field}
        for result in results:
            provider = result["provider"].split()[0]  # Azure, Amazon, Google
            field_data = result["fields"].get(field)
            if field_data:
                row[f"{provider}_valeur"] = field_data["value"][:30]
                row[f"{provider}_confiance"] = f"{field_data['confidence']:.1%}"
            else:
                row[f"{provider}_valeur"] = "NON EXTRAIT"
                row[f"{provider}_confiance"] = "-"
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


# Exécution (adapter selon les providers disponibles)
results = []

# Décommenter selon les providers configurés :
# results.append(extract_with_azure("./test_invoice.pdf"))
# results.append(extract_with_textract("./test_invoice.pdf", os.environ["S3_BUCKET_NAME"]))
# results.append(extract_with_docai("./test_invoice.pdf"))

if results:
    df = compare_results(results)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))

    # Afficher les métriques de performance
    print("\n=== Performances ===")
    for r in results:
        print(f"{r['provider']:40s} | Durée: {r['duration_seconds']}s | Champs: {r['raw_fields_count']}")
```

---

## Partie 4 — Questions d'analyse

Répondez à ces questions en vous basant sur vos résultats :

### Questions sur les résultats

1. **Complétude** : Quel service a extrait le plus grand nombre de champs ? Tous les champs importants ont-ils été extraits par chaque service ?

2. **Précision** : Comparez les valeurs extraites. Y a-t-il des différences entre les providers sur un même champ ? Lequel semble le plus précis ?

3. **Confiance** : Analysez les scores de confiance. Un score élevé correspond-il toujours à une valeur correcte ? Que faire quand la confiance est basse ?

4. **Performance** : Quel service répond le plus rapidement ? Ce critère est-il important pour votre use case (traitement de nuit vs traitement temps réel) ?

### Questions sur le choix du provider

5. **Coût estimé** : Pour 500 factures par mois, estimez le coût mensuel de chaque service. Lequel est le moins cher ?

6. **Intégration** : Si votre infrastructure est déjà sur AWS, quel impact cela a-t-il sur votre recommandation ?

7. **RGPD** : Ces factures contiennent des données fournisseurs (noms, adresses, SIRET). Quelles précautions RGPD devez-vous prendre ? Quelle région choisir pour chaque provider ?

8. **Fallback** : Si un service est en panne, avez-vous une stratégie de fallback ? Comment architecturer un système résilient ?

---

## Partie 5 — Recommandation écrite

Rédigez une recommandation de 200 à 400 mots à destination de la direction de l'entreprise. Elle doit inclure :

- Le service recommandé et pourquoi (avec arguments techniques ET business)
- Les limitations connues du service choisi
- Une estimation du ROI (temps homme économisé vs coût cloud)
- Les risques identifiés et comment les mitiger
- Un plan d'implémentation en 3 phases (POC → pilote → production)

---

## Critères d'évaluation

| Critère | Points | Description |
|---------|--------|-------------|
| Code fonctionnel (2+ providers) | 4 | Le code s'exécute et retourne des résultats |
| Tableau comparatif complété | 3 | Tous les champs remplis avec valeurs et confiances |
| Analyse des résultats | 4 | Réponses aux questions avec argumentation |
| Recommandation écrite | 4 | Argumentée, réaliste, orientée business |
| Considérations RGPD | 2 | Correctes et pertinentes |
| Qualité du code (structure, commentaires) | 3 | Code lisible, fonctions bien nommées |
| **Total** | **20** | |

---

## Ressources utiles

- Azure Document Intelligence pricing : [https://azure.microsoft.com/pricing/details/ai-document-intelligence/](https://azure.microsoft.com/pricing/details/ai-document-intelligence/)
- Textract pricing : [https://aws.amazon.com/textract/pricing/](https://aws.amazon.com/textract/pricing/)
- Document AI pricing : [https://cloud.google.com/document-ai/pricing](https://cloud.google.com/document-ai/pricing)
- Factures de test (open source) : [https://github.com/invoice-x/invoice2data](https://github.com/invoice-x/invoice2data)
