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

**For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md)**

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account (free tier)
- Google Cloud account (for Gemini API)

### Rapid Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/autism-chat-bot.git
cd autism-chat-bot

# 2. Set up environment variables
cp .env.example .env
cp frontend/.env.example frontend/.env.local
# Edit .env with your Supabase and Gemini credentials

# 3. Install backend dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Set up Supabase database
# Run backend/scripts/supabase_setup.sql in Supabase SQL Editor

# 5. Install frontend dependencies
npm install

# 6. Start backend (terminal 1)
cd backend
python -m uvicorn main:app --reload

# 7. Start frontend (terminal 2)
npm run dev
```

Visit `http://localhost:5173` to use the application!

## Project Structure

```
nc-ask/
├── backend/                    # FastAPI backend
│   ├── api/                   # API routes and models
│   │   ├── routes.py         # API endpoints
│   │   └── models.py         # Pydantic models
│   ├── services/              # Core business logic
│   │   ├── config.py         # Configuration
│   │   ├── supabase_client.py # Supabase integration
│   │   ├── embeddings.py     # Sentence transformers
│   │   ├── document_processor.py # Document chunking
│   │   ├── ingestion.py      # Document ingestion
│   │   ├── retrieval.py      # Vector search
│   │   ├── llm_service.py    # Gemini integration
│   │   ├── crisis_detection.py # Crisis detection
│   │   └── rag_pipeline.py   # Main RAG orchestrator
│   ├── scripts/               # Utility scripts
│   │   ├── ingest_documents.py # Document ingestion
│   │   └── supabase_setup.sql # Database schema
│   ├── data/                  # Source documents
│   ├── tests/                 # Tests
│   └── main.py               # FastAPI app entry point
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── CrisisBanner.tsx
│   │   │   ├── QueryResponse.tsx
│   │   │   ├── SearchInput.tsx
│   │   │   └── ...
│   │   ├── pages/            # Page components
│   │   │   ├── Home.tsx
│   │   │   └── About.tsx
│   │   ├── services/         # API client
│   │   │   └── api.ts
│   │   └── main.tsx          # App entry point
│   └── ...
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── ROADMAP.md            # Development roadmap
│   ├── CLAUDE.md             # Development guidelines
│   └── SETUP.md              # Setup instructions
│
├── .env.example               # Environment template
├── docker-compose.yml         # Docker configuration
├── requirements.txt           # Python dependencies
└── package.json              # Node.js dependencies
```

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

## Documentation

- **[SETUP.md](docs/SETUP.md)**: Complete setup instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture and data flow
- **[ROADMAP.md](docs/ROADMAP.md)**: 8-week development roadmap
- **[CLAUDE.md](docs/CLAUDE.md)**: Development guidelines and conventions

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (future)
npm run test
```

### Type Checking

```bash
# Frontend TypeScript
npm run typecheck

# Backend (via mypy, if configured)
cd backend
mypy .
```

### Linting

```bash
# Frontend
npm run lint

# Backend
cd backend
flake8 .
```

### Adding Documents

1. Place documents in `backend/data/`
2. Run ingestion script:
   ```bash
   cd backend
   python scripts/ingest_documents.py
   ```

## Key Workflows

### Query Processing Flow
1. User submits question via frontend
2. Frontend sends request to `/api/query`
3. Backend validates and sanitizes input
4. Crisis detection checks for urgent keywords
5. Query embedding generated via sentence-transformers
6. Vector similarity search in Supabase pgvector
7. Top-k relevant chunks retrieved
8. Context assembled and sent to Gemini
9. LLM generates plain language response
10. Disclaimers and citations added
11. If crisis detected, resources prepended
12. Response returned to frontend

### Document Ingestion Flow
1. Documents placed in `backend/data/`
2. Ingestion script extracts text (PDF, DOCX, HTML, TXT)
3. Files uploaded to Supabase Storage
4. Text chunked semantically (200-800 tokens)
5. Embeddings generated for each chunk
6. Vectors and metadata stored in Supabase
7. Automatic indexing for similarity search

## Environment Variables

### Backend (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GOOGLE_API_KEY=your_gemini_api_key
SECRET_KEY=your_random_secret_key
```

### Frontend (frontend/.env.local)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## MVP Success Criteria

### Technical Metrics
- ✅ 95%+ uptime
- ✅ < 5 second query response time (p95)
- ✅ 95%+ crisis detection accuracy
- ✅ 0 privacy violations

### User Metrics
- ✅ 80%+ query answering accuracy
- ✅ 4/5 average user satisfaction
- ✅ WCAG 2.2 AA compliance

## Current Status

### Phase 0: Project Setup ✅ COMPLETE
- Backend FastAPI structure
- Supabase client configuration
- Frontend React + TypeScript setup
- Development environment

### Phase 1: Core RAG Pipeline ✅ COMPLETE
- Document ingestion system
- Embedding generation (sentence-transformers)
- Vector similarity search (Supabase pgvector)
- LLM integration (Gemini 1.5 Flash)
- Query processing pipeline
- API endpoints

### Phase 2: Safety & Crisis Features ✅ COMPLETE
- Crisis keyword detection
- Crisis resource database
- Crisis banner UI component
- Safety guardrails

### Next Steps
See [ROADMAP.md](docs/ROADMAP.md) for remaining phases:
- Phase 3: Plain Language & Accessibility
- Phase 4: Core Features & Polish
- Phase 5: Testing & Documentation
- Phase 6: Deployment & Launch

## Contributing

This is a university course project (COMP 523). For questions or issues:
1. Check existing documentation in `docs/`
2. Review code comments
3. Contact the team

## License

[To be determined by client and university]

## Acknowledgments

- Dr. Rohan Patel - Project client and domain expert
- UNC COMP 523 teaching staff
- North Carolina autism services community

## Support Resources

For autism services information in North Carolina:
- **NC Autism Society**: 1-800-442-2762
- **NC DHHS**: 1-800-662-7030
- **Crisis Support**: 988 (24/7)

---

**Note**: This is an educational tool providing general information. It is not a substitute for professional medical, legal, or therapeutic advice.