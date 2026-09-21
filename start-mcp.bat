@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo           Smart Tutor - Local MCP Launcher
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found at .venv\Scripts\python.exe
    echo Please make sure the .venv is set up first.
    echo.
    pause
    exit /b 1
)

if /i "%~1"=="--server" goto server
if /i "%~1"=="--client" goto client

echo.
echo Opening two PowerShell windows:
echo   1. Smart Tutor MCP Server
echo   2. Smart Tutor MCP Client
echo.
echo Type MCP commands in the Client window.
echo ========================================================
echo.

start "Smart Tutor MCP Server" powershell -NoExit -ExecutionPolicy Bypass -Command "$Host.UI.RawUI.WindowTitle = 'Smart Tutor MCP Server'; Set-Location -LiteralPath '%CD%'; & '.\.venv\Scripts\python.exe' 'mcp_server/server.py'; Write-Host ''; Read-Host 'Server stopped. Press Enter to close'"

timeout /t 2 /nobreak >nul

start "Smart Tutor MCP Client" powershell -NoExit -ExecutionPolicy Bypass -Command "$Host.UI.RawUI.WindowTitle = 'Smart Tutor MCP Client'; Set-Location -LiteralPath '%CD%'; & '.\.venv\Scripts\python.exe' 'mcp_server/interactive_client.py'; Write-Host ''; Read-Host 'Client exited. Press Enter to close'"

exit /b 0

:server
title Smart Tutor MCP Server
echo Starting MCP server on http://127.0.0.1:8765/sse ...
echo Press Ctrl+C in this window to stop the server.
echo.
".venv\Scripts\python.exe" mcp_server/server.py

if errorlevel 1 (
    echo.
    echo MCP server exited with an error code.
)
pause
exit /b %errorlevel%

:client
title Smart Tutor MCP Client
echo Starting interactive MCP client...
echo.
".venv\Scripts\python.exe" mcp_server/interactive_client.py
pause
exit /b %errorlevel%
