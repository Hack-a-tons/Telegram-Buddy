#!/bin/bash

# Telegram Buddy AI Deployment Script
# Run this on your Ubuntu server

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Deploying Telegram Buddy AI from $SCRIPT_DIR..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    echo "cp .env.example .env"
    echo "# Then edit .env with your API keys"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and back in, then run this script again."
    exit 1
fi

# Check if docker compose is available (modern Docker includes it)
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose not available. Please update Docker to a newer version."
    exit 1
fi

echo "📦 Building services..."
cd docker
if ! docker compose build; then
    echo "❌ Build failed! Deployment aborted."
    exit 1
fi

echo "🔄 Stopping existing services..."
docker compose down

echo "🚀 Starting services..."
docker compose up -d

echo "✅ Deployment complete!"
echo ""
echo "🌐 Web interface: http://your-server:${PORT:-8000}"
echo "🤖 Telegram bot: Running in background"
echo ""
echo "📊 Check status:"
echo "  docker compose logs web"
echo "  docker compose logs telegram-bot"
echo ""
echo "🛑 Stop services:"
echo "  docker compose down"
