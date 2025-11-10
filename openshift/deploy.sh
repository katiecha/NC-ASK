#!/bin/bash
# NC-ASK OpenShift Deployment Script
# This script helps deploy NC-ASK to OpenShift with proper configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  ${1}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if oc is installed
check_oc_installed() {
    if ! command -v oc &> /dev/null; then
        print_error "OpenShift CLI (oc) is not installed!"
        print_info "Install from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html"
        exit 1
    fi
    print_success "OpenShift CLI found: $(oc version --client | head -n1)"
}

# Check if logged into OpenShift
check_oc_login() {
    if ! oc whoami &> /dev/null; then
        print_error "Not logged into OpenShift!"
        print_info "Login with: oc login --token=<your-token> --server=https://api.your-cluster.com:6443"
        exit 1
    fi
    print_success "Logged in as: $(oc whoami)"
    print_info "Server: $(oc whoami --show-server)"
}

# Create or switch to project
setup_project() {
    local project_name="nc-ask"

    print_header "Setting up OpenShift Project"

    if oc get project "$project_name" &> /dev/null; then
        print_warning "Project '$project_name' already exists"
        oc project "$project_name"
    else
        print_info "Creating project '$project_name'..."
        oc new-project "$project_name" \
            --description="NC Autism Support & Knowledge Platform" \
            --display-name="NC-ASK"
        print_success "Project created successfully"
    fi
}

# Create secrets interactively
create_secrets() {
    print_header "Creating Secrets"

    if oc get secret nc-ask-secrets &> /dev/null; then
        print_warning "Secret 'nc-ask-secrets' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping secrets creation"
            return
        fi
        oc delete secret nc-ask-secrets
    fi

    print_info "Please provide the following credentials:"
    echo ""

    read -p "Supabase URL: " SUPABASE_URL
    read -p "Supabase Anon Key: " SUPABASE_ANON_KEY
    read -sp "Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
    echo ""
    read -sp "Google Gemini API Key: " GOOGLE_API_KEY
    echo ""

    print_info "Generating random secret key..."
    SECRET_KEY=$(openssl rand -hex 32)

    oc create secret generic nc-ask-secrets \
        --from-literal=SUPABASE_URL="$SUPABASE_URL" \
        --from-literal=SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
        --from-literal=SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
        --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
        --from-literal=SECRET_KEY="$SECRET_KEY"

    print_success "Secrets created successfully"
}

# Apply manifests
apply_manifests() {
    print_header "Applying Manifests"

    local manifests=(
        "configmap.yaml"
        "buildconfig.yaml"
        "backend-deployment.yaml"
        "frontend-deployment.yaml"
        "route.yaml"
    )

    for manifest in "${manifests[@]}"; do
        print_info "Applying $manifest..."
        oc apply -f "openshift/$manifest"
        print_success "$manifest applied"
    done
}

# Start builds
start_builds() {
    print_header "Starting Builds"

    print_info "Starting backend build..."
    oc start-build nc-ask-backend

    print_info "Starting frontend build..."
    oc start-build nc-ask-frontend

    print_success "Builds initiated"
    print_warning "Builds are running in the background. Monitor with: oc get builds -w"
}

# Wait for builds to complete
wait_for_builds() {
    print_header "Waiting for Builds to Complete"

    print_info "Waiting for backend build..."
    oc wait --for=condition=Complete build/nc-ask-backend-1 --timeout=600s || {
        print_error "Backend build failed or timed out"
        print_info "Check logs with: oc logs -f bc/nc-ask-backend"
        exit 1
    }
    print_success "Backend build completed"

    print_info "Waiting for frontend build..."
    oc wait --for=condition=Complete build/nc-ask-frontend-1 --timeout=600s || {
        print_error "Frontend build failed or timed out"
        print_info "Check logs with: oc logs -f bc/nc-ask-frontend"
        exit 1
    }
    print_success "Frontend build completed"
}

# Wait for deployments to be ready
wait_for_deployments() {
    print_header "Waiting for Deployments"

    print_info "Waiting for backend deployment..."
    oc rollout status deployment/nc-ask-backend --timeout=300s
    print_success "Backend deployment ready"

    print_info "Waiting for frontend deployment..."
    oc rollout status deployment/nc-ask-frontend --timeout=300s
    print_success "Frontend deployment ready"
}

# Update CORS configuration
update_cors() {
    print_header "Updating CORS Configuration"

    print_info "Getting frontend route URL..."
    FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')

    if [ -z "$FRONTEND_URL" ]; then
        print_error "Could not get frontend route URL"
        return 1
    fi

    print_info "Frontend URL: https://$FRONTEND_URL"

    print_info "Updating CORS configuration..."
    oc patch configmap nc-ask-config -p "{\"data\":{\"ALLOWED_ORIGINS\":\"https://$FRONTEND_URL\"}}"

    print_info "Restarting backend to apply changes..."
    oc rollout restart deployment/nc-ask-backend

    print_success "CORS configuration updated"
}

# Update frontend with backend URL
update_frontend_backend_url() {
    print_header "Updating Frontend Backend URL"

    print_info "Getting backend route URL..."
    BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')

    if [ -z "$BACKEND_URL" ]; then
        print_error "Could not get backend route URL"
        return 1
    fi

    print_info "Backend URL: https://$BACKEND_URL"

    print_info "Updating BuildConfig..."
    oc patch bc/nc-ask-frontend -p "{\"spec\":{\"strategy\":{\"dockerStrategy\":{\"buildArgs\":[{\"name\":\"VITE_API_BASE_URL\",\"value\":\"https://$BACKEND_URL\"}]}}}}"

    print_info "Rebuilding frontend..."
    oc start-build nc-ask-frontend --follow

    print_success "Frontend updated with backend URL"
}

# Display final information
display_info() {
    print_header "Deployment Complete!"

    FRONTEND_URL=$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')
    BACKEND_URL=$(oc get route nc-ask-backend -o jsonpath='{.spec.host}')

    echo -e "${GREEN}Application URLs:${NC}"
    echo -e "  Frontend: ${BLUE}https://$FRONTEND_URL${NC}"
    echo -e "  Backend:  ${BLUE}https://$BACKEND_URL${NC}"
    echo ""
    echo -e "${GREEN}Useful Commands:${NC}"
    echo -e "  View pods:          ${YELLOW}oc get pods${NC}"
    echo -e "  View logs:          ${YELLOW}oc logs -f deployment/nc-ask-backend${NC}"
    echo -e "  View routes:        ${YELLOW}oc get routes${NC}"
    echo -e "  Scale deployment:   ${YELLOW}oc scale deployment/nc-ask-backend --replicas=3${NC}"
    echo ""
    echo -e "${GREEN}Health Check:${NC}"
    echo -e "  ${YELLOW}curl https://$BACKEND_URL/api/health${NC}"
    echo ""
}

# Main deployment flow
main() {
    print_header "NC-ASK OpenShift Deployment"

    check_oc_installed
    check_oc_login

    echo ""
    echo "This script will:"
    echo "  1. Create/switch to 'nc-ask' project"
    echo "  2. Create secrets (if needed)"
    echo "  3. Apply all manifests"
    echo "  4. Start builds"
    echo "  5. Wait for deployments"
    echo "  6. Configure CORS and routes"
    echo ""
    read -p "Continue? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi

    setup_project
    create_secrets
    apply_manifests
    start_builds

    print_warning "Do you want to wait for builds to complete? This may take several minutes."
    read -p "Wait for builds? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        wait_for_builds
        wait_for_deployments
        update_cors
        update_frontend_backend_url
    else
        print_info "Builds are running in the background"
        print_info "Monitor with: oc get builds -w"
        print_info "After builds complete, run these commands:"
        print_info "  1. Update CORS: oc patch configmap nc-ask-config -p '{\"data\":{\"ALLOWED_ORIGINS\":\"https://\$(oc get route nc-ask-frontend -o jsonpath='{.spec.host}')\"}}"
        print_info "  2. Restart backend: oc rollout restart deployment/nc-ask-backend"
        print_info "  3. Update frontend: oc start-build nc-ask-frontend"
    fi

    display_info
}

# Run main function
main
