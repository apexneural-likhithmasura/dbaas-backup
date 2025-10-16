#!/bin/bash

# Pain Point & Market Gap Analyzer - Startup Script

echo "🚀 Starting Pain Point & Market Gap Analyzer API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from env.example..."
    cp env.example .env
    echo "⚠️  Please edit .env and add your API keys before running the server."
    exit 1
fi

# Run the server
echo "✅ Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📖 Alternative Docs: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

