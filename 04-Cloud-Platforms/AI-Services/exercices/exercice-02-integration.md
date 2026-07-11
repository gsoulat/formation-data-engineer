# Exercice 02 — Intégration d'un service cloud AI avec Python + Docker

## Contexte

Suite à l'exercice comparatif, votre équipe a choisi un service cloud AI pour l'extraction automatique de factures. Il faut maintenant construire un microservice production-ready : une API REST Python qui reçoit un PDF, appelle le service cloud AI, et retourne les données extraites en JSON.

Ce service sera conteneurisé avec Docker et devra respecter les bonnes pratiques : gestion des secrets, logs structurés, gestion d'erreurs, et health check.

---

## Objectifs

- Construire une API FastAPI qui encapsule un appel de service cloud AI
- Gérer les credentials de manière sécurisée (pas de clés en dur)
- Conteneuriser avec Docker (image légère, multi-stage build)
- Écrire des tests unitaires avec mock des appels API
- Documenter l'API (Swagger auto-généré par FastAPI)

---

## Prérequis

```bash
pip install fastapi uvicorn python-multipart python-dotenv pytest pytest-mock httpx
# + le SDK du provider choisi (Azure / AWS / GCP)
```

---

## Architecture du microservice

```
ocr-service/
├── .env.example          ← Template des variables d'environnement
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py           ← Point d'entrée FastAPI
│   ├── config.py         ← Configuration via variables d'environnement
│   ├── models.py         ← Modèles Pydantic (requêtes/réponses)
│   ├── services/
│   │   ├── __init__.py
│   │   └── ocr_service.py   ← Logique métier d'appel au cloud AI
│   └── routers/
│       ├── __init__.py
│       └── documents.py     ← Endpoints FastAPI
└── tests/
    ├── __init__.py
    ├── test_ocr_service.py
    └── test_endpoints.py
```

---

## Partie 1 — Configuration

### app/config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuration chargée depuis les variables d'environnement ou le fichier .env.
    Pydantic-settings valide automatiquement les types et signale les champs manquants.
    """
    # Choix du provider : "azure", "aws", "gcp"
    cloud_provider: str = "azure"

    # Azure Document Intelligence
    azure_endpoint: str = ""
    azure_key: str = ""

    # AWS Textract
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "eu-west-3"
    aws_s3_bucket: str = ""

    # GCP Document AI
    gcp_project_id: str = ""
    gcp_processor_id: str = ""
    gcp_location: str = "eu"
    google_application_credentials: str = ""

    # App settings
    max_file_size_mb: int = 10
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### .env.example

```bash
# Copier ce fichier en .env et remplir les valeurs
# Ne jamais committer .env dans git !

CLOUD_PROVIDER=azure  # azure | aws | gcp

# Azure Document Intelligence
AZURE_ENDPOINT=https://votre-resource.cognitiveservices.azure.com/
AZURE_KEY=votre_cle_ici

# AWS Textract
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-west-3
AWS_S3_BUCKET=

# GCP Document AI
GCP_PROJECT_ID=
GCP_PROCESSOR_ID=
GCP_LOCATION=eu
GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json

# App
MAX_FILE_SIZE_MB=10
LOG_LEVEL=INFO
```

---

## Partie 2 — Modèles de données

### app/models.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExtractedField(BaseModel):
    """Un champ extrait du document avec sa valeur et sa confiance."""
    value: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class InvoiceData(BaseModel):
    """Données extraites d'une facture."""
    vendor_name: Optional[ExtractedField] = None
    invoice_number: Optional[ExtractedField] = None
    invoice_date: Optional[ExtractedField] = None
    due_date: Optional[ExtractedField] = None
    subtotal: Optional[ExtractedField] = None
    tax_amount: Optional[ExtractedField] = None
    total_amount: Optional[ExtractedField] = None
    customer_name: Optional[ExtractedField] = None


class ExtractionResponse(BaseModel):
    """Réponse complète de l'API d'extraction."""
    success: bool
    provider: str
    processing_time_ms: int
    document_pages: int = 1
    data: Optional[InvoiceData] = None
    error: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Réponse du health check."""
    status: str
    provider: str
    version: str = "1.0.0"
```

---

## Partie 3 — Service OCR

### app/services/ocr_service.py

Implémentez la classe `OcrService` avec la méthode `extract_invoice(pdf_bytes: bytes) -> InvoiceData`.

```python
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.models import InvoiceData, ExtractedField
from app.config import Settings

logger = logging.getLogger(__name__)


class BaseOcrProvider(ABC):
    """Interface commune pour tous les providers OCR."""

    @abstractmethod
    def extract_invoice(self, pdf_bytes: bytes) -> tuple[InvoiceData, int]:
        """
        Extrait les données d'une facture.
        Retourne (InvoiceData, pages_count).
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Vérifie que le provider est accessible."""
        pass


class AzureOcrProvider(BaseOcrProvider):
    """Provider Azure Document Intelligence."""

    def __init__(self, settings: Settings):
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        self.client = DocumentIntelligenceClient(
            endpoint=settings.azure_endpoint,
            credential=AzureKeyCredential(settings.azure_key)
        )
        logger.info("AzureOcrProvider initialisé")

    def extract_invoice(self, pdf_bytes: bytes) -> tuple[InvoiceData, int]:
        poller = self.client.begin_analyze_document(
            model_id="prebuilt-invoice",
            analyze_request=pdf_bytes,
            content_type="application/octet-stream"
        )
        result = poller.result()

        invoice_data = InvoiceData()

        if result.documents:
            doc = result.documents[0]
            fields = doc.fields

            def get_field(name: str) -> Optional[ExtractedField]:
                f = fields.get(name)
                if f:
                    return ExtractedField(
                        value=str(f.content or "").strip(),
                        confidence=f.confidence or 0.0
                    )
                return None

            invoice_data.vendor_name = get_field("VendorName")
            invoice_data.invoice_number = get_field("InvoiceId")
            invoice_data.invoice_date = get_field("InvoiceDate")
            invoice_data.due_date = get_field("DueDate")
            invoice_data.subtotal = get_field("SubTotal")
            invoice_data.tax_amount = get_field("TotalTax")
            invoice_data.total_amount = get_field("InvoiceTotal")
            invoice_data.customer_name = get_field("CustomerName")

        pages = len(result.pages) if result.pages else 1
        return invoice_data, pages

    def health_check(self) -> bool:
        try:
            models = list(self.client.list_document_models())
            return len(models) > 0
        except Exception as e:
            logger.error(f"Azure health check failed: {e}")
            return False


class AwsOcrProvider(BaseOcrProvider):
    """Provider Amazon Textract."""

    def __init__(self, settings: Settings):
        import boto3
        self.textract = boto3.client("textract", region_name=settings.aws_region)
        self.s3 = boto3.client("s3", region_name=settings.aws_region)
        self.bucket = settings.aws_s3_bucket
        logger.info("AwsOcrProvider initialisé")

    def extract_invoice(self, pdf_bytes: bytes) -> tuple[InvoiceData, int]:
        # Upload temporaire vers S3
        import time
        s3_key = f"temp/invoice_{int(time.time())}.pdf"
        self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=pdf_bytes)

        try:
            response = self.textract.analyze_document(
                Document={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["QUERIES"],
                QueriesConfig={"Queries": [
                    {"Text": "What is the vendor or seller name?", "Alias": "vendor_name"},
                    {"Text": "What is the invoice number?", "Alias": "invoice_number"},
                    {"Text": "What is the invoice date?", "Alias": "invoice_date"},
                    {"Text": "What is the payment due date?", "Alias": "due_date"},
                    {"Text": "What is the subtotal or net amount?", "Alias": "subtotal"},
                    {"Text": "What is the tax amount?", "Alias": "tax_amount"},
                    {"Text": "What is the total amount due?", "Alias": "total_amount"},
                    {"Text": "What is the customer or buyer name?", "Alias": "customer_name"},
                ]}
            )
        finally:
            # Supprimer le fichier temporaire
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)

        blocks_by_id = {b["Id"]: b for b in response["Blocks"]}
        field_values = {}

        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY":
                alias = block["Query"].get("Alias")
                for rel in block.get("Relationships", []):
                    if rel["Type"] == "ANSWER":
                        for answer_id in rel["Ids"]:
                            answer_block = blocks_by_id.get(answer_id, {})
                            if answer_block.get("BlockType") == "QUERY_RESULT":
                                field_values[alias] = ExtractedField(
                                    value=answer_block.get("Text", ""),
                                    confidence=answer_block.get("Confidence", 0) / 100
                                )

        invoice_data = InvoiceData(
            vendor_name=field_values.get("vendor_name"),
            invoice_number=field_values.get("invoice_number"),
            invoice_date=field_values.get("invoice_date"),
            due_date=field_values.get("due_date"),
            subtotal=field_values.get("subtotal"),
            tax_amount=field_values.get("tax_amount"),
            total_amount=field_values.get("total_amount"),
            customer_name=field_values.get("customer_name"),
        )

        return invoice_data, 1  # Textract sync = 1 page

    def health_check(self) -> bool:
        try:
            # Test minimal : lister les jobs (0 appels facturés)
            self.textract.list_document_text_detection_jobs(MaxResults=1)
            return True
        except Exception as e:
            logger.error(f"AWS health check failed: {e}")
            return False


def get_ocr_provider(settings: Settings) -> BaseOcrProvider:
    """Factory : retourne le bon provider selon la configuration."""
    providers = {
        "azure": AzureOcrProvider,
        "aws": AwsOcrProvider,
    }

    provider_class = providers.get(settings.cloud_provider.lower())
    if not provider_class:
        raise ValueError(
            f"Provider inconnu : {settings.cloud_provider}. "
            f"Valeurs valides : {list(providers.keys())}"
        )

    return provider_class(settings)
```

---

## Partie 4 — Endpoints FastAPI

### app/routers/documents.py

```python
import logging
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.models import ExtractionResponse, HealthResponse
from app.config import Settings, get_settings
from app.services.ocr_service import get_ocr_provider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/extract-invoice", response_model=ExtractionResponse)
async def extract_invoice(
    file: UploadFile = File(..., description="Fichier PDF de la facture"),
    settings: Settings = Depends(get_settings)
):
    """
    Extrait les données d'une facture PDF via le service cloud AI configuré.

    Retourne les champs structurés (fournisseur, numéro, montants, dates)
    avec les scores de confiance associés.
    """
    # Validation du type de fichier
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")

    # Lecture du contenu
    content = await file.read()

    # Validation de la taille
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux. Maximum : {settings.max_file_size_mb} MB"
        )

    logger.info(f"Traitement de {file.filename} ({len(content)} bytes) avec {settings.cloud_provider}")

    start_ms = int(time.time() * 1000)

    try:
        provider = get_ocr_provider(settings)
        invoice_data, pages = provider.extract_invoice(content)
        elapsed_ms = int(time.time() * 1000) - start_ms

        logger.info(f"Extraction réussie : {file.filename} en {elapsed_ms}ms")

        return ExtractionResponse(
            success=True,
            provider=settings.cloud_provider,
            processing_time_ms=elapsed_ms,
            document_pages=pages,
            data=invoice_data
        )

    except Exception as e:
        elapsed_ms = int(time.time() * 1000) - start_ms
        logger.error(f"Erreur lors de l'extraction de {file.filename}: {e}", exc_info=True)

        return ExtractionResponse(
            success=False,
            provider=settings.cloud_provider,
            processing_time_ms=elapsed_ms,
            error=str(e)
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Vérifie l'état de santé du service et la connectivité au provider cloud AI.
    """
    try:
        provider = get_ocr_provider(settings)
        is_healthy = provider.health_check()

        if not is_healthy:
            return JSONResponse(
                status_code=503,
                content=HealthResponse(
                    status="degraded",
                    provider=settings.cloud_provider
                ).model_dump(mode="json")
            )

        return HealthResponse(status="healthy", provider=settings.cloud_provider)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "provider": settings.cloud_provider, "error": str(e)}
        )
```

### app/main.py

```python
import logging
from fastapi import FastAPI
from app.routers import documents
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

settings = get_settings()

app = FastAPI(
    title="OCR Invoice Service",
    description="API d'extraction de données de factures via cloud AI",
    version="1.0.0"
)

app.include_router(documents.router)


@app.get("/")
def root():
    return {"service": "ocr-invoice", "provider": settings.cloud_provider, "status": "running"}
```

---

## Partie 5 — Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer les dépendances dans un venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Image finale légère
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copier le venv et l'application
COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Utilisateur non-root (bonne pratique sécurité)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/documents/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# docker-compose.yml
version: "3.9"

services:
  ocr-service:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
    volumes:
      # Monter les credentials GCP si nécessaire
      - ./gcp-credentials.json:/app/gcp-credentials.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/documents/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Partie 6 — Tests

### tests/test_ocr_service.py

```python
import pytest
from unittest.mock import MagicMock, patch
from app.models import InvoiceData, ExtractedField
from app.config import Settings


def make_settings(provider: str = "azure") -> Settings:
    return Settings(
        cloud_provider=provider,
        azure_endpoint="https://test.cognitiveservices.azure.com/",
        azure_key="test-key"
    )


class TestAzureOcrProvider:
    """Tests du provider Azure avec mock."""

    @patch("app.services.ocr_service.DocumentIntelligenceClient")
    def test_extract_invoice_success(self, mock_client_class):
        """Vérifie que les champs sont correctement extraits quand Azure retourne des données."""
        # Arrange : construire un mock de réponse Azure
        mock_field = MagicMock()
        mock_field.content = "Acme Corp"
        mock_field.confidence = 0.95

        mock_doc = MagicMock()
        mock_doc.fields = {"VendorName": mock_field}

        mock_result = MagicMock()
        mock_result.documents = [mock_doc]
        mock_result.pages = [MagicMock()]

        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client

        # Act
        from app.services.ocr_service import AzureOcrProvider
        provider = AzureOcrProvider(make_settings("azure"))
        invoice_data, pages = provider.extract_invoice(b"%PDF-1.4 fake content")

        # Assert
        assert invoice_data.vendor_name is not None
        assert invoice_data.vendor_name.value == "Acme Corp"
        assert invoice_data.vendor_name.confidence == 0.95
        assert pages == 1

    @patch("app.services.ocr_service.DocumentIntelligenceClient")
    def test_extract_invoice_empty_result(self, mock_client_class):
        """Vérifie le comportement quand Azure ne retourne aucun document."""
        mock_result = MagicMock()
        mock_result.documents = []
        mock_result.pages = []

        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client

        from app.services.ocr_service import AzureOcrProvider
        provider = AzureOcrProvider(make_settings("azure"))
        invoice_data, pages = provider.extract_invoice(b"fake pdf")

        assert invoice_data.vendor_name is None
        assert invoice_data.total_amount is None
```

### tests/test_endpoints.py

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from app.main import app
from app.models import InvoiceData, ExtractedField


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ocr-invoice"


def test_extract_invoice_not_pdf():
    """Vérifie le rejet des fichiers non-PDF."""
    fake_file = io.BytesIO(b"not a pdf content")
    response = client.post(
        "/documents/extract-invoice",
        files={"file": ("document.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400


def test_extract_invoice_too_large():
    """Vérifie le rejet des fichiers trop volumineux."""
    large_content = b"%PDF-1.4 " + b"X" * (11 * 1024 * 1024)  # 11 MB
    fake_file = io.BytesIO(large_content)
    response = client.post(
        "/documents/extract-invoice",
        files={"file": ("big.pdf", fake_file, "application/pdf")}
    )
    assert response.status_code == 413


@patch("app.routers.documents.get_ocr_provider")
def test_extract_invoice_success(mock_get_provider):
    """Vérifie le traitement complet d'une facture."""
    mock_provider = MagicMock()
    mock_provider.extract_invoice.return_value = (
        InvoiceData(
            vendor_name=ExtractedField(value="Acme Corp", confidence=0.95),
            total_amount=ExtractedField(value="1500.00", confidence=0.99)
        ),
        1
    )
    mock_get_provider.return_value = mock_provider

    fake_pdf = io.BytesIO(b"%PDF-1.4 mock content")
    response = client.post(
        "/documents/extract-invoice",
        files={"file": ("facture.pdf", fake_pdf, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["vendor_name"]["value"] == "Acme Corp"
    assert data["data"]["total_amount"]["confidence"] == 0.99
```

---

## Commandes de lancement

```bash
# Développement local
uvicorn app.main:app --reload --port 8080

# Avec Docker
docker build -t ocr-service .
docker run --env-file .env -p 8080:8080 ocr-service

# Avec Docker Compose
docker-compose up --build

# Lancer les tests
pytest tests/ -v

# Tester l'API avec curl
curl -X POST http://localhost:8080/documents/extract-invoice \
  -F "file=@./test_invoice.pdf" \
  | python -m json.tool
```

---

## Critères d'évaluation

| Critère | Points | Description |
|---------|--------|-------------|
| Service OCR fonctionnel (1+ provider) | 5 | L'extraction retourne des données réelles |
| API FastAPI avec modèles Pydantic | 4 | Endpoints documentés, validation des entrées |
| Dockerfile fonctionnel (multi-stage) | 3 | Image se build et se lance correctement |
| Tests unitaires avec mocks | 4 | Tests sans dépendance aux services cloud réels |
| Gestion des erreurs et logs | 2 | Les erreurs sont captées et loggées proprement |
| Secrets non exposés | 2 | Pas de clés dans le code ou les images Docker |
| **Total** | **20** | |

---

## Ressources

- FastAPI docs : [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Dockerfile best practices : [https://docs.docker.com/develop/develop-images/dockerfile_best-practices/](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- pytest-mock : [https://pytest-mock.readthedocs.io/](https://pytest-mock.readthedocs.io/)
- pydantic-settings : [https://docs.pydantic.dev/latest/concepts/pydantic_settings/](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
