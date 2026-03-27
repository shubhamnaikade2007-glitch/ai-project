@echo off
REM ============================================================
REM HealthFit AI - Troubleshooting Script
REM Diagnoses and attempts to fix common issues
REM ============================================================

title HealthFit AI - Fix All

echo.
echo HealthFit AI - Diagnostics ^& Auto-Fix
echo ======================================
echo.

set ERRORS=0

REM ── Python check ──────────────────────────────────────────
echo [CHECK 1] Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [FAIL] Python not found
    echo   FIX: Install Python from https://python.org (check "Add to PATH")
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo   [PASS] Python %%v
)

REM ── Node.js check ─────────────────────────────────────────
echo [CHECK 2] Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [FAIL] Node.js not found
    echo   FIX: Install from https://nodejs.org
    set /a ERRORS+=1
) else (
    for /f %%v in ('node --version') do echo   [PASS] Node.js %%v
)

REM ── MySQL service check ────────────────────────────────────
echo [CHECK 3] MySQL service...
sc query MySQL80 >nul 2>&1
if %errorlevel% neq 0 (
    sc query MySQL >nul 2>&1
    if %errorlevel% neq 0 (
        echo   [WARN] MySQL service not found by name - trying connection...
    )
)

mysql -u root -proot123 -e "SELECT 1" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [FAIL] Cannot connect to MySQL
    echo   FIX: Starting MySQL service...
    net start MySQL80 >nul 2>&1
    net start MySQL >nul 2>&1
    timeout /t 3 /nobreak >nul
    mysql -u root -proot123 -e "SELECT 1" >nul 2>&1
    if %errorlevel% neq 0 (
        echo   [FAIL] MySQL still unreachable
        echo   Manual fix: Open MySQL Workbench or Services and start MySQL
        set /a ERRORS+=1
    ) else (
        echo   [FIXED] MySQL started successfully
    )
) else (
    echo   [PASS] MySQL connected (root/root123)
)

REM ── Database check ────────────────────────────────────────
echo [CHECK 4] Database tables...
mysql -u root -proot123 -e "USE healthfit_db; SHOW TABLES;" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [FAIL] healthfit_db not found or empty
    echo   FIX: Running schema and sample data...
    if exist database\mysql\schema.sql (
        mysql -u root -proot123 < database\mysql\schema.sql
        mysql -u root -proot123 < database\mysql\sample_data.sql
        if %errorlevel% equ 0 (
            echo   [FIXED] Database created with sample data
        ) else (
            echo   [FAIL] Database creation failed
            set /a ERRORS+=1
        )
    ) else (
        echo   [FAIL] schema.sql not found - run from project root
        set /a ERRORS+=1
    )
) else (
    echo   [PASS] Database exists
)

REM ── Backend venv check ────────────────────────────────────
echo [CHECK 5] Flask backend venv...
if exist backend\flask-backend\venv\Scripts\python.exe (
    echo   [PASS] Virtual environment exists
) else (
    echo   [FAIL] Virtual environment missing
    echo   FIX: Creating venv...
    cd backend\flask-backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    call venv\Scripts\deactivate.bat
    cd ..\..
    echo   [FIXED] venv created and packages installed
)

REM ── Backend .env check ────────────────────────────────────
echo [CHECK 6] Backend .env file...
if exist backend\flask-backend\.env (
    echo   [PASS] .env file exists
) else (
    echo   [FAIL] .env file missing
    echo   FIX: Creating .env from template...
    if exist .env.example (
        copy .env.example backend\flask-backend\.env >nul
        echo   [FIXED] .env created
    ) else (
        (
            echo FLASK_ENV=development
            echo FLASK_DEBUG=1
            echo SECRET_KEY=healthfit-dev-secret-key
            echo JWT_SECRET_KEY=healthfit-jwt-secret
            echo MYSQL_HOST=localhost
            echo MYSQL_PORT=3306
            echo MYSQL_USER=root
            echo MYSQL_PASSWORD=root123
            echo MYSQL_DATABASE=healthfit_db
            echo AI_API_HOST=localhost
            echo AI_API_PORT=8001
        ) > backend\flask-backend\.env
        echo   [FIXED] .env created with defaults
    )
)

REM ── Frontend node_modules check ───────────────────────────
echo [CHECK 7] Frontend dependencies...
if exist frontend\node_modules (
    echo   [PASS] node_modules exists
) else (
    echo   [FAIL] node_modules missing
    echo   FIX: Running npm install...
    cd frontend
    call npm install --legacy-peer-deps
    cd ..
    echo   [FIXED] npm packages installed
)

REM ── Port check ────────────────────────────────────────────
echo [CHECK 8] Port availability...
netstat -an | findstr ":5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [WARN] Port 5000 is in use - Flask backend may conflict
    echo   FIX: Kill the process or change PORT in .env
) else (
    echo   [PASS] Port 5000 is available
)

netstat -an | findstr ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo   [WARN] Port 3000 is in use - React may conflict
) else (
    echo   [PASS] Port 3000 is available
)

REM ── Pip packages check ────────────────────────────────────
echo [CHECK 9] Python packages...
if exist backend\flask-backend\venv\Scripts\python.exe (
    backend\flask-backend\venv\Scripts\python.exe -c "import flask, flask_sqlalchemy, flask_jwt_extended" >nul 2>&1
    if %errorlevel% neq 0 (
        echo   [FAIL] Core Flask packages missing
        echo   FIX: Reinstalling...
        cd backend\flask-backend
        call venv\Scripts\activate.bat
        pip install -r requirements.txt --quiet
        call venv\Scripts\deactivate.bat
        cd ..\..
        echo   [FIXED] Packages reinstalled
    ) else (
        echo   [PASS] Flask packages installed
    )
)

REM ── Summary ───────────────────────────────────────────────
echo.
echo ======================================
if %ERRORS% equ 0 (
    echo  ✅ All checks passed!
    echo.
    echo  Start services:
    echo    1. backend\flask-backend\venv\Scripts\activate ^& python run.py
    echo    2. python ai-models\api\main.py
    echo    3. cd frontend ^& npm start
) else (
    echo  ❌ %ERRORS% issue(s) need manual attention above
    echo     Check the [FAIL] items and follow the instructions
)
echo ======================================
echo.
pause
