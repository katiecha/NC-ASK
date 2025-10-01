# NC-ASK Quick Start Guide

Get NC-ASK running in under 15 minutes.

## Prerequisites Checklist

- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **Python 3.11+** installed (`python --version`)
- [ ] **Git** installed
- [ ] **Supabase account** (free at https://supabase.com)
- [ ] **Google account** for Gemini API

## 5-Step Setup

### Step 1: Clone & Install (2 min)

```bash
# Clone repository
git clone https://github.com/your-org/autism-chat-bot.git
cd autism-chat-bot

# Install backend dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies
npm install
```

### Step 2: Supabase Setup (5 min)

1. **Create project**: https://supabase.com → New Project
   - Name: `nc-ask`
   - Region: `us-east-1`
   - Save database password!

2. **Run SQL**: Go to SQL Editor → New query
   - Copy entire contents of `backend/scripts/supabase_setup.sql`
   - Paste and run

3. **Create bucket**: Go to Storage → Create bucket
   - Name: `documents`
   - Public: **OFF**

4. **Get credentials**: Settings → API
   - Copy: Project URL, anon key, service_role key

📖 **Detailed instructions**: See `SUPABASE_SETUP_INSTRUCTIONS.md`

### Step 3: Gemini API Setup (2 min)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 4: Configure Environment (2 min)

```bash
# Create environment files
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Edit .env with your credentials
nano .env  # or use your editor
```

**Required in `.env`**:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
GOOGLE_API_KEY=your_gemini_api_key
```

Generate secret key:
```bash
# On macOS/Linux
openssl rand -hex 32

# Copy output to .env as SECRET_KEY
```

### Step 5: Run the Application (1 min)

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Start frontend
npm run dev
```

**Open browser**: http://localhost:5173

## Test It Works

### 1. Health Check

Visit: http://localhost:8000/api/health

Should see:
```json
{
  "status": "healthy",
  "service": "NC-ASK Backend API"
}
```

### 2. Test Query (Optional - No Documents Yet)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What services are available?"}'
```

### 3. Test Crisis Detection

In the web UI (http://localhost:5173), type:
```
I am feeling hopeless
```

You should see a **red crisis banner** with resources.

## Add Your First Documents (Optional)

```bash
# 1. Add files to backend/data/
cp /path/to/your/documents/*.pdf backend/data/

# 2. Run ingestion
cd backend
python scripts/ingest_documents.py

# 3. Test with a real question
# Go to http://localhost:5173 and ask about your documents
```

**Supported formats**: PDF, DOCX, TXT, HTML

## Common Issues

### "Failed to initialize Supabase client"
- ✅ Check `.env` has correct Supabase credentials
- ✅ Verify Supabase project is active

### "Failed to load embedding model"
- ⏳ First download takes ~2 min (downloading 80MB model)
- ✅ Check internet connection

### Frontend shows "Failed to fetch"
- ✅ Ensure backend is running on port 8000
- ✅ Check `frontend/.env.local` has `VITE_API_BASE_URL=http://localhost:8000`

### Backend crashes on query
- ✅ Verify Google API key is correct
- ✅ Check you've run the Supabase SQL script

## Project Structure

```
autism-chat-bot/
├── backend/          # FastAPI backend
│   ├── main.py      # Start here
│   ├── services/    # Core logic
│   └── scripts/     # Utilities
├── frontend/        # React frontend
│   └── src/
└── docs/           # Documentation
```

## Next Steps

1. **Add documents**: Place PDFs/DOCX in `backend/data/` and run ingestion
2. **Read architecture**: `docs/ARCHITECTURE.md`
3. **Check roadmap**: `docs/ROADMAP.md`
4. **Review features**: `README.md`

## Development Workflow

```bash
# Always activate venv first
source venv/bin/activate

# Start backend with hot reload
cd backend
python -m uvicorn main:app --reload

# Start frontend with hot reload
npm run dev

# Type checking
npm run typecheck

# Linting
npm run lint
```

## Docker Alternative (Optional)

If you prefer Docker:

```bash
# Build and start everything
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Getting Help

- **Setup issues**: See `docs/SETUP.md`
- **Supabase help**: See `SUPABASE_SETUP_INSTRUCTIONS.md`
- **Architecture questions**: See `docs/ARCHITECTURE.md`
- **Implementation details**: See `IMPLEMENTATION_SUMMARY.md`

## Summary

You should now have:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5173
- ✅ Database configured in Supabase
- ✅ Crisis detection working
- ✅ Ready to add documents and test queries

**Total setup time**: ~15 minutes

**Ready for**: Development, testing, document ingestion

---

🎉 **You're all set!** Start asking questions at http://localhost:5173
