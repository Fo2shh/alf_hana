@echo off
cd /d "%~dp0"

echo ========================================
echo     Alfhana Kitchen - Setup & Run
echo ========================================
echo.

echo [1/7] Checking Virtual Environment...
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

pause
