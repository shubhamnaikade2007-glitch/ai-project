@echo off
REM ============================================================
REM HealthFit AI - Create Python Virtual Environment
REM Run this from: backend/flask-backend/
REM ============================================================

echo.
echo =============================================
echo  HealthFit AI - Backend Setup
echo =============================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [4/4] Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

echo.
echo [5/5] Copying .env file...
if not exist .env (
    if exist ..\..\env.example (
        copy ..\..\env.example .env
        echo .env file created from example
    ) else (
        echo WARNING: No .env.example found. Create .env manually.
    )
)

echo.
echo =============================================
echo  Setup Complete!
echo =============================================
echo.
echo To start the backend:
echo   1. venv\Scripts\activate
echo   2. python run.py
echo.
pause
