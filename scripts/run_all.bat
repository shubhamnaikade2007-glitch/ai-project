@echo off
REM ============================================================
REM HealthFit AI - Complete Run Script (Windows)
REM Launches Backend, AI API, and Frontend in separate terminals
REM Prerequisites: Run scripts/setup_mysql.bat first (or manually setup MySQL)
REM Usage: Double-click or: scripts\run_all.bat
REM ============================================================

setlocal EnableDelayedExpansion
title HealthFit AI - Starting All Services...

echo.
echo  ██╗  ██╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗███████╗██╗████████╗
echo  ██║  ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║██╔════╝██║╚══██╔══╝
echo  ███████║█████╗  ███████║██║     ██║   ███████║█████╗  ██║   ██║
echo  ██╔══██║██╔══╝  ██╔══██║██║     ██║   ██╔══██║██╔══╝  ██║   ██║
echo  ██║  ██║███████╗██║  ██║███████╗██║   ██║  ██║██║     ██║   ██║
echo  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝
echo.
echo  🚀 Starting HealthFit AI - Full Stack Application
echo  ==================================================
echo.

REM Check project root
if not exist "backend\flask-backend" (
    echo [ERROR] Run from PROJECT ROOT (healthfit_clean folder)
    pause
    exit /b 1
)

REM Check if setup_mysql.bat was run (check for backend venv)
if not exist "backend\flask-backend\venv" (
    echo [WARNING] Backend venv not found. Run: scripts\setup_mysql.bat first
    echo           Or manually: cd backend\flask-backend ^&^& python -m venv venv ^&^& pip install -r requirements.txt
    choice /C YN /M "Continue anyway? (Y/N)"
    if errorlevel 2 exit /b 1
)

echo [1/3] Starting Backend API (Flask :5000)...
start "HealthFit Backend" cmd /k "cd backend\flask-backend ^&^& call venv\Scripts\activate.bat ^&^& echo Starting Flask backend... ^&^& python run.py"

echo [2/3] Starting AI Service (FastAPI :8001)...
start "HealthFit AI API" cmd /k "cd ai-models ^&^& echo Installing AI deps if needed... ^&^& pip install -r requirements-ai.txt ^&^& echo Starting AI FastAPI... ^&^& python api\main.py"

echo [3/3] Starting Frontend (React :3000)...
start "HealthFit Frontend" cmd /k "cd frontend ^&^& echo Installing if needed... ^&^& npm install ^&^& echo Starting React app... ^&^& npm start"

echo.
echo ✅ All services launched!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔗 Backend API: http://localhost:5000
echo 🤖 AI API: http://localhost:8001
echo.
echo 👤 Login with:
echo    Patient: patient@gmail.com/ password123
echo    Doctor:  doctor@gmail.com/ password123
echo    Admin:   admin@gmails.com / admin123
echo.
echo [TIP] Close terminals to stop services.
