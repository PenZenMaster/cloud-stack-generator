@echo off
echo.
echo ==========================================
echo   GitHub Issues Creator
echo   Cloud Stack Generator Template Import/Export Feature
echo ==========================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking required packages...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests package...
    pip install requests
)

echo.
echo Running GitHub Issues Creator...
echo.
python tools\github_issues_creator.py

echo.
pause