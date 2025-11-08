#!/bin/bash

# Flask API startup script

echo "Starting Flask Todo API..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    uv venv
fi

# Install/update dependencies
echo "Installing dependencies..."
uv sync

# Run the application
echo "Starting server on port ${FLASK_PORT:-5000}..."
uv run python main.py
