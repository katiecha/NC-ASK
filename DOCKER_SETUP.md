# NC-ASK Docker Setup Guide

Complete guide to run NC-ASK entirely in Docker without installing anything on your local system.

## Prerequisites

- **Docker Desktop** installed and running
- **Supabase account** (free at https://supabase.com)
- **Google account** for Gemini API

## Quick Start (5 minutes)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd autism-chat-bot

# Copy environment template
cp env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```bash
# Supabase (get from https://app.supabase.com/project/YOUR_PROJECT/settings/api)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Google Gemini API (get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_gemini_api_key_here

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
```

### 3. Start Everything with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health

## Detailed Setup Instructions

### Step 1: Supabase Setup

1. **Create Supabase Project**:
   - Go to https://supabase.com
   - Click "New Project"
   - Name: `nc-ask`
   - Region: `us-east-1`
   - Save the database password!

2. **Run Database Setup**:
   - Go to SQL Editor in Supabase
   - Copy contents of `backend/scripts/supabase_setup.sql`
   - Paste and run the script

3. **Create Storage Bucket**:
   - Go to Storage → Create bucket
   - Name: `documents`
   - Public: **OFF**
   - File size limit: `52428800` (50 MB)
   - Allowed MIME types: `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/html`, `text/plain`

4. **Get API Credentials**:
   - Go to Settings → API
   - Copy Project URL, anon key, and service_role key

### Step 2: Google Gemini API Setup

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key to your `.env` file

### Step 3: Environment Configuration

Create `.env` file in the project root:

```bash
# Copy the template
cp env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

Required variables:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GOOGLE_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_generated_secret_key
ENVIRONMENT=development
```

### Step 4: Run with Docker

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Docker Services

### Backend (FastAPI)
- **Port**: 8000
- **Image**: Built from `./backend/Dockerfile`
- **Features**: 
  - FastAPI server with hot reload
  - Vector embeddings with sentence-transformers
  - Document processing (PDF, DOCX, HTML, TXT)
  - Crisis detection
  - RAG pipeline

### Frontend (React/Vite)
- **Port**: 5173
- **Image**: Built from `./frontend/Dockerfile`
- **Features**:
  - React 18 with TypeScript
  - Vite development server
  - Hot module replacement
  - Responsive design

### Redis
- **Port**: 6379
- **Image**: `redis:7-alpine`
- **Features**:
  - Caching layer
  - Session storage
  - Persistent data with AOF

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
- ✅ Check `.env` has correct Supabase credentials
- ✅ Verify Supabase project is active
- ✅ Ensure service_role key is used for backend operations

#### "Failed to load embedding model"
- ⏳ First download takes ~2 minutes (80MB model)
- ✅ Check internet connection
- ✅ Check Docker has enough memory (4GB+ recommended)

#### Frontend shows "Failed to fetch"
- ✅ Ensure backend is running on port 8000
- ✅ Check `VITE_API_BASE_URL=http://localhost:8000` in docker-compose.yml
- ✅ Verify backend container is healthy

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

# Check Redis
docker-compose exec redis redis-cli ping
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f backend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Production Deployment

For production deployment, you'll want to:

1. **Use production Dockerfiles**:
   - Build optimized frontend with `npm run build`
   - Use production-grade WSGI server (gunicorn)
   - Remove development dependencies

2. **Environment variables**:
   - Use Docker secrets or external secret management
   - Set `ENVIRONMENT=production`
   - Configure proper logging

3. **Database**:
   - Use managed PostgreSQL instead of Supabase for production
   - Configure proper backup and monitoring

4. **Reverse proxy**:
   - Use nginx or traefik for SSL termination
   - Configure proper CORS and security headers

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

1. ✅ **Test the setup**: Visit http://localhost:5173
2. ✅ **Add documents**: Place files in `backend/data/` and run ingestion
3. ✅ **Test queries**: Ask questions about your documents
4. ✅ **Test crisis detection**: Try queries like "I feel hopeless"
5. ✅ **Read documentation**: Check `docs/` folder for more details

## Support

- **Setup issues**: Check this guide and `docs/SETUP.md`
- **Supabase help**: See `SUPABASE_SETUP_INSTRUCTIONS.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`

---

🎉 **You're all set!** The application should now be running entirely in Docker at http://localhost:5173
