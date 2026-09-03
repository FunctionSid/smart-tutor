@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo           Smart Tutor - Local MCP Server Launcher
echo ========================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at .venv\Scripts\activate.bat
    echo Please make sure the .venv is set up first.
    echo.
    pause
    exit /b 1
)

echo Activating Python virtual environment (.venv)...
call ".venv\Scripts\activate.bat"

echo.
echo Starting MCP server on http://127.0.0.1:8765/sse ...
echo Tools provided:
echo   1. list_study_files
echo   2. read_study_file
echo   3. calculate
echo.
echo Press Ctrl+C in this window to stop the server.
echo ========================================================
echo.

python mcp_server/server.py

if errorlevel 1 (
    echo.
    echo MCP server exited with an error code.
)
pause
