# NC-ASK Docker Setup Guide

Complete guide to run NC-ASK entirely in Docker without installing anything on your local system.

**Note**: This guide covers **development** Docker setup. For production deployment, see [05_DEPLOYMENT.md](05_DEPLOYMENT.md).

## Prerequisites

- [x] **Docker Desktop** installed and running
- [x] **Git** installed

**Note:** You'll need Supabase and Gemini API keys later, but we'll get Docker running first.

---

## Quick Start (5 minutes)

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd NC-ASK
```

### Step 2: Setup Environment (Placeholders for Now)

```bash
# Copy environment template
cp .env.example .env
```

**For now**, leave placeholder values in `.env`. We'll add real credentials after Docker is running:

```bash
# Placeholders - we'll update these after seeing Docker work
SUPABASE_URL=https://placeholder.supabase.co
SUPABASE_ANON_KEY=placeholder
SUPABASE_SERVICE_ROLE_KEY=placeholder
GOOGLE_API_KEY=placeholder

# Generate a real secret key
SECRET_KEY=$(openssl rand -hex 32)

ENVIRONMENT=development
```

### Step 3: Start Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up --build -d
```

Docker will:
- Build backend container (Python + FastAPI)
- Build frontend container (Node + React)
- Download ~80MB model for embeddings (first run only)

**This will take 3-5 minutes on first run.**

### Step 4: Verify It's Running

```bash
# Check container status
docker-compose ps
# Should show both backend and frontend as "Up"
```

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/health

Press `Ctrl+C` to stop (or `docker-compose down` if running detached).

---

## External Services Setup

Now let's configure the external services for full functionality.

### Step 5: Supabase Setup

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
   - Restart Docker: `docker-compose restart`

### Step 6: Google Gemini API Setup

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Update `.env` file: Replace `GOOGLE_API_KEY=placeholder` with your actual key
5. Restart Docker: `docker-compose restart`

### Step 7: Ingest Documents (Optional)

```bash
# Access backend container
docker-compose exec backend bash

# Run ingestion script
python scripts/ingest_documents.py

# Exit container
exit
```

---

## You're Done!

Visit http://localhost:5173 to use the application!

## Common Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Restart services (after .env changes)
docker-compose restart

# Rebuild images (after code changes)
docker-compose up --build
```

---

## Docker Services

### Backend (FastAPI)
- **Port**: 8000
- **Image**: Built from `./backend/Dockerfile.dev`
- **Features**:
  - FastAPI server with hot reload
  - Vector embeddings with sentence-transformers
  - Document processing (PDF, DOCX, HTML, TXT)
  - Crisis detection
  - RAG pipeline

### Frontend (React/Vite)
- **Port**: 5173
- **Image**: Built from `./frontend/Dockerfile.dev`
- **Features**:
  - React 18 with TypeScript
  - Vite development server
  - Hot module replacement
  - Responsive design

**Note**: Redis has been removed from the MVP as it was not being used. Add it back if implementing caching.

## Development Workflow

### Making Changes

```bash
# Code changes are automatically reflected due to volume mounts
# Backend changes: Edit files in ./backend/
# Frontend changes: Edit files in ./frontend/

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Adding Documents

```bash
# 1. Add documents to backend/data/
cp /path/to/your/documents/*.pdf backend/data/

# 2. Run ingestion inside the backend container
docker-compose exec backend python scripts/ingest_documents.py

# 3. Test with queries in the web UI
```

### Database Management

```bash
# Access the backend container
docker-compose exec backend bash

# Run Python scripts
docker-compose exec backend python scripts/ingest_documents.py

# Check logs
docker-compose logs backend
```

## Troubleshooting

### Common Issues

#### "Failed to connect to Supabase"
- Check `.env` has correct Supabase credentials
- Verify Supabase project is active
- Ensure service_role key is used for backend operations

#### "Failed to load embedding model"
- First download takes ~2 minutes (80MB model)
- Check internet connection
- Check Docker has enough memory (4GB+ recommended)

#### Frontend shows "Failed to fetch"
- Ensure backend is running on port 8000
- Check `VITE_API_BASE_URL=http://localhost:8000` in docker-compose.yml
- Verify backend container is healthy

#### "Port already in use"
```bash
# Check what's using the port
lsof -i :8000
lsof -i :5173

# Stop conflicting services or change ports in docker-compose.yml
```

#### Docker build fails
```bash
# Clean up Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Health Checks

```bash
# Check all services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:5173
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Production Deployment

**For production deployment, see [05_DEPLOYMENT.md](05_DEPLOYMENT.md)**

Production setup includes:
- Multi-stage Dockerfiles (`Dockerfile.prod`)
- Gunicorn for backend (4 workers)
- Nginx for serving frontend
- Proper security headers
- Health checks
- Environment-based configuration

Run production stack:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## File Structure

```
autism-chat-bot/
├── backend/
│   ├── Dockerfile          # Backend container
│   ├── main.py            # FastAPI app
│   ├── services/          # Core business logic
│   └── scripts/           # Utility scripts
├── frontend/
│   ├── Dockerfile         # Frontend container
│   ├── src/               # React source code
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Multi-container setup
├── env.example           # Environment template
└── .env                  # Your environment config (not in git)
```

## Next Steps

1. **Test the setup**: Visit http://localhost:5173
2. **Add documents**: Place files in `backend/data/` and run ingestion
3. **Test queries**: Ask questions about your documents
4. **Test crisis detection**: Try queries like "I feel hopeless"
5. **Read documentation**: Check `docs/` folder for more details

## Support

- **Setup issues**: Check this guide and `docs/SETUP.md`
- **Supabase help**: See `SUPABASE_SETUP_INSTRUCTIONS.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`

---

**You're all set!** The application should now be running entirely in Docker at http://localhost:5173
