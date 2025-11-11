# NC-ASK OpenShift Deployment Walkthrough

This is a complete, step-by-step guide to deploy NC-ASK to OpenShift from the ground up.

## Prerequisites

Before you begin, ensure you have:

1. **Access to an OpenShift cluster (Using Red Hat’s OpenShift Sandbox)**
   - Go to https://developers.redhat.com/developer-sandbox
   - Click Start your Sandbox for free
   - After provisioning (takes ~5–10 minutes), you’ll get:
      - Cluster Console URL (e.g., https://console-openshift-console.apps.sandbox.xxxx.openshift.com)
      - Login command
   - In the web console (top right corner → your name → Copy login command):
      - Click “Display Token”
      - Copy the oc login command (it will look like): oc login https://api.sandbox.xxxx.openshift.com:6443 --token=sha256~xxxxxxxxxxxxxxxxxx
   - Run that command in your terminal to connect your local CLI (oc) to the cluster.

2. **Required credentials ready** (write these down):
   - [ ] Supabase Project URL
   - [ ] Supabase Anon Key
   - [ ] Supabase Service Role Key
   - [ ] Google Gemini API Key

---

## Complete Deployment Steps

### Step 1: Install OpenShift CLI (if not already installed)

**On macOS:**
```bash
brew install openshift-cli
```

**On Linux:**
```bash
# Download the latest oc CLI
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz

# Extract and install
tar -xvf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/
sudo chmod +x /usr/local/bin/oc
```

**Verify:**
```bash
oc version --client
```

---

### Step 2: Get Your OpenShift Login Credentials

1. Open your OpenShift web console in a browser
2. Click your username in the top right corner
3. Click **"Copy login command"**
4. Click **"Display Token"**
5. Copy the full `oc login` command that looks like:
   ```bash
   oc login --token=sha256~xxxxx --server=https://api.your-cluster.com:6443
   ```

---

### Step 3: Login to OpenShift

```bash
# Paste the login command you copied from the web console
oc login --token=sha256~xxxxx --server=https://api.your-cluster.com:6443

# Verify you're logged in
oc whoami
# Should show your username

oc whoami --show-server
# Should show your cluster URL
```

**Expected output:**
```
Logged into "https://api.your-cluster.com:6443" as "your-username" using the token provided.
```

---

### Step 4: Create a New Project (Namespace)

```bash
# Create the nc-ask project
oc new-project nc-ask \
  --description="NC Autism Support & Knowledge Platform" \
  --display-name="NC-ASK"

# Verify you're in the project
oc project
# Should show: Using project "nc-ask"

# Check project status
oc status
```

**What this does:**
- Creates an isolated namespace called `nc-ask` for all your resources
- Automatically switches to this project

---

### Step 5: Prepare Your Credentials

Now you'll create the secrets. You need:

1. **Supabase URL** - Get from https://app.supabase.com/project/YOUR_PROJECT/settings/api
   - Format: `https://xxxxxxxxxxxxx.supabase.co`

2. **Supabase Anon Key** - Get from the same page
   - Starts with `eyJ...`

3. **Supabase Service Role Key** - Get from the same page
   - Starts with `eyJ...` (different from anon key)

4. **Google Gemini API Key** - Get from https://makersuite.google.com/app/apikey
   - Starts with `AIza...`

5. **Secret Key** - Generate a random string:
   ```bash
   openssl rand -hex 32
   ```

---

### Step 6: Create the Kubernetes Secret

**IMPORTANT:** Replace the placeholder values with your actual credentials!

```bash
# Create the secret with your actual values
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='https://your-project-id.supabase.co' \
  --from-literal=SUPABASE_ANON_KEY='eyJhbGciOi...' \
  --from-literal=GOOGLE_API_KEY='AIzaSyD...' \
  --from-literal=SECRET_KEY='your-random-32-char-hex-string'

# Verify the secret was created
oc get secret nc-ask-secrets

# Check secret details (won't show values)
oc describe secret nc-ask-secrets
```

**Expected output:**
```
secret/nc-ask-secrets created

NAME              TYPE     DATA   AGE
nc-ask-secrets    Opaque   5      5s
```

**Security Note:** Never commit these credentials to Git!

---

### Step 7: Apply the ConfigMap

```bash
# Apply the ConfigMap from the openshift directory
oc apply -f openshift/configmap.yaml

# Verify
oc get configmap nc-ask-config
oc describe configmap nc-ask-config
```

**What this does:**
- Creates non-sensitive configuration like rate limits, model names, etc.
- These can be changed later without recreating secrets

---

### Step 8: Apply BuildConfig and ImageStreams

```bash
# Apply the BuildConfig
oc apply -f openshift/buildconfig.yaml

# Verify BuildConfigs were created
oc get buildconfig
# Should show: nc-ask-backend and nc-ask-frontend

# Verify ImageStreams were created
oc get imagestream
# Should show: backend and frontend
```

**What this does:**
- Creates build configurations that will build Docker images from your Git repo
- Creates ImageStreams to store the built images

---

### Step 9: Start the Builds

This will clone your Git repository and build the Docker images.

**IMPORTANT:** Complete builds BEFORE applying deployments in Step 10!

```bash
# Start backend build
oc start-build nc-ask-backend

# Start frontend build (in a separate terminal or wait for backend)
oc start-build nc-ask-frontend

# Watch the builds in real-time
oc get builds -w
# Press Ctrl+C to stop watching
```

**Follow build logs:**
```bash
# Backend build logs
oc logs -f bc/nc-ask-backend

# Frontend build logs (in another terminal)
oc logs -f bc/nc-ask-frontend
```

**Build time:** This will take 5-10 minutes for each build.

**Expected output:**
```
build.build.openshift.io/nc-ask-backend-1 created
build.build.openshift.io/nc-ask-frontend-1 created
```

**Wait for builds to complete:**
```bash
# Check build status
oc get builds

# Look for STATUS: Complete
NAME                  TYPE     FROM          STATUS     STARTED          DURATION
nc-ask-backend-1      Docker   Git@main      Complete   5 minutes ago    4m30s
nc-ask-frontend-1     Docker   Git@main      Complete   3 minutes ago    3m15s
```

**If a build fails:**
```bash
# Check the build logs
oc logs build/nc-ask-backend-1

# Common issues:
# - Git repository not accessible: Check if your repo is public
# - Dockerfile errors: Check backend/Dockerfile.prod
# - Build timeout: Increase timeout in BuildConfig
```

---

### Step 10: Apply Deployments

Once builds are complete, deploy the applications:

```bash
# Apply backend deployment
oc apply -f openshift/backend-deployment.yaml

# Apply frontend deployment
oc apply -f openshift/frontend-deployment.yaml

# Watch pods starting
oc get pods -w
# Press Ctrl+C when all pods are Running
```

**Expected output:**
```
deployment.apps/nc-ask-backend created
service/nc-ask-backend created
deployment.apps/nc-ask-frontend created
service/nc-ask-frontend created
```

**Wait for pods to be Running:**
```bash
# Check pod status
oc get pods

# Should show something like:
NAME                                READY   STATUS    RESTARTS   AGE
nc-ask-backend-xxxxx-xxxxx         1/1     Running   0          2m
nc-ask-backend-xxxxx-xxxxx         1/1     Running   0          2m
nc-ask-frontend-xxxxx-xxxxx        1/1     Running   0          2m
nc-ask-frontend-xxxxx-xxxxx        1/1     Running   0          2m
```

**If pods are not starting:**
```bash
# Check pod events
oc describe pod nc-ask-backend-xxxxx-xxxxx

# Check pod logs
oc logs nc-ask-backend-xxxxx-xxxxx

# Common issues:
# - ImagePullBackOff: Build might have failed, check builds
# - CrashLoopBackOff: Check logs for errors
# - Pending: Check resource limits
```

---

### Step 11: Create Routes (External Access)

```bash
# Apply routes
oc apply -f openshift/route.yaml

# Get the URLs
oc get routes

# Or get URLs individually
echo "Frontend: https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')"
echo "Backend: https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')"
```

**Expected output:**
```
route.route.openshift.io/nc-ask-frontend created
route.route.openshift.io/nc-ask-backend created

NAME               HOST/PORT                                          PATH   SERVICES           PORT   TERMINATION   WILDCARD
nc-ask-frontend    nc-ask-frontend-nc-ask.apps.your-cluster.com             nc-ask-frontend    http   edge          None
nc-ask-backend     nc-ask-backend-nc-ask.apps.your-cluster.com              nc-ask-backend     http   edge          None
```

**Save these URLs!** You'll need them in the next steps.

---

### Step 12: Update CORS Configuration

The backend needs to know which frontend URL to allow for CORS:

```bash
# Get frontend URL
FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')

# Show what we're setting
echo "Setting CORS to allow: https://$FRONTEND_URL"

# Update ConfigMap with the frontend URL
oc patch configmap nc-ask-config -p '{"data":{"ALLOWED_ORIGINS":"https://'$FRONTEND_URL'"}}'

# Restart backend to pick up the new CORS setting
oc rollout restart deployment/nc-ask-backend

# Wait for rollout to complete
oc rollout status deployment/nc-ask-backend
```

**Expected output:**
```
configmap/nc-ask-config patched
deployment.apps/nc-ask-backend restarted
Waiting for deployment "nc-ask-backend" rollout to finish: 1 old replicas are pending termination...
deployment "nc-ask-backend" successfully rolled out
```

---

### Step 13: Rebuild Frontend with Backend URL

The frontend needs to be rebuilt with the correct backend API URL:

```bash
# Get backend URL
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')

# Show what we're setting
echo "Setting frontend API URL to: https://$BACKEND_URL"

# Update the BuildConfig
oc patch bc/nc-ask-frontend -p '{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"VITE_API_BASE_URL","value":"https://'$BACKEND_URL'"}]}}}}'

# Trigger a new build
oc start-build nc-ask-frontend --follow

# This will take 3-5 minutes
# Wait for "Push successful" message
```

**Expected output:**
```
buildconfig.build.openshift.io/nc-ask-frontend patched
build.build.openshift.io/nc-ask-frontend-2 created

...build output...

Pushing image ...
Push successful
```

**After build completes:**
```bash
# The new frontend pods will automatically deploy
# Watch the rollout
oc rollout status deployment/nc-ask-frontend
```

---

### Step 14: Test the Deployment

Now everything should be working! Let's test:

```bash
# Get your URLs
FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')

echo "Frontend: https://$FRONTEND_URL"
echo "Backend: https://$BACKEND_URL"

# Test backend health endpoint
curl https://$BACKEND_URL/api/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00Z"}
```

**In your browser:**
1. Open `https://your-frontend-url.apps.your-cluster.com`
2. You should see the NC-ASK interface
3. Try a test query like "What is autism?"
4. You should get a response with citations

---

### Step 15: Verify Everything is Working

```bash
# Check all pods are running
oc get pods

# All should show 1/1 READY and Running STATUS

# Check all services
oc get svc

# Check routes
oc get routes

# View recent logs
oc logs deployment/nc-ask-backend --tail=50
oc logs deployment/nc-ask-frontend --tail=50

# Check for any errors
oc get events --sort-by='.lastTimestamp' | grep -i error
```

---

## Deployment Complete!

Your NC-ASK application is now deployed on OpenShift!

**Your URLs:**
- Frontend: `https://nc-ask-frontend-nc-ask.apps.your-cluster.com`
- Backend API: `https://nc-ask-backend-nc-ask.apps.your-cluster.com`

---

## What Was Deployed?

```
OpenShift Cluster (nc-ask project)
│
├── Builds
│   ├── nc-ask-backend (BuildConfig + ImageStream)
│   └── nc-ask-frontend (BuildConfig + ImageStream)
│
├── Deployments
│   ├── nc-ask-backend (2 replicas)
│   │   ├── Pod 1 (FastAPI + Gunicorn)
│   │   └── Pod 2 (FastAPI + Gunicorn)
│   └── nc-ask-frontend (2 replicas)
│       ├── Pod 1 (React + nginx)
│       └── Pod 2 (React + nginx)
│
├── Services
│   ├── nc-ask-backend (port 8000)
│   └── nc-ask-frontend (port 80)
│
├── Routes (HTTPS)
│   ├── nc-ask-backend
│   └── nc-ask-frontend
│
├── Configuration
│   ├── nc-ask-config (ConfigMap)
│   └── nc-ask-secrets (Secret)
│
└── External Services
    ├── Supabase (vector database)
    └── Google Gemini (LLM)
```

---

## Common Operations

### View Logs
```bash
# Backend logs
oc logs -f deployment/nc-ask-backend

# Frontend logs
oc logs -f deployment/nc-ask-frontend
```

### Restart a Service
```bash
# Restart backend
oc rollout restart deployment/nc-ask-backend

# Restart frontend
oc rollout restart deployment/nc-ask-frontend
```

### Scale Replicas
```bash
# Scale backend to 3 replicas
oc scale deployment/nc-ask-backend --replicas=3

# Scale frontend to 3 replicas
oc scale deployment/nc-ask-frontend --replicas=3
```

### Update Application Code
```bash
# If you pushed code to your Git repo
oc start-build nc-ask-backend
oc start-build nc-ask-frontend

# Or from local directory
oc start-build nc-ask-backend --from-dir=. --follow
```

### Update Configuration
```bash
# Edit ConfigMap
oc edit configmap nc-ask-config

# After editing, restart deployments
oc rollout restart deployment/nc-ask-backend
```

### Update Secrets
```bash
# Delete and recreate
oc delete secret nc-ask-secrets
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='...' \
  --from-literal=SUPABASE_ANON_KEY='...' \
  # ... other secrets

# Restart deployment to use new secrets
oc rollout restart deployment/nc-ask-backend
```

---

## Critical Pre-Deployment Checks

Before deploying to OpenShift, verify these essential configurations to avoid common deployment failures:

### 1. Dockerfile Configuration Checklist

**✅ Verify `backend/Dockerfile.prod` has correct settings:**

```bash
# Check these critical lines in your Dockerfile:
grep -A 3 "pip install" backend/Dockerfile.prod
# Should show: pip install --prefix=/install (NOT --user)

grep -A 2 "COPY --from=builder" backend/Dockerfile.prod
# Should show: COPY --from=builder /install /usr/local (NOT /root/.local)

grep "timeout" backend/Dockerfile.prod
# Should show: "--timeout", "300" in gunicorn command

grep "HEALTHCHECK" backend/Dockerfile.prod
# Should show: curl -f http://localhost:8000/health (NOT /api/health)
# Should show: --start-period=180s (allows 3 minutes for startup)
```

**Required Dockerfile patterns:**
```dockerfile
# Stage 1: Builder
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
COPY --from=builder /install /usr/local

# Healthcheck with correct path and startup time
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=180s \
    CMD curl -f http://localhost:8000/health || exit 1

# Gunicorn with 5-minute timeout for ML model loading
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
```

### 2. Environment Variables Checklist

**✅ Verify secrets exist with all required keys:**

```bash
# Check secret exists
oc get secret nc-ask-secrets

# Verify all 4 keys are present
oc get secret nc-ask-secrets -o jsonpath='{.data}' | jq 'keys'
# Must show: ["GOOGLE_API_KEY", "SECRET_KEY", "SUPABASE_ANON_KEY", "SUPABASE_URL"]
```

**✅ Verify deployment is configured to use secrets:**

```bash
# Check deployment environment variables
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].env[*].name}'
# Must include: SUPABASE_URL SUPABASE_ANON_KEY GOOGLE_API_KEY SECRET_KEY

# If missing, configure:
oc set env deployment/nc-ask-backend --from=secret/nc-ask-secrets
```

### 3. Health Probe Configuration Checklist

**✅ Verify health probes use correct path and timing:**

```bash
# Check readiness probe
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' | jq

# Must have:
# - path: /health (NOT /api/health)
# - initialDelaySeconds: 180 or higher
# - timeoutSeconds: 5 or higher
```

**✅ Set correct probes if needed:**

```bash
# Readiness probe (allows 3 minutes for startup)
oc set probe deployment/nc-ask-backend --readiness \
  --get-url=http://:8000/health \
  --initial-delay-seconds=180 \
  --period-seconds=10 \
  --timeout-seconds=5 \
  --failure-threshold=3

# Liveness probe (or remove during initial setup)
oc set probe deployment/nc-ask-backend --liveness \
  --get-url=http://:8000/health \
  --initial-delay-seconds=180 \
  --period-seconds=30 \
  --timeout-seconds=10 \
  --failure-threshold=3
```

### 4. BuildConfig Branch Verification

**✅ Ensure BuildConfig uses correct git branch:**

```bash
# Check current branch in BuildConfig
oc get bc nc-ask-backend -o jsonpath='{.spec.source.git.ref}'

# Check your local branch
git branch --show-current

# If different, update BuildConfig:
oc patch bc/nc-ask-backend -p '{"spec":{"source":{"git":{"ref":"your-branch-name"}}}}'
```

### 5. Image Path Verification

**✅ Verify deployment uses correct namespace:**

```bash
# Get your namespace
NAMESPACE=$(oc project -q)
echo "Your namespace: $NAMESPACE"

# Check deployment image path
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].image}'
# Should contain: image-registry.openshift-image-registry.svc:5000/$NAMESPACE/backend

# If wrong, update:
oc set image deployment/nc-ask-backend backend=image-registry.openshift-image-registry.svc:5000/$NAMESPACE/backend:latest
```

### 6. Resource Limits Verification (CRITICAL FOR ML WORKLOADS)

**✅ Ensure sufficient CPU and memory for ML model loading:**

```bash
# Check current resource limits
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].resources}' | jq

# REQUIRED minimums for 4 workers:
# - CPU limit: 2000m (2 cores)
# - Memory limit: 3Gi
# - CPU request: 1000m
# - Memory request: 2Gi

# If limits are too low, update:
oc set resources deployment/nc-ask-backend \
  --limits=cpu=2000m,memory=3Gi \
  --requests=cpu=1000m,memory=2Gi
```

**Why this is critical:**
- NC-ASK uses sentence-transformers ML models
- 4 gunicorn workers each load models on startup
- Insufficient resources cause workers to hang indefinitely
- Symptoms: Pod `Running` but never `Ready`, health checks timeout

**Resource requirements:**
- **Minimum:** CPU=1000m, Memory=1.5Gi (1 worker only, testing)
- **Production:** CPU=2000m, Memory=3Gi (4 workers, recommended)
- **High traffic:** CPU=4000m, Memory=4Gi (8 workers)

---

## Troubleshooting

### Quick Reference: Common Issues

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| **Pod maxed at CPU/memory limits, workers hang** | **Resource limits too low for ML workload (MOST COMMON)** | **Set limits: CPU=2000m, Memory=3Gi** `oc set resources deployment/nc-ask-backend --limits=cpu=2000m,memory=3Gi --requests=cpu=1000m,memory=2Gi` |
| `ImagePullBackOff` with "authentication required" | Wrong namespace in image path | Update deployment: `oc set image deployment/nc-ask-backend backend=image-registry.openshift-image-registry.svc:5000/<YOUR_NAMESPACE>/backend:latest` |
| `CreateContainerError` with "executable file not found" | Docker image built with wrong package paths | Check Dockerfile uses `pip install --prefix=/install` and copies to `/usr/local` (not `/root/.local`) |
| `CrashLoopBackOff` after workers boot | Gunicorn worker timeout (30s default) too short for ML model loading | Add `--timeout 300` to gunicorn command in Dockerfile |
| Workers boot but app never starts | Missing environment variables | Configure secrets: `oc set env deployment/nc-ask-backend --from=secret/nc-ask-secrets` |
| Health check failures | Wrong health check path or insufficient startup time | Health endpoint is `/health` (not `/api/health`), set readiness initialDelaySeconds to 180s+ |
| Build takes 10-25 minutes | sentence-transformers downloads 80MB+ ML models (normal) | Wait for "Push successful" message, do not interrupt |
| BuildConfig using wrong branch | BuildConfig pointing to wrong git branch | Update: `oc patch bc/nc-ask-backend -p '{"spec":{"source":{"git":{"ref":"your-branch"}}}}'` |
| Pods stuck in `Pending` | Resource limits or quotas | Check: `oc describe pod <pod-name>` |

### Deployment Fails with "ProgressDeadlineExceeded"

**Symptom:** Pods fail to start and deployment times out
**Common Causes:**
1. Image pull authentication errors
2. Container startup failures
3. Health check failures

**Solution:**
```bash
# Check what's happening
oc get pods
oc describe pod <pod-name>
oc get events --sort-by='.lastTimestamp' | tail -20
```

### Image Pull Errors: "authentication required"

**Symptom:** Pods show `ImagePullBackOff` or `ErrImagePull` with authentication errors

**Root Cause:** The deployment is trying to pull from the wrong namespace or image doesn't exist

**Solution:**
```bash
# 1. Check which namespace you're in
oc project

# 2. Check if the image exists in your namespace
oc get imagestream

# 3. Verify the deployment is using the correct image path
# The image path should match your current namespace
oc get deployment nc-ask-backend -o yaml | grep image:

# 4. Update deployment to use correct namespace image
# Replace <YOUR_NAMESPACE> with your actual namespace (e.g., from `oc project`)
oc set image deployment/nc-ask-backend backend=image-registry.openshift-image-registry.svc:5000/<YOUR_NAMESPACE>/backend:latest

# 5. Verify the fix
oc rollout status deployment/nc-ask-backend
```

### Container Crashes: "executable file not found in $PATH"

**Symptom:** Pods show `CreateContainerError` with message like `exec: "gunicorn": executable file not found`

**Root Cause:** The Docker image was built without required dependencies

**Solution:**
```bash
# 1. Trigger a fresh build to rebuild the image with all dependencies
oc start-build nc-ask-backend --follow

# 2. Wait for build to complete (5-10 minutes)
# Watch for "Push successful" message

# 3. Verify build succeeded
oc get builds

# 4. Once build completes, pods should automatically restart with new image
oc get pods -w
```

**Prevention:** Ensure `requirements.txt` includes all runtime dependencies (gunicorn, uvicorn, etc.)

### CrashLoopBackOff: Workers Timeout During Startup

**Symptom:** Pods show `CrashLoopBackOff`, logs show gunicorn workers boot but FastAPI app never starts

**Root Cause:** The default gunicorn worker timeout (30 seconds) is too short for loading ML models like sentence-transformers (~80MB download on first startup)

**Diagnosis:**
```bash
# Check pod logs - you'll see workers boot but then container restarts
oc logs <pod-name> --tail=50

# Expected pattern indicating this issue:
# [INFO] Starting gunicorn
# [INFO] Booting worker with pid: 7
# [INFO] Booting worker with pid: 8
# ... (then container restarts with no error message)
```

**Solution:**

1. **Update Dockerfile to increase gunicorn timeout:**
   ```dockerfile
   CMD ["gunicorn", "main:app", \
        "--workers", "4", \
        "--worker-class", "uvicorn.workers.UvicornWorker", \
        "--bind", "0.0.0.0:8000", \
        "--timeout", "300", \
        "--access-logfile", "-", \
        "--error-logfile", "-", \
        "--log-level", "info"]
   ```

2. **Rebuild and redeploy:**
   ```bash
   # Commit Dockerfile changes
   git add backend/Dockerfile.prod
   git commit -m "fix: increase gunicorn timeout for ML model loading"
   git push

   # Trigger new build
   oc start-build nc-ask-backend --follow

   # Wait for build to complete (20-25 minutes)
   # Deploy new image
   oc rollout restart deployment/nc-ask-backend
   ```

**Why this happens:** On first startup, sentence-transformers needs to download the all-MiniLM-L6-v2 model from HuggingFace. This can take 60-120 seconds depending on network speed. The default 30s timeout kills workers before they finish loading.

### Missing Environment Variables

**Symptom:** Workers boot but app never loads, no error messages in logs

**Root Cause:** Required environment variables (SUPABASE_URL, SUPABASE_ANON_KEY, GOOGLE_API_KEY, SECRET_KEY) not configured

**Diagnosis:**
```bash
# Check if environment variables are configured
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].env[*].name}'

# Should show: SUPABASE_URL SUPABASE_ANON_KEY GOOGLE_API_KEY SECRET_KEY ENVIRONMENT
# If missing, need to add them
```

**Solution:**
```bash
# 1. Verify secret exists and has required keys
oc get secret nc-ask-secrets -o jsonpath='{.data}' | jq 'keys'
# Should show: ["GOOGLE_API_KEY", "SECRET_KEY", "SUPABASE_ANON_KEY", "SUPABASE_URL"]

# 2. Configure deployment to use secret as environment variables
oc set env deployment/nc-ask-backend --from=secret/nc-ask-secrets

# 3. Pods will automatically restart with new environment variables
oc get pods -w
```

### Health Check Failures

**Symptom:** Pods stuck in not-ready state, health checks timing out or returning 404

**Common Causes:**
1. Wrong health check path (using `/api/health` when app has `/health`)
2. Insufficient startup time for ML model loading
3. Health check timeout too short

**Diagnosis:**
```bash
# Check current health check configuration
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' | jq

# Check what path the app actually exposes
oc exec deployment/nc-ask-backend -- curl -s http://localhost:8000/health
# vs
oc exec deployment/nc-ask-backend -- curl -s http://localhost:8000/api/health
```

**Solution:**

1. **Verify the correct health endpoint path** (check `backend/main.py` - NC-ASK uses `/health` at root level, not `/api/health`)

2. **Update readiness probe with correct path and timing:**
   ```bash
   # Set readiness probe to /health with 3-minute initial delay
   oc set probe deployment/nc-ask-backend --readiness \
     --get-url=http://:8000/health \
     --initial-delay-seconds=180 \
     --period-seconds=10 \
     --timeout-seconds=5 \
     --failure-threshold=3
   ```

3. **Remove liveness probe temporarily during initial setup** (prevents premature restarts):
   ```bash
   oc set probe deployment/nc-ask-backend --liveness --remove
   ```

4. **After confirming app starts successfully, re-add liveness probe:**
   ```bash
   oc set probe deployment/nc-ask-backend --liveness \
     --get-url=http://:8000/health \
     --initial-delay-seconds=180 \
     --period-seconds=30 \
     --timeout-seconds=10 \
     --failure-threshold=3
   ```

**Also update Dockerfile healthcheck:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=180s \
    CMD curl -f http://localhost:8000/health || exit 1
```

### BuildConfig Using Wrong Branch

**Symptom:** New builds don't include your latest code changes, even after pushing to git

**Root Cause:** OpenShift BuildConfig is pulling from a different git branch than your code

**Diagnosis:**
```bash
# Check which branch BuildConfig is using
oc get bc nc-ask-backend -o jsonpath='{.spec.source.git.ref}'
# Shows: main (or other branch name)

# Check which branch your code is on
git branch --show-current
# Shows: openshift-deployment (or other branch name)

# If these don't match, BuildConfig won't use your changes
```

**Solution:**
```bash
# Update BuildConfig to use your branch
oc patch bc/nc-ask-backend -p '{"spec":{"source":{"git":{"ref":"openshift-deployment"}}}}'

# Verify the update
oc get bc nc-ask-backend -o jsonpath='{.spec.source.git.ref}'

# Trigger new build with correct branch
oc start-build nc-ask-backend --follow

# Check build used correct commit
oc get build nc-ask-backend-<build-number> -o jsonpath='{.spec.revision.git.commit}'
```

### CRITICAL: Insufficient Resource Limits (CPU/Memory)

**Symptom:** Pod is `Running` but never becomes `Ready`. Workers boot but app never starts. Health checks timeout. Pod shows high CPU/memory usage near limits.

**This is the #1 cause of deployment failures for ML applications.**

**Root Cause:** The NC-ASK backend loads ML models (sentence-transformers) which requires significant CPU and memory. With 4 gunicorn workers, each loading models simultaneously on startup, insufficient resources cause:
- Workers to hang indefinitely while loading models
- CPU throttling preventing models from loading
- Memory pressure causing OOM or extreme slowness

**Diagnosis:**

```bash
# 1. Check current resource usage
oc adm top pod -l component=backend

# Look for CPU/memory at or near limits:
# NAME                       CPU(cores)   MEMORY(bytes)
# nc-ask-backend-xxx-xxx     501m         1023Mi     # BAD: maxed out at 500m/1Gi limits

# 2. Check configured limits
oc get deployment nc-ask-backend -o jsonpath='{.spec.template.spec.containers[0].resources}' | jq

# 3. Check if workers are hanging
oc logs deployment/nc-ask-backend --tail=50
# If you see workers boot but no "Application startup complete", it's resource starvation
```

**Solution:**

Set resource limits appropriate for ML workload:

```bash
# Set CPU to 2 cores and memory to 3GB (minimum for 4 workers + ML models)
oc set resources deployment/nc-ask-backend \
  --limits=cpu=2000m,memory=3Gi \
  --requests=cpu=1000m,memory=2Gi

# Wait for new pod to be created
oc get pods -w

# Verify new pod has higher limits
oc describe pod <new-pod-name> | grep -A 5 "Limits:"
```

**Expected behavior after fix:**
- Pod becomes `Ready` within 3-4 minutes
- Logs show "Application startup complete" for all 4 workers
- Health checks return HTTP 200
- CPU usage: 200-800m (well below 2000m limit)
- Memory usage: 1.5-2.5Gi (well below 3Gi limit)

**Resource Requirements for NC-ASK:**

| Configuration | CPU Limit | Memory Limit | Notes |
|--------------|-----------|--------------|-------|
| **Minimum (1 worker)** | 1000m (1 core) | 1.5Gi | For testing only |
| **Recommended (4 workers)** | 2000m (2 cores) | 3Gi | Production default |
| **High traffic** | 4000m (4 cores) | 4Gi | Scale up workers to 8 |

**Why these limits?**
- Each worker loads sentence-transformers model (~200-300MB RAM)
- Model loading uses significant CPU (encoding operations)
- 4 workers loading simultaneously = 4x resource spike on startup
- After startup, steady-state usage is much lower

**Alternative: Reduce worker count** (if resource limits are strict):

```dockerfile
# In Dockerfile.prod, reduce from 4 to 2 workers:
CMD ["gunicorn", "main:app", \
     "--workers", "2", \
     ...
```

Then rebuild and redeploy. 2 workers require: CPU=1000m, Memory=2Gi

### Docker Multi-Stage Build Permission Issues

**Symptom:** `CreateContainerError` with "executable file not found in $PATH" for commands installed via pip (gunicorn, uvicorn, etc.)

**Root Cause:** In multi-stage Dockerfile, Python packages installed to `/root/.local` in builder stage, but runtime container runs as non-root user (`appuser`) who can't access `/root/.local`

**Diagnosis:**
```bash
# Debug by checking where packages are installed
oc debug deployment/nc-ask-backend --image=<your-image> -- ls -la /root/.local/bin
# Error: Permission denied (appuser can't read /root/.local)

oc debug deployment/nc-ask-backend --image=<your-image> -- ls -la /usr/local/bin
# Should see gunicorn, uvicorn, etc. here for correct setup
```

**Solution - Update Dockerfile:**

**WRONG** (packages only accessible to root):
```dockerfile
# Builder stage
RUN pip install --user -r requirements.txt

# Runtime stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
USER appuser  # Can't access /root/.local!
```

**CORRECT** (packages accessible to all users):
```dockerfile
# Builder stage
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Runtime stage
COPY --from=builder /install /usr/local
USER appuser  # Can access /usr/local!
```

After fixing Dockerfile, rebuild:
```bash
git add backend/Dockerfile.prod
git commit -m "fix: install packages to /usr/local for non-root access"
git push
oc start-build nc-ask-backend --follow
```

### Pods Not Starting

```bash
# Check pod status
oc get pods

# Describe the pod to see events
oc describe pod nc-ask-backend-xxxxx-xxxxx

# Check logs
oc logs nc-ask-backend-xxxxx-xxxxx

# Common fixes:
# - ImagePullBackOff: Check namespace and image path (see above)
# - CreateContainerError: Rebuild image with dependencies (see above)
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check resource limits or quotas
```

### Build Failures

```bash
# Check build logs
oc logs build/nc-ask-backend-1

# Retry build
oc start-build nc-ask-backend

# Common issues:
# - Git clone failed: Check if repo is public or add credentials
# - Dockerfile errors: Check Dockerfile syntax
# - Dependency errors: Check requirements.txt or package.json
# - Build timeout: Large ML dependencies may need more time (normal for first build)
```

### Frontend Can't Connect to Backend

```bash
# Verify backend is running
oc get pods -l component=backend

# Check backend route
oc get route nc-ask-backend

# Verify CORS is set correctly
oc get configmap nc-ask-config -o yaml | grep ALLOWED_ORIGINS

# Rebuild frontend with correct backend URL
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
oc patch bc/nc-ask-frontend -p '{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"VITE_API_BASE_URL","value":"https://'$BACKEND_URL'"}]}}}}'
oc start-build nc-ask-frontend --follow
```

### Application Errors

```bash
# Check backend logs for errors
oc logs deployment/nc-ask-backend | grep -i error

# Check if Supabase credentials are correct
oc exec deployment/nc-ask-backend -- env | grep SUPABASE

# Test backend health
curl https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')/api/health

# Check pod events
oc get events --sort-by='.lastTimestamp' | grep -i error
```

---

## Best Practices & Tips

### Verify Image Paths Before Deployment

Before applying deployments, ensure the image paths match your namespace:

```bash
# Get your current namespace
NAMESPACE=$(oc project -q)

# Verify images exist in your namespace
oc get imagestream

# Check deployment YAML uses correct namespace
grep "image:" openshift/backend-deployment.yaml

# Expected format:
# image: image-registry.openshift-image-registry.svc:5000/<YOUR_NAMESPACE>/backend:latest
```

### Wait for Builds to Complete

Don't apply deployments until builds finish successfully:

```bash
# Start builds
oc start-build nc-ask-backend
oc start-build nc-ask-frontend

# Wait for both to complete
oc get builds -w

# Verify STATUS shows "Complete" before proceeding
# Then apply deployments
oc apply -f openshift/backend-deployment.yaml
oc apply -f openshift/frontend-deployment.yaml
```

### Monitor Deployment Progress

After applying deployments, actively monitor for issues:

```bash
# Watch pods starting
oc get pods -w

# In another terminal, watch events
oc get events -w

# Check for errors
oc get events --sort-by='.lastTimestamp' | grep -i "error\|warning"
```

### Handling Long Build Times

The backend build can take 10+ minutes due to ML dependencies (sentence-transformers):

```bash
# Start build in background and monitor
oc start-build nc-ask-backend --follow

# This is NORMAL:
# - Downloading 80MB+ for sentence-transformers
# - Installing PyTorch dependencies
# - Building wheels for various packages

# The build will show "Push successful" when complete
```

---

## Cleanup

If you need to remove the deployment:

```bash
# Delete everything in the project
oc delete all -l app=nc-ask

# Delete ConfigMap and Secrets
oc delete configmap nc-ask-config
oc delete secret nc-ask-secrets

# Or delete the entire project
oc delete project nc-ask
```

---

## Next Steps

1. **Set up monitoring** - Configure alerts for pod health
2. **Set up autoscaling** - Scale based on CPU/memory
3. **Configure backups** - Export configuration regularly
4. **Update regularly** - Keep dependencies updated
5. **Monitor costs** - Track resource usage

For detailed documentation, see:
- **Full deployment guide:** `docs/10_DEPLOYMENT.md`
- **Architecture details:** `docs/06_ARCHITECTURE.md`
- **Local setup:** `docs/04_LOCAL_SETUP.md`

---

## Deployment Checklist

### Pre-Deployment
- [ ] OpenShift CLI installed
- [ ] Logged into OpenShift cluster
- [ ] Created `nc-ask` project
- [ ] Created secrets with Supabase and Gemini credentials (all 4 keys)
- [ ] Applied ConfigMap

### Critical Configuration Checks
- [ ] **Verified Dockerfile uses `pip install --prefix=/install`** (not `--user`)
- [ ] **Verified Dockerfile copies to `/usr/local`** (not `/root/.local`)
- [ ] **Verified Dockerfile has `--timeout 300`** in gunicorn command
- [ ] **Verified Dockerfile healthcheck uses `/health`** (not `/api/health`)
- [ ] **Set resource limits: CPU=2000m, Memory=3Gi** (CRITICAL for ML workload)
- [ ] Configured environment variables from secrets
- [ ] Set health probes: path=`/health`, initialDelaySeconds=180s
- [ ] Verified BuildConfig uses correct git branch

### Build & Deploy
- [ ] Applied BuildConfig and started builds
- [ ] Builds completed successfully (wait for "Push successful")
- [ ] Applied Deployments
- [ ] All pods are Running **AND Ready (1/1)**
- [ ] Pods show "Application startup complete" in logs
- [ ] Health checks returning HTTP 200

### Post-Deployment
- [ ] Applied Routes
- [ ] Updated CORS configuration
- [ ] Rebuilt frontend with backend URL
- [ ] Tested backend health endpoint
- [ ] Tested frontend in browser
- [ ] Verified application works end-to-end

### Common Gotchas (Double-check these!)
- [ ] Resource limits set to at least CPU=2000m, Memory=3Gi
- [ ] Environment variables configured (run: `oc set env deployment/nc-ask-backend --from=secret/nc-ask-secrets`)
- [ ] Health probe path is `/health` not `/api/health`
- [ ] Gunicorn timeout is 300s not default 30s
- [ ] BuildConfig branch matches your code branch