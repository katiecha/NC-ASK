# NC-ASK - North Carolina Autism Support & Knowledge

<!-- Badges -->
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](docs/)
<!-- Add when CI/CD is configured: [![Build Status](https://github.com/YOUR_ORG/NC-ASK/workflows/CI/badge.svg)](https://github.com/YOUR_ORG/NC-ASK/actions) -->
<!-- Add when releases are tagged: [![Release](https://img.shields.io/github/v/release/YOUR_ORG/NC-ASK)](https://github.com/YOUR_ORG/NC-ASK/releases) -->

> AI-powered educational platform providing clear, accessible information about autism services in North Carolina

<!--
Add screenshot or demo GIF here:
![NC-ASK Demo](design/screenshots/demo.gif)

Suggested screenshots:
1. Main chat interface showing a natural language query
2. Crisis detection in action with resource display
3. Source citations at bottom of response
-->

---

## Table of Contents

- [Why NC-ASK?](#why-nc-ask)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation & Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: Local Development](#option-2-local-development)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Technology Stack](#technology-stack)
- [Project Status](#project-status)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Why NC-ASK?

Led by Dr. Rohan Patel, a Developmental Behavioral Pediatrician, NC Autism Support and Knowledge (NC-ASK) addresses a critical need in autism care delivery.

**The Problem:**
Families and healthcare providers face overwhelming information overload when navigating autism services, healthcare systems, insurance requirements, and educational resources. Finding reliable, actionable guidance is time-consuming and frustrating.

**The Solution:**
NC-ASK is an educational tool powered by a privacy-first LLM application that delivers clear, tailored, and accurate guidance. Using Retrieval-Augmented Generation (RAG), it cuts through the noise to provide source-based answers in plain language, helping families and providers make informed decisions quickly.

---

## Key Features

### Core Capabilities

- **Natural Language Q&A** - Ask questions in plain English about autism services, IEPs, Medicaid waivers, and more
- **RAG-Powered Responses** - Retrieval-Augmented Generation ensures accurate, source-based answers from authoritative documents
- **Crisis Detection** - Automatic detection of mental health crises with immediate display of NC-specific crisis resources
- **Plain Language Output** - All responses written at 8th grade reading level for maximum accessibility
- **Source Citations** - Every answer includes citations to authoritative sources for verification
- **Privacy-First Design** - No user accounts, no tracking, ephemeral sessions only - your data stays private

### Safety & Compliance

- Automatic crisis keyword detection with 3-tier severity levels
- Immediate display of crisis resources (988 Lifeline, Crisis Text Line, NC Hope4NC, 911)
- Medical and legal disclaimers on all responses
- No PII storage or logging - complete privacy protection
- De-identified logging for system improvement only

---

## Quick Start

Get NC-ASK running in under 5 minutes:

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/NC-ASK.git
cd NC-ASK

# Run with Docker (recommended)
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

**Not sure which setup to use?** See our [Setup Decision Guide](docs/02_WHICH_SETUP.md)

---

## Installation & Setup

### Prerequisites

Choose your development path:

**Option 1: Docker Development (Recommended)**
- Docker Desktop
- Git

**Option 2: Local Development**
- Node.js 18+
- Python 3.11+
- Git

**External Services (for both options)**
- [Supabase](https://supabase.com) account (free tier) - Database and vector storage
- [Google Gemini API](https://ai.google.dev/) key (free tier) - LLM for generating responses

### Option 1: Docker (Recommended)

Run everything in containers with complete isolation:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/NC-ASK.git
cd NC-ASK

# 2. Start all services
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Benefits:** Consistent environment, no version conflicts, easy cleanup

**Full Guide:** [Docker Setup Documentation](docs/03_DOCKER_SETUP.md) (~5 minutes)

### Option 2: Local Development

Run frontend and backend locally with hot reload for faster iteration:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/NC-ASK.git
cd NC-ASK

# 2. Install dependencies and start development servers
npm run dev

# This starts:
# - Frontend dev server (http://localhost:5173)
# - Backend API (http://localhost:8000)
```

**Benefits:** Faster hot reload, direct debugging, native performance

**Full Guide:** [Local Setup Documentation](docs/04_LOCAL_SETUP.md) (~10 minutes)

### Production Deployment

Ready to deploy NC-ASK to production? We support multiple deployment options:

- **Docker Production** - Containerized deployment to any cloud provider
- **OpenShift** - Enterprise Kubernetes deployment (fully documented)
- **Cloud Platforms** - Vercel (frontend) + Render/Railway (backend)

See our [Deployment Guide](docs/05_DEPLOYMENT.md) for detailed instructions.

---

## Usage Examples

### Basic Query

Ask a question in natural language:

```
User: "What is an IEP and how do I get one for my child?"

NC-ASK: An IEP (Individualized Education Program) is a legally binding document
that outlines specialized instruction and services for students with disabilities...

[Response includes citations to authoritative sources]
```

### API Usage

Query the backend API directly:

```bash
# Health check
curl http://localhost:8000/api/health

# Query endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What autism services are covered by Medicaid in NC?"}'

# Export conversation via email
curl -X POST http://localhost:8000/api/email-export \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "messages": [...]}'

# Get crisis resources
curl http://localhost:8000/api/crisis-resources
```

### Document Ingestion

Add new documents to the knowledge base:

```bash
# 1. Add document metadata to backend/config/documents.json
# 2. Place document file in backend/data/
# 3. Run ingestion script
cd backend
python scripts/ingest_documents.py
```

For detailed configuration options, see [Document Configuration](#document-configuration) below.

---

## Architecture

NC-ASK uses a modern, privacy-first architecture:

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  React Frontend │─────▶│  FastAPI Backend │─────▶│    Supabase     │
│   (TypeScript)  │      │   (Python 3.11)  │      │  (PostgreSQL +  │
│                 │      │                  │      │    pgvector)    │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ├──────▶ Google Gemini 1.5 Flash (LLM)
                                  │
                                  └──────▶ sentence-transformers (Embeddings)
```

<!--
Add architecture diagram:
![NC-ASK Architecture](docs/diagrams/architecture.png)
-->

**Key Components:**
- **Frontend:** React 18 + TypeScript + Vite with CSS Modules
- **Backend:** FastAPI with RAG pipeline for document retrieval
- **Database:** Supabase (PostgreSQL + pgvector for vector search)
- **LLM:** Google Gemini 1.5 Flash for response generation
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2

**Future Roadmap (OpenShift Production):**
- Migration to self-hosted LLM (Llama 3.1 8B) for complete data residency
- No external API calls for user queries
- Full privacy-first deployment on OpenShift

For detailed architecture information, see [Architecture Documentation](docs/06_ARCHITECTURE.md).

---

## Documentation

Our comprehensive documentation covers all aspects of NC-ASK:

### Getting Started
- [Setup Decision Guide](docs/02_WHICH_SETUP.md) - Choose between Docker and local development
- [Docker Setup](docs/03_DOCKER_SETUP.md) - Container-based development setup (~5 min)
- [Local Setup](docs/04_LOCAL_SETUP.md) - Local environment setup (~10 min)

### Deployment & Operations
- [Deployment Guide](docs/05_DEPLOYMENT.md) - Production deployment instructions
- [OpenShift Deployment](docs/10_DEPLOYMENT.md) - Enterprise Kubernetes deployment

### Technical Deep Dives
- [Architecture](docs/06_ARCHITECTURE.md) - System architecture and technical design
- [Architecture (Revised)](docs/architecture_revised.md) - Updated architecture for production
- [Implementation Summary](docs/07_IMPLEMENTATION_SUMMARY.md) - Current implementation status
- [Safety & Crisis Detection](docs/08_SAFETY.md) - Crisis detection system and safety protocols

### Development
- [Claude Code Guidance](docs/CLAUDE.md) - AI-assisted development guidelines
- [Guiding Principles](docs/09_NC_ASK_AI_SG_Guiding_Principles_v0.docx) - Project principles and goals

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104.1 (Python 3.11+)
- **Database:** Supabase (PostgreSQL + pgvector)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **LLM:** Google Gemini 1.5 Flash
- **Document Processing:** PyPDF2, python-docx, BeautifulSoup4
- **Server:** Uvicorn/Gunicorn

### Frontend
- **Framework:** React 18.2.0
- **Language:** TypeScript 5.2.2
- **Build Tool:** Vite 4.4.9
- **Routing:** React Router DOM 6.15.0
- **Styling:** CSS Modules
- **Markdown:** React Markdown 10.1.0

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Deployment:** OpenShift, Vercel (frontend), Render/Railway (backend)
- **Development:** Hot reload for both frontend and backend

### API Endpoints

- `POST /api/query` - Natural language query processing
- `POST /api/email-export` - Export conversation to email
- `GET /api/health` - Health check endpoint
- `GET /api/crisis-resources` - Retrieve crisis resources

---

## Project Status

**Current Status:** 🚧 In Development

NC-ASK is currently an MVP (Minimum Viable Product) with core functionality complete:

- ✅ RAG pipeline fully functional
- ✅ Crisis detection with 3-tier severity levels
- ✅ Privacy-first: no PII storage, ephemeral sessions
- ✅ Plain language responses (8th grade reading level)
- ✅ Source citations for all answers
- ✅ Docker and local development setups
- ✅ OpenShift deployment configuration

**Next Steps:**
- Migration to self-hosted LLM (Llama 3.1 8B) for production
- Enhanced document management interface
- Advanced analytics for system improvement
- Expanded document knowledge base

---

## FAQ

### General Questions

**Q: Is NC-ASK free to use?**
A: Yes, NC-ASK is an open-source educational tool licensed under AGPL v3.0.

**Q: What kind of questions can I ask?**
A: You can ask questions about autism services in North Carolina, including IEPs, Medicaid waivers, therapy services, educational rights, insurance coverage, and more.

**Q: Does NC-ASK provide medical advice?**
A: No. NC-ASK is an educational tool only and does not provide medical, legal, or professional advice. Always consult qualified professionals for personalized guidance.

### Privacy & Data

**Q: Do you store my questions or conversations?**
A: No. NC-ASK uses ephemeral sessions only. We do not store user queries, conversations, or any personally identifiable information (PII).

**Q: What data do you collect?**
A: We collect only de-identified system logs for performance monitoring and improvement. No user data, queries, or PII is stored.

### Technical Questions

**Q: Can I run NC-ASK offline?**
A: Currently, NC-ASK requires internet access for Supabase (database) and Google Gemini API (LLM). The future OpenShift production deployment will support fully offline operation with a self-hosted LLM.

**Q: How do I add new documents to the knowledge base?**
A: Add document metadata to `backend/config/documents.json`, place the file in `backend/data/`, and run `python scripts/ingest_documents.py`. See [Document Configuration](#document-configuration) for details.

**Q: What document formats are supported?**
A: PDF, DOCX, HTML, and TXT files are currently supported.

### Development

**Q: How can I contribute?**
A: See our [Contributing](#contributing) section below. We welcome bug reports, feature requests, and pull requests.

**Q: What are the system requirements?**
A: For Docker: Docker Desktop and Git. For local development: Node.js 18+, Python 3.11+, and Git.

---

## Contributing

We welcome contributions to NC-ASK! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork the repository** - Create your own fork of the NC-ASK project
2. **Create a feature branch** - `git checkout -b feature/amazing-feature`
3. **Make your changes** - Write clean, documented code following our style
4. **Test thoroughly** - Ensure your changes don't break existing functionality
5. **Commit your changes** - `git commit -m 'Add some amazing feature'`
6. **Push to your branch** - `git push origin feature/amazing-feature`
7. **Open a Pull Request** - Describe your changes and why they're needed

### Development Guidelines

- Follow existing code style and conventions
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep PRs focused on a single feature or bug fix

### Areas for Contribution

- Document ingestion pipeline improvements
- Additional crisis detection keywords
- UI/UX enhancements
- Performance optimizations
- Documentation improvements
- Bug fixes and security patches

### Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/YOUR_ORG/NC-ASK/issues) with:
- Clear description of the problem or feature
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, browser, versions)

---

## Support

### Getting Help

- **Documentation:** Check our comprehensive [docs](docs/) first
- **GitHub Issues:** [Report bugs or request features](https://github.com/YOUR_ORG/NC-ASK/issues)
- **Discussions:** [Ask questions and share ideas](https://github.com/YOUR_ORG/NC-ASK/discussions)

### Team (Project Group B, COMP 523 F25)

- **Kush Gupta** - Client Manager
- **Nick Nguyen** - Project Manager
- **Hong Liu** - Tech Lead
- **Katie Chai** - Tech Lead

---

## License

NC-ASK is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This means:
- ✅ You can use, modify, and distribute this software freely
- ✅ You must share any modifications under the same license
- ✅ If you run a modified version as a web service, you must make the source code available
- ❌ This software comes with NO WARRANTY

See the [LICENSE](LICENSE) file for full legal text.

**Why AGPL?** We chose AGPL to ensure that any improvements to NC-ASK remain open and accessible to the autism support community, even when deployed as a service.

---

## Acknowledgments

NC-ASK is made possible by:

- **Dr. Rohan Patel** - Project vision and clinical guidance as Developmental Behavioral Pediatrician
- **UNC COMP 523 (Fall 2025)** - Academic support and project framework
- **Autism Society of North Carolina** - Domain expertise and document resources
- **Open Source Community** - Tools and libraries that power NC-ASK (FastAPI, React, Supabase, Google Gemini)
- **Families and Providers** - Whose needs drive this project's mission

---

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
# Navigate to backend
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

**Supported formats:** PDF, DOCX, HTML, TXT

---

<div align="center">

Made with ❤️ for the autism support community in North Carolina

[Report Bug](https://github.com/YOUR_ORG/NC-ASK/issues) · [Request Feature](https://github.com/YOUR_ORG/NC-ASK/issues) · [Documentation](docs/)

</div>
