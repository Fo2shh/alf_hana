@echo off
color 0A
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_MODULE=%PYTHON_EXE% -m pip"

echo ========================================
echo     Alfhana Kitchen - Run Server
echo ========================================
echo.

if not exist "%PYTHON_EXE%" (
    echo ERROR: Virtual Environment not found at "%VENV_DIR%"
    echo Please run startfresh.bat first to set up the project
    pause
    exit /b 1
)

echo [1/5] Checking Virtual Environment...
echo Using venv Python at: "%PYTHON_EXE%"
echo.

echo [2/5] Verifying Django installation...
"%PYTHON_EXE%" -c "import django; from django.utils.version import get_version" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Django is missing or corrupted. Reinstalling packages...
    %PIP_MODULE% install --no-cache-dir --force-reinstall -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo ERROR: Failed to reinstall packages. Run startfresh.bat for a full reset.
        pause
        exit /b 1
    )
    echo Packages reinstalled successfully
) else (
    for /f "delims=" %%i in ('"%PYTHON_EXE%" -c "import django; print(django.get_version())"') do set "DJVER=%%i"
    echo Django OK (version !DJVER!)
)
echo.

echo [3/5] Applying database migrations...
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" makemigrations
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations
    pause
    exit /b 1
)
echo Migrations completed
echo.

echo [4/5] Collecting static files...
if not exist "%SCRIPT_DIR%staticfiles" (
    mkdir "%SCRIPT_DIR%staticfiles"
)
"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" collectstatic --noinput
echo Static files collected
echo.

echo ========================================
echo          Starting Django Server
echo ========================================
echo.
echo Open your browser at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo ========================================
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%manage.py" runserver

pause
