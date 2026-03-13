#!/bin/bash
echo "🚀 Deploying Zero2Hacker CTF Platform (Production Mode)"

# Check for required environment variables
if [ -z "$SECRET_KEY" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ Required environment variables not set"
    echo "Please set: SECRET_KEY, DB_PASSWORD"
    exit 1
fi

# Build production images
echo "🏗️ Building production images..."
docker-compose -f deploy/production.yml build

# Deploy with production configuration
echo "📦 Deploying services..."
docker-compose -f deploy/production.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Initialize database
echo "🗄️ Initializing database..."
docker-compose -f deploy/production.yml exec backend python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"

echo "✅ Production deployment complete!"
echo "🌐 Platform: https://zero2hacker.com"
echo "🔧 API: https://api.zero2hacker.com"
