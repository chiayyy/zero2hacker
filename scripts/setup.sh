#!/bin/bash

# Zero2Hacker CTF Platform Setup Script
# This script sets up the complete development environment

set -e

echo "🚀 Zero2Hacker CTF Platform Setup"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/ollama
mkdir -p uploads/challenges
mkdir -p backups

# Copy environment files
echo "⚙️ Setting up environment configuration..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Backend .env file created from example"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Frontend .env file created from example"
fi

# Generate secrets
echo "🔐 Generating secure secrets..."
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)

# Update backend .env with generated secrets
sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/g" backend/.env
sed -i "s/DATABASE_URL=sqlite:\/\/\/\.\/zero2hacker\.db/DATABASE_URL=postgresql:\/\/ctf_user:$DB_PASSWORD@localhost:5432\/zero2hacker_ctf/g" backend/.env

echo "✅ Secrets generated and configured"

# Download Ollama models
echo "🤖 Setting up AI models..."
cat > scripts/download_models.sh << 'EOF'
#!/bin/bash
echo "Downloading AI models for challenge generation..."
docker exec zero2hacker-ctf-ollama-1 ollama pull llama3
docker exec zero2hacker-ctf-ollama-1 ollama pull mistral
docker exec zero2hacker-ctf-ollama-1 ollama pull codellama
echo "AI models downloaded successfully!"
EOF
chmod +x scripts/download_models.sh

# Create development startup script
cat > scripts/dev-start.sh << 'EOF'
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
EOF
chmod +x scripts/dev-start.sh

# Create production deployment script
cat > scripts/prod-deploy.sh << 'EOF'
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
EOF
chmod +x scripts/prod-deploy.sh

# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
echo "💾 Creating backup..."

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker exec zero2hacker-ctf-postgres-1 pg_dump -U ctf_user zero2hacker_ctf > "$BACKUP_DIR/database.sql"

# Backup uploaded files
tar -czf "$BACKUP_DIR/uploads.tar.gz" uploads/

# Backup configuration
cp -r backend/.env frontend/.env docker/ "$BACKUP_DIR/"

echo "✅ Backup created: $BACKUP_DIR"
EOF
chmod +x scripts/backup.sh

# Create monitoring setup script
cat > scripts/setup-monitoring.sh << 'EOF'
#!/bin/bash
echo "📊 Setting up monitoring and logging..."

# Create Prometheus configuration
mkdir -p monitoring
cat > monitoring/prometheus.yml << 'PROMETHEUS'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'zero2hacker-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
PROMETHEUS

# Create Grafana dashboards directory
mkdir -p monitoring/grafana/dashboards

echo "✅ Monitoring configuration created"
EOF
chmod +x scripts/setup-monitoring.sh

# Create test script
cat > scripts/run-tests.sh << 'EOF'
#!/bin/bash
echo "🧪 Running tests..."

# Backend tests
echo "Testing backend..."
cd backend
python -m pytest tests/ -v --cov=app --cov-report=html

# Frontend tests
echo "Testing frontend..."
cd ../frontend
npm test -- --coverage --watchAll=false

echo "✅ All tests completed"
EOF
chmod +x scripts/run-tests.sh

# Initialize Git repository if not exists
if [ ! -d .git ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Zero2Hacker CTF Platform"
    echo "✅ Git repository initialized"
fi

# Final setup
echo "🔧 Final setup steps..."
./scripts/setup-monitoring.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review and update configuration files:"
echo "   - backend/.env"
echo "   - frontend/.env"
echo ""
echo "2. Start the development environment:"
echo "   ./scripts/dev-start.sh"
echo ""
echo "3. Or deploy to production:"
echo "   ./scripts/prod-deploy.sh"
echo ""
echo "4. Create regular backups:"
echo "   ./scripts/backup.sh"
echo ""
echo "📖 Documentation: README.md"
echo "🌐 Once started, visit: http://localhost:3000"