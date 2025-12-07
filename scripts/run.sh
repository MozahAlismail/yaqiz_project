#!/bin/bash

echo "AI Emergency Dispatch Assistant - Startup Script"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize databases
echo "Initializing databases..."
python data/init_db.py

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set!"
    echo "Please set it with: export OPENAI_API_KEY=your-key"
    exit 1
fi

# Start the server
echo "Starting FastAPI server..."
python main.py
