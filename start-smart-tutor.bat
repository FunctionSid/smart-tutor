@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Missing virtual environment at .venv\Scripts\activate.bat
    echo Create it first, then run this launcher again.
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

where smarttutor >nul 2>nul
if errorlevel 1 (
    echo Installing Smart Tutor into the local virtual environment...
    python -m pip install -e .
    if errorlevel 1 (
        echo.
        echo Smart Tutor install failed.
        pause
        exit /b 1
    )
)

if not exist "web\node_modules" (
    echo Installing frontend dependencies...
    pushd web
    call npm ci --legacy-peer-deps
    if errorlevel 1 (
        popd
        echo.
        echo Frontend dependency install failed.
        pause
        exit /b 1
    )
    popd
)

echo.
echo Starting Smart Tutor...
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3782
echo.

start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 8; Start-Process 'http://localhost:3782'"

smarttutor start --dev

echo.
echo Smart Tutor stopped.
pause
