#!/bin/bash

# Dircolor Editor Launcher
# Simple script to launch the dircolor editor

cd "$(dirname "$0")"

echo "🎨 Starting Dircolor Editor..."
echo "   Loading your ~/.dircolors file..."
echo "   Use Ctrl+C to exit"
echo ""

# Check if GUI is available
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "❌ No display found. This is a GUI application."
    echo "   Make sure you're running in a desktop environment."
    exit 1
fi

# Launch the application
python3 run.py "$@"