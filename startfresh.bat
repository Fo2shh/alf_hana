@echo off
color 0A
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_MODULE=%PYTHON_EXE% -m pip"

echo ========================================
echo   Alfhana Kitchen - First Time Setup
echo ========================================
echo.

echo [1/9] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)
python --version
echo.

echo [2/9] Setting up Virtual Environment...
if exist "%VENV_DIR%" (
    echo.
    echo Existing Virtual Environment found at:
    echo   "%VENV_DIR%"
    echo.
    echo   [1] Keep existing venv and continue (faster)
    echo   [2] DELETE venv and rebuild from scratch (fixes corrupted installs)
    echo.
    set /p VENV_CHOICE="Enter choice [1/2] (default 1): "
    if "!VENV_CHOICE!"=="2" (
        echo.
        echo Deleting old venv for a clean rebuild...
        rmdir /s /q "%VENV_DIR%"
        if exist "%VENV_DIR%" (
            echo WARNING: Could not fully delete old venv. Some files may be locked.
        ) else (
            echo Old venv removed successfully
        )
    ) else (
        echo Keeping existing venv
    )
)

if not exist "%PYTHON_EXE%" (
    echo Creating fresh venv at "%VENV_DIR%"...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create Virtual Environment
        pause
        exit /b 1
    )
    echo Virtual Environment created successfully
)
echo.

echo [3/9] Upgrading pip to latest version...
%PIP_MODULE% install --upgrade pip >nul 2>&1
echo pip ready
echo.

echo [4/9] Installing required packages...
%PIP_MODULE% install --no-cache-dir -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install required packages
    echo.
    echo Troubleshooting tips:
    echo   - Run this script again and choose option [2] to rebuild venv
    echo   - Check your internet connection
    echo   - Ensure antivirus is not blocking pip
    echo.
    pause
    exit /b 1
)
echo Packages installed successfully
echo.

echo [5/9] Verifying Django installation...
"%PYTHON_EXE%" -c "import django; print('Django version: ' + django.get_version()); from django.utils.version import get_version; print('Django health: OK')"
if errorlevel 1 (
    echo ERROR: Django verification failed! The installation may be corrupted.
    echo Run this script again and choose option [2] to delete and rebuild venv.
    pause
    exit /b 1
)
echo.

echo [6/9] Creating database migrations...
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" makemigrations
echo.

echo [7/9] Applying migrations to database...
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations
    pause
    exit /b 1
)
echo Migrations applied successfully
echo.

echo [8/9] Collecting static files...
if not exist "%SCRIPT_DIR%staticfiles" (
    mkdir "%SCRIPT_DIR%staticfiles"
)
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" collectstatic --noinput
echo Static files collected
echo.

echo [9/9] Creating default users...
"%PYTHON_EXE%" "%SCRIPT_DIR%create_admin.py"
if errorlevel 1 (
    echo ERROR: Failed to create default users
    pause
    exit /b 1
)
echo Users ready
echo.

echo ========================================
echo      Setup completed successfully!
echo ========================================
echo.
echo Login credentials:
echo   - Admin   : admin / admin123
echo   - Kitchen : kitchen / kitchen123
echo   - Driver  : driver1 / driver123
echo.
echo Next time, just run: start.bat  (faster daily startup)
echo.
echo Starting Django development server...
echo Open your browser at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" runserver

pause
