#!/bin/bash

# Therapeutic Painting Canvas - Quick Start Script

echo "================================================"
echo "  Therapeutic Painting - Fabric.js Canvas"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Error installing dependencies"
    exit 1
fi

# Start the FastAPI server
echo ""
echo "================================================"
echo "  Starting FastAPI server..."
echo "================================================"
echo ""
echo "🎨 Canvas will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server as a module (required for relative imports)
python -m api.server
