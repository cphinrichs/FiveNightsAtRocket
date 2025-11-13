#!/bin/bash
# Build script for Five Nights at Rocket
# This script packages the game for browser deployment using pygbag

echo "========================================"
echo "Five Nights at Rocket - Build Script"
echo "========================================"
echo ""

# Check if pygbag is installed
if ! python3 -c "import pygbag" 2>/dev/null; then
    echo "[ERROR] pygbag is not installed!"
    echo "Installing pygbag..."
    pip3 install pygbag
    echo ""
fi

echo "Building game with pygbag..."
echo "This will create a web-deployable version of the game."
echo ""

cd "$(dirname "$0")"
python3 -m pygbag --build main.py

echo ""
echo "========================================"
echo "Build complete!"
echo "========================================"
echo ""
echo "To test the game in browser:"
echo "1. Run: python3 -m pygbag main.py"
echo "2. Open the URL shown in your browser"
echo ""
echo "Or test locally with:"
echo "   python3 main.py"
echo ""
