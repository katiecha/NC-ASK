# NC-ASK MVP Implementation Roadmap

## Phase 0: Project Setup (Week 1)

### Infrastructure Setup
- [ ] Set up GitHub repository with branch protection
- [ ] Configure GitHub Actions for CI/CD
- [ ] Set up Docker Compose environment (local dev only)
- [ ] Create Supabase project and configure pgvector
- [ ] Set up Supabase Storage buckets
- [ ] Create .env.example templates
- [ ] Set up local development environment documentation

### Backend Foundation
- [ ] Initialize FastAPI project structure
- [ ] Set up Supabase client with Pydantic models
- [ ] Configure CORS and middleware
- [ ] Implement health check endpoint
- [ ] Set up logging infrastructure
- [ ] Create Supabase table schemas and RLS policies

### Frontend Foundation
- [ ] Verify Vite + React + TypeScript setup (already exists)
- [ ] Configure API client and base URL
- [ ] Set up error boundary components
- [ ] Implement basic routing structure
- [ ] Configure CSS modules

**Deliverable**: Running "Hello World" full-stack application

---

## Phase 1: Core RAG Pipeline (Weeks 2-3)

### Document Ingestion System
- [ ] Create document ingestion script
- [ ] Implement text extraction (PDF, DOCX, HTML)
- [ ] Build semantic chunking logic (200-800 tokens)
- [ ] Integrate sentence-transformers/all-MiniLM-L6-v2
- [ ] Generate embeddings for document chunks
- [ ] Store files in Supabase Storage
- [ ] Store vectors and metadata in Supabase PostgreSQL/pgvector
- [ ] Create sample NC autism services dataset (10-20 documents)

### Query Processing
- [ ] Implement input validation and sanitization
- [ ] Build query embedding generation
- [ ] Create Supabase pgvector similarity search function
- [ ] Implement retrieval logic (top-k similar chunks)
- [ ] Build context assembly for LLM

### LLM Integration
- [ ] Set up Google Gemini 2.5 Flash-lite API client
- [ ] Design system prompts for plain language responses
- [ ] Implement RAG prompt engineering
- [ ] Build LLM response parsing and validation
- [ ] Add citation extraction from retrieved chunks
- [ ] Test with sample queries

### API Endpoints
- [ ] POST `/api/query` - Main query endpoint
- [ ] GET `/api/health` - Health check
- [ ] Implement error handling and logging

**Deliverable**: Basic Q&A system that can answer simple questions about autism services

**Test Criteria**:
- Successfully answers 5 test queries
- Returns relevant citations
- Response time < 10 seconds

---

## Phase 2: Safety & Crisis Features (Week 4)

### Crisis Detection System
- [ ] Create crisis keyword database
- [ ] Implement keyword matching algorithm
- [ ] Build crisis flag detection in query pipeline
- [ ] Design crisis resource response format
- [ ] Create static crisis resources table
- [ ] Implement GET `/api/crisis-resources` endpoint
- [ ] Test crisis detection with 20 test cases

### Crisis Response Integration
- [ ] Inject 988 Lifeline in crisis responses
- [ ] Add NC-specific crisis resources
- [ ] Design crisis banner UI component
- [ ] Implement immediate crisis resource display
- [ ] Add logging for crisis detections (de-identified)

### Safety Guardrails
- [ ] Implement disclaimer injection for medical/legal topics
- [ ] Add output validation for harmful content
- [ ] Create fallback responses for uncertain queries
- [ ] Test edge cases and adversarial inputs

**Deliverable**: System that reliably detects and responds to crisis queries

**Test Criteria**:
- 95%+ crisis detection accuracy on test set
- Crisis resources display within 2 seconds
- No false negatives for critical crisis terms

---

## Phase 3: Plain Language & Accessibility (Week 5)

### Plain Language Processing
- [ ] Implement readability scoring (Flesch-Kincaid)
- [ ] Build language simplification prompts
- [ ] Add jargon detection and definition injection
- [ ] Create response formatting (short sentences, active voice)
- [ ] Test responses with readability tools
- [ ] Validate with non-technical users

### Frontend Accessibility
- [ ] Audit existing components with axe-core
- [ ] Add ARIA labels to all interactive elements
- [ ] Implement keyboard navigation
- [ ] Ensure color contrast meets WCAG 2.2 AA
- [ ] Add visible focus indicators
- [ ] Test with screen readers (NVDA, VoiceOver)

### Mobile-First UI Refinements
- [ ] Optimize search interface for mobile
- [ ] Implement responsive crisis banner
- [ ] Ensure touch targets are ≥44px
- [ ] Test on iOS Safari and Android Chrome
- [ ] Optimize font sizes for mobile readability

**Deliverable**: Fully accessible, mobile-optimized UI with plain language responses

**Test Criteria**:
- All responses at 8th grade reading level or below
- WCAG 2.2 AA compliance verified
- Keyboard navigation works for all features
- Mobile usability testing completed

---

## Phase 4: Core Features & Polish (Week 6)

### Resource Lookup Enhancement
- [ ] Improve citation formatting
- [ ] Add source URL validation
- [ ] Implement relevance score display
- [ ] Create "Learn More" sections
- [ ] Add NC-specific resource links
- [ ] Design resource card UI components

### Account-Free Experience
- [ ] Implement ephemeral session IDs
- [ ] Use sessionStorage (no persistent cookies)
- [ ] Add session timeout (1 hour)
- [ ] Create privacy notice modal
- [ ] Display data handling transparency message

### Rate Limiting & Security
- [ ] Implement IP-based rate limiting (10/min)
- [ ] Add query length validation (500 char max)
- [ ] Configure CSP headers
- [ ] Add SQL injection prevention tests
- [ ] Implement XSS sanitization
- [ ] Test rate limiting under load

### Performance Optimization
- [ ] Add database connection pooling
- [ ] Optimize pgvector index parameters
- [ ] Implement query result caching (optional)
- [ ] Minimize LLM prompt size
- [ ] Test with 10 concurrent users

**Deliverable**: Secure, performant MVP ready for testing

**Test Criteria**:
- Query response time < 5 seconds (p95)
- Handles 10 concurrent users
- No security vulnerabilities in basic audit
- Privacy protections verified

---

## Phase 5: Testing & Documentation (Week 7)

### Comprehensive Testing
- [ ] Create test suite for all user stories
- [ ] Test all functional requirements (FR-001 to FR-005)
- [ ] Validate non-functional requirements (NFR-001 to NFR-005)
- [ ] Perform accessibility audit
- [ ] Conduct mobile device testing
- [ ] Run load testing
- [ ] Test edge cases and error scenarios

### User Acceptance Testing
- [ ] Recruit test users from target audiences
- [ ] Conduct moderated usability sessions
- [ ] Gather feedback on response quality
- [ ] Validate plain language effectiveness
- [ ] Test crisis resource discoverability
- [ ] Collect satisfaction scores

### Documentation
- [ ] Complete API documentation
- [ ] Write deployment guide
- [ ] Create user guide
- [ ] Document known limitations
- [ ] Write incident response procedures
- [ ] Create monitoring runbook

**Deliverable**: Tested, documented MVP ready for soft launch

**Test Criteria**:
- All MVP success criteria met (see SPECS.md)
- User satisfaction score ≥ 4/5
- Documentation complete and reviewed

---

## Phase 6: Deployment & Launch (Week 8)

### Pre-Production Setup
- [ ] Set up Render/Railway account for FastAPI hosting
- [ ] Configure Supabase production project
- [ ] Set up SendGrid account (for future email feature)
- [ ] Configure monitoring and alerts
- [ ] Set up logging aggregation
- [ ] Create backup and recovery procedures (Supabase handles most)

### Production Deployment
- [ ] Deploy backend to Render/Railway
- [ ] Deploy frontend to Vercel
- [ ] Configure production environment variables
- [ ] Set up HTTPS certificates (automatic with Vercel/Render)
- [ ] Configure CDN for static assets (Vercel Edge Network)
- [ ] Verify production health checks

### Soft Launch
- [ ] Deploy to production with limited access
- [ ] Monitor performance metrics
- [ ] Watch for errors and issues
- [ ] Gather initial user feedback
- [ ] Fix critical bugs
- [ ] Optimize based on real usage patterns

### Public Launch
- [ ] Open access to public
- [ ] Announce launch to stakeholders
- [ ] Monitor usage and performance
- [ ] Provide support channels
- [ ] Collect user feedback
- [ ] Plan post-MVP enhancements

**Deliverable**: Live, publicly accessible NC-ASK MVP

---

## Post-MVP Enhancements (Backlog)

### High Priority
- [ ] Email-to-self feature (FR-006)
- [ ] Advanced analytics dashboard
- [ ] Improved context re-ranking
- [ ] Expanded document corpus
- [ ] Multi-turn conversation support

### Medium Priority
- [ ] Cost monitoring and alerts (NFR-006)
- [ ] Redis caching layer
- [ ] Advanced query understanding (intent detection)
- [ ] Admin interface for content management
- [ ] A/B testing framework

### Low Priority
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] PDF export of responses
- [ ] Integration with NC services portals
- [ ] Real-time chat with support staff

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation |
|------|------------|
| Gemini API rate limits | User has Gemini Pro, should be sufficient |
| Poor embedding quality | Test alternative models, fine-tune chunking |
| Slow query responses | Supabase optimization, implement caching |
| Supabase free tier limits | Monitor usage, upgrade to Pro when needed |

### Product Risks
| Risk | Mitigation |
|------|------------|
| Inaccurate responses | Human review of sample responses, clear disclaimers |
| Crisis detection failures | Extensive testing, conservative keyword list |
| Low user adoption | User testing during development, iterate on feedback |
| Privacy concerns | Clear privacy policy, no PII storage, transparency |

### Resource Risks
| Risk | Mitigation |
|------|------------|
| Limited development time | Strict MVP scope, prioritize core features |
| Budget constraints for APIs | Monitor costs closely, optimize prompts |
| Limited testing resources | Automate where possible, focus on critical paths |

---

## Success Metrics (MVP)

### Technical Metrics
- ✅ 95%+ uptime during business hours (Supabase SLA)
- ✅ < 5 second query response time (p95)
- ✅ 95%+ crisis detection accuracy
- ✅ 0 privacy violations
- ✅ Stay within Supabase free tier limits (500MB)

### User Metrics
- ✅ 80%+ query answering accuracy
- ✅ 4/5 average user satisfaction
- ✅ 100% of target user stories addressed
- ✅ WCAG 2.2 AA compliance

### Business Metrics
- Target: 50+ users in first month
- Target: 500+ queries in first month
- Target: $0/month in hosting costs (free tiers)
- Target: 0 critical incidents

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|----------------|
| Phase 0 | Week 1 | Running full-stack app |
| Phase 1 | Weeks 2-3 | Basic Q&A system |
| Phase 2 | Week 4 | Crisis detection |
| Phase 3 | Week 5 | Accessible, plain language UI |
| Phase 4 | Week 6 | Polished MVP |
| Phase 5 | Week 7 | Tested, documented system |
| Phase 6 | Week 8 | Public launch |

**Total MVP Timeline**: 8 weeks

---

## Next Steps

1. **Immediate**: Review and approve these specification documents
2. **This week**: Complete Phase 0 (project setup)
3. **Week 2**: Begin document ingestion and RAG pipeline
4. **Ongoing**: Weekly team sync to review progress and blockers
5. **Before each phase**: Review checklist and adjust timeline as needed

## Questions to Resolve

- [ ] What is the initial document corpus size and source?
- [ ] Who are the domain experts for response validation?
- [ ] What is the target launch date?
- [ ] What is the budget for Gemini API usage?
- [ ] Who will handle user support after launch?
- [ ] Are there legal/compliance reviews required?

