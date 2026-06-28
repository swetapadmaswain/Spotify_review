#!/bin/bash
# Vercel build script for FastAPI backend

set -e

echo "🔍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"
echo "🚀 Starting backend..."

# Verify app structure
echo "📁 Project structure:"
find . -name "*.py" -path "./app/*" | head -10

# Start the backend
echo "✅ Backend ready!"
