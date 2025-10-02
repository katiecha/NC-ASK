# NC-ASK Changelog

## Recent Updates (October 2025)

### Docker Setup & Configuration
- ✅ Complete Docker setup with multi-container orchestration
- ✅ Created `backend/Dockerfile` with Python 3.11-slim
- ✅ Created `frontend/Dockerfile` with Node 18-alpine  
- ✅ Updated `docker-compose.yml` with health checks and proper dependencies
- ✅ Created `preflight-check.sh` validation script
- ✅ Created `env.example` with all required environment variables

### Dependency Fixes
- ✅ Fixed `sentence-transformers` version (2.2.2 → >=2.3.0) to resolve huggingface_hub import errors
- ✅ Fixed `httpx` version conflict (0.25.2 → >=0.24.0,<0.25.0) for supabase compatibility
- ✅ Updated frontend to use `npm install` instead of `npm ci` (no package-lock.json)

### Configuration Updates
- ✅ Fixed `ALLOWED_ORIGINS` handling in backend config (now uses property method for flexibility)
- ✅ Updated Vite config for Docker (port 5173, host 0.0.0.0, usePolling for file watching)
- ✅ Created `frontend/package.json` for standalone frontend container
- ✅ Fixed backend config to properly parse CORS origins from environment variables

### Documentation Updates
- ✅ Updated `docs/SETUP.md` - Added comprehensive Docker section as recommended method
- ✅ Updated `docs/ARCHITECTURE.md` - Added Docker deployment details and updated AI/ML versions
- ✅ Updated `docs/IMPLEMENTATION_SUMMARY.md` - Added Docker files and updated setup instructions
- ✅ Created `START_HERE.md` - Step-by-step Docker setup guide
- ✅ Created `DOCKER_SETUP.md` - Detailed Docker reference and troubleshooting

### Files Removed (Cleanup)
- ❌ `QUICKSTART.md` - Superseded by START_HERE.md (Docker-focused)
- ❌ `FIXES_APPLIED.md` - Internal documentation, no longer needed
- ❌ `setup-docker.sh` - Replaced by preflight-check.sh

### Files Created
- 📄 `START_HERE.md` - Primary Docker setup guide
- 📄 `DOCKER_SETUP.md` - Comprehensive Docker documentation
- 📄 `env.example` - Environment variables template
- 📄 `frontend/Dockerfile` - Frontend container configuration
- 📄 `backend/Dockerfile` - Backend container configuration  
- 📄 `frontend/package.json` - Frontend dependencies
- 📄 `preflight-check.sh` - Pre-flight validation script
- 📄 `CHANGELOG.md` - This file

## System Status

### ✅ Working
- Backend container builds and runs successfully
- Frontend container builds and runs successfully
- Redis container runs with persistent storage
- Hot reload works for both frontend and backend
- Health checks enabled on all services
- Crisis detection functional
- RAG pipeline operational

### 📝 Configuration Required
Users need to provide:
- Supabase URL and API keys
- Google Gemini API key
- Generate SECRET_KEY with `openssl rand -hex 32`

### 🎯 Next Steps
1. Complete Supabase setup (follow SUPABASE_SETUP_INSTRUCTIONS.md in docs/)
2. Get Google Gemini API key
3. Configure `.env` file
4. Run `docker compose up --build`
5. Add documents to `backend/data/`
6. Run ingestion: `docker compose exec backend python scripts/ingest_documents.py`

## Architecture

```
NC-ASK System
├── Backend (FastAPI + Python 3.11)
│   ├── RAG Pipeline (LangChain)
│   ├── Embeddings (sentence-transformers >=2.3.0)
│   ├── LLM (Google Gemini 1.5 Flash)
│   └── Crisis Detection
├── Frontend (React 18 + Vite + TypeScript)
│   └── Accessible UI Components
├── Redis (Caching & Sessions)
└── Supabase (PostgreSQL + pgvector + Storage)
```

## Development Workflow

### Docker Commands
```bash
# Start everything
docker compose up --build

# View logs
docker compose logs -f

# Run ingestion
docker compose exec backend python scripts/ingest_documents.py

# Access backend shell
docker compose exec backend bash

# Stop everything
docker compose down
```

### Port Mappings
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Redis: localhost:6379

## Known Issues & Solutions

### Issue: Port Already in Use
**Solution**: Check what's using the port: `lsof -i :8000` or `lsof -i :5173`

### Issue: Docker Not Running
**Solution**: Start Docker Desktop and wait for it to fully initialize

### Issue: Frontend Can't Connect to Backend
**Solution**: Ensure `VITE_API_BASE_URL=http://localhost:8000` in docker-compose.yml

### Issue: Backend Dependencies Fail
**Solution**: Clear Docker cache with `docker system prune -a` and rebuild

## References

- Main Documentation: `README.md`
- Docker Setup: `START_HERE.md` and `DOCKER_SETUP.md`
- Architecture: `docs/ARCHITECTURE.md`
- Supabase Setup: `docs/SUPABASE_SETUP_INSTRUCTIONS.md`
- Development: `docs/SETUP.md`

---

For questions or issues, check the documentation or run `./preflight-check.sh` for diagnostics.

