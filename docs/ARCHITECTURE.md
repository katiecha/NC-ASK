# NC-ASK System Architecture

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS Modules (as per current implementation)
- **State Management**: React hooks (useState, useContext)
- **HTTP Client**: Fetch API / Axios

### Backend
- **API Framework**: FastAPI (Python 3.11+)
- **Document Processing**: LangChain
- **Database**: Supabase (PostgreSQL 15+ with pgvector extension)
- **Storage**: Supabase Storage (for source documents)
- **Caching**: Redis (optional for MVP)

### AI/ML Components
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (Hugging Face)
- **LLM**: Google Gemini 2.5 Flash-lite
- **Orchestration**: LangChain for RAG pipeline

### Infrastructure
- **Containerization**: Docker + Docker Compose (local dev)
- **Deployment**: Render/Railway (FastAPI) + Supabase (Database)
- **Email Service**: SendGrid API
- **CI/CD**: GitHub Actions

### Security & Governance
- NC ASK Security Guidelines: /autism-chat-bot/docs/NC ASK AI S&G Guiding Principles v0.docx
- AI Safety & Governance Guidelines

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                          │
│  (Mobile Browser / Desktop Browser - No Login Required)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Frontend (React/Vite)                         │
│                   Hosted on Vercel                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Search UI    │  │ Crisis Banner│  │ Email Export │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                               │
│              Hosted on Render/Railway                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Gateway Layer                       │   │
│  │  - Rate Limiting                                     │   │
│  │  - Input Validation                                  │   │
│  │  - CORS Configuration                                │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────▼───────────────────────────────────────┐   │
│  │           RAG Pipeline (LangChain)                   │   │
│  │                                                       │   │
│  │  1. Query Processing                                 │   │
│  │     - Sanitization                                   │   │
│  │     - Crisis Detection                               │   │
│  │     - Query Embedding (sentence-transformers)       │   │
│  │                                                       │   │
│  │  2. Document Retrieval                               │   │
│  │     - Vector Similarity Search (Supabase)           │   │
│  │     - Metadata Filtering                             │   │
│  │     - Re-ranking                                     │   │
│  │                                                       │   │
│  │  3. Response Generation                              │   │
│  │     - Context Assembly                               │   │
│  │     - LLM Prompting (Gemini)                        │   │
│  │     - Plain Language Simplification                  │   │
│  │     - Citation Injection                             │   │
│  │                                                       │   │
│  │  4. Safety Layer                                     │   │
│  │     - Crisis Flag Detection                          │   │
│  │     - Disclaimer Injection                           │   │
│  │     - Response Validation                            │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│ Supabase │ │ Gemini  │ │SendGrid  │
│PostgreSQL│ │ API     │ │ API      │
│+ pgvector│ │         │ │          │
│+ Storage │ │- LLM    │ │- Email   │
│- Vectors │ │  Calls  │ │  Export  │
│- Metadata│ │         │ │          │
│- Files   │ │         │ │          │
└──────────┘ └─────────┘ └──────────┘
```

## Data Flow

### Query Processing Flow
1. **User submits query** via frontend search interface
2. **Frontend** sends HTTPS POST request to `/api/query` endpoint
3. **API Gateway** validates input, checks rate limits
4. **Query Processor** sanitizes and analyzes query
5. **Crisis Detector** checks for crisis keywords/patterns
6. **Embedding Service** converts query to vector using sentence-transformers
7. **Vector Search** queries pgvector for similar document chunks
8. **Context Builder** assembles retrieved chunks with metadata
9. **LLM Service** sends context + query to Gemini 2.5 Flash-lite
10. **Response Processor** simplifies language, adds citations
11. **Safety Layer** injects disclaimers/crisis resources if needed
12. **API** returns JSON response to frontend
13. **Frontend** renders response with citations and resources

### Document Ingestion Flow (Admin/Setup)
1. Source documents uploaded to FastAPI ingestion endpoint
2. **Document Parser** (FastAPI) extracts text (PDF, DOCX, HTML, etc.)
3. **File Storage** uploads original files to Supabase Storage
4. **Chunker** (FastAPI) splits documents into semantic chunks (200-800 tokens)
5. **Metadata Extractor** (FastAPI) tags chunks with source, type, category
6. **Embedding Generator** (FastAPI) creates vectors using sentence-transformers
7. **Database Writer** (FastAPI) stores vectors + metadata in Supabase PostgreSQL/pgvector
8. **Index** automatically updated for similarity search

## API Endpoints

### Core Endpoints (MVP)

#### POST `/api/query`
Query the system with a natural language question.

**Request:**
```json
{
  "query": "How do I request an IEP evaluation?",
  "session_id": "optional-ephemeral-id"
}
```

**Response:**
```json
{
  "response": "To request an IEP evaluation in North Carolina...",
  "citations": [
    {
      "title": "NC IEP Process Guide",
      "url": "https://...",
      "relevance_score": 0.92
    }
  ],
  "crisis_detected": false,
  "disclaimers": ["This is general information..."]
}
```

#### POST `/api/email-export` (Post-MVP)
Email conversation or response to user.

**Request:**
```json
{
  "email": "user@example.com",
  "content": "Response text to send",
  "session_id": "abc123"
}
```

#### GET `/api/health`
Health check endpoint for monitoring.

#### GET `/api/crisis-resources`
Get static list of crisis resources (cached, high availability).

## Database Schema

### documents table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT,
    content_type VARCHAR(50),
    file_path TEXT,  -- Supabase Storage path
    upload_date TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
```

### document_chunks table
```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    embedding vector(384),  -- all-MiniLM-L6-v2 dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Supabase automatically creates pgvector indexes
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

### crisis_resources table (static)
```sql
CREATE TABLE crisis_resources (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    url TEXT,
    description TEXT,
    priority INTEGER,
    active BOOLEAN DEFAULT true
);
```

## Security Considerations

### Privacy Protection
- **No user accounts**: No PII collection required
- **Ephemeral sessions**: Session IDs are temporary, not stored long-term
- **No query logging**: Queries logged in de-identified format only for monitoring
- **No cookies**: Use sessionStorage only, no persistent tracking

### Input Validation
- Query length limits (max 500 characters)
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization
- Rate limiting: 10 queries per minute per IP

### Crisis Detection
- Keyword matching for crisis terms
- Immediate resource injection
- High-priority logging (de-identified)
- No delay in response delivery

## Deployment Architecture

### Docker Compose (Local Development)
```yaml
services:
  - frontend (Vite dev server)
  - backend (FastAPI with hot reload)
  # Note: Uses Supabase cloud for database/storage
  - redis (optional, for caching)
```

### Production Deployment
- **Frontend**: Vercel (free tier)
- **Backend**: Render/Railway (FastAPI containers)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Storage**: Supabase Storage (for documents)
- **CDN**: Vercel Edge Network
- **Monitoring**: Supabase Dashboard + FastAPI logs

## Performance Targets

### MVP Targets
- Query response time: < 5 seconds (p95)
- Concurrent users: 10-20
- Supabase queries: < 100ms (built-in optimization)
- LLM latency: < 3 seconds
- Embedding generation: < 500ms

### Scalability Considerations (Post-MVP)
- Horizontal scaling of FastAPI instances (Render/Railway)
- Supabase read replicas (Pro plan)
- Redis caching layer for frequent queries
- Vercel Edge Functions for static responses
- Supabase connection pooling (built-in)

