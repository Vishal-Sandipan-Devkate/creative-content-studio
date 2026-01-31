#!/bin/bash

# Creative Content Studio MCP - Setup Script
# ============================================
# This script sets up the project environment

set -e  # Exit on error

echo "🎨 Creative Content Studio MCP - Setup"
echo "======================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.10+ required. You have Python $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for FFmpeg (needed for video processing)
echo "🎬 Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
else
    echo "⚠️  FFmpeg not found (needed for video features)"
    echo "   Install with:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt-get install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/"
fi
echo ""

# Check for espeak (needed for text-to-speech)
echo "🔊 Checking for espeak..."
if command -v espeak &> /dev/null; then
    echo "✅ espeak is installed"
else
    echo "⚠️  espeak not found (needed for text-to-speech)"
    echo "   Install with:"
    echo "   - macOS: brew install espeak"
    echo "   - Ubuntu: sudo apt-get install espeak"
fi
echo ""

# Create output directory
echo "📁 Creating output directory..."
mkdir -p content_outputs
echo "✅ Output directory ready"
echo ""

# Check for API key
echo "🔑 Checking for API key..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  No .env file found"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   Please edit .env and add your ANTHROPIC_API_KEY"
fi
echo ""

# Setup complete
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Add your API key to .env:"
echo "   export ANTHROPIC_API_KEY='your-key-here'"
echo ""
echo "2. Run the demo:"
echo "   python demo.py"
echo ""
echo "3. Or start interactive mode:"
echo "   python content_studio_client.py content_studio_server.py"
echo ""
echo "Happy creating! 🚀"
