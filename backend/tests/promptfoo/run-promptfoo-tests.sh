#!/bin/bash
# Script to run Promptfoo tests for NC-ASK
# This script checks if backend is running and runs the promptfoo test suite

set -e

echo "🚀 NC-ASK Promptfoo Test Runner"
echo "================================"

# Check if backend is already running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "Backend server is already running"
else
    echo "Backend server is not running"
    echo "Please start the backend server first with:"
    echo "  cd backend && uvicorn main:app --reload"
    echo ""
    echo "Or in another terminal, run:"
    echo "  npm run dev:backend"
    exit 1
fi

echo ""
echo "Running Promptfoo tests..."
echo "=========================="
echo ""

# Get to project root (3 levels up from backend/tests/promptfoo)
cd "$(dirname "$0")/../../.."

# Run promptfoo with the comprehensive test suite
npm run promptfoo

echo ""
echo "Tests complete!"
echo ""
echo "To view results in the web UI, run:"
echo "  npm run promptfoo:view"
