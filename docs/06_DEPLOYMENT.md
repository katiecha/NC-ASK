# NC-ASK OpenShift Deployment Guide

Complete step-by-step guide to deploy NC-ASK to OpenShift.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Steps](#deployment-steps)
- [Common Operations](#common-operations)
- [Critical Configuration Requirements](#critical-configuration-requirements)
- [Troubleshooting](#troubleshooting)
  - [Backend Issues](#backend-issues)
  - [Frontend Issues](#frontend-issues)
- [Cleanup](#cleanup)
- [Deployment Summary](#deployment-summary)

---

## Prerequisites

1. **OpenShift Cluster Access** (Red Hat Developer Sandbox)
   - Get free account: https://developers.redhat.com/developer-sandbox
   - Save your cluster Console URL and login command

2. **Required Credentials:**
   - Supabase Project URL and Keys (from https://app.supabase.com)
   - Google Gemini API Key (from https://makersuite.google.com/app/apikey)

---

## Deployment Steps

### 1. Install OpenShift CLI

```bash
# macOS
brew install openshift-cli

# Linux
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xvf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/
```

### 2. Login to OpenShift

```bash
# Get login command from web console: top right → Copy login command → Display Token
oc login --token=sha256~xxxxx --server=https://api.your-cluster.com:6443

# Verify
oc whoami
```

### 3. Create Project

```bash
oc new-project nc-ask --description="NC Autism Support & Knowledge Platform"
```

### 4. Create Secrets

```bash
# Replace with your actual credentials
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='https://your-project-id.supabase.co' \
  --from-literal=SUPABASE_ANON_KEY='eyJhbGciOi...' \
  --from-literal=GOOGLE_API_KEY='AIzaSyD...' \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32)
```

### 5. Apply ConfigMap and BuildConfig

```bash
oc apply -f openshift/configmap.yaml
oc apply -f openshift/buildconfig.yaml
```

### 6. Build Images

```bash
# Start builds (takes 5-10 minutes each)
oc start-build nc-ask-backend --follow
oc start-build nc-ask-frontend --follow

# Verify builds completed
oc get builds
```

### 7. Deploy Applications

```bash
oc apply -f openshift/backend-deployment.yaml
oc apply -f openshift/frontend-deployment.yaml

# Watch pods start
oc get pods -w
```

### 8. Create Routes

```bash
oc apply -f openshift/route.yaml

# Get URLs
echo "Frontend: https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')"
echo "Backend: https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')"
```

### 9. Configure CORS and Rebuild Frontend

```bash
# Update CORS
FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')
oc patch configmap nc-ask-config -p '{"data":{"ALLOWED_ORIGINS":"https://'$FRONTEND_URL'"}}'
oc rollout restart deployment/nc-ask-backend

# Rebuild frontend with backend URL
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
oc patch bc/nc-ask-frontend -p '{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"VITE_API_BASE_URL","value":"https://'$BACKEND_URL'"}]}}}}'
oc start-build nc-ask-frontend --follow
```

### 10. Verify Deployment

```bash
# Test backend
curl https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')/api/health

# Check pods are ready
oc get pods
```

---

## Deployment Complete!

Get your deployment URLs:
```bash
echo "Frontend: https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')"
echo "Backend: https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')"
```

Visit your frontend URL in a browser and test with a query like "What is autism?"

---

## Common Operations

```bash
# View logs
oc logs -f deployment/nc-ask-backend
oc logs -f deployment/nc-ask-frontend

# Restart services
oc rollout restart deployment/nc-ask-backend

# Scale replicas
oc scale deployment/nc-ask-backend --replicas=3

# Trigger new builds
oc start-build nc-ask-backend --follow

# Update configuration
oc edit configmap nc-ask-config
oc rollout restart deployment/nc-ask-backend
```

---

## Critical Configuration Requirements

**Before deploying, ensure these are set correctly to avoid failures:**

### Backend Dockerfile Requirements

#### Package Installation Path
```dockerfile
# Package installation for non-root access
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt
COPY --from=builder /install /usr/local  # NOT /root/.local
```

**Why:** The runtime container runs as a non-root user (`appuser`). If packages are installed to `/root/.local` (using `pip install --user`), the non-root user cannot access them, causing "executable not found" errors. Installing to `/usr/local` makes packages accessible to all users.

#### ML Model Loading Timeout
```dockerfile
CMD ["gunicorn", "main:app", "--timeout", "300", ...]
```

**Why:** The default gunicorn worker timeout is 30 seconds. NC-ASK loads sentence-transformer models (~80MB) from HuggingFace on first startup, which can take 60-120 seconds depending on network speed. Without the extended timeout, gunicorn kills workers before they finish loading, causing `CrashLoopBackOff`.

#### Health Check Configuration
```dockerfile
HEALTHCHECK --start-period=180s \
    CMD curl -f http://localhost:8000/api/health || exit 1
```

**Why:** ML models take 3-4 minutes to load across 4 workers. The `--start-period=180s` gives the container 3 minutes before health checks count as failures. Without this, Docker/OpenShift will restart the container prematurely while it's still initializing.

### Resource Limits (CRITICAL for ML workloads)
```bash
# Set adequate resources for ML model loading
oc set resources deployment/nc-ask-backend \
  --limits=cpu=2000m,memory=3Gi \
  --requests=cpu=1000m,memory=2Gi
```

**Why:** 4 gunicorn workers each simultaneously load sentence-transformer models (~300MB RAM each) on startup. With default limits (500m CPU, 1Gi RAM), workers hit resource constraints and hang indefinitely. The pod shows `Running` but never becomes `Ready`. 2 cores and 3Gi RAM provide sufficient headroom for the startup spike.

### Health Probes
```bash
# Set correct path and adequate startup time
oc set probe deployment/nc-ask-backend --readiness \
  --get-url=http://:8000/api/health \
  --initial-delay-seconds=180
```

**Why:** OpenShift uses health probes to determine if a pod is ready to receive traffic. The health endpoint is `/api/health` to match the FastAPI router in `backend/api/routes.py`. The `initialDelaySeconds=180` (3 minutes) allows ML models to load before health checks begin. Without adequate delay, OpenShift marks the pod as failed and restarts it repeatedly.

---

## Troubleshooting

### Backend Issues

#### Pod Running but Never Ready - Resource Limits Too Low (MOST COMMON)

**Symptom:** Pod shows `Running` but never becomes `Ready`. Workers boot but app never starts. Health checks timeout.

**Cause:** ML applications need significantly higher resources. 4 gunicorn workers each load sentence-transformer models (~300MB RAM each). Default limits (500m CPU, 1Gi RAM) cause workers to hang.

**Fix:**
```bash
oc set resources deployment/nc-ask-backend \
  --limits=cpu=2000m,memory=3Gi \
  --requests=cpu=1000m,memory=2Gi
```

#### ImagePullBackOff - Wrong Namespace

**Symptom:** `ImagePullBackOff` with "authentication required"

**Cause:** Deployment referencing wrong namespace in image path

**Fix:**
```bash
NAMESPACE=$(oc project -q)
oc set image deployment/nc-ask-backend \
  backend=image-registry.openshift-image-registry.svc:5000/$NAMESPACE/backend:latest
```

#### CreateContainerError - Executable Not Found

**Symptom:** `CreateContainerError` with "executable file not found" for gunicorn/uvicorn

**Cause:** Packages installed to `/root/.local` instead of `/usr/local` in Dockerfile

**Fix:** Update `backend/Dockerfile.prod`:
```dockerfile
# Builder stage
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Runtime stage
COPY --from=builder /install /usr/local  # NOT /root/.local
```

#### CrashLoopBackOff - Worker Timeout

**Symptom:** Workers boot but container restarts with no error

**Cause:** Gunicorn timeout (30s default) too short for ML model loading

**Fix:** Add to Dockerfile:
```dockerfile
CMD ["gunicorn", "main:app", "--timeout", "300", ...]
```

#### Missing Environment Variables

**Symptom:** Workers boot but app never loads, no error messages

**Fix:**
```bash
oc set env deployment/nc-ask-backend --from=secret/nc-ask-secrets
```

#### Health Check Failures

**Symptom:** Pod not ready, health checks returning 404

**Cause:** Wrong path or insufficient startup time

**Fix:**
```bash
oc set probe deployment/nc-ask-backend --readiness \
  --get-url=http://:8000/api/health \
  --initial-delay-seconds=180
```

#### BuildConfig Using Wrong Branch

**Symptom:** New builds don't include latest code changes

**Fix:**
```bash
oc patch bc/nc-ask-backend -p '{"spec":{"source":{"git":{"ref":"your-branch"}}}}'
```

### Frontend Issues

#### nginx Permission Denied (OpenShift Random UIDs)

**Symptom:** `mkdir() "/var/cache/nginx/client_temp" failed (13: Permission denied)`

**Cause:** OpenShift assigns random UIDs (e.g., 1000650000) for security. nginx can't write to cache directories.

**Fix:** Update `frontend/Dockerfile.prod`:
```dockerfile
# Pre-create directories with wide permissions for random UID
RUN mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp && \
    chmod -R 777 /var/cache/nginx && \
    chmod -R 777 /var/log/nginx && \
    chmod -R 777 /var/run

# Don't specify USER - let OpenShift assign random UID
EXPOSE 8080  # OpenShift doesn't allow ports < 1024
```

Update `nginx.conf`:
```nginx
server {
    listen 8080;  # Changed from 80
    # ... rest of config
}
```

Update service and health probes:
```bash
# Update service to use port 8080
oc patch service nc-ask-frontend -p '{"spec":{"ports":[{"name":"http","port":80,"targetPort":8080}]}}'

# Update health probes
oc set probe deployment/nc-ask-frontend --readiness --get-url=http://:8080/
oc set probe deployment/nc-ask-frontend --liveness --get-url=http://:8080/
```

#### Health Probe Failures After Fixing Permissions

**Symptom:** nginx starts successfully but pod stays `0/1 Running`

**Cause:** Health probes checking port 80 when nginx listens on 8080

**Fix:** Update probes to port 8080 (see commands above)

### Debugging Commands

```bash
# Check pod status and logs
oc get pods
oc describe pod <pod-name>
oc logs <pod-name> --tail=50

# Check resource usage
oc adm top pod -l component=backend

# Check events
oc get events --sort-by='.lastTimestamp' | tail -20

# Test health endpoint
oc exec deployment/nc-ask-backend -- curl http://localhost:8000/api/health

# Monitor builds
oc get builds -w
oc logs -f build/nc-ask-backend-1
```

---


## Deployment Summary

### What Was Deployed
**Deployment Date:** November 11, 2025
**OpenShift Cluster:** Red Hat OpenShift Sandbox
**Namespace:** `katiechai-dev`

#### Backend Deployment
- **Status:** Running and Healthy
- **URL:** https://nc-ask-backend-katiechai-dev.apps.rm3.7wse.p1.openshiftapps.com
- **Image:** `image-registry.openshift-image-registry.svc:5000/katiechai-dev/backend@sha256:bf420f6ce4fe1e04d94f2586f2aeb645ca4484a6bf904e8b20c3094e654a6dbe`
- **Build:** #6 (from `openshift-deployment` branch, commit `b6e729d`)
- **Pod:** `nc-ask-backend-57c6d99c89-k4t9j`
- **Replicas:** 1/1 Running
- **Resources:**
  - CPU Limit: 2000m (2 cores)
  - Memory Limit: 3Gi
  - CPU Request: 1000m
  - Memory Request: 2Gi
- **Configuration:**
  - Gunicorn workers: 4
  - Worker timeout: 300s
  - Health check: `/api/health`
  - Initial delay: 180s
  - Port: 8000

#### Frontend Deployment
- **Status:** Running and Healthy
- **URL:** https://nc-ask-frontend-katiechai-dev.apps.rm3.7wse.p1.openshiftapps.com
- **Image:** `image-registry.openshift-image-registry.svc:5000/katiechai-dev/frontend@sha256:20ade03c7f1abb0a365d6e68c003d99e047d63c410d67a7cd7ed899eb3b3a5fe`
- **Build:** #7 (from `openshift-deployment` branch, commit `351caa0`)
- **Pod:** `nc-ask-frontend-677884668c-jdcld`
- **Replicas:** 1/1 Running
- **Configuration:**
  - Nginx workers: 8 (auto-detected)
  - Port: 8080
  - Health check: `/` on port 8080
  - VITE_API_BASE_URL: `https://nc-ask-backend-katiechai-dev.apps.rm3.7wse.p1.openshiftapps.com`

#### Build Statistics
| Component | Builds | Final Build Time | Status |
|-----------|--------|------------------|--------|
| Backend | 6 builds | ~23.5 minutes | Success |
| Frontend | 7 builds | ~93 seconds (cached) | Success |

#### Deployment Architecture

```
Internet (HTTPS)
    │
    ├──> Route: nc-ask-frontend
    │    └──> Service: nc-ask-frontend (port 80 → 8080)
    │         └──> Pod: nc-ask-frontend-677884668c-jdcld
    │              ├── nginx:alpine (8 workers, port 8080)
    │              └── Static React build (dist/)
    │
    └──> Route: nc-ask-backend
         └──> Service: nc-ask-backend (port 8000)
              └──> Pod: nc-ask-backend-57c6d99c89-k4t9j
                   ├── Gunicorn (4 workers, 300s timeout)
                   ├── FastAPI application
                   ├── sentence-transformers (ML models)
                   └── Resources: 2 CPU cores, 3Gi RAM
                   │
                   └──> External APIs
                        ├──> Supabase (pgvector database)
                        └──> Google Gemini (LLM)
```
---
