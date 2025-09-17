#!/bin/bash

# Telegram Buddy AI Deployment Script
# Run this on your Ubuntu server

echo "🚀 Deploying Telegram Buddy AI..."

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

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "📦 Building and starting services..."
cd docker
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Deployment complete!"
echo ""
echo "🌐 Web interface: http://your-server:8000"
echo "🤖 Telegram bot: Running in background"
echo ""
echo "📊 Check status:"
echo "  docker-compose logs web"
echo "  docker-compose logs telegram-bot"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
