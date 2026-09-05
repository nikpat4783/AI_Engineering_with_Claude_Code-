@echo off
REM ALOCA+ QA System Startup Script for Windows

echo.
echo ========================================
echo   ALOCA+ QA System Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or later.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 14 or later.
    pause
    exit /b 1
)

REM Start Backend
echo [INFO] Starting Backend Server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update requirements
echo [INFO] Installing Python dependencies...
pip install -q -r requirements.txt

REM Start backend server in new window
start "ALOCA+ Backend" cmd /k "python main.py"
echo [OK] Backend server started
timeout /t 2

REM Start Frontend
echo.
echo [INFO] Starting Frontend Server...
cd ..\frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo [INFO] Installing npm dependencies (this may take a minute)...
    call npm install -q
)

REM Start frontend server in new window
start "ALOCA+ Frontend" cmd /k "npm start"
echo [OK] Frontend server started

echo.
echo ========================================
echo   ALOCA+ QA System is running!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Close these windows to stop the servers.
echo.
pause
