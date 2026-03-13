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
