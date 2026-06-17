#!/bin/bash
set -e

echo "=== AI Knowledge Base Management Platform ==="
echo "Starting development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Please update the configuration."
fi

# Start Docker Compose
docker compose up -d

echo ""
echo "Services starting..."
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - pgAdmin:   http://localhost:5050 (if enabled)"
echo ""
echo "Run 'docker compose logs -f' to view logs"
echo "Run './scripts/dev_stop.sh' to stop all services"
