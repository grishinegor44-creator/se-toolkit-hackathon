#!/usr/bin/env bash
# Quick local start script for the demo.
# Usage: bash scripts/run_local.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== CocktailBot — Local Start ==="

# Check .env exists
if [ ! -f .env ]; then
  echo "ERROR: .env file not found."
  echo "Copy .env.example to .env and fill in BOT_TOKEN."
  exit 1
fi

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker Desktop first."
  exit 1
fi

echo "Starting services with Docker Compose..."
docker compose up --build -d

echo ""
echo "Waiting for backend to be healthy..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    echo "Backend is up!"
    break
  fi
  echo "  Waiting... ($i/30)"
  sleep 2
done

echo ""
echo "=== All services started ==="
echo ""
echo "Backend API docs: http://localhost:8000/docs"
echo "Backend health:   http://localhost:8000/health"
echo ""
echo "Bot logs:"
docker compose logs --tail=20 bot
echo ""
echo "Your bot is ready! Open Telegram and send /start"
echo ""
echo "To stop: docker compose down"
