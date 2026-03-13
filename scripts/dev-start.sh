#!/bin/bash
echo "🚀 Starting Zero2Hacker CTF Platform (Development Mode)"
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🤖 Downloading AI models (this may take a while)..."
./scripts/download_models.sh

echo "✅ Development environment is ready!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📊 Grafana: http://localhost:3001 (admin/admin)"
