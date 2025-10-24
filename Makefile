.PHONY: help dev docker-dev docker-prod test lint typecheck ingest clean

# Default target
help:
	@echo "NC-ASK Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run local dev (requires venv + npm)"
	@echo "  make docker-dev    - Run development Docker containers"
	@echo "  make docker-prod   - Run production Docker containers"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          - Run backend tests"
	@echo "  make lint          - Run linters"
	@echo "  make typecheck     - Run TypeScript type checking"
	@echo ""
	@echo "Data:"
	@echo "  make ingest        - Ingest documents to Supabase"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Stop Docker containers and clean up"

# Development
dev:
	@echo "Starting local development..."
	npm run dev

docker-dev:
	@echo "Starting development Docker containers..."
	docker-compose up --build

docker-prod:
	@echo "Starting production Docker containers..."
	docker-compose -f docker-compose.prod.yml up --build

# Testing & Quality
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest -v

lint:
	@echo "Running linters..."
	@echo "Frontend lint..."
	npm run lint
	@echo "TypeScript check..."
	npm run typecheck

typecheck:
	@echo "Running TypeScript type checking..."
	npm run typecheck

# Data
ingest:
	@echo "Ingesting documents..."
	cd backend && python scripts/ingest_documents.py

# Cleanup
clean:
	@echo "Stopping Docker containers..."
	docker-compose down
	docker-compose -f docker-compose.prod.yml down
	@echo "Cleaned up!"
