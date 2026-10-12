@echo off
setlocal enabledelayedexpansion
title Shark Kitchen Launcher

cd /d "%~dp0"

:main
cls
echo ========================================
echo   Shark Kitchen Launcher
echo ========================================
echo.

if not exist "manage.py" (
    echo Project not found in current folder.
    echo.
    echo Options:
    echo 1 - Download project from GitHub (RECOMMENDED)
    echo 2 - Exit
    echo.
    set /p no_project_choice="Choose option (1-2): "

    if "%no_project_choice%"=="1" goto download
    if "%no_project_choice%"=="2" goto end

    echo Invalid option!
    pause
    goto main
)

echo Options:
echo.
echo 1 - Install / Setup (First time only)
echo 2 - Update from GitHub
echo 3 - Add Menu Items (seed_menu)
echo 4 - Run Project
echo 5 - Open Browser
echo 6 - Create Admin Users
echo 7 - Exit
echo.

set /p choice="Choose option (1-7): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto update
if "%choice%"=="3" goto seed_menu
if "%choice%"=="4" goto run
if "%choice%"=="5" goto browser
if "%choice%"=="6" goto create_users
if "%choice%"=="7" goto end

echo Invalid option!
pause
goto main

:download
echo.
echo ========================================
echo   Download Project from GitHub
echo ========================================
echo.
echo This will download the project from GitHub
echo Make sure you have internet connection.
echo.
pause

echo Downloading project from GitHub...
echo.

powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/Fo2shh/alf_hana/archive/refs/heads/main.zip'; $output = 'alf_hana.zip'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to download project
    echo Please check your internet connection
    pause
    goto main
)

echo Downloaded successfully!
echo.

echo Extracting files...
echo.

powershell -Command "Expand-Archive -Path 'alf_hana.zip' -DestinationPath '.' -Force"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to extract files
    pause
    goto main
)

echo Extracted successfully!
echo.

echo Cleaning up...
del "alf_hana.zip" >nul 2>&1

echo Moving files to current folder...
xcopy /E /I /Y "alf_hana-main\*" "." >nul
rmdir /S /Q "alf_hana-main" >nul 2>&1

echo.
echo ========================================
echo SUCCESS: Project downloaded!
echo ========================================
echo.
echo Now run option 1 (Install / Setup)
echo.
timeout /t 2 >nul
goto main

:install
echo.
echo ========================================
echo   Install / Setup
echo ========================================
echo.

if not exist "manage.py" (
    echo ERROR: manage.py not found
    echo Please download the project first (option 1)
    pause
    goto main
)

echo Step 1: Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.10+ from https://python.org
    pause
    goto main
)
python --version
echo.

echo Step 2: Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        goto main
    )
    echo Virtual environment created
)
echo.

echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 4: Installing packages...
pip install -r requirements.txt >nul
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    goto main
)
echo Packages installed
echo.

echo Step 5: Running migrations...
python manage.py migrate >nul
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    goto main
)
echo Migrations completed
echo.

echo Step 6: Collecting static files...
if not exist "staticfiles" mkdir staticfiles >nul 2>&1
python manage.py collectstatic --noinput >nul 2>&1
echo Static files collected
echo.

echo Step 7: Creating admin users...
if exist "create_admin.py" (
    python create_admin.py
) else (
    echo WARNING: create_admin.py not found
    echo You can create users later using option 5
)
echo.

echo ========================================
echo SUCCESS: Setup completed!
echo ========================================
echo.
echo Login credentials:
echo   - Admin   : admin / admin123
echo   - Kitchen : kitchen / kitchen123
echo   - Driver  : driver1 / driver123
echo.
timeout /t 2 >nul
goto main

:seed_menu
echo.
echo ========================================
echo   Add Menu Items
echo ========================================
echo.

if not exist "manage.py" (
    echo ERROR: manage.py not found
    echo Please install the project first (option 1)
    pause
    goto main
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Adding menu items to database...
python manage.py seed_menu
if errorlevel 1 (
    echo.
    echo ERROR: Failed to add menu items
    echo Make sure seed_menu.py exists in the project
    pause
    goto main
)

echo.
echo ========================================
echo SUCCESS: Menu items added!
echo ========================================
echo.
timeout /t 2 >nul
goto main

:update
echo.
echo ========================================
echo   Update from GitHub
echo ========================================
echo.

if exist ".git" (
    echo Git repository found, pulling changes...
    echo.

    git pull
    if %errorlevel% equ 0 (
        echo.
        echo SUCCESS: Updated successfully!
    ) else (
        echo.
        echo WARNING: Update failed due to untracked files
        echo Attempting to clean untracked files and retry...
        echo.

        git clean -df >nul 2>&1
        git pull

        if %errorlevel% equ 0 (
            echo.
            echo SUCCESS: Updated successfully after cleaning!
        ) else (
            echo.
            echo ERROR: Update failed even after cleaning
            echo Alternative: Re-download the project using option 1
        )
    )
) else (
    echo No Git repository found.
    echo Downloading fresh copy from GitHub...
    echo.

    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $url = 'https://github.com/Fo2shh/alf_hana/archive/refs/heads/main.zip'; $output = 'alf_hana.zip'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing"

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to download project
        echo Please check your internet connection
        pause
        goto main
    )

    echo Downloaded successfully!
    echo.

    echo Extracting files...
    powershell -Command "Expand-Archive -Path 'alf_hana.zip' -DestinationPath '.' -Force"

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to extract files
        pause
        goto main
    )

    echo Extracted successfully!
    echo.

    echo Cleaning up...
    del "alf_hana.zip" >nul 2>&1

    echo Moving files to current folder...
    xcopy /E /I /Y "alf_hana-main\*" "." >nul
    rmdir /S /Q "alf_hana-main" >nul 2>&1

    echo.
    echo SUCCESS: Project updated from GitHub!
)
echo.
timeout /t 2 >nul
goto main

:run
echo.
echo Starting project...
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    start /B python manage.py runserver >nul 2>&1
) else (
    start /B python manage.py runserver >nul 2>&1
)

echo.
echo Waiting for server to start...
timeout /t 3 >nul

echo Opening browser...
start "" http://127.0.0.1:8000

echo.
echo Server is running
echo Press any key to stop the server...
pause

echo.
echo Stopping server...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 1 >nul
goto main

:browser
echo.
echo Opening browser...
start "" http://127.0.0.1:8000
echo.
echo Browser opened
echo.
pause
goto main

:create_users
echo.
echo ========================================
echo   Create Admin Users
echo ========================================
echo.

if not exist "manage.py" (
    echo ERROR: manage.py not found
    echo Please install the project first (option 1)
    pause
    goto main
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if exist "create_admin.py" (
    echo Creating admin users...
    python create_admin.py
    if errorlevel 1 (
        echo ERROR: Failed to create users
        pause
        goto main
    )
    echo.
    echo SUCCESS: Users created!
    echo.
    echo Login credentials:
    echo   - Admin   : admin / admin123
    echo   - Kitchen : kitchen / kitchen123
    echo   - Driver  : driver1 / driver123
) else (
    echo ERROR: create_admin.py not found
    echo This file should be in the project folder
)
echo.
pause
goto main

:end
cls
echo.
echo Thank you for using Shark Kitchen Launcher
echo.
timeout /t 2 >nul
exit
