# 🚀 START HERE - Complete Setup Guide

This guide will get you running with zero issues. Follow these steps **exactly** in order.

## Prerequisites

✅ **Python 3.11+** installed
✅ **Node.js 18+** installed
✅ **Supabase account** (free tier)
✅ **Google Cloud account** (for Gemini API)
✅ Terminal access

---

## Requirements & Dependencies

### Python Dependencies (Backend)
All Python dependencies are listed in `requirements.txt`:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Supabase** - Database and vector storage
- **Sentence Transformers** - Embeddings (~80MB model download on first run)
- **Google Generative AI** - LLM integration (Gemini)
- **Document Processing** - PyPDF2, python-docx, BeautifulSoup
- **Testing** - pytest, pytest-asyncio

### Node.js Dependencies (Frontend)
Frontend dependencies are in `package.json`:
- **React 18** + TypeScript
- **Vite** - Build tool and dev server
- See `package.json` for complete list

---

## Step-by-Step Setup

### Step 1: Environment Configuration

Create your `.env` file from the example template:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```bash
# Supabase Configuration (from https://app.supabase.com/project/YOUR_PROJECT/settings/api)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Google Gemini API Key (from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_gemini_api_key_here

# Generate a secret key: openssl rand -hex 32
SECRET_KEY=your_random_secret_key_here

# Other settings can use defaults
ENVIRONMENT=development
```

**Required API Keys:**
1. **Supabase**: Sign up at https://supabase.com (free tier available)
2. **Google Gemini**: Get API key at https://makersuite.google.com/app/apikey

### Step 2: Backend Setup (Python/FastAPI)

```bash
# Navigate to project root directory
cd <path-to-NC-ASK>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies from requirements.txt
pip install -r requirements.txt
```

**First run note**: The sentence-transformers library will download an ~80MB model on first startup. This is normal and only happens once.

### Step 3: Database Setup (Supabase)

1. Create a Supabase account at https://supabase.com (if you don't have one)
2. Create a new project
3. Navigate to the SQL Editor in your project dashboard
4. Copy and run the setup script located at: `backend/scripts/supabase_setup.sql`
5. This creates the necessary tables and enables pgvector for embeddings

**What this does:**
- Creates `documents` and `document_chunks` tables
- Enables pgvector extension for similarity search
- Sets up vector indexing for fast retrieval

### Step 4: Frontend Setup (React/TypeScript)

```bash
# Install root-level dependencies (includes concurrently for running both servers)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 5: Running the Application

Run both backend and frontend servers with a single command:

```bash
npm run dev
```

This uses `concurrently` to run both servers simultaneously:
- **Backend**: `http://localhost:8000` (FastAPI + uvicorn with auto-reload)
- **Frontend**: `http://localhost:5173` (Vite dev server with HMR)

**First startup note**: The backend will download an ~80MB embedding model. Wait 2-3 minutes for this to complete.

**What's running:**
- Backend auto-reloads on Python file changes
- Frontend hot-reloads on React/TypeScript changes
- Color-coded terminal output (blue=backend, green=frontend)

To stop both servers, press `Ctrl+C` in the terminal.

### Step 6: Verify Everything Works

Open these URLs in your browser:

1. **Frontend**: http://localhost:5173
   - Should show the NC-ASK interface

2. **Backend Health**: http://localhost:8000/health
   - Should show: `{"status":"healthy","service":"NC-ASK Backend"}`

3. **Backend API Docs**: http://localhost:8000/docs
   - Should show Swagger UI with all endpoints

---

## Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Find what's using the port
lsof -i :8000
lsof -i :5173

# Kill the process or use different ports
kill -9 <PID>
```

### Issue: "Module not found" or import errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Failed to load embedding model"
- **Solution**: This is normal on first run! Wait 2-3 minutes for the model to download.
- **Check**: Look for "Downloading (…)%" in terminal output
- The model is cached after first download

### Issue: "Failed to initialize Supabase client"
- **Solution**: Verify your `.env` file has correct Supabase credentials
- **Check**: Ensure no extra spaces or quotes around values
- **Test**: Try accessing your Supabase URL in browser

### Issue: Python version conflicts
```bash
# Check your Python version
python --version  # Should be 3.11+

# If using multiple Python versions
python3.11 -m venv venv
```

### Issue: Node.js version conflicts
```bash
# Check your Node.js version
node --version  # Should be 18+

# Consider using nvm (Node Version Manager) to switch versions
```

---

## Testing Your Setup

### 1. Test Backend Health Endpoint
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"NC-ASK Backend"}
```

### 2. Test Crisis Detection
In the web UI (http://localhost:5173), type:
```
I feel hopeless
```
You should see a red crisis banner with 988 resources.

### 3. Document Ingestion (Optional but Recommended)

To populate the RAG system with documents:

```bash
# Place your documents in the data folder
cp /path/to/your/*.pdf backend/data/
cp /path/to/your/*.docx backend/data/

# Activate virtual environment (if not already active)
source venv/bin/activate

# Run ingestion script
cd backend
python scripts/ingest_documents.py
```

**Supported formats**: PDF, DOCX, HTML, TXT

The ingestion script will:
1. Extract text from documents
2. Upload files to Supabase Storage
3. Chunk text semantically (200-800 tokens)
4. Generate embeddings using sentence-transformers
5. Store vectors in Supabase pgvector database

---

## Useful Commands

### Development Workflow
```bash
# Start both backend and frontend servers
npm run dev

# Stop both servers
# Press Ctrl+C in the terminal

# Alternative: Run servers separately (if needed)
npm run dev:backend   # Backend only
npm run dev:frontend  # Frontend only
```

### Testing
```bash
# Run backend tests
cd backend
pytest

# Run backend tests with coverage
pytest --cov

# Run frontend tests (when available)
npm run test

# Type checking (frontend)
npm run typecheck
```

### Linting & Formatting
```bash
# Frontend linting
npm run lint

# Backend linting (if configured)
cd backend
flake8 .
```

### Managing Dependencies
```bash
# Add new Python package
pip install <package-name>
pip freeze > requirements.txt

# Add new Node.js package
npm install <package-name>
```

### Database Operations
```bash
# Run document ingestion
cd backend
python scripts/ingest_documents.py

# Access Supabase dashboard
# Visit: https://app.supabase.com/project/YOUR_PROJECT_ID
```

---

## Architecture Overview

```
┌─────────────┐
│  Browser    │
│  :5173      │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────→│  Backend    │─────→│  Supabase   │
│  React+Vite │      │  FastAPI    │      │  (Cloud)    │
│             │      │  +Gemini AI │      │  +pgvector  │
└─────────────┘      └─────────────┘      └─────────────┘
```

## What's Running

| Component | Port | Purpose | Access |
|-----------|------|---------|--------|
| Frontend | 5173 | React/TypeScript UI | http://localhost:5173 |
| Backend | 8000 | FastAPI + RAG Pipeline | http://localhost:8000 |
| Supabase | N/A | PostgreSQL + pgvector | Cloud (via API) |
| Gemini API | N/A | LLM (Google Gemini 1.5) | Cloud (via API) |

## Development Features

- **Backend Hot Reload**: Python files auto-reload via `uvicorn --reload`
- **Frontend HMR**: React/TS files hot reload via Vite
- **Environment Variables**: Requires server restart to take effect
- **Dependencies**: Requires reinstallation (`pip install -r requirements.txt` or `npm install`)

---

## Next Steps

1. ✅ **Setup environment**: Create virtual environment and install dependencies
2. ✅ **Configure Supabase**: Run database setup script
3. ✅ **Start servers**: Run backend and frontend in separate terminals
4. ✅ **Verify setup**: Check all 3 URLs (frontend, health, API docs)
5. ✅ **Test features**: Try crisis detection in the UI
6. ✅ **Add documents**: Place files in `backend/data/`
7. ✅ **Run ingestion**: Process documents into RAG system
8. ✅ **Ask questions**: Test the chatbot with your documents!

---

## Getting Help

### Documentation
- **Setup Guide**: `docs/SETUP.md` - Detailed setup instructions
- **Architecture**: `docs/ARCHITECTURE.md` - System design and data flow
- **Development**: `docs/CLAUDE.md` - Development guidelines
- **Roadmap**: `docs/ROADMAP.md` - Project milestones

### Troubleshooting
1. Check terminal output for error messages
2. Verify `.env` file has correct credentials
3. Ensure Python 3.11+ and Node.js 18+ are installed
4. Check that ports 8000 and 5173 are available
5. Review common issues section above

### Resources
- **Supabase Dashboard**: https://app.supabase.com (login to access your project)
- **FastAPI Docs**: http://localhost:8000/docs (when running)
- **Team**: COMP 523 Project Group B

---

## Quick Reference Card

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
npm install && cd frontend && npm install && cd ..

# Run application (single command for both servers!)
npm run dev

# Run tests
cd backend && pytest
npm run test

# Ingest documents
cd backend && python scripts/ingest_documents.py

# Check what's running
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port

# Build for production
npm run build
```

---

## System Information

- **Python Dependencies**: See `requirements.txt`
- **Node Dependencies**: See `package.json`
- **Database**: Supabase PostgreSQL + pgvector
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM**: Google Gemini 1.5 Flash
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + Python 3.11+

---

🎉 **That's it!** You should now have NC-ASK running at http://localhost:5173

**Important**: Keep the terminal running while using the application. The `npm run dev` command runs both backend and frontend servers concurrently.

