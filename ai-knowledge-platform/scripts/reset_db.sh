#!/bin/bash
set -e

echo "Resetting database..."
docker compose down -v postgres
docker compose up -d postgres
echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo "Running migrations..."
docker compose run --rm backend alembic upgrade head

echo "Seeding initial data..."
docker compose run --rm backend python scripts/seed_data.py

echo "Database reset complete."
