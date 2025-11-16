# START HERE - Local Development Setup

Get NC-ASK running locally for fast iteration and development.

## Prerequisites

- [x] **Python 3.11+** installed
- [x] **Node.js 18+** installed
- [x] **Git** installed
- [x] Terminal access

**Note:** You'll need Supabase and Gemini API keys later, but we'll get the project running first.

---

## Step-by-Step Setup

### Step 1: Clone and Navigate

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd NC-ASK
```

### Step 2: Backend Setup (Python/FastAPI)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

**Note:** The sentence-transformers library will download an ~80MB model on first run. This is normal and only happens once.

**What gets installed:**
- FastAPI - Web framework
- Uvicorn - ASGI dev server
- Supabase client - Database and vector storage
- Sentence Transformers - Embeddings model
- Google Generative AI - LLM integration (Gemini)
- Document processing tools (PyPDF2, python-docx, BeautifulSoup)
- Testing tools (pytest, pytest-asyncio)

### Step 3: Frontend Setup (React/TypeScript)

```bash
# Install root-level dependencies (includes concurrently for running both servers)
npm install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

**What gets installed:**
- React 18 + TypeScript
- Vite - Build tool and dev server
- React Router - Navigation
- See `frontend/package.json` for complete list

### Step 4: Environment Configuration

Create environment files:

```bash
# Copy backend environment template
cp .env.example .env

# Create frontend environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env.local
```

**For now**, use placeholder values in `.env`:

```bash
# Temporary placeholders - we'll add real values after external setup
SUPABASE_URL=https://placeholder.supabase.co
SUPABASE_ANON_KEY=placeholder
SUPABASE_SERVICE_ROLE_KEY=placeholder
GOOGLE_API_KEY=placeholder

# Generate a real secret key
SECRET_KEY=$(openssl rand -hex 32)

# Other settings
ENVIRONMENT=development
```

### Step 5: Test Local Setup

Try running the application (it will fail to connect to Supabase, but that's expected):

```bash
npm run dev
```

You should see:
- Backend starting on http://localhost:8000
- Frontend starting on http://localhost:5173

Press `Ctrl+C` to stop for now.

---

## External Services Setup

Now let's set up the external services needed for full functionality.

### Step 6: Supabase Database Setup

1. **Create Supabase Account**
   - Go to https://supabase.com and sign up (free tier)
   - Click "New Project"
   - Fill in:
     - Name: `nc-ask`
     - Database Password: Generate strong password (save it!)
     - Region: `us-east-1` (East US - closest to North Carolina)
   - Wait ~2 minutes for project to initialize

2. **Run Database Setup Script**
   - In Supabase Dashboard, go to **SQL Editor** (left sidebar)
   - Click "New query"
   - Open file: `backend/scripts/supabase_setup.sql` on your computer
   - Copy the **entire contents** and paste into Supabase SQL Editor
   - Click "Run" (or press Ctrl+Enter / Cmd+Enter)
   - You should see "Success. No rows returned"

3. **Get API Credentials**
   - Go to Settings → API
   - Copy these values:
     - `Project URL` → This is your `SUPABASE_URL`
     - `anon public` key → This is your `SUPABASE_ANON_KEY`
     - `service_role` key → This is your `SUPABASE_SERVICE_ROLE_KEY`

4. **Update `.env` file**
   - Open `.env` in your editor
   - Replace the placeholder values with your actual Supabase credentials

### Step 7: Google Gemini API Setup

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Update `.env` file: Replace `GOOGLE_API_KEY=placeholder` with your actual key

### Step 8: Run the Application

Now with everything configured, start the application:

```bash
# Make sure you're in the project root and venv is activated
npm run dev
```

This runs both servers simultaneously:
- **Backend**: http://localhost:8000 (FastAPI + uvicorn with auto-reload)
- **Frontend**: http://localhost:5173 (Vite dev server with HMR)

### Step 9: Ingest Documents (Optional)

To load sample documents into the vector database:

```bash
# In a new terminal, with venv activated
cd backend
python scripts/ingest_documents.py
```

---

## You're Done!

Visit http://localhost:5173 and start querying!

## Development Tips

- **Hot reload**: Changes to Python or TypeScript files will auto-reload
- **Debugging**:
  - Backend: Attach debugger to uvicorn process on port 8000
  - Frontend: Use browser DevTools
- **Type checking**: Run `npm run typecheck` before committing
- **Testing**: Run `cd backend && pytest` to run backend tests

## Troubleshooting

**Backend won't start:**
- Make sure venv is activated: `source venv/bin/activate`
- Check `.env` has valid Supabase and Gemini credentials

**Frontend can't connect to backend:**
- Verify `frontend/.env.local` exists with `VITE_API_BASE_URL=http://localhost:8000`
- Check backend is running on port 8000

**"Model not found" error:**
- First run downloads ~80MB model - wait a few minutes
- Needs internet connection for download

**Supabase connection error:**
- Verify credentials in `.env` are correct
- Check Supabase project is active and not paused