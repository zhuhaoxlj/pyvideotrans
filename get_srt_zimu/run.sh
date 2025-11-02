#!/bin/bash

# Whisper Auto Captions - Launcher Script (using uv)

echo "🎬 Whisper Auto Captions - Python Edition"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    
    # Install uv
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        echo "❌ Error: Please install uv manually from https://github.com/astral-sh/uv"
        exit 1
    fi
    
    echo "✓ uv installed successfully"
fi

# Check uv version
UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
echo "✓ Found uv $UV_VERSION"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg is not installed"
    echo "Please install FFmpeg for audio processing:"
    echo "  macOS:   brew install ffmpeg"
    echo "  Ubuntu:  sudo apt install ffmpeg"
    echo ""
fi

# Sync dependencies (create venv if needed, install packages)
echo "📦 Syncing dependencies..."
uv sync

echo ""
echo "🚀 Starting Whisper Auto Captions..."
echo ""

# Run the application with uv
uv run python main.py
