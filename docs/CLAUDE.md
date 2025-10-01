# NC-ASK Development Guidelines

## Quick Commands

### Frontend
```bash
npm run dev          # Start Vite dev server
npm run build        # Build for production
npm run typecheck    # Run TypeScript type checking
npm run lint         # Run ESLint
```

### Backend
```bash
cd backend
python -m uvicorn main:app --reload  # Start FastAPI dev server
python -m pytest                      # Run tests
python -m pytest tests/test_rag.py   # Run specific test
python scripts/ingest_documents.py   # Ingest documents to Supabase
```

### Docker (Local Development Only)
```bash
docker-compose up           # Start FastAPI + Redis (uses Supabase cloud)
docker-compose up -d        # Start in background
docker-compose down         # Stop all services
docker-compose logs -f      # Follow logs
```

## Code Style

### General Python (Backend)
- Use type hints for all function signatures
- Follow PEP 8 style guide
- Use descriptive variable names: `embedding_vector`, `document_chunks`, `rag_pipeline`
- Prefer async/await for I/O operations
- Use Pydantic models for API request/response validation
- Add comprehensive docstrings (Google style)
- Maximum line length: 100 characters

### TypeScript/React (Frontend)
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports: `import { useState } from 'react'`
- Use TypeScript strict mode with comprehensive type definitions
- Prefer async/await over Promise chains
- Use functional components with hooks (no class components)
- Implement proper error boundaries
- Use descriptive variable names reflecting domain: `queryResponse`, `crisisDetected`
- Add JSDoc comments for complex functions

### CSS
- Use CSS Modules (`.module.css` files)
- Mobile-first media queries
- Follow BEM naming convention for clarity
- Use CSS custom properties for theme values
- Ensure WCAG 2.2 AA contrast ratios

## Development Workflow

### Before Starting Work
1. Pull latest changes: `git pull origin main`
2. Create feature branch: `git checkout -b feature/your-feature-name`
3. Start Docker services: `docker-compose up -d`
4. Verify services are running: `docker-compose ps`

### During Development
1. Make incremental commits with clear messages
2. Run type checking frequently: `npm run typecheck` (frontend)
3. Test API endpoints with sample queries
4. Verify crisis detection with test phrases
5. Check mobile responsiveness in browser dev tools

### Before Committing
1. Run type checking: `npm run typecheck`
2. Run linter: `npm run lint`
3. Test critical user flows manually
4. Verify no sensitive data in code
5. Check accessibility with screen reader/keyboard navigation

### Code Review Checklist
- [ ] No PII/PHI data stored or logged
- [ ] Crisis detection working for test cases
- [ ] Plain language validated (8th grade level)
- [ ] Mobile responsive
- [ ] WCAG 2.2 AA compliant
- [ ] No hardcoded secrets/API keys
- [ ] Error handling implemented
- [ ] Tests added for new features

## Environment Setup

### Required Software
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- Docker & Docker Compose (local dev)
- Git
- Supabase CLI (optional, for local development)

### Environment Variables

#### Frontend (.env.local)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

#### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # For admin operations

# AI Services
GOOGLE_API_KEY=your_gemini_api_key
HUGGINGFACE_API_TOKEN=your_hf_token  # Optional for model downloads

# Email (optional for MVP)
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@ncask.org

# Security
SECRET_KEY=your_secret_key_for_session_signing
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Feature Flags
ENABLE_EMAIL_EXPORT=false
ENABLE_QUERY_LOGGING=true
LOG_LEVEL=INFO
```

**Important**: Never commit `.env` or `.env.local` files. Use `.env.example` for templates.

### First-Time Setup
```bash
# 1. Clone repository
git clone https://github.com/your-org/NC-ASK.git
cd NC-ASK

# 2. Install frontend dependencies
npm install

# 3. Set up backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# 4. Create Supabase project
# Go to https://supabase.com and create a new project
# Enable pgvector extension in SQL Editor: CREATE EXTENSION vector;

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase URL and keys

# 6. Set up Supabase tables
python backend/scripts/setup_supabase.py

# 7. Ingest initial documents
python backend/scripts/ingest_documents.py

# 8. Start development servers
npm run dev  # Frontend (terminal 1)
cd backend && python -m uvicorn main:app --reload  # Backend (terminal 2)
```

## Domain-Specific Guidelines

### RAG Pipeline
- Document chunks: 200-800 tokens for optimal embedding performance
- Overlap: 50 tokens between chunks for context continuity
- Retrieval: Top 5 most similar chunks per query (Supabase pgvector)
- Re-ranking: Use cross-encoder for improved relevance (post-MVP)
- Context window: Max 2000 tokens for Gemini input
- Storage: Original files in Supabase Storage, vectors in Supabase DB

### Plain Language Requirements
- Target reading level: 8th grade or below
- Use short sentences (< 20 words average)
- Avoid jargon; define necessary technical terms
- Use active voice
- Break complex processes into numbered steps
- Test with readability tools (Flesch-Kincaid)

### Crisis Detection
- **Critical**: Crisis detection must never fail or delay responses
- Keywords monitored: suicide, self-harm, harm to others, severe distress
- Response: Inject 988 Suicide & Crisis Lifeline immediately
- Include: Local NC crisis resources
- Log: De-identified flag for monitoring (no query content)
- Always return crisis resources first, then answer

### Accessibility Requirements
- All interactive elements keyboard accessible
- ARIA labels for screen readers
- Color contrast ratio ≥ 4.5:1 for normal text
- Color contrast ratio ≥ 3:1 for large text
- Focus indicators visible
- Alt text for all images
- Form labels properly associated
- Test with: NVDA, JAWS, VoiceOver

### Source Document Types
- **ProceduralGuide**: Step-by-step instructions (IEP requests, waiver applications)
- **FAQ**: Common questions and answers
- **LegalRights**: Rights under IDEA, ADA, etc.
- **ResourceDirectory**: Contact info for services
- **CrisisSupport**: Crisis intervention resources

## Security Requirements

### Privacy Protection
- **NEVER** store user queries beyond session
- **NEVER** store email addresses long-term
- **NEVER** log PII in any form
- Use session IDs only for active session management
- Clear session data after 1 hour of inactivity
- No tracking cookies or analytics with PII

### Input Validation
- Validate all API inputs with Pydantic models
- Sanitize user input before processing
- Use Supabase client (built-in SQL injection protection)
- Implement rate limiting: 10 queries/minute per IP
- Maximum query length: 500 characters
- Block SQL injection patterns
- Escape HTML/JS in responses

### API Security
- CORS: Whitelist frontend origins only
- No authentication for MVP (account-free)
- HTTPS only in production
- Rate limiting per IP address
- Content Security Policy headers
- No sensitive data in API responses

### LLM Safety
- Prompt injection detection
- Output validation for harmful content
- Disclaimer injection for medical/legal topics
- Crisis flag detection before response delivery
- Fallback to conservative responses when uncertain

## Testing Strategy

### Frontend Testing (Future)
- Unit tests: Vitest
- Component tests: React Testing Library
- E2E tests: Playwright
- Accessibility: axe-core

### Backend Testing
- Unit tests: pytest
- Integration tests: pytest with test database
- API tests: pytest + httpx
- Load tests: locust (post-MVP)

### Test Datasets
- Sample queries covering all user story scenarios
- Crisis detection test cases (positive and negative)
- Plain language validation samples
- Edge cases: empty queries, very long queries, special characters

### Manual Testing Checklist
- [ ] Crisis queries show resources immediately
- [ ] Plain language verified by non-technical user
- [ ] Mobile experience on iOS and Android
- [ ] Keyboard navigation works
- [ ] Screen reader announces content correctly
- [ ] Citations link to correct sources
- [ ] Email export works (if enabled)

## Git Workflow

### Branch Naming
- `feature/query-processing` - New features
- `fix/crisis-detection-bug` - Bug fixes
- `docs/api-documentation` - Documentation
- `refactor/rag-pipeline` - Code refactoring

### Commit Messages
Follow conventional commits:
```
feat: add crisis detection to RAG pipeline
fix: correct embedding dimension mismatch
docs: update API endpoint documentation
test: add unit tests for query sanitization
refactor: simplify LLM prompt construction
```

### Pull Request Process
1. Create PR with descriptive title
2. Link related issues
3. Add screenshots for UI changes
4. Request review from at least one team member
5. Ensure CI/CD checks pass
6. Squash and merge after approval

## Monitoring & Debugging

### Key Metrics to Monitor
- Query response time (p50, p95, p99)
- Crisis detection rate
- LLM API errors
- Database query performance
- Rate limit violations
- User session duration

### Logging Best Practices
- Log level: INFO for production, DEBUG for development
- Include request IDs for tracing
- Log query metadata, NOT query content
- Log crisis detections (de-identified)
- Log errors with stack traces
- Rotate logs daily

### Common Issues

#### Slow queries
- Check Supabase pgvector index in dashboard
- Verify embedding dimension: 384 for all-MiniLM-L6-v2
- Check Supabase connection limits (free tier: 60 connections)
- Monitor Supabase dashboard for performance metrics

#### Crisis detection failures
- Verify keyword list is loaded
- Check for typos in crisis keywords
- Test with exact phrases from test suite

#### Plain language issues
- Run through readability checker
- Get feedback from target users
- Simplify complex sentence structures
- Define jargon inline

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://docs.langchain.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)

### Internal Links
- [SPECS.md](./SPECS.md) - User stories and requirements
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [README.md](./README.md) - Project overview and setup

### NC-Specific Resources
- NC Autism Services: https://www.ncdhhs.gov/
- NC Innovations Waiver: https://www.ncdhhs.gov/divisions/mhddsas
- NC IEP Guidelines: https://www.dpi.nc.gov/

