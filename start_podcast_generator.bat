@echo off
echo ========================================
echo    Podcast Generator - Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env file...
    echo Please enter your Google Gemini API Key:
    echo (Get it from: https://aistudio.google.com/app/apikey)
    set /p GEMINI_KEY="API Key: "
    echo GEMINI_API_KEY=!GEMINI_KEY! > .env
    echo.
    echo [OK] .env file created
    echo.
)

REM Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)
echo.

REM Create outputs directory if it doesn't exist
if not exist "outputs" mkdir outputs

echo ========================================
echo    Starting Podcast Generator Server
echo ========================================
echo.
echo Server will start at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask server
python app.py

pause
