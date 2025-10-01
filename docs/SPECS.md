# NC-ASK MVP Specifications

## Project Overview
NC-ASK is an AI-powered information system that provides accessible, plain-language answers about autism rights, services, and resources in North Carolina. The system prioritizes privacy, accessibility, and crisis support.

## User Stories

### As an individual with autism…
- **US-001**: I want to ask questions about my rights and services in simple language so that I can understand what support is available to me without needing someone else to explain it.
- **US-002**: I want to access information without creating accounts or passwords so that I can get help quickly without barriers.
- **US-003**: I want to get access to information about autism with privacy protections so that I can prevent my personal data from being stored.

### As a parent of a child with autism…
- **US-004**: I want a clear, step-by-step guide of what to do first so that I don't feel overwhelmed and can start getting my child the help they need.
- **US-005**: I want immediate access to crisis intervention resources and calming strategies so that I can help my child during meltdowns and know when to seek additional help.
- **US-006**: I want to know how to request an IEP evaluation and what my rights are during the process so that I can ensure my child gets appropriate educational supports.
- **US-007**: I want to email important information to myself so that I can reference it later or share it with my spouse or care team.

### As a healthcare provider…
- **US-008**: I want to understand the current waiting times and eligibility requirements for NC Innovations Waiver so that I can set realistic expectations when discussing services with families.
- **US-009**: I want to understand the latest autism screening and diagnostic guidelines so that I can provide appropriate early intervention recommendations.

## Requirements

### Functional Requirements

#### Definite (MVP Critical)
- **FR-001**: **Basic Q&A (RAG core)** - System must accept natural language queries and return relevant, accurate responses using Retrieval-Augmented Generation
- **FR-002**: **Plain-language responses** - All system responses must be written in simple, accessible language (targeting 8th grade reading level or below)
- **FR-003**: **Resource lookup** - System must provide citations and links to source documents/resources
- **FR-004**: **Account-free access** - Users must be able to access all features without creating accounts or logging in
- **FR-005**: **Crisis support features** - System must detect crisis-related queries and provide immediate, appropriate resources (988 Suicide & Crisis Lifeline, local crisis services)

#### Perhaps (Post-MVP)
- **FR-006**: **Email-to-self transcript/export** - Users can email conversation transcripts or specific answers to their own email address

### Non-Functional Requirements

#### Definite (MVP Critical)
- **NFR-001**: **Mobile-first design** - UI must be fully responsive and optimized for mobile devices (primary use case)
- **NFR-002**: **Privacy protection** - No PII/PHI storage; sessions are ephemeral; compliance with HIPAA privacy considerations
- **NFR-003**: **Accessibility** - WCAG 2.2 AA compliance minimum; screen reader compatible; keyboard navigable
- **NFR-004**: **Response time** - Queries should return results within 5 seconds under normal load
- **NFR-005**: **Availability** - Target 95% uptime during business hours (MVP phase)

#### Perhaps (Post-MVP)
- **NFR-006**: **Cost controls** - Per-query budget limits; monitoring and alerting for API costs
- **NFR-007**: **High availability** - 99%+ uptime with redundancy and failover

## Success Criteria

### MVP Launch Criteria
1. Successfully answers 80%+ of test queries related to:
   - NC autism services
   - Educational rights (IEP/504)
   - NC Innovations Waiver
   - Crisis resources
2. Crisis detection accuracy of 95%+ for test scenarios
3. All responses meet plain-language standards
4. Mobile experience tested on iOS Safari and Android Chrome
5. Privacy audit completed with no PII storage violations
6. Load tested for 10 concurrent users

### User Acceptance Criteria
- Average user satisfaction score of 4/5 or higher
- Users can complete primary tasks without assistance
- Crisis resources are clearly visible and accessible
- Response accuracy validated by domain experts (autism services professionals)

## Out of Scope (MVP)
- User accounts and authentication
- Multi-language support
- Voice input/output
- Conversation history persistence beyond session
- Admin dashboard for content management
- Integration with external scheduling systems
- Real-time chat with human support staff
- PDF generation of responses
- Advanced analytics and reporting

