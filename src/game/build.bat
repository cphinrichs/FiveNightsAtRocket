@echo off
REM Build script for Five Nights at Rocket
REM This script packages the game for browser deployment using pygbag

echo ========================================
echo Five Nights at Rocket - Build Script
echo ========================================
echo.

REM Check if pygbag is installed
python -c "import pygbag" 2>nul
if errorlevel 1 (
    echo [ERROR] pygbag is not installed!
    echo Installing pygbag...
    pip install pygbag
    echo.
)

echo Building game with pygbag...
echo This will create a web-deployable version of the game.
echo.

cd /d "%~dp0"
python -m pygbag --build main.py

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo To test the game in browser:
echo 1. Run: python -m pygbag main.py
echo 2. Open the URL shown in your browser
echo.
echo Or test locally with:
echo    python main.py
echo.

pause
