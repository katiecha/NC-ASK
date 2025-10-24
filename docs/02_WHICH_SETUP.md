# Which Setup Should I Use?

Quick decision guide for NC-ASK development and deployment.

---

## TL;DR - Which One?

| Use Case | Use This | Why |
|----------|----------|-----|
| **Daily coding/iteration** | `npm run dev` | Fastest hot reload, direct debugging |
| **Team consistency** | `docker-compose up` | Everyone has same environment |
| **Demos/presentations** | `docker-compose.prod.yml` | Production-like, professional |
| **Production deployment** | See DEPLOYMENT.md | Proper production setup |

---

## Local Development (`npm run dev`)

**Use when:** You're actively coding and want fastest iteration.

### Pros
- **Fastest hot reload** - Changes reflect instantly
- **Easy debugging** - Direct access to Python/Node processes
- **Native tools** - Use your IDE's debugger, breakpoints work perfectly
- **Direct file access** - No container layers

### Cons
- Requires Python 3.11+ and Node 18+ installed locally
- More setup (venv, npm install)
- Environment inconsistencies possible across team

### Setup
See [04_LOCAL_SETUP.md](04_LOCAL_SETUP.md) (~10 minutes)

### Commands
```bash
npm run dev              # Start both frontend + backend
# OR
make dev                 # Using Makefile
```

---

## Docker Development (`docker-compose up`)

**Use when:** You want consistent environment or don't want to install Python/Node locally.

### Pros
- **Consistent environment** - Everyone runs the same thing
- **No local dependencies** - Just need Docker
- **Closer to production** - Same containerization
- **Clean machine** - No Python/Node polluting your system

### Cons
- Slightly slower hot reload (volume mounts)
- Debugging is harder (need to attach to container)
- Uses more disk space
- Requires Docker Desktop

### Setup
See [03_DOCKER_SETUP.md](03_DOCKER_SETUP.md) (~5 minutes)

### Commands
```bash
docker-compose up --build    # Start dev containers
# OR
make docker-dev              # Using Makefile
```

---

## Production/Demo Setup

**Use when:** Demoing or deploying to production.

### For Demos
```bash
# Run production containers locally
docker-compose -f docker-compose.prod.yml up --build

# OR with Makefile
make docker-prod
```

This gives you:
- Gunicorn (4 workers) instead of uvicorn dev server
- Nginx serving optimized React build
- Security headers enabled
- Production-like performance
- No dev volumes or debug tools

### For Production Deployment
See [05_DEPLOYMENT.md](05_DEPLOYMENT.md) for:
- Cloud deployment (Vercel + Render)
- Self-hosted Docker deployment
- Environment variable security
- Monitoring setup

---

## Key Differences Summary

| Feature | Local Dev | Docker Dev | Production |
|---------|-----------|------------|------------|
| **Hot reload** | Fastest | Fast | N/A (build once) |
| **Setup time** | 10 min | 5 min | 20 min |
| **Requires** | Python + Node | Docker | Docker |
| **Debugging** | Easy | Medium | Hard |
| **Environment** | Varies | Consistent | Consistent |
| **Backend** | uvicorn | uvicorn | gunicorn |
| **Frontend** | Vite dev | Vite dev | nginx + built |
| **Image size** | N/A | ~1.5GB | ~200MB |

---

## Recommendation for Your Team

### Daily Development
- **Frontend-focused devs**: Use `npm run dev` (local) - fastest React hot reload
- **Backend-focused devs**: Use `npm run dev` (local) - easy Python debugging
- **Full-stack devs**: Your choice, both work great
- **New team members**: Use Docker - less setup hassle

### Demos & Testing
- **Demos**: Use `docker-compose.prod.yml`
- **Integration testing**: Use Docker dev or prod
- **E2E testing**: Use production setup

---

## Switching Between Modes

You can freely switch between modes:

```bash
# Stop local dev
Ctrl+C on terminal running npm run dev

# Start Docker dev
docker-compose up --build

# Switch back to local
docker-compose down
npm run dev
```

**Important:** Make sure to use the right `.env` setup:
- **Local mode**: Create `frontend/.env.local` with `VITE_API_BASE_URL=http://localhost:8000`
- **Docker mode**: Already configured in `docker-compose.yml`

---

## Still Unsure?

**Start with Docker if:**
- You're new to the project
- You don't have Python 3.11+ or Node 18+ installed
- You want "it just works" experience

**Start with Local if:**
- You're actively developing features
- You need fast iteration cycles
- You're comfortable with Python + Node setup

Both are fully supported and work great!
