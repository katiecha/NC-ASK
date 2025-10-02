# 🚀 START HERE - Complete Docker Setup Guide

This guide will get you running with zero issues. Follow these steps **exactly** in order.

## Prerequisites

✅ Docker Desktop installed and running  
✅ Completed Supabase setup (you mentioned you did this)  
✅ Terminal access

## Step-by-Step Setup (5 minutes)

### Step 1: Create Environment File

```bash
cd /Users/hongliu/UNC/2025-2026/COMP523/autism-chat-bot
cp env.example .env
```

### Step 2: Get Your API Keys

#### A. Supabase Keys (You already have these!)
1. Go to https://app.supabase.com/project/YOUR_PROJECT/settings/api
2. Copy these three values:
   - **Project URL** (looks like: `https://abcdefgh.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)
   - **service_role key** (long string starting with `eyJ...`)

#### B. Google Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### C. Generate Secret Key
```bash
openssl rand -hex 32
```
Copy the output (64-character string)

### Step 3: Update .env File

Open `.env` in your editor and replace these values:

```bash
# Paste your Supabase URL
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co

# Paste your Supabase anon key
SUPABASE_ANON_KEY=eyJhbGc...

# Paste your Supabase service role key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Paste your Gemini API key
GOOGLE_API_KEY=AIza...

# Paste the generated secret key
SECRET_KEY=abc123def456...

# Keep this as is
ENVIRONMENT=development
```

**Save the file!**

### Step 4: Run Pre-flight Check

This will validate everything before starting:

```bash
./preflight-check.sh
```

**If you see errors**, fix them before proceeding. The script tells you exactly what's wrong.

### Step 5: Start Docker Compose

```bash
docker compose up --build
```

**What to expect:**
- First run takes 5-10 minutes (downloading images, installing dependencies)
- Backend will download an 80MB AI model (sentence-transformers)
- You'll see lots of output - this is normal!
- Look for these success messages:
  - ✅ `redis_1     | Ready to accept connections`
  - ✅ `backend_1   | Application startup complete`
  - ✅ `frontend_1  | Local: http://localhost:5173/`

### Step 6: Verify Everything Works

Open these URLs in your browser:

1. **Frontend**: http://localhost:5173
   - Should show the NC-ASK interface

2. **Backend Health**: http://localhost:8000/health
   - Should show: `{"status":"healthy","service":"NC-ASK Backend"}`

3. **Backend API Docs**: http://localhost:8000/docs
   - Should show Swagger UI with all endpoints

## Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Find what's using the port
lsof -i :8000
lsof -i :5173

# Stop the process or change ports in docker-compose.yml
```

### Issue: "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop application
# Wait for it to fully start (icon in menu bar)
# Try again
```

### Issue: "Failed to load embedding model"
- **Solution**: This is normal on first run! Wait 2-3 minutes for the model to download.
- **Check**: Look for "Downloading (…)%" in backend logs

### Issue: "Failed to initialize Supabase client"
- **Solution**: Check your `.env` file has correct Supabase credentials
- **Verify**: Run `./preflight-check.sh`

### Issue: Build fails with dependency errors
- **Solution**: Clear Docker cache and rebuild
```bash
docker compose down
docker system prune -a
docker compose up --build
```

## Testing Your Setup

### 1. Test Health Endpoint
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"NC-ASK Backend"}
```

### 2. Test Crisis Detection
In the web UI (http://localhost:5173), type:
```
I feel hopeless
```
You should see a red crisis banner with resources.

### 3. Add Documents (Optional)
```bash
# Copy documents to data folder
cp /path/to/your/*.pdf backend/data/

# Run ingestion
docker compose exec backend python scripts/ingest_documents.py
```

## Useful Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f redis
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop Everything
```bash
# Stop but keep containers
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove everything including volumes
docker compose down -v
```

### Access Container Shell
```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend sh
```

### Rebuild After Code Changes
```bash
# Backend changes are auto-detected (hot reload)
# Frontend changes are auto-detected (HMR)

# If you need to rebuild:
docker compose up --build
```

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
│  (Vite)     │      │  (FastAPI)  │      │  (Cloud)    │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            ↓
                     ┌─────────────┐
                     │   Redis     │
                     │  (Cache)    │
                     └─────────────┘
```

## What's Running

| Service  | Port | Purpose                    | Access                   |
|----------|------|----------------------------|--------------------------|
| Frontend | 5173 | React/Vite UI              | http://localhost:5173    |
| Backend  | 8000 | FastAPI + AI/ML            | http://localhost:8000    |
| Redis    | 6379 | Caching + Sessions         | Internal only            |
| Supabase | N/A  | Database + Vector Search   | Cloud (via API)          |

## File Changes & Hot Reload

- **Backend Python files**: Auto-reload (via uvicorn --reload)
- **Frontend React/TS files**: Auto-reload (via Vite HMR)
- **Environment variables**: Requires restart
- **Dependencies**: Requires rebuild (`docker compose up --build`)

## Next Steps

1. ✅ Verify all 3 URLs work (frontend, backend health, API docs)
2. ✅ Test crisis detection in the UI
3. ✅ Add your first documents to `backend/data/`
4. ✅ Run document ingestion
5. ✅ Ask questions about your documents!

## Getting Help

- **Pre-flight issues**: Run `./preflight-check.sh` for diagnostics
- **Build issues**: Check `docker compose logs backend`
- **Runtime issues**: Check `docker compose logs -f`
- **Documentation**: See `DOCKER_SETUP.md` for detailed info

---

## Quick Reference Card

```bash
# Start everything
docker compose up --build

# Stop everything
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps

# Run pre-flight check
./preflight-check.sh

# Access backend shell
docker compose exec backend bash

# Run ingestion
docker compose exec backend python scripts/ingest_documents.py
```

---

🎉 **That's it!** You should now have NC-ASK running at http://localhost:5173

