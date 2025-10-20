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