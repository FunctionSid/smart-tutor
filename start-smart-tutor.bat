@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found on PATH.
    echo Install Python or activate the expected environment, then run this launcher again.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
    echo Missing virtual environment at .venv\Scripts\activate.bat
    echo Create it first, then run this launcher again.
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

where node >nul 2>nul
if errorlevel 1 (
    echo Node.js was not found on PATH.
    echo Install Node.js 20+ and run this launcher again.
    echo.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo npm was not found on PATH.
    echo Install Node.js/npm and run this launcher again.
    echo.
    pause
    exit /b 1
)

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
echo The browser will open after the backend and frontend are ready.
echo.

set SMARTTUTOR_OPEN_BROWSER=1
smarttutor start --dev

echo.
echo Smart Tutor stopped.
pause
