# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NC-ASK (North Carolina Autism Support & Knowledge) is an educational LLM-powered Q&A platform that helps families and providers navigate autism services in North Carolina. The system uses RAG (Retrieval-Augmented Generation) to provide accurate, source-based answers with crisis detection and plain language responses.

**Key Characteristics:**
- Privacy-first (no user accounts, ephemeral sessions)
- Crisis detection with immediate resource display
- Plain language responses (8th grade reading level)
- Source citations for all answers

## Core Architecture Principle: Modularity

The system is designed with a microservices mindset where every component is independently swappable through well-defined interfaces:
- **Interface-Based Design**: All components communicate through interfaces defined in `backend/services/interfaces.py`
- **Dependency Injection**: Services are created via `ServiceFactory` in `backend/services/service_factory.py`
- **Loose Coupling**: Components can be swapped (e.g., pgvector → Elasticsearch) without rewriting the system
- **Single Responsibility**: Each service handles one clear concern


## Essential Commands

### Development
```bash
# Option A: Docker (from project root)
docker-compose up --build

# Option B: Local with hot reload (from project root)
npm run dev

# See README.md for detailed setup instructions
```

### Testing & Quality
```bash
# Type check (MUST pass before committing)
npm run typecheck

# Lint
npm run lint

# Run backend tests
cd backend && python -m pytest
```

### Production
```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up --build

# See DEPLOYMENT.md for full deployment guide
```

### Document Ingestion
```bash
cd backend
python scripts/ingest_documents.py
```

## High-Level Architecture

### Backend Structure (FastAPI + RAG Pipeline)

The backend follows a layered architecture with dependency injection:

```
backend/
├── main.py                    # FastAPI app entry point
├── api/
│   ├── routes.py             # API endpoints (uses dependency injection)
│   └── models.py             # Pydantic request/response models
├── services/
│   ├── interfaces.py         # Interface definitions for all services
│   ├── service_factory.py    # Creates services with proper dependencies
│   ├── rag_pipeline.py       # Orchestrates: retrieval → LLM → response
│   ├── retrieval.py          # Vector similarity search
│   ├── vector_store.py       # Supabase pgvector operations
│   ├── embeddings.py         # sentence-transformers wrapper
│   ├── llm_service.py        # Gemini API integration
│   ├── crisis_detection.py   # Keyword-based crisis detection
│   ├── document_processor.py # PDF/DOCX/HTML text extraction
│   ├── ingestion.py          # Document chunking and storage
│   └── supabase_client.py    # Supabase client initialization
├── config/
│   ├── documents.json        # Document metadata configuration
│   └── document_config.py    # Document config loader
└── scripts/
    └── ingest_documents.py   # Script to ingest docs into vector store
```

**Key Architecture Points:**
1. **Dependency Injection**: All services implement interfaces from `interfaces.py` and are created via `ServiceFactory`
2. **RAG Pipeline Flow** (`rag_pipeline.py:process_query()`):
   - Crisis Detection → Query Embedding → Vector Search → Context Assembly → LLM Generation → Citation Injection
3. **Vector Store**: Uses Supabase pgvector with cosine similarity for semantic search
4. **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
5. **LLM**: Google Gemini 1.5 Flash via google-generativeai SDK

### Frontend Structure (React + TypeScript)

```
frontend/src/
├── main.tsx                  # Entry point
├── App.tsx                   # Main app with routing
├── pages/
│   ├── Home.tsx             # Main query interface
│   └── About.tsx            # About page
├── components/
│   ├── SearchInput.tsx      # Query input component
│   ├── QueryResponse.tsx    # Response display with citations
│   ├── Layout.tsx           # Page layout wrapper
│   ├── Sidebar.tsx          # Navigation sidebar
│   ├── DarkModeToggle.tsx   # Theme switcher
│   └── PrivacyModal.tsx     # Privacy policy modal
├── contexts/
│   └── DarkModeContext.tsx  # Theme state management
└── services/
    └── api.ts               # Backend API client (fetch wrapper)
```

**Key Architecture Points:**
1. **Routing**: react-router-dom for navigation
2. **State Management**: React Context for dark mode, local state for query/response
3. **Styling**: CSS Modules (`.module.css` files) for scoped styles
4. **API Communication**: `services/api.ts` centralizes all backend calls
5. **Accessibility**: WCAG 2.2 AA compliant with keyboard navigation and screen reader support

## Code Style Guidelines

### Python (Backend)
- **Type hints required** for all function signatures
- **Async/await** for I/O operations (Supabase calls, LLM API)
- **Pydantic models** for all API request/response validation
- **Descriptive names**: `embedding_vector`, `document_chunks`, `retrieved_context`
- **Docstrings**: Google style for all public methods
- **Max line length**: 100 characters

### TypeScript/React (Frontend)
- **ES modules only**: `import/export` (not CommonJS `require`)
- **Functional components** with hooks (no class components)
- **Strict TypeScript**: Comprehensive type definitions, no `any`
- **Async/await**: Preferred over Promise chains
- **Descriptive names**: `queryResponse`, `crisisDetected`, `citationList`

## Development Workflow

### Before Committing
```bash
# Always run these before committing:
npm run typecheck  # Type check TypeScript (must pass)
npm run lint       # Lint frontend code
cd backend && python -m pytest  # Run backend tests (if you modified backend)
```

### Branch Naming Convention
- `feature/query-processing` - New features
- `fix/crisis-detection-bug` - Bug fixes
- `docs/api-documentation` - Documentation
- `refactor/rag-pipeline` - Code refactoring

### Commit Messages (Conventional Commits)
```
feat: add crisis detection to RAG pipeline
fix: correct embedding dimension mismatch
docs: update API endpoint documentation
test: add unit tests for query sanitization
refactor: simplify LLM prompt construction
```

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root with:

```bash
# Supabase (get from https://app.supabase.com/project/YOUR_PROJECT/settings/api)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Google Gemini API (get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_gemini_api_key_here

# Generate with: openssl rand -hex 32
SECRET_KEY=your_random_secret_key_here

# Usually can use defaults
ENVIRONMENT=development
```

**IMPORTANT**:
- Never commit `.env` files
- Use `.env.example` as a template
- The sentence-transformers library downloads an ~80MB model on first run (normal, happens once)

## Critical Domain Requirements

### Crisis Detection (HIGHEST PRIORITY)
**Implementation**: `backend/services/crisis_detection.py`

Crisis detection must NEVER fail or delay responses:
- Keyword monitoring: suicide, self-harm, harm to others, severe distress
- Response: Inject 988 Suicide & Crisis Lifeline IMMEDIATELY
- Always return crisis resources FIRST, then answer
- Log de-identified flag only (NEVER log query content)

### RAG Pipeline Configuration
**Implementation**: `backend/services/rag_pipeline.py`

- **Document chunks**: 200-800 tokens (optimal for all-MiniLM-L6-v2)
- **Chunk overlap**: 50 tokens (maintains context continuity)
- **Retrieval**: Top 5 most similar chunks via Supabase pgvector cosine similarity
- **Embedding model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM context window**: Max 2000 tokens for Gemini 1.5 Flash
- **Vector storage**: Supabase PostgreSQL with pgvector extension

### Plain Language Responses
All responses MUST meet:
- Reading level: 8th grade or below (Flesch-Kincaid test)
- Sentence length: < 20 words average
- Active voice preferred
- Complex processes → numbered steps
- Define technical terms inline

### Document Configuration
**File**: `backend/config/documents.json`

When adding documents to the RAG system, configure metadata in `documents.json`:
```json
{
  "your_doc_key": {
    "title": "Document Title",
    "topic": "Education",
    "audience": ["families", "providers"],
    "content_type": "ProceduralGuide",  // or FAQ, LegalRights, ResourceDirectory, etc.
    "source_org": "Organization Name",
    "authority_level": 2  // 1=highest, 3=lowest (affects retrieval ranking)
  }
}
```

Then run: `cd backend && python scripts/ingest_documents.py`

## Security & Privacy (CRITICAL)

### Privacy-First Design
**NEVER**:
- Store user queries beyond active session
- Store email addresses long-term
- Log PII in any form (including query content)

**Session Management**:
- Ephemeral session IDs only
- Clear session data after 1 hour inactivity
- No tracking cookies

### Input Validation
**Implementation**: All API endpoints use Pydantic models (`backend/api/models.py`)

- Max query length: 500 characters
- Rate limiting: 10 queries/minute per IP
- Supabase client has built-in SQL injection protection
- Sanitize all user input before processing

### API Security
- CORS: Whitelist only `http://localhost:5173` (dev) and production frontend URL
- No user authentication (account-free by design)
- HTTPS required in production
- Pydantic validation on all requests

## Testing

### Backend Tests
**Run**: `cd backend && python -m pytest`

- Test files: `backend/tests/`
- Framework: pytest with pytest-asyncio
- Key test files:
  - `rag_pipeline_test.py` - RAG pipeline integration tests
  - `retrieval_test.py` - Vector search tests

### Frontend Testing
Not yet implemented. When adding:
- Use Vitest for unit tests
- React Testing Library for component tests
- Test accessibility with axe-core

## Common Issues & Troubleshooting

### Slow Query Performance
1. Check Supabase pgvector index in dashboard
2. Verify embedding dimension is 384 (all-MiniLM-L6-v2)
3. Monitor Supabase connection limits (free tier: 60 connections)
4. Check Supabase dashboard performance metrics

### Crisis Detection Not Working
- Implementation: `backend/services/crisis_detection.py`
- Verify keyword list is loaded correctly
- Test with exact phrases from test suite
- Check logs for crisis flag activation

### First-Time Setup Issues
- **"Model not found"**: sentence-transformers downloads ~80MB model on first run (normal)
- **Supabase connection error**: Verify `SUPABASE_URL` and keys in `.env`
- **CORS error**: Check `backend/main.py` allows frontend origin (`http://localhost:5173`)

## Additional Documentation

For more detailed information, see:
- [01_README.md](/01_README.md) - Project overview and quick start
- [04_LOCAL_SETUP.md](/04_LOCAL_SETUP.md) - Local development setup guide
- [03_DOCKER_SETUP.md](/03_DOCKER_SETUP.md) - Docker development guide
- [05_DEPLOYMENT.md](/05_DEPLOYMENT.md) - Production deployment guide
- [06_ARCHITECTURE.md](./06_ARCHITECTURE.md) - Detailed system architecture
- [SPECS.md](./SPECS.md) - User stories and requirements

