# NC ASK RAG System Architecture: Current State & OpenShift Migration Path

## Introduction

This document describes the current system architecture for the North Carolina ASK (NC ASK) proof-of-concept and provides a roadmap for migrating to a production-ready deployment on OpenShift. The goal is to build a privacy-focused retrieval-augmented generation (RAG) system that provides anonymous access to NC policy information while maintaining complete data residency and user privacy.

**Key Design Principles:**
- **User Privacy First** - No external services with access to user queries
- **Data Residency** - All data remains on state-controlled infrastructure
- **Modularity** - Services can be independently upgraded or replaced
- **Portability** - Clear migration path from POC to production

---

## 1. Current State - Proof of Concept

The POC implements a functional RAG pipeline using managed cloud services for rapid development. It demonstrates core capabilities while we refine features and gather user feedback before migrating to self-hosted infrastructure.

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Development Stack                    │
│                                                         │
│  ┌──────────────┐         ┌─────────────────┐           │
│  │   Frontend   │         │   FastAPI       │           │
│  │ React+Vite   │────────▶│   Backend       │           │
│  │  TypeScript  │         │   (Python 3.11) │           │
│  └──────────────┘         └────────┬────────┘           │
│                                    │                    │
│                                    ▼                    │
│                          ┌──────────────────┐           │
│  ┌──────────────┐        │  RAG Pipeline    │           │
│  │  Supabase    │◀───────│  Orchestration   │           │
│  │  PostgreSQL  │        └────────┬─────────┘           │
│  │  + pgvector  │                 │                     │
│  └──────────────┘                 ▼                     │
│                          ┌──────────────────┐           │
│  ┌──────────────┐        │  Document        │           │
│  │  Supabase    │◀───────│  Processing      │           │
│  │  Storage     │        └──────────────────┘           │
│  └──────────────┘                                       │
│                                                         │
│  ┌─────────────────────────────────┐                    │
│  │    Google Gemini 1.5 Flash      │                    │
│  │    (External API)               │◀──────────┐        │
│  └─────────────────────────────────┘           │        │
│                                                │        │
│                               ┌────────────────┴──┐     │
│                               │  LLM Service      │     │
│                               └───────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Component Overview

| Layer/Service | Technology | Description |
|---------------|------------|-------------|
| **User Interface** | React 18 + TypeScript + Vite | Web front-end with view selector (Provider/Patient), search interface, and response display with citations. Includes dark mode and accessibility features. |
| **API Layer** | FastAPI 0.104.1 | RESTful API with dependency injection pattern. Orchestrates document ingestion, retrieval, and response generation. |
| **Document Processing** | Custom Implementation | Text extraction using PyPDF2 (PDF), python-docx (DOCX), BeautifulSoup4 (HTML). Smart chunking with sentence boundary detection (500 chars/chunk, 50 char overlap). |
| **Embeddings** | sentence-transformers | Local embedding generation using all-MiniLM-L6-v2 model (384 dimensions). Batch processing for efficiency. |
| **Vector Store** | Supabase (PostgreSQL + pgvector) | Stores document chunks and embeddings. Uses IVFFlat index with cosine similarity search. Custom RPC function for efficient retrieval. |
| **Object Storage** | Supabase Storage | Stores original uploaded documents and metadata. |
| **Retrieval & Orchestration** | Custom RAG Pipeline | Executes vector similarity search, assembles context window with token limits, formats citations, and manages view-specific prompts. |
| **Model Service** | Google Gemini 1.5 Flash | Hosted LLM for answer generation. **Note: Will be replaced with self-hosted model for production.** |
| **Crisis Detection** | Keyword-based System | Detects crisis keywords (suicide, self-harm, abuse) and displays immediate resources (988 Lifeline, Crisis Text Line, NC Hope4NC). Three severity levels: Critical, High, Moderate. |
| **Deployment** | Docker Compose | Multi-container setup for local development with hot reload. Separate dev and prod configurations. |

### 1.3 Data Flow

**Document Ingestion:**
1. User uploads document via frontend
2. File stored in Supabase Storage, metadata in `documents` table
3. Text extracted based on file type (PDF/DOCX/HTML/TXT)
4. Content split into chunks with overlap (500/50 chars)
5. Chunks embedded using sentence-transformers (batch processing)
6. Embeddings and chunks stored in `document_chunks` table with vector index

**Query & Response:**
1. User submits question with selected view (Provider or Patient)
2. Backend sanitizes input and validates query length
3. Crisis detection scans for emergency keywords
4. Query embedded using same model (all-MiniLM-L6-v2)
5. Vector similarity search retrieves top-5 relevant chunks (cosine similarity)
6. Chunks formatted into context window (max 2000 tokens ≈ 8000 chars)
7. View-specific system prompt applied with few-shot examples
8. LLM generates response based on retrieved context
9. Medical/legal disclaimers added automatically
10. Crisis resources prepended if crisis detected
11. Response returned with source citations

**View-Based Response Tailoring:**
- **Provider View**: Clinical tone, medical terminology, evidence-based language
- **Patient View**: Plain language (8th grade reading level), empathetic tone, simplified explanations
- Each view has custom system prompt and few-shot examples
- Frontend view selector allows users to choose perspective

### 1.4 Key Features

**Currently Implemented:**
- Natural language Q&A with source citations
- View-based response tailoring (Provider/Patient)
- Crisis detection with immediate resource display
- Multi-format document support (PDF, DOCX, HTML, TXT)
- Vector similarity search with pgvector
- Input sanitization and validation
- Medical/legal disclaimer automation
- Dark mode support
- Mobile-responsive UI
- Privacy-focused (no PII storage, ephemeral sessions)
- Docker-based development environment

**Post-POC / Production Features:**
- Self-hosted LLM (planned for OpenShift migration)
- Hybrid search (BM25 + vector fusion)
- Response caching for common queries
- User feedback collection and quality metrics
- Analytics dashboard for monitoring
- Kubernetes/OpenShift deployment
- Email export (optional, SendGrid integration)

### 1.5 Technology Stack

**Frontend:**
- React 18.2.0
- TypeScript 5.0.2
- Vite 4.4.9 (build tool)
- React Router DOM 6 (routing)
- React Markdown (response rendering)
- CSS Modules (styling)

**Backend:**
- Python 3.11+
- FastAPI 0.104.1
- Uvicorn 0.24.0 (ASGI server)
- sentence-transformers 2.3.0+ (embeddings)
- PyPDF2 3.0.1 (PDF extraction)
- python-docx 1.1.0 (DOCX extraction)
- BeautifulSoup4 4.12.2 (HTML parsing)
- google-generativeai 0.3.1 (Gemini API)

**Data & Storage:**
- Supabase (PostgreSQL 15+ with pgvector)
- Supabase Storage (object storage)
- Vector dimension: 384 (all-MiniLM-L6-v2)

**Deployment:**
- Docker & Docker Compose
- Multi-stage builds for dev/prod
- Health check endpoints

---

## 2. Production State - OpenShift Migration

The production architecture migrates all services to OpenShift for complete data residency and user privacy. External managed services (Supabase, Google Gemini) are replaced with self-hosted alternatives while maintaining the same interfaces.

### 2.1 Design Principles

**Privacy & Compliance:**
- **Zero external API calls** - No user queries sent to third-party services
- **Data residency** - All data remains on NC state infrastructure
- **Anonymity** - No user tracking or PII collection
- **Audit logging** - Complete query/response logging for transparency

**Technical Architecture:**
- **Modularity** - Services communicate via well-defined APIs
- **Loose coupling** - Each service can be developed and scaled independently
- **Interface-based design** - Easy to swap implementations (already implemented via service factory pattern)
- **Infrastructure as Code** - Kubernetes manifests and Helm charts for reproducible deployments

### 2.2 Production Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      OpenShift Cluster                           │
│                                                                  │
│  ┌─────────────────┐          ┌──────────────────┐               │
│  │    Frontend     │          │   FastAPI        │               │
│  │  React + Vite   │─────────▶│   Backend        │               │
│  │    (nginx)      │          │                  │               │
│  │  Deployment     │          │  Deployment (3x) │               │
│  └─────────────────┘          └────────┬─────────┘               │
│                                        │                         │
│  ┌─────────────────┐          ┌────────▼─────────┐               │
│  │  PostgreSQL 15  │◀─────────│  Vector Store    │               │
│  │   + pgvector    │          │    Service       │               │
│  │  StatefulSet    │          └──────────────────┘               │
│  └─────────────────┘                                             │
│                                                                  │
│  ┌─────────────────┐          ┌──────────────────┐               │
│  │     MinIO       │◀─────────│   Document       │               │
│  │ Object Storage  │          │   Ingestion      │               │
│  │  StatefulSet    │          └──────────────────┘               │
│  └─────────────────┘                                             │
│                                                                  │
│  ┌──────────────────────────────────────────┐                    │
│  │         vLLM Model Server                │                    │
│  │    Llama 3.1 8B (4-bit quantized)        │                    │
│  │         GPU Node (1x GPU)                │◀──────────┐        │
│  │    OpenAI-compatible API                 │           │        │
│  └──────────────────────────────────────────┘           │        │
│                                                         │        │
│                                        ┌────────────────┴────┐   │
│                                        │   RAG Pipeline      │   │
│                                        │   Orchestrator      │   │
│                                        └─────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │            Optional Future Enhancements                  │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐   │    │
│  │  │   Redis     │  │  Monitoring  │  │   Analytics    │   │    │
│  │  │   Cache     │  │  Prometheus  │  │   Dashboard    │   │    │
│  │  └─────────────┘  └──────────────┘  └────────────────┘   │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Migration Components

| Component | Current (POC) | Production (OpenShift) | Migration Effort |
|-----------|---------------|------------------------|------------------|
| **Vector Store** | Supabase PostgreSQL | Self-hosted PostgreSQL 15 + pgvector on OpenShift | **Medium** - Export/import data, update connection string |
| **Object Storage** | Supabase Storage | MinIO on OpenShift | **Medium** - Download/re-upload files, update storage service |
| **LLM Service** | Google Gemini API | vLLM with Llama 3.1 8B (self-hosted) | **High** - Deploy vLLM, test quality, tune parameters |
| **Frontend** | Docker (dev) | OpenShift Deployment with nginx | **Low** - Create K8s manifests, build production image |
| **Backend** | Docker (dev) | OpenShift Deployment (3 replicas) | **Low** - Create K8s manifests, configure for K8s |
| **Embeddings** | Local (sentence-transformers) | Same (runs on backend pods) | **None** - Already self-hosted |

### 2.4 Self-Hosted LLM Strategy

**Model Selection Criteria:**
- Quality comparable to Gemini 1.5 Flash
- Fits on available GPU infrastructure (1-2 GPUs per node)
- Open-source with permissive license
- Good instruction-following and RAG performance

**Recommended Model: Llama 3.1 8B Instruct**
- **Size:** 8B parameters
- **Quantization:** 4-bit (GPTQ or AWQ) → ~4.5GB VRAM
- **Performance:** Excellent instruction-following, good factual accuracy
- **License:** Llama 3.1 Community License (permissive for government use)
- **Alternative:** Mistral 7B v0.3 (faster inference, slightly lower quality)

**Deployment Stack:**
- **Serving:** vLLM 0.5+ (fast inference with PagedAttention)
- **API:** OpenAI-compatible endpoint
- **Scaling:** 1-2 replicas initially, scale based on load
- **GPU Requirement:** 1x GPU with 16GB+ VRAM per replica

**Quality Validation Process:**
1. Deploy vLLM with Llama 3.1 8B in test environment
2. Run evaluation set (50-100 representative queries)
3. Compare responses to current Gemini baseline
4. Tune parameters (temperature, top_p, repetition_penalty)
5. Measure latency (target: <5s p95)
6. Validate medical/policy accuracy with domain experts

### 2.5 Infrastructure Requirements

**Compute:**
- **Frontend:** 2 pods, 0.5 CPU / 512MB RAM each
- **Backend:** 3 pods, 1 CPU / 2GB RAM each
- **PostgreSQL:** 1 pod, 2 CPU / 4GB RAM
- **MinIO:** 1 pod, 1 CPU / 2GB RAM
- **vLLM:** 1-2 pods, 4 CPU / 16GB RAM + 1 GPU (16GB VRAM) each

**Storage:**
- **PostgreSQL:** 100GB persistent volume (SSD)
- **MinIO:** 500GB persistent volume (can scale)
- **Model weights:** 10GB persistent volume (read-only)

**Network:**
- Internal service mesh for inter-pod communication
- External ingress for frontend (HTTPS)
- TLS/mTLS for all service-to-service communication

### 2.6 Deployment Strategy

**Phase 1: Infrastructure Setup (Weeks 1-4)**
1. Create OpenShift project/namespace
2. Deploy PostgreSQL StatefulSet with pgvector
3. Deploy MinIO StatefulSet
4. Create Kubernetes manifests for frontend/backend
5. Create Helm chart for full stack
6. Test in development OpenShift environment

**Phase 2: Data Migration (Weeks 2-4)**
1. Export documents from Supabase Storage → MinIO
2. Export database from Supabase → OpenShift PostgreSQL
3. Validate data integrity (checksums, row counts)
4. Test retrieval functionality

**Phase 3: LLM Deployment (Weeks 4-8)**
1. Deploy vLLM on GPU nodes
2. Test model quality vs Gemini baseline
3. Tune inference parameters
4. Implement self-hosted LLM service class
5. Update service factory to use self-hosted endpoint
6. Performance and load testing

**Phase 4: Testing & Cutover (Weeks 8-12)**
1. Parallel testing (current vs OpenShift)
2. Security review and hardening
3. Backup/disaster recovery testing
4. User acceptance testing
5. DNS/routing cutover
6. Monitor and iterate

---

## 3. Recommended Enhancements (Post-Migration)

These enhancements should be considered **after** successful OpenShift migration and POC refinement. Prioritize based on user feedback and measured performance gaps.

### 3.1 High-Priority Enhancements

**1. Hybrid Search (BM25 + Vector)**
- **What:** Combine keyword search (BM25) with vector similarity
- **Why:** Improves recall, handles exact term matching better
- **Effort:** Medium (requires BM25 index, fusion algorithm)
- **ROI:** High - proven to improve retrieval quality 10-15%
- **Implementation:** Use PostgreSQL full-text search + pgvector, reciprocal rank fusion

**2. Response Caching**
- **What:** Cache responses for common queries
- **Why:** Reduce latency and LLM costs for repeated questions
- **Effort:** Low (Redis deployment, cache key logic)
- **ROI:** High - instant responses for cached queries
- **Implementation:** Redis cluster, cache key = hash(query + view + top chunks)

**3. Monitoring & Quality Metrics**
- **What:** Track retrieval quality, response accuracy, latency, errors
- **Why:** Validate system performance, identify degradation
- **Effort:** Medium (Prometheus + Grafana setup, custom metrics)
- **ROI:** High - essential for production operations
- **Metrics:** Query latency, retrieval relevance, user feedback, error rates

**4. User Feedback Collection**
- **What:** Thumbs up/down on responses, optional comments
- **Why:** Identify bad responses, measure user satisfaction
- **Effort:** Low (frontend UI, backend endpoint, database table)
- **ROI:** High - direct signal for system improvement

### 3.2 Medium-Priority Enhancements

**5. Re-Ranking with Cross-Encoder**
- **What:** Re-score top-K chunks with cross-encoder model for better relevance
- **Why:** Improves precision, reduces irrelevant context
- **Effort:** Medium (deploy cross-encoder, integrate into pipeline)
- **ROI:** Medium - validate retrieval quality issues first
- **Note:** Only implement if you measure retrieval quality problems

**6. Document Source Connectors**
- **What:** Automated ingestion from NC state websites, databases, APIs
- **Why:** Keep knowledge base current without manual uploads
- **Effort:** High (varies by source - web scraping, API integration, ETL)
- **ROI:** Medium-High - depends on document update frequency

**7. Advanced Chunking Strategies**
- **What:** Semantic chunking, section-aware splitting, metadata extraction
- **Why:** Better chunk quality improves retrieval accuracy
- **Effort:** Medium (implement new chunking logic, re-index documents)
- **ROI:** Medium - current chunking may be sufficient

### 3.3 Lower-Priority / Validate-Need-First

**8. Email Response Export**
- **What:** Send long responses via email (SendGrid integration)
- **Why:** Better UX for detailed answers, async workflow
- **Effort:** Low (SendGrid API, template design)
- **ROI:** Low-Medium - validate user demand first
- **Note:** May not be needed if responses are fast enough

**9. Multilingual Support**
- **What:** Translation for non-English speakers
- **Why:** Accessibility for diverse NC population
- **Effort:** High (translation API, multilingual embeddings, UI changes)
- **ROI:** Medium - depends on non-English user base size

**10. Personalization / Session Memory**
- **What:** Remember user context across questions in session
- **Why:** Better follow-up question handling
- **Effort:** Medium (session storage, context management)
- **ROI:** Medium - validate use case (most queries are single-shot)

### 3.4 NOT Recommended (At This Time)

**Knowledge Graphs**
- **Why skip:** High complexity, unclear ROI for policy documents, vector search likely sufficient
- **When to reconsider:** If you have structured data sources (databases, APIs) or measure specific relationship query failures

**Multi-Model Routing**
- **Why skip:** Modern LLMs handle multiple tasks well, routing adds complexity
- **When to reconsider:** If you need specialized models for specific tasks (unlikely)

---

## 4. Code Architecture (Current Implementation)

The codebase follows solid software engineering practices with clear separation of concerns and dependency injection.

### 4.1 Backend Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── routers/
│   ├── documents.py          # Document upload/management endpoints
│   ├── query.py              # RAG query endpoints
│   └── health.py             # Health check endpoints
├── services/
│   ├── service_factory.py    # Dependency injection factory
│   ├── interfaces.py         # Protocol-based interfaces
│   ├── rag_pipeline.py       # Main RAG orchestration
│   ├── document_processor.py # Text extraction & chunking
│   ├── embeddings.py         # Embedding generation
│   ├── vector_store.py       # Vector search (Supabase/pgvector)
│   ├── storage_service.py    # Object storage (Supabase Storage)
│   ├── llm_service.py        # LLM interface (Gemini)
│   ├── retrieval.py          # Retrieval orchestration
│   └── crisis_detection.py   # Crisis keyword detection
├── config/
│   ├── prompts.py            # System prompts (provider/patient views)
│   ├── examples.py           # Few-shot examples
│   └── document_config.py    # Document metadata
├── models/
│   └── schemas.py            # Pydantic models
└── scripts/
    ├── supabase_setup.sql    # Database schema
    └── ingest_documents.py   # Bulk ingestion script
```

### 4.2 Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchBar.tsx     # Query input with view selector
│   │   ├── Response.tsx      # Response display with markdown
│   │   ├── Citations.tsx     # Source citation display
│   │   ├── CrisisResources.tsx # Crisis banner
│   │   ├── ViewSelector.tsx  # Provider/Patient toggle
│   │   └── PrivacyModal.tsx  # Privacy information
│   ├── contexts/
│   │   ├── DarkModeContext.tsx # Dark mode state
│   │   └── ViewContext.tsx   # View selection state
│   ├── services/
│   │   └── api.ts            # API client (axios)
│   └── App.tsx               # Main application
└── public/                   # Static assets
```

### 4.3 Dependency Injection Pattern

The service factory pattern enables easy swapping of implementations:

```python
# services/service_factory.py
class ServiceFactory:
    def create_llm_service(self) -> LLMInterface:
        provider = os.getenv("LLM_PROVIDER", "gemini")
        if provider == "gemini":
            return GeminiLLM(api_key=os.getenv("GOOGLE_API_KEY"))
        elif provider == "self-hosted":
            return SelfHostedLLM(endpoint=os.getenv("VLLM_ENDPOINT"))

    def create_vector_store(self) -> VectorStoreInterface:
        # Can swap Supabase → self-hosted PostgreSQL easily
        return SupabaseVectorStore(...)
```

**For OpenShift Migration:**
- Add `SelfHostedLLM` class (vLLM client)
- Add `MinIOStorageService` class (MinIO client)
- Update `PostgresVectorStore` class (direct PostgreSQL connection)
- **No changes to routers or orchestration logic**

---

## 5. Migration Checklist

Use this checklist when ready to migrate (3+ months from now):

### Pre-Migration
- [ ] POC feature-complete and tested
- [ ] User feedback incorporated
- [ ] OpenShift project/namespace created
- [ ] GPU nodes allocated and tested
- [ ] Persistent volume storage provisioned
- [ ] Network/ingress configuration approved
- [ ] Security review completed

### Infrastructure Deployment
- [ ] PostgreSQL StatefulSet deployed
- [ ] pgvector extension installed and tested
- [ ] MinIO StatefulSet deployed
- [ ] Object storage buckets created
- [ ] Frontend deployment created (nginx + React)
- [ ] Backend deployment created (FastAPI, 3 replicas)
- [ ] vLLM deployment created (GPU nodes)
- [ ] Health checks passing for all services

### Code Changes
- [ ] Kubernetes manifests created (deployments, services, ingress)
- [ ] Helm chart created and tested
- [ ] ConfigMaps created (non-sensitive config)
- [ ] Secrets created (API keys, passwords)
- [ ] `SelfHostedLLM` class implemented
- [ ] `MinIOStorageService` class implemented
- [ ] `PostgresVectorStore` updated for direct connection
- [ ] Service factory updated for OpenShift config
- [ ] Environment variables configured

### Data Migration
- [ ] Database export from Supabase completed
- [ ] Database import to OpenShift PostgreSQL completed
- [ ] Data integrity validated (row counts, checksums)
- [ ] Documents exported from Supabase Storage
- [ ] Documents imported to MinIO
- [ ] File integrity validated (checksums)

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Model quality validated (vs Gemini baseline)
- [ ] Latency acceptable (<5s p95 for queries)
- [ ] Load testing completed (target: 100 concurrent users)
- [ ] Security testing completed (penetration test)
- [ ] Backup/restore tested
- [ ] Disaster recovery plan validated

### Cutover
- [ ] Parallel environment running (current + OpenShift)
- [ ] DNS/routing ready to switch
- [ ] Rollback plan documented
- [ ] Monitoring dashboards configured
- [ ] On-call rotation established
- [ ] User communication sent
- [ ] Cutover executed
- [ ] Post-cutover monitoring (24-48 hours)
- [ ] Legacy environment decommissioned (after retention period)

---

## 6. Conclusion

The NC ASK POC demonstrates a solid RAG implementation with unique view-based response tailoring and privacy-focused design. The current architecture using managed services (Supabase, Google Gemini) is appropriate for POC development and user feedback gathering.

The migration to OpenShift will achieve complete data residency and user privacy by self-hosting all components (PostgreSQL, MinIO, vLLM with Llama 3.1). The modular service architecture with dependency injection makes this migration straightforward - most changes are configuration and infrastructure, not application logic.

**Focus for next 3 months (POC refinement):**
- Gather user feedback on response quality and UX
- Refine view-based prompting based on actual usage
- Test crisis detection accuracy
- Add user feedback collection (thumbs up/down)
- Implement basic monitoring/analytics
- Document known issues and edge cases

**After POC validation (3+ months):**
- Begin OpenShift migration planning
- Deploy self-hosted LLM and validate quality
- Migrate data and infrastructure
- Implement production monitoring and security hardening
- Consider high-ROI enhancements (hybrid search, caching)

This phased approach balances rapid POC iteration with a clear path to production-grade infrastructure that meets your privacy and data residency requirements.
