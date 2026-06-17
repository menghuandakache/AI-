#!/bin/bash
set -e

echo "Building AI Knowledge Base Management Platform..."
docker compose build

echo "Build complete. Run './scripts/dev_start.sh' to start."
