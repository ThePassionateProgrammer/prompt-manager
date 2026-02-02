#!/bin/bash
# Prompt Manager Setup Script
# This script automates the installation process for the Prompt Manager application.

set -e

echo "========================================"
echo "  Prompt Manager - Setup Script"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "  Found Python $PYTHON_VERSION"
else
    echo "  ERROR: Python 3 is not installed."
    echo "  Please install Python 3.11 or later from https://python.org"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "  Virtual environment created."
else
    echo ""
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "  Activated."

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  Dependencies installed."

# Check for Ollama (optional)
echo ""
echo "Checking for Ollama (local AI models)..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -1)
    echo "  Found Ollama: $OLLAMA_VERSION"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  Ollama server is running."

        # List available models
        MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ', ' | sed 's/,$//')
        if [ -n "$MODELS" ]; then
            echo "  Available models: $MODELS"
        else
            echo "  No models downloaded yet."
            echo "  TIP: Run 'ollama pull gemma3:4b' to download a lightweight model."
        fi
    else
        echo "  Ollama is installed but not running."
        echo "  TIP: Run 'ollama serve' to start the Ollama server."
    fi
else
    echo "  Ollama not found (optional - for local AI models)."
    echo "  Install from: https://ollama.ai"
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the Prompt Manager:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python prompt_manager_app.py"
echo ""
echo "  3. Open your browser to:"
echo "     http://localhost:8000"
echo ""
echo "  4. Go to Settings to add your API keys"
echo "     (or use Ollama for local models)"
echo ""
