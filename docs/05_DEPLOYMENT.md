# NC-ASK Production Deployment Guide

This guide covers deploying NC-ASK to production using either Docker (self-hosted) or cloud platforms.

## Table of Contents
- [Docker Production Deployment](#docker-production-deployment)
- [Cloud Deployment (Vercel + Render)](#cloud-deployment-vercel--render)
- [Environment Variables](#environment-variables)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)

---

## Docker Production Deployment

### Prerequisites
- Docker and Docker Compose installed
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- Production `.env` file configured

### Step 1: Configure Environment

Create `.env` file with production values:

```bash
# Copy template
cp .env.example .env

# Edit with production values
nano .env
```

**Critical settings for production:**
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO

# Use production Supabase instance
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_ANON_KEY=your_production_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_production_service_role_key

# Production Gemini API key
GOOGLE_API_KEY=your_production_api_key

# Generate strong secret: openssl rand -hex 32
SECRET_KEY=<strong-random-secret-key>

# Set production frontend URL
ALLOWED_ORIGINS=https://your-domain.com
```

### Step 2: Build and Run

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run in detached mode
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

**Services will run on:**
- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000`

### Step 3: Add Reverse Proxy (Recommended)

Use nginx or Caddy as a reverse proxy for SSL termination:

**Example nginx config:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 4: Database Setup

Run the Supabase setup SQL in your production database:

```bash
# In Supabase Dashboard → SQL Editor
# Paste and run: backend/scripts/supabase_setup.sql
```

### Step 5: Ingest Documents

```bash
# Access backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# Run ingestion
python scripts/ingest_documents.py
```

---

## Cloud Deployment (Vercel + Render)

### Frontend: Vercel

1. **Connect Repository**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Select `frontend` as root directory

2. **Configure Build Settings**
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

3. **Set Environment Variables**
   ```
   VITE_API_BASE_URL=https://your-backend.onrender.com
   ```

4. **Deploy**
   - Vercel will auto-deploy on push to main

### Backend: Render

1. **Create Web Service**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repo

2. **Configure Service**
   ```
   Name: nc-ask-backend
   Environment: Docker
   Dockerfile Path: ./backend/Dockerfile.prod
   Port: 8000
   ```

3. **Set Environment Variables**
   Add all required variables from `.env.example`:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `GOOGLE_API_KEY`
   - `SECRET_KEY`
   - `ENVIRONMENT=production`
   - `ALLOWED_ORIGINS=https://your-frontend.vercel.app`

4. **Deploy**
   - Render will build and deploy automatically

### Alternative: Railway

Similar to Render but with different pricing:

1. **Create Project** at [railway.app](https://railway.app)
2. **Add Service** → GitHub Repo
3. **Configure** using production Dockerfile
4. **Set Environment Variables**
5. **Deploy**

---

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Set to `production` | `production` |
| `SUPABASE_URL` | Production Supabase URL | `https://proj.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | `eyJ...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | `eyJ...` |
| `GOOGLE_API_KEY` | Gemini API key | `AIza...` |
| `SECRET_KEY` | Session signing key (32+ chars) | `<random-hex>` |
| `ALLOWED_ORIGINS` | Frontend URLs (comma-separated) | `https://yourdomain.com` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `RATE_LIMIT_PER_MINUTE` | `10` | API rate limit |
| `MAX_QUERY_LENGTH` | `500` | Max query characters |

---

## Security Considerations

### 1. Secrets Management
- **Never commit** `.env` files
- Use platform secret management (Render Secrets, Vercel Environment Variables)
- Rotate `SECRET_KEY` periodically
- Use separate Supabase projects for dev/prod

### 2. API Keys
- Restrict Gemini API key to production domain
- Use Supabase Row Level Security (RLS) policies
- Monitor API usage for anomalies

### 3. CORS Configuration
- Set `ALLOWED_ORIGINS` to only your production frontend
- Never use `*` in production

### 4. HTTPS
- Always use HTTPS in production
- Configure HSTS headers
- Use HTTP/2

### 5. Container Security
- Run containers as non-root user (already configured in Dockerfile.prod)
- Keep base images updated
- Scan images for vulnerabilities

---

## Monitoring

### Health Checks

Both services expose health check endpoints:

- **Backend**: `https://your-api.com/api/health`
- **Frontend**: `https://your-app.com/health`

### Logging

**Docker deployment:**
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

**Cloud deployment:**
- Render: View logs in dashboard
- Vercel: View function logs in dashboard

### Metrics to Monitor

1. **API Response Times** (target < 5s p95)
2. **Error Rates** (target < 1%)
3. **Supabase Connection Pool** (free tier: 60 connections)
4. **LLM API Costs** (Gemini Flash pricing)
5. **Crisis Detection Rate**

### Alerts

Set up alerts for:
- API error rate > 5%
- Response time > 10s
- Service downtime
- API quota exceeded

---

## Backup & Disaster Recovery

### Database Backups

Supabase automatically backs up your database daily (Pro plan).

**Manual backup:**
```bash
# From Supabase Dashboard
# Settings → Database → Download backup
```

### Document Storage

Documents in Supabase Storage are replicated across availability zones.

**Manual backup:**
```bash
# Download all documents from Supabase Storage bucket
# Use Supabase CLI or dashboard
```

---

## Scaling

### Current Architecture (MVP)

- **Backend**: Single container with 4 gunicorn workers
- **Frontend**: Static files served by nginx
- **Database**: Supabase free tier (60 connections)

### Scaling Options

1. **Horizontal Scaling**
   - Run multiple backend containers behind load balancer
   - Update `docker-compose.prod.yml` with replicas

2. **Database Scaling**
   - Upgrade to Supabase Pro for connection pooling
   - Add read replicas

3. **CDN**
   - Use Cloudflare or similar for frontend caching
   - Cache static assets

4. **Caching**
   - Add Redis for frequent queries
   - Cache LLM responses (with appropriate TTL)

---

## Troubleshooting

### Backend container won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# - Missing environment variables
# - Supabase connection error
# - Port already in use
```

### Frontend shows "Failed to fetch"
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS settings in backend
- Verify backend is accessible from frontend

### High API costs
- Implement query caching
- Add rate limiting per IP
- Monitor Gemini API dashboard

---

## Support

For deployment issues:
- Check [03_DOCKER_SETUP.md](03_DOCKER_SETUP.md) for Docker troubleshooting
- Review [06_ARCHITECTURE.md](06_ARCHITECTURE.md) for system design
- Create an issue in the GitHub repository

