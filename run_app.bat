@echo off
REM Cognitive Fatigue Tracker - Launcher
REM Automatically uses the correct Python environment

cd /d "%~dp0"

echo ================================================
echo  Cognitive Fatigue Tracker
echo ================================================
echo.

REM Check if venv311 exists
if not exist "d:\code3\venv311\Scripts\python.exe" (
    echo ERROR: Python 3.11 environment not found!
    echo Please run the setup first.
    echo.
    pause
    exit /b 1
)

echo Starting application...
echo Using Python 3.11 environment (venv311)
echo.

REM Run the application
d:\code3\venv311\Scripts\python.exe "%~dp0main.py"

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================
    echo  Application exited with error code: %ERRORLEVEL%
    echo ================================================
    echo.
    echo Check logs\app_*.log for details
    echo.
    pause
)
