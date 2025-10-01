# Bash commands
- npm run build: Build the project
- npm run typecheck: Run the typechecker

# Code style
- Do not use useEffects, should defer to ReactQuery
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')
- Use TypeScript strict mode with comprehensive type definitions
- Prefer async/await over Promise chains
- Use descriptive variable names reflecting domain concepts (ragPipeline, documentChunks, embeddingVector)
- Use functional components with hooks for React
- Implement proper error boundaries and error handling
- Add comprehensive JSDoc comments for public APIs

# Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- Run database migrations before testing new schema changes
- Test vector embeddings with small sample dataset first
- Validate LLM responses against expected citation format
- Check escalation flags trigger proper disclaimers
- Use feature branches for new capabilities (feature/scenario-modules, feature/multilingual-support)
- Run accessibility audits before merging UI changes

# Environment setup
- Node.js 18+ required
- PostgreSQL 15+ with pgvector extension
- Redis for caching and session management
- Docker for local development environment
- Environment variables: DATABASE_URL, REDIS_URL, LLM_API_KEY, EMBEDDING_API_KEY
- Use .env.local for development secrets (never commit)

# Domain-specific notes
- Document chunks should be 200-800 tokens for optimal embedding performance
- Use hybrid search combining vector similarity and BM25 keyword matching
- Implement content-aware chunking based on document type (ProceduralGuide, FAQ, LegalRight)
- Always include source citations in responses
- Apply safety filters for crisis, medical_advice, and legal_advice escalation flags
- Support hierarchical document relationships (parent documents → child chunks)
- Maintain WCAG 2.2 AA compliance for all UI components

# Security requirements
- Never store PII or PHI data
- Implement input validation and sanitization for all user inputs
- Use parameterized queries to prevent SQL injection
- Add rate limiting for API endpoints
- Implement CORS properly for frontend-backend communication
- Log all queries in de-identified format only
- Add escalation flag checks before response generation