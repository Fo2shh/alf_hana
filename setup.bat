@echo off
title Shark Kitchen Setup

cd /d "%~dp0"

echo ========================================
echo   Shark Kitchen Setup
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.8 or later is installed
    pause
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo Step 4: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo.
echo Step 5: Creating initial data...
python manage.py seed_menu
if %errorlevel% neq 0 (
    echo WARNING: Failed to create initial data
    echo You can run it later using: python manage.py seed_menu
)

echo.
echo ========================================
echo SUCCESS: Setup completed!
echo ========================================
echo.
echo You can now run the project using:
echo shark_launcher.bat
echo.
pause
