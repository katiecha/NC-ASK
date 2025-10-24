# NC ASK - North Carolina Autism Support & Knowledge

Led by Dr. Rohan Patel, a Developmental Behavioral Pediatrician, NC Autism Support and Knowledge (NC-ASK) addresses a critical need he sees every day in his work. As a developmental pediatrician and clinical informatician who treats children with Autism Spectrum Disorder (ASD), he witnessed firsthand the immense challenges families and providers face with information overload and the complexities of navigating healthcare, insurance, and educational systems.

NC-ASK is an educational tool, driven by an LLM application that provides clear, tailored, and actionable guidance, cutting through the noise to deliver reliable information.

## Team (Project Group B, COMP 523 F25)
- Kush Gupta - Client Manager
- Nick Nguyen - Project Manager
- Hong Liu - Tech Lead
- Katie Chai - Tech Lead

## Features

### Core Capabilities
- **Natural Language Q&A**: Ask questions in plain language about autism services, IEPs, waivers, and more
- **RAG-Powered Responses**: Retrieval-Augmented Generation ensures accurate, source-based answers
- **Crisis Detection**: Automatic detection of mental health crises with immediate resource display
- **Plain Language**: All responses written at 8th grade reading level for accessibility
- **Source Citations**: Every answer includes citations to authoritative sources
- **Privacy-First**: No user accounts, no tracking, ephemeral sessions only

### Safety Features
- Automatic crisis keyword detection
- 988 Suicide & Crisis Lifeline integration
- NC-specific crisis resources
- Medical and legal disclaimers
- No PII storage or logging

## Quick Start

**Not sure which setup to use?** → See [WHICH_SETUP.md](WHICH_SETUP.md) for a decision guide

### Development Setup - Choose Your Path

#### Option A: Docker (Recommended for consistency)
Run everything in containers with one command:
```bash
docker-compose up --build
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

→ See [DOCKER_SETUP.md](DOCKER_SETUP.md) for full setup (~5 minutes)

#### Option B: Local (Faster iteration)
Run frontend and backend locally with hot reload:
```bash
npm run dev
```
Requires Python 3.11+ venv and Node.js 18+.

→ See [START_HERE.md](START_HERE.md) for full setup (~10 minutes)

### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for production Docker or cloud deployment instructions.

---

## What You'll Need

**To get started developing:**
- Node.js 18+ and Python 3.11+ (for local development)
- OR Docker Desktop (for Docker development)

**External services (set up after project is running):**
- Supabase account (free tier) - Database and vector storage
- Google Gemini API key (free tier) - LLM for generating responses

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: Google Gemini 1.5 Flash
- **Storage**: Supabase Storage
- **Document Processing**: PyPDF2, python-docx, BeautifulSoup

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: CSS Modules
- **State Management**: React Hooks
- **API Client**: Fetch API

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Development**: Hot reload for both frontend and backend
- **Deployment**: Vercel (frontend), Render/Railway (backend)

## Document Configuration

NC-ASK uses a modular configuration system for managing document metadata. This separates document data from ingestion logic for better maintainability.

### Adding Documents

Documents are configured in `backend/config/documents.json`. To add a new document:

```json
{
  "your_document_key": {
    "title": "Document Title",
    "topic": "Topic Name",
    "subtopic": "Subtopic Name",
    "audience": ["families", "providers"],
    "tags": ["tag1", "tag2", "tag3"],
    "content_type": "ProceduralGuide",
    "source_org": "Organization Name",
    "source_url": "https://example.com/document.pdf",
    "authority_level": 2
  }
}
```

### Required Fields

- **title**: Display name of the document
- **topic**: Main category (e.g., "Education", "Medicaid Programs")
- **audience**: List of target audiences (e.g., ["families", "providers"])
- **tags**: List of searchable keywords
- **content_type**: Type of document (see valid types below)
- **source_org**: Originating organization

### Optional Fields

- **subtopic**: Subcategory within the topic
- **source_url**: URL to fetch the document from (for remote documents)
- **authority_level**: 1 (highest) to 3 (lowest) - affects retrieval ranking
- **escalation_flag**: Set to "crisis" for urgent/crisis-related content

### Valid Content Types

- `ProceduralGuide` - Step-by-step instructions
- `FAQ` - Frequently asked questions
- `LegalRight` - Legal rights and protections
- `ClinicalSummary` - Clinical/medical information
- `FormTemplate` - Forms and templates
- `ResourceDirectory` - Lists of resources
- `GeneralInfo` - General information

### Using Document Config in Code

```python
from config import get_document_config

# Load all documents
config = get_document_config()
all_docs = config.get_all_documents()

# Get specific document
doc = config.get_document("iep_referral_process")

# Filter by topic
education_docs = config.get_documents_by_topic("Education")

# Filter by content type
guides = config.get_documents_by_content_type("ProceduralGuide")

# Filter by organization
asnc_docs = config.get_documents_by_source_org("Autism Society of North Carolina")

# Validate configuration
if config.validate_all():
    print("All documents are valid!")
```

### Document Ingestion

To ingest documents into the RAG system:

```bash
# Navigate to project root
cd backend

# Run ingestion script
python scripts/ingest_documents.py
```

The script will:
1. Load configurations from `backend/config/documents.json`
2. Download remote documents (if `source_url` is provided)
3. Process local documents from `backend/data/`
4. Extract text and generate embeddings
5. Store in Supabase with metadata

**Supported formats**: PDF, DOCX, HTML, TXT