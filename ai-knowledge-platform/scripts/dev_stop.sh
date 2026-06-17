#!/bin/bash
set -e

echo "Stopping AI Knowledge Base Management Platform..."
docker compose down
echo "All services stopped."
