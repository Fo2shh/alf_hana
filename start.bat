@echo off
color 0A

set REPO_URL=https://github.com/Fo2shh/alf_hana.git
set TARGET_DIR=%CD%\alfhana_kitchen

if "%~1"=="--clone-only" (
    echo Checking if project exists...
    if not exist "%TARGET_DIR%" (
        echo Project not found, cloning from GitHub...
        git clone "%REPO_URL%" "%TARGET_DIR%"
        if errorlevel 1 (
            echo ERROR: Failed to clone repository
            pause
            exit /b 1
        )
        echo Project cloned successfully
    ) else (
        echo Project already exists
    )
    pause
    exit /b 0
)

:MAIN_SETUP

echo ========================================
echo     Alfhana Kitchen - Download & Setup
if "%~1"=="--silent" (
    echo ========================================
echo     QUIET MODE - Skipping confirmations
) else (
    echo ========================================
echo.
)

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Git is not installed or not in PATH
    echo Please install Git and try again
    echo.
    pause
    exit /b 1
)

echo Git is available

REM Check if project directory exists
if not exist "%TARGET_DIR%" (
    echo.
    echo Project directory not found at "%TARGET_DIR%"
    echo Do you want to download the project from GitHub? (Y/N)
    set /p choice="[Y/N] "
    if /i "%choice%"=="Y" (
        echo.
        echo Downloading project from GitHub...
        git clone "%REPO_URL%" "%TARGET_DIR%"
        if errorlevel 1 (
            echo ERROR: Failed to clone repository
            pause
            exit /b 1
        )
        echo Project downloaded and extracted
    ) else (
        echo.
        echo Setup cancelled. Please run the script again from the correct directory
        echo Alternatively, download the repository manually from: %REPO_URL%
        pause
        exit /b 1
    )
) else (
    echo.
    echo Using existing project at "%TARGET_DIR%"
)

echo.

if "%~1"=="--silent" (
    echo [1/7] Installing required packages...
    cd /d "%TARGET_DIR%"
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd /d "%TARGET_DIR%"
    python manage.py makemigrations
    python manage.py migrate
    if not exist "staticfiles" mkdir staticfiles
    python manage.py collectstatic --noinput
    python create_admin.py
    echo [7/7] Starting server...
    python manage.py runserver
) else (
    echo [1/7] Checking Virtual Environment...
    cd /d "%TARGET_DIR%"
    if not exist "venv" (
        echo venv not found, creating...
        python -m venv venv
        if not exist "venv" (
            echo ERROR: Failed to create Virtual Environment
            pause
            exit /b 1
        )
        echo Virtual Environment created successfully
    ) else (
        echo Virtual Environment exists
    )

    echo.
    echo [2/7] Activating Virtual Environment...
    call venv\Scripts\activate
    if errorlevel 1 (
        echo ERROR: Failed to activate Virtual Environment
        pause
        exit /b 1
    )
    echo Virtual Environment activated successfully
    echo.

    echo [3/7] Installing required packages...
    pip install -r requirements.txt
    echo Packages installed
    echo.

    echo [4/7] Creating migrations...
    python manage.py makemigrations
    echo.

    echo [5/7] Applying migrations to database...
    python manage.py migrate
    if errorlevel 1 (
        echo ERROR: Failed to apply migrations
        pause
        exit /b 1
    )
    echo Migrations applied successfully
    echo.

    echo [6/7] Collecting static files...
    if not exist "staticfiles" (
        mkdir staticfiles
    )
    python manage.py collectstatic --noinput
    echo.

    echo [7/7] Creating users...
    python create_admin.py
    echo.

    echo ========================================
    echo          Setup completed successfully!
    echo ========================================
    echo.
    echo Login credentials:
    echo - Admin: admin / admin123
    echo - Kitchen: kitchen / kitchen123
    echo - Driver: driver1 / driver123
    echo.
    echo Starting server...
    echo Open browser at: http://127.0.0.1:8000
    echo.
    echo Press Ctrl+C to stop the server
    echo ========================================
    echo.

    python manage.py runserver
)

pause