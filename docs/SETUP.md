# NC-ASK Setup Guide

Complete setup instructions for the NC-ASK application.

## Prerequisites

### Docker Setup (Recommended)
- **Docker Desktop** installed and running
- **Git**
- **Supabase Account** (free tier is sufficient for MVP)
- **Google Cloud Account** (for Gemini API)

### Local Development Setup (Alternative)
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**
- **Supabase Account** (free tier is sufficient for MVP)
- **Google Cloud Account** (for Gemini API)

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/autism-chat-bot.git
cd autism-chat-bot
```

## 2. Supabase Setup

### Create Supabase Project

1. Go to [Supabase](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in project details:
   - Name: `nc-ask` (or your preferred name)
   - Database Password: (generate a strong password)
   - Region: Choose closest to North Carolina (e.g., `us-east-1`)

### Run Database Setup Script

1. Navigate to your Supabase project
2. Go to SQL Editor: `https://app.supabase.com/project/YOUR_PROJECT/sql`
3. Create a new query
4. Copy the entire contents of `backend/scripts/supabase_setup.sql`
5. Paste and run the script
6. Verify tables were created in the Table Editor

### Create Storage Bucket

1. Go to Storage: `https://app.supabase.com/project/YOUR_PROJECT/storage/buckets`
2. Click "Create new bucket"
3. Settings:
   - Name: `documents`
   - Public: **No** (keep private)
   - File size limit: `52428800` (50MB)
   - Allowed MIME types:
     - `application/pdf`
     - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
     - `text/html`
     - `text/plain`
4. Click "Create bucket"

### Get Supabase Credentials

1. Go to Settings → API: `https://app.supabase.com/project/YOUR_PROJECT/settings/api`
2. Copy these values (you'll need them later):
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (for client-side access)
   - **service_role key** (for server-side admin access)

## 3. Google Gemini API Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (you'll need it for `.env`)

## 4. Backend Setup

### Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and fill in your credentials
nano .env  # or use your preferred editor
```

Update the following in `.env`:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=generate-a-random-secret-key  # Run: openssl rand -hex 32
```

### Test Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

Visit `http://localhost:8000` - you should see:
```json
{
  "message": "NC-ASK API",
  "version": "1.0.0",
  "status": "running"
}
```

Visit `http://localhost:8000/api/health` to verify health check.

## 5. Frontend Setup

### Install Dependencies

```bash
npm install
```

### Configure Environment Variables

```bash
# Copy the example env file
cp frontend/.env.example frontend/.env.local

# Edit if needed (default should work)
nano frontend/.env.local
```

The default should be:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Test Frontend

```bash
npm run dev
```

Visit `http://localhost:5173` - you should see the NC-ASK interface.

## 6. Ingest Sample Documents

### Add Documents to Data Directory

1. Place your source documents in `backend/data/`
2. Supported formats: PDF, DOCX, TXT, HTML

Example:
```bash
backend/data/
  ├── nc-iep-guide.pdf
  ├── autism-resources.docx
  └── faq.txt
```

### Run Ingestion Script

```bash
cd backend
python scripts/ingest_documents.py
```

You should see output like:
```
Ingesting: nc-iep-guide.pdf
✓ Successfully ingested: nc-iep-guide
  - Document ID: 1
  - Chunks created: 25
```

## 7. Test the Complete System

### Test Query Endpoint

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I request an IEP evaluation?"}'
```

### Test Crisis Detection

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "I am feeling hopeless"}'
```

You should see crisis resources in the response.

### Test Frontend Integration

1. Open `http://localhost:5173`
2. Type a question: "What autism services are available in NC?"
3. Submit and verify you get a response with citations

## 8. Docker Setup (Recommended Method)

Docker is the recommended way to run NC-ASK as it eliminates the need to install Python, Node.js, and other dependencies on your local system.

### Quick Start with Docker

1. **Ensure Docker is running**:
```bash
docker --version  # Should show Docker version
```

2. **Create environment file**:
```bash
cp env.example .env
# Edit .env with your Supabase and Gemini credentials
```

3. **Run preflight check** (optional but recommended):
```bash
./preflight-check.sh
```

4. **Start all services**:
```bash
docker compose up --build
```

Services will be available at:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Redis**: Port 6379 (internal)

### Docker Services

The application runs three Docker containers:
- **backend** - FastAPI with Python 3.11, sentence-transformers, and all AI/ML dependencies
- **frontend** - React/Vite with Node 18
- **redis** - Redis 7 for caching and session storage

### Docker Commands

```bash
# Start services (detached mode)
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after code changes
docker compose up --build

# Check status
docker compose ps

# Access backend shell
docker compose exec backend bash

# Run document ingestion
docker compose exec backend python scripts/ingest_documents.py
```

### Docker Configuration Files

- `docker-compose.yml` - Multi-container orchestration
- `backend/Dockerfile` - Backend container configuration  
- `frontend/Dockerfile` - Frontend container configuration
- `env.example` - Environment variables template
- `preflight-check.sh` - Pre-flight validation script

### Advantages of Docker Setup

✅ No need to install Python or Node.js locally  
✅ Consistent environment across all machines  
✅ Isolated dependencies (won't conflict with system packages)  
✅ Easy to start/stop all services  
✅ Hot reload works for both frontend and backend  
✅ Production-like environment  

For detailed Docker setup instructions, see `../START_HERE.md` and `../DOCKER_SETUP.md`.

## Troubleshooting

### Backend Issues

**Error: "Failed to initialize Supabase client"**
- Verify your Supabase credentials in `.env`
- Check that your Supabase project is active

**Error: "Failed to load embedding model"**
- First download may take time (downloading model from HuggingFace)
- Ensure you have internet connection
- Check disk space (model is ~80MB)

**Error: "Failed to initialize Gemini model"**
- Verify your Google API key is correct
- Check API quota limits

### Frontend Issues

**Error: "Failed to fetch"**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `VITE_API_BASE_URL` in `.env.local`

### Database Issues

**Error: "relation does not exist"**
- Run the Supabase setup script again
- Verify all tables were created in Table Editor

**Slow vector search**
- Vector search requires at least 1000 rows for optimal performance
- Add more documents to improve index performance

## Next Steps

1. **Add More Documents**: Place documents in `backend/data/` and run ingestion
2. **Test All Features**:
   - Crisis detection with various keywords
   - Plain language responses
   - Citation accuracy
3. **Monitor Logs**: Check backend logs for any errors
4. **Review Architecture**: See `docs/ARCHITECTURE.md` for system details
5. **Check Roadmap**: See `docs/ROADMAP.md` for next phase

## Production Deployment

For production deployment instructions, see:
- Phase 6 in `docs/ROADMAP.md`
- Backend: Deploy to Render/Railway
- Frontend: Deploy to Vercel
- Database: Already on Supabase (ensure you upgrade from free tier if needed)

## Support

For issues or questions:
- Check existing documentation in `docs/`
- Review code comments
- Check Supabase documentation: https://supabase.com/docs
- Check FastAPI documentation: https://fastapi.tiangolo.com/
