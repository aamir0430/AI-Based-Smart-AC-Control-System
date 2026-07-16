@echo off
echo 🏠 Starting Haier AC Control System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import cv2, mediapipe, numpy, requests, sounddevice" >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing required libraries...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        echo Try running: pip install --user -r requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ All dependencies ready
echo.

REM Check if camera is available
echo 🎥 Testing camera...
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera available' if cap.isOpened() else 'Camera not available'); cap.release()" 2>nul
if errorlevel 1 (
    echo ⚠️  Camera test failed - continuing anyway
)

echo.
echo 🚀 Starting AC Control System...
echo Press 'q' in the camera window to quit
echo.

REM Run the main program
python main.py

echo.
echo 👋 AC Control System stopped
pause


