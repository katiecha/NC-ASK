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