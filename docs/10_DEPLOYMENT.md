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

## 📋 Complete Deployment Steps

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

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
oc get pods

# Describe the pod to see events
oc describe pod nc-ask-backend-xxxxx-xxxxx

# Check logs
oc logs nc-ask-backend-xxxxx-xxxxx

# Common fixes:
# - ImagePullBackOff: Check if build completed successfully
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

- [ ] OpenShift CLI installed
- [ ] Logged into OpenShift cluster
- [ ] Created `nc-ask` project
- [ ] Created secrets with Supabase and Gemini credentials
- [ ] Applied ConfigMap
- [ ] Applied BuildConfig and started builds
- [ ] Builds completed successfully
- [ ] Applied Deployments
- [ ] All pods are Running
- [ ] Applied Routes
- [ ] Updated CORS configuration
- [ ] Rebuilt frontend with backend URL
- [ ] Tested backend health endpoint
- [ ] Tested frontend in browser
- [ ] Verified application works end-to-end