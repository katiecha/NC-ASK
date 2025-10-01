# Data Directory

Place your source documents here for ingestion into the knowledge base.

## Supported File Formats
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Plain Text (`.txt`)
- HTML (`.html`, `.htm`)

## Document Types
According to the architecture, documents should be categorized as:
- **ProceduralGuide**: Step-by-step instructions (IEP requests, waiver applications)
- **FAQ**: Common questions and answers
- **LegalRights**: Rights under IDEA, ADA, etc.
- **ResourceDirectory**: Contact info for services
- **CrisisSupport**: Crisis intervention resources

## Running Ingestion

From the `backend` directory:

```bash
python scripts/ingest_documents.py
```

## Note
Documents added here are for initial development and testing. In production, documents will be managed through an admin interface or upload API.
