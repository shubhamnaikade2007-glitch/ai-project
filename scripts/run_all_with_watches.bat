@echo off
echo Starting HealthFit with Smartwatch Support...
start cmd /k "cd ai-models\api && python main.py"
timeout /t 3
start cmd /k "cd backend\flask-backend && python run.py"
timeout /t 3
start cmd /k "cd frontend && npm start"
echo 🚀 All services + Smartwatch sync ready!
echo Connect Fitbit: http://localhost:5000/smartwatch/fitbit/auth
pause
