# Azure Document Intelligence — Extraction de données depuis des PDFs

## Introduction

**Azure Document Intelligence** (anciennement Azure Form Recognizer) est un service de traitement de documents basé sur l'IA. Il permet d'extraire automatiquement du texte, des tableaux, des champs structurés et des données sémantiques à partir de documents scannés, de PDFs ou d'images.

Ce service va bien au-delà d'un simple OCR : il comprend la structure des documents et peut identifier des champs spécifiques (numéro de facture, montant, date, etc.) sans que vous ayez à définir des règles de parsing manuellement.

---

## Modèles disponibles

Azure Document Intelligence propose deux catégories de modèles :

### Modèles pré-entraînés (Read-to-use)

Ces modèles sont directement utilisables sans aucune configuration :

| Modèle | Identifiant | Usage |
|--------|------------|-------|
| Lecture générale | `prebuilt-read` | Extraction de texte pur, OCR basique |
| Document général | `prebuilt-document` | Texte + structure (tableaux, paires clé-valeur) |
| Facture | `prebuilt-invoice` | Extraction structurée de factures |
| Reçu | `prebuilt-receipt` | Tickets de caisse, reçus de paiement |
| Carte d'identité | `prebuilt-idDocument` | Passeports, CNI, permis de conduire |
| Carte de visite | `prebuilt-businessCard` | Nom, entreprise, email, téléphone |
| Formulaire fiscal US | `prebuilt-tax.us.w2` | Formulaires W2 américains |
| Contrat | `prebuilt-contract` | Clauses, parties, dates dans les contrats |

### Modèles personnalisés (Custom)

Pour les documents spécifiques à votre métier (bons de commande internes, formulaires propres à votre secteur) :

- **Custom template** : pour les documents à structure fixe (formulaires)
- **Custom neural** : pour les documents avec structure variable (lettres, contrats complexes)
- **Composed model** : combine plusieurs modèles custom pour classifier et traiter automatiquement

---

## Créer et configurer la ressource

### Via le portail Azure

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Portail Azure → Créer une ressource → "Document Intelligence" → Configuration de la ressource (région France Central, F0) → accès au Document Intelligence Studio → upload d'une facture PDF → lancement de l'analyse avec le modèle prebuilt-invoice → visualisation des résultats extraits dans l'interface graphique.
> **Expliquer :** Montrer côte à côte le PDF original et les champs extraits dans le panneau de droite. Insister sur la confiance (confidence score) de chaque champ extrait. Montrer qu'on peut télécharger le JSON de résultat.
---

```bash
# Création via CLI
az cognitiveservices account create \
  --name mon-document-intelligence \
  --resource-group rg-formation-ai \
  --kind FormRecognizer \
  --sku S0 \
  --location francecentral \
  --yes
```

---

## Installation et configuration

```bash
pip install azure-ai-documentintelligence
```

```python
# Configuration de base
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
key = os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]

client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

---

## Exemple 1 : Extraction de texte brut (prebuilt-read)

```python
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un PDF local.
    Retourne le texte concaténé de toutes les pages.
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    poller = client.begin_analyze_document(
        model_id="prebuilt-read",
        analyze_request=pdf_bytes,
        content_type="application/octet-stream"
    )
    result = poller.result()

    full_text = []
    for page in result.pages:
        print(f"Page {page.page_number}: {page.width}x{page.height} {page.unit}")
        for line in page.lines:
            full_text.append(line.content)

    return "\n".join(full_text)


# Usage
text = extract_text_from_pdf("./documents/rapport_annuel.pdf")
print(f"Texte extrait ({len(text)} caractères):")
print(text[:500])
```

---

## Exemple 2 : Extraction de facture (prebuilt-invoice)

```python
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from typing import Optional

def extract_invoice_data(pdf_path: str) -> dict:
    """
    Extrait les données structurées d'une facture PDF.
    Retourne un dictionnaire avec les champs principaux.
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        analyze_request=pdf_bytes,
        content_type="application/octet-stream"
    )
    result = poller.result()

    invoices = []

    for doc in result.documents:
        fields = doc.fields

        def get_field(name: str) -> Optional[str]:
            """Récupère la valeur d'un champ avec sa confiance."""
            field = fields.get(name)
            if field:
                return {
                    "value": field.value_string or field.value_number or str(field.content),
                    "confidence": field.confidence
                }
            return None

        invoice = {
            "vendor_name": get_field("VendorName"),
            "vendor_address": get_field("VendorAddress"),
            "customer_name": get_field("CustomerName"),
            "customer_address": get_field("CustomerAddress"),
            "invoice_id": get_field("InvoiceId"),
            "invoice_date": get_field("InvoiceDate"),
            "due_date": get_field("DueDate"),
            "subtotal": get_field("SubTotal"),
            "total_tax": get_field("TotalTax"),
            "invoice_total": get_field("InvoiceTotal"),
            "items": []
        }

        # Extraction des lignes d'articles
        items_field = fields.get("Items")
        if items_field and items_field.value_array:
            for item in items_field.value_array:
                item_fields = item.value_object or {}
                invoice["items"].append({
                    "description": get_field_from_dict(item_fields, "Description"),
                    "quantity": get_field_from_dict(item_fields, "Quantity"),
                    "unit_price": get_field_from_dict(item_fields, "UnitPrice"),
                    "amount": get_field_from_dict(item_fields, "Amount"),
                })

        invoices.append(invoice)

    return invoices


def get_field_from_dict(fields: dict, name: str):
    """Helper pour extraire un champ depuis un dictionnaire de champs."""
    field = fields.get(name)
    if field:
        return {
            "value": str(field.content) if field.content else None,
            "confidence": field.confidence
        }
    return None


# Usage et affichage
import json

invoices = extract_invoice_data("./documents/facture_exemple.pdf")
for i, invoice in enumerate(invoices):
    print(f"\n=== Facture {i+1} ===")
    print(f"Fournisseur : {invoice['vendor_name']}")
    print(f"Client      : {invoice['customer_name']}")
    print(f"N° Facture  : {invoice['invoice_id']}")
    print(f"Date        : {invoice['invoice_date']}")
    print(f"Total HT    : {invoice['subtotal']}")
    print(f"TVA         : {invoice['total_tax']}")
    print(f"Total TTC   : {invoice['invoice_total']}")

    if invoice["items"]:
        print(f"\nLignes ({len(invoice['items'])} articles):")
        for item in invoice["items"]:
            print(f"  - {item['description']} | Qté: {item['quantity']} | "
                  f"PU: {item['unit_price']} | Montant: {item['amount']}")
```

---

## Exemple 3 : Extraction de tableaux

Le modèle `prebuilt-document` extrait automatiquement les tableaux :

```python
def extract_tables_from_document(pdf_path: str) -> list[dict]:
    """
    Extrait tous les tableaux d'un document.
    Retourne une liste de tableaux sous forme de dictionnaires.
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    poller = client.begin_analyze_document(
        model_id="prebuilt-document",
        analyze_request=pdf_bytes,
        content_type="application/octet-stream"
    )
    result = poller.result()

    tables = []

    for table_idx, table in enumerate(result.tables or []):
        print(f"\nTableau {table_idx + 1}: {table.row_count} lignes x {table.column_count} colonnes")

        # Construire une matrice 2D
        matrix = [[None] * table.column_count for _ in range(table.row_count)]

        for cell in table.cells:
            matrix[cell.row_index][cell.column_index] = {
                "content": cell.content,
                "kind": cell.kind,  # "columnHeader", "rowHeader", "content"
                "confidence": cell.confidence
            }

        tables.append({
            "row_count": table.row_count,
            "column_count": table.column_count,
            "cells": matrix
        })

        # Affichage en console
        for row in matrix:
            row_str = " | ".join([
                (cell["content"] if cell else "").ljust(20)
                for cell in row
            ])
            print(f"  {row_str}")

    return tables
```

---

## Exemple 4 : Analyse de documents depuis une URL

```python
def analyze_document_from_url(url: str, model_id: str = "prebuilt-read") -> dict:
    """
    Analyse un document accessible via une URL publique.
    Utile pour les documents stockés dans Azure Blob Storage (avec SAS token).
    """
    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentSource

    poller = client.begin_analyze_document(
        model_id=model_id,
        analyze_request=AnalyzeDocumentRequest(
            url_source=url
        )
    )
    result = poller.result()

    return {
        "model_id": result.model_id,
        "page_count": len(result.pages),
        "content": result.content,
        "paragraphs": [p.content for p in (result.paragraphs or [])],
        "tables_count": len(result.tables or [])
    }


# Exemple avec une facture publique
url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"
result = analyze_document_from_url(url, "prebuilt-invoice")
print(f"Pages analysées: {result['page_count']}")
print(f"Tableaux trouvés: {result['tables_count']}")
```

---

## Traitement en lot (batch processing)

Pour traiter plusieurs documents efficacement :

```python
import asyncio
from pathlib import Path

async def process_invoices_batch(pdf_directory: str) -> list[dict]:
    """
    Traite tous les PDFs d'un répertoire en parallèle.
    """
    pdf_files = list(Path(pdf_directory).glob("*.pdf"))
    print(f"Traitement de {len(pdf_files)} factures...")

    # Soumettre tous les pollers en parallèle
    pollers = []
    for pdf_path in pdf_files:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        poller = client.begin_analyze_document(
            model_id="prebuilt-invoice",
            analyze_request=pdf_bytes,
            content_type="application/octet-stream"
        )
        pollers.append((pdf_path.name, poller))

    # Attendre les résultats
    results = []
    for filename, poller in pollers:
        try:
            result = poller.result(timeout=120)
            results.append({
                "file": filename,
                "status": "success",
                "documents": len(result.documents),
                "data": result.documents[0].fields if result.documents else {}
            })
            print(f"  OK : {filename}")
        except Exception as e:
            results.append({
                "file": filename,
                "status": "error",
                "error": str(e)
            })
            print(f"  ERREUR : {filename} — {e}")

    return results


# Usage
import asyncio
results = asyncio.run(process_invoices_batch("./factures/"))
success_count = sum(1 for r in results if r["status"] == "success")
print(f"\nRésultat : {success_count}/{len(results)} factures traitées avec succès")
```

---

## Modèles personnalisés — Vue d'ensemble

Lorsque les modèles pré-entraînés ne correspondent pas à vos documents :

### Workflow de création d'un modèle custom

```
1. PRÉPARER les données d'entraînement
   └── 5 à 15 exemples minimum (idéalement 20-50)
   └── Documents représentatifs de la variabilité réelle

2. UPLOADER sur Azure Blob Storage
   └── Créer un container dédié
   └── Obtenir un SAS token avec permissions lecture

3. ÉTIQUETER dans Document Intelligence Studio
   └── https://documentintelligence.ai.azure.com/
   └── Définir les champs à extraire
   └── Annoter chaque document d'entraînement

4. ENTRAÎNER le modèle
   └── Durée : quelques minutes à quelques heures selon le volume

5. TESTER et ÉVALUER
   └── Mesurer l'accuracy sur un jeu de test
   └── Itérer si nécessaire

6. DÉPLOYER et utiliser
   └── Même API que les modèles pré-entraînés
```

```python
# Utiliser un modèle custom
CUSTOM_MODEL_ID = "mon-modele-bon-de-commande-v2"

poller = client.begin_analyze_document(
    model_id=CUSTOM_MODEL_ID,
    analyze_request=pdf_bytes,
    content_type="application/octet-stream"
)
result = poller.result()

for doc in result.documents:
    print(f"Modèle utilisé : {doc.doc_type}")
    print(f"Confiance globale : {doc.confidence:.2%}")
    for field_name, field_value in doc.fields.items():
        print(f"  {field_name}: {field_value.content} (confiance: {field_value.confidence:.2%})")
```

---

## Ressources officielles

- Documentation Azure Document Intelligence : [https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/](https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/)
- Document Intelligence Studio : [https://documentintelligence.ai.azure.com/](https://documentintelligence.ai.azure.com/)
- SDK Python : `pip install azure-ai-documentintelligence`
- Exemples GitHub : [https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence)
