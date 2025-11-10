# OpenShift Deployment Guide for NC-ASK

This guide provides step-by-step instructions for deploying the NC-ASK application on Red Hat OpenShift.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Configuration](#configuration)
- [Accessing the Application](#accessing-the-application)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Updating the Application](#updating-the-application)
- [Cleanup](#cleanup)

## Prerequisites

### Required Tools
- OpenShift CLI (`oc`) installed and configured
- Access to an OpenShift cluster (OpenShift 4.x)
- Git repository with NC-ASK code

### Required Credentials
Before deployment, you'll need:
1. **Supabase credentials**:
   - Project URL
   - Anon key
   - Service role key
2. **Google Gemini API key**
3. **Random secret key** (generate with `openssl rand -hex 32`)

### OpenShift Access
Ensure you're logged into your OpenShift cluster:
```bash
oc login --token=<your-token> --server=https://api.your-cluster.com:6443
```

## Quick Start

For a rapid deployment, run these commands:

```bash
# 1. Create a new project
oc new-project nc-ask

# 2. Create secrets (replace with your actual values)
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='https://your-project.supabase.co' \
  --from-literal=SUPABASE_ANON_KEY='your-anon-key' \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY='your-service-key' \
  --from-literal=GOOGLE_API_KEY='your-gemini-key' \
  --from-literal=SECRET_KEY='your-random-secret'

# 3. Apply all manifests
oc apply -f openshift/configmap.yaml
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/backend-deployment.yaml
oc apply -f openshift/frontend-deployment.yaml
oc apply -f openshift/route.yaml

# 4. Start the builds
oc start-build nc-ask-backend
oc start-build nc-ask-frontend

# 5. Watch the deployment
oc get pods -w
```

## Detailed Deployment Steps

### Step 1: Create OpenShift Project

Create a dedicated namespace for the application:

```bash
oc new-project nc-ask --description="NC Autism Support & Knowledge Platform" \
  --display-name="NC-ASK"
```

Verify the project was created:
```bash
oc project nc-ask
oc status
```

### Step 2: Configure Secrets

**Option A: Using oc create (Recommended)**

```bash
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='https://xxxxxxxxxxxxx.supabase.co' \
  --from-literal=SUPABASE_ANON_KEY='eyJhbGc...' \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY='eyJhbGc...' \
  --from-literal=GOOGLE_API_KEY='AIzaSyD...' \
  --from-literal=SECRET_KEY='your-random-hex-string'
```

**Option B: Using YAML file**

1. Copy the template:
```bash
cp openshift/secrets.yaml.template openshift/secrets.yaml
```

2. Encode your secrets:
```bash
echo -n "https://your-project.supabase.co" | base64
echo -n "your-anon-key" | base64
echo -n "your-service-key" | base64
echo -n "your-gemini-key" | base64
echo -n "$(openssl rand -hex 32)" | base64
```

3. Edit `openshift/secrets.yaml` with the base64 values

4. Apply:
```bash
oc apply -f openshift/secrets.yaml
```

5. **IMPORTANT**: Don't commit `secrets.yaml` to git:
```bash
echo "openshift/secrets.yaml" >> .gitignore
```

Verify the secret was created:
```bash
oc get secret nc-ask-secrets
oc describe secret nc-ask-secrets
```

### Step 3: Apply ConfigMap

The ConfigMap contains non-sensitive configuration:

```bash
oc apply -f openshift/configmap.yaml
```

**Important**: After deployment, update the `ALLOWED_ORIGINS` in the ConfigMap with your actual frontend route URL:

```bash
# Get your frontend route URL
FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')
echo "Frontend URL: https://$FRONTEND_URL"

# Update ConfigMap
oc patch configmap nc-ask-config -p '{"data":{"ALLOWED_ORIGINS":"https://'$FRONTEND_URL'"}}'

# Restart backend to pick up changes
oc rollout restart deployment/nc-ask-backend
```

Verify:
```bash
oc get configmap nc-ask-config
oc describe configmap nc-ask-config
```

### Step 4: Set Up Build Configuration

**Option A: Build from Git Repository (Recommended for Production)**

1. Update `openshift/buildconfig.yaml` with your Git repository URL:
```yaml
git:
  uri: https://github.com/YOUR_ORG/NC-ASK.git
  ref: main  # or your production branch
```

2. Apply the BuildConfig:
```bash
oc apply -f openshift/buildconfig.yaml
```

3. Start the builds:
```bash
oc start-build nc-ask-backend
oc start-build nc-ask-frontend
```

4. Monitor the builds:
```bash
# Follow build logs
oc logs -f bc/nc-ask-backend
oc logs -f bc/nc-ask-frontend

# Check build status
oc get builds
```

**Option B: Build from Local Source (Development/Testing)**

```bash
# Build backend from local directory
oc start-build nc-ask-backend --from-dir=. --follow

# Build frontend from local directory
oc start-build nc-ask-frontend --from-dir=. --follow
```

### Step 5: Deploy the Application

After successful builds, deploy the application:

```bash
# Apply deployment manifests
oc apply -f openshift/backend-deployment.yaml
oc apply -f openshift/frontend-deployment.yaml
```

Monitor the deployment:
```bash
# Watch pods starting up
oc get pods -w

# Check deployment status
oc get deployments

# View deployment events
oc get events --sort-by='.lastTimestamp'
```

Wait for all pods to be in "Running" state:
```bash
oc get pods
# Should show:
# NAME                               READY   STATUS    RESTARTS   AGE
# nc-ask-backend-xxxxx-xxxxx        1/1     Running   0          2m
# nc-ask-backend-xxxxx-xxxxx        1/1     Running   0          2m
# nc-ask-frontend-xxxxx-xxxxx       1/1     Running   0          2m
# nc-ask-frontend-xxxxx-xxxxx       1/1     Running   0          2m
```

### Step 6: Create Routes for External Access

```bash
oc apply -f openshift/route.yaml
```

Get the route URLs:
```bash
# Frontend URL (main application)
oc get route nc-ask-frontend -o jsonpath='{.spec.host}'

# Backend API URL
oc get route nc-ask-backend -o jsonpath='{.spec.host}'
```

### Step 7: Update Backend Route in Frontend Build

If you need to rebuild the frontend with the correct backend URL:

```bash
# Get backend URL
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')

# Update BuildConfig with backend URL
oc patch bc/nc-ask-frontend -p '{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"VITE_API_BASE_URL","value":"https://'$BACKEND_URL'"}]}}}}'

# Rebuild frontend
oc start-build nc-ask-frontend --follow
```

## Configuration

### Environment Variables

All environment variables are managed through ConfigMaps and Secrets:

**Secrets** (sensitive data in `nc-ask-secrets`):
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_API_KEY`
- `SECRET_KEY`

**ConfigMap** (non-sensitive in `nc-ask-config`):
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 10)
- `MAX_QUERY_LENGTH`: Max query character limit (default: 500)
- `EMBEDDING_MODEL`: Sentence transformer model
- `LLM_MODEL`: Gemini model version
- `ALLOWED_ORIGINS`: CORS allowed origins

### Modifying Configuration

Update ConfigMap:
```bash
oc edit configmap nc-ask-config
```

Update Secrets:
```bash
oc edit secret nc-ask-secrets
```

After changes, restart deployments:
```bash
oc rollout restart deployment/nc-ask-backend
oc rollout restart deployment/nc-ask-frontend
```

### Scaling

Scale the application horizontally:

```bash
# Scale backend
oc scale deployment/nc-ask-backend --replicas=3

# Scale frontend
oc scale deployment/nc-ask-frontend --replicas=3

# Verify
oc get pods -l app=nc-ask
```

Enable autoscaling:
```bash
# Autoscale backend based on CPU
oc autoscale deployment/nc-ask-backend --min=2 --max=5 --cpu-percent=75

# Autoscale frontend
oc autoscale deployment/nc-ask-frontend --min=2 --max=5 --cpu-percent=75

# Check HPA status
oc get hpa
```

## Accessing the Application

### Get Application URLs

```bash
# Frontend (main application)
echo "https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')"

# Backend API
echo "https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')"
```

### Test the Deployment

```bash
# Test backend health
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
curl https://$BACKEND_URL/api/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00Z"}
```

Visit the frontend URL in your browser to access the application.

## Monitoring and Troubleshooting

### View Logs

```bash
# Backend logs
oc logs -f deployment/nc-ask-backend

# Frontend logs
oc logs -f deployment/nc-ask-frontend

# Logs from specific pod
oc logs nc-ask-backend-xxxxx-xxxxx

# Previous logs (if pod restarted)
oc logs nc-ask-backend-xxxxx-xxxxx --previous
```

### Check Pod Status

```bash
# List all pods
oc get pods -l app=nc-ask

# Detailed pod info
oc describe pod nc-ask-backend-xxxxx-xxxxx

# Pod events
oc get events --sort-by='.lastTimestamp' | grep nc-ask
```

### Common Issues

#### Pods Not Starting

```bash
# Check pod events
oc describe pod <pod-name>

# Common causes:
# - Image pull errors: Check BuildConfig and ImageStream
# - Resource limits: Check pod resource requests/limits
# - Secret/ConfigMap missing: Verify they exist
```

#### Backend Health Check Failing

```bash
# Check backend logs
oc logs deployment/nc-ask-backend | tail -50

# Common causes:
# - Missing environment variables (check secrets)
# - Supabase connection issues
# - Port misconfiguration
```

#### Frontend Can't Connect to Backend

```bash
# Verify backend route exists
oc get route nc-ask-backend

# Check CORS configuration
oc get configmap nc-ask-config -o yaml | grep ALLOWED_ORIGINS

# Rebuild frontend with correct backend URL
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
oc start-build nc-ask-frontend --follow --build-arg=VITE_API_BASE_URL=https://$BACKEND_URL
```

#### Image Pull Errors

```bash
# Check ImageStreams
oc get imagestreams

# Verify builds completed successfully
oc get builds

# Check build logs if build failed
oc logs -f build/nc-ask-backend-1
```

### Debugging

Execute commands inside pods:

```bash
# Get a shell in backend pod
oc rsh deployment/nc-ask-backend

# Run Python in backend pod
oc exec deployment/nc-ask-backend -- python -c "import sys; print(sys.version)"

# Check environment variables
oc exec deployment/nc-ask-backend -- env | grep -E 'SUPABASE|GOOGLE'
```

## Updating the Application

### Update from Git Repository

If using Git-based builds:

```bash
# Trigger new build
oc start-build nc-ask-backend --follow
oc start-build nc-ask-frontend --follow

# Deployments will automatically update when builds complete
```

### Update from Local Changes

```bash
# Build and deploy backend
oc start-build nc-ask-backend --from-dir=. --follow

# Build and deploy frontend
oc start-build nc-ask-frontend --from-dir=. --follow
```

### Rolling Updates

OpenShift performs rolling updates by default. Monitor the rollout:

```bash
# Watch rollout status
oc rollout status deployment/nc-ask-backend
oc rollout status deployment/nc-ask-frontend

# View rollout history
oc rollout history deployment/nc-ask-backend

# Rollback if needed
oc rollout undo deployment/nc-ask-backend
```

## Backup and Disaster Recovery

### Export Configuration

Backup your configuration:

```bash
# Export all resources
oc get all,configmap,secret,route -l app=nc-ask -o yaml > nc-ask-backup.yaml

# Export only config (without secrets in plain text)
oc get configmap,secret -l app=nc-ask -o yaml > nc-ask-config-backup.yaml
```

### Restore from Backup

```bash
# Restore configuration
oc apply -f nc-ask-backup.yaml

# Verify
oc get all -l app=nc-ask
```

## Security Best Practices

1. **Never commit secrets to git**
   ```bash
   echo "openshift/secrets.yaml" >> .gitignore
   ```

2. **Use RBAC for access control**
   ```bash
   # Create service account with minimal permissions
   oc create sa nc-ask-sa
   ```

3. **Enable network policies**
   ```bash
   # Restrict traffic to only necessary pods
   oc apply -f openshift/network-policy.yaml
   ```

4. **Regular security updates**
   ```bash
   # Rebuild images regularly to get security patches
   oc start-build nc-ask-backend
   oc start-build nc-ask-frontend
   ```

5. **Monitor security advisories**
   - Keep Python dependencies updated (`requirements.txt`)
   - Update Node.js packages regularly
   - Monitor Supabase and Google API announcements

## Cleanup

### Delete Individual Resources

```bash
# Delete deployments
oc delete deployment nc-ask-backend nc-ask-frontend

# Delete services
oc delete service nc-ask-backend nc-ask-frontend

# Delete routes
oc delete route nc-ask-backend nc-ask-frontend

# Delete builds
oc delete bc nc-ask-backend nc-ask-frontend
oc delete is backend frontend

# Delete configuration
oc delete configmap nc-ask-config
oc delete secret nc-ask-secrets
```

### Delete Entire Project

```bash
# WARNING: This deletes everything in the project
oc delete project nc-ask
```

## Deployment Files Overview

The `openshift/` directory contains all Kubernetes/OpenShift manifest files:

| File | Purpose |
|------|---------|
| `backend-deployment.yaml` | Backend Deployment and Service definitions |
| `frontend-deployment.yaml` | Frontend Deployment and Service definitions |
| `buildconfig.yaml` | BuildConfigs and ImageStreams for building container images |
| `configmap.yaml` | Non-sensitive configuration (RAG settings, rate limits, etc.) |
| `secrets.yaml.template` | Template for creating Kubernetes secrets (DO NOT commit actual secrets!) |
| `route.yaml` | OpenShift Routes for external access (HTTPS) |
| `deploy.sh` | Automated deployment script |

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│            OpenShift Cluster                │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │         nc-ask Namespace              │ │
│  │                                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │   Frontend   │  │   Backend    │  │ │
│  │  │  (nginx)     │  │  (gunicorn)  │  │ │
│  │  │              │  │              │  │ │
│  │  │  2 replicas  │  │  2 replicas  │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  │ │
│  │         │                  │          │ │
│  │  ┌──────▼───────┐  ┌──────▼───────┐  │ │
│  │  │   Service    │  │   Service    │  │ │
│  │  │  port: 80    │  │  port: 8000  │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  │ │
│  │         │                  │          │ │
│  │  ┌──────▼───────┐  ┌──────▼───────┐  │ │
│  │  │    Route     │  │    Route     │  │ │
│  │  │  (HTTPS)     │  │  (HTTPS)     │  │ │
│  │  └──────────────┘  └──────────────┘  │ │
│  │                                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  ConfigMap   │  │   Secrets    │  │ │
│  │  └──────────────┘  └──────────────┘  │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
         │                      │
         ▼                      ▼
   ┌──────────┐          ┌───────────┐
   │ Supabase │          │  Gemini   │
   │   API    │          │    API    │
   └──────────┘          └───────────┘
```

### Resource Requirements

**Backend**
- **Requests**: 250m CPU, 512Mi memory
- **Limits**: 500m CPU, 1Gi memory
- **Replicas**: 2 (configurable)

**Frontend**
- **Requests**: 100m CPU, 128Mi memory
- **Limits**: 200m CPU, 256Mi memory
- **Replicas**: 2 (configurable)

### Security Features

- ✅ Non-root containers
- ✅ Read-only root filesystem capability
- ✅ Dropped all Linux capabilities
- ✅ TLS-enabled routes (edge termination)
- ✅ Secrets managed via Kubernetes Secrets
- ✅ Network isolation via Services
- ✅ Health checks (liveness & readiness probes)

## Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [OpenShift CLI Reference](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)
- [NC-ASK Architecture Documentation](./06_ARCHITECTURE.md)
- [NC-ASK Setup Guide](./04_LOCAL_SETUP.md)

## Support

For issues specific to:
- **NC-ASK application**: See project documentation
- **OpenShift platform**: Contact your cluster administrator
- **Supabase**: Check Supabase documentation and support
- **Google Gemini API**: See Google AI documentation

## Appendix A: Complete Command Reference

```bash
# Login
oc login --token=<token> --server=https://api.cluster.com:6443

# Create project
oc new-project nc-ask

# Create secrets
oc create secret generic nc-ask-secrets --from-literal=...

# Apply manifests
oc apply -f openshift/configmap.yaml
oc apply -f openshift/buildconfig.yaml
oc apply -f openshift/backend-deployment.yaml
oc apply -f openshift/frontend-deployment.yaml
oc apply -f openshift/route.yaml

# Start builds
oc start-build nc-ask-backend
oc start-build nc-ask-frontend

# Monitor
oc get pods -w
oc logs -f deployment/nc-ask-backend
oc get routes

# Scale
oc scale deployment/nc-ask-backend --replicas=3

# Update
oc start-build nc-ask-backend --follow

# Rollback
oc rollout undo deployment/nc-ask-backend

# Debug
oc rsh deployment/nc-ask-backend
oc logs deployment/nc-ask-backend
oc describe pod <pod-name>

# Cleanup
oc delete project nc-ask
```

## Appendix B: OpenShift Command Cheatsheet

Quick reference for common operations.

### Initial Setup

```bash
# Login to OpenShift
oc login --token=<your-token> --server=https://api.your-cluster.com:6443

# Create project
oc new-project nc-ask

# Create secrets (replace with actual values)
oc create secret generic nc-ask-secrets \
  --from-literal=SUPABASE_URL='https://xxx.supabase.co' \
  --from-literal=SUPABASE_ANON_KEY='eyJ...' \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY='eyJ...' \
  --from-literal=GOOGLE_API_KEY='AIza...' \
  --from-literal=SECRET_KEY='random-hex-32-chars'
```

### Automated Deployment

```bash
# Use the deployment script
cd openshift
./deploy.sh
```

### Monitoring Commands

```bash
# View all resources
oc get all

# View pods
oc get pods
oc get pods -w  # Watch mode

# View services
oc get svc

# View routes (URLs)
oc get routes

# View builds
oc get builds
oc get builds -w  # Watch mode

# View deployments
oc get deployments
```

### Logging Commands

```bash
# Backend logs (live)
oc logs -f deployment/nc-ask-backend

# Frontend logs (live)
oc logs -f deployment/nc-ask-frontend

# Logs from specific pod
oc logs nc-ask-backend-xxxxx-xxxxx

# Previous logs (if pod crashed)
oc logs nc-ask-backend-xxxxx-xxxxx --previous

# Build logs
oc logs -f build/nc-ask-backend-1
oc logs -f bc/nc-ask-backend  # Latest build

# Follow logs from all pods with label
oc logs -f -l app=nc-ask --all-containers=true
```

### Debugging Commands

```bash
# Describe pod (shows events, errors)
oc describe pod nc-ask-backend-xxxxx-xxxxx

# Get shell in pod
oc rsh deployment/nc-ask-backend

# Execute command in pod
oc exec deployment/nc-ask-backend -- env | grep SUPABASE
oc exec deployment/nc-ask-backend -- curl localhost:8000/api/health

# Port forward to local machine
oc port-forward deployment/nc-ask-backend 8000:8000
# Then access: http://localhost:8000

# View recent events
oc get events --sort-by='.lastTimestamp'

# Events for specific resource
oc describe deployment nc-ask-backend

# Check recent errors
oc get events --sort-by='.lastTimestamp' | grep -i error
```

### Configuration Management

```bash
# Edit ConfigMap
oc edit configmap nc-ask-config

# Edit Secret
oc edit secret nc-ask-secrets

# Restart deployments (to pick up config changes)
oc rollout restart deployment/nc-ask-backend
oc rollout restart deployment/nc-ask-frontend

# Update single config value
oc patch configmap nc-ask-config -p '{"data":{"LOG_LEVEL":"DEBUG"}}'

# Update CORS with frontend URL
FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')
oc patch configmap nc-ask-config -p '{"data":{"ALLOWED_ORIGINS":"https://'$FRONTEND_URL'"}}'

# List all env vars in deployment
oc set env deployment/nc-ask-backend --list

# Add environment variable
oc set env deployment/nc-ask-backend NEW_VAR=value

# Remove environment variable
oc set env deployment/nc-ask-backend NEW_VAR-
```

### Scaling Commands

```bash
# Manual scaling
oc scale deployment/nc-ask-backend --replicas=3
oc scale deployment/nc-ask-frontend --replicas=2

# View current scale
oc get deployment

# Autoscaling
oc autoscale deployment/nc-ask-backend --min=2 --max=5 --cpu-percent=75
oc get hpa  # View horizontal pod autoscalers
oc delete hpa nc-ask-backend  # Remove autoscaling

# View resource usage
oc adm top pods
oc adm top nodes
oc adm top pods --containers
```

### Building and Deploying

```bash
# Rebuild from Git
oc start-build nc-ask-backend
oc start-build nc-ask-frontend

# Rebuild from local directory
oc start-build nc-ask-backend --from-dir=. --follow

# Watch build progress
oc logs -f build/nc-ask-backend-1

# Check build status
oc get builds

# Cancel running build
oc cancel-build nc-ask-backend-1
```

### Rollout Management

```bash
# Watch rollout status
oc rollout status deployment/nc-ask-backend

# View rollout history
oc rollout history deployment/nc-ask-backend

# Rollback to previous version
oc rollout undo deployment/nc-ask-backend

# Rollback to specific revision
oc rollout undo deployment/nc-ask-backend --to-revision=2

# Pause rollout
oc rollout pause deployment/nc-ask-backend

# Resume rollout
oc rollout resume deployment/nc-ask-backend
```

### Routes and Networking

```bash
# Get all routes
oc get routes

# Get specific route URL
oc get route nc-ask-frontend -o jsonpath='{.spec.host}'

# Get full URL with protocol
echo "https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')"

# Test backend health
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
curl https://$BACKEND_URL/api/health

# View services
oc get svc

# View endpoints
oc get endpoints

# Test service connectivity from inside cluster
oc run test-pod --image=curlimages/curl --rm -it -- \
  curl http://nc-ask-backend:8000/api/health
```

### Secrets Management

```bash
# View secret (won't show values)
oc describe secret nc-ask-secrets

# Get secret values (base64 encoded)
oc get secret nc-ask-secrets -o yaml

# Decode secret value
oc get secret nc-ask-secrets -o jsonpath='{.data.GOOGLE_API_KEY}' | base64 -d

# Update secret
oc delete secret nc-ask-secrets
oc create secret generic nc-ask-secrets --from-literal=...

# Or patch existing secret
oc patch secret nc-ask-secrets -p '{"data":{"NEW_KEY":"'$(echo -n "value" | base64)'"}}'
```

### Resource Management

```bash
# Edit deployment (change resources, replicas, etc.)
oc edit deployment nc-ask-backend

# Update resource limits
oc set resources deployment/nc-ask-backend \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

### ImageStreams

```bash
# View image streams
oc get imagestreams
oc get is

# View image tags
oc get istag

# Describe image stream
oc describe is backend

# Import external image
oc import-image myimage --from=docker.io/myorg/myimage:latest --confirm

# Tag image
oc tag backend:latest backend:prod
```

### Health Checks

```bash
# Test backend health endpoint
BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')
curl https://$BACKEND_URL/api/health

# Check readiness probes
oc get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'

# View pod conditions
oc get pod nc-ask-backend-xxxxx-xxxxx -o jsonpath='{.status.conditions}' | jq
```

### Export and Backup

```bash
# Export all resources
oc get all,configmap,secret,route -l app=nc-ask -o yaml > nc-ask-backup.yaml

# Export specific resource
oc get deployment nc-ask-backend -o yaml > backend-deployment-backup.yaml

# Apply backup
oc apply -f nc-ask-backup.yaml
```

### Project Management

```bash
# List all projects
oc projects

# Switch project
oc project nc-ask

# View current project
oc project

# Project details
oc describe project nc-ask
```

### Quick Diagnostics

```bash
# One-liner to check everything
oc get pods,svc,routes,builds,is

# Check if all pods are running
oc get pods | grep -v Running

# Get pod names only
oc get pods -o name

# Get pod IPs
oc get pods -o wide

# JSON output for scripting
oc get pods -o json | jq '.items[].metadata.name'

# Custom columns
oc get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP

# Watch pods continuously
watch oc get pods
```

### Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# OpenShift aliases
alias ocp='oc project'
alias ocg='oc get'
alias ocd='oc describe'
alias ocl='oc logs -f'
alias oce='oc exec -it'
alias ocr='oc rsh'

# NC-ASK specific
alias ncpods='oc get pods -l app=nc-ask'
alias nclogs-be='oc logs -f deployment/nc-ask-backend'
alias nclogs-fe='oc logs -f deployment/nc-ask-frontend'
alias ncurl='echo "Frontend: https://$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')" && echo "Backend: https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')"'
```

### Getting Help

```bash
# General help
oc help

# Command-specific help
oc logs --help
oc get --help

# Explain resource types
oc explain pod
oc explain deployment.spec
```

### Quick Reference Table

| Task | Command |
|------|---------|
| View pods | `oc get pods` |
| View logs | `oc logs -f deployment/nc-ask-backend` |
| Shell into pod | `oc rsh deployment/nc-ask-backend` |
| Restart deployment | `oc rollout restart deployment/nc-ask-backend` |
| Scale up | `oc scale deployment/nc-ask-backend --replicas=3` |
| Rebuild | `oc start-build nc-ask-backend` |
| Get URLs | `oc get routes` |
| Watch builds | `oc get builds -w` |
| Rollback | `oc rollout undo deployment/nc-ask-backend` |
| Delete all | `oc delete all -l app=nc-ask` |
| Health check | `curl https://$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')/api/health` |
| View events | `oc get events --sort-by='.lastTimestamp'` |
| Resource usage | `oc adm top pods` |
