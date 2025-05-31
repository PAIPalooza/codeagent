#!/bin/bash

# Print header
echo "======================================"
echo "  CodeAgent Development Setup"
echo "======================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.9+ is required but it's not installed."
    exit 1
else
    echo "✅ Found Python $(python3 --version | cut -d' ' -f2)"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 16+ is required but it's not installed."
    exit 1
else
    echo "✅ Found Node.js $(node --version)"
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but it's not installed."
    exit 1
else
    echo "✅ Found npm $(npm --version)"
fi

# Check for PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is recommended but not found. Some features may not work."
else
    echo "✅ Found PostgreSQL $(psql --version | awk '{print $3}')"
fi

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Some AI features may not work."
    echo "    Install from: https://ollama.ai/"
else
    echo "✅ Found Ollama"
fi

# Create and activate virtual environment
echo -e "\n🚀 Setting up Python virtual environment..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install Python dependencies
echo -e "\n📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo -e "\n🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "ℹ️  Created .env file. Please update it with your configuration."
else
    echo "ℹ️  .env file already exists. Skipping..."
fi

# Install Node.js dependencies
echo -e "\n📦 Installing Node.js dependencies..."
cd ../frontend
npm install

# Initialize database
echo -e "\n💾 Initializing database..."
# Add database initialization commands here

# Print success message
echo -e "\n✨ Setup complete! ✨"
echo -e "\nTo start the development servers, run:"
echo -e "1. Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo -e "2. Frontend: cd frontend && npm start"

echo -e "\nAccess the application at http://localhost:3000"
echo -e "API documentation is available at http://localhost:8000/docs"
