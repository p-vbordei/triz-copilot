#!/bin/bash

# Setup script for Ollama embedding service
set -e

echo "Setting up Ollama for TRIZ Co-Pilot..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed. Please install from https://ollama.ai"
    exit 1
fi

# Start Ollama service if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

# Pull required embedding model
echo "Pulling nomic-embed-text model..."
ollama pull nomic-embed-text

# Verify model is available
echo "Verifying model installation..."
if ollama list | grep -q "nomic-embed-text"; then
    echo "✓ nomic-embed-text model successfully installed"
else
    echo "✗ Failed to install nomic-embed-text model"
    exit 1
fi

# Optional: Pull additional models for future use
echo "Optional: Pull additional models? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    ollama pull all-minilm
    echo "Additional models pulled"
fi

echo "Ollama setup complete!"
echo "To test: ollama run nomic-embed-text 'test embedding'"