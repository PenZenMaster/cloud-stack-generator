@echo off
echo.
echo ==========================================
echo   GitHub Token Setup for Cloud Stack Generator
echo ==========================================
echo.

cd /d "%~dp0"

REM Prefer the project virtual environment when present
set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"

REM Check if Python is available
%PY% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the token manager
echo Running GitHub token setup...
echo.
%PY% tools\github_token_manager.py

echo.
echo Setup complete!
pause