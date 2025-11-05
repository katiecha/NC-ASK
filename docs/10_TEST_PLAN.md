# NC-ASK Test Plan

## Part 1: Ideal Test Plan
### 1. Unit Testing
#### Backend Unit Tests
- **Coverage Goal**: 90%+ code coverage
- **Scope**:
  - All service modules (config, crisis_detection, document_processor, embeddings, llm_service, rag_pipeline, retrieval, vector_store, supabase_client)
  - API models and validation (Pydantic schemas)
  - Utility functions and helpers
  - Prompt template generation
  - Error handling and edge cases
- **Approach**: Expand existing pytest suite with comprehensive test cases, mocking external dependencies (LLM, database, embedding models)

#### Frontend Unit Tests
- **Coverage Goal**: 90%+ code coverage
- **Scope**:
  - All 11+ React components (ActionButtons, DarkModeToggle, HamburgerMenu, InfoButton, Layout, PrivacyModal, QueryResponse, SearchInput, Sidebar, ViewIndicator, ViewSelector)
  - Context providers (DarkModeContext, ViewContext)
  - API service client (api.ts)
  - Routing logic
  - State management hooks
- **Approach**: Vitest + React Testing Library, component isolation testing, mock API calls

---

### 2. Integration Testing
#### Backend Integration Tests
- **RAG Pipeline Integration**:
  - End-to-end RAG flow (query → embedding → retrieval → LLM → response)
  - Document ingestion → storage → retrieval workflow
  - Crisis detection integration with response generation
  - Citation extraction and formatting
- **Database Integration**:
  - Supabase client operations (CRUD)
  - Vector similarity search with pgvector
  - RLS policy enforcement
  - Connection pooling and transactions
- **External Service Integration**:
  - Google Gemini API calls (with rate limiting)
  - Embedding model operations
  - Document storage operations

#### Frontend-Backend Integration
- **API Contract Testing**:
  - All endpoint request/response validation
  - Error response handling
  - Session management flow
  - View-type parameter propagation

---

### 3. System Testing (End-to-End with UI)
#### User Workflows
- **First-Time User Journey**:
  1. Landing page load
  2. View selection modal interaction
  3. Privacy modal acceptance
  4. First query submission
  5. Response viewing with citations
  6. Multi-turn conversation
- **Crisis Detection Flow**:
  - Submit crisis-related query
  - Verify crisis banner display
  - Verify crisis resources appear
  - Check de-identified logging
- **View Switching**:
  - Test provider vs. patient/caregiver responses
  - Verify view indicator updates
  - Verify response tone differences
- **Navigation & UI Features**:
  - Dark mode toggle
  - Sidebar navigation
  - About page
  - Mobile responsiveness
  - Hamburger menu on mobile

#### Cross-Browser Testing
- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Android)

---

### 4. End User Types
#### Primary User Personas
**1. Healthcare Provider**
- **Goals**: Quick access to accurate clinical guidelines, referral information
- **Tech Literacy**: High
- **Use Cases**:
  - Finding diagnostic criteria
  - Locating specialist referrals
  - Understanding insurance coverage
  - Accessing evidence-based interventions

**2. Parent/Caregiver**
- **Goals**: Understanding diagnosis, finding local support services
- **Tech Literacy**: Moderate
- **Use Cases**:
  - Understanding what autism means
  - Finding therapy options (ABA, OT, speech)
  - Navigating school services (IEP)
  - Locating support groups
  - Crisis resources

**3. Patient**
- **Goals**: Finding adult services, employment support
- **Tech Literacy**: High
- **Use Cases**:
  - Employment resources
  - Independent living support
  - Social skills groups
  - Mental health services

**4. Educator**
- **Goals**: Classroom strategies, student support resources
- **Tech Literacy**: Moderate-High
- **Use Cases**:
  - Behavioral strategies
  - IEP accommodations
  - Sensory accommodations
  - Communication tools

---

### 5. Usability Testing
#### Accessibility Compliance
- **WCAG 2.1 Level AA**:
  - Keyboard navigation (all interactive elements)
  - Screen reader compatibility (NVDA, JAWS, VoiceOver)
  - Color contrast ratios (4.5:1 minimum)
  - Focus indicators
  - Alt text for images
  - ARIA labels where needed

---

### 6. Performance, Reliability, & Security Testing
#### Performance Testing
- **Load Testing**:
  - Baseline: 10 concurrent users
  - Target: 50 concurrent users
  - Peak: 100 concurrent users
- **Stress Testing**: Identify breaking point
- **Metrics**:
  - Response time (p50, p95, p99)
  - Target: <3s p95 for query responses
  - Target: <500ms for page loads
  - Throughput (requests per second)
  - Error rate under load
- **Bottleneck Analysis**:
  - Database query performance
  - Vector search performance
  - LLM API latency
  - Embedding generation time
  - Frontend bundle size

#### Reliability Testing
- **Uptime**: 99.5% target
- **Error Recovery**:
  - LLM API failures (graceful degradation)
  - Database connection failures
  - Network timeouts
- **Data Consistency**:
  - Vector store integrity
  - Citation accuracy over time
  - Session management reliability

#### Security Testing
- **Input Validation**:
  - XSS prevention (malicious scripts in queries)
  - SQL injection prevention
  - Prompt injection attacks
  - Oversized inputs
- **API Security**:
  - Rate limiting (prevent abuse)
  - CORS configuration
  - Authentication for admin endpoints
- **Data Privacy**:
  - No PII storage verification
  - Session data ephemeral nature
  - No cookie tracking
- **RLS Policy Testing**: Verify database-level security
- **Dependency Scanning**: Known vulnerabilities in package

---

### 7. Acceptance Testing
#### Functional Acceptance Criteria
- **Core Functionality**:
  - User can submit queries and receive relevant responses
  - Responses include accurate citations with relevance scores
  - Crisis keywords trigger crisis detection and resources
  - Provider and patient/caregiver views produce different responses
  - Multi-turn conversations maintain context
  - Privacy modal acceptance required before use
  - Dark mode toggle works across all pages

#### Content Acceptance
- **RAG Accuracy**:
  - Sample 100 queries across topics
  - Expert review by Dr. Patel
  - Accuracy rate target: >90%
  - Citation relevance target: >85%
- **Response Quality**:
  - Appropriate tone for each view
  - No hallucinations or false information
  - Proper disclaimers included
  - Reading level appropriate

#### User Acceptance Testing (UAT)
- **Participants**: Real end users from each persona
- **Duration**: 1-2 weeks of real-world usage
- **Feedback Collection**: Surveys, interviews, usage analytics

---

## Part 2 (Realistic Test Plan)

**Priority**: RAG accuracy & citations, Performance & scalability

### 1. Unit Testing
#### Backend
- **Expand existing tests** in these files:
  - `test_rag_pipeline.py`: Add edge cases for RAG flow
  - `test_retrieval.py`: Test vector search with various query types
  - `test_crisis_detection.py`: Already comprehensive, verify all scenarios pass
- **Add new tests**:
  - Citation extraction accuracy (new file: `test_citations.py`)
  - View-type parameter handling (add to `test_rag_pipeline.py`)
- **Skip**: Comprehensive coverage of all modules, focus on RAG core

#### Frontend
- **Set up Vitest** (minimal config)
- **Test 3 critical components**:
  - SearchInput: Can submit query
  - QueryResponse: Renders response and citations correctly
  - PrivacyModal: Blocks usage until accepted
- **Skip**: Full component suite, context testing, edge cases

---

### 2. Integration Testing
#### RAG Accuracy Testing
- **Create test query set** (30-50 queries):
  - 10 queries per topic (diagnosis, therapies, school services, insurance, crisis)
  - Mix of provider and patient/caregiver views
- **Manual testing process**:
  1. Submit each query via actual application
  2. Record response, citations, and relevance scores
  3. Expert review (Dr. Patel or teammate) - mark as correct/incorrect
  4. Calculate accuracy rate
- **Target**: >85% accuracy
- **Document failures** for future improvement

#### Citation Verification
- **For each test query**, verify:
  - Citations are present
  - Citations link to actual source documents
  - Cited content is relevant to response
  - Relevance scores make sense (higher = more relevant)
- **Create spreadsheet**: Query | Response | Citations | Relevance | Correct? (Y/N)

---

### 3. System Testing
#### E2E Critical Paths (Manual Testing)
- **Test 5 core workflows** (30 min each):
  1. First-time user → view selection → privacy accept → query → response
  2. Crisis query → crisis banner + resources appear
  3. Provider view query → professional tone response
  4. Patient view query → simpler tone response
  5. Multi-turn conversation (3 turns)
- **Test on 2 browsers**: Chrome + one other (Firefox or Safari)
- **Test on mobile**: iOS or Android (responsive design check)

---

### 4. End User Types (No separate testing phase)
**Document personas** (see Part 1, Section 4) and use them to inform test query creation. No separate user testing sessions due to time constraints.

---

### 5. Usability Testing
#### Quick Accessibility Audit
- **Automated scan**: Run axe DevTools and Lighthouse on key pages (Home, About)
- **Keyboard navigation test**: Tab through entire application
- **Screen reader spot check**: Test 1-2 workflows with screen reader
- **Fix critical issues only** (e.g., missing alt text, keyboard traps)

---

### 6. Performance & Reliability Testing
#### Performance Benchmarking
- **Baseline Metrics** (1 hour):
  - Time 10 queries with stopwatch
  - Record response times
  - Calculate average, p95
  - Note: Gemini API latency likely dominates

- **Load Testing** (2 hours setup + 4 hours testing):
  - Set up Locust or k6 (simple script)
  - Test scenario: Submit queries at increasing rates
  - Test with 10, 20, 30 concurrent users
  - Measure:
    - Response times (p50, p95, p99)
    - Error rate
    - Throughput
  - **Target**: <5s p95, <5% error rate at 10 concurrent users

- **Bottleneck Identification**:
  - Add timing logs to backend:
    - Embedding generation time
    - Vector search time
    - LLM API call time
    - Total request time
  - Run 20 queries, analyze where time is spent
  - Document findings

- **Database Performance**:
  - Check pgvector index usage (EXPLAIN ANALYZE on match_document_chunks)
  - Verify queries are fast (<100ms for vector search)
  - Test with different embedding counts (100, 500, 1000+ chunks)

#### Reliability Checks
- **Error Handling**:
  - Test with invalid queries (empty, very long, special characters)
  - Disconnect network during query (simulate LLM timeout)
  - Verify graceful error messages
  - Check error logging

- **Crisis Detection Reliability**:
  - Re-run existing crisis detection tests
  - Test 20 crisis queries manually
  - Verify 100% detection rate
  - Verify crisis resources always load

#### Basic Security Checks
- **Input Validation**:
  - Try XSS payloads in query input: `<script>alert('xss')</script>`
  - Try SQL injection patterns: `'; DROP TABLE documents; --`
  - Verify sanitization works
- **Dependency Scan**:
  - Run `npm audit` (frontend)
  - Run `pip-audit` or `safety check` (backend)
  - Document high/critical vulnerabilities

---

### 7. Acceptance Testing
#### RAG Accuracy Review
- **Review results** from Integration Testing (Section 2)
- **Calculate metrics**:
  - Overall accuracy: % of queries with correct responses
  - Citation accuracy: % of citations that are relevant
  - View-specific accuracy: Provider vs. patient/caregiver
- **Create report** with findings and recommendations