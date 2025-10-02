#!/bin/bash

# NC-ASK Pre-flight Check Script
# Run this before starting Docker to catch configuration issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 NC-ASK Pre-flight Check"
echo "=========================="
echo ""

ERRORS=0

# Check 1: Docker is installed and running
echo -n "1. Checking Docker... "
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    ERRORS=$((ERRORS + 1))
elif ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker daemon not running${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Docker is running${NC}"
fi

# Check 2: Docker Compose is available
echo -n "2. Checking Docker Compose... "
if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not available${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Docker Compose available${NC}"
fi

# Check 3: .env file exists
echo -n "3. Checking .env file... "
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "   Run: cp env.example .env"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check 4: Required environment variables
if [ -f ".env" ]; then
    echo "4. Checking environment variables..."
    
    check_env_var() {
        local var_name=$1
        local placeholder=$2
        
        if ! grep -q "^${var_name}=" .env; then
            echo -e "   ${RED}✗ ${var_name} not found in .env${NC}"
            ERRORS=$((ERRORS + 1))
        elif grep -q "^${var_name}=${placeholder}" .env; then
            echo -e "   ${YELLOW}⚠ ${var_name} needs to be updated${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "   ${GREEN}✓ ${var_name} configured${NC}"
        fi
    }
    
    check_env_var "SUPABASE_URL" "https://your-project-id.supabase.co"
    check_env_var "SUPABASE_ANON_KEY" "your_anon_key_here"
    check_env_var "SUPABASE_SERVICE_ROLE_KEY" "your_service_role_key_here"
    check_env_var "GOOGLE_API_KEY" "your_gemini_api_key_here"
    check_env_var "SECRET_KEY" "your_secret_key_here"
fi

# Check 5: Required files exist
echo "5. Checking required files..."
FILES=(
    "backend/main.py"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/vite.config.ts"
    "requirements.txt"
    "docker-compose.yml"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓ $file${NC}"
    else
        echo -e "   ${RED}✗ $file missing${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 6: Ports availability
echo "6. Checking port availability..."
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "   ${YELLOW}⚠ Port $port is in use${NC}"
        echo "     Run: lsof -i :$port to see what's using it"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "   ${GREEN}✓ Port $port is available${NC}"
    fi
}

check_port 8000
check_port 5173
check_port 6379

# Check 7: Backend directory structure
echo -n "7. Checking backend structure... "
if [ -d "backend/api" ] && [ -d "backend/services" ] && [ -d "backend/scripts" ]; then
    echo -e "${GREEN}✓ Backend structure valid${NC}"
else
    echo -e "${RED}✗ Backend structure incomplete${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: Frontend directory structure
echo -n "8. Checking frontend structure... "
if [ -d "frontend/src" ] && [ -f "frontend/index.html" ]; then
    echo -e "${GREEN}✓ Frontend structure valid${NC}"
else
    echo -e "${RED}✗ Frontend structure incomplete${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=========================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready to run Docker Compose${NC}"
    echo ""
    echo "Run: docker compose up --build"
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS issue(s). Please fix them before running Docker Compose${NC}"
    echo ""
    echo "Common fixes:"
    echo "  • Update .env with your actual credentials"
    echo "  • Generate SECRET_KEY: openssl rand -hex 32"
    echo "  • Get Supabase keys from: https://app.supabase.com/project/YOUR_PROJECT/settings/api"
    echo "  • Get Gemini API key from: https://makersuite.google.com/app/apikey"
    echo "  • Stop services using required ports"
    exit 1
fi

