# Google Document AI — Processeurs, Form Parser et extraction structurée

## Introduction

**Google Document AI** est le service GCP d'extraction de données structurées depuis des documents. Il propose une approche basée sur des **processeurs** : chaque processeur est spécialisé dans un type de document (formulaires génériques, factures, reçus, contrats, etc.).

Document AI utilise des modèles de deep learning entraînés par Google sur des millions de documents réels. Son point fort est la précision sur les documents complexes et la gestion des layouts variés.

---

## Processeurs disponibles

### Processeurs génériques

| Processeur | ID type | Description |
|-----------|---------|-------------|
| Document OCR | `DOCUMENT_OCR_PROCESSOR` | Extraction de texte brut avec positions |
| Form Parser | `FORM_PARSER_PROCESSOR` | Paires clé-valeur dans les formulaires |
| Document Quality | `DOCUMENT_QUALITY_PROCESSOR` | Évaluation de la qualité d'un scan |

### Processeurs spécialisés (pré-entraînés)

| Processeur | Langue | Description |
|-----------|--------|-------------|
| Invoice Parser | Multi | Extraction de factures (fournisseur, montant, TVA...) |
| Receipt Parser | Multi | Tickets de caisse et reçus |
| Expense Parser | Multi | Notes de frais |
| US Driver License | EN | Permis de conduire américain |
| US Passport | EN | Passeports américains |
| FR Driver License | FR | Permis de conduire français |
| Identity Document OCR | Multi | Documents d'identité génériques |
| Bank Statement | Multi | Relevés bancaires |
| W2/1099 | EN | Formulaires fiscaux US |

> Google élargit régulièrement la liste des processeurs. Consultez la console Document AI pour la liste complète.

---
> 🔴 **ACTION FORMATEUR — CAPTURE REQUISE**
> **Capturer :** Console GCP → Document AI → "Explore processors" → sélectionner "Invoice Parser" → créer le processeur (région europe-west9) → uploader un PDF de facture → lancer le traitement → parcourir l'interface de résultats : onglet "Entities" pour les champs extraits, onglet "Text" pour le texte brut, onglet "Pages" pour les bounding boxes visuelles.
> **Expliquer :** Insister sur la section "Entities" qui montre les champs sémantiques extraits (pas juste le texte). Montrer la visualisation des bounding boxes sur le document original. Expliquer la différence entre un processeur "pré-entraîné" et un processeur "custom" qu'on peut entraîner sur ses propres données.
---

---

## Installation et configuration

```bash
pip install google-cloud-documentai
```

```python
import os
from google.cloud import documentai
from google.api_core.client_options import ClientOptions

PROJECT_ID = os.environ["GCP_PROJECT_ID"]
LOCATION = "eu"  # "us" ou "eu" (régions disponibles pour Document AI)

# Client avec endpoint régional
opts = ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
docai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
```

---

## Créer un processeur

```python
def create_processor(display_name: str, processor_type: str) -> documentai.Processor:
    """
    Crée un processeur Document AI dans votre projet.
    Ex: processor_type = "INVOICE_PROCESSOR"
    """
    parent = docai_client.common_location_path(PROJECT_ID, LOCATION)

    processor = docai_client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name=display_name,
            type_=processor_type
        )
    )

    print(f"Processeur créé : {processor.name}")
    print(f"  Type : {processor.type_}")
    print(f"  État : {processor.state.name}")
    return processor


# Exemple
invoice_processor = create_processor(
    display_name="Invoice Parser Formation",
    processor_type="INVOICE_PROCESSOR"
)

# Sauvegarder l'ID du processeur pour les appels suivants
PROCESSOR_ID = invoice_processor.name.split("/")[-1]
```

---

## Lister les processeurs disponibles

```python
def list_processor_types() -> None:
    """
    Liste tous les types de processeurs disponibles dans votre région.
    """
    parent = docai_client.common_location_path(PROJECT_ID, LOCATION)
    processor_types = docai_client.fetch_processor_types(parent=parent)

    print(f"Processeurs disponibles en {LOCATION}:")
    for pt in sorted(processor_types.processor_types, key=lambda p: p.type_):
        if pt.allow_creation:
            categories = ", ".join(pt.category for pt in pt.category if True)
            print(f"  {pt.type_:50s} {pt.name}")


def list_my_processors() -> list:
    """
    Liste les processeurs créés dans votre projet.
    """
    parent = docai_client.common_location_path(PROJECT_ID, LOCATION)
    processors = list(docai_client.list_processors(parent=parent))

    print(f"Vos processeurs ({len(processors)}) :")
    for p in processors:
        print(f"  {p.display_name:40s} | Type: {p.type_:30s} | État: {p.state.name}")

    return processors
```

---

## Traitement synchrone d'un document

```python
def process_document_sync(document_path: str, processor_id: str,
                            mime_type: str = "application/pdf") -> documentai.Document:
    """
    Traite un document de manière synchrone.
    Limite : 15 pages / 20 MB. Pour les documents plus grands, utiliser le batch.
    """
    processor_name = docai_client.processor_path(PROJECT_ID, LOCATION, processor_id)

    with open(document_path, "rb") as f:
        document_content = f.read()

    raw_document = documentai.RawDocument(
        content=document_content,
        mime_type=mime_type
    )

    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document
    )

    result = docai_client.process_document(request=request)
    return result.document


def extract_invoice_entities(document: documentai.Document) -> dict:
    """
    Extrait les entités d'une facture traitée par Document AI.
    """
    entities = {}

    for entity in document.entities:
        entity_name = entity.type_
        entity_value = entity.mention_text

        # Gérer les entités avec propriétés (ex: lignes d'articles)
        if entity.properties:
            sub_entities = {}
            for prop in entity.properties:
                sub_entities[prop.type_] = prop.mention_text
            entities.setdefault(entity_name, []).append({
                "value": entity_value,
                "confidence": entity.confidence,
                "sub_fields": sub_entities
            })
        else:
            if entity_name in entities:
                # Si plusieurs valeurs pour le même champ
                if not isinstance(entities[entity_name], list):
                    entities[entity_name] = [entities[entity_name]]
                entities[entity_name].append({
                    "value": entity_value,
                    "confidence": entity.confidence
                })
            else:
                entities[entity_name] = {
                    "value": entity_value,
                    "confidence": entity.confidence
                }

    return entities


# Usage
document = process_document_sync("./documents/facture.pdf", PROCESSOR_ID)
entities = extract_invoice_entities(document)

print("Entités extraites :")
for field, data in entities.items():
    if isinstance(data, dict):
        print(f"  {field}: {data['value']} (confiance: {data['confidence']:.2%})")
    elif isinstance(data, list):
        print(f"  {field}: {len(data)} occurrence(s)")
```

---

## Extraction du texte et des tableaux

```python
def extract_text_and_tables(document: documentai.Document) -> dict:
    """
    Extrait le texte brut et les tableaux du document traité.
    """
    result = {
        "full_text": document.text,
        "pages": []
    }

    for page in document.pages:
        page_data = {
            "page_number": page.page_number,
            "tables": [],
            "form_fields": []
        }

        # Extraction des tableaux
        for table in page.tables:
            table_data = {"header_rows": [], "body_rows": []}

            for header_row in table.header_rows:
                row = []
                for cell in header_row.cells:
                    row.append(extract_text_from_layout(document.text, cell.layout))
                table_data["header_rows"].append(row)

            for body_row in table.body_rows:
                row = []
                for cell in body_row.cells:
                    row.append(extract_text_from_layout(document.text, cell.layout))
                table_data["body_rows"].append(row)

            page_data["tables"].append(table_data)

        # Extraction des champs de formulaire
        for form_field in page.form_fields:
            key_text = extract_text_from_layout(document.text, form_field.field_name)
            value_text = extract_text_from_layout(document.text, form_field.field_value)
            page_data["form_fields"].append({
                "key": key_text.strip(),
                "value": value_text.strip(),
                "confidence": form_field.value_confidence
            })

        result["pages"].append(page_data)

    return result


def extract_text_from_layout(document_text: str, layout: documentai.Document.Page.Layout) -> str:
    """
    Extrait le texte d'un layout en utilisant les indices de texte.
    """
    text_parts = []
    for segment in layout.text_anchor.text_segments:
        start = int(segment.start_index) if segment.start_index else 0
        end = int(segment.end_index)
        text_parts.append(document_text[start:end])
    return "".join(text_parts)
```

---

## Traitement en lot (batch) depuis GCS

Pour les gros volumes de documents (plus de 15 pages ou traitement en masse) :

```python
import time
from google.cloud import storage

def batch_process_documents(gcs_input_prefix: str, gcs_output_prefix: str,
                              processor_id: str) -> list[dict]:
    """
    Traitement en lot de documents depuis GCS.
    gcs_input_prefix: ex "gs://mon-bucket/input/"
    gcs_output_prefix: ex "gs://mon-bucket/output/"
    """
    processor_name = docai_client.processor_path(PROJECT_ID, LOCATION, processor_id)

    gcs_documents = documentai.GcsDocuments(
        documents=[
            documentai.GcsDocument(
                gcs_uri=f"{gcs_input_prefix}facture_001.pdf",
                mime_type="application/pdf"
            ),
            documentai.GcsDocument(
                gcs_uri=f"{gcs_input_prefix}facture_002.pdf",
                mime_type="application/pdf"
            ),
        ]
    )

    output_config = documentai.DocumentOutputConfig(
        gcs_output_config=documentai.DocumentOutputConfig.GcsOutputConfig(
            gcs_uri=gcs_output_prefix,
            sharding_config=documentai.DocumentOutputConfig.GcsOutputConfig.ShardingConfig(
                pages_per_shard=10
            )
        )
    )

    request = documentai.BatchProcessRequest(
        name=processor_name,
        input_documents=documentai.BatchDocumentsInputConfig(
            gcs_documents=gcs_documents
        ),
        document_output_config=output_config
    )

    # Lancer l'opération longue
    operation = docai_client.batch_process_documents(request=request)
    print(f"Batch lancé. Opération : {operation.operation.name}")

    # Attendre la fin
    print("Traitement en cours...")
    operation.result(timeout=300)
    print("Batch terminé !")

    # Lister les fichiers de sortie
    gcs_client = storage.Client()
    bucket_name = gcs_output_prefix.split("/")[2]
    prefix = "/".join(gcs_output_prefix.split("/")[3:])

    bucket = gcs_client.bucket(bucket_name)
    output_files = list(bucket.list_blobs(prefix=prefix))

    results = []
    for blob in output_files:
        if blob.name.endswith(".json"):
            content = blob.download_as_text()
            import json
            doc_data = json.loads(content)
            results.append({
                "file": blob.name,
                "entities_count": len(doc_data.get("entities", []))
            })
            print(f"  Résultat : {blob.name}")

    return results
```

---

## Processeurs custom — Workflow

Document AI permet de créer des processeurs entraînés sur vos propres données :

```
1. CHOISIR le type de base
   └── Custom extractor (champs arbitraires)
   └── Custom classifier (classification de documents)
   └── Custom splitter (séparation de lots de documents)

2. PRÉPARER les données dans GCS
   └── Minimum 10 documents annotés (idéalement 50+)
   └── Format JSONL ou annotation via l'interface

3. ANNOTER dans la console Document AI
   └── Console GCP → Document AI → votre processeur → Train → Upload documents

4. ENTRAÎNER
   └── Durée : quelques heures selon le volume

5. ÉVALUER
   └── Métriques F1, précision, rappel par entité

6. DÉPLOYER une nouvelle version
   └── La version active reçoit le trafic de production
```

---

## Ressources officielles

- Documentation Document AI : [https://cloud.google.com/document-ai/docs](https://cloud.google.com/document-ai/docs)
- Console Document AI : [https://console.cloud.google.com/ai/document-ai](https://console.cloud.google.com/ai/document-ai)
- Processeurs disponibles : [https://cloud.google.com/document-ai/docs/processors-list](https://cloud.google.com/document-ai/docs/processors-list)
- SDK Python : `pip install google-cloud-documentai`
- Quickstart : [https://cloud.google.com/document-ai/docs/quickstart-client-libraries](https://cloud.google.com/document-ai/docs/quickstart-client-libraries)
